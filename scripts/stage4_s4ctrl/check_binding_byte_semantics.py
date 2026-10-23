#!/usr/bin/env python3
"""证据绑定字节口径核查（只读，N-1 支撑）。

对契约 `upstream_bindings`、缺口登记表 `basis_bindings` 及契约自身，逐项测量三种口径：
  1. 工作树**磁盘字节** SHA-256；
  2. `git hash-object`（应用 clean 过滤器，即“将入库的字节”）SHA-256；
  3. `git hash-object --no-filters`（原始字节）SHA-256；
并读取 `git check-attr` 判定该路径的换行属性归属，最后与清单声明的 SHA 比对。

目的：判定“声明的是磁盘字节还是 blob 字节”，为下一版显式声明绑定口径、以及需要改绑的条目提供事实。

退出码：0 = 分析完成；1 = 存在声明值两种口径都不匹配（真问题）；2 = 输入/环境错误。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
CN = timezone(timedelta(hours=8))

CONTRACT = WORKTREE / "docs" / "stage4" / "s4b_shared_input_result_contract.json"
REGISTRY = WORKTREE / "docs" / "stage4" / "S4B_raw_system_g0_gap_registry.json"

# 路径前缀 → 所属工作树（用于 git 口径测量）
TREE_ROOTS = (
    ("D:\\codex-worktrees\\w4", Path("D:/codex-worktrees/w4")),
    ("D:\\codex-worktrees\\w5", Path("D:/codex-worktrees/w5")),
    ("D:\\codex-worktrees\\dbdf", Path("D:/codex-worktrees/dbdf")),
    ("D:\\FPGA_Competition\\w2b", Path("D:/FPGA_Competition/w2b")),
    ("D:\\FPGA_Competition", Path("D:/FPGA_Competition")),
)


def sha256_of(path: Path) -> str:
    """按 1 MiB 分块计算磁盘字节 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_path(text: str) -> Path:
    """相对路径按本工作树解析，绝对路径原样使用。"""
    path = Path(text)
    return path if path.is_absolute() else WORKTREE / text


def owning_tree(path: Path) -> Path:
    """返回该路径所属的 git 工作树根。"""
    normalised = str(path).replace("\\", "/")
    for prefix, root in TREE_ROOTS:
        if normalised.lower().startswith(prefix.replace("\\", "/").lower()):
            return root
    return WORKTREE


def git(cmd: list[str]) -> tuple[int, str, str]:
    """执行只读 git 命令。"""
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def git_bytes(cmd: list[str]) -> tuple[int, bytes]:
    """执行只读 git 命令并返回原始字节（不做换行翻译）。"""
    proc = subprocess.run(cmd, capture_output=True)
    return proc.returncode, proc.stdout


def line_ending_counts(data: bytes) -> dict[str, int]:
    """统计 CR / LF / CRLF 数量（供口径判定）。"""
    return {"cr": data.count(b"\r"), "lf": data.count(b"\n"), "crlf": data.count(b"\r\n")}


def measure(label: str, path_text: str, declared: str | None, declared_basis: str | None = None) -> dict[str, object]:
    """测量一个绑定条目的三种口径，并按声明的字节口径判定。"""
    path = resolve_path(path_text)
    basis = declared_basis or "worktree_disk_bytes"
    entry: dict[str, object] = {"label": label, "path": str(path), "declared_sha256": declared,
                                "declared_byte_basis": basis}
    if not path.is_file():
        entry["status"] = "MISSING"
        return entry
    entry["disk_sha256"] = sha256_of(path)
    tree = owning_tree(path)
    entry["git_tree"] = str(tree)
    rel = str(path.relative_to(tree)).replace("\\", "/")

    code, out, err = git(["git", "-C", str(tree), "hash-object", "--", str(path)])
    entry["hash_object_filtered"] = out if code == 0 else None
    entry["hash_object_filtered_exit"] = code
    code_raw, out_raw, err_raw = git(["git", "-C", str(tree), "hash-object", "--no-filters", "--", str(path)])
    entry["hash_object_raw"] = out_raw if code_raw == 0 else None
    code_ls, out_ls, _ = git(["git", "-C", str(tree), "ls-tree", "HEAD", "--", rel])
    committed = out_ls.split()[2] if code_ls == 0 and out_ls else None
    entry["committed_blob_object"] = committed
    # committed blob 的内容必须按原始字节取（text=True 会翻译换行，不可用）
    code_cat, blob_bytes = git_bytes(["git", "-C", str(tree), "cat-file", "blob", f"HEAD:{rel}"])
    entry["committed_blob_content_sha256"] = (
        hashlib.sha256(blob_bytes).hexdigest() if code_cat == 0 else None
    )
    entry["committed_blob_size"] = len(blob_bytes) if code_cat == 0 else None
    disk_bytes = path.read_bytes()
    entry["disk_size"] = len(disk_bytes)
    entry["disk_line_endings"] = line_ending_counts(disk_bytes)
    entry["blob_line_endings"] = line_ending_counts(blob_bytes) if code_cat == 0 else None
    code_attr, out_attr, _ = git(["git", "-C", str(tree), "check-attr", "-a", "--", rel])
    entry["attributes"] = out_attr or "(none)"

    declared_matches = {
        "disk": declared is not None and declared == entry.get("disk_sha256"),
        "filtered": declared is not None and declared == entry.get("hash_object_filtered"),
        "raw": declared is not None and declared == entry.get("hash_object_raw"),
        "committed_blob_content": declared is not None
        and declared == entry.get("committed_blob_content_sha256"),
    }
    entry["declared_matches"] = declared_matches
    expected_key = "committed_blob_content" if basis == "git_blob_content" else "disk"
    entry["expected_basis_key"] = expected_key
    if declared is None:
        entry["status"] = "NO_DECLARED_SHA"
    elif declared_matches[expected_key]:
        entry["status"] = "MATCH"
        entry["matched_basis"] = expected_key
    elif any(declared_matches.values()):
        entry["status"] = "MATCH_WRONG_BASIS"
        entry["matched_basis"] = [k for k, v in declared_matches.items() if v]
    else:
        entry["status"] = "MISMATCH_ALL_BASES"
    return entry


