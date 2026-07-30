import { config } from 'dotenv'
import { Pool } from '@neondatabase/serverless'
import { drizzle } from 'drizzle-orm/neon-serverless'
import { migrate } from 'drizzle-orm/neon-serverless/migrator'

import { configureWebSocketForNode } from './client'

/**
 * Chạy migration theo thứ tự, dùng Pool/WebSocket.
 *
 * Bắt buộc dùng Pool chứ không dùng HTTP: migration là nhiều câu lệnh trong
 * MỘT transaction, mà driver HTTP không hỗ trợ transaction tương tác — nó sẽ
 * âm thầm chạy từng câu lệnh rời nhau và để lại schema nửa vời khi có lỗi.
 */
async function main(): Promise<void> {
  config({ path: '.env.local' })
  config({ path: '.env' })

  const url = process.env.DATABASE_URL
  if (!url) {
    console.error('DATABASE_URL chưa được đặt. Copy .env.example thành .env.local và điền vào.')
    process.exit(2)
  }

  await configureWebSocketForNode()

  const pool = new Pool({ connectionString: url })
  try {
    const db = drizzle(pool)
    console.log('Đang chạy migration...')
    await migrate(db, { migrationsFolder: './drizzle' })
    console.log('Migration xong.')
  } finally {
    await pool.end()
  }
}

main().catch((err) => {
  console.error('Migration thất bại:', err instanceof Error ? err.message : err)
  process.exit(1)
})
