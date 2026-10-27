"""Showreel kho hiệu ứng video dài (longform.js): mọi họ hiệu ứng chạy đủ số lần để bộ chọn
đi qua hết các biến thể. Không TTS: wav im lặng + manifest tự dựng, phụ đề là
tên hiệu ứng. Chạy từ gốc repo: python hf_showreel.py [draft|looks]"""
import json, subprocess, sys
from pathlib import Path

OUT = Path("output/cl_staging/reel"); OUT.mkdir(parents=True, exist_ok=True)
STEP = 4.0
L = [
 "**Kho hiệu ứng video dài**",
 "Vòng mười hai con giáp — lối vào một.", "Quan hệ vẽ ra đúng lúc được nhắc tới.",
 "Bố cục ảnh tự luân phiên.",
 "**Sơ đồ ngũ hành**",
 "Ngũ hành nạp âm — lối vào một.", "Thẻ năm sinh lật, mũi tên sinh khắc.",
 "Video nền tràn khung.",
 "Thẻ năm sinh — biến thể một.",
 "Danh sách — biến thể một.", "Mục sau hiện khi được nhắc tới.",
 "Bố cục ảnh thứ ba.",
 "**Dòng thời gian mười hai năm**",
 "Điểm sáng chạy qua từng mốc năm.", "Mốc hiện tại tô vàng.",
 "So sánh hai vế — thẻ mở như sách.", "Vế phải vào khi được nhắc tới.",
 "Con số lớn đếm lên cùng vòng.",
 "Bố cục ảnh thứ tư.",
 "Vòng mười hai con giáp — lối vào hai.", "Tam hợp và lục hợp.",
 "Thẻ năm sinh — biến thể hai.",
 "Danh sách — biến thể hai.", "Bật lên từ đáy như lò xo.",
 "Bố cục ảnh thứ năm.",
 "**Phần bốn của video**",
 "Vòng mười hai con giáp — lối vào ba.", "Xung và tam hình.",
 "Thẻ năm sinh — biến thể ba.",
 "Danh sách — biến thể ba.", "Mục đang nói sáng lên.",
 "Ngũ hành nạp âm — lối vào hai.", "Bước thứ hai.",
 "Bố cục ảnh thứ sáu.",
 "**Phần năm của video**",
 "Bố cục ảnh thứ bảy.",
 "Video nền thứ hai.",
 "**Phase A: nét vẽ tay và kính**",
 "Người xưa xem năm xung là **lời nhắc thận trọng**, không phải một bản án.",
 "Hình là **vướng mắc**, còn phá là **gián đoạn** giữa chừng.",
 "Tuổi Tuất giữ **chữ tín** làm điểm tựa trong năm này.",
 "Ảnh ghim bảng, dán băng keo.",
 "Thẻ kính trên ảnh tràn khung.",
 "Vòng tròn vẽ tay quanh năm sinh.",
 "Danh sách có bút dạ quang.", "Mục đang đọc được tô.",
 "Bố cục ảnh cuối.",
 "Hết showreel.",
]
n = len(L)
media = {
 "4": {"kind": "image", "query": "zodiac wheel chinese temple ceiling", "reveal": "iris"},
 "8": {"kind": "video", "query": "goat on mountain"},
 "12": {"kind": "image", "query": "red lanterns lunar new year", "reveal": "wipe"},
 "19": {"kind": "image", "query": "old temple courtyard morning", "reveal": "rise"},
 "25": {"kind": "image", "query": "vietnamese family gathering elderly", "reveal": "iris"},
 "34": {"kind": "image", "query": "asian water buffalo close up", "reveal": "wipe"},
 "36": {"kind": "image", "query": "calm lake morning mist", "reveal": "rise"},
 "37": {"kind": "video", "query": "clouds timelapse mountain"},
 "42": {"kind": "image", "query": "hand turning calendar page", "layout": "pinned"},
 "43": {"kind": "image", "query": "red lanterns night festival", "layout": "full"},
 "47": {"kind": "image", "query": "incense sticks burning smoke close up", "reveal": "wipe"},
}
yrs = [{"yr": "1970", "sub": "Canh Tuất"}, {"yr": "1982", "sub": "Nhâm Tuất"}, {"yr": "1994", "sub": "Giáp Tuất"}]
lst = lambda t: {"type": "list", "title": t, "items": [{"text": "Đọc kỹ giấy tờ"}, {"text": "Làm từng bước nhỏ"}, {"text": "Giữ chữ tín"}]}
visuals = {
 "2": {"type": "wheel", "title": "VÒNG 12 CON GIÁP", "steps": [{"at": 2, "rel": "focus", "chi": ["Tuất"], "label": "TUỔI TUẤT"},
       {"at": 3, "rel": "pha", "chi": ["Tuất", "Mùi"], "label": "LỤC PHÁ"}], "until": 3},
 "6": {"type": "elements", "year": {"element": "Thủy", "label": "2027 · THIÊN HÀ THỦY"}, "steps": [
       {"at": 6, "from": "Kim", "to": "Thủy", "kind": "sinh", "card": {"yr": "1970", "sub": "Canh Tuất", "note": "Thoa Xuyến Kim"}, "pill": "KIM SINH THỦY"},
       {"at": 7, "from": "Thủy", "to": "Hỏa", "kind": "khac", "card": {"yr": "1994", "sub": "Giáp Tuất", "note": "Sơn Đầu Hỏa"}, "pill": "THỦY KHẮC HỎA"}], "until": 7},
 "9": {"type": "years", "items": yrs},
 "10": dict(lst("LIST 1"), until=11),
 "14": {"type": "timeline", "title": "VÒNG MƯỜI HAI NĂM", "items": [{"yr": "1982"}, {"yr": "1994"}, {"yr": "2006"}, {"yr": "2018"},
       {"yr": "2027", "label": "Đinh Mùi", "now": True}], "until": 15},
 "16": {"type": "compare", "title": "HÌNH & PHÁ", "left": {"eyebrow": "TAM HÌNH", "title": "Vướng mắc", "body": "Giấy tờ, lời qua tiếng lại", "badge": "HÌNH"},
       "right": {"eyebrow": "LỤC PHÁ", "title": "Gián đoạn", "body": "Việc đang làm dễ dở dang", "badge": "PHÁ", "at": 17}, "until": 17},
 "18": {"type": "stat", "value": 12, "suffix": "", "label": "NĂM MỘT VÒNG CON GIÁP"},
 "20": {"type": "wheel", "steps": [{"at": 20, "rel": "tamhop", "chi": ["Dần", "Ngọ", "Tuất"]},
       {"at": 21, "rel": "luchop", "chi": ["Mão", "Tuất"]}], "until": 21},
 "22": {"type": "years", "items": yrs},
 "23": dict(lst("LIST 2"), until=24),
 "27": {"type": "wheel", "steps": [{"at": 27, "rel": "xung", "chi": ["Thìn", "Tuất"]},
       {"at": 28, "rel": "tamhinh", "chi": ["Sửu", "Tuất", "Mùi"]}], "until": 28},
 "29": {"type": "years", "items": yrs},
 "30": dict(lst("LIST 3"), until=31),
 "39": {"type": "quote", "variant": "page", "source": "Lời người xưa"},
 "40": {"type": "quote", "variant": "kinetic"},
 "41": {"type": "quote", "variant": "glass", "source": "Tóm ý"},
 "44": {"type": "years", "items": [{"yr": "1958", "sub": "Mậu Tuất"}, {"yr": "1982", "sub": "Nhâm Tuất", "mark": True}, {"yr": "2006", "sub": "Bính Tuất"}]},
 "45": dict(lst("DẠ QUANG"), until=46),
 "32": {"type": "elements", "year": {"element": "Thủy", "label": "2027"}, "steps": [
       {"at": 32, "from": "Thủy", "to": "Mộc", "kind": "sinh", "card": {"yr": "1958", "sub": "Mậu Tuất", "note": "Bình Địa Mộc"}, "pill": "THỦY SINH MỘC"},
       {"at": 33, "from": "Thủy", "to": "Thủy", "kind": "hoa", "card": {"yr": "1982", "sub": "Nhâm Tuất", "note": "Đại Hải Thủy"}, "pill": "BÌNH HÒA"}], "until": 33},
}
if len(sys.argv) > 2 and sys.argv[2] == "c":  # chỉ Phase C: chữ theo nghĩa, minh hoạ SVG, thẻ kết shader
    OUT = Path("output/cl_staging/reel_c"); OUT.mkdir(parents=True, exist_ok=True)
    L = ["**Phase C**", "Mọi thứ đều **vô thường**.", "Một khoảnh khắc **tỉnh thức**.", "Tuổi Sửu gặp **xung** Thái Tuế.",
         "Chữ **phá** làm việc dở dang.", "Nước chảy như **dòng sông**.", "Khi lòng **buồn** và nặng trĩu.",
         "Cơn **giận** như ngọn lửa.", "Mọi hành trình **bắt đầu** từ một bước.",
         "Con đường một điểm tụ.", "Mặt trời lên sau núi.", "Hoa sen nở trên mặt nước.", "Trăng khuyết và mây trôi.",
         "Ngôi nhà và la bàn.", "Hẹn gặp lại."]
    n = len(L)
    media = {}
    visuals = {str(i): {"type": "word"} for i in range(2, 10)}
    for i, sc in zip(range(10, 15), ["road", "sunrise", "lotus", "moon", "house"]):
        visuals[str(i)] = {"type": "illus", "scene": sc}
    visuals["15"] = {"type": "endcard", "text": "Đăng ký kênh", "sub": "MỖI NGÀY MỘT BÀI SUY NGẪM"}
