"""在官方Vitis环境借用独占JTAG服务执行一次OCM诊断，不打开UART。"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).absolute().parents[1]


def run(config_path: Path, *, run_id: str, r08_result_binding: dict, review_binding: dict) -> dict:
    """完整预检后暖连接；所有资源仅清理本次拥有的对象。"""
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location("s2b_cpu_owned_runtime", ROOT / "vitis/run_s2b_model_acceptance.py")
    runner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = runner
    spec.loader.exec_module(runner)
    from verification import s2b_cpu_bresp_experiment as experiment

    config_file = runner.exact_path(config_path)
    config_raw = config_file.read_bytes()
    config = runner.strict_json(config_raw)
    runner.validate_preflight_basis(config)
    runner.validate_csr_reentry(config, scope="csr")
    runner._verify_csr_flow_sources()
    apis = runner.load_apis("csr")
    runner.validate_v1_inputs(config, apis, scope="csr")
    parent = runner.exact_path(ROOT / "report/evidence/S2B-T20", "directory")
    runner.require(type(run_id) is str and run_id and Path(run_id).name == run_id and
                   "/" not in run_id and "\\" not in run_id and ":" not in run_id and
                   run_id not in (".", ".."), "诊断RunId必须是单个目录名")
    runner.require(not any(p.name.casefold() == run_id.casefold() for p in parent.iterdir()), "拒绝覆盖诊断RunId")
    output = parent / run_id
    output.mkdir()
    (output / "input_config.json").write_bytes(config_raw)
    journal = runner.Journal(output / "orchestrator_calls.jsonl")
    runtime = runner.ProductionRuntime()
    record = {"schema_version": 1, "status": "IN_PROGRESS", "run_id": run_id,
              "source_commit": config["source_commit"], "r08_result": r08_result_binding,
              "diagnostic_review": review_binding,
              "hardware_execution": "EXPLICIT_WARM_JTAG_CPU_DIAGNOSTIC",
              "uart_opened": False, "system_reset_or_ack_issued": False,
              "cleanup_errors": [], "limitations": ["独立OCM诊断，不是生产infer.elf运行结果。",
              "不恢复旧CPU执行上下文；安全后仅把原infer.elf下载并停在入口，后续须正式重部署与黄金恢复。"]}
    xsdb = session = channel = controller = None
    owner = {}
    helper, _ = runner.load_pinned_csr_map_helper()
    helper_config = {"sdk_files": config["runtime"]["sdk_files"]}
    helper_record = {"verified_inputs": {"compat_artifacts": {"implemented_xsa": config["bindings"]["xsa"]}},
                     "cleanup_errors": []}
    try:
        record["identity_before"] = journal.call("identity.before_warm_attach", runtime.identity, config)
        xsdb, serial_module = journal.call("runtime.import_bound_modules", runtime.modules, config)
        def capture_session(value):
            nonlocal session
            session = value
        session, channel = runtime.session(xsdb, serial_module, config, journal, capture_session)
        controller = apis.jtag.JtagController(session, config["bindings"], output)
        controller.select_and_gate()
        helper.register_csr_debug_map(helper_config, helper_record, journal, session, controller, owner)
        diag_path = runner.exact_path(experiment.DIAG_DIR / "s2b_bresp_diag.elf")
        diag_binding = {"path": str(diag_path), "sha256": hashlib.sha256(diag_path.read_bytes()).hexdigest()}
        record["experiment"] = experiment.execute_cpu_bresp_experiment(
            controller, r08_result_binding, diag_binding, review_binding, output)
        record["status"] = "DIAGNOSTIC_RESULTS_SAVED_NOT_STAGE_ACCEPTANCE"
    except BaseException as error:
        record.update(status="FAILED", error=repr(error), traceback=traceback.format_exc())
        if controller is not None:
            try:
                controller.fail_stop()
            except BaseException as stop_error:
                record["cleanup_errors"].append({"step": "failure_stop", "error": repr(stop_error)})
    finally:
        if controller is not None:
            try:
                controller.close()
            except BaseException as error:
                record["cleanup_errors"].append({"step": "controller.close", "error": repr(error)})
        if session is not None and owner.get("attempted"):
            try:
                helper.clear_csr_debug_map(helper_config, helper_record, journal, session, owner)
            except BaseException as error:
                record["cleanup_errors"].append({"step": "csr_debug_map.clear", "error": repr(error)})
        record["cleanup_errors"].extend(helper_record.get("cleanup_errors", []))
        if session is not None:
            try:
                journal.call("session.disconnect", session.disconnect, **({"chan": channel} if channel is not None else {}))
            except BaseException as error:
                record["cleanup_errors"].append({"step": "session.disconnect", "error": repr(error)})
        if xsdb is not None:
            try:
                journal.call("xsdb.dispose", xsdb.dispose)
            except BaseException as error:
                record["cleanup_errors"].append({"step": "xsdb.dispose", "error": repr(error)})
        try:
            journal.close()
        except BaseException as error:
            record["cleanup_errors"].append({"step": "journal.close", "error": repr(error)})
        if record["cleanup_errors"]:
            record["status"] = "FAILED"
        record["native_exit_code"] = 2 if record["status"] == "FAILED" else 0
        runner.save_json_new(output / "launcher_result.json", record)
        files = [runner._manifest_file("result", p) for p in sorted(output.rglob("*")) if p.is_file()]
        files.extend(runner._manifest_file("source", p) for p in
                     (Path(__file__), Path(experiment.__file__), ROOT / "vitis/s2b_bresp_diag.S",
                      ROOT / "vitis/build_s2b_bresp_diag.py"))
        inputs = [binding["path"] for binding in config["bindings"].values()]
        inputs.extend((r08_result_binding["path"], review_binding["path"],
                       str(experiment.DIAG_DIR / "s2b_bresp_diag.elf"),
                       str(experiment.DIAG_DIR / "build_result.json")))
        files.extend(runner._manifest_file("input", runner.exact_path(p)) for p in sorted(set(inputs)))
        runner.save_json_new(output / "delivery_manifest.json", {
            "schema_version": 1, "stage": "2B", "task_id": "S2B-T20", "run_id": run_id,
            "source_commit": config["source_commit"], "evidence_dir": output.relative_to(ROOT).as_posix(),
            "files": files, "checks": [{"name": "OCM诊断执行", "status": "FAIL" if record["native_exit_code"] else "PASS",
            "command": "run_s2b_cpu_bresp_experiment.run(explicit_config, explicit_r08_binding)",
            "exit_code": record["native_exit_code"], "reason": "仅表示诊断入口执行；具体SLVERR/UNKNOWN与安全返回见experiment，不表示阶段验收。"}],
            "tool_versions": {"Python": sys.version.split()[0]}, "limitations": record["limitations"]})
    return record
