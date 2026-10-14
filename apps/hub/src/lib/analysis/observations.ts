import { ANALYSIS_THRESHOLDS, confidenceBandFor } from './config'
import { deltaRatio, median, round } from './stats'
import type { VideoInput } from './compute'

/**
 * Sinh quan sát TẤT ĐỊNH.
 *
 * Quy tắc bất di bất dịch của tầng này: `statement` chỉ MÔ TẢ cái đo được.
 * Mọi câu trả lời cho "vì sao" đều phải đi vào `hypothesisQuestion` với
 * `isHypothesis = true`. Ranh giới đó là toàn bộ lý do tồn tại của kiến trúc
 * "thuật toán trước, LLM sau": nếu tầng tất định bắt đầu suy đoán nguyên nhân,
 * LLM sẽ thừa hưởng suy đoán đó như thể là dữ kiện, và không ai truy ngược
 * được nữa.
 *
 * Cấm dùng: "vì", "do", "gây ra", "dẫn tới", "nhờ" trong `statement`.
 * Có test khoá lại điều này (`no unsupported causal statements`).
 */

export type ObservationKind =
  | 'TOP_PERFORMER'
  | 'BOTTOM_PERFORMER'
  | 'HIGH_RETENTION_LOW_REACH'
  | 'HIGH_REACH_LOW_RETENTION'
  | 'HIGH_CTR_LOW_WATCH'
  | 'LOW_CTR_HIGH_RETENTION'
  | 'SUBSCRIBER_EFFICIENT'
  | 'COHORT_TREND'
  | 'FORMAT_COMPARISON'
  | 'PUBLISH_TIME_COMPARISON'
  | 'CHANNEL_TREND_CHANGE'
  | 'ANOMALY'
  | 'DATA_QUALITY'
  | 'HYPOTHESIS_CANDIDATE'

export type Polarity = 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL'
export type BaselineKind =
  | 'CHANNEL_ALL'
  | 'CHANNEL_FORMAT'
  | 'RECENT_WINDOW'
  | 'MATURE_VIDEOS'
  | 'COHORT'
  | 'NONE'

export interface EvidenceRef {
  refType: 'VIDEO' | 'VIDEO_DAILY_METRIC' | 'CHANNEL_DAILY_METRIC' | 'FEATURE_VALUE' | 'COHORT_SUMMARY'
  refId?: string
  refKey?: string
  detail?: Record<string, unknown>
}

export interface Observation {
  kind: ObservationKind
  polarity: Polarity
  channelId: string
  videoId?: string
  statement: string
  metricValues: Record<string, number | string | null>
  baselineKind: BaselineKind
  baselineValue?: number | null
  observedValue?: number | null
  deltaRatio?: number | null
  percentile?: number | null
  confidence: number
  sampleSize?: number
  limitations: string[]
  evidence: EvidenceRef[]
  rankScore: number
  /** Khoá sắp xếp ổn định — quyết định tính tất định của thứ tự trong gói. */
  orderKey: string
  isHypothesis: boolean
  hypothesisQuestion?: string
}

/** Từ ngữ nhân quả bị cấm trong `statement` của tầng tất định. */
export const CAUSAL_MARKERS = [
  'vì',
  'do ',
  'gây ra',
  'dẫn tới',
  'dẫn đến',
  'nhờ ',
  'khiến',
  'nguyên nhân',
  'because',
  'causes',
  'caused',
  'due to',
  'leads to',
  'results in',
  'thanks to',
]

export function containsCausalClaim(text: string): boolean {
  const lower = text.toLowerCase()
  return CAUSAL_MARKERS.some((m) => lower.includes(m))
}

