import { createHash } from 'node:crypto'

import { stableStringify } from '@/lib/analysis/package'
import { afterAll, beforeAll, describe, expect, it } from 'vitest'
import { eq, sql } from 'drizzle-orm'

import * as schema from '@/db/schema'
import {
  loadCompositeInputs,
  runCompositeStage,
  verifyCompositeInputs,
  type CompositeInputs,
} from '@/lib/cursor/composite'
import { buildObligationSet, hashAnalysisPayload, hashObligationSet } from '@/lib/cursor/obligation'
import { buildPrompt } from '@/lib/cursor/prompt'
import {
  ANALYSIS_SCHEMA_VERSION,
  COMPOSITE_VALIDATOR_VERSION,
  DECLARATION_SCHEMA_VERSION,
  OBLIGATION_GENERATOR_VERSION,
  type ClaimObligationSet,
  type CursorAnalysis,
} from '@/lib/cursor/schema'
import { closeTestPool, hasTestDatabase, testDb, truncateAll } from '../helpers/db'

/**
 * G5 — CẤP PHÉP KẾT QUẢ CHÍNH THỨC.
 *
 * Chặng hợp nhất là cổng CUỐI. Mọi test ở đây hỏi đúng một câu: có đường nào để
 * một hiện vật chính thức ra đời mà KHÔNG đi qua cả ba phán quyết, đúng cặp
 * execution, đúng băm không.
 *
 * Phần lớn là test PHỦ ĐỊNH, có chủ đích: một cổng chỉ được chứng minh bằng
 * những thứ nó CHẶN, không phải bằng thứ nó cho qua.
 */
