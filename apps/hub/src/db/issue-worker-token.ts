import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { config } from 'dotenv'
import { Pool } from '@neondatabase/serverless'
import { drizzle } from 'drizzle-orm/neon-serverless'
import { eq } from 'drizzle-orm'

import { configureWebSocketForNode } from './client'
import * as schema from './schema'
import { generateToken } from '../lib/auth'

const REPO_ROOT = resolve(import.meta.dirname, '../../../..')
const TOKEN_FILE = resolve(REPO_ROOT, '.youtube_hub.env')

/**
 * Ghi token vào file env đã gitignore, giữ nguyên các khoá khác nếu file đã có.
 * chmod 600 ngay khi ghi để không tồn tại cửa sổ nào file readable rộng hơn.
 */
function writeTokenFile(label: string, token: string): void {
  const existing = existsSync(TOKEN_FILE) ? readFileSync(TOKEN_FILE, 'utf8') : ''
  const kept = existing
    .split('\n')
    .filter((line) => !/^HUB_WORKER_TOKEN=/.test(line) && !/^HUB_WORKER_LABEL=/.test(line))
    .join('\n')
    .trimEnd()

  const header = kept
    ? kept
    : [
        '# Sinh bởi `npm run worker:token`. ĐÃ GITIGNORE — không commit.',
        '# Token worker chỉ tồn tại ở đây và dưới dạng sha256 trong database.',
        '# Base URL của backend Content Hub (mặc định http://127.0.0.1:3000).',
        '# HUB_API_BASE=http://127.0.0.1:3000',
      ].join('\n')

  writeFileSync(
    TOKEN_FILE,
    `${header}\n\nHUB_WORKER_LABEL=${label}\nHUB_WORKER_TOKEN=${token}\n`,
    { mode: 0o600 },
  )
}

/**
 * Cấp token cho một máy worker.
 *
 * Token gốc chỉ tồn tại MỘT LẦN ở đây rồi không lấy lại được: database chỉ lưu
 * sha256. Mất token thì cấp lại cái mới — đó chính là mục đích.
 *
 *   npm run worker:token -- --label mac-mini
 *
 * Token được GHI THẲNG vào <repo>/.youtube_hub.env (đã gitignore, chmod 600).
 * TUYỆT ĐỐI KHÔNG in ra stdout: stdout đi vào log terminal, log CI và transcript
 * của agent — tức là credential sống bị sao chép ra những nơi không ai dọn.
 * Chỉ in tiền tố để đối chiếu.
 */
async function main(): Promise<void> {
  config({ path: '.env.local' })
  config({ path: '.env' })

  const args = process.argv.slice(2)
  const labelIndex = args.indexOf('--label')
  const label = labelIndex >= 0 ? args[labelIndex + 1] : undefined
  if (!label) {
    console.error('Thiếu --label <tên máy>')
    process.exit(2)
  }

  const workspaceSlug = 'vietneu'
  if (!process.env.DATABASE_URL) {
    console.error('DATABASE_URL chưa đặt.')
    process.exit(2)
  }

  await configureWebSocketForNode()
  const pool = new Pool({ connectionString: process.env.DATABASE_URL })

  try {
    const db = drizzle(pool, { schema, casing: 'snake_case' })

    const ws = await db
      .select({ id: schema.workspace.id })
      .from(schema.workspace)
      .where(eq(schema.workspace.slug, workspaceSlug))
      .limit(1)
    if (!ws[0]) {
      console.error(`Chưa có workspace "${workspaceSlug}". Chạy npm run db:seed trước.`)
      process.exit(2)
    }

    const { token, hash, prefix } = generateToken('WORKER')

    await db
      .insert(schema.workerMachine)
      .values({
        workspaceId: ws[0].id,
        machineLabel: label,
        tokenHash: hash,
        tokenPrefix: prefix,
        capabilities: ['SYNC_ANALYTICS', 'RUN_LLM_ANALYSIS', 'ANALYZE_CONTENT'],
      })
      .onConflictDoUpdate({
        target: [schema.workerMachine.workspaceId, schema.workerMachine.machineLabel],
        // Cấp lại token cho cùng một máy sẽ THU HỒI token cũ (hash bị ghi đè).
        set: { tokenHash: hash, tokenPrefix: prefix, revokedAt: null },
      })

    writeTokenFile(label, token)

    console.log(`\nĐã cấp token cho máy "${label}".`)
    console.log(`Ghi vào: ${TOKEN_FILE} (chmod 600, đã gitignore)`)
    console.log(`Tiền tố để đối chiếu: ${prefix}...`)
    console.log('Token cũ của máy này (nếu có) đã bị thu hồi.')
  } finally {
    await pool.end()
  }
}

main().catch((err) => {
  console.error('Cấp token thất bại:', err instanceof Error ? err.message : err)
  process.exit(1)
})
