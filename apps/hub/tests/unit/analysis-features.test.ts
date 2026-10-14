import { describe, expect, it } from 'vitest'

import { ANALYSIS_THRESHOLDS, comparisonFormat, durationBucket, publishHourBucket } from '@/lib/analysis/config'
import {
  confidenceScore,
  metricCoverageScore,
  metricsInAgeWindow,
  percentileFeature,
  performanceStability,
  ratePerThousand,
  videoAgeDays,
  weightedFeature,
  windowSum,
  type DailyMetric,
  type VideoInput,
} from '@/lib/analysis/compute'
import { CAUSAL_MARKERS, containsCausalClaim, makeOrderKey } from '@/lib/analysis/observations'
import { FEATURE_SPECS } from '@/lib/analysis/features'

function metric(date: string, over: Partial<DailyMetric> = {}): DailyMetric {
  return {
    date,
    views: null,
    estimatedMinutesWatched: null,
    averageViewDurationSeconds: null,
    averageViewPercentage: null,
    impressions: null,
    impressionCtr: null,
    likes: null,
    dislikes: null,
    comments: null,
    shares: null,
    subscribersGained: null,
    subscribersLost: null,
    ...over,
  }
}

function video(over: Partial<VideoInput> = {}): VideoInput {
  return {
    id: 'v1',
    youtubeVideoId: 'aaaaaaaaaaa',
    title: 'T',
    publishedAt: '2026-07-01T00:00:00Z',
    publishDate: '2026-07-01',
    publishedHourLocal: 9,
    publishedWeekdayLocal: 3,
    durationSeconds: 45,
    format: 'SHORT',
    metrics: [],
    ...over,
  }
}

describe('chuẩn hoá theo tuổi video', () => {
  it('cửa sổ N ngày tính TỪ NGÀY ĐĂNG, không phải từ ngày lịch', () => {
    const v = video({
      publishDate: '2026-07-01',
      metrics: [
        metric('2026-06-30', { views: 999 }), // trước khi đăng -> loại
        metric('2026-07-01', { views: 10 }),
        metric('2026-07-07', { views: 20 }),
        metric('2026-07-08', { views: 40 }), // ngoài cửa sổ 7 ngày
      ],
    })
    const rows = metricsInAgeWindow(v, 7)
    expect(rows.map((r) => r.date)).toEqual(['2026-07-01', '2026-07-07'])
  })

  it('video CHƯA đủ tuổi trả INSUFFICIENT_AGE, KHÔNG trả 0', () => {
    // Gán 0 sẽ kéo trung vị kênh xuống và làm mọi video mới trông như thất bại.
    const v = video({
      publishDate: '2026-07-25',
      metrics: [metric('2026-07-25', { views: 100 })],
    })
    const r = windowSum(v, 7, 'views', '2026-07-27')
    expect(r.value).toBeUndefined()
    expect(r.missing).toBe('INSUFFICIENT_AGE')
  })

  it('video đủ tuổi thì cộng đúng', () => {
    const v = video({
      publishDate: '2026-07-01',
      metrics: [
        metric('2026-07-01', { views: 100 }),
        metric('2026-07-02', { views: 50 }),
      ],
    })
    const r = windowSum(v, 7, 'views', '2026-07-27')
    expect(r.value).toBe(150)
  })

  it('có hàng nhưng chỉ số vắng mặt -> METRIC_NOT_PROVIDED', () => {
    const v = video({
      publishDate: '2026-07-01',
      metrics: [metric('2026-07-01', { views: null })],
    })
    expect(windowSum(v, 7, 'views', '2026-07-27').missing).toBe('METRIC_NOT_PROVIDED')
  })

  it('không có hàng nào -> NO_METRIC_ROWS', () => {
    const v = video({ publishDate: '2026-07-01', metrics: [] })
    expect(windowSum(v, 7, 'views', '2026-07-27').missing).toBe('NO_METRIC_ROWS')
  })

  it('tuổi video tính theo nhãn ngày', () => {
    expect(videoAgeDays(video({ publishDate: '2026-07-01' }), '2026-07-08')).toBe(7)
  })
})

