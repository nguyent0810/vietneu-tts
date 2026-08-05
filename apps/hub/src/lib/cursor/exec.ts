import { spawn, type ChildProcessWithoutNullStreams } from 'node:child_process'
import { createHash } from 'node:crypto'
import { existsSync, lstatSync, mkdirSync, mkdtempSync, realpathSync, statSync } from 'node:fs'
import { delimiter, dirname, join, resolve } from 'node:path'

import { scrubSecrets } from '../errors'

/**
 * Vỏ bọc tiến trình con cho Cursor CLI.
 *
 * Các kiểm soát an toàn, và lý do từng cái tồn tại:
 *
 *  - ALLOWLIST tệp thực thi: chỉ chạy đúng `cursor-agent`. Không có đường nào
 *    để tên chương trình đến từ dữ liệu.
 *  - KHÔNG dùng shell: `spawn` với mảng đối số, `shell: false`. Nội dung prompt
 *    không bao giờ đi qua trình thông dịch shell, nên không có chuyện chèn lệnh.
 *  - Prompt truyền qua STDIN, không qua argv: argv hiện trong `ps` của mọi tiến
 *    trình trên máy.
 *  - ALLOWLIST biến môi trường: tiến trình con chỉ thấy đúng những biến được
 *    liệt kê. Kế thừa nguyên `process.env` sẽ trao cả DATABASE_URL,
 *    HUB_WORKER_TOKEN, GITHUB_TOKEN, HF_TOKEN cho một tiến trình gọi mạng ra
 *    ngoài — đây là kiểm soát quan trọng nhất trong tệp này.
 *  - Thư mục làm việc bị GIỚI HẠN vào một sandbox rỗng, không phải repo. Cursor
 *    chạy ở chế độ `ask` (chỉ đọc, không có công cụ ghi/shell), nhưng thư mục
 *    làm việc vẫn phải là nơi không có gì để đọc.
 *  - Giới hạn TIMEOUT và KÍCH THƯỚC output, kèm dọn tiến trình con.
 *  - stderr được LỌC SECRET trước khi lưu hoặc ghi log.
 */

export const CURSOR_EXECUTABLE = 'cursor-agent'

/**
 * Biến môi trường DUY NHẤT được truyền xuống.
 *
 * Cursor tự lo xác thực qua đăng nhập đã lưu của nó; ta không truyền API key.
 * PATH cần để nạp runtime; HOME cần để Cursor đọc cấu hình của chính nó.
 */
const ENV_ALLOWLIST = ['PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR'] as const

export const DEFAULT_TIMEOUT_MS = 600_000
export const DEFAULT_MAX_OUTPUT_BYTES = 2_000_000

export interface CursorExecOptions {
  prompt: string
  sandboxDir: string
  timeoutMs?: number
  maxOutputBytes?: number
  model?: string
  signal?: AbortSignal
}

export interface CursorExecResult {
  stdout: string
  stderr: string
  stdoutHash: string
  stderrHash: string
  stdoutBytes: number
  exitCode: number | null
  timedOut: boolean
  truncated: boolean
  durationMs: number
  startedAt: Date
  finishedAt: Date
  flags: string[]
  toolName: string
}

function buildEnv(): Record<string, string> {
  // Record<string,string> chứ không phải NodeJS.ProcessEnv: kiểu đó (qua
  // @types/node của Next) bắt buộc có NODE_ENV, mà ta CỐ Ý không truyền biến
  // nào ngoài allowlist.
  const env: Record<string, string> = {}
  for (const key of ENV_ALLOWLIST) {
    const value = process.env[key]
    if (value !== undefined) env[key] = value
  }
  return env
}

/**
 * Sandbox phải TỒN TẠI, phải RỖNG, và không được là symlink.
 *
 * Cursor được cấp `--trust` cho thư mục làm việc; trỏ vào repo nghĩa là trao
 * quyền đọc toàn bộ mã nguồn và mọi tệp `.env` chưa gitignore ở đó.
 *
 * Bản đầu chỉ `mkdir -p` rồi trả về, nên `--sandbox <repo>` hay `--sandbox
 * <symlink tới repo>` đều được chấp nhận lặng lẽ. Kết hợp với `--trust` và khả
 * năng prompt-injection từ tiêu đề/mô tả video, đó là đường đọc tệp ngoài phạm
 * vi. Ba kiểm tra dưới đây đóng đường đó, và đều FAIL-CLOSED.
 */
