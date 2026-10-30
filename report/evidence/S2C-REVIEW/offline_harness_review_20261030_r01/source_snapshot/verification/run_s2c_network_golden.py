#!/usr/bin/env python3
"""运行 S2C RTL11 全网理想 native-bulk 黄金对拍。"""

from __future__ import annotations

import argparse
import atexit
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "S2C-RTL11"
SAMPLE_INDEX = 0
EXPECTED_TB_SHA256 = "6b9b3b4330366a691d81178b3c7bcb80260560cca3b999d20ebc18aec83aff76"
EXPECTED_FIXTURE = {
    "manifest": "bc3cd53c7bb34fb14030a40484b3fe1d07ddc6662f4e233125f4ea2e8ed485d0",
    "input": "da26d3850d23d6f8cb466416799358e77fbeceaa8ee27696ebf7ab365248ab9e",
    "weights": "f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39",
    "golden": "090b1422f8e8d4d22124568af9778ba7bd5e7168407c0125e1e729d4a5a46f80",
}
EXPECTED_GOLDEN_BYTES = 11_382_150
EXPECTED_HEADS = {13: (29, 5_070), 26: (36, 20_280)}
MIN_FREE_MEMORY_BYTES = 3 * 1024**3
HEAVY_PROCESS_NAMES = [
    "vivado.exe", "vivado_lab.exe", "vivado_hls.exe", "xsim.exe", "xsimk.exe", "xelab.exe", "xvlog.exe", "xvhdl.exe",
    "verilator_bin.exe", "make.exe", "mingw32-make.exe", "g++.exe", "gcc.exe", "cc1plus.exe",
    "collect2.exe", "ld.exe", "Vtb_s2c_rtl11_network_golden.exe",
]
RTL_TOOLCHAIN_ROOT = Path(r"D:\FPGA_S2A_MSYS2_20261001\env")
REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT_DEFAULT = Path(r"D:\FPGA_Competition\report\evidence\S2A-T68\run01\fixtures")
_RUN_LOCK_PATH: Path | None = None
_RUN_LOCK_TOKEN: str | None = None
_KEEP_RUN_LOCK = False


