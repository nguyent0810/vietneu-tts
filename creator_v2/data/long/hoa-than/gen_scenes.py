"""Cảnh biên tập CH00–CH03 của hồ sơ Hòa Thân."""
import json, sys, importlib.util
from pathlib import Path
D = Path(__file__).resolve().parent
ROOT = D.parents[2]
sys.path.insert(0, str(ROOT / "motion" / "long"))
from scenekit import sc, kin, write, FILMV
_RES = json.loads((ROOT / "output/long/hoa-than/research.json").read_text(encoding="utf-8"))["images"]
def im(i, must):
    f = _RES[i]["file"]
    if must not in f: raise ValueError(f"Ảnh {i} không khớp: {f}")
    return f
IMGS = {"hoa": im(0,"Hesen"), "phu": im(1,"PrinceGong"), "phu2": im(2,"PrinceGong"), "phu3": im(3,"PrinceGong"), "phu4": im(4,"Gongwangfu"), "phu5": im(5,"Gongwangfu"), "phu6": im(6,"Gongwangfu"), "phu7": im(7,"Gongwangfu"), "phu8": im(8,"Gongwangfu"), "ho": im(152,"Shichahai"), "ho2": im(153,"Shichahai"), "ngua": im(11,"Horseback"), "canlong": im(12,"Qianlong"), "giakhanh": im(37,"嘉庆"), "luudung": im(39,"Liu Yong"), "cung": im(84,"map"), "thanh": im(103,"Meridian"), "cua": im(101,"Harmony"), "ngubut": im(125,"和珅"), "ky": im(55,"Qing Dynasty"), "quan": im(82,"Review"), "tranh": im(121,"Heshen"), "ai01":"EXT:ai:ai_01", "ai02":"EXT:ai:ai_02", "ai03":"EXT:ai:ai_03", "ai10":"EXT:ai:ai_10"}
IMGS.update({"hieu": im(41,"Princess He Xiao"), "agui": im(151,"Agui"), "mac": im(137,"Macartney"), "sud": im(13,"Embassy"), "canton": im(146,"Canton"), "tranhle": im(142,"Approach"), "ai12":"EXT:ai:ai_12", "ai13":"EXT:ai:ai_13", "ai14":"EXT:ai:ai_14"})
IMGS.update({"ai15":"EXT:ai:ai_15", "ai16":"EXT:ai:ai_16", "ai17":"EXT:ai:ai_17", "ai18":"EXT:ai:ai_18", "ai19":"EXT:ai:ai_19", "ai04":"EXT:ai:ai_04", "ai07":"EXT:ai:ai_07"})

