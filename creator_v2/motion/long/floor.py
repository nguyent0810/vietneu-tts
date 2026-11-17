"""Sàn sản xuất của video dài: một Long mới không được kém các Long đã chứng minh.

Ngày 11/10/2026 có 4 Long (escobar, capone, bulger, namcam) được dựng cách nhau ~25 phút: kịch bản
1.300–2.100 âm tiết (7–11 phút), 0 ảnh, 0 b-roll, 0 bản đồ, 94% cảnh là chữ trên nền trống — mỗi cảnh
là 4 từ đầu câu do scenes_from tự cắt. Cổng `craft` không chặn vì nó chỉ soi từng câu, không soi tư liệu.

Sàn này đo đúng những thứ đó. Ngưỡng lấy từ 6 Long đã đăng (yakuza, mafia, shanghai, ripper, kowloon,
golden) — cả 6 đều qua, nên sàn áp cho MỌI topic, không cần cờ bật/tắt:

                      thấp nhất trong 6 Long     sàn
  âm tiết kịch bản            5.610             5.000   (≈ 23 phút ở 215 âm tiết/phút)
  số chương                      12                10
  số loại cảnh                   19                14
  ảnh khác nhau dùng             49                40
  cảnh có b-roll                 35                30
  tỷ lệ kinetic (cao nhất)      34%            ≤ 38%
  chữ trên nền trống (cao nhất) 10%            ≤ 12%

`build_long.py html` in cảnh báo; `render` (bản thật), `final` và `publish_long.py` TỪ CHỐI.

Đây chỉ là sàn nội dung. Không viết lại cổng kỹ thuật đã có:
- `build_long.py` tạo TTS/timing, kiểm asset và `html_lint`, rồi kiểm `craft`;
- `scripts/long_gate.py` kiểm timing, nhịp/cảnh, lặp clip/ảnh, cấu trúc cảnh,
  dữ kiện và nguồn công khai.
Các cổng đó vẫn chạy cho mọi kênh. Riêng MIM/CK cần `timing.json` để đo thời
lượng chữ nền trống; vì vậy `problems(..., topic=...)` có thể đọc dữ liệu đo.

076: Long mới theo danh sách legacy #275 thay ngưỡng kinetic/nền trống theo
số cảnh bằng ngân sách visual_mix theo giây (12% cảnh báo, 15% lỗi), thêm
lặp ảnh 4/6 và mật độ ảnh cảnh báo. Các ngưỡng chữ cũ chỉ còn cho legacy.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

# Same repo-root import convention as long_ambience._load_amb; append so the
# creator_v2 module names keep their existing precedence.
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.append(str(_REPO_ROOT))
from tools import visual_mix

MIN_SYL = 5000
MIN_CHAPTERS = 10
MIN_TYPES = 14
MIN_IMGS = 40
MIN_VID_SCENES = 30
MAX_KINETIC = 0.38             # legacy only; new topics use visual_mix seconds
MAX_NAKED = 0.12
MAX_PANO = 6                   # cảnh pano (ảnh rộng lia theo lời) tối đa mỗi Long
MAX_PANO_SHARE = 0.25          # và tối đa 25% thời lượng
MIN_FINAL_MIN = 20.0          # final.mp4 ngắn hơn thế này thì không đăng như một Long
# MIM/CK thử Long 8–15 phút: đo theo giây thật để chặn slide chữ, nhưng không
# ép các ngưỡng 20+ phút/tư liệu của CL vốn được rút từ sáu Long hồ sơ đã đăng.
MIM_CK_MAX_EMPTY_BACKGROUND_PERCENT = 22.0
MIM_CK_MAX_CONSECUTIVE_TEXT_SECONDS = 17.0
_TEXT_ONLY = {"kinetic", "slam", "date", "counter", "question", "quote"}
_STYLE_TYPES = {"woodcut", "papercut", "oneline", "film16", "blueprint", "pencil"}
ROOT = Path(__file__).resolve().parents[2]


def visual_mix_is_new(topic: str | None, root: Path | None = None) -> bool:
    """Mirror build_long.is_legacy_topic (#275), including missing-data fallback."""
    root = root or ROOT
    legacy = root / "data" / "long" / "_legacy_topics.json"
    if not topic or not legacy.exists() or not (root / "data" / "long" / topic / "spec.json").exists():
        return False
    return topic not in json.loads(legacy.read_text(encoding="utf-8"))


def _norm_word(word):
    return re.sub(r"[^\w]", "", unicodedata.normalize("NFC", str(word).lower()))


def _mix_anchor(anchor, segments) -> float:
    """Same int/float/word anchor contract as build.Anchors; no engine import.

    Without aligned words, interpolate within the spoken segment and label the
    report as estimated. Never interpret a float (absolute seconds) as a line.
    """
    if isinstance(anchor, bool):
        raise ValueError("visual_mix: boolean anchor")
    if isinstance(anchor, float):
        return anchor
    if isinstance(anchor, int):
        return float(segments[anchor]["start"])
    if not isinstance(anchor, list) or not anchor:
        raise ValueError(f"visual_mix: invalid anchor {anchor!r}")
    index, word = anchor[0], anchor[1] if len(anchor) > 1 else None
    occurrence = anchor[2] if len(anchor) > 2 and anchor[2] is not None else 0
    offset = anchor[3] if len(anchor) > 3 and anchor[3] is not None else 0.0
    segment = segments[index]
    if word is None:
        return float(segment["start"]) + offset
    tokens = segment.get("words")
    if not tokens:
        words = segment.get("text", "").split()
        span = segment["end"] - segment["start"]
        tokens = [{"w": w, "t": segment["start"] + span * i / len(words)} for i, w in enumerate(words)]
    hits = [token for token in tokens if _norm_word(token["w"]) == _norm_word(word)]
    if occurrence >= len(hits):
        raise ValueError(f"visual_mix: câu {index} không có chữ {word!r} lần {occurrence}")
    return float(hits[occurrence]["t"]) + offset


def visual_mix_scenes(chapters, *, timings=None, spec=None) -> list[dict]:
    """Read source chNN scenes; use TTS timings, else estimate at 215 tiếng/min.

    Image aliases resolve through spec.imgs, so aliases/crops of one file share
    a reuse identity. Extra split/background images use the shared images field.
    """
    timings, spec = timings or {}, spec or {}
    image_map = spec.get("imgs") or {}
    scenes, offset = [], 0.0
    for name, chapter in chapters:
        timing = timings.get(name)
        if timing is None:
            segments, t = [], 0.0
            for line in chapter.get("lines", []):
                text = _text(line)
                duration = len(text.split()) * 60 / 215
                segments.append({"start": t, "end": t + duration, "text": text})
                pause = (line["p"] if isinstance(line, dict) and "p" in line else
                         0.6 if text.rstrip().endswith("?") else
                         0.45 if text.rstrip().endswith("…") else 0.32)
                t += duration + pause
            timing = {"segments": segments, "duration": t + 0.9}  # build_long.TAIL
        segments = timing.get("segments") or []
        duration = float(timing.get("duration") or (segments[-1]["end"] if segments else 0))
        source = chapter.get("scenes") or []
        starts = [0.0 if i == 0 else _mix_anchor(s["at"], segments) for i, s in enumerate(source)]
        for i, scene in enumerate(source):
            kind = scene.get("type", "unknown")
            refs = []
            for key in _imgs(scene):
                ref = image_map.get(key, key)
                if isinstance(ref, dict):
                    ref = ref.get("path") or ref.get("file") or ref.get("ref") or ref.get("url")
                if ref:
                    refs.append(str(ref))
            # Kinetic/slam/quote/question remain full-screen text treatments
            # with decorative media beds. Only explicit overlays, or
            # date/counter with media, are exempt from the text budget.
            video = scene.get("vid") or (kind == "broll" and scene.get("pd"))
            if (scene.get("overlay") or kind in {"date", "counter"}) and (refs or video):
                kind = "broll" if video else "photo"
            scenes.append({"kind": kind, "t0": offset + starts[i],
                           "t1": offset + (starts[i + 1] if i + 1 < len(starts) else duration),
                           "image": refs[0] if refs else None, "images": refs[1:],
                           "style": scene.get("type") if scene.get("type") in _STYLE_TYPES else
                           (scene.get("style") if scene.get("style") in _STYLE_TYPES else None)})
        offset += duration
    return scenes


def visual_mix_metrics(chapters, topic: str | None = None, *, root: Path | None = None) -> dict:
    root = root or ROOT
    spec_path = root / "data" / "long" / str(topic) / "spec.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8")) if spec_path.exists() else {}
    timings, estimated = {}, []
    for name, chapter in chapters:
        folder = root / "output" / "long" / str(topic) / name
        path = folder / "timing.json"
        if not path.exists():
            estimated.append(name + ": 215 tiếng/phút + line_pause/TAIL runner")
            continue
        timing = json.loads(path.read_text(encoding="utf-8"))
        # data.js carries aligned word times. Only read its lines, never stale
        # rendered scene types: classification always comes from source chNN.
        aligned = folder / "data.js"
        if aligned.exists():
            data = json.loads(aligned.read_text(encoding="utf-8").split("=", 1)[1].strip().rstrip(";"))
            lines = data.get("lines") or []
            if len(lines) == len(timing.get("segments") or []) and all(
                a.get("text") == b.get("text") and a.get("start") == b.get("start")
                and a.get("end") == b.get("end") for a, b in zip(lines, timing["segments"])
            ):
                timing["segments"] = lines
        if any(isinstance(s.get("at"), list) and len(s["at"]) > 1 and s["at"][1]
               for s in chapter.get("scenes", [])) and not all(s.get("words") for s in timing.get("segments", [])):
            estimated.append(name + ": nội suy neo chữ từ TTS")
        timings[name] = timing
    metrics = visual_mix.measure(visual_mix_scenes(chapters, timings=timings, spec=spec))
    metrics["estimated"] = estimated
    metrics["reason"] = spec.get("text_budget_reason")
    return metrics


