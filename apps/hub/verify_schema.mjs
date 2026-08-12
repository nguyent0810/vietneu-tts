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
  '0028_composite_pass_uniqueness',
  '0029_authoritative_lineage_indelible',
  '0030_drop_redundant_indelible_triggers',
  '0031_authorization_race_and_lineage',
  '0032_fix_0031_overreach',
  '0033_declaration_payload_scope',
  '0034_manifest_immutable',
  '0035_manifest_source_hashes',
  '0036_composite_requires_declaration_role',
  '0027_declaration_result_composite_verdict',
  '0023_execution_role_contracts',
  '0024_claim_obligation',
  '0025_validation_stage',
  '0026_result_role_composite_gate',
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
/*
 * Cot CHO PHEP NULL nhung BAT BUOC PHAI TON TAI (0035).
 *
 * Tach khoi EXPECT_COLUMNS vi danh sach do duoc nuoi boi mot cau truy van chi
 * loc `column_name='analysis_run_id'`, va no doi NOT NULL. Nam cot cua 0035 co
 * chu dinh cho phep NULL (hang cu va duong chay mot luot khong co chung).
 *
 * Vi sao van phai kiem: SQL cua 0035 la phep cong thuan tuy, nhung MA thi khong
 * — `run.ts` ghi ca nam cot o MOI ban ke. Tren mot database chua ap 0035, script
 * nay se in "LUOC DO DAT" trong khi moi lan chay chet ngay o INSERT dau tien.
 * Dung loai lech TEST/MAIN ma 0026 ghi nhan da tung xay ra mot lan.
 */
