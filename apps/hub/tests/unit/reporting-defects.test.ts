import { spawnSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

// @ts-expect-error — module JS thuần, dùng chung với `attempt_table.mjs`.
import { accountAttempts, severityCounts, TERMINAL_VALIDATION_LATERAL } from '../../attempt_accounting.mjs'

/**
 * Phần `repairErrors` nằm ở `cursor-two-pass.test.ts` — nơi đã có sẵn gói bằng
 * chứng và hàm `runAnalysis`. Dựng gói thứ ba ở đây chỉ để chạy bộ kiểm sẽ tạo
 * ra một bản sao nữa phải giữ đồng bộ bằng tay.
 */

/**
 * HAI KHIẾM KHUYẾT BÁO CÁO do lần thăm dò 2026-08-06 phát hiện.
 *
 * Cả hai đều IM LẶNG và cả hai đều khiến người đọc hiểu sai một lần chạy thật:
 *
 *   1. Bảng lần thử chỉ đọc dòng kiểm định chặng COMPOSITE. Lần thăm dò hỏng ở
 *      chặng PHÂN TÍCH nên không có dòng COMPOSITE nào, và bảng in `0/0/0` mức
 *      nghiêm trọng — giấu sạch hai lỗi đã chặn nó.
 *   2. `repairErrors` gom từ tập vi phạm CHƯA lọc theo chặng, nên prompt sửa lỗi
 *      nhắc lỗi CTR trong khi báo cáo chính thức ghi 0 vi phạm CTR.
 *
 * Không quy tắc ngữ nghĩa nào bị đụng tới. Lần thăm dò hỏng vì một câu NHÂN QUẢ
 * có thật của mô hình, và câu đó vẫn phải bị chặn y như cũ.
 */

/**
 * Dựng các dòng ĐÚNG NHƯ database trả về.
 *
 * Bản fixture trước mô hình hoá một trạng thái BẤT KHẢ: lượt PHÂN TÍCH ĐẠT với
 * `result_id: null`. `persistAttempt` ghi hàng kết quả VÀ chốt `SUCCEEDED` trong
 * cùng một khối `if (args.passed && args.persistResult)`, nên hàng đó luôn có
 * `result_id`. Vì fixture sai, cả 8 test kế toán đều xanh trong khi tử số bị
 * thổi phồng ở mọi lô thật.
 */
function realRows(attempts: Array<{ id: string; analysisPassed: boolean; authorized: boolean }>) {
  const rows: Array<Record<string, unknown>> = []
  for (const a of attempts) {
    rows.push({
      // F6 — `exec_id` LUÔN có trong câu SELECT của `attempt_table.mjs`
      // (`e.id exec_id`). Fixture cũ bỏ trống nó, nên khoá gộp dự phòng của kế
      // toán không thể được kiểm — và F3 vô hình suốt.
      exec_id: `exec-analysis-${a.id}`,
      execution_role: 'ANALYSIS', parent_execution_id: null,
      // CHECK 0023 buộc bản kê vai ANALYSIS mang NULL ở cột này.
      analysis_execution_id: null,
      status: a.analysisPassed ? 'SUCCEEDED' : 'REJECTED_SCHEMA',
      // Lượt phân tích ĐẠT ghi hàng kết quả vai ANALYSIS.
      result_id: a.analysisPassed ? `res-analysis-${a.id}` : null,
      result_role: a.analysisPassed ? 'ANALYSIS' : null,
      timed_out: false,
    })
    if (!a.analysisPassed) continue
    rows.push({
      exec_id: `exec-decl-${a.id}`,
      execution_role: 'DECLARATION', parent_execution_id: null, analysis_execution_id: a.id,
      status: a.authorized ? 'SUCCEEDED' : 'RUNNING',
      result_id: a.authorized ? `res-composite-${a.id}` : null,
      result_role: a.authorized ? 'COMPOSITE' : null,
      timed_out: false,
    })
  }
  return rows
}

/**
 * Hàng MỘT LƯỢT — kiến trúc cũ, vẫn hợp lệ theo 0026.
 *
 * F6: đây chính là hàng mà fixture trước THIẾU. Database CHÍNH có 32 hàng như
 * vậy: vai execution ANALYSIS, hàng kết quả vai COMPOSITE, và
 * `analysis_execution_id` NULL vì không có lượt khai báo riêng nào.
 */
function onePassRow(id: string) {
  return {
    exec_id: `exec-onepass-${id}`,
    execution_role: 'ANALYSIS',
    parent_execution_id: null,
    analysis_execution_id: null,
    status: 'SUCCEEDED',
    result_id: `res-composite-${id}`,
    result_role: 'COMPOSITE',
    timed_out: false,
  }
}

describe('0. BLOCKER kế toán: tử số CHỈ đếm hiện vật chính thức', () => {
  it('BA bài phân tích ĐẠT, chỉ HAI hiện vật chính thức -> authorized = 2, cổng TRƯỢT', () => {
    // Đây là ca đã tái dựng được và đã cho `authorized = 3` ở bản trước.
    const rows = realRows([
      { id: 'A', analysisPassed: true, authorized: true },
      { id: 'B', analysisPassed: true, authorized: true },
      { id: 'C', analysisPassed: true, authorized: false },
    ])
    const a = accountAttempts(rows)
    expect(a.attempts).toBe(3)
    expect(a.authorized, 'tử số đếm cả hàng kết quả vai ANALYSIS').toBe(2)
    expect(a.rejected).toBe(1)
    // Cổng lô chính thức đòi >= 3 mẫu ĐẠT.
    expect(a.authorized >= 3, 'cổng phải TRƯỢT khi chỉ có 2 hiện vật').toBe(false)
  })

  it('KHÔNG hiện vật nào -> authorized = 0, không phải 1', () => {
    // Hàng vai ANALYSIS đưa `null` vào Set; `null` là MỘT phần tử.
    const rows = realRows([
      { id: 'A', analysisPassed: true, authorized: false },
      { id: 'B', analysisPassed: true, authorized: false },
    ])
    expect(accountAttempts(rows).authorized).toBe(0)
  })

  it('mẫu số không bao giờ nhỏ hơn tử số (từ chối không âm)', () => {
    const rows = realRows([
      { id: 'A', analysisPassed: true, authorized: true },
      { id: 'B', analysisPassed: true, authorized: true },
    ])
    const a = accountAttempts(rows)
    expect(a.authorized).toBe(2)
    expect(a.attempts).toBe(2)
    expect(a.rejected).toBeGreaterThanOrEqual(0)
  })

  it('MỘT bài phân tích không đóng góp quá một mẫu dù dữ liệu hỏng cho hai hàng', () => {
    const rows = realRows([{ id: 'A', analysisPassed: true, authorized: true }])
    rows.push({
      execution_role: 'DECLARATION', parent_execution_id: null, analysis_execution_id: 'A',
      status: 'SUCCEEDED', result_id: 'res-composite-A2', result_role: 'COMPOSITE', timed_out: false,
    })
    expect(accountAttempts(rows).authorized).toBe(1)
  })

  it('F3: hiện vật MỘT LƯỢT hợp lệ vẫn được ĐẾM', () => {
    // Bản sửa A-1 (lọc bỏ khoá null) vứt luôn hàng này. Database CHÍNH có 32
    // hàng như vậy, nên tử số tụt về 0 cho toàn bộ dữ liệu một lượt.
    const rows = [onePassRow('X'), onePassRow('Y')]
    const a = accountAttempts(rows)
    expect(a.attempts).toBe(2)
    expect(a.authorized, 'hiện vật một lượt hợp lệ bị vứt khỏi tử số').toBe(2)
    expect(a.rejected).toBe(0)
  })

  it('F3: hàng MỘT LƯỢT không gộp nhầm thành MỘT mẫu', () => {
    // Lý do A-1 tồn tại: `null` là MỘT phần tử của Set. Ba hàng một lượt phải là
    // BA mẫu, không phải một.
    const rows = [onePassRow('X'), onePassRow('Y'), onePassRow('Z')]
    expect(accountAttempts(rows).authorized).toBe(3)
  })

  it('F3: trộn một lượt và hai lượt -> đếm đúng cả hai', () => {
    const rows = [
      ...realRows([
        { id: 'A', analysisPassed: true, authorized: true },
        { id: 'B', analysisPassed: true, authorized: false },
      ]),
      onePassRow('X'),
    ]
    const a = accountAttempts(rows)
    // 2 lượt phân tích hai-lượt + 1 lượt một-lượt = 3 mẫu số.
    expect(a.attempts).toBe(3)
    // A đạt, B trượt, X đạt = 2.
    expect(a.authorized).toBe(2)
  })

  it('F3 RANH GIỚI: hàng KHAI BÁO thiếu analysis_execution_id KHÔNG tự thành mẫu', () => {
    // Fail-closed: một bản kê hỏng không được biến thành một "mẫu" mới. Nếu khoá
    // dự phòng dùng `exec_id` cho MỌI vai thì hai lần khai báo hỏng của cùng một
    // bài phân tích sẽ đếm thành hai mẫu.
    const rows = [
      {
        exec_id: 'exec-decl-broken-1', execution_role: 'DECLARATION',
        parent_execution_id: null, analysis_execution_id: null, status: 'SUCCEEDED',
        result_id: 'res-composite-1', result_role: 'COMPOSITE', timed_out: false,
      },
      {
        exec_id: 'exec-decl-broken-2', execution_role: 'DECLARATION',
        parent_execution_id: null, analysis_execution_id: null, status: 'SUCCEEDED',
        result_id: 'res-composite-2', result_role: 'COMPOSITE', timed_out: false,
      },
    ]
    expect(accountAttempts(rows).authorized).toBe(0)
  })

  it('mẫu 0 NGHĨA VỤ được đếm TÁCH RIÊNG, không gộp vào "đạt"', () => {
    // Quy tắc báo cáo bắt buộc của mục 5 PHASE4_TRUST_BOUNDARIES.md. Viết trong
    // tài liệu mà không có gì cưỡng chế thì sớm muộn cũng bị bỏ qua.
    const rows = realRows([
      { id: 'A', analysisPassed: true, authorized: true },
      { id: 'B', analysisPassed: true, authorized: true },
    ])
    // A chạm ô nhạy cảm, B thì bộ dò không thấy gì.
    for (const r of rows) {
      if (r.result_role === 'COMPOSITE') r.obligation_count = r.analysis_execution_id === 'B' ? 0 : 3
    }
    const a = accountAttempts(rows)
    expect(a.authorized, '0 nghĩa vụ vẫn là một mẫu hợp lệ').toBe(2)
    expect(a.zeroObligationAuthorized, 'không đếm tách được mẫu 0 nghĩa vụ').toBe(1)
  })

  it('bảng lần thử THẬT SỰ in cảnh báo 0 nghĩa vụ', () => {
    const src = readFileSync(new URL('../../attempt_table.mjs', import.meta.url), 'utf8')
    expect(src).toContain('acct.zeroObligationAuthorized')
    expect(src).toContain('KHÔNG phải "phân tích sạch"')
  })

  it('`attempt_table.mjs` PHẢI phân tích cú pháp được', () => {
    /*
     * Mọi phép kiểm khác trên tệp này đều là `grep` chuỗi, nên chúng xanh kể cả
     * khi tệp KHÔNG chạy nổi. Điều đó đã xảy ra thật: một dấu backtick trong một
     * dòng chú thích SQL đóng sớm template literal chứa câu truy vấn, và toàn bộ
     * bộ test vẫn xanh — vì không test nào từng THỰC THI tệp này.
     *
     * `node --check` là mức tối thiểu: nó chạy trình phân tích cú pháp thật.
     */
    const r = spawnSync('node', ['--check', fileURLToPath(new URL('../../attempt_table.mjs', import.meta.url))], {
      encoding: 'utf8',
    })
    expect(r.status, `attempt_table.mjs không parse được:\n${r.stderr}`).toBe(0)
  })

  it('CÂU SQL phải lọc vai kết quả — không chỉ mã JS', () => {
    // Hàng rào thứ hai: nếu câu SQL mang về hàng vai ANALYSIS thì mã JS vẫn phải
    // chặn, nhưng câu SQL cũng không được mang nó về ngay từ đầu.
    const sql = readFileSync(new URL('../../attempt_table.mjs', import.meta.url), 'utf8')
    expect(sql).toContain("res.result_role = 'COMPOSITE'")
  })
})

describe('1. bảng lần thử — kế toán và mức nghiêm trọng', () => {
  it('HÌNH DẠNG LẦN THĂM DÒ THẬT: hỏng ở ANALYSIS -> 0 được cấp phép', () => {
    // Đúng lần chạy 2026-08-06: một execution ANALYSIS, không lượt khai báo,
    // không kết quả chính thức.
    const rows = [{
      execution_role: 'ANALYSIS', parent_execution_id: null, analysis_execution_id: null,
      status: 'REJECTED_SCHEMA', result_id: null, timed_out: false,
    }]
    const acct = accountAttempts(rows)
    expect(acct.attempts).toBe(1)
    expect(acct.authorized).toBe(0)
    expect(acct.declarationAttempts).toBe(0)
  })

  it('mức nghiêm trọng đọc được từ dòng ANALYSIS (bản cũ in 0/0/0)', () => {
    // Đúng hai vi phạm của lần thăm dò: 1 BLOCKER + 1 HIGH.
    const row = {
      claim_issues: [{ severity: 'BLOCKER', rule: 'causal_claim', excerpt: 'CTA dày có thể làm giảm giữ chân' }],
      quality_issues: [{ severity: 'HIGH', rule: 'selfcheck_contradicted', message: 'selfCheck mâu thuẫn' }],
    }
    const s = severityCounts(row)
    expect(s.B).toBe(1)
    expect(s.H).toBe(1)
    expect(s.B + s.H).toBe(2)
    expect(s.excerpt).toContain('CTA dày')
  })

  it('HAI lỗi HIGH ở chặng ANALYSIS hiện đủ 2 HIGH', () => {
    const s = severityCounts({
      quality_issues: [
        { severity: 'HIGH', rule: 'selfcheck_contradicted' },
        { severity: 'HIGH', rule: 'finding_without_evidence' },
      ],
    })
    expect(s.H).toBe(2)
  })

  it('không có dòng kiểm định -> 0/0/0, và người gọi phải in kèm chặng', () => {
    expect(severityCounts(null)).toMatchObject({ B: 0, H: 0, M: 0 })
    expect(severityCounts({})).toMatchObject({ B: 0, H: 0, M: 0 })
  })

  it('mệnh đề SQL dùng chung CHỌN MỘT dòng và xếp theo chặng', () => {
    // Bộ test KHÔNG viết lại phép chọn bằng JavaScript — nó kiểm chính câu SQL
    // mà `attempt_table.mjs` chạy. Một bản chép lại sẽ xanh kể cả khi SQL sai.
    expect(TERMINAL_VALIDATION_LATERAL).toContain('ORDER BY av.stage DESC')
    expect(TERMINAL_VALIDATION_LATERAL).toContain('LIMIT 1')
    expect(TERMINAL_VALIDATION_LATERAL).toContain('av.llm_execution_id = e.id')
    // Không được khoá cứng vào một chặng nào.
    expect(TERMINAL_VALIDATION_LATERAL).not.toContain("stage = 'COMPOSITE'")
  })
})
