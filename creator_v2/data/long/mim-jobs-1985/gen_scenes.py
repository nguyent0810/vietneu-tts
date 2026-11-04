"""Cảnh + spec cho Long MIM `mim-jobs-1985` (viết tay từng chương, 29/10/2026).

    python data/long/mim-jobs-1985/gen_scenes.py            # bản thật (ảnh AI ai01–ai06 đã có)
    python data/long/mim-jobs-1985/gen_scenes.py --standin  # thay ảnh AI bằng ảnh tư liệu để soát html

Mọi chữ trên màn hình là cụm viết tay (dữ kiện, con số, tên, đối lập), không cắt từ đầu câu.
"""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).parent
TOPIC = "mim-jobs-1985"
TITLE = "Steve Jobs 1985: Bị Gạt Khỏi Apple, Thành Đường Quay Lại"
STANDIN = "--standin" in sys.argv

SAY = {"steve":"Xtiv","jobs":"Giốp","apple":"Áp-pồ","sculley":"Xcơ-li","pepsi":"Pép-xi","macintosh":"Mác-kin-tót","next":"Nét-xờt","nextstep":"Nét-xờt-step","openstep":"Âu-pần-step","webobjects":"Web-óp-dích","pixar":"Pích-xa","lucasfilm":"Lu-cát-phim","cern":"Xơn","berners-lee":"Bơ-nờz Li","beos":"Bi-ô-ét","ceo":"xi i ô","sec":"ét i xi","10-k":"mười ca"}
IMGS = {"jobs84":"File:Steve_Jobs_and_Macintosh_computer,_January_1984,_by_Bernard_Gotfryd_-_edited.jpg","mac84":"File:Apple_Museum_(Prague)_Macintosh_128K_(1984)_-_1.jpg","nextcube2":"File:Living_Computers_-_NeXT_Cube_(39802959523).jpg","nextstation":"File:NeXTstation_left_side.jpg","sculley06":"File:John_Sculley_2006.jpg"}
STAND = {"ai01":"jobs84","ai02":"mac84","ai03":"nextcube2","ai04":"nextcube2","ai05":"nextstation","ai06":"nextstation"}
if not STANDIN:
    IMGS.update({f"ai0{i}": f"EXT:ai:ai_0{i}" for i in range(1, 7)})
def im(k): return STAND[k] if STANDIN and k in STAND else k

T = {"ch00":"Lá đơn tháng 9","ch01":"Thành công chưa đủ","ch02":"Cuộc chọn lựa tháng 4","ch03":"Mất quyền, rồi rời đi","ch04":"Khoảng trống mang tên NeXT","ch05":"NeXT không thắng ở máy tính","ch06":"Apple cần một lối ra","ch07":"Thương vụ khép vòng","ch08":"Thất bại nào mở đường?"}
LEDGER = "ĐƯỜNG VÒNG 1985 → 2001"
ROWS = [("1983–1984","SCULLEY VỀ · MACINTOSH RA MẮT"),("04.1985","HỘI ĐỒNG CHỌN SCULLEY"),("09.1985","TỰ NỘP ĐƠN TỪ CHỨC"),
        ("1988","NEXT COMPUTER RA MẮT"),("1993","NEXT BỎ PHẦN CỨNG"),("12.1996","APPLE CÔNG BỐ MUA NEXT"),
        ("09.1997","JOBS LÀ CEO TẠM QUYỀN"),("03.2001","MAC OS X PHÁT HÀNH")]
# Ảnh dọc: khung 16:9 phải lấy vùng mặt / thân máy.
FOCUS = {"jobs84":[0.5,0.18], "mac84":[0.45,0.35], "sculley06":[0.5,0.25], "nextcube2":[0.5,0.38]}
VM, AIL = "VIDEO MINH HỌA", "ẢNH MINH HỌA"

def a(line, word): return [line, word]
def _kin(at, text, small=None):
    return [{"text":text,"at":at,"acc":True}] + ([{"text":small,"at":at,"sm":True}] if small else [])
def chapter(no, k, title, sub, bg, at):
    o = {"type":"chapter","no":str(no),"k":k,"title":title,"sub":sub,"bg":im(bg),"titleAt":at}
    if bg in FOCUS: o["focus"] = FOCUS[bg]
    if bg and bg.startswith("ai"): o.update({"credit":False,"illus":AIL})
    return o
def photo(img, at, k, v, s=None, move="in", zoom=None, reveal=None, kin=None):
    o = {"type":"photo","at":at,"img":im(img),"tone":"bw","move":move,"veil":.55,"label":{"k":k,"v":v,"at":at}}
    if s: o["label"]["s"] = s
    if img in FOCUS: o["focus"] = FOCUS[img]
    if img.startswith("ai"): o.update({"illus":AIL,"credit":False,"tone":"color"})
    if zoom: o["zoom"] = zoom
    if reveal: o["reveal"] = reveal
    if kin: o["kin"] = _kin(at, kin)
    return o
