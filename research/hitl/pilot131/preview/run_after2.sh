#!/bin/bash
while kill -0 56343 2>/dev/null; do sleep 20; done
cd ~/pilot131 && mkdir -p qa_round1 && rm -rf qa_round1/p131_fs_quet_nha_c1v2 && mv out/p131_fs_quet_nha_c1v2 qa_round1/ && ~/vietneu-tts/.venv/bin/python run.py p131_fs_quet_nha_c1v2 >> run.log 2>&1
