import { z } from 'zod'

/**
 * Schema NGHIÊM NGẶT cho output của Cursor.
 *
 * `.strict()` ở mọi tầng, có chủ đích: một trường lạ nghĩa là mô hình đang bịa
 * ra cấu trúc riêng, và im lặng bỏ qua nó sẽ khiến ta tưởng đã hiểu output
 * trong khi thực tế thì không. Thà từ chối và sửa còn hơn.
 *
 * Mảng đều có TRẦN. Không phải để tiết kiệm byte mà để ép ưu tiên: "3 khuyến
 * nghị mạnh" hữu ích hơn "20 gợi ý chung chung", và trần là cách duy nhất buộc
 * điều đó xảy ra.
 */

export const CURSOR_OUTPUT_SCHEMA_VERSION = '2.1'

/**
 * Phiên bản 2.0 thêm `metricClaims` BẮT BUỘC.
 *
 * Lý do: năm lô đo ổn định liên tiếp hỏng vì bộ kiểm định phải ĐOÁN xem một
 * tính từ đang bổ nghĩa cho danh từ nào. Bảy cấu trúc ngữ pháp khác nhau đã
 * đánh bại nó — "và", "nếu…sẽ", "thay vì", "để", "làm", "với", và từ ghép
 * "high-retention". Vấn đề không nằm ở từng mẫu regex mà ở chỗ suy đoán ngữ
 * pháp từ văn xuôi.
 *
 * 2.0 buộc mô hình KHAI BÁO ngữ nghĩa thay vì để ta đoán. Payload 1.0 bị từ
 * chối cho lần chạy mới.
 */
export const LEGACY_SCHEMA_VERSIONS = ['1.0', '2.0'] as const

export const confidenceEnum = z.enum(['LOW', 'MEDIUM', 'HIGH'])
export const findingTypeEnum = z.enum(['OBSERVATION', 'SYNTHESIS', 'LIMITATION'])
export const priorityEnum = z.enum(['P0', 'P1', 'P2'])
export const recommendationCategoryEnum = z.enum([
  'CONTINUE',
  'STOP',
  'INVESTIGATE',
  'TEST',
  'COLLECT_DATA',
])
export const levelEnum = z.enum(['LOW', 'MEDIUM', 'HIGH'])

const idPattern = (prefix: string) => z.string().regex(new RegExp(`^${prefix}-\\d{3}$`))

/**
 * Chỉ số NHẠY CẢM — những chỉ số mà một kết luận sai gây hại nhất.
 *
 * Danh sách này chỉ nói "đây là các chỉ số cần cảnh giác". Việc chỉ số nào
 * THỰC SỰ thiếu dữ liệu được đọc từ `dataCoverage` của gói lúc kiểm định, không
 * hardcode — nếu một kênh có impressions thật thì quy tắc tự nới ra.
 */
export const SENSITIVE_METRICS = ['impressions', 'impression_ctr', 'thumbnail', 'packaging'] as const

/**
 * Chỉ số được phép đứng tên ở `subjectMetric` / `relatedMetric`.
 *
 * Bao gồm cả chỉ số CÓ dữ liệu, vì một phát biểu về giới hạn phương pháp
 * thường có chủ ngữ là chỉ số có dữ liệu và chỉ NHẮC TỚI chỉ số thiếu:
 * "cỡ mẫu views thấp làm CTR nhiễu" -> subject = sample_size, related = ctr.
 * Thiếu các chỉ số này thì câu hợp lệ đó không có cách nào khai đúng.
 */
export const CLAIM_METRICS = [
  ...SENSITIVE_METRICS,
  'views',
  'views_d7',
  'retention',
  'average_view_percentage',
  'watch_time',
  'reach',
  'subscribers',
  'engagement',
  'sample_size',
  'publish_cadence',
  'data_coverage',
  'NONE',
] as const

export const claimTypeEnum = z.enum([
  'OBSERVATION',
  'COMPARISON',
  'CAUSAL',
  'DIAGNOSTIC_PLAN',
  'METHODOLOGY_LIMITATION',
  'RECOMMENDATION',
])

export const judgementEnum = z.enum([
  'HIGH',
  'LOW',
  'INCREASED',
  'DECREASED',
  'EFFECTIVE',
  'INEFFECTIVE',
  'UNKNOWN',
  'NOT_APPLICABLE',
])

export const assertionStatusEnum = z.enum([
  'ASSERTED',
  'CONDITIONAL',
  'QUESTION',
  'NEGATED_ACTION',
  'LIMITATION',
])

/** Nơi câu văn nằm trong output — để đối chiếu văn xuôi với khai báo. */
export const claimSourceEnum = z.enum([
  'ANALYSIS_SUMMARY',
  'KEY_FINDING',
  'HYPOTHESIS',
  'RECOMMENDATION',
  'EXPERIMENT',
  'MANUAL_REVIEW',
  'DATA_REQUEST',
  'NON_CONCLUSION',
])

