# GH-228: CL Long 3 Đông Lăng, bước 2 (tư liệu) và bộ khung hình

**Đầu vào:** `data/long/dong-lang/plan.md` (Lead duyệt), báo cáo đề `docs/pm/tickets/GH-228-cl-long3-topics-report.md`.

Làm như Hòa Thân: xem `docs/pm/tickets/GH-179-hoathan-research-agy.md` và `GH-179-hoathan-visual-agy.md`.

**Việc:**
1. Chạy `python motion/long/research_long.py dong-lang`, tìm theo các bài:
   - Sun Dianying;
   - Eastern Qing Tombs;
   - Yuling (Qianlong mausoleum);
   - Ding Dongling;
   - Empress Dowager Cixi;
   - Qianlong Emperor;
   - Puyi;
   - Dongling looting (nếu có bài);
   - Warlord Era;
   - Republic of China (1912–1949).

   Bổ sung bằng `media_search.py` (artic, europeana). Soát contact sheet, đếm ảnh dùng được cho từng chương, mục tiêu ≥ 50 ảnh.
2. Viết `data/long/dong-lang/visual_plan.md`:
   - 14 chương, nhịp 3–5 giây;
   - nhóm A ≥ 50%, B+C ≤ 25%, D chiếm 20–30%. Ở Hòa Thân, D chỉ đạt 7%;
   - luật nhóm B/C như Hòa Thân: không vẽ người thật bằng AI, không chữ Hán, không ấn triện giả, không cảnh bạo lực hay nổ mìn chi tiết.
3. Gom mọi prompt AI vào `data/long/dong-lang/ai_prompts.md`. Mỗi mục có tiêu đề `## ai_NN.png — CHxx: …` hoặc `## vid_NN.mp4 — CHxx: …` và một dòng `- Prompt (tiếng Anh): …`. Tối đa 16 ảnh và 6 clip. Trước khi xin ảnh mới, tra kho chung (`python ../library/tools/assets.py find`, tag `cl`/`hinh_su`).

**Được ghi:**
- `output/long/dong-lang/*` (do script tạo);
- `visual_plan.md`, `ai_prompts.md`;
- báo cáo `docs/pm/tickets/GH-228-donglang-research-report.md`.

Ghi UTF-8. Không viết kịch bản, không render, không commit.
