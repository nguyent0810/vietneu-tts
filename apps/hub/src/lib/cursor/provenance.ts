import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { readFileSync, realpathSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

import {
  ANALYSIS_SCHEMA_VERSION,
  COMPOSITE_VALIDATOR_VERSION,
  CURSOR_OUTPUT_SCHEMA_VERSION,
  DECLARATION_SCHEMA_VERSION,
  OBLIGATION_GENERATOR_VERSION,
} from './schema'

/**
 * NGUỒN GỐC — một bản ghi, dùng chung cho MỌI bề mặt.
 *
 * Bài học của các vòng trước: mỗi bề mặt (`_meta` trong artifact, `INDEX.json`,
 * bản kê trong database) tự thu thập nguồn gốc của riêng nó, nên chúng lệch nhau
 * mà không ai thấy. Một bản ghi, một nơi tính, ba nơi chép ra — thì lệch nhau
 * trở thành phát hiện được bằng phép so, không còn là chuyện may rủi.
 *
 * RANH GIỚI TIN CẬY, nhắc lại vì tệp này dễ bị đọc quá lời: đây là BẢN GHI CÓ
 * KỶ LUẬT, KHÔNG phải attestation. Băm được tính lúc nạp module bằng cách đọc
 * tệp trên đĩa; nó không chứng minh runtime đã thực thi đúng những byte ấy. Xem
 * creator_specs/PHASE4_TRUST_BOUNDARIES.md.
 */

function repoRoot(): string {
  return join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..')
}

function git(args: string[]): string {
  try {
    return execFileSync('git', args, { cwd: repoRoot(), encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] })
      .trim()
  } catch {
    return 'unavailable'
  }
}

/**
 * Băm của DIFF BẨN, không phải cờ boolean.
 *
 * "dirty: true" chỉ nói có thay đổi chưa commit; nó không phân biệt hai lần chạy
 * với hai thay đổi KHÁC NHAU. Một băm thì phân biệt được, và đó chính là điều
 * cần khi đối chiếu một lô đo với mã đã sinh ra nó.
 */
function dirtyDiffHash(): { hash: string; dirty: boolean } {
  const diff = git(['diff', 'HEAD'])
  // Git không chạy được => KHÔNG BIẾT cây làm việc sạch hay bẩn. Trả `dirty:
  // false` ở đây là khai một trạng thái không xác định thành "sạch" — đúng cái
  // khẳng định mạnh nhất, dựa trên đúng cái ta biết ít nhất.
  if (diff === 'unavailable') return { hash: 'unavailable', dirty: true }
  if (diff === '') return { hash: createHash('sha256').update('', 'utf8').digest('hex'), dirty: false }
  return { hash: createHash('sha256').update(diff, 'utf8').digest('hex'), dirty: true }
}

function packageVersion(): string {
  try {
    return (JSON.parse(readFileSync(join(repoRoot(), 'package.json'), 'utf8')) as { version?: string })
      .version ?? 'unavailable'
  } catch {
    return 'unavailable'
  }
}

export interface ContractProvenance {
  /** SÁU hợp đồng — xem mục 4.1 của PHASE4_1_DECLARATION_PASS_DESIGN.md. */
  analysisSchemaVersion: string
  analysisPromptVersion: string
  obligationGeneratorVersion: string
  declarationSchemaVersion: string
  declarationPromptVersion: string
  compositeValidatorVersion: string
  compositeSchemaVersion: string

  /** Băm MÃ NGUỒN của các tệp quyết định ngữ nghĩa. */
  validatorHash: string
  schemaHash: string
  promptSourceHash: string
  declarationPromptSourceHash: string
  obligationGeneratorHash: string
  compositeSourceHash: string
  /** Từ điển ô nhạy cảm — HỢP ĐỒNG, xem `SENSITIVE_LEXICON_HASH` trong run.ts. */
  sensitiveLexiconHash: string
  identitySourceHash: string
  provenanceSourceHash: string

