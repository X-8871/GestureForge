"""T20借用既有会话验收外层CSR；导入不创建会话、不访问设备。"""
from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import time

try:
    from . import s2b_board_acceptance as model
    from . import s2b_board_jtag as jtag
    from . import s2b_board_transport as transport
except ImportError:
    import s2b_board_acceptance as model
    import s2b_board_jtag as jtag
    import s2b_board_transport as transport

ROOT = Path(__file__).absolute().parents[1]
TZ = timezone(timedelta(hours=8))
OFFSETS = (0, 4) + tuple(range(0x00C, 0x078, 4))
BASE_PARAMETERS = {0x018: 0, 0x01C: 519168, 0x020: 0x00100000,
                   0x024: 5903100}
CONFIG_KEYS = {"schema_version", "source_commit", "bindings", "build_details",
               "visibility_proof", "visibility_review", "visibility_review_sha256",
               "final_platform_manifest", "final_review", "final_review_sha256", "scene"}
PARAMETER_CASES = (
    ("input_range", {0x018: 4}, 2),
    ("gf8_range", {0x020: 0x00100004}, 2),
    ("input_length", {0x01C: 519167}, 3),
    ("gf8_length", {0x024: 5903099}, 3),
    ("zero_core_deadline", {0x028: 0}, 1),
    ("zero_drain_deadline", {0x02C: 0}, 1),
    ("range_over_length_argument", {0x018: 4, 0x01C: 519167, 0x028: 0}, 2),
    ("length_over_argument", {0x024: 5903099, 0x02C: 0}, 3),
)


class CsrAcceptanceError(RuntimeError):
    """实际响应、身份或安全条件与已冻结语义不符。"""


def require(condition, message):
    """拒绝缺失条件；不能用部分观察替代实板证明。"""
    if not condition:
        raise CsrAcceptanceError(message)


def uint(value, bits=32):
    """拒绝布尔、负数和溢出，不自动截断参数。"""
    require(type(value) is int and 0 <= value < 1 << bits, "整数范围或类型错误")
    return value


def bound_json(item):
    """实际字节SHA及重复字段核验，复用现有精确路径校验。"""
    require(type(item) is dict and set(item) == {"path", "sha256"}, "文件绑定字段错误")
    raw = jtag.bound_bytes(item)
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "JSON重复字段")
            result[key] = value
        return result
    def constant(value):
        raise CsrAcceptanceError("JSON非有限数值：" + value)
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=constant)


def epoch(snapshot):
    """从已逐字核验的快照组成64位epoch。"""
    return snapshot[0x050] | snapshot[0x054] << 32


def checked_snapshot(snapshot):
    """完整字段类型、标识、常量及保留位检查。"""
    require(type(snapshot) is dict and set(snapshot) == set(OFFSETS), "CSR快照字段缺失或多余")
    for key, value in snapshot.items():
        uint(key); uint(value)
    require(snapshot[0] == 0x53324250 and snapshot[4] == 0x100, "CSR ID/ABI错误")
    require(snapshot[0x00C] & ~0x3F07 == 0 and snapshot[0x00C] & 7 <= 6, "CSR状态保留位/编码错误")
    require(0 <= snapshot[0x010] <= 12 and 0 <= snapshot[0x064] <= 6 and
            snapshot[0x068] <= 0x3FF and snapshot[0x074] <= 0x1F, "CSR诊断保留位/编码错误")
    expected = {0x030: 0x10000000, 0x034: 0x02000000, 0x038: 0x01000000,
                0x03C: 0x01ADADB8, 0x040: 0x01A46100, 0x044: 5070,
                0x048: 0x01AD5E80, 0x04C: 20280}
    require(all(snapshot[k] == v for k, v in expected.items()), "arena/head固定布局错误")
    return snapshot


def idle(snapshot):
    """空闲必须真实安全、PS owner、head无效、账本零且无故障。"""
    checked_snapshot(snapshot)
    require(snapshot[0x00C] == 0x400 and snapshot[0x010] == 0 and
            all(snapshot[k] == 0 for k in (0x068, 0x06C, 0x070, 0x074)), "并非安全空闲/账本非零")


