#!/usr/bin/env python3
"""Danh mục và tra cứu kho tài sản ảnh/video đa kênh tất định (ticket #47, #58, #95, #140/#142).

Python thuần, không gọi LLM, không đổi tên hay xóa file media.
Hỗ trợ các lệnh:
  - scan: quét kho media, ghi library/assets/manifest.jsonl (tất định, gộp trùng nội dung)
  - find: tra cứu tài sản theo kênh rồi chung (fallback), tag, loại, lọc 7 ngày, kho_loc
  - add: nhập 1 ảnh đã soát vào manifest (không copy/xoá file)
  - mark-used: ghi nhận đã dùng trên một kênh/ngày
  - merge-external: gộp manifest Mimck (remote, không chép file)
  - check: kiểm tra toàn vẹn (file mất, sha lệch, giấy phép unknown, ảnh AI chưa strip_mark)
  - manifest-for: xuất danh sách file + sha256 cho một plan (dùng cho rsync --files-from và sha256sum -c)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import subprocess
import io
import sys
import time
import tempfile
import unicodedata
from datetime import date, timedelta
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
DEFAULT_MANIFEST = REPO_ROOT / "library" / "assets" / "manifest.jsonl"
CHANNELS_DIR = REPO_ROOT / "library" / "channels"
LEXICON_DIR = REPO_ROOT / "library" / "assets" / "lexicon"
TAXONOMY_PATH = REPO_ROOT / "library" / "inventory" / "taxonomy.json"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".m4v"}
MEDIA_EXTS = IMAGE_EXTS | VIDEO_EXTS

DEFAULT_SCAN_DIRS = [
    "chunks_cache/commons",
    "chunks_cache/museum",
    "chunks_cache/openverse",
    "chunks_cache/pdvideo",
    "chunks_cache/relic",
    "chunks_cache/symbol_clips",
    "chunks_cache/extmedia",
    "chunks_cache/beat_assets",
    "output/cl_staging/long/research/ai_media",
    "output/cl_staging/grok/samples/flow_mark",
    "output/cl_staging/grok/samples/opening/flow_out",
    "output/cl_staging/grok/samples/packaging/flow_raw",
    "hyperframes_short/compositions/_media",
    "assets/symbol_library",
    "output/cl_staging/grokbot",
    "output/cl_staging/flow",
]

GROKBOT_REL = "output/cl_staging/grokbot"
# Lô ảnh Flow (ai_image_batch run-flow): <lô>/raw/*.jpg, cùng luật LEAD_DA_XEM + LOAI_BO.txt như GrokBot
FLOW_REL = "output/cl_staging/flow"
AI_BATCH_RELS = (GROKBOT_REL, FLOW_REL)
SCHEMA_VERSION = "1.2.0"
PROMPT_GROUP_TAGS = {
    "MIM": ["mim", "cong_nghe"],
    "CK": ["ck", "tien_bac"],
    "CL": ["cl", "hinh_su", "minh_hoa_chung"],
}


def fold(text: str) -> str:
    """Chuẩn hoá chữ thường, bỏ dấu tiếng Việt, đ -> d."""
    if not text:
        return ""
    text = text.lower().replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def get_image_dimensions(path: Path) -> tuple[int, int]:
    """Lấy kích thước w, h của ảnh bằng Pillow hoặc pure Python fallback."""
    try:
        from PIL import Image  # noqa: PLC0415
        Image.MAX_IMAGE_PIXELS = None
        with Image.open(path) as img:
            return int(img.width), int(img.height)
    except Exception:
        pass

    # Pure Python fallback for PNG, GIF, JPEG
    try:
        with open(path, "rb") as f:
            header = f.read(32)
            if header.startswith(b"\x89PNG\r\n\x1a\n"):
                w, h = struct.unpack(">II", header[16:24])
                return int(w), int(h)
            if header.startswith((b"GIF87a", b"GIF89a")):
                w, h = struct.unpack("<HH", header[6:10])
                return int(w), int(h)
            # JPEG scan
            f.seek(0)
            data = f.read(65536)
            idx = 2
            while idx < len(data) - 9:
                if data[idx] == 0xFF:
                    m = data[idx + 1]
                    if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                        h, w = struct.unpack(">HH", data[idx + 5:idx + 9])
                        return int(w), int(h)
                    seg_len = struct.unpack(">H", data[idx + 2:idx + 4])[0]
                    idx += 2 + seg_len
                else:
                    idx += 1
    except Exception:
        pass
    return 1920, 1080


def get_video_dimensions_and_duration(path: Path) -> tuple[int, int, float | None]:
    """Lấy w, h, duration_s của video từ sidecar json hoặc pure Python mp4 parser."""
    sidecar_json = path.with_suffix(path.suffix + ".json")
    if not sidecar_json.is_file():
        # Try without extension suffix, e.g. foo.json for foo.mp4
        cand = path.with_suffix(".json")
        if cand.is_file():
            sidecar_json = cand

    if sidecar_json.is_file():
        try:
            meta = json.loads(sidecar_json.read_text(encoding="utf-8"))
            w = meta.get("source_w") or meta.get("width") or meta.get("w")
            h = meta.get("source_h") or meta.get("height") or meta.get("h")
            dur = meta.get("dur") or meta.get("duration_s") or meta.get("source_dur")
            if w and h:
                return int(w), int(h), float(dur) if dur is not None else None
        except Exception:
            pass

    # Pure Python MP4 parser
    w, h, dur = 1920, 1080, None
    try:
        with open(path, "rb") as f:
            data = f.read(250000)
            # mvhd
            idx = data.find(b"mvhd")
            if idx != -1 and idx + 36 <= len(data):
                v = data[idx + 4]
                if v == 0:
                    timescale, duration = struct.unpack(">II", data[idx + 16:idx + 24])
                else:
                    timescale, duration = struct.unpack(">IQ", data[idx + 24:idx + 36])
                if timescale > 0:
                    dur = round(duration / timescale, 2)
            # tkhd
            tidx = data.find(b"tkhd")
            if tidx != -1:
                tv = data[tidx + 4]
                # width and height are fixed-point 16.16 at end of tkhd box (84 bytes for v0, 96 bytes for v1)
                offset = tidx + (96 if tv == 1 else 84)
                if offset <= len(data):
                    tw = struct.unpack(">I", data[offset - 8:offset - 4])[0] >> 16
                    th = struct.unpack(">I", data[offset - 4:offset])[0] >> 16
                    if tw > 0 and th > 0:
                        w, h = tw, th
    except Exception:
        pass
    return w, h, dur


def _read_yaml_or_json(path: Path) -> Any:
    """Đọc YAML hoặc JSON; thử JSON trước (hồ sơ kênh trong repo là JSON hợp lệ YAML)."""
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except Exception:
        import yaml  # noqa: PLC0415
        return yaml.safe_load(raw)


def _channel_record(data: dict, stem: str = "", external: bool = False) -> dict:
    return {
        "id": str(data["kenh"]).strip(),
        "ngach": [str(x).strip() for x in data.get("ngach") or []],
        "assets": data.get("assets") or {},
        "kho_loc": data.get("kho_loc") if isinstance(data.get("kho_loc"), dict) else {},
        "stem": stem,
        "repo": data.get("repo"),
        "external": external,
    }


def load_channels(channels_dir: Path) -> list[dict]:
    """Tải hồ sơ kênh thực từ ``channels/*.yaml`` (bỏ file bắt đầu bằng ``_``)."""
    channels: list[dict] = []
    if not channels_dir.is_dir():
        return channels
    for p in sorted(channels_dir.iterdir()):
        if p.name.startswith("_"):
            continue
        if p.suffix not in (".yaml", ".json"):
            continue
        try:
            data = _read_yaml_or_json(p)
            if isinstance(data, dict) and data.get("kenh"):
                channels.append(_channel_record(data, stem=p.stem, external=False))
        except Exception:
            pass
    return channels


def pham_vi_hop_le(channels: list[dict] | None = None, channels_dir: Path | None = None) -> list[str]:
    """Danh sách pham_vi hợp lệ: id/stem hồ sơ kênh + ``chung``."""
    if channels is None:
        channels = load_channels(channels_dir or CHANNELS_DIR)
    ids: list[str] = []
    seen: set[str] = set()
    for ch in channels:
        for cid in channel_aliases(ch):
            if cid and cid not in seen:
                ids.append(cid)
                seen.add(cid)
    if "chung" not in seen:
        ids.append("chung")
    return ids


def expand_pham_vi_query(pham_vi: str, channels: list[dict]) -> set[str]:
    """Đổi stem yaml (vsd) ↔ id kênh khi so khớp pham_vi."""
    if not pham_vi:
        return set()
    out = {pham_vi}
    for ch in channels:
        als = set(channel_aliases(ch))
        if pham_vi in als:
            out.update(als)
    return out


def channel_aliases(ch: dict) -> list[str]:
    """Id kênh và tên file yaml (stem) — dùng khớp tên lô, không gõ cứng."""
    aliases: list[str] = []
    for a in (ch.get("id"), ch.get("stem")):
        s = str(a or "").strip()
        if s and s not in aliases:
            aliases.append(s)
    return aliases


def kho_loc_for(pham_vi: str, channels: list[dict]) -> dict:
    """Lấy kho_loc của kênh đang tra; không có thì {}."""
    if not pham_vi or pham_vi == "chung":
        return {}
    for ch in channels:
        if ch.get("id") == pham_vi or ch.get("stem") == pham_vi:
            return ch.get("kho_loc") or {}
    return {}


def license_family(lic_type: str) -> str:
    """Chuẩn hoá giấy phép thành họ: PD, CC0, CC BY, CC BY-SA, CC BY-NC, CC BY-ND, GFDL, hoặc chuỗi gốc."""
    t = fold(lic_type or "")
    t = t.replace("_", " ").replace(".", " ")
    t = re.sub(r"\s+", " ", t).strip()
    if not t or t == "unknown":
        return ""
    compact = t.replace(" ", "").replace("-", "")
    if "gfdl" in compact or "gnufreedocumentation" in compact:
        return "GFDL"
    if "bync" in compact or "noncommercial" in compact or "non commercial" in t:
        return "CC BY-NC"
    if "bynd" in compact or "noderiv" in compact or "no deriv" in t:
        return "CC BY-ND"
    if "bysa" in compact or "sharealike" in compact or "share alike" in t:
        return "CC BY-SA"
    if "cc0" in compact:
        return "CC0"
    if compact.startswith("ccby") or "ccby" in compact:
        return "CC BY"
    if "publicdomain" in compact or compact in {"pd", "pdm"} or t.startswith("pd "):
        return "PD"
    return fold(lic_type).upper()


def license_allowed(lic_type: str, allowed: list[str]) -> bool:
    """True khi họ giấy phép nằm trong license_cho_phep (so khớp họ, không tiền tố CC BY ⊂ CC BY-SA)."""
    if not allowed:
        return True
    fam = license_family(lic_type)
    if not fam:
        return False
    allowed_fams = []
    for a in allowed:
        af = license_family(str(a))
        allowed_fams.append(af if af else fold(str(a)).upper())
    return fam in allowed_fams


def pham_vi_set(record: dict) -> set[str]:
    raw = str(record.get("pham_vi") or "chung")
    return {x.strip() for x in raw.split(",") if x.strip()}


def passes_kho_loc(record: dict, kho_loc: dict) -> bool:
    """Áp luật lọc kênh (license_cho_phep, tag_cam) kể cả khi record thuộc chung."""
    if not kho_loc:
        return True
    is_ai = bool(record.get("ai_generated"))
    # Kênh cấm ảnh AI (vd CL: Long chỉ dùng tư liệu tự do, creator_v2/CLAUDE.md)
    if is_ai and kho_loc.get("cam_anh_ai"):
        return False
    required_ai_tag = kho_loc.get("anh_ai_can_tag")
    if is_ai and required_ai_tag and required_ai_tag not in ((record.get("tags") or {}).get("core") or []) + ((record.get("tags") or {}).get("domain") or []):
        return False
    allowed = kho_loc.get("license_cho_phep") or []
    # license_cho_phep là luật cho ảnh của bên thứ ba; ảnh AI tự tạo không mang giấy phép PD/CC nên bỏ qua bước này
    if allowed and not is_ai:
        lic = str((record.get("license") or {}).get("type") or "")
        if not license_allowed(lic, [str(x) for x in allowed]):
            return False
    tag_cam = kho_loc.get("tag_cam") or []
    if tag_cam:
        tags = record.get("tags") or {}
        parts = list(tags.get("core") or []) + list(tags.get("domain") or [])
        parts.append(str(record.get("path") or ""))
        parts.append(str(record.get("prompt") or ""))
        parts.append(str((record.get("source") or {}).get("ref") or ""))
        blob = fold(" ".join(str(x).replace("_", " ").replace("-", " ") for x in parts))
        words = set(re.findall(r"[a-z0-9]+", blob))
        for cam in tag_cam:
            if _match_phrase(str(cam), blob, words):
                return False
    return True


def image_phash(image: Any) -> str:
    """64-bit DCT perceptual hash, encoded as 16 hexadecimal digits."""
    import numpy as np
    from PIL import Image
    pixels = np.asarray(image.convert("L").resize((32, 32), Image.Resampling.LANCZOS), dtype=float)
    x = np.arange(32)
    basis = np.cos(np.pi * (2 * x + 1)[:, None] * np.arange(8)[None, :] / 64)
    coeff = basis.T @ pixels @ basis
    median = np.median(coeff.flatten()[1:])
    value = 0
    for bit in (coeff.flatten() > median):
        value = (value << 1) | int(bit)
    return f"{value:016x}"


def media_phashes(path: Path, kind: str, duration: float | None = None) -> list[str]:
    from PIL import Image
    if kind == "img":
        with Image.open(path) as image:
            return [image_phash(image)]
    if not duration or duration <= 0:
        probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)], capture_output=True, check=True, text=True)
        duration = float(probe.stdout.strip())
    hashes = []
    for i in range(5):
        result = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(duration * (i + 0.5) / 5), "-i", str(path), "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True)
        with Image.open(io.BytesIO(result.stdout)) as image:
            hashes.append(image_phash(image))
    return hashes


def _hashes(record: dict) -> list[str]:
    value = record.get("phash")
    return [value] if isinstance(value, str) else (value or [])


def near_match(hashes: list[str], records: list[dict], threshold: int, root: Path) -> dict | None:
    for record in records:
        old = _hashes(record)
        if not old:
            path = root / str(record.get("path") or "")
            if path.is_file():
                try:
                    old = media_phashes(path, record.get("kind", "img"), record.get("duration_s"))
                except (OSError, ValueError, subprocess.SubprocessError):
                    continue
        if any((int(a, 16) ^ int(b, 16)).bit_count() <= threshold for a in hashes for b in old):
            return record
    return None


def near_dups(records: list[dict], threshold: int = 8, root: Path = REPO_ROOT) -> list[dict]:
    pairs = []
    for i, record in enumerate(records):
        hashes = _hashes(record)
        if not hashes:
            try:
                hashes = media_phashes(root / record["path"], record.get("kind", "img"), record.get("duration_s"))
            except (OSError, ValueError, subprocess.SubprocessError):
                continue
        for other in records[:i]:
            if near_match(hashes, [other], threshold, root):
                pairs.append({"asset_id": other["asset_id"], "near_id": record["asset_id"]})
    return pairs


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fp:
        while chunk := fp.read(65536):
            h.update(chunk)
    return h.hexdigest()


def write_manifest(manifest_path: Path, records: list[dict]) -> None:
    records = sorted(records, key=lambda r: r["asset_id"])
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as out:
        for r in records:
            out.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")


def _is_grokbot_path(rel_path: str) -> bool:
    """Ảnh thuộc một lô AI do Lead soát (GrokBot hoặc Flow)."""
    posix = rel_path.replace("\\", "/")
    return any(posix == r or posix.startswith(r + "/") for r in AI_BATCH_RELS)


def _is_flow_path(rel_path: str) -> bool:
    posix = rel_path.replace("\\", "/")
    return posix == FLOW_REL or posix.startswith(FLOW_REL + "/")


def parse_batch_prompts(batch_dir: Path) -> dict[str, str]:
    """Khớp prompt theo tên file từ prompts.md / prompt.md (tiêu đề ## file.png)."""
    text = ""
    for name in ("prompts.md", "prompt.md"):
        p = batch_dir / name
        if p.is_file():
            text = p.read_text(encoding="utf-8")
            break
    result: dict[str, str] = {}
    current_file: str | None = None
    current_lines: list[str] = []
    in_prompt = False
    file_re = re.compile(r"^##\s+(\S+\.(?:png|jpg|jpeg|webp|gif))\b", re.I)
    prompt_re = re.compile(r"^(?:[-*]\s*)?Prompt\s*\(EN\)\s*:\s*(.*)$", re.I)
    stop_re = re.compile(r"^(?:[-*]\s*)?(Khung|Cấm|Phong cách|Chương)\s*:", re.I)
    for line in text.splitlines():
        m = file_re.match(line)
        if m:
            if current_file:
                result[current_file] = "\n".join(current_lines).strip()
            current_file = m.group(1)
            current_lines = []
            in_prompt = False
            continue
        if current_file is None:
            continue
        pm = prompt_re.match(line)
        if pm:
            current_lines = [pm.group(1)] if pm.group(1) else []
            in_prompt = True
            continue
        if in_prompt:
            if line.startswith("## ") or stop_re.match(line):
                in_prompt = False
            else:
                current_lines.append(line)
    if current_file:
        result[current_file] = "\n".join(current_lines).strip()
    # Lô Flow: prompts*.txt dạng "tên | prompt" (tên = stem file, Flow thêm _1_<hash> khi tải)
    for txt in sorted(batch_dir.glob("prompts*.txt")):
        for line in txt.read_text(encoding="utf-8").splitlines():
            if "|" in line and not line.lstrip().startswith("#"):
                name, prompt = (t.strip() for t in line.split("|", 1))
                if name and prompt:
                    result.setdefault("stem:" + name, prompt)
    return result


def load_scenes_kenh(batch_dir: Path) -> dict[str, str]:
    p = batch_dir / "scenes.json"
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}
    out: dict[str, str] = {}
    if not isinstance(data, list):
        return out
    for item in data:
        if not isinstance(item, dict):
            continue
        slug = str(item.get("slug") or "").strip()
        kenh = str(item.get("kenh") or "").strip()
        if slug and kenh:
            out[slug] = kenh
    return out


def infer_pham_vi_from_batch(batch_name: str, channels: list[dict]) -> str | None:
    """Suy kênh từ tên lô: {id}_… hoặc {id} kèm số (bud24_…), khớp alias từ yaml."""
    name = fold(batch_name)
    hits: list[tuple[int, str]] = []
    for ch in channels:
        for alias in channel_aliases(ch):
            a = fold(alias)
            if not a:
                continue
            if name == a or name.startswith(a + "_"):
                hits.append((len(a), ch["id"]))
            elif name.startswith(a) and len(name) > len(a) and name[len(a)].isdigit():
                hits.append((len(a), ch["id"]))
    if not hits:
        return None
    hits.sort(key=lambda x: -x[0])
    best_len = hits[0][0]
    ids = {h[1] for h in hits if h[0] == best_len}
    if len(ids) == 1:
        return next(iter(ids))
    return None


def infer_pham_vi_from_text(text: str, channels: list[dict]) -> str | None:
    """Suy kênh từ prompt/ngạch; một kênh khớp thì trả về, nhiều/không thì None."""
    if not text:
        return None
    norm = fold(text)
    words = set(re.findall(r"[a-z0-9]+", norm))
    matched: set[str] = set()
    for ch in channels:
        for alias in channel_aliases(ch):
            if alias and _match_phrase(alias, norm, words):
                matched.add(ch["id"])
        for ng in ch.get("ngach") or []:
            if ng and _match_phrase(ng, norm, words):
                matched.add(ch["id"])
    if len(matched) == 1:
        return next(iter(matched))
    return None


def kenh_from_scenes(filename: str, scenes_map: dict[str, str], valid_ids: set[str]) -> str | None:
    if not scenes_map:
        return None
    stem = Path(filename).stem
    best: tuple[str, str] | None = None
    for slug, kenh in scenes_map.items():
        if slug and slug in stem and kenh in valid_ids:
            if best is None or len(slug) > len(best[0]):
                best = (slug, kenh)
    return best[1] if best else None


def style_tags_from_prompt(prompt: str) -> list[str]:
    """Tag phong cách tất định từ prompt (không LLM)."""
    if not prompt:
        return []
    n = fold(prompt)
    tags: list[str] = []
    if "painterly" in n or "illustration" in n:
        tags.append("painterly")
    if "photograph" in n or re.search(r"\bphoto\b", n):
        tags.append("photo")
    if "16:9" in prompt or "1920x1080" in n:
        tags.append("khung_169")
    if "9:16" in prompt or "1080x1920" in n:
        tags.append("khung_916")
    return tags


def grokbot_meta_for_file(
    png: Path,
    channels: list[dict],
    prompt_cache: dict[str, dict[str, str]],
    scenes_cache: dict[str, dict[str, str]],
) -> dict:
    """prompt + pham_vi cho một PNG GrokBot đã soát (LEAD_DA_XEM)."""
    batch_dir = png.parent.parent
    key = str(batch_dir)
    if key not in prompt_cache:
        prompt_cache[key] = parse_batch_prompts(batch_dir)
    if key not in scenes_cache:
        scenes_cache[key] = load_scenes_kenh(batch_dir)
    prompt = prompt_cache[key].get(png.name, "")
    if not prompt:
        stems = [k[5:] for k in prompt_cache[key] if k.startswith("stem:")]
        hit = max((st for st in stems if png.stem == st or png.stem.startswith(st + "_")), key=len, default=None)
        if hit:
            prompt = prompt_cache[key]["stem:" + hit]
    valid = set(pham_vi_hop_le(channels))
    pv = kenh_from_scenes(png.name, scenes_cache[key], valid)
    if not pv:
        pv = infer_pham_vi_from_batch(batch_dir.name, channels)
    if not pv:
        pv = infer_pham_vi_from_text(prompt, channels)
    if not pv:
        pv = "chung"
    return {"prompt": prompt, "pham_vi": pv, "batch": batch_dir.name}


def _loai_bo(batch: Path) -> set[str]:
    p = batch / "LOAI_BO.txt"
    if not p.is_file():
        return set()
    return {ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")}


def collect_grokbot_pngs(root: Path) -> tuple[list[Path], list[str]]:
    """Ảnh lô AI đã soát: grokbot/*/out/*.png và flow/*/raw/*.(jpg|png).

    Chỉ nạp lô có LEAD_DA_XEM; bỏ file Lead liệt kê trong LOAI_BO.txt. Trả (files, lô bỏ vì thiếu LEAD).
    """
    files: list[Path] = []
    skipped: list[str] = []
    for rel, sub, exts in ((GROKBOT_REL, "out", {".png"}), (FLOW_REL, "raw", {".jpg", ".jpeg", ".png", ".webp"})):
        base = root / rel
        if not base.is_dir():
            continue
        for batch in sorted(p for p in base.iterdir() if p.is_dir()):
            out = batch / sub
            imgs = sorted(p for p in out.iterdir() if p.is_file() and p.suffix.lower() in exts) if out.is_dir() else []
            if not imgs:
                continue
            if not (batch / "LEAD_DA_XEM").is_file():
                skipped.append(batch.name)
                continue
            bo = _loai_bo(batch)
            files.extend(p for p in imgs if p.name not in bo)
    return files, skipped


def parse_iso_date(value: str) -> date | None:
    try:
        return date.fromisoformat(str(value).strip()[:10])
    except Exception:
        return None


def usage_in_window(record: dict, channel: str, days: int, today: date) -> bool:
    """True nếu video_da_dung có mục cùng kênh trong [today-days, today]."""
    cutoff = today - timedelta(days=days)
    for item in record.get("video_da_dung") or []:
        if not isinstance(item, dict):
            continue
        if str(item.get("kenh") or "").strip() != channel:
            continue
        d = parse_iso_date(str(item.get("ngay") or ""))
        if d is None:
            continue
        if cutoff <= d <= today:
            return True
    return False


def load_taxonomy(taxonomy_path: Path) -> list[dict]:
    """Tải từ điển phân loại kỹ thuật/phong cách từ library/inventory/taxonomy.json."""
    if not taxonomy_path.is_file():
        return []
    try:
        data = json.loads(taxonomy_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def load_lexicon(lexicon_dir: Path) -> tuple[list[dict], dict[str, list[dict]]]:
    """Tải từ điển chủ thể chung và riêng từng kênh từ library/assets/lexicon/*.json."""
    core_entries: list[dict] = []
    domain_entries: dict[str, list[dict]] = {}
    if not lexicon_dir.is_dir():
        return core_entries, domain_entries

    for p in sorted(lexicon_dir.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            muc = data.get("muc") if isinstance(data, dict) else data
            if not isinstance(muc, list):
                continue
            stem = p.stem.lower()
            if stem == "chung":
                core_entries.extend(muc)
            else:
                domain_entries[stem] = muc
        except Exception:
            pass
    return core_entries, domain_entries


def load_plan_usages(repo_root: Path) -> dict[str, set[str]]:
    """Quét các plan và out json để ghi nhận video/plan nào đã sử dụng tài sản nào."""
    usage: dict[str, set[str]] = {}
    plan_files = list((repo_root / "output" / "cl_staging" / "long").glob("plan_long_*.json"))
    plan_files.extend(list((repo_root / "output" / "cl_staging" / "long" / "out").glob("*.json")))

    for pf in plan_files:
        try:
            data = json.loads(pf.read_text(encoding="utf-8"))
            rows = data if isinstance(data, list) else [data]
            for row in rows:
                if not isinstance(row, dict):
                    continue
                pid = str(row.get("id") or pf.stem).strip()
                if not pid or pid.endswith((".render", ".tts", ".opts")):
                    continue

                # Media dictionary
                media_dict = row.get("media") or {}
                if isinstance(media_dict, dict):
                    for _k, v in media_dict.items():
                        targets = []
                        if isinstance(v, dict):
                            for key in ("path", "file", "ref", "museum", "query"):
                                val = v.get(key)
                                if val:
                                    targets.append(str(val).strip())
                        elif isinstance(v, str):
                            targets.append(v.strip())

                        for t in targets:
                            usage.setdefault(t, set()).add(pid)
                            usage.setdefault(Path(t).name, set()).add(pid)
        except Exception:
            pass
    return usage


import functools

@functools.lru_cache(maxsize=4096)
def _phrase_pat(p: str) -> re.Pattern:
    return re.compile(r"(?<![a-z0-9])" + re.escape(p) + r"(?![a-z0-9])")


ALIAS_KEYWORDS: dict[str, list[str]] = {
    "la_ban": ["la ban", "la kinh", "compass", "luopan", "geomantic"],
    "lich": ["lich", "calendar", "almanac", "am lich"],
    "ban_tho": ["ban tho", "altar", "incense", "lu huong", "bat huong", "censer"],
    "bat_quai": ["bat quai", "bagua", "pa kua", "hexagram", "trigram"],
    "chua": ["chua", "pagoda", "temple", "shrine", "monastery"],
    "tuong_phat": ["tuong phat", "buddha", "bodhisattva", "phat thich ca", "di lac"],
    "hoa_sen": ["hoa sen", "lotus"],
    "thanh_luy": ["thanh", "citadel", "rampart", "fortress", "luy thay", "thanh co"],
    "may": ["may", "cloud", "clouds", "sky"],
    "mua": ["mua", "rain", "drizzle"],
}


def _match_phrase(phrase: str, norm_text: str, norm_words: set[str]) -> bool:
    """Khớp cụm từ cực nhanh và chính xác có ranh giới từ để tránh từ ngắn (mo, ho, do) khớp nhầm."""
    if not phrase or not norm_text:
        return False
    p = fold(phrase).strip()
    if not p or len(p) < 2:
        return False
    if " " not in p:
        return p in norm_words
    if p not in norm_text:
        return False
    return bool(_phrase_pat(p).search(norm_text))


def extract_tags_and_pham_vi(
    rel_path: str,
    file_name: str,
    sidecar_text: str,
    used_in_plans: list[str],
    channels: list[dict],
    taxonomy: list[dict],
    core_lex: list[dict],
    domain_lex: dict[str, list[dict]],
) -> tuple[str, list[str], list[str]]:
    """Trích xuất tất định (không LLM) pham_vi và bộ tag 2 tầng (core, domain)."""
    full_text = f"{rel_path} {file_name} {sidecar_text} {' '.join(used_in_plans)}"
    norm = fold(full_text)
    norm_words = set(re.findall(r"[a-z0-9]+", norm))

    core_tags: set[str] = set()
    domain_tags: set[str] = set()
    matched_channels: set[str] = set()

    # 1. Khớp từ điển taxonomy
    for item in taxonomy:
        kw_list = item.get("keywords") or []
        item_id = item.get("id") or ""
        group = item.get("group") or ""
        for kw in kw_list:
            if kw and len(kw) >= 3 and _match_phrase(kw, norm, norm_words):
                core_tags.add(item_id)
                if group:
                    core_tags.add(group)
                break

    # 2. Khớp ALIAS_KEYWORDS (song ngữ Anh - Việt cho các chủ thể then chốt)
    for tag_name, syns in ALIAS_KEYWORDS.items():
        if any(_match_phrase(syn, norm, norm_words) for syn in syns):
            # Gán domain tag nếu tag thuộc hồ sơ kênh động
            is_domain = False
            for ch in channels:
                assets_cfg = ch.get("assets") or {}
                if tag_name in assets_cfg.get("nhom_canh", []) or tag_name in ch.get("ngach", []):
                    domain_tags.add(tag_name)
                    matched_channels.add(ch["id"])
                    is_domain = True
            if not is_domain:
                core_tags.add(tag_name)

    # 3. Khớp từ điển core_lex (chung)
    for entry in core_lex:
        vi = entry.get("vi") or ""
        en = entry.get("en") or ""
        nhom = entry.get("nhom") or ""
        if (vi and _match_phrase(vi, norm, norm_words)) or (en and _match_phrase(en, norm, norm_words)):
            if nhom:
                core_tags.add(nhom)
            if vi and len(fold(vi)) >= 3:
                core_tags.add(fold(vi).replace(" ", "_"))

    # 4. Khớp từ điển domain_lex theo từng kênh (các từ khóa đặc thù miền)
    for ch_name, entries in domain_lex.items():
        ch_hit = False
        for entry in entries:
            vi = entry.get("vi") or ""
            en = entry.get("en") or ""
            nhom = entry.get("nhom") or ""
            if (vi and _match_phrase(vi, norm, norm_words)) or (en and _match_phrase(en, norm, norm_words)):
                ch_hit = True
                if nhom:
                    domain_tags.add(nhom)
                if vi and len(fold(vi)) >= 3:
                    domain_tags.add(fold(vi).replace(" ", "_"))
        if ch_hit:
            matched_channels.add(ch_name)

    # 5. Kiểm tra hồ sơ kênh từ channels
    for ch in channels:
        ch_id = ch["id"]
        # Khớp định danh kênh trong đường dẫn (vd: gpt_bud, bud_monk, fs_compass)
        if f"_{ch_id}_" in norm or f"/{ch_id}/" in norm or norm.startswith(f"{ch_id}_") or f"gpt_{ch_id}" in norm:
            matched_channels.add(ch_id)
        # Khớp ngạch chuyên biệt của kênh
        for ng in ch.get("ngach") or []:
            if ng and _match_phrase(ng, norm, norm_words):
                domain_tags.add(ng)
                matched_channels.add(ch_id)

    # 5. Quyết định pham_vi (không gõ cứng kênh)
    if len(matched_channels) == 1:
        pham_vi = next(iter(matched_channels))
    elif len(matched_channels) > 1:
        pham_vi = ",".join(sorted(matched_channels))
    else:
        pham_vi = "chung"

    # 6. Fallback tag nếu chưa có tag nào
    if not core_tags and not domain_tags:
        stem_tokens = [tok for tok in re.split(r"[-_.\s]+", Path(file_name).stem.lower()) if len(tok) >= 3 and not tok.isdigit()]
        for tok in stem_tokens[:4]:
            core_tags.add(fold(tok))

    return pham_vi, sorted(core_tags), sorted(domain_tags)


def parse_source_and_license(path: Path, rel_path: str) -> tuple[dict, dict, bool, bool | None]:
    """Xác định source, license, ai_generated, strip_mark từ file và sidecar (KHÔNG bịa thông tin)."""
    ai_generated = False
    strip_mark: bool | None = None
    source = {"type": "unknown", "ref": path.name, "page_url": None}
    license_info = {
        "type": "unknown",
        "commercial_allowed": False,
        "attribution_required": False,
        "attribution_text": None,
        "basis": "unknown",
        "basis_ref": None,
    }

    # GrokBot (ảnh AI đã soát, chỉ nạp khi lô có LEAD_DA_XEM)
    if _is_grokbot_path(rel_path):
        ai_generated = True
        source["type"] = "flow" if _is_flow_path(rel_path) else "grokbot"
        if _is_flow_path(rel_path):
            strip_mark = "crop"  # run-flow luôn tải bằng --strip-mark crop
        source["ref"] = path.name
        license_info["type"] = "AI Generated (Internal License)"
        license_info["commercial_allowed"] = True
        license_info["attribution_required"] = False
        license_info["basis"] = "sidecar"
        license_info["basis_ref"] = "LEAD_DA_XEM"
        return source, license_info, ai_generated, strip_mark

    # Kiểm tra AI folders
    if "ai_media" in rel_path or "flow_mark" in rel_path or "flow_raw" in rel_path or "flow_out" in rel_path:
        ai_generated = True
        is_flow = "flow" in rel_path.lower()
        source["type"] = "flow_ai" if is_flow else "chatgpt_ai"
        source["ref"] = path.name

        if is_flow:
            if "flow_raw" in rel_path or "_raw" in path.name:
                strip_mark = False
            elif "flow_mark/out" in rel_path or "clean" in path.name:
                strip_mark = True
            else:
                # Flow generate mặc định strip-mark từ 29/10 (ADR 0004 đã huỷ theo luật 21)
                strip_mark = True
        # Không có sidecar và không có fetcher_policy chứng minh -> license unknown
        return source, license_info, ai_generated, strip_mark

    # Symbol library
    if "symbol_library" in rel_path:
        source["type"] = "internal"
        source["ref"] = path.name
        return source, license_info, ai_generated, strip_mark

    # Sidecar json check
    sidecars = [
        path.with_suffix(path.suffix + ".json"),
        path.with_suffix(".json"),
        path.with_name(path.stem + ".source.json"),
    ]
    sidecar_data = None
    for sc in sidecars:
        if sc.is_file():
            try:
                sidecar_data = json.loads(sc.read_text(encoding="utf-8"))
                break
            except Exception:
                pass

    if "chunks_cache/commons" in rel_path:
        source["type"] = "commons"
        ref_file = sidecar_data.get("file") if sidecar_data else f"File:{path.name}"
        source["ref"] = ref_file or f"File:{path.name}"
        if sidecar_data and sidecar_data.get("license"):
            lic = str(sidecar_data["license"]).strip()
            license_info["type"] = lic
            license_info["commercial_allowed"] = "nc" not in lic.lower() and "nd" not in lic.lower()
            license_info["attribution_required"] = "by" in lic.lower()
            license_info["attribution_text"] = sidecar_data.get("credit")
            license_info["basis"] = "sidecar"
        elif sidecar_data and sidecar_data.get("credit"):
            license_info["type"] = "Wikimedia Commons Free License"
            license_info["commercial_allowed"] = True
            license_info["attribution_required"] = True
            license_info["attribution_text"] = sidecar_data.get("credit")
            license_info["basis"] = "sidecar"

    elif "chunks_cache/museum" in rel_path:
        source["type"] = "museum"
        source["ref"] = path.name
        if sidecar_data:
            # Fetcher hf_museum.py chỉ lấy CC0 từ The Met (dòng 115), AIC (dòng 121), CMA (dòng 127) và luôn ghi sidecar kèm theo
            license_info["type"] = "CC0 1.0"
            license_info["commercial_allowed"] = True
            license_info["attribution_required"] = False
            license_info["basis"] = "fetcher_policy"
            license_info["basis_ref"] = "hf_museum.py:115-128"
            license_info["attribution_text"] = sidecar_data.get("credit")
            source["page_url"] = sidecar_data.get("img")
        else:
            license_info["type"] = "unknown"
            license_info["basis"] = "unknown"

    elif "chunks_cache/relic" in rel_path:
        # Derivative 2.5D của hf_relic.py; không có sidecar giấy phép và hf_relic không phải fetcher lọc CC0
        source["type"] = "relic"
        source["ref"] = path.name
        license_info["type"] = "unknown"
        license_info["basis"] = "unknown"

    elif "chunks_cache/openverse" in rel_path:
        source["type"] = "openverse"
        source["ref"] = (sidecar_data.get("ref") if sidecar_data else None) or path.name
        if sidecar_data and sidecar_data.get("license"):
            lic = str(sidecar_data.get("license") or "by").lower()
            license_info["type"] = f"CC {lic.upper()}"
            license_info["commercial_allowed"] = "nc" not in lic and "nd" not in lic
            license_info["attribution_required"] = True
            license_info["attribution_text"] = sidecar_data.get("credit")
            license_info["basis"] = "sidecar"
            source["page_url"] = sidecar_data.get("landing")

    elif "chunks_cache/pdvideo" in rel_path:
        source["type"] = "pdvideo"
        source["ref"] = (sidecar_data.get("ref") if sidecar_data else None) or path.name
        if sidecar_data and sidecar_data.get("license"):
            license_info["type"] = str(sidecar_data["license"])
            license_info["commercial_allowed"] = True
            license_info["basis"] = "sidecar"
            license_info["attribution_text"] = sidecar_data.get("credit")
            source["page_url"] = sidecar_data.get("page")
        else:
            license_info["type"] = "unknown"
            license_info["basis"] = "unknown"

    elif "chunks_cache/beat_assets" in rel_path:
        if sidecar_data and (sidecar_data.get("provider") or sidecar_data.get("license")):
            provider = (sidecar_data.get("provider") or "").lower()
            if "pexels" in provider:
                source["type"] = "pexels"
                license_info["type"] = "Pexels License"
                license_info["commercial_allowed"] = True
                license_info["attribution_required"] = False
                license_info["attribution_text"] = sidecar_data.get("author")
                license_info["basis"] = "sidecar"
            elif "pixabay" in provider:
                source["type"] = "pixabay"
                license_info["type"] = "Pixabay License"
                license_info["commercial_allowed"] = True
                license_info["attribution_required"] = False
                license_info["attribution_text"] = sidecar_data.get("author")
                license_info["basis"] = "sidecar"
            elif sidecar_data.get("license"):
                source["type"] = str(sidecar_data.get("provider") or "beat_stock")
                license_info["type"] = str(sidecar_data["license"])
                license_info["commercial_allowed"] = True
                license_info["attribution_text"] = sidecar_data.get("author")
                license_info["basis"] = "sidecar"
            else:
                source["type"] = "unknown"
                license_info["type"] = "unknown"
                license_info["basis"] = "unknown"
            source["ref"] = (sidecar_data.get("id") if sidecar_data else None) or path.stem
            source["page_url"] = sidecar_data.get("page") if sidecar_data else None
        else:
            license_info["type"] = "unknown"
            license_info["basis"] = "unknown"

    elif "chunks_cache/extmedia" in rel_path:
        source["type"] = "extmedia"
        source["ref"] = path.name
        if sidecar_data and sidecar_data.get("license"):
            lic = str(sidecar_data["license"])
            license_info["type"] = lic
            license_info["commercial_allowed"] = "nc" not in lic.lower() and "nd" not in lic.lower()
            license_info["attribution_required"] = "by" in lic.lower()
            license_info["attribution_text"] = sidecar_data.get("credit")
            license_info["basis"] = "sidecar"

    return source, license_info, ai_generated, strip_mark


def scan_assets(
    root: Path = REPO_ROOT,
    manifest_path: Path = DEFAULT_MANIFEST,
    dirs: list[str] | None = None,
    near_threshold: int = 8, allow_near: bool = False,
) -> dict:
    """Quét các thư mục media, tính sha256, gộp tệp trùng lặp và ghi manifest.jsonl tất định."""
    t0 = time.time()
    scan_dir_names = dirs if dirs is not None else DEFAULT_SCAN_DIRS

    channels = load_channels(root / "library" / "channels")
    taxonomy = load_taxonomy(root / "library" / "inventory" / "taxonomy.json")
    core_lex, domain_lex = load_lexicon(root / "library" / "assets" / "lexicon")
    plan_usages = load_plan_usages(root)

    # 1. Thu thập tệp media (GrokBot không rglob cả cây — chỉ */out/*.png có LEAD_DA_XEM)
    found_files: list[Path] = []
    include_grokbot = False
    for dname in scan_dir_names:
        posix = str(dname).replace("\\", "/").rstrip("/")
        if any(posix == r or posix.startswith(r + "/") for r in AI_BATCH_RELS):
            include_grokbot = True
            continue
        p = root / dname
        if not p.exists():
            continue
        if p.is_file() and p.suffix.lower() in MEDIA_EXTS:
            found_files.append(p)
        elif p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file() and f.suffix.lower() in MEDIA_EXTS:
                    found_files.append(f)

    grokbot_skipped: list[str] = []
    grokbot_files: list[Path] = []
    if include_grokbot:
        grokbot_files, grokbot_skipped = collect_grokbot_pngs(root)
        found_files.extend(grokbot_files)

    # Sắp xếp danh sách tệp theo đường dẫn tương đối để đảm bảo thứ tự duyệt tất định
    found_files.sort(key=lambda x: str(x.relative_to(root)))
    prompt_cache: dict[str, dict[str, str]] = {}
    scenes_cache: dict[str, dict[str, str]] = {}

    # 2. Băm sha256 và gom nhóm theo sha256
    by_sha: dict[str, list[Path]] = {}
    for f in found_files:
        try:
            h = hashlib.sha256()
            with open(f, "rb") as fp:
                while chunk := fp.read(65536):
                    h.update(chunk)
            digest = h.hexdigest()
            by_sha.setdefault(digest, []).append(f)
        except Exception:
            pass

    # 3. Tạo record tài sản
    old_records = load_manifest(manifest_path) if manifest_path.is_file() else []
    old_by_sha = {r.get("sha256"): r for r in old_records}
    asset_records: list[dict] = []
    rejected_near = []
    hash_errors = []
    for sha, paths in by_sha.items():
        asset_id = sha[:16]
        canonical_path = paths[0]
        rel_path = canonical_path.relative_to(root).as_posix()
        rel_paths = sorted(p.relative_to(root).as_posix() for p in paths)

        file_bytes = canonical_path.stat().st_size
        suffix = canonical_path.suffix.lower()
        kind = "vid" if suffix in VIDEO_EXTS else "img"

        if kind == "vid":
            w, h, duration_s = get_video_dimensions_and_duration(canonical_path)
        else:
            w, h = get_image_dimensions(canonical_path)
            duration_s = None

        # Tập hợp video_da_dung từ tất cả đường dẫn / tên tệp / ref
        used_plans: set[str] = set()
        for p in paths:
            rel = p.relative_to(root).as_posix()
            used_plans.update(plan_usages.get(rel, set()))
            used_plans.update(plan_usages.get(p.name, set()))
            if p.name.startswith("File:"):
                used_plans.update(plan_usages.get(p.name, set()))
            used_plans.update(plan_usages.get(f"File:{p.name}", set()))
            # Thử tên file bỏ dấu gạch dưới
            spaced = p.stem.replace("_", " ")
            used_plans.update(plan_usages.get(f"File:{spaced}{p.suffix}", set()))

        # Sidecar text
        sidecar_text = ""
        for p in paths:
            candidates = [
                p.with_suffix(p.suffix + ".json"),
                p.with_suffix(".json"),
                p.with_name(p.stem + ".source.json"),
            ]
            for sc in candidates:
                if sc.is_file():
                    try:
                        raw = sc.read_text(encoding="utf-8")
                        try:
                            sc_data = json.loads(raw)
                            if isinstance(sc_data, dict):
                                sidecar_text += " " + " ".join(str(v) for v in sc_data.values() if isinstance(v, (str, int, float)))
                            else:
                                sidecar_text += " " + str(sc_data)
                        except Exception:
                            sidecar_text += " " + raw
                    except Exception:
                        pass

        gb_prompt = ""
        gb_pv = None
        for p in paths:
            prel = p.relative_to(root).as_posix()
            if _is_grokbot_path(prel):
                meta = grokbot_meta_for_file(p, channels, prompt_cache, scenes_cache)
                if not gb_prompt and meta.get("prompt"):
                    gb_prompt = meta["prompt"]
                if gb_pv is None and meta.get("pham_vi"):
                    gb_pv = meta["pham_vi"]

        tag_text = sidecar_text + (" " + gb_prompt if gb_prompt else "")
        pham_vi, core_tags, domain_tags = extract_tags_and_pham_vi(
            rel_path,
            canonical_path.name,
            tag_text,
            sorted(used_plans),
            channels,
            taxonomy,
            core_lex,
            domain_lex,
        )
        if gb_pv:
            pham_vi = gb_pv
        for st in style_tags_from_prompt(gb_prompt):
            if st not in core_tags:
                core_tags.append(st)
        core_tags = sorted(set(core_tags))

        source, license_info, ai_generated, strip_mark = parse_source_and_license(canonical_path, rel_path)

        try:
            hashes = media_phashes(canonical_path, kind, duration_s)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            hash_errors.append({"path": rel_path, "error": str(exc)})
            hashes = []
        comparison = asset_records + [r for r in old_records if r.get("sha256") != sha and r.get("sha256") not in by_sha]
        match = near_match(hashes, comparison, near_threshold, root) if hashes and not allow_near else None
        if match:
            rejected_near.append({"path": rel_path, "near_id": match["asset_id"]})
            continue

        record = {
            "phash": hashes[0] if kind == "img" and hashes else hashes,
            "schema_version": SCHEMA_VERSION,
            "asset_id": asset_id,
            "kind": kind,
            "path": rel_path,
            "paths": rel_paths,
            "sha256": sha,
            "byte": file_bytes,
            "w": w,
            "h": h,
            "duration_s": duration_s,
            "fps": None,
            "pham_vi": pham_vi,
            "tags": {
                "core": core_tags,
                "domain": domain_tags,
            },
            "source": source,
            "license": license_info,
            "ai_generated": ai_generated,
            "strip_mark": strip_mark,
            "video_da_dung": sorted(used_plans),
            "host": None,
            "path_kind": "local",
            "prompt": gb_prompt or None,
        }
        previous = old_by_sha.get(sha, {})
        for key in ("remote_path", "video_da_dung"):
            if key in previous:
                record[key] = previous[key]
        asset_records.append(record)

    # 4. Sắp xếp tất định theo asset_id và ghi manifest
    asset_records.extend(r for r in old_records if r.get("remote_path") and r.get("sha256") not in by_sha)
    write_manifest(manifest_path, asset_records)

    dt = time.time() - t0

    # Thống kê
    by_kind = {}
    by_pv = {}
    by_lic = {}
    for r in asset_records:
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
        by_pv[r["pham_vi"]] = by_pv.get(r["pham_vi"], 0) + 1
        lic_type = r["license"]["type"]
        by_lic[lic_type] = by_lic.get(lic_type, 0) + 1

    grokbot_assets = sum(1 for r in asset_records if (r.get("source") or {}).get("type") == "grokbot")
    stats = {
        "near_rejected": rejected_near,
        "hash_errors": hash_errors,
        "total_files": len(found_files),
        "total_assets": len(asset_records),
        "duplicate_groups": len(found_files) - len(asset_records),
        "duration_seconds": round(dt, 2),
        "manifest_path": str(manifest_path),
        "by_kind": by_kind,
        "by_pham_vi": by_pv,
        "by_license": by_lic,
        "grokbot_files": len(grokbot_files),
        "grokbot_assets": grokbot_assets,
        "grokbot_skipped_batches": grokbot_skipped,
    }
    return stats


def load_manifest(manifest_path: Path = DEFAULT_MANIFEST) -> list[dict]:
    """Đọc manifest.jsonl."""
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Không thấy manifest tại {manifest_path}; hãy chạy 'assets.py scan' trước.")
    records = []
    with open(manifest_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def find_assets(
    pham_vi: str | None = None,
    tag: str | None = None,
    kind: str | None = None,
    min_w: int | None = None,
    chua_dung_trong: str | None = None,
    manifest_path: Path = DEFAULT_MANIFEST,
    top: int | None = None,
    exclude_used_days: int | None = None,
    channel: str | None = None,
    today: date | None = None,
    channels_dir: Path | None = None,
    root: Path | None = None,
    max_uses: int | None = None, min_gap_days: int | None = None,
) -> list[dict]:
    """Tìm kiếm: kênh trước, rồi chung (fallback). Áp kho_loc của kênh kể cả khi fallback."""
    records = load_manifest(manifest_path)
    filtered = []
    tag_norm = fold(tag) if tag else None
    search_pv = pham_vi or channel

    repo_root = root
    if repo_root is None:
        try:
            repo_root = manifest_path.resolve().parents[2]
        except Exception:
            repo_root = REPO_ROOT
    ch_dir = channels_dir or (repo_root / "library" / "channels")
    channels = load_channels(ch_dir)
    loc = kho_loc_for(search_pv, channels) if search_pv else {}
    usage_channel = channel or (pham_vi if pham_vi and pham_vi != "chung" else None)
    max_uses = loc.get("max_dung") if max_uses is None else max_uses
    min_gap_days = loc.get("cach_ngay") if min_gap_days is None else min_gap_days
    today_d = today or date.today()

    # Mở rộng từ đồng nghĩa cho tag tìm kiếm
    search_tags: set[str] = {tag_norm} if tag_norm else set()
    if tag_norm:
        for k, syns in ALIAS_KEYWORDS.items():
            if fold(k) == tag_norm or any(fold(s) == tag_norm for s in syns):
                search_tags.add(fold(k))
                for s in syns:
                    search_tags.add(fold(s))
    # Tag/đường dẫn lưu kiểu gạch dưới (nghien_muc), người tra gõ dấu cách ("nghiên mực"): khớp cả hai dạng.
    search_tags |= {t.replace(" ", "_") for t in search_tags} | {t.replace("_", " ") for t in search_tags}

    for r in records:
        # Lọc kind
        if kind and r.get("kind") != kind:
            continue

        # Lọc min_w
        if min_w and (r.get("w") or 0) < min_w:
            continue

        hang = "all"
        if search_pv:
            s = pham_vi_set(r)
            qset = expand_pham_vi_query(search_pv, channels)
            is_chung = "chung" in s
            is_kenh = bool((s & qset) - {"chung"})
            if search_pv == "chung":
                if not is_chung:
                    continue
                hang = "chung"
            else:
                if is_kenh:
                    hang = "kenh"
                elif is_chung:
                    hang = "chung"
                else:
                    continue

        if loc and not passes_kho_loc(r, loc):
            continue

        # Lọc chưa dùng trong plan
        if chua_dung_trong:
            used = r.get("video_da_dung") or []
            used_ids = []
            for u in used:
                if isinstance(u, str):
                    used_ids.append(u)
                elif isinstance(u, dict) and u.get("video_id"):
                    used_ids.append(str(u["video_id"]))
            if chua_dung_trong in used_ids:
                continue

        if exclude_used_days is not None and usage_channel:
            if usage_in_window(r, usage_channel, int(exclude_used_days), today_d):
                continue

        # Lọc tag
        uses = [u for u in (r.get("video_da_dung") or []) if isinstance(u, dict) and u.get("kenh") == usage_channel]
        if usage_channel and max_uses is not None and len(uses) >= int(max_uses):
            continue
        if usage_channel and min_gap_days is not None and any((d := parse_iso_date(u.get("ngay", ""))) and d <= today_d and (today_d - d).days < int(min_gap_days) for u in uses):
            continue
        score = 0
        if search_tags:
            tag_matched = False
            core_tags = [fold(t) for t in (r.get("tags") or {}).get("core") or []]
            domain_tags = [fold(t) for t in (r.get("tags") or {}).get("domain") or []]
            path_fold = fold(r.get("path") or "")
            ref_fold = fold((r.get("source") or {}).get("ref") or "")
            prompt_fold = fold(r.get("prompt") or "")

            for st in search_tags:
                if any(st in t for t in domain_tags):
                    tag_matched = True
                    score += 100
                if any(st in t for t in core_tags):
                    tag_matched = True
                    score += 50
                if st in path_fold or st in ref_fold or st in prompt_fold:
                    tag_matched = True
                    score += 30

            if not tag_matched:
                continue
        else:
            score = 10

        # Ưu tiên tính kênh cụ thể hơn chung
        if search_pv and hang == "kenh":
            score += 25

        # Ưu tiên giấy phép thương mại
        if (r.get("license") or {}).get("commercial_allowed"):
            score += 15

        # Điểm độ phân giải
        w = r.get("w") or 0
        h = r.get("h") or 0
        score += round((w * h) / 1000000, 3)

        row = dict(r)
        row["hang_pham_vi"] = hang
        filtered.append((0 if hang == "kenh" else 1, -score, row["asset_id"], row))

    # Thứ tự: kênh trước, rồi chung; trong nhóm điểm cao trước, tie-break asset_id
    filtered.sort(key=lambda item: (item[0], item[1], item[2]))
    results = [item[3] for item in filtered]
    if top is not None and top > 0:
        results = results[:top]
    return results


def check_assets(
    manifest_path: Path = DEFAULT_MANIFEST,
    root: Path = REPO_ROOT,
) -> dict:
    """Kiểm tra toàn vẹn tài sản: file mất, sha lệch, giấy phép unknown, ảnh AI chưa strip_mark."""
    records = load_manifest(manifest_path)
    missing_files = []
    sha_mismatches = []
    unknown_licenses = []
    ai_unstripped = []

    for r in records:
        aid = r.get("asset_id")
        expected_sha = r.get("sha256")
        paths = r.get("paths") or [r.get("path")]

        # 1. Kiểm tra tồn tại tệp và sha256 (bỏ qua path remote — file không có trên máy này)
        is_remote = (r.get("path_kind") == "remote")
        for rel in paths:
            full = root / rel
            if not full.is_file():
                if is_remote:
                    continue
                missing_files.append({"asset_id": aid, "path": rel, "error": "file_missing"})
            else:
                try:
                    actual_sha = sha256_file(full)
                    if actual_sha != expected_sha:
                        sha_mismatches.append({
                            "asset_id": aid,
                            "path": rel,
                            "expected_sha": expected_sha,
                            "actual_sha": actual_sha,
                        })
                except Exception as e:
                    missing_files.append({"asset_id": aid, "path": rel, "error": str(e)})

        # 2. Giấy phép unknown
        lic_type = str((r.get("license") or {}).get("type") or "").lower()
        if not lic_type or lic_type == "unknown":
            unknown_licenses.append({"asset_id": aid, "path": r.get("path")})

        # 3. Ảnh AI chưa strip_mark
        if r.get("ai_generated") and r.get("strip_mark") is False:
            ai_unstripped.append({"asset_id": aid, "path": r.get("path")})

    report = {
        "total_checked": len(records),
        "missing_files_count": len(missing_files),
        "sha_mismatches_count": len(sha_mismatches),
        "unknown_licenses_count": len(unknown_licenses),
        "ai_unstripped_count": len(ai_unstripped),
        "missing_files": missing_files,
        "sha_mismatches": sha_mismatches,
        "unknown_licenses": unknown_licenses,
        "ai_unstripped": ai_unstripped,
        "status": "PASS" if not missing_files and not sha_mismatches else "FAIL",
    }
    return report


class MissingAssetsError(FileNotFoundError):
    """Lỗi khi thiếu tài sản hoặc cache phụ thuộc render cho một plan."""

    def __init__(self, message: str, missing: list[dict] | None = None):
        super().__init__(message)
        self.missing = missing or []


def resolve_stock_image_cache(
    query: str,
    orientation: str = "portrait",
    root: Path = REPO_ROOT,
) -> tuple[Path, Path, bool]:
    """Lấy đường dẫn cache ảnh stock (img_*.jpg và img_*.source.json) qua hàm thật của stock_image.

    Ưu tiên gọi stock_image.cache_path_for nếu có; nếu chưa có thì tra cache qua hàm thật
    get_or_fetch_stock_image ở chế độ 'chỉ tra cache' (chặn fetch mạng).
    Trả về (image_path, sidecar_path, is_hit).
    """
    import stock_image

    if hasattr(stock_image, "cache_path_for"):
        cp = stock_image.cache_path_for(query, orientation=orientation)
        try:
            rel = cp.relative_to(stock_image.PROJECT_ROOT)
        except ValueError:
            rel = Path("chunks_cache") / "beat_assets" / cp.name
        img_p = root / rel
        return img_p, img_p.with_suffix(".source.json"), img_p.is_file()

    orig_cache_dir = stock_image.CACHE_DIR
    orig_search = stock_image.search
    stock_image.CACHE_DIR = root / "chunks_cache" / "beat_assets"
    stock_image.search = lambda *a, **kw: None
    try:
        real_p = stock_image.get_or_fetch_stock_image(query, orientation=orientation)
    finally:
        stock_image.CACHE_DIR = orig_cache_dir
        stock_image.search = orig_search

    if real_p is not None:
        return real_p, real_p.with_suffix(".source.json"), True

    # Khi cache trượt trên đĩa: tính đường dẫn mong đợi để ghi nhận file thiếu đúng tên/hash
    key = query if orientation == "portrait" else f"{query}|{orientation}"
    h = stock_image._query_hash(key)
    cp = root / "chunks_cache" / "beat_assets" / f"img_{h}.jpg"
    return cp, cp.with_suffix(".source.json"), False


def resolve_stock_video_cache(
    query: str,
    root: Path = REPO_ROOT,
) -> tuple[Path, bool]:
    """Lấy đường dẫn cache clip stock (vid_*.mp4) qua hàm thật của asset_generation.

    Ưu tiên gọi asset_generation.cache_path_for nếu có; nếu chưa có thì tra cache qua hàm thật
    get_or_fetch_stock_video ở chế độ 'chỉ tra cache' (chặn fetch clip mới).
    Trả về (video_path, is_hit).
    """
    import asset_generation

    if hasattr(asset_generation, "cache_path_for"):
        cp = asset_generation.cache_path_for(query)
        try:
            rel = cp.relative_to(REPO_ROOT)
        except ValueError:
            rel = Path("chunks_cache") / "beat_assets" / cp.name
        vid_p = root / rel
        return vid_p, vid_p.is_file()

    orig_cache_dir = asset_generation.ASSET_CACHE_DIR
    orig_script = getattr(asset_generation, "FETCH_STOCK_SCRIPT", None)
    asset_generation.ASSET_CACHE_DIR = root / "chunks_cache" / "beat_assets"
    asset_generation.FETCH_STOCK_SCRIPT = Path("/nonexistent_dummy_fetch_stock")
    try:
        real_p = asset_generation.get_or_fetch_stock_video(query)
    finally:
        asset_generation.ASSET_CACHE_DIR = orig_cache_dir
        if orig_script is not None:
            asset_generation.FETCH_STOCK_SCRIPT = orig_script

    if real_p is not None:
        return real_p, True

    # Khi cache trượt trên đĩa: tính đường dẫn mong đợi để ghi nhận file thiếu đúng tên/hash
    h = asset_generation._prompt_hash(query)
    cp = root / "chunks_cache" / "beat_assets" / f"vid_{h}.mp4"
    return cp, False


def manifest_for_plan(
    plan_id_or_path: str,
    root: Path = REPO_ROOT,
    out_format: str = "sha256",
    out_path: Path | None = None,
    check_missing: bool = True,
) -> list[dict]:
    """Xuất danh sách tệp + sha256 mà một plan cần (dùng cho rsync --files-from và sha256sum -c)."""
    target = plan_id_or_path.strip()
    plan_file: Path | None = None

    if Path(target).is_file():
        plan_file = Path(target)
        stem = plan_file.stem
        # Bỏ phần đuôi .render, .tts nếu có
        stem = re.sub(r"\.(render|tts|opts|script)$", "", stem)
    else:
        # Tìm trong output/cl_staging/long/out/
        cand = root / "output" / "cl_staging" / "long" / "out" / f"{target}.json"
        if cand.is_file():
            plan_file = cand
            stem = target
        else:
            # Thử tìm theo id trong plan_long_*.json
            for pf in (root / "output" / "cl_staging" / "long").glob("plan_long_*.json"):
                try:
                    data = json.loads(pf.read_text(encoding="utf-8"))
                    rows = data if isinstance(data, list) else [data]
                    for r in rows:
                        if isinstance(r, dict) and r.get("id") == target:
                            plan_file = pf
                            stem = target
                            break
                    if plan_file:
                        break
                except Exception:
                    pass

    if not plan_file or not plan_file.is_file():
        raise FileNotFoundError(f"Không tìm thấy plan cho định danh hoặc đường dẫn: {target}")

    # Thu thập tất cả các tệp phụ thuộc và danh sách tệp thiếu
    needed_files: set[Path] = set()
    missing_files: list[dict] = []

    if plan_file.is_file():
        needed_files.add(plan_file)

    # 1. Các file out liên quan đến plan
    out_dir = root / "output" / "cl_staging" / "long" / "out"
    clean_stem = stem
    if clean_stem.startswith("L_fs_"):
        short_stem = clean_stem.replace("L_fs_", "")
    elif clean_stem.startswith("L_bud_"):
        short_stem = clean_stem.replace("L_bud_", "")
    else:
        short_stem = clean_stem

    for f in out_dir.glob(f"{clean_stem}.*"):
        if f.is_file() and not f.name.endswith(".mp4"):
            needed_files.add(f)

    # 2. Tìm plan row đầy đủ
    target_row = None
    try:
        data = json.loads(plan_file.read_text(encoding="utf-8"))
        rows = data if isinstance(data, list) else [data]
        for r in rows:
            if isinstance(r, dict) and (r.get("id") == target or r.get("id") == clean_stem):
                target_row = r
                break
    except Exception:
        pass

    if target_row is None:
        for pf in (root / "output" / "cl_staging" / "long").glob("plan_long_*.json"):
            try:
                data = json.loads(pf.read_text(encoding="utf-8"))
                rows = data if isinstance(data, list) else [data]
                for r in rows:
                    if isinstance(r, dict) and (r.get("id") == target or r.get("id") == clean_stem):
                        target_row = r
                        needed_files.add(pf)
                        break
                if target_row:
                    break
            except Exception:
                pass

    if target_row is None:
        cand_out_json = out_dir / f"{clean_stem}.json"
        if cand_out_json.is_file():
            try:
                data = json.loads(cand_out_json.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    target_row = data
            except Exception:
                pass

    # 3. Thu thập TTS chunk cache từng câu/chunk
    script_lines = []
    if target_row and target_row.get("script"):
        script_lines = target_row["script"]
    elif (out_dir / f"{clean_stem}.txt").is_file():
        script_lines = (out_dir / f"{clean_stem}.txt").read_text(encoding="utf-8").splitlines()

    tts_spec = {}
    if target_row and target_row.get("tts"):
        tts_spec = target_row["tts"]
    elif (out_dir / f"{clean_stem}.tts.json").is_file():
        try:
            tts_spec = json.loads((out_dir / f"{clean_stem}.tts.json").read_text(encoding="utf-8"))
        except Exception:
            pass
    elif (out_dir / f"{clean_stem}.json").is_file():
        try:
            d_out = json.loads((out_dir / f"{clean_stem}.json").read_text(encoding="utf-8"))
            if isinstance(d_out, dict) and d_out.get("tts"):
                tts_spec = d_out["tts"]
        except Exception:
            pass

    if script_lines and tts_spec:
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        try:
            import hf_voice
            for i, line in enumerate(script_lines, 1):
                try:
                    text = hf_voice.clean(line)
                    spoken = hf_voice.spoken_text(text, tts_spec)
                    voice, vstyle, k, engine = hf_voice.line_cfg(tts_spec, i)
                    donor = hf_voice.line_donor(tts_spec, i, engine)
                    first_temp = hf_voice.line_temperature(tts_spec, i)
                    if hf_voice.uses_new_cache(tts_spec):
                        key = hf_voice.cache_key(engine, voice, vstyle, k, spoken, temperature=first_temp, donor=donor, text_mode=tts_spec.get("text_mode") or "production")
                    else:
                        key = hf_voice.cache_key(engine, voice, vstyle, k, spoken)
                    cp = root / "chunks_cache" / "voice_lines" / f"{key}.wav"
                    if cp.is_file():
                        needed_files.add(cp)
                    else:
                        missing_files.append({
                            "type": "tts_chunk",
                            "path": str(cp.relative_to(root)),
                            "line": i,
                            "key": key,
                            "text": spoken[:40],
                        })
                    sp = root / "chunks_cache" / "voice_lines" / f"{key}.suspect"
                    if sp.is_file():
                        needed_files.add(sp)
                except Exception as exc:
                    missing_files.append({
                        "type": "tts_error",
                        "error": str(exc),
                        "line": i,
                    })
        except Exception as exc:
            missing_files.append({
                "type": "tts_module_error",
                "error": str(exc),
            })

        for tts_aux in ("tts_lexicon.json", "tts_ruleset.json"):
            aux_p = root / tts_aux
            if aux_p.is_file():
                needed_files.add(aux_p)

    # 4. File media precheck trong hyperframes_short/assets/ và declared media
    hf_assets = root / "hyperframes_short" / "assets"
    media_files: set[Path] = set()
    if hf_assets.is_dir():
        for prefix in (f"precheck_{short_stem}_s", f"precheck_{clean_stem}_s", f"{clean_stem}_s"):
            for f in hf_assets.glob(f"{prefix}*.*"):
                if f.is_file():
                    needed_files.add(f)
                    media_files.add(f)

    if target_row:
        for m_dict in (target_row.get("media") or {}, target_row.get("visuals") or {}):
            if isinstance(m_dict, dict):
                for _k, v in m_dict.items():
                    if isinstance(v, dict):
                        if v.get("path"):
                            mp = root / v["path"]
                            if mp.is_file():
                                needed_files.add(mp)
                                media_files.add(mp)
                        if v.get("museum"):
                            safe_m = re.sub(r"[^\w]+", "_", v["museum"])
                            mp = root / "chunks_cache" / "museum" / f"{safe_m}.jpg"
                            if mp.is_file():
                                needed_files.add(mp)
                                media_files.add(mp)
                            sc = root / "chunks_cache" / "museum" / f"{safe_m}.json"
                            if sc.is_file():
                                needed_files.add(sc)
                        if v.get("file"):
                            safe_f = re.sub(r"[^\w.-]+", "_", v["file"].replace("File:", ""))[:120]
                            mp = root / "chunks_cache" / "commons" / f"{safe_f}.jpg"
                            if mp.is_file():
                                needed_files.add(mp)
                                media_files.add(mp)
                            sc = root / "chunks_cache" / "commons" / f"{safe_f}.json"
                            if sc.is_file():
                                needed_files.add(sc)
                        if v.get("query"):
                            raw_q = v.get("query", "").strip()
                            default_kind = "image" if m_dict is target_row.get("visuals") else "video"
                            kind = (v.get("kind") or default_kind).lower()
                            try:
                                import hyperframes_bridge as HB
                            except ImportError:
                                HB = None

                            stem_parts = clean_stem.split("_")
                            series_name = target_row.get("series") or (stem_parts[1] if clean_stem.startswith("L_") and len(stem_parts) > 1 else "CL")
                            domain = HB.SERIES_DOMAIN.get(str(series_name).lower(), "CL") if HB else "CL"
                            row_style = target_row.get("style", "studio_long")
                            orientation = "landscape" if row_style.endswith(("_wide", "_long")) or (HB and row_style in getattr(HB, "LONG_STYLES", ())) else "portrait"
                            query = HB.sanitize_query(raw_q, domain) if HB else raw_q

                            if kind == "image":
                                cp, sp, is_hit = resolve_stock_image_cache(query, orientation=orientation, root=root)
                                if is_hit:
                                    needed_files.add(cp)
                                    media_files.add(cp)
                                else:
                                    missing_files.append({
                                        "type": "stock_image",
                                        "path": str(cp.relative_to(root)),
                                        "sentence_id": _k,
                                        "query": query,
                                    })
                                if sp.is_file():
                                    needed_files.add(sp)
                                else:
                                    missing_files.append({
                                        "type": "stock_image_meta",
                                        "path": str(sp.relative_to(root)),
                                        "sentence_id": _k,
                                        "query": query,
                                    })
                            elif kind == "video":
                                cp, is_hit = resolve_stock_video_cache(query, root=root)
                                if is_hit:
                                    needed_files.add(cp)
                                    media_files.add(cp)
                                else:
                                    missing_files.append({
                                        "type": "stock_video",
                                        "path": str(cp.relative_to(root)),
                                        "sentence_id": _k,
                                        "query": query,
                                    })

    # 5. Phụ thuộc cache 2.5D / depth và relic
    # Với ảnh có layout: depth, tính khoá theo đúng file mà bridge đưa vào split_depth
    # (tái dùng hàm _frame_local_image của bridge, không chép logic)
    if target_row:
        import tempfile
        try:
            import hyperframes_bridge as HB
        except ImportError:
            HB = None

        row_style = target_row.get("style", "studio_long")
        is_landscape = row_style.endswith(("_wide", "_long"))

        for m_dict in (target_row.get("media") or {}, target_row.get("visuals") or {}):
            if isinstance(m_dict, dict):
                for sid_k, v in m_dict.items():
                    if not isinstance(v, dict):
                        continue
                    layout = (v.get("layout") or "").lower()
                    preset = v.get("preset") or ""
                    shots = v.get("shots") or []
                    wants_depth = layout == "depth" or preset == "parallax" or any(
                        isinstance(s, dict) and s.get("preset") == "parallax" for s in shots
                    )
                    if wants_depth:
                        # 1) Kiểm tra file precheck / asset trong hyperframes_short/assets/
                        cand = None
                        for pref_name in (
                            f"{clean_stem}_s{sid_k}.jpg",
                            f"{clean_stem}_s{sid_k}.png",
                            f"precheck_{short_stem}_s{sid_k}.jpg",
                            f"precheck_{short_stem}_s{sid_k}.png",
                            f"precheck_{clean_stem}_s{sid_k}.jpg",
                            f"precheck_{clean_stem}_s{sid_k}.png",
                            f"{short_stem}_s{sid_k}.jpg",
                            f"{short_stem}_s{sid_k}.png",
                        ):
                            p_cand = hf_assets / pref_name
                            if p_cand.is_file():
                                cand = p_cand
                                break

                        target_bytes = None
                        if cand is not None:
                            try:
                                target_bytes = cand.read_bytes()
                            except Exception:
                                pass
                        elif v.get("path") and HB is not None:
                            src_p = root / v["path"]
                            if src_p.is_file():
                                try:
                                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tf:
                                        tmp_p = Path(tf.name)
                                    HB._frame_local_image(src_p, tmp_p, crop=v.get("crop"), landscape=is_landscape)
                                    if tmp_p.is_file():
                                        target_bytes = tmp_p.read_bytes()
                                    tmp_p.unlink(missing_ok=True)
                                except Exception:
                                    pass

                        if target_bytes:
                            dkey = hashlib.sha1(target_bytes).hexdigest()[:16]
                            for dext in ("_bg.jpg", "_fg.png", ".cover"):
                                df = root / "chunks_cache" / "depth" / f"{dkey}{dext}"
                                if df.is_file():
                                    needed_files.add(df)

    for mf in list(media_files):
        try:
            mbytes = mf.read_bytes()
            mkey = hashlib.sha1(mbytes).hexdigest()[:16]
            for dext in ("_bg.jpg", "_fg.png", ".cover"):
                df = root / "chunks_cache" / "depth" / f"{mkey}{dext}"
                if df.is_file():
                    needed_files.add(df)
            rkey = hashlib.sha1(mbytes + b"3").hexdigest()[:16]
            for rext in ("_bg.jpg", "_fg.png", "_sketch.png", ".json"):
                rf = root / "chunks_cache" / "relic" / f"{rkey}{rext}"
                if rf.is_file():
                    needed_files.add(rf)
                rf_old = root / "chunks_cache" / "relic" / f"{mkey}{rext}"
                if rf_old.is_file():
                    needed_files.add(rf_old)
        except Exception:
            pass

    # 6. Phân tích nhạc BGM (bgm_ledger.json, render.json, sound spec)
    ledger_file = root / "output" / "cl_staging" / "long" / "bgm_ledger.json"
    if ledger_file.is_file():
        needed_files.add(ledger_file)
        try:
            ld = json.loads(ledger_file.read_text(encoding="utf-8"))
            for stem_key in (clean_stem, target, short_stem, f"L_fs_{short_stem}", f"L_bud_{short_stem}"):
                if stem_key in ld:
                    info = ld[stem_key]
                    for track in (info.get("pool") or []) + (info.get("used") or []):
                        if track:
                            bp = root / track if not Path(track).is_absolute() else Path(track)
                            if not bp.is_file():
                                bp = root / "bgm" / Path(track).name
                            if bp.is_file():
                                needed_files.add(bp)
                            else:
                                missing_files.append({"type": "bgm", "path": str(bp.relative_to(root)) if bp.is_relative_to(root) else str(bp)})
                    break
        except Exception:
            pass

    render_json = out_dir / f"{clean_stem}.render.json"
    if render_json.is_file():
        try:
            rd = json.loads(render_json.read_text(encoding="utf-8"))
            for b in rd.get("bgm_used") or []:
                bp = root / "bgm" / b
                if bp.is_file():
                    needed_files.add(bp)
                else:
                    missing_files.append({"type": "bgm", "path": f"bgm/{b}"})
            if rd.get("bgm"):
                bp = Path(rd["bgm"])
                if not bp.is_absolute():
                    bp = root / bp
                if bp.is_file():
                    needed_files.add(bp)
                else:
                    missing_files.append({"type": "bgm", "path": str(bp.relative_to(root)) if bp.is_relative_to(root) else str(bp)})
        except Exception:
            pass

    if target_row and target_row.get("sound"):
        snd = target_row["sound"]
        if isinstance(snd, dict) and snd.get("bgm"):
            bp = root / "bgm" / snd["bgm"]
            if bp.is_file():
                needed_files.add(bp)
            else:
                missing_files.append({"type": "bgm", "path": f"bgm/{snd['bgm']}"})

    # 7. Cấu hình sound & foley theo kênh (sound: foley-v1 là procedural, không có file sfx)
    series = None
    if target_row and target_row.get("series"):
        series = str(target_row["series"]).strip().lower()
    elif "fs" in clean_stem:
        series = "fs"
    elif "bud" in clean_stem:
        series = "bud"

    if series:
        ch_yaml = root / "library" / "channels" / f"{series}.yaml"
        if ch_yaml.is_file():
            needed_files.add(ch_yaml)

    # 8. Font và Asset composition (HyperFrames studio / studio_long)
    style = target_row.get("style", "studio_long") if target_row else "studio_long"
    comp_file = root / "hyperframes_short" / "compositions" / f"{style}.html"
    if comp_file.is_file():
        needed_files.add(comp_file)

    comp_dir = root / "hyperframes_short" / "compositions"
    for comp_dep in ("base.css", "wide.css", "longform.css", "engine.js", "longform.js"):
        cf = comp_dir / comp_dep
        if cf.is_file():
            needed_files.add(cf)

    prof_file = root / "domain_creative_profiles.json"
    if prof_file.is_file():
        needed_files.add(prof_file)

    theme_id = (target_row.get("theme") if target_row else None) or "son-mai"
    if theme_id:
        th_file = root / "hyperframes_short" / "studio" / "themes" / f"{theme_id}.json"
        if th_file.is_file():
            needed_files.add(th_file)
            try:
                th_data = json.loads(th_file.read_text(encoding="utf-8"))
                fams = set()
                for k, v in th_data.get("vars", {}).items():
                    if k.startswith("font-"):
                        fams |= set(re.findall(r'"([^"]+)"', v))
                faces_file = root / "hyperframes_short" / "studio" / "fonts" / "faces.json"
                if faces_file.is_file():
                    needed_files.add(faces_file)
                    faces = json.loads(faces_file.read_text(encoding="utf-8"))
                    for fc in faces:
                        if fc.get("family") in fams:
                            ff = root / "hyperframes_short" / "studio" / fc["file"]
                            if ff.is_file():
                                needed_files.add(ff)
            except Exception:
                pass

        for st_file in ("base.css", "kit.css", "core.js"):
            sf = root / "hyperframes_short" / "studio" / st_file
            if sf.is_file():
                needed_files.add(sf)

        devices_dir = root / "hyperframes_short" / "studio" / "devices"
        if devices_dir.is_dir():
            for dev in devices_dir.glob("*.js"):
                if dev.is_file():
                    needed_files.add(dev)

    # Kiểm tra danh sách tệp thiếu
    if check_missing and missing_files:
        raise MissingAssetsError(
            f"Thiếu {len(missing_files)} file phụ thuộc render cho plan {target}",
            missing=missing_files,
        )

    # Tính sha256 cho từng tệp
    results = []
    for f in sorted(needed_files):
        try:
            rel = f.relative_to(root).as_posix()
            h = hashlib.sha256()
            with open(f, "rb") as fp:
                while chunk := fp.read(65536):
                    h.update(chunk)
            results.append({
                "path": rel,
                "sha256": h.hexdigest(),
                "byte": f.stat().st_size,
            })
        except Exception:
            pass

    # Sắp xếp theo đường dẫn tương đối
    results.sort(key=lambda x: x["path"])

    # Ghi file nếu có out_path
    if out_path:
        out_p = Path(out_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        if out_p.suffix == ".json" or out_format == "json":
            out_p.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        elif out_format == "files":
            out_p.write_text("\n".join(r["path"] for r in results) + "\n", encoding="utf-8")
        else:
            # sha256 format
            lines = [f"{r['sha256']}  {r['path']}" for r in results]
            out_p.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return results


class NearDuplicateError(ValueError):
    def __init__(self, asset_id: str):
        self.asset_id = asset_id
        super().__init__(f"Near duplicate asset: {asset_id}")


def add_asset(
    file_path: str | Path,
    pham_vi: str,
    prompt: str = "",
    tags: list[str] | None = None,
    root: Path = REPO_ROOT,
    manifest_path: Path = DEFAULT_MANIFEST,
    ai: bool | None = None,
    near_threshold: int = 8, allow_near: bool = False,
    reject_existing: bool = False,
) -> dict:
    """Nhập 1 ảnh đã soát vào manifest; không copy/di chuyển file gốc.

    `ai`: True/False ghi rõ ảnh AI hay ảnh thật. None = tự đoán: chỉ coi là AI khi
    có prompt VÀ không đọc được nguồn thật (sidecar) — prompt mô tả ảnh thật không làm đổi cờ.
    """
    src = Path(file_path)
    if not src.is_file():
        raise FileNotFoundError(f"Không thấy file: {src}")
    channels = load_channels(root / "library" / "channels")
    valid = set(pham_vi_hop_le(channels))
    if pham_vi not in valid:
        raise ValueError(f"pham_vi không hợp lệ: {pham_vi}. Hợp lệ: {', '.join(valid)}")

    src_res = src.resolve()
    root_res = root.resolve()
    try:
        rel_path = src_res.relative_to(root_res).as_posix()
    except ValueError:
        raise ValueError(f"File phải nằm trong repo root ({root_res})") from None

    sha = sha256_file(src_res)
    asset_id = sha[:16]
    suffix = src_res.suffix.lower()
    kind = "vid" if suffix in VIDEO_EXTS else "img"
    if kind == "vid":
        w, h, duration_s = get_video_dimensions_and_duration(src_res)
    else:
        w, h = get_image_dimensions(src_res)
        duration_s = None

    extra_tags = [fold(t).replace(" ", "_") for t in (tags or []) if str(t).strip()]
    taxonomy = load_taxonomy(root / "library" / "inventory" / "taxonomy.json")
    core_lex, domain_lex = load_lexicon(root / "library" / "assets" / "lexicon")
    tag_text = (prompt or "") + " " + " ".join(extra_tags)
    pv_guess, core_tags, domain_tags = extract_tags_and_pham_vi(
        rel_path, src_res.name, tag_text, [], channels, taxonomy, core_lex, domain_lex,
    )
    for t in extra_tags:
        if t and t not in core_tags:
            core_tags.append(t)
    for st in style_tags_from_prompt(prompt or ""):
        if st not in core_tags:
            core_tags.append(st)
    core_tags = sorted(set(core_tags))
    domain_tags = sorted(set(domain_tags))

    source, license_info, ai_generated, strip_mark = parse_source_and_license(src_res, rel_path)
    if ai is None:
        ai = bool(prompt) and source.get("type") == "unknown"
    if ai:
        ai_generated = True
        if source.get("type") == "unknown":
            source["type"] = "grokbot"
            license_info["type"] = "AI Generated (Internal License)"
            license_info["commercial_allowed"] = True
            license_info["basis"] = "sidecar"
            license_info["basis_ref"] = "LEAD_DA_XEM"

    records: list[dict] = []
    if manifest_path.is_file():
        records = load_manifest(manifest_path)
    by_sha = {r["sha256"]: r for r in records}

    if reject_existing and sha in by_sha:
        raise NearDuplicateError(by_sha[sha]["asset_id"])
    hashes = media_phashes(src_res, kind, duration_s)
    if sha not in by_sha and not allow_near:
        match = near_match(hashes, records, near_threshold, root)
        if match:
            raise NearDuplicateError(match["asset_id"])

    if sha in by_sha:
        rec = by_sha[sha]
        paths = list(rec.get("paths") or [rec.get("path")])
        if rel_path not in paths:
            paths.append(rel_path)
            rec["paths"] = sorted(paths)
        rec["pham_vi"] = pham_vi
        if prompt:
            rec["prompt"] = prompt
        rec_core = list((rec.get("tags") or {}).get("core") or [])
        rec_domain = list((rec.get("tags") or {}).get("domain") or [])
        rec["tags"] = {
            "core": sorted(set(rec_core + core_tags)),
            "domain": sorted(set(rec_domain + domain_tags)),
        }
        rec["ai_generated"] = rec.get("ai_generated") or ai_generated
        write_manifest(manifest_path, list(by_sha.values()))
        return rec

    rec = {
        "phash": hashes[0] if kind == "img" else hashes,
        "schema_version": SCHEMA_VERSION,
        "asset_id": asset_id,
        "kind": kind,
        "path": rel_path,
        "paths": [rel_path],
        "sha256": sha,
        "byte": src_res.stat().st_size,
        "w": w,
        "h": h,
        "duration_s": duration_s,
        "fps": None,
        "pham_vi": pham_vi or pv_guess or "chung",
        "tags": {"core": core_tags, "domain": domain_tags},
        "source": source,
        "license": license_info,
        "ai_generated": ai_generated,
        "strip_mark": strip_mark,
        "video_da_dung": [],
        "host": None,
        "path_kind": "local",
        "prompt": prompt or None,
    }
    records.append(rec)
    write_manifest(manifest_path, records)
    return rec


def mark_used(
    asset_id: str,
    video_id: str,
    kenh: str,
    ngay: str,
    manifest_path: Path = DEFAULT_MANIFEST,
    ngay_public: str | None = None,
) -> dict:
    """Ghi nhận tài sản đã dùng trên kênh/ngày (phục vụ find --exclude-used-days)."""
    if parse_iso_date(ngay) is None:
        raise ValueError(f"Ngày không hợp lệ (YYYY-MM-DD): {ngay}")
    records = load_manifest(manifest_path)
    found = None
    for r in records:
        if r.get("asset_id") == asset_id:
            found = r
            break
    if found is None:
        raise KeyError(f"Không thấy asset_id {asset_id} trong manifest")
    if ngay_public is not None and parse_iso_date(ngay_public) is None:
        raise ValueError(f"Ngày public không hợp lệ (YYYY-MM-DD): {ngay_public}")
    entry = {"video_id": str(video_id), "kenh": str(kenh), "ngay": str(ngay)[:10]}
    used = list(found.get("video_da_dung") or [])
    if ngay_public:   # ghi/ cập nhật ngày public cho lần dùng đã có (prune cần bằng chứng public)
        for x in used:
            if isinstance(x, dict) and x.get("video_id") == entry["video_id"] and x.get("kenh") == entry["kenh"]:
                x["ngay_public"] = ngay_public[:10]
        entry["ngay_public"] = ngay_public[:10]

    def _same(x: Any) -> bool:
        return isinstance(x, dict) and x.get("video_id") == entry["video_id"] and x.get("kenh") == entry["kenh"] and x.get("ngay") == entry["ngay"]

    if not any(_same(x) for x in used):
        used.append(entry)
    found["video_da_dung"] = used
    write_manifest(manifest_path, records)
    return found


def merge_external(
    external_manifest: Path,
    pham_vi: str,
    host: str,
    manifest_path: Path = DEFAULT_MANIFEST,
    root: Path = REPO_ROOT,
) -> dict:
    """Gộp manifest ngoài (Mimck) theo cùng schema. Không chép file. Trùng sha256 thì gộp."""
    channels = load_channels(root / "library" / "channels")
    valid = set(pham_vi_hop_le(channels))
    if pham_vi not in valid:
        raise ValueError(f"pham_vi không hợp lệ: {pham_vi}. Hợp lệ: {', '.join(valid)}")
    ext_path = Path(external_manifest)
    if not ext_path.is_file():
        raise FileNotFoundError(f"Không thấy manifest ngoài: {ext_path}")

    existing: list[dict] = load_manifest(manifest_path) if manifest_path.is_file() else []
    by_sha: dict[str, dict] = {r["sha256"]: r for r in existing if r.get("sha256")}
    incoming: list[dict] = []
    with open(ext_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                incoming.append(json.loads(line))

    added = 0
    merged = 0
    for rec in incoming:
        sha = rec.get("sha256")
        if not sha:
            continue
        incoming_copy = dict(rec)
        # Giữ nguyên ai_generated, license, source của bản ngoài
        incoming_copy["host"] = host
        incoming_copy["path_kind"] = "remote"
        incoming_copy["pham_vi"] = pham_vi
        incoming_copy.setdefault("schema_version", SCHEMA_VERSION)
        incoming_copy.setdefault("video_da_dung", [])
        if sha in by_sha:
            old = by_sha[sha]
            paths = list(old.get("paths") or ([old.get("path")] if old.get("path") else []))
            new_path = incoming_copy.get("path")
            if new_path and new_path not in paths:
                paths.append(new_path)
            old["paths"] = sorted(str(p) for p in paths if p)
            old_used = list(old.get("video_da_dung") or [])
            for u in incoming_copy.get("video_da_dung") or []:
                if u not in old_used:
                    old_used.append(u)
            old["video_da_dung"] = old_used
            hosts = list(old.get("hosts") or [])
            old_host = old.get("host")
            if old_host and old_host not in hosts:
                hosts.append(old_host)
            if "local" not in hosts and (old.get("path_kind") or "local") == "local":
                hosts.append("local")
            if host not in hosts:
                hosts.append(host)
            old["hosts"] = hosts
            if old.get("path_kind") != "local" and not old.get("path"):
                old["path_kind"] = "remote"
                old["host"] = host
            merged += 1
        else:
            if not incoming_copy.get("asset_id"):
                incoming_copy["asset_id"] = sha[:16]
            by_sha[sha] = incoming_copy
            added += 1

    write_manifest(manifest_path, list(by_sha.values()))
    return {"added": added, "merged": merged, "total": len(by_sha), "manifest_path": str(manifest_path)}


def remote_base() -> str:
    remote = os.environ.get("ASSET_REMOTE", "").strip()
    if not remote:
        raise ValueError("Missing ASSET_REMOTE environment variable")
    root = os.environ.get("ASSET_REMOTE_ROOT", "creator-assets").strip().strip("/")
    return remote.rstrip("/") + ("/" if not remote.endswith(":") else "") + root


def remote_url(remote_path: str) -> str:
    """remote_path trong manifest chỉ là khóa tương đối (repo public: không ghi tên remote). Bản cũ có ':' thì dùng nguyên."""
    return remote_path if ":" in remote_path else remote_base() + "/" + remote_path.lstrip("/")



def parse_ingest_prompts(path: Path) -> dict[str, dict]:
    """Parse prompts and groups from filename headings."""
    result: dict[str, dict] = {}
    current = None
    heading = re.compile(r"^##\s+(\S+\.(?:png|jpe?g|webp|gif|mp4|mov|webm|m4v))\s*(?:\u2014|\u2013|-)\s*(.*?)\s*$", re.I)
    prompt_line = re.compile(r"^\s*[-*]\s*Prompt\s*\(ti\u1ebfng Anh\)\s*:\s*(.*)$", re.I)
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        match = heading.match(line)
        if match:
            current = match.group(1)
            group = match.group(2).strip().upper()
            result[current] = {"prompt": "", "tags": PROMPT_GROUP_TAGS.get(group, [])}
        elif line.startswith("## "):
            current = None
        elif current is not None:
            match = prompt_line.match(line)
            if match:
                result[current]["prompt"] = match.group(1).strip()
    return result


def ingest_dir(directory: Path, pham_vi: str, *, ai: bool | None = None,
               tags: list[str] | None = None, prompts_path: Path | None = None,
               push: bool = False, near_threshold: int = 8, dry_run: bool = False,
               root: Path = REPO_ROOT, manifest_path: Path = DEFAULT_MANIFEST) -> dict:
    if not directory.is_dir():
        raise NotADirectoryError(f"Directory not found: {directory}")
    prompts = parse_ingest_prompts(prompts_path) if prompts_path else {}
    result = {"added": [], "near_duplicates": [], "errors": [], "pushed": []}

    def ingest(active_manifest: Path) -> None:
        for path in sorted(directory.iterdir(), key=lambda p: p.name):
            if not path.is_file() or path.suffix.lower() not in MEDIA_EXTS:
                continue
            info = prompts.get(path.name, {})
            try:
                rec = add_asset(path, pham_vi, prompt=info.get("prompt", ""),
                                tags=(tags or []) + info.get("tags", []), root=root,
                                manifest_path=active_manifest, ai=ai,
                                near_threshold=near_threshold, reject_existing=True)
                result["added"].append({"path": str(path), "asset_id": rec["asset_id"]})
            except NearDuplicateError as exc:
                result["near_duplicates"].append({"path": str(path), "near_id": exc.asset_id})
            except (ValueError, OSError, subprocess.SubprocessError) as exc:
                result["errors"].append({"path": str(path), "error": str(exc)})

    if dry_run:
        with tempfile.TemporaryDirectory() as tmp:
            temporary_manifest = Path(tmp) / "manifest.jsonl"
            if manifest_path.is_file():
                temporary_manifest.write_bytes(manifest_path.read_bytes())
            ingest(temporary_manifest)
    else:
        ingest(manifest_path)
        if push:
            for item in result["added"]:
                try:
                    result["pushed"].extend(push_assets([item["asset_id"]], False, manifest_path, root))
                except (ValueError, OSError, subprocess.SubprocessError) as exc:
                    result["errors"].append({"path": item["path"], "error": f"push: {exc}"})
    return result


def remote_sha(path: str) -> str:
    result = subprocess.run(["rclone", "hashsum", "SHA-256", path], capture_output=True, text=True, check=True)
    parts = result.stdout.strip().split()
    if not parts or not re.fullmatch(r"[0-9a-fA-F]{64}", parts[0]):
        raise ValueError(f"Remote does not provide SHA-256 for {path}")
    return parts[0].lower()


def push_assets(ids: list[str], all_local: bool, manifest_path: Path, root: Path) -> list[str]:
    base = remote_base()
    records = load_manifest(manifest_path)
    selected = [r for r in records if r.get("asset_id") in ids or (all_local and (root / r["path"]).is_file())]
    missing = set(ids) - {r["asset_id"] for r in selected}
    if missing:
        raise ValueError(f"Asset not found: {', '.join(sorted(missing))}")
    done = []
    for r in selected:
        local = root / r["path"]
        if sha256_file(local) != r["sha256"]:
            raise ValueError(f"Local SHA mismatch: {r['asset_id']}")
        key = r["sha256"] + local.suffix.lower()
        dest = base + "/" + key
        subprocess.run(["rclone", "copyto", str(local), dest], check=True, capture_output=True)
        if remote_sha(dest) != r["sha256"]:
            raise ValueError(f"Remote SHA mismatch: {r['asset_id']}")
        r["remote_path"] = key
        write_manifest(manifest_path, records)
        done.append(r["asset_id"])
    return done


def _plan_values(data: Any) -> set[str]:
    if isinstance(data, dict):
        return set().union(*(_plan_values(v) for v in data.values())) if data else set()
    if isinstance(data, list):
        return set().union(*(_plan_values(v) for v in data)) if data else set()
    return {str(data)} if isinstance(data, str) else set()


def pull_assets(ids: list[str], plan: str | None, manifest_path: Path, root: Path) -> list[str]:
    remote_base()
    records = load_manifest(manifest_path)
    if plan:
        path = Path(plan)
        if not path.is_file():
            path = root / plan
        if not path.is_file():
            raise FileNotFoundError(f"Plan not found: {plan}")
        values = _plan_values(json.loads(path.read_text(encoding="utf-8")))
        ids = [r["asset_id"] for r in records if r["asset_id"] in values or any(str(p) in values for p in r.get("paths", [r.get("path")]))]
    missing = set(ids) - {r["asset_id"] for r in records}
    if missing:
        raise ValueError(f"Asset not found: {', '.join(sorted(missing))}")
    cache = Path(os.environ.get("ASSET_CACHE", str(root / "output" / "asset_cache")))
    cache.mkdir(parents=True, exist_ok=True)
    done = []
    for r in records:
        if r["asset_id"] not in ids:
            continue
        if not r.get("remote_path"):
            raise ValueError(f"Missing remote_path: {r['asset_id']}")
        dest = cache / (r["sha256"] + Path(r["path"]).suffix.lower())
        temp = dest.with_suffix(dest.suffix + ".part")
        try:
            subprocess.run(["rclone", "copyto", remote_url(r["remote_path"]), str(temp)], check=True, capture_output=True)
            if sha256_file(temp) != r["sha256"]:
                raise ValueError(f"Downloaded SHA mismatch: {r['asset_id']}")
            temp.replace(dest)
        finally:
            if temp.exists():
                temp.unlink()
        done.append(str(dest))
    return done


def prune_assets(manifest_path: Path, root: Path, yes: bool = False, today: date | None = None) -> list[dict]:
    remote_base()
    records = load_manifest(manifest_path)
    today = today or date.today()
    # Treat every discovered plan as active; ambiguity must never cause deletion.
    values: set[str] = set()
    plan_dir = root / "output"
    if plan_dir.exists():
        for plan in plan_dir.rglob("*plan*.json"):
            try:
                values.update(_plan_values(json.loads(plan.read_text(encoding="utf-8"))))
            except (OSError, ValueError):
                raise ValueError(f"Cannot read plan: {plan}") from None
    decisions = []
    for r in records:
        path = root / r["path"]
        if not path.resolve().is_relative_to(root.resolve()) or path.is_symlink() or not path.is_file() or not r.get("remote_path"):
            continue
        paths = r.get("paths") or [r["path"]]
        if r["asset_id"] in values or any(str(p) in values or Path(p).name in values for p in paths):
            continue
        uses = r.get("video_da_dung") or []
        # Asset chưa dùng: Drive có bản khớp sha là đủ để xóa bản trên máy.
        # Đã dùng: mọi lần dùng phải có ngay_public quá 7 ngày; mục cũ dạng chuỗi hoặc thiếu ngày thì giữ.
        if uses and any(not isinstance(u, dict) or not parse_iso_date(u.get("ngay_public", "")) for u in uses):
            continue
        if uses and any((today - parse_iso_date(u["ngay_public"])).days <= 7 for u in uses):
            continue
        try:
            if sha256_file(path) != r["sha256"] or remote_sha(remote_url(r["remote_path"])) != r["sha256"]:
                continue
        except (OSError, ValueError, subprocess.SubprocessError):
            continue
        decisions.append({"asset_id": r["asset_id"], "path": str(path), "deleted": yes})
        if yes:
            path.unlink()
    return decisions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="VietNeu Asset Catalog Tool (#47, #95, #142)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: scan
    scan_p = subparsers.add_parser("scan", help="Quét kho tài sản và ghi manifest.jsonl tất định")
    scan_p.add_argument("--root", type=Path, default=REPO_ROOT, help="Thư mục gốc repo")
    scan_p.add_argument("--out", type=Path, default=DEFAULT_MANIFEST, help="Đường dẫn file manifest.jsonl")
    scan_p.add_argument("--dirs", type=str, help="Danh sách thư mục phân cách bằng dấu phẩy")

    # Subcommand: find
    find_p = subparsers.add_parser("find", help="Tra cứu tài sản tất định (kênh trước, chung fallback)")
    find_p.add_argument("--pham-vi", type=str, help="Lọc theo kênh (id trong channels/*.yaml) hoặc chung")
    find_p.add_argument("--channel", type=str, help="Alias --pham-vi; dùng với --exclude-used-days")
    find_p.add_argument("--tag", type=str, help="Tag từ khoá cần tìm")
    find_p.add_argument("--kind", choices=["img", "vid"], help="Loại tài sản: img hoặc vid")
    find_p.add_argument("--min-w", type=int, help="Chiều rộng tối thiểu (pixel)")
    find_p.add_argument("--chua-dung-trong", type=str, help="Loại trừ tài sản đã dùng trong plan này")
    find_p.add_argument("--exclude-used-days", type=int, help="Loại ảnh đã dùng trên kênh trong N ngày (video_da_dung)")
    find_p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Đường dẫn manifest.jsonl")
    find_p.add_argument("--root", type=Path, default=REPO_ROOT, help="Repo root (đọc channels/kho_loc)")
    find_p.add_argument("--top", type=int, default=10, help="Số lượng kết quả tối đa")
    find_p.add_argument("--json", action="store_true", help="Xuất kết quả định dạng JSON")

    # Subcommand: add
    add_p = subparsers.add_parser("add", help="Nhập 1 ảnh đã soát vào manifest (không copy file)")
    add_p.add_argument("file", type=Path, help="Đường dẫn file ảnh/video trong repo")
    add_p.add_argument("--pham-vi", required=True, type=str, help="Kênh hoặc chung")
    add_p.add_argument("--prompt", default="", type=str, help="Prompt gốc nếu ảnh AI")
    ai_grp = add_p.add_mutually_exclusive_group()
    ai_grp.add_argument("--ai", dest="ai", action="store_true", default=None, help="Ảnh do AI tạo")
    ai_grp.add_argument("--real", dest="ai", action="store_false", help="Ảnh thật (prompt chỉ để mô tả)")
    add_p.add_argument("--tags", default="", type=str, help="Tag thêm, phân cách bằng dấu phẩy")
    add_p.add_argument("--root", type=Path, default=REPO_ROOT)
    add_p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)

    ingest_p = subparsers.add_parser("ingest-dir", help="Import images and videos from a directory")
    ingest_p.add_argument("directory", type=Path)
    ingest_p.add_argument("--pham-vi", required=True)
    ingest_p.add_argument("--ai", action="store_true", default=None)
    ingest_p.add_argument("--tags", default="")
    ingest_p.add_argument("--tags-from-prompts", type=Path)
    ingest_p.add_argument("--push", action="store_true")
    ingest_p.add_argument("--dry-run", action="store_true")
    ingest_p.add_argument("--near-threshold", type=int, default=8)
    ingest_p.add_argument("--root", type=Path, default=REPO_ROOT)
    ingest_p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)

    # Subcommand: mark-used
    mark_p = subparsers.add_parser("mark-used", help="Ghi nhận đã dùng: asset_id video_id kênh ngày")
    mark_p.add_argument("asset_id", type=str)
    mark_p.add_argument("video_id", type=str)
    mark_p.add_argument("kenh", type=str)
    mark_p.add_argument("ngay", type=str, help="YYYY-MM-DD")
    mark_p.add_argument("--public-date", type=str, default=None, help="YYYY-MM-DD video lên public (prune cần)")
    mark_p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)

    # Subcommand: merge-external
    merge_p = subparsers.add_parser("merge-external", help="Gộp manifest ngoài (không chép file)")
    merge_p.add_argument("external", type=Path, help="manifest.jsonl bên Mimck")
    merge_p.add_argument("--pham-vi", required=True, type=str)
    merge_p.add_argument("--host", required=True, type=str, help="Máy nguồn, vd windows")
    merge_p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Manifest local để ghi")
    merge_p.add_argument("--root", type=Path, default=REPO_ROOT)

    # Subcommand: check
    check_p = subparsers.add_parser("check", help="Kiểm tra toàn vẹn tài sản")
    check_p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Đường dẫn manifest.jsonl")
    check_p.add_argument("--root", type=Path, default=REPO_ROOT, help="Thư mục gốc repo")
    check_p.add_argument("--json", action="store_true", help="Xuất báo cáo định dạng JSON")

    # Subcommand: manifest-for
    mfor_p = subparsers.add_parser("manifest-for", help="Xuất danh sách file + sha256 cho một plan")
    mfor_p.add_argument("plan", type=str, help="ID plan (vd L_fs_tv05) hoặc đường dẫn file plan")
    mfor_p.add_argument("--root", type=Path, default=REPO_ROOT, help="Thư mục gốc repo")
    mfor_p.add_argument("--format", choices=["sha256", "files", "json"], default="sha256", help="Định dạng xuất")
    mfor_p.add_argument("--out", type=Path, help="Ghi ra tệp xuất")

    for p in (scan_p, add_p):
        p.add_argument("--near-threshold", type=int, default=8)
        p.add_argument("--allow-near", action="store_true")
    find_p.add_argument("--max-uses", type=int)
    find_p.add_argument("--min-gap-days", type=int)
    near_p = subparsers.add_parser("near-dups")
    near_p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    near_p.add_argument("--root", type=Path, default=REPO_ROOT)
    near_p.add_argument("--near-threshold", type=int, default=8)
    push_p = subparsers.add_parser("push")
    group = push_p.add_mutually_exclusive_group(required=True)
    group.add_argument("--id", action="append")
    group.add_argument("--all-local", action="store_true")
    pull_p = subparsers.add_parser("pull")
    group = pull_p.add_mutually_exclusive_group(required=True)
    group.add_argument("--ids", nargs="+", help="IDs, separated by spaces or commas")
    group.add_argument("--plan")
    prune_p = subparsers.add_parser("prune")
    prune_p.add_argument("--dry-run", action="store_true")
    prune_p.add_argument("--yes", action="store_true")
    for p in (push_p, pull_p, prune_p):
        p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
        p.add_argument("--root", type=Path, default=REPO_ROOT)

    args = parser.parse_args(argv)
    if getattr(args, "near_threshold", 8) not in range(65):
        parser.error("--near-threshold must be between 0 and 64")
    if args.command == "ingest-dir":
        try:
            result = ingest_dir(args.directory, args.pham_vi, ai=args.ai,
                                tags=[t.strip() for t in args.tags.split(",") if t.strip()],
                                prompts_path=args.tags_from_prompts, push=args.push,
                                near_threshold=args.near_threshold, dry_run=args.dry_run,
                                root=args.root, manifest_path=args.manifest)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 1 if result["errors"] else 0
        except (ValueError, OSError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
    if args.command == "near-dups":
        print(json.dumps(near_dups(load_manifest(args.manifest), args.near_threshold, args.root), ensure_ascii=False, indent=2))
        return 0
    if args.command in ("push", "pull", "prune"):
        try:
            if args.command == "push":
                result = push_assets(args.id or [], args.all_local, args.manifest, args.root)
            elif args.command == "pull":
                ids = [part for value in (args.ids or []) for part in value.split(",") if part]
                result = pull_assets(ids, args.plan, args.manifest, args.root)
            else:
                result = prune_assets(args.manifest, args.root, args.yes and not args.dry_run)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        except (ValueError, OSError, subprocess.SubprocessError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    if args.command == "scan":
        dir_list = [d.strip() for d in args.dirs.split(",") if d.strip()] if args.dirs else None
        stats = scan_assets(root=args.root, manifest_path=args.out, dirs=dir_list, near_threshold=args.near_threshold, allow_near=args.allow_near)
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return 0

    elif args.command == "find":
        results = find_assets(
            pham_vi=args.pham_vi,
            tag=args.tag,
            kind=args.kind,
            min_w=args.min_w,
            chua_dung_trong=args.chua_dung_trong,
            manifest_path=args.manifest,
            top=args.top,
            exclude_used_days=args.exclude_used_days,
            channel=args.channel,
            root=args.root,
            max_uses=args.max_uses, min_gap_days=args.min_gap_days,
        )
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(f"Tìm thấy {len(results)} tài sản phù hợp (thứ tự: kênh → chung fallback):")
            for idx, r in enumerate(results, 1):
                dur_str = f" {r['duration_s']}s" if r.get("duration_s") else ""
                hang = r.get("hang_pham_vi") or ""
                hang_str = f" | hang: {hang}" + (" (fallback)" if hang == "chung" and (args.pham_vi or args.channel) not in (None, "chung") else "")
                print(f"[{idx}] {r['asset_id']} | {r['kind']}{dur_str} | {r['w']}x{r['h']} | pham_vi: {r['pham_vi']}{hang_str}")
                print(f"    Path: {r['path']}")
                print(f"    Tags: core={r['tags']['core'][:4]} domain={r['tags']['domain'][:4]}")
                print(f"    License: {r['license']['type']} (commercial={r['license']['commercial_allowed']}) | Source: {r['source']['type']}")
        return 0

    elif args.command == "add":
        tags = [t.strip() for t in (args.tags or "").split(",") if t.strip()]
        rec = add_asset(
            args.file,
            pham_vi=args.pham_vi,
            prompt=args.prompt,
            tags=tags,
            root=args.root,
            manifest_path=args.manifest,
            ai=args.ai, near_threshold=args.near_threshold, allow_near=args.allow_near,
        )
        print(json.dumps({"asset_id": rec["asset_id"], "path": rec["path"], "pham_vi": rec["pham_vi"]}, ensure_ascii=False))
        return 0

    elif args.command == "mark-used":
        rec = mark_used(args.asset_id, args.video_id, args.kenh, args.ngay, manifest_path=args.manifest, ngay_public=args.public_date)
        print(json.dumps({"asset_id": rec["asset_id"], "video_da_dung": rec.get("video_da_dung")}, ensure_ascii=False))
        return 0

    elif args.command == "merge-external":
        stats = merge_external(
            args.external,
            pham_vi=args.pham_vi,
            host=args.host,
            manifest_path=args.manifest,
            root=args.root,
        )
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return 0

    elif args.command == "check":
        report = check_assets(manifest_path=args.manifest, root=args.root)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(f"Kiểm tra tài sản: {report['status']}")
            print(f"  Tổng mục: {report['total_checked']}")
            print(f"  File mất: {report['missing_files_count']}")
            print(f"  SHA lệch: {report['sha_mismatches_count']}")
            print(f"  Giấy phép unknown: {report['unknown_licenses_count']}")
            print(f"  Ảnh AI chưa strip_mark: {report['ai_unstripped_count']}")
            if report["missing_files"]:
                print("  Chi tiết file mất:")
                for m in report["missing_files"][:5]:
                    print(f"    - {m['path']}")
            if report["sha_mismatches"]:
                print("  Chi tiết SHA lệch:")
                for s in report["sha_mismatches"][:5]:
                    print(f"    - {s['path']}")
            if report["ai_unstripped"]:
                print("  Chi tiết ảnh AI chưa strip_mark:")
                for u in report["ai_unstripped"][:5]:
                    print(f"    - {u['path']}")
        return 0 if report["status"] == "PASS" else 1

    elif args.command == "manifest-for":
        try:
            items = manifest_for_plan(args.plan, root=args.root, out_format=args.format, out_path=args.out)
        except MissingAssetsError as exc:
            print(f"LỖI: Thiếu {len(exc.missing)} tài sản / phụ thuộc render cho {args.plan}:", file=sys.stderr)
            for m in exc.missing[:20]:
                print(f"  - [{m.get('type')}] {m.get('path', m.get('error'))}", file=sys.stderr)
            if len(exc.missing) > 20:
                print(f"  ... và {len(exc.missing) - 20} tệp khác.", file=sys.stderr)
            return 1
        total_sz = sum(item["byte"] for item in items)
        if not args.out:
            if args.format == "files":
                for item in items:
                    print(item["path"])
            elif args.format == "json":
                print(json.dumps(items, ensure_ascii=False, indent=2))
            else:
                for item in items:
                    print(f"{item['sha256']}  {item['path']}")
        print(f"# manifest-for {args.plan}: {len(items)} files, {total_sz / 1024 / 1024:.2f} MB", file=sys.stderr)
        return 0

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, KeyError, FileNotFoundError) as exc:   # lỗi người dùng (ảnh gần trùng, thiếu ASSET_REMOTE...): một dòng, không traceback
        print(f"LỖI: {exc}", file=sys.stderr)
        sys.exit(2)
