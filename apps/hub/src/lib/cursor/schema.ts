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

/* -------------------------------------------------------------------------
 * SÁU HỢP ĐỒNG, SÁU PHIÊN BẢN — không gộp
 *
 * 2.1 dùng MỘT `schemaVersion` che ba hợp đồng khác nhau, nên khi một lô hỏng
 * thì không truy vấn được nó hỏng vì đổi prompt, đổi schema hay đổi validator.
 * Kiến trúc hai lượt có sáu hợp đồng độc lập; mỗi cái phiên bản hoá riêng.
 *
 * Chi tiết và quy tắc "đổi cái nào thì tăng cái nào":
 * creator_specs/PHASE4_1_DECLARATION_PASS_DESIGN.md mục 4.1.
 * ---------------------------------------------------------------------- */

/** 1. Hình dạng VĂN XUÔI của lượt phân tích. */
export const ANALYSIS_SCHEMA_VERSION = '3.0'

/**
 * 3. Bộ SINH NGHĨA VỤ — hợp đồng NGANG HÀNG với schema, không phải chi tiết cài đặt.
 *
 * Nó quyết định ô nào PHẢI được khai báo, tức nó định nghĩa "đầy đủ" nghĩa là
 * gì. Đổi `enumerateUnits`, đổi cách nhận diện ô nhạy cảm, hay đổi
 * `allowedAssertionStatuses` mà không tăng số này là đổi thước đo giữa chừng.
 */
/*
 * 1.0 -> 1.1 (2026-08-07): `sensitive.ts` nhận thêm "ảnh bìa"/"hình bìa" cho
 * `thumbnail`. Đó là đổi ĐỊNH NGHĨA "ô nào phải khai báo" — đúng loại thay đổi
 * mà số này tồn tại để đánh dấu — nên số đo trước và sau KHÔNG được gộp.
 *
 * 1.1 -> 1.2 (2026-08-13): bảng bí danh nay tự sinh dạng camelCase của chính
 * khoá, nên một ô viết `impressionCtr` / `viewsD7` / `averageViewPercentage`
 * mới được nhận là ô nhạy cảm. Ô trước đây KHÔNG sinh nghĩa vụ thì nay CÓ —
 * đúng nghĩa đổi thước đo, nên lô thăm dò 2026-08-13 (0/18, chạy ở 1.1) KHÔNG
 * được gộp với bất kỳ lô nào chạy ở 1.2.
 */
export const OBLIGATION_GENERATOR_VERSION = '1.2'

/** 4. Hình dạng KHAI BÁO của lượt hai. */
export const DECLARATION_SCHEMA_VERSION = '3.0'

/** 6. Bộ kiểm định HỢP NHẤT — tăng khi bất kỳ quy tắc O/U/S nào đổi. */
/*
 * 1.0 -> 1.1 (2026-08-13): R0b (`subject_metric_not_in_text`) miễn trừ
 * `data_coverage`. Trước đó R0b và `methodology_subject_also_missing` đối nghịch
 * nhau, khiến câu NÊU THIẾU DỮ LIỆU — câu bắt buộc phải có trong mọi bài phân
 * tích của miền này — không còn bản khai hợp lệ nào (đo được: 113 lần trên một
 * lô). Đây là sửa MÂU THUẪN, không phải nới luật; xem chú thích tại R0b.
 */
/*
 * 1.1 -> 1.2 (2026-08-13): `MODALITY_MARKERS.LIMITATION` nhận thêm bốn cách nói
 * BẤT KHẢ của tiếng Việt (đo trên 383 câu thật: bảng cũ bỏ sót 105 câu
 * "không … được", 104 câu "thiếu", 68 câu "không có"), kèm chốt bù R1b cấm
 * `subjectMetric = data_coverage` mang phán xét. Lô 4 chạy ở 1.1 KHÔNG gộp
 * được với lô sau.
 */
