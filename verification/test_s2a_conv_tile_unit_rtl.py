"""以冻结 T17 查询验证新 tile 算术路径；不覆盖内存调度或整层遍历。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import time

import test_s2a_conv_engine_rtl as oracle

ROOT = Path(__file__).resolve().parents[1]
HEADER = struct.Struct("<8I")
LANE = struct.Struct("<iB")
SOURCES = ("src/s2a_network_descriptor_pkg.sv", "src/s2a_conv_tile_engine.sv",
           "sim/tb_s2a_conv_tile_unit.sv")


def sha(path: Path) -> str:
    """计算当前文件的精确字节摘要。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geometry(layer: dict, channel: int, row: int, col: int) -> dict:
    """计算真实描述符内的起始 tile、尾组与所选点。"""
    _, channels, height, width = layer["output_shape_nchw"]
    if not (0 <= channel < channels and 0 <= row < height and 0 <= col < width):
        raise ValueError("查询越界")
    ty, tx, group = row // 8 * 8, col // 8 * 8, channel // 8 * 8
    th, tw = min(8, height - ty), min(8, width - tx)
    return {"tile_y": ty, "tile_x": tx, "tile_height": th, "tile_width": tw,
            "group": group, "lanes": min(8, channels - group),
            "point": (row - ty) * tw + col - tx}


def prepare(work: Path) -> dict:
    """只从已绑定模型参数生成查询；不访问网络图片或运行证据。"""
    manifest, proof, weights, package = oracle._load_bound_inputs()
    historical = json.loads((ROOT / "report/evidence/S2A-T17/conv_engine_simulation.json").read_text(encoding="utf-8"))
    if historical["result"] != "PASS":
        raise ValueError("历史 T17 基线未通过")
    historical_layers = {r["layer_index"]: r for r in historical["layers"]}
    proof_layers = {r["layer_index"]: r for r in proof["layers"]}
    stream = oracle._XorShift32()
    rows = []
    query_count = 0
    lane_count = 0
    with (work / "queries.bin").open("xb") as output:
        for layer in manifest["layers"]:
            if layer["op"] != "convolutional":
                continue
            lid = int(layer["layer_index"])
            parameters = oracle._candidate_parameters(layer, proof_layers[lid])
            vector_file = work / f"t17_layer_{lid}.bin"
            meta = oracle._write_layer_vectors(vector_file, layer, weights[lid], parameters, manifest, "full", stream)
            old = historical_layers[lid]
            for key in ("vector_sha256", "activation_bytes_sha256", "selected_gf8_weight_bytes_sha256",
                        "golden_output_sha256", "random_stream_start_state", "random_stream_end_state",
                        "random_stream_u32_draws", "case_count"):
                if meta[key] != old[key]:
                    raise ValueError(f"T17 冻结向量不一致：layer={lid} field={key}")
            k = meta["reduction_length"]
            data = vector_file.read_bytes()
            record_size = oracle._CASE_HEADER.size + 2 * k
            if len(data) != record_size * 1016:
                raise ValueError("T17 向量长度异常")
            for offset in range(0, len(data), record_size):
                record = data[offset:offset + record_size]
                ordinal, kind, channel, y, x, bias, _pm, _pq, _nm, _nq, acc, expected = oracle._CASE_HEADER.unpack_from(record)
                acts = [oracle._signed_byte(b) for b in record[oracle._CASE_HEADER.size:oracle._CASE_HEADER.size + k]]
                effective, _ = oracle._mask_padding_activations(layer, y, x, acts)
                g = geometry(layer, channel, y, x)
                group_weights = weights[lid][g["group"] * k:(g["group"] + g["lanes"]) * k]
                output.write(HEADER.pack(lid, ordinal, kind, channel, y, x, k, g["lanes"]))
                output.write(bytes(a & 255 for a in acts))
                output.write(group_weights)
                for lane in range(g["lanes"]):
                    oc = g["group"] + lane
                    w = [oracle._signed_byte(v) for v in group_weights[lane * k:(lane + 1) * k]]
                    accumulator = oracle._checked_accumulator(effective, w, int(layer["bias_accumulator_int32_per_output_channel"][oc]))
                    result = oracle._d2_quantize(accumulator, float(layer["input_scale"]),
                                                float(layer["weight_scale_per_output_channel"][oc]),
                                                float(layer["output_scale"]), layer["activation"])
                    if oc == channel and (accumulator & 0xffffffff != acc or result & 255 != expected or
                                          int(layer["bias_accumulator_int32_per_output_channel"][oc]) & 0xffffffff != bias):
                        raise ValueError("所选输出的独立 oracle 与冻结 T17 不符")
                    output.write(LANE.pack(accumulator, result & 255))
                query_count += 1
                lane_count += g["lanes"]
            rows.append(meta)
    if query_count != 21336 or stream.draws != 20794000 or stream.state != 767883764:
        raise ValueError("随机流或查询数不完整")
    snapshot = work / "source"
    snapshot.mkdir()
    sources = []
    for rel in SOURCES:
        src = ROOT / rel
        if not src.is_file() or src.is_symlink():
            raise ValueError(f"编译源不是普通文件：{src}")
        dst = snapshot / src.name
        shutil.copyfile(src, dst)
        sources.append({"path": rel, "sha256": sha(dst)})
    return {"schema": "s2a_tile_whitebox_arithmetic_v1", "status": "PREPARED_NOT_RTL_PASS",
            "scope": "真实模型描述符与 8-lane 算术；白盒预装所选点 patch/真实 GF8 组，跳过 memory、tile/group/point 遍历，所选点 requant 后 abort",
            "not_covered": ["memory stall/error/cancel", "cache loading/reuse", "full tensor", "G4/G5"],
            "seed": 20260922, "queries": query_count, "lane_checks": lane_count,
            "u32_draws": stream.draws, "final_random_state": stream.state,
            "queries_sha256": sha(work / "queries.bin"), "queries_bytes": (work / "queries.bin").stat().st_size,
            "gf8_path": str(package), "gf8_sha256": sha(package), "sources": sources, "layers": rows,
            "runner_sha256": sha(Path(__file__)), "oracle_sha256": sha(Path(oracle.__file__)),
            "manifest_sha256": sha(oracle._MANIFEST), "t16_proof_sha256": sha(oracle._T16_PROOF),
            "exception_cases": {"executed": 0, "pending": ["overflow", "invalid INT8 -128", "invalid descriptor"]}}


