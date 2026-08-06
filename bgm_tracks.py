"""Cấu hình BGM theo topic cho Short -- xem bgm/LICENSE.txt cho đầy đủ điều
khoản CC BY 4.0 + ghi nguồn gốc từng track.

Tách riêng khỏi mix_bgm.py (Long, 1 track cố định "Meditation Impromptu 01")
để không đụng vào pipeline Long đã chạy ổn -- Short cần NHIỀU track khác
nhau theo topic (Phật giáo dùng track thiền định, Phong Thuỷ dùng track
khác tông hơn) nên cần 1 lớp tra cứu theo topic riêng.

BUG THẬT phát hiện qua rà soát trước khi wire BGM cho Short (xem phiên làm
việc): mix_bgm.py::ATTRIBUTION_TEXT (ghi nguồn bắt buộc theo giấy phép CC
BY 4.0) chỉ được PRINT ra màn hình như lời nhắc ("NHỚ thêm vào mô tả
video") khi chạy mix_bgm.py CLI trực tiếp -- KHÔNG có chỗ nào tự động chèn
vào mô tả video thật (Long dựa hoàn toàn vào con người tự nhớ chép tay,
rủi ro vi phạm giấy phép nếu quên). Với Short, short_batch_runner.py sẽ tự
động nối `attribution` vào description SAU KHI SEO đã qua review (không để
model tự viết lại câu ghi nguồn -- rủi ro model diễn giải sai/thiếu, chỉ
nối chuỗi cố định để đảm bảo ĐÚNG NGUYÊN VĂN yêu cầu của giấy phép).

MỖI TOPIC GIỜ CÓ NHIỀU TRACK (audit 9 điểm mục #4 -- trước chỉ 1 track/
topic, dùng lặp lại mọi video). pick_bgm_for_topic() xoay vòng qua
rotation_state.pick_and_commit_next() (cùng cơ chế atomic đã dùng cho biến
thể Bát Quái/Ngũ Hành -- xem domain_creative_profiles.py).

CẢNH BÁO QUAN TRỌNG cho caller (bug THIẾU CHÚT NỮA mắc phải khi wire, xem
phiên làm việc): pick_bgm_for_topic() làm ĐỔI STATE (rotate) mỗi lần gọi --
PHẢI gọi ĐÚNG 1 LẦN cho mỗi content item (lúc render video, khi track THẬT
SỰ được mix vào file), rồi LƯU kết quả (`entry["bgm"]`) vào registry để các
bước sau (SEO/upload, có thể chạy ở lần script khác nếu resume) đọc lại
CHÍNH kết quả đã lưu -- KHÔNG được gọi lại hàm này để "tra lại" attribution,
vì lần gọi sau sẽ rotate sang track KHÁC, ghi sai nguồn so với track thật
đã mix vào video (vi phạm giấy phép CC BY 4.0 -- ghi nguồn phải đúng track
thật, không phải track ngẫu nhiên nào đó).

G4 (Audio Generation remediation, finding E2): mỗi track dưới đây giờ có
thêm `integrated_lufs`/`true_peak_dbfs` -- đo THẬT bằng
``ffmpeg -af ebur128=peak=true`` (EBU R128, không đoán mù) -- và `gain_db`
tính từ 2 số đó, xem :func:`_compute_gain_db`. TRƯỚC fix: mọi track (7
track, chênh nhau tới ~8 LU độ to thật) đều bị áp CÙNG 1 hệ số 10%
(``DEFAULT_BGM_VOLUME_PCT`` trong ``video_tool_clone/core/pipeline/bgm.py``)
KHÔNG phân biệt -- track vốn to hơn ra video vẫn to hơn, không nhất quán
giữa các video Short (đã đo lại xác nhận đúng phát hiện của audit/Codex).
`gain_db` giờ được tính RIÊNG cho từng track để đưa VỀ CÙNG 1 mức "nền"
mục tiêu, có giới hạn true-peak (dựa trên phép đo decode hiện tại, xem
lưu ý ở SAFE_TRUE_PEAK_CEILING_DBTP) để gain không vượt ngưỡng an toàn dù
target đó đòi hỏi gain dương. Track nào cần khác biệt CÓ CHỦ Ý (không
phải do đo lệch) chỉ cần set thẳng `gain_db` khác trong entry của nó --
_compute_gain_db() chỉ là GIÁ TRỊ MẶC ĐỊNH áp dụng khi không có lý do
khác, không phải quy tắc cứng ép mọi track về múc y hệt nhau."""
from pathlib import Path

