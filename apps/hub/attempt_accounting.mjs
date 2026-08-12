/**
 * KẾ TOÁN LẦN THỬ — tách riêng để KIỂM ĐƯỢC.
 *
 * Phần này quyết định hai con số của lô chính thức: mẫu số ("chạy bao nhiêu lần
 * thử") và tử số ("bao nhiêu lần cho ra hiện vật chính thức"). Khi nó nằm lẫn
 * trong script in bảng, không test nào với tới, và rà soát đối kháng đã tìm ra
 * hai sai sót — cả hai đều đẩy con số theo hướng LẠC QUAN:
 *
 *   1. Mẫu số đếm cả lượt KHAI BÁO. Lượt khai báo đầu tiên cũng có
 *      `parent_execution_id = NULL`, nên mỗi lần chạy hoá hai lần thử.
 *   2. Tử số đếm `status === 'SUCCEEDED'` trên mọi dòng. Trạng thái ấy nói
 *      "execution chạy xong", KHÔNG nói "có hiện vật chính thức". Một lô mà mọi
 *      lượt khai báo đều trượt ngữ nghĩa vẫn hiện ĐỦ 3 MẪU.
 */

/**
 * @param {Array<Record<string, unknown>>} rows các dòng execution của MỘT kênh
 * @returns {{attempts: number, authorized: number, timeouts: number, rejected: number,
 *            declarationAttempts: number, failedDeclarations: number}}
 */
export function accountAttempts(rows) {
  // MẪU SỐ: chỉ chuỗi của lượt PHÂN TÍCH. Một lần thử ổn định = một bài phân
  // tích được yêu cầu, bất kể sau đó phải khai báo lại mấy lần.
  const analysisRoots = rows.filter(
    (x) => x.parent_execution_id === null && x.execution_role === 'ANALYSIS',
  )

  // TỬ SỐ: số lượt phân tích ĐÃ SINH RA một hiện vật CHÍNH THỨC.
  //
  // BA điều kiện, và bỏ bất kỳ điều nào cũng thổi phồng con số:
  //
  //   1. `result_id` khác null — có hàng kết quả.
  //   2. Hàng ấy phải mang vai COMPOSITE. Một lượt PHÂN TÍCH ĐẠT cũng ghi một
  //      hàng kết quả (vai ANALYSIS, là văn xuôi đã đóng băng), nên nếu không
  //      lọc vai thì mỗi bài phân tích đạt tự cấp cho mình một "mẫu".
  //   3. Khoá gộp phải PHÂN BIỆT được từng lần thử. CHECK 0023 buộc bản kê vai
  //      ANALYSIS có `analysis_execution_id IS NULL`, nên nếu lấy thẳng cột ấy
  //      làm khoá thì mọi hàng một lượt cùng đổ vào MỘT phần tử `null`.
  //
  // Hậu quả của bản trước, tái dựng được: ba bài phân tích đạt nhưng chỉ hai
  // hiện vật chính thức -> `authorized = 3`, cổng in "ĐỦ 3 MẪU" và thoát 0.
  //
  // F3 — bản sửa ĐẦU TIÊN cho lỗi đó (lọc bỏ khoá `null`) đi quá tay theo chiều
  // NGƯỢC LẠI: nó vứt luôn hiện vật chính thức MỘT LƯỢT hợp lệ. Đó không phải
  // giả định — database CHÍNH có đúng 32 hàng như vậy
  // (`execution_role='ANALYSIS'`, `result_role='COMPOSITE'`,
  // `analysis_execution_id IS NULL`), và 0026 cố ý giữ chúng hợp lệ. Tức là tử
  // số tụt về 0 cho toàn bộ dữ liệu một lượt.
  //
  // Khoá đúng: gộp theo lượt PHÂN TÍCH khi có, ngược lại theo CHÍNH execution ấy
  // — nhưng CHỈ khi nó mang vai ANALYSIS. Một hàng vai DECLARATION mà thiếu
  // `analysis_execution_id` là dữ liệu HỎNG, và cho nó tự làm khoá riêng sẽ biến
  // một bản kê hỏng thành một "mẫu" mới. Ở đó fail-closed là đúng.
  const authorized = new Set(
    rows
      .filter((x) => x.result_id !== null && x.result_id !== undefined)
      .filter((x) => x.result_role === 'COMPOSITE')
      .map((x) =>
        x.analysis_execution_id ?? (x.execution_role === 'ANALYSIS' ? x.exec_id : null),
      )
      .filter((k) => k !== null && k !== undefined),
  )

  const declarations = rows.filter((x) => x.execution_role === 'DECLARATION')

  /*
   * MẪU mà bộ dò KHÔNG TÌM THẤY ô nhạy cảm nào.
   *
   * Phải in TÁCH RIÊNG, và không được mô tả là "sạch" — xem mục 5 của
   * `creator_specs/PHASE4_TRUST_BOUNDARIES.md`. `obligationCount = 0` nghĩa là
   * "bộ dò không thấy gì"; sự vắng mặt của vi phạm ở đây là hệ quả trực tiếp của
   * sự vắng mặt của phát hiện, không phải bằng chứng về chất lượng.
   *
   * Con số này tồn tại để quy tắc báo cáo ấy được CƯỠNG CHẾ, không chỉ được viết
   * trong tài liệu.
   */
  const zeroObligation = new Set(
    rows
      .filter((x) => x.result_id !== null && x.result_id !== undefined)
      .filter((x) => x.result_role === 'COMPOSITE')
      .filter((x) => x.obligation_count === 0)
      .map((x) =>
        x.analysis_execution_id ?? (x.execution_role === 'ANALYSIS' ? x.exec_id : null),
      )
      .filter((k) => k !== null && k !== undefined),
  )

  return {
    attempts: analysisRoots.length,
    authorized: authorized.size,
    zeroObligationAuthorized: zeroObligation.size,
    timeouts: rows.filter((x) => x.timed_out).length,
    rejected: analysisRoots.length - authorized.size,
    declarationAttempts: declarations.length,
    // Lần khai báo trượt phải ĐẾM ĐƯỢC, không được biến mất: chúng là chi phí
    // thật của lô và là bằng chứng cho mọi kết luận về độ ổn định.
    failedDeclarations: declarations.filter(
      (x) => x.result_id === null || x.result_id === undefined,
    ).length,
  }
}

