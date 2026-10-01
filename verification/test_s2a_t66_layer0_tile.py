"""离线核验 T66 夹具绑定、RTL/仿真输入绑定和完整层仿真证据。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE_DIR = ROOT / "report" / "evidence" / "S2A-T66" / "tile01"
INPUT_SHA256 = "da26d3850d23d6f8cb466416799358e77fbeceaa8ee27696ebf7ab365248ab9e"
WEIGHT_SHA256 = "df49b5d3aeaebd6b4107b99d83ffa791d7a7e24bd7b26df0815c246e5717e633"
OUTPUT_SHA256 = "220499b6b8122c3264bef4d581967d51eedccc9e28813df3e0ff8f8716bc2ed8"
SHARD_SHA256 = "49488538ced503bad996e284a3593d4fc7a1cf3b605d90221b3ca09875c4966e"
RAW_SHA256 = "090b1422f8e8d4d22124568af9778ba7bd5e7168407c0125e1e729d4a5a46f80"
INPUT_BYTES = 519_168
WEIGHT_BYTES = 864
OUTPUT_BYTES = 1_384_448
PASS_MARKER = "PASS: T66 sample0 layer0 full tensor matched T25; bytes=1384448 mismatches=0"
EXPECTED_ATTEMPT02_FAILURE_SHA256 = {
    "runner_log": "03a6445b00dcd38e8350d1328cdc282ed39fc40aaec4d85e6722f71cf790b736",
    "offline_resume_preflight": "fac7ed9962012310439ea3d7be50f7dae3c418936398a7a044b1c554ee161841",
    "status": "c7dfcffdf90e38f167ea849f9ef5696f2cbcfeea615ed6846d3c72df313794aa",
    "execution_record": "d49780d7032e2211812ee0d661e65215ad6b3055f11d4f9493107ff274b63041",
    "compile_snapshot": "0fc684b60d0107314f9172cb2474bde326d091bf328f52df0e324bdb7c382f2f",
}
PROCESS_ALLOWLIST_PATH = ROOT / "report" / "evidence" / "S2A-T65" / "run02" / "process_identity_allowlist.json"
PROCESS_ALLOWLIST_SHA256 = "bc743da5ac3d3b2a2e493f3b1b23bf8cc0dfce3913e179062022806797aa090e"
EXPECTED_CACHE_POLICY = {
    "decision": "A",
    "tile_order": "spatial_tile_major",
    "feature_patch_capacity_bytes": 51_200,
    "feature_patch_loads_per_spatial_tile": 1,
    "feature_patch_reuse_scope": "all_output_channel_groups_in_current_tile",
    "weight_group_capacity_bytes": 36_864,
    "weight_group_output_channel_lanes": 8,
    "weight_group_reuse_scope": "all_spatial_points_in_current_tile",
    "weight_group_loads_per_tile_per_output_channel_group": 1,
    "weight_group_reloads_across_spatial_tiles": "accepted_by_decision_A",
    "output_block_capacity_bytes": 512,
}
EXPECTED_LAYER0_TRANSFER_BUDGET = {
    "transaction_unit": "单次 transaction 为一条 32-bit 对齐 word 请求内 one-hot strobe 选中的 1 个字节；计数单位是 byte request",
    "tile_count": 676,
    "feature_patch_bytes_total": 586_092,
    "feature_in_bounds_byte_requests": 583_443,
    "feature_zero_padding_patch_bytes": 2_649,
    "weight_byte_requests": 584_064,
    "output_byte_requests": OUTPUT_BYTES,
    "all_single_byte_requests": 2_551_955,
    "request_latency_cycles": 7_655_865,
    "request_stall_cycles": 6_635_073,
    "response_stall_cycles": 6_635_073,
    "feature_request_stall_cycles": 1_516_947,
    "weight_request_stall_cycles": 1_518_566,
    "output_request_stall_cycles": 3_599_560,
    "feature_response_stall_cycles": 1_516_947,
    "weight_response_stall_cycles": 1_518_566,
    "output_response_stall_cycles": 3_599_560,
    "effective_mac_operations": 37_380_096,
    "parallel_mac_cycles": 4_672_512,
    "requant_cycles": 173_056,
    "point_bias_init_cycles": 170_352,
    "tile_group_control_cycles": 228_488,
    "boundary_padding_scan_cycles": 2_649,
    "estimated_total_cycles": 26_002_716,
    "watchdog_cycles": 75_000_000,
    "stall_pattern": [0, 1, 2, 7, 3],
}


class VerificationError(RuntimeError):
    """表示 T66 离线核验失败。"""


def require(condition: bool, message: str) -> None:
    """不满足核验条件时中止并指出具体对象。"""
    if not condition:
        raise VerificationError(message)


def sha256_file(path: Path) -> str:
    """分块计算文件摘要。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path, label: str) -> dict[str, Any]:
    """读取 UTF-8 JSON 对象。"""
    require(path.is_file() and not path.is_symlink(), f"{label} 普通文件缺失：{path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"{label} 无法读取：{path}: {exc}") from exc
    require(isinstance(value, dict), f"{label} 顶层不是 JSON 对象：{path}")
    return value


def verify_process_snapshot(path: Path, phase: str, expected_identities: list[dict[str, Any]],
                            expected_sha256: str) -> None:
    """核对编译阶段进程快照阶段标记、摘要和受保护进程身份。"""
    snapshot = read_json(path, f"T66 {phase} 进程快照")
    rows = snapshot.get("processes", [])
    require(snapshot.get("phase") == phase and
            sha256_file(path) == expected_sha256 and
            isinstance(rows, list) and len(rows) == len(expected_identities),
            f"T66 {phase} 进程快照阶段、摘要或进程数量不匹配")
    fields = ("pid", "parent_pid", "name", "executable_path", "command_line")
    by_pid = {row.get("pid"): row for row in rows if isinstance(row, dict)}
    expected_by_pid = {row.get("pid"): row for row in expected_identities}
    require(len(by_pid) == len(rows) and set(by_pid) == set(expected_by_pid),
            f"T66 {phase} 进程快照 PID 集合或唯一性不匹配")
    for pid, expected in expected_by_pid.items():
        actual = by_pid[pid]
        require(all(actual.get(field) == expected.get(field) for field in fields),
                f"T66 {phase} PID {pid} 的路径、父进程或命令行身份不匹配")
        actual_ticks = utc_timestamp_ticks(actual.get("creation_date_utc"), phase, pid)
        expected_ticks = utc_timestamp_ticks(expected.get("creation_date_utc"), phase, pid)
        require(actual_ticks == expected_ticks,
                f"T66 {phase} PID {pid} 的 UTC 创建时刻不匹配")


def utc_timestamp_ticks(value: Any, phase: str, pid: Any) -> int:
    """把带 Z 后缀的 ISO UTC 时间转换成精确的 100 ns tick。"""
    require(isinstance(value, str), f"T66 {phase} PID {pid} 创建时刻必须是字符串")
    match = re.fullmatch(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,7}))?Z", value)
    require(match is not None, f"T66 {phase} PID {pid} 创建时刻不是有效 UTC ISO 字符串")
    try:
        whole_seconds = datetime.strptime(match.group(1), "%Y-%m-%dT%H:%M:%S").replace(
            tzinfo=timezone.utc
        )
    except ValueError as exc:
        raise VerificationError(f"T66 {phase} PID {pid} 创建时刻无效：{value}") from exc
    delta = whole_seconds - datetime(1970, 1, 1, tzinfo=timezone.utc)
    seconds = delta.days * 86_400 + delta.seconds
    fractional_ticks = int((match.group(2) or "0").ljust(7, "0"))
    return seconds * 10_000_000 + fractional_ticks


