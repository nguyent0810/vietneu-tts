/**
 * Kiểm chứng Phase 4 — KHÔNG tin vào trạng thái, chỉ tin vào dữ liệu.
 *
 * Trạng thái SUCCEEDED là thứ dễ sai nhất: chính lỗi Codex #4 cho thấy một lần
 * chạy mang 3 lỗi HIGH vẫn được ghi SUCCEEDED và trông y hệt một lần đạt thật.
 * Vì vậy script này kiểm lại từ dữ liệu thô, không đọc cột status.
 */
import { config } from 'dotenv'
import { Client, neonConfig } from '@neondatabase/serverless'
import { createHash } from 'node:crypto'
import { readdirSync, readFileSync, statSync } from 'node:fs'
import { pathToFileURL } from 'node:url'
import ws from 'ws'

neonConfig.webSocketConstructor = ws
config({ path: '.env.local' })

const SINCE = process.argv[2] ? new Date(process.argv[2]) : new Date(Date.now() - 3600_000)

/*
 * BA THAM SỐ MÔI TRƯỜNG — chỉ để KIỂM ĐƯỢC chính cổng này (H-2).
 *
 * Trước đây script ghim cứng `DATABASE_URL` và `../../analysis_out/`, nên không
 * có cách nào chạy nó trên dữ liệu dựng sẵn. Hệ quả đúng như mục 10 của handoff
 * cảnh báo: bản viết lại cho hợp đồng hai lượt được KHẲNG ĐỊNH là hoạt động mà
 * chưa từng chạy qua một hiện vật thật nào.
 *
 * Mặc định GIỮ NGUYÊN hành vi cũ từng chữ. Không có biến nào được đặt thì đây
 * vẫn là đúng script mà lô chính thức chạy.
 */
const DB_URL = process.env.VERIFY_DATABASE_URL || process.env.DATABASE_URL
const CHANNELS = process.env.VERIFY_CHANNELS
  ? process.env.VERIFY_CHANNELS.split(',').map((s) => s.trim()).filter(Boolean)
  : ['phat_giao', 'hinh_su', 'phong_thuy']

const c = new Client({ connectionString: DB_URL })
await c.connect()

let failures = 0
const fail = (m) => { console.log(`   ✗ ${m}`); failures++ }
const ok = (m) => console.log(`   ✓ ${m}`)

/**
 * Dạng CHUẨN TẮC của một giá trị JSON: khoá object sắp xếp, mảng giữ nguyên.
 *
 * Dùng để so thân hiện vật trên đĩa với `payload` lấy từ `jsonb`. Thứ tự khoá
 * KHÔNG mang thông tin trong JSON, và `jsonb` chủ động sắp lại — nên so thô là
 * so nhầm thứ.
 */
/**
 * Chuỗi dùng để BĂM LẠI payload đã lưu.
 *
 * Dùng chính `canon` (khoá đã sắp xếp) để phép băm không phụ thuộc thứ tự khoá
 * của `jsonb` — cùng lý do như phép so thân.
 */
const canonBytes = (v) => canon(v)

