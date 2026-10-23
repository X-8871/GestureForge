"""离线核对S4-B PL G0来源并验证D2量化阈值候选。"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import struct
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree


def _read_json(path: Path) -> dict[str, object]:
    """读取UTF-8 JSON对象。"""
    value = json.loads(path.read_text(encoding="utf-8"))
    if type(value) is not dict:
        raise ValueError(f"JSON顶层必须是对象：{path}")
    return value


def _sha256(path: Path) -> str:
    """计算文件原字节SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _f64_bits(value: float) -> int:
    return struct.unpack("<Q", struct.pack("<d", value))[0]


def _f64_from_bits(value: int) -> float:
    return struct.unpack("<d", struct.pack("<Q", value))[0]


def _d2_quantize_resized_value(reference: object, value: float) -> int:
    """按D2归一化、夹紧及固定scale路径量化插值结果。"""
    normalized = max(0.0, min(1.0, reference._finite(value, "resized_rgb") / 255.0))
    return reference.quantize_symmetric(normalized, reference.INPUT_SCALE)


def _threshold_table(reference: object) -> list[int]:
    """搜索每个输出码的最小非负binary64输入位型。"""
    low_bits = _f64_bits(0.0)
    high_bits = _f64_bits(255.0)
    if _d2_quantize_resized_value(reference, 0.0) != 0:
        raise ValueError("D2零输入未量化为零")
    if _d2_quantize_resized_value(reference, 255.0) != 127:
        raise ValueError("D2最大RGB输入未饱和到127")
    thresholds: list[int] = []
    for code in range(1, 128):
        left, right = low_bits, high_bits
        while left < right:
            middle = (left + right) // 2
            value = _f64_from_bits(middle)
            if _d2_quantize_resized_value(reference, value) >= code:
                right = middle
            else:
                left = middle + 1
        if _d2_quantize_resized_value(reference, _f64_from_bits(left)) != code:
            raise ValueError(f"D2输出码{code}没有独立阈值")
        thresholds.append(left)
    if thresholds != sorted(set(thresholds)):
        raise ValueError("D2量化阈值不严格递增")
    return thresholds


def _threshold_quantize(value: float, thresholds: list[int]) -> int:
    """用有序binary64位型执行阈值下界查找。"""
    if value < 0.0:
        raise ValueError("阈值候选仅适用于非负插值像素")
    bits = _f64_bits(value)
    low, high = 0, len(thresholds)
    while low < high:
        middle = (low + high) // 2
        if thresholds[middle] <= bits:
            low = middle + 1
        else:
            high = middle
    return low


def _parse_hwh(xsa_path: Path) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """从冻结XSA内部读取PS7参数、外部DDR段及器件资源。"""
    with zipfile.ZipFile(xsa_path, "r") as archive:
        hwh = ElementTree.fromstring(archive.read("s2b_inference.hwh"))
        sysdef = ElementTree.fromstring(archive.read("sysdef.xml"))
    params = {
        row.attrib["NAME"]: row.attrib.get("VALUE", "")
        for row in hwh.findall(".//MODULE[@INSTANCE='ps7']//PARAMETER")
        if "NAME" in row.attrib
    }
    segments: dict[str, str] = {}
    for row in hwh.findall(".//MEMRANGE"):
        name = row.attrib.get("INSTANCE", row.attrib.get("NAME", ""))
        segments[name] = f"{row.attrib.get('BASEVALUE', '')}..{row.attrib.get('HIGHVALUE', '')}"
    systeminfo = sysdef.find(".//SYSTEMINFO")
    resources = sysdef.find(".//USEDRESOURCES")
    if systeminfo is None or resources is None:
        raise ValueError("XSA缺少器件或USEDRESOURCES记录")
    device = dict(systeminfo.attrib)
    device["USEDRESOURCES"] = json.dumps(resources.attrib, sort_keys=True)
    return params, segments, device


def _map_region(text: str, name: str) -> tuple[int, int]:
    """读取GNU map的Memory Configuration区域。"""
    match = re.search(rf"(?m)^\s*{re.escape(name)}\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)\s*$", text)
    if match is None:
        raise ValueError(f"链接图缺少内存区：{name}")
    return int(match.group(1), 16), int(match.group(2), 16)