/*
 * 1.2 -> 1.3 (2026-08-13): ba khoảng trống từ vựng đo được trên lô 5 —
 * CONDITIONAL thiếu `khi` trần, QUESTION thiếu `có nên`/`hay`, LIMITATION thiếu
 * `bằng không`/`bằng 0`. Bảng năm luật CẤM tổ hợp tách ra thành
 * `CLAIM_CONTRADICTIONS` để prompt sinh từ nó, không chép tay nữa.
 */
/*
 * 1.3 -> 1.4 (2026-08-13): `undeclared_metric_in_claim_text` miễn cho claim
 * KHÔNG mang phán xét. Câu TỪ CHỐI KẾT LUẬN thường nhắc 3–4 chỉ số nhạy cảm
 * (đo trên lô 6: 14/17 lần chặn), trong khi một claim chỉ có HAI ô chỉ số và
 * mỗi nghĩa vụ chỉ có MỘT claim — nên câu đúng hợp đồng nhất lại không khai nổi.
 */
/*
 * 1.4 -> 1.5 (2026-08-17): R1c — `judgement=UNKNOWN` không được CHE một phán xét
 * có thật trong câu. Codex vòng 21 tìm ra: ba miễn trừ của C-14..C-16 ghép lại
 * cho phép "Thumbnail kém dù thiếu impressions/CTR" khai UNKNOWN+LIMITATION và
 * đi lọt hoàn toàn. Nguyên nhân gốc: `judgemental` suy ra từ TRƯỜNG KHAI BÁO,
 * không từ văn xuôi — một bản tự khai không thể là bằng chứng về chính nó.
 */
/*
 * 1.5 -> 1.6 (2026-08-17): R1c chỉ bịt MỘT cửa. Tự rà soát bằng CHẠY cho thấy
 * cùng câu "Thumbnail kém …" chỉ cần đổi `assertionStatus` sang NEGATED_ACTION /
 * CONDITIONAL / QUESTION là ra 0 blocker — vì 1.5 vẫn hỏi bản khai trước khi đọc
 * câu. Nay quy tắc bỏ hẳn bản khai và chỉ hỏi VỊ TRÍ trong câu: (a) chỉ số nào
 * sát từ phán xét nhất mới là kẻ bị phán xét, (b) từ tình thái phải đứng TRƯỚC
 * phán xét thì mới bao trùm được nó. Đổi tên luật thành
 * `judgement_on_missing_metric_in_text` vì nó không còn nói về `judgement` khai.
 */
export const COMPOSITE_VALIDATOR_VERSION = '1.6'

/**
 * Phiên bản của KẾT QUẢ HỢP NHẤT — thứ được ghi vào `cursor_analysis_result`.
 *
 * 3.0 tách việc VIẾT khỏi việc KHAI. Bốn lần thăm dò của 2.1 cho thấy mô hình
 * trỏ `sourceRef` đúng 100% (R=0 cả bốn lần) nhưng ĐẾM SÓT ô phải khai, dao động
 * 2–19 lỗi và nghịch chiều với số claim nó viết. Việc đếm ô là việc SỔ SÁCH mà
 * `enumerateUnits` tính được tất định — 3.0 lấy nó khỏi tay mô hình.
 */
export const CURSOR_OUTPUT_SCHEMA_VERSION = '3.0'

/**
 * Payload của các bản cũ bị TỪ CHỐI dứt khoát cho lần chạy mới.
 *
 * 2.1 vào danh sách này vì nó mang `metricClaims` do MÔ HÌNH viết, tức không có
 * tập nghĩa vụ nào để đối chiếu. Chấp nhận nó nghĩa là chấp nhận một payload
 * không có bảo đảm đầy đủ — đúng thứ 3.0 sinh ra để có.
 */
export const LEGACY_SCHEMA_VERSIONS = ['1.0', '2.0', '2.1'] as const

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
 * `section` -> TÊN TRƯỜNG của nó trong output.
 *
 * Đây là chỗ DUY NHẤT nối hằng số section với hình dạng schema. Danh sách
 * `field` hợp lệ của mỗi section được SINH RA từ schema qua bảng này (xem
 * `sourceRefSections()` trong prompt.ts), nên thêm một trường văn bản vào schema
 * là prompt tự biết — không có bước "nhớ cập nhật prompt" nào để quên.
 *
 * Có test buộc bảng này phủ ĐÚNG mọi giá trị của `claimSourceEnum` và mọi tên
 * trường phải tồn tại thật trong `cursorOutputSchema`.
 */