def visual_mix_findings(chapters, topic=None):
    metrics = visual_mix_metrics(chapters, topic)
    return visual_mix.issues(metrics, is_new=visual_mix_is_new(topic), is_long=True,
                             reason=metrics["reason"])


def visual_mix_report(chapters, topic=None) -> str:
    metrics = visual_mix_metrics(chapters, topic)
    label = "; ".join(metrics["estimated"]) or "TTS"
    findings = visual_mix.issues(metrics, is_new=visual_mix_is_new(topic), is_long=True,
                                reason=metrics["reason"])
    return (f"visual_mix ({label}):\n" + visual_mix.format_table(metrics)
            + "".join(f"\nvisual_mix {level}: {msg}" for level, msg in findings))


def _text(line) -> str:
    return line if isinstance(line, str) else line.get("t", "")


def _imgs(s: dict) -> list[str]:
    out = [s.get("img"), s.get("bg"), (s.get("a") or {}).get("img"), (s.get("b") or {}).get("img")]
    return [x for x in out if x]


def measure(chapters) -> dict:
    """chapters: [(name, ch_dict)] như build_long.load trả về."""
    syl = total = kinetic = naked = vid = auto = 0
    types, imgs = set(), set()
    for _, ch in chapters:
        syl += sum(len(_text(ln).split()) for ln in ch.get("lines", []))
        for s in ch.get("scenes", []):
            total += 1
            types.add(s.get("type"))
            imgs.update(_imgs(s))
            kinetic += s.get("type") == "kinetic"
            vid += bool(s.get("vid") or (s.get("type") == "broll" and s.get("pd")))
            auto += bool(s.get("auto"))
            if s.get("type") in _TEXT_ONLY and not _imgs(s) and not s.get("vid"):
                naked += 1
    return {"syl": syl, "chapters": len(chapters), "scenes": total, "types": len(types), "imgs": len(imgs),
            "vid_scenes": vid, "auto": auto, "kinetic": kinetic / total if total else 1.0, "naked": naked / total if total else 1.0}


