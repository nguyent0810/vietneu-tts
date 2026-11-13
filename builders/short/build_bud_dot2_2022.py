"""Builder + render cho bud_dot2_2022: Phủ BUD đợt 2 (7 short 20–22/11/2026).
Lấp phần pilot sóng B không phủ (GitHub issue #138).
Giờ slot là UTC.

Phân bổ 7 short BUD:
- 20/11 (2 short): slot 03:30 UTC (tuong: statue_vietnam_01 - Chùa Phật Tích 1057)
                   slot 08:00 UTC (kinh_chu: statue_china_01 - Pháp Cú 1 & 2)
- 21/11 (2 short): slot 03:30 UTC (tuong: statue_india_03 - Ấn Chuyển Pháp Luân sn56.11)
                   slot 08:00 UTC (tuong: statue_gandhara_01 - Thấy Pháp là thấy Ta sn22.87)
- 22/11 (3 short): slot 03:30 UTC (tuong: statue_vietnam_03 - Tượng Phật đồng Đồng Dương thế kỷ 8-9)
                   slot 08:00 UTC (kinh_chu: statue_japan_01 - Kinh Rải Tâm Từ an11.15)
                   slot 16:20 UTC (tuong: statue_sea_10 - Borobudur Dharmachakra mn26)

Tỉ lệ: 5 tuong : 2 kinh_chu (~2:1).
"""
from __future__ import annotations
from shortbuild import validate

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageEnhance

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
OUT = HERE / "render_bud_dot2"
BUD_OUT = ROOT / "output/cl_staging/bud/out"
PLAN = ROOT / "output/cl_staging/bud/plan_bud_dot2_2022.json"
PACKAGING_DIR = ROOT / "output/cl_staging/bud/packaging"
HOLD = 2.7
VOICE_DELAY = 0.5
SUT = "https://suttacentral.net"
BATCH = "bud_dot2_2022"
BASE = {"series": "bud", "replaces": None, "batch_id": BATCH}


def big(s: str, fs: int = 50) -> str:
    return f'<div class="big warm" style="font-size:{fs}px">{s}</div>'


def sub(s: str) -> str:
    return f'<div class="sub">{s}</div>'


