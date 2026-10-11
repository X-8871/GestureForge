"""补充独立来源与完整postconfig逐调用反例；只保留本Run内mock原件。"""

import ast
import hashlib
import importlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

RUN = Path(__file__).absolute().parent
ROOT = RUN.parents[3]
sys.path.insert(0, str(ROOT))
FIXTURES = RUN / "supplement_fixtures"
FIXTURES.mkdir()
original_mkdtemp = tempfile.mkdtemp


def isolated_mkdtemp(*args, **kwargs):
    """只重定向测试临时落点，不改生产门禁或清理函数。"""
    kwargs["dir"] = FIXTURES
    return original_mkdtemp(*args, **kwargs)


class KeptTemp:
    """保留失败和成功的原字节；不自动删除Reviewer依赖。"""
    def __init__(self, *args, **kwargs):
        self.name = isolated_mkdtemp(prefix="cold_")

    def cleanup(self):
        pass


def save(name, data):
    with (RUN / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def sources():
    """实际192文件与23定义分别核验；通过AST不导入SDK。"""
    entry = ast.parse((ROOT / "vitis/run_s2b_visibility_probe.py").read_text(encoding="utf-8"))
    function = next(node for node in entry.body if isinstance(node, ast.FunctionDef) and node.name == "verify_runtime_sources")
    assignment = next(node for node in function.body if isinstance(node, ast.Assign) and any(isinstance(item, ast.Name) and item.id == "implementations" for item in node.targets))
    definitions = ast.literal_eval(assignment.value)
    binding = json.loads((ROOT / "report/evidence/S2B-T16/postconfig_20261011_r02/consumer_binding.json").read_text(encoding="utf-8"))
    closure = binding["sdk_file_closure"]
    checked = []
    for module, names in definitions.items():
        path = Path(closure[module]["path"])
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == closure[module]["sha256"]
        tree = ast.parse(raw.decode("utf-8-sig"))
        for name in names:
            body = tree.body
            value = None
            for part in name.split("."):
                values = [node for node in body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == part]
                assert len(values) == 1, (module, name)
                value = values[0]
                body = value.body
            assert isinstance(value, ast.FunctionDef)
            checked.append({"module": module, "definition": name, "line": value.lineno, "source_sha256": closure[module]["sha256"]})
    main = sum(len(names) for module, names in definitions.items() if module not in ("xsdb._tcf_reset", "xsdb._breakpoint"))
    assert main == 19 and len(definitions["xsdb._tcf_reset"]) == len(definitions["xsdb._breakpoint"]) == 2
    assert len(checked) == 23 and len(closure) == 192
    save("independent_23_definition_audit.json", {"status": "PASS", "sdk_files": 192, "main_definitions": 19,
         "tcf_reset_definitions": 2, "breakpoint_definitions": 2, "total_definitions": 23, "definitions": checked,
         "real_sdk_imports": 0})
    generated = RUN / "attempt_r02/generated_basis"
    root = ET.fromstring((generated / "s2b_inference.hwh").read_bytes())
    def port(instance, name):
        rows = root.findall(".//MODULE[@INSTANCE='" + instance + "']/PORTS/PORT[@NAME='" + name + "']")
        assert len(rows) == 1
        return rows[0]
    def links(node):
        return {(row.get("INSTANCE"), row.get("PORT")) for row in node.findall("./CONNECTIONS/CONNECTION")}
    consumers = {("ps7", "M_AXI_GP0_ACLK"), ("ps7", "S_AXI_HP0_ACLK"), ("axi_gp0_lite", "aclk"),
                 ("rst_fclk0", "slowest_sync_clk"), ("infer", "clk")}
    assert links(port("ps7", "FCLK_CLK0")) == consumers
    assert port("ps7", "FCLK_CLK0").get("CLKFREQUENCY") == "50000000"
    for instance, name in consumers:
        node = port(instance, name)
        assert node.get("CLKFREQUENCY") == "50000000" and links(node) == {("ps7", "FCLK_CLK0")}
    assert links(port("ps7", "FCLK_RESET0_N")) == {("rst_fclk0", "ext_reset_in")}
    assert links(port("rst_fclk0", "ext_reset_in")) == {("ps7", "FCLK_RESET0_N")}
    assert links(port("rst_fclk0", "peripheral_aresetn")) == {("axi_gp0_lite", "aresetn"), ("infer", "cold_resetn")}
    for instance, name in (("ps7", "FCLK_RESET0_N"), ("rst_fclk0", "ext_reset_in"), ("rst_fclk0", "peripheral_aresetn")):
        assert port(instance, name).get("POLARITY") == "ACTIVE_LOW"
    assert [node.get("VALUE") for node in root.findall(".//MODULE[@INSTANCE='rst_fclk0']/PARAMETERS/PARAMETER[@NAME='C_EXT_RESET_HIGH']")] == ["0"]
    csr = (ROOT / "src/s2b_control_csr.sv").read_text(encoding="utf-8")
    assert "q <= '0;\n            q.input_bytes <= 519168;\n            q.weight_addr <= 32'h00100000;\n            q.weight_bytes <= 5903100;" in csr
    save("independent_hwh_cold_defaults.json", {"status": "PASS", "hwh_clock_hz": 50000000,
         "clock_consumers": sorted(consumers), "reset_polarity": "ACTIVE_LOW", "ext_reset_high": 0,
         "csr_source_sha256": hashlib.sha256(csr.encode("utf-8")).hexdigest(),
         "cold_reset": {"zero_struct": True, "input_bytes": 519168, "weight_addr": "0x00100000", "weight_bytes": 5903100},
         "actual_frequency_measured": False})
    raw_dir = ROOT / "report/evidence/S2B-T16/postconfig_20261011_r02/mock_calls"
    raw_audit = []
    for folder in sorted(raw_dir.iterdir()):
        calls = [json.loads(line) for line in (folder / "jtag_calls.jsonl").read_text(encoding="utf-8").splitlines()]
        result = json.loads((folder / "jtag_result.json").read_text(encoding="utf-8"))
        assert result["calls"] == calls
        assert not result["cold_lifecycle_proven"]
        assert all("args" in row and "kwargs" in row and "stdout" in row and "stderr" in row for row in calls)
        app = [row for row in calls if row["api"] == "cpu0.dow.app"]
        if folder.name != "happy":
            assert not app and result["status"] == "FAILED"
        else:
            assert len(app) == 1 and result["postconfiguration"]["status"] == "PASS"
        assert not any(row["api"] == "cpu1.con" for row in calls)
        raw_audit.append({"scenario": folder.name, "simulated_api_calls": len(calls), "cold_lifecycle_proven": False})
    assert len(raw_audit) == 6 and sum(row["simulated_api_calls"] for row in raw_audit) == 673
    save("developer_six_raw_audit.json", {"status": "PASS", "real_sdk_calls": 0, "mock_calls": 673, "scenarios": raw_audit})


def tests():
    """逐调用83故障与T19三个wire锁反例在隔离Run复跑。"""
    from verification import test_s2b_cold_observation as cold
    from verification import test_s2b_visibility_probe as visibility
    suite = unittest.TestSuite()
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(cold.PostconfigTests))
    suite.addTest(visibility.LifecycleTests("test_postconfig_failure_locks_wire_before_app_load_or_uart_request"))
    with patch.object(tempfile, "mkdtemp", side_effect=isolated_mkdtemp), patch.object(tempfile, "TemporaryDirectory", KeptTemp):
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    assert not any(name == "xsdb" or name.startswith("xsdb.") or name == "serial" for name in sys.modules)
    files = list(FIXTURES.rglob("jtag_calls.jsonl"))
    simulated = sum(len(path.read_text(encoding="utf-8").splitlines()) for path in files)
    save("supplement_test_result.json", {"status": "PASS" if result.wasSuccessful() else "FAIL",
         "methods": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
         "retained_jtag_call_logs": len(files), "simulated_api_calls": simulated, "real_sdk_calls": 0,
         "hardware_operations": 0, "temp_root_redirected": True, "temp_cleanup_preserved_raw": True,
         "test_source_unchanged": True})
    return result.wasSuccessful()


if __name__ == "__main__":
    sources()
    raise SystemExit(0 if tests() else 1)
