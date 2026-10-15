#!/usr/bin/env python3
"""验证候选 HP0 AXI3 单 word 桥，并保留每次运行的源码与原始证据。"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
MODEL = "report/evidence/S2A-T01/tiny416_model_manifest.json"
MODEL_SHA = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
SPEC = "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
SOURCES = ("src/s2b_request_guard.sv", "src/s2b_hp0_word_adapter.sv",
           "sim/tb_s2b_hp0_word_adapter.sv", "verification/test_s2b_hp0_word_adapter_rtl.py")
SEED = 0x2B101010
GUARD_VALIDATION_SOURCES = ("sim/tb_s2b_request_guard.sv", "verification/test_s2b_request_guard_rtl.py")


def sha(path: Path) -> str:
    """计算原始字节 SHA。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_vectors(model: dict) -> tuple[str, dict]:
    """独立以冻结对象集合验证选中字节，并按字节地址计算数据。"""
    objects = []
    for name in ("input", "weight_package"):
        obj = model["address_map"][name]
        objects.append((obj["address"], obj["address"] + obj["length_bytes"], False))
    for layer in model["layers"]:
        if layer["op"] != "yolo":
            objects.append((layer["tensor_address"], layer["tensor_address"] + layer["tensor_length_bytes"], True))
    if len(objects) != 38:
        raise ValueError("冻结对象数量变化")
    rows = []
    categories, errors, masks, positions = Counter(), Counter(), Counter(), Counter()
    rng = random.Random(SEED)

    def add(category: str, write: int, address: int, rmask: int, wmask: int) -> None:
        """用集合包含关系作准入参考，不读取 guard 或 adapter RTL 的常量。"""
        data = rng.getrandbits(32)
        selected = wmask if write else rmask
        byte_set = {address + lane for lane in range(4) if selected & (1 << lane)}
        error = 0
        if address % 4 or not selected or (rmask if write else wmask):
            error = 1
        elif not (0x10000000 <= address + 0x10000000 < 0x12000000) or not any(
            (not write or writable) and all(begin <= byte < end for byte in byte_set)
            for begin, end, writable in objects
        ):
            error = 2
        read_data = 0
        if not write and not error:
            for lane in range(4):
                if selected & (1 << lane):
                    physical = address + lane + 0x10000000
                    value = ((physical * 37) ^ (physical >> 8) ^ 0xA5) & 255
                    read_data |= value << (8 * lane)
        rows.append(" ".join(f"{v:x}" for v in (write, address, data, rmask, wmask, int(not error), error, read_data)))
        categories[category] += 1
        errors[str(error)] += 1
        if not error:
            masks[f"{'W' if write else 'R'}:{selected:04b}"] += 1
            positions[str((address // 4) % 2)] += 1

    for begin, end, _writable in objects:
        for address in sorted({begin, begin + 4, (end - 1) & ~3, (end - 5) & ~3, end & ~3, begin - 4}):
            if address < 0:
                continue
            for write in (0, 1):
                for mask in range(16):
                    add("all_object_masks_and_boundaries", write, address, 0 if write else mask, mask if write else 0)
        for write in (0, 1):
            add("unaligned", write, begin + 1, 0 if write else 15, 15 if write else 0)
            add("direction_conflict", write, begin, 1, 1)
    for address in (0x02000000, 0x10000000, 0xEFFFFFFC, 0xF0000000, 0xFFFFFFFC):
        for write in (0, 1):
            for mask in range(16):
                add("arena_and_overflow", write, address, 0 if write else mask, mask if write else 0)
    for index in range(1000):
        begin, end, _writable = rng.choice(objects)
        address = rng.randrange(begin, end + 8) & ~3
        write, mask = rng.randrange(2), rng.randrange(16)
        add("random_requests", write, address, 0 if write else mask, mask if write else 0)
    # 独立手算：0x11a474cc的两个合法byte分别是ad与70，高两lane禁用。
    physical = 0x11A474CC
    hand = [((physical + i) * 37 ^ ((physical + i) >> 8) ^ 0xA5) & 255 for i in range(2)]
    if hand != [0xAD, 0x70]:
        raise ValueError(f"手算夹具不一致：{hand}")
    return "\n".join(rows) + "\n", {"seed": SEED, "random_requests": 1000,
        "total_vectors": len(rows), "categories": dict(categories), "expected_errors": dict(errors),
        "legal_mask_counts": dict(masks), "word_position_counts": dict(positions),
        "bus_stall_seed": SEED, "per_stall_cycles": "固定xorshift32产生0..3周期",
        "directed_expected": 179, "random_cancel_histories": 128,
        "directed_categories": {"predeclaration_cancel_withdraw_runclose": 3,
            "cancel_write_accept_sets": 4, "cancel_read_declared_or_accepted": 2,
            "cancel_early_B_before_AW": 1, "cancel_response_or_RESP_slot": 4,
            "byte_withdraw_or_cancel": 2, "all_payload_fields_changed": 5,
            "epoch_change_with_RUN_high_or_low": 2, "read_wdata_changed": 1,
            "byte_between_payload_changed": 1, "R_response_errors_and_protocol": 7,
            "B_response_errors_and_protocol": 7, "duplicate_R_in_RESP": 1,
            "unexpected_R_or_B_in_RESP": 2, "unexpected_B_before_declaration": 1,
            "cancel_guard_error_RESP": 2, "late_protocol_after_first_error": 1,
            "permanent_AR_or_AW_W_stall_256cycles": 2, "idle_RUN_and_cancel_clear": 1,
            "clear_with_unexpected_response": 1, "three_same_epoch_successes": 1,
            "random_cancel_histories": 128},
        "reference_basis": "冻结manifest对象集合包含关系；总线字节函数与lane按字节独立求值，不读取RTL状态。",
        "hand_calculated": {"logical_addr": "0x01A474CC", "mask": "0011", "bytes": hand,
                            "expected_word": "0x000070AD", "outside_mask": "0100 -> BAD_RANGE"}}


def run(work: Path, evidence: Path, toolchain: Path, report: dict) -> None:
    """单job构建，单线程仿真；180秒无完成停止，失败不覆盖原件。"""
    if sha(ROOT / MODEL) != MODEL_SHA:
        raise ValueError("冻结manifest SHA变化")
    report["sources"] = [{"path": p, "sha256": sha(ROOT / p)} for p in SOURCES]
    report["inputs"] = [{"path": p, "sha256": sha(ROOT / p)} for p in (MODEL, SPEC)]
    (work / "source").mkdir()
    (evidence / "source_snapshot").mkdir()
    for p in SOURCES:
        shutil.copyfile(ROOT / p, evidence / "source_snapshot" / Path(p).name)
        if p.endswith(".sv"):
            shutil.copyfile(ROOT / p, work / "source" / Path(p).name)
    vectors, coverage = build_vectors(json.loads((ROOT / MODEL).read_text(encoding="utf-8")))
    (evidence / "vectors.txt").write_text(vectors, encoding="utf-8")
    report["coverage"] = coverage
    tools_dir, make_dir = toolchain / "mingw64/bin", toolchain / "usr/bin"
    verilator = tools_dir / "verilator_bin.exe"
    for p in (verilator, tools_dir / "g++.exe", make_dir / "make.exe", tools_dir.parent / "share/verilator"):
        if not p.exists():
            raise ValueError(f"工具缺失：{p}")
    env = os.environ.copy()
    env["PATH"] = str(make_dir) + os.pathsep + str(tools_dir) + os.pathsep + env.get("PATH", "")
    env["VERILATOR_ROOT"] = str(tools_dir.parent / "share/verilator")
    report["tool_versions"] = {"python": sys.version.split()[0], "verilator": subprocess.check_output(
        [str(verilator), "--version"], cwd=work, env=env, text=True, timeout=30).strip()}
    report["tool_files"] = [{"path": str(p), "sha256": sha(p)} for p in (verilator, tools_dir / "g++.exe", make_dir / "make.exe")]
    commands = [
        ("compile", [str(verilator), "--binary", "--timing", "--timescale", "1ns/1ps", "-Wall", "-j", "1", "--threads", "1",
                     "--top-module", "tb_s2b_hp0_word_adapter", "--Mdir", "obj_dir",
                     "-MAKEFLAGS", "PYTHON3='\"" + sys.executable + "\"'", "-CFLAGS", "-D_GLIBCXX_USE_CXX11_ABI=0",
                     *["source/" + Path(p).name for p in SOURCES if p.endswith(".sv")]]),
        ("simulation", [str(work / "obj_dir/Vtb_s2b_hp0_word_adapter.exe"), f"+VECTORS={evidence / 'vectors.txt'}"]),
    ]
    for name, command in commands:
        started = time.monotonic()
        log = evidence / f"{name}.log"
        with log.open("x", encoding="utf-8") as stream:
            process = subprocess.Popen(command, cwd=work, env=env, stdout=stream, stderr=subprocess.STDOUT)
            timed_out = False
            try:
                process.wait(timeout=180)
            except subprocess.TimeoutExpired:
                timed_out = True
                # PID来自本次Popen，不按名称查杀其他窗口的进程。
                if os.name == "nt":
                    stopped = subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        stdout=stream, stderr=subprocess.STDOUT, timeout=30)
                    report["timeout_stop_exit_code"] = stopped.returncode
                else:
                    process.kill()
                process.wait(timeout=30)
        report["runs"].append({"name": name, "command": command, "exit_code": process.returncode,
                               "seconds": round(time.monotonic() - started, 3), "log_sha256": sha(log),
                               "timed_out": timed_out})
        if timed_out or process.returncode:
            raise ValueError(f"{name}失败")
    simulation = (evidence / "simulation.log").read_text(encoding="utf-8")
    matches = re.findall(r"PASS HP0_WORD_ADAPTER vectors=(\d+) directed=(\d+) cycles=(\d+) logical=(\d+) AR=(\d+) AW=(\d+) W=(\d+) R=(\d+) B=(\d+)", simulation)
    if len(matches) != 1 or int(matches[0][0]) != coverage["total_vectors"]:
        raise ValueError("缺少精确样本数PASS标记")
    report["simulation_counts"] = dict(zip(("vectors", "directed", "cycles", "logical", "AR", "AW", "W", "R", "B"), map(int, matches[0])))
    if report["simulation_counts"]["directed"] != coverage["directed_expected"] or sum(coverage["directed_categories"].values()) != coverage["directed_expected"]:
        raise ValueError("定向验证计数与覆盖分类不一致")
    for p in report["sources"]:
        if sha(ROOT / p["path"]) != p["sha256"]:
            raise ValueError("运行期间源码变化")
    report["status"] = "PASS_CANDIDATE_HP0_WORD_ADAPTER"


def write_delivery(evidence: Path, report: dict) -> None:
    """绑定候选接口与真实源码，清单检查不代表部署接口已冻结。"""
    files = [{"path": p, "sha256": sha(ROOT / p), "role": "source"} for p in SOURCES]
    if "guard_regression" in report:
        files += [{"path": p, "sha256": sha(ROOT / p), "role": "source"} for p in GUARD_VALIDATION_SOURCES]
    files += [{"path": MODEL, "sha256": sha(ROOT / MODEL), "role": "input"}]
    for path in sorted(p for p in evidence.rglob("*") if p.is_file()):
        if path.name != "delivery_manifest.json":
            files.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path),
                "role": "source" if path.parent.name == "source_snapshot" else "log" if path.suffix == ".log" else "input" if path.name == "vectors.txt" else "result"})
    checks = [{"name": r["name"], "status": "PASS" if r["exit_code"] == 0 else "FAIL",
               "command": subprocess.list2cmdline(r["command"]), "exit_code": r["exit_code"],
               "reason": "隔离Verilator实际RTL验证；单job/单线程、180秒观察上限。"} for r in report["runs"]]
    if "guard_regression" in report:
        guard_report = report["guard_regression"]
        checks += [{"name": "guard_" + r["name"], "status": "PASS" if r["exit_code"] == 0 else "FAIL",
                    "command": subprocess.list2cmdline(r["command"]), "exit_code": r["exit_code"],
                    "reason": "复用既有独立guard全部70736向量与严格Verilator验证；在T10隔离目录串行执行。"}
                   for r in guard_report["runs"]]
        checks += [{"name": "guard完整回归", "status": "PASS" if guard_report["status"].startswith("PASS_") else "FAIL",
                    "command": f"python -B verification/test_s2b_hp0_word_adapter_rtl.py --run-id {evidence.name} --guard-regression",
                    "exit_code": 0 if guard_report["status"].startswith("PASS_") else 2,
                    "reason": "冻结manifest独立字节集合参考，样本数必须精确70736。"}]
    checks += [{"name": "独立向量与定向验证", "status": "PASS" if report["status"].startswith("PASS_") else "FAIL",
                "command": f"python -B verification/test_s2b_hp0_word_adapter_rtl.py --run-id {evidence.name}",
                "exit_code": 0 if report["status"].startswith("PASS_") else 2,
                "reason": "精确计数PASS标记与源码前后哈希核对；无覆盖重跑。"},
               {"name": "完整2B部署与实物", "status": "BLOCKED", "command": None, "exit_code": None,
                "reason": "候选接口未冻结；本leaf不含CSR停止确认、排空timer、缓存与所有权。"}]
    delivery = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T10", "run_id": evidence.name,
        "source_commit": report["source_commit"], "evidence_dir": evidence.relative_to(ROOT).as_posix(),
        "interfaces": [{"name": "阶段2B物理接口候选", "version": "s2b-physical-candidate/0.1.2",
                        "frozen": False, "path": SPEC, "sha256": sha(ROOT / SPEC)}],
        "files": files, "checks": checks, "limitations": report["limitations"],
        "tool_versions": report.get("tool_versions", {"python": sys.version.split()[0]})}
    (evidence / "delivery_manifest.json").write_text(json.dumps(delivery, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    """使用新RunId；所有失败证据保留，运行结束由总控另行审查。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--toolchain", type=Path, default=Path(r"D:\FPGA_S2A_MSYS2_20261001\env"))
    parser.add_argument("--guard-regression", action="store_true", help="串行复用既有guard全部70736条回归")
    args = parser.parse_args()
    if not args.run_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in args.run_id):
        parser.error("RunId只允许英文、数字、下划线与连字符")
    evidence_parent, work_parent = ROOT / "report/evidence/S2B-T10", ROOT / "tmp/2B/S2B-T10"
    for parent in (evidence_parent, work_parent):
        if not parent.parent.is_dir() or parent.is_symlink():
            parser.error(f"父目录未核验或链接：{parent}")
        parent.mkdir(exist_ok=True)
    evidence, work = evidence_parent / args.run_id, work_parent / args.run_id
    if evidence.exists() or work.exists() or evidence.is_symlink() or work.is_symlink():
        parser.error("不得复用RunId")
    evidence.mkdir(); work.mkdir()
    started = time.monotonic()
    report = {"status": "FAIL", "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "runs": [], "limitations": ["物理接口0.1.1未冻结；不构成完整2B G0/G4/G5或SAFE_TO_REUSE证明。",
        "未修改冻结2A；guard仅显式无符号lane兼容修复；未做HP/DDR/cache/完整CSR集成、综合、时序、实物测试。",
        "cancel只模拟外层已决定取消，不包含CSR监视、STOP确认或drain timeout控制器。",
        "所有输入VALID模拟在采样沿前稳定；异常R/B仍消费但隔离只允许统一冷恢复清除。",
        "峰值内存未测；每Run单编译job和单仿真线程，无波形；重跑次数见独立RunId目录。"]}
    try:
        run(work, evidence, args.toolchain.absolute(), report)
        if args.guard_regression:
            guard_work, guard_evidence = work / "guard", evidence / "guard"
            guard_work.mkdir(); guard_evidence.mkdir()
            guard_report = {"status": "FAIL", "runs": []}
            report["guard_regression"] = guard_report
            module_spec = importlib.util.spec_from_file_location("s2b_guard_regression", ROOT / GUARD_VALIDATION_SOURCES[1])
            if module_spec is None or module_spec.loader is None:
                raise ValueError("既有guard验证模块无法加载")
            guard_module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(guard_module)
            guard_module.run(guard_work, guard_evidence, args.toolchain.absolute(), guard_report)
            if guard_report.get("coverage", {}).get("total_samples") != 70736:
                raise ValueError("既有guard全回归样本数变化")
    except Exception as exc:
        report["status"] = "FAIL"
        report["error"] = str(exc)
    report["elapsed_seconds"] = round(time.monotonic() - started, 3)
    (evidence / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_delivery(evidence, report)
    print(json.dumps({"status": report["status"], "error": report.get("error"),
                      "counts": report.get("simulation_counts"), "seconds": report["elapsed_seconds"]}, ensure_ascii=False))
    return 0 if report["status"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
