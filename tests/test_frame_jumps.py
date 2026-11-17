"""tools/frame_jumps: bắt cú giật một khung trong cảnh, bỏ qua seam (Quét nhà NIj0goKjNtc, 17/11/2026)."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import frame_jumps as F  # noqa: E402

import studio  # noqa: E402


def test_spike_while_panning_is_caught():
    # số đo thật quanh giây 1,2 của Quét nhà: camera đang trượt (~12) rồi nhảy 52,6
    d = [0.0] + [11.0] * 33 + [11.2, 11.9, 12.2, 52.6, 7.9, 7.4] + [7.0] * 20
    assert F.spikes(d) == [round(37 / 30, 3)]


def test_smooth_motion_and_seam_are_not_jumps():
    smooth = [0.0] + [8.0 + (i % 3) for i in range(90)]
    assert F.spikes(smooth) == []
    seam = [0.0] * 60 + [40.0] + [0.0] * 30          # giật ở giây 2,0 nhưng là mốc cắt cảnh
    assert F.spikes(seam, cuts=[2.1]) == []
    assert F.spikes(seam) == [2.0]


def test_qa_ok_fails_on_jumps_only_when_measured():
    base = {"lint": {"ok": True}, "check": {"ok": True}}
    assert studio.qa_ok(base) is True
    assert studio.qa_ok({**base, "jumps": {"ok": None, "error": "x"}}) is True
    assert studio.qa_ok({**base, "jumps": {"ok": True, "at": []}}) is True
    assert studio.qa_ok({**base, "jumps": {"ok": False, "at": [1.2]}}) is False


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="không có ffmpeg")
def test_real_video_one_frame_jump(tmp_path):
    # ô vuông trượt đều rồi nhảy hẳn sang chỗ khác ở giây 1,0 (một khung), sau đó trượt tiếp
    mp4 = tmp_path / "j.mp4"
    expr = "if(lt(t,1),10+t*20,150+(t-1)*20)"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=gray:s=360x640:r=30:d=2",
                    "-f", "lavfi", "-i", "color=c=white:s=200x200:r=30:d=2",
                    "-filter_complex", f"[0][1]overlay=x='{expr}':y=200:shortest=1",
                    "-pix_fmt", "yuv420p", str(mp4)], check=True)
    jumps = F.spikes(F.frame_diffs(str(mp4)))
    assert len(jumps) == 1 and abs(jumps[0] - 1.0) < .05
