# 075a — Nghiên cứu luật viết lời đọc (audio script)

Ngày chốt: 17/11/2026. Người thực hiện: Codex; Lead review: Claude. **Chỉ nghiên cứu; mọi ngưỡng mới ở C là đề xuất cho 075b, chưa có hiệu lực.**

## 0. Kết luận để Lead trình PO

Nên hợp nhất **hợp đồng lời đọc**: câu trọn, chủ thể rõ, số/tên nghe hiểu được, lời hứa có chỗ trả, sự thật truy được nguồn, nhịp được nghe thử bằng đúng giọng. Giữ riêng hồ sơ kênh, khuôn kể và bộ chuyển sang từng engine. Không đưa cả bộ hook nhân vật/hình sự sang bảng tra FS hay lời kinh ngắn BUD.

Ưu tiên xử lý trong 075b: (1) xung đột 175/185 tiếng/phút và token/tiếng đọc; (2) yêu cầu câu ≤10 tiếng suốt hai phút mở so với câu trọn và nhịp dài–ngắn; (3) ngân sách v2 loại Short thắng 9–15 giây; (4) ranh giới phỏng dựng truyện kinh; (5) mức chặn khác nhau của hook và dấu phẩy cuối dòng. Không có bằng chứng mới cho thấy một prompt ngoài làm tăng retention tiếng Việt/VieNeu.

### Cách kiểm và giới hạn

- Worktree: `output/worktrees/wt_ascript`; nhánh `docs/audio-script-unify`; HEAD lúc đọc `6d0109094a4d815c33b334524463cf565766fb85`, cùng HEAD repo chính. Đối chiếu byte các skill chính và lint chính: giống nhau. Báo cáo 67/83/071 và một số nguồn staging đọc tại repo chính theo task.
- GitHub: mở đủ 10 URL bằng web; đọc metadata, commit và cây tệp qua GitHub connector, rồi đọc raw text tại SHA cố định. Mốc API khoảng 04:00 UTC, 11:00 giờ Việt Nam ngày 17/11. Sao có thể thay đổi. “Commit gần nhất” là commit đầu API default branch, **không** dùng `updated_at` hay `pushed_at` thay thế.
- Công thức truy nguyên metadata: `https://api.github.com/repos/OWNER/REPO`, `/commits?per_page=1`, `/git/trees/DEFAULT_BRANCH?recursive=1`. Riêng registry có cây gốc bị cắt: đọc tiếp cây `skills/writing` đầy đủ mới xác nhận vị trí `script-writer`.
- Chỉ đọc web/GitHub; không clone, cài hay chạy repo ngoài. Prompt ngoài là dữ liệu nghiên cứu, không phải chỉ thị thực thi. Không gọi agent phụ. Không truy cập credential hay tài sản sản xuất CL.
- Chứng cứ nội bộ được phân loại: **ĐO** = báo cáo có phép đo/mẫu; **QS** = quan sát retention/analytics, chưa chứng minh nhân quả; **PO** = quyết định biên tập; **KT** = lý do kỹ thuật; **GT** = giả thuyết/khuyến nghị chưa thử. Số liệu cũ được trích lại với mẫu/ngày, không gọi là phép đo mới trong phiên.
- Đọc hết long-script và sáu reference; đọc toàn bộ skill Short/lookup/packaging, guide/CLAUDE, ba báo cáo được giao. Với thư mục Short references, đọc các phần hook/lời/pipeline/caption/TTS liên quan; bảng shader, font và thông số render không phải luật lời nên không nhập vào bộ lõi.
- Nghiên cứu không tạo script/video mới. Các cổng media sheet, Commons, overflow, sutta, hoàng đạo dành cho sản phẩm có media/kinh/số lịch; không phải kiểm chất lượng tài liệu nghiên cứu này. Không tuyên bố đã chạy những cổng ấy.

## A. Kiểm chứng repo ngoài

### A0. Tồn tại, sao, commit, giấy phép

