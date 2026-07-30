import { config } from 'dotenv'

config({ path: '.env.local' })
config({ path: '.env' })

/**
 * Integration test chạy trên PostgreSQL THẬT (Neon) và TRUNCATE bảng giữa các
 * test, nên bắt buộc phải trỏ vào một database RIÊNG.
 *
 * Quy tắc cứng: chỉ TEST_DATABASE_URL mới được dùng. Nếu nó không được đặt thì
 * DATABASE_URL bị XOÁ khỏi môi trường test — KHÔNG rơi về dùng nó. Rơi về sẽ
 * TRUNCATE thẳng vào database thật, và đó là kiểu lỗi chỉ phát hiện được sau
 * khi dữ liệu đã mất.
 */
const testUrl = process.env.TEST_DATABASE_URL?.trim()
const prodUrl = process.env.DATABASE_URL?.trim()

if (testUrl && prodUrl && testUrl === prodUrl) {
  throw new Error(
    'TEST_DATABASE_URL trùng DATABASE_URL. Integration test sẽ TRUNCATE mọi bảng — ' +
      'hãy tạo một Neon branch/database riêng cho test.',
  )
}

if (testUrl) {
  process.env.DATABASE_URL = testUrl
} else {
  delete process.env.DATABASE_URL
}
