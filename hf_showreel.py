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
 "32": {"type": "elements", "year": {"element": "Thủy", "label": "2027"}, "steps": [
       {"at": 32, "from": "Thủy", "to": "Mộc", "kind": "sinh", "card": {"yr": "1958", "sub": "Mậu Tuất", "note": "Bình Địa Mộc"}, "pill": "THỦY SINH MỘC"},
       {"at": 33, "from": "Thủy", "to": "Thủy", "kind": "hoa", "card": {"yr": "1982", "sub": "Nhâm Tuất", "note": "Đại Hải Thủy"}, "pill": "BÌNH HÒA"}], "until": 33},
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
print(" ".join(cmd[:4]), "...", flush=True)
sys.exit(subprocess.run(cmd).returncode)
