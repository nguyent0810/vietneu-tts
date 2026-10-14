"""Khoá file ngắn hạn dùng chung cho thao tác đọc-sửa-ghi registry.json
(short_batch_runner.py, long_batch_runner.py).

BUG THẬT (audit tự động hoá đa kênh, mục C): registry được load 1 lần vào bộ
nhớ rồi giữ NGUYÊN trong suốt cả quá trình xử lý (có thể mất nhiều phút/giờ,
qua nhiều bước TTS/render/SEO/upload) -- nếu 1 tiến trình KHÁC (cùng topic,
cùng loại nội dung) chạy song song và save trước, tiến trình sau vẫn giữ bản
ghi nhớ CŨ, save_registry() ghi đè TRẮNG cả file, XOÁ MẤT các entry mà tiến
trình kia vừa thêm/sửa cho các key KHÁC.

Sửa: mỗi lần save, giữ khoá NGẮN HẠN (chỉ quanh bước đọc-ghi JSON, KHÔNG giữ
suốt thời gian xử lý), đọc lại bản MỚI NHẤT trên đĩa, MERGE với bản trong bộ
nhớ (bộ nhớ thắng cho các key nó có -- phản ánh đúng thay đổi tiến trình này
vừa làm; các key CHỈ có trên đĩa, do tiến trình khác thêm, được GIỮ LẠI thay
vì bị xoá). Không giải quyết hoàn toàn trường hợp 2 tiến trình CÙNG lúc xử lý
CÙNG 1 key (xem ghi chú riêng ở nơi gọi save_registry lần đầu cho 1 mục) --
đó là rủi ro hẹp hơn, cần thêm bước "claim" riêng ở phía gọi.

G1 (Video Generation remediation, audit finding: production registry.json bị
1 ad-hoc/test script ghi đè NHẦM -- 2 lần thật, xem _reconstruction_note
trong output/shorts/{Phật giáo,Phong Thủy}/registry.json): thêm 4 lớp bảo vệ
mới, dùng CHUNG bởi short_batch_runner.py/long_batch_runner.py qua các hàm
dưới đây (không tự chế lại logic ở mỗi nơi gọi):
  1. write_registry_atomic() -- ghi ra file tạm CÙNG THƯ MỤC rồi fsync +
     os.replace() (atomic rename POSIX) thay vì path.write_text() trực tiếp
     -- nếu tiến trình chết giữa chừng, file THẬT trên đĩa không bao giờ ở
     trạng thái nửa-ghi.
  2. validate_registry_schema() -- chặn ghi/đọc dữ liệu sai cấu trúc rõ ràng
     (root không phải dict, key rỗng, entry không phải dict, status sai kiểu)
     trước khi nó có cơ hội trở thành 1 bản "hỏng" trên đĩa.
  3. _rotate_backup()/read_registry_safe() -- trước MỖI lần ghi thật, sao
     lưu bản hiện tại (nếu hợp lệ) vào .registry_backups/ (giữ 10 bản gần
     nhất); khi ĐỌC, nếu file chính hỏng/sai schema, tự động khôi phục từ
     bản backup hợp lệ gần nhất thay vì crash hay âm thầm trả về {} --
     "fail-closed" nghĩa là KHÔNG BAO GIỜ âm thầm dùng dữ liệu hỏng, nhưng
     CŨNG không bỏ cuộc ngay nếu còn cách phục hồi an toàn.
  4. mark_production_entry()/_is_production_write_allowed() -- ĐÂY LÀ SỬA
     TRỰC TIẾP CHO BUG THẬT Ở TRÊN: short_batch_runner.py/long_batch_runner.py
     gọi mark_production_entry() ĐÚNG 1 LẦN, ở dòng ĐẦU TIÊN của main() (chỉ
     ở đó) -- đánh dấu tiến trình này được phép ghi vào output/{shorts,long}/
     thật. Bất kỳ script/test nào KHÁC import các hàm save_registry* rồi gọi
     trực tiếp (đúng kịch bản bug thật đã xảy ra) mà KHÔNG đi qua main()
     thật sẽ bị write_registry_atomic() từ chối NGAY (RegistryWriteBlocked)
     thay vì âm thầm ghi đè -- không cần cấu hình gì thêm cho production
     (main() tự đánh dấu), không phá test hiện có (test đã theo quy ước
     monkeypatch _registry_path sang tmp_path, nên path không nằm trong cây
     production_root -- _is_production_write_allowed() bỏ qua check này)."""
