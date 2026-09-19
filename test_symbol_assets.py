"""Test tự động cho symbol_library Bát Quái/Ngũ Hành (audit 9 điểm mục #2)
-- thêm theo yêu cầu Codex review (chỉ kiểm bằng mắt là không đủ, cần bắt
được regression hình học/màu khi có ai đó sửa nhầm generate_symbol_assets.py
sau này). KHÔNG thay ảnh -- chỉ đọc lại 6 file PNG đã sinh + gọi
rotation_state.pick_and_commit_next() thật."""
import math
import multiprocessing
from pathlib import Path

from PIL import Image

from generate_symbol_assets import NGU_HANH, PALETTES, SIZE, CENTER, OUT_DIR
import rotation_state

VARIANTS = list(PALETTES.keys())


def test_all_six_pngs_exist_correct_size():
    for symbol in ("bat_quai_hau_thien", "ngu_hanh"):
        for variant in VARIANTS:
            path = OUT_DIR / f"{symbol}_{variant}.png"
            assert path.exists(), f"Thiếu file {path}"
            with Image.open(path) as img:
                assert img.size == (SIZE, SIZE), f"{path} sai kích thước: {img.size}"


def test_ngu_hanh_node_colors_identical_across_variants():
    """Màu nút từng hành PHẢI giống hệt giữa 3 biến thể (chỉ nền/viền được
    đổi) -- lấy mẫu pixel tại đúng toạ độ tâm mỗi node, so khớp màu khai
    báo trong NGU_HANH."""
    r = SIZE * 0.30
    for i, (name, expected_color) in enumerate(NGU_HANH):
        angle = math.radians(-90 + i * 72)
        x = round(CENTER + r * math.cos(angle))
        y = round(CENTER + r * math.sin(angle))
        for variant in VARIANTS:
            path = OUT_DIR / f"ngu_hanh_{variant}.png"
            with Image.open(path) as img:
                pixel = img.convert("RGB").getpixel((x, y))
            assert pixel == expected_color, (
                f"variant={variant} node={name} tại ({x},{y}) có màu {pixel}, "
                f"kỳ vọng {expected_color} -- màu hành bị lệch giữa các biến thể (SAI NỘI DUNG)."
            )


def test_ngu_hanh_node_positions_identical_across_variants():
    """Bố cục ngũ giác PHẢI giống hệt giữa 3 biến thể -- so khớp 1 điểm
    mẫu nhỏ NẰM TRONG phần fill của node nhưng LỆCH khỏi tâm (nơi có chữ
    nhãn) -- màu chữ nhãn (palette["cream"]) CHỦ Ý đổi theo biến thể (chữ
    trang trí, xem docstring generate_ngu_hanh), so ngay tại tâm sẽ báo
    lỗi giả. Điểm mẫu lệch lên trên node_r*0.6 vẫn chắc chắn nằm trong
    hình tròn fill (node_r), đủ xa vùng chữ theo chiều dọc."""
    r = SIZE * 0.30
    node_r = SIZE * 0.075
    offset_y = node_r * 0.6
    crop_half = 10
    ref_variant = VARIANTS[0]
    with Image.open(OUT_DIR / f"ngu_hanh_{ref_variant}.png") as ref_img:
        ref_img = ref_img.convert("RGB")
        for i, (name, expected_color) in enumerate(NGU_HANH):
            angle = math.radians(-90 + i * 72)
            x = round(CENTER + r * math.cos(angle))
            y = round(CENTER + r * math.sin(angle) - offset_y)
            ref_crop = ref_img.crop((x - crop_half, y - crop_half, x + crop_half, y + crop_half))
            assert all(p == expected_color for p in ref_crop.getdata()), (
                f"node={name} điểm mẫu lệch tâm không khớp màu fill kỳ vọng {expected_color} -- vị trí/bán kính node có thể sai."
            )
            for variant in VARIANTS[1:]:
                with Image.open(OUT_DIR / f"ngu_hanh_{variant}.png") as other_img:
                    other_crop = other_img.convert("RGB").crop((x - crop_half, y - crop_half, x + crop_half, y + crop_half))
                    assert list(ref_crop.getdata()) == list(other_crop.getdata()), (
                        f"node={name} vùng fill khác nhau giữa {ref_variant} và {variant} -- bố cục bị lệch."
                    )