def cine_warning(scenes):
    images = [s for s in scenes if s.get('type') in {'photo', 'print', 'split', 'pano'}]
    count = sum(bool(s.get('cam')) for s in images)
    return f"cine_auto: chỉ {count}/{len(images)} ảnh có cam (dưới 50%)" if images and count / len(images) < .5 else None


def pano_share(planned_chapters) -> tuple[int, float]:
    """planned_chapters: [[scene,...], ...] đã plan() (có t0/t1). Trả (số pano, tỉ lệ thời lượng)."""
    total = pano = 0.0
    count = 0
    for scenes in planned_chapters:
        total += max((s.get("t1", 0) for s in scenes), default=0)
        for s in scenes:
            if s.get("type") == "pano":
                count += 1
                pano += s["t1"] - s["t0"]
    return count, (pano / total if total else 0.0)


def _planned_scenes(topic: str, chapters, out_root: Path | None = None):
    """Cảnh đã plan() của mọi chương từ output/long/<topic>/chNN/data.js; thiếu chương nào thì None (không đo được)."""
    import json
    root = out_root or Path(__file__).resolve().parents[2] / "output" / "long"
    planned = []
    for name, _ in chapters:
        try:
            raw = (root / topic / name / "data.js").read_text(encoding="utf-8")
            planned.append(json.loads(raw.split("=", 1)[1].strip().rstrip(";")).get("scenes") or [])
        except (OSError, IndexError, ValueError):
            return None
    return planned


def pano_problems(chapters, topic: str | None = None, out_root: Path | None = None) -> list[str]:
    """Tối đa MAX_PANO cảnh pano và MAX_PANO_SHARE thời lượng. Số cảnh đếm từ kịch bản; tỉ lệ cần data.js đã dựng."""
    out = []
    count = sum(1 for _, ch in chapters for s in ch.get("scenes", []) if s.get("type") == "pano")
    if count > MAX_PANO:
        out.append(f"{count} cảnh pano, tối đa {MAX_PANO} mỗi Long (ảnh rộng lia máy là gia vị, không phải khuôn)")
    planned = _planned_scenes(topic, chapters, out_root) if topic and count else None
    if planned:
        _, share = pano_share(planned)
        if share > MAX_PANO_SHARE:
            out.append(f"pano chiếm {share:.0%} thời lượng, tối đa {MAX_PANO_SHARE:.0%}")
    return out