import rotation_state

BGM_DIR = Path(__file__).parent / "bgm"
BGM_ROTATION_STATE_PATH = Path(__file__).parent / "chunks_cache" / "bgm_rotation_state.json"

# G4: mục tiêu loudness "nền" (Integrated Loudness, LUFS, đo bằng
# ffmpeg ebur128) cho MỌI track BGM Short sau khi áp gain -- chọn để NHẤT
# QUÁN với mức Long đã dùng thật (không bịa ra 1 triết lý thứ 3):
# "meditation_impromptu_01.mp3" đo được -23.3 LUFS gốc, mix_bgm.py (Long)
# đã cộng thêm -10dB (hiệu chỉnh thủ công dựa trên đo mean_volume RIÊNG,
# xem docstring mix_bgm.py) -> hiệu ứng thực tế ~-33.3 LUFS. Dùng -33.0
# LUFS cho Short: tính theo công thức dưới đây, CHÍNH track đó tự ra gain
# -9.7dB -- gần khớp -10dB Long đã chọn. LƯU Ý (Codex review round 1,
# finding Low #3): đây là kiểm tra TÍNH NHẤT QUÁN nội bộ (cùng 1 track,
# cùng công thức), KHÔNG phải validate độc lập bằng phương pháp khác --
# Long's -10dB tự nó được chọn thủ công qua volumedetect mean_volume +
# khoảng cách với giọng đọc, không phải qua đo LUFS. Xác nhận cân bằng
# giọng đọc/nhạc nền RÕ RÀNG (nghe thử/đo thật) trên video hoàn chỉnh vẫn
# nên làm trước khi coi mục tiêu này là ĐÃ TỐI ƯU, không chỉ nhất quán.
TARGET_BGM_INTEGRATED_LUFS = -33.0

# G4: trần True Peak an toàn (dBTP) -- gain cho 1 track không được vượt
# ngưỡng này dựa trên true_peak_dbfs ĐÃ ĐO (ffmpeg ebur128, không phải
# sample-peak thô) dù target loudness phía trên đòi hỏi gain dương lớn
# hơn. -1 dBTP là margin an toàn phổ biến (EBU R128/ITU-R BS.1770). LƯU Ý
# (Codex review round 1, finding Medium #2): đây là bảo vệ dựa trên phép
# đo decode hiện tại, KHÔNG phải đảm bảo tuyệt đối cho MỌI khâu xử lý sau
# đó (resample 48kHz, encode AAC, re-encode phía YouTube... có thể tạo
# true-peak thực tế hơi khác) -- với margin -1dBTP và mọi track hiện tại
# đều nằm sâu dưới ngưỡng (peak sau gain: -11 đến -18 dBTP), rủi ro thực
# tế thấp, nhưng 1 track TƯƠNG LAI rơi sát đúng ngưỡng vẫn nên xem xét
# thêm margin.
SAFE_TRUE_PEAK_CEILING_DBTP = -1.0


def _compute_gain_db(integrated_lufs: float, true_peak_dbfs: float) -> float:
    """Gain (dB) để đưa track về TARGET_BGM_INTEGRATED_LUFS, GIỚI HẠN bởi
    SAFE_TRUE_PEAK_CEILING_DBTP -- peak SUY RA TỪ true_peak_dbfs đầu vào
    (phép đo decode hiện tại) sẽ không vượt trần an toàn dù target loudness
    đòi hỏi gain lớn hơn (bảo vệ chống clip; xem lưu ý ở
    SAFE_TRUE_PEAK_CEILING_DBTP về giới hạn của phép đo này)."""
    gain_for_target = TARGET_BGM_INTEGRATED_LUFS - integrated_lufs
    gain_peak_ceiling = SAFE_TRUE_PEAK_CEILING_DBTP - true_peak_dbfs
    return round(min(gain_for_target, gain_peak_ceiling), 2)


def gain_db_to_volume_pct(gain_db: float) -> float:
    """Quy đổi gain (dB) -> `volume_pct` (%) mà
    ``video_tool_clone/core/pipeline/bgm.py::BGMConfig.volume_pct`` cần
    (hệ số nhân biên độ tuyến tính * 100, KHÔNG phải dB) -- dB -> hệ số
    biên độ tuyến tính là ``10**(dB/20)`` (định nghĩa dB biên độ chuẩn)."""
    return round((10 ** (gain_db / 20)) * 100, 4)


