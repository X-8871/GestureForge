"""只读核对S12失败证据归档与自有会话结束，不访问板卡。"""
import hashlib
import json
from pathlib import Path
import psutil

ROOT = Path(__file__).parents[4]
ARCHIVE = ROOT / "report/evidence/S2B-T17/s12_root_closure_20261012_r01"

def read(name):
    """按UTF-8读取归档原件。"""
    return json.loads((ARCHIVE / name).read_text(encoding="utf-8"))

for row in read("archive_mapping_final.json"):
    for side in ("original", "saved"):
        item = row[side]
        raw = (ROOT / item["path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == item["sha256"]
        assert len(raw) == item["bytes"]
    assert row["original"]["sha256"] == row["saved"]["sha256"]
review = read("support/independent_s12_actual_failure_review_20261012_r01/final_review_receipt.json")
assert review["status"] == "PASS_EVIDENCE_INTEGRITY_ONLY"
assert review["source_commit"] == "467463757158aed80d6f75afadff6a8458614a29"
stop = read("owned_stop.tool.json")
assert json.loads(stop["content"][0]["text"])["status"] == "success"
binding = read("owned_binding_current.json")
try:
    process = psutil.Process(binding["pid"])
    assert process.create_time() != binding["create_time"], "自有Vivado尚未退出"
except psutil.NoSuchProcess:
    pass
print(json.dumps({"status": "PASS_ARCHIVE_AND_OWNED_EXIT_ONLY", "review_status": review["status"], "archive_rows": len(read("archive_mapping_final.json")), "hardware_execution": "NOT_RUN", "limitations": ["只证明归档和自有根进程已退出，不代表完整物理预算、STA或G3通过。"]}, ensure_ascii=False))