def print_scene(img, at, head, k, h, lines, pos=None, maxH=None, maxW=None):
    # Renderer không vẽ `head`: tiêu đề chính phải nằm trong side.h.
    side_lines = ([] if not h or h == head else [{"text":h,"at":at}]) + [{"text":t,"at":x} for t,x in lines]
    o = {"type":"print","at":at,"img":im(img),"tone":"bw","head":head,"side":{"k":k,"h":head or h,"lines":side_lines}}
    if img in FOCUS: o["focus"] = FOCUS[img]
    if pos is not None: o["pos"] = pos
    if maxH is not None: o["maxH"] = maxH
    if maxW is not None: o["maxW"] = maxW
    return o
def broll(vid, at, text, small=None, pan=None):
    o = {"type":"broll","at":at,"vid":str(vid),"veil":.6,"illus":VM,"kin":_kin(at, text, small)}
    if pan: o["pan"] = pan
    return o
def with_vid(scene, vid):
    scene.update({"vid":str(vid),"illus":VM}); return scene
def with_bg(scene, bg):
    scene["bg"] = im(bg)
    if bg.startswith("ai"): scene.update({"credit":False,"illus":AIL})
    return scene
def kinetic(at, text, small=None): return {"type":"kinetic","at":at,"items":_kin(at, text, small)}
def slam(at, text, sub): return {"type":"slam","at":at,"text":text,"sub":sub}
def date(at, day, d, sub): return {"type":"date","at":at,"day":day,"date":d,"sub":{"text":sub,"at":at}}
def question(at, text): return {"type":"question","at":at,"text":text}
def quote(at, text, by, lbl="DIỄN Ý"): return {"type":"quote","at":at,"text":text,"by":by,"lbl":lbl}
def counter(at, to, suffix, label, year=False): return {"type":"counter","at":at,"from":0,"to":to,"suffix":suffix,"label":label,"year":year}
def timeline(at, items, bg=None):
    o = {"type":"timeline","at":at,"items":[{"year":y,"text":t,"at":x} for y,t,x in items]}
    if bg: o["bg"] = im(bg)
    return o
def org(at, nodes): return {"type":"org","at":at,"nodes":[dict(zip(("id","t","s","p","at"),n)) for n in nodes]}
def bars(at, title, unit, items): return {"type":"bars","at":at,"title":title,"unit":unit,"items":[{"k":k,"v":v,"at":x,**({"acc":True} if acc else {})} for k,v,x,acc in items]}
def split(at, title, A, B):
    return {"type":"split","at":at,"title":title,"a":{"img":im(A[0]),"label":A[1],"at":A[2],"tone":"bw"},"b":{"img":im(B[0]),"label":B[1],"at":B[2],"tone":"bw"}}
def file_card(at, k, name, desc, rows): return {"type":"file","at":at,"k":k,"name":name,"desc":desc,"rows":[{"k":x,"v":y,"at":z} for x,y,z in rows]}
def source(at, src, ref, snippet, hl, seal): return {"type":"source","at":at,"source":src,"ref":ref,"snippet":snippet,"hlAt":hl,"seal":seal}
def evidence(img, at, callouts): return {"type":"evidence","at":at,"img":im(img),"tone":"bw","callouts":[{"x":x,"y":y,"text":t,"at":w,"side":sd} for x,y,t,w,sd in callouts]}
def ledger(n, at): return {"type":"ledger","at":at,"title":LEDGER,"srcnote":"MỖI CHƯƠNG THÊM MỘT MỐC","rows":[{"k":k,"v":v,"at":at} for k,v in ROWS[max(0,n-5):n]]}

def ch00(): return [
 chapter(0,"MỞ ĐẦU","LÁ ĐƠN\nTHÁNG 9","09.1985 · NGƯỜI ĐỒNG SÁNG LẬP RỜI APPLE","jobs84",a(0,"tháng")),
 broll(5924021,a(0,"lập"),"ĐƠN TỪ CHỨC · 09.1985","NGƯỜI ĐỒNG SÁNG LẬP RỜI CÔNG TY CỦA MÌNH"),
 photo("ai01",a(1,"trước"),"TRƯỚC LÁ ĐƠN","ĐÃ MẤT QUYỀN ĐIỀU HÀNH","VẪN GIỮ GHẾ CHỦ TỊCH HỘI ĐỒNG",reveal={"kind":"wipe","at":a(1,"trước"),"d":0.9}),
 broll(6951393,a(2,"hội"),"HỘI ĐỒNG QUẢN TRỊ","GIÁM SÁT NHỮNG QUYẾT ĐỊNH LỚN"),
 org(a(3,"quyền"),[("hd","HỘI ĐỒNG","GIÁM SÁT",None,a(3,"quyền")),("dh","NGƯỜI ĐIỀU HÀNH","VIỆC MỖI NGÀY","hd",a(3,"công")),("sp","NHÂN SỰ · SẢN PHẨM","NGƯỜI PHỤ TRÁCH · HƯỚNG ĐI","dh",a(3,"phụ"))]),
 kinetic(a(4,"vì"),"CÒN Ở LẠI · HẾT CẦM LÁI","CÓ MẶT TRONG CÔNG TY NHƯNG KHÔNG ĐIỀU HÀNH"),
 slam(a(5,"nghịch"),"NGHỊCH LÝ","RỜI ĐI RỒI QUAY LẠI"),
 timeline(a(6,"mua"),[("1985","RỜI APPLE",a(6,"mua")),("02.1997","APPLE MUA XONG NEXT",a(6,"lập")),("09.1997","CEO TẠM QUYỀN",a(7,"rồi"))]),
 question(a(8,"vậy"),"VÌ SAO LẦN RỜI ĐI\nTHÀNH ĐƯỜNG QUAY LẠI?"),
 slam(a(9,"để"),"HAI VIỆC KHÁC NHAU","THƯỜNG BỊ GỘP LÀM MỘT"),
 kinetic(a(10,"bị"),"BƯỚC MỘT","BỊ TƯỚC QUYỀN ĐIỀU HÀNH"),
 broll(7685810,a(11,"ông"),"BƯỚC HAI","TỰ CHỌN RỜI KHỎI APPLE")]