const EXPECT_NULLABLE_COLUMNS = [
  ['cursor_execution_manifest', 'obligation_generator_hash'],
  ['cursor_execution_manifest', 'composite_source_hash'],
  ['cursor_execution_manifest', 'sensitive_lexicon_hash'],
  ['cursor_execution_manifest', 'identity_source_hash'],
  ['cursor_execution_manifest', 'provenance_source_hash'],
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
  const nullableCols = await c.query(`SELECT table_name, column_name FROM information_schema.columns
    WHERE (table_name, column_name) IN (${EXPECT_NULLABLE_COLUMNS.map(
      ([t, col]) => `('${t}','${col}')`,
    ).join(',')})`)
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

  /*
   * TRIGGER 0036/0037 phải ĐANG TỒN TẠI, không chỉ "đã từng được áp".
   *
   * `verify_migrations_g8.mjs` so băm tệp migration với băm đã ghi — nó chứng
   * minh LỊCH SỬ, không chứng minh TRẠNG THÁI HIỆN TẠI. Một `DROP TRIGGER` sau
   * đó không làm phép so ấy đỏ, và hai lớp cấp phép mới nhất biến mất trong im
   * lặng: hàng COMPOSITE lại ra đời được từ execution vai ANALYSIS, và bản khai
   * lệch bản kê lại cấp phép được.
   */
  const authTrg = await c.query(`SELECT tgname FROM pg_trigger WHERE tgname IN
    ('cursor_z_composite_requires_declaration_role_trg',
     'cursor_zz_declaration_row_matches_manifest_trg') ORDER BY tgname`)
  const authNames = authTrg.rows.map((r) => r.tgname)
  for (const t of [
    'cursor_z_composite_requires_declaration_role_trg',
    'cursor_zz_declaration_row_matches_manifest_trg',
  ]) {
    if (!authNames.includes(t)) fail(`thiếu trigger cấp phép ${t} (0036/0037 đã bị gỡ?)`)
    else ok(`trigger cấp phép ${t} còn hiệu lực`)
  }
  // Và phải là ĐÚNG bản, không phải một hàm cùng tên đã bị viết lại rỗng.
  const authFns = await c.query(`SELECT proname, prosrc FROM pg_proc WHERE proname IN
    ('cursor_composite_requires_declaration_role','cursor_declaration_row_matches_manifest')`)
  for (const [name, needle] of [
    ['cursor_composite_requires_declaration_role', 'COMPOSITE_REQUIRES_DECLARATION_ROLE'],
    ['cursor_declaration_row_matches_manifest', 'DECLARATION_ANALYSIS_MISMATCH'],
  ]) {
    const row = authFns.rows.find((r) => r.proname === name)
    if (!row) fail(`thiếu hàm ${name}`)
    else if (!row.prosrc.includes(needle)) fail(`hàm ${name} KHÔNG còn nêu ${needle}`)
    else ok(`hàm ${name} đúng bản`)
  }
  if (prov.rows.length !== 5 || prov.rows.some((r) => r.is_nullable !== 'NO'))
    fail(`cột nguồn gốc 0019 thiếu hoặc nullable (${prov.rows.length}/5)`)
  else ok('5 cột nguồn gốc 0019 đủ và NOT NULL')
  if (trig.rows.length !== 2) fail(`thiếu trigger (${trig.rows.map((r) => r.tgname).join(', ')})`)
  else ok('cả hai trigger 0020/0022 hoạt động')
  if (chk.rows.length !== 2) fail(`thiếu CHECK (${chk.rows.map((r) => r.conname).join(', ')})`)
  else ok('CHECK băm + CHECK schema payload hoạt động')
  // --- G3: kiến trúc HAI LƯỢT ---------------------------------------------
  const g3idx = await c.query(`SELECT indexname, indexdef FROM pg_indexes WHERE indexname IN
    ('analysis_validation_execution_stage_key','analysis_validation_execution_key',
     'cursor_obligation_analysis_execution_key')`)
  const byName = Object.fromEntries(g3idx.rows.map((r) => [r.indexname, r.indexdef]))
  if (byName['analysis_validation_execution_key']) fail('0025: index kiem dinh CU van con')
  else ok('0025: index kiểm định cũ đã gỡ')
  const stageIdx = byName['analysis_validation_execution_stage_key']
  if (!stageIdx || !stageIdx.startsWith('CREATE UNIQUE INDEX') ||
      !stageIdx.includes('(llm_execution_id, stage)') || stageIdx.includes('WHERE'))
    fail(`0025: index chặng sai định nghĩa: ${stageIdx}`)
  else ok('0025: UNIQUE(llm_execution_id, stage), không partial')
  if (!byName['cursor_obligation_analysis_execution_key']) fail('0024: thiếu UNIQUE tập nghĩa vụ')
  else ok('0024: UNIQUE(analysis_execution_id)')

  const nullStage = await c.query(`SELECT count(*)::int n FROM analysis_validation WHERE stage IS NULL`)
  if (nullStage.rows[0].n > 0) fail(`0025: ${nullStage.rows[0].n} dòng stage NULL`)
  else ok('0025: không có stage NULL')

  const dupStage = await c.query(`SELECT count(*)::int n FROM (
    SELECT llm_execution_id, stage FROM analysis_validation GROUP BY 1,2 HAVING count(*)>1) d`)
  if (dupStage.rows[0].n > 0) fail(`0025: ${dupStage.rows[0].n} cặp (execution,stage) trùng`)
  else ok('0025: không có cặp (execution,stage) trùng')

  // --- G5: cấp phép kết quả chính thức -------------------------------------
  const g5idx = await c.query(`SELECT indexdef FROM pg_indexes
    WHERE indexname='cursor_declaration_execution_key'`)
  if (!g5idx.rows[0]?.indexdef?.startsWith('CREATE UNIQUE INDEX'))
    fail('0027: thiếu UNIQUE index bản khai')
  else ok('0027: UNIQUE(llm_execution_id) trên bản khai')
  const g5trg = await c.query(`SELECT tgname FROM pg_trigger WHERE tgname IN
    ('cursor_declaration_immutability','analysis_validation_single_composite') ORDER BY tgname`)
  if (g5trg.rows.length !== 2) fail(`0027: thiếu trigger (${g5trg.rows.map((r) => r.tgname).join(', ')})`)
  else ok('0027: trigger bất biến bản khai + phán quyết COMPOSITE duy nhất')
  const g6fn = (await c.query(
    `SELECT prosrc FROM pg_proc WHERE proname='cursor_single_authoritative_result'`)).rows[0]?.prosrc ?? ''
  if (!g6fn.includes('COMPETING_AUTHORITATIVE_RESULT')) fail('0028: thiếu hàng rào kết quả duy nhất')
  else ok('0028: chặn kết quả chính thức cạnh tranh')
  if (!(await c.query(`SELECT 1 FROM pg_trigger WHERE tgname='cursor_result_single_authoritative'`)).rowCount)
    fail('0028: thiếu trigger kết quả duy nhất')
  else ok('0028: trigger kết quả chính thức duy nhất')
  const g6dupResult = await c.query(`SELECT count(*)::int n FROM (
    SELECT m.analysis_execution_id FROM cursor_analysis_result r
    JOIN cursor_execution_manifest m ON m.llm_execution_id = r.llm_execution_id
    WHERE r.result_role='COMPOSITE' AND m.analysis_execution_id IS NOT NULL
    GROUP BY m.analysis_execution_id HAVING count(*)>1) d`)
  if (g6dupResult.rows[0].n > 0) fail(`0028: ${g6dupResult.rows[0].n} lượt phân tích có >1 kết quả chính thức`)
  else ok('0028: không có kết quả chính thức cạnh tranh trong dữ liệu')

  // --- 0029/0030: chống mồ côi đến từ trigger CŨ, không từ 0029 ---
  //
  // 0029 thêm hai trigger trùng lặp rồi 0030 gỡ đi. Kiểm ở đây đúng hai điều:
  // trigger thừa đã biến mất, và trigger THẬT vẫn còn — vì hỏng nguy hiểm nhất
  // của một lần gỡ là gỡ nhầm cái đang bảo vệ.
  const g7 = await c.query(`SELECT tgname FROM pg_trigger WHERE tgname IN
    ('cursor_result_indelible','analysis_validation_composite_indelible',
     'cursor_result_immutability','analysis_validation_immutability') ORDER BY tgname`)
  const tg = g7.rows.map((r) => r.tgname)
  if (tg.includes('cursor_result_indelible') || tg.includes('analysis_validation_composite_indelible'))
    fail('0030: trigger thừa của 0029 vẫn còn')
  else ok('0030: đã gỡ trigger thừa của 0029')
  // --- 0031: khoá chống đua + lineage + trần theo SỐ LƯỢNG ---
  const g8 = await c.query(`SELECT proname, prosrc FROM pg_proc WHERE proname IN
    ('cursor_single_composite_verdict','cursor_single_authoritative_result',
     'cursor_declaration_lineage_sound','cursor_result_semantic_lineage')`)
  const g8src = Object.fromEntries(g8.rows.map((r) => [r.proname, r.prosrc]))
  for (const fn of ['cursor_single_composite_verdict', 'cursor_single_authoritative_result',
                    'cursor_declaration_lineage_sound']) {
    if (!g8src[fn]?.includes('pg_advisory_xact_lock')) fail(`0031: ${fn} chưa lấy khoá chống đua`)
    else ok(`0031: ${fn} lấy khoá trước khi đọc`)
  }
  if (!g8src.cursor_declaration_lineage_sound?.includes('DECLARATION_ATTEMPT_CAP'))
    fail('0031: thiếu trần lần thử theo SỐ LƯỢNG')
  else ok('0031: trần lần thử tính theo số lượng, không theo giá trị cột')
  if (!g8src.cursor_result_semantic_lineage?.includes('RESULT_WITHOUT_DECLARATION_PAYLOAD'))
    fail('0031: kết quả không đòi bản khai đã lưu')
  else ok('0031: kết quả chính thức đòi bản khai đã lưu')

  // 0034: bản kê là bảng CUỐI CÙNG trong chuỗi cấp phép còn sửa/xoá được.
  const g9 = await c.query(`SELECT tgname, tgtype FROM pg_trigger
    WHERE tgname = 'cursor_manifest_immutability'`)
  if (!g9.rows.length) fail('0034: thiếu trigger bất biến bản kê')
  else {
    const mask = Number(g9.rows[0].tgtype)
    if (!(mask & 8)) fail(`0034: trigger bản kê không chạy trên DELETE (tgtype=${mask})`)
    else if (!(mask & 16)) fail(`0034: trigger bản kê không chạy trên UPDATE (tgtype=${mask})`)
    else ok('0034: bản kê bất biến trên CẢ UPDATE và DELETE')
  }

  for (const t of ['cursor_result_immutability', 'analysis_validation_immutability']) {
    if (!tg.includes(t)) fail(`0030: MẤT trigger bất biến thật "${t}"`)
    else ok(`0030: giữ nguyên trigger bất biến "${t}"`)
  }

  const g5fn = (await c.query(
    `SELECT prosrc FROM pg_proc WHERE proname='cursor_single_composite_verdict'`)).rows[0]?.prosrc ?? ''
  if (!g5fn.includes('COMPETING_COMPOSITE_VERDICT')) fail('0027: trigger phán quyết duy nhất sai định nghĩa')
  else ok('0027: chặn phán quyết COMPOSITE cạnh tranh')
  const g5dupComposite = await c.query(`SELECT count(*)::int n FROM (
    SELECT m.analysis_execution_id FROM analysis_validation v
    JOIN cursor_execution_manifest m ON m.llm_execution_id = v.llm_execution_id
    WHERE v.stage='COMPOSITE' AND v.passed IS TRUE AND m.analysis_execution_id IS NOT NULL
    GROUP BY m.analysis_execution_id HAVING count(*)>1) d`)
  if (g5dupComposite.rows[0].n > 0) fail(`0027: ${g5dupComposite.rows[0].n} lượt phân tích có >1 phán quyết COMPOSITE ĐẠT`)
  else ok('0027: không có phán quyết COMPOSITE ĐẠT cạnh tranh trong dữ liệu')

  const lineageSrc = (await c.query(
    `SELECT prosrc FROM pg_proc WHERE proname='cursor_result_semantic_lineage'`)).rows[0]?.prosrc ?? ''
  const missingGates = ['RESULT_WITHOUT_OBLIGATION_SET','RESULT_WITH_FAILED_ANALYSIS',
    'RESULT_WITH_FAILED_DECLARATION','RESULT_LINEAGE_DRIFT','RESULT_ROLE_MISMATCH']
    .filter((m) => !lineageSrc.includes(m))
  if (missingGates.length) fail(`0026: trigger thiếu cổng: ${missingGates.join(', ')}`)
  else ok('0026: trigger hợp nhất đủ năm cổng')

  const repairSrc = (await c.query(
    `SELECT prosrc FROM pg_proc WHERE proname='cursor_repair_version_immutable'`)).rows[0]?.prosrc ?? ''
  if (!repairSrc.includes('MIXED_ROLE_REPAIR_CHAIN')) fail('0023: trigger 0020 chưa so vai')
  else ok('0023: trigger 0020 so cả sáu hợp đồng + vai')

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
  const nullableSet = new Set(nullableCols.rows.map((r) => `${r.table_name}.${r.column_name}`))
  for (const [t, col] of EXPECT_NULLABLE_COLUMNS) {
    if (!nullableSet.has(`${t}.${col}`)) fail(`thiếu cột ${t}.${col} (0035 chưa áp?)`)
    else ok(`${t}.${col} có`)
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

  // --- 2b. SCHEMA 2.1: round-trip JSONB + hành vi THẬT của CHECK 0022 --------
  //
  // Bản thiết kế kết luận "không cần migration cho 2.1" vì `payload` là JSONB và
  // CHECK 0022 so cột với `payload->>'schemaVersion'` chứ không hardcode giá
  // trị. Đó là một SUY LUẬN. Ở đây nó được thi hành thật.
  //
  // Ràng buộc dùng để thử được LẤY TỪ CHÍNH DATABASE (`pg_get_constraintdef`),
  // không chép lại từ tệp migration — nếu database đang chạy một định nghĩa
  // khác với tệp, phép thử này chạy theo cái ĐANG CHẠY.
  //
  // Toàn bộ nằm trong một transaction có ROLLBACK và một TEMP TABLE: không đụng
  // vào dữ liệu thật, nhưng vẫn là postgres thật đánh giá đúng biểu thức đó.
  {
    const def = (
      await c.query(
        `SELECT pg_get_constraintdef(oid) AS def FROM pg_constraint
         WHERE conname = 'cursor_result_schema_matches_payload'`,
      )
    ).rows[0]?.def
    if (!def) fail('không đọc được định nghĩa CHECK cursor_result_schema_matches_payload')
    else if (/'2\.0'|'1\.0'|'2\.1'/.test(def)) {
      fail(`CHECK 0022 HARDCODE phiên bản, sẽ phải sửa mỗi lần lên bản: ${def}`)
    } else {
      ok('CHECK 0022 so cột với payload, không hardcode phiên bản')

      const PAYLOAD_21 = {
        schemaVersion: '2.1',
        keyFindings: [{ id: 'F-001', limitations: ['cỡ mẫu lượt xem thấp nên CTR nhiễu', 'chưa bật đo impressions'] }],
        metricClaims: [
          {
            id: 'MC-001',
            sourceRef: { section: 'KEY_FINDING', itemId: 'F-001', field: 'limitations', ordinal: 0 },
          },
          // itemId RỖNG và field dạng "@N": hai bề mặt dễ bị driver chuẩn hoá nhất.
          { id: 'MC-002', sourceRef: { section: 'MANUAL_REVIEW', itemId: '', field: 'reason@0', ordinal: 1 } },
        ],
      }

      await c.query('BEGIN')
      try {
        await c.query(
          `CREATE TEMP TABLE probe_2_1 (
             schema_version text NOT NULL,
             payload jsonb NOT NULL,
             CONSTRAINT probe_schema_matches_payload ${def}
           ) ON COMMIT DROP`,
        )

        // 33 — round-trip: đưa vào, lấy ra, phải y hệt từng khoá.
        await c.query('INSERT INTO probe_2_1 VALUES ($1, $2::jsonb)', ['2.1', JSON.stringify(PAYLOAD_21)])
        const back = (await c.query('SELECT payload FROM probe_2_1')).rows[0].payload
        // So theo GIÁ TRỊ, không so theo chuỗi.
        //
        // `jsonb` KHÔNG giữ thứ tự khoá (nó sắp lại theo độ dài rồi theo byte) và
        // không giữ khoá trùng. Vì vậy `JSON.stringify(a) === JSON.stringify(b)`
        // là phép so SAI ở đây: nó báo đỏ cho một round-trip hoàn toàn đúng.
        // Điều này cũng có nghĩa: băm payload phải tính trên CHUỖI GỐC trước khi
        // ghi, không bao giờ tính lại từ giá trị đọc ra khỏi JSONB.
        const deepEqual = (a, b) => {
          if (a === b) return true
          if (typeof a !== typeof b || a === null || b === null) return false
          if (Array.isArray(a) !== Array.isArray(b)) return false
          if (typeof a !== 'object') return false
          const ka = Object.keys(a).sort()
          const kb = Object.keys(b).sort()
          if (ka.length !== kb.length || ka.some((k, i) => k !== kb[i])) return false
          return ka.every((k) => deepEqual(a[k], b[k]))
        }
        if (!deepEqual(back, PAYLOAD_21)) {
          fail(`payload 2.1 KHÔNG round-trip nguyên vẹn qua JSONB: ${JSON.stringify(back)}`)
        } else ok('payload 2.1 round-trip qua JSONB nguyên vẹn (kể cả itemId rỗng, field "@N", ordinal số)')

        const probe = (
          await c.query(
            `SELECT payload->'metricClaims'->1->'sourceRef'->>'itemId' AS item,
                    (payload->'metricClaims'->1->'sourceRef'->>'ordinal')::int AS ord
             FROM probe_2_1`,
          )
        ).rows[0]
        if (probe.item !== '' || probe.ord !== 1) fail(`sourceRef bị đổi trong JSONB: ${JSON.stringify(probe)}`)
        else ok('đọc thẳng sourceRef trong JSONB cho đúng giá trị đã ghi')

        // 34 — CHECK phải NHẬN 2.1 và vẫn TỪ CHỐI hai ca hỏng.
        const rejects = async (label, sv, payload) => {
          try {
            await c.query('SAVEPOINT s')
            await c.query('INSERT INTO probe_2_1 VALUES ($1, $2::jsonb)', [sv, JSON.stringify(payload)])
            await c.query('ROLLBACK TO SAVEPOINT s')
            fail(`CHECK 0022 KHÔNG chặn ${label}`)
          } catch {
            await c.query('ROLLBACK TO SAVEPOINT s')
            ok(`CHECK 0022 chặn ${label}`)
          }
        }
        await rejects('payload THIẾU schemaVersion', '2.1', { keyFindings: [] })
        await rejects('payload khai LỆCH cột (cột 2.1, payload 2.0)', '2.1', { schemaVersion: '2.0' })
      } finally {
        await c.query('ROLLBACK')
      }
    }
  }

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
