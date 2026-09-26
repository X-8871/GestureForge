"""验证 layer36 通道0 row0 的 G0 字节 strobe feeder pilot。"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
import re
import subprocess
import tempfile
import time
import unittest
import uuid
from pathlib import Path
from typing import Any


_ROOT = Path(__file__).resolve().parents[1]
_BASELINE_HEAD = "7213179f5e65cf7d61240776a9cc8f1aaaacb7e1"
_VIVADO_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")
_G0_SHA256 = "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230"
_MANIFEST_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
_D2_SHA256 = "5dfdbb4a9e57256b362629a2de40b9724df6d28ae225ce6d6622429b9cbad393"
_T16_PROOF_SHA256 = "edd2e766278849136c806b755b275c6ad089964ff784ebe687032733f2ccbb24"
_T16_SCRIPT_SHA256 = "3bfb6d711160c21ae38147a181a042dcc5fee872d0688ae688f31e5909ebe8c9"
_T20_RUNNER_SHA256 = "9474108ee39ed1d89113241ebaef1ac177a0d0cca6878dbfc1415f25543117c2"
_T20_EVIDENCE_SHA256 = "d6bc16966a2d3c7707d98aafa6b435ae158cd28faa53baa8f795e13e86a17887"
_T20_INPUT_SHA256 = "3ab3cb8aba6e67fe3ffa6b9b071c706a905563b125d4f500b814fa9d0092572b"
_T20_GOLDEN_SHA256 = "80462a11ba6e9e0f3ba2bfbf5c25e6c6db24bf884dd93d0c00d79b348f5a6bda"
_T30_RTL_SHA256 = "42ad5217e7be65b8fa255a587bb27382b10da7b32ede2ce6f24b2e7787b97fdb"
_T30_RUNNER_SHA256 = "9b9345a9d8d36b2f7ac53fd8ce27a24da21675bd0f36c68300e0a5c55ced4f45"
_T30_EVIDENCE_SHA256 = "eba77ffd0a94524dfc3844207bbbe646b064066ba346ba4b344b3e3425c58443"
_CHANNEL0_WEIGHT_SHA256 = "62b6b53c4f05027806a42e441e6de0a5d123fed4ff4dd4aff3299748772228d9"
_INPUT_BYTES = 173056
_INPUT_CHANNEL_STRIDE = 676
_PIXELS_PER_ROW = 26
_K = 256
_BIAS = -40
_STALL_SEED = 0x20260927
_TOTAL_REQUESTS = 2304


class T31Error(RuntimeError):
    """报告冻结输入、仿真或综合失败。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise T31Error(message)


