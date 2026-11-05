"""Cảnh viết tay cho Long BAO THANH THIÊN Ngoài Đời Thật: Bao Chửng (ch00-ch06; ch07-ch13 ở gen_scenes2.py).

    python data/long/bao-thanh-thien/gen_scenes.py
Ảnh: lấy theo số thứ tự trong research.json (05/11/2026, không chạy lại research) và kiểm tên file.
Không ảnh AI, không clip phim, không hình diễn viên. Chân dung Bao Chửng đều là tranh/tượng đời sau: ghi rõ trên nhãn.
"""
import json
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = D.parents[2]
sys.path.insert(0, str(ROOT / "motion" / "long"))
from scenekit import FILMV, chapter, kin, sc, write  # noqa: E402

_RES = json.loads((ROOT / "output" / "long" / D.name / "research.json").read_text(encoding="utf-8"))["images"]


def im(i, must):
    f = _RES[i]["file"]
    if must not in f:
        raise SystemExit(f"ảnh #{i} là {f!r}, không chứa {must!r}: research.json đã đổi?")
    return f


IMGS = {
    "statue": im(0, "BaoZheng"), "tomb": im(1, "Baogongmu1"), "sketch": im(3, "scth"), "court": im(4, "Kaifeng court"),
    "novel": im(6, "Ten Thousand Flowers"), "shrine": im(7, "haiching"), "p8": im(8, "Famous Men - Bao Zheng.jpg"), "p9": im(9, "歷代聖賢"),
    "garden": im(12, "Imperial-Garden"), "pag13": im(13, "Iron Pagoda d"), "bjmap": im(14, "Outer city"), "kfmap": im(19, "Kaifeng in Northern Song.jpg"),
    "kf1950": im(22, "1950s"), "model1": im(23, "Dynasty d"), "model2": im(24, "Model of Kaifeng"), "gate": im(25, "Daliang"),
    "dragon": im(26, "Dragon Pavilion"), "xiang": im(27, "Xiangguo"), "street": im(29, "122"), "fu": im(30, "6162261508"),
    "renzong": im(33, "Renzong.jpg"), "caoemp": im(34, "Cao Empress"), "rtomb": im(35, "Yongzhao"), "palace": im(38, "Song-Palace1"),
    "guests": im(41, "Ma Lin"), "banknote": im(59, "Plate of Paper"), "cavalry": im(57, "Cavalry"), "qm65": im(65, "清明上河图.jpg"),
    "mifei": im(75, "Mi Fei"), "yuji": im(79, "Yuji"), "yingzao": im(80, "Yingzao"), "hefeimap": im(85, "HefeiWallMap"),
    "zqwall": im(102, "肇庆城墙"), "zqrock": im(104, "Qixing Yan"), "zqview": im(106, "七星岩远眺.JPG"), "zqmei": im(110, "Mei'an"),
    "zqtower": im(111, "Yuejiang"), "zqgate": im(113, "牌坊"), "opera": im(114, "京劇"), "gate116": im(116, "Bianjing city gate"),
    "qm118": im(118, "清明上河圖.png"), "bao124": im(124, "Baogong Temple"), "p125": im(125, "998-1061"), "p140": im(140, "Bao Zheng.png"),
    "yanluo": im(142, "Yanluo"), "slab": im(143, "Ink Slab"), "epit": im(144, "Rubbings"), "rel1": im(149, "9974272044"),
    "rel2": im(150, "9974271424"), "rel3": im(151, "9974312026"), "rel4": im(152, "9974248185"), "hf153": im(153, "2012-06.JPG"),
    "guil": im(154, "02 2012-06"), "hf156": im(156, "panoramio.jpg"), "hf167": im(167, "安徽合肥包公祠"), "ren181": im(181, "Song Renzong.jpg"),
    "ren185": im(185, "宋代帝半身像册.05.宋仁宗.jpg"), "party": im(188, "Elegant Party"), "wc196": im(196, "L0075719"), "wc198": im(198, "L0075721"),
    "breit": im(199, "Breitenstein"), "pag203": im(203, "1049 AD"), "pag211": im(211, "View of Kaifeng"), "map1141": im(193, "1141"),
    "hf165": im(165, "Bao Gong Ci"),
    "liu": im(190, "Empress of Zhenzong"), "hydro": im(192, "grain mill"), "taizu": im(52, "Taizu"),
    "literary": im(70, "Literary Garden"), "go": im(76, "Go players"), "pag77": im(77, "开封铁塔"), "pag216": im(216, "Park 03"), "pag219": im(219, "Park 09"),
    "bao155": im(155, "6162185552"), "hf157": im(157, "JtWang"), "hf163": im(163, "2010-10-16"), "bao90": im(90, "panoramio.jpg"), "park93": im(93, "浮莊"),
    "hf166": im(166, "2014.11"), "p141": im(141, "Men - Bao Zheng 2"), "zq107": im(107, "往市区方向远眺"), "zq109": im(109, "远眺-2"),
    "pag17": im(17, "6162387102"), "pag215": im(215, "Park 01"), "pag217": im(217, "Park 07"), "pag218": im(218, "Park 08"), "model3": im(61, "10340676846"), "bridge18": im(18, "Small Bridge"),
    "clock58": im(58, "Clock Tower"), "star68": im(68, "Star Map 1"), "star69": im(69, "Star Map 2"), "ship67": im(67, "Songrivership3"), "zq105": im(105, "牌坊广场全景"),
}

GEO = {
    "china": {"countries": ["China"], "context": ["Mongolia", "Vietnam", "Laos", "Myanmar", "India", "Nepal", "Bhutan", "Kazakhstan", "Kyrgyzstan",
                                                   "Tajikistan", "Pakistan", "Russia", "North Korea", "South Korea", "Japan", "Taiwan", "Thailand"],
              "labels": {"China": "TRUNG QUỐC"}, "bbox": [96.0, 18.0, 128.0, 46.0], "box": [260, 110, 1660, 880],
              "pins": [{"name": "Hợp Phì", "lon": 117.28, "lat": 31.86, "label": "HỢP PHÌ"}, {"name": "Khai Phong", "lon": 114.31, "lat": 34.8, "label": "KHAI PHONG"},
                       {"name": "Triệu Khánh", "lon": 112.47, "lat": 23.05, "label": "ĐOAN CHÂU"}, {"name": "Bắc Kinh", "lon": 116.4, "lat": 39.9, "label": "BẮC KINH"},
                       {"name": "Thiên Trường", "lon": 118.99, "lat": 32.68, "label": "THIÊN TRƯỜNG"}, {"name": "Tây Hạ", "lon": 106.2, "lat": 38.5, "label": "TÂY HẠ"},
                       {"name": "Liêu", "lon": 117.0, "lat": 42.5, "label": "LIÊU"}, {"name": "Hùng Châu", "lon": 116.1, "lat": 39.0, "label": "HÙNG CHÂU"},
                       {"name": "Trác Châu", "lon": 115.97, "lat": 39.49, "label": "TRÁC CHÂU"}, {"name": "Hàng Châu", "lon": 120.15, "lat": 30.27, "label": "HÀNG CHÂU"}]},
}

