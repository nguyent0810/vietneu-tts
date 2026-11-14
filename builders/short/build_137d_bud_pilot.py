"""137d_bud_list_pilot_build: Pilot thăm dò BUD Micro-Documentary Sóng A (16-19/11).
4 cặp (8 bài: 4 Micro-Documentary + 4 Đối chứng).

    .venv/bin/python output/cl_staging/grok/build_137d_bud_pilot.py [--html-only] [--only=id1,id2]
"""
from __future__ import annotations
from shortbuild import validate

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "output/cl_staging/long"))

import build_bud_1023r as B   # noqa: E402
import build_r1024 as R4      # noqa: E402
import build_r1025 as R5      # noqa: E402
import build_r1026 as R6      # noqa: E402
import hf_music               # noqa: E402

D = B.D
OUT = HERE / "render_137d"
PLAN = ROOT / "output/cl_staging/bud/plan_137d_bud_pilot.json"
PACKAGING_DIR = ROOT / "output/cl_staging/bud/packaging"
COMMONS = ROOT / "chunks_cache/commons"
MUSEUM = ROOT / "chunks_cache/museum"
GROKBOT_LIB = ROOT / "output/cl_staging/grokbot/lib48_lo2/out"

HOLD = 2.0
VOICE_DELAY = 0.5
SUT = "https://suttacentral.net"
BATCH_ID = "bud_pilot137"

