"""
Pre-upload duplicate-publish guard cho Long-form (channel-agnostic -- BUD/
FS/CL đều gọi qua long_batch_runner.py, KHÔNG có logic riêng cho BUD).

BUG THẬT phát hiện 2026-08-11 (điều tra trực tiếp qua YouTube Data API thật,
so khớp video_id + contentDetails.duration): kênh BUD (Phật giáo) có 3 tập
bị đăng TRÙNG thật trên YouTube:
  - EP005: 3 lần -- DmlFetbmhAw (24/07), dxqNBmz2trw (04/08), 2Tfwh3B-1SU
    (06/08, bản registry hiện tại).
  - EP006: 2 lần -- W0lATzhAlWc (31/07), Ag9Ei-Yfhw0 (11/08, đã bị người
    dùng tự xoá trực tiếp trên YouTube).
  - EP007: 2 lần -- TTsGD4f_bpM (07/08), M_7WbvpNdHI (10/08, bản registry
    hiện tại).

Nguyên nhân gốc: 1 số bản render hoàn chỉnh (giai đoạn "test pipeline"
tháng 7/2026) được upload THỦ CÔNG qua script ad-hoc, kết quả chỉ lưu trong
output/video_test/*_youtube_upload_metadata.json -- KHÔNG BAO GIỜ được ghi
vào output/long/<topic>/registry.json, nguồn sự thật DUY NHẤT mà
long_batch_runner.py dùng để quyết định "tập này đã upload chưa" (xem
long_batch_runner.py TERMINAL_STATUSES). Khi bản render "chính thức" (theo
registry) của CÙNG tập bị kẹt/lỗi rồi được retry sau đó, pipeline không có
cách nào biết 1 video giống hệt về nội dung đã tồn tại thật trên kênh --
render + upload TRÙNG. Registry.json chỉ phản ánh những gì CHÍNH quy trình
tự động đã làm, không phản ánh trạng thái THẬT của kênh YouTube.

Sửa tận gốc mô hình tin cậy: KHÔNG tin registry.json vô điều kiện nữa cho
câu hỏi "đã đăng chưa" -- đối chiếu THẬT với kênh YouTube ngay TRƯỚC bước
upload (cùng tinh thần fetch_scheduled_counts_per_day() ở
batch_orchestration.py, đối chiếu thật thay vì chỉ tin state cục bộ).

Vì sao KHÔNG dùng title để khớp: xác nhận thật qua chính 3 vụ trên -- EP005's
3 lần upload dùng 3 tiêu đề SEO KHÁC NHAU (content_seo.py sinh 5 lựa chọn mỗi
lần chạy, _pick_title() trong long_batch_runner.py không đảm bảo chọn lại
đúng cùng 1 câu qua các lần chạy khác nhau), EP007 dùng 2 tiêu đề khác nhau
-- so khớp theo title sẽ BỎ LỌT cả 2 vụ đó. Duration (giây, từ
contentDetails.duration) bắt được cả 3 vụ thật, vì video sinh ra từ CÙNG 1
audio narration gốc sẽ có thời lượng gần như giống hệt (chỉ lệch vài giây do
encoding/khung hình làm tròn) dù render lại nhiều lần với tiêu đề khác nhau.

Rủi ro của CHỈ dùng 1 tín hiệu duration: 2 video KHÔNG liên quan có thể
trùng thời lượng do NGẪU NHIÊN (video dài hàng chục phút, sai số vài giây --
xác suất trùng không phải 0, nhất là 1 kênh đăng đều đặn nhiều tập cùng độ
dài mục tiêu tương tự). Module này dùng THÊM 1 phép đo ĐỘC LẬP: thời lượng
audio NGUỒN của chính tập đang xử lý (file .wav TTS gốc, tách biệt hoàn
toàn khỏi file .mp4 đã render) -- đo trực tiếp bằng ffprobe NGAY TRƯỚC khi
upload, không tin bất kỳ giá trị cache/registry nào. Video được dựng bằng
cách đồng bộ khung hình theo ĐÚNG audio này (xem audio_tool_render.py,
policy content_sync) nên thời lượng video luôn RẤT GẦN thời lượng audio gốc
(sai số nhỏ do fade/silence biên, không phải 1 hằng số lớn như intro/outro
bumper -- dự án này không dùng bumper). Nếu CẢ HAI phép đo (video render VÀ
audio nguồn, 2 file khác nhau, đo độc lập) cùng khớp 1 video đã có sẵn trên
kênh, khả năng đó là trùng NGẪU NHIÊN giảm mạnh so với chỉ 1 tín hiệu --
video không liên quan mà vừa khéo trùng CẢ 2 phép đo là cực khó xảy ra tình
cờ. Khi thiếu audio nguồn (wav_path không có/không đọc được), vẫn FAIL
CLOSED theo tín hiệu duration đơn (đã đủ bắt cả 3 vụ thật ở trên) nhưng ghi
rõ "secondary_signal_available": False để người xem biết mức độ tin cậy.

Fail-closed: nếu tìm thấy khả năng trùng, KHÔNG upload -- caller
(long_batch_runner.py) phải tự đánh dấu registry entry là
"possible_duplicate_detected" (không lẫn với "failed"/"needs_review") kèm
đủ thông tin video nghi trùng, để người thật xem xét (xem
record_existing_upload.py cho hướng backfill/giải quyết thủ công). Module
này KHÔNG tự quyết "đây có thực sự là trùng hay không" -- không lục lại
registry.json nghi trùng nữa nếu API lỗi vì chỉ điều đó cũng chưa đủ để tin
tưởng.

RACE CONDITION thật (Codex CLI adversarial review round 1, finding HIGH):
kiểm tra trùng (đọc catalog kênh) rồi upload là 2 bước TÁCH RỜI theo thời
gian (time-of-check/time-of-use) -- nếu 2 tiến trình (vd 1 lần launchd theo
lịch + 1 lần chạy tay chồng lấn, đúng kịch bản đã gây ra sự cố gốc) cùng
đọc catalog kênh gần như đồng thời, CẢ HAI đều thấy "chưa có bản nào khớp"
(vì video của tiến trình kia CHƯA xuất hiện trên kênh lúc đó), cả hai đều
tiếp tục upload -- tạo bản TRÙNG THẬT giống hệt sự cố gốc, dù mỗi tiến
trình RIÊNG LẺ đã kiểm tra đúng. channel_upload_lock() dưới đây khoá liên-
tiến-trình theo TỪNG KÊNH (dựa vào chính đường dẫn credentials_path -- mỗi
kênh 1 file credentials riêng) -- caller (long_batch_runner.py) PHẢI giữ
khoá này xuyên suốt từ lúc gọi check_for_possible_duplicate() tới khi
upload xong VÀ đã lưu video_id vào registry, không chỉ trong lúc gọi hàm
kiểm tra. GIỚI HẠN THẬT (không tự nhận vơ là giải quyết triệt để): khoá
này chỉ có hiệu lực với các entrypoint THẬT SỰ import + gọi hàm này
(long_batch_runner.py) -- 1 script ad-hoc thủ công (đúng kịch bản gây ra
sự cố gốc) không biết gì về module này vẫn có thể bỏ qua khoá hoàn toàn;
không có cách nào ép buộc 1 tiến trình hoàn toàn bên ngoài codebase phải tự
khoá. Đây là lý do record_existing_upload.py (chiều còn lại của lỗ hổng)
quan trọng không kém: khuyến khích ghi NGAY vào registry ngay sau bất kỳ
upload thủ công nào, thu hẹp cửa sổ mà 1 upload "vô hình" với khoá này có
thể tồn tại.
"""
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from registry_lock import FileLock
from youtube_catalog import (
    CHANNELS_URL,
    _get,
    get_videos_details,
    list_playlist_video_ids,
)
# Tái dùng NGUYÊN parser ISO8601 duration đã có + đã chạy thật ở
# youtube_sync.py (contentDetails.duration, vd "PT27M3S") -- không viết lại
# 1 bản khác có thể lệch hành vi ở edge case (vd thiếu "PT", giá trị rỗng).
from youtube_sync import _parse_iso8601_duration

