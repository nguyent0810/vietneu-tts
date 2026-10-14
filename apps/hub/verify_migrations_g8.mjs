/**
 * Kiểm 0028..0031 TRỰC TIẾP trên database, không qua ORM và không qua log.
 *
 *   node verify_migrations_g8.mjs MAIN|TEST
 *
 * "migrate() không lỗi" đã từng in ra ba lần trong khi không có gì được áp — kể
 * cả lần ngay trước tệp này, khi 0029 vắng mặt trong `_journal.json` nên bị bỏ
 * qua trong im lặng, ĐÚNG BẰNG một dòng "không lỗi" y hệt lần thành công. Nên ở
 * đây không đọc gì do migrate() nói ra: chỉ đọc `pg_proc.prosrc` và `pg_trigger`.
 *
 * CHỈ ĐỌC. Phần chứng minh ràng buộc thật sự TỪ CHỐI một lần ghi nằm trong bộ
 * test tích hợp trên database TEST — xem mục [3] ở cuối tệp.
 */
import { config } from 'dotenv'
import { Client, neonConfig } from '@neondatabase/serverless'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import ws from 'ws'

neonConfig.webSocketConstructor = ws
config({ path: '.env.local' })

const target = (process.argv[2] ?? '').toUpperCase()
if (!['MAIN', 'TEST'].includes(target)) {
  console.error('Dùng: node verify_migrations_g8.mjs MAIN|TEST')
  process.exit(2)
}
const url = target === 'MAIN' ? process.env.DATABASE_URL : process.env.TEST_DATABASE_URL
const c = new Client({ connectionString: url })
await c.connect()
console.log(`${target} @ ${new URL(url.replace(/^postgres/, 'http')).host}`)

let fails = 0
const ok = (label, cond, detail = '') => {
  console.log(`  ${cond ? '✓' : '✗'} ${label}${detail ? `  — ${detail}` : ''}`)
  if (!cond) fails++
}

/* --- 1. Nhật ký migration + băm mã nguồn --------------------------------- */
console.log('\n[1] NHẬT KÝ MIGRATION')
const j = await c.query('SELECT count(*)::int n FROM drizzle.__drizzle_migrations')
const journal = JSON.parse(readFileSync('drizzle/meta/_journal.json', 'utf8'))
ok('số dòng nhật ký khớp số mục trong _journal.json', j.rows[0].n === journal.entries.length,
  `db=${j.rows[0].n} tệp=${journal.entries.length}`)
// BĂM ĐÃ ÁP so với BĂM MÃ NGUỒN HIỆN TẠI.
//
// Đếm số dòng thôi thì chưa đủ: sửa nội dung một tệp .sql ĐÃ áp mà giữ nguyên
// nhật ký sẽ không làm lệch con số nào, và database vẫn đang chạy phiên bản cũ
// trong khi mã nguồn nói một điều khác. Drizzle lưu sha256 của NGUYÊN VĂN tệp,
// nên so trực tiếp được.
const applied = await c.query(
  'SELECT hash, created_at FROM drizzle.__drizzle_migrations ORDER BY created_at',
)
const appliedHashes = new Set(applied.rows.map((r) => r.hash))
for (const tag of [
  '0028_composite_pass_uniqueness',
  '0029_authoritative_lineage_indelible',
  '0030_drop_redundant_indelible_triggers',
  '0031_authorization_race_and_lineage',
  '0032_fix_0031_overreach',
  '0033_declaration_payload_scope',
  '0034_manifest_immutable',
]) {
  const present = journal.entries.some((e) => e.tag === tag)
  const src = readFileSync(`drizzle/${tag}.sql`, 'utf8')
  const h = createHash('sha256').update(src, 'utf8').digest('hex')
  ok(`${tag} có trong nhật ký`, present, `băm nguồn ${h.slice(0, 16)}…`)
  ok(`${tag} băm ĐÃ ÁP khớp mã nguồn hiện tại`, appliedHashes.has(h),
    appliedHashes.has(h) ? '' : 'mã nguồn đã đổi SAU khi áp — database chạy phiên bản khác')
}

// Mọi migration trong nhật ký đều phải khớp băm, không chỉ bốn cái trên.
let drift = 0
for (const e of journal.entries) {
  const h = createHash('sha256').update(readFileSync(`drizzle/${e.tag}.sql`, 'utf8'), 'utf8').digest('hex')
  if (!appliedHashes.has(h)) { drift++; console.log(`    ✗ lệch băm: ${e.tag}`) }
}
ok('TOÀN BỘ nhật ký khớp băm mã nguồn', drift === 0, `${drift} tệp lệch`)

