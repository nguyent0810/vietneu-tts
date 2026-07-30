import { sql } from 'drizzle-orm'

import { getDb } from '@/db/client'

/**
 * AC-6 — Token bucket dùng chung, trạng thái nằm trong Neon.
 *
 * KHÔNG dùng biến đếm ở module scope: trên Vercel mỗi invocation là một
 * process riêng, biến sẽ reset liên tục và rate limit *trông như* đang chạy
 * trong khi thực tế không chặn gì. Đó là lý do trạng thái phải nằm ở DB.
 *
 * Toàn bộ phép "nạp lại theo thời gian trôi qua + trừ 1 token + trả về kết quả"
 * gói trong MỘT câu lệnh nguyên tử, nên:
 *  - không cần transaction tương tác (driver HTTP dùng được);
 *  - hai request đồng thời không thể cùng tiêu một token cuối cùng.
 *
 * `ON CONFLICT ... WHERE` không dùng được cho phép trừ có điều kiện, nên bucket
 * luôn được UPSERT rồi mới đọc kết quả — chi phí một round-trip, đổi lấy tính
 * nguyên tử.
 */

export interface RateLimitResult {
  allowed: boolean
  remaining: number
  retryAfterSeconds: number
}

export interface RateLimitOptions {
  /** Số token tối đa (kích thước burst). */
  capacity: number
  /** Token nạp lại mỗi giây. */
  refillRate: number
  /** Số token mà request này tiêu. */
  cost?: number
}

export async function consumeRateLimit(
  key: string,
  options: RateLimitOptions,
): Promise<RateLimitResult> {
  const { capacity, refillRate, cost = 1 } = options

  if (cost > capacity) {
    throw new Error(`cost (${cost}) vượt capacity (${capacity}) — bucket sẽ không bao giờ cho qua.`)
  }

  const db = getDb()

  // Số token sau khi nạp lại theo thời gian đã trôi, chặn trần ở capacity.
  // Dùng lại nguyên văn ở cả SET lẫn WHERE để hai vế luôn nhất quán.
  const refilled = sql`LEAST(
    capacity,
    tokens + EXTRACT(EPOCH FROM (now() - updated_at)) * refill_rate
  )`

  // Bước 1 — đảm bảo bucket tồn tại. Idempotent; nhiều request đồng thời thì
  // đúng một cái tạo được, phần còn lại DO NOTHING (KHÔNG reset token).
  await db.execute(sql`
    INSERT INTO rate_limit_bucket (key, tokens, refill_rate, capacity, updated_at)
    VALUES (${key}, ${capacity}, ${refillRate}, ${capacity}, now())
    ON CONFLICT (key) DO NOTHING
  `)

  // Bước 2 — nạp lại và trừ token trong MỘT câu UPDATE có điều kiện (CAS).
  //
  // Vì sao không gộp bước 1 và 2 vào một CTE: trong PostgreSQL, mọi
  // sub-statement của WITH dùng CHUNG một snapshot và không thấy tác động của
  // nhau lên cùng bảng. Bản đầu tiên viết theo kiểu đó nên nhánh UPDATE không
  // bao giờ nhìn thấy hàng vừa được INSERT, và rate limit chặn đứng mọi
  // request ngay từ cái đầu tiên. Test đồng thời là thứ phát hiện ra.
  //
  // Ở mức READ COMMITTED, hai UPDATE tranh nhau cùng hàng sẽ nối đuôi: cái sau
  // chờ cái trước commit rồi ĐÁNH GIÁ LẠI mệnh đề WHERE trên phiên bản hàng
  // mới. Nhờ đó đúng `capacity` request được qua, không hơn.
  const spent = await db.execute<{ tokens: string }>(sql`
    UPDATE rate_limit_bucket
       SET tokens = ${refilled} - ${cost},
           refill_rate = ${refillRate},
           capacity = ${capacity},
           updated_at = now()
     WHERE key = ${key}
       AND ${refilled} >= ${cost}
    RETURNING tokens
  `)

  const spentRow = spent.rows[0]
  if (spentRow) {
    return { allowed: true, remaining: Math.max(0, Number(spentRow.tokens)), retryAfterSeconds: 0 }
  }

  // Bị chặn — đọc số token hiện có để tính thời gian chờ.
  const current = await db.execute<{ tokens: string }>(sql`
    SELECT ${refilled} AS tokens FROM rate_limit_bucket WHERE key = ${key}
  `)
  const remaining = Number(current.rows[0]?.tokens ?? 0)

  return {
    allowed: false,
    remaining: Math.max(0, remaining),
    retryAfterSeconds: Math.max(1, Math.ceil((cost - remaining) / refillRate)),
  }
}