def ch01(): return [
 chapter(1,"CHƯƠNG MỘT","THÀNH CÔNG\nCHƯA ĐỦ","1983 → 1984 · SCULLEY VÀ MACINTOSH","mac84",a(0,"năm")),
 date(a(0,"tuyển"),"JOHN SCULLEY VỀ APPLE","1983","TỪ PEPSI · JOBS GÓP PHẦN TUYỂN"),
 print_scene("jobs84",a(1,"một"),"","MACINTOSH","RA MẮT",[("GIAI ĐOẠN ĐẦY KỲ VỌNG",a(1,"một"))]),
 photo("mac84",a(2,"nhưng"),"MACINTOSH 128K","SẢN PHẨM GÂY CHÚ Ý","ẢNH BẢO TÀNG APPLE, PRAGUE"),
 broll(7593886,a(2,"khi"),"SẢN PHẨM · NHÂN SỰ · TIỀN BẠC","AI CHỊU TRÁCH NHIỆM?"),
 slam(a(3,"danh"),"NHÀ SÁNG LẬP","CHƯA CHẮC NẮM QUYỀN HẰNG NGÀY"),
 quote(a(4,"theo"),"HỘI ĐỒNG ĐÃ CHỌN CHÍNH NGƯỜI TÔI MỜI VỀ.","STEVE JOBS · STANFORD 2005","TRÍCH DỊCH"),
 photo("ai02",a(5,"xác"),"HAI PHÍA MỘT CUỘC CHỌN","JOBS VÀ SCULLEY",move="pan"),
 broll(6951506,a(6,"người"),"AI QUYẾT ĐỊNH?","KHÔNG PHẢI NGƯỜI MUA MACINTOSH"),
 org(a(7,"hội"),[("hd","HỘI ĐỒNG QUẢN TRỊ","NGƯỜI QUYẾT ĐỊNH",None,a(7,"hội")),("dh","NGƯỜI ĐIỀU HÀNH","CHỊU GIÁM SÁT","hd",a(7,"giám"))]),
 kinetic(a(8,"thành"),"DOANH SỐ KHÔNG PHẢI LÁ PHIẾU","TRONG TRANH CHẤP QUYỀN LỰC"),
 org(a(9,"khi"),[("sp","NGƯỜI TẠO SẢN PHẨM","JOBS",None,a(9,"khi")),("dh","NGƯỜI ĐIỀU HÀNH","TỔ CHỨC","sp",a(9,"điều"))]),
 ledger(1,a(10,"sự"))]

def ch02(): return [
 chapter(2,"CHƯƠNG HAI","CUỘC CHỌN LỰA\nTHÁNG 4","04.1985 · HỘI ĐỒNG QUẢN TRỊ HỌP","sculley06",a(0,"tháng")),
 date(a(0,"họp"),"HỘI ĐỒNG HỌP HAI NGÀY","10.04.1985","CHỌN GIỮA JOBS VÀ SCULLEY"),
 with_vid(kinetic(a(1,"cuộc"),"NHẤT TRÍ","ỦNG HỘ SCULLEY · THEO CULT OF MAC"),6951299),
 photo("ai02",a(2,"kết"),"KẾT QUẢ","JOBS MẤT VAI TRÒ ĐIỀU HÀNH","PHÓ CHỦ TỊCH · QUẢN LÝ BỘ PHẬN MACINTOSH",move="out"),
 slam(a(3,"ông"),"CHƯA RỜI APPLE","SAU CUỘC HỌP THÁNG 4"),
 org(a(4,"đổi"),[("hd","HỘI ĐỒNG","ĐÃ CHỌN",None,a(4,"đổi")),("sc","SCULLEY","NẮM QUYỀN ĐIỀU HÀNH","hd",a(4,"nơi")),("jb","JOBS","CÒN TÊN VÀ CHỨC DANH","hd",a(4,"trong"))]),
 photo("mac84",a(5,"nhưng"),"BỘ PHẬN MACINTOSH","KHÔNG CÒN TRONG TAY JOBS",move="pan"),
 broll(6951393,a(6,"đây"),"KHÔNG CHỈ LÀ BẤT ĐỒNG","GIỮA HAI CÁ NHÂN",pan="l"),
 kinetic(a(7,"lựa"),"QUYẾT ĐỊNH CỦA HỘI ĐỒNG","CƠ QUAN GIÁM SÁT ĐÃ CHỌN"),
 slam(a(8,"giữ"),"CHƯA BỊ SA THẢI","VẪN GIỮ GHẾ CHỦ TỊCH MỘT THỜI GIAN"),
 timeline(a(9,"quyền"),[("04.1985","QUYỀN ĐIỀU HÀNH CHUYỂN ĐI",a(9,"quyền")),("09.1985","ĐƠN TỪ CHỨC",a(9,"đơn"))]),
 ledger(2,a(10,"từ")),
 question(a(11,"còn"),"KHÔNG ĐƯỢC ĐIỀU HÀNH,\nJOBS CÒN LÀM GÌ?")]

