import { config } from 'dotenv'
import { eq, sql } from 'drizzle-orm'

import { getDb, configureWebSocketForNode } from './client'
import * as schema from './schema'
import type { CursorOutput } from '../lib/cursor/schema'

/**
 * Đo ĐỘ ỔN ĐỊNH của phân tích Cursor.
 *
 * So sánh nhiều lần chạy trên CÙNG gói + CÙNG phiên bản prompt.
 *
 * Không đòi văn bản giống hệt — LLM không tất định và ép nó tất định cũng
 * không phải mục tiêu. Cái phải ổn định là KẾT LUẬN CỐT LÕI: cùng nhóm chủ đề
 * phát hiện, cùng hạng ưu tiên khuyến nghị, cùng tập bằng chứng được trích, và
 * mức tin cậy không nhảy loạn.
 *
 *   npm run cursor:stability -- --channel phat_giao
 */
interface RunRow {
  executionSequence: number
  payload: CursorOutput
  createdAt: string
}

/** Jaccard: phần giao trên phần hợp. 1 = trùng khớp, 0 = rời nhau. */
function jaccard(a: Set<string>, b: Set<string>): number {
  if (a.size === 0 && b.size === 0) return 1
  const inter = [...a].filter((x) => b.has(x)).length
  const union = new Set([...a, ...b]).size
  return union === 0 ? 1 : inter / union
}

/** Từ khoá nội dung của một câu — bỏ từ nối để so chủ đề, không so câu chữ. */
function topicTokens(text: string): Set<string> {
  const stop = new Set([
    'và','của','có','là','trong','với','cho','các','những','một','này','đó','khi','thì','mà','ở','từ',
    'the','and','of','in','to','for','a','an','is','are','with','on','at','by','from','that','this',
  ])
  return new Set(
    text
      .toLowerCase()
      .replace(/[^\p{L}\p{N}_\s-]/gu, ' ')
      .split(/\s+/)
      .filter((w) => w.length > 2 && !stop.has(w)),
  )
}

function summarize(runs: RunRow[]): void {
  console.log(`\nSố lần chạy so sánh: ${runs.length}`)

  // --- Phần TẤT ĐỊNH: phải giống hệt, khác là lỗi hệ thống chứ không phải
  // dao động của mô hình. Nhóm này đã được chọn theo cùng packageHash +
  // promptHash, nên mọi khác biệt dưới đây đều đáng báo động.
  const det = runs.map((r) => ({
    schema: r.payload.schemaVersion,
    // Ràng buộc cứng của tầng này: mọi giả thuyết phải ở trạng thái UNVERIFIED.
    allUnverified: r.payload.hypotheses.every((h) => h.status === 'UNVERIFIED'),
  }))
  const detStable =
    new Set(det.map((d) => d.schema)).size === 1 && det.every((d) => d.allUnverified)
  console.log(
    `\n[TẤT ĐỊNH] phiên bản schema + ràng buộc UNVERIFIED: ${detStable ? 'GIỐNG NHAU ✓' : 'KHÁC NHAU ✗'}`,
  )
  console.log('[MÔ HÌNH]  phần dưới đây được PHÉP dao động — đo mức độ, không đòi giống hệt:')

  for (const r of runs) {
    const p = r.payload
    console.log(
      `  #${r.executionSequence}: ${p.keyFindings.length} phát hiện, ${p.hypotheses.length} giả thuyết, ` +
        `${p.recommendations.length} khuyến nghị, ${p.experiments.length} thí nghiệm, ` +
        `tin cậy ${p.analysisSummary.confidence}`,
    )
  }

  // --- Độ ổn định của mức tin cậy tổng thể ---
  const confidences = runs.map((r) => r.payload.analysisSummary.confidence)
  const sameConfidence = new Set(confidences).size === 1
  console.log(`\nTin cậy tổng thể: ${confidences.join(', ')}  -> ${sameConfidence ? 'ỔN ĐỊNH' : 'DAO ĐỘNG'}`)

  // --- Trùng lặp bằng chứng được trích ---
  const evidenceSets = runs.map(
    (r) =>
      new Set([
        ...r.payload.keyFindings.flatMap((f) => f.evidenceIds),
        ...r.payload.hypotheses.flatMap((h) => h.supportingEvidenceIds),
        ...r.payload.recommendations.flatMap((x) => x.evidenceIds),
      ]),
  )
  const evidencePairs: number[] = []
  for (let i = 0; i < evidenceSets.length; i++) {
    for (let j = i + 1; j < evidenceSets.length; j++) {
      evidencePairs.push(jaccard(evidenceSets[i]!, evidenceSets[j]!))
    }
  }
  const avg = (xs: number[]) => (xs.length ? xs.reduce((s, x) => s + x, 0) / xs.length : 1)
  console.log(`Trùng lặp bằng chứng (Jaccard TB): ${(avg(evidencePairs) * 100).toFixed(1)}%`)

  // --- Trùng lặp CHỦ ĐỀ của phát hiện ---
  const findingTopics = runs.map(
    (r) => new Set(r.payload.keyFindings.flatMap((f) => [...topicTokens(f.statement)])),
  )
  const findingPairs: number[] = []
  for (let i = 0; i < findingTopics.length; i++) {
    for (let j = i + 1; j < findingTopics.length; j++) {
      findingPairs.push(jaccard(findingTopics[i]!, findingTopics[j]!))
    }
  }
  console.log(`Trùng lặp chủ đề phát hiện (Jaccard TB): ${(avg(findingPairs) * 100).toFixed(1)}%`)

  // --- Trùng lặp phân loại khuyến nghị ---
  const recCats = runs.map((r) => new Set(r.payload.recommendations.map((x) => `${x.category}:${x.priority}`)))
  const recPairs: number[] = []
  for (let i = 0; i < recCats.length; i++) {
    for (let j = i + 1; j < recCats.length; j++) recPairs.push(jaccard(recCats[i]!, recCats[j]!))
  }
  console.log(`Trùng lặp (loại,ưu tiên) khuyến nghị: ${(avg(recPairs) * 100).toFixed(1)}%`)

  // --- Ràng buộc chính có nhất quán không ---
  const constraints = runs.map((r) => r.payload.analysisSummary.primaryConstraint.toLowerCase())
  const allMentionCtr = constraints.every((c) => /impression|ctr/.test(c))
  console.log(
    `Ràng buộc chính đều nêu thiếu impressions/CTR: ${allMentionCtr ? 'CÓ' : 'KHÔNG'}`,
  )

  // --- Mâu thuẫn: cùng một chủ đề nhưng cực trái ngược ---
  const posNeg = runs.map((r) => ({
    seq: r.executionSequence,
    p0: r.payload.recommendations.filter((x) => x.priority === 'P0').length,
    stop: r.payload.recommendations.filter((x) => x.category === 'STOP').length,
    cont: r.payload.recommendations.filter((x) => x.category === 'CONTINUE').length,
  }))
  console.log('\nHướng hành động theo lần chạy:')
  for (const x of posNeg) console.log(`  #${x.seq}: P0=${x.p0}  STOP=${x.stop}  CONTINUE=${x.cont}`)
  const contradictory = posNeg.some((a) => posNeg.some((b) => a.stop > 0 && b.stop === 0 && b.cont > 0 && a.cont === 0))
  console.log(`Mâu thuẫn hướng hành động: ${contradictory ? 'CÓ — cần xem lại' : 'KHÔNG'}`)
}