import fcntl
import itertools
import json
import os
import re
import time
from pathlib import Path

# Bộ đếm riêng cho mỗi process -- dùng cùng timestamp để đặt tên file backup/
# temp KHÔNG BAO GIỜ trùng nhau, kể cả khi 2 lần ghi LIÊN TIẾP (không đồng
# thời -- FileLock đã đảm bảo tuần tự) rơi vào CÙNG mili-giây (Codex review
# G1 vòng 1 phát hiện: giả lập time.time() cố định qua 3 lần ghi liên tiếp
# làm 3 bản backup ghi đè lẫn nhau, "giữ 10 bản gần nhất" không còn đúng)."""
_backup_seq = itertools.count()


class FileLock:
    def __init__(self, path: Path):
        self._lock_path = path.with_suffix(path.suffix + ".lock")
        self._fh = None

    def __enter__(self):
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self._lock_path, "w")
        fcntl.flock(self._fh, fcntl.LOCK_EX)  # blocking -- giao dịch này luôn rất ngắn (đọc/ghi JSON registry)
        return self

    def __exit__(self, *exc):
        fcntl.flock(self._fh, fcntl.LOCK_UN)
        self._fh.close()


class RegistryValidationError(Exception):
    """Nội dung registry (đọc từ đĩa hoặc chuẩn bị ghi) không đúng cấu trúc
    tối thiểu mong đợi."""


class RegistryWriteBlocked(RuntimeError):
    """Từ chối ghi vì path trông giống cây production_root thật nhưng tiến
    trình này chưa gọi mark_production_entry() -- xem docstring module."""


_PRODUCTION_ENTRY_ENV = "VIETNEU_REGISTRY_PRODUCTION_ENTRY"
_BACKUP_KEEP = 10


def mark_production_entry() -> None:
    """Gọi ĐÚNG 1 LẦN, ở dòng ĐẦU TIÊN của main() trong
    short_batch_runner.py/long_batch_runner.py -- KHÔNG gọi ở nơi khác
    (kể cả trong test: test hợp lệ phải monkeypatch _registry_path sang
    tmp_path thay vì gọi hàm này để "tắt" bảo vệ)."""
    os.environ[_PRODUCTION_ENTRY_ENV] = "1"


def _is_production_write_allowed(path: Path, production_root: Path) -> bool:
    try:
        path.resolve().relative_to(production_root.resolve())
    except ValueError:
        return True  # path không nằm trong cây production thật -- luôn cho phép (test/tmp path)
    return os.environ.get(_PRODUCTION_ENTRY_ENV) == "1"


def validate_registry_schema(data) -> None:
    """Kiểm tra cấu trúc TỐI THIỂU -- đủ để chặn dữ liệu hỏng rõ ràng,
    KHÔNG cố định cứng nhắc mọi field (registry thật có rất nhiều field tuỳ
    chọn khác nhau giữa Long/Short/các topic -- xem REGISTRY_SCHEMAS.md của
    audit). Raise RegistryValidationError với lý do cụ thể nếu sai."""
    if not isinstance(data, dict):
        raise RegistryValidationError(f"registry root phải là dict, nhận {type(data).__name__}")
    for key, entry in data.items():
        if not isinstance(key, str) or not key:
            raise RegistryValidationError(f"registry key phải là string khác rỗng, nhận {key!r}")
        if not isinstance(entry, dict):
            raise RegistryValidationError(f"entry {key!r} phải là dict, nhận {type(entry).__name__}")
        status = entry.get("status")
        if not isinstance(status, str) or not status:
            # G1 (Codex review vòng 1, finding Low #4): TẤT CẢ 69 entry thật
            # trên cả 5 registry production hiện tại đều có status (đã xác
            # nhận trực tiếp) -- 1 entry thiếu status không mang trạng thái
            # resumable nào hữu ích, không có lý do hợp lệ để tồn tại trên
            # đĩa. Bắt buộc, không chỉ "nếu có" như bản đầu.
            raise RegistryValidationError(
                f"entry {key!r}: 'status' phải là string khác rỗng, nhận {status!r}"
            )


