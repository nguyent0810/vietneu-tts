import { afterAll, beforeEach, describe, expect, it } from 'vitest'
import { sql } from 'drizzle-orm'

import { consumeRateLimit } from '@/lib/ratelimit'
import { closeTestPool, hasTestDatabase, testDb } from '../helpers/db'

/**
 * AC-6 — rate limit phải dùng chung giữa các instance.
 *
 * Điểm mấu chốt của bộ test này: nó gọi `consumeRateLimit` qua driver HTTP của
 * Neon (`@/db/client`), trong khi phần dọn dẹp dùng Pool/WebSocket riêng. Hai
 * đường kết nối KHÁC NHAU tới cùng database chính là mô phỏng cho hai
 * invocation serverless khác nhau — thứ mà một biến đếm trong bộ nhớ không bao
 * giờ chặn được.
 */
describe.skipIf(!hasTestDatabase)('rate limit dùng chung (PostgreSQL thật)', () => {
  const db = testDb()

  beforeEach(async () => {
    await db.execute(sql`TRUNCATE TABLE rate_limit_bucket`)
  })

  afterAll(async () => {
    await closeTestPool()
  })

  it('cho qua tới capacity rồi chặn', async () => {
    const key = `test:burst:${Date.now()}`
    const opts = { capacity: 3, refillRate: 0.001 }

    const first = await consumeRateLimit(key, opts)
    const second = await consumeRateLimit(key, opts)
    const third = await consumeRateLimit(key, opts)
    const fourth = await consumeRateLimit(key, opts)

    expect(first.allowed).toBe(true)
    expect(second.allowed).toBe(true)
    expect(third.allowed).toBe(true)
    expect(fourth.allowed).toBe(false)
    expect(fourth.retryAfterSeconds).toBeGreaterThan(0)
  })

  it('trạng thái nằm ở DB nên thấy được từ kết nối khác', async () => {
    const key = `test:shared:${Date.now()}`
    const opts = { capacity: 2, refillRate: 0.001 }

    await consumeRateLimit(key, opts)
    await consumeRateLimit(key, opts)

    // Đọc bằng Pool/WebSocket -- kết nối hoàn toàn khác với driver HTTP ở trên.
    const rows = await db.execute<{ tokens: string }>(
      sql`SELECT tokens FROM rate_limit_bucket WHERE key = ${key}`,
    )
    expect(rows.rows).toHaveLength(1)
    expect(Number(rows.rows[0]!.tokens)).toBeLessThan(1)

    const blocked = await consumeRateLimit(key, opts)
    expect(blocked.allowed).toBe(false)
  })

  it('đồng thời: đúng `capacity` request được qua, không hơn', async () => {
    const key = `test:concurrent:${Date.now()}`
    const capacity = 5
    const attempts = 20
    const opts = { capacity, refillRate: 0.001 }

    // Nếu phép trừ token không nguyên tử, nhiều request sẽ cùng đọc được cùng
    // một giá trị tokens và cùng cho qua -- test này bắt đúng lỗi đó.
    const results = await Promise.all(
      Array.from({ length: attempts }, () => consumeRateLimit(key, opts)),
    )

    const allowed = results.filter((r) => r.allowed).length
    expect(allowed).toBe(capacity)
    expect(results.filter((r) => !r.allowed)).toHaveLength(attempts - capacity)
  })

  it('nạp lại token theo thời gian trôi qua', async () => {
    const key = `test:refill:${Date.now()}`
    // 1 token/giây. Tốc độ nạp phải đủ CHẬM so với độ trễ mạng tới Neon:
    // với 20 token/giây, chỉ riêng một round-trip (~100ms) đã nạp đủ 1 token
    // và lần gọi thứ hai được cho qua -- test sẽ fail vì lý do không liên quan
    // đến tính đúng đắn của rate limit.
    const opts = { capacity: 1, refillRate: 1 }

    expect((await consumeRateLimit(key, opts)).allowed).toBe(true)
    // Ngay sau đó: chưa trôi đủ 1 giây nên phải bị chặn.
    expect((await consumeRateLimit(key, opts)).allowed).toBe(false)

    await new Promise((resolve) => setTimeout(resolve, 1500))

    expect((await consumeRateLimit(key, opts)).allowed).toBe(true)
  })

  it('không bao giờ vượt quá capacity dù để lâu', async () => {
    const key = `test:cap:${Date.now()}`
    const opts = { capacity: 2, refillRate: 1000 }

    await consumeRateLimit(key, opts)
    await new Promise((resolve) => setTimeout(resolve, 200))

    const rows = await db.execute<{ tokens: string }>(
      sql`SELECT tokens FROM rate_limit_bucket WHERE key = ${key}`,
    )
    // Sau khi nạp lại, tokens không được vượt capacity (LEAST(...) trong SQL).
    await consumeRateLimit(key, opts)
    const after = await db.execute<{ tokens: string }>(
      sql`SELECT tokens FROM rate_limit_bucket WHERE key = ${key}`,
    )
    expect(Number(after.rows[0]!.tokens)).toBeLessThanOrEqual(opts.capacity)
    expect(rows.rows).toHaveLength(1)
  })

  it('từ chối cấu hình cost lớn hơn capacity', async () => {
    await expect(
      consumeRateLimit('test:bad', { capacity: 2, refillRate: 1, cost: 5 }),
    ).rejects.toThrow(/capacity/)
  })
})
