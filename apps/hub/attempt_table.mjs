/**
 * Bảng TOÀN BỘ lần chạy Cursor, kể cả lần hỏng.
 *
 * Chỉ báo cáo trên các lần ĐẠT là thiên lệch kẻ sống sót: một kênh hỏng 9/10 sẽ
 * trông "ổn định" vì chỉ kẻ sống sót được đem so. Ở đây mọi lần thử đều xuất
 * hiện, và cột `hợp lệ` nói rõ lần nào được tính vào thống kê ổn định.
 *
 *   node attempt_table.mjs <ISO thời điểm bắt đầu lô>
 */
import { config } from 'dotenv'
import { Client, neonConfig } from '@neondatabase/serverless'
import { existsSync, readFileSync, statSync } from 'node:fs'
import { resolve } from 'node:path'
import ws from 'ws'
import {
  accountAttempts,
  artifactIndexGateOk,
  ATTEMPT_CAP,
  mixedAcrossBatch,
  mixedWithinAttempt,
  samplingCapOk,
  severityCounts,
  TERMINAL_VALIDATION_LATERAL,
} from './attempt_accounting.mjs'

neonConfig.webSocketConstructor = ws
config({ path: '.env.local' })

const SINCE = process.argv[2] ?? '1970-01-01T00:00:00Z'
const OUT = resolve(process.cwd(), '../../analysis_out')

const c = new Client({ connectionString: process.env.DATABASE_URL })
await c.connect()

const r = await c.query(
  `SELECT ch.label,
          e.id exec_id, e.analysis_run_id run_id, e.status, e.execution_sequence seq,
          e.created_at,
          m.attempt_number, m.parent_execution_id, m.failure_class, m.duration_ms, m.timed_out,
          m.stdout_bytes, m.tool_name,
          m.validator_hash, m.schema_version, m.prompt_version,
          m.schema_hash, m.prompt_source_hash,
          -- Năm băm mã nguồn còn lại (0035, M-3). Không có cột thì bảng này
          -- khong so duoc chung o muc lo, va mot thay doi sensitive.ts giua
          -- chừng chỉ được GHI LẠI chứ không bị PHÁT HIỆN.
          m.obligation_generator_hash, m.composite_source_hash,
          m.sensitive_lexicon_hash, m.identity_source_hash, m.provenance_source_hash,
          -- NGUỒN GỐC HAI LƯỢT: thiếu các cột này thì bảng lần thử không phân
          -- biệt nổi một lượt PHÂN TÍCH với một lượt KHAI BÁO, và mọi con số
          -- ổn định gộp chung hai thứ khác hẳn nhau.
          m.execution_role, m.analysis_execution_id,
          m.obligation_generator_version, m.declaration_prompt_version,
          m.declaration_prompt_source_hash, m.composite_validator_version,
          m.analysis_payload_hash, m.obligation_set_hash,
          req.id request_id, req.package_hash,
          v.passed, v.total_evidence_refs tot, v.unresolved_evidence_refs unres,
          v.causal_violations cv, v.ctr_violations ctr, v.unsupported_metric_violations umv,
          res.result_role,
          -- So nghia vu cua luot phan tich tuong ung: 0 phai DEM TACH RIENG.
          o.obligation_count,
          v.id terminal_validation_id, v.stage terminal_stage,
          v.failure_class terminal_failure_class,
          res.id result_id,
          v.structural_issues, v.evidence_issues, v.claim_issues, v.quality_issues
   FROM llm_execution e
   JOIN cursor_execution_manifest m ON m.llm_execution_id = e.id
   JOIN cursor_analysis_request req ON req.id = m.request_id
   JOIN channel ch ON ch.id = req.channel_id
   ${TERMINAL_VALIDATION_LATERAL}
   -- CHỈ hiện vật CHÍNH THỨC. Không lọc vai thì hàng kết quả vai ANALYSIS
   -- (văn xuôi đã đóng băng) cũng làm result_id khác null, và mỗi bài phân
   -- tích đạt tự cấp cho mình một mẫu.
   LEFT JOIN cursor_analysis_result res
     ON res.llm_execution_id = e.id AND res.result_role = 'COMPOSITE'
   LEFT JOIN cursor_claim_obligation o
     ON o.analysis_execution_id = COALESCE(m.analysis_execution_id, e.id)
   WHERE e.provider = 'CURSOR_CLI' AND e.created_at >= $1
   ORDER BY ch.label, e.created_at`,
  [SINCE],
)

