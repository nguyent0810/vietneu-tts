/**
 * Kiểm chứng G3 TRỰC TIẾP qua pg_catalog/information_schema, trên CẢ HAI database.
 *
 * Không đọc log migration. `migrate()` không ném lỗi KHÔNG phải bằng chứng —
 * chính lần chạy đầu của loạt này đã "không lỗi" trên TEST rồi hỏng trên MAIN.
 */
import { config } from 'dotenv'
import { Client, neonConfig } from '@neondatabase/serverless'
import ws from 'ws'
neonConfig.webSocketConstructor = ws
config({ path: '.env.local' })

const upto = Number(process.argv[2] ?? 4)
let failures = 0
const snap = {}
const fail = (m) => { console.log(`  ✗ ${m}`); failures++ }
const ok = (m) => console.log(`  ✓ ${m}`)

for (const [name, url] of [['MAIN', process.env.DATABASE_URL], ['TEST', process.env.TEST_DATABASE_URL]]) {
  console.log(`\n== ${name} ==`)
  const c = new Client({ connectionString: url }); await c.connect()
  const s = {}
  const one = async (q, p = []) => (await c.query(q, p)).rows[0]
  const all = async (q, p = []) => (await c.query(q, p)).rows

  s.migrations = (await one('SELECT count(*)::int n FROM drizzle.__drizzle_migrations')).n
  console.log(`  migrations ghi nhận: ${s.migrations}`)

  if (upto >= 1) {
    const col = await one(`SELECT data_type, is_nullable, column_default FROM information_schema.columns
      WHERE table_name='cursor_execution_manifest' AND column_name='execution_role'`)
    if (!col || col.is_nullable !== 'NO') fail('0023: execution_role thiếu hoặc nullable')
    else ok(`0023: execution_role NOT NULL, default ${col.column_default}`)
    s.roleEnum = (await all(`SELECT e.enumlabel FROM pg_type t JOIN pg_enum e ON e.enumtypid=t.oid
      WHERE t.typname='cursor_execution_role' ORDER BY e.enumsortorder`)).map(r=>r.enumlabel)
    if (s.roleEnum.join(',') !== 'ANALYSIS,DECLARATION') fail(`0023: enum vai = ${s.roleEnum}`)
    else ok(`0023: enum vai = ${s.roleEnum.join(',')}`)
    for (const n of ['cursor_manifest_analysis_execution_run_fk','cursor_manifest_role_lineage','cursor_manifest_declaration_hash_format']) {
      if (!(await one(`SELECT 1 FROM pg_constraint WHERE conname=$1`, [n]))) fail(`0023: thiếu ${n}`)
      else ok(`0023: ${n}`)
    }
    const src = (await one(`SELECT prosrc FROM pg_proc WHERE proname='cursor_repair_version_immutable'`)).prosrc
    s.repairSrc = src
    if (!src.includes('MIXED_ROLE_REPAIR_CHAIN')) fail('0023: trigger 0020 chưa cập nhật')
    else ok('0023: trigger 0020 so cả sáu hợp đồng + vai')
  }
  if (upto >= 2) {
    if (!(await one(`SELECT 1 FROM information_schema.tables WHERE table_name='cursor_claim_obligation'`)))
      fail('0024: thiếu bảng cursor_claim_obligation')
    else ok('0024: bảng cursor_claim_obligation')
    const idx = await one(`SELECT indexdef FROM pg_indexes WHERE indexname='cursor_obligation_analysis_execution_key'`)
    if (!idx || !idx.indexdef.startsWith('CREATE UNIQUE INDEX')) fail('0024: unique index nghĩa vụ sai')
    else ok('0024: UNIQUE(analysis_execution_id)')
    if (!(await one(`SELECT 1 FROM pg_trigger WHERE tgname='cursor_obligation_immutability'`)))
      fail('0024: thiếu trigger bất biến')
    else ok('0024: trigger bất biến')
    s.obligationChecks = (await all(`SELECT conname FROM pg_constraint WHERE conname LIKE 'cursor_obligation%' ORDER BY 1`)).map(r=>r.conname)
  }
  if (upto >= 3) {
    const oldIdx = await one(`SELECT 1 FROM pg_indexes WHERE indexname='analysis_validation_execution_key'`)
    const oldCon = await one(`SELECT 1 FROM pg_constraint WHERE conname='analysis_validation_execution_key'`)
    if (oldIdx) fail('0025: index CŨ vẫn còn (pg_indexes)')
    else ok('0025: index cũ đã gỡ (pg_indexes)')
    if (oldCon) fail('0025: constraint CŨ vẫn còn (pg_constraint)')
    else ok('0025: index cũ đã gỡ (pg_constraint)')
    const nd = await one(`SELECT indexdef FROM pg_indexes WHERE indexname='analysis_validation_execution_stage_key'`)
    s.stageIdx = nd?.indexdef
    if (!nd) fail('0025: thiếu index mới')
    else if (!nd.indexdef.startsWith('CREATE UNIQUE INDEX')) fail(`0025: index mới không UNIQUE: ${nd.indexdef}`)
    else if (!nd.indexdef.includes('(llm_execution_id, stage)')) fail(`0025: sai cột/thứ tự: ${nd.indexdef}`)
    else if (nd.indexdef.includes('WHERE')) fail(`0025: index PARTIAL: ${nd.indexdef}`)
    else ok(`0025: ${nd.indexdef}`)
    const st = await all(`SELECT stage, count(*)::int n FROM analysis_validation GROUP BY stage ORDER BY 1`)
    s.stageCounts = st.map(r=>`${r.stage}=${r.n}`).join(',') || '(rỗng)'
    console.log(`  0025: phân bố stage = ${s.stageCounts}`)
    if ((await one(`SELECT count(*)::int n FROM analysis_validation WHERE stage IS NULL`)).n > 0)
      fail('0025: còn dòng stage NULL')
    else ok('0025: không có stage NULL')
    const bad = (await one(`SELECT count(*)::int n FROM analysis_validation WHERE stage NOT IN ('ANALYSIS','DECLARATION','COMPOSITE')`)).n
    if (bad > 0) fail(`0025: ${bad} dòng stage không hợp lệ`); else ok('0025: mọi stage hợp lệ')
    const dup = (await all(`SELECT llm_execution_id, stage FROM analysis_validation GROUP BY 1,2 HAVING count(*)>1`)).length
    if (dup > 0) fail(`0025: ${dup} cặp (execution,stage) trùng`); else ok('0025: không có cặp trùng')
  }
  if (upto >= 4) {
    const col = await one(`SELECT is_nullable, column_default FROM information_schema.columns
      WHERE table_name='cursor_analysis_result' AND column_name='result_role'`)
    if (!col || col.is_nullable !== 'NO') fail('0026: result_role thiếu hoặc nullable')
    else ok(`0026: result_role NOT NULL, default ${col.column_default}`)
    const rr = await all(`SELECT result_role, count(*)::int n FROM cursor_analysis_result GROUP BY 1 ORDER BY 1`)
    s.resultRoles = rr.map(r=>`${r.result_role}=${r.n}`).join(',') || '(rỗng)'
    console.log(`  0026: phân bố result_role = ${s.resultRoles}`)
    const src = (await one(`SELECT prosrc FROM pg_proc WHERE proname='cursor_result_semantic_lineage'`)).prosrc
    s.lineageSrc = src
    for (const marker of ['RESULT_WITHOUT_OBLIGATION_SET','RESULT_WITH_FAILED_ANALYSIS','RESULT_WITH_FAILED_DECLARATION','RESULT_LINEAGE_DRIFT','RESULT_ROLE_MISMATCH']) {
      if (!src.includes(marker)) fail(`0026: trigger thiếu ${marker}`)
    }
    if (['RESULT_WITHOUT_OBLIGATION_SET','RESULT_WITH_FAILED_ANALYSIS','RESULT_WITH_FAILED_DECLARATION','RESULT_LINEAGE_DRIFT','RESULT_ROLE_MISMATCH'].every(m=>src.includes(m)))
      ok('0026: trigger hợp nhất đủ năm cổng')
  }
  snap[name] = s
  await c.end()
}

console.log('\n== SO KHỚP MAIN vs TEST ==')
const a = snap.MAIN, b = snap.TEST
for (const k of ['migrations','roleEnum','stageIdx','repairSrc','lineageSrc','obligationChecks']) {
  const x = JSON.stringify(a?.[k]), y = JSON.stringify(b?.[k])
  if (x !== y) fail(`PHÂN KỲ ở "${k}": MAIN=${String(x).slice(0,80)} TEST=${String(y).slice(0,80)}`)
}
if (!failures) ok('hai database khớp nhau ở mọi định nghĩa đã kiểm')
console.log(`\n${failures === 0 ? 'G3 VERIFY ĐẠT' : `G3 VERIFY THẤT BẠI: ${failures} vấn đề`}`)
process.exit(failures ? 1 : 0)
