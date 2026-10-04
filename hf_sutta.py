"""Tra nguyên văn kinh để SOÁT lời Phật trong kịch bản BUD: bản dịch Anh của Bhikkhu Sujato (CC0) + Pali, SuttaCentral.

Ý từ scripts/fetch_phapcu.py của Youtube_Creator_V2 (04/10/2026), mở rộng cho mọi bộ: luật kênh là lời Phật chỉ
khi có kinh -> trước khi plan, đối chiếu từng câu dẫn với đúng bài kinh đã ghi số.

    python hf_sutta.py mn7                    # in bản dịch (cache chunks_cache/suttacentral/mn7.json)
    python hf_sutta.py sn47.19 --pali         # kèm Pali
    python hf_sutta.py dhp113 "hundred years" # chỉ in đoạn có cụm từ
    python hf_sutta.py cite "Trung Bộ 7"      # đổi số kinh tiếng Việt -> uid SuttaCentral

Kịch bản tiếng Việt là DIỄN Ý có ghi số kinh; không chép bản dịch Việt còn bản quyền.
Pháp Cú: uid theo khoảng kệ của SuttaCentral (dhp100-115 chứa kệ 113) -- `uid_for("dhp113")` tự đổi.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "chunks_cache" / "suttacentral"
UA = {"User-Agent": "vietneu-tts/1.0 (scripture citation check)"}
DHP = ["1-20", "21-32", "33-43", "44-59", "60-75", "76-89", "90-99", "100-115", "116-128", "129-145", "146-156",
       "157-166", "167-178", "179-196", "197-208", "209-220", "221-234", "235-255", "256-272", "273-289", "290-305",
       "306-319", "320-333", "334-359", "360-382", "383-423"]
BOOKS = {"trường bộ": "dn", "trung bộ": "mn", "tương ưng bộ": "sn", "tương ưng": "sn", "tăng chi bộ": "an",
         "tăng chi": "an", "kinh tập": "snp", "pháp cú": "dhp", "trưởng lão ni kệ": "thig", "trưởng lão tăng kệ": "thag",
         "phật thuyết như vậy": "iti", "phật tự thuyết": "ud", "tiểu bộ khuddakapatha": "kp"}


def uid_for(uid: str) -> str:
    m = re.fullmatch(r"dhp(\d+)", uid)
    if m:
        n = int(m.group(1))
        return next(f"dhp{r}" for r in DHP if int(r.split("-")[0]) <= n <= int(r.split("-")[1]))
    return uid


def cite(text: str) -> str | None:
    """'Tăng Chi Bộ 11.15' -> 'an11.15'; 'Pháp Cú 246-247' -> 'dhp246'."""
    t = text.lower()
    for name in sorted(BOOKS, key=len, reverse=True):
        m = re.search(re.escape(name) + r"\s+(\d+(?:\.\d+)?)", t)
        if m:
            return BOOKS[name] + m.group(1)
    return None


def fetch(uid: str) -> dict:
    uid = uid_for(uid.lower().replace(" ", ""))
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{uid}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    url = f"https://suttacentral.net/api/bilarasuttas/{uid}/sujato?lang=en"
    for k in range(5):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
            break
        except Exception:  # noqa: BLE001 -- mạng chập chờn: lùi dần
            if k == 4:
                raise
            time.sleep(4 * (k + 1))
    tr, root = d.get("translation_text") or {}, d.get("root_text") or {}
    if not tr:
        raise SystemExit(f"SuttaCentral không có bản Sujato cho {uid}")
    rec = {"uid": uid, "url": f"https://suttacentral.net/{uid}/en/sujato", "license": "CC0 (Bhikkhu Sujato)",
           "segments": [{"id": k, "en": v.strip(), "pi": (root.get(k) or "").strip()} for k, v in tr.items() if v.strip()]}
    f.write_text(json.dumps(rec, ensure_ascii=False, indent=0), encoding="utf-8")
    return rec


def main() -> int:
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 0
    if a[0] == "cite":
        print(cite(" ".join(a[1:])))
        return 0
    rec = fetch(a[0])
    words = [x for x in a[1:] if not x.startswith("--")]
    print(rec["url"])
    for s in rec["segments"]:
        if words and not all(w.lower() in s["en"].lower() for w in words):
            continue
        print(f"  {s['id']:<14} {s['en']}" + (f"\n  {'':<14} {s['pi']}" if "--pali" in a else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