if len(sys.argv) > 2 and sys.argv[2] == "g":  # bản đồ vùng + mặt cắt (hf_geo_region; cần dữ liệu ở VIENEU_GEO_DATA)
    OUT = Path("output/cl_staging/reel_g"); OUT.mkdir(parents=True, exist_ok=True)
    L = ["**Bản đồ vùng**", "Toàn vùng Quảng Bình, nền địa hình.", "Ghim rơi đúng lúc được nhắc.",
         "Camera phóng vào Đồng Hới.", "Đường thử vẽ dần, mũi tên thử.", "Vùng ước định nét đứt.",
         "Camera lùi ra.", "Mặt cắt độ cao, tây sang đông.", "Mốc hiện khi được nhắc.", "Hết."]
    n = len(L)
    media = {}
    visuals = {
     "2": {"type": "region", "title": "QUẢNG BÌNH", "bbox": [106.05, 17.20, 107.05, 17.80], "source": "showreel", "certainty": "thử",
           "camera": [{"center": [106.55, 17.50], "zoom": 1}, {"at": 4, "center": [106.62, 17.45], "zoom": 2.4},
                      {"at": 7, "center": [106.55, 17.50], "zoom": 1.1}],
           "pins": [{"name": "Quảng Bình Quan", "lon": 106.62405, "lat": 17.46334, "at": 3},
                    {"name": "Cửa Gianh", "lon": 106.49105, "lat": 17.70121, "at": 3, "side": "left"}],
           "lines": [{"name": "Đường thử", "sub": "không phải vị trí lũy", "kind": "wall", "at": 5, "certainty": "C", "label": [106.585, 17.475],
                      "coords": [[106.6260, 17.4834], [106.6235, 17.4700], [106.6170, 17.4560], [106.6050, 17.4420]]},
                     {"kind": "arrow", "at": 5, "coords": [[106.50, 17.66], [106.55, 17.58], [106.60, 17.50]]}],
           "areas": [{"name": "Vùng thử", "center": [106.58, 17.43], "r_km": 1.5, "at": 6}], "until": 7},
     "8": {"type": "profile", "title": "MẶT CẮT ĐỒNG HỚI", "from": [106.45, 17.463], "to": [106.70, 17.463], "source": "showreel",
           "marks": [{"label": "Quảng Bình Quan", "lon": 106.62405, "lat": 17.463, "at": 9}], "until": 9},
    }