# b-roll Pexels (đều ngang, SDR; đã soát clip_sheet)
V = dict(ink1="856911", ink2="9785157", inks="39583060", sumi="39583060", seal="9785157", letter="30117908", pen="856911", incense="2865316",
         tincense="34070866", candle_red="39579888", arch="36382688", court="39550230", heaven="40233547", lamp="32540543", rainroof="17079051",
         raindrops="6252550", lantern="35182250", lantern_rain="39333459", watertown="39531176", canal="39519061", carving="36239253",
         relief="36239253", docs="30117908", abooks="11765182", obooks="11765182", magnifier="6980366", skull="5762177", skull_glass="5762179",
         bones="10041487", dig="3967264", fly1="7379692", fly2="18304655", fly3="30568888", market="36494728", dali="40479561",
         aerial_sunset="30103886", aerial="30103893", misty="38368356", cemfog="38368356", candles="32540543", flood="19486650", demol="5594429",
         gogame="39277761", inkwater="18333375", rainarch="40328878", tiles="17079051", temple66="35977046", tentr="36382688", ttl="33009780",
         dalipag="40442683", bamlantern="35244435", bamboo="39611578", tea="39277761")

CH = {}

CH["ch00"] = dict(hud={"k": "MỞ ĐẦU", "t": "MƯỜI MỘT CHIẾC QUAN TÀI"}, bgm={"mood": "tense", "at": 0, "gain": 0.12}, scenes=[
    sc("date", None, vid=V["cemfog"], tone="noir", day="HỢP PHÌ · AN HUY · TRUNG QUỐC", date="08.1973"),
    sc("map", 1, geo="china", pins=[{"name": "Hợp Phì", "label": "HỢP PHÌ · AN HUY", "at": [1, "xương"]}], zoom="Hợp Phì", zoomK=1.5),
    sc("photo", 2, img="hefeimap", tone="sepia", move="in", kin=kin(("BỐN THÁNG ĐÀO BỚI", [2, "Bốn"]), ("ĐÃ XONG", [2, "xong"], "acc")),
       label={"k": "BẢN ĐỒ HỢP PHÌ XƯA", "v": "TƯ LIỆU · THÀNH LŨY CŨ", "at": [2, "đào"]}),
    sc("print", 3, img="epit", tone="color", side={"k": "KHU MỘ HỌ BAO", "h": "12 NGÔI MỘ", "hAt": [3, "mười"],
       "lines": [{"text": "Bia mộ và *11 bộ hài cốt*", "at": [3, "bia"]}]}),
    sc("counter", 4, bg="tomb", **{"from": 0, "to": 11}, suffix=" QUAN TÀI NHỎ", countAt=[4, "mười"], label="XẾP HÀI CỐT VÀO TỪNG CHIẾC"),
    sc("photo", 5, img="p8", tone="color", move="in", kin=kin(("BAO CHỬNG · 999 — 1062", [5, "Bao"], "acc"), ("BAO THANH THIÊN", [5, "Thiên"])),
       label={"k": "BAO CHỬNG (包拯)", "v": "TRANH VẼ ĐỜI SAU · KHÔNG CÓ CHÂN DUNG ĐƯƠNG THỜI", "at": [5, "hài"]}),
    sc("file", 6, k="CON CHÁU HỌ BAO", name="XIN ĐEM VỀ\nLÀNG CŨ", desc="Để chôn theo họ tộc", bg="hf156",
       rows=[{"k": "ĐỀ NGHỊ", "v": "Chôn ở *quê nhà*", "at": [6, "chôn"]}]),
    sc("slam", 7, vid=V["court"], tone="noir", text="KHÔNG\nCHO CHÔN", hitAt=[7, "không"], sub="BÍ THƯ CÔNG XÃ Ở LÀNG · THEO LỜI MỘT NGƯỜI CHÁU KỂ LẠI"),
    sc("quote", 9, text="Bao Công là kẻ bảo vệ vương triều phong kiến, không được chôn ở quê.", by="BÍ THƯ CÔNG XÃ · THEO LỜI MỘT NGƯỜI CHÁU KỂ LẠI",
       lbl="TRÍCH DỊCH", qline=9, typeAt=[9, "Bao"]),
    sc("kinetic", 10, vid=V["rainroof"], tone="noir", items=kin(("CHÍN TRĂM NĂM SAU", [10, "Chín"], "sm"), ("QUAN TÀI KHÔNG AI NHẬN", [10, "không"], "acc"))),
    sc("broll", 11, vid=V["raindrops"], tone="noir", veil=0.4, illus=FILMV, kin=kin(("GIẤU TẠM", [11, "giấu"]), ("DƯỚI MÁI HIÊN DỘT", [11, "mái"], "acc"))),
    sc("kinetic", 12, vid=V["lamp"], tone="night", items=kin(("MỘT ĐÊM NỌ", [12, "đêm"], "sm"), ("LÉN ĐEM ĐI CHÔN", [12, "lén"], "acc"))),
    sc("map", 13, geo="china", pins=[{"name": "Hợp Phì", "at": [13, "Một"]}, {"name": "Bắc Kinh", "label": "BẮC KINH · GIÁM ĐỊNH", "at": [13, "Một"]}],
       routes=[{"from": "Hợp Phì", "to": "Bắc Kinh", "at": [13, "Một"], "until": [13, "định"], "bend": 0.15}]),
    sc("slam", 14, vid=V["skull_glass"], tone="noir", text="CHỈ HAI DÒNG", white=True, hitAt=[14, "hai"], sub="KẾT QUẢ GIÁM ĐỊNH"),
    sc("photo", 15, img="opera", tone="color", move="in", kin=kin(("ÔNG TRÊN MÀN ẢNH", [15, "màn"]), ("GƯƠNG MẶT ĐEN", [16, "Gương"], "acc"), ("VẦNG TRĂNG KHUYẾT", [16, "vầng"])),
       label={"k": "NHÂN VẬT KINH KỊCH", "v": "TRANH LỤA CUỐI ĐỜI THANH · BẢO TÀNG MET", "at": [15, "thấy"]}),
    sc("question", 17, bg="guil", text="Nếu ba chiếc đao không có trong hồ sơ,\nông đã xử những vụ án nào?"),
    sc("slam", 18, bg="yanluo", text="DIÊM LA", white=True, hitAt=[18, "Diêm"], sub="VÌ SAO DÂN KINH THÀNH GỌI ÔNG NHƯ VẬY?"),
    sc("kinetic", 19, bg="tomb", items=kin(("NẮM XƯƠNG CUỐI CÙNG", [19, "nắm"]), ("BÂY GIỜ NẰM Ở ĐÂU?", [19, "bây"], "acc"))),
])

