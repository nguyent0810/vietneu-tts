import type { ContractProvenance } from './provenance'
import type { RunCursorAnalysisResult } from './run'

/**
 * DANH TÍNH của một lần chạy — mọi id cần để lần ngược một hiện vật về database.
 *
 * Tách khỏi `run-cursor.ts` để `INDEX.json` và bộ test gọi CÙNG một hàm. Bản
 * trước dựng khối này ngay tại chỗ ghi tệp, nên test chỉ có hai lựa chọn: chạy
 * cả CLI, hoặc chép lại logic — và một test chép lại logic thì xanh kể cả khi
 * bản thật thiếu trường, vì nó đang kiểm chính nó.
 */
export interface RunIdentity {
  status: string
  requestId: string | null
  analysisRunId: string | null
  channelId: string | null
  analysisExecutionId: string | null
  declarationExecutionId: string | null
  compositeValidationId: string | null
  resultId: string | null
  /**
   * Execution ĐÃ SINH RA hiện vật — khoá mà `attempt_table.mjs` và
   * `verify_phase4.mjs` dùng để đối chiếu artifact với database.
   *
   * Cùng giá trị với `declarationExecutionId` ở kiến trúc hai lượt, nhưng phải
   * là một trường RIÊNG: hai bộ kiểm hiện có tra đúng tên này, và khi phép ghép
   * `_meta` được gom vào `buildArtifactMeta` thì trường này bị rơi — mọi lô
   * lành mạnh đều in "_meta KHÔNG khớp DB".
   */
  llmExecutionId: string | null
  analysisPayloadHash: string | null
  obligationSetHash: string | null
  obligationCount: number | null
  compositePayloadHash: string | null
  analysisAttempts: number
  declarationAttempts: number
  compositeFailureClass: string | null
}

/**
 * Trường nào PHẢI khác null khi lần chạy ĐẠT.
 *
 * Ở lần chạy hỏng, phần lớn trong số này null một cách chính đáng — hỏng ở lượt
 * 1 thì làm gì có id lượt khai báo. Nên điều kiện gắn với `status`, chứ không
 * phải một danh sách "luôn phải có" mà lần hỏng nào cũng vi phạm.
 */
export const IDENTITY_REQUIRED_ON_SUCCESS = [
  'requestId',
  'analysisRunId',
  'channelId',
  'analysisExecutionId',
  'declarationExecutionId',
  'compositeValidationId',
  'resultId',
  'llmExecutionId',
  'analysisPayloadHash',
  'obligationSetHash',
  'obligationCount',
  'compositePayloadHash',
] as const satisfies ReadonlyArray<keyof RunIdentity>

export function runIdentity(r: RunCursorAnalysisResult): RunIdentity {
  return {
    status: r.status,
    requestId: r.requestId,
    analysisRunId: r.analysisRunId ?? null,
    channelId: r.channelId ?? null,
    analysisExecutionId: r.analysisExecutionId,
    declarationExecutionId: r.declarationExecutionId ?? null,
    compositeValidationId: r.compositeValidationId ?? null,
    resultId: r.resultId ?? null,
    llmExecutionId: r.declarationExecutionId ?? r.analysisExecutionId ?? null,
    analysisPayloadHash: r.analysisPayloadHash,
    obligationSetHash: r.obligationSetHash,
    // Mang ở ĐÂY chứ không chỉ dựa vào `_meta` của chặng hợp nhất: nếu chỉ lấy
    // từ đó thì `_meta` của artifact mất trường này ngay khi chặng hợp nhất đổi,
    // và ma trận phủ sẽ báo thiếu ở một chỗ chẳng liên quan gì.
    obligationCount: r.obligationCount,
    compositePayloadHash: r.compositePayloadHash ?? null,
    analysisAttempts: r.analysisAttempts.length,
    declarationAttempts: r.declarationAttempts.length,
    compositeFailureClass: r.compositeFailureClass ?? null,
  }
}

/** Trường bắt buộc còn thiếu ở một lần chạy ĐẠT. Rỗng nghĩa là đủ. */
export function missingIdentityFields(id: RunIdentity): string[] {
  if (id.status !== 'SUCCEEDED') return []
  return IDENTITY_REQUIRED_ON_SUCCESS.filter((k) => id[k] === null || id[k] === undefined)
}

/**
 * `_meta` của ARTIFACT và khối nguồn gốc của `INDEX.json`.
 *
 * Cùng lý do như `runIdentity`: dựng tại chỗ ghi tệp thì bộ test không với tới,
 * và một test tự dựng lại khối này sẽ xanh ngay cả khi bản thật thiếu trường.
 */