def _overlap(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] < right[1] and right[0] < left[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--xsa", type=Path, required=True)
    parser.add_argument("--platform-json", type=Path, required=True)
    parser.add_argument("--memory-ranges", type=Path, required=True)
    parser.add_argument("--link-map", type=Path, required=True)
    parser.add_argument("--sample-audit", type=Path, required=True)
    parser.add_argument("--r04-utilization", type=Path, required=True)
    parser.add_argument("--r04-timing", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    paths = {
        name: path.resolve(strict=True)
        for name, path in vars(args).items()
        if name not in {"output"}
    }
    output = args.output.resolve(strict=False)
    if output.exists():
        raise FileExistsError(f"拒绝覆盖证据文件：{output}")
    reference_path = paths["reference"]
    sys.path.insert(0, str(reference_path.parent))
    import s1_t02_d2_numeric_reference as d2

    if Path(d2.__file__).resolve(strict=True) != reference_path:
        raise RuntimeError("D2导入路径与显式绑定文件不一致")

    params, segments, device = _parse_hwh(paths["xsa"])
    platform = _read_json(paths["platform_json"])
    memory = platform["memory"]
    ranges = _read_json(paths["memory_ranges"])
    samples = _read_json(paths["sample_audit"])
    map_text = paths["link_map"].read_text(encoding="utf-8", errors="strict")
    app_map = _map_region(map_text, "ps7_ddr_0_memory_0")
    tensor_map = _map_region(map_text, "s2b_tensor_ddr")

    sample_count = int(samples["sample_count"])
    max_raw = int(samples["packed_raw_max_bytes"])
    max_dimensions = [1920, 1920]
    if max_dimensions[0] * max_dimensions[1] * 3 != max_raw:
        raise ValueError("已绑定样本审计的最大帧尺寸与packed RGB888字节数不一致")

    raw_region_bytes = 12 * 1024 * 1024
    mailbox_region_bytes = 32 * 1024
    candidate_raw = (0x12000000, 0x12000000 + raw_region_bytes)
    candidate_mailbox = (candidate_raw[1], candidate_raw[1] + mailbox_region_bytes)
    known_reserved = {
        "ps_app_arena": (int(ranges["ps_app_arena"]["start"]), int(ranges["ps_app_arena"]["end_exclusive"])),
        "s2b_tensor_arena": (int(ranges["s2b_tensor_arena"]["start"]), int(ranges["s2b_tensor_arena"]["end_exclusive"])),
    }
    ddr_base = int(params["PCW_DDR_RAM_BASEADDR"], 16)
    ddr_end = int(params["PCW_DDR_RAM_HIGHADDR"], 16) + 1
    ddr_range = (ddr_base, ddr_end)
    candidate_range_ok = (
        ddr_range[0] <= candidate_raw[0] < candidate_raw[1] <= ddr_range[1]
        and candidate_mailbox[0] < candidate_mailbox[1] <= ddr_range[1]
        and all(not _overlap(candidate_raw, reserved) and not _overlap(candidate_mailbox, reserved)
                for reserved in known_reserved.values())
        and candidate_raw[0] >= int(memory["arena_end_exclusive"], 16)
    )

    thresholds = _threshold_table(d2)
    checked = 0
    boundary_checks = 0

    def check_value(value: float) -> None:
        nonlocal checked
        expected = _d2_quantize_resized_value(d2, value)
        actual = _threshold_quantize(value, thresholds)
        if actual != expected:
            raise AssertionError(f"阈值表不等价：value={value.hex()} expected={expected} actual={actual}")
        checked += 1

    for index, bits in enumerate(thresholds):
        for delta in (-2, -1, 0, 1, 2):
            check_value(_f64_from_bits(bits + delta))
            boundary_checks += 1
        code = index + 1
        if (_threshold_quantize(_f64_from_bits(bits - 1), thresholds) != code - 1 or
                _threshold_quantize(_f64_from_bits(bits), thresholds) != code):
            raise AssertionError(f"阈值{code}相邻位型边界不符")

    for code in range(256):
        check_value(float(code))
        if code < 255:
            check_value(code + 0.5)
            check_value(math.nextafter(code + 0.5, -math.inf))
            check_value(math.nextafter(code + 0.5, math.inf))

    rng = random.Random(20261023)
    random_count = 100_000
    low_bits, high_bits = _f64_bits(0.0), _f64_bits(255.0)
    for _ in range(random_count):
        check_value(_f64_from_bits(rng.randrange(low_bits, high_bits + 1)))

    coeff_entry_bytes = 20
    coeff_entry_count_max = 2 * 416
    coeff_bytes_max = coeff_entry_bytes * coeff_entry_count_max
    descriptor_bytes = 128
    memory_traffic = max_raw + 2 * 519_168
    output_channels = 416 * 416 * 3
    arithmetic_ops_per_channel = 9
    threshold_cycles_per_channel = 7
    ideal_cycles = output_channels * (arithmetic_ops_per_channel + threshold_cycles_per_channel)
    result: dict[str, object] = {
        "schema_version": 1,
        "status": "OFFLINE_G0_BASIS_PROBE_PASS_NOT_G0_APPROVAL",
        "hardware": "NOT_RUN",
        "vivado_or_synthesis": "NOT_RUN",
        "source_bindings": {
            name: {"path": str(path), "sha256": _sha256(path), "bytes": path.stat().st_size}
            for name, path in paths.items()
        },
        "d2_threshold_candidate": {
            "source_semantics": "binary64 resized 0..255 -> clamp(fl(value/255.0),0,1) -> frozen D2 fixed-scale quantizer",
            "threshold_count": len(thresholds),
            "threshold_hex_bits": [f"0x{value:016x}" for value in thresholds],
            "threshold_rom_bytes": len(thresholds) * 8,
            "binary_search_comparisons_max": math.ceil(math.log2(len(thresholds) + 1)),
            "boundary_neighbor_checks": boundary_checks,
            "integer_and_half_step_checks": 256 + 255 * 3,
            "random_bit_pattern_checks": random_count,
            "total_direct_equivalence_checks": checked,
            "random_seed": 20261023,
            "scope": "仅验证单调binary64插值结果到D2 INT8的精确阈值映射；不验证PL浮点运算实现。",
            "proof_obligation": "直接D2映射在非负binary64有序位型上单调；每个码的下界通过位型二分精确定位。阈值邻居和随机测试是附加检查，不替代形式证明或RTL对拍。",
        },
        "xsa_ps_ddr": {
            "xsa_sha256": _sha256(paths["xsa"]),
            "part": device.get("PART"),
            "generated_used_resources": json.loads(device["USEDRESOURCES"]),
            "pcw_ddr_base": f"0x{ddr_base:08x}",
            "pcw_ddr_high_inclusive": f"0x{ddr_end - 1:08x}",
            "pcw_ddr_aperture_bytes": ddr_end - ddr_base,
            "pcw_ddr_device_capacity": params.get("PCW_UIPARAM_DDR_DEVICE_CAPACITY"),
            "pcw_ddr_bus_width": params.get("PCW_UIPARAM_DDR_BUS_WIDTH"),
            "pcw_ddr_dram_width": params.get("PCW_UIPARAM_DDR_DRAM_WIDTH"),
            "pcw_ddr_part": params.get("PCW_UIPARAM_DDR_PARTNO"),
            "pcw_ddr_freq_mhz": params.get("PCW_UIPARAM_DDR_FREQ_MHZ"),
            "pcw_hp0_data_width": params.get("PCW_S_AXI_HP0_DATA_WIDTH"),
            "pcw_hp0_freq_mhz": params.get("PCW_S_AXI_HP0_FREQMHZ"),
            "xsa_segments": segments,
            "interpretation_limit": "XSA为Vivado设计配置且BOARD为空；不证明当前PCB实装/温度等级/板上DDR训练。",
        },
        "address_candidate": {
            "candidate_only": True,
            "existing_linker_ps_app_region": {"base": f"0x{app_map[0]:08x}", "length": f"0x{app_map[1]:x}"},
            "existing_linker_tensor_region": {"base": f"0x{tensor_map[0]:08x}", "length": f"0x{tensor_map[1]:x}"},
            "existing_s2b_tensor_arena": {
                "base": memory["arena_base"], "end_exclusive": memory["arena_end_exclusive"],
                "direct_hp0": memory["direct_hp0"], "axcache": memory["axcache"],
            },
            "known_reserved_ranges": {
                name: {"base": f"0x{start:08x}", "end_exclusive": f"0x{end:08x}"}
                for name, (start, end) in known_reserved.items()
            },
            "raw_region": {"base": f"0x{candidate_raw[0]:08x}", "end_exclusive": f"0x{candidate_raw[1]:08x}",
                           "bytes": raw_region_bytes, "frame_bytes_at_packed_max": max_raw,
                           "frame_slack_bytes": raw_region_bytes - max_raw,
                           "max_stride_for_1920_rows_if_64B_aligned": (raw_region_bytes // 1920 // 64) * 64},
            "mailbox_region": {"base": f"0x{candidate_mailbox[0]:08x}",
                                "end_exclusive": f"0x{candidate_mailbox[1]:08x}",
                                "bytes": mailbox_region_bytes,
                                "coefficient_table_bytes_max": coeff_bytes_max,
                                "descriptor_bytes_candidate": descriptor_bytes},
            "candidate_within_configured_aperture_and_known_ranges": candidate_range_ok,
            "known_aperture_limit": {"base": f"0x{ddr_range[0]:08x}", "end_exclusive": f"0x{ddr_range[1]:08x}"},
            "warning": "未审计其他固件/显示/PS运行时保留区；地址仍待系统G0与Vivado地址图审查，不可用于构建或写入。",
        },
        "resource_and_ideal_cycle_basis": {
            "device_totals": {"lut": int(device.get("LUT", "0")), "ff": int(device.get("FF", "0")),
                              "bram36_tiles": int(device.get("BRAM", "0")), "dsp48e1": int(device.get("DSP", "0"))},
            "r04_used_resources": json.loads(device["USEDRESOURCES"]),
            "r04_routed_timing_summary_sha256": _sha256(paths["r04_timing"]),
            "r04_utilization_report_sha256": _sha256(paths["r04_utilization"]),
            "line_buffer_capacity_lower_bound": {
                "bytes": 2 * 1920 * 3, "bits": 2 * 1920 * 3 * 8,
                "bram36_capacity_bits": 36864,
                "minimum_bram36_tiles_by_capacity": math.ceil(2 * 1920 * 3 * 8 / 36864),
                "actual_mapping_status": "UNMEASURED; ports/banking/packing may need more",
            },
            "shared_53x53_multiplier_dsp_decomposition_candidate": {
                "18bit_partials": math.ceil(53 / 18) ** 2,
                "fraction_of_r04_remaining_dsp": math.ceil(53 / 18) ** 2 / (int(device.get("DSP", "0")) - int(json.loads(device["USEDRESOURCES"])["DSP"])),
                "status": "ARITHMETIC_LOWER_BOUND_ONLY; no synthesis or timing result",
            },
            "one_shared_f64_alu_ideal_cycles_per_channel": arithmetic_ops_per_channel,
            "output_channels_per_frame": output_channels,
            "threshold_search_cycles_per_channel": threshold_cycles_per_channel,
            "ideal_serial_cycles_per_frame": ideal_cycles,
            "ideal_serial_time_at_xsa_50MHz_ms": ideal_cycles / 50_000,
            "ideal_time_limit": "仅一操作/周期且无流水气泡、DDR等待/背压、初始化与控制；不是实测或批准性能门槛。",
            "payload_bytes_lower_estimate": {
                "max_stride_raw_read": max_raw,
                "preprocessor_tensor_write": 519_168,
                "network_tensor_read": 519_168,
                "sum_excluding_coefficients_weights_features_heads_and_protocol": memory_traffic,
            },
        },
        "sample_scope": {
            "sample_count": sample_count,
            "packed_raw_max_bytes": max_raw,
            "over_4mib_count": len(samples["over_4MiB"]),
            "over_8mib_count": len(samples["over_8MiB"]),
            "limitations": samples["limitations"],
        },
        "decision": "路线可进入独立数值核开发；完整HP0接入仍需系统G0、位流/链接图、资源与时序审查。",
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    result["canonical_result_sha256"] = hashlib.sha256(canonical).hexdigest()
    output.parent.mkdir(parents=False, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({
        "status": result["status"], "output": str(output),
        "d2_thresholds": len(thresholds), "d2_equivalence_checks": checked,
        "raw_region": result["address_candidate"]["raw_region"],
        "mailbox_region": result["address_candidate"]["mailbox_region"],
        "candidate_range_ok": candidate_range_ok,
        "ideal_serial_ms": result["resource_and_ideal_cycle_basis"]["ideal_serial_time_at_xsa_50MHz_ms"],
        "hardware": "NOT_RUN", "synthesis": "NOT_RUN",
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
