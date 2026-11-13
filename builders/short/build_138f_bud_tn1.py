"""138f_bud_tn1_question_hook: 12 short BUD (6 thử có ? vs 6 đối chứng không ?) lane phap/niem phủ 09-15/11.

    .venv/bin/python output/cl_staging/grok/build_138f_bud_tn1.py [--html-only] [--only=id1,id2]
"""
from __future__ import annotations
from shortbuild import validate

import json
import statistics
import subprocess
import sys
from pathlib import Path
from PIL import Image

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
OUT = HERE / "render_138f"
PLAN = ROOT / "output/cl_staging/bud/plan_138f_bud_tn1.json"
HOLD = 3.05
VOICE_DELAY = 0.5
SUT = "https://suttacentral.net"
BASE = {"series": "bud", "replaces": None, "batch_id": "bud_tn1_1109"}
HYP = "TN1 138d: câu 1 có ? tăng stay proxy ≥5 điểm"


def big(s: str, fs: int = 54) -> str:
    return f'<div class="big warm" style="font-size:{fs}px">{s}</div>'


def sub(s: str) -> str:
    return f'<div class="sub">{s}</div>'


ITEMS = [
    # ---------------- Pair 1 (phap): Giận dữ & Oán hờn ----------------
    dict(
        id="bud_tn1_01q", pair_id="pair_1", hook_type="question", day="2026-11-09", slot="08:00",
        lane="phap", sid="statue_gandhara_01", kind="phap", acc=("#f2b48a", "#2b1407"),
        title="Giết thứ gì thì đêm về ngủ yên?", chip="LỜI PHẬT · KINH TƯƠNG ƯNG", srcline="TƯƠNG ƯNG 1.71",
        head='GIẾT THỨ GÌ THÌ<br><span class="warm">ĐÊM VỀ NGỦ YÊN?</span>',
        script=[
            "Giết thứ gì thì đêm về ngủ yên, không còn sầu muộn?",
            "Kinh Tương Ưng một chấm bảy mốt, vị trời đến hỏi Đức Phật.",
            "Ngài đáp: **giết cơn giận** thì ngủ yên, không còn sầu khổ.",
            "Cơn giận có **gốc rễ độc**, nhưng ngọn lại ngọt ngào.",
            "Bậc trí diệt trừ cơn giận, vì **dứt nó là dứt khổ**.",
            "Đêm nay, bạn có đang để cơn giận giữ mình thức trắng?"
        ],
        cards=[
            None,
            big("VỊ TRỜI ĐẾN HỎI<br>ĐỨC PHẬT", 50),
            sub("Tương Ưng 1.71") + big("GIẾT CƠN GIẬN<br>THÌ NGỦ YÊN", 54),
            big("CƠN GIẬN GỐC ĐỘC<br>NGỌN NGỌT NGÀO", 50),
            big("DỨT CƠN GIẬN<br>LÀ DỨT KHỔ", 54),
            None
        ],
        source=f"Kinh Tương Ưng 1.71 (sn1.71:1.1–3.6), bản Bhikkhu Sujato (CC0): {SUT}/sn1.71/en/sujato — 'When what is slain do you sleep at ease? When what is slain is there no sorrow? … When anger’s slain you sleep at ease. When anger’s slain there is no sorrow. Anger has a poisonous root and a sweet tip, O deity. The noble ones praise its killing, for when it’s slain there is no sorrow.' Pali: Kodhaṁ vadhitvā sukhaṁ seti, kodhaṁ vadhitvā na socati; Kodhassa visamūlassa, madhuraggassa devate; Vadhaṁ ariyā pasaṁsanti, tañhi vadhitvā na socatīti."
    ),
    dict(
        id="bud_tn1_01s", pair_id="pair_1", hook_type="statement", day="2026-11-10", slot="08:00",
        lane="phap", sid="statue_gandhara_07", kind="phap", acc=("#f2b48a", "#2b1407"),
        title="Hận thù không bao giờ dập tắt được hận thù", chip="LỜI PHẬT · KINH PHÁP CÚ", srcline="PHÁP CÚ 5",
        head='HẬN THÙ KHÔNG THỂ<br><span class="warm">DẬP TẮT HẬN THÙ</span>',
        script=[
            "Hận thù không bao giờ dập tắt được hận thù ở cõi đời này.",
            "Kinh Pháp Cú câu năm ghi rõ lời Đức Phật chỉ dạy.",
            "Lấy oán báo oán, **oán hận chất chồng** không dứt.",
            "Chỉ có **lòng từ bi** mới dập tắt được oán hờn.",
            "Đây là **định luật ngàn thu** muôn đời không thay đổi.",
            "Hôm nay, bạn chọn nuôi oán hờn hay buông xuống bằng từ bi?"
        ],
        cards=[
            None,
            sub("Kinh Pháp Cú 5") + big("LỜI ĐỨC PHẬT DẠY<br>VỀ OÁN HẬN", 50),
            big("LẤY OÁN BÁO OÁN<br>CHẤT CHỒNG MÃI", 52),
            big("CHỈ CÓ TỪ BI<br>MỚI DẬP TẮT OÁN", 52),
            big("ĐỊNH LUẬT NGÀN THU<br>KHÔNG THAY ĐỔI", 48),
            None
        ],
        source=f"Kinh Pháp Cú 5 (dhp5:1–4), bản Bhikkhu Sujato (CC0): {SUT}/dhp1-20/en/sujato — 'For never is hatred laid to rest by hate, it’s laid to rest by love: this is an ancient teaching.' Pali: Na hi verena verāni, sammantīdha kudācanaṁ; Averena ca sammanti, esa dhammo sanantano."
    ),

    # ---------------- Pair 2 (phap): Của cải & Sáng tối ----------------
    dict(
        id="bud_tn1_02q", pair_id="pair_2", hook_type="question", day="2026-11-11", slot="08:00",
        lane="phap", sid="statue_india_01", kind="phap", acc=("#f4cf6b", "#2a1a05"),
        title="Bốn niềm an lạc lớn nhất của người kiếm ra tiền là gì?", chip="LỜI PHẬT · KINH TĂNG CHI", srcline="TĂNG CHI 4.62 · KHÔNG NỢ",
        head='KIẾM RA TIỀN CHÂN CHÍNH,<br><span class="warm">4 NIỀM AN LẠC LÀ GÌ?</span>',
        script=[
            "Kiếm ra tiền chân chính, người cư sĩ có bốn niềm vui lớn là gì?",
            "Kinh Tăng Chi bốn chấm sáu mươi hai chỉ rõ.",
            "Thứ nhất là **tự có tài sản** bằng mồ hôi của mình.",
            "Thứ hai là **hưởng dụng của cải**, thứ ba là **không nợ nần ai**.",
            "Nhưng lớn nhất là sống thanh sạch, **không lỗi lầm**.",
            "Trong bốn niềm vui này, bạn đang có mấy điều?"
        ],
        cards=[
            None,
            sub("Tăng Chi 4.62") + big("ĐỨC PHẬT CHỈ RÕ<br>4 NIỀM AN LẠC", 50),
            big("TỰ LÀM RA TÀI SẢN<br>BẰNG MỒ HÔI", 50),
            big("HƯỞNG DỤNG CỦA CẢI<br>KHÔNG NỢ NẦN AI", 48),
            big("SỐNG ĐỜI THANH SẠCH<br>KHÔNG LỖI LẦM", 48),
            None
        ],
        source=f"Kinh Tăng Chi 4.62, Kinh Không Nợ (an4.62:2.1–8.4), bản Bhikkhu Sujato (CC0): {SUT}/an4.62/en/sujato — 'The happiness of ownership, using wealth, debtlessness, and blamelessness.' 'Discerning clearly, a clever person knows both kinds of happiness: the other kind is not worth a sixteenth part of the happiness of blamelessness.' Pali: atthisukha, bhogasukha, anaṇasukha, anavajjasukha."
    ),
    dict(
        id="bud_tn1_02s", pair_id="pair_2", hook_type="statement", day="2026-11-12", slot="08:00",
        lane="phap", sid="statue_india_05", kind="phap", acc=("#f4cf6b", "#2a1a05"),
        title="Bốn con đường sáng tối của đời người", chip="LỜI PHẬT · KINH TĂNG CHI", srcline="TĂNG CHI 4.85",
        head='BỐN CON ĐƯỜNG<br><span class="warm">SÁNG TỐI Ở ĐỜI</span>',
        script=[
            "Đời người luôn có bốn lối đi giữa bóng tối và ánh sáng.",
            "Kinh Tăng Chi bốn chấm tám mươi lăm phân biệt rõ ràng.",
            "Hạng **từ tối vào tối**, và hạng **từ tối ra sáng**.",
            "Hạng **từ sáng vào tối**, và hạng **từ sáng ra sáng**.",
            "Dù khó khăn, làm việc lành thì **tương lai bừng sáng**.",
            "Hôm nay, bạn đang bước về phía ánh sáng nào?"
        ],
        cards=[
            None,
            sub("Kinh Tăng Chi 4.85") + big("BỐN HẠNG NGƯỜI<br>TRONG CÕI ĐỜI", 52),
            big("TỪ TỐI VÀO TỐI<br>TỪ TỐI RA SÁNG", 50),
            big("TỪ SÁNG VÀO TỐI<br>TỪ SÁNG RA SÁNG", 50),
            big("HÀNH ĐIỀU LÀNH<br>TƯƠNG LAI BỪNG SÁNG", 48),
            None
        ],
        source=f"Kinh Tăng Chi 4.85 (an4.85:1.1–5.7), bản Bhikkhu Sujato (CC0): {SUT}/an4.85/en/sujato — 'these four individuals are found in the world. The dark bound for darkness, the dark bound for light, the light bound for darkness, and the light bound for light.' 'they do good things by way of body, speech, and mind. When their body breaks up, after death, they’re reborn in a good place, a heavenly realm. That’s how an individual is dark and bound for light.'"
    ),

    # ---------------- Pair 3 (phap): Già chết & Cung kính ----------------
    dict(
        id="bud_tn1_03q", pair_id="pair_3", hook_type="question", day="2026-11-13", slot="08:00",
        lane="phap", sid="statue_china_01", kind="phap", acc=("#9fd3c7", "#0b2420"),
        title="Bốn ngọn núi già chết đang ập đến, ta phải làm gì?", chip="LỜI PHẬT · KINH TƯƠNG ƯNG", srcline="TƯƠNG ƯNG 3.25 · NÚI ĐÁ",
        head='NÚI GIÀ CHẾT ĐANG TỚI,<br><span class="warm">ĐỨC PHẬT DẠY LÀM GÌ?</span>',
        script=[
            "Nếu bốn ngọn núi già và chết đang lăn tới, bạn sẽ làm gì?",
            "Kinh Tương Ưng ba chấm hai mươi lăm, Đức Phật hỏi vua Ba-tư-nặc.",
            "Nhà vua thưa: lúc ấy con chỉ biết **sống đúng chánh pháp**.",
            "Đức Phật dạy: **già và chết** đang ập đến như thế, chớ buông lung.",
            "Hôm nay, bạn đã chuẩn bị hành trang lành nào cho mình?"
        ],
        cards=[
            None,
            sub("Tương Ưng 3.25") + big("ĐỨC PHẬT HỎI VUA<br>BA TƯ NẶC", 50),
            big("CHỈ CÒN BIẾT SỐNG<br>ĐÚNG CHÁNH PHÁP", 50),
            big("GIÀ CHẾT ĐANG TỚI<br>CHỚ CÓ BUÔNG LUNG", 48),
            None
        ],
        source=f"Kinh Tương Ưng 3.25, Kinh Núi Đá (sn3.25:2.1–5.4), bản Bhikkhu Sujato (CC0): {SUT}/sn3.25/en/sujato — 'Since old age and death are advancing upon you, what would you do? What else can I do, sir, except practice the teaching, practice morality, and do good and skillful deeds?' 'I declare to you, great king, I make known to you: old age and death are advancing upon you. Since old age and death are advancing upon you, what will you do?'"
    ),
    dict(
        id="bud_tn1_03s", pair_id="pair_3", hook_type="statement", day="2026-11-15", slot="08:00",
        lane="phap", sid="statue_china_03", kind="phap", acc=("#9fd3c7", "#0b2420"),
        title="Bốn phước lành lớn của người biết kính trên nhường dưới", chip="LỜI PHẬT · KINH PHÁP CÚ", srcline="PHÁP CÚ 109",
        head='BỐN PHƯỚC LÀNH LỚN<br><span class="warm">KHI BIẾT CUNG KÍNH</span>',
        script=[
            "Người biết cung kính bậc trưởng thượng luôn nhận được bốn phước lành.",
            "Kinh Pháp Cú một trăm lẻ chín ghi rõ lời Phật dạy.",
            "Thứ nhất là **tăng tuổi thọ**, thứ hai là **sắc diện tươi nhuận**.",
            "Thứ ba là **tâm an lạc**, và thứ tư là **sức mạnh nội tâm**.",
            "Tâm khiêm kính luôn mang lại **phước báu bền lâu**.",
            "Hôm nay, bạn đã gửi lời chào kính trọng đến ai?"
        ],
        cards=[
            None,
            sub("Kinh Pháp Cú 109") + big("LỜI ĐỨC PHẬT DẠY<br>VỀ SỰ CUNG KÍNH", 48),
            big("TĂNG TUỔI THỌ<br>SẮC DIỆN TƯƠI NHUẬN", 50),
            big("TÂM ĐƯỢC AN LẠC<br>TĂNG THÊM SỨC MẠNH", 48),
            big("TÂM KHIÊM HẠ<br>PHƯỚC BÁU BỀN LÂU", 50),
            None
        ],
        source=f"Kinh Pháp Cú 109 (dhp109:1–4), bản Bhikkhu Sujato (CC0): {SUT}/dhp100-115/en/sujato — 'For one in the habit of bowing, always honoring the elders, four blessings grow: lifespan, beauty, happiness, and strength.' Pali: Abhivādanasīlissa, niccaṁ vuḍḍhāpacāyino; Cattāro dhammā vaḍḍhanti, āyu vaṇṇo sukhaṁ balaṁ."
    ),

    # ---------------- Pair 4 (niem): Quán hơi thở ----------------
    dict(
        id="bud_tn1_04q", pair_id="pair_4", hook_type="question", day="2026-11-09", slot="12:30",
        lane="niem", sid="statue_gandhara_05", kind="niem", acc=("#c9b8ff", "#1c1236"),
        title="Thở vào thở ra thế nào để tâm bình an trở lại?", chip="THỰC HÀNH · QUÁN HƠI THỞ", srcline="TRUNG BỘ 118 · NHẬP TỨC XUẤT TỨC",
        head='THỞ THẾ NÀO ĐỂ<br><span class="warm">TÂM AN TRỞ LẠI?</span>',
        script=[
            "Thở vào thở ra như thế nào để tâm đang rối loạn bình an trở lại?",
            "Kinh Trung Bộ một trăm mười tám dạy phép quán niệm hơi thở.",
            "Thở vào một hơi thật sâu, **biết mình đang thở vào**.",
            "Thở ra một hơi thật nhẹ, **biết mình đang thở ra**.",
            "Không nghĩ chuyện ngày mai, chỉ gom trọn tâm về **ngay giây phút này**.",
            "Ngay lúc này, hơi thở của bạn đang nông hay sâu?"
        ],
        cards=[
            None,
            sub("Trung Bộ 118") + big("PHÉP QUÁN NIỆM<br>HƠI THỞ TỰ NHIÊN", 50),
            big("THỞ VÀO BIẾT VÀO<br>THẬT TỰ NHIÊN", 50),
            big("THỞ RA BIẾT RA<br>BUÔNG LỎNG THÂN", 50),
            big("GOM TRỌN TÂM VỀ<br>GIÂY PHÚT NÀY", 52),
            None
        ],
        source=f"Kinh Trung Bộ 118, Quán Niệm Hơi Thở (mn118:17.1–18.4), bản Bhikkhu Sujato (CC0): {SUT}/mn118/en/sujato — 'Breathing in heavily they know: “I’m breathing in heavily.” Breathing out heavily they know: “I’m breathing out heavily.” Breathing in lightly they know … Always mindful they breathe in, mindful they breathe out.'"
    ),
    dict(
        id="bud_tn1_04s", pair_id="pair_4", hook_type="statement", day="2026-11-11", slot="12:30",
        lane="niem", sid="statue_gandhara_06", kind="niem", acc=("#c9b8ff", "#1c1236"),
        title="Theo dõi hơi thở vào ra giúp lắng dịu thân tâm", chip="THỰC HÀNH · QUÁN HƠI THỞ", srcline="TRUNG BỘ 118 · NHẬP TỨC XUẤT TỨC",
        head='THEO DÕI HƠI THỞ<br><span class="warm">GIÚP LẮNG DỊU THÂN TÂM</span>',
        script=[
            "Theo dõi hơi thở vào ra giúp lắng dịu toàn bộ thân tâm.",
            "Kinh Trung Bộ một trăm mười tám dạy rõ từng bước.",
            "Thở vào cảm nhận toàn thân, **thở ra làm an tịnh thân thể**.",
            "Nhẹ nhàng **đưa tâm trở về với hơi thở**.",
            "Tâm dần buông bỏ **mọi căng thẳng và lo âu**.",
            "Hôm nay, bạn đã dành phút nào để lắng dịu thân tâm?"
        ],
        cards=[
            None,
            sub("Trung Bộ 118") + big("TỪNG BƯỚC THỰC HÀNH<br>QUÁN HƠI THỞ", 48),
            big("THỞ VÀO BIẾT RÕ<br>CẢM GIÁC TOÀN THÂN", 48),
            big("ĐƯA TÂM TRỞ VỀ<br>VỚI TỪNG NHỊP THỞ", 48),
            big("BUÔNG BỎ CĂNG THẲNG<br>LẮNG DỊU LO ÂU", 48),
            None
        ],
        source=f"Kinh Trung Bộ 118, Quán Niệm Hơi Thở (mn118:18.1–24.4), bản Bhikkhu Sujato (CC0): {SUT}/mn118/en/sujato — '“Experiencing the whole body I will breathe in”, they practice like this. “Experiencing the whole body I will breathe out”, they practice like this. “Calming the body’s motion I will breathe in” … “Calming the body’s motion I will breathe out”.'"
    ),

    # ---------------- Pair 5 (niem): Từ tâm & Quán tâm như đất ----------------
    dict(
        id="bud_tn1_05q", pair_id="pair_5", hook_type="question", day="2026-11-13", slot="12:30",
        lane="niem", sid="statue_vietnam_01", kind="niem", acc=("#f4cf6b", "#2a1a05"),
        title="Nuôi dưỡng lòng từ bi mang lại những lợi ích gì?", chip="THỰC HÀNH · QUÁN TỪ BI", srcline="TĂNG CHI 11.15 · TỪ TÂM",
        head='LÒNG TỪ BI MANG LẠI<br><span class="warm">NHỮNG LỢI ÍCH GÌ?</span>',
        script=[
            "Nuôi dưỡng lòng từ bi mang lại những lợi ích lớn gì?",
            "Kinh Tăng Chi mười một chấm mười lăm kể ra mười một điều an lành.",
            "Ngủ được an yên, **thức dậy nhẹ nhõm**, không gặp ác mộng.",
            "Được mọi người yêu mến, **chư thiên bảo bọc chở che**.",
            "**Tâm dễ định tĩnh**, nét mặt luôn tươi sáng rạng rỡ.",
            "Hôm nay, bạn đã gửi lời chúc an lành đến ai chưa?"
        ],
        cards=[
            None,
            sub("Tăng Chi 11.15") + big("MƯỜI MỘT ĐIỀU LÀNH<br>CỦA TÂM TỪ", 48),
            big("NGỦ AN THỨC VUI<br>KHÔNG ÁC MỘNG", 50),
            big("ĐƯỢC YÊU QUÝ<br>CHƯ THIÊN BẢO BỌC", 50),
            big("TÂM TRÍ ĐỊNH TĨNH<br>NÉT MẶT TƯƠI SÁNG", 48),
            None
        ],
        source=f"Kinh Tăng Chi 11.15, Lợi Ích Của Từ Tâm (an11.15:1.1–2.3), bản Bhikkhu Sujato (CC0): {SUT}/an11.15/en/sujato — 'You can expect eleven benefits when the heart’s release by love has been cultivated … You sleep at ease. You wake happily. You don’t have bad dreams. Humans love you. Non-humans love you. Deities protect you … Your mind quickly enters immersion. Your face is clear and bright.'"
    ),
    dict(
        id="bud_tn1_05s", pair_id="pair_5", hook_type="statement", day="2026-11-15", slot="12:30",
        lane="niem", sid="statue_vietnam_07", kind="niem", acc=("#f4cf6b", "#2a1a05"),
        title="Tập tâm bao dung như đất trước mọi khen chê ở đời", chip="THỰC HÀNH · QUÁN TÂM", srcline="TRUNG BỘ 62 · ĐẠI LA HẦU LA",
        head='TẬP TÂM NHƯ ĐẤT<br><span class="warm">TRƯỚC MỌI KHEN CHÊ</span>',
        script=[
            "Đức Phật dạy La Hầu La hãy rèn luyện tâm mình vững vàng như đất.",
            "Kinh Trung Bộ sáu mươi hai ghi lại lời dạy thâm sâu này.",
            "Dù người ta đổ hoa thơm hay đồ dơ bẩn, **đất không giận không mừng**.",
            "Giữ tâm như đất, thì **lời khen tiếng chê** không làm ta chao đảo.",
            "Không bám víu điều vừa ý, **chẳng buồn bực điều trái tai**.",
            "Trước lời khen chê hôm nay, tâm bạn đã vững vàng như đất chưa?"
        ],
        cards=[
            None,
            sub("Kinh Trung Bộ 62") + big("LỜI PHẬT DẠY<br>NGÀI LA HẦU LA", 50),
            big("ĐỔ HOA HAY RÁC<br>ĐẤT KHÔNG GIẬN MỪNG", 48),
            big("KHEN CHÊ Ở ĐỜI<br>KHÔNG THỂ DAO ĐỘNG", 48),
            big("KHÔNG BÁM VÍU<br>CHẲNG BUỒN GIẬN", 52),
            None
        ],
        source=f"Kinh Trung Bộ 62, Đại Giáo Giới La-hầu-la (mn62:13.1–13.5), bản Bhikkhu Sujato (CC0): {SUT}/mn62/en/sujato — 'Rāhula, meditate like the earth. For when you meditate like the earth, pleasant and unpleasant contacts will not occupy your mind. Suppose they were to dump clean or dirty things on the earth … the earth is not repulsed, humiliated, or disgusted. In the same way, meditate like the earth.'"
    ),

    # ---------------- Pair 6 (niem): Niệm chết & Niệm Phật ----------------
    dict(
        id="bud_tn1_06q", pair_id="pair_6", hook_type="question", day="2026-11-14", slot="23:00",
        lane="niem", sid="statue_japan_01", kind="niem", acc=("#f2b48a", "#2b1407"),
        title="Đời người ngắn ngủi trong bao lâu theo lời Phật dạy?", chip="THỰC HÀNH · QUÁN NIỆM", srcline="TĂNG CHI 6.19 · NIỆM SỰ CHẾT",
        head='ĐỜI NGƯỜI NGẮN NGỦI<br><span class="warm">TRONG BAO LÂU?</span>',
        script=[
            "Đời người ngắn ngủi trong bao lâu theo lời Đức Phật dạy?",
            "Kinh Tăng Chi sáu chấm mười chín ghi cuộc đối thoại sâu sắc.",
            "Có vị nghĩ một ngày, có vị nghĩ bằng **bữa ăn cơm**.",
            "Nhưng Phật dạy: mạng sống mong manh trong **một hơi thở**.",
            "Thở ra không thở vào là sang đời khác, **chớ buông lung**.",
            "Nhớ mạng người mong manh, bạn sẽ sống hôm nay thế nào?"
        ],
        cards=[
            None,
            sub("Tăng Chi 6.19") + big("ĐỨC PHẬT HỎI CÁC SƯ<br>VỀ MẠNG SỐNG", 48),
            big("MỘT NGÀY ĐÊM HAY<br>MỘT BỮA ĂN?", 50),
            big("CHỈ MONG MANH TRONG<br>MỘT HƠI THỞ", 50),
            big("THỞ RA KHÔNG VÀO<br>LÀ SANG ĐỜI KHÁC", 48),
            None
        ],
        source=f"Kinh Tăng Chi 6.19, Niệm Sự Chết (an6.19:1.6–16.3), bản Bhikkhu Sujato (CC0): {SUT}/an6.19/en/sujato — '‘Oh, if I’d only live as long as it takes to breathe out after breathing in, or to breathe in after breathing out, I’d focus on the Buddha’s instructions’ … these are called mendicants who live diligently. They keenly develop mindfulness of death for the ending of defilements.'"
    ),
    dict(
        id="bud_tn1_06s", pair_id="pair_6", hook_type="statement", day="2026-11-15", slot="23:00",
        lane="niem", sid="statue_japan_02", kind="niem", acc=("#f2b48a", "#2b1407"),
        title="Niệm tưởng ân đức Phật giúp gạn đục khơi trong tâm trí", chip="THỰC HÀNH · NIỆM PHẬT", srcline="TĂNG CHI 6.10 · MAHANAMA",
        head='NIỆM ÂN ĐỨC PHẬT<br><span class="warm">GIÚP TÂM THANH TỊNH</span>',
        script=[
            "Niệm ân đức Phật giúp tâm gột sạch tham sân và tìm lại an tĩnh.",
            "Kinh Tăng Chi sáu chấm mười dạy cư sĩ cách an trú tâm.",
            "Nhớ đến bậc Giác Ngộ, **tâm không còn bị tham sân trói buộc**.",
            "Hướng về điều thiện lành, **niềm hoan hỷ tự nhiên khởi sinh**.",
            "Từ hoan hỷ sinh an tịnh, giúp ta **bình thản giữa dòng đời**.",
            "Hôm nay, bạn đã dành phút nào để hướng tâm về tĩnh tại?"
        ],
        cards=[
            None,
            sub("Kinh Tăng Chi 6.10") + big("LỜI DẠY CƯ SĨ<br>CÁCH AN TRÚ TÂM", 50),
            big("KHÔNG BỊ THAM SÂN<br>TRÓI BUỘC TÂM", 48),
            big("LÒNG HƯỚNG ĐIỀU LÀNH<br>HOAN HỶ KHỞI SINH", 48),
            big("TÂM TRÍ AN TỊNH<br>BÌNH THẢN GIỮA ĐỜI", 50),
            None
        ],
        source=f"Kinh Tăng Chi 6.10, Kinh Mahānāma (an6.10:2.1–2.9), bản Bhikkhu Sujato (CC0): {SUT}/an6.10/en/sujato — 'When a noble disciple recollects the Realized One their mind is not full of greed, hate, and delusion. At that time their mind is unswerving, based on the Realized One … joy springs up. In someone who is joyful, rapture springs up. In someone with a rapturous mind, the body becomes tranquil. When the body is tranquil, one feels bliss.'"
    ),
]

