import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import time


# 只刷新本次候选交付的生成清单和源码快照，不执行测试或硬件操作。
root = pathlib.Path(__file__).resolve().parents[4]
run = root / "report/evidence/S2B-T07/physical_contract_20261009_r01"
relative = run.relative_to(root).as_posix()
bindings_path = run / "source_snapshot_bindings.json"
bindings = json.loads(bindings_path.read_text(encoding="utf-8"))
for item in bindings["files"]:
    source = root / item["original_path"]
    snapshot = root / item["snapshot_path"]
    if source.read_bytes() != snapshot.read_bytes():
        raise ValueError(f"源码快照与当前原件不同：{source}")
    item["sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    item["bytes"] = source.stat().st_size
external_sources = []
for name in ["xil_cache.c", "xil_mmu.c"]:
    exact = pathlib.Path("D:/Xilinx/2026.1/data/embeddedsw/lib/bsp/standalone_v9_5/src/arm/cortexa9") / name
    if not exact.is_file():
        raise ValueError(f"官方BSP源码精确路径不存在：{exact}")
    snapshot = run / "snapshots" / name
    if snapshot.exists():
        raise ValueError(f"不覆盖已有BSP源码快照：{snapshot}")
    shutil.copyfile(exact, snapshot)
    external_sources.append({"original_exact_path": str(exact), "snapshot_path": snapshot.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(exact.read_bytes()).hexdigest(), "bytes": exact.stat().st_size,
        "reason": "只读官方BSP cache/MMU实现依据，不读取外部模型或图像"})
bindings["external_official_bsp_sources"] = external_sources
bindings_path.write_text(json.dumps(bindings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
commands = []
cmd = ["git", "diff", "--check", "--", "docs/obsidian-project/02-方案设计/系统设计.md", "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"]
start = time.perf_counter()
result = subprocess.run(cmd, cwd=root, capture_output=True)
(run / "diff_check_console.txt").write_bytes(result.stdout + result.stderr)
commands.append({"command": "git diff --check -- docs/obsidian-project/02-方案设计/系统设计.md docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md", "argv": cmd, "exit_code": result.returncode, "elapsed_seconds": time.perf_counter() - start})
if result.returncode:
    raise SystemExit(result.returncode)
commands.append({"command": "python -B tmp/2B/S2B-T07/physical_contract_packaging_20261009_r01/finalize_evidence.py", "exit_code": 0,
    "reason": "前半段已逐件比较原件和快照并刷新binding；本生成记录不是测试或整脚本最终退出码证明"})
(run / "finalization_execution.json").write_text(json.dumps(commands, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
subprocess.run([sys.executable, "-B", str(run / "layout_analysis.py"), "--mode", "manifest"], cwd=root, check=True)
cmd = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", "evidence", "--manifest", f"{relative}/delivery_manifest.json"]
result = subprocess.run(cmd, cwd=root, capture_output=True)
(run / "finalized_packaging_console.txt").write_bytes(result.stdout + result.stderr)
(run / "finalized_packaging_execution.json").write_text(json.dumps({"command": f"python -B verification/check_stage_delivery.py --mode evidence --manifest {relative}/delivery_manifest.json", "argv": cmd,
    "exit_code": result.returncode, "reason": "已刷新正式候选快照与binding后的包装只读核查；日志本身随后加入清单"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
subprocess.run([sys.executable, "-B", str(run / "layout_analysis.py"), "--mode", "manifest"], cwd=root, check=True)
print((result.stdout + result.stderr).decode("utf-8", errors="replace"))
raise SystemExit(result.returncode)
