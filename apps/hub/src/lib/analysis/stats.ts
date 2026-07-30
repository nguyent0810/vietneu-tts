/**
 * Nền thống kê cho tầng phân tích tất định.
 *
 * Dùng MEDIAN/MAD chứ không dùng MEAN/STDDEV ở mọi nơi so sánh.
 *
 * Lý do không phải sở thích: phân phối lượt xem trên YouTube lệch rất mạnh
 * (một video viral có thể gấp 100 lần trung vị). Trung bình và độ lệch chuẩn bị
 * chính outlier kéo đi, nên "z-score" cổ điển sẽ nói outlier đó chỉ lệch ~1σ và
 * đồng thời đẩy toàn bộ video bình thường xuống "dưới trung bình". Trung vị và
 * MAD có điểm gãy 50%, tức nửa số dữ liệu phải hỏng thì chúng mới hỏng.
 *
 * Mọi hàm ở đây đều THUẦN và TẤT ĐỊNH: cùng đầu vào cho cùng đầu ra, không phụ
 * thuộc thời gian, ngẫu nhiên hay thứ tự chèn.
 */

/** Hằng số quy đổi MAD sang thang lệch chuẩn với phân phối chuẩn (1/0.6745). */
export const MAD_TO_SIGMA = 1.4826

/**
 * Ngưỡng z hiệu chỉnh để coi là bất thường.
 *
 * 3.5 là mốc Iglewicz–Hoaglin khuyến nghị cho modified z-score — không phải số
 * tự chọn. Đặt trong `ANALYSIS_THRESHOLDS` để đổi được mà không sửa code.
 */
export const DEFAULT_ANOMALY_THRESHOLD = 3.5

export function median(values: readonly number[]): number | null {
  if (values.length === 0) return null
  const sorted = [...values].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 0 ? (sorted[mid - 1]! + sorted[mid]!) / 2 : sorted[mid]!
}

/**
 * Phân vị theo phương pháp nội suy tuyến tính (kiểu 7 của R, mặc định của numpy).
 * Ghi rõ phương pháp vì các thư viện khác nhau cho kết quả khác nhau ở mẫu nhỏ.
 */
export function quantile(values: readonly number[], q: number): number | null {
  if (values.length === 0) return null
  if (q <= 0) return Math.min(...values)
  if (q >= 1) return Math.max(...values)
  const sorted = [...values].sort((a, b) => a - b)
  const pos = (sorted.length - 1) * q
  const lower = Math.floor(pos)
  const upper = Math.ceil(pos)
  if (lower === upper) return sorted[lower]!
  return sorted[lower]! + (pos - lower) * (sorted[upper]! - sorted[lower]!)
}

/** Median Absolute Deviation — thước đo phân tán bền với outlier. */
export function mad(values: readonly number[]): number | null {
  const med = median(values)
  if (med === null) return null
  return median(values.map((v) => Math.abs(v - med)))
}

/**
 * z hiệu chỉnh theo MAD.
 *
 * Khi MAD = 0 (quá nửa số giá trị bằng nhau — rất hay gặp ở kênh nhỏ, nhiều
 * video 0 view) thì công thức chuẩn chia cho 0. Rơi về khoảng tứ phân vị; nếu
 * cũng bằng 0 thì phân tán thực sự bằng 0 và KHÔNG có khái niệm outlier — trả
 * `null` thay vì Infinity, để phía gọi ghi nhận là không tính được thay vì báo
 * mọi giá trị khác biệt đều là bất thường.
 */
export function modifiedZScore(value: number, values: readonly number[]): number | null {
  const med = median(values)
  if (med === null) return null

  const madValue = mad(values)
  if (madValue !== null && madValue > 0) {
    return (value - med) / (MAD_TO_SIGMA * madValue)
  }

  const p75 = quantile(values, 0.75)
  const p25 = quantile(values, 0.25)
  if (p75 === null || p25 === null) return null
  const iqr = p75 - p25
  if (iqr <= 0) return null

  // 1.349 = IQR của phân phối chuẩn chuẩn hoá, để thang khớp với nhánh MAD.
  return (value - med) / (iqr / 1.349)
}

/**
 * Hạng phân vị của `value` trong `values`, thang 0..100.
 *
 * Dùng định nghĩa "midrank": các giá trị bằng nhau nhận cùng một phân vị. Nếu
 * không, thứ tự chèn sẽ quyết định ai đứng trên ai — phá vỡ tính tất định khi
 * có nhiều giá trị trùng (rất phổ biến: hàng loạt video 0 view).
 */
export function percentileRank(value: number, values: readonly number[]): number | null {
  if (values.length === 0) return null
  let below = 0
  let equal = 0
  for (const v of values) {
    if (v < value) below++
    else if (v === value) equal++
  }
  return ((below + equal / 2) / values.length) * 100
}

/** Chia an toàn: mẫu số 0 hoặc không hữu hạn trả `null`, không trả Infinity/NaN. */
export function safeDivide(numerator: number | null, denominator: number | null): number | null {
  if (numerator === null || denominator === null) return null
  if (!Number.isFinite(numerator) || !Number.isFinite(denominator)) return null
  if (denominator === 0) return null
  const result = numerator / denominator
  return Number.isFinite(result) ? result : null
}

/**
 * Làm tròn tới N chữ số thập phân.
 *
 * BẮT BUỘC trước khi đưa số vào gói gửi LLM: số dấu phẩy động nhị phân có thể
 * cho ra 3.1000000000000005 tuỳ thứ tự phép tính, và khác biệt đó sẽ làm hash
 * của gói đổi dù đầu vào không đổi — phá vỡ yêu cầu tất định.
 */
export function round(value: number | null, digits = 4): number | null {
  if (value === null || !Number.isFinite(value)) return null
  const factor = 10 ** digits
  // +0 để tránh -0, thứ mà JSON.stringify in ra là "-0" và làm lệch hash.
  return Math.round(value * factor) / factor + 0
}

/** Tỉ lệ chênh lệch so với đường cơ sở: (observed - baseline) / |baseline|. */
export function deltaRatio(observed: number | null, baseline: number | null): number | null {
  if (observed === null || baseline === null) return null
  if (baseline === 0) return null
  return (observed - baseline) / Math.abs(baseline)
}

export interface Distribution {
  count: number
  median: number | null
  p25: number | null
  p75: number | null
  min: number | null
  max: number | null
  mad: number | null
}

export function describe(values: readonly number[]): Distribution {
  return {
    count: values.length,
    median: round(median(values)),
    p25: round(quantile(values, 0.25)),
    p75: round(quantile(values, 0.75)),
    min: values.length ? round(Math.min(...values)) : null,
    max: values.length ? round(Math.max(...values)) : null,
    mad: round(mad(values)),
  }
}