def verify_timestamp_normalization_regression(metadata: Any, context: str) -> None:
    """核对 PowerShell DateTime 与 ISO UTC 字符串的 tick 归一化回归记录。"""
    require(isinstance(metadata, dict) and
            metadata.get("status") == "PASS" and
            metadata.get("normalization") == "UTC_DateTimeOffset_100ns_ticks" and
            metadata.get("parsed_json_type") == "System.DateTime" and
            metadata.get("equivalent_iso_utc_matched") is True and
            metadata.get("plus_one_tick_rejected") is True and
            metadata.get("different_instant_rejected") is True,
            f"{context} 未记录通过的 UTC 创建时间归一化回归")
    base = utc_timestamp_ticks(metadata.get("test_timestamp_utc"), context, "regression")
    plus_one = utc_timestamp_ticks(metadata.get("plus_one_tick_utc"), context, "regression")
    different = utc_timestamp_ticks(metadata.get("different_instant_utc"), context, "regression")
    require(plus_one == base + 1 and different != base,
            f"{context} 的 +1 tick 或不同瞬间回归向量无效")


def previous_attempt_failure_semantics_valid(record: Any, status_line: Any,
                                             expected_failure: str) -> bool:
    """允许 invocation 计数字段缺席或为 null，其余失败身份字段须精确匹配。"""
    if not isinstance(record, dict):
        return False
    invocation_count_is_null_or_missing = (
        "xsim_invocation_attempt_count" not in record or
        record.get("xsim_invocation_attempt_count") is None
    )
    return (
        record.get("status") == "FAIL_XSIM" and
        record.get("xsim_started") is False and
        type(record.get("xsim_launch_count")) is int and
        record.get("xsim_launch_count") == 0 and
        invocation_count_is_null_or_missing and
        status_line == "FAIL_XSIM" and
        record.get("failure") == expected_failure
    )