def _backup_dir_for(path: Path) -> Path:
    return path.parent / ".registry_backups"


_GENERATION_RE = re.compile(r"\.(\d+)\.")  # 1+ chữ số -- xem ghi chú finding vòng 4 dưới đây
_MAX_BACKUP_CREATE_ATTEMPTS = 1000


def _highest_generation_among_existing_backups(bdir: Path) -> int:
    """Quét TÊN FILE backup đã có trên đĩa (không phải .gen) để tìm
    generation lớn nhất từng dùng -- dùng làm SÀN (floor) khi .gen bị mất/
    hỏng, xem docstring _next_generation()."""
    if not bdir.exists():
        return 0
    highest = 0
    for f in bdir.iterdir():
        if not f.is_file():
            continue
        m = _GENERATION_RE.search(f.name)
        if m:
            highest = max(highest, int(m.group(1)))
    return highest


def _next_generation(bdir: Path) -> int:
    """Bộ đếm generation TOÀN CỤC (KHÔNG phải per-process) cho backup của 1
    registry -- đọc/tăng/ghi trong file ẩn .gen ngay trong thư mục backup.

    G1 (Codex review vòng 1 finding Medium #2, vòng 2 finding Medium #1):
    bản vá vòng 1 dùng itertools.count() per-process -- Codex review vòng 2
    tái hiện THẬT bằng 2 tiến trình python RIÊNG BIỆT (không phải 2 lần gọi
    trong CÙNG 1 process), mỗi tiến trình có bộ đếm process-local RIÊNG bắt
    đầu lại từ 0 -- 2 tiến trình đó tạo file backup TRÙNG TÊN, tiến trình
    sau ghi đè mất backup của tiến trình trước. Hàm này thay thế
    _backup_seq: đọc/ghi 1 SỐ NGUYÊN trên ĐĨA (không phải biến trong bộ
    nhớ process) -- được bảo vệ bởi CHÍNH FileLock mà caller (write_registry_
    atomic(), qua _rotate_backup()) đã giữ trước khi gọi, nên duy nhất THẬT
    SỰ và đúng thứ tự thời gian XUYÊN SUỐT nhiều tiến trình, không chỉ 1.

    G1 (Codex review vòng 3, finding Medium): nếu .gen bị MẤT hoặc HỎNG
    (vd đĩa lỗi, hoặc chính .gen bị ngắt giữa lúc ghi -- write_text() cũ
    không atomic) trong khi ĐÃ CÓ backup dùng generation cao hơn, đếm lại
    từ 0 sẽ tạo generation TRÙNG với 1 backup CŨ đã tồn tại -> ghi đè MẤT
    backup đó. Sửa: lấy SÀN là generation lớn nhất tìm được TRONG CHÍNH TÊN
    CÁC FILE BACKUP đã có (không chỉ tin .gen), rồi +1 từ đó -- đúng ngay cả
    khi .gen mất/hỏng hoàn toàn. Đồng thời ghi .gen bằng temp+replace (atomic)
    thay vì write_text() trực tiếp, để giảm khả năng .gen tự nó bị hỏng."""
    bdir.mkdir(parents=True, exist_ok=True)
    gen_file = bdir / ".gen"
    from_file = 0
    if gen_file.exists():
        try:
            from_file = int(gen_file.read_text(encoding="utf-8").strip())
        except (ValueError, OSError):
            from_file = 0
    floor = max(from_file, _highest_generation_among_existing_backups(bdir))
    nxt = floor + 1
    tmp_gen = bdir / f".gen.tmp-{os.getpid()}-{next(_backup_seq):06d}"
    try:
        tmp_gen.write_text(str(nxt), encoding="utf-8")
        os.replace(tmp_gen, gen_file)
    except BaseException:
        try:
            tmp_gen.unlink(missing_ok=True)
        except OSError:
            pass
        raise
    return nxt


