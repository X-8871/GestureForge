#!/usr/bin/env python3
"""用冻结 manifest 独立参考验证候选请求准入 RTL，生成可复核证据。"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
MODEL = "report/evidence/S2A-T01/tiny416_model_manifest.json"
MODEL_SHA = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
SPEC = "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
SOURCES = ("src/s2b_request_guard.sv", "sim/tb_s2b_request_guard.sv",
           "verification/test_s2b_request_guard_rtl.py")
SEED = 0x2B091010


def sha(path: Path) -> str:
    """对文件原始字节计算 SHA。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference(request: tuple[int, int, int, int], objects: list[dict]) -> tuple[int, int, int]:
    """以选中字节集合是否为一个允许对象的子集判定，不读取 RTL 常量。"""
    write, address, rmask, wmask = request
    mask = wmask if write else rmask
    if address % 4 or not mask or (rmask if write else wmask):
        return 0, 0, 1
    selected_bytes = {address + lane for lane in range(4) if mask & (1 << lane)}
    physical = address + 0x10000000
    if physical > 0xFFFFFFFF or not 0x10000000 <= physical < 0x12000000:
        return 0, 0, 2
    for obj in objects:
        if write and not obj["writable"]:
            continue
        if all(obj["start"] <= byte < obj["end"] for byte in selected_bytes):
            return 1, physical, 0
    return 0, 0, 2


