import { describe, expect, it } from 'vitest'

import {
  checkProvenanceCoverage,
  PROVENANCE_EQUALITIES,
  PROVENANCE_MATRIX,
  type ProvenanceSurfaceName,
} from '@/lib/cursor/provenance'

/**
 * MA TRẬN PHỦ NGUỒN GỐC — yêu cầu đến TỪ MA TRẬN, không đến từ caller.
 *
 * Đây là bài học của chính vòng trước. `checkProvenanceAgreement` chỉ so đúng
 * những trường caller truyền vào, nên một caller quên `obligationSetHash` sẽ
 * nhận về "đồng thuận: đúng" — không phải vì mọi bề mặt khớp nhau, mà vì không
 * ai hỏi. Một phép kiểm mà người gọi tự chọn phạm vi thì cái nó bảo vệ chính là
 * cái nó bỏ sót đầu tiên.
 *
 * `checkProvenanceCoverage` lấy danh sách bắt buộc từ `PROVENANCE_MATRIX`. Quên
 * là hỏng.
 */

const FULL: Record<string, unknown> = {}
for (const spec of Object.values(PROVENANCE_MATRIX)) {
  for (const f of spec.required) FULL[f] = `giá-trị-${f}`
}
/** Một bề mặt hợp lệ: đủ trường bắt buộc, không có trường không-áp-dụng. */
const surface = (name: ProvenanceSurfaceName, over: Record<string, unknown> = {}) => {
  const spec = PROVENANCE_MATRIX[name]
  const o: Record<string, unknown> = {}
  for (const f of spec.required) o[f] = FULL[f]
  return { ...o, ...over }
}

describe('ma trận: hình dạng', () => {
  it('không trường nào vừa BẮT BUỘC vừa KHÔNG ÁP DỤNG trên cùng một bề mặt', () => {
    for (const [name, spec] of Object.entries(PROVENANCE_MATRIX)) {
      const overlap = spec.required.filter((f) => spec.notApplicable.includes(f))
      expect(overlap, `${name} tự mâu thuẫn ở: ${overlap.join(', ')}`).toEqual([])
    }
  })

  it('mọi quan hệ BẰNG NHAU chỉ nhắc tới bề mặt có thật', () => {
    for (const eq of PROVENANCE_EQUALITIES) {
      for (const s of eq.surfaces) {
        expect(PROVENANCE_MATRIX[s], `bề mặt lạ "${s}" trong quan hệ ${eq.field}`).toBeDefined()
      }
    }
  })

  it('mọi quan hệ BẰNG NHAU chỉ so trường mà bề mặt ấy THỰC SỰ mang', () => {
    // Một quan hệ nhắc tới trường mà bề mặt kia đánh dấu "không áp dụng" là quan
    // hệ không bao giờ chạy — tức một phép so tưởng là có mà thật ra không có.
    for (const eq of PROVENANCE_EQUALITIES) {
      for (const s of eq.surfaces) {
        expect(
          PROVENANCE_MATRIX[s].notApplicable.includes(eq.field),
          `quan hệ "${eq.field}" nhắc bề mặt "${s}" nhưng bề mặt đó đánh dấu KHÔNG ÁP DỤNG`,
        ).toBe(false)
      }
    }
  })

  it('mọi bề mặt được liệt kê đều có đặc tả', () => {
    expect(Object.keys(PROVENANCE_MATRIX).length).toBeGreaterThanOrEqual(14)
    for (const [name, spec] of Object.entries(PROVENANCE_MATRIX)) {
      expect(spec.required.length, `${name} không đòi hỏi gì cả`).toBeGreaterThan(0)
    }
  })
})

describe('ma trận: THIẾU trường bắt buộc', () => {
  it('THIẾU dù caller KHÔNG hề hỏi tới trường đó', () => {
    // Không có tham số "required" nào ở đây. Caller không thể thu hẹp phạm vi.
    const s = surface('obligationSet')
    delete (s as Record<string, unknown>).obligationSetHash
    const r = checkProvenanceCoverage({ obligationSet: s }, ['obligationSet'])
    expect(r.ok).toBe(false)
    expect(r.missing).toContainEqual({ surface: 'obligationSet', field: 'obligationSetHash' })
  })

  it('null cũng là THIẾU, không phải "có mặt"', () => {
    const r = checkProvenanceCoverage(
      { resultRow: surface('resultRow', { payloadHash: null }) },
      ['resultRow'],
    )
    expect(r.ok).toBe(false)
    expect(r.missing).toContainEqual({ surface: 'resultRow', field: 'payloadHash' })
  })

  it('mỗi bề mặt: bỏ từng trường bắt buộc một -> đều bị bắt', () => {
    for (const name of Object.keys(PROVENANCE_MATRIX) as ProvenanceSurfaceName[]) {
      for (const f of PROVENANCE_MATRIX[name].required) {
        const s = surface(name)
        delete (s as Record<string, unknown>)[f]
        const r = checkProvenanceCoverage({ [name]: s }, [name])
        expect(r.ok, `${name}.${f} thiếu mà vẫn ĐẠT`).toBe(false)
        expect(r.missing).toContainEqual({ surface: name, field: f })
      }
    }
  })
})

