"""消费绑定的 S1 STA 解析记录，以真实原生码表示时序结论。"""
import hashlib
import json
from pathlib import Path
import sys

run = Path(__file__).resolve().parent
record = json.loads((run / "collector_sta_classification.json").read_text(encoding="utf-8"))
for item in record["inputs"]:
    path = Path.cwd() / item["path"]
    assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
failed = record["timing"]["wns_ns"] < 0 or record["timing"]["tns_ns"] < 0 or record["timing"]["setup_failing_endpoints"] > 0
assert failed and record["status"] == "FAIL_TIMING"
print(json.dumps({"status": "FAIL_TIMING", "native_exit_code": 2, "report_command_native_exit_code": record["report_command_native_exit_code"], "timing": record["timing"]}, ensure_ascii=False))
sys.exit(2)