/**
 * Phiên bản/băm bị TRỘN trong cùng MỘT lần thử ổn định.
 *
 * Nghiêm trọng hơn trộn ở mức lô: hai lượt khai báo của cùng một bài phân tích
 * neo vào hai băm nghĩa vụ khác nhau nghĩa là một trong hai đang khai cho một
 * tập nghĩa vụ không còn tồn tại, và phán quyết "đạt" của nó vô nghĩa.
 *
 * @param {Array<Record<string, unknown>>} rows
 * @returns {Array<{analysisExecutionId: unknown, field: string, values: number}>}
 */
export function mixedWithinAttempt(rows) {
  const byAnalysis = new Map()
  for (const row of rows.filter((x) => x.execution_role === 'DECLARATION')) {
    const k = row.analysis_execution_id
    if (!byAnalysis.has(k)) byAnalysis.set(k, [])
    byAnalysis.get(k).push(row)
  }
  const out = []
  for (const [analysisExecutionId, decls] of byAnalysis) {
    for (const field of [
      'analysis_payload_hash',
      'obligation_set_hash',
      'validator_hash',
      'schema_hash',
    ]) {
      const values = new Set(decls.map((x) => x[field]))
      if (values.size > 1) out.push({ analysisExecutionId, field, values: values.size })
    }
  }
  return out
}

/**
 * Cột hợp đồng phải ĐỒNG NHẤT trên toàn lô.
 *
 * BĂM MÃ NGUỒN cũng phải đồng nhất, không chỉ SỐ PHIÊN BẢN: việc bump phiên bản
 * là quy ước thủ công, không gì cưỡng chế nó. Sửa nội dung `prompt.ts` giữa lần
 * chạy 2 và 3 mà quên bump khiến `prompt_version` không đổi trong khi
 * `prompt_source_hash` đổi — lô trộn hai prompt mà bảng in "sạch".
 *
 * Năm băm cuối chỉ có cột từ 0035 (M-3). Trước đó chúng chỉ nằm trong `_meta`
 * của hiện vật, tức được GHI LẠI mà không được ĐỐI CHIẾU.
 */
export const BATCH_CONTRACT_COLUMNS = [
  'obligation_generator_version',
  'declaration_prompt_version',
  'declaration_prompt_source_hash',
  'composite_validator_version',
  'schema_hash',
  'prompt_source_hash',
  'obligation_generator_hash',
  'composite_source_hash',
  'sensitive_lexicon_hash',
  'identity_source_hash',
  'provenance_source_hash',
]

/**
 * Cột hợp đồng bị TRỘN trên toàn lô.
 *
 * Tách khỏi `attempt_table.mjs` vì M-4: phép kiểm cũ chỉ `grep` mã nguồn tìm tên
 * cột, và reviewer đã chứng minh bằng mutation rằng xoá hẳn dòng kiểm THẬT vẫn
 * để test xanh — tên cột còn nằm trong câu SELECT và trong danh sách. Một
 * assertion không thể sai thì không phải assertion.
 *
 * Hàng mang NULL bị BỎ QUA: đường chạy một lượt và mọi hàng có trước 0035 không
 * có các băm này, và "không ghi" khác hẳn "ghi khác".
 *
 * @param {Array<Record<string, unknown>>} rows
 * @returns {Array<{column: string, values: number}>}
 */
export function mixedAcrossBatch(rows) {
  const out = []
  for (const col of BATCH_CONTRACT_COLUMNS) {
    const v = new Set(rows.filter((x) => x[col] !== null && x[col] !== undefined).map((x) => x[col]))
    if (v.size > 1) out.push({ column: col, values: v.size })
  }
  return out
}