export const CLAIM_SOURCE_PROPERTY = {
  ANALYSIS_SUMMARY: 'analysisSummary',
  KEY_FINDING: 'keyFindings',
  HYPOTHESIS: 'hypotheses',
  RECOMMENDATION: 'recommendations',
  EXPERIMENT: 'experiments',
  MANUAL_REVIEW: 'manualReviewTargets',
  DATA_REQUEST: 'dataRequests',
  NON_CONCLUSION: 'explicitNonConclusions',
} as const satisfies Record<z.infer<typeof claimSourceEnum>, string>

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

/**
 * THÂN của một bản phân tích: mọi thứ trừ `schemaVersion` và `metricClaims`.
 *
 * Dùng chung cho hai schema để chúng KHÔNG THỂ lệch nhau. Kết quả hợp nhất phải
 * chứa đúng văn xuôi của lượt phân tích; định nghĩa hai lần là mở đường cho hai
 * hình dạng khác nhau mang cùng một cái tên.
 */
const analysisBodyShape = {
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
  selfCheck: selfCheckSchema,
} as const

/**
 * LƯỢT 1 — chỉ VĂN XUÔI. KHÔNG có `metricClaims`.
 *
 * `.strict()` làm phần việc quan trọng nhất ở đây: mô hình KHÔNG THỂ tự khai
 * sớm. Một output lượt 1 kèm `metricClaims` bị từ chối toàn bộ, vì claim viết
 * trước khi có tập nghĩa vụ là claim không đối chiếu được với gì cả.
 */
export const cursorAnalysisSchema = z
  .object({ schemaVersion: z.literal(ANALYSIS_SCHEMA_VERSION), ...analysisBodyShape })
  .strict()

/**
 * KẾT QUẢ HỢP NHẤT — văn xuôi lượt 1 + `metricClaims` do ỨNG DỤNG ghép.
 *
 * Hình dạng `metricClaim` giữ NGUYÊN như 2.1, nên toàn bộ quy tắc S và mọi báo
 * cáo phía sau không phải viết lại. Cái đổi là NGUỒN GỐC của mảng này: nó không
 * còn do mô hình viết mà do ghép (nghĩa vụ ⋈ khai báo) theo `id`.
 *
 * Trần 120 giữ nguyên: số claim do NỘI DUNG quyết định, và nay nó bằng đúng số
 * ô nhạy cảm mà `enumerateUnits` đếm được — không phải một con số mô hình chọn.
 */
export const cursorOutputSchema = z
  .object({
    schemaVersion: z.literal(CURSOR_OUTPUT_SCHEMA_VERSION),
    ...analysisBodyShape,
    metricClaims: z.array(metricClaimSchema).max(120),
  })
  .strict()

/* -------------------------------------------------------------------------
 * TẬP NGHĨA VỤ KHAI BÁO — do ỨNG DỤNG sinh, không do mô hình
 * ---------------------------------------------------------------------- */

/**
 * MỘT nghĩa vụ khai báo: "ô này nhắc chỉ số nhạy cảm, hãy khai ngữ nghĩa của nó".
 *
 * Mọi trường ở đây là SỰ KIỆN do thuật toán tính, không phải phán xét. Mô hình
 * đọc chúng và không được sửa chúng — schema lượt 2 không có chỗ nào để sửa.
 */
