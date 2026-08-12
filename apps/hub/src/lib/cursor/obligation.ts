import { createHash } from 'node:crypto'

import { stableStringify } from '../analysis/package'
import {
  ANALYSIS_SCHEMA_VERSION,
  assertionStatusEnum,
  OBLIGATION_GENERATOR_VERSION,
  type ClaimObligation,
  type ClaimObligationSet,
  type CursorAnalysis,
} from './schema'
import { mentionedSensitiveMetrics, speechActKey, STRUCTURAL_SPEECH_ACT } from './sensitive'
import { enumerateUnits, resolveSourceRef, type ResolvedUnit } from './source-ref'

/**
 * BỘ SINH NGHĨA VỤ KHAI BÁO — trái tim của kiến trúc hai lượt.
 *
 * Bốn lần thăm dò của hợp đồng 2.1 một lượt cho thấy mô hình trỏ `sourceRef`
 * đúng 100% (R=0 cả bốn lần) nhưng ĐẾM SÓT ô phải khai, dao động 2–19 lỗi và
 * nghịch chiều với số claim nó viết. Việc đếm ô là việc SỔ SÁCH — và
 * `enumerateUnits` tính được nó một cách tất định.
 *
 * Tệp này lấy việc đó khỏi tay mô hình. Mô hình chỉ còn phải trả lời "ô NÀY nói
 * gì về chỉ số nào", đúng phần nó đã chứng minh là làm được.
 *
 * RANH GIỚI TIN CẬY: tập nghĩa vụ là TẤT ĐỊNH (cùng bản phân tích cho cùng tập,
 * từng ký tự). Nhưng việc một ô CÓ nhắc chỉ số nhạy cảm hay không vẫn là
 * HEURISTIC NGÔN NGỮ — nó dựa trên `SENSITIVE_MENTION`. Tất định KHÔNG có nghĩa
 * là đúng; nó chỉ có nghĩa là lặp lại được và kiểm được.
 */

/**
 * Chuẩn hoá văn bản trước khi băm.
 *
 * Băm phải bất biến trước những khác biệt KHÔNG mang nghĩa (khoảng trắng thừa,
 * xuống dòng khác kiểu) nhưng nhạy với mọi khác biệt CÓ nghĩa. Không hạ chữ
 * thường: "CTR" và "ctr" khác nhau về hình thức trình bày và ta muốn thấy điều
 * đó nếu văn xuôi bị viết lại.
 */
export function normalizeForHash(text: string): string {
  return text.replace(/\r\n/gu, '\n').replace(/[ \t]+/gu, ' ').trim()
}

export function hashText(text: string): string {
  return createHash('sha256').update(normalizeForHash(text), 'utf8').digest('hex')
}

/**
 * Băm của BẢN PHÂN TÍCH ĐÃ ĐÓNG BĂNG.
 *
 * Dùng `stableStringify` (khoá đã sắp) chứ không `JSON.stringify`: payload đi
 * qua JSONB sẽ quay về với thứ tự khoá khác, và một phép băm nhạy thứ tự khoá sẽ
 * báo trôi dạt giả ở mọi lần đọc lại từ database.
 */
export function hashAnalysisPayload(analysis: CursorAnalysis): string {
  return createHash('sha256').update(stableStringify(analysis), 'utf8').digest('hex')
}

/** Băm của TẬP NGHĨA VỤ. Nghĩa vụ đã sắp theo `id` nên kết quả tất định. */
export function hashObligationSet(set: ClaimObligationSet): string {
  return createHash('sha256').update(stableStringify(set), 'utf8').digest('hex')
}

/**
 * `assertionStatus` nào hợp lệ cho một ô.
 *
 * Với ô NHÃN, CẤU TRÚC đã quy định hành vi lời nói: `metricOrArtifact` là dữ
 * liệu cần thu thập, `missingEvidence` là bằng chứng còn thiếu,
 * `reviewQuestions` là câu hỏi. Tính sẵn ở đây thay vì bắt mô hình đoán — và
 * `ASSERTED` bị loại khỏi tập, nên nó trở thành BẤT KHẢ BIỂU DIỄN ở các ô đó.
 */
function allowedStatusesFor(unit: ResolvedUnit): string[] {
  const [section = '', , fieldWithOrdinal = ''] = unit.canonical.split('|')
  const field = fieldWithOrdinal.split('#')[0] ?? ''
  const structural = STRUCTURAL_SPEECH_ACT[speechActKey(section, field)]
  return structural ? [...structural.allowed] : [...assertionStatusEnum.options]
}