const canon = (v) => {
  if (Array.isArray(v)) return `[${v.map(canon).join(',')}]`
  if (v && typeof v === 'object') {
    return `{${Object.keys(v).sort().map((k) => `${JSON.stringify(k)}:${canon(v[k])}`).join(',')}}`
  }
  return JSON.stringify(v)
}

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
           v.unsupported_metric_violations umv, v.stage terminal_stage,
           v.structural_issues, v.evidence_issues, v.claim_issues, v.quality_issues,
           res.payload, res.payload_hash res_hash
    FROM llm_execution e
    JOIN cursor_execution_manifest m ON m.llm_execution_id = e.id
    JOIN cursor_analysis_request req ON req.id = m.request_id
    JOIN analysis_package p ON p.id = req.analysis_package_id
    JOIN channel ch ON ch.id = req.channel_id
    -- CHẶNG KẾT THÚC, chọn TẤT ĐỊNH.
    --
    -- Không có mệnh đề "stage" thì một execution vai DECLARATION khớp HAI hàng
    -- kiểm định (DECLARATION và COMPOSITE) có cùng "created_at", và "LIMIT 1"
    -- lấy hàng nào là do thứ tự vật lý quyết định. Khi hàng DECLARATION thắng,
    -- mọi phép kiểm bên dưới đọc phán quyết của SAI CHẶNG: "passed" của lượt
    -- khai báo, bộ đếm 0/0/0 của nó, và mảng vi phạm rỗng của nó — che sạch
    -- BLOCKER/HIGH của chặng hợp nhất. Đúng loại lỗi mà tệp này được viết ra để
    -- bắt, nhưng ở chính bộ máy đi bắt.
    --
    -- "ORDER BY av.stage DESC" đúng vì enum "validation_stage" xếp theo thứ tự
    -- đường ống: ANALYSIS < DECLARATION < COMPOSITE.
    LEFT JOIN LATERAL (
      SELECT av.passed, av.total_evidence_refs, av.unresolved_evidence_refs,
             av.causal_violations, av.ctr_violations, av.unsupported_metric_violations,
             av.structural_issues, av.evidence_issues, av.claim_issues, av.quality_issues,
             av.stage
        FROM analysis_validation av
       WHERE av.llm_execution_id = e.id
       ORDER BY av.stage DESC
       LIMIT 1
    ) v ON true
    -- CHỈ hiện vật CHÍNH THỨC: hàng vai ANALYSIS là văn xuôi đã đóng băng, và
    -- coi nó là kết quả sẽ làm một lần chạy KHÔNG có hiện vật nào trông như đạt.
    LEFT JOIN cursor_analysis_result res
      ON res.llm_execution_id = e.id AND res.result_role = 'COMPOSITE'
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
  // Chặng kết thúc phải là HỢP NHẤT. Một lần chạy dừng ở ANALYSIS/DECLARATION
  // KHÔNG có hiện vật chính thức, và "đạt ở chặng giữa" không phải là đạt.
  if (x.terminal_stage !== 'COMPOSITE') {
    fail(`chặng kiểm định cuối là ${x.terminal_stage} — lần chạy KHÔNG tới chặng hợp nhất`)
  } else ok('chặng kiểm định cuối: COMPOSITE')
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

}

/* =========================================================================
 * PHẦN HAI — ARTIFACT của kiến trúc HAI LƯỢT
 *
 * Viết lại hoàn toàn. Bản trước kiểm theo hợp đồng MỘT LƯỢT và ĐỎ ở mọi lô lành
 * mạnh vì bốn lý do độc lập: đọc `{label}.cursor.json` trong khi lô ổn định ghi
 * `.s1/.s2/.s3`; so `_meta` với các cột bản kê mà câu SELECT không hề lấy; so
 * thân tệp với `payload` trong DB vốn CÓ mang `_meta`; và không neo vào danh
 * tính nào. Một cổng luôn đỏ bị bỏ qua, và khi ấy một lệch THẬT cũng chìm theo.
 *
 * Nay: lấy INDEX.json làm nguồn TUYÊN BỐ tập tệp chính thức, rồi với mỗi danh
 * tính trong đó, đối chiếu tệp trên đĩa với ĐÚNG các hàng database mà danh tính
 * ấy chỉ tới. "Không tìm thấy gì" LUÔN là thất bại, không bao giờ là đạt.
 * ====================================================================== */

const OUT_DIR = process.env.VERIFY_OUT_DIR
  ? pathToFileURL(process.env.VERIFY_OUT_DIR.replace(/\/?$/, '/'))
  : new URL('../../analysis_out/', import.meta.url)
const idxUrl = new URL('INDEX.json', OUT_DIR)

console.log(`\n${'='.repeat(72)}\nARTIFACT (hai lượt)\n${'='.repeat(72)}`)

let idx = null
try {
  idx = JSON.parse(readFileSync(idxUrl, 'utf8'))
  ok('đọc được INDEX.json')
} catch (e) {
  fail(`không đọc được INDEX.json: ${e.message}`)
}

