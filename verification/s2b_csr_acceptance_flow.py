"""T18内固定CSR恢复顺序；复用既有控制器、UART与T20证据helper。"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import traceback

from verification import s2b_board_acceptance as model
from verification import s2b_board_jtag as jtag
from verification import s2b_board_transport as transport
from verification import s2b_csr_board_acceptance as csr
from verification import s2b_csr_busy_observer as busy
from verification import s2b_csr_deadline_flow as deadline

ROOT = Path(__file__).absolute().parents[1]
TZ = timezone(timedelta(hours=8))
BOARD_SOURCE_SHA256 = "9ad1060b08eb8429770e58b21f8a4eea542a7bd8949ded9a0c920986709bad97"
BUSY_SOURCE_SHA256 = "bc6d69c8de4594e65a9db95443d36484ecd1ed0631158e915662060522b7197c"


def _save(path: Path, value: object) -> bytes:
    raw = (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        import os
        os.fsync(stream.fileno())
    return raw


def _binding(path: Path) -> dict:
    actual = transport.exact_path(path)
    return {"path": str(actual), "sha256": transport.digest(actual.read_bytes())}


def _scope_check(results: dict) -> dict:
    """用检查器约定保存受阻状态，不给未执行的检查伪造退出码。"""
    passed = results["status"] in ("PASS_CSR_RECOVERY_SCOPE_ONLY",
                                   "PASS_CSR_DEADLINE_SCOPE_ONLY")
    blocked = results["status"] == "BLOCKED_CSR_RECOVERY_SCOPE_ONLY"
    reason = results.get("error", "已执行场景与未关闭项见stages/blockers/deadline_scope；模型corpus与压力未执行。")
    if results["status"] == "PASS_CSR_DEADLINE_SCOPE_ONLY":
        reason = "deadline有限范围通过；本profile的busy与ABORT未运行，真实pending晚响应未声称。"
    return {"name": "CSR恢复固定顺序", "status": "PASS" if passed else "BLOCKED" if blocked else "FAIL",
            "command": "s2b_csr_acceptance_flow.execute(borrowed_controller, borrowed_wire)",
            "exit_code": 0 if passed else None if blocked else 1,
            "reason": reason}


def _profile_stages(config: dict) -> tuple[str, ...]:
    """返回生产流程实际采用的互斥阶段，便于离线核对路由。"""
    if config.get("csr_profile") == "with_deadlines":
        return ("deadline",)
    return ("busy", "reaccept", "abort")


def _scene_config(controller, config: dict, checked: dict, apis, *, label: str,
                   static: bool, run_dir: Path) -> dict:
    snapshot = controller.stable_csr("t18.csr_scope." + label)
    csr.checked_snapshot(snapshot)
    csr.idle(snapshot)
    scene = {"schema_version": 1,
             "kind": "s2b-csr-static-scene/1.0.0" if static else "s2b-csr-uart-scene/1.0.0",
             "expected_snapshot": {str(key): snapshot[key] for key in csr.OFFSETS}}
    scene_path = run_dir / (label + "_scene.json")
    scene_raw = _save(scene_path, scene)
    value = {"schema_version": 1, "source_commit": config["source_commit"],
             "bindings": controller.bindings, "build_details": config["build_details"]["path"],
             "visibility_proof": config["visibility_proof"]["path"],
             "visibility_review": config["visibility_review"]["path"],
             "visibility_review_sha256": config["visibility_review"]["sha256"],
             "final_platform_manifest": config["final_platform_manifest"]["path"],
             "final_review": config["final_review"]["path"],
             "final_review_sha256": config["final_review"]["sha256"],
             "scene": {"path": str(scene_path), "sha256": transport.digest(scene_raw)}}
    path = run_dir / (label + "_config.json")
    raw = _save(path, value)
    return {"path": str(path), "sha256": transport.digest(raw)}


def execute(controller, wire, config: dict, checked: dict, apis, admission: dict,
            journal=None) -> dict:
    """按选定CSR profile完成sample000恢复与静止CSR矩阵。"""
    require = model.require
    run_dir = checked["run_dir"]
    run_dir.mkdir()
    with_deadlines = config.get("csr_profile") == "with_deadlines"
    profile_stages = set(_profile_stages(config))
    results = {"schema_version": 1,
               "scope": "CSR_DEADLINE_LIMITED" if with_deadlines else "CSR_RECOVERY_ONLY",
               "status": "IN_PROGRESS", "hardware_execution": "BORROWED_SESSION_UART_DAP_REQUESTED",
               "stages": [], "t20_outputs": [], "blockers": [], "limitations": [
                   "不代表109样本corpus或1000次连续压力完成。",
                   "short_deadline保留既有BLOCKED，本流程未执行。",
                   "静止矩阵内busy_start仍为BLOCKED；实际忙启动拒绝由独立BusyObserver阶段记录。",
                   "静止矩阵wire_after_external_csr仍为BLOCKED；该helper没有外部epoch同步。"]}
    if with_deadlines:
        results["limitations"][1] = "此profile只声明deadline有限范围；busy与ABORT本profile未运行，未证明真实pending晚响应。"
        results["limitations"][2] = "静止矩阵busy_start为BLOCKED；此profile不运行真实BusyObserver。"
    t20_runs: list[Path] = []

    def register(label: str, result: dict, output_dir: Path):
        results["stages"].append({"name": label, "status": result.get("status", "UNKNOWN"),
                                  "evidence_dir": str(output_dir)})

    def fresh_run(label: str) -> Path:
        path = t20_root / (config["run_id"] + "_" + label)
        require(not any(item.name.casefold() == path.name.casefold() for item in t20_root.iterdir()),
                "拒绝覆盖已有T20 RunId：" + str(path))
        t20_runs.append(path)
        return path

    def persist_result() -> None:
        outputs = {}
        for directory in t20_runs:
            if directory.is_dir():
                for path in sorted(directory.rglob("*")):
                    if path.is_file():
                        item = _binding(path)
                        outputs[item["path"]] = item
        for item in results.get("deadline_scope", {}).get("t20_outputs", []):
            outputs[item["path"]] = item
        results["t20_outputs"] = [outputs[key] for key in sorted(outputs)]
        result_path = run_dir / "acceptance_result.json"
        raw = (json.dumps(results, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")
        with result_path.open("wb") as stream:
            stream.write(raw)
            stream.flush()
            import os
            os.fsync(stream.fileno())
        files = {}
        for path in sorted(run_dir.rglob("*")):
            if path.is_file() and path.name != "delivery_manifest.json":
                item = _binding(path)
                files[item["path"]] = {"path": Path(item["path"]).relative_to(ROOT).as_posix(),
                                        "sha256": item["sha256"], "role": "result"}
        for item in results["t20_outputs"]:
            files[item["path"]] = {"path": Path(item["path"]).relative_to(ROOT).as_posix(),
                                   "sha256": item["sha256"], "role": "result"}
        manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T18",
                    "run_id": run_dir.name, "source_commit": config["source_commit"],
                    "evidence_dir": run_dir.relative_to(ROOT).as_posix(),
                    "files": [files[key] for key in sorted(files)],
                    "checks": [_scope_check(results)],
                    "tool_versions": {"Python": __import__("sys").version.split()[0]},
                    "limitations": results["limitations"]}
        manifest_path = run_dir / "delivery_manifest.json"
        raw = (json.dumps(manifest, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")
        with manifest_path.open("wb") as stream:
            stream.write(raw)
            stream.flush()
            import os
            os.fsync(stream.fileno())

    try:
        _, preparation_raw = model.read_bound(config["preparation"])
        plan = json.loads(preparation_raw.decode("utf-8"))
        model.validate_plan(plan)
        t20_root = transport.exact_path(ROOT / "report/evidence/S2B-T20", "directory")
        transport.require(not wire.failed and wire.abort_pending is None, "CSR流程开始前wire失败或有pending")

        seed_dir = fresh_run("csr_seed_sample000")
        seed = model.AcceptanceRunner(wire, seed_dir, admission, capture_wire_receipts=True)
        seed.record["hardware_execution"] = "BORROWED_SESSION_UART_DAP_REQUESTED"
        weight_path, weights = model.read_bound(plan["weights"])
        seq = wire.last_sequence + 1
        request, header = transport.make_request(transport.OP_WEIGHTS, seq, 0, weights)
        seed.send(request, header, weights, {"path": str(weight_path), "sha256": transport.digest(weights)})
        seed.receive(request, 0)
        seed.run_input(plan["rows"][0], seq + 1, 0, 1, config["core_timeout"],
                       config["drain_timeout"], "csr_seed")
        register("sample000_seed_frame0", seed.finish("PASS_SAMPLE000_SEED_ONLY"), seed_dir)

        if "busy" in profile_stages:
            busy_config = _scene_config(controller, config, checked, apis, label="before_busy_start",
                                         static=False, run_dir=run_dir)
            busy_dir = fresh_run("csr_busy_observer")
            busy_result = busy.execute_busy_start(controller, wire, busy_config, busy_dir,
                                                  preparation=config["preparation"],
                                                  observation_seconds=5.0, poll_seconds=0.01)
            register("real_busy_start_response_last_reject", busy_result, busy_dir)
            busy_status = busy_result.get("status")
            require(busy_status in ("PASS_BUSY_START_REJECTION_AND_GOLD",
                                   "BUSY_REJECTION_AND_GOLD_BRESP_UNRESOLVED"),
                    "实际忙启动拒绝BusyObserver未通过")
            if busy_status == "BUSY_REJECTION_AND_GOLD_BRESP_UNRESOLVED":
                results["blockers"].append({"name": "busy_start_native_bresp", "status": "BLOCKED",
                    "reason": "通用AHB错误及拒绝副作用已观测；具体SLVERR响应未由SDK暴露。",
                    "evidence_dir": str(busy_dir)})

        if "reaccept" in profile_stages:
            second_dir = fresh_run("csr_reaccept_sample000_frame0")
            second = model.AcceptanceRunner(wire, second_dir, admission, capture_wire_receipts=True)
            second.record["hardware_execution"] = "BORROWED_SESSION_UART_DAP_REQUESTED"
            second.run_input(plan["rows"][0], wire.last_sequence + 1, 0, 1,
                             config["core_timeout"], config["drain_timeout"], "csr_reaccept")
            register("sample000_reaccept_frame0", second.finish("PASS_SAMPLE000_REACCEPT_FRAME0_ONLY"), second_dir)

        if "deadline" in profile_stages:
            deadline_dir = run_dir / "deadline_scope"
            deadline_checked = {**checked, "run_dir": deadline_dir}
            results["deadline_scope"] = deadline.execute_after_seed(
                controller, wire, config, deadline_checked, apis, admission, journal)
            register("actual_deadline_and_golden_recovery", results["deadline_scope"], deadline_dir)
            require(results["deadline_scope"].get("status") == "PASS_CSR_DEADLINE_SCOPE_ONLY",
                    "实际deadline子流程未通过；停止后续任务")
            final_deadline = controller.stable_csr("t18.deadline_scope.after_recovery")
            csr.idle(final_deadline)
            require(csr.epoch(final_deadline) == wire.epoch and
                    controller.state("cpu0").startswith("Stopped") and
                    controller.state("cpu1").startswith("Stopped"),
                    "deadline恢复后CPU或UART/CSR身份不一致")

        if "abort" in profile_stages:
            abort_config = _scene_config(controller, config, checked, apis, label="before_abort_recovery",
                                          static=False, run_dir=run_dir)
            abort_dir = fresh_run("csr_abort_recovery")
            abort_result, recovery = csr.execute_abort_recovery(
                controller, wire, abort_config, config["preparation"], abort_dir, frame=0,
                core_timeout=config["core_timeout"], drain_timeout=config["drain_timeout"])
            register("wait_final_ack_sample000_recovery", abort_result, abort_dir)
            require(recovery.get("status") == "PASS" and
                    abort_result.get("status") == "SCENARIO_RESULTS_SAVED_NOT_STAGE_ACCEPTANCE",
                    "ABORT热恢复未通过")

        controller.gate(both=False)
        state0 = controller.state("cpu0")
        if not state0.startswith("Stopped"):
            require(not with_deadlines, "deadline profile要求CPU0保持停止，拒绝恢复运行或继续操作")
            controller.call("t18.csr_scope.cpu0.stop", controller.targets["cpu0"].stop)
        require(controller.state("cpu0").startswith("Stopped"), "CSR矩阵前CPU0未停止")
        require(controller.state("cpu1").startswith("Stopped"), "CSR矩阵前CPU1未停止")
        controller.gate(both=True)
        static_config = _scene_config(controller, config, checked, apis, label="before_static_matrix",
                                      static=True, run_dir=run_dir)
        static_dir = fresh_run("csr_static_matrix")
        static_result, final_snapshot = csr.execute_static_matrix(
            controller, wire, static_config, static_dir, frame_base=0,
            core_timeout=config["core_timeout"], drain_timeout=config["drain_timeout"])
        register("static_csr_negative_matrix", static_result, static_dir)
        scenarios = static_result.get("scenarios", [])
        require(static_result.get("status") == "SCENARIO_RESULTS_SAVED_NOT_STAGE_ACCEPTANCE" and scenarios and
                all(item.get("status") == "PASS" for item in scenarios if item.get("name") != "busy_start") and
                all(item.get("status") == "BLOCKED" for item in scenarios if item.get("name") == "busy_start") and
                any(item.get("name") == "busy_start" and item.get("status") == "BLOCKED" for item in scenarios),
                "静止CSR矩阵场景状态与固定PASS/BLOCKED集合不符")
        require(csr.checked_snapshot(final_snapshot), "静止CSR最终快照无效")
        results["status"] = ("PASS_CSR_DEADLINE_SCOPE_ONLY" if with_deadlines else
                             "BLOCKED_CSR_RECOVERY_SCOPE_ONLY" if results["blockers"] else
                             "PASS_CSR_RECOVERY_SCOPE_ONLY")
        results["scope_details"] = {
            "model_corpus_109": "NOT_RUN",
            "continuous_stress_1000": "NOT_RUN",
            "short_deadline": "PASS_CSR_DEADLINE_SCOPE_ONLY" if with_deadlines else "BLOCKED_UNCHANGED_NOT_RUN",
            "profile": "deadline有限范围；本profile的busy与ABORT为NOT_RUN" if with_deadlines else "standard恢复范围",
            "late_pending_response": "NOT_CLAIMED",
            "static_matrix_busy_start": "BLOCKED_UNCHANGED; " +
                ("真实BusyObserver在本profile为NOT_RUN" if with_deadlines else
                 "real busy refusal is covered by the separate BusyObserver stage"),
            "static_matrix_wire_after_external_csr": "BLOCKED_UNCHANGED; the T20 helper cannot synchronize UART epoch",
            "frame_identity": "The accepted requests use sample000 with frame 0 repeatedly; UART sequence and epoch are checked by existing helpers.",
            "weights": "Transferred once and used by this profile's sample000 seed and subsequent stages."}
        persist_result()
    except BaseException as error:
        results.update(status="FAILED_CSR_RECOVERY_SCOPE_ONLY", error=repr(error),
                       traceback=traceback.format_exc())
        try:
            persist_result()
        except BaseException as packaging_error:
            results["evidence_packaging_error"] = repr(packaging_error)
            results["evidence_packaging_traceback"] = traceback.format_exc()
            try:
                with (run_dir / "acceptance_result.json").open("wb") as stream:
                    stream.write((json.dumps(results, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8"))
                    stream.flush()
                    import os
                    os.fsync(stream.fileno())
            except BaseException:
                pass
        return results
    return results
