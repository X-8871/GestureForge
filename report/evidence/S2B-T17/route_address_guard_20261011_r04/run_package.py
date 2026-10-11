#!/usr/bin/env python3
"""捕获封包器和最终检查器真实退出码，最终检查输出只写隔离tmp避免清单自引用。"""
from pathlib import Path
import copy
import hashlib
import json
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
RUN = "route_address_guard_20261011_r04"
WORK = ROOT/"tmp/2B/S2B-T17"/RUN
EVIDENCE = ROOT/"report/evidence/S2B-T17"/RUN


def digest(p):
    """绑定原始字节。"""
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, obj):
    """新文件不覆盖。"""
    with p.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(obj, ensure_ascii=False, indent=2)+"\n")


def run(command):
    """直接捕获进程returncode及stdout，峰未测明确null。"""
    started = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return result.stdout, {"command": command, "native_exit_code": result.returncode,
        "seconds": round(time.monotonic()-started, 3), "peak_tree_rss_bytes": None, "capture_method": "subprocess.run.returncode"}


def main():
    """封闭r03产物，再只读验证最终清单；不更改生产源码。"""
    out, record = run([sys.executable, "-B", str(WORK/"pack_delivery.py")])
    (EVIDENCE/"pack_native_stdout.log").write_text(out, encoding="utf-8", newline="\n")
    write(EVIDENCE/"pack_native_capture.json", record)
    print(out, flush=True)
    if record["native_exit_code"] != 0: return record["native_exit_code"]
    shutil.copyfile(Path(__file__), EVIDENCE/"run_package.py")
    prior = json.loads((EVIDENCE/"delivery_manifest_r02.json").read_text(encoding="utf-8"))
    rows = {r["path"]: r for r in prior["files"]}
    for p in EVIDENCE.rglob("*"):
        if p.is_file():
            relative = p.relative_to(ROOT).as_posix()
            rows[relative] = {"path": relative, "sha256": digest(p), "role": "log" if p.suffix == ".log" else "diagnostic" if p.name == "source_diff.patch" else "artifact"}
    prior["files"] = sorted(rows.values(), key=lambda r: r["path"])
    prior["checks"].append({"name": "r03_package_build", "status": "PASS", "command": subprocess.list2cmdline(record["command"]), "exit_code": record["native_exit_code"]})
    final = EVIDENCE/"delivery_manifest_r03.json"; write(final, prior)
    closure = []
    for mode, expected in (("evidence", 0), ("inputs", 2)):
        stdout, actual = run([sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", mode,
                             "--manifest", final.relative_to(ROOT).as_posix()])
        (WORK/("final_"+mode+".log")).write_text(stdout, encoding="utf-8", newline="\n")
        actual["stdout_sha256"] = digest(WORK/("final_"+mode+".log")); closure.append(actual)
        if actual["native_exit_code"] != expected:
            write(WORK/"final_failure.json", {"records": closure}); print(stdout, flush=True); return 1
    freeze = json.loads((EVIDENCE/"source_freeze.json").read_text(encoding="utf-8"))
    assert all(digest(ROOT/p) == value for p, value in freeze["source_sha256"].items())
    receipt = {"status": "STOP_PASS_G1_ONLY", "manifest": final.relative_to(ROOT).as_posix(),
        "manifest_sha256": digest(final), "source_freeze_sha256": digest(EVIDENCE/"source_freeze.json"),
        "source_binding_count": freeze["source_binding_count"], "static_binding_count": freeze["static_binding_count"],
        "records": closure, "source_still_stopped": True, "g2": "NOT_RUN", "sta": "NOT_RUN", "g3": "NOT_RUN",
        "receipt_placement": "最终只读检查输出在tmp；正式目录已封闭，避免自引用hash"}
    write(WORK/"final_receipt.json", receipt)
    print(json.dumps(receipt, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
