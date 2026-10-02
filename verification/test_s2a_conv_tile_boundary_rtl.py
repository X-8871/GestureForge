"""验证真实 head 的黑盒尾 tile、缓存复用及分开标明的异常原语。"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import time

import numpy as np

import test_s2a_conv_engine_rtl as oracle

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ("src/s2a_network_descriptor_pkg.sv", "src/s2a_conv_tile_engine.sv", "sim/tb_s2a_conv_tile_boundary.sv")
TILE_SHA = "be3106daa3dc2adea13894d03bf21cd5ec693ce667cb610ec8d9511364112e66"


def sha(path: Path) -> str:
    """核对精确文件字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(work: Path) -> dict:
    """加载已冻结真实参数，仅生成零 feature 的独立黄金，不读图片/shards。"""
    manifest, _, weights, package = oracle._load_bound_inputs()
    if sha(ROOT / SOURCES[1]) != TILE_SHA:
        raise ValueError("生产 tile 与任务基线不一致")
    rows = []
    for lid in (29, 36):
        layer = next(row for row in manifest["layers"] if row["layer_index"] == lid)
        n, channels, h, w = layer["output_shape_nchw"]
        if (n, channels, h, w) != (1, 30, 13 if lid == 29 else 26, 13 if lid == 29 else 26) or layer["kernel_hw"] != [1, 1]:
            raise ValueError("head 真实形状发生变化")
        values = [oracle._d2_quantize(int(bias), float(layer["input_scale"]), float(layer["weight_scale_per_output_channel"][c]), float(layer["output_scale"]), layer["activation"]) for c, bias in enumerate(layer["bias_accumulator_int32_per_output_channel"])]
        golden = b"".join(bytes([value & 255]) * (h * w) for value in values)
        weight_path, golden_path = work / f"weight_{lid}.bin", work / f"golden_{lid}.bin"
        weight_path.write_bytes(weights[lid])
        golden_path.write_bytes(golden)
        _, cin, ih, iw = layer["input_shape_nchw"]
        if (ih, iw) != (h, w) or layer["stride_hw"] != [1, 1]:
            raise ValueError("只接受真实1x1 stride1 head")
        ic, y, x = np.indices((cin, ih, iw), dtype=np.int64)
        pattern = ((ic*3+y*5+x*7)%255-127).astype(np.int8)
        (work / f"feature_zero_{lid}.bin").write_bytes(bytes(cin*ih*iw))
        (work / f"feature_pattern_{lid}.bin").write_bytes(pattern.tobytes())
        # 使用INT64独立点积和D2 binary64量化；不使用生产MQ ROM求黄金。
        matrix = np.frombuffer(weights[lid], dtype=np.int8).astype(np.int64).reshape(channels, cin)
        accumulators = matrix @ pattern.astype(np.int64).reshape(cin, h*w)
        accumulators += np.asarray(layer["bias_accumulator_int32_per_output_channel"], dtype=np.int64)[:, None]
        # 对所有中间tap的最坏绝对界作独立检查，避免仅终值未溢出掩盖中间越界。
        safe_bounds = np.abs(matrix).sum(axis=1)*127+np.abs(np.asarray(layer["bias_accumulator_int32_per_output_channel"], dtype=np.int64))
        if np.any(safe_bounds > 2147483647):
            raise ValueError("pattern点积中间INT32安全界不成立")
        pattern_golden = bytes(oracle._d2_quantize(int(accumulators[c, p]), float(layer["input_scale"]), float(layer["weight_scale_per_output_channel"][c]), float(layer["output_scale"]), layer["activation"]) & 255 for c in range(channels) for p in range(h*w))
        (work / f"golden_pattern_{lid}.bin").write_bytes(pattern_golden)
        rows.append({"layer": lid, "input_shape": layer["input_shape_nchw"], "output_shape": layer["output_shape_nchw"], "weight_sha256": sha(weight_path), "golden_sha256": sha(golden_path), "golden_channel_values": values,
                     "feature_zero_sha256": sha(work / f"feature_zero_{lid}.bin"), "feature_pattern_sha256": sha(work / f"feature_pattern_{lid}.bin"), "golden_pattern_sha256": sha(work / f"golden_pattern_{lid}.bin"),
                     "pattern_golden_distinct_values": len(set(pattern_golden)), "pattern_int32_absolute_bounds": safe_bounds.tolist(),
                     "expected_feature_reads": int(layer["input_shape_nchw"][1])*h*w,
                     "expected_weight_reads": ((h+7)//8)*((w+7)//8)*len(weights[lid]), "expected_output_writes": len(golden)})
    (work / "source").mkdir()
    sources = []
    for rel in SOURCES:
        src = ROOT / rel
        if not src.is_file() or src.is_symlink():
            raise ValueError(f"编译源类型不符：{src}")
        dst = work / "source" / src.name
        shutil.copyfile(src, dst)
        sources.append({"path": rel, "sha256": sha(dst)})
    return {"schema": "s2a_tile_boundary_blackbox_v1", "status": "PREPARED_NOT_PASS", "layers": rows,
            "source_commit": subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip(),
            "sources": sources, "runner_sha256": sha(Path(__file__)), "oracle_sha256": sha(Path(oracle.__file__)),
            "manifest_sha256": sha(oracle._MANIFEST), "gf8_path": str(package), "gf8_sha256": sha(package),
            "blackbox_scope": "真实 layer29/36 形状，零特征验证cache计数，空间/channel非零模式验证跨tile/group缓存数据；真实完整GF8，从start到全部输出，无state/起点注入",
            "exception_scope": "mode3仅在首个真实compute tap白盒注入INT32最大值与1*1，明确不代表真实GF8溢出；其他异常通过输入端口/响应字节",
            "pattern": "feature(ic,y,x)=(ic*3+y*5+x*7)%255-127；INT64独立点积+D2 binary64量化",
            "not_covered": ["109整网", "每层1000随机+16定向", "3x3缓存完整遍历", "G4/G5"],
            "request_stall_pattern": [0, 1, 2, 7, 3], "response_stall": "一拍响应，无response stall覆盖", "simulations": []}


def execute(work: Path, report: dict, toolchain: Path, timeout: int) -> None:
    """只用一个编译job和一个模拟线程，无波形；结果与日志保留在新目录。"""
    tools, make = toolchain / "mingw64/bin", toolchain / "usr/bin"
    verilator = tools / "verilator_bin.exe"
    required = (verilator, tools / "g++.exe", make / "make.exe", tools.parent / "share/verilator", Path(sys.executable))
    for path in required:
        if not path.exists():
            raise ValueError(f"工具缺失：{path}")
    env = os.environ.copy()
    env["PATH"] = str(make) + os.pathsep + str(tools) + os.pathsep + env.get("PATH", "")
    env["VERILATOR_ROOT"] = str(tools.parent / "share/verilator")
    report["tools"] = [{"path": str(p), "sha256": sha(p)} for p in required if p.is_file()]
    report["verilator_version"] = subprocess.check_output([str(verilator), "--version"], cwd=work, env=env, text=True, timeout=30).strip()
    command = [str(verilator), "--binary", "--timing", "-Wno-fatal", "-j", "1", "--threads", "1", "--top-module", "tb_s2a_conv_tile_boundary", "--Mdir", "obj_dir",
               "-MAKEFLAGS", "PYTHON3='\"" + sys.executable + "\"'", "-CFLAGS", "-D_GLIBCXX_USE_CXX11_ABI=0"] + [str(Path("source") / Path(p).name) for p in SOURCES]
    started = time.monotonic()
    with (work / "compile.log").open("x", encoding="utf-8") as log:
        completed = subprocess.run(command, cwd=work, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
    report["compile"] = {"command": command, "exit_code": completed.returncode, "seconds": round(time.monotonic()-started, 3), "log_sha256": sha(work / "compile.log")}
    if completed.returncode:
        raise ValueError("编译失败")
    for lid, mode in [(29, 0), (36, 0), (29, 4), (36, 4)] + [(29, mode) for mode in (1, 2, 3, 11, 12, 13, 14, 15)]:
        for row in report["sources"]:
            if sha(work / "source" / Path(row["path"]).name) != row["sha256"]:
                raise ValueError("隔离源码变化")
        bound = next(row for row in report["layers"] if row["layer"] == lid)
        feature_name = f"feature_{'pattern' if mode==4 else 'zero'}"
        golden_name = "golden_pattern" if mode==4 else "golden"
        for prefix in ("weight", golden_name, feature_name):
            if sha(work / f"{prefix}_{lid}.bin") != bound[f"{prefix}_sha256"]:
                raise ValueError("输入夹具发生变化")
        command = [str(work / "obj_dir/Vtb_s2a_conv_tile_boundary.exe"), f"+LAYER={lid}", f"+MODE={mode}", f"+WEIGHT=weight_{lid}.bin", f"+GOLDEN={golden_name}_{lid}.bin", f"+FEATURE={feature_name}_{lid}.bin"]
        started = time.monotonic()
        path = work / f"layer{lid}_mode{mode}.log"
        with path.open("x", encoding="utf-8") as log:
            completed = subprocess.run(command, cwd=work, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
        row = {"layer": lid, "mode": mode, "command": command, "exit_code": completed.returncode, "seconds": round(time.monotonic()-started, 3), "log_sha256": sha(path)}
        report["simulations"].append(row)
        text = path.read_text(encoding="utf-8")
        if completed.returncode or text.count(f"PASS TILE_BOUNDARY layer={lid} mode={mode} ") != 1:
            raise ValueError(f"RTL用例失败 layer={lid} mode={mode}")
        match = re.search(r"PASS TILE_BOUNDARY layer=(\d+) mode=(\d+) feature=(\d+) weight=(\d+) writes=(\d+) error=(\d+) cycles=(\d+)", text)
        if match is None:
            raise ValueError("通过标记缺少统计")
        row["observed"] = dict(zip(("layer", "mode", "feature_reads", "weight_reads", "writes", "error", "cycles"), map(int, match.groups())))
        if mode in (0, 4) and (row["observed"]["feature_reads"], row["observed"]["weight_reads"], row["observed"]["writes"]) != (bound["expected_feature_reads"], bound["expected_weight_reads"], bound["expected_output_writes"]):
            raise ValueError("实测cache计数与独立manifest预算不一致")
        print(f"PASS layer={lid} mode={mode}", flush=True)
    for row in report["sources"]:
        if sha(ROOT / row["path"]) != row["sha256"]:
            raise ValueError("运行期间生产源码发生变化")
    report["status"] = "PASS_FOUR_HEAD_BLACKBOX_AND_EIGHT_EXCEPTION_CASES"


def main() -> int:
    """拒绝复用目录，失败保存原始日志，不自动改变生产RTL。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--toolchain", type=Path, default=Path(r"D:\FPGA_S2A_MSYS2_20261001\env"))
    parser.add_argument("--timeout-seconds", type=int, default=1200)
    args = parser.parse_args()
    work = args.work_dir.absolute()
    if work.exists() or work.is_symlink() or not work.parent.is_dir() or work.parent.is_symlink() or args.timeout_seconds <= 0:
        parser.error("要求不存在的工作目录、真实父目录和正timeout")
    work.mkdir()
    report = {"status": "FAILED"}
    try:
        report = prepare(work)
        execute(work, report, args.toolchain.absolute(), args.timeout_seconds)
    except Exception as exc:
        report["status"] = "FAILED"
        report["error"] = str(exc)
    finally:
        (work / "boundary_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(report["status"], flush=True)
    return 0 if report["status"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