def run_rtl(work: Path, report: dict, toolchain: Path, timeout: int) -> None:
    """单线程编译与运行，不覆盖既有结果，不产生波形。"""
    tools = toolchain / "mingw64/bin"
    make = toolchain / "usr/bin"
    verilator = tools / "verilator_bin.exe"
    for required in (verilator, tools / "g++.exe", make / "make.exe", tools.parent / "share/verilator"):
        if not required.exists():
            raise ValueError(f"工具不存在：{required}")
    env = os.environ.copy()
    env["PATH"] = str(make) + os.pathsep + str(tools) + os.pathsep + env.get("PATH", "")
    env["VERILATOR_ROOT"] = str(tools.parent / "share/verilator")
    report["tools"] = [{"path": str(p), "sha256": sha(p)} for p in
                       (verilator, tools / "g++.exe", make / "make.exe", Path(sys.executable))]
    report["python_version"] = sys.version
    if sha(work / "queries.bin") != report["queries_sha256"]:
        raise ValueError("准备后查询文件发生变化")
    for row in report["sources"]:
        if sha(work / "source" / Path(row["path"]).name) != row["sha256"]:
            raise ValueError("准备后隔离编译源发生变化")
    version = subprocess.run([str(verilator), "--version"], cwd=work, env=env,
                             capture_output=True, text=True, timeout=30, check=True)
    report["verilator_version"] = version.stdout.strip()
    command = [str(verilator), "--binary", "--timing", "-Wno-fatal", "-j", "1", "--threads", "1",
               "--top-module", "tb_s2a_conv_tile_unit", "--Mdir", "obj_dir",
               "-MAKEFLAGS", "PYTHON3='\"" + sys.executable + "\"'",
               "-CFLAGS", "-D_GLIBCXX_USE_CXX11_ABI=0"] + [str(Path("source") / Path(p).name) for p in SOURCES]
    report["compile_command"] = command
    for label, cmd in (("compile", command), ("simulation", [str(work / "obj_dir/Vtb_s2a_conv_tile_unit.exe")])):
        started = time.monotonic()
        with (work / f"{label}.log").open("x", encoding="utf-8") as log:
            result = subprocess.run(cmd, cwd=work, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=timeout, check=False)
        report[label] = {"exit_code": result.returncode, "seconds": round(time.monotonic() - started, 3)}
        if result.returncode:
            raise ValueError(f"{label} 失败，见 {work / (label + '.log')}")
    text = (work / "simulation.log").read_text(encoding="utf-8")
    marker = f"PASS TILE_WHITEBOX queries={report['queries']} lane_checks={report['lane_checks']}"
    if text.count(marker) != 1:
        raise ValueError("仿真未生成唯一完整通过标记")
    report["status"] = "PASS_WHITEBOX_ARITHMETIC_ONLY"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("self-test", "prepare", "rtl"), default="self-test")
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--toolchain", type=Path, default=Path(r"D:\FPGA_S2A_MSYS2_20261001\env"))
    parser.add_argument("--timeout-seconds", type=int, default=1200)
    args = parser.parse_args()
    if args.mode == "self-test":
        layer = {"output_shape_nchw": [1, 30, 13, 26]}
        assert geometry(layer, 29, 12, 25) == {"tile_y": 8, "tile_x": 24, "tile_height": 5,
                                             "tile_width": 2, "group": 24, "lanes": 6, "point": 9}
        try:
            geometry(layer, 30, 0, 0)
        except ValueError:
            pass
        else:
            raise AssertionError("未拒绝越界查询")
        print("PASS tile fixture geometry self-test; NOT RTL")
        return 0
    work = args.work_dir
    if work is None or not work.is_absolute() or work.exists() or not work.parent.is_dir() or work.parent.is_symlink():
        parser.error("--work-dir 必须是已存在普通父目录内的全新绝对目录")
    if args.timeout_seconds <= 0:
        parser.error("timeout 必须为正数")
    work.mkdir()
    report = {"status": "FAILED", "scope": "whitebox arithmetic only"}
    try:
        report = prepare(work)
        if args.mode == "rtl":
            run_rtl(work, report, args.toolchain, args.timeout_seconds)
    except Exception as exc:
        report["status"] = "FAILED"
        report["error"] = str(exc)
        raise
    finally:
        (work / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(report["status"], work / "summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
