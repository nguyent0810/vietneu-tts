"""Cầu nối giữa pipeline TTS của repo này và HyperFrames (HTML -> MP4).

VÌ SAO có file này: hình cho Short lâu nay lấy từ B-roll/ảnh sinh tự động,
là chỗ tốn thời gian nhất và cũng là chỗ rủi ro nhất với kênh Hình Sự (phải
có cả bộ `broll_query_sanitizer` trong domain_creative_profiles.json chỉ để
chặn ảnh bạo lực lọt vào). HyperFrames render thẳng 1 file HTML thành MP4
bằng headless Chrome + ffmpeg: không gọi API ảnh, không tải stock footage,
không có gì để kiểm duyệt ngoài chính HTML ta viết -- và vì timing lấy
TRỰC TIẾP từ manifest TTS (`.json` cạnh file `.wav`) nên phụ đề khớp chính
xác tuyệt đối, không cần ASR đoán lại.

Vị trí trong hạ tầng cũ: đây là lựa chọn THỨ HAI song song với
`video_tool_bridge.py` (shot_list + Ken Burns + B-roll). Cùng một đầu vào
(`wav` + `segments-json`), cùng một đầu ra (1 file mp4 9:16 có sẵn audio),
nên `short_batch_runner.py` có thể gọi cái nào tuỳ nội dung: dùng
HyperFrames cho dạng "giải thích điều luật/cảnh báo/kể chuyện" (chữ là
chính), giữ video_tool cho dạng cần cảnh thật.

HyperFrames CLI cần Node >= 22 trong khi repo này chưa pin Node nào (launchd
đang chạy Node 20 của nvm cho các tool khác) -- vì vậy gọi qua nvm trong 1
shell con, KHÔNG đổi Node mặc định của máy.

Usage (CLI, test tay):
    python3 hyperframes_bridge.py \
        --script  scratch/s1.txt  --wav scratch/s1.wav \
        --series law --kicker "HIỂU ĐÚNG LUẬT" --badge "ĐIỀU 22 · BLHS 2015" \
        --output output/cl_staging/s1_hf.mp4

Biến môi trường khi render:
    HYPERFRAMES_BROWSER_PATH  Chromium hệ thống (máy Linux như Oracle; Mac để trống).
    HF_RENDER_TIMEOUT_X       Hệ số hạn chờ render theo thời lượng (mặc định 6, khớp tốc độ Mac).
                              Hạn = max(timeout, thời lượng × hệ số + 600 giây). Máy chậm như
                              Oracle (~9 lần thời lượng) cần 20; giá trị sai hoặc <= 0 thì giữ 6.
"""
import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image

def _find_repo_root(start: Path) -> Path:
    p = start.resolve()
    for parent in [p] + list(p.parents):
        if (parent / ".git").is_dir():
            return parent
    return start


PROJECT_ROOT = Path(__file__).parent
REPO_ROOT = _find_repo_root(PROJECT_ROOT)
HF_PROJECT = PROJECT_ROOT / "hyperframes_short"
HF_ASSETS = HF_PROJECT / "assets"
NODE_MAJOR = "22"
DEFAULT_TIMEOUT_S = 900
RENDER_TIMEOUT_X_DEFAULT = 6.0


def render_timeout(duration: float, timeout: int = DEFAULT_TIMEOUT_S) -> int:
    """Hạn chờ một lần render: lớn theo độ dài, hệ số chỉnh được qua HF_RENDER_TIMEOUT_X."""
    raw = os.environ.get("HF_RENDER_TIMEOUT_X", "")
    try:
        factor = float(raw) if raw else RENDER_TIMEOUT_X_DEFAULT
    except ValueError:
        factor = RENDER_TIMEOUT_X_DEFAULT
    if not factor > 0:
        factor = RENDER_TIMEOUT_X_DEFAULT
    return max(timeout, int(duration * factor) + 600)

# Mỗi series 1 bảng màu + nhãn mặc định. Giữ ở đây (không nhét vào
# domain_creative_profiles.json) vì đây là thuộc tính TRÌNH BÀY của template
# HyperFrames, không phải ràng buộc nội dung/an toàn của domain.
# series -> khoá domain trong domain_creative_profiles.json. Dùng nhầm bộ
# sanitizer là hỏng đúng thứ nó sinh ra để chặn: bộ của CL đổi từ bạo lực
# sang từ pháp lý, bộ của BUD đổi từ Thiên Chúa giáo sang Phật giáo.
SERIES_DOMAIN = {"law": "CL", "scam": "CL", "case": "CL", "tale": "CL", "bud": "BUD", "fs": "FS"}

# Cách media xuất hiện. Tất cả đều dựa trên mask (biến CSS) -- KHÔNG dùng
# `filter` hay `scale` làm reveal: `filter` đang chở house grade, `scale`
# đang chở Ken Burns.
REVEALS = ("ink", "wipe", "iris", "rise")

# `ink` là vệt mực THẤM VÀO GIẤY. Đặt lên style nền tối thì mask để lại một
# mảng sáng lem nhem trên nền đen -- đọc ra là lỗi render, không phải thư pháp.
# Chỉ style có nền giấy mới dùng được.
# oilpaint TỪNG nằm trong danh sách này -- sai: nền nó là sơn dầu nâu đen
# (#3d2c1e -> #120c08), không phải giấy. Chỉ inkwash mới thật sự có nền giấy.
PAPER_STYLES = ("inkwash", "inkwash_wide", "inkwash_long", "studio_long")

# "House grade": MỘT bảng màu áp cho MỌI media của kênh. Khi một bài có 4-5
# ảnh lấy từ 4-5 nhiếp ảnh gia khác nhau, thứ quyết định đẹp hay không không
# phải hiệu ứng trên từng tấm, mà là việc tất cả cùng một tông. Không có nó
# thì thêm ảnh = thêm nhiễu.
# Tham số dò bằng `hyperframes media-treatment --analyze` rồi nướng thẳng vào
# thẻ, để mỗi lần render không phải gọi thêm một bước CLI nào.
HOUSE_GRADE = {
    "BUD": "saturate(0.84) contrast(1.05) sepia(0.14) brightness(1.03)",
    "CL":  "saturate(0.92) contrast(1.08) brightness(0.97)",
    # Phong thuỷ: tranh mực Á Đông nhấn vàng ấm (image_style_anchor của FS).
    "FS":  "saturate(0.9) contrast(1.06) sepia(0.1) brightness(1.02)",
}

# Treatment CẤM trên media của kênh Phật giáo. Biến một pho tượng thành chấm
# in, nhiễu băng từ hay khối pixel đọc ra là cợt nhả, dù ý định không phải
# vậy -- cùng tinh thần với bộ sanitizer của CL: chặn bằng luật, không dựa
# vào việc người viết nhớ.
FORBIDDEN_TREATMENT = {
    "BUD": ("glitch", "pixelate", "halftone", "dither", "chromableed", "tapedamage",
            "crtcurvature", "scanlines", "invert", "hue-rotate"),
    "CL": (),
    "FS": ("glitch", "pixelate", "tapedamage", "crtcurvature", "scanlines", "invert", "hue-rotate"),
}

# Dòng nội dung trong một series -- quyết định chữ trên cùng khung hình, như
# law/scam/case/tale bên kênh Hình Sự. Kênh Phật giáo từng in cố định "SUY
# NGẪM" cho mọi bài, dù bài giải nghĩa sám hối và bài về điện thoại là hai
# loại khác hẳn nhau.
SERIES_LANES = {
    "bud": {
        "niem":    "CHÁNH NIỆM",             # cảm xúc, thói quen hằng ngày
        "phap":    "HIỂU ĐÚNG PHẬT PHÁP",     # giải một khái niệm / một hiểu lầm
        "doi":     "TU GIỮA ĐỜI THƯỜNG",      # gia đình, quan hệ, công việc
        "tuong":   "BIỂU TƯỢNG PHẬT GIÁO",    # tượng, thủ ấn, Bồ Tát
        "diatang": "KINH ĐỊA TẠNG",
        "long":    "LỜI PHẬT DẠY",            # video dài, series chữa lành
    },
    "fs": {
        "lich":     "LỊCH HOÀNG ĐẠO",        # số liệu tính bằng vnlunar, không viết tay
        "tuoi":     "TUỔI & CON GIÁP",        # tam hợp, lục hợp, xung
        "nguhanh":  "NGŨ HÀNH · CAN CHI",
        "kinhdich": "KINH DỊCH",
        "nhao":     "PHONG THỦY NHÀ Ở",
        "long":     "12 CON GIÁP · 2027",     # video dài
    },
}


SERIES_PRESETS = {
    "law":  {"accent": "#e5484d", "kicker": "HIỂU ĐÚNG LUẬT",
             "footer": "Phổ biến kiến thức pháp luật — không phải tư vấn cho vụ việc cụ thể"},
    "scam": {"accent": "#f5a524", "kicker": "CẢNH BÁO LỪA ĐẢO",
             "footer": "Nhận ra kịch bản — đừng chuyển tiền khi đang hoảng"},
    "case": {"accent": "#3b82f6", "kicker": "HỒ SƠ VỤ ÁN",
             "footer": "Dẫn theo hồ sơ công khai của cơ quan điều tra"},
    "tale": {"accent": "#8b5cf6", "kicker": "CHUYỆN ĐÊM KHUYA",
             "footer": "Truyện hư cấu — mọi nhân vật và tình tiết đều do tưởng tượng"},
    # Kênh Phật giáo: nhịp 18-28 giây/beat, "giữ khung hình đủ lâu để cảm xúc
    # lắng đọng" (pacing_guidance của BUD) -- ngược hẳn nhịp nhanh của CL.
    # Kênh Phong Thuỷ: kiến thức truyền thống, nhịp vừa (16-22 giây/beat).
    "fs":   {"accent": "#d4a93a", "kicker": "PHONG THỦY",
             "footer": "Kiến thức truyền thống — để tham khảo"},
    "bud":  {"accent": "#c9a227", "kicker": "SUY NGẪM",
             "footer": "Nội dung suy ngẫm — không thay cho việc học Phật pháp trực tiếp"},
}

_MARKER_RE = re.compile(r"\*\*(.+?)\*\*")

# "Style" = CÁI NHÌN của ngày hôm đó (mỗi ngày 1 dạng), tách hẳn khỏi
# "series" = LÀN NỘI DUNG (điều luật/lừa đảo/vụ án/truyện). Cùng 1 kịch bản
# đổi style là ra một video khác hẳn, không phải đổi nội dung.
# accent thuộc về STYLE (cái nhìn của ngày), không thuộc series: 5 short
# cùng ngày phải trông như cùng một tập phim, phân biệt nhau bằng nhãn
# kicker chứ không phải bằng màu.
# Loại sơ đồ longform.js dựng được, và bố cục ảnh ngoài ô mặc định của style.
VISUAL_TYPES = ("wheel", "elements", "years", "list", "timeline", "compare", "stat", "quote", "map",
                "word", "illus", "endcard", "doc", "photo", "clock", "ask", "shadow", "hexagram", "luoshu", "ledger", "breath", "museum", "napam", "cuudieu", "eclipse",
                "lookup", "annot", "relic", "chiwheel", "pie", "compass", "teaser",
                "clues", "stamp", "scroll", "dialog", "wind", "bagua", "studio", "region", "profile",
                "woodcut", "papercut", "oneline", "film16", "blueprint", "pencil")
# Bộ style bổ sung (issue #258, longform_styles.js): điểm nhấn dùng tiết chế, CHỈ khi plan gọi tên.
# Không bộ chọn nào tự chèn; bridge chặn quá 3 cảnh style một lần render và hai cảnh style liền nhau.
STYLE_VISUAL_TYPES = ("woodcut", "papercut", "oneline", "film16", "blueprint", "pencil")
STYLE_MAX_PER_RENDER = 3
MEDIA_LAYOUTS =("full", "card3d", "split", "split_r", "polaroid", "pinned", "depth")
MOTION_PRESETS = ("slow_zoom", "pan_focus", "push_detail", "parallax", "highlight", "reveal")
_MOTION_NUM = ("scale_from", "scale_to", "pan", "min_s", "max_s")
CINE_CAMS = ("push_in", "pull_out", "pan_left", "pan_right", "tilt_up", "rack_focus", "dolly_parallax")
CINE_FX = ("rain", "fog", "dust", "embers", "candle_flicker", "god_rays", "lightning", "mist_drift", "petals", "snow_ash")
CINE_GRADES = ("warm", "cold", "night", "dawn")
CINE_TRANSITIONS = ("cut", "flash_white", "dip_black", "whip", "match_dissolve")
CINE_KEYS = {"cam", "depth", "fx", "grade", "intensity", "transition_in"}


def parse_cine(raw: object, where: str = "media") -> dict | None:
    """Kiểm và chuẩn hoá khoá `cine` của media ảnh Long (024). Không có -> None."""
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise HyperFramesError(f"{where}: cine phải là object")
    extra = sorted(set(raw) - CINE_KEYS)
    if extra:
        raise HyperFramesError(f"{where}: cine có khoá lạ {extra!r}")
    cam = raw.get("cam", "push_in")
    if not isinstance(cam, str) or cam not in CINE_CAMS:
        raise HyperFramesError(f"{where}: cine.cam lạ {cam!r} (có: {', '.join(CINE_CAMS)})")
    depth = raw.get("depth", False)
    if not isinstance(depth, bool):
        raise HyperFramesError(f"{where}: cine.depth phải là bool")
    fx_raw = raw.get("fx")
    if fx_raw is None:
        fx_list: list[str] = []
    elif isinstance(fx_raw, list):
        fx_list = []
        for item in fx_raw:
            if not isinstance(item, str) or item not in CINE_FX:
                raise HyperFramesError(f"{where}: cine.fx lạ {item!r} (có: {', '.join(CINE_FX)})")
            if item not in fx_list:
                fx_list.append(item)
        if len(fx_list) > 3:
            raise HyperFramesError(f"{where}: cine.fx tối đa 3 lớp (nhận {len(fx_list)})")
    else:
        raise HyperFramesError(f"{where}: cine.fx phải là danh sách")
    grade = raw.get("grade")
    if grade is not None and (not isinstance(grade, str) or grade not in CINE_GRADES):
        raise HyperFramesError(f"{where}: cine.grade lạ {grade!r} (có: {', '.join(CINE_GRADES)})")
    intensity = raw.get("intensity", 0.75)
    if isinstance(intensity, bool) or not isinstance(intensity, (int, float)):
        raise HyperFramesError(f"{where}: cine.intensity phải là số 0.0..1.0")
    intensity_f = float(intensity)
    if not (0.0 <= intensity_f <= 1.0):
        raise HyperFramesError(f"{where}: cine.intensity ngoài khoảng 0.0..1.0 ({intensity_f})")
    transition_in = raw.get("transition_in", "cut")
    if not isinstance(transition_in, str) or transition_in not in CINE_TRANSITIONS:
        raise HyperFramesError(
            f"{where}: cine.transition_in lạ {transition_in!r} (có: {', '.join(CINE_TRANSITIONS)})")
    out: dict = {
        "cam": cam,
        "depth": depth,
        "fx": fx_list,
        "intensity": round(intensity_f, 3),
        "transition_in": transition_in,
    }
    if grade is not None:
        out["grade"] = grade
    return out


validate_cine = parse_cine


def copy_cine(media_out: dict, spec: dict, where: str = "media") -> dict | None:
    """Chép `cine` đã kiểm vào `media_out` khi plan khai báo. Plan cũ không đổi."""
    cine = parse_cine(spec.get("cine"), where=where)
    if cine is not None:
        media_out["cine"] = cine
    return cine


# ===== 028: Toàn cảnh quét ngang (panorama pan) =====
PAN_KEYS = {
    "dir", "stops", "ease", "depth", "fx", "grade", "intensity",
    "transition_in", "transition_out", "end_x", "end_y", "end_zoom",
    "axis", "focus_pull", "zoom", "layers"
}
PAN_AXES = ("h", "v")
PAN_DIRS = ("ltr", "rtl", "ttb", "btt")
PAN_TRANSITIONS_OUT = ("cut", "fade", "whip", "flash_white", "dip_black")
PAN_EASES = ("inOut", "linear", "in", "out", "sine.inOut", "power1.inOut", "power2.inOut")
PAN_SPEED_MAX = 180.0
PAN_HOLD_MAX_S = 20.0
PAN_VIDEO_PCT_WARN = 0.25
CAMERA_KEYS = {
    "canvas", "stops", "axis", "ease", "transition_in", "transition_out",
    "orbit", "focus_pull", "end_x", "end_y", "end_zoom"
}
LAYER_KEYS = {
    "path", "path_frames", "fps", "track", "bob", "sway", "shadow",
    "water", "match_color", "follow", "light", "opacity", "z_index", "anchor"
}
LAYER_LIGHT_DIRS = ("left", "right", "top")


def _parse_focus_pull(raw: object, where: str = "media") -> list[dict]:
    """Kiểm tra và chuẩn hoá cấu hình focus_pull."""
    if raw is None:
        return []
    items = raw if isinstance(raw, list) else [raw]
    out: list[dict] = []
    for j, it in enumerate(items):
        if not isinstance(it, dict):
            raise HyperFramesError(f"{where}: focus_pull {j} phải là object")
        extra = sorted(set(it) - {"line", "to", "dur"})
        if extra:
            raise HyperFramesError(f"{where}: focus_pull {j} có khoá lạ {extra!r}")
        line_val = it.get("line")
        try:
            line_int = int(line_val)
        except (TypeError, ValueError) as exc:
            raise HyperFramesError(f"{where}: focus_pull {j} thiếu hoặc sai line") from exc
        if line_int < 1:
            raise HyperFramesError(f"{where}: focus_pull {j} line phải >= 1 ({line_int})")
        to_val = it.get("to")
        if to_val not in ("fg", "bg"):
            raise HyperFramesError(f"{where}: focus_pull {j} 'to' phải là 'fg' hoặc 'bg' (nhận {to_val!r})")
        dur_val = it.get("dur", 1.0)
        if isinstance(dur_val, bool) or not isinstance(dur_val, (int, float)) or float(dur_val) <= 0:
            raise HyperFramesError(f"{where}: focus_pull {j} dur phải là số > 0")
        out.append({"line": line_int, "to": to_val, "dur": round(float(dur_val), 3)})
    return out