CH["ch01"] = dict(hud={"k": "CHƯƠNG 01", "t": "HAI HỒ SƠ"}, bgm={"mood": "mystery", "at": 0, "gain": 0.12}, scenes=[
    chapter("1", "CHƯƠNG MỘT", "HAI\nHỒ SƠ", "NGƯỜI TRONG PHIM · NGƯỜI TRONG SỬ", "Hai", bg="p140"),
    sc("broll", 1, vid=V["docs"], tone="noir", veil=0.4, illus=FILMV, kin=kin(("HAI TẬP HỒ SƠ", [1, "hai"]), ("ĐẶT TRÊN BÀN", [1, "bàn"], "acc"))),
    sc("file", 2, k="HỒ SƠ A", name="NGƯỜI\nTRONG PHIM", desc="Ông quan áo đen giữa công đường", bg="opera",
       rows=[{"k": "TRANG PHỤC", "v": "Quan phục *đen*", "at": [3, "quan"]}, {"k": "NƠI NGỒI", "v": "Giữa công đường", "at": [3, "công"]}]),
    sc("ledger", 4, title="HAI CHIẾC ĐAO ĐẦU TIÊN", bg="guil", rows=[{"k": "ĐẦU CHÓ", "v": "DÂN THƯỜNG", "at": [4, "chó"]}, {"k": "ĐẦU HỔ", "v": "QUAN LẠI", "at": [4, "hổ"]}]),
    sc("slam", [4, "rồng"], bg="guil", text="ĐẦU RỒNG\nCHÉM CẢ HOÀNG THÂN", hitAt=[4, "rồng"]),
    sc("kinetic", 5, bg="bao124", items=kin(("KHÔNG AI Ở KINH THÀNH", [5, "Không"], "sm"), ("DÁM ĐỘNG VÀO ÔNG", [5, "dám"], "acc"))),
    sc("file", 6, k="HỒ SƠ B", name="NGƯỜI\nTRONG SỬ", desc="Mỏng hơn nhiều", bg="sketch"),
    sc("date", 7, vid=V["ink1"], tone="noir", day="TỐNG SỬ · CÁC SỬ GIA ĐỜI NGUYÊN SOẠN", date="1345"),
    sc("counter", 8, bg="palace", **{"from": 0, "to": 60}, suffix="+ NĂM", countAt=[8, "sáu"], label="SAU KHI TRIỀU TỐNG SỤP ĐỔ"),
    sc("kinetic", 9, vid=V["abooks"], tone="noir", items=kin(("VÀI BẢN TẤU CÒN SÓT LẠI", [9, "bản"]), ("DÒNG CHÉP CỦA NGƯỜI ĐƯƠNG THỜI", [9, "dòng"], "sm"))),
    sc("map", 10, geo="china", pins=[{"name": "Hợp Phì", "label": "SINH NĂM 999 · HỢP PHÌ", "at": [10, "Hợp"]}], zoom="Hợp Phì", zoomK=1.4),
    sc("date", 11, bg="pag203", day="MẤT Ở KHAI PHONG · THỌ KHOẢNG 63 TUỔI", date="1062"),
    sc("slam", 12, bg="p8", text="KHÔNG MỘT\nCHIẾC ĐAO", white=True, hitAt=[12, "đao"]),
    sc("kinetic", 13, vid=V["ink2"], tone="noir", items=kin(("THỨ HỒ SƠ A", [13, "hồ"], "sm"), ("KHÔNG DÁM CÓ", [13, "không"], "acc"))),
    sc("split", 14, title="HỒ SƠ B CÓ GÌ", a={"img": "yingzao", "label": "VỤ ÁN NHỎ ĐẾN BUỒN CƯỜI", "at": [14, "Những"]},
       b={"img": "qm65", "label": "BẢN TẤU LỚN ĐẾN DỄ MẤT CHỨC", "at": [14, "bản"]}),
    sc("ledger", 15, title="CÁCH ĐỌC HỒ SƠ", bg="mifei", rows=[{"k": "ĐỌC", "v": "HỒ SƠ B · TỪNG VỤ", "at": [15, "đọc"]}, {"k": "THỨ TỰ", "v": "THEO NĂM THÁNG", "at": [15, "thứ"]}]),
    sc("slam", 16, bg="opera", text="HỒ SƠ A CHEN VÀO\nTA GHI CHỖ GÃY", hitAt=[16, "ghi"]),
    sc("question", 17, bg="p9", text="Và ở cuối,\nta phán xử cả hai."),
    sc("slam", 18, bg="statue", text="KHÔNG PHẢI\nQUAN TÒA", white=True, hitAt=[19, "không"], sub="CHI TIẾT CẦN NHỚ NGAY TỪ ĐẦU"),
    sc("timeline", 20, bg="kfmap", items=[{"year": "TRI HUYỆN", "text": "Thiên Trường"}, {"year": "TRI CHÂU", "text": "Đoan Châu"}, {"year": "NGỰ SỬ", "text": "*Khai Phong*"},
       {"year": "PHÓ SỨ", "text": "*Khu mật viện*"}]),
    sc("counter", 21, bg="fu", **{"from": 0, "to": 1}, suffix=" NĂM", countAt=[21, "một"], label="ĐỨNG ĐẦU PHỦ KHAI PHONG · NƠI SINH RA TIẾNG TĂM"),
    sc("question", 22, bg="p140", text="Vậy ông là ai,\nnếu không phải quan tòa trong phim?"),
    sc("photo", 23, img="hf167", tone="color", move="in", kin=kin(("MỘT CẬU HỌC TRÒ Ở HỢP PHÌ", [23, "cậu"]), ("MỘT QUYẾT ĐỊNH KỲ LẠ", [23, "quyết"], "acc")),
       label={"k": "ĐỀN THỜ BAO CÔNG · HỢP PHÌ", "v": "ẢNH NGÀY NAY", "at": [23, "Hợp"]}),
])