export interface VideoFeatureRow {
  video: VideoInput
  viewsD7: number | null
  viewsD1: number | null
  watchMinutesD7: number | null
  avgViewPercentage: number | null
  avgViewDurationSeconds: number | null
  likeRatePer1k: number | null
  commentRatePer1k: number | null
  subsPer1k: number | null
  impressions: number | null
  impressionCtr: number | null
  channelPercentileViewsD7: number | null
  formatPercentileViewsD7: number | null
  cohortPercentileViewsD7: number | null
  recentBaselineDelta: number | null
  matureBaselineDelta: number | null
  anomalyScore: number | null
  confidence: number
  stability: number | null
  coverage: number | null
}

function videoEvidence(row: VideoFeatureRow): EvidenceRef[] {
  return [
    {
      refType: 'VIDEO',
      refId: row.video.id,
      detail: {
        youtubeVideoId: row.video.youtubeVideoId,
        publishedAt: row.video.publishedAt,
        format: row.video.format,
        durationSeconds: row.video.durationSeconds,
        metricDays: row.video.metrics.length,
      },
    },
  ]
}

/**
 * Khoá sắp xếp ổn định.
 *
 * Gồm điểm hạng (đảo, đệm 0) rồi tới youtubeVideoId để phá thế hoà. Không có
 * phần phá hoà tất định thì hai quan sát cùng điểm sẽ đổi chỗ giữa các lần chạy
 * tuỳ thứ tự trả về của database, và hash gói sẽ đổi dù dữ liệu không đổi.
 */
export function makeOrderKey(kind: string, rankScore: number, tiebreak: string): string {
  const inverted = Math.max(0, 1_000_000 - Math.round(rankScore * 1000))
  return `${kind}:${String(inverted).padStart(9, '0')}:${tiebreak}`
}

export function topPerformers(
  channelId: string,
  rows: VideoFeatureRow[],
  limit: number,
): Observation[] {
  const eligible = rows.filter(
    (r) => r.viewsD7 !== null && r.formatPercentileViewsD7 !== null,
  )
  const sorted = [...eligible].sort(
    (a, b) =>
      (b.formatPercentileViewsD7 ?? 0) - (a.formatPercentileViewsD7 ?? 0) ||
      (b.viewsD7 ?? 0) - (a.viewsD7 ?? 0) ||
      a.video.youtubeVideoId.localeCompare(b.video.youtubeVideoId),
  )

  return sorted.slice(0, limit).map((r) => ({
    kind: 'TOP_PERFORMER' as const,
    polarity: 'POSITIVE' as const,
    channelId,
    videoId: r.video.id,
    statement:
      `Video ${r.video.youtubeVideoId} đạt phân vị ${round(r.formatPercentileViewsD7, 1)} về lượt xem 7 ngày đầu ` +
      `trong nhóm ${r.video.format} của kênh (${r.viewsD7} lượt xem).`,
    metricValues: {
      views_d7: r.viewsD7,
      format_percentile: r.formatPercentileViewsD7,
      avg_view_percentage: r.avgViewPercentage,
      format: r.video.format,
    },
    baselineKind: 'CHANNEL_FORMAT' as const,
    observedValue: r.viewsD7,
    percentile: r.formatPercentileViewsD7,
    confidence: r.confidence,
    limitations: buildLimitations(r),
    evidence: videoEvidence(r),
    rankScore: r.formatPercentileViewsD7 ?? 0,
    orderKey: makeOrderKey('TOP_PERFORMER', r.formatPercentileViewsD7 ?? 0, r.video.youtubeVideoId),
    isHypothesis: false,
  }))
}

