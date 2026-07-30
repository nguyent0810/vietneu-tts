import { writeFileSync, mkdirSync } from 'node:fs'
import { resolve } from 'node:path'

import { config } from 'dotenv'
import { eq, sql } from 'drizzle-orm'

import { getDb, configureWebSocketForNode } from './client'
import * as schema from './schema'
import { runDeterministicAnalysis } from '../lib/analysis/run'
import { stableStringify } from '../lib/analysis/package'

/**
 * Chạy phân tích tất định cho một hoặc tất cả kênh.
 *
 *   npm run analyze -- --all --from 2026-04-28 --to 2026-07-27
 *   npm run analyze -- --channel hinh_su --from 2026-04-28 --to 2026-07-27
 *   npm run analyze -- --all --dry-run          # tính, không ghi
 *   npm run analyze -- --all --out analysis_out # xuất gói ra file JSON
 */
async function main(): Promise<void> {
  config({ path: '.env.local' })
  config({ path: '.env' })
  await configureWebSocketForNode()

  const args = process.argv.slice(2)
  const flag = (name: string): string | undefined => {
    const i = args.indexOf(`--${name}`)
    return i >= 0 ? args[i + 1] : undefined
  }
  const has = (name: string): boolean => args.includes(`--${name}`)

  if (!process.env.DATABASE_URL) {
    console.error('DATABASE_URL chưa đặt.')
    process.exit(2)
  }

  const db = getDb()
  const ws = await db
    .select({ id: schema.workspace.id })
    .from(schema.workspace)
    .where(eq(schema.workspace.slug, 'vietneu'))
    .limit(1)
  if (!ws[0]) {
    console.error('Chưa có workspace "vietneu". Chạy npm run db:seed.')
    process.exit(2)
  }
  const workspaceId = ws[0].id

  const channels = has('all')
    ? (
        await db
          .select({ label: schema.channel.label })
          .from(schema.channel)
          .where(eq(schema.channel.workspaceId, workspaceId))
          .orderBy(schema.channel.label)
      ).map((c) => c.label)
    : [flag('channel')].filter((c): c is string => Boolean(c))

  if (channels.length === 0) {
    console.error('Cần --channel <label> hoặc --all.')
    process.exit(2)
  }

  // Mặc định: toàn bộ dải ngày đã có dữ liệu, để đường cơ sở dày nhất có thể.
  const bounds = await db.execute<{ min: string | null; max: string | null }>(
    sql`SELECT min(date)::text AS min, max(date)::text AS max FROM video_daily_metric`,
  )
  const windowStart = flag('from') ?? bounds.rows[0]?.min ?? '2026-01-01'
  const windowEnd = flag('to') ?? bounds.rows[0]?.max ?? '2026-12-31'
  const dryRun = has('dry-run')
  const outDir = flag('out')

  console.log(`Cửa sổ phân tích: ${windowStart} → ${windowEnd}${dryRun ? '  (DRY RUN)' : ''}\n`)

  let totalRaw = 0
  let totalPackage = 0

  for (const label of channels) {
    const result = await runDeterministicAnalysis({
      workspaceId,
      channelLabel: label,
      windowStart,
      windowEnd,
      dryRun,
    })

    totalRaw += result.rawInputBytes
    totalPackage += result.packageBytes

    const pkg = result.package
    console.log(`▶ ${label}  (${pkg.scope.channelTitle})`)
    console.log(`   video                : ${pkg.dataCoverage.videosTotal} (${pkg.dataCoverage.videosWithMetrics} có chỉ số, ${pkg.dataCoverage.videosImmature} chưa chín)`)
    console.log(`   feature tính được    : ${result.featureCount}   (thiếu có lý do: ${result.missingFeatureCount})`)
    console.log(`   quan sát             : ${result.observationCount}   bất thường: ${result.anomalyCount}`)
    console.log(`   độ tin cậy           : ${pkg.confidence.score} (${pkg.confidence.band})`)
    console.log(
      `   NÉN                  : ${fmtBytes(result.rawInputBytes)} → ${fmtBytes(result.packageBytes)}  ` +
        `giảm ${result.reductionPercent}%`,
    )
    console.log(`   hash gói             : ${result.packageHash.slice(0, 16)}...`)
    if (result.analysisRunId) console.log(`   analysis_run         : ${result.analysisRunId}`)

    const top = pkg.observations.filter((o) => o.polarity === 'POSITIVE').slice(0, 2)
    const bottom = pkg.observations.filter((o) => o.polarity === 'NEGATIVE').slice(0, 2)
    for (const o of [...top, ...bottom]) console.log(`     • ${o.statement}`)
    if (pkg.hypothesisCandidates.length) {
      console.log(`   giả thuyết (chưa kiểm chứng): ${pkg.hypothesisCandidates.length}`)
    }
    if (pkg.missingData.length) {
      for (const m of pkg.missingData.slice(0, 3)) console.log(`     ⚠ ${m}`)
    }
    console.log()

    if (outDir) {
      const dir = resolve(process.cwd(), '..', '..', outDir)
      mkdirSync(dir, { recursive: true })
      writeFileSync(resolve(dir, `${label}.package.json`), stableStringify(pkg), 'utf8')
    }
  }

  const overall = ((totalRaw - totalPackage) / totalRaw) * 100
  console.log('─'.repeat(70))
  console.log(
    `TỔNG: ${fmtBytes(totalRaw)} dữ liệu thô → ${fmtBytes(totalPackage)} gói bằng chứng  ` +
      `(giảm ${overall.toFixed(2)}%)`,
  )
  if (outDir) console.log(`Đã xuất gói JSON vào ${outDir}/`)
}

function fmtBytes(n: number): string {
  if (n < 1024) return `${n} B`
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`
  return `${(n / 1024 / 1024).toFixed(2)} MB`
}

main().catch((err) => {
  console.error('Phân tích thất bại:', err instanceof Error ? err.message : err)
  if (err instanceof Error && err.stack) console.error(err.stack.split('\n').slice(1, 4).join('\n'))
  process.exit(1)
})