def verify_previous_attempt_failure_semantics_regression() -> None:
    """回归 missing/null invocation 字段及其余失败身份字段的严格拒绝行为。"""
    expected_failure = (
        "T66_PROCESS_SNAPSHOT_CHANGED: 批准快照之后出现新的或变化的 Xilinx 进程："
        "pid=8712 name=vivado.exe"
    )
    base = {
        "status": "FAIL_XSIM",
        "xsim_started": False,
        "xsim_launch_count": 0,
        "failure": expected_failure,
    }
    missing = dict(base)
    explicit_null = {**base, "xsim_invocation_attempt_count": None}
    invalid_records = (
        {**base, "xsim_invocation_attempt_count": 0},
        {**base, "status": "PASS_FULL_LAYER0"},
        {**base, "xsim_started": True},
        {**base, "xsim_launch_count": 1},
        {**base, "xsim_started": "false"},
        {**base, "xsim_launch_count": "0"},
        {**base, "failure": "T66_OTHER_FAILURE"},
    )
    require(previous_attempt_failure_semantics_valid(missing, "FAIL_XSIM", expected_failure) and
            previous_attempt_failure_semantics_valid(explicit_null, "FAIL_XSIM", expected_failure),
            "T66 missing/null invocation 字段回归未接受有效 attempt02 失败记录")
    require(all(not previous_attempt_failure_semantics_valid(record, "FAIL_XSIM", expected_failure)
                for record in invalid_records) and
            not previous_attempt_failure_semantics_valid(missing, "COMPILED_WAITING_PARENT_REVIEW", expected_failure),
            "T66 attempt02 非 null invocation 或错误身份字段未被拒绝")


def verify_previous_attempt_failure_evidence(evidence_dir: Path, metadata: Any) -> None:
    """核对 attempt02 的快照前失败记录被 attempt03 原样引用。"""
    previous_dir = evidence_dir.parent / "compile_attempt02"
    expected_paths = {
        "runner_log": previous_dir / "run_simulation_runner_round4.txt",
        "offline_resume_preflight": previous_dir / "offline_resume_preflight_console.txt",
        "status": previous_dir / "status.txt",
        "execution_record": previous_dir / "execution_record.json",
        "compile_snapshot": previous_dir / "compile_pre_xsim_process_snapshot.json",
    }
    require(isinstance(metadata, dict) and
            Path(metadata.get("evidence_directory", "")).resolve() == previous_dir.resolve() and
            metadata.get("files_sha256") == EXPECTED_ATTEMPT02_FAILURE_SHA256 and
            metadata.get("compile_snapshot_path") == str(expected_paths["compile_snapshot"]) and
            metadata.get("compile_snapshot_sha256") == EXPECTED_ATTEMPT02_FAILURE_SHA256["compile_snapshot"],
            "T66 attempt03 未精确绑定 attempt02 失败证据")
    for name, path in expected_paths.items():
        require(path.is_file() and not path.is_symlink() and
                sha256_file(path) == EXPECTED_ATTEMPT02_FAILURE_SHA256[name],
                f"T66 attempt02 冻结失败证据改变：{path}")
    previous = read_json(expected_paths["execution_record"], "T66 attempt02 执行记录")
    status_line = expected_paths["status"].read_text(encoding="utf-8").splitlines()[0]
    expected_failure = "T66_PROCESS_SNAPSHOT_CHANGED: 批准快照之后出现新的或变化的 Xilinx 进程：pid=8712 name=vivado.exe"
    require(previous_attempt_failure_semantics_valid(previous, status_line, expected_failure) and
            previous_attempt_failure_semantics_valid(metadata, metadata.get("status"), expected_failure) and
            metadata.get("failure") == previous.get("failure"),
            "T66 attempt02 失败原因或 XSim 未启动计数不匹配")


