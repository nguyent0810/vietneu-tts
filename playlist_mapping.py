"""Mapping content_id -> playlist_title (đúng nguyên văn playlist đã có,
hoặc tên playlist MỚI cần tạo) cho 35 Short tuần này. Quyết định thủ công
dựa trên đối chiếu nội dung thật của từng content_id với danh sách
playlist thật đã lấy qua list_playlists() (xem phiên làm việc)."""

# BUD -- toàn bộ 14 Short đều là 1 phẩm trong Kinh Địa Tạng -> playlist đã
# có sẵn đúng loạt này, khớp CHÍNH XÁC, không cần tạo mới.
BUD_PLAYLIST = "GIẢI MÃ KINH ĐỊA TẠNG | Địa Tạng Vương Bồ Tát, Nhân Quả, Hiếu Đạo Và Con Đường Chuyển Hóa"

# FS -- một số content_id khớp CHÍNH XÁC playlist mệnh/con giáp đã có sẵn;
# phần còn lại (không có playlist mệnh/chủ đề khớp) -> playlist MỚI theo
# category (content_categories.py) để không gộp bừa vào playlist tổng
# "Video Ngắn..." (659 video, không giúp điều hướng).
FS_MAPPING = {
    "FS_D1_element_color_moc": "Mệnh Mộc Trong Tử Vi: Tìm Hiểu Vận Mệnh và Cách Hóa Giải",  # đã có, khớp đúng
    "FS_D5_element_color_hoa": "🔥 Bí Mật Phong Thủy Mệnh Hỏa - Kích Hoạt Tài Lộc & Thành Công Nhanh Nhất!",  # đã có
    "FS_D6_element_color_tho": "🌟 Phong Thủy Mệnh Thổ | Bí Quyết Hút Tài Lộc & May Mắn Cho Người Mệnh Thổ",  # đã có
    "FS_D4_zodiac_month": "Tử vi 12 con giáp",  # đã có, khớp đúng chủ đề con giáp
    "FS_D7_zodiac": "Tử vi 12 con giáp",  # đã có
    # Không có playlist khớp sẵn -- tạo mới theo nhóm nội dung (Category 1
    # Grounded Data hàng ngày: 12 vị Thần + vật phẩm may mắn hôm nay).
    "FS_D2_twelve_gods": "12 Vị Thần Hôm Nay -- Phong Thuỷ Mỗi Ngày",  # MỚI
    "FS_D3_twelve_gods": "12 Vị Thần Hôm Nay -- Phong Thuỷ Mỗi Ngày",  # MỚI (cùng playlist trên)
    "FS_D2_element_luck": "Màu & Vật Phẩm Hợp Mệnh Hôm Nay",  # MỚI
    "FS_D7_element_luck": "Màu & Vật Phẩm Hợp Mệnh Hôm Nay",  # MỚI (cùng playlist trên)
    # SỬA theo Codex review #5 vòng 1 (NEEDS_REVISION): KHÔNG gộp lịch
    # hoàng đạo vào "Màu & Vật Phẩm..." -- intent người xem khác nhau
    # (Codex: "Người xem tìm lịch hoàng đạo có intent khác với màu/vật
    # phẩm hợp mệnh"). Tách playlist riêng "Lịch Hoàng Đạo Hôm Nay" dù chỉ
    # có 1 video khởi điểm -- xác nhận qua short_batch_runner.py
    # PHONG_THUY_TIME_SLOTS + lich_hoang_dao_generator.py: đây là
    # generator XOAY VÒNG EVERGREEN có khung giờ cố định hàng tuần, KHÔNG
    # phải nội dung 1 lần -- sẽ có thêm video đều đặn, không phải playlist
    # "mồ côi" 1 video vĩnh viễn (đáp ứng điều kiện Codex đặt ra: "chỉ tạo
    # playlist mới nếu có kế hoạch bổ sung đều đặn").
    "FS_D4_lich_hoang_dao": "Lịch Hoàng Đạo Hôm Nay",  # MỚI
    "FS_D1_educational": "Kiến Thức Ngũ Hành & Phong Thuỷ Căn Bản",  # MỚI
    "FS_D1_storytelling": "Giai Thoại & Truyền Thuyết Phong Thuỷ",  # MỚI
    "FS_D3_western_zodiac_cugiai": "12 Cung Hoàng Đạo Phương Tây",  # MỚI
    "FS_D6_western_zodiac_thienyet": "12 Cung Hoàng Đạo Phương Tây",  # MỚI (cùng playlist trên)
    "FS_D5_iching": "Kinh Dịch Ứng Dụng Đời Sống",  # MỚI
}

# CL -- 2 Short giáo dục pháp luật chung (không vụ án cụ thể) khớp
# "Điểm tin pháp luật" đã có. 4 Short về vụ án thật (Năm Cam, Lê Văn
# Luyện, Cát Tường, O.J. Simpson) -- CẦN QUYẾT ĐỊNH giữa 2 playlist có sẵn:
# "Từ điển giang hồ Việt Nam" (đúng cho Năm Cam -- nhân vật giang hồ có
# thật) vs "Những Kẻ Sát Nhân & Bí Ẩn Lịch Sử: Tâm Lý Tội Phạm" (đúng hơn
# cho Lê Văn Luyện/Cát Tường/O.J. Simpson -- trọng tâm là vụ án/pháp lý,
# không phải nhân vật giang hồ có tổ chức).
CL_MAPPING = {
    "CL_D2_luat1_an_treo": "Điểm tin pháp luật",  # đã có, khớp đúng (giáo dục pháp luật chung)
    "CL_D7_luat2_no_lua_dao": "Điểm tin pháp luật",  # đã có
    "CL_D3_nam_cam": "Từ điển giang hồ Việt Nam",  # đã có -- Năm Cam là nhân vật giang hồ có thật
    "CL_D4_le_van_luyen": "Những Kẻ Sát Nhân & Bí Ẩn Lịch Sử: Tâm Lý Tội Phạm",  # đã có -- trọng tâm pháp lý/tâm lý tội phạm
    "CL_D5_cat_tuong": "Những Kẻ Sát Nhân & Bí Ẩn Lịch Sử: Tâm Lý Tội Phạm",  # đã có
    "CL_D6_oj_simpson": "Những Kẻ Sát Nhân & Bí Ẩn Lịch Sử: Tâm Lý Tội Phạm",  # đã có
}
