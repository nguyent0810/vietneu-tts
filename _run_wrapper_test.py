import subprocess
import sys
result = subprocess.run(
    [sys.executable, "/private/tmp/test_short_content_review_wrapper.py"],
    cwd="/Users/nguyenthanhtung/Documents/Local AI/Vietneu-TTS",
    capture_output=True,
    text=True,
)
print(result.stdout, end="")
print(result.stderr, end="", file=sys.stderr)
sys.exit(result.returncode)