  /** Môi trường thực thi. */
  lockfileHash: string
  packageVersion: string
  gitCommit: string
  gitDirty: boolean
  gitDirtyDiffHash: string
  nodeVersion: string
}

/**
 * Bản ghi nguồn gốc TĨNH, tính một lần lúc nạp module.
 *
 * Tính lúc nạp chứ không lúc ghi: gắn nó vào execution ngay khi tạo, để nó là
 * bản ghi VỀ tiến trình đang chạy chứ không phải một suy luận ngược từ artifact.
 */
export function buildContractProvenance(hashes: {
  validatorHash: string
  schemaHash: string
  promptSourceHash: string
  declarationPromptSourceHash: string
  obligationGeneratorHash: string
  compositeSourceHash: string
  sensitiveLexiconHash: string
  identitySourceHash: string
  provenanceSourceHash: string
  lockfileHash: string
  analysisPromptVersion: string
  declarationPromptVersion: string
}): ContractProvenance {
  const dirty = dirtyDiffHash()
  return {
    analysisSchemaVersion: ANALYSIS_SCHEMA_VERSION,
    analysisPromptVersion: hashes.analysisPromptVersion,
    obligationGeneratorVersion: OBLIGATION_GENERATOR_VERSION,
    declarationSchemaVersion: DECLARATION_SCHEMA_VERSION,
    declarationPromptVersion: hashes.declarationPromptVersion,
    compositeValidatorVersion: COMPOSITE_VALIDATOR_VERSION,
    compositeSchemaVersion: CURSOR_OUTPUT_SCHEMA_VERSION,

    validatorHash: hashes.validatorHash,
    schemaHash: hashes.schemaHash,
    promptSourceHash: hashes.promptSourceHash,
    declarationPromptSourceHash: hashes.declarationPromptSourceHash,
    obligationGeneratorHash: hashes.obligationGeneratorHash,
    compositeSourceHash: hashes.compositeSourceHash,
    sensitiveLexiconHash: hashes.sensitiveLexiconHash,
    identitySourceHash: hashes.identitySourceHash,
    provenanceSourceHash: hashes.provenanceSourceHash,

    lockfileHash: hashes.lockfileHash,
    packageVersion: packageVersion(),
    gitCommit: git(['rev-parse', 'HEAD']),
    gitDirty: dirty.dirty,
    gitDirtyDiffHash: dirty.hash,
    nodeVersion: process.version,
  }
}

/** Đường dẫn THẬT của tệp thực thi, sau khi bỏ symlink. */
export function resolveExecutableRealpath(path: string): string {
  try {
    return realpathSync(path)
  } catch {
    return path
  }
}

export interface ProvenanceMismatch {
  field: string
  surfaces: Record<string, unknown>
}

/**
 * ĐỒNG THUẬN NGUỒN GỐC — điều kiện của cổng đóng băng.
 *
 * So từng trường giữa các bề mặt. Lệch MỘT trường là không đồng thuận, kể cả khi
 * mọi phép kiểm khác đều xanh: hai bề mặt nói hai điều khác nhau về cùng một lần
 * chạy nghĩa là ít nhất một trong hai đang nói dối, và ta không biết cái nào.
 *
 * `surfaces` là map tên-bề-mặt -> object nguồn gốc. Chỉ so các trường CÓ MẶT ở
 * từ hai bề mặt trở lên: một bề mặt không mang trường nào đó thì đó là thiếu sót
 * về phạm vi, không phải mâu thuẫn — và được báo riêng qua `missing`.
 */
