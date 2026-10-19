"""T20正常UART任务中的busy START观测；仅借用已审核会话，导入不访问硬件。"""
from __future__ import annotations

import copy
from datetime import datetime
import json
import math
from pathlib import Path
import re
import struct
import time

try:
    from . import s2b_csr_board_acceptance as csr
except ImportError:
    import s2b_csr_board_acceptance as csr

jtag, model, transport = csr.jtag, csr.model, csr.transport


class BusyWindowUnavailable(csr.CsrAcceptanceError):
    """真实观测未能包围同一个忙任务；不能算busy负例已执行。"""


def _seconds(value, label, maximum):
    """超时为有限正数，布尔值不能充当秒数。"""
    csr.require(type(value) in (int, float) and math.isfinite(value) and 0 < value <= maximum,
                label + "必须为有限正秒数")
    return value


def _is_ahb_ap_write_bresp_unresolved(error, address):
    """只识别本次CSR START写的精确DAP/AHB错误原文，不推断AXI BRESP。"""
    if type(address) is not int or address != jtag.CSR_BASE + 8:
        return False
    message = error if type(error) is str else str(error)
    address_hex = f"0x{address:08X}"
    address_dec = str(address)
    pattern = (
        rf'TCF command exception:\n'
        rf'Command: Memory set "[^"\r\n]+", {address_dec}, 0, 4\.\.\.\n'
        rf'Exception: Memory write error at {address_hex}\. '
        rf'AHB AP transaction error, DAP status 0xF0000021\n'
        rf'Error code: 1'
    )
    return re.fullmatch(pattern, message) is not None


def _request(wire, plan):
    """严格重放真实LOAD/seed记录，沿用其期限并发送下一seq/frame。"""
    csr.prior_model_success(wire, plan)
    previous, _, payload = wire.sent_requests[wire.last_sequence]
    core, drain = struct.unpack_from("<II", payload)
    csr.require(core > 0 and drain > 0 and wire.epoch < 0xFFFFFFFFFFFFFFFF and
                wire.last_sequence < 0xFFFFFFFF and previous.frame < 0xFFFFFFFF,
                "期限或seq/frame/epoch没有合法递增空间")
    _, input_raw = model.read_bound(plan["rows"][0]["input"])
    reference = csr.bound_json(plan["rows"][0]["reference"])["samples"][0]
    csr.require(reference["input"]["geometry_wh"] == [previous.width, previous.height] and
                transport.digest(input_raw) == reference["input"]["pl_input_sha256"],
                "冻结sample000输入或几何来源身份不匹配")
    payload = struct.pack("<II", core, drain) + input_raw
    request, header = transport.make_request(transport.OP_RUN, wire.last_sequence + 1,
        previous.frame + 1, payload, width=previous.width, height=previous.height, repeat=1)
    return request, header, payload