def error_safe(snapshot, expected_epoch, frame, code):
    """错误安全终态保留失败身份，不能有PL owner/head或待决事务。"""
    checked_snapshot(snapshot)
    require(snapshot[0x00C] == 0xC05 and snapshot[0x010] == code and
            epoch(snapshot) == expected_epoch and snapshot[0x058] == frame and
            snapshot[0x068] == 0, "ERROR_SAFE/epoch/frame/error/账本不符")


def unchanged(before, after, allowed=()):
    """LAST_REJECT等约定诊断只在明确允许时改变，其余字段逐字相等。"""
    checked_snapshot(before); checked_snapshot(after)
    require(all(before[key] == after[key] for key in OFFSETS if key not in allowed),
            "拒绝操作产生额外CSR副作用")


def preflight(controller, wire, config_binding, *, static):
    """复用T18实际artifact/visibility1门禁，冻结scene不代替实际核状态。"""
    require(type(controller) is jtag.JtagController and type(wire) is jtag.JtagWireSession,
            "必须借用真实T16控制器和UART对象")
    config = bound_json(config_binding)
    require(type(config) is dict and set(config) == CONFIG_KEYS and
            type(config["schema_version"]) is int and config["schema_version"] == 1, "配置schema错误")
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    require(result.returncode == 0 and result.stdout.strip() == config["source_commit"], "配置源码基线不是当前HEAD")
    require(config["bindings"] == controller.bindings, "配置和实际部署bindings不一致")
    admitted = model.admit(controller, wire, config["build_details"], config["visibility_proof"],
                           config["visibility_review"], config["visibility_review_sha256"],
                           config["final_platform_manifest"], config["final_review"], config["final_review_sha256"])
    scene = bound_json(config["scene"])
    require(type(scene) is dict and set(scene) == {"schema_version", "kind", "expected_snapshot"} and
            type(scene["schema_version"]) is int and scene["schema_version"] == 1 and
            scene["kind"] == ("s2b-csr-static-scene/1.0.0" if static else "s2b-csr-uart-scene/1.0.0"),
            "场景schema/种类错误")
    require(type(scene["expected_snapshot"]) is dict and
            set(scene["expected_snapshot"]) == {str(k) for k in OFFSETS}, "scene CSR字段不完整")
    expected = {k: scene["expected_snapshot"][str(k)] for k in OFFSETS}
    checked_snapshot(expected); idle(expected)
    controller.gate(both=static)
    require(controller.state("cpu0").startswith("Stopped") if static else controller.state("cpu0") == "Running",
            "CPU0状态不满足本场景")
    actual = controller.stable_csr("t20_admission")
    require(actual == expected and epoch(actual) == wire.epoch, "实际场景或UART epoch与冻结scene不同")
    return config, admitted, actual


