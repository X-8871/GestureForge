#!/usr/bin/env python3
"""准备 T56 row20 的 CPU oracle 与仿真 fixture。"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any
sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
BASE_HEAD = "ad99b18f23122436bcdf900ef5dee15cb6492d42"
T54_REPORT = ROOT / "report/evidence/S2A-T54/layer35_row18_all_channels.json"
T54_REPORT_SHA256 = "089c0aa4b0b163d49c38602e44c61c0e606b8efc7ecbc546c1cfc8385f327f7a"
T55_REPORT = ROOT / "report/evidence/S2A-T55/layer35_row19_all_channels.json"
T55_REPORT_SHA256 = "73000657e78b9477d7391391d84d336212a7c42ffe829e5fb2cf760190e97e0f"
T55_RUNNER = ROOT / "verification/test_s2a_conv_layer35_row19_all_channels_rtl.py"
T55_RUNNER_SHA256 = "06b0c76102e7c0a28e8511d30009feb9284cceac2aa674728c7cbd54c217a049"
T54_RUNNER = ROOT / "verification/test_s2a_conv_layer35_row18_all_channels_rtl.py"
T54_RUNNER_SHA256 = "4ec6a743d6a80c380505be2a8601879c311a7f42e07323027098c07a8dadd4f3"
G0_PATH = ROOT / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
G0_SHA256 = "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230"
PREFLIGHT_ROOT = Path(r"C:\Users\22061\AppData\Local\Temp\s2a_t56_layer35_row20_preflight_20260928_01")
FIXTURE_ROOT = Path(r"C:\Users\22061\AppData\Local\Temp\s2a_t56_layer35_row20_all_channels_20260928_run01")
EVIDENCE_PATH = ROOT / "report/evidence/S2A-T56/layer35_row20_all_channels.json"
TESTBENCH_PATH = ROOT / "sim/tb_s2a_conv_layer35_row20_all_channels.sv"
NO_WAVE_PATH = ROOT / "sim/s2a_t56_no_wave.tcl"
RTL_PATHS = (
    "src/int8_conv_tap_geometry.sv",
    "src/int8_conv_weight_address.sv",
    "src/int8_mac_accumulator.sv",
    "src/s2a_conv_engine.sv",
    "src/s2a_conv_layer35_channel_probe.sv",
)
ROW = 20
OUTPUT_XS = tuple(range(26))
POINTS = tuple((ROW, x) for x in OUTPUT_XS)
RAW_COUNT = 6_656
INT8_COUNT = 6_656
RAW_BYTES = RAW_COUNT * 4
INT8_BYTES = INT8_COUNT
GOLDEN_BYTES = RAW_BYTES + INT8_BYTES
FEATURE_BYTES = 259_584
WEIGHT_BYTES = 884_736


class T56PreparationError(RuntimeError):
    """表示 T56 的冻结绑定或 CPU fixture 准备失败。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise T56PreparationError(message)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path) -> tuple[dict[str, Any], str]:
    data = path.read_bytes()
    value = json.loads(data.decode("utf-8"))
    _require(isinstance(value, dict), f"JSON 根节点不是对象：{path}")
    return value, _sha256(data)


def _current_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
        text=True, encoding="utf-8", errors="replace", check=False,
    )
    _require(result.returncode == 0, f"读取 Git HEAD 失败：{result.stderr.strip()}")
    return result.stdout.strip()


