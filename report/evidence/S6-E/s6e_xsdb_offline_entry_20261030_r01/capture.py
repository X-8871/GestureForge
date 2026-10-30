#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""固定离线入口输入并只读采集主机，不调用厂商程序或板卡接口。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
from datetime import datetime, timezone, timedelta

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[3]
MAIN = Path(r"D:\FPGA_Competition")
GIT = Path(r"C:\Program Files\Git\cmd\git.exe")
BASE = "b0f4a688aa618f891b673c9b779f6b68f6e7472c"
MAIN_BASE = "17624c371ec8ab0db541897898fd0621cc891236"
STATE_INITIAL = "643270038e5df06a7d72b0b33b768986392e2af33a0553e45ba57299658a3af9"
EXPECTED_ROOT = Path(r"D:\codex-worktrees\w6")


def dump(path, value):
    """新建原始采集文件，拒绝覆盖。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def execute(argv, cwd=ROOT):
    """保存真实命令及工作目录，不把查询成功等同空闲。"""
    started = time.perf_counter()
    result = subprocess.run(argv, cwd=cwd, capture_output=True)
    return {"argv": argv, "working_directory": str(cwd), "exit_code": result.returncode,
            "stdout": result.stdout.decode("utf-8-sig", "replace"),
            "stderr": result.stderr.decode("utf-8-sig", "replace"),
            "duration_seconds": round(time.perf_counter() - started, 6)}


def git(*args):
    return execute([str(GIT), "--no-optional-locks", "-c", "core.longpaths=true", "-C", str(ROOT), *args])


def inputs():
    """仅消费指定五份固定提交 blob，逐字节保真。"""
    specs = [
        (MAIN, MAIN_BASE, "report/evidence/CTRL-DSH-HANDOFF/dsh_mailbox/DSH-20261030-014-ack-cdx-015-019-semantics-and-xsdb-entry.md", "input_dsh014.md"),
        (MAIN, MAIN_BASE, "verification/check_stage_delivery.py", "input_check_stage_delivery.py"),
        (MAIN, MAIN_BASE, "verification/check_manifest_hash_basis.py", "input_check_manifest_hash_basis.py"),
        (ROOT, BASE, "report/evidence/S6-E/s6e_board_window_check_20261030_r01/delivery_manifest.json", "input_prior_delivery_manifest.json"),
        (ROOT, BASE, "report/evidence/S6-E/s6e_board_window_check_20261030_r01/execution.json", "input_prior_execution.json"),
    ]
    bindings = []
    for repository, commit, path, target in specs:
        argv = [str(GIT), "--no-optional-locks", "-c", "core.longpaths=true", "-C", str(repository), "cat-file", "blob", f"{commit}:{path}"]
        proc = subprocess.run(argv, capture_output=True, check=True)
        with (RUN / target).open("xb") as stream:
            stream.write(proc.stdout)
        bindings.append({"repository": str(repository), "commit": commit, "path": path,
                         "sha256": digest(proc.stdout), "hash_basis": "commit_blob", "snapshot": target,
                         "bytes": len(proc.stdout), "command": argv, "exit_code": proc.returncode})
    dump(RUN / "source_bindings.json", {"hash_basis": "commit_blob", "bindings": bindings,
         "note": "所有固定输入权威字节均来自声明提交的Git blob；不修改原失败RunId"})


def state_comparison(content):
    """只允许剔除本轮总控新增的完整同级段，不能忽略旧STATE变化。"""
    marker = "## XSDB官方入口恢复".encode("utf-8")
    if marker not in content:
        return content, "STATE未含本轮新增段，直接比较初始字节"
    if content.count(marker) != 1:
        raise ValueError("STATE新增段标记不唯一")
    begin = content.index(marker)
    if begin and content[begin - 1:begin] != b"\n":
        raise ValueError("STATE新增段不是行首标题")
    end = content.find(b"\n## ", begin + len(marker))
    if end == -1:
        return content[:begin], "剔除本轮XSDB官方入口恢复段至文件结尾"
    return content[:begin] + content[end + 1:], "仅剔除本轮XSDB官方入口恢复段至下一同级标题"


def protection():
    """296项使用旧清单，STATE严格恢复到本轮初始哈希。"""
    reference = ROOT / "report/evidence/S6-C/s6c_isolated_recovery_20261030_r01/protected_worktree_check.json"
    original = json.loads(reference.read_text(encoding="utf-8"))
    records = []
    for item in original["files"]:
        content = (ROOT / item["path"]).read_bytes()
        compared, note = (state_comparison(content) if item["path"] == ".codex/STATE.md" else (content, "旧清单原始字节"))
        expected = STATE_INITIAL if item["path"] == ".codex/STATE.md" else item["sha256"]
        records.append({"path": item["path"], "sha256": digest(content), "hash_basis": "worktree_disk",
                        "expected_sha256": expected, "expected_hash_basis": "worktree_disk",
                        "compared_sha256": digest(compared), "comparison_note": note,
                        "matches_expected": digest(compared) == expected})
    return {"reference": reference.relative_to(ROOT).as_posix(), "reference_sha256": digest(reference.read_bytes()),
            "hash_basis": "worktree_disk", "file_count": len(records), "mismatches": [x["path"] for x in records if not x["matches_expected"]],
            "note": "不与oldguard旧STATE直接比；STATE按本轮初始SHA且仅允许移除声明新增段", "records": records}


def capture(label):
    """读取CIM、USB设备和监听；每个标签只采集一次。"""
    script = r'''
$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false)
$all=Get-CimInstance Win32_Process
$wanted=@($all | Where-Object { $_.Name -match '^(hw_server|xsdb|vivado|xsim|vitis|python)(\.exe)?$' })
$ids=@($wanted.ProcessId)+@($wanted.ParentProcessId)
$processes=@($all | Where-Object { $_.ProcessId -in $ids -or $_.ParentProcessId -in @($wanted.ProcessId) } | Select-Object Name,ProcessId,ParentProcessId,ExecutablePath,CreationDate)
$devices=@(Get-PnpDevice | Where-Object { $_.InstanceId -match 'FTDI|VID_0403|VID_10C4' -or $_.FriendlyName -match 'FTDI|CP210' } | Select-Object Status,Class,FriendlyName,InstanceId)
$listeners=@(Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -in @(3121,23121) } | Select-Object LocalAddress,LocalPort,OwningProcess,State)
[pscustomobject]@{Processes=$processes; Devices=$devices; Listeners=$listeners; PowerShellVersion=$PSVersionTable.PSVersion.ToString()} | ConvertTo-Json -Depth 8
'''
    commands = {"root": ("rev-parse", "--show-toplevel"), "branch": ("branch", "--show-current"), "head": ("rev-parse", "HEAD"),
                "index": ("diff", "--cached", "--name-only"), "lock": ("rev-parse", "--git-path", "index.lock"), "status": ("status", "--short")}
    queries = {key: git(*args) for key, args in commands.items()}
    lock = Path(queries["lock"]["stdout"].strip())
    if not lock.is_absolute():
        lock = ROOT / lock
    host_query = execute(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script])
    root_matches = Path(queries["root"]["stdout"].strip()).resolve() == EXPECTED_ROOT.resolve()
    valid = (ROOT == EXPECTED_ROOT and root_matches and queries["head"]["stdout"].strip() == BASE
             and queries["branch"]["stdout"].strip() == "stage6-interact-prep" and not queries["index"]["stdout"].strip()
             and not lock.exists() and all(x["exit_code"] == 0 for x in queries.values()))
    snapshot = {"captured_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(), "label": label, "worktree": str(ROOT),
                "git_queries": queries, "resolved_index_lock": str(lock), "index_lock_exists": lock.exists(),
                "identity_check": "PASS" if valid else "FAIL", "host_query": host_query,
                "host_query_status": "PASS" if host_query["exit_code"] == 0 else "FAIL",
                "hardware_api_called": False, "serial_opened": False, "peak_memory_bytes": None,
                "peak_memory_note": "峰值内存未测；采集成功不自动声明主机空闲"}
    if host_query["exit_code"] == 0:
        host = json.loads(host_query["stdout"])
        snapshot["host"] = host
        relevant = {"hw_server.exe", "xsdb.exe", "vivado.exe", "xsim.exe", "vitis.exe"}
        active = [p for p in host["Processes"] if p["Name"].lower() in relevant]
        snapshot["host_observation"] = {"relevant_processes_present": bool(active), "listeners_present": bool(host["Listeners"]),
             "observed_idle_for_listed_tools_and_ports": not active and not host["Listeners"],
             "scope": "只针对已列工具与3121/23121端口；不证明板卡状态、租约或硬件身份"}
    dump(RUN / f"host_snapshot_{label}.json", snapshot)
    dump(RUN / ("protected_worktree_check.json" if label == "pre" else "protected_worktree_check_post.json"), protection())
    print(json.dumps({"label": label, "identity": snapshot["identity_check"], "host_query": snapshot["host_query_status"]}, ensure_ascii=False))


if __name__ == "__main__":
    if ROOT != EXPECTED_ROOT or RUN.name != "s6e_xsdb_offline_entry_20261030_r01":
        raise SystemExit("精确路径核验失败")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["inputs", "capture"])
    parser.add_argument("--label", choices=["pre", "post"], default="pre")
    args = parser.parse_args()
    inputs() if args.action == "inputs" else capture(args.label)
