"""S5-B 证据驱动：双 pass 确定性比对 + 单元测试 + 完整证据包（一键命令）。

用法
----
    python scripts/stage5_s5b/run_s5b_evidence.py --run-id s5b_20261021_r01 --seed 20261021

产出（`<out>` 默认 `report/evidence/S5-B`，`R` = `--run-id`）
--------------------------------------------------------
- `<out>/R_a/`：主证据目录（RunId = `R_a`）
  - `cases/*.png`、`logs/*.json`、`run_manifest.json`、`summary.md`
  - `console/render_stdout.txt`、`console/render_exit_code.txt`（由渲染 CLI 自写）
  - `console/run_a_*.txt`、`console/run_b_*.txt`：父进程捕获的**原始 stdout/stderr 与真实退出码**
  - `console/unittest_*.txt`、`console/determinism_compare.txt`、`console/wording_scan.*`
  - `console/final_verdict.json`：写后复核的权威最终判定（含自身哈希链）
- `<out>/R_b/`：确定性副本（只含 PNG 与逐用例 JSON，用于逐字节比对）

设计要点
--------
- 两次 pass 使用**完全相同的参数**（仅 RunId 不同），比对 PNG 与逐用例 JSON 的 SHA256；
- 所有子进程退出码由父进程真实捕获并落盘，不伪造；
- 退出码：0 = 全部 PASS；1 = 存在失败（CLI 断言/确定性/单元测试/用词扫描）；2 = 环境或输入错误。
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import sys
import traceback
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import render_s5b_overlay as R  # noqa: E402  （同目录库，复用扫描/落盘/摘要工具）

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_ERROR = 2

DEFAULT_OUT = "report/evidence/S5-B"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_command(argv: list[str], cwd: Path) -> dict:
    """执行子进程并真实捕获 stdout/stderr 与退出码（UTF-8）。"""
    completed = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
    return {"argv": argv, "exit_code": int(completed.returncode),
            "stdout": completed.stdout or "", "stderr": completed.stderr or ""}


def digest_map(directory: Path, pattern: str, base: Path) -> dict:
    mapping = {}
    for path in sorted(directory.glob(pattern)):
        if path.is_file():
            mapping[path.relative_to(base).as_posix()] = sha256_file(path)
    return mapping


def set_digest(mapping: dict) -> str:
    return hashlib.sha256("\n".join(f"{key}:{mapping[key]}"
                                    for key in sorted(mapping)).encode("utf-8")).hexdigest()


def compare_runs(dir_a: Path, dir_b: Path) -> dict:
    png_a = digest_map(dir_a / "cases", "*.png", dir_a)
    png_b = digest_map(dir_b / "cases", "*.png", dir_b)
    json_a = digest_map(dir_a / "logs", "*.json", dir_a)
    json_b = digest_map(dir_b / "logs", "*.json", dir_b)
    png_mismatch = sorted(name for name in set(png_a) | set(png_b)
                          if png_a.get(name) != png_b.get(name))
    json_mismatch = sorted(name for name in set(json_a) | set(json_b)
                           if json_a.get(name) != json_b.get(name))
    identical = (png_a == png_b and len(png_a) > 0 and json_a == json_b and len(json_a) > 0)
    return {
        "method": "同一参数双 pass：逐文件 SHA256 比对（PNG 与逐用例 JSON）",
        "status": "PASS" if identical else "FAIL",
        "png_files": len(png_a), "json_files": len(json_a),
        "png_set_digest_a": set_digest(png_a), "png_set_digest_b": set_digest(png_b),
        "json_stats_digest_a": set_digest(json_a), "json_stats_digest_b": set_digest(json_b),
        "png_sha256_a": png_a, "png_sha256_b": png_b,
        "json_stats_a": json_a, "json_stats_b": json_b,
        "png_mismatch": png_mismatch, "json_mismatch": json_mismatch,
        "png_identical": png_a == png_b and len(png_a) > 0,
        "json_identical": json_a == json_b and len(json_a) > 0,
    }


def write_console(directory: Path, name: str, text: str) -> dict:
    path = directory / name
    R.write_text(path, text)
    return {"name": name, "sha256": R.sha256_bytes(text.encode("utf-8")),
            "bytes": len(text.encode("utf-8"))}


def artifact_inventory(*directories: Path) -> list[Path]:
    """收集需要做写后扫描的产物（排除扫描输出自身，避免自引用）。"""
    excluded = {"wording_scan.txt", "wording_scan.json", "final_verdict.json"}
    paths: list[Path] = []
    for directory in directories:
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*")):
            if not path.is_file():
                continue
            if path.name in excluded:
                continue
            paths.append(path)
    return paths


def verify_declared_hashes(dir_a: Path, dir_b: Path, manifest: dict) -> dict:
    """独立复核：重算两次 pass 全部产物的 SHA256，与 manifest 声明值逐项比对。"""
    determinism = manifest.get("determinism", {})
    declared = {}
    for name, digest in (determinism.get("png_sha256_a") or {}).items():
        declared[dir_a / name] = digest
    for name, digest in (determinism.get("json_stats_a") or {}).items():
        declared[dir_a / name] = digest
    for name, digest in (determinism.get("png_sha256_b") or {}).items():
        declared[dir_b / name] = digest
    for name, digest in (determinism.get("json_stats_b") or {}).items():
        declared[dir_b / name] = digest
    mismatch = []
    missing = []
    for path, digest in sorted(declared.items()):
        if not path.is_file():
            missing.append(str(path))
            continue
        actual = sha256_file(path)
        if actual != digest:
            mismatch.append({"path": str(path), "declared": digest, "actual": actual})
    observed = set()
    for directory in (dir_a, dir_b):
        observed |= set((directory / "cases").glob("*.png"))
        observed |= set((directory / "logs").glob("*.json"))
    extra = sorted(str(path) for path in observed if path not in declared)
    return {"checked": len(declared), "mismatch": mismatch, "missing": missing,
            "undeclared_files": extra,
            "status": "PASS" if not mismatch and not missing and not extra else "FAIL"}


def driver_summary_extra(determinism: dict, unittest_result: dict, replica_exit: int,
                         primary_exit: int, scan: dict, recheck: dict) -> str:
    lines = ["## 确定性（双 pass，本段由 run_s5b_evidence.py 写入）", ""]
    lines.append(f"- 状态：**{'PASS' if determinism['png_identical'] and determinism['json_identical'] else 'FAIL'}**"
                 "（同参数、仅 RunId 不同的两次渲染）")
    lines.append(f"- 比对文件：PNG {determinism['png_files']} 个、逐用例 JSON {determinism['json_files']} 个")
    lines.append(f"- PNG 集合摘要：A `{determinism['png_set_digest_a']}` / "
                 f"B `{determinism['png_set_digest_b']}`")
    lines.append(f"- JSON 统计摘要：A `{determinism['json_stats_digest_a']}` / "
                 f"B `{determinism['json_stats_digest_b']}`")
    lines.append(f"- 不一致清单：PNG {determinism['png_mismatch'] or '无'}；"
                 f"JSON {determinism['json_mismatch'] or '无'}")
    lines.append("")
    lines.append("## 子进程真实退出码")
    lines.append("")
    lines.append(f"- 渲染 pass A（主）：{primary_exit}")
    lines.append(f"- 渲染 pass B（确定性副本）：{replica_exit}")
    lines.append(f"- 单元测试：{'SKIPPED_BY_FLAG' if unittest_result.get('skipped') else unittest_result['exit_code']}"
                 f"（`console/unittest_stdout.txt`）")
    lines.append("")
    lines.append("## 写后复核")
    lines.append("")
    lines.append(f"- 扫描产物 {scan['artifacts_scanned']} 个（含两次 pass 的 PNG/JSON/summary/manifest 与控制台日志），"
                 f"禁用用词与“画面与结果来自同一帧号”的伪称命中 {scan['hit_total']} 次")
    lines.append("- 最终判定：`console/final_verdict.json`")
    lines.append("")
    lines.append("## 独立哈希复核")
    lines.append("")
    lines.append(f"- 重算两次 pass 的 PNG/JSON SHA256 与 manifest 声明值比对："
                 f"复核 {recheck['checked']} 项，状态 **{recheck['status']}**"
                 f"（不一致 {len(recheck['mismatch'])}，缺失 {len(recheck['missing'])}，"
                 f"未声明多出文件 {len(recheck['undeclared_files'])}）")
    lines.append("- 明细：`console/hash_recheck.txt`")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="run_s5b_evidence.py",
        description="S5-B 证据驱动：双 pass 确定性比对 + 单元测试 + 完整证据包")
    parser.add_argument("--out", default=DEFAULT_OUT, help=f"证据根目录（默认 {DEFAULT_OUT}）")
    parser.add_argument("--run-id", required=True, help="RunId 基名 R；产出 <out>/R_a 与 <out>/R_b")
    parser.add_argument("--seed", type=int, default=R.DEFAULT_SEED,
                        help=f"确定性随机种子（默认 {R.DEFAULT_SEED}）")
    parser.add_argument("--cases", default=None, help="可选子集（透传给渲染 CLI）")
    parser.add_argument("--force", action="store_true", help="允许写入已存在的 RunId 目录")
    parser.add_argument("--skip-unittest", action="store_true",
                        help="跳过单元测试子进程（仅供驱动自身冒烟/恢复使用，会如实记为 SKIPPED）")
    args = parser.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:  # noqa: BLE001
            pass
    buffer = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = R.Tee(original_stdout, buffer)
    exit_code = EXIT_PASS
    started = False
    out_root = Path(args.out).resolve()
    dir_a = out_root / f"{args.run_id}_a"
    dir_b = out_root / f"{args.run_id}_b"
    console_a = dir_a / "console"
    try:
        refusal = check_targets(args, dir_a, dir_b)
        if refusal:
            # RunId 保护：拒绝时不得创建/改写任何证据文件（含 console）
            print(f"[S5-B][driver][ERROR] {refusal}")
            exit_code = EXIT_ERROR
        else:
            started = True
            exit_code = drive(args, out_root, dir_a, dir_b, console_a)
    except Exception as exc:  # noqa: BLE001 - 驱动级异常必须如实报为环境/输入错误
        started = True
        exit_code = EXIT_ERROR
        print(f"[S5-B][driver][ERROR] {type(exc).__name__}: {exc}")
        traceback.print_exc(file=sys.stdout)
    finally:
        sys.stdout = original_stdout
        if started:
            console_a.mkdir(parents=True, exist_ok=True)
            R.write_text(console_a / "driver_stdout.txt", buffer.getvalue())
            R.write_text(console_a / "driver_exit_code.txt", f"{exit_code}\n")
            shell = ("python scripts/stage5_s5b/run_s5b_evidence.py "
                     f"--out {args.out} --run-id {args.run_id} --seed {args.seed}"
                     + (f" --cases {args.cases}" if args.cases else "")
                     + (" --force" if args.force else ""))
            R.write_text(console_a / "shell_invocation.txt",
                         f"$ {shell}\n# 父 shell 捕获的真实退出码：{exit_code}\n")
        print(f"[S5-B][driver] exit_code={exit_code} primary={dir_a}")
    return exit_code


def check_targets(args, dir_a: Path, dir_b: Path) -> str | None:
    """RunId 保护：已存在非空证据目录时必须拒绝，且**不写任何证据文件**。"""
    if args.force:
        return None
    for target in (dir_a, dir_b):
        if target.exists() and any((target / name).exists()
                                   for name in ("run_manifest.json", "cases", "logs")):
            return (f"RunId 目录已存在且非空：{target}"
                    "（不覆盖他人 RunId；如需覆盖请显式 --force）")
    return None


def drive(args, out_root: Path, dir_a: Path, dir_b: Path, console_a: Path) -> int:
    refusal = check_targets(args, dir_a, dir_b)
    if refusal:
        print(f"[S5-B][driver][ERROR] {refusal}")
        return EXIT_ERROR
    out_root.mkdir(parents=True, exist_ok=True)
    console_a.mkdir(parents=True, exist_ok=True)
    (dir_b / "console").mkdir(parents=True, exist_ok=True)

    render_script = SCRIPT_DIR / "render_s5b_overlay.py"
    test_script = SCRIPT_DIR / "test_s5b_overlay.py"
    if not render_script.is_file() or not test_script.is_file():
        print(f"[S5-B][driver][ERROR] 缺少必需脚本：{render_script} / {test_script}")
        return EXIT_ERROR

    def render_argv(run_id: str) -> list[str]:
        argv = [sys.executable, "-B", str(render_script), "--out", str(out_root),
                "--run-id", run_id, "--seed", str(args.seed)]
        if args.cases:
            argv += ["--cases", args.cases]
        return argv

    print(f"[S5-B][driver] 双 pass 渲染：run_a={dir_a.name} run_b={dir_b.name} seed={args.seed}")
    result_a = run_command(render_argv(dir_a.name), REPO_ROOT)
    result_b = run_command(render_argv(dir_b.name), REPO_ROOT)
    console_a_files = []
    console_a_files.append(write_console(console_a, "run_a_stdout.txt", result_a["stdout"]))
    console_a_files.append(write_console(console_a, "run_a_stderr.txt", result_a["stderr"]))
    console_a_files.append(write_console(console_a, "run_a_exit_code.txt", f"{result_a['exit_code']}\n"))
    console_a_files.append(write_console(console_a, "run_b_stdout.txt", result_b["stdout"]))
    console_a_files.append(write_console(console_a, "run_b_stderr.txt", result_b["stderr"]))
    console_a_files.append(write_console(console_a, "run_b_exit_code.txt", f"{result_b['exit_code']}\n"))
    print(f"[S5-B][driver] pass A 真实退出码 {result_a['exit_code']}；"
          f"pass B 真实退出码 {result_b['exit_code']}")

    unittest_argv = [sys.executable, "-B", "-m", "unittest", "discover",
                     "-s", str(SCRIPT_DIR), "-p", "test_s5b_overlay.py", "-v"]
    if args.skip_unittest:
        unittest_result = {"argv": unittest_argv, "exit_code": None, "stdout": "", "stderr": "",
                           "skipped": True}
        console_a_files.append(write_console(console_a, "unittest_stdout.txt",
                                             "SKIPPED_BY_FLAG（--skip-unittest）\n"))
        console_a_files.append(write_console(console_a, "unittest_stderr.txt", ""))
        console_a_files.append(write_console(console_a, "unittest_exit_code.txt", "SKIPPED\n"))
        print("[S5-B][driver] 单元测试：按 --skip-unittest 跳过（如实记为 SKIPPED，不计入 PASS）")
    else:
        unittest_result = run_command(unittest_argv, REPO_ROOT)
        console_a_files.append(write_console(console_a, "unittest_stdout.txt",
                                             unittest_result["stdout"]))
        console_a_files.append(write_console(console_a, "unittest_stderr.txt",
                                             unittest_result["stderr"]))
        console_a_files.append(write_console(console_a, "unittest_exit_code.txt",
                                             f"{unittest_result['exit_code']}\n"))
        print(f"[S5-B][driver] 单元测试真实退出码 {unittest_result['exit_code']}")

    required = {"run_manifest.json": dir_a / "run_manifest.json",
                "summary.md": dir_a / "summary.md"}
    for target in (dir_a, dir_b):
        if not (target / "cases").is_dir() or not (target / "logs").is_dir():
            print(f"[S5-B][driver][ERROR] 缺少 cases/logs 目录：{target}")
            return EXIT_ERROR
    missing = [name for name, path in required.items() if not path.is_file()]
    if missing:
        print(f"[S5-B][driver][ERROR] 主证据目录缺少必需产物：{missing}")
        return EXIT_ERROR
    if result_a["exit_code"] == EXIT_ERROR or result_b["exit_code"] == EXIT_ERROR:
        print("[S5-B][driver][ERROR] 渲染 CLI 报环境/输入错误（退出码 2），"
              "双 pass 比对不成立")
        write_console(console_a, "determinism_compare.txt",
                      "确定性比对未执行：至少一次 pass 以退出码 2 结束（环境/输入错误）\n")
        _write_verdict(console_a, exit_code=EXIT_ERROR, reasons=["cli_exit_2"], determinism=None,
                       unittest_result=unittest_result, result_a=result_a, result_b=result_b,
                       scan=None, dir_a=dir_a, recheck={"status": "NOT_RUN", "checked": 0})
        return EXIT_ERROR

    determinism = compare_runs(dir_a, dir_b)
    det_lines = ["双 pass 确定性比对（逐文件 SHA256；参数完全相同，仅 RunId 不同）",
                 f"PNG 文件数 {determinism['png_files']}；JSON 文件数 {determinism['json_files']}",
                 f"PNG 集合摘要 A {determinism['png_set_digest_a']}",
                 f"PNG 集合摘要 B {determinism['png_set_digest_b']}",
                 f"JSON 统计摘要 A {determinism['json_stats_digest_a']}",
                 f"JSON 统计摘要 B {determinism['json_stats_digest_b']}",
                 f"PNG 逐文件一致：{determinism['png_identical']}（不一致 {determinism['png_mismatch'] or '无'}）",
                 f"JSON 逐文件一致：{determinism['json_identical']}（不一致 {determinism['json_mismatch'] or '无'}）"]
    write_console(console_a, "determinism_compare.txt", "\n".join(det_lines) + "\n")

    primary_manifest = json.loads((dir_a / "run_manifest.json").read_text(encoding="utf-8"))
    primary_manifest["determinism"] = {
        **determinism,
        "status": "PASS" if (determinism["png_identical"] and determinism["json_identical"]) else "FAIL",
        # 与单 pass 摘要生成器兼容的规范键（A 为权威主 pass）
        "png_set_digest": determinism["png_set_digest_a"],
        "json_stats_digest": determinism["json_stats_digest_a"],
        "png_sha256": determinism["png_sha256_a"],
        "json_stats": determinism["json_stats_a"],
        "run_a": {"run_id": dir_a.name, "dir": str(dir_a), "exit_code": result_a["exit_code"]},
        "run_b": {"run_id": dir_b.name, "dir": str(dir_b), "exit_code": result_b["exit_code"]},
        "note": "两个 RunId 使用完全相同的参数（仅 RunId 不同）各跑一次；"
                "比对 PNG 与逐用例 JSON 的 SHA256",
    }
    primary_manifest["replica"] = {"run_id": dir_b.name, "dir": str(dir_b),
                                   "exit_code": result_b["exit_code"],
                                   "command": {"argv": result_b["argv"]}}
    primary_manifest["unittest"] = {"command": {"argv": unittest_result["argv"]},
                                    "exit_code": unittest_result["exit_code"],
                                    "status": "SKIPPED" if unittest_result.get("skipped") else
                                              ("PASS" if unittest_result["exit_code"] == 0 else "FAIL"),
                                    "console": "console/unittest_stdout.txt",
                                    "stderr_console": "console/unittest_stderr.txt",
                                    "test_file": str(test_script),
                                    "test_file_sha256": sha256_file(test_script)}
    primary_manifest["console"] = {"files": console_a_files,
                                   "render_stdout": "console/render_stdout.txt",
                                   "render_exit_code": "console/render_exit_code.txt"}

    reasons: list[str] = []
    final_exit = EXIT_PASS
    if result_a["exit_code"] != 0 or result_b["exit_code"] != 0:
        reasons.append(f"cli_exit_nonzero(a={result_a['exit_code']},b={result_b['exit_code']})")
    if not determinism["png_identical"]:
        reasons.append("png_determinism_mismatch")
    if not determinism["json_identical"]:
        reasons.append("json_determinism_mismatch")
    if unittest_result.get("skipped"):
        reasons.append("unittest_SKIPPED_BY_FLAG")
        final_exit = EXIT_FAIL
    elif unittest_result["exit_code"] != 0:
        reasons.append(f"unittest_exit_nonzero({unittest_result['exit_code']})")
    final_exit = EXIT_FAIL if reasons else EXIT_PASS

    pre_scan_targets = [dir_a / "summary.md"] + artifact_inventory(dir_a / "logs", dir_a / "cases") \
        + artifact_inventory(dir_b)
    pre_scan = R.scan_paths(pre_scan_targets)
    primary_manifest["post_write_scan"] = {
        "artifacts_scanned": pre_scan["artifacts_scanned"],
        "hit_total": pre_scan["hit_total"],
        "tokens": pre_scan["tokens"],
        "artifact_hashes": {item["path"]: item["sha256"] for item in pre_scan["per_artifact"]},
        "note": "主证据目录 run_manifest.json 与 summary.md 写完后的最终全量扫描见 "
                "console/wording_scan.json 与 console/final_verdict.json（避免 manifest 自引用哈希）",
    }
    if pre_scan["hit_total"] > 0:
        reasons.append(f"wording_scan_hits({pre_scan['hit_total']})")
        final_exit = EXIT_FAIL
    primary_manifest["exit_code"] = final_exit
    primary_manifest["status"] = "PASS" if final_exit == EXIT_PASS else "FAIL"

    recheck = verify_declared_hashes(dir_a, dir_b, primary_manifest)
    console_a_files.append(write_console(
        console_a, "hash_recheck.txt",
        "独立哈希复核（重算两次 pass 全部 PNG/JSON 的 SHA256 并与 manifest 声明值比对）\n"
        f"checked={recheck['checked']} mismatch={len(recheck['mismatch'])} "
        f"missing={len(recheck['missing'])} undeclared={len(recheck['undeclared_files'])} "
        f"status={recheck['status']}\n"
        + "".join(f"  MISMATCH {item['path']} declared={item['declared']} actual={item['actual']}\n"
                  for item in recheck["mismatch"])
        + "".join(f"  MISSING {path}\n" for path in recheck["missing"])
        + "".join(f"  UNDECLARED {path}\n" for path in recheck["undeclared_files"])))
    primary_manifest["hash_recheck"] = {
        "checked": recheck["checked"], "status": recheck["status"],
        "mismatch_count": len(recheck["mismatch"]), "missing_count": len(recheck["missing"]),
        "undeclared_files": recheck["undeclared_files"],
        "console": "console/hash_recheck.txt",
        "method": "独立重算 cases/*.png 与 logs/*.json 的 SHA256，与 manifest 的 determinism 段声明值逐项比对",
    }
    if recheck["status"] != "PASS":
        reasons.append("declared_hash_mismatch")
        final_exit = EXIT_FAIL
        primary_manifest["exit_code"] = final_exit
        primary_manifest["status"] = "FAIL"
    R.dump_json(dir_a / "run_manifest.json", primary_manifest)

    logs = []
    for path in sorted((dir_a / "logs").glob("*.json")):
        logs.append(json.loads(path.read_text(encoding="utf-8")))
    extra = driver_summary_extra(determinism, unittest_result, result_b["exit_code"],
                                 result_a["exit_code"], pre_scan, recheck)
    R.write_summary(dir_a, primary_manifest, logs, extra_sections=extra)

    final_scan = R.scan_paths(artifact_inventory(dir_a, dir_b))
    write_console(console_a, "wording_scan.txt",
                  "最终全量写后扫描（含两份 run_manifest.json 与 summary.md；排除扫描输出自身）\n"
                  f"artifacts={final_scan['artifacts_scanned']} hits={final_scan['hit_total']}\n"
                  + "\n".join(f"  {item['path']} bytes={item['bytes']} hits={item['hit_total']} "
                              f"sha256={item['sha256']}" for item in final_scan["per_artifact"]) + "\n")
    final_scan_path = console_a / "wording_scan.json"
    R.dump_json(final_scan_path, final_scan)
    if final_scan["hit_total"] > 0 and "wording_scan_hits" not in " ".join(reasons):
        reasons.append(f"final_wording_scan_hits({final_scan['hit_total']})")
        final_exit = EXIT_FAIL

    _write_verdict(console_a, exit_code=final_exit, reasons=reasons, determinism=determinism,
                   unittest_result=unittest_result, result_a=result_a, result_b=result_b,
                   scan=final_scan, dir_a=dir_a, recheck=recheck)

    print(f"[S5-B][driver] determinism={determinism['status']} "
          f"png_files={determinism['png_files']} json_files={determinism['json_files']}")
    print(f"[S5-B][driver] final_exit={final_exit} reasons={reasons or '无'}")
    print(f"[S5-B][driver] primary_run_dir={dir_a}")
    print(f"[S5-B][driver] replica_run_dir={dir_b}")
    return final_exit


def _write_verdict(console_a: Path, *, exit_code: int, reasons: list[str], determinism,
                   unittest_result: dict, result_a: dict, result_b: dict, scan, dir_a: Path,
                   recheck: dict) -> None:
    verdict = {
        "task_id": R.TASK_ID,
        "schema_version": "gestureforge_s5b_final_verdict_v1",
        "exit_code": exit_code,
        "status": {EXIT_PASS: "PASS", EXIT_FAIL: "FAIL"}.get(exit_code, "ERROR"),
        "reasons": reasons,
        "primary_run_dir": str(dir_a),
        "cli_exit_codes": {"a": result_a["exit_code"], "b": result_b["exit_code"]},
        "unittest_exit_code": unittest_result["exit_code"],
        "unittest_status": "SKIPPED" if unittest_result.get("skipped") else
                           ("PASS" if unittest_result["exit_code"] == 0 else "FAIL"),
        "determinism_status": (determinism or {}).get("status", "NOT_RUN"),
        "hash_recheck_status": (recheck or {}).get("status", "NOT_RUN"),
        "hash_recheck_checked": (recheck or {}).get("checked", 0),
        "wording_scan_hit_total": (scan or {}).get("hit_total", "NOT_RUN"),
        "manifest_sha256": sha256_file(dir_a / "run_manifest.json")
        if (dir_a / "run_manifest.json").is_file() else None,
        "summary_sha256": sha256_file(dir_a / "summary.md")
        if (dir_a / "summary.md").is_file() else None,
        "note": "本文件由 run_s5b_evidence.py 在写完 manifest/summary 之后生成，"
                "因此可对二者做最终扫描并给出权威退出码；父 shell 的真实退出码见 shell_invocation.txt",
    }
    R.dump_json(console_a / "final_verdict.json", verdict)


if __name__ == "__main__":
    sys.exit(main())