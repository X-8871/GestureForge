#!/usr/bin/env python3
"""S6-A 冻结自证工具（F6 规则）：任何"冻结/交付"提交必须自证。

做法：把目标提交用 `git archive` 导出到隔离目录（不写被审工作树），然后用**该提交内的**
自检与两个交付检查器复跑：

  * `verification/s6_g0_selfcheck.py`（含 C11 清单/STATE 一致性）
  * `verification/check_stage_delivery.py --mode inputs`
  * `verification/check_stage_delivery.py --mode evidence`

三项都 exit 0 才判 `SELF_PROVEN`；任一项非 0 即 `NOT_SELF_PROVEN`，并记录真实退出码与输出。
额外记录该提交内被 STATE 声明的证据目录文件数（用于定位"声明强于产物"这类缺陷）。

用法（可多次 --commit）：
    python -B verification/export_selfproof.py --project-root D:/codex-worktrees/w6 \
        --commit 04ea58e1 --commit <r07 提交> \
        --out report/evidence/S6-A/s6a_g0_20261022_r07/export_selfproof.json

    # 提交前自验（导出当前工作区快照，不含 .git 与 tmp）：
    python -B verification/export_selfproof.py --project-root D:/codex-worktrees/w6 --worktree-snapshot ...
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

UTC8 = timezone(timedelta(hours=8))
BEHAVIOR = "docs/stage6/s6a_stage6_g0_behavior_v1.json"
DOC = "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"
SKIP_DIRS = {".git", "tmp", "__pycache__", ".pytest_cache"}
SKIP_SUFFIX = {".pyc", ".pyo"}


def run(command: list[str], cwd: Path) -> dict:
    completed = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", check=False)
    return {"command": subprocess.list2cmdline(command), "exit_code": completed.returncode,
            "stdout_tail": "\n".join(completed.stdout.strip().splitlines()[-3:]),
            "stderr_tail": "\n".join(completed.stderr.strip().splitlines()[-3:])}


def _mirror_checkout_config(root: Path, destination: Path) -> None:
    """镜像源仓库的换行配置，保证导出检出的字节与工作区口径一致。"""
    for key, fallback in (("core.autocrlf", "true"), ("core.eol", None)):
        value = subprocess.run(["git", "-C", str(root), "config", "--get", key],
                               capture_output=True, text=True, check=False).stdout.strip()
        if not value and fallback:
            value = fallback
        if value:
            subprocess.run(["git", "-C", str(destination), "config", key, value], check=False)


def prepare_commit_repo(root: Path, rev: str, destination: Path) -> Path:
    """克隆（借用对象，便宜）后检出目标提交：导出目录即一个可核验的 Git 仓库根。"""
    destination.parent.mkdir(parents=True, exist_ok=True)
    clone = subprocess.run(["git", "clone", "--quiet", "--shared", "--no-checkout",
                            str(root), str(destination)],
                           capture_output=True, text=True, check=False)
    if clone.returncode != 0:
        raise RuntimeError(f"git clone 失败：{clone.stderr.strip()}")
    _mirror_checkout_config(root, destination)
    checkout = subprocess.run(["git", "-C", str(destination), "checkout", "--quiet", rev],
                              capture_output=True, text=True, check=False)
    if checkout.returncode != 0:
        raise RuntimeError(f"checkout {rev} 失败：{checkout.stderr.strip()}")
    return destination


def prepare_snapshot_repo(root: Path, destination: Path, excludes: list[Path]) -> Path:
    """克隆 HEAD 后清空工作树、覆盖为当前工作区快照内容并提交（source_commit 仍可解析）。"""
    prepare_commit_repo(root, "HEAD", destination)
    for child in list(destination.iterdir()):
        if child.name == ".git":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    excluded = {path.resolve() for path in excludes if path is not None}
    count = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] in SKIP_DIRS:
            continue
        if path.suffix in SKIP_SUFFIX or any(part in SKIP_DIRS for part in relative.parts):
            continue
        if path.resolve() in excluded:
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        count += 1
    print(f"[snapshot] {count} 个文件（不含 .git/tmp 与本工具输出）")
    for command in (["git", "add", "-A"],
                    ["git", "-c", "user.email=selfproof@local", "-c", "user.name=selfproof",
                     "commit", "--quiet", "-m", "worktree snapshot for self-proof"]):
        subprocess.run(command, cwd=str(destination), capture_output=True, check=False)
    return destination


def align_by_manifest_hashes(tree: Path, manifest_rel: str) -> dict:
    """按清单已声明的哈希，在「原字节 / LF 归一 / CRLF 归一」三者中选择一个。

    只做换行口径选择：若三者都不匹配，说明内容确实不同——**保留原字节并登记**，由检查器如实报错。
    这样导出副本与清单绑定的工作区口径（O1：MD/JSON 为 CRLF、.py/STATE 为 LF）可比对。
    """
    manifest_path = tree / manifest_rel
    if not manifest_path.is_file():
        return {"aligned": 0, "unresolved": [], "note": "导出内没有清单，跳过口径对齐"}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    aligned = 0
    unresolved: list[str] = []
    for item in manifest.get("files", []):
        relative = str(item["path"]).replace("\\", "/")
        want = str(item["sha256"]).lower()
        path = tree / relative
        if not path.is_file():
            continue
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() == want:
            continue
        normalized = data.replace(b"\r\n", b"\n")
        candidates = (normalized, normalized.replace(b"\n", b"\r\n"))
        for candidate in candidates:
            if hashlib.sha256(candidate).hexdigest() == want:
                path.write_bytes(candidate)
                aligned += 1
                break
        else:
            unresolved.append(relative)
    return {"aligned": aligned, "unresolved": unresolved,
            "note": "仅选择换行口径（LF/CRLF）；两者都不匹配即内容不同，保留原字节并登记"}


def normalize_line_endings(tree: Path, source_root: Path) -> dict:
    """仅当内容与源工作区文件一致（差别只在换行）时，用源工作区字节替换导出文件。

    返回 {"aligned": n, "content_differs": [relpath, ...]}；内容真正不同的文件保留提交字节，
    交给检查器如实报错（不做任何内容级"修正"）。
    """
    aligned = 0
    content_differs: list[str] = []
    for path in sorted(tree.rglob("*")):
        if not path.is_file() or ".git" in path.relative_to(tree).parts:
            continue
        relative = path.relative_to(tree)
        source = source_root / relative
        if not source.is_file():
            continue
        exported = path.read_bytes()
        original = source.read_bytes()
        if exported == original:
            continue
        if exported.replace(b"\r\n", b"\n") == original.replace(b"\r\n", b"\n"):
            path.write_bytes(original)
            aligned += 1
        else:
            content_differs.append(relative.as_posix())
    return {"aligned": aligned, "content_differs": content_differs}


def self_prove(tree: Path, work: Path, label: str, source_root: Path | None = None,
               s6b_rel: str | None = None, s6a_rel: str | None = None) -> dict:
    behavior = tree / BEHAVIOR
    alignment = None
    if not behavior.is_file():
        return {"label": label, "verdict": "NOT_SELF_PROVEN", "error": f"导出内缺少 {BEHAVIOR}"}
    version_data = json.loads(behavior.read_text(encoding="utf-8"))
    # BLK-D1 修复：**取消按行为表 run_id 的隐式查找**（该字段曾被漏同步到上一轮 RunId，
    # 导致工具复算旧包 ⇒ 假 NOT_SELF_PROVEN）。现在必须显式给出 S6-A RunId。
    if not s6a_rel:
        return {"label": label, "verdict": "NOT_SELF_PROVEN",
                "error": "缺少显式 --s6a-run（BLK-D1 之后不再按行为表 run_id 隐式查找）"}
    evidence_rel = (s6a_rel if s6a_rel.startswith("report/evidence/")
                    else f"report/evidence/S6-A/{s6a_rel}")
    evidence = tree / evidence_rel
    # N-r07-1：**先**按工作区口径归一（内容一致、仅换行不同才写回），**再**按清单已声明哈希做最终口径选择。
    # 顺序颠倒会把刚对齐好的文件再翻回去，在 autocrlf=true 的干净克隆上产生 NOT_SELF_PROVEN 假阴性。
    worktree_alignment = None
    if source_root is not None:
        worktree_alignment = normalize_line_endings(tree, source_root)
    alignment = align_by_manifest_hashes(tree, f"{evidence_rel}/delivery_manifest.json")
    if worktree_alignment is not None:
        alignment = dict(alignment, worktree_bytes=worktree_alignment,
                         order_note="先工作区口径、后清单口径（N-r07-1 修正）")
    s6b_dir_rel = "report/evidence/S6-B"
    s6b_files = ([p for p in (tree / s6b_dir_rel).rglob("*") if p.is_file()]
                 if (tree / s6b_dir_rel).is_dir() else [])

    checks: list[dict] = []
    selfcheck_out = work / f"{label}_selfcheck.json"
    checks.append(dict(
        name="selfcheck（C11：清单 + STATE）" if not s6b_rel else "selfcheck（C11：仅 STATE 声明存在性；S6-B 模式下不复算 S6-A 旧轮次清单哈希）",
        **run([sys.executable, "-B", str(tree / "verification/s6_g0_selfcheck.py"),
               "--json", str(behavior), "--doc", str(tree / DOC),
               "--cases", str(evidence / "hand_computed_cases.json"),
               "--upstream", str(evidence / "upstream_bindings.json"),
               "--out", str(selfcheck_out), "--project-root", str(tree),
               "--evidence-dir", str(evidence),
               *(["--manifest", str(evidence / "delivery_manifest.json")] if not s6b_rel else []),
               "--state", str(tree / ".codex/STATE.md")], tree)))
    if not s6b_rel:
        # S6-A 轮次清单绑定的是该轮次构建时的源码字节；进入 S6-B 模式（工作区已前进）时
        # 旧轮次清单的源码哈希自然不再匹配，故只在非 S6-B 模式下复算 S6-A 清单。
        checks.append(dict(
            name="check_stage_delivery --mode inputs",
            **run([sys.executable, "-B", str(tree / "verification/check_stage_delivery.py"),
                   "--mode", "inputs", "--manifest", str(evidence / "inputs_manifest.json"),
                   "--project-root", str(tree)], tree)))
        checks.append(dict(
            name="check_stage_delivery --mode evidence",
            **run([sys.executable, "-B", str(tree / "verification/check_stage_delivery.py"),
                   "--mode", "evidence", "--manifest", str(evidence / "delivery_manifest.json"),
                   "--project-root", str(tree)], tree)))
    if s6b_rel:
        s6b_dir = tree / s6b_rel
        checks.append(dict(
            name="S6-B 确定性用例驱动（该提交内）",
            **run([sys.executable, "-B", str(tree / "verification/s6b_run_cases.py"),
                   "--project-root", str(tree), "--run-dir", str(s6b_dir)], tree)))
        checks.append(dict(
            name="S6-B check_stage_delivery --mode inputs",
            **run([sys.executable, "-B", str(tree / "verification/check_stage_delivery.py"),
                   "--mode", "inputs", "--manifest", str(s6b_dir / "inputs_manifest.json"),
                   "--project-root", str(tree)], tree)))
        checks.append(dict(
            name="S6-B check_stage_delivery --mode evidence",
            **run([sys.executable, "-B", str(tree / "verification/check_stage_delivery.py"),
                   "--mode", "evidence", "--manifest", str(s6b_dir / "delivery_manifest.json"),
                   "--project-root", str(tree)], tree)))
    selfcheck_status = None
    selfcheck_errors: list[str] = []
    if selfcheck_out.is_file():
        try:
            payload = json.loads(selfcheck_out.read_text(encoding="utf-8"))
            selfcheck_status = payload["status"]
            selfcheck_errors = list(payload.get("errors", []))[:5]
        except Exception:  # pragma: no cover - 结果文件损坏时如实留空
            selfcheck_status = "UNREADABLE"
    proven = all(item["exit_code"] == 0 for item in checks)
    return {
        "label": label,
        "newline_alignment": alignment,
        "artifact_version": version_data.get("artifact_version"),
        "run_id": run_id,
        "evidence_dir": evidence_rel,
        "evidence_dir_file_count": len([p for p in evidence.rglob("*") if p.is_file()]) if evidence.is_dir() else 0,
        "state_declared_s6b_dir_files_in_commit": len(s6b_files),
        "checks": checks,
        "selfcheck_status": selfcheck_status,
        "selfcheck_errors": selfcheck_errors,
        "verdict": "SELF_PROVEN" if proven else "NOT_SELF_PROVEN",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S6-A 冻结自证（导出副本复跑）")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--commit", action="append", default=[],
                        help="待自证提交（可多次）；与 --worktree-snapshot 可同时使用")
    parser.add_argument("--worktree-snapshot", action="store_true",
                        help="额外导出当前工作区快照做提交前自验")
    parser.add_argument("--s6b-run", default=None,
                        help="S6-B 证据目录（相对路径）：额外跑 S6-B 驱动 + 其 inputs/evidence 检查器")
    parser.add_argument("--out", default=None, help="报告输出路径（JSON）")
    parser.add_argument("--markdown", default=None, help="报告输出路径（Markdown）")
    args = parser.parse_args(argv)

    root = Path(args.project_root).resolve()
    out_path = Path(args.out).resolve() if args.out else None
    results: list[dict] = []
    work_root = Path(tempfile.mkdtemp(prefix="s6a_selfproof_"))
    try:
        for rev in args.commit:
            tree = prepare_commit_repo(root, rev, work_root / f"commit_{rev}")
            entry = self_prove(tree, work_root, f"commit_{rev}", source_root=root,
                               s6b_rel=args.s6b_run, s6a_rel=args.s6a_run)
            entry["subject"] = f"commit {rev}"
            try:
                entry["commit_tree"] = subprocess.run(["git", "-C", str(root), "rev-parse", f"{rev}^{{tree}}"],
                                                      capture_output=True, text=True, check=False).stdout.strip()
            except Exception:  # pragma: no cover
                entry["commit_tree"] = None
            results.append(entry)
        if args.worktree_snapshot:
            # 不排除本工具的既有输出：清单已声明它们，快照必须与清单一致（快照只是复制工作区字节）
            tree = prepare_snapshot_repo(root, work_root / "worktree", [])
            entry = self_prove(tree, work_root, "worktree_snapshot", source_root=root,
                               s6b_rel=args.s6b_run, s6a_rel=args.s6a_run)
            entry["subject"] = "worktree snapshot（提交前自验；不含 .git/tmp 与本工具输出）"
            results.append(entry)
    finally:
        pass

    # 活文档不进硬哈希集合（lead 裁定 (a)）：STATE 哈希仅作为信息性快照记录
    _state_path = root / ".codex/STATE.md"
    state_hash = (hashlib.sha256(_state_path.read_bytes()).hexdigest()
                  if _state_path is not None and _state_path.is_file() else None)
    report = {
        "schema_version": 1,
        "artifact": "s6a_export_selfproof",
        "task_id": "S6-A",
        "rule": "任何冻结/交付提交必须自证：导出该提交后，自检 + inputs + evidence 三项检查全部 exit 0。",
        "tool": "verification/export_selfproof.py",
        "generated_at": datetime.now(UTC8).strftime("%Y-%m-%d %H:%M:%S%z"),
        "subjects": results,
        "verdict": ("ALL_SELF_PROVEN" if results and all(r["verdict"] == "SELF_PROVEN" for r in results)
                    else "NOT_ALL_SELF_PROVEN"),
        "scope_statement": ("导出复跑只证明该提交的证据自足性与清单/STATE 一致性；"
                            "不代表语义正确、独立审查或实物验收通过。"),
        "degradation_note": ("S6-B 模式（--s6b-run）下**不复算 S6-A 旧轮次的 inputs/evidence 清单**："
                             "旧轮次清单绑定其构建时的源码字节，工作区前进后哈希自然不匹配（NB-10 显式声明）。"
                             "该模式下仍跑 S6-A 自检（仅校验 STATE 声明存在性）与 S6-B 驱动 + S6-B 两个检查器。"),
        "live_document_note": ("活文档（.codex/STATE.md）**不进硬哈希集合**（lead 裁定 (a)）：STATE 每轮维护都会变化，"
                              "绑哈希会让证据包当场失效；此处以信息性快照记录其哈希，F6 判定仍依赖「STATE 声明的文件/目录是否真实存在」。"),
        "state_snapshot_sha256": state_hash,
        "subject_note": ("报告主体至少包含：交付轮次的工作区快照；提交后可用同一命令追加 `--commit <交付提交>`，"
                         "把交付提交本身列为主体（N-r07-2）。报告存放在同 RunId 的 `_selfproof` 兄弟目录，"
                         "不属于被清单声明的运行目录，故可在提交后原地更新而不影响清单绑定。"),
        "newline_note": ("既有口径 O1：工作区 MD/JSON 为 CRLF、.py/STATE 为 LF，git blob 为 LF。"
                         "本工具只对「内容与工作区一致、仅换行不同」的文件做换行口径对齐，"
                         "内容真正不同的文件保留提交字节并由检查器如实报错；不对内容做任何修正。"),
        "work_dir_note": "每次运行的导出副本与自检结果落在系统临时目录，不写入被审工作树。",
    }
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.markdown:
        lines = ["# S6-A 冻结自证报告（导出副本复跑）", "",
                 f"- 规则：{report['rule']}", f"- 生成：{report['generated_at']}", ""]
        for entry in results:
            lines += [f"## {entry['subject']}", "",
                      f"- 判定：**{entry['verdict']}**；契约 `{entry.get('artifact_version')}`；"
                      f"RunId `{entry.get('run_id')}`",
                      f"- 该提交内 S6-B 证据目录文件数：**{entry.get('state_declared_s6b_dir_files_in_commit')}**"
                      f"（STATE 声明该目录时必须 > 0）",
                      f"- 证据目录文件数：{entry.get('evidence_dir_file_count')}", "",
                      "| 检查 | 真实退出码 |", "|---|---|"]
            for item in entry.get("checks", []):
                lines.append(f"| {item['name']} | {item['exit_code']} |")
            lines.append("")
        lines += [f"**总体判定：{report['verdict']}**", "", report["scope_statement"]]
        Path(args.markdown).resolve().write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": report["verdict"],
                      "subjects": [(r["subject"], r["verdict"],
                                    [c["exit_code"] for c in r.get("checks", [])]) for r in results]},
                     ensure_ascii=False))
    shutil.rmtree(work_root, ignore_errors=True)
    return 0 if report["verdict"] == "ALL_SELF_PROVEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
