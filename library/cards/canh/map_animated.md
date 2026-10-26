---
{
  "id": "map_animated",
  "ten": "Bản đồ động",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "giai_thich",
    "tra_cuu",
    "van_hoa"
  ],
  "cam_ngach": [],
  "so_muc": 24,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "engine",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [
    "output/cl_staging/hyperframes_oct/plan_o05.json",
    "output/cl_staging/hyperframes_sept/plan_d29.json"
  ],
  "vi_du": [
    "https://x.com/guguimuzzio/status/2104665953883615408",
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/casemap.html"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/casemap.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Bản đồ giữ địa lý làm nền rồi lần lượt bật tuyến/vùng; casemap dùng đường biên và marker theo lớp.

## Khi nào dùng

Short giải thích một tuyến; Long lần theo nhiều địa điểm. Không nên dùng: Không xác định được vị trí hoặc ranh giới nguồn không đáng tin.

## Cách dựng trong HyperFrames

Nhánh dựng cho map animated nằm tại `hyperframes_short/compositions/casemap.html:1`; caller hoặc phần cấu hình tương ứng ở `hyperframes_bridge.py:700`.

visual type `map`; truyền GeoJSON/điểm tuyến rồi `hf_geo.bake()` trước render.

## Rủi ro

Marker sai hệ tọa độ đặt nhầm nơi; polygon rỗng khiến bridge không bake được.