CH["ch02"] = dict(hud={"k": "CHƯƠNG 02", "t": "MƯỜI NĂM Ở NHÀ CHỊU TANG"}, bgm={"mood": "quiet", "at": 0, "gain": 0.12}, scenes=[
    chapter("2", "CHƯƠNG HAI", "MƯỜI NĂM Ở NHÀ\nCHỊU TANG", "HỢP PHÌ · 999 — 1037", "Mười", bg="hefeimap"),
    sc("kinetic", 1, vid=V["arch"], tone="noir", items=kin(("NGƯỜI THI ĐỖ THƯỜNG", [1, "Người"], "sm"), ("LO CHẠY CHỨC", [1, "chạy"], "acc"))),
    sc("slam", 2, bg="sketch", text="ÔNG LÀM\nĐIỀU NGƯỢC LẠI", hitAt=[2, "ngược"]),
    sc("question", 3, vid=V["heaven"], tone="noir", text="Vừa đỗ kỳ thi lớn nhất đời,\nbạn có dám từ chối chiếc ghế quan?"),
    sc("file", 4, k="HỒ SƠ B · GIA CẢNH", name="BAO CHỬNG", desc="Sinh trong gia đình trí thức bậc trung", bg="p9",
       rows=[{"k": "CHA", "v": "Một viên quan nhỏ", "at": [5, "Cha"]}, {"k": "ÔNG NỘI", "v": "Dân thường", "at": [5, "nội"]}]),
    sc("counter", 6, vid=V["sumi"], tone="noir", **{"from": 0, "to": 29}, suffix=" TUỔI", countAt=[6, "tuổi"], label="ĐỖ TIẾN SĨ · KỲ THI CAO NHẤT TRIỀU TỐNG"),
    sc("photo", 7, img="mifei", tone="color", move="in", kin=kin(("THỜI TỐNG", [7, "Tống"], "sm"), ("KHOA CỬ QUAN TRỌNG HƠN BAO GIỜ HẾT", [7, "khoa"], "acc")),
       label={"k": "THƯ PHÁP ĐỜI TỐNG", "v": "BÚT TÍCH MI PHẤT · TƯ LIỆU", "at": [7, "Tống"]}),
    sc("split", 8, title="CÁCH CHỌN QUAN", a={"img": "cavalry", "label": "DÒNG DÕI QUÂN SỰ · QUÝ TỘC", "at": [8, "dòng"]},
       b={"img": "guests", "label": "BÀI THI", "at": [8, "bài"]}),
    sc("photo", 9, img="party", tone="color", move="pan", kin=kin(("CON NHÀ BẬC TRUNG", [9, "người"]), ("CŨNG NGỒI VÀO GHẾ QUAN", [9, "ghế"], "acc"))),
    sc("file", 10, k="TRIỀU ĐÌNH CỬ", name="TRI HUYỆN\nKIẾN XƯƠNG", desc="Chức quan đầu tiên được giao", bg="mifei"),
    sc("slam", 11, vid=V["incense"], tone="noir", text="ÔNG XIN HOÃN", hitAt=[11, "xin"]),
    sc("kinetic", 12, bg="hf165", items=kin(("CHA MẸ ĐÃ GIÀ", [12, "cha"]), ("Ở NHÀ PHỤNG DƯỠNG", [12, "phụng"], "acc"))),
    sc("kinetic", 13, vid=V["candle_red"], tone="night", items=kin(("CHA MẸ LẦN LƯỢT MẤT", [13, "lần"]))),
    sc("file", 14, k="LỄ THỜI TỐNG", name="ĐỂ TANG", desc="Con phải để tang, tránh việc quan", bg="tomb",
       rows=[{"k": "ĐIỀU LỆ", "v": "Tránh việc quan", "at": [14, "tránh"]}]),
    sc("counter", 15, vid=V["lantern_rain"], tone="noir", **{"from": 0, "to": 10}, suffix=" NĂM", countAt=[15, "mười"], label="Ở NHÀ · GẦN MƯỜI NĂM"),
    sc("photo", 16, img="p9", tone="sepia", move="in", kin=kin(("TIẾN SĨ NGỒI NHÀ", [16, "đỗ"]), ("TÓC BẠC DẦN", [16, "tóc"], "acc"))),
    sc("kinetic", 17, vid=V["pen"], tone="noir", items=kin(("NGHE NHƯ MỘT CHI TIẾT ĐẠO ĐỨC", [17, "đạo"], "sm"), ("DỄ THƯƠNG", [17, "dễ"]))),
    sc("slam", 18, bg="rel1", text="NHƯNG CÓ HỆ QUẢ", hitAt=[18, "hệ"]),
    sc("timeline", 19, bg="hefeimap", items=[{"year": "999", "text": "Sinh ở *Hợp Phì*"}, {"year": "29 TUỔI", "text": "Đỗ *tiến sĩ*"}, {"year": "≈ 10 NĂM", "text": "Ở nhà *chịu tang*"},
       {"year": "39 TUỔI", "text": "Nhận chức *đầu tiên*"}]),
    sc("counter", 20, bg="rel2", **{"from": 0, "to": 39}, suffix=" TUỔI", countAt=[20, "tuổi"], label="NHẬN CHỨC ĐẦU TIÊN"),
    sc("kinetic", 21, vid=V["market"], tone="noir", items=kin(("KHÔNG PHẢI THẦN ĐỒNG", [21, "thần"]), ("BAY LÊN NHANH", [21, "bay"], "acc"))),
    sc("slam", 22, bg="gate116", text="KHÔNG CÓ NGƯỜI\nCHỐNG LƯNG", hitAt=[22, "chống"]),
    sc("kinetic", 23, vid=V["dali"], tone="noir", items=kin(("CHỨC NHỎ", [23, "nhỏ"], "sm"), ("NƠI HẺO LÁNH", [23, "hẻo"]), ("SỐNG BẰNG LƯƠNG", [23, "lương."], "acc"))),
    sc("question", 24, bg="rel3", text="Một người 39 tuổi mới có quyền xử án.\nÔng nhìn đời từ phía nào?"),
    sc("photo", 26, img="rel4", tone="color", move="in", kin=kin(("NHÌN ĐỜI TỪ PHÍA DÂN NGHÈO", [26, "dân"]), ("GẦN MƯỜI NĂM", [26, "gần"], "acc")),
       label={"k": "PHÙ ĐIÊU CUỘC ĐỜI BAO CHỬNG", "v": "PHÒNG TƯỞNG NIỆM · HỢP PHÌ", "at": [26, "Ông"]}),
    sc("map", 27, geo="china", pins=[{"name": "Thiên Trường", "label": "THIÊN TRƯỜNG · AN HUY", "at": [27, "Thiên"]}], zoom="Thiên Trường", zoomK=1.6),
    sc("slam", 28, vid=V["obooks"], tone="noir", text="VỤ ÁN ĐẦU TIÊN\nTRONG SỬ", white=True, hitAt=[28, "đầu"]),
    sc("question", 29, bg="statue", text="Nó liên quan tới\nmột con bò."),
])

