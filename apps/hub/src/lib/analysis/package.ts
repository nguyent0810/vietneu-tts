import { createHash } from 'node:crypto'

import { ANALYSIS_ALGORITHM_VERSION, ANALYSIS_THRESHOLDS, PACKAGE_SCHEMA_VERSION } from './config'
import type { Observation } from './observations'

/**
 * Gói bằng chứng GỌN gửi cho Cursor CLI.
 *
 * Nguyên tắc: Cursor nhận BÀI TOÁN SUY LUẬN CÒN LẠI, không nhận bảng chỉ số thô.
 * Mọi thứ đếm được, chuẩn hoá được, xếp hạng được, nén được đã làm xong ở tầng
 * tất định. Cái còn lại — vì sao các tín hiệu này đi cùng nhau, nên làm gì tiếp
 * — mới cần ngữ cảnh và mới đáng gọi LLM.
 *
 * Gói KHÔNG chứa lịch sử chỉ số theo ngày. Thay vào đó nó chứa `evidenceRefs`:
 * Cursor thấy được bằng chứng nào chống lưng cho mỗi quan sát, và nếu cần chi
 * tiết thì hỏi lại đúng phần đó.
 */

export interface PackageLimitsApplied {
  positiveObservations: { included: number; total: number }
  negativeObservations: { included: number; total: number }
  anomalies: { included: number; total: number }
  rankedVideos: { included: number; total: number }
  cohorts: { included: number; total: number }
  hypotheses: { included: number; total: number }
  truncatedForSize: boolean
}

export interface AnalysisPackage {
  schemaVersion: string
  algorithmVersion: string
  scope: {
    workspaceId: string
    channelId: string
    channelLabel: string
    channelTitle: string
    reportingTimezone: string
    windowStart: string
    windowEnd: string
    analysisRunId: string
    inputHash: string
  }
  channelSummary: Record<string, number | string | null>
  dataCoverage: {
    videosTotal: number
    videosWithMetrics: number
    videosImmature: number
    metricRows: number
    expectedDates: number
    observedDates: number
    missingDates: string[]
    metricCoverage: Record<string, number>
    revisedRows: number
  }
  confidence: { score: number; band: string; drivers: Record<string, number> }
  baselines: Array<{
    key: string
    kind: string
    description: string
    videoCount: number
    medianViewsD7: number | null
  }>
  featureDefinitions: Array<{
    key: string
    label: string
    unit: string
    direction: string
    version: string
    formula: string
  }>
  observations: Array<PackagedObservation>
  anomalies: Array<Record<string, unknown>>
  rankedVideos: Array<Record<string, unknown>>
  cohortComparisons: Array<Record<string, unknown>>
  formatComparison: Record<string, unknown> | null
  hypothesisCandidates: Array<PackagedObservation>
  unresolvedQuestions: string[]
  missingData: string[]
  analysisTasks: string[]
  limitsApplied: PackageLimitsApplied
}

export interface PackagedObservation {
  kind: string
  polarity: string
  statement: string
  videoId?: string
  metricValues: Record<string, number | string | null>
  baselineKind: string
  percentile?: number | null
  deltaRatio?: number | null
  confidence: number
  limitations: string[]
  evidenceRefs: Array<Record<string, unknown>>
  isHypothesis: boolean
  hypothesisQuestion?: string
}

/**
 * Tuần tự hoá JSON có thứ tự khoá ỔN ĐỊNH.
 *
 * `JSON.stringify` giữ nguyên thứ tự chèn của khoá, nên hai lần chạy dựng object
 * theo thứ tự khác nhau sẽ cho hai chuỗi khác nhau — và hai hash khác nhau — dù
 * nội dung y hệt. Sắp khoá theo bảng chữ cái ở mọi tầng khiến hash chỉ phụ thuộc
 * NỘI DUNG, đúng yêu cầu "cùng input cho cùng output và cùng hash".
 */
export function stableStringify(value: unknown): string {
  return JSON.stringify(sortValue(value))
}

function sortValue(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortValue)
  if (value !== null && typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>)
      .filter(([, v]) => v !== undefined) // undefined biến mất khi stringify -> loại sớm cho nhất quán
      .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
    return Object.fromEntries(entries.map(([k, v]) => [k, sortValue(v)]))
  }
  return value
}

/**
 * Hash NỘI DUNG của gói.
 *
 * Loại `scope.analysisRunId` ra khỏi phần được băm, có chủ đích: id đó là một
 * UUID sinh ngẫu nhiên lúc ghi, nên nếu đưa vào hash thì hai lần chạy trên
 * CÙNG dữ liệu sẽ cho hai hash khác nhau — đúng thứ mà yêu cầu "cùng input cho
 * cùng hash" tồn tại để phát hiện. Khi đó hash không còn dùng để so sánh được
 * gì, kể cả để nhận ra một lần tính lại không đổi kết quả.
 *
 * Danh tính lần chạy vẫn được giữ ở hai chỗ khác: cột `analysis_run_id` của
 * bảng, và `scope.inputHash` (băm chính dữ liệu đầu vào). Cái ta cần ở đây là
 * căn cước của NỘI DUNG.
 */