def prior_model_success(wire, plan):
    """按实际发送与消费顺序重放，最后有效权重及最后完整RUN绑定sample000。"""
    require(not wire.failed and wire.abort_pending is None and wire.epoch > 0, "缺少正常模型会话")
    wire.rx_file.flush()
    raw_path = transport.exact_path(wire.rx_file.name)
    actual = raw_path.read_bytes()
    require(actual == b"".join(wire.rx_chunks), "UART磁盘原字节与实际读取记录不同")
    _, weights = model.read_bound(plan["weights"])
    _, input_raw = model.read_bound(plan["rows"][0]["input"])
    _, reference_raw = model.read_bound(plan["rows"][0]["reference"])
    reference = json.loads(reference_raw.decode("utf-8"))["samples"][0]
    geometry = reference["input"]["geometry_wh"]
    require(type(geometry) is list and len(geometry) == 2 and
            all(type(value) is int and 1 <= value <= 0xFFFF for value in geometry),
            "sample000冻结黄金几何格式错误")
    sent_rows = list(wire.sent_requests.items())
    require(sent_rows and [key for key, _ in sent_rows] == list(range(1, wire.last_sequence + 1)),
            "前置发送sequence缺失或乱序")
    require(len(wire.receipt_attempts) == len(sent_rows) and len(wire.events) == 2 * len(sent_rows),
            "前置存在未消费、重复、失败或未登记receipt")
    wire.tx_header_file.flush()
    require(transport.exact_path(wire.tx_header_file.name).read_bytes() ==
            b"".join(row[1][1] for row in sent_rows), "前置TX磁盘header与发送记录不同")
    response_bytes, current_weights, previous_epoch = [], None, 0
    last_request, last_payload = None, None
    for index, ((sequence, sent_row), attempt) in enumerate(zip(sent_rows, wire.receipt_attempts)):
        require(attempt.get("abort_ready") is False, "前置中间ABORT阶段不能充当完整成功receipt")
        raw = bytes.fromhex(attempt["raw_received_hex"])
        require(len(raw) >= transport.HEADER.size + transport.META.size, "前置receipt截断或失败")
        request = transport.Header.unpack(bytes.fromhex(attempt["request_header_hex"]))
        sent, header, payload = sent_row
        checked, checked_header = transport.make_request(request.op, request.sequence, request.frame, payload,
            width=request.width, height=request.height, repeat=request.repeat)
        require(sequence == request.sequence and sent == request == checked and
                header == request.pack() == checked_header and payload.hex() == attempt["request_payload_hex"],
                "前置发送记录与receipt不一致")
        require(request.repeat == 1, "前置重复RUN缺少逐帧receipt绑定")
        tx, rx = wire.events[2 * index:2 * index + 2]
        require(tx.get("direction") == "TX" and tx.get("status") == "SENT_TO_SERIAL_DRIVER" and
                tx.get("sequence") == sequence and tx.get("frame") == request.frame and tx.get("op") == request.op and
                tx.get("header_sha256") == transport.digest(header) and
                tx.get("payload_sha256") == transport.digest(payload) and
                tx.get("payload_crc32") == request.payload_crc and
                tx.get("sent_bytes") == len(header) + len(payload) and
                tx.get("sent_sha256") == transport.digest(header + payload), "前置TX实际发送事件不一致或交错")
        response_header = transport.Header.unpack(raw[:40])
        require(rx.get("direction") == "RX" and rx.get("header") == response_header.__dict__ and
                rx.get("header_sha256") == transport.digest(raw[:40]) and
                rx.get("payload_sha256") == transport.digest(raw[40:]) and rx.get("bytes") == len(raw) and
                rx.get("raw_meta") == list(transport.META.unpack_from(raw, 40)), "前置RX实际消费事件不一致或交错")
        meta, _, _ = transport.decode_response(raw[:40], raw[40:], request, 0, previous_epoch)
        require(meta["response_code"] == 0, "前置receipt不是完整成功")
        if request.op == transport.OP_WEIGHTS:
            current_weights = payload
        if request.op in (transport.OP_RUN, transport.OP_DIAG):
            previous_epoch = meta["epoch"]
        response_bytes.append(raw)
        last_request, last_payload = request, payload
    responses = b"".join(response_bytes)
    require(actual.endswith(responses), "前置receipt与UART磁盘连续原字节不一致")
    prefix = actual[:len(actual) - len(responses)]
    if prefix:
        # 唯一允许的响应前缀是既有启动banner，禁止将任意多余接收字节当作历史噪声。
        parts = prefix.decode("ascii").strip().split(" ")
        require(len(parts) == 5 and parts[:2] == ["S2B-INFERENCE/1", "READY"] and
                parts[2].startswith("SOURCE=") and parts[3].startswith("XSA=") and
                all(len(part.split("=", 1)[1]) == 64 and
                    all(char in "0123456789abcdef" for char in part.split("=", 1)[1]) for part in parts[2:4]) and
                prefix == (" ".join(parts[:4]) + " MODEL=" + transport.MODEL_SHA + "\r\n").encode("ascii"),
                "前置UART含未绑定的额外字节或错误启动banner")
    transport.require(previous_epoch == wire.epoch, "前置重放epoch与实际wire不同")
    require(current_weights == weights and last_request.op == transport.OP_RUN and last_request.frame == 0 and
            (last_request.width, last_request.height, last_request.repeat) == (*geometry, 1) and
            last_payload[8:] == input_raw,
            "最后有效LOAD或最终完整消费RUN不是冻结权重与sample000")


