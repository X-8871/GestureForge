"""独立审阅重建，只向本审阅隔离目录写入验证证据。"""
from pathlib import Path
import hashlib
import importlib.util
import json
import time

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent

def main():
    """复用已审阅的真实编译入口，保存失败与成功原始输出。"""
    report = {"status": "FAIL", "runs": []}
    started = time.monotonic()
    try:
        spec = importlib.util.spec_from_file_location("control_runner", ROOT / "verification/test_s2b_control_csr_rtl.py")
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        work, evidence = BASE / "control_work", BASE / "control_evidence"
        work.mkdir(); evidence.mkdir()
        runner.run(work, evidence, Path(r"D:\FPGA_S2A_MSYS2_20261001\env"), report)
    except Exception as exc:
        report["status"] = "FAIL"
        report["error"] = str(exc)
    report["elapsed_seconds"] = round(time.monotonic() - started, 3)
    (BASE / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"].startswith("PASS") else 2

if __name__ == "__main__":
    raise SystemExit(main())