describe('tách Shorts và Long-form', () => {
  it('suy từ thời lượng, không tin nhãn đã lưu', () => {
    expect(comparisonFormat(45, 'UNKNOWN')).toBe('SHORT')
    expect(comparisonFormat(180, 'UNKNOWN')).toBe('SHORT')
    expect(comparisonFormat(181, 'SHORT')).toBe('LONG_FORM')
    expect(comparisonFormat(600, 'UNKNOWN')).toBe('LONG_FORM')
  })

  it('không có thời lượng thì mới dùng nhãn đã lưu', () => {
    expect(comparisonFormat(null, 'SHORT')).toBe('SHORT')
    expect(comparisonFormat(null, 'UNKNOWN')).toBe('UNKNOWN')
  })

  it('nhóm thời lượng khớp ranh giới Shorts', () => {
    expect(durationBucket(20)).toBe('ultra_short')
    expect(durationBucket(60)).toBe('short')
    expect(durationBucket(180)).toBe('long_short')
    expect(durationBucket(500)).toBe('mid_form')
    expect(durationBucket(5000)).toBe('long_form')
    expect(durationBucket(null)).toBeNull()
  })

  it('nhóm giờ đăng phủ kín 24 giờ', () => {
    for (let h = 0; h < 24; h++) expect(publishHourBucket(h)).not.toBeNull()
    expect(publishHourBucket(null)).toBeNull()
  })
})

describe('dữ liệu thật gây bất ngờ vẫn phải xử lý được', () => {
  it('phần trăm xem VƯỢT 100 được giữ nguyên (người xem tua lại)', () => {
    const v = video({
      metrics: [
        metric('2026-07-01', { views: 100, averageViewPercentage: 143.7 }),
        metric('2026-07-02', { views: 100, averageViewPercentage: 120 }),
      ],
    })
    const r = weightedFeature(v, 'averageViewPercentage')
    expect(r.value).toBeCloseTo(131.85, 2)
  })

  it('chỉ số ÂM (đăng ký ròng) giữ nguyên dấu', () => {
    const v = video({
      metrics: [
        metric('2026-07-01', { views: 1000, subscribersGained: 1, subscribersLost: 6 }),
      ],
    })
    const r = ratePerThousand(v, 'subscribersGained', '2026-07-27', 'subscribersLost')
    expect(r.value).toBe(-5)
  })

  it('trung bình có TRỌNG SỐ theo lượt xem, không phải trung bình đơn giản', () => {
    const v = video({
      metrics: [
        metric('2026-07-01', { views: 1000, averageViewPercentage: 90 }),
        metric('2026-07-02', { views: 1, averageViewPercentage: 10 }),
      ],
    })
    // Trung bình đơn giản = 50, sai hoàn toàn: ngày 1 view không thể nặng bằng
    // ngày 1000 view.
    const r = weightedFeature(v, 'averageViewPercentage')
    expect(r.value).toBeGreaterThan(89)
  })

  it('views = 0 là DỮ LIỆU THẬT, khác hẳn thiếu dữ liệu', () => {
    const v = video({
      publishDate: '2026-07-01',
      metrics: [metric('2026-07-01', { views: 0 })],
    })
    const r = windowSum(v, 1, 'views', '2026-07-27')
    expect(r.value).toBe(0)
    expect(r.missing).toBeUndefined()
  })

  it('mẫu số bằng 0 -> DIVISION_BY_ZERO, không phải Infinity', () => {
    const v = video({
      metrics: [metric('2026-07-01', { views: 0, likes: 5 })],
    })
    expect(ratePerThousand(v, 'likes', '2026-07-27').missing).toBe('DIVISION_BY_ZERO')
  })
})

describe('ngưỡng lượng mẫu', () => {
  it('phân vị cần tối thiểu N phần tử', () => {
    const small = [1, 2, 3]
    expect(percentileFeature(2, small).missing).toBe('INSUFFICIENT_SAMPLE')
    const ok = [1, 2, 3, 4, 5]
    expect(percentileFeature(3, ok).value).not.toBeUndefined()
  })

  it('độ ổn định cần tối thiểu 3 điểm', () => {
    const v = video({ metrics: [metric('2026-07-01', { views: 10 })] })
    expect(performanceStability(v).missing).toBe('INSUFFICIENT_SAMPLE')
  })
})