def parse_layers(raw: object, where: str = "media") -> list[dict]:
    """Kiểm tra và chuẩn hoá cấu hình `layers` cho máy bám nhân vật (028c)."""
    if raw is None:
        return []
    items = [raw] if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        raise HyperFramesError(f"{where}: layers phải là danh sách hoặc object")

    out: list[dict] = []
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            raise HyperFramesError(f"{where}: layer {i} phải là object")
        extra = sorted(set(it) - LAYER_KEYS)
        if extra:
            raise HyperFramesError(f"{where}: layer {i} có khoá lạ {extra!r}")

        path_val = it.get("path")
        frames_val = it.get("path_frames")
        if not path_val and not frames_val:
            raise HyperFramesError(f"{where}: layer {i} cần có path hoặc path_frames")
        if path_val is not None and not isinstance(path_val, str):
            raise HyperFramesError(f"{where}: layer {i} path phải là str")

        parsed_frames = []
        if frames_val is not None:
            if not isinstance(frames_val, list) or not frames_val:
                raise HyperFramesError(f"{where}: layer {i} path_frames phải là danh sách không rỗng")
            for f_idx, f_item in enumerate(frames_val):
                if not isinstance(f_item, str):
                    raise HyperFramesError(f"{where}: layer {i} path_frames[{f_idx}] phải là str")
                parsed_frames.append(f_item)

        fps_val = it.get("fps", 4.0 if parsed_frames else None)
        if fps_val is not None:
            if isinstance(fps_val, bool) or not isinstance(fps_val, (int, float)) or float(fps_val) <= 0:
                raise HyperFramesError(f"{where}: layer {i} fps phải là số > 0")
            fps_val = round(float(fps_val), 2)

        track_raw = it.get("track")
        if not isinstance(track_raw, list) or not track_raw:
            raise HyperFramesError(f"{where}: layer {i} track phải là danh sách ít nhất 1 điểm dừng")

        parsed_track: list[dict] = []
        prev_line = -1
        for t_idx, s in enumerate(track_raw):
            if not isinstance(s, dict):
                raise HyperFramesError(f"{where}: layer {i} track[{t_idx}] phải là object")
            extra_t = sorted(set(s) - {"line", "x", "y", "scale", "at"})
            if extra_t:
                raise HyperFramesError(f"{where}: layer {i} track[{t_idx}] có khoá lạ {extra_t!r}")
            line_val = s.get("line")
            try:
                line_int = int(line_val)
            except (TypeError, ValueError) as exc:
                raise HyperFramesError(f"{where}: layer {i} track[{t_idx}] thiếu hoặc sai line") from exc
            if line_int < 1:
                raise HyperFramesError(f"{where}: layer {i} track[{t_idx}] line phải >= 1 ({line_int})")
            if line_int <= prev_line:
                raise HyperFramesError(f"{where}: layer {i} track[{t_idx}] line ({line_int}) phải tăng dần sau câu {prev_line}")
            prev_line = line_int

            x_val = s.get("x", 0.5)
            y_val = s.get("y", 0.5)
            if isinstance(x_val, bool) or not isinstance(x_val, (int, float)):
                raise HyperFramesError(f"{where}: layer {i} track[{t_idx}] x phải là số")
            if isinstance(y_val, bool) or not isinstance(y_val, (int, float)):
                raise HyperFramesError(f"{where}: layer {i} track[{t_idx}] y phải là số")
            xf, yf = float(x_val), float(y_val)
            if not (0.0 <= xf <= 1.0):
                raise HyperFramesError(f"{where}: layer {i} track[{t_idx}] x ngoài khoảng 0.0..1.0 ({xf})")
            if not (0.0 <= yf <= 1.0):
                raise HyperFramesError(f"{where}: layer {i} track[{t_idx}] y ngoài khoảng 0.0..1.0 ({yf})")

            scale_val = s.get("scale", 1.0)
            if isinstance(scale_val, bool) or not isinstance(scale_val, (int, float)):
                raise HyperFramesError(f"{where}: layer {i} track[{t_idx}] scale phải là số")
            sc_f = float(scale_val)
            if not (0.2 <= sc_f <= 1.5):
                raise HyperFramesError(f"{where}: layer {i} track[{t_idx}] scale ngoài khoảng 0.2..1.5 ({sc_f})")

            t_dict = {"line": line_int, "x": round(xf, 4), "y": round(yf, 4), "scale": round(sc_f, 3)}
            if s.get("at") in ("start", "end"):
                t_dict["at"] = s["at"]
            parsed_track.append(t_dict)

        # bob: {px, hz} hoặc số hoặc bool
        bob_val = it.get("bob")
        parsed_bob = None
        if bob_val is not None and bob_val is not False and bob_val != 0:
            if isinstance(bob_val, dict):
                extra_b = sorted(set(bob_val) - {"px", "hz"})
                if extra_b:
                    raise HyperFramesError(f"{where}: layer {i} bob có khoá lạ {extra_b!r}")
                px_val = bob_val.get("px", 3.0)
                hz_val = bob_val.get("hz", 1.6)
                if isinstance(px_val, bool) or not isinstance(px_val, (int, float)) or float(px_val) < 0:
                    raise HyperFramesError(f"{where}: layer {i} bob.px phải là số >= 0")
                if isinstance(hz_val, bool) or not isinstance(hz_val, (int, float)) or float(hz_val) <= 0:
                    raise HyperFramesError(f"{where}: layer {i} bob.hz phải là số > 0")
                parsed_bob = {"px": round(float(px_val), 2), "hz": round(float(hz_val), 2)}
            elif isinstance(bob_val, (int, float)) and not isinstance(bob_val, bool):
                parsed_bob = {"px": round(float(bob_val), 2), "hz": 1.6}
            elif bob_val is True:
                parsed_bob = {"px": 3.0, "hz": 1.6}
            else:
                raise HyperFramesError(f"{where}: layer {i} bob không hợp lệ")

        # sway: {deg, hz} hoặc số hoặc bool
        sway_val = it.get("sway")
        parsed_sway = None
        if sway_val is not None and sway_val is not False and sway_val != 0:
            if isinstance(sway_val, dict):
                extra_sw = sorted(set(sway_val) - {"deg", "hz"})
                if extra_sw:
                    raise HyperFramesError(f"{where}: layer {i} sway có khoá lạ {extra_sw!r}")
                deg_val = sway_val.get("deg", 1.5)
                hz_val = sway_val.get("hz", 0.8)
                if isinstance(deg_val, bool) or not isinstance(deg_val, (int, float)) or float(deg_val) < 0:
                    raise HyperFramesError(f"{where}: layer {i} sway.deg phải là số >= 0")
                if isinstance(hz_val, bool) or not isinstance(hz_val, (int, float)) or float(hz_val) <= 0:
                    raise HyperFramesError(f"{where}: layer {i} sway.hz phải là số > 0")
                parsed_sway = {"deg": round(float(deg_val), 2), "hz": round(float(hz_val), 2)}
            elif isinstance(sway_val, (int, float)) and not isinstance(sway_val, bool):
                parsed_sway = {"deg": round(float(sway_val), 2), "hz": 0.8}
            elif sway_val is True:
                parsed_sway = {"deg": 1.5, "hz": 0.8}
            else:
                raise HyperFramesError(f"{where}: layer {i} sway không hợp lệ")

        # shadow: bool hoặc dict {light, opacity}
        shadow_val = it.get("shadow", False)
        parsed_shadow = None
        if shadow_val is True:
            parsed_shadow = {"light": it.get("light", "top"), "opacity": 0.45}
        elif isinstance(shadow_val, dict):
            sh_light = shadow_val.get("light", it.get("light", "top"))
            if sh_light not in LAYER_LIGHT_DIRS:
                raise HyperFramesError(f"{where}: layer {i} shadow.light lạ {sh_light!r} (có: {', '.join(LAYER_LIGHT_DIRS)})")
            sh_op = shadow_val.get("opacity", 0.45)
            if isinstance(sh_op, bool) or not isinstance(sh_op, (int, float)) or not (0.0 <= float(sh_op) <= 1.0):
                raise HyperFramesError(f"{where}: layer {i} shadow.opacity phải là số 0.0..1.0")
            parsed_shadow = {"light": sh_light, "opacity": round(float(sh_op), 3)}
        elif shadow_val is False or shadow_val is None:
            parsed_shadow = False
        else:
            raise HyperFramesError(f"{where}: layer {i} shadow phải là bool hoặc dict")

        water = bool(it.get("water", False))
        match_color_val = bool(it.get("match_color", False))
        follow_val = bool(it.get("follow", False))

        light_val = it.get("light", "top")
        if light_val not in LAYER_LIGHT_DIRS:
            raise HyperFramesError(f"{where}: layer {i} light lạ {light_val!r} (có: {', '.join(LAYER_LIGHT_DIRS)})")

        opacity_val = it.get("opacity", 1.0)
        if isinstance(opacity_val, bool) or not isinstance(opacity_val, (int, float)) or not (0.0 <= float(opacity_val) <= 1.0):
            raise HyperFramesError(f"{where}: layer {i} opacity phải là số 0.0..1.0")

        lyr_dict: dict = {
            "path": path_val,
            "track": parsed_track,
            "bob": parsed_bob,
            "sway": parsed_sway,
            "shadow": parsed_shadow,
            "water": water,
            "match_color": match_color_val,
            "follow": follow_val,
            "light": light_val,
            "opacity": round(float(opacity_val), 3),
        }
        if parsed_frames:
            lyr_dict["path_frames"] = parsed_frames
            lyr_dict["fps"] = fps_val
        if it.get("z_index") is not None:
            lyr_dict["z_index"] = int(it["z_index"])
        if it.get("anchor") is not None:
            lyr_dict["anchor"] = str(it["anchor"])

        out.append(lyr_dict)

    return out


validate_layers = parse_layers


def parse_pan(raw: object, where: str = "media") -> dict | None:
    """Kiểm và chuẩn hoá khoá `pan` của media ảnh rộng Long (028 & 028b). Không có -> None."""
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise HyperFramesError(f"{where}: pan phải là object")
    extra = sorted(set(raw) - PAN_KEYS)
    if extra:
        raise HyperFramesError(f"{where}: pan có khoá lạ {extra!r}")

    axis = raw.get("axis", "h")
    if not isinstance(axis, str) or axis not in PAN_AXES:
        raise HyperFramesError(f"{where}: pan.axis lạ {axis!r} (có: {', '.join(PAN_AXES)})")

    default_dir = "ttb" if axis == "v" else "ltr"
    pan_dir = raw.get("dir", default_dir)
    if not isinstance(pan_dir, str) or pan_dir not in PAN_DIRS:
        raise HyperFramesError(f"{where}: pan.dir lạ {pan_dir!r} (có: {', '.join(PAN_DIRS)})")

    stops_raw = raw.get("stops")
    if not isinstance(stops_raw, list) or not stops_raw:
        raise HyperFramesError(f"{where}: pan.stops phải là danh sách ít nhất 1 điểm dừng")

    stops: list[dict] = []
    prev_line = -1
    for i, s in enumerate(stops_raw):
        if not isinstance(s, dict):
            raise HyperFramesError(f"{where}: pan stop {i} phải là object")
        extra_s = sorted(set(s) - {"line", "x", "y", "zoom", "at", "focus"})
        if extra_s:
            raise HyperFramesError(f"{where}: pan stop {i} có khoá lạ {extra_s!r}")
        line_val = s.get("line")
        try:
            line_int = int(line_val)
        except (TypeError, ValueError) as exc:
            raise HyperFramesError(f"{where}: pan stop {i} thiếu hoặc sai line") from exc
        if line_int < 1:
            raise HyperFramesError(f"{where}: pan stop {i} line phải >= 1 ({line_int})")
        if line_int <= prev_line:
            raise HyperFramesError(f"{where}: pan stop {i} line ({line_int}) phải tăng dần sau câu {prev_line}")
        prev_line = line_int

        stop_dict: dict = {"line": line_int}

        if axis == "v":
            y_val = s.get("y")
            if y_val is None and s.get("x") is not None:
                y_val = s.get("x")
            if y_val is None:
                raise HyperFramesError(f"{where}: pan stop {i} (axis=v) thiếu toạ độ y")
            if isinstance(y_val, bool) or not isinstance(y_val, (int, float)):
                raise HyperFramesError(f"{where}: pan stop {i} y phải là số")
            y_f = float(y_val)
            if not (0.0 <= y_f <= 1.0):
                raise HyperFramesError(f"{where}: pan stop {i} y ngoài khoảng 0.0..1.0 ({y_f})")
            stop_dict["y"] = round(y_f, 4)
            if s.get("x") is not None:
                x_val = s.get("x")
                if isinstance(x_val, bool) or not isinstance(x_val, (int, float)):
                    raise HyperFramesError(f"{where}: pan stop {i} x phải là số")
                x_f = float(x_val)
                if not (0.0 <= x_f <= 1.0):
                    raise HyperFramesError(f"{where}: pan stop {i} x ngoài khoảng 0.0..1.0 ({x_f})")
                stop_dict["x"] = round(x_f, 4)
        else:
            x_val = s.get("x")
            if x_val is None and s.get("y") is not None:
                x_val = s.get("y")
            if x_val is None:
                raise HyperFramesError(f"{where}: pan stop {i} (axis=h) thiếu toạ độ x")
            if isinstance(x_val, bool) or not isinstance(x_val, (int, float)):
                raise HyperFramesError(f"{where}: pan stop {i} x phải là số")
            x_f = float(x_val)
            if not (0.0 <= x_f <= 1.0):
                raise HyperFramesError(f"{where}: pan stop {i} x ngoài khoảng 0.0..1.0 ({x_f})")
            stop_dict["x"] = round(x_f, 4)
            if s.get("y") is not None:
                y_val = s.get("y")
                if isinstance(y_val, bool) or not isinstance(y_val, (int, float)):
                    raise HyperFramesError(f"{where}: pan stop {i} y phải là số")
                y_f = float(y_val)
                if not (0.0 <= y_f <= 1.0):
                    raise HyperFramesError(f"{where}: pan stop {i} y ngoài khoảng 0.0..1.0 ({y_f})")
                stop_dict["y"] = round(y_f, 4)

        if s.get("zoom") is not None:
            z_val = s.get("zoom")
            if isinstance(z_val, bool) or not isinstance(z_val, (int, float)):
                raise HyperFramesError(f"{where}: pan stop {i} zoom phải là số")
            z_f = float(z_val)
            if not (1.0 <= z_f <= 1.6):
                raise HyperFramesError(f"{where}: pan stop {i} zoom ngoài khoảng 1.0..1.6 ({z_f})")
            stop_dict["zoom"] = round(z_f, 3)

        if s.get("focus") is not None:
            stop_dict["focus"] = str(s["focus"])

        if s.get("at") is not None:
            if s.get("at") not in ("start", "end"):
                raise HyperFramesError(f"{where}: pan stop {i} at phải là 'start' hoặc 'end'")
            stop_dict["at"] = s["at"]
        stops.append(stop_dict)

    ease = raw.get("ease", "inOut")
    if not isinstance(ease, str) or ease not in PAN_EASES:
        raise HyperFramesError(f"{where}: pan.ease lạ {ease!r} (có: {', '.join(PAN_EASES)})")

    depth = raw.get("depth", False)
    if not isinstance(depth, bool):
        raise HyperFramesError(f"{where}: pan.depth phải là bool")

    fx_raw = raw.get("fx")
    if fx_raw is None:
        fx_list: list[str] = []
    elif isinstance(fx_raw, list):
        fx_list = []
        for item in fx_raw:
            if not isinstance(item, str) or item not in CINE_FX:
                raise HyperFramesError(f"{where}: pan.fx lạ {item!r} (có: {', '.join(CINE_FX)})")
            if item not in fx_list:
                fx_list.append(item)
        if len(fx_list) > 3:
            raise HyperFramesError(f"{where}: pan.fx tối đa 3 lớp (nhận {len(fx_list)})")
    else:
        raise HyperFramesError(f"{where}: pan.fx phải là danh sách")

    grade = raw.get("grade")
    if grade is not None and (not isinstance(grade, str) or grade not in CINE_GRADES):
        raise HyperFramesError(f"{where}: pan.grade lạ {grade!r} (có: {', '.join(CINE_GRADES)})")

    intensity = raw.get("intensity", 0.75)
    if isinstance(intensity, bool) or not isinstance(intensity, (int, float)):
        raise HyperFramesError(f"{where}: pan.intensity phải là số 0.0..1.0")
    intensity_f = float(intensity)
    if not (0.0 <= intensity_f <= 1.0):
        raise HyperFramesError(f"{where}: pan.intensity ngoài khoảng 0.0..1.0 ({intensity_f})")

    transition_in = raw.get("transition_in", "cut")
    if not isinstance(transition_in, str) or transition_in not in CINE_TRANSITIONS:
        raise HyperFramesError(f"{where}: pan.transition_in lạ {transition_in!r}")

    transition_out = raw.get("transition_out", "fade")
    if not isinstance(transition_out, str) or transition_out not in PAN_TRANSITIONS_OUT:
        raise HyperFramesError(f"{where}: pan.transition_out lạ {transition_out!r} (có: {', '.join(PAN_TRANSITIONS_OUT)})")

    focus_pull = _parse_focus_pull(raw.get("focus_pull"), where=where)

    out: dict = {
        "axis": axis,
        "dir": pan_dir,
        "stops": stops,
        "ease": ease,
        "depth": depth,
        "fx": fx_list,
        "intensity": round(intensity_f, 3),
        "transition_in": transition_in,
        "transition_out": transition_out,
    }
    if focus_pull:
        out["focus_pull"] = focus_pull
    if grade is not None:
        out["grade"] = grade
    if raw.get("end_x") is not None:
        end_x = float(raw["end_x"])
        if not (0.0 <= end_x <= 1.0):
            raise HyperFramesError(f"{where}: pan.end_x ngoài khoảng 0.0..1.0 ({end_x})")
        out["end_x"] = round(end_x, 4)
    if raw.get("end_y") is not None:
        end_y = float(raw["end_y"])
        if not (0.0 <= end_y <= 1.0):
            raise HyperFramesError(f"{where}: pan.end_y ngoài khoảng 0.0..1.0 ({end_y})")
        out["end_y"] = round(end_y, 4)
    if raw.get("end_zoom") is not None:
        end_z = float(raw["end_zoom"])
        if not (1.0 <= end_z <= 1.6):
            raise HyperFramesError(f"{where}: pan.end_zoom ngoài khoảng 1.0..1.6 ({end_z})")
        out["end_zoom"] = round(end_z, 3)
    if raw.get("layers") is not None:
        out["layers"] = parse_layers(raw["layers"], where=f"{where}.layers")
    return out