if (idx) {
  const channels = Object.entries(idx.channels ?? {})
  if (!channels.length) fail('INDEX.json không tuyên bố kênh nào — không có gì để đối chiếu')

  /*
   * MỌI kênh được KỲ VỌNG phải có mặt trong INDEX.json.
   *
   * PHẦN HAI chỉ lặp trên `idx.channels`, nên một kênh nằm trong danh sách kỳ
   * vọng mà KHÔNG có mục trong chỉ mục thì không bị đối chiếu gì cả — nó lặng lẽ
   * biến khỏi tầm nhìn. Phép quét hiện vật mồ côi cũng không cứu được: nếu tệp
   * của kênh ấy đã bị xoá thì không còn gì trên đĩa để mà mồ côi.
   *
   * Hệ quả: một lô CHỈ chạy được một kênh vẫn qua cổng đóng băng, trong khi lô
   * chính thức đòi ba kênh. "Không thấy gì" LUÔN là thất bại.
   */
  const declaredChannelKeys = new Set(channels.map(([k]) => k))
  for (const expected of CHANNELS) {
    if (!declaredChannelKeys.has(expected)) {
      fail(`INDEX.json KHÔNG tuyên bố kênh "${expected}" — kênh được kỳ vọng nhưng không có hiện vật nào`)
    }
  }

  for (const [label, info] of channels) {
    console.log(`\n-- ${label} --`)
    const identities = info.identities ?? []
    if (!identities.length) { fail(`${label}: INDEX.json không có danh tính nào`); continue }

    const authorized = identities.filter((d) => d.status === 'SUCCEEDED' && d.resultId)
    const files = info.files ?? []
    if (files.length !== authorized.length) {
      fail(`${label}: ${files.length} tệp nhưng ${authorized.length} lần chạy được cấp phép`)
    }

    /*
     * BẢNG ĐẾM của chính INDEX phải khớp số danh tính được cấp phép.
     *
     * `channels[label]` mang sẵn `{attempts, successes, ...}` do `run-cursor.ts`
     * ghi, nhưng cổng này trước đó chỉ đọc `identities` và `files`. Xoá một cặp
     * (một danh tính + tệp của nó) làm CẢ HAI cùng co lại, nên phép so
     * `files.length !== authorized.length` vẫn xanh — trong khi `successes` vẫn
     * ghi con số CŨ và tự tố cáo việc cắt bớt.
     *
     * Đây KHÔNG phải phép kiểm đầy đủ cho việc cắt mẫu — bảng đếm cũng sửa được
     * — nên nó đi CÙNG phép đối chiếu DATABASE → INDEX ở cuối tệp. Ở đây chỉ
     * đóng phiên bản rẻ tiền: xoá tệp mà quên sửa số.
     */
    if (Number(info.successes) !== authorized.length) {
      fail(
        `${label}: INDEX.successes = ${info.successes} nhưng chỉ có ${authorized.length} ` +
          `danh tính được cấp phép — chỉ mục tự mâu thuẫn`,
      )
    }

    /*
     * KHÔNG có lần chạy nào được cấp phép = THẤT BẠI.
     *
     * `run-cursor.ts` đẩy một danh tính cho MỌI lần chạy, kể cả lần hỏng, nên
     * `identities` khác rỗng không nói lên điều gì. Khi mọi lần đều hỏng thì
     * `authorized` rỗng, `files` rỗng, phép so `0 !== 0` là false, vòng lặp
     * không chạy lần nào — và cả kênh đi qua mà KHÔNG một dòng ✗ hay ✓ nào.
     * Đúng thứ mà tiêu đề mục này cấm: "không thấy gì" LUÔN là thất bại.
     */
    if (!authorized.length) {
      fail(`${label}: KHÔNG có lần chạy nào được cấp phép — không có hiện vật để đối chiếu`)
      continue
    }

    /*
     * GHÉP theo `resultId`, KHÔNG theo vị trí.
     *
     * `files` đến từ `readdirSync`, vốn KHÔNG sắp xếp: thứ tự là do hệ tệp băm
     * tên quyết định (APFS, ext4+dir_index). `authorized` thì theo thứ tự chạy.
     * Ghép `files[n]` với `authorized[n]` nghĩa là cổng ĐỎ trên một lô hoàn toàn
     * lành mạnh ngay khi hệ tệp trả về thứ tự khác — và XANH khi nó tình cờ trả
     * đúng thứ tự. Một cổng chập chờn còn tệ hơn một cổng luôn đỏ.
     *
     * `_meta.resultId` đã có sẵn trong tệp và là khoá thật của phép ghép này.
     */
    /*
     * MỘT-ĐỔI-MỘT giữa danh tính và tệp.
     *
     * Ghép theo `resultId` chưa đủ: nếu INDEX khai HAI danh tính cùng một
     * `resultId`, vòng lặp tra cùng một tệp HAI LẦN, còn tệp thứ hai — vẫn được
     * INDEX tuyên bố nên thoát cả phép quét mồ côi — KHÔNG bao giờ được kiểm.
     * Số lượng khớp nhau, mọi phép kiểm đều xanh, và một mẫu chưa từng được đối
     * chiếu vẫn nằm trong lô.
     */
    const seenResultIds = new Set()
    for (const id of authorized) {
      if (seenResultIds.has(id.resultId)) {
        fail(`${label}: INDEX khai TRÙNG resultId ${id.resultId} — hai mẫu trỏ cùng một hàng kết quả`)
      }
      seenResultIds.add(id.resultId)
    }

    const byResultId = new Map()
    for (const fname of files) {
      if (fname.includes('/') || fname.includes('\\') || fname.includes('..')) {
        fail(`${label}: tên tệp "${fname}" không phải tên trần trong thư mục hiện vật`)
        continue
      }
      let disk
      try {
        disk = JSON.parse(readFileSync(new URL(fname, OUT_DIR), 'utf8'))
      } catch (e) { fail(`${label}/${fname}: không đọc được (${e.message})`); continue }
      const rid = disk?._meta?.resultId
      if (!rid) { fail(`${label}/${fname}: _meta thiếu resultId — không ghép được về database`); continue }
      if (byResultId.has(rid)) { fail(`${label}: hai tệp cùng khai resultId ${rid}`); continue }
      byResultId.set(rid, fname)
    }

    const consumedFiles = new Set()
    for (const [n, id] of authorized.entries()) {
      const fname = byResultId.get(id.resultId)
      if (!fname) { fail(`${label}: thiếu tệp cho mẫu ${n + 1} (resultId ${id.resultId})`); continue }
      consumedFiles.add(fname)
      // Tên tệp đã được kiểm THOÁT THƯ MỤC ở vòng ghép phía trên: mọi `fname` tới
      // được đây đều đến từ `byResultId`, nên một tên độc hại không bao giờ lọt
      // xuống đây. Không lặp lại phép kiểm — một nhánh không bao giờ chạy chỉ tạo
      // cảm giác có hai lớp bảo vệ trong khi chỉ có một.
      // Hợp đồng tên tệp của lô ổn định. Tên CŨ một lượt không được coi là hợp lệ.
      if (!/\.cursor\.s\d+\.json$/.test(fname) && !/\.cursor\.run\d+\.json$/.test(fname)) {
        fail(`${label}: tên tệp "${fname}" không theo hợp đồng .sN/.runN của lô ổn định`)
        continue
      }

      let disk
      try {
        disk = JSON.parse(readFileSync(new URL(fname, OUT_DIR), 'utf8'))
      } catch (e) { fail(`${label}/${fname}: không đọc được (${e.message})`); continue }

      const meta = disk._meta
      if (!meta) { fail(`${label}/${fname}: thiếu khối _meta`); continue }

      // 1. DANH TÍNH: mọi id trong tệp phải TRA RA hàng database có thật.
      const rows = await c.query(`
        SELECT r.id result_id, r.payload, r.payload_hash, r.schema_version,
               r.analysis_payload_hash, r.obligation_set_hash,
               m.llm_execution_id, m.analysis_execution_id, m.validator_hash,
               m.schema_hash, m.prompt_source_hash, m.declaration_prompt_source_hash,
               m.obligation_generator_version, m.composite_validator_version,
               -- NĂM băm mà migration 0035 thêm vào bản kê. Không đọc chúng ở đây
               -- thì 0035 chỉ GHI nguồn gốc mà không ai ĐỐI CHIẾU: một hiện vật
               -- khai sensitiveLexiconHash khác hẳn hàng bản kê nó tự nhận là
               -- xuất thân vẫn qua cổng.
               m.obligation_generator_hash, m.composite_source_hash,
               m.sensitive_lexicon_hash, m.identity_source_hash, m.provenance_source_hash,
               req.id req_id, req.package_hash, req.prompt_hash, req.analysis_run_id,
               req.channel_id result_channel_id, ch2.label result_channel_label,
               v.id composite_validation_id, v.passed
          FROM cursor_analysis_result r
          JOIN cursor_execution_manifest m ON m.llm_execution_id = r.llm_execution_id
          JOIN cursor_analysis_request req ON req.id = m.request_id
          JOIN channel ch2 ON ch2.id = req.channel_id
          -- CỬA SỔ THỜI GIAN: hàng kết quả phải thuộc lần chạy ĐANG XÉT.
          --
          -- Không có ràng buộc này thì "INDEX.json" chỉ cần trỏ tới một hàng
          -- COMPOSITE hợp lệ nhưng CŨ của cùng kênh, rồi ghi lại tệp hiện vật cho
          -- mtime mới, là qua cổng: phép tra database chỉ ràng buộc "r.id", còn
          -- phép chống-cũ chỉ nhìn mtime của TỆP. Hai nửa cùng xanh trong khi
          -- lineage database và hiện vật thuộc hai lần chạy khác nhau.
          JOIN llm_execution e2
            ON e2.id = r.llm_execution_id AND e2.created_at >= $2
          JOIN analysis_validation v
            ON v.llm_execution_id = r.llm_execution_id AND v.stage = 'COMPOSITE'
         WHERE r.id = $1 AND r.result_role = 'COMPOSITE'`, [id.resultId, SINCE])

      if (!rows.rows.length) {
        fail(
          `${label}/${fname}: resultId ${id.resultId} KHÔNG có hàng kết quả chính thức nào ` +
            `trong cửa sổ đang xét (từ ${SINCE.toISOString()})`,
        )
        continue
      }
      const x = rows.rows[0]

      /*
       * KÊNH phải khớp — hiện vật nằm DƯỚI khoá kênh nào trong INDEX.json thì
       * hàng kết quả của nó phải thuộc đúng kênh ấy.
       *
       * Không có phép kiểm này thì một cặp (danh tính, hiện vật) HỢP LỆ của kênh
       * `phat_giao` — băm thật, `_meta` thật, lineage thật — chép nguyên sang
       * dưới khoá `hinh_su` sẽ qua TOÀN BỘ cổng: mọi trường trong `bind` đều đối
       * chiếu hàng DB của CHÍNH NÓ và đều khớp. Cổng đóng băng chứng nhận một
       * mẫu cho kênh chưa từng sinh ra nó.
       */
      if (x.result_channel_label !== label) {
        fail(
          `${label}/${fname}: hiện vật nằm dưới kênh "${label}" nhưng hàng kết quả ` +
            `thuộc kênh "${x.result_channel_label}" — tráo hiện vật giữa các kênh`,
        )
      } else ok(`${label}/${fname}: hiện vật thuộc đúng kênh`)

      /*
       * DANH TÍNH TRONG INDEX cũng phải khớp database.
       *
       * `authorized` chỉ dùng `status` và `resultId`; phép tra database cũng chỉ
       * dùng `resultId`; và toàn bộ `bind` so `_meta` TRÊN ĐĨA với DB. Không có
       * dòng nào so DANH TÍNH TRONG INDEX với bất cứ thứ gì — nên một chỉ mục
       * khai `analysisExecutionId`/`requestId`/băm của một lần chạy KHÁC vẫn qua
       * cổng, dù chính chỉ mục ấy là thứ người ta đọc để lần ngược.
       */
      const indexBind = [
        ['analysisExecutionId', id.analysisExecutionId, x.analysis_execution_id],
        ['declarationExecutionId', id.declarationExecutionId, x.llm_execution_id],
        ['llmExecutionId', id.llmExecutionId, x.llm_execution_id],
        ['compositeValidationId', id.compositeValidationId, x.composite_validation_id],
        ['requestId', id.requestId, x.req_id],
        ['analysisRunId', id.analysisRunId, x.analysis_run_id],
        ['channelId', id.channelId, x.result_channel_id],
        ['analysisPayloadHash', id.analysisPayloadHash, x.analysis_payload_hash],
        ['obligationSetHash', id.obligationSetHash, x.obligation_set_hash],
      ]
      let indexOk = true
      for (const [k, got, want] of indexBind) {
        if (got === undefined || got === null) {
          fail(`${label}/${fname}: INDEX.identities thiếu ${k}`)
          indexOk = false
        } else if (got !== want) {
          fail(`${label}/${fname}: INDEX.identities.${k} = ${got} nhưng DB có ${want}`)
          indexOk = false
        }
      }
      if (indexOk) ok(`${label}/${fname}: ${indexBind.length} trường danh tính của INDEX khớp DB`)

      const bind = [
        ['resultId', meta.resultId, x.result_id],
        ['channelId', meta.channelId, x.result_channel_id],
        ['channelLabel', meta.channelLabel, x.result_channel_label],
        ['llmExecutionId', meta.llmExecutionId, x.llm_execution_id],
        ['declarationExecutionId', meta.declarationExecutionId, x.llm_execution_id],
        ['analysisExecutionId', meta.analysisExecutionId, x.analysis_execution_id],
        ['compositeValidationId', meta.compositeValidationId, x.composite_validation_id],
        ['requestId', meta.requestId, x.req_id],
        ['analysisRunId', meta.analysisRunId, x.analysis_run_id],
        ['packageHash', meta.packageHash, x.package_hash],
        ['promptHash', meta.promptHash, x.prompt_hash],
        ['analysisPayloadHash', meta.analysisPayloadHash, x.analysis_payload_hash],
        ['obligationSetHash', meta.obligationSetHash, x.obligation_set_hash],
        ['validatorHash', meta.validatorHash, x.validator_hash],
        ['schemaHash', meta.schemaHash, x.schema_hash],
        ['promptSourceHash', meta.promptSourceHash, x.prompt_source_hash],
        ['declarationPromptSourceHash', meta.declarationPromptSourceHash, x.declaration_prompt_source_hash],
        ['obligationGeneratorVersion', meta.obligationGeneratorVersion, x.obligation_generator_version],
        ['compositeValidatorVersion', meta.compositeValidatorVersion, x.composite_validator_version],
        ['outputSchemaVersion', meta.outputSchemaVersion, x.schema_version],
        // 0035 — BĂM MÃ NGUỒN của năm mô-đun quyết định nghĩa của lô.
        //
        // Bump SỐ PHIÊN BẢN là quy ước thủ công, không gì cưỡng chế; sửa nội dung
        // `sensitive.ts` giữa hai kênh mà quên bump thì `obligationGeneratorVersion`
        // vẫn khớp trong khi ĐỊNH NGHĨA "ô nhạy cảm" đã đổi. Chỉ băm nguồn bắt
        // được, và trước bản này không phép kiểm nào đọc tới chúng.
        ['obligationGeneratorHash', meta.obligationGeneratorHash, x.obligation_generator_hash],
        ['compositeSourceHash', meta.compositeSourceHash, x.composite_source_hash],
        ['sensitiveLexiconHash', meta.sensitiveLexiconHash, x.sensitive_lexicon_hash],
        ['identitySourceHash', meta.identitySourceHash, x.identity_source_hash],
        ['provenanceSourceHash', meta.provenanceSourceHash, x.provenance_source_hash],
      ]
      /*
       * SENTINEL bị tính là THIẾU, không phải là giá trị.
       *
       * `hashSource()` và `git()` trả về chuỗi 'unavailable' khi không đọc được,
       * và chuỗi ấy đi thẳng vào CONTRACT_PROVENANCE rồi được chép y hệt sang
       * bản kê, sang _meta của hiện vật và sang INDEX.json. Phép so bằng nhau
       * vẫn XANH: ba bề mặt khớp nhau hoàn hảo, và cả ba cùng không biết gì.
       * `checkProvenanceCoverage` đã coi đây là THIẾU từ vòng G8, nhưng cổng này
       * thì chưa — nên một lô chạy từ một checkout không đọc được mã nguồn vẫn
       * in "18 trường danh tính/băm khớp DB".
       */
      const SENTINELS = new Set(['unavailable', '', 'unknown'])
      let bound = true
      for (const [k, got, want] of bind) {
        if (got === undefined || got === null) { fail(`${label}/${fname}: _meta thiếu ${k}`); bound = false; continue }
        if (typeof got === 'string' && SENTINELS.has(got)) {
          fail(`${label}/${fname}: _meta.${k} = "${got}" là giá trị SENTINEL — nguồn gốc không đọc được, không phải đã khớp`)
          bound = false
          continue
        }
        if (got !== want) { fail(`${label}/${fname}: _meta.${k} = ${got} nhưng DB có ${want}`); bound = false }
      }
      if (bound) ok(`${label}/${fname}: ${bind.length} trường danh tính/băm khớp DB`)

      if (x.passed !== true) fail(`${label}/${fname}: phán quyết COMPOSITE KHÔNG đạt`)

      /*
       * BĂM payload — cột `payload_hash` trước đây được SELECT rồi bỏ không.
       *
       * Phép so thân (bước 2) chứng minh tệp trên đĩa khớp `payload` trong DB,
       * nhưng KHÔNG chứng minh cái nào trong hai khớp con số mà đường ống đã cam
       * kết. Băm bắt được một hàng bị sửa payload mà quên sửa băm, và ngược lại.
       *
       * GIỚI HẠN, nói thẳng: `payload` đã được driver `JSON.parse` TRƯỚC khi tới
       * đây, nên một số nguyên vượt ngoài dải an toàn của IEEE-754
       * (9007199254740993 -> ...992) đã bị làm tròn từ trước. Băm lại giá trị ĐÃ
       * giải mã KHÔNG khôi phục và KHÔNG kiểm được byte gốc. Muốn thế phải đọc
       * `payload::text` thẳng từ Postgres. Đây là ranh giới đã biết, không phải
       * điều phép kiểm này tuyên bố bao phủ.
       */
      const reHash = createHash('sha256').update(canonBytes(x.payload), 'utf8').digest('hex')
      if (x.payload_hash !== reHash) {
        fail(
          `${label}/${fname}: băm payload đã lưu (${String(x.payload_hash).slice(0, 12)}…) ` +
            `khác băm tính lại từ chính payload (${reHash.slice(0, 12)}…)`,
        )
      } else ok(`${label}/${fname}: băm payload khớp payload đã lưu`)

      // 2. THÂN payload. `payload` trong DB CÓ mang `_meta`, nên phải gỡ ở CẢ HAI
      //    phía trước khi so — nếu không thì mọi lần chạy đúng đều báo lệch.
      //
      //    So bằng dạng CHUẨN TẮC, không bằng `JSON.stringify` thô: PostgreSQL
      //    lưu `jsonb`, và `jsonb` KHÔNG giữ thứ tự khoá — nó sắp lại theo độ dài
      //    rồi theo byte. Tệp trên đĩa giữ thứ tự lúc ghi. Nên phép so thô ĐỎ ở
      //    MỌI lô lành mạnh, và một cổng luôn đỏ thì bị bỏ qua — đúng lúc một
      //    lệch THẬT xuất hiện thì nó cũng chìm theo.
      //
      //    Mảng GIỮ NGUYÊN thứ tự: ở đó thứ tự có nghĩa.
      const { _meta: _diskMeta, ...diskBody } = disk
      const { _meta: _dbMeta, ...dbBody } = x.payload
      if (canon(diskBody) !== canon(dbBody)) {
        fail(`${label}/${fname}: thân tệp KHÁC payload trong DB`)
      } else ok(`${label}/${fname}: thân tệp khớp payload DB (dạng chuẩn tắc)`)

      // 3. `_meta` đã lưu trong DB phải khớp `_meta` trên đĩa ở phần lineage.
      // Thiếu `_meta` trong payload đã lưu là HỎNG, không phải "bỏ qua vì không có
      // dữ liệu": phép so thân vẫn xanh (gỡ `_meta` khỏi một object không có nó
      // là phép không), nên hàng chính thức mất sạch nguồn gốc mà không ai kêu.
      if (!_dbMeta) {
        fail(`${label}/${fname}: payload trong DB KHÔNG có khối _meta — mất nguồn gốc`)
      } else {
        for (const k of ['analysisExecutionId', 'declarationExecutionId', 'analysisPayloadHash', 'obligationSetHash']) {
          if (_dbMeta[k] !== meta[k]) {
            fail(`${label}/${fname}: _meta.${k} trên đĩa khác _meta đã lưu trong DB`)
          }
        }
      }

      // 4. CHỐNG CŨ: tệp phải được ghi trong cửa sổ đang xét.
      try {
        const st = statSync(new URL(fname, OUT_DIR))
        if (st.mtime < SINCE) fail(`${label}/${fname}: tệp CŨ (mtime ${st.mtime.toISOString()})`)
      } catch (e) { fail(`${label}/${fname}: không stat được (${e.message})`) }
    }

    // Tệp ĐƯỢC INDEX tuyên bố nhưng KHÔNG danh tính nào dùng tới = chưa kiểm.
    for (const f of files) {
      if (!consumedFiles.has(f)) {
        fail(`${label}: tệp "${f}" được INDEX tuyên bố nhưng KHÔNG mẫu nào đối chiếu tới — chưa hề được kiểm`)
      }
    }

    // Tệp trên đĩa KHÔNG được INDEX tuyên bố = hiện vật mồ côi.
    const declared = new Set(files)
    for (const f of readdirSync(OUT_DIR)) {
      if (f.startsWith(`${label}.cursor`) && f.endsWith('.json') && !declared.has(f)) {
        fail(`${label}: tệp "${f}" có trên đĩa nhưng KHÔNG được INDEX.json tuyên bố`)
      }
    }
  }

  /*
   * M-5 — HIỆN VẬT của kênh mà INDEX.json KHÔNG hề nhắc tới.
   *
   * `run-cursor.ts` ghi `INDEX.json` từ `tally`, và `tally` chỉ chứa các kênh
   * của LẦN GỌI NÀY. Chạy lại một kênh (`--channel hinh_su`) ghi đè chỉ mục ba
   * kênh bằng một chỉ mục MỘT kênh — trong khi hiện vật của hai kênh kia vẫn
   * nằm nguyên trên đĩa.
   *
   * Vòng lặp phía trên không bắt được: nó chỉ chạy cho các kênh CÓ TRONG chỉ
   * mục, nên hiện vật của hai kênh kia không được đối chiếu với bất cứ thứ gì —
   * chúng chỉ đơn giản biến khỏi tầm nhìn của cổng, trong khi một consumer đọc
   * thư mục vẫn thấy chúng và vẫn tin.
   *
   * "Không thấy gì" LUÔN là thất bại, không bao giờ là đạt.
   */
  const declaredChannels = new Set(channels.map(([label]) => label))
  for (const f of readdirSync(OUT_DIR)) {
    // Mọi hậu tố, kể cả nhiều đoạn (`.s1.bak.json`): một tệp lạ mang tên kênh
    // vẫn là hiện vật với bất kỳ consumer nào đọc thư mục này.
    const m = /^(.+?)\.cursor(?:\..+)?\.json$/.exec(f)
    if (!m) continue
    if (!declaredChannels.has(m[1])) {
      fail(
        `hiện vật "${f}" thuộc kênh "${m[1]}" mà INDEX.json KHÔNG tuyên bố — ` +
          `chỉ mục có thể đã bị một lần chạy MỘT KÊNH ghi đè`,
      )
    }
  }

  /*
   * CHIỀU NGƯỢC — DATABASE → INDEX. Chống CẮT MẪU.
   *
   * Mọi phép đối chiếu phía trên đều đi MỘT CHIỀU, khởi hành từ `INDEX.json`:
   * danh tính → database (`WHERE r.id = $1`), tệp → danh tính, đĩa → chỉ mục.
   * Không có dòng nào hỏi database xem NÓ có hàng nào mà chỉ mục KHÔNG nhắc.
   *
   * Đường lách vì thế rất rẻ, và nó phá đúng thứ mà cả cổng này sinh ra để bảo
   * vệ — hợp đồng "3 mẫu ỔN ĐỊNH":
   *
   *   1. chạy một kênh 5 lần. `loadPackage` dùng lại gói mới nhất nên cả 5 chung
   *      `analysis_run_id`, nhưng mỗi lần là một lượt PHÂN TÍCH riêng -> tập
   *      nghĩa vụ riêng -> 5 hàng COMPOSITE hợp lệ. `cursor_single_authoritative
   *      _result` khoá theo `analysis_execution_id` nên không phản đối; trần 3
   *      lần của 0031 là trần lượt KHAI BÁO cho MỘT lượt phân tích, không phải
   *      trần số lượt phân tích.
   *   2. giữ 3 hiện vật đẹp nhất, xoá 2 tệp còn lại VÀ mục của chúng trong
   *      `identities` + `files`.
   *   3. `files.length === authorized.length` (3 = 3), không mồ côi, không tệp
   *      thừa, mọi danh tính còn lại đều tra ra hàng thật -> cổng XANH.
   *
   * Tức là "chạy tới khi đẹp rồi chọn" — đúng thứ mà một cổng ổn định tồn tại
   * để cấm — không để lại một vết đỏ nào.
   *
   * Phép kiểm này an toàn với lô LÀNH MẠNH: `persistComposite` chỉ ghi hàng kết
   * quả khi phán quyết ĐẠT (không đạt thì dừng ở bản kiểm định, không có hàng),
   * nên mọi hàng COMPOSITE trong cửa sổ đều là một mẫu được cấp phép và PHẢI có
   * mặt trong chỉ mục.
   */
  const declaredResultIds = new Set()
  for (const [, info] of channels) {
    for (const d of info.identities ?? []) {
      if (d.resultId) declaredResultIds.add(String(d.resultId))
    }
  }
  const scopeLabels = [...new Set([...CHANNELS, ...declaredChannels])]
  const dbRows = await c.query(
    `SELECT r.id result_id, ch.label
       FROM cursor_analysis_result r
       JOIN llm_execution e ON e.id = r.llm_execution_id AND e.created_at >= $1
       JOIN cursor_execution_manifest m ON m.llm_execution_id = r.llm_execution_id
       JOIN cursor_analysis_request req ON req.id = m.request_id
       JOIN channel ch ON ch.id = req.channel_id
      WHERE r.result_role = 'COMPOSITE' AND ch.label = ANY($2::text[])
      ORDER BY ch.label, e.created_at`,
    [SINCE, scopeLabels],
  )
  const undeclared = dbRows.rows.filter((r) => !declaredResultIds.has(String(r.result_id)))
  for (const r of undeclared) {
    fail(
      `kênh "${r.label}": database CÓ hàng kết quả chính thức ${r.result_id} trong cửa sổ ` +
        `nhưng INDEX.json KHÔNG tuyên bố — mẫu đã bị loại khỏi chỉ mục sau khi được cấp phép`,
    )
  }
  if (!undeclared.length) {
    ok(`DB→INDEX: cả ${dbRows.rows.length} hàng COMPOSITE trong cửa sổ đều được chỉ mục tuyên bố`)
  }
}

console.log(`\n${'='.repeat(72)}`)
console.log(failures === 0 ? 'TẤT CẢ KIỂM CHỨNG ĐỀU ĐẠT' : `CÓ ${failures} KIỂM CHỨNG THẤT BẠI`)
await c.end()
process.exit(failures === 0 ? 0 : 1)