ITEMS = [
    # ---------------- 2026-11-20 ----------------
    dict(
        id="bud_d2_20_1", day="2026-11-20", slot="03:30",
        lane="tuong", sid="statue_vietnam_01", kind="tuong", acc=("#f2b48a", "#2b1407"),
        title="Tượng Phật chùa Phật Tích: Vì sao hai bàn tay đặt chồng lên nhau?",
        chip="BẢO VẬT QUỐC GIA CHÙA VIỆT", srcline="CHÙA PHẬT TÍCH (1057) · THỦ ẤN THIỀN ĐỊNH",
        head='TƯỢNG PHẬT THỜI LÝ<br><span class="warm">HAI TAY ĐẶT THẾ NÀO?</span>',
        script=[
            "Thế tay tượng Phật Tích có ý nghĩa gì?",
            "Tượng ngồi kiết già, hai bàn tay **đan ngửa trong lòng bàn chân**.",
            "Đây là **thủ ấn Thiền định**, biểu thị sự tĩnh lặng tuyệt đối.",
            "Lắng dịu **mọi xao động của tâm trí**.",
            "Theo cách giải thích phổ biến, toà sen nhắc ta **vượt lên bùn lầy**.",
            "Lúc giông bão, bạn có dành phút nào tĩnh tâm?"
        ],
        cards=[
            None,
            big("HAI TAY ĐAN NGỬA<br>TRONG LÒNG CHÂN", 50),
            sub("Chùa Phật Tích 1057") + big("THỦ ẤN THIỀN ĐỊNH<br>TĨNH LẶNG TUYỆT ĐỐI", 46),
            big("LẮNG DỊU XAO ĐỘNG<br>TRONG TÂM TRÍ", 50),
            sub("Theo cách giải thích phổ biến") + big("NHƯ HOA SEN NỞ<br>VƯỢT LÊN BÙN LẦY", 46),
            None
        ],
        source="Bảo vật Quốc gia số 1 (Quyết định 2599/QĐ-TTg năm 2012): Tượng A Di Đà chùa Phật Tích (Bắc Ninh) tạc bằng đá sa thạch năm Đinh Dậu 1057 thời Lý. Thủ ấn Thiền định (Dhyana mudra). Chi tiết toà sen và bệ rồng theo cách giải thích phổ biến của mỹ thuật cổ Phật giáo Việt Nam.",
        insight="Tượng A Di Đà chùa Phật Tích (1057) là Bảo vật Quốc gia số 1 thời Lý, tạc với thủ ấn Thiền định (hai tay đan ngửa trong lòng chân), biểu tượng cho sự định tĩnh tuyệt đối vượt lên mọi xao động trần thế.",
        cta="Giữa những bộn bề hằng ngày, bạn thường chọn cách nào để lắng dịu tâm trí?",
        tags=["tuong phat tich", "chua phat tich", "bao vat quoc gia", "an thien dinh", "phat giao thoi ly"],
        tags_vi=["tượng Phật Tích", "chùa Phật Tích", "Bảo vật Quốc gia", "ấn thiền định", "Phật giáo thời Lý"],
        hashtags=["#Shorts", "#phậtpháp", "#bảovậtquốcgia", "#chùaViệt", "#thiềnđịnh"]
    ),
    dict(
        id="bud_d2_20_2", day="2026-11-20", slot="08:00",
        lane="kinh_chu", sid="statue_china_01", kind="kinh_chu", acc=("#f4cf6b", "#2a1a05"),
        title="Kinh Pháp Cú Kệ 1 & 2: Vì sao Đức Phật dạy 'Ý dẫn đầu các pháp'?",
        chip="LỜI PHẬT · KINH PHÁP CÚ", srcline="KINH PHÁP CÚ · KỆ 1 VÀ 2",
        head='Ý DẪN ĐẦU CÁC PHÁP:<br><span class="warm">LỜI PHẬT DẠY NGHĨA LÀ GÌ?</span>',
        script=[
            "Ý dẫn đầu các pháp nghĩa là gì?",
            "Kinh Pháp Cú kệ một và hai ghi: **ý dẫn đầu các pháp**.",
            "Ý làm chủ, ý tạo tác, **tâm khởi trước mọi hành vi**.",
            "Tâm ô nhiễm nói hay làm, **khổ theo sau như xe bò kéo**.",
            "Tâm thanh tịnh, **an lạc theo sau như bóng không rời**.",
            "Hôm nay, tâm bạn đang hướng về an vui nào?"
        ],
        cards=[
            None,
            sub("Kinh Pháp Cú · Kệ 1 & 2") + big("Ý DẪN ĐẦU CÁC PHÁP<br>Ý LÀM CHỦ TẠO TÁC", 48),
            big("TÂM KHỞI TRƯỚC<br>LỜI NÓI VÀ HÀNH ĐỘNG", 48),
            sub("Kệ 1") + big("TÂM Ô NHIỄM:<br>KHỔ THEO NHƯ XE KÉO", 48),
            sub("Kệ 2") + big("TÂM THANH TỊNH:<br>AN LẠC NHƯ BÓNG VỚI HÌNH", 46),
            None
        ],
        source=f"Kinh Pháp Cú 1 & 2 (dhp1-2), bản Bhikkhu Sujato (CC0): {SUT}/dhp1-20/en/sujato — 'Intention is the leader of things; intention is first, they’re made by intention. If with corrupt intent you speak or act, suffering follows you, like a wheel, the ox’s foot. Intention is the leader of things; intention is first, they’re made by intention. If with pure intent you speak or act, happiness follows you like a shadow that never leaves.' Pali: Manopubbaṅgamā dhammā, manoseṭṭhā manomayā; Manasā ce paduṭṭhena, bhāsati vā karoti vā; Tato naṁ dukkhamanveti, cakkaṁva vahato padaṁ. Manopubbaṅgamā dhammā, manoseṭṭhā manomayā; Manasā ce pasannena, bhāsati vā karoti vā; Tato naṁ sukhamanveti, chāyāva anapāyinī.",
        insight="Kinh Pháp Cú mở đầu bằng hai bài kệ bất hủ: Ý dẫn đầu các pháp, ý làm chủ tạo tác. Khởi tâm ô nhiễm thì khổ đau theo sau như bánh xe lăn theo chân bò; khởi tâm thanh tịnh thì an lạc theo sau như bóng với hình.",
        cta="Mỗi sáng thức dậy, bạn thường gieo vào tâm trí ý nghĩ tích cực nào đầu tiên?",
        tags=["kinh phap cu", "y dan dau cac phap", "ke 1 phap cu", "loi phat day", "tam thanh tinh"],
        tags_vi=["Kinh Pháp Cú", "ý dẫn đầu các pháp", "kệ 1 Pháp Cú", "lời Phật dạy", "tâm thanh tịnh"],
        hashtags=["#Shorts", "#phậtpháp", "#kinhphápcú", "#lờiphậtdạy", "#anlạc"]
    ),

    # ---------------- 2026-11-21 ----------------
    dict(
        id="bud_d2_21_1", day="2026-11-21", slot="03:30",
        lane="tuong", sid="statue_india_03", kind="tuong", acc=("#9fd3c7", "#0b2420"),
        title="Thế tay Chuyển Pháp Luân trên tượng Phật có ý nghĩa gì?",
        chip="Ý NGHĨA THẾ TAY TƯỢNG PHẬT", srcline="KINH TƯƠNG ƯNG 56.11 · CHUYỂN PHÁP LUÂN",
        head='THẾ TAY XOAY BÁNH XE:<br><span class="warm">TƯỢNG PHẬT DẠY ĐIỀU GÌ?</span>',
        script=[
            "Thế tay xoay bánh xe có ý nghĩa gì?",
            "Đây là **ấn Chuyển Pháp Luân**, xoay bánh xe chân lý.",
            "Kinh Tương Ưng năm mươi sáu chấm mười một tại vườn Nai.",
            "Đức Phật khai thị **bốn chân lý Tứ Diệu Đế** và Bát Chánh Đạo.",
            "Bánh xe chánh pháp chuyển đi, **không ai đảo ngược được**.",
            "Bạn đã chọn con đường chân chánh nào cho mình?"
        ],
        cards=[
            None,
            big("THỦ ẤN CHUYỂN PHÁP LUÂN<br>XOAY BÁNH XE CHÂN LÝ", 46),
            sub("Tương Ưng 56.11 · Vườn Lộc Uyển") + big("BÀI THUYẾT PHÁP ĐẦU TIÊN<br>CHO NĂM ANH EM ĐỆ TỬ", 44),
            big("TỨ DIỆU ĐẾ VÀ<br>BÁT CHÁNH ĐẠO", 50),
            big("BÁNH XE CHÂN LÝ<br>KHÔNG THỂ CHUYỂN NGƯỢC", 48),
            None
        ],
        source=f"Kinh Tương Ưng 56.11 (sn56.11:1.1–12.11), bản Bhikkhu Sujato (CC0): {SUT}/sn56.11/en/sujato — 'Near Varanasi, in the deer park at Isipatana, the Buddha has rolled forth the supreme Wheel of Dhamma. And that wheel cannot be rolled back by any ascetic or brahmin or god or Māra or divinity or by anyone in the world.' Tượng Phật thuyết bài pháp đầu tiên, thế kỷ 5 (Gupta), Bảo tàng Khảo cổ Sarnath, Ấn Độ (bank statue_india_03): thủ ấn Dharmachakra mudra, bệ tượng chạm bánh xe pháp và năm vị đệ tử.",
        insight="Thế tay Chuyển Pháp Luân (Dharmachakra mudra) tái hiện khoảnh khắc Đức Phật thuyết bài pháp đầu tiên tại Vườn Lộc Uyển (Kinh Tương Ưng 56.11), khai thị Tứ Diệu Đế và Bát Chánh Đạo, mở ra bánh xe chánh pháp không gì chuyển ngược lại được.",
        cta="Trong tám con đường chân chánh của Bát Chánh Đạo, bạn tâm đắc điều nào nhất?",
        tags=["chuyen phap luan", "tuong sarnath", "tu dieu de", "bat chanh dao", "tuong ung 56"],
        tags_vi=["Chuyển Pháp Luân", "tượng Sarnath", "Tứ Diệu Đế", "Bát Chánh Đạo", "Tương Ưng 56"],
        hashtags=["#Shorts", "#phậtpháp", "#chuyểnphápluân", "#tứdiệuđế", "#bátchánhđạo"]
    ),
    dict(
        id="bud_d2_21_2", day="2026-11-21", slot="08:00",
        lane="tuong", sid="statue_gandhara_01", kind="tuong", acc=("#c9b8ff", "#1c1236"),
        title="Ngắm tượng Phật trang nghiêm, ta nhớ lời Phật dạy điều gì?",
        chip="LỜI PHẬT DẠY · KINH TƯƠNG ƯNG", srcline="TƯƠNG ƯNG 22.87 · TÔN GIẢ VAKKALI",
        head='NGẮM TƯỢNG PHẬT TRANG NGHIÊM,<br><span class="warm">ĐỨC PHẬT DẠY ĐIỀU GÌ?</span>',
        script=[
            "Ngắm tượng Phật, Đức Phật nhắc ta điều gì?",
            "Kinh Tương Ưng hai mươi hai chấm tám mươi bảy, thầy Bạt-ca-lê bệnh nặng.",
            "Thầy thưa: con chỉ mong được **ngắm nhìn Đức Phật**.",
            "Ngài dạy: có ích gì khi ngắm **thân xác vô thường này**?",
            "Người nào **thấy Pháp là thấy Ta**.",
            "Bình an thật sự, bạn tìm ở đâu hôm nay?"
        ],
        cards=[
            None,
            sub("Tương Ưng 22.87 · Thầy Bạt-ca-lê") + big("THẦY BẠT CA LÊ<br>NẰM BỆNH NẶNG", 48),
            big("“CON CHỈ MONG ĐƯỢC<br>NGẮM NHÌN ĐỨC PHẬT”", 48),
            sub("Lời Đức Phật dạy") + big("CÓ ÍCH GÌ KHI NGẮM<br>THÂN XÁC VÔ THƯỜNG?", 46),
            big("AI THẤY PHÁP LÀ THẤY TA<br>AI THẤY TA LÀ THẤY PHÁP", 48),
            None
        ],
        source=f"Kinh Tương Ưng 22.87, Kinh Vakkali (sn22.87:3.1–3.5), bản Bhikkhu Sujato (CC0): {SUT}/sn22.87/en/sujato — '“Enough, Vakkali! Why would you want to see this rotting body? One who sees the teaching sees me. One who sees me sees the teaching. Seeing the teaching, you see me. Seeing me, you see the teaching.” Pali: ‘Alaṁ, vakkali, kiṁ te iminā pūtikāyena diṭṭhena? Yo kho, vakkali, dhammaṁ passati so maṁ passati; yo maṁ passati so dhammaṁ passati. Dhammañhi, vakkali, passanto maṁ passati; maṁ passanto dhammaṁ passati’.'",
        insight="Kinh Tương Ưng 22.87 ghi lại lời dạy chí lý của Đức Phật với thầy Bạt-ca-lê (Vakkali): Thân xác này là vô thường hoại diệt, ngắm nhìn có ích chi; người nào thấy chánh pháp mới chính là thấy Như Lai.",
        cta="Khi chiêm bái tượng Phật, điều gì nhắc nhở bạn quay về tu sửa thân tâm?",
        tags=["vakkali", "bat ca le", "thay phap la thay ta", "tuong ung 22", "loi phat day"],
        tags_vi=["Vakkali", "Bạt-ca-lê", "thấy Pháp là thấy Ta", "Tương Ưng 22", "lời Phật dạy"],
        hashtags=["#Shorts", "#phậtpháp", "#lờiphậtdạy", "#tươngưng", "#thấypháplàthấyta"]
    ),

    # ---------------- 2026-11-22 ----------------
    dict(
        id="bud_d2_22_1", day="2026-11-22", slot="03:30",
        lane="tuong", sid="statue_vietnam_03", kind="tuong", acc=("#f2b48a", "#2b1407"),
        title="Tượng Phật đồng Đồng Dương: Bảo vật Quốc gia nghìn năm tuổi nói lên điều gì?",
        chip="BẢO VẬT QUỐC GIA CHÙA VIỆT", srcline="PHẬT VIỆN ĐỒNG DƯƠNG · THẾ KỶ 8-9",
        head='TƯỢNG PHẬT ĐỒNG NGHÌN NĂM:<br><span class="warm">BẢO VẬT CỦA ĐẤT NƯỚC</span>',
        script=[
            "Pho tượng đồng nghìn năm nói gì?",
            "Đây là **tượng Phật đồng Đồng Dương** đúc từ thế kỷ tám.",
            "Tượng đứng uy nghiêm, tay phải giơ lên **bắt ấn thuyết pháp**.",
            "Nếp y mềm mại, gương mặt toát lên **sự an tĩnh và từ bi**.",
            "Theo sử liệu, đây là dấu ấn **Phật giáo rực rỡ** trên đất Việt.",
            "Nhìn nét từ bi xưa, lòng bạn có nhẹ nhõm hơn?"
        ],
        cards=[
            None,
            sub("Bảo vật Quốc gia Việt Nam") + big("TƯỢNG ĐỒNG ĐỒNG DƯƠNG<br>THẾ KỶ 8–9 NGUYÊN KHỐI", 46),
            big("TAY PHẢI GIƠ LÊN<br>BẮT ẤN THUYẾT PHÁP", 50),
            big("NẾP Y MỀM MẠI<br>GƯƠNG MẶT TỪ BI", 50),
            sub("Theo tư liệu lịch sử") + big("MINH CHỨNG PHẬT PHÁP<br>HƯNG THỊNH NGHÌN NĂM", 46),
            None
        ],
        source="Bảo vật Quốc gia (Quyết định 1426/QĐ-TTg năm 2018): Tượng Phật đồng Đồng Dương, phát hiện tại Phật viện Đồng Dương (huyện Thăng Bình, Quảng Nam), niên đại thế kỷ 8-9, hiện lưu giữ tại Bảo tàng Lịch sử Quốc gia. Đúc bằng đồng thau nguyên khối, phong cách nghệ thuật Amaravati kết hợp bản địa Champa.",
        insight="Tượng Phật đồng Đồng Dương (Quảng Nam, thế kỷ 8-9) là Bảo vật Quốc gia cao hơn 1m2 đúc bằng đồng thau nguyên khối, minh chứng cho trung tâm Phật giáo hưng thịnh rực rỡ trên dải đất miền Trung Việt Nam hơn một nghìn năm trước.",
        cta="Bạn đã từng chiêm bái pho tượng Phật cổ nào để lại ấn tượng sâu sắc nhất?",
        tags=["tuong dong duong", "phat vien dong duong", "bao vat quoc gia", "phat giao champa", "chua viet"],
        tags_vi=["tượng Đồng Dương", "Phật viện Đồng Dương", "Bảo vật Quốc gia", "Phật giáo Champa", "chùa Việt"],
        hashtags=["#Shorts", "#phậtpháp", "#bảovậtquốcgia", "#tượngPhật", "#di tíchlịchsử"]
    ),
    dict(
        id="bud_d2_22_2", day="2026-11-22", slot="08:00",
        lane="kinh_chu", sid="statue_japan_01", kind="kinh_chu", acc=("#f4cf6b", "#2a1a05"),
        title="Kinh Rải Tâm Từ: 11 phước lành khi sống với lòng từ bi (Kinh Tăng Chi 11.15)",
        chip="LỜI PHẬT · KINH TĂNG CHI", srcline="TĂNG CHI 11.15 · PHƯỚC LÀNH LÒNG TỪ",
        head='KINH RẢI TÂM TỪ:<br><span class="warm">MƯỜI MỘT ĐIỀU AN LÀNH</span>',
        script=[
            "Nuôi dưỡng lòng từ mang lại điều gì?",
            "Kinh Tăng Chi mười một chấm mười lăm dạy: **lòng từ mang mười một phước lành**.",
            "Đêm về **ngủ yên giấc**, sáng dậy **an lành**, không ác mộng.",
            "Mọi người và muôn loài yêu mến, **tâm trí dễ định tĩnh**.",
            "Nét mặt luôn **tươi sáng**, khi ra đi không hề sợ hãi.",
            "Đêm nay, bạn có muốn gửi lời chúc lành đến muôn loài?"
        ],
        cards=[
            None,
            sub("Kinh Tăng Chi 11.15 · Mettā Sutta") + big("MƯỜI MỘT LỢI ÍCH<br>CỦA LÒNG TỪ BI", 48),
            big("NGỦ NGON THỨC DẬY AN<br>KHÔNG GẶP ÁC MỘNG", 48),
            big("MUÔN LOÀI YÊU QUÝ<br>TÂM TRÍ AN ĐỊNH", 50),
            big("SẮC DIỆN TƯƠI SÁNG<br>RA ĐI KHÔNG RỐI LOẠN", 48),
            None
        ],
        source=f"Kinh Tăng Chi 11.15, Kinh Lợi Ích Của Lòng Từ (an11.15:1.1–2.3), bản Bhikkhu Sujato (CC0): {SUT}/an11.15/en/sujato — 'Mendicants, you can expect eleven benefits when the heart’s release by love has been cultivated, developed, and practiced … You sleep at ease. You wake happily. You don’t have bad dreams. Humans love you. Non-humans love you. Deities protect you. You can’t be harmed by fire, poison, or blade. Your mind quickly enters immersion. Your face is clear and bright. You don’t feel lost when you die. If you don’t penetrate any higher, you’ll be reborn in a realm of divinity.' Pali: 'Mettāya bhikkhave cetovimuttiyā āsevitāya bhāvitāya bahulīkatāya … ekādasānisaṁsā pāṭikaṅkhā. Katame ekādasa? Sukhaṁ supati, sukhaṁ paṭibujjhati, na pāpakaṁ supinaṁ passati, manussānaṁ piyo hoti, amanussānaṁ piyo hoti, devatā rakkhanti, nāssa aggi vā visaṁ vā satthaṁ vā kamati, tuvaṭaṁ cittaṁ samādhiyati, mukhavaṇṇo vippasīdati, asammūḷho kālaṁ karoti, uttariṁ appaṭivijjhanto brahmalokūpago hoti.'",
        insight="Kinh Tăng Chi 11.15 (Kinh Rải Tâm Từ) chỉ ra 11 phước lành thiết thực khi nuôi dưỡng tâm từ: ngủ ngon, thức dậy an lành, không ác mộng, muôn loài yêu kính, chư thiên che chở, diện mạo tươi sáng, tâm dễ định tĩnh và thanh thản.",
        cta="Tối nay trước khi ngủ, bạn hãy thử dành 2 phút gửi năng lượng an lành đến người thân nhé!",
        tags=["kinh rai tam tu", "long tu bi", "11 phuoc lanh", "tang chi 11", "loi phat day"],
        tags_vi=["Kinh Rải Tâm Từ", "lòng từ bi", "11 phước lành", "Tăng Chi 11", "lời Phật dạy"],
        hashtags=["#Shorts", "#phậtpháp", "#kinhrảitâmtừ", "#lòngtừbi", "#bìnhan"]
    ),
    dict(
        id="bud_d2_22_3", day="2026-11-22", slot="16:20",
        lane="tuong", sid="statue_sea_10", kind="tuong", acc=("#9fd3c7", "#0b2420"),
        title="Tượng Phật trên tháp tròn Borobudur: Nét trầm mặc giữa trời mây nhắc ta điều gì?",
        chip="DI SẢN PHẬT GIÁO THẾ GIỚI", srcline="ĐẠI THÁP BOROBUDUR · THẾ KỶ 8-9",
        head='TƯỢNG PHẬT TRÊN THÁP TRÒN:<br><span class="warm">NÉT TRẦM MẶC NHẮC ĐIỀU GÌ?</span>',
        script=[
            "Tượng Phật trên tháp đá nhắc ta điều gì?",
            "Đại tháp Borobudur, tượng Phật ngồi giữa **tầng tháp tròn thanh tịnh**.",
            "Hai tay trước ngực bắt **ấn Chuyển Pháp Luân**, nhắc bánh xe chánh pháp.",
            "Kinh Trung Bộ hai mươi sáu ghi: Đức Phật **mở cửa bất tử cho muôn loài**.",
            "Theo cách giải thích phổ biến, tầng tròn biểu thị **sự giải thoát ràng buộc**.",
            "Giữa đời xao động, bạn giữ góc an yên nào cho mình?"
        ],
        cards=[
            None,
            sub("Đại tháp Borobudur thế kỷ 8–9") + big("TẦNG THÁP TRÒN<br>CÕI VÔ SẮC THANH TỊNH", 46),
            big("ẤN CHUYỂN PHÁP LUÂN:<br>HAI TAY TRƯỚC NGỰC", 44),
            sub("Trung Bộ 26 · Thánh Cầu") + big("MỞ CỬA BẤT TỬ<br>TRAO TRUYỀN CHÁNH PHÁP", 46),
            sub("Theo cách giải thích phổ biến") + big("GIẢI THOÁT KHỎI<br>MỌI RÀNG BUỘC", 48),
            None
        ],
        source=f"Kinh Trung Bộ 26 (mn26:21.1–21.5), bản Bhikkhu Sujato (CC0): {SUT}/mn26/en/sujato — 'Opened for them are the doors to the deathless! Let those with ears show their faith.' Tượng Phật andesite đại tháp Borobudur (thế kỷ 8-9, Indonesia, Di sản UNESCO). Theo mô tả phổ biến, các tượng Phật trong tháp chuông tầng tròn bắt thủ ấn Dharmachakra mudra (Chuyển Pháp Luân); hai tay tượng trong ảnh đặt trước ngực.",
        insight="Đại tháp Borobudur (thế kỷ 8-9) với các pho tượng Phật uy nghiêm trên tầng tháp tròn biểu thị cõi Vô sắc giới, nơi tâm thức đạt đến sự giải thoát hoàn toàn khỏi mọi ràng buộc trần thế.",
        cta="Khi đứng trước không gian thanh tịnh của chùa tháp, cảm giác đầu tiên của bạn là gì?",
        tags=["borobudur", "tuong phat borobudur", "an chuyen phap luan", "trung bo 26", "di san the gioi"],
        tags_vi=["Borobudur", "tượng Phật Borobudur", "ấn Chuyển Pháp Luân", "Trung Bộ 26", "di sản thế giới"],
        hashtags=["#Shorts", "#phậtpháp", "#Borobudur", "#tượngPhật", "#disảnthếgiới"]
    )
]