/**
 * Tham chiếu ỔN ĐỊNH tới ô văn bản gốc.
 *
 * Neo vào DANH TÍNH (`itemId`), không neo vào vị trí mảng. JSON Pointer suy ra
 * được chỉ dùng để chẩn đoán, không phải nguồn sự thật — đảo thứ tự `keyFindings`
 * không được làm hỏng tham chiếu.
 *
 * `ordinal` chỉ định vị TRONG một field mảng của MỘT item. Bề mặt vị trí còn lại
 * này được xử lý fail-closed: nếu field chứa hai phần tử trùng nội dung thì mọi
 * tham chiếu vào đó là MẬP MỜ và bị chặn, thay vì phân giải bừa.
 */
export const sourceRefSchema = z
  .object({
    section: claimSourceEnum,
    /** 'F-001' | 'H-001' | 'R-001' | 'E-001'; RỖNG với ANALYSIS_SUMMARY và mảng cấp cao nhất. */
    itemId: z.string().max(20),
    field: z.string().min(1).max(40),
    /** Vị trí trong field mảng; 0 với field chuỗi đơn. */
    ordinal: z.number().int().min(0).max(20).default(0),
  })
  .strict()

/**
 * MỘT phát biểu liên quan tới chỉ số, được KHAI BÁO TƯỜNG MINH.
 *
 * `subjectMetric` là thứ BỊ PHÁN XÉT; `relatedMetric` là thứ chỉ ĐƯỢC NHẮC TỚI.
 *
 * KHÔNG còn `text`. Schema 2.0 bắt mô hình sao chép nguyên văn câu của chính nó,
 * và toàn bộ lô 2.0 hỏng vì hai bản văn bản lệch nhau (55 lỗi "khớp mập mờ", 24
 * claim mồ côi). 2.1 TRỎ tới ô gốc, nên chỉ còn MỘT bản để kiểm.
 */
export const metricClaimSchema = z
  .object({
    id: idPattern('MC'),
    claimType: claimTypeEnum,
    subjectMetric: z.enum(CLAIM_METRICS),
    relatedMetric: z.enum(CLAIM_METRICS).default('NONE'),
    judgement: judgementEnum,
    assertionStatus: assertionStatusEnum,
    evidenceIds: z.array(z.string().max(120)).max(12).default([]),
    requiresMissingnessDisclosure: z.boolean().default(false),
    sourceRef: sourceRefSchema,
  })
  .strict()

export const keyFindingSchema = z
  .object({
    id: idPattern('F'),
    statement: z.string().min(10).max(600),
    findingType: findingTypeEnum,
    confidence: confidenceEnum,
    evidenceIds: z.array(z.string().max(120)).max(12),
    supportingReasoning: z.string().min(10).max(1200),
    contradictingEvidenceIds: z.array(z.string().max(120)).max(12).default([]),
    limitations: z.array(z.string().max(400)).max(6).default([]),
  })
  .strict()

export const hypothesisSchema = z
  .object({
    id: idPattern('H'),
    statement: z.string().min(10).max(600),
    // Chỉ một giá trị hợp lệ: tầng này KHÔNG kiểm chứng được giả thuyết nào.
    status: z.literal('UNVERIFIED'),
    confidence: confidenceEnum,
    supportingEvidenceIds: z.array(z.string().max(120)).max(12),
    contradictingEvidenceIds: z.array(z.string().max(120)).max(12).default([]),
    missingEvidence: z.array(z.string().max(300)).max(8),
    validationMethod: z.string().min(10).max(800),
  })
  .strict()

export const recommendationSchema = z
  .object({
    id: idPattern('R'),
    action: z.string().min(10).max(600),
    priority: priorityEnum,
    category: recommendationCategoryEnum,
    rationale: z.string().min(10).max(1200),
    evidenceIds: z.array(z.string().max(120)).max(12),
    expectedValue: levelEnum,
    effort: levelEnum,
    reversibility: levelEnum,
    measurementFeasibility: levelEnum,
    risks: z.array(z.string().max(400)).max(6).default([]),
    successMetric: z.string().min(3).max(400),
  })
  .strict()

export const experimentSchema = z
  .object({
    id: idPattern('E'),
    hypothesisId: idPattern('H'),
    change: z.string().min(10).max(600),
    baseline: z.string().min(3).max(400),
    successMetrics: z.array(z.string().max(300)).min(1).max(5),
    minimumWindowDays: z.number().int().min(1).max(365),
    sampleLimitations: z.array(z.string().max(400)).max(6).default([]),
    stopConditions: z.array(z.string().max(300)).min(1).max(5),
    interpretationRisks: z.array(z.string().max(400)).min(1).max(6),
  })
  .strict()

