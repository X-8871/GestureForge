#!/usr/bin/env python3
"""只通过显式配置运行重建app的有限实板验收。"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).absolute().parents[1]
TZ = timezone(timedelta(hours=8))
RUNNER_PATH = ROOT / "vitis/run_s2b_model_acceptance.py"
CONFIG_KEYS = {"schema_version", "source_commit", "run_id", "bindings", "cold_basis",
               "runtime", "serial", "hw_server", "response_timeout_seconds"}
for import_path in (str(ROOT), str(ROOT / "verification")):
    if import_path not in sys.path:
        sys.path.insert(0, import_path)

try:
    from vitis import run_s2b_model_acceptance as production
except ImportError:
    import run_s2b_model_acceptance as production

from verification import s2b_rebuilt_app_acceptance as acceptance


class RebuiltAppRunnerError(RuntimeError):
    """配置、真实设备身份或本次运行未满足有限验收范围。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RebuiltAppRunnerError(message)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _write_new(path: Path, raw: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        import os
        os.fsync(stream.fileno())


def _current_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True, encoding="utf-8")
    _require(result.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}", result.stdout.strip()) is not None,
             "无法读取完整HEAD提交")
    return result.stdout.strip()


def validate_config(config: object) -> dict:
    """核验新ELF、R04部署输入、冷回执及官方运行时配置，不检查或声称旧G0。"""
    _require(type(config) is dict and set(config) == CONFIG_KEYS, "独立入口config字段集合错误")
    _require(type(config["schema_version"]) is int and config["schema_version"] == 1,
             "config schema_version错误")
    _require(type(config["run_id"]) is str and re.fullmatch(r"rebuilt_app_acceptance_[A-Za-z0-9_-]+",
             config["run_id"]) is not None, "需要新的独立T18 RunId")
    _require(config["source_commit"] == _current_commit(), "config source_commit不是当前HEAD")
    _require(type(config["response_timeout_seconds"]) is int and
             1 <= config["response_timeout_seconds"] <= 900, "UART响应期限超出允许范围")
    recovery = acceptance.verify_recovery_inputs()
    expected_bindings = {
        "app_elf": recovery["new_app_elf"],
        "init_elf": recovery["original_r04_init_elf"],
        "xsa": recovery["original_r04_xsa"],
        "bit": recovery["original_r04_bit"],
    }
    bindings = config["bindings"]
    _require(type(bindings) is dict and set(bindings) == production.CONTROLLER_BINDING_KEYS,
             "controller bindings字段集合错误")
    for name, expected in expected_bindings.items():
        _require(bindings.get(name) == {"path": expected["path"], "sha256": expected["sha256"]},
                 "controller未精确绑定恢复scope输入：" + name)
    for name, item in bindings.items():
        production.verify_binding(item, "controller binding " + name,
                                  max_bytes=128 * 1024 * 1024, within_root=False)
    _require(bindings["tool_source"]["path"] == str(ROOT / "verification/s2b_board_jtag.py") and
             bindings["transport_source"]["path"] == str(ROOT / "verification/s2b_board_transport.py") and
             bindings["acceptance_source"]["path"] == str(ROOT / "verification/s2b_board_acceptance.py") and
             bindings["runner_source"]["path"] == str(RUNNER_PATH),
             "生产controller来源绑定路径错误")
    production._verify_pinned_basis(config["cold_basis"], "R04冷生命周期依据",
                                    production.COLD_BASIS_PATH, production.COLD_BASIS_SHA256)
    _require(type(config["runtime"]) is dict and
             {"sdk_init", "sdk_files", "pyserial_init", "pyserial_files", "pyserial_version"} <=
             set(config["runtime"]), "缺少ProductionRuntime所需官方XSDB/pyserial绑定")
    _require(type(config["serial"]) is dict and type(config["serial"].get("identity")) is dict and
             type(config["hw_server"]) is dict, "缺少ProductionRuntime系统身份绑定")
    return {"recovery": recovery, "source_sha256": recovery["application_source"]["sha256"],
            "new_app_elf": recovery["new_app_elf"], "scope": "REBUILT_APP_SINGLE_SAMPLE_AND_DDR256B_PROBE",
            "old_g0_receipt": "NOT_REUSED"}


