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
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
HF_PROJECT = PROJECT_ROOT / "hyperframes_short"
HF_ASSETS = HF_PROJECT / "assets"
NODE_MAJOR = "22"
DEFAULT_TIMEOUT_S = 900

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
PAPER_STYLES = ("inkwash", "inkwash_wide", "inkwash_long")

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
                "word", "illus", "endcard")
MEDIA_LAYOUTS = ("full", "card3d", "split", "split_r", "polaroid", "pinned", "depth")
# "frame" = ô mặc định của style (la bàn / khung giấy). Video động hợp tràn khung.
LAYOUT_POOL = ("frame", "full", "card3d", "split", "split_r", "polaroid", "pinned", "depth")
VIDEO_LAYOUT_POOL = ("full", "card3d", "frame")
LONG_STYLES = ("laban_long", "inkwash_long")
# Short dọc (style BUD nạp longform.js + shortform.css) chỉ dùng được các cảnh đã
# đặt lại cho khung 1080x1920; sơ đồ rộng (vòng, bản đồ, dòng thời gian) thì không.
SHORT_VISUAL_STYLES = ("silence", "oilpaint", "lightfield", "inkwash", "dustbeam")
SHORT_VISUAL_TYPES = ("word", "quote", "illus", "stat", "list")

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
}


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
        if found is None:
            raise HyperFramesError(f"câu {sentence_id}: không tìm được ảnh cho {query!r}")
        local = HF_ASSETS / f"{stem}_s{sentence_id}.jpg"
        _shrink_image(found, local)
        return local, query, stock_image.credit_line(found), grade

    import asset_generation  # noqa: PLC0415 -- kéo theo cả stack nặng, chỉ nạp khi cần
    clip = asset_generation.get_or_fetch_stock_video(query)
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


def apply_visuals(lines: list[dict], visuals: dict, media: dict) -> None:
    """Gắn sơ đồ (plan `visuals`) vào câu gốc và đánh dấu các câu nó còn chiếm
    màn hình (`until`, mặc định = câu của bước cuối). Bridge không hiểu nội dung
    sơ đồ -- chỉ kiểm loại, khoảng câu, và không cho sơ đồ đè lên ảnh/figure."""
    n = len(lines)
    for key, spec in visuals.items():
        sid = int(key)
        if not 1 <= sid <= n:
            raise HyperFramesError(f"sơ đồ ở câu {sid}: ngoài kịch bản ({n} câu)")
        if (spec.get("type") or "") not in VISUAL_TYPES:
            raise HyperFramesError(f"câu {sid}: loại sơ đồ lạ {spec.get('type')!r} (có: {', '.join(VISUAL_TYPES)})")
        ats = [int(x["at"]) for x in (spec.get("steps") or spec.get("items") or spec.get("pins") or []) if x.get("at")]
        until = int(spec.get("until") or max([sid] + ats))
        if any(a < sid or a > until for a in ats) or until > n:
            raise HyperFramesError(f"câu {sid}: bước của sơ đồ phải nằm trong câu {sid}..{until}")
        for k in range(sid, until + 1):
            ln = lines[k - 1]
            if str(k) in media or k in media:
                raise HyperFramesError(f"câu {k}: vừa có ảnh vừa nằm trong sơ đồ của câu {sid}")
            if (ln.get("figure") or {}).get("type", "none") != "none":
                raise HyperFramesError(f"câu {k}: vừa có figure vừa nằm trong sơ đồ của câu {sid}")
            if k > sid and (ln.get("visual") or ln.get("visual_cont")):
                raise HyperFramesError(f"câu {k}: hai sơ đồ chồng nhau")
        lines[sid - 1]["visual"] = spec
        for k in range(sid + 1, until + 1):
            lines[k - 1]["visual_cont"] = sid


def media_holds(lines: list[dict], media_ids: set[int], max_span: float = HOLD_MAX_S) -> dict[int, int]:
    """{chỉ số dòng có ảnh: chỉ số dòng cuối cùng ảnh còn hiện} (0-based)."""
    holds = {}
    for i, ln in enumerate(lines):
        if ln["sentence_id"] not in media_ids:
            continue
        k = i
        while k + 1 < len(lines):
            nxt = lines[k + 1]
            if (nxt["sentence_id"] in media_ids or nxt.get("heading") or nxt.get("visual")
                    or nxt.get("visual_cont")
                    or (nxt.get("figure") or {}).get("type", "none") != "none"
                    or nxt["end"] - ln["start"] > max_span):
                break
            k += 1
        holds[i] = k
    return holds


