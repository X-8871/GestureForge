"""S2B-T20独立deadline实板流程：真实CSR超时、外部epoch对账与黄金恢复。"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import struct
import subprocess
import time
import traceback

from verification import s2b_board_acceptance as model
from verification import s2b_board_jtag as jtag
from verification import s2b_board_transport as transport
from verification import s2b_csr_board_acceptance as csr

ROOT = Path(__file__).absolute().parents[1]
TZ = timezone(timedelta(hours=8))
CORE_TIMEOUT = 10000
DRAIN_LIMIT = 1
SEED_DRAIN_TIMEOUT = 0xFFFFFFFF
EXPECTED_PL_CLOCK_HZ = 50_000_000
DEADLINE_OBSERVATION_SECONDS = 120.0


def _save(path: Path, value: object) -> bytes:
    raw = (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2, default=repr) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        import os
        os.fsync(stream.fileno())
    return raw


def _binding(path: Path) -> dict:
    actual = transport.exact_path(path)
    return {"path": str(actual), "sha256": transport.digest(actual.read_bytes())}


def _collect_output_bindings(directories) -> list[dict]:
    """对每个已登记stage目录中的全部真实文件生成路径及SHA绑定。"""
    bound = {}
    for directory in directories:
        if directory.is_dir():
            for path in sorted(directory.rglob("*")):
                if path.is_file():
                    item = _binding(path)
                    bound[item["path"]] = item
    return [bound[key] for key in sorted(bound)]


def _manifest_file_entries(run_dir: Path, output_bindings: list[dict]) -> list[dict]:
    """汇总主Run与所有stage输出，供生产清单和离线覆盖测试共用。"""
    files = {}
    for path in sorted(run_dir.rglob("*")):
        if path.is_file() and path.name != "delivery_manifest.json":
            item = _binding(path)
            files[item["path"]] = {"path": Path(item["path"]).relative_to(ROOT).as_posix(),
                                    "sha256": item["sha256"], "role": "result"}
    for item in output_bindings:
        files[item["path"]] = {"path": Path(item["path"]).relative_to(ROOT).as_posix(),
                                "sha256": item["sha256"], "role": "result"}
    return [files[key] for key in sorted(files)]


def _fresh_run(outputs: list[Path], parent: Path, run_id: str, suffix: str) -> Path:
    """登记不可覆盖的stage输出目录，供各stage和清单共用同一目录表。"""
    actual_parent = transport.exact_path(parent, "directory")
    path = actual_parent / (run_id + "_" + suffix)
    model.require(not any(item.name.casefold() == path.name.casefold() for item in actual_parent.iterdir()),
                  "拒绝覆盖已有T20 RunId：" + str(path))
    outputs.append(path)
    return path


def _bounded_stop_after_resume_failure(controller, wire, rx_start: int, prior_epoch: int) -> dict:
    """CPU0恢复后的异常只尝试一次stop并各读取一次CPU状态，保留RX原字节。"""
    evidence = {"status": "IN_PROGRESS", "stop_attempt_limit": 1,
                "cpu_state_read_limit_each": 2, "ack_start_reset_or_buffer_clear": "NOT_ISSUED",
                "wire_epoch_before_cleanup": prior_epoch}
    try:
        evidence["cpu0_before"] = controller.state("cpu0")
    except BaseException as error:
        evidence["cpu0_before_error"] = repr(error)
    if not str(evidence.get("cpu0_before", "")).startswith("Stopped"):
        try:
            controller.call("t20.csr_deadline.cpu0.stop_after_diag_failure",
                            controller.targets["cpu0"].stop)
            evidence["stop_api"] = "RETURNED"
        except BaseException as error:
            evidence["stop_api"] = "RAISED"
            evidence["stop_error"] = repr(error)
    try:
        evidence["cpu0_after"] = controller.state("cpu0")
    except BaseException as error:
        evidence["cpu0_after_error"] = repr(error)
    try:
        evidence["cpu1_after"] = controller.state("cpu1")
    except BaseException as error:
        evidence["cpu1_after_error"] = repr(error)
    evidence["cpu0_stopped"] = str(evidence.get("cpu0_after", "")).startswith("Stopped")
    evidence["cpu1_stopped"] = str(evidence.get("cpu1_after", "")).startswith("Stopped")
    evidence["wire_epoch_after_cleanup"] = wire.epoch
    evidence["wire_epoch_unchanged"] = wire.epoch == prior_epoch
    evidence["status"] = "PASS_CPU_STOPPED" if evidence["cpu0_stopped"] and evidence["cpu1_stopped"] else "FAIL_CPU_STOP_UNCONFIRMED"
    try:
        wire.rx_file.flush()
        rx_path = transport.exact_path(wire.rx_file.name)
        raw = rx_path.read_bytes()
        evidence["rx_preservation"] = {"path": str(rx_path), "response_offset": rx_start,
                                       "total_bytes": len(raw), "response_bytes": len(raw) - rx_start,
                                       "sha256": transport.digest(raw),
                                       "response_sha256": transport.digest(raw[rx_start:])}
    except BaseException as error:
        evidence["rx_preservation_error"] = repr(error)
        evidence["status"] = "FAIL_CPU_OR_RX_PRESERVATION_UNCONFIRMED"
    return evidence


def _seed_reuse_evidence(wire, plan: dict, preparation: dict) -> dict:
    """绑定已由prior_model_success重放核验的权重与sample000会话。"""
    wire.rx_file.flush(); wire.tx_header_file.flush()
    rx_path = transport.exact_path(wire.rx_file.name)
    tx_path = transport.exact_path(wire.tx_header_file.name)
    sequence = wire.last_sequence
    request, header, payload = wire.sent_requests[sequence]
    return {"status": "PASS_REUSED_PRIOR_REAL_SAMPLE000_SESSION",
            "validation": "csr.prior_model_success completed before this record",
            "preparation": preparation,
            "weights": plan["weights"], "sample000_input": plan["rows"][0]["input"],
            "sample000_reference": plan["rows"][0]["reference"],
            "epoch": wire.epoch, "last_sequence": sequence,
            "last_request": {"op": request.op, "frame": request.frame,
                             "header_hex": header.hex(), "payload_sha256": transport.digest(payload)},
            "receipt_count": len(wire.receipt_attempts),
            "tx_header_file": {"path": str(tx_path), "bytes": tx_path.stat().st_size,
                               "sha256": transport.digest(tx_path.read_bytes())},
            "rx_raw_file": {"path": str(rx_path), "bytes": rx_path.stat().st_size,
                            "sha256": transport.digest(rx_path.read_bytes())}}


def _epoch(snapshot: dict) -> int:
    return snapshot[0x050] | snapshot[0x054] << 32


def _scene_config(controller, config: dict, run_dir: Path, label: str, snapshot: dict) -> dict:
    """冻结安全IDLE现场，复用T18的同构配置schema供短期限preflight。"""
    csr.checked_snapshot(snapshot)
    csr.idle(snapshot)
    scene = {"schema_version": 1, "kind": "s2b-csr-static-scene/1.0.0",
             "expected_snapshot": {str(key): snapshot[key] for key in csr.OFFSETS}}
    scene_path = run_dir / (label + "_scene.json")
    scene_raw = _save(scene_path, scene)
    value = {"schema_version": 1, "source_commit": config["source_commit"],
             "bindings": controller.bindings,
             "build_details": config["build_details"]["path"],
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


def _stop_cpus(controller) -> None:
    """保留共享板卡门禁，只停止CPU0/CPU1，不做reset或resume。"""
    controller.gate(both=False)
    for label in ("cpu0", "cpu1"):
        if not controller.state(label).startswith("Stopped"):
            controller.call("t20.csr_deadline." + label + ".stop",
                            controller.targets[label].stop)
        model.require(controller.state(label).startswith("Stopped"), label + "未停止")
    controller.gate(both=True)


def _wire_quiescent(wire) -> dict:
    """确认UART会话无失败、无待ACK、无未配对请求或接收缓冲。"""
    model.require(not wire.failed and wire.abort_pending is None, "epoch对账前UART失败或有ABORT pending")
    sent = list(wire.sent_requests)
    model.require(len(sent) == len(wire.receipt_attempts) and
                  [item["request_header_hex"] for item in wire.receipt_attempts] ==
                  [wire.sent_requests[key][1].hex() for key in sent],
                  "epoch对账前存在未消费或不匹配的UART receipt")
    wire.rx_file.flush()
    rx_path = transport.exact_path(wire.rx_file.name)
    position, size = wire.rx_file.tell(), rx_path.stat().st_size
    model.require(position == size, "UART原始接收文件存在未落盘字节")
    waiting = getattr(wire.stream, "in_waiting", None)
    model.require(type(waiting) is int and waiting == 0, "串口尚有未消费RX字节或无法证明接收队列为空")
    return {"sent_sequences": sent, "completed_receipt_count": len(wire.receipt_attempts),
            "rx_file": {"path": str(rx_path), "bytes": size, "sha256": transport.digest(rx_path.read_bytes())},
            "serial_in_waiting": waiting}


def _measure_normal_start(runner, *, frame: int, clock_profile: dict) -> dict:
    """测量完整合法START到稳定DONE_SAFE的保守wall-time上界并匹配ACK。"""
    clock_hz = clock_profile["hwh_clock_hz"]
    model.require(type(clock_hz) is int and clock_hz == EXPECTED_PL_CLOCK_HZ,
                  "绑定XSA/HWH配置的PL时钟不是预期50MHz")
    before = runner.snapshot("deadline_measurement:before", stable=True)
    csr.idle(before)
    before_epoch = _epoch(before)
    params = runner.parameters(frame, 0xFFFFFFFF, 0xFFFFFFFF)
    expected_epoch = before_epoch + 1
    model.require(expected_epoch <= 0xFFFFFFFFFFFFFFFF, "deadline测量epoch溢出")
    runner.event("deadline_measurement_armed", {"before": before, "parameters": params,
                                                 "frame": frame, "core_timeout": 0xFFFFFFFF,
                                                 "drain_timeout": 0xFFFFFFFF,
                                                 "clock_hz_configured": clock_hz,
                                                 "clock_basis": clock_profile})
    started_ns = time.monotonic_ns()
    runner.write(0x008, 1)
    deadline = time.monotonic() + DEADLINE_OBSERVATION_SECONDS
    observations = 0
    while time.monotonic() < deadline:
        current = runner.snapshot("deadline_measurement:observe", stable=False)
        observations += 1
        model.require(_epoch(current) == expected_epoch and current[0x058] == frame and
                      not current[0x00C] & 0x200, "正常deadline任务epoch/frame/head状态异常")
        phase = current[0x00C] & 7
        if phase == 4:
            terminal = runner.snapshot("deadline_measurement:done_safe", stable=True)
            model.require(_epoch(terminal) == expected_epoch and terminal[0x058] == frame and
                          terminal[0x00C] == 0xE04 and terminal[0x010] == 0 and
                          terminal[0x068] == 0, "测量任务不是DONE_SAFE/HEAD_VALID/ledger0")
            finished_ns = time.monotonic_ns()
            elapsed_ns = finished_ns - started_ns
            cycles_upper = (elapsed_ns * clock_hz + 999_999_999) // 1_000_000_000
            margin_ok = cycles_upper * 5 <= 0xFFFFFFFF * 4
            measurement = {"status": "PASS_DONE_SAFE_MEASURED",
                           "start_monotonic_ns": started_ns, "safe_monotonic_ns": finished_ns,
                           "elapsed_ns_upper_bound": elapsed_ns,
                           "clock_hz_configured": clock_hz,
                           "clock_basis": clock_profile,
                           "cycles_interpretation": "基于绑定XSA/HWH配置时钟假设的wall-time cycles上界，不是实测FCLK或精确PL cycles",
                           "cycles_upper_bound": cycles_upper,
                           "margin_factor": "1.25",
                           "margin_check": "PASS" if margin_ok else "FAIL",
                           "margin_equation": "cycles_upper_bound*5 <= 0xffffffff*4",
                           "observation_count": observations, "frame": frame,
                           "epoch": expected_epoch, "terminal": terminal,
                           "golden_comparison": "NOT_APPLICABLE_TO_DIRECT_DAP_START"}
            runner.event("deadline_measurement_result", measurement)
            runner.write(0x05C, expected_epoch & 0xFFFFFFFF)
            runner.write(0x060, expected_epoch >> 32)
            runner.write(0x008, 4)
            after_ack = runner.snapshot("deadline_measurement:after_ack", stable=True)
            csr.idle(after_ack)
            model.require(_epoch(after_ack) == expected_epoch, "DONE_SAFE ACK后epoch不保持")
            measurement["after_ack"] = after_ack
            measurement["status"] = "PASS_DONE_SAFE_MEASURED_ACKED"
            return measurement
        model.require(phase in (1, 2, 3), "正常deadline任务进入错误或隔离状态；不ACK、不启动后续阶段")
        time.sleep(0.001)
    pending = runner.snapshot("deadline_measurement:observation_timeout", stable=False)
    runner.event("deadline_measurement_pending", {"snapshot": pending,
                                                   "elapsed_observation_seconds": DEADLINE_OBSERVATION_SECONDS,
                                                   "ack_or_reset": "NOT_ISSUED"})
    raise RuntimeError("最大合法deadline任务未在观察期限内达到DONE_SAFE；保留现场且不ACK")


def _manual_mode0_diag(controller, wire, expected_epoch: int, frame: int = 0) -> dict:
    """用真实DIAG mode0响应对账外部DAP epoch；解析成功前不改wire.epoch。"""
    model.require(type(expected_epoch) is int and 0 <= expected_epoch <= 0xFFFFFFFFFFFFFFFF,
                  "CSR外部epoch越界")
    model.require(wire.epoch < expected_epoch, "外部CSR epoch没有领先于UART或已经对账")
    before = _wire_quiescent(wire)
    payload = struct.pack("<III", 0, 0, 0)
    sequence = wire.last_sequence + 1
    request, header = transport.make_request(transport.OP_DIAG, sequence, frame, payload)
    source = {"kind": "csr_deadline_external_epoch_reconciliation", "expected_csr_epoch": expected_epoch,
              "prior_uart_epoch": wire.epoch, "csr_status_offset": "0x00c",
              "csr_epoch_offsets": ["0x050", "0x054"]}
    rx_start = wire.rx_file.tell()
    chunk_start = len(wire.rx_chunks)
    resume_attempted = False
    try:
        controller.gate(both=False)
        resume_attempted = True
        controller.call("t20.csr_deadline.cpu0.resume_for_mode0_epoch_diag",
                        controller.targets["cpu0"].con)
        model.require(controller.state("cpu0") == "Running", "CPU0未运行，不能消费真实DIAG")
        controller.gate(both=False)
        wire.send(request, header, payload, source)
        deadline = time.monotonic() + wire.response_timeout
        raw_header = wire.read_exact(transport.HEADER.size, deadline)
        parsed_header = transport.Header.unpack(raw_header)
        model.require(parsed_header.op == (request.op | 0x8000) and parsed_header.sequence == request.sequence,
                      "mode0 DIAG响应op/sequence不匹配")
        model.require(transport.META.size <= parsed_header.length <= transport.MAX_RESPONSE,
                      "mode0 DIAG响应长度越界")
        raw_payload = wire.read_exact(parsed_header.length, deadline)
        raw = raw_header + raw_payload
        parsed = transport.decode_response(raw_header, raw_payload, request, 0, expected_epoch)
        meta = parsed[0]
        model.require(meta["response_code"] == 0 and meta["epoch"] == expected_epoch and
                      meta["phys_status"] == 0x400 and meta["error_code"] == 0,
                      "真实DIAG未证明目标CSR epoch处于安全IDLE")
        wire.record_completed_receipt(request, raw, previous_epoch=expected_epoch,
                                       rx_chunk_start=chunk_start, parsed=parsed)
        wire.events.append({"direction": "RX", "sequence": sequence, "frame": frame,
                            "op": request.op | 0x8000, "header_sha256": transport.digest(raw_header),
                            "payload_sha256": transport.digest(raw_payload), "bytes": len(raw),
                            "status": "RECEIVED_AND_DECODED_WITH_EXTERNAL_CSR_EPOCH"})
        after = _wire_quiescent(wire)
        wire.epoch = meta["epoch"]
        wire.rx_file.flush()
        rx_path = transport.exact_path(wire.rx_file.name)
        raw_binding = {"path": str(rx_path), "offset": rx_start, "bytes": len(raw),
                       "sha256": transport.digest(raw)}
        return {"status": "PASS_REAL_DIAG_MODE0_EPOCH_RECONCILIATION",
            "prior_uart_epoch": source["prior_uart_epoch"],
            "external_csr_epoch": expected_epoch, "reconciled_uart_epoch": wire.epoch,
            "request": {"sequence": sequence, "frame": frame, "header_hex": header.hex(),
                        "payload_hex": payload.hex(), "source": source},
            "response": {"header_hex": raw_header.hex(), "payload_hex": raw_payload.hex(),
                         "meta": meta, "raw_uart_binding": raw_binding,
                         "rx_chunk_count": len(wire.rx_chunks) - chunk_start,
                         "wire_quiescence_after": after},
            "wire_quiescence_before": before}
    except BaseException as error:
        if resume_attempted:
            cleanup = _bounded_stop_after_resume_failure(controller, wire, rx_start,
                                                         source["prior_uart_epoch"])
            controller.failed = True
            wire.failed = True
            try:
                setattr(error, "deadline_cpu_stop_cleanup", cleanup)
            except BaseException:
                error = RuntimeError(repr(error) + "; cleanup=" + repr(cleanup))
        raise error


def execute(controller, wire, config: dict, checked: dict, apis, admission: dict,
            journal=None, *, reuse_seed: bool = False) -> dict:
    """真实CORE deadline、DRAIN超限、ACK、mode0 epoch对账及sample000黄金恢复。"""
    require = model.require
    run_dir: Path = checked["run_dir"]
    run_dir.mkdir()
    t20_root = transport.exact_path(ROOT / "report/evidence/S2B-T20", "directory")
    outputs: list[Path] = []
    results = {"schema_version": 1,
               "scope": "CSR_MAX_DEADLINE_MEASUREMENT_CORE_TIMEOUT_DRAIN_LIMIT_SAFE_ACK_ONLY",
               "status": "IN_PROGRESS", "hardware_execution": "BORROWED_SESSION_UART_DAP_REQUESTED",
               "entrypoint": "execute_after_seed" if reuse_seed else "execute",
               "seed_mode": "REUSE_PRIOR_VALIDATED_SAMPLE000" if reuse_seed else "LOAD_AND_RUN_SAMPLE000",
               "source_commit": config["source_commit"], "stages": [], "t20_outputs": [],
               "uart_epoch_state": "MATCHED_AT_FLOW_ENTRY",
               "uart_epoch_reconciliation": "NOT_RUN",
               "hot_golden_recovery": "NOT_RUN",
               "limitations": ["不代表完整2B验收、真实pending晚排空或busy/pending reset通过。",
                               "DRAIN阶段只验收真实bit3超限、后续安全终态和ACK；不声称采到真实pending响应。",
                               "模型黄金恢复只在mode0真实外部epoch对账成功后执行。"]}
    seed_epoch = None
    first_external_epoch = None
    second_external_epoch = None
    cpu0_resumed_for_diag = False
    diag_rx_start = None

    def record_stage(name: str, status: str, path: Path, **details) -> None:
        results["stages"].append({"name": name, "status": status, "evidence_dir": str(path), **details})
        if journal is not None:
            journal.event("csr_deadline." + name, status, evidence_dir=str(path), **details)

    def fresh_run(suffix: str) -> Path:
        return _fresh_run(outputs, t20_root, config["run_id"], suffix)

    def persist_result() -> None:
        results["t20_outputs"] = _collect_output_bindings(outputs)
        result_path = run_dir / "acceptance_result.json"
        _save(result_path, results)
        files = _manifest_file_entries(run_dir, results["t20_outputs"])
        inputs = [_binding(Path(__file__)), _binding(Path(csr.__file__)),
                  _binding(Path(model.__file__)), _binding(Path(transport.__file__))]
        if "preparation" in config:
            inputs.append({"path": str(transport.exact_path(config["preparation"]["path"])),
                           "sha256": config["preparation"]["sha256"]})
        for item in controller.bindings.values():
            inputs.append(item)
        manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T20",
                    "run_id": run_dir.name, "source_commit": config["source_commit"],
                    "evidence_dir": run_dir.relative_to(ROOT).as_posix(),
                    "inputs": inputs, "files": files,
                    "checks": [{"name": "CSR CORE timeout / DRAIN limit / safe ACK / UART epoch reconciliation",
                                "status": "PASS" if results["status"] == "PASS_CSR_DEADLINE_SCOPE_ONLY" else "FAIL",
                                "command": "s2b_csr_deadline_flow." + results["entrypoint"] + "(borrowed_controller, borrowed_wire)",
                                "exit_code": 0 if results["status"] == "PASS_CSR_DEADLINE_SCOPE_ONLY" else 1,
                                "reason": results.get("error", "仅报告实际执行并满足的deadline子范围。")}],
                    "tool_versions": {"Python": __import__("sys").version.split()[0]},
                    "limitations": results["limitations"]}
        manifest_path = run_dir / "delivery_manifest.json"
        _save(manifest_path, manifest)

    try:
        require(type(config) is dict and type(config.get("run_id")) is str and config["run_id"],
                "deadline run_id缺失")
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, encoding="utf-8")
        require(head.returncode == 0 and head.stdout.strip() == config["source_commit"],
                "deadline配置源码基线不是当前HEAD")
        controller.verify_bindings()
        require(not wire.failed and wire.abort_pending is None, "流程开始时UART失败或有未完成ABORT")
        for timeout in (config["core_timeout"], config["drain_timeout"]):
            require(type(timeout) is int and 1 <= timeout <= 0xFFFFFFFF,
                    "sample000准备/恢复deadline必须为非零32-bit")
        _, preparation_raw = model.read_bound(config["preparation"])
        plan = json.loads(preparation_raw.decode("utf-8"))
        model.validate_plan(plan)
        require(plan["rows"], "固定样本计划为空")
        seed_epoch = wire.epoch

        if reuse_seed:
            require(type(admission) is dict and admission, "复用入口缺少原有效admission")
        else:
            seed_dir = fresh_run("csr_deadline_seed_sample000")
            seed = model.AcceptanceRunner(wire, seed_dir, admission, capture_wire_receipts=True)
            seed.record["hardware_execution"] = "BORROWED_SESSION_DAP_REQUESTED"
            weight_path, weights = model.read_bound(plan["weights"])
            sequence = wire.last_sequence + 1
            request, header = transport.make_request(transport.OP_WEIGHTS, sequence, 0, weights)
            seed.send(request, header, weights, {"path": str(weight_path), "sha256": transport.digest(weights)})
            seed.receive(request, 0)
            seed.run_input(plan["rows"][0], sequence + 1, 0, 1, config["core_timeout"],
                           config["drain_timeout"], "csr_deadline_seed")
            seed_result = seed.finish("PASS_SAMPLE000_SEED_ONLY")
            record_stage("sample000_seed", seed_result["status"], seed_dir,
                         initial_uart_epoch=seed_epoch, final_uart_epoch=wire.epoch,
                         frame=0, capture_check="PASS")

        _stop_cpus(controller)
        csr.prior_model_success(wire, plan)
        if reuse_seed:
            reuse_evidence = _seed_reuse_evidence(wire, plan, config["preparation"])
            _save(run_dir / "sample000_seed_reuse.json", reuse_evidence)
            record_stage("sample000_seed_reused", reuse_evidence["status"], run_dir,
                         initial_uart_epoch=seed_epoch, final_uart_epoch=wire.epoch,
                         frame=0, proof=reuse_evidence)
        before_preflight = controller.stable_csr("t20.csr_deadline.before_preflight")
        csr.checked_snapshot(before_preflight); csr.idle(before_preflight)
        require(_epoch(before_preflight) == wire.epoch, "预检前CSR与UART epoch不同")
        scene_binding = _scene_config(controller, config, run_dir, "before_deadline_sequence",
                                      before_preflight)
        preflight_config, admitted, preflight_snapshot = csr.preflight(
            controller, wire, scene_binding, static=True)
        require(preflight_snapshot == before_preflight and preflight_config["bindings"] == controller.bindings,
                "deadline序列preflight现场或产物绑定变化")
        if reuse_seed:
            require(admitted == admission, "复用入口当前preflight结果与传入原admission不一致")
            admitted = admission
        results["preflight"] = {"status": "PASS", "config_binding": scene_binding,
                                "snapshot": preflight_snapshot,
                                "admission": admitted,
                                "source_commit": config["source_commit"],
                                "bindings": controller.bindings}
        results["uart_epoch_state"] = "MATCHED_AT_PRE_DAP_PREFLIGHT"
        _save(run_dir / "deadline_preflight.json", results["preflight"])
        clock_profile = jtag.postconfig_basis(jtag.bound_bytes(controller.bindings["xsa"]))
        results["configured_pl_clock"] = {
            "clock_hz": clock_profile["hwh_clock_hz"],
            "xsa_binding": controller.bindings["xsa"],
            "hwh_clock_evidence": clock_profile,
            "meaning": "绑定XSA/HWH中的配置频率；不代表本轮实测FCLK。"}
        _save(run_dir / "configured_pl_clock.json", results["configured_pl_clock"])

        normal_dir = fresh_run("csr_deadline_max_start_measurement")
        transport.new_directory(normal_dir, parent=t20_root)
        normal_runner = csr._Runner(controller, wire, normal_dir, admitted,
                                    scope="BORROWED_SESSION_DAP_REQUESTED")
        normal_runner.record["config_binding"] = scene_binding
        normal_runner.record["deadline_test_profile"] = {
            "core_timeout": 0xFFFFFFFF, "drain_timeout": 0xFFFFFFFF,
            "frame": 1, "PL_clock_hz_configured": clock_profile["hwh_clock_hz"],
            "measurement": "START写前至DONE_SAFE稳定快照后的monotonic wall time upper bound"}
        normal_runner.event("preflight_binding", results["preflight"])
        normal_finished = False
        try:
            normal_measurement = _measure_normal_start(normal_runner, frame=1,
                                                       clock_profile=clock_profile)
            normal_runner.event("deadline_measurement_summary", normal_measurement)
            normal_runner.finish("SCENARIO_RESULTS_SAVED_NOT_STAGE_ACCEPTANCE")
            normal_finished = True
            normal_external_epoch = normal_measurement["epoch"]
            require(normal_external_epoch == wire.epoch + 1,
                    "最大deadline实测START epoch不是seed UART epoch加一")
            record_stage("maximum_deadline_start_measurement", normal_measurement["status"],
                         normal_dir, result=normal_measurement)
        except BaseException as error:
            controller.failed = True; wire.failed = True
            if not normal_finished:
                normal_runner.finish("FAIL_LATCHED", error)
            raise

        after_normal = controller.stable_csr("t20.csr_deadline.after_normal_start_ack")
        csr.checked_snapshot(after_normal); csr.idle(after_normal)
        require(_epoch(after_normal) == normal_external_epoch and after_normal[0x068] == 0,
                "最大deadline任务ACK后未证明同epoch的安全IDLE/ledger0")
        results["epoch_causality"] = {"seed_uart_epoch": seed_epoch,
                                      "normal_start_terminal_epoch": normal_external_epoch,
                                      "uart_epoch_after_normal_start": wire.epoch,
                                      "after_normal_ack_csr_epoch": _epoch(after_normal),
                                      "after_normal_ack_snapshot": after_normal}
        results["uart_epoch_state"] = "STALE_AFTER_EXTERNAL_DAP_START"
        _save(run_dir / "deadline_epoch_causality.json", results["epoch_causality"])

        core_dir = fresh_run("csr_deadline_core_timeout")
        transport.new_directory(core_dir, parent=t20_root)
        core_runner = csr._Runner(controller, wire, core_dir, admitted,
                                  scope="BORROWED_SESSION_DAP_REQUESTED_EXTERNAL_EPOCH")
        core_runner.record["config_binding"] = scene_binding
        core_runner.event("core_timeout_precondition", {"snapshot": after_normal,
                                                         "wire_epoch_intentionally_stale": wire.epoch,
                                                         "actual_csr_epoch": normal_external_epoch,
                                                         "core_timeout": CORE_TIMEOUT,
                                                         "drain_timeout": SEED_DRAIN_TIMEOUT})
        core_finished = False
        try:
            core_value = core_runner.short_deadline(frame=2, core=CORE_TIMEOUT,
                                                    drain=SEED_DRAIN_TIMEOUT,
                                                    observation_seconds=DEADLINE_OBSERVATION_SECONDS)
            core_runner.finish("SCENARIO_RESULTS_SAVED_NOT_STAGE_ACCEPTANCE"
                               if core_value.get("status") == "PASS" else "FAIL_LATCHED",
                               None if core_value.get("status") == "PASS" else RuntimeError(
                                   "CORE timeout未达到ERROR_SAFE；未ACK且保留真实现场"))
            core_finished = True
        except BaseException as error:
            controller.failed = True; wire.failed = True
            if not core_finished:
                core_runner.finish("FAIL_LATCHED", error)
            raise
        record_stage("core_timeout_code5_safe_ack", core_value.get("status", "UNKNOWN"),
                     core_dir, result=core_value)
        require(core_value.get("status") == "PASS", "CORE timeout未形成真实ERROR_SAFE/code5/ACK")
        core_terminal = core_value["terminal"]
        first_external_epoch = _epoch(core_terminal)
        require(first_external_epoch == normal_external_epoch + 1,
                "CORE timeout epoch未紧接最大deadline实测START")

        post_core = controller.stable_csr("t20.csr_deadline.after_core_ack")
        csr.checked_snapshot(post_core); csr.idle(post_core)
        require(_epoch(post_core) == first_external_epoch and post_core[0x068] == 0,
                "CORE ACK后未证明同一epoch的IDLE/ledger0")
        results["epoch_causality"].update(core_timeout_terminal_epoch=first_external_epoch,
                                          after_core_ack_csr_epoch=_epoch(post_core),
                                          after_core_ack_snapshot=post_core,
                                          next_drain_start_expected_epoch=first_external_epoch + 1)
        _save(run_dir / "deadline_epoch_causality.json", results["epoch_causality"])

        drain_dir = fresh_run("csr_deadline_drain_limit")
        transport.new_directory(drain_dir, parent=t20_root)
        drain_runner = csr._Runner(controller, wire, drain_dir, admitted,
                                   scope="BORROWED_SESSION_DAP_REQUESTED_EXTERNAL_EPOCH")
        stage_binding = {"source_commit": config["source_commit"], "bindings": controller.bindings,
                         "preparation": config["preparation"], "admission": admitted,
                         "preceding_core_terminal_epoch": first_external_epoch,
                         "expected_drain_start_epoch": first_external_epoch + 1,
                         "before_snapshot": post_core, "core_timeout": CORE_TIMEOUT,
                         "drain_timeout": DRAIN_LIMIT,
                         "limitation": "不宣稱真实pending或晚响应；只检查bit3、safe terminal和ACK。"}
        controller.verify_bindings()
        controller.gate(both=True)
        live_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                                   text=True, encoding="utf-8")
        require(live_head.returncode == 0 and live_head.stdout.strip() == config["source_commit"],
                "第二阶段源码基线已变化")
        _save(drain_dir / "stage_binding.json", stage_binding)
        drain_runner.event("drain_stage_precondition", {"snapshot": post_core,
                                                        "wire_epoch_intentionally_stale": wire.epoch,
                                                        "actual_csr_epoch": first_external_epoch})
        drain_finished = False
        try:
            drain_value = drain_runner.short_deadline(frame=3, core=CORE_TIMEOUT,
                                                      drain=DRAIN_LIMIT, observation_seconds=120.0,
                                                      required_fault_detail_mask=0x8)
            if drain_value.get("status") != "PASS":
                current = drain_runner.snapshot("drain_limit:observation_deadline", stable=False)
                drain_value["actual_final_snapshot"] = current
                drain_value["acceptance_scope"] = "PENDING_DRAIN_TRIGGER_OR_SAFE_TERMINAL_UNRESOLVED"
                drain_value["fault_detail_bit3_observed"] = bool(current[0x074] & 0x8)
                drain_value["late_pending_response"] = "NOT_CLAIMED"
                drain_runner.finish("FAIL_LATCHED", RuntimeError("DRAIN超时未到达安全终态；保留真实现场"))
                drain_finished = True
                controller.failed = True; wire.failed = True
                record_stage("drain_limit_and_safe_return", "PENDING_DRAIN_TIMEOUT_NOT_SAFE", drain_dir,
                             result=drain_value)
                results["status"] = "PENDING_DRAIN_LIMIT_UNRESOLVED"
                persist_result()
                return results
            drain_terminal = drain_value["terminal"]
            second_external_epoch = _epoch(drain_terminal)
            require(second_external_epoch == first_external_epoch + 1,
                    "DRAIN limit terminal epoch未连续递增")
            require(drain_terminal[0x074] & 0x8 != 0,
                    "真实ERROR_SAFE未保留FAULT_DETAIL.bit3，DRAIN limit未证明")
            drain_after = controller.stable_csr("t20.csr_deadline.after_drain_ack")
            csr.checked_snapshot(drain_after); csr.idle(drain_after)
            require(_epoch(drain_after) == second_external_epoch and drain_after[0x068] == 0,
                    "DRAIN ACK后未证明安全IDLE/ledger0")
            drain_value["acceptance_scope"] = "PASS_DRAIN_LIMIT_AND_SAFE_RETURN_ONLY"
            drain_value["late_pending_response"] = "NOT_CLAIMED"
            drain_value["before_snapshot"] = post_core
            drain_value["after_ack_snapshot"] = drain_after
            drain_runner.event("drain_stage_safe_ack", {"terminal": drain_terminal,
                                                        "after_ack": drain_after,
                                                        "late_pending_response": "NOT_CLAIMED"})
            drain_runner.finish("SCENARIO_RESULTS_SAVED_NOT_STAGE_ACCEPTANCE")
            drain_finished = True
            record_stage("drain_limit_and_safe_return", "PASS_DRAIN_LIMIT_AND_SAFE_RETURN_ONLY",
                         drain_dir, result=drain_value)
        except BaseException as error:
            controller.failed = True; wire.failed = True
            if not drain_finished:
                drain_runner.finish("FAIL_LATCHED", error)
            raise

        results["epoch_causality"].update(
            drain_timeout_terminal_epoch=second_external_epoch,
            after_drain_ack_csr_epoch=_epoch(drain_after), after_drain_ack_snapshot=drain_after)
        _save(run_dir / "deadline_epoch_causality.json", results["epoch_causality"])

        pre_diag = controller.stable_csr("t20.csr_deadline.before_mode0_epoch_diag")
        csr.checked_snapshot(pre_diag); csr.idle(pre_diag)
        require(_epoch(pre_diag) == second_external_epoch and wire.epoch == seed_epoch,
                "mode0 DIAG前外部/旧UART epoch链不符")
        results["uart_epoch_reconciliation"] = "IN_PROGRESS_REAL_MODE0_DIAG"
        diag_rx_start = wire.rx_file.tell()
        results["external_epoch_reconciliation"] = _manual_mode0_diag(controller, wire, second_external_epoch)
        cpu0_resumed_for_diag = True
        results["uart_epoch_state"] = "RECONCILED_TO_EXTERNAL_CSR_EPOCH"
        results["uart_epoch_reconciliation"] = "PASS_REAL_DIAG_MODE0_RESPONSE"
        _save(run_dir / "external_epoch_reconciliation.json", results["external_epoch_reconciliation"])
        record_stage("real_mode0_epoch_reconciliation", "PASS_REAL_DIAG_MODE0_EPOCH_RECONCILIATION",
                     run_dir, prior_uart_epoch=seed_epoch,
                     external_csr_epoch=second_external_epoch, reconciled_uart_epoch=wire.epoch)

        recovery_dir = fresh_run("csr_deadline_sample000_recovery")
        recovery = model.AcceptanceRunner(wire, recovery_dir, admitted, capture_wire_receipts=True)
        recovery.record["hardware_execution"] = "BORROWED_SESSION_UART_DAP_REQUESTED_AFTER_REAL_DIAG_RECONCILIATION"
        recovery.run_input(plan["rows"][0], wire.last_sequence + 1, 0, 1,
                           config["core_timeout"], config["drain_timeout"], "csr_deadline_recovery")
        recovery_result = recovery.finish("PASS_SAMPLE000_DEADLINE_RECOVERY_GOLDEN")
        require(recovery_result["status"] == "PASS_SAMPLE000_DEADLINE_RECOVERY_GOLDEN" and
                len(recovery_result["frames"]) == 1 and wire.epoch == second_external_epoch + 1,
                "mode0对账后的sample000黄金恢复不完整")
        results["hot_golden_recovery"] = "PASS_SAMPLE000_DEADLINE_RECOVERY_GOLDEN"
        record_stage("sample000_golden_recovery", recovery_result["status"], recovery_dir,
                     before_epoch=second_external_epoch, result_epoch=wire.epoch,
                     sample_index=0, frame=0)

        cpu0_resumed_for_diag = False
        _stop_cpus(controller)
        final_snapshot = controller.stable_csr("t20.csr_deadline.final_stopped_idle")
        csr.checked_snapshot(final_snapshot); csr.idle(final_snapshot)
        require(_epoch(final_snapshot) == wire.epoch, "结束时CSR与UART epoch不一致")
        results["final_snapshot"] = final_snapshot
        results["wire_epoch"] = {"epoch": wire.epoch, "sequence": wire.last_sequence,
                                  "receipt_count": len(wire.receipt_attempts),
                                  "sent_count": len(wire.sent_requests),
                                  "cpu0": controller.state("cpu0"), "cpu1": controller.state("cpu1")}
        require(controller.state("cpu0").startswith("Stopped") and
                controller.state("cpu1").startswith("Stopped"), "结束时CPU0/CPU1没有保持停止")
        results["scope_details"] = {
            "core_timeout_code5_safe_return_and_ack": "PASS",
            "drain_timeout_flag3_safe_return_and_ack": "PASS_DRAIN_LIMIT_AND_SAFE_RETURN_ONLY",
            "actual_pending_drain_and_late_response": "NOT_CLAIMED",
            "busy_or_pending_reset": "NOT_RUN",
            "uart_epoch_reconciliation": results["uart_epoch_reconciliation"],
            "sample000_golden_recovery": results["hot_golden_recovery"],
            "model_corpus_109": "NOT_RUN",
            "continuous_stress_1000": "NOT_RUN",
            "cpu_state_at_exit": "STOPPED"}
        margin_ok = normal_measurement["margin_check"] == "PASS"
        results["scope_details"]["maximum_deadline_start_measurement"] = {
            "status": normal_measurement["status"],
            "elapsed_ns_upper_bound": normal_measurement["elapsed_ns_upper_bound"],
            "cycles_upper_bound": normal_measurement["cycles_upper_bound"],
            "clock_hz_configured": clock_profile["hwh_clock_hz"],
            "margin_check": normal_measurement["margin_check"]}
        results["status"] = ("PASS_CSR_DEADLINE_SCOPE_ONLY" if margin_ok else
                              "FAILED_CSR_DEADLINE_MARGIN_AFTER_SAFE_RECOVERY")
        if not margin_ok:
            results["error"] = "已完成安全流程与黄金恢复，但实测最大deadline的1.25 margin条件失败。"
        persist_result()
        return results
    except BaseException as error:
        cleanup = getattr(error, "deadline_cpu_stop_cleanup", None)
        if cleanup is None and cpu0_resumed_for_diag:
            cleanup = _bounded_stop_after_resume_failure(controller, wire,
                                                         diag_rx_start if diag_rx_start is not None else 0,
                                                         wire.epoch)
            controller.failed = True
            wire.failed = True
            try:
                setattr(error, "deadline_cpu_stop_cleanup", cleanup)
            except BaseException:
                pass
        if cleanup is not None:
            results["cpu_stop_after_resume_failure"] = cleanup
        if results.get("uart_epoch_state") == "STALE_AFTER_EXTERNAL_DAP_START":
            results["uart_epoch_reconciliation"] = "FAILED_OR_UNVERIFIED_EXTERNAL_EPOCH_UART_UNUSABLE"
            results["hot_golden_recovery"] = "NOT_RUN_EXTERNAL_EPOCH_UNRECONCILED"
        results.update(status="FAILED_CSR_DEADLINE_FLOW", error=repr(error),
                       traceback=traceback.format_exc())
        if controller is not None:
            controller.failed = True
        if wire is not None:
            wire.failed = True
        try:
            persist_result()
        except BaseException as packaging_error:
            results["evidence_packaging_error"] = repr(packaging_error)
            results["evidence_packaging_traceback"] = traceback.format_exc()
            try:
                with (run_dir / "acceptance_result.json").open("wb") as stream:
                    stream.write((json.dumps(results, ensure_ascii=False, allow_nan=False, indent=2,
                                             default=repr) + "\n").encode("utf-8"))
                    stream.flush()
                    import os
                    os.fsync(stream.fileno())
            except BaseException:
                pass
        if journal is not None:
            journal.event("csr_deadline.flow", "FAILED", exception=repr(error))
        return results


def execute_after_seed(controller, wire, config: dict, checked: dict, apis, admission: dict,
                       journal=None) -> dict:
    """复用已验证的sample000实板会话，不重发weights或seed RUN。"""
    return execute(controller, wire, config, checked, apis, admission, journal, reuse_seed=True)