export function checkProvenanceAgreement(
  surfaces: Record<string, Record<string, unknown>>,
  required: string[],
): { agreed: boolean; mismatches: ProvenanceMismatch[]; missing: Array<{ surface: string; field: string }> } {
  const mismatches: ProvenanceMismatch[] = []
  const missing: Array<{ surface: string; field: string }> = []
  const names = Object.keys(surfaces)

  for (const field of required) {
    const present: Record<string, unknown> = {}
    for (const n of names) {
      const v = surfaces[n]![field]
      if (v === undefined || v === null) missing.push({ surface: n, field })
      else present[n] = v
    }
    const values = Object.values(present)
    if (values.length < 2) continue
    const first = JSON.stringify(values[0])
    if (values.some((v) => JSON.stringify(v) !== first)) {
      mismatches.push({ field, surfaces: present })
    }
  }
  return { agreed: mismatches.length === 0 && missing.length === 0, mismatches, missing }
}

/* =========================================================================
 * MA TRẬN PHỦ NGUỒN GỐC
 * ====================================================================== */

/**
 * Mọi BỀ MẶT mang nguồn gốc của một lần chạy hai lượt.
 *
 * Liệt kê tường minh thay vì "bất cứ thứ gì caller truyền vào": một bề mặt bị
 * quên là một khoảng trống im lặng, và cách duy nhất phát hiện là có một danh
 * sách để đối chiếu.
 */
export type ProvenanceSurfaceName =
  | 'request'
  | 'analysisExecution'
  | 'analysisRepairExecution'
  | 'obligationSet'
  | 'declarationExecution'
  | 'declarationRepairExecution'
  | 'analysisValidation'
  | 'declarationValidation'
  | 'compositeValidation'
  | 'resultRow'
  | 'storedMeta'
  | 'artifactMeta'
  | 'indexJson'
  | 'attemptTable'

export interface SurfaceSpec {
  /** PHẢI có mặt và khác null. Thiếu là hỏng, kể cả khi caller quên hỏi. */
  required: readonly string[]
  /**
   * KHÔNG áp dụng cho bề mặt này — và có mặt thì cũng là hỏng.
   *
   * Ghi rõ "không áp dụng" khác hẳn với "quên": hàng tập nghĩa vụ ra đời TRƯỚC
   * lượt khai báo nên nó không thể mang phiên bản prompt khai báo, và nếu một
   * ngày nó mang thì đó là dấu hiệu ai đó đang nhồi dữ liệu sai chỗ.
   */
  notApplicable: readonly string[]
}

const CONTRACT_FIELDS = [
  'analysisSchemaVersion',
  'analysisPromptVersion',
  'obligationGeneratorVersion',
  'declarationSchemaVersion',
  'declarationPromptVersion',
  'compositeValidatorVersion',
  // M-1 — `compositeSchemaVersion` có trên BA bề mặt (`storedMeta`,
  // `artifactMeta`, `indexJson`) nhưng ma trận không đòi và không so. Một trường
  // có mặt ở nhiều nơi mà không ai so thì nó chỉ là chữ: hai bề mặt nói hai bản
  // schema khác nhau về cùng một hiện vật vẫn qua cổng.
  'compositeSchemaVersion',
  'validatorHash',
  'schemaHash',
  'promptSourceHash',
  'declarationPromptSourceHash',
  'obligationGeneratorHash',
  'compositeSourceHash',
  'sensitiveLexiconHash',
  'identitySourceHash',
  'provenanceSourceHash',
] as const

const ENV_FIELDS = [
  'lockfileHash',
  'packageVersion',
  'gitCommit',
  'gitDirty',
  'gitDirtyDiffHash',
  'nodeVersion',
] as const

const LINEAGE_FIELDS = [
  'analysisExecutionId',
  'declarationExecutionId',
  'analysisPayloadHash',
  'obligationSetHash',
  'obligationCount',
] as const

