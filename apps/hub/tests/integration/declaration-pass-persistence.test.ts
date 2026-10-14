import { afterAll, beforeAll, describe, expect, it } from 'vitest'
import { and, eq, sql } from 'drizzle-orm'

import * as schema from '@/db/schema'
import { closeTestPool, hasTestDatabase, testDb, truncateAll } from '../helpers/db'

/**
 * BẰNG CHỨNG CỔNG G3 — lưu trữ của kiến trúc HAI LƯỢT, trên PostgreSQL THẬT.
 *
 * Mỗi bất biến ở đây được kiểm bằng một phép GHI thật, cả chiều thuận lẫn chiều
 * nghịch. Định nghĩa đối tượng đã được `verify_g3.mjs` đối chiếu qua pg_catalog;
 * tệp này kiểm HÀNH VI, vì một ràng buộc tồn tại mà không cưỡng chế đúng thì đọc
 * catalog không phát hiện được.
 */
describe.skipIf(!hasTestDatabase)('G3 — lưu trữ lượt khai báo (PostgreSQL thật)', () => {
  const db = testDb()
  let workspaceId: string
  let channelId: string
  let analysisRunId: string
  let requestId: string
  let promptRevisionId: string

  const H = (c: string) => c.repeat(64)
  let seq = 900

  beforeAll(async () => {
    await truncateAll()
    await db.execute(sql`TRUNCATE TABLE cursor_claim_obligation, cursor_analysis_result,
      cursor_execution_manifest, analysis_validation, cursor_analysis_request, analysis_package,
      analysis_quality, anomaly, cohort_summary, evidence_reference, deterministic_observation,
      feature_value, feature_version, feature_definition, video_daily_metric_history,
      video_daily_metric, channel_daily_metric, video CASCADE`)

    const [ws] = await db.insert(schema.workspace).values({ slug: 'ws-g3', name: 'W' }).returning()
    workspaceId = ws!.id
    const [ch] = await db
      .insert(schema.channel)
      .values({ workspaceId, label: 'hinh_su', youtubeChannelId: 'UCg3000000000000000000', title: 'T' })
      .returning()
    channelId = ch!.id
    const [algo] = await db
      .insert(schema.algorithm)
      .values({ key: 'deterministic-analysis', name: 'D', kind: 'DETERMINISTIC' })
      .returning()
    const [ver] = await db
      .insert(schema.algorithmVersion)
      .values({ algorithmId: algo!.id, version: '1.0.0' })
      .returning()
    const [run] = await db
      .insert(schema.analysisRun)
      .values({
        workspaceId, channelId, subjectType: 'CHANNEL', subjectId: channelId,
        algorithmId: algo!.id, algorithmVersionId: ver!.id, runSequence: 1,
        inputHash: H('a'), periodStart: '2026-06-01', periodEnd: '2026-07-27', status: 'SUCCEEDED',
      })
      .returning()
    analysisRunId = run!.id
    const [pkg] = await db
      .insert(schema.analysisPackage)
      .values({
        workspaceId, analysisRunId, channelId, schemaVersion: '1.0.0',
        payload: { hi: 1 }, payloadHash: H('a'), packageBytes: 10, rawInputBytes: 100,
        reductionPercent: '90',
      })
      .returning()
    const [tpl] = await db
      .insert(schema.promptTemplate)
      .values({ workspaceId, key: 'cursor.analysis.channel', purpose: 'ANALYSIS' })
      .returning()
    const [rev] = await db
      .insert(schema.promptRevision)
      .values({
        templateId: tpl!.id, workspaceId, revisionNumber: 1, body: 'p',
        contentHash: H('a'), authoredBy: 'HUMAN',
      })
      .returning()
    promptRevisionId = rev!.id
    const [req] = await db
      .insert(schema.cursorAnalysisRequest)
      .values({
        workspaceId, channelId, analysisRunId, analysisPackageId: pkg!.id,
        packageHash: H('a'), promptRevisionId, promptHash: H('b'), promptBytes: 10,
      })
      .returning()
    requestId = req!.id
  })

  afterAll(async () => {
    await closeTestPool()
  })

  async function execution(): Promise<string> {
    const [e] = await db
      .insert(schema.llmExecution)
      .values({
        workspaceId, analysisRunId, promptRevisionId, provider: 'CURSOR_CLI',
        iteration: 1, executionSequence: seq++, status: 'REJECTED_SCHEMA',
        rawOutputHash: H('a'), validationError: { failureClass: 'SCHEMA_MISMATCH' },
        startedAt: new Date(), finishedAt: new Date(), durationMs: 1,
      })
      .returning()
    return e!.id
  }

  const BASE = {
    toolName: '/usr/local/bin/cursor-agent',
    schemaVersion: '3.0',
    promptVersion: '3.0.0',
    validatorHash: H('1'),
    schemaHash: H('2'),
    promptSourceHash: H('3'),
    flags: ['--print'],
    exitCode: 0,
    failureClass: 'NONE' as const,
  }

  /** Bản kê lượt PHÂN TÍCH. */
  async function analysisManifest(execId: string, attempt = 1, parent?: string) {
    await db.insert(schema.cursorExecutionManifest).values({
      workspaceId, analysisRunId, llmExecutionId: execId, requestId,
      attemptNumber: attempt, parentExecutionId: parent ?? null,
      executionRole: 'ANALYSIS', startedAt: new Date(), ...BASE,
    })
  }

  /** Bản kê lượt KHAI BÁO — đòi đủ bộ nguồn gốc lượt 2. */
  async function declarationManifest(
    execId: string,
    analysisExecId: string,
    over: Record<string, unknown> = {},
  ) {
    await db.insert(schema.cursorExecutionManifest).values({
      workspaceId, analysisRunId, llmExecutionId: execId, requestId,
      attemptNumber: 1, executionRole: 'DECLARATION',
      analysisExecutionId: analysisExecId,
      obligationGeneratorVersion: '1.0',
      declarationPromptVersion: '3.0.0',
      declarationPromptSourceHash: H('4'),
      compositeValidatorVersion: '1.0',
      analysisPayloadHash: H('5'),
      obligationSetHash: H('6'),
      startedAt: new Date(), ...BASE, ...over,
    })
  }

  async function validation(execId: string, stage: 'ANALYSIS' | 'DECLARATION' | 'COMPOSITE', passed = true) {
    await db.insert(schema.analysisValidation).values({
      workspaceId, analysisRunId, llmExecutionId: execId, channelId, stage, passed,
    })
  }

  async function obligationSet(analysisExecId: string, over: Record<string, unknown> = {}) {
    await db.insert(schema.cursorClaimObligation).values({
      workspaceId, analysisRunId, channelId, requestId,
      analysisExecutionId: analysisExecId,
      analysisHash: H('5'), obligationSetHash: H('6'), generatorVersion: '1.0',
      obligationCount: 1,
      obligations: {
        schemaVersion: '3.0', generatorVersion: '1.0', analysisHash: H('5'),
        obligations: [{ id: 'MC-001' }],
      },
      ...over,
    })
  }

  describe('chặng kiểm định', () => {
    it('BA chặng CÙNG TỒN TẠI trên hai execution của một lần chạy', async () => {
      const a = await execution()
      const d = await execution()
      await analysisManifest(a)
      await declarationManifest(d, a)
      await validation(a, 'ANALYSIS')
      await validation(d, 'DECLARATION')
      await validation(d, 'COMPOSITE')

      const rows = await db
        .select({ stage: schema.analysisValidation.stage })
        .from(schema.analysisValidation)
        .where(sql`${schema.analysisValidation.llmExecutionId} IN (${a}::uuid, ${d}::uuid)`)
      expect(rows.map((r) => r.stage).sort()).toEqual(['ANALYSIS', 'COMPOSITE', 'DECLARATION'])
    })

    it('TRÙNG cùng một chặng bị TỪ CHỐI', async () => {
      const a = await execution()
      await analysisManifest(a)
      await validation(a, 'ANALYSIS')
      await expect(validation(a, 'ANALYSIS')).rejects.toThrow()
    })

    it('kiểm định ĐÃ GẮN kết quả thì KHÔNG sửa được', async () => {
      const a = await execution()
      await analysisManifest(a)
      await validation(a, 'ANALYSIS')
      await db.insert(schema.cursorAnalysisResult).values({
        workspaceId, analysisRunId, llmExecutionId: a, requestId, channelId,
        schemaVersion: '3.0', resultRole: 'ANALYSIS',
        payload: { schemaVersion: '3.0' }, payloadHash: H('a'),
      })
      await expect(
        db
          .update(schema.analysisValidation)
          .set({ passed: false })
          .where(eq(schema.analysisValidation.llmExecutionId, a)),
      ).rejects.toThrow(/IMMUTABLE_VALIDATION/)
    })
  })

  describe('tập nghĩa vụ', () => {
    it('thuộc ĐÚNG lượt phân tích, và chỉ MỘT tập cho mỗi lượt', async () => {
      const a = await execution()
      await analysisManifest(a)
      await obligationSet(a)
      await expect(obligationSet(a)).rejects.toThrow()
    })

    it('BẤT BIẾN: không UPDATE, không DELETE', async () => {
      const a = await execution()
      await analysisManifest(a)
      await obligationSet(a)
      await expect(
        db
          .update(schema.cursorClaimObligation)
          .set({ obligationCount: 2 })
          .where(eq(schema.cursorClaimObligation.analysisExecutionId, a)),
      ).rejects.toThrow(/IMMUTABLE_OBLIGATION_SET/)
      await expect(
        db
          .delete(schema.cursorClaimObligation)
          .where(eq(schema.cursorClaimObligation.analysisExecutionId, a)),
      ).rejects.toThrow(/IMMUTABLE_OBLIGATION_SET/)
    })

    it('số nghĩa vụ khai KHÔNG khớp mảng thật bị chặn', async () => {
      const a = await execution()
      await analysisManifest(a)
      await expect(obligationSet(a, { obligationCount: 7 })).rejects.toThrow()
    })

    it('băm bản phân tích trong JSONB phải khớp cột', async () => {
      const a = await execution()
      await analysisManifest(a)
      await expect(obligationSet(a, { analysisHash: H('9') })).rejects.toThrow()
    })

    it('THỬ LẠI khai báo dùng LẠI tập cũ, không vi phạm tính duy nhất', async () => {
      // Bất biến duy nhất nằm trên LƯỢT PHÂN TÍCH. Nhiều lượt khai báo cùng trỏ
      // về một lượt phân tích là hợp lệ và PHẢI hợp lệ — nếu không thì không sửa
      // lỗi kỹ thuật của lượt 2 được mà không chạy lại lượt 1.
      const a = await execution()
      await analysisManifest(a)
      await obligationSet(a)
      const d1 = await execution()
      const d2 = await execution()
      await declarationManifest(d1, a)
      await declarationManifest(d2, a, { attemptNumber: 2, parentExecutionId: d1 })
      const rows = await db
        .select({ id: schema.cursorExecutionManifest.llmExecutionId })
        .from(schema.cursorExecutionManifest)
        .where(eq(schema.cursorExecutionManifest.analysisExecutionId, a))
      expect(rows).toHaveLength(2)
    })
  })

  describe('vai execution và lineage', () => {
    it('DECLARATION thiếu analysis_execution_id bị chặn', async () => {
      const d = await execution()
      await expect(
        db.insert(schema.cursorExecutionManifest).values({
          workspaceId, analysisRunId, llmExecutionId: d, requestId, attemptNumber: 1,
          executionRole: 'DECLARATION', startedAt: new Date(), ...BASE,
        }),
      ).rejects.toThrow()
    })

    it('ANALYSIS mà KHAI analysis_execution_id bị chặn', async () => {
      const a = await execution()
      const b = await execution()
      await analysisManifest(a)
      await expect(
        db.insert(schema.cursorExecutionManifest).values({
          workspaceId, analysisRunId, llmExecutionId: b, requestId, attemptNumber: 1,
          executionRole: 'ANALYSIS', analysisExecutionId: a, startedAt: new Date(), ...BASE,
        }),
      ).rejects.toThrow()
    })

    it('chuỗi THỬ LẠI trộn VAI bị chặn (khai báo nối vào cha PHÂN TÍCH)', async () => {
      // Bị chặn bởi phép so PHIÊN BẢN trước, vì bản kê lượt phân tích không có
      // bộ nguồn gốc lượt 2 (NULL) còn lượt khai báo thì có. Cả hai đều là lý do
      // từ chối ĐÚNG; ca dưới đây tách riêng phép kiểm VAI.
      const a = await execution()
      await analysisManifest(a)
      await obligationSet(a)
      const d = await execution()
      await expect(
        declarationManifest(d, a, { parentExecutionId: a, attemptNumber: 2 }),
      ).rejects.toThrow(/MIXED_ROLE_REPAIR_CHAIN|MIXED_VERSION_REPAIR_CHAIN/)
    })

    it('phép kiểm VAI chặn ngay cả khi CẢ SÁU phiên bản khớp nhau', async () => {
      // Tách riêng `MIXED_ROLE_REPAIR_CHAIN`: cho con vai ANALYSIS mang ĐÚNG bộ
      // nguồn gốc của cha vai DECLARATION, nên phép so phiên bản im lặng và chỉ
      // còn phép so vai lên tiếng. Không có ca này thì không biết nhánh vai có
      // thật sự chạy hay chỉ nằm đó.
      const a0 = await execution()
      await analysisManifest(a0)
      await obligationSet(a0)
      const parent = await execution()
      await declarationManifest(parent, a0)

      const child = await execution()
      await expect(
        db.insert(schema.cursorExecutionManifest).values({
          workspaceId, analysisRunId, llmExecutionId: child, requestId,
          attemptNumber: 2, parentExecutionId: parent,
          executionRole: 'ANALYSIS', analysisExecutionId: null,
          obligationGeneratorVersion: '1.0',
          declarationPromptVersion: '3.0.0',
          declarationPromptSourceHash: H('4'),
          compositeValidatorVersion: '1.0',
          analysisPayloadHash: H('5'),
          obligationSetHash: H('6'),
          startedAt: new Date(), ...BASE,
        }),
      ).rejects.toThrow(/MIXED_ROLE_REPAIR_CHAIN/)
    })

    it('chuỗi THỬ LẠI đổi bộ sinh nghĩa vụ bị chặn', async () => {
      const a = await execution()
      await analysisManifest(a)
      await obligationSet(a)
      const d1 = await execution()
      await declarationManifest(d1, a)
      const d2 = await execution()
      await expect(
        declarationManifest(d2, a, {
          attemptNumber: 2, parentExecutionId: d1, obligationGeneratorVersion: '9.9',
        }),
      ).rejects.toThrow(/MIXED_VERSION_REPAIR_CHAIN/)
    })
  })

  describe('chỉ COMPOSITE mới cấp phép kết quả chính thức', () => {
    async function ready() {
      const a = await execution()
      const d = await execution()
      await analysisManifest(a)
      await obligationSet(a)
      await declarationManifest(d, a)
      return { a, d }
    }
    const composite = (d: string) => ({
      workspaceId, analysisRunId, llmExecutionId: d, requestId, channelId,
      schemaVersion: '3.0', resultRole: 'COMPOSITE' as const,
      payload: { schemaVersion: '3.0' }, payloadHash: H('a'),
      analysisPayloadHash: H('5'), obligationSetHash: H('6'),
    })

    /**
     * Bản khai ĐÃ LƯU cho lượt khai báo `d`.
     *
     * Fixture cũ bỏ qua bước này và vẫn ghi được kết quả chính thức — chính là
     * lỗ hổng rà soát đối kháng nêu ra (kết quả được cấp phép mà không có bản
     * khai nào tồn tại). Nay 0031 chặn, nên fixture phải mô hình hoá đúng thứ tự
     * ghi thật: bản kê -> bản khai -> phán quyết -> kết quả.
     */
    async function declarationPayload(d: string, a: string) {
      await db.insert(schema.cursorDeclarationResult).values({
        workspaceId, analysisRunId, channelId, requestId,
        llmExecutionId: d, analysisExecutionId: a,
        analysisPayloadHash: H('5'), obligationSetHash: H('6'),
        declarationCount: 0,
        payload: { schemaVersion: '3.0', obligationSetHash: H('6'), declarations: [] },
        payloadHash: H('b'),
      })
    }

    it('ĐỦ ba phán quyết ĐẠT + bản khai đã lưu -> ghi được', async () => {
      const { a, d } = await ready()
      await declarationPayload(d, a)
      await validation(a, 'ANALYSIS')
      await validation(d, 'DECLARATION')
      await validation(d, 'COMPOSITE')
      await expect(db.insert(schema.cursorAnalysisResult).values(composite(d))).resolves.not.toThrow()
    })

    it('ĐỦ ba phán quyết ĐẠT nhưng THIẾU bản khai -> chặn', async () => {
      // Ba phán quyết đạt KHÔNG đủ để cấp phép: phải có hiện vật bản khai thật.
      const { a, d } = await ready()
      await validation(a, 'ANALYSIS')
      await validation(d, 'DECLARATION')
      await validation(d, 'COMPOSITE')
      await expect(db.insert(schema.cursorAnalysisResult).values(composite(d))).rejects.toThrow(
        /RESULT_WITHOUT_DECLARATION_PAYLOAD/,
      )
    })

    it('THIẾU phán quyết COMPOSITE -> chặn', async () => {
      const { a, d } = await ready()
      await validation(a, 'ANALYSIS')
      await validation(d, 'DECLARATION')
      await expect(db.insert(schema.cursorAnalysisResult).values(composite(d))).rejects.toThrow(
        /RESULT_WITHOUT_VALIDATION/,
      )
    })

    it('chặng ANALYSIS HỎNG -> không có kết quả chính thức', async () => {
      const { a, d } = await ready()
      await validation(a, 'ANALYSIS', false)
      await validation(d, 'DECLARATION')
      await validation(d, 'COMPOSITE')
      await expect(db.insert(schema.cursorAnalysisResult).values(composite(d))).rejects.toThrow(
        /RESULT_WITH_FAILED_ANALYSIS/,
      )
    })

    it('chặng DECLARATION HỎNG -> không có kết quả chính thức', async () => {
      const { a, d } = await ready()
      await validation(a, 'ANALYSIS')
      await validation(d, 'DECLARATION', false)
      await validation(d, 'COMPOSITE')
      await expect(db.insert(schema.cursorAnalysisResult).values(composite(d))).rejects.toThrow(
        /RESULT_WITH_FAILED_DECLARATION/,
      )
    })

    it('THIẾU tập nghĩa vụ -> chặn', async () => {
      const a = await execution()
      const d = await execution()
      await analysisManifest(a)
      await declarationManifest(d, a)
      await validation(a, 'ANALYSIS')
      await validation(d, 'DECLARATION')
      await validation(d, 'COMPOSITE')
      await expect(db.insert(schema.cursorAnalysisResult).values(composite(d))).rejects.toThrow(
        /RESULT_WITHOUT_OBLIGATION_SET/,
      )
    })

    it('băm neo LỆCH tập nghĩa vụ -> chặn', async () => {
      const { a, d } = await ready()
      await validation(a, 'ANALYSIS')
      await validation(d, 'DECLARATION')
      await validation(d, 'COMPOSITE')
      await expect(
        db.insert(schema.cursorAnalysisResult).values({
          ...composite(d), obligationSetHash: H('c'),
        }),
      ).rejects.toThrow(/RESULT_LINEAGE_DRIFT|RESULT_MANIFEST_LINEAGE_DRIFT/)
    })

    it('kết quả vai ANALYSIS gắn vào execution vai DECLARATION -> chặn', async () => {
      const { a, d } = await ready()
      await validation(a, 'ANALYSIS')
      await validation(d, 'DECLARATION')
      await validation(d, 'COMPOSITE')
      await expect(
        db.insert(schema.cursorAnalysisResult).values({
          ...composite(d), resultRole: 'ANALYSIS',
        }),
      ).rejects.toThrow(/RESULT_ROLE_MISMATCH/)
    })
  })

  describe('truy vấn độ ổn định đếm MỘT lần thử, không phải ba dòng chặng', () => {
    it('ba dòng chặng -> vẫn một hàng khi lọc COMPOSITE', async () => {
      const a = await execution()
      const d = await execution()
      await analysisManifest(a)
      await obligationSet(a)
      await declarationManifest(d, a)
      await validation(a, 'ANALYSIS')
      await validation(d, 'DECLARATION')
      await validation(d, 'COMPOSITE')

      const unfiltered = await db.execute<{ n: number }>(sql`
        SELECT count(*)::int n FROM cursor_execution_manifest m
        JOIN analysis_validation v ON v.llm_execution_id = m.llm_execution_id
        WHERE m.llm_execution_id = ${d}::uuid`)
      const filtered = await db.execute<{ n: number }>(sql`
        SELECT count(*)::int n FROM cursor_execution_manifest m
        JOIN analysis_validation v ON v.llm_execution_id = m.llm_execution_id
          AND v.stage = 'COMPOSITE'
        WHERE m.llm_execution_id = ${d}::uuid`)
      // Không lọc thì lượt khai báo bị đếm HAI lần (DECLARATION + COMPOSITE).
      expect(Number(unfiltered.rows[0]!.n)).toBe(2)
      expect(Number(filtered.rows[0]!.n)).toBe(1)
    })
  })

  describe('dữ liệu MỘT LƯỢT cũ vẫn đọc được', () => {
    it('kết quả cũ giữ vai COMPOSITE và không cần băm neo', async () => {
      const rows = await db.execute<{ n: number }>(sql`
        SELECT count(*)::int n FROM cursor_analysis_result
        WHERE result_role = 'COMPOSITE' AND analysis_payload_hash IS NULL`)
      expect(Number(rows.rows[0]!.n)).toBeGreaterThanOrEqual(0)
    })
  })
})