CH["ch03"] = dict(hud={"k": "CHƯƠNG 03", "t": "CÁI LƯỠI CON BÒ"}, bgm={"mood": "tense", "at": 0, "gain": 0.12}, scenes=[
    chapter("3", "CHƯƠNG BA", "CÁI LƯỠI\nCON BÒ", "THIÊN TRƯỜNG · VỤ ÁN ĐẦU TIÊN", "Cái", bg="rel1"),
    sc("broll", 1, vid=V["watertown"], tone="noir", veil=0.4, illus=FILMV, kin=kin(("MỘT BUỔI SÁNG", [1, "buổi"], "sm"), ("CÓ NGƯỜI ĐẾN BÁO QUAN", [1, "báo"], "acc"))),
    sc("kinetic", 2, bg="hf153", items=kin(("CON BÒ BỊ CẮT MẤT LƯỠI", [2, "cắt"]), ("KẺ CẮT LÀ AI?", [2, "kẻ"], "acc"))),
    sc("question", 3, vid=V["court"], tone="noir", text="Nếu bạn là quan huyện,\nbạn sẽ làm gì?"),
    sc("ledger", 4, title="BA CÁCH THÔNG THƯỜNG", bg="fu", rows=[{"k": "TÌM", "v": "DẤU CHÂN", "at": [4, "dấu"]}, {"k": "TRA HỎI", "v": "HÀNG XÓM", "at": [4, "hàng"]},
       {"k": "BẮT", "v": "NGƯỜI ĐI NGANG", "at": [4, "bắt"]}]),
    sc("slam", 5, bg="p125", text="ÔNG KHÔNG\nLÀM GÌ TRONG SỐ ĐÓ", hitAt=[5, "không"]),
    sc("kinetic", 6, vid=V["ink1"], tone="noir", items=kin(("CHỈ BẢO CHỦ BÒ", [6, "chỉ"], "sm"), ("MỘT CÂU", [6, "một"], "acc"))),
    sc("quote", 7, text="Cứ về đi, giết con bò ấy mà bán.", by="BAO CHỬNG · THEO TỐNG SỬ", lbl="TRÍCH DỊCH", qline=7, typeAt=[7, "Cứ"]),
    sc("photo", 8, img="rel3", tone="color", move="pan", kin=kin(("CHỦ BÒ LÀM THEO", [8, "chủ"], "acc")),
       label={"k": "PHÙ ĐIÊU CUỘC ĐỜI BAO CHỬNG", "v": "PHÒNG TƯỞNG NIỆM · HỢP PHÌ", "at": [8, "chủ"]}),
    sc("kinetic", 9, vid=V["raindrops"], tone="noir", items=kin(("CON BÒ MẤT LƯỠI", [9, "mất"], "sm"), ("KHÔNG SỐNG ĐƯỢC LÂU", [9, "sống"], "acc"))),
    sc("kinetic", 10, vid=V["lantern"], tone="night", items=kin(("ÍT LÂU SAU", [10, "lâu"], "sm"), ("LẠI CÓ NGƯỜI ĐẾN CỬA QUAN", [10, "cửa"]))),
    sc("slam", 11, bg="hf156", text="LẦN NÀY\nLÀ ĐỂ TỐ GIÁC", hitAt=[11, "tố"]),
    sc("file", 12, k="ĐƠN TỐ GIÁC", name="TỰ TIỆN\nGIẾT BÒ", desc="Hắn báo chủ bò đã tự tiện giết bò", bg="rel2",
       rows=[{"k": "NGƯỜI TỐ", "v": "*Không rõ tên*", "at": [12, "Hắn"]}]),
    sc("photo", 13, img="rel2", tone="sepia", move="in", kin=kin(("BÒ LÀ SỨC KÉO CÀY", [13, "bò"]), ("GIẾT TRỘM BÒ LÀ TỘI", [13, "giết"], "acc")),
       label={"k": "PHÙ ĐIÊU CUỘC ĐỜI BAO CHỬNG", "v": "PHÒNG TƯỞNG NIỆM · HỢP PHÌ", "at": [13, "sức"]}),
    sc("counter", 14, vid=V["abooks"], tone="noir", **{"from": 0, "to": 1}, suffix=" NĂM TÙ KHỔ SAI", countAt=[14, "một"], label="MỨC PHẠT · THEO MỘT BẢN GHI CHÉP"),
    sc("slam", 15, bg="court", text="BAO CHỬNG\nQUÁT LÊN", hitAt=[15, "quát"]),
    sc("quote", 16, text="Sao ngươi cắt lưỡi bò của người ta rồi lại đi tố cáo họ?", by="BAO CHỬNG · THEO TỐNG SỬ", lbl="TRÍCH DỊCH", qline=16, typeAt=[16, "Sao"]),
    sc("photo", 17, img="court", tone="color", move="in", kin=kin(("KẺ KIA HOẢNG SỢ", [17, "hoảng"]), ("NHẬN TỘI NGAY TRƯỚC CÔNG ĐƯỜNG", [17, "nhận"], "acc")),
       label={"k": "CÔNG ĐƯỜNG PHỤC DỰNG · KHAI PHONG", "v": "CÔNG TRÌNH HIỆN ĐẠI · ẢNH NGÀY NAY", "at": [17, "công"]}),
    sc("kinetic", 18, vid=V["candles"], tone="noir", items=kin(("HÃY NHÌN MẠCH LÝ", [18, "mạch"]))),
    sc("ledger", 19, title="AI BIẾT BÒ SẼ BỊ GIẾT?", bg="rel3", rows=[{"k": "CHỦ BÒ", "v": "LÀM THEO LỜI QUAN", "at": [19, "bò"]}, {"k": "AI KHÁC", "v": "*CHỈ KẺ BIẾT TRƯỚC*", "at": [20, "Chỉ"]}]),
    sc("slam", 21, bg="p9", text="KHÔNG TÌM\nCHỨNG CỨ", white=True, hitAt=[21, "không"]),
    sc("sketch", 22, art="parcel", title="Một cái bẫy: kẻ có tội tự bước vào"),
    sc("kinetic", 23, vid=V["arch"], tone="noir", items=kin(("KHÔNG PHẢI KHOA HỌC", [23, "khoa"]))),
    sc("kinetic", 24, bg="hf153", items=kin(("HIỂU LÒNG NGƯỜI", [24, "hiểu"]), ("HIỂU LUẬT", [24, "luật."], "acc"))),
    sc("split", 25, title="KIỂU TỘI PHẠM ĂN THUA", a={"img": "statue", "label": "ĐỦ KHÔN ĐỂ LÊN KẾ HOẠCH", "at": [25, "đủ"]},
       b={"img": "p140", "label": "KHÔNG ĐỦ KHÔN ĐỂ DỪNG", "at": [25, "không"]}),
    sc("kinetic", 26, vid=V["ink2"], tone="noir", items=kin(("KHÔNG BẮT ĐẦU BẰNG VIỆC TÌM HUNG THỦ", [26, "bắt"], "sm"))),
    sc("slam", 27, bg="bao124", text="ĐOÁN HUNG THỦ\nSẼ LÀM GÌ TIẾP", hitAt=[27, "đoán"]),
    sc("file", 28, k="TỐNG SỬ · QUYỂN 316", name="CHỈ VÀI DÒNG", desc="Sử chép rất ngắn cho vụ này", bg="sketch",
       rows=[{"k": "TÊN NGƯỜI CHỦ BÒ", "v": "KHÔNG CÓ", "at": [29, "tên"]}, {"k": "NĂM XẢY RA", "v": "KHÔNG CÓ", "at": [29, "năm"]}, {"k": "KẺ BỊ PHẠT", "v": "KHÔNG RÕ", "at": [29, "kẻ"]}]),
    sc("kinetic", 30, vid=V["obooks"], tone="noir", items=kin(("CHI TIẾT CÒN LẠI", [30, "chi"], "sm"), ("DO NGƯỜI ĐỜI SAU THÊM", [30, "người"], "acc"))),
    sc("photo", 31, img="zqview", tone="color", move="pan", kin=kin(("NƠI ĐẤT ĐAI HỨA HẸN NHIỀU QUÀ HƠN", [31, "đất"])),
       label={"k": "ĐOAN CHÂU · NAY LÀ TRIỆU KHÁNH", "v": "THẠCH THẤT SƠN · ẢNH NGÀY NAY", "at": [31, "nơi"]}),
    sc("slam", 32, bg="slab", text="VÙNG LÀM\nNGHIÊN MỰC", hitAt=[32, "nghiên"]),
])

