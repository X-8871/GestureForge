"""独立额外场景，复用公共驱动而独立给出预期值。"""
from pathlib import Path
import importlib.util
import json
import os
import shutil
import time

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
report = {"status": "FAIL", "runs": []}
started = time.monotonic()
try:
    spec = importlib.util.spec_from_file_location("runner", ROOT / "verification/test_s2b_control_csr_rtl.py")
    runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
    work, evidence = BASE / "supplemental_work_r02", BASE / "supplemental_evidence_r02"
    work.mkdir(); evidence.mkdir(); (work / "source").mkdir()
    for source in (BASE / "control_work/source").iterdir():
        shutil.copyfile(source, work / "source" / source.name)
    tb = work / "source/tb_s2b_control_csr.sv"
    original = tb.read_text(encoding="utf-8")
    assert original.count("    initial begin\n") == 1
    fixture = original.split("    initial begin\n")[0]
    fixture = fixture.replace("random_count=0, ", "")
    fixture = fixture.replace("    int phase_coverage[4]='{default:0};\n", "")
    fixture = fixture.replace("    int runtime_phase_coverage[4]='{default:0};\n", "")
    fixture = fixture.replace("    int unsigned rng=32'h2b111010;\n", "")
    fixture = fixture.replace("            if(adapter_progress[8])", "            must(!(adapter_progress[7] && adapter_progress[9]),\"独立B待归还与已见互斥\");\n            if(adapter_progress[8])")
    tb.write_text(fixture + (BASE / "supplemental.svfrag").read_text(encoding="utf-8"), encoding="utf-8")
    shutil.copyfile(tb, evidence / "tb_independent.sv")
    report["fixture_sha256"] = runner.sha(tb)
    old = json.loads((BASE / "result.json").read_text(encoding="utf-8"))
    report["sources"] = old["sources"]
    tools = Path(r"D:\FPGA_S2A_MSYS2_20261001\env")
    env = os.environ.copy()
    env["PATH"] = str(tools / "usr/bin") + os.pathsep + str(tools / "mingw64/bin") + os.pathsep + env["PATH"]
    env["VERILATOR_ROOT"] = str(tools / "mingw64/share/verilator")
    runner.execute("compile", old["runs"][0]["command"], work, evidence, env, report)
    runner.execute("simulation", [str(work / "obj_dir/Vtb_s2b_control_csr.exe")], work, evidence, env, report)
    assert "PASS_INDEPENDENT_CONTROL cases=6" in (evidence / "simulation.log").read_text(encoding="utf-8")
    report["status"] = "PASS_INDEPENDENT_6_SCENARIOS"
except Exception as exc:
    report["error"] = str(exc)
report["seconds"] = round(time.monotonic() - started, 3)
(BASE / "supplemental_result_r02.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))
raise SystemExit(0 if report["status"].startswith("PASS") else 2)
