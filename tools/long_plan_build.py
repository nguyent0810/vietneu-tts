"""Dựng khung plan JSON cho 5 Long pilot điện ảnh (07/11, Lead) từ script_P*.txt — tất định, chỉ số dòng khớp.

Quy ước kịch bản:
  - mỗi dòng một câu đọc; dòng `**Tên**` là thẻ chương (giữ trong script như plan_long_tt5)
  - dòng riêng `[cảnh Cx ...]`  -> câu đọc kế tiếp gắn visuals {"type":"clip","clip":"Cx"}
  - `[im]` / `[hit]` (dòng riêng hoặc cuối câu) -> beats {"<câu>": "silence"|"hit"} (câu đọc kế tiếp, 1-based)
  - `[KE]` / `[TA]` đầu dòng -> voices ("ke"/"ta"), bỏ tiền tố
  - `[BẢNG 12 CHI]`, `[BẢN ĐỒ 6 PHẦN]` (ghi chú hình) -> câu kế tiếp gắn visual từ META[...]["marker_visuals"]
  - ghi chú `[...]` khác bị bỏ khỏi lời đọc
Khung chưa có ảnh/clip thật cho thân bài: `media` để trống, điền ở bước asset.

    python output/cl_staging/long/pilot_plan_build.py            # dựng cả 5
    python output/cl_staging/long/pilot_plan_build.py P1_temiya  # một bài

    python tools/long_plan_build.py --script script.txt --id new_id \
        --series bud --base base.json --out plan.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LONG_DIR = REPO_ROOT / "output" / "cl_staging" / "long"
HERE = DEFAULT_LONG_DIR
BUD_BASE = HERE / "plan_long_tt5.json"
FS_BASE = HERE / "plan_P5_12canhcua.haiku_v1.json"  # khung FS do agent Haiku dựng (style/tts/thumbnail/seo); visuals bảng lấy lại ở dưới

MARK_RE = re.compile(r"\[(im|hit)\]")
SCENE_RE = re.compile(r"^\[cảnh\s+(C\d+)\b")
NOTE_RE = re.compile(r"\[[^\]]*\]")


META = {
    "P1_temiya": dict(
        id="L_bud_P1_temiya", base=BUD_BASE, kicker="TRUYỆN TIỀN THÂN · PHIM",
        title="Hoàng Tử Temiya | 16 Năm Giả Câm Để Không Phải Làm Vua (Phim Trọn Bộ)",
        questions=[("Bên miệng hố, cậu nói gì?", 4, "Ta không điếc, không câm"),
                   ("Khi vua cha dâng lại ngai vàng, cậu trả lời ra sao?", 6, "Ai bảo đảm được mặt trời ngày mai"),
                   ("Người cầm xẻng hôm ấy, về sau là ai?", 7, "Xá Lợi Phất")],
        ambience=["forest", "temple_bell_far", "fire", "night_insects", "forest", "wind", "forest", "river"],
    ),
    "P2_kisagotami": dict(
        id="L_bud_P2_kisagotami", base=BUD_BASE, kicker="TÍCH TRUYỆN PHÁP CÚ",
        title="Vì Sao Đức Phật Bảo Người Mẹ Mất Con Đi Xin Một Hạt Cải? | Tích Truyện Pháp Cú – Kisa Gotami",
        questions=[("Cô xin thuốc cứu con. Đức Phật trả lời cô bằng gì?", 5, "một việc để làm"),
                   ("Cô có tìm được ngôi nhà chưa ai chết không?", 7, "lời đáp cho câu hỏi thứ hai"),
                   ("Ngọn đèn dầu nói gì với cô, nhiều năm sau?", 10, "lời đáp cho câu hỏi thứ ba")],
        ambience=["market", "market", "temple_bell_far", "night_insects", "market", "temple_bell_far", "market",
                  "night_insects", "river", "wind", "fire", "temple_bell_far"],
    ),
    "P3_ananda": dict(
        id="L_bud_P3_ananda", base=BUD_BASE, kicker="NGÔI THỨ NHẤT · A NAN",
        voice_ta="Tuyen",  # Lead chọn 07/11 (ticket 018): nam BUD trầm ấm, tách khỏi giọng kể Binh
        title="Theo Phật 25 Năm Vẫn Chưa Thoát: Đêm Cuối Cùng Của Tôn Giả A Nan",
        questions=[("A Nan đứng khóc bên một cánh cửa. Đức Phật nói gì với ngài?", 5, "cánh cửa"),
                   ("Giữa lúc chân rời đất và đầu chạm gối, điều gì xảy ra?", 6, "gối"),
                   ("Vì sao, sau khi chứng quả, ngài vẫn bị nêu ra năm lỗi?", 8, "năm lỗi")],
        ambience=["night_insects", "forest", "forest", "rain", "wind", "forest", "night_insects", "cave",
                  "temple_bell_far"],
    ),
    "P4_thanglong": dict(
        id="L_fs_P4_thanglong", base=FS_BASE, kicker="THĂNG LONG · TRUYỀN THUYẾT",
        title="Vì Sao Bùa Yểm Không Trụ Nổi Ở Thăng Long? Ngựa Trắng Bạch Mã Và 4 Vị Thần Giữ Kinh Thành",
        questions=[("Long Đỗ là ai, mà kẻ đi yểm phải lập đền thờ?", 2, "Long Đỗ"),
                   ("Dưới đất Ba Đình, có gì thật?", 3, "giếng"),
                   ("Bốn vị thần, vì sao đứng đúng bốn điểm ấy?", 4, "tứ trấn"),
                   ("Con ngựa trắng xuất hiện lần đầu trong cuốn sách nào?", 6, "Thăng Long cổ tích khảo")],
        ambience=["rain", "rain", "wind", "cave", "temple_bell_far", "river", "night_insects"],
        cold_clips={"C1": "Mùa thu năm", "C2": "Bức tường đất", "C3": "Thợ đứng im", "C4": "Rồi từ phía đền Long Đỗ",
                    "C5": "Mỗi bước, nó để lại"},
    ),
    "P5_12canhcua": dict(
        id="L_fs_P5_12canhcua", base=FS_BASE, kicker="TỬ VI 2027 · TẬP 1", format="tra_cuu",
        title="12 Cánh Cửa Của Năm 2027: Con Giáp Nào Bước Tiếp, Con Giáp Nào Nên Dừng Lại?",
        questions=None,
        ambience=["night_insects", "wind", "market", "temple_bell_far", "river", "fire", "forest", "night_insects",
                  "night_insects", "forest", "forest", "temple_bell_far", "fire", "night_insects", "temple_bell_far"],
        cold_clips={"C1": "Đêm giao thừa.", "C2": "Một người đàn bà", "C3": "Thầy Sơn đặt la bàn", "C4": "Thầy đặt tay lên ô",
                    "C5": "Bạn sinh năm nào?"},
    ),
}


def parse(path: Path):
    lines, voices, visuals, beats, markers = [], [], {}, [], []
    pending_scene, pending_beats, pending_marker = None, [], None
    for raw in path.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s:
            continue
        m = SCENE_RE.match(s)
        if m:
            pending_scene = m.group(1)
            rest = NOTE_RE.sub("", s).strip()
            if not rest:
                continue
            s = s[s.index("]") + 1:].strip()
        if s in ("[BẢNG 12 CHI]", "[BẢN ĐỒ 6 PHẦN]") or (s.startswith("[") and s.endswith("]") and not MARK_RE.fullmatch(s)
                                                       and not s.startswith(("[KE]", "[TA]"))):
            if "BẢNG" in s or "BẢN ĐỒ" in s:
                pending_marker = s
            if not MARK_RE.search(s):
                continue
        voice = "ke"
        if s.startswith("[KE]"):
            s = s[4:].strip()
        elif s.startswith("[TA]"):
            voice, s = "ta", s[4:].strip()
        kinds = MARK_RE.findall(s)
        inline_mk = re.search(r"\[(BẢNG 12 CHI|BẢN ĐỒ 6 PHẦN)", s)
        text = NOTE_RE.sub("", s).strip()
        if not text:  # dòng chỉ có [im]/[hit]
            pending_beats += kinds
            continue
        lines.append(text)
        voices.append(voice)
        n = len(lines)
        for k in pending_beats:
            beats.append({"line": n, "kind": "silence" if k == "im" else "hit"})
        pending_beats = []
        if pending_scene:
            visuals[str(n)] = {"type": "clip", "clip": pending_scene}
            pending_scene = None
        if pending_marker:
            markers.append((n, pending_marker))
            pending_marker = None
        if inline_mk:
            markers.append((n, inline_mk.group(1)))
        # [im]/[hit] cuối câu: nhịp rơi ngay sau câu này
        pending_beats += kinds
    return lines, voices, visuals, beats, markers


def build(key: str, long_dir: Path = DEFAULT_LONG_DIR) -> Path:
    here = Path(long_dir)
    meta = META[key]
    base_path = Path(long_dir) / Path(meta["base"]).name
    base = json.loads(base_path.read_text(encoding="utf-8"))[0]
    lines, voices, visuals, beats, markers = parse(here / f"script_{key}.txt")
    heads = [i for i, l in enumerate(lines, 1) if l.startswith("**")]
    # KHÔNG chép seo/tags/playlists của plan mẫu (review 07/11: mang metadata tập khác) — điền ở bước đóng gói
    keep = {k: base[k] for k in ("style", "theme", "series", "lane", "badge", "chapters", "pacing", "kinetic",
                                 "captions", "tts", "sound", "layout_policy") if k in base}
    plan = {**keep, "id": meta["id"], "day": None, "slot": None, "hold": True, "kicker": meta["kicker"],
            "title": meta["title"], "thumbnail": None, "script": lines}
    # khoảng nghỉ theo dòng của plan mẫu không áp được cho kịch bản mới
    plan["tts"] = {**plan.get("tts", {}), "pauses": {}}
    if meta.get("format"):
        plan["format"] = meta["format"]
    if "ta" in voices:
        plan["voices"] = voices
        plan["tts"] = {**plan.get("tts", {}), "voice_ta": meta.get("voice_ta")}
    # định dạng hf_ambience (nhánh feat/011): {"<câu>": "silence"|"hit"}, nhịp rơi NGAY TRƯỚC câu đó
    plan["beats"] = {str(b["line"]): b["kind"] for b in beats}
    plan["silence"] = [b["line"] for b in beats if b["kind"] == "silence"]
    plan["pace_gate"] = "on"
    plan["subs"] = "chunk"
    # ambience: phần mở đầu (trước thẻ đầu tiên, nếu có) + mỗi chương
    # định dạng hf_ambience: chapter 0 = cold open trước thẻ chương đầu; gain_db cộng vào mức chuẩn (0 = chuẩn)
    chaps = ([0] if not heads or heads[0] != 1 else []) + list(range(1, len(heads) + 1))
    amb = meta["ambience"]
    plan["ambience"] = [{"chapter": c, "kind": amb[min(i, len(amb) - 1)], "gain_db": 0}
                        for i, c in enumerate(chaps)]
    # Dữ liệu visual đặc thù của pilot nằm cạnh plan pilot, không trong builder.
    marker_visuals = meta.get("marker_visuals")
    pilot_data_path = here / f"pilot_tables_{key}.json"  # thiếu file thì bỏ qua bảng
    if pilot_data_path.exists():
        marker_visuals = json.loads(pilot_data_path.read_text(encoding="utf-8"))
    if marker_visuals:
        first = {}
        for n, mk in markers:
            first.setdefault("BẢNG" if "BẢNG" in mk else "BẢN ĐỒ", n)
        for tag, v in marker_visuals.items():
            if tag in first:
                v = json.loads(json.dumps(v))
                n0 = first[tag]
                if v["type"] == "lookup":
                    v["until"] = max(n for n, mk in markers if "BẢNG" in mk)
                    v["find"] = [{"row": f["row"], "at": n0 + f["off"], "word": f["word"], "note": f["note"]}
                                 for f in v.pop("find_rel", [])]
                else:
                    v["until"] = n0
                    for it in v["items"]:
                        it["at"] = n0
                visuals[str(n0)] = v
    elif meta.get("marker_visuals_from"):
        old = json.loads((Path(long_dir) / Path(meta["marker_visuals_from"]).name).read_text(encoding="utf-8"))[0]["visuals"]
        table = next((v for v in old.values() if v.get("type") == "lookup"), None)
        lst = next((v for v in old.values() if v.get("type") == "list"), None)
        for n, mk in markers:
            v = table if "BẢNG" in mk else lst
            if v and str(n) not in visuals:
                visuals[str(n)] = v
    # clip cold open do agent Haiku gắn (kịch bản không có dòng [cảnh]): khớp lại theo NỘI DUNG câu, không theo chỉ số
    hk = here / f"plan_{key}.haiku_v1.json"
    src = hk if hk.exists() else (here / f"plan_{key}.json")
    if src.exists() and not any(v.get("type") == "clip" for v in visuals.values()):
        old = json.loads(src.read_text(encoding="utf-8"))[0]
        oscript = old.get("script", [])
        for k, v in (old.get("visuals") or {}).items():
            if v.get("type") == "clip" and k.isdigit() and 0 < int(k) <= len(oscript):
                txt = NOTE_RE.sub("", oscript[int(k) - 1]).strip()
                if txt in lines:
                    visuals.setdefault(str(lines.index(txt) + 1), {"type": "clip", "clip": v["clip"]})
    for clip, prefix in (meta.get("cold_clips") or {}).items():
        i = next((j for j, l in enumerate(lines, 1) if l.startswith(prefix)), None)
        if i:
            visuals.setdefault(str(i), {"type": "clip", "clip": clip})
    # engine chưa có loại visual "clip": tách sang khoá `clips` {"<câu>": "Cx"}; bước asset đổi thành media mp4
    plan["clips"] = {k: v["clip"] for k, v in visuals.items() if v.get("type") == "clip"}
    plan["visuals"] = {k: v for k, v in visuals.items() if v.get("type") != "clip"}
    plan["media"] = {}
    plan["seo"], plan["tags"], plan["playlists"] = None, [], []
    if meta["questions"]:
        plan["questions"] = [{"id": f"q{i}", "chapter": ch} for i, (_, ch, _) in enumerate(meta["questions"], 1)]
        plan["answers"] = [{"chapter": ch, "answers": [f"q{i}"]} for i, (_, ch, _) in enumerate(meta["questions"], 1)]
        plan["vong"] = [{"mo": q, "dong": d} for q, _, d in meta["questions"]]
    out = here / f"plan_{key}.json"
    # giữ phần thợ asset/đóng gói đã điền (media, ảnh trong visuals, thumbnail, seo, tags, playlists)
    if out.exists():
        prev = json.loads(out.read_text(encoding="utf-8"))[0]
        if prev.get("media"):
            plan["media"] = prev["media"]
            plan["clips"] = {}  # thợ asset đã điền media cho cold open (clip/ảnh khung đầu) — bỏ chỗ giữ clip
        for k, v in (prev.get("visuals") or {}).items():
            plan["visuals"].setdefault(k, v)
        for k in ("thumbnail", "seo", "tags", "playlists", "day", "slot"):
            if prev.get(k):
                plan[k] = prev[k]
    if out.exists():
        bak = out.with_suffix(".haiku_v1.json")
        if not bak.exists():
            bak.write_text(out.read_text(encoding="utf-8"), encoding="utf-8")
    from library.tools.plan_enrich import enrich_long_plan  # #294: trộn kiểu hình mặc định cho Long mới
    _ch = "bud" if str(plan.get("series") or plan.get("id") or "").lower().find("bud") >= 0 else "fs"
    plan = enrich_long_plan(plan, _ch)
    import hf_batch_render as HBR
    HBR.save_plan_rows(out, [plan], channel=_ch, legacy=False)
    print(f"{key}: {len(lines)} dòng, {len(heads)} thẻ chương, {len(plan['visuals'])} visual, {len(plan['clips'])} clip, {len(beats)} nhịp"
          + (f", ke/ta {voices.count('ke')}/{voices.count('ta')}" if "ta" in voices else ""))
    return out


def build_new(script: Path, ident: str, series: str, base_path: Path, out_path: Path) -> Path:
    """Build a new Long row using a caller-supplied template and script."""
    base_data = json.loads(base_path.read_text(encoding="utf-8"))
    base = base_data[0] if isinstance(base_data, list) else base_data
    lines, voices, visuals, beats, markers = parse(script)
    heads = [i for i, line in enumerate(lines, 1) if line.startswith("**")]
    base_visuals = base.get("visuals") or {}
    table = next((v for v in base_visuals.values()
                  if isinstance(v, dict) and v.get("type") == "lookup"), None)
    listing = next((v for v in base_visuals.values()
                    if isinstance(v, dict) and v.get("type") == "list"), None)
    for line_no, marker in markers:
        visual = table if "BẢNG" in marker else listing if "BẢN ĐỒ" in marker else None
        if visual and str(line_no) not in visuals:
            visuals[str(line_no)] = json.loads(json.dumps(visual, ensure_ascii=False))
    keep = {key: base[key] for key in (
        "style", "theme", "series", "lane", "badge", "chapters", "pacing", "kinetic",
        "captions", "tts", "sound", "layout_policy",
    ) if key in base}
    plan = {**keep,
        "id": ident,
        "series": series,
        "lane": "long",
        "day": None,
        "slot": None,
        "hold": True,
        "title": None,
        "thumbnail": None,
        "script": lines,
        "visuals": visuals,
        "media": {},
        "seo": None,
        "tags": [],
        "playlists": [],
    }
    plan["tts"] = {**plan.get("tts", {}), "pauses": {}}
    if "ta" in voices:
        plan["voices"] = voices
    else:
        plan.pop("voices", None)
    plan["beats"] = {str(b["line"]): b["kind"] for b in beats}
    plan["silence"] = [b["line"] for b in beats if b["kind"] == "silence"]
    plan["pace_gate"] = "on"
    plan["subs"] = "chunk"
    chapter_ids = (([0] if not heads or heads[0] != 1 else []) + list(range(1, len(heads) + 1)))
    base_ambience = base.get("ambience") or [{"kind": "forest", "gain_db": 0}]
    plan["ambience"] = [
        {"chapter": chapter, **{k: v for k, v in base_ambience[min(i, len(base_ambience) - 1)].items()
                                if k != "chapter"}}
        for i, chapter in enumerate(chapter_ids)
    ]
    plan["clips"] = {k: v["clip"] for k, v in visuals.items() if v.get("type") == "clip"}
    plan["visuals"] = {k: v for k, v in visuals.items() if v.get("type") != "clip"}
    from library.tools.plan_enrich import enrich_long_plan
    plan = enrich_long_plan(plan, series)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    import hf_batch_render as HBR
    HBR.save_plan_rows(out_path, [plan], channel=series, legacy=False)
    print(f"{ident}: {len(lines)} dòng, {len(heads)} thẻ chương, {len(plan['visuals'])} visual, {len(plan['clips'])} clip, {len(beats)} nhịp"
          + (f", ke/ta {voices.count('ke')}/{voices.count('ta')}" if "ta" in voices else ""))
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pilot_ids", nargs="*", help="Pilot id cũ; bỏ trống để dựng cả 5")
    parser.add_argument("--long-dir", type=Path, default=DEFAULT_LONG_DIR,
                        help="Thư mục chứa base plan và META cho chế độ pilot")
    parser.add_argument("--script", type=Path, help="Tệp kịch bản Long mới")
    parser.add_argument("--id", dest="ident", help="ID plan mới")
    parser.add_argument("--series", choices=("bud", "fs"), help="Kênh của plan mới")
    parser.add_argument("--base", type=Path, help="Base plan JSON")
    parser.add_argument("--out", type=Path, help="Plan JSON đầu ra")
    args = parser.parse_args(argv)
    explicit = (args.script, args.ident, args.series, args.base, args.out)
    if any(explicit):
        if not all(explicit):
            parser.error("--script, --id, --series, --base và --out phải dùng cùng nhau")
        build_new(args.script, args.ident, args.series, args.base, args.out)
        return 0
    if args.pilot_ids and args.pilot_ids != ["--help"]:
        for key in args.pilot_ids:
            build(key, args.long_dir)
    else:
        for key in META:
            if (args.long_dir / f"script_{key}.txt").exists():
                build(key, args.long_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