export function bottomPerformers(
  channelId: string,
  rows: VideoFeatureRow[],
  limit: number,
): Observation[] {
  const eligible = rows.filter(
    (r) => r.viewsD7 !== null && r.formatPercentileViewsD7 !== null,
  )
  const sorted = [...eligible].sort(
    (a, b) =>
      (a.formatPercentileViewsD7 ?? 0) - (b.formatPercentileViewsD7 ?? 0) ||
      (a.viewsD7 ?? 0) - (b.viewsD7 ?? 0) ||
      a.video.youtubeVideoId.localeCompare(b.video.youtubeVideoId),
  )

  return sorted.slice(0, limit).map((r) => ({
    kind: 'BOTTOM_PERFORMER' as const,
    polarity: 'NEGATIVE' as const,
    channelId,
    videoId: r.video.id,
    statement:
      `Video ${r.video.youtubeVideoId} chỉ đạt phân vị ${round(r.formatPercentileViewsD7, 1)} về lượt xem 7 ngày đầu ` +
      `trong nhóm ${r.video.format} của kênh (${r.viewsD7} lượt xem).`,
    metricValues: {
      views_d7: r.viewsD7,
      format_percentile: r.formatPercentileViewsD7,
      avg_view_percentage: r.avgViewPercentage,
      format: r.video.format,
    },
    baselineKind: 'CHANNEL_FORMAT' as const,
    observedValue: r.viewsD7,
    percentile: r.formatPercentileViewsD7,
    confidence: r.confidence,
    limitations: buildLimitations(r),
    evidence: videoEvidence(r),
    rankScore: 100 - (r.formatPercentileViewsD7 ?? 0),
    orderKey: makeOrderKey(
      'BOTTOM_PERFORMER',
      100 - (r.formatPercentileViewsD7 ?? 0),
      r.video.youtubeVideoId,
    ),
    isHypothesis: false,
  }))
}

/**
 * Tổ hợp tín hiệu: giữ chân tốt nhưng tiếp cận kém, và các biến thể.
 *
 * Đây là nơi tầng tất định tiến sát ranh giới suy luận nhất, nên `statement`
 * vẫn thuần mô tả ("giữ chân ở phân vị X, tiếp cận ở phân vị Y") còn phần diễn
 * giải nằm ở `hypothesisQuestion` và được đánh dấu chưa kiểm chứng.
 */
