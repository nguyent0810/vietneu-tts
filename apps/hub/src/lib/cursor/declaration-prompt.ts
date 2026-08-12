import { createHash } from 'node:crypto'

import { stableStringify } from '../analysis/package'
import {
  CLAIM_METRICS,
  claimTypeEnum,
  DECLARATION_SCHEMA_VERSION,
  judgementEnum,
  type ClaimObligationSet,
} from './schema'

/**
 * PROMPT CỦA LƯỢT KHAI BÁO.
 *
 * Tệp RIÊNG, không nhét vào `prompt.ts`, vì hai lý do:
 *
 *  1. nó là một HỢP ĐỒNG ĐỘC LẬP, có phiên bản và băm nguồn riêng (mục 4.1 của
 *     `PHASE4_1_DECLARATION_PASS_DESIGN.md`). Nằm chung tệp thì hai băm dính vào
 *     nhau và không còn trả lời được "lô này hỏng vì đổi prompt nào";
 *  2. mọi thứ ở đây đã bị GỠ khỏi prompt phân tích. Để chúng cạnh nhau là mời
 *     người sửa sau vô tình đưa phần khai báo trở lại lượt 1.
 *
 * Điều lượt này KHÔNG làm: nó không nhận gói bằng chứng đầy đủ, không viết lại
 * văn xuôi, không chọn ô. Nó nhận một BẢNG NGHĨA VỤ đã tính sẵn và điền bảy
 * trường ngữ nghĩa cho từng dòng.
 */

/** 1.0.0 — bản đầu của hợp đồng khai báo tách lượt. */
export const DECLARATION_PROMPT_VERSION = '1.0.0'

/**
 * Trần ký tự.
 *
 * Prompt này KHÔNG mang gói bằng chứng, chỉ mang văn xuôi đã đóng băng và bảng
 * nghĩa vụ, nên nhỏ hơn prompt phân tích nhiều. Trần vẫn đặt bằng để một output
 * bất thường lộ ra ở đây chứ không lộ ra dưới dạng prompt bị cắt.
 */
export const MAX_DECLARATION_PROMPT_CHARS = 200_000

export interface BuiltDeclarationPrompt {
  text: string
  hash: string
  bytes: number
  promptVersion: string
  obligationCount: number
}

/**
 * Bảng nghĩa vụ, một dòng một ô.
 *
 * Trình bày THEO DÒNG chứ không JSON: mô hình phải đọc từng ô một và trả lời
 * từng ô một, và một bảng dễ đọc làm giảm khả năng nó trả lời gộp. Thứ tự là
 * thứ tự `id`, tất định.
 */
function obligationTable(set: ClaimObligationSet): string[] {
  return set.obligations.map((ob) => {
    const statuses = ob.allowedAssertionStatuses.join(' | ')
    return [
      `### ${ob.id}`,
      `  ô          : ${ob.pointer}`,
      `  chỉ số nhắc: ${ob.mentionedMetrics.join(', ')}`,
      `  trạng thái hợp lệ: ${statuses}`,
      `  VĂN BẢN    : ${ob.resolvedText}`,
    ].join('\n')
  })
}

