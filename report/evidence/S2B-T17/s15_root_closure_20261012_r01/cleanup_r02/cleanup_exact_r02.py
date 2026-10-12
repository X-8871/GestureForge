"""仅按已结束任务的固定清单删除可重建缓存，并核对保留证据。"""
import hashlib
import json
from pathlib import Path
import stat
import time
from datetime import datetime, timezone, timedelta
import psutil

ROOT = Path(r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition")
WORK = Path(__file__).parent
PLAN = ROOT / "tmp/2B/S2B-T17/s15_cache_cleanup_20261012_r02/cleanup_plan.json"
EXPECTED = "411485547cb120ee5c37c094b782956d85165e841d4a89f210d97327f1c7c143"

def digest(path):
    """流式计算原字节哈希。"""
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()

def exact_file(path):
    """完整路径逐组件核验，拒绝链接、目录及越出本工作树的目标。"""
    path = Path(path)
    assert path.is_absolute() and path.is_relative_to(ROOT)
    current = Path(path.anchor)
    for name in path.parts[1:]:
        assert name in {entry.name for entry in current.iterdir()}, str(path)
        current = current / name
        assert not current.is_symlink() and not current.is_junction()
        assert not current.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT
    assert current.is_file() and str(current) == str(path)
    return current

def process_snapshot():
    """全系统枚举名字，重型或目标缓存消费者存在时阻断清理。"""
    rows = []
    heavy = {"vivado.exe", "loader.exe", "g++.exe", "cc1plus.exe", "verilator_bin.exe", "xsim.exe", "xelab.exe", "xvlog.exe"}
    for process in psutil.process_iter():
        try:
            name = process.name()
            if name.lower() in heavy or name.lower().startswith("vtb_"):
                rows.append(dict(pid=process.pid, create_time=process.create_time(), name=name,
                                 exe=process.exe(), cwd=process.cwd(), cmdline=process.cmdline()))
        except psutil.NoSuchProcess:
            continue
    assert not rows, rows
    return dict(heavy_processes=rows, process_name_enumeration_complete=True,
                ram_available_bytes=psutil.virtual_memory().available,
                c_free_bytes=psutil.disk_usage("C:\\").free)

started = time.monotonic()
assert digest(exact_file(PLAN)) == EXPECTED
plan = json.loads(PLAN.read_text(encoding="utf-8"))
assert plan["item_count"] == len(plan["items"]) == 12
assert plan["total_bytes"] == sum(row["bytes"] for row in plan["items"]) == 1739249645
for field in ("completion_proofs", "formal_manifest_audit", "preserved_artifact_inventory", "dependency_reference_audit"):
    binding = plan[field]
    assert digest(exact_file(ROOT / binding["path"])) == binding["sha256"]
proofs = json.loads((ROOT / plan["completion_proofs"]["path"]).read_text(encoding="utf-8"))
dependencies = json.loads((ROOT / plan["dependency_reference_audit"]["path"]).read_text(encoding="utf-8"))
assert not dependencies["exact_candidate_reference_hits"] and not dependencies["formal_manifest_required_gch_files"]
audit = json.loads((ROOT / plan["formal_manifest_audit"]["path"]).read_text(encoding="utf-8"))
preserved = json.loads((ROOT / plan["preserved_artifact_inventory"]["path"]).read_text(encoding="utf-8"))
retained = {row["path"]: row["actual_sha256"] for group in audit["audits"] for row in group["rows"]}
retained.update({row["path"]: row["sha256"] for row in preserved})
for row in audit["summaries"]:
    assert digest(exact_file(ROOT / row["path"])) == row["sha256"] and not row["gch_declared_paths"]
for proof in proofs:
    for field in ("compile_record", "simulation_record"):
        binding = proof[field]
        assert digest(exact_file(ROOT / binding["path"])) == binding["sha256"]
        record = binding["record"]
        assert record.get("native_exit_code", record.get("exit_code")) == 0
for path, sha in retained.items():
    target = Path(path) if Path(path).is_absolute() else ROOT / path
    assert digest(exact_file(target)) == sha, str(target)
targets = []
for row in plan["items"]:
    target = exact_file(row["exact_windows_path"])
    assert target.is_relative_to(ROOT / "tmp/2B/S2B-T17")
    assert row["eligible_after_root_rechecks"] and str(target.parent) == proofs[row["completion_proof_index"]]["object_directory"]
    info = target.lstat()
    assert info.st_size == row["bytes"] and info.st_nlink == 1 and info.st_mtime_ns == row["mtime_ns"]
    assert digest(target) == row["sha256"]
    targets.append((target, row))
before = process_snapshot()
deleted = []
for target, row in targets:
    exact_file(target)
    assert target.stat().st_size == row["bytes"] and digest(target) == row["sha256"]
    target.unlink()
    assert not target.exists()
    deleted.append(dict(path=str(target), bytes=row["bytes"], sha256=row["sha256"]))
for path, sha in retained.items():
    target = Path(path) if Path(path).is_absolute() else ROOT / path
    assert digest(exact_file(target)) == sha, str(target)
after = process_snapshot()
receipt = dict(status="EXACT_REBUILDABLE_CACHE_CLEANUP_COMPLETE", plan_sha256=EXPECTED,
               before=before, after=after, deleted=deleted, bytes=sum(x["bytes"] for x in deleted),
               retained_hashes_checked_before_and_after=len(retained), elapsed_seconds=time.monotonic()-started,
               created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),
               limitations=["只删除固定12项结束任务GCH；不删除exe/o/a、源码、黄金或失败证据。", "进程读回是离散观测，未证明操作期间系统没有新进程。"])
with (WORK / "cleanup_exact_receipt_r02.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps(receipt, ensure_ascii=False))
