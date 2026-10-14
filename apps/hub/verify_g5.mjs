import { config } from 'dotenv'
import { Client, neonConfig } from '@neondatabase/serverless'
import ws from 'ws'
neonConfig.webSocketConstructor = ws
config({ path: '.env.local' })
let failures = 0
const snap = {}
const fail = (m) => { console.log(`  ✗ ${m}`); failures++ }
const ok = (m) => console.log(`  ✓ ${m}`)
for (const [name, url] of [['MAIN', process.env.DATABASE_URL], ['TEST', process.env.TEST_DATABASE_URL]]) {
  console.log(`\n== ${name} ==`)
  const c = new Client({ connectionString: url }); await c.connect()
  const one = async (q) => (await c.query(q)).rows[0]
  const s = {}
  s.migrations = (await one('SELECT count(*)::int n FROM drizzle.__drizzle_migrations')).n
  console.log(`  migrations: ${s.migrations}`)
  if (!(await one(`SELECT 1 FROM information_schema.tables WHERE table_name='cursor_declaration_result'`)))
    fail('0027: thiếu bảng cursor_declaration_result'); else ok('0027: bảng cursor_declaration_result')
  s.declIdx = (await one(`SELECT indexdef FROM pg_indexes WHERE indexname='cursor_declaration_execution_key'`))?.indexdef
  if (!s.declIdx?.startsWith('CREATE UNIQUE INDEX')) fail(`0027: unique index bản khai sai: ${s.declIdx}`)
  else ok('0027: UNIQUE(llm_execution_id) trên bản khai')
  for (const t of ['cursor_declaration_immutability','analysis_validation_single_composite']) {
    if (!(await one(`SELECT 1 FROM pg_trigger WHERE tgname='${t}'`))) fail(`0027: thiếu trigger ${t}`)
    else ok(`0027: trigger ${t}`)
  }
  s.singleComposite = (await one(`SELECT prosrc FROM pg_proc WHERE proname='cursor_single_composite_verdict'`))?.prosrc ?? ''
  if (!s.singleComposite.includes('COMPETING_COMPOSITE_VERDICT')) fail('0027: trigger phán quyết duy nhất chưa đúng')
  else ok('0027: trigger chặn phán quyết COMPOSITE cạnh tranh')
  s.checks = (await c.query(`SELECT conname FROM pg_constraint WHERE conname LIKE 'cursor_declaration%' ORDER BY 1`)).rows.map(r=>r.conname)
  console.log(`  CHECK/FK bản khai: ${s.checks.join(', ')}`)
  snap[name] = s
  await c.end()
}
console.log('\n== SO KHỚP MAIN vs TEST ==')
for (const k of ['migrations','declIdx','singleComposite','checks']) {
  if (JSON.stringify(snap.MAIN?.[k]) !== JSON.stringify(snap.TEST?.[k])) fail(`PHÂN KỲ ở "${k}"`)
}
if (!failures) ok('hai database khớp nhau')
console.log(`\n${failures === 0 ? 'G5 SCHEMA ĐẠT' : `G5 SCHEMA THẤT BẠI: ${failures}`}`)
process.exit(failures ? 1 : 0)