class ResourceBlocked(RuntimeError):
    """全机资源查询失败或忙碌时 fail-closed。"""


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: Any) -> None:
    temporary = path.with_name(path.name + ".writing")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def acquire_runner_lock(path: Path) -> None:
    """用独占创建串行化本 runner；不约束 Vivado 等其他启动器。"""
    global _RUN_LOCK_PATH, _RUN_LOCK_TOKEN
    path.parent.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex
    payload = {"token": token, "pid": os.getpid(), "started_utc": now_utc(), "state": "RUNNING"}
    descriptor = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.write(descriptor, (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
    finally:
        os.close(descriptor)
    _RUN_LOCK_PATH = path
    _RUN_LOCK_TOKEN = token
    atexit.register(release_runner_lock)


def preserve_runner_lock(reason: str) -> None:
    """资源树未清空时保留锁，阻止后续本 runner 启动。"""
    global _KEEP_RUN_LOCK
    _KEEP_RUN_LOCK = True
    if _RUN_LOCK_PATH is None or _RUN_LOCK_TOKEN is None or not _RUN_LOCK_PATH.is_file():
        return
    try:
        current = json.loads(_RUN_LOCK_PATH.read_text(encoding="utf-8"))
        if current.get("token") == _RUN_LOCK_TOKEN:
            current["state"] = "RESOURCE_HELD"
            current["reason"] = reason
            current["updated_utc"] = now_utc()
            write_json(_RUN_LOCK_PATH, current)
    except Exception:
        _KEEP_RUN_LOCK = True


def release_runner_lock() -> None:
    """只清理由本进程创建且 token 仍匹配的空闲锁。"""
    if _KEEP_RUN_LOCK or _RUN_LOCK_PATH is None or _RUN_LOCK_TOKEN is None:
        return
    try:
        current = json.loads(_RUN_LOCK_PATH.read_text(encoding="utf-8"))
        if current.get("token") == _RUN_LOCK_TOKEN:
            _RUN_LOCK_PATH.unlink()
    except FileNotFoundError:
        return
    except Exception:
        return


def run_capture(command: list[str], *, timeout: int = 30, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def git_bytes(*args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git 命令失败，退出码 {result.returncode}: {args!r}")
    return result.stdout


def source_hash_basis(relative_path: str, disk_bytes: bytes, commit: str) -> tuple[str, str]:
    tracked = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "--error-unmatch", "--", relative_path],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if tracked.returncode == 0:
        committed = git_bytes("cat-file", "blob", f"{commit}:{relative_path}")
        if committed == disk_bytes:
            return sha256_bytes(committed), "commit_blob"
    return sha256_bytes(disk_bytes), "worktree_disk"


def verify_inside(path: Path, root: Path) -> Path:
    resolved = path.resolve(strict=True)
    root_resolved = root.resolve(strict=True)
    if os.path.commonpath([str(resolved), str(root_resolved)]) != str(root_resolved):
        raise RuntimeError(f"路径超出已确认根目录：{resolved}")
    return resolved


def load_fixtures(fixture_root: Path) -> dict[str, Any]:
    run_root = fixture_root.parent
    manifest_path = fixture_root / "sample_000" / "fixture_manifest.json"
    input_path = run_root / "fixtures/sample_000/input_chw_int8.bin"
    weights_path = run_root / "fixtures/common/weights.gf8"
    golden_path = run_root / "fixtures/sample_000/golden_unique.bin"
    for path in (manifest_path, input_path, weights_path, golden_path):
        if not path.is_file():
            raise RuntimeError(f"fixture 缺少文件：{path}")
    manifest_hash = sha256_file(manifest_path)
    input_hash = sha256_file(input_path)
    weights_hash = sha256_file(weights_path)
    golden_hash = sha256_file(golden_path)
    actual = {"manifest": manifest_hash, "input": input_hash, "weights": weights_hash, "golden": golden_hash}
    if actual != EXPECTED_FIXTURE:
        raise RuntimeError(f"T68 sample000 fixture SHA 与冻结值不一致：{actual}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("sample_index") != SAMPLE_INDEX or manifest.get("sample_id") != "test_fist_000":
        raise RuntimeError("fixture manifest sample_index/sample_id 不符")
    if manifest.get("input", {}).get("bytes") != 519168:
        raise RuntimeError("fixture 输入字节数不符")
    if manifest.get("weight_package", {}).get("bytes") != 5_903_100:
        raise RuntimeError("fixture 权重字节数不符")
    if manifest.get("golden_unique_stream", {}).get("bytes") != EXPECTED_GOLDEN_BYTES:
        raise RuntimeError("fixture golden 字节数不符")
    verify_inside(manifest_path, run_root)
    verify_inside(input_path, run_root)
    verify_inside(weights_path, run_root)
    verify_inside(golden_path, run_root)
    binding = {
        "fixture_manifest": {"path": str(manifest_path), "bytes": manifest_path.stat().st_size, "sha256": manifest_hash, "hash_basis": "worktree_disk"},
        "input": {"path": str(input_path), "bytes": input_path.stat().st_size, "sha256": input_hash, "hash_basis": "worktree_disk"},
        "weight_package": {"path": str(weights_path), "bytes": weights_path.stat().st_size, "sha256": weights_hash, "hash_basis": "worktree_disk"},
        "golden_unique_stream": {"path": str(golden_path), "bytes": golden_path.stat().st_size, "sha256": golden_hash, "hash_basis": "worktree_disk"},
    }
    return {"manifest": manifest, "manifest_path": manifest_path, "input_path": input_path, "weights_path": weights_path, "golden_path": golden_path, "bindings": binding}


def candidate_sources() -> tuple[list[str], Path]:
    platform_path = REPO_ROOT / "board" / "s2b_inference_platform.json"
    platform = json.loads(platform_path.read_text(encoding="utf-8"))
    if platform.get("candidate_generics") != {"CONV_OUTPUT_LANES": 32, "ENABLE_BULK": 1}:
        raise RuntimeError("平台候选泛型不是 32 lane + bulk")
    if platform.get("clock_hz") != 100_000_000:
        raise RuntimeError("平台候选时钟不是 100 MHz")
    sources = platform.get("rtl_sources")
    if not isinstance(sources, list) or len(sources) != 21 or len(set(sources)) != 21:
        raise RuntimeError("平台 RTL source 列表应有 21 个唯一文件")
    return sources, platform_path


def snapshot_sources(snapshot_root: Path, commit: str, runner_path: Path, sources: list[str], platform_path: Path) -> tuple[list[dict[str, Any]], str]:
    rows: list[dict[str, Any]] = []
    files_to_snapshot = list(sources) + ["sim/tb_s2c_rtl11_network_golden.sv", "board/s2b_inference_platform.json", "verification/run_s2c_network_golden.py"]
    tb_path = REPO_ROOT / "sim" / "tb_s2c_rtl11_network_golden.sv"
    if sha256_file(tb_path) != EXPECTED_TB_SHA256:
        raise RuntimeError("RTL11 已审查 testbench SHA 发生变化，拒绝以新版本冒充已审查输入")
    for relative in files_to_snapshot:
        origin = (REPO_ROOT / Path(relative)).resolve(strict=True)
        if not origin.is_file():
            raise RuntimeError(f"source 不是文件：{origin}")
        disk_bytes = origin.read_bytes()
        digest, basis = source_hash_basis(relative.replace("\\", "/"), disk_bytes, commit)
        if relative == "verification/run_s2c_network_golden.py" and origin != runner_path.resolve(strict=True):
            raise RuntimeError("runner 自身路径和快照路径不一致")
        target = snapshot_root / Path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(disk_bytes)
        copied_hash = sha256_file(target)
        if copied_hash != digest:
            raise RuntimeError(f"source 快照复制后 SHA 不一致：{relative}")
        rows.append({
            "path": relative.replace("\\", "/"),
            "origin_path": str(origin),
            "snapshot_path": str(target),
            "bytes": len(disk_bytes),
            "sha256": digest,
            "hash_basis": basis,
        })
    snapshot_binding = sha256_bytes(json.dumps(rows, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    write_json(snapshot_root / "source_snapshot.json", {"schema_version": "gestureforge_s2c_rtl11_source_snapshot_v1", "git_head": commit, "rows": rows, "snapshot_binding_sha256": snapshot_binding, "hash_basis": "worktree_disk"})
    return rows, snapshot_binding


def evidence_item(path: Path, role: str, basis: str, digest: str | None = None) -> dict[str, Any]:
    resolved = path.resolve(strict=True)
    relative = os.path.relpath(resolved, REPO_ROOT)
    if relative == os.pardir or relative.startswith(os.pardir + os.sep):
        raise RuntimeError(f"manifest item 超出工作树：{resolved}")
    return {
        "path": relative.replace("\\", "/"),
        "role": role,
        "bytes": resolved.stat().st_size,
        "sha256": digest or sha256_file(resolved),
        "hash_basis": basis,
    }


def source_items(source_rows: list[dict[str, Any]], snapshot_manifest: Path, commit: str, binary: Path | None = None) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in source_rows:
        relative = row["path"]
        if relative.startswith("src/"):
            role = "source"
        elif relative == "sim/tb_s2c_rtl11_network_golden.sv":
            role = "testbench"
        elif relative == "board/s2b_inference_platform.json":
            role = "platform"
        else:
            role = "runner"
        for path, item_role, basis, digest in (
            (Path(row["origin_path"]), role, row["hash_basis"], row["sha256"]),
            (Path(row["snapshot_path"]), f"{role}_snapshot", "worktree_disk", row["sha256"]),
        ):
            item = evidence_item(path, item_role, basis, digest)
            if item["path"] not in seen:
                seen.add(item["path"])
                items.append(item)
    snapshot_item = evidence_item(snapshot_manifest, "source_snapshot_manifest", "worktree_disk")
    if snapshot_item["path"] not in seen:
        seen.add(snapshot_item["path"])
        items.append(snapshot_item)
    if binary is not None and binary.is_file():
        binary_item = evidence_item(binary, "compiled_binary", "worktree_disk")
        if binary_item["path"] not in seen:
            items.append(binary_item)
    return items


def replace_or_append_item(items: list[dict[str, Any]], item: dict[str, Any]) -> list[dict[str, Any]]:
    updated = [existing for existing in items if existing.get("path") != item.get("path")]
    updated.append(item)
    return updated


def add_existing_item(manifest: dict[str, Any], path: Path, role: str) -> None:
    if path.is_file():
        items = manifest.setdefault("items", [])
        manifest["items"] = replace_or_append_item(items, evidence_item(path, role, "worktree_disk"))


def powershell_path() -> str:
    resolved = shutil.which("powershell.exe") or shutil.which("powershell")
    if not resolved:
        raise RuntimeError("找不到 Windows PowerShell，无法做 CIM fail-closed 资源门禁")
    return resolved


def resource_preflight() -> dict[str, Any]:
    names = ",".join("'" + name.replace("'", "''") + "'" for name in HEAVY_PROCESS_NAMES)
    script = (
        "$ErrorActionPreference='Stop';"
        f"$names=@({names});"
        "$p=@(Get-CimInstance Win32_Process | Where-Object { $names -contains $_.Name } | "
        "Select-Object ProcessId,ParentProcessId,Name,ExecutablePath,CommandLine);"
        "$o=Get-CimInstance Win32_OperatingSystem;"
        "[ordered]@{processes=$p;available_bytes=([long]$o.FreePhysicalMemory*1024)} | ConvertTo-Json -Depth 5 -Compress"
    )
    result = run_capture([powershell_path(), "-NoProfile", "-NonInteractive", "-Command", script], timeout=30)
    if result.returncode != 0:
        raise ResourceBlocked(f"CIM 全机资源检查失败，fail-closed；退出码={result.returncode} 输出={result.stdout[-2000:]}")
    try:
        data = json.loads(result.stdout.strip())
    except json.JSONDecodeError as exc:
        raise ResourceBlocked(f"CIM 返回非 JSON，fail-closed：{result.stdout[-2000:]}") from exc
    processes = data.get("processes") or []
    if isinstance(processes, dict):
        processes = [processes]
    available = int(data["available_bytes"])
    if processes:
        raise ResourceBlocked(f"检测到全机重型任务，fail-closed：{processes}")
    if available < MIN_FREE_MEMORY_BYTES:
        raise ResourceBlocked(f"可用内存低于 3 GiB，fail-closed：{available} bytes")
    return {"status": "PASS", "available_memory_bytes_before": available, "peak_memory_bytes": None, "peak_memory_measurement": "未采集峰值；本 runner 只做启动前 CIM 门禁", "heavy_processes": processes, "minimum_free_memory_bytes": MIN_FREE_MEMORY_BYTES, "cim_command_exit_code": result.returncode}


def build_verilator_env(tool_bin: Path, make_bin: Path, verilator_root: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = str(make_bin) + os.pathsep + str(tool_bin) + os.pathsep + env.get("PATH", "")
    env["VERILATOR_ROOT"] = str(verilator_root.resolve())
    for name in ("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "CMAKE_BUILD_PARALLEL_LEVEL", "NINJAFLAGS", "JOBS", "PARALLEL"):
        env.pop(name, None)
    env["MAKEFLAGS"] = ""
    env["MFLAGS"] = ""
    env["CMAKE_BUILD_PARALLEL_LEVEL"] = "1"
    env["NINJAFLAGS"] = "-j1"
    return env


def powershell_process_identity(pid: int) -> dict[str, Any] | None:
    script = (
        "$ErrorActionPreference='Stop';"
        f"$p=Get-CimInstance Win32_Process -Filter 'ProcessId={int(pid)}';"
        "if ($null -eq $p) { 'null' } else { "
        "[ordered]@{ProcessId=$p.ProcessId;ParentProcessId=$p.ParentProcessId;Name=$p.Name;"
        "ExecutablePath=$p.ExecutablePath;CommandLine=$p.CommandLine;CreationDate=([string]$p.CreationDate)} | ConvertTo-Json -Compress }"
    )
    try:
        result = run_capture([powershell_path(), "-NoProfile", "-NonInteractive", "-Command", script], timeout=30)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    raw = result.stdout.strip()
    if raw == "null":
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def powershell_process_table() -> list[dict[str, Any]] | None:
    script = (
        "$ErrorActionPreference='Stop';"
        "$p=@(Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name,ExecutablePath,CommandLine,CreationDate);"
        "$p | ConvertTo-Json -Depth 4 -Compress"
    )
    try:
        result = run_capture([powershell_path(), "-NoProfile", "-NonInteractive", "-Command", script], timeout=60)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    raw = result.stdout.strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict):
        return [data]
    return data if isinstance(data, list) else None


def process_tree(rows: list[dict[str, Any]], root_pid: int) -> list[dict[str, Any]]:
    parent_ids = {root_pid}
    tree: dict[int, dict[str, Any]] = {}
    changed = True
    while changed:
        changed = False
        for row in rows:
            try:
                pid = int(row.get("ProcessId", -1))
                parent = int(row.get("ParentProcessId", -2))
            except (TypeError, ValueError):
                continue
            if parent in parent_ids and pid not in parent_ids:
                parent_ids.add(pid)
                tree[pid] = row
                changed = True
    root = next((row for row in rows if int(row.get("ProcessId", -1)) == root_pid), None)
    if root is not None:
        tree[root_pid] = root
    return list(tree.values())


def verify_exited_tree(process: subprocess.Popen[Any], expected_identity: dict[str, Any] | None) -> dict[str, Any]:
    rows = powershell_process_table()
    tree = process_tree(rows, process.pid) if rows is not None else None
    if rows is None or tree is None or not rows:
        preserve_runner_lock("根进程已退出，但 CIM 无法确认其进程树为空")
        return {"cleanup_status": "RESOURCE_HELD", "reason": "根进程已退出但无法核验子进程残留", "remaining_processes": None}
    if tree:
        preserve_runner_lock("根进程已退出但 CIM 仍发现同 PID 进程或其子进程")
        return {"cleanup_status": "RESOURCE_HELD", "reason": "根进程已退出但同 PID 树仍有 CIM 记录", "remaining_processes": tree}
    return {"cleanup_status": "CLEARED", "reason": "Popen 根进程句柄确认已退出，CIM 未发现其 PID 下的残留进程", "taskkill_exit_code": None, "wait_error": None, "remaining_processes": []}


def terminate_verified_tree(process: subprocess.Popen[Any], expected_executable: Path, expected_identity: dict[str, Any] | None) -> dict[str, Any]:
    if process.poll() is not None:
        return verify_exited_tree(process, expected_identity)
    live = powershell_process_identity(process.pid)
    if process.poll() is not None:
        return verify_exited_tree(process, expected_identity)
    expected_path = os.path.normcase(os.path.abspath(str(expected_executable)))
    if live and expected_identity:
        live_path = os.path.normcase(os.path.abspath(str(live.get("ExecutablePath") or "")))
        same_identity = (
            int(live.get("ProcessId", -1)) == process.pid
            and str(live.get("CreationDate")) == str(expected_identity.get("CreationDate"))
            and live_path == expected_path
            and live.get("CommandLine") == expected_identity.get("CommandLine")
        )
        if not same_identity:
            preserve_runner_lock("超时进程身份变化，未能核验本轮进程树是否已清空")
            return {"cleanup_status": "RESOURCE_HELD", "reason": "超时进程身份与启动时快照不一致，未发出终止命令", "live_identity": live, "remaining_processes": [live]}
        proof = "CIM PID、创建时间、可执行路径及命令行与启动快照完全一致"
    else:
        # Popen 持有本轮创建的根进程句柄；仍存活时其 PID 不会复用，且参数必须等于本轮命令。
        args = process.args if isinstance(process.args, list) else []
        process_executable = os.path.normcase(os.path.abspath(str(args[0]))) if args else ""
        if process.poll() is not None:
            return verify_exited_tree(process, expected_identity)
        if process_executable != expected_path:
            preserve_runner_lock("CIM 不可用且 Popen 身份不足以核验进程归属")
            return {"cleanup_status": "RESOURCE_HELD", "reason": "CIM 不可用且 Popen 根进程句柄/可执行路径无法确认，未发出终止命令", "live_identity": live, "remaining_processes": [live] if live else None}
        proof = "CIM 不可用；由本轮 Popen 活进程句柄、PID 未复用条件和原始 argv[0] 确认根进程归属"
    taskkill = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "taskkill.exe"
    before_tree = powershell_process_table()
    if before_tree is None:
        before_tree = []
    before_owned = process_tree(before_tree, process.pid)
    taskkill_exit_code: int | None = None
    taskkill_output = ""
    taskkill_error: str | None = None
    if taskkill.is_file():
        try:
            taskkill_result = subprocess.run(
                [str(taskkill), "/PID", str(process.pid), "/T", "/F"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                check=False,
            )
            taskkill_exit_code = taskkill_result.returncode
            taskkill_output = taskkill_result.stdout[-2000:]
        except (OSError, subprocess.TimeoutExpired) as exc:
            taskkill_error = f"{type(exc).__name__}: {exc}"
    else:
        taskkill_error = f"taskkill 不存在：{taskkill}"
    wait_error: str | None = None
    try:
        process.wait(timeout=30)
    except subprocess.TimeoutExpired as exc:
        wait_error = f"根进程 wait 超时：{exc}"
        try:
            process.kill()
            process.wait(timeout=30)
        except Exception as kill_exc:
            wait_error += f"；Popen 句柄终止/等待失败：{type(kill_exc).__name__}: {kill_exc}"
    except Exception as exc:
        wait_error = f"根进程等待异常：{type(exc).__name__}: {exc}"

    remaining: list[dict[str, Any]] | None = None
    for _ in range(10):
        after = powershell_process_table()
        if after is None:
            remaining = None
            time.sleep(1)
            continue
        remaining = process_tree(after, process.pid)
        if not remaining:
            break
        time.sleep(1)
    cleanup_status = "CLEARED" if remaining == [] and before_tree and process.poll() is not None else "RESOURCE_HELD"
    record = {
        "cleanup_status": cleanup_status,
        "reason": "身份核验后清理本轮根进程树，并在 CIM 中复查残留",
        "identity_proof": proof,
        "verified_identity": live,
        "taskkill_exit_code": taskkill_exit_code,
        "taskkill_output": taskkill_output,
        "taskkill_error": taskkill_error,
        "wait_error": wait_error,
        "process_tree_before": before_owned,
        "remaining_processes": remaining,
    }
    if cleanup_status != "CLEARED":
        preserve_runner_lock("超时清理后 CIM 仍有自家进程树残留或无法确认进程树为空")
    return record


def run_logged(command: list[str], *, cwd: Path, env: dict[str, str], stdout_path: Path, stderr_path: Path, timeout_seconds: int, no_progress_seconds: int | None = None, progress_path: Path | None = None) -> dict[str, Any]:
    started = time.monotonic()
    started_utc = now_utc()
    identity: dict[str, Any] | None = None
    timed_out = False
    last_activity = started
    last_sizes = (-1, -1, -1)
    kill_info: dict[str, Any] | None = None
    monitor_error: str | None = None
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    with stdout_path.open("wb") as stdout_stream, stderr_path.open("wb") as stderr_stream:
        process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=stdout_stream, stderr=stderr_stream, creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
        try:
            identity_deadline = time.monotonic() + 10
            while identity is None and process.poll() is None and time.monotonic() < identity_deadline:
                identity = powershell_process_identity(process.pid)
                if identity is None:
                    time.sleep(0.25)
            while process.poll() is None:
                now = time.monotonic()
                try:
                    sizes = (stdout_path.stat().st_size, stderr_path.stat().st_size, progress_path.stat().st_size if progress_path and progress_path.exists() else 0)
                except OSError:
                    sizes = last_sizes
                if sizes != last_sizes:
                    last_activity = now
                    last_sizes = sizes
                if now - started >= timeout_seconds:
                    timed_out = True
                    kill_info = terminate_verified_tree(process, Path(command[0]), identity)
                    break
                if no_progress_seconds is not None and now - last_activity >= no_progress_seconds:
                    timed_out = True
                    kill_info = terminate_verified_tree(process, Path(command[0]), identity)
                    break
                time.sleep(1)
        except Exception as exc:
            monitor_error = f"监控异常：{type(exc).__name__}: {exc}"
            if process.poll() is None:
                timed_out = True
                try:
                    kill_info = terminate_verified_tree(process, Path(command[0]), identity)
                except Exception as cleanup_exc:
                    preserve_runner_lock("监控异常后进程树清理异常，无法证明资源已释放")
                    kill_info = {"cleanup_status": "RESOURCE_HELD", "reason": f"清理异常：{type(cleanup_exc).__name__}: {cleanup_exc}"}
        if process.poll() is None and not timed_out:
            try:
                process.wait()
            except Exception as exc:
                monitor_error = f"等待异常：{type(exc).__name__}: {exc}"
                if process.poll() is None:
                    try:
                        kill_info = terminate_verified_tree(process, Path(command[0]), identity)
                        timed_out = True
                    except Exception as cleanup_exc:
                        preserve_runner_lock("等待异常后进程树清理异常，无法证明资源已释放")
                        kill_info = {"cleanup_status": "RESOURCE_HELD", "reason": f"清理异常：{type(cleanup_exc).__name__}: {cleanup_exc}"}
        exit_code = process.poll()
    ended = time.monotonic()
    stdout_hash = sha256_file(stdout_path) if stdout_path.exists() else None
    stderr_hash = sha256_file(stderr_path) if stderr_path.exists() else None
    progress_hash = sha256_file(progress_path) if progress_path and progress_path.exists() else None
    return {
        "command": command,
        "cwd": str(cwd),
        "started_utc": started_utc,
        "ended_utc": now_utc(),
        "duration_seconds": round(ended - started, 3),
        "exit_code": exit_code,
        "timeout": timed_out,
        "timeout_kill": kill_info,
        "resource_held": bool(kill_info and kill_info.get("cleanup_status") != "CLEARED"),
        "monitor_error": monitor_error,
        "process_id": process.pid,
        "process_identity_at_start": identity,
        "stdout_log": {"path": str(stdout_path), "sha256": stdout_hash, "hash_basis": "worktree_disk"},
        "stderr_log": {"path": str(stderr_path), "sha256": stderr_hash, "hash_basis": "worktree_disk"},
        "progress_log": {"path": str(progress_path), "sha256": progress_hash, "hash_basis": "worktree_disk"} if progress_path else None,
    }


def parse_summary(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        for key, value in re.findall(r"([A-Za-z0-9_]+)=([^\s]+)", line):
            values[key] = value
    return values


def validate_outputs(fixtures: dict[str, Any], run_dir: Path, summary_path: Path, head13_path: Path, head26_path: Path, sample_index: int) -> dict[str, Any]:
    summary = parse_summary(summary_path)
    if summary.get("status") != "PASS_LAYERWISE_EXACT_GOLDEN_NATIVE_BULK":
        raise RuntimeError("RTL11 summary 未给出全网 native-bulk PASS")
    scope_match = re.search(r"sample_(\d+)", summary.get("scope", ""))
    if not scope_match or int(scope_match.group(1)) != sample_index:
        raise RuntimeError("RTL11 summary sample_index 不符")
    if summary.get("feature_write_bytes") != str(EXPECTED_GOLDEN_BYTES) or summary.get("mismatches") != "0":
        raise RuntimeError("RTL11 全网逐字节黄金字节数或差异数不符")
    cycles = int(summary.get("cycles", "0"))
    if cycles <= 0:
        raise RuntimeError("RTL11 未报告正的理想模型周期数")
    if summary.get("bulk_seed", "").lower() != "0x11c02026":
        raise RuntimeError("RTL11 bulk seed 与固定种子不符")
    if summary.get("head13_bytes") != "5070" or summary.get("head26_bytes") != "20280":
        raise RuntimeError("RTL11 head 张量尺寸不符")
    expected_ranges: dict[int, tuple[int, int]] = {}
    for layer in fixtures["manifest"]["layers"]:
        if layer.get("layer_index") in (29, 36):
            expected_ranges[layer["layer_index"]] = (int(layer["golden_stream_offset"]), int(layer["byte_length"]))
    head_rows: dict[str, Any] = {}
    with fixtures["golden_path"].open("rb") as golden:
        for head_number, (layer_index, expected_bytes) in EXPECTED_HEADS.items():
            actual_path = head13_path if head_number == 13 else head26_path
            offset, length = expected_ranges[layer_index]
            if length != expected_bytes or not actual_path.is_file() or actual_path.stat().st_size != expected_bytes:
                raise RuntimeError(f"head{head_number} 文件缺失或长度不符")
            golden.seek(offset)
            expected = golden.read(length)
            actual = actual_path.read_bytes()
            if actual != expected:
                raise RuntimeError(f"head{head_number} 与独立 golden 对应张量不逐字节相等")
            head_rows[f"head{head_number}"] = {"path": str(actual_path), "bytes": len(actual), "sha256": sha256_bytes(actual), "hash_basis": "worktree_disk", "golden_offset": offset, "golden_sha256": sha256_bytes(expected), "golden_sha256_hash_basis": "worktree_disk", "matches_golden": True}
    return {
        "status": "PASS_IDEAL_BULK_FRAME",
        "sample_index": sample_index,
        "sample_id": fixtures["manifest"]["sample_id"],
        "scope": "36 stored output tensors byte-exact against independent T25 golden; 2 alias rows excluded from writes",
        "feature_write_bytes": EXPECTED_GOLDEN_BYTES,
        "mismatches": 0,
        "cycles": cycles,
        "cycle_semantics": "RTL ideal native-bulk model cycles only; not AXI cycles, board cycles, or board fps",
        "bulk_model": {"seed": summary.get("bulk_seed"), "bytes_per_cycle": 1, "extra_wait_cycles": "0..3 LFSR low2 cycles", "legacy_stall_pattern_per_class": "0,1,2,7,3"},
        "fixture_bindings": fixtures["bindings"],
        "source_snapshot_binding_sha256_hash_basis": "worktree_disk",
        "golden_compare": {"path": str(fixtures["golden_path"]), "bytes": EXPECTED_GOLDEN_BYTES, "sha256": EXPECTED_FIXTURE["golden"], "hash_basis": "worktree_disk", "result_summary_path": str(summary_path), "summary_sha256": sha256_file(summary_path), "summary_sha256_hash_basis": "worktree_disk"},
        "heads": head_rows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="S2C RTL11 全网逐字节 golden 验证；仿真周期仅代表理想 bulk 模型。")
    parser.add_argument("--run-id", required=True, help="新 RunId；只允许文件名安全字符且不可覆盖既有目录")
    parser.add_argument("--phase", choices=("all", "compile-only", "run-only"), default="all", help="完整一次运行，或分离编译/仿真阶段")
    parser.add_argument("--fixture-root", type=Path, default=FIXTURE_ROOT_DEFAULT, help="T68 run01/fixtures 根目录，必须绑定固定 sample000 SHA")
    parser.add_argument("--sample-index", type=int, choices=(0,), default=0, help="当前候选仅接受已冻结 sample 000")
    parser.add_argument("--max-cycles", type=int, default=4_294_967_295)
    parser.add_argument("--timeout-seconds", type=int, default=21_600, help="每个重型阶段的硬超时秒数")
    parser.add_argument("--no-progress-seconds", type=int, default=3_600, help="仿真进度文件无变化超时秒数")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{2,79}", args.run_id):
        raise RuntimeError("RunId 仅允许 3..80 个 ASCII 字母、数字、点、下划线、连字符，且首字符为字母或数字")
    if args.max_cycles <= 0 or args.timeout_seconds <= 0 or args.no_progress_seconds <= 0:
        raise RuntimeError("cycle 与 timeout 参数必须大于零")
    evidence_parent = REPO_ROOT / "report" / "evidence" / TASK_ID
    temp_parent = REPO_ROOT / "tmp" / "S2C" / TASK_ID
    lock_path = temp_parent / ".network_golden.lock"
    try:
        acquire_runner_lock(lock_path)
    except FileExistsError:
        print(f"{TASK_ID} runner lock 已存在，拒绝并发启动：{lock_path}", file=sys.stderr)
        return 2
    evidence_dir = evidence_parent / args.run_id
    work_dir = temp_parent / args.run_id
    manifest_path = evidence_dir / "manifest.json"
    result_path = evidence_dir / "result.json"
    runner_path = Path(__file__).resolve(strict=True)
    if args.phase == "run-only":
        if not evidence_dir.is_dir() or not work_dir.is_dir() or not manifest_path.is_file():
            raise RuntimeError("run-only 要求同 RunId 已有 compile-only manifest 与 build 目录")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("phase") != "compile-only" or manifest.get("compile", {}).get("exit_code") != 0:
            raise RuntimeError("run-only 仅可继续成功的 compile-only 记录")
        if manifest.get("simulation") is not None:
            raise RuntimeError("此 RunId 已有仿真执行记录；禁止覆盖，使用新 RunId")
        for name in ("verilator_simulation.stdout.log", "verilator_simulation.stderr.log", "progress_markers.txt", "rtl11_result_summary.txt", "head13_actual_int8.bin", "head26_actual_int8.bin"):
            if (evidence_dir / name).exists():
                raise RuntimeError(f"run-only 检测到既有仿真产物，保留失败证据且拒绝覆盖：{evidence_dir / name}")
        if manifest.get("runner", {}).get("sha256") != sha256_file(runner_path):
            raise RuntimeError("run-only 当前 runner 与编译阶段快照不同")
        compile_result = manifest.get("compile_result") or {}
        compile_result_path = evidence_dir / "compile_result.json"
        if not compile_result_path.is_file() or sha256_file(compile_result_path) != compile_result.get("sha256"):
            raise RuntimeError("run-only 缺少或改动了原 compile_result.json，拒绝覆盖编译阶段证据")
        snapshot_manifest = Path(manifest["source_snapshot"]["path"])
        if not snapshot_manifest.is_file() or sha256_file(snapshot_manifest) != manifest["source_snapshot"]["sha256"]:
            raise RuntimeError("run-only source_snapshot.json 缺失或 SHA 改变")
        for row in manifest.get("source_snapshot", {}).get("rows", []):
            snapshot = Path(row["snapshot_path"])
            if not snapshot.is_file() or sha256_file(snapshot) != row["sha256"]:
                raise RuntimeError(f"run-only source 快照缺失或 SHA 改变：{snapshot}")
        compiled_binary = manifest.get("compiled_binary") or {}
        compiled_binary_path = Path(compiled_binary.get("path", ""))
        if not compiled_binary_path.is_file() or sha256_file(compiled_binary_path) != compiled_binary.get("sha256"):
            raise RuntimeError("run-only 编译产物与原 compile-only 绑定不同")
    else:
        if evidence_dir.exists() or work_dir.exists():
            raise RuntimeError(f"RunId 已存在，拒绝覆盖：{evidence_dir} 或 {work_dir}")
        evidence_dir.mkdir(parents=True, exist_ok=False)
        work_dir.mkdir(parents=True, exist_ok=False)
        manifest = {}

    result: dict[str, Any] = {
        "schema_version": "gestureforge_s2c_rtl11_network_golden_result_v1",
        "status": "PREPARING",
        "run_id": args.run_id,
        "sample_index": args.sample_index,
        "sample_count": 1,
        "cycles": None,
        "peak_memory_bytes": None,
        "hash_basis": "worktree_disk",
    }
    started_utc = now_utc()
    try:
        if args.phase != "run-only":
            fixtures = load_fixtures(args.fixture_root.resolve(strict=True))
            sources, platform_path = candidate_sources()
            git_head = git_bytes("rev-parse", "HEAD").decode("ascii").strip()
            snapshot_root = evidence_dir / "source_snapshot"
            source_rows, snapshot_binding = snapshot_sources(snapshot_root, git_head, runner_path, sources, platform_path)
            runner_sha = sha256_file(runner_path)
            tool_bin = RTL_TOOLCHAIN_ROOT / "mingw64" / "bin"
            make_bin = RTL_TOOLCHAIN_ROOT / "usr" / "bin"
            verilator = tool_bin / "verilator_bin.exe"
            make = make_bin / "make.exe"
            compiler = tool_bin / "g++.exe"
            verilator_root = tool_bin / ".." / "share" / "verilator"
            for path in (verilator, make, compiler):
                if not path.is_file():
                    raise RuntimeError(f"Verilator 工具链缺少文件：{path}")
            if not verilator_root.is_dir():
                raise RuntimeError(f"Verilator_ROOT 不存在：{verilator_root}")
            env = build_verilator_env(tool_bin, make_bin, verilator_root)
            version = run_capture([str(verilator), "--version"], timeout=30, env=env)
            if version.returncode != 0:
                raise RuntimeError(f"verilator --version 失败：{version.stdout[-2000:]}")
            preflight = resource_preflight()
            rtl_snapshot_root = snapshot_root
            source_files = [str(rtl_snapshot_root / Path(path)) for path in sources]
            testbench = str(rtl_snapshot_root / "sim" / "tb_s2c_rtl11_network_golden.sv")
            build_dir = work_dir / "build"
            build_dir.mkdir(parents=True, exist_ok=False)
            compile_command = [
                str(verilator), "--binary", "--build-jobs", "1", "--timing", "-Wno-fatal", "--top-module", "tb_s2c_rtl11_network_golden",
                "--Mdir", str(build_dir), "-CFLAGS", "-D_GLIBCXX_USE_CXX11_ABI=0", *source_files, testbench,
            ]
            compile_stdout_path = evidence_dir / "verilator_compile.stdout.log"
            compile_stderr_path = evidence_dir / "verilator_compile.stderr.log"
            manifest = {
                "schema_version": "gestureforge_s2c_rtl11_network_golden_manifest_v1",
                "task_id": TASK_ID,
                "run_id": args.run_id,
                "phase": "compile-only" if args.phase == "compile-only" else "all",
                "started_utc": started_utc,
                "git_head": git_head,
                "hash_basis": "worktree_disk",
                "hash_basis_commit": git_head,
                "concurrency": {"lock_path": str(lock_path), "lock_scope": "仅串行化本 runner；其他工具由总控协调并由启动前 CIM 门禁检查。"},
                "sample_index": args.sample_index,
                "fixture_bindings": fixtures["bindings"],
                "platform": {"path": str(platform_path), "sha256": sha256_file(platform_path), "hash_basis": next(row["hash_basis"] for row in source_rows if row["path"] == "board/s2b_inference_platform.json")},
                "candidate": {"clock_hz": 100_000_000, "conv_output_lanes": 32, "enable_bulk": 1},
                "source_snapshot": {"path": str(snapshot_root / "source_snapshot.json"), "sha256": sha256_file(snapshot_root / "source_snapshot.json"), "hash_basis": "worktree_disk", "snapshot_binding_sha256": snapshot_binding, "rows": source_rows},
                "runner": {"path": str(runner_path), "snapshot_path": str(snapshot_root / "verification" / "run_s2c_network_golden.py"), "sha256": runner_sha, "hash_basis": "worktree_disk"},
                "tool": {"name": "Verilator --binary --build-jobs 1 --timing", "version": version.stdout.strip(), "version_exit_code": version.returncode, "verilator_path": str(verilator), "make_path": str(make), "compiler_path": str(compiler), "verilator_root": str(verilator_root.resolve()), "build_jobs": 1, "makeflags": "", "mflags": ""},
                "resource_preflight": preflight,
                "compile": {"status": "RUNNING", "command": compile_command, "started_utc": now_utc(), "stdout_log_path": str(compile_stdout_path), "stderr_log_path": str(compile_stderr_path)},
                "simulation": None,
                "limitations": ["理想 native-bulk 仿真周期不是 AXI/板级周期或帧率。", "峰值内存未采集；资源门禁记录启动前可用内存。", "该运行只覆盖 sample_index=0。"],
                "items": source_items(source_rows, snapshot_root / "source_snapshot.json", git_head),
            }
            write_json(manifest_path, manifest)
            compile_record = run_logged(
                compile_command, cwd=work_dir, env=env,
                stdout_path=compile_stdout_path,
                stderr_path=compile_stderr_path,
                timeout_seconds=args.timeout_seconds,
            )
            manifest["compile"] = compile_record
            manifest["status"] = "COMPILE_TIMEOUT" if compile_record["timeout"] else ("COMPILE_PASS" if compile_record["exit_code"] == 0 else "COMPILE_FAIL")
            write_json(manifest_path, manifest)
            result["fixture_bindings"] = fixtures["bindings"]
            result["source_snapshot_binding_sha256"] = snapshot_binding
            result["tool_version"] = version.stdout.strip()
            result["compile_exit_code"] = compile_record["exit_code"]
            if compile_record["exit_code"] != 0 or compile_record["timeout"]:
                if compile_record.get("resource_held"):
                    result["status"] = "RESOURCE_HELD"
                else:
                    result["status"] = "COMPILE_FAIL" if not compile_record["timeout"] else "COMPILE_TIMEOUT"
                result["compile"] = compile_record
                compile_result_path = evidence_dir / "compile_result.json"
                write_json(compile_result_path, result)
                manifest["compile_result"] = {"path": str(compile_result_path), "sha256": sha256_file(compile_result_path), "hash_basis": "worktree_disk"}
                add_existing_item(manifest, compile_result_path, "compile_result")
                write_json(result_path, result)
                add_existing_item(manifest, result_path, "result")
                manifest["status"] = result["status"]
                manifest["ended_utc"] = now_utc()
                write_json(manifest_path, manifest)
                return 3 if compile_record.get("resource_held") else 1
            binary_path = work_dir / "build" / "Vtb_s2c_rtl11_network_golden.exe"
            if not binary_path.is_file():
                raise RuntimeError(f"Verilator 编译成功但预期仿真 binary 缺失：{binary_path}")
            manifest["compiled_binary"] = {"path": str(binary_path), "sha256": sha256_file(binary_path), "hash_basis": "worktree_disk"}
            add_existing_item(manifest, binary_path, "compiled_binary")
            result["compiled_binary"] = manifest["compiled_binary"]
            result["compile"] = compile_record
            result["status"] = "COMPILE_ONLY" if args.phase == "compile-only" else "COMPILE_READY_FOR_SIMULATION"
            compile_result_path = evidence_dir / "compile_result.json"
            write_json(compile_result_path, result)
            manifest["compile_result"] = {"path": str(compile_result_path), "sha256": sha256_file(compile_result_path), "hash_basis": "worktree_disk"}
            add_existing_item(manifest, compile_result_path, "compile_result")
            write_json(result_path, result)
            add_existing_item(manifest, result_path, "result")
            manifest["status"] = result["status"]
            write_json(manifest_path, manifest)
            if args.phase == "compile-only":
                manifest["ended_utc"] = now_utc()
                write_json(manifest_path, manifest)
                return 0
        else:
            fixtures = load_fixtures(args.fixture_root.resolve(strict=True))
            if fixtures["bindings"] != manifest.get("fixture_bindings"):
                raise RuntimeError("run-only fixture 绑定与 compile-only 记录不同")
            source_snapshot = manifest["source_snapshot"]
            source_rows = source_snapshot["rows"]
            runner_sha = sha256_file(runner_path)
            tool_info = manifest["tool"]
            verilator = Path(tool_info["verilator_path"])
            tool_bin = verilator.parent
            make_bin = RTL_TOOLCHAIN_ROOT / "usr" / "bin"
            env = build_verilator_env(tool_bin, make_bin, Path(tool_info["verilator_root"]))

        build_dir = work_dir / "build"
        binary = build_dir / "Vtb_s2c_rtl11_network_golden.exe"
        if not binary.is_file():
            raise RuntimeError(f"Verilator 编译产物缺失：{binary}")
        simulation_preflight = resource_preflight()
        expected_binary_hash = sha256_file(binary)
        compiled_binary = manifest.get("compiled_binary")
        if not compiled_binary or compiled_binary.get("sha256") != expected_binary_hash:
            raise RuntimeError("仿真 binary SHA 与该 RunId 编译阶段记录不一致")
        run_output_dir = evidence_dir
        summary_path = run_output_dir / "rtl11_result_summary.txt"
        progress_path = run_output_dir / "progress_markers.txt"
        head13_path = run_output_dir / "head13_actual_int8.bin"
        head26_path = run_output_dir / "head26_actual_int8.bin"
        simulation_command = [
            str(binary),
            f"+SAMPLE_INDEX={args.sample_index}",
            f"+FIXTURE_DIR={args.fixture_root.resolve(strict=True) / 'sample_000'}",
            f"+RESULT_FILE={summary_path}",
            f"+PROGRESS_FILE={progress_path}",
            f"+HEAD13_FILE={head13_path}",
            f"+HEAD26_FILE={head26_path}",
            f"+MAX_CYCLES={args.max_cycles}",
        ]
        simulation_record = run_logged(
            simulation_command, cwd=build_dir, env=env,
            stdout_path=evidence_dir / "verilator_simulation.stdout.log",
            stderr_path=evidence_dir / "verilator_simulation.stderr.log",
            timeout_seconds=args.timeout_seconds,
            no_progress_seconds=args.no_progress_seconds,
            progress_path=progress_path,
        )
        manifest["phase"] = "all" if args.phase == "all" else "run-only"
        manifest["resource_preflight_simulation"] = simulation_preflight
        manifest["simulation"] = simulation_record
        manifest["binary"] = {"path": str(binary), "sha256": expected_binary_hash, "hash_basis": "worktree_disk"}
        manifest["ended_utc"] = now_utc()
        result["fixture_bindings"] = fixtures["bindings"]
        result["source_snapshot_binding_sha256"] = manifest["source_snapshot"]["snapshot_binding_sha256"]
        result["source_snapshot_binding_sha256_hash_basis"] = "worktree_disk"
        result["tool_version"] = manifest["tool"]["version"]
        result["compile_exit_code"] = manifest["compile"]["exit_code"]
        result["simulation_exit_code"] = simulation_record["exit_code"]
        result["simulation"] = simulation_record
        result["binary_sha256"] = expected_binary_hash
        result["binary_sha256_hash_basis"] = "worktree_disk"
        if simulation_record["exit_code"] != 0 or simulation_record["timeout"]:
            if simulation_record.get("resource_held"):
                result["status"] = "RESOURCE_HELD"
            else:
                result["status"] = "SIMULATION_FAIL" if not simulation_record["timeout"] else "SIMULATION_TIMEOUT"
        else:
            validated = validate_outputs(fixtures, evidence_dir, summary_path, head13_path, head26_path, args.sample_index)
            result.update(validated)
        result["ended_utc"] = now_utc()
        manifest["status"] = result["status"]
        add_existing_item(manifest, summary_path, "actual_summary")
        add_existing_item(manifest, head13_path, "head13")
        add_existing_item(manifest, head26_path, "head26")
        write_json(result_path, result)
        manifest["result"] = {"path": str(result_path), "sha256": sha256_file(result_path), "hash_basis": "worktree_disk"}
        add_existing_item(manifest, result_path, "result")
        write_json(manifest_path, manifest)
        if result["status"] == "RESOURCE_HELD":
            return 3
        return 0 if result["status"] == "PASS_IDEAL_BULK_FRAME" else 1
    except Exception as exc:
        result["status"] = "RESOURCE_BLOCKED" if isinstance(exc, ResourceBlocked) else "RUNNER_ERROR"
        result["error"] = str(exc)
        result["ended_utc"] = now_utc()
        if evidence_dir.is_dir():
            write_json(result_path, result)
            if not manifest:
                manifest = {
                    "schema_version": "gestureforge_s2c_rtl11_network_golden_manifest_v1",
                    "task_id": TASK_ID,
                    "run_id": args.run_id,
                    "phase": args.phase,
                    "started_utc": started_utc,
                    "sample_index": args.sample_index,
                    "hash_basis": "worktree_disk",
                }
                if "fixtures" in locals():
                    manifest["fixture_bindings"] = fixtures.get("bindings")
                if "source_rows" in locals() and "snapshot_binding" in locals():
                    local_snapshot_root = evidence_dir / "source_snapshot"
                    local_snapshot_manifest = local_snapshot_root / "source_snapshot.json"
                    manifest["source_snapshot"] = {
                        "path": str(local_snapshot_manifest),
                        "sha256": sha256_file(local_snapshot_manifest) if local_snapshot_manifest.is_file() else None,
                        "hash_basis": "worktree_disk",
                        "snapshot_binding_sha256": snapshot_binding,
                        "rows": source_rows,
                    }
                    manifest["hash_basis_commit"] = locals().get("git_head")
                    manifest["items"] = source_items(source_rows, local_snapshot_manifest, locals().get("git_head", ""))
                if not manifest.get("items"):
                    fallback_items: list[dict[str, Any]] = []
                    for path, role in (
                        (runner_path, "runner"),
                        (REPO_ROOT / "sim" / "tb_s2c_rtl11_network_golden.sv", "testbench"),
                        (REPO_ROOT / "board" / "s2b_inference_platform.json", "platform"),
                    ):
                        if path.is_file():
                            fallback_items.append(evidence_item(path, role, "worktree_disk"))
                    manifest["items"] = fallback_items
                if "git_head" in locals():
                    manifest["hash_basis_commit"] = git_head
                manifest["concurrency"] = {"lock_path": str(lock_path), "lock_scope": "仅串行化本 runner；其他工具由总控协调并由启动前 CIM 门禁检查。"}
                if "compile_record" in locals():
                    manifest["compile"] = compile_record
            manifest["status"] = result["status"]
            manifest["error"] = str(exc)
            manifest["ended_utc"] = now_utc()
            for path, role in (
                (work_dir / "build" / "Vtb_s2c_rtl11_network_golden.exe", "compiled_binary"),
                (evidence_dir / "compile_result.json", "compile_result"),
                (evidence_dir / "rtl11_result_summary.txt", "actual_summary"),
                (evidence_dir / "head13_actual_int8.bin", "head13"),
                (evidence_dir / "head26_actual_int8.bin", "head26"),
            ):
                add_existing_item(manifest, path, role)
            write_json(result_path, result)
            manifest["result"] = {"path": str(result_path), "sha256": sha256_file(result_path), "hash_basis": "worktree_disk"}
            add_existing_item(manifest, result_path, "result")
            write_json(manifest_path, manifest)
        print(f"{TASK_ID} runner error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
