#!/bin/bash
# sau Mậu Thân (run_after3): render lại Vessantara (media ảnh, không video)
sleep 60
while pgrep -f run_after3.sh >/dev/null || pgrep -f run_after2.sh >/dev/null; do sleep 20; done
cd ~/pilot131 && mkdir -p qa_round1 && rm -rf qa_round1/L_p131_bud_vessantara_c3v2 && mv out/L_p131_bud_vessantara_c3v2 qa_round1/ && ~/vietneu-tts/.venv/bin/python run.py L_p131_bud_vessantara_c3v2 >> run.log 2>&1
