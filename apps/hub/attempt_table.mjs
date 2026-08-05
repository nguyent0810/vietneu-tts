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
          req.package_hash,
          v.passed, v.total_evidence_refs tot, v.unresolved_evidence_refs unres,
          v.causal_violations cv, v.ctr_violations ctr, v.unsupported_metric_violations umv,
          v.structural_issues, v.evidence_issues, v.claim_issues, v.quality_issues
   FROM llm_execution e
   JOIN cursor_execution_manifest m ON m.llm_execution_id = e.id
   JOIN cursor_analysis_request req ON req.id = m.request_id
   JOIN channel ch ON ch.id = req.channel_id
   LEFT JOIN analysis_validation v ON v.llm_execution_id = e.id
   WHERE e.provider = 'CURSOR_CLI' AND e.created_at >= $1
   ORDER BY ch.label, e.created_at`,
  [SINCE],
)

const sev = (row) => {
  const all = [
    ...(row.structural_issues || []),
    ...(row.evidence_issues || []),
    ...(row.claim_issues || []),
    ...(row.quality_issues || []),
  ]
  return {
    B: all.filter((i) => i.severity === 'BLOCKER').length,
    H: all.filter((i) => i.severity === 'HIGH').length,
    M: all.filter((i) => i.severity === 'MEDIUM').length,
    excerpt:
      all.find((i) => i.excerpt)?.excerpt ??
      all.find((i) => i.message)?.message ??
      '',
  }
}

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
  ['kênh', 'lần', 'exec', 'run', 'trạng thái', 'giây', 'timeout', 'KB', 'bằng chứng', 'B/H/M', 'phân loại']
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
    `${s.B}/${s.H}/${s.M}`,
    cls,
  ]
  console.log(line.map((x) => String(x).padEnd(10)).join(''))
  if (s.excerpt) console.log(`${' '.repeat(10)}↳ "${s.excerpt.slice(0, 150)}"`)

  if (!byChannel.has(row.label)) byChannel.set(row.label, [])
  byChannel.get(row.label).push({ ...row, cls })
}

// Một lô CHỈ hợp lệ khi mọi execution dùng CÙNG một băm validator.
const hashes = new Set(r.rows.map((x) => x.validator_hash))
const versions = new Set(r.rows.map((x) => `${x.schema_version}/${x.prompt_version}`))
console.log(`\n${'='.repeat(70)}\nPHIÊN BẢN TRONG LÔ\n${'='.repeat(70)}`)
console.log(`  băm validator: ${[...hashes].map((h) => String(h).slice(0, 12)).join(', ')}`)
console.log(`  schema/prompt: ${[...versions].join(', ')}`)
if (hashes.size > 1 || versions.size > 1) {
  console.log('  ✗ LÔ TRỘN PHIÊN BẢN — không dùng được để tính ổn định')
}

console.log(`\n${'='.repeat(70)}\nTỔNG HỢP THEO KÊNH\n${'='.repeat(70)}`)
let gateOk = true
for (const [label, rows] of byChannel) {
  // MỘT lần thử ổn định = một CHUỖI execution (gốc + các lần sửa lỗi kỹ thuật).
  // Đếm theo execution sẽ thổi phồng mẫu số và làm tưởng như vượt trần 6.
  const roots = rows.filter((x) => x.parent_execution_id === null)
  const n = roots.length
  const ok = rows.filter((x) => x.status === 'SUCCEEDED').length
  const to = rows.filter((x) => x.timed_out).length
  const rej = n - ok
  const pass = ok >= 3
  if (!pass) gateOk = false
  console.log(
    `${label.padEnd(12)} đạt ${ok}/${n} (${((ok / n) * 100).toFixed(0)}%)  ` +
      `từ chối=${rej}  timeout=${to}  -> ${pass ? 'ĐỦ 3 MẪU' : 'THIẾU MẪU: CỔNG THẤT BẠI'}`,
  )
  // Nếu quá 6 lần thử thì bản thân việc lấy mẫu đã sai quy trình.
  if (n > 6) console.log(`${' '.repeat(12)}⚠ ${n} lần thử ổn định > trần 6 — lô này không hợp lệ`)
  console.log(`${' '.repeat(12)}(${rows.length} execution, gồm cả lần sửa lỗi kỹ thuật trong cùng một lần thử)`)
}

// --- Artifact + _meta ---
console.log(`\n${'='.repeat(70)}\nARTIFACT\n${'='.repeat(70)}`)
const idxPath = resolve(OUT, 'INDEX.json')
if (!existsSync(idxPath)) console.log('✗ thiếu INDEX.json')
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
