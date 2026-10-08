"""将已停写的最小输入闭包复制到独立复核副本，保留真实字节绑定。"""

from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time


def digest(data):
    return hashlib.sha256(data).hexdigest()


def command(arguments, cwd):
    result = subprocess.run(arguments, cwd=cwd, capture_output=True)
    if result.returncode:
        raise RuntimeError((arguments, result.returncode, result.stderr.decode("utf-8", "replace")))
    return result.stdout


def existing_exact(path, directory=False):
    path = path.absolute()
    current = Path(path.anchor)
    for part in path.parts[1:]:
        matches = [item for item in current.iterdir() if item.name == part]
        if len(matches) != 1:
            raise RuntimeError(f"不存在精确路径分量：{path}，{part}")
        current = matches[0]
        if current.is_symlink() or current.lstat().st_file_attributes & 0x400:
            raise RuntimeError(f"输入路径包含重解析点：{current}")
    if directory != current.is_dir() or (not directory and not current.is_file()):
        raise RuntimeError(f"输入类型不符：{current}")
    return current


def main():
    root = existing_exact(Path.cwd(), True)
    clone = existing_exact(root / "tmp/2B/S2B-T06/rv1", True)
    existing_exact(clone / ".git", True)
    head = command(["git", "rev-parse", "HEAD"], root).decode("utf-8").strip()
    shared_index = command(["git", "diff", "--cached", "--binary"], root)
    shared_status = command(["git", "status", "--porcelain=v1", "-z"], root)
    if shared_index:
        raise RuntimeError("共享暂存区必须为空")
    frozen = json.loads(existing_exact(Path(sys.argv[1])).read_text(encoding="utf-8"))
    if frozen["writer_stopped"] is not True or frozen["baseline_commit"] != head:
        raise RuntimeError("未固定开发停写和真实基线")
    started = time.perf_counter()
    sources = dict(frozen["sources"])
    checker = existing_exact(root / "verification/check_stage_delivery.py")
    sources[checker.relative_to(root).as_posix()] = digest(checker.read_bytes())
    manifest = existing_exact(root / "report/evidence/S2B-T06/ps_smoke_20261008_r01/inputs_manifest_r03.json")
    sources[manifest.relative_to(root).as_posix()] = digest(manifest.read_bytes())
    inputs = json.loads(manifest.read_text(encoding="utf-8"))
    for item in inputs["files"] + inputs["interfaces"]:
        sources[item["path"]] = item["sha256"]
    rows = []
    for relative, expected in sources.items():
        rel = Path(relative)
        if rel.is_absolute() or ".." in rel.parts:
            raise RuntimeError(f"拒绝越界相对路径：{relative}")
        source = existing_exact(root / rel)
        data = source.read_bytes()
        if digest(data) != expected:
            raise RuntimeError(f"源字节已变化：{relative}")
        parent = clone
        for part in rel.parts[:-1]:
            target = parent / part
            names = [item.name for item in parent.iterdir()]
            if part not in names:
                if any(name.casefold() == part.casefold() for name in names):
                    raise RuntimeError(f"目标大小写冲突：{target}")
                target.mkdir()
            parent = existing_exact(target, True)
        destination = parent / rel.name
        if any(item.name.casefold() == rel.name.casefold() for item in parent.iterdir()):
            raise RuntimeError(f"目标不是全新：{destination}")
        with destination.open("xb") as output:
            output.write(data)
        if digest(existing_exact(destination).read_bytes()) != expected:
            raise RuntimeError(f"副本字节不符：{destination}")
        rows.append({"source": str(source), "destination": str(destination), "path": relative,
                     "sha256": expected, "bytes": len(data)})
    if command(["git", "rev-parse", "HEAD"], root).decode("utf-8").strip() != head:
        raise RuntimeError("复制期间共享 HEAD 变化")
    if command(["git", "diff", "--cached", "--binary"], root) != shared_index:
        raise RuntimeError("复制期间共享暂存区变化")
    if command(["git", "status", "--porcelain=v1", "-z"], root) != shared_status:
        raise RuntimeError("复制期间共享文件状态变化")
    receipt = {"status": "PASS_FROZEN_MINIMAL_INPUT_COPY", "baseline_commit": head,
               "developer_stopped": True, "elapsed_seconds": time.perf_counter() - started,
               "shared_index_sha256": digest(shared_index), "shared_status_sha256": digest(shared_status),
               "count": len(rows), "files": rows, "hardware_execution": "NOT_RUN"}
    target = clone / "review_input_copy.json"
    with target.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(receipt, output, ensure_ascii=False, indent=2)
        output.write("\n")
    print(json.dumps({"status": receipt["status"], "count": len(rows), "receipt": str(target),
                      "sha256": digest(target.read_bytes()), "elapsed_seconds": receipt["elapsed_seconds"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
