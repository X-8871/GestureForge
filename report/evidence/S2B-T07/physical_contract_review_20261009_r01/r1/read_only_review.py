import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time


# 独立只读计算和包装核查；仅向本审查隔离目录写入结果。
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
T07 = "report/evidence/S2B-T07/physical_contract_20261009_r01"
T06 = "report/evidence/S2B-T06/serial_port_recheck_20261009_225453_r01"
EXPECTED = {
    ".codex/STATE.md": "4d5f425d2f87ef09a43fc7ddfc6c91f80b494016c19acff1a193b9b820226276",
    ".gitattributes": "6c9162bcb5672e8c97ade6836dc210e4c61cce90dea3e30c91a160003c68470c",
    "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md": "e14ea46239d987336ea0ee53afb962b77733626294447c47b7f06f158dc06242",
    "docs/obsidian-project/02-方案设计/系统设计.md": "2e2589afc37defbd48b023635f3755fe1a267c4613375559518951e5dc78408e",
    f"{T07}/delivery_manifest.json": "635c148b8e653c78aeec6ac6122f5c22e966f24d7777d9bf44ebe9945b024d3d",
    f"{T07}/layout_result.json": "34bc0b1aa4a632ad4fdabd5154ee181ab3f3a7708cafff2968a863263a2f7b1f",
    f"{T06}/delivery_manifest.json": "478df7054e4cdabe079f67e6b58ef859b1529db8bdac7929d5414a04b899ff67",
}


def exact_file(relative):
    current = ROOT
    for part in Path(relative).parts:
        if part not in {p.name for p in current.iterdir()}:
            raise ValueError(f"路径字符不存在：{relative}")
        current = current / part
    if not current.is_file() or current.is_symlink():
        raise ValueError(f"目标不是普通文件：{relative}")
    return current


def sha(relative):
    return hashlib.sha256(exact_file(relative).read_bytes()).hexdigest()


def read_json(relative):
    return json.loads(exact_file(relative).read_text(encoding="utf-8"))


def save(name, value):
    path = OUT / name
    if path.exists():
        raise ValueError(f"审查输出已经存在：{name}")
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


start = time.perf_counter()
baseline = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
assert baseline == "3f6e327a0ff9adc04ed6c98c1578862b8c2fae64"
bindings = []
for relative, expected in EXPECTED.items():
    actual = sha(relative)
    bindings.append({"path": relative, "sha256": actual, "expected": expected, "match": actual == expected})
assert all(row["match"] for row in bindings)
manifest_hashes = []
for run in (T07, T06):
    for row in read_json(f"{run}/delivery_manifest.json")["files"]:
        actual = sha(row["path"])
        manifest_hashes.append({"path": row["path"], "match": actual == row["sha256"]})
assert all(row["match"] for row in manifest_hashes)
snapshot_bindings = read_json(f"{T07}/source_snapshot_bindings.json")["files"]
for row in snapshot_bindings:
    assert sha(row["original_path"]) == sha(row["snapshot_path"]) == row["sha256"]

model = read_json("report/evidence/S2A-T01/tiny416_model_manifest.json")
assert sha("report/evidence/S2A-T01/tiny416_model_manifest.json") == "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
independent = []
aliases = []
weights = []
for row in model["layers"]:
    length = math.prod(row["output_shape_nchw"])
    assert length == row["tensor_length_bytes"]
    address = row["tensor_address"]
    if row["op"] == "yolo":
        source = model["layers"][row["output_tensor_index"]]
        assert (address, length) == (source["tensor_address"], source["tensor_length_bytes"])
        aliases.append(row["layer_index"])
    else:
        assert address % 64 == 0
        independent.append((address, address + length, row["layer_index"]))
    if row["op"] == "convolutional":
        oc = row["output_shape_nchw"][1]
        raw_length = oc * row["input_shape_nchw"][1] * math.prod(row["kernel_hw"]) // row["groups"]
        gf = row["gf8_parameter_offsets"]
        assert gf["quantized_weight_bytes"] == raw_length
        assert gf["weight_scale_offset"] == gf["record_offset"] + 32
        assert gf["fused_bias_offset"] == gf["weight_scale_offset"] + oc * 4
        assert gf["quantized_weight_offset"] == gf["fused_bias_offset"] + oc * 4
        weights.append((gf["record_offset"], gf["quantized_weight_offset"] + raw_length, raw_length, oc))
independent.sort()
gaps = []
cursor = 0x01000000
for low, high, layer in independent:
    assert low >= cursor
    if low > cursor:
        gaps.append({"start": cursor, "end_exclusive": low, "bytes": low - cursor})
    cursor = high
assert cursor == model["address_map"]["feature_workspace"]["end_address_exclusive"]
weights.sort()
package_cursor = 28
for record, end, count, channels in weights:
    assert record == package_cursor
    package_cursor = end
