"""重建阶段4 冻结包清单（S4-T33，r4 起：哈希基座结构性加固）。

设计要点（针对本项目第 5 次"哈希基座"类缺陷）：
  1. **唯一声明值来源 = `git cat-file blob <commit>:<path>`**：`files[]` 每项的 sha256 都按提交
     blob 计算，**禁止**"磁盘字节算完后声明 commit_blob"；
  2. 写盘统一 `newline="\\n"`（LF），使 disk 与 blob 尽量一致；但声明值仍以 blob 为准；
  3. 两种基座**不得混于同一项**：能取 blob 的项一律 `commit_blob`；确实不在提交内的项，
     landing 清单直接拒绝（exit 3），delivery 清单允许并**显式** `worktree_disk` 且并列
     `blob_available=false`；
  4. **写盘后立即自检**：调用 `check_manifest_hash_basis.py --mode strict` 与
     `check_stage_delivery.py --mode evidence`，任一非 0 ⇒ 删除刚写的清单并 **exit 6**，
     绝不打印成功（失败当场暴露，不靠外部复审）；
  5. **确定性**：同一输入连续运行，两份清单逐字节相同（排序固定、无时间戳）。

用法：
  python -B scripts/stage4_s4ctrl/build_freeze_package_manifests.py \
      --repo D:/codex-worktrees/w4 \
      --evidence-dir report/evidence/S4-FREEZE/stage4_freeze_20261028_r04 \
      --commit <冻结包提交>

退出码：0=成功且自检通过；2=输入错误；3=存在未入库路径；4=存在日志/被忽略项；5=输入类文件自指；6=自检失败。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

VERIFIER = "scripts/stage4_s4ctrl/verify_stage4_freeze_package.py"
GATE = r"D:\FPGA_Competition\verification\check_manifest_hash_basis.py"
DELIVERY = r"D:\FPGA_Competition\verification\check_stage_delivery.py"
MANIFEST_NAMES = ("landing_manifest.json", "delivery_manifest.json")


def git(repo: Path, *args: str) -> tuple[int, str]:
    """跑 git，返回 (退出码, 文本)。"""
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def git_bytes(repo: Path, *args: str) -> bytes:
    """跑 git 取原始字节。"""
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True).stdout


def blob_sha256(repo: Path, commit: str, rel: str) -> str | None:
    """按提交 blob 计算 SHA-256；路径不在提交内返回 None。"""
    code, _ = git(repo, "cat-file", "-e", f"{commit}:{rel}")
    if code != 0:
        return None
    return hashlib.sha256(git_bytes(repo, "cat-file", "blob", f"{commit}:{rel}")).hexdigest()


def disk_sha256(path: Path) -> str:
    """磁盘字节 SHA-256（仅用于显式 worktree_disk 项）。"""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path: Path, obj: dict) -> None:
    """以 LF 换行写 JSON（避免 CRLF 造成 disk/blob 分歧）。"""
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    """生成清单、自检、失败即回滚。"""
    ap = argparse.ArgumentParser(description="生成阶段4 冻结包清单（哈希基座加固）")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--evidence-dir", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--checks", default="", help="可选：checks 列表 JSON 路径")
    ap.add_argument("--no-selfcheck", action="store_true", help="仅调试用：跳过写盘后自检")
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
    _, tree_out = git(repo, "rev-parse", f"{commit}^{{tree}}")
    tree = tree_out.strip().splitlines()[0]

    package_files = [p for p in sorted(ev.rglob("*")) if p.is_file()]
    for p in package_files:
        rel = str(p.relative_to(repo)).replace("\\", "/")
        if rel.lower().endswith(".log"):
            print(f"[FAIL] 包内不得含日志：{rel}", file=sys.stderr)
            return 4
        if git(repo, "check-ignore", "-q", rel)[0] == 0:
            print(f"[FAIL] 包内不得含被 gitignore 忽略项：{rel}", file=sys.stderr)
            return 4

    # 输入类文件不得包含被绑定提交/树的哈希（自指防护）
    self_ref = []
    for p in package_files:
        if p.name in MANIFEST_NAMES:
            continue
        text = p.read_text(encoding="utf-8", errors="replace").lower()
        if commit.lower() in text or tree.lower() in text:
            self_ref.append(str(p.relative_to(repo)).replace("\\", "/"))
    if self_ref:
        print("[FAIL] 输入类文件包含被绑定提交/树的哈希（自指）：", file=sys.stderr)
        for rel in self_ref:
            print("  -", rel, file=sys.stderr)
        return 5

    # ---- landing：除两份清单外的全部包内文件，全部必须可解析到提交 blob ----
    landing_files = []
    for p in package_files:
        if p.name in MANIFEST_NAMES:
            continue
        rel = str(p.relative_to(repo)).replace("\\", "/")
        h = blob_sha256(repo, commit, rel)
        if h is None:
            print(f"[FAIL] landing 成员不在提交 {commit} 内：{rel}", file=sys.stderr)
            return 3
        landing_files.append({"path": rel, "sha256": h, "hash_basis": "commit_blob",
                              "source_commit": commit, "size_bytes": p.stat().st_size})

    # ---- delivery：除自身外的全部包内文件 + 验证器源码 ----
    delivery_files = []
    for p in package_files:
        if p.name == "delivery_manifest.json":
            continue
        rel = str(p.relative_to(repo)).replace("\\", "/")
        h = blob_sha256(repo, commit, rel)
        if h is None:
            # 不在提交内：必须显式 worktree_disk 且并列 blob 不可得
            delivery_files.append({"path": rel, "sha256": disk_sha256(p), "role": "result",
                                   "hash_basis": "worktree_disk", "blob_available": False})
        else:
            role = "artifact" if p.name in ("frozen_set.json", "results_freeze.json",
                                            "frozen_set_report.json") else "result"
            delivery_files.append({"path": rel, "sha256": h, "role": role,
                                   "hash_basis": "commit_blob", "source_commit": commit,
                                   "size_bytes": p.stat().st_size})
    ver_h = blob_sha256(repo, commit, VERIFIER)
    if ver_h is None:
        print(f"[FAIL] 验证器不在提交树内：{VERIFIER}", file=sys.stderr)
        return 3
    delivery_files.append({"path": VERIFIER, "sha256": ver_h, "role": "source",
                           "hash_basis": "commit_blob", "source_commit": commit,
                           "keep_reason": "冻结包验证器源码"})

    if args.checks:
        checks = json.loads(Path(args.checks).read_text(encoding="utf-8"))
    else:
        checks = []
        for name, label in (("selftest", "freeze_verifier_selftest"),
                            ("verifier_repo", "freeze_verifier_repo"),
                            ("clean_export", "freeze_verifier_clean_export")):
            f = ev / f"exit_{name}.txt"
            if f.is_file():
                txt = f.read_text(encoding="utf-8")
                rc = int(txt.split("exit=")[1].split()[0])
                checks.append({"name": label, "status": "PASS" if rc == 0 else "FAIL",
                               "command": f"see exit_{name}.txt", "exit_code": rc,
                               "reason": None if rc == 0 else "见 stdout"})

    landing = {
        "schema_version": 1, "stage": "4", "task_id": "S4-T33", "run_id": ev.name,
        "purpose": "阶段4 离线冻结包（输入类成员清单；验证输出见兄弟 RunId）",
        "hash_basis": "commit_blob", "hash_basis_commit": commit,
        "hash_basis_note": "files[].sha256 一律取自 `git cat-file blob <hash_basis_commit>:<path>`；"
                           "生成器仅按 blob 口径计算，且写盘后自检两条门禁。",
        "freeze_id": "stage4-offline-freeze-20261028-r4",
        "freeze_tag": "stage4-offline-freeze-20261028-r4",
        "excluded_from_manifest": {
            "paths": [f"{args.evidence_dir}/delivery_manifest.json".replace("//", "/")],
            "reason": "两份清单互引会形成哈希环；交付清单由提交与 tag 绑定，并由 check_stage_delivery 校验。"},
        "files": landing_files,
        "boundary": "全离线；未接触板卡；ENABLE=0；不主张 G3/G4/G5。",
    }
    delivery = {
        "schema_version": 1, "stage": "4", "task_id": "S4-FREEZE", "run_id": ev.name,
        "source_commit": commit,
        "evidence_dir": args.evidence_dir.replace("\\", "/"),
        "interfaces": [],
        "interfaces_not_applicable_reason": "本清单不引入新接口；接口与地址契约已作为 spec 成员冻结",
        "files": delivery_files,
        "checks": checks,
        "limitations": ["artifact_identity 共 11 项，其中 3 项仓库外产物不列入清单，由冻结验证器按绝对路径重算",
                        "NEITHER_ACCOUNTED 候选区 6 字节变化根因未定", "M3 FAIL/未闭合",
                        "M4-a/M4-b NOT_RUN", "PL v2 未完成、4-D 位流未产出", "PS 真实解码未接线",
                        "旧 F1–F8 语义验证器 exit 1（7/8，F5）", "工作区仍有已声明的非冻结脏项",
                        "冻结不等于验收通过"],
        "tool_versions": {"python": "3.12 (Windows x64)",
                          "git": git(repo, "--version")[1].strip(),
                          "vivado": "2026.1（仅历史登记）"},
        "hash_basis": "commit_blob", "hash_basis_commit": commit,
    }

    landing_path = ev / "landing_manifest.json"
    delivery_path = ev / "delivery_manifest.json"
    dump(landing_path, landing)
    dump(delivery_path, delivery)

    if not args.no_selfcheck:
        gcode = subprocess.run([sys.executable, "-B", GATE, "--repo", str(repo), "--commit", commit,
                                "--paths", str(landing_path.relative_to(repo)), "--mode", "strict"],
                               capture_output=True, text=True)
        dcode = subprocess.run([sys.executable, "-B", DELIVERY, "--mode", "evidence",
                                "--manifest", str(delivery_path), "--project-root", str(repo)],
                               capture_output=True, text=True)
        if gcode.returncode != 0 or dcode.returncode != 0:
            print("[FAIL] 写盘后自检未通过，已回滚清单：", file=sys.stderr)
            print("  gate:", gcode.returncode, (gcode.stdout or "").strip()[-600:], file=sys.stderr)
            print("  delivery:", dcode.returncode, (dcode.stdout or "").strip()[-600:], file=sys.stderr)
            landing_path.unlink(missing_ok=True)
            delivery_path.unlink(missing_ok=True)
            return 6
    print(f"MANIFESTS_OK commit={commit} landing_files={len(landing_files)} delivery_files={len(delivery_files)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())