export const PROVENANCE_MATRIX: Record<ProvenanceSurfaceName, SurfaceSpec> = {
  request: {
    required: ['requestId', 'analysisRunId', 'channelId', 'analysisPackageId', 'packageHash', 'promptHash'],
    notApplicable: ['obligationSetHash', 'declarationExecutionId', 'compositeValidatorVersion'],
  },
  analysisExecution: {
    required: [
      'llmExecutionId', 'executionRole', 'attemptNumber', 'toolName',
      'schemaVersion', 'promptVersion', 'validatorHash', 'schemaHash', 'promptSourceHash',
    ],
    // Lượt PHÂN TÍCH không được mang lineage của lượt khai báo — CHECK 0023 cưỡng chế.
    notApplicable: ['analysisExecutionId'],
  },
  analysisRepairExecution: {
    required: [
      'llmExecutionId', 'executionRole', 'attemptNumber', 'parentExecutionId', 'toolName',
      'schemaVersion', 'promptVersion', 'validatorHash', 'schemaHash', 'promptSourceHash',
    ],
    notApplicable: ['analysisExecutionId'],
  },
  obligationSet: {
    required: [
      'analysisExecutionId', 'analysisPayloadHash', 'obligationSetHash',
      'obligationGeneratorVersion', 'obligationCount',
    ],
    // Ra đời TRƯỚC lượt khai báo: không thể biết gì về nó.
    notApplicable: ['declarationExecutionId', 'declarationPromptVersion', 'compositeValidatorVersion'],
  },
  declarationExecution: {
    required: [
      'llmExecutionId', 'executionRole', 'attemptNumber', 'toolName', 'analysisExecutionId',
      'schemaVersion', 'promptVersion', 'validatorHash', 'schemaHash', 'promptSourceHash',
      'obligationGeneratorVersion', 'declarationPromptVersion', 'declarationPromptSourceHash',
      'compositeValidatorVersion', 'analysisPayloadHash', 'obligationSetHash',
    ],
    notApplicable: [],
  },
  declarationRepairExecution: {
    required: [
      'llmExecutionId', 'executionRole', 'attemptNumber', 'parentExecutionId', 'toolName',
      'analysisExecutionId', 'schemaVersion', 'promptVersion', 'validatorHash', 'schemaHash',
      'promptSourceHash', 'obligationGeneratorVersion', 'declarationPromptVersion',
      'declarationPromptSourceHash', 'compositeValidatorVersion', 'analysisPayloadHash',
      'obligationSetHash',
    ],
    notApplicable: [],
  },
  analysisValidation: {
    required: ['llmExecutionId', 'stage', 'passed'],
    // Dòng kiểm định là PHÁN QUYẾT, không phải nơi chứa băm hợp đồng.
    notApplicable: [...CONTRACT_FIELDS, ...ENV_FIELDS],
  },
  declarationValidation: {
    required: ['llmExecutionId', 'stage', 'passed'],
    notApplicable: [...CONTRACT_FIELDS, ...ENV_FIELDS],
  },
  compositeValidation: {
    required: ['llmExecutionId', 'stage', 'passed'],
    notApplicable: [...CONTRACT_FIELDS, ...ENV_FIELDS],
  },
  resultRow: {
    required: [
      'llmExecutionId', 'resultRole', 'schemaVersion', 'payloadHash',
      'analysisPayloadHash', 'obligationSetHash',
    ],
    notApplicable: ['obligationCount'],
  },
  storedMeta: {
    required: [...CONTRACT_FIELDS, ...ENV_FIELDS, ...LINEAGE_FIELDS],
    notApplicable: [],
  },
  artifactMeta: {
    required: [
      ...CONTRACT_FIELDS, ...ENV_FIELDS, ...LINEAGE_FIELDS,
      'channelLabel', 'packageHash', 'promptHash', 'requestId', 'writtenAt',
      'analysisAttempts', 'declarationAttempts',
      /*
       * M-2 — BỐN trường danh tính mà `verify_phase4.mjs` neo vào nhưng ma trận
       * KHÔNG đòi. `llmExecutionId` là đúng trường mà C-2 nói tới: nó từng bị rơi
       * khi phép ghép `_meta` được gom vào `buildArtifactMeta`, và thứ duy nhất
       * giữ nó lại là MỘT assertion viết tay. Một trường mà chỉ một assertion tay
       * bảo vệ thì nó không nằm trong cổng.
       */
      'llmExecutionId', 'resultId', 'compositeValidationId', 'analysisRunId',
    ],
    notApplicable: [],
  },
  indexJson: {
    required: [
      ...CONTRACT_FIELDS, ...ENV_FIELDS,
      'generatedAt', 'schemaVersion',
    ],
    notApplicable: [],
  },
  attemptTable: {
    required: ['attemptNumber', 'llmExecutionId', 'executionRole', 'failureClass', 'passed'],
    notApplicable: [...ENV_FIELDS],
  },
}