def main() -> int:
    """执行全部测量。"""
    parser = argparse.ArgumentParser(description="证据绑定字节口径核查")
    parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()

    if not CONTRACT.is_file() or not REGISTRY.is_file():
        print("[FAIL] 缺少契约或缺口登记表")
        return 2
    out_dir = Path(args.evidence_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        print(f"[FAIL] 证据目录非空：{out_dir}")
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    targets: list[tuple[str, str, str | None, str | None]] = []
    for binding in contract["upstream_bindings"]:
        targets.append((f"contract.upstream_bindings[{binding['id']}]", binding["path"],
                        binding.get("sha256"), binding.get("byte_basis")))
    for binding in registry["basis_bindings"]:
        targets.append((f"registry.basis_bindings[{binding['id']}]", binding["path"],
                        binding.get("sha256"), binding.get("byte_basis")))
    targets.append(("contract.self", str(CONTRACT), None, None))
    targets.append(("registry.self", str(REGISTRY), None, None))

    results = [measure(label, path, declared, basis) for label, path, declared, basis in targets]
    mismatches = [r for r in results if r["status"] in ("MISMATCH_ALL_BASES", "MATCH_WRONG_BASIS")]
    disk_only = [r for r in results if r["status"] == "MATCH" and r.get("expected_basis_key") == "disk"
                 and r.get("declared_matches", {}).get("disk")
                 and not r.get("declared_matches", {}).get("committed_blob_content")]

    report = {
        "task_id": "S4-CTRL/S4-T21",
        "checker": "check_binding_byte_semantics",
        "checker_version": "r01",
        "generated_at_utc8": datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds"),
        "command": " ".join([sys.executable, *sys.argv]),
        "python_version": sys.version,
        "platform": platform.platform(),
        "hardware_execution": "NOT_RUN",
        "worktree": str(WORKTREE),
        "summary": {
            "entries": len(results),
            "match": sum(1 for r in results if r["status"] == "MATCH"),
            "declared_disk_only_not_blob": len(disk_only),
            "mismatch_all_bases": len(mismatches),
            "no_declared_sha": sum(1 for r in results if r["status"] == "NO_DECLARED_SHA"),
            "missing": sum(1 for r in results if r["status"] == "MISSING"),
        },
        "entries": results,
        "score": {
            "decisive_note": "declared 值为工作树磁盘字节时，在 clean 过滤器（CRLF→LF）生效的路径上，"
                             "提交后的 blob 与磁盘会不同；跨环境复算必须显式声明口径。",
        },
        "boundary": "只读测量；不修改任何绑定或文件。",
    }
    (out_dir / "binding_byte_semantics.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"entries={len(results)} match={report['summary']['match']} "
          f"disk_only={report['summary']['declared_disk_only_not_blob']} "
          f"mismatch_all_bases={report['summary']['mismatch_all_bases']}")
    for entry in results:
        if entry["status"] != "MATCH":
            print(f"[{entry['status']}] {entry['label']} -> {entry['path']}")
        elif entry.get("declared_matches", {}).get("disk") and not entry["declared_matches"].get("committed_blob_content"):
            print(f"[DISK_ONLY] {entry['label']} declared==disk but != committed blob content；"
                  f"disk={entry.get('disk_line_endings')} blob={entry.get('blob_line_endings')} attrs={entry['attributes']}")
    if mismatches:
        for entry in mismatches:
            print(f"[FAIL] {entry['label']} 声明的 SHA 与磁盘/过滤/原始/已提交四种口径均不匹配")
        return 1
    print("[PASS] 口径分析完成（无“四种口径全不匹配”的条目）")
    return 0


if __name__ == "__main__":
    sys.exit(main())