#!/bin/bash
# sau khi quét nhà render lại xong: render lại Mậu Thân (có media)
while pgrep -f run_after2.sh >/dev/null; do sleep 20; done
cd ~/pilot131 && mkdir -p qa_round1 && rm -rf qa_round1/L_p131_fs_mauthan_c2v2 && mv out/L_p131_fs_mauthan_c2v2 qa_round1/ && rm -rf long/out/L_p131_fs_mauthan_c2v2* && ~/vietneu-tts/.venv/bin/python run.py L_p131_fs_mauthan_c2v2 >> run.log 2>&1
