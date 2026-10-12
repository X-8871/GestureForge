"""纯fixture验证44/43集合、严格配置、client移交；不读取生产源或生成冻结。"""
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import collector as c
import compat_pins as pins

W = Path(__file__).absolute().parent


class Closure(unittest.TestCase):
    def run_closure(self, count=44, broken=None):
        names = ["fixture/源"+str(i) for i in range(count-1)]+["verification/test_s2b_conv_tile_origin_rtl.py"]
        hashes = {name: "a"*64 for name in names}; static = {name: value for name, value in list(hashes.items())[:33]}
        original14 = dict(list(static.items())[:14]); rtl = names[:18]
        freeze = dict(profile="s2b-inference-platform/0.1.13", source_commit="b"*40, source_files=[dict(path=k, sha256=v) for k,v in hashes.items()], frozen14=original14, active_rtl_sources=rtl)
        profile = dict(version=freeze["profile"], rtl_sources=rtl, source_derivation=dict(derived_sources=names[:8]), clock_hz=50000000, visibility_default=0)
        if broken == "runner": freeze["source_files"] = freeze["source_files"][:-1]
        if broken == "profile": freeze["profile"] = "s2b-inference-platform/0.1.12"
        if broken == "rtl": profile["rtl_sources"] = rtl[:-1]
        if broken == "clock": profile["clock_hz"] = 40000000
        loader = SimpleNamespace(exec_module=lambda module: (setattr(module, "check_static", lambda root: static), setattr(module, "FROZEN_CORE_SHA256", original14)))
        with patch.object(pins, "require_ready"), patch.object(c, "require_pinned_commit"), patch.object(c, "exact", side_effect=lambda p,*a: p), patch.object(c, "sha", return_value="a"*64), patch.object(c, "FREEZE_SHA", "a"*64), patch.object(c, "read", side_effect=lambda p: freeze if p==c.FREEZE else profile), patch.object(c.importlib.util, "spec_from_file_location", return_value=SimpleNamespace(loader=loader)), patch.object(c.importlib.util, "module_from_spec", return_value=SimpleNamespace()):
            return c.load_freeze()

    def test_actual_count_not_fixed43(self):
        for count in (43, 44): self.assertEqual(len(self.run_closure(count)[1]), count)

    def test_hard_requirements(self):
        for broken in ("runner", "profile", "rtl", "clock"):
            with self.assertRaises(ValueError): self.run_closure(broken=broken)


class Pairing(unittest.TestCase):
    def call(self, payload):
        return dict(input=dict(session_id="fixture-only", command="wait_on_run synth_1"), result=dict(content=[dict(type="text", text=json.dumps(payload))]))

    def test_running_handoff(self):
        payload=dict(status="running", command="wait_on_run synth_1", session_id="fixture-only")
        result=c.client_pair(dict(command=payload["command"], code=0), "wait", self.call(payload))
        self.assertTrue(result["client_running_handoff"]); self.assertIsNone(result["client_exit_code"])
        for key,value in (("session_id", "other"), ("exit_code", 0), ("command", "wait_on_run impl_1")):
            broken=dict(payload); broken[key]=value
            with self.assertRaises(ValueError): c.client_pair(dict(command=payload["command"],code=0), "wait", self.call(broken))
        with self.assertRaises(ValueError): c.client_pair(dict(command=payload["command"],code=0), "launch", self.call(payload))

    def test_products_capture_failure_preserved(self):
        row=c.client_pair(dict(command="products",code=1), "builder", self.call(dict(exit_code=1)))
        self.assertEqual(row["client_exit_code"], 1)
        with self.assertRaises(ValueError): c.client_pair(dict(code=0), "close", self.call(dict(exit_code=True)))


class Config(unittest.TestCase):
    def test_pending_refused(self):
        self.assertFalse(pins.RUNTIME_CONFIG.exists())
        for pnr in (False, True):
            with self.assertRaises(ValueError): pins.require_ready(pnr)

    def test_schema_duplicate_extra_normalization(self):
        data={key: None for key in pins._CONFIG_FIELDS}
        for key in pins._CONFIG_PATHS:
            if key not in {"SYNTH_MANIFEST", "SYNTH_G2"}: data[key]=str(W/"fixture_only_unused_target")
        cases=[("duplicate", '{"SOURCE_COMMIT":null,"SOURCE_COMMIT":null}'), ("extra", json.dumps(dict(data, GUARD_SHA="a"*64))), ("normalized", json.dumps(dict(data, PROJECT=(W/"fixture_only_unused_target").as_posix())))]
        directory=W/"config_schema_fixtures_r02"; directory.mkdir()
        saved={key:getattr(pins,key) for key in pins._CONFIG_FIELDS}; saved_sha=pins._LOADED_CONFIG_SHA
        for label,raw in cases:
            path=directory/(label+".json")
            with path.open("x",encoding="utf-8",newline="\n") as stream: stream.write(raw+"\n")
            with patch.object(pins,"RUNTIME_CONFIG",path):
                with self.assertRaises(ValueError): pins.load_runtime_config()
            for key,value in saved.items(): setattr(pins,key,value)
            pins._LOADED_CONFIG_SHA=saved_sha

    def test_parse_and_common_fixed(self):
        digest=hashlib.sha256((W/"collector.py").read_bytes()).hexdigest()
        for name in ("impl_collector.py", "source_after_check.py"):
            tree=ast.parse((W/name).read_text(encoding="utf-8"))
            values={node.targets[0].id: ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and isinstance(node.value,ast.Constant)}
            self.assertEqual(values["COMMON_SHA"],digest)
        for path in W.glob("*.py"): ast.parse(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(cls) for cls in (Closure,Pairing,Config)]))
    if not result.wasSuccessful(): raise SystemExit(1)
    with (W/"collector_fixture_result_r02.json").open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(dict(status="PASS_G1_FIXTURE_ONLY",methods=result.testsRun,source_count_cases=[43,44],actual_production_reads=False,production_source_commit=None,source_freeze_written=False,project_created=False,hardware_or_vivado_started=False),stream,ensure_ascii=False,indent=2); stream.write("\n")