def _verify_t54_parent() -> tuple[dict[str, Any], dict[str, Any]]:
    _require(T54_REPORT.is_file(), f"缺少 T54 直接父报告：{T54_REPORT}")
    report, report_sha = _read_json(T54_REPORT)
    _require(report_sha == T54_REPORT_SHA256, "T54 直接父报告 SHA-256 不匹配")
    _require(report.get("task_id") == "S2A-T54" and
             report.get("status") == "PASS_SIMULATION_DATA_ONLY" and
             report.get("acceptance_status") == "PASS_INDEPENDENT_REVIEW_DATA_ONLY",
             "T54 直接父报告状态或独立 G2 审查状态不匹配")
    _require(report.get("scope") ==
             "tiny416 cfg section36 layer35; all 256 output channels at y=18, x=0..25; not full layer or network",
             "T54 直接父报告范围不匹配")

    bindings = report.get("bindings", {})
    fixed = bindings.get("fixed_points_yx", [])
    expected_parent_points = [[18, x] for x in OUTPUT_XS]
    _require(fixed == expected_parent_points, "T54 父报告坐标不是 y=18、x=0..25")
    parent_sources = bindings.get("T54_source_hashes", {})
    expected_parent_paths = (*RTL_PATHS,
                             "sim/tb_s2a_conv_layer35_row18_all_channels.sv",
                             "verification/test_s2a_conv_layer35_row18_all_channels_rtl.py")
    _require(set(parent_sources) == set(expected_parent_paths),
             "T54 父报告源码绑定集合与已审查版本不一致")
    for relative, expected in parent_sources.items():
        source = ROOT / relative
        _require(source.is_file() and _sha_file(source) == expected,
                 f"T54 父报告源码绑定不匹配：{relative}")
    _require(parent_sources.get("verification/test_s2a_conv_layer35_row18_all_channels_rtl.py") ==
             T54_RUNNER_SHA256 and _sha_file(T54_RUNNER) == T54_RUNNER_SHA256,
             "T54 已审查 runner 源码绑定不匹配")

    simulation = report.get("simulation", {})
    mcp_run = report.get("mcp_project_run", {})
    mcp_result = mcp_run.get("simulation_result", {})
    _require(simulation.get("status") == "PASS" and
             simulation.get("raw_int32_compares") == RAW_COUNT and
             simulation.get("quantized_int8_compares") == INT8_COUNT and
             simulation.get("progress_checkpoint_count") == 256 and
             simulation.get("finish_observed") is True and
             simulation.get("rpc_status") == "TIMEOUT" and
             simulation.get("rpc_exit_code") is None,
             "T54 直接父报告仿真计数或 MCP RPC 事实不匹配")
    _require(mcp_run.get("status") == "PASS_SIMULATION_DATA" and
             mcp_run.get("acceptance_status") == "PASS_INDEPENDENT_REVIEW_DATA_ONLY" and
             mcp_result.get("status") == "PASS" and
             mcp_result.get("raw_int32_compares") == RAW_COUNT and
             mcp_result.get("quantized_int8_compares") == INT8_COUNT and
             mcp_result.get("progress_checkpoint_count") == 256,
             "T54 MCP 工程仿真直接证据不匹配")
    return report, bindings


