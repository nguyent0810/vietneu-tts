#!/usr/bin/env python3
"""Quét secret trên đúng tập file mà git SẼ commit (tracked + untracked, đã
trừ .gitignore). Chạy ở mọi phase gate của Content Hub và trước mỗi commit.

    python3 scripts/secret_scan.py            # quét toàn bộ tập committable
    python3 scripts/secret_scan.py --staged   # chỉ file đang staged (pre-commit hook)

Exit 0 = sạch, 1 = có phát hiện, 2 = lỗi chạy / không đọc được file.

Bốn thuộc tính an toàn, mỗi cái từng là một lỗ thật đã bị Codex review bắt:

1. **Không in giá trị khớp.** Chỉ `file:dòng` + tên rule. Nếu không thì chính
   báo cáo quét lại làm rò secret ra log phase gate/CI.
2. **`--staged` đọc blob trong INDEX, không đọc working tree.** Stage một file
   có secret rồi sửa working tree cho sạch thì thứ được commit vẫn là bản có
   secret -- đọc working tree sẽ cho qua.
3. **Placeholder xét trên ĐOẠN KHỚP, không xét cả dòng.** Nếu xét cả dòng thì
   một credential thật nằm cạnh chữ "example"/"sample"/"fake" sẽ bị nuốt.
4. **Nhị phân nhận diện bằng nội dung, không bằng đuôi file.** SVG là text và
   chứa được secret; loại theo đuôi file là bỏ sót. File nhị phân vẫn được quét
   bằng nhóm rule "hình dạng token" và được ĐẾM RA trong báo cáo.

Fail closed: đọc lỗi một file committable nào đó thì exit 2, không báo CLEAN.

Viết bằng Python chứ không phải bash: macOS chỉ có bash 3.2 (không có
`mapfile`), bản bash đầu tiên đã sai âm thầm khi chạy thật.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

# SECRET_SCAN_ROOT chỉ để test trỏ scanner vào repo git tạm -- nhờ đó test
# dựng được tình huống index khác working tree thật sự, thay vì giả lập.
REPO_ROOT = Path(os.environ.get("SECRET_SCAN_ROOT") or Path(__file__).resolve().parent.parent).resolve()

# Rule "hình dạng token": khớp dựa trên tiền tố/cấu trúc đặc thù của nhà cung
# cấp, gần như không phụ thuộc ngữ cảnh -> chạy được cả trên file nhị phân.
TOKEN_SHAPE_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("google_oauth_client_secret", re.compile(r"GOCSPX-[A-Za-z0-9_-]{10,}")),
    ("google_api_key", re.compile(r"AIza[A-Za-z0-9_-]{30,}")),
    ("google_refresh_token", re.compile(r"1//[A-Za-z0-9_-]{30,}")),
    ("github_pat", re.compile(r"\b(?:ghp|gho|ghu|ghs)_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{30,}")),
    ("openai_key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}")),
    ("anthropic_key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private_key_block", re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----")),
    ("hf_token", re.compile(r"\bhf_[A-Za-z0-9]{34,}")),
    ("postgres_url_with_password", re.compile(r"postgres(?:ql)?://[^:/@\s]+:[^@\s]{8,}@[^\s\"']+")),
]

# Rule phụ thuộc ngữ cảnh: chỉ chạy trên file text, vì trên nhị phân sẽ nhiễu.
CONTEXT_RULES: list[tuple[str, re.Pattern[str]]] = [
    (
        "hardcoded_credential_assignment",
        re.compile(
            r"(?i)\b(?:client_secret|refresh_token|access_token|api_key|apikey|secret_key|"
            r"auth_token|password|passwd)\b\s*[:=]\s*[\"'][^\"'\s]{12,}[\"']"
        ),
    ),
]

TEXT_RULES = TOKEN_SHAPE_RULES + CONTEXT_RULES

# Áp lên ĐOẠN KHỚP (không phải cả dòng). Đoạn khớp mà chứa dấu hiệu này thì là
# placeholder/đọc-từ-env, không phải secret thật.
PLACEHOLDER = re.compile(
    r"<[^>]*>|YOUR_|CỦA_BẠN|EXAMPLE|example\.com|placeholder|REDACTED|"
    r"\bfake\b|\bdummy\b|\bsample\b|\bchangeme\b|\btest_?only\b|"
    r"[=:_\-/]x{3,}\b|\.\.\.|\$\{|\$[A-Z_]{2,}|"
    r"os\.environ|os\.getenv|process\.env|getenv\(",
    re.IGNORECASE,
)

SKIP_PREFIXES = ("content_repo_clone/", "video_tool_clone/", "youtube_manager_clone/", "node_modules/")

# File credential thật -- tuyệt đối không được nằm trong tập git theo dõi.
FORBIDDEN_PATHS = re.compile(
    r"^(?:\.youtube_channels/|\.youtube_oauth_clients\.env$|\.github_integration\.env$|"
    r"\.env$|\.env\.local$|.*/\.env$|.*/\.env\.local$)"
)

BINARY_SNIFF_BYTES = 8192


def git_files(staged: bool) -> list[str]:
    cmd = (
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"]
        if staged
        else ["git", "ls-files", "-co", "--exclude-standard"]
    )
    out = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    return [line for line in out.stdout.splitlines() if line.strip()]


def read_candidate(rel: str, staged: bool) -> bytes:
    """Đọc nội dung SẼ được commit.

    Ở chế độ --staged phải đọc blob trong index (`git show :path`) chứ không
    phải file trên đĩa: nếu stage bản có secret rồi sửa working tree cho sạch,
    đọc working tree sẽ cho qua trong khi bản được commit vẫn dính secret.
    """
    if staged:
        result = subprocess.run(
            ["git", "show", f":{rel}"], cwd=REPO_ROOT, capture_output=True, check=True
        )
        return result.stdout
    return (REPO_ROOT / rel).read_bytes()


def is_binary(blob: bytes) -> bool:
    return b"\x00" in blob[:BINARY_SNIFF_BYTES]


def scan_blob(rel: str, blob: bytes) -> tuple[list[str], bool]:
    """Trả về (findings, đã_coi_là_nhị_phân)."""
    findings: list[str] = []
    binary = is_binary(blob)

    if binary:
        # Chỉ chạy nhóm rule hình dạng token; giải mã latin-1 để không mất byte.
        text = blob.decode("latin-1")
        for name, pattern in TOKEN_SHAPE_RULES:
            for match in pattern.finditer(text):
                if PLACEHOLDER.search(match.group(0)):
                    continue
                findings.append(f"SECRET[{name}] {rel}:<nội dung nhị phân>")
        return findings, True

    text = blob.decode("utf-8", errors="replace")
    for lineno, line in enumerate(text.splitlines(), start=1):
        for name, pattern in TEXT_RULES:
            for match in pattern.finditer(line):
                # Xét placeholder trên ĐOẠN KHỚP, không trên cả dòng: nếu xét cả
                # dòng thì secret thật nằm cạnh chữ "example" sẽ bị bỏ sót.
                if PLACEHOLDER.search(match.group(0)):
                    continue
                findings.append(f"SECRET[{name}] {rel}:{lineno}")
    return findings, False


def main() -> int:
    staged = "--staged" in sys.argv
    try:
        candidates = git_files(staged)
    except subprocess.CalledProcessError as exc:
        print(f"SECRET SCAN: lỗi gọi git: {exc}", file=sys.stderr)
        return 2

    findings: list[str] = []
    unreadable: list[str] = []
    scanned = 0
    binary_scanned = 0

    for rel in candidates:
        if rel.startswith(SKIP_PREFIXES):
            continue
        if FORBIDDEN_PATHS.match(rel):
            findings.append(f"SECRET[credential_file_tracked] {rel}  <-- file credential bị git theo dõi")
            continue
        if not staged and not (REPO_ROOT / rel).is_file():
            continue  # symlink hỏng / thư mục submodule

        try:
            blob = read_candidate(rel, staged)
        except (OSError, subprocess.CalledProcessError) as exc:
            # Fail closed: một file committable không đọc được thì KHÔNG được
            # phép báo CLEAN -- đó đúng là chỗ secret có thể nấp.
            unreadable.append(f"{rel} ({type(exc).__name__})")
            continue

        file_findings, was_binary = scan_blob(rel, blob)
        findings.extend(file_findings)
        scanned += 1
        if was_binary:
            binary_scanned += 1

    for f in findings:
        print(f)

    if unreadable:
        print("---")
        print(f"SECRET SCAN: ERROR — {len(unreadable)} file committable không đọc được:")
        for u in unreadable:
            print(f"  {u}")
        print("Không kết luận CLEAN khi còn file chưa kiểm tra được.")
        return 2

    print("---")
    text_scanned = scanned - binary_scanned
    if findings:
        print(f"SECRET SCAN: FAIL — {len(findings)} phát hiện trên {scanned} file.")
        print("Không in giá trị khớp. Mở đúng file:dòng ở trên để xử lý.")
        return 1
    print(
        f"SECRET SCAN: CLEAN — 0 phát hiện trên {scanned} file "
        f"({text_scanned} text, {binary_scanned} nhị phân quét bằng rule hình dạng token)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
