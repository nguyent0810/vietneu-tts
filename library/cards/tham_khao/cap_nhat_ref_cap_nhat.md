---
{
  "id": "cap_nhat_ref_cap_nhat",
  "ten": "cap nhat",
  "loai": "tham_khao",
  "dinh_dang": [],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [],
  "cam_ngach": [],
  "so_muc": 1,
  "so_nguon": 1,
  "nguon": [],
  "bang_chung_dung": [],
  "vi_du": [],
  "nguon_su_that": [
    ".claude/skills/motion-library/references/prompt_motion/cap_nhat.py:1"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-27",
  "so_lieu": {},
  "dang_dung_o": {},
  "mo_ta_nguon": "Chỉ đọc trang công khai, nghỉ 0,5 s giữa hai trang, không tải video. Chạy bằng python có chứng chỉ SSL (.venv): .venv/bin/python .claude/skills/motion-library/references/prompt_motion/cap_nhat.py /tmp/pm_raw Mục đã có trong items_raw.json được bỏ qua; mục mới cần phân loại theo khoá của catalog.json rồi chạy build_catalog.py. \"\"\" import re, json, html, time, sys, urllib.request from pathlib import Path D = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(\".\") out = D / \"items_raw.json\" sm = urllib.request.urlopen(urllib.request.Request(\"https://prompt-motion.com/sitemap.xml\", headers={\"User-Agent\": \"Mozilla/5.0\"}), timeout=30).read().decode() SKIP = re.compile(r\"/(templates|customize|blog|ta",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---
## Trích nguồn (tự động)

Nguồn sự thật: `.claude/skills/motion-library/references/prompt_motion/cap_nhat.py:1`. Chỉ đọc trang công khai, nghỉ 0,5 s giữa hai trang, không tải video. Chạy bằng python có chứng chỉ SSL (.venv): .venv/bin/python .claude/skills/motion-library/references/prompt_motion/cap_nhat.py /tmp/pm_raw Mục đã có trong items_raw.json được bỏ qua; mục mới cần phân loại theo khoá của catalog.json rồi chạy build_catalog.py. """ import re, json, html, time, sys, urllib.request from pathlib import Path D = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".") out = D / "items.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
