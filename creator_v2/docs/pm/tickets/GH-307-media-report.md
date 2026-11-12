# GH-307 — báo cáo gắn tư liệu minh họa

**Chưa đạt cổng bàn giao toàn bài.** Đã hoàn thành phần gắn nền trong phạm vi ticket và qua `floor.measure` / `floor.problems`; `long_gate` vẫn TRƯỢT vì thiếu TTS và trường YouTube, là các việc ticket giao Lead. `cadence` còn cảnh báo ước lượng ở CH00; chưa có timing thật để kết luận.

- Trước: 0 cảnh b-roll, 45 khóa ảnh, 49,38% chữ nền trống; sau: 31 cảnh b-roll, 84 khóa ảnh, 0,21% chữ nền trống, 35,63% kinetic, 14 loại cảnh, 480 cảnh, 5.814 âm tiết; `problems()` trả `[]`.
- Giữ các neo và loại cảnh, không chèn cảnh, không thay chân dung/thư pháp, bản đồ, timeline hoặc ledger; thêm `bg` hoặc `vid` cho cảnh chữ. Ảnh AI gắn `credit: false`, `illus: TÁI DỰNG MINH HỌA`, `tags: [minh_hoa_chung]`; clip cùng chú thích và tag. Nguồn thật gắn nhãn tư liệu minh họa. Clip vàng chỉ ở câu về tài sản tịch biên.
- Số lần dùng clip tối đa 5, hai lần cùng clip cách ít nhất một chương; nền ảnh AI tối đa 6, nền ảnh research tối đa 4. Đây là đếm riêng số lần làm nền; số lần dùng ảnh trong mọi vai trò có ở bảng dưới.
- Không thêm dữ kiện hay trích dẫn, không kiểm nguồn mới; tính khớp trực quan thực tế của tư liệu và độ rõ nhãn chưa kiểm được vì ticket cấm render. Chưa có clip sheet hoặc thumbnail mới trong bước này.

## Bảng thay đổi theo chương

Chỉ số cảnh và số câu neo đều tính từ **0** như trong JSON; `cảnh:tư_liệu@câu`. Cảnh có neo từ vẫn giữ nguyên neo từ. Các mục là cảnh chữ được gắn nền, không phải cảnh chèn mới.

