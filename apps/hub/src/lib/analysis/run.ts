import { createHash } from 'node:crypto'

import { and, eq, sql } from 'drizzle-orm'

import { getDb, withTransaction, type Executor } from '@/db/client'
import * as schema from '@/db/schema'
import {
  ANALYSIS_ALGORITHM_KEY,
  ANALYSIS_ALGORITHM_VERSION,
  ANALYSIS_THRESHOLDS,
  comparisonFormat,
  confidenceBandFor,
  durationBucket,
  publishHourBucket,
} from './config'
import {
  anomalyScoreFeature,
  baselineDeltaFeature,
  confidenceScore,
  impressionCtrFeature,
  metricCoverageScore,
  percentileFeature,
  performanceStability,
  ratePerThousand,
  videoAgeDays,
  weightedFeature,
  windowSum,
  addDays,
  daysBetween,
  type DailyMetric,
  type FeatureResult,
  type VideoInput,
} from './compute'
import { FEATURE_SPECS, featureSpec } from './features'
import {
  bottomPerformers,
  cohortTrend,
  formatComparison,
  publishTimeComparison,
  signalCombinations,
  topPerformers,
  type CohortStat,
  type Observation,
  type VideoFeatureRow,
} from './observations'
import { buildPackage, hashPackage, packageBytes, stableStringify, type AnalysisPackage } from './package'
import { median, modifiedZScore, percentileRank, round } from './stats'

/**
 * Điều phối phân tích tất định cho MỘT kênh trong MỘT cửa sổ.
 *
 * Luồng: đọc chỉ số đã chuẩn hoá -> tính feature -> dựng đường cơ sở -> sinh
 * quan sát và bất thường -> nén thành gói -> ghi tất cả kèm nguồn gốc đầy đủ.
 *
 * Không có lời gọi LLM nào ở đây. Đó là điểm mấu chốt: khi Cursor được gọi ở
 * Phase 4, mọi thứ tính được đã tính xong rồi.
 */

export interface RunAnalysisParams {
  workspaceId: string
  channelLabel: string
  windowStart: string
  windowEnd: string
  /** Chỉ tính, không ghi — dùng cho test tính tất định. */
  dryRun?: boolean
}

export interface RunAnalysisResult {
  analysisRunId: string | null
  channelId: string
  channelLabel: string
  package: AnalysisPackage
  packageHash: string
  packageBytes: number
  rawInputBytes: number
  reductionPercent: number
  featureCount: number
  missingFeatureCount: number
  observationCount: number
  anomalyCount: number
}

interface ChannelRow {
  id: string
  label: string
  title: string
  reportingTimezone: string
  youtubeChannelId: string
}

