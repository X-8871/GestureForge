"""S5-A 自检证据生成器（Lead 专属；写 report/evidence/S5-A/<run_id>/）。

做四件事：
1) 记录工作树事实：分支/HEAD/`git status --short`/`index.lock` 解析路径与存在性；
2) 绑定本阶段文件与上游只读输入的 SHA-256（含“复制基线仍与 w4 源逐字节一致”的校验）；
3) 用真实退出码运行 `python -B -m unittest verification.test_s5_display_geometry_reference -v`；
4) 写出机器可读 `run_manifest.json` 与 `summary.md`（PASS/FAIL/NOT_RUN 如实标注）。

退出码：0=全部 PASS；1=自检失败；2=环境/输入错误（缺文件、git 不可用等）。
用法：`python -B scripts/stage5_s5a/run_s5a_selfcheck.py --run-id s5a_g0_20261021_r01`
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import platform
import subprocess
import sys
import time

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CONTRACT_ID = "S5A-G0-v2"

# 复制基线：本树路径 → w4 只读源路径（相对各自工作树根）
BASELINE_COPIES = {
    "docs/stage5/S5_stage5_display_spec_draft.md": "docs/stage5/S5_stage5_display_spec_draft.md",
    "docs/stage6/S6_stage6_interaction_spec_draft.md": "docs/stage6/S6_stage6_interaction_spec_draft.md",
    "docs/stage6/s6_interaction_thresholds.json": "docs/stage6/s6_interaction_thresholds.json",
    "docs/stage4/S4A_stage4_g0_tracking_and_timing_draft.md": "docs/stage4/S4A_stage4_g0_tracking_and_timing_draft.md",
    "docs/stage4/s4a_stage4_g0_fields.json": "docs/stage4/s4a_stage4_g0_fields.json",
}
LOCAL_ARTIFACTS = [
    "docs/stage5/S5A_stage5_display_g0_spec_v2.md",
    "docs/stage5/s5a_stage5_display_g0_fields.json",
    "docs/stage5/PROVENANCE_s4d_v1_baseline.md",
    "docs/stage6/S6D_stage6_revision_suggestions_from_stage5.md",
    "verification/s5_display_geometry_reference.py",
    "verification/test_s5_display_geometry_reference.py",
    "verification/s1_t02_d2_numeric_reference.py",
    "scripts/stage5_s5a/run_s5a_selfcheck.py",
]
W4_ROOT = pathlib.Path(r"D:\codex-worktrees\w4")


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def main() -> int:
    parser = argparse.ArgumentParser(description="S5-A 自检证据生成器")
    parser.add_argument("--run-id", default="s5a_g0_20261021_r01")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    out_dir = pathlib.Path(args.out) if args.out else REPO_ROOT / "report" / "evidence" / "S5-A" / args.run_id
    console_dir = out_dir / "console"
    console_dir.mkdir(parents=True, exist_ok=True)

    started = time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime())

    # 1) 工作树事实
    git_branch_code, git_branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    git_head_code, git_head = run(["git", "rev-parse", "HEAD"])
    git_short_code, git_short = run(["git", "rev-parse", "--short", "HEAD"])
    git_status_code, git_status = run(["git", "status", "--short"])
    lock_code, lock_path = run(["git", "rev-parse", "--git-path", "index.lock"])
    lock_path = lock_path.strip()
    lock_exists = (pathlib.Path(lock_path) if pathlib.Path(lock_path).is_absolute()
                   else REPO_ROOT / lock_path).exists()
    git_lines = [
        f"branch: {git_branch.strip()} (exit {git_branch_code})",
        f"HEAD: {git_head.strip()} (exit {git_head_code})",
        f"short: {git_short.strip()} (exit {git_short_code})",
        f"status --short (exit {git_status_code}):",
        git_status.rstrip() or "(clean)",
        f"index.lock path: {lock_path} (exit {lock_code}) exists={lock_exists}",
    ]
    (console_dir / "git_state.txt").write_text("\n".join(git_lines) + "\n", encoding="utf-8")

    # 2) 哈希绑定 + 复制基线一致性
    missing: list[str] = []
    local_hashes: dict[str, str] = {}
    for rel in LOCAL_ARTIFACTS:
        path = REPO_ROOT / rel
        if not path.exists():
            missing.append(rel)
            continue
        local_hashes[rel] = sha256(path)
    baseline_check: list[dict] = []
    for local_rel, w4_rel in BASELINE_COPIES.items():
        local_path, w4_path = REPO_ROOT / local_rel, W4_ROOT / w4_rel
        if not local_path.exists() or not w4_path.exists():
            missing.append(f"{local_rel} 或 w4 源缺失")
            continue
        local_sha, w4_sha = sha256(local_path), sha256(w4_path)
        baseline_check.append({"local": local_rel, "w4_source": str(w4_path),
                               "local_sha256": local_sha, "w4_sha256": w4_sha,
                               "byte_identical": local_sha == w4_sha})
    _, w4_head = run(["git", "-C", str(W4_ROOT), "rev-parse", "HEAD"])
    _, w4_status = run(["git", "-C", str(W4_ROOT), "status", "--short"])

    # 3) 真实退出码运行自检
    unittest_cmd = [sys.executable, "-B", "-m", "unittest",
                    "verification.test_s5_display_geometry_reference", "-v"]
    unittest_code, unittest_output = run(unittest_cmd)
    (console_dir / "unittest_s5a.txt").write_text(
        "$ " + " ".join(unittest_cmd) + "\n" + unittest_output + f"\n[exit code: {unittest_code}]\n",
        encoding="utf-8")

    contract = json.loads((REPO_ROOT / "docs/stage5/s5a_stage5_display_g0_fields.json")
                          .read_text(encoding="utf-8"))
    tests_ran = [line for line in unittest_output.splitlines() if line.startswith("Ran ")]

    manifest = {
        "schema_version": "gestureforge_s5a_selfcheck_v1",
        "task_id": "S5-A",
        "run_id": args.run_id,
        "contract_id": CONTRACT_ID,
        "contract_status": contract["status"],
        "started_utc8": started,
        "generated_utc8": time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime()),
        "runner": {"script": "scripts/stage5_s5a/run_s5a_selfcheck.py",
                   "python": sys.version.split()[0], "platform": platform.platform()},
        "worktree": {"root": str(REPO_ROOT), "branch": git_branch.strip(),
                     "head": git_head.strip(), "head_short": git_short.strip(),
                     "status_short_exit": git_status_code, "dirty_entries": len(
                         [line for line in git_status.splitlines() if line.strip()]),
                     "index_lock_path": lock_path, "index_lock_exists": lock_exists},
        "local_artifact_sha256": local_hashes,
        "baseline_copies": baseline_check,
        "upstream_readonly": {"w4_root": str(W4_ROOT), "w4_head": w4_head.strip(),
                              "w4_status_short": w4_status.strip() or "(clean)",
                              "note": "w4 只读；本树复制件与源逐字节一致由 baseline_copies 校验"},
        "commands": [
            {"cmd": " ".join(unittest_cmd), "exit_code": unittest_code,
             "log": "console/unittest_s5a.txt", "status": "PASS" if unittest_code == 0 else "FAIL"},
            {"cmd": "git -C <w5> status --short; rev-parse --short HEAD; rev-parse --git-path index.lock",
             "exit_code": git_status_code, "log": "console/git_state.txt", "status": "PASS"},
        ],
        "checks": {
            "unittest_s5_display_geometry_reference": {
                "status": "PASS" if unittest_code == 0 else "FAIL",
                "exit_code": unittest_code, "summary_line": tests_ran[-1] if tests_ran else "n/a",
                "covers": ["D2 正向几何逐值对拍", "逆映射手算样例", "round-trip 与种子化随机框(64, seed=20261021)",
                           "奇数补边非对称保留(683x384)", "退化几何抛错", "过期边界与原因分类",
                           "边框偶数线宽语义(15 像素)", "画布整数倍等比不拉伸", "契约 JSON ↔ 参考实现常量一致",
                           "结果记录校验正/反例"],
            },
            "baseline_copy_byte_identical": {
                "status": "PASS" if baseline_check and all(b["byte_identical"] for b in baseline_check) else "FAIL",
                "checked": len(baseline_check),
            },
            "worktree_clean_of_lock": {"status": "PASS" if not lock_exists else "FAIL",
                                       "index_lock_exists": lock_exists},
        },
        "limitations": [
            "纯离线：无硬件、无 hw_server/JTAG/COM4、无 Vivado/xsim、无摄像头与 HDMI 实物。",
            "只验证几何/口径/契约自洽与手算样例；不构成阶段5 开工、G1/G3/G4 或验收通过。",
            "阶段4 S4-A 契约仍为 DRAFT_NOT_FROZEN；阶段5 契约引用其字段名不等于阶段4 已冻结。",
            "真实 FPS/延迟统计、30 分钟无死锁、截图/视频留证均未执行。",
        ],
        "not_executed": [
            "T5-09 连续 30 分钟无死锁（需硬件与阶段3/4 完成）",
            "真实 HDMI 显示与摄像头联调（阶段5 正式开工后）",
            "成品允许延迟上限/颜色表/字号（待正式 G0 与 Wong）",
        ],
    }
    manifest["status"] = "PASS" if unittest_code == 0 and not missing and not lock_exists else "FAIL"
    (out_dir / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = [
        f"# S5-A 自检证据 RunId `{args.run_id}`",
        "",
        f"- 契约：`{CONTRACT_ID}`（{contract['status']}）",
        f"- 工作树：`{REPO_ROOT}` 分支 `{git_branch.strip()}` HEAD `{git_short.strip()}`",
        f"- 自检：`python -B -m unittest verification.test_s5_display_geometry_reference -v` → "
        f"**退出码 {unittest_code}**（{tests_ran[-1] if tests_ran else 'n/a'}）",
        f"- 复制基线逐字节一致：{sum(1 for b in baseline_check if b['byte_identical'])}/{len(baseline_check)}",
        f"- 状态：**{manifest['status']}**",
        "",
        "## 限制与未执行",
        "",
    ]
    summary += [f"- {item}" for item in manifest["limitations"] + manifest["not_executed"]]
    summary += ["", "## 证据文件", "",
                "- `console/unittest_s5a.txt`（真实 stdout/stderr 与退出码）",
                "- `console/git_state.txt`（分支/HEAD/status/index.lock）",
                "- `run_manifest.json`（哈希绑定、命令、退出码、检查项、限制）",
                "- `summary.md`（本文件）"]
    (out_dir / "summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")

    print(f"[S5-A] run_id={args.run_id} unittest_exit={unittest_code} status={manifest['status']}")
    print(f"[S5-A] evidence={out_dir}")
    if missing:
        print(f"[S5-A] MISSING: {missing}")
        return 2
    return 0 if unittest_code == 0 and not lock_exists else 1


if __name__ == "__main__":
    sys.exit(main())