class _Observer:
    """内部动作与离线原生夹具共用；正式入口必须先完成全部实际准入门禁。"""
    def __init__(self, controller, wire, run, admission, initial, *, scope):
        csr.require(type(controller) is jtag.JtagController and type(wire) is jtag.JtagWireSession,
                    "必须使用真实T16对象类型")
        self.controller, self.wire, self.run = controller, wire, run
        self.initial = copy.deepcopy(initial)
        self.call_start = len(controller.record["calls"])
        self.receipt_start, self.event_start = len(wire.receipt_attempts), len(wire.events)
        self.log = (run / "busy_events.jsonl").open("x", encoding="utf-8", newline="\n")
        self.started = time.monotonic()
        self.owned_stop = self.tx_attempted = self.dap_attempted = False
        self.last_busy_state = 1
        self.record = {"schema_version": 1, "status": "IN_PROGRESS", "hardware_execution": scope,
            "admission": admission, "initial_snapshot": initial,
            "source": model.binding(Path(__file__)), "started_at_utc8": datetime.now(csr.TZ).isoformat(),
            "limitations": ["离散DAP读不能排除读间不可观察的账本/状态瞬态；不能关闭ILA缺口。",
                "AXI_PROGRESS和STATUS.AXI_PENDING按逐次读诊断保存，不要求跨读相等。",
                "仅同一sample000任务busy拒绝及全部双头/框；不代表109/1000或阶段G3/G4/G5。",
                "CPU1状态与目标链为逐次观测；PL时钟没有暂停命令；峰值内存未测。"]}

    def event(self, kind, value):
        """动作前后即时持久化，包括未知SDK输出与失败现场。"""
        row = {"time_utc8": datetime.now(csr.TZ).isoformat(), "kind": kind, "value": value}
        model.append(self.log, json.loads(json.dumps(row, ensure_ascii=False, default=repr)))

    def observation(self, label):
        """STATUS包围HI→LO→HI及完整原CSR，不把分次读取伪称原子快照。"""
        c = self.controller
        csr.require(not c.failed and not self.wire.failed, "失败会话禁止继续观测或提交命令")
        c.verify_bindings(); c.gate(both=self.owned_stop)
        row = {"label": label}
        try:
            row["status_before"] = c.words(jtag.CSR_BASE + 0x00C, 1)[0]
            row["epoch_hi_before"] = c.words(jtag.CSR_BASE + 0x054, 1)[0]
            row["epoch_lo"] = c.words(jtag.CSR_BASE + 0x050, 1)[0]
            row["epoch_hi_after"] = c.words(jtag.CSR_BASE + 0x054, 1)[0]
            row["result_frame"] = c.words(jtag.CSR_BASE + 0x058, 1)[0]
            row["error_code"] = c.words(jtag.CSR_BASE + 0x010, 1)[0]
            row["snapshot"] = c.full_csr()
            row["status_after"] = c.words(jtag.CSR_BASE + 0x00C, 1)[0]
        finally:
            self.event("observation", row)
        csr.checked_snapshot(row["snapshot"])
        csr.require(row["epoch_hi_before"] == row["epoch_hi_after"], "epoch高位变化，无法绑定本次任务")
        return row

    def busy(self, row, expected, reject):
        """只接受ARMING→RUN，保留进度变化，首错/参数/身份/所有权必须一致。"""
        snapshot = row["snapshot"]
        states = [row["status_before"], snapshot[0x00C], row["status_after"]]
        if any((value & 7) not in (1, 2) for value in states):
            raise BusyWindowUnavailable("STATUS未完整包围ARMING/RUN：" + repr(states))
        for value in states:
            csr.require(value in (0x101, 0x102, 0x1102), "忙状态owner/head/safe/terminal/首错/保留位不符")
            state = value & 7
            csr.require(state >= self.last_busy_state, "RUN倒退至ARMING")
            self.last_busy_state = state
        observed_epoch = row["epoch_lo"] | row["epoch_hi_before"] << 32
        csr.require(observed_epoch == csr.epoch(snapshot) == self.expected_epoch and
                    row["result_frame"] == snapshot[0x058] == self.request.frame and row["error_code"] == 0,
                    "忙窗epoch/frame/错误身份变化")
        # AXI账本逐读变化是合法诊断；首故障寄存器并非动态LAST_AXI，必须保持无错。
        allowed = (0x00C, 0x064, 0x068)
        csr.require(all(snapshot[key] == expected[key] for key in csr.OFFSETS if key not in allowed),
                    "忙窗配置、常量、身份或首故障字段变化")
        csr.require(snapshot[0x064] == reject, "LAST_REJECT未形成真实0→1转换")
        if 1 in [value & 7 for value in states] and snapshot[0x00C] & 7 == 1:
            csr.require(snapshot[0x068] == 0, "ARMING尚未声明memory事务")
        return snapshot

    def await_busy(self, expected, seconds, poll_seconds):
        """UART发送完再观测；PS尚在IDLE装载时等待，终态/过快不能冒充忙窗。"""
        deadline = time.monotonic() + seconds
        while True:
            row = self.observation("await_busy")
            states = (row["status_before"], row["snapshot"][0x00C], row["status_after"])
            if all(value & 7 in (1, 2) for value in states):
                return self.busy(row, expected, 0)
            if not all(value in (0x400, 0x101, 0x102, 0x1102) for value in states):
                raise BusyWindowUnavailable("请求已离开可用忙窗口：" + repr(states))
            csr.require([value & 7 for value in states] == sorted(value & 7 for value in states),
                        "等待START期间状态倒退")
            if all(value == 0x400 for value in states):
                csr.require(csr.epoch(row["snapshot"]) == csr.epoch(self.initial) and
                            row["snapshot"][0x010] == 0 and row["snapshot"][0x064] == 0,
                            "等待START时IDLE身份或错误变化")
            # 首次跨越IDLE→ARMING/RUN的读不是忙窗证明，重读直到整组被忙状态包围。
            if time.monotonic() >= deadline:
                raise BusyWindowUnavailable("等待ARMING/RUN超时，未提交DAP负例")
            time.sleep(min(poll_seconds, max(0, deadline - time.monotonic())))

    def stop_cpu0(self):
        """仅在本次RUN已观测忙后停止当前运行CPU0，登记所有权并保存PC。"""
        c = self.controller
        c.verify_bindings(); c.gate(both=False)
        csr.require(not c.failed and not self.wire.failed and c.state("cpu0") == "Running",
                    "CPU0并非本次可停止的运行核")
        self.event("cpu0_stop_requested", {"ownership": "THIS_BUSY_OBSERVER", "pl_clock_action": "NONE"})
        c.call("t20.busy.cpu0.stop", c.targets["cpu0"].stop)
        state = c.state("cpu0")
        csr.require(state.startswith("Stopped"), "CPU0 stop未生效")
        self.owned_stop = True
        c.gate()
        self.record["cpu0_stop"] = {"state": state, "pc": c.pc(), "ownership": "THIS_BUSY_OBSERVER"}
        self.event("cpu0_stopped", self.record["cpu0_stop"])

    def resume_cpu0(self):
        """拒绝证明成立后只继续本观察器实际停止的CPU0，失败锁绝不清除。"""
        c = self.controller
        csr.require(self.owned_stop and not c.failed and not self.wire.failed, "CPU0继续缺少所有权或会话已失败")
        c.verify_bindings(); c.gate()
        self.event("cpu0_resume_requested", {"ownership": "THIS_BUSY_OBSERVER", "pc": c.pc()})
        c.call("t20.busy.cpu0.con", c.targets["cpu0"].con)
        state = c.state("cpu0")
        csr.require(state == "Running", "CPU0 continue未生效")
        self.owned_stop = False
        c.gate(both=False)
        self.event("cpu0_resumed", {"state": state})

    def capture(self, row):
        """消费同一真实receipt，保存原UART、两个完整头及全部框后复用T18 checker。"""
        directory = transport.new_directory(self.run / "same_run_golden")
        self.wire.rx_file.flush()
        start = self.wire.rx_file.tell()
        previous_epoch = self.wire.epoch
        result = {"status": "IN_PROGRESS", "sequence": self.request.sequence, "frame": self.request.frame}
        try:
            receipt = self.controller.call("t20.busy.wire.receipt", self.wire.receipt, self.request)
            self.event("same_run_receipt", receipt)
            raw = bytes.fromhex(receipt["header_hex"] + receipt["payload_hex"])
            self.wire.rx_file.flush()
            with transport.exact_path(self.wire.rx_file.name).open("rb") as stream:
                stream.seek(start)
                actual = stream.read(self.wire.rx_file.tell() - start)
            csr.require(actual == raw, "同RUN receipt与实际UART磁盘字节不同")
            meta, heads, boxes = transport.decode_response(raw[:40], raw[40:], self.request, 0, previous_epoch)
            csr.require(meta == receipt["meta"] and meta["epoch"] == self.expected_epoch and
                        meta["last_reject"] == 1, "同RUN终态未保留busy拒绝或epoch身份")
            result["meta"] = meta
            model.save(directory / "boxes.json", boxes)
            tensors = {}
            for name, payload in heads.items():
                path = directory / (name + ".bin")
                with path.open("xb") as stream:
                    stream.write(payload)
                tensors[name] = {"path": str(path), "tensor_sha256": transport.digest(payload), "byte_length": len(payload)}
            reference_path, reference_raw = model.read_bound(row["reference"])
            reference = json.loads(reference_raw.decode("utf-8"))["samples"][0]
            capture = {"frame_id": reference["frame_id"], "sample_id": reference["sample_id"],
                       "input": reference["input"], "head_tensors": tensors,
                       "nms_output_box_count": len(boxes), "detections": boxes}
            model.save(directory / "capture.json", {"schema_version": 1, "kind": "s2b_fixed_capture",
                "model_manifest_sha256": transport.MODEL_SHA, "samples": [capture]})
            result["checker_identity_mapping"] = {"actual_frame": self.request.frame,
                "frozen_reference_frame": reference["frame_id"], "reason": "同冻结sample000输入；原UART独立绑定实际身份"}
            report = model.checker.check_capture(reference_path, directory / "capture.json")
            model.save(directory / "capture_check.json", report)
            csr.require(report["status"] == "PASS_OFFLINE_CAPTURE_CHECK", "同RUN检测头或全部检测框黄金不符")
            result["status"] = "PASS_SAME_RUN_RECEIPT_AND_GOLD"
            return result
        except BaseException as error:
            result.update(status="FAIL_LATCHED", error=repr(error))
            raise
        finally:
            self.wire.rx_file.flush()
            path = transport.exact_path(self.wire.rx_file.name)
            with path.open("rb") as stream:
                stream.seek(start); raw = stream.read(self.wire.rx_file.tell() - start)
            with (directory / "uart_response_raw.bin").open("xb") as stream:
                stream.write(raw)
            result["raw_uart"] = {"path": str(path), "offset": start, "bytes": len(raw), "sha256": transport.digest(raw)}
            model.save(directory / "result.json", result)

    def verify_ack_idle(self):
        """黄金结果消费后确认相同任务已ACK并安全回到IDLE。"""
        self.controller.verify_bindings()
        self.controller.gate(both=False)
        snapshot = self.controller.full_csr()
        csr.idle(snapshot)
        csr.require(csr.epoch(snapshot) == self.expected_epoch and
                    snapshot[0x058] == self.request.frame,
                    "同RUN黄金消费后的ACK/IDLE身份不符")
        return snapshot

    def execute(self, request, header, payload, row, *, observation_seconds, poll_seconds):
        """完整动作闭环；异常后fail_stop保留CPU0停止和失败锁，不操作CPU1。"""
        self.request, self.expected_epoch = request, self.wire.epoch + 1
        core, drain = struct.unpack_from("<II", payload)
        expected = {**self.initial, 0x014: request.frame, **csr.BASE_PARAMETERS, 0x028: core, 0x02C: drain,
                    0x010: 0, 0x050: self.expected_epoch & 0xFFFFFFFF, 0x054: self.expected_epoch >> 32,
                    0x058: request.frame, 0x064: 0, 0x06C: 0, 0x070: 0, 0x074: 0}
        try:
            self.record["request"] = {"header_hex": header.hex(), "payload_sha256": transport.digest(payload),
                "input": row["input"], "core_timeout": core, "drain_timeout": drain,
                "previous_epoch": self.wire.epoch, "expected_epoch": self.expected_epoch}
            self.event("run_request", self.record["request"])
            self.tx_attempted = True
            self.controller.call("t20.busy.wire.send", self.wire.send, request, header, payload, row["input"])
            self.await_busy(expected, observation_seconds, poll_seconds)
            self.stop_cpu0()
            before = self.busy(self.observation("before_start"), expected, 0)
            response, error_text, error_repr = "SDK_RETURNED_WITHOUT_EXCEPTION", None, None
            self.dap_attempted = True
            try:
                self.controller.call("t20.busy.apu.mwr", self.controller.targets["apu"].mwr,
                    "--bypass_cache_synq", address=jtag.CSR_BASE + 8, size=1, word_size=4, words=[1])
            except Exception as error:
                response, error_text, error_repr = jtag.bus_error_kind(error), str(error), repr(error)
            self.event("dap_start_response", {"native_response": response, "exception_text": error_text,
                "exception_repr": error_repr})
            # 无论原生结果能否识别，先保留真实后快照，再作拒绝判定。
            after = self.busy(self.observation("after_start"), expected, 1)
            unresolved = response == "UNKNOWN" and _is_ahb_ap_write_bresp_unresolved(
                error_text, jtag.CSR_BASE + 8)
            self.record["rejection"] = {"before": before, "after": after, "native_response": response,
                "exception_text": error_text, "exception_repr": error_repr,
                "expected_bresp": "SLVERR",
                "observed_bresp": (response if response in ("SLVERR", "DECERR")
                                   else "NOT_OBSERVED")}
            if unresolved:
                self.record["rejection"]["classification"] = "AHB_AP_TRANSACTION_ERROR_BRESP_UNRESOLVED"
            csr.require(response == "SLVERR" or unresolved,
                        "原生响应不能证明SLVERR，也不符合限定的AHB AP错误签名：" + response)
            self.resume_cpu0()
            self.record["golden"] = self.capture(row)
            self.record["ack_idle"] = self.verify_ack_idle()
            status = ("BUSY_REJECTION_AND_GOLD_BRESP_UNRESOLVED" if unresolved
                      else "PASS_BUSY_START_REJECTION_AND_GOLD")
            return self.finish(status)
        except BaseException as error:
            if self.tx_attempted:
                self.controller.failed = self.wire.failed = True
                self.controller.record.update(status="FAILED", error=repr(error))
                try:
                    self.controller.fail_stop()
                except BaseException as cleanup_error:
                    self.controller.record.setdefault("cleanup_errors", []).append(repr(cleanup_error))
            status = "NOT_EXECUTED_IN_BUSY" if isinstance(error, BusyWindowUnavailable) else "FAIL_LATCHED"
            self.finish(status, error)
            raise

    def finish(self, status, error=None):
        """保留此观察器范围的原生调用、UART事件及实际原件SHA，不抹去失败证据。"""
        self.record.update(status=status, finished_at_utc8=datetime.now(csr.TZ).isoformat(),
            elapsed_seconds=time.monotonic() - self.started, tx_attempted=self.tx_attempted,
            dap_start_attempted=self.dap_attempted, cpu0_stop_still_owned=self.owned_stop,
            final_wire_epoch=self.wire.epoch, final_sequence=self.wire.last_sequence,
            sdk_calls=copy.deepcopy(self.controller.record["calls"][self.call_start:]),
            cleanup_errors=copy.deepcopy(self.controller.record.get("cleanup_errors", [])),
            uart_receipt_attempts=copy.deepcopy(self.wire.receipt_attempts[self.receipt_start:]),
            uart_events=copy.deepcopy(self.wire.events[self.event_start:]))
        for name, stream in (("uart_rx", self.wire.rx_file), ("uart_tx_headers", self.wire.tx_header_file)):
            stream.flush(); self.record[name] = model.binding(Path(stream.name))
        if error is not None:
            self.record["error"] = repr(error)
        self.log.close()
        model.save(self.run / "busy_result.json", json.loads(json.dumps(self.record, ensure_ascii=False, default=repr)))
        return self.record