export function hashPackage(pkg: AnalysisPackage): string {
  const { analysisRunId, ...scopeWithoutRun } = pkg.scope
  void analysisRunId
  const canonical = { ...pkg, scope: scopeWithoutRun }
  return createHash('sha256').update(stableStringify(canonical), 'utf8').digest('hex')
}

export function packageBytes(pkg: AnalysisPackage): number {
  return Buffer.byteLength(stableStringify(pkg), 'utf8')
}

function packObservation(o: Observation): PackagedObservation {
  const packed: PackagedObservation = {
    kind: o.kind,
    polarity: o.polarity,
    statement: o.statement,
    metricValues: o.metricValues,
    baselineKind: o.baselineKind,
    confidence: o.confidence,
    limitations: o.limitations,
    // Giới hạn số tham chiếu bằng chứng: mục đích là CHỈ ĐƯỜNG tới dữ liệu gốc,
    // không phải nhúng lại dữ liệu gốc vào gói.
    evidenceRefs: o.evidence
      .slice(0, ANALYSIS_THRESHOLDS.limits.evidenceRefsPerObservation)
      .map((e) => ({
        refType: e.refType,
        ...(e.refId ? { refId: e.refId } : {}),
        ...(e.refKey ? { refKey: e.refKey } : {}),
        ...(e.detail ? { detail: e.detail } : {}),
      })),
    isHypothesis: o.isHypothesis,
  }
  if (o.videoId) packed.videoId = o.videoId
  if (o.percentile !== undefined && o.percentile !== null) packed.percentile = o.percentile
  if (o.deltaRatio !== undefined && o.deltaRatio !== null) packed.deltaRatio = o.deltaRatio
  if (o.hypothesisQuestion) packed.hypothesisQuestion = o.hypothesisQuestion
  return packed
}

export interface BuildPackageInput {
  scope: AnalysisPackage['scope']
  channelSummary: AnalysisPackage['channelSummary']
  dataCoverage: AnalysisPackage['dataCoverage']
  confidence: AnalysisPackage['confidence']
  baselines: AnalysisPackage['baselines']
  featureDefinitions: AnalysisPackage['featureDefinitions']
  observations: Observation[]
  anomalies: Array<Record<string, unknown>>
  rankedVideos: Array<Record<string, unknown>>
  cohortComparisons: Array<Record<string, unknown>>
  formatComparison: Record<string, unknown> | null
  unresolvedQuestions: string[]
  missingData: string[]
}

/**
 * Nhiệm vụ giao cho Cursor.
 *
 * Cố ý viết dưới dạng câu hỏi SUY LUẬN, và nói thẳng những gì KHÔNG được làm.
 * Đây là phần chuyển giao giữa hai tầng: nếu để mơ hồ, LLM sẽ quay lại tính
 * toán số liệu — thứ tầng tất định đã làm xong và làm chính xác hơn.
 */
export const ANALYSIS_TASKS: string[] = [
  'Diễn giải Ý NGHĨA khi các tín hiệu đi cùng nhau; không tính lại bất kỳ chỉ số nào.',
  'Với mỗi giả thuyết ứng viên, đánh giá nó MẠNH hay YẾU và nêu rõ bằng chứng nào trong gói ủng hộ hoặc bác bỏ.',
  'Đề xuất thay đổi nội dung cụ thể, xếp theo mức tác động kỳ vọng và công sức bỏ ra.',
  'Đề xuất thí nghiệm kiểm chứng được cho các giả thuyết chưa ngã ngũ, kèm tiêu chí thành công.',
  'Chỉ ra bằng chứng BỔ SUNG nào sẽ giải toả được phần chưa chắc chắn lớn nhất.',
  'Nêu rõ những gì KHÔNG kết luận được từ dữ liệu hiện có.',
  'KHÔNG bịa chỉ số không có trong gói. KHÔNG khẳng định nhân quả khi bằng chứng chỉ cho thấy tương quan.',
]

