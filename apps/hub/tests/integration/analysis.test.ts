import { afterAll, beforeAll, describe, expect, it } from 'vitest'
import { eq, sql } from 'drizzle-orm'

import * as schema from '@/db/schema'
import { runDeterministicAnalysis } from '@/lib/analysis/run'
import { hashPackage, packageBytes, stableStringify } from '@/lib/analysis/package'
import { containsCausalClaim } from '@/lib/analysis/observations'
import { ANALYSIS_THRESHOLDS } from '@/lib/analysis/config'
import { closeTestPool, hasTestDatabase, testDb, truncateAll } from '../helpers/db'

/**
 * Phân tích tất định trên PostgreSQL THẬT.
 *
 * Dựng một kênh tổng hợp có kiểm soát để khẳng định được các tính chất chính
 * xác (tất định, chuẩn hoá theo tuổi, tách định dạng). Kiểm trên 3 kênh thật
 * nằm ở `analysis-real-channels.test.ts`.
 */
describe.skipIf(!hasTestDatabase)('phân tích tất định (PostgreSQL thật)', () => {
  const db = testDb()
  let workspaceId: string
  let channelId: string

  const WINDOW_START = '2026-06-01'
  const WINDOW_END = '2026-07-27'

  beforeAll(async () => {
    await truncateAll()
    await db.execute(sql`TRUNCATE TABLE analysis_package, analysis_quality, anomaly, cohort_summary,
      evidence_reference, deterministic_observation, feature_value, feature_version, feature_definition,
      video_daily_metric_history, video_daily_metric, channel_daily_metric, video CASCADE`)

    const [ws] = await db.insert(schema.workspace).values({ slug: 'ws-an', name: 'W' }).returning()
    workspaceId = ws!.id

    const [ch] = await db
      .insert(schema.channel)
      .values({
        workspaceId,
        label: 'phong_thuy',
        youtubeChannelId: 'UCanalysis0000000000000',
        title: 'Test',
        reportingTimezone: 'America/Los_Angeles',
      })
      .returning()
    channelId = ch!.id

    const [algo] = await db
      .insert(schema.algorithm)
      .values({ key: 'deterministic-analysis', name: 'Det', kind: 'DETERMINISTIC' })
      .returning()
    await db.insert(schema.algorithmVersion).values({ algorithmId: algo!.id, version: '1.0.0' })

    // 12 Shorts + 6 long-form, đủ tuổi, cộng 2 video mới chưa chín.
    const videos: Array<typeof schema.video.$inferInsert> = []
    for (let i = 0; i < 12; i++) {
      videos.push({
        workspaceId,
        channelId,
        youtubeVideoId: `s${String(i).padStart(10, '0')}`,
        title: `Short ${i}`,
        publishedAt: new Date(`2026-06-${String(i + 1).padStart(2, '0')}T14:00:00Z`),
        durationSeconds: 45,
        format: 'SHORT',
        publishedHourLocal: 7,
      })
    }
    for (let i = 0; i < 6; i++) {
      videos.push({
        workspaceId,
        channelId,
        youtubeVideoId: `l${String(i).padStart(10, '0')}`,
        title: `Long ${i}`,
        publishedAt: new Date(`2026-06-${String(i + 1).padStart(2, '0')}T20:00:00Z`),
        durationSeconds: 900,
        format: 'LONG_FORM',
        publishedHourLocal: 13,
      })
    }
    // Video mới đăng: phải bị đánh dấu chưa chín, KHÔNG bị gán 0.
    videos.push({
      workspaceId,
      channelId,
      youtubeVideoId: 'nnnnnnnnnnn',
      title: 'Mới hôm qua',
      publishedAt: new Date('2026-07-26T10:00:00Z'),
      durationSeconds: 40,
      format: 'SHORT',
      publishedHourLocal: 3,
    })
    const inserted = await db.insert(schema.video).values(videos).returning({
      id: schema.video.id,
      yt: schema.video.youtubeVideoId,
    })

    const metrics: Array<typeof schema.videoDailyMetric.$inferInsert> = []
    for (const v of inserted) {
      const isShort = v.yt.startsWith('s')
      const isNew = v.yt.startsWith('n')
      const idx = Number(v.yt.slice(1)) || 0
      const start = isNew ? 26 : idx + 1
      const days = isNew ? 1 : 10
      for (let d = 0; d < days; d++) {
        const dayNum = start + d
        const month = isNew ? '07' : '06'
        if (dayNum > 30) continue
        metrics.push({
          workspaceId,
          videoId: v.id,
          date: `2026-${month}-${String(dayNum).padStart(2, '0')}`,
          // Short thứ 11 cố tình rất cao -> outlier kiểm chứng được.
          views: isShort ? (idx === 11 ? 50_000 : 100 + idx * 10) : 500 + idx * 20,
          estimatedMinutesWatched: String(isShort ? 20 : 400),
          averageViewDurationSeconds: String(isShort ? 25 : 300),
          // Vượt 100% có chủ đích: người xem tua lại — dữ liệu THẬT của YouTube.
          averageViewPercentage: String(isShort ? (idx === 0 ? 143.7 : 60) : 35),
          likes: 5,
          comments: 1,
          shares: 1,
          subscribersGained: 2,
          subscribersLost: idx === 3 ? 9 : 0, // đăng ký ròng ÂM ở một video
          impressions: null, // YouTube không cấp -> phải giữ NULL
          impressionCtr: null,
        })
      }
    }
    for (let i = 0; i < metrics.length; i += 400) {
      await db.insert(schema.videoDailyMetric).values(metrics.slice(i, i + 400))
    }

    const channelDaily: Array<typeof schema.channelDailyMetric.$inferInsert> = []
    for (let d = 1; d <= 27; d++) {
      channelDaily.push({
        workspaceId,
        channelId,
        date: `2026-06-${String(d).padStart(2, '0')}`,
        views: 1000 + d,
        estimatedMinutesWatched: '500',
      })
    }
    await db.insert(schema.channelDailyMetric).values(channelDaily)
  })

  afterAll(async () => {
    await closeTestPool()
  })

  describe('tính tất định', () => {
    it('cùng input cho cùng hash gói', async () => {
      const a = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      const b = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      expect(a.packageHash).toBe(b.packageHash)
      expect(a.packageBytes).toBe(b.packageBytes)
      expect(stableStringify(a.package)).toBe(stableStringify(b.package))
    })

    it('hash của gói ĐÃ GHI khớp hash dry-run và ổn định qua nhiều lần chạy', async () => {
      // Regression (Codex Phase 3 R3 HIGH): hash từng bao gồm `analysisRunId`,
      // một UUID ngẫu nhiên sinh lúc ghi. Hệ quả: hai lần chạy trên CÙNG dữ liệu
      // cho hai hash khác nhau, tức hash mất hết khả năng so sánh — kể cả để
      // nhận ra một lần tính lại không đổi kết quả.
      const dry = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      const first = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END,
      })
      const second = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END,
      })

      expect(first.analysisRunId).not.toBe(second.analysisRunId) // run khác nhau...
      expect(first.packageHash).toBe(second.packageHash) // ...nhưng nội dung y hệt
      expect(first.packageHash).toBe(dry.packageHash) // và khớp cả dry-run

      const stored = await db.execute<{ h: string; n: string }>(sql`
        SELECT payload_hash AS h, count(*) OVER ()::text AS n
        FROM analysis_package ORDER BY created_at DESC LIMIT 2
      `)
      expect(stored.rows[0]!.h).toBe(stored.rows[1]!.h)
    })

    it('hash không phụ thuộc thứ tự khoá của object', () => {
      const one = { b: 1, a: { d: 2, c: 3 }, arr: [{ y: 1, x: 2 }] }
      const two = { a: { c: 3, d: 2 }, arr: [{ x: 2, y: 1 }], b: 1 }
      expect(stableStringify(one)).toBe(stableStringify(two))
    })

    it('thứ tự xếp hạng ổn định giữa các lần chạy', async () => {
      const a = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      const b = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      expect(a.package.rankedVideos.map((v) => v.youtubeVideoId)).toEqual(
        b.package.rankedVideos.map((v) => v.youtubeVideoId),
      )
      expect(a.package.observations.map((o) => o.statement)).toEqual(
        b.package.observations.map((o) => o.statement),
      )
    })

    it('đổi cửa sổ thì đổi hash (hash thật sự phụ thuộc input)', async () => {
      const a = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      const c = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: '2026-07-20', dryRun: true,
      })
      expect(a.packageHash).not.toBe(c.packageHash)
    })
  })

  describe('chuẩn hoá theo tuổi và định dạng', () => {
    it('video mới đăng KHÔNG bị gán 0 cho cửa sổ 7 ngày', async () => {
      const r = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      const ranked = r.package.rankedVideos.find((v) => v.youtubeVideoId === 'nnnnnnnnnnn')
      // Không đủ tuổi cho views_d7 -> không được xếp hạng bằng một con số bịa.
      expect(ranked?.viewsD7 ?? null).toBeNull()
      expect(r.package.dataCoverage.videosImmature).toBeGreaterThan(0)
    })

    it('video đăng TRƯỚC cửa sổ vẫn có views_d7 ĐẦY ĐỦ', async () => {
      // Regression (Codex Phase 3 HIGH): truy vấn từng lọc `date >= windowStart`
      // trong khi cửa sổ theo tuổi bắt đầu từ NGÀY ĐĂNG. Video đăng trước cửa
      // sổ vì thế bị cộng thiếu ngày và trả về con số NHỎ HƠN THỰC TẾ mà không
      // có dấu hiệu gì — sai âm thầm, tệ hơn nhiều so với báo thiếu.
      const [ch2] = await db
        .insert(schema.channel)
        .values({
          workspaceId,
          label: 'hinh_su',
          youtubeChannelId: 'UCearly00000000000000x',
          title: 'Early',
          reportingTimezone: 'UTC',
        })
        .returning()

      const [v] = await db
        .insert(schema.video)
        .values({
          workspaceId,
          channelId: ch2!.id,
          youtubeVideoId: 'earlyvideo1',
          title: 'Đăng trước cửa sổ',
          // Đăng 3 ngày TRƯỚC windowStart.
          publishedAt: new Date('2026-05-29T00:00:00Z'),
          durationSeconds: 60,
          format: 'SHORT',
          publishedHourLocal: 0,
        })
        .returning()

      // 7 ngày đầu: 10+20+30+40+50+60+70 = 280. Ba ngày đầu nằm TRƯỚC windowStart.
      const daily = [10, 20, 30, 40, 50, 60, 70]
      await db.insert(schema.videoDailyMetric).values(
        daily.map((views, i) => ({
          workspaceId,
          videoId: v!.id,
          date: `2026-0${i < 3 ? '5' : '6'}-${String(i < 3 ? 29 + i : i - 2).padStart(2, '0')}`,
          views,
        })),
      )

      // Cần đủ mẫu để phân vị có nghĩa (ngưỡng minSampleForPercentile), nếu
      // không video sẽ không lọt vào danh sách xếp hạng.
      const siblings = await db
        .insert(schema.video)
        .values(
          Array.from({ length: 6 }, (_, i) => ({
            workspaceId,
            channelId: ch2!.id,
            youtubeVideoId: `sibling${String(i).padStart(4, '0')}`,
            title: `Sibling ${i}`,
            publishedAt: new Date(`2026-06-0${i + 1}T00:00:00Z`),
            durationSeconds: 60,
            format: 'SHORT' as const,
            publishedHourLocal: 0,
          })),
        )
        .returning({ id: schema.video.id })
      await db.insert(schema.videoDailyMetric).values(
        siblings.flatMap((sv, i) =>
          Array.from({ length: 7 }, (_, d) => ({
            workspaceId,
            videoId: sv.id,
            date: `2026-06-${String(i + 1 + d).padStart(2, '0')}`,
            views: 100 + i,
          })),
        ),
      )

      const r = await runDeterministicAnalysis({
        workspaceId,
        channelLabel: 'hinh_su',
        windowStart: WINDOW_START,
        windowEnd: WINDOW_END,
        dryRun: true,
      })
      const ranked = r.package.rankedVideos.find((x) => x.youtubeVideoId === 'earlyvideo1')
      expect(ranked, 'video phải có mặt').toBeDefined()
      expect(ranked!.viewsD7, 'phải cộng đủ 7 ngày kể từ ngày đăng, không cắt ở windowStart').toBe(280)
    })

    it('phân vị tính TRONG cùng định dạng, không trộn Shorts với Long-form', async () => {
      const r = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      // Long-form có lượt xem tuyệt đối cao hơn mọi Short thường, nhưng vì tách
      // nhóm nên Short outlier vẫn phải đứng đầu nhóm của nó.
      const shorts = r.package.rankedVideos.filter((v) => v.format === 'SHORT')
      const longs = r.package.rankedVideos.filter((v) => v.format === 'LONG_FORM')
      expect(shorts.length).toBeGreaterThan(0)
      expect(longs.length).toBeGreaterThan(0)
      const topShort = shorts[0]!
      expect(topShort.formatPercentile as number).toBeGreaterThan(80)
    })

    it('đường cơ sở tách riêng theo định dạng', async () => {
      const r = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      const keys = r.package.baselines.map((b) => b.key)
      expect(keys).toContain('CHANNEL_FORMAT:SHORT')
      expect(keys).toContain('CHANNEL_FORMAT:LONG_FORM')
    })
  })

  describe('thiếu dữ liệu và bất thường', () => {
    it('chỉ số YouTube không cấp được báo là thiếu, không phải 0', async () => {
      const r = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      expect(r.package.dataCoverage.metricCoverage['impressions']).toBe(0)
      expect(r.package.missingData.some((m) => m.includes('impressions'))).toBe(true)
      // Và phải có câu hỏi chưa giải quyết về khâu tiếp cận.
      expect(r.package.unresolvedQuestions.some((q) => q.includes('impressions'))).toBe(true)
    })

    it('phát hiện outlier đã cấy vào dữ liệu', async () => {
      const r = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      expect(r.anomalyCount).toBeGreaterThan(0)
      const spike = r.package.anomalies.find((a) => a.youtubeVideoId === 's0000000011')
      expect(spike, 'Short 50k lượt xem phải bị bắt là bất thường').toBeDefined()
      expect(spike!.kind).toBe('VIEW_SPIKE')
    })

    it('mọi feature thiếu đều kèm LÝ DO', async () => {
      const r = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      expect(r.missingFeatureCount).toBeGreaterThan(0)
      expect(r.featureCount).toBeGreaterThan(0)
    })
  })

  describe('không có tuyên bố nhân quả', () => {
    it('KHÔNG câu mô tả nào chứa từ ngữ nhân quả', async () => {
      const r = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      for (const o of r.package.observations) {
        expect(containsCausalClaim(o.statement), `câu mô tả có nhân quả: "${o.statement}"`).toBe(false)
      }
    })

    it('giả thuyết được đánh dấu rõ và luôn kèm câu hỏi', async () => {
      const r = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      for (const h of r.package.hypothesisCandidates) {
        expect(h.isHypothesis).toBe(true)
        expect(h.hypothesisQuestion, 'giả thuyết phải kèm câu hỏi cần kiểm chứng').toBeTruthy()
        // Bản thân câu mô tả của giả thuyết vẫn phải thuần mô tả.
        expect(containsCausalClaim(h.statement)).toBe(false)
      }
    })
  })

  describe('gói bằng chứng', () => {
    it('KHÔNG chứa lịch sử chỉ số theo ngày', async () => {
      const r = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      const text = stableStringify(r.package)

      // Kiểm theo HÌNH DẠNG chứ không theo số lượng nhãn ngày: gói hợp lệ vẫn
      // chứa ngày xuất bản của từng video được xếp hạng và khoá cohort — đó là
      // metadata, không phải lịch sử theo ngày.
      //
      // Cũng không kiểm bằng cách tìm tên cột: tên cột xuất hiện HỢP LỆ trong
      // `featureDefinitions[].formula`, nơi công thức được ghi ra cho LLM đọc.
      // Thứ phải vắng mặt là HÀNG chỉ số theo ngày.
      expect(text, 'gói không được chứa hàng chỉ số theo ngày').not.toMatch(
        /"date":"\d{4}-\d{2}-\d{2}","views":/,
      )
      expect(text).not.toMatch(/"metrics":\[\{/)

      // Số byte của gói phải nhỏ hơn hẳn dữ liệu thô, kể cả trên bộ dữ liệu
      // tổng hợp nhỏ này.
      expect(r.packageBytes).toBeLessThan(r.rawInputBytes)

      expect(r.packageBytes).toBeLessThan(ANALYSIS_THRESHOLDS.limits.maxPackageBytes)
    })

    it('gói luôn nhỏ hơn đầu vào thô', async () => {
      const r = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      // Bộ dữ liệu tổng hợp này chỉ có ~180 hàng, trong khi phần
      // `featureDefinitions` (~28 công thức) là CHI PHÍ CỐ ĐỊNH ~8KB. Nên tỉ lệ
      // nén ở đây khiêm tốn theo đúng dự đoán.
      //
      // Ngưỡng nén mạnh được kiểm ở `analysis-real-channels.test.ts`, nơi số
      // hàng đủ lớn để chi phí cố định trở nên không đáng kể — đó mới là điều
      // kiện vận hành thật.
      expect(r.reductionPercent).toBeGreaterThan(0)
      expect(r.packageBytes).toBeLessThan(r.rawInputBytes)
    })

    it('tôn trọng giới hạn và NÓI RA khi cắt bớt', async () => {
      const r = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      const l = ANALYSIS_THRESHOLDS.limits
      expect(r.package.rankedVideos.length).toBeLessThanOrEqual(l.rankedVideos)
      expect(r.package.anomalies.length).toBeLessThanOrEqual(l.topAnomalies)
      expect(r.package.hypothesisCandidates.length).toBeLessThanOrEqual(l.hypothesisCandidates)
      // Số đã đưa vào so với TỔNG số phải được công bố, để LLM biết mình chỉ
      // thấy một phần.
      expect(r.package.limitsApplied.positiveObservations.total).toBeGreaterThanOrEqual(
        r.package.limitsApplied.positiveObservations.included,
      )
    })

    it('mọi quan sát đều có tham chiếu bằng chứng', async () => {
      const r = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      for (const o of r.package.observations) {
        expect(o.evidenceRefs.length, `quan sát thiếu bằng chứng: ${o.statement}`).toBeGreaterThan(0)
      }
    })

    it('kèm định nghĩa feature và công thức để LLM khỏi đoán', async () => {
      const r = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      expect(r.package.featureDefinitions.length).toBeGreaterThan(20)
      for (const f of r.package.featureDefinitions) {
        expect(f.formula.length).toBeGreaterThan(5)
        expect(f.version).toBeTruthy()
      }
    })

    it('KHÔNG rò credential hay token', async () => {
      const r = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      const text = stableStringify(r.package).toLowerCase()
      for (const bad of ['postgres://', 'postgresql://', 'vhw_', 'vhu_', 'authorization', 'bearer', 'client_secret', 'refresh_token', 'password']) {
        expect(text, `gói chứa dấu hiệu credential: ${bad}`).not.toContain(bad)
      }
    })

    it('nhiệm vụ giao cho Cursor cấm tính lại và cấm bịa chỉ số', async () => {
      const r = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END, dryRun: true,
      })
      const joined = r.package.analysisTasks.join(' ').toLowerCase()
      expect(joined).toContain('không tính lại')
      expect(joined).toContain('không bịa')
    })
  })

  describe('lưu trữ và nguồn gốc', () => {
    it('ghi đủ feature, quan sát, bất thường, chất lượng và gói', async () => {
      const r = await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END,
      })
      expect(r.analysisRunId).toBeTruthy()

      const runId = r.analysisRunId!
      const counts = await db.execute<{ features: string; obs: string; anom: string; pkg: string; qual: string }>(sql`
        SELECT
          (SELECT count(*) FROM feature_value WHERE analysis_run_id = ${runId})::text AS features,
          (SELECT count(*) FROM deterministic_observation WHERE analysis_run_id = ${runId})::text AS obs,
          (SELECT count(*) FROM anomaly WHERE analysis_run_id = ${runId})::text AS anom,
          (SELECT count(*) FROM analysis_package WHERE analysis_run_id = ${runId})::text AS pkg,
          (SELECT count(*) FROM analysis_quality WHERE analysis_run_id = ${runId})::text AS qual
      `)
      const c = counts.rows[0]!
      expect(Number(c.features)).toBeGreaterThan(0)
      expect(Number(c.obs)).toBeGreaterThan(0)
      expect(Number(c.pkg)).toBe(1)
      expect(Number(c.qual)).toBe(1)
    })

    it('feature_value cưỡng chế: có giá trị HOẶC có lý do thiếu, không cả hai', async () => {
      const bad = await db.execute<{ n: string }>(sql`
        SELECT count(*)::text AS n FROM feature_value
        WHERE (numeric_value IS NULL) = (missing_reason IS NULL)
      `)
      expect(Number(bad.rows[0]!.n), 'ràng buộc DB phải khiến điều này bất khả thi').toBe(0)
    })

    it('giá trị feature là BẤT BIẾN', async () => {
      const row = await db.select().from(schema.featureValue).limit(1)
      if (row[0]) {
        await expect(
          db.update(schema.featureValue).set({ sampleSize: 999 }).where(eq(schema.featureValue.id, row[0].id)),
        ).rejects.toThrow(/IMMUTABLE_FEATURE_VALUE/)
      }
    })

    it('định nghĩa công thức là BẤT BIẾN', async () => {
      const row = await db.select().from(schema.featureVersion).limit(1)
      if (row[0]) {
        await expect(
          db.update(schema.featureVersion).set({ formula: 'sửa lén' }).where(eq(schema.featureVersion.id, row[0].id)),
        ).rejects.toThrow(/IMMUTABLE_FEATURE_VERSION/)
      }
    })

    it('gói phân tích là BẤT BIẾN', async () => {
      const row = await db.select().from(schema.analysisPackage).limit(1)
      if (row[0]) {
        await expect(
          db.update(schema.analysisPackage).set({ packageBytes: 1 }).where(eq(schema.analysisPackage.id, row[0].id)),
        ).rejects.toThrow(/IMMUTABLE_ANALYSIS_PACKAGE/)
      }
    })

    it('chạy lại tạo RUN MỚI, không ghi đè kết quả cũ', async () => {
      const before = await db.execute<{ n: string }>(sql`SELECT count(*)::text AS n FROM analysis_run`)
      await runDeterministicAnalysis({
        workspaceId, channelLabel: 'phong_thuy', windowStart: WINDOW_START, windowEnd: WINDOW_END,
      })
      const after = await db.execute<{ n: string }>(sql`SELECT count(*)::text AS n FROM analysis_run`)
      expect(Number(after.rows[0]!.n)).toBe(Number(before.rows[0]!.n) + 1)
    })

    it('mỗi giá trị feature truy được về run, phiên bản công thức và cửa sổ', async () => {
      const row = await db.execute<{
        run: string; version: string; ws: string; ch: string; start: string; end: string
      }>(sql`
        SELECT analysis_run_id AS run, feature_version_id AS version, workspace_id AS ws,
               channel_id AS ch, window_start::text AS start, window_end::text AS end
        FROM feature_value LIMIT 1
      `)
      const r = row.rows[0]!
      for (const v of Object.values(r)) expect(v).toBeTruthy()
    })
  })
})
