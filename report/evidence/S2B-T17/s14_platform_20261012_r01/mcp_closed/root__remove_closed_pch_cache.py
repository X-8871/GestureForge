"""只删除固定G1回执列出的14份已结束可重建缓存，保全全部证据。"""
import hashlib
import json
from pathlib import Path
import stat
import time
import psutil

ROOT = Path(__file__).parents[4]
HERE = Path(__file__).parent
BASE = ROOT / "tmp/2B/S2B-T17/s14_arithmetic_fix_20261012_r01/all_r01"
FORMAL = ROOT / "report/evidence/S2B-T17/s14_arithmetic_fix_20261012_r01"

def exact(path, directory=False):
    """逐组件核验完整原拼写、类型和重解析属性。"""
    assert path.is_absolute()
    current = Path(path.anchor)
    for name in path.parts[1:]:
        assert name in {p.name for p in current.iterdir()}, str(path)
        current = current / name
        info = current.lstat()
        assert not stat.S_ISLNK(info.st_mode)
        assert not getattr(info, "st_file_attributes", 0) & 1024
    assert current.is_dir() if directory else current.is_file()
    return current

def digest(path):
    """流式核验实际原字节。"""
    value = hashlib.sha256()
    with exact(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            value.update(block)
    return value.hexdigest()

def main():
    """全部目标预检后逐份复核，禁止触及其他缓存或证据。"""
    exact(ROOT, True)
    exact(BASE, True)
    exact(FORMAL, True)
    output = HERE / "closed_pch_cleanup_receipt.json"
    assert not output.exists()
    final = exact(FORMAL / "final_receipt.json")
    assert digest(final) == "4f392af31bb02c785ae8f966dd2f3426980e522fd9137dcf515d4cbd370d7086"
    data = json.loads(final.read_text(encoding="utf-8"))
    manifest_path = exact(FORMAL / "delivery_manifest_r02.json")
    config = json.loads(exact(HERE / "pch_cleanup_config.json").read_text(encoding="utf-8"))
    assert digest(manifest_path) == config["manifest_sha256"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bound = {row["path"]: row["sha256"] for row in manifest["files"]}
    for name, expected in bound.items():
        assert digest(ROOT / name) == expected, name
    identities, commands = [], []
    for test in data["tests"].values():
        for run in test["runs"]:
            assert run["native_exit_code"] == run["direct_wait_exit_code"] == 0
            assert run["terminal_state"] == "EXITED_DIRECT_CHILD_WAIT"
            pid, birth = run["pid"], run["create_time_unix"]
            try:
                current = psutil.Process(pid).create_time()
                assert current != birth, (pid, "原G1进程仍存在")
                identities.append(dict(pid=pid, birth=birth, observed_birth=current, status="PID_REUSED"))
            except psutil.NoSuchProcess:
                identities.append(dict(pid=pid, birth=birth, status="ABSENT"))
            commands.append(run["command"])
    assert len(identities) == 14
    targets = data["gch_rebuildable_ended_runs"]
    assert len(targets) == len({row["path"] for row in targets}) == 14
    assert sum(row["size"] for row in targets) == data["gch_total_bytes"] == 2021122024
    for row in targets:
        path = exact(Path(row["path"]))
        assert path.resolve().is_relative_to(BASE.resolve())
        assert path.parent.name == "obj_dir" and path.suffix == ".gch"
        assert path.name.endswith(("__pch.h.fast.gch", "__pch.h.slow.gch"))
        assert path.stat().st_size == row["size"] and digest(path) == row["sha256"]
        assert path.relative_to(ROOT).as_posix() not in bound
    before = psutil.disk_usage("C:/").free
    deleted = []
    for row in targets:
        path = exact(Path(row["path"]))
        assert path.resolve().is_relative_to(BASE.resolve())
        assert path.stat().st_size == row["size"] and digest(path) == row["sha256"]
        path.unlink()
        assert not path.exists()
        deleted.append(row)
    for name, expected in bound.items():
        assert digest(ROOT / name) == expected, "保全失败：" + name
    result = dict(status="REMOVED_EXACT_CLOSED_REBUILDABLE_PCH_ONLY", deleted=deleted,
                  completed_identities=identities, completed_commands=commands,
                  evidence_files_preserved=len(bound),
                  c_disk_free_before=before, c_disk_free_after=psutil.disk_usage("C:/").free,
                  available_ram_bytes=psutil.virtual_memory().available, observed_unix=time.time(),
                  limitations=["仅14份回执列出的已结束G1缓存；源、黄金、日志、exe、o及a保留。"])
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({k: v for k, v in result.items() if k not in
                     ("deleted", "completed_identities", "completed_commands")}, ensure_ascii=False))

if __name__ == "__main__":
    main()
