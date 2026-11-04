#!/usr/bin/env python3
"""init_library.py — Khởi tạo và kiểm tra schema 8 mẫu opening_library (Ticket #54)."""
import json
from pathlib import Path

BASE = Path(__file__).parent
SHARED = BASE / "shared"
PROFILES = BASE / "profiles"

PATTERNS = {
    "mystery_reveal": {
        "id": "mystery_reveal",
        "ten": "Lộ diện bí ẩn",
        "phuong_thuc_uu_tien": "C_hybrid",
        "ly_do_phuong_thuc": "Nền Flow tạo không khí huyền bí, khói sương cuộn điện ảnh; HyperFrames vẽ tiêu đề và phụ đề karaoke sắc nét không méo chữ.",
        "hook_types_compatible": ["to_mo", "cau_hoi", "nhay_vao_canh"],
        "so_anh_toi_thieu": 1,
        "timeline": [
            {"t": [0.0, 2.0], "phase": "ambience_shroud", "action": "Khung cảnh mờ tối hoặc phủ sương khói, tiêu đề hook xuất hiện"},
            {"t": [2.0, 5.0], "phase": "slow_reveal", "action": "Camera đẩy vào (push-in), ánh sáng hé lộ một phần chủ thể"},
            {"t": [5.0, 8.0], "phase": "key_focus", "action": "Chạm diện mạo/chi tiết then chốt, audio chạm từ khóa cao trào"}
        ],
        "visual_engine": {
            "hyperframes_visual": "quote",
            "flow_prompt_template": "A cinematic slow camera push-in on {subject} in dark atmospheric {setting}, volumetric soft light slowly reveals details, 4k editorial, photorealistic, no text"
        },
        "typography": {"kicker": True, "title_size": "huge", "wcag_contrast": "AAA"},
        "subtitle_zone": {"safe_zone_y": [880, 1040], "avoid_overlap": True},
        "audio_tts": {"tempo": 1.0, "pause_after_hook": 0.4},
        "duration_limit": {"min_s": 5.0, "max_s": 8.0},
        "fallback": "photo_ken_burns_slow_zoom",
        "qa_gates": ["check_contrast", "check_capzone_overlap", "check_face_integrity"]
    },
    "shocking_number": {
        "id": "shocking_number",
        "ten": "Con số gây sốc",
        "phuong_thuc_uu_tien": "B_hyperframes",
        "ly_do_phuong_thuc": "HyperFrames vẽ số vector và đếm tăng (countup) tất định 100%, đồng bộ theo mili-giây với từ đọc; Flow video vẽ số bị méo và chữ Hán giả.",
        "hook_types_compatible": ["so_thoi_gian", "canh_bao", "cau_hoi"],
        "so_anh_toi_thieu": 0,
        "timeline": [
            {"t": [0.0, 1.5], "phase": "ring_init", "action": "Vòng tiến độ SVG vẽ nét (drawOn), số bắt đầu đếm từ 0"},
            {"t": [1.5, 4.5], "phase": "rapid_countup", "action": "Số đếm tăng nhanh với gia tốc power2.out"},
            {"t": [4.5, 7.0], "phase": "lock_and_pulse", "action": "Khóa số tại giá trị đích, nhãn định danh bật sáng, vòng hào quang mở rộng"}
        ],
        "visual_engine": {
            "hyperframes_visual": "stat",
            "flow_prompt_template": None
        },
        "typography": {"font_weight": "bold", "unit_suffix": True, "wcag_contrast": "AAA"},
        "subtitle_zone": {"safe_zone_y": [880, 1040], "avoid_overlap": True},
        "audio_tts": {"tempo": 1.02, "pause_after_hook": 0.3},
        "duration_limit": {"min_s": 5.0, "max_s": 7.5},
        "fallback": "word_stat_highlight",
        "qa_gates": ["check_number_accuracy_fstring", "check_contrast", "check_capzone_overlap"]
    },
    "map_dive": {
        "id": "map_dive",
        "ten": "Bay lặn bản đồ",
        "phuong_thuc_uu_tien": "B_hyperframes",
        "ly_do_phuong_thuc": "hf_geo nướng TopoJSON chuẩn tọa độ địa lý (kinh vĩ độ thật), không cần mạng; Flow không vẽ được bản đồ hành chính thật và không định vị được điểm lịch sử.",
        "hook_types_compatible": ["dia_danh", "nhay_vao_canh", "so_thoi_gian"],
        "so_anh_toi_thieu": 0,
        "timeline": [
            {"t": [0.0, 2.0], "phase": "macro_view", "action": "Đường biên giới quốc gia vẽ nét trên giấy inkwash"},
            {"t": [2.0, 4.5], "phase": "camera_dive", "action": "Sân khấu phóng to 0.95 -> 1.04 lia về vùng chiến lược"},
            {"t": [4.5, 7.5], "phase": "pin_radar_pulse", "action": "Ghim địa danh cắm xuống kèm vòng radar sóng lan tỏa, thẻ tên và năm lịch sử hiện"}
        ],
        "visual_engine": {
            "hyperframes_visual": "map",
            "flow_prompt_template": None
        },
        "typography": {"card_background": "glass_or_paper", "title_contrast": "AA"},
        "subtitle_zone": {"safe_zone_y": [880, 1040], "avoid_overlap": True},
        "audio_tts": {"tempo": 0.98, "pause_after_hook": 0.4},
        "duration_limit": {"min_s": 6.0, "max_s": 8.5},
        "fallback": "photo_landscape_ken_burns",
        "qa_gates": ["check_geo_bounds", "check_capzone_overlap", "check_title_map_margin"]
    },
    "before_after": {
        "id": "before_after",
        "ten": "Trước và sau",
        "phuong_thuc_uu_tien": "B_hyperframes",
        "ly_do_phuong_thuc": "HyperFrames chia đôi màn hình 3D (visuals.compare) đối xứng hoàn hảo; Flow không đảm bảo góc nhìn tương đồng giữa 2 trạng thái.",
        "hook_types_compatible": ["van_de_giai_phap", "doi_lap", "to_mo"],
        "so_anh_toi_thieu": 2,
        "timeline": [
            {"t": [0.0, 2.0], "phase": "card_left_enter", "action": "Thẻ trạng thái cũ xoay 3D vào từ bên trái"},
            {"t": [2.0, 4.5], "phase": "card_right_enter", "action": "Thẻ trạng thái mới xoay 3D vào đối trọng từ bên phải"},
            {"t": [4.5, 7.0], "phase": "badge_highlight", "action": "Huy hiệu kết quả nảy bật (pop), so sánh 2 mặt"}
        ],
        "visual_engine": {
            "hyperframes_visual": "compare",
            "flow_prompt_template": None
        },
        "typography": {"eyebrow": True, "badge": True, "wcag_contrast": "AA"},
        "subtitle_zone": {"safe_zone_y": [880, 1040], "avoid_overlap": True},
        "audio_tts": {"tempo": 1.0, "pause_after_hook": 0.3},
        "duration_limit": {"min_s": 5.0, "max_s": 8.0},
        "fallback": "wind_text_contrast",
        "qa_gates": ["check_contrast", "check_capzone_overlap"]
    },
    "countdown_deadline": {
        "id": "countdown_deadline",
        "ten": "Đếm ngược thời khắc",
        "phuong_thuc_uu_tien": "B_hyperframes",
        "ly_do_phuong_thuc": "visuals.clock và timeline chạy kim và canh giờ tất định; AI video không thể đồng bộ nhịp kim đồng hồ theo giây audio.",
        "hook_types_compatible": ["so_thoi_gian", "canh_bao", "to_mo"],
        "so_anh_toi_thieu": 0,
        "timeline": [
            {"t": [0.0, 2.0], "phase": "dial_draw", "action": "Mặt đồng hồ 24 giờ / timeline xuất hiện"},
            {"t": [2.0, 5.0], "phase": "hand_rotation", "action": "Kim quét qua các khắc giờ, tô sáng cung canh giờ mục tiêu"},
            {"t": [5.0, 7.5], "phase": "deadline_strike", "action": "Kim chạm điểm giới hạn, thẻ giờ bật sáng"}
        ],
        "visual_engine": {
            "hyperframes_visual": "clock",
            "flow_prompt_template": None
        },
        "typography": {"hour_ticks": True, "chip_label": True, "wcag_contrast": "AAA"},
        "subtitle_zone": {"safe_zone_y": [880, 1040], "avoid_overlap": True},
        "audio_tts": {"tempo": 1.05, "pause_after_hook": 0.25},
        "duration_limit": {"min_s": 5.0, "max_s": 8.0},
        "fallback": "timeline_bar_scrub",
        "qa_gates": ["check_contrast", "check_capzone_overlap"]
    },
    "evidence_reveal": {
        "id": "evidence_reveal",
        "ten": "Trưng bày bằng chứng",
        "phuong_thuc_uu_tien": "C_hybrid",
        "ly_do_phuong_thuc": "Flow video tạo nền bàn gỗ cổ / ánh nến lung linh; HyperFrames render văn bản cổ (doc/annot) và vệt dạ quang highlighter chạy theo lời đọc.",
        "hook_types_compatible": ["to_mo", "nhay_vao_canh", "cau_hoi"],
        "so_anh_toi_thieu": 1,
        "timeline": [
            {"t": [0.0, 2.0], "phase": "document_drop", "action": "Văn bản cổ rơi nhẹ nghiêng góc trên bàn tài liệu"},
            {"t": [2.0, 5.0], "phase": "highlighter_sweep", "action": "Vệt dạ quang màu vàng/đỏ quét theo dòng chữ trích dẫn quan trọng"},
            {"t": [5.0, 8.0], "phase": "annotation_note", "action": "Nét bút phê mực đỏ ghi chú kết luận bên lề"}
        ],
        "visual_engine": {
            "hyperframes_visual": "annot",
            "flow_prompt_template": "An antique wooden desk with candlelight, ink stone and scroll background, warm cinematic lighting, shallow depth of field, 4k"
        },
        "typography": {"handwritten_font": "Charm_or_Caveat", "quote_font": "Cormorant", "wcag_contrast": "AAA"},
        "subtitle_zone": {"safe_zone_y": [880, 1040], "avoid_overlap": True},
        "audio_tts": {"tempo": 0.95, "pause_after_hook": 0.4},
        "duration_limit": {"min_s": 5.5, "max_s": 8.5},
        "fallback": "quote_card_clean",
        "qa_gates": ["check_contrast", "check_capzone_overlap", "check_evidence_authenticity"]
    },
    "chain_reaction": {
        "id": "chain_reaction",
        "ten": "Phản ứng dây chuyền",
        "phuong_thuc_uu_tien": "B_hyperframes",
        "ly_do_phuong_thuc": "Sơ đồ tương sinh tương khắc ngũ hành (chiwheel/cuudieu) đòi hỏi quan hệ mắt xích chính xác tuyệt đối bằng đồ thị vector; AI video chỉ tạo được hiệu ứng hỗn loạn vô nghĩa.",
        "hook_types_compatible": ["canh_bao", "van_de_giai_phap", "to_mo"],
        "so_anh_toi_thieu": 0,
        "timeline": [
            {"t": [0.0, 2.0], "phase": "element_1_trigger", "action": "Nguyên nhân gốc (hành A / sao A) bừng sáng"},
            {"t": [2.0, 4.5], "phase": "energy_flow", "action": "Tia năng lượng vector truyền dọc mũi tên sang mắt xích B"},
            {"t": [4.5, 7.5], "phase": "system_impact", "action": "Toàn bộ đồ hình chuyển động, kích hoạt kết quả chung cuộc"}
        ],
        "visual_engine": {
            "hyperframes_visual": "chiwheel",
            "flow_prompt_template": None
        },
        "typography": {"node_labels": True, "wcag_contrast": "AA"},
        "subtitle_zone": {"safe_zone_y": [880, 1040], "avoid_overlap": True},
        "audio_tts": {"tempo": 1.0, "pause_after_hook": 0.3},
        "duration_limit": {"min_s": 5.5, "max_s": 8.0},
        "fallback": "list_cascade_reveal",
        "qa_gates": ["check_contrast", "check_capzone_overlap"]
    },
    "missing_piece": {
        "id": "missing_piece",
        "ten": "Mảnh ghép còn thiếu",
        "phuong_thuc_uu_tien": "B_hyperframes",
        "ly_do_phuong_thuc": "Ma phương Lạc Thư (luoshu) hoặc Bát quái khuyết hào (hexagram) cần số hoặc hào rơi vào đúng tọa độ lưới; HyperFrames điều khiển pixel chính xác.",
        "hook_types_compatible": ["to_mo", "cau_hoi", "van_de_giai_phap"],
        "so_anh_toi_thieu": 0,
        "timeline": [
            {"t": [0.0, 2.0], "phase": "matrix_display", "action": "Ma trận 3x3 hiện rõ 8 ô, ô trung tâm để trống nhấp nháy"},
            {"t": [2.0, 4.5], "phase": "piece_descent", "action": "Mảnh ghép / con số then chốt từ từ rơi xuống từ trên cao"},
            {"t": [4.5, 7.0], "phase": "lock_and_balance", "action": "Mảnh ghép khóa chặt vị trí, ma phương cân bằng tổng số 15"}
        ],
        "visual_engine": {
            "hyperframes_visual": "luoshu",
            "flow_prompt_template": None
        },
        "typography": {"grid_contrast": "AAA", "highlight_cell": True},
        "subtitle_zone": {"safe_zone_y": [880, 1040], "avoid_overlap": True},
        "audio_tts": {"tempo": 0.98, "pause_after_hook": 0.35},
        "duration_limit": {"min_s": 5.0, "max_s": 7.5},
        "fallback": "lookup_table_cell",
        "qa_gates": ["check_contrast", "check_capzone_overlap"]
    }
}

