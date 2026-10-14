import { describe, expect, it } from 'vitest'

import { checkProvenanceAgreement } from '@/lib/cursor/provenance'

/**
 * Bộ so ĐỒNG THUẬN NGUỒN GỐC — test thuần, không chạm database.
 *
 * Phần đối chiếu với hàng database THẬT nằm ở `two-pass-loop.test.ts`, nơi có
 * một lần chạy hai lượt thật để đối chiếu. Bản đầu của tệp này đọc "kết quả
 * COMPOSITE gần nhất còn trong database test" — và khi không có, nó XANH mà
 * không kiểm gì. Một test luôn xanh vì dữ liệu vắng mặt còn tệ hơn không có test.
 */

describe('bộ so đồng thuận nguồn gốc', () => {
  it('phát hiện LỆCH giữa hai bề mặt', () => {
    const r = checkProvenanceAgreement(
      { a: { h: 'x' }, b: { h: 'y' } },
      ['h'],
    )
    expect(r.agreed).toBe(false)
    expect(r.mismatches[0]!.field).toBe('h')
  })

  it('phát hiện THIẾU trường ở một bề mặt', () => {
    const r = checkProvenanceAgreement({ a: { h: 'x' }, b: {} }, ['h'])
    expect(r.agreed).toBe(false)
    expect(r.missing).toEqual([{ surface: 'b', field: 'h' }])
  })

  it('đồng thuận khi mọi bề mặt nói cùng một điều', () => {
    const r = checkProvenanceAgreement({ a: { h: 'x' }, b: { h: 'x' } }, ['h'])
    expect(r.agreed).toBe(true)
  })
})