CH["ch04"] = dict(hud={"k": "CHƯƠNG 04", "t": "NGHIÊN MỰC ĐOAN CHÂU"}, bgm={"mood": "mystery", "at": 0, "gain": 0.12}, scenes=[
    chapter("4", "CHƯƠNG BỐN", "NGHIÊN MỰC\nĐOAN CHÂU", "TRIỆU KHÁNH · 1040 — 1043", "Nghiên", bg="slab"),
    sc("date", 1, bg="zqwall", day="BAO CHỬNG LÀM TRI CHÂU ĐOAN CHÂU", date="1040"),
    sc("map", [1, "Đoan"], geo="china", pins=[{"name": "Triệu Khánh", "label": "ĐOAN CHÂU · TRIỆU KHÁNH", "at": [1, "Triệu"]}], zoom="Triệu Khánh", zoomK=1.5),
    sc("photo", 2, img="slab", tone="color", move="in", kin=kin(("NGHIÊN MỰC ĐÁ", [3, "đá"]), ("LOẠI TỐT NHẤT TRIỀU TỐNG", [3, "tốt"], "acc")),
       label={"k": "NGHIÊN MỰC BẮC TỐNG", "v": "BẢO TÀNG AN HUY · TRONG MỘ HỌ BAO", "at": [3, "Nghiên"]}),
    sc("file", 4, k="CỐNG PHẨM HẰNG NĂM", name="NỘP LÊN\nTRIỀU ĐÌNH", desc="Mỗi năm châu phải nộp một số nghiên", bg="zqrock",
       rows=[{"k": "MÓN CỐNG", "v": "Nghiên đá *Đoan*", "at": [4, "nghiên"]}]),
    sc("kinetic", 5, vid=V["magnifier"], tone="noir", items=kin(("ÔNG XEM SỔ SÁCH", [5, "xem"], "sm"), ("THẤY MỘT ĐIỀU LẠ", [5, "lạ."], "acc"))),
    sc("slam", 6, bg="zqrock", text="GẤP HÀNG CHỤC LẦN\nSỐ CỐNG PHẨM", white=True, hitAt=[6, "gấp"], sub="THỢ BỊ BẮT LÀM QUÁ SỐ · CÁC QUAN TIỀN NHIỆM"),
    sc("org", 7, bg="zqmei", nodes=[{"id": "t", "t": "THỢ ĐÁ ĐOAN CHÂU", "s": "LÀM QUÁ SỐ", "cls": "top", "at": [7, "Phần"]},
       {"id": "q", "t": "PHẦN DƯ", "s": "KHÔNG NỘP LÊN KINH", "p": "t", "at": [7, "không"]}, {"id": "r", "t": "NGƯỜI CÓ QUYỀN THẾ", "s": "NHẬN BIẾU", "p": "q", "cls": "acc", "at": [8, "quyền"]}]),
    sc("slam", 9, bg="zqtower", text="ĐƯỜNG DÂY\nBẰNG ĐÁ", white=True, hitAt=[9, "đường"], sub="THAM NHŨNG VẬN HÀNH BẰNG SỰ QUEN THUỘC"),
    sc("kinetic", 10, vid=V["ink1"], tone="noir", items=kin(("TỐNG SỬ GHI CÁCH PHÁ", [10, "Tống"], "sm"), ("CHỈ TRONG MỘT CÂU", [10, "một"], "acc"))),
    sc("quote", 11, text="Ông ra lệnh cho thợ chỉ làm vừa đủ số cống. Hết nhiệm kỳ, ông không mang về một chiếc nghiên nào.", by="TỐNG SỬ · QUYỂN 316", lbl="TRÍCH DỊCH", qline=11,
       typeAt=[11, "Ông"]),
    sc("slam", 12, bg="slab", text="HÃY NHỚ\nCHI TIẾT NÀY", hitAt=[12, "nhớ"], sub="NÓ SẼ QUAY LẠI"),
    sc("kinetic", 13, vid=V["inks"], tone="noir", items=kin(("MỘT CHIẾC NGHIÊN", [13, "nghiên"]), ("KHÔNG ĐÁNG BAO NHIÊU TIỀN", [13, "không"], "acc"))),
    sc("slam", 14, bg="zqmei", text="VÌ RẺ\nNÊN LÀ CON DAO", white=True, hitAt=[14, "dao"]),
    sc("kinetic", 15, vid=V["tincense"], tone="noir", items=kin(("BIẾU MỘT CHIẾC NGHIÊN", [15, "biếu"], "sm"), ("AI CŨNG THẤY CHẲNG CÓ GÌ", [15, "chẳng"], "acc"))),
    sc("kinetic", 16, bg="zqgate", items=kin(("MỖI NGƯỜI NHẬN MỘT CHÚT", [16, "nhận"]))),
    sc("photo", 17, img="zqwall", tone="bw", move="in", film=True, kin=kin(("CẢ HỆ THỐNG CÙNG NHẬN", [17, "cả"]), ("KHÔNG AI CÒN NÓI VỀ NÓ", [17, "không"], "acc"))),
    sc("slam", 18, bg="zqrock", text="NGƯỜI TỪ CHỐI ĐẦU TIÊN\nTHÀNH KẺ PHÁ LUẬT NGẦM", hitAt=[18, "phá"]),
    sc("question", 19, vid=V["lamp"], tone="night", text="Nhìn vụ này như một\nhồ sơ hình sự."),
    sc("ledger", 20, title="HỒ SƠ NGHIÊN MỰC", bg="zqview", rows=[{"k": "NẠN NHÂN", "v": "NHỮNG NGƯỜI THỢ", "at": [20, "Nạn"]}, {"k": "BỊ ÉP LÀM", "v": "QUÁ SỐ", "at": [20, "quá"]}]),
    sc("ledger", 21, title="HỒ SƠ NGHIÊN MỰC", bg="zqview", rows=[{"k": "KẺ CHỦ MƯU", "v": "KHÔNG AI CẢ", "at": [21, "chủ"]}, {"k": "VÀ", "v": "TẤT CẢ MỌI NGƯỜI", "at": [21, "tất"]}]),
    sc("slam", 22, bg="slab", text="HUNG KHÍ\nMỘT CHIẾC NGHIÊN MỰC", white=True, hitAt=[22, "chiếc"]),
    sc("kinetic", 23, vid=V["sumi"], tone="noir", items=kin(("BAO CHỬNG PHÁ VỤ NÀY", [23, "phá"], "sm"), ("BẰNG CÁCH KHÔNG LÀM GÌ", [23, "không"], "acc"))),
    sc("slam", 24, bg="zqwall", text="CHỈ ĐẶT LẠI\nCON SỐ CHO ĐÚNG", hitAt=[24, "đặt"]),
    sc("photo", 25, img="epit", tone="color", move="in", kin=kin(("KHU MỘ HỌ BAO · HỢP PHÌ", [25, "khu"], "sm"), ("NGHIÊN MỰC ĐÁ BẮC TỐNG", [25, "nghiên"], "acc")),
       label={"k": "BIA MỘ THÁC BẢN · BAO CHỬNG ĐỨNG ĐẦU", "v": "BẢO TÀNG AN HUY", "at": [25, "người"]}),
    sc("sketch", 26, art="parcel", title="Bản chép tay: “không mang về một chiếc nghiên”"),
    sc("kinetic", 27, vid=V["watertown"], tone="noir", items=kin(("NGƯỜI DÂN ĐOAN CHÂU", [27, "Người"], "sm"), ("CÓ THỂ CHẲNG BAO GIỜ BIẾT TÊN ÔNG", [27, "chẳng"]))),
    sc("slam", 28, bg="gate116", text="NHƯNG TRIỀU ĐÌNH\nTHÌ BIẾT", hitAt=[28, "triều"]),
    sc("photo", 29, img="street", tone="color", move="in", kin=kin(("GỌI VỀ KINH", [29, "gọi"]), ("VÀO MỘT CHỨC MỚI", [29, "chức"], "acc")),
       label={"k": "NGỰ NHẬT KHAI PHONG", "v": "ĐƯỜNG PHỤC DỰNG · ẢNH NGÀY NAY", "at": [29, "kinh"]}),
    sc("kinetic", 30, vid=V["candles"], tone="noir", items=kin(("MỘT CHỨC KHÔNG TẠO RA BẠN BÈ", [30, "không"], "sm"), ("CHỈ TẠO RA KẺ THÙ", [30, "kẻ"], "acc"))),
])

