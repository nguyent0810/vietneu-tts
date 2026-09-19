"""
Client sinh ảnh qua Cursor Agent CLI (`agent`, ~/.local/bin/agent -- lệnh
`cursor.com/install`, KHÁC HẲN `agy`/Antigravity CLI) -- model nền
"Nano Banana Pro". Đã test trực tiếp: chất lượng RÕ RÀNG cao hơn hẳn cả
Codex lẫn agy lẫn ComfyUI/SDXL-Turbo cho cùng 1 prompt (Thanh Long ink
painting) -- chữ Hán thật đọc được, không lỗi giải phẫu (móng vuốt, vảy),
bố cục điện ảnh hơn. Vì vậy đứng ĐẦU chuỗi fallback 4 tầng cho beat premium:
Cursor -> Codex -> agy -> ComfyUI (xem asset_generation.py).

QUAN TRỌNG -- khác biệt rủi ro so với 3 tầng còn lại: agent CLI cần cờ
`--trust` (tắt hẳn cơ chế hỏi xác nhận từng lệnh của chính nó) mới chạy
headless không tương tác được. Người dùng đã xác nhận rõ ràng chấp nhận
việc pipeline tự động gọi with --trust cho mục đích DUY NHẤT sinh ảnh (xem
phiên làm việc) -- KHÔNG dùng module này cho việc gì khác ngoài
generate_image() ở đây. CWD cố định tại CURSOR_WORKDIR (trong repo, đã
.gitignore) để --trust chỉ áp dụng cho đúng 1 thư mục cô lập, không phải
thư mục dự án gốc.

Cursor lưu ảnh vào cache RIÊNG của nó (~/.cursor/projects/<hash cwd>/assets/),
KHÔNG lưu thẳng vào output_path mình chỉ định -- bắt agent tự in đường dẫn
đã lưu theo format cố định (SAVED_TO:, cùng quy ước đã dùng cho
agy_image_client.py) rồi tự copy sang cache_path của asset_generation.py."""
import re
import subprocess
from pathlib import Path

AGENT_BIN = Path.home() / ".local" / "bin" / "agent"
CURSOR_WORKDIR = Path(__file__).parent / "chunks_cache" / "cursor_image_workdir"
CURSOR_IMAGE_TIMEOUT_S = 180

_QUOTA_KEYWORDS = (
    "rate limit", "quota", "insufficient credits", "upgrade your plan",
    "usage limit", "billing", "not available on your plan",
)

_PATH_RE = re.compile(r"SAVED_TO:\s*(\S+\.(?:png|jpg|jpeg))", re.IGNORECASE)


class CursorImageError(RuntimeError):
    pass


class CursorQuotaExceededError(CursorImageError):
    """Raise riêng để caller (asset_generation.py) bật circuit breaker và
    chuyển sang tầng fallback tiếp theo (Codex)."""
    pass


def generate_image(prompt_text: str, output_path: Path, timeout_s: float = CURSOR_IMAGE_TIMEOUT_S) -> Path:
    if not AGENT_BIN.exists():
        raise CursorImageError(f"Chưa cài Cursor Agent CLI tại {AGENT_BIN} (curl https://cursor.com/install -fsSL | bash).")

    CURSOR_WORKDIR.mkdir(parents=True, exist_ok=True)
    prompt = (
        f"Generate an image: {prompt_text}. "
        "After saving it, print the EXACT absolute file path it was saved to, "
        "on its own line, starting with 'SAVED_TO:'."
    )
    try:
        result = subprocess.run(
            [str(AGENT_BIN), "-p", prompt, "--output-format", "text", "--trust"],
            capture_output=True, text=True, timeout=timeout_s, cwd=str(CURSOR_WORKDIR),
        )
    except subprocess.TimeoutExpired:
        raise CursorImageError(f"Cursor Agent timeout sau {timeout_s}s.")

    combined = result.stdout + result.stderr
    lowered = combined.lower()
    if any(kw in lowered for kw in _QUOTA_KEYWORDS):
        raise CursorQuotaExceededError(f"Cursor Agent hết quota/không có quyền sinh ảnh: {combined[-500:]}")
    if result.returncode != 0:
        raise CursorImageError(f"Cursor Agent lỗi (exit {result.returncode}): {combined[-1000:]}")

    match = _PATH_RE.search(result.stdout)
    if not match:
        raise CursorImageError(f"Cursor Agent không báo đường dẫn ảnh đã lưu (SAVED_TO:): {result.stdout[-800:]}")
    generated_path = Path(match.group(1))
    if not generated_path.exists():
        raise CursorImageError(f"Cursor Agent báo lưu tại {generated_path} nhưng file không tồn tại.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(generated_path.read_bytes())
    return output_path
