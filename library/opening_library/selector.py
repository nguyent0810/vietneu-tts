"""selector.py — Bộ chọn cảnh mở đầu (Opening Selector) cho Ticket #54.
[CÔNG CỤ TUỲ CHỌN — KHÔNG GỌI TỰ ĐỘNG TRONG RUNTIME / PIPELINE (PO DUYỆT 05/11, AUDIT #140)]

Chỉ để gợi ý cold open khi viết plan; hook vẫn do người duyệt.
Chạy tham khảo trước bộ chọn cảnh #51 (scene_picker.py) để gợi ý cảnh 5–15 giây đầu tiên.
Thứ tự xét:
1. Khớp nội dung câu hook (hook_type)
2. Đủ dữ liệu/tài sản (số liệu, tọa độ, ảnh)
3. Hợp phong cách kênh (priority_patterns, cấm forbidden_patterns)
4. Không trùng mẫu gần đây (recent_history)
5. Đạt QA kiểm soát rủi ro
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE = Path(__file__).parent
SHARED = BASE / "shared"
PROFILES = BASE / "profiles"


class OpeningSelector:
    def __init__(self, channel: str):
        self.channel = channel
        self.profile = self._load_profile(channel)
        self.patterns = self._load_patterns()

    def _load_profile(self, ch: str) -> dict:
        pf = PROFILES / f"{ch}.json"
        if not pf.exists():
            return {
                "channel": ch,
                "priority_patterns": ["mystery_reveal", "before_after", "shocking_number"],
                "forbidden_patterns": [],
                "tone_rules": ""
            }
        return json.loads(pf.read_text(encoding="utf-8"))

    def _load_patterns(self) -> dict:
        pats = {}
        for f in SHARED.glob("*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            pats[data["id"]] = data
        return pats

    def select_opening(
        self,
        hook_text: str,
        hook_type: str,
        available_assets: dict,
        recent_patterns: list[str] | None = None
    ) -> dict:
        recent = recent_patterns or []
        candidates = []

        # 1. Lọc theo cấm của kênh
        forbidden = set(self.profile.get("forbidden_patterns", []))

        # 2. Xếp hạng ứng viên
        for pid, pat in self.patterns.items():
            if pid in forbidden:
                continue

            score = 0
            # Khớp loại hook
            if hook_type in pat.get("hook_types_compatible", []):
                score += 40

            # Ưu tiên theo hồ sơ kênh
            priorities = self.profile.get("priority_patterns", [])
            if pid in priorities:
                idx = priorities.index(pid)
                score += (30 - idx * 5)

            # Kiểm tra đủ tài sản
            min_imgs = pat.get("so_anh_toi_thieu", 0)
            cur_imgs = len(available_assets.get("images", []))
            if cur_imgs < min_imgs:
                # Không đủ ảnh -> loại trừ hoặc phạt nặng
                continue

            # Cấm tuyệt đối chọn lại mẫu vừa dùng gần nhất (chống lặp tuyệt đối)
            if recent and recent[-1] == pid:
                continue
            if len(recent) >= 2 and recent[-2] == pid:
                score -= 30

            # Thưởng nếu có dữ liệu tương thích
            if pid == "shocking_number" and any(char.isdigit() for char in hook_text):
                score += 25
            if pid == "map_dive" and available_assets.get("coordinates"):
                score += 30

            candidates.append((score, pid, pat))

        if not candidates:
            # Fallback an toàn
            fallback_pat = self.patterns.get("mystery_reveal")
            return {
                "selected_pattern": "mystery_reveal",
                "method": "B_hyperframes",
                "reason": "fallback_default",
                "spec": fallback_pat
            }

        candidates.sort(key=lambda x: x[0], reverse=True)
        best_score, best_pid, best_pat = candidates[0]

        return {
            "selected_pattern": best_pid,
            "score": best_score,
            "method": best_pat.get("phuong_thuc_uu_tien", "B_hyperframes"),
            "visual_engine": best_pat.get("visual_engine"),
            "timeline": best_pat.get("timeline"),
            "fallback": best_pat.get("fallback"),
            "qa_gates": best_pat.get("qa_gates")
        }


if __name__ == "__main__":
    sel_fs = OpeningSelector("fs")
    res_fs = sel_fs.select_opening(
        hook_text="Bước sang năm 2027, lịch âm có 354 ngày",
        hook_type="so_thoi_gian",
        available_assets={"images": []},
        recent_patterns=["before_after"]
    )
    print("FS Selection:", res_fs["selected_pattern"], "Score:", res_fs["score"], "Method:", res_fs["method"])

    sel_bud = OpeningSelector("bud")
    res_bud = sel_bud.select_opening(
        hook_text="Bên dưới pho tượng cổ phủ bóng thời gian",
        hook_type="to_mo",
        available_assets={"images": ["tượng"]},
        recent_patterns=[]
    )
    print("BUD Selection:", res_bud["selected_pattern"], "Score:", res_bud["score"], "Method:", res_bud["method"])

    sel_ls = OpeningSelector("lich_su")
    res_ls = sel_ls.select_opening(
        hook_text="Tại dải đất hẹp Lũy Thầy Quảng Bình",
        hook_type="dia_danh",
        available_assets={"images": [], "coordinates": (106.6, 17.47)},
        recent_patterns=[]
    )
    print("Lịch Sử Selection:", res_ls["selected_pattern"], "Score:", res_ls["score"], "Method:", res_ls["method"])