CH["ch05"] = dict(hud={"k": "CHƯƠNG 05", "t": "NGƯỜI ĐƯỢC PHÉP HẶC CẢ HOÀNG THÂN"}, bgm={"mood": "epic", "at": 0, "gain": 0.11}, scenes=[
    chapter("5", "CHƯƠNG NĂM", "NGƯỜI ĐƯỢC PHÉP\nHẶC CẢ HOÀNG THÂN", "KHAI PHONG · 1044 — 1049", "Người", bg="kfmap"),
    sc("kinetic", 1, vid=V["aerial_sunset"], tone="noir", items=kin(("VÌ SAO CHỨC MỚI NGUY HIỂM?", [1, "nguy"]), ("PHẢI BIẾT TRIỀU ĐÌNH LÚC ĐÓ", [1, "triều"], "sm"))),
    sc("photo", 2, img="renzong", tone="color", move="in", kin=kin(("TỐNG NHÂN TÔNG", [2, "Nhân"], "acc"), ("TRỊ VÌ 41 NĂM · DÀI NHẤT TRIỀU TỐNG", [2, "trị"])),
       label={"k": "TỐNG NHÂN TÔNG (1010 — 1063)", "v": "TRANH CHÂN DUNG · TƯ LIỆU", "at": [2, "Vua"]}),
    sc("kinetic", 3, bg="banknote", items=kin(("KINH TẾ PHÁT TRIỂN", [3, "kinh"]), ("QUÂN ĐỘI YẾU", [3, "quân"], "acc"))),
    sc("map", 4, geo="china", pins=[{"name": "Liêu", "label": "NƯỚC LIÊU · PHÍA BẮC", "at": [4, "bắc"]}, {"name": "Tây Hạ", "label": "NƯỚC TÂY HẠ · PHÍA TÂY", "at": [4, "tây"]},
       {"name": "Khai Phong", "label": "KINH ĐÔ TỐNG", "at": [4, "Phía"]}]),
    sc("date", 5, bg="map1141", day="THỦ LĨNH TÂY HẠ XƯNG ĐẾ · ĐÒI NGANG HÀNG VUA TỐNG", date="1038"),
    sc("date", 6, bg="cavalry", day="HAI BÊN GIẢNG HÒA · ĐỔI LẠI LÀ QUÀ HẰNG NĂM", date="1044"),
    sc("photo", 7, img="palace", tone="color", move="pan", kin=kin(("ĐỂ GIỮ HÒA BÌNH", [7, "giữ"], "sm"), ("TRẢ NHỮNG KHOẢN TIỀN CỐNG RẤT LỚN", [7, "trả"], "acc"))),
    sc("slam", 8, bg="banknote", text="THUẾ\nTĂNG MẠNH", white=True, hitAt=[8, "tăng"]),
    sc("kinetic", 9, vid=V["relief"], tone="noir", items=kin(("NÔNG DÂN", [9, "Nông"], "sm"), ("NGHÈO KÉO DÀI", [9, "nghèo"], "acc"))),
    sc("file", 10, k="KHOẢNG NHỮNG NĂM 1040", name="CẢI CÁCH", desc="Đã được thử, rồi thất bại", bg="garden",
       rows=[{"k": "NGƯỜI ĐỀ XƯỚNG", "v": "Phạm Trọng Yêm · Phú Bật", "at": [11, "Phạm"]}, {"k": "", "v": "Hàn Kỳ · Âu Dương Tu", "at": [11, "Hàn"]}]),
    sc("slam", 12, bg="party", text="THẤT BẠI KHI\nPHẠM TRỌNG YÊM RỜI CHỨC", hitAt=[12, "thất"]),
    sc("date", 13, bg="street", day="BAO CHỬNG TRỞ LẠI KINH THÀNH KHAI PHONG", date="1044"),
    sc("file", 14, k="CHỨC MỚI", name="GIÁM SÁT\nNGỰ SỬ", desc="Kiểm toán viên của quyền lực", bg="yingzao"),
    sc("kinetic", 16, bg="mifei", items=kin(("ĐỌC · XÉT · HẶC TỘI QUAN LẠI", [16, "đọc"]), ("KỂ CẢ NGƯỜI LỚN NHẤT", [16, "kể"], "acc"))),
    sc("counter", 17, vid=V["letter"], tone="noir", **{"from": 0, "to": 13}, suffix=" BẢN TẤU", countAt=[17, "mười"], label="TRONG HAI NĂM ĐẦU · ÍT NHẤT"),
    sc("ledger", 18, title="CHỦ ĐỀ CÁC BẢN TẤU", bg="mifei", rows=[{"k": "QUÂN ĐỘI", "v": "●", "at": [18, "quân"]}, {"k": "THUẾ KHÓA", "v": "●", "at": [18, "thuế"]},
       {"k": "KHOA CỬ", "v": "●", "at": [18, "khoa"]}, {"k": "QUAN THAM · QUAN BẤT TÀI", "v": "●", "at": [18, "quan"]}]),
    sc("kinetic", 19, bg="gate116", items=kin(("CHỨC NGỰ SỬ", [19, "chức"], "sm"), ("ĐƯA LÊN CAO HOẶC ĐƯA ĐI ĐÀY", [19, "đi"], "acc"))),
    sc("map", 20, geo="china", pins=[{"name": "Liêu", "label": "SỨ THẦN SANG LIÊU", "at": [20, "sứ"]}, {"name": "Khai Phong", "at": [20, "Năm"]}],
       routes=[{"from": "Khai Phong", "to": "Liêu", "at": [20, "cử"], "until": [20, "Liêu."], "bend": 0.15}]),
    sc("kinetic", 21, vid=V["market"], tone="noir", items=kin(("MỘT QUAN LIÊU", [21, "quan"], "sm"), ("BUỘC TỘI NHÀ TỐNG", [21, "buộc"], "acc"))),
    sc("map", 22, geo="china", pins=[{"name": "Hùng Châu", "label": "HÙNG CHÂU · CỬA HÔNG", "at": [22, "Hùng"]}], zoom="Hùng Châu", zoomK=1.8),
    sc("slam", 23, bg="cavalry", text="BAO CHỬNG\nĐÁP NGAY", hitAt=[23, "đáp"]),
    sc("quote", 24, text="Ở Trác Châu, các ngài cũng từng mở cửa. Việc dò xét biên giới đâu cần phải mở cửa hông?", by="BAO CHỬNG · THEO TỐNG SỬ", lbl="TRÍCH DỊCH", qline=24,
       typeAt=[24, "Ở"]),
    sc("map", 25, geo="china", pins=[{"name": "Trác Châu", "label": "TRÁC CHÂU · PHÍA LIÊU", "at": [25, "Liêu"]}], zoom="Trác Châu", zoomK=1.8),
    sc("photo", 26, img="rel1", tone="color", move="in", kin=kin(("VỤ LƯỠI BÒ", [26, "lưỡi"], "sm"), ("KẺ GIAN TỰ MÂU THUẪN BẰNG MỘT CÁI BẪY", [27, "bẫy"], "acc")),
       label={"k": "PHÙ ĐIÊU CUỘC ĐỜI BAO CHỬNG", "v": "PHÒNG TƯỞNG NIỆM · HỢP PHÌ", "at": [26, "Hãy"]}),
    sc("kinetic", 28, bg="cavalry", items=kin(("SỨ LIÊU", [28, "đối"], "sm"), ("TỰ MÂU THUẪN BẰNG CHÍNH LỜI VỪA NÓI", [28, "chính"], "acc"))),
    sc("slam", 29, bg="p125", text="CÁCH NHAU CẢ CHỤC NĂM\nCÙNG MỘT KIỂU TƯ DUY", hitAt=[29, "cùng"]),
    sc("kinetic", 30, vid=V["ink2"], tone="noir", items=kin(("KHÔNG PHẢI ĐAO HAY GƯƠM", [30, "đao"], "sm"), ("LẬT LẠI CÂU HỎI", [31, "lật"], "acc"))),
    sc("kinetic", 32, vid=V["lantern_rain"], tone="noir", items=kin(("MỘT CHUYỆN KHÔNG THỂ NÉ", [32, "không"]))),
    sc("photo", 33, img="caoemp", tone="color", move="in", kin=kin(("HỌ HÀNG CỦA SỦNG PHI", [33, "họ"]), ("SẮP ĐƯỢC THĂNG QUAN", [33, "thăng"], "acc")),
       label={"k": "HOÀNG HẬU ĐỜI NHÂN TÔNG", "v": "TRANH CHÂN DUNG · NGỰ DUNG", "at": [33, "sủng"]}),
    sc("slam", 34, vid=V["candle_red"], tone="night", text="MỘT CANH BẠC", hitAt=[34, "canh"], sub="THẮNG THÌ ĐƯỢC TIẾNG · THUA THÌ MẤT CHỨC"),
    sc("slam", 36, bg="renzong", text="TRƯƠNG\nNGHIÊU TÁ", white=True, hitAt=[36, "Trương"]),
])