IMGS.update({'emperor_jifu_robe': 'EXT:artic:68830', 'qianlong_essay_old_age': 'EXT:europeana:/1100/655', 'qianlong_poem_flowers': 'EXT:europeana:/1100/1672', 'wenguan_portrait_1': 'EXT:artic:35364', 'wenguan_portrait_2': 'EXT:artic:37722', 'court_jifu_robe': 'EXT:artic:75521', 'qianlong_lacquer_teabowl': 'EXT:artic:134', 'qianlong_dragon_dish': 'EXT:artic:41882', 'qianlong_poem_victory': 'EXT:europeana:/1100/871', 'qianlong_temple_name': 'EXT:europeana:/1100/654', 'bridal_dragon_robe': 'EXT:artic:47283'})
V = {"v1":"900001", "v2":"900002", "v3":"900003", "v4":"900004", "v5":"900005", "v6":"900006", "v7":"900007", "v8":"900008"}
GEO = {}
IMGS.update({
 "thanh2": im(104,"West wing"), "ngai": im(100,"Dragon Throne"), "cmon": im(114,"乾清门"), "dien": im(113,"Hall of Supreme"),
 "ngom": im(112,"Cité interdite"), "cungtu": im(93,"Coal Hill"), "qlhau": im(16,"Qianlong and the Empress"), "qlsan": im(19,"Qianlong emperor hunting"),
 "qltrieu": im(135,"Court Dress"), "qlyen": im(21,"Banquets"), "qlcung": im(33,"Qianlong in the Forbidden"), "kyvan": im(40,"Ji Yun"),
 "thi": im(132,"和珅书弘历"), "nguaC": im(24,"Chaoni"), "nguaL": im(25,"Laiyuanliu"), "nguaY": im(26,"Yuekulai"), "nguaK": im(27,"Lingkunbai"),
 "dichan": im(147,"Prince Gong.JPG"), "hamphong": im(76,"咸豐通寶"), "ho3": im(154,"Shichahai 1"), "hoa2": im(134,"Hesen (cropped)"),
 "pg1": im(150,"154948"), "pg2": im(155,"Prince Gong 1.jpg"), "pg3": im(156,"Prince Gong 2.jpg"), "pg4": im(157,"Prince Gong 3.jpg"),
 "pg5": im(158,"Prince Gong 4.jpg"), "pg6": im(159,"Prince Gong 5.jpg"), "pg7": im(161,"155256"), "pg8": im(162,"160013"),
 "pg9": im(163,"160204"), "pg10": im(164,"162145"), "pg11": im(165,"162350"), "pg12": im(166,"170002"), "pg13": im(167,"170211"),
 "pg14": im(168,"170330"), "pg15": im(170,"Theatre"), "pg16": im(171,"Doorway"), "pg17": im(173,"2611721407"),
 "ai01": "EXT:ai:ai_01", "ai02": "EXT:ai:ai_02", "ai05": "EXT:ai:ai_05", "ai06": "EXT:ai:ai_06", "ai08": "EXT:ai:ai_08", "ai09": "EXT:ai:ai_09",
 "ai11": "EXT:ai:ai_11", "ai20": "EXT:ai:ai_20",
 "qianlong_poem_siege": "EXT:europeana:/1100/867",
})
TD = "TÁI DỰNG MINH HỌA"
MS = "CUNG VƯƠNG PHỦ NGÀY NAY"
TC = "TỬ CẤM THÀNH NGÀY NAY"
HO = "HỒ THẬP SÁT HẢI NGÀY NAY"
def ph(at, img, illus=None, move="in", **k):
    d = dict(img=img, tone="color", move=move, **k)
    if illus: d["illus"] = illus
    return sc("photo", at, **d)
def ai(at, img, cap=False, move="in", **k):
    d = dict(img=img, credit=False, tone="color", move=move, **k)
    if cap: d["illus"] = TD
    return sc("photo", at, **d)
def clip(at, v, *items, tone="noir", veil=0.4):
    return sc("broll", at, vid=V[v], tone=tone, veil=veil, illus=FILMV, kin=kin(*items))
def led(at, title, rows, **k):
    return sc("ledger", at, title=title, rows=[{"k": a, "v": b, "at": c} for a, b, c in rows], **k)
def cnt(at, to, suffix, label, cat, **k):
    return sc("counter", at, **{"from": 0}, to=to, suffix=suffix, countAt=cat, label=label, **k)
def bars(at, title, unit, items, **k):
    return sc("bars", at, title=title, unit=unit, items=[dict(k=a, v=b, at=c, **({"acc": True} if i == len(items) - 1 else {})) for i, (a, b, c) in enumerate(items)], **k)
def tl(at, items, **k):
    return sc("timeline", at, items=[{"year": a, "text": b, "at": c} for a, b, c in items], **k)
