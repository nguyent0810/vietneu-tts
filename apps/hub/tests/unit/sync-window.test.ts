import { describe, expect, it } from 'vitest'

import { LOOKBACK_DAYS, addDays, computeSyncWindow, reportingDateBounds } from '@/lib/sync'

/**
 * Xử lý ngày báo cáo và múi giờ.
 *
 * Đây là chỗ dễ sai âm thầm nhất trong toàn bộ Phase 2: một ngày lệch không làm
 * hỏng chương trình, nó chỉ làm mọi so sánh ở Phase 3 sai đi một chút và không
 * ai nhận ra. Vì thế các test dưới đây cố định `now` thay vì dùng giờ hệ thống.
 */
describe('mốc ngày báo cáo', () => {
  it('tính ngày theo múi giờ của KÊNH, không theo giờ máy chạy', () => {
    // 2026-07-30T05:00:00Z = 2026-07-29 22:00 giờ Los Angeles -> vẫn là ngày 29.
    const at = new Date('2026-07-30T05:00:00Z')
    expect(reportingDateBounds('America/Los_Angeles', at).today).toBe('2026-07-29')
    expect(reportingDateBounds('UTC', at).today).toBe('2026-07-30')
    // Việt Nam đã sang ngày 30 lúc 12:00 trưa.
    expect(reportingDateBounds('Asia/Ho_Chi_Minh', at).today).toBe('2026-07-30')
  })

  it('lùi lại các ngày YouTube chưa chốt số liệu', () => {
    const at = new Date('2026-07-30T20:00:00Z')
    const { today, lastComplete } = reportingDateBounds('America/Los_Angeles', at)
    expect(today).toBe('2026-07-30')
    // Bỏ 2 ngày gần nhất vì YouTube còn sửa.
    expect(lastComplete).toBe('2026-07-28')
  })
})

describe('addDays', () => {
  it('cộng trừ đúng qua ranh giới tháng và năm', () => {
    expect(addDays('2026-07-31', 1)).toBe('2026-08-01')
    expect(addDays('2026-01-01', -1)).toBe('2025-12-31')
    expect(addDays('2026-03-01', -1)).toBe('2026-02-28')
    expect(addDays('2028-03-01', -1)).toBe('2028-02-29') // năm nhuận
  })

  it('không bị lệch do múi giờ của máy chạy', () => {
    // Phép toán trên NHÃN NGÀY, không phải trên thời điểm: cộng 0 phải bất biến.
    for (const d of ['2026-01-01', '2026-06-15', '2026-12-31']) {
      expect(addDays(d, 0)).toBe(d)
    }
  })
})

describe('computeSyncWindow', () => {
  const now = new Date('2026-07-30T20:00:00Z') // = 2026-07-30 tại Los Angeles

  it('lần chạy đầu (chưa có checkpoint) lùi đúng initialDays', () => {
    const w = computeSyncWindow({
      timezone: 'America/Los_Angeles',
      lastCompleteDate: null,
      initialDays: 90,
      now,
    })
    expect(w.to).toBe('2026-07-28')
    expect(w.from).toBe(addDays('2026-07-28', -90))
  })

  it('có checkpoint thì lấy lại một cửa sổ lùi, không lấy từ checkpoint trở đi', () => {
    // Nếu chỉ lấy từ checkpoint trở đi thì mọi chỉnh sửa muộn của YouTube
    // (48-72h) sẽ không bao giờ vào database.
    const w = computeSyncWindow({
      timezone: 'America/Los_Angeles',
      lastCompleteDate: '2026-07-20',
      initialDays: 90,
      now,
    })
    expect(w.from).toBe(addDays('2026-07-20', -LOOKBACK_DAYS))
    expect(w.to).toBe('2026-07-28')
  })

  it('không bao giờ lấy quá mốc ổn định, kể cả khi checkpoint đã vượt lên', () => {
    const w = computeSyncWindow({
      timezone: 'America/Los_Angeles',
      lastCompleteDate: '2026-12-31',
      initialDays: 90,
      now,
    })
    expect(w.to).toBe('2026-07-28')
    expect(w.from <= w.to).toBe(true)
  })

  it('cửa sổ luôn hợp lệ (from <= to) với mọi checkpoint', () => {
    for (const cp of [null, '2020-01-01', '2026-07-27', '2026-07-28', '2030-01-01']) {
      const w = computeSyncWindow({
        timezone: 'America/Los_Angeles',
        lastCompleteDate: cp,
        initialDays: 30,
        now,
      })
      expect(w.from <= w.to, `checkpoint=${cp}`).toBe(true)
    }
  })
})