def _verify_t55_parent() -> tuple[dict[str, Any], dict[str, Any]]:
    _require(T55_REPORT.is_file(), f"缺少 T55 直接父报告：{T55_REPORT}")
    report, report_sha = _read_json(T55_REPORT)
    _require(report_sha == T55_REPORT_SHA256, "T55 直接父报告 SHA-256 不匹配")
    _require(report.get("task_id") == "S2A-T55" and
             report.get("status") == "PASS_SIMULATION_DATA_ONLY" and
             report.get("acceptance_status") == "PASS_INDEPENDENT_REVIEW_DATA_ONLY",
             "T55 父报告状态或独立 G2 审查状态不匹配")
    _require(report.get("scope") ==
             "tiny416 cfg section36 layer35; all 256 output channels at y=19, x=0..25; not full layer or network",
             "T55 父报告范围不匹配")

    bindings = report.get("bindings", {})
    expected_points = [[19, x] for x in OUTPUT_XS]
    _require(bindings.get("fixed_points_yx") == expected_points,
             "T55 父报告固定坐标不是 y=19、x=0..25")
    parent_sources = bindings.get("T55_source_hashes", {})
    expected_paths = (*RTL_PATHS,
                       "sim/tb_s2a_conv_layer35_row19_all_channels.sv",
                       "sim/s2a_t55_no_wave.tcl",
                       "verification/test_s2a_conv_layer35_row19_all_channels_rtl.py")
    _require(set(parent_sources) == set(expected_paths),
             "T55 父报告源码绑定集合不匹配")
    for relative, expected in parent_sources.items():
        source = ROOT / relative
        _require(source.is_file() and _sha_file(source) == expected,
                 f"T55 父报告源码绑定不匹配：{relative}")
    _require(parent_sources.get("verification/test_s2a_conv_layer35_row19_all_channels_rtl.py") ==
             T55_RUNNER_SHA256 and _sha_file(T55_RUNNER) == T55_RUNNER_SHA256,
             "T55 已审查 runner SHA-256 不匹配")

    t54_binding = bindings.get("T54_parent_report", {})
    _require(t54_binding.get("sha256") == T54_REPORT_SHA256 and T54_REPORT.is_file() and
             _sha_file(T54_REPORT) == T54_REPORT_SHA256,
             "T55 的 T54 祖先报告 SHA-256 不匹配")
    t54_sources = bindings.get("T54_source_hashes", {})
    expected_t54_paths = (*RTL_PATHS,
                          "sim/tb_s2a_conv_layer35_row18_all_channels.sv",
                          "verification/test_s2a_conv_layer35_row18_all_channels_rtl.py")
    _require(set(t54_sources) == set(expected_t54_paths), "T55 报告中的 T54 源码集合不匹配")
    for relative, expected in t54_sources.items():
        source = ROOT / relative
        _require(source.is_file() and _sha_file(source) == expected,
                 f"T55 报告中的 T54 源码绑定不匹配：{relative}")

    simulation = report.get("simulation", {})
    _require(simulation.get("status") == "PASS" and
             simulation.get("raw_int32_compares") == RAW_COUNT and
             simulation.get("quantized_int8_compares") == INT8_COUNT and
             simulation.get("progress_checkpoint_count") == 256 and
             simulation.get("finish_observed") is True and
             simulation.get("rpc_status") == "TIMEOUT" and
             simulation.get("rpc_exit_code") is None,
             "T55 父仿真计数或 RPC 事实不匹配")
    mcp_run = report.get("mcp_project_run", {})
    result = mcp_run.get("simulation_result", {})
    _require(mcp_run.get("status") == "PASS_SIMULATION_DATA" and
             mcp_run.get("acceptance_status") == "PASS_INDEPENDENT_REVIEW_DATA_ONLY" and
             result.get("status") == "PASS" and
             result.get("raw_int32_compares") == RAW_COUNT and
             result.get("quantized_int8_compares") == INT8_COUNT and
             result.get("progress_checkpoint_count") == 256,
             "T55 MCP 仿真数据或 G2 状态不匹配")
    return report, bindings

def _load_reviewed_t54_runner() -> Any:
    _require(T54_RUNNER.is_file() and _sha_file(T54_RUNNER) == T54_RUNNER_SHA256,
             "T54 已审查 runner 文件缺失或 SHA-256 不匹配")
    spec = importlib.util.spec_from_file_location("s2a_t54_reviewed_runner_for_t56", T54_RUNNER)
    _require(spec is not None and spec.loader is not None, "无法载入 T54 已审查 runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    # 复用 T54 冻结的数据装载与数值 oracle，将本任务 HEAD 作为当前工作树基线。
    module.BASE_HEAD = BASE_HEAD
    return module


def _source_hashes() -> dict[str, str]:
    paths = (*RTL_PATHS,
             "sim/tb_s2a_conv_layer35_row20_all_channels.sv",
             "sim/s2a_t56_no_wave.tcl",
             "verification/test_s2a_conv_layer35_row20_all_channels_rtl.py")
    result: dict[str, str] = {}
    for relative in paths:
        path = ROOT / relative
        _require(path.is_file(), f"T56 源文件不存在：{relative}")
        result[relative] = _sha_file(path)
    return result


def _artifact_record(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), "bytes": path.stat().st_size, "sha256": _sha_file(path)}


def _vectors_bytes(vectors: list[tuple[int, int, int, int, int, int, int, int]]) -> bytes:
    text = "".join(" ".join(str(value) for value in row) + "\n" for row in vectors)
    return text.encode("ascii")