# G4: integrated_lufs/true_peak_dbfs đo THẬT bằng
# `ffmpeg -i <track> -af ebur128=peak=true -f null -` (EBU R128) cho từng
# file trong bgm/ tại thời điểm remediation -- không phải số suy đoán.
# gain_db = _compute_gain_db(integrated_lufs, true_peak_dbfs) áp dụng SAU
# khi đo (không tính lại lúc runtime -- tránh phụ thuộc ffmpeg mỗi lần
# render, và cho phép override thủ công gain_db riêng nếu 1 track cần khác
# biệt CÓ CHỦ Ý sau này).
BGM_BY_TOPIC = {
    "Phật giáo": [
        {
            "path": BGM_DIR / "meditation_impromptu_01.mp3",
            "attribution": (
                'Nhạc nền: "Meditation Impromptu 01" by Kevin MacLeod (incompetech.com), '
                "licensed under CC BY 4.0 (http://creativecommons.org/licenses/by/4.0/)"
            ),
            "integrated_lufs": -23.3,
            "true_peak_dbfs": -2.1,
            "gain_db": -9.7,
        },
        {
            "path": BGM_DIR / "meditation_impromptu_02.mp3",
            "attribution": (
                'Nhạc nền: "Meditation Impromptu 02" by Kevin MacLeod (incompetech.com), '
                "licensed under CC BY 4.0 (http://creativecommons.org/licenses/by/4.0/)"
            ),
            "integrated_lufs": -23.0,
            "true_peak_dbfs": -2.4,
            "gain_db": -10.0,
        },
        {
            "path": BGM_DIR / "meditation_impromptu_03.mp3",
            "attribution": (
                'Nhạc nền: "Meditation Impromptu 03" by Kevin MacLeod (incompetech.com), '
                "licensed under CC BY 4.0 (http://creativecommons.org/licenses/by/4.0/)"
            ),
            "integrated_lufs": -22.5,
            "true_peak_dbfs": -1.0,
            "gain_db": -10.5,
        },
    ],
    "Phong Thủy": [
        {
            "path": BGM_DIR / "asian_drums.mp3",
            "attribution": (
                'Nhạc nền: "Asian Drums" by Kevin MacLeod (incompetech.com), '
                "licensed under CC BY 4.0 (http://creativecommons.org/licenses/by/4.0/)"
            ),
            "integrated_lufs": -22.2,
            "true_peak_dbfs": -0.3,
            "gain_db": -10.8,
        },
        {
            "path": BGM_DIR / "comfortable_mystery_4.mp3",
            "attribution": (
                'Nhạc nền: "Comfortable Mystery 4" by Kevin MacLeod (incompetech.com), '
                "licensed under CC BY 4.0 (http://creativecommons.org/licenses/by/4.0/)"
            ),
            "integrated_lufs": -15.3,
            "true_peak_dbfs": -0.1,
            "gain_db": -17.7,
        },
    ],
    # Hình Sự -- audit 9 điểm mục #4: trước đây KHÔNG có track nào (đúng
    # thiết kế, tránh áp sai tông cho nội dung tội phạm thật khi chưa có
    # lựa chọn được duyệt). Đã chọn CÓ CHỦ ĐÍCH 2 track tên gọi/thể loại
    # hướng trung lập/suy ngẫm (KHÔNG kịch tính/giật gân) theo yêu cầu
    # người dùng -- LƯU Ý: chọn dựa trên tra cứu tên/thể loại, CHƯA nghe
    # trực tiếp, người dùng cần tự nghe thử trên video thật đầu tiên.
    "Hình Sự": [
        {
            "path": BGM_DIR / "deliberate_thought.mp3",
            "attribution": (
                'Nhạc nền: "Deliberate Thought" by Kevin MacLeod (incompetech.com), '
                "licensed under CC BY 4.0 (http://creativecommons.org/licenses/by/4.0/)"
            ),
            "integrated_lufs": -17.7,
            "true_peak_dbfs": -2.1,
            "gain_db": -15.3,
        },
        {
            "path": BGM_DIR / "thinking_music.mp3",
            "attribution": (
                'Nhạc nền: "Thinking Music" by Kevin MacLeod (incompetech.com), '
                "licensed under CC BY 4.0 (http://creativecommons.org/licenses/by/4.0/)"
            ),
            "integrated_lufs": -20.5,
            "true_peak_dbfs": -0.1,
            "gain_db": -12.5,
        },
    ],
}

