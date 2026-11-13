"""002_bud_short_phu_1104: 11 short BUD phủ 04-08/11 (dạng thắng + sửa tỉ lệ xem hết). Giờ `slot` là UTC.

    .venv/bin/python output/cl_staging/grok/build_002_bud_phu_1104.py [--html-only] [--only=id1,id2]
"""
from __future__ import annotations
from shortbuild import validate

import json
import sys
from pathlib import Path

from PIL import Image, ImageEnhance

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "output/cl_staging/long"))
import build_bud_1023r as B   # noqa: E402
import build_r1024 as R4      # noqa: E402
import build_r1025 as R5      # noqa: E402
import build_r1026 as R6      # noqa: E402
import hf_music               # noqa: E402

D = B.D
OUT = HERE / "render_002"
PLAN = ROOT / "output/cl_staging/bud/plan_002_bud_phu_1104.json"
AI = ROOT / "output/cl_staging/grokbot/bud_doithuong_bg_1103/out"
HOLD = 3.3
AI_CREDIT = ("Ảnh minh hoạ AI (ChatGPT qua GrokBot), không phải tư liệu lịch sử", "Ảnh minh hoạ AI (ChatGPT qua GrokBot) · không phải tư liệu lịch sử", "AI")
SUT = "https://suttacentral.net"
BASE = {"series": "bud", "replaces": None, "batch_id": "bud_w45a"}
HYP = "20–27s + câu 1 là tình huống/câu hỏi đời sống cụ thể + vòng lặp câu cuối tăng stay"


def big(s, fs=56): return f'<div class="big warm" style="font-size:{fs}px">{s}</div>'
def sub(s): return f'<div class="sub">{s}</div>'