for it in ITEMS:
    it.update(BASE)
    it["test_cell"] = "TN1_" + it["hook_type"]
    it["style"] = "statue_cards"
    it["narrative_structure"] = "cau_hoi_cu_the_lat_nguon_vong_lap" if it["hook_type"] == "question" else "cau_khang_dinh_lat_nguon_vong_lap"
    it["hypothesis"] = HYP
    it["format_subtag"] = "phap_loi_phat" if it["lane"] == "phap" else "niem_quan_niem"
    it["novelty_ok"] = "đã kiểm tra qua hf_novelty, không trùng"
    it["img_kind"] = "statue_real"

# Setup images and cards in R5 dictionaries
for it in ITEMS:
    R5.IMG[it["id"]] = (R5.bank_path(it["sid"]), 250, 0.92)
    s = next(x for x in json.loads((ROOT / "output/cl_staging/bud/banks/statues.json").read_text(encoding="utf-8")) if x["id"] == it["sid"])
    R5.CREDITS[it["id"]] = (f"{s['title']} — {s.get('author') or 'Wikimedia Commons'}, {s['license']}", f"{s['title']} · {s['license']}", s["license"])
    R5.CARDS[it["id"]] = it["cards"]
    R5.HEAD[it["id"]] = (it["chip"], it["head"], it["srcline"])
    R5.ACCENT[it["id"]] = it["acc"]
    R5.LISTS.update({})

