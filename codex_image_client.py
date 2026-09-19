"""
Client sinh ảnh qua Codex CLI (OpenAI) -- tool `imagegen` built-in, chất
lượng vượt trội hẳn ComfyUI/SDXL-Turbo (đã test trực tiếp trên 1 ảnh mẫu:
tay đúng giải phẫu, ánh sáng/composition đẹp như tranh vẽ tay thật -- xem
lịch sử hội thoại). Nhưng đây KHÔNG phải API ảnh chuyên dụng -- Codex chạy
qua 1 coding-agent CLI đầy đủ vòng lặp reasoning, nên tốn RẤT NHIỀU token
mỗi lần gọi (~37K token cho 1 ảnh test) -- gần chắc chắn hết quota rất
nhanh khi sinh hàng loạt 100+ ảnh/tập. Vì vậy đây là TẦNG 1 trong chuỗi
fallback 3 tầng: Codex (hết token) -> agy (hết quota) -> ComfyUI (local,
không quota) -- xem asset_generation.py.

Sandbox của Codex CHẶN ghi file ra ngoài thư mục làm việc (đã xác nhận
qua test: yêu cầu lưu vào /tmp bị từ chối "Operation not permitted") --
vì vậy KHÔNG yêu cầu Codex tự lưu vào output_path tuỳ ý; để nó lưu đúng
vị trí mặc định của tool imagegen (~/.codex/generated_images/<session_id>/),
rồi client này tự tìm + copy file sang cache path của ta.

Không có API JSON sạch để gọi -- chạy `codex exec` qua subprocess, parse
"session id: <uuid>" trong output để biết đúng thư mục cần tìm file mới
sinh (không quét toàn bộ generated_images/ -- tránh nhặt nhầm ảnh từ
session khác chạy song song/trước đó).
"""
import re
import subprocess
from pathlib import Path

from content_seo import CODEX_BIN, _codex_subprocess_env  # resolve "codex"/"node" bare-name an toàn dưới launchd, xem ghi chú ở đó

CODEX_GENERATED_DIR = Path.home() / ".codex" / "generated_images"
CODEX_TIMEOUT_S = 180

_SESSION_ID_RE = re.compile(r"session id:\s*([0-9a-f-]+)")

_QUOTA_KEYWORDS = (
    "quota", "rate limit", "insufficient_quota", "usage limit",
    "token limit", "out of credits", "usage_limit_reached",
)


class CodexImageError(RuntimeError):
    pass


class CodexQuotaExceededError(CodexImageError):
    """Raise riêng để caller (asset_generation.py) bật circuit breaker và
    chuyển sang tầng fallback tiếp theo (agy), không nhầm với lỗi khác."""
    pass


def generate_image(prompt_text: str, output_path: Path, timeout_s: float = CODEX_TIMEOUT_S) -> Path:
    prompt = f"Dùng tool imagegen để sinh 1 ảnh minh hoạ, không cần lưu ra vị trí nào khác: {prompt_text}"
    try:
        result = subprocess.run(
            [CODEX_BIN, "exec", "--skip-git-repo-check", prompt],
            capture_output=True, text=True, timeout=timeout_s,
            env=_codex_subprocess_env(),
        )
    except subprocess.TimeoutExpired:
        raise CodexImageError(f"Codex timeout sau {timeout_s}s.")
    except FileNotFoundError:
        raise CodexImageError("Chưa cài Codex CLI (npm install -g @openai/codex).")

    stdout = result.stdout
    combined = stdout + result.stderr
    if any(kw in combined.lower() for kw in _QUOTA_KEYWORDS):
        raise CodexQuotaExceededError(f"Codex hết token/quota: {combined[-500:]}")
    if result.returncode != 0:
        raise CodexImageError(f"Codex lỗi (exit {result.returncode}): {combined[-1000:]}")

    session_match = _SESSION_ID_RE.search(stdout)
    if not session_match:
        raise CodexImageError(f"Không tìm thấy session id trong output Codex: {stdout[-500:]}")
    session_dir = CODEX_GENERATED_DIR / session_match.group(1)
    if not session_dir.exists():
        raise CodexImageError(f"Codex báo hoàn tất nhưng thư mục ảnh không tồn tại: {session_dir}")

    candidates = sorted(session_dir.rglob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise CodexImageError(f"Không tìm thấy file .png nào trong {session_dir}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(candidates[0].read_bytes())
    return output_path
