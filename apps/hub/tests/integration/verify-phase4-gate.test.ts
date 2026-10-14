import { execFile } from 'node:child_process'
import { createHash } from 'node:crypto'
import { mkdtempSync, readFileSync, readdirSync, rmSync, unlinkSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { basename, join, resolve } from 'node:path'
import { promisify } from 'node:util'

import { sql } from 'drizzle-orm'
import { afterAll, beforeAll, describe, expect, it } from 'vitest'

import * as schema from '@/db/schema'
import { stableStringify } from '@/lib/analysis/package'
import { buildArtifactFile, buildIndexJson, runIdentity, type RunIdentity } from '@/lib/cursor/identity'
import { CONTRACT_PROVENANCE } from '@/lib/cursor/run'
import type { RunCursorAnalysisResult } from '@/lib/cursor/run'
import { ANALYSIS_SCHEMA_VERSION, CURSOR_OUTPUT_SCHEMA_VERSION } from '@/lib/cursor/schema'
import { closeTestPool, hasTestDatabase, testDb, truncateAll } from '../helpers/db'

const run = promisify(execFile)

/**
 * H-2 — `verify_phase4.mjs` chạy THẬT, qua BỘ GHI HIỆN VẬT THẬT.
 *
 * Bản viết lại của `verify_phase4.mjs` cho hợp đồng hai lượt từng được KHẲNG
 * ĐỊNH là hoạt động mà chưa từng chạy qua một hiện vật nào — đúng lỗi mà mục 10
 * của handoff gọi tên ("không khẳng định điều chưa kiểm"). Một cổng chưa từng
 * chạy thì không phải cổng.
 *
 * Bộ test này KHÔNG chép lại logic của cổng. Nó:
 *   1. dựng lineage THẬT trên PostgreSQL,
 *   2. ghi hiện vật bằng ĐÚNG `buildArtifactFile` / `buildIndexJson` mà
 *      `run-cursor.ts` gọi — không phải bằng một khối JSON viết tay,
 *   3. gọi `node verify_phase4.mjs` như một tiến trình con và đọc MÃ THOÁT.
 *
 * Một cổng chỉ được chứng minh bằng những thứ nó CHẶN. Năm ca dưới đây làm hỏng
 * đúng MỘT mắt xích mỗi ca; ca thứ sáu kiểm rằng tên tệp CŨ không vô tình thoả.
 */
describe.skipIf(!hasTestDatabase)('H-2 — cổng verify_phase4.mjs (PostgreSQL thật)', () => {
  const db = testDb()
  const LABEL = 'hinh_su'
  const H = (ch: string) => ch.repeat(64)
  const hashOf = (p: unknown) => createHash('sha256').update(stableStringify(p), 'utf8').digest('hex')

  let outDir: string
  let workspaceId: string
  let channelId: string
  let analysisRunId: string
  let requestId: string
  let promptRevisionId: string
  let analysisExecId: string
  let declExecId: string
  let resultId: string
  let compositeValidationId: string
  let identity: RunIdentity
  let artifact: Record<string, unknown>
  let seq = 9000

  const ANALYSIS_PAYLOAD_HASH = H('a')
  const OBLIGATION_SET_HASH = H('b')

  /** Thân payload hợp nhất — hình dạng mà PHẦN MỘT của cổng đọc tới. */
  const BODY = {
    schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
    analysisSummary: {
      overallAssessment: 'Kênh có một video vượt trội rõ rệt so với phần còn lại trong cửa sổ.',
      confidence: 'MEDIUM',
      confidenceRationale: 'Độ phủ dữ liệu cốt lõi đầy đủ trong cửa sổ quan sát này.',
      primaryConstraint: 'Cỡ mẫu còn nhỏ nên kết luận xu hướng cần thận trọng.',
    },
    keyFindings: [{
      id: 'F-001',
      statement: 'Video aaaaaaaaaaa nằm ở nhóm dẫn đầu về lượt xem 7 ngày trong nhóm Shorts.',
      findingType: 'OBSERVATION',
      confidence: 'MEDIUM',
      evidenceIds: ['OBS-001'],
      supportingReasoning: 'Quan sát tất định ghi nhận phân vị 92 trong nhóm cùng định dạng.',
      contradictingEvidenceIds: [],
      limitations: [],
    }],
    hypotheses: [],
    recommendations: [],
    experiments: [],
    manualReviewTargets: [],
    dataRequests: [],
    explicitNonConclusions: ['Không kết luận được về khâu tiếp cận.'],
    metricClaims: [],
    selfCheck: {
      usedOnlyProvidedEvidence: true, recomputedMetrics: false, madeCausalClaims: false,
      madeCtrOrImpressionClaims: false, allFindingEvidenceResolved: true,
    },
  }

  beforeAll(async () => {
    outDir = mkdtempSync(join(tmpdir(), 'h2-verify-'))
    await truncateAll()
    await db.execute(sql`TRUNCATE TABLE cursor_declaration_result, cursor_claim_obligation,
      cursor_analysis_result, cursor_execution_manifest, analysis_validation,
      cursor_analysis_request, analysis_package, prompt_revision, prompt_template CASCADE`)

    const [ws] = await db.insert(schema.workspace).values({ slug: 'ws-h2', name: 'W' }).returning()
    workspaceId = ws!.id
    const [ch] = await db.insert(schema.channel)
      .values({ workspaceId, label: LABEL, youtubeChannelId: 'UCh2000000000000000000', title: 'T' })
      .returning()
    channelId = ch!.id
    const [algo] = await db.insert(schema.algorithm)
      .values({ key: 'deterministic-analysis', name: 'D', kind: 'DETERMINISTIC' }).returning()
    const [ver] = await db.insert(schema.algorithmVersion)
      .values({ algorithmId: algo!.id, version: '1.0.0' }).returning()
    const [ar] = await db.insert(schema.analysisRun).values({
      workspaceId, channelId, subjectType: 'CHANNEL', subjectId: channelId,
      algorithmId: algo!.id, algorithmVersionId: ver!.id, runSequence: 1, inputHash: H('c'),
      periodStart: '2026-06-01', periodEnd: '2026-07-27', status: 'SUCCEEDED',
    }).returning()
    analysisRunId = ar!.id

    const pkgPayload = { schemaVersion: '1.0.0', scope: { analysisRunId, channelId } }
    const pkgHash = H('a')
    const [pkg] = await db.insert(schema.analysisPackage).values({
      workspaceId, analysisRunId, channelId, schemaVersion: '1.0.0',
      payload: pkgPayload as never, payloadHash: pkgHash, packageBytes: 100,
      rawInputBytes: 1000, reductionPercent: '90',
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
      packageHash: pkgHash, promptRevisionId, promptHash: H('b'), promptBytes: 10,
    }).returning()
    requestId = req!.id

    /*
     * Trạng thái ban đầu KHÔNG phải SUCCEEDED — có trigger chặn
     * `EXECUTION_SUCCEEDED_WITHOUT_RESULT`. Đúng thứ tự của lần chạy thật: chạy
     * xong, ghi kết quả + phán quyết, RỒI mới được mang trạng thái ĐẠT.
     */
    const execution = async (): Promise<string> => {
      const [e] = await db.insert(schema.llmExecution).values({
        workspaceId, analysisRunId, promptRevisionId, provider: 'CURSOR_CLI',
        iteration: 1, executionSequence: seq++, status: 'RUNNING',
        rawOutputHash: H('f'), startedAt: new Date(), finishedAt: new Date(), durationMs: 1,
      }).returning()
      return e!.id
    }
    const markSucceeded = async (id: string) => {
      await db.execute(sql`UPDATE llm_execution SET status = 'SUCCEEDED' WHERE id = ${id}`)
    }

    /*
     * Băm nguồn lấy từ `CONTRACT_PROVENANCE` THẬT, không phải chuỗi giữ chỗ.
     *
     * Bản kê của lần chạy thật ghi đúng các băm này, và `_meta` của hiện vật cũng
     * chép từ đó. Dùng chuỗi giữ chỗ ở một phía sẽ làm ca "lành mạnh" ĐỎ vì một
     * lý do bịa — và khi ấy bộ test không còn chứng minh được gì về cổng.
     */
    const BASE = {
      toolName: '/usr/local/bin/cursor-agent', schemaVersion: ANALYSIS_SCHEMA_VERSION,
      promptVersion: '4.0.0',
      validatorHash: CONTRACT_PROVENANCE.validatorHash,
      schemaHash: CONTRACT_PROVENANCE.schemaHash,
      promptSourceHash: CONTRACT_PROVENANCE.promptSourceHash,
      // Năm băm của 0035 — cổng nay ĐỐI CHIẾU chúng với `_meta` của hiện vật.
      obligationGeneratorHash: CONTRACT_PROVENANCE.obligationGeneratorHash,
      compositeSourceHash: CONTRACT_PROVENANCE.compositeSourceHash,
      sensitiveLexiconHash: CONTRACT_PROVENANCE.sensitiveLexiconHash,
      identitySourceHash: CONTRACT_PROVENANCE.identitySourceHash,
      provenanceSourceHash: CONTRACT_PROVENANCE.provenanceSourceHash,
      flags: ['--print'], exitCode: 0, failureClass: 'NONE' as const,
    }

    // --- lượt PHÂN TÍCH ---
    analysisExecId = await execution()
    await db.insert(schema.cursorExecutionManifest).values({
      workspaceId, analysisRunId, llmExecutionId: analysisExecId, requestId, attemptNumber: 1,
      executionRole: 'ANALYSIS', startedAt: new Date(), ...BASE,
    })
    await db.insert(schema.analysisValidation).values({
      workspaceId, analysisRunId, llmExecutionId: analysisExecId, channelId,
      stage: 'ANALYSIS', passed: true,
    })
    // Văn xuôi lượt 1 được đóng băng thành hàng kết quả vai ANALYSIS — đúng như
    // lần chạy hai lượt thật ghi, và là hàng mà F3/F6 nói tới.
    await db.insert(schema.cursorAnalysisResult).values({
      workspaceId, analysisRunId, llmExecutionId: analysisExecId, requestId, channelId,
      schemaVersion: ANALYSIS_SCHEMA_VERSION, resultRole: 'ANALYSIS',
      payload: { schemaVersion: ANALYSIS_SCHEMA_VERSION, note: 'văn xuôi lượt 1' } as never,
      payloadHash: ANALYSIS_PAYLOAD_HASH,
    })
    await markSucceeded(analysisExecId)

    // Tập nghĩa vụ — bắt buộc: có trigger `RESULT_WITHOUT_OBLIGATION_SET` chặn
    // hiện vật hợp nhất ra đời khi lượt phân tích chưa sinh tập nghĩa vụ.
    await db.insert(schema.cursorClaimObligation).values({
      workspaceId, analysisRunId, channelId, requestId, analysisExecutionId: analysisExecId,
      analysisHash: ANALYSIS_PAYLOAD_HASH, obligationSetHash: OBLIGATION_SET_HASH,
      generatorVersion: '1.0', obligationCount: 1,
      obligations: { analysisHash: ANALYSIS_PAYLOAD_HASH, obligations: [{ id: 'MC-001' }] } as never,
    })

    // --- lượt KHAI BÁO (mang hiện vật hợp nhất) ---
    declExecId = await execution()
    await db.insert(schema.cursorExecutionManifest).values({
      workspaceId, analysisRunId, llmExecutionId: declExecId, requestId, attemptNumber: 1,
      executionRole: 'DECLARATION', analysisExecutionId: analysisExecId,
      obligationGeneratorVersion: CONTRACT_PROVENANCE.obligationGeneratorVersion,
      declarationPromptVersion: CONTRACT_PROVENANCE.declarationPromptVersion,
      declarationPromptSourceHash: CONTRACT_PROVENANCE.declarationPromptSourceHash,
      compositeValidatorVersion: CONTRACT_PROVENANCE.compositeValidatorVersion,
      analysisPayloadHash: ANALYSIS_PAYLOAD_HASH, obligationSetHash: OBLIGATION_SET_HASH,
      startedAt: new Date(), ...BASE,
    })
    await db.insert(schema.analysisValidation).values({
      workspaceId, analysisRunId, llmExecutionId: declExecId, channelId,
      stage: 'DECLARATION', passed: true,
    })
    const [cv] = await db.insert(schema.analysisValidation).values({
      workspaceId, analysisRunId, llmExecutionId: declExecId, channelId,
      stage: 'COMPOSITE', passed: true,
      totalEvidenceRefs: 1, unresolvedEvidenceRefs: 0,
      causalViolations: 0, ctrViolations: 0, unsupportedMetricViolations: 0,
      structuralIssues: [], evidenceIssues: [], claimIssues: [], qualityIssues: [],
    }).returning()
    compositeValidationId = cv!.id

    // Bản khai của lượt 2 — trigger `RESULT_WITHOUT_DECLARATION_PAYLOAD` đòi.
    const declPayload = {
      schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
      obligationSetHash: OBLIGATION_SET_HASH,
      declarations: [{ id: 'MC-001' }],
    }
    await db.insert(schema.cursorDeclarationResult).values({
      workspaceId, analysisRunId, channelId, requestId,
      llmExecutionId: declExecId, analysisExecutionId: analysisExecId,
      analysisPayloadHash: ANALYSIS_PAYLOAD_HASH, obligationSetHash: OBLIGATION_SET_HASH,
      declarationCount: 1, payloadHash: hashOf(declPayload), payload: declPayload as never,
    })

    /*
     * `payload` trong DB MANG `_meta` — đúng như bộ ghi thật lưu. Cổng phải gỡ
     * `_meta` ở CẢ HAI phía trước khi so thân, và ca "lành mạnh ĐẠT" là chỗ duy
     * nhất chứng minh được điều đó.
     */
    const dbPayload = {
      _meta: {
        analysisExecutionId: analysisExecId,
        declarationExecutionId: declExecId,
        analysisPayloadHash: ANALYSIS_PAYLOAD_HASH,
        obligationSetHash: OBLIGATION_SET_HASH,
        obligationGeneratorVersion: CONTRACT_PROVENANCE.obligationGeneratorVersion,
        compositeValidatorVersion: CONTRACT_PROVENANCE.compositeValidatorVersion,
      },
      ...BODY,
    }
    const [res] = await db.insert(schema.cursorAnalysisResult).values({
      workspaceId, analysisRunId, llmExecutionId: declExecId, requestId, channelId,
      schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION, resultRole: 'COMPOSITE',
      payload: dbPayload as never, payloadHash: hashOf(dbPayload),
      analysisPayloadHash: ANALYSIS_PAYLOAD_HASH, obligationSetHash: OBLIGATION_SET_HASH,
    }).returning()
    resultId = res!.id
    await markSucceeded(declExecId)

    /*
     * HIỆN VẬT dựng bằng ĐÚNG hàm mà `run-cursor.ts` gọi. Đây là điều kiện của
     * H-2: đi qua BỘ GHI THẬT, không phải một khối JSON viết tay trong test.
     */
    const r = {
      requestId, channelLabel: LABEL, packageHash: pkgHash, promptHash: H('b'), promptBytes: 1,
      attempts: [], finalAttempt: 1, output: dbPayload as never, report: null,
      status: 'SUCCEEDED', analysisAttempts: [{}], declarationAttempts: [{}],
      analysisExecutionId: analysisExecId, declarationExecutionId: declExecId,
      obligationCount: 0, obligationSetHash: OBLIGATION_SET_HASH,
      analysisPayloadHash: ANALYSIS_PAYLOAD_HASH, declarations: [], declarationPromptBytes: 1,
      compositePayloadHash: hashOf(dbPayload), resultId, compositeValidationId,
      analysisRunId, channelId, compositeFailureClass: null,
    } as unknown as RunCursorAnalysisResult

    identity = runIdentity(r)
    artifact = buildArtifactFile(dbPayload as unknown as Record<string, unknown>, r, CONTRACT_PROVENANCE, {
      channelLabel: LABEL,
      durationMs: 10,
      outputSchemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
      writtenAt: new Date().toISOString(),
    })
  })

  afterAll(async () => {
    rmSync(outDir, { recursive: true, force: true })
    await closeTestPool()
  })

  /** Ghi hiện vật + INDEX.json, cho phép từng ca làm hỏng đúng một mắt xích. */
  function writeArtifacts(over: {
    artifactMutate?: (a: Record<string, unknown>) => Record<string, unknown>
    identityMutate?: (i: RunIdentity) => RunIdentity
    fileName?: string
    deleteFileAfter?: boolean
    /** Thứ tự `files` mà INDEX tuyên bố — mô phỏng readdirSync trả về thứ tự khác. */
    fileOrder?: (names: string[]) => string[]
    /** Danh tính BỔ SUNG (nhiều mẫu) kèm hiện vật riêng. */
    extra?: Array<{ fileName: string; mutate: (a: Record<string, unknown>) => Record<string, unknown>; ident: RunIdentity }>
    /** Không có lần chạy nào được cấp phép. */
    noneAuthorized?: boolean
  } = {}) {
    for (const f of readdirSync(outDir)) unlinkSync(resolve(outDir, f))

    const fname = over.fileName ?? `${LABEL}.cursor.s1.json`
    const names: string[] = []
    const idents: RunIdentity[] = []

    if (!over.noneAuthorized) {
      const a = over.artifactMutate ? over.artifactMutate(structuredClone(artifact)) : artifact
      writeFileSync(resolve(outDir, fname), JSON.stringify(a, null, 2), 'utf8')
      names.push(fname)
      idents.push(over.identityMutate ? over.identityMutate(structuredClone(identity)) : identity)
    } else {
      // Mọi lần chạy đều HỎNG: `run-cursor.ts` vẫn đẩy danh tính cho lần hỏng.
      idents.push({ ...structuredClone(identity), status: 'REJECTED_SCHEMA', resultId: null })
    }

    for (const e of over.extra ?? []) {
      writeFileSync(resolve(outDir, e.fileName), JSON.stringify(e.mutate(structuredClone(artifact)), null, 2), 'utf8')
      names.push(e.fileName)
      idents.push(e.ident)
    }

    const declared = over.fileOrder ? over.fileOrder([...names]) : names
    const index = buildIndexJson({
      contract: CONTRACT_PROVENANCE,
      generatedAt: new Date().toISOString(),
      schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
      mode: 'successes=1',
      tally: { [LABEL]: { attempts: 1, successes: idents.length, timeouts: 0, validationFails: 0, other: 0 } },
      identities: { [LABEL]: idents },
      filesFor: () => declared,
    })
    writeFileSync(resolve(outDir, 'INDEX.json'), JSON.stringify(index, null, 2), 'utf8')

    if (over.deleteFileAfter) unlinkSync(resolve(outDir, fname))
  }

  /**
   * Dựng MẪU THỨ HAI đầy đủ trên database và hiện vật tương ứng.
   *
   * Cần cho ca "thứ tự readdirSync": với một mẫu duy nhất thì ghép theo vị trí
   * và ghép theo `resultId` không thể phân biệt được — và đó chính là lý do
   * khiếm khuyết này sống sót qua vòng test trước.
   */
  async function seedSecondSample(opts: {
    channelLabel?: string
    badPayloadHash?: boolean
  } = {}): Promise<{
    fileName: string
    mutate: (a: Record<string, unknown>) => Record<string, unknown>
    ident: RunIdentity
    artifact: Record<string, unknown>
  }> {
    const BASE2 = {
      toolName: '/usr/local/bin/cursor-agent', schemaVersion: ANALYSIS_SCHEMA_VERSION,
      promptVersion: '4.0.0',
      validatorHash: CONTRACT_PROVENANCE.validatorHash,
      schemaHash: CONTRACT_PROVENANCE.schemaHash,
      promptSourceHash: CONTRACT_PROVENANCE.promptSourceHash,
      // Năm băm của 0035 — cổng nay ĐỐI CHIẾU chúng với `_meta` của hiện vật.
      obligationGeneratorHash: CONTRACT_PROVENANCE.obligationGeneratorHash,
      compositeSourceHash: CONTRACT_PROVENANCE.compositeSourceHash,
      sensitiveLexiconHash: CONTRACT_PROVENANCE.sensitiveLexiconHash,
      identitySourceHash: CONTRACT_PROVENANCE.identitySourceHash,
      provenanceSourceHash: CONTRACT_PROVENANCE.provenanceSourceHash,
      flags: ['--print'], exitCode: 0, failureClass: 'NONE' as const,
    }
    const exec2 = async (runId: string): Promise<string> => {
      const [e] = await db.insert(schema.llmExecution).values({
        workspaceId, analysisRunId: runId, promptRevisionId, provider: 'CURSOR_CLI',
        iteration: 1, executionSequence: seq++, status: 'RUNNING',
        rawOutputHash: H('f'), startedAt: new Date(), finishedAt: new Date(), durationMs: 1,
      }).returning()
      return e!.id
    }
    const mark = (id: string) => db.execute(sql`UPDATE llm_execution SET status = 'SUCCEEDED' WHERE id = ${id}`)

    const aHash = H('7')
    const oHash = H('8')

    /*
     * Kênh RIÊNG khi được yêu cầu: cần channel + analysis_run + package +
     * request riêng, vì khoá ngoại tổ hợp buộc request phải cùng kênh và cùng
     * lần phân tích với kết quả.
     */
    let sampleChannelId = channelId
    let sampleRunId = analysisRunId
    let sampleRequestId = requestId
    if (opts.channelLabel) {
      const [ch2row] = await db.insert(schema.channel).values({
        workspaceId, label: opts.channelLabel,
        youtubeChannelId: `UCoth${seq}0000000000000`.slice(0, 24), title: 'O',
      }).returning()
      sampleChannelId = ch2row!.id
      const [algo2] = await db.insert(schema.algorithm)
        .values({ key: `det-${seq}`, name: 'D', kind: 'DETERMINISTIC' }).returning()
      const [ver2] = await db.insert(schema.algorithmVersion)
        .values({ algorithmId: algo2!.id, version: '1.0.0' }).returning()
      const [ar2] = await db.insert(schema.analysisRun).values({
        workspaceId, channelId: sampleChannelId, subjectType: 'CHANNEL', subjectId: sampleChannelId,
        algorithmId: algo2!.id, algorithmVersionId: ver2!.id, runSequence: 1, inputHash: H('c'),
        periodStart: '2026-06-01', periodEnd: '2026-07-27', status: 'SUCCEEDED',
      }).returning()
      sampleRunId = ar2!.id
      const [pkg2] = await db.insert(schema.analysisPackage).values({
        workspaceId, analysisRunId: sampleRunId, channelId: sampleChannelId, schemaVersion: '1.0.0',
        payload: { schemaVersion: '1.0.0' } as never, payloadHash: H('a'),
        packageBytes: 100, rawInputBytes: 1000, reductionPercent: '90',
      }).returning()
      const [req2] = await db.insert(schema.cursorAnalysisRequest).values({
        workspaceId, channelId: sampleChannelId, analysisRunId: sampleRunId,
        analysisPackageId: pkg2!.id, packageHash: H('a'), promptRevisionId,
        promptHash: H('b'), promptBytes: 10,
      }).returning()
      sampleRequestId = req2!.id
    }

    const a2 = await exec2(sampleRunId)
    await db.insert(schema.cursorExecutionManifest).values({
      workspaceId, analysisRunId: sampleRunId, llmExecutionId: a2, requestId: sampleRequestId, attemptNumber: 1,
      executionRole: 'ANALYSIS', startedAt: new Date(), ...BASE2,
    })
    await db.insert(schema.analysisValidation).values({
      workspaceId, analysisRunId: sampleRunId, llmExecutionId: a2, channelId: sampleChannelId, stage: 'ANALYSIS', passed: true,
    })
    await db.insert(schema.cursorAnalysisResult).values({
      workspaceId, analysisRunId: sampleRunId, llmExecutionId: a2, requestId: sampleRequestId, channelId: sampleChannelId,
      schemaVersion: ANALYSIS_SCHEMA_VERSION, resultRole: 'ANALYSIS',
      payload: { schemaVersion: ANALYSIS_SCHEMA_VERSION, note: 'văn xuôi mẫu 2' } as never,
      payloadHash: aHash,
    })
    await mark(a2)
    await db.insert(schema.cursorClaimObligation).values({
      workspaceId, analysisRunId: sampleRunId, channelId: sampleChannelId, requestId: sampleRequestId, analysisExecutionId: a2,
      analysisHash: aHash, obligationSetHash: oHash, generatorVersion: '1.0',
      obligationCount: 1, obligations: { analysisHash: aHash, obligations: [{ id: 'MC-001' }] } as never,
    })

    const d2 = await exec2(sampleRunId)
    await db.insert(schema.cursorExecutionManifest).values({
      workspaceId, analysisRunId: sampleRunId, llmExecutionId: d2, requestId: sampleRequestId, attemptNumber: 1,
      executionRole: 'DECLARATION', analysisExecutionId: a2,
      obligationGeneratorVersion: CONTRACT_PROVENANCE.obligationGeneratorVersion,
      declarationPromptVersion: CONTRACT_PROVENANCE.declarationPromptVersion,
      declarationPromptSourceHash: CONTRACT_PROVENANCE.declarationPromptSourceHash,
      compositeValidatorVersion: CONTRACT_PROVENANCE.compositeValidatorVersion,
      analysisPayloadHash: aHash, obligationSetHash: oHash,
      startedAt: new Date(), ...BASE2,
    })
    await db.insert(schema.analysisValidation).values({
      workspaceId, analysisRunId: sampleRunId, llmExecutionId: d2, channelId: sampleChannelId, stage: 'DECLARATION', passed: true,
    })
    const [cv2] = await db.insert(schema.analysisValidation).values({
      workspaceId, analysisRunId: sampleRunId, llmExecutionId: d2, channelId: sampleChannelId, stage: 'COMPOSITE', passed: true,
      totalEvidenceRefs: 1, unresolvedEvidenceRefs: 0,
      causalViolations: 0, ctrViolations: 0, unsupportedMetricViolations: 0,
      structuralIssues: [], evidenceIssues: [], claimIssues: [], qualityIssues: [],
    }).returning()
    const declPayload2 = {
      schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION, obligationSetHash: oHash,
      declarations: [{ id: 'MC-001' }],
    }
    await db.insert(schema.cursorDeclarationResult).values({
      workspaceId, analysisRunId: sampleRunId, channelId: sampleChannelId, requestId: sampleRequestId,
      llmExecutionId: d2, analysisExecutionId: a2,
      analysisPayloadHash: aHash, obligationSetHash: oHash,
      declarationCount: 1, payloadHash: hashOf(declPayload2), payload: declPayload2 as never,
    })
    const dbPayload2 = {
      _meta: {
        analysisExecutionId: a2, declarationExecutionId: d2,
        analysisPayloadHash: aHash, obligationSetHash: oHash,
        obligationGeneratorVersion: CONTRACT_PROVENANCE.obligationGeneratorVersion,
        compositeValidatorVersion: CONTRACT_PROVENANCE.compositeValidatorVersion,
      },
      ...BODY,
    }
    const [res2] = await db.insert(schema.cursorAnalysisResult).values({
      workspaceId, analysisRunId: sampleRunId, llmExecutionId: d2, requestId: sampleRequestId, channelId: sampleChannelId,
      schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION, resultRole: 'COMPOSITE',
      payload: dbPayload2 as never,
      payloadHash: opts.badPayloadHash ? H('9') : hashOf(dbPayload2),
      analysisPayloadHash: aHash, obligationSetHash: oHash,
    }).returning()
    await mark(d2)

    const r2 = {
      requestId: sampleRequestId, channelLabel: opts.channelLabel ?? LABEL,
      packageHash: H('a'), promptHash: H('b'), promptBytes: 1,
      attempts: [], finalAttempt: 1, output: dbPayload2 as never, report: null,
      status: 'SUCCEEDED', analysisAttempts: [{}], declarationAttempts: [{}],
      analysisExecutionId: a2, declarationExecutionId: d2,
      obligationCount: 1, obligationSetHash: oHash, analysisPayloadHash: aHash,
      declarations: [], declarationPromptBytes: 1,
      compositePayloadHash: hashOf(dbPayload2), resultId: res2!.id,
      compositeValidationId: cv2!.id, analysisRunId: sampleRunId, channelId: sampleChannelId,
      compositeFailureClass: null,
    } as unknown as RunCursorAnalysisResult

    const art2 = buildArtifactFile(dbPayload2 as unknown as Record<string, unknown>, r2, CONTRACT_PROVENANCE, {
      channelLabel: opts.channelLabel ?? LABEL, durationMs: 10,
      outputSchemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION, writtenAt: new Date().toISOString(),
    })
    return {
      fileName: `${LABEL}.cursor.s2.json`,
      mutate: () => art2,
      ident: runIdentity(r2),
      artifact: art2,
    }
  }

  const seedOtherChannelSample = () => seedSecondSample({ channelLabel: 'phat_giao' })
  const seedBadPayloadHashSample = () => seedSecondSample({ badPayloadHash: true })

  /** Chạy cổng THẬT như tiến trình con. Trả về mã thoát và toàn bộ output. */
  async function runGate(): Promise<{ code: number; out: string }> {
    const since = new Date(Date.now() - 3600_000).toISOString()
    try {
      const { stdout } = await run('node', ['verify_phase4.mjs', since], {
        cwd: resolve(__dirname, '../..'),
        env: {
          ...process.env,
          // `DATABASE_URL` trong vitest ĐÃ là database TEST (xem tests/setup.ts).
          VERIFY_DATABASE_URL: process.env.DATABASE_URL,
          VERIFY_OUT_DIR: outDir,
          VERIFY_CHANNELS: LABEL,
        },
        maxBuffer: 20 * 1024 * 1024,
      })
      return { code: 0, out: stdout }
    } catch (e) {
      const err = e as { code?: number; stdout?: string; stderr?: string }
      return { code: err.code ?? 1, out: `${err.stdout ?? ''}${err.stderr ?? ''}` }
    }
  }

  it('1. hiện vật LÀNH MẠNH -> cổng ĐẠT (mã thoát 0)', async () => {
    writeArtifacts()
    const { code, out } = await runGate()
    expect(code, out).toBe(0)
    expect(out).toContain('TẤT CẢ KIỂM CHỨNG ĐỀU ĐẠT')
    // Không phải "đạt vì không kiểm gì": phải thấy đúng phép neo danh tính.
    expect(out).toMatch(/\d+ trường danh tính\/băm khớp DB/)
    expect(out).toMatch(/9 trường danh tính của INDEX khớp DB/)
    expect(out).toContain('hiện vật thuộc đúng kênh')
    expect(out).toContain('băm payload khớp payload đã lưu')
    expect(out).toContain('thân tệp khớp payload DB (dạng chuẩn tắc)')
    /*
     * ĐỐI CHỨNG cho phép kiểm DB→INDEX của ca 8.
     *
     * Không có nó, ca 8 vẫn xanh ngay cả khi phép kiểm ấy ĐỎ trên MỌI lô — kể cả
     * lô lành mạnh — và một cổng luôn đỏ thì bị bỏ qua chứ không được tin.
     *
     * Chỗ duy nhất đặt được là ca này: nó chạy TRƯỚC mọi ca dựng thêm mẫu, nên
     * cửa sổ một giờ chỉ chứa đúng một hàng COMPOSITE. Các ca sau chỉ khẳng định
     * "khác 0" nên những hàng tồn đọng ấy không làm chúng sai.
     */
    expect(out).toMatch(/DB→INDEX: cả 1 hàng COMPOSITE trong cửa sổ đều được chỉ mục tuyên bố/)
  })

  it('2a. INDEX khai sai resultId -> TRƯỢT (không ghép được về tệp)', async () => {
    writeArtifacts({
      identityMutate: (i) => ({ ...i, resultId: '00000000-0000-4000-8000-000000000001' }),
    })
    const { code, out } = await runGate()
    expect(code, out).not.toBe(0)
    expect(out).toMatch(/thiếu tệp cho mẫu 1 \(resultId 00000000-0000-4000-8000-000000000001\)/)
  })

  it('2b. resultId KHÔNG có hàng kết quả chính thức trong DB -> TRƯỢT', async () => {
    // Ghép theo resultId nên phải làm hỏng CẢ HAI phía để tới được phép tra DB.
    // Đây là ca chứng minh cổng thật sự HỎI database, không chỉ so tệp với INDEX.
    const fake = '00000000-0000-4000-8000-000000000009'
    writeArtifacts({
      identityMutate: (i) => ({ ...i, resultId: fake }),
      artifactMutate: (a) => {
        ;(a._meta as Record<string, unknown>).resultId = fake
        return a
      },
    })
    const { code, out } = await runGate()
    expect(code, out).not.toBe(0)
    expect(out).toMatch(/KHÔNG có hàng kết quả chính thức nào/)
  })

  it('3. sai id lượt KHAI BÁO trong _meta -> TRƯỢT', async () => {
    writeArtifacts({
      artifactMutate: (a) => {
        const m = a._meta as Record<string, unknown>
        m.declarationExecutionId = '00000000-0000-4000-8000-000000000002'
        return a
      },
    })
    const { code, out } = await runGate()
    expect(code, out).not.toBe(0)
    expect(out).toMatch(/_meta\.declarationExecutionId = .* nhưng DB có/)
  })

  it('4. băm payload CŨ trong _meta -> TRƯỢT', async () => {
    writeArtifacts({
      artifactMutate: (a) => {
        const m = a._meta as Record<string, unknown>
        m.analysisPayloadHash = H('9')
        return a
      },
    })
    const { code, out } = await runGate()
    expect(code, out).not.toBe(0)
    expect(out).toMatch(/_meta\.analysisPayloadHash = /)
  })

  it('5. thiếu tệp .sN -> TRƯỢT (không được im lặng bỏ qua)', async () => {
    writeArtifacts({ deleteFileAfter: true })
    const { code, out } = await runGate()
    expect(code, out).not.toBe(0)
    expect(out).toMatch(/không đọc được/)
  })

  it('6. tên tệp CŨ một lượt KHÔNG được vô tình thoả', async () => {
    // `hinh_su.cursor.json` là tên của chế độ MỘT LƯỢT. Nó phải bị từ chối bằng
    // HỢP ĐỒNG TÊN, chứ không được đi tiếp rồi tình cờ khớp mọi phép kiểm khác.
    writeArtifacts({ fileName: `${LABEL}.cursor.json` })
    const { code, out } = await runGate()
    expect(code, out).not.toBe(0)
    expect(out).toMatch(/không theo hợp đồng \.sN\/\.runN/)
  })

  /* =====================================================================
   * Phát hiện của vòng rà soát đối kháng — mỗi ca là một cổng TỪNG XANH SAI
   * ================================================================== */

  it('RÀ SOÁT (BLOCKER): KHÔNG lần chạy nào được cấp phép -> TRƯỢT', async () => {
    // `run-cursor.ts` đẩy danh tính cho MỌI lần chạy kể cả lần hỏng, nên
    // `identities` khác rỗng. Trước khi sửa: `authorized` rỗng, `files` rỗng,
    // `0 !== 0` là false, vòng lặp không chạy — cả kênh đi qua KHÔNG một dòng
    // kiểm nào, và cổng thoát 0 cho một lô không có hiện vật nào.
    writeArtifacts({ noneAuthorized: true })
    const { code, out } = await runGate()
    expect(code, out).not.toBe(0)
    expect(out).toMatch(/KHÔNG có lần chạy nào được cấp phép/)
  })

  it('RÀ SOÁT (HIGH): thứ tự tệp của readdirSync KHÔNG được đổi phán quyết', async () => {
    // `files` đến từ `readdirSync` (không sắp xếp); `identities` theo thứ tự
    // chạy. Ghép theo VỊ TRÍ nghĩa là cổng đỏ trên một lô lành mạnh ngay khi hệ
    // tệp trả về thứ tự khác — và xanh khi nó tình cờ trả đúng. Ca này khai thứ
    // tự ĐẢO NGƯỢC; nếu phép ghép theo `resultId` đúng thì vẫn phải ĐẠT.
    const second = await seedSecondSample()
    writeArtifacts({
      extra: [second],
      fileOrder: (n) => [...n].reverse(),
    })
    const { code, out } = await runGate()
    expect(code, out).toBe(0)
    expect(out).toContain('TẤT CẢ KIỂM CHỨNG ĐỀU ĐẠT')
  })

  it('RÀ SOÁT (HIGH): giá trị SENTINEL trong _meta -> TRƯỢT', async () => {
    // 'unavailable' được chép y hệt sang mọi bề mặt, nên phép so bằng nhau vẫn
    // xanh: ba bản sao khớp nhau hoàn hảo và cả ba cùng không biết gì.
    writeArtifacts({
      artifactMutate: (a) => {
        ;(a._meta as Record<string, unknown>).validatorHash = 'unavailable'
        return a
      },
    })
    const { code, out } = await runGate()
    expect(code, out).not.toBe(0)
    expect(out).toMatch(/là giá trị SENTINEL/)
  })

  /* =====================================================================
   * Phát hiện của cổng CODEX (bắt buộc) — mỗi ca là một lỗ cổng TỪNG XANH SAI
   * ================================================================== */

  it('CODEX (HIGH): TRÁO hiện vật giữa hai kênh -> TRƯỢT', async () => {
    /*
     * Cặp (danh tính, hiện vật) HỢP LỆ của kênh khác — băm thật, `_meta` thật,
     * lineage thật — đặt dưới khoá kênh này. Mọi trường trong `bind` đối chiếu
     * hàng DB của CHÍNH NÓ nên đều khớp; không có gì so khoá kênh của INDEX với
     * kênh của hàng kết quả. Cổng đóng băng chứng nhận một mẫu cho kênh chưa
     * từng sinh ra nó.
     */
    const other = await seedOtherChannelSample()
    for (const f of readdirSync(outDir)) unlinkSync(resolve(outDir, f))
    const fname = `${LABEL}.cursor.s1.json`
    writeFileSync(resolve(outDir, fname), JSON.stringify(other.artifact, null, 2), 'utf8')
    const index = buildIndexJson({
      contract: CONTRACT_PROVENANCE,
      generatedAt: new Date().toISOString(),
      schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
      mode: 'successes=1',
      tally: { [LABEL]: { attempts: 1, successes: 1, timeouts: 0, validationFails: 0, other: 0 } },
      identities: { [LABEL]: [other.ident] },
      filesFor: () => [fname],
    })
    writeFileSync(resolve(outDir, 'INDEX.json'), JSON.stringify(index, null, 2), 'utf8')

    const { code, out } = await runGate()
    expect(code, out).not.toBe(0)
    expect(out).toMatch(/tráo hiện vật giữa các kênh/)
  })

  it('CODEX (HIGH): `payload_hash` KHÔNG khớp payload -> TRƯỢT', async () => {
    // Kiểm này từng KHÔNG có test nào: xoá đúng khối băm payload trong
    // `verify_phase4.mjs` mà mọi assertion vẫn xanh.
    const bad = await seedBadPayloadHashSample()
    for (const f of readdirSync(outDir)) unlinkSync(resolve(outDir, f))
    const fname = `${LABEL}.cursor.s1.json`
    writeFileSync(resolve(outDir, fname), JSON.stringify(bad.artifact, null, 2), 'utf8')
    const index = buildIndexJson({
      contract: CONTRACT_PROVENANCE,
      generatedAt: new Date().toISOString(),
      schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
      mode: 'successes=1',
      tally: { [LABEL]: { attempts: 1, successes: 1, timeouts: 0, validationFails: 0, other: 0 } },
      identities: { [LABEL]: [bad.ident] },
      filesFor: () => [fname],
    })
    writeFileSync(resolve(outDir, 'INDEX.json'), JSON.stringify(index, null, 2), 'utf8')

    const { code, out } = await runGate()
    expect(code, out).not.toBe(0)
    expect(out).toMatch(/băm payload đã lưu .* khác băm tính lại/)
  })

  it('CODEX R2 (HIGH): kênh ĐƯỢC KỲ VỌNG mà INDEX.json không tuyên bố -> TRƯỢT', async () => {
    /*
     * PHẦN HAI chỉ lặp trên `idx.channels`. Một kênh nằm trong danh sách kỳ vọng
     * mà KHÔNG có mục trong chỉ mục thì không được đối chiếu gì cả — và phép quét
     * hiện vật mồ côi cũng không cứu được, vì nếu tệp của nó đã bị xoá thì không
     * còn gì trên đĩa để mà mồ côi. Lô một kênh sẽ qua cổng đòi ba kênh.
     *
     * Ca này chạy cổng với HAI kênh kỳ vọng trong khi INDEX chỉ tuyên bố một.
     */
    writeArtifacts()
    const since = new Date(Date.now() - 3600_000).toISOString()
    let out = ''
    let code = 0
    try {
      const r = await run('node', ['verify_phase4.mjs', since], {
        cwd: resolve(__dirname, '../..'),
        env: {
          ...process.env,
          VERIFY_DATABASE_URL: process.env.DATABASE_URL,
          VERIFY_OUT_DIR: outDir,
          VERIFY_CHANNELS: `${LABEL},phong_thuy`,
        },
        maxBuffer: 20 * 1024 * 1024,
      })
      out = r.stdout
    } catch (e) {
      const err = e as { code?: number; stdout?: string; stderr?: string }
      code = err.code ?? 1
      out = `${err.stdout ?? ''}${err.stderr ?? ''}`
    }
    expect(code, out).not.toBe(0)
    expect(out).toMatch(/KHÔNG tuyên bố kênh "phong_thuy"/)
  })

  it('CODEX R3 (HIGH): INDEX khai TRÙNG resultId -> TRƯỢT', async () => {
    /*
     * Ghép theo `resultId` chưa đủ. Nếu INDEX khai HAI danh tính cùng một
     * `resultId`, vòng lặp tra cùng một tệp HAI LẦN; tệp thứ hai vẫn được INDEX
     * tuyên bố nên thoát cả phép quét mồ côi, và KHÔNG bao giờ được đối chiếu.
     * Số lượng khớp, mọi phép kiểm xanh, một mẫu chưa từng được kiểm vẫn nằm
     * trong lô.
     */
    const second = await seedSecondSample()
    for (const f of readdirSync(outDir)) unlinkSync(resolve(outDir, f))
    const f1 = `${LABEL}.cursor.s1.json`
    const f2 = second.fileName
    writeFileSync(resolve(outDir, f1), JSON.stringify(artifact, null, 2), 'utf8')
    writeFileSync(resolve(outDir, f2), JSON.stringify(second.artifact, null, 2), 'utf8')
    const index = buildIndexJson({
      contract: CONTRACT_PROVENANCE,
      generatedAt: new Date().toISOString(),
      schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
      mode: 'successes=2',
      tally: { [LABEL]: { attempts: 2, successes: 2, timeouts: 0, validationFails: 0, other: 0 } },
      // HAI danh tính, CÙNG một resultId.
      identities: { [LABEL]: [identity, { ...second.ident, resultId: identity.resultId }] },
      filesFor: () => [f1, f2],
    })
    writeFileSync(resolve(outDir, 'INDEX.json'), JSON.stringify(index, null, 2), 'utf8')

    const { code, out } = await runGate()
    expect(code, out).not.toBe(0)
    expect(out).toMatch(/khai TRÙNG resultId/)
    expect(out, 'tệp thứ hai phải bị nêu là chưa hề được kiểm').toMatch(/KHÔNG mẫu nào đối chiếu tới/)
  })

  it('CODEX R14 (MEDIUM): trường danh tính INDEX bị hỏng -> TRƯỢT', async () => {
    // Chín trường `indexBind` mới cần một ca làm hỏng THẬT, nếu không xoá một
    // dòng trong danh sách ấy mà toàn bộ test vẫn xanh.
    writeArtifacts({
      identityMutate: (i) => ({
        ...i,
        analysisExecutionId: '00000000-0000-4000-8000-0000000000aa',
      }),
    })
    const { code, out } = await runGate()
    expect(code, out).not.toBe(0)
    expect(out).toMatch(/INDEX\.identities\.analysisExecutionId = .* nhưng DB có/)
  })

  it('CODEX R14 (HIGH): tên tệp THOÁT khỏi thư mục hiện vật -> TRƯỢT', async () => {
    /*
     * `new URL(fname, OUT_DIR)` giải đường dẫn tương đối, nên một chỉ mục khai
     * `"../x/hinh_su.cursor.s1.json"` khiến cổng đọc tệp NGOÀI thư mục đang xét.
     */
    writeArtifacts()
    const index = JSON.parse(readFileSync(resolve(outDir, 'INDEX.json'), 'utf8')) as {
      channels: Record<string, { files: string[] }>
    }
    index.channels[LABEL]!.files = [`../${basename(outDir)}/${LABEL}.cursor.s1.json`]
    writeFileSync(resolve(outDir, 'INDEX.json'), JSON.stringify(index, null, 2), 'utf8')

    const { code, out } = await runGate()
    expect(code, out).not.toBe(0)
    expect(out).toMatch(/không phải tên trần trong thư mục hiện vật/)
  })

  it('CODEX R20 (HIGH): hàng kết quả CŨ + tệp hiện vật MỚI -> TRƯỢT', async () => {
    /*
     * Phép tra database của PHẦN HAI chỉ ràng buộc `r.id`, còn phép chống-cũ chỉ
     * nhìn mtime của TỆP. Nên `INDEX.json` chỉ cần trỏ tới một hàng COMPOSITE
     * hợp lệ nhưng CŨ của cùng kênh, rồi ghi lại tệp cho mtime mới, là qua cổng —
     * chứng nhận một lô mà lineage database và hiện vật thuộc hai lần chạy khác nhau.
     */
    const stale = await seedSecondSample()
    // Đẩy execution của mẫu ấy ra NGOÀI cửa sổ đang xét.
    await db.execute(sql`
      UPDATE llm_execution SET created_at = now() - interval '400 days'
       WHERE id = ${stale.ident.declarationExecutionId}`)

    for (const f of readdirSync(outDir)) unlinkSync(resolve(outDir, f))
    const fname = `${LABEL}.cursor.s1.json`
    writeFileSync(resolve(outDir, fname), JSON.stringify(stale.artifact, null, 2), 'utf8')
    const index = buildIndexJson({
      contract: CONTRACT_PROVENANCE,
      generatedAt: new Date().toISOString(),
      schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
      mode: 'successes=1',
      tally: { [LABEL]: { attempts: 1, successes: 1, timeouts: 0, validationFails: 0, other: 0 } },
      identities: { [LABEL]: [stale.ident] },
      filesFor: () => [fname],
    })
    writeFileSync(resolve(outDir, 'INDEX.json'), JSON.stringify(index, null, 2), 'utf8')

    const { code, out } = await runGate()
    expect(code, out).not.toBe(0)
    expect(out).toMatch(/trong cửa sổ đang xét/)
  })

  it('M-5: hiện vật của kênh KHÔNG có trong INDEX.json -> TRƯỢT', async () => {
    // Chạy lại MỘT kênh ghi đè chỉ mục ba kênh bằng chỉ mục một kênh, trong khi
    // hiện vật hai kênh kia vẫn nằm trên đĩa. Vòng lặp theo kênh-được-tuyên-bố
    // không bao giờ chạm tới chúng, nên chúng biến khỏi tầm nhìn của cổng.
    writeArtifacts()
    writeFileSync(resolve(outDir, 'phat_giao.cursor.s1.json'), '{}', 'utf8')
    const { code, out } = await runGate()
    expect(code, out).not.toBe(0)
    expect(out).toMatch(/thuộc kênh "phat_giao" mà INDEX\.json KHÔNG tuyên bố/)
  })

  it('7. hiện vật MỒ CÔI trên đĩa -> TRƯỢT', async () => {
    // Không nằm trong 6 yêu cầu của H-2 nhưng cùng họ: bản viết lại tuyên bố phát
    // hiện được hiện vật mồ côi, và tuyên bố ấy cũng chưa từng được chạy.
    writeArtifacts()
    writeFileSync(resolve(outDir, `${LABEL}.cursor.s2.json`), '{}', 'utf8')
    const { code, out } = await runGate()
    expect(code, out).not.toBe(0)
    expect(out).toMatch(/KHÔNG được INDEX\.json tuyên bố/)
  })

  it('8. CẮT MẪU: hàng COMPOSITE có trong DB mà INDEX không tuyên bố -> TRƯỢT', async () => {
    /*
     * Đường lách rẻ nhất còn lại: mọi phép đối chiếu khác đều khởi hành TỪ
     * `INDEX.json`, nên xoá một cặp (danh tính + tệp) làm cả `files` lẫn
     * `authorized` cùng co lại và phép so `3 = 3` vẫn xanh. Chạy tới khi đẹp rồi
     * chọn 3 mẫu ưng ý không để lại vết đỏ nào.
     *
     * Ở đây: dựng ĐỦ mẫu trên database rồi CỐ Ý không đưa nó vào chỉ mục. Khẳng
     * định trên ĐÚNG `resultId` vừa dựng, không trên tổng số, để ca này không
     * phụ thuộc vào những mẫu mà các ca chạy trước đã để lại trong cửa sổ.
     */
    const dropped = await seedSecondSample()
    writeArtifacts()
    const { code, out } = await runGate()
    expect(code, out).not.toBe(0)
    expect(out).toContain(
      `database CÓ hàng kết quả chính thức ${dropped.ident.resultId} trong cửa sổ nhưng INDEX.json KHÔNG tuyên bố`,
    )
  })

  it('9. BẢNG ĐẾM của INDEX mâu thuẫn với số danh tính -> TRƯỢT', async () => {
    // Phiên bản rẻ tiền của ca 8: xoá tệp mà quên sửa `successes`.
    writeArtifacts()
    const p = resolve(outDir, 'INDEX.json')
    const idx = JSON.parse(readFileSync(p, 'utf8'))
    idx.channels[LABEL].successes = 3
    writeFileSync(p, JSON.stringify(idx, null, 2), 'utf8')
    const { code, out } = await runGate()
    expect(code, out).not.toBe(0)
    expect(out).toMatch(/INDEX\.successes = 3 nhưng chỉ có 1 danh tính được cấp phép/)
  })
})
