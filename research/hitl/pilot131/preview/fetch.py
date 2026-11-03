"""Tải ảnh Commons cho pilot #131 bằng hf_commons.fetch (thumbnail chuẩn 1920/1280, kiểm giấy phép, cache chung).
Ghi assets/<topic>/credits.json: title, local (đường cache), license, credit, w, h, sha1. Ảnh trùng nội dung bị loại."""
import hashlib, json, sys, time
from pathlib import Path

sys.path.insert(0, "/home/ubuntu/vietneu-tts")
import hf_commons
from PIL import Image

sets = json.load(open(sys.argv[1]))
root = Path("/home/ubuntu/pilot131/assets")
seen = {}
for topic, files in sets.items():
    d = root / topic
    d.mkdir(parents=True, exist_ok=True)
    cp = d / "credits.json"
    cred = json.loads(cp.read_text()) if cp.exists() else []
    for c in cred:
        seen[c["sha1"]] = c["title"]
    have = {c["title"] for c in cred}
    for f in files:
        if f in have:
            continue
        for k in range(4):
            try:
                p, credit = hf_commons.fetch(f, allow_by=True)
                break
            except ValueError as e:  # giấy phép không dùng được
                print("LICENSE", f, e, flush=True)
                p = None
                break
            except Exception as e:  # noqa: BLE001 -- 429: chờ lâu rồi thử lại
                print("  retry", k, f, str(e)[:80], flush=True)
                p = None
                time.sleep(90 * (k + 1))
        if not p:
            print("FAIL", f, flush=True)
            continue
        h = hashlib.sha1(p.read_bytes()).hexdigest()
        if h in seen:
            print("DUP", f, "=", seen[h], flush=True)
            continue
        seen[h] = f
        im = Image.open(p)
        meta = json.loads(p.with_suffix(".json").read_text()) if p.with_suffix(".json").exists() else {}
        cred.append({"title": f, "local": str(p), "lic": meta.get("license", ""), "credit": credit,
                     "w": im.width, "h": im.height, "sha1": h})
        cp.write_text(json.dumps(cred, ensure_ascii=False, indent=1))
        print(topic, meta.get("license", ""), p.name, im.size, flush=True)
        time.sleep(12)
print("DONE", flush=True)
