"""Lời đọc short BUD/FS bằng hf_voice (giọng D theo kênh): tts_short.py spec.json voice_spec.json out.wav"""
import json, sys
from pathlib import Path
sys.path.insert(0, "/home/ubuntu/vietneu-tts")
import hf_voice
spec = json.load(open(sys.argv[1])); vs = json.load(open(sys.argv[2]))
m = hf_voice.synth(spec["lines"], vs, Path(sys.argv[3]))
print(json.dumps({k: m.get(k) for k in ("duration_s", "n_retried")}))