export const claimObligationSchema = z
  .object({
    id: idPattern('MC'),
    sourceRef: sourceRefSchema,
    /** `section|itemId|field#ordinal` — danh tính Ô, gồm cả ordinal. */
    canonical: z.string().min(1).max(200),
    /** Con trỏ suy ra, chỉ để chẩn đoán. */
    pointer: z.string().min(1).max(200),
    /** VĂN BẢN THẬT tại ô, đã phân giải khỏi bản phân tích đóng băng. */
    resolvedText: z.string().min(1).max(2000),
    /** sha256 của `resolvedText` — nền của O-INV-2. */
    resolvedHash: z.string().length(64),
    /** Chỉ số nhạy cảm mà ô này nhắc tới; luôn ít nhất một, nếu không đã không thành nghĩa vụ. */
    mentionedMetrics: z.array(z.enum(SENSITIVE_METRICS)).min(1),
    /**
     * Tập `assertionStatus` hợp lệ cho ô này.
     *
     * Với ô NHÃN (`metricOrArtifact`, `missingEvidence`, `reviewQuestions`), cấu
     * trúc đã quy định hành vi lời nói nên tập này bị thu hẹp và KHÔNG chứa
     * `ASSERTED`. Tính sẵn ở đây thay vì bắt mô hình đoán.
     */
    allowedAssertionStatuses: z.array(assertionStatusEnum).min(1),
  })
  .strict()

export const claimObligationSetSchema = z
  .object({
    schemaVersion: z.literal(ANALYSIS_SCHEMA_VERSION),
    /*
     * CHUỖI, không phải `z.literal` — phép chặn nằm ở chặng hợp nhất.
     *
     * Ghim bằng `z.literal` ở đây làm `composite_generator_version_drift` thành
     * mã CHẾT: `loadCompositeInputs` parse tập nghĩa vụ trước, trả về sớm khi
     * parse hỏng, nên một tập sinh bởi bộ sinh 1.0 được báo là
     * `composite_obligation_set_malformed` ("hình dạng không đúng") và bị nâng
     * thành `systemFailure` — người vận hành đi tìm một hàng hỏng, trong khi
     * thứ họ gặp chỉ là RANH GIỚI PHIÊN BẢN.
     *
     * Fail-closed không đổi: `verifyCompositeInputs` vẫn chặn mọi phiên bản khác
     * bản đang chạy, chỉ là bằng đúng tên gọi của nó.
     */
    generatorVersion: z.string().min(1).max(32),
    /** Băm payload lượt 1 — neo O-INV-1. */
    analysisHash: z.string().length(64),
    obligations: z.array(claimObligationSchema).max(120),
  })
  .strict()

/* -------------------------------------------------------------------------
 * LƯỢT 2 — KHAI BÁO. Mô hình chỉ điền BẢY trường ngữ nghĩa.
 * ---------------------------------------------------------------------- */

/**
 * Một khai báo cho đúng một nghĩa vụ.
 *
 * KHÔNG có `sourceRef`, KHÔNG có `text`, KHÔNG có gì định vị. `.strict()` biến
 * điều 4 của hợp đồng ("không thêm, bớt, đảo, nhân bản, đổi mục tiêu") thành bất
 * khả BIỂU DIỄN thay vì một phép kiểm chạy sau — mô hình không có chỗ để viết ra
 * một mục tiêu khác.
 */
export const claimDeclarationSchema = z
  .object({
    /** PHẢI trùng `id` của một nghĩa vụ. Ghép theo đây, không theo thứ tự mảng. */
    id: idPattern('MC'),
    subjectMetric: z.enum(CLAIM_METRICS),
    relatedMetric: z.enum(CLAIM_METRICS).default('NONE'),
    claimType: claimTypeEnum,
    judgement: judgementEnum,
    assertionStatus: assertionStatusEnum,
    evidenceIds: z.array(z.string().max(120)).max(12).default([]),
    requiresMissingnessDisclosure: z.boolean().default(false),
  })
  .strict()

export const declarationOutputSchema = z
  .object({
    schemaVersion: z.literal(DECLARATION_SCHEMA_VERSION),
    /** Băm tập nghĩa vụ mà lượt này đang trả lời — neo O-INV-4. */
    obligationSetHash: z.string().length(64),
    declarations: z.array(claimDeclarationSchema).max(120),
  })
  .strict()

