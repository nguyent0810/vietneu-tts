#!/bin/bash
P="$(cd "$(dirname "$0")/.." && pwd)"
cd "$P/indep"
for t in tt05_temiya vsd_fansipan ck_bybit_2025 f19_hue_phong_thuy fs_short_ngay_tot_cuoi; do
  t0=$(date +%s)
  codex exec --skip-git-repo-check -s read-only -C "$P/indep" "$(cat PROMPT.md) File: $t.input.json" < /dev/null > "$t.codex.log" 2>&1 &
  pid=$!; ( sleep 1500; kill $pid 2>/dev/null ) & wait $pid
  echo "$t $(( $(date +%s) - t0 ))s $(grep -A1 '^tokens used' "$t.codex.log" | tail -1)" >> timing.txt
done
echo done
