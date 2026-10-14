import { sql } from 'drizzle-orm'
import {
  check,
  index,
  pgTable,
  text,
  timestamp,
  unique,
  uniqueIndex,
  uuid,
} from 'drizzle-orm/pg-core'

/**
 * Workspace là biên giới sở hữu dữ liệu. Mọi bảng nghiệp vụ đều mang
 * `workspace_id` để truy vấn không bao giờ vô tình cắt ngang giữa các workspace.
 * MVP chỉ có một workspace, nhưng đặt sẵn khoá này rẻ hơn nhiều so với thêm nó
 * sau khi dữ liệu đã lớn.
 */
export const workspace = pgTable(
  'workspace',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    slug: text('slug').notNull(),
    name: text('name').notNull(),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [uniqueIndex('workspace_slug_key').on(t.slug)],
)

/**
 * Ba kênh YouTube đang vận hành. `youtube_channel_id` (UC...) là định danh
 * THẬT của YouTube và duy nhất toàn cục — không chỉ trong workspace — vì cùng
 * một kênh không thể thuộc hai workspace cùng lúc.
 *
 * `timezone` là mấu chốt của Phase 2: YouTube Analytics báo cáo theo ngày ở
 * múi giờ Thái Bình Dương (America/Los_Angeles) chứ không theo UTC, nên
 * "ngày" phải quy chiếu tường minh thay vì suy từ timestamp.
 */
export const channel = pgTable(
  'channel',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workspaceId: uuid('workspace_id')
      .notNull()
      .references(() => workspace.id, { onDelete: 'restrict' }),
    label: text('label').notNull(),
    youtubeChannelId: text('youtube_channel_id').notNull(),
    title: text('title').notNull(),
    reportingTimezone: text('reporting_timezone').notNull().default('America/Los_Angeles'),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    uniqueIndex('channel_youtube_id_key').on(t.youtubeChannelId),
    uniqueIndex('channel_workspace_label_key').on(t.workspaceId, t.label),
    index('channel_workspace_idx').on(t.workspaceId),
    // Đích cho khoá ngoại GHÉP từ các bảng con: bảng con tham chiếu đồng thời
    // (channel_id, workspace_id) nên không thể khai workspace A trong khi trỏ
    // vào kênh của workspace B. Xem content_item / analysis_run.
    unique('channel_id_workspace_key').on(t.id, t.workspaceId),
    // Label dùng làm khoá tra cứu từ CLI local (.youtube_channels/{label}.json),
    // nên phải khớp đúng dạng slug đó -- chặn ngay ở DB thay vì tin phía gọi.
    check('channel_label_format', sql`${t.label} ~ '^[a-z][a-z0-9_]{1,62}$'`),
  ],
)