/**
 * Quan hệ BẰNG NHAU giữa các bề mặt.
 *
 * Đây là phần mang giá trị thật: một trường có mặt ở nhiều nơi mà không ai so
 * thì nó chỉ là chữ. Mỗi dòng dưới đây nói "các bề mặt này phải nói cùng một
 * điều về trường này", và chỉ so các bề mặt CÓ MẶT trong lần kiểm.
 */
export const PROVENANCE_EQUALITIES: ReadonlyArray<{
  field: string
  surfaces: readonly ProvenanceSurfaceName[]
}> = [
  { field: 'analysisPayloadHash', surfaces: ['obligationSet', 'declarationExecution', 'resultRow', 'storedMeta', 'artifactMeta'] },
  { field: 'obligationSetHash', surfaces: ['obligationSet', 'declarationExecution', 'resultRow', 'storedMeta', 'artifactMeta'] },
  { field: 'obligationCount', surfaces: ['obligationSet', 'storedMeta', 'artifactMeta'] },
  { field: 'obligationGeneratorVersion', surfaces: ['obligationSet', 'declarationExecution', 'storedMeta', 'artifactMeta', 'indexJson'] },
  { field: 'declarationPromptVersion', surfaces: ['declarationExecution', 'storedMeta', 'artifactMeta', 'indexJson'] },
  { field: 'declarationPromptSourceHash', surfaces: ['declarationExecution', 'storedMeta', 'artifactMeta', 'indexJson'] },
  { field: 'compositeValidatorVersion', surfaces: ['declarationExecution', 'storedMeta', 'artifactMeta', 'indexJson'] },
  { field: 'validatorHash', surfaces: ['analysisExecution', 'declarationExecution', 'storedMeta', 'artifactMeta', 'indexJson'] },
  { field: 'schemaHash', surfaces: ['analysisExecution', 'declarationExecution', 'storedMeta', 'artifactMeta', 'indexJson'] },
  { field: 'promptSourceHash', surfaces: ['analysisExecution', 'declarationExecution', 'storedMeta', 'artifactMeta', 'indexJson'] },
  { field: 'analysisExecutionId', surfaces: ['obligationSet', 'declarationExecution', 'storedMeta', 'artifactMeta'] },
  { field: 'requestId', surfaces: ['request', 'artifactMeta'] },
  { field: 'packageHash', surfaces: ['request', 'artifactMeta'] },
  { field: 'promptHash', surfaces: ['request', 'artifactMeta'] },
  // M-1 — bản schema hợp nhất phải GIỐNG NHAU ở ba bề mặt mang nó.
  { field: 'compositeSchemaVersion', surfaces: ['storedMeta', 'artifactMeta', 'indexJson'] },
  // M-2 — id execution sinh ra hiện vật: bản kê lượt khai báo và `_meta` của
  // hiện vật phải trỏ cùng một execution. Đây là phép so mà `verify_phase4.mjs`
  // vẫn làm trong khi ma trận thì không.
  { field: 'llmExecutionId', surfaces: ['declarationExecution', 'artifactMeta'] },
  { field: 'declarationExecutionId', surfaces: ['storedMeta', 'artifactMeta'] },
  { field: 'gitCommit', surfaces: ['storedMeta', 'artifactMeta', 'indexJson'] },
  { field: 'gitDirtyDiffHash', surfaces: ['storedMeta', 'artifactMeta', 'indexJson'] },
  { field: 'lockfileHash', surfaces: ['storedMeta', 'artifactMeta', 'indexJson'] },
]

