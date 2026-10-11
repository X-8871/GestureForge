"""独立判定真实业务状态，不继承Vitis wrapper退出码。"""
import json,sys
from pathlib import Path
d=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
valid=d.get("hardware_execution")=="NOT_RUN" and d.get("status")==sys.argv[2]
if sys.argv[2]=="PASS_OFFLINE_FULL_XSA_BUILD":
    calls={x["name"]:x for x in d.get("api_calls",[])}
    valid=valid and d.get("hardware_mode")=="FULL_PLATFORM_BOUND" and all(calls.get(n,{}).get("return_type")=="int" and calls.get(n,{}).get("return_repr")=="0" for n in ("platform.build","app.build","init.build"))
else:
    valid=valid and d.get("tests")=={"run":24,"failures":0,"errors":0,"skipped":0}
print(json.dumps({"status":"PASS_BUSINESS_JSON" if valid else "FAIL_BUSINESS_JSON","actual_status":d.get("status"),"native_exit_code":0 if valid else 2},ensure_ascii=False))
sys.exit(0 if valid else 2)
