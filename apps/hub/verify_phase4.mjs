/**
 * Kiểm chứng Phase 4 — KHÔNG tin vào trạng thái, chỉ tin vào dữ liệu.
 *
 * Trạng thái SUCCEEDED là thứ dễ sai nhất: chính lỗi Codex #4 cho thấy một lần
 * chạy mang 3 lỗi HIGH vẫn được ghi SUCCEEDED và trông y hệt một lần đạt thật.
 * Vì vậy script này kiểm lại từ dữ liệu thô, không đọc cột status.
 */
import { config } from 'dotenv'
import { Client, neonConfig } from '@neondatabase/serverless'
import { readFileSync, statSync } from 'node:fs'
import ws from 'ws'

neonConfig.webSocketConstructor = ws
config({ path: '.env.local' })

const SINCE = process.argv[2] ? new Date(process.argv[2]) : new Date(Date.now() - 3600_000)
const CHANNELS = ['phat_giao', 'hinh_su', 'phong_thuy']

const c = new Client({ connectionString: process.env.DATABASE_URL })
await c.connect()

let failures = 0
const fail = (m) => { console.log(`   ✗ ${m}`); failures++ }
const ok = (m) => console.log(`   ✓ ${m}`)

for (const label of CHANNELS) {
  console.log(`\n${'='.repeat(72)}\n${label}\n${'='.repeat(72)}`)

  // Lần chạy MỚI NHẤT của kênh này, kèm toàn bộ lineage.
  const r = await c.query(`
    SELECT e.id exec_id, e.status, e.execution_sequence seq, e.created_at,
           e.analysis_run_id, m.attempt_number, m.failure_class, m.tool_name,
           req.id req_id, req.package_hash, req.prompt_hash,
           req.analysis_package_id, req.analysis_run_id req_run, req.channel_id req_channel,
           p.analysis_run_id pkg_run, p.channel_id pkg_channel, p.payload_hash pkg_hash,
           ch.id channel_id, ch.label,
           v.passed, v.total_evidence_refs tot, v.unresolved_evidence_refs unres,
           v.causal_violations cv, v.ctr_violations ctr,
           v.unsupported_metric_violations umv,
           v.structural_issues, v.evidence_issues, v.claim_issues, v.quality_issues,
           res.payload, res.payload_hash res_hash
    FROM llm_execution e
    JOIN cursor_execution_manifest m ON m.llm_execution_id = e.id
    JOIN cursor_analysis_request req ON req.id = m.request_id
    JOIN analysis_package p ON p.id = req.analysis_package_id
    JOIN channel ch ON ch.id = req.channel_id
    LEFT JOIN analysis_validation v ON v.llm_execution_id = e.id
    LEFT JOIN cursor_analysis_result res ON res.llm_execution_id = e.id
    WHERE ch.label = $1 AND e.created_at >= $2
    ORDER BY e.created_at DESC LIMIT 1
  `, [label, SINCE])

  if (!r.rows.length) { fail(`không có lần chạy nào sau ${SINCE.toISOString()}`); continue }
  const x = r.rows[0]

  console.log(`   exec=${x.exec_id.slice(0,8)} seq=${x.seq} attempt=${x.attempt_number} status=${x.status}`)
  console.log(`   gói=${x.package_hash.slice(0,12)} prompt=${x.prompt_hash.slice(0,12)}`)

  // --- lineage: gói phải thuộc đúng lần chạy và đúng kênh của yêu cầu ---
  if (x.req_run !== x.pkg_run) fail(`lineage: run yêu cầu ${x.req_run} != run của gói ${x.pkg_run}`)
  else ok('lineage: gói thuộc đúng lần phân tích')
  if (x.req_channel !== x.pkg_channel) fail(`lineage: kênh yêu cầu != kênh của gói`)
  else ok('lineage: gói thuộc đúng kênh')
  if (x.package_hash !== x.pkg_hash) fail(`băm gói lưu ở yêu cầu (${x.package_hash.slice(0,12)}) != băm thật của gói (${x.pkg_hash.slice(0,12)})`)
  else ok('băm gói khớp với gói thật')

  // --- kiểm định ---
  if (x.passed !== true) fail(`validation.passed = ${x.passed}`)
  else ok('kiểm định: ĐẠT')
  if (Number(x.unres) !== 0) fail(`bằng chứng chưa giải: ${x.unres}`)
  else ok(`bằng chứng: ${x.tot}/${x.tot} giải được (100%)`)
  for (const [name, n] of [['nhân quả', x.cv], ['CTR', x.ctr], ['chỉ số bịa', x.umv]]) {
    if (Number(n) !== 0) fail(`vi phạm ${name}: ${n}`); else ok(`vi phạm ${name}: 0`)
  }

  // --- KHÔNG còn BLOCKER/HIGH ở bất kỳ nhóm nào ---
  const all = [...(x.structural_issues||[]), ...(x.evidence_issues||[]),
               ...(x.claim_issues||[]), ...(x.quality_issues||[])]
  const bad = all.filter(i => i.severity === 'BLOCKER' || i.severity === 'HIGH')
  if (bad.length) { fail(`còn ${bad.length} lỗi BLOCKER/HIGH:`); bad.forEach(i => console.log(`        [${i.severity}] ${i.rule}: ${i.message}`)) }
  else ok(`không còn BLOCKER/HIGH (tổng ${all.length} lỗi mức thấp)`)

  // --- vòng tròn / tự trích trong payload thật ---
  const pl = x.payload
  if (!pl) { fail('không có payload kết quả'); continue }
  const pkgPrefixes = /^(OBS|ANOM|VIDEO|BASE|COHORT|HYP)-/
  const internal = new Map()
  for (const f of pl.keyFindings) internal.set(f.id, f.evidenceIds)
  for (const h of pl.hypotheses) internal.set(h.id, h.supportingEvidenceIds)
  const grounded = (id, seen) => {
    if (pkgPrefixes.test(id)) return true
    if (seen.has(id)) return false
    seen.add(id)
    const refs = internal.get(id)
    return refs ? refs.some(rr => rr !== id && grounded(rr, seen)) : false
  }
  let circ = 0, self = 0
  for (const [id, refs] of internal) {
    if (refs.includes(id)) self++
    else if (refs.length && !refs.some(rr => grounded(rr, new Set([id])))) circ++
  }
  if (self) fail(`tự trích chính nó: ${self}`); else ok('không có mục tự trích chính nó')
  if (circ) fail(`chỉ trích dẫn nội bộ, không neo về gói: ${circ}`); else ok('mọi mục đều neo về bằng chứng của gói')

  // --- nội dung: có thực chất không ---
  console.log(`   nội dung: ${pl.keyFindings.length} phát hiện, ${pl.hypotheses.length} giả thuyết, ` +
              `${pl.recommendations.length} khuyến nghị, ${pl.experiments.length} thí nghiệm`)
  console.log(`   tin cậy: ${pl.analysisSummary.confidence}`)
  if (!pl.hypotheses.every(h => h.status === 'UNVERIFIED')) fail('có giả thuyết không ở trạng thái UNVERIFIED')
  else ok('mọi giả thuyết đều UNVERIFIED')

  // --- output trên đĩa có ĐƯỢC GHI LẠI không (chống stale) ---
  const path = `../../analysis_out/${label}.cursor.json`
  try {
    const st = statSync(new URL(path, import.meta.url))
    const disk = JSON.parse(readFileSync(new URL(path, import.meta.url), 'utf8'))
    const fresh = st.mtime >= SINCE
    if (!fresh) fail(`tệp trên đĩa CŨ (mtime ${st.mtime.toISOString()} < ${SINCE.toISOString()})`)
    else ok(`tệp trên đĩa mới (${st.mtime.toISOString()})`)
    // _meta là phần thêm vào khi ghi tệp; payload còn lại phải khớp DB từng byte.
    const { _meta, ...body } = disk
    if (JSON.stringify(body) !== JSON.stringify(pl)) fail('nội dung tệp KHÁC payload trong DB')
    else ok('nội dung tệp khớp payload trong DB')

    if (!_meta) fail('tệp thiếu khối _meta')
    else {
      const checks = [
        ['channelLabel', _meta.channelLabel, label],
        ['packageHash', _meta.packageHash, x.package_hash],
        ['promptHash', _meta.promptHash, x.prompt_hash],
        ['requestId', _meta.requestId, x.req_id],
        ['llmExecutionId', _meta.llmExecutionId, x.exec_id],
      ]
      for (const [k, got, want] of checks) {
        if (got !== want) fail(`_meta.${k} = ${got} nhưng DB có ${want}`)
      }
      if (checks.every(([, g, w]) => g === w)) ok('_meta khớp execution/run/kênh/băm gói trong DB')
      if (!_meta.promptVersion) fail('_meta thiếu promptVersion')
      else ok(`_meta.promptVersion = ${_meta.promptVersion}`)
      if (!_meta.outputSchemaVersion) fail('_meta thiếu outputSchemaVersion')

      // Băm mã nguồn phải khớp bản kê trong DB. Lệch nghĩa là artifact không
      // thuộc lần chạy mà nó tự nhận — hoặc mã nguồn đã đổi giữa chừng.
      for (const [k, col] of [
        ['validatorHash', 'validator_hash'],
        ['schemaHash', 'schema_hash'],
        ['promptSourceHash', 'prompt_source_hash'],
      ]) {
        if (!_meta[k]) { fail(`_meta thiếu ${k}`); continue }
        if (_meta[k] !== x[col]) fail(`_meta.${k} khác bản kê DB (${_meta[k]} vs ${x[col]})`)
      }
      if (_meta.validatorHash && _meta.validatorHash === x.validator_hash) {
        ok(`băm validator/schema/prompt khớp bản kê DB (${String(_meta.validatorHash).slice(0, 12)}…)`)
      }
      if (_meta.outputSchemaVersion !== x.schema_version)
        fail(`_meta.outputSchemaVersion (${_meta.outputSchemaVersion}) khác DB (${x.schema_version})`)

      // Trần 600s + chặn cứng 15s. Vượt nghĩa là timeout không được thực thi.
      const LIMIT = 615_000
      if (typeof _meta.durationMs !== 'number') fail('_meta thiếu durationMs')
      else if (_meta.durationMs > LIMIT)
        fail(`thời gian ${(_meta.durationMs / 1000).toFixed(1)}s VƯỢT trần 600s + 15s`)
      else ok(`thời gian ${(_meta.durationMs / 1000).toFixed(1)}s trong trần 600s + 15s`)
    }
  } catch (e) { fail(`không đọc được ${path}: ${e.message}`) }
}

console.log(`\n${'='.repeat(72)}`)
console.log(failures === 0 ? 'TẤT CẢ KIỂM CHỨNG ĐỀU ĐẠT' : `CÓ ${failures} KIỂM CHỨNG THẤT BẠI`)
await c.end()
process.exit(failures === 0 ? 0 : 1)
