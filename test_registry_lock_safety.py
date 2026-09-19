"""G1 (Video Generation remediation) -- test các lớp bảo vệ mới trong
registry_lock.py: atomic write, schema validation, backup rotation/recovery,
và guard chặn ghi ngoài ý muốn vào cây production (bug thật: ad-hoc/test
script ghi đè NHẦM registry.json production 2 lần, xem
output/shorts/{Phật giáo,Phong Thủy}/registry.json's _reconstruction_note).

TOÀN BỘ test dùng tmp_path -- KHÔNG test nào được đụng tới registry.json
production thật."""
import json
import os
import subprocess
import sys

import pytest

import registry_lock as rl

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


# ─── validate_registry_schema() ─────────────────────────────────────────

def test_validate_schema_accepts_real_shaped_data():
    data = {
        "EP001": {"key": "EP001", "status": "uploaded", "seo": {"titles": ["a"]}},
        "05_seg_01": {"key": "05_seg_01", "status": "needs_review", "hook_score": 7.5},
    }
    rl.validate_registry_schema(data)  # không raise


def test_validate_schema_rejects_entry_without_status():
    """G1 (Codex review vòng 1, finding Low #4): TẤT CẢ 69 entry thật trên
    5 registry production hiện tại đều có status -- 1 entry thiếu status
    không mang trạng thái resumable hữu ích nào, phải bị chặn."""
    with pytest.raises(rl.RegistryValidationError, match="status.*phải là string khác rỗng"):
        rl.validate_registry_schema({"EP004": {"key": "EP004", "shot_list_path": None}})


def test_validate_schema_rejects_empty_string_status():
    with pytest.raises(rl.RegistryValidationError, match="status.*phải là string khác rỗng"):
        rl.validate_registry_schema({"EP004": {"status": ""}})


def test_validate_schema_rejects_non_dict_root():
    with pytest.raises(rl.RegistryValidationError, match="root phải là dict"):
        rl.validate_registry_schema(["not", "a", "dict"])


def test_validate_schema_rejects_non_dict_entry():
    with pytest.raises(rl.RegistryValidationError, match="phải là dict"):
        rl.validate_registry_schema({"EP001": "not a dict"})


def test_validate_schema_rejects_empty_key():
    with pytest.raises(rl.RegistryValidationError, match="key phải là string"):
        rl.validate_registry_schema({"": {"status": "uploaded"}})


def test_validate_schema_rejects_non_string_status():
    with pytest.raises(rl.RegistryValidationError, match="status.*phải là string"):
        rl.validate_registry_schema({"EP001": {"status": 123}})


# ─── write_registry_atomic(): atomic write + fsync/rename ──────────────

def test_write_registry_atomic_creates_file_with_exact_content(tmp_path):
    path = tmp_path / "output" / "shorts" / "Test" / "registry.json"
    data = {"k1": {"status": "uploaded"}}
    rl.mark_production_entry()  # simula production entry -- production_root below is tmp_path, never real
    rl.write_registry_atomic(path, data, production_root=tmp_path)
    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8")) == data


def test_write_registry_atomic_no_stray_tmp_file_left_on_success(tmp_path):
    path = tmp_path / "registry.json"
    rl.mark_production_entry()
    rl.write_registry_atomic(path, {"k": {"status": "x"}}, production_root=tmp_path)
    leftovers = [p for p in tmp_path.iterdir() if p.name.startswith(".registry.json.tmp-")]
    assert leftovers == []


def test_write_registry_atomic_rejects_bad_schema_before_touching_disk(tmp_path):
    path = tmp_path / "registry.json"
    path.write_text('{"original": "content"}', encoding="utf-8")
    rl.mark_production_entry()
    with pytest.raises(rl.RegistryValidationError):
        rl.write_registry_atomic(path, {"bad": "not a dict shaped like an entry... wait this IS the value"},
                                  production_root=tmp_path)
    # entry value above is a string, not dict -- must be rejected; original file untouched
    assert path.read_text(encoding="utf-8") == '{"original": "content"}'


