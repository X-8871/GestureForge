"""ROOT派发前独立读取当前真实三流及六字段；仅离散准入。"""
import hashlib
import json
import sys
from pathlib import Path
import time

HERE = Path(__file__).parent
WORK = HERE.parents[3] / "tmp/2B/S2B-T17/s13_launch_prepare_20261012_r01"
sys.path.insert(0, str(WORK))
import runtime_consumer as consumer

def main():
    """拒绝空行、过期、终态、身份变化和任何预算告警。"""
    path = HERE / "consumer_config_r02.json"
    raw = path.read_bytes(); config = json.loads(raw)
    binding = consumer.load_bound(config["binding"])
    consumer.load_bound(config["plan"])
    journal, ji = consumer.complete(str(Path(config["supervision_dir"]) / "supervision.jsonl"))
    samples, si = consumer.complete(str(Path(config["supervision_dir"]) / "guard/samples.jsonl"))
    rows, ri = consumer.complete(str(Path(config["output_dir"]) / "consumption.jsonl"))
    latest = rows[-1]
    assert rows and all(row["status"] == "CONSUMED_LIVE_READY" and not row["blocked_latched"] for row in rows)
    assert time.monotonic() - latest["monotonic_seconds"] <= 10
    assert consumer.evaluate(journal, samples, binding, config["guard_identity"], [ji, si], latest["actual_gap_seconds"]) == []
    readback = {}
    for name, expected in (("root", binding), ("guard", config["guard_identity"]), ("consumer", latest["consumer_identity"])):
        current = consumer.identity(expected["pid"])
        assert consumer.same(current, expected)
        readback[name] = current
    for item in config["tool_bindings"]:
        assert hashlib.sha256(Path(item["path"]).read_bytes()).hexdigest() == item["sha256"]
    assert not (Path(config["supervision_dir"]) / "supervisor_receipt.json").exists()
    assert not (Path(config["supervision_dir"]) / "guard/guard_receipt.json").exists()
    assert not (Path(config["output_dir"]) / "consumer_receipt.json").exists()
    assert path.read_bytes() == raw
    receipt = dict(status="READY_CURRENT_DISCRETE_ADMISSION", config_sha256=hashlib.sha256(raw).hexdigest(),
        identities=readback, current_monotonic_seconds=time.monotonic(), consumption_rows=len(rows),
        latest_consumption=latest, supervision_binding=ji, samples_binding=si, consumption_binding=ri,
        limitation="只证明本次派发前当前离散准入，不追认r01，也不证明未来持续预算或STA。")
    with (HERE / "dispatch_admission_r02.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2); stream.write("\n")
    print(json.dumps(dict(status=receipt["status"], rows=len(rows), pids={k: v["pid"] for k, v in readback.items()})))

if __name__ == "__main__":
    main()
