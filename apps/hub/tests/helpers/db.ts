import { Pool } from '@neondatabase/serverless'
import { drizzle } from 'drizzle-orm/neon-serverless'
import { sql } from 'drizzle-orm'
import ws from 'ws'
import { neonConfig } from '@neondatabase/serverless'

import * as schema from '@/db/schema'

neonConfig.webSocketConstructor = ws

/**
 * Chưa cấu hình TEST_DATABASE_URL thì bỏ qua cả file test (dùng
 * `describe.skipIf(!hasTestDatabase)`), thay vì để nó fail bằng một lỗi kết nối
 * khó hiểu. Xem tests/setup.ts.
 */
export const hasTestDatabase = Boolean(process.env.DATABASE_URL)

let pool: Pool | undefined

export function testPool(): Pool {
  if (!process.env.DATABASE_URL) {
    throw new Error('TEST_DATABASE_URL chưa đặt — xem apps/hub/.env.example')
  }
  if (!pool) {
    pool = new Pool({ connectionString: process.env.DATABASE_URL })
    // Neon đóng kết nối WebSocket đang rảnh sau một lúc. Nếu không bắt sự kiện
    // 'error' thì lỗi trên client rảnh sẽ nổi lên thành unhandled error và làm
    // hỏng một test hoàn toàn không liên quan. Bắt ở đây để pool tự thay client
    // mới ở lần truy vấn kế tiếp.
    pool.on('error', () => {
      /* client rảnh bị ngắt — pool sẽ tự tạo client mới khi cần */
    })
  }
  return pool
}

export function testDb() {
  return drizzle(testPool(), { schema, casing: 'snake_case' })
}

export async function closeTestPool(): Promise<void> {
  if (pool) {
    await pool.end()
    pool = undefined
  }
}

/**
 * Danh sách bảng nghiệp vụ cần dọn giữa các test, theo thứ tự KHÔNG quan
 * trọng vì dùng TRUNCATE ... CASCADE.
 *
 * `drizzle.__drizzle_migrations` cố ý KHÔNG nằm trong danh sách: xoá nó sẽ
 * khiến migration chạy lại từ đầu ở lần sau.
 */
const BUSINESS_TABLES = [
  // Phase 2 — analytics. Phải nằm trước các bảng chúng tham chiếu, dù TRUNCATE
  // CASCADE không cần thứ tự; liệt kê đủ để không sót bảng nào giữa các test.
  'video_daily_metric_history',
  'video_daily_metric',
  'channel_daily_metric',
  'analytics_api_call',
  'sync_checkpoint',
  'sync_run',
  'video',
  'critique',
  'llm_execution',
  'score',
  'evaluation',
  'analysis_result',
  'analysis_run',
  'prompt_revision',
  'prompt_template',
  'approval',
  'audit_event',
  'content_revision',
  'content_item',
  'algorithm_version',
  'algorithm',
  'score_dimension',
  'user_api_token',
  'user_account',
  'worker_machine',
  'rate_limit_bucket',
  'channel',
  'workspace',
] as const

/**
 * Dọn sạch dữ liệu nghiệp vụ.
 *
 * `audit_event` và các bảng bất biến khác có trigger chặn DELETE/UPDATE, nhưng
 * TRUNCATE KHÔNG kích hoạt trigger hàng — nên vẫn dọn được. Đây là lý do dùng
 * TRUNCATE thay vì DELETE ở đây, và cũng là lý do bộ test bắt buộc phải chạy
 * trên database riêng.
 */
export async function truncateAll(): Promise<void> {
  const db = testDb()
  await db.execute(sql.raw(`TRUNCATE TABLE ${BUSINESS_TABLES.join(', ')} RESTART IDENTITY CASCADE`))
}
