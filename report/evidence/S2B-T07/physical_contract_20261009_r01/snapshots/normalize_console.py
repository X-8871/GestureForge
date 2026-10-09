import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys


# 先按UTF-8严格读取原始字节，仅在严格解码失败时才尝试GBK，不凭终端显示判断编码。
root = pathlib.Path(__file__).resolve().parents[4]
run = root / "report/evidence/S2B-T07/physical_contract_20261009_r01"
records = []
for name in ["packaging_initial_console.txt", "finalized_packaging_console.txt"]:
    path = run / name
    raw = path.read_bytes()
    backup = run / name.replace(".txt", "_raw.bin")
    if backup.exists():
        if backup.read_bytes() != raw:
            raise ValueError("原始日志备份与当前字节不符，不覆盖")
    else:
        backup.write_bytes(raw)
    try:
        text = raw.decode("utf-8", errors="strict")
        source_encoding = "utf-8"
    except UnicodeDecodeError:
        text = raw.decode("gbk", errors="strict")
        source_encoding = "gbk"
    parsed = json.loads(text)
    if parsed["status"] != "CHECKS_OK":
        raise ValueError("包装结果与此前退出0不符")
    path.write_text(text, encoding="utf-8", newline="")
    records.append({"path": path.relative_to(root).as_posix(), "raw_path": backup.relative_to(root).as_posix(),
        "raw_sha256": hashlib.sha256(raw).hexdigest(), "raw_bytes": len(raw),
        "source_encoding": source_encoding, "target_encoding": "utf-8", "decode_errors": "strict",
        "status_after_json_decode": parsed["status"],
        "reason": "按原始字节严格检测，原raw完整保留；终端二次显示不能证明文件编码"})
(run / "console_encoding_record.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for name in ["finalize_evidence.py", "normalize_console.py"]:
    destination = run / "snapshots" / name
    if destination.exists():
        raise ValueError("不覆盖包装源码快照")
    shutil.copyfile(pathlib.Path(__file__).resolve().parent / name, destination)
subprocess.run([sys.executable, "-B", str(run / "layout_analysis.py"), "--mode", "manifest"], cwd=root, check=True)
relative = run.relative_to(root).as_posix()
cmd = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", "evidence", "--manifest", f"{relative}/delivery_manifest.json"]
result = subprocess.run(cmd, cwd=root, capture_output=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
(run / "utf8_packaging_console.txt").write_bytes(result.stdout + result.stderr)
(run / "utf8_packaging_execution.json").write_text(json.dumps({"command": f"PYTHONIOENCODING=utf-8 python -B verification/check_stage_delivery.py --mode evidence --manifest {relative}/delivery_manifest.json",
    "argv": cmd, "exit_code": result.returncode, "scope": "UTF-8日志归档后包装核查；随后新增此日志并刷新清单，最终由总控再检查"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
subprocess.run([sys.executable, "-B", str(run / "layout_analysis.py"), "--mode", "manifest"], cwd=root, check=True)
print(json.dumps({"console_verified_count": len(records), "actual_transcode_count": sum(r["source_encoding"] != "utf-8" for r in records), "packaging_exit_code": result.returncode}))
raise SystemExit(result.returncode)
