"""fs_calendar - Thư viện tính toán âm lịch, can chi, tử vi, ngày tốt và hoàng đạo Việt Nam.

Được tách ra từ các kịch bản thực thi và tự động hóa video của Vietneu-TTS (FS / Phong Thủy).
Mọi số liệu tính toán thuần bằng code (amlich, canchi, tuvi_year), tuyệt đối không dùng vnlunar cho thần/trực/nạp âm.
"""

from . import amlich
from . import canchi
from . import tuvi_year
from . import ngaytot
from . import hoangdao_daily

__all__ = [
    "amlich",
    "canchi",
    "tuvi_year",
    "ngaytot",
    "hoangdao_daily",
]
