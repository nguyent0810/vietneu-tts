#!/bin/bash
P=$(cat ~/pilot131/run.pid)
while kill -0 "$P" 2>/dev/null; do sleep 20; done
cd ~/pilot131 && mkdir -p qa_round2 && rm -rf qa_round2/L_p131_fs_mauthan_c2v2 && mv out/L_p131_fs_mauthan_c2v2 qa_round2/ && rm -f long/out/L_p131_fs_mauthan_c2v2.mp4 && ~/vietneu-tts/.venv/bin/python run.py L_p131_fs_mauthan_c2v2 >> run.log 2>&1
