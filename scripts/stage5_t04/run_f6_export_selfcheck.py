#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T04 **F6 自证性**：冻结提交单独检出/导出后，在独立副本里复跑自检与检查器。

为什么不是整树导出
==================
w5 工作树约 9.4 GB（历史证据占绝大多数），而本机磁盘余量不足以再做一份整树副本；
因此按**冻结集自述的路径**做**稀疏检出**——提取路径由 `frozen_set.json` 的成员清单现场推导
（冻结成员 + 冻结工具 + 本冻结包），既覆盖 F6 要证的全部对象，又不复制与冻结无关的历史证据。

两种"单独"形态都做（各自留证）
============================
- **A. `git archive` 导出（无 Git 元数据）**：按同一路径集导出后，在导出副本内跑冻结集校验器
  ⇒ 证明**每个冻结成员字节都能仅凭该提交复现**；
- **B. `git clone --shared --no-checkout` 独立检出（有独立 `.git`）**：在检出副本内跑冻结集校验器
  **与 `check_stage_delivery --mode evidence`**（该检查器要求 project-root 精确指向 Git 仓库根）
  ⇒ 证明提交单独检出后自检与检查器都能通过。

判定：A 校验器 exit 0、B 校验器 exit 0、B 检查器 exit 0、现工作树 handoff_check exit 0 ⇒ 本脚本 exit 0。
边界：只读提交内容；副本在 `tmp/5/S5-T04/**`；不 push、不动硬件、不改写被冻结文件。
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import tarfile
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_stage5_freeze_evidence as R          # noqa: E402  （复用命令执行/清单/哈希工具）

REPO_ROOT = R.REPO_ROOT
CHECKER = R.CHECKER
HANDOFF = pathlib.Path("D:/FPGA_Competition/verification/handoff_check.py")
FROZEN_RUN_DIR = "report/evidence/S5-T04/s5_freeze_20261027_r01"
FROZEN_MANIFEST = f"{FROZEN_RUN_DIR}/delivery_manifest.json"
FROZEN_SET = f"{FROZEN_RUN_DIR}/frozen_set.json"
DEFAULT_RUN_DIR = "report/evidence/S5-T04/s5_freeze_f6export_20261027_r01"

EXTRA_PATHSPECS = (
    ".gitattributes",
    "verification",
    "scripts/stage5_t04",
    "report/README.md",
    ".codex/STATE.md",
    FROZEN_RUN_DIR,
)


def pathspecs_from_frozen_set(frozen_set_path: pathlib.Path) -> list[str]:
    """由冻结集成员现场推导提取路径（repo 成员 + 冻结工具 + 本冻结包）。"""
    data = json.loads(frozen_set_path.read_text(encoding="utf-8"))
    specs: list[str] = []
    for member in data["members"]:
        if member.get("scope", "repo") != "repo":
            continue
        path = member["path"]
        if path not in specs:
            specs.append(path)
    for extra in EXTRA_PATHSPECS:
        if extra not in specs:
            specs.append(extra)
    return specs


