"""Ảnh tư liệu NGOÀI Commons/Openverse cho BUD/FS: Wellcome Collection, Art Institute of Chicago, Europeana.

Port motion/long/media_search.py của Youtube_Creator_V2 (04/10/2026) — chỉ nguồn đã kiểm giấy phép dùng thương mại
(kênh bật kiếm tiền): PDM / CC0 / CC BY / CC BY-SA. Không NC/ND.
- wellcome  : tranh/ảnh Ấn Độ, Trung Hoa thế kỷ 18-19 (nghệ nhân, lễ hội, y học cổ) — IIIF.
- artic     : Art Institute of Chicago, tác phẩm phạm vi công cộng (CC0) — tượng Phật, tranh Á Đông — IIIF.
- europeana : bảo tàng/lưu trữ châu Âu (Tropenmuseum, KITLV...) — ảnh Đông Dương đầu thế kỷ 20. Khoá miễn phí
              EUROPEANA_KEY (không có thì dùng khoá demo api2demo, giới hạn thấp).

    python hf_extmedia.py search "pagoda tonkin"            # in ứng viên (ref, giấy phép, tiêu đề)
    media trong plan: {"kind": "ext", "ref": "europeana:/2048128/618564", "tagged": true}

Ảnh tải về: chunks_cache/extmedia/<src>_<id>.jpg + .json {credit, license, page}. Giữ file .json (bằng chứng giấy phép).
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "chunks_cache" / "extmedia"
UA = {"User-Agent": "vietneu-tts/1.0 (educational documentaries; Buddhism & feng shui channels)",
      # AIC chặn IIIF (403) nếu thiếu header riêng của họ -- đây là lý do hf_museum "aic:" tải hỏng từ trước 04/10/2026
      "AIC-User-Agent": "vietneu-tts (educational documentaries)"}
SRC_NAME = {"wellcome": "Wellcome Collection", "artic": "Art Institute of Chicago", "europeana": "Europeana"}


def _get(url: str, tries: int = 4) -> bytes:
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001 -- 429/5xx: lùi dần
            if k == tries - 1:
                raise
            time.sleep(3 * (k + 1) + (6 if "429" in str(e) else 0))
    raise RuntimeError("unreachable")


def _json(url: str, **params) -> dict:
    return json.loads(_get(url + ("?" + urllib.parse.urlencode(params) if params else "")))


def _wellcome(i: dict) -> dict | None:
    loc = (i.get("locations") or [{}])[0]
    lab = {"cc-0": "CC0", "pdm": "Public domain", "cc-by": "CC BY 4.0"}.get((loc.get("license") or {}).get("id", ""))
    if not lab or not loc.get("url"):
        return None
    base = loc["url"].rsplit("/info.json", 1)[0]
    src = i.get("source") or {}
    return {"ref": f"wellcome:{i['id']}", "title": src.get("title", ""), "license": lab, "artist": "Wellcome Collection",
            "thumb": base + "/full/300,/0/default.jpg", "full": base + "/full/1920,/0/default.jpg",
            "page": f"https://wellcomecollection.org/works/{src.get('id', '')}"}


def _artic(i: dict) -> dict | None:
    if not i.get("is_public_domain") or not i.get("image_id"):
        return None
    base = f"https://www.artic.edu/iiif/2/{i['image_id']}"
    return {"ref": f"artic:{i['id']}", "title": i.get("title", ""), "license": "CC0",
            "artist": (i.get("artist_display") or "").split("\n")[0][:80], "thumb": base + "/full/300,/0/default.jpg",
            "full": base + "/full/843,/0/default.jpg",   # IIIF công khai của AIC tối đa 843px (1686 -> 403)
            "page": f"https://www.artic.edu/artworks/{i['id']}"}


def _eu_license(rights: str) -> str | None:
    if "publicdomain/mark" in rights:
        return "Public domain"
    if "publicdomain/zero" in rights:
        return "CC0"
    m = re.search(r"licenses/(by(?:-sa)?)/(\d\.\d)", rights)
    return f"CC {m.group(1).upper()} {m.group(2)}" if m else None


def _europeana(i: dict) -> dict | None:
    lab = _eu_license((i.get("rights") or [""])[0])
    full = (i.get("edmIsShownBy") or [None])[0]
    if not lab or not full:
        return None
    prov = ((i.get("dataProvider") or [""])[0])[:40]
    return {"ref": f"europeana:{i['id']}", "title": (i.get("title") or [""])[0], "license": lab,
            "artist": ((i.get("dcCreator") or [""])[0])[:80] or prov, "thumb": (i.get("edmPreview") or [full])[0],
            "full": full, "page": i.get("guid") or "", "provider": prov}


def search(q: str, srcs: tuple[str, ...] = ("wellcome", "artic", "europeana"), limit: int = 15) -> list[dict]:
    out = []
    for s in srcs:
        try:
            if s == "wellcome":
                d = _json("https://api.wellcomecollection.org/catalogue/v2/images", query=q, pageSize=40, **{"locations.license": "cc-0,cc-by,pdm"})
                rows = [_wellcome(i) for i in d.get("results", [])]
            elif s == "artic":
                d = _json("https://api.artic.edu/api/v1/artworks/search", q=q, limit=40, fields="id,title,image_id,artist_display,is_public_domain")
                rows = [_artic(i) for i in d.get("data", [])]
            else:
                d = _json("https://api.europeana.eu/record/v2/search.json", wskey=os.environ.get("EUROPEANA_KEY", "api2demo"), query=q,
                          reusability="open", media="true", qf="TYPE:IMAGE", rows=40, profile="rich")
                rows = [_europeana(i) for i in d.get("items", [])]
        except Exception as e:  # noqa: BLE001 -- một kho lỗi không chặn các kho khác
            print(f"{s} lỗi: {e}")
            continue
        got = [r for r in rows if r][:limit]
        CACHE.mkdir(parents=True, exist_ok=True)
        idx = CACHE / "index.json"
        known = json.loads(idx.read_text(encoding="utf-8")) if idx.exists() else {}
        known.update({r["ref"]: r for r in got})
        idx.write_text(json.dumps(known, ensure_ascii=False), encoding="utf-8")
        out += got
    return out


def _lookup(ref: str) -> dict:
    idx = CACHE / "index.json"
    known = json.loads(idx.read_text(encoding="utf-8")) if idx.exists() else {}
    if ref in known:
        return known[ref]
    src, oid = ref.split(":", 1)
    if src == "wellcome":
        r = _wellcome(_json(f"https://api.wellcomecollection.org/catalogue/v2/images/{oid}", include="source"))
    elif src == "artic":
        r = _artic(_json(f"https://api.artic.edu/api/v1/artworks/{oid}", fields="id,title,image_id,artist_display,is_public_domain")["data"])
    elif src == "europeana":
        rec = _json(f"https://api.europeana.eu/record/v2{oid}.json", wskey=os.environ.get("EUROPEANA_KEY", "api2demo"))["object"]
        agg = (rec.get("aggregations") or [{}])[0]
        r = _europeana({"id": oid, "rights": [((agg.get("edmRights") or {}).get("def") or [""])[0]],
                        "edmIsShownBy": [agg.get("edmIsShownBy")], "title": [(rec.get("title") or {}).get("def", [""])[0]],
                        "dataProvider": [((agg.get("edmDataProvider") or {}).get("def") or [""])[0]], "guid": agg.get("edmIsShownAt")})
    else:
        raise ValueError(f"{ref}: nguồn không hỗ trợ (wellcome|artic|europeana)")
    if not r:
        raise ValueError(f"{ref}: giấy phép không dùng được (cần PD/CC0/CC BY/CC BY-SA)")
    return r


def fetch(ref: str) -> tuple[Path, str]:
    """(đường dẫn jpg, dòng ghi công). Giấy phép không dùng được -> ValueError."""
    from PIL import Image  # noqa: PLC0415
    safe = re.sub(r"[^\w-]+", "_", ref)
    CACHE.mkdir(parents=True, exist_ok=True)
    dst, meta = CACHE / f"{safe}.jpg", CACHE / f"{safe}.json"
    if dst.exists() and meta.exists():
        return dst, json.loads(meta.read_text(encoding="utf-8"))["credit"]
    r = _lookup(ref)
    r["full"] = r["full"].replace("/full/1686,/", "/full/843,/")   # chỉ mục cũ: AIC tối đa 843px
    im = Image.open(io.BytesIO(_get(r["full"])))
    if im.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", im.size, (255, 255, 255))
        im = im.convert("RGBA")
        bg.paste(im, mask=im.split()[-1])
        im = bg
    im = im.convert("RGB")
    if max(im.size) > 2400:
        im.thumbnail((2400, 2400))
    im.save(dst, quality=90)
    src = SRC_NAME[ref.split(":", 1)[0]] + (f" ({r['provider']})" if r.get("provider") else "")
    title = re.sub(r"\s+", " ", r.get("title") or "").strip()[:80]
    credit = f"{title} — {r.get('artist') or 'không rõ tác giả'}, {r['license']}, {src}"
    meta.write_text(json.dumps({**r, "credit": credit}, ensure_ascii=False, indent=1), encoding="utf-8")
    return dst, credit


if __name__ == "__main__":
    if sys.argv[1:2] == ["search"]:
        for c in search(" ".join(sys.argv[2:])):
            print(f"{c['ref']:<46} {c['license']:<14} {c['title'][:70]}")