/**
 * Cổng có ĐẠT được không, xét riêng phần chỉ mục hiện vật.
 *
 * Tách ra để CHẠY ĐƯỢC trong test (M-4/Codex-MEDIUM). Phép kiểm cũ chỉ `grep`
 * mã nguồn tìm chuỗi `gateOk = false` trong một đoạn 260 ký tự quanh chữ
 * "thiếu INDEX.json" — nên xoá hẳn lệnh gán THẬT mà để lại chuỗi ấy trong một
 * chú thích lân cận thì test vẫn xanh. Đúng khuôn mẫu assertion-không-thể-sai
 * mà chính tệp này đã ghi chú ngay bên dưới.
 *
 * `indexExists = false` PHẢI cho `false`: `attempt_table.mjs` đối chiếu artifact
 * với database HOÀN TOÀN trong nhánh có INDEX, nên thiếu nó nghĩa là không kiểm
 * được gì — và một cổng không kiểm được gì thì phải ĐỎ, không im lặng cho qua.
 *
 * @param {{indexExists: boolean, declaredFilesMissing?: number}} args
 * @returns {boolean}
 */
export function artifactIndexGateOk(args) {
  if (!args.indexExists) return false
  return (args.declaredFilesMissing ?? 0) === 0
}

/** TRẦN số lần thử phân tích cho MỘT kênh trong một lô ổn định. */
export const ATTEMPT_CAP = 6

/**
 * Số lần thử của một kênh có nằm trong TRẦN lấy mẫu không.
 *
 * `attempt_table.mjs` vốn in đúng câu "lô này không hợp lệ" khi vượt trần rồi
 * `process.exit(0)`: dòng ấy là lệnh `console.log` duy nhất trong cả vòng lặp
 * KHÔNG kèm `gateOk = false`, trong khi mọi tình trạng bất hợp lệ khác đều gán.
 * Một cổng tự tuyên bố lô không hợp lệ rồi thoát 0 thì không phải cổng.
 *
 * Điều đó quan trọng hơn vẻ ngoài của nó: trần này là thứ DUY NHẤT chặn việc
 * chạy lại lượt phân tích cho tới khi các con số đẹp lên. Trần 3 lần của
 * migration 0031 là trần lượt KHAI BÁO phục vụ MỘT lượt phân tích; không
 * migration nào giới hạn số lượt PHÂN TÍCH cho một kênh.
 *
 * Tách khỏi script theo đúng lý do đã ghi ở `artifactIndexGateOk`: quyết định
 * nằm trong tệp này thì bộ test gọi được nó và mutation làm test ĐỎ.
 *
 * @param {number} attempts
 * @returns {boolean}
 */
export function samplingCapOk(attempts) {
  return attempts <= ATTEMPT_CAP
}

/**
 * Mệnh đề chọn dòng kiểm định của CHẶNG KẾT THÚC.
 *
 * MỘT định nghĩa, hai người dùng: `attempt_table.mjs` và bộ test tích hợp. Nếu
 * bộ test tự viết lại phép chọn bằng JavaScript thì nó kiểm chính nó, và câu SQL
 * thật có thể sai mà vẫn xanh — đúng kiểu test rỗng nghĩa đã gặp ở vòng G7.
 *
 * Chặng kết thúc = chặng CAO NHẤT đã chạy. Enum `validation_stage` xếp theo thứ
 * tự đường ống (ANALYSIS < DECLARATION < COMPOSITE), nên `ORDER BY stage DESC`
 * cho đúng dòng cần. `LIMIT 1` bảo đảm không đếm trùng khi có đủ ba dòng.
 */
export const TERMINAL_VALIDATION_LATERAL = `
  LEFT JOIN LATERAL (
    SELECT av.id, av.stage, av.passed, av.failure_class,
           av.total_evidence_refs, av.unresolved_evidence_refs,
           av.causal_violations, av.ctr_violations, av.unsupported_metric_violations,
           av.structural_issues, av.evidence_issues, av.claim_issues, av.quality_issues
    FROM analysis_validation av
    WHERE av.llm_execution_id = e.id
    ORDER BY av.stage DESC
    LIMIT 1
  ) v ON true`

/**
 * Đếm mức nghiêm trọng từ MỘT dòng kiểm định.
 *
 * `null` (không có dòng nào) trả về 0/0/0 — nhưng đó là "chưa kiểm", khác hẳn
 * "đã kiểm và sạch". Người gọi phải in kèm chặng để phân biệt hai thứ đó.
 */
export function severityCounts(row) {
  const all = [
    ...(row?.structural_issues || []),
    ...(row?.evidence_issues || []),
    ...(row?.claim_issues || []),
    ...(row?.quality_issues || []),
  ]
  return {
    B: all.filter((i) => i.severity === 'BLOCKER').length,
    H: all.filter((i) => i.severity === 'HIGH').length,
    M: all.filter((i) => i.severity === 'MEDIUM').length,
    excerpt: all.find((i) => i.excerpt)?.excerpt ?? all.find((i) => i.message)?.message ?? '',
  }
}
