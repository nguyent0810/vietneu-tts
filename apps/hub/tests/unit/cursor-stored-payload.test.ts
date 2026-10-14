import { describe, expect, it } from 'vitest'

import { parseStoredCompositePayload } from '@/lib/cursor/composite'
import {
  COMPOSITE_VALIDATOR_VERSION,
  CURSOR_OUTPUT_SCHEMA_VERSION,
  OBLIGATION_GENERATOR_VERSION,
} from '@/lib/cursor/schema'

/**
 * Đọc lại một payload HỢP NHẤT ĐÃ LƯU.
 *
 * `cursorOutputSchema` là `.strict()`, còn payload đã lưu mang thêm `_meta`. Có
 * đúng hai cách sai và cả hai đều im lặng: ném thẳng vào `safeParse` rồi kết
 * luận nhầm là dữ liệu hỏng; hoặc gỡ `_meta` mà quên kiểm nó, tức vứt luôn phần
 * mang nguồn gốc. Hàm này là cách DUY NHẤT đúng, nên nó phải có test riêng.
 */

const BODY = {
  schemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,
  analysisSummary: {
    overallAssessment: 'Kênh có một video vượt trội rõ rệt so với phần còn lại trong cửa sổ.',
    confidence: 'MEDIUM',
    confidenceRationale: 'Độ phủ dữ liệu cốt lõi đầy đủ trong cửa sổ quan sát này.',
    primaryConstraint: 'Cỡ mẫu còn nhỏ nên kết luận xu hướng cần thận trọng.',
  },
  keyFindings: [
    {
      id: 'F-001',
      statement: 'Video aaaaaaaaaaa nằm ở nhóm dẫn đầu về lượt xem 7 ngày trong nhóm Shorts.',
      findingType: 'OBSERVATION',
      confidence: 'MEDIUM',
      evidenceIds: ['OBS-001'],
      supportingReasoning: 'Quan sát tất định ghi nhận phân vị 92 trong nhóm cùng định dạng.',
      contradictingEvidenceIds: [],
      limitations: [],
    },
  ],
  hypotheses: [],
  recommendations: [],
  experiments: [],
  manualReviewTargets: [],
  dataRequests: [],
  explicitNonConclusions: ['Không kết luận được về khâu tiếp cận.'],
  metricClaims: [],
  selfCheck: {
    usedOnlyProvidedEvidence: true,
    recomputedMetrics: false,
    madeCausalClaims: false,
    madeCtrOrImpressionClaims: false,
    allFindingEvidenceResolved: true,
  },
}

const META = {
  analysisExecutionId: 'a-1',
  declarationExecutionId: 'd-1',
  analysisPayloadHash: 'a'.repeat(64),
  obligationSetHash: 'b'.repeat(64),
  obligationCount: 3,
  // Lấy TỪ HẰNG SỐ, không gõ tay: bộ dò lệch phiên bản so `_meta` với mã đang
  // chạy, nên một chuỗi cứng trong fixture biến mọi lần bump hợp đồng thành một
  // test đỏ giả — và áp lực sửa sẽ rơi vào chỗ SAI.
  obligationGeneratorVersion: OBLIGATION_GENERATOR_VERSION,
  compositeValidatorVersion: COMPOSITE_VALIDATOR_VERSION,
}

const stored = (over: Record<string, unknown> = {}) => ({ ...BODY, _meta: META, ...over })

describe('payload đã lưu: đường ĐẠT', () => {
  it('gỡ `_meta` rồi kiểm phần còn lại bằng schema nghiêm ngặt', () => {
    const r = parseStoredCompositePayload(stored())
    expect(r.ok, JSON.stringify(r.issues)).toBe(true)
    expect(r.payload).not.toBeNull()
    expect(r.meta).toEqual(META)
    // `_meta` KHÔNG được lọt vào payload đã kiểm.
    expect(Object.keys(r.payload!)).not.toContain('_meta')
  })

  it('đối chiếu `_meta` với hàng database khi được cho biết kỳ vọng', () => {
    const r = parseStoredCompositePayload(stored(), {
      analysisExecutionId: 'a-1',
      declarationExecutionId: 'd-1',
      analysisPayloadHash: 'a'.repeat(64),
      obligationSetHash: 'b'.repeat(64),
      obligationCount: 3,
    })
    expect(r.ok, JSON.stringify(r.issues)).toBe(true)
  })
})

