"""Ảnh tư liệu từ Openverse (api.openverse.org) -- kho tổng hợp ảnh giấy phép mở của nhiều nguồn trên thế giới
(Flickr, Smithsonian, bảo tàng, thư viện, Wikimedia...). Bổ sung cho Commons + bảo tàng CC0 (người dùng 04/10/2026:
"nghiên cứu kĩ kho tư liệu cộng đồng nhiều nguồn trên thế giới").

CHỈ nhận CC0 / Public Domain Mark / CC BY / CC BY-SA (không NC, không ND); dòng ghi công có tác giả + giấy phép + nguồn.
Lưu ý quyền hình ảnh: giấy phép CC phủ bản quyền, không phủ quyền chân dung -> không dùng ảnh cận mặt người thật để
minh hoạ điều tiêu cực (bệnh tật, xui rủi, phạm tội).

    python hf_openverse.py search "hanoi old quarter"        # ứng viên
    media spec trong plan: {"kind": "openverse", "ref": "ov:<id>"}
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
CACHE = ROOT / "chunks_cache" / "openverse"
UA = {"User-Agent": "vietneu-tts/1.0 (documentary long videos; open-licence images with attribution)"}
API = "https://api.openverse.org/v1/images/"
OK = {"cc0", "pdm", "by", "by-sa"}
LIC_NAME = {"cc0": "CC0", "pdm": "Public domain", "by": "CC BY", "by-sa": "CC BY-SA"}


def _get(url: str, tries: int = 5) -> bytes:
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except Exception as e:  # 429/5xx: lùi dần
            if k == tries - 1:
                raise
            time.sleep(3 * (k + 1) + (15 if "429" in str(e) else 0))
    raise RuntimeError("unreachable")


def _license(r: dict) -> str:
    lic = (r.get("license") or "").lower()
    name = LIC_NAME.get(lic, lic.upper())
    v = r.get("license_version") or ""
    return f"{name} {v}".strip() if lic in ("by", "by-sa") and v else name


def search(query: str, limit: int = 20) -> list[dict]:
    """Ứng viên: [{ref, title, creator, license, source, thumb, w, h}] -- chỉ giấy phép dùng được."""
    q = urllib.parse.urlencode({"q": query, "license": ",".join(sorted(OK)), "page_size": min(limit, 20),
                                "mature": "false"})
    d = json.loads(_get(f"{API}?{q}"))
    out = []
    for r in d.get("results", []):
        if (r.get("license") or "").lower() not in OK:
            continue
        out.append({"ref": "ov:" + r["id"], "title": (r.get("title") or "")[:90], "creator": r.get("creator") or "",
                    "license": _license(r), "source": r.get("source") or r.get("provider") or "",
                    "thumb": r.get("thumbnail"), "w": r.get("width"), "h": r.get("height")})
    return out


def fetch(ref: str) -> tuple[Path, str]:
    """Tải (có cache) ảnh, trả (đường dẫn jpg, dòng ghi công). Giấy phép không dùng được -> ValueError."""
    from PIL import Image  # noqa: PLC0415
    oid = ref.split(":", 1)[-1].strip()
    if not re.fullmatch(r"[0-9a-f-]{36}", oid):
        raise ValueError(f"{ref}: mã Openverse không hợp lệ (cần ov:<uuid>)")
    CACHE.mkdir(parents=True, exist_ok=True)
    dst, meta = CACHE / f"{oid}.jpg", CACHE / f"{oid}.json"
    if dst.exists() and meta.exists():
        m = json.loads(meta.read_text(encoding="utf-8"))
        return dst, m["credit"]
    r = json.loads(_get(f"{API}{oid}/"))
    if (r.get("license") or "").lower() not in OK:
        raise ValueError(f"{ref}: giấy phép '{r.get('license')}' không dùng được (cần CC0/PD/CC BY/CC BY-SA)")
    try:
        raw = _get(r["url"])
    except Exception:  # noqa: BLE001 -- ảnh gốc ở nguồn hỏng/chặn -> ảnh thu nhỏ của Openverse
        raw = _get(r["thumbnail"])
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
    title = re.sub(r"\s+", " ", r.get("title") or "").strip()[:80]
    src = r.get("source") or r.get("provider") or "Openverse"
    credit = f"{title} — {(r.get('creator') or 'không rõ tác giả') + ', '}{_license(r)}, {src} via Openverse"
    meta.write_text(json.dumps({"ref": ref, "license": r.get("license"), "credit": credit,
                                "landing": r.get("foreign_landing_url")}, ensure_ascii=False), encoding="utf-8")
    return dst, credit


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "search":
        for c in search(" ".join(sys.argv[2:])):
            print(f"{c['ref']}  {c['license']:<12} {c['source']:<12} {c['creator'][:20]:<20} {c['title'][:60]}")
    elif len(sys.argv) >= 3 and sys.argv[1] == "fetch":
        print(fetch(sys.argv[2]))
    else:
        print(__doc__)
