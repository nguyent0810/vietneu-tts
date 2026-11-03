#!/bin/bash
# chờ lô hiện tại (theo PID) rồi render 2 Long
P=$(cat ~/pilot131/run.pid)
while kill -0 "$P" 2>/dev/null; do sleep 20; done
cd ~/pilot131 && ~/vietneu-tts/.venv/bin/python run.py L_p131_fs_mauthan_c2v2 L_p131_bud_vessantara_c3v2 >> run.log 2>&1
