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

import { contentKindEnum, contentStatusEnum, revisionStateEnum } from './enums'
import { channel, workspace } from './workspace'

/**
 * Một đơn vị nội dung (kịch bản dài hoặc short). Bản thân nó là thực thể KHẢ
 * BIẾN chỉ ở phần trạng thái/con trỏ; toàn bộ nội dung thật nằm ở
 * `content_revision` và bất biến sau khi FREEZE.
 */
export const contentItem = pgTable(
  'content_item',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    channelId: uuid('channel_id').notNull(),
    /** Khoá đối chiếu sang gói nội dung gốc trong repo Content-Creator. */
    externalRef: text('external_ref'),
    kind: contentKindEnum('kind').notNull(),
    title: text('title').notNull(),
    status: contentStatusEnum('status').notNull().default('DRAFT'),
    /**
     * AC-5: cột này để nullable và CHƯA có khoá ngoại. Bảng `video` chỉ ra đời
     * ở migration sau (Phase 2); tạo FK ngay bây giờ sẽ làm migration fail khi
     * chạy từ database rỗng. FK được thêm ở migration sau khi `video` tồn tại.
     */
    publishedVideoId: text('published_video_id'),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    // Khoá ngoại GHÉP: kênh phải thuộc ĐÚNG workspace mà content_item khai báo.
    // Hai khoá ngoại rời nhau (workspace_id, channel_id) sẽ cho phép một hàng
    // khai workspace A trong khi trỏ vào kênh của workspace B -- phá vỡ cách ly
    // giữa các workspace mà không có gì báo lỗi.
    foreignKey({
      columns: [t.channelId, t.workspaceId],
      foreignColumns: [channel.id, channel.workspaceId],
      name: 'content_item_channel_workspace_fk',
    }).onDelete('restrict'),
    index('content_item_workspace_idx').on(t.workspaceId),
    index('content_item_channel_idx').on(t.channelId),
    uniqueIndex('content_item_external_ref_key')
      .on(t.workspaceId, t.externalRef)
      .where(sql`${t.externalRef} IS NOT NULL`),
    // Đích cho khoá ngoại ghép từ content_revision.
    unique('content_item_id_workspace_key').on(t.id, t.workspaceId),
  ],
)

/**
 * Bản sửa đổi BẤT BIẾN của nội dung. Chỉ lưu TEXT — kịch bản audio và SEO.
 * Không lưu audio/video/ảnh: media ở lại máy local theo đúng quyết định kiến
 * trúc (xem AC-7).
 *
 * Bất biến được cưỡng chế ở tầng DB bằng trigger (migration 0001), không chỉ ở
 * tầng ứng dụng: một revision đã FROZEN mà vẫn sửa được thì mọi điểm số và phê
 * duyệt trỏ vào nó đều mất ý nghĩa.
 *
 * `onDelete: 'restrict'` (KHÔNG phải cascade) là có chủ đích: nếu để cascade
 * thì xoá một `content_item` sẽ xoá sạch các revision đã FROZEN cùng lịch sử
 * phân tích của chúng — đúng thứ mà trigger bất biến sinh ra để ngăn. Muốn
 * "bỏ" một nội dung thì đổi `status` sang ARCHIVED, không xoá.
 */
export const contentRevision = pgTable(
  'content_revision',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    contentItemId: uuid('content_item_id').notNull(),
    /**
     * Denormalize workspace để khoá ngoại ghép ở `analysis_run` neo được cả
     * revision lẫn workspace. Bản thân cột này bị ràng buộc phải khớp workspace
     * của content_item cha (khoá ngoại ghép ngay dưới), nên không thể lệch.
     */
    workspaceId: uuid('workspace_id').notNull(),
    revisionNumber: integer('revision_number').notNull(),
    state: revisionStateEnum('state').notNull().default('DRAFT'),
    /** Kịch bản đọc thành audio. Đây là "content" duy nhất được lưu server-side. */
    audioScript: text('audio_script').notNull(),
    /** title/description/tags/thumbnail_text — chỉ metadata dạng text. */
    seo: jsonb('seo').notNull().default(sql`'{}'::jsonb`),
    /** sha256 của (audio_script || seo chuẩn hoá). Dùng để phát hiện sửa lén. */
    contentHash: text('content_hash').notNull(),
    frozenAt: timestamp('frozen_at', { withTimezone: true }),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    foreignKey({
      columns: [t.contentItemId, t.workspaceId],
      foreignColumns: [contentItem.id, contentItem.workspaceId],
      name: 'content_revision_item_workspace_fk',
    }).onDelete('restrict'),
    uniqueIndex('content_revision_item_number_key').on(t.contentItemId, t.revisionNumber),
    index('content_revision_item_idx').on(t.contentItemId),
    // Đích cho khoá ngoại ghép từ analysis_run.
    unique('content_revision_id_workspace_key').on(t.id, t.workspaceId),
    check('content_revision_number_positive', sql`${t.revisionNumber} >= 1`),
    check('content_revision_hash_format', sql`${t.contentHash} ~ '^[0-9a-f]{64}$'`),
    // FROZEN thì bắt buộc có frozen_at, và ngược lại. Hai cột này không được
    // phép lệch nhau -- nếu lệch thì bất biến S-0 (freeze trước khi audit)
    // không kiểm chứng được nữa.
    check(
      'content_revision_frozen_consistency',
      sql`(${t.state} = 'FROZEN') = (${t.frozenAt} IS NOT NULL)`,
    ),
  ],
)