def ch03(): return [
 chapter(3,"CHƯƠNG BA","MẤT QUYỀN,\nRỒI RỜI ĐI","05 → 09.1985","ai05",a(0,"tháng")),
 timeline(a(0,"thất"),[("04.1985","HỘI ĐỒNG CHỌN SCULLEY",a(0,"thất")),("05.1985","PHẢN CÔNG THẤT BẠI",a(0,"theo"))]),
 broll(7581306,a(1,"cuối"),"TÁI CẤU TRÚC · CUỐI THÁNG 5","HẾT VAI TRÒ ĐIỀU HÀNH HẰNG NGÀY"),
 date(a(2,"ngày"),"SAN JOSE MERCURY NEWS","01.06.1985","BÀI BÁO VỀ CUỘC TÁI CẤU TRÚC"),
 source(a(2,"việc"),"BÁO 1985 · DO TECHNOLOGIZER LƯU LẠI","NGƯỜI ĐỒNG SÁNG LẬP BỊ GIÁNG CHỨC","Tờ báo gọi việc tái cấu trúc là [[giáng chức]] người đồng sáng lập Apple.",a(2,"giáng"),"DẪN LẠI QUA TECHNOLOGIZER"),
 broll(8888818,a(3,"ông"),"VAI TRÒ RỘNG HƠN?","ĐỔI MỚI SẢN PHẨM · CHIẾN LƯỢC"),
 print_scene("sculley06",a(4,"ngày"),"JOHN SCULLEY · 25.07.1985","JOBS KHÔNG CÓ VAI TRÒ ĐIỀU HÀNH", "",[("ẢNH NĂM 2006",a(4,"ngày"))]),
 org(a(5,"hai"),[("m","BƯỚC 1 · BỊ TƯỚC QUYỀN","MẤT VAI TRÒ ĐIỀU HÀNH",None,a(5,"hai")),("t","BƯỚC 2 · TỰ NỘP ĐƠN","MỚI LÀ TỪ CHỨC","m",a(5,"việc"))]),
 with_bg(quote(a(6,"trong"),"NĂM 30 TUỔI, TÔI BỊ LOẠI RA, RẤT CÔNG KHAI.","STEVE JOBS · STANFORD 2005","TRÍCH DỊCH"),"ai01"),
 kinetic(a(7,"quyền"),"QUYỀN ĐÃ SANG TAY","CHỨC DANH CHƯA MẤT NGAY"),
 broll(5924021,a(8,"nộp"),"DẤU CHẤM PHÁP LÝ","LÁ ĐƠN TỪ CHỨC THÁNG 9"),
 ledger(3,a(9,"phần")),
 print_scene("nextcube2",a(10,"đó"),"BƯỚC TIẾP THEO","1985","RỜI APPLE ĐỂ LẬP NEXT",[("MÁY NEXT CUBE · ẢNH BẢO TÀNG",a(10,"đó"))])]

