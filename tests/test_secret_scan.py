"""Test cho scripts/secret_scan.py.

Lý do tồn tại: một scanner hỏng luôn báo "CLEAN" thì tệ hơn là không có
scanner nào -- nó tạo cảm giác an toàn giả ở MỌI phase gate. Các test dưới đây
bơm secret GIẢ (giá trị bịa, cố ý nối chuỗi để chính file test không bị scanner
bắt) và bắt buộc scanner phải phát hiện, đồng thời phải KHÔNG báo động với
placeholder/đọc-từ-env.

Nhóm test `TestRealGitRepo` dựng repo git THẬT trong thư mục tạm (qua biến môi
trường SECRET_SCAN_ROOT) để kiểm tra được các tình huống chỉ xuất hiện khi chạy
thật: index khác working tree, file không đọc được, file nhị phân.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCANNER = REPO_ROOT / "scripts" / "secret_scan.py"


def _load_scanner():
    spec = importlib.util.spec_from_file_location("secret_scan", SCANNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


scanner = _load_scanner()


def _matches(line: str) -> list[str]:
    """Tên các rule khớp một dòng text, sau khi lọc placeholder theo ĐOẠN KHỚP."""
    hits: list[str] = []
    for name, pattern in scanner.TEXT_RULES:
        for match in pattern.finditer(line):
            if scanner.PLACEHOLDER.search(match.group(0)):
                continue
            hits.append(name)
    return hits


# Secret GIẢ -- cấu trúc giống thật để khớp regex, giá trị hoàn toàn bịa.
POSITIVES = [
    ("google_oauth_client_secret", "client_secret=GOCSPX-" + "a1b2c3d4e5f6g7h8i9j0"),
    ("google_api_key", "key: AIza" + "SyD-1234567890abcdefghijklmnopqrstuvw"),
    ("google_refresh_token", "1/" + "/04aB9cDeFgHiJkLmNoPqRsTuVwZ0123456789abcd"),
    ("github_pat", "ghp" + "_1234567890abcdefghijklmnopqrstuvwyzAB"),
    ("openai_key", "sk" + "-1234567890abcdefghijklmnopqrstuvwyzABCD"),
    ("anthropic_key", "sk-ant" + "-api03-abcdefghijklmnopqrstuvwyz"),
    ("slack_token", "xoxb" + "-123456789012-abcdefghijkl"),
    ("aws_access_key", "AKIA" + "IOSFODNN7ABCDEFG"),
    ("private_key_block", "-----BEGIN RSA " + "PRIVATE KEY-----"),
    ("hf_token", "hf" + "_ABCDEFGHIJKLMNOPQRSTUVWYZabcdefghijkl"),
    ("postgres_url_with_password", "postgresql://neondb_owner:np" + "g_S3cr3tPaSsW0rd@ep-x.neon.tech/db"),
]


@pytest.mark.parametrize("rule_name,line", POSITIVES, ids=[p[0] for p in POSITIVES])
def test_scanner_detects_known_secret_shapes(rule_name: str, line: str) -> None:
    assert rule_name in _matches(line), f"rule {rule_name!r} KHÔNG bắt được dòng mẫu"


# Những dòng này xuất hiện thật trong repo/tài liệu và PHẢI không báo động,
# nếu không thì scanner sẽ bị bỏ qua vì quá ồn.
NEGATIVES = [
    'client_secret = os.environ["GOOGLE_CLIENT_SECRET"]',
    'token = os.getenv("GITHUB_TOKEN")',
    "const url = process.env.DATABASE_URL",
    'rclone config update gdrive client_secret="CLIENT_SECRET_CỦA_BẠN"',
    "GITHUB_TOKEN=",
    "CONTENT_TOOL_REPO=https://github.com/<user>/<content-tool-repo>",
    "# HF_TOKEN=hf_...",
    "DATABASE_URL=postgresql://user:<password>@host/db",
    'apiKey: "YOUR_API_KEY_HERE"',
    "raise ContentRepoUnavailableError('Thiếu GITHUB_TOKEN — không thể truy cập repo.')",
    "print('CẢNH BÁO: Codex hết token -- chuyển sang agy.')",
    'PHONG_THUY_CLIENT_SECRET=',
]


@pytest.mark.parametrize("line", NEGATIVES)
def test_scanner_ignores_placeholders_and_env_reads(line: str) -> None:
    assert _matches(line) == [], f"báo động giả trên dòng an toàn: {line!r}"


def test_placeholder_marker_does_not_hide_real_secret() -> None:
    """Regression: allowlist từng dùng `x{3,}` trần, nên secret THẬT chứa "xxx"
    ở giữa bị nuốt im lặng."""
    assert "google_oauth_client_secret" in _matches('s = "GOCSPX-' + 'a1xxxb2c3d4e5f6g7h8i9"')
    assert _matches("HF_TOKEN=hf_xxx") == []
    assert _matches("api_key: sk-xxx") == []


def test_allowlist_word_on_same_line_does_not_hide_real_secret() -> None:
    """Regression (Codex Phase 0 HIGH): trước đây chỉ cần dòng chứa BẤT KỲ chữ
    placeholder nào ("example", "sample", "fake", os.environ...) là cả dòng bị
    bỏ qua -- credential thật đứng cạnh chú thích sẽ lọt."""
    real = "GOCSPX-" + "k9m2p7q4r1s8t5v3w6y0"
    for noisy in (
        f'client_secret = "{real}"  # see example.com for details',
        f'# sample config\nclient_secret = "{real}"'.replace("\n", " ; "),
        f'fake_flag = True; client_secret = "{real}"',
        f'password = os.environ["X"] or "{real}"',
    ):
        assert "google_oauth_client_secret" in _matches(noisy), f"bỏ sót secret trong: {noisy[:60]!r}"


def test_forbidden_credential_paths_are_flagged() -> None:
    for rel in (
        ".youtube_channels/phong_thuy.json",
        ".youtube_oauth_clients.env",
        ".github_integration.env",
        ".env",
        "apps/hub/.env.local",
        ".vercel_token.env",
        ".vercel/project.json",
    ):
        assert scanner.FORBIDDEN_PATHS.match(rel), f"{rel} phải bị chặn khỏi git"


def test_normal_paths_are_not_flagged_as_credential_files() -> None:
    for rel in (".env.example", ".github_integration.env.example", "youtube_auth.py", "docs/a.md"):
        assert not scanner.FORBIDDEN_PATHS.match(rel), f"{rel} bị chặn nhầm"


def test_binary_detection_uses_content_not_extension() -> None:
    """Regression (Codex Phase 0 HIGH): loại file theo đuôi thì SVG/text lạ bị
    bỏ qua hoàn toàn, secret trong đó lọt mọi phase gate."""
    assert scanner.is_binary(b"\x89PNG\r\n\x1a\n\x00\x00binary")
    assert not scanner.is_binary(b'<svg xmlns="http://www.w3.org/2000/svg"></svg>')


def test_scanner_runs_clean_on_current_repo() -> None:
    """Phase gate dựa vào exit code này, nên test luôn chính hợp đồng đó."""
    result = subprocess.run([sys.executable, str(SCANNER)], cwd=REPO_ROOT, capture_output=True, text=True)
    assert result.returncode == 0, f"secret scan FAIL trên repo hiện tại:\n{result.stdout}"
    assert "CLEAN" in result.stdout


class TestRealGitRepo:
    """Dựng repo git thật trong thư mục tạm để kiểm các tình huống runtime."""

    @staticmethod
    def _init_repo(tmp_path: Path) -> Path:
        repo = tmp_path / "repo"
        repo.mkdir()
        for cmd in (
            ["git", "init", "-q"],
            ["git", "config", "user.email", "t@example.com"],
            ["git", "config", "user.name", "t"],
        ):
            subprocess.run(cmd, cwd=repo, check=True, capture_output=True)
        return repo

    @staticmethod
    def _run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        env = {**os.environ, "SECRET_SCAN_ROOT": str(repo)}
        return subprocess.run(
            [sys.executable, str(SCANNER), *args], cwd=repo, capture_output=True, text=True, env=env
        )

    def test_staged_mode_reads_index_not_working_tree(self, tmp_path: Path) -> None:
        """Regression (Codex Phase 0 HIGH): stage bản CÓ secret rồi dọn working
        tree cho sạch -- thứ được commit vẫn dính secret, nên gate phải FAIL.
        Bản cũ đọc working tree nên cho qua."""
        repo = self._init_repo(tmp_path)
        real = "GOCSPX-" + "z3x8c1v6b9n4m7k2j5h0"
        target = repo / "config.py"

        target.write_text(f'client_secret = "{real}"\n', encoding="utf-8")
        subprocess.run(["git", "add", "config.py"], cwd=repo, check=True, capture_output=True)
        # Working tree giờ sạch, nhưng INDEX vẫn giữ secret.
        target.write_text('client_secret = os.environ["X"]\n', encoding="utf-8")

        result = self._run(repo, "--staged")
        assert result.returncode == 1, f"gate cho qua secret nằm trong index:\n{result.stdout}"
        assert "config.py" in result.stdout
        assert real not in result.stdout

    def test_secret_in_svg_is_detected(self, tmp_path: Path) -> None:
        """SVG là text và commit được -- loại theo đuôi file là bỏ sót."""
        repo = self._init_repo(tmp_path)
        real = "AIza" + "SyD-9876543210zyxwvutsrqponmlkjihgf"
        (repo / "logo.svg").write_text(f'<svg><desc>{real}</desc></svg>', encoding="utf-8")
        result = self._run(repo)
        assert result.returncode == 1, f"bỏ sót secret trong SVG:\n{result.stdout}"
        assert "logo.svg" in result.stdout

    def test_secret_embedded_in_binary_is_detected(self, tmp_path: Path) -> None:
        repo = self._init_repo(tmp_path)
        real = ("ghp" + "_abcdefghij1234567890ABCDEFGHIJ098765").encode()
        (repo / "blob.bin").write_bytes(b"\x00\x01\x02" + real + b"\x00trailing")
        result = self._run(repo)
        assert result.returncode == 1, f"bỏ sót secret nhúng trong file nhị phân:\n{result.stdout}"
        assert "blob.bin" in result.stdout

    def test_unreadable_file_fails_closed(self, tmp_path: Path) -> None:
        """Regression (Codex Phase 0 MEDIUM): file committable không đọc được
        từng bị bỏ qua im lặng và scan vẫn báo CLEAN -- đúng chỗ secret nấp."""
        repo = self._init_repo(tmp_path)
        blocked = repo / "locked.txt"
        blocked.write_text("nothing to see", encoding="utf-8")
        blocked.chmod(0o000)
        try:
            result = self._run(repo)
            assert result.returncode == 2, f"phải exit 2 khi không đọc được file:\n{result.stdout}"
            assert "locked.txt" in result.stdout
            assert "SECRET SCAN: CLEAN" not in result.stdout
        finally:
            blocked.chmod(0o644)

    def test_clean_repo_reports_clean(self, tmp_path: Path) -> None:
        repo = self._init_repo(tmp_path)
        (repo / "ok.py").write_text('token = os.getenv("GITHUB_TOKEN")\n', encoding="utf-8")
        result = self._run(repo)
        assert result.returncode == 0, result.stdout
        assert "CLEAN" in result.stdout

    def test_never_prints_matched_values(self, tmp_path: Path) -> None:
        """Bản thân báo cáo không được làm rò secret -- chỉ in file:dòng."""
        repo = self._init_repo(tmp_path)
        real = "GOCSPX-" + "q7r2m9k4t1w6b3n8j5v0"
        (repo / "leak.py").write_text(f'client_secret = "{real}"\n', encoding="utf-8")
        result = self._run(repo)
        assert result.returncode == 1
        assert "leak.py" in result.stdout
        assert real not in result.stdout, "scanner in giá trị secret ra stdout"
        assert real not in result.stderr, "scanner in giá trị secret ra stderr"

    def test_forbidden_credential_file_blocked_even_if_empty(self, tmp_path: Path) -> None:
        repo = self._init_repo(tmp_path)
        (repo / ".env").write_text("", encoding="utf-8")
        result = self._run(repo)
        assert result.returncode == 1
        assert "credential_file_tracked" in result.stdout
