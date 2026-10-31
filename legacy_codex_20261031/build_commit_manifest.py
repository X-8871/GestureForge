"""在实际提交之后从Git blob建立权威清单；绝不以磁盘哈希冒充提交哈希。"""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path, PurePosixPath


def git(root, *args):
    """仅调用只读Git命令，错误立即停止。"""
    result = subprocess.run(["git", "--no-optional-locks", "-C", str(root), *args], capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", "replace"))
    return result.stdout


def main():
    """必须显式给出已存在的提交与清单，未提交文件不能成为权威条目。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    commit = git(root, "rev-parse", "--verify", args.commit + "^{commit}").decode().strip()
    inventory_path = args.inventory.resolve(strict=True)
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    paths = {item["path"]: item for item in inventory["files"]}
    inventory_rel = inventory_path.relative_to(root).as_posix()
    paths[inventory_rel] = {"path": inventory_rel, "sha256": hashlib.sha256(inventory_path.read_bytes()).hexdigest()}
    files = []
    for rel, expected in sorted(paths.items()):
        path = PurePosixPath(rel)
        if path.is_absolute() or ".." in path.parts or "\\" in rel or ":" in rel:
            raise ValueError(f"不是精确仓库相对路径：{rel}")
        if not any(rel == prefix or rel.startswith(prefix + "/") for prefix in inventory["allowed_prefixes"]):
            raise ValueError(f"条目越出授权范围：{rel}")
        raw = git(root, "cat-file", "blob", commit + ":" + rel)
        digest = hashlib.sha256(raw).hexdigest()
        if digest != expected["sha256"]:
            raise ValueError(f"提交内容与待提交清单不一致：{rel}")
        files.append({"path": rel, "sha256": digest, "bytes": len(raw), "hash_basis": "commit_blob"})
    parent = args.out.parent.resolve(strict=True)
    output = parent / args.out.name
    if not parent.is_relative_to(root / "report/evidence/CTRL-LEGACY") or output.is_symlink() or output.exists():
        raise ValueError("输出必须是本任务证据范围内的全新文件")
    manifest = {"schema_version": 1, "task_id": "CTRL-LEGACY", "run_id": "residuals_20261031_r01",
                "source_commit": commit, "hash_basis": "commit_blob", "hash_basis_commit": commit,
                "files": files,
                "limitations": ["清单/strict通过只表示固定提交的文件身份一致；M3成对取样NOT_RUN、C2板上NOT_RUN、C4仍CHANGES_REQUIRED",
                                "未包含用户既有历史差异、其他工作树或编译缓存；不代表阶段5/6重新冻结"]}
    # 独占创建拒绝已存在对象，包括悬空符号链接；不跟随既有输出链接。
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": "MANIFEST_CREATED", "commit": commit, "entries": len(files), "path": str(output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