# Sai số cho phép giữa duration LOCAL (video vừa render xong, đo bằng
# ffprobe NGAY TRƯỚC upload) và duration trên YouTube của 1 video đã có sẵn
# trên kênh -- 2 lần render của CÙNG audio gốc lệch nhau tối đa vài giây do
# làm tròn khung hình/encoding, KHÔNG lệch hàng chục giây. 2.0s đủ chặt để
# không khớp nhầm 2 tập nội dung khác nhau (thường lệch hàng chục giây tới
# vài phút với nội dung Long ~15-30 phút) nhưng đủ rộng để không bỏ lọt do
# làm tròn.
DURATION_TOLERANCE_SEC = 2.0

# Sai số RỘNG HƠN cho tín hiệu phụ (audio nguồn thô so với video ĐÃ RENDER)
# -- audio TTS gốc không có fade-out/khoảng lặng biên mà bước render/mix_bgm
# có thể thêm (xem mix_bgm.py DEFAULT_FADE_SEC=3.0, atrim theo đúng duration
# video nên KHÔNG kéo dài thêm -- chỉ fade trong biên có sẵn). Không dùng
# hằng số bumper lớn vì dự án này không chèn intro/outro cố định (xác nhận
# qua audio_tool_render.py -- video đồng bộ trực tiếp theo timeline audio).
AUDIO_DURATION_TOLERANCE_SEC = 6.0


