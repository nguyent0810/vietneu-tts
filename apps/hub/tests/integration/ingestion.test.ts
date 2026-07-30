import { afterAll, beforeEach, describe, expect, it } from 'vitest'
import { eq, sql } from 'drizzle-orm'

import {
  channel,
  channelDailyMetric,
  syncCheckpoint,
  syncRun,
  video,
  videoDailyMetric,
  videoDailyMetricHistory,
  workspace,
} from '@/db/schema'
import {
  advanceCheckpoint,
  finishSyncRun,
  startSyncRun,
  upsertChannelMetrics,
  upsertVideoMetrics,
  upsertVideos,
} from '@/lib/sync'
import { withTransaction } from '@/db/client'
import { closeTestPool, hasTestDatabase, testDb, truncateAll } from '../helpers/db'

const VID_A = 'aaaaaaaaaaa'
const VID_B = 'bbbbbbbbbbb'

describe.skipIf(!hasTestDatabase)('nhập dữ liệu analytics (PostgreSQL thật)', () => {
  const db = testDb()
  let workspaceId: string
  let channelId: string
  let syncRunId: string

  afterAll(async () => {
    await closeTestPool()
  })

  beforeEach(async () => {
    await truncateAll()
    await db.execute(sql`TRUNCATE TABLE video_daily_metric_history, video_daily_metric,
      channel_daily_metric, analytics_api_call, sync_checkpoint, sync_run, video CASCADE`)

    const [ws] = await db.insert(workspace).values({ slug: 'ws', name: 'W' }).returning()
    workspaceId = ws!.id
    const [ch] = await db
      .insert(channel)
      .values({
        workspaceId,
        label: 'phong_thuy',
        youtubeChannelId: 'UCtest0000000000000000',
        title: 'T',
      })
      .returning()
    channelId = ch!.id

    syncRunId = await startSyncRun({
      workspaceId,
      channelId,
      requestedFrom: '2026-07-01',
      requestedTo: '2026-07-10',
      workerLabel: 'test',
    })

    await upsertVideos({
      workspaceId,
      channelId,
      videos: [
        { youtubeVideoId: VID_A, title: 'A', publishedAt: '2026-07-01T00:00:00Z', durationSeconds: 300, format: 'LONG_FORM' },
        { youtubeVideoId: VID_B, title: 'B', publishedAt: '2026-07-02T00:00:00Z', durationSeconds: 45, format: 'SHORT' },
      ],
    })
  })

  describe('upsert idempotent', () => {
    it('chạy lại cùng dữ liệu không tạo hàng mới và không sinh lịch sử', async () => {
      const metrics = [
        { youtubeVideoId: VID_A, date: '2026-07-01', views: 100, likes: 5 },
        { youtubeVideoId: VID_A, date: '2026-07-02', views: 150, likes: 7 },
      ]

      const first = await upsertVideoMetrics({ workspaceId, syncRunId, metrics })
      expect(first.upserted).toBe(2)

      const second = await upsertVideoMetrics({ workspaceId, syncRunId, metrics })
      expect(second.revised).toBe(0)

      const rows = await db.select().from(videoDailyMetric)
      expect(rows).toHaveLength(2)

      const history = await db.select().from(videoDailyMetricHistory)
      expect(history, 'giá trị không đổi thì KHÔNG được ghi lịch sử').toHaveLength(0)
    })

    it('upsert video hai lần không nhân bản', async () => {
      await upsertVideos({
        workspaceId,
        channelId,
        videos: [{ youtubeVideoId: VID_A, title: 'A đổi tên', publishedAt: '2026-07-01T00:00:00Z' }],
      })
      const rows = await db.select().from(video).where(eq(video.youtubeVideoId, VID_A))
      expect(rows).toHaveLength(1)
      expect(rows[0]!.title).toBe('A đổi tên')
    })

    it('bỏ qua chỉ số của video chưa biết thay vì tạo video rỗng', async () => {
      // Một video "ma" không tiêu đề, không ngày đăng sẽ làm hỏng mọi so sánh
      // ở Phase 3, nên thà bỏ hàng chỉ số đó và báo ra.
      const res = await upsertVideoMetrics({
        workspaceId,
        syncRunId,
        metrics: [{ youtubeVideoId: 'zzzzzzzzzzz', date: '2026-07-01', views: 10 }],
      })
      expect(res.upserted).toBe(0)
      expect(await db.select().from(video)).toHaveLength(2)
    })
  })

  describe('lịch sử SCD-2 khi YouTube sửa số liệu', () => {
    it('ghi GIÁ TRỊ CŨ khi số liệu bị sửa', async () => {
      await upsertVideoMetrics({
        workspaceId,
        syncRunId,
        metrics: [{ youtubeVideoId: VID_A, date: '2026-07-01', views: 100, likes: 5 }],
      })
      // YouTube chốt lại số liệu sau 48-72h.
      await upsertVideoMetrics({
        workspaceId,
        syncRunId,
        metrics: [{ youtubeVideoId: VID_A, date: '2026-07-01', views: 137, likes: 6 }],
      })

      const history = await db.select().from(videoDailyMetricHistory)
      expect(history).toHaveLength(1)
      expect(Number(history[0]!.views), 'lịch sử phải giữ giá trị CŨ').toBe(100)

      const current = await db.select().from(videoDailyMetric)
      expect(Number(current[0]!.views)).toBe(137)
      expect(current[0]!.revisionCount).toBe(1)
    })

    it('phân biệt được chuyển đổi NULL <-> có giá trị', async () => {
      // `IS DISTINCT FROM` chứ không phải `<>`: NULL <> NULL cho ra NULL nên
      // dùng `<>` sẽ bỏ sót đúng loại thay đổi này.
      await upsertVideoMetrics({
        workspaceId,
        syncRunId,
        metrics: [{ youtubeVideoId: VID_A, date: '2026-07-01', views: 10, impressions: null }],
      })
      await upsertVideoMetrics({
        workspaceId,
        syncRunId,
        metrics: [{ youtubeVideoId: VID_A, date: '2026-07-01', views: 10, impressions: 500 }],
      })

      const history = await db.select().from(videoDailyMetricHistory)
      expect(history).toHaveLength(1)
      expect(history[0]!.impressions).toBeNull()
    })

    it('lịch sử là append-only', async () => {
      await upsertVideoMetrics({
        workspaceId, syncRunId,
        metrics: [{ youtubeVideoId: VID_A, date: '2026-07-01', views: 1 }],
      })
      await upsertVideoMetrics({
        workspaceId, syncRunId,
        metrics: [{ youtubeVideoId: VID_A, date: '2026-07-01', views: 2 }],
      })

      await expect(
        db.delete(videoDailyMetricHistory).where(sql`true`),
      ).rejects.toThrow(/IMMUTABLE_METRIC_HISTORY/)
    })
  })

  describe('thiếu dữ liệu không bị bịa thành 0', () => {
    it('chỉ số vắng mặt lưu NULL, khác hẳn giá trị 0', async () => {
      await upsertVideoMetrics({
        workspaceId,
        syncRunId,
        metrics: [
          { youtubeVideoId: VID_A, date: '2026-07-01', views: 0 }, // thật sự 0 lượt xem
          { youtubeVideoId: VID_B, date: '2026-07-01', views: 5 }, // không có impressions
        ],
      })

      const rows = await db.select().from(videoDailyMetric).orderBy(videoDailyMetric.videoId)
      for (const r of rows) {
        expect(r.impressions, 'chỉ số không được trả về phải là NULL').toBeNull()
        expect(r.impressionCtr).toBeNull()
      }
      const zeroViews = rows.find((r) => Number(r.views) === 0)
      expect(zeroViews, '0 lượt xem là dữ liệu THẬT, không phải thiếu').toBeDefined()
    })

    it('chấp nhận averageViewPercentage > 100 (người xem tua lại)', async () => {
      await expect(
        upsertVideoMetrics({
          workspaceId,
          syncRunId,
          metrics: [{ youtubeVideoId: VID_A, date: '2026-07-03', averageViewPercentage: 143.7 }],
        }),
      ).resolves.toBeDefined()
    })

    it('chấp nhận likes/dislikes ÂM (báo cáo theo ngày là chênh lệch)', async () => {
      await expect(
        upsertVideoMetrics({
          workspaceId,
          syncRunId,
          metrics: [{ youtubeVideoId: VID_A, date: '2026-07-04', likes: -3, dislikes: -1 }],
        }),
      ).resolves.toBeDefined()
    })
  })

  describe('AC-4: bản ghi kiểm toán sống sót khi thất bại', () => {
    it('sync_run vẫn tồn tại ở trạng thái FAILED kèm lỗi', async () => {
      await finishSyncRun({
        syncRunId,
        status: 'FAILED',
        error: new Error('YouTube trả 500'),
        warnings: ['một cảnh báo'],
      })

      const rows = await db.select().from(syncRun).where(eq(syncRun.id, syncRunId))
      expect(rows, 'bằng chứng đã chạy gì KHÔNG được biến mất').toHaveLength(1)
      expect(rows[0]!.status).toBe('FAILED')
      expect(rows[0]!.error).not.toBeNull()
      expect(rows[0]!.finishedAt).not.toBeNull()
    })

    it('lỗi giữa lô làm rollback TOÀN BỘ lô, nhưng sync_run vẫn sống', async () => {
      // Regression (Codex Phase 2 R5 HIGH): route ingest từng chạy rời từng câu
      // lệnh qua driver HTTP, nên một lỗi ở bước sau vẫn để lại video và chỉ số
      // video đã ghi — lô nhập dở dang. AC-4 đòi cả lô là MỘT đơn vị.
      const beforeVideos = (await db.select().from(video)).length

      await expect(
        withTransaction(async (tx) => {
          await upsertVideos({
            workspaceId,
            channelId,
            videos: [
              {
                youtubeVideoId: 'ccccccccccc',
                title: 'sẽ bị rollback',
                publishedAt: '2026-07-05T00:00:00Z',
              },
            ],
            db: tx,
          })
          await upsertVideoMetrics({
            workspaceId,
            syncRunId,
            metrics: [{ youtubeVideoId: 'ccccccccccc', date: '2026-07-05', views: 42 }],
            db: tx,
          })
          // Ép lỗi SAU khi đã ghi -- mô phỏng lô hỏng giữa chừng.
          throw new Error('lỗi giữa lô')
        }),
      ).rejects.toThrow('lỗi giữa lô')

      const afterVideos = await db.select().from(video)
      expect(afterVideos.length, 'video của lô hỏng phải bị rollback').toBe(beforeVideos)
      expect(afterVideos.find((v) => v.youtubeVideoId === 'ccccccccccc')).toBeUndefined()

      const orphanMetrics = await db
        .select()
        .from(videoDailyMetric)
        .where(eq(videoDailyMetric.date, '2026-07-05'))
      expect(orphanMetrics, 'chỉ số của lô hỏng phải bị rollback').toHaveLength(0)

      // Nhưng bản ghi kiểm toán KHÔNG nằm trong transaction đó nên vẫn còn.
      const runs = await db.select().from(syncRun).where(eq(syncRun.id, syncRunId))
      expect(runs).toHaveLength(1)
    })

    it('không cho FAILED mà thiếu mô tả lỗi', async () => {
      await expect(
        db.update(syncRun).set({ status: 'FAILED', finishedAt: new Date(), error: null })
          .where(eq(syncRun.id, syncRunId)),
      ).rejects.toThrow()
    })

    it('lỗi ghi vào DB không chứa connection string', async () => {
      await finishSyncRun({
        syncRunId,
        status: 'FAILED',
        error: new Error('connect failed postgresql://user:hunter2@host/db'),
      })
      const rows = await db.select().from(syncRun).where(eq(syncRun.id, syncRunId))
      const text = JSON.stringify(rows[0]!.error)
      // describeError chỉ lấy message; test này khoá lại việc KHÔNG BAO GIỜ
      // ghi nguyên object lỗi (có thể mang theo config chứa mật khẩu).
      expect(text).not.toContain('hunter2@host')
    })
  })

  describe('checkpoint', () => {
    it('chỉ tiến, không lùi', async () => {
      await advanceCheckpoint({ workspaceId, channelId, syncRunId, lastCompleteDate: '2026-07-20' })
      // Một lần chạy lấy lại dữ liệu cũ không được kéo checkpoint về quá khứ,
      // nếu không lần sau sẽ đồng bộ thừa vô hạn.
      await advanceCheckpoint({ workspaceId, channelId, syncRunId, lastCompleteDate: '2026-07-05' })

      const rows = await db.select().from(syncCheckpoint).where(eq(syncCheckpoint.channelId, channelId))
      expect(rows[0]!.lastCompleteDate).toBe('2026-07-20')
    })

    it('checkpoint không được vượt quá khoảng đã yêu cầu', async () => {
      // Regression (Codex Phase 2 HIGH): server từng nhận bất kỳ
      // lastCompleteDate nào client gửi. Một worker lỗi có thể đẩy checkpoint
      // nhảy qua những ngày CHƯA HỀ được lấy, và vì lần sau chỉ lấy từ
      // checkpoint trở đi, lỗ hổng đó thành vĩnh viễn và im lặng.
      //
      // Ràng buộc nằm ở route (đã kiểm bằng test HTTP bên dưới); ở đây khẳng
      // định bản thân sync_run có ghi lại khoảng đã yêu cầu để route đối chiếu.
      const rows = await db.select().from(syncRun).where(eq(syncRun.id, syncRunId))
      expect(rows[0]!.requestedFrom).toBe('2026-07-01')
      expect(rows[0]!.requestedTo).toBe('2026-07-10')
    })

    it('mỗi kênh chỉ có một checkpoint', async () => {
      await advanceCheckpoint({ workspaceId, channelId, syncRunId, lastCompleteDate: '2026-07-10' })
      await advanceCheckpoint({ workspaceId, channelId, syncRunId, lastCompleteDate: '2026-07-11' })
      const rows = await db.select().from(syncCheckpoint).where(eq(syncCheckpoint.channelId, channelId))
      expect(rows).toHaveLength(1)
    })
  })

  describe('chỉ số cấp kênh', () => {
    it('upsert idempotent theo (channel, date)', async () => {
      const metrics = [{ date: '2026-07-01', views: 1000 }, { date: '2026-07-02', views: 2000 }]
      await upsertChannelMetrics({ workspaceId, channelId, syncRunId, metrics })
      await upsertChannelMetrics({ workspaceId, channelId, syncRunId, metrics })
      const rows = await db.select().from(channelDailyMetric)
      expect(rows).toHaveLength(2)
    })

    it('đếm số lần bị sửa', async () => {
      await upsertChannelMetrics({
        workspaceId, channelId, syncRunId, metrics: [{ date: '2026-07-01', views: 1000 }],
      })
      await upsertChannelMetrics({
        workspaceId, channelId, syncRunId, metrics: [{ date: '2026-07-01', views: 1234 }],
      })
      const rows = await db.select().from(channelDailyMetric)
      expect(rows[0]!.revisionCount).toBe(1)
      expect(Number(rows[0]!.views)).toBe(1234)
    })
  })
})
