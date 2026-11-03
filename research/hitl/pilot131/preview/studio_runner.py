"""Gọi studio.py y nguyên, chỉ nâng timeout bước `hyperframes render` (mặc định 1800 s) cho Oracle 2 OCPU.
Không sửa code production; phát hiện này ghi vào báo cáo pilot #131."""
import sys
sys.path.insert(0, "/home/ubuntu/vietneu-tts")
import studio  # noqa: E402

_orig = studio.hf


def hf(job, args, timeout=1800):
    if args.startswith("render "):
        timeout = max(timeout, 4 * 3600)
    return _orig(job, args, timeout=timeout)


studio.hf = hf
sys.argv = ["studio.py"] + sys.argv[1:]
sys.exit(studio.main())