def ch04(): return [
 chapter(4,"CHƯƠNG BỐN","KHOẢNG TRỐNG\nMANG TÊN NEXT","1985 → 1995 · NEXT VÀ PIXAR","ai04",a(0,"sau")),
 photo("ai03",a(0,"người"),"NĂM NGƯỜI THEO JOBS","RỜI APPLE LẬP NEXT","THEO TƯ LIỆU TỔNG HỢP",reveal={"kind":"circle","at":a(0,"người"),"d":0.9}),
 broll(6285657,a(1,"kiện"),"APPLE KIỆN NEXT","CHỈ ÍT NGÀY SAU"),
 slam(a(1,"bị"),"VỤ KIỆN BỊ RÚT","HOẶC BÃI BỎ TRƯỚC KHI XÉT XỬ"),
 print_scene("nextcube2",a(2,"năm"),"NEXT COMPUTER","RA MẮT NĂM 1988","",[("MÁY NEXT CUBE · ẢNH BẢO TÀNG",a(2,"năm"))]),
 counter(a(2,"giá"),6500," USD","GIÁ CƠ BẢN · THEO CHM"),
 org(a(3,"máy"),[("hw","MÁY NEXT","PHẦN CỨNG",None,a(3,"máy")),("dev","MÔI TRƯỜNG LẬP TRÌNH","CÔNG CỤ PHÁT TRIỂN","hw",a(3,"môi"))]),
 broll(854027,a(4,"thiết"),"GIÁO DỤC · NGHIÊN CỨU","THỊ TRƯỜNG NEXT NHẮM TỚI"),
 kinetic(a(4,"tạo"),"VIẾT PHẦN MỀM MỚI","KHÔNG CHỈ CHẠY PHẦN MỀM CÓ SẴN"),
 photo("nextstation",a(5,"lựa"),"LỰA CHỌN THỊ TRƯỜNG","XA MÁY TÍNH ĐẠI CHÚNG","ẢNH: NEXTSTATION",move="pan"),
 org(a(6,"nhưng"),[("tt","TRUNG TÂM CỦA NEXT","",None,a(6,"nhưng")),("os","HỆ ĐIỀU HÀNH","","tt",a(6,"nhưng")),("cc","CÔNG CỤ PHÁT TRIỂN","","tt",a(6,"nó"))]),
 counter(a(7,"đầu"),10," TRIỆU USD","ĐẦU TƯ VÀO PIXAR · ĐẦU 1986"),
 bars(a(8,"theo"),"10 TRIỆU USD CHIA ĐÔI","TRIỆU USD · THEO ALVY RAY SMITH",[("TRẢ LUCASFILM",5,a(8,"theo"),False),("VỐN CÔNG TY MỚI",5,a(8,"trả"),True)]),
 broll(856593,a(9,"năm"),"TOY STORY · 1995","RA RẠP VÀI NGÀY TRƯỚC KHI PIXAR LÊN SÀN"),
 with_vid(timeline(a(10,"theo"),[("22.11.1995","PHIM RA RẠP",a(10,"theo")),("28.11.1995","CHÀO BÁN CỔ PHIẾU",a(10,"chào"))]),7988642),
 slam(a(11,"đây"),"HAI THÀNH CÔNG\nKHÁC HẲN","PIXAR · NEXT"),
 broll(37203868,a(12,"chứng"),"ĐỒ HỌA MÁY TÍNH","ĐỦ SỨC LÀM PHIM DÀI"),
 kinetic(a(13,"bên"),"BÊN KIA LÀ NEXT","RỜI BÁN MÁY · DỒN VÀO PHẦN MỀM"),
 org(a(14,"dự"),[("jb","STEVE JOBS SAU 1985","",None,a(14,"dự")),("nx","NEXT","DỰ ÁN CÔNG NGHỆ MỚI","jb",a(14,"công")),("px","PIXAR","ĐẦU TƯ · PHIM ĐỒ HỌA","jb",a(15,"khoản"))]),
 with_vid(kinetic(a(16,"bảo"),"CHƯA GÌ BẢO ĐẢM","MỘT ĐƯỜNG VỀ APPLE"),7651686),
 ledger(4,a(17,"nhưng")),
 slam(a(18,"chỉ"),"CHỈ CÓ NEXT","NỐI THẲNG VỚI THƯƠNG VỤ VỀ SAU")]

def ch05(): return [
 chapter(5,"CHƯƠNG NĂM","NEXT KHÔNG THẮNG\nỞ MÁY TÍNH","1993 · NEXT SOFTWARE","nextstation",a(0,"theo")),
 counter(a(0,"máy"),50," NGHÌN MÁY","TỔNG SỐ MÁY NEXT ĐÃ BÁN · XẤP XỈ"),
 kinetic(a(1,"công"),"1993 · NEXT SOFTWARE","RỜI MẢNG PHẦN CỨNG"),
 bars(a(1,"cắt"),"NHÂN SỰ NEXT NĂM 1993","NGƯỜI",[("BỊ CẮT GIẢM",230,a(1,"cắt"),True),("CÒN LẠI",300,a(1,"trong"),False)]),
 photo("ai04",a(2,"chiếc"),"MÁY KHÔNG THẮNG LỚN","PHẦN MỀM KHÔNG BIẾN MẤT"),
 slam(a(3,"đó"),"BƯỚC NGOẶT","MÁY THUA · PHẦN MỀM Ở LẠI"),
 broll(7140937,a(4,"công"),"GIÁ TRỊ Ở BÊN TRONG","KHÔNG NẰM Ở VỎ MÁY"),
 org(a(5,"với"),[("n","NEXT SOFTWARE","THỨ CÒN LẠI",None,a(5,"với")),("h","HỆ ĐIỀU HÀNH","","n",a(5,"hệ")),("c","CÔNG CỤ LÀM PHẦN MỀM","","n",a(5,"công"))]),
 kinetic(a(6,"giá"),"KHÔNG ĐO BẰNG SỐ MÁY","GIÁ TRỊ ĐÃ ĐỔI CHỖ"),
 broll(8888977,a(7,"nằm"),"PHẦN MỀM ẤY","GIÚP CÔNG TY KHÁC LÀM GÌ?"),
 with_vid(kinetic(a(8,"dấu"),"MỘT DẤU VẾT CỤ THỂ","CÔNG NGHỆ ĐI XA HƠN CHIẾC MÁY"),30607101),
 org(a(9,"tại"),[("cern","CERN · 1990","WEBSITE ĐẦU TIÊN",None,a(9,"tại")),("next","MÁY NEXT","NƠI ĐẶT MÁY CHỦ","cern",a(9,"máy"))]),
 date(a(10,"trình"),"TRÌNH DUYỆT WEB ĐẦU TIÊN","1990","THEO CERN"),
 kinetic(a(11,"điều"),"KHÔNG THÀNH HÃNG MÁY THẮNG LỚN","NHƯNG NỀN TẢNG VẪN SỐNG"),
 org(a(12,"nền"),[("n","NỀN TẢNG NEXT","",None,a(12,"nền")),("r","ĐỜI SỐNG RIÊNG","NGOÀI PHẦN CỨNG","n",a(12,"riêng"))]),
 broll(8888818,a(13,"đánh"),"ĐỪNG CHỈ ĐẾM SỐ MÁY","KHI ĐÁNH GIÁ NEXT"),
 with_vid(kinetic(a(14,"những"),"NHÌN VÀO THỨ ĐƯỢC XÂY","TRÊN HỆ ĐIỀU HÀNH ẤY"),854027),
 ledger(5,a(15,"lý"))]