/* --- 2. Định nghĩa trigger đọc từ pg_proc.prosrc -------------------------- */
console.log('\n[2] ĐỊNH NGHĨA TRIGGER (pg_proc.prosrc)')
const need = {
  cursor_single_composite_verdict: ['NEW.passed IS NOT TRUE', 'COMPETING_COMPOSITE_VERDICT', 'pg_advisory_xact_lock'],
  cursor_single_authoritative_result: ['COMPETING_AUTHORITATIVE_RESULT', 'pg_advisory_xact_lock'],
  // Bảo vệ chống MỒ CÔI đến từ hai trigger CŨ, không phải từ 0029. 0029 đã bị
  // 0030 gỡ vì trùng lặp — xem đầu tệp 0030.
  enforce_cursor_result_immutability: ['IMMUTABLE_CURSOR_RESULT'],
  enforce_validation_immutability: ['IMMUTABLE_VALIDATION'],
  // 0031 — đua giữa hai giao dịch, lineage, trần theo số lượng.
  cursor_declaration_lineage_sound: ['DECLARATION_ANALYSIS_WRONG_ROLE', 'DECLARATION_ATTEMPT_CAP', 'pg_advisory_xact_lock'],
  // 0032 gộp phép kiểm bản khai vào CUỐI hàm lineage — không còn trigger riêng.
  cursor_result_semantic_lineage: ['RESULT_WITHOUT_DECLARATION_PAYLOAD', 'RESULT_WITH_FAILED_ANALYSIS'],
  // 0034 — bản kê bất biến. Thiếu mục này thì trigger MỚI NHẤT lại là trigger
  // KHÔNG được bộ xác minh nào canh: ai đó DROP nó trên MAIN và mọi lệnh kiểm
  // vẫn xanh, vì băm migration ghi lại thứ ĐÃ ÁP chứ không phải thứ ĐANG ĐÚNG.
  enforce_cursor_manifest_immutability: ['IMMUTABLE_CURSOR_MANIFEST'],
}
for (const [fn, needles] of Object.entries(need)) {
  const r = await c.query('SELECT prosrc FROM pg_proc WHERE proname = $1', [fn])
  if (!r.rows.length) { ok(`hàm ${fn} tồn tại`, false); continue }
  const src = r.rows[0].prosrc
  ok(`hàm ${fn}`, true, `${src.length} ký tự, băm ${createHash('sha256').update(src).digest('hex').slice(0, 16)}…`)
  for (const n of needles) ok(`  chứa "${n}"`, src.includes(n))
}
for (const tg of [
  'analysis_validation_single_composite',
  'cursor_result_single_authoritative',
  'cursor_result_immutability',
  'analysis_validation_immutability',
  'cursor_manifest_declaration_lineage',
  'cursor_result_semantic_lineage',
  'cursor_manifest_immutability',
]) {
  const r = await c.query(
    `SELECT t.tgname, c.relname, t.tgtype FROM pg_trigger t
     JOIN pg_class c ON c.oid = t.tgrelid WHERE t.tgname = $1`, [tg])
  ok(`trigger ${tg} gắn trên bảng`, r.rows.length === 1, r.rows[0]?.relname ?? 'KHÔNG CÓ')
}

/* --- 2b. Trigger 0029 phải KHÔNG còn ---------------------------------- */
console.log('\n[2b] TRIGGER THỪA CỦA 0029 ĐÃ GỠ')
for (const tg of [
  'cursor_result_indelible',
  'analysis_validation_composite_indelible',
  // 0032: trigger song song che mất chẩn đoán cụ thể — phải biến mất.
  'cursor_result_requires_declaration',
]) {
  const r = await c.query('SELECT 1 FROM pg_trigger WHERE tgname = $1', [tg])
  ok(`${tg} đã gỡ`, r.rows.length === 0)
}

/* --- 3. Hành vi ghi: CỐ Ý không làm ở đây ------------------------------- */
//
// Sáu phép thử ghi (nhiều phán quyết KHÔNG ĐẠT; phán quyết ĐẠT đầu tiên; phán
// quyết ĐẠT thứ hai bị từ chối; kết quả chính thức thứ hai bị từ chối; xoá/sửa
// bị từ chối) nằm ở `tests/integration/composite-authorization.test.ts`, chạy
// trên database TEST với đầy đủ fixture.
//
// Không dựng chúng ở đây vì tệp này cũng chạy trên MAIN, và MAIN mang dữ liệu
// thật. Một giao dịch có ROLLBACK vẫn tiêu id tuần tự và vẫn ghi WAL; "gần như
// không để lại gì" không phải lý do đủ để ghi vào database sản xuất khi cùng
// bằng chứng ấy lấy được ở nơi khác mà không có rủi ro nào.
console.log('\n[3] HÀNH VI GHI — xem composite-authorization.test.ts (chạy trên TEST)')

await c.end()
console.log(`\n${fails === 0 ? `0028..0034 TREN ${target}: DAT` : `0028..0034 TREN ${target}: THAT BAI (${fails} muc)`}`)
process.exit(fails === 0 ? 0 : 1)
