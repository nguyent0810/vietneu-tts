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
import json
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


def resolve_media(media: dict, sentence_id: int, stem: str) -> tuple[Path, str]:
    """Lấy clip stock cho 1 câu. Trả (đường dẫn trong project, query đã lọc).

    Dùng lại `asset_generation.get_or_fetch_stock_video`: đã cache theo hash
    query, đã gọi `asset_safety.assert_asset_safe_for_assembly` mỗi lần trả
    từ cache -- một clip bị gắn cờ không thể lặng lẽ quay lại."""
    import asset_generation  # noqa: PLC0415 -- kéo theo cả stack nặng, chỉ nạp khi cần

    raw = (media or {}).get("query", "").strip()
    if not raw:
        raise HyperFramesError(f"câu {sentence_id}: media thiếu 'query'")
    query = sanitize_query(raw)
    clip = asset_generation.get_or_fetch_stock_video(query)
    if clip is None:
        raise HyperFramesError(f"câu {sentence_id}: không lấy được clip cho {query!r}")
    HF_ASSETS.mkdir(parents=True, exist_ok=True)
    local = HF_ASSETS / f"{stem}_s{sentence_id}{clip.suffix}"
    shutil.copy2(clip, local)
    return local, query


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


def _words_with_timing(line_text: str, start: float, end: float) -> list[dict]:
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
                figure_labels: dict | None = None) -> list[dict]:
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
    lines, prev_key = [], None
    for idx, (raw, seg) in enumerate(zip(raw_lines, segments), start=1):
        parts = _key_parts(raw, avoid=prev_key)
        prev_key = parts[0]["t"]
        lines.append({
            "sentence_id": idx,
            "start": round(float(seg["start"]), 3),
            "end": round(float(seg["end"]), 3),
            "key_parts": parts,
            "words": _words_with_timing(raw, float(seg["start"]), float(seg["end"])),
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


def render(script: Path, wav: Path, series: str, output: Path, *, badge: str = "",
           kicker: str | None = None, footer: str | None = None, bgm: Path | None = None,
           bgm_gain: float = 0.16, quality: str = "looks", style: str = "clean",
           figures: dict | None = None, figure_labels: dict | None = None,
           media: dict | None = None, timeout: int = DEFAULT_TIMEOUT_S) -> dict:
    if series not in SERIES_PRESETS:
        raise HyperFramesError(f"series lạ: {series!r} (có: {', '.join(SERIES_PRESETS)})")
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
    lines = build_lines(script, manifest, figures, figure_labels)

    media_tags: list[str] = []
    for line in lines:
        spec = (media or {}).get(str(line["sentence_id"])) or (media or {}).get(line["sentence_id"])
        if not spec:
            continue
        if line.get("figure") and line["figure"].get("type") != "none":
            raise HyperFramesError(
                f'câu {line["sentence_id"]}: có cả figure lẫn clip -- chọn một. '
                f'Hai thứ cùng chiếm vùng giữa khung.')
        clip, used_query = resolve_media(spec, line["sentence_id"], output.stem)
        dur = round(max(1.0, line["end"] - line["start"]), 2)
        # Chỉ thẻ <video>. Mọi lớp trang trí (khung, nhãn, quầng, hạt) do
        # style dựng trong buildMediaScene -- mỗi style một kiểu, không phải
        # một khung chung dán vào đâu cũng được.
        media_tags.append(
            f'  <video id="mediaclip{line["sentence_id"]}" class="media-clip clip" '
            f'src="assets/{clip.name}" muted '
            f'data-start="{line["start"]}" data-duration="{dur}" data-track-index="2"></video>')
        line["media"] = {"query": used_query}
    duration = json.loads(manifest.read_text(encoding="utf-8"))["duration_s"]

    variables = {
        "series": series,
        "accent": STYLES[style]["accent"] or preset["accent"],
        "kicker": kicker if kicker is not None else preset["kicker"],
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
    silent_out = output.with_name(output.stem + "_silent.mp4")
    cmd = (f'export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh" >/dev/null 2>&1; '
           f'nvm use {NODE_MAJOR} >/dev/null 2>&1 || exit 97; '
           f'cd {HF_PROJECT.as_posix()!r} && npx --yes hyperframes@0.8.75 render . '
           f'-c {comp_path.relative_to(HF_PROJECT).as_posix()} --variables-file {vars_path.name} '
           f'--output {silent_out.resolve().as_posix()!r} '
           f'--quality {quality} --fps 30 --quiet')
    proc = subprocess.run(["/bin/bash", "-lc", cmd], capture_output=True, text=True, timeout=timeout)
    tail = ((proc.stdout or "") + (proc.stderr or ""))[-2500:]
    if proc.returncode == 97:
        raise HyperFramesError("Không tìm thấy Node 22 qua nvm (HyperFrames yêu cầu Node >= 22).")
    if proc.returncode != 0 or not silent_out.is_file():
        raise HyperFramesError(f"hyperframes render lỗi (exit {proc.returncode}):\n{tail}")
    vars_path.unlink(missing_ok=True)
    comp_path.unlink(missing_ok=True)

    mux_audio(silent_out, wav, output, bgm=bgm, bgm_gain=bgm_gain, duration=duration)
    silent_out.unlink(missing_ok=True)
    return {"ok": True, "output": str(output), "duration_s": duration, "n_lines": len(lines),
            "style": style, "log_tail": tail}


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
    ap.add_argument("--footer", default=None)
    ap.add_argument("--bgm", default=None)
    ap.add_argument("--bgm-gain", type=float, default=0.16)
    ap.add_argument("--quality", default="looks", choices=["draft", "looks", "delivery"])
    ap.add_argument("--style", default="clean", choices=sorted(STYLES), help="Cái nhìn của ngày (mỗi ngày 1 dạng)")
    ap.add_argument("--figures", default=None, help='File JSON {"<số thứ tự câu>": <semantic figure>} theo hf_figure_schema.json')
    ap.add_argument("--media", default=None, help='File JSON {"<số thứ tự câu>": {"query": "..."}} -- clip stock Pexels')
    ap.add_argument("--figure-labels", default=None, help='File JSON {"<số thứ tự câu>": {left,right,note}} -- chữ người viết đặt tay (ADR-0002)')
    args = ap.parse_args()
    try:
        result = render(Path(args.script), Path(args.wav), args.series, Path(args.output),
                        badge=args.badge, kicker=args.kicker, footer=args.footer,
                        bgm=Path(args.bgm) if args.bgm else None, bgm_gain=args.bgm_gain,
                        quality=args.quality, style=args.style,
                        figures=json.loads(Path(args.figures).read_text(encoding="utf-8")) if args.figures else None,
                        figure_labels=json.loads(Path(args.figure_labels).read_text(encoding="utf-8")) if args.figure_labels else None,
                        media=json.loads(Path(args.media).read_text(encoding="utf-8")) if args.media else None)
    except HyperFramesError as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({k: v for k, v in result.items() if k != "log_tail"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