export function ensureSandbox(dir: string): string {
  const root = resolve(dir)

  if (existsSync(root)) {
    // lstat chứ không stat: stat đi theo symlink nên symlink-tới-repo sẽ trông
    // như một thư mục bình thường và lọt qua.
    const st = lstatSync(root)
    if (st.isSymbolicLink()) throw new Error(`Sandbox không được là symlink: ${root}`)
    if (!st.isDirectory()) throw new Error(`Sandbox phải là thư mục: ${root}`)
  } else {
    mkdirSync(root, { recursive: true })
  }

  // KHÔNG được là repo, và không được nằm trong repo.
  //
  // Đây là cách trực tiếp nhất để chặn `--sandbox <repo>`: Cursor chạy với
  // `--trust` ở thư mục làm việc, nên trỏ vào cây mã nguồn là trao quyền đọc
  // toàn bộ mã và mọi tệp `.env` chưa gitignore.
  //
  // Phải đi trên ĐƯỜNG DẪN THẬT, không phải đường dẫn chữ nghĩa. Chỉ lstat mỗi
  // nút cuối rồi duyệt cha theo chuỗi ký tự sẽ bỏ lọt tổ tiên là symlink:
  //   /tmp/alias -> /repo/private/sub
  //   sandbox    =  /tmp/alias/cursor-sandbox
  // Nút cuối là thư mục thường, còn phép duyệt chữ nghĩa chỉ thấy /tmp/... nên
  // không bao giờ chạm /repo/.git — và sandbox "an toàn" lại nằm trong repo.
  const realRoot = realpathSync(root)
  for (let d = realRoot; ; ) {
    if (existsSync(resolve(d, '.git'))) {
      throw new Error(
        `Sandbox không được nằm trong một git repository: ${root} ` +
          `(đường dẫn thật ${realRoot}, thấy .git ở ${d}). ` +
          `Dùng một thư mục tạm nằm ngoài cây mã nguồn.`,
      )
    }
    const parent = dirname(d)
    if (parent === d) break
    d = parent
  }

  // Mỗi lần chạy được cấp một thư mục con MỚI TINH.
  //
  // Bản trước cho phép tồn tại sẵn `.cursor` để dùng lại sandbox. Nhưng `.cursor`
  // chính là nơi chứa cấu hình/chỉ dẫn dự án, và thư mục này chạy với `--trust`:
  // một `.cursor` cũ hoặc bị chèn nội dung có thể ảnh hưởng lần chạy sau. Cấp
  // thư mục mới mỗi lần vừa bảo đảm RỖNG THẬT, vừa vẫn cho phép tái dùng gốc.
  return mkdtempSync(join(realRoot, 'run-'))
}

/**
 * Phân giải tệp thực thi thành ĐƯỜNG DẪN TUYỆT ĐỐI, đã bỏ symlink.
 *
 * Spawn bằng tên trần `cursor-agent` nghĩa là thứ được chạy là tệp trùng tên
 * ĐẦU TIÊN trên PATH — tức là PATH quyết định, không phải ta. Một PATH bị sửa
 * (hoặc một thư mục ghi được đứng trước trong PATH) đủ để thay thế binary, và
 * binary đó nhận trọn prompt qua stdin.
 *
 * Phân giải ở đây không loại bỏ được mọi rủi ro — nếu PATH đã bị kiểm soát thì
 * đường dẫn phân giải ra cũng là của kẻ đó. Nhưng nó cố định MỘT đường dẫn cho
 * cả lần chạy, ghi lại đường dẫn thật vào bản kê, và biến một thay thế thầm
 * lặng thành thứ nhìn thấy được khi hậu kiểm.
 *
 * Có thể ghi đè bằng CURSOR_AGENT_PATH để trỏ tới bản cài đã biết.
 */
export function resolveExecutable(): string {
  const override = process.env.CURSOR_AGENT_PATH
  if (override) {
    const abs = resolve(override)
    if (!existsSync(abs)) throw new Error(`CURSOR_AGENT_PATH không tồn tại: ${abs}`)
    return realpathSync(abs)
  }
  const dirs = (process.env.PATH ?? '').split(delimiter).filter(Boolean)
  for (const d of dirs) {
    const candidate = resolve(d, CURSOR_EXECUTABLE)
    if (!existsSync(candidate)) continue
    const real = realpathSync(candidate)
    const st = statSync(real)
    if (!st.isFile()) continue
    // Bỏ qua thư mục AI CŨNG GHI ĐƯỢC.
    //
    // Một thư mục ghi được cho group/other đứng trước trong PATH là đường thay
    // thế binary kinh điển, và binary đó nhận trọn prompt qua stdin. Đây không
    // phải hàng rào tuyệt đối (xem giới hạn đã ghi nhận), nhưng loại bỏ được
    // trường hợp dễ khai thác nhất.
    const dirStat = statSync(dirname(real))
    // eslint-disable-next-line no-bitwise
    if ((dirStat.mode & 0o022) !== 0) continue
    return real
  }
  throw new Error(
    `Không tìm thấy "${CURSOR_EXECUTABLE}" trên PATH. ` +
      `Đặt CURSOR_AGENT_PATH nếu nó nằm ngoài PATH.`,
  )
}