def _git_output(arguments: list[str], cwd: Path, input_text: str | None = None) -> str:
    result = subprocess.run(
        ["git", *arguments], cwd=cwd, input=input_text,
        capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        raise T31Error(
            f"git {' '.join(arguments)} 失败，exit={result.returncode}："
            f"{result.stderr.strip()}"
        )
    return result.stdout.strip()


def _read_git_head(cwd: Path) -> str:
    return _git_output(["rev-parse", "HEAD"], cwd)


def _is_ancestor(ancestor: str, descendant: str, cwd: Path) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    raise T31Error(
        "git merge-base --is-ancestor 执行失败，"
        f"exit={result.returncode}：{result.stderr.strip()}"
    )


def _require_baseline_ancestor(baseline: str, runtime_head: str, cwd: Path) -> None:
    _require(
        _is_ancestor(baseline, runtime_head, cwd),
        f"运行 HEAD 不属于冻结基线的后代：baseline={baseline} runtime={runtime_head}",
    )


def _require_stable_head(head_before: str, head_after: str) -> None:
    _require(
        head_before == head_after,
        f"验证期间 HEAD 发生变化：before={head_before} after={head_after}",
    )


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise T31Error(f"不能加载冻结 helper：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _signed_byte(value: int) -> int:
    value &= 0xFF
    return value if value < 128 else value - 256


def _raw_row0_oracle(input_bytes: bytes, channel0_weights: bytes) -> list[int]:
    """按像素列独立逐 K 累加，并在每一步检查 signed INT32。"""
    _require(len(input_bytes) == _INPUT_BYTES, "layer36 输入张量字节数不符")
    _require(len(channel0_weights) == _K, "通道0权重字节数不符")
    outputs: list[int] = []
    for x in range(_PIXELS_PER_ROW):
        accumulator = _BIAS
        for k in range(_K):
            activation = _signed_byte(input_bytes[k * _INPUT_CHANNEL_STRIDE + x])
            weight = _signed_byte(channel0_weights[k])
            _require(-127 <= activation <= 127 and -127 <= weight <= 127,
                     f"发现非法 INT8 -128：x={x} k={k}")
            accumulator += activation * weight
            _require(-(1 << 31) <= accumulator <= (1 << 31) - 1,
                     f"Python oracle 检出 INT32 溢出：x={x} k={k}")
        outputs.append(accumulator)
    return outputs


def _resource_value(report: str, labels: tuple[str, ...]) -> int:
    for label in labels:
        match = re.search(
            rf"^\s*(?:\|\s*)?{re.escape(label)}\s*\|\s*([0-9,]+)\s*\|",
            report,
            re.MULTILINE | re.IGNORECASE,
        )
        if match:
            return int(match.group(1).replace(",", ""))
    raise T31Error(f"Vivado utilization report 缺少资源字段：{labels}")


def _run_tool(name: str, tool: Path, arguments: list[str], work: Path,
              timeout_seconds: float = 600.0) -> dict[str, Any]:
    if not tool.is_file():
        raise T31Error(f"未找到 Vivado 工具：{tool}")
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
        raise T31Error(f"{name} 超过 {timeout_seconds:.0f}s；日志：{log_path}") from exc
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


class S2ASpatialRow0PilotTests(unittest.TestCase):
    """绑定 T01/T16/T20 冻结数据并检查 row0 feeder pilot。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = _ROOT
        head = _read_git_head(cls.root)
        _require_baseline_ancestor(_BASELINE_HEAD, head, cls.root)
        cls.head_start = head
        cls.rtl_path = cls.root / "src/s2a_conv_spatial_row0_pilot.sv"
        cls.tile_rtl_path = cls.root / "src/s2a_conv_spatial_tile16.sv"
        cls.tb_path = cls.root / "sim/tb_s2a_conv_spatial_row0_pilot.sv"
        cls.runner_path = Path(__file__).resolve()
        cls.default_evidence_path = (
            cls.root / "report/evidence/S2A-T31/spatial_row0_pilot.json"
        )
        cls.evidence_path = Path(os.environ.get(
            "S2A_T31_EVIDENCE_PATH", str(cls.default_evidence_path),
        ))
        cls.custom_evidence_path = "S2A_T31_EVIDENCE_PATH" in os.environ
        _require(cls.evidence_path.is_absolute(),
                 "S2A_T31_EVIDENCE_PATH 必须是绝对路径")
        _require(not os.path.lexists(str(cls.evidence_path)),
                 f"evidence 目标已经存在，拒绝覆盖：{cls.evidence_path}")
        if "S2A_T31_WORK_DIR" in os.environ:
            selected_work = Path(os.environ["S2A_T31_WORK_DIR"])
            _require(selected_work.is_absolute(),
                     "S2A_T31_WORK_DIR 必须是绝对路径")
            _require(not os.path.lexists(str(selected_work)),
                     f"TEMP 工作目录已经存在，拒绝复用：{selected_work}")
        if not cls.custom_evidence_path:
            _require(not os.path.lexists(str(cls.default_evidence_path)),
                     f"默认 evidence 已存在，拒绝覆盖：{cls.default_evidence_path}")
            _require(not os.path.lexists(str(cls.root / "report/evidence/S2A-T31")),
                     "默认 S2A-T31 evidence 目录已存在，拒绝复用")
            _require(
                (cls.root / "report/evidence").is_dir(),
                "report/evidence 精确父目录不存在",
            )
        for path in (cls.rtl_path, cls.tile_rtl_path, cls.tb_path):
            _require(path.is_file(), f"RTL/testbench 文件缺失：{path}")

        cls.g0_path = cls.root / (
            "docs/obsidian-project/04-提交材料/阶段验收/"
            "S2A-T01_模型交付规格与G0接口冻结.md"
        )
        cls.manifest_path = cls.root / "report/evidence/S2A-T01/tiny416_model_manifest.json"
        cls.d2_path = cls.root / "verification/s1_t02_d2_int8_forward.py"
        cls.t16_proof_path = cls.root / "report/evidence/S2A-T16/conv_requant_proof.json"
        cls.t16_script_path = cls.root / "verification/s2a_conv_requant_proof.py"
        cls.t17_path = cls.root / "verification/test_s2a_conv_engine_rtl.py"
        cls.t20_path = cls.root / "verification/test_s2a_conv_layer_scheduler_rtl.py"
        cls.t20_evidence_path = cls.root / (
            "report/evidence/S2A-T20/conv_layer_scheduler_simulation.json"
        )
        cls.t30_runner_path = cls.root / "verification/test_s2a_conv_spatial_tile16_rtl.py"
        cls.t30_evidence_path = cls.root / "report/evidence/S2A-T30/spatial_tile16_pilot.json"

        _require(_sha256_file(cls.g0_path) == _G0_SHA256,
                 "G0 冻结规范 SHA-256 不符")
        _require(_sha256_file(cls.manifest_path) == _MANIFEST_SHA256,
                 "T01 manifest SHA-256 不符")
        _require(_sha256_file(cls.d2_path) == _D2_SHA256,
                 "阶段一 D2 参考 SHA-256 不符")
        _require(_sha256_file(cls.t16_proof_path) == _T16_PROOF_SHA256 and
                 _sha256_file(cls.t16_script_path) == _T16_SCRIPT_SHA256,
                 "T16 冻结参数证明或脚本 SHA-256 不符")
        _require(_sha256_file(cls.t20_path) == _T20_RUNNER_SHA256,
                 "T20 helper runner SHA-256 不符")
        _require(_sha256_file(cls.t20_evidence_path) == _T20_EVIDENCE_SHA256,
                 "T20 layer36 证据 SHA-256 不符")
        _require(_sha256_file(cls.tile_rtl_path) == _T30_RTL_SHA256,
                 "T30 tile16 RTL SHA-256 不符")
        _require(_sha256_file(cls.t30_runner_path) == _T30_RUNNER_SHA256,
                 "T30 runner SHA-256 不符")
        _require(_sha256_file(cls.t30_evidence_path) == _T30_EVIDENCE_SHA256,
                 "T30 evidence SHA-256 不符")

        cls.t20 = _load_module("s2a_t31_t20_helpers", cls.t20_path)
        cls.t17 = cls.t20._load_t17_runner()
        cls.manifest, cls.t16_proof, cls.weights_by_layer, cls.package_path = (
            cls.t17._load_bound_inputs()
        )
        cls.layers = {int(row["layer_index"]): row for row in cls.manifest["layers"]}
        cls.layer = cls.layers[36]
        cls.source_layer = cls.layers[35]
        proof_layers = {
            int(row["layer_index"]): row for row in cls.t16_proof["layers"]
        }
        cls.parameters = cls.t17._candidate_parameters(cls.layer, proof_layers[36])
        cls.parameter0 = cls.parameters[0]
        _require(
            cls.layer.get("cfg_section") == 37 and
            cls.layer.get("op") == "convolutional" and
            cls.layer.get("input_shape_nchw") == [1, 256, 26, 26] and
            cls.layer.get("output_shape_nchw") == [1, 30, 26, 26] and
            cls.layer.get("kernel_hw") == [1, 1] and
            cls.layer.get("activation") == "linear" and
            cls.layer.get("layout") == "NCHW" and
            cls.layer.get("input_scale") == 0.12693486251230315 and
            cls.layer.get("output_scale") == 0.30223452951025775,
            "T01 layer36 cfg、张量规格、layout 或 scale 不符",
        )
        _require(
            cls.source_layer.get("output_shape_nchw") == [1, 256, 26, 26] and
            cls.source_layer.get("tensor_length_bytes") == _INPUT_BYTES and
            cls.source_layer.get("tensor_address") == 27966080 and
            cls.source_layer.get("output_scale") == cls.layer["input_scale"],
            "T01 layer35 输入地址、张量尺寸或 scale 不符",
        )
        weight_map = cls.manifest["address_map"]["weight_package"]
        weight_offsets = cls.layer["gf8_parameter_offsets"]
        _require(int(weight_map["address"]) == 0x00100000 and
                 int(weight_map["length_bytes"]) == 5903100 and
                 int(weight_offsets["quantized_weight_offset"]) == 5895420 and
                 int(weight_offsets["quantized_weight_bytes"]) == 7680,
                 "T01 GFINT8W1 layer36 权重映射不符")
        cls.layer_weights = cls.weights_by_layer[36]
        _require(len(cls.layer_weights) == 7680,
                 "T17 GF8 parser 返回的 layer36 权重字节数不符")
        cls.channel0_weights = cls.layer_weights[:_K]
        _require(_sha256_bytes(cls.channel0_weights) == _CHANNEL0_WEIGHT_SHA256,
                 "GFINT8W1 layer36 通道0 权重 SHA-256 不符")
        cls.bias = int(cls.layer["bias_accumulator_int32_per_output_channel"][0])
        _require(cls.bias == _BIAS, "通道0 frozen INT32 bias 不符")
        cls.weight_scale = float(cls.layer["weight_scale_per_output_channel"][0])
        cls.input_bytes, cls.sentinel_offsets = cls.t20._input_fixture()
        cls.golden_input, cls.full_golden, cls.golden_summary = cls.t20._input_and_golden(
            cls.layer, cls.layer_weights, cls.parameters, cls.t17,
        )
        _require(cls.input_bytes == cls.golden_input,
                 "T20 input helper 两次重建结果不一致")
        _require(len(cls.input_bytes) == _INPUT_BYTES and
                 _sha256_bytes(cls.input_bytes) == _T20_INPUT_SHA256,
                 "T20 layer35 输入 fixture size/hash 不符")
        _require(len(cls.full_golden) == 20280 and
                 _sha256_bytes(cls.full_golden) == _T20_GOLDEN_SHA256,
                 "T20 layer36 CPU golden size/hash 不符")
        _require(len(cls.sentinel_offsets) == 675,
                 "T20 fixture raw -128 sentinel 修正数量不符")
        cls.raw_row0 = _raw_row0_oracle(cls.input_bytes, cls.channel0_weights)
        cls.quantized_row0 = [
            _signed_byte(cls.t17._fixed_point_quantize(value, cls.parameter0))
            for value in cls.raw_row0
        ]
        cls.t20_quantized_row0 = [_signed_byte(value) for value in cls.full_golden[:26]]
        _require(cls.quantized_row0 == cls.t20_quantized_row0,
                 "独立 row0 raw oracle 经 T16 参数量化后与 T20 CPU golden 不一致")

        cls.t20_evidence = json.loads(
            cls.t20_evidence_path.read_text(encoding="utf-8")
        )
        cls.t30_evidence = json.loads(
            cls.t30_evidence_path.read_text(encoding="utf-8")
        )
        _require(cls.t30_evidence.get("task") == "S2A-T30" and
                 cls.t30_evidence.get("result") == "PASS",
                 "T30 tile16 pilot evidence 不是已验收 PASS")
        t30_raw = cls.t30_evidence["t20_cpu_reference"]["tile_raw_accumulators_int32"]
        t30_quant = cls.t30_evidence["t20_cpu_reference"]["tile_quantized_bytes_signed"]
        _require(cls.raw_row0[:16] == list(map(int, t30_raw)),
                 "row0 x=0..15 raw 向量与 T30 tile16 证据不一致")
        _require(cls.quantized_row0[:16] == list(map(int, t30_quant)),
                 "row0 x=0..15 CPU quantized reference 与 T30 证据不一致")

        cls.parameter_record = {
            key: int(value) for key, value in cls.parameter0.items()
            if isinstance(value, (int, bool))
        }
        cls.source_paths = {
            "g0_spec": cls.g0_path,
            "t01_manifest": cls.manifest_path,
            "d2_int8_forward": cls.d2_path,
            "t16_proof": cls.t16_proof_path,
            "t16_proof_script": cls.t16_script_path,
            "t17_runner": cls.t17_path,
            "t17_engine": cls.root / "src/s2a_conv_engine.sv",
            "t17_geometry": cls.root / "src/int8_conv_tap_geometry.sv",
            "t17_weight_address": cls.root / "src/int8_conv_weight_address.sv",
            "t17_mac": cls.root / "src/int8_mac_accumulator.sv",
            "t17_testbench": cls.root / "sim/tb_s2a_conv_engine.sv",
            "t17_evidence": cls.root / "report/evidence/S2A-T17/conv_engine_simulation.json",
            "t20_runner": cls.t20_path,
            "t20_scheduler": cls.root / "src/s2a_conv_layer_scheduler.sv",
            "t20_testbench": cls.root / "sim/tb_s2a_conv_layer_scheduler.sv",
            "t20_evidence": cls.t20_evidence_path,
            "gfint8w1_package": cls.package_path,
            "t30_tile16_rtl": cls.tile_rtl_path,
            "t30_runner": cls.t30_runner_path,
            "t30_evidence": cls.t30_evidence_path,
            "t31_feeder_rtl": cls.rtl_path,
            "t31_testbench": cls.tb_path,
            "t31_runner": cls.runner_path,
        }
        cls.source_hashes = {
            name: _sha256_file(path) for name, path in cls.source_paths.items()
        }
        t20_hashes = cls.t20_evidence.get("bindings", {}).get("t20_sha256", {})
        _require(t20_hashes.get("t20_scheduler") == cls.source_hashes["t20_scheduler"] and
                 t20_hashes.get("t20_testbench") == cls.source_hashes["t20_testbench"] and
                 t20_hashes.get("t20_runner") == cls.source_hashes["t20_runner"],
                 "T20 evidence 中冻结的 RTL/testbench/runner SHA 与当前文件不符")
        _require(cls.t20_evidence["bindings"]["dependency_sha256"]["t17_engine"] ==
                 cls.source_hashes["t17_engine"] and
                 cls.t20_evidence["bindings"]["dependency_sha256"]["t17_geometry"] ==
                 cls.source_hashes["t17_geometry"] and
                 cls.t20_evidence["bindings"]["dependency_sha256"]["t17_weight_address"] ==
                 cls.source_hashes["t17_weight_address"] and
                 cls.t20_evidence["bindings"]["dependency_sha256"]["t17_mac"] ==
                 cls.source_hashes["t17_mac"] and
                 cls.t20_evidence["bindings"]["dependency_sha256"]["t17_testbench"] ==
                 cls.source_hashes["t17_testbench"] and
                 cls.t20_evidence["bindings"]["dependency_sha256"]["t17_runner"] ==
                 cls.source_hashes["t17_runner"] and
                 cls.t20_evidence["bindings"]["dependency_sha256"]["t17_evidence"] ==
                 cls.source_hashes["t17_evidence"],
                 "T20 evidence 中 T17 依赖绑定与当前源不符")
        print(
            "T31_PREFLIGHT_PASS head={} layer36/cfg37 row0_pixels=26 "
            "input_sha256={} channel0_weight_sha256={} raw_oracle_values=26".format(
                cls.head_start, _sha256_bytes(cls.input_bytes),
                _sha256_bytes(cls.channel0_weights),
            ),
            flush=True,
        )

    def test_frozen_row0_cpu_reference(self) -> None:
        self.assertEqual(self.raw_row0[:16],
                         self.t30_evidence["t20_cpu_reference"]["tile_raw_accumulators_int32"])
        self.assertEqual(len(self.raw_row0), 26)
        self.assertEqual(self.quantized_row0, self.t20_quantized_row0)
        self.assertEqual(self.parameter_record.get("positive_multiplier"), 4521539)
        self.assertEqual(self.parameter_record.get("negative_multiplier"), 4521539)
        self.assertEqual(self.parameter_record.get("positive_q_shift"), 33)
        self.assertEqual(self.parameter_record.get("negative_q_shift"), 33)

    def test_git_ancestry_and_head_stability_policy(self) -> None:
        self.assertTrue(_is_ancestor(_BASELINE_HEAD, _BASELINE_HEAD, self.root))
        self.assertTrue(_is_ancestor(_BASELINE_HEAD, self.head_start, self.root))
        _require_stable_head(self.head_start, self.head_start)
        with self.assertRaises(T31Error):
            _require_stable_head(self.head_start, "0" * 40)

        with tempfile.TemporaryDirectory(prefix="s2a_t31_git_topology_") as temp:
            repo = Path(temp)
            _git_output(["init", "--quiet"], repo)
            _git_output(["config", "user.name", "S2A T31 topology test"], repo)
            _git_output(["config", "user.email", "s2a-t31@example.invalid"], repo)
            tree = _git_output(["mktree"], repo, input_text="")
            baseline = _git_output(["commit-tree", tree, "-m", "frozen baseline"], repo)
            descendant = _git_output(
                ["commit-tree", tree, "-p", baseline, "-m", "descendant"], repo,
            )
            unrelated = _git_output(["commit-tree", tree, "-m", "unrelated branch"], repo)
            self.assertTrue(_is_ancestor(baseline, baseline, repo))
            self.assertTrue(_is_ancestor(baseline, descendant, repo))
            self.assertFalse(_is_ancestor(baseline, unrelated, repo))

    def test_vivado_simulation_and_module_only_synthesis(self) -> None:
        selected_work = os.environ.get("S2A_T31_WORK_DIR")
        if selected_work:
            work = Path(selected_work)
        else:
            temp_root = Path(os.environ.get("TEMP", tempfile.gettempdir()))
            work = temp_root / f"s2a_t31_row0_{uuid.uuid4().hex}"
        _require(work.is_absolute(), "TEMP 工作目录必须是绝对路径")
        _require(not os.path.lexists(str(work)),
                 f"TEMP 工作目录已经存在，拒绝复用：{work}")
        _require(work.parent.is_dir(), f"TEMP 父目录不存在：{work.parent}")
        work.mkdir()
        progress_path = work / "progress.log"
        phases: list[dict[str, Any]] = []

        def progress(message: str) -> None:
            with progress_path.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(message + "\n")
            print(message, flush=True)

        def current_source_hashes() -> dict[str, str]:
            return {name: _sha256_file(path) for name, path in self.source_paths.items()}

        head_before = _read_git_head(self.root)
        _require_baseline_ancestor(_BASELINE_HEAD, head_before, self.root)
        _require_stable_head(self.head_start, head_before)
        source_hashes_before = current_source_hashes()
        self.assertEqual(source_hashes_before, self.source_hashes,
                         "冻结输入/源码在前置检查后发生变化")
        progress(f"PREFLIGHT_PASS work={work} evidence={self.evidence_path} head={head_before}")

        fixture_paths = {
            "input": work / "input_fixture.hex",
            "weights": work / "channel0_weights.hex",
            "expected_raw": work / "expected_raw.hex",
        }
        fixture_paths["input"].write_text(
            "".join(f"{value:02x}\n" for value in self.input_bytes),
            encoding="ascii", newline="\n",
        )
        fixture_paths["weights"].write_text(
            "".join(f"{value:02x}\n" for value in self.channel0_weights),
            encoding="ascii", newline="\n",
        )
        fixture_paths["expected_raw"].write_text(
            "".join(f"{value & 0xFFFF_FFFF:08x}\n" for value in self.raw_row0),
            encoding="ascii", newline="\n",
        )
        fixture_evidence = {
            name: {
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
            for name, path in fixture_paths.items()
        }
        progress("FIXTURE_READY input_bytes={} raw_values={} input_sha256={}".format(
            fixture_paths["input"].stat().st_size,
            len(self.raw_row0),
            fixture_evidence["input"]["sha256"],
        ))

        xvlog = _VIVADO_BIN / "xvlog.bat"
        xelab = _VIVADO_BIN / "xelab.bat"
        xsim = _VIVADO_BIN / "xsim.bat"
        phases_spec = [
            ("xvlog", xvlog, ["-sv", str(self.tile_rtl_path),
                               str(self.rtl_path), str(self.tb_path)]),
            ("xelab", xelab, ["-top", "tb_s2a_conv_spatial_row0_pilot",
                              "-snapshot", "s2a_t31_row0_snapshot"]),
            ("xsim", xsim, ["-R", "s2a_t31_row0_snapshot"]),
        ]
        sim_output = ""
        for name, tool, arguments in phases_spec:
            progress(f"PHASE_START {name} command={[str(tool), *arguments]}")
            phase = _run_tool(name, tool, arguments, work)
            phases.append(phase)
            self.assertEqual(
                phase["exit_code"], 0,
                f"{name} exit={phase['exit_code']}；日志尾部：\n{phase['output'][-6000:]}",
            )
            if name == "xsim":
                sim_output = phase["output"]
                self.assertNotIn("FAIL:", sim_output,
                                 "xsim 输出包含 testbench FAIL 标记")
            progress("PHASE_PASS {} exit_code={} elapsed_seconds={}".format(
                name, phase["exit_code"], phase["elapsed_seconds"],
            ))

        summary_match = re.search(r"PASS: baseline_reads=.*", sim_output)
        self.assertIsNotNone(summary_match, "xsim 缺少 row0 feeder PASS summary")
        summary = {
            key: int(value)
            for key, value in re.findall(r"([a-z0-9_]+)=([0-9]+)", summary_match.group(0))
        }
        expected_summary = {
            "baseline_reads": _TOTAL_REQUESTS,
            "baseline_feature_reads": 1792,
            "baseline_weight_reads": 512,
            "baseline_feature_bytes": 6656,
            "baseline_weight_bytes": 512,
            "baseline_core_beats": 512,
            "baseline_valid_values": 26,
            "tile_a_mask": 65535,
            "tile_b_mask": 1023,
            "normal_runs": 6,
            "memory_error_codes": 3,
            "abort_pending_cancel": 1,
            "reset_pending_cancel": 1,
            "recovery_runs": 5,
            "stall_seed": _STALL_SEED,
            "writes": 0,
            "errors": 0,
        }
        self.assertEqual(set(summary), set(expected_summary) | {"stall_cycles"},
                         "xsim summary 字段缺失或出现非预期字段")
        self.assertGreater(summary["stall_cycles"], 0, "缺少 memory stall 覆盖")
        for key, value in expected_summary.items():
            self.assertEqual(summary.get(key), value, f"xsim summary {key} 不符")

        tcl_path = work / "synth_row0_pilot.tcl"
        utilization_path = work / "utilization.rpt"
        tcl_text = (
            f"read_verilog -sv {{{self.tile_rtl_path.as_posix()}}}\n"
            f"read_verilog -sv {{{self.rtl_path.as_posix()}}}\n"
            "synth_design -top s2a_conv_spatial_row0_pilot -part xc7z020clg400-1\n"
            f"report_utilization -file {{{utilization_path.as_posix()}}}\n"
            "puts \"S2A_T31_SYNTH_PASS\"\n"
            "exit\n"
        )
        tcl_path.write_text(tcl_text, encoding="utf-8", newline="\n")
        vivado = _VIVADO_BIN / "vivado.bat"
        synth_arguments = [
            "-mode", "batch", "-source", str(tcl_path),
            "-log", str(work / "vivado_native.log"),
            "-journal", str(work / "vivado_native.jou"),
        ]
        progress(f"PHASE_START standalone_synthesis command={[str(vivado), *synth_arguments]}")
        synthesis = _run_tool("synthesis", vivado, synth_arguments, work)
        phases.append(synthesis)
        self.assertEqual(
            synthesis["exit_code"], 0,
            f"Vivado standalone synthesis exit={synthesis['exit_code']}；"
            f"日志尾部：\n{synthesis['output'][-6000:]}",
        )
        self.assertIn("S2A_T31_SYNTH_PASS", synthesis["output"])
        self.assertTrue(utilization_path.is_file(), "Vivado utilization report 缺失")
        utilization_text = utilization_path.read_text(encoding="utf-8", errors="replace")
        resources = {
            "lut": _resource_value(utilization_text, ("Slice LUTs*", "Slice LUTs", "CLB LUTs")),
            "ff": _resource_value(utilization_text, ("Slice Registers", "CLB Registers")),
            "bram_tile": _resource_value(utilization_text, ("Block RAM Tile",)),
            "dsp": _resource_value(utilization_text, ("DSPs",)),
        }
        progress(f"PHASE_PASS standalone_synthesis exit_code=0 resources={resources}")

        head_after = _read_git_head(self.root)
        _require_baseline_ancestor(_BASELINE_HEAD, head_after, self.root)
        _require_stable_head(head_before, head_after)
        source_hashes_after = current_source_hashes()
        self.assertEqual(source_hashes_after, source_hashes_before,
                         "仿真与综合期间冻结源或输入发生变化")

        evidence = {
            "schema_version": 1,
            "task": "S2A-T31",
            "result": "PASS",
            "scope": "layer36 channel0 row0 的两 tile G0-memory feeder pilot",
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
                "input_scale": float(self.layer["input_scale"]),
                "output_scale": float(self.layer["output_scale"]),
                "channel0_weight_scale": self.weight_scale,
                "channel0_bias_int32": self.bias,
                "channel0_requant_parameters_from_t16": self.parameter_record,
                "feature_mapping": "FEATURE_BASE + k*676 + x；row y=0，x=0..25",
                "feature_base_address": 27966080,
                "feature_tensor_bytes": _INPUT_BYTES,
                "weight_mapping": "package_base + layer36_quantized_offset + channel0*256 + k",
                "weight_package_base_address": 0x00100000,
                "layer36_quantized_weight_offset": 5895420,
                "layer36_weight_slice_bytes": 7680,
                "channel0_weight_bytes": _K,
                "channel0_weight_sha256": _sha256_bytes(self.channel0_weights),
                "package_bytes": int(self.manifest["address_map"]["weight_package"]["length_bytes"]),
            },
            "tile_mapping": {
                "tile_a_x": list(range(16)),
                "tile_b_x": list(range(16, 26)),
                "tile_a_valid_mask": 65535,
                "tile_b_valid_mask": 1023,
                "tile_b_invalid_lanes": list(range(10, 16)),
                "tile_mac_input_lane_mapping": "tile-local lane=word_index*4+byte_lane；tile B 地址偏移+16",
                "k_order": list(range(_K)),
                "feature_bytes_per_k": 26,
                "weight_bytes_per_k": 1,
                "input_nchw_byte_offset": "k*676+x",
            },
            "cpu_reference": {
                "input_fixture_helper": "verification/test_s2a_conv_layer_scheduler_rtl.py::_input_fixture",
                "golden_helper": "verification/test_s2a_conv_layer_scheduler_rtl.py::_input_and_golden",
                "input_generator": "按 T20 helper 使用 T10 地址 XOR byte pattern，并将 raw 0x80 sentinel 置零",
                "input_fixture_bytes": len(self.input_bytes),
                "input_fixture_sha256": _sha256_bytes(self.input_bytes),
                "patched_minus128_sentinel_count": len(self.sentinel_offsets),
                "channel0_raw_int32_by_x": self.raw_row0,
                "channel0_cpu_quantized_reference_by_x": self.quantized_row0,
                "cpu_quantized_reference_matches_t20_output": True,
                "first_16_raw_values_match_t30_tile16_evidence": True,
                "first_16_quantized_values_match_t30_evidence": True,
                "python_version": platform.python_version(),
                "numpy_version": self.t17.np.__version__,
                "T20_full_layer_golden_bytes": len(self.full_golden),
                "T20_full_layer_golden_sha256": _sha256_bytes(self.full_golden),
                "oracle": "Python 独立按 k=0..255 有序整数乘加；每步检查 signed INT32",
            },
            "memory_protocol": {
                "aligned_word_bytes": 4,
                "byte_order": "little-endian，lane n 对应 mem_addr+n",
                "single_outstanding": True,
                "request_fields_stable_until_handshake": True,
                "response_data_and_error_on_handshake": True,
                "read_strobe_nonzero": True,
                "write_strobe_always_zero": True,
                "output_buffer_writes": 0,
                "expected_normal_requests": _TOTAL_REQUESTS,
                "expected_feature_reads": 1792,
                "expected_weight_reads": 512,
                "expected_selected_feature_bytes": 6656,
                "expected_selected_weight_bytes": 512,
                "tile_b_final_feature_strobe": "0011 for x=24,25 only",
                "out_of_range_feature_reads": 0,
                "omitted_or_duplicated_valid_feature_bytes": 0,
                "timeout_counter": "不在本 pilot；由外层 G0 scheduler 负责",
            },
            "stimulus": {
                "fixtures": fixture_evidence,
                "stall_seed": _STALL_SEED,
                "stall_cycles_observed": summary["stall_cycles"],
                "success_runs": summary["normal_runs"],
                "memory_errors_injected_and_propagated": [1, 2, 6],
                "pending_abort_cancellations": summary["abort_pending_cancel"],
                "pending_reset_cancellations": summary["reset_pending_cancel"],
                "successful_recovery_runs": summary["recovery_runs"],
            },
            "simulation": {
                "simulator": "Vivado xvlog/xelab/xsim v2026.1",
                "commands": [phase["command"] for phase in phases[:3]],
                "phases": [
                    {key: value for key, value in phase.items() if key != "output"}
                    for phase in phases[:3]
                ],
                "testbench_summary": summary,
                "raw_int32_values_compared": 26,
                "expected_tile_result_count": 2,
                "tile_raw_handshakes_per_tile": 256,
                "core_accepted_k_beats": 512,
                "protocol_cases": {
                    "memory_error_code_1": "首个 weight read 同周期应答，精确返回并恢复",
                    "memory_error_code_2": "首个 feature read 同周期应答，精确返回并恢复",
                    "memory_error_code_6": "tile B 的部分字节 feature read 应答，精确返回并恢复",
                    "abort_during_pending_request": "请求撤销，无迟到应答，后续完整成功事务",
                    "reset_during_pending_request": "请求撤销，无迟到应答，后续完整成功事务",
                    "stalled_request_fields": "全部 memory 请求在未握手期间保持稳定",
                    "result_stall": "两个 tile result 各停顿3周期且字段稳定",
                },
            },
            "standalone_synthesis": {
                "tool": "Vivado v2026.1",
                "top": "s2a_conv_spatial_row0_pilot",
                "rtl_inputs": [str(self.tile_rtl_path), str(self.rtl_path)],
                "part": "xc7z020clg400-1",
                "opened_project_xpr": False,
                "utilization": resources,
                "phase_exit_code": synthesis["exit_code"],
                "phase_elapsed_seconds": synthesis["elapsed_seconds"],
                "tcl_path": str(tcl_path),
                "stdout_log_path": synthesis["stdout_log_path"],
                "stdout_log_sha256": synthesis["stdout_log_sha256"],
                "utilization_report_path": str(utilization_path),
                "utilization_report_sha256": _sha256_file(utilization_path),
                "timing_constraints_applied": False,
                "timing_conclusion": "未提供 XDC/时钟约束；不作时序结论。",
            },
            "limits": [
                "这是固定 layer36 channel0 row0 的 feeder/address/protocol pilot；不是完整 layer36 卷积或整网通过。",
                "不写输出 buffer；CPU 量化字节仅为 T16 参数推导的参考值，不代表 RTL requant。",
                "不包含 tile buffer 装载、外部总线集成、PS 接口、调度器 timeout counter 或系统调度。",
                "综合只覆盖本 wrapper 与 T30 tile16 模块，不加载 XPR/XDC；资源不是全系统估算且无时序结论。",
                "仅使用 T20 纯 helper 合成输入 fixture 与 CPU golden；不调用 T20 baseline-pinned spec/full XSIM。",
                "未读取 T25 shard或原图；未训练、未连接板卡、未烧录、未进入阶段2B/3。",
            ],
        }
        evidence_parent = self.evidence_path.parent
        if not evidence_parent.is_dir():
            if not self.custom_evidence_path:
                evidence_parent.mkdir()
            else:
                raise T31Error(f"evidence 输出父目录不存在：{evidence_parent}")
        _require(not os.path.lexists(str(self.evidence_path)),
                 f"evidence 目标在运行期间已出现，拒绝覆盖：{self.evidence_path}")
        with self.evidence_path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
        progress("EVIDENCE_WRITTEN path={} sha256={}".format(
            self.evidence_path, _sha256_file(self.evidence_path),
        ))
        print("S2A_T31_PASS evidence={} evidence_sha256={} work={} resources={}".format(
            self.evidence_path, _sha256_file(self.evidence_path), work, resources,
        ), flush=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