def execute_busy_start(controller, wire, config_binding, run_dir, *, preparation,
                       observation_seconds=5.0, poll_seconds=0.01):
    """正式入口：同一已审visibility1会话、真实IDLE及109计划/LOAD/seed门禁全部必须成立。"""
    run = csr._new_run(run_dir)
    call_start = len(controller.record["calls"]) if type(controller) is jtag.JtagController else 0
    try:
        _seconds(observation_seconds, "观测期限", 120)
        _seconds(poll_seconds, "轮询间隔", 1)
        _, admitted, initial = csr.preflight(controller, wire, config_binding, static=False)
        plan = csr.bound_json(preparation)
        model.validate_plan(plan)
        admitted["preparation"] = preparation
        request, header, payload = _request(wire, plan)
    except BaseException as error:
        calls = controller.record["calls"][call_start:] if type(controller) is jtag.JtagController else []
        model.save(run / "busy_result.json", {"schema_version": 1, "status": "BLOCKED_BEFORE_TX",
            "hardware_execution": "NOT_RUN", "config_binding": config_binding, "preparation": preparation,
            "error": repr(error), "sdk_calls": json.loads(json.dumps(calls, ensure_ascii=False, default=repr))})
        raise
    observer = _Observer(controller, wire, run, admitted, initial, scope="BORROWED_SESSION_UART_DAP_REQUESTED")
    observer.call_start = call_start
    return observer.execute(request, header, payload, plan["rows"][0],
                            observation_seconds=observation_seconds, poll_seconds=poll_seconds)
