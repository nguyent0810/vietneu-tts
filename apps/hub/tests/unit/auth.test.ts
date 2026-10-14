import { describe, expect, it } from 'vitest'

import {
  USER_TOKEN_PREFIX,
  WORKER_TOKEN_PREFIX,
  assertCanApprove,
  constantTimeEqualHex,
  extractBearer,
  generateToken,
  hashToken,
  requireCapability,
  requireScope,
  type UserPrincipal,
  type WorkerPrincipal,
} from '@/lib/auth'
import { ApiError } from '@/lib/errors'

const userPrincipal = (scopes: UserPrincipal['scopes']): UserPrincipal => ({
  kind: 'USER',
  userId: 'u1',
  workspaceId: 'w1',
  tokenId: 't1',
  scopes,
})

const workerPrincipal = (caps: WorkerPrincipal['capabilities']): WorkerPrincipal => ({
  kind: 'WORKER',
  machineId: 'm1',
  workspaceId: 'w1',
  machineLabel: 'mac-mini',
  capabilities: caps,
})

describe('sinh và băm token', () => {
  it('token người dùng và worker có tiền tố khác nhau', () => {
    expect(generateToken('USER').token.startsWith(USER_TOKEN_PREFIX)).toBe(true)
    expect(generateToken('WORKER').token.startsWith(WORKER_TOKEN_PREFIX)).toBe(true)
  })

  it('mỗi lần sinh ra token khác nhau', () => {
    const tokens = new Set(Array.from({ length: 50 }, () => generateToken('USER').token))
    expect(tokens.size).toBe(50)
  })

  it('hash là sha256 hex và ổn định', () => {
    const { token, hash } = generateToken('USER')
    expect(hash).toMatch(/^[0-9a-f]{64}$/)
    expect(hashToken(token)).toBe(hash)
  })

  it('prefix lưu để hiển thị không đủ để dựng lại token', () => {
    const { token, prefix } = generateToken('WORKER')
    expect(token.startsWith(prefix)).toBe(true)
    expect(prefix.length).toBeLessThan(token.length / 2)
  })
})

describe('constantTimeEqualHex', () => {
  it('đúng với hai hash giống nhau', () => {
    const h = hashToken('abc')
    expect(constantTimeEqualHex(h, h)).toBe(true)
  })

  it('sai với hash khác nhau', () => {
    expect(constantTimeEqualHex(hashToken('a'), hashToken('b'))).toBe(false)
  })

  it('sai (không ném lỗi) với đầu vào không phải hex hoặc lệch độ dài', () => {
    expect(constantTimeEqualHex('abc', 'abcd')).toBe(false)
    // Regression: Buffer.from('zz','hex') trả buffer RỖNG chứ không ném lỗi,
    // nên nếu không kiểm định dạng trước thì hai chuỗi rác này sẽ "bằng nhau".
    expect(constantTimeEqualHex('z'.repeat(64), 'z'.repeat(64))).toBe(false)
    expect(constantTimeEqualHex('', '')).toBe(false)
    // Đúng độ dài 64 nhưng có ký tự ngoài hex.
    expect(constantTimeEqualHex('g'.repeat(64), 'g'.repeat(64))).toBe(false)
  })
})

describe('extractBearer', () => {
  it('lấy được token', () => {
    expect(extractBearer('Bearer vhu_abc')).toBe('vhu_abc')
    expect(extractBearer('bearer vhu_abc')).toBe('vhu_abc')
  })

  it('từ chối header thiếu hoặc sai định dạng', () => {
    for (const bad of [null, '', 'vhu_abc', 'Basic abc', 'Bearer', 'Bearer  a b']) {
      expect(() => extractBearer(bad)).toThrow(ApiError)
    }
  })
})

describe('scope người dùng', () => {
  it('cho qua khi có đúng scope', () => {
    expect(() => requireScope(userPrincipal(['READ']), 'READ')).not.toThrow()
  })

  it('ADMIN bao trùm mọi scope', () => {
    expect(() => requireScope(userPrincipal(['ADMIN']), 'APPROVE')).not.toThrow()
  })

  it('chặn khi thiếu scope', () => {
    try {
      requireScope(userPrincipal(['READ']), 'WRITE')
      throw new Error('phải ném lỗi')
    } catch (err) {
      expect((err as ApiError).code).toBe('INSUFFICIENT_SCOPE')
      expect((err as ApiError).status).toBe(403)
    }
  })
})

describe('capability của worker', () => {
  it('cho qua khi được cấp', () => {
    expect(() => requireCapability(workerPrincipal(['SYNC_ANALYTICS']), 'SYNC_ANALYTICS')).not.toThrow()
  })

  it('chặn khi không được cấp', () => {
    try {
      requireCapability(workerPrincipal(['SYNC_ANALYTICS']), 'RUN_LLM_ANALYSIS')
      throw new Error('phải ném lỗi')
    } catch (err) {
      expect((err as ApiError).code).toBe('CAPABILITY_NOT_GRANTED')
    }
  })

  it('worker KHÔNG có khái niệm scope kiểu người dùng', () => {
    // capabilities và scopes là hai không gian tên tách biệt; một worker không
    // thể nào mang scope APPROVE.
    const worker = workerPrincipal(['ANALYZE_CONTENT'])
    expect(Object.hasOwn(worker, 'scopes')).toBe(false)
  })
})

describe('chỉ người dùng mới được phê duyệt', () => {
  it('chặn worker phê duyệt', () => {
    try {
      assertCanApprove(workerPrincipal(['ANALYZE_CONTENT']))
      throw new Error('phải ném lỗi')
    } catch (err) {
      expect((err as ApiError).code).toBe('WORKER_CANNOT_APPROVE')
      expect((err as ApiError).status).toBe(403)
    }
  })

  it('chặn người dùng thiếu scope APPROVE', () => {
    try {
      assertCanApprove(userPrincipal(['READ', 'WRITE']))
      throw new Error('phải ném lỗi')
    } catch (err) {
      expect((err as ApiError).code).toBe('INSUFFICIENT_SCOPE')
    }
  })

  it('cho qua người dùng có scope APPROVE', () => {
    expect(() => assertCanApprove(userPrincipal(['APPROVE']))).not.toThrow()
  })
})
