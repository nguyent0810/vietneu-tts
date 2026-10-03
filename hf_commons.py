"""Ảnh tư liệu từ Wikimedia Commons -- CHỈ phạm vi công cộng / CC0.

Port từ Youtube_Creator_V2 (motion/stier/build.py + research.py). Vì sao dùng:
ảnh stock (Pexels) cho kênh Phật giáo / Phong Thuỷ hay trả sai ngữ cảnh (đền
Hindu, ly rượu, nữ tu Công giáo...); tranh Phật cổ, kinh lá bối, la bàn cổ trên
Commons vừa thật vừa đúng chủ đề.

    python hf_commons.py search "palm leaf manuscript buddhist"   # ứng viên PD
    media spec trong plan: {"kind": "commons", "file": "File:Tên.jpg"}

upload.wikimedia.org chặn tải bản gốc (429) -> luôn xin ảnh thu nhỏ cỡ chuẩn.
"""
from __future__ import annotations

import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
CACHE = ROOT / "chunks_cache" / "commons"
UA = {"User-Agent": "vietneu-tts/1.0 (documentary shorts; contact via channel)"}
PD = re.compile(r"public domain|^pd|cc0|no restrictions", re.I)
# Video dài (theo V2 build_long): nhận thêm CC BY / CC BY-SA, KHÔNG nhận NC/ND; ghi tác giả + giấy phép.
BY = re.compile(r"^cc[ -]by(-sa)?([ -][\d.]+)?$|^cc[ -]by(-sa)?$|attribution", re.I)
BAD = re.compile(r"\bNC\b|\bND\b", re.I)


def ok_license(lic: str, allow_by: bool = False) -> bool:
    if PD.search(lic):
        return True
    return allow_by and bool(BY.search(lic.strip())) and not BAD.search(lic)
SKIP = re.compile(r"(logo|icon|flag_of|\.svg$|signature|coat_of_arms|map_marker|\.pdf$|\.djvu$|\.tif)", re.I)


def _get(url: str, tries: int = 6) -> bytes:
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return r.read()
        except Exception as e:  # 429/5xx: lùi dần
            if k == tries - 1:
                raise
            time.sleep(3 * (k + 1) + (10 if "429" in str(e) else 0))
    raise RuntimeError("unreachable")


def _api(**params) -> dict:
    params |= {"format": "json", "formatversion": "2"}
    time.sleep(0.3)
    return json.loads(_get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)))


def license_of(ii: dict) -> str:
    return ii.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")


def search(query: str, limit: int = 30, allow_by: bool = False) -> list[dict]:
    """Ứng viên ảnh PD/CC0: [{file, w, h, license, thumb}]."""
    d = _api(action="query", generator="search", gsrnamespace=6, gsrsearch=query, gsrlimit=limit,
             prop="imageinfo", iiprop="url|size|extmetadata", iiurlwidth=400)
    out = []
    for p in (d.get("query") or {}).get("pages", []):
        ii = (p.get("imageinfo") or [{}])[0]
        if SKIP.search(p["title"]) or not ok_license(license_of(ii), allow_by):
            continue
        out.append({"file": p["title"], "w": ii.get("width"), "h": ii.get("height"),
                    "license": license_of(ii), "thumb": ii.get("thumburl")})
    return out


def fetch(file: str, allow_by: bool = False) -> tuple[Path, str]:
    """Tải (có cache) ảnh PD, trả (đường dẫn jpg, dòng ghi công). Không PD -> ValueError."""
    from PIL import Image  # noqa: PLC0415
    CACHE.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^\w.-]+", "_", file.replace("File:", ""))[:120]
    dst = CACHE / (Path(safe).stem + ".jpg")
    meta = dst.with_suffix(".json")
    if dst.exists() and meta.exists():
        m = json.loads(meta.read_text(encoding="utf-8"))
        if not ok_license(m.get("license", ""), allow_by):
            raise ValueError(f"{file}: giấy phép '{m.get('license')}' cần allow_by")
        return dst, m["credit"]

    def info(width=None):
        prm = {"action": "query", "prop": "imageinfo", "titles": file, "iiprop": "url|size|extmetadata"}
        if width:
            prm["iiurlwidth"] = width
        return _api(**prm)["query"]["pages"][0]["imageinfo"][0]

    ii = info()
    w = next((x for x in (1920, 1280, 960, 500) if x < ii["width"]), None)
    if w:
        ii = info(w)
    lic = license_of(ii)
    if not ok_license(lic, allow_by):
        raise ValueError(f"{file}: giấy phép '{lic}' không dùng được (cần PD/CC0, hoặc CC BY/BY-SA khi allow_by)")
    raw = _get(ii.get("thumburl") or ii["url"])
    im = Image.open(io.BytesIO(raw))
    if im.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", im.size, (255, 255, 255))
        im = im.convert("RGBA")
        bg.paste(im, mask=im.split()[-1])
        im = bg
    im = im.convert("RGB")
    if max(im.size) > 2400:
        im.thumbnail((2400, 2400))
    im.save(dst, quality=90)
    artist = re.sub(r"<[^>]+>", "", ii.get("extmetadata", {}).get("Artist", {}).get("value", "")).strip()
    credit = f"{file.replace('File:', '')} — {artist + ', ' if artist else ''}{lic}, Wikimedia Commons"
    meta.write_text(json.dumps({"file": file, "license": lic, "credit": credit}, ensure_ascii=False), encoding="utf-8")
    return dst, credit


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "search":
        for c in search(" ".join(sys.argv[2:])):
            print(f"{c['w']}x{c['h']}  {c['license']:<22} {c['file']}")
    elif len(sys.argv) >= 3 and sys.argv[1] == "fetch":
        print(fetch(sys.argv[2]))
