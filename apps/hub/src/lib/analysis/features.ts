/**
 * Danh mục feature CÓ PHIÊN BẢN.
 *
 * Mỗi feature khai báo: khoá, đơn vị, chiều "tốt", chỉ số YouTube bắt buộc, và
 * CÔNG THỨC viết dạng người đọc được. Công thức đi kèm vào gói gửi Cursor, nên
 * LLM biết chính xác con số nó đang đọc được tính thế nào và không phải đoán —
 * cũng là cách ngăn nó "tính lại" hay bịa chỉ số.
 *
 * Đổi công thức thì PHẢI tăng `version` và thêm một mục mới, không sửa mục cũ:
 * `feature_version` bất biến ở tầng DB, và giá trị cũ vẫn trỏ về phiên bản đã
 * sinh ra chúng.
 */
export type FeatureUnit =
  | 'COUNT'
  | 'RATIO'
  | 'PERCENT'
  | 'SECONDS'
  | 'MINUTES'
  | 'PER_DAY'
  | 'ZSCORE'
  | 'RANK'
  | 'HOUR_OF_DAY'
  | 'DAY_OF_WEEK'

export type FeatureDirection = 'HIGHER_IS_BETTER' | 'LOWER_IS_BETTER' | 'NEUTRAL'
export type FeatureSubject = 'CHANNEL' | 'VIDEO'

export interface FeatureSpec {
  key: string
  label: string
  description: string
  unit: FeatureUnit
  direction: FeatureDirection
  subjectType: FeatureSubject
  version: string
  formula: string
  /** Chỉ số YouTube phải có; thiếu -> giá trị MISSING kèm lý do. */
  requiredMetrics: string[]
  spec?: Record<string, unknown>
}

const V1 = '1.0.0'

/**
 * Vì sao dùng cửa sổ theo TUỔI VIDEO chứ không theo ngày lịch:
 *
 * Một Short đăng hôm qua và một video dài đăng 3 tháng trước không so sánh được
 * bằng "lượt xem trong tháng 7". Cửa sổ theo tuổi (ngày 0..6 kể từ khi đăng) đặt
 * mọi video lên cùng một mốc so sánh — đây chính là "age normalization" mà đề
 * bài yêu cầu, và là lý do các feature dưới đây có hậu tố `_d1/_d7/_d14/_d30`.
 *
 * Video chưa đủ tuổi KHÔNG được gán 0: nó nhận INSUFFICIENT_AGE. Gán 0 sẽ kéo
 * trung vị của cả kênh xuống và làm mọi phân vị sai lệch.
 */
