"""
Backfill 1 registry entry Long với video_id đã tồn tại THẬT trên YouTube --
đóng chiều CÒN LẠI của lỗ hổng đã gây ra vụ đăng trùng thật 2026-08-11 (xem
duplicate_check.py docstring cho toàn bộ điều tra): nguyên nhân gốc không
chỉ là "pipeline không kiểm tra trùng trước khi upload" (đã sửa ở
duplicate_check.py + long_batch_runner.py) mà còn là "1 số video được
upload THỦ CÔNG (ngoài luồng long_batch_runner.py) không bao giờ được ghi
vào registry.json" -- lần chạy tự động SAU đó hoàn toàn không biết video
thủ công đó đã tồn tại.

Dùng khi nào:
  1. Vừa upload thủ công 1 video Long ngoài luồng (vd test/debug, hoặc xử
     lý khẩn) -- ghi NGAY vào registry để lần chạy long_batch_runner.py kế
     tiếp không render+upload trùng đúng tập đó.
  2. Registry entry đang ở status "possible_duplicate_detected" (xem
     duplicate_check.py) và người xem đã XÁC NHẬN đúng là trùng (video nghi
     ngờ CHÍNH LÀ tập này) -- backfill video_id nghi ngờ đó thay vì để
     pipeline thử upload lại.

KHÔNG dùng để "che" 1 tập chưa từng thực sự upload -- xem các lớp bảo vệ
dưới đây, thiết kế RÕ RÀNG để không thể lạm dụng ngầm:
  1. --video-id BẮT BUỘC tường minh (không tự đoán/tự chọn video nào).
  2. Tra cứu THẬT videos.list cho chính video_id đó -- KHÔNG cho phép
     backfill 1 video_id không tồn tại/không đọc được.
  3. Xác nhận video đó thuộc ĐÚNG kênh của --credentials đang dùng (so
     snippet.channelId thật với get_own_channel_id()) -- chặn backfill
     nhầm kênh (vd dán video_id của kênh khác).
  4. Nếu registry entry có wav_path (audio nguồn cục bộ của CHÍNH tập này)
     đọc được, đối chiếu duration audio đó với duration THẬT của video trên
     YouTube (cùng ngưỡng AUDIO_DURATION_TOLERANCE_SEC ở duplicate_check.py)
     -- lệch quá xa (video không khớp nội dung âm thanh của tập này) thì
     TỪ CHỐI trừ khi --force + có --reason giải thích rõ (ghi lại nguyên
     văn vào registry để audit sau).
  5. --reason BẮT BUỘC (câu chữ tự do, ghi vào entry["backfill_reason"]) --
     luôn có dấu vết TẠI SAO 1 entry được backfill thay vì để trống.
  6. Nếu entry đã có status="uploaded" với 1 video_id KHÁC, từ chối trừ khi
     --force -- không âm thầm ghi đè bằng chứng video_id cũ (có thể chính
     nó là 1 trong các bản trùng cần biết, không phải xoá dấu vết)."""
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import long_batch_runner as lbr
from duplicate_check import AUDIO_DURATION_TOLERANCE_SEC, channel_upload_lock, probe_duration_seconds
from registry_lock import mark_production_entry
from youtube_catalog import VIDEOS_URL, YouTubeCatalogError, _get, get_own_channel_id
from youtube_sync import _parse_iso8601_duration


class RecordExistingUploadError(RuntimeError):
    pass


def _fetch_real_video(credentials_path: str, video_id: str) -> dict:
    """Tra cứu THẬT videos.list cho ĐÚNG 1 video_id -- trả về
    {video_id, title, channel_id, duration_seconds, published_at}. Raise
    nếu video không tồn tại/không đọc được (KHÔNG cho phép backfill mù)."""
    data = _get(credentials_path, VIDEOS_URL, {"part": "snippet,contentDetails", "id": video_id})
    items = data.get("items", [])
    if not items:
        raise RecordExistingUploadError(
            f"videos.list không trả về video nào cho id={video_id!r} -- có thể video_id sai/video đã bị xoá. "
            f"KHÔNG backfill mù, sửa lại --video-id."
        )
    item = items[0]
    snippet = item.get("snippet", {})
    duration_raw = item.get("contentDetails", {}).get("duration")
    return {
        "video_id": item["id"],
        "title": snippet.get("title", ""),
        "channel_id": snippet.get("channelId"),
        "duration_seconds": float(_parse_iso8601_duration(duration_raw) or 0) if duration_raw else None,
        "published_at": snippet.get("publishedAt"),
    }