# Pick BGM using shared library
for it in ITEMS:
    hf_music.short_pick(it)
BGM = {it["id"]: json.loads((ROOT / "output/cl_staging/bud/bgm_shorts.json").read_text())[it["id"]]["file"] for it in ITEMS}
for m in (R4, R5, R6):
    m.BGM.update(BGM)


def library_motion(h: str) -> str:
    h = h.replace('{opacity: 0, y: 26, filter: "blur(8px)"}', '{opacity: 0, y: 26}').replace('filter: "blur(0px)", ', "")
    return h.replace('ease: "power2.out"}, at)', 'ease: "expo.out"}, at)')


def main() -> int:
    html_only = "--html-only" in sys.argv
    only = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)

    R6.guards(ITEMS)
    for it in ITEMS:
        fin_json = json.loads((D / f"{it['id']}_final.json").read_text(encoding="utf-8"))
        it["dur"] = round(fin_json["duration_s"] + VOICE_DELAY + HOLD, 2)

    jobs = []
    print("=== TTS & HTML BUILD ===")
    for it in ITEMS:
        if only and it["id"] not in only:
            continue
        R6.tts(it, (0.45, 0.55))
        t = R5.segs(it["id"], VOICE_DELAY)
        h = library_motion(R5.html_statue(it["id"], t, it["dur"]))
        jobs.append((it, h))

    # Duration stats check
    dur_q = [it["dur"] for it in ITEMS if it["hook_type"] == "question"]
    dur_s = [it["dur"] for it in ITEMS if it["hook_type"] == "statement"]
    med_q = statistics.median(dur_q)
    med_s = statistics.median(dur_s)
    diff = abs(med_q - med_s)
    print(f"Durations Question (THỬ): {dur_q} (median={med_q:.2f}s)")
    print(f"Durations Statement (ĐỐI CHỨNG): {dur_s} (median={med_s:.2f}s)")
    print(f"Median diff: {diff:.2f}s (chuẩn < 3s: {'ĐẠT' if diff < 3.0 else 'LỆCH'})")
    all_in_band = all(21.0 <= it["dur"] <= 27.0 for it in ITEMS)
    print(f"All in 21-27s band: {'ĐẠT' if all_in_band else 'LỖI'}")

    clean = {
        "id", "pair_id", "day", "slot", "replaces", "lane", "test_cell", "style", "title",
        "script", "source", "series", "dur", "batch_id", "hook_type", "narrative_structure",
        "hypothesis", "format_subtag", "novelty_ok", "img_kind"
    }
    plan = []
    for it in ITEMS:
        p = {k: it[k] for k in clean if k in it}
        p["media_credit"] = R5.CREDITS[it["id"]][0]
        p["image"] = it["sid"]
        plan.append(p)
    validate(plan)
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    for it, h in jobs:
        (B.COMP / f"_r_{it['id']}.html").write_text(h, encoding="utf-8")
        print(f"[{it['id']}] dur={it['dur']}s saved HTML")

    if html_only:
        return 0

    OUT.mkdir(parents=True, exist_ok=True)
    print("=== RENDER & AUDIO MIX ===")
    for it, _ in jobs:
        rid = it["id"]
        if only and rid not in only:
            continue
        silent, mp4 = D / f"{rid}_silent.mp4", OUT / f"{rid}.mp4"
        B.to_trash(silent)
        B.to_trash(mp4)
        print(f"[{rid}] render silent mp4 ...", flush=True)
        R4.render(f"_r_{rid}.html", silent)
        print(f"[{rid}] mix audio ...", flush=True)
        vl, gain, ml = R4.mix(rid, silent, D / f"{rid}_final.wav", mp4, it["dur"], VOICE_DELAY, True)
        B.to_trash(silent)
        meta = {
            "ok": True, "output": str(mp4.relative_to(ROOT)), "duration_s": it["dur"],
            "style": it["style"], "lane": it["lane"], "pair_id": it["pair_id"],
            "hook_type": it["hook_type"], "batch_id": it["batch_id"],
            "img_kind": it["img_kind"],
            "bgm": f"bgm/{BGM[rid]}", "bgm_title": hf_music.TITLES[BGM[rid]], "bgm_gain": round(gain, 4),
            "media_credits": [{"id": rid, "kind": "commons", "credit": R5.CREDITS[rid][0]}],
            "voice": "Binh", "lufs": {"voice": round(vl, 1), "mix": round(ml, 1), "offset_db": -20.0},
            "sfx_credit": B.BELL_CREDIT
        }
        (OUT / f"{rid}.render.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{rid}] xong | LUFS giọng {vl:.1f} mix {ml:.1f}", flush=True)

    make_preview_sheet()
    return 0