describe('ma trận: bề mặt VẮNG MẶT', () => {
  it('bề mặt được đòi mà caller không đưa -> hỏng, KHÔNG phải bỏ qua', () => {
    // Ca đã suýt lọt ở vòng trước: test đọc "kết quả gần nhất", không thấy, rồi
    // XANH. Vắng dữ liệu phải là thất bại, vì nếu không thì mọi phép kiểm đều
    // thoả mãn được bằng cách không cung cấp gì.
    const r = checkProvenanceCoverage({ resultRow: surface('resultRow') }, ['resultRow', 'storedMeta'])
    expect(r.ok).toBe(false)
    expect(r.absentSurfaces).toEqual(['storedMeta'])
  })

  it('đủ mọi bề mặt được đòi -> không báo vắng', () => {
    const r = checkProvenanceCoverage(
      { resultRow: surface('resultRow'), storedMeta: surface('storedMeta') },
      ['resultRow', 'storedMeta'],
    )
    expect(r.absentSurfaces).toEqual([])
  })
})

describe('ma trận: trường KHÔNG ÁP DỤNG', () => {
  it('bề mặt mang trường nó không được mang -> hỏng', () => {
    const r = checkProvenanceCoverage(
      { obligationSet: surface('obligationSet', { declarationPromptVersion: '1.0.0' }) },
      ['obligationSet'],
    )
    expect(r.ok).toBe(false)
    expect(r.unexpected).toContainEqual({ surface: 'obligationSet', field: 'declarationPromptVersion' })
  })

  it('dòng kiểm định không được mang băm hợp đồng', () => {
    const r = checkProvenanceCoverage(
      { compositeValidation: surface('compositeValidation', { validatorHash: 'x' }) },
      ['compositeValidation'],
    )
    expect(r.ok).toBe(false)
    expect(r.unexpected).toContainEqual({ surface: 'compositeValidation', field: 'validatorHash' })
  })

  it('lượt PHÂN TÍCH không được mang `analysisExecutionId`', () => {
    const r = checkProvenanceCoverage(
      { analysisExecution: surface('analysisExecution', { analysisExecutionId: 'tự trỏ mình' }) },
      ['analysisExecution'],
    )
    expect(r.ok).toBe(false)
    expect(r.unexpected).toContainEqual({ surface: 'analysisExecution', field: 'analysisExecutionId' })
  })
})

describe('ma trận: quan hệ BẰNG NHAU', () => {
  it('hai bề mặt nói khác nhau về cùng một băm -> hỏng', () => {
    const r = checkProvenanceCoverage(
      {
        obligationSet: surface('obligationSet'),
        resultRow: surface('resultRow', { obligationSetHash: 'BĂM KHÁC' }),
      },
      ['obligationSet', 'resultRow'],
    )
    expect(r.ok).toBe(false)
    expect(r.mismatches.map((m) => m.field)).toContain('obligationSetHash')
  })

  it('một bề mặt duy nhất mang trường -> không phải mâu thuẫn', () => {
    // Không có gì để so thì không kết luận gì. Phần thiếu đã do `missing` lo.
    const r = checkProvenanceCoverage({ obligationSet: surface('obligationSet') }, ['obligationSet'])
    expect(r.mismatches).toEqual([])
    expect(r.ok).toBe(true)
  })

  it('mọi bề mặt khớp nhau -> ĐẠT', () => {
    const r = checkProvenanceCoverage(
      {
        obligationSet: surface('obligationSet'),
        declarationExecution: surface('declarationExecution'),
        resultRow: surface('resultRow'),
        storedMeta: surface('storedMeta'),
        artifactMeta: surface('artifactMeta'),
      },
      ['obligationSet', 'declarationExecution', 'resultRow', 'storedMeta', 'artifactMeta'],
    )
    expect(r.ok, JSON.stringify(r, null, 1)).toBe(true)
  })

  it('phát hiện lệch NGAY CẢ khi chỉ một trong năm bề mặt sai', () => {
    for (const bad of ['obligationSet', 'declarationExecution', 'resultRow', 'storedMeta'] as const) {
      const all = {
        obligationSet: surface('obligationSet'),
        declarationExecution: surface('declarationExecution'),
        resultRow: surface('resultRow'),
        storedMeta: surface('storedMeta'),
      }
      all[bad] = { ...all[bad], analysisPayloadHash: `lệch-${bad}` }
      const r = checkProvenanceCoverage(all, Object.keys(all) as ProvenanceSurfaceName[])
      expect(r.ok, `lệch ở ${bad} mà không bắt được`).toBe(false)
      expect(r.mismatches.map((m) => m.field)).toContain('analysisPayloadHash')
    }
  })
})