const sev = severityCounts

/** Phân loại thất bại theo BẰNG CHỨNG, không theo phỏng đoán. */
function classify(row) {
  if (row.status === 'SUCCEEDED') return 'đạt'
  if (row.timed_out) return 'timeout'
  if (['CLI_NONZERO_EXIT', 'OUTPUT_TOO_LARGE'].includes(row.failure_class)) return 'lỗi vendor/runtime'
  if (['INVALID_JSON', 'PROSE_OUTSIDE_JSON', 'SCHEMA_MISMATCH', 'MISSING_REQUIRED_FIELD',
       'UNSUPPORTED_SCHEMA_VERSION', 'TRUNCATED_OUTPUT'].includes(row.failure_class))
    return 'mô hình sai định dạng'
  if (row.failure_class === 'UNSUPPORTED_CLAIM') return 'khẳng định không có căn cứ (mô hình)'
  if (row.failure_class === 'EVIDENCE_UNRESOLVED') return 'bằng chứng không neo được (mô hình)'
  return row.failure_class
}

const byChannel = new Map()
console.log(
  ['kênh', 'lần', 'exec', 'run', 'trạng thái', 'giây', 'timeout', 'KB', 'bằng chứng', 'chặng cuối', 'B/H/M', 'phân loại']
    .map((h) => h.padEnd(10))
    .join(''),
)
console.log('-'.repeat(120))

for (const row of r.rows) {
  const s = sev(row)
  const cls = classify(row)
  const line = [
    row.label.slice(0, 10),
    String(row.attempt_number),
    row.exec_id.slice(0, 8),
    row.run_id.slice(0, 8),
    row.status.slice(0, 10),
    (row.duration_ms / 1000).toFixed(0),
    row.timed_out ? 'CÓ' : '-',
    (row.stdout_bytes / 1024).toFixed(1),
    row.tot === null ? '-' : `${row.tot - row.unres}/${row.tot}`,
    // Chặng nào SINH RA các con số bên cạnh — không có cột này thì "0/0/0" của
    // một lần hỏng ở chặng phân tích trông y hệt "0/0/0" của một lần sạch sẽ.
    row.terminal_stage ?? '-',
    `${s.B}/${s.H}/${s.M}`,
    cls,
  ]
  console.log(line.map((x) => String(x).padEnd(10)).join(''))
  if (s.excerpt) console.log(`${' '.repeat(10)}↳ "${s.excerpt.slice(0, 150)}"`)

  if (!byChannel.has(row.label)) byChannel.set(row.label, [])
  byChannel.get(row.label).push({ ...row, cls })
}

// PHIÊN BẢN: so TRONG TỪNG VAI, không so gộp.
//
// Kiến trúc hai lượt làm phép kiểm cũ sai: lượt PHÂN TÍCH chạy prompt 3.0.0 còn
// lượt KHAI BÁO chạy prompt khai báo 1.0.0, nên một tập gộp LUÔN có hai phần tử
// và cảnh báo "lô trộn phiên bản" sẽ kêu ở mọi lô đúng đắn. Một cảnh báo luôn
// kêu là một cảnh báo không ai đọc. Trong TỪNG vai thì đồng nhất vẫn là bắt buộc.
const hashes = new Set(r.rows.map((x) => x.validator_hash))
console.log(`\n${'='.repeat(70)}\nPHIÊN BẢN TRONG LÔ\n${'='.repeat(70)}`)
console.log(`  băm validator: ${[...hashes].map((h) => String(h).slice(0, 12)).join(', ')}`)
let versionOk = hashes.size <= 1
if (hashes.size > 1) console.log('  ✗ TRỘN BĂM VALIDATOR — không dùng được để tính ổn định')