describe('điểm tin cậy', () => {
  it('nằm trong [0,1] và tăng theo độ đầy đủ dữ liệu', () => {
    const sparse = video({
      publishDate: '2026-07-26',
      metrics: [metric('2026-07-26', { views: 5 })],
    })
    const rich = video({
      publishDate: '2026-06-01',
      metrics: Array.from({ length: 20 }, (_, i) =>
        metric(`2026-06-${String(i + 1).padStart(2, '0')}`, {
          views: 100,
          estimatedMinutesWatched: 50,
          averageViewDurationSeconds: 30,
          averageViewPercentage: 60,
          likes: 5,
          comments: 1,
          shares: 1,
          subscribersGained: 1,
          subscribersLost: 0,
        }),
      ),
    })
    const a = confidenceScore(sparse, '2026-07-27').value!
    const b = confidenceScore(rich, '2026-07-27').value!
    expect(a).toBeGreaterThanOrEqual(0)
    expect(b).toBeLessThanOrEqual(1)
    expect(b).toBeGreaterThan(a)
  })

  it('độ phủ chỉ số phản ánh chỉ số nào thực sự có', () => {
    const v = video({ metrics: [metric('2026-07-01', { views: 1, likes: 1 })] })
    const r = metricCoverageScore(v)
    expect(r.value).toBeGreaterThan(0)
    expect(r.value).toBeLessThan(1)
  })
})

describe('tầng tất định KHÔNG được tuyên bố nhân quả', () => {
  it('bộ dò từ ngữ nhân quả hoạt động ở cả hai ngôn ngữ', () => {
    expect(containsCausalClaim('Lượt xem giảm vì tiêu đề yếu')).toBe(true)
    expect(containsCausalClaim('Thumbnail caused the drop')).toBe(true)
    expect(containsCausalClaim('Video X ở phân vị 92 về lượt xem 7 ngày')).toBe(false)
  })

  it('danh sách marker không rỗng và toàn chữ thường', () => {
    expect(CAUSAL_MARKERS.length).toBeGreaterThan(5)
    for (const m of CAUSAL_MARKERS) expect(m).toBe(m.toLowerCase())
  })
})

describe('khoá sắp xếp ổn định', () => {
  it('điểm cao đứng trước khi sắp theo chuỗi', () => {
    const high = makeOrderKey('X', 95, 'aaa')
    const low = makeOrderKey('X', 10, 'bbb')
    expect([low, high].sort()[0]).toBe(high)
  })

  it('điểm bằng nhau thì phá hoà TẤT ĐỊNH bằng id', () => {
    const a = makeOrderKey('X', 50, 'aaa')
    const b = makeOrderKey('X', 50, 'bbb')
    expect(a).not.toBe(b)
    expect([b, a].sort()).toEqual([a, b])
  })
})

describe('danh mục feature', () => {
  it('khoá là duy nhất và đúng định dạng', () => {
    const keys = FEATURE_SPECS.map((f) => f.key)
    expect(new Set(keys).size).toBe(keys.length)
    for (const k of keys) expect(k).toMatch(/^[a-z][a-z0-9_]{2,63}$/)
  })

  it('mọi feature đều có công thức và phiên bản', () => {
    for (const f of FEATURE_SPECS) {
      expect(f.formula.length, `${f.key} thiếu công thức`).toBeGreaterThan(5)
      expect(f.version).toMatch(/^\d+\.\d+\.\d+$/)
    }
  })

  it('phủ hết các nhóm feature đề bài yêu cầu', () => {
    const keys = new Set(FEATURE_SPECS.map((f) => f.key))
    for (const required of [
      'publish_hour_local',
      'publish_weekday',
      'video_age_days',
      'duration_seconds',
      'views_velocity_d7',
      'watch_velocity_d7',
      'subscriber_conversion_per_1k',
      'like_rate_per_1k',
      'comment_rate_per_1k',
      'avg_view_duration_seconds',
      'avg_view_percentage',
      'impressions_total',
      'impression_ctr',
      'views_d1',
      'views_d7',
      'views_d14',
      'views_d30',
      'channel_percentile_views_d7',
      'cohort_percentile_views_d7',
      'recent_baseline_delta_views_d7',
      'mature_baseline_delta_views_d7',
      'upload_frequency_per_week',
      'gap_since_previous_upload_days',
      'performance_stability',
      'anomaly_score_views_d7',
      'metric_coverage_score',
      'confidence_score',
    ]) {
      expect(keys.has(required), `thiếu feature ${required}`).toBe(true)
    }
  })

  it('ngưỡng có cơ sở, không phải số tuỳ tiện', () => {
    expect(ANALYSIS_THRESHOLDS.anomalyZThreshold).toBe(3.5) // Iglewicz–Hoaglin
    expect(ANALYSIS_THRESHOLDS.minSampleForPercentile).toBeGreaterThanOrEqual(5)
    const w = ANALYSIS_THRESHOLDS.confidenceWeights
    expect(w.metricCoverage + w.dateCompleteness + w.sampleSize + w.maturity).toBeCloseTo(1, 6)
  })
})