def archive_export(commit: str, target: pathlib.Path, specs: list[str]) -> dict:
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    tar_path = target.parent / f"f6_archive_{commit[:12]}.tar"
    if tar_path.exists():
        tar_path.unlink()
    command = ["git", "-C", str(REPO_ROOT), "archive", "--format=tar",
               f"--output={tar_path}", commit, "--", *specs]
    completed = subprocess.run(command, capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
    if completed.returncode != 0:
        return {"command": f"git archive <commit> -- <{len(specs)} pathspecs>",
                "exit_code": completed.returncode, "stdout": completed.stdout,
                "stderr": completed.stderr, "extracted": 0}
    extracted = 0
    with tarfile.open(tar_path) as archive:
        for member in archive.getmembers():
            name = member.name.replace("\\", "/").lstrip("/")
            if ".." in name.split("/"):
                raise RuntimeError(f"导出包含越界路径：{member.name}")
            archive.extract(member, target)
            if member.isfile():
                extracted += 1
    return {"command": f"git archive --format=tar {commit} -- <{len(specs)} pathspecs>",
            "exit_code": completed.returncode, "extracted": extracted, "tar": str(tar_path)}


def shared_checkout(commit: str, branch: str, target: pathlib.Path, specs: list[str]) -> dict:
    if target.exists():
        shutil.rmtree(target)
    clone = ["git", "clone", "--shared", "--no-checkout", "--single-branch",
             "--branch", branch, str(REPO_ROOT), str(target)]
    cloned = subprocess.run(clone, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if cloned.returncode != 0:
        return {"command": " ".join(clone), "exit_code": cloned.returncode,
                "stdout": cloned.stdout, "stderr": cloned.stderr, "checked_out": 0}
    # 先取 `.gitattributes`：否则后续 checkout 读不到 `-text` 规则，core.autocrlf 会把 LF 转成 CRLF
    # （r01 实测：44 项哈希因此不符）。这一步是字节保真的前提。
    attrs = subprocess.run(["git", "-C", str(target), "checkout", commit, "--", ".gitattributes"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
    checkout = ["git", "-C", str(target), "checkout", commit, "--", *specs]
    checked = subprocess.run(checkout, capture_output=True, text=True, encoding="utf-8", errors="replace")
    toplevel = subprocess.run(["git", "-C", str(target), "rev-parse", "--show-toplevel"],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")
    kind = subprocess.run(["git", "-C", str(target), "cat-file", "-t", commit],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    return {"command": f"git clone --shared --no-checkout --branch {branch} <w5> <tmp>; "
                       f"git -C <tmp> checkout {commit} -- <{len(specs)} pathspecs>",
            "exit_code": checked.returncode if cloned.returncode == 0 else cloned.returncode,
            "clone_exit_code": cloned.returncode,
            "gitattributes_exit_code": attrs.returncode,
            "checkout_exit_code": checked.returncode,
            "toplevel": toplevel.stdout.strip(), "commit_object_kind": kind.stdout.strip(),
            "checked_out": len(specs),
            "stderr": (cloned.stderr + attrs.stderr + checked.stderr).strip()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument("--branch", default="stage5-display-prep")
    parser.add_argument("--run-dir", default=DEFAULT_RUN_DIR)
    args = parser.parse_args(argv)

    run_dir = REPO_ROOT / args.run_dir
    if run_dir.exists() and any(run_dir.iterdir()):
        print(f"[ENV_ERROR] RunId 目录已存在且非空：{run_dir}", file=sys.stderr)
        return 2
    (run_dir / "console").mkdir(parents=True, exist_ok=True)

    frozen_set_path = REPO_ROOT / FROZEN_SET
    if not frozen_set_path.is_file():
        print(f"[ENV_ERROR] 冻结集缺失：{frozen_set_path}", file=sys.stderr)
        return 2
    specs = pathspecs_from_frozen_set(frozen_set_path)
    (run_dir / "console" / "f6_pathspecs.txt").write_text(
        "\n".join([f"# 由 frozen_set.json 现场推导的提取路径（{len(specs)} 条）", *specs, ""]),
        encoding="utf-8")

    # ── A. git archive 导出（无 .git）→ 冻结集校验器 ─────────────────────
    archive_dir = REPO_ROOT / "tmp" / "5" / "S5-T04" / f"f6_archive_{args.commit[:12]}"
    archive = archive_export(args.commit, archive_dir, specs)
    verify_a = R.run_command([sys.executable, "-B", str(archive_dir / "verification" / "verify_stage5_frozen_set.py"),
                              "--root", str(archive_dir),
                              "--frozen-set", str(archive_dir / FROZEN_SET),
                              "--json-out", str(run_dir / "f6a_frozen_set_report.json")])
    (run_dir / "console" / "f6a_archive_and_verify.txt").write_text("\n".join([
        f"archive_command={archive['command']}", f"archive_exit_code={archive['exit_code']}",
        f"extracted_files={archive.get('extracted')}", f"export_dir={archive_dir}",
        f"verify_command={verify_a['command']}", f"verify_exit_code={verify_a['exit_code']}",
        "--- verifier stdout tail ---", "\n".join(verify_a["stdout"].rstrip().splitlines()[-6:]),
        "--- verifier stderr ---", verify_a["stderr"].rstrip(), ""]), encoding="utf-8")
    report_a_path = run_dir / "f6a_frozen_set_report.json"
    report_a = (json.loads(report_a_path.read_text(encoding="utf-8")) if report_a_path.is_file()
                else {"status": "NO_REPORT", "totals": {}})
    a_ok = archive["exit_code"] == 0 and verify_a["exit_code"] == 0 and \
        report_a.get("status") == "FROZEN_SET_VERIFIED"

    # ── B. 独立检出（独立 .git）→ 校验器 + check_stage_delivery ──────────
    checkout_dir = REPO_ROOT / "tmp" / "5" / "S5-T04" / f"f6_checkout_{args.commit[:12]}"
    checkout = shared_checkout(args.commit, args.branch, checkout_dir, specs)
    verify_b = R.run_command([sys.executable, "-B", str(checkout_dir / "verification" / "verify_stage5_frozen_set.py"),
                              "--root", str(checkout_dir),
                              "--frozen-set", str(checkout_dir / FROZEN_SET),
                              "--json-out", str(run_dir / "f6b_frozen_set_report.json")])
    checker_b = R.run_command([sys.executable, "-B", str(CHECKER), "--mode", "evidence",
                               "--project-root", str(checkout_dir),
                               "--manifest", str(checkout_dir / FROZEN_MANIFEST)])
    (run_dir / "console" / "f6b_checkout_verify_and_checker.txt").write_text("\n".join([
        f"checkout_command={checkout['command']}", f"clone_exit_code={checkout.get('clone_exit_code')}",
        f"checkout_exit_code={checkout.get('checkout_exit_code')}",
        f"toplevel={checkout.get('toplevel')}", f"commit_object_kind={checkout.get('commit_object_kind')}",
        f"checkout_dir={checkout_dir}",
        f"verify_command={verify_b['command']}", f"verify_exit_code={verify_b['exit_code']}",
        f"checker_command={checker_b['command']}", f"checker_exit_code={checker_b['exit_code']}",
        "--- verifier stdout tail ---", "\n".join(verify_b["stdout"].rstrip().splitlines()[-6:]),
        "--- checker stdout ---", checker_b["stdout"].rstrip(),
        "--- stderr ---", (verify_b["stderr"] + checker_b["stderr"]).rstrip(), ""]), encoding="utf-8")
    report_b_path = run_dir / "f6b_frozen_set_report.json"
    report_b = (json.loads(report_b_path.read_text(encoding="utf-8")) if report_b_path.is_file()
                else {"status": "NO_REPORT", "totals": {}})
    b_ok = (checkout.get("checkout_exit_code") == 0 and checkout.get("toplevel", "").replace("\\", "/").lower()
            == str(checkout_dir).replace("\\", "/").lower()
            and verify_b["exit_code"] == 0 and report_b.get("status") == "FROZEN_SET_VERIFIED"
            and checker_b["exit_code"] == 0 and R.STATUS_OK in checker_b["stdout"])

    # ── C. 现工作树 handoff_check（检出副本为部分检出，状态不洁故不在副本内跑）──
    handoff_run = R.run_command([sys.executable, "-B", str(HANDOFF), "--worktree", str(REPO_ROOT), "--json"])
    (run_dir / "console" / "handoff_live_worktree.txt").write_text("\n".join([
        "# handoff_check 需要完整工作树状态：在**现工作树**执行（不在部分检出副本内）",
        f"command={handoff_run['command']}", f"exit_code={handoff_run['exit_code']}",
        "--- stdout ---", handoff_run["stdout"].rstrip(),
        "--- stderr ---", handoff_run["stderr"].rstrip(), ""]), encoding="utf-8")
    c_ok = handoff_run["exit_code"] == 0

    final_ok = a_ok and b_ok and c_ok
    results = {
        "task_id": R.TASK_ID, "run_id": run_dir.name,
        "purpose": "F6 自证性：冻结提交单独导出/检出后复跑自检与检查器",
        "generated_utc8": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()) + "+08:00",
        "exported_commit": args.commit, "branch": args.branch,
        "pathspec_count": len(specs),
        "steps": {
            "A_archive_export_and_verify": {
                "command": archive["command"], "exit_code": archive["exit_code"],
                "extracted_files": archive.get("extracted"), "export_dir": str(archive_dir),
                "verify_command": verify_a["command"], "verify_exit_code": verify_a["exit_code"],
                "verify_status": report_a.get("status"), "verify_totals": report_a.get("totals")},
            "B_shared_checkout_verify_and_checker": {
                "command": checkout["command"], "clone_exit_code": checkout.get("clone_exit_code"),
                "checkout_exit_code": checkout.get("checkout_exit_code"),
                "toplevel": checkout.get("toplevel"), "checkout_dir": str(checkout_dir),
                "verify_command": verify_b["command"], "verify_exit_code": verify_b["exit_code"],
                "verify_status": report_b.get("status"), "verify_totals": report_b.get("totals"),
                "checker_command": checker_b["command"], "checker_exit_code": checker_b["exit_code"],
                "checker_checks_ok": R.STATUS_OK in checker_b["stdout"]},
            "C_handoff_check_live_worktree": {"command": handoff_run["command"],
                                             "exit_code": handoff_run["exit_code"]},
        },
        "verdict": "F6_SELFCHECK_PASS" if final_ok else "F6_SELFCHECK_FAIL",
        "limitations": [
            "w5 工作树约 9.4 GB，本机磁盘余量不足以整树复制：提取路径**由 `frozen_set.json` 成员现场推导**"
            "（冻结成员 + 冻结工具 + 本冻结包，不含与冻结无关的历史证据）——这正是 F6 要覆盖的对象集合，"
            "若有冻结成员不在提交内，校验器会 exit 2 而非静默通过。",
            "`scope=host` 宿主侧引用（阶段3/阶段4/Wong 回执）在本次复跑中仍从本机原路径解析；"
            "换机复跑需 `--skip-host-references` 并逐条核对跳过项。",
            "检出副本是**部分检出**（未检出与冻结无关的路径），故 `handoff_check` 不在副本内执行，"
            "而在现工作树单独执行并如实标注；不得把两者混为一项。",
            "本自证只证明**离线冻结集字节可复现**，不代表 G0/G1/G3/G4/G5、板级或实物验收；"
            "`CHECKS_OK` 只代表包装/绑定检查通过。",
        ],
    }
    checks = [
        {"name": "A. git archive 导出后冻结集校验（无 Git 元数据）",
         "status": "PASS" if a_ok else "FAIL",
         "command": verify_a["command"], "exit_code": verify_a["exit_code"],
         "reason": f"导出 {archive.get('extracted')} 个文件；{report_a.get('status')}；"
                   f"totals={json.dumps(report_a.get('totals', {}), ensure_ascii=False)}"},
        {"name": "B. 独立检出后冻结集校验 + check_stage_delivery --mode evidence",
         "status": "PASS" if b_ok else "FAIL",
         "command": checker_b["command"], "exit_code": checker_b["exit_code"],
         "reason": f"检出 root={checkout.get('toplevel')}；verifier={verify_b['exit_code']}"
                   f"({report_b.get('status')})；checker={checker_b['exit_code']}；CHECKS_OK 仅代表包装检查通过"},
        {"name": "C. handoff_check（现工作树；部分检出副本不适用）",
         "status": "PASS" if c_ok else "FAIL",
         "command": handoff_run["command"], "exit_code": handoff_run["exit_code"],
         "reason": "只读核验；与导出自证分别记录"},
    ]
    results["checks"] = checks
    (run_dir / "results_f6export.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    R.write_hashes(run_dir)
    manifest = R.build_manifest(args.run_dir, args.commit, checks)
    checker_m = R.run_checker(manifest)
    results["checker_exit"] = checker_m["exit_code"]
    (run_dir / "results_f6export.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    R.write_hashes(run_dir)
    R.build_manifest(args.run_dir, args.commit, checks)

    print(f"A_archive={archive['exit_code']} A_verify={verify_a['exit_code']}({report_a.get('status')}) "
          f"B_checkout={checkout.get('checkout_exit_code')} B_verify={verify_b['exit_code']}"
          f"({report_b.get('status')}) B_checker={checker_b['exit_code']} C_handoff={handoff_run['exit_code']} "
          f"manifest_checker={checker_m['exit_code']}")
    print(f"verdict={results['verdict']}")
    return 0 if final_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())