def test_write_registry_atomic_interrupted_write_leaves_original_untouched(tmp_path, monkeypatch):
    """Mô phỏng crash GIỮA CHỪNG ghi (sau khi mở temp file, trước
    os.replace) -- file THẬT ở path phải giữ nguyên nội dung CŨ, không bao
    giờ ở trạng thái nửa-ghi hay bị mất."""
    path = tmp_path / "registry.json"
    original = {"k1": {"status": "uploaded"}}
    rl.mark_production_entry()
    rl.write_registry_atomic(path, original, production_root=tmp_path)
    original_bytes = path.read_bytes()

    def _boom(*a, **kw):
        raise OSError("simulated crash mid-write (disk full / killed)")

    monkeypatch.setattr(os, "replace", _boom)
    with pytest.raises(OSError, match="simulated crash"):
        rl.write_registry_atomic(path, {"k1": {"status": "CORRUPTED_ATTEMPT"}}, production_root=tmp_path)
    assert path.read_bytes() == original_bytes, "real file must be byte-identical to before the failed write"


def test_write_registry_atomic_fsyncs_before_replace(tmp_path, monkeypatch):
    """Xác nhận os.fsync() THẬT được gọi trước os.replace() -- không chỉ
    write buffer rồi close, dễ mất dữ liệu nếu OS crash ngay sau close. Sau
    G1 review vòng 1 finding Low #3, còn có 1 lần fsync thư mục SAU replace
    (best-effort durability cho chính thao tác rename) -- thứ tự đúng là
    fsync(file) -> replace -> fsync(dir)."""
    path = tmp_path / "registry.json"
    calls = []
    real_fsync = os.fsync
    real_replace = os.replace

    def _track_fsync(fd):
        calls.append("fsync")
        return real_fsync(fd)

    def _track_replace(src, dst):
        calls.append("replace")
        return real_replace(src, dst)

    monkeypatch.setattr(os, "fsync", _track_fsync)
    monkeypatch.setattr(os, "replace", _track_replace)
    rl.mark_production_entry()
    rl.write_registry_atomic(path, {"k": {"status": "x"}}, production_root=tmp_path)
    assert calls == ["fsync", "replace", "fsync"], "file must be fsynced before replace, dir fsynced after"


def test_write_registry_atomic_cleans_up_stray_tmp_file_on_replace_failure(tmp_path, monkeypatch):
    """G1 review vòng 1, finding Low #3: nếu os.replace() lỗi giữa chừng,
    file .tmp-* KHÔNG được để lại mồ côi trên đĩa."""
    path = tmp_path / "registry.json"
    rl.mark_production_entry()
    rl.write_registry_atomic(path, {"k": {"status": "seed"}}, production_root=tmp_path)

    def _boom(*a, **kw):
        raise OSError("simulated replace failure")

    monkeypatch.setattr(os, "replace", _boom)
    with pytest.raises(OSError, match="simulated replace failure"):
        rl.write_registry_atomic(path, {"k": {"status": "new"}}, production_root=tmp_path)
    leftovers = [p for p in tmp_path.iterdir() if p.name.startswith(".registry.json.tmp-")]
    assert leftovers == [], f"must not leave stray temp files behind on failure, found: {leftovers}"


# ─── write guard: mark_production_entry() / RegistryWriteBlocked ───────

def test_write_blocked_outside_production_tree_without_marker(tmp_path, monkeypatch):
    monkeypatch.delenv(rl._PRODUCTION_ENTRY_ENV, raising=False)
    path = tmp_path / "output" / "shorts" / "Test" / "registry.json"
    with pytest.raises(rl.RegistryWriteBlocked, match="mark_production_entry"):
        rl.write_registry_atomic(path, {"k": {"status": "x"}}, production_root=tmp_path)
    assert not path.exists(), "blocked write must never touch disk"


