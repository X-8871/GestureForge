#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只读采集主机进程、设备、监听及工作树身份；不调用任何板卡接口。"""
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
BASE = "8d30a9ff693284d5d8fffcd676c6ca94627e6790"
MAIN_BASE = "0fa4272f7ffff85b9314a71de79724398aa4e7d8"
OFFER_BASE = "4646d4852fa1e8584e3ccf69582672b127335bd4"

def dump(path, value):
    """以无 BOM 的 UTF-8 写入新文件，不覆盖原始采集。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")

def digest(data):
    return hashlib.sha256(data).hexdigest()

def execute(argv, cwd=ROOT):
    """保留实际命令、退出码和耗时，不隐去查询失败。"""
    started = time.perf_counter()
    result = subprocess.run(argv, cwd=cwd, capture_output=True)
    return {"command": argv, "exit_code": result.returncode,
            "stdout": result.stdout.decode("utf-8-sig", "replace"),
            "stderr": result.stderr.decode("utf-8-sig", "replace"),
            "duration_seconds": round(time.perf_counter() - started, 6)}

def git(*args):
    return execute([str(GIT), "--no-optional-locks", "-c", "core.longpaths=true", "-C", str(ROOT), *args])

def inputs():
    """固定输入直接复制 Git blob；未提交回函仅作为磁盘附注。"""
    specs = [(MAIN_BASE, "report/evidence/CTRL-DSH-HANDOFF/dsh_mailbox/DSH-20261030-012-stage6-unblock-producer-and-board-window.md", "input_dsh012.md"),
             (OFFER_BASE, ".codex/STATE.md", "input_offer_state.md"),
             (OFFER_BASE, "verification/check_stage_delivery.py", "input_check_stage_delivery.py"),
             (OFFER_BASE, "verification/check_manifest_hash_basis.py", "input_check_manifest_hash_basis.py")]
    bindings = []
    for commit, path, target in specs:
        argv = [str(GIT), "--no-optional-locks", "-C", str(MAIN), "cat-file", "blob", f"{commit}:{path}"]
        proc = subprocess.run(argv, capture_output=True, check=True)
        with (RUN / target).open("xb") as stream:
            stream.write(proc.stdout)
        bindings.append({"repository": str(MAIN), "commit": commit, "path": path, "sha256": digest(proc.stdout),
                         "hash_basis": "commit_blob", "snapshot": target, "bytes": len(proc.stdout)})
    path = MAIN / "report/evidence/CTRL-DSH-HANDOFF/codex_mailbox/CDX-20261030-015-stage6-producer-partial-and-readonly-window.md"
    content = path.read_bytes()
    with (RUN / "input_cdx015_disk.md").open("xb") as stream:
        stream.write(content)
    bindings.append({"repository": str(MAIN), "path": path.relative_to(MAIN).as_posix(), "sha256": digest(content),
                     "hash_basis": "worktree_disk", "snapshot": "input_cdx015_disk.md", "note": "未提交回函，仅磁盘附注"})
    dump(RUN / "source_bindings.json", {"bindings": bindings, "note": "固定输入的权威字节为各自提交blob；快照逐字节复制"})

def protection():
    """只检查已声明的297个旧文件。STATE采用本轮初始哈希。"""
    reference = ROOT / "report/evidence/S6-C/s6c_isolated_recovery_20261030_r01/protected_worktree_check.json"
    original = json.loads(reference.read_text(encoding="utf-8"))
    records = []
    for item in original["files"]:
        content = (ROOT / item["path"]).read_bytes()
        current = digest(content)
        compared = content
        if item["path"] == ".codex/STATE.md":
            begin = content.index("## 6-E 板卡只读窗口（2026-10-30 21:00".encode("utf-8"))
            end = content.index("## 6-D 最新阶段5交付资格核验".encode("utf-8"), begin)
            compared = content[:begin] + content[end:]
        expected = ("f1c03a22161af100e29985f810f43e205939401b0ed0e268b82adb68ea2f7800" if item["path"] == ".codex/STATE.md" else item["sha256"])
        records.append({"path": item["path"], "sha256": current, "hash_basis": "worktree_disk", "expected_sha256": expected, "compared_sha256": digest(compared), "matches_expected": digest(compared) == expected})
    return {"reference": reference.relative_to(ROOT).as_posix(), "reference_sha256": digest(reference.read_bytes()),
            "hash_basis": "worktree_disk", "file_count": len(records), "mismatches": [x["path"] for x in records if not x["matches_expected"]],
            "note": "STATE剔除总控授权新增6-E段后比对本轮初始SHA，其余296项使用已提交旧清单；不剔除其他字节", "records": records}

def capture(label):
    """每个标签采集一次；异常如实保留，不重试硬件。"""
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
    host = execute(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script])
    valid = (queries["head"]["stdout"].strip() == BASE and queries["branch"]["stdout"].strip() == "stage6-interact-prep"
             and not queries["index"]["stdout"].strip() and not lock.exists() and all(x["exit_code"] == 0 for x in queries.values()))
    snapshot = {"captured_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(), "label": label, "worktree": str(ROOT),
                "git_queries": queries, "resolved_index_lock": str(lock), "index_lock_exists": lock.exists(), "identity_check": "PASS" if valid else "FAIL",
                "host_query": host, "host_query_status": "PASS" if host["exit_code"] == 0 else "FAIL", "hardware_api_called": False, "serial_opened": False,
                "peak_memory_bytes": None, "peak_memory_note": "未测量峰值内存"}
    if host["exit_code"] == 0:
        snapshot["host"] = json.loads(host["stdout"])
    dump(RUN / f"host_snapshot_{label}.json", snapshot)
    if label == "pre":
        dump(RUN / "protected_worktree_check.json", protection())
    print(json.dumps({"label": label, "identity": snapshot["identity_check"], "host_query": snapshot["host_query_status"]}, ensure_ascii=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["inputs", "capture"])
    parser.add_argument("--label", choices=["pre", "post"], default="pre")
    args = parser.parse_args()
    inputs() if args.action == "inputs" else capture(args.label)