ITEMS = [
 dict(id="bud002_t1", day="2026-11-04", slot="08:00", lane="tuong", ai="ai_01.png", kind="tuong", acc=("#f2b48a", "#2b1407"),
  title="Đi khất thực mà không ai cúng, Đức Phật làm gì?", chip="ĐỜI THƯỜNG CỦA ĐỨC PHẬT", srcline="TƯƠNG ƯNG 4.18",
  head='ĐI KHẤT THỰC MÀ<br><span class="warm">KHÔNG AI CÚNG?</span>',
  script=["Đi khất thực mà cả làng không ai cúng, Đức Phật làm gì?",
          "Ma Vương khiến dân làng nghĩ: **đừng cho ông ấy gì**.",
          "Ngài rời làng với **chiếc bát vẫn sạch** như lúc bước vào.",
          "Ma Vương hỏi: **có được gì không**?",
          "Đức Phật đáp: dù chẳng có gì, ta vẫn hạnh phúc, nuôi mình bằng **hỷ lạc**.",
          "Nếu hôm nay bát của bạn trống, bạn sẽ làm gì?"],
  cards=[None, big("MA VƯƠNG XÚI DÂN LÀNG<br>ĐỪNG CHO GÌ", 48), big("BÁT VẪN SẠCH<br>NHƯ LÚC VÀO", 54), big("“CÓ ĐƯỢC GÌ KHÔNG?”", 54),
         sub("Tương Ưng 4.18") + big("NUÔI MÌNH BẰNG HỶ LẠC", 52), None],
  source=f"Kinh Tương Ưng 4.18 (sn4.18:1.2–5.1), bản Bhikkhu Sujato (CC0): {SUT}/sn4.18/en/sujato — 'Māra had possessed the brahmins and householders of Pañcasālā, so that they thought, “Don’t let the ascetic Gotama get any alms!”' 'the Buddha left the village with his bowl as clean-washed as it was when he entered' 'Let us live so very happily, we who have nothing. We shall feed on rapture, like the gods of sublime luminosity.'"),
 dict(id="bud002_k1", day="2026-11-04", slot="12:30", lane="kinh_chu", sid="statue_china_01", kind="kinh_chu", acc=("#f4cf6b", "#2a1a05"),
  title="Lễ quy y ở chùa, vì sao đọc mỗi câu ba lần?", chip="CÂU QUEN THUỘC Ở CHÙA", srcline="KHUDDAKAPĀṬHA 1 · BA QUY Y",
  head='LỄ QUY Y VÌ SAO<br><span class="warm">ĐỌC MỖI CÂU 3 LẦN?</span>',
  script=["Lễ quy y ở chùa, vì sao đọc mỗi câu ba lần?",
          "Vì kinh ghi đúng vậy: quy y **Phật**, **Pháp**, **Tăng**.",
          "Rồi đọc lại, **lần thứ hai**, quy y Phật, Pháp, Tăng.",
          "Rồi **lần thứ ba**.",
          "Quy y nghĩa là **nương tựa** vào Phật, Pháp, Tăng.",
          "Lần tới đọc câu này, bạn nhớ mình đọc mấy lần?"],
  cards=[None, big("PHẬT · PHÁP · TĂNG", 60) + sub("kinh Tiểu Tụng 1"), big("LẦN THỨ HAI", 66), big("LẦN THỨ BA", 66),
         big("QUY Y = NƯƠNG TỰA", 56), None],
  source=f"Khuddakapāṭha 1 (kp1:2.1–4.3), bản Bhikkhu Sujato (CC0): {SUT}/kp1/en/sujato — 'I take refuge in the Buddha, I take refuge in the Teaching, I take refuge in the Saṅgha. For the second time … For the third time …' Pali: Buddhaṁ saraṇaṁ gacchāmi, Dhammaṁ saraṇaṁ gacchāmi, Saṅghaṁ saraṇaṁ gacchāmi; dutiyampi …; tatiyampi …"),
 dict(id="bud002_t2", day="2026-11-05", slot="03:30", lane="tuong", ai="ai_02.png", kind="tuong", acc=("#9fd3c7", "#0b2420"),
  title="Vị sư bệnh nằm một mình, Đức Phật làm gì?", chip="ĐỜI THƯỜNG CỦA ĐỨC PHẬT", srcline="LUẬT TẠNG · ĐẠI PHẨM 8",
  head='VỊ SƯ BỆNH<br><span class="warm">KHÔNG AI CHĂM?</span>',
  script=["Vị sư bệnh nằm một mình, không ai chăm, Đức Phật làm gì?",
          "Ngài **tự tay** đổ nước, cùng A Nan lau rửa cho vị ấy.",
          "Chư tăng thưa: vì vị ấy **chẳng làm gì cho chúng con**.",
          "Đức Phật dạy: **không chăm nhau thì ai chăm?** Ai muốn chăm Ta, hãy **chăm người bệnh**.",
          "Quanh bạn, ai đang bệnh mà không ai chăm?"],
  cards=[None, big("TỰ TAY ĐỔ NƯỚC<br>CÙNG A NAN LAU RỬA", 50), sub("chư tăng thưa") + big("“VỊ ẤY CHẲNG LÀM GÌ<br>CHO CHÚNG CON”", 46),
         sub("Luật tạng · Đại phẩm 8") + big("KHÔNG CHĂM NHAU THÌ AI CHĂM?<br>CHĂM NGƯỜI BỆNH LÀ CHĂM TA", 40), None],
  source=f"Luật tạng, Đại phẩm 8 (pli-tv-kd8:26.1.1–26.3.13), bản Bhikkhu Brahmali (CC0): {SUT}/pli-tv-kd8/en/brahmali — 'The Buddha said to Ānanda, “Go and get some water, Ānanda. Let’s give him a wash.” … the Buddha poured the water, while Ānanda cleaned him up.' '“But why don’t you nurse him?” “Because he doesn’t do anything for us.”' '“Monks, you have no mother or father to nurse you. If you don’t nurse one another, who will? Whoever would nurse me should nurse one who is sick.”'"),
 dict(id="bud002_d1", day="2026-11-05", slot="23:00", lane="doi_song", sid="statue_gandhara_04", kind="doi_song", acc=("#f2b48a", "#2b1407"),
  title="Lương về là hết, Đức Phật dạy cư sĩ làm gì?", chip="ĐỜI SỐNG · LỜI PHẬT DẠY", srcline="KINH TĂNG CHI 8.54",
  head='LƯƠNG VỀ LÀ HẾT,<br><span class="warm">ĐỨC PHẬT DẠY GÌ?</span>',
  script=["Lương về là hết sạch, Đức Phật dạy cư sĩ gì?",
          "Ngài ví tiền như **cái hồ** có bốn cửa vào, bốn cửa ra.",
          "Mở cửa ra, đóng cửa vào, hồ **cạn dần**.",
          "Cửa ra là rượu, cờ bạc và bạn xấu.",
          "Hãy giữ **thu nhiều hơn chi**, không phung phí, không keo kiệt.",
          "Tháng này, cửa nào trong hồ bạn đang mở?"],
  cards=[None, big("TIỀN NHƯ CÁI HỒ<br>4 CỬA VÀO · 4 CỬA RA", 46), big("MỞ CỬA RA<br>HỒ CẠN DẦN", 54), sub("cửa ra") + big("RƯỢU · CỜ BẠC · BẠN XẤU", 46),
         sub("Tăng Chi 8.54") + big("THU NHIỀU HƠN CHI", 54), None],
  source=f"Kinh Tăng Chi 8.54 (an8.54:5.2, 6.1–6.8), bản Bhikkhu Sujato (CC0): {SUT}/an8.54/en/sujato — 'knowing his income and expenditure, balances his finances, being neither too extravagant nor too frugal. He thinks, “In this way my income will exceed my expenditure, not the reverse.”' 'There are four drains on wealth … Womanizing, drinking, gambling, and having bad friends … Suppose there was a large reservoir with four inlets and four drains. And someone was to open up the drains and close off the inlets … You’d expect that large reservoir to dwindle, not expand.' (Kịch bản diễn ý, nêu 3 trong 4 cửa ra.)"),
 dict(id="bud002_t3", day="2026-11-06", slot="10:00", lane="tuong", ai="ai_03.png", kind="tuong", acc=("#f2b48a", "#2b1407"),
  title="Tám mươi tuổi, Đức Phật tự ví thân mình như gì?", chip="ĐỜI THƯỜNG CỦA ĐỨC PHẬT", srcline="TRƯỜNG BỘ 16",
  head='80 TUỔI, ĐỨC PHẬT<br><span class="warm">TỰ VÍ THÂN MÌNH?</span>',
  script=["Tám mươi tuổi, Đức Phật tự ví thân thể mình như vật gì?",
          "Một **chiếc xe cũ kỹ**, chạy được nhờ có dây buộc giữ lại.",
          "Kinh Trường Bộ mười sáu ghi, Ngài nói điều ấy với ngài A Nan.",
          "Có lúc Ngài vào **định không tướng**, thân mới thấy dễ chịu hơn.",
          "Bậc giác ngộ cũng có tuổi già, Ngài nói rất thật.",
          "Bạn tự ví cơ thể mình lúc này như vật gì?"],
  cards=[None, big("XE CŨ KỸ<br>GIỮ BẰNG DÂY BUỘC", 54), sub("Kinh Trường Bộ 16") + big("NÓI VỚI NGÀI A NAN", 54), big("ĐỊNH KHÔNG TƯỚNG<br>THÂN DỄ CHỊU HƠN", 50),
         big("BẬC GIÁC NGỘ<br>CŨNG CÓ TUỔI GIÀ", 54), None],
  source=f"Kinh Trường Bộ 16 (dn16:2.25.9–2.25.13), bản Bhikkhu Sujato (CC0): {SUT}/dn16/en/sujato — 'I’m currently eighty years old. Just as a decrepit old cart is kept going by a rope, in the same way, the Realized One’s body is kept going as if by a rope. Sometimes the Realized One, not focusing on any signs … enters and remains in the signless immersion of the heart. Only then does the Realized One’s body become more comfortable.'"),
 dict(id="bud002_k2", day="2026-11-06", slot="12:30", lane="kinh_chu", sid="statue_vietnam_06", kind="kinh_chu", acc=("#f4cf6b", "#2a1a05"),
  title="Đức Phật lấy hình ảnh người mẹ để dạy điều gì?", chip="CÂU KINH QUEN THUỘC · KINH TỪ BI", srcline="KINH TẬP 1.8 · KARANĪYA METTA",
  head='ĐỨC PHẬT LẤY HÌNH ẢNH<br><span class="warm">NGƯỜI MẸ DẠY GÌ?</span>',
  script=["Đức Phật lấy hình ảnh người mẹ để dạy điều gì?",
          "Kinh Từ Bi: như mẹ **che chở bằng cả mạng sống** đứa con duy nhất của mình.",
          "Cũng vậy, hãy **mở rộng một trái tim vô lượng** với mọi loài.",
          "Không lừa dối ai, không **coi thường ai** ở bất cứ nơi đâu.",
          "Dù bị chọc giận, cũng **đừng mong người kia đau khổ**.",
          "Hôm nay, bạn che chở ai như thế?"],
  cards=[None, big("NHƯ MẸ CHE CHỞ<br>CON DUY NHẤT", 54), big("MỞ RỘNG<br>MỘT TRÁI TIM VÔ LƯỢNG", 50), big("KHÔNG LỪA DỐI<br>KHÔNG COI THƯỜNG AI", 50),
         big("BỊ CHỌC GIẬN CŨNG<br>KHÔNG MONG AI KHỔ", 50), None],
  source=f"Kinh Tập 1.8, Kinh Từ Bi (snp1.8:6.1–8.2), bản Bhikkhu Sujato (CC0): {SUT}/snp1.8/en/sujato — 'Let none deceive another, nor look down on anyone anywhere. Though provoked or aggrieved, let them not wish pain on each other. Even as a mother would protect with her life her child, her only child, so too for all creatures unfold a boundless heart.'"),
 dict(id="bud002_t4", day="2026-11-07", slot="03:30", lane="tuong", ai="ai_04.png", kind="tuong", acc=("#9fd3c7", "#0b2420"),
  title="Mệt giữa đường, Đức Phật xin A Nan điều gì?", chip="ĐỜI THƯỜNG CỦA ĐỨC PHẬT", srcline="TRƯỜNG BỘ 16",
  head='MỆT GIỮA ĐƯỜNG,<br><span class="warm">ĐỨC PHẬT XIN GÌ?</span>',
  script=["Mệt giữa đường, Đức Phật xin ngài A Nan điều gì?",
          "Gấp **tấm y làm bốn**, trải ra ngồi nghỉ dưới gốc cây.",
          "Ngài xin nước. A Nan thưa: nước suối vừa bị **năm trăm cỗ xe** làm đục.",
          "Đức Phật vẫn xin, **đến lần thứ ba**.",
          "Kinh kể, A Nan tới, nước đã **trong veo**.",
          "Mệt giữa đường, bạn sẽ xin ai?"],
  cards=[None, big("GẤP Y LÀM BỐN<br>NGỒI NGHỈ GỐC CÂY", 50), sub("A Nan thưa") + big("NƯỚC BỊ 500 CỖ XE<br>LÀM ĐỤC", 50), big("XIN ĐẾN LẦN THỨ 3", 56),
         sub("Kinh Trường Bộ 16") + big("NƯỚC ĐÃ TRONG VEO", 54), None],
  source=f"Kinh Trường Bộ 16 (dn16:4.21.2–4.25.8), bản Bhikkhu Sujato (CC0): {SUT}/dn16/en/sujato — '“Go on then, Ānanda, fold my outer robe in four and spread it out for me. I am tired and will sit down.”' '“Sir, just now around five hundred carts have passed by. The shallow water has been churned up by their wheels, and it flows cloudy and murky.”' 'And for a third time, the Buddha said to Ānanda … when Ānanda approached it flowed transparent, clear, and unclouded.'"),
 dict(id="bud002_d2", day="2026-11-07", slot="23:00", lane="doi_song", sid="statue_china_04", kind="doi_song", acc=("#9fd3c7", "#0b2420"),
  title="Nằm xuống rồi mà đầu vẫn nghĩ chuyện ngày mai?", chip="ĐỜI SỐNG · LỜI PHẬT DẠY", srcline="TRUNG BỘ 131 · MỘT ĐÊM HIỀN",
  head='NẰM XUỐNG RỒI VẪN<br><span class="warm">NGHĨ CHUYỆN NGÀY MAI?</span>',
  script=["Nằm xuống rồi mà đầu vẫn nghĩ chuyện ngày mai, Đức Phật dạy gì?",
          "Kinh Trung Bộ một trăm ba mươi mốt dạy: **đừng chạy theo quá khứ**.",
          "**Đừng mong chờ tương lai.**",
          "Quá khứ đã bỏ lại phía sau, tương lai thì **chưa đến**.",
          "Điều cần làm là **nhìn rõ điều đang có mặt**, ngay hôm nay.",
          "Lúc này, đầu bạn đang ở hôm qua hay ngày mai?"],
  cards=[None, sub("Trung Bộ 131") + big("ĐỪNG CHẠY THEO<br>QUÁ KHỨ", 56), big("ĐỪNG MONG CHỜ<br>TƯƠNG LAI", 56), big("QUÁ KHỨ ĐÃ BỎ LẠI<br>TƯƠNG LAI CHƯA ĐẾN", 48),
         big("NHÌN RÕ ĐIỀU<br>ĐANG CÓ MẶT", 54), None],
  source=f"Kinh Trung Bộ 131, Nhất Dạ Hiền Giả (mn131:3.1–3.6), bản Bhikkhu Sujato (CC0): {SUT}/mn131/en/sujato — 'Don’t run back to the past, don’t anticipate the future. What’s past is left behind, the future has not arrived; and any present phenomenon you clearly discern in every case.'"),
 dict(id="bud002_t5", day="2026-11-08", slot="08:00", lane="tuong", ai="ai_05.png", kind="tuong", acc=("#f2b48a", "#2b1407"),
  title="Đứng xin cơm giữa mùa cày, Đức Phật bị nói gì?", chip="ĐỜI THƯỜNG CỦA ĐỨC PHẬT", srcline="KINH TẬP 1.4",
  head='XIN CƠM GIỮA MÙA CÀY,<br><span class="warm">BỊ NÓI GÌ?</span>',
  script=["Xin cơm giữa mùa cày, Đức Phật bị người nông dân nói gì?",
          "Ông ta bảo: tôi **cày, gieo** rồi mới ăn, ông cũng vậy.",
          "Đức Phật đáp: Ta **cũng cày** và gieo rồi mới ăn.",
          "**Đức tin là hạt giống**, trí tuệ là cái cày.",
          "Nghe xong, ông nông dân xin **quy y** theo Ngài.",
          "Hôm nay bạn đã gieo gì cho bữa cơm tối?"],
  cards=[None, big("“TÔI CÀY, GIEO<br>RỒI MỚI ĂN”", 54), big("“TA CŨNG CÀY<br>VÀ GIEO”", 56), sub("Kinh Tập 1.4") + big("ĐỨC TIN LÀ HẠT GIỐNG<br>TRÍ TUỆ LÀ CÁI CÀY", 46),
         big("ÔNG NÔNG DÂN<br>XIN QUY Y", 54), None],
  source=f"Kinh Tập 1.4 (snp1.4:2.3–6.2, 15.4), bản Bhikkhu Sujato (CC0): {SUT}/snp1.4/en/sujato — '“I plough and sow, ascetic, and then I eat. You too should plough and sow, then you may eat.” “I too plough and sow, brahmin, and then I eat.”' 'Faith is my seed, fervor my rain, and wisdom is my yoke and plough.' 'I go for refuge to the worthy Gotama, to the teaching, and to the mendicant Saṅgha.'"),
 dict(id="bud002_k3", day="2026-11-08", slot="12:30", lane="kinh_chu", sid="statue_japan_01", kind="kinh_chu", acc=("#f4cf6b", "#2a1a05"),
  title="Câu cuối Tâm Kinh “Yết đế yết đế” nghĩa là gì?", chip="CÂU QUEN THUỘC Ở CHÙA", srcline="TÂM KINH · CÂU CHÚ CUỐI",
  head='“YẾT ĐẾ YẾT ĐẾ”<br><span class="warm">NGHĨA LÀ GÌ?</span>',
  script=["Cuối Tâm Kinh, cả chùa đọc: yết đế, yết đế. Nghĩa là gì?",
          "Đây là **tiếng Phạn**, bản Hán và Việt chỉ phiên âm.",
          "Chữ đầu nghĩa là **đã đi**, đã sang bờ bên kia.",
          "Chữ cuối là **bồ đề**: giác ngộ.",
          "Cả câu: **đã đi, đã sang bờ bên kia, giác ngộ**.",
          "Lần tới nghe câu này, bạn sẽ hiểu mình đang đọc gì."],
  cards=[None, big("TIẾNG PHẠN<br>CHỈ PHIÊN ÂM", 56), sub("gate = đã đi") + big("ĐÃ ĐI · ĐÃ ĐI<br>SANG BỜ BÊN KIA", 50), sub("bodhi") + big("BỒ ĐỀ = GIÁC NGỘ", 54),
         big("ĐÃ ĐI, ĐÃ SANG<br>BỜ BÊN KIA, GIÁC NGỘ", 46), None],
  source="Mantra cuối Tâm Kinh: Sanskrit 'gate gate pāragate pārasaṃgate bodhi svāhā'; bản Hán 揭諦揭諦，波羅揭諦，波羅僧揭諦，菩提薩婆訶 (phiên âm: Yết đế, yết đế, Ba la yết đế, Ba la tăng yết đế, Bồ đề tát bà ha). Nghĩa: Max Müller (1884) 'Gone, gone, gone to the other shore, landed at the other shore, “O Wisdom, svāhā!”'; D.T. Suzuki 'O Bodhi, gone, gone…' — tổng hợp tại https://en.wikipedia.org/wiki/Heart_Sutra (mục Mantra). Nghĩa 'tung hô' của svāhā theo cách giải thích phổ biến."),
 dict(id="bud002_t6", day="2026-11-08", slot="14:30", lane="tuong", ai="ai_06.png", kind="tuong", acc=("#9fd3c7", "#0b2420"),
  title="Sư mới đến chùa thấy sân bẩn, Đức Phật dạy làm gì?", chip="ĐỜI THƯỜNG CỦA ĐỨC PHẬT", srcline="LUẬT TẠNG · TIỂU PHẨM 8",
  head='SÂN CHÙA BẨN,<br><span class="warm">ĐỨC PHẬT DẠY GÌ?</span>',
  script=["Sư mới đến chùa, thấy sân bẩn, Đức Phật dạy làm gì?",
          "Một vị sư mới đến mở cửa phòng, **rắn rơi xuống vai**.",
          "Đức Phật liền dạy **phép tắc cho sư mới đến**.",
          "Hỏi chỗ ở, hỏi nước uống, nước rửa chân.",
          "Và nếu **sân bẩn thì quét sân**, cổng bẩn thì quét cổng.",
          "Nơi bạn ở hôm nay, có chỗ nào đang cần quét?"],
  cards=[None, big("MỞ CỬA PHÒNG<br>RẮN RƠI XUỐNG VAI", 52), sub("Luật tạng · Tiểu phẩm 8") + big("PHÉP TẮC CHO<br>SƯ MỚI ĐẾN", 54), big("HỎI CHỖ Ở<br>HỎI NƯỚC UỐNG", 54),
         big("SÂN BẨN → QUÉT SÂN<br>CỔNG BẨN → QUÉT CỔNG", 46), None],
  source=f"Luật tạng, Tiểu phẩm 8 (pli-tv-kd18:1.1.3–1.1.4, 1.2.1, 1.5.11–1.5.12), bản Bhikkhu Brahmali (CC0): {SUT}/pli-tv-kd18/en/brahmali — 'A certain newly-arrived monk lifted the latch of an unoccupied dwelling, opened the door, and entered hastily. A snake fell from above the door frame onto his shoulders.' '[Proper conduct for newly-arrived monks] … he should then enter the monastery carefully and without hurry.' 'If the yard is dirty, he should sweep it. If the gatehouse is dirty, he should sweep it.' (Ảnh Đức Phật quét sân chỉ là minh hoạ; kinh không ghi Ngài tự quét.)"),
]
for it in ITEMS:
    it.update(BASE)
    it["test_cell"] = "W45A_" + it["kind"]
    it["style"] = "ai_cards" if it.get("ai") else "statue_cards"
    it["hook_type"] = "tinh_huong_doi_song"
    it["narrative_structure"] = "cau_hoi_cu_the_lat_nguon_vong_lap"
    it["hypothesis"] = HYP
    it["format_subtag"] = {"tuong": "doi_thuong_cua_phat", "kinh_chu": "cau_niem_quen_thuoc", "doi_song": "cau_hoi_doi_song_test"}[it["kind"]]
    if it["kind"] == "kinh_chu":
        it["novelty_ok"] = "câu niệm/kinh quen thuộc, đã chạy hf_novelty"

