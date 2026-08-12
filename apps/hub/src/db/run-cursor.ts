import { existsSync, mkdirSync, readdirSync, rmSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { config } from 'dotenv'
import { eq } from 'drizzle-orm'

import { getDb, configureWebSocketForNode } from './client'
import * as schema from './schema'
import {
  runCursorAnalysis,
  VALIDATOR_HASH,
  CONTRACT_PROVENANCE,
  SCHEMA_HASH,
  PROMPT_SOURCE_HASH,
} from '../lib/cursor/run'
import {
  buildArtifactFile,
  buildIndexJson,
  missingIdentityFields,
  runIdentity,
  shouldWriteArtifact,
  type RunIdentity,
} from '../lib/cursor/identity'
import { PROMPT_VERSION } from '../lib/cursor/prompt'
import { CURSOR_OUTPUT_SCHEMA_VERSION, type CursorOutput } from '../lib/cursor/schema'

/**
 * Chạy phân tích Cursor cho một hoặc tất cả kênh.
 *
 *   npm run cursor -- --all --sandbox /tmp/cursor_sandbox
 *   npm run cursor -- --channel hinh_su --repeat 3     # đo độ ổn định
 *   npm run cursor -- --all --out analysis_out
 */
async function main(): Promise<void> {
  config({ path: '.env.local' })
  config({ path: '.env' })
  await configureWebSocketForNode()

  const args = process.argv.slice(2)
  const flag = (n: string): string | undefined => {
    const i = args.indexOf(`--${n}`)
    return i >= 0 ? args[i + 1] : undefined
  }
  const has = (n: string): boolean => args.includes(`--${n}`)

  if (!process.env.DATABASE_URL) {
    console.error('DATABASE_URL chưa đặt.')
    process.exit(2)
  }

  const sandbox = flag('sandbox') ?? '/tmp/cursor_sandbox'
  const repeat = Number(flag('repeat') ?? '1')
  /**
   * Đo độ ổn định cần N mẫu THÀNH CÔNG độc lập, không phải N lần thử.
   *
   * `--repeat 3` đếm cả lần hỏng, nên một kênh hỏng 2/3 vẫn "có 3 mẫu" — đó là
   * thiên lệch lấy mẫu. `--successes 3 --max-attempts 6` chạy tới khi đủ 3 lần
   * ĐẠT hoặc chạm trần, và báo rõ tỉ lệ đạt cùng số lần đã thử.
   */
  const wantSuccesses = flag('successes') ? Number(flag('successes')) : null
  const maxAttempts = Number(flag('max-attempts') ?? String((wantSuccesses ?? 1) * 2))
  const outDir = flag('out')
  const model = flag('model')

  const db = getDb()
  const ws = await db
    .select({ id: schema.workspace.id })
    .from(schema.workspace)
    .where(eq(schema.workspace.slug, 'vietneu'))
    .limit(1)
  if (!ws[0]) {
    console.error('Chưa có workspace "vietneu".')
    process.exit(2)
  }

  const labels = has('all')
    ? (
        await db
          .select({ label: schema.channel.label })
          .from(schema.channel)
          .where(eq(schema.channel.workspaceId, ws[0].id))
          .orderBy(schema.channel.label)
      ).map((c) => c.label)
    : [flag('channel')].filter((c): c is string => Boolean(c))

  if (!labels.length) {
    console.error('Cần --channel <label> hoặc --all.')
    process.exit(2)
  }

  /** Thống kê để báo cáo trung thực, kể cả các lần hỏng. */
  const identities: Record<string, RunIdentity[]> = {}
  const tally: Record<
    string,
    { attempts: number; successes: number; timeouts: number; validationFails: number; other: number }
  > = {}

  for (const label of labels) {
    tally[label] = { attempts: 0, successes: 0, timeouts: 0, validationFails: 0, other: 0 }
    identities[label] = []

    // Dọn MỌI biến thể tệp của kênh này trước khi chạy.
    //
    // Ba chế độ ghi ra ba kiểu tên: `x.cursor.json`, `x.cursor.runN.json`,
    // `x.cursor.sN.json`. Chỉ dọn đúng tên của chế độ hiện tại sẽ để lại tệp
    // của chế độ trước — và cái nguy hiểm nhất là `x.cursor.json`, đúng cái tên
    // mà một consumer coi là bản chính thức. Nó thuộc gói CŨ mà trông vẫn mới.
    if (outDir) {
      const dir = resolveOutDir(outDir)
      if (existsSync(dir)) {
        for (const f of readdirSync(dir)) {
          if (f.startsWith(`${label}.cursor`) && f.endsWith('.json')) {
            rmSync(resolve(dir, f))
          }
        }
      }
    }
    const totalPlanned = wantSuccesses ? maxAttempts : repeat
    for (let run = 1; run <= totalPlanned; run++) {
      if (wantSuccesses && tally[label]!.successes >= wantSuccesses) break
      const started = Date.now()
      const r = await runCursorAnalysis({
        workspaceId: ws[0].id,
        channelLabel: label,
        sandboxDir: sandbox,
        model,
        dryRun: has('dry-run'),
      })

      const ident = runIdentity(r)
      const missingIds = missingIdentityFields(ident)
      if (missingIds.length) {
        // Không im lặng: một lần chạy ĐẠT mà thiếu id nghĩa là INDEX.json không
        // lần ngược được về database, và đó là hỏng cổng nguồn gốc chứ không
        // phải một ô trống vô hại.
        console.log(`   ⚠ THIẾU DANH TÍNH: ${missingIds.join(', ')}`)
      }
      identities[label]!.push(ident)

      const t = tally[label]!
      t.attempts++
      if (r.status === 'SUCCEEDED') t.successes++
      else if (r.attempts.some((a) => a.timedOut)) t.timeouts++
      else if (r.status === 'REJECTED_SCHEMA') t.validationFails++
      else t.other++

      const tag = wantSuccesses
        ? ` [mẫu ${t.successes}/${wantSuccesses}, lần thử ${t.attempts}/${maxAttempts}]`
        : repeat > 1
          ? ` [lần ${run}/${repeat}]` : ''
      console.log(`\n▶ ${label}${tag}  —  ${r.status}`)
      console.log(`   gói           : ${r.packageHash.slice(0, 12)}…`)
      console.log(`   prompt        : ${(r.promptBytes / 1024).toFixed(1)} KB  hash ${r.promptHash.slice(0, 12)}…`)
      console.log(`   số lần thử    : ${r.attempts.length}  (chốt ở lần ${r.finalAttempt ?? '—'})`)
      console.log(`   thời gian     : ${((Date.now() - started) / 1000).toFixed(1)}s`)

      for (const a of r.attempts) {
        console.log(
          `     lần ${a.attemptNumber}: ${a.passed ? 'ĐẠT' : a.failureClass}` +
            `  ${(a.durationMs / 1000).toFixed(1)}s  stdout=${(a.stdoutBytes / 1024).toFixed(1)}KB` +
            (a.repairErrors.length ? `  lỗi=${a.repairErrors.length}` : ''),
        )
        for (const e of a.repairErrors.slice(0, 3)) console.log(`        - ${e}`)
      }

      if (r.report) {
        const rep = r.report
        console.log(
          `   kiểm định     : bằng chứng ${rep.totalEvidenceRefs - rep.unresolvedEvidenceRefs}/${rep.totalEvidenceRefs}` +
            ` (${rep.evidenceResolutionRate === null ? '—' : (rep.evidenceResolutionRate * 100).toFixed(1) + '%'})` +
            `  nhân quả=${rep.causalViolations}  CTR=${rep.ctrViolations}  chỉ số lạ=${rep.unsupportedMetricViolations}`,
        )
        console.log(
          `   nội dung      : ${rep.counts.findings} phát hiện, ${rep.counts.hypotheses} giả thuyết, ` +
            `${rep.counts.recommendations} khuyến nghị, ${rep.counts.experiments} thí nghiệm`,
        )
        const q = rep.qualityIssues.length
        if (q) console.log(`   cảnh báo chất lượng: ${q}`)
      }

      /*
       * GHI ARTIFACT chỉ khi lần chạy ĐƯỢC CẤP PHÉP.
       *
       * `r.output` KHÔNG đủ để kết luận "đạt": ba nhánh THẤT BẠI cũng gán
       * `result.output = analysisPass.value` để giữ văn xuôi làm bằng chứng —
       * cạn ngân sách khai báo, hỏng bộ sinh nghĩa vụ, và chế độ dryRun.
       *
       * Hậu quả nếu chỉ xét `r.output`, và nó GHI ĐÈ chứ không chỉ thêm rác:
       * hậu tố tệp là `.s${successes}`, mà `successes` chỉ tăng khi ĐẠT. Nên một
       * lần chạy hỏng ghi đúng vào ô của MẪU ĐẠT GẦN NHẤT, thay một hiện vật đã
       * được cấp phép bằng một payload chỉ có văn xuôi — trong khi database vẫn
       * đếm mẫu ấy là hợp lệ. Cổng in "ĐỦ 3 MẪU" với một tệp chưa từng được cấp phép.
       */
      const authorized = shouldWriteArtifact(r)

      if (r.output) {
        const s = r.output.analysisSummary
        console.log(`   tin cậy       : ${s.confidence}`)
        console.log(`   ràng buộc chính: ${s.primaryConstraint.slice(0, 100)}`)
        const conf = r.output.keyFindings.reduce<Record<string, number>>((acc, f) => {
          acc[f.confidence] = (acc[f.confidence] ?? 0) + 1
          return acc
        }, {})
        console.log(`   phân bố tin cậy phát hiện: ${JSON.stringify(conf)}`)

        if (outDir && authorized) {
          const dir = resolveOutDir(outDir)
          mkdirSync(dir, { recursive: true })
          const suffix = wantSuccesses
            ? `.s${tally[label]!.successes}`
            : repeat > 1 ? `.run${run}` : ''
          // Kèm NGUỒN GỐC vào chính tệp: đọc tệp mà không biết nó thuộc gói nào,
          // lần chạy nào thì không thể phát hiện một tệp cũ còn sót lại.
          // NGUỒN GỐC chép từ BẢN GHI DÙNG CHUNG, không tự thu thập lại.
          //
          // Trước đây mỗi bề mặt tự gom nguồn gốc của riêng nó, nên chúng lệch
          // nhau mà không ai thấy. Nay artifact, INDEX.json và bản kê đều chép
          // từ `CONTRACT_PROVENANCE`, và phép so giữa chúng mới có nghĩa.
          //
          // Phép GHÉP nằm trong `buildArtifactFile`, không viết tại chỗ: bản
          // trước viết `{ _meta: ..., ...r.output }` và vì `r.output` mang
          // `_meta` riêng, spread ghi đè ngược lại, xoá sạch phần bổ sung lúc
          // ghi tệp. Tệp vẫn đúng schema nên không có gì kêu.
          const withMeta = buildArtifactFile(
            r.output as unknown as Record<string, unknown>,
            r,
            CONTRACT_PROVENANCE,
            {
              channelLabel: label,
              durationMs: Date.now() - started,
              outputSchemaVersion: r.output.schemaVersion,
              writtenAt: new Date().toISOString(),
            },
          )
          writeFileSync(
            resolve(dir, `${label}.cursor${suffix}.json`),
            JSON.stringify(withMeta, null, 2),
            'utf8',
          )
        }
      }

      if (outDir && !authorized) {
        // THẤT BẠI: xoá tệp cũ thay vì để nguyên.
        //
        // Để nguyên nghĩa là lần chạy sau đọc tệp đó sẽ thấy kết quả của một gói
        // CŨ và tưởng là mới. Vắng mặt là trung thực; một tệp cũ đội lốt tệp mới
        // thì không. Đây đúng là loại lỗi "thành công giả" mà cả tầng này sinh
        // ra để chặn.
        const dir = resolveOutDir(outDir)
        const suffix = wantSuccesses
          ? `.s${tally[label]!.successes + 1}`
          : repeat > 1 ? `.run${run}` : ''
        const stale = resolve(dir, `${label}.cursor${suffix}.json`)
        if (existsSync(stale)) {
          rmSync(stale)
          console.log(`   đã xoá tệp cũ (lần chạy này thất bại): ${stale}`)
        }
      }
    }
  }

  // Chỉ mục TUYÊN BỐ tập tệp chính thức của lần gọi này.
  //
  // Không có nó, consumer phải tự đoán tệp nào là bản hiện hành; có nó thì mọi
  // tệp không nằm trong danh sách đều là thừa và phát hiện được ngay.
  if (outDir) {
    const dir = resolveOutDir(outDir)
    mkdirSync(dir, { recursive: true })
    writeFileSync(
      resolve(dir, 'INDEX.json'),
      JSON.stringify(
        // Toàn bộ khối do `buildIndexJson` dựng — nguồn gốc, tally VÀ danh tính.
        //
        // Trước đây tally và danh tính được viết ngay tại đây, ngoài tầm với của
        // mọi test: một thay đổi làm rơi `identities` hoặc đếm sót lần thất bại
        // sẽ không làm đỏ bất cứ thứ gì.
        buildIndexJson({
          contract: CONTRACT_PROVENANCE,
          generatedAt: new Date().toISOString(),
          schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
          mode: wantSuccesses ? `successes=${wantSuccesses}` : `repeat=${repeat}`,
          tally,
          identities,
          filesFor: (label) =>
            existsSync(dir)
              ? readdirSync(dir).filter(
                  (f) => f.startsWith(`${label}.cursor`) && f.endsWith('.json'),
                )
              : [],
        }),
        null,
        2,
      ),
      'utf8',
    )
  }

  printTally(tally, wantSuccesses)
}

/**
 * Giải đường dẫn --out theo THƯ MỤC HIỆN TẠI, như mọi CLI khác.
 *
 * Bản trước dùng `resolve(process.cwd(), '..', '..', outDir)`, tức mặc định
 * "cwd là apps/hub VÀ outDir tính từ gốc repo". Chạy từ apps/hub với
 * `--out ../../analysis_out` thì hai giả định cộng lại thành
 * `<repo>/../../analysis_out` — tệp được ghi RA NGOÀI repo, lặng lẽ, trong khi
 * `analysis_out/` trong repo vẫn giữ kết quả cũ và trông như vừa được cập nhật.
 * Đúng loại "artifact cũ đội lốt mới" mà cả vòng kiểm này sinh ra để bắt.
 */
export function resolveOutDir(outDir: string): string {
  return resolve(process.cwd(), outDir)
}

function printTally(
  tally: Record<string, { attempts: number; successes: number; timeouts: number; validationFails: number; other: number }>,
  wantSuccesses: number | null,
): void {
  console.log(`\n${'='.repeat(64)}\nTỔNG KẾT (kể cả các lần hỏng)\n${'='.repeat(64)}`)
  for (const [label, t] of Object.entries(tally)) {
    const rate = t.attempts ? ((t.successes / t.attempts) * 100).toFixed(0) : '0'
    console.log(
      `${label.padEnd(12)} đạt ${t.successes}/${t.attempts} (${rate}%)  ` +
        `timeout=${t.timeouts}  kiểm định hỏng=${t.validationFails}  khác=${t.other}`,
    )
    if (wantSuccesses && t.successes < wantSuccesses) {
      console.log(`             ✗ KHÔNG đủ ${wantSuccesses} mẫu hợp lệ -> cổng ĐO ỔN ĐỊNH THẤT BẠI`)
    }
  }
}

// Chỉ chạy khi được gọi TRỰC TIẾP.
//
// Không có guard này, chỉ cần `import` module để test một hàm thuần cũng kích
// hoạt cả CLI: kết nối database, chạy Cursor, rồi `process.exit` giữa chừng
// test runner.
const isDirectRun =
  process.argv[1] !== undefined && process.argv[1].includes('run-cursor')

if (isDirectRun) {
  main().catch((err) => {
    console.error('Phân tích Cursor thất bại:', err instanceof Error ? err.message : err)
    if (err instanceof Error && err.stack) console.error(err.stack.split('\n').slice(1, 4).join('\n'))
    process.exit(1)
  })
}