| Chương | Cảnh:tư liệu@câu |
|---|---|
| CH00 | 0:v3@0, 1:ai14@1, 5:v8@5, 9:v7@9, 13:ai11@13 |
| CH01 | 0:v1@0, 2:ai17@2, 5:ai01@5, 6:ai08@6, 8:r73@8, 9:r74@9, 12:ai07@13, 14:ai18@15, 15:r82@17, 16:r85@18, 17:r89@19, 18:r90@20, 20:r91@23, 23:r92@26, 24:r93@27, 25:r95@28, 26:r100@29, 27:r103@30, 28:r104@31, 29:r105@32, 30:v4@33, 32:r115@35 |
| CH02 | 1:ai02@2, 3:r48@4, 4:ai05@5, 8:v3@9, 9:ai15@11, 12:ai09@15, 13:r116@16, 14:r117@17, 15:r118@18, 17:paper@20, 18:book@21, 20:book2@23, 21:page@24, 23:writing@27, 24:writing2@29, 25:writing3@30, 28:writing4@33, 29:writing5@35, 31:writing6@37, 34:v8@41, 36:writing7@43, 37:writing8@44 |
| CH03 | 1:ai04@1, 2:r37@2, 9:v7@9, 11:call111@11, 12:call119@13, 13:ai12@14, 14:ai06@15, 16:ai10@17, 17:call120@18, 19:call126@20, 21:v5@22, 25:ai03@26, 26:call127@27, 29:ai14@30, 31:r45@32, 32:ai11@33, 33:ai07@34 |
| CH04 | 2:v1@2, 4:ai02@4, 7:r48@7, 8:ai05@8, 9:ai01@9, 10:r73@10, 11:v8@11, 13:r74@13, 14:r82@14, 16:r85@16, 17:r89@17, 20:ai03@20, 22:r90@22, 24:v2@24, 26:ai06@26, 27:r91@27, 30:r92@30, 31:r93@31, 34:r103@35, 36:r104@37, 37:r105@38 |
| CH05 | 0:ai08@0, 1:v4@1, 7:ai18@7, 9:ai15@9, 12:v7@12, 13:r95@13, 14:r100@13, 15:ai09@14, 16:r115@15, 18:r116@17, 20:r117@19, 21:r118@20, 23:paper@22, 25:book@24, 26:book2@25, 28:page@27, 30:writing@29, 32:writing2@31 |
| CH06 | 2:writing3@1, 3:writing4@2, 8:writing5@7, 11:v6@10, 12:writing6@11, 14:v1@13, 17:writing7@16, 19:writing8@18, 21:call111@20, 22:call119@21, 25:call120@24, 26:v8@25, 28:call126@27, 30:call127@29, 31:ai14@30 |
| CH07 | 4:ai02@2, 5:r48@3, 10:ai11@8, 12:ai07@10, 13:ai01@11, 16:v7@14, 17:r73@15, 19:ai05@18, 21:r74@21, 24:r82@24, 26:r85@26, 27:r89@27, 29:v2@30, 36:r90@37, 38:r91@39, 40:r92@41, 43:r93@44 |
| CH08 | 0:r95@0, 4:ai13@4, 6:ai13@6, 8:ai13@8, 9:r100@9, 11:ai18@11, 12:r103@12, 15:r104@15, 16:r105@16, 19:r115@19, 21:r116@21, 25:r117@25, 28:r118@28, 29:paper@29, 32:book@32, 33:ai03@33, 36:book2@37, 37:page@38 |
| CH09 | 3:writing@3, 4:writing2@4, 7:writing3@7, 8:writing4@8, 9:writing5@9, 13:v1@13, 14:writing6@14, 15:writing7@15, 16:writing8@16, 19:call111@19, 23:call119@23, 25:v4@25, 29:v3@29, 30:call120@30, 31:call126@31 |
| CH10 | 0:v2@0, 2:call127@2, 6:ai14@6, 8:ai15@8, 10:v5@10, 13:ai11@13, 14:ai07@14, 18:ai01@18, 20:v7@20, 21:ai02@21, 22:r48@22, 24:ai09@24, 26:ai15@26, 28:ai09@28, 29:v8@29, 31:ai05@31, 34:ai18@34, 35:r73@35, 37:r74@37, 39:r82@39 |
| CH11 | 1:r85@1, 3:v4@3, 5:r89@5, 8:r90@8, 11:r91@10, 13:ai17@12, 15:ai17@14, 17:ai08@16, 19:ai17@18, 20:ai08@19, 22:r92@21, 24:r93@23 |
| CH12 | 0:r95@0, 2:r100@2, 8:r103@8, 11:r104@11, 16:r105@16, 17:r115@17, 20:v3@20, 22:r116@22, 23:r117@23, 25:r118@25, 27:paper@27, 32:v2@32 |
| CH13 | 0:book@0, 2:book2@2, 4:page@4, 5:writing@5, 9:writing2@9, 10:writing3@10, 13:writing4@13, 14:writing5@14, 15:writing6@15, 17:writing7@17, 20:writing8@20, 21:call111@21, 25:call119@25, 27:v4@27, 29:call120@29, 30:call126@30, 31:call127@31, 32:ai08@32, 35:v5@34, 36:ai11@35, 38:ai18@37, 40:ai17@39 |

## Số lần dùng clip

| Clip | Số cảnh |
|---|---:|
| v1 / 900001 | 4 |
| v2 / 900002 | 4 |
| v3 / 900003 | 4 |
| v4 / 900004 | 5 |
| v5 / 900005 | 3 |
| v6 / 900006 | 1 |
| v7 / 900007 | 5 |
| v8 / 900008 | 5 |

## Số lần dùng ảnh

Tổng tính theo số lần xuất hiện ở các trường `img`, `bg`, `a.img`, `b.img`; cột nền tính riêng `bg`, gồm cả nền cảnh chương có sẵn. Các khóa khác nhau có thể trỏ tới cùng một tệp research.

