#!/usr/bin/env python3
"""S6-E（6-E 离线：验收用例集）证据包构建器：清单/哈希/真实退出码写回（不动点 + 收尾断言）。

    python -B verification/s6e_build_evidence.py --run-dir report/evidence/S6-E/s6e_acceptance_20261024_r01 \
        --project-root D:/codex-worktrees/w6

流程：
  1. 跑 `s6e_acceptance_check.py --inject-self-test`（基线 ALL_PASS + 6 类注入必须全被捕获）；
  2. 生成 inputs_manifest.json（role=input 的输入集合）并实跑 `--mode inputs`；
  3. 不动点：写 hashes + delivery_manifest → 实跑 `--mode evidence` → 收敛；
  4. 收尾断言：`--mode evidence` 必须 exit 0（run-dir 无未声明文件、哈希一致）。

说明：批准记录在 main（不在 w6 树内），因此**不绑其哈希**，只在 limitations 显式披露——不伪造绑定。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

TEXT_SUFFIXES = (".md", ".json", ".jsonl", ".txt", ".py", ".csv", ".yaml", ".yml", ".xdc")
SOURCES = (
    "docs/stage6/s6e_stage6_acceptance_cases_v1.json",
    "docs/stage6/S6E_stage6_acceptance_cases_v1.md",
    "docs/stage6/s6a_stage6_g0_behavior_v1.json",
    "verification/s6e_acceptance_check.py",
    "verification/s6e_build_evidence.py",
)
INPUT_ROLES = {
    "docs/stage6/s6e_stage6_acceptance_cases_v1.json": ("input", "6-E 验收用例集（本包主体）"),
    "docs/stage6/S6E_stage6_acceptance_cases_v1.md": ("input", "6-E 验收用例集人读版"),
    "docs/stage6/s6a_stage6_g0_behavior_v1.json": ("input", "24 项参数与 threshold 的机读来源（已批准 2026-10-23）"),
    "verification/s6e_acceptance_check.py": ("input", "用例集机器校验器（E1..E11；含 6 类必 FAIL 注入）"),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_normalized(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def run_command(command: list[str], root: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=str(root), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", check=False)
    return {"command_text": subprocess.list2cmdline(command), "exit_code": completed.returncode,
            "stdout": completed.stdout, "stderr": completed.stderr}


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="S6-E 证据包构建器")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--project-root", required=True)
    args = ap.parse_args(argv)
    root = Path(args.project_root).resolve()
    run_dir = (root / args.run_dir).resolve()
    if not run_dir.is_dir():
        print(f"运行目录不存在：{run_dir}")
        return 2
    checker = root / "verification/check_stage_delivery.py"
    run_id = run_dir.name

    # 1) 用例集校验（基线 + 6 类注入自测）
    check_out = run_dir / "s6e_acceptance_check.json"
    check_stdout = run_dir / "s6e_acceptance_check_stdout.txt"
    check_run = run_command([sys.executable, "-B", str(root / "verification/s6e_acceptance_check.py"),
                             "--project-root", str(root), "--inject-self-test",
                             "--out", str(check_out.relative_to(root)).replace("\\", "/")], root)
    check_stdout.write_text(check_run["stdout"] + check_run["stderr"], encoding="utf-8")
    print(f"[s6e-check] exit={check_run['exit_code']}")
    if check_run["exit_code"] != 0:
        print(check_run["stdout"]); print(check_run["stderr"]); return 1

    source_commit = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
                                   text=True, encoding="utf-8", check=False).stdout.strip()
    tool_versions = {"python": sys.version.split()[0],
                     "git": subprocess.run(["git", "--version"], capture_output=True, text=True,
                                           encoding="utf-8", check=False).stdout.strip()}

    inputs_manifest_path = run_dir / "inputs_manifest.json"
    manifest_path = run_dir / "delivery_manifest.json"
    hashes_path = run_dir / "hashes_sha256.txt"
    inputs_out = run_dir / "check_inputs_mode_output.txt"
    evidence_out = run_dir / "check_evidence_mode_output.txt"
    for placeholder in (inputs_out, evidence_out):
        placeholder.write_text("", encoding="utf-8")

    inputs_files = []
    for rel, (role, reason) in INPUT_ROLES.items():
        path = root / rel
        if not path.is_file():
            print(f"缺少输入文件：{rel}")
            return 2
        inputs_files.append({"path": rel, "sha256": hash_normalized(path), "role": role, "keep_reason": reason})
    write_json(inputs_manifest_path, {
        "schema_version": 1, "stage": "6", "task_id": "S6-E", "run_id": run_id,
        "source_commit": source_commit, "evidence_dir": args.run_dir,
        "interfaces": [],
        "interfaces_not_applicable_reason": (
            "S6-E 不消费已冻结的接口：其输入是阶段6 自己的已批准行为表（参数已批准但接口契约未冻结）与"
            "本轮冻结的用例集；阶段4 结果记录与阶段5 显示契约仍未冻结，验收执行依赖 BLOCKED。"),
        "files": inputs_files,
        "checks": [{"name": "输入文件 SHA-256 复算", "status": "PASS",
                    "command": "内置复算（构建器）", "exit_code": 0}],
        "limitations": [
            "批准记录 `report/evidence/CTRL-DSH-HANDOFF/decisions/stage6_approval_receipt_20261023_r01.md` 在 main 树内，"
            "不在 w6 工作树；因此**不绑其哈希**，只在 delivery_manifest.limitations 披露该引用，不伪造绑定。",
            "inputs 模式 CHECKS_OK 只表示清单/路径/哈希检查通过，不代表用例集语义正确或验收通过。",
        ],
    })
    inputs_run = run_command([sys.executable, "-B", str(checker), "--mode", "inputs",
                              "--manifest", str(inputs_manifest_path), "--project-root", str(root)], root)
    print(f"[inputs-mode] exit={inputs_run['exit_code']}")
    if inputs_run["exit_code"] != 0:
        print(inputs_run["stdout"]); print(inputs_run["stderr"]); return 1
    inputs_out.write_text(inputs_run["stdout"], encoding="utf-8")

    def file_entries() -> list[dict[str, str]]:
        rows = []
        for path in sorted(run_dir.rglob("*")):
            if not path.is_file():
                continue
            local = path.relative_to(run_dir).as_posix()
            if local == "delivery_manifest.json":
                continue
            rows.append({"path": path.relative_to(root).as_posix(), "sha256": hash_normalized(path),
                         "role": "diagnostic" if local.startswith("preserved_failures/") else "result",
                         "keep_reason": f"S6-E 证据文件：{local}"})
        for rel in SOURCES:
            path = root / rel
            if path.is_file():
                rows.append({"path": rel, "sha256": hash_normalized(path), "role": "source",
                             "keep_reason": "S6-E 用例集/校验器/构建器绑定"})
        return rows

    def write_hashes() -> None:
        lines = []
        for path in sorted(run_dir.rglob("*")):
            if not path.is_file():
                continue
            local = path.relative_to(run_dir).as_posix()
            if local in ("hashes_sha256.txt", "delivery_manifest.json"):
                continue
            lines.append(f"{sha256_file(path)}  {local}")
        hashes_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    checks = [
        {"name": "S6-E 用例集校验（E1..E11 基线 ALL_PASS）", "status": "PASS",
         "command": check_run["command_text"], "exit_code": check_run["exit_code"]},
        {"name": "S6-E 注入自测（6 类必 FAIL 全部被捕获）", "status": "PASS",
         "command": check_run["command_text"] + " --inject-self-test", "exit_code": check_run["exit_code"]},
        {"name": "check_stage_delivery.py --mode inputs", "status": "PASS",
         "command": inputs_run["command_text"], "exit_code": inputs_run["exit_code"]},
        {"name": "check_stage_delivery.py --mode evidence", "status": "NOT_RUN", "command": None,
         "exit_code": None, "reason": "首版清单生成后立即实跑"},
    ]

    def write_manifest(evidence_exit) -> None:
        write_json(manifest_path, {
            "schema_version": 1, "stage": "6", "task_id": "S6-E", "run_id": run_id,
            "source_commit": source_commit, "evidence_dir": args.run_dir,
            "interfaces": [],
            "interfaces_not_applicable_reason": (
                "S6-E 不消费已冻结接口：输入是阶段6 已批准行为表与本轮冻结用例集；"
                "阶段4/5 契约未冻结，6-E 执行依赖 BLOCKED。"),
            "files": file_entries(), "checks": checks, "tool_versions": tool_versions,
            "limitations": [
                f"source_commit = 本轮构建时 HEAD（{source_commit}）；本清单绑定该提交 + 本轮未提交差异。",
                "本包只**冻结**验收用例与判定口径；6-E 验收未执行（execution_status=NOT_RUN），不代表任何指标通过。",
                "T6-A03 数值仍 NOT_RUN（缺阶段4 实测帧周期 P）；禁止填造。",
                "批准记录在 main 树内，w6 不绑其哈希（见 inputs_manifest.limitations）。",
                "preserved_failures/ 内为**本轮真实失败**产物（套件首轮 UNEXPECTED、新鲜证据对在清单过期窗口内的 FAILED），"
                "按「失败不覆盖」原则原样保留，不作为通过凭据。",
                "活文档（.codex/STATE.md）不进硬哈希集合；只有交付物绑哈希。",
                "FIXPOINT 必须是最后动作；冻结后禁止再改动 run-dir 内容（收尾断言兜底）。",
            ],
        })

    previous = None
    for iteration in range(5):
        write_hashes()
        write_manifest(None)
        evidence_run = run_command([sys.executable, "-B", str(checker), "--mode", "evidence",
                                    "--manifest", str(manifest_path), "--project-root", str(root)], root)
        print(f"[evidence-mode:iter{iteration}] exit={evidence_run['exit_code']}")
        evidence_out.write_text(evidence_run["stdout"], encoding="utf-8")
        checks[-1] = {"name": "check_stage_delivery.py --mode evidence",
                      "status": "PASS" if evidence_run["exit_code"] == 0 else "FAIL",
                      "command": evidence_run["command_text"], "exit_code": evidence_run["exit_code"]}
        if evidence_run["exit_code"] != 0:
            print(evidence_run["stdout"]); print(evidence_run["stderr"]); return 1
        state = {p.relative_to(run_dir).as_posix(): sha256_file(p)
                 for p in sorted(run_dir.rglob("*")) if p.is_file()}
        if previous == state:
            print(f"[FIXPOINT-S6E] converged at round {iteration + 1}")
            break
        previous = state
    else:
        print("[FIXPOINT-S6E] 清单无法收敛")
        return 1

    closing = run_command([sys.executable, "-B", str(checker), "--mode", "evidence",
                           "--manifest", str(manifest_path), "--project-root", str(root)], root)
    if closing["exit_code"] != 0:
        print("[CLOSING] run-dir 出现未声明文件或哈希不符，构建中止")
        print(closing["stdout"]); return 1
    print("[CLOSING] run-dir 无未声明文件、清单一致")
    print(json.dumps({"status": "S6E_EVIDENCE_BUILT", "checks": [(c["name"], c["status"], c["exit_code"]) for c in checks],
                      "files": len(file_entries())}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())