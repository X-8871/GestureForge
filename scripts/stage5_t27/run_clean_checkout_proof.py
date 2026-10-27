#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T27 **干净检出自证**（N1 验收）：独立检出里复跑两套门禁，必须 exit 0。

做法
====
1. `git clone --shared --no-checkout --single-branch --branch <branch> <w5> <tmp>/clean_<commit>`
   （独立 `.git`、独立工作树；不写 w5 的 .git）；
2. **先检出三处 `.gitattributes`**（根 + `scripts/stage5_t27/` + `report/evidence/S5-T27/`），
   否则后续 checkout 读不到 `-text` 规则、`core.autocrlf` 会把 LF 转 CRLF（N1 的原始成因）；
3. 再检出 r02 证据包与源码绑定路径；
4. 在副本内跑：
   - `check_manifest_hash_basis.py --mode strict` / `--mode declared-only`（针对 delivery_manifest 与 hash_basis_manifest）
   - `check_stage_delivery.py --mode evidence`（project-root = 副本根）
5. 记录真实退出码与关键输出。

只读承诺：只读提交内容；副本与输出在 `tmp/5/S5-T27/**`（自证包目录除外，由调用方指定）。
退出码：0 = 全部门禁 0；1 = 有门禁非 0；2 = 输入/环境错误。
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
GATE = pathlib.Path("D:/FPGA_Competition/verification/check_manifest_hash_basis.py")
CHECKER = pathlib.Path("D:/FPGA_Competition/verification/check_stage_delivery.py")
RUN_DIR = "report/evidence/S5-T27/s5t27_replay_colour_20261027_r02"
ATTR_FILES = (".gitattributes", "scripts/stage5_t27/.gitattributes", "report/evidence/S5-T27/.gitattributes")
EXTRA_PATHS = ("docs/stage5/S5T27_replay_colour_input_path_v1.md",
               "scripts/stage5_t03/s5t03_replay_colour_input.py",
               "scripts/stage5_t03/s5t03_replay_colour_regression.py",
               "scripts/stage5_t03/test_s5t03_replay_colour.py",
               "scripts/stage5_t27/run_s5t27_evidence.py",
               "scripts/stage5_t27/finalize_manifest_basis.py",
               "verification/s5_display_geometry_reference.py")


def run(cmd: list[str], cwd: pathlib.Path | None = None) -> dict:
    completed = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", cwd=str(cwd) if cwd else None)
    return {"command": " ".join(cmd), "exit_code": completed.returncode,
            "stdout": completed.stdout, "stderr": completed.stderr}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument("--branch", default="stage5-display-prep")
    parser.add_argument("--out", required=True, help="自证包目录（相对仓库根）")
    args = parser.parse_args(argv)

    out_dir = REPO_ROOT / args.out
    if out_dir.exists() and any(out_dir.iterdir()):
        print(f"[ENV_ERROR] 输出目录非空：{out_dir}", file=sys.stderr)
        return 2
    (out_dir / "console").mkdir(parents=True, exist_ok=True)

    resolved = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "--verify",
                              f"{args.commit}^{{commit}}"], capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
    if resolved.returncode != 0:
        print(f"[ENV_ERROR] 提交不可解析：{args.commit}", file=sys.stderr)
        return 2
    commit = resolved.stdout.strip()
    clone_dir = REPO_ROOT / "tmp" / "5" / "S5-T27" / f"clean_{commit[:12]}"
    if clone_dir.exists():
        shutil.rmtree(clone_dir)

    clone = run(["git", "clone", "--shared", "--no-checkout", "--single-branch",
                 "--branch", args.branch, str(REPO_ROOT), str(clone_dir)])
    if clone["exit_code"] != 0:
        (out_dir / "console" / "clone.txt").write_text("\n".join([
            f"command={clone['command']}", f"exit_code={clone['exit_code']}",
            clone["stderr"]]), encoding="utf-8")
        print("[ENV_ERROR] clone 失败", file=sys.stderr)
        return 2
    attr = run(["git", "-C", str(clone_dir), "checkout", commit, "--", *ATTR_FILES])
    rest = run(["git", "-C", str(clone_dir), "checkout", commit, "--", RUN_DIR, *EXTRA_PATHS])
    toplevel = run(["git", "-C", str(clone_dir), "rev-parse", "--show-toplevel"])
    (out_dir / "console" / "clean_checkout.txt").write_text("\n".join([
        f"clone_command={clone['command']}", f"clone_exit_code={clone['exit_code']}",
        f"attributes_first_command={attr['command']}", f"attributes_exit_code={attr['exit_code']}",
        f"content_command={rest['command']}", f"content_exit_code={rest['exit_code']}",
        f"toplevel={toplevel['stdout'].strip()}", f"clone_dir={clone_dir}",
        "说明：先检出 .gitattributes 再检出内容——否则 autocrlf 会把 LF 转 CRLF（N1 成因）", ""]),
        encoding="utf-8")

    manifest = f"{RUN_DIR}/delivery_manifest.json"
    basis = f"{RUN_DIR}/hash_basis_manifest.json"
    results: dict[str, dict] = {}
    for name, cmd in (
            ("gate_strict_delivery", [sys.executable, "-B", str(GATE), "--repo", str(clone_dir),
                                      "--commit", commit, "--paths", manifest, "--mode", "strict", "--json"]),
            ("gate_declared_delivery", [sys.executable, "-B", str(GATE), "--repo", str(clone_dir),
                                        "--commit", commit, "--paths", manifest,
                                        "--mode", "declared-only", "--json"]),
            ("gate_strict_basis", [sys.executable, "-B", str(GATE), "--repo", str(clone_dir),
                                   "--commit", commit, "--paths", basis, "--mode", "strict", "--json"]),
            ("gate_declared_basis", [sys.executable, "-B", str(GATE), "--repo", str(clone_dir),
                                     "--commit", commit, "--paths", basis,
                                     "--mode", "declared-only", "--json"]),
            ("checker_evidence", [sys.executable, "-B", str(CHECKER), "--mode", "evidence",
                                  "--project-root", str(clone_dir),
                                  "--manifest", str(clone_dir / manifest)])):
        results[name] = run(cmd)
        (out_dir / "console" / f"{name}.txt").write_text("\n".join([
            f"command={results[name]['command']}", f"exit_code={results[name]['exit_code']}",
            "--- stdout ---", results[name]["stdout"].rstrip(),
            "--- stderr ---", results[name]["stderr"].rstrip(), ""]), encoding="utf-8")

    ok = all(item["exit_code"] == 0 for item in results.values())
    payload = {
        "task_id": "S5-T27", "run_id": out_dir.name,
        "purpose": "N1 验收：独立检出（干净工作树）内复跑哈希基座门禁与交付检查器",
        "commit": commit, "clone_dir": str(clone_dir),
        "attributes_checked_out_first": list(ATTR_FILES),
        "exit_codes": {name: item["exit_code"] for name, item in results.items()},
        "verdict": "CLEAN_CHECKOUT_PASS" if ok else "CLEAN_CHECKOUT_FAIL",
        "notes": [
            "副本为部分检出（只取 r02 证据包 + 源码绑定 + .gitattributes），不含与自证无关的历史证据。",
            "本自证只证明字节基座与包装门禁在干净检出下一致，不代表语义/审查/关口通过。",
        ],
    }
    (out_dir / "results_clean_checkout.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())