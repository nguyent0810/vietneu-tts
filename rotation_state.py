"""Vòng xoay trạng thái dùng chung cho các Short generator "evergreen" xoay
qua 1 danh sách cố định (mệnh Ngũ Hành, quẻ Bát Thuần, cung hoàng đạo...).

BUG THẬT #1 (đã sửa trước đó) phát hiện qua Codex CLI review độc lập: bản
gốc (element_color_short_generator.py/_next_element(), iching_short_
generator.py/_next_quai(), western_zodiac_short_generator.py/_next_sign())
ĐỀU ghi state ngay khi CHỌN mục tiếp theo, TRƯỚC KHI biết
generate_verified_script() có PASS hay không -- nếu vòng sinh/chấm lỗi hết
cả MAX_ITERATIONS lần (agy/Codex down, fact-check fail liên tục...), mục đó
vẫn bị coi là "đã dùng" vĩnh viễn dù CHƯA từng ra được script hợp lệ, mất 1
mục khỏi vòng xoay mỗi lần lỗi -- nghiêm trọng hơn khi chạy cron không
giám sát vì lỗi có thể lặp lại nhiều lần liên tiếp.

Sửa #1: tách PEEK (chỉ xem mục tiếp theo) khỏi COMMIT (ghi lại mục VỪA DÙNG
THÀNH CÔNG) -- caller PHẢI tự gọi commit() SAU KHI xác nhận
result["passed"] is True, không phải ngay khi chọn mục để thử.

BUG THẬT #2 (audit tự động hoá đa kênh, mục C): giao dịch peek→(sinh nội
dung, có thể mất nhiều phút)→commit hoàn toàn KHÔNG có khoá nào bao trọn --
2 tiến trình gọi peek_next() gần như đồng thời (vd health-check kickstart
lại + lịch chạy bình thường trùng giờ) đều nhận về CÙNG 1 mục "tiếp theo",
cả 2 cùng sinh nội dung cho mục đó rồi cùng commit -- 1 mục trong vòng xoay
bị dùng 2 lần liên tiếp trong khi mục lẽ ra phải tới lượt lại bị bỏ qua.

Sửa #2: peek_next() giờ ĐÁNH DẤU "reserved" mục vừa trả về (ghi kèm
reserved_at), dưới 1 khoá flock CHỈ giữ trong lúc đọc-ghi JSON (rất ngắn,
không giữ suốt thời gian sinh nội dung). Lần peek_next() kế tiếp, nếu thấy
mục ứng viên đang bị 1 tiến trình khác reserved và reservation đó còn
"tươi" (chưa quá RESERVATION_TIMEOUT_SECONDS), sẽ tự nhảy sang mục sau đó
thay vì trả về cùng 1 mục. Reservation quá hạn (tiến trình giữ nó nhiều khả
năng đã chết/treo, không tự commit cũng không còn chạy) được coi như bỏ
trống, mục đó lại khả dụng bình thường. commit() xoá reservation khi ghi
last_item thành công."""
import fcntl
import json
import time
from pathlib import Path

RESERVATION_TIMEOUT_SECONDS = 900  # 15 phút -- quá hạn này coi như tiến trình giữ reservation đã chết/treo


class _StateFileLock:
    """flock ngắn hạn CHỈ bao quanh phần đọc-sửa-ghi JSON state -- KHÔNG giữ
    suốt thời gian sinh nội dung (gọi agy/codex, có thể mất nhiều phút)."""

    def __init__(self, state_path: Path):
        self._lock_path = state_path.with_suffix(state_path.suffix + ".lock")
        self._fh = None

    def __enter__(self):
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self._lock_path, "w")
        fcntl.flock(self._fh, fcntl.LOCK_EX)  # blocking -- giao dịch này luôn rất ngắn (đọc/ghi vài chục byte JSON)
        return self

    def __exit__(self, *exc):
        fcntl.flock(self._fh, fcntl.LOCK_UN)
        self._fh.close()


def _load_state(state_path: Path) -> dict:
    if not state_path.exists():
        return {}
    return json.loads(state_path.read_text(encoding="utf-8"))


