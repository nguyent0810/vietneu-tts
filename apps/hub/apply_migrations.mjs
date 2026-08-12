/**
 * Áp migration cho MỘT database chỉ định, in rõ HOST đang đụng vào.
 *
 * `migrate.ts` chỉ đọc DATABASE_URL nên không nói được nó vừa chạy trên database
 * nào. Với hai database phải giữ giống hệt nhau, "không nói được" là không chấp
 * nhận được: một lần chạy nhầm mục tiêu sẽ không có gì báo.
 */
import { config } from 'dotenv'
import { Pool, neonConfig } from '@neondatabase/serverless'
import { drizzle } from 'drizzle-orm/neon-serverless'
import { migrate } from 'drizzle-orm/neon-serverless/migrator'
import ws from 'ws'

neonConfig.webSocketConstructor = ws
config({ path: '.env.local' })

const target = process.argv[2]
const url = target === 'MAIN' ? process.env.DATABASE_URL
          : target === 'TEST' ? process.env.TEST_DATABASE_URL : null
if (!url) { console.error('Dùng: node apply_migrations.mjs MAIN|TEST'); process.exit(2) }

const host = new URL(url).host
console.log(`Áp migration cho ${target} @ ${host}`)
const pool = new Pool({ connectionString: url })
try {
  await migrate(drizzle(pool), { migrationsFolder: './drizzle' })
  console.log(`${target}: migrate() trả về không lỗi (CHƯA phải bằng chứng — xem verify)`)
} finally { await pool.end() }