describe.skipIf(!hasTestDatabase)('G5 — cấp phép kết quả chính thức (PostgreSQL thật)', () => {
  const db = testDb()
  let workspaceId: string
  let channelId: string
  let analysisRunId: string
  let requestId: string
  let promptRevisionId: string
  let seq = 5000
  const H = (c: string) => c.repeat(64)
  /** Băm payload bản khai — CÙNG công thức mà `run.ts` dùng khi ghi thật. */
  const declHash = (p: unknown) =>
    createHash('sha256').update(stableStringify(p), 'utf8').digest('hex')

  const ANALYSIS: CursorAnalysis = {
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

  const DECL = (id: string, over: Record<string, unknown> = {}) => ({
    id, subjectMetric: 'views', relatedMetric: 'impression_ctr',
    claimType: 'METHODOLOGY_LIMITATION', judgement: 'LOW', assertionStatus: 'LIMITATION',
    evidenceIds: [] as string[], requiresMissingnessDisclosure: false, ...over,
  })

  let pkgPayload: Record<string, unknown>

  beforeAll(async () => {
    await truncateAll()
    await db.execute(sql`TRUNCATE TABLE cursor_declaration_result, cursor_claim_obligation,
      cursor_analysis_result, cursor_execution_manifest, analysis_validation,
      cursor_analysis_request, analysis_package, analysis_quality, anomaly, cohort_summary,
      evidence_reference, deterministic_observation, feature_value, feature_version,
      feature_definition, video_daily_metric_history, video_daily_metric, channel_daily_metric,
      video, prompt_revision, prompt_template CASCADE`)

    const [ws] = await db.insert(schema.workspace).values({ slug: 'ws-g5', name: 'W' }).returning()
    workspaceId = ws!.id
    const [ch] = await db.insert(schema.channel)
      .values({ workspaceId, label: 'hinh_su', youtubeChannelId: 'UCg5000000000000000000', title: 'T' })
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
    analysisRunId = run!.id

    pkgPayload = {
      schemaVersion: '1.0.0', algorithmVersion: '1.0.0',
      scope: {
        workspaceId, channelId, channelLabel: 'hinh_su', channelTitle: 'K',
        reportingTimezone: 'America/Los_Angeles', windowStart: '2026-06-01',
        windowEnd: '2026-07-27', analysisRunId, inputHash: H('a'),
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
    const [pkg] = await db.insert(schema.analysisPackage).values({
      workspaceId, analysisRunId, channelId, schemaVersion: '1.0.0',
      payload: pkgPayload, payloadHash: H('a'), packageBytes: 100, rawInputBytes: 1000,
      reductionPercent: '90',
    }).returning()
    const [tpl] = await db.insert(schema.promptTemplate)
      .values({ workspaceId, key: 'cursor.analysis.channel', purpose: 'ANALYSIS' }).returning()
    const [rev] = await db.insert(schema.promptRevision).values({
      templateId: tpl!.id, workspaceId, revisionNumber: 1, body: 'p',
      contentHash: H('a'), authoredBy: 'HUMAN',
    }).returning()
    promptRevisionId = rev!.id
    const [req] = await db.insert(schema.cursorAnalysisRequest).values({
      workspaceId, channelId, analysisRunId, analysisPackageId: pkg!.id,
      packageHash: H('a'), promptRevisionId, promptHash: H('b'), promptBytes: 10,
    }).returning()
    requestId = req!.id
  })

  afterAll(async () => { await closeTestPool() })

  async function execution(): Promise<string> {
    const [e] = await db.insert(schema.llmExecution).values({
      workspaceId, analysisRunId, promptRevisionId, provider: 'CURSOR_CLI',
      iteration: 1, executionSequence: seq++, status: 'REJECTED_SCHEMA',
      rawOutputHash: H('a'), validationError: { failureClass: 'SCHEMA_MISMATCH' },
      startedAt: new Date(), finishedAt: new Date(), durationMs: 1,
    }).returning()
    return e!.id
  }

  const BASE = {
    toolName: '/usr/local/bin/cursor-agent', schemaVersion: ANALYSIS_SCHEMA_VERSION,
    promptVersion: '4.0.0', validatorHash: H('1'), schemaHash: H('2'), promptSourceHash: H('3'),
    flags: ['--print'], exitCode: 0, failureClass: 'NONE' as const,
  }

  /**
   * Dựng một cặp (phân tích, khai báo) ĐẦY ĐỦ và HỢP LỆ trên database.
   *
   * `over` cho phép từng ca làm hỏng đúng MỘT mắt xích — nhờ vậy mỗi lỗi báo ra
   * đều quy được về đúng thứ đã bị làm hỏng.
   */
  async function seed(over: {
    analysis?: CursorAnalysis
    analysisPassed?: boolean
    declarationPassed?: boolean
    skipObligation?: boolean
    obligationHashOverride?: string
    declaredHashOverride?: string
    declarationsOverride?: Array<Record<string, unknown>>
    declarationAnalysisOverride?: string
    /**
     * Làm HỎNG tập nghĩa vụ ĐÃ LƯU trong khi giữ nó TỰ NHẤT QUÁN.
     *
     * Băm được tính TRÊN tập đã sửa, nên mọi phép so băm "tập khớp cột lưu băm
     * của tập" vẫn đạt. Chỉ phép TÁI SINH từ bản phân tích mới bắt được.
     */
    obligationSetMutate?: (s: ClaimObligationSet) => ClaimObligationSet
    /** Băm phân tích ghi trên HÀNG BẢN KHAI (không đổi bản kê) — kiểm 0037. */
    declarationAnalysisHashOverride?: string
    /** Băm tập nghĩa vụ ghi trên HÀNG BẢN KHAI (không đổi bản kê) — kiểm 0037. */
    declaredObligationHashOverride?: string
  } = {}) {
    const analysis = over.analysis ?? ANALYSIS
    const built = buildObligationSet(analysis)
    const set = over.obligationSetMutate ? over.obligationSetMutate(structuredClone(built)) : built
    const setHash = hashObligationSet(set)
    const analysisHash = hashAnalysisPayload(analysis)

    const a = await execution()
    await db.insert(schema.cursorExecutionManifest).values({
      workspaceId, analysisRunId, llmExecutionId: a, requestId, attemptNumber: 1,
      executionRole: 'ANALYSIS', startedAt: new Date(), ...BASE,
    })
    await db.insert(schema.analysisValidation).values({
      workspaceId, analysisRunId, llmExecutionId: a, channelId,
      stage: 'ANALYSIS', passed: over.analysisPassed ?? true,
    })
    if (over.analysisPassed !== false) {
      await db.insert(schema.cursorAnalysisResult).values({
        workspaceId, analysisRunId, llmExecutionId: a, requestId, channelId,
        schemaVersion: ANALYSIS_SCHEMA_VERSION, resultRole: 'ANALYSIS',
        payload: analysis as never, payloadHash: analysisHash,
      })
    }
    if (!over.skipObligation) {
      await db.insert(schema.cursorClaimObligation).values({
        workspaceId, analysisRunId, channelId, requestId, analysisExecutionId: a,
        analysisHash, obligationSetHash: over.obligationHashOverride ?? setHash,
        generatorVersion: OBLIGATION_GENERATOR_VERSION, obligationCount: set.obligations.length, obligations: set,
      })
    }

    const d = await execution()
    await db.insert(schema.cursorExecutionManifest).values({
      workspaceId, analysisRunId, llmExecutionId: d, requestId, attemptNumber: 1,
      executionRole: 'DECLARATION', analysisExecutionId: a,
      obligationGeneratorVersion: OBLIGATION_GENERATOR_VERSION, declarationPromptVersion: '1.0.0',
      declarationPromptSourceHash: H('4'), compositeValidatorVersion: COMPOSITE_VALIDATOR_VERSION,
      analysisPayloadHash: analysisHash, obligationSetHash: over.obligationHashOverride ?? setHash,
      startedAt: new Date(), ...BASE,
    })
    await db.insert(schema.analysisValidation).values({
      workspaceId, analysisRunId, llmExecutionId: d, channelId,
      stage: 'DECLARATION', passed: over.declarationPassed ?? true,
    })
    const declarations = over.declarationsOverride ?? set.obligations.map((o) => DECL(o.id))
    const payload = {
      schemaVersion: DECLARATION_SCHEMA_VERSION,
      obligationSetHash: over.declaredHashOverride ?? setHash,
      declarations,
    }
    await db.insert(schema.cursorDeclarationResult).values({
      workspaceId, analysisRunId, channelId, requestId,
      llmExecutionId: d, analysisExecutionId: over.declarationAnalysisOverride ?? a,
      analysisPayloadHash: over.declarationAnalysisHashOverride ?? analysisHash,
      obligationSetHash:
        over.declaredObligationHashOverride ?? over.obligationHashOverride ?? setHash,
      // BĂM THẬT của payload, không phải chuỗi giữ chỗ.
      //
      // Chặng hợp nhất nay tính lại băm và đối chiếu, nên một fixture dùng băm
      // giả sẽ bị chặn — đúng như nó phải thế. Fixture cũ đi lọt chỉ vì phép
      // kiểm ấy chưa tồn tại.
      declarationCount: declarations.length, payloadHash: declHash(payload), payload,
    })
    return { a, d, set, setHash, analysisHash }
  }

  const allowed = () => {
    const b = buildPrompt({ pkg: pkgPayload as never })
    return { evidenceIds: b.allowedEvidenceIds, videoIds: b.allowedVideoIds, cohortKeys: b.allowedCohortKeys }
  }

  async function compose(a: string, d: string) {
    const loaded = await loadCompositeInputs(a, d)
    if ('issues' in loaded) return { loadIssues: loaded.issues, outcome: null, inputs: null }
    const outcome = runCompositeStage(loaded.inputs, pkgPayload as never, allowed(), {})
    return { loadIssues: [], outcome, inputs: loaded.inputs }
  }

  describe('đường ĐẠT', () => {
    it('cặp hợp lệ -> hợp nhất ĐẠT, claim ghép từ nghĩa vụ + khai báo', async () => {
      const { a, d, set } = await seed()
      const { outcome } = await compose(a, d)
      expect(outcome!.ok, JSON.stringify(outcome!.ok ? [] : outcome!.report?.claimIssues)).toBe(true)
      if (!outcome!.ok) return
      expect(outcome!.result.claimCount).toBe(set.obligations.length)
      const claim = outcome!.result.payload.metricClaims[0]!
      // `sourceRef` đến từ NGHĨA VỤ, không từ mô hình.
      expect(claim.sourceRef).toEqual(set.obligations[0]!.sourceRef)
      expect(claim.id).toBe(set.obligations[0]!.id)
      // Bảy trường ngữ nghĩa đến từ KHAI BÁO.
      expect(claim.subjectMetric).toBe('views')
    })

    it('_meta mang đủ lineage và băm', async () => {
      const { a, d, setHash, analysisHash } = await seed()
      const { outcome } = await compose(a, d)
      expect(outcome!.ok).toBe(true)
      if (!outcome!.ok) return
      const m = outcome!.result.payload._meta
      expect(m.analysisExecutionId).toBe(a)
      expect(m.declarationExecutionId).toBe(d)
      expect(m.analysisPayloadHash).toBe(analysisHash)
      expect(m.obligationSetHash).toBe(setHash)
      expect(m.obligationGeneratorVersion).toBe(OBLIGATION_GENERATOR_VERSION)
      expect(m.compositeValidatorVersion).toBe(COMPOSITE_VALIDATOR_VERSION)
    })

    it('S1–S8 nhận VĂN XUÔI ĐÃ PHÂN GIẢI, không nhận bản sao của mô hình', async () => {
      // Khai chủ ngữ KHÔNG có trong ô. Nếu S1 chạy trên một bản sao do mô hình
      // gửi thì nó không thể biết; chạy trên ô đã phân giải thì bắt được ngay.
      const { a, d } = await seed({
        declarationsOverride: [DECL('MC-001', { subjectMetric: 'packaging', relatedMetric: 'NONE' })],
      })
      const { outcome } = await compose(a, d)
      expect(outcome!.ok).toBe(false)
      if (outcome!.ok) return
      const rules = outcome!.report?.claimIssues.map((i) => i.rule) ?? []
      expect(rules).toContain('subject_metric_not_in_text')
    })

    it('evidence_support_unverified vẫn là HIGH và CHẶN', async () => {
      // OBS-001 nói về lượt xem; khai chủ ngữ retention -> bằng chứng không nói
      // điều claim nói. Mức HIGH, và HIGH thì không được coi là đạt.
      const { a, d } = await seed({
        analysis: {
          ...ANALYSIS,
          keyFindings: [{ ...ANALYSIS.keyFindings[0]!, limitations: ['giữ chân thấp dễ nhầm với vấn đề CTR'] }],
        },
        declarationsOverride: [DECL('MC-001', {
          subjectMetric: 'retention', relatedMetric: 'impression_ctr',
          claimType: 'OBSERVATION', judgement: 'LOW', assertionStatus: 'ASSERTED',
          evidenceIds: ['OBS-001'],
        })],
      })
      const { outcome } = await compose(a, d)
      expect(outcome!.ok).toBe(false)
      if (outcome!.ok) return
      const q = outcome!.report?.qualityIssues.map((i) => i.rule) ?? []
      expect(q).toContain('evidence_support_unverified')
      expect(outcome!.report?.passed).toBe(false)
    })
  })

  describe('CỔNG CODEX — cấp phép không qua cổng', () => {
    it('BLOCKER: hiện vật hợp nhất MỚI từ execution vai ANALYSIS -> BỊ CHẶN', async () => {
      /*
       * Đường một lượt: `cursor_result_semantic_lineage` (0033) đặt TOÀN BỘ phần
       * kiểm nghiêm ngặt trong `IF m.execution_role = 'DECLARATION'`, nên với bản
       * kê vai ANALYSIS chỉ còn đúng một điều kiện — có một dòng kiểm định
       * COMPOSITE đạt. Cộng với hai giá trị DEFAULT ('COMPOSITE' cho cả
       * `analysis_validation.stage` lẫn `cursor_analysis_result.result_role`),
       * ba lệnh INSERT tối thiểu KHÔNG nêu vai nào là đủ sinh ra một "hiện vật
       * chính thức" không tập nghĩa vụ, không bản khai, không lineage. Lặp N lần
       * cho N hiện vật cạnh tranh: hai trigger đếm trùng đều bỏ qua hình dạng này.
       *
       * 0036 đóng đường GHI và giữ nguyên tương thích ĐỌC cho 32 hàng cũ.
       */
      const a = await execution()
      await db.insert(schema.cursorExecutionManifest).values({
        workspaceId, analysisRunId, llmExecutionId: a, requestId, attemptNumber: 1,
        executionRole: 'ANALYSIS', startedAt: new Date(), ...BASE,
      })
      await db.insert(schema.analysisValidation).values({
        workspaceId, analysisRunId, llmExecutionId: a, channelId,
        stage: 'COMPOSITE', passed: true,
      })

      await expect(
        db.insert(schema.cursorAnalysisResult).values({
          workspaceId, analysisRunId, llmExecutionId: a, requestId, channelId,
          schemaVersion: ANALYSIS_SCHEMA_VERSION, resultRole: 'COMPOSITE',
          payload: { x: 1 } as never, payloadHash: H('e'),
        }),
      ).rejects.toThrow(/COMPOSITE_REQUIRES_DECLARATION_ROLE/)
    })

    it('RANH GIỚI: hàng vai ANALYSIS (văn xuôi đóng băng) VẪN ghi được', async () => {
      // 0036 không được chặn nhầm đường ghi đang chạy: lượt phân tích ĐẠT vẫn
      // phải lưu được văn xuôi của nó dưới vai ANALYSIS.
      const a = await execution()
      await db.insert(schema.cursorExecutionManifest).values({
        workspaceId, analysisRunId, llmExecutionId: a, requestId, attemptNumber: 1,
        executionRole: 'ANALYSIS', startedAt: new Date(), ...BASE,
      })
      await db.insert(schema.analysisValidation).values({
        workspaceId, analysisRunId, llmExecutionId: a, channelId, stage: 'ANALYSIS', passed: true,
      })
      await expect(
        db.insert(schema.cursorAnalysisResult).values({
          workspaceId, analysisRunId, llmExecutionId: a, requestId, channelId,
          schemaVersion: ANALYSIS_SCHEMA_VERSION, resultRole: 'ANALYSIS',
          payload: ANALYSIS as never, payloadHash: hashAnalysisPayload(ANALYSIS),
        }),
      ).resolves.toBeDefined()
    })

    it('BLOCKER: bản khai TỒN TẠI nhưng trỏ SAI lượt phân tích -> BỊ CHẶN ở DB', async () => {
      /*
       * 0033 chỉ hỏi "có tồn tại bản khai nào cho execution này không". Nó không
       * so `analysis_execution_id`, `analysis_payload_hash` hay
       * `obligation_set_hash` của hàng bản khai với bản kê — nên một bản khai
       * trỏ sang lượt phân tích KHÁC vẫn thoả, rồi hàng kết quả mang băm của
       * lượt phân tích ĐÚNG được cấp phép. "Bản khai được cấp phép" và "bản khai
       * được kiểm" là hai thứ khác nhau. 0037 đóng khoảng cách đó.
       *
       * Dựng từ đầu chứ không ghi đè: `cursor_declaration_result` là BẤT BIẾN
       * (không DELETE/UPDATE được) — một lớp bảo vệ khác, đã kiểm bằng chạy.
       */
      const otherAnalysis = await execution()
      await db.insert(schema.cursorExecutionManifest).values({
        workspaceId, analysisRunId, llmExecutionId: otherAnalysis, requestId, attemptNumber: 1,
        executionRole: 'ANALYSIS', startedAt: new Date(), ...BASE,
      })

      const { d } = await seed({ declarationAnalysisOverride: otherAnalysis })
      await db.insert(schema.analysisValidation).values({
        workspaceId, analysisRunId, llmExecutionId: d, channelId, stage: 'COMPOSITE', passed: true,
      })

      const analysisHash = hashAnalysisPayload(ANALYSIS)
      const setHash = hashObligationSet(buildObligationSet(ANALYSIS))
      await expect(
        db.insert(schema.cursorAnalysisResult).values({
          workspaceId, analysisRunId, llmExecutionId: d, requestId, channelId,
          schemaVersion: ANALYSIS_SCHEMA_VERSION, resultRole: 'COMPOSITE',
          payload: { schemaVersion: ANALYSIS_SCHEMA_VERSION } as never, payloadHash: H('e'),
          analysisPayloadHash: analysisHash, obligationSetHash: setHash,
        }),
      ).rejects.toThrow(/DECLARATION_ANALYSIS_MISMATCH/)
    })

    it('0037: bản khai neo SAI băm phân tích -> BỊ CHẶN ở DB', async () => {
      // 0037 thêm BA phép so. Ca trên chỉ chứng minh phép so `analysis_execution_id`;
      // hai phép so băm cần ca riêng, nếu không xoá chúng đi mà test vẫn xanh.
      /*
       * Hàng KẾT QUẢ phải neo ĐÚNG, chỉ hàng BẢN KHAI sai — nếu không thì
       * `RESULT_LINEAGE_DRIFT` (0033) bắt trước và ca này không chứng minh gì về
       * 0037. Đó chính là khoảng cách: 0033 so hàng KẾT QUẢ với bảng nghĩa vụ,
       * KHÔNG bao giờ so hàng BẢN KHAI.
       */
      const { d } = await seed({ declarationAnalysisHashOverride: H('7') })
      await db.insert(schema.analysisValidation).values({
        workspaceId, analysisRunId, llmExecutionId: d, channelId, stage: 'COMPOSITE', passed: true,
      })
      await expect(
        db.insert(schema.cursorAnalysisResult).values({
          workspaceId, analysisRunId, llmExecutionId: d, requestId, channelId,
          schemaVersion: ANALYSIS_SCHEMA_VERSION, resultRole: 'COMPOSITE',
          payload: { schemaVersion: ANALYSIS_SCHEMA_VERSION } as never, payloadHash: H('e'),
          analysisPayloadHash: hashAnalysisPayload(ANALYSIS),
          obligationSetHash: hashObligationSet(buildObligationSet(ANALYSIS)),
        }),
      ).rejects.toThrow(/DECLARATION_ANALYSIS_HASH_MISMATCH/)
    })

    it('0037: bản khai neo SAI băm tập nghĩa vụ -> BỊ CHẶN ở DB', async () => {
      const { d } = await seed({ declaredObligationHashOverride: H('7') })
      await db.insert(schema.analysisValidation).values({
        workspaceId, analysisRunId, llmExecutionId: d, channelId, stage: 'COMPOSITE', passed: true,
      })
      await expect(
        db.insert(schema.cursorAnalysisResult).values({
          workspaceId, analysisRunId, llmExecutionId: d, requestId, channelId,
          schemaVersion: ANALYSIS_SCHEMA_VERSION, resultRole: 'COMPOSITE',
          payload: { schemaVersion: ANALYSIS_SCHEMA_VERSION } as never, payloadHash: H('e'),
          analysisPayloadHash: hashAnalysisPayload(ANALYSIS),
          obligationSetHash: hashObligationSet(buildObligationSet(ANALYSIS)),
        }),
      ).rejects.toThrow(/DECLARATION_OBLIGATION_HASH_MISMATCH/)
    })

    it('HIGH: tập nghĩa vụ TỰ NHẤT QUÁN nhưng KHÔNG tái sinh được -> chặn', async () => {
      /*
       * `allowedAssertionStatuses` là nơi DUY NHẤT cưỡng chế hành vi lời nói theo
       * cấu trúc, và S2 chỉ đối chiếu nó với CHÍNH BẢN ĐÃ LƯU. Một hàng nghĩa vụ
       * mang `sourceRef` và băm THẬT nhưng cho phép `ASSERTED` ở một ô
       * `DATA_REQUEST|metricOrArtifact` sẽ qua mọi CHECK của database và mọi phép
       * so băm — rồi cấp phép cho đúng trạng thái mà 3.0 tuyên bố là BẤT KHẢ
       * BIỂU DIỄN ở ô đó. Chỉ phép TÁI SINH bắt được.
       */
      const { a, d } = await seed({
        obligationSetMutate: (s) => ({
          ...s,
          obligations: s.obligations.map((o) => ({
            ...o,
            allowedAssertionStatuses: ['ASSERTED', ...o.allowedAssertionStatuses],
          })),
        }),
      })
      const { outcome, loadIssues } = await compose(a, d)
      const rules = [
        ...loadIssues.map((i: { rule: string }) => i.rule),
        ...(outcome?.ok === false ? outcome.report?.claimIssues.map((i) => i.rule) ?? [] : []),
        ...(outcome?.ok === false ? outcome.issues?.map((i) => i.rule) ?? [] : []),
      ]
      expect(outcome?.ok ?? false, 'tập nghĩa vụ giả mạo vẫn được cấp phép').toBe(false)
      expect(
        rules.some((r) => r === 'composite_obligation_set_not_reproducible'),
        `không có quy tắc tái sinh nào kêu lên: ${rules.join(', ')}`,
      ).toBe(true)
    })
  })

  describe('CHẶN: thiếu mắt xích', () => {
    it('thiếu tập nghĩa vụ -> chặn', async () => {
      const { a, d } = await seed({ skipObligation: true })
      const { loadIssues } = await compose(a, d)
      expect(loadIssues.map((i) => i.rule)).toContain('composite_missing_obligation_set')
    })

    it('thiếu payload phân tích -> chặn', async () => {
      const { d } = await seed()
      const orphan = await execution()
      const { loadIssues } = await compose(orphan, d)
      expect(loadIssues.map((i) => i.rule)).toContain('composite_missing_analysis_payload')
    })

    it('thiếu bản khai -> chặn', async () => {
      const { a } = await seed()
      const orphan = await execution()
      const { loadIssues } = await compose(a, orphan)
      expect(loadIssues.map((i) => i.rule)).toContain('composite_missing_declaration_payload')
    })
  })

  describe('CHẶN: trôi dạt băm và danh tính', () => {
    it('bản khai dội SAI băm tập nghĩa vụ -> chặn', async () => {
      const { a, d } = await seed({ declaredHashOverride: H('f') })
      const { outcome } = await compose(a, d)
      expect(outcome!.ok).toBe(false)
      if (outcome!.ok) return
      expect(outcome!.issues.map((i) => i.rule)).toContain('obligation_set_drift')
    })

    it('băm tập nghĩa vụ trong cột KHÔNG khớp nội dung -> chặn', async () => {
      const { a, d } = await seed({ obligationHashOverride: H('e') })
      const { outcome } = await compose(a, d)
      expect(outcome!.ok).toBe(false)
      if (outcome!.ok) return
      expect(outcome!.issues.map((i) => i.rule)).toContain('composite_obligation_set_drift')
    })

    it('khai THIẾU / THỪA / TRÙNG -> chặn', async () => {
      for (const [label, decls] of [
        ['thiếu', []],
        ['thừa', [DECL('MC-001'), DECL('MC-099')]],
        ['trùng', [DECL('MC-001'), DECL('MC-001')]],
      ] as Array<[string, Array<Record<string, unknown>>]>) {
        const { a, d } = await seed({ declarationsOverride: decls })
        const { outcome } = await compose(a, d)
        expect(outcome!.ok, label).toBe(false)
        if (outcome!.ok) continue
        const rules = outcome!.issues.map((i) => i.rule)
        expect(rules.some((r) => r.startsWith('declaration_')), label).toBe(true)
      }
    })

    it('bản khai của MỘT LƯỢT PHÂN TÍCH KHÁC -> chặn', async () => {
      const first = await seed()
      const second = await seed()
      // Bản khai của cặp thứ hai, ghép với lượt phân tích của cặp thứ nhất.
      const { loadIssues, outcome } = await compose(first.a, second.d)
      const rules = [...loadIssues.map((i) => i.rule), ...(outcome && !outcome.ok ? outcome.issues.map((i) => i.rule) : [])]
      expect(rules).toContain('composite_declaration_wrong_analysis')
    })

    it('VĂN XUÔI bị đổi sau khi sinh nghĩa vụ -> chặn', async () => {
      const { a, d, set, analysisHash } = await seed()
      // Giả lập trôi dạt bằng cách xây đầu vào tay với văn xuôi đã đổi.
      const tampered: CursorInputsLike = {
        analysisExecutionId: a, declarationExecutionId: d,
        analysis: {
          ...ANALYSIS,
          keyFindings: [{ ...ANALYSIS.keyFindings[0]!, limitations: ['cỡ mẫu lượt xem RẤT thấp nên CTR nhiễu'] }],
        },
        analysisPayloadHash: analysisHash,
        obligationSet: set, obligationSetHash: hashObligationSet(set), generatorVersion: OBLIGATION_GENERATOR_VERSION,
        declarations: set.obligations.map((o) => DECL(o.id)),
        declaredObligationSetHash: hashObligationSet(set),
        requestId, channelId, analysisRunId, workspaceId,
      }
      const issues = verifyCompositeInputs(tampered as CompositeInputs)
      const rules = issues.map((i) => i.rule)
      expect(rules).toContain('composite_analysis_payload_drift')
      expect(rules.some((r) => r === 'obligation_source_drift' || r === 'obligation_analysis_mismatch')).toBe(true)
    })
  })

  describe('G8 — hàng đã lưu phải khớp BĂM CỦA CHÍNH NÓ', () => {
    it('payload bản khai KHÔNG khớp `payload_hash` -> chặn', async () => {
      // Trước G8, chặng hợp nhất đọc `payload` mà không bao giờ đối chiếu với
      // `payload_hash`. Một lần ghi hỏng — hoặc một script ghi thẳng — đặt
      // payload B cạnh băm của payload A sẽ đi lọt toàn bộ: B hợp schema, B
      // mang đúng băm tập nghĩa vụ, B qua S1–S8, và được cấp phép làm hiện vật
      // chính thức trong khi chính hàng đó nói nó là A.
      const { a, d } = await seed()
      // `cursor_declaration_result` là BẤT BIẾN, nên không UPDATE được. Dựng ca
      // này bằng cách ghi một cặp lệch ngay từ INSERT — đúng như một script sai
      // sẽ làm.
      const d2 = await execution()
      await db.insert(schema.cursorExecutionManifest).values({
        workspaceId, analysisRunId, llmExecutionId: d2, requestId, attemptNumber: 2,
        executionRole: 'DECLARATION', analysisExecutionId: a,
        obligationGeneratorVersion: OBLIGATION_GENERATOR_VERSION, declarationPromptVersion: '1.0.0',
        declarationPromptSourceHash: H('4'), compositeValidatorVersion: COMPOSITE_VALIDATOR_VERSION,
        analysisPayloadHash: hashAnalysisPayload(ANALYSIS),
        obligationSetHash: hashObligationSet(buildObligationSet(ANALYSIS)),
        startedAt: new Date(), ...BASE,
      })
      await db.insert(schema.analysisValidation).values({
        workspaceId, analysisRunId, llmExecutionId: d2, channelId, stage: 'DECLARATION', passed: true,
      })
      const set = buildObligationSet(ANALYSIS)
      const payload = {
        schemaVersion: DECLARATION_SCHEMA_VERSION,
        obligationSetHash: hashObligationSet(set),
        declarations: set.obligations.map((o) => DECL(o.id)),
      }
      await db.insert(schema.cursorDeclarationResult).values({
        workspaceId, analysisRunId, channelId, requestId,
        llmExecutionId: d2, analysisExecutionId: a,
        analysisPayloadHash: hashAnalysisPayload(ANALYSIS),
        obligationSetHash: hashObligationSet(set),
        declarationCount: payload.declarations.length,
        payload,
        payloadHash: H('f'), // BĂM SAI, cố ý
      })

      const { loadIssues } = await compose(a, d2)
      expect(loadIssues.map((i) => i.rule)).toContain('composite_declaration_payload_hash_mismatch')
      expect(d).toBeTruthy()
    })

    it('cột neo văn xuôi của bản khai lệch băm THẬT -> chặn', async () => {
      const { a } = await seed()
      const d2 = await execution()
      await db.insert(schema.cursorExecutionManifest).values({
        workspaceId, analysisRunId, llmExecutionId: d2, requestId, attemptNumber: 2,
        executionRole: 'DECLARATION', analysisExecutionId: a,
        obligationGeneratorVersion: OBLIGATION_GENERATOR_VERSION, declarationPromptVersion: '1.0.0',
        declarationPromptSourceHash: H('4'), compositeValidatorVersion: COMPOSITE_VALIDATOR_VERSION,
        analysisPayloadHash: hashAnalysisPayload(ANALYSIS),
        obligationSetHash: hashObligationSet(buildObligationSet(ANALYSIS)),
        startedAt: new Date(), ...BASE,
      })
      await db.insert(schema.analysisValidation).values({
        workspaceId, analysisRunId, llmExecutionId: d2, channelId, stage: 'DECLARATION', passed: true,
      })
      const set = buildObligationSet(ANALYSIS)
      const payload = {
        schemaVersion: DECLARATION_SCHEMA_VERSION,
        obligationSetHash: hashObligationSet(set),
        declarations: set.obligations.map((o) => DECL(o.id)),
      }
      await db.insert(schema.cursorDeclarationResult).values({
        workspaceId, analysisRunId, channelId, requestId,
        llmExecutionId: d2, analysisExecutionId: a,
        analysisPayloadHash: H('e'), // neo vào một văn xuôi KHÁC
        obligationSetHash: hashObligationSet(set),
        declarationCount: payload.declarations.length,
        payload, payloadHash: declHash(payload),
      })

      const { loadIssues } = await compose(a, d2)
      expect(loadIssues.map((i) => i.rule)).toContain('composite_declaration_analysis_hash_mismatch')
    })
  })

  describe('CHẶN ở tầng DATABASE', () => {
    it('ANALYSIS ĐẠT một mình KHÔNG tạo được kết quả chính thức', async () => {
      const { a } = await seed()
      await expect(
        db.insert(schema.cursorAnalysisResult).values({
          workspaceId, analysisRunId, llmExecutionId: a, requestId, channelId,
          schemaVersion: '3.0', resultRole: 'COMPOSITE',
          payload: { schemaVersion: '3.0' }, payloadHash: H('c'),
          analysisPayloadHash: H('5'), obligationSetHash: H('6'),
        }),
      ).rejects.toThrow()
    })

    it('DECLARATION ĐẠT một mình (chưa có COMPOSITE) KHÔNG tạo được kết quả', async () => {
      const { d, analysisHash, setHash } = await seed()
      await expect(
        db.insert(schema.cursorAnalysisResult).values({
          workspaceId, analysisRunId, llmExecutionId: d, requestId, channelId,
          schemaVersion: '3.0', resultRole: 'COMPOSITE',
          payload: { schemaVersion: '3.0' }, payloadHash: H('c'),
          analysisPayloadHash: analysisHash, obligationSetHash: setHash,
        }),
      ).rejects.toThrow(/RESULT_WITHOUT_VALIDATION/)
    })

    it('ANALYSIS HỎNG -> không thể tới kết quả chính thức', async () => {
      const { d, analysisHash, setHash } = await seed({ analysisPassed: false })
      await db.insert(schema.analysisValidation).values({
        workspaceId, analysisRunId, llmExecutionId: d, channelId, stage: 'COMPOSITE', passed: true,
      })
      await expect(
        db.insert(schema.cursorAnalysisResult).values({
          workspaceId, analysisRunId, llmExecutionId: d, requestId, channelId,
          schemaVersion: '3.0', resultRole: 'COMPOSITE',
          payload: { schemaVersion: '3.0' }, payloadHash: H('c'),
          analysisPayloadHash: analysisHash, obligationSetHash: setHash,
        }),
      ).rejects.toThrow(/RESULT_WITH_FAILED_ANALYSIS|RESULT_WITHOUT_ANALYSIS_VALIDATION/)
    })

    it('DECLARATION HỎNG -> không thể tới kết quả chính thức', async () => {
      const { d, analysisHash, setHash } = await seed({ declarationPassed: false })
      await db.insert(schema.analysisValidation).values({
        workspaceId, analysisRunId, llmExecutionId: d, channelId, stage: 'COMPOSITE', passed: true,
      })
      await expect(
        db.insert(schema.cursorAnalysisResult).values({
          workspaceId, analysisRunId, llmExecutionId: d, requestId, channelId,
          schemaVersion: '3.0', resultRole: 'COMPOSITE',
          payload: { schemaVersion: '3.0' }, payloadHash: H('c'),
          analysisPayloadHash: analysisHash, obligationSetHash: setHash,
        }),
      ).rejects.toThrow(/RESULT_WITH_FAILED_DECLARATION/)
    })

    it('phán quyết COMPOSITE CẠNH TRANH cho cùng lượt phân tích bị chặn', async () => {
      const { a, d } = await seed()
      await db.insert(schema.analysisValidation).values({
        workspaceId, analysisRunId, llmExecutionId: d, channelId, stage: 'COMPOSITE', passed: true,
      })
      // Lượt khai báo THỨ HAI của CÙNG lượt phân tích.
      const d2 = await execution()
      await db.insert(schema.cursorExecutionManifest).values({
        workspaceId, analysisRunId, llmExecutionId: d2, requestId, attemptNumber: 2,
        executionRole: 'DECLARATION', analysisExecutionId: a,
        obligationGeneratorVersion: OBLIGATION_GENERATOR_VERSION, declarationPromptVersion: '1.0.0',
        declarationPromptSourceHash: H('4'), compositeValidatorVersion: COMPOSITE_VALIDATOR_VERSION,
        analysisPayloadHash: hashAnalysisPayload(ANALYSIS),
        obligationSetHash: hashObligationSet(buildObligationSet(ANALYSIS)),
        startedAt: new Date(), ...BASE,
      })
      await expect(
        db.insert(schema.analysisValidation).values({
          workspaceId, analysisRunId, llmExecutionId: d2, channelId, stage: 'COMPOSITE', passed: true,
        }),
      ).rejects.toThrow(/COMPETING_COMPOSITE_VERDICT/)
    })

    it('hai phán quyết COMPOSITE trên CÙNG execution bị chặn', async () => {
      const { d } = await seed()
      await db.insert(schema.analysisValidation).values({
        workspaceId, analysisRunId, llmExecutionId: d, channelId, stage: 'COMPOSITE', passed: true,
      })
      await expect(
        db.insert(schema.analysisValidation).values({
          workspaceId, analysisRunId, llmExecutionId: d, channelId, stage: 'COMPOSITE', passed: false,
        }),
      ).rejects.toThrow()
    })

    it('bản khai đã lưu là BẤT BIẾN', async () => {
      const { d } = await seed()
      await expect(
        db.update(schema.cursorDeclarationResult).set({ declarationCount: 99 })
          .where(eq(schema.cursorDeclarationResult.llmExecutionId, d)),
      ).rejects.toThrow(/IMMUTABLE_DECLARATION_RESULT/)
    })
  })

  /* ---------------------------------------------------------------------
   * 0029 — quyền đã cấp thì KHÔNG MẤT ĐƯỢC
   * ------------------------------------------------------------------ */
  describe('G7 — phán quyết ĐẠT và kết quả chính thức không mồ côi được', () => {
    /** Dựng một lượt khai báo thứ n cho CÙNG lượt phân tích `a`. */
    async function extraDeclaration(a: string, attempt: number) {
      const d = await execution()
      await db.insert(schema.cursorExecutionManifest).values({
        workspaceId, analysisRunId, llmExecutionId: d, requestId, attemptNumber: attempt,
        executionRole: 'DECLARATION', analysisExecutionId: a,
        obligationGeneratorVersion: OBLIGATION_GENERATOR_VERSION, declarationPromptVersion: '1.0.0',
        declarationPromptSourceHash: H('4'), compositeValidatorVersion: COMPOSITE_VALIDATOR_VERSION,
        analysisPayloadHash: hashAnalysisPayload(ANALYSIS),
        obligationSetHash: hashObligationSet(buildObligationSet(ANALYSIS)),
        startedAt: new Date(), ...BASE,
      })
      // Lượt khai báo phải có phán quyết DECLARATION riêng của nó trước khi
      // chặng hợp nhất được xét — cổng 0026 đòi đúng thứ tự này.
      await db.insert(schema.analysisValidation).values({
        workspaceId, analysisRunId, llmExecutionId: d, channelId, stage: 'DECLARATION', passed: true,
      })
      const set = buildObligationSet(ANALYSIS)
      const declarations = set.obligations.map((o) => DECL(o.id))
      const declPayload = {
        schemaVersion: DECLARATION_SCHEMA_VERSION,
        obligationSetHash: hashObligationSet(set),
        declarations,
      }
      await db.insert(schema.cursorDeclarationResult).values({
        workspaceId, analysisRunId, channelId, requestId,
        llmExecutionId: d, analysisExecutionId: a,
        analysisPayloadHash: hashAnalysisPayload(ANALYSIS),
        obligationSetHash: hashObligationSet(set),
        declarationCount: declarations.length,
        payload: declPayload,
        payloadHash: declHash(declPayload),
      })
      return d
    }

    async function authorize(d: string, analysisHash: string, setHash: string) {
      await db.insert(schema.analysisValidation).values({
        workspaceId, analysisRunId, llmExecutionId: d, channelId, stage: 'COMPOSITE', passed: true,
      })
      const [row] = await db.insert(schema.cursorAnalysisResult).values({
        workspaceId, analysisRunId, llmExecutionId: d, requestId, channelId,
        schemaVersion: '3.0', resultRole: 'COMPOSITE',
        payload: { schemaVersion: '3.0' }, payloadHash: H('c'),
        analysisPayloadHash: analysisHash, obligationSetHash: setHash,
      }).returning({ id: schema.cursorAnalysisResult.id })
      return row!.id
    }

    it('NHIỀU lần khai báo trượt ngữ nghĩa đều LƯU LẠI ĐƯỢC và đọc lại được', async () => {
      // Yêu cầu cốt lõi: một lần thử trượt phải để lại dấu vết. Nếu trigger chặn
      // phán quyết trượt thứ hai thì bảng lần thử sẽ nói "trượt" mà không chỉ ra
      // được bằng chứng nào, và người đọc chỉ còn cách tin lời tóm tắt.
      const { a, d: d1 } = await seed()
      const ds = [d1, await extraDeclaration(a, 2), await extraDeclaration(a, 3)]
      for (const d of ds) {
        await db.insert(schema.analysisValidation).values({
          workspaceId, analysisRunId, llmExecutionId: d, channelId,
          stage: 'COMPOSITE', passed: false, failureClass: 'UNSUPPORTED_CLAIM',
        })
      }
      const rows = await db.execute<{ n: number }>(sql`
        SELECT count(*)::int n FROM analysis_validation v
        JOIN cursor_execution_manifest m ON m.llm_execution_id = v.llm_execution_id
        WHERE v.stage = 'COMPOSITE' AND v.passed = false AND m.analysis_execution_id = ${a}::uuid`)
      expect(Number(rows.rows[0]!.n)).toBe(3)
    })

    it('trượt NHIỀU LẦN rồi ĐẠT: giữ cả ba phán quyết trượt lẫn một kết quả', async () => {
      const { a, d: d1, analysisHash, setHash } = await seed()
      for (const d of [d1, await extraDeclaration(a, 2)]) {
        await db.insert(schema.analysisValidation).values({
          workspaceId, analysisRunId, llmExecutionId: d, channelId,
          stage: 'COMPOSITE', passed: false, failureClass: 'UNSUPPORTED_CLAIM',
        })
      }
      const win = await extraDeclaration(a, 3)
      await authorize(win, analysisHash, setHash)

      const v = await db.execute<{ passed: boolean }>(sql`
        SELECT v.passed FROM analysis_validation v
        JOIN cursor_execution_manifest m ON m.llm_execution_id = v.llm_execution_id
        WHERE v.stage='COMPOSITE' AND m.analysis_execution_id = ${a}::uuid
        ORDER BY m.attempt_number`)
      expect(v.rows.map((x) => x.passed)).toEqual([false, false, true])

      const res = await db.execute<{ n: number }>(sql`
        SELECT count(*)::int n FROM cursor_analysis_result
        WHERE analysis_run_id = ${analysisRunId}::uuid AND result_role = 'COMPOSITE'`)
      // Lọc theo VAI: hàng kết quả của lượt PHÂN TÍCH cũng nằm trong bảng này,
      // và đếm gộp sẽ báo 2 rồi khiến người đọc tưởng có hai hiện vật chính thức.
      expect(Number(res.rows[0]!.n)).toBe(1)
    })

    it('XOÁ kết quả chính thức bị CHẶN', async () => {
      const { a, analysisHash, setHash } = await seed()
      const d = await extraDeclaration(a, 2)
      const resultId = await authorize(d, analysisHash, setHash)
      await expect(
        db.execute(sql`DELETE FROM cursor_analysis_result WHERE id = ${resultId}::uuid`),
      ).rejects.toThrow(/IMMUTABLE_CURSOR_RESULT/)
    })

    it('SỬA kết quả chính thức bị CHẶN', async () => {
      const { a, analysisHash, setHash } = await seed()
      const d = await extraDeclaration(a, 2)
      const resultId = await authorize(d, analysisHash, setHash)
      await expect(
        db.execute(sql`UPDATE cursor_analysis_result SET payload_hash = ${H('9')} WHERE id = ${resultId}::uuid`),
      ).rejects.toThrow(/IMMUTABLE_CURSOR_RESULT/)
    })

    it('XOÁ phán quyết ĐẠT đang cấp phép cho một kết quả bị CHẶN', async () => {
      const { a, analysisHash, setHash } = await seed()
      const d = await extraDeclaration(a, 2)
      await authorize(d, analysisHash, setHash)
      await expect(
        db.execute(sql`
          DELETE FROM analysis_validation WHERE llm_execution_id = ${d}::uuid AND stage = 'COMPOSITE'`),
      ).rejects.toThrow(/IMMUTABLE_VALIDATION/)
    })

    it('phán quyết KHÔNG ĐẠT cũng KHÔNG xoá được — nó là bằng chứng', async () => {
      // Bản đầu của test này khẳng định ngược lại, vì tôi đã đọc sót: bảo vệ
      // không đến từ migration mới nào cả, mà từ `analysis_validation_immutability`
      // có từ trước — và nó chặn MỌI xoá/sửa, không phân biệt ĐẠT hay trượt.
      //
      // Đó lại là hành vi đúng hơn ý định ban đầu của tôi: một phán quyết trượt
      // là bằng chứng về một lần thử, và toàn bộ lập luận của Phase 4 dựa trên
      // việc bằng chứng không biến mất. Dọn dữ liệu test dùng TRUNCATE, vốn
      // không kích hoạt trigger hàng, nên không có gì phải nới lỏng.
      const { a } = await seed()
      const d = await extraDeclaration(a, 2)
      await db.insert(schema.analysisValidation).values({
        workspaceId, analysisRunId, llmExecutionId: d, channelId,
        stage: 'COMPOSITE', passed: false, failureClass: 'UNSUPPORTED_CLAIM',
      })
      await expect(
        db.execute(sql`
          DELETE FROM analysis_validation WHERE llm_execution_id = ${d}::uuid AND stage = 'COMPOSITE'`),
      ).rejects.toThrow(/IMMUTABLE_VALIDATION/)
    })

    it('kết quả chính thức THỨ HAI cho cùng lượt phân tích bị CHẶN', async () => {
      const { a, analysisHash, setHash } = await seed()
      const d1 = await extraDeclaration(a, 2)
      await authorize(d1, analysisHash, setHash)
      // Phán quyết ĐẠT thứ hai đã bị 0028 chặn, nên để dựng được ca "kết quả thứ
      // hai" phải đi vòng: một lượt phân tích khác, nhưng CÙNG analysis_run.
      const d2 = await extraDeclaration(a, 3)
      await expect(
        db.insert(schema.analysisValidation).values({
          workspaceId, analysisRunId, llmExecutionId: d2, channelId, stage: 'COMPOSITE', passed: true,
        }),
      ).rejects.toThrow(/COMPETING_COMPOSITE_VERDICT/)
    })

    it('TRẦN lần thử khai báo tính theo SỐ LƯỢNG, không theo giá trị cột', async () => {
      // Bản đầu của test này chỉ thử `attempt_number = 4` rồi kết luận "có trần
      // chung". Kết luận ấy SAI, và rà soát đối kháng đã chỉ ra: CHECK
      // `attempt_number BETWEEN 1 AND 3` giới hạn GIÁ TRỊ của một hàng, không
      // giới hạn SỐ HÀNG. Một script tạo 100 lượt khai báo cùng mang
      // `attempt_number = 1` sẽ thoả CHECK ở mọi hàng, rồi chọn lần đẹp nhất để
      // xin phán quyết ĐẠT — đúng định nghĩa gian lận thử lại.
      //
      // Trần thật do 0031 cưỡng chế: ĐẾM số lượt khai báo của cùng một lượt
      // phân tích. Test này chứng minh cả hai chiều.
      const { a } = await seed()
      await extraDeclaration(a, 2)
      await extraDeclaration(a, 3)

      // Lần thứ tư — dù mang attempt_number HỢP LỆ — vẫn bị chặn.
      await expect(extraDeclaration(a, 1)).rejects.toThrow(/DECLARATION_ATTEMPT_CAP/)
      await expect(extraDeclaration(a, 2)).rejects.toThrow(/DECLARATION_ATTEMPT_CAP/)
      await expect(extraDeclaration(a, 3)).rejects.toThrow(/DECLARATION_ATTEMPT_CAP/)

      // Và giá trị ngoài dải vẫn bị CHECK chặn như trước.
      await expect(extraDeclaration(a, 4)).rejects.toThrow(
        /DECLARATION_ATTEMPT_CAP|cursor_manifest_attempt_bounds/,
      )

      const n = await db.execute<{ n: number }>(sql`
        SELECT count(*)::int n FROM cursor_execution_manifest
        WHERE analysis_execution_id = ${a}::uuid AND execution_role = 'DECLARATION'`)
      expect(Number(n.rows[0]!.n)).toBe(3)
    })

    it('lượt khai báo KHÔNG neo được vào một execution mang vai DECLARATION', async () => {
      // `analysis_execution_id` chỉ có khoá ngoại tới `llm_execution`, nên nó
      // trỏ được vào BẤT KỲ execution nào — kể cả một lượt khai báo khác. Cả một
      // chuỗi giả có thể tự nhất quán về băm mà không có bài phân tích nào.
      const { a, d } = await seed()
      const rogue = await execution()
      await expect(
        db.insert(schema.cursorExecutionManifest).values({
          workspaceId, analysisRunId, llmExecutionId: rogue, requestId, attemptNumber: 1,
          executionRole: 'DECLARATION', analysisExecutionId: d,
          obligationGeneratorVersion: OBLIGATION_GENERATOR_VERSION, declarationPromptVersion: '1.0.0',
          declarationPromptSourceHash: H('4'), compositeValidatorVersion: COMPOSITE_VALIDATOR_VERSION,
          analysisPayloadHash: hashAnalysisPayload(ANALYSIS),
          obligationSetHash: hashObligationSet(buildObligationSet(ANALYSIS)),
          startedAt: new Date(), ...BASE,
        }),
      ).rejects.toThrow(/DECLARATION_ANALYSIS_WRONG_ROLE/)
      expect(a).toBeTruthy()
    })

    it('HAI GIAO DỊCH ĐỒNG THỜI không thể cùng ghi phán quyết ĐẠT', async () => {
      // Đây là khiếm khuyết NGHIÊM TRỌNG NHẤT mà rà soát đối kháng tìm ra, và
      // là loại mà test tuần tự KHÔNG BAO GIỜ thấy.
      //
      // Trigger 0028 làm "SELECT rồi INSERT". Ở mức cô lập mặc định, hai giao
      // dịch đồng thời ghi phán quyết ĐẠT cho hai lượt khai báo của CÙNG một
      // lượt phân tích đều đọc trên ảnh chụp riêng, không thấy hàng chưa commit
      // của bên kia, nên CẢ HAI kết luận "chưa ai có quyền" và cùng qua.
      //
      // 0031 lấy `pg_advisory_xact_lock` TRƯỚC khi đọc, nên giao dịch thứ hai
      // phải đợi giao dịch thứ nhất kết thúc rồi mới đọc — và khi đó nó thấy.
      const { a, d: d1 } = await seed()
      const d2 = await extraDeclaration(a, 2)

      const { Client, neonConfig } = await import('@neondatabase/serverless')
      const ws = (await import('ws')).default
      neonConfig.webSocketConstructor = ws
      const url = process.env.TEST_DATABASE_URL!
      const c1 = new Client({ connectionString: url })
      const c2 = new Client({ connectionString: url })
      await c1.connect()
      await c2.connect()

      const insertVerdict = (c: InstanceType<typeof Client>, execId: string) =>
        c.query(
          `INSERT INTO analysis_validation
             (workspace_id, analysis_run_id, llm_execution_id, channel_id, stage, passed)
           VALUES ($1,$2,$3,$4,'COMPOSITE',true)`,
          [workspaceId, analysisRunId, execId, channelId],
        )

      try {
        await c1.query('BEGIN')
        await c2.query('BEGIN')

        // c1 ghi trước và GIỮ khoá (chưa commit).
        await insertVerdict(c1, d1)

        // c2 ghi song song: phải ĐỢI khoá, không được đi qua.
        let c2Settled = false
        const c2Insert = insertVerdict(c2, d2).then(
          () => { c2Settled = true; return 'ĐI QUA' },
          (e: Error) => { c2Settled = true; return e.message },
        )

        // Cho c2 một khoảng để chạy. Nếu nó KHÔNG bị khoá chặn, nó sẽ xong ngay.
        await new Promise((r) => setTimeout(r, 700))
        expect(c2Settled, 'giao dịch thứ hai KHÔNG bị khoá chặn — đua vẫn còn').toBe(false)

        await c1.query('COMMIT')
        const c2Result = await c2Insert
        expect(c2Result).toMatch(/COMPETING_COMPOSITE_VERDICT/)
        await c2.query('ROLLBACK')

        // Chỉ MỘT phán quyết ĐẠT tồn tại.
        const n = await db.execute<{ n: number }>(sql`
          SELECT count(*)::int n FROM analysis_validation v
          JOIN cursor_execution_manifest m ON m.llm_execution_id = v.llm_execution_id
          WHERE v.stage='COMPOSITE' AND v.passed = true AND m.analysis_execution_id = ${a}::uuid`)
        expect(Number(n.rows[0]!.n)).toBe(1)
      } finally {
        await c1.query('ROLLBACK').catch(() => {})
        await c2.query('ROLLBACK').catch(() => {})
        await c1.end()
        await c2.end()
      }
    })

    it('kết quả chính thức KHÔNG cấp được khi chưa lưu bản khai nào', async () => {
      // Trigger cấp phép đọc phán quyết và tập nghĩa vụ, nhưng trước 0031 nó
      // không đòi `cursor_declaration_result` tồn tại. Đường ứng dụng luôn ghi
      // bản khai trước, nên lỗ hổng chỉ lộ ra với script ghi thẳng database —
      // và đó chính là kẻ mà ràng buộc ở tầng database sinh ra để chặn.
      const { a } = await seed()
      const bare = await execution()
      await db.insert(schema.cursorExecutionManifest).values({
        workspaceId, analysisRunId, llmExecutionId: bare, requestId, attemptNumber: 2,
        executionRole: 'DECLARATION', analysisExecutionId: a,
        obligationGeneratorVersion: OBLIGATION_GENERATOR_VERSION, declarationPromptVersion: '1.0.0',
        declarationPromptSourceHash: H('4'), compositeValidatorVersion: COMPOSITE_VALIDATOR_VERSION,
        analysisPayloadHash: hashAnalysisPayload(ANALYSIS),
        obligationSetHash: hashObligationSet(buildObligationSet(ANALYSIS)),
        startedAt: new Date(), ...BASE,
      })
      for (const stage of ['DECLARATION', 'COMPOSITE'] as const) {
        await db.insert(schema.analysisValidation).values({
          workspaceId, analysisRunId, llmExecutionId: bare, channelId, stage, passed: true,
        })
      }
      await expect(
        db.insert(schema.cursorAnalysisResult).values({
          workspaceId, analysisRunId, llmExecutionId: bare, requestId, channelId,
          schemaVersion: '3.0', resultRole: 'COMPOSITE',
          payload: { schemaVersion: '3.0' }, payloadHash: H('c'),
          analysisPayloadHash: hashAnalysisPayload(ANALYSIS),
          obligationSetHash: hashObligationSet(buildObligationSet(ANALYSIS)),
        }),
      ).rejects.toThrow(/RESULT_WITHOUT_DECLARATION_PAYLOAD/)
    })
  })

  /* ---------------------------------------------------------------------
   * G-R5 — BẢN KÊ bất biến (0034)
   * ------------------------------------------------------------------ */
  describe('G-R5 — bản kê execution KHÔNG sửa, KHÔNG xoá được', () => {
    /** Lượt khai báo thứ n cho cùng lượt phân tích — bản cục bộ của khối này. */
    async function decl(a: string, attempt: number) {
      const d = await execution()
      await db.insert(schema.cursorExecutionManifest).values({
        workspaceId, analysisRunId, llmExecutionId: d, requestId, attemptNumber: attempt,
        executionRole: 'DECLARATION', analysisExecutionId: a,
        obligationGeneratorVersion: OBLIGATION_GENERATOR_VERSION, declarationPromptVersion: '1.0.0',
        declarationPromptSourceHash: H('4'), compositeValidatorVersion: COMPOSITE_VALIDATOR_VERSION,
        analysisPayloadHash: hashAnalysisPayload(ANALYSIS),
        obligationSetHash: hashObligationSet(buildObligationSet(ANALYSIS)),
        startedAt: new Date(), ...BASE,
      })
      return d
    }

    it('SỬA bản kê bị CHẶN', async () => {
      const { a } = await seed()
      await expect(
        db.execute(sql`
          UPDATE cursor_execution_manifest SET attempt_number = 2
          WHERE llm_execution_id = ${a}::uuid`),
      ).rejects.toThrow(/IMMUTABLE_CURSOR_MANIFEST/)
    })

    it('ĐỔI VAI từ ANALYSIS sang DECLARATION bị CHẶN — đây là đường vượt trần', async () => {
      // Trigger trần lần thử của 0031 chỉ chạy BEFORE INSERT. Chèn vai ANALYSIS
      // (được trả NEW ngay) rồi UPDATE sang DECLARATION là cách lách trần mà
      // không phép kiểm nào từng chạy.
      const { a } = await seed()
      const rogue = await execution()
      await db.insert(schema.cursorExecutionManifest).values({
        workspaceId, analysisRunId, llmExecutionId: rogue, requestId, attemptNumber: 1,
        executionRole: 'ANALYSIS', startedAt: new Date(), ...BASE,
      })
      await expect(
        db.execute(sql`
          UPDATE cursor_execution_manifest
             SET execution_role = 'DECLARATION', analysis_execution_id = ${a}::uuid
           WHERE llm_execution_id = ${rogue}::uuid`),
      ).rejects.toThrow(/IMMUTABLE_CURSOR_MANIFEST/)
    })

    it('XOÁ bản kê bị CHẶN — không xoá được bằng chứng, không đặt lại trần', async () => {
      const { a } = await seed()
      await decl(a, 2)
      await expect(
        db.execute(sql`
          DELETE FROM cursor_execution_manifest
           WHERE analysis_execution_id = ${a}::uuid AND execution_role = 'DECLARATION'`),
      ).rejects.toThrow(/IMMUTABLE_CURSOR_MANIFEST/)

      // Trần vẫn tính đủ số hàng cũ -> lần thứ tư vẫn bị chặn.
      await decl(a, 3)
      await expect(decl(a, 1)).rejects.toThrow(/DECLARATION_ATTEMPT_CAP/)
    })

    it('lineage và số lần thử KHÔNG đổi được sau khi chèn', async () => {
      const { a, d } = await seed()
      for (const stmt of [
        sql`UPDATE cursor_execution_manifest SET analysis_execution_id = NULL WHERE llm_execution_id = ${d}::uuid`,
        sql`UPDATE cursor_execution_manifest SET obligation_set_hash = ${H('9')} WHERE llm_execution_id = ${d}::uuid`,
        sql`UPDATE cursor_execution_manifest SET execution_role = 'ANALYSIS' WHERE llm_execution_id = ${d}::uuid`,
      ]) {
        await expect(db.execute(stmt)).rejects.toThrow(/IMMUTABLE_CURSOR_MANIFEST/)
      }
      expect(a).toBeTruthy()
    })

    it('trigger lineage của 0031 VẪN còn — 0034 không được gỡ nhầm nó', async () => {
      const r = await db.execute<{ n: number }>(sql`
        SELECT count(*)::int n FROM pg_trigger WHERE tgname = 'cursor_manifest_declaration_lineage'`)
      expect(Number(r.rows[0]!.n)).toBe(1)
    })
  })

  describe('truy vấn độ ổn định', () => {
    it('ba chặng -> vẫn MỘT lần thử khi lọc COMPOSITE', async () => {
      const { d } = await seed()
      await db.insert(schema.analysisValidation).values({
        workspaceId, analysisRunId, llmExecutionId: d, channelId, stage: 'COMPOSITE', passed: true,
      })
      const filtered = await db.execute<{ n: number }>(sql`
        SELECT count(*)::int n FROM cursor_execution_manifest m
        JOIN analysis_validation v ON v.llm_execution_id = m.llm_execution_id AND v.stage = 'COMPOSITE'
        WHERE m.llm_execution_id = ${d}::uuid`)
      expect(Number(filtered.rows[0]!.n)).toBe(1)
    })
  })
})

/** Kiểu nới lỏng cho ca dựng đầu vào bằng tay. */
type CursorInputsLike = Omit<CompositeInputs, 'declarations'> & {
  declarations: Array<Record<string, unknown>>
}