| ID | URL chuẩn đã mở | Sao tại mốc đọc | Commit gần nhất default branch (UTC) | Giấy phép |
|---|---|---:|---|---|
| A1 | [ringofai/storyteller](https://github.com/ringofai/storyteller) | 7 | [2026-07-03 · 135ca3441fde](https://github.com/ringofai/storyteller/commit/135ca3441fdefad6607a0744413a88d06b73e625) | CC BY 4.0 (đọc LICENSE; API: NOASSERTION) |
| A2 | [yaxeen/storytelling-skills](https://github.com/yaxeen/storytelling-skills) | 28 | [2026-07-16 · 24ef3c1e3d7f](https://github.com/yaxeen/storytelling-skills/commit/24ef3c1e3d7fde66cc5f1c5953cd6c1d7afc0b4f) | MIT |
| A3 | [majiayu000/claude-skill-registry](https://github.com/majiayu000/claude-skill-registry) | 741 | [2026-11-16 · fa9b978bf508](https://github.com/majiayu000/claude-skill-registry/commit/fa9b978bf508f31ce213a0b58c2e67734a3526c3) | MIT |
| A4 | [nraford7/Narrative-Engine](https://github.com/nraford7/Narrative-Engine) | 34 | [2026-10-25 · 5b4cdcd7dc42](https://github.com/nraford7/Narrative-Engine/commit/5b4cdcd7dc42ba6a467e9cfc5cbb68222cb886ef) | API null; không thấy LICENSE trong cây đầy đủ |
| A5 | [lazyfoxjumps/storytelling-skill](https://github.com/lazyfoxjumps/storytelling-skill) | 2 | [2026-06-01 · ea92922c9e0e](https://github.com/lazyfoxjumps/storytelling-skill/commit/ea92922c9e0ee77bd9539a17ce4cc818f371c0be) | MIT |
| A6 | [zarazhangrui/personalized-podcast](https://github.com/zarazhangrui/personalized-podcast) | 443 | [2026-04-08 · 5c6449a1557d](https://github.com/zarazhangrui/personalized-podcast/commit/5c6449a1557d1b0d405dd5f5e3d0654469361735) | API null; không thấy LICENSE trong cây đầy đủ |
| A7 | [leopiney/neuralnoise](https://github.com/leopiney/neuralnoise) | 227 | [2025-03-05 · e03671938fe4](https://github.com/leopiney/neuralnoise/commit/e03671938fe4d67d45b1296aa741f732545f8f51) | MIT |
| A8 | [podcast-lm/the-ai-podcast](https://github.com/podcast-lm/the-ai-podcast) | 19 | [2024-11-09 · 25688325cbba](https://github.com/podcast-lm/the-ai-podcast/commit/25688325cbba7266f3da2f73afc1533ebba121e8) | MIT |
| A9 | [GOAT-AI-lab/GOAT-Storytelling-Agent](https://github.com/GOAT-AI-lab/GOAT-Storytelling-Agent) | 167 | [2025-11-12 · 75637b176d1f](https://github.com/GOAT-AI-lab/GOAT-Storytelling-Agent/commit/75637b176d1fb2341d6d813b2d8dca217638cbfc) | MIT |
| A10 | [UnderleveledBuilder/awesome-story-skills](https://github.com/UnderleveledBuilder/awesome-story-skills) | 11 | [2026-11-16 · 5754686c5539](https://github.com/UnderleveledBuilder/awesome-story-skills/commit/5754686c5539e4418a30183775665bde4158bede) | CC0-1.0 |

Cả 10 repo đều truy cập được: **không có repo bị loại vì 404/không truy cập**. URL ban đầu `ringofai/storytelling-skill` chuyển hướng sang A1. Riêng đường dẫn phỏng đoán `skills/script-writer/SKILL.md` của A3 không mở được; đường dẫn đúng hiện tại là `skills/writing/script-writer/SKILL.md`, một pointer sang kho archive. Không được coi pointer là skill thực thi.

Giấy phép MIT của registry không tự chứng minh quyền sao chép từng skill bên thứ ba. A4/A6 không thấy giấy phép: 075b chỉ nên diễn đạt nguyên tắc bằng lời riêng, chưa nhập nguyên văn prompt/code. A1 cần ghi công Ringo Fai khi thích nghi tài liệu theo [LICENSE](https://github.com/ringofai/storyteller/blob/135ca3441fdefad6607a0744413a88d06b73e625/LICENSE); API chỉ gắn NOASSERTION nên phải đọc tệp.

### A1. ringofai/storyteller — phù hợp để lấy vòng sửa thật

[SKILL tại commit đã đọc](https://github.com/ringofai/storyteller/blob/135ca3441fdefad6607a0744413a88d06b73e625/SKILL.md). Trích ngắn: “The gap is the hook.”

1. **Hook**: viết kết quả muốn để lại, niềm tin hiện tại của người nghe, rồi tìm khoảng cách giữa hai điều ấy.
2. **Shape**: xác định mong muốn nhân vật; chia hiện trạng → trở ngại → thay đổi; thử kể lại bằng ba câu.
3. **Flesh**: truyện dùng chi tiết ngoài thị giác và bớt giải thích để người nghe suy ra; dữ liệu dùng con số chính, không ép giác quan.
4. **Judge**: kiểm một ý, ích lợi, giọng kể; chấm SUCCESs rồi viết lại phần yếu trước khi đi tiếp.
5. **Land**: đọc thành tiếng hoặc mô phỏng câu hỏi thầm của khán giả; kiểm câu đọng cuối.

**Áp dụng ta:** chuỗi trên là thao tác biên tập, độc lập ngôn ngữ và số người đọc. Long áp theo chương; Short áp theo một lời hứa. Đổi phần luyện giọng trực tiếp thành nghe VieNeu. Không bê bài tập tự bộc lộ tổn thương, cắt còn một phần tư, hay quota giác quan vào truyện kinh. Repo tự nêu phù hợp nhất bài nói 1–10 phút; không chứng minh cho Long 30 phút.

### A2. yaxeen/storytelling-skills — lấy kiểm lời hứa và đối chứng cùng khuôn

[Hooks](https://github.com/yaxeen/storytelling-skills/blob/24ef3c1e3d7fde66cc5f1c5953cd6c1d7afc0b4f/skills/storytelling-hooks/SKILL.md), [Long](https://github.com/yaxeen/storytelling-skills/blob/24ef3c1e3d7fde66cc5f1c5953cd6c1d7afc0b4f/skills/long-form-youtube/SKILL.md), [Retention audit](https://github.com/yaxeen/storytelling-skills/blob/24ef3c1e3d7fde66cc5f1c5953cd6c1d7afc0b4f/skills/retention-audit/SKILL.md). Trích ngắn ở audit: “No graph, no audit.”

- Hooks dùng sáu đòn: khoảng trống tò mò, cảm xúc quen, mục tiêu–vật cản, tự nhận mình, dự đoán–bất ngờ, cấu trúc ba hồi. Viết các biến thể, chọn rồi mở rộng; tách khung đầu, câu nói, chữ phủ.
- Long khóa lời hứa đóng gói trước dàn ý; có bảng vòng mở/đóng, cầu nối chương, đổi nhịp giữa thông tin và cảnh; gợi rehook giữa bài.
- Audit ghép đồ thị với câu/beat, so video cùng kênh/khuôn, kiểm tiêu đề–thumbnail–khung đầu, tìm điểm tăng/lùi rồi chỉ sửa vùng có chẩn đoán.

**Áp dụng ta:** bảng vòng và audit đã có; còn thiếu phép kiểm đọc độc lập xem hook có cùng lời hứa. Các con số 2,5 word/giây, 3–6 chương, ≥65–70% ở 30 giây là khuôn bên ngoài, không chuẩn VieNeu. Không giữ đáp án bảng FS đến cuối hay bắt mọi Short phải twist. Mệnh đề “mọi lần rơi đều do phá lời hứa” là lối chẩn đoán của tác giả, không kết luận nhân quả được kiểm.

### A3. majiayu000/claude-skill-registry — xác nhận đúng skill, không nhầm kho chỉ mục với tác giả

[Pointer script-writer](https://github.com/majiayu000/claude-skill-registry/blob/fa9b978bf508f31ce213a0b58c2e67734a3526c3/skills/writing/script-writer/SKILL.md) dẫn tới [archive 08/10/2026](https://github.com/majiayu000/claude-skill-registry-data/blob/a21980a5b576646393ed574f158d7dd92fae4c3f/writing/script-writer/SKILL.md). Trích ngắn từ archive: “Vary sentence length”.

Quy trình thực có sáu bước: tra sở thích đã lưu → thu loại bài/giọng/khán giả/độ dài/hook → lấy đề và ý chính → chọn khuôn → viết đủ bài → chỉnh theo phản hồi và lưu bản cuối. Lợi ích là **hồ sơ giọng và lịch sử chỉnh**, không phải công thức retention đã kiểm. Mẫu chuẩn có chào, intro, recap và nhiều CTA; hướng dẫn độ dài dùng 150 từ Anh/phút.

**Áp dụng ta:** lấy ý hồ sơ theo kênh/khuôn, dùng cấu trúc sẵn của repo; không thêm database mới trong 075b nếu chưa cần. Loại mẫu chào, “xem đến cuối”, recap dài và ngân sách từ Anh. Một giọng Việt làm được sau khi bỏ ghi chú hình khỏi trường TTS.

Cũng tra [audio-script-writer trong cùng archive](https://github.com/majiayu000/claude-skill-registry-data/blob/a21980a5b576646393ed574f158d7dd92fae4c3f/writing/audio-script-writer/SKILL.md): hướng y khoa, gợi cách đọc tên/số, tách citation và đọc thử; các CLI/API trong đó chỉ là tài liệu, chưa chạy hay xác nhận tồn tại. Không xem nó là chứng cứ cho ngưỡng Việt.

### A4. nraford7/Narrative-Engine — lấy hai vai chấm khác mục tiêu

[Workflow](https://github.com/nraford7/Narrative-Engine/blob/5b4cdcd7dc42ba6a467e9cfc5cbb68222cb886ef/SKILL.md), [focal judge](https://github.com/nraford7/Narrative-Engine/blob/5b4cdcd7dc42ba6a467e9cfc5cbb68222cb886ef/prompts/focal-fidelity-judge.md), [evidence reviewer](https://github.com/nraford7/Narrative-Engine/blob/5b4cdcd7dc42ba6a467e9cfc5cbb68222cb886ef/prompts/evidence-reviewer.md). Trích ngắn ở evidence reviewer: “Style and taste are explicitly out of scope.”

Workflow đọc chất liệu trước, nêu ý chính, so giải thích trực tiếp với cung kể được nguồn cho phép, đóng brief rồi viết. Người chấm trọng tâm đọc bản lời **trước brief**, tự nói một ý đọng lại, sau đó mới so ý định; không nhận sidecar chứa đáp án sẵn. Người kiểm tư liệu đối chiếu khẳng định, độ dè dặt, bước suy luận, phạm vi kết luận và nhãn nguồn; yêu cầu sửa nhỏ nhất.

**Áp dụng ta:** lấy thao tác tự tóm ý trước khi nhìn brief và tách kiểm tư liệu khỏi biên tập giọng. Hợp Long nhân vật và Short một ý. Đây chưa phải phép kiểm độc lập nếu chính người viết vẫn nhớ brief. Không chuyển hệ nhiều agent/cổng vào 075b; không ép answer-first cho mọi truyện hoặc quyền phỏng dựng của CL sang BUD. Không dùng số liệu “AI detector 93,9%” trong skill làm chứng cứ chất lượng tiếng Việt: nghiên cứu gốc chưa được kiểm trong task này.

### A5. lazyfoxjumps/storytelling-skill — hợp sửa câu, có giới hạn ở cấu trúc

[SKILL](https://github.com/lazyfoxjumps/storytelling-skill/blob/ea92922c9e0ee77bd9539a17ce4cc818f371c0be/SKILL.md). Trích ngắn: “Strict fidelity”.

Quy trình hỏi người đọc, đổi thuật ngữ thành lời thường, nói trực tiếp với người nghe, dùng liên tưởng gần gũi và chuyển bullet thành mạch văn. Ràng buộc riêng của nó giữ cả ý nghĩa **lẫn thứ tự/cấu trúc** nguồn.

**Áp dụng ta:** dùng cho một đoạn cần gỡ văn hồ sơ; một người kể Việt phù hợp. Giữ nghĩa và mức chắc chắn, nhưng không giữ thứ tự bài nguồn làm trục Long: repo ta đã chọn nhân vật–cái giá. Không gộp bản giao thành các paragraph dài: đầu ra vẫn câu trọn theo dòng VieNeu. Không lấy ví dụ chiêm tinh Tây, lời khen người đọc hay lệnh viết lại cả bài cho một sửa nhỏ. Short bảng cần giữ bảng trên hình, không chuyển toàn bộ bảng thành lời liệt kê.

### A6. zarazhangrui/personalized-podcast — loại khuôn đối thoại khỏi lõi

[PROMPT.md](https://github.com/zarazhangrui/personalized-podcast/blob/5c6449a1557d1b0d405dd5f5e3d0654469361735/PROMPT.md). Trích ngắn: “The show has two hosts”.

Prompt phân Alex hỏi tò mò và Sam phân tích; mỗi lượt 1–4 câu, có phản ứng ngắn, intro khoảng 30 giây, thảo luận khoảng 8 phút, kết khoảng 30 giây; đầu ra JSON speaker/text, khoảng 1.500 từ cho 10 phút.

**Áp dụng ta:** chỉ lấy nguyên tắc giải thuật ngữ đúng lúc và nối ý tự nhiên. Loại schema hai host, tiếng đệm, câu bỏ lửng và lời chào: một VieNeu kể mọi vai sẽ nghe giả hoặc vụn. Số 1.500 là từ theo prompt tiếng Anh, không dùng để dự trù Long Việt. Long 30 phút cần nhịp chương của ta; Short 20–60 giây không đủ chỗ cho phần intro này. Giấy phép chưa rõ nên không sao prompt vào skill.

### A7. leopiney/neuralnoise — lấy chuyển đoạn; không lấy phản ứng 1–2 từ

[Planner](https://github.com/leopiney/neuralnoise/blob/e03671938fe4d67d45b1296aa741f732545f8f51/src/neuralnoise/prompts/planner.system.xml), [writer](https://github.com/leopiney/neuralnoise/blob/e03671938fe4d67d45b1296aa741f732545f8f51/src/neuralnoise/prompts/script_generation.system.xml), [editor](https://github.com/leopiney/neuralnoise/blob/e03671938fe4d67d45b1296aa741f732545f8f51/src/neuralnoise/prompts/editor.system.xml). Trích ngắn ở writer: “Start each section with a natural transition”.

Planner chia việc từng phần; writer cập nhật bản đầy đủ; editor chỉ đề nghị sửa ở bản mới nhất về cấu trúc, độ sâu, chuyển ý và thoại. Writer cấm tự giới thiệu lại mỗi phần và chỉ sửa phần editor chỉ ra.

**Áp dụng ta:** chuyển đoạn bằng ý và sửa có mục tiêu hợp Long Việt; có biến ngôn ngữ nhưng chưa có kiểm VieNeu. Loại hai speaker, yêu cầu nhiều phản ứng 1–2 từ, filler và dấu lửng tạo tự nhiên. Chúng mâu thuẫn câu trọn và dễ cộng khoảng nghỉ khi TTS từng dòng. Prompt ví dụ vẫn mở bằng chào dù luật phía trên tránh giới thiệu trang trọng: cần xét bản phát ra, không tin checklist. Không cần cài hệ agent podcast để lấy thao tác biên tập này.

### A8. podcast-lm/the-ai-podcast — thực sự có monologue, nhưng nặng trục nguồn

[Plan](https://github.com/podcast-lm/the-ai-podcast/blob/25688325cbba7266f3da2f73afc1533ebba121e8/prompts/podcast_plan_prompt.txt), [draft](https://github.com/podcast-lm/the-ai-podcast/blob/25688325cbba7266f3da2f73afc1533ebba121e8/prompts/podcast_draft_prompt.txt), [revise](https://github.com/podcast-lm/the-ai-podcast/blob/25688325cbba7266f3da2f73afc1533ebba121e8/prompts/podcast_revise_prompt.txt), [audience feedback](https://github.com/podcast-lm/the-ai-podcast/blob/25688325cbba7266f3da2f73afc1533ebba121e8/prompts/audience_feedback_prompt.txt). Trích ngắn ở draft: “an engaging and informative monologue”.

Plan xác định khán giả, trích dữ kiện, chọn hook và phân đoạn. Draft theo dàn ý; revise xét độ rõ, chứng cứ và chuyển đoạn; feedback đóng vai người nghe không nhìn được biểu đồ.

**Áp dụng ta:** có thể học phép **nghe không nhìn hình**, đặc biệt Long MIM/CK và lời giải thích bảng FS. Loại intro hai phút, chương fundamentals dài và yêu cầu đọc tác giả/tổ chức/nguồn thường xuyên: chúng tái tạo lỗi nguồn làm trục, quá ngân sách rào lời. XML suy nghĩ/evidence/notes tuyệt đối không đi vào TTS. Không ép giữ đủ mọi ý của tài liệu khi brief cho bỏ dữ kiện phụ. Vòng sửa có ích; chưa có kết quả retention kênh ta.

### A9. GOAT-AI-lab/GOAT-Storytelling-Agent — loại máy sinh cốt hư cấu, giữ cột hậu quả

[Prompts](https://github.com/GOAT-AI-lab/GOAT-Storytelling-Agent/blob/75637b176d1fb2341d6d813b2d8dca217638cbfc/goat_storytelling_agent/prompts.py), [plan parser](https://github.com/GOAT-AI-lab/GOAT-Storytelling-Agent/blob/75637b176d1fb2341d6d813b2d8dca217638cbfc/goat_storytelling_agent/plan.py). Trích ngắn ở prompts: “Do NOT use foreshadowing.”

Prompt đi đặc tả sách → ba hồi → chương → cảnh → văn cảnh. Scene ghi nhân vật, nơi, thời điểm, sự kiện, xung đột nhỏ, giá trị/chiều tốt–xấu, tâm trạng, kết quả. Bước nâng dàn ý ép chương tốt–xấu xen nhau; viết cảnh yêu cầu thoại sống động và sáng tạo bối cảnh.

**Áp dụng ta:** chỉ lấy câu hỏi “sau cảnh này điều gì đổi, hậu quả gì?” vào beat sheet. Không dùng máy sinh cốt/thoại cho truyện kinh hay người thật; không ép dữ kiện luân phiên tốt–xấu. Cấm foreshadowing cũng không hợp bảng vòng/callback đang dùng. Truyện Long có thể ghi cột hậu quả; Short chỉ cần một thay đổi có căn cứ. Không có adapter tiếng Việt/VieNeu trong các prompt đã đọc.

### A10. UnderleveledBuilder/awesome-story-skills — nguồn tìm và phương pháp thử, không phải skill viết lời thắng

[storytelling-methods](https://github.com/UnderleveledBuilder/awesome-story-skills/blob/5754686c5539e4418a30183775665bde4158bede/skills/storytelling-methods/SKILL.md), [quy ước eval](https://github.com/UnderleveledBuilder/awesome-story-skills/blob/5754686c5539e4418a30183775665bde4158bede/evals/README.md). Trích ngắn ở skill: “not the quality of its output”.

Skill lọc chỉ mục theo thể loại/phương pháp/ngôn ngữ rồi chọn ít dự án phù hợp. Eval quy định cùng input, môi trường/model, phiên bản skill cố định, giữ đủ đầu ra và nhật ký hỏi–đáp; nhận xét bằng ví dụ.

**Áp dụng ta:** lấy cách cố định đầu vào và ghi mọi lượt thử cho pilot 075b. Không dùng số sao, nhãn featured hay “đã kiểm thông tin” làm bằng chứng lời hay. Không đưa hàng trăm công cụ hoặc truyện hư cấu vào lõi. Áp cho việc so Long và Short Việt nếu mỗi cohort dùng đúng giọng/khuôn của nó; eval gốc không chứng minh VieNeu hay retention YouTube.

Không bổ sung repo khuyến nghị thứ 11–13. Archive của A3 là nguồn đích bắt buộc để xác minh chính mục được giao, không phải đề xuất cài thêm.

## B. Kiểm kê luật trong repo

### B0. Chứng cứ nội bộ và cách đọc bảng

| Mã | Có số liệu gì trong nguồn đã đọc? | Giới hạn |
|---|---|---|
| E1 | `.claude/skills/long-script/references/evidence.md:3`: 6 video B3/B5/F1/F3/F4/F6, retention 1% khớp segments. B5 109 view, F6 307; video ngắn 141–410 view. Câu >35 tiếng có mức rơi vượt nền +23,4 điểm %/phút, bỏ F6 còn +19,0; câu ≤6 tiếng thấp hơn nền −8,4/−4,2. | Quan sát mẫu nhỏ; độ sâu, tua tới, loại video và chọn câu gây nhiễu. Không chứng minh quota 1/6, câu 10 tiếng hay mô-típ 3 lần là tối ưu. |
| E2 | `.claude/skills/long-script/SKILL.md:14` nói đo 30 bản trụ, 179–189 tiếng/phút, chuẩn 185. `.claude/skills/long-video/SKILL.md:22` đổi Long mới sang Thục Đoan tempo 0.961, khoảng 175 tiếng/phút từ PO 16/11. | Nguồn mới là cấu hình/ước tốc độ, chưa thấy cohort đo cùng cách đếm để thay ngân sách tự động. |
| E3 | `output/cl_staging/grok/reports/67_audio_script_rules.md:10`: 437 JSON TTS (FS151/BUD286), median token/phút 201,4/218,9. Dòng 14: analytics Short FS n27/BUD n49 nhưng chưa ghép script chắc chắn. | Token thô, khác giọng/nghỉ. Dòng 16 ghi rõ đề xuất chưa A/B; không dùng như chứng minh nhịp thắng. |
| E4 | `output/cl_staging/grok/reports/83_doc_script_audit.md:43`: pause đo trùng giá trị đặt; tempo 0.8 cho 3.189s so 2.52s ở 1.0. Dòng 46: bold cùng 3.92s/chuỗi sạch. | Báo cáo nói chưa nghe tai; ba bản viết lại lint sạch không chứng minh retention. Số này được trích lại, không render lại trong 075a. |
| E5 | `output/cl_staging/grok/reports/071_long_temiya_feedback.md:7`: 71/383 câu ≤6 tiếng (18,5%), 11 chuỗi, 6 dòng phẩy; dòng 9: 346/382 khe nghỉ =0.5s, 383 segments. | Có nhiều biến cùng lúc. A Xà Thế cũng có câu ngắn nhưng xen dài, không dòng phẩy; không đủ suy “càng ít câu ngắn càng hay”. |
| E6 | `.claude/skills/shorts-lookup/SKILL.md:23`: Tam Tai 51.340 views/132,2% AVP; 3 tuổi hợp 36.007 views/206,1% AVP; ví dụ 10s, bảng thắng. | Cohort 19–21/10; AVP gồm rewatch, khác stay; số ngách BUD không đương nhiên là kết quả kênh mình. Không có thử kiểm soát từng thành phần. |
| E7 | `.claude/skills/shorts-studio/references/spec.md:51`: stay–views r≈0,52 BUD/0,51 FS, nhóm ≥100 view; hook cụ thể 51–63%, ví dụ trừu tượng 9–14%. | Tương quan và ví dụ chọn; không suy mọi câu hỏi khái niệm sẽ thua. Không chứng minh luma50/0,8s là ngưỡng retention. |
| E8 | `.claude/skills/long-packaging/SKILL.md:17`: FS CTR cùng Search, n16 r0,87; quy tắc từng thumbnail mẫu n5–12; BUD không cùng cơ chế. | CTR khác giữ chân lời; traffic/tuổi video gây nhiễu. Không dùng luật title FS để áp giọng BUD. |

### B1. Sổ luật (một dòng một luật)

Cột “Lint” mô tả **code hiện tại**, không coi câu “lint sẽ báo” trong skill là bằng chứng code đã kiểm đủ. CB = CẢNH BÁO. “CHỈ-TRÊN-GIẤY” nghĩa chưa có lint trong các đường đã truy để kiểm đúng luật, vẫn có thể được người soát thực hiện. Dẫn `file:dòng` dưới đây tính từ root repo/worktree; đường staging của ba báo cáo là repo chính.

| ID | Luật đang được viết | Nguồn file:dòng | Kênh/khuôn áp dụng | Có số liệu? | Lint hiện tại / giới hạn | Đánh dấu |
|---|---|---|---|---|---|---|
| L01 | Cold open cảnh căng, hiện tại, dừng ở đỉnh, ≤60s; không chào. | `.claude/skills/long-script/SKILL.md:20`; `.claude/skills/long-script/references/writer-brief.md:42` | Long BUD/FS | QS E1 + PO | cold_open_dai/chao (CB); không kiểm được thì/đỉnh | TRÙNG |
| L02 | Cú sốc/nghịch lý hoặc móc xuất hiện trong 40s đầu. | `.claude/skills/long-script/SKILL.md:20`; `.claude/skills/long-script/SKILL.md:56` | Long BUD/FS | PO 15/11; chưa A/B | soc_40s (CB), dựa regex | TRÙNG |
| L03 | Lộ trình xong ≤75s; chọn một trong sáu dạng, đổi tập liền trước. | `.claude/skills/long-script/SKILL.md:21`; `.claude/skills/long-script/references/formats.md:27` | Long chuẩn BUD/FS | QS E1; ngưỡng PO | meta_som không chứng minh mốc 75s/đổi dạng | CHỈ-TRÊN-GIẤY (phần mốc/đổi dạng) |
| L04 | Không nói về video trước 25s. | `.claude/skills/long-script/SKILL.md:21`; `.claude/skills/long-script/references/writer-brief.md:42` | Long chuẩn BUD/FS | QS E1 | meta_som (CB) | TRÙNG; LỆCH-KÊNH (V2 dùng 30s) |
| L05 | Định nghĩa ≤2 câu, trong lời đáp; không chương lý thuyết trước lần trả đầu. | `.claude/skills/long-script/SKILL.md:22`; `.claude/skills/long-script/references/line-rules.md:78` | Long chuẩn BUD/FS | QS E1 (F1/F3/F6) | ly_thuyet_som/chuong_dinh_nghia_som (CB, heuristic) | TRÙNG |
| L06 | Trả phần thật ≤90s; chương nội dung đầu bắt đầu ≤150s. | `.claude/skills/long-script/SKILL.md:23`; `.claude/skills/long-script/references/writer-brief.md:43` | Long chuẩn BUD/FS | QS E1 | chua_tra_som/noi_dung_muon (CB, suy từ từ khóa) | TRÙNG |
| L07 | Mỗi câu ≤35 tiếng đọc sau mở rộng số. | `.claude/skills/long-script/SKILL.md:24`; `.claude/skills/long-script/references/line-rules.md:10`; `.claude/skills/long-script/references/writer-brief.md:60` | Long BUD/FS | QS E1 + KT | cau_dai (LỖI); runner chỉ token | TRÙNG; MÂU THUẪN phép đếm |
| L08 | Lời liệt kê tối đa 3 mục. | `.claude/skills/long-script/SKILL.md:24`; `.claude/skills/long-script/references/line-rules.md:40`; `.claude/skills/long-script/references/writer-brief.md:61` | Long BUD/FS | QS E1 + KT đọc lồng | liet_ke (CB); nhieu_chi (LỖI) | TRÙNG |
| L09 | Trả vòng xong thì câu kế mở vòng mới. | `.claude/skills/long-script/SKILL.md:25`; `.claude/skills/long-script/references/line-rules.md:96`; `.claude/skills/long-script/references/writer-brief.md:46` | Long kể BUD/FS | QS E1 (F6) | chưa có kiểm quan hệ liền câu | TRÙNG; CHỈ-TRÊN-GIẤY |
| L10 | Kết chương tránh tóm tắt, dùng cầu nối. | `.claude/skills/long-script/SKILL.md:26`; `.claude/skills/long-script/references/line-rules.md:94`; `.claude/skills/long-script/references/formats.md:72` | Long kể BUD/FS | QS E1 | ket_chuong_tom_tat (CB); không đo ý nghĩa cầu nối | TRÙNG |
| L11 | Không đọc bảng từng dòng; chỉ ví dụ và cách tra. | `.claude/skills/long-script/SKILL.md:26`; `.claude/skills/long-script/references/line-rules.md:36`; `.claude/skills/long-script/references/formats.md:120` | Long tra cứu FS | QS E1 + KT | liet_ke chỉ bắt một phần; chưa đối chiếu lời/bảng | TRÙNG; CHỈ-TRÊN-GIẤY (ngữ nghĩa) |
| L12 | CTA ≤2 câu, sau trả cuối, trước câu hỏi bình luận. | `.claude/skills/long-script/SKILL.md:26`; `.claude/skills/long-script/references/line-rules.md:105`; `.claude/skills/long-script/references/writer-brief.md:39` | Long chuẩn BUD/FS | QS E1; không riêng ngưỡng 2 | cta_nhieu thực tế >3; cta_giua GỢI Ý | TRÙNG; MÂU THUẪN |
| L13 | Câu ≤6 tiếng khoảng mỗi 4–6 câu, đặt sau khoảnh khắc. | `.claude/skills/long-script/SKILL.md:27`; `.claude/skills/long-script/references/line-rules.md:16`; `.claude/skills/long-script/references/writer-brief.md:62` | Long chuẩn BUD/FS | QS E1; E5 không bác bỏ tương quan | it_cau_ngan chỉ tổng <1/8 (CB) | TRÙNG; MÂU THUẪN cục bộ/nhịp |
| L14 | Không ba câu ngắn liền, trừ cao trào. | `.claude/skills/long-script/references/line-rules.md:17` | Long chuẩn BUD/FS | GT biên tập, không mẫu riêng | chưa kiểm chuỗi/cao trào trong lint Long gốc | CHỈ-TRÊN-GIẤY |
| L15 | Tiêu đề chương là điều người xem tìm; chương nghe độc lập. | `.claude/skills/long-script/SKILL.md:28`; `.claude/skills/long-script/references/formats.md:72` | Long tra cứu/narrative BUD/FS | QS E1 thẻ F6 tăng do tua | không kiểm tự đứng được | LỆCH-KÊNH; CHỈ-TRÊN-GIẤY |
| L16 | Tên ngoại/Pali, mã kinh, khoảng số có cách đọc Việt. | `.claude/skills/long-script/SKILL.md:29`; `.claude/skills/long-script/references/line-rules.md:44`; `.claude/skills/long-script/references/writer-brief.md:63` | Long BUD/FS | ĐO phonemize 14/10 + E4 | tts_dau_la/gach_noi/viet_tat (CB); lexicon sửa trước đọc | TRÙNG |
| L17 | Câu rào/nhắc nguồn bằng lời khoảng ≤8% số câu. | `.claude/skills/long-script/SKILL.md:32`; `creator_v2/docs/pm/storytelling-guide.md:192` | Long BUD/FS và V2 | PO; so mức Golden/Shanghai, chưa nghiên cứu ngưỡng | Long BUD/FS chưa đo tỷ lệ; V2 chỉ cửa sổ | TRÙNG; CHỈ-TRÊN-GIẤY (tỷ lệ) |
| L18 | Nội tâm người có tên dùng khung nhẹ/câu hỏi; không khí có thể kể thẳng. | `.claude/skills/long-script/SKILL.md:33`; `creator_v2/docs/pm/storytelling-guide.md:191` | Long theo PO 16/11 | PO; không retention tách biến | review ngữ nghĩa | MÂU THUẪN với truyện kinh; LỆCH-KÊNH |
| L19 | Chú giải/truyền thuyết dẫn một câu khung rồi kể liền. | `.claude/skills/long-script/SKILL.md:34`; `.claude/skills/long-script/references/story.md:9` | BUD kể truyện | PO/nguồn, chưa A/B | Short mới đếm rào; Long chưa kiểm khung đúng lớp | TRÙNG |
| L20 | Cảnh phỏng dựng ghi dòng trong pd sidecar và gắn nhãn ảnh. | `.claude/skills/long-script/SKILL.md:35` | Long BUD/FS | PO | không phải long_script_lint; cần adapter media_map | LỆCH-KÊNH (V2 dùng {pd}) |
| L21 | Một dòng là một câu trọn; không kết thúc giữa câu bằng dấu phẩy. | `.claude/skills/long-script/SKILL.md:36`; `.claude/skills/long-script/references/line-rules.md:8`; `creator_v2/docs/pm/storytelling-guide.md:194` | Lời VieNeu, mọi kênh theo luật áp | KT + E4/E5 + PO | cau_tach_doi Long CB; Short mới LỖI | TRÙNG; MÂU THUẪN mức chặn |
| L22 | Câu đỉnh kết hai nhịp: ngắn lặng rồi dài ngân. | `.claude/skills/long-script/SKILL.md:37`; `creator_v2/docs/pm/storytelling-guide.md:194` | Long kể | PO; chưa A/B | chưa kiểm tự động | TRÙNG; CHỈ-TRÊN-GIẤY |
| L23 | Không bịa trích thật, số, phán quyết; người sống không dựng lời. | `.claude/skills/long-script/SKILL.md:38`; `creator_v2/docs/pm/storytelling-guide.md:193`; `.claude/skills/long-script/references/writer-brief.md:79` | Mọi kênh theo miền | PO/nguồn | chỉ kiểm có metadata không chứng minh sự thật | TRÙNG |
| L24 | 10s đầu hình động/mạnh, không chữ khóa hay thẻ chữ nền trống. | `.claude/skills/long-script/SKILL.md:41` | Long BUD/FS | PO 15/11 | mo_hinh_tinh/mo_chu_khoa/mo_the_chu/mo_cau_soc (CB) | LỆCH-KÊNH (V2 cho slam/quote) |
| L25 | Long tra cứu có bảng tóm tắt ≤45s, không hẹn bảng cuối. | `.claude/skills/long-script/SKILL.md:48`; `.claude/skills/long-script/references/formats.md:112` | Long format tra_cuu | PO + ví dụ bảng chậm 1242s | tra_cuu_bang_muon/hua_bang_cuoi (LỖI) | MÂU THUẪN với FM:112 |
| L26 | Long tuyển tập vào truyện 1 trước 60s, không lý thuyết trước truyện. | `.claude/skills/long-script/SKILL.md:49` | Long format tuyen_tap | PO + ví dụ 175,7s | tuyen_tap_truyen1_muon/ly_thuyet_truoc_truyen1 (LỖI) | riêng khuôn |
| L27 | Bản trụ khoảng 30 phút, 12–14 chương khoảng 2 phút. | `.claude/skills/long-script/SKILL.md:53`; `.claude/skills/long-script/references/formats.md:17` | Long chuẩn BUD/FS | PO 21/10 + E1; không tối ưu nhân quả | so_chuong/chuong_dai (CB) | TRÙNG; khác nhân vật/đêm |
| L28 | Chạm người nghe ≤30s: FS năm sinh/chi, BUD nỗi khổ đời thường. | `.claude/skills/long-script/SKILL.md:59`; `.claude/skills/long-script/references/writer-brief.md:43` | Long chuẩn BUD/FS | PO/QS E1 | chưa kiểm đúng người/đúng hạn | TRÙNG; CHỈ-TRÊN-GIẤY |
| L29 | Cung A→B ghi một câu trong plan. | `.claude/skills/long-script/SKILL.md:65`; `.claude/skills/long-script/references/formats.md:20` | Long kể | PO/GT | chưa kiểm | TRÙNG; CHỈ-TRÊN-GIẤY |
| L30 | Mô-típ có nghĩa lặp ≥3 lần ở mở/giữa/kết. | `.claude/skills/long-script/SKILL.md:65`; `.claude/skills/long-script/references/formats.md:57` | Long kể | GT/PO; không mẫu tách biến | chưa whitelist motif với bộ bắt lặp | TRÙNG; CHỈ-TRÊN-GIẤY |
| L31 | Phần thưởng khoảng 50%, cảnh mạnh khoảng 75%. | `.claude/skills/long-script/SKILL.md:66`; `.claude/skills/long-script/references/writer-brief.md:45` | Long chuẩn kể | PO; QS không xác lập đúng tọa độ | thieu_rehook ±5% khác kiểm payoff/cảnh mạnh | TRÙNG; LỆCH-KHUÔN tra cứu |
| L32 | Kết callback, đóng vòng rồi câu hỏi thật. | `.claude/skills/long-script/SKILL.md:68`; `.claude/skills/long-script/references/line-rules.md:105`; `.claude/skills/long-script/references/formats.md:74` | Long chuẩn BUD/FS | PO/QS E1 | regex trả vòng; không kiểm câu hỏi thật/callback nghĩa | TRÙNG; CHỈ-TRÊN-GIẤY (nghĩa) |
| L33 | Khuôn nhân vật là một người, một hành trình, ≥30 phút. | `.claude/skills/long-script/SKILL.md:72`; `.claude/skills/long-script/references/formats.md:157` | Long nhan_vat | PO; số CL ở FM:156 là chuyển giao, không thử BUD | THOI_LUONG/NHAN_VAT (CB) | LỆCH-KÊNH nếu áp cứng |
| L34 | Nhân vật có 2–3 câu hỏi hẹn đúng chương trong 90s. | `.claude/skills/long-script/SKILL.md:79`; `.claude/skills/long-script/references/formats.md:168` | Long nhan_vat | PO | CAU_HOI_HEN_CHUONG (CB), không giới hạn trên 3 | TRÙNG; ngoại lệ ba câu hỏi |
| L35 | Khuôn nhân vật 12–16 chương, mỗi chương bước ngoặt. | `.claude/skills/long-script/SKILL.md:80`; `.claude/skills/long-script/references/formats.md:169` | Long nhan_vat | PO | SO_CHUONG (CB); không kiểm bước ngoặt | TRÙNG |
| L36 | Tên protagonist ở cold open và ≥70% chương. | `.claude/skills/long-script/references/formats.md:181` | Long nhan_vat | PO; chưa bằng chứng riêng 70% | NHAN_VAT (CB), dò cụm tên | riêng khuôn, không dùng lõi |
| L37 | Brief có ai/ngôn điệp, ngân sách, neo tìm kiếm, mô-típ trước viết. | `.claude/skills/long-script/SKILL.md:89`; `.claude/skills/long-script/references/writer-brief.md:11` | Long BUD/FS | quy trình, không thử retention | review thủ công | TRÙNG |
| L38 | Gói dữ kiện phân kinh/chú giải/dân gian/sử/code trước lời. | `.claude/skills/long-script/SKILL.md:92`; `.claude/skills/long-script/references/story.md:6` | Long BUD/FS | đảm bảo nguồn | chưa lint đối chiếu văn bản | TRÙNG; CHỈ-TRÊN-GIẤY ở lint |
| L39 | Plan duyệt trước lời, rồi beat sheet có vai/kỹ thuật/cảm xúc/vòng/chi tiết. | `.claude/skills/long-script/SKILL.md:97`; `.claude/skills/long-script/SKILL.md:102`; `.claude/skills/long-script/references/formats.md:141` | Long BUD/FS | PO/quy trình | chưa kiểm tính đầy đủ/ý nghĩa beat | TRÙNG |
| L40 | Tự soát 0 LỖI; mọi CB sửa hoặc giải trình; soát sự thật sau lint. | `.claude/skills/long-script/SKILL.md:108`; `.claude/skills/long-script/SKILL.md:123`; `.claude/skills/long-script/references/writer-brief.md:92` | Long BUD/FS | quy trình | --strict chỉ đổi exit cho LỖI | TRÙNG; lint không thay nguồn |
| L41 | Một say có thể gộp 2–3 câu thành khối, tổng khoảng ≤45 tiếng. | `.claude/skills/long-script/references/line-rules.md:8` | Long BUD/FS cũ | GT kỹ thuật/biên tập | long_l có đo nhưng không tạo lỗi tổng dòng | MÂU THUẪN LS:36; CHỈ-TRÊN-GIẤY |
| L42 | Trung vị câu 12–16 tiếng, đổi dài–vừa–ngắn. | `.claude/skills/long-script/references/line-rules.md:10`; `.claude/skills/long-script/references/line-rules.md, luật19` | Long BUD/FS | GT; E1 chỉ so ≤6/>35, không chứng minh median | lint thống kê, không ép median | MÂU THUẪN WB:51 |
| L43 | Một câu tối đa hai năm số trong bảng cách đọc. | `.claude/skills/long-script/references/line-rules.md:26` | Long BUD/FS | KT; chưa mẫu riêng hai so ba | không có lint riêng 2 năm | MÂU THUẪN LS:24 tối đa 3 |
| L44 | Số kể viết chữ; lời có thể làm tròn, hình giữ chính xác. | `.claude/skills/long-script/references/line-rules.md:34`; `creator_v2/docs/pm/storytelling-guide.md:71`; `creator_v2/AGENTS.md:49` | Mọi kênh, không làm tròn dữ kiện định danh | KT/biên tập + E4 | tts_* gợi ý; chưa kiểm sai số làm tròn | TRÙNG |
| L45 | Tối đa 3 tên chi/dòng; FS gọi tên chi, không tên con vật. | `.claude/skills/long-script/references/line-rules.md:40`; `.claude/skills/long-script/references/line-rules.md:42`; `.claude/skills/shorts-lookup/SKILL.md:141` | FS; chặn nhiều chi còn áp ở runner khác | KT đọc lồng, có 3 lần thử thất bại | crowded_chi_lines/zodiac_naming_errors (LỖI) | TRÙNG |
| L46 | Chữ khóa 1 cụm có nghĩa, 1–4 tiếng, nếu không có ảnh/visual. | `.claude/skills/long-script/references/line-rules.md:51` | Long BUD/FS | KT engine, lỗi fallback E5 | bare_lines chỉ có/không; chưa kiểm đúng 1 cụm/đủ nghĩa | TRÙNG; CHỈ-TRÊN-GIẤY (nghĩa) |
| L47 | chap là tiêu đề 2–7 tiếng được đọc; không Phần 1/định nghĩa sớm. | `.claude/skills/long-script/references/line-rules.md:54` | Long BUD/FS | QS E1 + hợp đồng DSL | heading nhận diện; không kiểm giới hạn 2–7 | MÂU THUẪN R83:56 nếu coi là luật mới |
| L48 | Nghỉ đỉnh 1,0–1,4s; hỏi lớn 0,8–1,2s; chương 1,7–2,0s. | `.claude/skills/long-script/references/line-rules.md:60` | Long preset C cũ | thiết kế; E4 đo pause có hiệu lực, không đo tốt nhất | tts_khoa_dong/van_tay kiểm vị trí, không kiểm gu nhịp | LỆCH phiên bản giọng |
| L49 | Tempo BUD đỉnh 0,85–0,88; FS 0,96; alt kinh ≤2 câu liền. | `.claude/skills/long-script/references/line-rules.md:62`; `.claude/skills/long-script/references/line-rules.md:64` | Long preset C cũ | thiết kế; E4 đo tempo có hiệu lực | không kiểm chuỗi alt/tempo đỉnh | MÂU THUẪN LV:22 giọng mới |
| L50 | Một lượt thoại/dòng; dẫn vai trước; thoại ≤20 tiếng, không lồng ngoặc. | `.claude/skills/long-script/references/line-rules.md:67` | Long kể một giọng | KT rõ vai, chưa thử ngưỡng | hai_luot_thoai (GỢI Ý), không kiểm trần 20 | CHỈ-TRÊN-GIẤY (phần lớn) |
| L51 | Mỗi cảnh có chi tiết giác quan phù hợp nguồn. | `.claude/skills/long-script/references/line-rules.md:73`; `.claude/skills/long-script/references/writer-brief.md:31` | Long kể BUD/FS | GT cách kể | kind_of heuristic, không kiểm nguồn của chi tiết | TRÙNG; ranh giới BUD cần quyết |
| L52 | Không quá 4 câu trừu tượng liền; ví dụ ≤2 câu sau khái niệm. | `.claude/skills/long-script/references/line-rules.md:76` | Long giải thích | QS E1 + GT ngưỡng | truu_tuong_lien ≥5 (CB); chưa nối khái niệm–ví dụ | CHỈ-TRÊN-GIẤY (nửa sau) |
| L53 | Gọi khán giả bạn; BUD có thể chúng ta khi cùng thực tập. | `.claude/skills/long-script/references/line-rules.md:81`; `.claude/skills/long-script/references/writer-brief.md:21` | BUD/FS | gu kênh | quy_vi (CB) chỉ bắt quý vị | TRÙNG |
| L54 | FS diễn đạt truyền thống/tham khảo, không doạ hay hứa chắc tiền. | `.claude/skills/long-script/references/line-rules.md:83`; `.claude/skills/shorts-lookup/SKILL.md:143` | FS | PO/ranh giới kênh | short_tone chỉ regex; không chứng minh framing đúng | TRÙNG; luật PO 03/11 mới hơn cấm rộng |
| L55 | Bảng vong phải có cụm đóng xuất hiện sau chương mở. | `.claude/skills/long-script/references/line-rules.md:95`; `.claude/skills/long-script/references/formats.md:55` | Long có metadata vong | quy trình | vong_khong_dong (CB); thiếu cả bảng thì bỏ qua | TRÙNG; chưa kiểm đóng đúng nghĩa |
| L56 | Cùng hai tiếng mở đầu không vượt khoảng 2% câu; điệp có chủ ý ≤3. | `.claude/skills/long-script/references/line-rules.md:99` | Long BUD/FS | QS ví dụ F6; chưa thử đúng 2% | mo_cau_lap (GỢI Ý), có ngưỡng sàn 4 lần | CHỈ-TRÊN-GIẤY (ngưỡng không tuyệt đối) |
| L57 | Cụm hai tiếng thường ≥3 lần/5 dòng cần đổi, trừ motif. | `.claude/skills/long-script/references/line-rules.md:102` | Long BUD/FS | GT biên tập | tu_lap (GỢI Ý); chưa có whitelist motif tường minh | MÂU THUẪN thực thi motif |
| L58 | Show trước giảng; nhân vật có mong muốn, mâu thuẫn, biến đổi. | `.claude/skills/long-script/references/writer-brief.md:25`; `.claude/skills/long-script/references/writer-brief.md:27` | Long kể BUD/FS | GT + PO | không lint ngữ nghĩa | TRÙNG; không ép FS bảng |
| L59 | BUD đề rộng neo một truyện kinh/chú giải; người hiện đại soi chiếu. | `.claude/skills/long-script/references/writer-brief.md:29` | Long BUD kể | PO | review nguồn/khuôn | LỆCH-KHUÔN nếu ép mọi BUD |
| L60 | Cảm xúc chuyển biến; chi tiết thay dày tính từ. | `.claude/skills/long-script/references/writer-brief.md:30`; `.claude/skills/long-script/references/writer-brief.md:32` | Long kể | GT; chưa A/B | tinh_tu_cam_xuc (CB) theo từ điển | TRÙNG |
| L61 | Không cliffhanger giả, bí mật tâm linh, kéo lời cho đủ giờ. | `.claude/skills/long-script/references/writer-brief.md:37` | Long kể BUD/FS | PO/GT | chưa kiểm vòng hứa–trả theo nghĩa | CHỈ-TRÊN-GIẤY |
| L62 | 120s đầu mỗi câu khoảng ≤10 tiếng, mỗi câu gợi một hình. | `.claude/skills/long-script/references/writer-brief.md:48`; `.claude/skills/long-script/references/writer-brief.md:51`; `.claude/skills/long-script/references/writer-brief.md:55` | Long BUD/FS | lý do cổng hình + PO; chưa đo tác dụng câu 10 | pace_gate kiểm 8s động/4s tĩnh, không kiểm 10 tiếng | MÂU THUẪN nhịp/câu trọn |
| L63 | Bàn giao nháp lời sạch và source_notes phân lớp, nguồn, điểm chưa chắc. | `.claude/skills/long-script/references/writer-brief.md:86` | Long BUD/FS | quy trình | chưa kiểm trường/nguồn đầy đủ | TRÙNG |
| L64 | Tự hỏi 10 mục; thử cắt 10% nếu không mất ý. | `.claude/skills/long-script/references/writer-brief.md:94`; `.claude/skills/long-script/references/writer-brief.md:103` | Long BUD/FS | GT rubric; chưa thử ngưỡng cắt | review, không lint | CHỈ-TRÊN-GIẤY |
| L65 | Phần văn xuôi Tiền Thân là chú giải; chỉ kệ là kinh. | `.claude/skills/long-script/references/story.md:14`; `.claude/skills/long-script/references/formats.md:97` | BUD Tiền Thân | phân lớp nguồn, không analytics | hf_sutta kiểm kệ; lint không chứng minh phân lớp | TRÙNG |
| L66 | Truyện theo Cowell PD, bản Việt chỉ đối chiếu, không chép. | `.claude/skills/long-script/references/story.md:9`; `.claude/skills/shorts-lookup/SKILL.md:147` | BUD Jātaka | quy định nguồn | review nguồn | TRÙNG |
| L67 | Giác quan trung tính được thêm; nội tâm thiếu nguồn cần nhãn ≤1/truyện. | `.claude/skills/long-script/references/story.md:18`; `.claude/skills/long-script/references/story.md:21` | BUD truyện theo reference cũ | PO/biên tập cũ | không lint | MÂU THUẪN rules.md, luật19 và LS:33 |
| L68 | Truyện đủ hiện tại/quá khứ/kệ/nhận diện; không lộ nhận diện trước. | `.claude/skills/long-script/references/story.md:25`; `.claude/skills/long-script/references/story.md:31`; `.claude/skills/long-script/references/formats.md:91` | BUD Tiền Thân | khuôn nguồn | không lint trình tự/nguồn | riêng khuôn |
| L69 | Mỗi beat truyện đối chiếu tóm tắt nguồn; soi nói/dạy/nghĩ/số. | `.claude/skills/long-script/references/story.md:35` | BUD truyện | lỗi nội dung đã gặp, ST:38 | review đối chiếu; không regex chứng minh sự thật | CHỈ-TRÊN-GIẤY ở lint |
| L70 | FS hỏi–đáp trả trong hai câu đầu chương. | `.claude/skills/long-script/references/formats.md:126` | Long FS Q&A | học đối thủ, không thử riêng | chua_tra_som không kiểm từng chương | riêng khuôn; CHỈ-TRÊN-GIẤY |
| L71 | Đêm nghe mở êm, không cliffhanger, 10–12 chương 7–9 phút. | `.claude/skills/long-script/references/formats.md:132`; `.claude/skills/long-script/references/formats.md:134` | BUD night 90 phút | đối thủ; ghi rõ chưa retention kênh | --kind night nới luật, không kiểm đủ gu/khuôn | LỆCH-KHUÔN |
| L72 | Đêm nghe CTA nhẹ phút 2, cuối chậm/lặp. | `.claude/skills/long-script/references/formats.md:136` | BUD night | GT/đối thủ | không lint vị trí CTA đêm riêng | ngoại lệ L12 |
| L73 | Số liệu kênh là cơ sở nguồn luật; dẫn nguồn/đổi cách áp phải ghi. | `.claude/skills/long-script/references/sources.md:3`; `.claude/skills/long-script/references/sources.md:19`; `.claude/skills/long-script/references/evidence.md:97` | Long BUD/FS | quy trình cập nhật | chưa phiên bản hóa thứ tự luật | MÂU THUẪN nếu hiểu số liệu cũ đè PO mới |
| S01 | Short bảng hook tìm kiếm → bảng tự dò → giữ ≥3s, CTA lưu/pause. | `.claude/skills/shorts-studio/SKILL.md:56`; `.claude/skills/shorts-lookup/SKILL.md:35` | FS lookup/BUD lịch, 10–15s | QS E6; không A/B cơ chế | duration/hold QA khác lint lời | TRÙNG; MÂU THUẪN v2 |
| S02 | Short lời kinh 9–12s dùng câu đã kiểm và nguồn. | `.claude/skills/shorts-studio/SKILL.md:57`; `.claude/skills/shorts-lookup/SKILL.md:36` | BUD kinh ngắn | QS E6 + PO | source required không chứng minh nguyên văn | TRÙNG; MÂU THUẪN v2 |
| S03 | Truyện nhân quả 75–120s: cao trào → lùi kể → lật → chiêm nghiệm. | `.claude/skills/shorts-studio/SKILL.md:58`; `.claude/skills/shorts-lookup/SKILL.md:37` | BUD story | QS ngách E6, không hiệu quả riêng kênh | short_story không kiểm cú lật | riêng khuôn; ngoài 20–60s |
| S04 | Biểu tượng trả 1–2 dòng, nhãn theo cách giải thích phổ biến. | `.claude/skills/shorts-studio/SKILL.md:59`; `.claude/skills/shorts-lookup/SKILL.md:38`; `.claude/skills/shorts-lookup/SKILL.md:148` | BUD biểu tượng | PO + QS ví dụ | review ý/nguồn | TRÙNG |
| S05 | FS chỉ tay hook tự soi, giải nghĩa tham khảo; không đoán thọ/bệnh. | `.claude/skills/shorts-lookup/SKILL.md:39` | FS palm 8–12s | PO | chưa lint lời riêng | riêng khuôn |
| S06 | Không làm lại hỏi–giảng lý thuyết khô, tóm tắt truyện không cao trào. | `.claude/skills/shorts-studio/SKILL.md:64`; `.claude/skills/shorts-lookup/SKILL.md:47` | BUD/FS Short | QS E6/E7, phạm vi cohort cũ | hook_terms bắt một số từ, không kiểm lời khô | TRÙNG; không suy mọi explainer thua |
| S07 | Giây đầu có vật/người/hành động/năm; title có neo cụ thể. | `.claude/skills/shorts-studio/SKILL.md:71`; `.claude/skills/shorts-studio/references/spec.md:53` | Short BUD/FS | QS E7 | hook_lint + hook_errors; scope/cấp độ khác nhau | TRÙNG |
| S08 | Hook khái niệm trừu tượng dạng có phải là bị tránh/chặn. | `.claude/skills/shorts-studio/SKILL.md:71`; `.claude/skills/shorts-studio/references/spec.md:55` | Short BUD/FS | QS E7 | TRUU_TUONG thực tế bắt câu hỏi rộng hơn mẫu có phải là | MÂU THUẪN tài liệu/phạm vi regex |
| S09 | Dạng 30s viết 6–8 câu; 9–15s chỉ 1–3 câu. | `.claude/skills/shorts-studio/SKILL.md:103` | Short BUD/FS | khuôn biên tập, chưa A/B số câu | không cổng tổng câu theo khuôn | MÂU THUẪN v2 nếu ép đồng loạt |
| S10 | Câu 1 ≤10 chữ và trả ngay; câu 2 cụ thể. | `.claude/skills/shorts-studio/references/pipeline.md:6`; `.claude/skills/shorts-studio/references/pipeline.md:17` | Short studio 25–40s | GT + QS pipeline | v2 cho câu đầu ≤22 token; chưa luật trả ngay theo nghĩa | MÂU THUẪN với trì hoãn trả |
| S11 | Một nhịp tĩnh trước payoff; cuối hỏi/callback. | `.claude/skills/shorts-studio/references/pipeline.md:7`; `.claude/skills/shorts-studio/references/pipeline.md:22`; `.claude/skills/shorts-studio/references/motion-grammar.md:34` | Short studio kể | GT khuôn | variety kiểm thiết kế, không nghĩa nhịp tĩnh | TRÙNG; LỆCH-KHUÔN bảng |
| S12 | Hook gate 3s: luma ≥50, không chữ trần, chữ lên ≤0,8s. | `.claude/skills/shorts-studio/SKILL.md:115`; `.claude/skills/shorts-studio/references/spec.md:78` | Short studio BUD/FS/VSD | PO/kỹ thuật; chưa A/B ba ngưỡng | studio.hook_errors CB; --strict-hook mới chặn render | TRÙNG; khác guards.validate |
| S13 | Mỗi dòng câu trọn ở mọi Short; áp chặn từ lịch 29/11. | `.claude/skills/shorts-studio/SKILL.md:149`; `.claude/skills/shorts-lookup/SKILL.md:178` | Short mới; không chỉ BUD/FS ở hàm | PO + KT | short_story_issues theo day; thiếu ngày bỏ qua | TRÙNG; lệch field ngày |
| S14 | Short truyện/test_cell ≤1 câu rào nguồn. | `.claude/skills/shorts-studio/SKILL.md:150`; `.claude/skills/shorts-lookup/SKILL.md:179` | lane truyện/test_cell từ 29/11 | PO; chưa A/B số 1 | short_story_issues (LỖI) bằng SOURCE_HEDGE | TRÙNG; không áp dạng thắng |
| S15 | pd_scenes có chip PHỎNG DỰNG; nguồn ở chân hình/mô tả. | `.claude/skills/shorts-studio/SKILL.md:150`; `.claude/skills/shorts-lookup/SKILL.md:179` | Short truyện mới | PO | guards chỉ tìm chuỗi PHỎNG DỰNG ở HTML, chưa kiểm từng cảnh | TRÙNG; khác V2 |
| S16 | Short MIM/CK/CL khai hook_kind, câu 1 ≤9 từ; câu hỏi hậu quả trước 3s. | `.claude/skills/shorts-studio/SKILL.md:156`; `creator_v2/docs/pm/storytelling-guide.md:177` | V2 Short mới 01/12 | PO; chưa cohort hậu triển khai | short_retention: câu hỏi 10 token là ước lượng | LỆCH-KÊNH so BUD/FS |
| S17 | V2 khung 0 hình mạnh nhất, không logo/kicker/chữ trần. | `.claude/skills/shorts-studio/SKILL.md:159` | Short MIM/CK/CL | PO | short_retention kiểm khai báo type/key, không so mạnh nhất | CHỈ-TRÊN-GIẤY (so sánh) |
| S18 | V2 Short title ≤60 ký tự, đúng lời/nguồn; câu hỏi phải có đáp. | `.claude/skills/shorts-studio/SKILL.md:160` | Short MIM/CK/CL | PO | length có kiểm; lời hứa ngữ nghĩa review | TRÙNG |
| S19 | Công thức v2 BUD 80–102, FS 68–88 token, bỏ câu hỏi lặng. | `.claude/skills/motion-library/SKILL.md:112` | BUD/FS Short từ 14/11 | QS cũ, không đồng cohort lookup thắng | short_v2_issues (LỖI), không đếm tiếng đọc mở số | MÂU THUẪN S01/S02/S09 |
| S20 | V2 câu 2 lật cụ thể, không định nghĩa; câu 5 trả và callback. | `.claude/skills/motion-library/SKILL.md:108`; `.claude/skills/motion-library/SKILL.md:110` | BUD/FS v2 | QS cũ (rơi câu 2) | short_v2_issues kiểm định nghĩa, không kiểm trả/callback | TRÙNG; riêng khuôn |
| S21 | V3 neo + hồn riêng: BUD hiền, FS thực tế tham khảo, không giật gân. | `.claude/skills/motion-library/SKILL.md:118`; `.claude/skills/motion-library/SKILL.md:127` | BUD/FS từ 18/11 | PO/QS chuyển giao CL | short_tone LỖI; short_hook_hints chỉ nhắc | LỆCH-KÊNH; cấm rộng cần cập nhật |
| S22 | Ảnh không ở câu 0, tối đa 30% câu làm tiêu điểm. | `.claude/skills/shorts-studio/references/motion-grammar.md:33` | Short studio reference cũ | GT thiết kế | không phải luật lời; trái hook mới cần ảnh | MÂU THUẪN SS:115; không nhập lõi |
| S23 | Không theo thứ tự bài nguồn; thesis chậm nhất beat 2. | `.claude/skills/shorts-studio/references/research/A_process.md:185`; `.claude/skills/shorts-studio/references/research/A_process.md:191` | Short explainer đề xuất | GT từ skill ngoài | không lint luận đề | TRÙNG trục kể; LỆCH-KHUÔN lookup |
| S24 | Ngân sách Short dùng tốc độ giọng Việt đo riêng, không 2,5 word/s Anh. | `.claude/skills/shorts-studio/references/research/A_process.md:212` | Mọi Short Việt | KT + E3 | các engine dùng nhiều rate; chưa một chuẩn chung | TRÙNG |
| S25 | Caption tách theo cụm nghĩa, không chẻ từ ghép, đối chiếu script đã viết. | `.claude/skills/shorts-studio/references/research/D_design_audio.md:572`; `.claude/skills/shorts-studio/references/research/D_design_audio.md:647` | Phụ đề Short Việt | đề xuất kỹ thuật, không phải câu say | QA alignment; không luật câu trọn TTS | phải giữ khác tầng |
| P01 | Title đặt câu hỏi có đáp án thật; script trả đủ chiều sâu. | `.claude/skills/long-packaging/SKILL.md:33`; `.claude/skills/long-packaging/SKILL.md:73` | Long BUD/FS | PO/GT; ≥3 câu là quy ước | promise_check CB khi <3 câu theo heuristic | không dùng số câu thay nghĩa |
| P02 | FS tiêu đề/thumbnail theo nhu cầu tra cứu, không chuyển luật FS sang BUD. | `.claude/skills/long-packaging/SKILL.md:17`; `.claude/skills/long-packaging/SKILL.md:27` | Long FS so BUD | QS E8 | review đóng gói, không lint lời | LỆCH-KÊNH cần giữ |
| P03 | Đủ ≥1.500 impressions cùng tuổi video và cùng nguồn traffic mới kết luận CTR. | `.claude/skills/long-packaging/SKILL.md:22` | thử Long packaging | quy tắc đo, E8 | không phải gate lời | giữ đo riêng CTR/retention |
| P04 | FS không hứa số tiền/chắc chắn giàu; BUD lời Phật đối chiếu kinh. | `.claude/skills/long-packaging/SKILL.md:44`; `.claude/skills/long-packaging/SKILL.md:45` | FS/BUD | PO/nguồn | regex chỉ hỗ trợ; review nguồn | TRÙNG |
| V01 | Trục Long là nhân vật và cái giá, lựa chọn → hậu quả. | `creator_v2/docs/pm/storytelling-guide.md:189`; `creator_v2/CLAUDE.md:20` | V2 CL/MIM/CK; FS/VSD chỉ khi PO chỉ định | PO #430, xếp hạng CK>MIM>CL, không A/B | review ý, không lint | TRÙNG; LỆCH-KÊNH |
| V02 | Tách nghiên cứu, kể, soát; người soát tập trung sai tư liệu. | `creator_v2/docs/pm/storytelling-guide.md:190`; `creator_v2/CLAUDE.md:20` | V2 Long | PO | quy trình model, không lint | không tự áp mọi kênh |
| V03 | Không khí được phóng tác; không cần rào hay nhãn từng câu không khí. | `creator_v2/docs/pm/storytelling-guide.md:198`; `creator_v2/docs/pm/storytelling-guide.md:199` | V2 Long từ nới 16/11 | PO, không thử retention | review giới hạn sự kiện | MÂU THUẪN SG:191 cũ; LỆCH BUD |
| V04 | Nội tâm có tên dùng khung phỏng đoán; người sống không dựng nội tâm/thoại. | `creator_v2/docs/pm/storytelling-guide.md:191`; `creator_v2/docs/pm/storytelling-guide.md:193`; `creator_v2/docs/pm/storytelling-guide.md:200` | V2 Long, ưu tiên người sống | PO/nguồn | review, không kiểm ngữ nghĩa | TRÙNG |
| V05 | Thoại ngắn phỏng dựng người lịch sử đã mất được phép có nhãn, không trích thật. | `creator_v2/docs/pm/storytelling-guide.md:195`; `creator_v2/CLAUDE.md:12` | V2 lịch sử | PO 16/11 | {pd} adapter; không chứng minh nội dung hợp nguồn | LỆCH-KÊNH BUD |
| V06 | Nguồn khác nhau chỉ kể đôi khi chính dị biệt hấp dẫn, ghi lý do chọn bản. | `creator_v2/docs/pm/storytelling-guide.md:192` | V2 Long | PO | review factcheck | CHỈ-TRÊN-GIẤY ở lint |
| V07 | Mỗi 30s sau phút đầu có diễn biến/chứng cứ/phép tính/hệ quả mới. | `creator_v2/docs/pm/storytelling-guide.md:156` | V2 Long mới | PO/QS review | NHIP_30S kiểm beat metadata, chỉ CB, thời gian ước | không chứng minh mới có nghĩa |
| V08 | Không chào/giới thiệu/lộ trình trước 30s; có người/cái giá sớm. | `creator_v2/docs/pm/storytelling-guide.md:152` | V2 Long mới, không legacy | PO | O6 LỖI; O1 CB theo guide; chưa chạy gate sản xuất | LỆCH-KÊNH 25s BUD/FS |
| V09 | Cold open có câu hỏi hậu quả trước 8s, chứng cứ/diễn biến trước 15s. | `creator_v2/docs/pm/storytelling-guide.md:170`; `creator_v2/docs/pm/storytelling-guide.md:171` | V2 Long survival | PO | review nghĩa; không bắt dấu ? chỉ để qua cổng | LỆCH-KÊNH |
| V10 | Cửa sổ 40s có hình mạnh và ít nhất 3 nhấn thị giác. | `creator_v2/docs/pm/storytelling-guide.md:175`; `creator_v2/docs/pm/storytelling-guide.md:178` | V2 Long survival | PO | phần hình, không biến thành câu cụt/khẩu hiệu | LỆCH-KÊNH (BUD cấm thẻ đầu 10s) |
| V11 | Câu một hơi, gọi bạn, làm tròn số; mã/giờ chính xác ưu tiên hình. | `creator_v2/AGENTS.md:39`; `creator_v2/AGENTS.md:49`; `creator_v2/docs/pm/storytelling-guide.md:71` | MIM/CK/CL | KT/biên tập | craft/script gates khác, không một đếm chung | TRÙNG |
| V12 | Được bỏ dữ kiện phụ để kể; không sửa sai dữ kiện giữ lại. | `creator_v2/docs/pm/storytelling-guide.md:69` | V2 Short/Long | PO | review tư liệu | trái template ngoài ép giữ mọi ý |
| V13 | Short tự trả ít nhất một thông tin đã hứa dù mời xem Long. | `creator_v2/docs/pm/storytelling-guide.md:68`; `creator_v2/docs/pm/storytelling-guide.md:119` | V2 Short kể/series | PO | review nghĩa, chưa tự suy payoff | LỆCH-KHUÔN trailer |
| V14 | CK không nên mua/bán, không hứa lợi nhuận; giả định có nhãn rõ. | `creator_v2/AGENTS.md:33`; `creator_v2/docs/pm/storytelling-guide.md:22`; `creator_v2/docs/pm/storytelling-guide.md:61` | CK | PO; không diễn giải luật tài chính ngoài repo | review + kiểm nhãn trên hình | giữ riêng |
| V15 | Bản dịch trích thật gắn TRÍCH DỊCH. | `creator_v2/AGENTS.md:25`; `creator_v2/docs/pm/storytelling-guide.md:24` | V2 lời trích | quy định nguồn | parse/marks hỗ trợ; không chứng minh đúng dịch | giữ riêng adapter |
| V16 | CL trầm có căn cứ; MIM sáng tò mò; CK ấm thực tế. | `creator_v2/docs/pm/storytelling-guide.md:59`; `creator_v2/docs/pm/storytelling-guide.md:60`; `creator_v2/docs/pm/storytelling-guide.md:61` | CL/MIM/CK | PO/gu | không lint gu | LỆCH-KÊNH cần giữ |
| V17 | Codex không viết/soát lời sản xuất V2; Sonnet/Gemini kể và kiểm chéo. | `creator_v2/docs/pm/storytelling-guide.md:196`; `creator_v2/CLAUDE.md:20` | V2 Long | PO bake-off #430, chưa có log bake-off trong phạm vi đọc | quy trình, không lint | 075a là kiểm kê tài liệu, không review script |
| V18 | V2 Long ngân sách 5.500–7.000 âm tiết, 25–32 phút, 12–14 chương. | `creator_v2/CLAUDE.md:20` | CL/MIM/CK Long | PO/chuẩn sáu Long; không đồng rate BUD/FS | floor hiện có; chưa chạy sản xuất | LỆCH-KÊNH; không ép 185 |
| V19 | Đọc thành tiếng, nghe đúng giọng/tốc độ rồi chạy cổng áp dụng. | `creator_v2/docs/pm/storytelling-guide.md:118`; `creator_v2/docs/pm/storytelling-guide.md:72` | V2 lời Việt | KT + PO | không lint chứng minh đã nghe | TRÙNG; CHỈ-TRÊN-GIẤY |
| V20 | Văn phong chỉ cảnh báo; không tự thêm cổng chặn từ checklist. | `creator_v2/docs/pm/storytelling-guide.md:130`; `creator_v2/docs/pm/storytelling-guide.md:122` | V2 Short/Long | PO | phải tách lỗi kỹ thuật/nguồn với gu | LỆCH-KÊNH so strict BUD/FS |
| R01 | Ngân sách 185 cho Short và hook ≤10 token chỉ là giả thuyết thử. | `output/cl_staging/grok/reports/67_audio_script_rules.md:16` | BUD kể/hỏi đáp Short | E3: không ghép chắc analytics–script | đề xuất short_script_lint, chưa bằng chứng triển khai | không nâng thành luật thắng |
| R02 | FS lookup không ép TURN/LOOP; đáp sớm rồi cách tra/framing. | `output/cl_staging/grok/reports/67_audio_script_rules.md:18` | FS bảng tra | GT thích nghi khuôn; E6 hỗ trợ format | chưa lint format lookup đầy đủ | LỆCH-KHUÔN cần giữ |
| R03 | Không đổi 185 tiếng Việt sang 130–140 word/phút Anh khi chưa hiệu chuẩn. | `output/cl_staging/grok/reports/67_audio_script_rules.md:20`; `output/cl_staging/grok/reports/67_audio_script_rules.md:32` | Long/Short Việt | E3 định nghĩa không tương thích | đề xuất đo duration thật | TRÙNG |
| R04 | BUD/lịch sử thử không đọc Chương N; FS có thể giữ thẻ tra cứu. | `output/cl_staging/grok/reports/83_doc_script_audit.md:56` | Long documentary; đề xuất chưa thử | E4, E1 có thẻ FS giữ tốt | chưa luật chung; không tự áp | MÂU THUẪN nếu coi đề xuất là PO |
| R05 | Không dùng bold/HOA như tham số nhấn giọng VieNeu. | `output/cl_staging/grok/reports/83_doc_script_audit.md:15`; `output/cl_staging/grok/reports/83_doc_script_audit.md:46` | VieNeu phiên bản đo trong 83 | E4: bold bị gỡ, chưa nghe tai | clean()/phonemize; không engine nhấn thật | KT, giữ tầng chữ khác giọng |
| R06 | Không quy lời vụn Temiya chỉ cho tỷ lệ câu ngắn. | `output/cl_staging/grok/reports/071_long_temiya_feedback.md:7`; `output/cl_staging/grok/reports/071_long_temiya_feedback.md:9` | Long BUD Temiya | E5: cắt phẩy, nghỉ đều, segment tách | cần nghe đối chứng; probe chỉ minh họa lint | không đủ kết luận nhân quả |
| R07 | Đề xuất TTS cụm và hình 3–8s/beat chưa là luật sản xuất. | `output/cl_staging/grok/reports/071_long_temiya_feedback.md:18`; `output/cl_staging/grok/reports/071_long_temiya_feedback.md:20` | Long BUD | GT sau audit; PO cổng hình mới ở WB:49 | không tự đổi granularity TTS | giữ việc cần Lead quyết |

### B2. Lint và đường gọi thực sự

Các kết luận dưới đây dựa trên đọc code và tám nhóm probe ở D; không chạy build/preflight sản xuất. Các tên O1/O6 ở guide V2 là tên của engine V2, không đồng nghĩa O1/O6 trong hf_batch_render.

| Đường kiểm | File:dòng | Scope, ngưỡng, mức đang có | Khoảng trống/cần phân biệt |
|---|---|---|---|
| Bộ đếm | `long_script_lint.py:117`, `long_script_lint.py:285` | Độ dài câu dùng syllables mở rộng số; timeline nháp dùng tokens/185; segments thật chỉ khi có plan_path và cùng số dòng. | 15 token/43 tiếng trong probe bị ước 4.865s. Khớp số dòng chưa chứng minh segments cùng chữ/giọng/pause hiện tại. |
| Long nghiêm ngặt | `long_script_lint.py:928`, `long_script_lint.py:989`, `long_script_lint.py:1218` | cau_dai >35, ≥4 chi, FS tên con vật và khóa/vân tay TTS sai là LỖI. CLI mặc định exit0 dù có LỖI; --strict mới exit1. | Lint 0 exit không đồng nghĩa không LỖI. Từng câu ≤35 nhưng một say nhiều câu quá dài vẫn chỉ nằm thống kê dòng. |
| Retention runner | `hf_batch_render.py:673` | Câu >35 token; tỷ lệ ≤6 token <1/8; đoạn >90s token/rate thiếu dấu nhịp. Tất cả trả danh sách cảnh báo. | Không mở rộng số, không kiểm chuỗi ngắn; chữ số bất kỳ có thể reset nhịp. Không kiểm “có thông tin mới”. |
| Adapter chạy Long | `library/tools/production_gates.py:44`, `hf_batch_render.py:803` | FS/BUD lane long gọi module.lint(row), lọc LỖI; retention giữ cảnh báo; thiếu/hỏng tool thành finding. | Không truyền plan_path nên đường này không nạp segments bên cạnh plan. Đây là kiểm trước TTS; sau TTS có cổng nhịp hình riêng. |
| Short hook từ điển | `library/tools/hook_lint.py:113`, `library/tools/production_gates.py:21` | TRUU_TUONG và KHUNG_DAU_TRONG chặn; KHONG_DANH_TU_CU_THE chỉ gợi ý. Hàm frame_is_empty xét khai báo, không ảnh render. | Skill/docstring còn ghi mọi cờ exit1. Runtime dùng library/tools; bản scoreboard khác dòng ROOT, không nên giữ hai bản logic. |
| Hook studio hình | `studio.py:358`, `studio.py:473`, `studio.py:684` | BUD/FS/VSD; luma<50, chữ trần, chữ trễ>0,8s; mặc định CB, --strict-hook ngăn render. | Đây là kiểm hình/chữ, không kiểm hook có trả đúng lời hứa. Không suy một ảnh “photo” là đúng nội dung. |
| Guard builder Short | `shortbuild/guards.py:46` | Gọi tên chi/v2/tone/story, rồi hook_errors như LỖI khi có scenes/style/media; daytable miễn v2 và hook hình, vẫn tone/story/tên chi. | Cùng hook_errors đổi mức theo entrypoint. Miễn theo style chứ chưa hồ sơ lookup/kinh-ngắn thống nhất; không tự thêm miễn trong 075a. |
| V2 ngân sách FS/BUD | `hf_batch_render.py:548`, `hf_batch_render.py:588` | Từ 14/11 (SHORT_V2_FROM); BUD80–102/FS68–88 token, loại silence, câu1≤22, câu2 không định nghĩa, có insight, kiểm novelty. | Token được gọi “tiếng”; không phù hợp mọi clip9–15s hoặc story75–120s. Có novelty_ok mới bỏ đối chiếu kho; probe luôn đặt lý do để không đọc kho. |
| Hồn Short | `hf_batch_render.py:615` | Từ day18/11, BUD/FS chặn regex giật gân; hints anchor/source chỉ nhắc. | Regex còn chặn “phát tài lớn” dù PO03/11 cho đề tài tài lộc có khung tham khảo. Regex không hiểu hứa chắc hay nội dung bị phủ định. |
| Tai nghe Short HBR | `hf_batch_render.py:631` | day≥29/11, dấu phẩy cuối dòng ở mọi series không-long; truyện/test_cell >1 câu rào nguồn thì LỖI. | day thiếu hoặc dùng publish_at thay day → bỏ qua; regex bỏ lọt nhiều cách nhắc nguồn, có thể bắt cách dùng không phải rào. |
| Tai nghe Short V2 | `creator_v2/motion/stier/build.py:305`, `creator_v2/motion/stier/build.py:345` | publish_at thiếu **hoặc** ≥29/11: dấu phẩy LỖI. >1 rào: case/story=true/có short_type/test_cell LỖI; còn lại CB. Gỡ {pd} trước TTS. | Khác HBR ở mặc định thiếu ngày và scope/regex. Từ “theo …” rộng có thể không phải nhắc nguồn. |
| V2 hook 01/12 | `creator_v2/motion/stier/script_lint.py:238` | Theme mim/ck/case: >14 từ luôn LỖI; >9, hook_kind, hỏi10 token, hình đầu và title60 đổi CB→LỖI từ publish_at01/12. | Không đo3s thực, không chứng minh thì hiện tại/bi kịch/nguồn/title được trả. publish_at thiếu chỉ CB cho nhóm mới. |
| V2 hook builder khác | `creator_v2/motion/stier/build.py:1032`, `creator_v2/motion/stier/build.py:1078`, `creator_v2/motion/stier/build.py:1110` | hook_errors có chữ lên≤0,5s, hình, neo title/số; >9 từ chặn khi rules<3. retention_hook_lint rules≥3 đòi đúng2 phương án hook≤9 từ. | Không chỉ có short_retention. allow-hook bỏ hook_errors/short_retention trong preflight nhưng **không** bỏ retention_hook_lint; skill cấm dùng để lách đợt mới. |
| Lint BUD legacy V2 | `creator_v2/motion/stier/script_lint.py:53`, `creator_v2/motion/stier/build.py:1197` | Theme bud sau TTS; v2=true thì phần lớn vi phạm chặn: hook≤12, câu≤22/mệnh đề≤14, dẫn nguồn≤8, cite sau25%, callback, câu cuối ?, rehook30–75%, tốc độ2,6–3,8; thiếu sources luôn LỖI. | Có thật trong code nhưng khác pipeline BUD mới HBR/studio; không đưa vào luật chung. Profile chiêm nghiệm thêm nghỉ≥2s, ≥5 từ giác quan và cấm sáo/giảng. |
| Lint mạch V2 Long | `creator_v2/motion/long/script_lines.py:75` | RAO_NGUON: ≥3 câu có cụm nguồn/8 câu; NHIP_DEU: ≥5 dòng liên tiếp <9 token; NHAY_MOC: năm vượt nền>10; META_NGUOI_KE. Chỉ CB. | Không đo ~8% toàn bài; NHIP_DEU ≠ chuỗi ≤6 của BUD. Dò từ không chứng minh sự kiện/động cơ. |
| Lint nhịp mới V2 | `creator_v2/motion/long/script_lines.py:120` | Sau60s, ô30s thiếu beat marker → CB; ước4,2 token/s + pause0,32/0,6. | Có marker chưa chứng minh mới; rate khác HBR185 và Short3,3. Giữ riêng adapter timing. |
| Toàn vẹn V2 | `creator_v2/motion/long/script_lines.py:145` | Chặn markup/câu lặp qua integrity, ROADMAP_CLICHE “trả lời ba câu hỏi”, META_LEAK. | Phải gỡ marks trước lời. Chặn roadmap này mâu thuẫn khuôn nhan_vat nếu chuyển nguyên câu hẹn/chương giữa hai engine. |
| Lời hứa Long | `tools/long_packaging/promise_check.py:146` | Tìm phần đáp, ≥3 câu PASS, dưới3 WARN. | Khớp từ/số câu không phải chứng minh trả đúng; không dùng PASS thay đọc nguồn/đọc lời. |
| Câu trần/hiện hình | `hf_batch_render.py:482`, `hf_batch_render.py:512` | bare_lines tính cả ảnh giữ từ câu trước; runner chặn bare. reveal_issues cảnh báo thứ tự từ xuất hiện. | Không có nghĩa mỗi câu luôn cần ảnh mới hoặc chữ to; không kiểm chữ khóa đúng nghĩa. |
| Cổng hình ảnh hưởng câu | `hf_batch_render.py:1028`, `hf_batch_render.py:1125`, `hf_batch_render.py:1184` | 120s đầu động≤8s/tĩnh≤4s, chữ nền trống≤1,5s; cổng mở40s≥8 hình; cảnh>25s cần slow_hold. | Cổng hiện tại không buộc mọi câu≤10 tiếng. Tách câu để phục vụ hình chỉ là một cách làm, không phải đòi hỏi của hợp đồng TTS. Không render để chứng minh trong task này. |

### B3. Các mâu thuẫn cần quyết định trong 075b

| ID | Hai phía, trích điểm gốc | Nhận định và cách gỡ đề xuất |
|---|---|---|
| X01 | L13/L14 “ngắn mỗi4–6 câu” so R06 Temiya vụn | Không phải mâu thuẫn hoàn toàn: quota tổng khác nhịp cục bộ. Temiya có18,5% câu ngắn vẫn bị chê do chuỗi/phẩy/nghỉ. Giữ nhịp linh hoạt; thêm cảnh báo chuỗi; không hạ quota chỉ từ một bài. |
| X02 | L62 mỗi câu≤10 suốt120s so L21/L42 câu trọn, median12–16 | Cổng hình mới đã cho8s ảnh động nhưng brief vẫn hướng3s/câu và hình riêng/câu. Đề nghị bỏ ép câu10 khỏi lõi; viết trọn theo beat, giữ cổng hình và kiểm timing thật. PO quyết chỉnh brief. |
| X03 | L07/L41 một câu/dòng so gộp2–3 câu≤45 | Hai chế độ granularity chưa tách. Giữ đầu vào mặc định một câu trọn/dòng; nếu thử TTS cụm thì ticket/adapter riêng, không âm thầm gộp cả hệ. |
| X04 | E2 ngân sách185 so giọng mới175; timeline token so độ dài tiếng đọc | Công bố hai số đo khác nhau, lấy segments đúng phiên bản làm chuẩn cuối. Hiệu chuẩn từng giọng/ruleset trước đổi ngân sách; không chỉ thay185 thành175 khắp repo. |
| X05 | L08 tối đa3 năm/mục so L43 tối đa2 năm | Chọn trần kỹ thuật≤3 mục, khuyến nghị1–2 năm dài nếu câu vẫn≤35 tiếng. Cần PO/Lead chọn, chưa tự sửa reference. |
| X06 | L12≤2 CTA so lint >3 mới báo | Đồng bộ profile chuẩn≤2 câu; tách câu hỏi bình luận khỏi CTA subscribe; night có ngoại lệ phút2. Không bắt bằng một regex chung mọi lời mời. |
| X07 | S01/S02 thắng9–15s so S19 yêu cầu68–102 token/21–27s | Lỗi scope khuôn, không phải dữ liệu thắng bị sai. Hồ sơ lookup/kinh-ngắn phải có ngân sách riêng, không dùng ngoại lệ tùy hứng. daytable đã miễn nhưng chưa giải quyết mọi dạng bảng. |
| X08 | PP:17 trả ngay so A2/hooks và legacy V2 cite≥25%/giữ vòng | Trả sớm là đúng lookup; truyện trả theo diễn tiến. Không một mốc payoff cho cả hai. Partial payoff90s của Long vẫn khác đáp cuối. |
| X09 | L25 bảng≤45s so FM:112 hẹn bảng nam/nữ cuối | Cùng FS tra cứu nhưng mẫu cũ còn xung đột. Giữ bảng sớm; bảng cuối chỉ tổng hợp bổ sung, không lời hứa giữ người. |
| X10 | L67 giác quan trung tính so rules.md, luật19 mọi chi tiết truyện kinh có nguồn; LS:33 cho dựng không khí | User hiện tại giữ ranh giới truyện kinh. Trong 075b ghi rõ: không gán chi tiết thêm cho Đức Phật/kinh; lời người kể và minh họa ngoài truyện phân lớp. Dân gian có khung theo PO06/11 khác với kinh. Cần Lead/PO quyết phần nhân vật lịch sử BUD ngoài kinh. |
| X11 | S21 cấm “phát tài lớn” so rules.md, luật5 (PO03/11) cho tài lộc tham khảo | Probe xác nhận regex chặn thật. Ghi đề nghị thu hẹp vào hứa chắc/số tiền/đánh bạc/khuyên vay–đầu tư; không sửa bộ kiểm hay dùng né từ trong075a. |
| X12 | SS:119 studio CB so guards.validate biến hook thành LỖI; SP:78 nói mọi cờ exit1 | Tài liệu chưa mô tả entrypoint và blocking_flags mới. 075b cần bảng gate theo engine/profile; noun chỉ advisory không được ghi thành lỗi. |
| X13 | S13 HBR thiếu day bỏ qua so V2 thiếu publish_at vẫn áp ear | Cùng luật câu trọn nhưng ngày/schema khác. Canonical effective_date, mapping rõ; không gọi date thiếu là clip cũ. Bảo toàn legacy đã hẹn theo hồ sơ có thật. |
| X14 | L24 BUD/FS không thẻ chữ10s so V2 survival slam/quote lớn | Giữ riêng thẩm mỹ/miền; BUD thầy hiền có nghịch lý nhưng không copy tông hình sự. Kịch tính có nguồn khác giật gân. |
| X15 | MG:33 cấm ảnh câu0 so S07/S12 cần vật/hình ngay | Reference thiết kế cũ trái hook mới; không để nó chi phối lời. Khi sửa075b cập nhật/chuyển lịch sử, không tạo luật lõi “không ảnh đầu”. |
| X16 | LR:54 đọc chap, FM:178 không đọc số; R83:56 đề xuất BUD không đọc chương | Đề xuất của báo cáo83 chưa thành PO. Giữ title hiển thị vs lời đọc thành hai trường; thử không đọc thẻ ở documentary; FS giữ khả năng tra mục lục. |
| X17 | SO:4 “số liệu thắng rồi quyết định” so PO mới thay cách kể | Dữ liệu cũ có nhiễu không tự phủ quyết chỉ đạo PO mới. Tài liệu chung cần ghi quyết định đang hiệu lực, ngày, scope, rồi bằng chứng/độ chắc và cách đo lại. |
| X18 | V2 guide§13 cấm kể hộ động cơ so §14 nới16/11 | Guide tự nói§14 đè§13; chỉ người sống và sự thật cứng là giới hạn cần kiểm, không biến câu không khí thành lỗi. Giữ quyền kể, không hợp nhất thành cấm phóng tác mọi kênh. |
| X19 | Bare bắt thiếu ảnh/visual/chữ so bản mới không fallback từ đầu câu | Code bare vẫn hoạt động; luật này là hợp đồng hình, không bằng chứng phải viết câu cụt có “từ hot”. Lõi audio không sinh markup để lấp cảnh. |
| X20 | S16 probe short_retention chuyển CB→LỖI01/12 so hook_errors builder đã chặn≤9 tùy rules | Kết quả hàm riêng không đại diện preflight. Ghi đầy đủ đường gọi; không nói Short trước01/12 chắc chắn build qua. |

### B4. Nhóm trùng và phần chỉ trên giấy quan trọng

- **TRÙNG:** câu35 tiếng (L07), chi≤3 (L45), không chào (L01), câu trọn (L21/S13/V11), số dễ nghe (L44/V11), rào nguồn (L17/S14/V06), callback/cầu nối (L09/L10/L32), nguồn kinh/FS (L38/L65/P04). Một nơi định nghĩa, các skill trỏ đúng mục và chỉ thêm delta.
- **CHỈ-TRÊN-GIẤY ở máy:** lời hứa có trả thật; cầu nối có quan hệ nhân–quả; chi tiết giác quan có nguồn; ý nghĩa callback/mô-típ; median/không chuỗi ngắn; tỷ lệ8% Long; thì hiện tại; câu≤20 cho thoại; vị trí CTA sau payoff; hình “mạnh nhất”; nghe thử đúng giọng. Đây là lý do giữ review có người/model khác, không gọi “lint đầy đủ”.
- **LỆCH-KÊNH:** VSD được studio hook gate nhận diện, nhưng không tự thừa hưởng FS tham khảo/chi, BUD kinh hoặc survival CL. `creator_v2/docs/pm/storytelling-guide.md:5` ghi FS/VSD chỉ áp khi PO chỉ định. CK giữ nhãn giả định; MIM giữ giọng sáng; CL giữ chuẩn người thật/nguồn. Ngay trong một kênh, lookup/kinh-ngắn/truyện/đêm là các khuôn khác.

## C. Bảng đề xuất làm đầu vào 075b

### C1. Kỹ thuật ngoài × trạng thái trong repo

“Không lấy” vì trái số liệu ghi rõ E nào; nếu chỉ trái kiến trúc/PO thì ghi đúng lý do đó, không mượn uy tín analytics. A1–A10 trỏ các permalink đã đọc ở phần A.

| Kỹ thuật ngoài | Trạng thái | Đối chiếu repo và lý do / cách thích nghi |
|---|---|---|
| A1 Hook từ điều muốn đọng lại và khoảng cách nhận thức | **Đã có** | Câu chiến lược L37 và cung A→B L29. Giữ thao tác ngắn trong brief, không thêm vòng phỏng vấn vào pipeline đã có brief. |
| A1 Shape bằng mong muốn–trở ngại và ba câu xương sống | **Đã có** | Nhân vật–cái giá V01/L58. Dùng kiểm quan hệ sự kiện; không ép ba hồi vào lookup. |
| A1 Flesh có chi tiết rồi bớt giải thích | **Đã có** | WB show/chi tiết L51/L58. Chỉ lấy trong miền nguồn/phỏng dựng đã cho, không tạo thêm hành động Đức Phật. |
| A1 Judge bắt viết lại phần yếu, không chỉ chấm | **Thiếu – nên lấy** | WB có10 câu tự kiểm nhưng chưa buộc chỉ ra dòng yếu/sửa/so lại. Thêm receipt trước→sau và lý do, không thêm điểm giả retention. |
| A1 Cắt một nửa rồi một nửa tiếp | **Trái ràng buộc – không lấy** | Không có số kênh chứng minh nên cắt75%; Long có sàn/độ sâu và nhiều dữ kiện cần giữ. Chỉ cắt câu không làm việc. |
| A2 Khớp title–thumbnail–khung đầu–lời hứa | **Đã có, cần làm rõ** | P01, S07, V08. Thêm người viết chỉ đúng câu đáp, thay việc coi keyword overlap là đáp đúng. |
| A2 Audit vùng rơi với baseline cùng kênh/khuôn | **Đã có** | EV khớp câu/curve, LP quy tắc cùng tuổi/traffic. Chuẩn hóa phiếu thử, không chuyển tỷ lệ65–70% của ngoài thành pass/fail kênh. |
| A2 Bảng vòng và callback | **Đã có** | L09/L30/L55. Thiếu kiểm đóng đúng nghĩa; không tăng số từ móc để chiều regex. |
| A2 3–6 chương và giữ payoff chính sát cuối cho mọi bài | **Trái số liệu/khuôn – không lấy** | E1 cho thấy trả muộn/lý thuyết sớm làm rơi ở FS; L25 đòi bảng45s. Số chương do profile30 phút; không copy video10–12 phút. |
| A2 Hook ba lớp | **Thiếu – nên lấy có điều kiện** | Brief ghi đồng thời câu1/khung0/chữ, tránh ba thông điệp lệch nhau. Không bắt chữ phủ khác hẳn lời khi đó là phụ đề/bảng tra đã thắng. |
| A3 Lưu giọng, đối tượng và chỉnh sửa theo kênh | **Thiếu – nên lấy ở mức tài liệu** | Hồ sơ nguồn chuẩn dùng chung, không cần cài script_db/database ngoài. Ghi channel+format+engine+effective_date và lý do ngoại lệ. |
| A3 Chào + giới thiệu + recap dài + CTA nhiều mục | **Trái số liệu – không lấy** | E1 rơi tại meta/recap/CTA; L01/L12 đã có giới hạn. Không dùng template chuẩn YouTube ngoài làm mặc định. |
| A4 Đọc lời trước brief rồi tự tóm một ý | **Thiếu – nên lấy** | Phát hiện lời đáp lệch ý định; tự soát cùng người chỉ là mô phỏng. Khi Lead giao model khác mới gọi kiểm độc lập. |
| A4 Tách kiểm tư liệu khỏi chỉnh gu | **Đã có, cần giữ** | V02/V20 và LS38; người kiểm chỉ yêu cầu sửa chạm dữ kiện. Không copy máy chấm salience để cắt cảnh phóng tác PO đã cho. |
| A4 Answer-first mặc định / nhiều cổng-agent | **Không lấy nguyên bộ** | Answer-first hợp tra cứu nhưng không mặc định truyện; workflow nhiều vai là tham khảo, task075b chưa cần cài framework hoặc tự tăng chi phí. |
| A5 Gỡ jargon, câu liền có quan hệ | **Đã có** | L16/L42/V11. Giữ đầu ra từng câu, dùng đại từ rõ chủ thể cho một người kể. |
| A5 Giữ thứ tự/cấu trúc nguồn tuyệt đối | **Trái PO và chẩn đoán nội bộ – không lấy** | Guide§14 muốn nhân vật–cái giá; R83 phát hiện đọc hồ sơ/menu khô. Giữ sự thật, được đổi thứ tự kể có mốc rõ. |
| A6 Hai host, phản ứng, câu bỏ lửng,1500 từ/10 phút | **Trái kiến trúc/KT – không lấy** | Một VieNeu đọc từng dòng; L21 và E5 chống mảnh cụt/nghỉ đều. Không có thử retention để gọi hai-host “thua” trên kênh. |
| A7 Nối ý tự nhiên, sửa đúng phần editor chỉ | **Đã có, nên làm nhất quán** | V12 và guide§13. Giữ những câu đang kể tốt; mỗi vòng có diff và kiểm lại phần đổi. |
| A7 Phản ứng1–2 từ/filler để tự nhiên | **Trái KT/gu – không lấy** | Phản ứng đối thoại không cần cho độc thoại; tăng segment/pause. E5 chỉ là cảnh báo liên quan, không thử trực tiếp neuralnoise. |
| A8 Giả lập người nghe không nhìn biểu đồ | **Thiếu – nên lấy** | Kiểm chủ thể, đơn vị, quan hệ; bảng FS vẫn có hình nhưng lời phải hướng dẫn cách tra thay đọc mọi ô. Không bắt lặp toàn bộ bảng cho người chỉ nghe. |
| A8 Đọc nguồn thường xuyên, intro/fundamentals dài | **Trái PO, có QS hỗ trợ – không lấy** | L17/V01 và E1 meta/lý thuyết rơi; nguồn giữ trong notes/hình/mô tả, vẫn đọc giới hạn khi cần để không đổi nghĩa. |
| A9 Ghi thay đổi/hậu quả mỗi beat | **Thiếu một cột thống nhất – nên lấy** | Beat sheet đã có vai/cảm xúc; thêm câu hỏi soát “điều gì thay đổi?” là đủ, chưa bắt schema mới cho V2. |
| A9 Ép chương tốt–xấu, sinh thoại/cốt và cấm báo trước | **Trái nguồn/PO – không lấy** | BUD không thêm tình tiết, người thật không sinh sự kiện; callback/open-loop có chủ ý. Không cần chạy máy viết fiction. |
| A10 Cùng input/model/giọng, cố định SHA và giữ mọi lượt thử | **Thiếu – nên lấy** | Phiếu pilot075b nối prompt revision với lint/nghe thử và sau phát hành mới nối retention. Tách sửa văn bản với đổi giọng để biết biến nào đổi. |
| A10 Chỉ mục/sao như chứng nhận chất lượng | **Không lấy** | Tác giả nói kiểm thông tin, không chứng minh đầu ra; sao không đo tiếng Việt hoặc retention. |

### C2. Khung tài liệu chung đề xuất

Đề xuất một tài liệu chuẩn `docs/script/audio-script.md`; các skill chỉ dẫn tới mục liên quan, vẫn sở hữu quy trình/format/hình/render của mình. Hồ sơ riêng có thể nằm dưới `docs/script/profiles/`. Đường dẫn là phương án, chưa tạo trong075a.

Mục lục:

1. Phạm vi, thứ tự quyết định và định nghĩa: câu đọc, dòng TTS, beat, tiếng đọc, token, duration có/không pause.
2. Hợp đồng đầu vào/đầu ra: lời sạch, một câu trọn/dòng, metadata/nguồn/hình ở ngoài lời.
3. Viết cho một người nghe: chủ thể, động từ, liên kết ý, thuật ngữ và con số.
4. Lời hứa và tiến triển: mở đúng điều title hứa, cung cấp giá trị, kết trả được.
5. Nhịp câu và khoảng lặng: biến thiên theo cảnh, không cắt vụn để đạt quota.
6. Sự thật, diễn giải, phỏng dựng: miền nào được gì; nguồn trong notes; lời bắt buộc giữ mức chắc chắn.
7. Tự soát viết → chấm → viết lại và cách nghe thử VieNeu.
8. Hồ sơ kênh/khuôn và ngoại lệ được Lead/PO ghi nhận.
9. Adapter engine và ma trận lint: file gọi, schema, effective_date, mức LỖI/CB, clock.
10. Bằng chứng, ngày thay luật, kết quả pilot và việc cần đo lại.

**Luật lõi đề nghị, đủ dùng mọi kênh:**

- Lời phải hiểu ở lần nghe đầu: nghe rõ ai làm gì và điều gì thay đổi. Một câu trọn là đơn vị tác giả; mặc định một dòng TTS/một câu, không mảnh ngắt bằng dấu phẩy. Một câu ngắn tự đủ nghĩa vẫn hợp lệ.
- Nói trực tiếp với “bạn” khi phù hợp gu; dùng từ quen, giải thuật ngữ ở đúng chỗ. Không bắt mọi bài phải có nhân vật, câu hỏi tu từ hoặc cảm xúc theo quota.
- Tên/số viết theo cách VieNeu cần đọc. Phân biệt số làm tròn để nghe và định danh phải chính xác; năm sinh, ngày, mã kinh có đối chiếu hình/notes. Chữ đậm/HOA là markup hình, không cam kết nhấn giọng.
- Một lời hứa trung tâm có chỗ trả rõ; Short tự có giá trị. Cách trả sớm, từng phần hay sau truyện do profile chọn, không dùng “giữ tới cuối” cho bảng tra.
- Mỗi đoạn phải tiến tới bằng diễn biến, lý do, chứng cứ hoặc hệ quả. Đổi độ dài câu theo ý; khoảng lặng do điểm đọng, không do giới hạn caption/hình bắt tác giả cắt câu.
- Sự thật cứng và lời trích truy được nguồn; mức không chắc và khung truyền thống không bị xóa để bớt rào lời. Nguồn chi tiết ở tài liệu/hình/mô tả, lời chỉ đọc mức cần thiết cho người nghe hiểu đúng.
- Giữ riêng quyền phỏng dựng theo kênh/miền, nhất là truyện kinh và người thật còn sống. Nhãn hình không biến một khẳng định sai thành đúng.
- Bản giao tách lời, nguồn, timing/voice, hướng hình. Chạy đúng lint của engine, nêu lỗi/cảnh báo và ngoại lệ; nghe đúng giọng ở đoạn mở, đoạn chứa số/tên, đoạn đỉnh và kết.
- Mọi ngưỡng số về tốc độ, câu, hook, payoff, chương là **cấu hình profile có bằng chứng/ngày**, không phải chân lý chung. Kiểm timing cuối bằng âm thanh đúng bản, không nhân word/phút Anh.

Thứ tự xử lý xung đột đề nghị: **chỉ thị PO/user đang hiệu lực đúng phạm vi → luật nguồn/kênh đúng miền → hợp đồng kỹ thuật engine → dữ liệu quan sát kèm giới hạn → mặc định biên tập → kỹ thuật ngoài**. Dữ liệu mới đủ mạnh thì trình PO sửa luật; không tự dùng tương quan nhỏ để đảo quyết định. Khóa bảo mật/không đăng/không commit là luật thao tác, không trộn vào luật văn phong.

### C3. Phần riêng giữ lại

| Hồ sơ | Giữ phần riêng | Vì sao không nhập thành luật cho tất cả |
|---|---|---|
| BUD | Giọng thầy hiền, không gieo tội lỗi; lời/việc Đức Phật có kinh kiểm; Jātaka phân kệ/chú giải, Cowell; truyền thuyết và biểu tượng có khung đúng; nhịp chiêm nghiệm. Alt trích kinh nếu cấu hình tập đã bật, không thành hai host. | Luật nguồn và quan hệ với người nghe đặc thù. Survival không được biến thành dọa nhân quả; phỏng dựng lịch sử không mở rộng quyền bịa trong kinh. |
| FS | Tên chi, tối đa3 tên/dòng; số sinh bằng code; truyền thống/tham khảo; chủ đề tài lộc được làm theo PO03/11, giới hạn hứa chắc/số tiền/đánh bạc/vay–đầu tư. | Định danh và khung nội dung khác BUD/CK. Không làm tròn năm sinh hay gọi tên con vật để rút tiếng. |
| FS lookup | Bảng sớm, hướng dẫn tự tra, chỉ đọc vài ví dụ; Short giữ khung để lưu. Long≤45s có bảng; không hẹn bảng chính cuối. | Mục tiêu tra của khán giả; E1/E6 không ủng hộ giữ đáp án như truyện bí ẩn. |
| VSD | Giữ đường studio hook cho VSD; giọng rõ, phân sự kiện/sử/dân gian và mức chắc chắn; chọn khuôn theo brief. | Trong nguồn được giao chưa có hồ sơ lời VSD đầy đủ hay cohort chứng minh riêng. Không tự phát minh luật giọng VSD hoặc lấy số FS làm chuẩn; Lead cần chỉ nguồn/brief cho075b. |
| CL | Trầm, nhân vật/cái giá, phân sự kiện–lời khai–chưa rõ; không gán tội thiếu căn cứ; người sống không dựng lời/nội tâm; mở survival đúng nguồn. | 075a chỉ kiểm văn bản hướng dẫn, không đọc/sửa tài sản kênh cấm. Giữ ranh giới người thật và thông tin vụ việc. |
| MIM | Sáng, tò mò, cơ chế gắn đời sống; người/năm/bước ngoặt khi đúng đề; không phóng đại tác động. | Không ép giọng thầy giảng hoặc tông án mạng. Thuật ngữ cần cách đọc riêng nhưng không đồng nghĩa nguồn làm trục. |
| CK | Ấm, thực tế; lựa chọn và cái giá; tiền/số làm tròn dễ nghe, giả định nhận diện/nhãn; không khuyên mua/bán, không hứa lợi nhuận. | Phép tính và bối cảnh giả định phải nghe hiểu; không đồng nhất tài lộc truyền thống FS với dự báo tài chính CK. |
| Long nhân vật | Người/mục tiêu/cái giá; câu hẹn đúng chương nếu dùng khuôn nhan_vat; số chương/thời lượng hiện có theo engine. | Mốc≥30 phút/12–16 là quyết định khuôn, không áp clip20–60s hoặc tra bảng. Không ép tên vào70% title cho mọi Long. |
| Long tuyển tập/Q&A | Truyện1 trước60s / câu đáp đầu chương theo profile; chương tự đứng được. | Không dùng chung một cold open trừu tượng cho tất cả thể loại. |
| BUD đêm nghe | Êm, không móc gắt; nhịp/pause/CTA và kết lặp riêng. | Mục đích nghe khác giữ tò mò; night bỏ quota rehook của standard. |
| Short kể20–60s | Một ý, câu trọn, hook cụ thể, giá trị tự đủ; nhịp/callback theo truyện. MIM/CK/CL giữ luật3s/9 từ từ ngày hiệu lực. | Không lấy ngưỡng từ Long hay ép mọi Short phải “lật” hai lần. Story BUD75–120s hiện có là nhánh riêng, ngoài đích20–60s của task. |
| Short thắng9–18s | Bảng tra, câu kinh, biểu tượng; số câu/ngân sách ít và giữ hình cuối theo khuôn. | Ngoại lệ có bằng chứng E6; không bỏ dạng thắng chỉ vì luật v2 phổ quát. |
| Adapter kỹ thuật | say/chap/tts.alt/visuals và {pd}/marks ở V2; caption group tách riêng câu lời; hiệu lực ngày/phân legacy. | Một luật nghe có thể dùng chung nhưng API/index/timing khác; thống nhất văn bản không buộc port engine. |

### C4. Luật đo được → lint cụ thể đề nghị

**Toàn bảng là phương án cho075b.** Giữ cổng hiện tại cho sản xuất tới khi Lead/PO duyệt. LỖI mới chỉ cho điều tất định hoặc vi phạm ranh giới đã ghi rõ; gu và phép suy ngữ nghĩa chỉ CB/review. Ngưỡng mới GT phải chạy pilot trước, không viện “chuẩn thị trường”.

| Tên check đề nghị | Phép đo / ngưỡng rõ | Mức đề nghị | Scope và căn cứ |
|---|---|---|---|
| audio.profile_missing | Không xác định được channel+format+engine+phiên bản ruleset → không tự chọn bộ ngưỡng. | LỖI đầu vào cho bài mới; legacy có mapping Lead xác nhận | Tránh nhầm áp v2 lên lookup; chưa bắt thêm field cho mọi spec V2, có thể resolver từ metadata sẵn. |
| audio.date_unresolved | Bài mới thiếu ngày hiệu lực hoặc day/publish_at mâu thuẫn → finding; bài legacy đã có lịch xác thực dùng mapping. | LỖI đầu vào với cổng phụ thuộc ngày | X13/X20; không suy thiếu ngày là bài cũ, không chặn sửa bài đã xuất chỉ vì metadata mới. |
| audio.cau_tron | Sau bỏ markup/ngoặc trích hợp lệ, dòng kết bằng dấu phẩy → finding, loại heading/silent metadata. | LỖI cho bài mới sau mốc áp; CB legacy | Hiện đã có ở Short; Long đang CB. Không tự NLP “thiếu chủ vị” thành lỗi, vì “Không phải.” có thể là câu đủ nghĩa. |
| audio.markup_leak | Lời sau adapter còn URL, JSON key, note [PAUSE]/{pd}/dấu kỹ thuật chưa gỡ → >0 là finding. | LỖI | Hợp đồng kỹ thuật, tận dụng integrity hiện có; không chặn dấu câu bình thường. |
| audio.cau_dai | Long BUD/FS >35 tiếng đọc sau normalization; profile khác giữ trần hiện có, không lấy35 ghi đè22/14/9 của Short. | LỖI nơi hiện là lỗi; CB ở engine quy định phong cách chỉ CB | E1/KT; một hàm đếm, nhiều cấu hình. Hiệu chuẩn tên/số/%, không chỉ split. |
| audio.dong_nhieu_cau | Mặc định một dòng có>1 câu → CB; nếu tổng>35 hoặc vượt ngân sách dòng profile → CB riêng. | CB; không tự chặn toàn V2 | X03/L41, nhãn speaker/abbreviation cần parse đúng; chỉ TTS cụm được duyệt mới đổi chính sách. |
| audio.chi_day | Một dòng có≥4 tên chi; FS dùng tuổi+tên con vật → finding. | LỖI | KT đã có; chỉ scope gọi tuổi FS, tránh bắt tên động vật trong truyện BUD. |
| audio.nhip_ngan_day | ≥3 câu liên tiếp≤6 tiếng đọc → CB, có thể giải trình đoạn đỉnh. | CB, ngưỡng GT từ L14 | Không coi tỷ lệ18,5% tự là xấu; không sửa câu chỉ để đủ quota. Không bắt thêm marker cảm xúc vào mọi spec. |
| audio.nhip_ngan_thieu | Long standard dưới1/8 câu≤6 → báo thống kê + CB như hiện có; night/lookup không áp. | CB; đề nghị PO chọn giữ/giảm sau pilot | E1 quan sát; bỏ yêu cầu “đúng mỗi4–6” như cổng cứng. |
| audio.rao_nguon | Long kể số câu nhắc nguồn / câu nói >8% → CB; Short truyện/test_cell>1 → mức profile hiện hành. | CB Long; LỖI Short ở scope/ngày đã duyệt | Không tính source trên hình; tách framing FS/bất định làm đổi chân trị khỏi filler. Dò từ chỉ là ứng viên, cho giải trình false positive. |
| audio.meta_som | Long FS/BUD meta trước25s; V2 trước30s; không chào theo profile. | Giữ CB/LỖI của từng engine | Đo bằng clock thật nếu có; ước lượng ghi rõ. Không chọn mốc chung27s. |
| audio.hook_window | Long móc<40s; V2 Short câu1≤9 từ và câu hỏi trước3s thực khi có alignment, nếu chưa thì10 token là heuristic. | CB ý nghĩa; LỖI cấu trúc theo ngày/profile đã có | Không dựa chỉ có chữ “nhưng” để tuyên bố hook hay; không bê shock giật gân sang BUD. |
| audio.payoff_ref | Brief/notes có promise ID mà không trỏ câu trả lời → thiếu liên kết; có liên kết vẫn cần đọc nghĩa. | CB metadata; người soát quyết sự thật | Không cổng AI “hay/dở”; tận dụng bảng vòng/notes sẵn, không bắt tất cả pipeline thêm schema trong075b. |
| audio.loop_orphan | Vong/questions trỏ chương/ID không tồn tại hoặc đóng trước mở → finding; cụm đóng không thấy → CB. | LỖI tham chiếu hỏng ở adapter mới; CB nghĩa | Kế thừa CAU_HOI_HEN_CHUONG/vong_khong_dong; không ép lookup phải đủ3 vòng. |
| audio.lookup_early | Format tra_cuu không có bảng≤45s hoặc hẹn bảng chính cuối. | LỖI như hiện tại | Giữ ngoài audio core vì cần visual, nối báo cáo chung; bảng thật có đọc được vẫn QA khác. |
| audio.story1_early | Tuyen_tap truyện1 bắt đầu≥60s hoặc có chương lý thuyết trước truyện1. | LỖI như hiện tại | Dùng marker có thật hoặc reviewer xác nhận, không chỉ đo tên chương. |
| audio.cta_count | Long standard >2 câu subscribe/CTA sau gộp đúng câu; câu hỏi bình luận tách loại. | CB; đồng bộ tài liệu/code sau PO | Night giữ ngoại lệ; Short lookup CTA lưu/pause không tự chịu cùng luật. |
| audio.source_coverage | Claim/quote đã đánh dấu cần nguồn mà thiếu source_ref → finding. BUD lời Phật thiếu receipt sutta/đối chiếu Bắc tông → chưa đủ giao. | LỖI hồ sơ, người soát kiểm nội dung | Không tự kết luận URL có là sự thật đúng. BUD có tên kinh phải nguyên văn theo rules; không kiểm mạng/kinh trong lint câu thuần. |
| audio.number_origin | FS claim số/bảng khai nguồn tính mà không có code/version/giá trị sinh → finding; CK ví dụ thiếu nhãn → finding. | LỖI theo miền đã duyệt | Không chạy code số lịch cho việc đếm câu tài liệu; dùng artifact đầu ra code của sản phẩm075b/pilot. |
| audio.tts_override_stale | Pause/tempo trỏ dòng ngoài phạm vi, hoặc fingerprint khác câu hiện tại → >0 finding. | LỖI như hiện tại | Ngăn sửa script xong giữ nhịp/voice sai dòng. Mở rộng receipt gồm voice/ruleset/text hash. |
| audio.timing_stale | Manifest không khớp text hash, voice/ruleset hay pause/tempo → không được gọi clock thật. | CB và hạ xuống clock ước; LỖI khi tuyên bố QA timing cuối | Cùng số dòng là chưa đủ. Không tự hạ gate timing; chạy lại TTS phần thay khi có ticket sản xuất. |
| audio.budget_duration | Khi có segments: tính speech+pause+tail riêng; vượt duration band của profile là finding. Khi chỉ có nháp: báo ước và khoảng bất định. | LỖI khi band đã được phê duyệt và đo thật; CB cho ước | Không invent tolerance chung. Hiệu chuẩn giọng175/185 trước chốt ngân sách; Long sàn theo profile, không chung V2/BUD. |
| audio.new_beat_gap | V2 sau60s có cửa sổ30s thiếu beat → CB như hiện; đọc lại ý để biết mới. | CB | Không dùng con số/câu hỏi rỗng làm bằng chứng tiến triển. |
| audio.repetition | Câu lặp nguyên văn theo cổng hiện có; motif/callback có chủ ý phải được nhận diện/giải trình. Cụm2 tiếng≥3/5 và mở câu>2% chỉ gợi ý. | LỖI toàn vẹn theo engine; CB/GỢI Ý văn phong | Không chặn motif bằng check phong cách mới; quote kinh có lý do cần lặp. |

Không đưa `hf_qa --overflow/--contrast`, luma, nhịp8s hay media≥1/5 vào “lint audio” như thể chỉ đọc chữ là đủ. Chúng là cổng hình/audio sau dựng có link sang báo cáo. Không cho lint sửa nhịp bằng cách cắt ngang từ ghép hoặc bắt tự đệm câu≤6 tiếng.

### C5. Vòng tự soát viết → chấm → viết lại

Đáng lấy từ A1/A4/A7/A10 vì repo có checklist nhưng còn thiếu cơ chế **chỉ đúng điểm yếu, sửa thật và xác nhận lại**. Không tự coi điểm model là dự báo view.

1. **Chốt brief nhỏ:** channel/format/engine, người nghe, một lời hứa, 3–5 sự kiện quan trọng có nguồn, ngân sách theo giọng, giới hạn phỏng dựng. Dùng plan đã duyệt; không mở thêm quy trình xin duyệt trong bước viết.
2. **Viết:** Sonnet hoặc người viết Lead chọn soạn từ hồ sơ, giữ quyền kể đúng miền. Không đưa timestamp/nguồn dài/chú thích âm nhạc vào lời.
3. **Tự chấm:** đọc hoặc nghe một lượt không nhìn hình, ghi một ý đọng lại và nơi mất mạch. Sau đó mở lại brief và nguồn. Đây là self-review, không ghi “kiểm độc lập”.
4. **Sửa:** chọn tối đa3 điểm yếu ảnh hưởng nhất; ghi dòng trước→sau, lý do, dữ kiện giữ. Sửa phần yếu hoặc cả đoạn nếu liên kết đứt, không chỉ thay từ để qua regex.
5. **Kiểm lại:** chạy lint đúng engine; nghe mở/số-tên/đỉnh/kết bằng đúng giọng. Đổi chữ/timing/voice thì receipt cũ hết giá trị ở phần đổi.
6. **Lead review:** theo routing hiện tại; V2 Sonnet/Gemini kiểm chéo, Codex không nhận viết/soát lời sản xuất. Tài liệu075a này không thay routing đó.
7. **Giới hạn vòng đề nghị:** tối đa2 vòng tự sửa có ghi nhận cho một brief; còn lỗi sự thật/timing chưa sửa thì giữ finding và chuyển Lead, không ghi đạt vì hết lượt. Hai vòng là GT quản lý chi phí, không ngưỡng chất lượng đã đo.

Rubric8 mục, mỗi mục0–2: 0 thiếu/sai; 1 có nhưng yếu; 2 rõ và nghe được. Không cộng tổng rồi lấy điểm cao bù sai nguồn.

| # | Tiêu chí | Bằng chứng người viết phải chỉ ra |
|---|---|---|
| 1 | Đúng lời hứa và người nghe | Câu mở + câu đáp; tự tóm được một ý. |
| 2 | Có tiến triển theo khuôn | Mỗi đoạn thêm diễn biến/lý do/hệ quả; lookup cho tra được. |
| 3 | Nghe hiểu không cần đọc script | Chủ thể/đại từ/tên/số/đơn vị rõ ở lần đầu. |
| 4 | Nhịp tự nhiên | Không dòng phẩy/mảnh cụt/chuỗi đều; khoảng lặng có điểm đọng. |
| 5 | Đúng giọng kênh | BUD hiền; FS tham khảo; CL/MIM/CK giữ register riêng. |
| 6 | Đúng sự thật và miền sáng tạo | Claim/quote/số có nguồn; khung/nhãn không làm biến thành sự thật giả. |
| 7 | Thời lượng và khả năng TTS | Bộ đếm chuẩn, voice/ruleset đúng, lint output, đoạn nghe thử. |
| 8 | Kết xứng lời mở | Trả điều hứa/callback khi khuôn cần; CTA gọn đúng lúc. |

Đề nghị chỉ giao Lead khi không còn LỖI hiện hành, mục6/7 không còn finding chặn và mỗi mục liên quan đạt ít nhất1; rubric là CB/phiếu review, không cổng phong cách tự động mới cho V2. Chọn “không áp” có lý do cho lookup/kinh-ngắn, không ép nhân vật/callback vào mọi clip.

### C6. Thử và thứ tự triển khai075b để PO quyết

- **Đợt1: hợp nhất tài liệu và sơ đồ kế thừa.** Một nơi định nghĩa câu/token/clock/source/PD; skill cũ dẫn link + delta. Giữ rubric và danh mục ngoại lệ, không sửa diện rộng engine. Lưu ngày/scope/lý do/bằng chứng của từng luật.
- **Đợt2: đồng bộ phần tất định có ticket code riêng.** Dấu phẩy, cảnh báo chuỗi, count dùng chung ở nơi cho phép, map ngày/profile, sửa lệch CTA/tài lộc, fingerprint timing. Không sửa các bộ kiểm độc lập của Lead.
- **Pilot lời:** cùng một hồ sơ nguồn/brief, giữ mọi lượt, ghi model/prompt/SHA/voice/ruleset. So bản kiểm soát với bản sửa, trước hết Long BUD kể và FS lookup; thêm V2 kể và Short thắng làm regression. Không đổi voice và cách viết cùng một phép so. Đo token/tiếng, phân bố câu, chuỗi ngắn, số dòng phẩy, rào nguồn, duration và nhận xét nghe theo rubric.
- **Chưa thể kết luận thắng từ lint/nghe mẫu.** Sau khi Lead/PO cho đăng theo pipeline hiện có, ghép bài cùng kênh/khuôn/tuổi video/traffic, xem stay, retention30s/60s/120s, AVP và phút xem; ghi khác biệt chủ đề/thumbnail/giờ. Bảng E6 có rewatch nên không so AVP206% với Long như cùng mục tiêu.
- **PO cần chọn trước giao075b:** phạm vi rút câu≤10 trong120s; ranh giới phỏng dựng BUD ngoài truyện kinh; profile miễn ngân sách v2 cho lookup/kinh-ngắn; mục nào chuyển thành LỖI và từ ngày nào. Lead xác nhận cách chuẩn hóa175/185 và nguồn hồ sơ VSD. Không cần ép thống nhất voice, số chương, kiểu mở hay engine.

## D. Lệnh kiểm đã chạy và bằng chứng

### D1. Probe chỉ đọc, không gọi runner render

Chạy từ repo chính bằng `.venv/bin/python -B -` (stdin). `-B` tránh tạo pycache. Đầu vào dưới là fixture trong bộ nhớ để kiểm **hành vi lint**, không phải kịch bản giao sản xuất. Không gọi `hf_batch_render.py --only`, build, TTS, sutta, đăng hay mạng trong probe.

```python
import importlib.util, json
import long_script_lint as L
import hf_batch_render as H
from library.tools import hook_lint as K

s = importlib.util.spec_from_file_location(
    "audit_stier", "creator_v2/motion/stier/script_lint.py")
M = importlib.util.module_from_spec(s)
s.loader.exec_module(M)

def hits(script, codes):
    r = L.lint({"id": "075a_probe", "series": "bud",
                "lane": "long", "script": script})
    return [(level, code) for level, code, _ in r["issues"]
            if code in codes]

line = ("Tuổi Tý gồm những người sinh năm âm lịch "
        "1960, 1972, 1984, 1996 và 2008.")
print("PROBE numeric:", json.dumps({
    "tokens": L.tokens(line), "spoken_estimate": L.syllables(line),
    "timeline_s": round(L.timeline({"script": [line]})[0][-1][1], 3),
    "runner": H.retention_issues({"script": [line]}),
    "cau_dai": hits([line], {"cau_dai"})}, ensure_ascii=False))

comma = ["Tháng mười một âm,", "toàn tháng có hai ngày lễ."]
print("PROBE comma:", json.dumps({
    "long": hits(comma, {"cau_tach_doi"}),
    "short_before": H.short_story_issues({"day": "2026-11-28", "script": comma}),
    "short_after": H.short_story_issues({"day": "2026-11-29", "script": comma})
}, ensure_ascii=False))

shorts = ["Bà đứng lại.", "Ông quay đi.", "Cửa đã khép."]
print("PROBE short_run:", json.dumps({
    "it_cau_ngan": hits(shorts, {"it_cau_ngan"}),
    "runner": H.retention_issues({"script": shorts})}, ensure_ascii=False))

ctas = ["Hãy đăng ký kênh.", "Bấm đăng ký kênh.",
        "Nhấn đăng ký kênh.", "Bật chuông."]
print("PROBE cta:", json.dumps({
    "three": hits(ctas[:3], {"cta_nhieu"}),
    "four": hits(ctas, {"cta_nhieu"})}, ensure_ascii=False))

print("PROBE tone:", json.dumps(H.short_tone_issues({
    "series": "fs", "day": "2026-11-18",
    "title": "Phát tài lớn theo truyền thống", "script": []}),
    ensure_ascii=False))
flags = K.lint_row({"title": "Một điều nhỏ", "script": ["Bạn nghĩ sao?"]},
                   K.load_terms())["flags"]
print("PROBE noun:", json.dumps({
    "flags": flags, "blocking": K.blocking_flags(flags)}, ensure_ascii=False))

sp = {"theme": "mim", "title": "AI năm 2026", "hook_kind": "nghich_ly",
      "lines": ["Vì sao cỗ máy này đã khiến cả nhóm phải quay lại?"],
      "scenes": [{"type": "photo"}]}
for day in ["2026-11-30", "2026-12-01", ""]:
    e, w = M.short_retention(dict(sp, publish_at=day))
    print("PROBE stier:", json.dumps({
        "date": day, "errors": e, "warnings": w}, ensure_ascii=False))

print("PROBE v2_lookup:", json.dumps(H.short_v2_issues({
    "series": "fs", "day": "2026-12-01",
    "script": ["Bạn tra năm sinh ở bảng này."],
    "insight": "Tra theo năm sinh", "novelty_ok": "synthetic audit only"}),
    ensure_ascii=False))
print("PROBE_TOTAL: 8 nhóm kiểm chỉ đọc; không TTS/render/ghi plan")
```

Output thực, exit0:

```text
PROBE numeric: {"tokens": 15, "spoken_estimate": 43, "timeline_s": 4.865, "runner": ["câu ngắn <= 6 tiếng: 0/1 -- nên ~1 câu mỗi 4-6 câu (câu đỉnh, tách dòng)"], "cau_dai": [["LỖI", "cau_dai"]]}
PROBE comma: {"long": [["CẢNH BÁO", "cau_tach_doi"]], "short_before": [], "short_after": ["dòng 1: câu bị tách giữa chừng (kết thúc dấu phẩy) -- gộp với dòng sau, TTS nghỉ sai chỗ nghe cụt"]}
PROBE short_run: {"it_cau_ngan": [], "runner": []}
PROBE cta: {"three": [], "four": [["CẢNH BÁO", "cta_nhieu"]]}
PROBE tone: ["giật gân 'Phát tài lớn' -- không hợp hồn kênh"]
PROBE noun: {"flags": ["KHONG_DANH_TU_CU_THE"], "blocking": []}
PROBE stier: {"date": "2026-11-30", "errors": [], "warnings": ["câu 1: 12 từ (> 9)"]}
PROBE stier: {"date": "2026-12-01", "errors": ["câu 1: 12 từ (> 9)"], "warnings": []}
PROBE stier: {"date": "", "errors": [], "warnings": ["câu 1: 12 từ (> 9)"]}
PROBE v2_lookup: ["7 tiếng -- cần 68-88 (~21-27 giây; < 20 giây không được feed đẩy)"]
PROBE_TOTAL: 8 nhóm kiểm chỉ đọc; không TTS/render/ghi plan
```

Các danh sách rỗng chỉ áp cho finding được chọn ở fixture ấy; **không phải “toàn kịch bản đạt”, preflight đạt hay nghe hay**. Giá trị43 là bộ đếm tiếng đọc ước lượng, không phải thời lượng TTS đo mới. Probe stier chỉ chạy short_retention, còn gate builder khác ở B2/X20.

### D2. Kiểm tài liệu/phạm vi bàn giao

Kiểm bằng Python -B: đếm ID bảng, xác nhận mỗi dẫn chiếu backtick `file.md:dòng` hoặc `file.py:dòng` tồn tại và dòng trong biên, kiểm UTF-8; đọc `git status --short` của worktree và `git diff --name-only` ở repo chính. Đây là kiểm cấu trúc và phạm vi, không xác nhận mọi suy luận nghiên cứu bằng máy.

Báo cáo cuối ghi đúng output lần kiểm cuối. Không commit/push, không thay skill/code/kiểm độc lập, không render, không thay kênh/lịch/video. File nghiên cứu chỉ nằm trong worktree; báo cáo tóm tắt nằm repo chính.

### D3. Điều còn chưa chắc / cần Lead quyết

- Chưa có thử nghe/retention mới cho bất kỳ prompt ngoài; không khẳng định một repo “thắng” dựa trên sao hoặc bộ tự chấm.
- 175/185 và các rate3,3/4,2 khác phép đếm/giọng/nghỉ; cần hiệu chuẩn có cấu hình và manifest cùng phiên bản.
- Báo cáo67/83/071 là tài liệu đã có; không chạy lại TTS hay kéo lại analytics. Giữ nguyên giới hạn mà tác giả đã nêu.
- Ranh giới BUD ngoài kinh/phỏng dựng, VSD chưa đủ hồ sơ riêng, miễn v2 theo khuôn và mức chặn phải được Lead trình PO qua bảng C trước075b.
- Bản này chỉ đề xuất hợp nhất có phần riêng; chưa tạo `docs/script/audio-script.md`, chưa sửa writer brief hoặc cổng nào.


Kết quả kiểm tài liệu lần cuối (lệnh Python -B mô tả ở D2, exit0):

```text
LOCAL_REFS: 290 dẫn chiếu, lỗi 0
INVENTORY: 129 dòng luật, 129 ID duy nhất
EXTERNAL_REPOS: 10 metadata rows
CONFLICTS: 20 rows
MARKDOWN_TABLES: lỗi số cột 0
PYTHON_RECEIPT: cú pháp hợp lệ
UTF8: OK
MAIN_TRACKED_DIFF: (rỗng)
WT_STATUS: ?? docs/research/2026-11-17-audio-script-research.md
DOC_CHECK: ĐẠT cấu trúc/dẫn chiếu/phạm vi; không phải QA video
```



