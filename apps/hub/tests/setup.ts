import { config } from 'dotenv'
import { neonConfig } from '@neondatabase/serverless'

/*
 * POSTGRES CỤC BỘ QUA PROXY — chỉ bật khi biến môi trường có mặt.
 *
 * Đặt ở ĐÂY chứ không trong `src/db/client.ts`: `neonConfig` là singleton toàn
 * cục, nên cấu hình một lần ở setup file là đủ cho MỌI driver được tạo sau đó.
 * Nhờ vậy mã sản phẩm không có một dòng nào biết tới sự tồn tại của CI.
 *
 * Cần HAI proxy vì `client.ts` cố ý dùng HAI driver khác nhau:
 *   - `getDb()` -> `neon()`  = HTTP, cần `fetchEndpoint`.
 *   - `withTransaction`      = Pool/WebSocket, cần `wsProxy`.
 * Một container `postgres` trần không nói được giao thức nào trong hai.
 */
const wsProxy = process.env.NEON_LOCAL_PROXY?.trim()
if (wsProxy) {
  neonConfig.wsProxy = () => `${wsProxy}/v1`
  neonConfig.useSecureWebSocket = false
  neonConfig.pipelineTLS = false
  neonConfig.pipelineConnect = false
}

const httpEndpoint = process.env.NEON_LOCAL_HTTP_ENDPOINT?.trim()
if (httpEndpoint) {
  neonConfig.fetchEndpoint = httpEndpoint
}


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

/**
 * Database CHÍNH (dữ liệu thật của 3 kênh), CHỈ ĐỌC.
 *
 * Bộ test dữ liệu thật chỉ chạy dry-run và không ghi gì. Tách biến riêng thay
 * vì dùng lại DATABASE_URL để không đường nào vô tình TRUNCATE database thật.
 */
if (prodUrl) process.env.HUB_PROD_DATABASE_URL = prodUrl
