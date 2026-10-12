"""启动器遇到首行写入竞态后，只读核验既有自有消费器；不重复启动。"""
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).parent
ROOT = HERE.parents[3]
WORK = ROOT / "tmp/2B/S2B-T17/s13_launch_prepare_20261012_r01"
sys.path.insert(0, str(WORK))
import runtime_consumer as consumer

def bind(path):
    """原字节绑定，仅精确存在文件。"""
    path = consumer.exact(str(path))
    raw = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))

def main():
    """既有消费记录、实时六字段和三条当前流均成立才建立ROOT准入。"""
    assert bind(WORK / "runtime_consumer.py")["sha256"] == "8e8d3f4d19ceeafa1a3894941a77e8839a5f6559760d114b826518ef7289df0b"
    config_path = HERE / "consumer_config_r01.json"
    config_raw = config_path.read_bytes()
    assert hashlib.sha256(config_raw).hexdigest() == "513349f116f5765d6de2fab89d9358cbd5b3916ea88c07db0eb0bf81e932a44a"
    config = json.loads(config_raw)
    rows, own_stream = consumer.complete(str(HERE / "native_consumer_r01/consumption.jsonl"))
    first, last = rows[0], rows[-1]
    assert all(x["status"] == "CONSUMED_LIVE_READY" and x["blocked_latched"] is False for x in rows)
    expected = first["consumer_identity"]
    assert expected["pid"] == 34840 and expected["create_time"] == 1791772023.0808072
    command = [sys.executable, "-X", "utf8", "-B", str(WORK / "runtime_consumer.py"), "--config", str(config_path)]
    assert expected["cmdline"] == command and expected["cwd"] == str(ROOT)
    current = consumer.identity(expected["pid"])
    assert consumer.same(current, expected)
    assert all(consumer.same(x["consumer_identity"], expected) for x in rows)
    assert 0 <= own_stream["mtime_age_seconds"] <= consumer.FRESHNESS_SECONDS
    binding = consumer.load_bound(config["binding"])
    plan = consumer.load_bound(config["plan"])
    assert all(plan.get(k) == v for k, v in consumer.LIMITS.items())
    assert consumer.same(consumer.identity(binding["pid"]), binding)
    assert consumer.same(consumer.identity(config["guard_identity"]["pid"]), config["guard_identity"])
    journal, journal_info = consumer.complete(str(HERE / "supervision_r01/supervision.jsonl"))
    samples, sample_info = consumer.complete(str(HERE / "supervision_r01/guard/samples.jsonl"))
    assert consumer.evaluate(journal, samples, binding, config["guard_identity"], [journal_info, sample_info], last["actual_gap_seconds"]) == []
    assert 0 <= time.monotonic() - last["monotonic_seconds"] <= consumer.FRESHNESS_SECONDS
    for row in config["tool_bindings"]:
        assert bind(Path(row["path"]))["sha256"] == row["sha256"]
    assert config_path.read_bytes() == config_raw and consumer.same(consumer.identity(expected["pid"]), current)
    result = dict(status="ROOT_ADOPTED_EXISTING_LIVE_READY", at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),
                  original_launcher_status="BLOCKED_BACKGROUND_STARTUP", original_launcher_exit_code=2,
                  reason="输出文件先创建、首完整行尚未可见时，启动器complete抛异常；同一消费器随后持续LIVE。",
                  consumer_identity=current, first_consumption=first, latest_consumption=last,
                  current_guard_identity=config["guard_identity"], current_root_identity=binding,
                  config_binding=bind(config_path), current_streams=[own_stream, journal_info, sample_info],
                  same_consumer_restart_count=0, direct_child_wait_code=None,
                  limitations=["未追改启动器2或补造原handoff；此为ROOT当前真实六字段和新鲜流准入。",
                               "只证明本次离散读回，实际目标间隔和连续预算仍按原流记录。",
                               "不据此声称consumer、guard、Vivado或整树已退出。"])
    with (HERE / "consumer_adoption_r01.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2); stream.write("\n")
    print(json.dumps(dict(status=result["status"], pid=current["pid"], birth=current["create_time"],
        existing_ready_consumptions=len(rows), restarted=False, original_launcher_exit_code=2), ensure_ascii=False))

if __name__ == "__main__":
    main()