def build_vectors(model: dict) -> tuple[str, dict]:
    """穷举对象附近全部 mask 与方向组合，另生成固定种子的随机样本。"""
    amap = model["address_map"]
    objects = []
    for name in ("input", "weight_package"):
        obj = amap[name]
        objects.append({"name": name, "start": obj["address"],
                        "end": obj["address"] + obj["length_bytes"], "writable": False})
    for layer in model["layers"]:
        if layer["op"] != "yolo":
            objects.append({"name": f"layer{layer['layer_index']}", "start": layer["tensor_address"],
                            "end": layer["tensor_address"] + layer["tensor_length_bytes"], "writable": True})
    if len(objects) != 38 or len({(o["start"], o["end"]) for o in objects}) != 38:
        raise ValueError("冻结对象数量或独立性变化")
    cases: list[tuple[str, tuple[int, int, int, int]]] = []
    def add(category: str, write: int, address: int, rmask: int, wmask: int) -> None:
        """仅保留接口可表示的 32-bit 地址。"""
        if 0 <= address <= 0xFFFFFFFF:
            cases.append((category, (write, address, rmask, wmask)))
    for obj in objects:
        # 所有首尾附近字节含相邻对象、间隙及未对齐跨边界情况。
        addresses = {obj["start"] + delta for delta in range(-4, 8)}
        addresses |= {obj["end"] + delta for delta in range(-8, 8)}
        addresses.add(((obj["start"] + obj["end"]) // 2) & ~3)
        for address in sorted(addresses):
            for write in (0, 1):
                for mask in range(16):
                    add("object_boundary_masks", write, address, 0 if write else mask, mask if write else 0)
        for read_mask in range(16):
            for write_mask in range(16):
                for write in (0, 1):
                    add("direction_conflicts", write, obj["start"], read_mask, write_mask)
    for left, right in zip(objects, objects[1:]):
        for address in {left["end"] & ~3, (left["end"] - 1) & ~3, right["start"] & ~3}:
            for write in (0, 1):
                for mask in range(16):
                    add("object_gap_or_adjacent", write, address, 0 if write else mask, mask if write else 0)
    head = next(o for o in objects if o["name"] == "layer29")
    for write in (0, 1):
        for mask in range(16):
            add("head13_tail_all_masks", write, (head["end"] - 1) & ~3,
                0 if write else mask, mask if write else 0)
    for address in (0x02000000, 0x10000000, 0xEFFFFFFC, 0xF0000000, 0xFFFFFFFC, 0xFFFFFFFF):
        for write in (0, 1):
            for mask in range(16):
                add("arena_and_uint32_overflow", write, address, 0 if write else mask, mask if write else 0)
    # 参数包的头、record、float scale/bias 与权重均在完整只读白名单中。
    package_start = amap["weight_package"]["address"]
    package_offsets = {0, 4, 24, amap["weight_package"]["length_bytes"] - 4}
    for layer in model["layers"]:
        offsets = layer.get("gf8_parameter_offsets")
        if offsets:
            package_offsets.update(offsets[key] for key in (
                "record_offset", "weight_scale_offset", "fused_bias_offset", "quantized_weight_offset"))
            package_offsets.add(offsets["quantized_weight_offset"] + offsets["quantized_weight_bytes"] - 1)
    for offset in sorted(package_offsets):
        for write in (0, 1):
            for mask in range(16):
                add("complete_gf8_sections_read_only", write, (package_start + offset) & ~3,
                    0 if write else mask, mask if write else 0)
    rng = random.Random(SEED)
    for index in range(10000):
        obj = rng.choice(objects)
        address = rng.getrandbits(32) if index % 4 == 0 else rng.randrange(obj["start"], obj["end"] + 8)
        if index % 3:
            address &= ~3
        write = rng.randrange(2)
        rmask, wmask = rng.randrange(16), rng.randrange(16)
        if index % 2:
            if write:
                rmask = 0
            else:
                wmask = 0
        add("random", write, address, rmask, wmask)
    rows = []
    results = Counter()
    category = Counter()
    for label, request in cases:
        expected = reference(request, objects)
        rows.append(" ".join(f"{x:x}" for x in (*request, *expected)))
        results[str(expected[2])] += 1
        category[label] += 1
    # 两个手算夹具独立于参考迭代实现：head13末尾只有低两个byte合法。
    assert reference((0, 0x01A474CC, 3, 0), objects) == (1, 0x11A474CC, 0)
    assert reference((1, 0x01A474CC, 0, 3), objects) == (1, 0x11A474CC, 0)
    assert reference((0, 0x01A474CC, 4, 0), objects) == (0, 0, 2)
    assert reference((1, 0x00100000, 0, 15), objects) == (0, 0, 2)
    return "\n".join(rows) + "\n", {"seed": SEED, "random_samples": 10000,
        "total_samples": len(cases), "categories": dict(category), "expected_error_counts": dict(results),
        "objects": objects, "reference_basis": "直接读取冻结manifest对象，选中byte集合属于同一对象；不读取RTL常量。",
        "adjacent_boundary_note": "冻结所有对象起点4B对齐；相邻对象边界不会被合法对齐单word跨越，未对齐跨界用BAD_ARGUMENT拒绝。"}


def run(work: Path, evidence: Path, toolchain: Path, report: dict) -> None:
    """单编译任务、单仿真线程，原始日志留证，不生成波形。"""
    if sha(ROOT / MODEL) != MODEL_SHA:
        raise ValueError("冻结manifest SHA变化")
    model = json.loads((ROOT / MODEL).read_text(encoding="utf-8"))
    text, coverage = build_vectors(model)
    (evidence / "vectors.txt").write_text(text, encoding="utf-8")
    report["coverage"] = coverage
    report["sources"] = [{"path": p, "sha256": sha(ROOT / p)} for p in SOURCES]
    report["inputs"] = [{"path": MODEL, "sha256": sha(ROOT / MODEL)}, {"path": SPEC, "sha256": sha(ROOT / SPEC)}]
    (work / "source").mkdir()
    (evidence / "source_snapshot").mkdir()
    for p in SOURCES:
        shutil.copyfile(ROOT / p, evidence / "source_snapshot" / Path(p).name)
        if p != SOURCES[2]:
            shutil.copyfile(ROOT / p, work / "source" / Path(p).name)
    tools, make = toolchain / "mingw64/bin", toolchain / "usr/bin"
    verilator = tools / "verilator_bin.exe"
    for p in (verilator, tools / "g++.exe", make / "make.exe", tools.parent / "share/verilator"):
        if not p.exists():
            raise ValueError(f"工具缺失：{p}")
    env = os.environ.copy()
    env["PATH"] = str(make) + os.pathsep + str(tools) + os.pathsep + env.get("PATH", "")
    env["VERILATOR_ROOT"] = str(tools.parent / "share/verilator")
    report["tool_versions"] = {"python": sys.version.split()[0], "verilator": subprocess.check_output(
        [str(verilator), "--version"], cwd=work, env=env, text=True, timeout=30).strip()}
    report["tool_files"] = [{"path": str(p), "sha256": sha(p)} for p in (verilator, tools / "g++.exe", make / "make.exe")]
    commands = [
        ("compile", [str(verilator), "--binary", "--timing", "-Wall", "-j", "1", "--threads", "1",
                     "--top-module", "tb_s2b_request_guard", "--Mdir", "obj_dir",
                     "-MAKEFLAGS", "PYTHON3='\"" + sys.executable + "\"'", "-CFLAGS", "-D_GLIBCXX_USE_CXX11_ABI=0",
                     "source/s2b_request_guard.sv", "source/tb_s2b_request_guard.sv"]),
        ("simulation", [str(work / "obj_dir/Vtb_s2b_request_guard.exe"), f"+VECTORS={evidence / 'vectors.txt'}"]),
    ]
    for name, command in commands:
        started = time.monotonic()
        log = evidence / f"{name}.log"
        with log.open("x", encoding="utf-8") as stream:
            completed = subprocess.run(command, cwd=work, env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=180)
        report["runs"].append({"name": name, "command": command, "exit_code": completed.returncode,
                               "seconds": round(time.monotonic() - started, 3), "log_sha256": sha(log)})
        if completed.returncode:
            raise ValueError(f"{name}失败")
    marker = f"PASS REQUEST_GUARD cases={coverage['total_samples']}"
    if (evidence / "simulation.log").read_text(encoding="utf-8").count(marker) != 1:
        raise ValueError("缺少精确样本数PASS标记")
    for p in report["sources"]:
        if sha(ROOT / p["path"]) != p["sha256"]:
            raise ValueError("运行期间源码变化")
    report["status"] = "PASS_COMBINATIONAL_REQUEST_GUARD"


def write_delivery(evidence: Path, report: dict) -> None:
    """清单保留未冻结部署依赖与实物限制；包装检查不能代替语义验收。"""
    files = [{"path": p, "sha256": sha(ROOT / p), "role": "source"} for p in SOURCES]
    files += [{"path": MODEL, "sha256": sha(ROOT / MODEL), "role": "input"}]
    for path in sorted(p for p in evidence.rglob("*") if p.is_file()):
        if path.name != "delivery_manifest.json":
            files.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path),
                          "role": "source" if path.parent.name == "source_snapshot" else "log" if path.suffix == ".log" else "input" if path.name == "vectors.txt" else "result"})
    checks = [{"name": r["name"], "status": "PASS" if r["exit_code"] == 0 else "FAIL",
               "command": subprocess.list2cmdline(r["command"]), "exit_code": r["exit_code"],
               "reason": "隔离Verilator组合模块验证，180秒超时。"} for r in report["runs"]]
    checks += [{"name": "全部向量与独立参考匹配", "status": "PASS" if report["status"].startswith("PASS_") else "FAIL",
                "command": f"python -B verification/test_s2b_request_guard_rtl.py --run-id {evidence.name}",
                "exit_code": 0 if report["status"].startswith("PASS_") else 2,
                "reason": "原始仿真精确PASS标记和参考样本总数一致，源码运行前后SHA未变；RunId不允许覆盖重跑。"},
               {"name": "物理接口部署冻结", "status": "BLOCKED", "command": None, "exit_code": None,
                "reason": "物理接口候选尚未冻结，当前仅验证独立组合准入模块。"},
               {"name": "AXI集成与实物", "status": "NOT_APPLICABLE", "command": None, "exit_code": None,
                "reason": "本任务模块无时钟、AXI或实物接口；请求门禁调用及AXI VALID行为属于后续集成验收。"}]
    delivery = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T09", "run_id": evidence.name,
        "source_commit": report["source_commit"], "evidence_dir": evidence.relative_to(ROOT).as_posix(),
        "interfaces": [{"name": "阶段2B物理接口候选", "version": "s2b-physical-candidate/0.1.1",
                        "frozen": False, "path": SPEC, "sha256": sha(ROOT / SPEC)}],
        "files": files, "checks": checks, "limitations": report["limitations"],
        "tool_versions": report.get("tool_versions", {"python": sys.version.split()[0]})}
    (evidence / "delivery_manifest.json").write_text(json.dumps(delivery, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    """要求新RunId并保留失败结果，不覆盖已有证据。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--toolchain", type=Path, default=Path(r"D:\FPGA_S2A_MSYS2_20261001\env"))
    args = parser.parse_args()
    if not args.run_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in args.run_id):
        parser.error("RunId只允许英文、数字、下划线与连字符")
    evidence_parent, work_parent = ROOT / "report/evidence/S2B-T09", ROOT / "tmp/2B/S2B-T09"
    for parent in (evidence_parent, work_parent):
        if not parent.parent.is_dir() or parent.is_symlink():
            parser.error(f"父目录未核验或链接：{parent}")
        parent.mkdir(exist_ok=True)
    evidence, work = evidence_parent / args.run_id, work_parent / args.run_id
    if evidence.exists() or work.exists() or evidence.is_symlink() or work.is_symlink():
        parser.error("不得复用RunId")
    evidence.mkdir()
    work.mkdir()
    started = time.monotonic()
    report = {"status": "FAIL", "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "runs": [], "limitations": ["物理接口未冻结；未修改冻结2A源码。", "未执行综合、资源/时序、AXI集成、DDR/cache或实物验证。",
                                            "组合模块调用者只在mem_valid时使用结果；本模块不包含valid、epoch或逐层owner。", "峰值内存未测；单编译job、单模拟线程，无波形。"]}
    try:
        run(work, evidence, args.toolchain.absolute(), report)
    except Exception as exc:
        report["error"] = str(exc)
    report["elapsed_seconds"] = round(time.monotonic() - started, 3)
    (evidence / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_delivery(evidence, report)
    print(json.dumps({"status": report["status"], "error": report.get("error"),
                      "samples": report.get("coverage", {}).get("total_samples"), "seconds": report["elapsed_seconds"]}, ensure_ascii=False))
    return 0 if report["status"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
