import { afterAll, beforeAll, describe, expect, it } from 'vitest'
import { eq, sql } from 'drizzle-orm'

import * as schema from '@/db/schema'
import { closeTestPool, hasTestDatabase, testDb, truncateAll } from '../helpers/db'

/**
 * Lưu trữ và nguồn gốc của tầng Cursor, trên PostgreSQL THẬT.
 *
 * Không gọi Cursor thật ở đây — các bất biến cần kiểm là của DATABASE (bất
 * biến, cách ly workspace, chuỗi retry), và chúng phải đúng bất kể output đến
 * từ đâu. Cursor thật được kiểm ở lần chạy 3 kênh.
 */
describe.skipIf(!hasTestDatabase)('lưu trữ tầng Cursor (PostgreSQL thật)', () => {
  const db = testDb()
  let workspaceId: string
  let otherWorkspaceId: string
  let channelId: string
  let analysisRunId: string
  let packageId: string
  let promptRevisionId: string
  let requestId: string

  const HASH_A = 'a'.repeat(64)
  const HASH_B = 'b'.repeat(64)

  beforeAll(async () => {
    await truncateAll()
    await db.execute(sql`TRUNCATE TABLE cursor_analysis_result, cursor_execution_manifest,
      analysis_validation, cursor_analysis_request, analysis_package, analysis_quality, anomaly,
      cohort_summary, evidence_reference, deterministic_observation, feature_value,
      feature_version, feature_definition, video_daily_metric_history, video_daily_metric,
      channel_daily_metric, video CASCADE`)

    const [ws] = await db.insert(schema.workspace).values({ slug: 'ws-c', name: 'W' }).returning()
    workspaceId = ws!.id
    const [ws2] = await db.insert(schema.workspace).values({ slug: 'ws-other', name: 'O' }).returning()
    otherWorkspaceId = ws2!.id

    const [ch] = await db
      .insert(schema.channel)
      .values({ workspaceId, label: 'phong_thuy', youtubeChannelId: 'UCcursor00000000000000', title: 'T' })
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
        workspaceId,
        channelId,
        subjectType: 'CHANNEL',
        subjectId: channelId,
        algorithmId: algo!.id,
        algorithmVersionId: ver!.id,
        runSequence: 1,
        inputHash: HASH_A,
        periodStart: '2026-06-01',
        periodEnd: '2026-07-27',
        status: 'SUCCEEDED',
      })
      .returning()
    analysisRunId = run!.id

    const [pkg] = await db
      .insert(schema.analysisPackage)
      .values({
        workspaceId,
        analysisRunId,
        channelId,
        schemaVersion: '1.0.0',
        payload: { hello: 'world' },
        payloadHash: HASH_A,
        packageBytes: 100,
        rawInputBytes: 1000,
        reductionPercent: '90',
      })
      .returning()
    packageId = pkg!.id

    const [tpl] = await db
      .insert(schema.promptTemplate)
      .values({ workspaceId, key: 'cursor.analysis.channel', purpose: 'ANALYSIS' })
      .returning()
    const [rev] = await db
      .insert(schema.promptRevision)
      .values({
        templateId: tpl!.id,
        workspaceId,
        revisionNumber: 1,
        body: 'prompt',
        contentHash: HASH_A,
        authoredBy: 'HUMAN',
      })
      .returning()
    promptRevisionId = rev!.id

    const [req] = await db
      .insert(schema.cursorAnalysisRequest)
      .values({
        workspaceId,
        channelId,
        analysisRunId,
        analysisPackageId: packageId,
        packageHash: HASH_A,
        promptRevisionId,
        promptHash: HASH_B,
        promptBytes: 1234,
      })
      .returning()
    requestId = req!.id
  })

  afterAll(async () => {
    await closeTestPool()
  })

  async function makeExecution(seq: number, status: 'SUCCEEDED' | 'REJECTED_SCHEMA' = 'REJECTED_SCHEMA') {
    const [exe] = await db
      .insert(schema.llmExecution)
      .values({
        workspaceId,
        analysisRunId,
        promptRevisionId,
        provider: 'CURSOR_CLI',
        iteration: 1,
        executionSequence: seq,
        status: status === 'SUCCEEDED' ? 'RUNNING' : status,
        rawOutputHash: HASH_A,
        validationError: status === 'REJECTED_SCHEMA' ? { failureClass: 'SCHEMA_MISMATCH' } : null,
        startedAt: new Date(),
        finishedAt: new Date(),
        durationMs: 1000,
      })
      .returning()
    return exe!.id
  }

  /**
   * Execution KÈM bản kê — dùng cho các test có ghi kết quả.
   *
   * Trigger `cursor_result_semantic_lineage` đòi bản kê phải tồn tại trước kết
   * quả, đúng như thứ tự ghi thật của runner.
   */
  async function makeExecutionWithManifest(seq: number, schemaVersion = '2.0') {
    const id = await makeExecution(seq)
    await db.insert(schema.cursorExecutionManifest).values({
      workspaceId,
      analysisRunId,
      llmExecutionId: id,
      requestId,
      attemptNumber: 1,
      toolName: '/usr/local/bin/cursor-agent',
      schemaVersion,
      promptVersion: '2.0.0',
      validatorHash: 'a'.repeat(64),
      schemaHash: 'b'.repeat(64),
      promptSourceHash: 'c'.repeat(64),
      flags: ['--print'],
      startedAt: new Date(),
      exitCode: 0,
      failureClass: 'NONE',
    })
    // 0022 đòi PHẢI có dòng kiểm định ĐẠT trước khi ghi kết quả — đúng thứ tự
    // ghi thật của runner: bản kê -> kiểm định -> kết quả.
    await db.insert(schema.analysisValidation).values({
      workspaceId,
      analysisRunId,
      llmExecutionId: id,
      channelId,
      passed: true,
    })
    return id
  }

  describe('chạy lặp lại không ghi đè nhau', () => {
    it('cùng gói + cùng prompt chạy được nhiều lần', async () => {
      const a = await makeExecution(1)
      const b = await makeExecution(2)
      const c = await makeExecution(3)
      expect(new Set([a, b, c]).size).toBe(3)

      const rows = await db
        .select()
        .from(schema.llmExecution)
        .where(eq(schema.llmExecution.analysisRunId, analysisRunId))
      expect(rows.length).toBeGreaterThanOrEqual(3)
    })

    it('trùng execution_sequence bị chặn', async () => {
      await expect(makeExecution(1)).rejects.toThrow()
    })
  })

  describe('bất biến sau khi chốt', () => {
    it('kết quả Cursor KHÔNG sửa được', async () => {
      const execId = await makeExecutionWithManifest(10)
      await db.insert(schema.cursorAnalysisResult).values({
        workspaceId,
        analysisRunId,
        llmExecutionId: execId,
        requestId,
        channelId,
        schemaVersion: '2.0',
        payload: { schemaVersion: '2.0', keyFindings: [] },
        payloadHash: HASH_A,
      })

      await expect(
        db
          .update(schema.cursorAnalysisResult)
          .set({ payloadHash: HASH_B })
          .where(eq(schema.cursorAnalysisResult.llmExecutionId, execId)),
      ).rejects.toThrow(/IMMUTABLE_CURSOR_RESULT/)

      await expect(
        db
          .delete(schema.cursorAnalysisResult)
          .where(eq(schema.cursorAnalysisResult.llmExecutionId, execId)),
      ).rejects.toThrow(/IMMUTABLE_CURSOR_RESULT/)
    })

    it('báo cáo kiểm định KHÔNG sửa được', async () => {
      const execId = await makeExecution(11)
      await db.insert(schema.analysisValidation).values({
        workspaceId,
        analysisRunId,
        llmExecutionId: execId,
        channelId,
        passed: false,
        failureClass: 'UNSUPPORTED_CLAIM',
        causalViolations: 2,
      })

      await expect(
        db
          .update(schema.analysisValidation)
          .set({ passed: true })
          .where(eq(schema.analysisValidation.llmExecutionId, execId)),
      ).rejects.toThrow(/IMMUTABLE_VALIDATION/)
    })
  })

  describe('bất biến SUCCEEDED phải có kết quả', () => {
    it('không thể chốt SUCCEEDED khi chưa có kết quả', async () => {
      const execId = await makeExecution(20)
      await expect(
        db
          .update(schema.llmExecution)
          .set({ status: 'SUCCEEDED' })
          .where(eq(schema.llmExecution.id, execId)),
      ).rejects.toThrow(/EXECUTION_SUCCEEDED_WITHOUT_RESULT/)
    })

    it('chốt được SUCCEEDED sau khi đã ghi kết quả', async () => {
      const execId = await makeExecutionWithManifest(21)
      await db.insert(schema.cursorAnalysisResult).values({
        workspaceId,
        analysisRunId,
        llmExecutionId: execId,
        requestId,
        channelId,
        schemaVersion: '2.0',
        payload: { schemaVersion: '2.0' },
        payloadHash: HASH_A,
      })
      await expect(
        db
          .update(schema.llmExecution)
          .set({ status: 'SUCCEEDED' })
          .where(eq(schema.llmExecution.id, execId)),
      ).resolves.toBeDefined()
    })
  })

  describe('chuỗi retry', () => {
    it('bản kê ghi số lần thử và lần chạy cha', async () => {
      const first = await makeExecution(30)
      const second = await makeExecution(31)

      await db.insert(schema.cursorExecutionManifest).values([
        {
          workspaceId,
          analysisRunId,
          llmExecutionId: first,
          requestId,
          attemptNumber: 1,
          toolName: 'cursor-agent',
          schemaVersion: '2.0',
          promptVersion: '2.0.0',
          validatorHash: 'a'.repeat(64),
          schemaHash: 'b'.repeat(64),
          promptSourceHash: 'c'.repeat(64),
          flags: ['--print', '--mode', 'ask'],
          startedAt: new Date(),
          exitCode: 0,
          failureClass: 'INVALID_JSON',
        },
        {
          workspaceId,
          analysisRunId,
          llmExecutionId: second,
          requestId,
          attemptNumber: 2,
          parentExecutionId: first,
          toolName: 'cursor-agent',
          schemaVersion: '2.0',
          promptVersion: '2.0.0',
          validatorHash: 'a'.repeat(64),
          schemaHash: 'b'.repeat(64),
          promptSourceHash: 'c'.repeat(64),
          flags: ['--print', '--mode', 'ask'],
          startedAt: new Date(),
          exitCode: 0,
          failureClass: 'NONE',
        },
      ])

      const rows = await db
        .select()
        .from(schema.cursorExecutionManifest)
        .where(eq(schema.cursorExecutionManifest.requestId, requestId))
      const child = rows.find((r) => r.attemptNumber === 2)
      expect(child?.parentExecutionId).toBe(first)
    })

    it('số lần thử bị giới hạn ở 3 tại tầng DB', async () => {
      const execId = await makeExecution(32)
      await expect(
        db.insert(schema.cursorExecutionManifest).values({
          workspaceId,
          analysisRunId,
          llmExecutionId: execId,
          requestId,
          attemptNumber: 4, // vượt trần
          toolName: 'cursor-agent',
          schemaVersion: '2.0',
          promptVersion: '2.0.0',
          validatorHash: 'a'.repeat(64),
          schemaHash: 'b'.repeat(64),
          promptSourceHash: 'c'.repeat(64),
          startedAt: new Date(),
        }),
      ).rejects.toThrow()
    })

    it('bản kê KHÔNG lưu dòng lệnh đầy đủ hay biến môi trường', async () => {
      const cols = await db.execute<{ column_name: string }>(sql`
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'cursor_execution_manifest'
      `)
      const names = cols.rows.map((c) => c.column_name)
      // Nếu có cột lưu argv/env thì credential sẽ tự động chảy vào database.
      expect(names).not.toContain('command_line')
      expect(names).not.toContain('environment')
      expect(names).not.toContain('argv')
      expect(names).toContain('flags')
      expect(names).toContain('stderr_hash')
    })
  })

  describe('cách ly workspace', () => {
    it('yêu cầu phân tích không thể trỏ gói của workspace khác', async () => {
      await expect(
        db.insert(schema.cursorAnalysisRequest).values({
          workspaceId: otherWorkspaceId, // workspace KHÁC
          channelId,
          analysisRunId,
          analysisPackageId: packageId,
          packageHash: HASH_A,
          promptRevisionId,
          promptHash: HASH_B,
          promptBytes: 1,
        }),
      ).rejects.toThrow()
    })

    it('kiểm định không thể trỏ execution của workspace khác', async () => {
      const execId = await makeExecution(40)
      await expect(
        db.insert(schema.analysisValidation).values({
          workspaceId: otherWorkspaceId,
          analysisRunId,
          llmExecutionId: execId,
          channelId,
          passed: true,
        }),
      ).rejects.toThrow()
    })
  })

  describe('nguồn gốc PHIÊN BẢN và chuỗi retry', () => {
    it('chuỗi sửa lỗi KHÔNG được trộn phiên bản (trigger DB chặn)', async () => {
      // Ràng buộc ở tầng database, không chỉ ứng dụng: một worker cũ còn chạy
      // song song vẫn ghi thẳng vào bảng được.
      const parent = await makeExecution(90)
      await db.insert(schema.cursorExecutionManifest).values({
        workspaceId,
        analysisRunId,
        llmExecutionId: parent,
        requestId,
        attemptNumber: 1,
        toolName: '/usr/local/bin/cursor-agent',
        schemaVersion: '2.0',
        promptVersion: '2.0.0',
        validatorHash: 'a'.repeat(64),
        schemaHash: 'b'.repeat(64),
        promptSourceHash: 'c'.repeat(64),
        flags: ['--print'],
        startedAt: new Date(),
        exitCode: 0,
        failureClass: 'SCHEMA_MISMATCH',
      })

      const child = await makeExecution(91)
      // Lần sửa lỗi khai validatorHash KHÁC -> phải bị từ chối.
      await expect(
        db.insert(schema.cursorExecutionManifest).values({
          workspaceId,
          analysisRunId,
          llmExecutionId: child,
          requestId,
          attemptNumber: 2,
          parentExecutionId: parent,
          toolName: '/usr/local/bin/cursor-agent',
          schemaVersion: '2.0',
          promptVersion: '2.0.0',
          validatorHash: 'd'.repeat(64), // KHÁC cha
          schemaHash: 'b'.repeat(64),
          promptSourceHash: 'c'.repeat(64),
          flags: ['--print'],
          startedAt: new Date(),
          exitCode: 0,
          failureClass: 'NONE',
        }),
      ).rejects.toThrow(/MIXED_VERSION_REPAIR_CHAIN/)
    })

    it('chuỗi sửa lỗi CÙNG phiên bản được chấp nhận', async () => {
      const parent = await makeExecution(92)
      const common = {
        schemaVersion: '2.0',
        promptVersion: '2.0.0',
        validatorHash: 'e'.repeat(64),
        schemaHash: 'f'.repeat(64),
        promptSourceHash: '0'.repeat(64),
      }
      await db.insert(schema.cursorExecutionManifest).values({
        workspaceId, analysisRunId, llmExecutionId: parent, requestId, attemptNumber: 1,
        toolName: '/usr/local/bin/cursor-agent', ...common,
        flags: ['--print'], startedAt: new Date(), exitCode: 0, failureClass: 'INVALID_JSON',
      })
      const child = await makeExecution(93)
      await expect(
        db.insert(schema.cursorExecutionManifest).values({
          workspaceId, analysisRunId, llmExecutionId: child, requestId, attemptNumber: 2,
          parentExecutionId: parent, toolName: '/usr/local/bin/cursor-agent', ...common,
          flags: ['--print'], startedAt: new Date(), exitCode: 0, failureClass: 'NONE',
        }),
      ).resolves.toBeDefined()
    })

    it('schema-1 và schema-2 không thể chung một chuỗi retry', async () => {
      const parent = await makeExecution(94)
      await db.insert(schema.cursorExecutionManifest).values({
        workspaceId, analysisRunId, llmExecutionId: parent, requestId, attemptNumber: 1,
        toolName: '/usr/local/bin/cursor-agent',
        schemaVersion: '1.0', promptVersion: '1.0.0',
        validatorHash: '1'.repeat(64), schemaHash: '2'.repeat(64), promptSourceHash: '3'.repeat(64),
        flags: ['--print'], startedAt: new Date(), exitCode: 0, failureClass: 'SCHEMA_MISMATCH',
      })
      const child = await makeExecution(95)
      await expect(
        db.insert(schema.cursorExecutionManifest).values({
          workspaceId, analysisRunId, llmExecutionId: child, requestId, attemptNumber: 2,
          parentExecutionId: parent, toolName: '/usr/local/bin/cursor-agent',
          schemaVersion: '2.0', promptVersion: '2.0.0',
          validatorHash: '1'.repeat(64), schemaHash: '2'.repeat(64), promptSourceHash: '3'.repeat(64),
          flags: ['--print'], startedAt: new Date(), exitCode: 0, failureClass: 'NONE',
        }),
      ).rejects.toThrow(/MIXED_VERSION_REPAIR_CHAIN/)
    })

    it('mọi chiều TRÔI DẠT phiên bản đều bị DB từ chối', async () => {
      // Kiểm từng cột một thay vì chỉ một ca đại diện: một cột bị bỏ sót khỏi
      // trigger sẽ là đúng loại lỗ im lặng mà tầng này sinh ra để chặn.
      const common = {
        schemaVersion: '2.0',
        promptVersion: '2.0.0',
        validatorHash: '7'.repeat(64),
        schemaHash: '8'.repeat(64),
        promptSourceHash: '9'.repeat(64),
      }
      const parent = await makeExecution(120)
      await db.insert(schema.cursorExecutionManifest).values({
        workspaceId, analysisRunId, llmExecutionId: parent, requestId, attemptNumber: 1,
        toolName: '/usr/local/bin/cursor-agent', ...common,
        flags: ['--print'], startedAt: new Date(), exitCode: 0, failureClass: 'SCHEMA_MISMATCH',
      })

      const DRIFTS: Array<[string, Partial<typeof common>]> = [
        ['validatorHash', { validatorHash: 'a'.repeat(64) }],
        ['schemaHash', { schemaHash: 'a'.repeat(64) }],
        ['promptSourceHash', { promptSourceHash: 'a'.repeat(64) }],
        ['schemaVersion', { schemaVersion: '1.0' }],
        ['promptVersion', { promptVersion: '1.0.0' }],
      ]
      let seq = 121
      for (const [name, drift] of DRIFTS) {
        const child = await makeExecution(seq++)
        await expect(
          db.insert(schema.cursorExecutionManifest).values({
            workspaceId, analysisRunId, llmExecutionId: child, requestId, attemptNumber: 2,
            parentExecutionId: parent, toolName: '/usr/local/bin/cursor-agent',
            ...common, ...drift,
            flags: ['--print'], startedAt: new Date(), exitCode: 0, failureClass: 'NONE',
          }),
          `trôi dạt ${name} KHÔNG bị chặn`,
        ).rejects.toThrow(/MIXED_VERSION_REPAIR_CHAIN/)
      }
    })

    it('lần sửa lỗi thuộc REQUEST khác bị từ chối (chặn trôi dạt gói/kênh)', async () => {
      // Băm gói, kênh và lần phân tích nằm ở request. "Cùng request" bao trọn
      // cả ba, và là bất biến đúng nghĩa của một chuỗi thử lại.
      const common = {
        schemaVersion: '2.0', promptVersion: '2.0.0',
        validatorHash: 'b'.repeat(64), schemaHash: 'c'.repeat(64), promptSourceHash: 'd'.repeat(64),
      }
      const parent = await makeExecution(140)
      await db.insert(schema.cursorExecutionManifest).values({
        workspaceId, analysisRunId, llmExecutionId: parent, requestId, attemptNumber: 1,
        toolName: '/usr/local/bin/cursor-agent', ...common,
        flags: ['--print'], startedAt: new Date(), exitCode: 0, failureClass: 'INVALID_JSON',
      })

      // Một request KHÁC trong cùng lần phân tích.
      const [otherReq] = await db
        .insert(schema.cursorAnalysisRequest)
        .values({
          workspaceId, channelId, analysisRunId, analysisPackageId: packageId,
          packageHash: HASH_B, promptRevisionId, promptHash: HASH_A, promptBytes: 10,
        })
        .returning()

      const child = await makeExecution(141)
      await expect(
        db.insert(schema.cursorExecutionManifest).values({
          workspaceId, analysisRunId, llmExecutionId: child, requestId: otherReq!.id,
          attemptNumber: 2, parentExecutionId: parent,
          toolName: '/usr/local/bin/cursor-agent', ...common,
          flags: ['--print'], startedAt: new Date(), exitCode: 0, failureClass: 'NONE',
        }),
      ).rejects.toThrow(/REPAIR_REQUEST_DRIFT/)
    })

    it('kết quả khai schema-2 nhưng payload schema-1 bị CHECK từ chối', async () => {
      // Chỗ dễ nói dối nhất: khai 2.0 ở cột, nhét payload 1.0 vào JSONB.
      const execId = await makeExecution(160)
      await db.insert(schema.cursorExecutionManifest).values({
        workspaceId, analysisRunId, llmExecutionId: execId, requestId, attemptNumber: 1,
        toolName: '/usr/local/bin/cursor-agent',
        schemaVersion: '2.0', promptVersion: '2.0.0',
        validatorHash: 'a'.repeat(64), schemaHash: 'b'.repeat(64), promptSourceHash: 'c'.repeat(64),
        flags: ['--print'], startedAt: new Date(), exitCode: 0, failureClass: 'NONE',
      })
      await expect(
        db.insert(schema.cursorAnalysisResult).values({
          workspaceId, analysisRunId, llmExecutionId: execId, requestId, channelId,
          schemaVersion: '2.0',
          payload: { schemaVersion: '1.0', keyFindings: [] },
          payloadHash: HASH_A,
        }),
      ).rejects.toThrow()
    })

    it('kết quả có schema KHÁC bản kê execution bị trigger từ chối', async () => {
      const execId = await makeExecution(161)
      await db.insert(schema.cursorExecutionManifest).values({
        workspaceId, analysisRunId, llmExecutionId: execId, requestId, attemptNumber: 1,
        toolName: '/usr/local/bin/cursor-agent',
        schemaVersion: '2.0', promptVersion: '2.0.0',
        validatorHash: 'd'.repeat(64), schemaHash: 'e'.repeat(64), promptSourceHash: 'f'.repeat(64),
        flags: ['--print'], startedAt: new Date(), exitCode: 0, failureClass: 'NONE',
      })
      await expect(
        db.insert(schema.cursorAnalysisResult).values({
          workspaceId, analysisRunId, llmExecutionId: execId, requestId, channelId,
          schemaVersion: '1.0',
          payload: { schemaVersion: '1.0', keyFindings: [] },
          payloadHash: HASH_A,
        }),
      ).rejects.toThrow(/RESULT_SCHEMA_MISMATCH/)
    })

    it('kết quả gắn vào execution có kiểm định KHÔNG ĐẠT bị từ chối', async () => {
      const execId = await makeExecution(162)
      await db.insert(schema.cursorExecutionManifest).values({
        workspaceId, analysisRunId, llmExecutionId: execId, requestId, attemptNumber: 1,
        toolName: '/usr/local/bin/cursor-agent',
        schemaVersion: '2.0', promptVersion: '2.0.0',
        validatorHash: '1'.repeat(64), schemaHash: '2'.repeat(64), promptSourceHash: '3'.repeat(64),
        flags: ['--print'], startedAt: new Date(), exitCode: 0, failureClass: 'UNSUPPORTED_CLAIM',
      })
      await db.insert(schema.analysisValidation).values({
        workspaceId, analysisRunId, llmExecutionId: execId, channelId, passed: false,
      })
      await expect(
        db.insert(schema.cursorAnalysisResult).values({
          workspaceId, analysisRunId, llmExecutionId: execId, requestId, channelId,
          schemaVersion: '2.0',
          payload: { schemaVersion: '2.0', keyFindings: [] },
          payloadHash: HASH_A,
        }),
      ).rejects.toThrow(/RESULT_WITH_FAILED_VALIDATION/)
    })

    it('băm SAI ĐỊNH DẠNG bị CHECK từ chối', async () => {
      const execId = await makeExecution(163)
      await expect(
        db.insert(schema.cursorExecutionManifest).values({
          workspaceId, analysisRunId, llmExecutionId: execId, requestId, attemptNumber: 1,
          toolName: '/usr/local/bin/cursor-agent',
          schemaVersion: '2.0', promptVersion: '2.0.0',
          validatorHash: 'khong-phai-bam', schemaHash: 'b'.repeat(64), promptSourceHash: 'c'.repeat(64),
          flags: ['--print'], startedAt: new Date(), exitCode: 0, failureClass: 'NONE',
        }),
      ).rejects.toThrow()
    })

    it('băm nguồn gốc TRUY VẤN ĐƯỢC bằng cột, không phải đào trong JSONB', async () => {
      const rows = await db.execute<{ n: number }>(sql`
        SELECT count(*)::int AS n FROM cursor_execution_manifest
        WHERE validator_hash = ${'e'.repeat(64)} AND schema_version = '2.0'
      `)
      expect(Number(rows.rows[0]!.n)).toBeGreaterThan(0)
    })

    it('payload schema-2 đầy đủ đi vòng qua JSONB KHÔNG bị đổi hay cắt', async () => {
      // Chứng minh thay vì giả định: metricClaims lồng nhau, chữ có dấu, số
      // thực, mảng rỗng, giá trị optional đều phải quay về nguyên vẹn.
      const execId = await makeExecutionWithManifest(96)
      const payload = {
        schemaVersion: '2.0',
        metricClaims: [
          {
            id: 'MC-001',
            claimType: 'METHODOLOGY_LIMITATION',
            subjectMetric: 'sample_size',
            relatedMetric: 'impression_ctr',
            judgement: 'LOW',
            assertionStatus: 'LIMITATION',
            evidenceIds: ['OBS-001', 'VIDEO-aaaaaaaaaaa'],
            requiresMissingnessDisclosure: true,
            text: 'Sample size view thấp làm CTR nhiễu — độ phủ 0%',
            sourceSection: 'KEY_FINDING',
            sourceId: 'F-001',
          },
        ],
        nested: { deep: { value: 1.23456789, empty: [], vi: 'giữ chân — hiệu quả' } },
      }
      await db.insert(schema.cursorAnalysisResult).values({
        workspaceId, analysisRunId, llmExecutionId: execId, requestId, channelId,
        schemaVersion: '2.0', payload, payloadHash: HASH_A,
      })
      const back = await db
        .select({ payload: schema.cursorAnalysisResult.payload, sv: schema.cursorAnalysisResult.schemaVersion })
        .from(schema.cursorAnalysisResult)
        .where(eq(schema.cursorAnalysisResult.llmExecutionId, execId))
      expect(back[0]!.sv).toBe('2.0')
      expect(back[0]!.payload).toEqual(payload)
    })
  })

  describe('nguồn gốc', () => {
    it('yêu cầu neo được về gói, băm gói, prompt và băm prompt', async () => {
      const rows = await db
        .select()
        .from(schema.cursorAnalysisRequest)
        .where(eq(schema.cursorAnalysisRequest.id, requestId))
      const r = rows[0]!
      expect(r.analysisPackageId).toBe(packageId)
      expect(r.packageHash).toBe(HASH_A)
      expect(r.promptRevisionId).toBe(promptRevisionId)
      expect(r.promptHash).toBe(HASH_B)
      expect(r.promptBytes).toBeGreaterThan(0)
    })

    it('gói phải thuộc ĐÚNG kênh và ĐÚNG lần phân tích của yêu cầu', async () => {
      // Trước khi có khoá ngoại phức hợp, ba ràng buộc được kiểm ĐỘC LẬP: kênh
      // thuộc workspace, lần chạy thuộc (workspace, kênh), gói thuộc workspace.
      // Không cái nào nối GÓI với LẦN CHẠY hay KÊNH — nên trong cùng workspace
      // vẫn ghi được "lần chạy của kênh B đã phân tích gói của kênh A". Mọi
      // khoá ngoại hợp lệ, nguồn gốc lưu lại thì SAI.
      const [ch2] = await db
        .insert(schema.channel)
        .values({
          workspaceId,
          label: 'kenh_khac',
          youtubeChannelId: 'UCcursor00000000000001',
          title: 'Kênh khác',
        })
        .returning()

      const [algo2] = await db
        .select()
        .from(schema.algorithm)
        .limit(1)
      const [ver2] = await db.select().from(schema.algorithmVersion).limit(1)

      const [run2] = await db
        .insert(schema.analysisRun)
        .values({
          workspaceId,
          channelId: ch2!.id,
          subjectType: 'CHANNEL',
          subjectId: ch2!.id,
          algorithmId: algo2!.id,
          algorithmVersionId: ver2!.id,
          runSequence: 1,
          inputHash: HASH_B,
          periodStart: '2026-06-01',
          periodEnd: '2026-07-27',
          status: 'SUCCEEDED',
        })
        .returning()

      // Cùng workspace, nhưng gói thuộc kênh/lần chạy KHÁC -> phải bị từ chối.
      await expect(
        db.insert(schema.cursorAnalysisRequest).values({
          workspaceId,
          channelId: ch2!.id,
          analysisRunId: run2!.id,
          analysisPackageId: packageId, // gói của kênh phong_thuy, lần chạy khác
          packageHash: HASH_A,
          promptRevisionId,
          promptHash: HASH_B,
          promptBytes: 1,
        }),
      ).rejects.toThrow()
    })

    it('kết quả KHÔNG ghép được execution của lần chạy khác', async () => {
      // Migration 0016 mới chỉ nối yêu cầu -> gói. Nếu kết quả chỉ kiểm workspace
      // riêng lẻ cho execution/request/channel thì trong cùng workspace vẫn ghi
      // được: execution của lần chạy B + request của lần chạy A. Mọi khoá ngoại
      // hợp lệ, payload của A được trình bày như kết quả của B.
      const [algo2] = await db.select().from(schema.algorithm).limit(1)
      const [ver2] = await db.select().from(schema.algorithmVersion).limit(1)
      const [runB] = await db
        .insert(schema.analysisRun)
        .values({
          workspaceId,
          channelId,
          subjectType: 'CHANNEL',
          subjectId: channelId,
          algorithmId: algo2!.id,
          algorithmVersionId: ver2!.id,
          runSequence: 99,
          inputHash: HASH_B,
          periodStart: '2026-06-01',
          periodEnd: '2026-07-27',
          status: 'SUCCEEDED',
        })
        .returning()

      const execId = await makeExecution(77)

      // execution thuộc lần chạy A, nhưng khai analysis_run_id = lần chạy B.
      await expect(
        db.insert(schema.cursorAnalysisResult).values({
          workspaceId,
          analysisRunId: runB!.id,
          llmExecutionId: execId,
          requestId,
          channelId,
          schemaVersion: '2.0',
          payload: { schemaVersion: '2.0', keyFindings: [] },
          payloadHash: HASH_A,
        }),
      ).rejects.toThrow()
    })

    it('parent execution phải CÙNG lần phân tích', async () => {
      // 0017 chỉ ràng (parent, workspace). Thiếu analysis_run_id, một bản kê của
      // lần chạy B vẫn khai được cha là execution của lần chạy A cùng workspace —
      // chuỗi retry bắc ngang hai lần phân tích.
      const [algo2] = await db.select().from(schema.algorithm).limit(1)
      const [ver2] = await db.select().from(schema.algorithmVersion).limit(1)
      const [runC] = await db
        .insert(schema.analysisRun)
        .values({
          workspaceId,
          channelId,
          subjectType: 'CHANNEL',
          subjectId: channelId,
          algorithmId: algo2!.id,
          algorithmVersionId: ver2!.id,
          runSequence: 98,
          inputHash: HASH_A,
          periodStart: '2026-06-01',
          periodEnd: '2026-07-27',
          status: 'SUCCEEDED',
        })
        .returning()

      // execution thuộc lần chạy A
      const parentInRunA = await makeExecution(81)

      // bản kê khai analysis_run_id = lần chạy C nhưng cha thuộc lần chạy A
      await expect(
        db.insert(schema.cursorExecutionManifest).values({
          workspaceId,
          analysisRunId: runC!.id,
          llmExecutionId: parentInRunA,
          requestId,
          attemptNumber: 2,
          parentExecutionId: parentInRunA,
          toolName: 'cursor-agent',
          schemaVersion: '2.0',
          promptVersion: '2.0.0',
          validatorHash: 'a'.repeat(64),
          schemaHash: 'b'.repeat(64),
          promptSourceHash: 'c'.repeat(64),
          flags: ['--print'],
          startedAt: new Date(),
          exitCode: 0,
          failureClass: 'NONE',
        }),
      ).rejects.toThrow()
    })

    it('bản kê KHÔNG trỏ được parent execution không tồn tại', async () => {
      // parent_execution_id trước đây không có khoá ngoại nào.
      const execId = await makeExecution(78)
      await expect(
        db.insert(schema.cursorExecutionManifest).values({
          workspaceId,
          analysisRunId,
          llmExecutionId: execId,
          requestId,
          attemptNumber: 2,
          parentExecutionId: '00000000-0000-0000-0000-000000000000',
          toolName: 'cursor-agent',
          schemaVersion: '2.0',
          promptVersion: '2.0.0',
          validatorHash: 'a'.repeat(64),
          schemaHash: 'b'.repeat(64),
          promptSourceHash: 'c'.repeat(64),
          flags: ['--print'],
          startedAt: new Date(),
          exitCode: 0,
          failureClass: 'NONE',
        }),
      ).rejects.toThrow()
    })

    it('băm phải đúng định dạng sha256', async () => {
      await expect(
        db.insert(schema.cursorAnalysisRequest).values({
          workspaceId,
          channelId,
          analysisRunId,
          analysisPackageId: packageId,
          packageHash: 'không-phải-hash',
          promptRevisionId,
          promptHash: HASH_B,
          promptBytes: 1,
        }),
      ).rejects.toThrow()
    })
  })
})
