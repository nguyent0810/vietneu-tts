"""VSD lô 1 (PO duyệt 10 đề 16/11/2026): dựng 10 spec Shorts Studio + packaging cho hàng đợi pipelines/vsd.

Chạy: .venv/bin/python builders/short/build_vsd_lo1.py  -> output/cl_staging/vsd/specs/<id>.json
Ảnh + credits.json (hf_commons.fetch) ở output/cl_staging/vsd/img/ (gitignored).
Workflow (PO duyệt (a) 16/11): Lead soát spec + chạy pipelines/vsd/check_layout.sh trên Oracle -> chép spec vào
pipelines/vsd/queue/ready/ -> n8n tự render + đăng. Bẫy bố cục: memory feedback_studio_vsd_layout_lessons.
Lịch: 2 bài/ngày 11:30 + 18:00 VN (04:30Z, 11:00Z), 17–21/11/2026.
Nguồn kiểm chứng: de_xuat_lo1_2026-11-16.md + ghi chú từng đề dưới đây.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "output" / "cl_staging" / "vsd"
IMG = "output/cl_staging/vsd/img/"
CRED = json.loads((HERE / "img" / "credits.json").read_text(encoding="utf-8"))
SIZE = {}
try:
    from PIL import Image
    for p in (HERE / "img").glob("t*_*.*"):
        if p.suffix != ".json":
            SIZE[p.stem] = Image.open(p).size
except ImportError:
    pass


def pan(k, line, label, stops, **kw):
    w, h = SIZE.get(k, (1600, 1000))
    return {"device": "pan_tour", "line": line, "img": IMG + CRED[k]["path"].split("/")[-1], "w": w, "h": h,
            "label": "", "stops": stops, "ghost": "", **kw}


def credit(*keys):
    return ["Ảnh: " + CRED[k]["credit"].split("\n")[0].replace(", Wikimedia Commons", "") + " (Wikimedia Commons)" for k in keys]


TAGS = ["#vansudia", "#lichsuvietnam", "#shorts"]
S = []

# ---------------- 1. Thăng Long (Toàn thư BK q.2 năm 1010; Chiếu dời đô; Minh Mạng đặt Hà Nội 1831)
S.append(dict(
    id="vsd_l1_thanglong", lane="vsd_su", theme="archive", kicker="SỬ · NĂM 1010", foot="Theo Đại Việt sử ký toàn thư",
    lines=[
        "Một kinh đô đổi tên, chỉ vì **một con rồng**.",
        "Mùa thu năm 1010, vua Lý Thái Tổ rời Hoa Lư, ra thành Đại La.",
        "Sử chép: thuyền vua vừa tới, có **rồng vàng** hiện ra bên thuyền ngự.",
        "Nhà vua đổi tên thành là **Thăng Long**, nghĩa là rồng bay lên.",
        "Còn lý do thật thì nằm trong Chiếu dời đô, viết từ trước đó.",
        "Đất rộng mà bằng, cao mà thoáng, dân khỏi cảnh ngập lụt.",
        "Cái tên Thăng Long đi cùng kinh đô hơn tám trăm năm.",
        "Tới năm 1831, vua Minh Mạng mới đặt tên mới là **Hà Nội**.",
        "Bạn biết Hà Nội còn những **tên gọi nào khác**?",
    ],
    scenes=[
        {"device": "hook_slam", "line": 0, "kick": "ĐẠI LA · NĂM 1010", "groups": [{"text": "Đổi tên vì"}, {"text": "MỘT CON RỒNG", "big": True, "at": [0, "rồng"]}], "markAt": [0, "rồng"], "allAtStart": True, "ghost": ""},
        pan("t1_lythaito", 1, "TƯỢNG LÝ THÁI TỔ · HÀ NỘI",
            [{"x": .5, "y": .5, "z": 1, "at": [1, "vua"], "note": "Lý Thái Tổ"},
             {"x": .5, "y": .3, "z": 1.8, "at": [2, "rồng"]}]),
        {"device": "time_spine", "line": 3, "kick": "ĐỔI TÊN · NĂM 1010",
         "items": [{"yr": "Đại La", "label": "Tên cũ", "at": [3, "nhà"]}, {"yr": "Thăng Long", "label": "Rồng bay lên", "at": [3, "thăng"]}], "ghost": ""},
        {"device": "source_card", "line": 4, "source": "CHIẾU DỜI ĐÔ · 1010", "ref": "Đại La",
         "snippet": "Đất [[rộng mà bằng]], cao mà thoáng, dân khỏi ngập lụt.", "hlAt": [5, "rộng"], "seal": "LÝ THÁI TỔ", "sealAt": [5, "thoáng"], "ghost": ""},
        {"device": "time_spine", "line": 6, "kick": "TÊN KINH ĐÔ",
         "items": [{"yr": "1010", "label": "Thăng Long", "at": [6, "thăng"]}, {"yr": "1831", "label": "Hà Nội", "at": [7, "minh"]}], "ghost": ""},
        {"device": "close", "line": 8, "q": "Bạn biết Hà Nội còn những **tên gọi nào khác**?", "markSpan": 4, "ghost": "", "fade": True, "lh": 1.55},
    ],
    packaging=dict(title="Vì Sao Đại La Đổi Tên Thành Thăng Long?",
                   description_first_line="Vì sao Đại La đổi tên thành Thăng Long: điềm rồng vàng năm 1010 và lý do thật trong Chiếu dời đô.",
                   hashtags=["#thanglong", *TAGS],
                   sources=["Nguồn: Đại Việt sử ký toàn thư, Bản kỷ q.2 (năm Canh Tuất 1010); Chiếu dời đô (Lý Thái Tổ, 1010)."] + credit("t1_lythaito"),
                   publish_slot_utc="2026-11-17T04:30:00Z"),
))

# ---------------- 2. Bạch Đằng 1288 (Toàn thư 1288; Yên Giang phát lộ khi đắp đê 1958; Đồng Vạn Muối, Đồng Má Ngựa)
S.append(dict(
    id="vsd_l1_bachdang", lane="vsd_su", theme="archive", kicker="SỬ · NĂM 1288", foot="Theo Toàn thư · khảo cổ Quảng Yên",
    lines=[
        "Trận đánh hơn **bảy trăm năm** trước, vẫn để lại cọc gỗ dưới ruộng.",
        "Năm 1288, Trần Hưng Đạo cho đóng cọc gỗ xuống lòng sông Bạch Đằng.",
        "Nước triều lên, cọc chìm dưới mặt sông, thuyền Nguyên kéo vào không hay biết.",
        "Triều rút, cả đoàn thuyền **mắc cọc**, quân Trần từ hai bờ đánh ra.",
        "Tướng Ô Mã Nhi bị bắt sống ngay trên sông.",
        "Gần bảy thế kỷ sau, người dân đắp đê ở Yên Giang, Quảng Yên đào trúng những cọc gỗ đầu tiên.",
        "Về sau, các nhà khảo cổ tìm thêm bãi cọc ở Đồng Vạn Muối và Đồng Má Ngựa.",
        "Nhiều cọc nay nằm trong bảo tàng, đầu vẫn còn **vót nhọn**.",
        "Nếu đứng bên bãi cọc ấy, bạn muốn hỏi người xưa **điều gì**?",
    ],
    scenes=[
        {"device": "hook_slam", "line": 0, "kick": "SÔNG BẠCH ĐẰNG",
         "groups": [{"text": "700 năm sau"}, {"text": "CỌC VẪN CÒN", "big": True, "at": [0, "cọc"]}], "markAt": [0, "ruộng"], "allAtStart": True, "ghost": "1288"},
        pan("t2_coc2", 1, "CỌC GỖ BẠCH ĐẰNG · BẢO TÀNG",
            [{"x": .5, "y": .45, "z": 1, "at": [1, "trần"], "note": "Cọc gỗ 1288"},
             {"x": .35, "y": .2, "z": 2.2, "at": [1, "lòng"], "note": "Đầu vót nhọn"}]),
        {"device": "time_spine", "line": 2, "kick": "THỦY TRIỀU BẠCH ĐẰNG",
         "items": [{"yr": "Triều lên", "label": "Cọc chìm dưới nước", "at": [2, "nước"]}, {"yr": "Triều rút", "label": "Thuyền Nguyên mắc cọc", "at": [3, "triều"]}], "ghost": ""},
        {"device": "source_card", "line": 4, "source": "TOÀN THƯ · NĂM 1288", "ref": "Ô Mã Nhi",
         "snippet": "[[Bị bắt sống]] trên sông Bạch Đằng", "hlAt": [4, "bắt"], "seal": "1288", "sealAt": [4, "sông"], "ghost": ""},
        {"device": "time_spine", "line": 5, "kick": "BÃI CỌC PHÁT LỘ",
         "items": [{"yr": "1288", "label": "Trận Bạch Đằng", "at": [5, "gần"]}, {"yr": "1958", "label": "Yên Giang", "at": [5, "yên"]},
                   {"yr": "Sau đó", "label": "Vạn Muối · Má Ngựa", "at": [6, "vạn"]}], "ghost": ""},
        pan("t2_coc2", 7, "CỌC GỖ BẠCH ĐẰNG · BẢO TÀNG", [{"x": .62, "y": .18, "z": 2.4, "at": [7, "vót"], "note": "Vót nhọn"}]),
        {"device": "close", "line": 8, "q": "Đứng bên bãi cọc, bạn muốn hỏi người xưa **điều gì**?", "markSpan": 2, "ghost": "", "fade": True, "lh": 1.55},
    ],
    packaging=dict(title="Bãi Cọc Bạch Đằng 1288 Nay Còn Không?",
                   description_first_line="Bãi cọc Bạch Đằng 1288: trận thủy triều của Trần Hưng Đạo và những cọc gỗ đào được dưới ruộng Quảng Yên.",
                   hashtags=["#bachdang", "#tranhungdao", *TAGS],
                   sources=["Nguồn: Đại Việt sử ký toàn thư (năm Mậu Tý 1288); Khu di tích Bạch Đằng, Quảng Yên (bãi cọc Yên Giang phát lộ năm 1958, Đồng Vạn Muối, Đồng Má Ngựa)."] + credit("t2_coc2"),
                   publish_slot_utc="2026-11-18T11:00:00Z"),
))

# ---------------- 3. Hoàng thành (khai quật 18 Hoàng Diệu 2002–2004; UNESCO 2010)
S.append(dict(
    id="vsd_l1_hoangthanh", lane="vsd_su", theme="archive", kicker="SỬ · 18 HOÀNG DIỆU", foot="UNESCO · Di sản thế giới 2010",
    lines=[
        "Định xây một tòa nhà, người ta đào lên **mười ba thế kỷ**.",
        "Năm 2002, khu đất 18 Hoàng Diệu, Hà Nội được khai quật trước khi xây Nhà Quốc hội.",
        "Dưới lớp đất là nền móng cung điện, giếng nước, gạch ngói của nhiều triều đại.",
        "Có dấu tích từ thời Đại La, qua Lý, Trần, Lê, tới tận thời Nguyễn.",
        "Các lớp ấy **chồng lên nhau**, ngay giữa lòng một thành phố vẫn đang sống.",
        "Năm 2010, đúng dịp Thăng Long tròn nghìn năm, UNESCO công nhận đây là **di sản thế giới**.",
        "Nay bạn có thể vào xem tận mắt các hố khai quật ở 18 Hoàng Diệu.",
        "Bạn đã từng đứng trước **những lớp đất ấy** chưa?",
    ],
    scenes=[
        {"device": "hook_slam", "line": 0, "kick": "18 HOÀNG DIỆU · HÀ NỘI", "groups": [{"text": "Đào móng nhà"}, {"text": "LỘ 13 THẾ KỶ", "big": True, "at": [0, "mười"]}], "markAt": [0, "kỷ"], "allAtStart": True, "ghost": ""},
        pan("t3_bacmon", 1, "CỬA BẮC · HOÀNG THÀNH THĂNG LONG",
            [{"x": .5, "y": .5, "z": 1, "at": [1, "khu"], "note": "Cửa Bắc"},
             {"x": .45, "y": .55, "z": 1.6, "at": [2, "nền"]}]),
        {"device": "list_build", "line": 3, "title": "Các lớp dấu tích",
         "items": [{"text": "Đại La", "sub": "trước thời Lý", "at": [3, "đại"]}, {"text": "Lý · Trần", "sub": "kinh thành Thăng Long", "at": [3, "lý"]},
                   {"text": "Lê · Nguyễn", "sub": "các lớp trên cùng", "at": [3, "nguyễn"]}], "ghost": ""},
        pan("t3_kinhthien", 4, "ĐIỆN KÍNH THIÊN · ẢNH CUỐI THẾ KỶ 19",
            [{"x": .5, "y": .5, "z": 1, "at": [4, "chồng"], "note": "Điện Kính Thiên"}]),
        {"device": "source_card", "line": 5, "source": "UNESCO · DI SẢN THẾ GIỚI", "ref": "2010",
         "snippet": "Khu trung tâm Hoàng thành Thăng Long – [[Hà Nội]]", "hlAt": [5, "công"], "seal": "DI SẢN", "sealAt": [5, "di"], "ghost": ""},
        {"device": "close", "line": 7, "q": "Bạn đã từng đứng trước **những lớp đất ấy** chưa?", "markSpan": 4, "ghost": "", "fade": True, "lh": 1.55},
    ],
    packaging=dict(title="Hoàng Thành Thăng Long: Vì Sao Là Di Sản Thế Giới?",
                   description_first_line="Hoàng thành Thăng Long thành di sản thế giới vì một cuộc khai quật ở 18 Hoàng Diệu, lộ ra mười ba thế kỷ kinh đô.",
                   hashtags=["#hoangthanhthanglong", *TAGS],
                   sources=["Nguồn: UNESCO World Heritage Centre, hồ sơ 1328 (2010); khai quật khảo cổ 18 Hoàng Diệu 2002–2004 (Viện Khảo cổ học)."] + credit("t3_bacmon", "t3_kinhthien"),
                   publish_slot_utc="2026-11-20T04:30:00Z"),
))

# ---------------- 4. Tây Sơn ăn Tết sớm (Hoàng Lê nhất thống chí hồi 14 — tiểu thuyết lịch sử; vào Thăng Long trưa mùng 5 Kỷ Dậu 1789)
S.append(dict(
    id="vsd_l1_taysontet", lane="vsd_su", theme="archive", kicker="SỬ · TẾT KỶ DẬU 1789", foot="Hoàng Lê nhất thống chí · hồi 14",
    lines=[
        "Ăn Tết trước, đánh trận sau, rồi vào Thăng Long đúng **mùng năm Tết**.",
        "Cuối năm 1788, vua Quang Trung kéo quân ra Bắc đánh quân Thanh.",
        "Tới núi Tam Điệp, nhà vua cho quân **ăn Tết sớm**, ngay ngày ba mươi tháng Chạp.",
        "Hoàng Lê nhất thống chí kể, ông hẹn tướng sĩ: mồng bảy năm mới sẽ vào Thăng Long mở tiệc.",
        "Đêm mồng ba, quân Tây Sơn hạ đồn Hà Hồi.",
        "Mờ sáng mồng năm, đồn Ngọc Hồi vỡ.",
        "Trưa hôm ấy, nhà vua đã vào Thăng Long, **sớm hơn hai ngày** so với lời hẹn.",
        "Theo bạn, ăn Tết sớm là để vui quân, hay để **giữ bí mật**?",
    ],
    scenes=[
        {"device": "hook_slam", "line": 0, "kick": "QUANG TRUNG RA BẮC",
         "groups": [{"text": "Ăn Tết trước"}, {"text": "ĐÁNH SAU", "big": True, "at": [0, "đánh"]}], "markAt": [0, "năm"], "allAtStart": True, "ghost": "1789"},
        pan("t4_quangtrung", 1, "TƯỢNG ĐÀI QUANG TRUNG · BÌNH ĐỊNH",
            [{"x": .5, "y": .5, "z": 1, "at": [1, "quang"], "note": "Quang Trung"},
             {"x": .5, "y": .3, "z": 1.6, "at": [2, "ăn"]}]),
        {"device": "source_card", "line": 3, "source": "HOÀNG LÊ NHẤT THỐNG CHÍ · HỒI 14", "ref": "Lời hẹn",
         "snippet": "[[Mồng bảy]] năm mới vào thành Thăng Long mở tiệc.", "hlAt": [3, "mồng"], "seal": "TIỂU THUYẾT SỬ", "sealAt": [3, "mở"], "ghost": ""},
        {"device": "time_spine", "line": 4, "kick": "TẾT KỶ DẬU",
         "items": [{"yr": "30 Chạp", "label": "Ăn Tết sớm", "at": [4, "đêm"]}, {"yr": "Mồng 3", "label": "Hạ đồn Hà Hồi", "at": [4, "hà"]},
                   {"yr": "Mồng 5", "label": "Vỡ đồn Ngọc Hồi", "at": [5, "ngọc"]}], "ghost": ""},
        {"device": "myth_strike", "line": 6, "mythLab": "LỜI HẸN", "myth": "Mồng 7", "truthLab": "THỰC TẾ",
         "truth": "**Mồng 5**", "strikeAt": [6, "trưa"], "truthAt": [6, "sớm"], "ghost": ""},
        {"device": "close", "line": 7, "q": "Ăn Tết sớm là để vui quân, hay để **giữ bí mật**?", "markSpan": 3, "ghost": "", "fade": True, "lh": 1.55},
    ],
    packaging=dict(title="Vì Sao Quân Tây Sơn Ăn Tết Sớm Trước Khi Ra Bắc?",
                   description_first_line="Quân Tây Sơn ăn Tết sớm ở Tam Điệp, rồi vào Thăng Long trưa mùng 5 Tết Kỷ Dậu 1789, sớm hơn lời hẹn hai ngày.",
                   hashtags=["#quangtrung", "#tayson", *TAGS],
                   sources=["Nguồn: Ngô gia văn phái, Hoàng Lê nhất thống chí, hồi 14 (tiểu thuyết lịch sử); Đại Nam chính biên liệt truyện (truyện Nguyễn Huệ)."] + credit("t4_quangtrung"),
                   publish_slot_utc="2026-11-21T11:00:00Z"),
))

# ---------------- 5. Nam quốc sơn hà (Việt điện u linh: gắn thời Lê Hoàn; đời sau gắn Lý Thường Kiệt 1077; tác giả còn tranh luận)
S.append(dict(
    id="vsd_l1_namquoc", lane="vsd_van", theme="archive", kicker="VĂN · NAM QUỐC SƠN HÀ", foot="Việt điện u linh · Toàn thư",
    lines=[
        "Bài thơ người Việt nào cũng thuộc, mà tác giả **vẫn còn tranh luận**.",
        "Nam quốc sơn hà Nam đế cư.",
        "Truyện xưa kể, đêm đêm có tiếng ngâm bài thơ ấy từ đền thờ thần bên sông Như Nguyệt.",
        "Quân Tống nghe thấy, hoảng sợ, rồi tan vỡ.",
        "Đời sau gắn bài thơ với **Lý Thường Kiệt**, vị tướng giữ phòng tuyến Như Nguyệt năm 1077.",
        "Nhưng có sách lại kể bài thơ vang lên từ thời Lê Hoàn, gần một trăm năm trước.",
        "Đến nay, giới nghiên cứu vẫn **chưa thống nhất** ai là người viết.",
        "Bạn tin bài thơ là của một người, hay của **cả một dân tộc**?",
    ],
    scenes=[
        {"device": "hook_slam", "line": 0, "kick": "NAM QUỐC SƠN HÀ", "groups": [{"text": "Ai cũng thuộc"}, {"text": "AI VIẾT?", "big": True, "at": [0, "tác"]}], "markAt": [0, "tranh"], "allAtStart": True, "ghost": ""},
        {"device": "quote", "line": 1, "mode": "karaoke", "source": "NAM QUỐC SƠN HÀ", "sourceAt": [1, "cư"], "ghost": "南國"},
        pan("t5_song", 2, "SÔNG CẦU · KHÚC NHƯ NGUYỆT XƯA",
            [{"x": .5, "y": .5, "z": 1, "at": [2, "đền"], "note": "Sông Cầu ngày nay"},
             {"x": .5, "y": .55, "z": 1.4, "at": [3, "quân"]}]),
        {"device": "time_spine", "line": 4, "kick": "HAI THUYẾT",
         "items": [{"yr": "1077", "label": "Lý Thường Kiệt", "at": [4, "lý"]}, {"yr": "981", "label": "Thời Lê Hoàn", "at": [5, "lê"]}], "ghost": ""},
        {"device": "myth_strike", "line": 6, "mythLab": "TÁC GIẢ", "myth": "Một người", "truthLab": "ĐẾN NAY",
         "truth": "**Chưa rõ**", "strikeAt": [6, "chưa"], "truthAt": [6, "thống"], "ghost": ""},
        {"device": "close", "line": 7, "q": "Bài thơ ấy của một người, hay của **cả một dân tộc**?", "markSpan": 4, "ghost": "", "fade": True, "lh": 1.55},
    ],
    packaging=dict(title="Nam Quốc Sơn Hà Thật Sự Do Ai Viết?",
                   description_first_line="Nam quốc sơn hà do ai viết? Bài thơ gắn với Lý Thường Kiệt, nhưng sách xưa kể khác và giới nghiên cứu vẫn tranh luận.",
                   hashtags=["#namquocsonha", "#lythuongkiet", *TAGS],
                   sources=["Nguồn: Việt điện u linh (truyện thần sông Như Nguyệt); Đại Việt sử ký toàn thư (năm 1076–1077); các tổng quan văn bản học về tác giả bài thơ."] + credit("t5_song"),
                   publish_slot_utc="2026-11-19T11:00:00Z"),
))

# ---------------- 6. Đoạn trường tân thanh (3.254 câu lục bát; cốt truyện Kim Vân Kiều truyện, Thanh Tâm Tài Nhân)
S.append(dict(
    id="vsd_l1_kieu", lane="vsd_van", theme="archive", kicker="VĂN · NGUYỄN DU", foot="Đoạn trường tân thanh · 3.254 câu",
    lines=[
        "Tác phẩm nổi tiếng nhất nước Việt, lại ít ai gọi **đúng tên**.",
        "Nguyễn Du đặt tên nó là **Đoạn trường tân thanh**.",
        "Nghĩa là: tiếng kêu mới, đau như đứt ruột.",
        "Cốt truyện ông mượn từ Kim Vân Kiều truyện, một tiểu thuyết Trung Hoa của Thanh Tâm Tài Nhân.",
        "Nhưng ba nghìn hai trăm năm mươi tư câu lục bát là lời của **riêng Nguyễn Du**.",
        "Người đọc thì gọi theo tên nàng, rồi gọn lại thành **Truyện Kiều**.",
        "Cái tên dân gian đã thắng, còn tên tác giả đặt nằm trên bìa sách cổ.",
        "Bạn đọc Truyện Kiều lần đầu **năm bao nhiêu tuổi**?",
    ],
    scenes=[
        {"device": "hook_slam", "line": 0, "kick": "TÁC PHẨM NỔI TIẾNG NHẤT",
         "groups": [{"text": "Ít ai gọi"}, {"text": "ĐÚNG TÊN", "big": True, "at": [0, "đúng"]}], "markAt": [0, "tên"], "allAtStart": True, "ghost": "斷腸"},
        pan("t6_dtts", 1, "BÌA SÁCH CỔ · ĐOẠN TRƯỜNG TÂN THANH",
            [{"x": .5, "y": .5, "z": 1, "at": [1, "nguyễn"]},
             {"x": .27, "y": .5, "z": 2.0, "at": [2, "đứt"], "note": "斷腸新聲"}]),
        {"device": "source_card", "line": 3, "source": "NGUỒN CỐT TRUYỆN", "ref": "Mượn cốt truyện",
         "snippet": "Kim Vân Kiều truyện của [[Thanh Tâm Tài Nhân]]", "hlAt": [3, "thanh"], "seal": "TRUNG HOA", "sealAt": [3, "tiểu"], "ghost": ""},
        {"device": "count_ring", "line": 4, "label": "Câu lục bát", "value": 3254, "from": 0, "suffix": "CÂU", "at": [4, "ba"], "pct": 1, "ghost": ""},
        pan("t6_kieu", 5, "BẢN IN TRUYỆN KIỀU CHỮ NÔM",
            [{"x": .5, "y": .45, "z": 1, "at": [5, "người"]},
             {"x": .45, "y": .4, "z": 1.8, "at": [5, "truyện"], "note": "Thúy Kiều truyện"}]),
        {"device": "source_card", "line": 6, "source": "TÊN NGUYỄN DU ĐẶT", "ref": "Đoạn trường tân thanh",
         "snippet": "Tiếng kêu mới, [[đau đứt ruột]]", "hlAt": [6, "tên"], "seal": "斷腸新聲", "sealAt": [6, "bìa"], "ghost": ""},
        {"device": "close", "line": 7, "q": "Bạn đọc Truyện Kiều lần đầu **năm bao nhiêu tuổi**?", "markSpan": 4, "ghost": "", "fade": True, "lh": 1.55},
    ],
    packaging=dict(title="Truyện Kiều Tên Thật Là Đoạn Trường Tân Thanh",
                   description_first_line="Truyện Kiều tên thật là Đoạn trường tân thanh: tên Nguyễn Du đặt, nghĩa là tiếng kêu mới đau đứt ruột.",
                   hashtags=["#truyenkieu", "#nguyendu", *TAGS],
                   sources=["Nguồn: Nguyễn Du, Đoạn trường tân thanh (các bản Nôm thế kỷ 19, bản Kiều Oánh Mậu 1902); Từ điển Văn học, mục Nguyễn Du và Truyện Kiều."] + credit("t6_dtts", "t6_kieu"),
                   publish_slot_utc="2026-11-18T04:30:00Z"),
))

# ---------------- 7. Hồ Xuân Hương — danh hiệu của Xuân Diệu
S.append(dict(
    id="vsd_l1_xuanhuong", lane="vsd_van", theme="archive", kicker="VĂN · HỒ XUÂN HƯƠNG", foot="Xuân Diệu · Hồ Xuân Hương, bà chúa thơ Nôm",
    lines=[
        "Danh hiệu **Bà chúa thơ Nôm**, hóa ra có người đặt hẳn hoi.",
        "Hồ Xuân Hương sống vào cuối thế kỷ mười tám, đầu thế kỷ mười chín.",
        "Bà làm thơ bằng **chữ Nôm**, thứ chữ ghi tiếng nói của người Việt.",
        "Thơ bà tả bánh trôi, quả mít, cái quạt, mà câu nào cũng có hai tầng nghĩa.",
        "Người đặt danh hiệu ấy là nhà thơ **Xuân Diệu**.",
        "Ông viết hẳn một công trình về bà, lấy tên là Hồ Xuân Hương, bà chúa thơ Nôm.",
        "Có điều, nhiều bài thơ mang tên bà vẫn còn tranh cãi thật giả.",
        "Bạn thuộc bài thơ nào của **Hồ Xuân Hương**?",
    ],
    scenes=[
        {"device": "hook_slam", "line": 0, "kick": "HỒ XUÂN HƯƠNG", "groups": [{"text": "Bà chúa thơ Nôm"}, {"text": "AI ĐẶT?", "big": True, "at": [0, "đặt"]}], "markAt": [0, "hoi"], "allAtStart": True, "ghost": ""},
        pan("t7_hxh", 1, "GIAI NHÂN DI MẶC · HÀ NỘI 1916",
            [{"x": .5, "y": .55, "z": 1, "at": [1, "hồ"], "note": "Hồ Xuân Hương"},
             {"x": .5, "y": .12, "z": 2.0, "at": [2, "chữ"], "note": "Giai nhân di mặc · 1916"}]),
        {"device": "list_build", "line": 3, "title": "Vật quen, hai tầng nghĩa",
         "items": [{"text": "Bánh trôi", "sub": "Bánh trôi nước", "at": [3, "bánh"]}, {"text": "Quả mít", "sub": "", "at": [3, "quả"]},
                   {"text": "Cái quạt", "sub": "Vịnh cái quạt", "at": [3, "cái"]}], "ghost": ""},
        {"device": "source_card", "line": 4, "source": "XUÂN DIỆU", "ref": "Người đặt tên",
         "snippet": "Hồ Xuân Hương, [[bà chúa thơ Nôm]]", "hlAt": [5, "bà"], "seal": "XUÂN DIỆU", "sealAt": [5, "nôm"], "ghost": ""},
        {"device": "myth_strike", "line": 6, "mythLab": "THƠ MANG TÊN BÀ", "myth": "Đều của bà", "truthLab": "THẬT RA", "truth": "**Còn tranh cãi**", "strikeAt": [6, "nhiều"], "truthAt": [6, "tranh"], "ghost": ""},
        {"device": "close", "line": 7, "q": "Bạn thuộc bài thơ nào của **Hồ Xuân Hương**?", "markSpan": 3, "ghost": "", "fade": True, "lh": 1.55},
    ],
    packaging=dict(title="Ai Gọi Hồ Xuân Hương Là Bà Chúa Thơ Nôm?",
                   description_first_line="Hồ Xuân Hương được gọi là Bà chúa thơ Nôm nhờ nhà thơ Xuân Diệu, người viết hẳn một công trình mang tên ấy.",
                   hashtags=["#hoxuanhuong", "#thonom", *TAGS],
                   sources=["Nguồn: Xuân Diệu, Hồ Xuân Hương, bà chúa thơ Nôm; Đông Châu Nguyễn Hữu Tiến, Giai nhân di mặc (Hà Nội, 1916)."] + credit("t7_hxh"),
                   publish_slot_utc="2026-11-20T11:00:00Z"),
))

# ---------------- 8. Cửu Long chín cửa (Ba Thắc bồi lấp; cống đập Ba Lai 2002)
S.append(dict(
    id="vsd_l1_cuulong", lane="vsd_dia", theme="blueprint", kicker="ĐỊA · SÔNG CỬU LONG", foot="Chín cửa xưa · bảy cửa nay",
    lines=[
        "Sông **Chín Rồng**, nhưng nay không còn đủ chín cửa.",
        "Sông Mê Kông vào Việt Nam chia hai nhánh: sông Tiền và sông Hậu.",
        "Sông Tiền đổ ra biển qua sáu cửa, sông Hậu qua ba cửa.",
        "Cửa Ba Thắc trên sông Hậu bị phù sa bồi lấp dần, nay **không còn**.",
        "Cửa Ba Lai trên sông Tiền bị chặn bởi cống đập Ba Lai, xây xong năm 2002.",
        "Chín cửa thành **bảy cửa**, nhưng người ta vẫn gọi là Cửu Long.",
        "Bảy cửa còn lại vẫn đưa phù sa nuôi cả miền Tây.",
        "Bạn có kể đủ tên **bảy cửa sông** còn lại không?",
    ],
    scenes=[
        {"device": "hook_poster", "line": 0, "num": "9", "kick": "SÔNG CHÍN RỒNG CÒN MẤY CỬA", "big": "**KHÔNG ĐỦ CHÍN**", "markAt": [0, "chín"], "ghost": ""},
        pan("t8_sat", 1, "ĐỒNG BẰNG SÔNG CỬU LONG · ẢNH VỆ TINH",
            [{"x": .45, "y": .4, "z": 1, "at": [1, "sông"], "note": "Tiền · Hậu"},
             {"x": .62, "y": .62, "z": 1.9, "at": [2, "sáu"], "note": "Các cửa sông"}]),
        {"device": "split", "line": 3, "a": {"lab": "CỬA BA THẮC", "val": "BỒI LẤP", "num": "−1", "at": [3, "cửa"]},
         "b": {"lab": "CỬA BA LAI · 2002", "val": "ĐẬP", "num": "−1", "at": [4, "cửa"]}, "ghost": ""},
        {"device": "window", "line": 5, "word": "7", "fill": "solid", "lab": "CỬA CÒN CHẢY RA BIỂN", "sub": "vẫn gọi là Cửu Long", "subAt": [5, "cửu"], "ghost": ""},
        {"device": "list_build", "line": 6, "title": "Bảy cửa còn lại",
         "items": [{"group": "SÔNG TIỀN", "at": [6, "bảy"]}, {"text": "Tiểu · Đại · Hàm Luông", "sub": "", "at": [6, "cửa"]},
                   {"text": "Cổ Chiên · Cung Hầu", "sub": "", "at": [6, "phù"]}, {"group": "SÔNG HẬU", "at": [6, "nuôi"]},
                   {"text": "Định An · Trần Đề", "sub": "", "at": [6, "miền"]}], "ghost": ""},
        {"device": "close", "line": 7, "q": "Bạn có kể đủ tên **bảy cửa sông** còn lại không?", "markSpan": 3, "ghost": "", "fade": True, "lh": 1.55},
    ],
    packaging=dict(title="Sông Cửu Long Chín Cửa, Nay Còn Mấy Cửa?",
                   description_first_line="Sông Cửu Long chín cửa nay còn bảy: cửa Ba Thắc bồi lấp, cửa Ba Lai bị chặn bởi cống đập năm 2002.",
                   hashtags=["#cuulong", "#mientay", *TAGS],
                   sources=["Nguồn: tài liệu thủy văn đồng bằng sông Cửu Long (cửa Ba Thắc bồi lấp); công trình cống đập Ba Lai, Bến Tre (hoàn thành 2002)."] + ["Ảnh: NASA (ảnh vệ tinh, phạm vi công cộng, Wikimedia Commons)"],
                   publish_slot_utc="2026-11-19T04:30:00Z"),
))

# ---------------- 9. Sơn Đoòng (Hồ Khanh, đầu thập niên 1990; BCRA khảo sát 2009)
S.append(dict(
    id="vsd_l1_sondoong", lane="vsd_dia", theme="blueprint", kicker="ĐỊA · QUẢNG BÌNH", foot="Phong Nha – Kẻ Bàng · khảo sát 2009",
    lines=[
        "Hang động lớn bậc nhất thế giới, được tìm thấy rồi **lạc mất** nhiều năm.",
        "Đầu thập niên 1990, anh Hồ Khanh, một người đi rừng ở Quảng Bình, trú mưa và gặp một cửa hang.",
        "Từ trong hang, gió lạnh thổi ra, tiếng nước chảy vọng lên.",
        "Anh không dám vào, và khi quay lại, **không tìm ra lối cũ** nữa.",
        "Nhiều năm sau, anh mới tìm lại được cửa hang ấy.",
        "Năm 2009, anh dẫn đoàn của Hiệp hội Nghiên cứu Hang động Anh vào khảo sát.",
        "Bên trong có **rừng cây**, có mây, có cả sông ngầm.",
        "Nếu được vào Sơn Đoòng, bạn muốn **xem gì đầu tiên**?",
    ],
    scenes=[
        {"device": "hook_slam", "line": 0, "kick": "HANG SƠN ĐOÒNG",
         "groups": [{"text": "Tìm thấy rồi"}, {"text": "LẠC MẤT", "big": True, "at": [0, "lạc"]}], "markAt": [0, "năm"], "allAtStart": True, "ghost": "?"},
        pan("t9_db1", 1, "HANG SƠN ĐOÒNG · QUẢNG BÌNH",
            [{"x": .5, "y": .5, "z": 1, "at": [1, "anh"]},
             {"x": .5, "y": .4, "z": 1.6, "at": [2, "gió"], "note": "Bên trong Sơn Đoòng"}]),
        {"device": "source_card", "line": 3, "source": "LẦN QUAY LẠI", "ref": "Mất lối",
         "snippet": "Anh [[không tìm ra]] lối cũ nữa", "hlAt": [3, "không", 2], "seal": "NHIỀU NĂM", "sealAt": [3, "nữa"], "ghost": ""},
        {"device": "time_spine", "line": 4, "kick": "HÀNH TRÌNH TÌM LẠI",
         "items": [{"yr": "1990s", "label": "Gặp cửa hang", "at": [4, "nhiều"]}, {"yr": "Sau đó", "label": "Tìm lại lối", "at": [4, "tìm"]},
                   {"yr": "2009", "label": "Đoàn khảo sát Anh", "at": [5, "dẫn"]}], "ghost": ""},
        pan("t9_db3", 6, "BÊN TRONG SƠN ĐOÒNG",
            [{"x": .5, "y": .5, "z": 1, "at": [6, "rừng"], "note": "Rừng trong hang"},
             {"x": .5, "y": .6, "z": 1.6, "at": [6, "sông"]}]),
        {"device": "close", "line": 7, "q": "Vào Sơn Đoòng, bạn muốn **xem gì đầu tiên**?", "markSpan": 4, "ghost": "", "fade": True, "lh": 1.55},
    ],
    packaging=dict(title="Hang Sơn Đoòng Được Tìm Thấy Thế Nào?",
                   description_first_line="Hang Sơn Đoòng được anh Hồ Khanh tìm thấy rồi lạc mất nhiều năm, trước khi đoàn khảo sát Anh vào năm 2009.",
                   hashtags=["#sondoong", "#quangbinh", *TAGS],
                   sources=["Nguồn: Vườn quốc gia Phong Nha – Kẻ Bàng; British Cave Research Association, khảo sát tháng 4/2009."] + credit("t9_db1", "t9_db3"),
                   publish_slot_utc="2026-11-17T11:00:00Z"),
))

# ---------------- 10. Đà Lạt (Đạ Lạch; huy hiệu Dat Aliis Laetitiam Aliis Temperiem có sau)
S.append(dict(
    id="vsd_l1_dalat", lane="vsd_dia", theme="blueprint", kicker="ĐỊA · LÂM ĐỒNG", foot="Đạ Lạch · suối của người Lạch",
    lines=[
        "Câu chữ La-tinh trên huy hiệu Đà Lạt **không phải** nguồn gốc tên thành phố.",
        "Năm 1893, bác sĩ Yersin lên cao nguyên Lang Biang.",
        "Ở đó có dòng suối người bản địa gọi là **Đạ Lạch**, nghĩa là suối của người Lạch.",
        "Tên Đà Lạt bắt nguồn từ chính dòng suối ấy.",
        "Về sau, huy hiệu thành phố mới có thêm một câu chữ La-tinh.",
        "Câu ấy nghĩa là: cho người này niềm vui, cho người kia sự mát lành.",
        "Năm chữ cái đầu ghép lại, vừa khít chữ **Đà Lạt**.",
        "Bạn từng nghe **giải thích nào** về tên Đà Lạt?",
    ],
    scenes=[
        {"device": "hook_poster", "line": 0, "num": "?", "kick": "TÊN THÀNH PHỐ KHÔNG ĐẾN TỪ", "big": "**CÂU LA-TINH**", "markAt": [0, "không"], "ghost": ""},
        pan("t10_langbiang", 1, "NÚI LANG BIANG · LÂM ĐỒNG",
            [{"x": .55, "y": .3, "z": 1, "at": [1, "năm"]},
             {"x": .55, "y": .3, "z": 1.5, "at": [1, "lang"], "note": "Cao nguyên Lang Biang", "r": 1}]),
        {"device": "split", "line": 3, "a": {"lab": "ĐẠ · TIẾNG BẢN ĐỊA", "val": "SUỐI", "at": [3, "tên"]},
         "b": {"lab": "LẠCH · TÊN TỘC NGƯỜI", "val": "LẠCH", "at": [3, "dòng"]}, "ghost": ""},
        {"device": "source_card", "line": 4, "source": "HUY HIỆU ĐÀ LẠT · THỜI PHÁP", "ref": "Câu La-tinh",
         "snippet": "[[Dat Aliis Laetitiam]] Aliis Temperiem", "hlAt": [5, "cho"], "seal": "CÓ SAU TÊN", "sealAt": [5, "mát"], "ghost": ""},
        {"device": "list_build", "line": 6, "title": "Năm chữ cái đầu",
         "items": [{"text": "Dat · Aliis", "sub": "D · A", "at": [6, "năm"]}, {"text": "Laetitiam · Aliis", "sub": "L · A", "at": [6, "ghép"]},
                   {"text": "Temperiem", "sub": "T  →  DALAT", "at": [6, "vừa"]}], "ghost": ""},
        {"device": "close", "line": 7, "q": "Bạn từng nghe **giải thích nào** về tên Đà Lạt?", "markSpan": 3, "ghost": "", "fade": True, "lh": 1.55},
    ],
    packaging=dict(title="Vì Sao Đà Lạt Tên Là Đà Lạt?",
                   description_first_line="Vì sao Đà Lạt tên là Đà Lạt: từ dòng suối Đạ Lạch của người Lạch, còn câu La-tinh trên huy hiệu có sau.",
                   hashtags=["#dalat", "#langbiang", *TAGS],
                   sources=["Nguồn: địa danh học Lâm Đồng (Đạ Lạch, suối của người Lạch); huy hiệu Đà Lạt thời Pháp với câu Dat Aliis Laetitiam Aliis Temperiem."] + credit("t10_langbiang"),
                   publish_slot_utc="2026-11-21T04:30:00Z"),
))


# Ảnh dải cảnh mở (hook img, PR fix/vsd-hook-photo): khác ảnh cảnh 2 để 4 giây đầu có hai hình.
HOOK_IMG = {"vsd_l1_thanglong": "t1_hoalu", "vsd_l1_bachdang": "t2_map", "vsd_l1_hoangthanh": "t3_kinhthien",
            "vsd_l1_taysontet": "t4_map", "vsd_l1_namquoc": "t5_ltk", "vsd_l1_kieu": "t6_kvk", "vsd_l1_xuanhuong": "t7_hxh",
            "vsd_l1_cuulong": "t8_cantho", "vsd_l1_sondoong": "t9_doline", "vsd_l1_dalat": "t10_view"}
for s_ in S:
    k = HOOK_IMG[s_["id"]]
    s_["scenes"][0]["img"] = IMG + CRED[k]["path"].split("/")[-1]
    if s_["id"] == "vsd_l1_xuanhuong":
        s_["scenes"][0]["imgPos"] = "50% 20%"
    c = credit(k)[0]
    if c not in s_["packaging"]["sources"] and s_["id"] != "vsd_l1_cuulong" or k == "t8_cantho":
        if c not in s_["packaging"]["sources"]:
            s_["packaging"]["sources"].append(c)


def main():
    out_dir = HERE / "specs"
    out_dir.mkdir(exist_ok=True)
    for s in S:
        spec = {"channel": "vsd", "tts": True, "tail": 3.0, "loop": True,
                "audio": {"bgm_gain_db": -20.0}, "out": f"output/cl_staging/vsd/out/{s['id']}.mp4", **s}
        (out_dir / f"{s['id']}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(S), "spec ->", out_dir)


if __name__ == "__main__":
    main()
