/**
 * Kiểm chứng lược đồ ĐỘC LẬP với log migration.
 *
 * Lý do tồn tại: cả 0016 lẫn 0017 đều từng in "Migration xong." trong khi KHÔNG
 * hề chạy — tệp SQL có, nhưng chưa đăng ký trong journal của Drizzle. Một dòng
 * log thành công không phải bằng chứng. Chỉ trạng thái thật của database mới là.
 */
import { config } from 'dotenv'
import { Client, neonConfig } from '@neondatabase/serverless'
import { readFileSync, existsSync } from 'node:fs'
import ws from 'ws'

neonConfig.webSocketConstructor = ws
config({ path: '.env.local' })

let failures = 0
const fail = (m) => { console.log(`  ✗ ${m}`); failures++ }
const ok = (m) => console.log(`  ✓ ${m}`)

// --- 1. Tệp SQL và journal phải khớp nhau ------------------------------------
console.log('\n== TỆP SQL + JOURNAL ==')
const journal = JSON.parse(readFileSync('drizzle/meta/_journal.json', 'utf8'))
const tags = journal.entries.map((e) => e.tag)
for (const n of [
  '0016_package_run_channel_lineage',
  '0017_downstream_lineage',
  '0018_parent_execution_run',
  '0019_structural_provenance',
  '0020_repair_same_request',
  '0021_result_semantic_lineage',
  '0022_result_requires_validation',
]) {
  const sqlPath = `drizzle/${n}.sql`
  if (!existsSync(sqlPath)) fail(`thiếu tệp SQL ${sqlPath}`)
  else ok(`có tệp SQL ${n}.sql`)
  if (!tags.includes(n)) fail(`${n} KHÔNG có trong journal`)
  else ok(`${n} đã đăng ký trong journal (idx ${journal.entries.find((e) => e.tag === n).idx})`)
}
// Mọi tệp .sql đều phải có mặt trong journal, không chỉ hai cái trên.
import { readdirSync } from 'node:fs'
const sqlFiles = readdirSync('drizzle').filter((f) => f.endsWith('.sql')).map((f) => f.replace('.sql', ''))
const orphans = sqlFiles.filter((f) => !tags.includes(f))
if (orphans.length) fail(`tệp SQL không có trong journal: ${orphans.join(', ')}`)
else ok(`cả ${sqlFiles.length} tệp SQL đều có trong journal`)

// --- 2. Trạng thái thật của cả hai database ----------------------------------
const EXPECT_COLUMNS = [
  ['cursor_analysis_result', 'analysis_run_id'],
  ['cursor_execution_manifest', 'analysis_run_id'],
  ['analysis_validation', 'analysis_run_id'],
]
const EXPECT_UNIQUE = [
  ['analysis_package', 'analysis_package_id_ws_run_channel_key'],
  ['llm_execution', 'llm_execution_id_ws_run_key'],
  ['cursor_analysis_request', 'cursor_request_id_ws_run_channel_key'],
  ['cursor_analysis_request', 'cursor_request_id_ws_run_key'],
]
const EXPECT_FK = [
  ['cursor_analysis_request', 'cursor_request_package_lineage_fk'],
  ['cursor_analysis_result', 'cursor_result_execution_run_fk'],
  ['cursor_analysis_result', 'cursor_result_request_run_channel_fk'],
  ['cursor_analysis_result', 'cursor_result_run_channel_fk'],
  ['cursor_execution_manifest', 'cursor_manifest_execution_run_fk'],
  ['cursor_execution_manifest', 'cursor_manifest_request_run_fk'],
  ['cursor_execution_manifest', 'cursor_manifest_parent_execution_run_fk'],
  ['analysis_validation', 'analysis_validation_execution_run_fk'],
  ['analysis_validation', 'analysis_validation_run_channel_fk'],
]
// Các ràng buộc CŨ phải BIẾN MẤT — còn sót nghĩa là migration chỉ chạy một nửa.
const EXPECT_ABSENT = [
  ['cursor_execution_manifest', 'cursor_manifest_parent_execution_fk'],
  ['cursor_analysis_request', 'cursor_request_package_workspace_fk'],
  ['cursor_analysis_result', 'cursor_result_execution_workspace_fk'],
  ['cursor_analysis_result', 'cursor_result_request_workspace_fk'],
  ['cursor_execution_manifest', 'cursor_manifest_execution_workspace_fk'],
  ['cursor_execution_manifest', 'cursor_manifest_request_workspace_fk'],
  ['analysis_validation', 'analysis_validation_execution_workspace_fk'],
]