def parse_camera(raw: object, where: str = "visual") -> dict | None:
    """Kiểm tra và chuẩn hoá đối tượng `camera` dùng chung cho đồ hoạ visuals (028b PO)."""
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise HyperFramesError(f"{where}: camera phải là object")
    extra = sorted(set(raw) - CAMERA_KEYS)
    if extra:
        raise HyperFramesError(f"{where}: camera có khoá lạ {extra!r}")

    axis = raw.get("axis", "h")
    if not isinstance(axis, str) or axis not in PAN_AXES:
        raise HyperFramesError(f"{where}: camera.axis lạ {axis!r} (có: {', '.join(PAN_AXES)})")

    canvas_raw = raw.get("canvas")
    canvas = {"w": 1920, "h": 1080}
    if canvas_raw is not None:
        if not isinstance(canvas_raw, dict):
            raise HyperFramesError(f"{where}: camera.canvas phải là object {{w, h}}")
        w_val = canvas_raw.get("w", 1920)
        h_val = canvas_raw.get("h", 1080)
        try:
            cw, ch = int(w_val), int(h_val)
        except (TypeError, ValueError) as exc:
            raise HyperFramesError(f"{where}: camera.canvas w/h phải là số nguyên") from exc
        if cw < 1920 or ch < 1080:
            raise HyperFramesError(f"{where}: camera.canvas tối thiểu 1920x1080 (nhận {cw}x{ch})")
        canvas = {"w": cw, "h": ch}

    stops_raw = raw.get("stops")
    if stops_raw is None:
        if raw.get("orbit") is not None:
            stops_raw = [{"line": 1, "x": 0.0, "y": 0.0, "zoom": 1.0}]
        else:
            raise HyperFramesError(f"{where}: camera.stops phải là danh sách ít nhất 1 điểm dừng")
    elif not isinstance(stops_raw, list) or not stops_raw:
        raise HyperFramesError(f"{where}: camera.stops phải là danh sách ít nhất 1 điểm dừng")

    stops: list[dict] = []
    prev_line = -1
    for i, s in enumerate(stops_raw):
        if not isinstance(s, dict):
            raise HyperFramesError(f"{where}: camera stop {i} phải là object")
        extra_s = sorted(set(s) - {"line", "x", "y", "zoom", "at", "focus"})
        if extra_s:
            raise HyperFramesError(f"{where}: camera stop {i} có khoá lạ {extra_s!r}")
        line_val = s.get("line")
        try:
            line_int = int(line_val)
        except (TypeError, ValueError) as exc:
            raise HyperFramesError(f"{where}: camera stop {i} thiếu hoặc sai line") from exc
        if line_int < 1:
            raise HyperFramesError(f"{where}: camera stop {i} line phải >= 1 ({line_int})")
        if line_int <= prev_line:
            raise HyperFramesError(f"{where}: camera stop {i} line ({line_int}) phải tăng dần sau câu {prev_line}")
        prev_line = line_int

        stop_dict: dict = {"line": line_int}
        if s.get("x") is not None:
            x_f = float(s["x"])
            if not (0.0 <= x_f <= 1.0):
                raise HyperFramesError(f"{where}: camera stop {i} x ngoài khoảng 0.0..1.0 ({x_f})")
            stop_dict["x"] = round(x_f, 4)
        else:
            stop_dict["x"] = 0.0

        if s.get("y") is not None:
            y_f = float(s["y"])
            if not (0.0 <= y_f <= 1.0):
                raise HyperFramesError(f"{where}: camera stop {i} y ngoài khoảng 0.0..1.0 ({y_f})")
            stop_dict["y"] = round(y_f, 4)
        else:
            stop_dict["y"] = 0.0

        if s.get("zoom") is not None:
            z_f = float(s["zoom"])
            if not (1.0 <= z_f <= 2.5):  # Vector visual cho phép zoom tới 2.5 mà không mờ
                raise HyperFramesError(f"{where}: camera stop {i} zoom ngoài khoảng 1.0..2.5 ({z_f})")
            stop_dict["zoom"] = round(z_f, 3)
        else:
            stop_dict["zoom"] = 1.0

        if s.get("focus") is not None:
            stop_dict["focus"] = str(s["focus"])
        if s.get("at") is not None:
            if s.get("at") not in ("start", "end"):
                raise HyperFramesError(f"{where}: camera stop {i} at phải là 'start' hoặc 'end'")
            stop_dict["at"] = s["at"]
        stops.append(stop_dict)

    ease = raw.get("ease", "inOut")
    if not isinstance(ease, str) or ease not in PAN_EASES:
        raise HyperFramesError(f"{where}: camera.ease lạ {ease!r} (có: {', '.join(PAN_EASES)})")

    transition_in = raw.get("transition_in", "cut")
    if not isinstance(transition_in, str) or transition_in not in CINE_TRANSITIONS:
        raise HyperFramesError(f"{where}: camera.transition_in lạ {transition_in!r}")

    transition_out = raw.get("transition_out", "fade")
    if not isinstance(transition_out, str) or transition_out not in PAN_TRANSITIONS_OUT:
        raise HyperFramesError(f"{where}: camera.transition_out lạ {transition_out!r} (có: {', '.join(PAN_TRANSITIONS_OUT)})")

    orbit = None
    if raw.get("orbit") is not None:
        orb_raw = raw["orbit"]
        if not isinstance(orb_raw, dict):
            raise HyperFramesError(f"{where}: camera.orbit phải là object {{deg, line}}")
        extra_o = sorted(set(orb_raw) - {"deg", "line"})
        if extra_o:
            raise HyperFramesError(f"{where}: camera.orbit có khoá lạ {extra_o!r}")
        deg = orb_raw.get("deg")
        if not isinstance(deg, (list, tuple)) or len(deg) != 2:
            raise HyperFramesError(f"{where}: camera.orbit.deg phải là mảng 2 góc độ [từ, đến]")
        orb_line = orb_raw.get("line")
        if not isinstance(orb_line, (list, tuple)) or len(orb_line) != 2:
            raise HyperFramesError(f"{where}: camera.orbit.line phải là mảng 2 câu [câu_bắt_đầu, câu_kết_thúc]")
        try:
            l0, l1 = int(orb_line[0]), int(orb_line[1])
            d0, d1 = float(deg[0]), float(deg[1])
        except (TypeError, ValueError) as exc:
            raise HyperFramesError(f"{where}: camera.orbit dữ liệu sai kiểu") from exc
        if l0 < 1 or l1 < l0:
            raise HyperFramesError(f"{where}: camera.orbit.line câu không hợp lệ: [{l0}, {l1}]")
        orbit = {"deg": [round(d0, 1), round(d1, 1)], "line": [l0, l1]}

    focus_pull = _parse_focus_pull(raw.get("focus_pull"), where=where)

    out_cam: dict = {
        "canvas": canvas,
        "axis": axis,
        "stops": stops,
        "ease": ease,
        "transition_in": transition_in,
        "transition_out": transition_out,
    }
    if orbit:
        out_cam["orbit"] = orbit
    if focus_pull:
        out_cam["focus_pull"] = focus_pull
    if raw.get("end_x") is not None:
        out_cam["end_x"] = round(float(raw["end_x"]), 4)
    if raw.get("end_y") is not None:
        out_cam["end_y"] = round(float(raw["end_y"]), 4)
    if raw.get("end_zoom") is not None:
        out_cam["end_zoom"] = round(float(raw["end_zoom"]), 3)
    return out_cam


validate_pan = parse_pan


def copy_pan(media_out: dict, spec: dict, where: str = "media") -> dict | None:
    """Chép `pan` đã kiểm vào `media_out` khi plan khai báo."""
    pan = parse_pan(spec.get("pan"), where=where)
    if pan is not None:
        media_out["pan"] = pan
    layers = parse_layers(spec.get("layers"), where=where)
    if layers:
        media_out["layers"] = layers
        if pan is not None and "layers" not in pan:
            pan["layers"] = layers
    return pan


def _ease_val(u: float, ease: str) -> float:
    import math
    u = max(0.0, min(1.0, u))
    if ease in ("inOut", "sine.inOut"):
        return 0.5 * (1.0 - math.cos(math.pi * u))
    if ease == "linear":
        return u
    if ease in ("in", "sine.in"):
        return 1.0 - math.cos(math.pi / 2.0 * u)
    if ease in ("out", "sine.out"):
        return math.sin(math.pi / 2.0 * u)
    if ease == "power1.inOut":
        return 2.0 * u * u if u < 0.5 else 1.0 - math.pow(-2.0 * u + 2.0, 2) / 2.0
    if ease == "power2.inOut":
        return 4.0 * u * u * u if u < 0.5 else 1.0 - math.pow(-2.0 * u + 2.0, 3) / 2.0
    return u


def _resolve_line_times(line_times: dict | list) -> tuple[dict[int, float], dict[int, float]]:
    """Trả về (starts, ends) theo sentence_id."""
    starts: dict[int, float] = {}
    ends: dict[int, float] = {}
    if isinstance(line_times, list):
        for item in line_times:
            sid = item["sentence_id"]
            starts[sid] = float(item["start"])
            ends[sid] = float(item.get("end", item["start"]))
    elif isinstance(line_times, dict):
        for k, v in line_times.items():
            sid = int(k)
            if isinstance(v, (list, tuple)) and len(v) >= 2:
                starts[sid] = float(v[0])
                ends[sid] = float(v[1])
            elif isinstance(v, dict):
                starts[sid] = float(v["start"])
                ends[sid] = float(v.get("end", v["start"]))
            else:
                starts[sid] = float(v)
                ends[sid] = float(v)
    return starts, ends


def _interpolate_generic_prop(
    pan_spec: dict,
    prop: str,
    default_val: float,
    t: float,
    line_times: dict | list,
    dur: float | None = None,
    min_val: float = 0.0,
    max_val: float = 1.0,
    end_prop_key: str | None = None,
) -> float:
    pan = parse_pan(pan_spec) if not (isinstance(pan_spec, dict) and "stops" in pan_spec) else pan_spec
    if not pan or "stops" not in pan or not pan["stops"]:
        return default_val

    starts, ends = _resolve_line_times(line_times)
    stops = pan["stops"]
    ease = pan.get("ease", "inOut")

    pts: list[tuple[float, float]] = []
    for s in stops:
        sid = s["line"]
        if sid not in starts:
            raise HyperFramesError(f"Không tìm thấy thời gian cho câu {sid} trong line_times")
        t_pt = ends[sid] if s.get("at") == "end" else starts[sid]
        val = float(s.get(prop, default_val))
        pts.append((t_pt, val))

    last_sid = stops[-1]["line"]
    pan_end_t = ends.get(last_sid, pts[-1][0])
    if dur is not None:
        pan_end_t = max(pan_end_t, pts[0][0] + float(dur))

    if pan_end_t > pts[-1][0]:
        end_val = pan.get(end_prop_key) if end_prop_key else None
        if end_val is None:
            if prop == "x":
                if pan.get("dir") == "rtl":
                    end_val = 0.0 if pts[-1][1] > 0.0 else pts[-1][1]
                else:
                    end_val = 1.0 if pts[-1][1] < 1.0 else pts[-1][1]
            elif prop == "y":
                if pan.get("dir") == "btt":
                    end_val = 0.0 if pts[-1][1] > 0.0 else pts[-1][1]
                else:
                    end_val = 1.0 if pts[-1][1] < 1.0 else pts[-1][1]
            else:
                end_val = pts[-1][1]
        pts.append((pan_end_t, float(end_val)))

    pts.sort(key=lambda p: p[0])

    if t <= pts[0][0]:
        return round(max(min_val, min(max_val, pts[0][1])), 4)
    if t >= pts[-1][0]:
        return round(max(min_val, min(max_val, pts[-1][1])), 4)

    for i in range(1, len(pts)):
        t_prev, v_prev = pts[i - 1]
        t_next, v_next = pts[i]
        if t <= t_next:
            if t_next <= t_prev:
                return round(max(min_val, min(max_val, v_next)), 4)
            u = (t - t_prev) / (t_next - t_prev)
            eased_u = _ease_val(u, ease)
            res = v_prev + (v_next - v_prev) * eased_u
            return round(max(min_val, min(max_val, res)), 4)

    return round(max(min_val, min(max_val, pts[-1][1])), 4)


def interpolate_pan_x(
    pan_spec: dict,
    t: float,
    line_times: dict | list,
    dur: float | None = None,
) -> float:
    """Nội suy toạ độ x của camera (0.0=mép trái, 1.0=mép phải) tại thời điểm t."""
    return _interpolate_generic_prop(pan_spec, "x", 0.0, t, line_times, dur, 0.0, 1.0, "end_x")


def interpolate_pan_y(
    pan_spec: dict,
    t: float,
    line_times: dict | list,
    dur: float | None = None,
) -> float:
    """Nội suy toạ độ y của camera (0.0=mép trên, 1.0=mép dưới) tại thời điểm t (axis=v)."""
    return _interpolate_generic_prop(pan_spec, "y", 0.0, t, line_times, dur, 0.0, 1.0, "end_y")


def interpolate_pan_zoom(
    pan_spec: dict,
    t: float,
    line_times: dict | list,
    dur: float | None = None,
) -> float:
    """Nội suy độ zoom của camera (1.0..1.6) tại thời điểm t."""
    return _interpolate_generic_prop(pan_spec, "zoom", 1.0, t, line_times, dur, 1.0, 2.5, "end_zoom")


def interpolate_camera(
    cam_spec: dict,
    t: float,
    line_times: dict | list,
    dur: float | None = None,
) -> dict[str, float]:
    """Nội suy trạng thái camera {'x', 'y', 'zoom'} tại thời điểm t."""
    return {
        "x": interpolate_pan_x(cam_spec, t, line_times, dur),
        "y": interpolate_pan_y(cam_spec, t, line_times, dur),
        "zoom": interpolate_pan_zoom(cam_spec, t, line_times, dur),
    }


def interpolate_layer_track(
    layer_spec: dict,
    t: float,
    line_times: dict | list,
    dur: float | None = None,
) -> dict[str, float]:
    """Nội suy toạ độ x, y và scale của layer nhân vật tại thời điểm t."""
    track = layer_spec.get("track")
    if not track:
        return {"x": 0.5, "y": 0.5, "scale": 1.0}

    starts, ends = _resolve_line_times(line_times)
    pts: list[tuple[float, float, float, float]] = []
    for s in track:
        sid = s["line"]
        if sid not in starts:
            raise HyperFramesError(f"Không tìm thấy thời gian cho câu {sid} trong line_times")
        t_pt = ends[sid] if s.get("at") == "end" else starts[sid]
        pts.append((t_pt, float(s.get("x", 0.5)), float(s.get("y", 0.5)), float(s.get("scale", 1.0))))

    pts.sort(key=lambda p: p[0])

    if t <= pts[0][0]:
        return {"x": round(pts[0][1], 4), "y": round(pts[0][2], 4), "scale": round(pts[0][3], 4)}
    if t >= pts[-1][0]:
        return {"x": round(pts[-1][1], 4), "y": round(pts[-1][2], 4), "scale": round(pts[-1][3], 4)}

    for i in range(1, len(pts)):
        t_prev, x_prev, y_prev, s_prev = pts[i - 1]
        t_next, x_next, y_next, s_next = pts[i]
        if t <= t_next:
            if t_next <= t_prev:
                return {"x": round(x_next, 4), "y": round(y_next, 4), "scale": round(s_next, 4)}
            u = (t - t_prev) / (t_next - t_prev)
            eased_u = _ease_val(u, "inOut")
            rx = x_prev + (x_next - x_prev) * eased_u
            ry = y_prev + (y_next - y_prev) * eased_u
            rs = s_prev + (s_next - s_prev) * eased_u
            return {"x": round(rx, 4), "y": round(ry, 4), "scale": round(rs, 4)}

    return {"x": round(pts[-1][1], 4), "y": round(pts[-1][2], 4), "scale": round(pts[-1][3], 4)}


