#!/bin/bash
# Kiểm bố cục spec VSD TRƯỚC khi xếp hàng render (Lead 16/11, workflow (a)).
# Dựng job (không render) + hyperframes check đúng mốc studio --qa dùng, in lỗi layout/contrast.
# Dùng: pipelines/vsd/check_layout.sh <spec_id>...   (spec ở output/cl_staging/vsd/specs/)
cd "$(dirname "$0")/../.."; export HYPERFRAMES_BROWSER_PATH=/usr/bin/chromium HF_HUB_OFFLINE=1
source ~/.nvm/nvm.sh >/dev/null 2>&1; nvm use 22 >/dev/null 2>&1
for id in "$@"; do
  .venv/bin/python studio.py build output/cl_staging/vsd/specs/$id.json --no-ledger > /tmp/chk_$id.log 2>&1 || { echo "$id BUILD_FAIL $(tail -2 /tmp/chk_$id.log)"; continue; }
  cd hyperframes_short/jobs/$id
  m=$(python3 -c "import json;print(\",\".join(\"%.2f\"%((a+b)/2) for a,b in json.load(open(\"plan.json\"))[\"windows\"]))")
  timeout 900 npx --yes hyperframes@0.8.75 check --json --at $m 2>/dev/null > /tmp/chk_$id.json
  python3 - "$id" <<'PY'
import json,sys
i=sys.argv[1];s=open(f"/tmp/chk_{i}.json").read();d=json.loads(s[s.find("{"):])
e=[(k,f["time"],f.get("text","")[:25],f["selector"][-45:]) for k in ("layout","contrast") for f in d.get(k,{}).get("findings",[]) if f.get("severity")=="error"]
print(i,"OK" if not e else "ERR %d"%len(e)); [print("   ",x) for x in e]
PY
  cd - >/dev/null
done
echo CHECK_DONE
