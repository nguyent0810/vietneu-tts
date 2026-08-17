import { createHash } from 'node:crypto'

import Anthropic from '@anthropic-ai/sdk'

import { DEFAULT_TIMEOUT_MS, type CursorExecOptions, type CursorExecResult } from './exec'

/**
 * BỘ THỰC THI thứ hai: gọi Anthropic Messages API thay vì spawn CLI.
 *
 * Vì sao tách tệp riêng, và vì sao TRẢ ĐÚNG `CursorExecResult`:
 *
 * Toàn bộ tầng cưỡng chế sự thật — `validate.ts`, `obligation.ts`, `composite.ts`,
 * `sensitive.ts` — KHÔNG hề biết ai sinh ra văn bản. Nó kiểm VĂN BẢN, không kiểm
 * TÁC GIẢ (đã kiểm bằng grep: không tệp nào trong số đó nhắc tới nhà cung cấp).
 * Nên đổi analyst chỉ cần một bộ thực thi khác trả về cùng hình dạng kết quả;
 * không đụng một dòng nào của tầng kiểm định.
 *
 * Đó cũng là lý do tệp này KHÔNG được "tiện tay" nới bất cứ quy tắc nào. Nếu một
 * lô chạy bằng Claude qua được cổng mà lô chạy bằng Cursor thì không, khác biệt
 * phải nằm ở CHẤT LƯỢNG MÔ HÌNH, không nằm ở việc hai đường chạy được chấm bằng
 * hai thước đo.
 *
 * KHÁC BIỆT có thật so với đường CLI, ghi ra đây để không ai phải đoán:
 *
 *  - `sandboxDir` KHÔNG dùng tới. Đường CLI cần thư mục làm việc cho tiến trình
 *    con; lời gọi API thì không có tiến trình con nào. Giữ trong chữ ký để hai
 *    bộ thực thi thay thế nhau được.
 *  - `exitCode` là GIẢ LẬP: 0 khi có văn bản, 1 khi lỗi/từ chối. Không có tiến
 *    trình nào để lấy mã thoát thật.
 *  - `stderr` mang thông điệp lỗi hoặc lý do TỪ CHỐI, để lớp phân loại thất bại
 *    phía trên có cái mà đọc.
 */

/** Model mặc định. Đổi số này là đổi thước đo — lô trước/sau KHÔNG gộp. */
export const ANTHROPIC_DEFAULT_MODEL = 'claude-opus-5'

/**
 * Trần token đầu ra.
 *
 * Lô thật của đường CLI cho stdout 22–28 KB, tức khoảng 8–10 nghìn token. Đặt
 * 32000 để còn chỗ cho phần SUY NGHĨ: trên Claude Opus 5, suy nghĩ BẬT MẶC ĐỊNH
 * và `max_tokens` là trần chung cho suy nghĩ CỘNG văn bản trả về — đặt sát nhu
 * cầu văn bản sẽ bị cắt giữa câu.
 */
export const ANTHROPIC_MAX_TOKENS = 32_000

const sha256 = (s: string): string => createHash('sha256').update(s, 'utf8').digest('hex')

/**
 * Gọi Messages API và trả về đúng hợp đồng của `execCursorAgent`.
 *
 * LUÔN dùng streaming. Không phải để hiển thị dần — không ai xem — mà vì một lời
 * gọi không-streaming với `max_tokens` lớn sẽ chạm timeout HTTP của SDK. Lô thật
 * có lần thử mất 832 giây; đó đúng vùng mà streaming là bắt buộc.
 */
export async function execAnthropicMessages(options: CursorExecOptions): Promise<CursorExecResult> {
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS
  const model = options.model ?? ANTHROPIC_DEFAULT_MODEL
  const startedAt = new Date()

  const client = new Anthropic()

  /*
   * Hạn giờ do TA giữ, không phó mặc cho SDK.
   *
   * Đường CLI có trần thời gian riêng và lớp trên phân loại `CLI_TIMEOUT` từ đó.
   * Nếu ở đây để SDK tự timeout thì lỗi hiện ra dưới dạng ngoại lệ mạng chung
   * chung và mất mất phân biệt "hết giờ" với "hỏng thật".
   */
  const abort = new AbortController()
  const external = options.signal
  if (external) {
    if (external.aborted) abort.abort()
    else external.addEventListener('abort', () => abort.abort(), { once: true })
  }
  let timedOut = false
  const timer = setTimeout(() => {
    timedOut = true
    abort.abort()
  }, timeoutMs)

  let stdout = ''
  let stderr = ''
  let exitCode: number | null = 0

  try {
    const stream = client.messages.stream(
      {
        model,
        max_tokens: ANTHROPIC_MAX_TOKENS,
        /*
         * `effort: high` chứ không phải mặc định ngầm.
         *
         * Đây là bài suy luận dài trên một gói bằng chứng 50+ KB, và mức nỗ lực
         * là thứ ảnh hưởng chất lượng mạnh nhất trên dòng model này. Ghi tường
         * minh để lô sau đọc mã là biết lô này chạy ở mức nào.
         */
        output_config: { effort: 'high' },
        messages: [{ role: 'user', content: options.prompt }],
      },
      { signal: abort.signal },
    )

    const message = await stream.finalMessage()

    /*
     * TỪ CHỐI là một KẾT QUẢ, không phải một ngoại lệ.
     *
     * Bộ phân loại an toàn có thể từ chối và API vẫn trả HTTP 200 với
     * `stop_reason: "refusal"` và `content` rỗng. Mã đọc thẳng `content[0]` sẽ
     * vỡ. Phải xét `stop_reason` TRƯỚC khi đọc nội dung.
     */
    if (message.stop_reason === 'refusal') {
      const category = message.stop_details?.category ?? 'không rõ'
      exitCode = 1
      stderr = `Anthropic từ chối yêu cầu (stop_reason=refusal, category=${category})`
    } else {
      stdout = message.content
        .filter((b): b is Anthropic.TextBlock => b.type === 'text')
        .map((b) => b.text)
        .join('')
      if (message.stop_reason === 'max_tokens') {
        // KHÔNG coi là thành công im lặng: output bị cắt giữa chừng thì lớp trên
        // phải thấy, nếu không nó đem một bài phân tích cụt đi kiểm định.
        stderr = `Output bị cắt vì chạm max_tokens (${ANTHROPIC_MAX_TOKENS})`
        exitCode = 1
      }
    }
  } catch (err) {
    exitCode = 1
    stderr = timedOut
      ? `Hết giờ sau ${timeoutMs} ms`
      : `Lỗi gọi Anthropic API: ${err instanceof Error ? err.message : String(err)}`
  } finally {
    clearTimeout(timer)
  }

  const finishedAt = new Date()
  return {
    stdout,
    stderr,
    stdoutHash: sha256(stdout),
    stderrHash: sha256(stderr),
    stdoutBytes: Buffer.byteLength(stdout, 'utf8'),
    exitCode,
    timedOut,
    truncated: false,
    durationMs: finishedAt.getTime() - startedAt.getTime(),
    startedAt,
    finishedAt,
    /*
     * `flags` là bản ghi PHÁP Y của lời gọi, không phải cờ dòng lệnh.
     *
     * Đường CLI ghi cờ thật vào bản kê; ở đây ghi tham số quyết định kết quả để
     * lô sau truy được "lô này chạy model nào, nỗ lực bao nhiêu, trần bao nhiêu".
     */
    flags: [`--model=${model}`, `--effort=high`, `--max-tokens=${ANTHROPIC_MAX_TOKENS}`, '--stream'],
    toolName: `anthropic:${model}`,
  }
}
