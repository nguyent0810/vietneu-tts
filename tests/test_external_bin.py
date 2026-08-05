"""Regression test cho external_bin.py -- module resolve binary ngoài dùng
chung cho toàn pipeline (git/rclone/codex/node/npx/osascript), viết sau đợt
hardening launchd 04/08 (xem twice_weekly_batch.py + Codex CLI audit trong
lịch sử phiên làm việc). Mục tiêu: đảm bảo resolve_bin() thật sự fail-closed
(raise rõ ràng, không bao giờ âm thầm trả về tên bare) và fallback glob hoạt
động đúng khi shutil.which() không thấy gì (mô phỏng đúng tình huống
launchd).

Round 2 (Codex CLI PR #2 review, BLOCKING trên CI Linux): TỪNG resolve CẢ 6
binary (git/rclone/node/codex/npx/osascript) NGAY LẬP TỨC lúc import module
này -- nghĩa là 1 consumer chỉ cần đúng 1 binary (vd short_health_check.py
chỉ cần osascript) vẫn crash IMPORT nếu BẤT KỲ binary nào khác trong 6 cái
đó thiếu, kể cả binary consumer đó không hề dùng tới. Phát hiện thật trên
CI: chạy Ubuntu (không có rclone, và osascript về bản chất KHÔNG THỂ cài
trên Linux -- binary macOS thuần) khiến collect test_short_health_check.py
(chỉ cần osascript) crash vì RCLONE_BIN resolve TRƯỚC ĐÓ trong cùng module.
Sửa: mỗi get_<tool>_bin() giờ LAZY (resolve + cache đúng 1 lần lúc gọi
THẬT). File test này giờ chia rõ 2 nhóm:
  - Logic cross-platform (resolve_bin(), missing-binary, lazy/import-safety,
    command construction) -- PHẢI chạy được trên Linux CI, không phụ thuộc
    binary thật nào ngoài "sh"/"git" (có sẵn trên mọi CI runner chuẩn).
  - Test cần binary THẬT sự cài trên máy (rclone/node/codex/npx) hoặc cần
    đúng macOS (osascript) -- skip CÓ LÝ DO RÕ RÀNG khi môi trường không
    đáp ứng, không phải blanket exclude cả file."""
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import unittest.mock
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from external_bin import resolve_bin, MissingBinaryError  # noqa: E402


class TestResolveBin(unittest.TestCase):
    """Cross-platform hoàn toàn -- CHỈ dùng "sh" (POSIX chuẩn, có trên mọi
    Linux/macOS CI runner) và binary giả không tồn tại. Không skip gì."""

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
        import os
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


def _run_in_subprocess(code: str, path: str = "/usr/bin:/bin:/usr/sbin:/sbin") -> subprocess.CompletedProcess:
    """Chạy `code` trong 1 process con HOÀN TOÀN cô lập -- PATH tối giản
    (loại /opt/homebrew, ~/.nvm) VÀ HOME trỏ tới thư mục tmp rỗng (loại
    luôn fallback glob dựa vào Path.home(), vd ~/.nvm/versions/node/*,
    ~/.local/bin/agy) -- mô phỏng ĐÚNG 1 máy/CI runner không hề cài
    rclone/node/codex/npx, độc lập với máy đang chạy test THẬT có gì."""
    with tempfile.TemporaryDirectory() as fake_home:
        env = {"PATH": path, "HOME": fake_home}
        return subprocess.run([sys.executable, "-c", code], cwd=str(REPO_ROOT),
                               capture_output=True, text=True, env=env, timeout=30)


