import { chmodSync, mkdtempSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest'
import { eq, sql } from 'drizzle-orm'

import * as schema from '@/db/schema'
import { buildObligationSet, hashObligationSet } from '@/lib/cursor/obligation'
import { parseStoredCompositePayload } from '@/lib/cursor/composite'
import {
  checkProvenanceAgreement,
  checkProvenanceCoverage,
  PROVENANCE_MATRIX,
  type ProvenanceSurfaceName,
} from '@/lib/cursor/provenance'
import {
  buildArtifactMeta,
  buildIndexProvenance,
  missingIdentityFields,
  runIdentity,
} from '@/lib/cursor/identity'
import { CONTRACT_PROVENANCE, EMPTY_DECLARATION_TOOL, runCursorAnalysis } from '@/lib/cursor/run'
import {
  ANALYSIS_SCHEMA_VERSION,
  DECLARATION_SCHEMA_VERSION,
  OBLIGATION_GENERATOR_VERSION,
} from '@/lib/cursor/schema'
import { closeTestPool, hasTestDatabase, testDb, truncateAll } from '../helpers/db'

/**
 * G4 — VÒNG CHẠY HAI LƯỢT, trên PostgreSQL thật, với một Cursor CLI GIẢ.
 *
 * CLI giả đọc kịch bản từ một tệp: mỗi lần được gọi nó lấy phản hồi kế tiếp. Nhờ
 * vậy dựng được đúng các ca không thể dựng bằng LLM thật — lượt 1 hỏng rồi sửa
 * được, lượt 2 hỏng ba lần, timeout ở đúng một lượt — mà vẫn đi qua toàn bộ
 * đường ghi thật: execution, bản kê, phán quyết, kết quả, tập nghĩa vụ.
 *
 * Kịch bản KHÔNG mô phỏng bộ kiểm định: output giả đi qua đúng validator thật.
 */
describe.skipIf(!hasTestDatabase)('G4 — vòng chạy hai lượt (PostgreSQL thật)', () => {
  const db = testDb()
  let workspaceId: string
  let channelId: string
  let scriptDir: string
  let scriptPath: string
  let planPath: string
  const savedAgent = process.env.CURSOR_AGENT_PATH

  const H = (c: string) => c.repeat(64)

  /** Bản phân tích hợp lệ: đúng MỘT ô nhạy cảm -> đúng một nghĩa vụ. */
  const ANALYSIS = {
    schemaVersion: ANALYSIS_SCHEMA_VERSION,
    analysisSummary: {
      overallAssessment: 'Kênh có một video vượt trội rõ rệt so với phần còn lại trong cửa sổ.',
      confidence: 'MEDIUM',
      confidenceRationale: 'Độ phủ dữ liệu cốt lõi đầy đủ trong cửa sổ quan sát này.',
      primaryConstraint: 'Cỡ mẫu còn nhỏ nên kết luận xu hướng cần thận trọng.',
    },
    keyFindings: [{
      id: 'F-001',
      statement: 'Video aaaaaaaaaaa nằm ở nhóm dẫn đầu về lượt xem 7 ngày trong nhóm Shorts.',
      findingType: 'OBSERVATION', confidence: 'MEDIUM', evidenceIds: ['OBS-001'],
      supportingReasoning: 'Quan sát tất định ghi nhận phân vị 92 trong nhóm cùng định dạng.',
      contradictingEvidenceIds: [], limitations: ['cỡ mẫu lượt xem thấp nên CTR nhiễu'],
    }],
    hypotheses: [], recommendations: [], experiments: [],
    manualReviewTargets: [], dataRequests: [],
    explicitNonConclusions: ['Không kết luận được về khâu tiếp cận.'],
    selfCheck: {
      usedOnlyProvidedEvidence: true, recomputedMetrics: false, madeCausalClaims: false,
      madeCtrOrImpressionClaims: false, allFindingEvidenceResolved: true,
    },
  }

  function declarationFor(analysis: unknown, over: Record<string, unknown> = {}) {
    const set = buildObligationSet(analysis as never)
    return {
      schemaVersion: DECLARATION_SCHEMA_VERSION,
      obligationSetHash: hashObligationSet(set),
      // Khai theo ĐÚNG nội dung từng ô. Chặng HỢP NHẤT chạy S1–S8 thật, nên
      // một bản khai "một cỡ cho tất cả" sẽ bị S1 chặn ở ô mà chủ ngữ đã khai
      // không hề xuất hiện — và đó là hành vi đúng, không phải phiền toái.
      declarations: set.obligations.map((o) => {
        const impressionsOnly =
          o.mentionedMetrics.includes('impressions') && !o.mentionedMetrics.includes('impression_ctr')
        return impressionsOnly
          ? {
              id: o.id,
              subjectMetric: 'impressions',
              relatedMetric: 'NONE',
              claimType: 'RECOMMENDATION',
              judgement: 'UNKNOWN',
              assertionStatus: 'NEGATED_ACTION',
              evidenceIds: [] as string[],
              requiresMissingnessDisclosure: false,
            }
          : {
              id: o.id,
              subjectMetric: 'views',
              relatedMetric: 'impression_ctr',
              claimType: 'METHODOLOGY_LIMITATION',
              judgement: 'LOW',
              assertionStatus: 'LIMITATION',
              evidenceIds: [] as string[],
              requiresMissingnessDisclosure: false,
            }
      }),
      ...over,
    }
  }

  /**
   * Đặt kịch bản cho CLI giả.
   *
   * Mỗi phần tử là một lần gọi. `{ sleep }` mô phỏng treo để kiểm timeout;
   * `{ exit }` mô phỏng tiến trình con chết.
   */
  type Step = { json?: unknown; raw?: string; sleep?: number; exit?: number }
  function plan(steps: Step[]): void {
    writeFileSync(planPath, JSON.stringify(steps), 'utf8')
    writeFileSync(join(scriptDir, 'cursor.counter'), '0', 'utf8')
  }

  beforeAll(async () => {
    scriptDir = mkdtempSync(join(tmpdir(), 'g4-cli-'))
    planPath = join(scriptDir, 'plan.json')
    scriptPath = join(scriptDir, 'cursor-agent')
    // CLI giả: đọc stdin (prompt) rồi in phản hồi kế tiếp của kịch bản.
    writeFileSync(
      scriptPath,
      `#!/usr/bin/env node
const fs = require('fs')
const path = require('path')
const dir = ${JSON.stringify(scriptDir)}
try { fs.readFileSync(0, 'utf8') } catch {}
const steps = JSON.parse(fs.readFileSync(path.join(dir, 'plan.json'), 'utf8'))
const counterFile = path.join(dir, 'cursor.counter')
const n = Number(fs.readFileSync(counterFile, 'utf8') || '0')
fs.writeFileSync(counterFile, String(n + 1))
const step = steps[n] || steps[steps.length - 1]
if (step.sleep) { const end = Date.now() + step.sleep; while (Date.now() < end) {} }
// stdout ĐƯỢC IN TRƯỚC khi thoát: một lần chạy thật có thể in ra rồi mới hỏng,
// và phần đã in vẫn là lời của mô hình. Bản trước thoát ngay nên không có cách
// nào dựng ca "CLI hỏng NHƯNG đã nói điều bị cấm".
if (step.raw !== undefined || step.json !== undefined) {
  process.stdout.write(step.raw !== undefined ? step.raw : JSON.stringify(step.json))
}
if (step.exit !== undefined) { process.stderr.write('gia lap loi'); process.exit(step.exit) }
`,
      'utf8',
    )
    chmodSync(scriptPath, 0o755)
    process.env.CURSOR_AGENT_PATH = scriptPath

    await truncateAll()
    await db.execute(sql`TRUNCATE TABLE cursor_claim_obligation, cursor_analysis_result,
      cursor_execution_manifest, analysis_validation, cursor_analysis_request, analysis_package,
      analysis_quality, anomaly, cohort_summary, evidence_reference, deterministic_observation,
      feature_value, feature_version, feature_definition, video_daily_metric_history,
      video_daily_metric, channel_daily_metric, video, prompt_revision, prompt_template CASCADE`)

    const [ws] = await db.insert(schema.workspace).values({ slug: 'ws-g4', name: 'W' }).returning()
    workspaceId = ws!.id
    const [ch] = await db.insert(schema.channel)
      .values({ workspaceId, label: 'hinh_su', youtubeChannelId: 'UCg4000000000000000000', title: 'T' })
      .returning()
    channelId = ch!.id
    const [algo] = await db.insert(schema.algorithm)
      .values({ key: 'deterministic-analysis', name: 'D', kind: 'DETERMINISTIC' }).returning()
    const [ver] = await db.insert(schema.algorithmVersion)
      .values({ algorithmId: algo!.id, version: '1.0.0' }).returning()
    const [run] = await db.insert(schema.analysisRun).values({
      workspaceId, channelId, subjectType: 'CHANNEL', subjectId: channelId,
      algorithmId: algo!.id, algorithmVersionId: ver!.id, runSequence: 1, inputHash: H('a'),
      periodStart: '2026-06-01', periodEnd: '2026-07-27', status: 'SUCCEEDED',
    }).returning()

    const pkg = {
      schemaVersion: '1.0.0', algorithmVersion: '1.0.0',
      scope: {
        workspaceId, channelId, channelLabel: 'hinh_su', channelTitle: 'K',
        reportingTimezone: 'America/Los_Angeles', windowStart: '2026-06-01',
        windowEnd: '2026-07-27', analysisRunId: run!.id, inputHash: H('a'),
      },
      channelSummary: { videos: 20, medianViewsD7: 100 },
      dataCoverage: {
        videosTotal: 20, videosWithMetrics: 18, videosImmature: 2, metricRows: 180,
        expectedDates: 57, observedDates: 57, missingDates: [],
        metricCoverage: { views: 1, impressions: 0, impressionCtr: 0 }, revisedRows: 0,
      },
      confidence: { score: 0.8, band: 'HIGH', drivers: {} },
      baselines: [{ key: 'CHANNEL_FORMAT:SHORT', kind: 'CHANNEL_FORMAT', description: 'S', videoCount: 12, medianViewsD7: 100 }],
      featureDefinitions: [{ key: 'views_d7', label: 'V', unit: 'COUNT', direction: 'HIGHER_IS_BETTER', version: '1.0.0', formula: 'sum' }],
      observations: [{
        kind: 'TOP_PERFORMER', polarity: 'POSITIVE',
        statement: 'Video aaaaaaaaaaa ở phân vị 92 về lượt xem 7 ngày.',
        metricValues: { views_d7: 900 }, baselineKind: 'CHANNEL_FORMAT', confidence: 0.8,
        limitations: [], evidenceRefs: [{ refType: 'VIDEO', refId: 'v1' }], isHypothesis: false,
      }],
      anomalies: [], rankedVideos: [{ youtubeVideoId: 'aaaaaaaaaaa', title: 'A', format: 'SHORT', viewsD7: 900 }],
      cohortComparisons: [], formatComparison: null, hypothesisCandidates: [],
      unresolvedQuestions: [], missingData: [], analysisTasks: [],
      limitsApplied: {
        positiveObservations: { included: 1, total: 1 }, negativeObservations: { included: 0, total: 0 },
        anomalies: { included: 0, total: 0 }, rankedVideos: { included: 1, total: 1 },
        cohorts: { included: 0, total: 0 }, hypotheses: { included: 0, total: 0 }, truncatedForSize: false,
      },
    }
    await db.insert(schema.analysisPackage).values({
      workspaceId, analysisRunId: run!.id, channelId, schemaVersion: '1.0.0',
      payload: pkg, payloadHash: H('a'), packageBytes: 100, rawInputBytes: 1000,
      reductionPercent: '90',
    })
  })

  afterEach(async () => {
    // Mỗi ca dựng lại lịch sử execution của riêng nó.
    await db.execute(sql`TRUNCATE TABLE cursor_claim_obligation, cursor_analysis_result,
      cursor_execution_manifest, analysis_validation, cursor_analysis_request CASCADE`)
    await db.execute(sql`DELETE FROM llm_execution`)
  })

  afterAll(async () => {
    if (savedAgent !== undefined) process.env.CURSOR_AGENT_PATH = savedAgent
    else delete process.env.CURSOR_AGENT_PATH
    await closeTestPool()
  })

  const go = () =>
    runCursorAnalysis({ workspaceId, channelLabel: 'hinh_su', sandboxDir: scriptDir, timeoutMs: 20_000 })

  const counts = async () => {
    const q = async (t: string) =>
      Number((await db.execute<{ n: number }>(sql`SELECT count(*)::int n FROM ${sql.raw(t)}`)).rows[0]!.n)
    return {
      executions: await q('llm_execution'),
      obligations: await q('cursor_claim_obligation'),
      results: await q('cursor_analysis_result'),
      validations: await q('analysis_validation'),
    }
  }
  const roleCount = async (role: string) =>
    Number((await db.execute<{ n: number }>(sql`
      SELECT count(*)::int n FROM cursor_execution_manifest WHERE execution_role = ${role}`)).rows[0]!.n)

  describe('đường ĐẠT', () => {
    it('hai lượt đạt: một nghĩa vụ, một kết quả ANALYSIS, hai vai execution', async () => {
      plan([{ json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const r = await go()
      expect(r.status, JSON.stringify(r.attempts.map((a) => a.repairErrors))).toBe('SUCCEEDED')
      expect(r.obligationCount).toBe(1)
      expect(r.declarations).toHaveLength(1)
      expect(await roleCount('ANALYSIS')).toBe(1)
      expect(await roleCount('DECLARATION')).toBe(1)
      const c = await counts()
      expect(c.obligations).toBe(1)
      // HAI kết quả: văn xuôi bất biến (ANALYSIS) và bản hợp nhất (COMPOSITE).
      // Giữ cả hai là cách duy nhất chứng minh lượt khai báo không sửa văn xuôi.
      expect(c.results).toBe(2)
      const roles = await db.execute<{ result_role: string }>(sql`
        SELECT result_role FROM cursor_analysis_result ORDER BY result_role`)
      expect(roles.rows.map((r) => r.result_role)).toEqual(['ANALYSIS', 'COMPOSITE'])
      expect(r.resultId).toBeTruthy()
    })

    it('phán quyết ghi đúng CHẶNG cho từng lượt', async () => {
      plan([{ json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      await go()
      const rows = await db.execute<{ stage: string }>(sql`
        SELECT stage FROM analysis_validation ORDER BY stage`)
      // `ORDER BY stage` sắp theo THỨ TỰ ENUM, mà thứ tự enum chính là thứ tự
      // đường ống: phân tích -> khai báo -> hợp nhất. Đó là điều ta muốn khẳng
      // định, nên giữ nguyên chứ không ép về thứ tự chữ cái.
      expect(rows.rows.map((r) => r.stage)).toEqual(['ANALYSIS', 'DECLARATION', 'COMPOSITE'])
    })

    it('MỘT lần thử độ ổn định dù lượt khai báo chạy nhiều lần', async () => {
      plan([
        { json: ANALYSIS },
        { raw: '{ hỏng' },
        { raw: '{ vẫn hỏng' },
        { json: declarationFor(ANALYSIS) },
      ])
      const r = await go()
      expect(r.status).toBe('SUCCEEDED')
      // Bảng lần thử độ ổn định chỉ đếm LƯỢT PHÂN TÍCH.
      expect(r.attempts).toHaveLength(1)
      expect(r.declarationAttempts.length).toBeGreaterThan(1)
      expect(await roleCount('DECLARATION')).toBe(r.declarationAttempts.length)
    })
  })

  describe('CỔNG: lượt 1 hỏng thì không có gì phía sau', () => {
    it('phân tích hỏng -> KHÔNG nghĩa vụ, KHÔNG execution khai báo', async () => {
      plan([{ json: { ...ANALYSIS, keyFindings: [] } }])
      const r = await go()
      expect(r.status).not.toBe('SUCCEEDED')
      expect(r.obligationCount).toBeNull()
      expect(r.declarations).toBeNull()
      const c = await counts()
      expect(c.obligations).toBe(0)
      expect(await roleCount('DECLARATION')).toBe(0)
      expect(c.results).toBe(0)
    })

    it('phân tích TUỒN metricClaims -> chặn, không sang lượt 2', async () => {
      plan([{ json: { ...ANALYSIS, metricClaims: [] } }])
      const r = await go()
      expect(r.status).not.toBe('SUCCEEDED')
      expect(await roleCount('DECLARATION')).toBe(0)
      const rules = r.attempts[0]!.report?.structuralIssues.map((i) => i.rule) ?? []
      expect(rules).toContain('claims_in_analysis_pass')
    })

    it('phân tích SỬA ĐƯỢC rồi mới sinh nghĩa vụ', async () => {
      plan([{ raw: 'không phải JSON' }, { json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const r = await go()
      expect(r.status).toBe('SUCCEEDED')
      expect(r.attempts).toHaveLength(2)
      expect(r.attempts[0]!.failureClass).toBe('INVALID_JSON')
      expect(r.obligationCount).toBe(1)
      // Tập nghĩa vụ sinh SAU khi lượt 1 đạt, nên chỉ có ĐÚNG MỘT.
      expect((await counts()).obligations).toBe(1)
    })

    it('chặng ANALYSIS KHÔNG phát lỗi thiếu khai báo', async () => {
      plan([{ json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const r = await go()
      const rules = r.attempts[0]!.report?.claimIssues.map((i) => i.rule) ?? []
      expect(rules).not.toContain('undeclared_sensitive_unit')
      expect(rules).not.toContain('declaration_missing_obligation')
    })
  })

  describe('nghĩa vụ sinh từ payload ĐỌC LẠI TỪ DATABASE', () => {
    it('băm tập nghĩa vụ khớp payload đã lưu, không phải object trong RAM', async () => {
      plan([{ json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const r = await go()
      const row = await db.execute<{ payload_hash: string; analysis_hash: string; obligation_set_hash: string; obligation_count: number; generator_version: string }>(sql`
        SELECT res.payload_hash, ob.analysis_hash, ob.obligation_set_hash,
               ob.obligation_count, ob.generator_version
        FROM cursor_claim_obligation ob
        JOIN cursor_analysis_result res ON res.llm_execution_id = ob.analysis_execution_id`)
      const got = row.rows[0]!
      // Băm của tập nghĩa vụ phải bằng ĐÚNG băm cột của payload đã ghi. Nếu bộ
      // sinh chạy trên object trong bộ nhớ thì hai giá trị này có thể khác nhau
      // mà không có gì báo.
      expect(got.analysis_hash).toBe(got.payload_hash)
      expect(got.analysis_hash).toBe(r.analysisPayloadHash)
      expect(got.obligation_set_hash).toBe(r.obligationSetHash)
      expect(Number(got.obligation_count)).toBe(1)
      expect(got.generator_version).toBe(OBLIGATION_GENERATOR_VERSION)
    })

    it('tập nghĩa vụ neo vào ĐÚNG execution phân tích', async () => {
      plan([{ json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const r = await go()
      const row = await db.execute<{ analysis_execution_id: string }>(sql`
        SELECT analysis_execution_id FROM cursor_claim_obligation`)
      expect(row.rows[0]!.analysis_execution_id).toBe(r.analysisExecutionId)
    })

    it('lỗi sinh nghĩa vụ được phân loại là THẤT BẠI HỆ THỐNG', async () => {
      // Dựng lỗi bằng cách chèn sẵn một tập nghĩa vụ cho execution SẼ được tạo
      // là bất khả; thay vào đó ta phá tính duy nhất bằng cách chạy hai lần trên
      // cùng một execution — không làm được từ ngoài. Nên kiểm bằng đường ngắn:
      // vi phạm CHECK đếm nghĩa vụ.
      plan([{ json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const r = await go()
      expect(r.systemFailure).toBeUndefined()
      // Một lần ghi trùng phải bị database chặn — đó là cùng con đường mà nhánh
      // SYSTEM bắt được.
      await expect(
        db.insert(schema.cursorClaimObligation).values({
          workspaceId, analysisRunId: (await db.execute<{ id: string }>(sql`SELECT analysis_run_id id FROM cursor_claim_obligation`)).rows[0]!.id,
          channelId, requestId: r.requestId!,
          analysisExecutionId: r.analysisExecutionId!,
          analysisHash: H('5'), obligationSetHash: H('6'), generatorVersion: '1.0',
          obligationCount: 1,
          obligations: { schemaVersion: '3.0', generatorVersion: '1.0', analysisHash: H('5'), obligations: [{ id: 'MC-001' }] },
        }),
      ).rejects.toThrow()
    })
  })

  describe('lượt 2 hỏng: giữ nguyên lượt 1 và tập nghĩa vụ', () => {
    it('khai báo THIẾU mục -> hỏng, nhưng phân tích và nghĩa vụ còn nguyên', async () => {
      plan([
        { json: ANALYSIS },
        { json: { ...declarationFor(ANALYSIS), declarations: [] } },
        { json: { ...declarationFor(ANALYSIS), declarations: [] } },
        { json: { ...declarationFor(ANALYSIS), declarations: [] } },
      ])
      const r = await go()
      expect(r.status).not.toBe('SUCCEEDED')
      expect(r.declarations).toBeNull()
      const c = await counts()
      expect(c.obligations).toBe(1)
      expect(c.results).toBe(1) // kết quả ANALYSIS vẫn còn
      expect(await roleCount('ANALYSIS')).toBe(1)
    })

    it('khai báo THỪA / TRÙNG / SAI BĂM đều fail-closed', async () => {
      const good = declarationFor(ANALYSIS)
      for (const bad of [
        { ...good, declarations: [...good.declarations, { ...good.declarations[0]!, id: 'MC-099' }] },
        { ...good, declarations: [good.declarations[0]!, good.declarations[0]!] },
        { ...good, obligationSetHash: H('f') },
      ]) {
        await db.execute(sql`TRUNCATE TABLE cursor_claim_obligation, cursor_analysis_result,
          cursor_execution_manifest, analysis_validation, cursor_analysis_request CASCADE`)
        await db.execute(sql`DELETE FROM llm_execution`)
        plan([{ json: ANALYSIS }, { json: bad }, { json: bad }, { json: bad }])
        const r = await go()
        expect(r.status, JSON.stringify(bad).slice(0, 80)).not.toBe('SUCCEEDED')
      }
    })

    it('ĐẢO THỨ TỰ khai báo vẫn ĐẠT', async () => {
      const multi = {
        ...ANALYSIS,
        keyFindings: [{
          ...ANALYSIS.keyFindings[0]!,
          limitations: ['cỡ mẫu lượt xem thấp nên CTR nhiễu', 'chưa bật đo impressions'],
        }],
      }
      const d = declarationFor(multi)
      plan([{ json: multi }, { json: { ...d, declarations: [...d.declarations].reverse() } }])
      const r = await go()
      expect(r.status, JSON.stringify(r.declarationAttempts.map((a) => a.repairErrors))).toBe('SUCCEEDED')
      expect(r.obligationCount).toBe(2)
    })

    it('CHỈ lượt 2 chạy lại — lượt 1 KHÔNG chạy lại', async () => {
      plan([{ json: ANALYSIS }, { raw: 'hỏng' }, { json: declarationFor(ANALYSIS) }])
      const r = await go()
      expect(r.status).toBe('SUCCEEDED')
      expect(r.attempts).toHaveLength(1)              // phân tích chạy đúng một lần
      expect(r.declarationAttempts).toHaveLength(2)   // khai báo chạy hai lần
      expect(await roleCount('ANALYSIS')).toBe(1)
      expect((await counts()).obligations).toBe(1)    // tập nghĩa vụ KHÔNG sinh lại
    })

    it('chuỗi thử lại của lượt 2 chỉ nối vào lượt 2', async () => {
      plan([{ json: ANALYSIS }, { raw: 'hỏng' }, { json: declarationFor(ANALYSIS) }])
      const r = await go()
      const rows = await db.execute<{ role: string; parent: string | null; child: string }>(sql`
        SELECT m.execution_role role, m.parent_execution_id parent, m.llm_execution_id child
        FROM cursor_execution_manifest m WHERE m.parent_execution_id IS NOT NULL`)
      for (const row of rows.rows) {
        const parentRole = await db.execute<{ role: string }>(sql`
          SELECT execution_role role FROM cursor_execution_manifest
          WHERE llm_execution_id = ${row.parent}`)
        expect(parentRole.rows[0]!.role).toBe(row.role)
      }
      expect(r.status).toBe('SUCCEEDED')
    })
  })

  describe('thất bại tiến trình con, tách theo lượt', () => {
    it('TIMEOUT ở lượt 1 -> ghi lại, không sang lượt 2', async () => {
      plan([{ sleep: 3000 }, { sleep: 3000 }, { sleep: 3000 }])
      const r = await runCursorAnalysis({
        workspaceId, channelLabel: 'hinh_su', sandboxDir: scriptDir, timeoutMs: 400,
      })
      expect(r.status).toBe('FAILED')
      expect(r.attempts.every((a) => a.timedOut)).toBe(true)
      expect(await roleCount('DECLARATION')).toBe(0)
      expect((await counts()).obligations).toBe(0)
    })

    it('TIMEOUT ở lượt 2 -> lượt 1 và nghĩa vụ vẫn còn', async () => {
      plan([{ json: ANALYSIS }, { sleep: 3000 }, { sleep: 3000 }, { sleep: 3000 }])
      const r = await runCursorAnalysis({
        workspaceId, channelLabel: 'hinh_su', sandboxDir: scriptDir, timeoutMs: 400,
      })
      expect(r.status).toBe('FAILED')
      expect(r.attempts).toHaveLength(1)
      expect(r.attempts[0]!.timedOut).toBe(false)
      expect(r.declarationAttempts.every((a) => a.timedOut)).toBe(true)
      expect((await counts()).obligations).toBe(1)
      expect(await roleCount('ANALYSIS')).toBe(1)
    })

    it('tiến trình con CHẾT ở lượt 2 được ghi riêng khỏi lượt 1', async () => {
      plan([{ json: ANALYSIS }, { exit: 3 }, { exit: 3 }, { exit: 3 }])
      const r = await go()
      expect(r.status).toBe('FAILED')
      expect(r.attempts[0]!.exitCode).toBe(0)
      expect(r.declarationAttempts.every((a) => a.exitCode === 3)).toBe(true)
      const rows = await db.execute<{ role: string; exit_code: number | null }>(sql`
        SELECT execution_role role, exit_code FROM cursor_execution_manifest ORDER BY created_at`)
      expect(rows.rows[0]!.role).toBe('ANALYSIS')
      expect(Number(rows.rows[0]!.exit_code)).toBe(0)
      expect(rows.rows.slice(1).every((x) => x.role === 'DECLARATION' && Number(x.exit_code) === 3)).toBe(true)
    })

    it('output HỎNG ĐỊNH DẠNG được ghi khác với timeout', async () => {
      plan([{ raw: 'không phải JSON' }, { json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const r = await go()
      expect(r.attempts[0]!.failureClass).toBe('INVALID_JSON')
      expect(r.attempts[0]!.timedOut).toBe(false)
      const rows = await db.execute<{ failure_class: string; timed_out: boolean }>(sql`
        SELECT failure_class, timed_out FROM cursor_execution_manifest ORDER BY created_at LIMIT 1`)
      expect(rows.rows[0]!.failure_class).toBe('INVALID_JSON')
      expect(rows.rows[0]!.timed_out).toBe(false)
    })
  })

  describe('bất biến sau khi lượt 2 bắt đầu', () => {
    it('không sửa được payload phân tích, không sửa được tập nghĩa vụ', async () => {
      plan([{ json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const r = await go()
      await expect(
        db.update(schema.cursorAnalysisResult).set({ payloadHash: H('9') })
          .where(eq(schema.cursorAnalysisResult.llmExecutionId, r.analysisExecutionId!)),
      ).rejects.toThrow(/IMMUTABLE_CURSOR_RESULT/)
      await expect(
        db.update(schema.cursorClaimObligation).set({ obligationCount: 99 })
          .where(eq(schema.cursorClaimObligation.analysisExecutionId, r.analysisExecutionId!)),
      ).rejects.toThrow(/IMMUTABLE_OBLIGATION_SET/)
    })
  })

  describe('tất định', () => {
    it('cùng gói cho cùng băm prompt và cùng thứ tự nghĩa vụ, hai lần chạy', async () => {
      plan([{ json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const first = await go()
      await db.execute(sql`TRUNCATE TABLE cursor_claim_obligation, cursor_analysis_result,
        cursor_execution_manifest, analysis_validation, cursor_analysis_request CASCADE`)
      await db.execute(sql`DELETE FROM llm_execution`)
      plan([{ json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const second = await go()
      expect(second.promptHash).toBe(first.promptHash)
      expect(second.obligationSetHash).toBe(first.obligationSetHash)
      expect(second.analysisPayloadHash).toBe(first.analysisPayloadHash)
      expect(second.declarationPromptBytes).toBe(first.declarationPromptBytes)
    })
  })

/**
 * G6 — PHÂN LOẠI THẤT BẠI VÀ NGỮ NGHĨA THỬ LẠI của chặng hợp nhất.
 *
 * Trọng tâm: một bản khai SAI NGỮ NGHĨA phải sửa được mà KHÔNG chạy lại lượt
 * phân tích, và mọi lần thử — kể cả hỏng — phải để lại bằng chứng đọc được.
 */
  describe('G6 — phân loại thất bại hợp nhất và thử lại', () => {

    it('khai lần 1 hỏng S1, lần 2 ĐẠT: cả hai đều còn dấu vết, chỉ một cấp phép', async () => {
      // Lần 1 khai chủ ngữ KHÔNG có trong ô -> S1 chặn ở chặng hợp nhất.
      // Lần 2 khai đúng -> đạt.
      const good = declarationFor(ANALYSIS)
      const bad = {
        ...good,
        declarations: good.declarations.map((d) => ({ ...d, subjectMetric: 'packaging', relatedMetric: 'NONE' })),
      }
      plan([{ json: ANALYSIS }, { json: bad }, { json: good }])
      const r = await go()

      expect(r.status, JSON.stringify(r.declarationAttempts.map((a) => a.repairErrors))).toBe('SUCCEEDED')
      // Lượt PHÂN TÍCH chạy đúng MỘT lần — một lần thử độ ổn định duy nhất.
      expect(r.attempts).toHaveLength(1)
      expect(r.declarationAttempts).toHaveLength(2)
      expect(await roleCount('ANALYSIS')).toBe(1)
      expect(await roleCount('DECLARATION')).toBe(2)

      // Tập nghĩa vụ KHÔNG sinh lại.
      expect((await counts()).obligations).toBe(1)

      // BẰNG CHỨNG: hai phán quyết COMPOSITE, một hỏng một đạt, đều đọc được.
      const verdicts = await db.execute<{ passed: boolean; llm_execution_id: string }>(sql`
        SELECT passed, llm_execution_id FROM analysis_validation
        WHERE stage = 'COMPOSITE' ORDER BY created_at`)
      expect(verdicts.rows).toHaveLength(2)
      expect(verdicts.rows.map((v) => v.passed)).toEqual([false, true])

      // QUYỀN: đúng MỘT kết quả chính thức, gắn vào lần khai ĐẠT.
      const results = await db.execute<{ llm_execution_id: string }>(sql`
        SELECT llm_execution_id FROM cursor_analysis_result WHERE result_role = 'COMPOSITE'`)
      expect(results.rows).toHaveLength(1)
      expect(results.rows[0]!.llm_execution_id).toBe(verdicts.rows[1]!.llm_execution_id)
      expect(r.resultId).toBeTruthy()
    })

    it('phán quyết hỏng ghi được nhiều lần; phán quyết ĐẠT thứ hai bị chặn', async () => {
      const good = declarationFor(ANALYSIS)
      const bad = {
        ...good,
        declarations: good.declarations.map((d) => ({ ...d, subjectMetric: 'packaging', relatedMetric: 'NONE' })),
      }
      plan([{ json: ANALYSIS }, { json: bad }, { json: bad }, { json: bad }])
      const r = await go()
      expect(r.status).not.toBe('SUCCEEDED')
      expect(r.compositeFailureClass).toBe('DECLARATION_SEMANTIC')

      // BA phán quyết KHÔNG ĐẠT cùng tồn tại — bằng chứng không bị chặn.
      const failed = await db.execute<{ n: number }>(sql`
        SELECT count(*)::int n FROM analysis_validation WHERE stage='COMPOSITE' AND passed = false`)
      expect(Number(failed.rows[0]!.n)).toBe(3)
      // KHÔNG có kết quả chính thức nào.
      const res = await db.execute<{ n: number }>(sql`
        SELECT count(*)::int n FROM cursor_analysis_result WHERE result_role='COMPOSITE'`)
      expect(Number(res.rows[0]!.n)).toBe(0)
    })

    it('lỗi ngữ nghĩa KHÔNG chạy lại lượt phân tích và KHÔNG đổi văn xuôi', async () => {
      const good = declarationFor(ANALYSIS)
      const bad = {
        ...good,
        declarations: good.declarations.map((d) => ({ ...d, subjectMetric: 'packaging', relatedMetric: 'NONE' })),
      }
      plan([{ json: ANALYSIS }, { json: bad }, { json: good }])
      const r = await go()
      const analysisRows = await db.execute<{ n: number; payload_hash: string }>(sql`
        SELECT count(*)::int n, min(payload_hash) payload_hash
        FROM cursor_analysis_result WHERE result_role = 'ANALYSIS'`)
      expect(Number(analysisRows.rows[0]!.n)).toBe(1)
      expect(analysisRows.rows[0]!.payload_hash).toBe(r.analysisPayloadHash)
    })

    it('thất bại TOÀN VẸN không được đối xử như lỗi mô hình', async () => {
      // Xoá tập nghĩa vụ ngay sau khi lượt 1 đạt là bất khả từ ngoài (bất biến),
      // nên dựng ca này bằng cách cho lượt 2 dội SAI băm: đó là lỗi TOÀN VẸN mà
      // bản khai gây ra được, và nó phải KHÔNG được thử lại nhiều lần vô ích.
      const good = declarationFor(ANALYSIS)
      plan([
        { json: ANALYSIS },
        { json: { ...good, obligationSetHash: 'f'.repeat(64) } },
        { json: { ...good, obligationSetHash: 'f'.repeat(64) } },
        { json: { ...good, obligationSetHash: 'f'.repeat(64) } },
      ])
      const r = await go()
      expect(r.status).not.toBe('SUCCEEDED')
      // Băm lệch bị chặn ở CHẶNG DECLARATION (trước hợp nhất), nên không có phán
      // quyết COMPOSITE nào — và cũng không có kết quả nào.
      const res = await db.execute<{ n: number }>(sql`
        SELECT count(*)::int n FROM cursor_analysis_result WHERE result_role='COMPOSITE'`)
      expect(Number(res.rows[0]!.n)).toBe(0)
    })

    it('bản khai của mỗi lần thử được lưu RIÊNG và BẤT BIẾN', async () => {
      const good = declarationFor(ANALYSIS)
      const bad = {
        ...good,
        declarations: good.declarations.map((d) => ({ ...d, subjectMetric: 'packaging', relatedMetric: 'NONE' })),
      }
      plan([{ json: ANALYSIS }, { json: bad }, { json: good }])
      await go()
      const decls = await db.execute<{ n: number }>(sql`
        SELECT count(*)::int n FROM cursor_declaration_result`)
      // Cả hai lần khai đều qua chặng DECLARATION nên cả hai đều được lưu.
      expect(Number(decls.rows[0]!.n)).toBe(2)
    })
})

  describe('G7 — đồng thuận nguồn gốc trên MỌI bề mặt', () => {
    it('bản kê, tập nghĩa vụ, kết quả và `_meta` nói CÙNG một điều', async () => {
      plan([{ json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const r = await go()
      expect(r.status).toBe('SUCCEEDED')

      const res = (await db.execute<Record<string, unknown>>(sql`
        SELECT payload, analysis_payload_hash, obligation_set_hash, llm_execution_id
        FROM cursor_analysis_result WHERE result_role = 'COMPOSITE' LIMIT 1`)).rows[0]!
      const man = (await db.execute<Record<string, unknown>>(sql`
        SELECT analysis_execution_id, obligation_generator_version, declaration_prompt_version,
               declaration_prompt_source_hash, composite_validator_version,
               analysis_payload_hash, obligation_set_hash, validator_hash, schema_hash,
               prompt_source_hash, tool_name
        FROM cursor_execution_manifest WHERE llm_execution_id = ${res.llm_execution_id as string}`)).rows[0]!
      const ob = (await db.execute<Record<string, unknown>>(sql`
        SELECT analysis_hash, obligation_set_hash, generator_version, obligation_count
        FROM cursor_claim_obligation
        WHERE analysis_execution_id = ${man.analysis_execution_id as string}`)).rows[0]!

      // Bộ đọc CHUẨN: gỡ `_meta`, kiểm nó, rồi kiểm thân bằng schema nghiêm ngặt.
      const parsed = parseStoredCompositePayload(res.payload, {
        analysisExecutionId: man.analysis_execution_id as string,
        declarationExecutionId: res.llm_execution_id as string,
        analysisPayloadHash: res.analysis_payload_hash as string,
        obligationSetHash: res.obligation_set_hash as string,
        obligationCount: Number(ob.obligation_count),
      })
      expect(parsed.ok, JSON.stringify(parsed.issues)).toBe(true)

      // So THEO CẶP, với đúng những trường mà cả hai bề mặt CÓ MANG.
      //
      // Một danh sách phẳng cho mọi bề mặt là sai: hàng tập nghĩa vụ ra đời
      // TRƯỚC lượt khai báo nên nó không thể mang `declarationPromptVersion`, và
      // hàng kết quả chỉ mang hai băm neo. Đòi chúng mang thứ chúng không có thì
      // "thiếu" mất hết ý nghĩa và phép so không còn phát hiện được lệch thật.
      const metaSurface = parsed.meta!
      const pairs: Array<[string, Record<string, unknown>, string[]]> = [
        ['manifest', {
          analysisPayloadHash: man.analysis_payload_hash,
          obligationSetHash: man.obligation_set_hash,
          obligationGeneratorVersion: man.obligation_generator_version,
          declarationPromptVersion: man.declaration_prompt_version,
          compositeValidatorVersion: man.composite_validator_version,
          declarationPromptSourceHash: man.declaration_prompt_source_hash,
          validatorHash: man.validator_hash,
          schemaHash: man.schema_hash,
          promptSourceHash: man.prompt_source_hash,
        }, [
          'analysisPayloadHash', 'obligationSetHash', 'obligationGeneratorVersion',
          'declarationPromptVersion', 'compositeValidatorVersion',
          'declarationPromptSourceHash', 'validatorHash', 'schemaHash', 'promptSourceHash',
        ]],
        ['obligationRow', {
          analysisPayloadHash: ob.analysis_hash,
          obligationSetHash: ob.obligation_set_hash,
          obligationGeneratorVersion: ob.generator_version,
        }, ['analysisPayloadHash', 'obligationSetHash', 'obligationGeneratorVersion']],
        ['resultRow', {
          analysisPayloadHash: res.analysis_payload_hash,
          obligationSetHash: res.obligation_set_hash,
        }, ['analysisPayloadHash', 'obligationSetHash']],
      ]
      for (const [name, surface, fields] of pairs) {
        const agreement = checkProvenanceAgreement({ meta: metaSurface, [name]: surface }, fields)
        expect(
          agreement.mismatches,
          `LỆCH meta vs ${name}: ${JSON.stringify(agreement.mismatches, null, 1)}`,
        ).toEqual([])
        expect(
          agreement.missing,
          `THIẾU meta vs ${name}: ${JSON.stringify(agreement.missing)}`,
        ).toEqual([])
      }
    })

    it('`_meta` mang ĐÚNG id hai execution và SÁU phiên bản hợp đồng', async () => {
      plan([{ json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const r = await go()
      const res = (await db.execute<{ payload: Record<string, unknown> }>(sql`
        SELECT payload FROM cursor_analysis_result WHERE result_role='COMPOSITE' LIMIT 1`)).rows[0]!
      const meta = res.payload._meta as Record<string, unknown>
      expect(meta.analysisExecutionId).toBe(r.analysisExecutionId)
      expect(meta.declarationExecutionId).toBe(r.declarationExecutionId)
      for (const k of [
        'analysisSchemaVersion', 'analysisPromptVersion', 'obligationGeneratorVersion',
        'declarationSchemaVersion', 'declarationPromptVersion', 'compositeValidatorVersion',
      ]) {
        expect(meta[k], `thiếu phiên bản "${k}"`).toBeDefined()
      }
    })

    it('`_meta` mang MÔI TRƯỜNG: git, băm diff bẩn, lockfile, package, node, tệp thực thi', async () => {
      plan([{ json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const r = await go()
      const res = (await db.execute<{ payload: Record<string, unknown> }>(sql`
        SELECT payload FROM cursor_analysis_result WHERE result_role='COMPOSITE' LIMIT 1`)).rows[0]!
      const meta = res.payload._meta as Record<string, unknown>
      for (const k of ['gitCommit', 'gitDirty', 'gitDirtyDiffHash', 'lockfileHash', 'packageVersion', 'nodeVersion']) {
        expect(meta[k], `\`_meta.${k}\` thiếu`).toBeDefined()
      }
      // Băm diff bẩn là BĂM chứ không phải cờ: hai lần chạy với hai thay đổi
      // chưa commit KHÁC NHAU phải phân biệt được.
      expect(String(meta.gitDirtyDiffHash)).toMatch(/^[0-9a-f]{64}$/)
      // Đường dẫn THẬT của tệp thực thi nằm ở bản kê (sau khi bỏ symlink).
      const man = (await db.execute<{ tool_name: string }>(sql`
        SELECT tool_name FROM cursor_execution_manifest WHERE llm_execution_id = ${r.analysisExecutionId!}`)).rows[0]!
      expect(man.tool_name.length).toBeGreaterThan(0)
      expect(man.tool_name).not.toContain('..')
    })

    it('bản ghi nguồn gốc DÙNG CHUNG khớp `_meta` — không bề mặt nào tự gom riêng', async () => {
      plan([{ json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      await go()
      const res = (await db.execute<{ payload: Record<string, unknown> }>(sql`
        SELECT payload FROM cursor_analysis_result WHERE result_role='COMPOSITE' LIMIT 1`)).rows[0]!
      const meta = res.payload._meta as Record<string, unknown>
      for (const k of [
        'validatorHash', 'schemaHash', 'promptSourceHash', 'declarationPromptSourceHash',
        'obligationGeneratorHash', 'compositeSourceHash', 'lockfileHash',
        'analysisSchemaVersion', 'compositeValidatorVersion', 'gitCommit',
      ] as const) {
        expect(meta[k], `lệch ở "${k}"`).toBe(CONTRACT_PROVENANCE[k])
      }
    })
  })

  /* ---------------------------------------------------------------------
   * G7 — MA TRẬN PHỦ: mọi bề mặt, mọi trường bắt buộc, mọi quan hệ bằng nhau
   * ------------------------------------------------------------------ */
  describe('G7 — ma trận phủ nguồn gốc trên MỌI bề mặt', () => {
    /** Gom TẤT CẢ bề mặt của một lần chạy vừa xong, đọc thẳng từ database. */
    async function collectSurfaces(r: Awaited<ReturnType<typeof go>>) {
      const one = async (q: ReturnType<typeof sql>) =>
        (await db.execute<Record<string, unknown>>(q)).rows[0] as Record<string, unknown> | undefined

      const req = await one(sql`
        SELECT id, analysis_run_id, channel_id, analysis_package_id, package_hash, prompt_hash
        FROM cursor_analysis_request WHERE id = ${r.requestId!}::uuid`)
      const manifest = async (execId: string) => one(sql`
        SELECT llm_execution_id, execution_role, attempt_number, parent_execution_id, tool_name,
               analysis_execution_id, schema_version, prompt_version, validator_hash, schema_hash,
               prompt_source_hash, obligation_generator_version, declaration_prompt_version,
               declaration_prompt_source_hash, composite_validator_version,
               analysis_payload_hash, obligation_set_hash, failure_class
        FROM cursor_execution_manifest WHERE llm_execution_id = ${execId}::uuid`)
      const ob = await one(sql`
        SELECT analysis_execution_id, analysis_hash, obligation_set_hash, generator_version, obligation_count
        FROM cursor_claim_obligation WHERE analysis_execution_id = ${r.analysisExecutionId!}::uuid`)
      const val = async (execId: string, stage: string) => one(sql`
        SELECT llm_execution_id, stage, passed FROM analysis_validation
        WHERE llm_execution_id = ${execId}::uuid AND stage = ${stage}`)
      const res = await one(sql`
        SELECT llm_execution_id, result_role, schema_version, payload, payload_hash,
               analysis_payload_hash, obligation_set_hash
        FROM cursor_analysis_result WHERE result_role = 'COMPOSITE' LIMIT 1`)

      const aMan = (await manifest(r.analysisExecutionId!))!
      const dMan = (await manifest(r.declarationExecutionId!))!
      const camel = (row: Record<string, unknown>, map: Record<string, string>) =>
        Object.fromEntries(Object.entries(map).map(([k, col]) => [k, row[col]]))

      const parsed = parseStoredCompositePayload(res!.payload)
      expect(parsed.ok, JSON.stringify(parsed.issues)).toBe(true)

      const artifact = buildArtifactMeta(r, CONTRACT_PROVENANCE, parsed.meta!, {
        channelLabel: 'hinh_su', durationMs: 1, writtenAt: '2026-08-06T00:00:00Z',
        outputSchemaVersion: String(r.output!.schemaVersion),
      })
      const index = buildIndexProvenance(CONTRACT_PROVENANCE, {
        generatedAt: '2026-08-06T00:00:00Z', schemaVersion: '3.0', mode: 'successes=1',
      })

      return {
        request: camel(req!, {
          requestId: 'id', analysisRunId: 'analysis_run_id', channelId: 'channel_id',
          analysisPackageId: 'analysis_package_id', packageHash: 'package_hash', promptHash: 'prompt_hash',
        }),
        analysisExecution: camel(aMan, {
          llmExecutionId: 'llm_execution_id', executionRole: 'execution_role',
          attemptNumber: 'attempt_number', toolName: 'tool_name', schemaVersion: 'schema_version',
          promptVersion: 'prompt_version', validatorHash: 'validator_hash', schemaHash: 'schema_hash',
          promptSourceHash: 'prompt_source_hash',
        }),
        obligationSet: camel(ob!, {
          analysisExecutionId: 'analysis_execution_id', analysisPayloadHash: 'analysis_hash',
          obligationSetHash: 'obligation_set_hash', obligationGeneratorVersion: 'generator_version',
          obligationCount: 'obligation_count',
        }),
        declarationExecution: camel(dMan, {
          llmExecutionId: 'llm_execution_id', executionRole: 'execution_role',
          attemptNumber: 'attempt_number', toolName: 'tool_name',
          analysisExecutionId: 'analysis_execution_id', schemaVersion: 'schema_version',
          promptVersion: 'prompt_version', validatorHash: 'validator_hash', schemaHash: 'schema_hash',
          promptSourceHash: 'prompt_source_hash',
          obligationGeneratorVersion: 'obligation_generator_version',
          declarationPromptVersion: 'declaration_prompt_version',
          declarationPromptSourceHash: 'declaration_prompt_source_hash',
          compositeValidatorVersion: 'composite_validator_version',
          analysisPayloadHash: 'analysis_payload_hash', obligationSetHash: 'obligation_set_hash',
        }),
        analysisValidation: camel((await val(r.analysisExecutionId!, 'ANALYSIS'))!, {
          llmExecutionId: 'llm_execution_id', stage: 'stage', passed: 'passed',
        }),
        declarationValidation: camel((await val(r.declarationExecutionId!, 'DECLARATION'))!, {
          llmExecutionId: 'llm_execution_id', stage: 'stage', passed: 'passed',
        }),
        compositeValidation: camel((await val(r.declarationExecutionId!, 'COMPOSITE'))!, {
          llmExecutionId: 'llm_execution_id', stage: 'stage', passed: 'passed',
        }),
        resultRow: camel(res!, {
          llmExecutionId: 'llm_execution_id', resultRole: 'result_role', schemaVersion: 'schema_version',
          payloadHash: 'payload_hash', analysisPayloadHash: 'analysis_payload_hash',
          obligationSetHash: 'obligation_set_hash',
        }),
        storedMeta: parsed.meta!,
        artifactMeta: artifact,
        indexJson: index,
        attemptTable: {
          attemptNumber: dMan.attempt_number, llmExecutionId: dMan.llm_execution_id,
          executionRole: dMan.execution_role, failureClass: dMan.failure_class,
          passed: true,
        },
      }
    }

    it('MƯỜI HAI bề mặt: đủ trường bắt buộc, không trường lạ, mọi quan hệ khớp', async () => {
      plan([{ json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const r = await go()
      expect(r.status).toBe('SUCCEEDED')
      const surfaces = await collectSurfaces(r)

      const expected: ProvenanceSurfaceName[] = [
        'request', 'analysisExecution', 'obligationSet', 'declarationExecution',
        'analysisValidation', 'declarationValidation', 'compositeValidation',
        'resultRow', 'storedMeta', 'artifactMeta', 'indexJson', 'attemptTable',
      ]
      const report = checkProvenanceCoverage(surfaces, expected)
      expect(report.missing, `THIẾU: ${JSON.stringify(report.missing)}`).toEqual([])
      expect(report.unexpected, `TRƯỜNG LẠ: ${JSON.stringify(report.unexpected)}`).toEqual([])
      expect(report.mismatches, `LỆCH: ${JSON.stringify(report.mismatches, null, 1)}`).toEqual([])
      expect(report.absentSurfaces, `VẮNG: ${report.absentSurfaces.join(', ')}`).toEqual([])
      expect(report.ok).toBe(true)
    })

    it('bề mặt SỬA ĐỔI dù chỉ một băm -> ma trận bắt được', async () => {
      // Phép kiểm chỉ có giá trị nếu nó biết KÊU. Ở đây bơm sai đúng một trường
      // vào một bề mặt đã lấy từ database thật, và đòi nó phải bị bắt.
      plan([{ json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const surfaces = await collectSurfaces(await go())
      const tampered = {
        ...surfaces,
        resultRow: { ...surfaces.resultRow, obligationSetHash: 'b'.repeat(64) },
      }
      const report = checkProvenanceCoverage(tampered, ['resultRow', 'obligationSet', 'storedMeta'])
      expect(report.ok).toBe(false)
      expect(report.mismatches.map((m) => m.field)).toContain('obligationSetHash')
    })

    it('bề mặt bị BỎ TRỐNG một trường bắt buộc -> ma trận bắt được', async () => {
      plan([{ json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const surfaces = await collectSurfaces(await go())
      const stripped: Record<string, unknown> = { ...surfaces.declarationExecution }
      delete stripped.obligationSetHash
      const report = checkProvenanceCoverage(
        { ...surfaces, declarationExecution: stripped }, ['declarationExecution'])
      expect(report.ok).toBe(false)
      expect(report.missing).toContainEqual({ surface: 'declarationExecution', field: 'obligationSetHash' })
    })

    it('DANH TÍNH của `INDEX.json`: request, run, phân tích, khai báo, kiểm định, kết quả', async () => {
      plan([{ json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const r = await go()
      // Gọi ĐÚNG hàm mà `INDEX.json` gọi — không dựng lại khối này trong test.
      const id = runIdentity(r)
      expect(missingIdentityFields(id), `thiếu: ${missingIdentityFields(id).join(', ')}`).toEqual([])

      // Mỗi id phải TRA RA một hàng thật, không chỉ khác null.
      const exists = async (table: string, col: string, v: string) =>
        Number((await db.execute<{ n: number }>(sql`
          SELECT count(*)::int n FROM ${sql.raw(table)} WHERE ${sql.raw(col)} = ${v}::uuid`)).rows[0]!.n)
      expect(await exists('cursor_analysis_request', 'id', id.requestId!)).toBe(1)
      expect(await exists('analysis_run', 'id', id.analysisRunId!)).toBe(1)
      expect(await exists('channel', 'id', id.channelId!)).toBe(1)
      expect(await exists('llm_execution', 'id', id.analysisExecutionId!)).toBe(1)
      expect(await exists('llm_execution', 'id', id.declarationExecutionId!)).toBe(1)
      expect(await exists('analysis_validation', 'id', id.compositeValidationId!)).toBe(1)
      expect(await exists('cursor_analysis_result', 'id', id.resultId!)).toBe(1)
    })

    it('lần chạy HỎNG: danh tính vẫn ghi được, và phán quyết trượt vẫn tra ra hàng thật', async () => {
      // Bảng danh tính không được chỉ hoạt động trên đường đạt: một lần chạy
      // hỏng mà không truy được thì đúng cái cần điều tra lại là cái mất dấu.
      const good = declarationFor(ANALYSIS)
      const bad = {
        ...good,
        declarations: good.declarations.map((d) => ({ ...d, subjectMetric: 'packaging', relatedMetric: 'NONE' })),
      }
      plan([{ json: ANALYSIS }, { json: bad }, { json: bad }, { json: bad }])
      const r = await go()
      expect(r.status).not.toBe('SUCCEEDED')
      const id = runIdentity(r)
      expect(id.resultId).toBeNull()
      expect(id.analysisExecutionId).not.toBeNull()
      expect(id.compositeValidationId).not.toBeNull()
      // `missingIdentityFields` CHỈ đòi hỏi ở lần chạy ĐẠT — nên lần hỏng không
      // bị báo thiếu, mà vẫn giữ được mọi id nó thật sự có.
      expect(missingIdentityFields(id)).toEqual([])
      const v = await db.execute<{ passed: boolean }>(sql`
        SELECT passed FROM analysis_validation WHERE id = ${id.compositeValidationId!}::uuid`)
      expect(v.rows[0]!.passed).toBe(false)
    })

    it('G8 — execution khai báo được CHỐT `SUCCEEDED` khi cấp phép kết quả', async () => {
      // Không có bước chốt này, execution khai báo nằm mãi ở `RUNNING`, và truy
      // vấn độ ổn định — vốn đòi `e.status='SUCCEEDED'` VÀ `v.passed=true` —
      // trả về RỖNG với MỌI lô. Báo cáo khi ấy in "cần ít nhất 2 lần chạy" rồi
      // thoát 0: một cổng luôn xanh vì chưa bao giờ nhìn thấy dữ liệu.
      plan([{ json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const r = await go()
      expect(r.status).toBe('SUCCEEDED')

      const st = await db.execute<{ status: string }>(sql`
        SELECT status FROM llm_execution WHERE id = ${r.declarationExecutionId!}::uuid`)
      expect(st.rows[0]!.status).toBe('SUCCEEDED')

      // Truy vấn ĐỘ ỔN ĐỊNH phải thấy đúng một dòng — đây mới là điều cần chứng
      // minh, chứ không phải riêng giá trị cột.
      const vis = await db.execute<{ n: number }>(sql`
        SELECT count(*)::int n
        FROM cursor_analysis_result res
        JOIN llm_execution e ON e.id = res.llm_execution_id
        JOIN analysis_validation v ON v.llm_execution_id = e.id AND v.stage = 'COMPOSITE'
        WHERE v.passed = true AND e.status = 'SUCCEEDED' AND res.result_role = 'COMPOSITE'`)
      expect(Number(vis.rows[0]!.n)).toBe(1)
    })

    it('G8 — lần khai báo TRƯỢT hợp nhất KHÔNG được chốt `SUCCEEDED`', async () => {
      // Chốt trạng thái phải gắn với "đã sinh hiện vật chính thức", không phải
      // "đã chạy xong". Nếu không, một lần trượt ngữ nghĩa vẫn lọt vào quần thể
      // đã đạt của mọi truy vấn ổn định.
      const good = declarationFor(ANALYSIS)
      const bad = {
        ...good,
        declarations: good.declarations.map((d) => ({ ...d, subjectMetric: 'packaging', relatedMetric: 'NONE' })),
      }
      plan([{ json: ANALYSIS }, { json: bad }, { json: bad }, { json: bad }])
      const r = await go()
      expect(r.status).not.toBe('SUCCEEDED')

      const st = await db.execute<{ status: string }>(sql`
        SELECT e.status FROM llm_execution e
        JOIN cursor_execution_manifest m ON m.llm_execution_id = e.id
        WHERE m.execution_role = 'DECLARATION'`)
      expect(st.rows.every((x) => x.status !== 'SUCCEEDED')).toBe(true)
    })

    it('bề mặt SỬA LỖI của CẢ HAI lượt cũng đủ trường bắt buộc', async () => {
      // Bốn bề mặt gốc dễ nhớ; hai bề mặt SỬA LỖI thì không, vì chúng chỉ xuất
      // hiện khi có lần thử lại. Đúng những bề mặt hiếm gặp mới là chỗ một
      // trường bị bỏ quên nằm im lâu nhất.
      const good = declarationFor(ANALYSIS)
      const badDecl = {
        ...good,
        declarations: good.declarations.map((d) => ({ ...d, subjectMetric: 'packaging', relatedMetric: 'NONE' })),
      }
      // Lượt 1 hỏng JSON -> sinh execution SỬA LỖI của lượt phân tích.
      // Lượt 2 trượt ngữ nghĩa -> sinh execution SỬA LỖI của lượt khai báo.
      plan([{ raw: 'không phải JSON' }, { json: ANALYSIS }, { json: badDecl }, { json: good }])
      const r = await go()
      expect(r.status, JSON.stringify(r.declarationAttempts.map((a) => a.repairErrors))).toBe('SUCCEEDED')

      const repairs = await db.execute<Record<string, unknown>>(sql`
        SELECT llm_execution_id, execution_role, attempt_number, parent_execution_id, tool_name,
               analysis_execution_id, schema_version, prompt_version, validator_hash, schema_hash,
               prompt_source_hash, obligation_generator_version, declaration_prompt_version,
               declaration_prompt_source_hash, composite_validator_version,
               analysis_payload_hash, obligation_set_hash
        FROM cursor_execution_manifest WHERE parent_execution_id IS NOT NULL
        ORDER BY execution_role, attempt_number`)
      // Phải có ĐÚNG hai: một của mỗi vai. Không có nghĩa là test không kiểm gì.
      expect(repairs.rows.map((x) => x.execution_role)).toEqual(['ANALYSIS', 'DECLARATION'])

      const map: Record<string, string> = {
        llmExecutionId: 'llm_execution_id', executionRole: 'execution_role',
        attemptNumber: 'attempt_number', parentExecutionId: 'parent_execution_id',
        toolName: 'tool_name', schemaVersion: 'schema_version', promptVersion: 'prompt_version',
        validatorHash: 'validator_hash', schemaHash: 'schema_hash', promptSourceHash: 'prompt_source_hash',
        analysisExecutionId: 'analysis_execution_id',
        obligationGeneratorVersion: 'obligation_generator_version',
        declarationPromptVersion: 'declaration_prompt_version',
        declarationPromptSourceHash: 'declaration_prompt_source_hash',
        compositeValidatorVersion: 'composite_validator_version',
        analysisPayloadHash: 'analysis_payload_hash', obligationSetHash: 'obligation_set_hash',
      }
      const pick = (row: Record<string, unknown>, keep: string[]) =>
        Object.fromEntries(keep.map((k) => [k, row[map[k]!]]))

      const aRepair = repairs.rows.find((x) => x.execution_role === 'ANALYSIS')!
      const dRepair = repairs.rows.find((x) => x.execution_role === 'DECLARATION')!
      const report = checkProvenanceCoverage(
        {
          analysisRepairExecution: pick(aRepair, [...PROVENANCE_MATRIX.analysisRepairExecution.required]),
          declarationRepairExecution: pick(dRepair, [...PROVENANCE_MATRIX.declarationRepairExecution.required]),
        },
        ['analysisRepairExecution', 'declarationRepairExecution'],
      )
      expect(report.missing, `THIẾU: ${JSON.stringify(report.missing)}`).toEqual([])
      expect(report.unexpected, `TRƯỜNG LẠ: ${JSON.stringify(report.unexpected)}`).toEqual([])
      expect(report.ok).toBe(true)

      // Chuỗi sửa lỗi nối vào ĐÚNG vai của nó — không bắc cầu sang lượt kia.
      expect(aRepair.parent_execution_id).not.toBe(dRepair.parent_execution_id)
      expect(dRepair.analysis_execution_id).toBe(r.analysisExecutionId)
    })

    it('TRẦN lần thử dùng CHUNG: ba lần khai trượt ngữ nghĩa, không có lần thứ tư', async () => {
      const good = declarationFor(ANALYSIS)
      const bad = {
        ...good,
        declarations: good.declarations.map((d) => ({ ...d, subjectMetric: 'packaging', relatedMetric: 'NONE' })),
      }
      // Kịch bản có THỪA phản hồi tốt ở cuối: nếu vòng lặp đặt lại trần thì nó
      // sẽ tiêu phản hồi thứ năm và ĐẠT. Trần đúng thì nó không bao giờ tới đó.
      plan([{ json: ANALYSIS }, { json: bad }, { json: bad }, { json: bad }, { json: good }])
      const r = await go()
      expect(r.status).not.toBe('SUCCEEDED')
      expect(r.declarationAttempts).toHaveLength(3)
      expect(r.attempts).toHaveLength(1)
      const n = await db.execute<{ n: number }>(sql`
        SELECT count(*)::int n FROM cursor_execution_manifest WHERE execution_role = 'DECLARATION'`)
      expect(Number(n.rows[0]!.n)).toBe(3)
    })
  })

  /* ---------------------------------------------------------------------
   * G-R3 — KHÔNG nghĩa vụ nào: vẫn phải đi hết đường CẤP PHÉP
   * ------------------------------------------------------------------ */
  describe('CODEX R6 — vòng chạy THẬT phải quét văn xuôi, không chỉ hàm trợ giúp', () => {
    /*
     * Các test trước gọi thẳng `validateProseOnly`, nên xoá hẳn lời gọi trong
     * `run.ts` mà chúng vẫn xanh. Hai ca dưới đây lái CLI GIẢ nên chúng đi qua
     * đúng nhánh `!json` của vòng chạy thật.
     */
    it('lượt PHÂN TÍCH trả về TOÀN văn xuôi có khẳng định -> KHÔNG thử lại', async () => {
      plan([{ raw: 'CTR của kênh đang thấp.' }])
      const r = await go()
      expect(r.status).not.toBe('SUCCEEDED')
      const cls = r.analysisAttempts.map((a) => a.failureClass)
      expect(cls, `lớp thất bại: ${cls.join(',')}`).toContain('UNSUPPORTED_CLAIM')
      // Không được thử lại: khẳng định bị cấm là thất bại NỘI DUNG.
      expect(r.analysisAttempts.length, 'đã thử lại một khẳng định bị cấm').toBe(1)
    })

    it('CLI thoát KHÁC 0 nhưng đã in khẳng định bị cấm -> KHÔNG thử lại', async () => {
      /*
       * `CLI_NONZERO_EXIT` / `CLI_TIMEOUT` / `OUTPUT_TOO_LARGE` đều RETRYABLE.
       * Nếu nhánh `if (execFailure)` bỏ qua phần quét thì mô hình chỉ cần in một
       * khẳng định bị cấm rồi thoát khác 0 là câu ấy biến mất khỏi hồ sơ và vòng
       * chạy tự thử lại.
       */
      plan([{ raw: 'CTR của kênh đang thấp.', exit: 1 }])
      const r = await go()
      expect(r.status).not.toBe('SUCCEEDED')
      const cls = r.analysisAttempts.map((a) => a.failureClass)
      expect(cls, `lớp thất bại: ${cls.join(',')}`).toContain('UNSUPPORTED_CLAIM')
      expect(r.analysisAttempts.length, 'đã thử lại một khẳng định bị cấm').toBe(1)
    })

    it('RANH GIỚI: CLI thoát khác 0 mà KHÔNG in gì -> VẪN thử lại được', async () => {
      // Hỏng hạ tầng thật không sinh văn xuôi, nên nó phải giữ nguyên lớp kỹ
      // thuật. Siết quá tay ở đây sẽ biến mọi trục trặc mạng thành thất bại vĩnh viễn.
      plan([{ raw: '', exit: 1 }, { json: ANALYSIS }, { json: declarationFor(ANALYSIS) }])
      const r = await go()
      const cls = r.analysisAttempts.map((a) => a.failureClass)
      expect(cls[0]).toBe('CLI_NONZERO_EXIT')
      expect(r.analysisAttempts.length, 'lỗi hạ tầng thuần phải được thử lại').toBeGreaterThan(1)
    })

    it('CODEX R16: lượt KHAI BÁO, CLI hỏng + khẳng định nhạy cảm trong JSON -> KHÔNG thử lại', async () => {
      /*
       * Khi CLI hỏng, `validateDeclarationOutput` KHÔNG chạy, nên phép quét
       * khẳng định nhạy cảm dành riêng cho lượt khai báo bị bỏ qua — và
       * `CLI_NONZERO_EXIT` thì RETRYABLE.
       */
      plan([
        { json: ANALYSIS },
        { raw: '{"extra":"CTR thấp."}', exit: 1 },
      ])
      const r = await go()
      expect(r.status).not.toBe('SUCCEEDED')
      const cls = r.declarationAttempts.map((a) => a.failureClass)
      expect(cls, `lớp thất bại: ${cls.join(',')}`).toContain('UNSUPPORTED_CLAIM')
      expect(r.declarationAttempts.length, 'đã thử lại một khẳng định bị cấm').toBe(1)
    })

    it('văn xuôi kẹp GIỮA hai object cũng bị quét', async () => {
      // `extractJson` từng trả CẢ chuỗi làm JSON khi nó bắt đầu bằng "{" và kết
      // thúc bằng "}", nên câu ở giữa biến mất và lớp là INVALID_JSON (thử lại được).
      plan([{ raw: '{"x":1} CTR của kênh đang thấp. {"y":2}' }])
      const r = await go()
      expect(r.status).not.toBe('SUCCEEDED')
      const cls = r.analysisAttempts.map((a) => a.failureClass)
      expect(cls, `lớp thất bại: ${cls.join(',')}`).toContain('UNSUPPORTED_CLAIM')
      expect(r.analysisAttempts.length).toBe(1)
    })
  })

  describe('G-R3 — lần chạy KHÔNG có ô nhạy cảm', () => {
    /** Bản phân tích SẠCH: không ô nào nhắc chỉ số nhạy cảm -> 0 nghĩa vụ. */
    const NO_SENSITIVE = {
      ...ANALYSIS,
      keyFindings: [{
        ...ANALYSIS.keyFindings[0],
        // Bỏ `limitations` nhắc CTR -> không còn ô nhạy cảm nào.
        limitations: [] as string[],
      }],
    }

    it('KHÔNG gọi LLM cho lượt khai báo, nhưng VẪN có phán quyết và kết quả', async () => {
      // Kịch bản CHỈ có phản hồi cho lượt PHÂN TÍCH. Nếu vòng chạy gọi CLI cho
      // lượt khai báo, kịch bản cạn và lần chạy sẽ hỏng — nên test này tự chứng
      // minh "không gọi LLM" chứ không chỉ khẳng định.
      plan([{ json: NO_SENSITIVE }])
      const r = await go()
      expect(r.status, JSON.stringify(r.declarationAttempts.map((a) => a.repairErrors))).toBe('SUCCEEDED')
      expect(r.obligationCount).toBe(0)
      expect(r.declarations).toEqual([])

      // MỘT lượt phân tích, MỘT lượt khai báo (tổng hợp, không gọi LLM).
      expect(await roleCount('ANALYSIS')).toBe(1)
      expect(await roleCount('DECLARATION')).toBe(1)

      // Lượt khai báo phải mang nhãn công cụ TỔNG HỢP — bằng chứng không có
      // tiến trình con nào chạy.
      const tool = await db.execute<{ tool_name: string }>(sql`
        SELECT tool_name FROM cursor_execution_manifest
        WHERE llm_execution_id = ${r.declarationExecutionId!}::uuid`)
      expect(tool.rows[0]!.tool_name).toBe(EMPTY_DECLARATION_TOOL)
    })

    it('ĐÚNG MỘT phán quyết COMPOSITE và ĐÚNG MỘT hiện vật chính thức', async () => {
      plan([{ json: NO_SENSITIVE }])
      const r = await go()
      expect(r.status).toBe('SUCCEEDED')

      const v = await db.execute<{ n: number }>(sql`
        SELECT count(*)::int n FROM analysis_validation WHERE stage = 'COMPOSITE'`)
      expect(Number(v.rows[0]!.n)).toBe(1)

      const res = await db.execute<{ n: number }>(sql`
        SELECT count(*)::int n FROM cursor_analysis_result WHERE result_role = 'COMPOSITE'`)
      expect(Number(res.rows[0]!.n)).toBe(1)

      // "Đạt" PHẢI có nghĩa là có hiện vật chính thức — không còn đường tắt.
      expect(r.resultId).not.toBeNull()
      expect(r.compositeValidationId).not.toBeNull()
      expect(r.compositePayloadHash).not.toBeNull()
      expect(missingIdentityFields(runIdentity(r))).toEqual([])
    })

    it('quy tắc NGỮ NGHĨA và BẰNG CHỨNG vẫn chạy trên đường này', async () => {
      // Bản khai rỗng KHÔNG được biến chặng hợp nhất thành hình thức: bằng chứng
      // vẫn phải neo được, và một bản phân tích có vi phạm vẫn phải bị chặn.
      plan([{ json: NO_SENSITIVE }])
      const r = await go()
      expect(r.compositeReport).not.toBeNull()
      expect(r.compositeReport!.totalEvidenceRefs).toBeGreaterThan(0)
      expect(r.compositeReport!.unresolvedEvidenceRefs).toBe(0)
      expect(r.compositeReport!.passed).toBe(true)
    })

    it('bản phân tích SẠCH nhưng có câu NHÂN QUẢ vẫn bị chặn ở lượt 1', async () => {
      const causal = {
        ...NO_SENSITIVE,
        keyFindings: [{
          ...NO_SENSITIVE.keyFindings[0],
          statement: 'CTA dày làm giảm giữ chân người xem ở nhóm Shorts của kênh này.',
        }],
      }
      plan([{ json: causal }])
      const r = await go()
      expect(r.status).not.toBe('SUCCEEDED')
      // Không có nghĩa vụ nào KHÔNG có nghĩa là bỏ qua kiểm định lượt 1.
      expect(await roleCount('DECLARATION')).toBe(0)
    })

    it('kế toán lần thử: vẫn là MỘT lần thử ổn định', async () => {
      plan([{ json: NO_SENSITIVE }])
      const r = await go()
      expect(r.attempts).toHaveLength(1)
      expect(r.analysisAttempts).toHaveLength(1)
      expect(r.declarationAttempts).toHaveLength(1)
    })
  })
})
