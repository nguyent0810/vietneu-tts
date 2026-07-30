import { describe, expect, it } from 'vitest'
import { z } from 'zod'

import {
  ApiError,
  ErrorCode,
  fromDatabaseError,
  fromZodError,
  statusForCode,
  toApiError,
} from '@/lib/errors'

describe('bảng phân loại lỗi', () => {
  it('mọi mã lỗi đều có HTTP status', () => {
    for (const code of Object.values(ErrorCode)) {
      const status = statusForCode(code)
      expect(status, `thiếu status cho ${code}`).toBeGreaterThanOrEqual(400)
      expect(status).toBeLessThan(600)
    }
  })

  it('mã lỗi và tên hằng trùng nhau (tránh lệch âm thầm)', () => {
    for (const [name, value] of Object.entries(ErrorCode)) {
      expect(value).toBe(name)
    }
  })

  it('ApiError sinh body đúng hình dạng hợp đồng', () => {
    const err = new ApiError(ErrorCode.NOT_FOUND, 'Không thấy.')
    const body = err.toBody('req-1')
    expect(body.error.code).toBe('NOT_FOUND')
    expect(body.error.requestId).toBe('req-1')
    expect(err.status).toBe(404)
  })
})

describe('fromZodError', () => {
  const schema = z.object({ name: z.string(), age: z.number() }).strict()

  it('trả VALIDATION_FAILED kèm đường dẫn trường lỗi', () => {
    const result = schema.safeParse({ name: 123, age: 'x' })
    expect(result.success).toBe(false)
    const err = fromZodError(result.error!)
    expect(err.code).toBe('VALIDATION_FAILED')
    expect(err.status).toBe(400)
    const details = err.details as Array<{ path: string }>
    expect(details.map((d) => d.path).sort()).toEqual(['age', 'name'])
  })

  it('KHÔNG vọng lại giá trị người dùng gửi lên', () => {
    // Nếu details chứa giá trị đầu vào thì một request mang token sẽ bị ghi
    // thẳng vào log lỗi -- đây chính là điều phải tránh.
    const secret = 'vhu_supersecrettokenvalue'
    const result = schema.safeParse({ name: secret, age: secret })
    const err = fromZodError(result.error!)
    expect(JSON.stringify(err.details)).not.toContain(secret)
  })

  it('.strict() bắt được trường thừa', () => {
    const result = schema.safeParse({ name: 'a', age: 1, extra: true })
    expect(result.success).toBe(false)
    expect(fromZodError(result.error!).code).toBe('VALIDATION_FAILED')
  })
})

describe('fromDatabaseError', () => {
  it('ánh xạ trùng run_sequence sang DUPLICATE_RUN_SEQUENCE', () => {
    const err = fromDatabaseError({ code: '23505', constraint: 'analysis_run_sequence_key' })
    expect(err.code).toBe('DUPLICATE_RUN_SEQUENCE')
    expect(err.status).toBe(409)
  })

  it('ánh xạ giới hạn 3 vòng lặp sang ITERATION_LIMIT_REACHED', () => {
    const err = fromDatabaseError({ code: '23514', constraint: 'llm_execution_iteration_bounds' })
    expect(err.code).toBe('ITERATION_LIMIT_REACHED')
  })

  it('ánh xạ chặn agent phê duyệt sang WORKER_CANNOT_APPROVE', () => {
    const err = fromDatabaseError({ code: '23514', constraint: 'approval_decider_must_be_human' })
    expect(err.code).toBe('WORKER_CANNOT_APPROVE')
    expect(err.status).toBe(403)
  })

  it('ánh xạ trigger bất biến sang REVISION_FROZEN', () => {
    const err = fromDatabaseError({
      code: 'P0001',
      message: 'IMMUTABLE_CONTENT_REVISION: revision abc da FROZEN',
    })
    expect(err.code).toBe('REVISION_FROZEN')
  })

  it('lỗi lạ trả INTERNAL chứ không rò chi tiết', () => {
    const err = fromDatabaseError({ code: '42P01', message: 'relation "secret_table" does not exist' })
    expect(err.code).toBe('INTERNAL')
    expect(err.message).not.toContain('secret_table')
  })
})

describe('toApiError', () => {
  it('giữ nguyên ApiError sẵn có', () => {
    const original = new ApiError(ErrorCode.RATE_LIMITED, 'chậm lại', { retryAfterSeconds: 5 })
    expect(toApiError(original)).toBe(original)
  })

  it('chuyển ZodError', () => {
    const result = z.string().safeParse(1)
    expect(toApiError(result.error!).code).toBe('VALIDATION_FAILED')
  })

  it('lỗi không rõ nguồn gốc trả INTERNAL', () => {
    expect(toApiError(new Error('bùm')).code).toBe('INTERNAL')
    expect(toApiError('chuỗi thô').code).toBe('INTERNAL')
  })
})