export function signalCombinations(
  channelId: string,
  rows: VideoFeatureRow[],
  retentionPercentiles: Map<string, number>,
): Observation[] {
  const out: Observation[] = []
  const hi = ANALYSIS_THRESHOLDS.highPercentile
  const lo = ANALYSIS_THRESHOLDS.lowPercentile

  for (const r of rows) {
    const reach = r.formatPercentileViewsD7
    const retention = retentionPercentiles.get(r.video.id) ?? null
    if (reach === null || retention === null) continue

    if (retention >= hi && reach <= lo) {
      out.push({
        kind: 'HIGH_RETENTION_LOW_REACH',
        polarity: 'NEUTRAL',
        channelId,
        videoId: r.video.id,
        statement:
          `Video ${r.video.youtubeVideoId}: giữ chân ở phân vị ${round(retention, 1)} nhưng lượt xem 7 ngày ` +
          `chỉ ở phân vị ${round(reach, 1)} trong nhóm ${r.video.format}.`,
        metricValues: {
          retention_percentile: retention,
          reach_percentile: reach,
          avg_view_percentage: r.avgViewPercentage,
          views_d7: r.viewsD7,
        },
        baselineKind: 'CHANNEL_FORMAT',
        percentile: reach,
        confidence: r.confidence,
        limitations: buildLimitations(r),
        evidence: videoEvidence(r),
        rankScore: retention - reach,
        orderKey: makeOrderKey('HIGH_RETENTION_LOW_REACH', retention - reach, r.video.youtubeVideoId),
        isHypothesis: true,
        hypothesisQuestion:
          'Người đã xem thì xem lâu, nhưng ít người bắt đầu xem. Cần xem lại tiêu đề/thumbnail/chủ đề ' +
          'và cách phân phối — GIẢ THUYẾT chưa kiểm chứng, cần đọc nội dung để xác nhận.',
      })
    }

    if (retention <= lo && reach >= hi) {
      out.push({
        kind: 'HIGH_REACH_LOW_RETENTION',
        polarity: 'NEUTRAL',
        channelId,
        videoId: r.video.id,
        statement:
          `Video ${r.video.youtubeVideoId}: lượt xem 7 ngày ở phân vị ${round(reach, 1)} nhưng giữ chân ` +
          `chỉ ở phân vị ${round(retention, 1)} trong nhóm ${r.video.format}.`,
        metricValues: {
          retention_percentile: retention,
          reach_percentile: reach,
          avg_view_percentage: r.avgViewPercentage,
          views_d7: r.viewsD7,
        },
        baselineKind: 'CHANNEL_FORMAT',
        percentile: reach,
        confidence: r.confidence,
        limitations: buildLimitations(r),
        evidence: videoEvidence(r),
        rankScore: reach - retention,
        orderKey: makeOrderKey('HIGH_REACH_LOW_RETENTION', reach - retention, r.video.youtubeVideoId),
        isHypothesis: true,
        hypothesisQuestion:
          'Nhiều người bấm vào nhưng rời sớm. Cần soát phần mở đầu và mức độ khớp giữa tiêu đề và nội dung ' +
          '— GIẢ THUYẾT chưa kiểm chứng.',
      })
    }

    // Chỉ xét khi CTR thực sự có dữ liệu. Ba kênh này hiện không được YouTube
    // cấp impressions/CTR, nên nhánh dưới sẽ không kích hoạt — đúng như mong
    // muốn: không có dữ liệu thì không có quan sát, thay vì suy đoán.
    if (r.impressionCtr !== null && r.avgViewPercentage !== null) {
      const ctrHigh = r.impressionCtr
      if (ctrHigh > 0 && retention <= lo) {
        out.push({
          kind: 'HIGH_CTR_LOW_WATCH',
          polarity: 'NEUTRAL',
          channelId,
          videoId: r.video.id,
          statement:
            `Video ${r.video.youtubeVideoId}: CTR ${round(r.impressionCtr, 2)}% nhưng giữ chân ở phân vị ` +
            `${round(retention, 1)}.`,
          metricValues: { impression_ctr: r.impressionCtr, retention_percentile: retention },
          baselineKind: 'CHANNEL_FORMAT',
          confidence: r.confidence,
          limitations: buildLimitations(r),
          evidence: videoEvidence(r),
          rankScore: ctrHigh,
          orderKey: makeOrderKey('HIGH_CTR_LOW_WATCH', ctrHigh, r.video.youtubeVideoId),
          isHypothesis: true,
          hypothesisQuestion:
            'Gói tiêu đề/thumbnail hút được click nhưng nội dung chưa giữ được người xem — GIẢ THUYẾT chưa kiểm chứng.',
        })
      }
    }

    if (r.subsPer1k !== null && r.subsPer1k > 0 && reach >= hi) {
      out.push({
        kind: 'SUBSCRIBER_EFFICIENT',
        polarity: 'POSITIVE',
        channelId,
        videoId: r.video.id,
        statement:
          `Video ${r.video.youtubeVideoId}: ${round(r.subsPer1k, 3)} đăng ký ròng trên 1000 lượt xem, ` +
          `với lượt xem 7 ngày ở phân vị ${round(reach, 1)}.`,
        metricValues: { subs_per_1k: r.subsPer1k, reach_percentile: reach, views_d7: r.viewsD7 },
        baselineKind: 'CHANNEL_FORMAT',
        observedValue: r.subsPer1k,
        percentile: reach,
        confidence: r.confidence,
        limitations: buildLimitations(r),
        evidence: videoEvidence(r),
        rankScore: r.subsPer1k,
        orderKey: makeOrderKey('SUBSCRIBER_EFFICIENT', r.subsPer1k, r.video.youtubeVideoId),
        isHypothesis: false,
      })
    }
  }
  return out
}

export interface CohortStat {
  key: string
  kind: string
  videoCount: number
  medianViews: number | null
}