| Khóa ảnh | Tổng | Làm nền | Nguồn trong spec |
|---|---:|---:|---|
| ai01 | 4 | 4 | EXT:ai:ai_01 |
| ai02 | 4 | 4 | EXT:ai:ai_02 |
| ai03 | 3 | 3 | EXT:ai:ai_03 |
| ai04 | 1 | 1 | EXT:ai:ai_04 |
| ai05 | 4 | 4 | EXT:ai:ai_05 |
| ai06 | 2 | 2 | EXT:ai:ai_06 |
| ai07 | 4 | 4 | EXT:ai:ai_07 |
| ai08 | 5 | 5 | EXT:ai:ai_08 |
| ai09 | 4 | 4 | EXT:ai:ai_09 |
| ai10 | 1 | 1 | EXT:ai:ai_10 |
| ai11 | 5 | 5 | EXT:ai:ai_11 |
| ai12 | 1 | 1 | EXT:ai:ai_12 |
| ai13 | 3 | 3 | EXT:ai:ai_13 |
| ai14 | 4 | 4 | EXT:ai:ai_14 |
| ai15 | 4 | 4 | EXT:ai:ai_15 |
| ai17 | 5 | 5 | EXT:ai:ai_17 |
| ai18 | 5 | 5 | EXT:ai:ai_18 |
| archive66 | 1 | 0 | File:遷都詔.jpg |
| book | 7 | 4 | File:The Complete Library in Four Sections (Siku Quanshu) WDL3020.jpg |
| book2 | 7 | 4 | File:Siku 1.png |
| call106 | 2 | 0 | File:MET 1980 531 O sf.jpg |
| call111 | 7 | 4 | File:刘镛行书杂书二段卷.png |
| call119 | 6 | 4 | File:刘墉 行书苏轼游汤泉诗轴.jpg |
| call120 | 6 | 4 | File:刘墉 行书轴.jpg |
| call126 | 7 | 4 | File:刘墉行书诗卷.png |
| call127 | 7 | 4 | File:刘墉行书录文卷.png |
| cells | 1 | 0 | File:Exam cells-large.jpg |
| city | 1 | 0 | File:万国来朝图 Qianlong in the Forbidden City, Peking in 1761.jpg |
| council | 2 | 0 | File:萬國來朝圖.jpg |
| court | 1 | 0 | File:Entering Suzhou and the Grand Canal11.jpg |
| edict | 1 | 0 | File:Shengyu Guangxun (Amplified Instructions on the Sacred Edict).jpg |
| exam | 1 | 0 | File:Xu Yang - Examination hall.jpg |
| exam2 | 1 | 0 | File:Ming-Beamtenprüfungen1.jpg |
| exam3 | 1 | 0 | File:Viewing the Pass List - attributed to Qiu Ying.jpg |
| exam41 | 1 | 0 | File:Exam cells model.jpg |
| gates | 1 | 0 | File:Along the River 7-119-3.jpg |
| heshen | 3 | 0 | File:Hesen.jpg |
| horse | 1 | 0 | File:The Qianlong Emperor in Ceremonial Armour on Horseback.jpg |
| jia | 1 | 0 | File:清 佚名 《清仁宗嘉庆皇帝朝服像》.jpg |
| land | 1 | 0 | File:Qing Court Artists - The New City of Feng.jpg |
| liu | 3 | 0 | File:Liu Yong.png |
| liu2 | 3 | 0 | File:劉墉人像圖1.jpg |
| liu3 | 3 | 0 | File:劉墉人像圖.jpg |
| official | 1 | 0 | File:Weng Pu Portrait of a young official.jpg |
| page | 4 | 4 | File:状元卷.JPG |
| painting154 | 3 | 1 | File:QingMingShangHeTu Big.jpg |
| painting53 | 1 | 0 | File:Xu Xianqing part11.jpg |
| painting71 | 1 | 0 | File:应元书院图.jpg |
| paper | 6 | 4 | File:Qing Paper of Imperial Exam (9887034294).jpg |
| plate160 | 1 | 0 | File:Qing Dynasty Plate with court scene.jpg |
| qian150 | 1 | 0 | File:Portrait of the Qianlong Emperor in Court Dress.jpg |
| qian151 | 1 | 0 | File:乾隆.jpg |
| qianlong | 1 | 0 | File:Qianlong11.jpg |
| r100 | 4 | 4 | File:Wen Zhengming 文徵明 - Letter - 1998-77 i - Princeton University Art Museum.jpg |
| r103 | 4 | 4 | File:Liu Yong Hongyinshanfang board.JPG |
| r104 | 4 | 4 | File:Liu Yong chengzisizhen board.JPG |
| r105 | 4 | 4 | File:Running script of Liu Yong.jpg |
| r115 | 4 | 4 | File:刘墉临 米芾《珊瑚帖》之一.jpg |
| r116 | 4 | 4 | File:刘墉临 米芾《珊瑚帖》之二.jpg |
| r117 | 4 | 4 | File:劉石菴1.png |
| r118 | 4 | 4 | File:劉石菴2.png |
| r37 | 1 | 1 | File:Prüfungszellen-Nanking.jpg |
| r45 | 1 | 1 | File:Quanzhou Museum - imperial exam winner boards - DSCF8225.JPG |
| r48 | 4 | 4 | File:北京国子监.JPG |
| r73 | 4 | 4 | File:The Calligraphy Model Mid-Autumn by Wang Xianzhi.jpg |
| r74 | 4 | 4 | File:The Calligraphy Model Boyuan by Wang Xun.jpg |
| r82 | 4 | 4 | File:KaishuOuyangxun.jpg |
| r85 | 4 | 4 | File:LantingXu.jpg |
| r89 | 4 | 4 | File:Wang Xizhi Huang Ting Jing.jpg |
| r90 | 4 | 4 | File:Wang Xizhi Shang Yu Tie.jpg |
| r91 | 4 | 4 | File:This Letter written by Mi Fei.jpg |
| r92 | 4 | 4 | File:Wang Xianzhi Imitation by Tang Dynasty.jpg |
| r93 | 4 | 4 | File:Mi Fu-On Calligraphy.jpg |
| r95 | 4 | 4 | File:The Calligraphy Model Sunny after Snow by Wang Xizhi.jpg |
| robe | 1 | 0 | File:Man's semi-formal court robe (jifu) - Google Art Project.jpg |
| rooms | 1 | 0 | File:Xu Xianqing part05.jpg |
| writing | 5 | 4 | File:刘墉各家手札卷.png |
| writing2 | 6 | 4 | File:刘墉行书论书法轴.png |
| writing3 | 6 | 4 | File:刘墉行书蔡明远叙轴.png |
| writing4 | 6 | 4 | File:刘墉行书自书诗卷.png |
| writing5 | 6 | 4 | File:刘墉行书题画轴.png |
| writing6 | 6 | 4 | File:刘墉行书录文、楷书濂溪诗并序两段卷.png |
| writing7 | 6 | 4 | File:刘墉行书临米帖轴.png |
| writing8 | 6 | 4 | File:刘墉行草书临帖录诗文轴.png |
| ai16 | 0 | 0 | EXT:ai:ai_16 |