for (const role of ['ANALYSIS', 'DECLARATION']) {
  const rows = r.rows.filter((x) => x.execution_role === role)
  if (!rows.length) continue
  const v = new Set(rows.map((x) => `${x.schema_version}/${x.prompt_version}`))
  console.log(`  ${role.padEnd(11)}: ${[...v].join(', ')}  (${rows.length} execution)`)
  if (v.size > 1) {
    console.log(`  ✗ VAI ${role} TRỘN PHIÊN BẢN`)
    versionOk = false
  }
}

// SÁU hợp đồng của lượt khai báo phải đồng nhất trên toàn lô.
// BĂM MÃ NGUỒN cũng phải đồng nhất, không chỉ SỐ PHIÊN BẢN.
//
// Việc bump phiên bản là quy ước thủ công; không gì cưỡng chế nó. Sửa nội dung
// `prompt.ts` giữa lần chạy 2 và 3 mà quên bump khiến `prompt_version` không
// đổi trong khi `prompt_source_hash` đổi — lô trộn hai prompt mà bảng in "sạch".
// Phép so nằm trong `attempt_accounting.mjs` để CHẠY ĐƯỢC trong test (M-4).
// Bản trước viết vòng lặp ngay tại đây và bộ test chỉ `grep` tên cột — một
// assertion không thể sai, đã chứng minh bằng mutation.
for (const m of mixedAcrossBatch(r.rows)) {
  const v = new Set(r.rows.filter((x) => x[m.column] != null).map((x) => x[m.column]))
  console.log(`  ✗ TRỘN ${m.column}: ${[...v].map((x) => String(x).slice(0, 12)).join(', ')}`)
  versionOk = false
}

// TRỘN TRONG MỘT LẦN THỬ ỔN ĐỊNH — nghiêm trọng hơn trộn trong lô.
//
// Một lần thử = một lượt phân tích + mọi lượt khai báo phục vụ nó. Nếu hai lượt
// khai báo của CÙNG một bài phân tích neo vào hai băm nghĩa vụ khác nhau thì
// một trong hai đang khai cho một tập nghĩa vụ không còn tồn tại, và kết quả
// "đạt" của nó vô nghĩa.
const mixed = mixedWithinAttempt(r.rows)
for (const m of mixed) {
  console.log(`  ✗ LẦN THỬ ${String(m.analysisExecutionId).slice(0, 8)} TRỘN ${m.field} — ${m.values} giá trị`)
  versionOk = false
}
const mixedAttempts = mixed.length
console.log(`  lần thử trộn phiên bản/băm: ${mixedAttempts}`)