class _Runner:
    """内部执行器；生产入口已通过门禁，mock只验证算法且明确标记无硬件。"""
    def __init__(self, controller, wire, run, admitted, *, scope="BORROWED_SESSION_DAP_REQUESTED"):
        self.controller, self.wire, self.run = controller, wire, run
        self.log = (run / "csr_events.jsonl").open("x", encoding="utf-8", newline="\n")
        self.started, self.call_start = time.monotonic(), len(controller.record["calls"])
        self.record = {"schema_version": 1, "status": "IN_PROGRESS", "hardware_execution": scope,
                       "admission": admitted, "scenarios": [], "started_at_utc8": datetime.now(TZ).isoformat(),
                       "limitations": ["不创建会话/服务/串口；不自动stop/resume/reset或清理外部资源。",
                                       "CPU1及目标链是逐次观测；进程树峰值内存未测。",
                                       "不能用mock或SDK未知总线异常宣称实板SLVERR。"]}

    def event(self, kind, value):
        """每次动作即时追加原始字段，异常前已有证据保留。"""
        row = {"time_utc8": datetime.now(TZ).isoformat(), "kind": kind, "value": value}
        self.log.write(json.dumps(row, ensure_ascii=False, default=repr) + "\n"); self.log.flush()

    def snapshot(self, label, *, stopped=True, stable=True):
        """静止CSR和运行观察分开；运行期不能假定全部progress不变。"""
        self.controller.verify_bindings(); self.controller.gate(both=stopped)
        result = self.controller.stable_csr(label) if stable else self.controller.full_csr()
        self.event("csr:" + label, result)
        return checked_snapshot(result)

    def write(self, offset, value, *, reject=None):
        """DAP拒绝必须有明确原生响应；成功由后续实际CSR效果核验。"""
        uint(offset); uint(value)
        require(offset in (0x008, 0x014, 0x018, 0x01C, 0x020, 0x024, 0x028, 0x02C, 0x05C, 0x060),
                "禁止写保留/调试/冷复位寄存器")
        self.controller.verify_bindings(); self.controller.gate()
        response, caught = "SDK_RETURNED_WITHOUT_EXCEPTION", None
        try:
            self.controller.call("t20.apu.mwr", self.controller.targets["apu"].mwr, "--bypass_cache_synq",
                                 address=jtag.CSR_BASE + offset, size=1, word_size=4, words=[value])
        except Exception as error:
            caught = error; response = jtag.bus_error_kind(error)
        self.event("write", {"offset": offset, "value": value, "native_response": response,
                             "exception_repr": repr(caught) if caught is not None else None})
        if reject is not None:
            require(response == reject, "原生拒绝无法证明：" + response)
        else:
            require(caught is None, "合法写产生原生异常：" + response)
        return response

    def reject_command(self, name, command, last_reject):
        """除LAST_REJECT外完全相同；不能将合法诊断变化当作副作用失败。"""
        before = self.snapshot(name + ":before")
        response = self.write(0x008, command, reject="SLVERR")
        after = self.snapshot(name + ":after")
        unchanged(before, after, (0x064,))
        require(after[0x064] == last_reject, "LAST_REJECT错误")
        self.record["scenarios"].append({"name": name, "status": "PASS", "native_response": response,
                                         "before": before, "after": after})
        return after

    def parameters(self, frame, core, drain, changes=None):
        """在IDLE逐字配置并读回，参数优先级只来自现有T11。"""
        uint(frame); uint(core); uint(drain)
        before = self.snapshot("parameters:before"); idle(before)
        values = {0x014: frame, **BASE_PARAMETERS, 0x028: core, 0x02C: drain}
        values.update(changes or {})
        for offset, value in values.items():
            self.write(offset, value)
        after = self.snapshot("parameters:after")
        expected = {**before, **values}
        require(after == expected, "参数写回或无副作用检查失败")
        return after

    def ack(self, expected_epoch, *, code, frame):
        """匹配ACK仅对稳定安全终态；不reset、不清真实adapter账本。"""
        before = self.snapshot("ack:before"); error_safe(before, expected_epoch, frame, code)
        self.write(0x05C, expected_epoch & 0xFFFFFFFF); self.write(0x060, expected_epoch >> 32)
        configured = self.snapshot("ack:configured")
        require(configured == {**before, 0x05C: expected_epoch & 0xFFFFFFFF, 0x060: expected_epoch >> 32},
                "ACK参数副作用错误")
        self.write(0x008, 4)
        after = self.snapshot("ack:after"); idle(after)
        expected = {**configured, 0x00C: 0x400, 0x010: 0, 0x064: 0,
                    0x06C: 0, 0x070: 0, 0x074: 0}
        require(after == expected, "matching ACK更改了额外字段或身份")
        return after

    def static_matrix(self, frame_base, core, drain):
        """参数START合法占一个epoch，ERROR_SAFE不取得PL所有权或memory事务。"""
        uint(frame_base); uint(core); uint(drain)
        require(core > 0 and drain > 0 and frame_base <= 0xFFFFFFFF - len(PARAMETER_CASES), "基线参数错误")
        initial = self.snapshot("matrix:initial"); idle(initial)
        require(epoch(initial) <= 0xFFFFFFFFFFFFFFFF - len(PARAMETER_CASES), "epoch空间不足")
        self.reject_command("idle_bad_encoding", 3, 5)
        for index, (name, changes, code) in enumerate(PARAMETER_CASES):
            frame = frame_base + index
            before = self.parameters(frame, core, drain, changes)
            target_epoch = epoch(before) + 1
            self.write(0x008, 1)
            terminal = self.snapshot(name + ":terminal")
            error_safe(terminal, target_epoch, frame, code)
            expected = {**before, 0x00C: 0xC05, 0x010: code, 0x050: target_epoch & 0xFFFFFFFF,
                        0x054: target_epoch >> 32, 0x058: frame, 0x064: 0}
            require(terminal == expected, "参数START存在额外epoch/owner/ledger/参数副作用")
            self.record["scenarios"].append({"name": name, "status": "PASS", "before": before,
                                             "terminal": terminal, "expected_error_code": code,
                                             "meaning": "合法START接受一次，参数准入失败；不是SLVERR"})
            if index == 0:
                self.reject_command("terminal_start", 1, 2)
                # 错误ACK只改变ACK寄存器与LAST_REJECT，终态本体保持。
                wrong = target_epoch ^ 1
                before_ack = self.snapshot("wrong_ack:before")
                self.write(0x05C, wrong & 0xFFFFFFFF); self.write(0x060, wrong >> 32)
                after_ack = self.snapshot("wrong_ack:configured")
                require(after_ack == {**before_ack, 0x05C: wrong & 0xFFFFFFFF, 0x060: wrong >> 32},
                        "错误ACK参数副作用")
                self.reject_command("wrong_ack", 4, 4)
            self.ack(target_epoch, code=code, frame=frame)
            self.reject_command("duplicate_ack:" + name, 4, 3)
        self.parameters(initial[0x014], initial[0x028], initial[0x02C],
                        {key: initial[key] for key in BASE_PARAMETERS})
        self.record["configuration_restored"] = "原始frame/input/GF8/deadline配置已逐字恢复；合法epoch及失败frame历史不回退。"
        self.record["scenarios"].append({"name": "busy_start", "status": "BLOCKED",
            "reason": "自然推进的AXI_PROGRESS不能逐字冻结，现有CSR无busy reject attempt身份或拒绝写因果trace。",
            "equivalent_observable_proposal": "由总控冻结最小真实AXI-Lite COMMAND/B响应及epoch/owner/START接受脉冲观测；不暂停PL clock或清账本。"})
        self.record["wire_after_external_csr"] = {"status": "BLOCKED", "protocol_epoch_unchanged": self.wire.epoch,
            "reason": "DAP START增epoch，而既有UART没有外部epoch同步；旧wire不得接正常RUN。需另行统一冷恢复建立新会话。"}
        return self.snapshot("matrix:final")

    def short_deadline(self, frame, core, drain, observation_seconds, *, required_fault_detail_mask=0):
        """CPU停核时实际START短期限；隔离仅观察，不把FAULT当作已安全归还。"""
        require(type(observation_seconds) in (int, float) and math.isfinite(observation_seconds) and
                0 < observation_seconds <= 120 and type(core) is int and 0 < core <= 10000 and
                type(drain) is int and 0 < drain <= 0xFFFFFFFF, "短期限或观察上限错误")
        uint(required_fault_detail_mask)
        require(required_fault_detail_mask & ~0x1F == 0, "必需故障标志超出FAULT_DETAIL定义")
        before = self.parameters(frame, core, drain)
        target_epoch = epoch(before) + 1
        require(target_epoch < 1 << 64, "epoch耗尽")
        self.write(0x008, 1)
        deadline = time.monotonic() + observation_seconds
        isolated_seen = False
        while time.monotonic() < deadline:
            current = self.snapshot("short_deadline:observe", stable=False)
            require(epoch(current) == target_epoch and current[0x058] == frame and not current[0x00C] & 0x200,
                    "取消任务epoch/frame/head错误")
            phase = current[0x00C] & 7
            if phase == 6:
                require(current[0x00C] & 0x100 and not current[0x00C] & 0xC00,
                        "隔离错误归还所有权")
                isolated_seen = True
            if phase == 5:
                terminal = self.snapshot("short_deadline:terminal")
                error_safe(terminal, target_epoch, frame, 5)
                require(terminal[0x074] & required_fault_detail_mask == required_fault_detail_mask,
                        "安全终态缺少本场景必需故障标志；保留终态，不发送ACK")
                self.ack(target_epoch, code=5, frame=frame)
                result = {"name": "short_deadline", "status": "PASS", "terminal": terminal,
                          "isolated_seen": isolated_seen, "hot_golden_recovery": "BLOCKED",
                          "reason": "只证明实际core timeout/code5安全排空及匹配ACK；DAP改变epoch，旧UART无同步入口。",
                          "next": "总控另行核实统一冷恢复→同位流/ELF重新部署→正常sample000黄金比对；该结果须独立记录冷恢复。"}
                self.record["scenarios"].append(result)
                return result
            require(phase in (1, 2, 3, 6), "短期限出现非约定终态")
            time.sleep(0.001)
        result = {"name": "short_deadline", "status": "BLOCKED", "isolated_seen": isolated_seen,
                  "reason": "观察期限内未取得稳定ERROR_SAFE/code5；未ACK/清账本/访问arena。",
                  "hot_golden_recovery": "NOT_RUN"}
        self.record["scenarios"].append(result)
        return result

    def finish(self, status, error=None):
        """复制本次真实DAP原日志，不关闭借用会话或丢弃失败UART。"""
        self.record.update(status=status, elapsed_seconds=time.monotonic() - self.started,
                           finished_at_utc8=datetime.now(TZ).isoformat())
        if error is not None:
            self.record["error"] = repr(error)
        self.record["dap_calls"] = copy.deepcopy(self.controller.record["calls"][self.call_start:])
        self.record["readbacks"] = copy.deepcopy(self.controller.record.get("readbacks", []))
        self.record["uart_receipt_attempts"] = copy.deepcopy(getattr(self.wire, "receipt_attempts", []))
        self.record["uart_events"] = copy.deepcopy(getattr(self.wire, "events", []))
        if hasattr(self.wire, "rx_file"):
            self.wire.rx_file.flush()
            path = transport.exact_path(self.wire.rx_file.name)
            self.record["uart_raw_binding"] = {"path": str(path), "bytes": path.stat().st_size,
                                               "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        self.log.close()
        # SDK调用含Header等原对象；与T16原日志同样保存其精确repr，避免收尾丢失失败证据。
        transport.write_json_new(self.run / "csr_result.json",
                                 json.loads(json.dumps(self.record, ensure_ascii=False, default=repr)))
        return self.record


def _new_run(run_dir):
    """板上正式证据只能写入T20新的RunId，不覆盖任何既有目录。"""
    parent = transport.exact_path(ROOT / "report/evidence/S2B-T20", "directory")
    return transport.new_directory(run_dir, parent=parent)


def _execute(controller, wire, config_binding, run_dir, action, *, static):
    """缺少依赖先保存BLOCKED；实际写失败锁存，不擅自恢复旧任务。"""
    run = _new_run(run_dir)
    try:
        _, admitted, _ = preflight(controller, wire, config_binding, static=static)
    except BaseException as error:
        transport.write_json_new(run / "csr_result.json", {"schema_version": 1, "status": "BLOCKED_BEFORE_IO",
            "hardware_execution": "NOT_RUN", "config_binding": config_binding, "error": repr(error)})
        raise
    runner = _Runner(controller, wire, run, admitted)
    try:
        value = action(runner)
        return runner.finish("SCENARIO_RESULTS_SAVED_NOT_STAGE_ACCEPTANCE"), value
    except BaseException as error:
        controller.failed = True; wire.failed = True
        runner.finish("FAIL_LATCHED", error)
        raise


def execute_static_matrix(controller, wire, config_binding, run_dir, *, frame_base,
                          core_timeout, drain_timeout):
    """root先停CPU0/1；只在visibility1安全IDLE验收静止矩阵，不自动resume。"""
    return _execute(controller, wire, config_binding, run_dir,
                    lambda runner: runner.static_matrix(frame_base, core_timeout, drain_timeout), static=True)


def execute_short_deadline(controller, wire, config_binding, preparation, run_dir, *, frame,
                           core_timeout, drain_timeout, observation_seconds):
    """需root事先装载有效模型/输入并停CPU；不伪造UART热恢复。"""
    def action(runner):
        plan = bound_json(preparation); model.validate_plan(plan)
        prior_model_success(wire, plan)
        return runner.short_deadline(frame, core_timeout, drain_timeout, observation_seconds)
    return _execute(controller, wire, config_binding, run_dir, action, static=True)


def execute_abort_recovery(controller, wire, config_binding, preparation, run_dir, *,
                           frame, core_timeout, drain_timeout):
    """已有有效LOAD/RUN后mode2→真实DAP ABORT→mode3 ACK→sample000黄金热恢复。"""
    def action(runner):
        uint(frame); uint(core_timeout); uint(drain_timeout)
        require(core_timeout > 0 and drain_timeout > 0 and frame < 0xFFFFFFFF, "ABORT配置错误")
        plan = bound_json(preparation)
        model.validate_plan(plan)
        prior_model_success(wire, plan)
        payload = struct.pack("<III", 2, core_timeout, drain_timeout)
        request, header = transport.make_request(transport.OP_DIAG, wire.last_sequence + 1, frame, payload)
        controller.call("t20.wire.abort.send", wire.send, request, header, payload,
                        {"kind": "t20_abort_diagnostic", "config": config_binding})
        runner.event("abort_request", {"header_hex": header.hex(), "payload_hex": payload.hex()})
        event = controller.dap_abort(wire, request)
        runner.event("abort_final", event)
        controller.call("t20.wire.abort.explicit_ack", wire.acknowledge_abort, wire.last_sequence + 1)
        require(wire.abort_pending is None and not wire.failed, "ABORT显式ACK未完成")
        actual = runner.snapshot("abort_ack:idle", stopped=False); idle(actual)
        require(epoch(actual) == wire.epoch, "ACK后的UART/CSR身份不符")
        sample_run = runner.run / "golden_sample000"
        golden = model.AcceptanceRunner(wire, sample_run, runner.record["admission"])
        golden.record["hardware_execution"] = runner.record["hardware_execution"]
        try:
            golden.run_input(plan["rows"][0], wire.last_sequence + 1, frame + 1, 1,
                             core_timeout, drain_timeout, "recovery")
            golden.finish("PASS_SAMPLE000_AFTER_ABORT_ONLY")
        except BaseException as error:
            golden.finish("FAIL_LATCHED", error)
            raise
        result = {"name": "dap_abort_hot_recovery", "status": "PASS", "abort_epoch": event["requested_epoch"],
                  "golden_epoch": wire.epoch, "scope": "真实WAIT/final/CSR/ACK及sample000完整双头/框，不代表109或1000"}
        runner.record["scenarios"].append(result)
        return result
    return _execute(controller, wire, config_binding, run_dir, action, static=False)