describe('payload đã lưu: `_meta` THIẾU', () => {
  it('không có `_meta` -> chặn', () => {
    const r = parseStoredCompositePayload(BODY)
    expect(r.ok).toBe(false)
    expect(r.issues.map((i) => i.rule)).toContain('stored_payload_missing_meta')
  })

  it('thiếu MỘT trường bắt buộc trong `_meta` -> chặn', () => {
    for (const k of [
      'analysisExecutionId',
      'declarationExecutionId',
      'analysisPayloadHash',
      'obligationSetHash',
      'obligationCount',
      'obligationGeneratorVersion',
      'compositeValidatorVersion',
    ]) {
      const meta: Record<string, unknown> = { ...META }
      delete meta[k]
      const r = parseStoredCompositePayload({ ...BODY, _meta: meta })
      expect(r.ok, `thiếu ${k} mà vẫn cho qua`).toBe(false)
      expect(r.issues.map((i) => i.rule)).toContain('stored_payload_malformed_meta')
    }
  })
})

describe('payload đã lưu: `_meta` HỎNG DẠNG', () => {
  it('`_meta` là chuỗi -> chặn', () => {
    const r = parseStoredCompositePayload({ ...BODY, _meta: 'không phải object' })
    expect(r.ok).toBe(false)
    expect(r.issues.map((i) => i.rule)).toContain('stored_payload_malformed_meta')
  })

  it('`_meta` là mảng -> chặn', () => {
    const r = parseStoredCompositePayload({ ...BODY, _meta: [] })
    expect(r.ok).toBe(false)
    expect(r.issues.map((i) => i.rule)).toContain('stored_payload_malformed_meta')
  })

  it('payload không phải object -> chặn', () => {
    for (const bad of ['chuỗi', 42, null, []]) {
      const r = parseStoredCompositePayload(bad)
      expect(r.ok, String(bad)).toBe(false)
      expect(r.issues.map((i) => i.rule)).toContain('stored_payload_not_object')
    }
  })
})

describe('payload đã lưu: `_meta` LỆCH hàng database', () => {
  it('lệch id execution -> chặn', () => {
    const r = parseStoredCompositePayload(stored(), { analysisExecutionId: 'a-KHÁC' })
    expect(r.ok).toBe(false)
    expect(r.issues.map((i) => i.rule)).toContain('stored_payload_meta_mismatch')
  })

  it('lệch băm -> chặn', () => {
    const r = parseStoredCompositePayload(stored(), { obligationSetHash: 'c'.repeat(64) })
    expect(r.ok).toBe(false)
    expect(r.issues.map((i) => i.rule)).toContain('stored_payload_meta_mismatch')
  })

  it('lệch số nghĩa vụ -> chặn', () => {
    const r = parseStoredCompositePayload(stored(), { obligationCount: 99 })
    expect(r.ok).toBe(false)
    expect(r.issues.map((i) => i.rule)).toContain('stored_payload_meta_mismatch')
  })
})

describe('payload đã lưu: THÂN hỏng', () => {
  it('thân sai schema -> chặn, kể cả khi `_meta` đúng', () => {
    const r = parseStoredCompositePayload({ ...stored(), keyFindings: [] })
    expect(r.ok).toBe(false)
    expect(r.issues.map((i) => i.rule)).toContain('stored_payload_schema')
  })

  it('thân mang trường lạ -> chặn (schema vẫn NGHIÊM NGẶT sau khi gỡ `_meta`)', () => {
    const r = parseStoredCompositePayload({ ...stored(), truongLa: 1 })
    expect(r.ok).toBe(false)
    expect(r.issues.map((i) => i.rule)).toContain('stored_payload_schema')
  })
})
