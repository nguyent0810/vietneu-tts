import { neon, neonConfig, Pool } from '@neondatabase/serverless'
import { drizzle } from 'drizzle-orm/neon-http'
import { drizzle as drizzlePool } from 'drizzle-orm/neon-serverless'

import * as schema from './schema'

/**
 * Hai driver Neon, chọn theo TÍNH CHẤT CÔNG VIỆC chứ không theo sở thích:
 *
 *  - `db` (HTTP): mỗi câu lệnh là một request HTTP riêng. Nhanh nhất, không giữ
 *    kết nối — nhưng KHÔNG hỗ trợ transaction tương tác. Dùng cho đọc và cho
 *    các thao tác ghi gói gọn trong MỘT câu lệnh (kể cả CTE nhiều tầng).
 *
 *  - `withTransaction` (Pool/WebSocket): dùng khi cần transaction thật sự nhiều
 *    câu lệnh — freeze revision, ghi kết quả + điểm, chốt vòng tinh chỉnh.
 *
 * Gọi nhầm driver không báo lỗi lúc biên dịch mà hỏng lúc chạy (HTTP âm thầm
 * chạy từng câu lệnh RỜI NHAU, không nguyên tử), nên ranh giới này phải rõ ràng
 * ở tầng API thay vì để mỗi nơi tự chọn.
 */

let cachedUrl: string | undefined

export function databaseUrl(): string {
  if (cachedUrl) return cachedUrl
  const url = process.env.DATABASE_URL
  if (!url) {
    throw new Error(
      'DATABASE_URL chưa được đặt. Copy apps/hub/.env.example thành .env.local và điền connection string Neon.',
    )
  }
  cachedUrl = url
  return url
}

let httpDb: ReturnType<typeof drizzle> | undefined

/**
 * Driver HTTP — chỉ dùng cho câu lệnh đơn.
 *
 * Khởi tạo LƯỜI, có chủ đích: nếu tạo client ngay lúc nạp module thì một
 * DATABASE_URL bị thiếu sẽ làm sập MỌI route ngay khi import, kể cả route
 * không hề chạm database (health check chẳng hạn) — và làm unit test thuần
 * không chạy được. Lỗi phải nổ ở đúng chỗ thực sự cần database.
 */
export function getDb(): ReturnType<typeof drizzle> {
  httpDb ??= drizzle(neon(databaseUrl()), { schema, casing: 'snake_case' })
  return httpDb
}

/** Chỉ dùng trong test: quên URL đã cache giữa các lần đổi env. */
export function resetDbForTesting(): void {
  httpDb = undefined
  cachedUrl = undefined
}

/** Handle transaction do Pool cấp. */
export type Tx = Parameters<Parameters<ReturnType<typeof drizzlePool>['transaction']>[0]>[0]

/**
 * Thứ chạy được câu lệnh: hoặc driver HTTP, hoặc một transaction của Pool.
 *
 * Nhờ kiểu này, các hàm ghi dữ liệu nhận executor từ ngoài và dùng được ở cả
 * hai chế độ, thay vì tự chọn driver bên trong — nếu tự chọn thì không cách nào
 * gói nhiều thao tác vào một transaction.
 */
export type Executor = ReturnType<typeof drizzle> | Tx

/**
 * Chạy một transaction thật sự qua Pool/WebSocket.
 *
 * Pool được tạo mới mỗi lần gọi và đóng ở `finally`: trên serverless, giữ pool
 * sống giữa các invocation sẽ rò kết nối khi instance bị đóng băng giữa chừng.
 */
export async function withTransaction<T>(fn: (tx: Tx) => Promise<T>): Promise<T> {
  // Bắt buộc trước khi mở Pool: trên Node (route runtime='nodejs', script CLI,
  // test) driver WebSocket không có sẵn `WebSocket` toàn cục, và nếu thiếu thì
  // lỗi chỉ nổ lúc chạy thật chứ không phải lúc biên dịch.
  await configureWebSocketForNode()
  const pool = new Pool({ connectionString: databaseUrl() })
  try {
    const pooled = drizzlePool(pool, { schema, casing: 'snake_case' })
    return await pooled.transaction(fn)
  } finally {
    await pool.end()
  }
}

/**
 * Trong Node (test, script CLI, `db:migrate`) driver WebSocket cần một
 * implementation `ws`; trên Edge/Vercel thì runtime đã có sẵn WebSocket.
 * Nạp động để bundle cho Edge không kéo theo `ws`.
 */
export async function configureWebSocketForNode(): Promise<void> {
  if (typeof globalThis.WebSocket !== 'undefined') return
  const ws = await import('ws')
  neonConfig.webSocketConstructor = ws.default
}

export { schema }
