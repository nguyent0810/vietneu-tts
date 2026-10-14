import { describe, expect, it } from 'vitest'

import { hasTestDatabase } from '../helpers/db'

/**
 * TIỀN ĐỀ của cổng — tệp này KHÔNG BAO GIỜ được skip.
 *
 * Toàn bộ bộ test tích hợp dùng `describe.skipIf(!hasTestDatabase)`. Điều đó
 * đúng cho máy lập trình viên chưa cấu hình database, nhưng biến `npm run
 * test:gate` thành một cổng có thể XANH mà không thực hiện một phép ghi nào:
 * thiếu biến môi trường thì mọi ca đối kháng ở tầng database lặng lẽ biến mất,
 * và bảng kết quả vẫn in "tất cả đã đạt".
 *
 * "Không kiểm được" phải khác "đã kiểm và đạt". Ca dưới đây làm ĐỎ cổng khi
 * database test vắng mặt, nên con số của cổng luôn nói đúng nó đã kiểm những gì.
 */
describe('tiền đề cổng', () => {
  it('database TEST phải có mặt — thiếu thì cổng ĐỎ, không im lặng bỏ qua', () => {
    expect(
      hasTestDatabase,
      'TEST_DATABASE_URL chưa cấu hình: toàn bộ ca đối kháng ở tầng database đã bị BỎ QUA. ' +
        'Kết quả "đạt" của lần chạy này KHÔNG chứng minh gì về các ràng buộc database.',
    ).toBe(true)
  })
})