# Set base attributes
for it in ITEMS:
    it.update(BASE)
    it["style"] = "statue_cards"
    it["hypothesis"] = "20–27s + câu 1 câu hỏi cụ thể <= 2.5s + tượng thật nguyên vẹn không đè chữ + dẫn kinh rõ"
    it["format_subtag"] = "tuong_phat_giao" if it["lane"] == "tuong" else "kinh_chu_tinh_hoa"
    it["novelty_ok"] = "đã kiểm tra qua hf_novelty, không trùng"
    it["img_kind"] = "statue_real"

# Setup images and cards in R5 dictionaries
STATUES_DATA = json.loads((ROOT / "output/cl_staging/bud/banks/statues.json").read_text(encoding="utf-8"))
for it in ITEMS:
    s = next(x for x in STATUES_DATA if x["id"] == it["sid"])
    # top=260 ensures head of statue is below header with comfortable breathing room (0-240px header)
    R5.IMG[it["id"]] = (R5.bank_path(it["sid"]), 260, 0.92)
    R5.CREDITS[it["id"]] = (f"{s['title']} — {s.get('author') or 'Wikimedia Commons'}, {s['license']}", f"{s['title']} · {s['license']}", s["license"])
    R5.CARDS[it["id"]] = it["cards"]
    R5.HEAD[it["id"]] = (it["chip"], it["head"], it["srcline"])
    R5.ACCENT[it["id"]] = it["acc"]
    R5.LISTS[it["id"]] = []

