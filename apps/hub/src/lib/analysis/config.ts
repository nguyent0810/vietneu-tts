/**
 * Ngưỡng và tham số của tầng phân tích tất định.
 *
 * Tập trung một chỗ và có phiên bản, vì đề bài yêu cầu "ngưỡng cấu hình được
 * hoặc có cơ sở thống kê, không phải kết luận cứng tuỳ tiện". Mỗi ngưỡng dưới
 * đây kèm lý do tồn tại; ngưỡng không giải thích được thì không nên có.
 */
export const ANALYSIS_ALGORITHM_KEY = 'deterministic-analysis'
export const ANALYSIS_ALGORITHM_VERSION = '1.0.0'
export const PACKAGE_SCHEMA_VERSION = '1.0.0'

export const ANALYSIS_THRESHOLDS = {
  /**
   * Số phần tử tối thiểu để một phân vị có nghĩa.
   *
   * Dưới 5, phân vị chỉ phản ánh vị trí trong một danh sách rất ngắn: với n=3,
   * "phân vị 83" chỉ có nghĩa là "đứng thứ 2 trên 3". Thà báo
   * INSUFFICIENT_SAMPLE còn hơn đưa một con số nghe có vẻ chính xác.
   */
  minSampleForPercentile: 5,

  /** Số video tối thiểu để so sánh hai cohort. Dưới mức này, chênh lệch trung
   *  vị chủ yếu là nhiễu. */
  minSampleForCohortComparison: 5,

  /** Số điểm tối thiểu để phát hiện bất thường bằng median/MAD. */
  minSampleForAnomaly: 8,

  /** z hiệu chỉnh vượt mức này thì coi là bất thường (Iglewicz–Hoaglin). */
  anomalyZThreshold: 3.5,

  /**
   * Tuổi (ngày) để coi một video là "đã chín".
   *
   * Shorts và video dài đều nhận phần lớn lượt xem trong những ngày đầu, nhưng
   * đuôi còn kéo dài. 14 ngày là mốc thoả hiệp: đủ để phần lớn lưu lượng đã
   * đến, mà vẫn giữ được lượng mẫu dùng được cho các kênh mới như 3 kênh này.
   */
  matureVideoAgeDays: 14,

  /** Các cửa sổ theo TUỔI video (ngày kể từ khi đăng). */
  performanceWindows: [1, 7, 14, 30] as const,

  /** Nửa tháng: cohort theo lô xuất bản. */
  cohortFortnightDays: 14,

  /**
   * Phân vị để gọi là "cao"/"thấp" khi ghép tín hiệu (vd retention cao + reach
   * thấp). Dùng phân vị chứ không dùng giá trị tuyệt đối, vì mức "tốt" khác
   * nhau hoàn toàn giữa các kênh và giữa Shorts với long-form.
   */
  highPercentile: 70,
  lowPercentile: 30,

  /** Chênh lệch trung vị tối thiểu để báo là thay đổi xu hướng cohort. */
  minCohortDeltaRatio: 0.15,

  /** Giới hạn kích thước gói gửi Cursor. */
  limits: {
    topPositiveObservations: 10,
    topNegativeObservations: 10,
    topAnomalies: 10,
    rankedVideos: 20,
    cohortSummaries: 12,
    hypothesisCandidates: 8,
    evidenceRefsPerObservation: 5,
    /** Trần cứng; vượt thì cắt bớt và ghi rõ đã cắt. */
    maxPackageBytes: 120_000,
  },

  /** Trọng số của điểm tin cậy. Tổng = 1. */
  confidenceWeights: {
    metricCoverage: 0.35,
    dateCompleteness: 0.25,
    sampleSize: 0.25,
    maturity: 0.15,
  },

  /** Ranh giới xếp hạng độ tin cậy. */
  confidenceBands: { high: 0.75, medium: 0.5 },

  /** Nhóm độ dài (giây). Ranh giới 180 khớp trần Shorts của YouTube. */
  durationBuckets: [
    { key: 'ultra_short', maxSeconds: 30 },
    { key: 'short', maxSeconds: 60 },
    { key: 'long_short', maxSeconds: 180 },
    { key: 'mid_form', maxSeconds: 600 },
    { key: 'long_form', maxSeconds: Number.POSITIVE_INFINITY },
  ] as const,

  /** Nhóm giờ đăng theo giờ địa phương của kênh. */
  publishHourBuckets: [
    { key: 'night_0_5', from: 0, to: 5 },
    { key: 'morning_6_11', from: 6, to: 11 },
    { key: 'afternoon_12_17', from: 12, to: 17 },
    { key: 'evening_18_23', from: 18, to: 23 },
  ] as const,
} as const

export type AnalysisThresholds = typeof ANALYSIS_THRESHOLDS

export function durationBucket(seconds: number | null): string | null {
  if (seconds === null) return null
  for (const bucket of ANALYSIS_THRESHOLDS.durationBuckets) {
    if (seconds <= bucket.maxSeconds) return bucket.key
  }
  return null
}

export function publishHourBucket(hour: number | null): string | null {
  if (hour === null) return null
  for (const bucket of ANALYSIS_THRESHOLDS.publishHourBuckets) {
    if (hour >= bucket.from && hour <= bucket.to) return bucket.key
  }
  return null
}

/**
 * Định dạng dùng để SO SÁNH, suy ra tại thời điểm phân tích.
 *
 * Ưu tiên `duration_seconds` hơn cột `format` đã lưu: cột đó do tầng nhập dữ
 * liệu gán, nên nó phản ánh quy tắc tại THỜI ĐIỂM SYNC. Khi ngưỡng Shorts đổi
 * (60s -> 180s), các hàng cũ giữ nhãn cũ cho tới lần sync sau — và đã xảy ra
 * đúng vậy: một lần sync đang chạy đã ghi đè bản phân loại lại, đưa 155 video
 * về UNKNOWN.
 *
 * Suy ra ở đây khiến kết quả phân tích chỉ phụ thuộc DỮ LIỆU (thời lượng), chứ
 * không phụ thuộc thời điểm chạy tầng nhập.
 */
export const SHORTS_MAX_SECONDS = 180

export function comparisonFormat(
  durationSeconds: number | null,
  storedFormat: string,
): 'SHORT' | 'LONG_FORM' | 'UNKNOWN' {
  if (durationSeconds !== null && Number.isFinite(durationSeconds)) {
    return durationSeconds <= SHORTS_MAX_SECONDS ? 'SHORT' : 'LONG_FORM'
  }
  return storedFormat === 'SHORT' || storedFormat === 'LONG_FORM' ? storedFormat : 'UNKNOWN'
}

export function confidenceBandFor(score: number): 'HIGH' | 'MEDIUM' | 'LOW' {
  if (score >= ANALYSIS_THRESHOLDS.confidenceBands.high) return 'HIGH'
  if (score >= ANALYSIS_THRESHOLDS.confidenceBands.medium) return 'MEDIUM'
  return 'LOW'
}
