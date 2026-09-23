"""通过隔离 Vivado 仿真验证 G0 独立 CSR/控制 FSM。"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]
_MANIFEST = _ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
_G0_SPEC = _ROOT / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
_EVIDENCE = _ROOT / "report/evidence/S2A-T11/control_csr_simulation.json"
_RTL = _ROOT / "src/s2a_control_csr.sv"
_TB = _ROOT / "sim/tb_s2a_control_csr.sv"
_RUNNER = Path(__file__).resolve()
_MANIFEST_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
_SEED = 0x2A110923
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")
_CONTROL_VECTOR_NAMES = (
    "csr", "completion_boundary", "timeout_recovery",
    "memory_error_recovery", "accumulator_overflow_recovery",
)
_REGISTER_EXPECTED = {
    "CMD": ("0x00", "W1P", 0),
    "STATUS": ("0x04", "RO", 0),
    "ERROR_CODE": ("0x08", "RO", 0),
    "FRAME_ID": ("0x0C", "RW_IDLE", 0),
    "INPUT_ADDR": ("0x10", "RW_IDLE", 0),
    "INPUT_BYTES": ("0x14", "RW_IDLE", 519168),
    "WEIGHT_ADDR": ("0x18", "RW_IDLE", 1048576),
    "WEIGHT_BYTES": ("0x1C", "RW_IDLE", 5903100),
    "FEATURE_BASE": ("0x20", "RO", 16777216),
    "FEATURE_LIMIT": ("0x24", "RO", 28159416),
    "TIMEOUT_CYCLES": ("0x28", "RW_IDLE", 0),
    "HEAD13_ADDR": ("0x2C", "RO", 27549952),
    "HEAD13_BYTES": ("0x30", "RO", 5070),
    "HEAD26_ADDR": ("0x34", "RO", 28139136),
    "HEAD26_BYTES": ("0x38", "RO", 20280),
    "ACK": ("0x3C", "W1P", 0),
}
_READ_DEFAULTS = {
    name: value[2] for name, value in _REGISTER_EXPECTED.items()
    if name not in ("CMD", "ACK")
}
_WRITABLE = {
    int(_REGISTER_EXPECTED[name][0], 16): name
    for name in ("FRAME_ID", "INPUT_ADDR", "INPUT_BYTES", "WEIGHT_ADDR",
                 "WEIGHT_BYTES", "TIMEOUT_CYCLES")
}
_READ_ONLY = {
    int(_REGISTER_EXPECTED[name][0], 16): name
    for name in ("STATUS", "ERROR_CODE", "FEATURE_BASE", "FEATURE_LIMIT",
                 "HEAD13_ADDR", "HEAD13_BYTES", "HEAD26_ADDR", "HEAD26_BYTES")
}


class XorShift32:
    """产生 T11 固定种子的随机 CSR 访问。"""

    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF

    def next_u32(self) -> int:
        value = self.state
        value ^= (value << 13) & 0xFFFFFFFF
        value &= 0xFFFFFFFF
        value ^= value >> 17
        value &= 0xFFFFFFFF
        value ^= (value << 5) & 0xFFFFFFFF
        self.state = value & 0xFFFFFFFF
        return self.state


def _sha256(data: bytes) -> str:
    """计算原始字节 SHA-256。"""
    return hashlib.sha256(data).hexdigest()


def _canonical_sha(value: object) -> str:
    """对稳定 JSON 表示计算摘要。"""
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":")).encode("utf-8")
    return _sha256(payload)


def _is_under(child: Path, parent: Path) -> bool:
    """跨盘符安全判断路径包含关系。"""
    try:
        return os.path.commonpath((str(child), str(parent))).casefold() == str(parent).casefold()
    except ValueError:
        return False


def _load_manifest() -> tuple[dict, bytes]:
    raw = _MANIFEST.read_bytes()
    if _sha256(raw) != _MANIFEST_SHA256:
        raise AssertionError("G0 manifest 原始 SHA-256 已变化")
    manifest = json.loads(raw.decode("utf-8"))
    protocol = manifest["control_protocol"]
    registers = protocol["register_map"]
    observed = {
        item["name"]: (item["offset"], item["access"], int(item["reset"]))
        for item in registers
    }
    if observed != _REGISTER_EXPECTED:
        raise AssertionError("G0 register_map 字段与 T11 冻结契约不一致")
    if protocol["handshake"] != (
        "single outstanding transfer accepted on rising edge when csr_valid && csr_ready; "
        "csr_rdata is the read value on that same cycle"
    ):
        raise AssertionError("G0 CSR handshake 语义变化")
    if protocol["ready"] != "csr_ready is high outside hard reset; software must change/deassert valid after each accepted transfer":
        raise AssertionError("G0 CSR ready 语义变化")
    if protocol["register_alignment"] != (
        "csr_addr must be 32-bit aligned; unaligned/reserved reads return zero and writes are ignored; "
        "writes to RO registers are ignored"
    ):
        raise AssertionError("G0 CSR 对齐/只读语义变化")
    if protocol["soft_reset"] != (
        "accepted CMD.soft_reset aborts current task and has priority over CMD.start in the same write"
    ):
        raise AssertionError("G0 soft_reset 语义变化")
    if protocol["timeout"] != (
        "timeout_cycles must be nonzero; count rising edges after the accepted start edge; "
        "completion at the Nth edge wins over timeout, otherwise abort at that edge"
    ):
        raise AssertionError("G0 timeout 语义变化")
    if protocol["priority"] != [
        "hard_reset", "soft_reset", "memory_or_argument_or_numeric_error",
        "completion", "timeout"
    ]:
        raise AssertionError("G0 控制优先级变化")

    vectors = manifest["operator_test_plan"]["protocol_vectors"]
    if (vectors["csr"]["ready_outside_hard_reset"] != 1 or
            vectors["csr"]["stall_cycles"] != [] or
            vectors["csr"]["transfer_rule"] != (
                "CSR has no backpressure; PS presents valid for one accepted rising edge, then deasserts or changes the request before the next rising edge"
            ) or
            vectors["completion_boundary"]["engine_done_edge_after_start"] != 5 or
            vectors["completion_boundary"]["timeout_cycles_equal"] != 5 or
            vectors["timeout_recovery"]["engine_done_edge_after_start"] != 5 or
            vectors["timeout_recovery"]["timeout_cycles"] != 4 or
            vectors["memory_error_recovery"]["response_cases"] != [
                {"mem_error_code": 6, "expected_csr_error_code": 6},
                {"mem_error_code": 7, "expected_csr_error_code": 6},
            ] or
            vectors["accumulator_overflow_recovery"]["expected_csr_error_code"] != 7):
        raise AssertionError("G0 控制协议 directed vectors 变化")
    return manifest, raw


def _make_random_vectors(manifest: dict) -> tuple[bytes, dict]:
    """按固定 PRNG 生成 256 个 CSR 读写及独立读回黄金。"""
    rng = XorShift32(_SEED)
    registers = dict(_READ_DEFAULTS)
    addresses = list(_WRITABLE) + list(_READ_ONLY) + [0x0D, 0x40]
    records: list[tuple[int, int, int, int]] = []
    expected_values: list[int] = []
    for index in range(256):
        address = addresses[rng.next_u32() % len(addresses)]
        data = rng.next_u32()
        mode = rng.next_u32() % 2
        if mode:
            if address in _WRITABLE:
                registers[_WRITABLE[address]] = data
            expected = (registers[_WRITABLE[address]] if address in _WRITABLE
                        else _READ_DEFAULTS.get(_READ_ONLY.get(address, ""), 0))
        else:
            expected = (registers[_WRITABLE[address]] if address in _WRITABLE
                        else _READ_DEFAULTS.get(_READ_ONLY.get(address, ""), 0))
        records.append((mode, address, data, expected))
        expected_values.append(expected)
    payload = "".join(
        f"{mode} {address:02X} {data:08X} {expected:08X}\n"
        for mode, address, data, expected in records
    ).encode("ascii")
    summary = {
        "count": len(records),
        "seed": f"0x{_SEED:08X}",
        "state_after_generation": f"0x{rng.state:08X}",
        "vector_sha256": _sha256(payload),
        "golden_readback_sha256": _canonical_sha(expected_values),
        "control_protocol_sha256": _canonical_sha(
            manifest["operator_test_plan"]["protocol_vectors"]
        ),
    }
    return payload, summary


def _combine_process_streams(stdout: str, stderr: str) -> str:
    """保留 stdout/stderr 全文，并在两路内容之间显式隔行。"""
    return stdout + "\n" + stderr


def _run_phase(command: list[str], work: Path, name: str) -> tuple[int, str]:
    """在隔离工作目录运行单个 Vivado 阶段并保存短日志文件。"""
    result = subprocess.run(command, cwd=work, capture_output=True, text=True,
                            errors="replace", timeout=600, check=False)
    combined = _combine_process_streams(result.stdout, result.stderr)
    (work / f"{name}.log").write_text(combined, encoding="utf-8", newline="\n")
    return result.returncode, combined


def _parse_xsim_summary(log: str) -> dict[str, int]:
    """拒绝仿真失败诊断，并只接受唯一且位于覆盖摘要之后的 PASS 标记。"""
    if "FAIL:" in log.upper():
        raise AssertionError("xsim 输出含 FAIL: 诊断")
    if re.search(r"(?im)^\s*(?:ERROR|FATAL)\s*:", log):
        raise AssertionError("xsim 输出含 ERROR/FATAL 诊断")
    result_matches = list(re.finditer(
        r"RESULT random_accesses=(\d+) csr_transfers=(\d+) directed_checks=(\d+) protocol_cases=(\d+)",
        log))
    if len(result_matches) != 1:
        raise AssertionError("xsim 必须恰有一条 RESULT 覆盖摘要")
    pass_marker = "PASS S2A-T11 standalone CSR/control FSM"
    pass_positions = [match.start() for match in re.finditer(re.escape(pass_marker), log)]
    if len(pass_positions) != 1:
        raise AssertionError("xsim 必须恰有一个 PASS 标记")
    if pass_positions[0] < result_matches[0].end():
        raise AssertionError("PASS 标记必须位于覆盖摘要之后")
    values = tuple(map(int, result_matches[0].groups()))
    return {
        "random_accesses": values[0],
        "csr_transfers": values[1],
        "directed_checks": values[2],
        "protocol_cases": values[3],
        "pass_marker_count": len(pass_positions),
    }


class S2AControlCsrRtlTest(unittest.TestCase):
    """运行隔离的 xvlog/xelab/xsim 并绑定仿真证据。"""

    def test_xsim_log_gate_rejects_failure_diagnostics(self) -> None:
        """即使工具退出码为零，失败诊断也不得被 PASS 摘要掩盖。"""
        result = (
            "RESULT random_accesses=256 csr_transfers=595 directed_checks=116 protocol_cases=5\n"
        )
        passed = result + "PASS S2A-T11 standalone CSR/control FSM\n"
        self.assertEqual(_parse_xsim_summary(passed)["protocol_cases"], 5)
        boundary_stdout = result.rstrip("\n") + "PASS S2A-T11 standalone CSR/control FSM"
        boundary_stderr = "FATAL: simulator diagnostic without trailing newline"
        merged_boundary = _combine_process_streams(boundary_stdout, boundary_stderr)
        self.assertEqual(merged_boundary,
                         boundary_stdout + "\n" + boundary_stderr)
        for failure_log in (
            result + "FAIL: state mismatch\nPASS S2A-T11 standalone CSR/control FSM\n",
            result + "ERROR: simulation diagnostic\nPASS S2A-T11 standalone CSR/control FSM\n",
            result + "FATAL: simulation fatal diagnostic\nPASS S2A-T11 standalone CSR/control FSM\n",
            merged_boundary,
            "PASS S2A-T11 standalone CSR/control FSM\n" + result,
            result,
            passed + "PASS S2A-T11 standalone CSR/control FSM\n",
        ):
            with self.assertRaises(AssertionError):
                _parse_xsim_summary(failure_log)

    def test_control_csr_and_backend_events(self) -> None:
        manifest, manifest_raw = _load_manifest()
        if not _G0_SPEC.is_file():
            self.fail("G0 正式冻结文档不存在")
        spec_raw = _G0_SPEC.read_bytes()
        if spec_raw.startswith(b"\xef\xbb\xbf"):
            self.fail("G0 正式冻结文档出现意外 UTF-8 BOM")
        random_vectors, random_summary = _make_random_vectors(manifest)
        for source in (_RTL, _TB, _RUNNER):
            if not source.is_file():
                self.fail(f"T11 输入文件缺失：{source.name}")
            raw = source.read_bytes()
            if raw.startswith(b"\xef\xbb\xbf") or b"\r\n" in raw:
                self.fail(f"T11 文件必须是 UTF-8 无 BOM/LF：{source.name}")
            raw.decode("utf-8")

        with tempfile.TemporaryDirectory(prefix="s2a_t11_control_") as temp_name:
            work = Path(temp_name).resolve(strict=True)
            temp_root = Path(tempfile.gettempdir()).resolve(strict=True)
            if not _is_under(work, temp_root):
                self.fail("Vivado 隔离目录不在系统 TEMP 下")
            if _is_under(work, _ROOT.resolve(strict=True)):
                self.fail("Vivado 工作目录错误地位于仓库内")
            (work / "s2a_control_csr.sv").write_bytes(_RTL.read_bytes())
            (work / "tb_s2a_control_csr.sv").write_bytes(_TB.read_bytes())
            (work / "csr_random.dat").write_bytes(random_vectors)
            for file_name in ("s2a_control_csr.sv", "tb_s2a_control_csr.sv", "csr_random.dat"):
                if not (work / file_name).is_file():
                    self.fail(f"隔离输入复制失败：{file_name}")

            xvlog, xvlog_log = _run_phase(
                [str(_XILINX_BIN / "xvlog.bat"), "-sv", "s2a_control_csr.sv",
                 "tb_s2a_control_csr.sv"], work, "xvlog")
            if xvlog != 0:
                self.fail(f"xvlog 失败，退出码 {xvlog}；隔离日志末尾：\n{xvlog_log[-5000:]}")
            xelab, xelab_log = _run_phase(
                [str(_XILINX_BIN / "xelab.bat"), "tb_s2a_control_csr",
                 "-s", "s2a_control_csr_sim"], work, "xelab")
            if xelab != 0:
                self.fail(f"xelab 失败，退出码 {xelab}；隔离日志末尾：\n{xelab_log[-5000:]}")
            xsim, xsim_log = _run_phase(
                [str(_XILINX_BIN / "xsim.bat"), "s2a_control_csr_sim", "-R"],
                work, "xsim")
            if xsim != 0:
                self.fail(f"xsim 失败，退出码 {xsim}；隔离日志末尾：\n{xsim_log[-5000:]}")
            try:
                xsim_summary = _parse_xsim_summary(xsim_log)
            except AssertionError as exc:
                self.fail(f"xsim 日志验收失败：{exc}")
            random_count = xsim_summary["random_accesses"]
            csr_transfer_count = xsim_summary["csr_transfers"]
            directed_count = xsim_summary["directed_checks"]
            protocol_case_count = xsim_summary["protocol_cases"]
            if (random_count != 256 or csr_transfer_count < random_count or
                    directed_count < 90 or
                    protocol_case_count != len(_CONTROL_VECTOR_NAMES)):
                self.fail(
                    "仿真覆盖计数低于固定验收门槛："
                    f"random={random_count}, csr_transfers={csr_transfer_count}, "
                    f"directed={directed_count}, protocol_cases={protocol_case_count}, "
                    f"expected_protocol_cases={len(_CONTROL_VECTOR_NAMES)}"
                )

            evidence = {
                "task": "S2A-T11",
                "baseline_head": "025724ccd904c2208b38783d274edeb728004e13",
                "binding_sha256": {
                    "g0_manifest": _sha256(manifest_raw),
                    "g0_spec": _sha256(spec_raw),
                    "rtl": _sha256(_RTL.read_bytes()),
                    "testbench": _sha256(_TB.read_bytes()),
                    "runner": _sha256(_RUNNER.read_bytes()),
                },
                "stimulus": random_summary,
                "coverage": {
                    "random_csr_accesses": random_count,
                    "csr_accepted_transfers": csr_transfer_count,
                    "directed_checks": directed_count,
                    "protocol_case_counter": protocol_case_count,
                    "manifest_protocol_vectors": list(_CONTROL_VECTOR_NAMES),
                    "not_covered_manifest_vector": "cancel_pending_write requires memory-master integration",
                    "argument_error_single_faults": {
                        "BAD_RANGE": 2,
                        "BAD_LENGTH": 2,
                        "BAD_ARGUMENT_zero_timeout": 1,
                    },
                    "operator_codes_preserved": [1, 2, 3, 4, 5, 6, 7],
                    "memory_codes_checked": {"1": 1, "2": 2, "6": 6, "7": 6},
                    "reset_cases": ["hard_reset_idle", "hard_reset_busy",
                                    "soft_reset_idle_defaults", "soft_reset_busy",
                                    "soft_reset_wins_over_start"],
                    "recovery_cases": ["ACK_done", "ACK_error", "legal_start_after_ACK"],
                },
                "vivado": {
                    "xvlog_exit_code": xvlog,
                    "xelab_exit_code": xelab,
                    "xsim_exit_code": xsim,
                    "xsim_pass_marker_count": xsim_summary["pass_marker_count"],
                    "xsim_failure_diagnostic_count": 0,
                },
                "limitations": [
                    "仅验证独立 CSR/控制 FSM 与行为后端事件 stub。",
                    "未连接 T10 memory model、PL memory master、DMA 或真实算子。",
                    "backend_abort 事件检查不证明未握手 memory 写撤销集成。",
                    "未执行综合、资源估算、时序分析或实物验证。",
                    "3-bit 错误输入域仅含 G0 定义的 0..7，不伪造不可表达的未知码。",
                    "不测试多个非法参数同时出现时的错误码优先级，也不承诺 CMD/ACK 读回或 ACK 双位同写语义。",
                ],
            }
            payload = (json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True)
                       + "\n").encode("utf-8")
            if payload.startswith(b"\xef\xbb\xbf") or b"\r\n" in payload:
                self.fail("证据必须为 UTF-8 无 BOM/LF")
            _EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
            _EVIDENCE.write_bytes(payload)
            parsed = json.loads(_EVIDENCE.read_text(encoding="utf-8"))
            self.assertEqual(parsed["binding_sha256"]["runner"], _sha256(_RUNNER.read_bytes()))
            self.assertEqual(parsed["vivado"]["xvlog_exit_code"], 0)
            self.assertEqual(parsed["vivado"]["xelab_exit_code"], 0)
            self.assertEqual(parsed["vivado"]["xsim_exit_code"], 0)

        self.assertIn("PASS S2A-T11", xsim_log)
        self.assertEqual(random_count, 256)


if __name__ == "__main__":
    unittest.main()
