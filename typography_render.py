"""
Bridge gọi Remotion (project Node/React riêng, `remotion_typography/`,
gitignored -- giống pattern video_tool_clone/comfyui_local) để render 1
clip typography (quote card có animation thật: spring physics, không phải
override-tag ASS thủ công) cho 1 beat.

4 style khớp đúng logic chọn trong creative_director.py::pick_typography_style():
  POP_IN       -- câu ngắn <=8 từ
  RISE_UP      -- câu 9-15 từ
  FLIP_3D      -- câu trùng Core Insight (tối đa 1 lần/tập)
  WORD_CASCADE -- câu >15 từ

Yêu cầu: `npm install` đã chạy trong remotion_typography/ (làm 1 lần khi
setup, không tự động ở đây). Nếu Remotion lỗi/chưa cài, raise
TypographyRenderError -- caller (audio_tool_render.py) tự fallback về
render nền màu phẳng cũ (không bao giờ để 1 beat trắng).
"""
import json
import subprocess
from pathlib import Path

from external_bin import NPX_BIN, node_subprocess_env

REMOTION_ROOT = Path(__file__).parent / "remotion_typography"
DYNAMIC_ASSETS_DIR = REMOTION_ROOT / "public" / "dynamic"
STYLE_TO_COMPOSITION = {
    "pop_in": "PopIn",
    "rise_up": "RiseUp",
    "flip_3d": "Flip3D",
    "word_cascade": "WordCascade",
}
RENDER_TIMEOUT_S = 120


def _stage_dynamic_asset(src_path: str) -> str:
    """Copy/symlink 1 file NGOÀI remotion_typography/public/ vào
    public/dynamic/, trả về đường dẫn TƯƠNG ĐỐI để component dùng qua
    staticFile(). Cần thiết vì đã test thật: Img src=<absolute path> bị
    Remotion hiểu nhầm thành route trên local dev server (404), còn
    src="file://..." bị Chrome headless chặn hẳn ("Not allowed to load
    local resource") -- staticFile()+public/ là cách duy nhất chính thống
    hoạt động cho asset sinh động (ảnh AI khác nhau mỗi beat/tập, không
    biết trước lúc build như font)."""
    import shutil
    src = Path(src_path).resolve()
    DYNAMIC_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    dest = DYNAMIC_ASSETS_DIR / f"{src.stem}_{abs(hash(str(src))) % 10**8}{src.suffix}"
    # COPY, không symlink -- đã test thật: Remotion's local dev server trả
    # 404 cho file symlink trỏ ra ngoài public/ (chặn theo kiểu static-file-
    # server thông thường, không phục vụ ra ngoài webroot dù đích hợp lệ).
    if not dest.exists():
        shutil.copy2(src, dest)
    return f"dynamic/{dest.name}"


class TypographyRenderError(RuntimeError):
    pass


def is_available() -> bool:
    return (REMOTION_ROOT / "node_modules").exists()


def render_typography_clip(
    text: str,
    style: str,
    duration_s: float,
    output_path: Path,
    font_family: str = "Be Vietnam Pro",
    accent_color: str = "#E6B45A",
    bg_color: str = "#241A10",
    font_size_px: int = 72,
) -> Path:
    if not is_available():
        raise TypographyRenderError(
            f"Chưa setup Remotion tại {REMOTION_ROOT} (cd remotion_typography && npm install)."
        )
    composition = STYLE_TO_COMPOSITION.get(style)
    if composition is None:
        raise TypographyRenderError(f"Style không hợp lệ: {style} (phải là 1 trong {list(STYLE_TO_COMPOSITION)}).")

    props = {
        "text": text, "fontFamily": font_family, "accentColor": accent_color,
        "bgColor": bg_color, "durationInSeconds": max(duration_s, 0.5), "fontSizePx": font_size_px,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    args = [
        NPX_BIN, "remotion", "render", composition, str(output_path.resolve()),
        "--props", json.dumps(props, ensure_ascii=False),
    ]
    try:
        result = subprocess.run(args, cwd=REMOTION_ROOT, capture_output=True, text=True, timeout=RENDER_TIMEOUT_S,
                                 env=node_subprocess_env())
    except subprocess.TimeoutExpired:
        raise TypographyRenderError(f"Remotion render timeout sau {RENDER_TIMEOUT_S}s cho: {text[:50]}...")

    if result.returncode != 0:
        raise TypographyRenderError(f"Remotion render lỗi (exit {result.returncode}): {result.stderr[-1000:] or result.stdout[-1000:]}")
    if not output_path.exists():
        raise TypographyRenderError(f"Remotion báo thành công nhưng không thấy file: {output_path}")
    return output_path


def render_annotated_diagram_clip(
    background_image_path: str,
    annotations: list[dict],
    duration_s: float,
    output_path: Path,
    font_family: str = "Be Vietnam Pro",
    accent_color: str = "#E6B45A",
    bg_color: str = "#241A10",
    font_size_px: int = 40,
) -> Path:
    """Beat DIAGRAM (xem creative_director.py) -- ảnh nền sinh AI riêng cho
    TỪNG tập + mũi tên/nhãn chỉ hướng đè lên, KHÁC hẳn symbol_library tĩnh
    dùng chung (Bát Quái/Ngũ Hành, không cần Remotion, chỉ Ken Burns đơn
    giản). `annotations`: [{"label": str, "angleDeg": float, "color": str|None}, ...]
    -- 0=Bắc(trên), xuôi kim đồng hồ, cùng quy ước la bàn với sơ đồ bát quái
    (generate_symbol_assets.py::generate_bat_quai())."""
    if not is_available():
        raise TypographyRenderError(
            f"Chưa setup Remotion tại {REMOTION_ROOT} (cd remotion_typography && npm install)."
        )
    if not annotations:
        raise TypographyRenderError("annotations rỗng -- AnnotatedDiagram cần ít nhất 1 điểm chú thích.")

    props = {
        "backgroundImagePath": _stage_dynamic_asset(background_image_path),
        "annotations": annotations,
        "fontFamily": font_family, "accentColor": accent_color, "bgColor": bg_color,
        "durationInSeconds": max(duration_s, 0.5), "fontSizePx": font_size_px,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    args = [
        NPX_BIN, "remotion", "render", "AnnotatedDiagram", str(output_path.resolve()),
        "--props", json.dumps(props, ensure_ascii=False),
    ]
    try:
        result = subprocess.run(args, cwd=REMOTION_ROOT, capture_output=True, text=True, timeout=RENDER_TIMEOUT_S,
                                 env=node_subprocess_env())
    except subprocess.TimeoutExpired:
        raise TypographyRenderError(f"Remotion render timeout sau {RENDER_TIMEOUT_S}s cho diagram: {background_image_path}")

    if result.returncode != 0:
        raise TypographyRenderError(f"Remotion render lỗi (exit {result.returncode}): {result.stderr[-1000:] or result.stdout[-1000:]}")
    if not output_path.exists():
        raise TypographyRenderError(f"Remotion báo thành công nhưng không thấy file: {output_path}")
    return output_path