export async function runCursor(options: CursorExecOptions): Promise<CursorExecResult> {
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS
  const maxOutputBytes = options.maxOutputBytes ?? DEFAULT_MAX_OUTPUT_BYTES
  const cwd = ensureSandbox(options.sandboxDir)

  // Đối số CỐ ĐỊNH. Không có mảnh nào đến từ dữ liệu người dùng hay backend.
  //  --print       : không tương tác
  //  --output-format text : trả thẳng văn bản, ta tự parse JSON
  //  --mode ask    : CHỈ ĐỌC — không công cụ ghi, không shell
  //  --trust       : tin thư mục sandbox rỗng (bắt buộc cho phi tương tác)
  const flags = ['--print', '--output-format', 'text', '--mode', 'ask', '--trust']
  if (options.model) flags.push('--model', options.model)

  const startedAt = new Date()
  const started = Date.now()

  // Phân giải MỘT LẦN trước khi chạy, và ghi lại đường dẫn thật vào kết quả.
  const executablePath = resolveExecutable()

  return new Promise<CursorExecResult>((resolvePromise, rejectPromise) => {
    const child: ChildProcessWithoutNullStreams = spawn(executablePath, flags, {
      cwd,
      // Ép kiểu vì @types/node khai NODE_ENV là bắt buộc, còn allowlist ở đây
      // CỐ Ý không có nó — tiến trình con chỉ được thấy đúng những biến liệt kê.
      env: buildEnv() as NodeJS.ProcessEnv,
      shell: false, // không bao giờ bật: prompt sẽ thành lệnh shell
      stdio: ['pipe', 'pipe', 'pipe'],
      // Tách nhóm tiến trình để giết được CẢ CÂY con.
      //
      // Không có nó, `kill()` chỉ hạ tiến trình gốc; tiến trình cháu vẫn sống
      // và vẫn GIỮ ống stdout, nên sự kiện 'close' không bao giờ phát ra và
      // lời gọi treo vĩnh viễn — kể cả khi timeout đã kích hoạt. Test timeout
      // là thứ phát hiện ra điều này.
      detached: true,
    })

    let stdout = ''
    let stderr = ''
    let stdoutBytes = 0
    let truncated = false
    let timedOut = false
    let settled = false

    /** Giết cả NHÓM tiến trình (pid âm), không chỉ tiến trình gốc. */
    const killTree = (signal: NodeJS.Signals): void => {
      if (child.pid === undefined) return
      try {
        process.kill(-child.pid, signal)
      } catch {
        // Nhóm đã chết hoặc chưa kịp tạo -> thử hạ riêng tiến trình gốc.
        try {
          child.kill(signal)
        } catch {
          /* đã kết thúc */
        }
      }
    }

    const terminate = (): void => {
      // SIGTERM trước, SIGKILL sau: cho cơ hội dọn dẹp, nhưng không để sống mãi.
      killTree('SIGTERM')
      setTimeout(() => {
        if (!settled) killTree('SIGKILL')
      }, 3_000)
    }

    /**
     * Chốt kết quả và NGỪNG chờ tiến trình con.
     *
     * Tách riêng khỏi handler 'exit' vì có trường hợp 'exit' không bao giờ đến.
     */
    const settle = (code: number | null): void => {
      if (settled) return
      settled = true
      clearTimeout(timer)
      clearTimeout(hardStop)
      options.signal?.removeEventListener('abort', onAbort)
      const cleanStderr = scrubSecrets(stderr)
      resolvePromise({
        stdout,
        stderr: cleanStderr,
        stdoutHash: createHash('sha256').update(stdout, 'utf8').digest('hex'),
        stderrHash: createHash('sha256').update(cleanStderr, 'utf8').digest('hex'),
        stdoutBytes,
        exitCode: code,
        timedOut,
        truncated,
        durationMs: Date.now() - started,
        startedAt,
        finishedAt: new Date(),
        flags,
        toolName: executablePath,
      })
    }

    const timer = setTimeout(() => {
      timedOut = true
      terminate()
    }, timeoutMs)

    /**
     * CHẶN CỨNG: hết hạn thì lời gọi PHẢI kết thúc, dù tiến trình con có chết hay không.
     *
     * Không có nó, timeout chỉ là "gửi tín hiệu rồi chờ tiếp" — và nếu tiến
     * trình con không chết, promise chờ mãi. Điều này đã xảy ra thật khi đo độ
     * ổn định: hai lần chạy hinh_su với trần 600s lại kéo dài 1016s và 1979s,
     * đều không có một byte stdout nào. Một cái trần bị vượt 400% thì không còn
     * là trần; nó chỉ tạo cảm giác có giới hạn.
     *
     * Cộng thêm 15s so với timeout để SIGTERM rồi SIGKILL có cơ hội tác dụng
     * trước khi ta bỏ cuộc và tự chốt.
     */
    const hardStop = setTimeout(() => {
      if (settled) return
      timedOut = true
      killTree('SIGKILL')
      settle(null)
    }, timeoutMs + 15_000)

    const onAbort = terminate
    options.signal?.addEventListener('abort', onAbort, { once: true })

    child.stdout.on('data', (chunk: Buffer) => {
      stdoutBytes += chunk.length
      if (stdoutBytes > maxOutputBytes) {
        // Chặn ngay khi vượt trần thay vì tích trữ vô hạn: output khổng lồ là
        // một cách làm cạn bộ nhớ.
        truncated = true
        terminate()
        return
      }
      stdout += chunk.toString('utf8')
    })

    child.stderr.on('data', (chunk: Buffer) => {
      if (stderr.length < 64_000) stderr += chunk.toString('utf8')
    })

    child.on('error', (err) => {
      if (settled) return
      settled = true
      clearTimeout(timer)
      clearTimeout(hardStop)
      options.signal?.removeEventListener('abort', onAbort)
      rejectPromise(new Error(`Không chạy được ${CURSOR_EXECUTABLE}: ${scrubSecrets(err.message)}`))
    })

    // Dùng 'exit' chứ không dùng 'close': 'close' chỉ phát khi MỌI ống stdio
    // đã đóng, mà tiến trình cháu còn sống vẫn giữ ống — nên 'close' có thể
    // không bao giờ đến. 'exit' phát ngay khi tiến trình gốc kết thúc.
    // Lọc secret TRƯỚC khi bất kỳ ai nhìn thấy stderr: thông báo lỗi của CLI
    // có thể mang theo token hoặc URL kèm tham số nhạy cảm — xử lý trong settle().
    child.on('exit', (code) => settle(code))

    child.stdin.on('error', () => {
      /* tiến trình con có thể đóng stdin sớm; không phải lỗi cần báo */
    })
    child.stdin.write(options.prompt, 'utf8')
    child.stdin.end()
  })
}