## Kiểm tra

1. `python data/long/cl-luu-gu/gen_scenes.py`: thành công, sinh CH00–CH13 và spec qua `write`.
2. `python motion/long/floor.py cl-luu-gu`: CLI không in gì. Gọi `measure` / `problems` trực tiếp cho kết quả nêu trên và không còn lỗi sàn.
3. `PYTHONIOENCODING=utf-8 python motion/variety.py audit cl-luu-gu`: OK, đủ khác các video gần đây.
4. `python motion/long/cadence.py cl-luu-gu`: **CẢNH BÁO** tổng; CH00 `map` #12 dài tối đa 14,31 giây theo ước lượng 150 giây/chương. Các chương khác không cảnh báo. Chưa có TTS/timing nên chỉ là ước lượng, Lead cần kiểm lại nhịp sau TTS.
5. `python motion/long/scene_params.py cl-luu-gu`: không có lỗi hoặc cảnh báo, nhưng `planned_chapters: 0`, chưa kiểm được cảnh đã plan và thời lượng thật.
6. `python scripts/long_gate.py cl-luu-gu --min-syl 1900`: **TRƯỢT, 2 lỗi**: thiếu TTS CH00–CH13; `spec.youtube` thiếu `publish_at`, `playlist`, `video_credits`. Ticket cấm chạy TTS và giao metadata cho Lead, do đó không thể đạt cổng trong phạm vi được phép. Báo cáo số cảnh 479 của gate khác 480 của floor do cách đếm khác nhau.

Không render, không TTS, không commit, không đăng; không tạo hay tải thêm tư liệu.

Kiểm bổ sung: các tệp ảnh AI và clip được tham chiếu đều tồn tại; nhãn và tag hiện diện trong JSON; số lần dùng nền research tính theo tên tệp không vượt 4. `rg` không thấy chuỗi ba dấu hỏi hoặc ký tự thay thế trong các file cảnh và báo cáo. Đây là kiểm dữ liệu, không thay thế việc xem khung hình sau dựng.
