import { describe, expect, it } from 'vitest'

// @ts-expect-error — module JS thuần, dùng chung với `attempt_table.mjs`.
import { accountAttempts, mixedWithinAttempt } from '../../attempt_accounting.mjs'

/**
 * KẾ TOÁN LẦN THỬ — con số quyết định lô chính thức có hợp lệ hay không.
 *
 * Rà soát đối kháng G8 tìm ra hai sai sót ở đây, cả hai đều theo hướng LẠC
 * QUAN, và cả hai đều vô hình vì phần này chưa từng có test:
 *
 *   * mẫu số đếm cả lượt khai báo -> phồng gấp đôi;
 *   * tử số đếm trạng thái execution -> một lô KHÔNG có hiện vật chính thức nào
 *     vẫn hiện "ĐỦ 3 MẪU".
 *
 * Ca đầu tiên dưới đây tái dựng đúng kịch bản thứ hai.
 */

/** Một lượt phân tích + n lượt khai báo, có/không có kết quả chính thức. */
const attempt = (
  id: string,
  decls: Array<{ resultId: string | null; obligationHash?: string }>,
) => [
  {
    execution_role: 'ANALYSIS',
    parent_execution_id: null,
    // CHECK 0023 buộc cột này NULL ở bản kê vai ANALYSIS.
    analysis_execution_id: null,
    status: 'SUCCEEDED',
    // Lượt phân tích ĐẠT LUÔN ghi một hàng kết quả vai ANALYSIS — trạng thái
    // `SUCCEEDED` kèm `result_id: null` là BẤT KHẢ ở đường ghi thật.
    result_id: `res-analysis-${id}`,
    result_role: 'ANALYSIS',
    timed_out: false,
  },
  ...decls.map((d, i) => ({
    // `result_role` PHẢI có: tử số chỉ đếm hiện vật vai COMPOSITE. Fixture cũ
    // bỏ trống cột này, nên nó mô hình hoá một hàng database không tồn tại.
    result_role: d.resultId ? 'COMPOSITE' : null,
    execution_role: 'DECLARATION',
    // Lượt khai báo ĐẦU cũng có parent null — đây chính là cái làm mẫu số phồng.
    parent_execution_id: i === 0 ? null : `${id}-d${i - 1}`,
    analysis_execution_id: id,
    status: 'RUNNING',
    result_id: d.resultId,
    timed_out: false,
    obligation_set_hash: d.obligationHash ?? 'h1',
    analysis_payload_hash: 'a1',
    validator_hash: 'v1',
    schema_hash: 's1',
  })),
]

describe('mẫu số: đếm theo LƯỢT PHÂN TÍCH', () => {
  it('ba lần chạy, mỗi lần một lượt khai báo -> BA lần thử, không phải sáu', () => {
    const rows = [
      ...attempt('A', [{ resultId: 'r1' }]),
      ...attempt('B', [{ resultId: 'r2' }]),
      ...attempt('C', [{ resultId: 'r3' }]),
    ]
    expect(accountAttempts(rows).attempts).toBe(3)
  })

  it('lượt khai báo THỬ LẠI không làm tăng mẫu số', () => {
    const rows = attempt('A', [{ resultId: null }, { resultId: null }, { resultId: 'r1' }])
    const a = accountAttempts(rows)
    expect(a.attempts).toBe(1)
    expect(a.declarationAttempts).toBe(3)
  })
})

describe('tử số: đếm theo HIỆN VẬT CHÍNH THỨC', () => {
  it('mọi lượt khai báo trượt -> ĐẠT = 0, dù lượt phân tích đều xong', () => {
    // Đây là kịch bản mà bản cũ báo "ĐỦ 3 MẪU". Ba bài phân tích chạy xong,
    // chín lần khai báo trượt ngữ nghĩa, KHÔNG hiện vật chính thức nào.
    const rows = [
      ...attempt('A', [{ resultId: null }, { resultId: null }, { resultId: null }]),
      ...attempt('B', [{ resultId: null }, { resultId: null }, { resultId: null }]),
      ...attempt('C', [{ resultId: null }, { resultId: null }, { resultId: null }]),
    ]
    const a = accountAttempts(rows)
    expect(a.attempts).toBe(3)
    expect(a.authorized).toBe(0)
    expect(a.rejected).toBe(3)
    // Chín lần trượt phải ĐẾM ĐƯỢC, không được biến mất khỏi báo cáo.
    expect(a.failedDeclarations).toBe(9)
  })

  it('một lượt phân tích chỉ đóng góp TỐI ĐA một mẫu', () => {
    // Ngay cả khi dữ liệu hỏng cho ra hai dòng kết quả cùng một lượt phân tích,
    // kế toán không được đếm thành hai mẫu.
    const rows = attempt('A', [{ resultId: 'r1' }, { resultId: 'r2' }])
    expect(accountAttempts(rows).authorized).toBe(1)
  })

  it('trượt hai lần rồi đạt -> một mẫu, hai lần khai trượt', () => {
    const rows = attempt('A', [{ resultId: null }, { resultId: null }, { resultId: 'r1' }])
    const a = accountAttempts(rows)
    expect(a.authorized).toBe(1)
    expect(a.failedDeclarations).toBe(2)
  })
})

describe('trộn phiên bản TRONG một lần thử', () => {
  it('hai lượt khai báo neo vào hai băm nghĩa vụ khác nhau -> báo động', () => {
    const rows = attempt('A', [
      { resultId: null, obligationHash: 'h1' },
      { resultId: 'r1', obligationHash: 'KHÁC' },
    ])
    const m = mixedWithinAttempt(rows)
    expect(m.map((x: { field: string }) => x.field)).toContain('obligation_set_hash')
  })

  it('mọi lượt khai báo cùng một băm -> không báo động', () => {
    const rows = attempt('A', [{ resultId: null }, { resultId: 'r1' }])
    expect(mixedWithinAttempt(rows)).toEqual([])
  })
})