for it in ITEMS:   # nguồn hình
    if it.get("ai"):
        continue
    R5.IMG[it["id"]] = (R5.bank_path(it["sid"]), 250, 0.92)
    s = next(x for x in json.loads((ROOT / "output/cl_staging/bud/banks/statues.json").read_text(encoding="utf-8")) if x["id"] == it["sid"])
    R5.CREDITS[it["id"]] = (f"{s['title']} — {s.get('author') or 'Wikimedia Commons'}, {s['license']}", f"{s['title']} · {s['license']}", s["license"])
    R5.CARDS[it["id"]] = it["cards"]
    R5.HEAD[it["id"]] = (it["chip"], it["head"], it["srcline"])
    R5.ACCENT[it["id"]] = it["acc"]
    R5.LISTS.update({})
for it in ITEMS:
    hf_music.short_pick(it)
BGM = {it["id"]: json.loads((ROOT / "output/cl_staging/bud/bgm_shorts.json").read_text())[it["id"]]["file"] for it in ITEMS}
for m in (R4, R5, R6):
    m.BGM.update(BGM)


def library_motion(h: str) -> str:
    h = h.replace('{opacity: 0, y: 26, filter: "blur(8px)"}', '{opacity: 0, y: 26}').replace('filter: "blur(0px)", ', "")
    return h.replace('ease: "power2.out"}, at)', 'ease: "expo.out"}, at)')


