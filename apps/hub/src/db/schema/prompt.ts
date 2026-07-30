import { sql } from 'drizzle-orm'
import {
  check,
  foreignKey,
  index,
  integer,
  jsonb,
  pgTable,
  text,
  timestamp,
  unique,
  uniqueIndex,
  uuid,
} from 'drizzle-orm/pg-core'

import { promptAuthorEnum, promptPurposeEnum } from './enums'
import { workspace } from './workspace'

/** Một "khe" prompt có tên, ví dụ 'cursor.analysis.channel'. */
export const promptTemplate = pgTable(
  'prompt_template',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    key: text('key').notNull(),
    purpose: promptPurposeEnum('purpose').notNull(),
    description: text('description'),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    uniqueIndex('prompt_template_workspace_key_key').on(t.workspaceId, t.key),
    // Đích cho khoá ngoại ghép từ prompt_revision.
    unique('prompt_template_id_workspace_key').on(t.id, t.workspaceId),
  ],
)

/**
 * Bản prompt BẤT BIẾN. Vòng lặp Phase 5 bắt buộc "giữ lại mọi phiên bản prompt,
 * kết quả, critique và đánh giá", nên ở đây không có UPDATE: tinh chỉnh prompt
 * tạo ra hàng MỚI trỏ về `parentRevisionId`, tạo thành một cây phả hệ đọc ngược
 * được từ bản cuối về bản gốc.
 *
 * Bất biến cưỡng chế bằng trigger ở tầng DB (migration 0001).
 */
export const promptRevision = pgTable(
  'prompt_revision',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    templateId: uuid('template_id').notNull(),
    /**
     * Denormalize workspace để `llm_execution` và `critique` neo được cả prompt
     * lẫn workspace bằng một khoá ngoại ghép. Cột này bị ràng buộc phải khớp
     * workspace của template cha (khoá ngoại ghép bên dưới) nên không lệch được.
     */
    workspaceId: uuid('workspace_id').notNull(),
    revisionNumber: integer('revision_number').notNull(),
    body: text('body').notNull(),
    /** Tên các biến mà body mong đợi — validate trước khi render. */
    variables: jsonb('variables').notNull().default(sql`'[]'::jsonb`),
    contentHash: text('content_hash').notNull(),
    authoredBy: promptAuthorEnum('authored_by').notNull(),
    /** Bản prompt mà bản này tinh chỉnh từ đó. NULL = bản gốc. */
    parentRevisionId: uuid('parent_revision_id'),
    /** Vì sao sửa — lấy từ critique của Codex ở Phase 5. */
    changeReason: text('change_reason'),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    foreignKey({
      columns: [t.templateId, t.workspaceId],
      foreignColumns: [promptTemplate.id, promptTemplate.workspaceId],
      name: 'prompt_revision_template_workspace_fk',
    }).onDelete('restrict'),
    // Đích cho khoá ngoại ghép từ llm_execution và critique.
    unique('prompt_revision_id_workspace_key').on(t.id, t.workspaceId),
    uniqueIndex('prompt_revision_template_number_key').on(t.templateId, t.revisionNumber),
    index('prompt_revision_template_idx').on(t.templateId),
    index('prompt_revision_parent_idx').on(t.parentRevisionId),
    check('prompt_revision_number_positive', sql`${t.revisionNumber} >= 1`),
    check('prompt_revision_hash_format', sql`${t.contentHash} ~ '^[0-9a-f]{64}$'`),
    // Không cho một bản tự nhận là cha của chính nó.
    check('prompt_revision_no_self_parent', sql`${t.parentRevisionId} IS DISTINCT FROM ${t.id}`),
  ],
)