assert package_cursor == model["address_map"]["weight_package"]["length_bytes"]
head_rows = []
for head in model["address_map"]["heads"]:
    end = head["address"] + head["length_bytes"]
    aligned = (end - 1) // 4 * 4
    legal_lanes = [lane for lane in range(4) if aligned + lane < end]
    head_rows.append({"address": head["address"], "length": head["length_bytes"], "end": end, "last_word": aligned, "last_mask": sum(1 << lane for lane in legal_lanes), "physical_end": 0x10000000 + end})
total = sum(high - low for low, high, _ in independent)
calc = {
    "allocated_features": len(independent), "yolo_aliases": aliases,
    "conv_records": len(weights), "feature_bytes": total,
    "feature_span": cursor - 0x01000000, "feature_gaps": gaps,
    "gf8_bytes": package_cursor, "weight_payload": sum(row[2] for row in weights),
    "input_bytes": 416 * 416 * 3,
    "effective_objects": total + package_cursor + 416 * 416 * 3,
    "arena_span": cursor, "arena_tail": 0x02000000 - cursor,
    "feature_cache_start": 0x11000000,
    "feature_cache_end": 0x10000000 + (cursor + 63) // 64 * 64,
    "feature_cache_length": (cursor + 63) // 64 * 64 - 0x01000000,
    "heads": head_rows, "max_timeout_seconds_50MHz": 0xFFFFFFFF / 50_000_000,
    "write_service_integer_limit": 0xFFFFFFFF // total,
    "physical_64bit_lane_formulas": {
        "aligned_word_lower_half": {"address_low3": 0, "data_shift": 0, "mask_shift": 0},
        "aligned_word_upper_half": {"address_low3": 4, "data_shift": 32, "mask_shift": 4},
        "byte_read": "数据选择physical_address低3bit对应byte，再放回logical_lane；未选lane为0",
    },
}
developer = read_json(f"{T07}/layout_result.json")
for lhs, rhs in (("allocated_features", "allocated_feature_count"), ("conv_records", "convolution_count"), ("feature_bytes", "feature_effective_bytes"), ("feature_span", "feature_span_bytes"), ("gf8_bytes", "gf8_package_bytes"), ("weight_payload", "gf8_weight_payload_bytes"), ("effective_objects", "input_gf8_feature_effective_bytes"), ("arena_span", "translated_used_span_bytes"), ("arena_tail", "arena_unused_tail_bytes"), ("feature_cache_length", "feature_cache_length")):
    assert calc[lhs] == developer["totals"][rhs]
assert head_rows[0]["last_mask"] == 3 and head_rows[1]["last_mask"] == 15

raw = json.loads(exact_file(f"{T06}/enumeration.stdout.log").read_text(encoding="utf-8-sig"))
result = read_json(f"{T06}/port_result.json")
assert raw == result["observation"]
old = read_json("report/evidence/S2B-T06/ps_uart_clock_retest_20261009_172557_r01/uart_capture_identity.json")
assert old["port"] == result["selected_port"] == "COM4"
assert old["port_pnp_id"] == result["expected_pnp"]
assert raw["serial_devices"][0]["PNPDeviceID"] == old["port_pnp_id"]
assert raw["com_devices"][0]["ConfigManagerErrorCode"] == 0
assert read_json(f"{T06}/execution.json")["exit_code"] == 0
assert read_json(f"{T06}/collector_failure.json")["exit_code"] == 1

commands = []
env = dict(os.environ, PYTHONIOENCODING="utf-8")
for run, mode, expected in ((T07, "evidence", 0), (T07, "inputs", 2), (T06, "evidence", 0), (T06, "inputs", 2)):
    argv = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", mode, "--manifest", f"{run}/delivery_manifest.json"]
    before = time.perf_counter()
    observed = subprocess.run(argv, cwd=ROOT, capture_output=True, env=env)
    key = ("t07" if run == T07 else "t06") + "_" + mode
    log = OUT / (key + "_r02.log")
    assert not log.exists()
    log.write_bytes(observed.stdout + observed.stderr)
    commands.append({"argv": argv, "exit_code": observed.returncode, "expected_exit_code": expected, "elapsed_seconds": time.perf_counter() - before, "log_path": str(log), "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest()})
    assert observed.returncode == expected
save("independent_facts.json", {"source_commit": baseline, "fixed_bindings": bindings, "manifest_files_checked": manifest_hashes, "source_snapshot_count": len(snapshot_bindings), "independent_layout": calc, "serial_read_only_identity_match": True, "commands": commands, "elapsed_seconds": time.perf_counter() - start, "scope": "只读公式、文件绑定及包装核查；无RTL/软件测试及硬件操作"})
print(json.dumps({"status": "INDEPENDENT_READ_ONLY_FACTS_OK", "files": len(manifest_hashes), "feature_bytes": total, "checker_exit_codes": [row["exit_code"] for row in commands]}, ensure_ascii=False))