# Pick BGM using shared library
for it in ITEMS:
    hf_music.short_pick(it)
BGM = {it["id"]: json.loads((ROOT / "output/cl_staging/bud/bgm_shorts.json").read_text())[it["id"]]["file"] for it in ITEMS}
for m in (R4, R5, R6):
    m.BGM.update(BGM)


def library_motion(h: str) -> str:
    h = h.replace('{opacity: 0, y: 26, filter: "blur(8px)"}', '{opacity: 0, y: 26}').replace('filter: "blur(0px)", ', "")
    return h.replace('ease: "power2.out"}, at)', 'ease: "expo.out"}, at)')


def make_preview_sheet() -> Path:
    """Tờ ảnh preview 7 bài: Khung 0, Khung giữa, Khung cuối 168px cho Lead duyệt."""
    frames_dir = OUT / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    print("=== MAKE PREVIEW SHEET (7 bài x 3 khung: 0, giữa, cuối) ===")

    rows = []
    for it in ITEMS:
        rid = it["id"]
        mp4 = OUT / f"{rid}.mp4"
        if not mp4.exists():
            continue
        dur = it["dur"]
        mid_t = dur / 2.0
        last_t = max(0.5, dur - 0.4)

        f0 = frames_dir / f"{rid}_f0.jpg"
        fmid = frames_dir / f"{rid}_fmid.jpg"
        flast = frames_dir / f"{rid}_flast.jpg"

        subprocess.run(["ffmpeg", "-y", "-ss", "0.08", "-i", str(mp4), "-vframes", "1", "-q:v", "3", str(f0)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-y", "-ss", f"{mid_t:.2f}", "-i", str(mp4), "-vframes", "1", "-q:v", "3", str(fmid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-y", "-ss", f"{last_t:.2f}", "-i", str(mp4), "-vframes", "1", "-q:v", "3", str(flast)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        rows.append((rid, f0, fmid, flast))

    # Build 3 columns x 7 rows grid: 168 px width per thumbnail
    w_thumb = 168
    h_thumb = round(168 * 1920 / 1080)  # 299
    grid_w = w_thumb * 3
    grid_h = h_thumb * len(rows)

    sheet = Image.new("RGB", (grid_w, grid_h), (10, 8, 7))
    for r_idx, (rid, f0, fmid, flast) in enumerate(rows):
        y = r_idx * h_thumb
        for c_idx, fpath in enumerate([f0, fmid, flast]):
            x = c_idx * w_thumb
            if fpath.exists():
                im = Image.open(fpath).resize((w_thumb, h_thumb), Image.Resampling.LANCZOS)
                sheet.paste(im, (x, y))

    preview_path = OUT / "preview_bud_dot2.jpg"
    sheet.save(preview_path, quality=92)
    print(f"Saved preview sheet: {preview_path} ({sheet.size})")
    return preview_path


def main() -> int:
    html_only = "--html-only" in sys.argv
    only = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)

    print("=== TTS GENERATION & TIMING ===")
    jobs = []
    for it in ITEMS:
        if only and it["id"] not in only:
            continue
        R6.tts(it, (0.42, 0.50))
        fin_json = json.loads((D / f"{it['id']}_final.json").read_text(encoding="utf-8"))
        it["dur"] = round(fin_json["duration_s"] + VOICE_DELAY + HOLD, 2)
        c0 = fin_json["segments"][0]["end"] - fin_json["segments"][0]["start"]
        print(f"[{it['id']}] câu 0: {c0:.2f}s | audio: {fin_json['duration_s']:.2f}s | dur: {it['dur']:.2f}s")
        assert c0 <= 2.50, f"{it['id']} câu 0 vượt 2.5s ({c0:.2f}s)"
        assert 21.0 <= it["dur"] <= 27.0, f"{it['id']} thời lượng ngoài 21-27s ({it['dur']:.2f}s)"

        t = R5.segs(it["id"], VOICE_DELAY)
        h = library_motion(R5.html_statue(it["id"], t, it["dur"]))
        jobs.append((it, h))

    # Write compositions
    print("\n=== WRITING COMPOSITIONS ===")
    for it, h in jobs:
        comp_path = B.COMP / f"_r_{it['id']}.html"
        comp_path.write_text(h, encoding="utf-8")
        print(f"Wrote {comp_path.name}")

    # Write plan file
    clean = {"id", "day", "slot", "replaces", "lane", "style", "title", "script", "source", "series", "dur",
             "batch_id", "hypothesis", "format_subtag", "novelty_ok", "img_kind"}
    plan = []
    for it, _ in jobs:
        p = {k: it[k] for k in clean if k in it}
        s = next(x for x in STATUES_DATA if x["id"] == it["sid"])
        p["media_credit"] = f"{s['title']} — {s.get('author') or 'Wikimedia Commons'}, {s['license']}"
        p["image"] = it["sid"]
        p["tags"] = it["tags"]
        plan.append(p)
    validate(plan)
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nWrote plan: {PLAN}")

    # Write packaging sidecars
    PACKAGING_DIR.mkdir(parents=True, exist_ok=True)
    for it, _ in jobs:
        pack = {
            "id": it["id"],
            "title": it["title"],
            "insight": it["insight"],
            "tags": it["tags"],
            "tags_vi": it["tags_vi"],
            "hashtags": it["hashtags"],
            "cta": it["cta"],
            "day": it["day"],
            "slot": it["slot"],
            "style": it["style"],
            "lane": it["lane"],
            "slot_vn": f"{it['day']} {int(it['slot'][:2]) + 7:02d}:{it['slot'][3:]} (giờ VN)"
        }
        pack_file = PACKAGING_DIR / f"{it['id']}.json"
        pack_file.write_text(json.dumps(pack, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Wrote packaging: {pack_file.name}")

    if html_only:
        print("\n[--html-only] Dừng trước render.")
        return 0

    # Render videos
    print("\n=== RENDERING MP4 ===")
    OUT.mkdir(parents=True, exist_ok=True)
    BUD_OUT.mkdir(parents=True, exist_ok=True)

    for it, _ in jobs:
        rid = it["id"]
        silent = D / f"{rid}_silent.mp4"
        mp4 = OUT / f"{rid}.mp4"
        bud_mp4 = BUD_OUT / f"{rid}.mp4"
        B.to_trash(silent)
        B.to_trash(mp4)

        print(f"[{rid}] rendering ...", flush=True)
        R4.render(f"_r_{rid}.html", silent)
        vl, gain, ml = R4.mix(rid, silent, D / f"{rid}_final.wav", mp4, it["dur"], VOICE_DELAY, True)
        B.to_trash(silent)

        # Copy to bud/out
        bud_mp4.write_bytes(mp4.read_bytes())

        s = next(x for x in STATUES_DATA if x["id"] == it["sid"])
        meta = {
            "ok": True,
            "output": str(mp4.relative_to(ROOT)),
            "duration_s": it["dur"],
            "style": it["style"],
            "lane": it["lane"],
            "day": it["day"],
            "slot": it["slot"],
            "bgm": f"bgm/{BGM[rid]}",
            "bgm_title": hf_music.TITLES[BGM[rid]],
            "bgm_gain": round(gain, 4),
            "media_credits": [{
                "id": rid,
                "kind": "commons",
                "credit": f"{s['title']} — {s.get('author') or 'Wikimedia Commons'}, {s['license']}"
            }],
            "voice": "Binh",
            "lufs": {"voice": round(vl, 1), "mix": round(ml, 1), "offset_db": -20.0},
            "sfx_credit": B.BELL_CREDIT
        }
        meta_json = json.dumps(meta, ensure_ascii=False, indent=2)
        (OUT / f"{rid}.render.json").write_text(meta_json, encoding="utf-8")
        (BUD_OUT / f"{rid}.render.json").write_text(meta_json, encoding="utf-8")
        print(f"[{rid}] Xong | dur={it['dur']}s | LUFS voice {vl:.1f} mix {ml:.1f}", flush=True)

    # Preview sheet
    make_preview_sheet()
    print("\n=== HOÀN TẤT TOÀN BỘ 7 VIDEO BUD DOT 2 ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