if __name__ == "__main__":
    import importlib.util
    extra = D / "gen_scenes2.py"
    if extra.exists():
        sys.modules["gen_scenes"] = sys.modules[__name__]
        s2 = importlib.util.spec_from_file_location("g2", extra)
        m = importlib.util.module_from_spec(s2)
        s2.loader.exec_module(m)
        CH.update(m.CH)
    import balance
    IMGS, swaps = balance.balance(CH, IMGS)
    FOCUS = {"p125": 0.3, "ren181": 0.2, "renzong": 0.2, "p8": 0.62, "p9": 0.55, "p140": 0.6, "opera": 0.4, "liu": 0.3, "bao155": 0.2, "statue": 0.3, "sketch": 0.5,
             "hf153": 0.6, "guil": 0.6, "wc196": 0.4, "wc198": 0.4, "kf1950": 0.35, "pag217": 0.35, "pag218": 0.35, "pag77": 0.3, "pag13": 0.3, "pag17": 0.3,
             "rel1": 0.5, "rel2": 0.55, "p141": 0.3, "novel": 0.45}
    for _n, _v in CH.items():
        for _s in _v["scenes"]:
            _k = _s.get("img") or _s.get("bg")
            if _k in FOCUS and "focus" not in _s:
                _s["focus"] = [0.5, FOCUS[_k]]
    for sw in swaps:
        print("  đổi", *sw)
    _fit = D / "fit.json"   # thao tác khớp thời lượng cảnh (2,5–9 s) theo timing thật: xem fit_calc.py
    if _fit.exists():
        for _op in json.loads(_fit.read_text(encoding="utf-8")):
            _sc = CH[_op["ch"]]["scenes"]
            if _op["op"] == "shift":
                _sc[1]["at"] = [1, _op["word"]]
            elif _op["op"] == "drop_next":
                _i = _op["idx"]
                if _sc[_i].get("at") is not None:
                    _sc[_i + 1]["at"] = _sc[_i]["at"]
                del _sc[_i]
            elif _op["op"] == "drop_prev":
                del _sc[_op["idx"]]
            elif _op["op"] == "clip":
                _sc[_op["idx"]]["vid"] = _op["vid"]
            elif _op["op"] == "sync":
                import fit_calc
                fit_calc.apply_sync(_sc[_op["idx"]])
    _used = set()

    def _walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("img", "bg") and isinstance(v, str):
                    _used.add(v)
                _walk(v)
        elif isinstance(o, list):
            for x in o:
                _walk(x)
    for _v in CH.values():
        _walk(_v["scenes"])
    IMGS = {k: v for k, v in IMGS.items() if k in _used}
    write(__file__, CH, IMGS, GEO, endcardBg="p125")