def make_preview_sheet() -> None:
    """Tờ ảnh mới 12 bài (khung 0 + khung giữa) theo PO 04/11."""
    frames_dir = OUT / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    print("=== MAKE PREVIEW SHEET (12 bài: khung 0 + khung giữa) ===")

    pairs = {}
    for it in ITEMS:
        rid = it["id"]
        mp4 = OUT / f"{rid}.mp4"
        if not mp4.exists():
            print(f"Warning: {mp4} does not exist, skipping frame extraction")
            continue
        fin_json = json.loads((D / f"{rid}_final.json").read_text(encoding="utf-8"))
        dur = round(fin_json["duration_s"] + VOICE_DELAY + HOLD, 2)
        mid_t = dur / 2.0

        f0 = frames_dir / f"{rid}_f0.jpg"
        fmid = frames_dir / f"{rid}_fmid.jpg"
        flast = frames_dir / f"{rid}_flast.jpg"
        last168 = frames_dir / f"{rid}_last168.png"

        subprocess.run(["ffmpeg", "-y", "-ss", "0.05", "-i", str(mp4), "-vframes", "1", "-q:v", "3", str(f0)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-y", "-ss", f"{mid_t:.2f}", "-i", str(mp4), "-vframes", "1", "-q:v", "3", str(fmid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-y", "-ss", f"{max(0.5, dur - 0.5):.2f}", "-i", str(mp4), "-vframes", "1", "-q:v", "3", str(flast)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if flast.exists():
            im_last = Image.open(flast)
            im_last.resize((168, round(168 * 1920 / 1080)), Image.Resampling.LANCZOS).save(last168)

        pid = it["pair_id"]
        if pid not in pairs:
            pairs[pid] = {}
        pairs[pid][it["hook_type"]] = (f0, fmid)

    # Build 4 columns x 6 rows grid: 1080 x 2880
    # col 0: Q f0, col 1: Q fmid, col 2: S f0, col 3: S fmid
    col_w, col_h = 270, 480
    sheet = Image.new("RGB", (1080, 2880), (10, 8, 7))
    for r_idx in range(6):
        pid = f"pair_{r_idx + 1}"
        pdata = pairs.get(pid, {})
        q_f0, q_fmid = pdata.get("question", (None, None))
        s_f0, s_fmid = pdata.get("statement", (None, None))
        row_frames = [q_f0, q_fmid, s_f0, s_fmid]
        y = r_idx * col_h
        for c_idx, fpath in enumerate(row_frames):
            x = c_idx * col_w
            if fpath and fpath.exists():
                im = Image.open(fpath).resize((col_w, col_h), Image.Resampling.LANCZOS)
                sheet.paste(im, (x, y))
    preview_path = OUT / "preview_tn1.jpg"
    sheet.save(preview_path, quality=92)
    print(f"Saved preview sheet: {preview_path} ({sheet.size})")


if __name__ == "__main__":
    sys.exit(main())
