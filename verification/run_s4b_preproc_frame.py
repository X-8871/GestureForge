"""为 S4-B 整帧 PL 离线仿真生成独立 D2 输入、黄金结果与 Tcl。"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import struct
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_ROOT = REPO_ROOT / "tmp" / "4" / "S4B-PL-FRAME-01"
EXPECTED_D2_SHA256 = "6a3453d5bd60ab122c236667fbc9bcb5aa161d14b76bc7115b602743d5cbe54f"
EXPECTED_GEOMETRY_BASE = "e1e79fcfcedd653681336e45c323de6ba3ed5558"
EXPECTED_NUMERIC_BASE = "c9bab114d535191ae2dc2ef8bdcd087f15ed672a"
MEMORY_WORDS = 130_000
OUTPUT_W = 4
OUTPUT_H = 4
LARGE_OUTPUT_W = 416
LARGE_OUTPUT_H = 416


def _sha256(path: Path) -> str:
    """计算文件原始字节的 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_module(name: str, path: Path) -> Any:
    """按精确路径导入一个本地 Python 模块。"""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_d2() -> tuple[Any, str]:
    """核验冻结 D2 源码后加载其独立标量参考。"""
    path = REPO_ROOT / "verification" / "s1_t02_d2_numeric_reference.py"
    source_hash = _sha256(path)
    if source_hash != EXPECTED_D2_SHA256:
        raise ValueError(f"冻结 D2 源 SHA 不匹配：{source_hash}")
    return _load_module("s4b_frame_frozen_d2", path), source_hash


def _load_geometry_builder() -> tuple[Any, str]:
    """加载已冻结的几何元数据生成器并记录其源码摘要。"""
    path = REPO_ROOT / "scripts" / "stage4_s4b" / "build_s4b_preproc_geometry.py"
    module = _load_module("s4b_frame_geometry_builder", path)
    return module, _sha256(path)


def _make_pixels(width: int, height: int, salt: int) -> list[list[list[int]]]:
    """构造可复现的小型 RGB 输入图。"""
    return [
        [
            [
                (31 * x + 47 * y + 73 * channel + 19 * x * y + salt) & 0xFF
                for channel in range(3)
            ]
            for x in range(width)
        ]
        for y in range(height)
    ]


def _large_boundary_pixels() -> list[list[list[int]]]:
    """构造任务指定的 202×329 首行量化边界输入。"""
    pixels = [[[0, 0, 0] for _ in range(202)] for _ in range(329)]
    pixels[0][0][0] = 201
    pixels[0][1][0] = 202
    pixels[1][0][0] = 201
    pixels[1][1][0] = 202
    return pixels


def _geometry_entries(
    builder: Any,
    source_width: int,
    source_height: int,
    output_width: int,
    output_height: int,
) -> tuple[dict[str, Any], bytes, bytes]:
    """使用冻结生成器构造定长、未使用项为零的轴表。"""
    metadata = builder.build_s4b_preproc_geometry(
        source_width,
        source_height,
        output_width,
        output_height,
    )
    axis_blobs: list[bytes] = []
    for axis_name, slot_count in (("x", output_width), ("y", output_height)):
        entries = metadata["axes"][axis_name]["entries"]
        if len(entries) > slot_count:
            raise ValueError(f"{axis_name} 活动几何项超过表容量")
        blob = bytearray(slot_count * 24)
        for index, entry in enumerate(entries):
            index_word = int(entry["i0"]) | (int(entry["i1"]) << 32)
            weight0 = int(entry["w0bits"], 16)
            weight1 = int(entry["w1bits"], 16)
            struct.pack_into("<QQQ", blob, index * 24, index_word, weight0, weight1)
        axis_blobs.append(bytes(blob))
    return metadata, axis_blobs[0], axis_blobs[1]


def _make_case(
    *,
    name: str,
    pixels: list[list[list[int]]],
    output_width: int,
    output_height: int,
    raw_base: int,
    xgeom_base: int,
    ygeom_base: int,
    tensor_base: int,
    session_id: int,
    frame_id: int,
    d2: Any,
    builder: Any,
) -> dict[str, Any]:
    """生成一例描述符、原始字节、几何表及直接 D2 结果。"""
    source_height = len(pixels)
    source_width = len(pixels[0])
    geometry, x_table, y_table = _geometry_entries(
        builder, source_width, source_height, output_width, output_height
    )
    resized_width = int(geometry["new_size"]["width"])
    resized_height = int(geometry["new_size"]["height"])
    pad_left = int(geometry["padding"]["left"])
    pad_top = int(geometry["padding"]["top"])
    stride = source_width * 3
    logical = stride * source_height
    storage = (logical + 7) & ~7
    raw = bytes(channel for row in pixels for pixel in row for channel in pixel)
    raw += bytes(storage - len(raw))
    chw = d2.preprocess_rgb_uint8_to_chw_int8(pixels, output_width, output_height)
    expected = bytes(value & 0xFF for channel in chw for row in channel for value in row)
    if len(expected) != output_width * output_height * 3:
        raise AssertionError("独立 D2 黄金输出长度错误")
    return {
        "name": name,
        "pixels": pixels,
        "raw": raw,
        "x_table": x_table,
        "y_table": y_table,
        "expected": expected,
        "descriptor": [
            source_width,
            source_height,
            stride,
            logical,
            storage,
            storage,
            resized_width,
            resized_height,
            pad_left,
            pad_top,
            raw_base,
            xgeom_base,
            ygeom_base,
            tensor_base,
            session_id,
            frame_id,
        ],
        "geometry": geometry,
    }