def compute_follow_camera_pan(
    layer_spec: dict,
    bg_w: int,
    bg_h: int,
    viewport_w: int = 1920,
    viewport_h: int = 1080,
) -> dict:
    """Tự động tính góc lia camera (pan) bám theo nhân vật:
    Giữ nhân vật gần 1/3 khung hình theo hướng di chuyển (640px cho LTR, 1280px cho RTL).
    """
    track = layer_spec.get("track", [])
    if not track:
        return {"dir": "ltr", "stops": [{"line": 1, "x": 0.0}], "axis": "h", "ease": "inOut", "depth": False, "intensity": 0.75}

    x0 = track[0]["x"]
    x1 = track[-1]["x"]
    if x1 > x0:
        pan_dir = "ltr"
        target_screen_x = viewport_w * (1.0 / 3.0)  # 640px
    elif x1 < x0:
        pan_dir = "rtl"
        target_screen_x = viewport_w * (2.0 / 3.0)  # 1280px
    else:
        pan_dir = "ltr"
        target_screen_x = viewport_w * 0.5  # 960px

    max_scroll_x = max(0, bg_w - viewport_w)
    stops = []
    for s in track:
        char_x = s["x"] * bg_w
        cam_x = char_x - target_screen_x
        cam_x_clamped = max(0.0, min(float(max_scroll_x), cam_x))
        pan_stop_x = cam_x_clamped / max(1.0, float(max_scroll_x))
        stops.append({"line": s["line"], "x": round(pan_stop_x, 4)})

    return {
        "dir": pan_dir,
        "stops": stops,
        "axis": "h",
        "ease": "inOut",
        "depth": False,
        "intensity": 0.75,
    }


def interpolate_layer_bob(bob_spec: dict | None, t: float) -> float:
    """Tính độ nhún dọc của nhân vật theo bước đi (pixel)."""
    if not bob_spec or not bob_spec.get("px"):
        return 0.0
    import math
    px = float(bob_spec.get("px", 3.0))
    hz = float(bob_spec.get("hz", 1.6))
    return round(math.sin(2.0 * math.pi * hz * t) * px, 3)


def interpolate_layer_sway(sway_spec: dict | None, t: float) -> float:
    """Tính độ lắc nghiêng của thuyền/bè (độ)."""
    if not sway_spec or not sway_spec.get("deg"):
        return 0.0
    import math
    deg = float(sway_spec.get("deg", 1.5))
    hz = float(sway_spec.get("hz", 0.8))
    return round(math.sin(2.0 * math.pi * hz * t) * deg, 3)


def match_color(
    layer_img: Image.Image,
    bg_patch: Image.Image,
    defringe_px: int = 2,
    light_wrap: float = 0.15,
    blend: float = 0.75,
) -> Image.Image:
    """Khớp màu/độ sáng của lớp nhân vật PNG alpha theo nền phía sau:
    1. Khử quầng màu viền (defringe) 1-2px mà KHÔNG đổi alpha.
    2. Khớp phân phối màu/độ sáng (mean & std histogram/levels) theo nền.
    3. Light-wrap: ánh sáng nền tràn nhẹ lên mép ngoài của chủ thể.
    QUY TẮC BẮT BUỘC: Giữ nguyên tuyệt đối kênh Alpha gốc.
    """
    import numpy as np
    from PIL import ImageFilter

    if layer_img.mode != "RGBA":
        layer_img = layer_img.convert("RGBA")

    orig_a = np.array(layer_img.split()[3], copy=True)
    if not np.any(orig_a > 10):
        return layer_img.copy()

    fg_rgb = np.array(layer_img.convert("RGB"), dtype=np.float32)
    bg_rgb = np.array(bg_patch.convert("RGB").resize(layer_img.size, Image.BILINEAR), dtype=np.float32)

    # 1. Defringe: khử viền quầng màu nền cũ ở biên
    core_mask = orig_a >= 240
    fringe_mask = (orig_a > 10) & (orig_a < 240)
    if np.any(core_mask) and np.any(fringe_mask) and defringe_px > 0:
        core_mean = fg_rgb[core_mask].mean(axis=0)
        for c in range(3):
            fg_rgb[fringe_mask, c] = fg_rgb[fringe_mask, c] * 0.4 + core_mean[c] * 0.6

    # 2. Histogram / Levels matching (Reinhard color transfer)
    actor_mask = orig_a > 20
    if np.any(actor_mask):
        fg_vals = fg_rgb[actor_mask]
        bg_vals = bg_rgb.reshape(-1, 3)
        fg_mean = fg_vals.mean(axis=0)
        fg_std = np.maximum(fg_vals.std(axis=0), 1e-4)
        bg_mean = bg_vals.mean(axis=0)
        bg_std = np.maximum(bg_vals.std(axis=0), 1e-4)
        matched = (fg_rgb - fg_mean) * (bg_std / fg_std) + bg_mean
        fg_rgb[actor_mask] = fg_rgb[actor_mask] * (1.0 - blend) + matched[actor_mask] * blend

    # 3. Light-wrap
    if light_wrap > 0:
        bg_blur = np.array(
            bg_patch.convert("RGB").resize(layer_img.size, Image.BILINEAR).filter(ImageFilter.GaussianBlur(radius=6)),
            dtype=np.float32,
        )
        edge_weight = np.clip((orig_a / 255.0) * (1.0 - orig_a / 255.0) * 4.0, 0.0, 1.0)
        edge_weight = edge_weight[:, :, np.newaxis] * light_wrap
        fg_rgb = fg_rgb * (1.0 - edge_weight) + bg_blur * edge_weight

    fg_rgb = np.clip(fg_rgb, 0.0, 255.0).astype(np.uint8)
    res_rgba = np.dstack([fg_rgb, orig_a])
    res = Image.fromarray(res_rgba)
    assert np.array_equal(np.array(res.split()[3]), orig_a), "Alpha channel must be identical!"
    return res


def pan_speed_check(
    pan_spec: dict,
    line_times: dict | list,
    iw: int = 3840,
    ih: int = 1080,
    max_speed: float = PAN_SPEED_MAX,
) -> list[str]:
    """Kiểm tra tốc độ trôi camera giữa các stop; cảnh báo nếu vượt max_speed (~180 px/s ở 1080p)."""
    pan = parse_pan(pan_spec) if not (isinstance(pan_spec, dict) and "stops" in pan_spec) else pan_spec
    if not pan or not pan.get("stops"):
        return []

    starts, ends = _resolve_line_times(line_times)
    stops = pan["stops"]
    axis = pan.get("axis", "h")

    if axis == "v":
        scaled_h = ih * (1920.0 / iw) if iw > 0 else 3240.0
        max_travel_px = max(0.0, scaled_h - 1080.0)
    else:
        scaled_w = iw * (1080.0 / ih) if ih > 0 else 3840.0
        max_travel_px = max(0.0, scaled_w - 1920.0)

    warnings = []
    pts = []
    for s in stops:
        sid = s["line"]
        t_pt = ends.get(sid, starts.get(sid, 0.0)) if s.get("at") == "end" else starts.get(sid, 0.0)
        coord = float(s.get("y" if axis == "v" else "x", 0.0))
        pts.append((sid, t_pt, coord))

    for i in range(1, len(pts)):
        sid_prev, t_prev, pos_prev = pts[i - 1]
        sid_curr, t_curr, pos_curr = pts[i]
        dt = t_curr - t_prev
        d_px = abs(pos_curr - pos_prev) * max_travel_px
        if dt > 0:
            speed = d_px / dt
            if speed > max_speed:
                term = "tilt dọc" if axis == "v" else "pan"
                warnings.append(
                    f"câu {sid_prev}–{sid_curr}: tốc độ {term} {speed:.1f} px/s vượt mức khuyến nghị ~{max_speed:.0f} px/s"
                )
    return warnings


def pan_zoom_resolution_check(
    pan_spec: dict,
    iw: int = 3840,
    ih: int = 1080,
) -> list[str]:
    """Cảnh báo khi phóng > 1.0 so với pixel gốc của ảnh."""
    pan = parse_pan(pan_spec) if not (isinstance(pan_spec, dict) and "stops" in pan_spec) else pan_spec
    if not pan or not pan.get("stops"):
        return []
    axis = pan.get("axis", "h")
    base_scale = (1920.0 / iw) if axis == "v" and iw > 0 else (1080.0 / ih) if ih > 0 else 1.0

    warnings = []
    for i, s in enumerate(pan["stops"]):
        z = s.get("zoom", 1.0)
        eff_scale = base_scale * z
        if eff_scale > 1.0 + 1e-4:
            warnings.append(
                f"stop {i} (câu {s['line']}): zoom {z:.2f} vượt 1.0 so với pixel gốc "
                f"(ảnh {iw}×{ih}, tỉ lệ phóng {eff_scale:.2f}x > 1.0)"
            )
    return warnings


def pan_hold_duration(pan_spec: dict, line_times: dict | list) -> float:
    """Tính tổng thời gian giữ của một pan; ném lỗi nếu vượt 20s (luật task 028)."""
    pan = parse_pan(pan_spec) if not (isinstance(pan_spec, dict) and "stops" in pan_spec) else pan_spec
    if not pan or not pan.get("stops"):
        return 0.0
    starts, ends = _resolve_line_times(line_times)
    stops = pan["stops"]
    start_t = starts.get(stops[0]["line"], 0.0)
    end_t = ends.get(stops[-1]["line"], start_t)
    dur = round(max(0.0, end_t - start_t), 2)
    if dur > PAN_HOLD_MAX_S + 0.001:
        raise HyperFramesError(
            f"câu {stops[0]['line']}: pan hold {dur:.1f}s vượt tối đa {PAN_HOLD_MAX_S:.0f}s"
        )
    return dur


def _valid_focus(focus, where: str):
    if not isinstance(focus, (list, tuple)) or len(focus) != 4:
        raise HyperFramesError(f"{where}: focus phải là [x, y, w, h]")
    try:
        x, y, w, h = (float(v) for v in focus)
    except (TypeError, ValueError) as exc:
        raise HyperFramesError(f"{where}: focus không phải số") from exc
    if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1 and x + w <= 1.001 and y + h <= 1.001):
        raise HyperFramesError(f"{where}: focus ngoài khoảng 0..1")
    return [round(x, 4), round(y, 4), round(w, 4), round(h, 4)]


def copy_motion(media_out: dict, spec: dict, iw: int | None = None, ih: int | None = None) -> None:
    """Chép preset/focus/shots khi plan có. Plan không có các khoá này thì không thêm gì."""
    if spec.get("preset") is None and spec.get("focus") is None and spec.get("shots") is None:
        return
    where = "media"
    if spec.get("preset") is not None:
        if spec.get("preset") not in MOTION_PRESETS:
            raise HyperFramesError(f"{where}: preset lạ {spec.get('preset')!r}")
        media_out["preset"] = spec["preset"]
    if spec.get("focus") is not None:
        media_out["focus"] = _valid_focus(spec["focus"], where)
    if spec.get("shots") is not None:
        shots = spec["shots"]
        if not isinstance(shots, list) or not shots or len(shots) > 3:
            raise HyperFramesError(f"{where}: shots phải là 1 đến 3 mục")
        clean = []
        for i, s in enumerate(shots):
            if not isinstance(s, dict) or s.get("preset") not in MOTION_PRESETS:
                raise HyperFramesError(f"{where}: shot {i} preset lạ")
            try:
                at = int(s.get("at"))
            except (TypeError, ValueError) as exc:
                raise HyperFramesError(f"{where}: shot {i} thiếu at") from exc
            item = {"at": at, "preset": s["preset"]}
            if s.get("focus") is not None:
                item["focus"] = _valid_focus(s["focus"], f"{where} shot {i}")
            for key in _MOTION_NUM:
                if s.get(key) is not None:
                    item[key] = float(s[key])
            clean.append(item)
        media_out["shots"] = clean
    if iw and ih:
        media_out["w"] = int(iw)
        media_out["h"] = int(ih)


def motion_layout(layout: str, spec: dict, tall: bool = False) -> str:
    """Parallax mà plan không ghi layout thì dùng depth. Layout ghi tay giữ nguyên.
    Ảnh dọc không ghi layout thì vẫn né full/depth (giữ đầu), như trước."""
    pan = spec.get("pan") if isinstance(spec.get("pan"), dict) else None
    if pan:
        if pan.get("depth") is True and not tall and layout in ("", "full", "depth"):
            return "depth"
        if not spec.get("layout") and not tall and not layout:
            return "full"
    cine = spec.get("cine") if isinstance(spec.get("cine"), dict) else None
    if cine:
        if cine.get("depth") is True and not tall and layout in ("", "full", "depth"):
            return "depth"
        if not spec.get("layout") and not tall and not layout:
            return "full"
    shots = spec.get("shots") if isinstance(spec.get("shots"), list) else []
    wants = spec.get("preset") == "parallax" or any(
        isinstance(s, dict) and s.get("preset") == "parallax" for s in shots)
    if wants and not spec.get("layout"):
        layout = "depth"
    if tall and layout in ("full", "depth") and not spec.get("layout"):
        layout = "pinned"
    return layout
# "frame" = ô mặc định của style (la bàn / khung giấy). Video động hợp tràn khung.
LAYOUT_POOL = ("frame", "full", "card3d", "split", "split_r", "polaroid", "pinned", "depth")
VIDEO_LAYOUT_POOL = ("full", "card3d", "frame")
LONG_STYLES = ("laban_long", "inkwash_long", "lacquer_long", "moon_long", "dongho_long", "ember_long", "studio_long")
# Short dọc (style BUD nạp longform.js + shortform.css) chỉ dùng được các cảnh đã
# đặt lại cho khung 1080x1920; sơ đồ rộng (vòng, bản đồ, dòng thời gian) thì không.
SHORT_VISUAL_STYLES = ("silence", "oilpaint", "lightfield", "inkwash", "dustbeam", "laban", "hongchi")
SHORT_VISUAL_TYPES = ("word", "quote", "illus", "stat", "list", "wheel", "elements",
                      "doc", "photo", "clock", "ask", "timeline")

STYLES = {
    "clean":         {"file": "index.html",                     "accent": None},
    "dossier":       {"file": "compositions/dossier.html",      "accent": "#c1121f"},
    "interrogation": {"file": "compositions/interrogation.html","accent": "#8fb8d8"},
    "vhs":           {"file": "compositions/vhs.html",          "accent": "#45d483"},
    "casemap":       {"file": "compositions/casemap.html",      "accent": "#38bdf8"},
    "night":         {"file": "compositions/night.html",        "accent": "#f59e0b"},
    # Năm trường phái cho kênh Phật giáo. Điểm chung: chuyển động gần như
    # không thấy, nhiều khoảng trống, phụ đề KHÔNG karaoke từng từ -- chữ
    # vàng nhảy theo từng tiếng là ngôn ngữ của short giật gân, ngược với
    # "để cảm xúc lắng đọng".
    "inkwash":       {"file": "compositions/inkwash.html",      "accent": "#8c2f22"},
    "oilpaint":      {"file": "compositions/oilpaint.html",     "accent": "#c9a227"},
    "silence":       {"file": "compositions/silence.html",      "accent": "#6b7f72"},
    "lightfield":    {"file": "compositions/lightfield.html",   "accent": "#d8a657"},
    "dustbeam":      {"file": "compositions/dustbeam.html",     "accent": "#e0b872"},
    "laban":         {"file": "compositions/laban.html",        "accent": "#d4a93a"},
    "hongchi":       {"file": "compositions/hongchi.html",      "accent": "#f0c14b"},
    # Khổ ngang 16:9 cho video dài (nạp thêm compositions/wide.css).
    "inkwash_wide":  {"file": "compositions/inkwash_wide.html", "accent": "#8c2f22"},
    "laban_wide":    {"file": "compositions/laban_wide.html",   "accent": "#d4a93a"},
    # Bản ngang + longform.js: sơ đồ, thẻ chương, bố cục ảnh luân phiên, video.
    "inkwash_long":  {"file": "compositions/inkwash_long.html", "accent": "#8c2f22"},
    "laban_long":    {"file": "compositions/laban_long.html",   "accent": "#d4a93a"},
    # Skin luân phiên cho video dài (02/10/2026): sơn mài (Phong Thủy), trăng thiền (Phật Giáo).
    "lacquer_long":  {"file": "compositions/lacquer_long.html", "accent": "#e2b441"},
    "moon_long":     {"file": "compositions/moon_long.html",    "accent": "#9fd8c8"},
    "dongho_long":   {"file": "compositions/dongho_long.html",  "accent": "#b8322a"},
    "ember_long":    {"file": "compositions/ember_long.html",   "accent": "#f0a35e"},
    # 15/10/2026: skin dựng từ theme Shorts Studio (plan "theme": saffron / tet-poster / son-mai / archive / blueprint ...)
    # + thiết bị studio làm sơ đồ (visual "studio"). Accent lấy từ theme.
    "studio_long":   {"file": "compositions/studio_long.html",  "accent": None},
}


