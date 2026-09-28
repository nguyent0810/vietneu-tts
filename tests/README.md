# VieNeu-TTS Testing Directory

This directory contains test suites and utilities for verifying the VieNeu-TTS package.

## How to run tests

Ensure you are in the project root:

```bash
uv run pytest
```

This will automatically discover and run all test suites in the `tests/` directory.

### Windows và nhóm test `unix_lock`

Một phần code production dùng khoá chỉ có trên Unix (`fcntl`, qua `registry_lock`, `rotation_state`...). Trên máy không có `fcntl` (Windows):

- Module test import code cần `fcntl` được **skip** với cùng một lý do ("cần khoá chỉ có trên Unix (fcntl)…"), không còn lỗi collection. Chạy `pytest -rs` để xem danh sách.
- Test lỗi lúc chạy vì code production import `fcntl` trễ (trong hàm) cũng được skip tự động với cùng lý do.
- Test cần khoá nhưng không lỗi import (vd kiểm tra hành vi khoá) thì gắn `@pytest.mark.unix_lock`.
- Binary giả chỉ trả lời `--version`; gọi thật sẽ thoát mã 127, nên không test nào "thành công" giả nhờ stub.
- `conftest.py` ở gốc repo thêm binary giả cho codex/npx/node/rclone/osascript/git **chỉ khi máy thiếu**, vì `external_bin` resolve chúng ngay lúc import. Test không bao giờ chạy binary thật.

Nhóm `unix_lock` chạy trên CI Ubuntu (mọi push lên `main` và `feat/**`) hoặc trong container Linux. Máy dev có Docker (không cần WSL distro):

```bash
docker run --rm -e UV_PROJECT_ENVIRONMENT=/tmp/venv -e VIRTUAL_ENV=/tmp/venv -v "$PWD":/src -w /src ghcr.io/astral-sh/uv:python3.12-bookworm sh -c "uv sync --group dev && uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu && uv run pytest -q"
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