def record_existing_upload(
    topic: str,
    episode_id: str,
    video_id: str,
    credentials_path: str,
    reason: str,
    ffprobe_path: str | None = None,
    force: bool = False,
) -> dict:
    real_video = _fetch_real_video(credentials_path, video_id)

    own_channel_id = get_own_channel_id(credentials_path)
    if real_video["channel_id"]:
        if real_video["channel_id"] != own_channel_id:
            # Xác nhận CHẮC CHẮN sai kênh -- KHÔNG có đường --force bypass ở
            # đây (khác hẳn nhánh "không xác nhận được" bên dưới): đây không
            # phải "chưa xác minh", mà là ĐÃ XÁC NHẬN sai, ghi đè bất chấp sẽ
            # ghi bằng chứng SAI vào registry của tập này.
            raise RecordExistingUploadError(
                f"video_id={video_id!r} thuộc kênh {real_video['channel_id']!r}, KHÔNG PHẢI kênh của "
                f"--credentials đang dùng ({own_channel_id!r}) -- có thể nhầm --credentials hoặc nhầm video_id. "
                f"Từ chối backfill sang sai kênh (không có --force nào bypass được lỗi này)."
            )
    elif not force:
        # Codex CLI adversarial review round 1, finding thật mục D: nếu
        # videos.list KHÔNG trả về channelId (trường hợp hiếm nhưng có
        # thật, vd video riêng tư/hạn chế theo khu vực), bản vá trước đây
        # ÂM THẦM COI LÀ ĐÃ XÁC NHẬN ĐÚNG KÊNH -- sai: "không biết" khác
        # hẳn "đã xác nhận đúng". Fail-closed: từ chối trừ khi --force.
        raise RecordExistingUploadError(
            f"videos.list KHÔNG trả về channelId cho video_id={video_id!r} -- không thể tự xác nhận video "
            f"này thuộc đúng kênh của --credentials đang dùng ({own_channel_id!r}). Từ chối backfill "
            f"(fail-closed). Nếu đã tự xác nhận thủ công (vd mở link video, xem đúng là kênh của mình), "
            f"truyền --force kèm --reason giải thích rõ."
        )

    # channel_upload_lock() (Codex CLI adversarial review round 3, finding
    # thật còn sót lại): long_batch_runner.py giữ khoá NÀY xuyên suốt từ
    # lúc kiểm tra trùng tới khi lưu registry -- nhưng script backfill THỦ
    # CÔNG này trước đây đọc/ghi registry HOÀN TOÀN NGOÀI khoá đó. Race
    # thật: long_batch_runner.py đọc registry TƯƠI (status="seo_ready")
    # ngay sau khi giành khoá kênh, rồi script backfill này (không tham
    # gia khoá) ghi status="uploaded" NGAY GIỮA lúc long_batch_runner.py
    # đang kiểm tra trùng/upload -- long_batch_runner.py không biết, vẫn
    # upload xong rồi GHI ĐÈ mất video_id vừa backfill (save_registry()'s
    # merge "bộ nhớ thắng cho key nó có" khiến bản ghi của long_batch_runner.py
    # đè lên). Tham gia CÙNG khoá kênh (cùng credentials_path -- cùng file
    # khoá vật lý với long_batch_runner.py, xem channel_upload_lock()) để
    # 2 con đường ghi "uploaded" (tự động vs thủ công) không bao giờ chồng
    # lấn thời gian đọc-quyết-ghi.
    with channel_upload_lock(credentials_path):
        registry = lbr.load_registry(topic)
        entry = registry.get(episode_id, {"key": episode_id})
        prior_status = entry.get("status")
        prior_video_id = entry.get("video_id")

        if prior_status == "uploaded" and prior_video_id and prior_video_id != video_id and not force:
            raise RecordExistingUploadError(
                f"Entry '{episode_id}' (topic={topic!r}) ĐÃ có status='uploaded' với video_id={prior_video_id!r} "
                f"khác với video_id={video_id!r} đang backfill -- có thể chính prior_video_id cũng là 1 bản trùng "
                f"cần biết, KHÔNG âm thầm ghi đè. Truyền --force nếu CHẮC CHẮN muốn thay thế (sẽ lưu lại "
                f"prior_video_id vào backfill_replaced_video_id để không mất dấu vết)."
            )

        # Đối chiếu duration audio nguồn CỤC BỘ (nếu còn) với duration THẬT
        # của video trên YouTube -- lớp bảo vệ CHÍNH chống lạm dụng
        # "backfill 1 video_id bất kỳ để che 1 tập chưa từng thực sự
        # upload" (xem docstring module). Chỉ kiểm được nếu registry entry
        # còn wav_path VÀ file đó còn tồn tại cục bộ (có thể đã bị
        # finalize_episode.py dọn/di chuyển với tập rất cũ -- khi đó không
        # kiểm được, coi là "không xác nhận được", KHÔNG coi là "đã xác
        # nhận khớp").
        #
        # QUAN TRỌNG (Codex CLI adversarial review round 1, finding thật
        # mục D): bản vá trước đây chỉ đòi --force khi CÓ kiểm tra ĐƯỢC và
        # kết quả LỆCH -- nếu không kiểm tra được (thiếu wav_path/ffprobe/
        # thiếu duration YouTube) thì backfill THÀNH CÔNG NGAY, không cần
        # --force. Đây là lỗ hổng thật: "video tồn tại thật + đúng kênh +
        # lý do bất kỳ (kể cả rỗng về mặt ngữ nghĩa)" là đủ để đánh dấu 1
        # tập là "đã upload" mà KHÔNG hề xác nhận nội dung có khớp không --
        # ai đó có thể dán video_id của 1 tập KHÁC thật trên cùng kênh
        # (không phải trùng, chỉ là không xác minh được) để "che" 1 tập
        # chưa từng thực sự tồn tại. Sửa: đòi --force cho CẢ 2 trường hợp
        # -- "kiểm tra được nhưng lệch" (như cũ) VÀ "không kiểm tra được"
        # (MỚI) -- không xác minh được thì KHÔNG được coi là an toàn mặc
        # định nữa, phải là lựa chọn TƯỜNG MINH của người vận hành.
        duration_check = {"performed": False, "matched": None, "diff_seconds": None}
        wav_path = entry.get("wav_path")
        if wav_path and ffprobe_path and real_video["duration_seconds"] is not None and Path(wav_path).exists():
            local_audio_duration = probe_duration_seconds(wav_path, ffprobe_path)
            diff = abs(real_video["duration_seconds"] - local_audio_duration)
            duration_check = {
                "performed": True,
                "matched": diff <= AUDIO_DURATION_TOLERANCE_SEC,
                "diff_seconds": diff,
            }

        if not force:
            if not duration_check["performed"]:
                raise RecordExistingUploadError(
                    f"KHÔNG THỂ tự đối chiếu duration audio nguồn cục bộ của tập '{episode_id}' với duration "
                    f"THẬT của video_id={video_id!r} trên YouTube (thiếu wav_path trong registry entry, thiếu "
                    f"--ffprobe, hoặc file wav không còn tồn tại cục bộ) -- KHÔNG đủ căn cứ tự động xác nhận "
                    f"video này đúng là bản của tập này. Từ chối backfill (fail-closed). Nếu đã tự xác nhận thủ "
                    f"công (vd tự nghe/xem lại video trên YouTube, đối chiếu nội dung), truyền --force kèm "
                    f"--reason nêu rõ CÁCH đã xác nhận."
                )
            if not duration_check["matched"]:
                raise RecordExistingUploadError(
                    f"Duration video THẬT trên YouTube ({real_video['duration_seconds']:.1f}s) LỆCH "
                    f"{duration_check['diff_seconds']:.1f}s so với audio nguồn cục bộ của tập '{episode_id}' -- "
                    f"vượt ngưỡng {AUDIO_DURATION_TOLERANCE_SEC}s cho phép. video_id={video_id!r} có thể "
                    f"KHÔNG PHẢI là bản của tập này. Từ chối backfill. Nếu CHẮC CHẮN đúng tập (vd audio đã "
                    f"chỉnh sửa/re-render sau khi video này lên sóng), truyền --force kèm --reason giải thích rõ."
                )

        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        entry["video_id"] = video_id
        entry["status"] = "uploaded"
        if real_video["published_at"]:
            entry.setdefault("publish_at", real_video["published_at"])
        entry["backfilled_manual_upload"] = True
        entry["backfilled_at"] = now_iso
        entry["backfill_reason"] = reason
        entry["backfilled_video_title"] = real_video["title"]
        entry["backfilled_video_duration_seconds"] = real_video["duration_seconds"]
        entry["backfill_duration_check"] = duration_check
        if prior_status == "uploaded" and prior_video_id and prior_video_id != video_id:
            entry["backfill_replaced_video_id"] = prior_video_id
        # Xoá cờ nghi trùng cũ (nếu có) -- entry giờ đã có quyết định RÕ
        # RÀNG của người thật (chính lệnh backfill này), không còn "chờ
        # xem xét" nữa.
        entry.pop("possible_duplicate", None)

        registry[episode_id] = entry
        lbr.save_registry(registry, topic)
        return entry


