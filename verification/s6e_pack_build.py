#!/usr/bin/env python3
"""通用 S6-E 家族证据包构建器（清单/哈希/真实退出码；不动点 + 收尾断言）。

    python -B verification/s6e_pack_build.py --project-root <abs> --run-dir <rel> \
        --task-id S6-E --input <rel> [--input ...] --source <rel> [--source ...]

与 `s6e_build_evidence.py` 的区别：本构建器**不含** S6-E 验收用例集的专用相位，
供后续无板卡轮（延迟方法学、窗口申请包等）复用；两个检查器均以绝对 `--project-root` 实跑并记录真实退出码。

约束：`--input` 至少一项（inputs 模式要求 role=input）；`--run-dir` 必须已存在。
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
    ap = argparse.ArgumentParser(description="通用 S6-E 家族证据包构建器")
    ap.add_argument("--project-root", required=True)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--task-id", default="S6-E")
    ap.add_argument("--input", action="append", default=[])
    ap.add_argument("--source", action="append", default=[])
    ap.add_argument("--interfaces-reason", default=(
        "S6-E 无板卡轮不消费任何已冻结接口：输入是阶段6 自己已批准的行为表与本轮冻结产物；"
        "阶段4 结果记录与阶段5 显示契约仍未冻结，6-E 实物验收依赖 BLOCKED。"))
    args = ap.parse_args(argv)
    root = Path(args.project_root).resolve()
    run_dir = (root / args.run_dir).resolve()
    if not run_dir.is_dir():
        print(f"运行目录不存在：{run_dir}")
        return 2
    if not args.input:
        print("至少需要一个 --input（inputs 模式要求 role=input）")
        return 2
    checker = root / "verification/check_stage_delivery.py"
    run_id = run_dir.name
    inputs_manifest_path = run_dir / "inputs_manifest.json"
    manifest_path = run_dir / "delivery_manifest.json"
    hashes_path = run_dir / "hashes_sha256.txt"
    inputs_out = run_dir / "check_inputs_mode_output.txt"
    evidence_out = run_dir / "check_evidence_mode_output.txt"
    for placeholder in (inputs_out, evidence_out):
        placeholder.write_text("", encoding="utf-8")

    source_commit = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
                                   text=True, encoding="utf-8", check=False).stdout.strip()
    tool_versions = {"python": sys.version.split()[0],
                     "git": subprocess.run(["git", "--version"], capture_output=True, text=True,
                                           encoding="utf-8", check=False).stdout.strip()}

    inputs_files = []
    for rel in args.input:
        path = root / rel
        if not path.is_file():
            print(f"缺少输入文件：{rel}")
            return 2
        inputs_files.append({"path": rel, "sha256": hash_normalized(path), "role": "input",
                             "keep_reason": "本包输入（受哈希绑定）"})
    write_json(inputs_manifest_path, {
        "schema_version": 1, "stage": "6", "task_id": args.task_id, "run_id": run_id,
        "source_commit": source_commit, "evidence_dir": args.run_dir,
        "interfaces": [], "interfaces_not_applicable_reason": args.interfaces_reason,
        "files": inputs_files,
        "checks": [{"name": "输入文件 SHA-256 复算", "status": "PASS",
                    "command": "内置复算（构建器）", "exit_code": 0}],
        "limitations": [
            "批准记录位于 main 树内，不在 w6 工作树；本包不绑其哈希，只在 delivery_manifest.limitations 披露引用。",
            "inputs 模式 CHECKS_OK 只表示清单/路径/哈希检查通过，不代表语义正确或验收通过。",
        ],
    })
    inputs_run = run_command([sys.executable, "-B", str(checker), "--mode", "inputs",
                              "--manifest", str(inputs_manifest_path), "--project-root", str(root)], root)
    print(f"[inputs-mode] exit={inputs_run['exit_code']}")
    if inputs_run["exit_code"] != 0:
        print(inputs_run["stdout"]); print(inputs_run["stderr"]); return 1
    inputs_out.write_text(inputs_run["stdout"], encoding="utf-8")

    def file_entries():
        rows = []
        for path in sorted(run_dir.rglob("*")):
            if not path.is_file():
                continue
            local = path.relative_to(run_dir).as_posix()
            if local == "delivery_manifest.json":
                continue
            rows.append({"path": path.relative_to(root).as_posix(), "sha256": hash_normalized(path),
                         "role": "result", "keep_reason": f"S6-E 无板卡轮证据文件：{local}"})
        for rel in args.source:
            path = root / rel
            if path.is_file():
                rows.append({"path": rel, "sha256": hash_normalized(path), "role": "source",
                             "keep_reason": "本包绑定产物"})
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
        {"name": "check_stage_delivery.py --mode inputs", "status": "PASS",
         "command": inputs_run["command_text"], "exit_code": inputs_run["exit_code"]},
        {"name": "check_stage_delivery.py --mode evidence", "status": "NOT_RUN", "command": None,
         "exit_code": None, "reason": "首版清单生成后立即实跑"},
    ]

    def write_manifest(evidence_exit) -> None:
        write_json(manifest_path, {
            "schema_version": 1, "stage": "6", "task_id": args.task_id, "run_id": run_id,
            "source_commit": source_commit, "evidence_dir": args.run_dir,
            "interfaces": [], "interfaces_not_applicable_reason": args.interfaces_reason,
            "files": file_entries(), "checks": checks, "tool_versions": tool_versions,
            "limitations": [
                f"source_commit = 本轮构建时 HEAD（{source_commit}）；本清单绑定该提交 + 本轮未提交差异。",
                "本包为**无板卡轮**产物：不含任何板级实测；回放/离线结论不得升级为实物或验收结论。",
                "T6-A03 数值仍 NOT_RUN（缺阶段4 实测帧周期 P）；禁止填造。",
                "板卡已由 Wong 拔下（2026-10-24）⇒ 板级工作暂停且不设期限。",
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
            print(f"[FIXPOINT-PACK] converged at round {iteration + 1}")
            break
        previous = state
    else:
        print("[FIXPOINT-PACK] 清单无法收敛")
        return 1

    closing = run_command([sys.executable, "-B", str(checker), "--mode", "evidence",
                           "--manifest", str(manifest_path), "--project-root", str(root)], root)
    if closing["exit_code"] != 0:
        print("[CLOSING] run-dir 出现未声明文件或哈希不符，构建中止")
        print(closing["stdout"]); return 1
    print("[CLOSING] run-dir 无未声明文件、清单一致")
    print(json.dumps({"status": "S6E_PACK_BUILT", "run_id": run_id,
                      "checks": [(c["name"], c["status"], c["exit_code"]) for c in checks],
                      "files": len(file_entries())}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())