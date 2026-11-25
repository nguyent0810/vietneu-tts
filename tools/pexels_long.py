"""Pexels-only Long resolution, frozen before chapter splitting.

Uses the existing credential loader and asset_safety protocol. Tests replace
both credential/network boundaries; enrichment never imports this module.
"""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

import asset_safety
import stock_image


def _slow_video(data: bytes, duration: float) -> bytes:
    """Freeze a deterministic 6s center excerpt at 0.8x, with audio removed.

    MP4 từ Pexels thường đặt moov ở cuối file -> không đọc được qua pipe (cần seek);
    ghi ra file tạm rồi mới cắt (Lead 25/11, lỗi khi tải thật)."""
    import tempfile
    source_duration = max(0.0, float(duration or 0))
    excerpt = min(6.0, source_duration) if source_duration else 6.0
    start = max(0.0, (source_duration - excerpt) / 2)
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = Path(tmp) / "in.mp4", Path(tmp) / "out.mp4"
        src.write_bytes(data)
        args = ["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-i", str(src), "-t", f"{excerpt:.3f}",
                "-vf", "setpts=1.25*PTS", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dst)]
        result = subprocess.run(args, capture_output=True, check=False)
        out = dst.read_bytes() if dst.exists() else b""
    if result.returncode or len(out) < 4096:
        raise ValueError("Pexels video không thể cắt/slow 0.8x an toàn bằng ffmpeg")
    return out


def has_visible_text(path: Path, min_words: int = 2) -> bool:
    """OCR (tesseract) ảnh hoặc khung giữa video: có ≥ min_words từ Latin rõ thì coi là dính chữ.

    Lead 25/11: tờ Pexels 1965 lọt "Lease Agreement", lịch tiếng Anh — luật kênh không chữ trên hình.
    Không có tesseract/ffmpeg thì trả False (không chặn), Lead vẫn soát tờ ảnh."""
    import shutil
    import tempfile
    if not shutil.which("tesseract"):
        return False
    with tempfile.TemporaryDirectory() as tmp:
        img = Path(path)
        if img.suffix.lower() == ".mp4":
            img = Path(tmp) / "frame.png"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "2", "-i", str(path), "-frames:v", "1", str(img)],
                           capture_output=True, check=False)
            if not img.exists():
                return False
        res = subprocess.run(["tesseract", str(img), "-", "--psm", "11", "tsv"], capture_output=True, text=True, check=False)
    words = 0
    for line in res.stdout.splitlines()[1:]:
        cols = line.split("\t")
        if len(cols) >= 12 and cols[10].replace(".", "", 1).lstrip("-").isdigit() and float(cols[10]) > 75:
            w = cols[11].strip()
            if len(w) >= 4 and w.isalpha():
                words += 1
    return words >= min_words


