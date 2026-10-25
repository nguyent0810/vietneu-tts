"""Sinh catalog.md từ catalog.json (234 mẫu prompt-motion.com, phân loại 25/10/2026).

    python3 .claude/skills/motion-library/references/prompt_motion/build_catalog.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
GROUPS = {
    "A": "Dòng thời gian, tiến trình", "B": "Sơ đồ, explainer, quy trình", "C": "Bảng so sánh, thẻ trích, bản tin",
    "D": "Số liệu, biểu đồ, lật số", "E": "Xử lý ảnh tư liệu, vẽ đè, collage", "F": "Chữ động, typography",
    "G": "Không khí, tái hiện không lộ mặt", "H": "Chuyển cảnh, morph, vật dẫn", "I": "Hook short dọc",
    "J": "Showreel chung chung (prompt một câu)", "K": "Quảng cáo sản phẩm, UI, app", "L": "3D, WebGL, shader, hạt",
    "M": "Nhạc, lyric, nhịp", "N": "Nhân vật hoạt hình, mascot, game",
}
rows = json.loads((HERE / "catalog.json").read_text(encoding="utf-8"))


def cell(s, n=160):
    s = " ".join(str(s or "").split()).replace("|", "/")
    return s if len(s) <= n else s[: n - 1] + "…"


out = ["# Danh mục 234 mẫu prompt-motion.com", "",
       "Sinh tự động từ `catalog.json` bằng `build_catalog.py`. Đừng sửa tay file này, sửa JSON rồi chạy lại.", "",
       "Cột: **FS/BUD** = độ hợp kênh 0–3 (3 dùng ngay, 2 dùng được sau khi đổi màu/nội dung, 1 chỉ mượn ý kỹ thuật, 0 không hợp).",
       "**P** = giá trị prompt 0–3 (prompt có cấu trúc, luật đáng học). **Engine** = loại cảnh đã có làm được, hoặc `MỚI:` cần viết.", ""]
good = [r for r in rows if max(r["fit_fs"], r["fit_bud"]) >= 1 or r["prompt_value"] >= 2]
rest = [r for r in rows if r not in good]
out += [f"## 1. Mẫu có giá trị cho kênh ({len(good)} mẫu)", ""]
for g, name in GROUPS.items():
    xs = [r for r in good if r["group"] == g]
    if not xs:
        continue
    out += [f"### {g}. {name} ({len(xs)})", "",
            "| Mẫu | Khung | FS | BUD | P | Kỹ thuật | Dùng cho kênh | Engine | Khó | Lưu ý |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(xs, key=lambda r: (-(r["fit_fs"] + r["fit_bud"]), -r["prompt_value"])):
        out.append(f"| [{cell(r['title'], 50)}]({r['url']}) | {r['aspect']} | {r['fit_fs']} | {r['fit_bud']} | {r['prompt_value']} | "
                   f"{cell(r['technique'])} | {cell(r['use_for'])} | {cell(r['engine'], 80)} | {r['effort']} | {cell(r['risk'], 100)} |")
    out.append("")
out += [f"## 2. Còn lại ({len(rest)} mẫu, fit 0 và prompt không đáng học)", "",
        "Phần lớn là showreel một câu \"go all out\" hoặc quảng cáo SaaS. Giữ để tra, không dùng làm mẫu.", ""]
for g, name in GROUPS.items():
    xs = [r for r in rest if r["group"] == g]
    if xs:
        out.append(f"- **{g}. {name} ({len(xs)}):** " + " · ".join(f"[{cell(r['title'], 40)}]({r['url']})" for r in xs))
(HERE / "catalog.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print(len(good), len(rest))