def _write_hex_words(path: Path, content: bytes) -> None:
    """按小端 64 位字写入完整仿真内存镜像。"""
    with path.open("w", encoding="ascii", newline="\n") as stream:
        for offset in range(0, len(content), 8):
            stream.write(f"{int.from_bytes(content[offset:offset + 8], 'little'):016x}\n")


def _write_hex_bytes(path: Path, content: bytes) -> None:
    """逐字节写入十六进制黄金文件。"""
    path.write_text("".join(f"{value:02x}\n" for value in content), encoding="ascii", newline="\n")


def build_fixtures(output_dir: Path) -> dict[str, Any]:
    """生成三例固定向量及离线验证清单。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    d2, d2_hash = _load_d2()
    builder, builder_hash = _load_geometry_builder()
    memory = bytearray(MEMORY_WORDS * 8)
    cases = [
        _make_case(
            name="same_size_4x4",
            pixels=_make_pixels(4, 4, 23),
            output_width=OUTPUT_W,
            output_height=OUTPUT_H,
            raw_base=0x1000,
            xgeom_base=0x2000,
            ygeom_base=0x3000,
            tensor_base=0x4000,
            session_id=0x53420001,
            frame_id=1,
            d2=d2,
            builder=builder,
        ),
        _make_case(
            name="axis_one_letterbox_1x3_to_4x4",
            pixels=_make_pixels(1, 3, 71),
            output_width=OUTPUT_W,
            output_height=OUTPUT_H,
            raw_base=0x8000,
            xgeom_base=0x9000,
            ygeom_base=0xA000,
            tensor_base=0xB000,
            session_id=0x53420002,
            frame_id=2,
            d2=d2,
            builder=builder,
        ),
        _make_case(
            name="boundary_202x329_to_416_prefix",
            pixels=_large_boundary_pixels(),
            output_width=LARGE_OUTPUT_W,
            output_height=LARGE_OUTPUT_H,
            raw_base=0x10000,
            xgeom_base=0x50000,
            ygeom_base=0x60000,
            tensor_base=0x70000,
            session_id=0x53420003,
            frame_id=3,
            d2=d2,
            builder=builder,
        ),
    ]

    for case in cases:
        descriptor = case["descriptor"]
        raw_base, raw = descriptor[10], case["raw"]
        x_base, x_table = descriptor[11], case["x_table"]
        y_base, y_table = descriptor[12], case["y_table"]
        for base, data in ((raw_base, raw), (x_base, x_table), (y_base, y_table)):
            end = base + len(data)
            if end > len(memory):
                raise ValueError(f"fixture memory image too small: {case['name']} @0x{base:x}")
            memory[base:end] = data

    expected_large = cases[2]["expected"][:88]
    if expected_large[81] != 100:
        raise AssertionError(f"D2 x=81 边界值应为100，实际为{expected_large[81]}")
    if expected_large[:80] != bytes([64] * 80):
        raise AssertionError("大尺寸样例首80个padding字节必须量化为64")

    _write_hex_words(output_dir / "memory.hex", bytes(memory))
    with (output_dir / "descriptor.hex").open("w", encoding="ascii", newline="\n") as stream:
        for case in cases:
            for value in case["descriptor"]:
                stream.write(f"{value:08x}\n")
    _write_hex_bytes(output_dir / "expected_small_same.hex", cases[0]["expected"])
    _write_hex_bytes(output_dir / "expected_small_axis1.hex", cases[1]["expected"])
    _write_hex_bytes(output_dir / "expected_large_prefix88.hex", expected_large)

    manifest = {
        "task": "S4B-PL-FRAME-01",
        "status": "FIXTURES_PREPARED_NOT_SIMULATED",
        "geometry_base": EXPECTED_GEOMETRY_BASE,
        "numeric_base": EXPECTED_NUMERIC_BASE,
        "d2_reference_sha256": d2_hash,
        "geometry_builder_sha256": builder_hash,
        "cases": [
            {
                "name": case["name"],
                "descriptor": case["descriptor"],
                "source_size": case["geometry"]["source_size"],
                "output_size": case["geometry"]["destination_size"],
                "new_size": case["geometry"]["new_size"],
                "padding": case["geometry"]["padding"],
                "expected_bytes": len(case["expected"]),
                "expected_sha256": hashlib.sha256(case["expected"]).hexdigest(),
            }
            for case in cases
        ],
        "boundary_prefix": {
            "bytes": len(expected_large),
            "padding_bytes": 80,
            "x81_value": expected_large[81],
            "sha256": hashlib.sha256(expected_large).hexdigest(),
        },
        "memory_words": MEMORY_WORDS,
        "memory_sha256": _sha256(output_dir / "memory.hex"),
        "descriptor_file_sha256": _sha256(output_dir / "descriptor.hex"),
        "limits": [
            "此产物是仿真fixture，不包含真实物理DDR地址或板测证据",
            "大图仅比较通道0首行88字节，随后受控abort",
            "Python黄金由SHA绑定的冻结D2标量函数直接生成",
        ],
    }
    (output_dir / "fixtures.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def _tcl_path(path: Path) -> str:
    """返回用于 Tcl 花括号字面量的正斜杠绝对路径。"""
    value = str(path.resolve()).replace("\\", "/")
    if "}" in value or "{" in value or "\n" in value or "\r" in value:
        raise ValueError("Tcl路径包含不支持的花括号或换行")
    return value


def write_simulation_tcl(run_dir: Path, vector_dir: Path) -> Path:
    """写入有界 Vivado/XSim 仿真脚本。"""
    sim_dir = run_dir / "vivado_project"
    temp_dir = run_dir / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    sim_dir.mkdir(parents=True, exist_ok=True)
    run_tcl = run_dir / "run_frame_xsim.tcl"
    source_rtl = REPO_ROOT / "src" / "s4b_preproc_fp64.sv"
    source_pixel = REPO_ROOT / "src" / "s4b_preproc_pixel.sv"
    source_frame = REPO_ROOT / "src" / "s4b_preproc_frame.sv"
    testbench = REPO_ROOT / "sim" / "tb_s4b_preproc_frame.sv"
    content = f"""set ::env(TEMP) {{{_tcl_path(temp_dir)}}}