class TestLazyResolution(unittest.TestCase):
    """BLOCKING finding round 2 (Codex CLI PR #2 review): import module này
    (hoặc bất kỳ consumer nào transitively kéo theo nó) KHÔNG được resolve
    bất kỳ binary nào -- chỉ get_<tool>_bin() gọi THẬT mới resolve, và chỉ
    đúng binary đó, không phải cả 6 cái. Cross-platform hoàn toàn (không
    cần binary nào ngoài "sh" có sẵn ở PATH tối giản của mọi Unix) -- PHẢI
    chạy được trên Linux CI."""

    def test_import_succeeds_even_when_every_optional_binary_is_unresolvable(self):
        """Đây CHÍNH XÁC là crash thật đã xảy ra trên CI Linux: dưới PATH
        tối giản + HOME rỗng (rclone/node/codex/npx/osascript đều KHÔNG
        resolve được qua PATH lẫn fallback glob) -- import external_bin
        PHẢI vẫn thành công (không giống bản cũ, resolve NGAY 6 binary lúc
        import và crash MissingBinaryError nếu bất kỳ cái nào thiếu)."""
        result = _run_in_subprocess("import external_bin; print('IMPORT_OK')")
        self.assertEqual(result.returncode, 0,
                          f"import phải thành công dù thiếu rclone/node/codex/npx/osascript -- "
                          f"stdout={result.stdout!r} stderr={result.stderr!r}")
        self.assertIn("IMPORT_OK", result.stdout)

    def test_short_health_check_imports_without_rclone(self):
        """LỊCH SỬ: đây chính là bug THẬT khiến CI Linux đỏ (xem PR #2
        review) -- collect test_short_health_check.py crash vì RCLONE_BIN
        resolve ngay lúc import external_bin.py (qua content_seo.py), dù
        short_health_check.py CHỈ cần osascript, không hề dùng rclone.
        PATH tối giản KHÔNG có rclone (git/osascript vẫn có, đều là system
        binary có sẵn trên máy chạy test này) -- import PHẢI thành công."""
        result = _run_in_subprocess("import short_health_check; print('IMPORT_OK')")
        self.assertEqual(result.returncode, 0,
                          f"stdout={result.stdout!r} stderr={result.stderr!r}")
        self.assertIn("IMPORT_OK", result.stdout)

    def test_only_the_binary_actually_called_is_required(self):
        """Kiến trúc: gọi get_git_bin() KHÔNG được kéo theo resolve_bin()
        cho BẤT KỲ binary nào khác (rclone/node/codex/npx/osascript) --
        chứng minh không có coupling ẩn giữa các getter (đúng yêu cầu
        "consumer dùng 1 binary không yêu cầu toàn toolchain"). Dùng spy
        bọc resolve_bin() thật (không mock giả -- git vẫn resolve THẬT,
        chỉ ghi lại binary nào từng được yêu cầu) thay vì dựa vào rclone
        có/không cài trên máy chạy test (rclone's fallback glob pattern
        là đường dẫn TUYỆT ĐỐI cố định /opt/homebrew, không phụ thuộc
        PATH/HOME nên không thể "làm biến mất" bằng cách sửa env)."""
        import external_bin
        external_bin.get_git_bin.cache_clear()
        real_resolve_bin = external_bin.resolve_bin
        requested = []

        def spy(display_name, exe_name, *args, **kwargs):
            requested.append(exe_name)
            return real_resolve_bin(display_name, exe_name, *args, **kwargs)

        with unittest.mock.patch.object(external_bin, "resolve_bin", side_effect=spy):
            git_path = external_bin.get_git_bin()

        self.assertTrue(git_path)
        self.assertEqual(requested, ["git"],
                          f"get_git_bin() không được resolve binary nào khác ngoài git: {requested}")

    def test_lazy_getter_caches_result_across_repeated_calls(self):
        """functools.lru_cache -- gọi get_git_bin() nhiều lần chỉ resolve
        THẬT (shutil.which/glob) đúng 1 lần, các lần sau trả về cache."""
        import external_bin
        external_bin.get_git_bin.cache_clear()
        first = external_bin.get_git_bin()
        second = external_bin.get_git_bin()
        self.assertEqual(first, second)
        info = external_bin.get_git_bin.cache_info()
        self.assertEqual(info.hits, 1)
        self.assertEqual(info.misses, 1)


class TestLazyGettersOnThisMachine(unittest.TestCase):
    """Xác nhận get_<tool>_bin() trả về đường dẫn tuyệt đối, tồn tại thật
    -- CHỈ chạy khi binary tương ứng THẬT SỰ có trên máy/CI runner này
    (skip có lý do rõ ràng nếu không, KHÔNG phải lỗi test). get_git_bin()
    không skip -- git là yêu cầu chuẩn của mọi CI runner (actions/checkout
    tự cần nó). osascript skip theo PLATFORM (macOS-only thật sự, không
    tồn tại trên Linux dưới bất kỳ hình thức nào) thay vì theo tool
    presence, đúng phân loại "darwin-only" người dùng yêu cầu."""

    def test_get_git_bin(self):
        path = self._external_bin().get_git_bin()
        self.assertTrue(Path(path).is_absolute())
        self.assertTrue(Path(path).exists())

    @unittest.skipIf(shutil.which("rclone") is None, "rclone chưa cài trên máy/CI này -- không phải lỗi test")
    def test_get_rclone_bin(self):
        path = self._external_bin().get_rclone_bin()
        self.assertTrue(Path(path).is_absolute())
        self.assertTrue(Path(path).exists())

    @unittest.skipIf(shutil.which("node") is None, "node chưa cài trên máy/CI này -- không phải lỗi test")
    def test_get_node_bin(self):
        path = self._external_bin().get_node_bin()
        self.assertTrue(Path(path).is_absolute())
        self.assertTrue(Path(path).exists())

    @unittest.skipIf(shutil.which("node") is None, "node subprocess env cần node để probe version -- không phải lỗi test")
    def test_node_subprocess_env_prepends_node_dir_to_path(self):
        eb = self._external_bin()
        env = eb.node_subprocess_env()
        node_dir = str(Path(eb.get_node_bin()).parent)
        self.assertTrue(env["PATH"].startswith(node_dir))

    @unittest.skipIf(shutil.which("codex") is None, "codex CLI chưa cài trên máy/CI này -- không phải lỗi test")
    def test_get_codex_bin(self):
        path = self._external_bin().get_codex_bin()
        self.assertTrue(Path(path).is_absolute())
        self.assertTrue(Path(path).exists())

    @unittest.skipIf(shutil.which("npx") is None, "npx chưa cài trên máy/CI này -- không phải lỗi test")
    def test_get_npx_bin(self):
        path = self._external_bin().get_npx_bin()
        self.assertTrue(Path(path).is_absolute())
        self.assertTrue(Path(path).exists())

    @unittest.skipUnless(sys.platform == "darwin", "osascript là framework macOS thuần -- không tồn tại trên Linux dưới bất kỳ hình thức nào")
    def test_get_osascript_bin(self):
        path = self._external_bin().get_osascript_bin()
        self.assertTrue(Path(path).is_absolute())
        self.assertTrue(Path(path).exists())

    @staticmethod
    def _external_bin():
        import external_bin
        return external_bin


if __name__ == "__main__":
    unittest.main()