def fetch(kind, query, used):
    key = hashlib.sha256(f"pexels|{kind}|{query}".encode()).hexdigest()[:20]
    folder = stock_image.CACHE_DIR / "pexels_long"
    folder.mkdir(parents=True, exist_ok=True)
    # Query metadata lets repeated queries choose different IDs and reuse cache
    # on a later full render, without a random provider fallback.
    for meta in sorted(folder.glob(f"{key}_*.source.json")):
        data = json.loads(meta.read_text())
        path = folder / data["filename"]
        if path.is_file():
            asset_safety.assert_asset_safe_for_assembly(path)
            if not has_visible_text(path) and hashlib.sha256(path.read_bytes()).hexdigest() not in used:
                return path, data
    pexels_key, _ = stock_image.load_keys()
    if not pexels_key:
        raise ValueError("Pexels Long chưa có cấu hình khoá")
    endpoint = "v1/search" if kind == "image" else "videos/search"
    for page in range(1, 4):
        url = f"https://api.pexels.com/{endpoint}?" + urllib.parse.urlencode(
            {"query": query, "orientation": "landscape", "per_page": 80, "page": page})
        payload = stock_image._get_json(url, headers={"Authorization": pexels_key})
        entries = payload.get("photos" if kind == "image" else "videos") or []
        for entry in entries:
            if kind == "image":
                hit = stock_image.pick_pexels({"photos": [entry]})
                if not hit:
                    continue
                src, author = hit["url"], hit["author"]
            else:
                files = [f for f in entry.get("video_files", []) if f.get("file_type") == "video/mp4"
                         and f.get("width", 0) >= 1280 and f.get("height", 0) >= 720 and f.get("link")]
                if not files:
                    continue
                src = min(files, key=lambda f: f["width"] * f["height"])["link"]
                author = (entry.get("user") or {}).get("name", "")
            asset_id = str(entry["id"])
            path = folder / f"{key}_{asset_id}.{'jpg' if kind == 'image' else 'mp4'}"
            asset_safety.assert_asset_safe_for_assembly(path)
            if not path.exists():
                req = urllib.request.Request(src, headers={"User-Agent": stock_image.USER_AGENT})
                with urllib.request.urlopen(req, timeout=stock_image.TIMEOUT_S) as response:
                    data = response.read()
                if len(data) < 4096:
                    continue
                if kind == "video":
                    data = _slow_video(data, float(entry.get("duration") or 0))
                path.write_bytes(data)
                asset_safety.assert_asset_safe_for_assembly(path)
                asset_safety.write_asset_safety_record(
                    path, asset_safety.AssetSafetyStatus.SAFE,
                    reason=f"Pexels {kind} id {asset_id}; chưa duyệt nội dung bằng mắt",
                    source="fetched_stock_no_content_review")
            asset_safety.assert_asset_safe_for_assembly(path)
            metadata = {"provider": "pexels", "id": asset_id, "page": entry.get("url", ""),
                        "author": author, "query": query, "filename": path.name}
            path.with_suffix(".source.json").write_text(json.dumps(metadata, ensure_ascii=False))
            if has_visible_text(path):
                continue  # dính chữ (OCR) -> lấy kết quả kế tiếp
            if hashlib.sha256(path.read_bytes()).hexdigest() not in used:
                return path, metadata
        if len(entries) < 80:
            break
    raise ValueError(f"Pexels {kind}: hết file khác nhau cho {query!r}; đổi query hoặc giảm media_mix")


def frozen_asset(spec):
    path = Path(spec["stock_path"]).resolve()
    allowed = (stock_image.CACHE_DIR / "pexels_long").resolve()
    if allowed not in path.parents or not path.is_file():
        raise ValueError("stock_path phải là cache Pexels Long đã đóng băng")
    asset_safety.assert_asset_safe_for_assembly(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != spec.get("stock_sha256"):
        raise ValueError("File stock thay đổi sau khi đóng băng")
    return path


def prepare(row):
    """Resolve once per whole Long; never reset used files at a chapter boundary."""
    from hyperframes_bridge import sanitize_query
    out, used = copy.deepcopy(row), set()
    # Include every cut, not just the first shot. Existing frozen files are
    # reserved before fetching new entries, so editing order cannot reuse them.
    specs = []
    for _, spec in sorted((out.get("media") or {}).items(), key=lambda kv: int(kv[0])):
        specs.extend([spec, *spec.get("cuts", [])])
    specs = [s for s in specs if s.get("provider") == "pexels" and s.get("kind") in {"image", "video"}]
    for spec in specs:
        if spec.get("stock_path"):
            digest = hashlib.sha256(frozen_asset(spec).read_bytes()).hexdigest()
            if digest in used:
                raise ValueError("Pexels Long: file trùng giữa các câu/chương")
            used.add(digest)
    for spec in specs:
        if spec.get("stock_path"):
            continue
        query = sanitize_query(spec["query"], str(out.get("series", "fs")).upper())
        path, meta = fetch(spec["kind"], query, used)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in used:
            raise ValueError("Pexels Long: file trùng (kể cả query khác)")
        used.add(digest)
        spec.update(stock_path=str(path.resolve()), stock_sha256=digest, stock_source=meta)
    return out
