"""独立重建修改后的adapter测试闭包，验证公开账本与故障元数据。"""
from pathlib import Path
import importlib.util
import json
import time

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
report = {"status": "FAIL", "runs": []}
started = time.monotonic()
try:
    spec = importlib.util.spec_from_file_location("adapter_runner", ROOT / "verification/test_s2b_hp0_word_adapter_rtl.py")
    runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
    work, evidence = BASE / "adapter_work", BASE / "adapter_evidence"
    work.mkdir(); evidence.mkdir()
    runner.run(work, evidence, Path(r"D:\FPGA_S2A_MSYS2_20261001\env"), report)
except Exception as exc:
    report["status"] = "FAIL"; report["error"] = str(exc)
report["elapsed_seconds"] = round(time.monotonic() - started, 3)
(BASE / "adapter_result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": report["status"], "runs": report["runs"], "seconds": report["elapsed_seconds"]}, ensure_ascii=False))
raise SystemExit(0 if report["status"].startswith("PASS") else 2)
