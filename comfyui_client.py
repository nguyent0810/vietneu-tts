"""
Client mỏng gọi ComfyUI (chạy local, xem comfyui_local/ -- clone riêng,
gitignored, giống nguyên tắc video_tool_clone/) qua HTTP API để sinh ảnh
bằng SDXL-Turbo -- thay thế agy làm nguồn sinh ảnh CHÍNH cho asset_generation.py
(agy được giải phóng để làm việc khác, xem content_seo.py).

Vì sao chuyển từ agy sang ComfyUI: agy phụ thuộc quota tài khoản Google
(20 request/ngày free tier, đã xác nhận cạn nhiều lần trong phiên làm
việc). ComfyUI + SDXL-Turbo chạy HOÀN TOÀN LOCAL, không quota, không phụ
thuộc mạng/billing -- đã test trực tiếp 3 phong cách (thuỷ mặc, 2D phẳng,
vẽ chì) trên đúng tông nội dung Phật giáo, chất lượng đạt yêu cầu.

Yêu cầu: server ComfyUI phải đang chạy sẵn (không tự khởi động ở đây --
tải model mất thời gian, nên chạy như 1 service riêng, xem README/lệnh
khởi động bên dưới). Nếu server không phản hồi, raise ComfyUIUnavailableError
-- caller (asset_generation.py) tự fallback (Pexels/typography).

Khởi động server (chạy riêng, giữ terminal mở hoặc chạy nền):
    cd comfyui_local && ./.venv-comfy/bin/python main.py --port 8189 --listen 127.0.0.1
"""
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

COMFYUI_SERVER = "http://127.0.0.1:8189"
COMFYUI_OUTPUT_DIR = Path(__file__).parent / "comfyui_local" / "output"
CHECKPOINT_NAME = "sd_xl_turbo_1.0_fp16.safetensors"  # giữ lại tương thích ngược -- không dùng trực tiếp nữa, xem _QUALITY_PROFILES

# "turbo" -- 4 bước, cực nhanh, nhưng tay/mặt dễ biến dạng (không đủ vòng
# lặp khử nhiễu để model tự sửa hình học phức tạp). "base" -- SDXL gốc
# (không chưng cất), 25 bước, chậm hơn hẳn (~5-10x) nhưng đúng cấu hình
# CFG/scheduler chuẩn của SDXL thường (Turbo dùng cfg=1.0/sgm_uniform chỉ
# hợp với chính nó, áp vào base sẽ ra ảnh tệ) -- đổi cả bộ tham số, không
# chỉ riêng checkpoint.
_QUALITY_PROFILES = {
    "turbo": {
        "checkpoint": "sd_xl_turbo_1.0_fp16.safetensors",
        "steps": 4, "cfg": 1.0, "sampler": "euler_ancestral", "scheduler": "sgm_uniform",
    },
    "base": {
        "checkpoint": "sd_xl_base_1.0.safetensors",
        "steps": 25, "cfg": 7.0, "sampler": "dpmpp_2m", "scheduler": "karras",
    },
}

# Bổ sung từ khoá riêng cho tay/mặt (phổ biến trong cộng đồng SD để giảm
# artifact hình học phức tạp) -- trước chỉ có "extra limbs, disfigured"
# chung chung, không nhắm riêng vào đúng chỗ hay lỗi nhất.
DEFAULT_NEGATIVE_PROMPT = (
    "text, watermark, photorealistic, blurry, low quality, extra limbs, disfigured, "
    "bad hands, malformed hands, extra fingers, fused fingers, missing fingers, "
    "mutated hands, poorly drawn hands, bad anatomy, poorly drawn face, asymmetric eyes"
)
POLL_INTERVAL_S = 1.5
# Đã thấy dao động thật 5-30s tuỳ tải hệ thống (nặng hơn khi Codex/agy vừa
# chạy xong, tranh chấp GPU/Neural Engine) -- 90s từng gây timeout giả khi
# máy đang tải cao, hạ ảnh premium xuống fallback oan uổng dù ComfyUI (tầng
# an toàn CUỐI trong chuỗi) vẫn chạy được, chỉ chậm hơn bình thường. Tăng
# lên 150s cho dư địa an toàn hơn.
GENERATION_TIMEOUT_S = 150


class ComfyUIUnavailableError(RuntimeError):
    pass