/**
 * Lấy object JSON từ stdout.
 *
 * Cursor đôi khi bọc JSON trong khối ``` hoặc thêm một câu dẫn, dù prompt đã
 * cấm. Bóc phần bao đó KHÔNG phải là dung túng: `hadProseOutsideJson` được trả
 * về và bộ kiểm định vẫn ghi nhận vi phạm — nhưng ta không vứt bỏ một phân tích
 * đúng chỉ vì cái vỏ.
 */
export function extractJson(stdout: string): {
  json: string | null
  hadProseOutsideJson: boolean
  /**
   * Văn bản NGOÀI object JSON.
   *
   * Trước đây phần này bị vứt đi và chỉ để lại một cờ mức MEDIUM, nên mô hình
   * có thể viết "Thumbnail kém đã làm giảm lượt xem và CTR đang thấp." ở ngoài
   * rồi kèm một JSON sạch — câu vi phạm không bao giờ được kiểm, và lần chạy
   * vẫn được ghi SUCCEEDED. Nay phần này được trả về để kiểm định quét.
   */
  proseText: string
} {
  const trimmed = stdout.trim()
  if (!trimmed) return { json: null, hadProseOutsideJson: false, proseText: '' }

  if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
    return { json: trimmed, hadProseOutsideJson: false, proseText: '' }
  }

  const fenced = /```(?:json)?\s*(\{[\s\S]*?\})\s*```/.exec(trimmed)
  if (fenced?.[1]) return { json: fenced[1], hadProseOutsideJson: true, proseText: trimmed.replace(fenced[1], ' ') }

  // Cân bằng ngoặc từ dấu `{` đầu tiên, có bỏ qua ngoặc nằm trong chuỗi.
  const start = trimmed.indexOf('{')
  if (start === -1) return { json: null, hadProseOutsideJson: true, proseText: trimmed }

  let depth = 0
  let inString = false
  let escaped = false
  for (let i = start; i < trimmed.length; i++) {
    const ch = trimmed[i]!
    if (escaped) {
      escaped = false
      continue
    }
    if (ch === '\\') {
      escaped = true
      continue
    }
    if (ch === '"') {
      inString = !inString
      continue
    }
    if (inString) continue
    if (ch === '{') depth++
    else if (ch === '}') {
      depth--
      if (depth === 0) {
        return {
          json: trimmed.slice(start, i + 1),
          hadProseOutsideJson: true,
          proseText: trimmed.slice(0, start) + ' ' + trimmed.slice(i + 1),
        }
      }
    }
  }

  return { json: null, hadProseOutsideJson: true, proseText: trimmed }
}