# ------------------------------------------------------------------ 8 BÀI SÓNG A (16-19/11)
ITEMS = [
    # CẶP 1 (19:30): A1 (16/11 19:30) vs K2 (17/11 19:30) -> pair_w47_1930_1 [cùng tranh_bich_hoa]
    dict(
        id="bud137d_a1", day="2026-11-16", slot="19:30", lane="tuong", arm="md", formula="M1",
        pair_id="pair_w47_1930_1", img_kind="tranh_bich_hoa",
        hypothesis="Micro-Documentary: nhịp cắt theo câu + hình động từng mục (số thứ tự + chữ khoá) tăng stay & engagement",
        title="Năm vị đệ tử kinh nêu trước hết", chip="NĂM VỊ ĐỆ TỬ BẬC NHẤT", srcline="TĂNG CHI 1.188–192",
        head='NĂM VỊ ĐỆ TỬ BẬC NHẤT<br><span class="warm">KINH NÊU TRƯỚC HẾT?</span>',
        script=[
            "Năm vị đệ tử kinh nêu trước hết?",
            "Một, Tôn giả Kiều Trần Như, bậc cao hạ nhất.",
            "Hai, Tôn giả Xá Lợi Phất, bậc trí tuệ đệ nhất.",
            "Ba, Tôn giả Mục Kiền Liên, bậc thần thông đệ nhất.",
            "Bốn, Tôn giả Ma Ha Ca Diếp, bậc đầu đà đệ nhất.",
            "Năm, Tôn giả A Nậu Lầu Đà, bậc thiên nhãn đệ nhất.",
            "Bạn từng nghe danh vị Tôn giả nào trong năm vị?"
        ],
        keywords=["KIỀU TRẦN NHƯ", "XÁ LỢI PHẤT", "MỤC KIỀN LIÊN", "MA HA CA DIẾP", "A NẬU LẦU ĐÀ"],
        subtitles=["Bậc cao hạ nhất", "Trí tuệ đệ nhất", "Thần thông đệ nhất", "Đầu đà đệ nhất", "Thiên nhãn đệ nhất"],
        images=[
            COMMONS / "Wat_Phra_Yuen_Phutthabat_Yukhon_5.jpg",
            COMMONS / "077_Sariputra_Maudgalyayana_and_Their_Followers_Ordain.jpg",
            COMMONS / "031_Moggallanas_Passing_and_Devadatta_is_Swallowed_by_the_Earth_34865778390_.jpg",
            COMMONS / "Burma_mid_19th_century_Mahākassapa_paying_homage_to_the_Buddha_s_feet.jpg",
            COMMONS / "Buddhist_painting_from_Ajanta_cave_9_Albert_Hall_Museum_Jaipur.jpg"
        ],
        source=f"Kinh Tăng Chi 1.188–192, bản Bhikkhu Sujato (CC0): {SUT}/an1.188-197/en/sujato — 'The foremost of my monk disciples in long standing is Koṇḍañña Who Understood. ... with great wisdom is Sāriputta. ... with psychic power is Mahāmoggallāna. ... who advocate austerities is Mahākassapa. ... with clairvoyance is Anuruddha.'",
        insight="Kinh Tăng Chi 1.188–192 nêu trước hết 5 vị đệ tử đứng đầu từng hạnh: Tôn giả Kiều Trần Như (cao hạ nhất), Xá Lợi Phất (trí tuệ), Mục Kiền Liên (thần thông), Ma Ha Ca Diếp (đầu đà) và A Nậu Lầu Đà (thiên nhãn).",
        tags=["nam vi de tu", "kieu tran nhu", "xa loi phat", "muc kien lien", "ca diep", "tang chi 1"],
        tags_vi=["năm vị đệ tử", "Kiều Trần Như", "Xá Lợi Phất", "Mục Kiền Liên", "Ca Diếp", "Tăng Chi"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#đệtửphật", "#tăngchi"],
        cta="Trong 5 vị đại đệ tử, bạn ấn tượng sâu sắc nhất với hạnh nguyện của vị Tôn giả nào?"
    ),

    # CẶP 2 (06:00): K1 (16/11 06:00) vs A2 (17/11 06:00) -> pair_w47_0600_1 [cùng tuong]
    dict(
        id="bud137d_k1", day="2026-11-16", slot="06:00", lane="tuong", arm="control", formula="control",
        pair_id="pair_w47_0600_1", img_kind="tuong",
        hypothesis="Kể liền truyền thống + một tượng Ken Burns tĩnh trang nghiêm",
        title="Đức Phật trao y gai cũ cho Ca-diếp", chip="ĐỜI THƯỜNG CỦA ĐỨC PHẬT", srcline="TƯƠNG ƯNG 16.11",
        head='ĐỨC PHẬT TRAO Y GAI CŨ<br><span class="warm">CHO CA DIẾP?</span>',
        script=[
            "Đức Phật trao y gai cũ cho Ca Diếp?",
            "Bên gốc cây, Tôn giả Ca Diếp trải tấm y chắp vá gấp tư mời Đức Phật ngồi.",
            "Ngài khen tấm y mềm, Ca Diếp xin Ngài thương nhận lấy.",
            "Đức Phật hỏi: Ca Diếp, ông có mặc tấm y gai cũ rách của Ta không?",
            "Ca Diếp nhận lời, và hai thầy trò đổi y cho nhau.",
            "Bạn thấy sự giản dị này đáng trân trọng không?"
        ],
        cards=[
            None,
            '<div class="big warm" style="font-size:48px">BÊN GỐC CÂY<br>CA DIẾP TRẢI Y MỜI NGỒI</div>',
            '<div class="big warm" style="font-size:50px">“TẤM Y NÀY MỀM”<br>XIN NGÀI NHẬN LẤY</div>',
            '<div class="big warm" style="font-size:48px">“ÔNG CÓ MẶC<br>Y GAI CŨ CỦA TA?”</div>',
            '<div class="big warm" style="font-size:50px">HAI THẦY TRÒ<br>ĐỔI Y CHO NHAU</div>',
            None
        ],
        image=MUSEUM / "cma_143465.jpg",
        source=f"Kinh Tương Ưng 16.11 (sn16.11:14.1–14.11), bản Bhikkhu Sujato (CC0): {SUT}/sn16.11/en/sujato — '‘In that case, Kassapa, will you wear my worn-out hempen rag robe?’ / and the Buddha presented me with his worn-out hempen rag robe.'",
        insight="Bên gốc cây, Tôn giả Ca Diếp trải y chắp vá mời Đức Phật ngồi; Ngài khen y mềm, Ca Diếp xin dâng, và Ngài trao lại tấm y gai cũ rách của mình: hai thầy trò đổi y cho nhau (Kinh Tương Ưng 16.11).",
        tags=["duc phat", "ca diep", "y gai cu", "tuong ung 16", "doi thuong duc phat"],
        tags_vi=["Đức Phật", "Ca Diếp", "y gai cũ", "Tương Ưng 16", "đời thường Đức Phật"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#đờithườngđứcphật", "#giảndị"],
        cta="Tấm y cũ của Đức Phật trao cho Ca Diếp nhắc chúng ta điều gì về sự buông bỏ vật chất?"
    ),

    dict(
        id="bud137d_a2", day="2026-11-17", slot="06:00", lane="tuong", arm="md", formula="M2",
        pair_id="pair_w47_0600_1", img_kind="tuong",
        hypothesis="Micro-Documentary: nhịp cắt theo câu + hình động từng mục (số thứ tự + chữ khoá) tăng stay & engagement",
        title="Bốn vị Phật đã ra đời trong hiền kiếp", chip="BỐN VỊ PHẬT HIỀN KIẾP", srcline="TRƯỜNG BỘ 14",
        head='BỐN VỊ PHẬT ĐÃ RA ĐỜI<br><span class="warm">TRONG HIỀN KIẾP?</span>',
        script=[
            "Bốn vị Phật đã ra đời trong hiền kiếp?",
            "Một, Đức Phật Câu Lưu Tôn đã xuất hiện ở đời, bậc Chánh Đẳng Giác.",
            "Hai, Đức Phật Câu Na Hàm Mâu Ni đã xuất hiện ở đời, bậc Chánh Đẳng Giác.",
            "Ba, Đức Phật Ca Diếp đã xuất hiện ở đời, bậc Chánh Đẳng Giác.",
            "Bốn, Đức Phật Thích Ca Mâu Ni nay xuất hiện ở đời, bậc Chánh Đẳng Giác.",
            "Bạn có nhớ hồng danh của bốn vị Phật này?"
        ],
        keywords=["CÂU LƯU TÔN", "CÂU NA HÀM MÂU NI", "PHẬT CA DIẾP", "THÍCH CA MÂU NI"],
        subtitles=["Vị Phật thứ nhất", "Vị Phật thứ hai", "Vị Phật thứ ba", "Vị Phật hiện tại"],
        images=[
            COMMONS / "Standing_Buddha_Gandhara_1st_century_AD_schist_-_Ethnological_Museum_Berlin_-_DSC01658.jpg",
            MUSEUM / "cma_161215.jpg",
            COMMONS / "Borobudur_-_Buddha_Statue_-_041_Vitarka_Mudra_11678522145_.jpg",
            COMMONS / "Seated_Buddha_British_Museum_1.jpg"
        ],
        source=f"Kinh Trường Bộ 14 (dn14:1.4.4–1.4.7), bản Bhikkhu Sujato (CC0): {SUT}/dn14/en/sujato — 'In the present fortunate eon, the Buddhas Kakusandha, Koṇāgamana, and Kassapa arose in the world, perfected and fully awakened. And I have arisen now in the world, perfected and fully awakened.'",
        insight="Trong hiền kiếp (Bhadrakalpa), Kinh Trường Bộ 14 ghi nhận đã có 4 vị Phật xuất hiện ở đời: Phật Câu Lưu Tôn, Phật Câu Na Hàm Mâu Ni, Phật Ca Diếp và Đức Phật Thích Ca Mâu Ni hiện tại.",
        tags=["bon vi phat", "hien kiep", "cau luu ton", "cau na ham", "thich ca", "truong bo 14"],
        tags_vi=["bốn vị Phật", "hiền kiếp", "Câu Lưu Tôn", "Câu Na Hàm", "Thích Ca", "Trường Bộ 14"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#hiềnkiếp", "#đứcphật"],
        cta="Bạn đã từng chiêm bái hoặc nghe danh bốn vị Phật của hiền kiếp chưa?"
    ),

    dict(
        id="bud137d_k2", day="2026-11-17", slot="19:30", lane="tuong", arm="control", formula="control",
        pair_id="pair_w47_1930_1", img_kind="tranh_bich_hoa",
        hypothesis="Kể liền truyền thống + một tượng Ken Burns tĩnh trang nghiêm",
        title="Đức Phật cạo tóc và khoác y màu hoàng thổ", chip="ĐỜI THƯỜNG CỦA ĐỨC PHẬT", srcline="TRUNG BỘ 36",
        head='CẠO TÓC XUẤT GIA,<br><span class="warm">KHOÁC Y HOÀNG THỔ?</span>',
        script=[
            "Đức Phật cạo tóc và khoác y hoàng thổ?",
            "Kinh Trung Bộ kể, khi tóc còn xanh đen và đang tuổi thanh xuân tràn đầy sức sống.",
            "Dù cha mẹ không muốn, khóc đẫm nước mắt, Ngài vẫn ra đi.",
            "Ngài tự tay cạo bỏ râu tóc, khoác lên mình tấm y màu hoàng thổ.",
            "Ngài rời đời sống gia đình, bước vào đời sống không nhà.",
            "Dũng khí buông bỏ ấy, nghìn năm sau vẫn làm lay động lòng người."
        ],
        cards=[
            None,
            '<div class="big warm" style="font-size:48px">KHI TÓC CÒN XANH ĐEN<br>TUỔI TRẺ TRÀN SỨC SỐNG</div>',
            '<div class="big warm" style="font-size:48px">DÙ CHA MẸ LỆ RƠI<br>QUYẾT CHÍ XUẤT GIA</div>',
            '<div class="big warm" style="font-size:48px">TỰ TAY CẠO RÂU TÓC<br>KHOÁC Y HOÀNG THỔ</div>',
            '<div class="big warm" style="font-size:50px">RỜI ĐỜI SỐNG GIA ĐÌNH<br>SỐNG KHÔNG NHÀ</div>',
            None
        ],
        image=COMMONS / "Sakyamuni_cuts_his_hair_Tang_Dynasty.jpg",
        source=f"Kinh Trung Bộ 36 (mn36:13.1), bản Bhikkhu Sujato (CC0): {SUT}/mn36/en/sujato — 'Some time later, while still with pristine black hair, blessed with youth, in the prime of life—though my mother and father wished otherwise, weeping with tearful faces—I shaved off my hair and beard, dressed in ocher robes, and went forth from the lay life to homelessness.'",
        insight="Kinh Trung Bộ 36 ghi lại khoảnh khắc xuất gia của Thái tử Tất Đạt Đa: giữa tuổi thanh xuân rực rỡ, Ngài tự cạo bỏ râu tóc, khoác áo màu hoàng thổ dấn thân vào con đường giải thoát.",
        tags=["xuat gia", "cao toc", "y hoang tho", "thai tu tat dat da", "trung bo 36"],
        tags_vi=["xuất gia", "cạo tóc", "y hoàng thổ", "Thái tử Tất Đạt Đa", "Trung Bộ 36"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#xuấtgia", "#buôngbỏ"],
        cta="Dũng khí buông bỏ mọi danh vọng phú quý của Đức Phật truyền cảm hứng gì cho bạn?"
    ),

    # CẶP 3 (06:00): K3 (18/11 06:00) vs P1 (19/11 06:00) -> pair_w47_0600_2 [cùng tranh_bich_hoa]
    dict(
        id="bud137d_k3", day="2026-11-18", slot="06:00", lane="tuong", arm="control", formula="control",
        pair_id="pair_w47_0600_2", img_kind="tranh_bich_hoa",
        hypothesis="Kể liền truyền thống + một tượng Ken Burns tĩnh trang nghiêm",
        title="Bát Đức Phật rời làng vẫn sạch như lúc vào", chip="ĐỜI THƯỜNG CỦA ĐỨC PHẬT", srcline="TƯƠNG ƯNG 4.18",
        head='BÁT ĐỨC PHẬT RỜI LÀNG<br><span class="warm">VẪN SẠCH NHƯ LÚC VÀO?</span>',
        script=[
            "Vì sao bát Phật rời làng vẫn sạch?",
            "Kinh Tương Ưng kể, một buổi sáng Đức Phật vào một làng Bà La Môn khất thực.",
            "Ma vương ám vào dân làng: đừng để sa môn Gotama nhận được gì.",
            "Đức Phật rời làng, bình bát vẫn sạch như lúc bước vào.",
            "Ma vương đến hỏi, Ngài quở Ma, rồi nói kệ: chúng ta không có gì, vẫn sống an vui, lấy hỷ làm thức ăn.",
            "Trong tay không có gì, bạn có giữ được an vui?"
        ],
        cards=[
            None,
            '<div class="big warm" style="font-size:48px">MỘT SÁNG ÔM BÁT<br>VÀO LÀNG KHẤT THỰC</div>',
            '<div class="big warm" style="font-size:48px">MA VƯƠNG ÁM DÂN LÀNG<br>“ĐỪNG ĐỂ ÔNG ẤY CÓ GÌ”</div>',
            '<div class="big warm" style="font-size:48px">RỜI LÀNG<br>BÁT VẪN SẠCH</div>',
            '<div class="big warm" style="font-size:48px">“KHÔNG CÓ GÌ<br>LẤY HỶ LÀM THỨC ĂN”</div>',
            None
        ],
        image=COMMONS / "022_Buddha_on_Alms_Round_30663640826_.jpg",
        source=f"Kinh Tương Ưng 4.18 (sn4.18:1.4–2.1, 2.3, 4.1–4.4), bản Bhikkhu Sujato (CC0): {SUT}/sn4.18/en/sujato — 'Now at that time Māra had possessed the brahmins and householders of Pañcasālā, so that they thought, “Don’t let the ascetic Gotama get any alms!” ... Then the Buddha left the village with his bowl as clean-washed as it was when he entered for alms. ... “Well, ascetic, did you get any alms?” ... “Let us live so very happily ... We shall feed on rapture, like the gods of sublime luminosity.”'",
        insight="Kinh Tương Ưng 4.18 kể: Ma vương ám vào dân làng Pañcasālā để Đức Phật không nhận được gì; Ngài rời làng với bình bát sạch như lúc vào, Ma vương đến hỏi, Ngài quở Ma rồi nói kệ: chúng ta không có gì vẫn sống an vui, lấy hỷ làm thức ăn như chư thiên Quang Âm.",
        tags=["khat thuc", "bat sach", "ma vuong", "tuong ung 4", "doi thuong duc phat"],
        tags_vi=["khất thực", "bát sạch", "Ma vương", "Tương Ưng 4", "đời thường Đức Phật"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#khấtthực", "#bìnhthản"],
        cta="Khi trao đi lòng tốt mà nhận lại sự thờ ơ, bạn có giữ được tâm bình thản như Phật không?"
    ),

    # CẶP 4 (19:30): A3 (18/11 19:30) vs K4 (19/11 19:30) -> pair_w47_1930_2 [cùng tuong]
    dict(
        id="bud137d_a3", day="2026-11-18", slot="19:30", lane="tuong", arm="md", formula="M3",
        pair_id="pair_w47_1930_2", img_kind="tuong",
        hypothesis="Micro-Documentary: nhịp cắt theo câu + hình động từng mục (số thứ tự + chữ khoá) tăng stay & engagement",
        title="Kinh kể nhiều vị đệ nhất, không chỉ một nhóm mười", chip="CÁC BẬC ĐỆ NHẤT TRONG KINH", srcline="TĂNG CHI 1.193–197",
        head='CÁC BẬC ĐỆ NHẤT TRONG KINH<br><span class="warm">KHÔNG CHỈ NHÓM MƯỜI?</span>',
        script=[
            "Ai là các bậc đệ nhất trong kinh?",
            "Một, Tôn giả Bạt Đề, xuất thân dòng dõi cao quý.",
            "Hai, Tôn giả Bạt Đề lùn, có giọng nói hay nhất.",
            "Ba, Tôn giả Bà Ra Đọa Xà, rống tiếng rống sư tử.",
            "Bốn, Tôn giả Phú Lâu Na, thuyết pháp đệ nhất.",
            "Năm, ngài Ca Chiên Diên, giảng rộng nghĩa một lời dạy ngắn.",
            "Bạn có biết thêm vị đệ tử xuất chúng nào?"
        ],
        keywords=["BẠT ĐỀ DÒNG DÕI", "BẠT ĐỀ LÙN", "BÀ RA ĐỌA XÀ", "PHÚ LÂU NA", "CA CHIÊN DIÊN"],
        subtitles=["Dòng dõi cao quý", "Giọng nói hay nhất", "Tiếng rống sư tử", "Thuyết pháp đệ nhất", "Giảng rộng lời ngắn"],
        images=[
            MUSEUM / "cma_153384.jpg",
            COMMONS / "Arhat_assis_Tamrabhadra.jpg",
            COMMONS / "遼_三彩羅漢像-Arhat_Luohan_MET_DP163962.jpg",
            COMMONS / "Seated_luohan_holding_a_rosary_MET_DP164000.jpg",
            MUSEUM / "cma_140198.jpg"
        ],
        source=f"Kinh Tăng Chi 1.193–197, bản Bhikkhu Sujato (CC0): {SUT}/an1.188-197/en/sujato — 'The foremost of my monk disciples ... from eminent families is Bhaddiya son of Kāḷīgodhā. ... with a charming voice is Bhaddiya the Dwarf. ... who roar their lion’s roar is Bhāradvāja the Alms-Gatherer. ... who speak on the teaching is Puṇṇa son of Mantāṇī. ... who explain a brief statement in detail is Mahākaccāna.'",
        insight="Kinh Tăng Chi 1.193–197 ghi nhận rất nhiều vị đệ nhất ngoài mười vị phổ biến: Bạt Đề dòng dõi, Bạt Đề lùn (giọng hay), Bà Ra Đọa Xà (rống tiếng sư tử), Phú Lâu Na (thuyết pháp) và Ca Chiên Diên (giảng rộng nghĩa một lời dạy ngắn).",
        tags=["cac vi de nhat", "bat de", "phu lau na", "ca chien dien", "tang chi 1"],
        tags_vi=["các vị đệ nhất", "Bạt Đề", "Phú Lâu Na", "Ca Chiên Diên", "Tăng Chi 1"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#đệtửphật", "#tăngchi1"],
        cta="Bạn đã từng nghe câu chuyện về vị Tôn giả có giọng nói hay nhất, Bạt Đề Lùn, chưa?"
    ),

    dict(
        id="bud137d_p1", day="2026-11-19", slot="06:00", lane="tuong", arm="md", formula="M4",
        pair_id="pair_w47_0600_2", img_kind="tranh_bich_hoa",
        hypothesis="Micro-Documentary: nhịp cắt theo câu + hình động từng mục (số thứ tự + chữ khoá) tăng stay & engagement",
        title="Kinh nêu năm ni cô đứng đầu", chip="NĂM VỊ NI CÔ ĐỨNG ĐẦU", srcline="TĂNG CHI 1.235–239",
        head='NĂM VỊ NI CÔ ĐỨNG ĐẦU<br><span class="warm">KINH NÊU TRƯỚC HẾT?</span>',
        script=[
            "Kinh nêu năm ni cô đứng đầu?",
            "Một, Ni sư Ma Ha Ba Xà Ba Đề, bậc cao hạ nhất.",
            "Hai, Ni sư Khê Ma, bậc trí tuệ đệ nhất.",
            "Ba, Ni sư Liên Hoa Sắc, bậc thần thông đệ nhất.",
            "Bốn, Ni sư Ba Ta Ca Ra, bậc thông thuộc giới luật.",
            "Năm, Ni sư Pháp Thí, bậc thuyết pháp đệ nhất.",
            "Bạn đã từng nghe câu chuyện của vị ni sư nào?"
        ],
        keywords=["BA XÀ BA ĐỀ", "KHÊ MA", "LIÊN HOA SẮC", "BA TA CA RA", "PHÁP THÍ"],
        subtitles=["Bậc cao hạ nhất", "Trí tuệ đệ nhất", "Thần thông đệ nhất", "Thuộc làu giới luật", "Thuyết pháp đệ nhất"],
        images=[
            COMMONS / "001_Mahapajapati_Gotami_13574237615_.jpg",
            COMMONS / "132_Queen_Khema_Sees_a_Woman_Age_and_Die.jpg",
            COMMONS / "016_Meditating_Bhikkhuni_9179357225_.jpg",
            COMMONS / "021_Meditating_Bhikkhuni_9179326979_.jpg",
            COMMONS / "005_Dhammadinna_13574219473_.jpg"
        ],
        source=f"Kinh Tăng Chi 1.235–239, bản Bhikkhu Sujato (CC0): {SUT}/an1.235-247/en/sujato — '“The foremost of my nun disciples in long standing is Mahāpajāpati Gotamī.” ... “... with great wisdom is Khemā.” ... “... with psychic power is Uppalavaṇṇā.” ... “... who have memorized the monastic law is Paṭācārā.” ... “... who speak on the teaching is Dhammadinnā.”'",
        insight="Kinh Tăng Chi 1.235–239 nêu trước hết 5 vị Tỳ-kheo-ni đứng đầu từng hạnh: Di Mẫu Ba Xà Ba Đề (cao hạ), Khê Ma (trí tuệ), Liên Hoa Sắc (thần thông), Ba Ta Ca Ra (giới luật), Pháp Thí (thuyết pháp).",
        tags=["nam vi ni co", "ba xa ba de", "khe ma", "lien hoa sac", "tang chi 1"],
        tags_vi=["năm vị ni cô", "Ba Xà Ba Đề", "Khê Ma", "Liên Hoa Sắc", "Tăng Chi 1"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#nicô", "#tăngchi"],
        cta="Trong 5 bậc ni cô đệ nhất, cuộc đời của vị ni sư nào khiến bạn xúc động nhất?"
    ),

    dict(
        id="bud137d_k4", day="2026-11-19", slot="19:30", lane="tuong", arm="control", formula="control",
        pair_id="pair_w47_1930_2", img_kind="tuong",
        hypothesis="Kể liền truyền thống + một tượng Ken Burns tĩnh trang nghiêm",
        title="Bảy ngày trong hang Pipphali không nhúc nhích", chip="ĐỜI THƯỜNG CỦA ĐỨC PHẬT", srcline="PHẬT TỰ THUYẾT 3.7",
        head='BẢY NGÀY TRONG HANG ĐÁ<br><span class="warm">KHÔNG NHÚC NHÍCH?</span>',
        script=[
            "Bảy ngày trong hang đá không nhúc nhích?",
            "Kinh Phật Tự Thuyết kể, Tôn giả Ma Ha Ca Diếp trú tại hang Pipphali.",
            "Ngài nhập định sâu, ngồi kiết già suốt bảy ngày đêm không hề cử động.",
            "Xuất định, năm trăm vị trời muốn dâng cúng, ngài đều từ chối.",
            "Ngài vẫn ôm bát vào thành Vương Xá, khất thực như mọi ngày.",
            "Bạn có bao giờ thử ngồi yên lắng lại tâm mình trong vài phút chưa?"
        ],
        cards=[
            None,
            '<div class="big warm" style="font-size:48px">TRÚ TRONG HANG<br>PIPPHALI</div>',
            '<div class="big warm" style="font-size:48px">SUỐT BẢY NGÀY ĐÊM<br>THÂN KHÔNG CỬ ĐỘNG</div>',
            '<div class="big warm" style="font-size:48px">XUẤT ĐỊNH<br>TỪ CHỐI 500 VỊ TRỜI</div>',
            '<div class="big warm" style="font-size:48px">ÔM BÁT VÀO THÀNH<br>KHẤT THỰC NHƯ THƯỜNG</div>',
            None
        ],
        image=COMMONS / "Kasyapa_China_probably_Shanxi_province_Sui_dynasty_581-618_AD_sandstone_with_traces_of_pigments_-_Östasiatiska_museet_St.jpg",
        source=f"Kinh Phật Tự Thuyết 3.7 (ud3.7:1.3–1.6, 2.1), bản Bhikkhu Sujato (CC0): {SUT}/ud3.7/en/sujato — 'Now at that time Venerable Mahākassapa was staying in the Pipphali cave. Having entered a certain state of immersion, he sat cross-legged for seven days without moving. When seven days had passed, Mahākassapa emerged from that state of immersion. ... “Why not enter Rājagaha for almsfood?” ... five hundred deities were ready and eager for the chance to offer alms to Venerable Mahākassapa. But Mahākassapa declined them, and in the morning ... entered Rājagaha for alms.'",
        insight="Kinh Phật Tự Thuyết 3.7 kể: Tôn giả Ma Ha Ca Diếp ngồi thiền kiết già suốt 7 ngày đêm bất động trong hang Pipphali, xuất định thì từ chối năm trăm vị trời muốn dâng cúng, rồi ôm bát vào thành Vương Xá khất thực như thường.",
        tags=["hang pipphali", "ca diep", "nhap dinh 7 ngay", "phat tu thuyet 3", "doi thuong duc phat"],
        tags_vi=["hang Pipphali", "Ca Diếp", "nhập định 7 ngày", "Phật Tự Thuyết 3", "đời thường Đức Phật"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#thiềnđịnh", "#nhậpđịnh"],
        cta="Bạn đã bao giờ dành ra vài phút mỗi ngày ngồi tĩnh lặng để làm lắng dịu tâm trí chưa?"
    ),
]

for it in ITEMS:
    it["series"] = "bud"
    it["batch_id"] = BATCH_ID

# BGM assignment
BGM_MAP = {
    "bud137d_a1": "garden_music.mp3",
    "bud137d_k1": "peace_of_mind.mp3",
    "bud137d_a2": "white_lotus.mp3",
    "bud137d_k2": "that_zen_moment.mp3",
    "bud137d_k3": "wood_and_metal_and_water.mp3",
    "bud137d_a3": "garden_music.mp3",
    "bud137d_p1": "ripples.mp3",
    "bud137d_k4": "parting_of_the_ways_part_1.mp3",
}
for m in (R4, R5, R6):
    m.BGM.update(BGM_MAP)


# ------------------------------------------------------------------ IMAGE HELPER
def crop_to_vertical(im_path: Path) -> Image.Image:
    im = Image.open(im_path).convert("RGB")
    k = 1920 / im.height
    w_new = round(im.width * k)
    if w_new < 1080:
        k = 1080 / im.width
        im_res = im.resize((1080, round(im.height * k)), Image.Resampling.LANCZOS)
        top = max(0, (im_res.height - 1920) // 2)
        im_crop = im_res.crop((0, top, 1080, top + 1920))
    else:
        im_res = im.resize((w_new, 1920), Image.Resampling.LANCZOS)
        left = max(0, (w_new - 1080) // 2)
        im_crop = im_res.crop((left, 0, left + 1080, 1920))

    mean_val = np.array(im_crop).mean()
    if mean_val < 70:
        factor = min(1.35, 90.0 / max(1.0, mean_val))
        return ImageEnhance.Brightness(im_crop).enhance(factor)
    elif mean_val < 90:
        return ImageEnhance.Brightness(im_crop).enhance(1.10)
    return im_crop


# ------------------------------------------------------------------ HTML BUILDERS
def build_html_control(it: dict, t: list[float], dur: float) -> str:
    """Đối chứng: Kể liền 1 cảnh, 1 tượng Ken Burns xuyên suốt 22-27s."""
    im = crop_to_vertical(it["image"])
    cards = it["cards"]
    card_html = "".join(f'<div class="card" id="c{i}">{c}</div>' for i, c in enumerate(cards) if c)
    shown = [i for i, c in enumerate(cards) if c]
    js = []
    for i in shown:
        nxt = next((j for j in range(i + 1, len(cards)) if cards[j]), None)
        nxt = nxt if nxt is not None else len(t) - 1
        js.append(f'tl.fromTo("#c{i}", {{opacity: 0, y: 26}}, {{opacity: 1, y: 0, duration: 0.6, ease: "expo.out"}}, T[{i}]);')
        js.append(f'tl.to("#c{i}", {{opacity: 0, y: -18, duration: 0.45, ease: "power1.in"}}, T[{nxt}] - 0.45);')

    return f"""<!doctype html><html lang="vi"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" /><title>{it['id']}</title>
<style>{B.font_css()}{B.BASE_CSS}
#root {{ background: #0a0807; }}
#photo {{ left: 0; top: 0; width: 1080px; height: 1920px; z-index: 1; transform-origin: 540px 700px; }}
#photo img {{ width: 100%; height: 100%; display: block; }}
#shade {{ left: 0; top: 0; width: 1080px; height: 1920px; z-index: 2;
  background: linear-gradient(180deg, rgba(10,8,7,0.92) 0px, rgba(10,8,7,0.75) 260px, rgba(10,8,7,0) 450px),
    linear-gradient(0deg, rgba(8,6,5,0.96) 0px, rgba(8,6,5,0.9) 340px, rgba(8,6,5,0.62) 580px, rgba(8,6,5,0) 820px); }}
#chip {{ background: #f2b48a; color: #2b1407; }}
.warm {{ color: #f2b48a; }}
.card {{ top: 1240px; }}
#footer {{ top: 1745px; }}
</style>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.2f}" data-width="1080" data-height="1920">
  <div id="photo" class="abs"><img src="{B.b64(im)}" alt="" /></div>
  <div id="shade" class="abs"></div>
  <div id="header"><div id="chip">{it['chip']}</div><div id="title">{it['head']}</div></div>
  {card_html}
  <div id="footer"><div id="src">{it['srcline']}</div></div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }}); window.__timelines.main = tl;
const T = {json.dumps(t)};
tl.fromTo("#photo", {{scale: 1.0}}, {{scale: 1.05, duration: T[T.length - 1] + 1.5, ease: "none"}}, 0);
{' '.join(js)}
</script></body></html>"""


def build_html_micro(it: dict, t: list[float], dur: float) -> str:
    """Micro-Documentary: Mỗi mục một ảnh, một số thứ tự vào/ra, một chữ khoá động."""
    formula = it["formula"]
    keywords = it["keywords"]
    subtitles = it["subtitles"]
    n_items = len(keywords)

    # Encode all images for this micro piece
    b64_imgs = [B.b64(crop_to_vertical(p)) for p in it["images"]]

    # Build layers for each item
    photos_html = []
    items_html = []
    for i in range(n_items):
        idx = i + 1
        num_str = f"0{idx}"
        kw = keywords[i]
        sub = subtitles[i]
        photos_html.append(f'<div class="photo-layer abs" id="photo_{idx}"><img src="{b64_imgs[i]}" alt="" /></div>')

        # Custom keyword markup per formula
        if formula == "M2":  # text-shimmer with dark protective box for WCAG AA
            kw_block = f'<div class="kw-shimmer" id="kw_{idx}"><div class="shimmer-box">{kw}</div></div>'
        elif formula == "M3":  # window badge
            kw_block = f'<div class="kw-window" id="kw_{idx}"><div class="win-box">{kw}</div></div>'
        elif formula == "M4":  # particle assemble with dark protective box
            kw_block = f'<div class="kw-particle" id="kw_{idx}"><div class="particle-box">{kw}</div></div>'
        else:  # M1 ink bleed reveal
            kw_block = f'<div class="kw-ink" id="kw_{idx}"><div class="ink-box">{kw}</div></div>'

        items_html.append(
            f'<div class="item-card abs" id="item_{idx}">'
            f'  <div class="num-badge num-{formula.lower()}" id="num_{idx}">{num_str}</div>'
            f'  {kw_block}'
            f'  <div class="sub-line" id="sub_{idx}">{sub}</div>'
            f'</div>'
        )

    # Extra CSS per formula
    extra_css = """
.photo-layer { left: 0; top: 0; width: 1080px; height: 1920px; z-index: 1; opacity: 0; transform-origin: 540px 700px; }
.photo-layer img { width: 100%; height: 100%; display: block; }
.item-card { left: 60px; width: 960px; top: 1180px; text-align: center; z-index: 20; }
.num-badge { font-weight: 900; font-size: 62px; color: #f4cf6b; letter-spacing: 0.06em; line-height: 1.1; margin-bottom: 8px; display: inline-block; background: rgba(18, 10, 5, 0.88); padding: 4px 28px; border-radius: 999px; border: 1.5px solid rgba(244, 207, 107, 0.45); box-shadow: 0 4px 18px rgba(0,0,0,0.85); }
.sub-line { font-weight: 700; font-size: 38px; color: #f5f0e6; line-height: 1.25; margin-top: 10px; opacity: 0; text-shadow: 0 3px 14px rgba(0,0,0,0.95); }

/* M1: Ink Bleed Reveal */
.kw-ink { opacity: 0; display: inline-block; }
.ink-box { font-weight: 900; font-size: 56px; line-height: 1.15; color: #fff; background: rgba(35,20,10,0.85); padding: 8px 32px; border-radius: 12px; border: 2px solid rgba(242,180,138,0.6); box-shadow: 0 8px 30px rgba(0,0,0,0.8); }

/* M2: Text Shimmer (dark protective pill for WCAG AA + gold shimmer) */
.kw-shimmer { opacity: 0; display: inline-block; }
.shimmer-box { font-weight: 900; font-size: 54px; line-height: 1.15; color: #ffffff; background: rgba(30,16,8,0.88); padding: 8px 34px; border-radius: 12px; border: 2px solid rgba(254,240,138,0.7); box-shadow: 0 8px 30px rgba(0,0,0,0.85); text-shadow: 0 2px 10px rgba(0,0,0,0.9); }

/* M3: Window Badge */
.kw-window { opacity: 0; display: inline-block; }
.win-box { font-weight: 900; font-size: 54px; line-height: 1.15; color: #fdf6e2; background: linear-gradient(180deg, rgba(45,28,14,0.92) 0%, rgba(20,12,6,0.95) 100%); padding: 10px 36px; border-radius: 16px; border: 2px solid #f2b48a; box-shadow: 0 10px 32px rgba(0,0,0,0.9); }

/* M4: Particle Assemble (transform-only, blur assemble, dark box) */
.kw-particle { opacity: 0; display: inline-block; }
.particle-box { font-weight: 900; font-size: 54px; line-height: 1.15; color: #ffffff; background: rgba(28,16,8,0.88); padding: 8px 34px; border-radius: 12px; border: 2px solid rgba(242,180,138,0.65); box-shadow: 0 8px 30px rgba(0,0,0,0.85); text-shadow: 0 2px 10px rgba(0,0,0,0.9); }
"""

    # Generate GSAP Timelines for each sentence cut
    js = []
    # Initial state
    js.append('tl.set("#photo_1", {opacity: 1});')

    for i in range(n_items):
        idx = i + 1
        s_time = t[idx]
        nxt_time = t[idx + 1] if (idx + 1) < len(t) else dur - 0.2

        # Photo cut with subtle scale
        js.append(f'tl.fromTo("#photo_{idx}", {{opacity: {1 if idx == 1 else 0}, scale: 1.0}}, {{opacity: 1, scale: 1.04, duration: {nxt_time - s_time:.2f}, ease: "none"}}, {s_time});')
        if idx > 1:
            js.append(f'tl.to("#photo_{idx - 1}", {{opacity: 0, duration: 0.35}}, {s_time});')

        # Sub line entrance & exit
        js.append(f'tl.fromTo("#sub_{idx}", {{opacity: 0, y: 15}}, {{opacity: 1, y: 0, duration: 0.4, ease: "power2.out"}}, {s_time + 0.2:.2f});')
        js.append(f'tl.to("#sub_{idx}", {{opacity: 0, duration: 0.3}}, {nxt_time - 0.3:.2f});')

        # Number & Keyword animation per formula
        if formula == "M1":
            # Waterfall entry from below -> ink bleed reveal -> exit up
            js.append(f'tl.fromTo("#num_{idx}", {{opacity: 0, y: 45}}, {{opacity: 1, y: 0, duration: 0.42, ease: "power2.out"}}, {s_time});')
            js.append(f'tl.to("#num_{idx}", {{opacity: 0, y: -25, duration: 0.3, ease: "power1.in"}}, {nxt_time - 0.3:.2f});')
            js.append(f'tl.fromTo("#kw_{idx}", {{opacity: 0, scale: 0.86, filter: "blur(8px)"}}, {{opacity: 1, scale: 1.0, filter: "blur(0px)", duration: 0.58, ease: "power2.out"}}, {s_time + 0.12:.2f});')
            js.append(f'tl.to("#kw_{idx}", {{opacity: 0, y: -40, duration: 0.42, ease: "power2.in"}}, {nxt_time - 0.42:.2f});')

        elif formula == "M2":
            # Counting dynamic scale -> text shimmer pass (pill glow shimmer)
            js.append(f'tl.fromTo("#num_{idx}", {{opacity: 0, scale: 1.6}}, {{opacity: 1, scale: 1.0, duration: 0.38, ease: "back.out(1.8)"}}, {s_time});')
            js.append(f'tl.to("#num_{idx}", {{opacity: 0, duration: 0.25}}, {nxt_time - 0.25:.2f});')
            js.append(f'tl.fromTo("#kw_{idx}", {{opacity: 0, scale: 0.88, y: 18}}, {{opacity: 1, scale: 1.0, y: 0, duration: 0.42, ease: "power2.out"}}, {s_time + 0.1:.2f});')
            js.append(f'tl.fromTo("#kw_{idx} .shimmer-box", {{borderColor: "rgba(254,240,138,0.7)"}}, {{borderColor: "rgba(255,255,255,1)", duration: 0.45, yoyo: true, repeat: 1, ease: "sine.inOut"}}, {s_time + 0.6:.2f});')
            js.append(f'tl.to("#kw_{idx}", {{opacity: 0, duration: 0.3}}, {nxt_time - 0.3:.2f});')

        elif formula == "M3":
            # Hook slam down -> window badge scale swap
            js.append(f'tl.fromTo("#num_{idx}", {{opacity: 0, scale: 2.2, y: -45}}, {{opacity: 1, scale: 1.0, y: 0, duration: 0.35, ease: "power3.out"}}, {s_time});')
            js.append(f'tl.to("#num_{idx}", {{opacity: 0, scale: 0.8, duration: 0.25}}, {nxt_time - 0.25:.2f});')
            js.append(f'tl.fromTo("#kw_{idx}", {{opacity: 0, scale: 0.88}}, {{opacity: 1, scale: 1.0, duration: 0.42, ease: "expo.out"}}, {s_time + 0.15:.2f});')
            js.append(f'tl.to("#kw_{idx}", {{opacity: 0, scale: 1.08, duration: 0.32, ease: "power2.in"}}, {nxt_time - 0.32:.2f});')

        elif formula == "M4":
            # Stamp badge -> particle assemble (transforms + blur only, NO letterSpacing)
            js.append(f'tl.fromTo("#num_{idx}", {{opacity: 0, scale: 1.7, rotate: -6}}, {{opacity: 1, scale: 1.0, rotate: 0, duration: 0.3, ease: "back.out(2.0)"}}, {s_time});')
            js.append(f'tl.to("#num_{idx}", {{opacity: 0, duration: 0.25}}, {nxt_time - 0.25:.2f});')
            js.append(f'tl.fromTo("#kw_{idx}", {{opacity: 0, scale: 0.82, filter: "blur(12px)"}}, {{opacity: 1, scale: 1.0, filter: "blur(0px)", duration: 0.60, ease: "power2.out"}}, {s_time + 0.1:.2f});')
            js.append(f'tl.to("#kw_{idx}", {{opacity: 0, y: -20, duration: 0.3}}, {nxt_time - 0.3:.2f});')

    return f"""<!doctype html><html lang="vi"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" /><title>{it['id']}</title>
<style>{B.font_css()}{B.BASE_CSS}
#root {{ background: #0a0807; }}
#shade {{ left: 0; top: 0; width: 1080px; height: 1920px; z-index: 2;
  background: linear-gradient(180deg, rgba(10,8,7,0.92) 0px, rgba(10,8,7,0.75) 260px, rgba(10,8,7,0) 450px),
    linear-gradient(0deg, rgba(8,6,5,0.96) 0px, rgba(8,6,5,0.9) 340px, rgba(8,6,5,0.62) 580px, rgba(8,6,5,0) 820px); }}
#chip {{ background: #f2b48a; color: #2b1407; }}
.warm {{ color: #f2b48a; }}
#footer {{ top: 1745px; }}
{extra_css}
</style>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.2f}" data-width="1080" data-height="1920">
  {' '.join(photos_html)}
  <div id="shade" class="abs"></div>
  <div id="header"><div id="chip">{it['chip']}</div><div id="title">{it['head']}</div></div>
  {' '.join(items_html)}
  <div id="footer"><div id="src">{it['srcline']}</div></div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }}); window.__timelines.main = tl;
const T = {json.dumps(t)};
{' '.join(js)}
</script></body></html>"""


# ------------------------------------------------------------------ PREVIEW SHEET
def export_preview_sheet() -> Path:
    """Tờ ảnh preview 137d: Khung 0, Khung giữa, Khung cuối 168px (so sánh độ tĩnh và chất lượng)."""
    col_w, col_h = 270, 480
    pad = 16
    hdr_w = 260
    n_rows = len(ITEMS)
    cols = ["Khung 0 (mở đầu)", "Khung giữa (nội dung chính)", "Khung cuối (168px - tĩnh)"]

    total_w = hdr_w + pad + (col_w + pad) * 3
    total_h = pad + (col_h + 36 + pad) * n_rows
    sheet = Image.new("RGB", (total_w, total_h), (20, 18, 16))
    draw = ImageDraw.Draw(sheet)

    for r_idx, it in enumerate(ITEMS):
        rid = it["id"]
        y = pad + r_idx * (col_h + 36 + pad)
        mp4 = OUT / f"{rid}.mp4"

        # Cột header
        header_text = f"{it['id']} ({it['arm'].upper()})\n{it['pair_id']}\n[{it.get('img_kind', '')}]\n{it['day']} {it['slot']}\n{it['title']}\n[{it.get('dur', 0)}s]"
        draw.text((pad, y + 20), header_text, fill=(245, 235, 220))

        frames = []
        # Frame 0
        f0 = OUT / f"_{rid}_f0.jpg"
        if mp4.exists():
            subprocess.run(["ffmpeg", "-y", "-ss", "0.05", "-i", str(mp4), "-vframes", "1", "-q:v", "3", str(f0)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        frames.append(f0 if f0.exists() else None)

        # Mid frame
        fmid = OUT / f"_{rid}_mid.jpg"
        if mp4.exists():
            mid_time = min(12.0, max(2.0, it.get("dur", 25.0) / 2.0))
            subprocess.run(["ffmpeg", "-y", "-ss", f"{mid_time:.2f}", "-i", str(mp4), "-vframes", "1", "-q:v", "3", str(fmid)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        frames.append(fmid if fmid.exists() else None)

        # Last frame
        flast = OUT / f"_{rid}_last.jpg"
        if mp4.exists():
            dur_last = max(0.5, it.get("dur", 25.0) - 0.5)
            subprocess.run(["ffmpeg", "-y", "-ss", f"{dur_last:.2f}", "-i", str(mp4), "-vframes", "1", "-q:v", "3", str(flast)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        frames.append(flast if flast.exists() else None)

        for c_idx, fpath in enumerate(frames):
            x = hdr_w + pad + c_idx * (col_w + pad)
            if fpath and fpath.exists():
                im = Image.open(fpath)
                if c_idx == 2:  # Khung cuối 168px
                    im168 = im.resize((168, round(168 * 1920 / 1080)), Image.Resampling.LANCZOS)
                    im_disp = Image.new("RGB", (col_w, col_h), (12, 10, 8))
                    im_disp.paste(im168, ((col_w - 168) // 2, (col_h - im168.height) // 2))
                    sheet.paste(im_disp, (x, y))
                else:
                    sheet.paste(im.resize((col_w, col_h), Image.Resampling.LANCZOS), (x, y))
            else:
                draw.rectangle([x, y, x + col_w, y + col_h], fill=(35, 30, 25))
                draw.text((x + 20, y + col_h // 2), f"Chưa render\n{cols[c_idx]}", fill=(180, 160, 140))

            draw.text((x + 10, y + col_h + 8), cols[c_idx], fill=(200, 190, 175))

    out_sheet = OUT / "preview_137d.jpg"
    sheet.save(out_sheet, quality=90)
    out_lead = OUT / "preview_lead_1106.jpg"
    sheet.save(out_lead, quality=90)
    out_lead_c = OUT / "preview_lead_1105c.jpg"
    sheet.save(out_lead_c, quality=90)
    print(f"Đã xuất tờ ảnh preview: {out_sheet} và {out_lead}")
    return out_lead


# ------------------------------------------------------------------ PACKAGING
def export_packaging() -> None:
    PACKAGING_DIR.mkdir(parents=True, exist_ok=True)
    for it in ITEMS:
        pkg = {
            "insight": it["insight"],
            "tags": it["tags"],
            "tags_vi": it["tags_vi"],
            "hashtags": it["hashtags"],
            "cta": it["cta"]
        }
        p = PACKAGING_DIR / f"{it['id']}.json"
        # 06/11: giữ khoá Lead thêm (day/slot UTC, style) — chỉ ghi đè trường builder sinh.
        old = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
        p.write_text(json.dumps({**old, **pkg}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Đã xuất 8 file packaging vào {PACKAGING_DIR}")


# ------------------------------------------------------------------ MAIN PIPELINE
def main() -> int:
    html_only = "--html-only" in sys.argv
    only = None
    for idx, a in enumerate(sys.argv):
        if a.startswith("--only="):
            only = a.split("=", 1)[1].split(",")
        elif a == "--only" and idx + 1 < len(sys.argv):
            only = sys.argv[idx + 1].split(",")

    R6.guards(ITEMS)
    jobs = []
    print("=== 1. TTS & HTML GENERATION ===")
    for it in ITEMS:
        rid = it["id"]
        if only and rid not in only:
            continue
        R6.tts(it, (0.35, 0.40))
        fin_json = json.loads((D / f"{rid}_final.json").read_text(encoding="utf-8"))
        it["dur"] = round(fin_json["duration_s"] + VOICE_DELAY + HOLD, 2)
        t = R5.segs(rid, VOICE_DELAY)

        if it["arm"] == "md":
            html_content = build_html_micro(it, t, it["dur"])
        else:
            html_content = build_html_control(it, t, it["dur"])

        comp_name = f"_r_{rid}.html"
        (B.COMP / comp_name).write_text(html_content, encoding="utf-8")
        jobs.append((it, html_content))
        print(f"[{rid}] dur={it['dur']}s câu 0={t[1]-t[0]:.2f}s đã lưu HTML {comp_name}")

    # Cập nhật dur cho các bài không chạy trong lượt này để đảm bảo đủ dữ liệu
    for it in ITEMS:
        rid = it["id"]
        if "dur" not in it:
            fin_file = D / f"{rid}_final.json"
            ren_file = OUT / f"{rid}.render.json"
            if fin_file.exists():
                it["dur"] = round(json.loads(fin_file.read_text(encoding="utf-8"))["duration_s"] + VOICE_DELAY + HOLD, 2)
            elif ren_file.exists():
                it["dur"] = json.loads(ren_file.read_text(encoding="utf-8")).get("duration_s", 25.0)

    # Kiểm tra thời lượng 21-28s (k3 câu 5 dài hơn theo kinh Tương Ưng 4.18)
    all_in_band = all(21.0 <= it["dur"] <= 28.0 for it in ITEMS if "dur" in it)
    print(f"All in 21-28s band: {'ĐẠT' if all_in_band else 'LỖI'} ({[it.get('dur') for it in ITEMS if 'dur' in it]})")
    assert all_in_band, "Có video ngoài dải 21-28s!"

    # Export plan manifest (gộp vào plan có sẵn chứ không ghi đè khi chạy --only)
    clean = {
        "id", "day", "slot", "lane", "arm", "formula", "pair_id", "hypothesis",
        "title", "script", "source", "series", "dur", "batch_id", "img_kind"
    }
    existing_plan = {}
    if PLAN.exists():
        try:
            for p in json.loads(PLAN.read_text(encoding="utf-8")):
                if "id" in p:
                    existing_plan[p["id"]] = p
        except Exception as e:
            print(f"Cảnh báo đọc plan cũ: {e}")

    for it, _ in jobs:
        p = {k: it[k] for k in clean if k in it}
        existing_plan[it["id"]] = p

    # Dựng lại plan đủ 8 bài theo thứ tự ITEMS: a1, k1, a2, k2, k3, a3, p1, k4
    plan = []
    for it in ITEMS:
        rid = it["id"]
        if rid in existing_plan:
            entry = existing_plan[rid]
            for k in clean:
                if k in it:
                    entry[k] = it[k]
            plan.append(entry)
        else:
            p = {k: it[k] for k in clean if k in it}
            plan.append(p)

    validate(plan)
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Đã ghi manifest plan đủ {len(plan)} bài vào {PLAN}")

    export_packaging()

    if html_only:
        print("HTML only mode complete.")
        return 0

    OUT.mkdir(parents=True, exist_ok=True)
    print("=== 2. RENDER VIDEO & AUDIO MIX ===")
    for it, _ in jobs:
        rid = it["id"]
        if only and rid not in only:
            continue

        comp_name = f"_r_{rid}.html"
        silent = D / f"{rid}_silent.mp4"
        mp4 = OUT / f"{rid}.mp4"
        B.to_trash(silent)
        B.to_trash(mp4)

        print(f"[{rid}] render silent mp4 ({comp_name}) ...", flush=True)
        R4.render(comp_name, silent)
        print(f"[{rid}] mix audio ...", flush=True)
        vl, gain, ml = R4.mix(rid, silent, D / f"{rid}_final.wav", mp4, it["dur"], VOICE_DELAY, True)
        B.to_trash(silent)

        media_credits = [{"id": rid, "source": it["source"]}]
        if rid == "bud137d_a2":
            media_credits.append({
                "role": "Mục 2 (Đức Phật Câu Na Hàm Mâu Ni)",
                "title": "Ayutthaya Seated Bronze Buddha",
                "period_place": "15th-16th century, Ayutthaya kingdom, Thailand",
                "source": "Cleveland Museum of Art (1970.63)",
                "license": "CC0 1.0 Universal",
                "file": "cma_161215.jpg",
                "statues_bank_id": "statue_sea_03"
            })
        elif rid == "bud137d_a3":
            media_credits.append({
                "role": "Mục 1 / Khung mở đầu",
                "title": "Early Heian Wood Shakyamuni",
                "period_place": "9th century, Heian period, Japan",
                "source": "Cleveland Museum of Art (1985.17)",
                "license": "CC0 1.0 Universal",
                "file": "cma_153384.jpg",
                "statues_bank_id": "statue_japan_02"
            })
            media_credits.append({
                "role": "Mục 5 (Tôn giả Ca Chiên Diên) / Khung cuối",
                "title": "Lohan (Arhat) Holding a Peach",
                "period_place": "1662–1722, Qing dynasty, China",
                "source": "Cleveland Museum of Art (1964.191.1)",
                "license": "CC0 1.0 Universal",
                "file": "cma_140198.jpg"
            })

        meta = {
            "ok": True, "output": str(mp4.relative_to(ROOT)), "duration_s": it["dur"],
            "arm": it["arm"], "formula": it["formula"], "pair_id": it["pair_id"],
            "batch_id": it["batch_id"], "lane": it["lane"],
            "bgm": f"bgm/{BGM_MAP[rid]}", "bgm_title": hf_music.TITLES[BGM_MAP[rid]], "bgm_gain": round(gain, 4),
            "media_credits": media_credits,
            "voice": "Binh", "lufs": {"voice": round(vl, 1), "mix": round(ml, 1), "offset_db": -20.0},
            "sfx_credit": B.BELL_CREDIT
        }
        (OUT / f"{rid}.render.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{rid}] Xong | LUFS giọng {vl:.1f} mix {ml:.1f}", flush=True)

    print("=== 3. CONTACT SHEET PREVIEW ===")
    export_preview_sheet()
    return 0


if __name__ == "__main__":
    sys.exit(main())
