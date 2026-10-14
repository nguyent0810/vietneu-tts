import { afterAll, describe, expect, it } from 'vitest'
import { eq, sql } from 'drizzle-orm'

import { getDb, configureWebSocketForNode } from '@/db/client'
import * as schema from '@/db/schema'
import { runDeterministicAnalysis } from '@/lib/analysis/run'
import { containsCausalClaim } from '@/lib/analysis/observations'
import { stableStringify } from '@/lib/analysis/package'
import { closeTestPool } from '../helpers/db'

/**
 * Kiểm chứng trên BA KÊNH THẬT đã nhập ở Phase 2.
 *
 * Chạy trên database CHÍNH (dữ liệu thật), không phải database test — nên chỉ
 * ĐỌC và chỉ chạy ở chế độ dry-run: không ghi gì. Test tự bỏ qua khi chưa có
 * dữ liệu thật, để bộ test vẫn chạy được trên máy sạch.
 *
 * Đây là nơi khẳng định mức nén, vì chỉ ở quy mô thật thì chi phí cố định của
 * phần định nghĩa feature mới trở nên không đáng kể.
 */
const PROD_URL = process.env.HUB_PROD_DATABASE_URL

describe.skipIf(!PROD_URL)('phân tích trên 3 kênh THẬT (chỉ đọc)', () => {
  afterAll(async () => {
    await closeTestPool()
  })

  async function withProdDb<T>(fn: () => Promise<T>): Promise<T> {
    const saved = process.env.DATABASE_URL
    process.env.DATABASE_URL = PROD_URL
    const { resetDbForTesting } = await import('@/db/client')
    resetDbForTesting()
    try {
      await configureWebSocketForNode()
      return await fn()
    } finally {
      process.env.DATABASE_URL = saved
      resetDbForTesting()
    }
  }

  it('cả 3 kênh cho ra gói hợp lệ, nén mạnh, tất định', async () => {
    await withProdDb(async () => {
      const db = getDb()
      const ws = await db
        .select({ id: schema.workspace.id })
        .from(schema.workspace)
        .where(eq(schema.workspace.slug, 'vietneu'))
        .limit(1)
      expect(ws[0], 'chưa seed workspace vietneu').toBeTruthy()

      const bounds = await db.execute<{ min: string | null; max: string | null }>(
        sql`SELECT min(date)::text AS min, max(date)::text AS max FROM video_daily_metric`,
      )
      const from = bounds.rows[0]?.min
      const to = bounds.rows[0]?.max
      expect(from, 'chưa có dữ liệu analytics thật').toBeTruthy()

      const labels = (
        await db
          .select({ label: schema.channel.label })
          .from(schema.channel)
          .where(eq(schema.channel.workspaceId, ws[0]!.id))
          .orderBy(schema.channel.label)
      ).map((c) => c.label)

      expect(labels.length, 'phải có đúng 3 kênh').toBe(3)

      let totalRaw = 0
      let totalPkg = 0

      for (const label of labels) {
        const r = await runDeterministicAnalysis({
          workspaceId: ws[0]!.id,
          channelLabel: label,
          windowStart: from!,
          windowEnd: to!,
          dryRun: true,
        })

        totalRaw += r.rawInputBytes
        totalPkg += r.packageBytes

        // --- Nén ---
        expect(r.reductionPercent, `${label}: nén phải trên 80%`).toBeGreaterThan(80)
        expect(r.packageBytes, `${label}: gói phải dưới 120KB`).toBeLessThan(120_000)

        // --- Nội dung ---
        expect(r.featureCount, `${label}: phải tính được feature`).toBeGreaterThan(0)
        expect(r.package.dataCoverage.videosTotal).toBeGreaterThan(0)
        expect(r.package.featureDefinitions.length).toBeGreaterThan(20)

        // --- Không tuyên bố nhân quả ---
        for (const o of r.package.observations) {
          expect(containsCausalClaim(o.statement), `${label}: "${o.statement}"`).toBe(false)
        }
        for (const h of r.package.hypothesisCandidates) {
          expect(h.isHypothesis).toBe(true)
          expect(h.hypothesisQuestion).toBeTruthy()
        }

        // --- Bằng chứng ---
        for (const o of r.package.observations) {
          expect(o.evidenceRefs.length, `${label}: quan sát thiếu bằng chứng`).toBeGreaterThan(0)
        }

        // --- Không lịch sử theo ngày ---
        const text = stableStringify(r.package)
        expect(text).not.toMatch(/"date":"\d{4}-\d{2}-\d{2}","views":/)

        // --- Không rò credential ---
        const lower = text.toLowerCase()
        for (const bad of ['postgres://', 'postgresql://', 'vhw_', 'vhu_', 'bearer ', 'client_secret', 'refresh_token']) {
          expect(lower, `${label}: gói chứa ${bad}`).not.toContain(bad)
        }

        // --- Tất định ---
        const again = await runDeterministicAnalysis({
          workspaceId: ws[0]!.id,
          channelLabel: label,
          windowStart: from!,
          windowEnd: to!,
          dryRun: true,
        })
        expect(again.packageHash, `${label}: hash phải ổn định`).toBe(r.packageHash)
      }

      const overall = ((totalRaw - totalPkg) / totalRaw) * 100
      expect(overall, 'tổng mức nén trên 3 kênh phải trên 85%').toBeGreaterThan(85)
    })
  }, 600_000)

  it('mọi feature thiếu đều có LÝ DO tường minh, không bịa số 0', async () => {
    await withProdDb(async () => {
      const db = getDb()
      const ws = await db
        .select({ id: schema.workspace.id })
        .from(schema.workspace)
        .where(eq(schema.workspace.slug, 'vietneu'))
        .limit(1)
      const bounds = await db.execute<{ min: string | null; max: string | null }>(
        sql`SELECT min(date)::text AS min, max(date)::text AS max FROM video_daily_metric`,
      )

      const r = await runDeterministicAnalysis({
        workspaceId: ws[0]!.id,
        channelLabel: 'phong_thuy',
        windowStart: bounds.rows[0]!.min!,
        windowEnd: bounds.rows[0]!.max!,
        dryRun: true,
      })

      // Ba kênh này không được YouTube cấp impressions/CTR -> phải hiện ra là
      // THIẾU, và phải chặn mọi kết luận về khâu tiếp cận.
      expect(r.package.dataCoverage.metricCoverage['impressions']).toBe(0)
      expect(r.package.missingData.length).toBeGreaterThan(0)
      expect(r.missingFeatureCount).toBeGreaterThan(0)
    })
  }, 300_000)
})