export function buildArtifactMeta(
  r: RunCursorAnalysisResult,
  contract: ContractProvenance,
  runMeta: Record<string, unknown>,
  extra: { channelLabel: string; durationMs: number; writtenAt: string; outputSchemaVersion: string },
): Record<string, unknown> {
  return {
    ...contract,
    // `_meta` do chặng hợp nhất gắn đã mang lineage hai lượt. Trải trước rồi mới
    // bổ sung phần thuộc về LẦN GHI TỆP, để không cái nào che cái nào.
    ...runMeta,
    ...runIdentity(r),
    channelLabel: extra.channelLabel,
    packageHash: r.packageHash,
    promptHash: r.promptHash,
    finalAttempt: r.finalAttempt,
    durationMs: extra.durationMs,
    outputSchemaVersion: extra.outputSchemaVersion,
    writtenAt: extra.writtenAt,
  }
}

export function buildIndexProvenance(
  contract: ContractProvenance,
  extra: { generatedAt: string; schemaVersion: string; mode: string },
): Record<string, unknown> {
  return { ...contract, ...extra }
}

/**
 * TỆP ARTIFACT hoàn chỉnh: `_meta` đầy đủ + thân payload.
 *
 * Tách ra vì phép GHÉP mới là chỗ hỏng, không phải phép dựng. Bản trước viết
 * `{ _meta: buildArtifactMeta(...), ...r.output }` — và vì `r.output` MANG
 * `_meta` của riêng nó, spread ghi đè ngược lại, xoá sạch `resultId`,
 * `compositeValidationId`, số lần thử, `writtenAt`. Tệp vẫn đúng schema nên
 * không có gì kêu; nó chỉ lặng lẽ không lần ngược được về database nữa.
 *
 * Test gọi ĐÚNG hàm này, nên phép ghép nằm trong phạm vi được kiểm.
 */
export function buildArtifactFile(
  output: Record<string, unknown>,
  r: RunCursorAnalysisResult,
  contract: ContractProvenance,
  extra: { channelLabel: string; durationMs: number; writtenAt: string; outputSchemaVersion: string },
): Record<string, unknown> {
  const { _meta: runMeta, ...body } = output as { _meta?: Record<string, unknown> }
  return {
    _meta: buildArtifactMeta(r, contract, runMeta ?? {}, extra),
    ...body,
  }
}

/**
 * `INDEX.json` hoàn chỉnh — nguồn gốc + tally + DANH TÍNH từng lần chạy.
 *
 * Phần quyết định mẫu số của lô (tally) và phần cho phép lần ngược (identities)
 * trước đây nằm ngay trong chỗ ghi tệp, ngoài tầm với của mọi test. Một thay đổi
 * làm rơi `identities`, hoặc đếm sót lần thất bại, sẽ không làm đỏ bất cứ thứ gì.
 */
export function buildIndexJson(args: {
  contract: ContractProvenance
  generatedAt: string
  schemaVersion: string
  mode: string
  tally: Record<string, { attempts: number; successes: number; timeouts: number; validationFails: number; other: number }>
  identities: Record<string, RunIdentity[]>
  filesFor: (label: string) => string[]
}): Record<string, unknown> {
  return {
    ...buildIndexProvenance(args.contract, {
      generatedAt: args.generatedAt,
      schemaVersion: args.schemaVersion,
      mode: args.mode,
    }),
    channels: Object.fromEntries(
      Object.entries(args.tally).map(([label, t]) => [
        label,
        { ...t, identities: args.identities[label] ?? [], files: args.filesFor(label) },
      ]),
    ),
  }
}

/**
 * Lần chạy này có được GHI ARTIFACT không?
 *
 * `r.output` KHÔNG phải câu trả lời: ba nhánh THẤT BẠI cũng gán `output` để giữ
 * văn xuôi làm bằng chứng. Và vì hậu tố tệp là `.s{số mẫu đạt}`, một lần chạy
 * hỏng ghi đúng vào ô của mẫu ĐẠT gần nhất — thay một hiện vật đã được cấp phép
 * bằng payload chỉ có văn xuôi, trong khi database vẫn đếm mẫu ấy là hợp lệ.
 *
 * Điều kiện đúng là ĐƯỢC CẤP PHÉP: trạng thái ĐẠT *và* có id kết quả chính thức.
 */
export function shouldWriteArtifact(r: RunCursorAnalysisResult): boolean {
  return r.status === 'SUCCEEDED' && (r.resultId ?? null) !== null
}