def ch06(): return [
 chapter(6,"CHƯƠNG SÁU","APPLE CẦN\nMỘT LỐI RA","1996 · TÌM HỆ ĐIỀU HÀNH MỚI","ai03",a(0,"năm")),
 broll(6134025,a(0,"hành"),"KHÔNG CHỈ CÓ NEXT","APPLE TÌM HỆ ĐIỀU HÀNH MỚI"),
 photo("ai05",a(1,"theo"),"HAI ỨNG VIÊN","BEOS · HỆ ĐIỀU HÀNH CỦA NEXT","THEO COMPUTER HISTORY MUSEUM"),
 org(a(1,"sánh"),[("ap","APPLE · 1996","ĐÀM PHÁN VÀ SO SÁNH",None,a(1,"sánh")),("be","BE","BEOS","ap",a(1,"hệ")),("nx","NEXT","NEXTSTEP","ap",a(1,"của"))]),
 slam(a(2,"sau"),"APPLE CHỌN NEXT","SAU CUỘC SO SÁNH"),
 date(a(3,"ngày"),"THÔNG CÁO MUA NEXT","20.12.1996","APPLE CÔNG BỐ THƯƠNG VỤ"),
 with_vid(counter(a(3,"công"),400," TRIỆU USD","GIÁ GHI TRONG THÔNG CÁO"),8426053),
 source(a(4,"báo"),"APPLE · BÁO CÁO NĂM 10-K NỘP SEC","TỔNG GIÁ MUA NEXT: 427 TRIỆU USD","Con số tính [[cả các nghĩa vụ]] được gộp vào thương vụ.",a(4,"gồm"),"ĐÃ ĐỐI CHIẾU BÁO CÁO NĂM"),
 bars(a(5,"đó"),"MỘT GIAO DỊCH · HAI CÁCH GHI","TRIỆU USD",[("THÔNG CÁO 12.1996",400,a(5,"đó"),False),("BÁO CÁO NĂM 10-K",427,a(5,"tài"),True)]),
 broll(7593886,a(6,"báo"),"SỨC ÉP RÕ RỆT","BÁO CÁO TÀI CHÍNH CÙNG KỲ"),
 bars(a(7,"doanh"),"DOANH THU APPLE","TRIỆU USD · NĂM TÀI CHÍNH",[("NĂM TC 1996",9833,a(7,"doanh"),False),("NĂM TC 1997",7081,a(7,"thấp"),True)]),
 counter(a(8,"lỗ"),1045," TRIỆU USD","LỖ RÒNG NĂM TC 1997 · KỲ TRƯỚC LỖ 816"),
 with_vid(kinetic(a(9,"chúng"),"KHÔNG PHẢI DỰ ÁN TRANG TRÍ","APPLE CẦN NỀN TẢNG MỚI"),6285657),
 question(a(10,"điều"),"APPLE THỰC SỰ\nMUA THỨ GÌ?"),
 timeline(a(11,"cần"),[("1996","APPLE CẦN HỆ ĐIỀU HÀNH MỚI",a(11,"cần")),("12.1996","MUA NEXT LẤY NỀN TẢNG",a(11,"nền"))]),
 org(a(12,"đem"),[("nx","NEXT MANG ĐẾN","",None,a(12,"đem")),("ns","NEXTSTEP","HỆ ĐIỀU HÀNH","nx",a(12,"đến")),("os","OPENSTEP","ĐẶC TẢ MỞ","nx",a(12,"và")),("wo","WEBOBJECTS","PHẦN MỀM WEB","nx",a(12,"chứ")),("sj","STEVE JOBS","KHÔNG CHỈ MỘT NGƯỜI","nx",a(12,"chứ"))]),
 kinetic(a(13,"vì"),"MỘT QUYẾT ĐỊNH · HAI HỆ QUẢ","KỸ THUẬT · NHÂN SỰ"),
 broll(30607101,a(14,"rời"),"LỜI GIẢI PHẦN MỀM","TỪ MỘT CÔNG TY ĐÃ BỎ PHẦN CỨNG"),
 slam(a(15,"đường"),"KHÔNG PHẢI HOÀI NIỆM","MÀ LÀ CÔNG NGHỆ"),
 ledger(6,a(16,"nó"))]

