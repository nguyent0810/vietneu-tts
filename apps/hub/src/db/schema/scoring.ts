import { sql } from 'drizzle-orm'
import {
  check,
  index,
  integer,
  jsonb,
  numeric,
  pgTable,
  text,
  timestamp,
  uniqueIndex,
  uuid,
} from 'drizzle-orm/pg-core'

import { dimensionSetEnum, evaluationVerdictEnum, evaluatorEnum } from './enums'
import { algorithmVersion } from './analysis'
import { analysisResult } from './analysis'

/**
 * Danh mục chiều điểm. Là BẢNG chứ không phải enum vì bộ chiều điểm sẽ đổi
 * theo thời gian, và mỗi điểm số cũ phải còn tra ngược được về định nghĩa
 * chiều tại thời điểm chấm.
 *
 * Hai bộ tách biệt (xem `dimension_set`):
 *  - CONTENT: chấm bản thân nội dung (17 chiều trong kế hoạch gốc).
 *  - ANALYSIS_RUBRIC: chấm CHẤT LƯỢNG một kết quả phân tích — 8 chiều bắt buộc
 *    của Phase 5 (factual grounding, evidence coverage, internal consistency,
 *    actionability, uncertainty calibration, channel relevance, no invented
 *    metrics, schema adherence).
 */
export const scoreDimension = pgTable(
  'score_dimension',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    dimensionSet: dimensionSetEnum('dimension_set').notNull(),
    key: text('key').notNull(),
    label: text('label').notNull(),
    description: text('description'),
    scaleMin: numeric('scale_min', { precision: 6, scale: 2 }).notNull().default('0'),
    scaleMax: numeric('scale_max', { precision: 6, scale: 2 }).notNull().default('5'),
    /** Trọng số khi gộp thành điểm tổng. */
    weight: numeric('weight', { precision: 6, scale: 3 }).notNull().default('1'),
    sortOrder: integer('sort_order').notNull().default(0),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    uniqueIndex('score_dimension_set_key_key').on(t.dimensionSet, t.key),
    check('score_dimension_scale_order', sql`${t.scaleMax} > ${t.scaleMin}`),
  ],
)

/**
 * Một lượt chấm điểm hoàn chỉnh trên MỘT `analysis_result`.
 *
 * Phase 5 so sánh bản cũ và bản mới bằng cách tạo hai `evaluation` dùng CÙNG
 * `rubricVersionId` — nếu rubric khác nhau thì phép so sánh vô nghĩa, nên
 * version của rubric được ghi thẳng vào đây thay vì suy đoán lúc đọc.
 */
export const evaluation = pgTable(
  'evaluation',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    analysisResultId: uuid('analysis_result_id')
      .notNull()
      .references(() => analysisResult.id, { onDelete: 'cascade' }),
    rubricVersionId: uuid('rubric_version_id')
      .notNull()
      .references(() => algorithmVersion.id, { onDelete: 'restrict' }),
    evaluator: evaluatorEnum('evaluator').notNull(),
    /** Điểm tổng đã tính theo trọng số. Lưu lại để không phải tính lại khi đọc. */
    totalScore: numeric('total_score', { precision: 8, scale: 3 }),
    verdict: evaluationVerdictEnum('verdict'),
    rationale: text('rationale'),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    uniqueIndex('evaluation_result_rubric_evaluator_key').on(
      t.analysisResultId,
      t.rubricVersionId,
      t.evaluator,
    ),
    index('evaluation_result_idx').on(t.analysisResultId),
  ],
)

/** Điểm của từng chiều trong một lượt chấm. */
export const score = pgTable(
  'score',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    evaluationId: uuid('evaluation_id')
      .notNull()
      .references(() => evaluation.id, { onDelete: 'cascade' }),
    dimensionId: uuid('dimension_id')
      .notNull()
      .references(() => scoreDimension.id, { onDelete: 'restrict' }),
    value: numeric('value', { precision: 6, scale: 2 }).notNull(),
    rationale: text('rationale'),
    /** Trích dẫn bằng chứng cho điểm này (id observation, video, metric...). */
    evidenceRefs: jsonb('evidence_refs').notNull().default(sql`'[]'::jsonb`),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    // Một chiều chỉ được chấm một lần trong mỗi lượt -- nếu không, "điểm tổng"
    // sẽ phụ thuộc vào việc đọc trúng hàng nào.
    uniqueIndex('score_evaluation_dimension_key').on(t.evaluationId, t.dimensionId),
    index('score_evaluation_idx').on(t.evaluationId),
  ],
)
