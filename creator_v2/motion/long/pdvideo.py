"""Bộ lọc video tư liệu riêng cho Long; tái sử dụng hf_pdvideo."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parent))
import hf_pdvideo as hf  # noqa: E402


def checked_info(ref):
    row = hf.info(ref)
    src, ident, _ = hf.parse_ref(ref)
    lic = str(row.get("license") or "")
    if src == "commons":
        if not re.search(r"\bcc0\b|public domain|\bpdm\b|^pd(?:\b|[-_])", lic, re.I) or re.search(r"\bcc\s*[- ]?by\b", lic, re.I):
            raise ValueError(f"{ref}: Commons chỉ nhận CC0, Public domain hoặc PDM; nhận {lic or 'không rõ'}")
    elif src == "ia":
        meta = hf._json(f"https://archive.org/metadata/{ident}").get("metadata") or {}
        cols = meta.get("collection") or []
        cols = {str(c).lower() for c in ([cols] if isinstance(cols, str) else cols)}
        trusted = bool(cols & hf.IA_TRUSTED_COLLECTIONS) or ident.startswith(("gov.archives.", "gov.dod."))
        community = bool(cols & {"opensource_movies", "community", "community_media"})
        basis_lic, basis = hf.ia_verdict(meta)
        year = hf._year(meta)
        pdm = "/publicdomain/mark/" in str(meta.get("licenseurl") or "").lower()
        creator = meta.get("creator") or ""
        creator = " ".join(creator) if isinstance(creator, list) else str(creator)
        government = bool(hf.IA_US_GOV.search(creator))
        if not basis_lic or (community and not trusted) or not (trusted or government or (year and year <= 1930 and pdm)):
            raise ValueError(f"{ref}: IA không đủ căn cứ lưu trữ đáng tin cậy ({basis}; collection: {', '.join(sorted(cols))})")
    elif not row.get("ok") or re.search(r"©|copyright", str(row.get("desc") or ""), re.I):
        raise ValueError(f"{ref}: NASA có bản quyền bên thứ ba hoặc giấy phép không rõ")
    return row


def prepare(scene, od, credits):
    """Trả đường dẫn dưới output và nhãn, giữ sidecar giấy phép."""
    ref = scene["pd"]
    try:
        # Lead 16/11 (HKV): pd cũng làm nền video cho cảnh chữ; nếu cảnh còn "vid" thì pd thay clip đó
        # (giữ "vid" để floor/opening_gate vẫn tính là cảnh có video nền).
        start, dur = float(scene.get("start", 0)), float(scene.get("dur", 15))
        if not (0 <= start < float('inf') and 0 < dur <= 20):
            raise ValueError("start phải >= 0, dur phải > 0 và <= 20")
        row = checked_info(ref)
        w, h = row.get("w"), row.get("h")
        fit = scene.get("fit") or ("blur" if w and h and abs(float(w) / float(h) - 4 / 3) < .08 else "cover")
        hf.CACHE = od / "pd" / "cache"
        src, _ = hf.fetch(ref, start=start, dur=dur, fit=fit)
        side = src.with_suffix(".json")
        meta = json.loads(side.read_text(encoding="utf-8"))
        digest = hashlib.sha256(f"{ref}|{start}|{dur}|{fit}".encode("utf-8")).hexdigest()[:20]
        dst = od / "pd" / f"{digest}.mp4"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        shutil.copyfile(side, dst.with_suffix(".json"))
        credits["pd:" + digest] = {"kind": "pdvideo", "ref": ref, "title": row.get("title") or ref,
                                  "source": hf.SRC_NAME[row["src"]], "license": row.get("license"), "page": row.get("page")}
        year = re.search(r"\b(?:18|19|20)\d{2}\b", str(row.get("date") or ""))
        label = scene.get("label") or ("TƯ LIỆU " + year.group() if year else "TƯ LIỆU")
        return dst, label
    except Exception as exc:
        raise ValueError(f"{ref}: {exc}") from exc


def credit_lines(od):
    path = od / "credits.json"
    credits = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    return [f"• {m['title']} — {m['source']} — {m['license']} — {m['page']}"
            for m in credits.values() if isinstance(m, dict) and m.get("kind") == "pdvideo"]