export function buildDeclarationPrompt(input: {
  analysisPayload: unknown
  obligationSet: ClaimObligationSet
  obligationSetHash: string
  analysisPayloadHash: string
}): BuiltDeclarationPrompt {
  const { obligationSet: set } = input
  const parts: string[] = [
    '## VAI TRÒ',
    '',
    'Bạn đang ở LƯỢT HAI của một quy trình hai lượt. Lượt một đã viết xong bản',
    'phân tích và bản đó ĐÃ ĐÓNG BĂNG — bạn không sửa được, và không được đề nghị',
    'sửa. Việc của bạn ở đây là KHAI BÁO NGỮ NGHĨA cho những ô văn bản đã được',
    'chọn sẵn.',
    '',
    'Danh sách ô KHÔNG do bạn chọn. Nó được tính bằng thuật toán từ chính bản',
    'phân tích: mọi ô có nhắc impressions / CTR / thumbnail / packaging đều nằm',
    'trong đó, không thiếu, không thừa. Bạn không cần tìm, không cần đếm, và',
    'không được thêm bớt.',
    '',
    '## VIỆC PHẢI LÀM',
    '',
    `Với MỖI nghĩa vụ dưới đây, trả về đúng một mục trong \`declarations\` mang`,
    'CÙNG `id`, và điền bảy trường ngữ nghĩa:',
    '',
    '  subjectMetric  = chỉ số ĐANG BỊ PHÁN XÉT trong ô đó (tính từ mô tả nó)',
    '  relatedMetric  = chỉ số chỉ ĐƯỢC NHẮC TỚI, không bị phán xét ("NONE" nếu không có)',
    '  claimType      = ' + claimTypeEnum.options.join(' | '),
    '  judgement      = ' + judgementEnum.options.join(' | '),
    '  assertionStatus= chọn trong "trạng thái hợp lệ" ghi ở từng nghĩa vụ',
    '  evidenceIds    = evidence id của gói mà phát biểu này dựa vào (mảng, có thể rỗng)',
    '  requiresMissingnessDisclosure = true nếu phát biểu này đòi nêu rõ dữ liệu thiếu',
    '',
    'Tách rõ HAI VAI — đây là phần hay sai nhất:',
    '  "views quá thấp để ổn định CTR"  -> subject = views,       related = impression_ctr',
    '  "sample size view thấp làm CTR nhiễu" -> subject = sample_size, related = impression_ctr',
    'Chữ "thấp"/"nhiễu" mô tả views và cỡ mẫu, KHÔNG mô tả CTR. Khai đúng vai là',
    'cách duy nhất để những câu hoàn toàn hợp lệ này không bị đọc thành kết luận',
    'về CTR.',
    '',
    'Giá trị hợp lệ cho subjectMetric / relatedMetric (dùng ĐÚNG chuỗi này):',
    `  ${CLAIM_METRICS.join(', ')}`,
    '',
    '## ĐIỀU BẠN KHÔNG ĐƯỢC LÀM',
    '',
    '- KHÔNG thêm một mục nào ngoài danh sách nghĩa vụ.',
    '- KHÔNG bỏ sót một nghĩa vụ nào. Thiếu một mục là cả output bị từ chối.',
    '- KHÔNG lặp lại một `id`.',
    '- KHÔNG viết `sourceRef`, `text`, hay bất kỳ trường định vị nào. Ô đã được',
    '  chỉ định sẵn; bạn không đổi được nó và không cần nhắc lại nó.',
    '- KHÔNG sửa, viết lại, hay bình luận về văn xuôi.',
    '',
    'Thứ tự các mục trong `declarations` KHÔNG quan trọng — ghép theo `id`.',
    '',
    '## RÀNG BUỘC NGỮ NGHĨA',
    '',
    '- `assertionStatus` phải nằm trong danh sách "trạng thái hợp lệ" của chính ô đó.',
    '  Với ô NHÃN (dữ liệu cần thu thập, bằng chứng còn thiếu, câu hỏi rà soát),',
    '  `ASSERTED` KHÔNG có trong danh sách: một cái nhãn không khẳng định gì.',
    '- `ASSERTED` + `judgement` khác UNKNOWN/NOT_APPLICABLE về một chỉ số có độ phủ',
    '  0% sẽ bị TỪ CHỐI. Nếu ô là kế hoạch đo hay giới hạn phương pháp thì khai đúng loại.',
    '- `claimType` = CAUSAL luôn phải có `evidenceIds`, và CAUSAL + ASSERTED bị cấm.',
    '- METHODOLOGY_LIMITATION bắt buộc `subjectMetric` KHÁC `relatedMetric`.',
    '- Bằng chứng được trích phải NÓI VỀ chính `subjectMetric`; trích một quan sát',
    '  về chỉ số khác sẽ bị đánh dấu cần người rà soát.',
    '',
    '## HÌNH DẠNG OUTPUT',
    '',
    'Trả về DUY NHẤT một object JSON. KHÔNG văn bản ngoài JSON, KHÔNG khối ```.',
    '',
    '  {',
    `    "schemaVersion": "${DECLARATION_SCHEMA_VERSION}",`,
    `    "obligationSetHash": "${input.obligationSetHash}",`,
    '    "declarations": [',
    '      {',
    '        "id": "MC-001",',
    '        "subjectMetric": "views",',
    '        "relatedMetric": "impression_ctr",',
    '        "claimType": "METHODOLOGY_LIMITATION",',
    '        "judgement": "LOW",',
    '        "assertionStatus": "LIMITATION",',
    '        "evidenceIds": [],',
    '        "requiresMissingnessDisclosure": false',
    '      }',
    '    ]',
    '  }',
    '',
    '`obligationSetHash` phải SAO CHÉP NGUYÊN VĂN giá trị ở trên. Nó neo bản khai',
    'của bạn vào đúng bảng nghĩa vụ này; sai một ký tự là output bị từ chối.',
    '',
    `## BẢN PHÂN TÍCH ĐÃ ĐÓNG BĂNG (chỉ để ĐỌC HIỂU ngữ cảnh)`,
    '',
    stableStringify(input.analysisPayload),
    '',
    `## NGHĨA VỤ KHAI BÁO — ${set.obligations.length} mục`,
    '',
    ...obligationTable(set),
    '',
    `Trả về đúng ${set.obligations.length} mục trong \`declarations\`, và chỉ JSON.`,
  ]

  const text = parts.join('\n')
  if (text.length > MAX_DECLARATION_PROMPT_CHARS) {
    throw new Error(
      `Prompt khai báo vượt trần: ${text.length} > ${MAX_DECLARATION_PROMPT_CHARS} ký tự.`,
    )
  }
  return {
    text,
    hash: createHash('sha256').update(text, 'utf8').digest('hex'),
    bytes: Buffer.byteLength(text, 'utf8'),
    promptVersion: DECLARATION_PROMPT_VERSION,
    obligationCount: set.obligations.length,
  }
}

