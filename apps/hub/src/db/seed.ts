import { readFileSync, readdirSync } from 'node:fs'
import { resolve } from 'node:path'

import { config } from 'dotenv'
import { Pool } from '@neondatabase/serverless'
import { drizzle } from 'drizzle-orm/neon-serverless'
import { eq, sql } from 'drizzle-orm'

import { configureWebSocketForNode } from './client'
import * as schema from './schema'

/**
 * Seed dữ liệu nền: 1 workspace, 3 kênh, thuật toán + phiên bản sentinel, và
 * bộ chiều điểm rubric của Phase 5.
 *
 * Idempotent: chạy lại nhiều lần không tạo bản trùng.
 */

const REPO_ROOT = resolve(import.meta.dirname, '../../../..')
const CHANNELS_DIR = resolve(REPO_ROOT, '.youtube_channels')

const WORKSPACE_SLUG = 'vietneu'

/**
 * Đọc DANH TÍNH kênh từ .youtube_channels/{label}.json.
 *
 * CHỈ lấy channel_label / channel_id / channel_title — ba trường công khai.
 * client_id, client_secret và refresh_token trong cùng file đó KHÔNG BAO GIỜ
 * được đọc vào đây và không bao giờ đi vào database: content database không
 * phải nơi chứa credential.
 */
function readChannelIdentities(): Array<{ label: string; youtubeChannelId: string; title: string }> {
  let files: string[]
  try {
    files = readdirSync(CHANNELS_DIR).filter((f) => f.endsWith('.json'))
  } catch {
    throw new Error(
      `Không đọc được ${CHANNELS_DIR}. Chạy bootstrap YouTube trước (xem youtube_auth.py).`,
    )
  }

  return files.map((file) => {
    const raw = JSON.parse(readFileSync(resolve(CHANNELS_DIR, file), 'utf8')) as Record<string, unknown>
    const label = String(raw.channel_label ?? '')
    const youtubeChannelId = String(raw.channel_id ?? '')
    const title = String(raw.channel_title ?? '')
    if (!label || !youtubeChannelId) {
      throw new Error(`${file} thiếu channel_label hoặc channel_id.`)
    }
    return { label, youtubeChannelId, title }
  })
}

/** 8 chiều rubric bắt buộc của Phase 5 để so sánh kết quả Cursor giữa các vòng. */
const ANALYSIS_RUBRIC = [
  ['factual_grounding', 'Bám dữ liệu thật', 'Mọi khẳng định truy được về số liệu đã thu thập.'],
  ['evidence_coverage', 'Độ phủ bằng chứng', 'Dùng hết bằng chứng sẵn có, không bỏ sót tín hiệu quan trọng.'],
  ['internal_consistency', 'Nhất quán nội tại', 'Các kết luận không mâu thuẫn nhau.'],
  ['actionability', 'Tính hành động được', 'Khuyến nghị đủ cụ thể để thực thi.'],
  ['uncertainty_calibration', 'Hiệu chỉnh độ chắc chắn', 'Mức tự tin tương xứng với chất lượng bằng chứng.'],
  ['channel_relevance', 'Sát với kênh', 'Bám đặc thù kênh, không phải lời khuyên chung chung.'],
  ['no_invented_metrics', 'Không bịa chỉ số', 'Không có chỉ số nào không tồn tại trong dữ liệu nguồn.'],
  ['schema_adherence', 'Tuân thủ schema', 'Output khớp đúng JSON schema đã quy định.'],
] as const

async function main(): Promise<void> {
  config({ path: '.env.local' })
  config({ path: '.env' })

  if (!process.env.DATABASE_URL) {
    console.error('DATABASE_URL chưa đặt.')
    process.exit(2)
  }

  await configureWebSocketForNode()
  const pool = new Pool({ connectionString: process.env.DATABASE_URL })

  try {
    const db = drizzle(pool, { schema, casing: 'snake_case' })

    // --- workspace ---
    const [ws] = await db
      .insert(schema.workspace)
      .values({ slug: WORKSPACE_SLUG, name: 'VieNeu Content Hub' })
      .onConflictDoUpdate({
        target: schema.workspace.slug,
        set: { name: 'VieNeu Content Hub', updatedAt: new Date() },
      })
      .returning()
    const workspaceId = ws!.id
    console.log(`workspace: ${WORKSPACE_SLUG}`)

    // --- 3 kênh ---
    const identities = readChannelIdentities()
    for (const ch of identities) {
      await db
        .insert(schema.channel)
        .values({ workspaceId, label: ch.label, youtubeChannelId: ch.youtubeChannelId, title: ch.title })
        .onConflictDoUpdate({
          target: schema.channel.youtubeChannelId,
          set: { title: ch.title, label: ch.label, updatedAt: new Date() },
        })
      console.log(`kênh: ${ch.label} (${ch.title})`)
    }

    // --- thuật toán ---
    const algorithms = [
      { key: 'deterministic-analysis', name: 'Phân tích tất định', kind: 'DETERMINISTIC' as const },
      { key: 'cursor-llm-analysis', name: 'Phân tích LLM qua Cursor CLI', kind: 'LLM' as const },
      { key: 'codex-critique', name: 'Phê bình bằng Codex CLI', kind: 'LLM' as const },
      { key: 'analysis-rubric', name: 'Rubric chấm kết quả phân tích', kind: 'DETERMINISTIC' as const },
      // AC-3: sentinel cho audit/analysis do người hoặc công cụ ngoài chạy.
      // Tồn tại để `algorithm_version_id` không bao giờ phải nullable — NULL
      // trong ràng buộc UNIQUE sẽ không chặn được trùng `run_sequence`.
      { key: 'external-human', name: 'Người/công cụ ngoài (sentinel)', kind: 'EXTERNAL' as const },
    ]

    for (const a of algorithms) {
      const [row] = await db
        .insert(schema.algorithm)
        .values(a)
        .onConflictDoUpdate({ target: schema.algorithm.key, set: { name: a.name } })
        .returning()

      await db
        .insert(schema.algorithmVersion)
        .values({ algorithmId: row!.id, version: '1.0.0' })
        .onConflictDoNothing()
      console.log(`thuật toán: ${a.key} v1.0.0`)
    }

    // --- chiều điểm rubric ---
    for (const [index, [key, label, description]] of ANALYSIS_RUBRIC.entries()) {
      await db
        .insert(schema.scoreDimension)
        .values({
          dimensionSet: 'ANALYSIS_RUBRIC',
          key,
          label,
          description,
          scaleMin: '0',
          scaleMax: '5',
          weight: '1',
          sortOrder: index,
        })
        .onConflictDoUpdate({
          target: [schema.scoreDimension.dimensionSet, schema.scoreDimension.key],
          set: { label, description, sortOrder: index },
        })
    }
    console.log(`chiều điểm rubric: ${ANALYSIS_RUBRIC.length}`)

    const counts = await db.execute<{ channels: string; algorithms: string; dimensions: string }>(sql`
      SELECT
        (SELECT count(*) FROM channel WHERE workspace_id = ${workspaceId}) AS channels,
        (SELECT count(*) FROM algorithm) AS algorithms,
        (SELECT count(*) FROM score_dimension WHERE dimension_set = 'ANALYSIS_RUBRIC') AS dimensions
    `)
    console.log('\nTổng kết:', counts.rows[0])
  } finally {
    await pool.end()
  }
}

main().catch((err) => {
  console.error('Seed thất bại:', err instanceof Error ? err.message : err)
  process.exit(1)
})
