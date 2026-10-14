import { ANALYSIS_THRESHOLDS, durationBucket, publishHourBucket } from './config'
import { mad, median, modifiedZScore, percentileRank, round, safeDivide } from './stats'

/**
 * Tính feature từ chỉ số thô. Thuần và tất định — không chạm DB, không chạm
 * đồng hồ hệ thống. Toàn bộ ngày tháng do phía gọi truyền vào, nên cùng đầu vào
 * luôn cho cùng đầu ra (và cùng hash gói).
 */

export type MissingReason =
  | 'METRIC_NOT_PROVIDED'
  | 'INSUFFICIENT_AGE'
  | 'INSUFFICIENT_SAMPLE'
  | 'NO_METRIC_ROWS'
  | 'DIVISION_BY_ZERO'
  | 'DEPENDENCY_MISSING'
  | 'OUTSIDE_WINDOW'

/** Giá trị feature: hoặc có số, hoặc có lý do thiếu — không bao giờ cả hai. */
export type FeatureResult =
  | { value: number; missing?: undefined; sampleSize: number }
  | { value?: undefined; missing: MissingReason; sampleSize: number }

export function present(value: number, sampleSize: number): FeatureResult {
  return { value, sampleSize }
}
export function missing(reason: MissingReason, sampleSize = 0): FeatureResult {
  return { missing: reason, sampleSize }
}

export interface DailyMetric {
  date: string
  views: number | null
  estimatedMinutesWatched: number | null
  averageViewDurationSeconds: number | null
  averageViewPercentage: number | null
  impressions: number | null
  impressionCtr: number | null
  likes: number | null
  dislikes: number | null
  comments: number | null
  shares: number | null
  subscribersGained: number | null
  subscribersLost: number | null
}

export interface VideoInput {
  id: string
  youtubeVideoId: string
  title: string
  publishedAt: string
  publishDate: string
  publishedHourLocal: number | null
  publishedWeekdayLocal: number | null
  durationSeconds: number | null
  format: 'SHORT' | 'LONG_FORM' | 'UNKNOWN'
  metrics: DailyMetric[]
}

export const CORE_METRIC_KEYS = [
  'views',
  'estimatedMinutesWatched',
  'averageViewDurationSeconds',
  'averageViewPercentage',
  'likes',
  'comments',
  'shares',
  'subscribersGained',
  'subscribersLost',
] as const

/** Số ngày giữa hai nhãn ngày YYYY-MM-DD (chênh lệch lịch, không phụ thuộc múi giờ). */
export function daysBetween(from: string, to: string): number {
  const a = Date.UTC(+from.slice(0, 4), +from.slice(5, 7) - 1, +from.slice(8, 10))
  const b = Date.UTC(+to.slice(0, 4), +to.slice(5, 7) - 1, +to.slice(8, 10))
  return Math.round((b - a) / 86_400_000)
}

export function addDays(isoDate: string, days: number): string {
  const dt = new Date(
    Date.UTC(+isoDate.slice(0, 4), +isoDate.slice(5, 7) - 1, +isoDate.slice(8, 10)),
  )
  dt.setUTCDate(dt.getUTCDate() + days)
  return dt.toISOString().slice(0, 10)
}

/**
 * Chỉ số nằm trong cửa sổ [publishDate, publishDate + days - 1].
 *
 * Đây là hạt nhân của chuẩn hoá theo tuổi: mọi video được đo trên cùng một
 * khoảng tuổi, nên Short mới đăng và video dài đã lâu so sánh được với nhau.
 */
export function metricsInAgeWindow(video: VideoInput, days: number): DailyMetric[] {
  const end = addDays(video.publishDate, days - 1)
  return video.metrics.filter((m) => m.date >= video.publishDate && m.date <= end)
}

function sumOf(rows: DailyMetric[], key: keyof DailyMetric): { sum: number; n: number } {
  let sum = 0
  let n = 0
  for (const r of rows) {
    const v = r[key]
    if (typeof v === 'number' && Number.isFinite(v)) {
      sum += v
      n++
    }
  }
  return { sum, n }
}

/**
 * Trung bình có TRỌNG SỐ theo lượt xem.
 *
 * Trung bình đơn giản của `average_view_percentage` theo ngày sẽ sai: một ngày
 * có 3 lượt xem được tính ngang với ngày có 3000 lượt xem. Trọng số theo views
 * cho ra đúng con số "trung bình trên mỗi lượt xem".
 */
