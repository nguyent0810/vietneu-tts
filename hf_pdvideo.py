"""Video tư liệu PHẠM VI CÔNG CỘNG / CC cho video dài BUD/FS (bù chỗ trống: trước đây "video" = chỉ Pexels).

Nguồn (kênh bật kiếm tiền -> chỉ PD / PDM / CC0 / CC BY / CC BY-SA; KHÔNG NC/ND):
- commons : Wikimedia Commons (webm/ogv/mpeg) -- giấy phép lấy từ extmetadata LicenseShortName.
- ia      : Internet Archive -- chỉ nhận item có licenseurl PD/CC0/CC BY/BY-SA, hoặc thuộc bộ Prelinger
            (Prelinger Archives tuyên bố phạm vi công cộng) mà không ghi quyền hạn chế. Kiểm TỪNG item.
- nasa    : NASA Image and Video Library (tác phẩm của chính phủ Mỹ = phạm vi công cộng; bỏ item ghi ©).

    python hf_pdvideo.py search "Gabriel Veyre" [--src commons|ia|nasa] [--n 20]
    python hf_pdvideo.py search "Category:Films by Gabriel Veyre"           # liệt kê video trong 1 thể loại Commons
    python hf_pdvideo.py info  "ia:Tin-Minh-1918"                            # giấy phép + danh sách file video
    python hf_pdvideo.py strip "commons:File:X.webm" [--n 8]                # dải khung hình + mốc giây để chọn đoạn
    python hf_pdvideo.py fetch "commons:File:X.webm" --start 12 --dur 15 [--fit cover|pad|blur]
    media spec trong plan: {"kind": "pdvideo", "ref": "commons:File:X.webm", "start": 12, "dur": 15,
                            "fit": "cover", "label": "TƯ LIỆU 1900"}

Tham chiếu (ref): commons:File:<tên>  |  ia:<identifier>[/<tên file>]  |  nasa:<nasa_id>
Đầu ra: chunks_cache/pdvideo/<ref>_<start>_<dur>_<fit>.mp4 (H.264, không tiếng, 1920x1080, 30 fps, tối đa 20 s)
        + .json cùng tên (tiêu đề, trang nguồn, tác giả, giấy phép, url gốc, đoạn cắt) -- GIỮ file .json (bằng chứng).
ffmpeg đọc thẳng url với -ss trước -i (HTTP range) -> không tải cả phim 300 MB để lấy 15 giây.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "chunks_cache" / "pdvideo"
UA_STR = "vietneu-tts/1.0 (educational documentaries; Buddhism & feng shui channels)"
UA = {"User-Agent": UA_STR}
MAX_DUR = 20.0
FITS = ("cover", "pad", "blur")
SRC_NAME = {"commons": "Wikimedia Commons", "ia": "Internet Archive", "nasa": "NASA"}
VIDEO_EXT = re.compile(r"\.(webm|ogv|ogg|mpe?g|mp4|m4v|mov|mkv|avi)$", re.I)
# Bản phục chế/trích từ phim tài liệu mới (vd "from the film «Lumière, l'aventure continue» 2025") -> rủi ro Content ID.
RISK = re.compile(r"restor|remaster|from the (?:film|documentary)|©|copyright|\b(?:19[89]\d|20[0-3]\d)\b.*\bfilm\b", re.I)


# ---------------- giấy phép ----------------
def ok_license(lic: str) -> bool:
    """PD / PDM / CC0 / CC BY / CC BY-SA (mọi phiên bản). NC, ND, "fair use", rỗng -> False."""
    import hf_commons  # noqa: PLC0415 -- dùng chung bộ lọc với ảnh để hai nơi không lệch nhau
    return bool(lic) and hf_commons.ok_license(lic.strip(), allow_by=True)


def license_from_url(url: str | None) -> str:
    """licenseurl của Internet Archive -> nhãn ngắn ("CC BY-SA 4.0", "Public Domain Mark 1.0"...). NC/ND/lạ -> ""."""
    u = (url or "").lower().strip()
    if "creativecommons.org" not in u:
        return ""
    ver = (re.search(r"/(\d(?:\.\d)?)/?", u.split("creativecommons.org", 1)[1]) or [None, ""])[1]
    if "/publicdomain/zero" in u:
        return f"CC0 {ver or '1.0'}"
    if "/publicdomain/mark" in u or "/publicdomain/" in u:
        return f"Public Domain Mark {ver or '1.0'}"
    m = re.search(r"/licenses/([a-z-]+)/", u)
    kind = (m.group(1) if m else "")
    if kind in ("by", "by-sa"):
        return f"CC {kind.upper()}{' ' + ver if ver else ''}"
    return ""


# ---------------- tham chiếu ----------------
def parse_ref(ref: str) -> tuple[str, str, str | None]:
    """'commons:File:X.webm' -> ('commons', 'File:X.webm', None); 'ia:id/a b.mp4' -> ('ia', 'id', 'a b.mp4');
    'nasa:abc' -> ('nasa', 'abc', None). Sai dạng -> ValueError."""
    src, sep, rest = (ref or "").strip().partition(":")
    src, rest = src.lower(), rest.strip()
    if not sep or not rest:
        raise ValueError(f"ref video lạ {ref!r} (cần commons:File:..., ia:<id>[/file], nasa:<id>)")
    if src == "commons":
        name = rest if rest.lower().startswith("file:") else "File:" + rest
        if not VIDEO_EXT.search(name):
            raise ValueError(f"{ref}: không phải file video (webm/ogv/mpeg...)")
        return "commons", "File:" + name.split(":", 1)[1].replace("_", " "), None
    if src == "ia":
        ident, _, file = rest.partition("/")
        if not re.fullmatch(r"[\w.-]+", ident):
            raise ValueError(f"{ref}: identifier Internet Archive không hợp lệ")
        return "ia", ident, (file or None)
    if src == "nasa":
        if not re.fullmatch(r"[\w .,'()-]+", rest):     # nasa_id có thể chứa khoảng trắng
            raise ValueError(f"{ref}: nasa_id không hợp lệ")
        return "nasa", rest, None
    raise ValueError(f"nguồn video lạ {src!r} (có: commons, ia, nasa)")


def clip_window(start, dur, total: float | None = None) -> tuple[float, float]:
    """Chuẩn hoá đoạn cắt: start ≥ 0, 0 < dur ≤ MAX_DUR, không vượt quá cuối phim (nếu biết độ dài)."""
    s, d = max(0.0, float(start or 0)), float(dur if dur is not None else 15)
    if d <= 0:
        raise ValueError(f"dur phải > 0 (nhận {dur})")
    d = min(d, MAX_DUR)
    if total:
        if s >= total - 0.5:
            raise ValueError(f"start {s}s vượt độ dài phim {total:.1f}s")
        d = min(d, total - s)
    return round(s, 2), round(d, 2)


def credit_line(meta: dict) -> str:
    """'tiêu đề — tác giả, giấy phép, nguồn' (cùng dạng ext/openverse để _short_credit bỏ tiêu đề)."""
    title = " ".join((meta.get("title") or "").split())[:90]
    author = " ".join((meta.get("author") or "").split())[:60]
    return f"{title} — {author + ', ' if author else ''}{meta.get('license', '')}, {SRC_NAME.get(meta.get('src'), meta.get('src', ''))}"


def cache_paths(ref: str, start: float, dur: float, fit: str) -> tuple[Path, Path]:
    safe = re.sub(r"[^\w.-]+", "_", ref.replace("File:", ""))[:110].strip("_")
    stem = f"{safe}_{start:g}_{dur:g}_{fit}"
    return CACHE / f"{stem}.mp4", CACHE / f"{stem}.json"


# ---------------- mạng ----------------
def _get(url: str, tries: int = 5) -> bytes:
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return r.read()
        except urllib.error.HTTPError as e:   # 429: tôn trọng Retry-After của Wikimedia
            if k == tries - 1 or e.code in (400, 403, 404):
                raise
            wait = int(e.headers.get("Retry-After") or 0) if e.code == 429 else 0
            time.sleep(max(wait, 3 * (k + 1)) + 1)
        except Exception:  # noqa: BLE001 -- mạng chập chờn: lùi dần
            if k == tries - 1:
                raise
            time.sleep(3 * (k + 1))
    raise RuntimeError("unreachable")


def _json(url: str, **params) -> dict:
    return json.loads(_get(url + ("?" + urllib.parse.urlencode(params, doseq=True) if params else "")))


def _commons_api(**params) -> dict:
    params |= {"format": "json", "formatversion": "2"}
    time.sleep(1.0)
    return _json("https://commons.wikimedia.org/w/api.php", **params)


def _strip(html: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", html or "").split())


# ---------------- Commons ----------------
def _commons_row(p: dict) -> dict | None:
    vi = (p.get("videoinfo") or p.get("imageinfo") or [{}])[0]
    em = vi.get("extmetadata") or {}
    if not vi or not str(vi.get("mime", "")).startswith(("video", "application/ogg")):
        return None
    if not vi.get("width"):        # .ogg chỉ có tiếng
        return None
    lic = (em.get("LicenseShortName") or {}).get("value", "")
    desc = _strip((em.get("ImageDescription") or {}).get("value", ""))
    credit = _strip((em.get("Credit") or {}).get("value", ""))
    return {"ref": f"commons:{p['title']}", "src": "commons", "title": p["title"].split(":", 1)[1].rsplit(".", 1)[0],
            "license": lic, "ok": ok_license(lic), "author": _strip((em.get("Artist") or {}).get("value", ""))[:80],
            "dur": round(float(vi.get("duration") or 0), 1), "w": vi.get("width"), "h": vi.get("height"),
            "date": re.sub(r"\s*date QS:.*", "", _strip((em.get("DateTimeOriginal") or {}).get("value", "")))[:30],
            "page": vi.get("descriptionurl") or "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(p["title"].replace(" ", "_")),
            "url": vi.get("url", "").split("?")[0], "derivatives": vi.get("derivatives") or [],
            "desc": desc[:300], "risk": bool(RISK.search(credit)), "credit_note": credit[:160]}


VI_PROPS = "url|size|mime|extmetadata"


def _commons_search(q: str, n: int) -> list[dict]:
    if q.lower().startswith("category:"):
        d = _commons_api(action="query", generator="categorymembers", gcmtitle=q, gcmtype="file", gcmlimit=min(n, 200),
                         prop="videoinfo", viprop=VI_PROPS)
    else:
        d = _commons_api(action="query", generator="search", gsrnamespace=6, gsrsearch=f"{q} filetype:video",
                         gsrlimit=min(n, 50), prop="videoinfo", viprop=VI_PROPS)
    rows = [_commons_row(p) for p in (d.get("query") or {}).get("pages", [])]
    return [r for r in rows if r]


def _commons_info(name: str) -> dict:
    d = _commons_api(action="query", titles=name, prop="videoinfo", viprop=VI_PROPS + "|derivatives")
    pages = (d.get("query") or {}).get("pages", [])
    if not pages or pages[0].get("missing"):
        raise ValueError(f"commons:{name}: không có trên Commons")
    row = _commons_row(pages[0])
    if not row:
        raise ValueError(f"commons:{name}: không phải video có hình")
    # upload.wikimedia.org hay trả 429 cho bản GỐC với máy không phải trình duyệt, còn bản chuyển mã (transcoded/*.vp9.webm)
    # thì tải được -> thử bản chuyển mã cao nhất (≤ 1080p) trước, bản gốc sau cùng.
    ders = [x for x in row["derivatives"] if "/transcoded/" in x.get("src", "") and "webm" in (x.get("type") or "") and x.get("height")]
    ders = sorted((x for x in ders if int(x["height"]) <= 1080), key=lambda x: -int(x["height"]))
    row["media_urls"] = [x["src"] for x in ders] + [row["url"]]
    row["media_url"] = row["media_urls"][0]
    return row


# ---------------- Internet Archive ----------------
# Giấy phép trên IA do NGƯỜI TẢI LÊN tự khai -> rất hay sai (thấy 14/10/2026: "A Better Tomorrow" CC BY 4.0,
# "Little Buddha 1993" PDM, phim BBC 2021 PDM, "Rambo 4" CC0). Vì vậy KHÔNG tin licenseurl một mình; chỉ nhận khi có căn cứ:
#   1. bộ sưu tập tin cậy (Prelinger, FedFlix/NARA, phim chính phủ Mỹ) hoặc tác giả là cơ quan liên bang Mỹ;
#   2. licenseurl PD/CC0 VÀ năm phát hành <= PD_YEAR (ở Mỹ, tác phẩm xuất bản trước 1931 đã hết bảo hộ năm 2026);
#   3. item đã kiểm tay trong IA_VERIFIED (ghi lý do).
IA_TRUSTED_COLLECTIONS = {"prelinger", "fedflix", "usgovfilms", "nasa", "national_archives", "usnationalarchives"}
IA_US_GOV = re.compile(r"united states\.|^u\.s\. |national archives|nasa\b|department of (?:the )?(?:army|navy|agriculture|interior|defense)"
                       r"|fish and wildlife|national park service", re.I)
PD_YEAR = 1930
IA_VERIFIED: dict[str, str] = {
    # identifier: căn cứ (đã đọc trang item + tra luật). Thêm tay, kèm lý do.
}
IA_FORMAT_RANK = {"h.264": 0, "h.264 hd": 0, "mpeg4": 1, "512kb mpeg4": 2, "h.264 ia": 2, "matroska": 3,
                  "ogg video": 4, "mpeg2": 5, "quicktime": 6, "cinepack": 9}


def _year(meta: dict) -> int | None:
    for k in ("year", "date"):
        m = re.search(r"\b(1[89]\d\d|20\d\d)\b", str(meta.get(k) or ""))
        if m:
            return int(m.group(1))
    return None


def ia_verdict(meta: dict) -> tuple[str, str]:
    """(nhãn giấy phép, căn cứ) cho một item IA, kiểm TỪNG item; không đủ căn cứ -> ("", lý do loại)."""
    lic = license_from_url(meta.get("licenseurl"))
    raw = (meta.get("licenseurl") or "").strip()
    if raw and not lic:
        return "", f"licenseurl NC/ND/lạ ({raw})"
    cols = meta.get("collection") or []
    cols = {c.lower() for c in ([cols] if isinstance(cols, str) else cols)}
    rights = " ".join(meta.get("rights") if isinstance(meta.get("rights"), list) else [str(meta.get("rights") or "")]).lower()
    if re.search(r"all rights reserved|non-?commercial|no derivative", rights):
        return "", f"rights ghi hạn chế ({rights[:60]})"
    ident = str(meta.get("identifier") or "")
    creator = " ".join(meta.get("creator") if isinstance(meta.get("creator"), list) else [str(meta.get("creator") or "")])
    if ident in IA_VERIFIED:
        return (lic or "Public domain"), "kiểm tay: " + IA_VERIFIED[ident]
    if "prelinger" in cols:
        return (lic or "Public domain (Prelinger Archives)"), "bộ Prelinger Archives"
    if cols & IA_TRUSTED_COLLECTIONS or ident.startswith(("gov.archives.", "gov.dod.")):
        return (lic or "Public domain (US federal work)"), "bộ sưu tập chính phủ Mỹ (" + ", ".join(sorted(cols & IA_TRUSTED_COLLECTIONS) or ["gov"]) + ")"
    if lic and IA_US_GOV.search(creator) and ("public domain" in lic.lower() or lic.startswith("CC0")):
        return lic, f"tác phẩm cơ quan liên bang Mỹ ({creator[:50]})"
    y = _year(meta)
    if lic and ("public domain" in lic.lower() or lic.startswith("CC0")) and y and y <= PD_YEAR:
        return lic, f"phát hành {y} (<= {PD_YEAR}: hết bảo hộ ở Mỹ)"
    return "", "giấy phép do người tải lên tự khai, không kiểm chứng được" if lic else "không có giấy phép"


def ia_license(meta: dict) -> str:
    return ia_verdict(meta)[0]


def _ia_search(q: str, n: int) -> list[dict]:
    d = _json("https://archive.org/advancedsearch.php",
              q=f"({q}) AND mediatype:movies AND (licenseurl:*creativecommons* OR collection:prelinger OR collection:fedflix)",
              **{"fl[]": ["identifier", "title", "licenseurl", "collection", "year", "date", "creator", "rights"],
                 "sort[]": "downloads desc", "rows": n * 2, "output": "json"})
    out = []
    for x in (d.get("response") or {}).get("docs", []):
        lic, basis = ia_verdict(x)
        if not lic:
            continue
        out.append({"ref": f"ia:{x['identifier']}", "src": "ia", "title": str(x.get("title") or "")[:90], "license": lic, "ok": True,
                    "author": str(x.get("creator") or "")[:60], "date": str(x.get("year") or x.get("date") or "")[:10],
                    "dur": None, "w": None, "h": None, "basis": basis,
                    "page": f"https://archive.org/details/{x['identifier']}", "risk": False})
        if len(out) >= n:
            break
    return out


def _ia_info(ident: str, file: str | None) -> dict:
    d = _json(f"https://archive.org/metadata/{ident}")
    m = d.get("metadata") or {}
    if not m:
        raise ValueError(f"ia:{ident}: không có item")
    lic, basis = ia_verdict(m)
    vids = [f for f in d.get("files", []) if VIDEO_EXT.search(f.get("name", "")) and "thumbs/" not in f.get("name", "")]
    if file:
        pick = next((f for f in vids if f["name"] == file), None)
        if not pick:
            raise ValueError(f"ia:{ident}: không có file video {file!r} (có: {[f['name'] for f in vids][:8]})")
    else:
        # file đầu tiên (theo tên) ở định dạng tốt nhất; phim nhiều tập thì ghi rõ ia:<id>/<file>
        if not vids:
            raise ValueError(f"ia:{ident}: item không có file video")
        pick = min(vids, key=lambda f: (IA_FORMAT_RANK.get((f.get("format") or "").lower(), 7), f["name"]))
    def _f(k):
        try:
            return float(pick.get(k) or 0) or None
        except (TypeError, ValueError):
            return None
    length = pick.get("length")
    try:
        total = float(length) if length and ":" not in str(length) else (
            sum(float(p) * 60 ** i for i, p in enumerate(reversed(str(length).split(":")))) if length else None)
    except ValueError:
        total = None
    creator = m.get("creator")
    return {"ref": f"ia:{ident}/{pick['name']}", "src": "ia", "title": str(m.get("title") or ident)[:120], "license": lic,
            "ok": bool(lic), "author": (", ".join(creator) if isinstance(creator, list) else str(creator or ""))[:80],
            "date": str(m.get("date") or m.get("year") or "")[:20], "dur": total, "w": _f("width"), "h": _f("height"),
            "page": f"https://archive.org/details/{ident}", "license_url": m.get("licenseurl") or "", "basis": basis,
            "media_url": f"https://archive.org/download/{ident}/{urllib.parse.quote(pick['name'])}",
            "files": [f"{f['name']} [{f.get('format')}, {f.get('length') or '?'}s]" for f in vids][:30],
            "risk": bool(RISK.search(str(m.get("rights") or ""))), "desc": _strip(str(m.get("description") or ""))[:300]}


# ---------------- NASA ----------------
def _nasa_row(it: dict) -> dict:
    m = (it.get("data") or [{}])[0]
    text = " ".join(str(m.get(k) or "") for k in ("description", "secondary_creator", "photographer", "keywords"))
    third = bool(re.search(r"©|copyright", text, re.I))
    return {"ref": f"nasa:{m.get('nasa_id')}", "src": "nasa", "title": (m.get("title") or "")[:90],
            "license": "" if third else "Public domain (NASA)", "ok": not third,
            "author": f"NASA{(' ' + m['center']) if m.get('center') else ''}", "date": (m.get("date_created") or "")[:10],
            "dur": None, "w": None, "h": None, "page": f"https://images.nasa.gov/details/{m.get('nasa_id')}",
            "risk": third, "desc": _strip(m.get("description") or "")[:300]}


def _nasa_search(q: str, n: int) -> list[dict]:
    d = _json("https://images-api.nasa.gov/search", q=q, media_type="video", page_size=n)
    return [r for r in (_nasa_row(it) for it in (d.get("collection") or {}).get("items", [])) if r["ok"]][:n]


def _nasa_info(nid: str) -> dict:
    d = _json("https://images-api.nasa.gov/search", nasa_id=nid)
    items = (d.get("collection") or {}).get("items", [])
    if not items:
        raise ValueError(f"nasa:{nid}: không có")
    row = _nasa_row(items[0])
    assets = [u for u in json.loads(_get(f"https://images-assets.nasa.gov/video/{urllib.parse.quote(nid)}/collection.json"))]
    mp4 = [u for u in assets if u.lower().endswith(".mp4")]
    pref = next((u for tag in ("~large.mp4", "~orig.mp4", "~medium.mp4", "~mobile.mp4") for u in mp4 if u.endswith(tag)), None)
    if not pref:
        raise ValueError(f"nasa:{nid}: không có bản mp4")
    row["media_url"] = pref.replace("http://", "https://").replace(" ", "%20")
    return row


# ---------------- API công khai ----------------
def search(query: str, src: str = "commons", n: int = 20) -> list[dict]:
    """Ứng viên đã qua cửa giấy phép (commons: in cả item bị loại kèm cờ ok=False để thấy lý do)."""
    fn = {"commons": _commons_search, "ia": _ia_search, "nasa": _nasa_search}[src]
    return fn(query, n)


def info(ref: str) -> dict:
    """Siêu dữ liệu + url phát được của một video (chưa tải). Không kiểm giấy phép -- fetch() mới chặn."""
    src, ident, file = parse_ref(ref)
    if src == "commons":
        return _commons_info(ident)
    if src == "ia":
        return _ia_info(ident, file)
    return _nasa_info(ident)


def _probe(path_or_url: str) -> dict:
    r = subprocess.run(["ffprobe", "-v", "error", "-user_agent", UA_STR, "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:format=duration", "-of", "json", path_or_url], capture_output=True, text=True, timeout=120)
    try:
        d = json.loads(r.stdout or "{}")
        st = (d.get("streams") or [{}])[0]
        return {"w": st.get("width"), "h": st.get("height"), "dur": float((d.get("format") or {}).get("duration") or 0) or None}
    except (ValueError, TypeError):
        return {}


MAX_DOWNLOAD = 600 * 1024 * 1024


def _download(url: str, ref: str) -> Path:
    """Tải nguyên file nguồn (có cache) theo từng khúc, tôn trọng Retry-After; quá MAX_DOWNLOAD -> ValueError."""
    srcdir = CACHE / "src"
    srcdir.mkdir(parents=True, exist_ok=True)
    ext = (re.search(r"\.(webm|ogv|ogg|mpe?g|mp4|m4v|mov|mkv)(?:\?|$)", url.split("?")[0], re.I) or [None, "bin"])[1]
    out = srcdir / (re.sub(r"[^\w.-]+", "_", VIDEO_EXT.sub("", ref.replace("File:", "")))[:110].strip("_") + "." + ext)
    if out.exists() and out.stat().st_size > 10_000:
        return out
    part = out.with_name(out.name + ".part")
    for k in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r, open(part, "wb") as fh:
                size = int(r.headers.get("Content-Length") or 0)
                if size > MAX_DOWNLOAD:
                    raise ValueError(f"{ref}: file nguồn {size / 1e6:.0f} MB quá lớn")
                while chunk := r.read(1 << 20):
                    fh.write(chunk)
            if size and part.stat().st_size != size:
                raise OSError(f"tải thiếu {part.stat().st_size}/{size}")
            part.replace(out)
            return out
        except urllib.error.HTTPError as e:
            if k == 2 or e.code in (403, 404):
                raise
            time.sleep(min(60, max(int(e.headers.get("Retry-After") or 0), 5 * (k + 1))) + 1)
        except OSError:
            if k == 2:
                raise
            time.sleep(5 * (k + 1))
    raise RuntimeError("unreachable")


def vf_for(fit: str) -> str:
    if fit == "pad":
        core = ("scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos,"
                "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black")
    elif fit == "blur":   # ảnh 4:3 giữa khung, hai bên là chính khung hình làm mờ (không viền đen)
        core = ("split[a][b];[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
                "boxblur=28:2,eq=brightness=-0.10[bg];[b]scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos[fg];"
                "[bg][fg]overlay=(W-w)/2:(H-h)/2")
    else:
        core = "scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080"
    return core + ",setsar=1,fps=30,format=yuv420p"


def fetch(ref: str, start: float = 0, dur: float = 15, fit: str = "cover") -> tuple[Path, str]:
    """Cắt đoạn [start, start+dur] -> mp4 1920x1080 H.264 không tiếng (có cache), trả (đường dẫn, dòng ghi công).
    Giấy phép không dùng được -> ValueError."""
    fit = (fit or "cover").lower()
    if fit not in FITS:
        raise ValueError(f"fit lạ {fit!r} (có: {', '.join(FITS)})")
    s0, d0 = clip_window(start, dur)
    dst, meta_p = cache_paths(ref, s0, d0, fit)
    if dst.exists() and meta_p.exists():
        m = json.loads(meta_p.read_text(encoding="utf-8"))
        if not ok_license(m.get("license", "")):
            raise ValueError(f"{ref}: giấy phép '{m.get('license')}' không dùng được")
        return dst, m["credit"]
    row = info(ref)
    if not ok_license(row.get("license", "")):
        raise ValueError(f"{ref}: giấy phép '{row.get('license') or 'không rõ'}' không dùng được "
                         f"(cần PD/PDM/CC0/CC BY/CC BY-SA; không NC/ND){' -- ' + row['basis'] if row.get('basis') else ''}")
    total = row.get("dur") or _probe(row["media_url"]).get("dur")
    s, d = clip_window(s0, d0, total)
    CACHE.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(".part.mp4")
    # upload.wikimedia.org cắt luồng giữa chừng khi bị đọc nhảy (ffmpeg: "File ended prematurely") -> tải cả file
    # (video Commons thường < 100 MB) vào chunks_cache/pdvideo/src rồi cắt tại chỗ. IA/NASA chịu HTTP range tốt -> đọc thẳng.
    src_in = row["media_url"]
    if row["src"] == "commons":
        for k, u in enumerate(row["media_urls"]):
            try:
                src_in = _download(u, row["ref"])
                row["media_url"] = u
                break
            except Exception:  # noqa: BLE001 -- bản này hỏng/429 -> bản kế
                if k == len(row["media_urls"]) - 1:
                    raise
    net = [] if row["src"] == "commons" else ["-user_agent", UA_STR, "-reconnect", "1", "-reconnect_streamed", "1",
                                              "-reconnect_delay_max", "30"]
    cmd = ["ffmpeg", "-v", "error", "-y", *net, "-ss", f"{s}", "-i", str(src_in), "-t", f"{d}",
           "-an", "-sn", "-dn", "-vf", vf_for(fit), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-profile:v", "high", "-movflags", "+faststart", str(tmp)]
    err = ""
    for k in range(3):
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        if r.returncode == 0 and tmp.exists() and tmp.stat().st_size > 10_000:
            break
        err = (r.stderr or "")[-400:]
        time.sleep(10 * (k + 1) + (20 if "429" in err else 0))
    else:
        raise RuntimeError(f"{ref}: ffmpeg không cắt được ({err.strip()[:200]})")
    tmp.replace(dst)
    m = {k: row.get(k) for k in ("ref", "src", "title", "author", "license", "license_url", "basis", "date", "page", "desc", "risk")}
    m |= {"ref_asked": ref, "original_url": row["media_url"], "file_url": row.get("url") or row["media_url"], "source_w": row.get("w"), "source_h": row.get("h"),
          "source_dur": total, "start": s, "dur": d, "fit": fit, "fetched": time.strftime("%Y-%m-%d"),
          "credit_note": row.get("credit_note", "")}
    m["credit"] = credit_line(m)
    meta_p.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    if m.get("risk"):
        print(f"  ! {ref}: có dấu hiệu bản phục chế/trích phim mới -> rủi ro Content ID ({m['credit_note'][:90]})", file=sys.stderr)
    return dst, m["credit"]


def _thumb(url: str) -> "Image.Image | None":
    import io  # noqa: PLC0415
    from PIL import Image  # noqa: PLC0415
    try:
        return Image.open(io.BytesIO(_get(url, tries=3))).convert("RGB")
    except Exception:  # noqa: BLE001
        return None


def strip(ref: str, n: int = 8, out: Path | None = None) -> Path:
    """Dải n khung hình rải đều cả phim, ghi mốc giây -- để chọn --start/--dur bằng mắt mà không tải bản lớn.
    Commons: tải bản chuyển mã nhỏ nhất rồi lấy khung; IA: thư mục .thumbs có sẵn; NASA: ffmpeg lấy khung qua HTTP."""
    from PIL import Image, ImageDraw  # noqa: PLC0415
    row = info(ref)
    total = float(row.get("dur") or 0)
    frames: list[tuple[float, Image.Image | None]] = []
    if row["src"] == "commons":
        # ảnh thu nhỏ "--seek=T" của Commons trả cùng một khung (ảnh đại diện) cho mọi T -> tải bản chuyển mã NHỎ
        # nhất (240p/360p, vài MB) rồi lấy khung tại chỗ.
        lows = sorted((x for x in row.get("derivatives") or [] if "/transcoded/" in x.get("src", "")
                       and "webm" in (x.get("type") or "") and x.get("height")), key=lambda x: int(x["height"]))
        url = lows[0]["src"] if lows else row["url"]
        local = _download(url, row["ref"] + "_preview")
        total = total or _probe(str(local)).get("dur") or 0
        url_in = str(local)
    elif row["src"] == "nasa":
        total = total or _probe(row["media_url"]).get("dur") or 0
        url_in = row["media_url"]
    if row["src"] in ("commons", "nasa"):
        import io  # noqa: PLC0415
        net = ["-user_agent", UA_STR] if row["src"] == "nasa" else []
        for i in range(n):
            t = round(total * (i + 0.5) / n, 1)
            r = subprocess.run(["ffmpeg", "-v", "error", *net, "-ss", str(t), "-i", url_in, "-frames:v", "1",
                                "-vf", "scale=330:-2", "-f", "image2pipe", "-vcodec", "mjpeg", "-"], capture_output=True, timeout=120)
            frames.append((t, Image.open(io.BytesIO(r.stdout)).convert("RGB") if r.returncode == 0 and r.stdout else None))
    if row["src"] == "ia":
        _, ident, file = parse_ref(row["ref"])
        d = _json(f"https://archive.org/metadata/{ident}")
        stem = Path(file or "").stem.split(".")[0]
        th = sorted((f["name"] for f in d.get("files", []) if ".thumbs/" in f["name"]),
                    key=lambda x: int((re.search(r"_(\d{6})\.jpg$", x) or [0, 0])[1]))
        th = [x for x in th if stem[:20] in x] or th
        pick = [th[int(len(th) * (i + 0.5) / n)] for i in range(n)] if len(th) >= n else th
        for x in pick:
            t = int((re.search(r"_(\d{6})\.jpg$", x) or [0, 0])[1])
            frames.append((t, _thumb(f"https://archive.org/download/{ident}/{urllib.parse.quote(x)}")))
    W, H = 330, 186
    canvas = Image.new("RGB", (W * len(frames), H + 26), (16, 16, 20))
    dr = ImageDraw.Draw(canvas)
    for k, (t, im) in enumerate(frames):
        if im is not None:
            im.thumbnail((W - 4, H - 4))
            canvas.paste(im, (k * W + (W - im.width) // 2, (H - im.height) // 2))
        dr.text((k * W + 6, H + 6), f"{int(t) // 60}:{int(t) % 60:02d}  ({int(t)}s)", fill=(255, 220, 90))
    out = out or CACHE / "strips" / (re.sub(r"[^\w.-]+", "_", ref.replace("File:", ""))[:110] + ".jpg")
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=82)
    return out


def _fmt(r: dict) -> str:
    dur = f"{r['dur']:.0f}s" if r.get("dur") else "?"
    size = f"{r['w']}x{r['h']}" if r.get("w") else ""
    flag = "!" if r.get("risk") else ("x" if not r.get("ok") else " ")
    return f"{flag} {r['license'][:26]:<26} {dur:>6} {size:<10} {r['ref'][:95]}{'  [' + r['basis'] + ']' if r.get('basis') else ''}"


if __name__ == "__main__":
    a = sys.argv[1:]

    def opt(name, default=None):
        return a[a.index(name) + 1] if name in a else default

    pos = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or not a[i - 1].startswith("--"))]
    if len(pos) >= 2 and pos[0] == "search":
        for r in search(" ".join(pos[1:]), opt("--src", "commons"), int(opt("--n", 20))):
            print(_fmt(r))
    elif len(pos) >= 2 and pos[0] == "info":
        print(json.dumps({k: v for k, v in info(pos[1]).items() if k != "derivatives"}, ensure_ascii=False, indent=1))
    elif len(pos) >= 2 and pos[0] == "strip":
        print(strip(pos[1], int(opt("--n", 8))))
    elif len(pos) >= 2 and pos[0] == "fetch":
        print(fetch(pos[1], float(opt("--start", 0)), float(opt("--dur", 15)), opt("--fit", "cover")))
    else:
        print(__doc__)
