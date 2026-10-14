import { sql } from 'drizzle-orm'
import {
  check,
  index,
  numeric,
  pgTable,
  text,
  timestamp,
  uniqueIndex,
  uuid,
} from 'drizzle-orm/pg-core'

import { tokenScopeEnum, workerCapabilityEnum } from './enums'
import { workspace } from './workspace'

/**
 * XÁC THỰC NGƯỜI DÙNG và XÁC THỰC MÁY WORKER là hai hệ TÁCH BIỆT, cố ý không
 * dùng chung bảng token.
 *
 * Lý do: worker chạy trên máy local và chỉ cần nhận việc + nộp kết quả. Nếu
 * dùng chung một bảng token với người dùng thì chỉ cần một lỗi phân quyền là
 * worker thừa hưởng được scope APPROVE — trong khi bất biến của hệ thống là
 * agent/worker KHÔNG BAO GIỜ được tự phê duyệt (xem `approval`).
 *
 * Cả hai bảng chỉ lưu HASH sha256 của token, không bao giờ lưu giá trị gốc.
 * Rò database vì thế không rò được token dùng lại được.
 */

export const userAccount = pgTable(
  'user_account',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    email: text('email').notNull(),
    displayName: text('display_name').notNull(),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
    disabledAt: timestamp('disabled_at', { withTimezone: true }),
  },
  (t) => [uniqueIndex('user_account_email_key').on(t.email)],
)

export const userApiToken = pgTable(
  'user_api_token',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    userId: uuid('user_id')
      .notNull()
      .references(() => userAccount.id, { onDelete: 'cascade' }),
    /** Nhãn để người dùng nhận ra token, ví dụ "laptop cá nhân". */
    label: text('label').notNull(),
    /** sha256 hex của token gốc. KHÔNG BAO GIỜ lưu token gốc. */
    tokenHash: text('token_hash').notNull(),
    /** 8 ký tự đầu của token, chỉ để hiển thị/đối chiếu — không đủ để dùng lại. */
    tokenPrefix: text('token_prefix').notNull(),
    scopes: tokenScopeEnum('scopes').array().notNull(),
    expiresAt: timestamp('expires_at', { withTimezone: true }),
    revokedAt: timestamp('revoked_at', { withTimezone: true }),
    lastUsedAt: timestamp('last_used_at', { withTimezone: true }),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    uniqueIndex('user_api_token_hash_key').on(t.tokenHash),
    index('user_api_token_user_idx').on(t.userId),
    check('user_api_token_hash_format', sql`${t.tokenHash} ~ '^[0-9a-f]{64}$'`),
    check('user_api_token_scopes_nonempty', sql`array_length(${t.scopes}, 1) >= 1`),
  ],
)

/**
 * Máy worker cục bộ. Token của worker KHÔNG có scope kiểu người dùng; thay vào
 * đó nó có `capabilities` — đúng danh sách loại job nó được phép nhận. Đây là
 * allowlist đóng: server không bao giờ gửi shell command tuỳ ý, worker chỉ nhận
 * loại việc nằm trong danh sách này.
 */
export const workerMachine = pgTable(
  'worker_machine',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    machineLabel: text('machine_label').notNull(),
    tokenHash: text('token_hash').notNull(),
    tokenPrefix: text('token_prefix').notNull(),
    capabilities: workerCapabilityEnum('capabilities').array().notNull(),
    lastSeenAt: timestamp('last_seen_at', { withTimezone: true }),
    revokedAt: timestamp('revoked_at', { withTimezone: true }),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    uniqueIndex('worker_machine_token_hash_key').on(t.tokenHash),
    uniqueIndex('worker_machine_workspace_label_key').on(t.workspaceId, t.machineLabel),
    check('worker_machine_hash_format', sql`${t.tokenHash} ~ '^[0-9a-f]{64}$'`),
    check('worker_machine_capabilities_nonempty', sql`array_length(${t.capabilities}, 1) >= 1`),
  ],
)

/**
 * AC-6 — rate limit dùng chung, lưu ở DB.
 *
 * Đếm trong bộ nhớ KHÔNG hoạt động trên Vercel: mỗi invocation là một process
 * riêng, biến đếm reset liên tục, nên rate limit sẽ *trông như* đang chạy mà
 * thực tế không chặn gì. Bảng này là token bucket dùng chung cho mọi instance;
 * việc nạp lại token tính theo thời gian trôi qua ngay trong câu UPDATE nguyên
 * tử, nên không cần tiến trình nền nào.
 */
export const rateLimitBucket = pgTable(
  'rate_limit_bucket',
  {
    /** vd "worker:<uuid>:claim" hoặc "ip:1.2.3.4:sync". */
    key: text('key').primaryKey(),
    tokens: numeric('tokens', { precision: 12, scale: 4 }).notNull(),
    /** Token nạp lại mỗi giây. */
    refillRate: numeric('refill_rate', { precision: 12, scale: 4 }).notNull(),
    capacity: numeric('capacity', { precision: 12, scale: 4 }).notNull(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    check('rate_limit_tokens_nonneg', sql`${t.tokens} >= 0`),
    check('rate_limit_capacity_positive', sql`${t.capacity} > 0`),
    check('rate_limit_refill_positive', sql`${t.refillRate} > 0`),
  ],
)