def _rotate_backup(path: Path) -> None:
    """Sao lưu bản HIỆN TẠI trên đĩa (nếu tồn tại và hợp lệ) trước khi nó bị
    ghi đè, giữ lại _BACKUP_KEEP bản gần nhất. Nếu bản hiện tại đã hỏng, KHÔNG
    backup nó (tránh đè lên lịch sử backup TỐT bằng 1 bản hỏng) -- write mới
    vẫn được validate_registry_schema() kiểm tra riêng trước khi commit.

    G1 (Codex review vòng 4): sau 3 vòng review liên tiếp đều tìm ra CÁCH
    MỚI khiến cơ chế "đếm generation rồi tin số đó" (dù đã qua nhiều lớp vá
    -- per-process counter -> đếm trên đĩa -> suy sàn từ tên file có sẵn)
    vẫn có thể bị lệch trong 1 trường hợp biên nào đó, Codex review vòng 4
    đề nghị THẲNG: đừng dựa vào việc "đoán đúng" số generation nữa -- dùng
    O_CREAT|O_EXCL (tạo file ĐỘC QUYỀN, hệ điều hành tự chối nếu đích đã
    tồn tại) làm ĐÚNG BẢO ĐẢM CUỐI CÙNG, không phụ thuộc bất kỳ giả định
    đếm/parse tên file nào có đúng hay không. _next_generation() (đếm +
    quét sàn) vẫn giữ lại làm GỢI Ý điểm bắt đầu (hiệu năng -- trường hợp
    thường, đúng ngay lần thử đầu), nhưng ĐÚNG ĐẮN không còn phụ thuộc vào
    gợi ý đó đúng hay sai: nếu tên đích đã tồn tại (bất kể lý do gì -- đếm
    sai, 2 tiến trình, tên file lạ khiến quét sai...), open() sẽ raise
    FileExistsError, vòng lặp CHỈ ĐƠN GIẢN thử số kế tiếp -- không bao giờ
    ghi đè 1 backup đã tồn tại."""
    if not path.exists():
        return
    try:
        raw = path.read_bytes()
        data = json.loads(raw.decode("utf-8"))
        validate_registry_schema(data)
    except Exception:
        return
    bdir = _backup_dir_for(path)
    hint = _next_generation(bdir)  # gợi ý điểm bắt đầu -- không cần đúng tuyệt đối
    stamp = time.strftime("%Y%m%dT%H%M%S", time.gmtime())  # chỉ để người đọc dễ nhận diện
    dest = None
    for attempt in range(_MAX_BACKUP_CREATE_ATTEMPTS):
        gen = hint + attempt
        candidate = bdir / f"{path.stem}.{gen:012d}.{stamp}{path.suffix}"
        try:
            fd = os.open(candidate, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            continue  # đích đã tồn tại (bất kể lý do) -- thử số kế tiếp, KHÔNG BAO GIỜ ghi đè
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(raw)
                f.flush()
                os.fsync(f.fileno())
        except BaseException:
            # G1 (Codex review vòng 5, finding Low): dọn dẹp CHÍNH NÓ cũng
            # có thể lỗi -- không được để lỗi dọn dẹp ĐÈ LÊN lỗi gốc (vd
            # disk-full) đang được raise lại, cùng nguyên tắc đã áp dụng
            # cho write_registry_atomic() ở trên.
            try:
                candidate.unlink(missing_ok=True)
            except OSError:
                pass
            raise
        dest = candidate
        break
    if dest is None:
        raise RuntimeError(
            f"không thể tạo file backup duy nhất cho {path} sau {_MAX_BACKUP_CREATE_ATTEMPTS} "
            f"lần thử bắt đầu từ generation {hint} -- kiểm tra thư mục {bdir}"
        )
    backups = sorted(bdir.glob(f"{path.stem}.*{path.suffix}"))
    for stale in backups[:-_BACKUP_KEEP]:
        stale.unlink(missing_ok=True)


def _backups_newest_first(path: Path) -> list[Path]:
    bdir = _backup_dir_for(path)
    if not bdir.exists():
        return []
    return sorted(bdir.glob(f"{path.stem}.*{path.suffix}"), reverse=True)


def read_registry_safe(path: Path) -> dict:
    """Đọc fail-closed: file không tồn tại -> {} (hành vi cũ, không đổi).
    File tồn tại nhưng JSON hỏng HOẶC sai schema -> thử khôi phục, LẦN LƯỢT
    từ backup MỚI NHẤT tới CŨ NHẤT, dừng ở bản ĐẦU TIÊN hợp lệ; nếu KHÔNG
    backup nào hợp lệ, raise RegistryValidationError thay vì âm thầm trả về
    {} hay dữ liệu hỏng.

    G1 (Codex review vòng 1, finding Medium #1): bản đầu tiên chỉ thử ĐÚNG 1
    backup (mới nhất) -- nếu chính bản đó CŨNG hỏng (vd corrupt đĩa 2 lần
    liên tiếp, hoặc chính do bug #2 ở trên khiến nhiều lần ghi trùng tên rồi
    lần ghi đè cuối bị hỏng) trong khi 1 backup CŨ HƠN vẫn còn hợp lệ, hàm
    sẽ raise dù có thể phục hồi được -- SỬA bằng cách thử LẦN LƯỢT."""
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
        validate_registry_schema(data)
        return data
    except (json.JSONDecodeError, RegistryValidationError) as primary_exc:
        last_exc = primary_exc
        for backup in _backups_newest_first(path):
            try:
                data_b = json.loads(backup.read_text(encoding="utf-8"))
                validate_registry_schema(data_b)
                return data_b
            except (json.JSONDecodeError, RegistryValidationError) as backup_exc:
                last_exc = backup_exc
                continue
        raise RegistryValidationError(
            f"{path} hỏng/sai schema ({primary_exc}) và không có backup HỢP LỆ nào tại "
            f"{_backup_dir_for(path)} (backup gần nhất thử được, nếu có, cũng lỗi: {last_exc})"
        ) from primary_exc


def write_registry_atomic(path: Path, data: dict, production_root: Path) -> None:
    """Ghi registry an toàn: chặn ghi ngoài ý muốn vào cây production
    (RegistryWriteBlocked), validate schema, backup bản cũ, rồi ghi ATOMIC
    (temp file cùng thư mục + fsync + os.replace). Caller PHẢI đã giữ
    FileLock(path) trước khi gọi hàm này (hàm này không tự khoá)."""
    if not _is_production_write_allowed(path, production_root):
        raise RegistryWriteBlocked(
            f"Từ chối ghi {path}: nằm trong cây production thật ({production_root}) nhưng "
            "tiến trình này chưa gọi mark_production_entry() (chỉ main() của "
            "short_batch_runner.py/long_batch_runner.py mới gọi hàm đó). Nếu đây là test, "
            "monkeypatch _registry_path sang tmp_path thay vì gọi save_registry*() trên path thật."
        )
    validate_registry_schema(data)
    _rotate_backup(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # _backup_seq (không phải chỉ pid+mili-giây) -- cùng lý do collision-
    # resistance như _rotate_backup() ở trên, áp dụng cho tên file TẠM.
    tmp = path.parent / f".{path.name}.tmp-{os.getpid()}-{next(_backup_seq):06d}-{int(time.time() * 1000)}"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=2))
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)  # atomic trên POSIX -- không bao giờ có trạng thái nửa-ghi ở path thật
    except BaseException:
        # G1 (Codex review vòng 1, finding Low #3): đừng để lại file .tmp-*
        # mồ côi nếu bất kỳ bước nào ở trên lỗi (serialize/fsync/replace).
        # G1 (Codex review vòng 2, finding Low #2): dọn dẹp CHÍNH NÓ cũng có
        # thể lỗi (vd quyền file) -- không được để lỗi dọn dẹp ĐÈ LÊN lỗi
        # gốc đang được raise lại; chỉ best-effort, luôn ưu tiên lỗi gốc.
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        raise
    else:
        # Best-effort: fsync CHÍNH thư mục chứa để bản thân thao tác rename
        # cũng bền vững qua mất điện đột ngột (rename đã atomic, nhưng
        # atomic != durable -- 1 số filesystem/nền tảng không hỗ trợ fsync
        # thư mục, nên chỉ best-effort, không chặn write đã thành công).
        try:
            dir_fd = os.open(str(path.parent), os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except OSError:
            pass
