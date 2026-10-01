#!/usr/bin/env python3
"""只读核验 S2A-T68 单样本 fixture 与冻结 source/golden 的绑定。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zlib
from pathlib import Path, PurePosixPath
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from verification.prepare_s2a_network_backend_golden import (
    DEFAULT_OUTPUT_ROOT,
    DESCRIPTOR_PACKAGE,
    EXPECTED_LAYER_COUNT,
    EXPECTED_SAMPLE_COUNT,
    PINNED_HASHES,
    ROOT,
    T01_MANIFEST,
    T01_SAMPLES,
    T25_INDEX,
    parse_descriptor_array,
    require,
    sha256_bytes,
    sha256_file,
)

T68_TESTBENCH = ROOT / "sim/tb_s2a_network_backend_golden.sv"
T68_RUNNER = ROOT / "verification/run_s2a_network_backend_verilator.ps1"
EXPECTED_RTL_SOURCE_PATHS = (
    "src/s2a_network_descriptor_pkg.sv",
    "src/int8_maxpool_geometry.sv",
    "src/int8_maxpool_window.sv",
    "src/int8_route_query.sv",
    "src/int8_upsample_query.sv",
    "src/s2a_conv_tile_engine.sv",
    "src/s2a_maxpool_engine.sv",
    "src/s2a_route_engine.sv",
    "src/s2a_upsample_engine.sv",
    "src/s2a_network_backend.sv",
)
PROGRESS_FUNCTIONAL_FIELDS = (
    "layer",
    "output",
    "tile_y",
    "tile_x",
    "group",
    "point",
    "reduction",
    "feature_scan",
    "weight_reduction",
    "output_lane",
    "output_point",
    "pool_tap",
    "bytes",
    "reads",
    "writes",
)


def read_json(path: Path) -> dict[str, Any]:
    """读取 UTF-8 JSON 对象。"""
    require(path.is_file(), f"缺少文件：{path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON 顶层不是对象：{path}")
    return value


def resolve_output_path(output_root: Path, value: str) -> Path:
    """按 run01 根目录解析受限的相对输出路径。"""
    relative = PurePosixPath(value)
    require(not relative.is_absolute() and ".." not in relative.parts, f"fixture 中包含越界路径：{value}")
    return output_root.joinpath(*relative.parts)


def progress_signature(values: dict[str, Any]) -> tuple[int, ...]:
    """只以真实层级、运算游标和存储事务计数构成功能进度签名。"""
    return tuple(values[name] for name in PROGRESS_FUNCTIONAL_FIELDS)


def verify_progress_watchdog_semantics(runner_text: str) -> dict[str, Any]:
    """离线验证周期变化不冒充工作进度，坏 marker 与超时不能通过。"""
    parser_match = re.search(
        r"function ConvertFrom-ProgressMarker \{(.*?)\n\}\s*\nfunction Test-ProgressSignatureChanged",
        runner_text,
        re.S,
    )
    require(parser_match is not None, "runner progress marker parser/function boundary 缺失")
    signature_match = re.search(r"\$signature\s*=\s*@\((.*?)\)\s*-join '\|'", parser_match.group(1), re.S)
    require(signature_match is not None, "runner 未构造功能进度签名")
    signature_fields = tuple(re.findall(r"\$Matches\.(\w+)", signature_match.group(1)))
    require(signature_fields == PROGRESS_FUNCTIONAL_FIELDS, "runner 功能签名字段与真实进度字段不匹配")
    require(
        not any(field in signature_fields for field in ("cycle", "phase", "time", "length")),
        "runner 将周期、阶段、时间或文件长度混入功能签名",
    )

    first = {
        "layer": 0, "output": 0, "tile_y": 0, "tile_x": 0, "group": 0,
        "point": 0, "reduction": 0, "feature_scan": 0, "weight_reduction": 0,
        "output_lane": 0, "output_point": 0, "pool_tap": 0, "bytes": 0,
        "reads": 100, "writes": 0,
    }
    later_cycle = 60_000_000
    first_cycle = 30_000_000
    require(later_cycle > first_cycle, "离线 cycle 增长样例构造错误")
    require(
        progress_signature(dict(first, cycle=first_cycle, phase="running"))
        == progress_signature(dict(first, cycle=later_cycle, phase="running")),
        "仅 cycle 增长时功能签名发生变化",
    )
    changed_layer = dict(first, layer=first["layer"] + 1)
    changed_tile_cursor = dict(first, tile_x=first["tile_x"] + 1)
    changed_tap_cursor = dict(first, pool_tap=first["pool_tap"] + 1)
    changed_transaction = dict(first, reads=first["reads"] + 1)
    changed_completed_bytes = dict(first, bytes=first["bytes"] + 1)
    require(progress_signature(first) != progress_signature(changed_layer), "layer 计数变化未识别为进展")
    require(progress_signature(first) != progress_signature(changed_tile_cursor), "tile 计数变化未识别为进展")
    require(progress_signature(first) != progress_signature(changed_tap_cursor), "tap 计数变化未识别为进展")
    require(progress_signature(first) != progress_signature(changed_transaction), "事务计数变化未识别为进展")
    require(progress_signature(first) != progress_signature(changed_completed_bytes), "完成字节变化未识别为进展")

    require(
        re.search(
            r"if \(Test-ProgressSignatureChanged.*?\) \{\s*\$lastProgressAtUtc = \[datetime\]::UtcNow\s*\$functionalProgressObserved = \$true",
            runner_text,
            re.S,
        ) is not None,
        "runner 只有功能签名变化时才刷新无进度计时",
    )
    require(
        re.search(
            r"\$progressMarkersValid\s*=\s*\(-not \$badProgressMarkerSeen\).*?\$functionalProgressObserved",
            runner_text,
            re.S,
        ) is not None,
        "runner progress validity 未拒绝坏 marker 或缺少功能进度",
    )
    require(
        re.search(r"if \(\$watchdogFailure\) \{\s*\$runnerExitCode = 124", runner_text) is not None,
        "runner watchdog timeout 未映射到失败退出码",
    )
    require(
        "if ($null -eq $progressMarker) {\n                    $badProgressMarkerSeen = $true" in runner_text
        and "if ($runnerExitCode -ne 0) { exit $runnerExitCode }" in runner_text,
        "坏 marker 未阻断 PASS 或 runner 未保留失败退出码",
    )
    return {
        "functional_signature_fields": list(signature_fields),
        "cycle_only_change_is_progress": False,
        "layer_change_is_progress": True,
        "tile_cursor_change_is_progress": True,
        "tap_cursor_change_is_progress": True,
        "transaction_change_is_progress": True,
        "completed_bytes_change_is_progress": True,
        "bad_marker_blocks_pass": True,
        "watchdog_timeout_blocks_pass": True,
    }


def verify_harness_bindings() -> dict[str, Any]:
    """只读核对编译闭包、端口、byte-lane 规则与无进度看门狗。"""
    runner_text = T68_RUNNER.read_text(encoding="utf-8")
    testbench_text = T68_TESTBENCH.read_text(encoding="utf-8")
    backend_text = (ROOT / "src/s2a_network_backend.sv").read_text(encoding="utf-8")
    match = re.search(r"\$rtlRelativePaths\s*=\s*@\((.*?)\n\)", runner_text, re.S)
    require(match is not None, "runner 缺少 RTL source list")
    rtl_paths = tuple(
        value.replace("\\", "/")
        for value in re.findall(r"^\s*'([^']+\.sv)'\s*,?\s*$", match.group(1), re.M)
    )
    require(rtl_paths == EXPECTED_RTL_SOURCE_PATHS, "runner compile source list 与冻结闭包不一致")
    source_paths = (*rtl_paths, "sim/tb_s2a_network_backend_golden.sv")
    source_rows: list[dict[str, Any]] = []
    source_texts: dict[str, str] = {}
    for relative_path in source_paths:
        source_path = ROOT / relative_path
        raw = source_path.read_bytes()
        source_texts[relative_path] = raw.decode("utf-8")
        source_rows.append(
            {
                "path": relative_path,
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )

    port_block = re.search(r"module\s+s2a_network_backend\s*\((.*?)\n\);", backend_text, re.S)
    require(port_block is not None, "无法解析 backend 外部端口")
    backend_ports = set(
        re.findall(r"(?:input|output)\s+logic(?:\s*\[[^]]+\])?\s+(\w+)", port_block.group(1))
    )
    instance_block = re.search(r"s2a_network_backend\s+u_backend\s*\((.*?)\n\s*\);", testbench_text, re.S)
    require(instance_block is not None, "TB 缺少冻结 backend instance")
    testbench_ports = set(re.findall(r"\.(\w+)\s*\(", instance_block.group(1)))
    require(backend_ports == testbench_ports, "TB/backend 端口集合不匹配")

    conv_text = source_texts["src/s2a_conv_tile_engine.sv"]
    maxpool_text = source_texts["src/s2a_maxpool_engine.sv"]
    route_text = source_texts["src/s2a_route_engine.sv"]
    upsample_text = source_texts["src/s2a_upsample_engine.sv"]
    require(
        re.search(r"request_strobe_latched\s*<=\s*4'b0001\s*<<\s*feature_source_address_wide\[1:0\]", conv_text)
        is not None,
        "conv feature read 未绑定 byte-per-request strobe",
    )
    require(
        re.search(r"request_strobe_latched\s*<=\s*4'b0001\s*<<\s*weight_source_address_wide\[1:0\]", conv_text)
        is not None,
        "conv weight read 未绑定 byte-per-request strobe",
    )
    require(
        re.search(r"selected_input_lane\s*=\s*4'b0001\s*<<\s*tap_address_latched\[read_tap_index\]\[1:0\]", maxpool_text)
        is not None,
        "maxpool read 未绑定 byte-per-request strobe",
    )
    require(
        re.search(r"selected_read_lane\s*=\s*4'b0001\s*<<\s*source_address_latched\[1:0\]", route_text)
        is not None,
        "route read 未绑定 byte-per-request strobe",
    )
    require(
        re.search(r"backend_req_rstrb\s*=\s*4'b0001\s*<<\s*source_address_latched\[1:0\]", upsample_text)
        is not None,
        "upsample read 未绑定 byte-per-request strobe",
    )

    addresses = parse_descriptor_array(source_texts["src/s2a_network_descriptor_pkg.sv"], "S2A_OUTPUT_ADDRESS", 32)
    lengths = parse_descriptor_array(source_texts["src/s2a_network_descriptor_pkg.sv"], "S2A_OUTPUT_LENGTH_BYTES", 32)
    write_required = parse_descriptor_array(
        source_texts["src/s2a_network_descriptor_pkg.sv"], "S2A_OUTPUT_MEMORY_WRITE_REQUIRED", 1
    )

    def tensor_owner(address: int) -> int:
        for layer_index, (base, length, stored) in enumerate(zip(addresses, lengths, write_required, strict=True)):
            if stored and base <= address < base + length:
                return layer_index + 2
        return -1

    cross_boundary_address = (addresses[29] + lengths[29] - 1) & 0xFFFFFFFC
    selected_owners = [tensor_owner(cross_boundary_address + lane) for lane in (0, 2)]
    require(selected_owners == [31, -1], "layer29 尾部跨界负向样例不再覆盖有效/非法 lanes")
    require(
        "function automatic logic [2:0] validate_read_request" in testbench_text
        and "lane_owner != first_owner" in testbench_text
        and "cross_boundary_test_strobe = 4'b0101" in testbench_text
        and "cross_boundary_test_address + 2" in testbench_text,
        "TB 缺少按 lane 拒绝跨 tensor/read 越界的检查",
    )
    require(
        "function automatic logic is_onehot4" in testbench_text
        and "!is_onehot4(mem_rstrb)" in testbench_text
        and "selected_address = address + selected_lane" in testbench_text,
        "TB 缺少 one-hot read 断言或按选中 lane 归属 transfer",
    )
    progress_marker_fields = (
        "sample=%0d", "layer=%0d", "cycle=%0d", "output=%0d", "conv_tile_y=%0d",
        "conv_tile_x=%0d", "conv_group=%0d", "conv_point=%0d", "conv_reduction=%0d",
        "conv_feature_scan=%0d", "conv_weight_reduction=%0d", "conv_output_lane=%0d",
        "conv_output_point=%0d", "pool_tap=%0d", "feature_write_bytes=%0d",
        "read_transactions=%0d", "write_transactions=%0d", "phase=%s",
    )
    require(
        "PROGRESS_INTERVAL_CYCLES = 64'd30000000" in testbench_text
        and "S2A_PROGRESS " in testbench_text
        and all(field in testbench_text for field in progress_marker_fields)
        and "$fflush(progress_marker_file_id);" in testbench_text
        and "$fflush();" in testbench_text,
        "TB progress marker 字段、频率或 flush 缺失",
    )
    require(
        re.search(
            r"ST_COMPUTE:\s*begin.*?compute_reduction_index\s*<=\s*compute_reduction_index\s*\+\s*32'd1",
            conv_text,
            re.S,
        ) is not None,
        "conv tile 缺少可用于长 MAC 阶段的真实 reduction 游标",
    )
    require(
        "Start-Process -FilePath $binary" in runner_text
        and "-WindowStyle Hidden" in runner_text
        and "function Test-StartedProcessIdentity" in runner_text
        and "Get-CimInstance -ClassName Win32_Process" in runner_text
        and "$simProcess.Kill()" in runner_text
        and "TotalSeconds -ge 1800" in runner_text
        and "watchdog_no_progress_seconds = 1800" in runner_text
        and "$MaxCycles -gt 4294967295" in runner_text,
        "runner 缺少 process identity watchdog 或 32-bit cycle ceiling",
    )
    for python_path in (
        ROOT / "verification/prepare_s2a_network_backend_golden.py",
        ROOT / "verification/verify_s2a_network_backend_golden.py",
    ):
        compile(python_path.read_text(encoding="utf-8"), str(python_path), "exec")
    watchdog_semantics = verify_progress_watchdog_semantics(runner_text)
    return {
        "source_count": len(source_rows),
        "sources": source_rows,
        "runner_sha256": sha256_file(T68_RUNNER),
        "testbench_sha256": sha256_file(T68_TESTBENCH),
        "verifier_sha256": sha256_file(Path(__file__)),
        "backend_port_set_matches": True,
        "conv_tile_byte_per_request": True,
        "cross_boundary_negative_check": {
            "layer_index": 29,
            "aligned_address": f"0x{cross_boundary_address:08x}",
            "selected_lanes": [0, 2],
            "owners": selected_owners,
            "expected_error": "BAD_RANGE",
        },
        "progress_interval_cycles": 30000000,
        "progress_watchdog_semantics": watchdog_semantics,
        "watchdog_no_progress_seconds": 1800,
        "32_bit_cycle_limit_retained": True,
        "python_syntax": True,
        "simulator_started": False,
    }


def verify(manifest_path: Path) -> dict[str, Any]:
    """核对 T01/T25、descriptor ROM 与已生成 fixture，不写入任何文件。"""
    output_root = manifest_path.absolute().parents[2]
    harness_bindings = verify_harness_bindings()
    manifest = read_json(manifest_path)
    require(manifest.get("schema_version") == "gestureforge_s2a_t68_sample_fixture_v1", "fixture manifest schema 不匹配")
    sample_index = manifest.get("sample_index")
    require(isinstance(sample_index, int) and 0 <= sample_index < EXPECTED_SAMPLE_COUNT, "sample index 不在 0..108")

    pinned_paths = {
        "t01_manifest": T01_MANIFEST,
        "t01_fixed_samples": T01_SAMPLES,
        "t25_index": T25_INDEX,
        "descriptor_package": DESCRIPTOR_PACKAGE,
        "numeric_reference": ROOT / "verification/s1_t02_d2_numeric_reference.py",
        "model_delivery": ROOT / "verification/s2a_model_delivery.py",
    }
    bindings = manifest.get("bindings", {})
    expected_binding_names = {
        "t01_manifest": "t01_manifest",
        "t01_fixed_samples": "t01_samples",
        "t25_index": "t25_index",
        "descriptor_package": "descriptor_package",
        "numeric_reference": "numeric_reference",
        "model_delivery": "model_delivery",
    }
    for binding_name, path in pinned_paths.items():
        expected_hash = PINNED_HASHES[expected_binding_names[binding_name]]
        require(sha256_file(path) == expected_hash, f"仓库 source SHA 不匹配：{path}")
        recorded = bindings.get(binding_name, {})
        require(recorded.get("sha256") == expected_hash, f"fixture manifest source SHA 不匹配：{binding_name}")

    t01_manifest = read_json(T01_MANIFEST)
    fixed_doc = read_json(T01_SAMPLES)
    t25_index = read_json(T25_INDEX)
    t01_row = fixed_doc["samples"][sample_index]
    t25_row = t25_index["samples"][sample_index]
    require(len(fixed_doc.get("samples", [])) == EXPECTED_SAMPLE_COUNT, "T01 样本数不是 109")
    require(len(t25_index.get("samples", [])) == EXPECTED_SAMPLE_COUNT, "T25 样本数不是 109")
    require(manifest.get("sample_id") == t01_row.get("sample_id") == t25_row.get("sample_id"), "sample id 与 T01/T25 不一致")
    require(manifest.get("frame_id") == t01_row.get("frame_id") == t25_row.get("frame_id"), "frame id 与 T01/T25 不一致")

    layer_rows = manifest.get("layers")
    t25_tensors = t25_row.get("network", {}).get("tensors")
    require(isinstance(layer_rows, list) and len(layer_rows) == EXPECTED_LAYER_COUNT, "fixture 层表不完整")
    require(isinstance(t25_tensors, list) and len(t25_tensors) == EXPECTED_LAYER_COUNT, "T25 tensor 层表不完整")
    model_layers = t01_manifest.get("layers", [])
    package_text = DESCRIPTOR_PACKAGE.read_text(encoding="utf-8")
    addresses = parse_descriptor_array(package_text, "S2A_OUTPUT_ADDRESS", 32)
    lengths = parse_descriptor_array(package_text, "S2A_OUTPUT_LENGTH_BYTES", 32)
    write_required = parse_descriptor_array(package_text, "S2A_OUTPUT_MEMORY_WRITE_REQUIRED", 1)
    aliases = parse_descriptor_array(package_text, "S2A_OUTPUT_ALIAS_LAYER_INDEX", 6)

    expected_offsets: dict[int, int] = {}
    cursor = 0
    rebuilt_parts: list[bytes] = []
    for index, (row, tensor) in enumerate(zip(layer_rows, t25_tensors, strict=True)):
        require(row.get("layer_index") == index == tensor.get("layer_index"), f"layer{index} 索引不匹配")
        require(len(model_layers) == EXPECTED_LAYER_COUNT, "T01 manifest 层数不是 38")
        require(row.get("address") == addresses[index] == model_layers[index].get("tensor_address"), f"layer{index} 地址不一致")
        require(row.get("byte_length") == lengths[index] == model_layers[index].get("tensor_length_bytes"), f"layer{index} 长度不一致")
        stored = bool(write_required[index])
        require(row.get("stored") is stored == bool(tensor.get("stored")), f"layer{index} stored 标志不一致")
        alias_index = tensor.get("alias_of_layer_index")
        require(row.get("alias_of_layer_index") == alias_index, f"layer{index} alias 目标不一致")
        if stored:
            require(alias_index is None, f"layer{index} stored tensor 不应 alias")
            require(row.get("golden_stream_offset") == cursor, f"layer{index} golden offset 不连续")
            require(tensor.get("byte_offset") == cursor, f"layer{index} T25 offset 不连续")
            expected_offsets[index] = cursor
            cursor += lengths[index]
        else:
            require(alias_index == aliases[index], f"layer{index} descriptor alias 不匹配")
            require(addresses[index] == addresses[alias_index] and lengths[index] == lengths[alias_index], f"layer{index} alias 地址或长度不匹配")
            require(row.get("golden_stream_offset") is None, f"layer{index} alias 不应占用 golden stream")

    shard_binding = bindings.get("t25_compressed_shard", {})
    shard_path = ROOT.joinpath(*PurePosixPath(shard_binding.get("path", "")).parts)
    shard_raw = shard_path.read_bytes()
    require(sha256_bytes(shard_raw) == shard_binding.get("sha256"), "T25 压缩 shard SHA 与 manifest 不一致")
    require(sha256_file(shard_path) == t25_row["network"]["compressed_shard"]["sha256"], "T25 压缩 shard 与 index 不一致")
    raw_stream = zlib.decompress(shard_raw)
    require(sha256_bytes(raw_stream) == t25_row["network"]["raw_stream_sha256"], "T25 解压 stream SHA 不匹配")
    require(len(raw_stream) == cursor == manifest["golden_unique_stream"]["bytes"], "T25 unique byte count 不匹配")
    for row, tensor in zip(layer_rows, t25_tensors, strict=True):
        if not row["stored"]:
            continue
        begin = tensor["byte_offset"]
        end = begin + tensor["byte_length"]
        tensor_bytes = raw_stream[begin:end]
        require(sha256_bytes(tensor_bytes) == tensor["tensor_sha256"] == row["t25_sha256"], f"layer{row['layer_index']} T25 tensor digest 不匹配")
        rebuilt_parts.append(tensor_bytes)
    golden_raw = b"".join(rebuilt_parts)
    require(sha256_bytes(golden_raw) == manifest["golden_unique_stream"]["sha256"], "重建的 unique golden SHA 不匹配")

    for field in ("input", "weight_package", "golden_unique_stream"):
        item = manifest[field]
        file_path = resolve_output_path(output_root, item["path"])
        require(file_path.is_file(), f"fixture 缺少文件：{file_path}")
        require(file_path.stat().st_size == item["bytes"], f"fixture 文件长度不匹配：{file_path}")
        require(sha256_file(file_path) == item["sha256"], f"fixture 文件 SHA 不匹配：{file_path}")
    input_raw = resolve_output_path(output_root, manifest["input"]["path"]).read_bytes()
    require(manifest["input"]["sha256"] == t01_row["pl_input_sha256"] == t25_row["preprocessed_input"]["sha256"], "input fixture 未同时绑定 T01/T25")
    require(len(input_raw) == t25_row["preprocessed_input"]["raw_bytes"], "input fixture 字节数不匹配")
    require(sha256_bytes(input_raw) == manifest["input"]["sha256"], "input fixture SHA 不匹配")

    weight_binding = t01_manifest["bindings"]["gf8_package"]
    require(manifest["weight_package"]["bytes"] == weight_binding["bytes"], "GF8 长度与 T01 不匹配")
    require(manifest["weight_package"]["sha256"] == weight_binding["sha256"], "GF8 SHA 与 T01 不匹配")
    require(resolve_output_path(output_root, manifest["golden_unique_stream"]["path"]).read_bytes() == golden_raw, "golden fixture 与 T25 bytes 不同")

    return {
        "status": "PASS_OFFLINE_FIXTURE_AND_HARNESS_BINDING_ONLY",
        "sample_index": sample_index,
        "sample_id": manifest["sample_id"],
        "layers": EXPECTED_LAYER_COUNT,
        "stored_tensors": sum(1 for row in layer_rows if row["stored"]),
        "alias_rows": sum(1 for row in layer_rows if not row["stored"]),
        "input_bytes": len(input_raw),
        "unique_golden_bytes": len(golden_raw),
        "fixture_manifest_sha256": sha256_file(manifest_path),
        "harness_bindings": harness_bindings,
        "simulator_started": False,
    }


def main() -> int:
    """执行只读 fixture 验证并打印 JSON 摘要。"""
    parser = argparse.ArgumentParser(description="只读核验 S2A-T68 fixture 与 T01/T25/source 绑定")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "fixtures/sample_000/fixture_manifest.json",
        help="样本夹具 JSON 路径",
    )
    args = parser.parse_args()
    try:
        result = verify(args.manifest.absolute())
    except (OSError, ValueError, KeyError, TypeError, zlib.error) as error:
        print(f"T68 只读验证失败：{error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