export function buildPackage(input: BuildPackageInput): AnalysisPackage {
  const limits = ANALYSIS_THRESHOLDS.limits

  const nonHypotheses = input.observations.filter((o) => !o.isHypothesis)
  const hypotheses = input.observations.filter((o) => o.isHypothesis)

  const positives = nonHypotheses
    .filter((o) => o.polarity === 'POSITIVE')
    .sort((a, b) => a.orderKey.localeCompare(b.orderKey))
  const negatives = nonHypotheses
    .filter((o) => o.polarity === 'NEGATIVE')
    .sort((a, b) => a.orderKey.localeCompare(b.orderKey))
  const neutrals = nonHypotheses
    .filter((o) => o.polarity === 'NEUTRAL')
    .sort((a, b) => a.orderKey.localeCompare(b.orderKey))

  const includedPositives = positives.slice(0, limits.topPositiveObservations)
  const includedNegatives = negatives.slice(0, limits.topNegativeObservations)
  const includedHypotheses = [...hypotheses]
    .sort((a, b) => a.orderKey.localeCompare(b.orderKey))
    .slice(0, limits.hypothesisCandidates)

  const pkg: AnalysisPackage = {
    schemaVersion: PACKAGE_SCHEMA_VERSION,
    algorithmVersion: ANALYSIS_ALGORITHM_VERSION,
    scope: input.scope,
    channelSummary: input.channelSummary,
    dataCoverage: input.dataCoverage,
    confidence: input.confidence,
    baselines: input.baselines,
    featureDefinitions: input.featureDefinitions,
    observations: [...includedPositives, ...includedNegatives, ...neutrals].map(packObservation),
    anomalies: input.anomalies.slice(0, limits.topAnomalies),
    rankedVideos: input.rankedVideos.slice(0, limits.rankedVideos),
    cohortComparisons: input.cohortComparisons.slice(0, limits.cohortSummaries),
    formatComparison: input.formatComparison,
    hypothesisCandidates: includedHypotheses.map(packObservation),
    unresolvedQuestions: input.unresolvedQuestions,
    missingData: input.missingData,
    analysisTasks: ANALYSIS_TASKS,
    limitsApplied: {
      positiveObservations: { included: includedPositives.length, total: positives.length },
      negativeObservations: { included: includedNegatives.length, total: negatives.length },
      anomalies: { included: Math.min(input.anomalies.length, limits.topAnomalies), total: input.anomalies.length },
      rankedVideos: { included: Math.min(input.rankedVideos.length, limits.rankedVideos), total: input.rankedVideos.length },
      cohorts: { included: Math.min(input.cohortComparisons.length, limits.cohortSummaries), total: input.cohortComparisons.length },
      hypotheses: { included: includedHypotheses.length, total: hypotheses.length },
      truncatedForSize: false,
    },
  }

  // Trần cứng kích thước.
  //
  // Cắt LẶP rồi kiểm lại từng vòng: một lần cắt duy nhất không đảm bảo điều gì,
  // vì phần quan sát trung tính, cohort hay tải trọng bằng chứng vẫn có thể đủ
  // lớn để gói tiếp tục vượt trần trong khi `truncatedForSize` đã bật — tức là
  // báo "đã cắt" mà vẫn quá khổ.
  //
  // Cắt thì phải NÓI RA: gói im lặng bị cắt sẽ khiến LLM tưởng nó đã thấy toàn
  // bộ bằng chứng.
  const shrinkSteps: Array<() => boolean> = [
    () => trim(pkg.rankedVideos, Math.max(5, Math.floor(limits.rankedVideos / 2)), (n) => {
      pkg.limitsApplied.rankedVideos.included = n
    }),
    () => trim(pkg.observations, limits.topPositiveObservations + limits.topNegativeObservations),
    () => trim(pkg.cohortComparisons, Math.max(2, Math.floor(limits.cohortSummaries / 2)), (n) => {
      pkg.limitsApplied.cohorts.included = n
    }),
    () => trim(pkg.anomalies, Math.max(3, Math.floor(limits.topAnomalies / 2)), (n) => {
      pkg.limitsApplied.anomalies.included = n
    }),
    () => trim(pkg.rankedVideos, 5, (n) => {
      pkg.limitsApplied.rankedVideos.included = n
    }),
    () => trim(pkg.observations, 10),
  ]

  for (const step of shrinkSteps) {
    if (packageBytes(pkg) <= limits.maxPackageBytes) break
    if (step()) pkg.limitsApplied.truncatedForSize = true
  }

  // Nếu vẫn quá khổ sau khi đã cắt hết phần cắt được, phần BẮT BUỘC (định nghĩa
  // feature, phạm vi, độ phủ) tự nó đã vượt trần. Im lặng để lọt là sai; báo
  // thẳng để người vận hành nới trần hoặc thu gọn danh mục feature.
  const finalBytes = packageBytes(pkg)
  if (finalBytes > limits.maxPackageBytes) {
    throw new Error(
      `Gói phân tích ${finalBytes} byte vẫn vượt trần ${limits.maxPackageBytes} sau khi đã cắt hết ` +
        `phần cắt được. Nới maxPackageBytes hoặc giảm số định nghĩa feature.`,
    )
  }

  return pkg
}

/** Cắt mảng về `size`; trả true nếu thực sự có cắt. */
function trim(arr: unknown[], size: number, onTrim?: (n: number) => void): boolean {
  if (arr.length <= size) return false
  arr.length = size
  onTrim?.(size)
  return true
}
