"""将指定项目笔记单向同步为仓库快照，默认只预览，不自动提交或推送。"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r"C:\Users\22061\Documents\Obsidian Vault\02-项目\基于 AX7Z020 的低比特神经网络 FPGA 加速系统，实现摄像头手势识别并驱动板卡进行实时交互")
DEST = ROOT / "docs" / "obsidian-project"
MANIFEST = ROOT / "docs" / "obsidian-manifest.json"


def digest(data):
    """计算内容校验值。"""
    return hashlib.sha256(data).hexdigest()


def linked(path):
    """拒绝符号链接与 Windows 目录联接，防止越出范围。"""
    return path.is_symlink() or bool(getattr(path.lstat(), "st_file_attributes", 0) & 0x400)


def main():
    """先完整核验，再按显式参数写入；源文件删除不自动传播。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="实际更新快照")
    args = parser.parse_args()
    if not SOURCE.is_dir():
        raise SystemExit("找不到指定项目笔记目录。")
    for base in (SOURCE, DEST, MANIFEST):
        for path in (base, *base.parents):
            if path.exists() and linked(path):
                raise SystemExit(f"拒绝链接路径：{path}")
    previous = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    contents = {}
    for directory, dirs, files in os.walk(SOURCE, followlinks=False):
        for name in dirs + files:
            if linked(Path(directory) / name):
                raise SystemExit(f"源目录包含链接，需人工核对：{name}")
        if any(name in {".git", ".obsidian"} for name in dirs):
            raise SystemExit("源项目内发现嵌套仓库或应用配置，停止同步。")
        for name in files:
            path = Path(directory) / name
            contents[path.relative_to(SOURCE).as_posix()] = path.read_bytes()
    removed = set(previous) - set(contents)
    if removed:
        raise SystemExit("源文件已移除，请单独核对仓库删除操作：" + ", ".join(sorted(removed)))
    if DEST.exists():
        for directory, dirs, files in os.walk(DEST, followlinks=False):
            for name in dirs + files:
                if linked(Path(directory) / name):
                    raise SystemExit("快照内发现链接，停止同步。")
            for name in files:
                path = Path(directory) / name
                rel = path.relative_to(DEST).as_posix()
                actual = digest(path.read_bytes())
                expected = previous.get(rel)
                if actual != expected and (rel not in contents or actual != digest(contents[rel])):
                    raise SystemExit(f"快照存在独立改动，请先协调：{rel}")
    changed = [rel for rel, data in contents.items() if not (DEST / rel).exists() or (DEST / rel).read_bytes() != data]
    print(json.dumps({"mode": "apply" if args.apply else "preview", "files": len(contents), "changed": changed}, ensure_ascii=False, indent=2))
    if args.apply:
        for rel in changed:
            target = DEST / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(contents[rel])
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps({rel: digest(data) for rel, data in sorted(contents.items())}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
