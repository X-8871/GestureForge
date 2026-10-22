"""对刚完成的新ELF样本只读补证ACK，不重写原运行或重新启动模型。"""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
import traceback
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "report/evidence/S2B-T18/rebuilt_app_ack_observation_20261022_r01"
PARENT = ROOT / "report/evidence/S2B-T18/rebuilt_app_acceptance_20261022_r02"
CONFIG = ROOT / "report/evidence/S2B-T18/formal_online_20261018_r01/rebuilt_app_config_20261022_r02.json"
for item in (ROOT, ROOT / "verification", ROOT / "vitis"):
    sys.path.insert(0, str(item))
spec = importlib.util.spec_from_file_location("rebuilt_ack_wrapper", ROOT / "vitis/run_s2b_rebuilt_app_acceptance.py")
wrapper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wrapper)
r = wrapper.production


def binding(path):
    """保留实际原字节的SHA及绝对路径。"""
    path = r.exact_path(path, "file")
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    """仅停核、读取CSR并关闭自身会话；不发UART、LOAD、START、ACK或reset。"""
    r.require(RUN.parent.is_dir() and not RUN.exists(), "拒绝覆盖RunId")
    config = r.strict_json(CONFIG.read_bytes())
    wrapper.validate_config(config)
    parent = r.strict_json((PARENT / "orchestrator_result.json").read_bytes())
    sample = r.strict_json((PARENT / "deployment/sample000/acceptance_result.json").read_bytes())
    r.require(parent["status"] == "FAILED_CLEANUP" and parent["acceptance"]["status"] == "FAILED_REBUILT_APP_ACCEPTANCE", "原失败身份不符")
    r.require(parent["cleanup_errors"] == [{"step": "controller.close", "error": "RebuiltAppRunnerError('controller关闭或断点清理失败')"}], "原运行并非唯一预期的host关闭标记错误")
    closed = {item["step"] for item in parent["cleanup_steps"] if item["status"] == "PASS"}
    r.require({"serial.close", "rx.close", "tx.close", "csr_debug_map.clear", "session.disconnect", "xsdb.dispose", "journal.close"} <= closed, "原运行实际资源未释放")
    raw_rows = parent["raw_logs"]
    r.require(type(raw_rows) is list and raw_rows, "原运行输出清单缺失")
    for row in raw_rows:
        r.require(binding(row["path"])["sha256"] == row["sha256"], "原运行输出发生漂移：" + row["path"])
    raw_paths = {row["path"] for row in raw_rows}
    r.require({str(PARENT / "deployment/sample000/acceptance_result.json"), str(PARENT / "uart_rx_raw.bin")} <= raw_paths, "原清单未绑定样本或原始UART")
    r.require(sample["status"] == "PASS_REBUILT_APP_SAMPLE000_GOLDEN" and sample["final_epoch"] == 1 and sample["final_sequence"] == 4, "原样本未通过")
    r.require([(x["phase"], x["sequence"], x["epoch"]) for x in sample["frames"]] == [("weights", 3, 0), ("rebuilt_app_sample000", 4, 1)], "原响应身份不符")
    r.require(parent["acceptance"]["recovery_inputs"]["new_app_elf"]["sha256"] == "f7a8bc96418590a497577bb45a7cbc0cc75dec416f6af1bf9b33ffd0308fa5a9", "新ELF身份不符")
    RUN.mkdir()
    journal = r.Journal(RUN / "observer_calls.jsonl")
    out = {"schema_version": 1, "run_id": RUN.name, "status": "IN_PROGRESS", "scope": "POST_R02_READ_ONLY_ACK_IDLE_OBSERVATION", "parent_run_unchanged": True, "new_model_requests": 0, "writes_to_csr": 0, "cleanup_errors": [], "started_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(), "bindings": [binding(CONFIG), binding(PARENT / "orchestrator_result.json"), binding(PARENT / "deployment/sample000/acceptance_result.json"), binding(PARENT / "uart_rx_raw.bin"), binding(__file__)]}
    runtime = r.ProductionRuntime()
    xsdb = session = channel = ctrl = helper = None
    owner = {}
    helper_record = {"verified_inputs": {"compat_artifacts": {"implemented_xsa": config["bindings"]["xsa"]}}, "cleanup_errors": []}
    try:
        out["identity_before"] = runtime.identity(config)
        xsdb, serial = runtime.modules(config)
        session, channel = runtime.session(xsdb, serial, config, journal, lambda value: None)
        apis = r.load_apis("csr")
        ctrl = apis.jtag.JtagController(session, config["bindings"], RUN)
        rows = ctrl.call("session.targets.properties", session.targets, "--target_properties")
        selected = apis.jtag.validate_targets(rows)
        ctrl.refresh_targets(selected)
        ctrl.record["targets"] = selected
        out["cpu_before"] = {name: {"state": ctrl.state(name), "pc": ctrl.pc(name)} for name in ("cpu0", "cpu1")}
        for name in ("cpu1", "cpu0"):
            if ctrl.state(name).startswith("Running"):
                ctrl.call(name + ".stop.authorized_ack_observer", ctrl.targets[name].stop)
        ctrl.gate(both=True)
        helper, out["csr_helper"] = r.load_pinned_csr_map_helper()
        helper.register_csr_debug_map({"sdk_files": config["runtime"]["sdk_files"]}, helper_record, journal, session, ctrl, owner)
        snapshot = ctrl.stable_csr("r02_after_golden_ack")
        apis.csr_flow.csr.idle(snapshot)
        r.require(apis.csr_flow.csr.epoch(snapshot) == 1 and all(snapshot[x] == 0 for x in (0x068, 0x06C, 0x070, 0x074)), "不是本次epoch1的安全IDLE/空账本")
        out["final_snapshot"] = snapshot
        out["cpu_after"] = {name: {"state": ctrl.state(name), "pc": ctrl.pc(name)} for name in ("cpu0", "cpu1")}
        out["status"] = "PASS_POST_R02_ACK_IDLE_EPOCH1_LEDGER0"
    except Exception as error:
        out.update(status="FAILED_ACK_OBSERVATION", error=repr(error), traceback=traceback.format_exc())
    finally:
        actions = []
        if helper is not None and owner.get("attempted"):
            actions.append(("csr_map", lambda: helper.clear_csr_debug_map({"sdk_files": config["runtime"]["sdk_files"]}, helper_record, journal, session, owner)))
        if ctrl is not None:
            actions.append(("controller", ctrl.close))
        if session is not None:
            actions.append(("disconnect", lambda: session.disconnect(**({"chan": channel} if channel is not None else {}))))
        if xsdb is not None:
            actions.append(("dispose", xsdb.dispose))
        for name, action in actions:
            try:
                action()
            except Exception as error:
                out["cleanup_errors"].append({"step": name, "error": repr(error)})
        out["cleanup_errors"].extend(helper_record["cleanup_errors"])
        try:
            out["identity_after"] = runtime.identity(config)
        except Exception as error:
            out["cleanup_errors"].append({"step": "identity_after", "error": repr(error)})
        try:
            journal.close()
        except Exception as error:
            out["cleanup_errors"].append({"step": "journal.close", "error": repr(error)})
        if out["cleanup_errors"]:
            out["status"] = "FAILED_ACK_OBSERVATION_CLEANUP"
        out["finished_at_utc8"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
        out["exit_code"] = 0 if out["status"].startswith("PASS_") else 2
        (RUN / "observer_result.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: out.get(k) for k in ("status", "exit_code", "error", "cleanup_errors")}, ensure_ascii=False))
    return out["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