class DuplicateCheckError(RuntimeError):
    pass


@dataclass
class ChannelVideo:
    video_id: str
    title: str
    duration_seconds: float | None
    published_at: str | None


@dataclass
class PossibleDuplicate:
    """Kết quả 1 khả năng trùng -- serializable trực tiếp vào registry entry
    qua asdict()/vars() (chỉ kiểu dữ liệu JSON-an toàn: str/float/bool/None)."""
    suspected_video_id: str
    suspected_title: str
    suspected_published_at: str | None
    suspected_duration_seconds: float
    local_video_duration_seconds: float
    duration_diff_seconds: float
    secondary_signal_available: bool
    secondary_signal_matched: bool
    local_audio_duration_seconds: float | None = None
    checked_at: str = ""

    def to_dict(self) -> dict:
        return {
            "suspected_video_id": self.suspected_video_id,
            "suspected_title": self.suspected_title,
            "suspected_published_at": self.suspected_published_at,
            "suspected_duration_seconds": self.suspected_duration_seconds,
            "local_video_duration_seconds": self.local_video_duration_seconds,
            "local_audio_duration_seconds": self.local_audio_duration_seconds,
            "duration_diff_seconds": self.duration_diff_seconds,
            "secondary_signal_available": self.secondary_signal_available,
            "secondary_signal_matched": self.secondary_signal_matched,
            "checked_at": self.checked_at,
        }


