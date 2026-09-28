# VieNeu-TTS Testing Directory

This directory contains test suites and utilities for verifying the VieNeu-TTS package.

## How to run tests

Ensure you are in the project root:

```bash
uv run pytest
```

This will automatically discover and run all test suites in the `tests/` directory.

### Windows và nhóm test `unix_lock`

Một phần code production dùng khoá chỉ có trên Unix (`fcntl`, qua `registry_lock`, `rotation_state`...). Các module test cần `fcntl` (trực tiếp hay gián tiếp) được liệt kê **tường minh** trong `UNIX_LOCK_TEST_MODULES` ở `conftest.py` và mang marker `unix_lock`:

- `pytest -m unix_lock` chọn đúng nhóm này; `pytest -m "not unix_lock"` chạy phần còn lại.
- Trên máy không có `fcntl` (Windows), chỉ các module trong danh sách được **skip** với cùng một lý do ("cần khoá chỉ có trên Unix (fcntl)…"). Chạy `pytest -rs` để xem. Module ngoài danh sách mà lỗi `fcntl` vẫn là lỗi thật.
- Viết test mới cần `fcntl` thì thêm file vào `UNIX_LOCK_TEST_MODULES`. `test_unix_lock_list_complete.py` giả lập máy không có `fcntl` và FAIL nếu một module test cần `fcntl` lúc import mà chưa có trong danh sách (chạy cả trên CI Ubuntu).

Binary giả cho `external_bin` (codex/npx/node/rclone/osascript/git) mặc định bật trên Windows; nơi khác chỉ bật khi đặt `VIETNEU_TEST_STUB_BINARIES=1` (CI của nhánh `feat/**` đặt; job `main` không đặt nên giữ nguyên hành vi cũ). Đặt `=0` để tắt. Chỉ binary thiếu trên PATH mới được thay; stub chỉ trả lời `--version`, gọi thật thoát mã 127. Khi stub bật, `TestResolvedConstants` (kiểm binary thật đã cài) bị skip có lý do.

Nhóm `unix_lock` chạy trên CI Ubuntu (mọi push lên `main` và `feat/**`) hoặc trong container Linux. Máy dev có Docker (không cần WSL distro). Git Bash:

```bash
docker run --rm -e UV_PROJECT_ENVIRONMENT=/tmp/venv -e VIRTUAL_ENV=/tmp/venv -e VIETNEU_TEST_STUB_BINARIES=1 -v "$PWD":/src -w /src ghcr.io/astral-sh/uv:python3.12-bookworm sh -c "uv sync --group dev && uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu && uv run pytest -q"
```

PowerShell (đường dẫn có dấu cách nên phải để trong ngoặc kép):

```powershell
docker run --rm -e UV_PROJECT_ENVIRONMENT=/tmp/venv -e VIRTUAL_ENV=/tmp/venv -e VIETNEU_TEST_STUB_BINARIES=1 -v "${PWD}:/src" -w /src ghcr.io/astral-sh/uv:python3.12-bookworm sh -c "uv sync --group dev && uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu && uv run pytest -q"
```

---

### Individual Test Suites
- **[test_engine_standard.py](test_engine_standard.py)**: Tests for the standard VieNeuTTS engine (Torch/GGUF).
- **[test_engine_remote.py](test_engine_remote.py)**: Tests for the Remote API engine.
- **[test_engine_fast.py](test_engine_fast.py)**: Tests for the Fast (LMDeploy) engine.
- **[test_factory.py](test_factory.py)**: Tests for the Vieneu factory class.
- **[test_utils.py](test_utils.py)**: Tests for audio and text processing utilities.

---

### Other Utilities
- **[benchmark.py](benchmark.py)**: RTF and latency benchmarking.