export const FEATURE_SPECS: FeatureSpec[] = [
  // --- Thuộc tính xuất bản (không phụ thuộc chỉ số) ---
  {
    key: 'publish_hour_local',
    label: 'Giờ đăng (giờ địa phương kênh)',
    description: 'Giờ trong ngày video được đăng, theo múi giờ báo cáo của kênh.',
    unit: 'HOUR_OF_DAY',
    direction: 'NEUTRAL',
    subjectType: 'VIDEO',
    version: V1,
    formula: 'hour(published_at trong reporting_timezone của kênh)',
    requiredMetrics: [],
  },
  {
    key: 'publish_weekday',
    label: 'Thứ trong tuần khi đăng',
    description: '0 = Chủ nhật ... 6 = Thứ bảy, theo múi giờ báo cáo của kênh.',
    unit: 'DAY_OF_WEEK',
    direction: 'NEUTRAL',
    subjectType: 'VIDEO',
    version: V1,
    formula: 'weekday(published_at trong reporting_timezone của kênh)',
    requiredMetrics: [],
  },
  {
    key: 'video_age_days',
    label: 'Tuổi video (ngày)',
    description: 'Số ngày từ lúc đăng tới hết cửa sổ phân tích.',
    unit: 'COUNT',
    direction: 'NEUTRAL',
    subjectType: 'VIDEO',
    version: V1,
    formula: 'window_end - date(published_at)',
    requiredMetrics: [],
  },
  {
    key: 'duration_seconds',
    label: 'Thời lượng (giây)',
    description: 'Độ dài video theo YouTube Data API.',
    unit: 'SECONDS',
    direction: 'NEUTRAL',
    subjectType: 'VIDEO',
    version: V1,
    formula: 'contentDetails.duration đổi ra giây',
    requiredMetrics: [],
  },
  {
    key: 'gap_since_previous_upload_days',
    label: 'Khoảng cách từ lần đăng trước (ngày)',
    description: 'Số ngày giữa video này và video đăng liền trước trên cùng kênh.',
    unit: 'COUNT',
    direction: 'NEUTRAL',
    subjectType: 'VIDEO',
    version: V1,
    formula: 'date(published_at) - date(published_at của video trước đó)',
    requiredMetrics: [],
  },

  // --- Hiệu suất theo cửa sổ tuổi ---
  ...[1, 7, 14, 30].flatMap((d): FeatureSpec[] => [
    {
      key: `views_d${d}`,
      label: `Lượt xem ${d} ngày đầu`,
      description: `Tổng lượt xem trong ${d} ngày đầu kể từ khi đăng. MISSING nếu video chưa đủ ${d} ngày tuổi.`,
      unit: 'COUNT',
      direction: 'HIGHER_IS_BETTER',
      subjectType: 'VIDEO',
      version: V1,
      formula: `sum(views) với date trong [publish_date, publish_date + ${d - 1}]`,
      requiredMetrics: ['views'],
      spec: { windowDays: d },
    },
    {
      key: `watch_minutes_d${d}`,
      label: `Phút xem ${d} ngày đầu`,
      description: `Tổng phút xem ước tính trong ${d} ngày đầu.`,
      unit: 'MINUTES',
      direction: 'HIGHER_IS_BETTER',
      subjectType: 'VIDEO',
      version: V1,
      formula: `sum(estimated_minutes_watched) với date trong [publish_date, publish_date + ${d - 1}]`,
      requiredMetrics: ['estimatedMinutesWatched'],
      spec: { windowDays: d },
    },
  ]),

  {
    key: 'views_velocity_d7',
    label: 'Tốc độ lượt xem (7 ngày đầu)',
    description: 'Lượt xem trung bình mỗi ngày trong 7 ngày đầu.',
    unit: 'PER_DAY',
    direction: 'HIGHER_IS_BETTER',
    subjectType: 'VIDEO',
    version: V1,
    formula: 'views_d7 / 7',
    requiredMetrics: ['views'],
  },
  {
    key: 'watch_velocity_d7',
    label: 'Tốc độ phút xem (7 ngày đầu)',
    description: 'Phút xem trung bình mỗi ngày trong 7 ngày đầu.',
    unit: 'PER_DAY',
    direction: 'HIGHER_IS_BETTER',
    subjectType: 'VIDEO',
    version: V1,
    formula: 'watch_minutes_d7 / 7',
    requiredMetrics: ['estimatedMinutesWatched'],
  },

  // --- Chất lượng giữ chân ---
  {
    key: 'avg_view_percentage',
    label: 'Phần trăm xem trung bình',
    description:
      'Trung bình có trọng số theo lượt xem của average_view_percentage. CÓ THỂ vượt 100% khi người xem tua lại.',
    unit: 'PERCENT',
    direction: 'HIGHER_IS_BETTER',
    subjectType: 'VIDEO',
    version: V1,
    formula: 'sum(average_view_percentage * views) / sum(views) trên toàn cửa sổ',
    requiredMetrics: ['averageViewPercentage', 'views'],
  },
  {
    key: 'avg_view_duration_seconds',
    label: 'Thời lượng xem trung bình (giây)',
    description: 'Trung bình có trọng số theo lượt xem của average_view_duration.',
    unit: 'SECONDS',
    direction: 'HIGHER_IS_BETTER',
    subjectType: 'VIDEO',
    version: V1,
    formula: 'sum(average_view_duration_seconds * views) / sum(views)',
    requiredMetrics: ['averageViewDurationSeconds', 'views'],
  },

  // --- Tương tác, chuẩn hoá theo lượt xem ---
  {
    key: 'like_rate_per_1k',
    label: 'Lượt thích trên 1000 view',
    description: 'Lượt thích chuẩn hoá theo lượt xem, để so được giữa video lớn nhỏ.',
    unit: 'RATIO',
    direction: 'HIGHER_IS_BETTER',
    subjectType: 'VIDEO',
    version: V1,
    formula: '1000 * sum(likes) / sum(views)',
    requiredMetrics: ['likes', 'views'],
  },
  {
    key: 'comment_rate_per_1k',
    label: 'Bình luận trên 1000 view',
    description: 'Bình luận chuẩn hoá theo lượt xem.',
    unit: 'RATIO',
    direction: 'HIGHER_IS_BETTER',
    subjectType: 'VIDEO',
    version: V1,
    formula: '1000 * sum(comments) / sum(views)',
    requiredMetrics: ['comments', 'views'],
  },
  {
    key: 'subscriber_conversion_per_1k',
    label: 'Đăng ký ròng trên 1000 view',
    description:
      'Đăng ký RÒNG (tăng trừ giảm) trên 1000 lượt xem. Có thể ÂM khi mất nhiều hơn được.',
    unit: 'RATIO',
    direction: 'HIGHER_IS_BETTER',
    subjectType: 'VIDEO',
    version: V1,
    formula: '1000 * (sum(subscribers_gained) - sum(subscribers_lost)) / sum(views)',
    requiredMetrics: ['subscribersGained', 'views'],
  },

  // --- Reach: thường thiếu trên các kênh này ---
  {
    key: 'impressions_total',
    label: 'Tổng lượt hiển thị',
    description: 'Tổng impressions trong cửa sổ. YouTube không cấp chỉ số này cho mọi kênh.',
    unit: 'COUNT',
    direction: 'HIGHER_IS_BETTER',
    subjectType: 'VIDEO',
    version: V1,
    formula: 'sum(impressions)',
    requiredMetrics: ['impressions'],
  },
  {
    key: 'impression_ctr',
    label: 'Tỉ lệ nhấp từ hiển thị (%)',
    description: 'CTR có trọng số theo impressions.',
    unit: 'PERCENT',
    direction: 'HIGHER_IS_BETTER',
    subjectType: 'VIDEO',
    version: V1,
    formula: '100 * sum(impressions * impression_ctr / 100) / sum(impressions)',
    requiredMetrics: ['impressions', 'impressionCtr'],
  },

  // --- Vị trí tương đối ---
  {
    key: 'channel_percentile_views_d7',
    label: 'Phân vị views 7 ngày trong kênh',
    description: 'Hạng phân vị của views_d7 so với MỌI video có views_d7 của cùng kênh.',
    unit: 'RANK',
    direction: 'HIGHER_IS_BETTER',
    subjectType: 'VIDEO',
    version: V1,
    formula: 'percentileRank(views_d7, tất cả views_d7 của kênh) — midrank cho giá trị trùng',
    requiredMetrics: ['views'],
  },
  {
    key: 'format_percentile_views_d7',
    label: 'Phân vị views 7 ngày trong cùng định dạng',
    description:
      'Như trên nhưng chỉ so với video CÙNG ĐỊNH DẠNG (Shorts vs Long-form) — so chéo định dạng là vô nghĩa.',
    unit: 'RANK',
    direction: 'HIGHER_IS_BETTER',
    subjectType: 'VIDEO',
    version: V1,
    formula: 'percentileRank(views_d7, views_d7 của video cùng format trong kênh)',
    requiredMetrics: ['views'],
  },
  {
    key: 'cohort_percentile_views_d7',
    label: 'Phân vị views 7 ngày trong cohort xuất bản',
    description: 'Phân vị trong cùng lô xuất bản nửa tháng và cùng định dạng.',
    unit: 'RANK',
    direction: 'HIGHER_IS_BETTER',
    subjectType: 'VIDEO',
    version: V1,
    formula: 'percentileRank(views_d7, cùng cohort nửa tháng + cùng format)',
    requiredMetrics: ['views'],
  },
  {
    key: 'recent_baseline_delta_views_d7',
    label: 'Chênh lệch so với đường cơ sở gần đây',
    description: 'views_d7 lệch bao nhiêu so với trung vị của các video gần đây cùng định dạng.',
    unit: 'RATIO',
    direction: 'HIGHER_IS_BETTER',
    subjectType: 'VIDEO',
    version: V1,
    formula: '(views_d7 - median(views_d7 của cohort gần đây cùng format)) / |median|',
    requiredMetrics: ['views'],
  },
  {
    key: 'mature_baseline_delta_views_d7',
    label: 'Chênh lệch so với đường cơ sở video đã chín',
    description: 'views_d7 lệch bao nhiêu so với trung vị của video đã đủ 14 ngày tuổi cùng định dạng.',
    unit: 'RATIO',
    direction: 'HIGHER_IS_BETTER',
    subjectType: 'VIDEO',
    version: V1,
    formula: '(views_d7 - median(views_d7 của video đã chín cùng format)) / |median|',
    requiredMetrics: ['views'],
  },

  // --- Chất lượng dữ liệu ---
  {
    key: 'metric_coverage_score',
    label: 'Điểm độ phủ chỉ số',
    description: 'Tỉ lệ chỉ số cốt lõi thực sự có dữ liệu cho video này.',
    unit: 'RATIO',
    direction: 'HIGHER_IS_BETTER',
    subjectType: 'VIDEO',
    version: V1,
    formula: 'số chỉ số cốt lõi khác NULL / tổng số chỉ số cốt lõi',
    requiredMetrics: [],
  },
  {
    key: 'performance_stability',
    label: 'Độ ổn định hiệu suất',
    description:
      'Nghịch đảo hệ số biến thiên bền của lượt xem theo ngày; cao = đều đặn, thấp = bùng nổ rồi tắt.',
    unit: 'RATIO',
    direction: 'NEUTRAL',
    subjectType: 'VIDEO',
    version: V1,
    formula: '1 / (1 + MAD(views theo ngày) / median(views theo ngày))',
    requiredMetrics: ['views'],
  },
  {
    key: 'anomaly_score_views_d7',
    label: 'Điểm bất thường của views 7 ngày',
    description: 'z hiệu chỉnh theo MAD của views_d7 trong nhóm cùng định dạng của kênh.',
    unit: 'ZSCORE',
    direction: 'NEUTRAL',
    subjectType: 'VIDEO',
    version: V1,
    formula: '(views_d7 - median) / (1.4826 * MAD); rơi về IQR/1.349 khi MAD = 0',
    requiredMetrics: ['views'],
  },
  {
    key: 'confidence_score',
    label: 'Điểm tin cậy',
    description: 'Độ tin cậy tổng hợp của video này dựa trên độ phủ, tuổi và lượng mẫu.',
    unit: 'RATIO',
    direction: 'HIGHER_IS_BETTER',
    subjectType: 'VIDEO',
    version: V1,
    formula:
      '0.35*coverage + 0.25*dateCompleteness + 0.25*sampleAdequacy + 0.15*maturity',
    requiredMetrics: [],
  },

  // --- Feature cấp kênh ---
  {
    key: 'upload_frequency_per_week',
    label: 'Tần suất đăng mỗi tuần',
    description: 'Số video đăng trong cửa sổ, quy về mỗi tuần.',
    unit: 'PER_DAY',
    direction: 'NEUTRAL',
    subjectType: 'CHANNEL',
    version: V1,
    formula: '7 * số video đăng trong cửa sổ / số ngày của cửa sổ',
    requiredMetrics: [],
  },
  {
    key: 'channel_median_views_d7',
    label: 'Trung vị views 7 ngày của kênh',
    description: 'Trung vị views_d7 trên mọi video đủ điều kiện của kênh.',
    unit: 'COUNT',
    direction: 'HIGHER_IS_BETTER',
    subjectType: 'CHANNEL',
    version: V1,
    formula: 'median(views_d7 của mọi video đủ điều kiện)',
    requiredMetrics: ['views'],
  },
  {
    key: 'channel_total_views_window',
    label: 'Tổng lượt xem kênh trong cửa sổ',
    description: 'Tổng lượt xem cấp kênh theo ngày lịch trong cửa sổ phân tích.',
    unit: 'COUNT',
    direction: 'HIGHER_IS_BETTER',
    subjectType: 'CHANNEL',
    version: V1,
    formula: 'sum(channel_daily_metric.views) trong cửa sổ',
    requiredMetrics: ['views'],
  },
]

export const FEATURE_KEYS = FEATURE_SPECS.map((f) => f.key)

export function featureSpec(key: string): FeatureSpec {
  const found = FEATURE_SPECS.find((f) => f.key === key)
  if (!found) throw new Error(`Feature chưa khai báo: ${key}`)
  return found
}