export async function runDeterministicAnalysis(
  params: RunAnalysisParams,
): Promise<RunAnalysisResult> {
  const db = getDb()

  const channels = await db
    .select({
      id: schema.channel.id,
      label: schema.channel.label,
      title: schema.channel.title,
      reportingTimezone: schema.channel.reportingTimezone,
      youtubeChannelId: schema.channel.youtubeChannelId,
    })
    .from(schema.channel)
    .where(
      and(
        eq(schema.channel.workspaceId, params.workspaceId),
        eq(schema.channel.label, params.channelLabel),
      ),
    )
    .limit(1)

  const channel = channels[0] as ChannelRow | undefined
  if (!channel) throw new Error(`Không tìm thấy kênh "${params.channelLabel}".`)

  // --- Đọc dữ liệu đã chuẩn hoá -------------------------------------------
  //
  // Sắp xếp TƯỜNG MINH theo (youtube_video_id, date). Không có ORDER BY, thứ tự
  // hàng do kế hoạch truy vấn quyết định và có thể đổi giữa hai lần chạy — đủ
  // để làm hash gói đổi dù dữ liệu y hệt.
  const videoRows = await db.execute<{
    id: string
    youtube_video_id: string
    title: string
    published_at: string
    publish_date: string
    published_hour_local: number | null
    duration_seconds: number | null
    format: string
  }>(sql`
    SELECT v.id, v.youtube_video_id, v.title, v.published_at::text,
           (v.published_at AT TIME ZONE ${channel.reportingTimezone})::date::text AS publish_date,
           v.published_hour_local, v.duration_seconds, v.format::text
    FROM video v
    WHERE v.channel_id = ${channel.id}
      AND (v.published_at AT TIME ZONE ${channel.reportingTimezone})::date <= ${params.windowEnd}::date
    ORDER BY v.youtube_video_id
  `)

  /**
   * KHÔNG chặn dưới bằng `windowStart`.
   *
   * Cửa sổ theo TUỔI bắt đầu từ ngày ĐĂNG của từng video, không phải từ đầu cửa
   * sổ phân tích. Một video đăng trước `windowStart` vẫn cần đủ N ngày đầu của
   * chính nó để `views_d7` đúng.
   *
   * Bản đầu lọc `m.date >= windowStart`, nên với video đăng 2026-06-28 và cửa
   * sổ 2026-07-01..07-31, `views_d7` chỉ cộng 4/7 ngày và trả về một con số
   * NHỎ HƠN THỰC TẾ mà không có dấu hiệu gì — sai âm thầm, tệ hơn nhiều so với
   * báo thiếu. Chặn trên vẫn giữ để không nhìn thấy tương lai của cửa sổ.
   */
  const metricRows = await db.execute<{
    video_id: string
    date: string
    views: string | null
    estimated_minutes_watched: string | null
    average_view_duration_seconds: string | null
    average_view_percentage: string | null
    impressions: string | null
    impression_ctr: string | null
    likes: number | null
    dislikes: number | null
    comments: number | null
    shares: number | null
    subscribers_gained: number | null
    subscribers_lost: number | null
  }>(sql`
    SELECT m.video_id, m.date::text, m.views::text, m.estimated_minutes_watched::text,
           m.average_view_duration_seconds::text, m.average_view_percentage::text,
           m.impressions::text, m.impression_ctr::text,
           m.likes, m.dislikes, m.comments, m.shares, m.subscribers_gained, m.subscribers_lost
    FROM video_daily_metric m
    JOIN video v ON v.id = m.video_id
    WHERE v.channel_id = ${channel.id}
      AND m.date <= ${params.windowEnd}::date
    ORDER BY v.youtube_video_id, m.date
  `)

  const channelMetricRows = await db.execute<{
    date: string
    views: string | null
    estimated_minutes_watched: string | null
    subscribers_gained: number | null
    subscribers_lost: number | null
  }>(sql`
    SELECT date::text, views::text, estimated_minutes_watched::text,
           subscribers_gained, subscribers_lost
    FROM channel_daily_metric
    WHERE channel_id = ${channel.id}
      AND date BETWEEN ${params.windowStart}::date AND ${params.windowEnd}::date
    ORDER BY date
  `)

  const num = (v: string | number | null): number | null => {
    if (v === null || v === undefined) return null
    const n = typeof v === 'number' ? v : Number(v)
    return Number.isFinite(n) ? n : null
  }

  const metricsByVideo = new Map<string, DailyMetric[]>()
  for (const r of metricRows.rows) {
    const list = metricsByVideo.get(r.video_id) ?? []
    list.push({
      date: r.date,
      views: num(r.views),
      estimatedMinutesWatched: num(r.estimated_minutes_watched),
      averageViewDurationSeconds: num(r.average_view_duration_seconds),
      averageViewPercentage: num(r.average_view_percentage),
      impressions: num(r.impressions),
      impressionCtr: num(r.impression_ctr),
      likes: num(r.likes),
      dislikes: num(r.dislikes),
      comments: num(r.comments),
      shares: num(r.shares),
      subscribersGained: num(r.subscribers_gained),
      subscribersLost: num(r.subscribers_lost),
    })
    metricsByVideo.set(r.video_id, list)
  }

  const videos: VideoInput[] = videoRows.rows.map((v) => ({
    id: v.id,
    youtubeVideoId: v.youtube_video_id,
    title: v.title,
    publishedAt: v.published_at,
    publishDate: v.publish_date,
    publishedHourLocal: v.published_hour_local,
    publishedWeekdayLocal: weekdayOf(v.publish_date),
    durationSeconds: v.duration_seconds,
    // Suy từ thời lượng, không tin nhãn đã lưu -- xem comparisonFormat().
    format: comparisonFormat(v.duration_seconds, v.format),
    metrics: metricsByVideo.get(v.id) ?? [],
  }))

  /**
   * Kích thước ĐẦU VÀO THÔ để so sánh mức nén.
   *
   * Đo trên chính dữ liệu mà cách làm ngây thơ sẽ nhồi vào prompt: toàn bộ hàng
   * chỉ số theo ngày cộng metadata video. Đây là mẫu số trung thực cho con số
   * "giảm bao nhiêu phần trăm".
   */
  const rawInputBytes = Buffer.byteLength(
    stableStringify({
      videos: videos.map((v) => ({
        id: v.youtubeVideoId,
        title: v.title,
        publishedAt: v.publishedAt,
        durationSeconds: v.durationSeconds,
        format: v.format,
        metrics: v.metrics,
      })),
      channelDaily: channelMetricRows.rows,
    }),
    'utf8',
  )

  // --- Tính feature --------------------------------------------------------
  const featureRows: VideoFeatureRow[] = []
  const rawFeatures = new Map<string, Map<string, FeatureResult>>()

  for (const video of videos) {
    const f = new Map<string, FeatureResult>()

    f.set('publish_hour_local', numOrMissing(video.publishedHourLocal))
    f.set('publish_weekday', numOrMissing(video.publishedWeekdayLocal))
    f.set('video_age_days', { value: videoAgeDays(video, params.windowEnd), sampleSize: 1 })
    f.set('duration_seconds', numOrMissing(video.durationSeconds))

    for (const d of ANALYSIS_THRESHOLDS.performanceWindows) {
      f.set(`views_d${d}`, windowSum(video, d, 'views', params.windowEnd))
      f.set(
        `watch_minutes_d${d}`,
        windowSum(video, d, 'estimatedMinutesWatched', params.windowEnd),
      )
    }

    const viewsD7 = f.get('views_d7')!
    const watchD7 = f.get('watch_minutes_d7')!
    f.set(
      'views_velocity_d7',
      viewsD7.value !== undefined
        ? { value: round(viewsD7.value / 7, 4)!, sampleSize: viewsD7.sampleSize }
        : { missing: viewsD7.missing!, sampleSize: viewsD7.sampleSize },
    )
    f.set(
      'watch_velocity_d7',
      watchD7.value !== undefined
        ? { value: round(watchD7.value / 7, 4)!, sampleSize: watchD7.sampleSize }
        : { missing: watchD7.missing!, sampleSize: watchD7.sampleSize },
    )

    f.set('avg_view_percentage', weightedFeature(video, 'averageViewPercentage'))
    f.set('avg_view_duration_seconds', weightedFeature(video, 'averageViewDurationSeconds'))
    f.set('like_rate_per_1k', ratePerThousand(video, 'likes', params.windowEnd))
    f.set('comment_rate_per_1k', ratePerThousand(video, 'comments', params.windowEnd))
    f.set(
      'subscriber_conversion_per_1k',
      ratePerThousand(video, 'subscribersGained', params.windowEnd, 'subscribersLost'),
    )
    f.set('impressions_total', windowSumAll(video, 'impressions'))
    f.set('impression_ctr', impressionCtrFeature(video))
    f.set('metric_coverage_score', metricCoverageScore(video))
    f.set('performance_stability', performanceStability(video))
    f.set('confidence_score', confidenceScore(video, params.windowEnd))

    rawFeatures.set(video.id, f)
  }

  // Khoảng cách giữa các lần đăng — cần thứ tự thời gian toàn kênh.
  const byPublish = [...videos].sort(
    (a, b) => a.publishDate.localeCompare(b.publishDate) || a.youtubeVideoId.localeCompare(b.youtubeVideoId),
  )
  for (let i = 0; i < byPublish.length; i++) {
    const cur = byPublish[i]!
    const prev = i > 0 ? byPublish[i - 1] : undefined
    rawFeatures
      .get(cur.id)!
      .set(
        'gap_since_previous_upload_days',
        prev
          ? { value: daysBetween(prev.publishDate, cur.publishDate), sampleSize: 1 }
          : { missing: 'INSUFFICIENT_SAMPLE', sampleSize: 0 },
      )
  }

  // --- Đường cơ sở ---------------------------------------------------------
  //
  // Tách theo ĐỊNH DẠNG ở mọi nhóm so sánh. Trộn Shorts với long-form sẽ cho ra
  // phân vị vô nghĩa: hai định dạng có cơ chế phân phối và thang lượt xem khác
  // hẳn nhau.
  const valueOf = (videoId: string, key: string): number | null =>
    rawFeatures.get(videoId)?.get(key)?.value ?? null

  const allViewsD7 = videos.map((v) => valueOf(v.id, 'views_d7')).filter((v): v is number => v !== null)
  const byFormat = new Map<string, number[]>()
  for (const v of videos) {
    const val = valueOf(v.id, 'views_d7')
    if (val === null) continue
    const list = byFormat.get(v.format) ?? []
    list.push(val)
    byFormat.set(v.format, list)
  }

  const matureViewsByFormat = new Map<string, number[]>()
  for (const v of videos) {
    const val = valueOf(v.id, 'views_d7')
    if (val === null) continue
    if (videoAgeDays(v, params.windowEnd) < ANALYSIS_THRESHOLDS.matureVideoAgeDays) continue
    const list = matureViewsByFormat.get(v.format) ?? []
    list.push(val)
    matureViewsByFormat.set(v.format, list)
  }

  const recentCutoff = addDays(params.windowEnd, -ANALYSIS_THRESHOLDS.cohortFortnightDays)
  const recentViewsByFormat = new Map<string, number[]>()
  for (const v of videos) {
    const val = valueOf(v.id, 'views_d7')
    if (val === null || v.publishDate < recentCutoff) continue
    const list = recentViewsByFormat.get(v.format) ?? []
    list.push(val)
    recentViewsByFormat.set(v.format, list)
  }

  const cohortKeyOf = (v: VideoInput): string => {
    const offset = daysBetween(v.publishDate, params.windowEnd)
    const index = Math.floor(offset / ANALYSIS_THRESHOLDS.cohortFortnightDays)
    const end = addDays(params.windowEnd, -index * ANALYSIS_THRESHOLDS.cohortFortnightDays)
    const start = addDays(end, -(ANALYSIS_THRESHOLDS.cohortFortnightDays - 1))
    return `${start}..${end}`
  }

  const cohortViews = new Map<string, number[]>()
  for (const v of videos) {
    const val = valueOf(v.id, 'views_d7')
    if (val === null) continue
    const key = `${cohortKeyOf(v)}|${v.format}`
    const list = cohortViews.get(key) ?? []
    list.push(val)
    cohortViews.set(key, list)
  }

  const retentionByFormat = new Map<string, number[]>()
  for (const v of videos) {
    const val = valueOf(v.id, 'avg_view_percentage')
    if (val === null) continue
    const list = retentionByFormat.get(v.format) ?? []
    list.push(val)
    retentionByFormat.set(v.format, list)
  }

  // --- Feature phụ thuộc nhóm so sánh --------------------------------------
  const retentionPercentiles = new Map<string, number>()
  for (const v of videos) {
    const f = rawFeatures.get(v.id)!
    const viewsD7Value = valueOf(v.id, 'views_d7')

    f.set(
      'channel_percentile_views_d7',
      viewsD7Value === null
        ? { missing: 'DEPENDENCY_MISSING', sampleSize: 0 }
        : percentileFeature(viewsD7Value, allViewsD7),
    )
    f.set(
      'format_percentile_views_d7',
      viewsD7Value === null
        ? { missing: 'DEPENDENCY_MISSING', sampleSize: 0 }
        : percentileFeature(viewsD7Value, byFormat.get(v.format) ?? []),
    )
    f.set(
      'cohort_percentile_views_d7',
      viewsD7Value === null
        ? { missing: 'DEPENDENCY_MISSING', sampleSize: 0 }
        : percentileFeature(viewsD7Value, cohortViews.get(`${cohortKeyOf(v)}|${v.format}`) ?? []),
    )
    f.set(
      'recent_baseline_delta_views_d7',
      viewsD7Value === null
        ? { missing: 'DEPENDENCY_MISSING', sampleSize: 0 }
        : baselineDeltaFeature(viewsD7Value, recentViewsByFormat.get(v.format) ?? []),
    )
    f.set(
      'mature_baseline_delta_views_d7',
      viewsD7Value === null
        ? { missing: 'DEPENDENCY_MISSING', sampleSize: 0 }
        : baselineDeltaFeature(viewsD7Value, matureViewsByFormat.get(v.format) ?? []),
    )
    f.set(
      'anomaly_score_views_d7',
      viewsD7Value === null
        ? { missing: 'DEPENDENCY_MISSING', sampleSize: 0 }
        : anomalyScoreFeature(viewsD7Value, byFormat.get(v.format) ?? []),
    )

    const retention = valueOf(v.id, 'avg_view_percentage')
    const group = retentionByFormat.get(v.format) ?? []
    if (retention !== null && group.length >= ANALYSIS_THRESHOLDS.minSampleForPercentile) {
      const pr = percentileRank(retention, group)
      if (pr !== null) retentionPercentiles.set(v.id, round(pr, 3)!)
    }

    featureRows.push({
      video: v,
      viewsD7: valueOf(v.id, 'views_d7'),
      viewsD1: valueOf(v.id, 'views_d1'),
      watchMinutesD7: valueOf(v.id, 'watch_minutes_d7'),
      avgViewPercentage: valueOf(v.id, 'avg_view_percentage'),
      avgViewDurationSeconds: valueOf(v.id, 'avg_view_duration_seconds'),
      likeRatePer1k: valueOf(v.id, 'like_rate_per_1k'),
      commentRatePer1k: valueOf(v.id, 'comment_rate_per_1k'),
      subsPer1k: valueOf(v.id, 'subscriber_conversion_per_1k'),
      impressions: valueOf(v.id, 'impressions_total'),
      impressionCtr: valueOf(v.id, 'impression_ctr'),
      channelPercentileViewsD7: valueOf(v.id, 'channel_percentile_views_d7'),
      formatPercentileViewsD7: valueOf(v.id, 'format_percentile_views_d7'),
      cohortPercentileViewsD7: valueOf(v.id, 'cohort_percentile_views_d7'),
      recentBaselineDelta: valueOf(v.id, 'recent_baseline_delta_views_d7'),
      matureBaselineDelta: valueOf(v.id, 'mature_baseline_delta_views_d7'),
      anomalyScore: valueOf(v.id, 'anomaly_score_views_d7'),
      confidence: valueOf(v.id, 'confidence_score') ?? 0,
      stability: valueOf(v.id, 'performance_stability'),
      coverage: valueOf(v.id, 'metric_coverage_score'),
    })
  }

  // --- Chất lượng dữ liệu --------------------------------------------------
  const windowDays = daysBetween(params.windowStart, params.windowEnd) + 1
  const videosPublishedInWindow = videos.filter(
    (v) => v.publishDate >= params.windowStart && v.publishDate <= params.windowEnd,
  ).length
  const observedDates = new Set(channelMetricRows.rows.map((r) => r.date))
  const missingDates: string[] = []
  for (let i = 0; i < windowDays; i++) {
    const d = addDays(params.windowStart, i)
    if (!observedDates.has(d)) missingDates.push(d)
  }

  const metricCoverage = computeMetricCoverage(videos)
  const videosWithMetrics = videos.filter((v) => v.metrics.length > 0).length
  const videosImmature = videos.filter(
    (v) => videoAgeDays(v, params.windowEnd) < ANALYSIS_THRESHOLDS.matureVideoAgeDays,
  ).length

  const coverageMean =
    Object.values(metricCoverage).reduce((s, v) => s + v, 0) /
    Math.max(1, Object.values(metricCoverage).length)
  const dateCompleteness = (windowDays - missingDates.length) / windowDays
  const sampleAdequacy = Math.min(1, videosWithMetrics / 20)
  const maturity = videos.length ? 1 - videosImmature / videos.length : 0
  const w = ANALYSIS_THRESHOLDS.confidenceWeights
  const channelConfidence = round(
    Math.max(
      0,
      Math.min(
        1,
        w.metricCoverage * coverageMean +
          w.dateCompleteness * dateCompleteness +
          w.sampleSize * sampleAdequacy +
          w.maturity * maturity,
      ),
    ),
    4,
  )!

  // --- Quan sát ------------------------------------------------------------
  const windowLabel = `${params.windowStart}..${params.windowEnd}`
  const observations: Observation[] = [
    ...topPerformers(channel.id, featureRows, ANALYSIS_THRESHOLDS.limits.topPositiveObservations),
    ...bottomPerformers(channel.id, featureRows, ANALYSIS_THRESHOLDS.limits.topNegativeObservations),
    ...signalCombinations(channel.id, featureRows, retentionPercentiles),
  ]

  const cohortStats: CohortStat[] = [...cohortViews.entries()]
    .map(([key, vals]) => {
      const [range, format] = key.split('|')
      return {
        key: `${range} (${format})`,
        kind: 'PUBLISH_FORTNIGHT',
        videoCount: vals.length,
        medianViews: round(median(vals)),
      }
    })
    .sort((a, b) => b.key.localeCompare(a.key))

  // So sánh hai cohort liền kề CÙNG ĐỊNH DẠNG.
  const byFormatCohorts = new Map<string, CohortStat[]>()
  for (const [key, vals] of cohortViews.entries()) {
    const [range, format] = key.split('|')
    const list = byFormatCohorts.get(format!) ?? []
    list.push({
      key: range!,
      kind: 'PUBLISH_FORTNIGHT',
      videoCount: vals.length,
      medianViews: round(median(vals)),
    })
    byFormatCohorts.set(format!, list)
  }
  for (const [format, list] of [...byFormatCohorts.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    const sorted = [...list].sort((a, b) => b.key.localeCompare(a.key))
    if (sorted.length >= 2) {
      const obs = cohortTrend(channel.id, sorted[0]!, sorted[1]!, `${windowLabel} (${format})`)
      if (obs) observations.push(obs)
    }
  }

  const fmtObs = formatComparison(
    channel.id,
    byFormat.get('SHORT') ?? [],
    byFormat.get('LONG_FORM') ?? [],
    windowLabel,
  )
  if (fmtObs) observations.push(fmtObs)

  // So sánh giờ đăng TÁCH RIÊNG theo định dạng.
  //
  // Gộp chung sẽ cho kết luận đảo ngược: nếu khung tối chủ yếu là long-form
  // (lượt xem tuyệt đối cao hơn) còn khung sáng chủ yếu là Shorts, thì "khung
  // tối tốt hơn" thực chất chỉ phản ánh tỉ lệ định dạng, không phản ánh giờ đăng.
  for (const format of ['SHORT', 'LONG_FORM'] as const) {
    const hourBuckets = new Map<string, number[]>()
    for (const v of videos) {
      if (v.format !== format) continue
      const val = valueOf(v.id, 'views_d7')
      const bucket = publishHourBucket(v.publishedHourLocal)
      if (val === null || bucket === null) continue
      const list = hourBuckets.get(bucket) ?? []
      list.push(val)
      hourBuckets.set(bucket, list)
    }
    const timeObs = publishTimeComparison(channel.id, hourBuckets, `${windowLabel} (${format})`)
    if (timeObs) observations.push(timeObs)
  }

  // --- Bất thường ----------------------------------------------------------
  const anomalies = detectAnomalies(channel.id, featureRows, byFormat, params)

  // --- Gói -----------------------------------------------------------------
  const inputHash = createHash('sha256')
    .update(
      stableStringify({
        channel: channel.youtubeChannelId,
        window: windowLabel,
        videos: videos.map((v) => ({ id: v.youtubeVideoId, metrics: v.metrics })),
        channelDaily: channelMetricRows.rows,
        algorithmVersion: ANALYSIS_ALGORITHM_VERSION,
      }),
      'utf8',
    )
    .digest('hex')

  const rankedVideos = [...featureRows]
    .filter((r) => r.formatPercentileViewsD7 !== null)
    .sort(
      (a, b) =>
        (b.formatPercentileViewsD7 ?? 0) - (a.formatPercentileViewsD7 ?? 0) ||
        a.video.youtubeVideoId.localeCompare(b.video.youtubeVideoId),
    )
    .map((r) => ({
      youtubeVideoId: r.video.youtubeVideoId,
      title: r.video.title.slice(0, 120),
      format: r.video.format,
      durationSeconds: r.video.durationSeconds,
      publishedAt: r.video.publishedAt,
      publishHourLocal: r.video.publishedHourLocal,
      durationBucket: durationBucket(r.video.durationSeconds),
      viewsD7: r.viewsD7,
      formatPercentile: r.formatPercentileViewsD7,
      avgViewPercentage: r.avgViewPercentage,
      likeRatePer1k: r.likeRatePer1k,
      commentRatePer1k: r.commentRatePer1k,
      subsPer1k: r.subsPer1k,
      anomalyScore: r.anomalyScore,
      confidence: r.confidence,
    }))

  const missingData: string[] = []
  for (const [key, cov] of Object.entries(metricCoverage)) {
    if (cov === 0) missingData.push(`${key}: YouTube không cấp chỉ số này cho kênh (0% độ phủ).`)
    else if (cov < 0.9) missingData.push(`${key}: chỉ ${round(cov * 100, 1)}% số hàng có dữ liệu.`)
  }
  if (missingDates.length) {
    missingData.push(`${missingDates.length}/${windowDays} ngày không có chỉ số cấp kênh.`)
  }
  if (videosImmature) {
    missingData.push(
      `${videosImmature}/${videos.length} video chưa đủ ${ANALYSIS_THRESHOLDS.matureVideoAgeDays} ngày; ` +
        `các cửa sổ dài hơn tuổi của chúng để MISSING thay vì gán 0.`,
    )
  }

  const unresolvedQuestions: string[] = []
  if ((metricCoverage['impressions'] ?? 0) === 0) {
    unresolvedQuestions.push(
      'Không có impressions/CTR nên KHÔNG phân biệt được "ít người thấy" với "thấy nhưng không bấm". ' +
        'Mọi kết luận về khâu tiếp cận đều bị chặn ở đây.',
    )
  }
  if (videosImmature > videos.length / 2) {
    unresolvedQuestions.push(
      'Quá nửa số video chưa đủ chín; so sánh xu hướng giữa các cohort còn sơ bộ.',
    )
  }

  const pkg = buildPackage({
    scope: {
      workspaceId: params.workspaceId,
      channelId: channel.id,
      channelLabel: channel.label,
      channelTitle: channel.title,
      reportingTimezone: channel.reportingTimezone,
      windowStart: params.windowStart,
      windowEnd: params.windowEnd,
      analysisRunId: 'pending',
      inputHash,
    },
    channelSummary: {
      videos: videos.length,
      videosWithMetrics,
      shorts: (byFormat.get('SHORT') ?? []).length,
      longform: (byFormat.get('LONG_FORM') ?? []).length,
      channelViewsInWindow: channelMetricRows.rows.reduce((s, r) => s + (num(r.views) ?? 0), 0),
      medianViewsD7: round(median(allViewsD7)),
      // Chỉ đếm video ĐĂNG TRONG cửa sổ. Dùng tổng số video (gồm cả lịch sử
      // trước cửa sổ) sẽ thổi phồng tần suất lên nhiều lần.
      uploadsPerWeek: round((videosPublishedInWindow / windowDays) * 7, 2),
      videosPublishedInWindow,
    },
    dataCoverage: {
      videosTotal: videos.length,
      videosWithMetrics,
      videosImmature,
      metricRows: metricRows.rows.length,
      expectedDates: windowDays,
      observedDates: observedDates.size,
      // Chỉ liệt kê 10 ngày thiếu đầu tiên: danh sách đầy đủ có thể dài hàng
      // trăm dòng và không giúp LLM suy luận thêm.
      missingDates: missingDates.slice(0, 10),
      metricCoverage,
      revisedRows: 0,
    },
    confidence: {
      score: channelConfidence,
      band: confidenceBandFor(channelConfidence),
      drivers: {
        metricCoverage: round(coverageMean, 4)!,
        dateCompleteness: round(dateCompleteness, 4)!,
        sampleAdequacy: round(sampleAdequacy, 4)!,
        maturity: round(maturity, 4)!,
      },
    },
    baselines: buildBaselineList(byFormat, recentViewsByFormat, matureViewsByFormat),
    featureDefinitions: FEATURE_SPECS.map((f) => ({
      key: f.key,
      label: f.label,
      unit: f.unit,
      direction: f.direction,
      version: f.version,
      formula: f.formula,
    })),
    observations,
    anomalies: anomalies.map((a) => ({
      kind: a.kind,
      youtubeVideoId: a.youtubeVideoId,
      metricKey: a.metricKey,
      score: a.score,
      threshold: a.threshold,
      observedValue: a.observedValue,
      medianValue: a.medianValue,
      sampleSize: a.sampleSize,
      method: a.method,
    })),
    rankedVideos,
    cohortComparisons: cohortStats
      .slice(0, ANALYSIS_THRESHOLDS.limits.cohortSummaries)
      .map((c) => ({ key: c.key, kind: c.kind, videoCount: c.videoCount, medianViewsD7: c.medianViews })),
    formatComparison: fmtObs
      ? { statement: fmtObs.statement, metricValues: fmtObs.metricValues, limitations: fmtObs.limitations }
      : null,
    unresolvedQuestions,
    missingData,
  })

  const bytes = packageBytes(pkg)
  const reductionPercent = round(((rawInputBytes - bytes) / rawInputBytes) * 100, 3)!

  const featureCount = [...rawFeatures.values()].reduce(
    (s, m) => s + [...m.values()].filter((r) => r.value !== undefined).length,
    0,
  )
  const missingFeatureCount = [...rawFeatures.values()].reduce(
    (s, m) => s + [...m.values()].filter((r) => r.missing !== undefined).length,
    0,
  )

  if (params.dryRun) {
    return {
      analysisRunId: null,
      channelId: channel.id,
      channelLabel: channel.label,
      package: pkg,
      packageHash: hashPackage(pkg),
      packageBytes: bytes,
      rawInputBytes,
      reductionPercent,
      featureCount,
      missingFeatureCount,
      observationCount: observations.length,
      anomalyCount: anomalies.length,
    }
  }

  const persisted = await persist({
    params,
    channel,
    videos,
    rawFeatures,
    observations,
    anomalies,
    cohortStats,
    pkg,
    inputHash,
    rawInputBytes,
    bytes,
    reductionPercent,
    quality: {
      videosTotal: videos.length,
      videosWithMetrics,
      videosImmature,
      metricRows: metricRows.rows.length,
      expectedDates: windowDays,
      observedDates: observedDates.size,
      missingDates,
      metricCoverage,
      confidence: channelConfidence,
    },
  })

  return {
    analysisRunId: persisted.analysisRunId,
    channelId: channel.id,
    channelLabel: channel.label,
    package: persisted.pkg,
    packageHash: persisted.packageHash,
    packageBytes: persisted.packageBytes,
    rawInputBytes,
    reductionPercent: persisted.reductionPercent,
    featureCount,
    missingFeatureCount,
    observationCount: observations.length,
    anomalyCount: anomalies.length,
  }
}

// --- Hàm phụ trợ ------------------------------------------------------------

function numOrMissing(value: number | null): FeatureResult {
  return value === null ? { missing: 'METRIC_NOT_PROVIDED', sampleSize: 0 } : { value, sampleSize: 1 }
}

function windowSumAll(video: VideoInput, key: keyof DailyMetric): FeatureResult {
  if (video.metrics.length === 0) return { missing: 'NO_METRIC_ROWS', sampleSize: 0 }
  let sum = 0
  let n = 0
  for (const m of video.metrics) {
    const v = m[key]
    if (typeof v === 'number' && Number.isFinite(v)) {
      sum += v
      n++
    }
  }
  if (n === 0) return { missing: 'METRIC_NOT_PROVIDED', sampleSize: video.metrics.length }
  return { value: round(sum, 4)!, sampleSize: n }
}

function weekdayOf(isoDate: string): number {
  const dt = new Date(
    Date.UTC(+isoDate.slice(0, 4), +isoDate.slice(5, 7) - 1, +isoDate.slice(8, 10)),
  )
  return dt.getUTCDay()
}

function computeMetricCoverage(videos: VideoInput[]): Record<string, number> {
  const keys: Array<keyof DailyMetric> = [
    'views',
    'estimatedMinutesWatched',
    'averageViewDurationSeconds',
    'averageViewPercentage',
    'impressions',
    'impressionCtr',
    'likes',
    'comments',
    'shares',
    'subscribersGained',
    'subscribersLost',
  ]
  const total = videos.reduce((s, v) => s + v.metrics.length, 0)
  const out: Record<string, number> = {}
  for (const key of keys) {
    if (total === 0) {
      out[key] = 0
      continue
    }
    let present = 0
    for (const v of videos) for (const m of v.metrics) if (typeof m[key] === 'number') present++
    out[key] = round(present / total, 4)!
  }
  return out
}

function buildBaselineList(
  byFormat: Map<string, number[]>,
  recent: Map<string, number[]>,
  mature: Map<string, number[]>,
): AnalysisPackage['baselines'] {
  const out: AnalysisPackage['baselines'] = []
  for (const [format, values] of [...byFormat.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    out.push({
      key: `CHANNEL_FORMAT:${format}`,
      kind: 'CHANNEL_FORMAT',
      description: `Mọi video ${format} của kênh có views_d7`,
      videoCount: values.length,
      medianViewsD7: round(median(values)),
    })
  }
  for (const [format, values] of [...recent.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    out.push({
      key: `RECENT_WINDOW:${format}`,
      kind: 'RECENT_WINDOW',
      description: `Video ${format} đăng trong ${ANALYSIS_THRESHOLDS.cohortFortnightDays} ngày cuối`,
      videoCount: values.length,
      medianViewsD7: round(median(values)),
    })
  }
  for (const [format, values] of [...mature.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    out.push({
      key: `MATURE_VIDEOS:${format}`,
      kind: 'MATURE_VIDEOS',
      description: `Video ${format} đã đủ ${ANALYSIS_THRESHOLDS.matureVideoAgeDays} ngày tuổi`,
      videoCount: values.length,
      medianViewsD7: round(median(values)),
    })
  }
  return out
}

interface DetectedAnomaly {
  kind: 'VIEW_SPIKE' | 'VIEW_COLLAPSE'
  channelId: string
  videoId: string
  youtubeVideoId: string
  metricKey: string
  method: string
  score: number
  threshold: number
  observedValue: number
  medianValue: number
  madValue: number | null
  sampleSize: number
}

function detectAnomalies(
  channelId: string,
  rows: VideoFeatureRow[],
  byFormat: Map<string, number[]>,
  params: RunAnalysisParams,
): DetectedAnomaly[] {
  void params
  const out: DetectedAnomaly[] = []
  const threshold = ANALYSIS_THRESHOLDS.anomalyZThreshold

  for (const r of rows) {
    if (r.viewsD7 === null) continue
    const group = byFormat.get(r.video.format) ?? []
    if (group.length < ANALYSIS_THRESHOLDS.minSampleForAnomaly) continue
    const z = modifiedZScore(r.viewsD7, group)
    if (z === null || Math.abs(z) < threshold) continue

    out.push({
      kind: z > 0 ? 'VIEW_SPIKE' : 'VIEW_COLLAPSE',
      channelId,
      videoId: r.video.id,
      youtubeVideoId: r.video.youtubeVideoId,
      metricKey: 'views_d7',
      method: 'modified_zscore_mad',
      score: round(z, 4)!,
      threshold,
      observedValue: r.viewsD7,
      medianValue: round(median(group))!,
      madValue: null,
      sampleSize: group.length,
    })
  }

  return out.sort(
    (a, b) => Math.abs(b.score) - Math.abs(a.score) || a.youtubeVideoId.localeCompare(b.youtubeVideoId),
  )
}

// --- Ghi xuống DB -----------------------------------------------------------

interface PersistArgs {
  params: RunAnalysisParams
  channel: ChannelRow
  videos: VideoInput[]
  rawFeatures: Map<string, Map<string, FeatureResult>>
  observations: Observation[]
  anomalies: DetectedAnomaly[]
  cohortStats: CohortStat[]
  pkg: AnalysisPackage
  inputHash: string
  rawInputBytes: number
  bytes: number
  reductionPercent: number
  quality: {
    videosTotal: number
    videosWithMetrics: number
    videosImmature: number
    metricRows: number
    expectedDates: number
    observedDates: number
    missingDates: string[]
    metricCoverage: Record<string, number>
    confidence: number
  }
}

async function persist(args: PersistArgs): Promise<{
  analysisRunId: string
  pkg: AnalysisPackage
  packageHash: string
  packageBytes: number
  reductionPercent: number
}> {
  const { params, channel } = args
  const db = getDb()

  const algo = await ensureAlgorithm(db)
  const featureVersionIds = await ensureFeatureRegistry(db)

  // run_sequence tiếp theo cho (subject, algorithm_version).
  const seqRow = await db.execute<{ next: string }>(sql`
    SELECT COALESCE(MAX(run_sequence), 0) + 1 AS next
    FROM analysis_run
    WHERE subject_type = 'CHANNEL' AND subject_id = ${channel.id}
      AND algorithm_version_id = ${algo.versionId}
  `)
  const runSequence = Number(seqRow.rows[0]?.next ?? 1)

  return withTransaction(async (tx) => {
    const [run] = await tx
      .insert(schema.analysisRun)
      .values({
        workspaceId: params.workspaceId,
        channelId: channel.id,
        subjectType: 'CHANNEL',
        subjectId: channel.id,
        algorithmId: algo.algorithmId,
        algorithmVersionId: algo.versionId,
        runSequence,
        inputHash: args.inputHash,
        periodStart: params.windowStart,
        periodEnd: params.windowEnd,
        status: 'RUNNING',
        startedAt: new Date(),
      })
      .returning({ id: schema.analysisRun.id })

    const analysisRunId = run!.id

    // Gói mang analysisRunId thật, nên hash phải tính LẠI sau khi biết id.
    const finalPkg: AnalysisPackage = {
      ...args.pkg,
      scope: { ...args.pkg.scope, analysisRunId },
    }
    const finalHash = hashPackage(finalPkg)
    const finalBytes = packageBytes(finalPkg)

    // Kiểm lại trần SAU khi thay `analysisRunId` thật.
    //
    // Lúc dựng gói, id còn là chuỗi tạm "pending" (7 ký tự); UUID thật dài 36
    // ký tự, nên một gói sát ngưỡng có thể vượt trần đúng ở bước ghi — nơi
    // không còn ai kiểm.
    if (finalBytes > ANALYSIS_THRESHOLDS.limits.maxPackageBytes) {
      throw new Error(
        `Gói phân tích ${finalBytes} byte vượt trần ${ANALYSIS_THRESHOLDS.limits.maxPackageBytes} ` +
          `sau khi gắn analysis_run_id thật.`,
      )
    }
    const finalReduction = round(
      ((args.rawInputBytes - finalBytes) / args.rawInputBytes) * 100,
      3,
    )!

    // Giá trị feature
    const featureValues: Array<typeof schema.featureValue.$inferInsert> = []
    for (const [videoId, featureMap] of args.rawFeatures.entries()) {
      for (const [key, result] of featureMap.entries()) {
        const versionId = featureVersionIds.get(key)
        if (!versionId) continue
        featureValues.push({
          workspaceId: params.workspaceId,
          analysisRunId,
          featureVersionId: versionId,
          subjectType: 'VIDEO',
          channelId: channel.id,
          videoId,
          windowStart: params.windowStart,
          windowEnd: params.windowEnd,
          numericValue: result.value !== undefined ? String(result.value) : null,
          missingReason: result.missing ?? null,
          sampleSize: result.sampleSize,
        })
      }
    }
    for (let i = 0; i < featureValues.length; i += 500) {
      await tx.insert(schema.featureValue).values(featureValues.slice(i, i + 500))
    }

    // Quan sát + tham chiếu bằng chứng
    for (const o of args.observations) {
      const [row] = await tx
        .insert(schema.deterministicObservation)
        .values({
          workspaceId: params.workspaceId,
          analysisRunId,
          kind: o.kind,
          polarity: o.polarity,
          channelId: channel.id,
          videoId: o.videoId ?? null,
          statement: o.statement,
          metricValues: o.metricValues,
          baselineKind: o.baselineKind,
          baselineValue: o.baselineValue !== undefined && o.baselineValue !== null ? String(o.baselineValue) : null,
          observedValue: o.observedValue !== undefined && o.observedValue !== null ? String(o.observedValue) : null,
          deltaRatio: o.deltaRatio !== undefined && o.deltaRatio !== null ? String(o.deltaRatio) : null,
          percentile: o.percentile !== undefined && o.percentile !== null ? String(o.percentile) : null,
          windowStart: params.windowStart,
          windowEnd: params.windowEnd,
          confidence: String(o.confidence),
          confidenceBand: confidenceBandFor(o.confidence),
          sampleSize: o.sampleSize ?? null,
          limitations: o.limitations,
          isHypothesis: o.isHypothesis,
          hypothesisQuestion: o.hypothesisQuestion ?? null,
          rankScore: String(round(o.rankScore, 6) ?? 0),
          orderKey: o.orderKey,
        })
        .returning({ id: schema.deterministicObservation.id })

      if (o.evidence.length) {
        await tx.insert(schema.evidenceReference).values(
          o.evidence.map((e) => ({
            observationId: row!.id,
            refType: e.refType,
            refId: e.refId ?? null,
            refKey: e.refKey ?? null,
            detail: e.detail ?? {},
          })),
        )
      }
    }

    // Bất thường
    if (args.anomalies.length) {
      await tx.insert(schema.anomaly).values(
        args.anomalies.map((a) => ({
          workspaceId: params.workspaceId,
          analysisRunId,
          channelId: channel.id,
          videoId: a.videoId,
          kind: a.kind,
          method: a.method,
          score: String(a.score),
          threshold: String(a.threshold),
          observedValue: String(a.observedValue),
          medianValue: String(a.medianValue),
          madValue: a.madValue !== null ? String(a.madValue) : null,
          sampleSize: a.sampleSize,
          metricKey: a.metricKey,
          context: { format: 'per-format group' },
          windowStart: params.windowStart,
          windowEnd: params.windowEnd,
        })),
      )
    }

    // Tóm tắt cohort
    if (args.cohortStats.length) {
      await tx.insert(schema.cohortSummary).values(
        args.cohortStats.map((c) => ({
          workspaceId: params.workspaceId,
          analysisRunId,
          channelId: channel.id,
          kind: 'PUBLISH_FORTNIGHT' as const,
          cohortKey: c.key,
          videoCount: c.videoCount,
          medianViews: c.medianViews !== null ? String(c.medianViews) : null,
          windowStart: params.windowStart,
          windowEnd: params.windowEnd,
        })),
      )
    }

    // Chất lượng
    await tx.insert(schema.analysisQuality).values({
      workspaceId: params.workspaceId,
      analysisRunId,
      channelId: channel.id,
      videosTotal: args.quality.videosTotal,
      videosWithMetrics: args.quality.videosWithMetrics,
      videosImmature: args.quality.videosImmature,
      metricRows: args.quality.metricRows,
      expectedDates: args.quality.expectedDates,
      observedDates: args.quality.observedDates,
      missingDates: args.quality.missingDates,
      metricCoverage: args.quality.metricCoverage,
      confidence: String(args.quality.confidence),
      confidenceBand: confidenceBandFor(args.quality.confidence),
      limitations: args.pkg.missingData,
    })

    // Gói
    await tx.insert(schema.analysisPackage).values({
      workspaceId: params.workspaceId,
      analysisRunId,
      channelId: channel.id,
      schemaVersion: finalPkg.schemaVersion,
      payload: finalPkg,
      payloadHash: finalHash,
      packageBytes: finalBytes,
      rawInputBytes: args.rawInputBytes,
      reductionPercent: String(finalReduction),
    })

    await tx
      .update(schema.analysisRun)
      .set({ status: 'SUCCEEDED', finishedAt: new Date() })
      .where(eq(schema.analysisRun.id, analysisRunId))

    return {
      analysisRunId,
      pkg: finalPkg,
      packageHash: finalHash,
      packageBytes: finalBytes,
      reductionPercent: finalReduction,
    }
  })
}

async function ensureAlgorithm(db: Executor): Promise<{ algorithmId: string; versionId: string }> {
  const rows = await db.execute<{ algorithm_id: string; version_id: string }>(sql`
    SELECT a.id AS algorithm_id, av.id AS version_id
    FROM algorithm a
    JOIN algorithm_version av ON av.algorithm_id = a.id
    WHERE a.key = ${ANALYSIS_ALGORITHM_KEY} AND av.version = ${ANALYSIS_ALGORITHM_VERSION}
    LIMIT 1
  `)
  const row = rows.rows[0]
  if (!row) {
    throw new Error(
      `Chưa seed thuật toán ${ANALYSIS_ALGORITHM_KEY}@${ANALYSIS_ALGORITHM_VERSION}. Chạy npm run db:seed.`,
    )
  }
  return { algorithmId: row.algorithm_id, versionId: row.version_id }
}

/**
 * Đảm bảo danh mục feature có mặt trong DB và trả về ánh xạ key -> version id.
 *
 * Idempotent: chạy lại không tạo bản trùng. Đổi công thức thì `featureSpec.version`
 * phải tăng, và khi đó một hàng `feature_version` MỚI ra đời — giá trị cũ vẫn
 * trỏ về phiên bản đã sinh ra chúng.
 */
async function ensureFeatureRegistry(db: Executor): Promise<Map<string, string>> {
  const map = new Map<string, string>()

  for (const spec of FEATURE_SPECS) {
    await db
      .insert(schema.featureDefinition)
      .values({
        key: spec.key,
        label: spec.label,
        description: spec.description,
        unit: spec.unit,
        direction: spec.direction,
        subjectType: spec.subjectType,
      })
      .onConflictDoNothing()
  }

  const defs = await db.execute<{ id: string; key: string }>(sql`SELECT id, key FROM feature_definition`)
  const defByKey = new Map(defs.rows.map((d) => [d.key, d.id]))

  for (const spec of FEATURE_SPECS) {
    const defId = defByKey.get(spec.key)
    if (!defId) continue
    await db
      .insert(schema.featureVersion)
      .values({
        definitionId: defId,
        version: spec.version,
        formula: spec.formula,
        spec: spec.spec ?? {},
        requiredMetrics: spec.requiredMetrics,
        codeHash: createHash('sha256').update(spec.formula, 'utf8').digest('hex').slice(0, 32),
      })
      .onConflictDoNothing()
  }

  // Lấy ĐÚNG phiên bản mà danh mục code đang khai báo.
  //
  // Bản đầu lấy MỌI phiên bản rồi ghi đè theo key, nên khi một feature có từ hai
  // phiên bản trở lên, giá trị ghi xuống có thể trỏ về phiên bản CŨ tuỳ thứ tự
  // trả về của database — vừa mất nguồn gốc, vừa mất tính tất định.
  const versions = await db.execute<{
    id: string; key: string; version: string; formula: string; code_hash: string | null
  }>(sql`
    SELECT fv.id, fd.key, fv.version, fv.formula, fv.code_hash
    FROM feature_version fv JOIN feature_definition fd ON fd.id = fv.definition_id
  `)
  const byKeyVersion = new Map(
    versions.rows.map((v) => [`${v.key}@${v.version}`, { id: v.id, formula: v.formula, codeHash: v.code_hash }]),
  )
  for (const spec of FEATURE_SPECS) {
    const stored = byKeyVersion.get(`${spec.key}@${spec.version}`)
    if (!stored) {
      throw new Error(
        `Thiếu feature_version ${spec.key}@${spec.version} trong danh mục — không ghi kết quả ` +
          `với nguồn gốc không xác định.`,
      )
    }

    // Đối chiếu công thức ĐÃ LƯU với công thức trong code.
    //
    // `onConflictDoNothing` ở trên không cập nhật hàng đã có, nên nếu ai đó sửa
    // công thức mà QUÊN tăng version, database vẫn giữ công thức cũ trong khi
    // giá trị mới được tính bằng công thức mới — và mọi giá trị đó sẽ trỏ về
    // một nguồn gốc SAI. Bản thân `feature_version` là bất biến (trigger), nên
    // cách duy nhất đúng là tăng version. Dừng ở đây thay vì ghi dữ liệu có
    // nguồn gốc lệch.
    const expectedHash = createHash('sha256').update(spec.formula, 'utf8').digest('hex').slice(0, 32)
    if (stored.formula !== spec.formula || stored.codeHash !== expectedHash) {
      throw new Error(
        `Công thức của ${spec.key}@${spec.version} đã đổi nhưng version thì không.\n` +
          `  đã lưu: ${stored.formula}\n  trong code: ${spec.formula}\n` +
          `Tăng version của feature này; định nghĩa cũ là bất biến theo thiết kế.`,
      )
    }
    map.set(spec.key, stored.id)
  }
  return map
}

export { featureSpec }