def probe_duration_seconds(path: str | Path, ffprobe_path: str) -> float:
    """Đo thời lượng THẬT của 1 file media cục bộ (audio hoặc video) bằng
    ffprobe -- cùng lệnh/cách parse đã dùng thật ở mix_bgm.py's
    _probe_duration() (không viết lại 1 cách khác có thể lệch hành vi)."""
    path = Path(path)
    if not path.exists():
        raise DuplicateCheckError(f"Không tìm thấy file để đo thời lượng: {path}")
    result = subprocess.run(
        [ffprobe_path, "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise DuplicateCheckError(f"ffprobe lỗi khi đọc thời lượng {path}: {result.stderr[-500:]}")
    return float(json.loads(result.stdout)["format"]["duration"])


def _get_uploads_playlist_id(credentials_path: str | Path) -> str:
    """Cùng lệnh gọi channels.list?part=contentDetails&mine=true đã dùng
    thật ở batch_orchestration.py's fetch_scheduled_counts_per_day() --
    tái dùng nguyên _get()/CHANNELS_URL từ youtube_catalog.py thay vì tự
    build request riêng."""
    ch_data = _get(credentials_path, CHANNELS_URL, {"part": "contentDetails", "mine": "true"})
    items = ch_data.get("items", [])
    if not items:
        raise DuplicateCheckError("channels.list mine=true không trả về kênh nào -- credentials có thể sai/hết quyền.")
    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]


def fetch_channel_video_catalog(credentials_path: str | Path) -> list[ChannelVideo]:
    """Liệt kê TOÀN BỘ video hiện có trên kênh (đúng credentials đang dùng)
    kèm duration thật -- tái dùng NGUYÊN pagination đã chạy thật của
    youtube_catalog.py (list_playlist_video_ids() tự phân trang hết, không
    giới hạn 200 như fetch_scheduled_counts_per_day() -- ở đây cần TOÀN BỘ
    lịch sử kênh vì bản trùng có thể đã đăng từ nhiều tuần trước, không chỉ
    trong vài ngày tới) + get_videos_details() (đã tự chia batch 50
    id/lần theo đúng giới hạn videos.list)."""
    uploads_playlist_id = _get_uploads_playlist_id(credentials_path)
    video_ids = list_playlist_video_ids(credentials_path, uploads_playlist_id)
    if not video_ids:
        return []
    details = get_videos_details(credentials_path, video_ids)
    catalog = []
    for item in details:
        duration_raw = item.get("duration")
        duration_seconds = _parse_iso8601_duration(duration_raw) if duration_raw else None
        catalog.append(ChannelVideo(
            video_id=item["id"],
            title=item.get("title") or "",
            duration_seconds=float(duration_seconds) if duration_seconds is not None else None,
            published_at=item.get("published_at"),
        ))
    return catalog


def _duration_matches(
    local_video_duration: float,
    catalog: list[ChannelVideo],
    exclude_video_id: str | None,
    tolerance_sec: float,
) -> list[ChannelVideo]:
    """Trả về TẤT CẢ video trong catalog khớp duration (trong biên độ
    tolerance_sec), sắp xếp GẦN NHẤT trước -- KHÔNG chỉ 1 video "tốt nhất"
    (xem check_for_possible_duplicate() -- khi có audio nguồn để đối chiếu,
    cần xét MỌI ứng viên khớp duration để tìm ra đúng ứng viên CŨNG khớp
    audio, không chỉ kiểm audio với riêng ứng viên gần nhất theo duration
    video -- Codex CLI adversarial review round 1 chỉ ra: 2 tập nội dung
    khác nhau nhưng vô tình cùng độ dài có thể khiến ứng viên gần nhất theo
    duration KHÔNG PHẢI là ứng viên thật sự khớp audio). exclude_video_id:
    bỏ qua 1 video_id cụ thể (vd chính entry này nếu đã có video_id từ 1
    lần chạy trước đó -- phòng hờ, tránh tự báo trùng với chính mình)."""
    matches = []
    for video in catalog:
        if video.duration_seconds is None:
            continue
        if exclude_video_id and video.video_id == exclude_video_id:
            continue
        diff = abs(video.duration_seconds - local_video_duration)
        if diff <= tolerance_sec:
            matches.append((diff, video))
    matches.sort(key=lambda pair: pair[0])
    return [video for _diff, video in matches]


def check_for_possible_duplicate(
    video_path: str | Path,
    credentials_path: str | Path,
    ffprobe_path: str,
    audio_path: str | Path | None = None,
    exclude_video_id: str | None = None,
    duration_tolerance_sec: float = DURATION_TOLERANCE_SEC,
    audio_duration_tolerance_sec: float = AUDIO_DURATION_TOLERANCE_SEC,
) -> PossibleDuplicate | None:
    """Kiểm tra THẬT trước khi upload -- gọi ngay trước upload_video() ở
    long_batch_runner.py. Trả về None nếu KHÔNG có khả năng trùng, hoặc
    PossibleDuplicate nếu có -- caller PHẢI fail-closed (không upload) khi
    kết quả khác None.

    QUAN TRỌNG (Codex CLI adversarial review round 1, finding HIGH -- bản vá
    trước đây có bug thật: tín hiệu phụ audio được TÍNH nhưng KHÔNG BAO GIỜ
    ảnh hưởng tới quyết định, luôn trả về PossibleDuplicate ngay khi duration
    khớp bất kể audio khớp hay không -- biến audio thành thông tin chẩn đoán
    suông, trái với chính docstring module "giảm khả năng báo nhầm"). Chính
    sách ĐÚNG (đã sửa): khi CÓ audio nguồn để đối chiếu, chỉ coi là khả năng
    trùng nếu tìm được ÍT NHẤT 1 ứng viên khớp CẢ HAI (duration video VÀ
    duration audio) -- 1 ứng viên chỉ khớp duration video nhưng audio nguồn
    rõ ràng KHÔNG khớp coi là trùng NGẪU NHIÊN, không flag (đúng mục tiêu
    thiết kế gốc). Khi KHÔNG CÓ audio nguồn để đối chiếu (wav_path thiếu/
    không đọc được), vẫn fail-closed theo duration đơn (đã đủ bắt cả 3 vụ
    thật EP005/006/007) vì không có cách nào khác để corroborate.

    KHÔNG tự bắt lỗi mạng/API ở đây (YouTubeCatalogError/DuplicateCheckError
    bay thẳng ra ngoài) -- caller (process_one_episode()'s except Exception
    trong main() vòng lặp) đã có cơ chế retry/error_count/MAX_RETRIES sẵn
    cho MỌI lỗi bước khác trong pipeline; không cần (và không nên) tự
    quyết "lỗi kiểm tra trùng thì cứ cho upload" ở đây -- im lặng bỏ qua
    exception rồi upload tiếp mới là lỗ hổng fail-OPEN thật sự."""
    local_video_duration = probe_duration_seconds(video_path, ffprobe_path)
    local_audio_duration = None
    if audio_path is not None and Path(audio_path).exists():
        local_audio_duration = probe_duration_seconds(audio_path, ffprobe_path)

    catalog = fetch_channel_video_catalog(credentials_path)
    candidates = _duration_matches(local_video_duration, catalog, exclude_video_id, duration_tolerance_sec)
    if not candidates:
        return None

    secondary_available = local_audio_duration is not None
    if not secondary_available:
        # Không có audio nguồn để đối chiếu -- fail-closed theo duration
        # đơn, lấy ứng viên GẦN NHẤT (đã sắp xếp sẵn trong _duration_matches()).
        match = candidates[0]
        return PossibleDuplicate(
            suspected_video_id=match.video_id,
            suspected_title=match.title,
            suspected_published_at=match.published_at,
            suspected_duration_seconds=match.duration_seconds,
            local_video_duration_seconds=local_video_duration,
            local_audio_duration_seconds=None,
            duration_diff_seconds=abs(match.duration_seconds - local_video_duration),
            secondary_signal_available=False,
            secondary_signal_matched=False,
            checked_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

    # Có audio nguồn -- tìm ứng viên GẦN NHẤT (theo duration video) trong số
    # các ứng viên MÀ audio nguồn CŨNG khớp. Nếu KHÔNG ứng viên nào trong
    # candidates (đã khớp duration video) cũng khớp audio, coi đây là trùng
    # NGẪU NHIÊN về duration video, KHÔNG flag.
    corroborated = [
        v for v in candidates
        if abs(v.duration_seconds - local_audio_duration) <= audio_duration_tolerance_sec
    ]
    if not corroborated:
        return None
    match = corroborated[0]
    return PossibleDuplicate(
        suspected_video_id=match.video_id,
        suspected_title=match.title,
        suspected_published_at=match.published_at,
        suspected_duration_seconds=match.duration_seconds,
        local_video_duration_seconds=local_video_duration,
        local_audio_duration_seconds=local_audio_duration,
        duration_diff_seconds=abs(match.duration_seconds - local_video_duration),
        secondary_signal_available=True,
        secondary_signal_matched=True,
        checked_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


def channel_upload_lock(credentials_path: str | Path) -> FileLock:
    """Khoá liên-tiến-trình theo TỪNG KÊNH -- xem docstring module (mục
    RACE CONDITION) cho lý do đầy đủ. Dùng NGUYÊN FileLock đã kiểm chứng
    thật ở registry_lock.py (fcntl.flock, chặn tiến trình khác cho tới khi
    giải phóng) thay vì viết khoá riêng -- khác cách dùng GỐC của FileLock
    (vốn cho giao dịch JSON rất ngắn), ở đây CỐ Ý giữ khoá lâu hơn (xuyên
    suốt bước upload mạng, có thể vài phút) vì fcntl.flock hỗ trợ giữ lâu
    bình thường, không có giả định nào trong bản thân class đó giới hạn
    thời lượng giữ khoá.

    Khoá theo file credentials (mỗi kênh 1 file .youtube_channels/<kênh>.json
    riêng) -- 2 kênh KHÁC nhau (vd FS và CL) vẫn upload song song bình
    thường, chỉ tuần tự hoá đúng trong CÙNG 1 kênh (đúng khuyến nghị chính
    YouTube: không nên nhiều resumable session song song trên cùng 1 kênh,
    xem youtube_upload.py's bulk_upload() docstring). File credentials
    KHÔNG bao giờ bị chính codebase này ghi lại (get_valid_access_token()
    ở youtube_auth.py luôn refresh mới, không cache access_token ngược vào
    file) nên dùng thẳng làm gốc đường dẫn khoá là an toàn, không đụng độ
    với bất kỳ writer thật nào khác."""
    return FileLock(Path(credentials_path))