function weightedMean(
  rows: DailyMetric[],
  valueKey: keyof DailyMetric,
  weightKey: keyof DailyMetric = 'views',
): { value: number | null; n: number } {
  let weighted = 0
  let weight = 0
  let n = 0
  for (const r of rows) {
    const v = r[valueKey]
    const w = r[weightKey]
    if (typeof v === 'number' && typeof w === 'number' && Number.isFinite(v) && Number.isFinite(w) && w > 0) {
      weighted += v * w
      weight += w
      n++
    }
  }
  if (weight === 0) return { value: null, n }
  return { value: weighted / weight, n }
}

/** Tuổi video tính tới hết cửa sổ phân tích. */
export function videoAgeDays(video: VideoInput, windowEnd: string): number {
  return daysBetween(video.publishDate, windowEnd)
}

/**
 * Hiệu suất trong N ngày đầu.
 *
 * Trả INSUFFICIENT_AGE khi video chưa sống đủ N ngày TÍNH ĐẾN HẾT CỬA SỔ. Gán 0
 * cho những video này là lỗi tinh vi nhất trong cả tầng phân tích: nó kéo trung
 * vị kênh xuống, đẩy phân vị của mọi video khác lên, và làm các video mới trông
 * như thất bại trong khi chúng chỉ đơn giản là chưa có thời gian.
 */
export function windowSum(
  video: VideoInput,
  days: number,
  key: keyof DailyMetric,
  windowEnd: string,
): FeatureResult {
  if (videoAgeDays(video, windowEnd) < days - 1) {
    return missing('INSUFFICIENT_AGE')
  }
  const rows = metricsInAgeWindow(video, days)
  if (rows.length === 0) return missing('NO_METRIC_ROWS')
  const { sum, n } = sumOf(rows, key)
  if (n === 0) return missing('METRIC_NOT_PROVIDED', rows.length)
  return present(round(sum, 4)!, n)
}

export function ratePerThousand(
  video: VideoInput,
  numeratorKey: keyof DailyMetric,
  windowEnd: string,
  negativeKey?: keyof DailyMetric,
): FeatureResult {
  void windowEnd
  const rows = video.metrics
  if (rows.length === 0) return missing('NO_METRIC_ROWS')

  const num = sumOf(rows, numeratorKey)
  if (num.n === 0) return missing('METRIC_NOT_PROVIDED', rows.length)

  let numerator = num.sum
  if (negativeKey) {
    const neg = sumOf(rows, negativeKey)
    numerator -= neg.sum
  }

  const views = sumOf(rows, 'views')
  if (views.n === 0) return missing('DEPENDENCY_MISSING', rows.length)
  const rate = safeDivide(numerator * 1000, views.sum)
  if (rate === null) return missing('DIVISION_BY_ZERO', rows.length)
  return present(round(rate, 4)!, num.n)
}

export function weightedFeature(
  video: VideoInput,
  valueKey: keyof DailyMetric,
): FeatureResult {
  const rows = video.metrics
  if (rows.length === 0) return missing('NO_METRIC_ROWS')
  const { value, n } = weightedMean(rows, valueKey)
  if (value === null) {
    return n === 0 ? missing('METRIC_NOT_PROVIDED', rows.length) : missing('DIVISION_BY_ZERO', n)
  }
  return present(round(value, 4)!, n)
}

/** CTR có trọng số theo impressions (không phải theo views). */
export function impressionCtrFeature(video: VideoInput): FeatureResult {
  const rows = video.metrics
  if (rows.length === 0) return missing('NO_METRIC_ROWS')
  const { value, n } = weightedMean(rows, 'impressionCtr', 'impressions')
  if (value === null) {
    return n === 0 ? missing('METRIC_NOT_PROVIDED', rows.length) : missing('DIVISION_BY_ZERO', n)
  }
  return present(round(value, 4)!, n)
}

/**
 * Độ ổn định: 1 / (1 + MAD/median) của lượt xem theo ngày.
 *
 * Gần 1 = lưu lượng đều; gần 0 = bùng nổ rồi tắt. Dùng MAD/median (hệ số biến
 * thiên bền) thay cho stddev/mean vì chuỗi lượt xem theo ngày gần như luôn có
 * một đỉnh ở ngày đầu.
 */