def test_write_allowed_outside_production_tree_when_marked(tmp_path, monkeypatch):
    monkeypatch.setenv(rl._PRODUCTION_ENTRY_ENV, "1")
    path = tmp_path / "output" / "shorts" / "Test" / "registry.json"
    rl.write_registry_atomic(path, {"k": {"status": "x"}}, production_root=tmp_path)
    assert path.exists()


def test_write_allowed_when_path_outside_production_root_regardless_of_marker(tmp_path, monkeypatch):
    """Path KHÔNG nằm trong production_root (vd tmp_path của 1 test khác,
    không monkeypatch _REGISTRY_PRODUCTION_ROOT sang chính production_root
    này) -- luôn cho phép, dù marker chưa set. Đây chính là lý do TOÀN BỘ
    test hiện có (monkeypatch _registry_path sang tmp_path riêng, KHÔNG
    đụng _REGISTRY_PRODUCTION_ROOT) vẫn chạy được mà không cần sửa gì."""
    monkeypatch.delenv(rl._PRODUCTION_ENTRY_ENV, raising=False)
    other_root = tmp_path / "totally_different_root"
    path = tmp_path / "some_other_tmp_dir" / "registry.json"
    rl.write_registry_atomic(path, {"k": {"status": "x"}}, production_root=other_root)
    assert path.exists()


def test_mark_production_entry_sets_env_var(monkeypatch):
    monkeypatch.delenv(rl._PRODUCTION_ENTRY_ENV, raising=False)
    assert os.environ.get(rl._PRODUCTION_ENTRY_ENV) != "1"
    rl.mark_production_entry()
    assert os.environ.get(rl._PRODUCTION_ENTRY_ENV) == "1"


# ─── read_registry_safe(): fail-closed read + backup recovery ──────────

def test_read_registry_safe_missing_file_returns_empty_dict(tmp_path):
    assert rl.read_registry_safe(tmp_path / "does_not_exist.json") == {}


def test_read_registry_safe_valid_file_roundtrips(tmp_path):
    path = tmp_path / "registry.json"
    data = {"k": {"status": "uploaded"}}
    path.write_text(json.dumps(data), encoding="utf-8")
    assert rl.read_registry_safe(path) == data


def test_read_registry_safe_corrupt_json_no_backup_raises(tmp_path):
    path = tmp_path / "registry.json"
    path.write_text("{not valid json!!!", encoding="utf-8")
    with pytest.raises(rl.RegistryValidationError, match="hỏng/sai schema"):
        rl.read_registry_safe(path)


def test_read_registry_safe_bad_schema_no_backup_raises(tmp_path):
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")
    with pytest.raises(rl.RegistryValidationError):
        rl.read_registry_safe(path)


def test_read_registry_safe_recovers_from_backup_when_primary_corrupt(tmp_path, monkeypatch):
    path = tmp_path / "registry.json"
    good = {"EP001": {"status": "uploaded"}}
    monkeypatch.setenv(rl._PRODUCTION_ENTRY_ENV, "1")
    rl.write_registry_atomic(path, good, production_root=tmp_path)  # creates a valid backup on the SECOND write
    rl.write_registry_atomic(path, {"EP001": {"status": "uploaded"}, "EP002": {"status": "assets_ready"}},
                              production_root=tmp_path)
    # corrupt the primary file directly (simulating disk corruption / bad manual edit)
    path.write_text("{{{ corrupted", encoding="utf-8")
    recovered = rl.read_registry_safe(path)
    assert recovered == good, "must recover the most recent VALID backup, not lose data or crash"


