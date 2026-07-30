import { afterAll, describe, expect, it } from 'vitest'
import { Client, Pool, neonConfig } from '@neondatabase/serverless'
import { drizzle } from 'drizzle-orm/neon-serverless'
import { migrate } from 'drizzle-orm/neon-serverless/migrator'
import { sql } from 'drizzle-orm'
import ws from 'ws'

import { hasTestDatabase } from '../helpers/db'

neonConfig.webSocketConstructor = ws

/**
 * AC-5 — chứng minh chuỗi migration chạy SẠCH TỪ DATABASE RỖNG.
 *
 * Vì sao cần file riêng: kiểm tra schema hiện tại (cột nullable, không có FK
 * `video`) chỉ chứng minh KẾT QUẢ, không chứng minh chuỗi migration tự chạy
 * được từ số không. Nếu 0000 tham chiếu một bảng chưa tồn tại thì lỗi chỉ lộ ra
 * đúng ở tình huống này.
 *
 * Test tự tạo một database dùng một lần rồi xoá đi ở cuối, nên không đụng tới
 * database test chung mà các file khác đang dùng.
 */
const SCRATCH_DB = `hub_migrate_probe_${Date.now()}`

function adminUrl(): string {
  const url = process.env.DATABASE_URL
  if (!url) throw new Error('TEST_DATABASE_URL chưa đặt')
  return url
}

function scratchUrl(): string {
  const u = new URL(adminUrl())
  u.pathname = `/${SCRATCH_DB}`
  return u.toString()
}

async function adminExec(statement: string): Promise<void> {
  const c = new Client({ connectionString: adminUrl() })
  await c.connect()
  try {
    await c.query(statement)
  } finally {
    await c.end()
  }
}

describe.skipIf(!hasTestDatabase)('AC-5: migration chạy sạch từ database rỗng', () => {
  afterAll(async () => {
    await adminExec(`DROP DATABASE IF EXISTS ${SCRATCH_DB}`).catch(() => {})
  })

  it('dựng toàn bộ schema từ số không rồi dùng được ngay', async () => {
    await adminExec(`CREATE DATABASE ${SCRATCH_DB}`)

    const pool = new Pool({ connectionString: scratchUrl() })
    try {
      const db = drizzle(pool)

      // Đây là phần thực sự kiểm chứng: chạy đúng chuỗi migration đã commit,
      // theo đúng thứ tự, trên một database chưa có gì.
      await migrate(db, { migrationsFolder: './drizzle' })

      const tables = await db.execute<{ count: string }>(sql`
        SELECT count(*)::text AS count FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
      `)
      expect(Number(tables.rows[0]!.count)).toBeGreaterThanOrEqual(21)

      // Trigger bất biến của 0001 phải tồn tại — nếu 0001 im lặng không chạy
      // thì mọi bảo đảm bất biến biến mất mà không có gì báo.
      const triggers = await db.execute<{ tgname: string }>(sql`
        SELECT tgname FROM pg_trigger WHERE NOT tgisinternal ORDER BY tgname
      `)
      const names = triggers.rows.map((r) => r.tgname)
      expect(names).toContain('content_revision_immutability')
      expect(names).toContain('content_revision_no_delete')
      expect(names).toContain('prompt_revision_immutability')
      expect(names).toContain('audit_event_append_only')
      expect(names).toContain('analysis_result_immutability')

      // AC-5 đúng nghĩa: cột tồn tại, nullable, và CHƯA có FK tới `video`.
      const column = await db.execute<{ is_nullable: string }>(sql`
        SELECT is_nullable FROM information_schema.columns
        WHERE table_name = 'content_item' AND column_name = 'published_video_id'
      `)
      expect(column.rows[0]!.is_nullable).toBe('YES')

      const videoTable = await db.execute<{ count: string }>(sql`
        SELECT count(*)::text AS count FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'video'
      `)
      expect(Number(videoTable.rows[0]!.count)).toBe(0)

      // Chạy lại lần hai phải là no-op, không được lỗi (migration có ghi sổ).
      await migrate(db, { migrationsFolder: './drizzle' })
    } finally {
      await pool.end()
    }
  })
})
