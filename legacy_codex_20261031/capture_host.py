"""保存M3板窗前后固定安装工具与部署文件身份，不启动硬件。"""

import argparse
import hashlib
import json
import shutil
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


def main():
    """现有精确RunId内只写全新快照名；安装及上游文件保持只读。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--phase", choices=("pre", "pre_verified", "post"), required=True)
    args = parser.parse_args()
    run = args.run.resolve(strict=True)
    target = run / (args.phase + "_host_tool_identities.json")
    if not run.is_dir() or target.exists():
        parser.error("RunId必须存在且快照不得覆盖")
    start = time.monotonic()
    base = Path(r"D:\Xilinx\2026.1\Vitis")
    fixed = [base / "bin/xsdb.bat", base / "bin/setupEnv.bat", base / "bin/loader.bat",
             base / "bin/rdiArgs.bat", base / "bin/unwrapped/win64.o/xsdb.exe", base / "lib/win64.o/tcl86t.dll",
             Path(r"D:\Xilinx\2026.1\Vivado\bin\hw_server.bat"),
             Path(r"D:\Xilinx\2026.1\Vivado\bin\unwrapped\win64.o\hw_server.exe")]
    artifacts = {
        r"D:\FPGA_Competition\w2b\report\evidence\S2B-T19\visibility1_csr_fixed_20261016_r04\artifacts\s2b_inference.bit": "555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7",
        r"D:\FPGA_Competition\w2b\report\evidence\S2B-T19\visibility1_csr_fixed_20261016_r04\artifacts\s2b_inference.xsa": "ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6",
        r"D:\codex-worktrees\w4\report\evidence\S4-B\s4b_ps_tensor_20261023_r13\verified_payload\init.elf": "237dd959f903589c657b743ea1fce175628aaa24020384058fc66339c779e7b1",
        r"D:\tmp\lead\tailfix_20261029_r01\build\s4d_ps_app_sw0_chainA.elf": "87e049b4db8f7debd212f91b354648c2e83f845d419048ae5783d1a9923bdc52",
        r"D:\codex-worktrees\w4\report\evidence\S4-T32\window_a_20261027_r01\m3_snapshot_orig.bin": "41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf"}
    entries = []
    for path in fixed + [Path(name) for name in artifacts]:
        path = path.resolve(strict=True)
        if not path.is_file():
            raise ValueError(f"不是普通文件：{path}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        expected = artifacts.get(str(path))
        if expected and digest != expected:
            raise ValueError(f"部署输入身份不符：{path}")
        entries.append({"host_path": str(path), "sha256": digest, "bytes": path.stat().st_size,
                        "hash_basis": "worktree_disk", "meaning": "安装/上游只读身份附注；权威交付清单绑定本快照的commit_blob"})
    command = "$ErrorActionPreference='Stop'; $p=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^(hw_server|xsdb|vivado|xsim|vitis)[.]exe$'} | Select-Object ProcessId,ParentProcessId,Name,CreationDate,ExecutablePath); $l=@(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object {$_.LocalPort -in @(3121,3122)} | Select-Object LocalAddress,LocalPort,OwningProcess); [pscustomobject]@{processes=$p; listeners=$l} | ConvertTo-Json -Depth 6"
    proc = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command], capture_output=True)
    if proc.returncode:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace"))
    host = json.loads(proc.stdout.decode("utf-8-sig"))
    root = Path(__file__).resolve().parent.parent
    cm = subprocess.run(["git", "--no-optional-locks", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, check=True).stdout.decode().strip()
    record = {"phase": args.phase, "at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
              "source_baseline": cm, "installation_label": "Xilinx 2026.1（按精确安装路径与各文件SHA绑定）", "files": entries,
              "host": host, "host_query_exit_code": proc.returncode, "duration_seconds": time.monotonic() - start,
              "free_disk_bytes": shutil.disk_usage(run).free, "peak_memory": "未测", "hardware_started": False}
    target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if args.phase == "post":
        pre = json.loads((run / "pre_host_tool_identities.json").read_text(encoding="utf-8"))
        if pre["files"] != entries:
            raise ValueError("板窗前后工具链或部署输入身份变化")
    print(json.dumps({"snapshot": str(target), "files": len(entries), "host": host, "exit_code": 0}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
