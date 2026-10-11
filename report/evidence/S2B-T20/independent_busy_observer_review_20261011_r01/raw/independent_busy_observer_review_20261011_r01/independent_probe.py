"""独立补充反例：仅扩展原生内存设备，不替换生产准入、receipt或失败锁。"""
import copy
import gc
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import traceback
import zlib

run = Path(__file__).resolve().parent
root = run.parents[3]
sys.path.insert(0, str(root))
from verification import test_s2b_csr_busy_observer as fixture
from verification import s2b_csr_busy_observer as busy

j, model, transport = busy.jtag, busy.model, busy.transport
temporary = run / "probe_cases"
temporary.mkdir()
fixture.TEST_PARENT = temporary
os.environ.pop("S2B_BUSY_FIXTURE_OUTPUT", None)
rows = []


def save(path, data):
    """每个审查结果单独新建，避免覆盖前轮。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


class ReviewTarget(fixture.NativeTarget):
    """以实际原生方法的返回/抛错注入停止失效及CPU1意外运行。"""
    def stop(self):
        if getattr(self.session, "stop_no_effect", False):
            self.session.operations.append(("stop_no_effect", self._name))
            return None
        result = super().stop()
        if getattr(self.session, "cpu1_after_stop", False):
            self.session.objects[12].running = True
        return result

    def con(self, *args, **kwargs):
        if getattr(self.session, "resume_no_effect", False):
            self.session.operations.append(("con_no_effect", self._name))
            return None
        return super().con(*args, **kwargs)


class ReviewSerial(fixture.NativeSerial):
    """仅修改原生串口实际产生/保存的字节，全部通过真实解析器。"""
    def complete(self):
        super().complete()
        kind = getattr(self.session, "extra_fault", None)
        if kind == "partial_header":
            del self.raw[13:]
        if kind == "partial_payload":
            del self.raw[53:]
        if kind in ("response_seq", "response_frame"):
            offset = 12 if kind == "response_frame" else 8
            struct.pack_into("<I", self.raw, offset, struct.unpack_from("<I", self.raw, offset)[0] + 1)
            struct.pack_into("<I", self.raw, 36, zlib.crc32(self.raw[:36]))

    def read(self, count):
        if (getattr(self.session, "extra_fault", None) == "rx_disk_extra" and
                self.next_request is not None and not getattr(self.session, "disk_injected", False)):
            self.session.review_rx.write(b"X")
            self.session.review_rx.flush()
            self.session.disk_injected = True
        return super().read(count)


# 只替换测试模块用来构造原生夹具的类；被测JtagController/WireSession和所有生产函数保持原样。
fixture.NativeTarget = ReviewTarget
fixture.NativeSerial = ReviewSerial


def run_case(name, configure, success=False, before_request=False, cleanup_may_fail=False):
    """复用最小手算场景，新增条件独立断言并保留动作原始证据。"""
    case = fixture.BusyObserverTests("test_progress_change_nonempty_gold_success")
    case.setUp()
    error = None
    try:
        case.session.review_rx = case.rx
        configure(case)
        try:
            result = case.execute()
        except Exception as exc:
            error = repr(exc)
            result = case.result() if (case.run / "busy_result.json").is_file() else None
        operations = copy.deepcopy(case.session.operations)
        assert not any(item[1] == j.NAMES[2] for item in operations), operations
        if success:
            assert error is None and result["status"] == "PASS_BUSY_START_REJECTION_AND_GOLD", error
            assert (case.wire.epoch, case.wire.last_sequence) == (2, 3)
            assert result["rejection"]["native_response"] == "SLVERR"
            observations = [json.loads(line)["value"] for line in (case.run / "busy_events.jsonl").read_text(encoding="utf-8").splitlines()
                            if json.loads(line)["kind"] == "observation"]
            assert len(observations) == 3
            assert [item["snapshot"]["104"] for item in observations] == [7, 0, 7]
            assert [item["snapshot"]["100"] for item in observations] == [0, 0, 1]
            assert all(item["epoch_hi_before"] == item["epoch_hi_after"] == 0 and item["epoch_lo"] == 2 for item in observations)
            actual = json.loads((case.run / "same_run_golden/boxes.json").read_text(encoding="utf-8"))
            assert len(actual) == 2
            for box, (r, c, category) in zip(actual, ((4, 3, 1), (6, 6, 0))):
                expected = [(32*c+16-40.5)/416, (32*r+16-41-52)/312,
                            (32*c+16+40.5)/416, (32*r+16+41-52)/312]
                assert box["score"] == .25 and box["class_id"] == category
                assert box["source_order"] == (r*13+c)*15+category
                assert max(abs(a-b) for a, b in zip(box["xyxy"], expected)) < 1e-15
            assert (case.run / "same_run_golden/head13.bin").read_bytes() == case.heads[:5070]
            assert (case.run / "same_run_golden/head26.bin").read_bytes() == case.heads[5070:]
        else:
            assert error is not None, "反例被错误接受"
            if before_request:
                assert not any(item[0] in ("mwr", "con", "stop") for item in operations)
                assert case.wire.last_sequence >= 2
            else:
                assert case.controller.failed and case.wire.failed
                assert result["status"] in ("FAIL_LATCHED", "NOT_EXECUTED_IN_BUSY")
                if not cleanup_may_fail:
                    assert not case.controller.targets["cpu0"].running
                else:
                    assert result["cleanup_errors"], "未保留实际停止失败"
        target = run / ("raw_" + name)
        target.mkdir()
        if not case.observer.log.closed:
            case.observer.finish("BLOCKED_BEFORE_REQUEST" if before_request else "REVIEW_ONLY")
        for filename in ("busy_events.jsonl", "busy_result.json"):
            shutil.copyfile(case.run / filename, target / filename)
        if (case.run / "same_run_golden").is_dir():
            shutil.copytree(case.run / "same_run_golden", target / "same_run_golden")
        if success:
            originals = target / "golden_originals"
            originals.mkdir()
            mapping = []
            for filename in ("basis.json", "golden_source.json", "reference.json", "head13.bin", "head26.bin"):
                source = case.root / filename
                shutil.copyfile(source, originals / filename)
                mapping.append({"original_path": str(source), "preserved_path": str(originals / filename),
                                "sha256": hashlib.sha256(source.read_bytes()).hexdigest()})
            save(originals / "mapping.json", {"files": mapping,
                 "input_generation": "ASCII I重复519168次，原件不复制", "weights_generation": "ASCII W重复5903100次，原件不复制"})
        rows.append({"name": name, "status": "PASS", "expected_success": success, "error": error,
                     "actual_status": result["status"] if result else "BLOCKED_BEFORE_REQUEST", "operations": operations,
                     "controller_failed": case.controller.failed, "wire_failed": case.wire.failed,
                     "cpu0_running": case.controller.targets["cpu0"].running, "cpu1_untouched": True})
        print(name + ": PASS", flush=True)
    finally:
        case.tearDown()
        gc.collect()


def set_session(key, value):
    """配置原生模拟设备，不改控制器及UART会话属性。"""
    return lambda case: setattr(case.session, key, value)


run_case("hand_nonempty_dynamic", lambda case: None, success=True)
for name, error in (("okay", None), ("unknown", "DAP write failed"), ("decerr", "DECERR"),
                    ("ambiguous_slverr", "SLVERR or disconnected")):
    run_case(name, set_session("bus_error", error))
for name, offset, value in (("epoch", 0x050, 3), ("epoch_hi", 0x054, 1), ("frame", 0x058, 2),
    ("config_frame", 0x014, 9), ("input_address", 0x018, 4), ("deadline", 0x028, 1),
    ("ack_shadow", 0x05c, 2), ("constant", 0x030, 4), ("owner", 0x00c, 2),
    ("fault_logical", 0x06c, 4), ("fault_physical", 0x070, 4), ("fault_detail", 0x074, 1),
    ("error_code", 0x010, 9), ("first_pending", 0x00c, 0x2102), ("head_valid", 0x00c, 0x302),
    ("recovering", 0x00c, 0x103), ("done_safe", 0x00c, 0xe04), ("error_safe", 0x00c, 0xc05),
    ("fault_isolated", 0x00c, 0x106), ("run_to_arming", 0x00c, 0x101)):
    run_case(name, set_session("mutation", (offset, value)))
for name, key in (("stale_reject", "stale_reject"), ("too_fast_send", "finish_on_send"),
    ("too_fast_stop", "finish_on_stop"), ("too_fast_after_start", "finish_after_write"),
    ("stop_exception", "fail_stop_native"), ("resume_exception", "fail_resume_native"),
    ("resume_no_effect", "resume_no_effect"), ("cpu1_unexpected_running", "cpu1_after_stop")):
    run_case(name, set_session(key, True))
run_case("stop_no_effect", set_session("stop_no_effect", True), cleanup_may_fail=True)
for fault in ("head", "box", "missing_box", "header_crc", "payload_crc", "epoch", "reject"):
    run_case("uart_" + fault, lambda case, fault=fault: setattr(case.serial, "response_fault", fault))
for fault in ("partial_header", "partial_payload", "response_seq", "response_frame", "rx_disk_extra"):
    run_case(fault, set_session("extra_fault", fault))


def replaced_history(case):
    """实际按序发送替换权重和新seed，最后有效LOAD必须被识别。"""
    case.send_receipt(1, 3, b"R" * 5903100)
    case.send_receipt(2, 4, struct.pack("<II", 1, 2) + b"I" * 519168)


def outstanding_history(case):
    """实际发送未消费LOAD，不制造返回字典。"""
    payload = b"W" * 5903100
    request, header = transport.make_request(1, 3, 0, payload)
    case.wire.send(request, header, payload, {"scope": "MOCK_ONLY"})


run_case("replaced_load", replaced_history, before_request=True)
run_case("outstanding_load", outstanding_history, before_request=True)
run_case("tx_disk_extra", lambda case: (case.tx.write(b"X"), case.tx.flush()), before_request=True)
run_case("history_rx_disk_extra", lambda case: (case.rx.write(b"X"), case.rx.flush()), before_request=True)

save(run / "independent_probe_result.json", {"status": "PASS", "count": len(rows), "cases": rows,
     "scope": "MOCK_ONLY_SOFTWARE，实际控制器/运输器及T18完整checker；不等于公开准入或实板通过",
     "production_monkeypatches": [], "admission_replacements": [], "manual_controller_latch_or_epoch_changes": []})
