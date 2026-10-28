#!/usr/bin/env python3
"""Sinh prompt ảnh AI tất định từ câu lời đọc. Không gọi LLM.

Khuôn câu: khối phong cách của hồ sơ kênh + chủ thể từ điển + văn hoá
kênh + ánh sáng + cụm khẳng định chống rủi ro. Tên kênh không được
gõ cứng; mọi khác biệt nằm trong hồ sơ và từ điển.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHANNELS = ROOT / "library" / "channels"
LEXICON = ROOT / "library" / "assets" / "lexicon"
LONG_OUT = ROOT / "output" / "cl_staging" / "long" / "out"
TOOLS_DIR = ROOT / "output" / "cl_staging" / "grok" / "tools"
if str(TOOLS_DIR) not in sys.path and TOOLS_DIR.is_dir():
    sys.path.insert(0, str(TOOLS_DIR))

try:
    import static_hold
    _static_image = static_hold.static_image
except ImportError:
    def _static_image(spec: dict) -> bool:
        kind = str(spec.get("kind") or "video").lower()
        if kind not in {"image", "local", "commons"}:
            return False
        path = str(spec.get("path") or spec.get("file") or "").lower()
        return not path.endswith((".mp4", ".mov", ".webm", ".m4v"))

# Giữ chỗ cho cụm ngoại lệ khi thay từ rủi ro, rồi trả lại nguyên văn.
_GHE = "\u0000p{0}\u0000"


def so_anh_bu(giay: float, N: float) -> int:
    """max(0, ceil(giây/N) - 1), giây làm tròn 2 số như static_hold."""
    if N <= 0:
        raise ValueError("N phải dương")
    g = round(float(giay), 2)
    return max(0, math.ceil(g / float(N) - 1e-12) - 1)


def fold(text: str) -> str:
    """Chữ thường, bỏ dấu. đ → d. Mỗi ký tự gốc còn một ký tự."""
    text = text.lower().replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def sach(text: str) -> str:
    return text.replace("*", " ").replace("#", " ").replace("\n", " ")


def _bien(needle: str) -> re.Pattern:
    return re.compile(r"(?<!\w)" + re.escape(needle) + r"(?!\w)")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_profile(path: Path) -> dict:
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"hồ sơ không phải đối tượng: {path}")
    return data


def profile_for(plan: dict, channel_profile: dict | None, profile_path: Path | None = None) -> dict:
    if channel_profile is not None:
        return channel_profile
    if profile_path is not None:
        return load_profile(profile_path)
    series = str(plan.get("series") or "").strip()
    path = CHANNELS / f"{series}.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"không có hồ sơ kênh {path}")
    return load_profile(path)


def _phrases(entry: dict) -> list[str]:
    vi = entry.get("vi")
    if isinstance(vi, str):
        return [vi.strip()] if vi.strip() else []
    if isinstance(vi, list):
        return [str(x).strip() for x in vi if str(x).strip()]
    return []


def load_lexicon(profile: dict, lexicon_dir: Path | None = None) -> tuple[dict, list[dict], list[str]]:
    """Trả (quy tắc đã trộn, mục từ điển, cụm chặn). Kênh ghi đè cùng một cụm."""
    folder = Path(lexicon_dir) if lexicon_dir else LEXICON
    chung = load_json(folder / "chung.json")
    kenh = str(profile.get("kenh") or "").strip()
    rieng: dict = {}
    path = folder / f"{kenh}.json" if kenh else None
    if path is not None and path.is_file():
        rieng = load_json(path)
    assets = profile.get("assets") if isinstance(profile.get("assets"), dict) else {}
    quy = chung.get("quy_tac") if isinstance(chung.get("quy_tac"), dict) else {}
    tu = dict(quy.get("tu_thay") or {})
    tu.update(assets.get("tu_thay") or {})
    tu.update(rieng.get("tu_thay") or {})
    hieu = {
        "ngoai_le": list(quy.get("ngoai_le") or []),
        "cam_phu_dinh": list(quy.get("cam_phu_dinh") or []),
        "cam_tu": list(quy.get("cam_tu") or []) + list(assets.get("cam_tu") or []),
        "cam_cum": list(quy.get("cam_cum") or []) + list(assets.get("cam_cum") or []),
        "tu_thay": tu,
    }
    by_key: dict[str, dict] = {}
    for src in (chung.get("muc") or [], rieng.get("muc") or []):
        if not isinstance(src, list):
            continue
        for entry in src:
            if not isinstance(entry, dict):
                continue
            for phrase in _phrases(entry):
                by_key[fold(phrase)] = {**entry, "vi": phrase}
    entries = list(by_key.values())
    chan = [str(x) for x in (chung.get("chan") or []) if str(x).strip()]
    chan += [str(x) for x in (rieng.get("chan") or []) if str(x).strip()]
    return hieu, entries, chan


def match_sentence(sentence: str, entries: list[dict], chan: list[str]) -> tuple[dict | None, str]:
    """Cụm dài khớp trước. Câu có dấu thì khớp đúng dấu, để hồ/họ và cửa/của không dính nhau.

    Câu không dấu thì so bản đã bỏ dấu. Cụm chặn nuốt khoảng chữ, cụm ngắn bên trong không khớp.
    """
    raw = sach(sentence).lower()
    folded = fold(raw)
    dung_fold = folded == raw.replace("đ", "d")
    hay = folded if dung_fold else raw

    def key_of(phrase: str) -> str:
        return fold(phrase) if dung_fold else phrase.lower()

    cands: list[tuple[int, str, dict | None, str]] = []
    for phrase in chan:
        key = key_of(phrase)
        if key:
            cands.append((len(key), key, None, phrase))
    for entry in entries:
        phrase = str(entry.get("vi") or "")
        key = key_of(phrase)
        if not key:
            continue
        blocker = not str(entry.get("en") or "").strip()
        cands.append((len(key), key, None if blocker else entry, phrase))
    cands.sort(key=lambda item: (-item[0], item[1]))
    occupied = [False] * (len(hay) + 1)
    for _length, key, entry, phrase in cands:
        for found in _bien(key).finditer(hay):
            span = range(found.start(), found.end())
            if any(occupied[i] for i in span):
                continue
            for i in span:
                occupied[i] = True
            if entry is not None:
                return entry, phrase
    return None, ""


def chon_cau(start: int, end: int, durations: list[float], extras: int,
             sentences: list[str] | None = None, entries: list[dict] | None = None,
             chan: list[str] | None = None) -> list[int]:
    """Chỉ số câu (0-based) để chèn ảnh.

    Ưu tiên câu có khớp từ điển (theo nghĩa) gần điểm chia đều nhất;
    không có thì mới chia đều, bỏ câu đầu.
    """
    if extras <= 0 or end <= start:
        return []
    offsets: list[tuple[int, float]] = []
    acc = 0.0
    for i in range(start, end + 1):
        offsets.append((i, acc))
        acc += durations[i]
    total = acc
    if total <= 0:
        return []
    targets = [k * total / (extras + 1) for k in range(1, extras + 1)]
    cands = [i for i in range(start + 1, end + 1)]
    if len(cands) <= extras:
        return cands

    offsets_map = dict(offsets)
    has_match: dict[int, bool] = {}
    if sentences is not None and entries is not None:
        for i in cands:
            s_text = sentences[i] if i < len(sentences) else ""
            m_entry, _ = match_sentence(s_text, entries, chan or [])
            has_match[i] = m_entry is not None
    else:
        for i in cands:
            has_match[i] = False

    used: set[int] = set()
    chosen: list[int] = []
    for target in targets:
        p_deu = None
        for i, off in offsets:
            if i == start or i in used:
                continue
            if off + 1e-9 >= target:
                p_deu = i
                break
        if p_deu is None:
            for i, _off in reversed(offsets):
                if i != start and i not in used:
                    p_deu = i
                    break

        if p_deu is not None and has_match.get(p_deu):
            pick = p_deu
        else:
            matched_unused = [i for i in cands if i not in used and has_match.get(i)]
            if matched_unused:
                ref_off = offsets_map[p_deu] if p_deu is not None else target
                pick = min(matched_unused, key=lambda i: (abs(offsets_map[i] - ref_off), i))
            else:
                pick = p_deu

        if pick is not None:
            used.add(pick)
            chosen.append(pick)
    chosen.sort()
    return chosen


def _chon_mau(video_id: str, sid: int, salt: str, options) -> str:
    opts = [str(x).strip() for x in (options or []) if str(x).strip()]
    if not opts:
        return ""
    digest = hashlib.sha256(f"{salt}|{video_id}|{sid}".encode()).digest()
    return opts[int.from_bytes(digest[:4], "big") % len(opts)]


def _dien(template: str, slots: dict[str, str]) -> str:
    out = template or ""
    for key, value in slots.items():
        out = out.replace("{" + key + "}", value)
    out = re.sub(r"\{[a-z0-9_]+\}", "", out)
    return " ".join(out.split())


def _ghi_ngoai_le(text: str, ngoai_le: list[str]) -> tuple[str, list[str]]:
    kept: list[str] = []

    def park(match: re.Match) -> str:
        kept.append(match.group(0))
        return _GHE.format(len(kept) - 1)

    for phrase in ngoai_le:
        if phrase:
            text = re.sub(re.escape(phrase), park, text, flags=re.I)
    return text, kept


def _tra_ngoai_le(text: str, kept: list[str]) -> str:
    for i, original in enumerate(kept):
        text = text.replace(_GHE.format(i), original)
    return text


def ap_tu_thay(text: str, tu_thay: dict, ngoai_le: list[str]) -> str:
    text, kept = _ghi_ngoai_le(text, ngoai_le)
    for src, dst in sorted(tu_thay.items(), key=lambda kv: -len(kv[0])):
        if not src:
            continue
        if " " in src:
            text = re.sub(re.escape(src), str(dst), text, flags=re.I)
        else:
            text = re.sub(rf"\b{re.escape(src)}\b", str(dst), text, flags=re.I)
    return _tra_ngoai_le(text, kept)


def van_de(text: str, quy: dict) -> list[str]:
    """Những chỗ còn câu phủ định hoặc từ rủi ro, sau khi đã trừ cụm ngoại lệ."""
    masked, _kept = _ghi_ngoai_le(text, list(quy.get("ngoai_le") or []))
    errs: list[str] = []
    for pat in quy.get("cam_phu_dinh") or []:
        if re.search(pat, masked, flags=re.I):
            errs.append(pat)
    for word in quy.get("cam_tu") or []:
        if word and re.search(rf"\b{re.escape(word)}\b", masked, flags=re.I):
            errs.append(word)
    for phrase in quy.get("cam_cum") or []:
        if phrase and phrase.lower() in masked.lower():
            errs.append(phrase)
    return errs


def ghep_prompt(profile: dict, entry: dict, video_id: str, sid: int, quy: dict) -> str:
    assets = profile.get("assets") if isinstance(profile.get("assets"), dict) else {}
    scale = entry.get("scale")
    khong_gian = entry.get("khong_gian")
    vung = entry.get("vung")

    shot_theo_scale = assets.get("shot_theo_scale") if isinstance(assets.get("shot_theo_scale"), dict) else {}
    shot_opts = shot_theo_scale.get(scale) if (scale and scale in shot_theo_scale) else assets.get("shot")
    shot = _chon_mau(video_id, sid, "shot", shot_opts)

    lens_theo_scale = assets.get("lens_theo_scale") if isinstance(assets.get("lens_theo_scale"), dict) else {}
    lens_opts = lens_theo_scale.get(scale) if (scale and scale in lens_theo_scale) else assets.get("lens")
    lens = _chon_mau(video_id, sid, "lens", lens_opts)

    nen = _chon_mau(video_id, sid, "nen", assets.get("nen"))
    slots = {
        "shot": shot,
        "lens": lens,
        "nen": nen,
    }

    ghi_de_vung = assets.get("ghi_de_vung") if isinstance(assets.get("ghi_de_vung"), dict) else {}
    ov = ghi_de_vung.get(vung) if (vung and vung in ghi_de_vung) else {}

    culture = entry.get("van_hoa") or ov.get("van_hoa") or assets.get("van_hoa") or ""

    if entry.get("anh_sang"):
        lighting_raw = entry["anh_sang"]
    elif ov:
        lighting_raw = (
            ov.get(f"anh_sang_{khong_gian}")
            or ov.get("anh_sang")
            or assets.get("anh_sang")
            or ""
        )
    elif khong_gian and assets.get("anh_sang_theo_khong_gian"):
        kg_map = assets["anh_sang_theo_khong_gian"]
        lighting_raw = kg_map.get(khong_gian) or assets.get("anh_sang") or ""
    else:
        lighting_raw = assets.get("anh_sang") or ""

    if isinstance(lighting_raw, list):
        lighting_template = _chon_mau(video_id, sid, "anh_sang", lighting_raw)
    else:
        lighting_template = str(lighting_raw)

    subject = " ".join(str(entry.get("en") or "").split())
    if entry.get("boi_canh"):
        subject = subject.rstrip(" .") + ", " + " ".join(str(entry["boi_canh"]).split())
    parts = [
        _dien(str(assets.get("phong_cach") or ""), slots),
        subject,
        _dien(str(culture), slots),
        _dien(lighting_template, slots),
    ]
    nhom = str(entry.get("nhom") or "")
    theo = assets.get("cum_theo_nhom") if isinstance(assets.get("cum_theo_nhom"), dict) else {}
    if nhom and theo.get(nhom):
        parts.append(str(theo[nhom]))
    for cum in assets.get("cum_khang_dinh") or []:
        parts.append(str(cum))
    if entry.get("bo_sung"):
        parts.append(str(entry["bo_sung"]))
    clean = [" ".join(p.split()).strip(" .;") for p in parts]
    text = ". ".join(p for p in clean if p) + "."
    return ap_tu_thay(text, quy.get("tu_thay") or {}, list(quy.get("ngoai_le") or []))


def _segments_of(plan: dict, video_id: str, segments) -> list[dict]:
    if segments is not None:
        return list(segments)
    if isinstance(plan.get("segments"), list):
        return list(plan["segments"])
    path = LONG_OUT / f"{video_id}.json"
    if not path.is_file():
        raise FileNotFoundError(f"không có giây thật: {path}")
    data = load_json(path)
    segs = data.get("segments")
    if not isinstance(segs, list):
        raise ValueError(f"{path} thiếu segments")
    return segs


def _media_of(plan: dict) -> dict:
    media = plan.get("media") or {}
    if isinstance(media, dict) and isinstance(media.get("media"), dict):
        media = media["media"]
    if not isinstance(media, dict):
        return {}
    return {str(k): v for k, v in media.items() if str(k).isdigit() and isinstance(v, dict)}


def _spans(plan: dict, segments: list[dict]) -> tuple[list[dict], list[float]]:
    """Cảnh ảnh tĩnh theo đúng media_holds của bridge. Trả (cảnh, duration từng câu)."""
    import hyperframes_bridge as HB

    script = list(plan.get("script") or [])
    n = min(len(script), len(segments))
    script, segments = script[:n], segments[:n]
    media = _media_of(plan)
    lines = []
    for i in range(n):
        raw = str(script[i])
        lines.append({
            "sentence_id": i + 1,
            "start": float(segments[i]["start"]),
            "end": float(segments[i]["end"]),
            "heading": raw.startswith("**") and raw.endswith("**") and raw.count("**") == 2,
        })
    visuals = plan.get("visuals") or {}
    if visuals:
        HB.apply_visuals(lines, visuals, media)
    holds = HB.media_holds(lines, {int(k) for k in media})
    durations = [
        (float(segments[i + 1]["start"]) if i + 1 < n else float(segments[i]["end"])) - float(segments[i]["start"])
        for i in range(n)
    ]
    scenes = []
    for start, end in holds.items():
        sid = start + 1
        spec = media.get(str(sid), {})
        if not _static_image(spec):
            continue
        dur = sum(durations[start:end + 1])
        scenes.append({
            "start": start,
            "end": end,
            "sid": sid,
            "duration_s": round(dur, 2),
            "text": str(segments[start].get("text") or script[start]),
        })
    return scenes, durations


def _cau(segments: list[dict], script: list, index: int) -> str:
    if index < len(segments) and segments[index].get("text"):
        return str(segments[index]["text"])
    if index < len(script):
        return str(script[index])
    return ""


def assemble(plan, video_id, N=8, channel_profile=None, *, entries=None, chan=None,
             quy=None, lexicon_dir=None, segments=None) -> tuple[list[dict], list[dict]]:
    """Trả (prompt khớp, dòng không dùng được)."""
    profile = profile_for(plan, channel_profile)
    if entries is None or quy is None:
        quy_file, entries_file, chan_file = load_lexicon(profile, lexicon_dir)
        if quy is None:
            quy = quy_file
        if entries is None:
            entries = entries_file
        if chan is None:
            chan = chan_file
    entries = entries or []
    chan = chan or []
    quy = quy or {"ngoai_le": [], "cam_phu_dinh": [], "cam_tu": [], "cam_cum": [], "tu_thay": {}}
    segs = _segments_of(plan, video_id, segments)
    script = list(plan.get("script") or [])
    scenes, durations = _spans(plan, segs)
    cau_texts = [_cau(segs, script, i) for i in range(len(durations))]
    matched: list[dict] = []
    missed: list[dict] = []
    for scene in scenes:
        extras = so_anh_bu(scene["duration_s"], N)
        if extras <= 0:
            continue
        picks = chon_cau(scene["start"], scene["end"], durations, extras, cau_texts, entries, chan)
        thieu_ranh_gioi = extras - len(picks)
        for _ in range(thieu_ranh_gioi):
            missed.append({
                "sid_chen": scene["sid"],
                "ten": "",
                "prompt": "",
                "cau": sach(scene["text"]).strip(),
                "ly_do": f"cảnh câu {scene['sid']} dài {scene['duration_s']}s cần {extras} ảnh, chỉ có {len(picks)} ranh giới câu",
            })
        for index in picks:
            cau = sach(_cau(segs, script, index)).strip()
            sid = index + 1
            entry, phrase = match_sentence(cau, entries, chan)
            ten = f"{video_id}_s{sid}"
            if entry is None:
                missed.append({
                    "sid_chen": sid,
                    "ten": ten,
                    "prompt": "",
                    "cau": cau,
                    "ly_do": "không khớp từ điển",
                })
                continue
            prompt = ghep_prompt(profile, entry, str(video_id), sid, quy)
            loi = van_de(prompt, quy)
            if loi:
                missed.append({
                    "sid_chen": sid,
                    "ten": ten,
                    "prompt": "",
                    "cau": cau,
                    "ly_do": "prompt còn từ cấm: " + ", ".join(loi),
                })
                continue
            matched.append({
                "sid_chen": sid,
                "ten": ten,
                "prompt": prompt,
                "cau": cau,
                "ly_do": (
                    f"cảnh mở câu {scene['sid']} dài {scene['duration_s']}s > N={N}, "
                    f"chèn tại câu {sid}; khớp «{phrase}»"
                ),
                "cum": phrase,
                "nhom": entry.get("nhom") or "",
                "rong": bool(entry.get("rong")),
            })
    matched.sort(key=lambda row: row["sid_chen"])
    missed.sort(key=lambda row: (row["sid_chen"], row["ly_do"]))
    return matched, missed


def build(plan, video_id, N=8, channel_profile=None, **kwargs) -> list[dict]:
    """Prompt đã khớp từ điển. Câu không khớp không được đoán."""
    matched, _missed = assemble(plan, video_id, N, channel_profile, **kwargs)
    return matched


def tom_tat(video_id: str, N: float, matched: list[dict], missed: list[dict]) -> dict:
    lex_miss = [row for row in missed if row["ly_do"] == "không khớp từ điển"]
    boundary = [row for row in missed if "ranh giới" in row["ly_do"]]
    banned = [row for row in missed if row["ly_do"].startswith("prompt còn")]
    can = len(matched) + len(lex_miss) + len(banned) + len(boundary)
    hep = sum(1 for row in matched if not row.get("rong"))
    dem: dict[str, int] = {}
    for row in matched:
        dem[row.get("cum") or ""] = dem.get(row.get("cum") or "", 0) + 1
    top = [{"cum": k, "n": v} for k, v in sorted(dem.items(), key=lambda kv: (-kv[1], kv[0]))[:8]]
    return {
        "id": video_id,
        "N": N,
        "can_chen": can,
        "khop": len(matched),
        "khop_hep": hep,
        "khong_khop": len(lex_miss),
        "vi_pham": len(banned),
        "khong_ranh_gioi": len(boundary),
        "ty_le": round(len(matched) / can, 4) if can else None,
        "ty_le_hep": round(hep / can, 4) if can else None,
        "top_cum": top,
    }


def viet_prompt(path: Path, video_id: str, N: float, rows: list[dict]) -> None:
    lines = [f"# prompt_builder {video_id} N={N}"]
    for row in rows:
        lines.append(f"{row['ten']} | {row['prompt']}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def viet_unmatched(path: Path, video_id: str, rows: list[dict]) -> None:
    lines = ["# id\tsid\tly_do\tcau"]
    for row in rows:
        cau = row["cau"].replace("\t", " ").replace("\n", " ")
        lines.append(f"{video_id}\t{row['sid_chen']}\t{row['ly_do']}\t{cau}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _tim_video(data, video_id: str) -> dict:
    if isinstance(data, dict) and data.get("id") == video_id:
        return data
    rows = data if isinstance(data, list) else (data.get("videos") or data.get("items") or [])
    for row in rows:
        if isinstance(row, dict) and row.get("id") == video_id:
            return row
    raise SystemExit(f"không thấy {video_id} trong plan")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sinh prompt ảnh AI tất định từ một Long")
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--N", type=float, default=8)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--unmatched", type=Path)
    ap.add_argument("--profile", type=Path, help="hồ sơ kênh, nếu không thì lấy theo series của plan")
    args = ap.parse_args(argv)
    plan = _tim_video(load_json(args.plan), args.id)
    profile = load_profile(args.profile) if args.profile else None
    matched, missed = assemble(plan, args.id, args.N, profile)
    summary = tom_tat(args.id, args.N, matched, missed)
    if args.out:
        viet_prompt(args.out, args.id, args.N, matched)
        unmatched = args.unmatched or (args.out.parent / "unmatched.txt")
        viet_unmatched(unmatched, args.id, missed)
        summary["prompts"] = str(args.out)
        summary["unmatched"] = str(unmatched)
    else:
        for row in matched:
            print(f"{row['ten']} | {row['prompt']}")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