set ::env(TMP) {{{_tcl_path(temp_dir)}}}
set ::env(TMPDIR) {{{_tcl_path(temp_dir)}}}
create_project s4b_frame_project {{{_tcl_path(sim_dir)}}} -part xc7z020clg400-2
set_property target_simulator XSim [current_project]
add_files -fileset sources_1 [list {{{_tcl_path(source_rtl)}}} {{{_tcl_path(source_pixel)}}} {{{_tcl_path(source_frame)}}}]
add_files -fileset sim_1 {{{_tcl_path(testbench)}}}
set_property top tb_s4b_preproc_frame [get_filesets sim_1]
set_property -name {{xsim.simulate.xsim.more_options}} -value {{-testplusarg VEC_DIR={_tcl_path(vector_dir)}}} -objects [get_filesets sim_1]
set_property xsim.simulate.runtime 5ms [get_filesets sim_1]
update_compile_order -fileset sources_1
update_compile_order -fileset sim_1
launch_simulation -simset sim_1 -mode behavioral
run all
"""
    run_tcl.write_text(content, encoding="utf-8", newline="\n")
    return run_tcl


def _validate_run_dir(run_dir: Path) -> None:
    """要求产物位于本工作树唯一任务目录下。"""
    selected = run_dir.resolve(strict=False)
    expected_parent = TASK_ROOT.resolve(strict=True)
    if selected.parent != expected_parent or not selected.name:
        raise ValueError(f"Run目录必须是任务专属目录的直接子目录：{expected_parent}")
    if not selected.exists() or not selected.is_dir():
        raise ValueError(f"Run目录必须已由调用者创建：{selected}")


def main(argv: list[str] | None = None) -> int:
    """生成fixture并写出MCP Tcl脚本，不启动硬件或Vivado。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        _validate_run_dir(args.run_dir)
        vector_dir = args.run_dir / "vectors"
        if vector_dir.exists():
            raise FileExistsError(f"fixture目录已存在，禁止覆盖：{vector_dir}")
        manifest = build_fixtures(vector_dir)
        tcl_path = write_simulation_tcl(args.run_dir, vector_dir)
        result = {
            "status": "PREPARED",
            "run_dir": str(args.run_dir.resolve()),
            "vector_dir": str(vector_dir.resolve()),
            "run_tcl": str(tcl_path.resolve()),
            "fixture_manifest": manifest,
        }
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, RuntimeError, AssertionError) as exc:
        print(f"FRAME_PREPARE_FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
