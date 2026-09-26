"""验证 layer36 固定空间 INT8 tile16 试验数据通路。"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any


_ROOT = Path(__file__).resolve().parents[1]
_BASELINE_HEAD = "7277b1a2afcc26ecd9febdd2d39255a48f5c4526"
_VIVADO_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")
_RANDOM_SEED = 20260926
_RANDOM_TILE_COUNT = 1000
_DATASET_TILE_COUNT = _RANDOM_TILE_COUNT + 2
_K = 256
_LANES = 16
_PIXELS_PER_ROW = 26 * 26
_MANIFEST_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
_G0_SPEC_SHA256 = "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230"
_T20_RUNNER_SHA256 = "9474108ee39ed1d89113241ebaef1ac177a0d0cca6878dbfc1415f25543117c2"
_T20_EVIDENCE_SHA256 = "d6bc16966a2d3c7707d98aafa6b435ae158cd28faa53baa8f795e13e86a17887"
_T20_LAYER_GOLDEN_SHA256 = "80462a11ba6e9e0f3ba2bfbf5c25e6c6db24bf884dd93d0c00d79b348f5a6bda"
_T20_INPUT_SHA256 = "3ab3cb8aba6e67fe3ffa6b9b071c706a905563b125d4f500b814fa9d0092572b"
_CHANNEL0_WEIGHT_SHA256 = "62b6b53c4f05027806a42e441e6de0a5d123fed4ff4dd4aff3299748772228d9"
_EXPECTED_T20_TILE_RAW = [
    -10746, -16049, -9216, -9143, 1061, 7628, 6667, -2638,
    11431, 18938, 15421, 16784, 19425, 31828, 31123, 28294,
]
_EXPECTED_T20_TILE_INT8 = [-6, -8, -5, -5, 1, 4, 4, -1, 6, 10, 8, 9, 10, 17, 16, 15]


class T30Error(RuntimeError):
    """报告冻结输入、仿真或综合失败。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise T30Error(message)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise T30Error(f"不能导入冻结 helper：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _signed_byte(value: int) -> int:
    value &= 0xFF
    return value if value < 128 else value - 256


def _checked_tile_accumulators(rows: list[tuple[int, list[int]]], bias: int) -> list[int]:
    accumulators = [bias] * _LANES
    for reduction_index, (weight, features) in enumerate(rows):
        if len(features) != _LANES or not -127 <= weight <= 127:
            raise T30Error(f"tile 输入布局或共享权重越界：k={reduction_index}")
        for lane, activation in enumerate(features):
            if not -127 <= activation <= 127:
                raise T30Error(f"tile activation 越界：k={reduction_index} lane={lane}")
            accumulators[lane] += activation * weight
            if not -(1 << 31) <= accumulators[lane] <= (1 << 31) - 1:
                raise T30Error(f"Python oracle 检出 INT32 溢出：k={reduction_index} lane={lane}")
    if len(rows) != _K:
        raise T30Error(f"tile reduction 长度错误：{len(rows)}")
    return accumulators


def _resource_value(report: str, labels: tuple[str, ...]) -> int:
    for label in labels:
        match = re.search(
            rf"^\s*(?:\|\s*)?{re.escape(label)}\s*\|\s*([0-9,]+)\s*\|",
            report,
            re.MULTILINE | re.IGNORECASE,
        )
        if match:
            return int(match.group(1).replace(",", ""))
    raise T30Error(f"Vivado utilization report 缺少资源字段：{labels}")


def _run_tool(name: str, tool: Path, arguments: list[str], work: Path,
              timeout_seconds: float = 600.0) -> dict[str, Any]:
    if not tool.is_file():
        raise T30Error(f"未找到 Vivado 工具：{tool}")
    command = " ".join(
        f'"{argument}"' if " " in argument else argument
        for argument in [str(tool), *arguments]
    )
    started = time.monotonic()
    try:
        process = subprocess.run(
            f'cmd.exe /d /s /c "{command}"',
            cwd=work,
            shell=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + (exc.stderr or "")
        log_path = work / f"{name}.stdout.log"
        log_path.write_text(output, encoding="utf-8", newline="\n")
        raise T30Error(f"{name} 超时；日志：{log_path}") from exc
    elapsed = time.monotonic() - started
    output = process.stdout + process.stderr
    log_path = work / f"{name}.stdout.log"
    log_path.write_text(output, encoding="utf-8", newline="\n")
    return {
        "name": name,
        "command": [str(tool), *arguments],
        "exit_code": process.returncode,
        "elapsed_seconds": round(elapsed, 3),
        "stdout_log_path": str(log_path),
        "stdout_log_sha256": _sha256_file(log_path),
        "output": output,
    }


class S2ASpatialTile16Tests(unittest.TestCase):
    """将 T20 固定输入、独立整数 oracle 和 tile16 RTL 联合验证。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = _ROOT
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=cls.root, check=True,
            capture_output=True, text=True, encoding="utf-8",
        ).stdout.strip()
        _require(head == _BASELINE_HEAD,
                 f"基线 HEAD 不符：expected={_BASELINE_HEAD} actual={head}")
        cls.head_start = head
        cls.rtl_path = cls.root / "src/s2a_conv_spatial_tile16.sv"
        cls.tb_path = cls.root / "sim/tb_s2a_conv_spatial_tile16.sv"
        cls.evidence_path = cls.root / "report/evidence/S2A-T30/spatial_tile16_pilot.json"
        _require(cls.rtl_path.is_file() and cls.tb_path.is_file(), "T30 RTL 或 testbench 缺失")
        _require(cls.evidence_path.parent.is_dir(), "T30 evidence 目录缺失")

        cls.t20_path = cls.root / "verification/test_s2a_conv_layer_scheduler_rtl.py"
        cls.t20 = _load_module("s2a_t30_t20_helpers", cls.t20_path)
        _require(_sha256_file(cls.t20_path) == _T20_RUNNER_SHA256,
                 "T20 纯 helper 源码 SHA-256 与冻结值不符")
        cls.t17 = cls.t20._load_t17_runner()
        _require(_sha256_file(cls.root / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md")
                 == _G0_SPEC_SHA256, "G0 冻结规格 SHA-256 与 T20 绑定不符")
        _require(_sha256_file(cls.t20._EVIDENCE) == _T20_EVIDENCE_SHA256,
                 "T20 layer36 证据 SHA-256 与冻结值不符")

        cls.manifest, cls.t16_proof, cls.weights_by_layer, cls.package_path = (
            cls.t17._load_bound_inputs()
        )
        cls.layers = {int(row["layer_index"]): row for row in cls.manifest["layers"]}
        cls.layer = cls.layers[36]
        source_layer = cls.layers[35]
        proof_layers = {int(row["layer_index"]): row for row in cls.t16_proof["layers"]}
        cls.parameters = cls.t17._candidate_parameters(cls.layer, proof_layers[36])
        _require(
            cls.layer["op"] == "convolutional" and
            cls.layer["cfg_section"] == 37 and
            cls.layer["input_shape_nchw"] == [1, 256, 26, 26] and
            cls.layer["output_shape_nchw"] == [1, 30, 26, 26] and
            cls.layer["kernel_hw"] == [1, 1] and
            cls.layer["activation"] == "linear" and
            cls.layer["layout"] == "NCHW" and
            cls.layer["input_scale"] == 0.12693486251230315 and
            cls.layer["output_scale"] == 0.30223452951025775,
            "T01 layer36 几何、layout 或 scale 与冻结规格不符",
        )
        _require(
            source_layer["output_shape_nchw"] == [1, 256, 26, 26] and
            source_layer["tensor_length_bytes"] == 173056 and
            source_layer["output_scale"] == cls.layer["input_scale"],
            "T01 layer35 到 layer36 输入绑定不符",
        )
        cls.layer_weights = cls.weights_by_layer[36]
        _require(len(cls.layer_weights) == 7680, "layer36 权重切片长度不符")
        cls.channel0_weights = cls.layer_weights[:_K]
        _require(_sha256_bytes(cls.channel0_weights) == _CHANNEL0_WEIGHT_SHA256,
                 "layer36 通道0 K=256 权重字节 SHA-256 不符")
        cls.bias = int(cls.layer["bias_accumulator_int32_per_output_channel"][0])
        cls.weight_scale = float(cls.layer["weight_scale_per_output_channel"][0])
        _require(cls.bias == -40 and cls.weight_scale == 0.0012533131521195173,
                 "layer36 通道0 冻结 bias 或 scale 不符")

        cls.t20_evidence = json.loads(cls.t20._EVIDENCE.read_text(encoding="utf-8"))
        cls.input_bytes, cls.sentinel_offsets = cls.t20._input_fixture()
        cls.golden_input, cls.full_golden, cls.golden_summary = cls.t20._input_and_golden(
            cls.layer, cls.layer_weights, cls.parameters, cls.t17
        )
        _require(cls.input_bytes == cls.golden_input, "T20 fixture helper 输入重放不一致")
        _require(len(cls.input_bytes) == 173056, "T20 layer36 输入 fixture 长度不符")
        _require(len(cls.full_golden) == 20280, "T20 layer36 CPU golden 输出长度不符")
        _require(_sha256_bytes(cls.input_bytes) == _T20_INPUT_SHA256,
                 "T20 地址生成输入 fixture SHA-256 不符")
        _require(_sha256_bytes(cls.full_golden) == _T20_LAYER_GOLDEN_SHA256,
                 "T20 layer36 full CPU golden SHA-256 不符")
        _require(len(cls.sentinel_offsets) == 675, "T20 T10 地址公式 sentinel 数量不符")
        _require(cls.t20_evidence["golden"]["expected_output_sha256"] == _T20_LAYER_GOLDEN_SHA256,
                 "T20 evidence 的 CPU golden SHA-256 与 helper 输出不一致")

        cls.real_rows = []
        for k in range(_K):
            features = [
                cls.t17._signed_byte(cls.input_bytes[k * _PIXELS_PER_ROW + lane])
                for lane in range(_LANES)
            ]
            cls.real_rows.append((cls.t17._signed_byte(cls.channel0_weights[k]), features))
        cls.real_raw = _checked_tile_accumulators(cls.real_rows, cls.bias)
        cls.real_quantized = [_signed_byte(value) for value in cls.full_golden[:_LANES]]
        _require(cls.real_raw == _EXPECTED_T20_TILE_RAW,
                 "T20 真实输入 tile raw accumulator 与核验值不符")
        _require(cls.real_quantized == _EXPECTED_T20_TILE_INT8,
                 "T20 CPU golden 通道0像素0..15 输出与核验值不符")
        _require(
            [cls.t17._fixed_point_quantize(value, cls.parameters[0]) for value in cls.real_raw]
            == cls.real_quantized,
            "T16 fixed-point 输出与 T20 CPU golden tile 不一致",
        )
        print(
            "T30_PREFLIGHT_PASS head={} layer=36 cfg=37 K=256 lanes=16 "
            "fixture_sha256={} golden_sha256={} t20_helper_sha256={}".format(
                cls.head_start, _sha256_bytes(cls.input_bytes),
                _sha256_bytes(cls.full_golden), _sha256_file(cls.t20_path),
            ),
            flush=True,
        )

    def test_frozen_t20_tile_binding_and_cpu_golden(self) -> None:
        self.assertEqual(self.layer["input_shape_nchw"], [1, 256, 26, 26])
        self.assertEqual(self.layer["output_shape_nchw"], [1, 30, 26, 26])
        self.assertEqual(self.bias, -40)
        self.assertEqual(len(self.real_rows), 256)
        self.assertEqual(len(self.real_raw), 16)
        self.assertEqual(self.real_quantized, _EXPECTED_T20_TILE_INT8)
        self.assertEqual(self.golden_summary["d2_float_cross_checks"], 20280)

    def test_vivado_simulation_and_module_only_synthesis(self) -> None:
        selected_work = os.environ.get("S2A_T30_WORK_DIR")
        if selected_work:
            work = Path(selected_work).resolve()
            self.assertFalse(work.exists(), f"拒绝复用已有 TEMP 工作目录：{work}")
            work.mkdir(parents=True)
        else:
            temp_root = Path(os.environ.get("TEMP", tempfile.gettempdir()))
            work = Path(tempfile.mkdtemp(prefix="s2a_t30_tile16_", dir=temp_root))
        progress_path = work / "progress.log"
        phases: list[dict[str, Any]] = []

        def progress(message: str) -> None:
            with progress_path.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(message + "\n")
            print(message, flush=True)

        def source_hashes() -> dict[str, str]:
            paths = {
                "g0_spec": self.t20._G0_SPEC,
                "t01_manifest": self.t17._MANIFEST,
                "d2_int8_forward": self.root / "verification/s1_t02_d2_int8_forward.py",
                "t16_proof": self.t17._T16_PROOF,
                "t16_proof_script": self.t17._T16_SCRIPT,
                "t17_loader_runner": self.root / "verification/test_s2a_conv_engine_rtl.py",
                "t20_helper_runner": self.t20_path,
                "t20_evidence": self.t20._EVIDENCE,
                "rtl": self.rtl_path,
                "testbench": self.tb_path,
                "test_runner": Path(__file__).resolve(),
                "gfint8w1_package": self.package_path,
            }
            return {name: _sha256_file(path) for name, path in paths.items()}

        head_before = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.root, check=True,
            capture_output=True, text=True, encoding="utf-8",
        ).stdout.strip()
        self.assertEqual(head_before, self.head_start)
        source_hashes_before = source_hashes()
        progress(f"PREFLIGHT_PASS work={work} head={head_before}")

        vector_path = work / "vectors.dat"
        vectors = self._write_vectors(vector_path, progress)
        progress(
            "VECTORS_READY tiles={} random={} directed=1 t20=1 bytes={} sha256={}".format(
                vectors["tile_count"], vectors["random_tile_count"],
                vectors["file_bytes"], vectors["file_sha256"],
            )
        )

        xvlog = _VIVADO_BIN / "xvlog.bat"
        xelab = _VIVADO_BIN / "xelab.bat"
        xsim = _VIVADO_BIN / "xsim.bat"
        phases_spec = [
            ("xvlog", xvlog, ["-sv", str(self.rtl_path), str(self.tb_path)]),
            ("xelab", xelab, ["-top", "tb_s2a_conv_spatial_tile16",
                              "-snapshot", "s2a_t30_tile16_snapshot"]),
            ("xsim", xsim, ["-R", "s2a_t30_tile16_snapshot"]),
        ]
        sim_output = ""
        for name, tool, arguments in phases_spec:
            progress(f"PHASE_START {name} work={work}")
            phase = _run_tool(name, tool, arguments, work)
            phases.append(phase)
            self.assertEqual(
                phase["exit_code"], 0,
                f"{name} 退出码 {phase['exit_code']}；日志尾部：\n{phase['output'][-6000:]}",
            )
            if name == "xsim":
                sim_output = phase["output"]
                self.assertNotIn("FAIL:", sim_output,
                                 "xsim 日志包含 testbench 失败标记")
            progress(
                "PHASE_PASS {} exit_code={} elapsed_seconds={}".format(
                    name, phase["exit_code"], phase["elapsed_seconds"],
                )
            )

        summary_match = re.search(r"PASS: dataset_tiles=.*", sim_output)
        self.assertIsNotNone(summary_match, "xsim 缺少 tile16 PASS summary")
        summary = {
            key: int(value)
            for key, value in re.findall(r"([a-z0-9_]+)=([0-9]+)", summary_match.group(0))
        }
        expected_summary = {
            "dataset_tiles": 1002,
            "t20_tiles": 1,
            "directed_tiles": 1,
            "random_tiles": 1000,
            "accepted_k_beats_per_tile": 256,
            "dataset_k_beats": 1002 * 256,
            "recovery_tiles": 8,
            "recovery_k_beats": 8 * 256,
            "bad_activation_beats": 1,
            "bad_weight_beats": 1,
            "overflow_beats": 2,
            "abort_accepted_beats": 5,
            "reset_accepted_beats": 5,
            "error_remaining_unissued_k": 1020,
            "abort_remaining_unissued_k": 251,
            "reset_remaining_unissued_k": 251,
            "invalid_start_transactions": 2,
            "invalid_start_unissued_k": 512,
            "protocol_scenarios": 8,
            "errors": 0,
        }
        self.assertEqual(summary, expected_summary, "xsim 握手/覆盖 summary 不符")
        self.assertIn("errors=0", summary_match.group(0))

        tcl_path = work / "synth_tile16.tcl"
        utilization_path = work / "utilization.rpt"
        timing_path = work / "timing_summary.rpt"
        rtl_tcl_path = self.rtl_path.as_posix()
        util_tcl_path = utilization_path.as_posix()
        timing_tcl_path = timing_path.as_posix()
        tcl_text = (
            f"read_verilog -sv {{{rtl_tcl_path}}}\n"
            "synth_design -top s2a_conv_spatial_tile16 -part xc7z020clg400-1\n"
            f"report_utilization -file {{{util_tcl_path}}}\n"
            f"report_timing_summary -file {{{timing_tcl_path}}}\n"
            "puts \"S2A_T30_SYNTH_PASS\"\n"
            "exit\n"
        )
        tcl_path.write_text(tcl_text, encoding="utf-8", newline="\n")
        vivado = _VIVADO_BIN / "vivado.bat"
        synth_arguments = [
            "-mode", "batch", "-source", str(tcl_path),
            "-log", str(work / "vivado_native.log"),
            "-journal", str(work / "vivado_native.jou"),
        ]
        progress(f"PHASE_START standalone_synthesis tool={vivado} tcl={tcl_path}")
        synthesis = _run_tool("synthesis", vivado, synth_arguments, work)
        phases.append(synthesis)
        self.assertEqual(
            synthesis["exit_code"], 0,
            f"Vivado standalone synthesis 退出码 {synthesis['exit_code']}；日志尾部：\n"
            f"{synthesis['output'][-6000:]}",
        )
        self.assertIn("S2A_T30_SYNTH_PASS", synthesis["output"])
        self.assertTrue(utilization_path.is_file(), "Vivado utilization report 缺失")
        utilization_text = utilization_path.read_text(encoding="utf-8", errors="replace")
        resources = {
            "lut": _resource_value(utilization_text, ("Slice LUTs*", "Slice LUTs", "CLB LUTs")),
            "ff": _resource_value(utilization_text, ("Slice Registers", "CLB Registers")),
            "bram_tile": _resource_value(utilization_text, ("Block RAM Tile",)),
            "dsp": _resource_value(utilization_text, ("DSPs",)),
        }
        timing_text = (
            timing_path.read_text(encoding="utf-8", errors="replace")
            if timing_path.is_file() else ""
        )
        progress(
            "PHASE_PASS standalone_synthesis exit_code=0 resources={} timing_report={}".format(
                resources, timing_path.is_file(),
            )
        )

        head_after = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.root, check=True,
            capture_output=True, text=True, encoding="utf-8",
        ).stdout.strip()
        self.assertEqual(head_after, head_before, "仿真/综合期间 HEAD 发生变化")
        source_hashes_after = source_hashes()
        self.assertEqual(source_hashes_after, source_hashes_before,
                         "验证期间源码或冻结输入发生变化")

        evidence = {
            "schema_version": 1,
            "task": "S2A-T30",
            "result": "PASS",
            "scope": "layer36 channel0 的16-lane spatial MAC datapath pilot",
            "baseline_git_head": _BASELINE_HEAD,
            "runtime_git_head_start": head_before,
            "runtime_git_head_end": head_after,
            "source_bindings_sha256": source_hashes_after,
            "frozen_layer36": {
                "model": "tiny416",
                "layer_index": 36,
                "cfg_section": 37,
                "input_shape_nchw": [1, 256, 26, 26],
                "output_shape_nchw": [1, 30, 26, 26],
                "kernel_hw": [1, 1],
                "activation": "linear",
                "layout": "NCHW",
                "reduction_k": 256,
                "tile": {
                    "output_channel": 0,
                    "row": 0,
                    "pixel_indices": list(range(16)),
                    "input_byte_mapping": "input_bytes[k*676+lane]",
                    "weight_byte_mapping": "package_weights[36][0*256+k]",
                    "shared_weight_broadcast_lanes": 16,
                },
                "input_scale": float(self.layer["input_scale"]),
                "output_scale": float(self.layer["output_scale"]),
                "channel0_weight_scale": self.weight_scale,
                "channel0_bias_int32": self.bias,
                "channel0_weight_bytes": _K,
                "channel0_weight_sha256": _sha256_bytes(self.channel0_weights),
                "integer_accumulation": "逐 lane 按 k=0..255 有序累加；每步检查 signed INT32；不回绕、不饱和",
            },
            "t20_cpu_reference": {
                "fixture_helper": "verification/test_s2a_conv_layer_scheduler_rtl.py::_input_fixture",
                "golden_helper": "verification/test_s2a_conv_layer_scheduler_rtl.py::_input_and_golden",
                "input_generator": "T10 地址 XOR byte pattern；raw 0x80 sentinel 按 T20 helper 置零",
                "input_bytes": len(self.input_bytes),
                "input_sha256": _sha256_bytes(self.input_bytes),
                "patched_minus128_sentinel_count": len(self.sentinel_offsets),
                "full_layer_output_bytes": len(self.full_golden),
                "full_layer_golden_sha256": _sha256_bytes(self.full_golden),
                "full_layer_accumulator_range": {
                    "min": int(self.golden_summary["int32_accumulator_min"]),
                    "max": int(self.golden_summary["int32_accumulator_max"]),
                },
                "d2_float_cross_checks": int(self.golden_summary["d2_float_cross_checks"]),
                "tile_raw_accumulators_int32": self.real_raw,
                "tile_quantized_bytes_signed": self.real_quantized,
                "tile_matches_t20_layer_golden": True,
            },
            "stimulus": vectors,
            "python_oracle": {
                "implementation": "独立 Python 整数逐步累加；每个 lane/k 检查 INT32 范围",
                "random_seed": _RANDOM_SEED,
                "random_valid_tiles": _RANDOM_TILE_COUNT,
                "random_lane_results_compared": _RANDOM_TILE_COUNT * _LANES,
                "random_tile_k_values": _K,
                "activation_and_weight_valid_range": [-127, 127],
                "random_raw_output_sha256": vectors["random_raw_output_sha256"],
                "directed_value_coverage": [-127, 0, 127],
            },
            "simulation": {
                "simulator": "Vivado xvlog/xelab/xsim v2026.1",
                "commands": [phase["command"] for phase in phases[:3]],
                "phases": [
                    {key: value for key, value in phase.items() if key != "output"}
                    for phase in phases[:3]
                ],
                "testbench_summary": summary,
                "successful_tile_k_handshakes": 1002 * 256,
                "accepted_k_beats_per_successful_tile": 256,
                "result_stall_cycles": 3,
                "protocol_coverage": {
                    "wrong_k_bad_argument": [255, 257],
                    "activation_minus128_bad_argument_beats": 1,
                    "weight_minus128_bad_argument_beats": 1,
                    "positive_int32_overflow_beats": 1,
                    "negative_int32_overflow_beats": 1,
                    "abort_accepted_beats_before_cancel": 5,
                    "reset_accepted_beats_before_cancel": 5,
                    "abort_unissued_k_remainder": 251,
                    "reset_unissued_k_remainder": 251,
                    "invalid_start_transactions_without_input": 2,
                    "invalid_start_unissued_k": 512,
                    "error_transactions_accepted_beats": 4,
                    "error_transactions_unissued_k_remainder": 1020,
                    "recovery_tiles_passed": 8,
                    "late_response_after_abort_or_reset": False,
                },
            },
            "standalone_synthesis": {
                "tool": "Vivado v2026.1",
                "top": "s2a_conv_spatial_tile16",
                "part": "xc7z020clg400-1",
                "opened_project_xpr": False,
                "included_other_rtl_modules": False,
                "phase_exit_code": synthesis["exit_code"],
                "phase_elapsed_seconds": synthesis["elapsed_seconds"],
                "tcl_path": str(tcl_path),
                "stdout_log_path": synthesis["stdout_log_path"],
                "stdout_log_sha256": synthesis["stdout_log_sha256"],
                "utilization_report_path": str(utilization_path),
                "utilization_report_sha256": _sha256_file(utilization_path),
                "module_only_utilization": resources,
                "timing_summary_path": str(timing_path),
                "timing_summary_sha256": _sha256_file(timing_path) if timing_path.is_file() else None,
                "timing_constraints_applied": False,
                "timing_risk": "独立综合未加入 XDC 或时钟周期约束；不报告目标时钟或系统时序结论。",
            },
            "limitations": [
                "仅为16路空间 MAC 数据通路 pilot，不是完整 layer36 卷积实现或系统联调。",
                "不含片上 tile buffer 加载、外部内存寻址/总线、requant RTL、PS 接口或系统调度。",
                "CPU T20 helper 生成地址公式输入和完整 layer golden；本测试只逐值核对 channel0 row0 的16个 raw INT32 累加及对应量化字节。",
                "未读取 T25 shard 或原图；未训练模型；未连接板卡、未烧录；未进入 2B 或阶段3。",
                "资源数字只对应本模块独立综合，不代表完整卷积层或全系统资源。",
            ],
        }
        _require(not self.evidence_path.exists(),
                 f"T30 evidence 目标已存在，拒绝覆盖：{self.evidence_path}")
        self.evidence_path.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        progress(
            "EVIDENCE_WRITTEN path={} sha256={}".format(
                self.evidence_path, _sha256_file(self.evidence_path),
            )
        )
        print(
            "S2A_T30_PASS evidence={} evidence_sha256={} work={} resources={}".format(
                self.evidence_path, _sha256_file(self.evidence_path), work, resources,
            ),
            flush=True,
        )

    def _write_vectors(self, destination: Path, progress) -> dict[str, Any]:
        vector_digest = hashlib.sha256()
        random_digest = hashlib.sha256()
        raw_digest = hashlib.sha256()
        random_min = 127
        random_max = -127
        random_value_set: set[int] = set()
        total_bytes = 0

        def emit_tile(stream, tile_id: int, bias: int,
                      rows: list[tuple[int, list[int]]], random_tile: bool) -> list[int]:
            nonlocal total_bytes, random_min, random_max
            outputs = _checked_tile_accumulators(rows, bias)
            header = "{} {} 0 {}\n".format(
                tile_id, bias, " ".join(str(value) for value in outputs),
            ).encode("ascii")
            body = bytearray()
            for weight, features in rows:
                body.extend((str(weight) + " " + " ".join(map(str, features)) + "\n").encode("ascii"))
                if random_tile:
                    random_value_set.add(weight)
                    random_min = min(random_min, weight)
                    random_max = max(random_max, weight)
                    for value in features:
                        random_value_set.add(value)
                        random_min = min(random_min, value)
                        random_max = max(random_max, value)
            stream.write(header)
            stream.write(body)
            vector_digest.update(header)
            vector_digest.update(body)
            total_bytes += len(header) + len(body)
            if random_tile:
                random_digest.update(body)
                raw_digest.update(
                    (str(tile_id) + " " + str(bias) + " " +
                     " ".join(str(value) for value in outputs) + "\n").encode("ascii")
                )
            return outputs

        directed_rows = []
        for k in range(_K):
            weight = -127 if k == 0 else (0 if k == 1 else (127 if k == 2 else 0))
            features = [0] * _LANES
            if k == 0:
                features[0:3] = [-127, 0, 127]
            elif k == 1:
                features = [-127, 0, 127, -127, 0, 127, -127, 0,
                            127, -127, 0, 127, -127, 0, 127, -127]
            elif k == 2:
                features[3] = 127
                features[4] = -127
            directed_rows.append((weight, features))
        directed_outputs = _checked_tile_accumulators(directed_rows, 17)
        _require(directed_outputs[:5] == [16146, 17, -16112, 16146, -16112],
                 "定向 -127/0/127 向量手算结果不符")

        rng = self.t17._XorShift32(_RANDOM_SEED)
        start_state = rng.state
        with destination.open("wb") as stream:
            emit_tile(stream, 0, self.bias, self.real_rows, False)
            emit_tile(stream, 1, 17, directed_rows, False)
            for random_index in range(_RANDOM_TILE_COUNT):
                bias = rng.selector(200001) - 100000
                rows: list[tuple[int, list[int]]] = []
                accumulators = [bias] * _LANES
                for k in range(_K):
                    weight = rng.int8()
                    features = [rng.int8() for _ in range(_LANES)]
                    for lane, activation in enumerate(features):
                        accumulators[lane] += activation * weight
                        if not -(1 << 31) <= accumulators[lane] <= (1 << 31) - 1:
                            raise T30Error(
                                f"随机 Python oracle INT32 overflow tile={random_index} k={k} lane={lane}"
                            )
                    rows.append((weight, features))
                expected_tile = emit_tile(
                    stream, random_index + 2, bias, rows, True,
                )
                if expected_tile != accumulators:
                    raise T30Error(f"随机 oracle 对同一 tile 的逐步结果不一致：{random_index}")
                if (random_index + 1) % 100 == 0:
                    progress(f"VECTOR_PROGRESS random_tiles={random_index + 1}/{_RANDOM_TILE_COUNT}")
        self.assertTrue({-127, 0, 127}.issubset(random_value_set),
                        "固定 seed 随机向量未覆盖 -127/0/127")
        self.assertEqual(random_min, -127)
        self.assertEqual(random_max, 127)
        return {
            "file_path": str(destination),
            "file_bytes": total_bytes,
            "file_sha256": _sha256_file(destination),
            "format": "每 tile 为 case_id/bias/error/16个raw结果头部，随后256行 shared_weight+16个signed activation",
            "tile_count": _DATASET_TILE_COUNT,
            "t20_real_tile_count": 1,
            "directed_boundary_tile_count": 1,
            "random_tile_count": _RANDOM_TILE_COUNT,
            "random_seed": _RANDOM_SEED,
            "xorshift32_state_start": start_state,
            "xorshift32_state_end": rng.state,
            "xorshift32_draws": rng.draws,
            "random_value_min": random_min,
            "random_value_max": random_max,
            "random_boundary_values_observed": sorted({-127, 0, 127} & random_value_set),
            "random_input_bytes_sha256": random_digest.hexdigest(),
            "random_raw_output_sha256": raw_digest.hexdigest(),
            "raw_lane_outputs_oracle_comparisons": _RANDOM_TILE_COUNT * _LANES,
            "t20_tile_raw_accumulators_int32": self.real_raw,
            "directed_tile_raw_accumulators_int32": directed_outputs,
        }


if __name__ == "__main__":
    unittest.main()
