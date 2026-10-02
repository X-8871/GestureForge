"""隔离恢复和CPU复验的临时执行器，不修改生产源码。"""
import datetime, hashlib, json, os, platform, subprocess, sys, time
from pathlib import Path
clean = Path(__file__).resolve().parent
evidence = Path(sys.argv[1])
started = time.monotonic()
result = {"schema_version": 1, "purpose": "真实干净副本T25恢复与CPU D9复验", "source_commit": "d530281d7399166c877a9b9105c3230cf175eeb0", "clean_root": str(clean), "python_executable": sys.executable, "runtime": {"python": platform.python_version()}, "start_time_local": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(), "restore": {"status": "NOT_RUN"}, "cpu_d9": {"status": "NOT_RUN"}, "runtime_109_inspected": False, "stage2a_frozen": False}
try:
    import numpy, cv2
    result["runtime"].update(numpy=numpy.__version__, opencv=cv2.__version__)
    expected = json.loads((clean / "report/evidence/S2A-T25/cpu_layer_golden_index.json").read_text(encoding="utf-8"))["runtime"]
    if result["runtime"] != expected:
        raise RuntimeError("恢复运行时与冻结index不一致")
    command = [sys.executable, "-B", "-u", str(clean / "verification/restore_s2a_t25_shards.py"), "--repo-root", str(clean), "--max-sample-seconds", "600", "--max-total-seconds", "7200"]
    result["restore"] = {"command": command, "status": "STARTED", "max_total_seconds": 7200, "max_sample_seconds": 600}
    print("开始单进程冻结T25真实恢复", flush=True)
    phase = time.monotonic()
    with (evidence / "restore_stdout.txt").open("xb") as out, (evidence / "restore_stderr.txt").open("xb") as err:
        completed = subprocess.run(command, cwd=clean, stdout=out, stderr=err, timeout=7320, check=False)
    result["restore"].update(exit_code=completed.returncode, elapsed_seconds=round(time.monotonic()-phase,3))
    text = (evidence / "restore_stdout.txt").read_text(encoding="utf-8")
    if completed.returncode != 0 or "S2A-T25 shards restored: 109/109 samples, 38 layers/sample" not in text:
        result["restore"]["status"] = "FAILED"
        raise RuntimeError("真实恢复失败；保留错误日志")
    result["restore"]["status"] = "PASS_109_RESTORED_SHARDS"
    cpu_code = 'import hashlib,json; from verification.verify_s2a_t68_d9_outputs import verify_frozen_cpu_baseline; from verification import s2a_decode_nms_reference as t29; report,rows=verify_frozen_cpu_baseline(); assert len(rows)==109; print(json.dumps({"status":"PASS_109_FROZEN_CPU_CANONICAL_REPLAY","samples":len(rows),"canonical_sha256":hashlib.sha256(t29._canonical_evidence_bytes(report)).hexdigest()}))'
    command = [sys.executable, "-B", "-u", "-c", cpu_code]
    phase = time.monotonic()
    with (evidence / "cpu_d9_stdout.txt").open("xb") as out, (evidence / "cpu_d9_stderr.txt").open("xb") as err:
        completed = subprocess.run(command, cwd=clean, stdout=out, stderr=err, timeout=1800, check=False)
    result["cpu_d9"] = {"command": command, "exit_code": completed.returncode, "elapsed_seconds": round(time.monotonic()-phase,3), "status": "FAILED"}
    if completed.returncode != 0:
        raise RuntimeError("恢复副本CPU D9复验失败")
    result["cpu_d9"].update(json.loads((evidence / "cpu_d9_stdout.txt").read_text(encoding="utf-8")))
    result["status"] = "PASS_CLEAN_COPY_T25_RESTORE_AND_CPU_D9"
except BaseException as exc:
    result["status"] = "FAILED"
    result["error"] = str(exc)
finally:
    result["elapsed_seconds"] = round(time.monotonic()-started,3)
    result["end_time_local"] = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    result["logs"] = [{"path": str(p), "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(evidence.glob("*_stdout.txt")) + sorted(evidence.glob("*_stderr.txt"))]
    with (evidence / "recovery_execution_record.json").open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(result["status"], flush=True)
sys.exit(0 if result["status"] == "PASS_CLEAN_COPY_T25_RESTORE_AND_CPU_D9" else 2)