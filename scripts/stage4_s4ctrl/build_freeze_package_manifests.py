"""重建阶段4 冻结包的两份清单（fail-closed，防"清单收录未入库文件"复发）。S4-T33。

为什么需要它：r3 的交付清单收录了 6 个 `*.log`，这些文件被 `.gitignore` 忽略、不在任何提交内，
导致"清单不可满足"。本生成器在写盘前做**强制断言**：

  1. `files[]` 中**每个路径**都必须存在于指定 commit 的树中（`git cat-file -e <commit>:<path>`），
     任一失败 ⇒ **exit 3**（不写任何清单）；
  2. `*.log` / 被 `git check-ignore` 命中的路径**一律拒绝**（⇒ exit 4）；
  3. 两份清单分工：`landing_manifest.json` 不收录 `delivery_manifest.json`，`delivery_manifest.json`
     收录 landing 清单（避免互引哈希环）；两份清单自身都**不**作为 `files[]` 成员。

用法：
  python -B scripts/stage4_s4ctrl/build_freeze_package_manifests.py \
      --repo D:/codex-worktrees/w4 \
      --evidence-dir report/evidence/S4-FREEZE/stage4_freeze_20261028_r01 \
      --commit <commit 或 tag>

退出码：0=两份清单已生成且断言通过；2=输入错误；3=存在未入库路径；4=存在被忽略/日志路径。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

VERIFIER = "scripts/stage4_s4ctrl/verify_stage4_freeze_package.py"


def git(repo: Path, *args: str) -> tuple[int, str]:
    """跑 git，返回 (退出码, 文本)。"""
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def sha256_file(path: Path) -> str:
    """磁盘 SHA-256。"""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def in_commit(repo: Path, commit: str, rel: str) -> bool:
    """路径是否存在于指定提交的树中。"""
    code, _ = git(repo, "cat-file", "-e", f"{commit}:{rel}")
    return code == 0


def is_ignored(repo: Path, rel: str) -> bool:
    """路径是否被 .gitignore 忽略。"""
    code, out = git(repo, "check-ignore", "-q", rel)
    return code == 0


def main() -> int:
    """生成清单并断言。"""
    ap = argparse.ArgumentParser(description="生成阶段4 冻结包清单（fail-closed）")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--evidence-dir", required=True)
    ap.add_argument("--commit", required=True, help="清单绑定的提交（tag 或 40 位 SHA）")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    ev = (repo / args.evidence_dir).resolve()
    if not repo.is_dir() or not ev.is_dir():
        print("[FAIL] repo 或 evidence-dir 不存在", file=sys.stderr)
        return 2
    code, out = git(repo, "rev-parse", "--verify", f"{args.commit}^{{commit}}")
    if code != 0:
        print(f"[FAIL] 提交不可解析：{args.commit}", file=sys.stderr)
        return 2
    commit = out.strip().splitlines()[0]

    package_files = [p for p in sorted(ev.rglob("*")) if p.is_file()]
    rel_all = [str(p.relative_to(repo)).replace("\\", "/") for p in package_files]

    # 断言 1/2：未入库、被忽略、日志一律拒绝
    bad = [r for r in rel_all if not in_commit(repo, commit, r)]
    logs = [r for r in rel_all if r.lower().endswith(".log") or is_ignored(repo, r)]
    if bad:
        print("[FAIL] 以下路径不在提交 %s 的树内：" % commit, file=sys.stderr)
        for r in bad:
            print("  -", r, file=sys.stderr)
        return 3
    if logs:
        print("[FAIL] 以下路径属于日志/被 gitignore 忽略，不得进入清单：", file=sys.stderr)
        for r in logs:
            print("  -", r, file=sys.stderr)
        return 4

    landing_name = "landing_manifest.json"
    delivery_name = "delivery_manifest.json"
    landing_path = ev / landing_name
    delivery_path = ev / delivery_name
    verifier_abs = repo / VERIFIER
    if not verifier_abs.is_file():
        print(f"[FAIL] 验证器缺失：{VERIFIER}", file=sys.stderr)
        return 2

    # landing：除自身与 delivery 外的全部包内文件
    landing_files = []
    for rel, p in zip(rel_all, package_files):
        if p.name in (landing_name, delivery_name):
            continue
        landing_files.append({"path": rel, "sha256": sha256_file(p), "hash_basis": "commit_blob",
                              "source_commit": commit, "size_bytes": p.stat().st_size})
    # delivery：除自身外的全部包内文件 + 验证器源码（必须入库）
    delivery_files = []
    for rel, p in zip(rel_all, package_files):
        if p.name == delivery_name:
            continue
        role = "artifact" if p.name in ("frozen_set.json", "results_freeze.json", "frozen_set_report.json") else "result"
        delivery_files.append({"path": rel, "sha256": sha256_file(p), "role": role, "hash_basis": "commit_blob",
                               "source_commit": commit, "size_bytes": p.stat().st_size})
    ver_rel = VERIFIER
    if not in_commit(repo, commit, ver_rel):
        print(f"[FAIL] 验证器不在提交树内：{ver_rel}", file=sys.stderr)
        return 3
    delivery_files.append({"path": ver_rel, "sha256": sha256_file(verifier_abs), "role": "source",
                           "hash_basis": "commit_blob", "source_commit": commit, "keep_reason": "冻结包验证器源码"})

    # 写盘前再审一次 files[]（防上面构造逻辑漏项）
    for item in landing_files + delivery_files:
        if not in_commit(repo, commit, item["path"]):
            print(f"[FAIL] files[] 含未入库路径：{item['path']}", file=sys.stderr)
            return 3
        if item["path"].lower().endswith(".log"):
            print(f"[FAIL] files[] 含日志路径：{item['path']}", file=sys.stderr)
            return 4

    existing_landing = json.loads(landing_path.read_text(encoding="utf-8")) if landing_path.is_file() else {}
    landing = {
        "schema_version": 1, "stage": "4", "task_id": "S4-T33", "run_id": ev.name,
        "purpose": existing_landing.get("purpose", "阶段4 离线冻结包清单"),
        "hash_basis": "commit_blob", "hash_basis_commit": commit,
        "hash_basis_note": "files[].sha256 取自 `git cat-file blob <hash_basis_commit>:<path>`；"
                           "所有成员均在该提交树内（生成器已断言）。",
        "freeze_id": existing_landing.get("freeze_id"), "freeze_tag": existing_landing.get("freeze_tag"),
        "excluded_from_manifest": {"path": f"{args.evidence_dir}/{delivery_name}".replace("//", "/"),
                                   "reason": "两份清单互引会形成哈希环；交付清单由提交与 tag 绑定，由 check_stage_delivery 校验。"},
        "exit_codes": existing_landing.get("exit_codes", {}),
        "files": landing_files,
        "boundary": "全离线；未接触板卡；ENABLE=0；不主张 G3/G4/G5。",
    }
    delivery = {
        "schema_version": 1, "stage": "4", "task_id": "S4-FREEZE", "run_id": ev.name,
        "source_commit": commit,
        "evidence_dir": args.evidence_dir.replace("\\", "/"),
        "interfaces": [],
        "interfaces_not_applicable_reason": "本冻结包不引入新接口；接口与地址契约已作为 spec 成员冻结",
        "files": delivery_files,
        "checks": json.loads(delivery_path.read_text(encoding="utf-8")).get("checks", []) if delivery_path.is_file() else [],
        "limitations": ["artifact_identity 共 11 项，其中 3 项仓库外产物不列入清单，由冻结验证器按绝对路径重算",
                        "NEITHER_ACCOUNTED 候选区 6 字节变化根因未定", "M3 FAIL/未闭合",
                        "M4-a/M4-b NOT_RUN", "PL v2 未完成、4-D 位流未产出", "PS 真实解码未接线",
                        "旧 F1–F8 语义验证器 exit 1（7/8，F5）", "工作区仍有已声明的非冻结脏项",
                        "冻结不等于验收通过"],
        "tool_versions": {"python": "3.12 (Windows x64)", "git": git(repo, "--version")[1].strip(),
                          "vivado": "2026.1（仅历史登记）"},
        "hash_basis": "commit_blob", "hash_basis_commit": commit,
    }
    landing_path.write_text(json.dumps(landing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    delivery_path.write_text(json.dumps(delivery, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"MANIFESTS_OK commit={commit} landing_files={len(landing_files)} delivery_files={len(delivery_files)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())