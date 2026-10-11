"""独立检查Vitis/测试真实业务JSON，给出实际非零失败码。"""
import json
from pathlib import Path
import sys

path = Path(sys.argv[1])
expected = sys.argv[2]
record = json.loads(path.read_text(encoding="utf-8"))
valid = record.get("status") == expected and record.get("hardware_execution") == "NOT_RUN"
if expected == "PASS_UNIT_ONLY_PS_XSA_BUILD":
    names = {row["name"]: row for row in record.get("api_calls", [])}
    valid = valid and all(name in names and names[name].get("return_type") == "int" and names[name].get("return_repr") == "0"
                          for name in ("platform.build", "app.build", "init.build"))
else:
    valid = valid and record.get("tests") == {"run": 19, "failures": 0, "errors": 0, "skipped": 0}
print(json.dumps({"status": "PASS_BUSINESS_JSON" if valid else "FAIL_BUSINESS_JSON", "actual_status": record.get("status"),
                  "expected_status": expected, "exit_code": 0 if valid else 2}, ensure_ascii=False))
sys.exit(0 if valid else 2)
