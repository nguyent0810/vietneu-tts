import { sql } from 'drizzle-orm'
import {
  check,
  index,
  jsonb,
  pgTable,
  text,
  timestamp,
  uniqueIndex,
  uuid,
} from 'drizzle-orm/pg-core'

import { actorTypeEnum, approvalStateEnum } from './enums'
import { workspace } from './workspace'

/**
 * Nhật ký append-only. Không có cột updated_at và không bao giờ UPDATE — một
 * dòng audit sửa được thì nó không còn là bằng chứng.
 */
export const auditEvent = pgTable(
  'audit_event',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    actorType: actorTypeEnum('actor_type').notNull(),
    /** id người dùng / machine label / tên tiến trình. KHÔNG BAO GIỜ chứa token. */
    actorId: text('actor_id').notNull(),
    action: text('action').notNull(),
    entityType: text('entity_type').notNull(),
    entityId: uuid('entity_id'),
    payload: jsonb('payload').notNull().default(sql`'{}'::jsonb`),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    index('audit_event_workspace_created_idx').on(t.workspaceId, t.createdAt),
    index('audit_event_entity_idx').on(t.entityType, t.entityId),
  ],
)

/**
 * Phê duyệt của CON NGƯỜI.
 *
 * Ràng buộc cốt lõi: agent/worker KHÔNG được tự phê duyệt. Điều này cưỡng chế
 * ở tầng DB (`approval_decider_must_be_human`) chứ không chỉ ở tầng route —
 * nếu chỉ chặn ở route thì một đường ghi khác, hoặc một bug phân quyền, là đủ
 * để một agent tự duyệt chính kết quả nó tạo ra.
 */
export const approval = pgTable(
  'approval',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    entityType: text('entity_type').notNull(),
    entityId: uuid('entity_id').notNull(),
    state: approvalStateEnum('state').notNull().default('PENDING'),
    decidedByType: actorTypeEnum('decided_by_type'),
    decidedById: text('decided_by_id'),
    decidedAt: timestamp('decided_at', { withTimezone: true }),
    reason: text('reason'),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    // Mỗi thực thể chỉ có một bản ghi phê duyệt đang mở.
    uniqueIndex('approval_entity_key').on(t.entityType, t.entityId),
    index('approval_workspace_state_idx').on(t.workspaceId, t.state),
    // Đã quyết định thì phải có đủ ai/khi nào; còn PENDING thì phải trống.
    check(
      'approval_decision_consistency',
      sql`(${t.state} = 'PENDING') = (${t.decidedAt} IS NULL AND ${t.decidedByType} IS NULL AND ${t.decidedById} IS NULL)`,
    ),
    // Chỉ USER mới được quyết định. AGENT/WORKER/SYSTEM bị chặn ở tầng DB.
    check(
      'approval_decider_must_be_human',
      sql`${t.decidedByType} IS NULL OR ${t.decidedByType} = 'USER'`,
    ),
  ],
)