def _save_state(state_path: Path, state: dict) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")


def peek_next(state_path: Path, order: list[str], state_key: str = "last_item") -> str:
    """Trả về mục TIẾP THEO trong `order` sau mục đã commit gần nhất -- an
    toàn gọi nhiều lần/gọi khi chỉ đang thử mà chưa chắc thành công. Tự động
    reserve mục trả về (khoá ngắn hạn quanh bước đọc-ghi) để 1 tiến trình
    khác gọi peek_next() gần như đồng thời không nhận về cùng 1 mục. Nếu
    state trống hoặc mục cuối không còn trong `order` (danh sách đổi), bắt
    đầu lại từ đầu."""
    with _StateFileLock(state_path):
        state = _load_state(state_path)
        order_len = len(order)
        last = state.get(state_key)
        last_idx = order.index(last) if last in order else -1

        reserved_item = state.get("reserved_item")
        reserved_at = state.get("reserved_at")
        reservation_fresh = (
            reserved_item is not None and reserved_at is not None
            and (time.time() - reserved_at) < RESERVATION_TIMEOUT_SECONDS
            and reserved_item in order
        )

        idx = (last_idx + 1) % order_len
        if reservation_fresh and idx == order.index(reserved_item):
            idx = (idx + 1) % order_len

        item = order[idx]
        state["reserved_item"] = item
        state["reserved_at"] = time.time()
        _save_state(state_path, state)
        return item


def commit(state_path: Path, item: str, state_key: str = "last_item") -> None:
    """Ghi lại mục VỪA DÙNG THÀNH CÔNG -- CHỈ gọi sau khi đã xác nhận
    generate_verified_script() trả passed=True cho mục này. Xoá reservation
    tương ứng (nếu còn khớp mục này)."""
    with _StateFileLock(state_path):
        state = _load_state(state_path)
        state[state_key] = item
        if state.get("reserved_item") == item:
            state.pop("reserved_item", None)
            state.pop("reserved_at", None)
        _save_state(state_path, state)


def pick_and_commit_next(state_path: Path, order: list[str], state_key: str = "last_item") -> str:
    """Chọn mục TIẾP THEO trong `order` VÀ ghi commit ngay -- TRONG CÙNG 1
    lock (đọc-chọn-ghi nguyên tử), khác hẳn cặp peek_next()+commit() (2
    lock riêng, có khoảng hở giữa đọc và ghi).

    BUG THẬT phát hiện qua Codex CLI review (audit 9 điểm, mục #2 -- xoay
    vòng biến thể ảnh Bát Quái/Ngũ Hành): dùng peek_next()+commit() cho
    trường hợp "chọn 1 asset tĩnh có sẵn, không có bước có thể fail" bị
    RACE CONDITION thật khi Long và Short render song song -- 2 tiến trình
    cùng gọi peek_next() gần như đồng thời trước khi bên nào kịp commit()
    có thể cùng nhận về CÙNG 1 item (do state chưa được ai commit lúc đọc),
    rồi cả 2 cùng commit tuần tự -- kết quả cuối phụ thuộc thứ tự commit
    (có thể đảo ngược lịch sử, thậm chí 2 tiến trình dùng TRÙNG variant
    trong cùng 1 đợt dù mục đích là tránh lặp).

    Dùng hàm này (không phải peek_next/commit) cho MỌI trường hợp việc
    "dùng mục" không thể fail sau khi chọn (vd chọn file ảnh tĩnh có sẵn)
    -- không cần khái niệm reservation vì không có khoảng hở giữa chọn và
    dùng. peek_next()/commit() vẫn giữ nguyên, KHÔNG đổi hành vi, cho các
    caller hiện có (sinh nội dung LLM có thể fail giữa lúc chọn và lúc
    dùng thật)."""
    with _StateFileLock(state_path):
        state = _load_state(state_path)
        order_len = len(order)
        last = state.get(state_key)
        last_idx = order.index(last) if last in order else -1
        item = order[(last_idx + 1) % order_len]
        state[state_key] = item
        _save_state(state_path, state)
        return item