def studio_long_inject(comp_src: str, theme_id: str | None) -> tuple[str, str]:
    """Tiêm theme Shorts Studio vào khuôn studio_long: :root token + --lf-theme, @font-face cục bộ (woff2 tiếng Việt),
    kit.css, core.js + mọi thiết bị, window.HFS_THEME. Trả (html, accent)."""
    import studio  # noqa: PLC0415
    if not theme_id:
        raise HyperFramesError("style studio_long cần \"theme\" trong plan (python studio.py themes)")
    try:
        th = studio.theme(theme_id)
    except OSError:
        raise HyperFramesError(f"theme studio lạ: {theme_id!r} (python studio.py themes)")
    ground = th["vars"].get("ground", "#ffffff").lstrip("#")
    lum = sum(int(ground[i:i + 2], 16) * w for i, w in ((0, .299), (2, .587), (4, .114))) if len(ground) == 6 else 255
    root_vars = ";".join(f"--{k}:{v}" for k, v in th["vars"].items()) + f";--lf-theme:{'paper' if lum > 128 else 'night'}"
    kit = (studio.ST / "kit.css").read_text(encoding="utf-8")
    head = f"<style>\n:root {{{root_vars}}}\n{studio.font_faces(th, None, url_prefix='../studio')}\n{kit}\n</style>"
    meta = {"id": th["id"], "motion": th["motion"], "seam": th.get("seam"), "karaoke": th.get("karaoke", True)}
    scripts = "\n".join(f'<script src="../studio/{p.relative_to(studio.ST).as_posix()}"></script>'
                        for p in [studio.ST / "core.js", *sorted((studio.ST / "devices").glob("*.js"))])
    scripts = f"<script>window.HFS_THEME = {json.dumps(meta, ensure_ascii=False)};</script>\n" + scripts
    return comp_src.replace("<!--HFS-HEAD-->", head, 1).replace("<!--HFS-SCRIPTS-->", scripts, 1), th["vars"].get("accent", "#B5651D")


class HyperFramesError(RuntimeError):
    pass


def sanitize_query(query: str, series_profile_key: str = "CL") -> str:
    """Chạy query stock qua `broll_query_sanitizer` của domain trước khi gửi
    đi. Bộ 34 rule của CL sinh ra sau một sự cố thật: query dịch từ nội dung
    án hình sự kéo về cảnh bạo lực. Bỏ qua bước này là quay lại đúng chỗ đó."""
    try:
        profiles = json.loads((PROJECT_ROOT / "domain_creative_profiles.json").read_text(encoding="utf-8"))
        rules = profiles.get(series_profile_key, {}).get("broll_query_sanitizer") or []
    except (OSError, json.JSONDecodeError):
        raise HyperFramesError("Không đọc được broll_query_sanitizer -- KHÔNG gửi query stock khi chưa lọc được")
    out = query
    for rule in rules:
        out = re.sub(rule["pattern"], rule["replacement"], out, flags=re.IGNORECASE)
    return out.strip()


def _shrink_image(src: Path, dst: Path, max_h: int = 2560) -> None:
    """Ảnh gốc Pexels thường 6000-8000px. Nạp thẳng vào headless Chrome là
    phí bộ nhớ và chậm; khung chỉ 1080x1920 nên 2560 chiều cao là dư."""
    res = subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(src),
         "-vf", f"scale=-2:'min({max_h},ih)'", "-q:v", "3", str(dst)],
        capture_output=True, text=True)
    if res.returncode != 0 or not dst.is_file():
        shutil.copy2(src, dst)


