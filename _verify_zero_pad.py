import sys
sys.path.insert(0, "src")
from vieneu_utils.phonemize_text import _fix_zero_padded_numbers, PuncNormalizer

cases = [
    "mã 012",
    "điện thoại 090 123 4567",
    "090 123 4567",
    "không quá 03 năm",
    "từ 01 đến 05 năm",
    "ngày 05 tháng 3",
    "phạt tiền từ 05 đến 50 triệu đồng",
    "phạt 05 triệu đồng",  # money without đến
    "gọi 090 đến 091",  # phone range with đến - potential FP
    "từ 08 đến 17 giờ",
    "lúc 09 giờ",
    "05 vụ",
    "09 tuổi",
    "02 bị cáo",
    "03 lần",
    "tháng 01/2024",
    "lúc 09:30",
    "điều 007 luật hình sự",
]

print("=== regex only ===")
for c in cases:
    out = _fix_zero_padded_numbers(c)
    flag = "CHANGED" if out != c else "same"
    print(f"[{flag}] {c!r} -> {out!r}")

print("\n=== PuncNormalizer / sea_g2p ===")
try:
    n = PuncNormalizer()
    e2e = [
        "mã 012",
        "điện thoại 090 123 4567",
        "từ 01 đến 05 năm",
        "không quá 03 năm",
        "gọi 090 đến 091",
        "phạt 05 triệu đồng",
        "lúc 09 giờ",
    ]
    for c in e2e:
        out = n.normalize(c, punc_norm=False)
        print(f"{c!r}\n  -> {out!r}")
except Exception as e:
    print("Normalizer failed:", type(e).__name__, e)

# also run pytest
import subprocess
r = subprocess.run([sys.executable, "-m", "pytest", "tests/test_phonemize_text_zero_pad.py", "-q", "--tb=line"], capture_output=True, text=True)
print("\n=== pytest ===")
print(r.stdout)
print(r.stderr)
print("exit", r.returncode)