export function performanceStability(video: VideoInput): FeatureResult {
  const views = video.metrics
    .map((m) => m.views)
    .filter((v): v is number => typeof v === 'number' && Number.isFinite(v))
  if (views.length < 3) return missing('INSUFFICIENT_SAMPLE', views.length)
  const med = median(views)
  const madValue = mad(views)
  if (med === null || madValue === null) return missing('INSUFFICIENT_SAMPLE', views.length)
  if (med === 0) return missing('DIVISION_BY_ZERO', views.length)
  return present(round(1 / (1 + madValue / med), 4)!, views.length)
}

/** Tỉ lệ chỉ số cốt lõi thực sự có dữ liệu cho video này. */
export function metricCoverageScore(video: VideoInput): FeatureResult {
  const rows = video.metrics
  if (rows.length === 0) return missing('NO_METRIC_ROWS')
  let covered = 0
  for (const key of CORE_METRIC_KEYS) {
    if (rows.some((r) => typeof r[key] === 'number')) covered++
  }
  return present(round(covered / CORE_METRIC_KEYS.length, 4)!, rows.length)
}

/**
 * Điểm tin cậy của một video.
 *
 * Bốn thành phần có trọng số (xem `confidenceWeights`):
 *  - độ phủ chỉ số: bao nhiêu chỉ số cốt lõi thực sự có;
 *  - độ đầy đủ ngày: có bao nhiêu ngày trong khoảng lẽ ra phải có;
 *  - lượng mẫu: số ngày có dữ liệu so với ngưỡng tối thiểu;
 *  - độ chín: video đã đủ 14 ngày chưa.
 *
 * Trả về SỐ chứ không phải nhãn, để phía gọi tự cắt băng — và để hai video có
 * cùng nhãn vẫn phân biệt được khi xếp hạng.
 */
export function confidenceScore(video: VideoInput, windowEnd: string): FeatureResult {
  const rows = video.metrics
  const w = ANALYSIS_THRESHOLDS.confidenceWeights

  const coverage = metricCoverageScore(video)
  const coverageValue = coverage.value ?? 0

  const age = videoAgeDays(video, windowEnd)
  const expectedDays = Math.max(1, Math.min(age + 1, ANALYSIS_THRESHOLDS.matureVideoAgeDays))
  const observedInExpected = metricsInAgeWindow(video, expectedDays).length
  const dateCompleteness = Math.min(1, observedInExpected / expectedDays)

  const sampleAdequacy = Math.min(1, rows.length / ANALYSIS_THRESHOLDS.minSampleForAnomaly)
  const maturity = Math.min(1, age / ANALYSIS_THRESHOLDS.matureVideoAgeDays)

  const score =
    w.metricCoverage * coverageValue +
    w.dateCompleteness * dateCompleteness +
    w.sampleSize * sampleAdequacy +
    w.maturity * maturity

  return present(round(Math.max(0, Math.min(1, score)), 4)!, rows.length)
}

/** Phân vị trong một nhóm; dưới ngưỡng mẫu tối thiểu thì trả INSUFFICIENT_SAMPLE. */
export function percentileFeature(value: number, group: readonly number[]): FeatureResult {
  if (group.length < ANALYSIS_THRESHOLDS.minSampleForPercentile) {
    return missing('INSUFFICIENT_SAMPLE', group.length)
  }
  const rank = percentileRank(value, group)
  if (rank === null) return missing('INSUFFICIENT_SAMPLE', group.length)
  return present(round(rank, 3)!, group.length)
}

export function anomalyScoreFeature(value: number, group: readonly number[]): FeatureResult {
  if (group.length < ANALYSIS_THRESHOLDS.minSampleForAnomaly) {
    return missing('INSUFFICIENT_SAMPLE', group.length)
  }
  const z = modifiedZScore(value, group)
  if (z === null) return missing('DIVISION_BY_ZERO', group.length)
  return present(round(z, 4)!, group.length)
}

export function baselineDeltaFeature(value: number, group: readonly number[]): FeatureResult {
  if (group.length < ANALYSIS_THRESHOLDS.minSampleForPercentile) {
    return missing('INSUFFICIENT_SAMPLE', group.length)
  }
  const med = median(group)
  if (med === null) return missing('INSUFFICIENT_SAMPLE', group.length)
  if (med === 0) return missing('DIVISION_BY_ZERO', group.length)
  return present(round((value - med) / Math.abs(med), 4)!, group.length)
}

export { durationBucket, publishHourBucket }