export interface CoverageReport {
  ok: boolean
  /** Trường BẮT BUỘC vắng mặt — kể cả khi caller không hỏi tới nó. */
  missing: Array<{ surface: string; field: string }>
  /** Trường KHÔNG ÁP DỤNG mà lại có mặt. */
  unexpected: Array<{ surface: string; field: string }>
  /** Các bề mặt nói khác nhau về cùng một trường. */
  mismatches: ProvenanceMismatch[]
  /** Bề mặt được yêu cầu kiểm nhưng caller không cung cấp. */
  absentSurfaces: string[]
}

/**
 * Cổng NGUỒN GỐC do MA TRẬN điều khiển, không do caller điều khiển.
 *
 * Khác biệt cốt lõi so với `checkProvenanceAgreement`: hàm kia so đúng những
 * trường caller đưa, nên caller quên một trường là phép kiểm im lặng bỏ qua.
 * Hàm này lấy yêu cầu TỪ MA TRẬN, nên quên là hỏng — đúng như phải thế.
 *
 * `expectSurfaces` liệt kê những bề mặt BẮT BUỘC phải có trong lần kiểm này.
 * Thiếu một bề mặt cũng là hỏng, không phải "bỏ qua vì không có dữ liệu".
 */
/**
 * Giá trị SENTINEL — có mặt nhưng không mang thông tin.
 *
 * `git()` và `hashSource()` trả `'unavailable'` khi không đọc được. Chuỗi ấy đi
 * thẳng vào `CONTRACT_PROVENANCE` rồi được chép sang MỌI bề mặt, nên phép so
 * bằng nhau vẫn xanh: các bản sao khớp nhau hoàn hảo, và tất cả cùng không biết
 * gì. Coi nó là THIẾU chứ không phải là giá trị.
 */
const SENTINELS = new Set(['unavailable', '', 'unknown'])

export function checkProvenanceCoverage(
  surfaces: Partial<Record<ProvenanceSurfaceName, Record<string, unknown>>>,
  expectSurfaces: readonly ProvenanceSurfaceName[],
): CoverageReport {
  const missing: Array<{ surface: string; field: string }> = []
  const unexpected: Array<{ surface: string; field: string }> = []
  const absentSurfaces: string[] = []

  for (const name of expectSurfaces) {
    if (!surfaces[name]) absentSurfaces.push(name)
  }

  for (const [name, values] of Object.entries(surfaces) as Array<
    [ProvenanceSurfaceName, Record<string, unknown>]
  >) {
    const spec = PROVENANCE_MATRIX[name]
    if (!spec) continue
    for (const f of spec.required) {
      const v = values[f]
      if (v === undefined || v === null) missing.push({ surface: name, field: f })
      else if (typeof v === 'string' && SENTINELS.has(v)) missing.push({ surface: name, field: f })
    }
    for (const f of spec.notApplicable) {
      if (values[f] !== undefined && values[f] !== null) unexpected.push({ surface: name, field: f })
    }
  }

  const mismatches: ProvenanceMismatch[] = []
  for (const eq of PROVENANCE_EQUALITIES) {
    const present: Record<string, unknown> = {}
    for (const s of eq.surfaces) {
      const v = surfaces[s]?.[eq.field]
      if (v !== undefined && v !== null) present[s] = v
    }
    const values = Object.values(present)
    if (values.length < 2) continue
    const first = JSON.stringify(values[0])
    if (values.some((v) => JSON.stringify(v) !== first)) {
      mismatches.push({ field: eq.field, surfaces: present })
    }
  }

  return {
    ok: missing.length === 0 && unexpected.length === 0 && mismatches.length === 0 && absentSurfaces.length === 0,
    missing,
    unexpected,
    mismatches,
    absentSurfaces,
  }
}