# Codex review điểm #4 (bug thật): CL ("Hình Sự") có 0 track TRƯỚC lần sửa
# này -- entry Short CL cũ (registry đã lưu trước khi có track) KHÔNG hề
# có BGM mix vào video. Nếu step 5 (short_batch_runner.py) fallback về
# bgm_for_topic(topic) một cách MÙ QUÁNG cho MỌI topic thiếu entry["bgm"],
# entry CL cũ sẽ bị gán NHẦM attribution "Deliberate Thought" dù video đó
# THẬT SỰ không có track nào -- sai nguồn, sai cả thực tế. CHỈ những topic
# ĐÃ CÓ SẴN đúng 1 track TRƯỚC migration này (BUD/FS) mới an toàn dùng
# bgm_for_topic() làm fallback cho entry cũ thiếu entry["bgm"] (vì track
# đầu tiên trong BGM_BY_TOPIC hiện tại CHÍNH LÀ track duy nhất từng tồn
# tại lúc đó). Topic mới/chưa từng có track (CL) KHÔNG được nằm trong tập
# này -- entry cũ của CL thiếu entry["bgm"] phải được hiểu là "không có
# BGM", không suy luận ngược.
LEGACY_SINGLE_TRACK_TOPICS = {"Phật giáo", "Phong Thủy"}


def bgm_for_topic(topic: str) -> dict | None:
    """LEGACY -- trả về track ĐẦU TIÊN cố định (KHÔNG rotate, không đổi
    state) cho topic. Giữ lại cho caller nào chỉ cần "có BGM hay không"
    (vd kiểm tra topic có cấu hình) mà không quan tâm track cụ thể nào.
    KHÔNG dùng hàm này để lấy attribution thật sự sẽ mix vào video --
    dùng pick_bgm_for_topic() (xem cảnh báo ở docstring module)."""
    tracks = BGM_BY_TOPIC.get(topic)
    return tracks[0] if tracks else None


def pick_bgm_for_topic(topic: str) -> dict | None:
    """Chọn 1 track XOAY VÒNG cho topic (rotation_state.pick_and_commit_next,
    atomic, có nhận biết lịch sử gần đây) -- None nếu topic chưa cấu hình
    BGM. GỌI ĐÚNG 1 LẦN/content item, LƯU kết quả vào registry ngay (xem
    cảnh báo docstring module)."""
    tracks = BGM_BY_TOPIC.get(topic)
    if not tracks:
        return None
    if len(tracks) == 1:
        return tracks[0]
    paths = [str(t["path"]) for t in tracks]
    chosen_path = rotation_state.pick_and_commit_next(BGM_ROTATION_STATE_PATH, paths, f"last_bgm_path::{topic}")
    return next(t for t in tracks if str(t["path"]) == chosen_path)


def resolve_gain_db_for_path(path: str, topic: str) -> float | None:
    """G4 (Codex review finding High #1): tra ngược `gain_db` cho 1 `path`
    ĐÃ BIẾT -- dùng để backfill entry["bgm"] cũ đã lưu vào registry TRƯỚC
    KHI G4 thêm gain_db vào catalog (registry thật đã kiểm tra: 28 entry
    Phật giáo/Phong Thuỷ có path+attribution nhưng THIẾU gain_db). Không
    backfill sẽ khiến các entry cũ đó âm thầm rơi về default 10% cũ mỗi
    lần resume -- tái hiện đúng bug E2 dù catalog đã sửa.

    FAIL-CLOSED: so khớp CHÍNH XÁC path với ĐÚNG 1 track trong
    BGM_BY_TOPIC[topic] -- trả None (KHÔNG đoán) nếu topic chưa cấu hình
    hoặc path không khớp đúng 1 track nào. Caller phải tự xử lý None (giữ
    hành vi cũ, không áp gain sai track nào)."""
    tracks = BGM_BY_TOPIC.get(topic)
    if not tracks:
        return None
    matches = [t for t in tracks if str(t["path"]) == str(path)]
    if len(matches) != 1:
        return None
    return matches[0]["gain_db"]