def _frame_local_image(src: Path, dst: Path, crop: list | None = None, *, landscape: bool = True,
                       max_h: int = 2560) -> None:
    """Ảnh AI (kind "local") vào khung: Long 24/10/2026 ra lỗi chân dung dọc bị khung ngang cắt chỉ còn búi tóc,
    và bridge chặn ảnh trùng byte trong một chương nên phải tự tạo bản cắt tay.
    - Ảnh dọc trong video ngang -> khung 16:9, chân dung giữa, hai bên là chính ảnh phóng to làm mờ.
    - `crop: [fx, fy]` hoặc `[fx, fy, zoom]` (mặc định zoom .72): khung cắt cận lấy theo vị trí fx, fy (0..1) trên
      khung đã dựng -- dùng lại một ảnh trong cùng chương mà ra hình (và byte) khác. Chân dung: để fy = 0 giữ trọn đầu."""
    from PIL import Image, ImageEnhance, ImageFilter  # noqa: PLC0415
    im = Image.open(src).convert("RGB")
    w, h = im.size
    if landscape and h > w:
        W, H = round(h * 16 / 9), h
        bg = im.resize((W, round(h * W / w))).crop((0, 0, W, H)).filter(ImageFilter.GaussianBlur(max(8, W // 40)))
        bg = ImageEnhance.Brightness(bg).enhance(.45)
        bg.paste(im, ((W - w) // 2, 0))
        im, w, h = bg, W, H
    if crop:
        fx, fy = float(crop[0]), float(crop[1])
        z = float(crop[2]) if len(crop) > 2 else .72
        cw, ch = round(w * z), round(h * z)
        x, y = round((w - cw) * min(1, max(0, fx))), round((h - ch) * min(1, max(0, fy)))
        im = im.crop((x, y, x + cw, y + ch)).resize((w, h), Image.LANCZOS)
    if im.height > max_h:
        im = im.resize((round(im.width * max_h / im.height), max_h), Image.LANCZOS)
    im.save(dst, "JPEG", quality=92)


def _short_credit(credit: str, kind: str) -> str:
    """Dòng nguồn ngắn trên màn hình (bản đầy đủ vẫn vào mô tả)."""
    c = " ".join((credit or "").split())
    if kind == "commons":
        body = c.split(" — ", 1)[-1] if " — " in c else c
        parts = body.split(", ")
        if len(parts) >= 3:  # "tác giả, giấy phép, Wikimedia Commons": tác giả dài/nhiều câu -> cắt gọn
            author = ", ".join(parts[:-2]).split(". ")[0][:40]
            body = ", ".join([author] + parts[-2:])
        return body.replace(", Wikimedia Commons", " · Wikimedia Commons")
    if kind == "museum":
        return c or "Bảo tàng mở (CC0)"
    if kind == "ext":                          # "tiêu đề — tác giả, giấy phép, Wellcome Collection" -> bỏ tiêu đề
        return c.split(" — ", 1)[-1]
    if kind == "pdvideo":                      # "tiêu đề — tác giả, giấy phép, Internet Archive" -> bỏ tiêu đề
        return c.split(" — ", 1)[-1].replace(", Wikimedia Commons", " · Wikimedia Commons")
    if kind == "openverse":                    # "tiêu đề — tác giả, CC BY 2.0, flickr via Openverse" -> bỏ tiêu đề
        body = c.split(" — ", 1)[-1]
        return body.replace(" via Openverse", " · Openverse")
    if "pexels" in c.lower():
        return "Pexels"
    if "pixabay" in c.lower():
        return "Pixabay"
    return c


def resolve_media(media: dict, sentence_id: int, stem: str,
                  domain: str = "CL", orientation: str = "portrait") -> tuple[Path, str, str, str]:
    """Lấy ảnh hoặc clip stock cho 1 câu.

    Trả (đường dẫn trong project, query đã lọc, ghi công nguồn, chuỗi filter).

    `kind` mặc định là "video" để plan cũ không đổi nghĩa. Với kênh Phật
    giáo thì "image" mới là lựa chọn chính -- `creative_director.py` đã ghi
    "stock hiếm khi hợp nội dung Phật giáo", và một tấm ảnh tĩnh + Ken Burns
    chậm hợp nhịp 18-28 giây/beat hơn một clip động.

    Cả hai nhánh đều đi qua sanitizer của domain và nghi thức `asset_safety`
    -- một asset bị gắn cờ không thể lặng lẽ quay lại qua cache."""
    kind = ((media or {}).get("kind") or "video").lower()
    if kind == "asset":
        # Sơ đồ đã vẽ theo dữ liệu tra cứu (thư viện biểu tượng của FS) -- đúng
        # vị trí, đúng chiều mũi tên. Không qua stock, không grade (màu ngũ hành
        # là thông tin), và chỉ được lấy trong thư viện đó.
        lib = (PROJECT_ROOT / "assets" / "symbol_library").resolve()
        src = (PROJECT_ROOT / (media.get("path") or "")).resolve()
        if lib not in src.parents or not src.is_file():
            raise HyperFramesError(f"câu {sentence_id}: asset phải là file trong assets/symbol_library ({src})")
        HF_ASSETS.mkdir(parents=True, exist_ok=True)
        local = HF_ASSETS / f"{stem}_s{sentence_id}{src.suffix}"
        shutil.copy2(src, local)
        return local, src.name, "", ""
    if kind == "local":
        # Ảnh / clip AI đã tải về kho (ChatGPT, Flow), chỉ lấy trong thư mục kho đó.
        lib = (REPO_ROOT / "output" / "cl_staging" / "long" / "research" / "ai_media").resolve()
        lib2 = (REPO_ROOT / "output" / "cl_staging" / "grokbot").resolve()
        src = (REPO_ROOT / (media.get("path") or "")).resolve() if not Path(media.get("path") or "").is_absolute() else Path(media.get("path")).resolve()
        if (lib not in src.parents and lib2 not in src.parents) or not src.is_file():
            raise HyperFramesError(f"câu {sentence_id}: media local phải là file trong {lib} hoặc {lib2} ({src})")
        HF_ASSETS.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() in (".mp4", ".mov", ".webm"):
            local = HF_ASSETS / f"{stem}_s{sentence_id}{src.suffix.lower()}"
            shutil.copy2(src, local)
        else:
            local = HF_ASSETS / f"{stem}_s{sentence_id}.jpg"
            _frame_local_image(src, local, media.get("crop"), landscape=orientation == "landscape")
        return local, src.name, media.get("credit") or "", ""
    if kind == "museum":
        # Hiện vật bảo tàng mở (The Met / AIC / Cleveland), CHỈ CC0 -- hf_museum kiểm giấy phép.
        import hf_museum  # noqa: PLC0415
        try:
            src, credit = hf_museum.fetch(media.get("ref") or "")
        except ValueError as exc:
            raise HyperFramesError(f"câu {sentence_id}: {exc}") from exc
        HF_ASSETS.mkdir(parents=True, exist_ok=True)
        local = HF_ASSETS / f"{stem}_s{sentence_id}.jpg"
        _shrink_image(src, local)
        return local, media.get("ref", ""), credit, ""
    if kind == "ext":
        # Wellcome / Art Institute of Chicago / Europeana (hf_extmedia kiểm giấy phép PD/CC0/CC BY/CC BY-SA).
        import hf_extmedia  # noqa: PLC0415
        try:
            src, credit = hf_extmedia.fetch(media.get("ref") or "")
        except ValueError as exc:
            raise HyperFramesError(f"câu {sentence_id}: {exc}") from exc
        HF_ASSETS.mkdir(parents=True, exist_ok=True)
        local = HF_ASSETS / f"{stem}_s{sentence_id}.jpg"
        _shrink_image(src, local)
        return local, media.get("ref", ""), credit, ""
    if kind == "openverse":
        # Ảnh giấy phép mở qua Openverse (Flickr, Smithsonian, bảo tàng...): CC0/PD/CC BY/CC BY-SA, hf_openverse kiểm.
        import hf_openverse  # noqa: PLC0415
        try:
            src, credit = hf_openverse.fetch(media.get("ref") or "")
        except ValueError as exc:
            raise HyperFramesError(f"câu {sentence_id}: {exc}") from exc
        HF_ASSETS.mkdir(parents=True, exist_ok=True)
        local = HF_ASSETS / f"{stem}_s{sentence_id}.jpg"
        _shrink_image(src, local)
        return local, media.get("ref", ""), credit, ""
    if kind == "pdvideo":
        # Phim tư liệu PD/CC (Commons / Internet Archive / NASA): hf_pdvideo kiểm giấy phép, cắt [start, start+dur]
        # (tối đa 20 s) thành mp4 1920x1080 không tiếng -> đi nhánh <video muted> như clip stock.
        import hf_pdvideo  # noqa: PLC0415
        treatment = (media.get("treatment") or "").strip()
        denied = [w for w in FORBIDDEN_TREATMENT.get(domain, ()) if w in treatment.lower()]
        if denied:
            raise HyperFramesError(f"câu {sentence_id}: treatment {denied[0]!r} bị cấm trên media của kênh {domain}")
        try:
            src, credit = hf_pdvideo.fetch(media.get("ref") or "", media.get("start", 0), media.get("dur", 15),
                                           media.get("fit") or "cover")
        except ValueError as exc:
            raise HyperFramesError(f"câu {sentence_id}: {exc}") from exc
        HF_ASSETS.mkdir(parents=True, exist_ok=True)
        local = HF_ASSETS / f"{stem}_s{sentence_id}.mp4"
        shutil.copy2(src, local)
        return local, media.get("ref", ""), credit, treatment
    if kind == "commons":
        # Tư liệu Wikimedia Commons, CHỈ phạm vi công cộng / CC0 (hf_commons kiểm giấy phép).
        import hf_commons  # noqa: PLC0415
        try:
            src, credit = hf_commons.fetch(media.get("file") or "", allow_by=bool(media.get("by")), page=media.get("page"))
        except ValueError as exc:
            raise HyperFramesError(f"câu {sentence_id}: {exc}") from exc
        HF_ASSETS.mkdir(parents=True, exist_ok=True)
        local = HF_ASSETS / f"{stem}_s{sentence_id}.jpg"
        _shrink_image(src, local)
        return local, media.get("file", ""), credit, ""
    raw = (media or {}).get("query", "").strip()
    if not raw:
        raise HyperFramesError(f"câu {sentence_id}: media thiếu 'query'")
    if kind not in ("video", "image"):
        raise HyperFramesError(f"câu {sentence_id}: media kind lạ {kind!r} (chỉ 'video' hoặc 'image')")
    query = sanitize_query(raw, domain)
    HF_ASSETS.mkdir(parents=True, exist_ok=True)

    treatment = (media.get("treatment") or "").strip()
    denied = [w for w in FORBIDDEN_TREATMENT.get(domain, ()) if w in treatment.lower()]
    if denied:
        raise HyperFramesError(
            f"câu {sentence_id}: treatment {denied[0]!r} bị cấm trên media của kênh {domain}")
    grade = treatment or HOUSE_GRADE.get(domain, "")

    if kind == "image":
        import stock_image  # noqa: PLC0415
        found = stock_image.get_or_fetch_stock_image(query, orientation)
        if found is not None:
            os.utime(found)   # đánh dấu "vừa dùng" cho hf_cleanup (cache stock dọn theo lần dùng cuối)
        if found is None:
            raise HyperFramesError(f"câu {sentence_id}: không tìm được ảnh cho {query!r}")
        local = HF_ASSETS / f"{stem}_s{sentence_id}.jpg"
        _shrink_image(found, local)
        return local, query, stock_image.credit_line(found), grade

    import asset_generation  # noqa: PLC0415 -- kéo theo cả stack nặng, chỉ nạp khi cần
    clip = asset_generation.get_or_fetch_stock_video(query)
    if clip is not None:
        os.utime(clip)
    if clip is None:
        raise HyperFramesError(f"câu {sentence_id}: không lấy được clip cho {query!r}")
    local = HF_ASSETS / f"{stem}_s{sentence_id}{clip.suffix}"
    shutil.copy2(clip, local)
    return local, query, "Video: Pexels/Pixabay", grade


def _split_marked(line_text: str) -> list[tuple[str, bool]]:
    """Tách câu thành các đoạn (text, đang-được-đánh-dấu). Phải tách ở mức
    CÂU chứ không phải mức từ: cụm "**Điều 22**" nằm trên 2 token, bóc
    marker theo từng token sẽ để lọt dấu ** ra tận phụ đề trên màn hình
    (đã dính đúng lỗi này ở bản render thử đầu tiên)."""
    parts, pos = [], 0
    for m in _MARKER_RE.finditer(line_text):
        if m.start() > pos:
            parts.append((line_text[pos:m.start()], False))
        parts.append((m.group(1), True))
        pos = m.end()
    if pos < len(line_text):
        parts.append((line_text[pos:], False))
    return parts


def _words_with_timing(line_text: str, start: float, end: float, env=None) -> list[dict]:
    """Rải mốc thời gian cho từng từ của DÒNG GỐC (còn hoa/thường, còn số
    dạng chữ số) theo tỷ lệ độ dài ký tự trong khoảng [start, end] của
    segment TTS tương ứng.

    KHÔNG dùng text đã normalize trong manifest làm phụ đề: TTS chuyển
    "Điều 22" -> "điều hai mươi hai" để đọc, hiển thị lên màn hình như vậy
    là sai. Đổi lại, số từ hai bên lệch nhau nên timing chỉ nội suy được
    theo tỷ lệ -- chấp nhận được với Short (câu ngắn, sai số < 0.2s), khác
    hẳn nhu cầu của video dài.
    """
    tokens: list[tuple[str, bool]] = []
    for chunk, hot in _split_marked(line_text):
        for tok in chunk.split():
            # Dấu câu đứng riêng sau 1 cụm **đánh dấu** (vd "**cần thiết**:")
            # phải dính vào từ trước, nếu không phụ đề hiện ra " : " lơ lửng
            # giữa câu.
            if tokens and re.fullmatch(r"[.,:;!?…)\]}»\"']+", tok):
                prev, prev_hot = tokens[-1]
                tokens[-1] = (prev + tok, prev_hot)
            else:
                tokens.append((tok, hot))
    if not tokens:
        return []
    if env is not None:
        # Video dài: bám năng lượng âm thanh thật (hf_align) -- xem docstring đó.
        import hf_align  # noqa: PLC0415
        times = hf_align.word_times(env[0], env[1], start, end, [hf_align.token_weight(t) for t, _ in tokens])
        return [{"w": tok, "t": t, "d": d, "hot": hot} for (tok, hot), (t, d) in zip(tokens, times)]
    weights = [len(t) + 1 for t, _ in tokens]
    total = sum(weights)
    span = max(0.2, end - start)
    out, cursor = [], start
    for (tok, hot), w in zip(tokens, weights):
        d = span * w / total
        out.append({"w": tok, "t": round(cursor, 3), "d": round(d, 3), "hot": hot})
        cursor += d
    return out


def _key_parts(line_text: str, avoid: str | None = None) -> list[dict]:
    """Cụm **đánh dấu** dài nhất của câu trở thành tiêu điểm trên thẻ hồ sơ
    giữa khung. Không có cụm nào -> lấy 4 từ đầu, để thẻ không bao giờ rỗng.

    `avoid` là key của câu TRƯỚC: hai thẻ liên tiếp cùng chữ trông như
    video bị đứng hình, nên nếu trùng thì lấy cụm dài kế tiếp (chỉ khi
    còn cụm khác -- không bịa chữ mới)."""
    marks = sorted(_MARKER_RE.findall(line_text), key=len, reverse=True)
    if avoid:
        distinct = [m for m in marks if m.upper() != avoid.upper()]
        marks = distinct or marks
    if marks:
        key = marks[0]
    else:
        key = " ".join(_MARKER_RE.sub(r"\1", line_text).split()[:4])
    return [{"t": key.upper(), "hot": True}]


def build_lines(script_path: Path, manifest_path: Path, figures: dict | None = None,
                figure_labels: dict | None = None, align_audio: Path | None = None) -> list[dict]:
    """Ghép DÒNG kịch bản gốc (nguồn chữ) với SEGMENT của manifest TTS
    (nguồn thời gian). Yêu cầu số dòng == số segment: pipeline chunk theo
    đúng dòng, lệch nhau nghĩa là kịch bản đã bị sửa sau khi render audio --
    fail to, không âm thầm ghép lệch câu.
    """
    raw_lines = [l.strip() for l in script_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    segments = json.loads(manifest_path.read_text(encoding="utf-8"))["segments"]
    if len(raw_lines) != len(segments):
        raise HyperFramesError(
            f"Lệch: {len(raw_lines)} dòng kịch bản vs {len(segments)} segment audio "
            f"({script_path.name}) -- render lại audio từ đúng kịch bản này trước.")
    figures = figures or {}
    figure_labels = figure_labels or {}
    env = None
    if align_audio is not None and Path(align_audio).is_file():
        try:
            import hf_align  # noqa: PLC0415
            env = hf_align.energy_envelope(align_audio)
        except Exception as exc:  # noqa: BLE001 -- đọc được audio là tốt, không được thì chia theo tỉ lệ như cũ
            print(f"CẢNH BÁO: không bám được mốc từ theo âm thanh ({exc}), chia theo tỉ lệ", file=sys.stderr)
    lines, prev_key = [], None
    for idx, (raw, seg) in enumerate(zip(raw_lines, segments), start=1):
        parts = _key_parts(raw, avoid=prev_key)
        prev_key = parts[0]["t"]
        lines.append({
            "sentence_id": idx,
            "start": round(float(seg["start"]), 3),
            "end": round(float(seg["end"]), 3),
            "key_parts": parts,
            "words": _words_with_timing(raw, float(seg["start"]), float(seg["end"]), env),
            # Câu in đậm TRỌN câu là tiêu đề chương (video dài) -- ảnh không
            # được giữ tràn qua nó.
            "heading": raw.startswith("**") and raw.endswith("**") and raw.count("**") == 2,
        })
        fig = figures.get(str(idx)) or figures.get(idx)
        if fig:
            # Figure gắn theo SỐ THỨ TỰ CÂU (1-based), không theo thời gian:
            # kịch bản là nguồn sự thật, sửa câu thì figure đi theo.
            # CHUYỂN TIẾP NGUYÊN VẸN -- bridge không tính toạ độ, không sinh
            # chữ, không hiểu figure (ADR-0001). Mọi thứ đó thuộc engine.js.
            lines[-1]["figure"] = fig
            labels = figure_labels.get(str(idx)) or figure_labels.get(idx)
            if labels:
                lines[-1]["figure_labels"] = labels
    return lines


# Video dài: ảnh chỉ sống đúng một câu thì 2/3 thời lượng là thẻ chữ trên nền
# trơn (đo trên L_bud_01, 29/09/2026). Ảnh phải ở lại qua các câu sau, tới ảnh
# kế, tới tiêu đề chương, hoặc tới trần thời gian -- cái nào đến trước.
HOLD_MAX_S = 22.0
OPENING_HOLD_S = 40.0
OVERLAY_VISUAL_TYPES = ("ask", "timeline", "stat", "list")


def is_overlay_visual(spec: dict | None) -> bool:
    """Thẻ ask/timeline/stat/list có `overlay: true`: phủ nền mờ trong suốt lên ảnh đang chạy."""
    return bool(isinstance(spec, dict) and spec.get("overlay") and spec.get("type") in OVERLAY_VISUAL_TYPES)


def _visual_spec_of(lines: list[dict], ln: dict) -> dict | None:
    if ln.get("visual"):
        return ln["visual"]
    if ln.get("visual_cont"):
        vc = int(ln["visual_cont"]) - 1
        if 0 <= vc < len(lines):
            return lines[vc].get("visual")
    return None


def auto_layouts(media: dict, seed: str) -> dict[int, str]:
    """Bố cục cho từng ảnh/clip mà plan không ghi `layout`: lấy bố cục ÍT DÙNG
    NHẤT, không lặp lại ngay bố cục trước, hoà thì bốc theo hạt giống = tên
    video (render lại ra y hệt, video khác ra thứ tự khác). Bản đầu của video
    dài dùng một ô la bàn cho cả 25 ảnh -- người xem chê nhàm."""
    import random  # noqa: PLC0415
    rng = random.Random(f"layout|{seed}")
    counts = {k: 0 for k in LAYOUT_POOL}
    last, out = None, {}
    for sid in sorted(int(k) for k in media):
        spec = media.get(str(sid)) or media.get(sid) or {}
        if (spec.get("kind") or "").lower() == "asset":
            continue
        chosen = (spec.get("layout") or "").lower()
        if not chosen:
            pool = VIDEO_LAYOUT_POOL if (spec.get("kind") or "video").lower() == "video" else LAYOUT_POOL
            cand = [p for p in pool if p != last] or list(pool)
            lo = min(counts.get(p, 0) for p in cand)
            chosen = rng.choice([p for p in cand if counts.get(p, 0) == lo])
        counts[chosen] = counts.get(chosen, 0) + 1
        last, out[sid] = chosen, chosen
    return out


WORDTS_FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,800;1,700;1,800'
                '&family=Lora:ital,wght@0,400;0,600;1,400;1,600&family=Oswald:wght@600;700&family=League+Gothic'
                '&family=Cormorant+Garamond:wght@600;700&family=Charm:wght@700&family=Fraunces:opsz,wght@144,900'
                '&display=block" rel="stylesheet" />')


def _studio_ats(node) -> list[int]:
    """Số câu của mọi mốc {"at": n, "word"...} trong spec thiết bị studio (để kiểm khoảng câu như sơ đồ thường)."""
    out = []
    if isinstance(node, dict):
        if isinstance(node.get("at"), int) and set(node) <= {"at", "word", "offset"}:
            return [node["at"]]
        for v in node.values():
            out += _studio_ats(v)
    elif isinstance(node, list):
        for v in node:
            out += _studio_ats(v)
    return out


def style_scene_issues(spans: list[tuple[int, int, str]], cap: int = STYLE_MAX_PER_RENDER) -> list[str]:
    """Luật PO cho bộ style bổ sung: tối đa `cap` cảnh style mỗi lần render (= mỗi chương khi render theo
    chương; hf_batch_render kiểm thêm cả video), và không hai cảnh style liền nhau (cảnh sau bắt đầu ngay
    câu kế tiếp khoảng của cảnh trước). `spans` = [(câu đầu, câu cuối, type)]."""
    out: list[str] = []
    spans = sorted(spans)
    if len(spans) > cap:
        out.append(f"bộ style bổ sung: {len(spans)} cảnh ({', '.join(f'câu {s}:{t}' for s, _, t in spans)}) "
                   f"> {cap} cảnh một lần render -- style là điểm nhấn, không phải nền chính")
    for (s0, u0, t0), (s1, _u1, t1) in zip(spans, spans[1:]):
        if s1 <= u0 + 1:
            out.append(f"bộ style bổ sung: câu {s0} ({t0}) và câu {s1} ({t1}) liền nhau -- chèn ít nhất một cảnh thường ở giữa")
    return out


def apply_visuals(lines: list[dict], visuals: dict, media: dict) -> None:
    """Gắn sơ đồ (plan `visuals`) vào câu gốc và đánh dấu các câu nó còn chiếm
    màn hình (`until`, mặc định = câu của bước cuối). Bridge không hiểu nội dung
    sơ đồ -- chỉ kiểm loại, khoảng câu, và không cho sơ đồ đè lên ảnh/figure."""
    n = len(lines)
    style_spans: list[tuple[int, int, str]] = []   # (câu đầu, câu cuối, type) của các cảnh style bổ sung
    for key, spec in visuals.items():
        sid = int(key)
        if not 1 <= sid <= n:
            raise HyperFramesError(f"sơ đồ ở câu {sid}: ngoài kịch bản ({n} câu)")
        if (spec.get("type") or "") not in VISUAL_TYPES:
            raise HyperFramesError(f"câu {sid}: loại sơ đồ lạ {spec.get('type')!r} (có: {', '.join(VISUAL_TYPES)})")
        if spec.get("type") == "studio":
            if not spec.get("device"):
                raise HyperFramesError(f"câu {sid}: visual studio thiếu \"device\" (python studio.py devices)")
            ats = _studio_ats(spec)
        else:
            ats = [int(x["at"]) for x in (spec.get("steps") or spec.get("items") or spec.get("pins") or spec.get("rows") or spec.get("notes") or []) if x.get("at")]
        until = int(spec.get("until") or max([sid] + ats))
        if any(a < sid or a > until for a in ats) or until > n:
            raise HyperFramesError(f"câu {sid}: bước của sơ đồ phải nằm trong câu {sid}..{until}")
        overlay = is_overlay_visual(spec)
        for k in range(sid, until + 1):
            ln = lines[k - 1]
            if (str(k) in media or k in media) and not overlay:
                raise HyperFramesError(f"câu {k}: vừa có ảnh vừa nằm trong sơ đồ của câu {sid}")
            if (ln.get("figure") or {}).get("type", "none") != "none":
                raise HyperFramesError(f"câu {k}: vừa có figure vừa nằm trong sơ đồ của câu {sid}")
            if k > sid and (ln.get("visual") or ln.get("visual_cont")):
                raise HyperFramesError(f"câu {k}: hai sơ đồ chồng nhau")
        if spec.get("camera") is not None:
            spec["camera"] = parse_camera(spec["camera"], where=f"câu {sid} visual {spec.get('type')}")
        if spec.get("type") in STYLE_VISUAL_TYPES:
            style_spans.append((sid, until, spec["type"]))
        lines[sid - 1]["visual"] = spec
        for k in range(sid + 1, until + 1):
            lines[k - 1]["visual_cont"] = sid
    for issue in style_scene_issues(style_spans):
        raise HyperFramesError(issue)


def media_holds(
    lines: list[dict],
    media_ids: set[int],
    max_span: float = HOLD_MAX_S,
    media_specs: dict | None = None,
) -> dict[int, int]:
    """{chỉ số dòng có ảnh: chỉ số dòng cuối cùng ảnh còn hiện} (0-based).
    Trong 40s đầu (026): câu không có hình giữ hình của mốc trước (không rơi về chữ khoá kể cả quá max_span);
    thẻ ask/timeline/stat/list có overlay: true phủ lên ảnh đang chạy, không ngắt nhịp giữ ảnh."""
    holds = {}
    media_specs = media_specs or {}
    n = len(lines)
    for i, ln in enumerate(lines):
        sid = ln["sentence_id"]
        if sid not in media_ids:
            continue
        spec = media_specs.get(str(sid)) or media_specs.get(sid) or {}
        pan = parse_pan(spec.get("pan"), where=f"câu {sid}") if isinstance(spec, dict) else None

        min_k = i
        if pan and pan.get("stops"):
            last_pan_line = max(s["line"] for s in pan["stops"])
            for idx_check in range(i, len(lines)):
                if lines[idx_check]["sentence_id"] == last_pan_line:
                    min_k = idx_check
                    break

        k = i
        last_valid = i
        while k + 1 < n:
            nxt = lines[k + 1]
            in_opening = nxt.get("start", 0.0) < OPENING_HOLD_S
            vspec = _visual_spec_of(lines, nxt)
            is_ov = is_overlay_visual(vspec)
            has_blocking_visual = bool(vspec and not is_ov)
            if (nxt["sentence_id"] in media_ids
                    or nxt.get("heading")
                    or (nxt.get("figure") or {}).get("type", "none") != "none"
                    or has_blocking_visual
                    or (not in_opening and nxt["end"] - ln["start"] > max_span)):
                break
            k += 1
        k = max(k, min_k)
        if pan:
            pan_dur = lines[k]["end"] - ln["start"]
            if pan_dur > PAN_HOLD_MAX_S + 0.001:
                raise HyperFramesError(f"câu {sid}: pan hold {pan_dur:.1f}s vượt tối đa {PAN_HOLD_MAX_S:.0f}s")
        holds[i] = k
    return holds


def load_channel_typography(channel_or_series: str, opts: dict | None = None) -> dict:
    """Đọc cấu hình typography từ hồ sơ kênh (library/channels/*.yaml) hoặc opts."""
    opts = opts or {}
    if isinstance(opts.get("typography"), dict):
        return opts["typography"]
    if isinstance(opts.get("channel_profile"), dict) and "typography" in opts["channel_profile"]:
        return opts["channel_profile"].get("typography") or {}
    if opts.get("profile"):
        prof_path = Path(opts["profile"])
        if prof_path.is_file():
            try:
                raw = json.loads(prof_path.read_text(encoding="utf-8"))
                return raw.get("typography") or {}
            except Exception:
                try:
                    import yaml
                    raw = yaml.safe_load(prof_path.read_text(encoding="utf-8")) or {}
                    return raw.get("typography") or {}
                except Exception:
                    pass
    ch = opts.get("channel") or channel_or_series
    channels_dir = PROJECT_ROOT / "library" / "channels"
    p = channels_dir / f"{ch}.yaml"
    if not p.is_file():
        p = channels_dir / f"{channel_or_series}.yaml"
    if p.is_file():
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
            return raw.get("typography") or {}
        except Exception:
            try:
                import yaml
                raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
                return raw.get("typography") or {}
            except Exception:
                pass
    return {}


def render(script: Path, wav: Path, series: str, output: Path, *, badge: str = "",
           kicker: str | None = None, lane: str | None = None, footer: str | None = None, bgm: Path | None = None,
           bgm_gain: float = 0.16, quality: str = "looks", style: str = "clean",
           figures: dict | None = None, figure_labels: dict | None = None,
           media: dict | None = None, timeout: int = DEFAULT_TIMEOUT_S,
           hold_media: bool | None = None, visuals: dict | None = None, opts: dict | None = None) -> dict:
    opts = opts or {}
    # Tên file tạm trong HF_PROJECT / HF_ASSETS (dùng CHUNG giữa các lần render) phải riêng cho từng output:
    # 02/10/2026 render F4 và B4 song song, cả hai đều có chương "ch01" -> .vars_ch01.json / .render_ch01.html
    # ghi đè nhau, ch01 của B4 ra nguyên hình của F4. Gắn băm đường dẫn output để hai video không bao giờ đụng nhau.
    uid = f"{output.stem}_{hashlib.sha1(str(Path(output).resolve()).encode()).hexdigest()[:8]}"
    if series not in SERIES_PRESETS:
        raise HyperFramesError(f"series lạ: {series!r} (có: {', '.join(SERIES_PRESETS)})")
    if lane and lane not in SERIES_LANES.get(series, {}):
        raise HyperFramesError(f"lane lạ {lane!r} cho series {series!r} "
                               f"(có: {', '.join(SERIES_LANES.get(series, {})) or 'không có lane'})")
    if style not in STYLES:
        raise HyperFramesError(f"style lạ: {style!r} (có: {', '.join(STYLES)})")
    # ADR-0004: validate TRƯỚC render. Bridge không biết vẽ, nhưng biết cái gì
    # hợp lệ -- nếu bỏ bước này, figure sai chỉ lộ ra ở frame đã render xong.
    if figures or figure_labels:
        import hf_figure_contract as _contract
        errors = _contract.validate({"figures": figures or {}, "figure_labels": figure_labels or {}})
        if errors:
            raise HyperFramesError("Figure không khớp hợp đồng:\n  - " + "\n  - ".join(errors))

    comp_rel = Path(STYLES[style]["file"])
    comp_dir = (HF_PROJECT / comp_rel).parent
    # File style nằm trong compositions/ nên đường dẫn asset phải lùi 1 cấp;
    # index.html nằm ngay gốc project thì không.
    asset_prefix = ""  # renderer phân giải media theo GỐC project, không theo vị trí file composition
    manifest = wav.with_suffix(".json")
    if not manifest.is_file():
        raise HyperFramesError(f"Thiếu manifest TTS cạnh wav: {manifest}")
    preset = SERIES_PRESETS[series]
    # Video dài: mốc từ bám âm thanh thật (chữ động, dạ quang, ghim bản đồ bám theo).
    lines = build_lines(script, manifest, figures, figure_labels,
                        align_audio=wav if (lane == "long" or visuals) else None)

    media_tags: list[str] = []
    media_credits: list[str] = []
    seen_assets: dict[str, object] = {}
    if any((v or {}).get("type") == "map" for v in (visuals or {}).values()):
        import hf_geo  # noqa: PLC0415 -- nướng biên giới + toạ độ trước, render không cần mạng
        visuals = {k: (hf_geo.bake(v) if v.get("type") == "map" else v) for k, v in visuals.items()}
    region_credits: list[str] = []
    if any((v or {}).get("type") in ("region", "profile") for v in (visuals or {}).values()):
        import hf_geo_region  # noqa: PLC0415 -- nền địa hình + mặt cắt nướng sẵn (cache), render không tính địa lý
        for key, v in list(visuals.items()):
            if v.get("type") == "region":
                v = hf_geo_region.bake(v)
                dst = HF_ASSETS / f"{uid}_v{key}_region{Path(v['_geo']['src']).suffix}"
                shutil.copy2(v["_geo"]["src"], dst)
                v["_geo"]["src"] = f"assets/{dst.name}"
                visuals[key] = v
            elif v.get("type") == "profile":
                visuals[key] = hf_geo_region.profile(v)
            else:
                continue
            if hf_geo_region.CREDIT not in region_credits:
                region_credits.append(hf_geo_region.CREDIT)
    if visuals and style not in LONG_STYLES:
        if style not in SHORT_VISUAL_STYLES:
            raise HyperFramesError(f"style {style!r} không nạp kho cảnh (có: {', '.join(LONG_STYLES + SHORT_VISUAL_STYLES)})")
        bad = sorted({v.get("type") for v in visuals.values()} - set(SHORT_VISUAL_TYPES))
        if bad:
            raise HyperFramesError(f"short dọc không dùng được cảnh {bad} (chỉ: {', '.join(SHORT_VISUAL_TYPES)})")
    visual_credits: list[str] = list(region_credits)
    for key, spec in (visuals or {}).items():
        if spec.get("type") not in ("doc", "photo", "museum", "napam", "cuudieu", "eclipse", "relic", "studio", "film16"):
            continue
        if spec.get("type") == "studio" and not (spec.get("museum") or spec.get("file") or spec.get("query")):
            continue  # thiết bị studio không có ảnh tư liệu
        if spec.get("type") == "film16" and not (spec.get("museum") or spec.get("file") or spec.get("query")):
            continue  # phim 16 mm chỉ thẻ tiêu đề, ảnh nền là tuỳ chọn
        if spec.get("type") in ("cuudieu", "eclipse") and not (spec.get("museum") or spec.get("file") or spec.get("query")):
            continue  # cảnh vẽ SVG thuần, ảnh nền là tuỳ chọn
        # Ảnh của cảnh tư liệu: bảo tàng CC0 (museum: "met:..|aic:..|cma:.."), Commons (file) hoặc stock (query).
        if spec.get("museum"):
            m = {"kind": "museum", "ref": spec["museum"]}
        else:
            m = {"kind": "commons", "file": spec["file"], "page": spec.get("page"), "by": spec.get("by")} if spec.get("file") else {"kind": "image", "query": spec.get("query", "")}
        asset, _q, credit, _g = resolve_media(m, 900 + int(key), uid, SERIES_DOMAIN.get(series, "CL"),
                                              orientation="portrait" if style not in LONG_STYLES else "landscape")
        from PIL import Image  # noqa: PLC0415
        if spec.get("type") == "relic":
            # 2.5D: nền + hiện vật cắt rời + nét phác + viền (hf_relic, Vision cục bộ). Không tách được -> museum thường.
            import hf_relic  # noqa: PLC0415
            rel = hf_relic.prepare(asset)
            if rel is None:
                spec["type"] = "museum"
            else:
                for part in ("bg", "fg", "sketch"):
                    dst = HF_ASSETS / f"{uid}_v{key}_{part}{Path(rel[part]).suffix}"
                    shutil.copy2(rel[part], dst)
                    spec[part] = f"assets/{dst.name}"
                spec["outline"], spec["w"], spec["h"] = rel["outline"], rel["w"], rel["h"]
                spec["src"] = spec["fg"]
                visual_credits.append(credit)
                continue
        with Image.open(asset) as im:
            spec["w"], spec["h"] = im.size
        spec["src"] = f"assets/{asset.name}"
        visual_credits.append(credit)
    apply_visuals(lines, visuals or {}, media or {})
    if lane == "long":
        chap = int(opts.get("chapter_base") or 0)   # render theo chương: đánh số tiếp theo cả video
        for ln in lines:
            if ln.get("heading"):
                chap += 1
                ln["chapter_no"] = chap
    if hold_media is None:
        hold_media = lane == "long"
    holds = media_holds(lines, {int(k) for k in (media or {})}, media_specs=media) if hold_media else {}
    auto = auto_layouts(media or {}, output.stem) if style in LONG_STYLES else {}
    for li, line in enumerate(lines):
        spec = (media or {}).get(str(line["sentence_id"])) or (media or {}).get(line["sentence_id"])
        if not spec:
            continue
        if line.get("figure") and line["figure"].get("type") != "none":
            raise HyperFramesError(
                f'câu {line["sentence_id"]}: có cả figure lẫn clip -- chọn một. '
                f'Hai thứ cùng chiếm vùng giữa khung.')
        asset, used_query, credit, grade = resolve_media(
            spec, line["sentence_id"], uid, SERIES_DOMAIN.get(series, "CL"),
            orientation="landscape" if style.endswith(("_wide", "_long")) else "portrait")
        # Hai query khác nhau vẫn có thể về cùng một ảnh -- Pexels trả đúng
        # một tấm nhà sư cho cả "alms round" lẫn "alms bowl", và video ra hai
        # màn liền nhau giống hệt mà không lỗi nào nổ. Chặn ở đây, nói rõ câu nào.
        digest = hashlib.sha1(asset.read_bytes()).hexdigest()
        if digest in seen_assets:
            raise HyperFramesError(
                f"câu {line['sentence_id']}: ảnh/clip trùng hệt câu {seen_assets[digest]} "
                f"(query {used_query!r}) -- đổi query cho một trong hai câu")
        seen_assets[digest] = line["sentence_id"]
        cine = parse_cine(spec.get("cine"), where=f"câu {line['sentence_id']}")
        if cine is not None:
            if style not in LONG_STYLES:
                raise HyperFramesError(
                    f"câu {line['sentence_id']}: cine cần style video dài ({', '.join(LONG_STYLES)})")
            if asset.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
                raise HyperFramesError(
                    f"câu {line['sentence_id']}: cine chỉ dùng cho ảnh tĩnh, không phải {asset.name!r}")
        pan = parse_pan(spec.get("pan"), where=f"câu {line['sentence_id']}")
        if pan is not None:
            if style not in LONG_STYLES:
                raise HyperFramesError(
                    f"câu {line['sentence_id']}: pan cần style video dài ({', '.join(LONG_STYLES)})")
            if asset.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
                raise HyperFramesError(
                    f"câu {line['sentence_id']}: pan chỉ dùng cho ảnh tĩnh, không phải {asset.name!r}")
        style_attr = f' style="filter: {grade}"' if grade else ""
        how = (spec.get("reveal") or "").lower()
        if how and how not in REVEALS:
            raise HyperFramesError(f"câu {line['sentence_id']}: reveal lạ {how!r} (có: {', '.join(REVEALS)})")
        if how == "ink" and style not in PAPER_STYLES:
            raise HyperFramesError(
                f"câu {line['sentence_id']}: reveal 'ink' cần style nền giấy "
                f"({', '.join(PAPER_STYLES)}), không phải {style!r}. "
                f"Trên nền tối nó ra một mảng sáng lem, không ra vệt mực.")
        reveal = f" media-reveal-{how}" if how else ""
        layout = (spec.get("layout") or auto.get(line["sentence_id"], "")).lower()
        if layout == "frame":
            layout = ""
        # Ảnh dọc (chân dung, tượng, tháp) trong khung ngang: cover cắt giữa ảnh -> mất đầu
        # (F19: chân dung Crawfurd phủ full 16:9 chỉ còn từ cổ xuống). Không cho full/depth, neo phía trên.
        tall = ""
        iw = ih = None
        if style in LONG_STYLES and asset.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            from PIL import Image  # noqa: PLC0415
            with Image.open(asset) as im:
                iw, ih = im.size
                if im.height > im.width * 1.1:
                    tall = " media-tall"
            layout = motion_layout(layout, spec, tall=bool(tall))
        if pan is not None:
            spd_warns = pan_speed_check(pan, lines, iw or 3840, ih or 1080)
            for w in spd_warns:
                print(f"[CẢNH BÁO PAN] {w}", file=sys.stderr)
            zoom_warns = pan_zoom_resolution_check(pan, iw or 3840, ih or 1080)
            for w in zoom_warns:
                print(f"[CẢNH BÁO PAN] {w}", file=sys.stderr)
        if layout and layout not in MEDIA_LAYOUTS:
            raise HyperFramesError(f"câu {line['sentence_id']}: layout lạ {layout!r} (có: {', '.join(MEDIA_LAYOUTS)})")
        if layout and style not in LONG_STYLES:
            raise HyperFramesError(f"câu {line['sentence_id']}: layout {layout!r} cần style video dài ({', '.join(LONG_STYLES)})")
        depth_fg = None
        if layout == "depth":
            # 2.5D: tách chủ thể khỏi nền (Vision, cục bộ). Nền là clip chính, chủ
            # thể là clip thứ hai đè lên, hai lớp trôi lệch nhau tạo chiều sâu.
            # Không tách được (phong cảnh, chủ thể quá nhỏ/to) -> thẻ 3D (hoặc full nếu ảnh cine/pan).
            split = None
            if asset.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                import hf_depth  # noqa: PLC0415
                split = hf_depth.split_depth(asset)
            if split is None:
                layout = "full" if (cine or pan) else "card3d"
            else:
                sid0 = line["sentence_id"]
                bg_local = HF_ASSETS / f"{uid}_s{sid0}_bg.jpg"
                depth_fg = HF_ASSETS / f"{uid}_s{sid0}_fg.png"
                shutil.copy2(split[0], bg_local); shutil.copy2(split[1], depth_fg)
                asset = bg_local
                reveal = ""  # mặt nạ hé lộ chỉ áp một lớp -> hai lớp lệch nhau lúc hé
        if layout:
            reveal += f" media-layout-{layout}"
        # Kéo dài cửa sổ hiển thị thêm một nhịp để cú fade-out kịp chạy hết
        # trước khi khung tự gỡ thẻ -- nếu không, thẻ biến mất giữa lúc đang
        # mờ dần, và đó lại là một cú cắt cứng khác.
        last_idx = holds.get(li, li)
        last = lines[last_idx]
        m_end = last["end"]
        next_spec = (
            ((media or {}).get(str(lines[last_idx + 1]["sentence_id"])) or (media or {}).get(lines[last_idx + 1]["sentence_id"]))
            if last_idx + 1 < len(lines) else None
        )
        next_has_cine = isinstance(next_spec, dict) and (next_spec.get("cine") is not None or next_spec.get("pan") is not None)
        if last_idx + 1 < len(lines):
            m_end = max(m_end, lines[last_idx + 1]["start"])
        dur = round(max(1.0, m_end - line["start"]), 2)
        dur_media = round(dur + 0.6, 2)
        sid = line["sentence_id"]
        # Chỉ thẻ media trần. Mọi lớp trang trí (khung, nhãn, quầng, hạt) do
        # style dựng trong buildMediaScene -- mỗi style một kiểu, không phải
        # một khung chung dán vào đâu cũng được.
        diagram = " media-diagram" if (spec.get("kind") or "").lower() == "asset" else ""
        layers = parse_layers(spec.get("layers") or (pan.get("layers") if pan else None), where=f"câu {line['sentence_id']}")
        layers_attr = ' data-layers="1"' if layers else ""
        pan_attr = ' data-pan="1"' if pan else ""
        pan_cls = (" media-pan media-pan-v" if pan.get("axis") == "v" else " media-pan") if pan else ""
        if asset.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            fg_attr = f' data-fg="mediafg{sid}"' if depth_fg else ""
            cine_attr = ' data-cine="1"' if cine else ""
            media_tags.append(
                f'  <img id="mediaclip{sid}" class="media-clip{diagram}{tall}{reveal}{pan_cls} clip" src="assets/{asset.name}" '
                f'data-start="{line["start"]}" data-duration="{dur_media}" data-track-index="2"'
                f'{fg_attr}{cine_attr}{pan_attr}{layers_attr}{style_attr} alt="" />')
            if depth_fg:
                media_tags.append(
                    f'  <img id="mediafg{sid}" class="media-clip media-depth-fg{pan_cls} clip" src="assets/{depth_fg.name}" '
                    f'data-start="{line["start"]}" data-duration="{dur_media}" data-track-index="3"'
                    f'{cine_attr}{pan_attr}{layers_attr}{style_attr} alt="" />')
        else:
            media_tags.append(
                f'  <video id="mediaclip{sid}" class="media-clip{reveal} clip" '
                f'src="assets/{asset.name}" muted '
                f'data-start="{line["start"]}" data-duration="{dur_media}" data-track-index="2"'
                f'{style_attr}></video>')
        media_credits.append(credit)
        line["media"] = {"query": used_query, "reveal": (spec.get("reveal") or ""), "layout": layout}
        if asset.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            line["media"]["src"] = f"assets/{asset.name}"     # skin studio_long: nền / ô ảnh cho thẻ chữ khoá kế sau
        copy_motion(line["media"], spec, iw, ih)
        if cine is not None:
            line["media"]["cine"] = cine
            if iw and ih:
                line["media"]["w"] = int(iw)
                line["media"]["h"] = int(ih)
        if pan is not None:
            line["media"]["pan"] = pan
            if iw and ih:
                line["media"]["w"] = int(iw)
                line["media"]["h"] = int(ih)
        if layers:
            for l_idx, lyr in enumerate(layers):
                l_path = lyr.get("path")
                if l_path:
                    src_p = Path(l_path)
                    if not src_p.is_absolute():
                        src_p = (ROOT / src_p).resolve()
                    if src_p.exists():
                        dst_name = f"{uid}_s{sid}_layer{l_idx}{src_p.suffix}"
                        dst_p = HF_ASSETS / dst_name
                        if lyr.get("match_color") and asset and asset.exists():
                            try:
                                with Image.open(src_p) as lim, Image.open(asset) as bgim:
                                    matched_im = match_color(lim, bgim)
                                    matched_im.save(dst_p)
                            except Exception as e:
                                print(f"[CẢNH BÁO MATCH_COLOR] lỗi câu {sid} layer {l_idx}: {e}", file=sys.stderr)
                                shutil.copy2(src_p, dst_p)
                        else:
                            shutil.copy2(src_p, dst_p)
                        lyr["path"] = f"assets/{dst_name}"
                if lyr.get("path_frames"):
                    new_frames = []
                    for f_idx, frame_str in enumerate(lyr["path_frames"]):
                        f_p = Path(frame_str)
                        if not f_p.is_absolute():
                            f_p = (ROOT / f_p).resolve()
                        if f_p.exists():
                            dst_f_name = f"{uid}_s{sid}_layer{l_idx}_f{f_idx}{f_p.suffix}"
                            dst_f = HF_ASSETS / dst_f_name
                            shutil.copy2(f_p, dst_f)
                            new_frames.append(f"assets/{dst_f_name}")
                        else:
                            new_frames.append(frame_str)
                    lyr["path_frames"] = new_frames

                if lyr.get("follow") and pan is None and iw and ih:
                    pan = compute_follow_camera_pan(lyr, int(iw), int(ih))
                    line["media"]["pan"] = pan

            line["media"]["layers"] = layers
            if pan:
                pan["layers"] = layers
        if spec.get("label") is not False and (spec.get("label") or spec.get("tagged")):
            k = (spec.get("kind") or "video").lower()
            line["media"]["label"] = spec.get("label") if isinstance(spec.get("label"), str) else (
                "TƯ LIỆU" if k in ("commons", "museum", "openverse", "ext", "pdvideo") else "ẢNH MINH HOẠ" if k == "image" else "VIDEO MINH HOẠ")
            line["media"]["credit"] = (spec.get("credit") or _short_credit(credit, k))[:90]
        if last_idx > li or m_end > line["end"]:
            line["media_end"] = m_end
            for cont in lines[li + 1:last_idx + 1]:
                vspec = _visual_spec_of(lines, cont)
                if not (vspec and not is_overlay_visual(vspec)):
                    cont["media_cont"] = line["sentence_id"]
    duration = json.loads(manifest.read_text(encoding="utf-8"))["duration_s"]
    total_pan_dur = sum(
        (ln.get("media_end", ln["end"]) - ln["start"])
        for ln in lines
        if ln.get("media") and ln["media"].get("pan")
    )
    if duration > 0 and (total_pan_dur / duration) > PAN_VIDEO_PCT_WARN:
        pct = (total_pan_dur / duration) * 100.0
        print(f"[CẢNH BÁO PAN] Tổng thời lượng pan ({total_pan_dur:.1f}s / {duration:.1f}s = {pct:.1f}%) vượt mức khuyến nghị 25%", file=sys.stderr)

    typo_cfg = load_channel_typography(series, opts)
    variables = {
        "series": series,
        "typography": typo_cfg,
        "accent": STYLES[style]["accent"] or preset["accent"],   # studio_long: thay bằng accent của theme bên dưới
        "kicker": kicker if kicker is not None else (
            SERIES_LANES[series][lane] if lane else preset["kicker"]),
        "badge": badge,
        "footer": footer if footer is not None else preset["footer"],
        "duration": duration,
        "narration": "",
        "bgm": "",
        "lines": json.dumps(lines, ensure_ascii=False),
        "caps": "chunk" if (opts.get("subs") == "chunk" or opts.get("caps") == "chunk") else (opts.get("caps") or ""),
        "subs": opts.get("subs") or "",
        "loop": "1" if opts.get("loop") else "",
        "kc": "v2" if opts.get("kinetic") else "",
        "ts": "1" if opts.get("wordts") else "",   # plan "wordts": thẻ chữ đổi kiểu chữ/màu (longform.js TS_STYLES)
        "seg_off": float(opts.get("seg_off") or 0),
        "seg_total": float(opts.get("seg_total") or 0),
    }
    vars_path = HF_PROJECT / f".vars_{uid}.json"
    vars_path.write_text(json.dumps(variables, ensure_ascii=False), encoding="utf-8")

    # Thời lượng phải NƯỚNG vào HTML trước khi render: renderer đọc
    # data-duration của root TRƯỚC khi script trong trang chạy, nên gán bằng
    # JS không có tác dụng -- bản render thử đầu tiên dài đúng 30.0s mặc định
    # trong khi audio chỉ 28.52s (thừa 1.5s đen ở cuối).
    comp_src = (HF_PROJECT / comp_rel).read_text(encoding="utf-8")
    comp_src = comp_src.replace('data-duration="30"', f'data-duration="{duration}"', 1)
    if style == "studio_long":
        comp_src, variables["accent"] = studio_long_inject(comp_src, opts.get("theme"))
        vars_path.write_text(json.dumps(variables, ensure_ascii=False), encoding="utf-8")
    if opts.get("wordts"):   # phông cho kiểu chữ thẻ chữ (đều có bộ tiếng Việt) + Lora của thẻ trích kinh (trước đây không nạp)
        comp_src = comp_src.replace("</head>", WORDTS_FONTS + "\n</head>", 1)

    # Clip stock phải là thẻ TĨNH trong HTML: compiler chỉ đếm media khai báo
    # tĩnh, thẻ do script tạo ra bị bỏ qua không một lời cảnh báo (đúng cái
    # bẫy từng làm video ra câm).
    if media_tags:
        # Chèn TRƯỚC #stage: clip phải nằm DƯỚI lớp scene thì thiết kế riêng
        # của từng style (khung, nhãn, gạch accent, quầng tối) mới vẽ đè lên
        # được. Chèn sau stage thì clip che mất mọi overlay.
        comp_src = comp_src.replace('  <div id="stage">', "\n".join(media_tags) + '\n  <div id="stage">', 1)
    comp_path = comp_dir / f".render_{uid}.html"
    comp_path.write_text(comp_src, encoding="utf-8")

    output.parent.mkdir(parents=True, exist_ok=True)
    if os.environ.get("HF_QA"):
        # Soát trước khi render (hf_qa): runtime, bố cục, tương phản WCAG ở giữa
        # từng cảnh. HF_QA=strict -> có lỗi thì dừng, không render.
        import hf_qa  # noqa: PLC0415
        mids = [round((ln["start"] + ln["end"]) / 2, 2) for ln in lines
                if ln.get("visual") or ln.get("media") or ln.get("chapter_no") or ln.get("media_cont")]
        step = max(1, -(-len(mids) // 24))  # tối đa 24 mẫu: 40 mẫu mất ~2 phút 40
        report = hf_qa.run(comp_path, vars_path, mids[::step] or None)
        output.with_suffix(".qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        summary = hf_qa.summarize(report)
        print(summary, file=sys.stderr)
        if os.environ.get("HF_QA") == "strict" and "CÓ LỖI" in summary:
            raise HyperFramesError("QA trước render không đạt (HF_QA=strict):\n" + summary)
    silent_out = output.with_name(output.stem + "_silent.mp4")
    cmd = (f'export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh" >/dev/null 2>&1; '
           f'nvm use {NODE_MAJOR} >/dev/null 2>&1 || exit 97; ')
    browser_path = os.environ.get("HYPERFRAMES_BROWSER_PATH")
    if browser_path:
        cmd += f'export HYPERFRAMES_BROWSER_PATH={shlex.quote(browser_path)}; '
    cmd += (f'cd {HF_PROJECT.as_posix()!r} && npx --yes hyperframes@0.8.75 render . '
            f'-c {comp_path.relative_to(HF_PROJECT).as_posix()} --variables-file {vars_path.name} '
            f'--output {silent_out.resolve().as_posix()!r} '
            f'--quality {quality} --fps 30 --quiet')
    # 900 giây đủ cho short 30 giây; video dài 8 phút render mất cỡ 15-25 phút.
    # Giới hạn phải lớn theo độ dài, không cố định.
    timeout = render_timeout(duration, timeout)
    proc = subprocess.run(["/bin/bash", "-lc", cmd], capture_output=True, text=True, timeout=timeout)
    tail = ((proc.stdout or "") + (proc.stderr or ""))[-2500:]
    if proc.returncode == 97:
        raise HyperFramesError("Không tìm thấy Node 22 qua nvm (HyperFrames yêu cầu Node >= 22).")
    if proc.returncode != 0 or not silent_out.is_file():
        raise HyperFramesError(f"hyperframes render lỗi (exit {proc.returncode}):\n{tail}")
    # HF_KEEP_HTML=1 giữ lại HTML + variables đã bake để mở bằng trình duyệt
    # mà soi DOM thật -- đoán mò từ frame đã lừa mình vài lần rồi.
    if not os.environ.get("HF_KEEP_HTML"):
        vars_path.unlink(missing_ok=True)
        comp_path.unlink(missing_ok=True)

    silence = {int(x) for x in (opts.get("silence") or [])}
    quiet = [(float(ln["start"]) - .15, float(ln["end"]) + .35) for ln in lines if ln["sentence_id"] in silence]
    if opts.get("video_only"):
        # Render theo chương: chỉ hình; tiếng trộn MỘT lần cho cả video (hf_batch_render).
        silent_out.replace(output)
        return {"ok": True, "output": str(output), "duration_s": duration, "n_lines": len(lines), "style": style,
                "media_credits": [c for c in media_credits + visual_credits if c], "log_tail": tail}
    if opts.get("sound"):
        # Âm thanh 4 lớp (hf_foley): giọng + vang, không khí nơi chốn, nhạc nén theo giọng,
        # tiếng động chất liệu -- trộn sẵn một file rồi chỉ chuẩn hoá độ to (LOUD_TARGET) khi ghép.
        import hf_foley  # noqa: PLC0415
        mixed = output.with_name(output.stem + "_mix.wav")
        hf_foley.mix_long(lines, series, wav, bgm, float(duration), opts["sound"], silence, mixed,
                          seed=hashlib.sha1(output.stem.encode()).digest()[0])
        mux_audio(silent_out, mixed, output, duration=duration,
                  loudness=LOUD_TARGET["long" if lane == "long" else "short"])
        silent_out.unlink(missing_ok=True)
        mixed.unlink(missing_ok=True)
        return {"ok": True, "output": str(output), "duration_s": duration, "n_lines": len(lines),
                "style": style, "media_credits": [c for c in media_credits + visual_credits if c],
                "bgm": str(bgm) if bgm else "", "bgm_gain": 0, "sound": "foley-v1", "log_tail": tail}
    sfx_path = None
    if opts.get("sfx"):
        import hf_sfx  # noqa: PLC0415 -- Phase D: tiếng động bám mốc cảnh
        sfx_path = output.with_name(output.stem + "_sfx.wav")
        hf_sfx.build(lines, series, sfx_path, float(duration), silence=silence, seed=hashlib.sha1(output.stem.encode()).digest()[0])
    mux_audio(silent_out, wav, output, bgm=bgm, bgm_gain=bgm_gain, duration=duration, sfx=sfx_path,
              sfx_gain=float(opts.get("sfx_gain", 0.42)), quiet=quiet)
    silent_out.unlink(missing_ok=True)
    if sfx_path:
        sfx_path.unlink(missing_ok=True)
    return {"ok": True, "output": str(output), "duration_s": duration, "n_lines": len(lines),
            "style": style, "media_credits": [c for c in media_credits + visual_credits if c],
            "bgm": str(bgm) if bgm else "", "bgm_gain": bgm_gain, "log_tail": tail}


# Nhạc nền đặt THEO GIỌNG, không theo một hệ số cố định: giọng Sơn (FS) nhỏ
# hơn giọng Phật giáo ~3 LU, còn "Comfortable Mystery 4" to hơn "Meditation
# Impromptu 01" ~8 LU -- cùng hệ số 0.14 ra khoảng cách giọng/nhạc chỉ 12 dB
# ở L_fs_01 (người xem chê nhạc to), trong khi L_bud_01 là 19 dB.
BGM_GAP_DB = 21.0


def integrated_lufs(path: Path) -> float:
    """Loudness tích hợp (EBU R128, ffmpeg ebur128) của cả file."""
    res = subprocess.run(["ffmpeg", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True)
    found = re.findall(r"I:\s+(-?\d+(?:\.\d+)?) LUFS", res.stderr or "")
    if not found:
        raise HyperFramesError(f"không đo được loudness của {path}")
    return float(found[-1])


def relative_bgm_gain(narration: Path, bgm: Path, gap_db: float = BGM_GAP_DB) -> float:
    """Hệ số biên độ để nhạc nền nằm dưới giọng đọc đúng `gap_db` LU."""
    gain = 10 ** ((integrated_lufs(narration) - gap_db - integrated_lufs(bgm)) / 20)
    return round(min(gain, 1.0), 4)


# Độ to đích (ticket 68, đo 23/10). Loudnorm một lượt cũ (đích -14) chỉ ra Short FS -20,8 / BUD -17,9 LUFS:
# giọng TTS có hệ số đỉnh ~18 dB (I -24,6 mà đỉnh đã -6 dBTP), kéo lên đích thì đỉnh vượt 0 dB nên loudnorm rơi
# về chế độ động và dừng sớm. Nay: trộn -> đo -> tăng gain tới đích -> limiter đỉnh thật (lấy mẫu dư 4x) -> đo lại, bù.
# Short -14 (mốc phát của nền tảng, cạnh tranh trong feed); Long -16 (giọng kể dài, ít nén -- đề xuất (a) của 68).
LOUD_TARGET = {"short": -14.0, "long": -16.0}
LOUD_TP = -1.0
LOUD_TOL = 0.3


def _limit(src: Path, dst: Path, gain_db: float, true_peak: float = LOUD_TP) -> None:
    """Tăng gain rồi giới hạn đỉnh thật, có thể đặt trần thấp hơn cho encode lossy."""
    lim = 10 ** ((true_peak - .5) / 20)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af",
                    f"volume={gain_db:.2f}dB,aresample=192000,alimiter=limit={lim:.4f}:attack=3:release=60:level=disabled,"
                    "aresample=48000", "-c:a", "pcm_s24le", str(dst)], check=True)


def normalize_loudness(src: Path, dst: Path, target: float, *, true_peak: float = LOUD_TP) -> tuple[float, float]:
    """Ghi `dst` gần `target` LUFS, giới hạn đỉnh. Trả (LUFS đo được, gain đã dùng)."""
    try:
        source_lufs = integrated_lufs(src)
    except Exception as exc:
        print(f"Loudness warning: cannot measure input; preserving original mix ({exc})", file=sys.stderr)
        shutil.copyfile(src, dst)
        return float("nan"), 0.0
    if source_lufs < -50:
        print(f"Loudness warning: input is {source_lufs:.1f} LUFS (< -50); preserving original mix without gain", file=sys.stderr)
        shutil.copyfile(src, dst)
        return source_lufs, 0.0
    gain = target - source_lufs
    _limit(src, dst, gain, true_peak)
    got = integrated_lufs(dst)
    # Limiter ăn bớt năng lượng, càng nhiều khi đỉnh càng nhọn: +4 dB gain có khi chỉ ra +1,4 LUFS. Bù theo cát tuyến
    # (độ dốc từ hai lần đo gần nhất), tối đa 4 lần.
    g0, l0 = gain, got
    for k in range(4):
        if abs(got - target) <= LOUD_TOL:
            break
        slope = 1.0 if k == 0 else max(.15, (got - l0) / (gain - g0)) if gain != g0 else 1.0
        g0, l0 = gain, got
        gain += min(12.0, (target - got) / slope)
        _limit(src, dst, gain, true_peak)
        got = integrated_lufs(dst)
    if abs(got - target) > 1.0:
        print(f"Loudness warning: normalized output is {got:.1f} LUFS, {abs(got-target):.1f} LU from target {target:.1f}", file=sys.stderr)
    return got, gain


def mux_audio(video: Path, narration: Path, output: Path, *, bgm: Path | None = None,
              bgm_gain: float = 0.16, duration: float = 0.0, sfx: Path | None = None,
              sfx_gain: float = 0.42, quiet: list[tuple[float, float]] | None = None,
              loudness: float = LOUD_TARGET["short"]) -> None:
    """Ghép tiếng vào video câm, độ to `loudness` LUFS, đỉnh thật <= -1 dBTP.
    Làm ở đây thay vì để HyperFrames xử lý audio vì compiler của nó chỉ đếm media KHAI BÁO TĨNH
    trong HTML -- thẻ <audio> do script dựng ra bị bỏ qua (audioCount:0), video ra câm mà không báo lỗi."""
    fade_at = max(0.0, float(duration) - 1.4)
    inputs = ["-i", str(narration)]
    if bgm and sfx:
        # Phase D: giọng + nhạc nền (tắt hẳn ở câu hỏi lặng) + tiếng động bám cảnh.
        mute = "".join(f",volume=0:enable='between(t,{a:.2f},{b:.2f})'" for a, b in (quiet or []))
        inputs += ["-stream_loop", "-1", "-i", str(bgm), "-i", str(sfx)]
        flt = (f"[1:a]volume={bgm_gain}{mute},afade=t=out:st={fade_at:.2f}:d=1.4[b];"
               f"[2:a]volume={sfx_gain}[s];"
               f"[0:a][b][s]amix=inputs=3:duration=first:dropout_transition=0:normalize=0[m]")
    elif bgm:
        inputs += ["-stream_loop", "-1", "-i", str(bgm)]
        flt = (f"[1:a]volume={bgm_gain},afade=t=out:st={fade_at:.2f}:d=1.4[b];"
               f"[0:a][b]amix=inputs=2:duration=first:dropout_transition=0[m]")
    else:
        flt = "[0:a]anull[m]"
    mixed, final = output.with_name(output.stem + "._mix.wav"), output.with_name(output.stem + "._loud.wav")
    try:
        res = subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", flt, "-map", "[m]",
                              "-c:a", "pcm_f32le", "-ar", "48000", "-ac", "2", str(mixed)], capture_output=True, text=True)
        if res.returncode != 0:
            raise HyperFramesError(f"ffmpeg trộn tiếng lỗi: {(res.stderr or '')[-800:]}")
        normalize_loudness(mixed, final, loudness)
        res = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(final),
                              "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                              "-ar", "48000", "-ac", "2", "-shortest", str(output)], capture_output=True, text=True)
    finally:
        mixed.unlink(missing_ok=True)
        final.unlink(missing_ok=True)
    if res.returncode != 0 or not output.is_file():
        raise HyperFramesError(f"ffmpeg mux audio lỗi: {(res.stderr or '')[-800:]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True, help="Kịch bản gốc, mỗi câu 1 dòng, **cụm quan trọng** đánh dấu bằng **")
    ap.add_argument("--wav", required=True, help="File audio TTS (phải có .json manifest cùng tên bên cạnh)")
    ap.add_argument("--series", required=True, choices=sorted(SERIES_PRESETS))
    ap.add_argument("--output", required=True)
    ap.add_argument("--badge", default="")
    ap.add_argument("--kicker", default=None)
    ap.add_argument("--lane", default=None, help="Dòng nội dung trong series (SERIES_LANES) -- quyết định chữ trên cùng")
    ap.add_argument("--footer", default=None)
    ap.add_argument("--bgm", default=None)
    ap.add_argument("--bgm-gain", type=float, default=0.16)
    ap.add_argument("--quality", default="looks", choices=["draft", "looks", "delivery"])
    ap.add_argument("--style", default="clean", choices=sorted(STYLES), help="Cái nhìn của ngày (mỗi ngày 1 dạng)")
    ap.add_argument("--figures", default=None, help='File JSON {"<số thứ tự câu>": <semantic figure>} theo hf_figure_schema.json')
    ap.add_argument("--visuals", default=None, help='File JSON {"<số thứ tự câu>": {"type": "wheel", ...}} -- sơ đồ video dài')
    ap.add_argument("--media", default=None, help='File JSON {"<số thứ tự câu>": {"query": "..."}} -- clip stock Pexels')
    ap.add_argument("--opts", default=None, help='File JSON {"caps": "chunk", "loop": true, "silence": [5], "sfx": true} -- Phase D')
    ap.add_argument("--figure-labels", default=None, help='File JSON {"<số thứ tự câu>": {left,right,note}} -- chữ người viết đặt tay (ADR-0002)')
    args = ap.parse_args()
    try:
        result = render(Path(args.script), Path(args.wav), args.series, Path(args.output),
                        badge=args.badge, kicker=args.kicker, lane=args.lane, footer=args.footer,
                        bgm=Path(args.bgm) if args.bgm else None, bgm_gain=args.bgm_gain,
                        quality=args.quality, style=args.style,
                        figures=json.loads(Path(args.figures).read_text(encoding="utf-8")) if args.figures else None,
                        figure_labels=json.loads(Path(args.figure_labels).read_text(encoding="utf-8")) if args.figure_labels else None,
                        media=json.loads(Path(args.media).read_text(encoding="utf-8")) if args.media else None,
                        visuals=json.loads(Path(args.visuals).read_text(encoding="utf-8")) if args.visuals else None,
                        opts=json.loads(Path(args.opts).read_text(encoding="utf-8")) if args.opts else None)
    except HyperFramesError as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({k: v for k, v in result.items() if k != "log_tail"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