def main() -> int:
    # PHẢI là dòng đầu tiên -- registry_lock.py mục 4 (G1): script này GHI
    # thật vào output/long/<topic>/registry.json production, cần tự đánh
    # dấu production entry giống long_batch_runner.py/short_batch_runner.py.
    mark_production_entry()
    ap = argparse.ArgumentParser(
        description="Backfill 1 registry entry Long với video_id đã upload THỦ CÔNG/đã xác nhận trùng thật.",
    )
    ap.add_argument("--topic", required=True, help='vd "Phật giáo"/"Phong Thủy"/"Hình Sự"')
    ap.add_argument("--episode-id", required=True, help='vd "EP005"')
    ap.add_argument("--video-id", required=True, help="video_id THẬT trên YouTube (11 ký tự, xem URL youtu.be/<id>)")
    ap.add_argument("--credentials", required=True, help="đường dẫn .youtube_channels/<kênh>.json ĐÚNG kênh chứa video này")
    ap.add_argument("--reason", required=True, help="Vì sao backfill thủ công thay vì để pipeline tự upload -- ghi lại để audit sau")
    ap.add_argument("--ffprobe", default=None, help="Đường dẫn ffprobe để đối chiếu duration audio nguồn (khuyến khích truyền, xem docstring)")
    ap.add_argument("--force", action="store_true", help="Bỏ qua cảnh báo lệch duration/ghi đè video_id cũ -- CHỈ dùng khi đã tự xác nhận thủ công")
    args = ap.parse_args()

    try:
        entry = record_existing_upload(
            args.topic, args.episode_id, args.video_id, args.credentials, args.reason,
            ffprobe_path=args.ffprobe, force=args.force,
        )
    except (RecordExistingUploadError, YouTubeCatalogError) as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 1

    print(f"OK: '{args.episode_id}' (topic={args.topic!r}) đã ghi video_id={entry['video_id']!r}, status='uploaded'.")
    print(f"  title thật trên YouTube: {entry.get('backfilled_video_title')!r}")
    if entry.get("backfill_duration_check", {}).get("performed"):
        c = entry["backfill_duration_check"]
        print(f"  đối chiếu duration audio nguồn: khớp={c['matched']} (lệch {c['diff_seconds']:.1f}s)")
    else:
        print("  đối chiếu duration audio nguồn: KHÔNG thực hiện được (thiếu wav_path/ffprobe/duration) -- tự xác nhận thủ công.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
