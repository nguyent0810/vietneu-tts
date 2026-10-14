import { createHash, randomBytes, timingSafeEqual } from 'node:crypto'

import { and, eq, isNull, or, gt } from 'drizzle-orm'

import { getDb } from '@/db/client'
import { userAccount, userApiToken, workerMachine } from '@/db/schema'
import { ApiError, ErrorCode } from './errors'

/**
 * Hai đường xác thực TÁCH BIỆT — người dùng và máy worker — cố ý không gộp.
 *
 * Định dạng token: `<prefix>_<32 byte base64url>`
 *   vhu_...  token người dùng
 *   vhw_...  token worker
 *
 * Tiền tố khác nhau nghĩa là một token worker gửi vào endpoint người dùng bị
 * loại ngay từ hình dạng, trước cả khi tra database.
 */

export const USER_TOKEN_PREFIX = 'vhu_'
export const WORKER_TOKEN_PREFIX = 'vhw_'

export type TokenScope = 'READ' | 'WRITE' | 'APPROVE' | 'ADMIN'
export type WorkerCapability =
  | 'ANALYZE_CONTENT'
  | 'SCORE_CONTENT'
  | 'IMPROVE_CONTENT'
  | 'SYNC_ANALYTICS'
  | 'RUN_LLM_ANALYSIS'

export interface UserPrincipal {
  kind: 'USER'
  userId: string
  workspaceId: string
  tokenId: string
  scopes: TokenScope[]
}

export interface WorkerPrincipal {
  kind: 'WORKER'
  machineId: string
  workspaceId: string
  machineLabel: string
  capabilities: WorkerCapability[]
}

export type Principal = UserPrincipal | WorkerPrincipal

export function hashToken(token: string): string {
  return createHash('sha256').update(token, 'utf8').digest('hex')
}

export function generateToken(kind: 'USER' | 'WORKER'): { token: string; hash: string; prefix: string } {
  const prefix = kind === 'USER' ? USER_TOKEN_PREFIX : WORKER_TOKEN_PREFIX
  const token = prefix + randomBytes(32).toString('base64url')
  return { token, hash: hashToken(token), prefix: token.slice(0, 12) }
}

/**
 * So sánh hai hash hex ở thời gian không đổi.
 *
 * Việc tra cứu chính đã dùng chỉ mục UNIQUE trên `token_hash` (không rò thời
 * gian theo nội dung), nhưng mọi so sánh còn lại vẫn dùng hàm này để không ai
 * vô tình thêm một phép `===` rò thời gian về sau.
 */
const HEX64 = /^[0-9a-f]{64}$/

export function constantTimeEqualHex(a: string, b: string): boolean {
  // Bắt buộc kiểm định dạng TRƯỚC: `Buffer.from('zz', 'hex')` trả về buffer
  // RỖNG chứ không ném lỗi, nên hai chuỗi không phải hex cùng độ dài sẽ được
  // timingSafeEqual coi là BẰNG NHAU. Đây là kiểu lỗi im lặng đúng nghĩa.
  if (!HEX64.test(a) || !HEX64.test(b)) return false
  return timingSafeEqual(Buffer.from(a, 'hex'), Buffer.from(b, 'hex'))
}

export function extractBearer(header: string | null): string {
  if (!header) {
    throw new ApiError(ErrorCode.UNAUTHENTICATED, 'Thiếu header Authorization.')
  }
  const match = /^Bearer\s+(\S+)$/i.exec(header.trim())
  if (!match?.[1]) {
    throw new ApiError(ErrorCode.UNAUTHENTICATED, 'Header Authorization phải có dạng "Bearer <token>".')
  }
  return match[1]
}