def test_read_registry_safe_skips_corrupt_newest_backup_and_uses_older_valid_one(tmp_path, monkeypatch):
    """G1 (Codex review vòng 1, finding Medium #1): nếu backup MỚI NHẤT
    cũng hỏng (vd chính đĩa bị lỗi 2 lần liên tiếp) nhưng 1 backup CŨ HƠN
    vẫn hợp lệ, phải phục hồi được từ bản cũ hơn đó, không được raise ngay
    sau khi thử đúng 1 backup."""
    path = tmp_path / "registry.json"
    monkeypatch.setenv(rl._PRODUCTION_ENTRY_ENV, "1")
    older_good = {"k": {"status": "v1"}}
    rl.write_registry_atomic(path, older_good, production_root=tmp_path)
    rl.write_registry_atomic(path, {"k": {"status": "v2"}}, production_root=tmp_path)  # rotates v1 into backups
    rl.write_registry_atomic(path, {"k": {"status": "v3"}}, production_root=tmp_path)  # rotates v2 into backups

    backups = rl._backups_newest_first(path)
    assert len(backups) >= 2, "need at least 2 backups for this test to be meaningful"
    newest_backup = backups[0]
    newest_backup.write_text("{{{ corrupted newest backup", encoding="utf-8")  # simulate disk corruption
    path.write_text("{{{ also corrupted primary", encoding="utf-8")

    recovered = rl.read_registry_safe(path)
    assert recovered["k"]["status"] in ("v1", "v2"), (
        f"must fall through to an OLDER valid backup when the newest is also corrupt, got {recovered}"
    )


def test_read_registry_safe_never_returns_corrupt_data_silently(tmp_path, monkeypatch):
    """Không có backup nào -- PHẢI raise, không được âm thầm trả {} hay
    dữ liệu 1 phần (fail-closed thật sự, không phải fail-open-với-{})."""
    path = tmp_path / "registry.json"
    path.write_text('{"k": {"status": "uploaded"}, "trailing":', encoding="utf-8")  # truncated JSON
    with pytest.raises(rl.RegistryValidationError):
        rl.read_registry_safe(path)


# ─── backup rotation ─────────────────────────────────────────────────────

def test_backup_filenames_do_not_collide_even_with_frozen_clock(tmp_path, monkeypatch):
    """Single-process case: đóng băng time.time()/time.gmtime() rồi ghi 3
    lần LIÊN TIẾP (không đồng thời) vào CÙNG registry, TRONG CÙNG 1 tiến
    trình python này. Xác nhận cả 3 bản backup THẬT SỰ tồn tại riêng biệt
    trên đĩa. (Xem test_backup_filenames_do_not_collide_across_processes
    ngay dưới cho trường hợp ĐA tiến trình -- Codex review G1 vòng 2 phát
    hiện bản vá vòng 1 (bộ đếm per-process) chỉ đúng cho case single-process
    này, KHÔNG đúng khi 2 tiến trình python THẬT GIỐNG NHAU ghi liên tiếp.)"""
    import time as time_module

    path = tmp_path / "registry.json"
    monkeypatch.setenv(rl._PRODUCTION_ENTRY_ENV, "1")
    frozen = 1700000000.123
    monkeypatch.setattr(time_module, "time", lambda: frozen)
    monkeypatch.setattr(time_module, "gmtime", lambda *a: time_module.struct_time((2023, 11, 14, 22, 13, 20, 1, 318, 0)))

    rl.write_registry_atomic(path, {"k": {"status": "v0"}}, production_root=tmp_path)
    rl.write_registry_atomic(path, {"k": {"status": "v1"}}, production_root=tmp_path)
    rl.write_registry_atomic(path, {"k": {"status": "v2"}}, production_root=tmp_path)

    backups = rl._backups_newest_first(path)
    assert len(backups) == 2, f"2 prior versions (v0, v1) should each have their own backup file, got {len(backups)}: {backups}"
    contents = {json.loads(b.read_text(encoding='utf-8'))['k']['status'] for b in backups}
    assert contents == {"v0", "v1"}, f"both distinct prior versions must be preserved, not collapsed into one, got {contents}"