def is_server_running() -> bool:
    try:
        with urllib.request.urlopen(f"{COMFYUI_SERVER}/system_stats", timeout=3) as resp:
            return resp.status == 200
    except (urllib.error.URLError, OSError):
        return False


def _build_workflow(prompt_text: str, negative_prompt: str, seed: int, width: int, height: int, profile: dict) -> dict:
    return {
        "3": {"class_type": "KSampler", "inputs": {
            "seed": seed, "steps": profile["steps"], "cfg": profile["cfg"], "sampler_name": profile["sampler"],
            "scheduler": profile["scheduler"], "denoise": 1.0,
            "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0],
        }},
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": profile["checkpoint"]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt_text, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative_prompt, "clip": ["4", 1]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "beat", "images": ["8", 0]}},
    }


def generate_image(
    prompt_text: str,
    output_path: Path,
    seed: int = 0,
    width: int = 1024,
    height: int = 576,
    negative_prompt: str = DEFAULT_NEGATIVE_PROMPT,
    quality: str = "turbo",
    timeout_s: float | None = None,
) -> Path:
    """Sinh 1 ảnh qua ComfyUI, copy sang output_path (đường dẫn ta tự quản
    lý, không phụ thuộc thư mục output mặc định của ComfyUI). Raise
    ComfyUIUnavailableError nếu server không chạy/lỗi/timeout -- caller tự
    fallback.

    `quality`: "turbo" (mặc định, 4 bước, nhanh nhưng tay/mặt dễ lỗi) hoặc
    "base" (SDXL gốc, 25 bước, chậm hơn ~5-10x nhưng đúng vòng lặp khử
    nhiễu cần thiết cho hình học phức tạp) -- xem _QUALITY_PROFILES."""
    if quality not in _QUALITY_PROFILES:
        raise ValueError(f"quality phải là 1 trong {list(_QUALITY_PROFILES)}, nhận '{quality}'.")
    profile = _QUALITY_PROFILES[quality]
    effective_timeout = timeout_s if timeout_s is not None else (GENERATION_TIMEOUT_S if quality == "turbo" else GENERATION_TIMEOUT_S * 5)

    if not is_server_running():
        raise ComfyUIUnavailableError(
            f"ComfyUI server không phản hồi tại {COMFYUI_SERVER} -- cần khởi động trước "
            f"(cd comfyui_local && ./.venv-comfy/bin/python main.py --port 8189 --listen 127.0.0.1)."
        )

    workflow = _build_workflow(prompt_text, negative_prompt, seed, width, height, profile)
    data = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(f"{COMFYUI_SERVER}/prompt", data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
    except (urllib.error.URLError, OSError) as exc:
        raise ComfyUIUnavailableError(f"Gửi prompt tới ComfyUI lỗi: {exc}")

    if "error" in result:
        raise ComfyUIUnavailableError(f"ComfyUI từ chối workflow: {result['error']}")
    prompt_id = result["prompt_id"]

    start = time.time()
    history = None
    while time.time() - start < effective_timeout:
        try:
            with urllib.request.urlopen(f"{COMFYUI_SERVER}/history/{prompt_id}", timeout=10) as resp:
                all_history = json.loads(resp.read())
        except (urllib.error.URLError, OSError) as exc:
            raise ComfyUIUnavailableError(f"Poll ComfyUI history lỗi: {exc}")
        if prompt_id in all_history:
            history = all_history[prompt_id]
            break
        time.sleep(POLL_INTERVAL_S)

    if history is None:
        raise ComfyUIUnavailableError(f"ComfyUI sinh ảnh quá {effective_timeout:.0f}s, timeout.")

    status = history.get("status", {})
    if status.get("status_str") == "error":
        raise ComfyUIUnavailableError(f"ComfyUI báo lỗi khi sinh: {status}")

    outputs = history.get("outputs", {})
    image_info = None
    for node_output in outputs.values():
        if "images" in node_output and node_output["images"]:
            image_info = node_output["images"][0]
            break
    if image_info is None:
        raise ComfyUIUnavailableError(f"ComfyUI hoàn tất nhưng không có ảnh output: {history}")

    generated_path = COMFYUI_OUTPUT_DIR / image_info.get("subfolder", "") / image_info["filename"]
    if not generated_path.exists():
        raise ComfyUIUnavailableError(f"ComfyUI báo ảnh tại {generated_path} nhưng file không tồn tại.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(generated_path.read_bytes())
    return output_path
