"""Regression test cho external_bin.py -- module resolve binary ngoài dùng
chung cho toàn pipeline (git/rclone/codex/node/npx), viết sau đợt hardening
launchd 04/08 (xem twice_weekly_batch.py + Codex CLI audit trong lịch sử
phiên làm việc). Mục tiêu: đảm bảo resolve_bin() thật sự fail-closed (raise
rõ ràng, không bao giờ âm thầm trả về tên bare) và fallback glob hoạt động
đúng khi shutil.which() không thấy gì (mô phỏng đúng tình huống launchd)."""
import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from external_bin import resolve_bin, MissingBinaryError


class TestResolveBin(unittest.TestCase):
    def test_resolves_via_which_when_on_path(self):
        # "sh" luôn có trên mọi máy Unix -- không phụ thuộc binary ngoài
        # nào có thể vắng mặt khi chạy CI.
        resolved = resolve_bin("shell", "sh")
        self.assertTrue(Path(resolved).is_absolute())
        self.assertTrue(Path(resolved).exists())

    def test_raises_missing_binary_error_when_truly_absent(self):
        # KHÔNG được âm thầm trả về tên bare -- đây chính là bug lớp
        # rclone/codex/node/npx đã gặp thật (subprocess.run(["rclone", ...])
        # crash FileNotFoundError SÂU trong lúc chạy launchd, thay vì báo
        # lỗi rõ ràng sớm lúc resolve).
        with self.assertRaises(MissingBinaryError):
            resolve_bin("khong-ton-tai", "binary-chac-chan-khong-ton-tai-xyz123")

    def test_error_message_includes_install_hint(self):
        try:
            resolve_bin("khong-ton-tai", "binary-chac-chan-khong-ton-tai-xyz123",
                        install_hint="brew install nothing")
            self.fail("Phải raise MissingBinaryError")
        except MissingBinaryError as exc:
            self.assertIn("brew install nothing", str(exc))

    def test_falls_back_to_glob_when_which_fails(self):
        # Mô phỏng ĐÚNG tình huống launchd: shutil.which() không thấy binary
        # (PATH tối giản), nhưng binary thật sự tồn tại ở 1 vị trí cố định
        # đã biết trước (giống rclone ở /opt/homebrew/bin, codex ở thư mục
        # nvm) -- resolve_bin() phải tìm ra qua glob pattern dự phòng.
        sh_path = shutil.which("sh")
        self.assertIsNotNone(sh_path, "cần 'sh' có thật trên máy chạy test")
        resolved = resolve_bin("shell-nhung-gia-lap-khong-thay-qua-which",
                                "binary-khong-co-that-nhung-glob-se-tim-ra",
                                extra_glob_patterns=[sh_path])
        self.assertEqual(resolved, sh_path)

    def test_glob_fallback_picks_highest_semantic_version_not_lexicographic(self):
        # BUG THẬT phát hiện qua Codex CLI review trước khi commit (2 vòng):
        # (1) sort lexicographic (sorted(matches)[-1]) chọn SAI -- "v9.0.0"
        # xếp SAU "v20.0.0" theo string dù v20 mới hơn hẳn; (2) bản sửa đầu
        # dùng mtime cũng bị bác -- mtime "mới cài gần đây" không tương
        # đương "version cao hơn" (vd downgrade). Tạo 2 thư mục kiểu nvm
        # thật (v9.0.0/bin/node, v20.0.0/bin/node), CỐ TÌNH ghi mtime của
        # v9 MỚI HƠN v20 (mô phỏng downgrade) -- resolve_bin() vẫn phải
        # chọn v20 theo version cao hơn, không phải theo mtime hay alphabet.
        with tempfile.TemporaryDirectory() as tmp:
            v9_bin = Path(tmp) / "v9.0.0" / "bin" / "node"
            v20_bin = Path(tmp) / "v20.0.0" / "bin" / "node"
            v9_bin.parent.mkdir(parents=True)
            v20_bin.parent.mkdir(parents=True)
            v9_bin.write_text("x")
            v20_bin.write_text("x")
            newer_time = time.time()
            older_time = newer_time - 3600
            os.utime(v20_bin, (older_time, older_time))  # v20 "cài" TRƯỚC (mtime cũ hơn)
            os.utime(v9_bin, (newer_time, newer_time))   # v9 "cài" SAU (mtime mới hơn, giả lập downgrade)
            resolved = resolve_bin("node-nhieu-version-gia-lap",
                                    "binary-khong-co-that-nhung-glob-se-tim-ra",
                                    extra_glob_patterns=[str(Path(tmp) / "*" / "bin" / "node")])
            self.assertEqual(resolved, str(v20_bin),
                              "Phải chọn version CAO HƠN (v20), không phải mtime mới hơn hay alphabet")

    def test_no_bare_name_ever_returned(self):
        # Bất kể tìm thấy qua which hay qua glob, kết quả PHẢI luôn là
        # đường dẫn tuyệt đối -- không bao giờ là chuỗi tên bare (vốn là
        # đúng bug gốc đã sửa: "return 'codex'" ở bản cũ trước khi có
        # module này).
        resolved = resolve_bin("shell", "sh")
        self.assertNotEqual(resolved, "sh")
        self.assertIn("/", resolved)


class TestResolvedConstants(unittest.TestCase):
    """Xác nhận các hằng số module-level (GIT_BIN/RCLONE_BIN/CODEX_BIN/
    NODE_BIN/NPX_BIN) đã thật sự resolve thành công lúc import module này
    trên MÁY CHẠY TEST -- nếu 1 trong các binary này không cài, import sẽ
    raise MissingBinaryError NGAY (fail-closed đúng như thiết kế), test
    này sẽ tự fail rõ ràng thay vì để lỗi trôi xuống runtime thật."""

    def test_all_resolved_constants_are_absolute_paths(self):
        import external_bin
        for name in ("GIT_BIN", "RCLONE_BIN", "CODEX_BIN", "NODE_BIN", "NPX_BIN"):
            path = getattr(external_bin, name)
            with self.subTest(binary=name):
                self.assertTrue(Path(path).is_absolute(), f"{name}={path} không phải đường dẫn tuyệt đối")
                self.assertTrue(Path(path).exists(), f"{name}={path} không tồn tại trên đĩa")

    def test_node_subprocess_env_prepends_node_dir_to_path(self):
        import external_bin
        env = external_bin.node_subprocess_env()
        node_dir = str(Path(external_bin.NODE_BIN).parent)
        self.assertTrue(env["PATH"].startswith(node_dir))


if __name__ == "__main__":
    unittest.main()