def render(script: Path, wav: Path, series: str, output: Path, *, badge: str = "",
           kicker: str | None = None, lane: str | None = None, footer: str | None = None, bgm: Path | None = None,
           bgm_gain: float = 0.16, quality: str = "looks", style: str = "clean",
           figures: dict | None = None, figure_labels: dict | None = None,
           media: dict | None = None, timeout: int = DEFAULT_TIMEOUT_S,
           hold_media: bool | None = None, visuals: dict | None = None) -> dict:
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
    if visuals and style not in LONG_STYLES:
        if style not in SHORT_VISUAL_STYLES:
            raise HyperFramesError(f"style {style!r} không nạp kho cảnh (có: {', '.join(LONG_STYLES + SHORT_VISUAL_STYLES)})")
        bad = sorted({v.get("type") for v in visuals.values()} - set(SHORT_VISUAL_TYPES))
        if bad:
            raise HyperFramesError(f"short dọc không dùng được cảnh {bad} (chỉ: {', '.join(SHORT_VISUAL_TYPES)})")
    apply_visuals(lines, visuals or {}, media or {})
    if lane == "long":
        chap = 0
        for ln in lines:
            if ln.get("heading"):
                chap += 1
                ln["chapter_no"] = chap
    if hold_media is None:
        hold_media = lane == "long"
    holds = media_holds(lines, {int(k) for k in (media or {})}) if hold_media else {}
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
            spec, line["sentence_id"], output.stem, SERIES_DOMAIN.get(series, "CL"),
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
        if layout and layout not in MEDIA_LAYOUTS:
            raise HyperFramesError(f"câu {line['sentence_id']}: layout lạ {layout!r} (có: {', '.join(MEDIA_LAYOUTS)})")
        if layout and style not in LONG_STYLES:
            raise HyperFramesError(f"câu {line['sentence_id']}: layout {layout!r} cần style video dài ({', '.join(LONG_STYLES)})")
        depth_fg = None
        if layout == "depth":
            # 2.5D: tách chủ thể khỏi nền (Vision, cục bộ). Nền là clip chính, chủ
            # thể là clip thứ hai đè lên, hai lớp trôi lệch nhau tạo chiều sâu.
            # Không tách được (phong cảnh, chủ thể quá nhỏ/to) -> thẻ 3D.
            split = None
            if asset.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                import hf_depth  # noqa: PLC0415
                split = hf_depth.split_depth(asset)
            if split is None:
                layout = "card3d"
            else:
                sid0 = line["sentence_id"]
                bg_local = HF_ASSETS / f"{output.stem}_s{sid0}_bg.jpg"
                depth_fg = HF_ASSETS / f"{output.stem}_s{sid0}_fg.png"
                shutil.copy2(split[0], bg_local); shutil.copy2(split[1], depth_fg)
                asset = bg_local
                reveal = ""  # mặt nạ hé lộ chỉ áp một lớp -> hai lớp lệch nhau lúc hé
        if layout:
            reveal += f" media-layout-{layout}"
        # Kéo dài cửa sổ hiển thị thêm một nhịp để cú fade-out kịp chạy hết
        # trước khi khung tự gỡ thẻ -- nếu không, thẻ biến mất giữa lúc đang
        # mờ dần, và đó lại là một cú cắt cứng khác.
        last = lines[holds.get(li, li)]
        dur = round(max(1.0, last["end"] - line["start"]), 2)
        dur_media = round(dur + 0.6, 2)
        sid = line["sentence_id"]
        # Chỉ thẻ media trần. Mọi lớp trang trí (khung, nhãn, quầng, hạt) do
        # style dựng trong buildMediaScene -- mỗi style một kiểu, không phải
        # một khung chung dán vào đâu cũng được.
        diagram = " media-diagram" if (spec.get("kind") or "").lower() == "asset" else ""
        if asset.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            fg_attr = f' data-fg="mediafg{sid}"' if depth_fg else ""
            media_tags.append(
                f'  <img id="mediaclip{sid}" class="media-clip{diagram}{reveal} clip" src="assets/{asset.name}" '
                f'data-start="{line["start"]}" data-duration="{dur_media}" data-track-index="2"'
                f'{fg_attr}{style_attr} alt="" />')
            if depth_fg:
                media_tags.append(
                    f'  <img id="mediafg{sid}" class="media-clip media-depth-fg clip" src="assets/{depth_fg.name}" '
                    f'data-start="{line["start"]}" data-duration="{dur_media}" data-track-index="3"'
                    f'{style_attr} alt="" />')
        else:
            media_tags.append(
                f'  <video id="mediaclip{sid}" class="media-clip{reveal} clip" '
                f'src="assets/{asset.name}" muted '
                f'data-start="{line["start"]}" data-duration="{dur_media}" data-track-index="2"'
                f'{style_attr}></video>')
        media_credits.append(credit)
        line["media"] = {"query": used_query, "reveal": (spec.get("reveal") or ""), "layout": layout}
        if holds.get(li, li) > li:
            line["media_end"] = last["end"]
            for cont in lines[li + 1:holds[li] + 1]:
                cont["media_cont"] = line["sentence_id"]
    duration = json.loads(manifest.read_text(encoding="utf-8"))["duration_s"]

    variables = {
        "series": series,
        "accent": STYLES[style]["accent"] or preset["accent"],
        "kicker": kicker if kicker is not None else (
            SERIES_LANES[series][lane] if lane else preset["kicker"]),
        "badge": badge,
        "footer": footer if footer is not None else preset["footer"],
        "duration": duration,
        "narration": "",
        "bgm": "",
        "lines": json.dumps(lines, ensure_ascii=False),
    }
    vars_path = HF_PROJECT / f".vars_{output.stem}.json"
    vars_path.write_text(json.dumps(variables, ensure_ascii=False), encoding="utf-8")

    # Thời lượng phải NƯỚNG vào HTML trước khi render: renderer đọc
    # data-duration của root TRƯỚC khi script trong trang chạy, nên gán bằng
    # JS không có tác dụng -- bản render thử đầu tiên dài đúng 30.0s mặc định
    # trong khi audio chỉ 28.52s (thừa 1.5s đen ở cuối).
    comp_src = (HF_PROJECT / comp_rel).read_text(encoding="utf-8")
    comp_src = comp_src.replace('data-duration="30"', f'data-duration="{duration}"', 1)

    # Clip stock phải là thẻ TĨNH trong HTML: compiler chỉ đếm media khai báo
    # tĩnh, thẻ do script tạo ra bị bỏ qua không một lời cảnh báo (đúng cái
    # bẫy từng làm video ra câm).
    if media_tags:
        # Chèn TRƯỚC #stage: clip phải nằm DƯỚI lớp scene thì thiết kế riêng
        # của từng style (khung, nhãn, gạch accent, quầng tối) mới vẽ đè lên
        # được. Chèn sau stage thì clip che mất mọi overlay.
        comp_src = comp_src.replace('  <div id="stage">', "\n".join(media_tags) + '\n  <div id="stage">', 1)
    comp_path = comp_dir / f".render_{output.stem}.html"
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
           f'nvm use {NODE_MAJOR} >/dev/null 2>&1 || exit 97; '
           f'cd {HF_PROJECT.as_posix()!r} && npx --yes hyperframes@0.8.75 render . '
           f'-c {comp_path.relative_to(HF_PROJECT).as_posix()} --variables-file {vars_path.name} '
           f'--output {silent_out.resolve().as_posix()!r} '
           f'--quality {quality} --fps 30 --quiet')
    # 900 giây đủ cho short 30 giây; video dài 8 phút render mất cỡ 15-25 phút.
    # Giới hạn phải lớn theo độ dài, không cố định.
    timeout = max(timeout, int(duration * 6) + 600)
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

    mux_audio(silent_out, wav, output, bgm=bgm, bgm_gain=bgm_gain, duration=duration)
    silent_out.unlink(missing_ok=True)
    return {"ok": True, "output": str(output), "duration_s": duration, "n_lines": len(lines),
            "style": style, "media_credits": [c for c in media_credits if c],
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


def mux_audio(video: Path, narration: Path, output: Path, *, bgm: Path | None = None,
              bgm_gain: float = 0.16, duration: float = 0.0) -> None:
    """Ghép tiếng vào video câm + chuẩn hoá về -14 LUFS (mốc YouTube tự
    normalize tới). Làm ở đây thay vì để HyperFrames xử lý audio vì compiler
    của nó chỉ đếm media KHAI BÁO TĨNH trong HTML -- thẻ <audio> do script
    dựng ra bị bỏ qua (audioCount:0), video ra câm mà không báo lỗi."""
    if bgm:
        fade_at = max(0.0, float(duration) - 1.4)
        flt = (f"[2:a]volume={bgm_gain},afade=t=out:st={fade_at:.2f}:d=1.4[b];"
               f"[1:a][b]amix=inputs=2:duration=first:dropout_transition=0,"
               f"loudnorm=I=-14:TP=-1.5:LRA=11[a]")
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(narration),
               "-stream_loop", "-1", "-i", str(bgm), "-filter_complex", flt,
               "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
               "-ar", "48000", "-ac", "2", "-shortest", str(output)]
    else:
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(narration),
               "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
               "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
               "-ar", "48000", "-ac", "2", "-shortest", str(output)]
    res = subprocess.run(cmd, capture_output=True, text=True)
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
                        visuals=json.loads(Path(args.visuals).read_text(encoding="utf-8")) if args.visuals else None)
    except HyperFramesError as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({k: v for k, v in result.items() if k != "log_tail"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