export type CursorAnalysis = z.infer<typeof cursorAnalysisSchema>
export type CursorOutput = z.infer<typeof cursorOutputSchema>
export type ClaimObligation = z.infer<typeof claimObligationSchema>
export type ClaimObligationSet = z.infer<typeof claimObligationSetSchema>
export type ClaimDeclaration = z.infer<typeof claimDeclarationSchema>
export type DeclarationOutput = z.infer<typeof declarationOutputSchema>
export type KeyFinding = z.infer<typeof keyFindingSchema>
export type Hypothesis = z.infer<typeof hypothesisSchema>
export type Recommendation = z.infer<typeof recommendationSchema>
export type Experiment = z.infer<typeof experimentSchema>
export type MetricClaim = z.infer<typeof metricClaimSchema>
export type SourceRef = z.infer<typeof sourceRefSchema>

/**
 * Vai của một execution trong kiến trúc hai lượt. HAI vai, không phải ba.
 *
 * Bản thiết kế đầu đề xuất thêm vai `REPAIR` và sửa trigger
 * `cursor_repair_version_immutable` (0020) để nó chỉ áp cho vai đó. Khi dựng
 * migration mới thấy điều đó KHÔNG cần thiết, và tránh được thì tốt hơn:
 *
 *  - retry đã được biểu diễn bằng `parent_execution_id` + `attempt_number`;
 *  - một lần sửa lỗi của lượt khai báo có cha là lần khai báo TRƯỚC ĐÓ, cùng vai,
 *    cùng mọi phiên bản — nên 0020 cho qua mà không phải đổi một dòng nào;
 *  - lượt khai báo nối về lượt phân tích bằng `analysis_execution_id`, KHÔNG bằng
 *    `parent_execution_id`, nên 0020 không bao giờ nhìn thấy quan hệ đó.
 *
 * Kết quả: một trigger đang chạy đúng KHÔNG bị đụng vào. Đổi phạm vi của nó là
 * việc phải kiểm lại toàn bộ chuỗi retry cũ; không đổi thì không phải kiểm.
 */
export const EXECUTION_ROLES = ['ANALYSIS', 'DECLARATION'] as const
export type ExecutionRole = (typeof EXECUTION_ROLES)[number]

/** Chặng kiểm định. Chỉ `COMPOSITE` mới cấp phép cho một kết quả chính thức. */
export const VALIDATION_STAGES = ['ANALYSIS', 'DECLARATION', 'COMPOSITE'] as const
export type ValidationStage = (typeof VALIDATION_STAGES)[number]

/* -------------------------------------------------------------------------
 * `sourceRef`: `section` / `field` hợp lệ — SINH TỪ SCHEMA
 *
 * Ba nơi cần biết danh sách này và KHÔNG được lệch nhau:
 *   - prompt: nói cho mô hình biết nó được phép trỏ vào đâu;
 *   - `resolveSourceRef`: từ chối ref trỏ ra ngoài danh sách;
 *   - `enumerateUnits`: quyết định ô nào bị đòi khai báo.
 * Ba danh sách viết tay thì sớm muộn cũng lệch; một bộ sinh thì không.
 * ---------------------------------------------------------------------- */

type ZodNode = { _def?: Record<string, unknown> }

function unwrapNode(node: unknown): ZodNode {
  let n = node as ZodNode
  while (n?._def && ['ZodDefault', 'ZodOptional', 'ZodNullable'].includes(n._def.typeName as string)) {
    n = n._def.innerType as ZodNode
  }
  return n
}

function shapeOf(node: ZodNode): Record<string, unknown> | null {
  if ((node?._def?.typeName as string) !== 'ZodObject') return null
  return (node._def!.shape as () => Record<string, unknown>)()
}