const snapshots = {}
for (const [name, url] of [['MAIN', process.env.DATABASE_URL], ['TEST', process.env.TEST_DATABASE_URL]]) {
  console.log(`\n== ${name} DATABASE ==`)
  if (!url) { fail(`${name}: chưa cấu hình URL`); continue }
  const c = new Client({ connectionString: url })
  await c.connect()

  const cols = await c.query(`SELECT table_name, column_name, is_nullable FROM information_schema.columns
    WHERE column_name='analysis_run_id'`)
  const prov = await c.query(`SELECT column_name, is_nullable FROM information_schema.columns
    WHERE table_name='cursor_execution_manifest' AND column_name IN
    ('schema_version','prompt_version','validator_hash','schema_hash','prompt_source_hash')
    ORDER BY column_name`)
  const trig = await c.query(`SELECT tgname FROM pg_trigger WHERE tgname IN
    ('cursor_repair_version_immutable','cursor_result_semantic_lineage') ORDER BY tgname`)
  const chk = await c.query(`SELECT conname FROM pg_constraint WHERE conname IN
    ('cursor_manifest_hash_format','cursor_result_schema_matches_payload') ORDER BY conname`)
  // Định nghĩa trigger phải khớp bản migration hiện tại: 0022 đòi PHẢI có dòng
  // kiểm định, không chỉ chặn khi nó FALSE.
  const fn = await c.query(`SELECT prosrc FROM pg_proc WHERE proname='cursor_result_semantic_lineage'`)
  const src = fn.rows[0]?.prosrc ?? ''
  if (!src.includes('RESULT_WITHOUT_VALIDATION')) fail('trigger 0021 CŨ còn hiệu lực (thiếu RESULT_WITHOUT_VALIDATION)')
  else ok('định nghĩa trigger khớp bản 0022')
  if (prov.rows.length !== 5 || prov.rows.some((r) => r.is_nullable !== 'NO'))
    fail(`cột nguồn gốc 0019 thiếu hoặc nullable (${prov.rows.length}/5)`)
  else ok('5 cột nguồn gốc 0019 đủ và NOT NULL')
  if (trig.rows.length !== 2) fail(`thiếu trigger (${trig.rows.map((r) => r.tgname).join(', ')})`)
  else ok('cả hai trigger 0020/0022 hoạt động')
  if (chk.rows.length !== 2) fail(`thiếu CHECK (${chk.rows.map((r) => r.conname).join(', ')})`)
  else ok('CHECK băm + CHECK schema payload hoạt động')
  const cons = await c.query(`SELECT c.conname, t.relname AS tbl, c.contype
    FROM pg_constraint c JOIN pg_class t ON t.oid=c.conrelid`)
  const mig = await c.query(`SELECT count(*)::int n FROM drizzle.__drizzle_migrations`)

  const colSet = new Set(cols.rows.map((r) => `${r.table_name}.${r.column_name}`))
  const conSet = new Set(cons.rows.map((r) => r.conname))

  console.log(`  migrations đã ghi nhận: ${mig.rows[0].n} (journal có ${journal.entries.length})`)
  if (mig.rows[0].n !== journal.entries.length) fail(`số migration lệch journal`)
  else ok('số migration khớp journal')

  for (const [t, col] of EXPECT_COLUMNS) {
    if (!colSet.has(`${t}.${col}`)) fail(`thiếu cột ${t}.${col}`)
    else {
      const row = cols.rows.find((r) => r.table_name === t)
      if (row.is_nullable !== 'NO') fail(`${t}.${col} phải NOT NULL`)
      else ok(`${t}.${col} có và NOT NULL`)
    }
  }
  for (const [t, n] of EXPECT_UNIQUE) {
    if (!conSet.has(n)) fail(`thiếu UNIQUE ${n} trên ${t}`); else ok(`UNIQUE ${n}`)
  }
  for (const [t, n] of EXPECT_FK) {
    if (!conSet.has(n)) fail(`thiếu FK ${n} trên ${t}`); else ok(`FK ${n}`)
  }
  for (const [t, n] of EXPECT_ABSENT) {
    if (conSet.has(n)) fail(`ràng buộc CŨ còn sót: ${n} trên ${t}`)
  }
  ok('không còn ràng buộc workspace-only đã bị thay thế')

  snapshots[name] = [...conSet].filter((n) => /cursor_|analysis_validation|analysis_package_id_ws|llm_execution_id_ws/.test(n)).sort()
  await c.end()
}

// --- 3. Hai database phải GIỐNG NHAU ----------------------------------------
console.log('\n== SO KHỚP MAIN vs TEST ==')
if (snapshots.MAIN && snapshots.TEST) {
  const onlyMain = snapshots.MAIN.filter((x) => !snapshots.TEST.includes(x))
  const onlyTest = snapshots.TEST.filter((x) => !snapshots.MAIN.includes(x))
  if (onlyMain.length) fail(`chỉ có ở MAIN: ${onlyMain.join(', ')}`)
  if (onlyTest.length) fail(`chỉ có ở TEST: ${onlyTest.join(', ')}`)
  if (!onlyMain.length && !onlyTest.length) ok(`hai database giống hệt (${snapshots.MAIN.length} ràng buộc liên quan)`)
}

console.log(`\n${failures === 0 ? 'LƯỢC ĐỒ ĐẠT' : `LƯỢC ĐỒ THẤT BẠI: ${failures} vấn đề`}`)
process.exit(failures === 0 ? 0 : 1)