/** Mục cần rà soát thủ công: một VIDEO hoặc một COHORT. */
export const manualReviewTargetSchema = z
  .object({
    targetType: z.enum(['VIDEO', 'COHORT']),
    /** youtubeVideoId khi VIDEO; khoá cohort khi COHORT. */
    targetId: z.string().min(1).max(120),
    reason: z.string().min(5).max(500),
    evidenceIds: z.array(z.string().max(120)).max(12).default([]),
    reviewQuestions: z.array(z.string().max(300)).min(1).max(6),
  })
  .strict()

export const dataRequestSchema = z
  .object({
    metricOrArtifact: z.string().min(2).max(200),
    reason: z.string().min(5).max(500),
    decisionUnlocked: z.string().min(5).max(500),
  })
  .strict()

/**
 * `selfCheck` là lời TỰ KHAI của mô hình, KHÔNG phải bằng chứng.
 *
 * Bộ kiểm định chạy độc lập và có quyền phủ quyết. Giá trị của trường này là ở
 * chỗ nó bắt mô hình tự soát lại, không phải ở chỗ ta tin nó.
 */
export const selfCheckSchema = z
  .object({
    usedOnlyProvidedEvidence: z.boolean(),
    recomputedMetrics: z.boolean(),
    madeCausalClaims: z.boolean(),
    madeCtrOrImpressionClaims: z.boolean(),
    allFindingEvidenceResolved: z.boolean(),
  })
  .strict()

export const cursorOutputSchema = z
  .object({
    schemaVersion: z.literal(CURSOR_OUTPUT_SCHEMA_VERSION),
    analysisSummary: z
      .object({
        overallAssessment: z.string().min(20).max(2000),
        confidence: confidenceEnum,
        confidenceRationale: z.string().min(10).max(1000),
        primaryConstraint: z.string().min(5).max(600),
      })
      .strict(),
    keyFindings: z.array(keyFindingSchema).min(1).max(10),
    hypotheses: z.array(hypothesisSchema).max(8),
    recommendations: z.array(recommendationSchema).max(10),
    experiments: z.array(experimentSchema).max(5),
    manualReviewTargets: z.array(manualReviewTargetSchema).max(10),
    dataRequests: z.array(dataRequestSchema).max(10),
    explicitNonConclusions: z.array(z.string().max(500)).min(1).max(10),
    /**
     * MỌI phát biểu nhắc tới chỉ số nhạy cảm phải có mặt ở đây.
     *
     * Văn xuôi được phép GIẢI THÍCH một claim đã khai, nhưng không được nêu một
     * phát biểu mới về chỉ số nhạy cảm mà không có claim tương ứng — lưới an
     * toàn từ vựng sẽ bắt trường hợp đó.
     */
    /**
     * Trần RỘNG, có chủ đích.
     *
     * Các trần khác ép ƯU TIÊN ("3 khuyến nghị mạnh hơn 20 gợi ý chung chung").
     * Trần này thì không: số claim do NỘI DUNG quyết định — mỗi câu nhắc tới chỉ
     * số nhạy cảm phải có đúng một claim. Đặt trần thấp là tự mâu thuẫn với yêu
     * cầu khai báo đầy đủ: một output có 40 câu như thế BẮT BUỘC phải có 40
     * claim, và trần 30 khiến việc tuân thủ trở thành bất khả thi.
     *
     * Ca thật: lần chạy thăm dò hinh_su sinh 32 claim và bị từ chối, rồi lần
     * sửa duy nhất khả dĩ (xoá bớt) lại vi phạm quy tắc bất biến ngữ nghĩa —
     * bế tắc hoàn toàn do lỗi thiết kế của trần này.
     */
    metricClaims: z.array(metricClaimSchema).max(120),
    selfCheck: selfCheckSchema,
  })
  .strict()

export type CursorOutput = z.infer<typeof cursorOutputSchema>
export type KeyFinding = z.infer<typeof keyFindingSchema>
export type Hypothesis = z.infer<typeof hypothesisSchema>
export type Recommendation = z.infer<typeof recommendationSchema>
export type Experiment = z.infer<typeof experimentSchema>
export type MetricClaim = z.infer<typeof metricClaimSchema>
export type SourceRef = z.infer<typeof sourceRefSchema>

/** Trần mảng, dùng cả trong prompt lẫn trong kiểm định để hai bên không lệch. */
export const OUTPUT_LIMITS = {
  keyFindings: 10,
  hypotheses: 8,
  recommendations: 10,
  experiments: 5,
  manualReviewTargets: 10,
  dataRequests: 10,
  explicitNonConclusions: 10,
  metricClaims: 120,
} as const