def test_backup_filenames_do_not_collide_across_processes(tmp_path):
    """G1 (Codex review vòng 2, finding Medium #1): tái hiện ĐÚNG kịch bản
    Codex đã dùng để tìm ra bug -- 2 tiến trình python THẬT (không phải mô
    phỏng trong cùng 1 process), mỗi tiến trình có time.time() đóng băng
    CÙNG 1 giá trị và bộ đếm process-local RIÊNG BẮT ĐẦU LẠI TỪ ĐẦU, ghi
    LIÊN TIẾP (tiến trình 2 chỉ chạy sau khi tiến trình 1 đã xong hẳn -- vẫn
    tuần tự đúng như FileLock đảm bảo, không phải chạy song song) vào CÙNG
    1 registry. Bản vá dùng _backup_seq per-process (vòng 1) sẽ làm tiến
    trình 2 ghi đè MẤT backup của tiến trình 1 (Codex xác nhận qua repro
    thật). Bản vá _next_generation() (đọc/ghi số nguyên trên ĐĨA, không
    phải bộ nhớ process) phải giữ được cả 2 bản backup."""
    script = """
import sys, os
sys.path.insert(0, {project_root!r})
import registry_lock as rl
rl.time.time = lambda: 1700000000.123
rl.time.gmtime = lambda *a: rl.time.struct_time((2023, 11, 14, 22, 13, 20, 1, 318, 0))
os.environ["{env_var}"] = "1"
from pathlib import Path
path = Path(sys.argv[1])
with rl.FileLock(path):
    rl.write_registry_atomic(path, {{"k": {{"status": sys.argv[2]}}}}, production_root=path.parent)
"""
    script = script.format(project_root=PROJECT_ROOT, env_var=rl._PRODUCTION_ENTRY_ENV)
    path = tmp_path / "registry.json"

    for version in ("v0", "v1", "v2"):
        result = subprocess.run(
            [sys.executable, "-c", script, str(path), version],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"subprocess for {version} failed: {result.stderr}"

    backups = rl._backups_newest_first(path)
    assert len(backups) == 2, (
        f"2 prior versions (v0, v1), each written by a SEPARATE real process, must each keep "
        f"their own backup file -- got {len(backups)}: {backups}"
    )
    contents = {json.loads(b.read_text(encoding='utf-8'))['k']['status'] for b in backups}
    assert contents == {"v0", "v1"}, (
        f"both distinct prior versions from 2 different processes must survive, not collapse "
        f"into one (this is the exact bug Codex found in G1 round 1's per-process counter), "
        f"got {contents}"
    )


def test_backup_generation_recovers_from_missing_gen_file_without_colliding(tmp_path, monkeypatch):
    """G1 (Codex review vòng 3, finding Medium): nếu .gen bị XOÁ MẤT (vd
    đĩa lỗi) trong khi ĐÃ có backup dùng generation cao, lần backup TIẾP
    THEO không được tạo lại generation THẤP (sẽ trùng tên, ghi đè mất
    backup cũ) -- phải tự suy ra sàn đúng từ chính tên các file backup đã
    có trên đĩa."""
    path = tmp_path / "registry.json"
    monkeypatch.setenv(rl._PRODUCTION_ENTRY_ENV, "1")
    rl.write_registry_atomic(path, {"k": {"status": "v0"}}, production_root=tmp_path)
    rl.write_registry_atomic(path, {"k": {"status": "v1"}}, production_root=tmp_path)
    backups_before = rl._backups_newest_first(path)
    assert len(backups_before) == 1  # backup of v0

    (tmp_path / ".registry_backups" / ".gen").unlink()  # simulate .gen loss

    rl.write_registry_atomic(path, {"k": {"status": "v2"}}, production_root=tmp_path)
    backups_after = rl._backups_newest_first(path)
    assert len(backups_after) == 2, f"must gain a 3rd distinct generation, not collide with the existing one, got {backups_after}"
    contents = {json.loads(b.read_text(encoding='utf-8'))['k']['status'] for b in backups_after}
    assert contents == {"v0", "v1"}, f"the pre-existing backup (v0) must survive the .gen loss, got {contents}"


def test_backup_generation_recovers_from_corrupt_gen_file_without_colliding(tmp_path, monkeypatch):
    """Cùng kịch bản trên nhưng .gen bị HỎNG (không phải mất hẳn) -- vd nội
    dung rác không parse được thành số nguyên."""
    path = tmp_path / "registry.json"
    monkeypatch.setenv(rl._PRODUCTION_ENTRY_ENV, "1")
    rl.write_registry_atomic(path, {"k": {"status": "v0"}}, production_root=tmp_path)
    rl.write_registry_atomic(path, {"k": {"status": "v1"}}, production_root=tmp_path)

    (tmp_path / ".registry_backups" / ".gen").write_text("not-a-number-garbage", encoding="utf-8")

    rl.write_registry_atomic(path, {"k": {"status": "v2"}}, production_root=tmp_path)
    backups_after = rl._backups_newest_first(path)
    assert len(backups_after) == 2, f"corrupt .gen must not cause a collision with an existing backup, got {backups_after}"
    contents = {json.loads(b.read_text(encoding='utf-8'))['k']['status'] for b in backups_after}
    assert contents == {"v0", "v1"}


def test_backup_never_overwrites_existing_file_even_when_generation_hint_is_wrong(tmp_path, monkeypatch):
    """G1 (Codex review vòng 4): tái hiện ĐÚNG kịch bản Codex dùng để phá
    bản vá vòng 3 -- 1 file backup "lạ" (không phải do code này tạo ra)
    mang generation SỐ LỚN HƠN 12 chữ số (13 chữ số), khiến gợi ý điểm bắt
    đầu tính sai (thấp hơn thực tế); NGAY CẢ KHI ĐÓ, cơ chế O_CREAT|O_EXCL
    phải tự phát hiện đích đã tồn tại và thử số kế tiếp, KHÔNG BAO GIỜ ghi
    đè bất kỳ backup nào đã có, bất kể gợi ý sai thế nào."""
    path = tmp_path / "registry.json"
    monkeypatch.setenv(rl._PRODUCTION_ENTRY_ENV, "1")
    rl.write_registry_atomic(path, {"k": {"status": "v0"}}, production_root=tmp_path)  # no backup yet
    rl.write_registry_atomic(path, {"k": {"status": "v1"}}, production_root=tmp_path)  # backs up v0

    bdir = tmp_path / ".registry_backups"
    # 1 file "lạ" mang generation 13 chữ số -- không đúng định dạng 12 chữ số code này tự tạo,
    # mô phỏng 1 backup thật đã tồn tại mà bộ đếm/gợi ý không biết chắc chắn về.
    (bdir / "registry.9999999999999.20990101T000000.json").write_text(
        json.dumps({"k": {"status": "future_or_foreign"}}), encoding="utf-8"
    )
    (bdir / ".gen").write_text("garbage", encoding="utf-8")  # cũng hỏng luôn, như review vòng 4 làm

    rl.write_registry_atomic(path, {"k": {"status": "v2"}}, production_root=tmp_path)
    rl.write_registry_atomic(path, {"k": {"status": "v3"}}, production_root=tmp_path)

    all_backups = sorted(bdir.glob("registry.*.json"))
    contents = [json.loads(b.read_text(encoding="utf-8"))["k"]["status"] for b in all_backups]
    # v0's backup, the foreign 13-digit file, and v1's and v2's backups must ALL still be present
    # and distinct -- none silently overwritten, regardless of how wrong the generation hint was.
    assert sorted(contents) == sorted(["v0", "future_or_foreign", "v1", "v2"]), (
        f"no backup may ever be silently overwritten, even with a corrupt .gen and a foreign "
        f"high-generation file skewing the hint -- got {contents}"
    )


def test_backup_rotation_keeps_only_last_n(tmp_path, monkeypatch):
    path = tmp_path / "registry.json"
    monkeypatch.setenv(rl._PRODUCTION_ENTRY_ENV, "1")
    monkeypatch.setattr(rl, "_BACKUP_KEEP", 3)
    for i in range(6):
        rl.write_registry_atomic(path, {"k": {"status": f"v{i}"}}, production_root=tmp_path)
    backups = sorted((tmp_path / ".registry_backups").glob("registry.*.json"))
    assert len(backups) == 3, f"expected exactly 3 backups kept, got {len(backups)}"


def test_backup_rotation_does_not_backup_a_corrupt_current_file(tmp_path, monkeypatch):
    """Nếu file HIỆN TẠI trên đĩa đã hỏng trước khi ghi mới, KHÔNG được
    backup bản hỏng đó đè lên lịch sử backup tốt."""
    path = tmp_path / "registry.json"
    monkeypatch.setenv(rl._PRODUCTION_ENTRY_ENV, "1")
    rl.write_registry_atomic(path, {"k": {"status": "good"}}, production_root=tmp_path)
    good_backups_before = list((tmp_path / ".registry_backups").glob("registry.*.json"))
    path.write_text("{{{ corrupted manually", encoding="utf-8")
    rl.write_registry_atomic(path, {"k": {"status": "new_good"}}, production_root=tmp_path)
    backups_after = list((tmp_path / ".registry_backups").glob("registry.*.json"))
    assert len(backups_after) == len(good_backups_before), "corrupt current file must not be backed up"


# ─── concurrent writers (regression -- existing FileLock+merge behavior) ─

def test_concurrent_writes_via_filelock_do_not_lose_updates(tmp_path, monkeypatch):
    """Regression: 2 'tiến trình' (mô phỏng bằng 2 lệnh gọi tuần tự dùng
    CÙNG khoá) ghi 2 key khác nhau -- cả 2 phải còn nguyên sau khi cả 2 đã
    save (đúng hành vi read-modify-write-merge đã có từ trước G1, KHÔNG
    được regress khi thêm atomic write/validation/backup)."""
    path = tmp_path / "registry.json"
    monkeypatch.setenv(rl._PRODUCTION_ENTRY_ENV, "1")

    def save_one_key(key, value):
        with rl.FileLock(path):
            on_disk = rl.read_registry_safe(path)
            on_disk[key] = value
            rl.write_registry_atomic(path, on_disk, production_root=tmp_path)

    save_one_key("proc_a_key", {"status": "uploaded", "owner": "A"})
    save_one_key("proc_b_key", {"status": "uploaded", "owner": "B"})
    final = rl.read_registry_safe(path)
    assert final == {
        "proc_a_key": {"status": "uploaded", "owner": "A"},
        "proc_b_key": {"status": "uploaded", "owner": "B"},
    }, "both processes' keys must survive -- this is the exact bug task #121 fixed, must not regress"


def test_concurrent_writes_real_threads(tmp_path, monkeypatch):
    """Cùng test trên nhưng dùng THREAD thật chạy song song (không chỉ tuần
    tự) để xác nhận FileLock thật sự chặn interleaving ghi hỏng dữ liệu."""
    import threading

    path = tmp_path / "registry.json"
    monkeypatch.setenv(rl._PRODUCTION_ENTRY_ENV, "1")
    rl.write_registry_atomic(path, {}, production_root=tmp_path)
    errors = []

    def worker(n):
        try:
            for i in range(5):
                with rl.FileLock(path):
                    on_disk = rl.read_registry_safe(path)
                    on_disk[f"thread{n}_item{i}"] = {"status": "uploaded"}
                    rl.write_registry_atomic(path, on_disk, production_root=tmp_path)
        except Exception as e:  # pragma: no cover -- surfaced via errors list assertion below
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == [], f"no worker should raise: {errors}"
    final = rl.read_registry_safe(path)
    assert len(final) == 4 * 5, f"expected 20 total entries from 4 threads x 5 writes each, got {len(final)}"