/** So sánh hai cohort xuất bản liền kề. */
export function cohortTrend(
  channelId: string,
  current: CohortStat,
  previous: CohortStat,
  windowLabel: string,
): Observation | null {
  if (
    current.videoCount < ANALYSIS_THRESHOLDS.minSampleForCohortComparison ||
    previous.videoCount < ANALYSIS_THRESHOLDS.minSampleForCohortComparison
  ) {
    return null
  }
  const delta = deltaRatio(current.medianViews, previous.medianViews)
  if (delta === null || Math.abs(delta) < ANALYSIS_THRESHOLDS.minCohortDeltaRatio) return null

  const direction = delta > 0 ? 'tăng' : 'giảm'
  return {
    kind: 'COHORT_TREND',
    polarity: delta > 0 ? 'POSITIVE' : 'NEGATIVE',
    channelId,
    statement:
      `Cohort ${current.key} ${direction} ${round(Math.abs(delta) * 100, 1)}% về trung vị lượt xem so với ` +
      `cohort ${previous.key} (${current.videoCount} vs ${previous.videoCount} video).`,
    metricValues: {
      current_median_views: current.medianViews,
      previous_median_views: previous.medianViews,
      current_videos: current.videoCount,
      previous_videos: previous.videoCount,
    },
    baselineKind: 'COHORT',
    baselineValue: previous.medianViews,
    observedValue: current.medianViews,
    deltaRatio: round(delta, 4),
    confidence: cohortConfidence(current.videoCount, previous.videoCount),
    sampleSize: current.videoCount + previous.videoCount,
    limitations: [
      'So sánh trung vị giữa hai cohort; không kiểm soát chủ đề, thời lượng hay thay đổi phân phối.',
      `Cửa sổ phân tích: ${windowLabel}.`,
    ],
    evidence: [
      { refType: 'COHORT_SUMMARY', refKey: `${current.kind}:${current.key}` },
      { refType: 'COHORT_SUMMARY', refKey: `${previous.kind}:${previous.key}` },
    ],
    rankScore: Math.abs(delta),
    orderKey: makeOrderKey('COHORT_TREND', Math.abs(delta), current.key),
    isHypothesis: false,
  }
}

/** So sánh giữa hai định dạng — luôn tách nhóm, không bao giờ trộn. */
export function formatComparison(
  channelId: string,
  shorts: number[],
  longform: number[],
  windowLabel: string,
): Observation | null {
  const min = ANALYSIS_THRESHOLDS.minSampleForCohortComparison
  if (shorts.length < min || longform.length < min) return null

  const shortMedian = median(shorts)
  const longMedian = median(longform)
  if (shortMedian === null || longMedian === null) return null

  const delta = deltaRatio(shortMedian, longMedian)
  return {
    kind: 'FORMAT_COMPARISON',
    polarity: 'NEUTRAL',
    channelId,
    statement:
      `Trung vị lượt xem 7 ngày: Shorts ${round(shortMedian, 1)} (n=${shorts.length}) so với ` +
      `Long-form ${round(longMedian, 1)} (n=${longform.length}).`,
    metricValues: {
      shorts_median_views_d7: shortMedian,
      longform_median_views_d7: longMedian,
      shorts_count: shorts.length,
      longform_count: longform.length,
    },
    baselineKind: 'CHANNEL_FORMAT',
    baselineValue: longMedian,
    observedValue: shortMedian,
    deltaRatio: round(delta, 4),
    confidence: cohortConfidence(shorts.length, longform.length),
    sampleSize: shorts.length + longform.length,
    limitations: [
      'Hai định dạng có cơ chế phân phối khác nhau; chênh lệch trung vị KHÔNG hàm ý định dạng nào tốt hơn.',
      `Cửa sổ phân tích: ${windowLabel}.`,
    ],
    evidence: [
      { refType: 'COHORT_SUMMARY', refKey: 'FORMAT:SHORT' },
      { refType: 'COHORT_SUMMARY', refKey: 'FORMAT:LONG_FORM' },
    ],
    rankScore: Math.abs(delta ?? 0),
    orderKey: makeOrderKey('FORMAT_COMPARISON', Math.abs(delta ?? 0), 'format'),
    isHypothesis: false,
  }
}

