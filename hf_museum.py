"""Tư liệu bảo tàng mở (CC0 / phạm vi công cộng) -- đào sâu hơn Wikimedia Commons.

    The Met Open Access   collectionapi.metmuseum.org   (isPublicDomain = CC0)
    Art Institute Chicago api.artic.edu + IIIF           (is_public_domain = CC0)
    Cleveland Museum      openaccess-api.clevelandart.org (cc0)

Vì sao: video dài 30+ phút cần 60-100 tư liệu thật cho một chủ đề. Commons có nhiều nhưng
lẫn ảnh chụp chất lượng thấp; ba bảo tàng này có ảnh chụp chuẩn bảo tàng của tượng, phù điêu,
tranh cuộn, la bàn, lịch cổ... kèm niên đại và xuất xứ (dùng luôn làm nhãn trên màn hình).

    python hf_museum.py search "gandhara relief buddha"      # gộp 3 nguồn, chỉ CC0
    python hf_museum.py fetch met:38123                       # -> (đường dẫn jpg, ghi công)
    plan: {"type": "museum"|"doc"|"photo", "museum": "aic:16568", ...}
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
CACHE = ROOT / "chunks_cache" / "museum"
UA = {"User-Agent": "vietneu-tts/1.0 (documentary research; non-commercial tooling)",
      "AIC-User-Agent": "vietneu-tts (educational documentaries)"}   # AIC IIIF: thiếu header này hoặc xin > 843px -> 403


def _get(url: str, tries: int = 4, raw: bool = False):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                b = r.read()
                return b if raw else json.loads(b)
        except Exception as e:  # noqa: BLE001 -- mạng chập chờn / 429: lùi dần
            if k == tries - 1:
                raise
            time.sleep(2 * (k + 1) + (8 if "429" in str(e) else 0))
    return None


# ---------------- The Met ----------------
def _met_search(q: str, limit: int) -> list[dict]:
    ids = (_get("https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&q="
                + urllib.parse.quote(q)) or {}).get("objectIDs") or []
    out = []
    for oid in ids[: limit * 3]:
        try:
            o = _get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}")
        except Exception:  # noqa: BLE001
            continue
        if not o.get("isPublicDomain") or not o.get("primaryImage"):
            continue
        out.append({"ref": f"met:{oid}", "title": o.get("title", ""), "date": o.get("objectDate", ""),
                    "place": o.get("culture") or o.get("country") or "", "img": o.get("primaryImage"),
                    "thumb": o.get("primaryImageSmall"), "credit": f"The Met, {o.get('creditLine', '')} (CC0)"})
        if len(out) >= limit:
            break
        time.sleep(.05)
    return out


# ---------------- Art Institute of Chicago ----------------
def _aic_search(q: str, limit: int) -> list[dict]:
    d = _get("https://api.artic.edu/api/v1/artworks/search?q=" + urllib.parse.quote(q)
             + f"&limit={limit * 2}&fields=id,title,image_id,is_public_domain,date_display,place_of_origin,credit_line")
    out = []
    for a in (d or {}).get("data", []):
        if not a.get("is_public_domain") or not a.get("image_id"):
            continue
        base = f"https://www.artic.edu/iiif/2/{a['image_id']}/full"
        out.append({"ref": f"aic:{a['id']}", "title": a.get("title", ""), "date": a.get("date_display", ""),
                    "place": a.get("place_of_origin", ""), "img": f"{base}/1686,/0/default.jpg",
                    "thumb": f"{base}/400,/0/default.jpg", "credit": f"Art Institute of Chicago, {a.get('credit_line', '')} (CC0)"})
        if len(out) >= limit:
            break
    return out


# ---------------- Cleveland Museum of Art ----------------
def _cma_search(q: str, limit: int) -> list[dict]:
    d = _get("https://openaccess-api.clevelandart.org/api/artworks/?cc0=1&has_image=1&limit="
             + str(limit) + "&q=" + urllib.parse.quote(q))
    out = []
    for a in (d or {}).get("data", []):
        im = (a.get("images") or {})
        url = ((im.get("print") or {}).get("url")) or ((im.get("web") or {}).get("url"))
        if not url:
            continue
        out.append({"ref": f"cma:{a['id']}", "title": a.get("title", ""), "date": a.get("creation_date", ""),
                    "place": a.get("culture", [""])[0] if a.get("culture") else "", "img": url,
                    "thumb": (im.get("web") or {}).get("url"), "credit": "Cleveland Museum of Art, Open Access (CC0)"})
    return out


SOURCES = {"met": _met_search, "aic": _aic_search, "cma": _cma_search}


def search(q: str, limit: int = 8, sources=("aic", "cma", "met")) -> list[dict]:
    out = []
    for s in sources:
        try:
            out += SOURCES[s](q, limit)
        except Exception as e:  # noqa: BLE001 -- một nguồn hỏng không làm hỏng cả lượt tìm
            print(f"  ({s} lỗi: {str(e)[:80]})", file=sys.stderr)
    return out


def _info(ref: str) -> dict:
    src, _, oid = ref.partition(":")
    if src == "met":
        o = _get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}")
        if not o.get("isPublicDomain"):
            raise ValueError(f"{ref}: không phải phạm vi công cộng")
        return {"img": o["primaryImage"], "title": o.get("title", ""), "date": o.get("objectDate", ""),
                "credit": f"{o.get('title', '')} — The Met, {o.get('creditLine', '')} (CC0)"}
    if src == "aic":
        a = _get(f"https://api.artic.edu/api/v1/artworks/{oid}?fields=id,title,image_id,is_public_domain,date_display,credit_line")["data"]
        if not a.get("is_public_domain"):
            raise ValueError(f"{ref}: không phải phạm vi công cộng")
        return {"img": f"https://www.artic.edu/iiif/2/{a['image_id']}/full/843,/0/default.jpg", "title": a.get("title", ""),
                "date": a.get("date_display", ""), "credit": f"{a.get('title', '')} — Art Institute of Chicago (CC0)"}
    if src == "cma":
        a = _get(f"https://openaccess-api.clevelandart.org/api/artworks/{oid}")["data"]
        if (a.get("share_license_status") or "").upper() != "CC0":
            raise ValueError(f"{ref}: không phải CC0")
        im = a.get("images") or {}
        return {"img": ((im.get("print") or {}).get("url")) or im["web"]["url"], "title": a.get("title", ""),
                "date": a.get("creation_date", ""), "credit": f"{a.get('title', '')} — Cleveland Museum of Art (CC0)"}
    raise ValueError(f"nguồn lạ: {ref}")


def fetch(ref: str) -> tuple[Path, str]:
    """Tải (có cache) ảnh CC0 của một hiện vật -> (jpg, dòng ghi công)."""
    import io  # noqa: PLC0415
    from PIL import Image  # noqa: PLC0415
    CACHE.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^\w]+", "_", ref)
    dst, meta = CACHE / f"{safe}.jpg", CACHE / f"{safe}.json"
    if dst.exists() and meta.exists():
        return dst, json.loads(meta.read_text(encoding="utf-8"))["credit"]
    info = _info(ref)
    im = Image.open(io.BytesIO(_get(info["img"], raw=True))).convert("RGB")
    if max(im.size) > 2600:
        im.thumbnail((2600, 2600))
    im.save(dst, quality=90)
    meta.write_text(json.dumps(info, ensure_ascii=False), encoding="utf-8")
    return dst, info["credit"]


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "search":
        for c in search(" ".join(sys.argv[2:])):
            print(f"{c['ref']:12s} {c['date'][:22]:22s} {c['place'][:18]:18s} {c['title'][:70]}")
    elif len(sys.argv) >= 3 and sys.argv[1] == "fetch":
        print(fetch(sys.argv[2]))
