"""137e_bud_pilot_waveB: Pilot thăm dò BUD Micro-Documentary Sóng B (20-27/11).
8 cặp (16 bài: 8 Micro-Documentary + 8 Đối chứng).

    .venv/bin/python output/cl_staging/grok/build_137e_bud_pilot.py [--html-only] [--only=id1,id2]
"""
from __future__ import annotations
from shortbuild import validate

import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

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
OUT = HERE / "render_137e"
BUD_OUT = ROOT / "output/cl_staging/bud/out"
PLAN = ROOT / "output/cl_staging/bud/plan_137e_bud_pilot.json"
PACKAGING_DIR = ROOT / "output/cl_staging/bud/packaging"
COMMONS = ROOT / "chunks_cache/commons"
MUSEUM = ROOT / "chunks_cache/museum"

HOLD = 2.0
VOICE_DELAY = 0.5
SUT = "https://suttacentral.net"
BATCH_ID = "bud_pilot137"

# ------------------------------------------------------------------ 16 BÀI SÓNG B (20-27/11)
ITEMS = [
    # PAIR 1 (W47 06:00): K5 (20/11 06:00 VN) vs P3 (21/11 06:00 VN) -> pair_w47_0600_3 [cùng tranh_bich_hoa]
    dict(
        id="bud137e_k5", day="2026-11-19", slot="23:00", slot_vn="2026-11-20 06:00 (giờ VN)",
        lane="tuong", arm="control", formula="control", pair_id="pair_w47_0600_3", img_kind="tranh_bich_hoa",
        hypothesis="Kể liền truyền thống + một tranh bích họa Ken Burns tĩnh trang nghiêm",
        title="Người đang cày thấy Đức Phật đứng khất thực", chip="ĐỜI THƯỜNG CỦA ĐỨC PHẬT", srcline="KINH TẬP 1.4",
        head='NGƯỜI ĐANG CÀY THẤY<br><span class="warm">ĐỨC PHẬT ĐỨNG KHẤT THỰC?</span>',
        script=[
            "Người cày thấy Phật đứng khất thực?",
            "Kinh kể, Đức Phật ôm bát đến nơi người cày đang làm việc.",
            "Người cày thấy Ngài đứng khất thực, liền nói:",
            "Ta cày cấy rồi mới ăn, sa môn cũng nên cày cấy rồi hãy ăn.",
            "Đức Phật đáp: Này Bà La Môn, Ta cũng cày cấy rồi mới ăn.",
            "Lời đáp của Đức Phật gợi cho bạn suy nghĩ gì?"
        ],
        cards=[
            None,
            '<div class="big warm" style="font-size:46px">ĐỨC PHẬT ÔM BÁT<br>ĐẾN NƠI ĐANG CÀY RUỘNG</div>',
            '<div class="big warm" style="font-size:48px">NGƯỜI CÀY THẤY NGÀI<br>ĐỨNG KHẤT THỰC</div>',
            '<div class="big warm" style="font-size:46px">“TA CÀY RỒI MỚI ĂN<br>ÔNG CŨNG NÊN CÀY ĐI”</div>',
            '<div class="big warm" style="font-size:48px">“NÀY BÀ LA MÔN<br>TA CŨNG CÀY RỒI MỚI ĂN”</div>',
            None
        ],
        image=COMMONS / "010_Cave_1_Ascetics_in_the_Forest_33438305044_.jpg",
        source=f"Kinh Tập 1.4 (snp1.4:1.4–2.4, 3.1), bản Bhikkhu Sujato (CC0): {SUT}/snp1.4/en/sujato — 'Then the Buddha robed up in the morning and, taking his bowl and robe, went to where Bhāradvāja the Farmer was working. ... Bhāradvāja the Farmer saw him standing for alms and said to him, “I plough and sow, ascetic, and then I eat. You too should plough and sow, then you may eat.” “I too plough and sow, brahmin, and then I eat.”'",
        insight="Kinh Tập 1.4 kể: Đức Phật khoác y ôm bát đến nơi người cày Bà Ra Đọa Xà đang làm việc; người cày thấy Ngài đứng khất thực liền bảo Ngài hãy cày rồi mới ăn; Đức Phật điềm tĩnh đáp rằng Ngài cũng cày và gieo mạ (bằng hạt giống niềm tin và trí tuệ) rồi mới ăn.",
        tags=["nguoi dang cay", "ba ra doa xa", "khat thuc", "kinh tap 1", "doi thuong duc phat"],
        tags_vi=["người đang cày", "Bà Ra Đọa Xà", "khất thực", "Kinh Tập 1", "đời thường Đức Phật"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#khấtthực", "#kinhtập"],
        cta="Khi đối diện với sự hoài nghi của người khác, bạn học được gì từ sự điềm đạm của Đức Phật?"
    ),

    # PAIR 2 (W47 19:30): P2 (20/11 19:30 VN) vs K6 (21/11 19:30 VN) -> pair_w47_1930_3 [cùng tranh_bich_hoa]
    dict(
        id="bud137e_p2", day="2026-11-20", slot="12:30", slot_vn="2026-11-20 19:30 (giờ VN)",
        lane="tuong", arm="md", formula="M1", pair_id="pair_w47_1930_3", img_kind="tranh_bich_hoa",
        hypothesis="Micro-Documentary: nhịp cắt theo câu + hình động từng mục (số thứ tự + chữ khoá) tăng stay & engagement",
        title="Năm vị cư sĩ kinh nêu trước hết", chip="NĂM VỊ CƯ SĨ ĐỨNG ĐẦU", srcline="TĂNG CHI 1.248–252",
        head='NĂM VỊ CƯ SĨ ĐỨNG ĐẦU<br><span class="warm">KINH NÊU TRƯỚC HẾT?</span>',
        script=[
            "Năm vị cư sĩ kinh nêu trước hết?",
            "Một, hai thương gia Đa Phù và Bạt Lợi, quy y trước hết.",
            "Hai, cư sĩ Tu Đạt Đa Cấp Cô Độc, bố thí đứng đầu.",
            "Ba, cư sĩ Chất Đa, đứng đầu về thuyết pháp.",
            "Bốn, cư sĩ Hát Thác Ca, đứng đầu hạnh nhiếp chúng.",
            "Năm, Ma Ha Nam dòng Thích Ca, dâng cúng đồ thù thắng.",
            "Bạn từng nghe câu chuyện của vị cư sĩ nào?"
        ],
        keywords=["ĐA PHÙ VÀ BẠT LỢI", "TU ĐẠT ĐA", "CƯ SĨ CHẤT ĐA", "HÁT THÁC CA", "MA HA NAM"],
        subtitles=["Quy y trước hết", "Bố thí đứng đầu", "Thuyết pháp đứng đầu", "Hạnh nhiếp chúng", "Dâng cúng đồ thù thắng"],
        images=[
            COMMONS / "021-The-Merchant-Muktaka-Original.jpg",
            COMMONS / "095_Anathapindaka_Buys_Jetavana_and_Offers_it_to_Buddha.jpg",
            COMMONS / "073_A_King_with_Attendees.jpg",
            COMMONS / "Borobudur_Relief_Panel_0979.jpg",
            COMMONS / "049_A_King_at_Court.jpg"
        ],
        source=f"Kinh Tăng Chi 1.248–252 (an1.248–252), bản Bhikkhu Sujato (CC0): {SUT}/an1.248-257/en/sujato — 'The foremost of my laymen disciples in first going for refuge are the merchants Tapussa and Bhallika. ... as a donor is the householder Sudatta Anāthapiṇḍika. ... who speak on the teaching is the householder Citta of Macchikāsaṇḍika. ... who attract a congregation by the four ways of being inclusive is Hatthaka of Āḷavī. ... who donate fine things is Mahānāma the Sakyan.'",
        insight="Kinh Tăng Chi 1.248–252 nêu 5 vị cư sĩ đứng đầu từng hạnh: Đa Phù và Bạt Lợi (quy y trước hết), Tu Đạt Đa Cấp Cô Độc (bố thí), Chất Đa (thuyết pháp), Hát Thác Ca (nhiếp chúng) và Ma Ha Nam (dâng cúng đồ thù thắng).",
        tags=["nam vi cu si", "da phu", "bat loi", "cap co doc", "tang chi 1"],
        tags_vi=["năm vị cư sĩ", "Đa Phù", "Bạt Lợi", "Cấp Cô Độc", "Tăng Chi 1"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#cưsĩ", "#tăngchi"],
        cta="Trong 5 vị cư sĩ tiêu biểu, tấm gương cống hiến nào truyền cảm hứng cho bạn nhất?"
    ),

    dict(
        id="bud137e_p3", day="2026-11-20", slot="23:00", slot_vn="2026-11-21 06:00 (giờ VN)",
        lane="tuong", arm="md", formula="M2", pair_id="pair_w47_0600_3", img_kind="tranh_bich_hoa",
        hypothesis="Micro-Documentary: nhịp cắt theo câu + hình động từng mục (số thứ tự + chữ khoá) tăng stay & engagement",
        title="Kinh kể bốn cách nằm", chip="BỐN CÁCH NẰM TRONG KINH", srcline="TĂNG CHI 4.246",
        head='BỐN CÁCH NẰM TRONG KINH<br><span class="warm">ĐƯỢC KỂ NHƯ THẾ NÀO?</span>',
        script=[
            "Kinh kể bốn cách nằm như thế nào?",
            "Một, người chết thường nằm ngửa thẳng lưng.",
            "Hai, người đắm dục lạc thường nằm nghiêng bên trái.",
            "Ba, sư tử chúa nằm nghiêng bên phải, chân này gác chân kia.",
            "Bốn, Đức Như Lai nằm nghiêng bên phải, an trú trong thiền định.",
            "Bạn thường nằm theo cách nào khi nghỉ ngơi?"
        ],
        keywords=["NẰM NGỬA", "NGHIÊNG BÊN TRÁI", "NGHIÊNG BÊN PHẢI", "AN TRÚ THIỀN ĐỊNH"],
        subtitles=["Dáng nằm người chết", "Người đắm dục lạc", "Dáng nằm sư tử", "Đức Phật an trú định"],
        images=[
            COMMONS / "103-The-King-Sleeping-Original.jpg",
            COMMONS / "049c_Archers_28141541574_.jpg",
            COMMONS / "046_Lion_33593460712_.jpg",
            COMMONS / "006a_E_A_Bodhisattva_Practicing_Meditation_28350358203_.jpg"
        ],
        source=f"Kinh Tăng Chi 4.246 (an4.246:1.1–4.2), bản Bhikkhu Sujato (CC0): {SUT}/an4.246/en/sujato — 'The ways a corpse, a pleasure seeker, a lion, and a Realized One lie down. Corpses usually lie flat on their backs. Pleasure seekers usually lie down on their left side. The lion, king of beasts, lies down on the right side, placing one foot on top of the other... It’s when a Realized One... enters and remains in the first absorption ... second ... third ... fourth.'",
        insight="Kinh Tăng Chi 4.246 phân biệt 4 tư thế nằm: người chết nằm ngửa, người hưởng dục nằm nghiêng trái, sư tử chúa nằm nghiêng phải gác chân, và Đức Như Lai nằm nghiêng phải an trú trong các tầng thiền định.",
        tags=["bon cach nam", "nam ngua", "nghieng ben phai", "su tu", "tang chi 4"],
        tags_vi=["bốn cách nằm", "nằm ngửa", "nghiêng bên phải", "sư tử", "Tăng Chi 4"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#thiềnđịnh", "#tăngchi"],
        cta="Tư thế nằm cát tường nghiêng bên phải của Đức Phật mang lại lợi ích gì cho giấc ngủ của bạn?"
    ),

    dict(
        id="bud137e_k6", day="2026-11-21", slot="12:30", slot_vn="2026-11-21 19:30 (giờ VN)",
        lane="tuong", arm="control", formula="control", pair_id="pair_w47_1930_3", img_kind="tranh_bich_hoa",
        hypothesis="Kể liền truyền thống + một tranh bích họa Ken Burns tĩnh trang nghiêm",
        title="Ngồi xuống khu rừng Uruvelā để tinh tấn", chip="ĐỜI THƯỜNG CỦA ĐỨC PHẬT", srcline="TRUNG BỘ 26",
        head='NGỒI XUỐNG RỪNG URUVELĀ<br><span class="warm">ĐỂ TINH TẤN TU TẬP?</span>',
        script=[
            "Đức Phật tìm nơi tinh tấn ở đâu?",
            "Kinh Trung Bộ kể, Ngài thấy một khu rừng khả ái, có dòng sông nước trong hiền hòa.",
            "Bờ sông phẳng lặng sạch sẽ, gần đó có làng để khất thực.",
            "Ngài nghĩ: Nơi này thật thích hợp để tinh tấn tu tập.",
            "Rồi Ngài ngồi xuống ngay tại chỗ ấy, dốc lòng hướng đến giác ngộ.",
            "Một góc tĩnh lặng có giúp bạn an lòng hơn mỗi ngày?"
        ],
        cards=[
            None,
            '<div class="big warm" style="font-size:46px">THẤY KHU RỪNG KHẢ ÁI<br>DÒNG SÔNG NƯỚC TRONG XANH</div>',
            '<div class="big warm" style="font-size:48px">BỜ SÔNG PHẲNG LẶNG<br>GẦN LÀNG ĐỂ KHẤT THỰC</div>',
            '<div class="big warm" style="font-size:46px">“NƠI NÀY THẬT THÍCH HỢP<br>ĐỂ TINH TẤN TU TẬP”</div>',
            '<div class="big warm" style="font-size:48px">NGỒI XUỐNG TẠI CHỖ<br>DỐC LÒNG HƯỚNG GIÁC NGỘ</div>',
            None
        ],
        image=COMMONS / "008_Cave_1_In_the_Forest_34239644366_.jpg",
        source=f"Kinh Trung Bộ 26 (mn26:17.2, 17.6, 17.7), bản Bhikkhu Sujato (CC0): {SUT}/mn26/en/sujato — 'There I saw a delightful park, a lovely grove with a flowing river that was clean and charming, with smooth banks. And nearby was a village to resort to for alms. So I sat down right there, thinking, “This is good enough for striving.”'",
        insight="Kinh Trung Bộ 26 ghi lại khoảnh khắc Bồ Tát tìm thấy chốn tu tập bên dòng sông Uruvelā phẳng lặng, gần làng khất thực, và Ngài ngồi xuống dốc trọn tâm lực tinh tấn cho đến ngày thành tựu đại giác ngộ.",
        tags=["rung uruvela", "tinh tan", "bo tat", "trung bo 26", "doi thuong duc phat"],
        tags_vi=["rừng Uruvelā", "tinh tấn", "Bồ Tát", "Trung Bộ 26", "đời thường Đức Phật"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#tịnhtâm", "#trungbộ"],
        cta="Bạn đã tạo cho mình một không gian tĩnh lặng để quay về với chính mình mỗi ngày chưa?"
    ),

    # PAIR 3 (W47 Extra): K7 (22/11 06:00 VN) vs P4 (22/11 19:30 VN) -> pair_w47_extra_1 [cùng tuong]
    dict(
        id="bud137e_k7", day="2026-11-21", slot="23:00", slot_vn="2026-11-22 06:00 (giờ VN)",
        lane="doi_song", arm="control", formula="control", pair_id="pair_w47_extra_1", img_kind="tuong",
        hypothesis="Kể liền truyền thống + một tượng Ken Burns tĩnh trang nghiêm",
        title="A-nan báo một vị vừa tịch, Đức Phật hỏi lại", chip="ĐỜI THƯỜNG CỦA ĐỨC PHẬT", srcline="TƯƠNG ƯNG 47.13",
        head='A-NAN BÁO ĐỆ TỬ TỊCH,<br><span class="warm">ĐỨC PHẬT HỎI LẠI ĐIỀU GÌ?</span>',
        script=[
            "Tin đệ tử tịch, Đức Phật dạy gì?",
            "Kinh kể, Tôn giả A Nan báo tin Tôn giả Xá Lợi Phất viên tịch.",
            "A Nan nghẹn ngào, đau buồn trước sự mất mát.",
            "Đức Phật hỏi: Xá Lợi Phất tịch có mang theo giới, định, tuệ của ông không?",
            "A Nan thưa không. Ngài dạy: Hãy tự mình là ngọn đèn cho chính mình.",
            "Lời dạy này nhắc bạn nương tựa vào điều gì trong đời?"
        ],
        cards=[
            None,
            '<div class="big warm" style="font-size:46px">A-NAN BÁO TIN<br>XÁ LỢI PHẤT VIÊN TỊCH</div>',
            '<div class="big warm" style="font-size:48px">NGHẸN NGÀO ĐAU BUỒN<br>TRƯỚC MẤT MÁT</div>',
            '<div class="big warm" style="font-size:44px">“XÁ LỢI PHẤT CÓ MANG THEO<br>GIỚI, ĐỊNH, TUỆ CỦA ÔNG KHÔNG?”</div>',
            '<div class="big warm" style="font-size:48px">HÃY TỰ MÌNH<br>LÀ NGỌN ĐÈN CHO CHÍNH MÌNH</div>',
            None
        ],
        image=COMMONS / "Buddha_in_Sarnath_Museum_Dhammajak_Mutra_.jpg",
        source=f"Kinh Tương Ưng 47.13 (sn47.13:4.3, 5.1), bản Bhikkhu Sujato (CC0): {SUT}/sn47.13/en/sujato — 'Venerable Sāriputta has become fully quenched. “Well, Ānanda, when Sāriputta was fully quenched, did he take away your entire spectrum of ethical conduct, of immersion, of wisdom, of freedom, or of the knowledge and vision of freedom?”'",
        insight="Khi Tôn giả A Nan đau buồn báo tin Xá Lợi Phất viên tịch, Đức Phật hỏi lại: Xá Lợi Phất tịch có mang theo giới, định hay tuệ của ông không? Qua đó Ngài nhắc nhở: Hãy tự mình là ngọn đèn, tự mình nương tựa chính mình (Kinh Tương Ưng 47.13).",
        tags=["xa loi phat", "a nan", "vien tich", "ngon den chinh minh", "tuong ung 47"],
        tags_vi=["Xá Lợi Phất", "A Nan", "viên tịch", "ngọn đèn chính mình", "Tương Ưng 47"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#ngọnđènchínhmình", "#vôthường"],
        cta="Khi người thân yêu rời xa, câu hỏi của Đức Phật nhắc chúng ta bài học sâu sắc nào về sự nương tựa tự thân?"
    ),

    dict(
        id="bud137e_p4", day="2026-11-22", slot="12:30", slot_vn="2026-11-22 19:30 (giờ VN)",
        lane="doi_song", arm="md", formula="M3", pair_id="pair_w47_extra_1", img_kind="tuong",
        hypothesis="Micro-Documentary: nhịp cắt theo câu + hình động từng mục (số thứ tự + chữ khoá) tăng stay & engagement",
        title="Kinh kể nhớ đức Phật, nhớ Pháp, nhớ Tăng, nhớ giới", chip="BỐN PHÁP TÙY NIỆM", srcline="TĂNG CHI 6.10",
        head='BỐN PHÁP TÙY NIỆM<br><span class="warm">KINH NÊU ĐẦU TIÊN?</span>',
        script=[
            "Bốn pháp tùy niệm kinh kể là gì?",
            "Một, người đệ tử nhớ nghĩ đến Đức Phật, bậc Giác Ngộ.",
            "Hai, người đệ tử nhớ nghĩ đến giáo Pháp chân thật.",
            "Ba, người đệ tử nhớ nghĩ đến Tăng chúng thanh tịnh.",
            "Bốn, người đệ tử nhớ nghĩ đến giới đức trong sạch của mình.",
            "Kinh còn nêu nhớ nghĩ bố thí và chư thiên, bạn thường nhớ nghĩ pháp nào?"
        ],
        keywords=["NHỚ NGHĨ PHẬT", "NHỚ NGHĨ PHÁP", "NHỚ NGHĨ TĂNG", "NHỚ NGHĨ GIỚI"],
        subtitles=["Bậc Giác Ngộ vẹn toàn", "Giáo pháp chân thật", "Tăng chúng thanh tịnh", "Giữ giới trong sạch"],
        images=[
            MUSEUM / "cma_141682.jpg",
            MUSEUM / "cma_135328.jpg",
            COMMONS / "Sitzstatue_Arhat_Liebieghaus_651.jpg",
            MUSEUM / "cma_169269.jpg"
        ],
        source=f"Kinh Tăng Chi 6.10 (an6.10:2.2, 3.1, 4.1, 5.1), bản Bhikkhu Sujato (CC0): {SUT}/an6.10/en/sujato — 'Firstly, a noble disciple recollects the Realized One ... recollects the teaching ... recollects the Saṅgha ... recollects their own ethical precepts, which are intact, impeccable, spotless, and unmarred...'",
        insight="Kinh Tăng Chi 6.10 kể 6 pháp tùy niệm, trong đó 4 pháp đầu là niệm Phật, niệm Pháp, niệm Tăng và niệm Giới; thực hành thường xuyên giúp tâm người đệ tử dứt trừ tham sân si, an trú hỷ lạc.",
        tags=["bon phap tuy niem", "niem phat", "niem phap", "niem tang", "tang chi 6"],
        tags_vi=["bốn pháp tùy niệm", "niệm Phật", "niệm Pháp", "niệm Tăng", "Tăng Chi 6"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#niệmphật", "#tăngchi"],
        cta="Mỗi khi lòng bất an, việc hướng tâm nhớ nghĩ đến Phật, Pháp, Tăng hay giới hạnh giúp bạn như thế nào?"
    ),

    # PAIR 4 (W48 06:00): P5 (23/11 06:00 VN) vs K9 (24/11 06:00 VN) -> pair_w48_0600_1 [cùng tranh_bich_hoa]
    dict(
        id="bud137e_p5", day="2026-11-22", slot="23:00", slot_vn="2026-11-23 06:00 (giờ VN)",
        lane="doi_song", arm="md", formula="M4", pair_id="pair_w48_0600_1", img_kind="tranh_bich_hoa",
        hypothesis="Micro-Documentary: nhịp cắt theo câu + hình động từng mục (số thứ tự + chữ khoá) tăng stay & engagement",
        title="Kinh kể bốn chỗ quán: thân, cảm thọ, tâm, nguyên lý", chip="BỐN CHỖ QUÁN TÂM", srcline="TRUNG BỘ 10",
        head='BỐN CHỖ QUÁN TÂM<br><span class="warm">KINH TRUNG BỘ DẠY GÌ?</span>',
        script=[
            "Bốn chỗ quán tâm kinh kể là gì?",
            "Một, vị tỳ-kheo quán sát thân nơi thân, nhiệt tâm tỉnh giác.",
            "Hai, vị ấy quán sát cảm thọ nơi các cảm thọ, không tham ưu.",
            "Ba, vị ấy quán sát tâm nơi tâm, sáng suốt ghi nhận.",
            "Bốn, vị ấy quán sát nguyên lý nơi các nguyên lý, nhiếp phục muộn phiền.",
            "Khi ngồi yên, bạn thường dễ nhận biết thân thể hay cảm thọ nhất?"
        ],
        keywords=["QUÁN THÂN", "QUÁN THỌ", "QUÁN TÂM", "QUÁN NGUYÊN LÝ"],
        subtitles=["Thân nơi thân nhiệt tâm", "Cảm thọ không tham ưu", "Tâm nơi tâm sáng suốt", "Nguyên lý nơi nguyên lý"],
        images=[
            COMMONS / "Bodhisattva_Padmapani_cave_1_Ajanta_India.jpg",
            COMMONS / "075b-A-Bodhisattva-in-Meditation-Original.jpg",
            COMMONS / "040_Cave_1_Four_Deer_One_Head_34122791662_.jpg",
            COMMONS / "063_Dharmacakra_on_Pillar_33620519361_.jpg"
        ],
        source=f"Kinh Trung Bộ 10 (mn10:3.2–3.5), bản Bhikkhu Sujato (CC0): {SUT}/mn10/en/sujato — 'meditates by observing an aspect of the body—keen, aware, and mindful, rid of covetousness and displeasure for the world ... observing an aspect of feelings ... observing an aspect of the mind ... observing an aspect of principles...'",
        insight="Kinh Trung Bộ 10 (Kinh Niệm Xứ) dạy 4 nền tảng quán chiếu: quán thân, quán thọ, quán tâm và quán nguyên lý (pháp); đây là con đường độc nhất đưa đến thanh tịnh và đoạn tận khổ ưu.",
        tags=["bon cho quan", "quan than", "quan tho", "quan tam", "trung bo 10"],
        tags_vi=["bốn chỗ quán", "quán thân", "quán thọ", "quán tâm", "Trung Bộ 10"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#niệmxứ", "#thiềnchánhniệm"],
        cta="Trong bốn lĩnh vực quán chiếu, bạn thấy quán sát hơi thở và thân thể có phải là bước đầu dễ thực hành nhất?"
    ),

    # PAIR 5 (W48 19:30): K8 (23/11 19:30 VN) vs P6 (24/11 19:30 VN) -> pair_w48_1930_1 [cùng tranh_bich_hoa]
    dict(
        id="bud137e_k8", day="2026-11-23", slot="12:30", slot_vn="2026-11-23 19:30 (giờ VN)",
        lane="doi_song", arm="control", formula="control", pair_id="pair_w48_1930_1", img_kind="tranh_bich_hoa",
        hypothesis="Kể liền truyền thống + một tranh bích họa Ken Burns tĩnh trang nghiêm",
        title="Bảy báu của bậc vua vẫn không đủ để đền", chip="CÔNG ƠN CHA MẸ", srcline="TĂNG CHI 2.33",
        head='BẢY BÁU CỦA ĐẾ VƯƠNG<br><span class="warm">VẪN KHÔNG ĐỦ ĐỀN ƠN?</span>',
        script=[
            "Ơn cha mẹ lớn đến mức nào?",
            "Kinh Tăng Chi dạy, dù có lập cha mẹ làm vua chúa tối cao trên cõi đất lớn này.",
            "Dù trao cho cha mẹ đầy đủ bảy món báu của bậc chuyển luân vương.",
            "Người con vẫn chưa đền đáp đủ công ơn sinh thành dưỡng dục.",
            "Đức Phật dạy, chỉ khi hướng cha mẹ vào giới đức và trí tuệ, mới là đền ơn trọn vẹn.",
            "Hôm nay bạn đã làm điều gì nhỏ bé để hiếu thảo với cha mẹ chưa?"
        ],
        cards=[
            None,
            '<div class="big warm" style="font-size:46px">DÙ LẬP CHA MẸ<br>LÀM VUA CÕI ĐẤT NÀY</div>',
            '<div class="big warm" style="font-size:48px">TRAO ĐỦ BẢY MÓN BÁU<br>CỦA BẬC ĐẾ VƯƠNG</div>',
            '<div class="big warm" style="font-size:48px">VẪN CHƯA ĐỀN ĐÁP ĐỦ<br>ƠN SÂU DƯỠNG DỤC</div>',
            '<div class="big warm" style="font-size:46px">HƯỚNG CHA MẸ VÀO ĐẠO<br>MỚI LÀ ĐỀN ƠN TRỌN VẸN</div>',
            None
        ],
        image=COMMONS / "050_The_Buddha_s_Step-Mother_Mahapajapati_offers_Robes_to_the_Sangha_9270724819_.jpg",
        source=f"Kinh Tăng Chi 2.33 (an2.33:1.6 trong an2.32-41), bản Bhikkhu Sujato (CC0): {SUT}/an2.32-41/en/sujato — 'Even if you were to establish your mother and father as supreme monarchs of this great earth, abounding in the seven treasures, you would still not have done enough to repay them.'",
        insight="Kinh Tăng Chi 2.33 dạy: Dù lập cha mẹ làm bậc đế vương sở hữu bảy báu trần gian, người con vẫn chưa đền đáp hết ơn sâu; chỉ khi giúp cha mẹ an trú vào niềm tin, giới hạnh và trí tuệ, mới là đền đáp công ơn sinh thành một cách trọn vẹn.",
        tags=["cong on cha me", "bay bau", "hieu thao", "tang chi 2", "loi phat day"]
        ,
        tags_vi=["công ơn cha mẹ", "bảy báu", "hiếu thảo", "Tăng Chi 2", "lời Phật dạy"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#hiếuđạo", "#tăngchi"],
        cta="Điều gì bạn có thể làm ngay hôm nay để mang lại niềm an vui thực sự cho cha mẹ?"
    ),

    dict(
        id="bud137e_k9", day="2026-11-23", slot="23:00", slot_vn="2026-11-24 06:00 (giờ VN)",
        lane="doi_song", arm="control", formula="control", pair_id="pair_w48_0600_1", img_kind="tranh_bich_hoa",
        hypothesis="Kể liền truyền thống + một tranh bích họa Ken Burns tĩnh trang nghiêm",
        title="Đức Phật không nhận lời sỉ nhục của bà-la-môn", chip="ĐỜI THƯỜNG CỦA ĐỨC PHẬT", srcline="TƯƠNG ƯNG 7.2",
        head='BỊ SỈ NHỤC VÀ MẮNG NHIẾC,<br><span class="warm">ĐỨC PHẬT LÀM GÌ?</span>',
        script=[
            "Bị mắng nhiếc, Đức Phật làm gì?",
            "Kinh kể, một người Bà La Môn tức giận đến mắng nhiếc Đức Phật.",
            "Đức Phật hỏi: Nhà ông dọn cỗ, khách không ăn thì đồ ăn về ai?",
            "Người ấy đáp: Thức ăn ấy sẽ thuộc về tôi.",
            "Phật dạy: Ta không nhận, thì lời mắng ấy thuộc về chính ông.",
            "Khi gặp lời cay nghiệt, bạn có chọn không nhận như Phật không?"
        ],
        cards=[
            None,
            '<div class="big warm" style="font-size:46px">BÀ LA MÔN TỨC GIẬN<br>MẮNG NHIẾC ĐỨC PHẬT</div>',
            '<div class="big warm" style="font-size:46px">“ÔNG DỌN CỖ CHO KHÁCH<br>KHÁCH KHÔNG ĂN THÌ VỀ AI?”</div>',
            '<div class="big warm" style="font-size:48px">“NẾU HỌ KHÔNG NHẬN<br>THỨC ĂN VỀ PHẦN TÔI”</div>',
            '<div class="big warm" style="font-size:46px">“ÔNG MẮNG TA KHÔNG NHẬN<br>LỜI MẮNG VỀ CHÍNH ÔNG”</div>',
            None
        ],
        image=COMMONS / "Ajatashatru_Worships_the_Buddha.jpg",
        source=f"Kinh Tương Ưng 7.2 (sn7.2:2.1, 2.9, 3.1), bản Bhikkhu Sujato (CC0): {SUT}/sn7.2/en/sujato — 'Angry and displeased he went to the Buddha and abused and insulted him with rude, harsh words. ... “In the same way, brahmin, when you abuse, harass, and attack us who do not abuse, harass, and attack, we don’t accept it. Someone who ... abuses in return is said to eat the food and have a reaction to it.”'",
        insight="Kinh Tương Ưng 7.2 kể: Khi bị một Bà La Môn thô bạo mắng chửi, Đức Phật ví lời chửi mắng như mâm cỗ khách không nhận thì thuộc về chủ nhà; Ngài không nhận thì oán giận tự quay về làm hại chính người buông lời cay nghiệt.",
        tags=["khong nhan loi mang", "ba la mon", "nhan nhuc", "tuong ung 7", "doi thuong duc phat"],
        tags_vi=["không nhận lời mắng", "Bà La Môn", "nhẫn nhục", "Tương Ưng 7", "đời thường Đức Phật"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#nhẫnnhục", "#bìnhan"],
        cta="Trước những lời chê bai ác ý, bí quyết 'không nhận' của Đức Phật có giúp bạn bảo vệ sự bình an nội tâm?"
    ),

    dict(
        id="bud137e_p6", day="2026-11-24", slot="12:30", slot_vn="2026-11-24 19:30 (giờ VN)",
        lane="doi_song", arm="md", formula="M1", pair_id="pair_w48_1930_1", img_kind="tranh_bich_hoa",
        hypothesis="Micro-Documentary: nhịp cắt theo câu + hình động từng mục (số thứ tự + chữ khoá) tăng stay & engagement",
        title="Năm điều của người bệnh dễ chăm, kinh kể", chip="NGƯỜI BỆNH DỄ CHĂM SÓC", srcline="TĂNG CHI 5.123",
        head='NGƯỜI BỆNH DỄ CHĂM SÓC<br><span class="warm">KINH KỂ NĂM ĐIỀU GÌ?</span>',
        script=[
            "Năm điều của người bệnh dễ chăm sóc?",
            "Một, người bệnh làm những việc thích hợp cho sức khỏe.",
            "Hai, biết chừng mực trong những việc thích hợp ấy.",
            "Ba, người bệnh chịu uống thuốc theo chỉ dẫn.",
            "Bốn, nói đúng triệu chứng bệnh cho người chăm sóc.",
            "Năm, có thể kham nhẫn chịu đựng các cơn đau thân thể.",
            "Bạn thấy đức tính kham nhẫn giúp ích gì nhất khi ốm đau?"
        ],
        keywords=["VIỆC THÍCH HỢP", "BIẾT CHỪNG MỰC", "CHỊU UỐNG THUỐC", "KỂ ĐÚNG BỆNH", "CHỊU ĐƯỢC ĐAU"],
        subtitles=["Làm việc thích hợp", "Chừng mực điều độ", "Tuân thủ dùng thuốc", "Báo đúng triệu chứng", "Kham nhẫn chịu đau"],
        images=[
            COMMONS / "013_Jataka_Story_9213182054_.jpg",
            COMMONS / "015_Jataka_Story_9213174450_.jpg",
            COMMONS / "COLLECTIE_TROPENMUSEUM_Reliëf_Sutasoma-jataka_3_Borobudur_TMnr_60042634.jpg",
            COMMONS / "COLLECTIE_TROPENMUSEUM_Reliëf_Mahisa-jataka_3_Borobudur_TMnr_60042638.jpg",
            COMMONS / "036_Mahisa_Jataka.jpg"
        ],
        source=f"Kinh Tăng Chi 5.123 (an5.123:2.1, 2.3), bản Bhikkhu Sujato (CC0): {SUT}/an5.123/en/sujato — 'A patient with five qualities is easy to care for. They do what is suitable. They know moderation in what is suitable. They take their medicine. Because their carer wants what’s best for them, they accurately report their symptoms ... And they can endure physical pain—sharp, severe, acute, unpleasant, disagreeable, and life-threatening.'",
        insight="Kinh Tăng Chi 5.123 nêu 5 phẩm chất của người bệnh dễ chăm sóc: làm việc thích hợp, biết chừng mực, chịu dùng thuốc, báo đúng tình trạng bệnh và kham nhẫn chịu đau đớn.",
        tags=["nguoi benh de cham", "chieu uong thuoc", "kham nhan", "tang chi 5", "loi phat day"],
        tags_vi=["người bệnh dễ chăm", "chịu uống thuốc", "kham nhẫn", "Tăng Chi 5", "lời Phật dạy"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#sứckhỏe", "#tăngchi"],
        cta="Khi gặp bệnh tật, tâm kham nhẫn và sự hợp tác có giúp quá trình hồi phục của bạn dễ dàng hơn không?"
    ),

    # PAIR 6 (W48 06:00): D1 (25/11 06:00 VN) vs K11 (26/11 06:00 VN) -> pair_w48_0600_2 [cùng tuong]
    dict(
        id="bud137e_d1", day="2026-11-24", slot="23:00", slot_vn="2026-11-25 06:00 (giờ VN)",
        lane="kinh_chu", arm="md", formula="M2", pair_id="pair_w48_0600_2", img_kind="tuong",
        hypothesis="Micro-Documentary: nhịp cắt theo câu + hình động từng mục (số thứ tự + chữ khoá) tăng stay & engagement",
        title="Bốn sự thật Đức Phật dạy đầu tiên", chip="BỐN SỰ THẬT CAO QUÝ", srcline="TƯƠNG ƯNG 56.11",
        head='BỐN SỰ THẬT CAO QUÝ<br><span class="warm">ĐỨC PHẬT DẠY ĐẦU TIÊN?</span>',
        script=[
            "Bốn sự thật Đức Phật dạy đầu tiên?",
            "Một, sự thật cao quý về sự khổ ở đời.",
            "Hai, sự thật cao quý về nguyên nhân sinh ra khổ.",
            "Ba, sự thật cao quý về sự chấm dứt hoàn toàn khổ.",
            "Bốn, sự thật cao quý về con đường dẫn đến diệt khổ.",
            "Bạn đã từng tìm hiểu sâu về bốn sự thật mầu nhiệm này chưa?"
        ],
        keywords=["SỰ THẬT VỀ KHỔ", "NGUYÊN NHÂN KHỔ", "CHẤM DỨT KHỔ", "CON ĐƯỜNG DIỆT KHỔ"],
        subtitles=["Khổ đế chân thật", "Tập đế sinh khởi", "Diệt đế tịch tịnh", "Đạo đế giải thoát"],
        images=[
            COMMONS / "Seated_Buddha_Gandhara_Pakistan_Kushan_dynasty_100s-200s_AD_schist_-_Tokyo_National_Museum_-_Tokyo_Japan_-_DSC08664.jpg",
            MUSEUM / "cma_153369.jpg",
            MUSEUM / "cma_145208.jpg",
            MUSEUM / "cma_140151.jpg"
        ],
        source=f"Kinh Tương Ưng 56.11 (sn56.11:4.1, 4.3, 4.6, 4.8), bản Bhikkhu Sujato (CC0): {SUT}/sn56.11/en/sujato — 'Now this is the noble truth of suffering. ... Now this is the noble truth of the origin of suffering. ... Now this is the noble truth of the cessation of suffering. ... Now this is the noble truth of the practice that leads to the cessation of suffering.'",
        insight="Trong bài kinh Chuyển Pháp Luân (Kinh Tương Ưng 56.11), Đức Phật lần đầu tiên tuyên thuyết Tứ Diệu Đế: nhận diện nỗi khổ, hiểu rõ nguyên nhân sinh khổ, chứng ngộ cảnh giới dứt khổ và thực hành con đường giải thoát.",
        tags=["bon su that", "tu dieu de", "kho tap diet dao", "tuong ung 56", "chuyen phap luan"],
        tags_vi=["bốn sự thật", "Tứ Diệu Đế", "Khổ Tập Diệt Đạo", "Tương Ưng 56", "Chuyển Pháp Luân"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#tứdiệuđế", "#tươngưng"],
        cta="Hiểu được bản chất của khổ đau giúp bạn tìm thấy sự bình an như thế nào giữa cuộc sống biến động?"
    ),

    # PAIR 7 (W48 19:30): K10 (25/11 19:30 VN) vs D2 (26/11 19:30 VN) -> pair_w48_1930_2 [cùng tuong]
    dict(
        id="bud137e_k10", day="2026-11-25", slot="12:30", slot_vn="2026-11-25 19:30 (giờ VN)",
        lane="kinh_chu", arm="control", formula="control", pair_id="pair_w48_1930_2", img_kind="tuong",
        hypothesis="Kể liền truyền thống + một tượng Ken Burns tĩnh trang nghiêm",
        title="Câu kính lễ mở đầu đảnh lễ bậc Giác Ngộ", chip="CÂU KÍNH LỄ MỞ ĐẦU", srcline="TIỂU TỤNG 1",
        head='CÂU KÍNH LỄ MỞ ĐẦU<br><span class="warm">ĐẢNH LỄ BẬC GIÁC NGỘ?</span>',
        script=[
            "Lời kinh đảnh lễ Đức Phật?",
            "Kinh Tiểu Tụng mở đầu bằng lời tán thán ba đức hạnh tối cao.",
            "Con xin kính lễ Đức Thế Tôn, bậc Ứng Cúng cao quý.",
            "Bậc Chánh Đẳng Giác, tự mình thấu suốt chân lý nhiệm mầu.",
            "Theo sau là ba lời nguyện trọn đời nương tựa Phật, Pháp, Tăng.",
            "Mỗi khi niệm câu kính lễ này, tâm bạn có thấy bình an hơn không?"
        ],
        cards=[
            None,
            '<div class="big warm" style="font-size:46px">KINH TIỂU TỤNG MỞ ĐẦU<br>TÁN THÁN ĐỨC PHẬT</div>',
            '<div class="big warm" style="font-size:48px">KÍNH LỄ ĐỨC THẾ TÔN<br>BẬC ỨNG CÚNG CAO QUÝ</div>',
            '<div class="big warm" style="font-size:46px">BẬC CHÁNH ĐẲNG GIÁC<br>THẤU SUỐT CHÂN LÝ</div>',
            '<div class="big warm" style="font-size:46px">TRỌN ĐỜI NƯƠNG TỰA<br>PHẬT, PHÁP VÀ TĂNG</div>',
            None
        ],
        image=COMMONS / "Buddha_Tượng_Phật_Đồng_Dương_the_Museum_of_Vietnamese_History.jpg",
        source=f"Kinh Tiểu Tụng 1 (kp1:1.1, 2.1–2.3), bản Bhikkhu Sujato (CC0): {SUT}/kp1/en/sujato — 'Homage to him, the blessed one, the perfected one, the fully awakened Buddha! I take refuge in the Buddha, I take refuge in the Teaching, I take refuge in the Saṅgha.'",
        insight="Kinh Tiểu Tụng 1 mở đầu kinh điển Pāli bằng câu kính lễ truyền thống: Namo Tassa Bhagavato Arahato Samma-sambuddhassa (Kính lễ Đức Thế Tôn, bậc Ứng Cúng, bậc Chánh Đẳng Giác) và lời phát nguyện Tam Quy.",
        tags=["cau kinh le", "namo tassa", "tieu tung 1", "danh le duc phat", "tam quy"],
        tags_vi=["câu kính lễ", "Namo Tassa", "Tiểu Tụng 1", "đảnh lễ Đức Phật", "Tam Quy"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#namotassa", "#tiểutụng"],
        cta="Mỗi ngày khởi đầu bằng ba câu niệm kính lễ Phật có giúp bạn định tĩnh hơn trong mọi công việc?"
    ),

    dict(
        id="bud137e_k11", day="2026-11-25", slot="23:00", slot_vn="2026-11-26 06:00 (giờ VN)",
        lane="kinh_chu", arm="control", formula="control", pair_id="pair_w48_0600_2", img_kind="tuong",
        hypothesis="Kể liền truyền thống + một tượng Ken Burns tĩnh trang nghiêm",
        title="Kinh lời từ mong mọi loài được an vui", chip="TÂM TỪ VÔ LƯỢNG", srcline="KINH TẬP 1.8",
        head='KINH LỜI TỪ MONG NGUYỆN<br><span class="warm">MỌI LOÀI ĐƯỢC AN VUI?</span>',
        script=[
            "Kinh mong nguyện gì cho muôn loài?",
            "Kinh Từ Bi dạy rải lòng thương yêu rộng lớn đến khắp muôn loài hữu tình.",
            "Dù kẻ yếu hay mạnh, lớn hay nhỏ, thấy được hay không thấy được.",
            "Dù ở gần hay ở xa, đã sinh ra hay sắp sinh ra.",
            "Nguyện cho tất cả chúng sinh khắp nơi đều được an lành và hạnh phúc.",
            "Gửi một lời chúc an lành đến người bên cạnh, tâm bạn có thấy nhẹ nhõm hơn?"
        ],
        cards=[
            None,
            '<div class="big warm" style="font-size:46px">RẢI LÒNG THƯƠNG YÊU<br>ĐẾN KHẮP MUÔN LOÀI</div>',
            '<div class="big warm" style="font-size:46px">DÙ KẺ YẾU HAY MẠNH<br>LỚN HAY NHỎ XA GẦN</div>',
            '<div class="big warm" style="font-size:46px">ĐÃ SINH HAY SẮP SINH<br>KHẮP TRONG MƯỜI PHƯƠNG</div>',
            '<div class="big warm" style="font-size:48px">NGUYỆN CHO TẤT CẢ<br>ĐỀU ĐƯỢC AN VUI</div>',
            None
        ],
        image=COMMONS / "Amitabha_of_Phat_Tich_pagoda_reproduction_Bac_Ninh_province_1057_AD_DSC04838.jpg",
        source=f"Kinh Tập 1.8 (snp1.8:3.4, 5.4), bản Bhikkhu Sujato (CC0): {SUT}/snp1.8/en/sujato — 'May all beings be happy! ... Whatever living creatures there may be ... frail or firm, long or large, medium or small ... seen or unseen, living far or near, born or seeking birth—may all beings be happy!'" ,
        insight="Kinh Từ Bi (Kinh Tập 1.8 - Metta Sutta) dạy rải tâm từ ái vô lượng không giới hạn đến khắp muôn loài hữu tình xa gần, cầu chúc tất cả chúng sinh đều sống trong an lạc và không thù hận.",
        tags=["kinh tu bi", "metta sutta", "mong moi loai an vui", "kinh tap 1", "tam tu"],
        tags_vi=["kinh Từ Bi", "Metta Sutta", "mong mọi loài an vui", "Kinh Tập 1", "tâm từ"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#kinhtừbi", "#từbi"],
        cta="Khi rải tâm từ chúc phúc cho cả những người từng làm ta tổn thương, gánh nặng trong lòng bạn vơi đi thế nào?"
    ),

    dict(
        id="bud137e_d2", day="2026-11-26", slot="12:30", slot_vn="2026-11-26 19:30 (giờ VN)",
        lane="kinh_chu", arm="md", formula="M3", pair_id="pair_w48_1930_2", img_kind="tuong",
        hypothesis="Micro-Documentary: nhịp cắt theo câu + hình động từng mục (số thứ tự + chữ khoá) tăng stay & engagement",
        title="Bốn nhánh đầu của con đường tám nhánh", chip="BỐN NHÁNH ĐẦU BÁT CHÁNH ĐẠO", srcline="TƯƠNG ƯNG 56.11",
        head='BỐN NHÁNH ĐẦU TIÊN CỦA<br><span class="warm">CON ĐƯỜNG TÁM NHÁNH?</span>',
        script=[
            "Bốn nhánh đầu Bát Chánh Đạo?",
            "Một, Chánh Kiến, cái nhìn thấu suốt lẽ thật.",
            "Hai, Chánh Tư Duy, suy nghĩ chân chính không hại người.",
            "Ba, Chánh Ngữ, lời nói hòa ái trung thực.",
            "Bốn, Chánh Nghiệp, hành động lương thiện trong sạch.",
            "Kinh còn dạy Chánh Mạng, Tinh Tấn, Niệm và Định, bạn đang rèn nhánh nào?"
        ],
        keywords=["CHÁNH KIẾN", "CHÁNH TƯ DUY", "CHÁNH NGỮ", "CHÁNH NGHIỆP"],
        subtitles=["Cái nhìn thấu suốt", "Suy nghĩ chân chính", "Lời nói hòa ái", "Hành động lương thiện"],
        images=[
            MUSEUM / "cma_94676.jpg",
            MUSEUM / "cma_121206.jpg",
            COMMONS / "Labit_-_Sitting_Buddha_meditating_-_Swat_Valley_Gandhara_Pakistan_D._70.1.2.jpg",
            MUSEUM / "aic_103274.jpg"
        ],
        source=f"Kinh Tương Ưng 56.11 (sn56.11:3.3, 4.10), bản Bhikkhu Sujato (CC0): {SUT}/sn56.11/en/sujato — 'right view, right purpose, right speech, right action, right livelihood, right effort, right mindfulness, and right immersion.'",
        insight="Trong Kinh Tương Ưng 56.11, Đức Phật chỉ rõ 4 nhánh đầu của Bát Chánh Đạo: Chánh kiến (thấy biết đúng), Chánh tư duy (nghĩ thiện), Chánh ngữ (lời chân thật) và Chánh nghiệp (hành động trong sạch).",
        tags=["bon nhanh dau", "bat chanh dao", "chanh kien", "chanh ngu", "tuong ung 56"],
        tags_vi=["bốn nhánh đầu", "Bát Chánh Đạo", "Chánh kiến", "Chánh ngữ", "Tương Ưng 56"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#bátchánhđạo", "#tươngưng"],
        cta="Trong đời sống hằng ngày, nhánh thực hành nào trong bốn nhánh đầu giúp bạn giữ tâm trong sáng nhất?"
    ),

    # PAIR 8 (W48 Extra): D3 (27/11 06:00 VN) vs K12 (27/11 19:30 VN) -> pair_w48_extra_1 [cùng tranh_bich_hoa]
    dict(
        id="bud137e_d3", day="2026-11-26", slot="23:00", slot_vn="2026-11-27 06:00 (giờ VN)",
        lane="kinh_chu", arm="md", formula="M4", pair_id="pair_w48_extra_1", img_kind="tranh_bich_hoa",
        hypothesis="Micro-Documentary: nhịp cắt theo câu + hình động từng mục (số thứ tự + chữ khoá) tăng stay & engagement",
        title="Người tại gia giữ mấy điều, kinh kể ra", chip="NĂM ĐIỀU NGƯỜI TẠI GIA GIỮ", srcline="TĂNG CHI 8.39",
        head='NĂM ĐIỀU NGƯỜI TẠI GIA<br><span class="warm">KINH KỂ NẰM TRONG TÁM?</span>',
        script=[
            "Người tại gia giữ những điều gì theo kinh dạy?",
            "Trong tám nguồn phước, một là từ bỏ sát hại chúng sinh.",
            "Hai, từ bỏ lấy của không cho, trộm cắp gian lận.",
            "Ba, từ bỏ tà hạnh buông thả trong dục vọng.",
            "Bốn, từ bỏ nói dối và lời chia rẽ.",
            "Năm, từ bỏ rượu bia và chất say làm mê muội.",
            "Theo bạn, điều nào cần nhiều sự tỉnh thức nhất trong cuộc sống hiện đại?"
        ],
        keywords=["TỪ BỎ SÁT SINH", "TỪ BỎ TRỘM CẮP", "TỪ BỎ TÀ HẠNH", "TỪ BỎ NÓI DỐI", "TỪ BỎ CHẤT SAY"],
        subtitles=["Không sát hại chúng sinh", "Không trộm cắp gian lận", "Không buông thả tà hạnh", "Không nói dối chia rẽ", "Không rượu bia say sưa"],
        images=[
            COMMONS / "007_Sasa_Jataka.jpg",
            COMMONS / "034_Matsya_Jataka.jpg",
            COMMONS / "106-A-Procession-of-Women-Original.jpg",
            COMMONS / "058-The-Bodhisattva-makes-an-Asservation-of-Truth-Original.jpg",
            COMMONS / "107-Ksantivadi-preaches-Patience-Original.jpg"
        ],
        source=f"Kinh Tăng Chi 8.39 (an8.39:3.5, 4.1, 5.1, 6.1, 7.1), bản Bhikkhu Sujato (CC0): {SUT}/an8.39/en/sujato — 'Firstly, a noble disciple gives up killing living creatures. ... gives up stealing ... gives up sexual misconduct ... gives up lying ... gives up intoxicants of beer, wine, and liquor.'",
        insight="Kinh Tăng Chi 8.39 liệt kê 5 món quà vô úy trong 8 nguồn phước báu của người đệ tử tại gia: không sát sinh, không trộm cắp, không tà hạnh, không nói dối và không dùng các chất say làm say sưa mê muội.",
        tags=["nguoi tai gia", "nam gioi", "tu bo sat sinh", "tang chi 8", "loi phat day"],
        tags_vi=["người tại gia", "năm giới", "từ bỏ sát sinh", "Tăng Chi 8", "lời Phật dạy"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#nămgiới", "#tăngchi"],
        cta="Giữ trọn vẹn năm điều giới đức này mang lại sự thanh thản và bình yên cho gia đình bạn như thế nào?"
    ),

    dict(
        id="bud137e_k12", day="2026-11-27", slot="12:30", slot_vn="2026-11-27 19:30 (giờ VN)",
        lane="kinh_chu", arm="control", formula="control", pair_id="pair_w48_extra_1", img_kind="tranh_bich_hoa",
        hypothesis="Kể liền truyền thống + một tranh bích họa Ken Burns tĩnh trang nghiêm",
        title="Kinh mong phần này cho người thân đã khuất", chip="HỒI HƯỚNG PHƯỚC BÁU", srcline="TIỂU TỤNG 7",
        head='KINH MONG PHẦN NÀY CHO<br><span class="warm">NGƯỜI THÂN ĐÃ KHUẤT?</span>',
        script=[
            "Kinh nguyện gì cho người thân đã khuất?",
            "Kinh Tiểu Tụng dạy người sống làm phước lành rồi hồi hướng cho thân quyến quá vãng.",
            "Đặt bát cúng dường với tâm thanh tịnh và kính cẩn.",
            "Rồi đọc lời nguyện: Nguyện phần phước này dâng đến những người thân đã khuất.",
            "Nguyện cho tất cả thân quyến của chúng con đều được an vui hạnh phúc.",
            "Lòng tưởng nhớ chân thành chính là món quà quý giá nhất gửi người đã khuất."
        ],
        cards=[
            None,
            '<div class="big warm" style="font-size:46px">LÀM VIỆC PHƯỚC LÀNH<br>HỒI HƯỚNG THÂN QUYẾN</div>',
            '<div class="big warm" style="font-size:48px">CÚNG DƯỜNG THANH TỊNH<br>VỚI TÂM KÍNH CẨN</div>',
            '<div class="big warm" style="font-size:46px">“NGUYỆN PHƯỚC NÀY ĐẾN<br>NGƯỜI THÂN ĐÃ KHUẤT”</div>',
            '<div class="big warm" style="font-size:48px">NGUYỆN CHO THÂN BẰNG<br>ĐỀU ĐƯỢC AN VUI</div>',
            None
        ],
        image=COMMONS / "042_Devotees_Worshipping_33709076186_.jpg",
        source=f"Kinh Tiểu Tụng 7 (kp7:4.1, 4.2), bản Bhikkhu Sujato (CC0): {SUT}/kp7/en/sujato — '“May this be for our relatives! May our relatives be happy!”'",
        insight="Kinh Tiểu Tụng 7 (Kinh Ngoài Bức Tường - Tirokudda Sutta) dạy người còn sống tạo phước lành hồi hướng đến cửu huyền thất tổ và người thân đã khuất: Mong phần phước này đến với thân quyến, nguyện cho thân quyến được an vui.",
        tags=["hoi huong phuoc bau", "nguoi than da khuat", "tieu tung 7", "tirokudda", "loi phat day"],
        tags_vi=["hồi hướng phước báu", "người thân đã khuất", "Tiểu Tụng 7", "Tirokudda", "lời Phật dạy"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#hồihướng", "#tiểutụng"],
        cta="Mỗi khi làm một việc thiện, bạn có thường khởi tâm hồi hướng an vui đến tổ tiên và người thân đã khuất?"
    ),
]

# ------------------------------------------------------------------ 137f: SỬA LỜI + ẢNH (vòng sửa duy nhất)
def _C(prefix):
    for d in (COMMONS, MUSEUM):
        m = sorted(d.glob(prefix + "*"))
        m = [x for x in m if x.suffix.lower() == ".jpg"]
        if m:
            return m[0]
    raise FileNotFoundError(prefix)

def _big(t, size=46):
    return f'<div class="big warm" style="font-size:{size}px">{t}</div>'

FIX137F = {
 "bud137e_k5": dict(head='NGƯỜI CÀY THẤY<br><span class="warm">PHẬT ĐỨNG KHẤT THỰC?</span>', insight="Kinh Tập 1.4 kể: Đức Phật khoác y ôm bát đến nơi người cày Bà Ra Đọa Xà (Bhāradvāja) đang làm việc; người cày thấy Ngài đứng khất thực liền bảo Ngài hãy cày cấy rồi mới ăn; Đức Phật đáp rằng Ngài cũng cày cấy rồi mới ăn."),
 "bud137e_p2": dict(images=["021-The-Merchant-Muktaka", "095_Anathapindaka", "049_A_King_at_Court", "007_Sasa_Jataka", "063_Dharmacakra"]),
 "bud137e_p3": dict(
    head='BỐN CÁCH NẰM<br><span class="warm">KINH KỂ THẾ NÀO?</span>',
    images=["103-The-King-Sleeping", "073_A_King_with_Attendees", "046_Lion", "Bodhisattva_Padmapani"],
    script={4: "Bốn, Đức Như Lai an trú trong bốn tầng thiền."},
    keywords={3: "BỐN TẦNG THIỀN"}, subtitles={3: "Cách nằm của Như Lai"},
    insight="Kinh Tăng Chi 4.246 nêu 4 cách nằm: người chết nằm ngửa, người hưởng dục nằm nghiêng bên trái, sư tử chúa nằm nghiêng bên phải, chân này gác lên chân kia, còn cách nằm của Như Lai là vào và an trú trong bốn tầng thiền.",
    cta="Trong bốn cách nằm kinh kể, bạn thấy cách nào gần với đời mình nhất?"),
 "bud137e_k6": dict(tags=["ruong rung kha ai","tinh tan","trung bo 26","doi thuong duc phat"], tags_vi=["khu rừng khả ái", "tinh tấn", "Trung Bộ 26", "đời thường Đức Phật"],
    title="Ngồi xuống khu rừng khả ái để tinh tấn", image="050_The_Buddha_s_Step-Mother",
    head='NGỒI XUỐNG RỪNG KHẢ ÁI<br><span class="warm">ĐỂ TINH TẤN TU TẬP?</span>',
    script={2: "Bờ sông bằng phẳng, gần đó có làng để khất thực.",
            4: "Rồi Ngài ngồi xuống ngay tại chỗ ấy, nghĩ: nơi này đủ để tinh tấn."},
    cards={2: _big("BỜ SÔNG BẰNG PHẲNG<br>GẦN LÀNG ĐỂ KHẤT THỰC", 48),
           4: _big("NGỒI XUỐNG NGAY TẠI CHỖ<br>“NƠI NÀY ĐỦ ĐỂ TINH TẤN”", 46)},
    insight="Kinh Trung Bộ 26 ghi lời Đức Phật kể: Ngài đến thị trấn Senā thuộc vùng Ưu-lâu-tần-loa (Uruvelā), thấy khu rừng khả ái có dòng sông trong, bờ phẳng, gần làng để khất thực, nghĩ nơi này đủ để tinh tấn nên ngồi xuống ngay đó."),
 "bud137e_k7": dict(tags=["xa loi phat","a nan","vien tich","chia lia","tuong ung 47"], tags_vi=["Xá Lợi Phất", "A Nan", "viên tịch", "chia lìa", "Tương Ưng 47"], hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#chialìa", "#vôthường"],
    script={2: "A Nan thưa: thân con như bị mê dại, tâm trí rối bời.",
            4: "A Nan thưa không. Đức Phật nhắc: mọi điều thân yêu rồi cũng phải chia lìa.",
            5: "Lời dạy này gợi bạn nghĩ gì về sự chia lìa?"},
    cards={2: _big("THÂN NHƯ MÊ DẠI<br>TÂM TRÍ RỐI BỜI", 48),
           4: _big("MỌI ĐIỀU THÂN YÊU<br>RỒI PHẢI CHIA LÌA", 48)},
    source="Kinh Tương Ưng 47.13 (sn47.13:4.3–4.5, 5.1–5.2, 6.1–6.2), bản Bhikkhu Sujato (CC0): https://suttacentral.net/sn47.13/en/sujato — 'Venerable Sāriputta has become fully quenched. ... my body feels like it’s drugged. I’m disorientated, and the teachings don’t spring to mind.” “Well, Ānanda, when Sāriputta was fully quenched, did he take away your entire spectrum of ethical conduct, of immersion, of wisdom, of freedom, or of the knowledge and vision of freedom?” “No, sir, he did not.” ... we must be parted and separated from all we hold dear and beloved?'",
    insight="Kinh Tương Ưng 47.13: A Nan báo tin Xá Lợi Phất viên tịch, nói thân như mê dại, tâm trí rối bời. Đức Phật hỏi Xá Lợi Phất có mang đi giới, định, tuệ, giải thoát của ông không; A Nan thưa không. Ngài nhắc rằng mọi điều thân yêu rồi đều phải chia lìa.",
    cta="Khi một người thân thương rời xa, bạn nương vào điều gì để đứng vững?"),
 "bud137e_p4": dict(images=["cma_141682", "cma_135328", "cma_169269", "cma_140151"]),
 "bud137e_p5": dict(images=["034_Matsya", "007_Sasa", "040_Cave_1_Four_Deer", "Borobudur_Relief_Panel_0979"]),
 "bud137e_k8": dict(image="095_Anathapindaka", 
    script={1: "Kinh Tăng Chi dạy, dù lập cha mẹ làm vua tối cao trên cõi đất lớn này.",
            2: "Dù cho cha mẹ đủ bảy món báu trên cõi đất này.",
            4: "Nhưng giúp cha mẹ vững niềm tin, giới đức, bố thí, trí tuệ, là đã đền đáp đủ."},
    cards={2: _big("TRAO ĐỦ BẢY MÓN BÁU<br>TRÊN CÕI ĐẤT NÀY", 48),
           4: _big("VỮNG TIN, GIỚI, THÍ, TUỆ<br>MỚI LÀ ĐỀN ƠN ĐỦ", 46)},
    insight="Kinh Tăng Chi 2.33: dù lập cha mẹ làm vua tối cao trên cõi đất lớn, đủ bảy món báu, người con vẫn chưa đền đáp đủ; nhưng giúp cha mẹ vững niềm tin, giới đức, bố thí và trí tuệ thì đã đền đáp đủ."),
 "bud137e_k9": dict(
    insight="Kinh Tương Ưng 7.2 kể: Bà La Môn Bhāradvāja nổi giận mắng nhiếc Đức Phật. Ngài hỏi nếu khách không nhận món ăn dọn ra thì món ấy thuộc về ai; ông đáp thuộc về mình. Ngài nói Ngài không nhận lời mắng ấy, nên nó vẫn thuộc về chính người mắng."),
 "bud137e_p6": dict(images=["036_Mahisa_Jataka", "COLLECTIE_TROPENMUSEUM_Reliëf_Sutasoma", "COLLECTIE_TROPENMUSEUM_Reliëf_Mahisa", "008_Cave_1_In_the_Forest", "049_A_King_at_Court"]),
 "bud137e_d1": dict(images=["Seated_Buddha_Gandhara", "cma_143465", "cma_145208", "cma_147588"]),
 "bud137e_k10": dict(
    script={1: "Kinh Tiểu Tụng mở đầu bằng lời đảnh lễ Đức Phật.",
            2: "Con xin kính lễ Đức Thế Tôn, bậc Ứng Cúng.",
            3: "Bậc Chánh Đẳng Giác, bậc đã tự mình giác ngộ trọn vẹn.",
            4: "Theo sau là ba lời quy y: quy y Phật, quy y Pháp, quy y Tăng."},
    cards={1: _big("KINH TIỂU TỤNG MỞ ĐẦU<br>ĐẢNH LỄ ĐỨC PHẬT"),
           2: _big("KÍNH LỄ ĐỨC THẾ TÔN<br>BẬC ỨNG CÚNG", 48),
           3: _big("BẬC CHÁNH ĐẲNG GIÁC<br>GIÁC NGỘ TRỌN VẸN"),
           4: _big("QUY Y PHẬT<br>QUY Y PHÁP, QUY Y TĂNG")},
    insight="Kinh Tiểu Tụng 1 mở đầu bằng câu kính lễ Đức Thế Tôn, bậc Ứng Cúng, bậc Chánh Đẳng Giác (Namo Tassa Bhagavato Arahato Sammāsambuddhassa), rồi đến lời quy y Phật, Pháp, Tăng."),
 "bud137e_k11": dict(chip="KINH TỪ BI", 
    script={1: "Kinh Tập có bài kinh nguyện cho muôn loài hữu tình được hạnh phúc.",
            4: "Nguyện cho tất cả chúng sinh đều được hạnh phúc."},
    cards={1: _big("NGUYỆN CHO MUÔN LOÀI<br>ĐƯỢC HẠNH PHÚC"),
           2: _big("DÙ YẾU HAY MẠNH, LỚN HAY NHỎ<br>THẤY HAY KHÔNG THẤY", 44),
           3: _big("XA HAY GẦN<br>ĐÃ SINH HAY SẮP SINH"),
           4: _big("NGUYỆN CHO TẤT CẢ<br>ĐỀU ĐƯỢC HẠNH PHÚC", 48)},
    insight="Kinh Tập 1.8 (Kinh Từ Bi) nguyện cho tất cả chúng sinh được hạnh phúc, dù yếu hay mạnh, lớn hay nhỏ, thấy được hay không thấy được, ở xa hay gần, đã sinh ra hay sắp sinh ra."),
 "bud137e_d2": dict(
    images=["cma_94676", "cma_121206", "aic_103274", "cma_169269"],
    script={1: "Một, Chánh Kiến, tức là cái thấy đúng đắn.", 2: "Hai, Chánh Tư Duy, tức là tư duy đúng đắn.",
            3: "Ba, Chánh Ngữ, tức là lời nói đúng đắn.", 4: "Bốn, Chánh Nghiệp, tức là hành động đúng đắn.",
            5: "Kinh còn nêu Chánh Mạng, Chánh Tinh Tấn, Chánh Niệm và Chánh Định, bạn đang rèn nhánh nào?"},
    subtitles={0: "Cái thấy đúng", 1: "Tư duy đúng", 2: "Lời nói đúng", 3: "Hành động đúng"},
    insight="Kinh Tương Ưng 56.11 nêu tám chi của con đường: chánh kiến, chánh tư duy, chánh ngữ, chánh nghiệp, chánh mạng, chánh tinh tấn, chánh niệm và chánh định; bốn chi đầu là chánh kiến, chánh tư duy, chánh ngữ, chánh nghiệp."),
 "bud137e_d3": dict(tags=["nam mon qua lon","tu bo sat sinh","tang chi 8","loi phat day"], tags_vi=["năm món quà lớn", "từ bỏ sát sinh", "Tăng Chi 8", "lời Phật dạy"], hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#giớiđức", "#tăngchi"],
    images=["007_Sasa_Jataka", "034_Matsya", "073_A_King_with_Attendees", "049_A_King_at_Court", "095_Anathapindaka"],
    title="Năm món quà lớn mà đệ tử bậc thánh trao", chip="NĂM MÓN QUÀ LỚN TRONG KINH",
    head='NĂM MÓN QUÀ LỚN<br><span class="warm">KINH NÊU LÀ GÌ?</span>',
    script={0: "Năm món quà lớn trong kinh là gì?",
            1: "Kinh Tăng Chi nêu năm món quà lớn. Một, từ bỏ sát hại chúng sinh.",
            2: "Hai, từ bỏ trộm cắp.", 3: "Ba, từ bỏ tà hạnh trong dục.",
            4: "Bốn, từ bỏ nói dối.", 5: "Năm, từ bỏ rượu bia và chất say."},
    subtitles={0: "Không sát hại", 1: "Không trộm cắp", 2: "Không tà hạnh trong dục", 3: "Không nói dối", 4: "Không rượu bia, chất say"},
    insight="Kinh Tăng Chi 8.39 nêu năm món quà lớn nằm trong tám nguồn phước: từ bỏ sát sinh, trộm cắp, tà hạnh trong dục, nói dối, rượu bia và chất say; mỗi điều trao cho vô số chúng sinh sự không sợ hãi, thù oán.",
    cta="Trong năm điều ấy, điều nào bạn thấy cần giữ chắc nhất?"),
 "bud137e_k12": dict(tags_vi=["người thân đã khuất", "thân quyến", "Tiểu Tụng 7", "Tirokuṭṭa", "lời Phật dạy"],
    image="Bodhisattva_Padmapani",
    script={1: "Kinh Tiểu Tụng kể, người thân đã khuất đứng chờ ngoài tường, nơi ngã tư.",
            2: "Người có lòng thương dâng thân quyến thức ăn nước uống đúng lúc, sạch, ngon.",
            3: "Rồi nguyện: Mong phần này đến với thân quyến của chúng ta.",
            4: "Mong thân quyến của chúng ta được hạnh phúc.",
            5: "Hôm nay bạn muốn gửi lời nguyện nào cho người thân đã khuất?"},
    cards={1: _big("NGƯỜI THÂN ĐÃ KHUẤT<br>ĐỨNG CHỜ NGOÀI TƯỜNG"),
           2: _big("DÂNG THÂN QUYẾN ĐỒ ĂN UỐNG<br>ĐÚNG LÚC, SẠCH, NGON", 44),
           3: _big("“MONG PHẦN NÀY<br>ĐẾN VỚI THÂN QUYẾN”", 48),
           4: _big("MONG THÂN QUYẾN<br>ĐƯỢC HẠNH PHÚC", 48)},
    source="Kinh Tiểu Tụng 7 (kp7:1.1–1.2, 3.1–3.4, 4.1–4.2), bản Bhikkhu Sujato (CC0): https://suttacentral.net/kp7/en/sujato — 'Outside the walls they stand and wait, at the junctions and the crossroads. ... That’s why those who have compassion give to their relatives food and drink at the right time, that’s clean, delicious, and suitable. “May this be for our relatives! May our relatives be happy!”'",
    insight="Kinh Tiểu Tụng 7 (Tirokuṭṭa, Ngoài Bức Tường): người thân đã khuất đứng chờ ngoài tường, nơi ngã tư; người có lòng thương dâng thân quyến thức ăn nước uống đúng lúc, sạch, ngon, hợp; rồi nguyện: mong phần này đến với thân quyến, mong thân quyến được hạnh phúc.",
    cta="Bạn muốn gửi lời nguyện nào đến người thân đã khuất?"),
}

def _apply_fix137f():
    byid = {it["id"]: it for it in ITEMS}
    for rid, fx in FIX137F.items():
        it = byid[rid]
        for k, v in fx.items():
            if k == "images":
                it["images"] = [_C(x) for x in v]
            elif k == "image":
                it["image"] = _C(v)
            elif isinstance(v, dict):
                for i, x in v.items():
                    it[k][i] = x
            else:
                it[k] = v
_apply_fix137f()

for it in ITEMS:
    it["series"] = "bud"
    it["batch_id"] = BATCH_ID

# BGM assignment
BGM_MAP = {
    "bud137e_k5": "garden_music.mp3",
    "bud137e_p2": "peace_of_mind.mp3",
    "bud137e_p3": "white_lotus.mp3",
    "bud137e_k6": "that_zen_moment.mp3",
    "bud137e_k7": "wood_and_metal_and_water.mp3",
    "bud137e_p4": "ripples.mp3",
    "bud137e_p5": "starry.mp3",
    "bud137e_k8": "parting_of_the_ways_part_1.mp3",
    "bud137e_k9": "meditation_impromptu_01.mp3",
    "bud137e_p6": "garden_music.mp3",
    "bud137e_d1": "eastern_thought.mp3",
    "bud137e_k10": "white_lotus.mp3",
    "bud137e_k11": "peace_of_mind.mp3",
    "bud137e_d2": "that_zen_moment.mp3",
    "bud137e_d3": "wood_and_metal_and_water.mp3",
    "bud137e_k12": "shores_of_avalon.mp3",
}
for m in (R4, R5, R6):
    m.BGM.update(BGM_MAP)


# ------------------------------------------------------------------ IMAGE HELPER
# bbox chủ thể khai tay (x0, y0, x1, y1 theo tỉ lệ ảnh) cho ảnh nền không đồng màu
FOCUS = {
    "Buddha_in_Sarnath_Museum_Dhammajak_Mutra_.jpg": (0.02, 0.06, 0.98, 0.97),
    "Buddha_Tượng_Phật_Đồng_Dương_the_Museum_of_Vietnamese_History.jpg": (0.15, 0.05, 0.85, 0.97),
    "Amitabha_of_Phat_Tich_pagoda_reproduction_Bac_Ninh_province_1057_AD_DSC04838.jpg": (0.0, 0.12, 0.85, 0.97),
    "Seated_Buddha_Gandhara_Pakistan_Kushan_dynasty_100s-200s_AD_schist_-_Tokyo_National_Museum_-_Tokyo_Japan_-_DSC08664.jpg": (0.05, 0.03, 0.95, 0.97),
}
HEAD_TOP_PX = 440     # đầu/đỉnh chủ thể đặt tại đây: dưới dải title 0-260 và có khoảng thở
SUBJ_H_PX = 1200


def _auto_bbox(im: Image.Image):
    """Chủ thể trên nền phòng tranh đồng màu: so với nền ước lượng theo hàng."""
    sm = im.resize((400, max(1, int(400 * im.height / im.width))))
    a = np.asarray(sm).astype(float)
    h, w, _ = a.shape
    k = max(2, int(w * 0.04))
    bg = np.median(np.concatenate([a[:, :k], a[:, -k:]], 1), axis=1)[:, None, :]
    m = np.abs(a - bg).mean(2) > 30
    ys = np.where(m.sum(1) > w * 0.02)[0]
    xs = np.where(m.sum(0) > h * 0.02)[0]
    if len(ys) < 5 or len(xs) < 5:
        return None
    return xs[0] / w, ys[0] / h, (xs[-1] + 1) / w, (ys[-1] + 1) / h


def crop_to_vertical(im_path: Path) -> Image.Image:
    """Căn theo chủ thể: đầu/đỉnh tượng nằm tại HEAD_TOP_PX (dưới dải title 0-260).
    Ảnh tượng bảo tàng: dò bbox chủ thể; ảnh phù điêu/tranh: neo mép trên ảnh ở y=330.
    Phần trống phía trên/dưới được lấp bằng bản mờ của chính ảnh (vùng đó đã bị shade tối)."""
    im = Image.open(im_path).convert("RGB")
    W, H = im.size
    studio = im_path.name.startswith(("cma_", "aic_"))
    bb = FOCUS.get(im_path.name) or (_auto_bbox(im) if studio else None)
    if bb:
        x0, y0, x1, y1 = bb
        s = max(1080 / W, 1000 / ((y1 - y0) * H))
        top_img = y0 * H * s
        left_img = (x0 + x1) / 2 * W * s - 540
        yoff = HEAD_TOP_PX - top_img
    else:
        s = max(1080 / W, 1300 / H)
        left_img = (W * s - 1080) / 2
        yoff = 330
    sc = im.resize((round(W * s), round(H * s)), Image.Resampling.LANCZOS)
    left_img = round(max(0, min(sc.width - 1080, left_img)))
    piece = sc.crop((left_img, 0, left_img + 1080, sc.height))
    yoff = round(yoff)
    canvas = Image.new("RGB", (1080, 1920), (12, 10, 8))
    canvas.paste(piece, (0, yoff))
    if yoff > 0:   # lấp khoảng trống phía trên bằng hàng mép kéo giãn + mờ (vùng đã bị shade tối)
        strip = piece.crop((0, 0, 1080, 6)).resize((1080, yoff)).filter(ImageFilter.GaussianBlur(20))
        canvas.paste(strip, (0, 0))
    bot = yoff + piece.height
    if bot < 1920:
        strip = piece.crop((0, piece.height - 6, 1080, piece.height)).resize((1080, 1920 - bot)).filter(ImageFilter.GaussianBlur(20))
        canvas.paste(strip, (0, bot))
    im_crop = canvas

    mean_val = np.array(im_crop).mean()
    if mean_val < 70:
        factor = min(1.5, 95.0 / max(1.0, mean_val))
        return ImageEnhance.Brightness(im_crop).enhance(factor)
    elif mean_val < 90:
        return ImageEnhance.Brightness(im_crop).enhance(1.10)
    return im_crop


# ------------------------------------------------------------------ HTML BUILDERS
def build_html_control(it: dict, t: list[float], dur: float) -> str:
    """Đối chứng: Kể liền 1 cảnh, 1 tượng / tranh Ken Burns xuyên suốt 22-27s."""
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

    b64_imgs = [B.b64(crop_to_vertical(p)) for p in it["images"]]

    photos_html = []
    items_html = []
    for i in range(n_items):
        idx = i + 1
        num_str = f"0{idx}"
        kw = keywords[i]
        sub = subtitles[i]
        photos_html.append(f'<div class="photo-layer abs" id="photo_{idx}"><img src="{b64_imgs[i]}" alt="" /></div>')

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

    js = []
    js.append('tl.set("#photo_1", {opacity: 1});')

    for i in range(n_items):
        idx = i + 1
        s_time = t[idx]
        nxt_time = t[idx + 1] if (idx + 1) < len(t) else dur - 0.2

        # 137f: ảnh mới hiện nhanh (0.35s) đè lên ảnh cũ, ảnh cũ tắt sau đó -> không có đoạn nền tối giữa hai mục
        js.append(f'tl.fromTo("#photo_{idx}", {{scale: 1.0}}, {{scale: 1.04, duration: {nxt_time - s_time:.2f}, ease: "none"}}, {s_time});')
        if idx > 1:
            js.append(f'tl.fromTo("#photo_{idx}", {{opacity: 0}}, {{opacity: 1, duration: 0.35, ease: "power1.out"}}, {s_time});')
            js.append(f'tl.set("#photo_{idx - 1}", {{opacity: 0}}, {s_time + 0.36:.2f});')

        js.append(f'tl.fromTo("#sub_{idx}", {{opacity: 0, y: 15}}, {{opacity: 1, y: 0, duration: 0.4, ease: "power2.out"}}, {s_time + 0.2:.2f});')
        js.append(f'tl.to("#sub_{idx}", {{opacity: 0, duration: 0.3}}, {nxt_time - 0.3:.2f});')

        if formula == "M1":
            js.append(f'tl.fromTo("#num_{idx}", {{opacity: 0, y: 45}}, {{opacity: 1, y: 0, duration: 0.42, ease: "power2.out"}}, {s_time});')
            js.append(f'tl.to("#num_{idx}", {{opacity: 0, y: -25, duration: 0.3, ease: "power1.in"}}, {nxt_time - 0.3:.2f});')
            js.append(f'tl.fromTo("#kw_{idx}", {{opacity: 0, scale: 0.86, filter: "blur(8px)"}}, {{opacity: 1, scale: 1.0, filter: "blur(0px)", duration: 0.58, ease: "power2.out"}}, {s_time + 0.12:.2f});')
            js.append(f'tl.to("#kw_{idx}", {{opacity: 0, y: -40, duration: 0.42, ease: "power2.in"}}, {nxt_time - 0.42:.2f});')

        elif formula == "M2":
            js.append(f'tl.fromTo("#num_{idx}", {{opacity: 0, scale: 1.6}}, {{opacity: 1, scale: 1.0, duration: 0.38, ease: "back.out(1.8)"}}, {s_time});')
            js.append(f'tl.to("#num_{idx}", {{opacity: 0, duration: 0.25}}, {nxt_time - 0.25:.2f});')
            js.append(f'tl.fromTo("#kw_{idx}", {{opacity: 0, scale: 0.88, y: 18}}, {{opacity: 1, scale: 1.0, y: 0, duration: 0.42, ease: "power2.out"}}, {s_time + 0.1:.2f});')
            js.append(f'tl.fromTo("#kw_{idx} .shimmer-box", {{borderColor: "rgba(254,240,138,0.7)"}}, {{borderColor: "rgba(255,255,255,1)", duration: 0.45, yoyo: true, repeat: 1, ease: "sine.inOut"}}, {s_time + 0.6:.2f});')
            js.append(f'tl.to("#kw_{idx}", {{opacity: 0, duration: 0.3}}, {nxt_time - 0.3:.2f});')

        elif formula == "M3":
            js.append(f'tl.fromTo("#num_{idx}", {{opacity: 0, scale: 2.2, y: -45}}, {{opacity: 1, scale: 1.0, y: 0, duration: 0.35, ease: "power3.out"}}, {s_time});')
            js.append(f'tl.to("#num_{idx}", {{opacity: 0, scale: 0.8, duration: 0.25}}, {nxt_time - 0.25:.2f});')
            js.append(f'tl.fromTo("#kw_{idx}", {{opacity: 0, scale: 0.88}}, {{opacity: 1, scale: 1.0, duration: 0.42, ease: "expo.out"}}, {s_time + 0.15:.2f});')
            js.append(f'tl.to("#kw_{idx}", {{opacity: 0, scale: 1.08, duration: 0.32, ease: "power2.in"}}, {nxt_time - 0.32:.2f});')

        elif formula == "M4":
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
    """Tờ ảnh preview 137e: Khung 0, Khung giữa, Khung cuối 168px (so sánh độ tĩnh và chất lượng)."""
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

        header_text = f"{it['id']} ({it['arm'].upper()})\n{it['pair_id']}\n[{it.get('img_kind', '')}]\n{it['day']} {it['slot']}\n{it['title']}\n[{it.get('dur', 0)}s]"
        draw.text((pad, y + 20), header_text, fill=(245, 235, 220))

        frames = []
        f0 = OUT / f"_{rid}_f0.jpg"
        if mp4.exists():
            subprocess.run(["ffmpeg", "-y", "-ss", "0.05", "-i", str(mp4), "-vframes", "1", "-q:v", "3", str(f0)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        frames.append(f0 if f0.exists() else None)

        fmid = OUT / f"_{rid}_mid.jpg"
        if mp4.exists():
            mid_time = min(12.0, max(2.0, it.get("dur", 25.0) / 2.0))
            subprocess.run(["ffmpeg", "-y", "-ss", f"{mid_time:.2f}", "-i", str(mp4), "-vframes", "1", "-q:v", "3", str(fmid)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        frames.append(fmid if fmid.exists() else None)

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

    out_sheet = OUT / "preview_137e.jpg"
    sheet.save(out_sheet, quality=90)
    print(f"Đã xuất tờ ảnh preview: {out_sheet}")
    return out_sheet


# ------------------------------------------------------------------ PACKAGING
def export_packaging() -> None:
    PACKAGING_DIR.mkdir(parents=True, exist_ok=True)
    for it in ITEMS:
        pkg = {
            "insight": it["insight"],
            "tags": it["tags"],
            "tags_vi": it["tags_vi"],
            "hashtags": it["hashtags"],
            "cta": it["cta"],
            "day": it["day"],
            "slot": it["slot"],
            "style": "budpilot",
            "slot_vn": it["slot_vn"]
        }
        p = PACKAGING_DIR / f"{it['id']}.json"
        old = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
        p.write_text(json.dumps({**old, **pkg}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Đã xuất 16 file packaging vào {PACKAGING_DIR}")


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

        it["câu_0_dur"] = round(t[1] - t[0], 2)
        comp_name = f"_r_{rid}.html"
        (B.COMP / comp_name).write_text(html_content, encoding="utf-8")
        jobs.append((it, html_content))
        print(f"[{rid}] dur={it['dur']}s câu 0={it['câu_0_dur']:.2f}s đã lưu HTML {comp_name}")

    for it in ITEMS:
        rid = it["id"]
        if "dur" not in it:
            fin_file = D / f"{rid}_final.json"
            ren_file = OUT / f"{rid}.render.json"
            if fin_file.exists():
                it["dur"] = round(json.loads(fin_file.read_text(encoding="utf-8"))["duration_s"] + VOICE_DELAY + HOLD, 2)
            elif ren_file.exists():
                it["dur"] = json.loads(ren_file.read_text(encoding="utf-8")).get("duration_s", 25.0)

    all_in_band = all(21.0 <= it["dur"] <= 27.5 for it in ITEMS if "dur" in it)
    cau0_ok = all(it.get("câu_0_dur", 0.0) <= 2.50 for it in ITEMS if "câu_0_dur" in it)
    print(f"All in 21-27s band: {'ĐẠT' if all_in_band else 'LỖI'} ({[it.get('dur') for it in ITEMS if 'dur' in it]})")
    print(f"All câu 0 <= 2.5s: {'ĐẠT' if cau0_ok else 'LỖI'} ({[it.get('câu_0_dur') for it in ITEMS if 'câu_0_dur' in it]})")
    assert all_in_band, "Có video ngoài dải 21-27s!"
    assert cau0_ok, "Có câu 0 vượt quá 2.5s!"

    clean = {
        "id", "day", "slot", "lane", "arm", "formula", "pair_id", "hypothesis",
        "title", "script", "source", "series", "dur", "batch_id", "img_kind", "slot_vn"
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
    BUD_OUT.mkdir(parents=True, exist_ok=True)
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

        # Sync to bud/out/
        bud_mp4 = BUD_OUT / f"{rid}.mp4"
        shutil.copy2(mp4, bud_mp4)

        media_credits = [{"id": rid, "source": it["source"]}]
        if it["arm"] == "md":
            for idx_img, p in enumerate(it["images"]):
                media_credits.append({
                    "role": f"Mục {idx_img + 1}",
                    "file": p.name,
                    "license": "CC0 / Public Domain"
                })
        else:
            media_credits.append({
                "role": "Hình nền toàn bài",
                "file": it["image"].name,
                "license": "CC0 / Public Domain"
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