/** `canonical` -> `sourceRef`. Bộ liệt kê dựng canonical, ta dựng lại ref từ nó. */
function refFromCanonical(canonical: string): {
  section: string
  itemId: string
  field: string
  ordinal: number
} {
  const [section = '', itemId = '', rest = ''] = canonical.split('|')
  const hashAt = rest.lastIndexOf('#')
  return {
    section,
    itemId,
    field: hashAt === -1 ? rest : rest.slice(0, hashAt),
    ordinal: hashAt === -1 ? 0 : Number(rest.slice(hashAt + 1)),
  }
}

/**
 * Dựng TẬP NGHĨA VỤ từ một bản phân tích đã đóng băng.
 *
 * Thứ tự nghĩa vụ = thứ tự `enumerateUnits`, và `id` cấp tuần tự theo thứ tự đó.
 * Nhờ vậy cùng một payload luôn cho cùng một tập, từng `id` một — điều kiện cần
 * để `obligationSetHash` có nghĩa.
 */
export function buildObligationSet(analysis: CursorAnalysis): ClaimObligationSet {
  const obligations: ClaimObligation[] = []

  for (const unit of enumerateUnits(analysis)) {
    const metrics = [...mentionedSensitiveMetrics(unit.text)]
    // Không nhắc chỉ số nhạy cảm -> không phải nghĩa vụ. Đây CHÍNH LÀ định nghĩa
    // của U3 cũ, nay là một phép lọc thay vì một phép kiểm chạy sau.
    if (metrics.length === 0) continue

    const ref = refFromCanonical(unit.canonical)
    obligations.push({
      id: `MC-${String(obligations.length + 1).padStart(3, '0')}`,
      sourceRef: {
        section: ref.section as ClaimObligation['sourceRef']['section'],
        itemId: ref.itemId,
        field: ref.field,
        ordinal: ref.ordinal,
      },
      canonical: unit.canonical,
      pointer: unit.pointer,
      resolvedText: unit.text,
      resolvedHash: hashText(unit.text),
      mentionedMetrics: metrics as ClaimObligation['mentionedMetrics'],
      allowedAssertionStatuses:
        allowedStatusesFor(unit) as ClaimObligation['allowedAssertionStatuses'],
    })
  }

  return {
    schemaVersion: ANALYSIS_SCHEMA_VERSION,
    generatorVersion: OBLIGATION_GENERATOR_VERSION,
    analysisHash: hashAnalysisPayload(analysis),
    obligations,
  }
}

export type ObligationCheck =
  | { ok: true }
  | { ok: false; rule: string; message: string; path?: string }

/**
 * O-INV-1 — tập nghĩa vụ thuộc ĐÚNG bản phân tích này.
 *
 * Không thừa: tập nghĩa vụ đi qua database và qua một lời gọi LLM trước khi được
 * dùng lại. Giữa hai điểm đó có đủ chỗ để ghép nhầm.
 */
export function checkObligationBelongsTo(
  set: ClaimObligationSet,
  analysis: CursorAnalysis,
): ObligationCheck {
  const actual = hashAnalysisPayload(analysis)
  if (set.analysisHash !== actual) {
    return {
      ok: false,
      rule: 'obligation_analysis_mismatch',
      message:
        `Tập nghĩa vụ khai analysisHash=${set.analysisHash.slice(0, 12)}… nhưng bản phân tích ` +
        `đang dùng có băm ${actual.slice(0, 12)}…. Tập nghĩa vụ thuộc về một lần phân tích KHÁC.`,
    }
  }
  return { ok: true }
}

/**
 * O-INV-2 — `sourceRef` và băm văn bản khớp bản phân tích ĐÃ ĐÓNG BĂNG.
 *
 * PHÂN GIẢI LẠI từng tham chiếu thay vì tin tập nghĩa vụ. Đây là chỗ giữ lại
 * toàn bộ sức mạnh của R1–R5 cũ: nếu văn xuôi bị đổi giữa hai lượt — worker cũ,
 * ghi thẳng database, lỗi ghép — băm không khớp và kết quả bị chặn.
 *
 * KHÔNG được bỏ với lý do "ứng dụng tự sinh nên chắc đúng". Chính vì tự sinh nên
 * không còn ai kiểm nó ngoài chỗ này.
 */
