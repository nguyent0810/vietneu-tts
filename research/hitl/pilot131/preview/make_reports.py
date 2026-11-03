"""Sinh qa_report.md cho từng video + out/REPORT.md tổng hợp (pilot #131)."""
import json
from pathlib import Path
R = Path("/home/ubuntu/pilot131"); OUT = R / "out"
notes = json.loads((R / "qa_notes.json").read_text())
rows = []
for d in sorted(p for p in OUT.iterdir() if p.is_dir()):
    st = json.loads((d / "status.json").read_text()) if (d / "status.json").exists() else {}
    n = notes.get(d.name, {})
    L = [f"# QA preview · {d.name}", "",
         f"- Chủ đề: {st.get('topic')} · phương án **{st.get('candidate_id')} v{st.get('version')}**",
         f"- content_sha256: `{st.get('content_sha256')}`",
         f"- candidates_file_sha256: `{st.get('candidates_file_sha256')}`",
         f"- Trạng thái duyệt: **{st.get('approval_status')}**" + (f" — {st['approval_note']}" if st.get('approval_note') else ""),
         f"- Title: {st.get('title')} · Thumbnail: {st.get('thumbnail_text')}",
         f"- Render: **{st.get('render_status')}** {st.get('error') or ''} · máy: {st.get('host')}",
         f"- Thời lượng: {st.get('duration_s')} s · thời gian render: {st.get('wall_s')} s · RAM đỉnh: {st.get('peak_ram_mb')} MB",
         f"- Âm thanh: {st.get('loudness')}", "",
         "## Nguồn", *[f"- {x}" for x in n.get("sources", [])], "",
         "## Fact đã dùng", "- " + ", ".join(n.get("facts_used", [])), "",
         "## Lỗi / điểm còn tồn tại", *[f"- {x}" for x in n.get("open_issues", [])], "",
         "## Cảnh cần PO chú ý", *[f"- {x}" for x in n.get("watch", [])], "",
         "## File", "- final_preview.mp4 · contact_sheet.jpg · first_frame.jpg · timing.json · status.json · render.log · mem_samples.txt", ""]
    (d / "qa_report.md").write_text("\n".join(L), encoding="utf-8")
    rows.append(st)
(OUT / "REPORT.md").write_text("# Pilot #131 · preview SS tier+ trên Oracle\n\n| Video | Phương án | Duyệt | Render | Dài (s) | Render (s) | RAM đỉnh (MB) |\n|---|---|---|---|---|---|---|\n" +
    "\n".join(f"| {r.get('job_id')} | {r.get('candidate_id')} v{r.get('version')} | {r.get('approval_status')} | {r.get('render_status')} | {r.get('duration_s')} | {r.get('wall_s')} | {r.get('peak_ram_mb')} |" for r in rows) + "\n", encoding="utf-8")
print("ok", len(rows))
