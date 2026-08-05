import { mkdtempSync, writeFileSync, chmodSync, readFileSync, existsSync, symlinkSync, mkdirSync, readdirSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'

import { afterAll, describe, expect, it } from 'vitest'

import { CURSOR_EXECUTABLE, ensureSandbox, extractJson, resolveExecutable, runCursor } from '@/lib/cursor/exec'

/**
 * Kiểm soát an toàn của lớp gọi tiến trình con.
 *
 * Dùng script giả thay cho Cursor thật để dựng được các ca biên (timeout, exit
 * khác 0, output khổng lồ, stderr chứa secret) một cách tất định. Cursor THẬT
 * được kiểm ở `tests/integration/cursor-real.test.ts` và ở lần chạy 3 kênh.
 */
const dir = mkdtempSync(join(tmpdir(), 'cursor-exec-'))

/**
 * Sandbox RỖNG mới cho mỗi lần chạy.
 *
 * `ensureSandbox` nay đòi thư mục rỗng — Cursor chạy với `--trust` ở đó, nên
 * mọi tệp trong thư mục đều đọc được. Thư mục `dir` dùng chung có chứa script
 * giả, nên không dùng làm sandbox được nữa.
 */
function freshSandbox(): string {
  return mkdtempSync(join(tmpdir(), 'cursor-sb-'))
}

function fakeTool(name: string, body: string): string {
  const path = join(dir, name)
  writeFileSync(path, `#!/bin/sh\n${body}\n`, { mode: 0o755 })
  chmodSync(path, 0o755)
  return path
}

describe('sandbox', () => {
  it('tạo thư mục nếu chưa có', () => {
    const target = join(dir, 'sb', 'nested')
    const abs = ensureSandbox(target)
    expect(existsSync(abs)).toBe(true)
  })
})

describe('cách ly sandbox', () => {
  it('cấp thư mục con MỚI TINH cho mỗi lần chạy', () => {
    // Không còn cho phép `.cursor` sót lại: thư mục đó chứa cấu hình/chỉ dẫn dự
    // án và chạy với --trust, nên một `.cursor` cũ hoặc bị chèn có thể ảnh
    // hưởng lần chạy sau. Mỗi lần chạy được một thư mục rỗng thật.
    const root = mkdtempSync(join(tmpdir(), 'sbroot-'))
    const a = ensureSandbox(root)
    const b = ensureSandbox(root)
    expect(a).not.toBe(b)
    expect(readdirSync(a)).toHaveLength(0)
    expect(readdirSync(b)).toHaveLength(0)
  })

  it('từ chối thư mục nằm trong git repository', () => {
    // Chặn thẳng `--sandbox <repo>`: Cursor chạy với --trust ở thư mục làm việc.
    const root = mkdtempSync(join(tmpdir(), 'gitrepo-'))
    mkdirSync(join(root, '.git'))
    expect(() => ensureSandbox(join(root, 'sub'))).toThrow(/git repository/)
  })

  it('từ chối symlink', () => {
    // lstat chứ không stat: stat đi theo symlink nên symlink-tới-repo sẽ trông
    // như thư mục bình thường và lọt qua.
    const base = mkdtempSync(join(tmpdir(), 'symlink-'))
    const real = join(base, 'real')
    mkdirSync(real)
    const link = join(base, 'link')
    symlinkSync(real, link)
    expect(() => ensureSandbox(link)).toThrow(/symlink/)
  })

  it('chấp nhận thư mục rỗng', () => {
    const target = mkdtempSync(join(tmpdir(), 'empty-'))
    expect(() => ensureSandbox(target)).not.toThrow()
  })
})

describe('phân giải tệp thực thi', () => {
  it('trả về ĐƯỜNG DẪN TUYỆT ĐỐI, không phải tên trần', () => {
    const toolDir = mkdtempSync(join(tmpdir(), 'resolve-'))
    writeFileSync(join(toolDir, 'cursor-agent'), '#!/bin/sh\necho x\n', { mode: 0o755 })
    chmodSync(join(toolDir, 'cursor-agent'), 0o755)
    const saved = process.env.PATH
    process.env.PATH = `${toolDir}:${saved}`
    try {
      const p = resolveExecutable()
      expect(p.startsWith('/')).toBe(true)
      expect(p).toContain('cursor-agent')
    } finally {
      process.env.PATH = saved
    }
  })

  it('báo lỗi rõ ràng khi không tìm thấy', () => {
    const saved = process.env.PATH
    const savedOverride = process.env.CURSOR_AGENT_PATH
    process.env.PATH = mkdtempSync(join(tmpdir(), 'nopath-'))
    delete process.env.CURSOR_AGENT_PATH
    try {
      expect(() => resolveExecutable()).toThrow(/Không tìm thấy/)
    } finally {
      process.env.PATH = saved
      if (savedOverride !== undefined) process.env.CURSOR_AGENT_PATH = savedOverride
    }
  })
})

describe('tên chương trình cố định', () => {
  it('chỉ chạy đúng cursor-agent, không lấy từ dữ liệu', () => {
    // Nếu hằng này thành biến lấy từ payload thì backend có thể chỉ định chạy
    // bất kỳ chương trình nào trên máy worker.
    expect(CURSOR_EXECUTABLE).toBe('cursor-agent')
  })
})

describe('bóc JSON', () => {
  it('không bị ngoặc trong chuỗi đánh lừa', () => {
    const r = extractJson('prefix {"note":"a } b","x":1} suffix')
    expect(JSON.parse(r.json!)).toEqual({ note: 'a } b', x: 1 })
  })

  it('bỏ qua escape trong chuỗi', () => {
    const r = extractJson('{"s":"a\\"}\\"b","n":2}')
    expect(JSON.parse(r.json!)).toEqual({ s: 'a"}"b', n: 2 })
  })

  it('JSON chưa đóng -> null', () => {
    expect(extractJson('{"a":1').json).toBeNull()
  })
})

/**
 * Các ca dưới đây gọi `runCursor` với PATH trỏ vào thư mục chứa script giả tên
 * `cursor-agent`, nhờ đó kiểm được hành vi tiến trình mà không cần Cursor thật.
 */
describe('hành vi tiến trình con', () => {
  async function withFakeTool<T>(body: string, fn: () => Promise<T>): Promise<T> {
    const toolDir = mkdtempSync(join(tmpdir(), 'faketool-'))
    writeFileSync(join(toolDir, 'cursor-agent'), `#!/bin/sh\n${body}\n`, { mode: 0o755 })
    chmodSync(join(toolDir, 'cursor-agent'), 0o755)
    const savedPath = process.env.PATH
    process.env.PATH = `${toolDir}:${savedPath}`
    try {
      return await fn()
    } finally {
      process.env.PATH = savedPath
    }
  }

  it('bắt stdout và tính băm', async () => {
    const r = await withFakeTool('echo \'{"ok":true}\'', () =>
      runCursor({ prompt: 'x', sandboxDir: freshSandbox() }),
    )
    expect(r.stdout.trim()).toBe('{"ok":true}')
    expect(r.exitCode).toBe(0)
    expect(r.stdoutHash).toMatch(/^[0-9a-f]{64}$/)
  })

  it('exit code khác 0 được ghi nhận, không ném lỗi', async () => {
    const r = await withFakeTool('echo boom >&2; exit 3', () =>
      runCursor({ prompt: 'x', sandboxDir: freshSandbox() }),
    )
    expect(r.exitCode).toBe(3)
    expect(r.timedOut).toBe(false)
  })

  it('timeout thì giết tiến trình và đánh dấu', async () => {
    const r = await withFakeTool('sleep 30', () =>
      runCursor({ prompt: 'x', sandboxDir: freshSandbox(), timeoutMs: 800 }),
    )
    expect(r.timedOut).toBe(true)
    expect(r.durationMs).toBeLessThan(15_000)
  }, 30_000)

  it('output vượt trần bị cắt và đánh dấu, không nuốt hết bộ nhớ', async () => {
    const r = await withFakeTool('head -c 200000 /dev/zero | tr "\\0" "a"', () =>
      runCursor({ prompt: 'x', sandboxDir: freshSandbox(), maxOutputBytes: 2_000 }),
    )
    expect(r.truncated).toBe(true)
  }, 30_000)

  it('stderr được LỌC SECRET trước khi trả về', async () => {
    // Nếu không lọc, thông báo lỗi của CLI có thể mang token vào log và database.
    const r = await withFakeTool(
      // Chuỗi GIẢ, dùng placeholder `xxx` để bộ quét bí mật nhận ra là mẫu thử
      // chứ không phải credential thật. Bộ lọc vẫn phải che nó.
      'echo "fail: postgresql://u:dummy-pw@h/db and Bearer dummy-token" >&2; echo "{}"',
      () => runCursor({ prompt: 'x', sandboxDir: freshSandbox() }),
    )
    expect(r.stderr).not.toContain('dummy-pw')
    expect(r.stderr).not.toContain('dummy-token')
    expect(r.stderr).toContain('<redacted>')
  })

  it('KHÔNG kế thừa biến môi trường nhạy cảm', async () => {
    // Kiểm soát quan trọng nhất của tệp này: Cursor gọi mạng ra ngoài, nên nó
    // tuyệt đối không được thấy DATABASE_URL hay token của worker.
    process.env.DATABASE_URL = 'postgresql://u:leakme@h/db'
    process.env.HUB_WORKER_TOKEN = 'vhw_should_not_leak'
    process.env.GITHUB_TOKEN = 'ghp_should_not_leak'
    try {
      const r = await withFakeTool('env', () => runCursor({ prompt: 'x', sandboxDir: freshSandbox() }))
      expect(r.stdout).not.toContain('leakme')
      expect(r.stdout).not.toContain('vhw_should_not_leak')
      expect(r.stdout).not.toContain('ghp_should_not_leak')
      expect(r.stdout).not.toContain('DATABASE_URL')
      // PATH vẫn phải có, nếu không thì không nạp được runtime.
      expect(r.stdout).toContain('PATH=')
    } finally {
      delete process.env.DATABASE_URL
      delete process.env.HUB_WORKER_TOKEN
      delete process.env.GITHUB_TOKEN
    }
  })

  it('prompt đi qua STDIN, KHÔNG qua tham số dòng lệnh', async () => {
    // argv hiện trong `ps` của mọi tiến trình trên máy.
    const r = await withFakeTool('cat; echo "---ARGS:$*"', () =>
      runCursor({ prompt: 'BÍ-MẬT-TRONG-PROMPT', sandboxDir: freshSandbox() }),
    )
    expect(r.stdout).toContain('BÍ-MẬT-TRONG-PROMPT') // đọc được từ stdin
    const argsLine = r.stdout.split('---ARGS:')[1] ?? ''
    expect(argsLine).not.toContain('BÍ-MẬT-TRONG-PROMPT')
  })

  it('cờ cố định và có ghi lại để kiểm toán', async () => {
    const r = await withFakeTool('echo "{}"', () => runCursor({ prompt: 'x', sandboxDir: freshSandbox() }))
    expect(r.flags).toContain('--print')
    expect(r.flags).toContain('--mode')
    expect(r.flags).toContain('ask') // chế độ chỉ đọc: không ghi tệp, không shell
    expect(r.flags).not.toContain('--yolo')
    expect(r.flags).not.toContain('-f')
  })

  it('nội dung prompt KHÔNG bị diễn giải bởi shell', async () => {
    // shell:false nên chuỗi nguy hiểm trong prompt chỉ là dữ liệu.
    const r = await withFakeTool('cat', () =>
      runCursor({ prompt: '$(touch /tmp/pwned_by_prompt); `id`; rm -rf /', sandboxDir: freshSandbox() }),
    )
    expect(r.stdout).toContain('$(touch /tmp/pwned_by_prompt)')
    expect(existsSync('/tmp/pwned_by_prompt')).toBe(false)
  })

  it('chạy trong thư mục sandbox chỉ định, không phải repo', async () => {
    const sb = freshSandbox()
    const r = await withFakeTool('pwd', () => runCursor({ prompt: 'x', sandboxDir: sb }))
    expect(r.stdout.trim()).toContain(sb.replace(/^\/private/, ''))
    expect(r.stdout).not.toContain('Vietneu-TTS/apps/hub')
  })
})

afterAll(() => {
  void readFileSync
})

describe('trần thời gian là trần THẬT', () => {
  it('lời gọi kết thúc dù tiến trình con phớt lờ tín hiệu dừng', async () => {
    // Phát hiện khi đo độ ổn định: hai lần chạy hinh_su với trần 600s lại kéo
    // dài 1016s và 1979s, không có một byte stdout nào. Gửi tín hiệu rồi chờ
    // tiếp KHÔNG phải là timeout — promise phải tự chốt khi hết hạn.
    const toolDir = mkdtempSync(join(tmpdir(), 'hangtool-'))
    // Phớt lờ SIGTERM và giữ tiến trình sống thật lâu.
    writeFileSync(join(toolDir, 'cursor-agent'), "#!/bin/sh\ntrap '' TERM\nsleep 120\n", { mode: 0o755 })
    chmodSync(join(toolDir, 'cursor-agent'), 0o755)
    const saved = process.env.PATH
    process.env.PATH = `${toolDir}:${saved}`
    try {
      const sb = mkdtempSync(join(tmpdir(), 'cursor-sb-'))
      const r = await runCursor({ prompt: 'x', sandboxDir: sb, timeoutMs: 1_000 })
      expect(r.timedOut).toBe(true)
      // 1s trần + 15s chặn cứng + dư địa; tuyệt đối không được tới 120s.
      expect(r.durationMs).toBeLessThan(30_000)
    } finally {
      process.env.PATH = saved
    }
  }, 60_000)
})

describe('giải đường dẫn --out', () => {
  it('tính theo cwd, KHÔNG cộng thêm ".." ngầm định', async () => {
    // Bản trước dùng resolve(cwd, '..', '..', outDir): mặc định "cwd là apps/hub
    // VÀ outDir tính từ gốc repo". Chạy từ apps/hub với --out ../../analysis_out
    // thì hai giả định cộng lại thành <repo>/../../analysis_out — ghi RA NGOÀI
    // repo, trong khi analysis_out/ trong repo vẫn giữ kết quả cũ và trông như
    // vừa cập nhật.
    const { resolveOutDir } = await import('@/db/run-cursor')
    const cwd = process.cwd()
    expect(resolveOutDir('analysis_out')).toBe(join(cwd, 'analysis_out'))
    expect(resolveOutDir('../../analysis_out')).toBe(
      resolve(cwd, '../../analysis_out'),
    )
    // Không bao giờ được leo thêm hai bậc ngoài ý muốn.
    expect(resolveOutDir('analysis_out')).not.toContain('..')
  })
})