export function checkObligationSourcesIntact(
  set: ClaimObligationSet,
  analysis: CursorAnalysis,
): ObligationCheck[] {
  const out: ObligationCheck[] = []
  for (const ob of set.obligations) {
    const res = resolveSourceRef(analysis, ob.sourceRef)
    if ('error' in res) {
      out.push({
        ok: false,
        rule: 'obligation_source_unresolved',
        message: `${ob.id}: sourceRef không còn phân giải được trên bản phân tích (${res.error})`,
        path: ob.pointer,
      })
      continue
    }
    if (res.ok.canonical !== ob.canonical) {
      out.push({
        ok: false,
        rule: 'obligation_source_drift',
        message: `${ob.id}: danh tính ô đổi từ "${ob.canonical}" thành "${res.ok.canonical}"`,
        path: ob.pointer,
      })
      continue
    }
    if (hashText(res.ok.text) !== ob.resolvedHash) {
      out.push({
        ok: false,
        rule: 'obligation_source_drift',
        message:
          `${ob.id}: VĂN BẢN ô nguồn đã đổi kể từ lúc sinh nghĩa vụ. ` +
          `Bản phân tích không còn là bản đã đóng băng.`,
        path: ob.pointer,
      })
    }
  }
  return out
}

/**
 * O-INV-3 — DANH TÍNH nghĩa vụ: không thiếu, không thừa, không trùng.
 *
 * So theo TẬP `id`, không theo thứ tự mảng: đảo thứ tự `declarations` là vô hại
 * và không được coi là trôi dạt. Bốn mã lỗi RIÊNG, không gộp — "thiếu một khai
 * báo" và "khai thừa một cái không tồn tại" là hai lỗi khác nhau và cần sửa khác
 * nhau.
 */
export function checkDeclarationIdentity(
  set: ClaimObligationSet,
  declarationIds: string[],
): ObligationCheck[] {
  const out: ObligationCheck[] = []
  const required = new Set(set.obligations.map((o) => o.id))
  const seen = new Set<string>()
  const duplicates = new Set<string>()

  for (const id of declarationIds) {
    if (seen.has(id)) duplicates.add(id)
    seen.add(id)
  }

  for (const id of duplicates) {
    out.push({
      ok: false,
      rule: 'declaration_duplicate',
      message: `Khai báo trùng id "${id}" — một nghĩa vụ chỉ được đúng một khai báo.`,
    })
  }
  for (const id of declarationIds) {
    if (!required.has(id)) {
      out.push({
        ok: false,
        rule: 'declaration_unknown_obligation',
        message: `Khai báo "${id}" không ứng với nghĩa vụ nào. Không được tự thêm claim.`,
      })
    }
  }
  for (const id of required) {
    if (!seen.has(id)) {
      out.push({
        ok: false,
        rule: 'declaration_missing_obligation',
        message: `Nghĩa vụ "${id}" chưa được khai báo.`,
      })
    }
  }
  if (declarationIds.length !== set.obligations.length) {
    out.push({
      ok: false,
      rule: 'declaration_count_mismatch',
      message: `Có ${declarationIds.length} khai báo cho ${set.obligations.length} nghĩa vụ.`,
    })
  }
  return out
}

/** O-INV-4 — lượt khai báo phải trả lời ĐÚNG tập nghĩa vụ đã đóng băng. */
export function checkObligationSetHash(expected: string, declared: string): ObligationCheck {
  if (expected !== declared) {
    return {
      ok: false,
      rule: 'obligation_set_drift',
      message:
        `Lượt khai báo khai obligationSetHash=${declared.slice(0, 12)}… nhưng tập nghĩa vụ ` +
        `hiện hành có băm ${expected.slice(0, 12)}…. Khai báo đang trả lời một tập KHÁC.`,
    }
  }
  return { ok: true }
}

/**
 * GHÉP nghĩa vụ với khai báo thành `metricClaims` của kết quả hợp nhất.
 *
 * Ghép theo `id`, không theo vị trí. `sourceRef` lấy từ NGHĨA VỤ, không bao giờ
 * từ khai báo — đó là lý do lượt 2 không thể đổi mục tiêu của một claim.
 *
 * Chỉ gọi sau khi O-INV-3 xanh; nếu không, một nghĩa vụ thiếu khai báo sẽ lặng
 * lẽ biến mất khỏi mảng kết quả.
 */
export function composeMetricClaims(
  set: ClaimObligationSet,
  declarations: Array<{ id: string } & Record<string, unknown>>,
): Array<Record<string, unknown>> {
  const byId = new Map(declarations.map((d) => [d.id, d]))
  return set.obligations.map((ob) => {
    const d = byId.get(ob.id)!
    return {
      id: ob.id,
      claimType: d.claimType,
      subjectMetric: d.subjectMetric,
      relatedMetric: d.relatedMetric,
      judgement: d.judgement,
      assertionStatus: d.assertionStatus,
      evidenceIds: d.evidenceIds,
      requiresMissingnessDisclosure: d.requiresMissingnessDisclosure,
      sourceRef: ob.sourceRef,
    }
  })
}
