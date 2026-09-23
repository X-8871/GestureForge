"""通过隔离 Vivado 验证 S2A-T12 runtime memory protocol integration。"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]
_MANIFEST = _ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
_SPEC = _ROOT / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
_CONTROL = _ROOT / "src/s2a_control_csr.sv"
_MODEL = _ROOT / "sim/s2a_memory_model.sv"
_MASTER = _ROOT / "src/s2a_memory_master.sv"
_SHELL = _ROOT / "src/s2a_runtime_shell.sv"
_TB = _ROOT / "sim/tb_s2a_runtime_protocol.sv"
_RUNNER = Path(__file__).resolve()
_EVIDENCE = _ROOT / "report/evidence/S2A-T12/runtime_protocol_simulation.json"
_MANIFEST_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
_BASELINE_HEAD = "2309d2cbe7a27951ac433b2ca4eca7987301021b"
_SEED = 0x2A120923
_STALL_SCHEDULE = [0, 1, 2, 7, 3]
_CLASS_NAMES = ["read_input", "read_weights", "read_feature", "write_feature"]
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")
_SOURCES = {
    "s2a_control_csr.sv": _CONTROL,
    "s2a_memory_model.sv": _MODEL,
    "s2a_memory_master.sv": _MASTER,
    "s2a_runtime_shell.sv": _SHELL,
    "tb_s2a_runtime_protocol.sv": _TB,
}


class XorShift32:
    """生成 T12 独立 runtime transaction 测试流。"""

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

    def selector(self, bound: int) -> int:
        if bound <= 0:
            raise ValueError("随机选择器范围必须为正数")
        return self.next_u32() % bound


def _sha256_bytes(payload: bytes) -> str:
    """计算原始字节 SHA-256。"""
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    """计算文件原始字节 SHA-256。"""
    return _sha256_bytes(path.read_bytes())


def _canonical_sha(value: object) -> str:
    """计算稳定 JSON 值摘要。"""
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(payload)


def _is_under(child: Path, parent: Path) -> bool:
    """判断 child 是否位于 parent 中。"""
    try:
        return os.path.commonpath((str(child), str(parent))).casefold() == str(parent).casefold()
    except ValueError:
        return False


def _load_manifest() -> tuple[dict, bytes, list[tuple[int, int]]]:
    """校验 G0 绑定并提取唯一 feature tensor 半开区间。"""
    raw = _MANIFEST.read_bytes()
    if _sha256_bytes(raw) != _MANIFEST_SHA256:
        raise AssertionError("G0 manifest 原始 SHA-256 改变")
    manifest = json.loads(raw.decode("utf-8"))
    address_map = manifest["address_map"]
    input_desc = address_map["input"]
    weight_desc = address_map["weight_package"]
    workspace = address_map["feature_workspace"]
    if ((int(input_desc["address"]), int(input_desc["length_bytes"])) != (0, 519168) or
            (int(weight_desc["address"]), int(weight_desc["length_bytes"])) !=
            (0x00100000, 5903100) or
            int(workspace["base_address"]) != 0x01000000 or
            int(workspace["end_address_exclusive"]) != 28159416):
        raise AssertionError("G0 input/weight/feature workspace address map 改变")
    unique_ranges: set[tuple[int, int]] = set()
    for layer in manifest["layers"]:
        if layer.get("op") == "yolo":
            continue
        start = int(layer["tensor_address"])
        end = start + int(layer["tensor_length_bytes"])
        if start < int(workspace["base_address"]) or end > int(workspace["end_address_exclusive"]):
            raise AssertionError("manifest feature tensor 超出 workspace")
        unique_ranges.add((start, end))
    ranges = sorted(unique_ranges)
    if len(ranges) != 36:
        raise AssertionError(f"G0 unique feature tensor count 改变：{len(ranges)}")
    for previous, current in zip(ranges, ranges[1:]):
        if previous[1] > current[0]:
            raise AssertionError("G0 feature tensor 区间重叠")
    protocol = manifest["memory_protocol"]
    vectors = manifest["operator_test_plan"]["protocol_vectors"]
    if (vectors["memory_stall_cycles"] != _STALL_SCHEDULE or
            protocol["handshake"] != (
                "single outstanding word request; accepted when mem_valid && mem_ready; "
                "selected read lanes, mem_rdata and mem_error_code are valid on that same cycle"
            ) or
            protocol["alignment"] != (
                "32-bit byte address; mem_addr[1:0] must be zero or the accepted request "
                "returns error code BAD_RANGE; little-endian byte lanes"
            ) or
            protocol["stability"] != (
                "hold valid, address, direction, write data and both strobes stable until handshake or abort"
            ) or
            protocol["reset_abort"] != (
                "hard/soft reset or timeout cancels a pending request without a later memory side effect"
            )):
        raise AssertionError("G0 memory protocol contract changed")
    recovery = vectors["memory_error_recovery"]["response_cases"]
    if recovery != [
        {"mem_error_code": 6, "expected_csr_error_code": 6},
        {"mem_error_code": 7, "expected_csr_error_code": 6},
    ]:
        raise AssertionError("G0 memory error recovery vectors changed")
    return manifest, raw, ranges


def _initial_byte(address: int) -> int:
    """复现 T10 行为模型公开的稳定初始 byte pattern。"""
    return ((address & 0xFF) ^ ((address >> 8) & 0xFF) ^
            ((address >> 16) & 0xFF) ^ ((address >> 24) & 0xFF) ^ 0xA5)


def _initial_word(address: int) -> int:
    """按 little-endian lane 构造初始读 word。"""
    return sum(_initial_byte(address + lane) << (lane * 8) for lane in range(4))


def _materialize_inputs(manifest: dict, ranges: list[tuple[int, int]],
                        work: Path) -> dict:
    """在隔离目录生成 G0 ranges 与随机 transfer vectors。"""
    input_desc = manifest["address_map"]["input"]
    weight_desc = manifest["address_map"]["weight_package"]
    feature_starts = [start for start, _ in ranges]
    range_lines = [
        f"{int(input_desc['address']):08X} "
        f"{int(input_desc['address']) + int(input_desc['length_bytes']):08X} "
        f"{int(weight_desc['address']):08X} "
        f"{int(weight_desc['address']) + int(weight_desc['length_bytes']):08X} "
        f"{len(ranges):08X}\n"
    ]
    range_lines.extend(f"{start:08X} {end:08X}\n" for start, end in ranges)
    range_payload = "".join(range_lines).encode("ascii")
    (work / "memory_ranges.dat").write_bytes(range_payload)

    params = feature_starts[2:6]
    if len(params) != 4 or any(address & 3 for address in params):
        raise AssertionError("manifest feature cancel-test addresses 未对齐")
    if any(address + 4 > ranges[index + 2][1] for index, address in enumerate(params)):
        raise AssertionError("manifest feature cancel-test word 超出 tensor 区间")
    params_payload = "".join(f"{address:08X}\n" for address in params).encode("ascii")
    (work / "runtime_params.dat").write_bytes(params_payload)

    random = XorShift32(_SEED)
    object_ranges = [
        (int(input_desc["address"]),
         int(input_desc["address"]) + int(input_desc["length_bytes"])),
        (int(weight_desc["address"]),
         int(weight_desc["address"]) + int(weight_desc["length_bytes"])),
        ranges[0], ranges[1],
    ]
    rows: list[str] = []
    stimuli: list[list[int]] = []
    goldens: list[list[int]] = []
    per_class = [0, 0, 0, 0]
    for class_id, (start, end) in enumerate(object_ranges):
        word_count = (end - start) // 4
        if word_count <= 0 or (end - start) % 4:
            raise AssertionError("runtime object 不包含完整对齐 word")
        for _ in range(1000):
            address = start + random.selector(word_count) * 4
            data = random.next_u32()
            strobe = 0xF
            expected_data = 0 if class_id == 3 else _initial_word(address)
            expected_stall = _STALL_SCHEDULE[per_class[class_id] % 5]
            per_class[class_id] += 1
            rows.append(
                f"{class_id} {address:08X} {data:08X} {strobe:X} "
                f"{expected_data:08X} {expected_stall}\n"
            )
            stimuli.append([class_id, address, data, strobe])
            goldens.append([class_id, expected_data, expected_stall])
    vector_payload = "".join(rows).encode("ascii")
    (work / "vectors.dat").write_bytes(vector_payload)
    if per_class != [1000, 1000, 1000, 1000]:
        raise AssertionError("random vector transfer counts changed")
    stall_plan = {
        name: [_STALL_SCHEDULE[index % 5] for index in range(1000)]
        for name in _CLASS_NAMES
    }
    return {
        "ranges_sha256": _sha256_bytes(range_payload),
        "ranges_bytes": len(range_payload),
        "ranges": ranges,
        "params_sha256": _sha256_bytes(params_payload),
        "feature_cancel_test_addresses": params,
        "vector_sha256": _sha256_bytes(vector_payload),
        "vector_bytes": len(vector_payload),
        "stimulus_sha256": _canonical_sha(stimuli),
        "golden_sha256": _canonical_sha(goldens),
        "stall_plan_sha256": _canonical_sha(stall_plan),
        "seed": _SEED,
        "state_after_generation": random.state,
        "counts": {name: 1000 for name in _CLASS_NAMES},
        "stimuli": stimuli,
        "goldens": goldens,
    }


def _combine_process_streams(stdout: str, stderr: str) -> str:
    """保留 Vivado 双流全文并插入明确行分隔。"""
    return stdout + "\n" + stderr


def _parse_xsim_summary(log: str) -> dict[str, int]:
    """严格解析唯一 RESULT/PASS，并拒绝任一失败诊断。"""
    if "FAIL:" in log.upper():
        raise AssertionError("xsim 日志含 FAIL: 诊断")
    if re.search(r"(?im)^\s*(?:ERROR|FATAL)\s*:", log):
        raise AssertionError("xsim 日志含 ERROR/FATAL 诊断")
    results = list(re.finditer(
        r"RESULT random_transfers=(\d+) accepted_read_input=(\d+) "
        r"accepted_read_weights=(\d+) accepted_read_feature=(\d+) "
        r"accepted_write_feature=(\d+) error_checks=(\d+) "
        r"cancel_checks=(\d+) retry_checks=(\d+)", log))
    if len(results) != 1:
        raise AssertionError("xsim 必须输出唯一 RESULT summary")
    pass_marker = "PASS S2A-T12 runtime protocol integration"
    pass_positions = [match.start() for match in re.finditer(re.escape(pass_marker), log)]
    if len(pass_positions) != 1 or pass_positions[0] < results[0].end():
        raise AssertionError("xsim 必须在 RESULT 后输出唯一 PASS marker")
    values = tuple(map(int, results[0].groups()))
    result = dict(zip(
        ("random_transfers", "read_input", "read_weights", "read_feature",
         "write_feature", "error_checks", "cancel_checks", "retry_checks"),
        values,
    ))
    if (result["random_transfers"] != 4000 or
            result["read_input"] != 1000 or result["read_weights"] != 1000 or
            result["read_feature"] != 1003 or result["write_feature"] != 1014 or
            result["error_checks"] != 5 or result["cancel_checks"] != 3 or
            result["retry_checks"] != 3):
        raise AssertionError(f"xsim summary count mismatch: {result}")
    result["pass_marker_count"] = len(pass_positions)
    return result


def _run_phase(tool: Path, args: list[str], work: Path, name: str,
               repository: Path, deadline: float) -> tuple[int, str]:
    """在经检查的系统 TEMP cwd 执行 Vivado 阶段。"""
    temp_root = Path(tempfile.gettempdir()).resolve(strict=True)
    work = work.resolve(strict=True)
    if (not work.is_dir() or not _is_under(work, temp_root) or
            _is_under(work, repository.resolve(strict=True))):
        raise RuntimeError(f"拒绝在仓库或系统 TEMP 之外运行 Vivado：{work}")
    if not tool.is_file():
        raise FileNotFoundError(f"Vivado 工具不存在：{tool}")
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("T12 Vivado 流程超过 600 秒限制")
    command = " ".join(
        f'"{arg}"' if (" " in arg or "&" in arg) else arg
        for arg in (str(tool), *args)
    )
    completed = subprocess.run(
        f'cmd.exe /d /s /c "{command}"', cwd=work, shell=False,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=remaining, check=False,
    )
    output = _combine_process_streams(completed.stdout, completed.stderr)
    (work / f"{name}.log").write_text(output, encoding="utf-8", newline="\n")
    return completed.returncode, output


class S2ARuntimeProtocolRtlTest(unittest.TestCase):
    """验证 log fail-closed 与 T12 Vivado runtime integration。"""

    def test_xsim_log_gate(self) -> None:
        """失败、错误、标记缺失/重复/错序均不能被退出码零掩盖。"""
        result = (
            "RESULT random_transfers=4000 accepted_read_input=1000 "
            "accepted_read_weights=1000 accepted_read_feature=1003 "
            "accepted_write_feature=1014 error_checks=5 "
            "cancel_checks=3 retry_checks=3\n"
        )
        passed = result + "PASS S2A-T12 runtime protocol integration\n"
        self.assertEqual(_parse_xsim_summary(passed)["random_transfers"], 4000)
        boundary_stdout = result.rstrip("\n") + "PASS S2A-T12 runtime protocol integration"
        boundary_stderr = "FATAL: no-newline stderr diagnostic"
        self.assertEqual(_combine_process_streams(boundary_stdout, boundary_stderr),
                         boundary_stdout + "\n" + boundary_stderr)
        failures = (
            result + "FAIL: mismatch\n" + passed,
            result + "ERROR: simulation diagnostic\n" + passed,
            result + "FATAL: simulation diagnostic\n" + passed,
            _combine_process_streams(boundary_stdout, boundary_stderr),
            "PASS S2A-T12 runtime protocol integration\n" + result,
            result,
            passed + "PASS S2A-T12 runtime protocol integration\n",
        )
        for log in failures:
            with self.subTest(log=log[-60:]):
                with self.assertRaises(AssertionError):
                    _parse_xsim_summary(log)

    def test_runtime_protocol_integration(self) -> None:
        """在系统 TEMP 中编译、仿真并写入字节稳定的绑定证据。"""
        manifest, manifest_raw, ranges = _load_manifest()
        if not _SPEC.is_file():
            self.fail("G0 冻结文档不存在")
        spec_raw = _SPEC.read_bytes()
        self.assertFalse(spec_raw.startswith(b"\xef\xbb\xbf"), "G0 文档含 BOM")
        source_raw: dict[str, bytes] = {}
        for name, path in _SOURCES.items():
            self.assertTrue(path.is_file(), f"T12 源文件缺失：{path}")
            raw = path.read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), f"{name} 含 BOM")
            self.assertNotIn(bytes((13, 10)), raw, f"{name} 含 CRLF")
            raw.decode("utf-8")
            source_raw[name] = raw
        source_hashes_before = {name: _sha256_bytes(raw)
                                for name, raw in source_raw.items()}

        tools = {name: _XILINX_BIN / f"{name}.bat"
                 for name in ("xvlog", "xelab", "xsim")}
        for tool in tools.values():
            self.assertTrue(tool.is_file(), f"Vivado tool missing: {tool}")

        with tempfile.TemporaryDirectory(prefix="s2a_t12_runtime_") as temp_name:
            work = Path(temp_name).resolve(strict=True)
            temp_root = Path(tempfile.gettempdir()).resolve(strict=True)
            self.assertTrue(_is_under(work, temp_root))
            self.assertFalse(_is_under(work, _ROOT.resolve(strict=True)))
            for name, raw in source_raw.items():
                (work / name).write_bytes(raw)
            generated = _materialize_inputs(manifest, ranges, work)
            phases: list[dict[str, int | str]] = []
            logs: dict[str, str] = {}
            commands = [
                ("xvlog", ["-sv", *_SOURCES.keys()]),
                ("xelab", ["tb_s2a_runtime_protocol", "-s",
                           "s2a_runtime_protocol_snapshot"]),
                ("xsim", ["s2a_runtime_protocol_snapshot", "-R"]),
            ]
            deadline = time.monotonic() + 600.0
            for phase, args in commands:
                exit_code, log = _run_phase(tools[phase], args, work, phase,
                                            _ROOT, deadline)
                phases.append({"phase": phase, "exit_code": exit_code})
                logs[phase] = log
                self.assertEqual(exit_code, 0,
                                 f"{phase} exit={exit_code}; log tail:\n{log[-5000:]}")
            try:
                summary = _parse_xsim_summary(logs["xsim"])
            except AssertionError as exc:
                self.fail(f"xsim fail-closed 日志验收失败：{exc}；日志末尾：\n{logs['xsim'][-8000:]}")
            for phase_log in logs.values():
                self.assertNotRegex(phase_log, r"(?im)^\s*(?:ERROR|FATAL)\s*:")
                self.assertNotIn("FAIL:", phase_log.upper())

        source_hashes_after = {name: _sha256_file(path)
                               for name, path in _SOURCES.items()}
        self.assertEqual(source_hashes_before, source_hashes_after,
                         "Vivado 运行期间源码发生变化")
        self.assertEqual(_sha256_file(_MANIFEST), _MANIFEST_SHA256,
                         "Vivado 运行期间 G0 manifest 发生变化")

        evidence = {
            "schema_version": "gestureforge_s2a_t12_runtime_protocol_simulation_v1",
            "task": "S2A-T12",
            "result": "PASS",
            "baseline_head": _BASELINE_HEAD,
            "scope": "T11 CSR/control + T12 单 outstanding memory master + T10 行为 memory model 集成",
            "bindings": {
                "manifest_path": "report/evidence/S2A-T01/tiny416_model_manifest.json",
                "manifest_sha256": _sha256_bytes(manifest_raw),
                "g0_spec_path": "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md",
                "g0_spec_sha256": _sha256_bytes(spec_raw),
                "control_rtl_sha256": source_hashes_after["s2a_control_csr.sv"],
                "memory_model_sha256": source_hashes_after["s2a_memory_model.sv"],
                "memory_master_sha256": source_hashes_after["s2a_memory_master.sv"],
                "runtime_shell_sha256": source_hashes_after["s2a_runtime_shell.sv"],
                "testbench_sha256": source_hashes_after["tb_s2a_runtime_protocol.sv"],
                "runner_sha256": _sha256_file(_RUNNER),
                "manifest_ranges_sha256": generated["ranges_sha256"],
                "runtime_params_sha256": generated["params_sha256"],
                "vector_file_sha256": generated["vector_sha256"],
                "stimulus_sha256": generated["stimulus_sha256"],
                "golden_response_sha256": generated["golden_sha256"],
                "stall_schedule_sha256": generated["stall_plan_sha256"],
            },
            "randomness": {
                "seed": generated["seed"],
                "prng": "xorshift32",
                "draw_order": "按 read_input/read_weights/read_feature/write_feature 分组；每笔先选 word，再产生 write data",
                "state_after_generation": f"0x{generated['state_after_generation']:08X}",
                "transfer_counts": generated["counts"],
                "stall_schedule_by_class": {name: _STALL_SCHEDULE for name in _CLASS_NAMES},
            },
            "coverage": {
                **summary,
                "memory_fault_mapping": {"code_1": 1, "code_2": 2,
                                         "code_6": 6, "code_7": 6},
                "memory_fault_directed_cases": 2,
                "bad_argument_zero_strobe_cases": 1,
                "bad_range_unaligned_cases": 1,
                "cancelled_pending_feature_write_cases": [
                    "hard_reset_before_ready_after_7_low_cycles",
                    "accepted_soft_reset_before_ready_after_7_low_cycles",
                    "timeout_before_ready_after_7_low_cycles",
                ],
                "post_cancel_readback_no_side_effect_cases": 3,
                "retry_same_write_feature_stall_slot_7_cases": 3,
                "accepted_write_feature_transfer_counts_include_retries": True,
                "backend_one_outstanding_stability_assertion": True,
                "operator_code0_completion_required_for_done_and_head_valid": True,
            },
            "objects": {
                "input": {"start_inclusive": 0, "end_exclusive": 519168,
                          "access": "read_only"},
                "weights": {"start_inclusive": 1048576, "end_exclusive": 6951676,
                            "external_weight_package_read": False, "access": "read_only"},
                "feature_unique_range_count": len(ranges),
                "feature_unique_ranges": [
                    {"start_inclusive": start, "end_exclusive": end}
                    for start, end in ranges
                ],
                "feature_cancel_test_addresses": generated["feature_cancel_test_addresses"],
                "feature_address_source": "manifest 非 YOLO tensor_address/tensor_length_bytes 去重",
            },
            "vivado": {
                "phases": phases,
                "xsim_pass_marker_count": summary["pass_marker_count"],
                "xsim_failure_diagnostic_count": 0,
                "log_gate_negative_cases": 7,
            },
            "limitations": [
                "只验证 T12 runtime shell、T11 控制与 T10 行为模型的仿真集成。",
                "backend request/response 是 T12 内部测试接口；没有实现真实算子或 PL DMA。",
                "未连接整网计算、PS 解码/NMS，未执行综合、资源估算、时序分析或实物验证。",
                "外部权重包未读取；权重区使用 T10 确定性 byte pattern。",
                "取消用例证明未握手 pending feature write 无模型副作用，不替代器件/真实 memory controller 集成。",
            ],
        }
        payload = (json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True)
                   + "\n").encode("utf-8")
        self.assertFalse(payload.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(bytes((13, 10)), payload)
        _EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        _EVIDENCE.write_bytes(payload)
        parsed = json.loads(_EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(parsed["bindings"]["runner_sha256"], _sha256_file(_RUNNER))
        self.assertEqual(parsed["vivado"]["phases"], [
            {"phase": "xvlog", "exit_code": 0},
            {"phase": "xelab", "exit_code": 0},
            {"phase": "xsim", "exit_code": 0},
        ])


if __name__ == "__main__":
    unittest.main()