def _worker_pick(state_path_str: str, order: list, state_key: str, out_queue) -> None:
    picked = rotation_state.pick_and_commit_next(Path(state_path_str), order, state_key)
    out_queue.put(picked)


def test_pick_and_commit_next_concurrent_no_corruption(tmp_path):
    """Codex review vòng 1: peek_next()+commit() (2 lock riêng) có race
    condition thật khi Long/Short render song song. pick_and_commit_next()
    (1 lock nguyên tử, đọc-chọn-ghi trong CÙNG 1 giao dịch) phải KHÔNG có
    hiện tượng đó.

    Codex review vòng 2 (siết test theo yêu cầu): chỉ kiểm "kết quả nằm
    trong order" là CHƯA ĐỦ -- 1 implementation lỗi (vd race khiến nhiều
    tiến trình cùng đọc "chưa ai dùng" rồi cùng trả biến thể đầu tiên) vẫn
    lọt qua kiểu test đó. Với n_workers=12 và order có 3 phần tử, nếu
    NGUYÊN TỬ THẬT thì state chỉ tiến đúng 1 bước/lần gọi (không phụ thuộc
    thứ tự tiến trình nào chạy trước) -- kết quả BẮT BUỘC phân bố ĐỀU
    TUYỆT ĐỐI 4 gold/4 jade/4 indigo (không may 5-4-3 hay 6-6-0). Đồng thời
    kiểm exitcode từng worker (không chỉ suy luận gián tiếp qua queue có
    đủ item hay không -- worker crash giữa chừng vẫn có thể để queue thiếu
    item mà không tự báo lỗi rõ ràng)."""
    state_path = tmp_path / "concurrent_rotation_state.json"
    order = ["gold", "jade", "indigo"]
    n_workers = 12
    ctx = multiprocessing.get_context("spawn")
    out_queue = ctx.Queue()
    procs = [
        ctx.Process(target=_worker_pick, args=(str(state_path), order, "last_variant", out_queue))
        for _ in range(n_workers)
    ]
    for p in procs:
        p.start()
    for p in procs:
        p.join(timeout=30)
        assert not p.is_alive(), "worker treo quá 30s"
        assert p.exitcode == 0, f"worker crash, exitcode={p.exitcode}"

    results = [out_queue.get_nowait() for _ in range(n_workers)]
    assert len(results) == n_workers
    from collections import Counter
    assert Counter(results) == Counter({"gold": 4, "jade": 4, "indigo": 4}), (
        f"phân bố KHÔNG đều -- bằng chứng race condition: {Counter(results)}"
    )

    final_state = rotation_state._load_state(state_path)
    assert final_state.get("last_variant") in order
    assert "reserved_item" not in final_state, "pick_and_commit_next không nên để lại reservation"


def test_bat_quai_and_ngu_hanh_rotation_independent(tmp_path):
    """2 symbol_key khác nhau dùng CHUNG 1 state file (thiết kế thật trong
    domain_creative_profiles.py) -- xác nhận rotation của bên này KHÔNG
    ảnh hưởng bên kia."""
    state_path = tmp_path / "shared_symbol_variant_state.json"
    paths_a = ["a1", "a2", "a3"]
    paths_b = ["b1", "b2", "b3"]

    seq_a = [rotation_state.pick_and_commit_next(state_path, paths_a, "last_bat_quai_variant") for _ in range(4)]
    seq_b = [rotation_state.pick_and_commit_next(state_path, paths_b, "last_ngu_hanh_variant") for _ in range(4)]

    assert seq_a == ["a1", "a2", "a3", "a1"]
    assert seq_b == ["b1", "b2", "b3", "b1"]


if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
