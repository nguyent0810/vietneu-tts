"""Reproduce voice-rate receipts from existing BUD/FS manifests, without TTS.

From the worktree:
../../../.venv/bin/python docs/research/075b/measure.py ../../.. > /tmp/075b-rates.json
"""
import collections
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from long_script_lint import syllables


def measure(root: Path) -> list[dict]:
    groups = collections.defaultdict(list)
    for path in (root / "output/cl_staging/long/out").glob("L_*.json"):
        if not path.name.startswith(("L_bud_", "L_fs_")):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not data.get("segments"):
            continue
        tts_path = path.with_suffix(".tts.json")
        tts = json.loads(tts_path.read_text(encoding="utf-8")) if tts_path.exists() else {}
        key = (data.get("voice"), tts.get("engine", "unspecified"), tts.get("tempo"))
        groups[key].append((path.stat().st_mtime, path, data, tts))
    results = []
    for config, files in sorted(groups.items(), key=lambda item: str(item[0])):
        files = sorted(files, reverse=True)[:3]
        counts = collections.defaultdict(lambda: [0, 0.0, 0.0, 0])
        sources = []
        for _, path, data, tts in files:
            sources.append({"file": str(path.relative_to(root)),
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "tts": tts})
            segments = data["segments"]
            for i, seg in enumerate(segments):
                stat = counts[seg.get("voice") or data.get("voice") or "unknown"]
                stat[0] += syllables(seg.get("spoken") or seg["text"])
                stat[1] += seg["end"] - seg["start"]
                following = segments[i + 1]["start"] if i + 1 < len(segments) else data.get("duration_s", seg["end"])
                stat[2] += following - seg["start"]
                stat[3] += 1
        for voice, (n, speech, clock, segment_count) in counts.items():
            results.append({"voice": voice, "config": list(config), "files": len(files),
                            "segments": segment_count, "syllables": n,
                            "speech_s": round(speech, 3), "clock_s": round(clock, 3),
                            "speech_spm": round(n / speech * 60, 1),
                            "clock_spm": round(n / clock * 60, 1), "sources": sources})
    return results


if __name__ == "__main__":
    print(json.dumps(measure(Path(sys.argv[1]).resolve()), ensure_ascii=False, indent=2))
