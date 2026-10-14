import { describe, expect, it } from 'vitest'

import {
  MAD_TO_SIGMA,
  deltaRatio,
  describe as describeDist,
  mad,
  median,
  modifiedZScore,
  percentileRank,
  quantile,
  round,
  safeDivide,
} from '@/lib/analysis/stats'

describe('median / quantile', () => {
  it('trung vị đúng cho mẫu lẻ và chẵn', () => {
    expect(median([3, 1, 2])).toBe(2)
    expect(median([4, 1, 2, 3])).toBe(2.5)
    expect(median([])).toBeNull()
  })

  it('phân vị dùng nội suy tuyến tính (kiểu 7 của R)', () => {
    const v = [1, 2, 3, 4]
    expect(quantile(v, 0.5)).toBe(2.5)
    expect(quantile(v, 0.25)).toBe(1.75)
    expect(quantile(v, 0.75)).toBe(3.25)
  })

  it('không sửa mảng đầu vào', () => {
    const input = [5, 1, 3]
    median(input)
    quantile(input, 0.5)
    expect(input).toEqual([5, 1, 3])
  })
})

describe('MAD và z hiệu chỉnh', () => {
  it('bền với outlier — nơi mean/stddev thất bại', () => {
    // 9 giá trị quanh 10, một giá trị 1000. Với mean/stddev, z của 1000 chỉ
    // khoảng 2.8 (dưới ngưỡng 3.5) vì chính nó kéo cả mean lẫn stddev lên.
    const values = [10, 11, 9, 10, 12, 8, 10, 11, 9, 1000]
    const z = modifiedZScore(1000, values)
    expect(z).not.toBeNull()
    expect(z!).toBeGreaterThan(3.5)

    const mean = values.reduce((a, b) => a + b, 0) / values.length
    const sd = Math.sqrt(values.reduce((s, v) => s + (v - mean) ** 2, 0) / values.length)
    const classicZ = (1000 - mean) / sd
    expect(classicZ, 'z cổ điển bỏ sót chính outlier đã bẻ cong nó').toBeLessThan(3.5)
  })

  it('rơi về IQR khi MAD = 0', () => {
    // Quá nửa giá trị bằng nhau -> MAD = 0 -> công thức chuẩn chia cho 0.
    const values = [0, 0, 0, 0, 0, 0, 1, 2, 50]
    expect(mad(values)).toBe(0)
    const z = modifiedZScore(50, values)
    expect(z).not.toBeNull()
    expect(Number.isFinite(z!)).toBe(true)
  })

  it('trả null (không phải Infinity) khi phân tán thực sự bằng 0', () => {
    expect(modifiedZScore(5, [5, 5, 5, 5, 5])).toBeNull()
  })

  it('hằng số quy đổi đúng chuẩn', () => {
    expect(MAD_TO_SIGMA).toBeCloseTo(1 / 0.6745, 3)
  })
})

describe('percentileRank', () => {
  it('giá trị TRÙNG nhau nhận CÙNG một phân vị (midrank)', () => {
    // Không có midrank, thứ tự chèn quyết định ai đứng trên ai -> mất tất định.
    const values = [0, 0, 0, 10]
    expect(percentileRank(0, values)).toBe(percentileRank(0, values))
    expect(percentileRank(0, values)).toBe(37.5)
    expect(percentileRank(10, values)).toBe(87.5)
  })

  it('không phụ thuộc thứ tự đầu vào', () => {
    const a = percentileRank(3, [1, 2, 3, 4, 5])
    const b = percentileRank(3, [5, 4, 3, 2, 1])
    expect(a).toBe(b)
  })

  it('mảng rỗng trả null', () => {
    expect(percentileRank(1, [])).toBeNull()
  })
})

describe('phép chia và làm tròn an toàn', () => {
  it('không bao giờ trả Infinity hay NaN', () => {
    expect(safeDivide(1, 0)).toBeNull()
    expect(safeDivide(null, 5)).toBeNull()
    expect(safeDivide(Number.POSITIVE_INFINITY, 2)).toBeNull()
    expect(safeDivide(10, 4)).toBe(2.5)
  })

  it('làm tròn khử nhiễu dấu phẩy động (giữ hash ổn định)', () => {
    expect(round(0.1 + 0.2)).toBe(0.3)
    expect(round(null)).toBeNull()
    expect(round(Number.NaN)).toBeNull()
  })

  it('khử -0 vì JSON.stringify in ra "-0" và làm lệch hash', () => {
    expect(Object.is(round(-0), -0)).toBe(false)
    expect(JSON.stringify(round(-0))).toBe('0')
  })

  it('deltaRatio xử lý được baseline âm và bằng 0', () => {
    expect(deltaRatio(150, 100)).toBe(0.5)
    expect(deltaRatio(50, 100)).toBe(-0.5)
    expect(deltaRatio(5, 0)).toBeNull()
    // Chuẩn hoá theo |baseline| nên dấu của delta luôn nói đúng hướng.
    expect(deltaRatio(-5, -10)).toBe(0.5)
  })
})

describe('describe()', () => {
  it('tóm tắt phân phối bằng thống kê bền', () => {
    const d = describeDist([1, 2, 3, 4, 100])
    expect(d.count).toBe(5)
    expect(d.median).toBe(3)
    expect(d.max).toBe(100)
    expect(d.mad).not.toBeNull()
  })

  it('mảng rỗng không làm vỡ', () => {
    const d = describeDist([])
    expect(d.count).toBe(0)
    expect(d.median).toBeNull()
    expect(d.min).toBeNull()
  })
})