def html_ai(it: dict, t: list[float], dur: float) -> str:
    im = Image.open(AI / it["ai"]).convert("RGB")
    k = 1920 / im.height
    im = im.resize((round(im.width * k), 1920), Image.LANCZOS)
    left = (im.width - 1080) // 2
    im = im.crop((left, 0, left + 1080, 1920))
    im = ImageEnhance.Brightness(im).enhance(0.95)
    acc, ink = it["acc"]
    cards = it["cards"]
    card_html = "".join(f'<div class="card" id="c{i}">{c}</div>' for i, c in enumerate(cards) if c)
    shown = [i for i, c in enumerate(cards) if c]
    js = []
    for i in shown:
        nxt = next((j for j in range(i + 1, len(cards)) if cards[j]), None)
        nxt = nxt if nxt is not None else len(t) - 1
        js.append(f'show("#c{i}", T[{i}]); hide("#c{i}", T[{nxt}]);')
    return f"""<!doctype html><html lang="vi"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" /><title>{it['id']}</title>
<style>{B.font_css()}{B.BASE_CSS}
#root {{ background: #0a0807; }}
#photo {{ left: 0; top: 0; width: 1080px; height: 1920px; z-index: 1; transform-origin: 540px 700px; }}
#photo img {{ width: 100%; height: 100%; display: block; }}
#shade {{ left: 0; top: 0; width: 1080px; height: 1920px; z-index: 2;
  background: linear-gradient(180deg, rgba(10,8,7,0.9) 0px, rgba(10,8,7,0.75) 250px, rgba(10,8,7,0) 440px),
    linear-gradient(0deg, rgba(8,6,5,0.96) 0px, rgba(8,6,5,0.9) 330px, rgba(8,6,5,0.62) 560px, rgba(8,6,5,0) 800px); }}
#chip {{ background: {acc}; color: {ink}; }}
.warm {{ color: {acc}; }}
.card {{ top: 1250px; }}
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
const show = (id, at) => tl.fromTo(id, {{opacity: 0, y: 26}}, {{opacity: 1, y: 0, duration: 0.6, ease: "expo.out"}}, at);
const hide = (id, at) => tl.to(id, {{opacity: 0, y: -18, duration: 0.45, ease: "power1.in"}}, at - 0.45);
tl.fromTo("#photo", {{scale: 1.0}}, {{scale: 1.05, duration: T[T.length - 1] + 1, ease: "none"}}, 0);
{' '.join(js)}
</script></body></html>"""