/** So sánh theo khung giờ đăng. Chỉ mô tả, không kết luận "nên đăng lúc X". */
export function publishTimeComparison(
  channelId: string,
  buckets: Map<string, number[]>,
  windowLabel: string,
): Observation | null {
  const usable = [...buckets.entries()]
    .filter(([, v]) => v.length >= ANALYSIS_THRESHOLDS.minSampleForCohortComparison)
    .map(([k, v]) => ({ key: k, count: v.length, med: median(v) }))
    .filter((b): b is { key: string; count: number; med: number } => b.med !== null)
    .sort((a, b) => b.med - a.med || a.key.localeCompare(b.key))

  if (usable.length < 2) return null
  const best = usable[0]!
  const worst = usable[usable.length - 1]!
  const delta = deltaRatio(best.med, worst.med)

  return {
    kind: 'PUBLISH_TIME_COMPARISON',
    polarity: 'NEUTRAL',
    channelId,
    statement:
      `Theo khung giờ đăng, trung vị lượt xem 7 ngày cao nhất ở ${best.key} (${round(best.med, 1)}, n=${best.count}) ` +
      `và thấp nhất ở ${worst.key} (${round(worst.med, 1)}, n=${worst.count}).`,
    metricValues: Object.fromEntries(usable.map((b) => [b.key, b.med])),
    baselineKind: 'CHANNEL_ALL',
    baselineValue: worst.med,
    observedValue: best.med,
    deltaRatio: round(delta, 4),
    confidence: cohortConfidence(best.count, worst.count),
    sampleSize: usable.reduce((s, b) => s + b.count, 0),
    limitations: [
      'Giờ đăng gắn chặt với chủ đề và ngày trong tuần; đây là TƯƠNG QUAN, không phải bằng chứng nhân quả.',
      `Cửa sổ phân tích: ${windowLabel}.`,
    ],
    evidence: usable.map((b) => ({
      refType: 'COHORT_SUMMARY' as const,
      refKey: `PUBLISH_HOUR_BUCKET:${b.key}`,
    })),
    rankScore: Math.abs(delta ?? 0),
    orderKey: makeOrderKey('PUBLISH_TIME_COMPARISON', Math.abs(delta ?? 0), best.key),
    isHypothesis: false,
  }
}

function cohortConfidence(a: number, b: number): number {
  const n = Math.min(a, b)
  // Bão hoà ở 20 video mỗi nhóm: trên mức đó, thêm mẫu gần như không đổi độ tin
  // cậy của một phép so trung vị.
  return round(Math.min(1, n / 20), 4)!
}

function buildLimitations(r: VideoFeatureRow): string[] {
  const out: string[] = []
  if (r.impressionCtr === null) {
    out.push('Không có impressions/CTR cho kênh này; không đánh giá được khâu tiếp cận.')
  }
  if (r.video.metrics.length < ANALYSIS_THRESHOLDS.minSampleForAnomaly) {
    out.push(`Chỉ có ${r.video.metrics.length} ngày dữ liệu.`)
  }
  if (r.confidence < ANALYSIS_THRESHOLDS.confidenceBands.medium) {
    out.push('Độ tin cậy thấp: dữ liệu thưa hoặc video còn quá mới.')
  }
  if (r.avgViewPercentage !== null && r.avgViewPercentage > 100) {
    out.push('Phần trăm xem vượt 100% (người xem tua lại) — đúng dữ liệu YouTube, không phải lỗi.')
  }
  return out
}

export { confidenceBandFor }