CH = {}
CH["ch00"] = dict(hud={"k":"MỞ ĐẦU","t":"NHÀ RIÊNG"}, bgm={"mood":"tense","at":0,"gain":0.12}, scenes=[
 sc("date",None,bg="phu",day="NHÀ RIÊNG · BẮC KINH",date="22.02.1799"),
 ai([0,"tại"],"ai01",cap=True),
 sc("photo",1,img="phu2",tone="color",move="in",illus="CUNG VƯƠNG PHỦ NGÀY NAY"),
 sc("slam",2,bg="phu5",text="TRÍ TRAI",hitAt=[2,"Trí"]),
 sc("file",3,k="NGƯỜI TRONG NHÀ",name="HÒA THÂN",desc="Nhà riêng: Trí Trai",bg="hoa"),
 cnt(4,15," NGÀY","SAU KHI CÀN LONG MẤT",[4,"Mười"],bg="canlong"),
 sc("photo",[4,"Thái"],img="canlong",tone="color",move="in",illus="TRANH CÀN LONG"),
 sc("date",5,bg="ky",day="NĂM NGÀY SAU NGÀY MẤT",date="12.02.1799"),
 sc("date",6,bg="cua",day="BA NGÀY SAU · CHỈ DỤ",date="15.02.1799"),
 sc("slam",7,bg="phu4",text="ÁN ĐƯỢC ĐỔI",hitAt=[7,"đổi"]),
 sc("kinetic",8,vid=V["v6"],tone="noir",items=kin(("KHÔNG RA GIỮA CHỢ",[8,"giữa"]))),
 sc("file",9,k="THANH SỬ CẢO",name="BỐN CHỮ",desc="Bản dịch tiếng Việt",bg="ngubut"),
 sc("quote",10,text="Ban cho tự vẫn.",by="THANH SỬ CẢO",lbl="TRÍCH DỊCH",qline=10,typeAt=[10,"Ban"]),
 clip(11,"v1",("TẠI CHÍNH",[11,"tại"]),("NGÔI NHÀ ẤY",[11,"ngôi"],"acc")),
 ai(12,"ai04"),
 sc("kinetic",[12,"bằng"],bg="phu6",items=kin(("BẰNG NHIỀU NĂM NGÂN SÁCH",[12,"bằng"],"acc"))),
 sc("kinetic",13,bg="ky",items=kin(("CÁC CON SỐ CHÊNH NHAU",[13,"Các"],"acc"))),
 sc("ledger",14,title="HAI ƯỚC TÍNH",rows=[{"k":"MỘT NGUỒN","v":"1,1 TỶ LẠNG BẠC","at":[14,"tỷ"]},{"k":"NGUỒN KHÁC","v":"KHOẢNG 60 TRIỆU","at":[15,"triệu"]}]),
 clip(16,"v7",("BẠN ĐÃ THẤY ÔNG",[16,"thấy"]),("TRÊN PHIM",[16,"phim"],"acc")),
 sc("print",18,img="kyvan",tone="color",side={"k":"NGƯỜI THẬT","h":"KỶ VÂN\n1724–1805","hAt":[18,"Nhiều"],"lines":[{"text":"Phim gọi là *Kỷ Hiểu Lam*","at":[18,"Kỷ"]}]}),
 sc("slam",[19,"Tể"],bg="luudung",text="TỂ TƯỚNG LƯU GÙ",hitAt=[19,"Tể"]),
 sc("kinetic",[19,"kẻ"],bg="ngubut",items=kin(("CHỈ LÀ KẺ PHẢN DIỆN",[19,"kẻ"],"acc"))),
 sc("evidence",20,img="hoa2",tone="color",maxW=700,maxH=760,callouts=[{"x":0.5,"y":0.3,"text":"TRANH ĐỜI THANH","at":[20,"Tranh"],"side":"r"},{"x":0.5,"y":0.5,"text":"KHÔNG BÉO","at":[20,"béo"],"side":"l"}]),
 sc("slam",21,vid=V["v1"],tone="noir",text="TRANH KHÔNG CƯỜI",hitAt=[21,"cười"]),
 sc("kinetic",22,bg="phu6",items=kin(("KHO VÀNG KHÔNG ĐỨNG YÊN",[22,"kho"],"acc"))),
 sc("question",[22,"thì"],bg="tranh",text="HÒA THÂN THẬT SỰ LÀ AI?"),
 sc("date",23,bg="giakhanh",day="GIA KHÁNH LÊN NGÔI",date="02.1796"),
 sc("kinetic",[23,"hoàng"],bg="giakhanh",items=kin(("ĐÃ LÀ HOÀNG ĐẾ",[23,"hoàng"],"acc"))),
 sc("question",[23,"phải"],bg="giakhanh",text="VÌ SAO GIA KHÁNH PHẢI ĐỢI?"),
 sc("question",24,bg="hoa",text="VÌ SAO PHIM CẦN MỘT GÃ HỀ?"),
 sc("slam",[24,"cùng"],bg="luudung",text="LƯU DUNG TỬ THÙ",hitAt=[24,"cùng"]),
])
CH["ch01"] = dict(hud={"k":"CHƯƠNG 01","t":"NGHỊCH LÝ"}, bgm={"mood":"mystery","at":0,"gain":0.12}, scenes=[
 sc("photo",None,img="ngubut",tone="color",move="in"),
 led(1,"MỘT BÊN CỦA MẶT BÀN",[("MỘT BẢN","1,1 TỶ LẠNG",[1,"tỷ"]),("ĐỔI RA","KHOẢNG 270 TỶ ĐÔ LA MỸ",[2,"270"]),("BẰNG","KHOẢNG 12 NĂM NGÂN SÁCH",[3,"12"])]),
 led(4,"BÊN KIA",[("CHỪNG","60 TRIỆU LẠNG",[4,"60"]),("CỠ","MỘT NĂM NGÂN SÁCH",[5,"một"])]),
 led(6,"ĐỘNG SẢN VÀ TỔNG",[("ĐỘNG SẢN GHI","60 ĐẾN 80 TRIỆU LẠNG",[6,"60"]),("TỔNG ƯỚC TÍNH","100 ĐẾN 800 TRIỆU LẠNG",[7,"100"])]),
 ai(8,"ai05",cap=True),
 clip(10,"v2",("BẠN THỬ",[10,"thử"]),("NHÌN CHO KỸ",[10,"kỹ"],"acc")),
 cnt(11,12," NĂM","NGÂN SÁCH · THEO MỘT BẢN",[11,"12"],bg="phu2"),
 cnt(12,1," NĂM","THU · THEO BẢN KIA",[12,"một"],bg="phu3"),
 sc("kinetic",13,vid=V["v2"],tone="noir",items=kin(("CÙNG MỘT NGƯỜI",[13,"người"]),("CÙNG MỘT VỤ TỊCH THU",[13,"tịch"]),("CÙNG NĂM 1799",[13,"1799"],"acc"))),
 sc("slam",[14,"lung"],vid=V["v6"],tone="noir",text="LUNG LAY",hitAt=[14,"lung"]),
 ai(16,"ai20"),
 sc("photo",17,img="luudung",tone="color",move="in",illus="TRANH LƯU DUNG"),
 sc("date",18,bg="hoa",day="BẮT ĐẦU CÙNG LÀM THƯỢNG THƯ BỘ LẠI",date="04.09.1784"),
 sc("date",[18,"đến"],bg="hoa",day="KẾT THÚC",date="16.09.1786"),
 sc("kinetic",19,vid=V["v3"],tone="noir",items=kin(("HAI NĂM · MỘT BỘ",[19,"Hai"],"acc"))),
 led(20,"BỘ LẠI · 1784–1786",[("THƯỢNG THƯ","LƯU DUNG · HÒA THÂN",[20,"hai"]),("MỘT NGƯỜI","PHIM GỌI THANH LIÊM",[21,"thanh"]),("MỘT NGƯỜI","PHIM GỌI GIAN",[22,"gian"])],bg="ky"),
 sc("file",24,k="HỒ SƠ GHI",name="HAI TÊN · MỘT CHỨC",desc="Thượng thư Bộ Lại",bg="cua",rows=[{"k":"TÊN THỨ NHẤT","v":"LƯU DUNG","at":[24,"hai"]},{"k":"TÊN THỨ HAI","v":"HÒA THÂN","at":[24,"chức"]}]),
 ph(26,"tranh","TRANH HÒA THÂN"),
 tl(28,[("1772","Thị vệ cửa cung",[28,"1772"]),("1776","Vào Quân cơ",[29,"1776"]),("1799","Qua đời, thọ 48 tuổi",[30,"1799"])],bg="cung"),
 cnt(31,27," NĂM","QUAN TRƯỜNG",[31,"27"],bg="cua"),
 clip(33,"v6",("PHIM DỪNG Ở TIẾNG CƯỜI",[33,"Phim"]),("VÀ Ở KHO VÀNG",[33,"kho"],"acc")),
 ph(35,"cmon",TC),
 sc("kinetic",36,bg="phu6",items=kin(("MỘT BẢN KÊ KHÔNG CỘNG ĐƯỢC",[36,"bản"]),("MỘT ÔNG VUA CON PHẢI ĐỢI",[37,"vua"]),("MỘT KHUÔN MẶT KHÔNG KHỚP TRANH",[38,"khuôn"],"acc"))),
 sc("question",40,bg="thanh",text="ÔNG BƯỚC VÀO CUNG TỪ ĐÂU?"),
])
CH["ch02"] = dict(hud={"k":"CHƯƠNG 02","t":"THỊ VỆ CỬA CUNG"}, bgm={"mood":"quiet","at":0,"gain":0.12}, scenes=[
 sc("date",None,bg="ky",day="BẮC KINH · THIỆN BẢO",date="01.07.1750"),
 sc("file",1,k="TÊN KHAI SINH",name="THIỆN BẢO",desc="Tự Trí Trai",bg="tranh",rows=[{"k":"TỰ","v":"TRÍ TRAI","at":[2,"Tự"]},{"k":"TỘC","v":"NỮU HỖ LỘC · CHÍNH HỒNG KỲ","at":[3,"Tộc"]}]),
 sc("kinetic",4,bg="ngubut",items=kin(("NGHÈO TỪ NHỎ",[4,"nghèo"],"acc"))),
 sc("photo",5,img="quan",tone="color",move="pan",illus="TRANH DUYỆT BINH TRIỀU THANH"),
 sc("kinetic",7,vid=V["v3"],tone="noir",items=kin(("MẤT MẸ TỪ NHỎ",[7,"mất"]),("MẸ KẾ",[7,"kế"]),("MỘT EM TRAI",[7,"em"],"acc"))),
 sc("ledger",9,title="NGÔN NGỮ",rows=[{"k":"TRONG TRIỀU","v":"QUAN THOẠI","at":[9,"Quan"]},{"k":"TỘC CỦA ÔNG","v":"MÃN","at":[9,"Mãn"]},{"k":"PHƯƠNG BẮC","v":"MÔNG CỔ","at":[9,"Mông"]},{"k":"KHÁCH XA","v":"TÂY TẠNG","at":[10,"Tây"]}]),
 sc("kinetic",[11,"nói"],bg="ngubut",items=kin(("TIẾNG TRONG TRIỀU · TIẾNG KHÁCH XA",[11,"nói"],"acc"))),
 sc("kinetic",13,bg="phu",items=kin(("VỐN NẰM SẴN TRONG NGƯỜI",[13,"vốn"],"acc"))),
 sc("date",15,bg="quan",day="THỪA TẬP TƯỚC",date="1769"),
 sc("file",16,k="CHỨC",name="TAM ĐẲNG THỊ VỆ",desc="Theo Thanh sử cảo",bg="quan"),
 sc("date",17,bg="ky",day="MỘT BẢN KHÁC GHI",date="1772"),
 sc("kinetic",18,vid=V["v4"],tone="noir",items=kin(("GOM CẢ QUÃNG THĂNG CHỨC",[18,"gom"],"acc"))),
 sc("date",20,bg="thanh",day="ĐIỀU VÀO TỬ CẤM THÀNH",date="1775"),
 sc("kinetic",21,bg="cmon",items=kin(("NĂM CÀN LONG THỨ 40",[21,"Năm"]),("TRỰC CỬA CÀN THANH",[21,"trực"]),("NGỰ TIỀN THỊ VỆ",[21,"Ngự"],"acc"))),
 cnt(22,40," NĂM","CÀN LONG TRỊ VÌ",[22,"bốn"],bg="canlong"),
 ai(23,"ai08",cap=True),
 sc("slam",24,bg="cua",text="ĐẨY LÊN RẤT NHANH",hitAt=[24,"nhanh"]),
 sc("date",25,bg="cua",day="VÀO QUÂN CƠ",date="22.04.1776"),
 sc("ledger",26,title="CÁC CHỨC ĐƯỢC GIAO",rows=[{"k":"THỊ LANG","v":"BỘ HỘ","at":[26,"Thị"]},{"k":"QUÂN CƠ","v":"ĐẠI THẦN","at":[26,"Quân"]},{"k":"KIÊM","v":"NỘI VỤ PHỦ","at":[26,"Nội"]},{"k":"KIÊM","v":"THỐNG LĨNH BỘ BINH","at":[27,"thống"]},{"k":"GIÁM SÁT","v":"THUẾ CỬA SÙNG VĂN","at":[27,"thuế"]}]),
 ph(30,"cung","SƠ ĐỒ TỬ CẤM THÀNH"),
 sc("kinetic",31,vid=V["v1"],tone="noir",items=kin(("NGƯỜI GIỮ SỔ ĐỨNG SÁT TAI",[31,"đứng"],"acc"))),
 cnt(33,65," TUỔI","HOÀNG ĐẾ · NĂM 1776",[33,"65"],bg="canlong"),
 bars(34,"TUỔI NĂM 1776","TUỔI",[("THỊ VỆ",26,[34,"26"]),("HOÀNG ĐẾ",65,[35,"65"])],bg="cua"),
 sc("kinetic",37,bg="quan",items=kin(("NGƯỜI GIỮ ĐƯỜNG PHỐ",[37,"người"],"acc"))),
 sc("kinetic",39,bg="cmon",items=kin(("HỒ SƠ KHÔNG GHI HỌ NÓI GÌ",[39,"Hồ"],"acc"))),
 sc("slam",40,bg="thanh",text="Ở CẢ HAI CHỖ",hitAt=[40,"cả"]),
 sc("question",41,bg="cua",text="NĂM SAU, ĐẶC ÂN CÒN LẠ HƠN"),
])
CH["ch03"] = dict(hud={"k":"CHƯƠNG 03","t":"HAI MƯƠI BẢY TUỔI"}, bgm={"mood":"mystery","at":0,"gain":0.12}, scenes=[
 sc("date",None,bg="ngua",day="HÒA THÂN · 27 TUỔI",date="1777"),
 sc("photo",1,img="ngua",tone="color",move="pan",illus="TRANH CÀN LONG CƯỠI NGỰA · MINH HỌA"),
 sc("kinetic",2,bg="cung",items=kin(("ĐẶC ÂN CHO QUAN GIÀ, QUAN CAO",[2,"quan"],"acc"))),
 sc("kinetic",4,bg="cua",items=kin(("NGỰA KHÔNG CHỈ LÀ CÁCH ĐI",[4,"ngựa"],"acc"))),
 sc("photo",5,img="ai10",credit=False,illus="TÁI DỰNG MINH HỌA",tone="color",move="in"),
 sc("kinetic",6,bg="thanh",items=kin(("VÌ TUỔI",[6,"vì"]),("VÌ PHẨM",[6,"phẩm"],"acc"))),
 ph(8,"dien",TC),
 tl(9,[("1735","Càn Long lên ngôi",[9,"1735"]),("1777","Bốn mươi hai năm trị vì",[10,"1777"])],bg="canlong"),
 bars(11,"TUỔI NĂM 1777","TUỔI",[("CÀN LONG",66,[11,"66"]),("HÒA THÂN",27,[12,"27"])],bg="canlong"),
 ph(14,"qltrieu","CHÂN DUNG CÀN LONG"),
 sc("photo",[15,"ngôi"],img="phu2",tone="color",move="in",illus="CUNG VƯƠNG PHỦ NGÀY NAY"),
 sc("photo",16,img="ho",tone="color",move="pan",illus="HỒ THẬP SÁT HẢI NGÀY NAY"),
 sc("ledger",17,title="KHUÔN VIÊN",bg="phu3",rows=[{"k":"PHÍA NAM","v":"NHÀ","at":[17,"nam"]},{"k":"PHÍA BẮC","v":"VƯỜN","at":[18,"bắc"]}]),
 sc("file",19,k="NĂM 1799",name="TRÍ TRAI",desc="Chưa mang tên Cung Vương Phủ",bg="phu4"),
 sc("kinetic",20,vid=V["v3"],tone="noir",items=kin(("NHÀ RIÊNG · TRÍ TRAI",[20,"Nó"],"acc"))),
 ph(21,"pg1",MS),
 sc("photo",24,img="ho2",tone="color",move="pan",illus="HỒ THẬP SÁT HẢI NGÀY NAY"),
 sc("kinetic",25,bg="phu5",items=kin(("NHÀ CỦA MỘT QUAN TRẺ",[25,"nhà"],"acc"))),
 sc("slam",26,bg="phu6",text="TÊN ẤY CHƯA CÓ",hitAt=[26,"chưa"]),
 sc("slam",27,bg="phu5",text="CHƯA CÓ KHO VÀNG ĐƯỢC KIỂM",hitAt=[27,"kho"]),
 clip(28,"v3",("PHIM CẦN MỘT HẦM",[28,"hầm"],"acc")),
 sc("photo",29,img="ai11",credit=False,tone="color",move="in",kin=kin(("MỘT CÔNG TRƯỜNG",[29,"công"]),("MỘT CON NGỰA",[29,"con"]),("MỘT HOÀNG ĐẾ GIÀ",[29,"hoàng"],"acc"))),
 sc("kinetic",30,bg="phu6",items=kin(("NGÔI NHÀ VỀ SAU BỊ ĐƯA VÀO BẢN ÁN",[30,"án"],"acc"))),
 sc("ledger",31,title="CHỮ TRONG BẢN ÁN",bg="phu",rows=[{"k":"CHẤT LIỆU","v":"GỖ NAM","at":[31,"Gỗ"]},{"k":"CHẾ ĐỘ","v":"QUY CHẾ CUNG ĐIỆN","at":[31,"Quy"]},{"k":"MỘ","v":"DÂN GỌI LÀ LĂNG","at":[31,"Ngôi"]}]),
 sc("kinetic",33,bg="phu3",items=kin(("MỚI CHỈ LÀ MÓNG",[33,"móng"]),("CHƯA GỌI LÀ LĂNG",[34,"lăng"]),("CHƯA GỌI LÀ KHO",[35,"kho"],"acc"))),
 sc("slam",37,vid=V["v8"],tone="noir",text="ĐỨNG ĐÚNG CHỖ ẤY",hitAt=[37,"đúng"]),
 sc("kinetic",[40,"Cả"],bg="phu",items=kin(("KINH THÀNH NHÌN THẤY",[40,"đều"],"acc"))),
 sc("question",41,bg="luudung",text="TỬ THÙ HAY HAI NGƯỜI ĐỒNG LIÊU?"),
 sc("slam",42,bg="luudung",text="HAI NGƯỜI NGỒI CÙNG MỘT BỘ",hitAt=[42,"ngồi"]),
])
if __name__ == "__main__":
    sys.modules["gen_scenes"] = sys.modules[__name__]
    for n in (2, 3, 4):
        p = D / f"gen_scenes{n}.py"
        if p.exists():
            spec = importlib.util.spec_from_file_location(f"g{n}", p)
            mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); CH.update(mod.CH)
    used=set()
    def walk(x):
        if isinstance(x,dict):
            for k,v in x.items():
                if k in ("img","bg") and isinstance(v,str): used.add(v)
                walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
    walk(CH)
    previous = json.loads((D / "spec.json").read_text(encoding="utf-8"))
    write(__file__, CH, {k:v for k,v in IMGS.items() if k in used}, GEO, endcardBg="hoa")

    generated = json.loads((D / "spec.json").read_text(encoding="utf-8"))
    generated["youtube"] = previous["youtube"]
    generated["say"] = previous["say"]
    (D / "spec.json").write_text(json.dumps(generated, ensure_ascii=False, indent=1)+"\n", encoding="utf-8")
    import subprocess
    # Giữ nguyên "lines" đã duyệt trong chNN.json: script_lines.py viết lại lines (bỏ "‖", gộp câu) làm lệch mọi mốc `at` đã neo vào chỉ số câu cũ.
    _keep = {f.name: json.loads(f.read_text(encoding="utf-8")) for f in D.glob("ch[0-9][0-9].json")}
    subprocess.run([sys.executable, str(ROOT / "motion/long/script_lines.py"), "hoa-than"], check=True)
    for _n, _old in _keep.items():
        _f = D / _n
        _d = json.loads(_f.read_text(encoding="utf-8")); _d["lines"] = _old["lines"]; _d["title"] = _old["title"]
        _f.write_text(json.dumps(_d, ensure_ascii=False, indent=1), encoding="utf-8")
