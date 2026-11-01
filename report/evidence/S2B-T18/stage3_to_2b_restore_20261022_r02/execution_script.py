"""从已验证BootROM/EOS0现场以全新XSDB会话恢复R04原始2B应用。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import traceback
from datetime import datetime, timedelta, timezone

ROOT = Path(r"D:\FPGA_Competition\w2b")
RUN_NAME = "stage3_to_2b_restore_20261022_r02"
OUT = ROOT / "report/evidence/S2B-T18" / RUN_NAME
RUNTIME = ROOT / "vitis/run_s2b_model_acceptance.py"
BASE_CONFIG = ROOT / "report/evidence/S2B-T18/formal_online_20261018_r01/model_config_csr_20261019_r10.json"
SDK_CONFIG = ROOT / "report/evidence/S2B-T18/formal_online_20261018_r01/rebuilt_app_config_20261021_r02.json"
SERVER_IDENTITY = ROOT / "tmp/2B/hw_server_20261022.json"
PRIOR_RESULT = ROOT / "report/evidence/S2B-T18/stage3_to_2b_restore_20261022_r01/restore_result.json"
PRIOR_RESULT_SHA256 = "66cbd23a74fb60fb729048529c6f7e4762275ee7a30047d60da558e48cf3e54e"
EXPECTED_CPU0_PC = 0xFFFFFF28
EXPECTED_CPU1_PC = 0xFFFFFF34
EXPECTED_APP_SHA256 = "a51499895e9387a74db87a3267843b9fbf7fdfa8b6646fcbc5db01485e090bf8"

sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("restore_bootrom_runtime", RUNTIME)
r = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r
spec.loader.exec_module(r)


def sha(raw: bytes) -> str:
    """计算原始字节SHA-256。"""
    return hashlib.sha256(raw).hexdigest()


def save_json(path: Path, value: object) -> None:
    """以独占创建方式保存UTF-8证据并同步到磁盘。"""
    raw = (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2, default=repr) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        import os
        os.fsync(stream.fileno())


def build_config() -> dict:
    """沿用R10冻结的R04部署输入，更新官方SDK、服务、HEAD与runner绑定。"""
    config = r.strict_json(r.exact_path(BASE_CONFIG, "file").read_bytes())
    sdk_config = r.strict_json(r.exact_path(SDK_CONFIG, "file").read_bytes())
    config["runtime"] = sdk_config["runtime"]
    config["hw_server"] = r.strict_json(r.exact_path(SERVER_IDENTITY, "file").read_bytes())
    config["source_commit"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
    runner = r.exact_path(RUNTIME, "file")
    config["bindings"]["runner_source"] = {"path": str(runner), "sha256": sha(runner.read_bytes())}
    app = r.exact_path(config["bindings"]["app_elf"]["path"], "file")
    r.require(sha(app.read_bytes()) == EXPECTED_APP_SHA256 and
              config["bindings"]["app_elf"]["sha256"] == EXPECTED_APP_SHA256,
              "R04原始infer ELF路径或SHA不符")
    config["run_id"] = RUN_NAME
    return config


def verify_prior_failure() -> dict:
    """仅核对前次失败回执用于解释PC位置，不继承其复位或总线连续性。"""
    path, raw = r.verify_binding({"path": str(PRIOR_RESULT), "sha256": PRIOR_RESULT_SHA256},
                                 "r01_restore_failure_locator", max_bytes=8 * 1024 * 1024)
    result = r.strict_json(raw)
    r.require(result.get("status") == "FAILED_RESTORE" and result.get("cleanup_errors") == [] and
              result.get("preflight_cpu", {}).get("pc_before") ==
                  {"cpu0": EXPECTED_CPU0_PC, "cpu1": EXPECTED_CPU1_PC} and
              result.get("preflight_cpu", {}).get("pc_after") ==
                  {"cpu0": EXPECTED_CPU0_PC, "cpu1": EXPECTED_CPU1_PC},
              "r01失败回执不是预期的BootROM PC现场定位证据")
    return {"path": str(path), "sha256": PRIOR_RESULT_SHA256,
            "use": "PC_LOCATOR_ONLY_NO_RESET_OR_COLD_CONTINUITY_REUSE"}


def require_bootrom_config(controller) -> dict:
    """核验CONFIG_STATUS显示EOS0、DONE/GWE/GTS关闭及启动状态机未完成。"""
    controller.observe_config_status("bootrom_pre_restore", 0)
    observation = controller.record["configuration_observations"][-1]
    fields = {row["name"]: row["value"] for row in observation["fields"]}
    required = {"END OF STARTUP (EOS) STATUS": 0, "DONE INTERNAL SIGNAL STATUS": 0,
                "DONE PIN": 0, "GWE STATUS": 0, "GTS_CFG_B STATUS": 0,
                "CFG STARTUP STATE MACHINE PHASE": 0}
    r.require(all(fields.get(name) == value for name, value in required.items()),
              "CONFIG_STATUS不是EOS0且PL未完成配置的BootROM现场")
    return observation


def main() -> int:
    """保存输入与硬件观察，只有实际BootROM/EOS0满足谓词后才部署2B。"""
    r.require(ROOT.is_dir() and OUT.parent.is_dir() and not OUT.exists(),
              "本RunId证据目录不存在或已存在，拒绝覆盖")
    OUT.mkdir()
    script_copy = OUT / "execution_script.py"
    script_copy.write_bytes(Path(__file__).read_bytes())
    prior = verify_prior_failure()
    config = build_config()
    config_raw = (json.dumps(config, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")
    with (OUT / "input_config.json").open("xb") as stream:
        stream.write(config_raw)
        stream.flush()
        import os
        os.fsync(stream.fileno())
    save_json(OUT / "input_basis.json", {"prior_failure_locator": prior,
        "continuity": "NOT_REUSED", "current_server_identity": config["hw_server"],
        "source_commit": config["source_commit"],
        "runner_source": config["bindings"]["runner_source"],
        "original_r04_infer": config["bindings"]["app_elf"],
        "runtime_sdk_file_count": len(config["runtime"]["sdk_files"])})
    apis = r.load_apis("csr")
    runtime = r.ProductionRuntime()
    journal = r.Journal(OUT / "runtime_calls.jsonl")
    xsdb = session = channel = controller = None
    helper, owner = None, {}
    helper_record = {"verified_inputs": {"compat_artifacts": {"implemented_xsa": config["bindings"]["xsa"]}},
                     "cleanup_errors": []}
    record = {"schema_version": 1, "run_id": RUN_NAME,
        "scope": "RESTORE_FROM_VERIFIED_BOOTROM_TO_R04_2B_NOT_ACCEPTANCE",
        "status": "IN_PROGRESS", "source_commit": config["source_commit"],
        "input_config_sha256": sha(config_raw), "prior_failure_locator": prior,
        "cleanup_errors": [], "continuity": "不复用旧DDR、权重、VDMA或POR连续性",
        "limitations": ["不执行UART模型请求、不做G3/G4/G5验收。",
                        "不修改传感器/I2C寄存器；部署仅用已绑定R04 init/XSA/full bit/original infer。",
                        "system reset不证明物理POR或旧AXI生命周期终止。", "峰值内存未测。"]}
    try:
        record["runtime_identity"] = runtime.identity(config)
        xsdb, serial = runtime.modules(config)
        session, channel = runtime.session(xsdb, serial, config, journal, lambda value: None)
        controller = apis.jtag.JtagController(session, config["bindings"], OUT)
        controller.select_and_gate()
        pcs = {"cpu0": controller.pc(), "cpu1": controller.pc("cpu1")}
        states = {"cpu0": controller.state("cpu0"), "cpu1": controller.state("cpu1")}
        boot_mode = controller.words(0xF800025C, 1)[0]
        r.require(all(value.startswith("Stopped") for value in states.values()),
                  "当前CPU核非停止态，拒绝system reset与部署")
        r.require(pcs == {"cpu0": EXPECTED_CPU0_PC, "cpu1": EXPECTED_CPU1_PC},
                  "当前PC不再是r01观测到的BootROM等待现场")
        r.require(boot_mode == 0, "当前BOOT_MODE不是JTAG=0")
        bootrom_status = require_bootrom_config(controller)
        record["verified_bootrom_precondition"] = {"cpu_states": states, "pc": pcs,
            "boot_mode": boot_mode, "configuration_status": bootrom_status,
            "status": "STOPPED_CORES_JTAG_BOOTROM_EOS0_PL_UNCONFIGURED"}
        controller.system_reset_stop(config["cold_basis"])
        record["system_reset"] = controller.record.get("system_reset")
        helper, _ = r.load_pinned_csr_map_helper()
        helper_config = {"sdk_files": config["runtime"]["sdk_files"]}
        helper.register_csr_debug_map(helper_config, helper_record, journal, session, controller, owner)
        controller.deploy()
        controller.call("cpu0.stop.restored_app", controller.targets["cpu0"].stop)
        controller.gate()
        restored = controller.stable_csr("restored_2b_safe_idle")
        apis.csr_flow.csr.idle(restored)
        record["restored_csr"] = restored
        record["restored_pc"] = controller.pc()
        record["deployment"] = controller.record
        record["csr_debug_map"] = helper_record
        record["status"] = "RESTORED_2B_IDLE_APP_STOPPED_NOT_ACCEPTANCE"
    except BaseException as error:
        record.update(status="FAILED_RESTORE", error=repr(error), traceback=traceback.format_exc())
        if controller is not None and controller.cpu0_touched and not controller.failed:
            try:
                controller.fail_stop()
            except BaseException as stop_error:
                record["fail_stop_error"] = repr(stop_error)
    finally:
        if helper is not None and session is not None and owner.get("attempted"):
            try:
                helper.clear_csr_debug_map({"sdk_files": config["runtime"]["sdk_files"]},
                    helper_record, journal, session, owner)
            except BaseException as error:
                record["cleanup_errors"].append({"step": "csr_debug_map", "error": repr(error)})
        for name, action in (("controller", lambda: controller.close() if controller else None),
                             ("session", lambda: session.disconnect(**({"chan": channel} if channel is not None else {})) if session else None),
                             ("xsdb", lambda: xsdb.dispose() if xsdb else None),
                             ("journal", journal.close)):
            try:
                action()
            except BaseException as error:
                record["cleanup_errors"].append({"step": name, "error": repr(error)})
        record["cleanup_errors"].extend({"step": "csr_map_helper", "error": error}
                                        for error in helper_record["cleanup_errors"])
        record["finished_at_utc8"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
        save_json(OUT / "restore_result.json", record)
    print(json.dumps({key: record.get(key) for key in
        ("status", "error", "verified_bootrom_precondition", "restored_pc", "restored_csr", "cleanup_errors")},
        ensure_ascii=False))
    return 0 if record["status"] == "RESTORED_2B_IDLE_APP_STOPPED_NOT_ACCEPTANCE" and not record["cleanup_errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