def _coverage_report(topic: str) -> dict:
    """Đo đúng cách coverage_lint phân lớp: biểu đồ/timeline/infographic không là nền chữ."""
    try:
        from motion.long import coverage_lint
    except ImportError:  # build_long.py nạp floor.py như module đứng một mình
        import coverage_lint
    return coverage_lint.analyse(topic)


def _mim_ck_problems(topic: str | None, *, check_percent=True) -> list[str]:
    if not topic:
        return ["chưa có timing"]
    try:
        coverage = _coverage_report(topic)
    except FileNotFoundError:
        return ["chưa có timing"]

    out = []
    text_percent = coverage["text_only_percent"]
    if check_percent and text_percent > MIM_CK_MAX_EMPTY_BACKGROUND_PERCENT:
        out.append("chữ nền trống "
                   f"{text_percent:.2f}% > {MIM_CK_MAX_EMPTY_BACKGROUND_PERCENT:.0f}%")
    text_run = coverage["longest_text_only_run_s"]
    if text_run > MIM_CK_MAX_CONSECUTIVE_TEXT_SECONDS:
        out.append("chuỗi chữ nền trống "
                   f"{text_run:.2f}s > {MIM_CK_MAX_CONSECUTIVE_TEXT_SECONDS:.0f}s")
    return out


def problems(chapters, channel: str = "CL", topic: str | None = None, idcards_enabled: bool = False) -> list[str]:
    """Trả lỗi sàn theo kênh; MIM/CK đo coverage từ ``timing.json`` của topic."""
    channel = (channel or "CL").upper()
    m = measure(chapters)
    is_new = visual_mix_is_new(topic)
    out = pano_problems(chapters, topic)
    if idcards_enabled:
        try:
            from motion.long import idcards
        except ImportError:
            import idcards
        out.extend(idcards.problems(chapters))
    if m["auto"]:
        out.append(f"{m['auto']} cảnh do scenes_from tự cắt 4 từ đầu câu (\"auto\") chưa ai biên tập: đó là bản nháp, không phải cảnh")
    if channel in {"MIM", "CK"}:
        out.extend(_mim_ck_problems(topic, check_percent=not is_new))
    else:  # CL, và spec Long cũ chưa khai báo channel, giữ nguyên sàn đã đăng.
        if m["syl"] < MIN_SYL:
            out.append(f"kịch bản {m['syl']} âm tiết (≈{m['syl'] / 215:.0f} phút), sàn {MIN_SYL} (≈23 phút)")
        if m["chapters"] < MIN_CHAPTERS:
            out.append(f"{m['chapters']} chương, sàn {MIN_CHAPTERS}")
        if m["types"] < MIN_TYPES:
            out.append(f"chỉ {m['types']} loại cảnh, sàn {MIN_TYPES} (photo, map, file, split, ledger, bars, sketch, broll…)")
        if m["imgs"] < MIN_IMGS:
            out.append(f"dùng {m['imgs']} ảnh tư liệu, sàn {MIN_IMGS} — chạy research_long.py / media_search.py trước khi viết cảnh")
        if m["vid_scenes"] < MIN_VID_SCENES:
            out.append(f"{m['vid_scenes']} cảnh có b-roll, sàn {MIN_VID_SCENES}")
        if not is_new and m["naked"] > MAX_NAKED:
            out.append(f"{m['naked']:.0%} cảnh là chữ trên nền trống (không ảnh, không b-roll), trần {MAX_NAKED:.0%}")
    if not is_new and m["kinetic"] > MAX_KINETIC:
        out.append(f"{m['kinetic']:.0%} cảnh là kinetic, trần {MAX_KINETIC:.0%}")
    if is_new:
        out.extend(f"visual_mix: {msg}" for level, msg in visual_mix_findings(chapters, topic) if level == "ERROR")
    return out


def has_research(od: Path) -> bool:
    return (od / "research.json").exists()


def report(chapters) -> str:
    m = measure(chapters)
    return (f"{m['syl']} âm tiết · {m['chapters']} chương · {m['scenes']} cảnh · {m['types']} loại · {m['imgs']} ảnh · "
            f"{m['vid_scenes']} cảnh b-roll · kinetic {m['kinetic']:.0%} · chữ nền trống {m['naked']:.0%}")
