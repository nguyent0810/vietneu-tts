import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'
import { eq, sql } from 'drizzle-orm'

import {
  algorithm,
  algorithmVersion,
  analysisResult,
  analysisRun,
  approval,
  auditEvent,
  channel,
  contentItem,
  contentRevision,
  critique,
  llmExecution,
  promptRevision,
  promptTemplate,
  video,
  workspace,
} from '@/db/schema'
import { closeTestPool, hasTestDatabase, testDb, truncateAll } from '../helpers/db'

const HASH_A = 'a'.repeat(64)
const HASH_B = 'b'.repeat(64)

/** Bắt lỗi Postgres và trả về {code, constraint} để assert chính xác. */
async function expectDbError(fn: () => Promise<unknown>): Promise<{ code?: string; constraint?: string; message: string }> {
  try {
    await fn()
  } catch (err) {
    const e = err as { code?: string; constraint?: string; message?: string }
    return { code: e.code, constraint: e.constraint, message: e.message ?? '' }
  }
  throw new Error('Kỳ vọng database từ chối thao tác này, nhưng nó đã thành công.')
}

describe.skipIf(!hasTestDatabase)('schema invariants (PostgreSQL thật)', () => {
  const db = testDb()

  let workspaceId: string
  let channelId: string
  let algorithmId: string
  let versionId: string
  let sentinelVersionId: string

  beforeAll(async () => {
    await truncateAll()
  })

  afterAll(async () => {
    await closeTestPool()
  })

  beforeEach(async () => {
    await truncateAll()

    const [ws] = await db
      .insert(workspace)
      .values({ slug: 'test-ws', name: 'Test Workspace' })
      .returning()
    workspaceId = ws!.id

    const [ch] = await db
      .insert(channel)
      .values({
        workspaceId,
        label: 'phong_thuy',
        youtubeChannelId: 'UCtest0000000000000000',
        title: 'Test Channel',
      })
      .returning()
    channelId = ch!.id

    const [algo] = await db
      .insert(algorithm)
      .values({ key: 'deterministic-analysis', name: 'Deterministic', kind: 'DETERMINISTIC' })
      .returning()
    algorithmId = algo!.id

    const versions = await db
      .insert(algorithmVersion)
      .values([
        { algorithmId, version: '1.0.0' },
        // Sentinel cho audit do người/công cụ ngoài chạy -- xem AC-3.
        { algorithmId, version: 'external-human' },
      ])
      .returning()
    versionId = versions[0]!.id
    sentinelVersionId = versions[1]!.id
  })

  // --- AC-3 -----------------------------------------------------------------

  describe('AC-3: run_sequence không bị NULL làm vô hiệu', () => {
    async function insertRun(seq: number, algorithmVersionId: string) {
      return db.insert(analysisRun).values({
        workspaceId,
        channelId,
        subjectType: 'CHANNEL',
        subjectId: channelId,
        algorithmId,
        algorithmVersionId,
        runSequence: seq,
        inputHash: HASH_A,
        periodStart: '2026-01-01',
        periodEnd: '2026-01-31',
      })
    }

    it('từ chối hai run trùng run_sequence với version thường', async () => {
      await insertRun(1, versionId)
      const err = await expectDbError(() => insertRun(1, versionId))
      expect(err.code).toBe('23505')
      expect(err.constraint).toBe('analysis_run_sequence_key')
    })

    it('từ chối hai run trùng run_sequence với version SENTINEL (nhánh từng dùng NULL)', async () => {
      // Đây chính là ca mà thiết kế cũ (algorithm_version_id nullable) sẽ CHO
      // QUA, vì PostgreSQL coi mọi NULL là khác nhau trong UNIQUE.
      await insertRun(1, sentinelVersionId)
      const err = await expectDbError(() => insertRun(1, sentinelVersionId))
      expect(err.code).toBe('23505')
      expect(err.constraint).toBe('analysis_run_sequence_key')
    })

    it('cho phép cùng run_sequence khi khác phiên bản thuật toán', async () => {
      await insertRun(1, versionId)
      await expect(insertRun(1, sentinelVersionId)).resolves.toBeDefined()
    })

    it('bắt buộc subject_type và content_revision_id nhất quán', async () => {
      const err = await expectDbError(() =>
        db.insert(analysisRun).values({
          workspaceId,
          channelId,
          subjectType: 'CONTENT_REVISION',
          subjectId: channelId,
          contentRevisionId: null, // mâu thuẫn với subjectType
          algorithmId,
          algorithmVersionId: versionId,
          runSequence: 1,
          inputHash: HASH_A,
          periodStart: '2026-01-01',
          periodEnd: '2026-01-31',
        }),
      )
      expect(err.constraint).toBe('analysis_run_subject_consistency')
    })
  })

  // --- Bất biến -------------------------------------------------------------

  describe('bất biến cưỡng chế ở tầng DB', () => {
    async function makeFrozenRevision() {
      const [item] = await db
        .insert(contentItem)
        .values({ workspaceId, channelId, kind: 'LONG_FORM', title: 'T' })
        .returning()
      const [rev] = await db
        .insert(contentRevision)
        .values({
          contentItemId: item!.id,
          workspaceId,
          revisionNumber: 1,
          state: 'FROZEN',
          audioScript: 'kịch bản',
          contentHash: HASH_A,
          frozenAt: new Date(),
        })
        .returning()
      return rev!
    }

    it('không cho UPDATE content_revision đã FROZEN', async () => {
      const rev = await makeFrozenRevision()
      const err = await expectDbError(() =>
        db.update(contentRevision).set({ audioScript: 'sửa lén' }).where(eq(contentRevision.id, rev.id)),
      )
      expect(err.message).toContain('IMMUTABLE_CONTENT_REVISION')
    })

    it('không cho xoá lẻ content_revision đã FROZEN', async () => {
      const rev = await makeFrozenRevision()
      const err = await expectDbError(() =>
        db.delete(contentRevision).where(eq(contentRevision.id, rev.id)),
      )
      expect(err.message).toContain('IMMUTABLE_CONTENT_REVISION')
    })

    it('cho phép sửa revision còn DRAFT rồi đóng băng đúng một lần', async () => {
      const [item] = await db
        .insert(contentItem)
        .values({ workspaceId, channelId, kind: 'SHORT', title: 'T2' })
        .returning()
      const [rev] = await db
        .insert(contentRevision)
        .values({
          contentItemId: item!.id,
          workspaceId,
          revisionNumber: 1,
          audioScript: 'bản nháp',
          contentHash: HASH_A,
        })
        .returning()

      await db
        .update(contentRevision)
        .set({ audioScript: 'sửa khi còn nháp' })
        .where(eq(contentRevision.id, rev!.id))

      await db
        .update(contentRevision)
        .set({ state: 'FROZEN', frozenAt: new Date(), contentHash: HASH_B })
        .where(eq(contentRevision.id, rev!.id))

      const err = await expectDbError(() =>
        db.update(contentRevision).set({ audioScript: 'sau khi đóng băng' }).where(eq(contentRevision.id, rev!.id)),
      )
      expect(err.message).toContain('IMMUTABLE_CONTENT_REVISION')
    })

    it('bắt buộc state FROZEN đi kèm frozen_at', async () => {
      const [item] = await db
        .insert(contentItem)
        .values({ workspaceId, channelId, kind: 'SHORT', title: 'T3' })
        .returning()
      const err = await expectDbError(() =>
        db.insert(contentRevision).values({
          contentItemId: item!.id,
          workspaceId,
          revisionNumber: 1,
          state: 'FROZEN',
          frozenAt: null,
          audioScript: 'x',
          contentHash: HASH_A,
        }),
      )
      expect(err.constraint).toBe('content_revision_frozen_consistency')
    })

    it('prompt_revision là bất biến ngay từ khi tạo', async () => {
      const [tpl] = await db
        .insert(promptTemplate)
        .values({ workspaceId, key: 'cursor.analysis', purpose: 'ANALYSIS' })
        .returning()
      const [rev] = await db
        .insert(promptRevision)
        .values({
          templateId: tpl!.id,
          workspaceId,
          revisionNumber: 1,
          body: 'prompt gốc',
          contentHash: HASH_A,
          authoredBy: 'HUMAN',
        })
        .returning()

      const err = await expectDbError(() =>
        db.update(promptRevision).set({ body: 'sửa' }).where(eq(promptRevision.id, rev!.id)),
      )
      expect(err.message).toContain('IMMUTABLE_PROMPT_REVISION')
    })

    it('audit_event là append-only', async () => {
      const [ev] = await db
        .insert(auditEvent)
        .values({
          workspaceId,
          actorType: 'USER',
          actorId: 'u1',
          action: 'TEST',
          entityType: 'content_item',
        })
        .returning()

      const updateErr = await expectDbError(() =>
        db.update(auditEvent).set({ action: 'ĐỔI' }).where(eq(auditEvent.id, ev!.id)),
      )
      expect(updateErr.message).toContain('IMMUTABLE_AUDIT_EVENT')

      const deleteErr = await expectDbError(() =>
        db.delete(auditEvent).where(eq(auditEvent.id, ev!.id)),
      )
      expect(deleteErr.message).toContain('IMMUTABLE_AUDIT_EVENT')
    })

    it('analysis_result là bất biến', async () => {
      const [run] = await db
        .insert(analysisRun)
        .values({
          workspaceId,
          channelId,
          subjectType: 'CHANNEL',
          subjectId: channelId,
          algorithmId,
          algorithmVersionId: versionId,
          runSequence: 1,
          inputHash: HASH_A,
          periodStart: '2026-01-01',
          periodEnd: '2026-01-31',
        })
        .returning()
      const [res] = await db
        .insert(analysisResult)
        .values({
          analysisRunId: run!.id,
          kind: 'DETERMINISTIC_EVIDENCE',
          schemaVersion: '1.0.0',
          payload: { observations: [] },
          payloadHash: HASH_A,
        })
        .returning()

      const err = await expectDbError(() =>
        db.update(analysisResult).set({ payload: { observations: ['sửa'] } }).where(eq(analysisResult.id, res!.id)),
      )
      expect(err.message).toContain('IMMUTABLE_ANALYSIS_RESULT')
    })
  })

  // --- Đường vòng xoá dữ liệu bất biến ---------------------------------------

  describe('không có đường vòng nào xoá được dữ liệu bất biến', () => {
    it('xoá content_item cha KHÔNG quét được revision đã FROZEN', async () => {
      // Regression: bản đầu dùng ON DELETE CASCADE + trigger có
      // `WHEN (pg_trigger_depth() = 0)`, nên chỉ cần xoá item cha là xoá sạch
      // mọi revision FROZEN — đúng thứ trigger sinh ra để ngăn.
      const [item] = await db
        .insert(contentItem)
        .values({ workspaceId, channelId, kind: 'LONG_FORM', title: 'có lịch sử' })
        .returning()
      await db.insert(contentRevision).values({
        contentItemId: item!.id,
        workspaceId,
        revisionNumber: 1,
        state: 'FROZEN',
        audioScript: 'kịch bản',
        contentHash: HASH_A,
        frozenAt: new Date(),
      })

      const err = await expectDbError(() => db.delete(contentItem).where(eq(contentItem.id, item!.id)))
      expect(err.code).toBe('23503') // FK restrict, không phải cascade

      const survivors = await db
        .select()
        .from(contentRevision)
        .where(eq(contentRevision.contentItemId, item!.id))
      expect(survivors).toHaveLength(1)
    })

    it('không cho XOÁ prompt_revision', async () => {
      const [tpl] = await db
        .insert(promptTemplate)
        .values({ workspaceId, key: 'cursor.analysis', purpose: 'ANALYSIS' })
        .returning()
      const [rev] = await db
        .insert(promptRevision)
        .values({
          templateId: tpl!.id,
          workspaceId,
          revisionNumber: 1,
          body: 'prompt gốc',
          contentHash: HASH_A,
          authoredBy: 'HUMAN',
        })
        .returning()

      const err = await expectDbError(() =>
        db.delete(promptRevision).where(eq(promptRevision.id, rev!.id)),
      )
      expect(err.message).toContain('IMMUTABLE_PROMPT_REVISION')
    })

    it('không cho XOÁ analysis_result, và không xoá được run của nó', async () => {
      const [run] = await db
        .insert(analysisRun)
        .values({
          workspaceId,
          channelId,
          subjectType: 'CHANNEL',
          subjectId: channelId,
          algorithmId,
          algorithmVersionId: versionId,
          runSequence: 1,
          inputHash: HASH_A,
          periodStart: '2026-01-01',
          periodEnd: '2026-01-31',
        })
        .returning()
      const [res] = await db
        .insert(analysisResult)
        .values({
          analysisRunId: run!.id,
          kind: 'DETERMINISTIC_EVIDENCE',
          schemaVersion: '1.0.0',
          payload: { observations: [] },
          payloadHash: HASH_A,
        })
        .returning()

      const directErr = await expectDbError(() =>
        db.delete(analysisResult).where(eq(analysisResult.id, res!.id)),
      )
      expect(directErr.message).toContain('IMMUTABLE_ANALYSIS_RESULT')

      // Đường vòng: xoá run cha. Trước đây là ON DELETE CASCADE nên sẽ quét
      // luôn kết quả mà không chạm trigger.
      const cascadeErr = await expectDbError(() =>
        db.delete(analysisRun).where(eq(analysisRun.id, run!.id)),
      )
      expect(cascadeErr.code).toBe('23503')

      const survivors = await db.select().from(analysisResult).where(eq(analysisResult.id, res!.id))
      expect(survivors).toHaveLength(1)
    })
  })

  // --- Cách ly workspace ------------------------------------------------------

  describe('khoá ngoại ghép chặn dữ liệu lẫn giữa các workspace', () => {
    async function makeOtherWorkspaceChannel() {
      const [other] = await db
        .insert(workspace)
        .values({ slug: 'other-ws', name: 'Workspace khác' })
        .returning()
      const [otherCh] = await db
        .insert(channel)
        .values({
          workspaceId: other!.id,
          label: 'hinh_su',
          youtubeChannelId: 'UCother00000000000000x',
          title: 'Kênh workspace khác',
        })
        .returning()
      return { otherWorkspaceId: other!.id, otherChannelId: otherCh!.id }
    }

    it('content_item không thể khai workspace A mà trỏ kênh của workspace B', async () => {
      const { otherChannelId } = await makeOtherWorkspaceChannel()
      const err = await expectDbError(() =>
        db.insert(contentItem).values({
          workspaceId, // workspace A
          channelId: otherChannelId, // kênh của workspace B
          kind: 'LONG_FORM',
          title: 'lẫn workspace',
        }),
      )
      expect(err.code).toBe('23503')
      expect(err.constraint).toBe('content_item_channel_workspace_fk')
    })

    it('analysis_run không thể khai workspace A mà trỏ kênh của workspace B', async () => {
      const { otherChannelId } = await makeOtherWorkspaceChannel()
      const err = await expectDbError(() =>
        db.insert(analysisRun).values({
          workspaceId,
          channelId: otherChannelId,
          subjectType: 'CHANNEL',
          subjectId: otherChannelId,
          algorithmId,
          algorithmVersionId: versionId,
          runSequence: 1,
          inputHash: HASH_A,
          periodStart: '2026-01-01',
          periodEnd: '2026-01-31',
        }),
      )
      expect(err.code).toBe('23503')
      expect(err.constraint).toBe('analysis_run_channel_workspace_fk')
    })

    it('content_revision không thể lệch workspace so với content_item cha', async () => {
      const { otherWorkspaceId } = await makeOtherWorkspaceChannel()
      const [item] = await db
        .insert(contentItem)
        .values({ workspaceId, channelId, kind: 'SHORT', title: 'T' })
        .returning()

      const err = await expectDbError(() =>
        db.insert(contentRevision).values({
          contentItemId: item!.id,
          workspaceId: otherWorkspaceId, // lệch so với item cha
          revisionNumber: 1,
          audioScript: 'x',
          contentHash: HASH_A,
        }),
      )
      expect(err.code).toBe('23503')
      expect(err.constraint).toBe('content_revision_item_workspace_fk')
    })

    it('analysis_run không thể trỏ revision của workspace khác', async () => {
      const { otherWorkspaceId, otherChannelId } = await makeOtherWorkspaceChannel()
      const [otherItem] = await db
        .insert(contentItem)
        .values({
          workspaceId: otherWorkspaceId,
          channelId: otherChannelId,
          kind: 'SHORT',
          title: 'của workspace khác',
        })
        .returning()
      const [otherRev] = await db
        .insert(contentRevision)
        .values({
          contentItemId: otherItem!.id,
          workspaceId: otherWorkspaceId,
          revisionNumber: 1,
          audioScript: 'x',
          contentHash: HASH_A,
        })
        .returning()

      const err = await expectDbError(() =>
        db.insert(analysisRun).values({
          workspaceId, // workspace A
          channelId,
          subjectType: 'CONTENT_REVISION',
          subjectId: otherRev!.id,
          contentRevisionId: otherRev!.id, // revision của workspace B
          algorithmId,
          algorithmVersionId: versionId,
          runSequence: 1,
          inputHash: HASH_A,
          periodStart: '2026-01-01',
          periodEnd: '2026-01-31',
        }),
      )
      expect(err.code).toBe('23503')
      expect(err.constraint).toBe('analysis_run_revision_workspace_fk')
    })
  })

  // --- Nguồn gốc dữ liệu của llm_execution ------------------------------------

  describe('llm_execution không thể nhận vơ prompt/kết quả của nơi khác', () => {
    async function makeRun(seq = 1) {
      const [run] = await db
        .insert(analysisRun)
        .values({
          workspaceId,
          channelId,
          subjectType: 'CHANNEL',
          subjectId: channelId,
          algorithmId,
          algorithmVersionId: versionId,
          runSequence: seq,
          inputHash: HASH_A,
          periodStart: '2026-01-01',
          periodEnd: '2026-01-31',
        })
        .returning()
      return run!
    }

    async function makePromptRevision(wsId: string) {
      const [tpl] = await db
        .insert(promptTemplate)
        .values({ workspaceId: wsId, key: `k-${Math.random()}`, purpose: 'ANALYSIS' })
        .returning()
      const [rev] = await db
        .insert(promptRevision)
        .values({
          templateId: tpl!.id,
          workspaceId: wsId,
          revisionNumber: 1,
          body: 'prompt',
          contentHash: HASH_A,
          authoredBy: 'HUMAN',
        })
        .returning()
      return rev!
    }

    it('prompt_revision không thể lệch workspace so với template cha', async () => {
      const [other] = await db
        .insert(workspace)
        .values({ slug: 'ws-prompt', name: 'khác' })
        .returning()
      const [tpl] = await db
        .insert(promptTemplate)
        .values({ workspaceId, key: 'k1', purpose: 'ANALYSIS' })
        .returning()

      const err = await expectDbError(() =>
        db.insert(promptRevision).values({
          templateId: tpl!.id,
          workspaceId: other!.id, // lệch so với template
          revisionNumber: 1,
          body: 'x',
          contentHash: HASH_A,
          authoredBy: 'HUMAN',
        }),
      )
      expect(err.constraint).toBe('prompt_revision_template_workspace_fk')
    })

    it('execution không thể dùng prompt của workspace khác', async () => {
      const run = await makeRun()
      const [other] = await db
        .insert(workspace)
        .values({ slug: 'ws-exec', name: 'khác' })
        .returning()
      const foreignPrompt = await makePromptRevision(other!.id)

      const err = await expectDbError(() =>
        db.insert(llmExecution).values({
          workspaceId,
          analysisRunId: run.id,
          promptRevisionId: foreignPrompt.id,
          provider: 'CURSOR_CLI',
        }),
      )
      expect(err.constraint).toBe('llm_execution_prompt_workspace_fk')
    })

    it('execution không thể nhận kết quả thuộc run KHÁC', async () => {
      const runA = await makeRun(1)
      const runB = await makeRun(2)
      const prompt = await makePromptRevision(workspaceId)

      // Kết quả này thuộc runB.
      const [resultB] = await db
        .insert(analysisResult)
        .values({
          analysisRunId: runB.id,
          kind: 'LLM_ANALYSIS',
          schemaVersion: '1.0.0',
          payload: {},
          payloadHash: HASH_A,
        })
        .returning()

      // Execution thuộc runA nhưng khai kết quả của runB.
      const err = await expectDbError(() =>
        db.insert(llmExecution).values({
          workspaceId,
          analysisRunId: runA.id,
          promptRevisionId: prompt.id,
          provider: 'CURSOR_CLI',
          status: 'SUCCEEDED',
          analysisResultId: resultB!.id,
        }),
      )
      expect(err.constraint).toBe('llm_execution_result_run_fk')
    })

    it('chấp nhận execution có prompt và kết quả đúng chỗ', async () => {
      const run = await makeRun()
      const prompt = await makePromptRevision(workspaceId)
      const [result] = await db
        .insert(analysisResult)
        .values({
          analysisRunId: run.id,
          kind: 'LLM_ANALYSIS',
          schemaVersion: '1.0.0',
          payload: {},
          payloadHash: HASH_A,
        })
        .returning()

      await expect(
        db.insert(llmExecution).values({
          workspaceId,
          analysisRunId: run.id,
          promptRevisionId: prompt.id,
          provider: 'CURSOR_CLI',
          status: 'SUCCEEDED',
          analysisResultId: result!.id,
        }),
      ).resolves.toBeDefined()
    })

    it('critique không thể khai sai prompt mà execution đã dùng', async () => {
      const run = await makeRun()
      const usedPrompt = await makePromptRevision(workspaceId)
      const otherPrompt = await makePromptRevision(workspaceId) // cùng workspace!

      const [exec] = await db
        .insert(llmExecution)
        .values({
          workspaceId,
          analysisRunId: run.id,
          promptRevisionId: usedPrompt.id,
          provider: 'CURSOR_CLI',
        })
        .returning()

      // Ràng buộc theo workspace là KHÔNG ĐỦ: otherPrompt cùng workspace nên sẽ
      // lọt. Chỉ khoá ngoại ghép (execution, prompt) mới chặn được.
      const err = await expectDbError(() =>
        db.insert(critique).values({
          workspaceId,
          llmExecutionId: exec!.id,
          critiquedPromptRevisionId: otherPrompt.id,
        }),
      )
      expect(err.constraint).toBe('critique_execution_prompt_fk')

      // Đúng prompt thì chấp nhận, và vẫn đề xuất được một bản prompt MỚI.
      const proposed = await makePromptRevision(workspaceId)
      await expect(
        db.insert(critique).values({
          workspaceId,
          llmExecutionId: exec!.id,
          critiquedPromptRevisionId: usedPrompt.id,
          proposedPromptRevisionId: proposed.id,
        }),
      ).resolves.toBeDefined()
    })

    it('cưỡng chế giới hạn 3 vòng tinh chỉnh ở tầng DB', async () => {
      const run = await makeRun()
      const prompt = await makePromptRevision(workspaceId)
      const err = await expectDbError(() =>
        db.insert(llmExecution).values({
          workspaceId,
          analysisRunId: run.id,
          promptRevisionId: prompt.id,
          provider: 'CURSOR_CLI',
          iteration: 4,
        }),
      )
      expect(err.constraint).toBe('llm_execution_iteration_bounds')
    })
  })

  // --- Phê duyệt ------------------------------------------------------------

  describe('agent/worker không được phê duyệt', () => {
    it('từ chối phê duyệt bởi AGENT ở tầng DB', async () => {
      const err = await expectDbError(() =>
        db.insert(approval).values({
          workspaceId,
          entityType: 'content_revision',
          entityId: channelId,
          state: 'APPROVED',
          decidedByType: 'AGENT',
          decidedById: 'claude',
          decidedAt: new Date(),
        }),
      )
      expect(err.constraint).toBe('approval_decider_must_be_human')
    })

    it('từ chối phê duyệt bởi WORKER ở tầng DB', async () => {
      const err = await expectDbError(() =>
        db.insert(approval).values({
          workspaceId,
          entityType: 'content_revision',
          entityId: channelId,
          state: 'APPROVED',
          decidedByType: 'WORKER',
          decidedById: 'mac-mini',
          decidedAt: new Date(),
        }),
      )
      expect(err.constraint).toBe('approval_decider_must_be_human')
    })

    it('cho phép phê duyệt bởi USER', async () => {
      await expect(
        db.insert(approval).values({
          workspaceId,
          entityType: 'content_revision',
          entityId: channelId,
          state: 'APPROVED',
          decidedByType: 'USER',
          decidedById: 'kliment',
          decidedAt: new Date(),
        }),
      ).resolves.toBeDefined()
    })

    it('bắt buộc PENDING thì chưa có thông tin quyết định', async () => {
      const err = await expectDbError(() =>
        db.insert(approval).values({
          workspaceId,
          entityType: 'content_revision',
          entityId: channelId,
          state: 'PENDING',
          decidedByType: 'USER',
          decidedById: 'kliment',
          decidedAt: new Date(),
        }),
      )
      expect(err.constraint).toBe('approval_decision_consistency')
    })
  })

  // --- AC-5 -----------------------------------------------------------------

  describe('AC-5: published_video_id — nullable ở 0000, có FK từ 0002', () => {
    it('vẫn nhận NULL khi nội dung chưa xuất bản', async () => {
      const [item] = await db
        .insert(contentItem)
        .values({ workspaceId, channelId, kind: 'LONG_FORM', title: 'chưa xuất bản' })
        .returning()
      expect(item!.publishedVideoId).toBeNull()
    })

    it('FK đã được thêm và CƯỠNG CHẾ: không trỏ được tới video không tồn tại', async () => {
      // Ở Phase 1 giá trị tự do được chấp nhận vì chưa có bảng `video`. Phase 2
      // tạo bảng đó và thêm FK, nên từ đây một ID bịa sẽ bị DB từ chối.
      const err = await expectDbError(() =>
        db.insert(contentItem).values({
          workspaceId,
          channelId,
          kind: 'LONG_FORM',
          title: 'video không tồn tại',
          publishedVideoId: 'dQw4w9WgXcQ',
        }),
      )
      expect(err.code).toBe('23503')
    })

    it('chấp nhận khi video có thật', async () => {
      await db.insert(video).values({
        workspaceId,
        channelId,
        youtubeVideoId: 'dQw4w9WgXcQ',
        title: 'video thật',
        publishedAt: new Date('2026-07-01T00:00:00Z'),
      })

      const [linked] = await db
        .insert(contentItem)
        .values({
          workspaceId,
          channelId,
          kind: 'LONG_FORM',
          title: 'đã xuất bản',
          publishedVideoId: 'dQw4w9WgXcQ',
        })
        .returning()
      expect(linked!.publishedVideoId).toBe('dQw4w9WgXcQ')
    })
  })

  // --- Ràng buộc định dạng --------------------------------------------------

  describe('ràng buộc định dạng', () => {
    it('từ chối content_hash không phải sha256 hex', async () => {
      const [item] = await db
        .insert(contentItem)
        .values({ workspaceId, channelId, kind: 'SHORT', title: 'T' })
        .returning()
      const err = await expectDbError(() =>
        db.insert(contentRevision).values({
          contentItemId: item!.id,
          workspaceId,
          revisionNumber: 1,
          audioScript: 'x',
          contentHash: 'không-phải-hash',
        }),
      )
      expect(err.constraint).toBe('content_revision_hash_format')
    })

    it('từ chối label kênh sai định dạng', async () => {
      const err = await expectDbError(() =>
        db.insert(channel).values({
          workspaceId,
          label: 'Phong Thuy!',
          youtubeChannelId: 'UCother000000000000000',
          title: 'x',
        }),
      )
      expect(err.constraint).toBe('channel_label_format')
    })

    it('từ chối khoảng thời gian phân tích đảo ngược', async () => {
      const err = await expectDbError(() =>
        db.insert(analysisRun).values({
          workspaceId,
          channelId,
          subjectType: 'CHANNEL',
          subjectId: channelId,
          algorithmId,
          algorithmVersionId: versionId,
          runSequence: 1,
          inputHash: HASH_A,
          periodStart: '2026-01-31',
          periodEnd: '2026-01-01',
        }),
      )
      expect(err.constraint).toBe('analysis_run_period_order')
    })
  })
})