def main() -> int:
    html_only = "--html-only" in sys.argv
    only = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)
    R6.guards(ITEMS)
    jobs = []
    for it in ITEMS:
        R6.tts(it, (0.6, 0.8))
        it["dur"] = round(json.loads((D / f"{it['id']}_final.json").read_text())["duration_s"] + 0.5 + HOLD, 2)
        t = R5.segs(it["id"], 0.5)
        h = html_ai(it, t, it["dur"]) if it.get("ai") else library_motion(R5.html_statue(it["id"], t, it["dur"]))
        jobs.append((it, h))
    clean = {"id", "day", "slot", "replaces", "lane", "test_cell", "style", "title", "script", "source", "series", "dur",
             "batch_id", "hook_type", "narrative_structure", "hypothesis", "format_subtag", "novelty_ok"}
    plan = []
    for it, _ in jobs:
        p = {k: it[k] for k in clean if k in it}
        p["media_credit"] = (AI_CREDIT if it.get("ai") else R5.CREDITS[it["id"]])[0]
        p["image"] = ("grokbot/bud_doithuong_bg_1103/out/" + it["ai"]) if it.get("ai") else it["sid"]
        plan.append(p)
    validate(plan)
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    for it, h in jobs:
        (B.COMP / f"_r_{it['id']}.html").write_text(h, encoding="utf-8")
        print(f"[{it['id']}] dur={it['dur']}s")
    if html_only:
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    for it, _ in jobs:
        rid = it["id"]
        if only and rid not in only:
            continue
        silent, mp4 = D / f"{rid}_silent.mp4", OUT / f"{rid}.mp4"
        B.to_trash(silent); B.to_trash(mp4)
        print(f"[{rid}] render ...", flush=True)
        R4.render(f"_r_{rid}.html", silent)
        vl, gain, ml = R4.mix(rid, silent, D / f"{rid}_final.wav", mp4, it["dur"], 0.5, True)
        B.to_trash(silent)
        meta = {"ok": True, "output": str(mp4.relative_to(ROOT)), "duration_s": it["dur"], "style": it["style"], "lane": it["lane"],
                "bgm": f"bgm/{BGM[rid]}", "bgm_title": hf_music.TITLES[BGM[rid]], "bgm_gain": round(gain, 4),
                "media_credits": [{"id": rid, "kind": "ai" if it.get("ai") else "commons", "credit": (AI_CREDIT if it.get("ai") else R5.CREDITS[rid])[0]}],
                "voice": "Binh", "lufs": {"voice": round(vl, 1), "mix": round(ml, 1), "offset_db": -20.0}, "sfx_credit": B.BELL_CREDIT}
        (OUT / f"{rid}.render.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{rid}] xong | LUFS giọng {vl:.1f} mix {ml:.1f}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