async function main(): Promise<void> {
  config({ path: '.env.local' })
  config({ path: '.env' })
  await configureWebSocketForNode()

  const args = process.argv.slice(2)
  const idx = args.indexOf('--channel')
  const label = idx >= 0 ? args[idx + 1] : undefined
  if (!label) {
    console.error('Cần --channel <label>')
    process.exit(2)
  }

  const db = getDb()

  // MỌI lần chạy, kể cả lần hỏng.
  //
  // Bản trước xuất phát từ `cursor_analysis_result`. Lần hỏng không có dòng kết
  // quả, nên chúng biến mất khỏi cả số mẫu lẫn mọi chỉ số. Hệ quả: 100 lần thử
  // với 2 lần đạt giống nhau và 98 lần hỏng sẽ được báo là "2 lần chạy" và gần
  // 100% ổn định — kênh trông ổn định CHÍNH VÌ chỉ những kẻ sống sót hiếm hoi
  // được đem ra so. Đó là thiên lệch lấy mẫu, và nó che đúng thứ cần thấy.
  const all = await db.execute<{
    status: string
    failure_class: string
    timed_out: boolean
    created_at: string
  }>(sql`
    SELECT e.status, m.failure_class, m.timed_out, e.created_at::text
    FROM llm_execution e
    JOIN cursor_execution_manifest m ON m.llm_execution_id = e.id
    JOIN cursor_analysis_request req ON req.id = m.request_id
    JOIN channel c ON c.id = req.channel_id
    WHERE c.label = ${label} AND e.provider = 'CURSOR_CLI'
    ORDER BY e.created_at
  `)

  const attempts = all.rows.length
  const succeeded = all.rows.filter((r) => r.status === 'SUCCEEDED').length
  const timeouts = all.rows.filter((r) => r.timed_out).length
  const rejected = all.rows.filter((r) => r.status === 'REJECTED_SCHEMA').length
  console.log('='.repeat(70))
  console.log(`Kênh ${label} — TOÀN BỘ lần chạy (không loại lần hỏng)`)
  console.log('='.repeat(70))
  console.log(`  tổng số lần chạy : ${attempts}`)
  console.log(
    `  đạt              : ${succeeded} (${attempts ? ((succeeded / attempts) * 100).toFixed(0) : 0}%)`,
  )
  console.log(`  kiểm định từ chối: ${rejected}`)
  console.log(`  timeout          : ${timeouts}`)
  const byClass = new Map<string, number>()
  for (const r of all.rows) {
    if (r.status === 'SUCCEEDED') continue
    byClass.set(r.failure_class, (byClass.get(r.failure_class) ?? 0) + 1)
  }
  if (byClass.size) {
    console.log('  lý do hỏng       :')
    for (const [k, v] of [...byClass].sort((a, b) => b[1] - a[1])) {
      console.log(`      ${k}: ${v}`)
    }
  }

  // FAIL-CLOSED: chỉ lấy kết quả có KIỂM ĐỊNH ĐẠT, đúng schema 2.0, và kèm
  // toàn bộ băm phiên bản để phát hiện lô trộn bản.
  //
  // Bản trước chọn MỌI dòng kết quả, không lọc schema cũng không lọc kiểm định.
  // Một dòng schema-1 ghi thẳng vào DB, hoặc một kết quả có kiểm định KHÔNG đạt,
  // đều lọt vào quần thể "đã đạt" và làm sai mọi con số ổn định.
  const rows = await db.execute<{
    execution_sequence: number
    payload: CursorOutput
    created_at: string
    package_hash: string
    prompt_hash: string
    schema_version: string
    prompt_version: string
    validator_hash: string
    schema_hash: string
    prompt_source_hash: string
  }>(sql`
    SELECT e.execution_sequence, r.payload, r.created_at::text,
           req.package_hash, req.prompt_hash,
           m.schema_version, m.prompt_version, m.validator_hash, m.schema_hash,
           m.prompt_source_hash
    FROM cursor_analysis_result r
    JOIN llm_execution e ON e.id = r.llm_execution_id
    JOIN cursor_execution_manifest m ON m.llm_execution_id = e.id
    JOIN analysis_validation v ON v.llm_execution_id = e.id
    JOIN cursor_analysis_request req ON req.id = r.request_id
    JOIN channel c ON c.id = r.channel_id
    WHERE c.label = ${label}
      AND v.passed = true
      AND e.status = 'SUCCEEDED'
      AND r.schema_version = m.schema_version
      AND r.payload->>'schemaVersion' = r.schema_version
    ORDER BY r.created_at
  `)

  // Một lô CHỈ so sánh được khi mọi mẫu dùng CÙNG bộ phiên bản.
  const versionKeys = new Set(
    rows.rows.map(
      (r) =>
        `${r.schema_version}|${r.prompt_version}|${r.validator_hash}|${r.schema_hash}|${r.prompt_source_hash}`,
    ),
  )
  if (versionKeys.size > 1) {
    console.log(
      `\n  ✗ LÔ TRỘN PHIÊN BẢN: ${versionKeys.size} bộ băm khác nhau trong số mẫu đạt.\n` +
        `    So sánh ổn định KHÔNG có ý nghĩa — cần chạy lại một lô đồng nhất.`,
    )
  }

  console.log(
    `\n  Các chỉ số ổn định dưới đây chỉ tính trên ${rows.rows.length} lần ĐẠT.\n` +
      `  Chúng KHÔNG nói gì về ${attempts - succeeded} lần hỏng ở trên — đọc kèm tỉ lệ đạt.`,
  )

  if (rows.rows.length < 2) {
    console.log(
      `Chỉ có ${rows.rows.length} kết quả cho "${label}". Cần ít nhất 2 lần chạy để so sánh.\n` +
        `Chạy: npm run cursor -- --channel ${label} --repeat 3`,
    )
    return
  }

  // Chỉ so các lần chạy CÙNG gói + CÙNG prompt; khác đầu vào thì so sánh vô nghĩa.
  const groups = new Map<string, typeof rows.rows>()
  for (const r of rows.rows) {
    const key = `${r.package_hash}|${r.prompt_hash}`
    groups.set(key, [...(groups.get(key) ?? []), r])
  }

  for (const [key, group] of groups) {
    if (group.length < 2) continue
    const [pkgHash, promptHash] = key.split('|')
    console.log('='.repeat(70))
    console.log(`Kênh ${label} — gói ${pkgHash!.slice(0, 12)}… prompt ${promptHash!.slice(0, 12)}…`)
    console.log('='.repeat(70))
    summarize(
      group.map((r) => ({
        executionSequence: r.execution_sequence,
        payload: r.payload,
        createdAt: r.created_at,
      })),
    )
  }
}

main().catch((err) => {
  console.error('Đo độ ổn định thất bại:', err instanceof Error ? err.message : err)
  process.exit(1)
})