def _write_exclusive(path: Path, content: bytes) -> None:
    with path.open("xb") as output:
        output.write(content)


def _prepare() -> dict[str, Any]:
    _require(_current_head() == BASE_HEAD, f"当前 HEAD 与 T56 冻结基线不符：{_current_head()}")
    _require(G0_PATH.is_file() and _sha_file(G0_PATH) == G0_SHA256,
             "S2A-T01 G0 规格 SHA-256 不匹配")
    _require(not EVIDENCE_PATH.exists(), f"拒绝覆盖已有 T56 报告：{EVIDENCE_PATH}")
    _require(not FIXTURE_ROOT.exists(), f"拒绝复用已有 T56 fixture 目录：{FIXTURE_ROOT}")
    evidence_parent = EVIDENCE_PATH.parent
    _require(evidence_parent.parent.is_dir(), f"T56 报告父目录不存在：{evidence_parent.parent}")
    if not evidence_parent.exists():
        evidence_parent.mkdir(exist_ok=False)
    _require(evidence_parent.is_dir(), f"T56 报告路径不是目录：{evidence_parent}")
    _require(PREFLIGHT_ROOT.is_dir(), f"CPU-only preflight 工作目录不存在：{PREFLIGHT_ROOT}")
    _require(not (PREFLIGHT_ROOT / "preflight.json").exists(), "拒绝覆盖已有 T56 preflight.json")
    expected_env = str(PREFLIGHT_ROOT.resolve())
    _require(Path.cwd().resolve() == PREFLIGHT_ROOT.resolve(), "当前工作目录不等于 T56 preflight 路径")
    _require(all(os.environ.get(key) and Path(os.environ[key]).resolve() == PREFLIGHT_ROOT.resolve()
                 for key in ("TEMP", "TMP", "TMPDIR")),
             "TEMP/TMP/TMPDIR 未全部绑定到 T56 preflight 路径")

    parent, parent_bindings = _verify_t55_parent()
    runner = _load_reviewed_t54_runner()
    inputs = runner._load_frozen_inputs()
    oracle = runner._build_oracle(inputs, progress=True, points=POINTS)
    _require(len(oracle["feature"]) == FEATURE_BYTES and
             len(inputs["weight_bytes"]) == WEIGHT_BYTES and
             len(oracle["raw_values"]) == RAW_COUNT and
             len(oracle["quantized_values"]) == INT8_COUNT and
             len(oracle["combined_golden"]) == GOLDEN_BYTES,
             "T56 fixture 长度或逐项比较计数不匹配")
    _require(all(y == ROW for y, _ in POINTS) and
             tuple(x for _, x in POINTS) == OUTPUT_XS,
             "T56 row20 坐标集合错误")

    blobs = {
        "feature_input.bin": oracle["feature"],
        "layer35_weights.bin": inputs["weight_bytes"],
        "golden.bin": oracle["combined_golden"],
        "vectors.txt": _vectors_bytes(oracle["vectors"]),
    }
    expected_sizes = {
        "feature_input.bin": FEATURE_BYTES,
        "layer35_weights.bin": WEIGHT_BYTES,
        "golden.bin": GOLDEN_BYTES,
        "vectors.txt": len(blobs["vectors.txt"]),
    }
    _require(all(len(blobs[name]) == size for name, size in expected_sizes.items()),
             "T56 fixture artifact 长度不匹配")

    FIXTURE_ROOT.mkdir(parents=True, exist_ok=False)
    for name, content in blobs.items():
        _write_exclusive(FIXTURE_ROOT / name, content)
    fixture_records = {name: _artifact_record(FIXTURE_ROOT / name) for name in blobs}
    fixture_manifest = {
        "schema": "GestureForge-S2A-T56-fixture-manifest-v1",
        "task_id": "S2A-T56",
        "status": "PREPARED_NOT_SIMULATED",
        "baseline_head": BASE_HEAD,
        "parent_report": {"path": str(T55_REPORT), "sha256": T55_REPORT_SHA256},
        "parent_runner": {"path": str(T54_RUNNER), "sha256": T54_RUNNER_SHA256},
        "runner_source_sha256": _sha_file(Path(__file__).resolve()),
        "fixture_root": str(FIXTURE_ROOT.resolve()),
        "files": fixture_records,
        "oracle": oracle["oracle"],
        "fixed_points_yx": [list(point) for point in POINTS],
    }
    fixture_manifest_path = FIXTURE_ROOT / "fixture_manifest.json"
    _write_exclusive(fixture_manifest_path,
                     (json.dumps(fixture_manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

    preflight_record = {
        "schema": "GestureForge-S2A-T56-cpu-preflight-v1",
        "task_id": "S2A-T56",
        "status": "PASS_CPU_ORACLE_ONLY",
        "baseline_head": BASE_HEAD,
        "scope": "tiny416 cfg section36 layer35; 256 output channels at y=20, x=0..25",
        "execution_context": {
            "cwd": str(Path.cwd().resolve()),
            "environment": {key: os.environ.get(key) for key in ("TEMP", "TMP", "TMPDIR")},
            "python": sys.executable,
            "runner": str(Path(__file__).resolve()),
            "runner_sha256": _sha_file(Path(__file__).resolve()),
            "vivado_or_xsim_invoked": False,
        },
        "parent": {"path": str(T55_REPORT), "sha256": T55_REPORT_SHA256,
                   "status": parent["status"],
                   "acceptance_status": parent["acceptance_status"],
                   "fixed_points_yx": parent_bindings["fixed_points_yx"]},
        "fixture_root": str(FIXTURE_ROOT.resolve()),
        "fixture_artifacts": fixture_records,
        "fixture_manifest": _artifact_record(fixture_manifest_path),
        "feature_fixture": oracle["fixture"],
        "weight_layer35": {"bytes": len(inputs["weight_bytes"]),
                            "sha256": inputs["weight_sha256"]},
        "oracle": oracle["oracle"],
        "expected_counts": oracle["expected_counts"],
    }
    preflight_path = PREFLIGHT_ROOT / "preflight.json"
    _write_exclusive(preflight_path,
                     (json.dumps(preflight_record, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

    source_hashes = _source_hashes()
    layer = inputs["layer35"]
    report = {
        "schema": "GestureForge-S2A-T56-layer35-row20-preparation-v1",
        "task_id": "S2A-T56",
        "status": "PREPARED_NOT_SIMULATED",
        "acceptance_status": "NOT_CLAIMED",
        "baseline_head": BASE_HEAD,
        "scope": "tiny416 cfg section36 layer35; all 256 output channels at y=20, x=0..25; not full layer or network",
        "bindings": {
            "T54_parent_report": parent_bindings["T54_parent_report"],
            "T54_source_hashes": parent_bindings["T54_source_hashes"],
            "T55_parent_report": {"path": str(T55_REPORT), "sha256": T55_REPORT_SHA256,
                                   "acceptance_status": parent["acceptance_status"]},
            "T55_source_hashes": parent_bindings["T55_source_hashes"],
            "T56_source_hashes": source_hashes,
            "G0_specification": {"path": str(G0_PATH), "sha256": G0_SHA256},
            "T01_manifest": inputs["bindings"]["T01_manifest"],
            "T23_parameter_table": inputs["bindings"]["T23_parameter_table"],
            "GF8_package": inputs["bindings"]["GF8_package"],
            "weight_layer35": {"byte_offset": inputs["layer35_weight_offset"],
                                "bytes": len(inputs["weight_bytes"]),
                                "sha256": inputs["weight_sha256"]},
            "model": {"name": "tiny416", "cfg_section": layer["cfg_section"],
                      "layer_index": layer["layer_index"],
                      "input_shape_nchw": layer["input_shape_nchw"],
                      "output_shape_nchw": layer["output_shape_nchw"],
                      "kernel_hw": layer["kernel_hw"], "stride_hw": layer["stride_hw"],
                      "padding_lrtb": layer["padding_lrtb"],
                      "padding_value_int8": layer["padding_value_int8"],
                      "layout": layer["layout"], "accumulator_bits": layer["accumulator_bits"]},
            "fixed_points_yx": [list(point) for point in POINTS],
            "oracle_source": {"path": str(T54_RUNNER), "sha256": T54_RUNNER_SHA256,
                              "methods": ["_load_frozen_inputs", "_build_oracle"]},
        },
        "fixture": {"generator": oracle["fixture"],
                    "root": str(FIXTURE_ROOT.resolve()),
                    "files": fixture_records,
                    "manifest": _artifact_record(fixture_manifest_path),
                    "golden_layout": {"raw_int32_le_bytes": RAW_BYTES,
                                      "int8_bytes": INT8_BYTES,
                                      "total_bytes": GOLDEN_BYTES,
                                      "order": "全部 raw INT32 little-endian，随后全部 INT8"}},
        "oracle": oracle["oracle"],
        "expected_counts": oracle["expected_counts"],
        "preflight": {"status": preflight_record["status"],
                      "path": str(preflight_path.resolve()),
                      "sha256": _sha_file(preflight_path),
                      "vivado_or_xsim_invoked": False},
        "attempt_history": [],
        "simulation": {"status": "NOT_RUN", "compile": "NOT_RUN", "elaboration": "NOT_RUN",
                       "xsim": "NOT_RUN", "mcp_simset": "sim_s2a_t56_row20"},
        "review": {"G2": "NOT_REVIEWED", "G3": "NOT_CLAIMED",
                    "G4": "NOT_CLAIMED", "G5": "NOT_CLAIMED"},
        "limitations": ["仅为 CPU oracle 与 fixture 准备；尚无 Vivado 编译、展开或仿真结果。",
                        "仅覆盖 y=20、x=0..25、256 通道；不代表整层或整网。",
                        "T54 的独立 G2 结论仅属于 T54 row18 证据，不自动扩展到 T56。"],
        "mcp_handoff": {
            "simset": "sim_s2a_t56_row20",
            "top": "tb_s2a_conv_layer35_row20_all_channels",
            "runtime": "all",
            "sources_in_order": [*RTL_PATHS,
                                  "sim/tb_s2a_conv_layer35_row20_all_channels.sv"],
            "no_wave_tcl": {"path": "sim/s2a_t56_no_wave.tcl",
                             "sha256": source_hashes["sim/s2a_t56_no_wave.tcl"],
                             "action": "关闭 debug_level 并将 log_all_signals 设为 0；须经 MCP source 执行并核实。"},
            "xsim_properties": {"xsim.elaborate.debug_level": "off",
                                "xsim.simulate.log_all_signals": 0},
            "fixture_files": list(blobs),
            "xsim_working_directory_suffix":
                "AX7Z020_Gesture.sim\\sim_s2a_t56_row20\\behav\\xsim",
        },
    }
    _write_exclusive(EVIDENCE_PATH,
                     (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    report["report_artifact"] = _artifact_record(EVIDENCE_PATH)
    print(json.dumps({
        "result": "PREPARED_NOT_SIMULATED",
        "report": str(EVIDENCE_PATH),
        "preflight": str(preflight_path),
        "fixture_root": str(FIXTURE_ROOT),
        "runner_sha256": source_hashes["verification/test_s2a_conv_layer35_row20_all_channels_rtl.py"],
        "counts": {"raw_int32": len(oracle["raw_values"]),
                   "int8": len(oracle["quantized_values"]),
                   "progress_checkpoints_expected": 256},
        "artifacts": fixture_records,
    }, ensure_ascii=False, indent=2), flush=True)
    return report


def _main() -> int:
    parser = argparse.ArgumentParser(description="T56 row20 CPU fixture preparation only")
    parser.add_argument("--prepare-only", action="store_true", help="仅运行 CPU oracle 并准备 fixture")
    args = parser.parse_args()
    if not args.prepare_only:
        parser.error("必须明确提供 --prepare-only；本 runner 不启动 Vivado/XSim")
    try:
        _prepare()
        return 0
    except Exception as exc:
        print(f"FAIL T56 {type(exc).__name__}: {exc}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(_main())
