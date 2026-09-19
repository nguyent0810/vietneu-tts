"""Topic-bank dùng chung cho các Short generator theo kiến trúc "trích chủ đề
1 lần / sinh nhiều lần" (educational_short_generator.py, storytelling_short_
generator.py) -- đọc research draft trong SOURCES 1 lần, cache lại danh sách
chủ đề + đoạn trích làm căn cứ fact-check, mỗi lần sinh Short chỉ lấy 1 chủ
đề CHƯA DÙNG.

BUG THẬT phát hiện qua Codex CLI review độc lập (xem phiên làm việc) -- CẢ
HAI bản gốc đều có chung 2 lỗi (đúng là lý do nên gộp vào 1 module dùng
chung thay vì mỗi generator tự chép lại 1 bản -- sửa 1 nơi thì lan sang cả
2 nơi, tránh drift):

1. `--rebuild-bank` XOÁ TRẮNG used_titles -- nếu rebuild sau khi đã đăng
   vài chủ đề, các chủ đề đó "quên" mình đã dùng, có nguy cơ bị CHỌN LẠI
   và đăng TRÙNG nội dung. Sửa: rebuild GIỮ NGUYÊN used_titles cũ; chỉ
   thay thế phần "topics" theo TỪNG source_file bị trích lại, không ghi đè
   toàn bộ bank.

2. File SOURCES trích lỗi (agy lỗi/JSON hỏng) bị BỎ QUA VĨNH VIỄN -- bank
   coi là "đã đủ" ngay khi topics không rỗng (dù thiếu hẳn 1-2 file bị
   lỗi), không có cơ chế thử lại riêng. Sửa: lưu "failed_sources" trong
   bank; mỗi lần build (kể cả không force) tự động thử lại CÁC FILE ĐÃ LỖI
   trước đó (không thử lại toàn bộ -- tiết kiệm request agy)."""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from content_seo import ContentSeoError  # noqa: E402


def _load_bank(bank_path: Path) -> dict:
    if bank_path.exists():
        bank = json.loads(bank_path.read_text(encoding="utf-8"))
        bank.setdefault("topics", [])
        bank.setdefault("used_titles", [])
        bank.setdefault("failed_sources", [])
        return bank
    return {"topics": [], "used_titles": [], "failed_sources": []}


def _save_bank(bank_path: Path, bank: dict) -> None:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    bank_path.write_text(json.dumps(bank, ensure_ascii=False, indent=2), encoding="utf-8")


def _validate_topics(topics, source_name: str) -> list[dict]:
    """extract_fn() (mã của TỪNG generator, vd educational_short_generator.py::
    extract_topic_bank()) đọc result["topics"] và t["source_file"]=... trực
    tiếp không validate -- JSON hợp lệ nhưng THIẾU/SAI KIỂU (thiếu key
    "topics", 1 topic không phải dict, thiếu "title"...) sẽ raise
    KeyError/TypeError THẲNG từ bên trong extract_fn, không phải
    ContentSeoError. BUG THẬT phát hiện qua Codex CLI review LẦN 2: lỗi đó
    KHÔNG được coi là "file trích lỗi -- thử lại sau" (chỉ except
    ContentSeoError), mà làm SẬP LUÔN build_full_topic_bank() giữa chừng,
    crash cả batch chỉ vì 1 file nguồn. Validate rõ ràng ở đây để lỗi hình
    dạng luôn được chuẩn hoá thành ContentSeoError, xử lý giống mọi lỗi
    trích chủ đề khác (ghi vào failed_sources, tự thử lại lần build sau)."""
    if not isinstance(topics, list) or not topics:
        raise ContentSeoError(f"extract_fn trả về topics rỗng/không phải list cho {source_name}: {topics!r}"[:500])
    for t in topics:
        if not isinstance(t, dict) or not isinstance(t.get("title"), str) or not t["title"].strip():
            raise ContentSeoError(f"1 topic thiếu/sai kiểu 'title' cho {source_name}: {t!r}"[:500])
    return topics


def build_full_topic_bank(bank_path: Path, sources_dir: Path, extract_fn, force_refresh: bool = False) -> dict:
    """extract_fn(source_path: Path) -> list[dict], mỗi dict PHẢI có 'title'
    và tự gán 'source_file' -- đây là hàm trích chủ đề RIÊNG của từng
    generator (prompt khác nhau: kiến thức nền vs giai thoại kể chuyện),
    module này chỉ điều phối cache/merge/retry, không biết nội dung prompt.

    force_refresh=False: chỉ trích các file CHƯA từng có trong bank VÀ các
    file đã lỗi lần build trước (failed_sources) -- không tốn request agy
    trích lại file đã trích thành công.
    force_refresh=True: trích lại TẤT CẢ file, nhưng used_titles GIỮ
    NGUYÊN (xem docstring module, đây chính là bug đã sửa)."""
    bank = _load_bank(bank_path)
    source_files = sorted(p for p in sources_dir.glob("*.md") if p.name != "SOURCE_REGISTRY.md")
    known_sources = {t["source_file"] for t in bank["topics"]}
    failed = set(bank.get("failed_sources", []))

    if force_refresh:
        to_process = source_files
    else:
        to_process = [sf for sf in source_files if sf.name not in known_sources or sf.name in failed]
        if not to_process and bank["topics"]:
            return bank

    still_failed = []
    for sf in to_process:
        try:
            topics = extract_fn(sf)
            topics = _validate_topics(topics, sf.name)
        except (ContentSeoError, KeyError, TypeError, ValueError) as exc:
            # Bắt cả KeyError/TypeError/ValueError THẲNG từ extract_fn (xem
            # docstring _validate_topics) -- không chỉ ContentSeoError, để
            # 1 file JSON hình dạng sai không làm sập cả batch.
            print(f"CẢNH BÁO: trích chủ đề lỗi cho {sf.name} ({exc!r}) -- giữ nguyên bản cũ nếu có, tự thử lại ở lần build kế tiếp.", file=sys.stderr)
            still_failed.append(sf.name)
            continue
        print(f"  {sf.name}: {len(topics)} chủ đề", flush=True)
        bank["topics"] = [t for t in bank["topics"] if t["source_file"] != sf.name] + topics

    bank["failed_sources"] = still_failed
    _save_bank(bank_path, bank)
    return bank


def next_unused_topic(bank_path: Path) -> dict | None:
    bank = _load_bank(bank_path)
    unused = [t for t in bank["topics"] if t["title"] not in bank["used_titles"]]
    if not unused:
        return None
    return random.choice(unused)


def mark_topic_used(bank_path: Path, title: str) -> None:
    bank = _load_bank(bank_path)
    if title not in bank["used_titles"]:
        bank["used_titles"].append(title)
        _save_bank(bank_path, bank)
