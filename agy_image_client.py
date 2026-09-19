"""
Client sinh ảnh qua agy (Antigravity CLI) -- tool `generate_image` built-in
(khác hẳn agy dùng cho content_seo.py/content_review.py/creative_director.py,
vốn chỉ dùng agy cho TEXT). Đây là TẦNG 2 trong chuỗi fallback 3 tầng:
Codex (hết token) -> agy (hết quota) -> ComfyUI (local, không quota) -- xem
asset_generation.py.

LƯU Ý: lúc viết file này, quota sinh ảnh của agy đang cạn thật (test trực
tiếp ra lỗi "429 Resource Exhausted", reset sau ~160 giờ) -- không test
được đường thành công thực tế. Thiết kế AN TOÀN theo hướng "thất bại thì
rơi xuống ComfyUI" (raise AgyImageError nếu không tìm thấy đường dẫn ảnh
trong output, không đoán mò/giả định) -- worst case là luôn rơi xuống tầng
3, không tệ hơn so với chỉ dùng ComfyUI từ đầu.

QUAN TRỌNG: dùng ĐÚNG đường dẫn tuyệt đối ~/.local/bin/agy -- PATH có 1
binary "agy" KHÁC (launcher IDE Antigravity tại ~/.antigravity/antigravity/bin/agy,
version hoàn toàn khác, KHÔNG PHẢI CLI agent), gây nhầm lẫn nếu gọi tên
"agy" trần không kèm đường dẫn đầy đủ."""
import re
import subprocess
from pathlib import Path

from external_bin import AGY_BIN  # noqa: F401 -- gom về 1 nguồn duy nhất (xem docstring ở đó)
AGY_IMAGE_TIMEOUT_S = 120

_QUOTA_KEYWORDS = (
    "429", "resource exhausted", "hạn ngạch", "quota", "rate limit", "vượt quá",
)

_PATH_RE = re.compile(r"SAVED_TO:\s*(\S+\.(?:png|jpg|jpeg))", re.IGNORECASE)


class AgyImageError(RuntimeError):
    pass


class AgyQuotaExceededError(AgyImageError):
    """Raise riêng để caller (asset_generation.py) bật circuit breaker và
    chuyển sang tầng fallback tiếp theo (ComfyUI)."""
    pass


def generate_image(prompt_text: str, output_path: Path, timeout_s: float = AGY_IMAGE_TIMEOUT_S) -> Path:
    if not AGY_BIN.exists():
        raise AgyImageError(f"Chưa cài agy tại {AGY_BIN}.")

    prompt = (
        f"Dùng tool sinh ảnh (generate_image) để tạo 1 ảnh: {prompt_text}. "
        "Sau khi sinh xong, in ra CHÍNH XÁC đường dẫn file ảnh đã lưu trên máy, "
        "bắt đầu bằng 'SAVED_TO:' (dòng riêng)."
    )
    try:
        result = subprocess.run([str(AGY_BIN), "-p", prompt], capture_output=True, text=True, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        raise AgyImageError(f"agy timeout sau {timeout_s}s.")

    combined = (result.stdout + result.stderr)
    lowered = combined.lower()
    if any(kw in lowered for kw in _QUOTA_KEYWORDS):
        raise AgyQuotaExceededError(f"agy hết quota sinh ảnh: {combined[-500:]}")
    if result.returncode != 0:
        raise AgyImageError(f"agy lỗi (exit {result.returncode}): {combined[-1000:]}")

    match = _PATH_RE.search(result.stdout)
    if not match:
        raise AgyImageError(f"agy không báo đường dẫn ảnh đã lưu (SAVED_TO:): {result.stdout[-500:]}")
    generated_path = Path(match.group(1))
    if not generated_path.exists():
        raise AgyImageError(f"agy báo lưu tại {generated_path} nhưng file không tồn tại.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(generated_path.read_bytes())
    return output_path