def verify(evidence_dir: Path, require_simulation: bool) -> dict[str, Any]:
    """核对夹具、源码快照和可选的唯一完整 XSim 结果。"""
    evidence_dir = evidence_dir.resolve()
    evidence_root = (ROOT / "report" / "evidence" / "S2A-T66").resolve()
    require(evidence_dir != evidence_root and evidence_root in evidence_dir.parents,
            f"核验目录必须位于 T66 evidence 子目录：{evidence_dir}")
    verify_previous_attempt_failure_semantics_regression()
    fixture_manifest_path = evidence_dir / "fixture_manifest.json"
    manifest = read_json(fixture_manifest_path, "T66 夹具清单")
    require(manifest.get("schema_version") == "gestureforge_s2a_t66_layer0_golden_fixture_v1" and
            manifest.get("task_id") == "S2A-T66-TILE01" and
            manifest.get("status") == "OFFLINE_FIXTURE_VERIFIED_SIMULATION_NOT_RUN" and
            manifest.get("baseline_commit") == "9fb9ab7b380430c22bf147654157858b52151dad",
            "T66 夹具清单 schema、状态或基线提交不匹配")
    require(manifest.get("cache_policy") == EXPECTED_CACHE_POLICY and
            manifest.get("layer0_transfer_budget") == EXPECTED_LAYER0_TRANSFER_BUDGET and
            manifest.get("execution_record_path") == str((evidence_dir / "execution_record.json").resolve()) and
            manifest.get("fixture_preparation_runtime", {}).get("xvlog_started") is False and
            manifest.get("fixture_preparation_runtime", {}).get("xelab_started") is False and
            manifest.get("fixture_preparation_runtime", {}).get("xsim_started") is False,
            "T66 夹具清单的决策 A 缓存策略或 layer0 预算不匹配")

    sample = manifest.get("sample", {})
    weights = manifest.get("weights", {})
    golden = manifest.get("golden", {})
    require(sample.get("sample_index") == 0 and sample.get("sample_id") == "test_fist_000" and
            sample.get("preprocessed_input_sha256") == INPUT_SHA256 and
            sample.get("input_bytes") == INPUT_BYTES and
            weights.get("weight_layer_index") == 0 and
            weights.get("quantized_weight_offset_bytes") == 316 and
            weights.get("quantized_weight_bytes") == WEIGHT_BYTES and
            weights.get("source_slice_sha256") == WEIGHT_SHA256 and
            golden.get("layer_index") == 0 and golden.get("shape_nchw") == [1, 32, 208, 208] and
            golden.get("tensor_byte_offset") == 0 and golden.get("tensor_byte_length") == OUTPUT_BYTES and
            golden.get("tensor_sha256") == OUTPUT_SHA256 and
            golden.get("compressed_shard_sha256") == SHARD_SHA256 and
            golden.get("decompressed_sha256") == RAW_SHA256,
            "T66 夹具清单的样本、权重或 T25 映射字段不匹配")

    fixture_specs = (
        ("sample0_input_chw_int8.bin", sample, "input_fixture_path", "input_fixture_sha256", INPUT_BYTES, INPUT_SHA256),
        ("sample0_layer0_gf8_weights.bin", weights, "fixture_path", "fixture_sha256", WEIGHT_BYTES, WEIGHT_SHA256),
        ("sample0_layer0_expected_nchw_int8.bin", golden, "fixture_path", "fixture_sha256", OUTPUT_BYTES, OUTPUT_SHA256),
    )
    fixture_paths: dict[str, Path] = {}
    for name, record, path_field, sha_field, expected_length, expected_sha in fixture_specs:
        path = evidence_dir / "fixture" / name
        require(path.is_file() and not path.is_symlink(), f"T66 夹具普通文件缺失：{path}")
        require(Path(record.get(path_field, "")).resolve() == path.resolve(),
                f"T66 夹具路径与清单不匹配：{name}")
        actual_sha = sha256_file(path)
        require(path.stat().st_size == expected_length and
                actual_sha == record.get(sha_field) == expected_sha,
                f"T66 夹具长度或 SHA 错误：{name} bytes={path.stat().st_size} sha256={actual_sha}")
        fixture_paths[name] = path

    sources = {
        "preparer": ROOT / "verification" / "prepare_s2a_t66_layer0_golden.py",
        "offline_verifier": Path(__file__).resolve(),
        "runner": ROOT / "verification" / "run_s2a_t66_layer0_tile.ps1",
        "testbench": ROOT / "sim" / "tb_s2a_t66_layer0_tile.sv",
        "tile_engine": ROOT / "src" / "s2a_conv_tile_engine.sv",
        "descriptor_package": ROOT / "src" / "s2a_network_descriptor_pkg.sv",
    }
    bound_sources = manifest.get("source_sha256", {})
    for name, path in sources.items():
        require(path.is_file() and not path.is_symlink(), f"T66 源码普通文件缺失：{path}")
        require(bound_sources.get(name) == sha256_file(path), f"T66 源码摘要绑定改变：{path}")

    cache_summary_path = evidence_dir / "cache_policy_summary.json"
    cache_summary = read_json(cache_summary_path, "T66 缓存策略摘要")
    cache_summary_binding = manifest.get("cache_policy_summary", {})
    require(cache_summary_binding.get("path") == str(cache_summary_path.resolve()) and
            cache_summary_binding.get("sha256") == sha256_file(cache_summary_path) and
            cache_summary.get("schema_version") == "gestureforge_s2a_t66_cache_policy_v1" and
            cache_summary.get("task_id") == "S2A-T66-TILE01" and
            cache_summary.get("status") == "OFFLINE_POLICY_AND_BUDGET_VERIFIED_SIMULATION_NOT_RUN" and
            cache_summary.get("baseline_commit") == "9fb9ab7b380430c22bf147654157858b52151dad" and
            cache_summary.get("cache_policy") == EXPECTED_CACHE_POLICY and
            cache_summary.get("layer0_transfer_budget") == EXPECTED_LAYER0_TRANSFER_BUDGET and
            cache_summary.get("source_sha256") == bound_sources,
            "T66 cache policy summary 与 manifest、预算或源码摘要绑定不符")

    engine_text = sources["tile_engine"].read_text(encoding="utf-8")
    bench_text = sources["testbench"].read_text(encoding="utf-8")
    runner_text = sources["runner"].read_text(encoding="utf-8")
    for token in (
        "function ConvertTo-UtcInstantTicks",
        "function Assert-UtcTimestampNormalizationRegression",
        "function Test-PreviousAttemptFailureSemantics",
        "function Assert-PreviousAttemptFailureSemanticsRegression",
        "2026-09-29T18:07:06.157789Z",
        "2026-09-29T18:07:06.1577891Z",
        "2026-09-29T18:07:07.157789Z",
        "ConvertTo-UtcInstantTicks -Value $process.creation_date_utc",
        "ConvertTo-UtcInstantTicks -Value $known.creation_date_utc",
        "Get-PreviousAttemptFailureEvidence",
    ):
        require(token in runner_text, f"T66 runner 缺少 UTC 创建时间归一化或 attempt02 失败证据检查：{token}")
    require("$process.creation_date_utc -ceq $known.creation_date_utc" not in runner_text,
            "T66 runner 仍使用 DateTime 与 ISO 字符串的原始类型比较")
    for token in (
        "module s2a_conv_tile_engine",
        "TILE_EDGE = 8",
        "LANE_COUNT = 8",
        "MAX_FEATURE_PATCH_BYTES = 51200",
        "MAX_WEIGHT_GROUP_BYTES = 36864",
        "OUTPUT_BLOCK_BYTES = 512",
        "S2A_CONV_BIAS_ACCUMULATOR_INT32",
        "S2A_T23_MQ_ROM",
        "ST_FEATURE_RESPONSE",
        "ST_WEIGHT_RESPONSE",
        "ST_COMPUTE_POINT_PREP",
        "state <= ST_COMPUTE_POINT_PREP",
        "ST_OUTPUT_RESPONSE",
        "backend_cancel = hard_reset || abort",
    ):
        require(token in engine_text, f"T66 RTL 缺少结构或协议声明：{token}")
    for token in (
        "s2a_conv_tile_engine u_dut",
        "[1,32,208,208]",
        "stall-pattern=[0,1,2,7,3]",
        "CYCLE_LIMIT = 75000000",
        "estimated_cycles<=26003000",
        "next_cycle_progress = 2000000",
        "T66 backpressure 期间 request 字段变化",
        "T66 重复写输出字节",
        "T66 输出 mismatch",
        "T66 有未写输出字节",
        "T66 memory model 发现第二个 outstanding 请求",
        "weight_seen[load_index]",
        "weight_seen[weight_byte_index] <= 1'b1",
        "request stall 序列错误",
        "response stall 序列错误",
        "T66_CLASS_STALL",
        "T66_POINT_BIAS_RESET_PASS",
        "first_tile_point0_requant_seen",
        "first_tile_point1_bias_checked",
        "u_dut.lane_accumulator[point_bias_lane]",
        "first_tile_point0_golden_seen",
        "first_tile_point1_golden_seen",
        "class_request_count[FEATURE_CLASS]",
        "class_request_count[WEIGHT_CLASS]",
        "class_request_count[OUTPUT_CLASS]",
        "backend_req_addr[1:0] != 2'b00",
        "response_delay_remaining",
        "T66_CYCLE_PROGRESS",
        "PASS: T66 sample0 layer0 full tensor matched T25; bytes=%0d mismatches=0",
    ):
        require(token in bench_text, f"T66 testbench 缺少完整层验收项：{token}")
    require("$value$plusargs" not in bench_text and "-testplusarg" not in runner_text,
            "T66 runner/testbench 不得通过 XSim 传入 D:/ 夹具路径参数")
    require("s2a_conv_tile_engine.sv" in runner_text and
            "tb_s2a_t66_layer0_tile.sv" in runner_text and
            r"EvidenceDirectory = 'D:\FPGA_Competition\report\evidence\S2A-T66\tile01'" in runner_text and
            "T66_EVIDENCE_SCOPE_INVALID" in runner_text and
            "'-debug'" in runner_text and "'off'" in runner_text and "'-R'" in runner_text,
            "T66 runner 没有绑定新 RTL/testbench 或关闭波形的执行选项")
    require("watchdog_cycles = 75000000" in runner_text and
            "simulator watchdog 75000000 cycles" in runner_text and
            "60000000" not in runner_text,
            "T66 runner 的 watchdog metadata 与 75M 周期限制不一致")
    for token in (
        "decision = 'A'",
        "tile_order = 'spatial_tile_major'",
        "feature_patch_loads_per_spatial_tile = 1",
        "weight_group_loads_per_tile_per_output_channel_group = 1",
        "weight_group_reloads_across_spatial_tiles = 'accepted_by_decision_A'",
        "weight_byte_requests = 584064",
    ):
        require(token in runner_text, f"T66 runner 缺少获批 cache policy/预算字段：{token}")
    compile_only_return = runner_text.find(
        "PASS: T66 fixture, xvlog, xelab complete; XSim not started."
    )
    compile_only_exit = runner_text.find("exit 0", compile_only_return)
    xsim_start = runner_text.find("$execution.status = 'XSIM_RUNNING'")
    require(compile_only_return >= 0 and compile_only_exit >= 0 and xsim_start > compile_only_exit,
            "T66 CompileOnly 路径没有在 XSim 状态逻辑之前显式退出")

    result: dict[str, Any] = {
        "fixture_manifest_sha256": sha256_file(fixture_manifest_path),
        "fixture_sha256": {name: sha256_file(path) for name, path in fixture_paths.items()},
        "source_sha256": {name: sha256_file(path) for name, path in sources.items()},
        "cache_policy_summary_sha256": sha256_file(cache_summary_path),
        "simulation_verified": False,
    }
    execution_path = evidence_dir / "execution_record.json"
    if execution_path.is_file() and not require_simulation:
        execution_record = read_json(execution_path, "T66 执行记录")
        require(execution_record.get("task_id") == "S2A-T66-TILE01" and
                execution_record.get("cache_policy") == EXPECTED_CACHE_POLICY and
                execution_record.get("layer0_transfer_budget") == manifest.get("layer0_transfer_budget") and
                execution_record.get("source_sha256") == bound_sources and
                execution_record.get("cache_policy_summary_path") == str(cache_summary_path.resolve()) and
                execution_record.get("cache_policy_summary_sha256") == cache_summary_binding.get("sha256"),
                "T66 execution record 未绑定获批缓存策略、layer0 预算或源码摘要")
        if execution_record.get("status") == "COMPILED_WAITING_PARENT_REVIEW":
            run_dir = evidence_dir / "sim"
            verify_timestamp_normalization_regression(
                execution_record.get("runtime_timestamp_regression"),
                "T66 execution record",
            )
            if evidence_dir.name == "compile_attempt03":
                verify_previous_attempt_failure_evidence(
                    evidence_dir,
                    execution_record.get("previous_attempt_failure_evidence"),
                )
            require(execution_record.get("xsim_started") is False and
                    execution_record.get("xsim_launch_count") == 0 and
                    execution_record.get("xvlog_started") is True and
                    execution_record.get("xvlog_launch_count") == 1 and
                    execution_record.get("xvlog_exit_code") == 0 and
                    execution_record.get("xelab_started") is True and
                    execution_record.get("xelab_launch_count") == 1 and
                    execution_record.get("xelab_exit_code") == 0,
                    "T66 CompileOnly 执行记录未证明 xvlog/xelab 成功或误示 XSim 已启动")
            expected_xvlog_command = [
                r"D:\Xilinx\2026.1\Vivado\bin\xvlog.bat", "-sv", "-work", "xil_defaultlib",
                str((ROOT / "src" / "s2a_network_descriptor_pkg.sv").resolve()),
                str((ROOT / "src" / "s2a_conv_tile_engine.sv").resolve()),
                str((ROOT / "sim" / "tb_s2a_t66_layer0_tile.sv").resolve()),
            ]
            expected_xelab_command = [
                r"D:\Xilinx\2026.1\Vivado\bin\xelab.bat", "-mt", "off", "-debug", "off",
                "xil_defaultlib.tb_s2a_t66_layer0_tile", "-s", "s2a_t66_layer0_tile_snapshot",
                "-log", "xelab.log",
            ]
            allowlist = read_json(PROCESS_ALLOWLIST_PATH, "T65 受保护进程 allowlist")
            require(sha256_file(PROCESS_ALLOWLIST_PATH) == PROCESS_ALLOWLIST_SHA256 and
                    allowlist.get("status") == "FROZEN_READ_ONLY_IDENTITIES" and
                    len(allowlist.get("identities", [])) == 3,
                    "T66 编译完成快照所用的 T65 受保护进程 allowlist 改变")
            expected_identities = allowlist["identities"]
            for tool_name, expected_command in (
                ("xvlog", expected_xvlog_command),
                ("xelab", expected_xelab_command),
            ):
                console_path = Path(execution_record.get(f"{tool_name}_console_path", ""))
                expected_console_path = run_dir / f"{tool_name}_console.txt"
                require(execution_record.get(f"{tool_name}_command") == expected_command and
                        execution_record.get(f"{tool_name}_working_directory") == str(run_dir.resolve()) and
                        console_path.resolve() == expected_console_path.resolve() and
                        console_path.is_file() and
                        sha256_file(console_path) == execution_record.get(f"{tool_name}_console_sha256") and
                        (run_dir / f"{tool_name}.log").is_file(),
                        f"T66 {tool_name} 精确命令、cwd、控制台摘要或日志不匹配")
                for edge in ("pre", "post"):
                    snapshot_path = Path(execution_record.get(
                        f"{tool_name}_{edge}_process_snapshot_path", ""))
                    verify_process_snapshot(
                        snapshot_path,
                        f"{'before' if edge == 'pre' else 'after'} {tool_name}",
                        expected_identities,
                        execution_record.get(f"{tool_name}_{edge}_process_snapshot_sha256", ""),
                    )
            compile_snapshot_path = Path(execution_record.get(
                "compile_pre_xsim_process_snapshot_path", ""))
            verify_process_snapshot(
                compile_snapshot_path,
                "compile_complete_prelaunch_snapshot",
                expected_identities,
                execution_record.get("compile_pre_xsim_process_snapshot_sha256", ""),
            )
            status_path = evidence_dir / "status.txt"
            require(status_path.is_file() and status_path.read_text(encoding="utf-8").strip() ==
                    "COMPILED_WAITING_PARENT_REVIEW",
                    "T66 CompileOnly 后状态文件不匹配")
            require(not (run_dir / "xsim.log").exists() and
                    not (run_dir / "xsim_console.txt").exists() and
                    not (run_dir / "xsim_stderr.txt").exists(),
                    "T66 CompileOnly 意外生成 XSim 运行日志")
        result["execution_record_sha256"] = sha256_file(execution_path)
    if require_simulation:
        run_dir = evidence_dir / "sim"
        record = read_json(execution_path, "T66 仿真执行记录")
        budget = record.get("cycle_budget", {})
        require(record.get("task_id") == "S2A-T66-TILE01" and
                record.get("status") == "PASS_FULL_LAYER0" and
                record.get("xsim_launch_count") == 1 and
                record.get("xsim_invocation_attempt_count") == 1 and
                record.get("xsim_started") is True and
                record.get("xsim_exit_code") == 0 and
                record.get("xvlog_exit_code") == 0 and
                record.get("xelab_exit_code") == 0 and
                record.get("watchdog_cycles") == 75_000_000 and
                record.get("estimated_cycles") == 26_003_000 and
                record.get("cache_policy") == EXPECTED_CACHE_POLICY and
                record.get("layer0_transfer_budget") == manifest.get("layer0_transfer_budget") and
                record.get("source_sha256") == bound_sources and
                record.get("cache_policy_summary_sha256") == cache_summary_binding.get("sha256") and
                record.get("xsim_working_directory") == str(run_dir.resolve()) and
                record.get("waveforms_enabled") is False,
                "T66 仿真执行记录未证明恰好一次成功 XSim 全层运行")
        require(budget.get("tile_count") == 676 and
                budget.get("feature_patch_bytes_total") == 586_092 and
                budget.get("feature_in_bounds_byte_requests") == 583_443 and
                budget.get("feature_zero_padding_patch_bytes") == 2_649 and
                budget.get("weight_byte_requests") == 584_064 and
                budget.get("output_byte_requests") == OUTPUT_BYTES and
                budget.get("all_single_byte_requests") == 2_551_955 and
                budget.get("request_latency_cycles") == 7_655_865 and
                budget.get("request_stall_cycles") == 6_635_073 and
                budget.get("response_stall_cycles") == 6_635_073 and
                budget.get("feature_request_stall_cycles") == 1_516_947 and
                budget.get("weight_request_stall_cycles") == 1_518_566 and
                budget.get("output_request_stall_cycles") == 3_599_560 and
                budget.get("feature_response_stall_cycles") == 1_516_947 and
                budget.get("weight_response_stall_cycles") == 1_518_566 and
                budget.get("output_response_stall_cycles") == 3_599_560 and
                budget.get("effective_mac_operations") == 37_380_096 and
                budget.get("parallel_mac_cycles") == 4_672_512 and
                budget.get("requant_cycles") == 173_056 and
                budget.get("point_bias_init_cycles") == 170_352 and
                budget.get("tile_group_control_cycles") == 228_488 and
                budget.get("boundary_padding_scan_cycles") == 2_649 and
                budget.get("estimated_total_cycles") == 26_002_716 and
                budget.get("stall_pattern") == [0, 1, 2, 7, 3],
                "T66 执行记录中的 8-lane cycle budget 不匹配冻结 descriptor")
        compile_snapshot_path = Path(record.get("compile_pre_xsim_process_snapshot_path", ""))
        require(compile_snapshot_path.is_file() and
                sha256_file(compile_snapshot_path) == record.get("compile_pre_xsim_process_snapshot_sha256"),
                "T66 编译完成、XSim 前审查快照摘要不匹配")
        for tool_name in ("xvlog", "xelab"):
            for edge in ("pre", "post"):
                path_key = f"{tool_name}_{edge}_process_snapshot_path"
                sha_key = f"{tool_name}_{edge}_process_snapshot_sha256"
                process_path = Path(record.get(path_key, ""))
                process_snapshot = read_json(process_path, f"T66 {tool_name} {edge} 进程快照")
                expected_phase = f"before {tool_name}" if edge == "pre" else f"after {tool_name}"
                require(process_snapshot.get("phase") == expected_phase and
                        sha256_file(process_path) == record.get(sha_key),
                        f"T66 {tool_name} {edge} 进程快照阶段或摘要不匹配")
        require(record.get("xsim_command") == [
                    r"D:\Xilinx\2026.1\Vivado\bin\xsim.bat", "-R", "-log", "xsim.log",
                    "s2a_t66_layer0_tile_snapshot",
                ] and "-testplusarg" not in record.get("xsim_command", []),
                "T66 实际 XSim 命令与经核对的无 plusarg 命令不符")
        xsim_log = run_dir / "xsim.log"
        console_log = run_dir / "xsim_console.txt"
        require(xsim_log.is_file() and console_log.is_file(), "T66 XSim 运行日志缺失")
        stderr_log = run_dir / "xsim_stderr.txt"
        require(stderr_log.is_file() and
                record.get("xsim_stderr_sha256") == sha256_file(stderr_log),
                "T66 XSim stderr 日志或摘要缺失")
        combined_logs = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in (xsim_log, console_log, stderr_log)
        )
        for transfer_class in range(3):
            require(f"T66_CLASS_STALL class={transfer_class} " in combined_logs,
                    f"T66 XSim 日志缺少 transfer class {transfer_class} 的 stall 序列记录")
        expected_class_metrics = {
            0: (583_443, 1_516_947),
            1: (584_064, 1_518_566),
            2: (OUTPUT_BYTES, 3_599_560),
        }
        observed_class_metrics: set[int] = set()
        for line in combined_logs.splitlines():
            class_match = re.search(
                r"T66_CLASS_STALL class=(\d+) requests=(\d+) request_stalls=(\d+) "
                r"responses=(\d+) response_stalls=(\d+) pattern=\[0,1,2,7,3\]",
                line,
            )
            if class_match is None:
                continue
            class_index, requests, request_stalls, responses, response_stalls = (
                int(value) for value in class_match.groups()
            )
            if class_index in expected_class_metrics:
                expected_count, expected_stalls = expected_class_metrics[class_index]
                require(requests == expected_count and responses == expected_count and
                        request_stalls == expected_stalls and response_stalls == expected_stalls,
                        f"T66 transfer class {class_index} 的实际 stall/request sequence 计数不符")
                observed_class_metrics.add(class_index)
        require(observed_class_metrics == set(expected_class_metrics),
                "T66 XSim 日志缺少一类或多类完整 stall/request sequence 指标")
        require(PASS_MARKER in combined_logs and "output_writes=1384448" in combined_logs and
                "mismatches=0" in combined_logs and "request_stalls=" in combined_logs and
                "response_stalls=" in combined_logs and "T66_CYCLE_PROGRESS" in combined_logs,
                "T66 XSim 日志缺少完整输出 PASS 证据")
        result_line = next((line for line in combined_logs.splitlines() if PASS_MARKER in line), "")
        metrics = re.search(
            r"input_reads=(\d+) weight_reads=(\d+) output_writes=(\d+) "
            r"requests=(\d+) responses=(\d+) request_stalls=(\d+) response_stalls=(\d+) cycles=(\d+)",
            result_line,
        )
        require(metrics is not None, "T66 PASS 行缺少完整 request/response/stall/cycle 计数")
        input_reads, weight_reads, output_writes, requests, responses, req_stalls, rsp_stalls, cycles = (
            int(value) for value in metrics.groups()
        )
        require(input_reads == 583_443 and weight_reads == 584_064 and
                output_writes == OUTPUT_BYTES and requests == 2_551_955 and
                responses == requests and req_stalls > 0 and rsp_stalls > 0 and
                req_stalls == 6_635_073 and rsp_stalls == 6_635_073 and
                cycles <= 75_000_000,
                "T66 PASS 行的全层读写、响应、stall 或周期计数不符")
        require(record.get("xsim_log_sha256") == sha256_file(xsim_log) and
                record.get("xsim_console_sha256") == sha256_file(console_log),
                "T66 执行记录中的 XSim 日志摘要不匹配")
        status_path = evidence_dir / "status.txt"
        require(status_path.is_file() and status_path.read_text(encoding="utf-8").strip() ==
                "PASS_FULL_SAMPLE0_LAYER0_ZERO_MISMATCH",
                "T66 最终状态文件不是完整 layer0 PASS")
        pre_snapshot = read_json(evidence_dir / "pre_xsim_process_snapshot.json", "T66 XSim 前进程快照")
        post_snapshot = read_json(evidence_dir / "post_xsim_process_snapshot.json", "T66 XSim 后进程快照")
        require(pre_snapshot.get("phase") == "immediately_before_xsim" and
                post_snapshot.get("phase") == "immediately_after_xsim",
                "T66 XSim 前后进程身份快照缺少准确阶段标记")
        require(record.get("pre_xsim_process_snapshot_sha256") == sha256_file(
                    evidence_dir / "pre_xsim_process_snapshot.json") and
                record.get("post_xsim_process_snapshot_sha256") == sha256_file(
                    evidence_dir / "post_xsim_process_snapshot.json"),
                "T66 进程快照摘要与执行记录不一致")
        result["simulation_verified"] = True
        result["execution_record_sha256"] = sha256_file(execution_path)
        result["xsim_log_sha256"] = sha256_file(xsim_log)

    return result


def main() -> int:
    """执行离线或完整仿真结果核验。"""
    parser = argparse.ArgumentParser(description="核验 T66 夹具绑定和 layer0 完整 XSim 结果")
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    parser.add_argument("--require-simulation", action="store_true")
    args = parser.parse_args()
    result = verify(args.evidence_dir, args.require_simulation)
    if args.require_simulation:
        print("PASS: T66 fixture/source binding and one full-layer XSim evidence verified")
        print(f"execution_record_sha256={result['execution_record_sha256']}")
        print(f"xsim_log_sha256={result['xsim_log_sha256']}")
    else:
        print("PASS: T66 offline fixture/source binding verified; XSim not evaluated")
        print(f"fixture_manifest_sha256={result['fixture_manifest_sha256']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VerificationError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
