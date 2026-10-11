"""代表性完整mock原调用证据；不消费正式ELF，不导入SDK，不打开串口。"""
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).absolute().parents[4]
RUN = ROOT / "report/evidence/S2B-T16/postconfig_20261011_r02"
sys.path.insert(0, str(ROOT))
from verification import test_s2b_board_jtag as fixture
from verification import s2b_board_jtag as j

assert RUN.is_dir() and not (RUN / "mock_capture_summary.json").exists()
assert not (RUN / Path(__file__).name).exists()
shutil.copyfile(Path(__file__), RUN / Path(__file__).name)
summaries = []
for scenario in ("happy", "reset_high_bits", "clock_bad", "unlock_partial_failure", "cleanup_failure", "cpu1_drift"):
    case = fixture.JtagTests(methodName="test_actual_symbol_addresses")
    case.setUp()
    original = case.session.objects[10].mwr
    def write(*args, **kwargs):
        original(*args, **kwargs)
        address = kwargs["address"]
        if scenario == "reset_high_bits" and address == 0xF8000240: case.session.memory[address] = 0x100
        if scenario in ("unlock_partial_failure", "cleanup_failure") and address == 0xF8000008: raise RuntimeError("MOCK原解锁异常")
        if scenario == "cleanup_failure" and address == 0xF8000004: raise RuntimeError("MOCK清理重锁异常")
        if scenario == "cpu1_drift" and address == 0xF8000008: case.session.objects[12].running = True
    case.session.objects[10].mwr = write
    if scenario == "clock_bad": case.session.memory[0xF8000170] = 0
    case.controller.record["hardware_execution"] = "NOT_RUN_MOCK_ONLY"
    error = None
    try:
        case.ready(); case.controller.deploy()
    except BaseException as caught: error = repr(caught)
    case.controller.close()
    target = RUN / "mock_calls" / scenario
    assert not target.exists(); target.mkdir(parents=True)
    for name in ("jtag_calls.jsonl", "jtag_result.json"):
        shutil.copyfile(case.run / name, target / name)
    summary = {"scenario": scenario, "scope": "MOCK_ONLY_NOT_HARDWARE", "raised": error,
               "controller_failed": case.controller.failed, "postconfigured": case.controller.postconfigured,
               "calls": len(case.controller.record["calls"]), "cpu1_running": case.session.objects[12].running,
               "app_downloads": sum(row[0] == "dow" and Path(row[2]).name == "app_elf" for row in case.session.operations),
               "operations": case.session.operations, "final_slcr_locksta": case.session.memory[0xF800000C],
               "input_fixture_files": {key: {"sha256": value["sha256"], "meaning": "由已冻结测试源码可重建；临时路径非实际下载输入。"} for key, value in case.bindings.items()}}
    assert (scenario == "happy") == (error is None)
    if scenario != "happy": assert summary["app_downloads"] == 0 and case.controller.failed
    summaries.append(summary)
    case.tearDown()
with (RUN / "mock_capture_summary.json").open("x", encoding="utf-8", newline="\n") as output:
    json.dump(summaries, output, ensure_ascii=False, indent=2); output.write("\n")
print(json.dumps({"mock_scenarios": len(summaries), "hardware_execution": "NOT_RUN", "real_sdk_calls": 0,
                  "call_count": sum(row["calls"] for row in summaries)}, ensure_ascii=False))
