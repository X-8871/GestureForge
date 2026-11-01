"""从已真实停稳VDMA并复位至EOS0的现场，以全新会话继续2B部署。"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import traceback

ROOT = Path(r"D:\FPGA_Competition\w2b")
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("restore_r03_runtime", ROOT / "vitis/run_s2b_model_acceptance.py")
r = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r
spec.loader.exec_module(r)
config = r.strict_json((ROOT / "report/evidence/S2B-T18/formal_online_20261018_r01/model_config_csr_20261019_r10.json").read_bytes())
config["hw_server"] = r.strict_json(r.exact_path(ROOT / "tmp/2B/hw_server_20261021.json").read_bytes())
config["source_commit"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
runner_path = r.exact_path(ROOT / "vitis/run_s2b_model_acceptance.py")
config["bindings"]["runner_source"] = {"path": str(runner_path), "sha256": r.digest(runner_path.read_bytes())}
out = ROOT / "report/evidence/S2B-T18/stage3_to_2b_restore_20261021_r03"
r.require(out.parent.is_dir() and not out.exists(), "证据目录必须全新")
out.mkdir()
r.save_json_new(out / "input_config.json", config)
(out / "execution_script.py").write_bytes(Path(__file__).read_bytes())
apis = r.load_apis("csr")
runtime = r.ProductionRuntime()
journal = r.Journal(out / "runtime_calls.jsonl")
record = {"status": "IN_PROGRESS", "scope": "RESTORE_ONLY_NOT_ACCEPTANCE", "cleanup_errors": [],
          "continuity": "不复用旧DDR、权重或冷启动连续性"}
xsdb = session = channel = controller = None
owner = {}
helper, _ = r.load_pinned_csr_map_helper()
hc = {"sdk_files": config["runtime"]["sdk_files"]}
hr = {"verified_inputs": {"compat_artifacts": {"implemented_xsa": config["bindings"]["xsa"]}}, "cleanup_errors": []}
record["csr_debug_map_evidence"] = hr
try:
    prior_dir = ROOT / "report/evidence/S2B-T18/stage3_to_2b_restore_20261021_r02"
    prior = {}
    for name, sha in (("restore_result.json", "2fca8c0593ef737a5b5ec24bebcecba522c4154ee5af987f55f4c186483e8d8d"),
                      ("jtag_result.json", "9e1c5176788d2a16618fbb9ce638cf22dc5b5edc414ee76bb9d33b2198813f04")):
        path, raw = r.verify_binding({"path": str(prior_dir / name), "sha256": sha}, name, max_bytes=8 * 1024 * 1024)
        prior[name] = r.strict_json(raw)
        record.setdefault("prior_evidence", {})[name] = {"path": str(path), "sha256": sha}
    old = prior["restore_result.json"]
    old_jtag = prior["jtag_result.json"]
    r.require(old["status"] == "FAILED_RESTORE" and old["cleanup_errors"] == [] and
              old["video_debug_map"]["cleanup"] == "UNLOADED_AND_SDK_MAP_EMPTY" and
              len(old["vdma"]) == 2 and all(row["status"] == "HALTED_RUNSTOP0" for row in old["vdma"]) and
              old_jtag["system_reset"]["after"]["boot_mode"] == 0 and
              any(row["phase"] == "after_system_reset" and row["status"] == "PASS" and row["eos"] == 0
                  for row in old_jtag["configuration_observations"]), "前次没有完成VDMA停稳及EOS0复位")
    state = r.exact_path(r"D:\codex-worktrees\dbdf\.codex\STATE.md")
    last_line = state.read_text(encoding="utf-8").strip().splitlines()[-1]
    r.require("状态/下一接手方=`OFFERED / DSH 阶段三总控`" in last_line, "阶段3交出状态已改变")
    record["stage3_state"] = {"path": str(state), "sha256": r.digest(state.read_bytes()), "last_line": last_line}
    record["identity"] = runtime.identity(config)
    xsdb, serial = runtime.modules(config)
    session, channel = runtime.session(xsdb, serial, config, journal, lambda value: None)
    controller = apis.jtag.JtagController(session, config["bindings"], out)
    controller.select_and_gate()
    controller.observe_config_status("resume_after_verified_reset", 0)
    live_pc = {"cpu0_pc": controller.pc(), "cpu1_pc": controller.pc("cpu1")}
    r.require(all(value == old_jtag["system_reset"]["after"][key] for key, value in live_pc.items()), "复位后PC现场已改变")
    record["pre_deployment_pc"] = live_pc
    controller.system_reset_stop(config["cold_basis"])
    helper.register_csr_debug_map(hc, hr, journal, session, controller, owner)
    controller.deploy()
    controller.call("cpu0.stop.restored_app", controller.targets["cpu0"].stop)
    controller.gate()
    record["restored_csr"] = controller.stable_csr("restored_2b")
    apis.csr_flow.csr.checked_snapshot(record["restored_csr"])
    apis.csr_flow.csr.idle(record["restored_csr"])
    record["restored_pc"] = controller.pc()
    record["status"] = "RESTORED_2B_IDLE_APP_STOPPED_NOT_ACCEPTANCE"
except BaseException as error:
    record.update(status="FAILED_RESTORE", error=repr(error), traceback=traceback.format_exc())
    if controller is not None and controller.cpu0_touched:
        controller.fail_stop()
finally:
    for label, action in (("controller", lambda: controller.close() if controller else None),
                          ("map", lambda: helper.clear_csr_debug_map(hc, hr, journal, session, owner) if session and owner.get("attempted") else None),
                          ("session", lambda: session.disconnect(**({"chan": channel} if channel is not None else {})) if session else None),
                          ("xsdb", lambda: xsdb.dispose() if xsdb else None)):
        try:
            action()
        except BaseException as error:
            record["cleanup_errors"].append({"step": label, "error": repr(error)})
    journal.close()
    record["cleanup_errors"].extend({"step": "map_helper", "error": error} for error in hr["cleanup_errors"])
    r.save_json_new(out / "restore_result.json", record)
print(json.dumps({key: record.get(key) for key in ("status", "error", "restored_pc", "restored_csr", "cleanup_errors")}, ensure_ascii=False))
raise SystemExit(0 if record["status"].startswith("RESTORED_") and not record["cleanup_errors"] else 2)