/**
 * Một trường có phải BỀ MẶT VĂN BẢN TỰ DO không.
 *
 * Quy tắc, không phải danh sách: chuỗi (hoặc mảng chuỗi) KHÔNG phải định danh.
 * Định danh nhận ra theo hai dấu hiệu độc lập —
 *   - có ràng buộc regex (`id`, `hypothesisId`): dạng cố định, không phải văn xuôi;
 *   - tên kết thúc bằng `Id`/`Ids` (`targetId`, `evidenceIds`, …).
 *
 * ENUM bị loại vì là ZodEnum, không phải ZodString — dù lúc chạy giá trị của nó
 * VẪN là chuỗi. Đây là lý do phép lọc phải hỏi SCHEMA chứ không hỏi `typeof`:
 * một ref trỏ vào `keyFindings[0].confidence` đọc ra "MEDIUM" hoàn toàn trót lọt
 * nếu chỉ kiểm kiểu lúc chạy.
 *
 * Nhờ là QUY TẮC, một trường văn bản mới thêm vào schema tự động lọt vào danh
 * sách này, thay vì phải nhớ đăng ký ở một chỗ thứ hai.
 */
function proseFieldsOf(objectNode: ZodNode): Array<{ name: string; array: boolean }> {
  const shape = shapeOf(objectNode)
  if (!shape) return []
  const out: Array<{ name: string; array: boolean }> = []
  for (const [name, raw] of Object.entries(shape)) {
    if (/Ids?$/u.test(name)) continue
    const node = unwrapNode(raw)
    const typeName = node?._def?.typeName as string | undefined
    if (typeName === 'ZodString') {
      const checks = (node._def!.checks as Array<{ kind: string }>) ?? []
      if (checks.some((c) => c.kind === 'regex')) continue
      out.push({ name, array: false })
      continue
    }
    if (typeName === 'ZodArray') {
      const el = unwrapNode(node._def!.type)
      if ((el?._def?.typeName as string) === 'ZodString') out.push({ name, array: true })
    }
  }
  return out
}

/** Ví dụ id suy ra thẳng từ regex của schema: `^F-\d{3}$` -> `F-001`. */
function idExampleFrom(objectNode: ZodNode): string {
  const shape = shapeOf(objectNode)
  const idNode = unwrapNode(shape?.['id'])
  if ((idNode?._def?.typeName as string) !== 'ZodString') return ''
  const checks = (idNode._def!.checks as Array<{ kind: string; regex?: RegExp }>) ?? []
  const re = checks.find((c) => c.kind === 'regex')?.regex
  if (!re) return ''
  return re.source
    .replace(/^\^/u, '')
    .replace(/\$$/u, '')
    .replace(/\\d\{(\d+)\}/u, (_m, n: string) => String(1).padStart(Number(n), '0'))
}

export interface SourceSectionSpec {
  section: string
  /**
   * ITEM       — mảng đối tượng CÓ id: `itemId` là id đó.
   * INDEXED    — mảng đối tượng KHÔNG id: `itemId` rỗng, `field` dùng "tên@N".
   * SINGLETON  — đối tượng đơn: `itemId` rỗng.
   * TEXT_ARRAY — mảng chuỗi cấp cao nhất: `itemId` rỗng, `ordinal` chọn phần tử.
   */
  kind: 'ITEM' | 'INDEXED' | 'SINGLETON' | 'TEXT_ARRAY'
  itemIdExample: string
  fields: Array<{ name: string; array: boolean }>
}

export function sourceRefSections(): SourceSectionSpec[] {
  const shape = shapeOf(unwrapNode(cursorOutputSchema))!
  return (Object.entries(CLAIM_SOURCE_PROPERTY) as Array<[string, string]>).map(
    ([section, property]) => {
      const node = unwrapNode(shape[property])
      const typeName = node?._def?.typeName as string | undefined

      if (typeName === 'ZodArray') {
        const el = unwrapNode(node._def!.type)
        if ((el?._def?.typeName as string) === 'ZodString') {
          return {
            section,
            kind: 'TEXT_ARRAY' as const,
            itemIdExample: '',
            fields: [{ name: property, array: true }],
          }
        }
        const itemIdExample = idExampleFrom(el)
        return {
          section,
          kind: itemIdExample ? ('ITEM' as const) : ('INDEXED' as const),
          itemIdExample,
          fields: proseFieldsOf(el),
        }
      }
      return { section, kind: 'SINGLETON' as const, itemIdExample: '', fields: proseFieldsOf(node) }
    },
  )
}

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