export async function authenticateUser(header: string | null): Promise<UserPrincipal> {
  const token = extractBearer(header)
  if (!token.startsWith(USER_TOKEN_PREFIX)) {
    throw new ApiError(ErrorCode.UNAUTHENTICATED, 'Token không phải token người dùng.')
  }

  const rows = await getDb()
    .select({
      tokenId: userApiToken.id,
      tokenHash: userApiToken.tokenHash,
      scopes: userApiToken.scopes,
      expiresAt: userApiToken.expiresAt,
      revokedAt: userApiToken.revokedAt,
      userId: userAccount.id,
      workspaceId: userAccount.workspaceId,
      disabledAt: userAccount.disabledAt,
    })
    .from(userApiToken)
    .innerJoin(userAccount, eq(userApiToken.userId, userAccount.id))
    .where(eq(userApiToken.tokenHash, hashToken(token)))
    .limit(1)

  const row = rows[0]
  if (!row || !constantTimeEqualHex(row.tokenHash, hashToken(token))) {
    throw new ApiError(ErrorCode.UNAUTHENTICATED, 'Token không hợp lệ.')
  }
  if (row.revokedAt) {
    throw new ApiError(ErrorCode.TOKEN_REVOKED, 'Token đã bị thu hồi.')
  }
  if (row.expiresAt && row.expiresAt.getTime() <= Date.now()) {
    throw new ApiError(ErrorCode.TOKEN_EXPIRED, 'Token đã hết hạn.')
  }
  if (row.disabledAt) {
    throw new ApiError(ErrorCode.UNAUTHENTICATED, 'Tài khoản đã bị vô hiệu hoá.')
  }

  return {
    kind: 'USER',
    userId: row.userId,
    workspaceId: row.workspaceId,
    tokenId: row.tokenId,
    scopes: row.scopes as TokenScope[],
  }
}

export async function authenticateWorker(header: string | null): Promise<WorkerPrincipal> {
  const token = extractBearer(header)
  if (!token.startsWith(WORKER_TOKEN_PREFIX)) {
    throw new ApiError(ErrorCode.UNAUTHENTICATED, 'Token không phải token worker.')
  }

  const rows = await getDb()
    .select({
      id: workerMachine.id,
      workspaceId: workerMachine.workspaceId,
      machineLabel: workerMachine.machineLabel,
      tokenHash: workerMachine.tokenHash,
      capabilities: workerMachine.capabilities,
      revokedAt: workerMachine.revokedAt,
    })
    .from(workerMachine)
    .where(eq(workerMachine.tokenHash, hashToken(token)))
    .limit(1)

  const row = rows[0]
  if (!row || !constantTimeEqualHex(row.tokenHash, hashToken(token))) {
    throw new ApiError(ErrorCode.UNAUTHENTICATED, 'Token không hợp lệ.')
  }
  if (row.revokedAt) {
    throw new ApiError(ErrorCode.TOKEN_REVOKED, 'Máy worker đã bị thu hồi quyền.')
  }

  return {
    kind: 'WORKER',
    machineId: row.id,
    workspaceId: row.workspaceId,
    machineLabel: row.machineLabel,
    capabilities: row.capabilities as WorkerCapability[],
  }
}

export function requireScope(principal: UserPrincipal, scope: TokenScope): void {
  if (principal.scopes.includes('ADMIN')) return
  if (!principal.scopes.includes(scope)) {
    throw new ApiError(ErrorCode.INSUFFICIENT_SCOPE, `Token thiếu scope ${scope}.`)
  }
}

export function requireCapability(principal: WorkerPrincipal, capability: WorkerCapability): void {
  if (!principal.capabilities.includes(capability)) {
    throw new ApiError(
      ErrorCode.CAPABILITY_NOT_GRANTED,
      `Máy worker không được cấp năng lực ${capability}.`,
    )
  }
}

/**
 * Chốt chặn cuối: worker/agent KHÔNG BAO GIỜ được phê duyệt.
 *
 * DB cũng đã chặn bằng CHECK `approval_decider_must_be_human`. Hai lớp là cố ý
 * — tầng ứng dụng cho thông báo lỗi rõ ràng, tầng DB đảm bảo không đường ghi
 * nào lách được, kể cả script chạy tay.
 */
export function assertCanApprove(principal: Principal): asserts principal is UserPrincipal {
  if (principal.kind !== 'USER') {
    throw new ApiError(
      ErrorCode.WORKER_CANNOT_APPROVE,
      'Chỉ người dùng mới được phê duyệt; agent/worker không được phép.',
    )
  }
  requireScope(principal, 'APPROVE')
}

/** Chỉ dùng cho seed/CLI quản trị — không gọi từ route xử lý request. */
export const activeTokenFilter = and(
  isNull(userApiToken.revokedAt),
  or(isNull(userApiToken.expiresAt), gt(userApiToken.expiresAt, new Date())),
)