def ch07(): return [
 chapter(7,"CHƯƠNG BẢY","THƯƠNG VỤ\nKHÉP VÒNG","1997 → 2001","nextstation",a(0,"ngày")),
 date(a(0,"hoàn"),"APPLE HOÀN TẤT MUA NEXT","07.02.1997","THEO MACTECH"),
 kinetic(a(1,"nói"),"CỐ VẤN CHO GIL AMELIO","VAI TRÒ ĐẦU TIÊN · THEO THÔNG CÁO"),
 timeline(a(2,"đến"),[("07.02.1997","HOÀN TẤT MUA NEXT",a(2,"đến")),("16.09.1997","CEO TẠM QUYỀN",a(2,"công"))]),
 kinetic(a(2,"nghĩa"),"TẠM QUYỀN","GIỮ GHẾ ĐẾN KHI CÓ CEO MỚI"),
 photo("ai06",a(3,"sự"),"TRỞ LẠI TỪNG BƯỚC","KHÔNG PHẢI MỘT BUỔI LỄ",reveal={"kind":"wipe","at":a(3,"sự"),"d":0.9}),
 print_scene("sculley06",a(4,"theo"),"JOHN SCULLEY","NHÌN LẠI NĂM 1985", "",[("ẢNH NĂM 2006",a(4,"theo"))]),
 quote(a(4,"việc"),"VIỆC NGƯỜI SÁNG LẬP RỜI ĐI LÀ MỘT SAI LẦM, VÀ TÔI CÓ PHẦN TRONG ĐÓ.","JOHN SCULLEY · THEO THE REGISTER","TRÍCH DỊCH"),
 org(a(5,"rõ"),[("cn","APPLE CẦN CÔNG NGHỆ","",None,a(5,"rõ")),("mn","MUA NEXT","","cn",a(5,"mua")),("tl","JOBS TRỞ LẠI","CẤU TRÚC MỚI","mn",a(5,"trở"))]),
 kinetic(a(6,"ghi"),"NEXTSTEP → MAC OS X","THEO COMPUTER HISTORY MUSEUM"),
 date(a(7,"phát"),"MAC OS X PHÁT HÀNH","03.2001","NỀN TẢNG GỐC NEXTSTEP"),
 slam(a(8,"chú"),"KHÔNG PHẢI\nCHÚ THÍCH BÊN LỀ","GIỮA HAI LẦN Ở APPLE"),
 broll(7651686,a(9,"lấy"),"CON ĐƯỜNG THỰC TẾ","CÔNG NGHỆ ĐI TRƯỚC · JOBS ĐI CÙNG"),
 with_vid(kinetic(a(10,"thất"),"PHẦN CỨNG THẤT BẠI","PHẦN MỀM VẪN CÒN GIÁ TRỊ"),8888977),
 ledger(7,a(11,"phân"))]

def ch08(): return [
 chapter(8,"CHƯƠNG TÁM","THẤT BẠI NÀO\nMỞ ĐƯỜNG?","1985 → 1997 · CÂU TRẢ LỜI","nextcube2",a(0,"mất")),
 photo("jobs84",a(1,"ông"),"1985","TỰ RỜI ĐI SAU KHI MẤT QUYỀN","ẢNH THÁNG 1 · 1984",move="pan"),
 org(a(2,"lần"),[("r","RỜI APPLE","",None,a(2,"lần")),("x","XÂY NEXT","","r",a(2,"xây")),("g","GIỮ PHẦN MỀM APPLE CẦN","","x",a(2,"giữ"))]),
 slam(a(3,"câu"),"LỜI GIẢI NGHỊCH LÝ","RỜI ĐI · XÂY · ĐƯỢC MUA LẠI"),
 photo("ai06",a(4,"gọi"),"KHÔNG CHỈ VÌ DANH HIỆU","NGƯỜI SÁNG LẬP",move="out"),
 broll(8426053,a(5,"mua"),"MUA ĐỂ LẤY CÔNG NGHỆ","NEXT CÓ THỨ APPLE CẦN"),
 timeline(a(6,"thương"),[("1997","JOBS TRỞ LẠI",a(6,"thương")),("2001","NỀN TẢNG MAC OS X",a(6,"nền"))]),
 broll(7685810,a(7,"chuyện"),"VẪN LẶP LẠI","NGƯỜI SÁNG LẬP BỊ GẠT KHỎI CÔNG TY"),
 kinetic(a(8,"đường"),"ĐƯỜNG VÒNG","KHÔNG XÓA CUỘC THUA CŨ"),
 ledger(8,a(9,"kinh"))]