(OUT / "reel.txt").write_text("\n".join(L) + "\n", encoding="utf-8")
segs = [{"start": round(k * STEP, 3), "end": round(k * STEP + STEP - .15, 3), "text": l.replace("**", "")} for k, l in enumerate(L)]
wav = OUT / "reel.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", str(n * STEP), str(wav)], check=True)
wav.with_suffix(".json").write_text(json.dumps({"duration_s": n * STEP, "segments": segs}, ensure_ascii=False), encoding="utf-8")
(OUT / "reel.media.json").write_text(json.dumps(media, ensure_ascii=False), encoding="utf-8")
(OUT / "reel.visuals.json").write_text(json.dumps(visuals, ensure_ascii=False), encoding="utf-8")
cmd = [sys.executable, "hyperframes_bridge.py", "--script", str(OUT / "reel.txt"), "--wav", str(wav), "--series", "fs",
       "--style", "laban_long", "--lane", "long", "--footer", "Kho hiệu ứng — bản xem thử",
       "--bgm", "bgm/comfortable_mystery_4.mp3", "--bgm-gain", "0.5",
       "--media", str(OUT / "reel.media.json"), "--visuals", str(OUT / "reel.visuals.json"),
       "--output", str(OUT / "showreel.mp4"), "--quality", sys.argv[1] if len(sys.argv) > 1 else "looks"]
if not media:
    i = cmd.index("--media"); del cmd[i:i + 2]
print(" ".join(cmd[:4]), "...", flush=True)
sys.exit(subprocess.run(cmd).returncode)
