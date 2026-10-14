import { config } from 'dotenv'
import { Client, neonConfig } from '@neondatabase/serverless'
import ws from 'ws'
neonConfig.webSocketConstructor = ws
config({ path: '.env.local' })

// BƯỚC 1 của quy trình 7.1 — TIỀN KIỂM, chạy TRƯỚC khi đụng bất cứ thứ gì.
let blocked = false
for (const [name, url] of [['MAIN', process.env.DATABASE_URL], ['TEST', process.env.TEST_DATABASE_URL]]) {
  const c = new Client({ connectionString: url }); await c.connect()
  const dup = await c.query(`SELECT llm_execution_id, count(*) n FROM analysis_validation
    GROUP BY llm_execution_id HAVING count(*) > 1`)
  const cons = await c.query(`SELECT conname FROM pg_constraint WHERE conname='analysis_validation_execution_key'`)
  const idx = await c.query(`SELECT indexname, indexdef FROM pg_indexes WHERE indexname='analysis_validation_execution_key'`)
  const total = await c.query(`SELECT count(*)::int n FROM analysis_validation`)
  console.log(`\n== ${name} ==`)
  console.log(`  tổng dòng kiểm định : ${total.rows[0].n}`)
  console.log(`  execution có >1 dòng: ${dup.rowCount}`)
  console.log(`  pg_constraint       : ${cons.rowCount ? cons.rows[0].conname : '(không có)'}`)
  console.log(`  pg_indexes          : ${idx.rowCount ? idx.rows[0].indexdef : '(không có)'}`)
  if (dup.rowCount > 0) { console.log('  ✗ CÓ TRÙNG — DỪNG, không chạy 0025'); blocked = true }
  else console.log('  ✓ không có trùng')
  await c.end()
}
console.log(blocked ? '\nKẾT LUẬN: DỪNG' : '\nKẾT LUẬN: đủ điều kiện chạy 0025')
process.exit(blocked ? 1 : 0)