CHANNEL_PROFILES = {
    "bud": {
        "channel": "bud",
        "name": "Kênh Phật Giáo (BUD)",
        "priority_patterns": ["mystery_reveal", "before_after", "missing_piece"],
        "forbidden_patterns": ["shocking_number"],
        "tone_rules": "Không giật gân, không mê tín, trang nghiêm, tôn trọng Luật 17 về tượng Phật.",
        "flow_quota_per_video": 10
    },
    "fs": {
        "channel": "fs",
        "name": "Kênh Phong Thủy (FS)",
        "priority_patterns": ["shocking_number", "before_after", "mystery_reveal"],
        "forbidden_patterns": [],
        "tone_rules": "Không biến lời dự đoán thành hứa hẹn tiền tài, mọi số tính bằng code, con giáp gọi tên chi.",
        "flow_quota_per_video": 10
    },
    "lich_su": {
        "channel": "lich_su",
        "name": "Kênh Lịch Sử Việt Nam",
        "priority_patterns": ["map_dive", "before_after", "countdown_deadline"],
        "forbidden_patterns": [],
        "tone_rules": "Chuẩn xác địa lý và niên đại, không dùng bản đồ fantasy, đối chiếu sự thật sử liệu.",
        "flow_quota_per_video": 10
    },
    "cl": {
        "channel": "cl",
        "name": "Kênh Pháp Luật / Hồ Sơ",
        "priority_patterns": ["mystery_reveal", "evidence_reveal", "countdown_deadline"],
        "forbidden_patterns": [],
        "tone_rules": "Bám sát hồ sơ điều tra công khai, chữ rõ đọc được, tính bằng chứng thép.",
        "flow_quota_per_video": 10
    },
    "mim": {
        "channel": "mim",
        "name": "Kênh Kiến Thức Tiền Bạc (MIM)",
        "priority_patterns": ["mystery_reveal", "shocking_number", "chain_reaction"],
        "forbidden_patterns": [],
        "tone_rules": "Số liệu tài chính chuẩn xác, trực quan hóa dòng tiền và cơ chế vĩ mô.",
        "flow_quota_per_video": 10
    },
    "ck": {
        "channel": "ck",
        "name": "Kênh Chứng Khoán (CK)",
        "priority_patterns": ["before_after", "shocking_number", "chain_reaction"],
        "forbidden_patterns": [],
        "tone_rules": "Đồ thị biến động, thống kê tỉ lệ %, cảnh báo rủi ro khách quan.",
        "flow_quota_per_video": 10
    }
}


def main():
    SHARED.mkdir(parents=True, exist_ok=True)
    PROFILES.mkdir(parents=True, exist_ok=True)

    for pid, pdata in PATTERNS.items():
        out_f = SHARED / f"{pid}.json"
        out_f.write_text(json.dumps(pdata, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"-> Tạo mẫu: {out_f.name}")

    for cid, cdata in CHANNEL_PROFILES.items():
        out_f = PROFILES / f"{cid}.json"
        out_f.write_text(json.dumps(cdata, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"-> Tạo hồ sơ kênh: {out_f.name}")

    print(f"Đã tạo đủ 8 mẫu trong {SHARED} và 6 hồ sơ kênh trong {PROFILES}")


if __name__ == "__main__":
    main()
