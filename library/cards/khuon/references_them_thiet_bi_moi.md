---
{
  "id": "references_them_thiet_bi_moi",
  "ten": "Thêm thiết bị mới",
  "loai": "khuon",
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
    ".claude/skills/shorts-studio/references/adding-a-device.md:1"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-26",
  "so_lieu": {},
  "mo_ta_nguon": "1. Tìm có sẵn: `npx hyperframes@0.8.75 catalog --query \"<động tác, tiếng Anh>\" --json` (Node 22). Có -> port logic (đọc nguồn read-only, không `add` vào repo nếu chỉ lấy ý). Không -> đọc rule/blueprint liên quan trong `/hyperframes-animation`. 2. File `hyperframes_short/studio/devices/<nhóm>.js`: ```js HFS.device(\"ten_thiet_bi\", { meta: { purpose: \"number\", framing: \"grid\", axis: \"X\", circle: 0, energy: \"M\" }, css: `.tt-x{position:absolute;left:100px;top:420px;color:var(--accent)}`,   // CHỈ biến token, không hex build(c, s, st, i) {          // dựng DOM trong st (.stage); KHÔNG tween ở đây; trả về mọi thứ enter cần const box = c.el(\"div\", \"tt-x\", null, st); return { box }; }, enter(c, h, t0",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---

## Trích nguồn (tự động)

Nguồn sự thật: `.claude/skills/shorts-studio/references/adding-a-device.md:1`. 1. Tìm có sẵn: `npx hyperframes@0.8.75 catalog --query "<động tác, tiếng Anh>" --json` (Node 22). Có -> port logic (đọc nguồn read-only, không `add` vào repo nếu chỉ lấy ý). Không -> đọc rule/blueprint liên quan trong `/hyperframes-animation`. 2. File `hyperframes_short/studio/devices/<nhóm>.js`: ```js HFS.device("ten_thiet_bi", { meta: { purpose: "number", framing: "grid", axis: "X", circle: 0, energy: "M" }, css: `.tt-x{position:absolute;left:100px;top:420px;color:var(--acc.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
