"""VSD lô 2 (PO duyệt lô 17/11/2026): 4 Short cho 22–23/11, đủ tuần thử 24/24 (17–23/11).

Chạy: .venv/bin/python builders/short/build_vsd_lo2.py  -> output/cl_staging/vsd/specs/<id>.json
Ảnh + credits.json (hf_commons.fetch) ở output/cl_staging/vsd/img/ (gitignored), khoá t11–t14.
Workflow (a): Lead soát spec + pipelines/vsd/check_layout.sh -> pipelines/vsd/queue/ready/ -> n8n render + đăng.
Đề xuất + nguồn: output/cl_staging/vsd/de_xuat_lo2_2026-11-17.md. Khung dùng chung với lô 1: build_vsd_lo1.py.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_vsd_lo1 import CRED, HERE, IMG, TAGS, credit, pan  # noqa: E402

S = []

# ---------------- 11. Văn Miếu: bia tiến sĩ dựng 1484, tấm sớm nhất khắc khoa 1442; 82 bia (1442–1779)
S.append(dict(
    id="vsd_l2_vanmieu", lane="vsd_su", theme="archive", kicker="SỬ · VĂN MIẾU", foot="Toàn thư · 82 bia tiến sĩ",
    lines=[
        "Tấm bia tiến sĩ sớm nhất ghi tên người đỗ từ **bốn mươi hai năm** trước khi bia được dựng.",
        "Năm 1070, vua Lý Thánh Tông cho lập Văn Miếu ở Thăng Long.",
        "Sáu năm sau có Quốc Tử Giám, được xem là trường đại học đầu tiên của nước ta.",
        "Phải tới năm 1484, vua Lê Thánh Tông mới cho dựng **bia tiến sĩ**.",
        "Tấm bia sớm nhất lại khắc tên những người đỗ khoa thi năm 1442.",
        "Mỗi khoa một tấm bia, đặt trên lưng một con **rùa đá**.",
        "Nay còn tám mươi hai tấm, khoa cuối cùng được khắc là năm 1779.",
        "Tám mươi hai bia ấy đã được UNESCO ghi danh là **di sản tư liệu** thế giới.",
        "Bạn đã từng đi giữa **vườn bia** Văn Miếu chưa?",
    ],
    scenes=[
        {"device": "hook_slam", "line": 0, "kick": "VĂN MIẾU · HÀ NỘI",
         "groups": [{"text": "Bia dựng sau"}, {"text": "42 NĂM", "big": True, "at": [0, "bốn"]}], "markAt": [0, "năm"], "allAtStart": True, "ghost": ""},
        {"device": "time_spine", "line": 1, "kick": "VĂN MIẾU · QUỐC TỬ GIÁM",
         "items": [{"yr": "1070", "label": "Lập Văn Miếu", "at": [1, "văn"]}, {"yr": "1076", "label": "Quốc Tử Giám", "at": [2, "quốc"]}], "ghost": ""},
        pan("t11_bia1442", 3, "", [{"x": .5, "y": .45, "z": 1, "at": [3, "bia"], "note": "Bia tiến sĩ khoa 1442"},
                                   {"x": .5, "y": .8, "z": 1.7, "at": [4, "khoa"]}]),
        {"device": "source_card", "line": 4, "source": "BIA SỚM NHẤT", "ref": "Khoa 1442",
         "snippet": "Dựng năm 1484, khắc tên [[khoa thi năm 1442]]", "hlAt": [4, "khắc"], "seal": "LÊ THÁNH TÔNG", "sealAt": [4, "thi"], "ghost": ""},
        pan("t11_bia_a", 5, "", [{"x": .5, "y": .7, "z": 1.5, "at": [5, "rùa"], "note": "Rùa đá đội bia"},
                                 {"x": .5, "y": .5, "z": 1, "at": [6, "tám"]}]),
        {"device": "source_card", "line": 7, "source": "UNESCO · KÝ ỨC THẾ GIỚI", "ref": "82 bia",
         "snippet": "Bia tiến sĩ các khoa thi [[1442 – 1779]]", "hlAt": [7, "di"], "seal": "DI SẢN", "sealAt": [7, "thế"], "ghost": ""},
        {"device": "close", "line": 8, "q": "Bạn đã từng đi giữa **vườn bia** Văn Miếu chưa?", "markSpan": 2, "ghost": "", "fade": True, "lh": 1.55},
    ],
    packaging=dict(title="Bia Tiến Sĩ Văn Miếu: Vì Sao Dựng Sau 42 Năm?",
                   description_first_line="Bia tiến sĩ Văn Miếu dựng năm 1484 nhưng tấm sớm nhất khắc khoa thi năm 1442: chuyện 82 tấm bia trên lưng rùa đá.",
                   hashtags=["#vanmieu", "#quoctugiam", *TAGS],
                   sources=["Nguồn: Đại Việt sử ký toàn thư (năm 1070 lập Văn Miếu; năm 1076 lập Quốc Tử Giám); hệ thống 82 bia tiến sĩ Văn Miếu – Quốc Tử Giám (khoa 1442–1779), UNESCO Ký ức Thế giới."]
                   + credit("t11_bia1442", "t11_bia_a"),
                   publish_slot_utc="2026-11-22T04:30:00Z"),
))

# ---------------- 12. Bình Ngô đại cáo (Nguyễn Trãi soạn 1428 thay lời Lê Lợi; chữ "Ngô": Chu Nguyên Chương từng xưng Ngô Vương)
S.append(dict(
    id="vsd_l2_binhngo", lane="vsd_van", theme="archive", kicker="VĂN · NGUYỄN TRÃI", foot="Bình Ngô đại cáo · năm 1428",
    lines=[
        "Bài cáo nổi tiếng nhất nước ta mang lời một người, nhưng do **người khác** viết.",
        "Đầu năm 1428, nghĩa quân Lam Sơn đánh đuổi quân Minh khỏi Đại Việt.",
        "Nguyễn Trãi soạn bài cáo, thay lời Bình Định Vương **Lê Lợi** báo tin thắng trận.",
        "Việc nhân nghĩa cốt ở yên dân.",
        "Tên bài là **Bình Ngô**, nghĩa là dẹp yên giặc Ngô.",
        "Lạ ở chỗ, kẻ thù là nhà Minh, mà bài cáo lại gọi là Ngô.",
        "Một cách giải thích là vua Minh Thái Tổ từng xưng **Ngô Vương** trước khi lên ngôi.",
        "Người đời sau gọi bài cáo này là **thiên cổ hùng văn**.",
        "Bạn còn thuộc **câu nào** trong Bình Ngô đại cáo?",
    ],
    scenes=[
        {"device": "hook_slam", "line": 0, "kick": "BÌNH NGÔ ĐẠI CÁO",
         "groups": [{"text": "Lời một người"}, {"text": "NGƯỜI KHÁC VIẾT", "big": True, "at": [0, "người", 2]}], "markAt": [0, "viết"], "allAtStart": True, "ghost": ""},
        {"device": "time_spine", "line": 1, "kick": "KHỞI NGHĨA LAM SƠN",
         "items": [{"yr": "1428", "label": "Đuổi quân Minh", "at": [1, "minh"]}, {"yr": "Cùng năm", "label": "Nguyễn Trãi soạn cáo", "at": [2, "soạn"]}], "ghost": ""},
        pan("t12_cao", 3, "", [{"x": .5, "y": .3, "z": 1, "at": [3, "việc"], "note": "Bình Ngô đại cáo · bản chữ Hán"},
                               {"x": .7, "y": .25, "z": 1.6, "at": [3, "dân"]}]),
        {"device": "source_card", "line": 4, "source": "TÊN BÀI CÁO", "ref": "Bình Ngô",
         "snippet": "Gọi giặc [[Ngô]], mà kẻ thù là nhà Minh", "hlAt": [4, "ngô"], "seal": "CHỮ NGÔ", "sealAt": [5, "minh"], "ghost": ""},
        {"device": "list_build", "line": 6, "title": "Một cách giải thích",
         "items": [{"text": "Minh Thái Tổ", "sub": "Chu Nguyên Chương", "at": [6, "minh"]}, {"text": "Từng xưng Ngô Vương", "sub": "trước khi lên ngôi", "at": [6, "ngô"]}], "ghost": ""},
        pan("t12_nguyentrai", 7, "", [{"x": .5, "y": .3, "z": 1, "at": [7, "người"], "note": "Chân dung Nguyễn Trãi"},
                                      {"x": .5, "y": .25, "z": 1.5, "at": [7, "hùng"]}]),
        {"device": "close", "line": 8, "q": "Bạn còn thuộc **câu nào** trong Bình Ngô đại cáo?", "markSpan": 2, "ghost": "", "fade": True, "lh": 1.55},
    ],
    packaging=dict(title="Bình Ngô Đại Cáo: Vì Sao Gọi Quân Minh Là Ngô?",
                   description_first_line="Bình Ngô đại cáo do Nguyễn Trãi soạn năm 1428 thay lời Lê Lợi, và vì sao bài cáo gọi quân Minh là giặc Ngô.",
                   hashtags=["#binhngodaicao", "#nguyentrai", *TAGS],
                   sources=["Nguồn: Bình Ngô đại cáo (Nguyễn Trãi, 1428), bản dịch Bùi Kỷ; các giải thích về chữ \"Ngô\" (Chu Nguyên Chương từng được phong Ngô Quốc Công, xưng Ngô Vương)."]
                   + credit("t12_cao", "t12_nguyentrai"),
                   publish_slot_utc="2026-11-22T11:00:00Z"),
))

# ---------------- 13. Hải Vân quan (Minh Mạng 1826; ngạch trước "Hải Vân quan", ngạch sau "Thiên hạ đệ nhất hùng quan" — Đại Nam thực lục)
S.append(dict(
    id="vsd_l2_haivan", lane="vsd_dia", theme="blueprint", kicker="ĐỊA · ĐÈO HẢI VÂN", foot="Đại Nam thực lục · năm 1826",
    lines=[
        "Cửa ải trên đèo Hải Vân có **hai tên**, mỗi mặt cổng một tên.",
        "Năm 1826, vua Minh Mạng cho xây một cửa quan trên đỉnh đèo.",
        "Mặt nhìn về Đà Nẵng ghi ba chữ **Hải Vân quan**.",
        "Mặt nhìn về kinh thành Huế ghi sáu chữ: **Thiên hạ đệ nhất hùng quan**.",
        "Nghĩa là cửa ải hùng vĩ bậc nhất thiên hạ.",
        "Tương truyền danh hiệu ấy có từ khi vua Lê Thánh Tông dừng quân ở đây, năm 1470.",
        "Cửa ải còn là ranh giới: phía Bắc thuộc Thừa Thiên, phía Nam thuộc **Quảng Nam**.",
        "Hải Vân nghĩa là biển và mây, đứng trên đèo thấy được cả hai.",
        "Bạn đã từng **đi qua** đèo Hải Vân chưa?",
    ],
    scenes=[
        {"device": "hook_slam", "line": 0, "kick": "ĐÈO HẢI VÂN",
         "groups": [{"text": "Một cửa ải"}, {"text": "HAI TÊN", "big": True, "at": [0, "hai"]}], "markAt": [0, "tên"], "allAtStart": True, "ghost": ""},
        pan("t13_quan", 1, "", [{"x": .6, "y": .45, "z": 1, "at": [1, "minh"], "note": "Hải Vân quan"},
                                {"x": .6, "y": .55, "z": 1.6, "at": [1, "đỉnh"]}]),
        {"device": "split", "line": 2, "a": {"lab": "MẶT NHÌN VỀ ĐÀ NẴNG", "val": "3 CHỮ", "at": [2, "ba"]},
         "b": {"lab": "MẶT NHÌN VỀ HUẾ", "val": "6 CHỮ", "at": [3, "sáu"]}, "ghost": ""},
        {"device": "source_card", "line": 4, "source": "BIỂN ĐỀ MẶT SAU", "ref": "Sáu chữ",
         "snippet": "[[Thiên hạ đệ nhất]] hùng quan", "hlAt": [4, "hùng"], "seal": "TƯƠNG TRUYỀN", "sealAt": [5, "lê"], "ghost": ""},
        {"device": "list_build", "line": 6, "title": "Ranh giới năm 1826",
         "items": [{"text": "Phía Bắc", "sub": "Thừa Thiên", "at": [6, "bắc"]}, {"text": "Phía Nam", "sub": "Quảng Nam", "at": [6, "nam"]}], "ghost": ""},
        pan("t13_ocean", 7, "", [{"x": .35, "y": .4, "z": 1, "at": [7, "biển"], "note": "Đèo Hải Vân nhìn ra biển"},
                                 {"x": .3, "y": .3, "z": 1.5, "at": [7, "mây"]}]),
        {"device": "close", "line": 8, "q": "Bạn đã từng **đi qua** đèo Hải Vân chưa?", "markSpan": 2, "ghost": "", "fade": True, "lh": 1.55},
    ],
    packaging=dict(title="Hải Vân Quan: Một Cửa Ải, Hai Cái Tên",
                   description_first_line="Hải Vân quan xây năm 1826 thời Minh Mạng: mặt hướng Đà Nẵng ghi Hải Vân quan, mặt hướng Huế ghi Thiên hạ đệ nhất hùng quan.",
                   hashtags=["#haivan", "#deohaivan", *TAGS],
                   sources=["Nguồn: Đại Nam thực lục chính biên (năm Minh Mạng thứ 7, 1826: xây Hải Vân quan, hai biển đề); di tích quốc gia Hải Vân quan (2017)."]
                   + credit("t13_quan", "t13_ocean"),
                   publish_slot_utc="2026-11-23T04:30:00Z"),
))

# ---------------- 14. Cổ Loa (tương truyền 9 vòng, dấu tích 3 vòng: 8 km, 6,5 km, 1,6 km; vòng trong có thể thời Ngô Quyền)
S.append(dict(
    id="vsd_l2_coloa", lane="vsd_su", theme="archive", kicker="SỬ · THÀNH CỔ LOA", foot="Khảo cổ Cổ Loa · Đông Anh, Hà Nội",
    lines=[
        "Truyền thuyết nói thành Cổ Loa có **chín vòng**, nhưng dấu tích chỉ còn ba.",
        "Cổ Loa là kinh đô nước Âu Lạc của An Dương Vương, khoảng thế kỷ thứ ba trước Công nguyên.",
        "Thành đắp bằng đất, chân thành kè đá và gốm vỡ cho khỏi sụt lở.",
        "Vòng ngoài dài khoảng **tám cây số**, vòng giữa khoảng sáu cây số rưỡi.",
        "Vòng trong cùng có lẽ được đắp muộn hơn, vào thời Ngô Quyền.",
        "Quanh thành, người ta đào được hàng vạn **mũi tên đồng**.",
        "Dân gian gắn chúng với chiếc **nỏ thần** của An Dương Vương.",
        "Bạn tin Cổ Loa từng có **mấy vòng** thành?",
    ],
    scenes=[
        {"device": "hook_slam", "line": 0, "kick": "THÀNH CỔ LOA",
         "groups": [{"text": "Chín vòng?"}, {"text": "CÒN LẠI BA", "big": True, "at": [0, "ba"]}], "markAt": [0, "vòng"], "allAtStart": True, "ghost": ""},
        pan("t14_citadelle", 1, "", [{"x": .5, "y": .4, "z": 1, "at": [1, "âu"], "note": "Di tích Cổ Loa"},
                                     {"x": .45, "y": .3, "z": 1.5, "at": [1, "dương"]}]),
        {"device": "source_card", "line": 2, "source": "KHẢO CỔ · THÀNH CỔ LOA", "ref": "Chân thành",
         "snippet": "Đắp đất, chân [[kè đá và gốm vỡ]]", "hlAt": [2, "kè"], "seal": "ÂU LẠC", "sealAt": [2, "sụt"], "ghost": ""},
        {"device": "list_build", "line": 3, "title": "Ba vòng thành",
         "items": [{"text": "Vòng ngoài", "sub": "khoảng 8 km", "at": [3, "ngoài"]}, {"text": "Vòng giữa", "sub": "khoảng 6,5 km", "at": [3, "giữa"]},
                   {"text": "Vòng trong", "sub": "có lẽ thời Ngô Quyền", "at": [4, "trong"]}], "ghost": ""},
        pan("t14_arrow", 5, "", [{"x": .5, "y": .45, "z": 1, "at": [5, "mũi"], "note": "Mũi tên đồng Cổ Loa"},
                                 {"x": .4, "y": .3, "z": 1.8, "at": [6, "nỏ"]}]),
        {"device": "close", "line": 7, "q": "Bạn tin Cổ Loa từng có **mấy vòng** thành?", "markSpan": 2, "ghost": "", "fade": True, "lh": 1.55},
    ],
    packaging=dict(title="Thành Cổ Loa Có Thật Chín Vòng Không?",
                   description_first_line="Thành Cổ Loa có thật chín vòng xoáy ốc? Dấu tích chỉ còn ba vòng thành đất, cùng hàng vạn mũi tên đồng.",
                   hashtags=["#coloa", "#anduongvuong", *TAGS],
                   sources=["Nguồn: khảo cổ học thành Cổ Loa (ba vòng thành: khoảng 8 km, 6,5 km, 1,6 km; mũi tên đồng); truyền thuyết An Dương Vương (Lĩnh Nam chích quái)."]
                   + credit("t14_citadelle", "t14_arrow"),
                   publish_slot_utc="2026-11-23T11:00:00Z"),
))

HOOK_IMG = {"vsd_l2_vanmieu": "t11_khuevan", "vsd_l2_binhngo": "t12_leloi", "vsd_l2_haivan": "t13_hungquan", "vsd_l2_coloa": "t14_den"}
for s_ in S:
    k = HOOK_IMG[s_["id"]]
    s_["scenes"][0]["img"] = IMG + CRED[k]["path"].split("/")[-1]
    c = credit(k)[0]
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