console.log(`\n${'='.repeat(70)}\nTỔNG HỢP THEO KÊNH\n${'='.repeat(70)}`)
let gateOk = versionOk
for (const [label, rows] of byChannel) {
  // KẾ TOÁN dùng chung với bộ test — xem attempt_accounting.mjs.
  const acct = accountAttempts(rows)
  const n = acct.attempts
  const ok = acct.authorized
  const to = acct.timeouts
  const rej = acct.rejected
  if (n === 0) {
    console.log(`${label.padEnd(12)} KHÔNG có lần thử phân tích nào — cổng THẤT BẠI`)
    gateOk = false
    continue
  }
  const pass = ok >= 3
  if (!pass) gateOk = false
  console.log(
    `${label.padEnd(12)} đạt ${ok}/${n} (${((ok / n) * 100).toFixed(0)}%)  ` +
      `từ chối=${rej}  timeout=${to}  -> ${pass ? 'ĐỦ 3 MẪU' : 'THIẾU MẪU: CỔNG THẤT BẠI'}`,
  )
  // MẪU mà bộ dò không tìm thấy ô nhạy cảm nào — in TÁCH RIÊNG, không gộp vào
  // "đạt", và KHÔNG được gọi là "sạch". Xem mục 5 của PHASE4_TRUST_BOUNDARIES.md.
  if (acct.zeroObligationAuthorized > 0) {
    console.log(
      `${' '.repeat(12)}⚠ ${acct.zeroObligationAuthorized}/${ok} mẫu có obligationCount = 0 ` +
        `— "bộ dò KHÔNG TÌM THẤY ô nhạy cảm nào", KHÔNG phải "phân tích sạch"`,
    )
  }
  // Nếu quá trần lần thử thì bản thân việc lấy mẫu đã sai quy trình — và "không
  // hợp lệ" phải làm cổng ĐỎ, không phải chỉ in ra rồi thoát 0.
  // Quyết định nằm trong `attempt_accounting.mjs` để CHẠY ĐƯỢC trong test.
  if (!samplingCapOk(n)) {
    console.log(`${' '.repeat(12)}✗ ${n} lần thử ổn định > trần ${ATTEMPT_CAP} — lô này không hợp lệ`)
    gateOk = false
  }
  console.log(`${' '.repeat(12)}(${rows.length} execution, gồm cả lần sửa lỗi kỹ thuật trong cùng một lần thử)`)
}

// --- Artifact + _meta ---
console.log(`\n${'='.repeat(70)}\nARTIFACT\n${'='.repeat(70)}`)
const idxPath = resolve(OUT, 'INDEX.json')
if (!existsSync(idxPath)) {
  // "Không có dữ liệu" KHÔNG phải "đạt". Toàn bộ phần đối chiếu artifact nằm
  // trong nhánh `else`, nên thiếu INDEX.json nghĩa là KHÔNG kiểm được gì —
  // và một cổng không kiểm được gì thì phải ĐỎ, không phải im lặng cho qua.
  console.log('✗ thiếu INDEX.json — KHÔNG đối chiếu được artifact với database')
  // Quyết định nằm trong `attempt_accounting.mjs` để CHẠY ĐƯỢC trong test.
  gateOk = artifactIndexGateOk({ indexExists: false }) && gateOk
}
else {
  const idx = JSON.parse(readFileSync(idxPath, 'utf8'))
  console.log(`INDEX.json mode=${idx.mode} promptVersion=${idx.promptVersion}`)
  for (const [label, info] of Object.entries(idx.channels)) {
    console.log(`  ${label}: đạt ${info.successes}/${info.attempts}, tệp: ${info.files.join(', ') || '(không có)'}`)
    for (const f of info.files) {
      const p = resolve(OUT, f)
      if (!existsSync(p)) { console.log(`    ✗ ${f} khai trong INDEX nhưng KHÔNG tồn tại`); gateOk = false; continue }
      const meta = JSON.parse(readFileSync(p, 'utf8'))._meta
      const st = statSync(p)
      const match = rows_lookup(label, meta)
      console.log(
        `    ${f}  ${(st.size / 1024).toFixed(1)}KB  ${st.mtime.toISOString().slice(0, 19)}  ` +
          `${match ? '_meta khớp DB ✓' : '_meta KHÔNG khớp DB ✗'}`,
      )
      if (!match) gateOk = false
    }
  }
}

function rows_lookup(label, meta) {
  if (!meta) return false
  const rows = byChannel.get(label) ?? []
  return rows.some((x) => x.exec_id === meta.llmExecutionId && x.package_hash === meta.packageHash)
}

console.log(`\n${gateOk ? 'CỔNG ỔN ĐỊNH + ARTIFACT: ĐẠT' : 'CỔNG ỔN ĐỊNH + ARTIFACT: THẤT BẠI'}`)
await c.end()
process.exit(gateOk ? 0 : 1)