SCENES = [ch00, ch01, ch02, ch03, ch04, ch05, ch06, ch07, ch08]
SOURCES = ["https://computerhistory.org/apple-timeline/","https://www.cultofmac.com/apple-history/steve-jobs-macintosh-division","https://technologizer.com/2011/08/25/steve-jobs-steps-down-the-first-time-the-1985-press-coverage/index.html","https://www.mactech.com/content/md1-apple-acquires-next-software-0","https://www.sec.gov/Archives/edgar/data/0000320193/000104746997006960/0001047469-97-006960.txt","https://www.mactech.com/1997/02/08/md1-apple-finalizes-next-acq","https://www.mactech.com/1997/09/16/md1-jobs-interim-ceo/","https://home.cern/science/computing/the-birth-of-the-web","https://www.alvyray.com/Pixar/PixarMyth1.htm","https://www.computerhistory.org/timeline/1988/"]

def make_spec(): return {"topic":TOPIC,"title":TITLE,"channel":"MIM","theme":"lab","look":"steel","accent":"#f59e0b","master":True,"beat2":True,"say":SAY,"imgs":IMGS,"chapters":[f"ch{i:02d}" for i in range(len(SCENES))],"youtube":{"titles":[TITLE],"publish_at":"2026-12-01T13:00:00Z","playlist":"Công Nghệ Quanh Ta","category":"28","thumb":"t1.jpg","summary":"Steve Jobs mất quyền điều hành tại Apple năm 1985 rồi rời đi. Mười hai năm sau, Apple mua NeXT để lấy nền tảng phần mềm, mở đường cho ông trở lại.","more":["Video dùng ảnh tư liệu được cấp phép, clip Pexels có nhãn VIDEO MINH HỌA và đồ họa minh họa dữ kiện."],"chapter_titles":T,"sources":SOURCES,"tags":["Steve Jobs","Apple","NeXT","Mac OS X","lịch sử công nghệ"],"hashtags":["SteveJobs","Apple","NeXT","MindInTheMachine"],"video_credits":["Ảnh tư liệu: Wikimedia Commons, Public Domain, CC0 hoặc CC BY.","Video minh họa: Pexels."]},"sources_internal":"Nguồn và giấy phép chi tiết trong factcheck.md; sáu ảnh minh họa ai01–ai06 đã có trong output/long/mim-jobs-1985/img."}

# ---------- tự kiểm neo: từ có thật trong câu, không phải số, không nằm trong SAY, tăng dần ----------
def _tok(line): return [re.sub(r"[^\wÀ-ỹ]", "", w).lower() for w in line.split()]
def _anchors(node, out):
    if isinstance(node, dict):
        for v in node.values(): _anchors(v, out)
    elif isinstance(node, list):
        if len(node) == 2 and isinstance(node[0], int) and isinstance(node[1], str): out.append(node)
        else:
            for v in node: _anchors(v, out)
def check(ch, scenes, lines):
    toks = [_tok(x if isinstance(x, str) else x.get("t", "")) for x in lines]
    def pos(x):
        w = x[1].lower()
        assert not re.search(r"\d", w) and w not in SAY, f"ch{ch:02d}: neo {x} là số hoặc tên trong SAY"
        assert x[0] < len(toks) and w in toks[x[0]], f"ch{ch:02d}: từ '{w}' không có trong câu {x[0]}: {toks[x[0]] if x[0] < len(toks) else '-'}"
        return (x[0], toks[x[0]].index(w))
    prev = (-1, -1)
    for i, s in enumerate(scenes):
        found = []; _anchors(s, found)
        p = pos(s.get("at") or s.get("titleAt"))
        assert i == 0 or p > prev, f"ch{ch:02d}: cảnh {i} ({s['type']}) neo {s.get('at')} không sau cảnh trước"
        for x in found: assert pos(x) >= p, f"ch{ch:02d}: cảnh {i} có neo con {x} trước neo cảnh"
        for k in ("nodes", "items"):
            if k in s and isinstance(s[k], list) and s[k] and "at" in s[k][0] and s["type"] in ("org", "timeline"):
                assert s[k][0]["at"] == s["at"], f"ch{ch:02d}: cảnh {i} mục đầu không neo cùng cảnh"
        prev = p

def main():
    (ROOT/"spec.json").write_text(json.dumps(make_spec(), ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    for n, fn in enumerate(SCENES):
        p = ROOT/f"ch{n:02d}.json"; d = json.loads(p.read_text(encoding="utf-8"))
        sc = fn(); check(n, sc, d.get("lines", []))
        d.update({"topic":TOPIC,"chapter":n,"scenes":sc,"hud":{"k":f"CHƯƠNG {n:02d}","t":T[f"ch{n:02d}"].upper()}})
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1)+"\n", encoding="utf-8")
    print(f"Đã tạo spec.json và {len(SCENES)} chương cho {TOPIC}"+(" (BẢN THAY TẠM ẢNH AI — đừng render)" if STANDIN else "."))
if __name__ == "__main__": main()