/**
 * Prompt SỬA LỖI của lượt khai báo.
 *
 * Cố ý KHÔNG gửi lại bản phân tích: lỗi ở lượt này là lỗi hình dạng hoặc lỗi
 * khai thiếu/thừa, và gửi lại toàn bộ văn xuôi chỉ mở đường cho mô hình bắt đầu
 * bình luận về nó. Bảng nghĩa vụ thì PHẢI gửi lại, vì đó là thứ nó phải trả lời
 * cho đủ.
 */
export function buildDeclarationRepairPrompt(params: {
  errors: string[]
  invalidOutput: string
  obligationSet: ClaimObligationSet
  obligationSetHash: string
  maxOutputChars?: number
}): { text: string; hash: string; truncated: boolean } {
  const cap = params.maxOutputChars ?? 150_000
  const truncated = params.invalidOutput.length > cap
  const excerpt = truncated
    ? `${params.invalidOutput.slice(0, cap)}\n...[đã cắt bớt]`
    : params.invalidOutput

  const text = [
    '## SỬA LẠI BẢN KHAI BÁO',
    '',
    'Bản khai trước KHÔNG hợp lệ. Các lỗi cần sửa:',
    ...params.errors.map((e, i) => `${i + 1}. ${e}`),
    '',
    '## HỢP ĐỒNG (không đổi)',
    `Trả về DUY NHẤT một object JSON, schemaVersion = "${DECLARATION_SCHEMA_VERSION}".`,
    `\`obligationSetHash\` phải đúng bằng "${params.obligationSetHash}".`,
    'KHÔNG văn bản ngoài JSON. KHÔNG khối ```.',
    '',
    'GIỮ NGUYÊN mọi phán xét ngữ nghĩa bạn đã khai đúng. Chỉ sửa những lỗi ở trên.',
    'Đổi `subjectMetric`/`judgement`/`assertionStatus` của một mục vốn đã hợp lệ',
    'là ĐỔI KẾT LUẬN, không phải sửa định dạng — và sẽ bị chặn.',
    '',
    `Danh sách nghĩa vụ KHÔNG đổi: đúng ${params.obligationSet.obligations.length} mục,`,
    `id từ ${params.obligationSet.obligations[0]?.id ?? '(rỗng)'} tới ` +
      `${params.obligationSet.obligations[params.obligationSet.obligations.length - 1]?.id ?? '(rỗng)'}.`,
    '',
    '## NGHĨA VỤ',
    '',
    ...obligationTable(params.obligationSet),
    '',
    '## BẢN KHAI KHÔNG HỢP LỆ',
    excerpt,
    '',
    'Trả về JSON đã sửa, và chỉ JSON.',
  ].join('\n')

  return { text, hash: createHash('sha256').update(text, 'utf8').digest('hex'), truncated }
}