def _execute_acceptance(execute_fn, controller, wire, *, run_dir: Path, run_id: str,
                        source_sha256: str, cold_basis: dict, journal, csr_map):
    """核对包装器创建的日志目录，再把相同controller对象交给真实执行入口。"""
    actual = acceptance.validate_deployment_directory(controller.run, run_id)
    expected = run_dir / "deployment"
    _require(actual == expected, "包装器部署目录与controller.run不一致")
    return execute_fn(controller, wire, run_id=run_id, source_sha256=source_sha256,
                      cold_basis=cold_basis, journal=journal, csr_map=csr_map)


def run(config_path: str | Path, *, runtime=None) -> dict:
    """调用方提供显式配置；ProductionRuntime只接入其声明的服务器、SDK与串口。"""
    config_file = production.exact_path(config_path)
    _require(config_file.is_relative_to(ROOT) and config_file.stat().st_size <= 1024 * 1024,
             "config必须是仓库内、不超过1MiB的显式文件")
    config_raw = config_file.read_bytes()
    config = production.strict_json(config_raw)
    try:
        checked = validate_config(config)
    except (production.RunnerError, acceptance.RebuiltAppAcceptanceError) as validation_error:
        raise RebuiltAppRunnerError("重建app离线准入失败：" + str(validation_error)) from validation_error
    parent = production.exact_path(ROOT / "report/evidence/S2B-T18", "directory")
    run_dir = parent / config["run_id"]
    _require(not run_dir.exists(), "拒绝覆盖已存在T18 RunId")
    run_dir.mkdir()
    run_dir = production.exact_path(run_dir, "directory")
    _write_new(run_dir / "input_config.json", config_raw)
    journal = production.Journal(run_dir / "orchestrator_calls.jsonl")
    record = {"schema_version": 1, "status": "IN_PROGRESS",
              "scope": checked["scope"], "hardware_execution": "REAL_PRODUCTION_RUNTIME_REQUESTED",
              "run_id": config["run_id"], "source_commit": config["source_commit"],
              "config": {"path": str(config_file), "sha256": _sha(config_raw)},
              "runtime_source": {"path": str(RUNNER_PATH), "sha256": _sha(RUNNER_PATH.read_bytes())},
              "acceptance_source": {"path": str(Path(acceptance.__file__)),
                                    "sha256": _sha(Path(acceptance.__file__).read_bytes())},
              "identity_snapshots": [], "cleanup_steps": [], "cleanup_errors": [],
              "limitations": ["不执行旧formal G0应用准入；独立记录本次重建ELF及输入。",
                              "只运行R04真实256B CPU↔DAP探针、一次真实weights及sample000黄金。",
                              "不重复109样本或1000连续任务，不作HP带宽/DDR板级身份或G4/G5结论。",
                              "峰值内存未测。"]}
    started = time.monotonic()
    runtime = runtime or production.ProductionRuntime()
    objects = {"xsdb": None, "serial": None, "session": None, "channel": None,
               "controller": None, "port": None, "wire": None, "rx": None, "tx": None,
               "csr_map": None}
    helper_record = None
    error = None
    apis = None
    try:
        record["preflight"] = checked
        record["identity_snapshots"].append({"label": "before_runtime",
            **journal.call("identity.before_runtime", runtime.identity, config)})
        helper, helper_source = production.load_pinned_csr_map_helper()
        apis = production.load_apis("model")
        record["csr_debug_map_helper"] = helper_source
        objects["xsdb"], objects["serial"] = journal.call("runtime.import_bound_modules", runtime.modules, config)
        objects["session"], objects["channel"] = runtime.session(
            objects["xsdb"], objects["serial"], config, journal,
            lambda value: objects.__setitem__("session", value))
        record["identity_snapshots"].append({"label": "after_connect",
            **journal.call("identity.after_connect", runtime.identity, config)})
        deployment_dir = run_dir / "deployment"
        deployment_dir.mkdir()
        objects["controller"] = apis.jtag.JtagController(
            objects["session"], config["bindings"], deployment_dir)
        map_config = {"sdk_files": config["runtime"]["sdk_files"]}
        helper_record = {"verified_inputs": {"compat_artifacts": {
            "implemented_xsa": config["bindings"]["xsa"]}}, "cleanup_errors": []}
        objects["csr_map"] = (helper, map_config, helper_record, objects["session"], {})
        record["identity_snapshots"].append({"label": "before_serial",
            **journal.call("identity.before_serial", runtime.identity, config)})
        objects["port"] = runtime.serial(objects["serial"], config, journal,
                                           lambda value: objects.__setitem__("port", value))
        record["identity_snapshots"].append({"label": "after_serial_open",
            **journal.call("identity.after_serial_open", runtime.identity, config)})
        objects["rx"] = (run_dir / "uart_rx_raw.bin").open("xb")
        objects["tx"] = (run_dir / "uart_tx_headers_raw.bin").open("xb")
        objects["wire"] = apis.jtag.JtagWireSession(
            objects["port"], objects["rx"], objects["tx"],
            response_timeout=config["response_timeout_seconds"])
        record["acceptance"] = _execute_acceptance(
            acceptance.execute, objects["controller"], objects["wire"], run_dir=run_dir,
            run_id=config["run_id"], source_sha256=checked["source_sha256"],
            cold_basis=config["cold_basis"], journal=journal, csr_map=objects["csr_map"])
        _require(record["acceptance"].get("status") ==
                 "PASS_REBUILT_APP_SINGLE_SAMPLE_AND_DDR256B_PROBE", "重建ELF有限实板验收未通过")
        record["status"] = "PASS_REBUILT_APP_SINGLE_SAMPLE_AND_DDR256B_PROBE"
    except BaseException as caught:
        error = caught
        record.update(status="FAILED_REBUILT_APP_ACCEPTANCE", error=repr(caught),
                      traceback=traceback.format_exc())
        if objects["wire"] is not None:
            objects["wire"].failed = True
        controller = objects["controller"]
        if controller is not None and not controller.failed:
            controller.failed = True
            try:
                controller.fail_stop()
                record["cleanup_steps"].append({"step": "failure_fail_stop", "status": "RETURNED"})
            except BaseException as stop_error:
                record["cleanup_errors"].append({"step": "failure_fail_stop", "error": repr(stop_error)})
    finally:
        port = objects["port"]
        if port is not None:
            try:
                if port.is_open:
                    journal.call("cleanup.serial.close", port.close)
                _require(not port.is_open, "串口关闭后仍处于打开状态")
                record["cleanup_steps"].append({"step": "serial.close", "status": "PASS"})
            except BaseException as cleanup_error:
                record["cleanup_errors"].append({"step": "serial.close", "error": repr(cleanup_error)})
        for key in ("rx", "tx"):
            stream = objects[key]
            if stream is not None:
                try:
                    stream.flush()
                    import os
                    os.fsync(stream.fileno())
                    stream.close()
                    _require(stream.closed, key + "原字节日志未关闭")
                    record["cleanup_steps"].append({"step": key + ".close", "status": "PASS"})
                except BaseException as cleanup_error:
                    record["cleanup_errors"].append({"step": key + ".close", "error": repr(cleanup_error)})
        controller = objects["controller"]
        if controller is not None:
            try:
                journal.call("cleanup.controller.close", controller.close)
                _require(controller.log.closed and not controller.failed and
                         not controller.record.get("cleanup_errors"), "controller关闭或断点清理失败")
                record["cleanup_steps"].append({"step": "controller.close", "status": "PASS"})
            except BaseException as cleanup_error:
                record["cleanup_errors"].append({"step": "controller.close", "error": repr(cleanup_error)})
        csr_map = objects["csr_map"]
        if csr_map is not None and csr_map[4].get("attempted"):
            try:
                helper, helper_config, helper_record, map_session, owner = csr_map
                journal.call("cleanup.csr_debug_map.clear", helper.clear_csr_debug_map,
                             helper_config, helper_record, journal, map_session, owner)
                _require(not helper_record.get("cleanup_errors"), "CSR debug map内部清理失败")
                record["cleanup_steps"].append({"step": "csr_debug_map.clear", "status": "PASS"})
            except BaseException as cleanup_error:
                record["cleanup_errors"].append({"step": "csr_debug_map.clear", "error": repr(cleanup_error)})
        elif csr_map is not None:
            record["cleanup_steps"].append({"step": "csr_debug_map.clear", "status": "NOT_NEEDED"})
        session = objects["session"]
        if session is not None:
            try:
                kwargs = {"chan": objects["channel"]} if objects["channel"] is not None else {}
                journal.call("cleanup.session.disconnect", session.disconnect, **kwargs)
                record["cleanup_steps"].append({"step": "session.disconnect", "status": "PASS"})
            except BaseException as cleanup_error:
                record["cleanup_errors"].append({"step": "session.disconnect", "error": repr(cleanup_error)})
        xsdb = objects["xsdb"]
        if xsdb is not None:
            try:
                journal.call("cleanup.xsdb.dispose", xsdb.dispose)
                record["cleanup_steps"].append({"step": "xsdb.dispose", "status": "PASS"})
            except BaseException as cleanup_error:
                record["cleanup_errors"].append({"step": "xsdb.dispose", "error": repr(cleanup_error)})
        try:
            record["identity_snapshots"].append({"label": "after_cleanup",
                **journal.call("identity.after_cleanup", runtime.identity, config)})
        except BaseException as cleanup_error:
            record["cleanup_errors"].append({"step": "identity.after_cleanup", "error": repr(cleanup_error)})
        if journal is not None:
            try:
                journal.close()
                record["cleanup_steps"].append({"step": "journal.close", "status": "PASS"})
            except BaseException as cleanup_error:
                record["cleanup_errors"].append({"step": "journal.close", "error": repr(cleanup_error)})

    if record["cleanup_errors"]:
        record["status"] = "FAILED_CLEANUP"
        error = error or RebuiltAppRunnerError("资源清理未全部通过")
    record["finished_at_utc8"] = datetime.now(TZ).isoformat()
    record["elapsed_seconds"] = time.monotonic() - started
    record["native_exit_code"] = 0 if error is None and record["status"].startswith("PASS_") else 2
    if helper_record is not None:
        record["csr_debug_map"] = helper_record
    if controller is not None and not controller.log.closed:
        try:
            snapshot_path = controller.run / "jtag_close_failure_snapshot.json"
            _write_new(snapshot_path, (json.dumps(controller.record, ensure_ascii=False,
                         allow_nan=False, indent=2, default=repr) + "\n").encode("utf-8"))
            controller.log.close()
            record["cleanup_errors"].append({"step": "controller.partial_log.close",
                                              "error": "controller关闭失败快照已保存"})
            record["status"] = "FAILED_CLEANUP"
            record["native_exit_code"] = 2
        except BaseException as snapshot_error:
            record["cleanup_errors"].append({"step": "controller.partial_log.close",
                                              "error": repr(snapshot_error)})
            record["status"] = "FAILED_CLEANUP"
            record["native_exit_code"] = 2
    record["raw_logs"] = []
    for path in sorted(run_dir.rglob("*")):
        if path.is_file() and path.name != "orchestrator_result.json":
            record["raw_logs"].append({"path": str(path), "bytes": path.stat().st_size,
                                       "sha256": _sha(path.read_bytes())})
    raw = (json.dumps(record, ensure_ascii=False, allow_nan=False, indent=2, default=repr) + "\n").encode("utf-8")
    _write_new(run_dir / "orchestrator_result.json", raw)
    return record


def main(argv=None) -> int:
    """命令行只接受显式config；无配置时不导入硬件运行模块。"""
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="独立重建app验收的显式T18配置")
    args = parser.parse_args(argv)
    result = run(args.config)
    print(json.dumps({"status": result["status"], "native_exit_code": result["native_exit_code"],
                      "run_id": result["run_id"]}, ensure_ascii=False))
    return result["native_exit_code"]


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RebuiltAppRunnerError, production.RunnerError, OSError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2)
