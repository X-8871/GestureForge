"""S2B-T18 runner 的隔离门禁与失败语义测试。"""
from __future__ import annotations

import importlib.util
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).absolute().parents[1]
RUNNER_PATH = ROOT / "vitis/run_s2b_model_acceptance.py"
SPEC = importlib.util.spec_from_file_location("s2b_model_acceptance_runner_test_target", RUNNER_PATH)
runner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = runner
SPEC.loader.exec_module(runner)


class FakeWire:
    """只记录请求边界的隔离 UART 替身。"""
    def __init__(self, trace=None, *, fail_send=False, fail_banner=False):
        self.sent_requests = {}
        self.failed = False
        self.fail_send = fail_send
        self.trace = trace if trace is not None else []
        self.fail_banner = fail_banner

    def banner(self, source_sha, xsa_sha):
        self.trace.append("banner")
        self.banner_bindings = (source_sha, xsa_sha)
        if self.fail_banner:
            raise RuntimeError("mock banner failure")
        raw = f"S2B-INFERENCE/1 READY SOURCE={source_sha} XSA={xsa_sha}".encode("ascii")
        return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "text": raw.decode("ascii")}

    def send_request(self):
        self.sent_requests[len(self.sent_requests)] = True
        if self.fail_send:
            raise OSError("mock serial write failure")


class FakeController:
    """模拟现有 deploy() 的 EOS、postconfig 与 app 顺序。"""
    def __init__(self, trace, fail_at=None, fail_select=False):
        self.trace = trace
        self.fail_at = fail_at
        self.fail_select = fail_select
        self.configured = False
        self.postconfigured = False
        self.app_running = False
        self.failed = False

    def select_and_gate(self):
        self.trace.append("select_and_gate")
        if self.fail_select:
            raise RuntimeError("mock dynamic JTAG target failure")

    def system_reset_stop(self, basis):
        self.trace.append("system_reset_stop")

    def deploy(self):
        self.trace.append("download_init")
        self.trace.append("observe_eos1")
        if self.fail_at == "eos":
            raise RuntimeError("mock EOS1 failure")
        self.configured = True
        self.trace.append("postconfig")
        if self.fail_at == "postconfig":
            raise RuntimeError("mock postconfig failure")
        self.postconfigured = True
        self.trace.append("download_app")
        self.app_running = True

    def fail_stop(self):
        self.trace.append("fail_stop")


class FakeAcceptance:
    """把准入与 UART 请求分开，确认请求不会越过准入门。"""
    def __init__(self, trace, wire, *, fail_receipt=False):
        self.trace = trace
        self.wire = wire
        self.fail_receipt = fail_receipt
        self.admitted = False
        self.execute_count = 0
        self.receipt = {
            "status": "PASS",
            "role": "INDEPENDENT_REVIEWER",
            "approved_manifest_sha256": "a" * 64,
            "approved_profile_sha256": "b" * 64,
            "visibility_parameter": 1,
            "same_runtime_bsp_mmu_macros": True,
            "only_visibility_parameter_changed": True,
        }

    def admit(self, controller, wire, build, proof, review, review_sha, manifest, final_review, final_sha):
        self.trace.append("admit")
        self.assert_zero_tx(wire)
        receipt = self.receipt
        if self.fail_receipt:
            receipt = {**receipt, "approved_manifest_sha256": "0" * 64}
        runner.validate_final_review_receipt(receipt, "a" * 64, "b" * 64)
        self.admitted = True
        return {"status": "ADMITTED"}

    @staticmethod
    def assert_zero_tx(wire):
        runner.require(not wire.sent_requests, "准入前出现 UART 请求")

    def execute(self, controller, wire, preparation, run_dir, **kwargs):
        self.trace.append("execute")
        self.execute_count += 1
        runner.require(self.admitted, "未完成准入就进入 T18 execute")
        self.assert_zero_tx(wire)
        wire.send_request()
        return {"status": "PASS_MODEL_CORPUS_AND_STRESS_ONLY"}


class FakeApis:
    def __init__(self, acceptance, csr_flow=None):
        self.acceptance = acceptance
        self.csr_flow = csr_flow


class ModelAcceptanceRunnerTests(unittest.TestCase):
    def test_import_and_help_never_load_device_modules(self):
        with mock.patch.object(runner.importlib, "import_module", side_effect=AssertionError("不应导入硬件模块")) as importer:
            with self.assertRaises(SystemExit) as help_exit:
                runner.main(["--help"])
            self.assertEqual(help_exit.exception.code, 0)
            with self.assertRaises(SystemExit) as missing_config:
                runner.main([])
            self.assertEqual(missing_config.exception.code, 2)
            importer.assert_not_called()
        source = RUNNER_PATH.read_text(encoding="utf-8")
        self.assertNotRegex(source, r"(?m)^\s*(?:import|from)\s+run_s2b_visibility_probe")
        self.assertNotIn("cache_probe", source)
        self.assertNotIn("visibility0", source)

    def test_missing_config_fails_before_loading_apis_or_runtime(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_missing_") as temp:
            root = Path(temp)
            with mock.patch.object(runner, "ROOT", root), \
                    mock.patch.object(runner, "load_apis", side_effect=AssertionError("不得继续")):
                with self.assertRaises(runner.RunnerError):
                    runner.run(root / "missing_explicit_board_config.json")

    def test_source_and_artifact_sha_mismatch_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_sha_") as temp:
            root = Path(temp)
            artifact = root / "bound.bin"
            artifact.write_bytes(b"known bytes")
            with mock.patch.object(runner, "ROOT", root):
                for label in ("source", "artifact"):
                    with self.subTest(label=label), self.assertRaises(runner.RunnerError):
                        runner.verify_binding({"path": str(artifact), "sha256": "0" * 64}, label)

    def test_csr_deadline_source_pin_matches_current_source(self):
        source = ROOT / "verification/s2b_csr_deadline_flow.py"
        actual = hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertEqual(actual, runner.CSR_DEADLINE_SOURCE_SHA256)
        runner._verify_csr_flow_sources()

    def test_unpinned_g0_and_cold_basis_fail_before_runtime_or_device_import(self):
        with mock.patch.object(runner, "G0_BASIS_PATH", None), \
                mock.patch.object(runner, "G0_BASIS_SHA256", None), \
                mock.patch.object(runner, "COLD_BASIS_PATH", None), \
                mock.patch.object(runner, "COLD_BASIS_SHA256", None), \
                tempfile.TemporaryDirectory(prefix="s2b_t18_default_block_") as temp:
            root = Path(temp)
            config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
            self._assert_run_preflight_fails(root, config_path, "尚无独立审查固定的正式回执SHA")

    def test_missing_g0_receipt_fails_before_runtime_or_device_import(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_missing_g0_") as temp:
            root = Path(temp)
            config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["g0_basis"] = None
            config_path.write_text(json.dumps(config), encoding="utf-8")
            self._assert_run_preflight_fails(root, config_path, "G0冻结回执 绑定格式错误")

    def test_candidate_not_frozen_blocks_even_when_config_claims_receipt(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_candidate_g0_") as temp:
            root = Path(temp)
            config_path = self._make_preflight_tree(root, physical="CANDIDATE_NOT_FROZEN", uart="G0_FROZEN")
            with mock.patch.object(runner, "G0_BASIS_PATH", Path("claimed.json")), \
                    mock.patch.object(runner, "G0_BASIS_SHA256", "a" * 64):
                self._assert_run_preflight_fails(root, config_path, "PS/PL物理接口仍未冻结")

    def test_checked_in_frozen_interface_versions_parse_without_claiming_g0_deployment(self):
        bindings = {}
        for name, relative in (
                ("interface", "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"),
                ("uart_interface", "docs/obsidian-project/02-方案设计/s2b_board_transport.md")):
            path = runner.ROOT / relative
            bindings[name] = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        self.assertEqual(runner._validate_interface_freeze_sources(bindings),
                         {"interface": "s2b-physical/1.0.0", "uart_interface": "s2bu/1.1"})

    def test_interface_version_parser_rejects_duplicate_and_wrong_prefix_versions(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_duplicate_interface_version_") as temp:
            root = Path(temp)
            config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
            config = json.loads(config_path.read_text(encoding="utf-8"))
            physical_path = Path(config["bindings"]["interface"]["path"])
            cases = (
                ("test-only: 状态：G0_FROZEN；版本：s2b-physical/1.0.0；版本：s2b-physical/1.1.0\n",
                 "唯一且前缀正确"),
                ("test-only: 状态：G0_FROZEN；版本：s2bu/1.1\n", "唯一且前缀正确"),
            )
            for content, error in cases:
                with self.subTest(content=content):
                    physical_path.write_text(content, encoding="utf-8")
                    config["bindings"]["interface"]["sha256"] = hashlib.sha256(
                        physical_path.read_bytes()).hexdigest()
                    with mock.patch.object(runner, "ROOT", root), self.assertRaisesRegex(
                            runner.RunnerError, error):
                        runner._validate_interface_freeze_sources(config["bindings"])

    def test_stale_g0_pin_fails_before_runtime_or_device_import(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_stale_g0_") as temp:
            root = Path(temp)
            config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
            config = json.loads(config_path.read_text(encoding="utf-8"))
            g0_path = Path(config["g0_basis"]["path"])
            with mock.patch.object(runner, "G0_BASIS_PATH", g0_path), \
                    mock.patch.object(runner, "G0_BASIS_SHA256", "f" * 64), \
                    mock.patch.object(runner, "COLD_BASIS_PATH", Path(config["cold_basis"]["path"])), \
                    mock.patch.object(runner, "COLD_BASIS_SHA256", config["cold_basis"]["sha256"]):
                self._assert_run_preflight_fails(root, config_path, "原字节与独立审查固定SHA不符")

    def test_nonempty_but_unapproved_cold_basis_fails_before_runtime_or_device_import(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_cold_unapproved_") as temp:
            root = Path(temp)
            config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
            config = json.loads(config_path.read_text(encoding="utf-8"))
            g0_path = Path(config["g0_basis"]["path"])
            cold_path = Path(config["cold_basis"]["path"])
            with mock.patch.object(runner, "G0_BASIS_PATH", g0_path), \
                    mock.patch.object(runner, "G0_BASIS_SHA256", config["g0_basis"]["sha256"]), \
                    mock.patch.object(runner, "COLD_BASIS_PATH", cold_path), \
                    mock.patch.object(runner, "COLD_BASIS_SHA256", "e" * 64):
                self._assert_run_preflight_fails(root, config_path, "原字节与独立审查固定SHA不符")

    def test_synthetic_test_only_exact_pins_pass_static_preflight(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_synthetic_pins_") as temp:
            root = Path(temp)
            config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
            config = json.loads(config_path.read_text(encoding="utf-8"))
            g0_path = Path(config["g0_basis"]["path"])
            cold_path = Path(config["cold_basis"]["path"])
            with mock.patch.object(runner, "ROOT", root), \
                    mock.patch.object(runner, "G0_BASIS_PATH", g0_path), \
                    mock.patch.object(runner, "G0_BASIS_SHA256", config["g0_basis"]["sha256"]), \
                    mock.patch.object(runner, "COLD_BASIS_PATH", cold_path), \
                    mock.patch.object(runner, "COLD_BASIS_SHA256", config["cold_basis"]["sha256"]), \
                    mock.patch.object(runner.subprocess, "run",
                                      return_value=mock.Mock(stdout=config["source_commit"] + "\n")):
                checked = runner.validate_preflight_basis(config)
            self.assertEqual(checked["g0_sha256"], config["g0_basis"]["sha256"])
            self.assertEqual(checked["cold_sha256"], config["cold_basis"]["sha256"])
            self.assertEqual(checked["source_commit"], config["source_commit"])

    def test_head_mismatch_fails_before_loading_apis(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_head_preflight_") as temp:
            root = Path(temp)
            config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
            config = json.loads(config_path.read_text(encoding="utf-8"))
            with mock.patch.object(runner, "G0_BASIS_PATH", Path(config["g0_basis"]["path"])), \
                    mock.patch.object(runner, "G0_BASIS_SHA256", config["g0_basis"]["sha256"]), \
                    mock.patch.object(runner, "COLD_BASIS_PATH", Path(config["cold_basis"]["path"])), \
                    mock.patch.object(runner, "COLD_BASIS_SHA256", config["cold_basis"]["sha256"]), \
                    mock.patch.object(runner.subprocess, "run", return_value=mock.Mock(stdout="b" * 40 + "\n")):
                self._assert_run_preflight_fails(root, config_path, "当前 HEAD 不一致")

    def test_tool_source_path_or_sha_mismatch_fails_before_loading_apis(self):
        for mismatch in ("path", "sha256"):
            with self.subTest(mismatch=mismatch), tempfile.TemporaryDirectory(prefix="s2b_t18_tool_preflight_") as temp:
                root = Path(temp)
                config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
                config = json.loads(config_path.read_text(encoding="utf-8"))
                if mismatch == "path":
                    wrong_path = root / "verification/alternate_jtag.py"
                    wrong_path.write_bytes((ROOT / "verification/s2b_board_jtag.py").read_bytes())
                    config["bindings"]["tool_source"]["path"] = str(wrong_path)
                    message = "正式 JTAG 源文件路径"
                else:
                    config["bindings"]["tool_source"]["sha256"] = "0" * 64
                    message = "SHA-256 不匹配"
                config_path.write_text(json.dumps(config), encoding="utf-8")
                with mock.patch.object(runner, "G0_BASIS_PATH", Path(config["g0_basis"]["path"])), \
                        mock.patch.object(runner, "G0_BASIS_SHA256", config["g0_basis"]["sha256"]), \
                        mock.patch.object(runner, "COLD_BASIS_PATH", Path(config["cold_basis"]["path"])), \
                        mock.patch.object(runner, "COLD_BASIS_SHA256", config["cold_basis"]["sha256"]), \
                        mock.patch.object(runner.subprocess, "run",
                                          return_value=mock.Mock(stdout=config["source_commit"] + "\n")):
                    self._assert_run_preflight_fails(root, config_path, message)

    def test_g0_receipt_rejects_wrong_document_version_or_sha(self):
        cases = (("interface", "version", "physical/9.9"), ("interface", "sha256", "0" * 64),
                 ("uart_interface", "version", "uart/9.9"), ("uart_interface", "sha256", "0" * 64),
                 ("interface", "path", "wrong/path.md"))
        for binding, field, value in cases:
            with self.subTest(field=field), tempfile.TemporaryDirectory(prefix="s2b_t18_g0_doc_binding_") as temp:
                root = Path(temp)
                config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
                config = json.loads(config_path.read_text(encoding="utf-8"))
                self._mutate_pinned_g0_receipt(
                    root, config, lambda receipt: receipt["bindings"][binding].__setitem__(field, value))
                with mock.patch.object(runner, "ROOT", root), \
                        mock.patch.object(runner, "G0_BASIS_PATH", Path(config["g0_basis"]["path"])), \
                        mock.patch.object(runner, "G0_BASIS_SHA256", config["g0_basis"]["sha256"]), \
                        mock.patch.object(runner, "COLD_BASIS_PATH", Path(config["cold_basis"]["path"])), \
                        mock.patch.object(runner, "COLD_BASIS_SHA256", config["cold_basis"]["sha256"]):
                    with self.assertRaisesRegex(runner.RunnerError, "path/version/SHA"):
                        runner.validate_preflight_basis(config)

    def test_g0_and_cold_receipts_reject_unknown_schema_fields(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_receipt_schema_") as temp:
            root = Path(temp)
            config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
            config = json.loads(config_path.read_text(encoding="utf-8"))
            self._mutate_pinned_g0_receipt(root, config, lambda receipt: receipt.__setitem__("unexpected", True))
            with mock.patch.object(runner, "ROOT", root), \
                    mock.patch.object(runner, "G0_BASIS_PATH", Path(config["g0_basis"]["path"])), \
                    mock.patch.object(runner, "G0_BASIS_SHA256", config["g0_basis"]["sha256"]), \
                    mock.patch.object(runner, "COLD_BASIS_PATH", Path(config["cold_basis"]["path"])), \
                    mock.patch.object(runner, "COLD_BASIS_SHA256", config["cold_basis"]["sha256"]):
                with self.assertRaisesRegex(runner.RunnerError, "G0 receipt schema"):
                    runner.validate_preflight_basis(config)
        with tempfile.TemporaryDirectory(prefix="s2b_t18_cold_receipt_schema_") as temp:
            root = Path(temp)
            config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
            config = json.loads(config_path.read_text(encoding="utf-8"))
            cold_path = Path(config["cold_basis"]["path"])
            cold_receipt = json.loads(cold_path.read_text(encoding="utf-8"))
            cold_receipt["unexpected"] = True
            cold_path.write_text(json.dumps(cold_receipt), encoding="utf-8")
            config["cold_basis"]["sha256"] = hashlib.sha256(cold_path.read_bytes()).hexdigest()
            with mock.patch.object(runner, "ROOT", root), \
                    mock.patch.object(runner, "G0_BASIS_PATH", Path(config["g0_basis"]["path"])), \
                    mock.patch.object(runner, "G0_BASIS_SHA256", config["g0_basis"]["sha256"]), \
                    mock.patch.object(runner, "COLD_BASIS_PATH", cold_path), \
                    mock.patch.object(runner, "COLD_BASIS_SHA256", config["cold_basis"]["sha256"]):
                with self.assertRaisesRegex(runner.RunnerError, "冷生命周期 receipt schema"):
                    runner.validate_preflight_basis(config)

    def test_g0_receipt_rejects_xsa_bit_and_build_binding_mismatches(self):
        for name in ("xsa", "bit", "build_details"):
            with self.subTest(binding=name), tempfile.TemporaryDirectory(prefix="s2b_t18_g0_artifact_binding_") as temp:
                root = Path(temp)
                config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
                config = json.loads(config_path.read_text(encoding="utf-8"))
                self._mutate_pinned_g0_receipt(
                    root, config, lambda receipt: receipt["bindings"][name].__setitem__("sha256", "0" * 64))
                with mock.patch.object(runner, "ROOT", root), \
                        mock.patch.object(runner, "G0_BASIS_PATH", Path(config["g0_basis"]["path"])), \
                        mock.patch.object(runner, "G0_BASIS_SHA256", config["g0_basis"]["sha256"]), \
                        mock.patch.object(runner, "COLD_BASIS_PATH", Path(config["cold_basis"]["path"])), \
                        mock.patch.object(runner, "COLD_BASIS_SHA256", config["cold_basis"]["sha256"]):
                    with self.assertRaisesRegex(runner.RunnerError, "path/version/SHA"):
                        runner.validate_preflight_basis(config)

    def test_g0_receipt_rejects_build_details_that_name_different_xsa(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_g0_build_mismatch_") as temp:
            root = Path(temp)
            config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
            config = json.loads(config_path.read_text(encoding="utf-8"))
            build_path = Path(config["build_details"]["path"])
            build = json.loads(build_path.read_text(encoding="utf-8"))
            build["config"]["xsa_sha256"] = "0" * 64
            build_path.write_text(json.dumps(build), encoding="utf-8")
            config["build_details"]["sha256"] = hashlib.sha256(build_path.read_bytes()).hexdigest()
            g0_path = Path(config["g0_basis"]["path"])
            receipt = json.loads(g0_path.read_text(encoding="utf-8"))
            receipt["bindings"]["build_details"] = dict(config["build_details"])
            g0_path.write_text(json.dumps(receipt), encoding="utf-8")
            config["g0_basis"]["sha256"] = hashlib.sha256(g0_path.read_bytes()).hexdigest()
            with mock.patch.object(runner, "ROOT", root), \
                    mock.patch.object(runner, "G0_BASIS_PATH", g0_path), \
                    mock.patch.object(runner, "G0_BASIS_SHA256", config["g0_basis"]["sha256"]), \
                    mock.patch.object(runner, "COLD_BASIS_PATH", Path(config["cold_basis"]["path"])), \
                    mock.patch.object(runner, "COLD_BASIS_SHA256", config["cold_basis"]["sha256"]):
                with self.assertRaisesRegex(runner.RunnerError, "build_details 与当前编译 XSA"):
                    runner.validate_preflight_basis(config)

    def test_g0_receipt_accepts_approved_ancestor_commit_for_current_head(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_g0_receipt_ancestor_") as temp:
            root = Path(temp)
            config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
            config = json.loads(config_path.read_text(encoding="utf-8"))
            approved_commit = config["source_commit"]
            runner.subprocess.run(["git", "commit", "--allow-empty", "-qm", "current config"],
                                  cwd=root, check=True, capture_output=True)
            current_commit = runner.subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                                                   capture_output=True, text=True, encoding="ascii",
                                                   check=True).stdout.strip()
            config["source_commit"] = current_commit
            config_path.write_text(json.dumps(config), encoding="utf-8")
            with mock.patch.object(runner, "ROOT", root), \
                    mock.patch.object(runner, "G0_BASIS_PATH", Path(config["g0_basis"]["path"])), \
                    mock.patch.object(runner, "G0_BASIS_SHA256", config["g0_basis"]["sha256"]), \
                    mock.patch.object(runner, "COLD_BASIS_PATH", Path(config["cold_basis"]["path"])), \
                    mock.patch.object(runner, "COLD_BASIS_SHA256", config["cold_basis"]["sha256"]):
                checked = runner.validate_preflight_basis(config)
            self.assertEqual(checked["source_commit"], current_commit)
            receipt = json.loads(Path(config["g0_basis"]["path"]).read_text(encoding="utf-8"))
            self.assertEqual(receipt["source_commit"], approved_commit)
            self.assertNotEqual(checked["source_commit"], receipt["source_commit"])

    def test_g0_receipt_rejects_unrelated_approved_commit(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_g0_receipt_nonancestor_") as temp:
            root = Path(temp)
            config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
            config = json.loads(config_path.read_text(encoding="utf-8"))
            tree = runner.subprocess.run(["git", "write-tree"], cwd=root, capture_output=True,
                                         text=True, encoding="ascii", check=True).stdout.strip()
            unrelated_commit = runner.subprocess.run(
                ["git", "commit-tree", tree, "-m", "unrelated approval"], cwd=root,
                capture_output=True, text=True, encoding="ascii", check=True).stdout.strip()
            g0_path = Path(config["g0_basis"]["path"])
            receipt = json.loads(g0_path.read_text(encoding="utf-8"))
            receipt["source_commit"] = unrelated_commit
            g0_path.write_text(json.dumps(receipt), encoding="utf-8")
            config["g0_basis"]["sha256"] = hashlib.sha256(g0_path.read_bytes()).hexdigest()
            config_path.write_text(json.dumps(config), encoding="utf-8")
            with mock.patch.object(runner, "ROOT", root), \
                    mock.patch.object(runner, "G0_BASIS_PATH", g0_path), \
                    mock.patch.object(runner, "G0_BASIS_SHA256", config["g0_basis"]["sha256"]), \
                    mock.patch.object(runner, "COLD_BASIS_PATH", Path(config["cold_basis"]["path"])), \
                    mock.patch.object(runner, "COLD_BASIS_SHA256", config["cold_basis"]["sha256"]):
                with self.assertRaisesRegex(runner.RunnerError, "G0 receipt source_commit 不是当前源码基线的祖先"):
                    runner.validate_preflight_basis(config)

    def test_g0_accepts_historical_ancestor_build_for_current_head(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_build_ancestor_") as temp:
            root = Path(temp)
            ancestor, current, _ = self._make_build_lineage(root)
            config = self._make_build_output_config(root, ancestor, current)
            with mock.patch.object(runner, "ROOT", root):
                runner._validate_g0_build_outputs(config)

    def test_g0_rejects_build_commit_outside_current_head_lineage(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_build_nonancestor_") as temp:
            root = Path(temp)
            _, current, unrelated = self._make_build_lineage(root)
            config = self._make_build_output_config(root, unrelated, current)
            with mock.patch.object(runner, "ROOT", root):
                with self.assertRaisesRegex(runner.RunnerError, "不是当前源码基线的祖先"):
                    runner._validate_g0_build_outputs(config)

    @staticmethod
    def _make_build_lineage(root: Path) -> tuple[str, str, str]:
        """建立含祖先提交和独立提交的临时Git历史。"""
        root.mkdir(parents=True, exist_ok=True)

        def git(*args: str) -> str:
            return runner.subprocess.run(["git", *args], cwd=root, capture_output=True,
                                         text=True, encoding="ascii", check=True).stdout.strip()

        git("init", "-q")
        git("config", "user.name", "T18 Test")
        git("config", "user.email", "t18-test@example.invalid")
        git("commit", "--allow-empty", "-qm", "ancestor")
        ancestor = git("rev-parse", "HEAD")
        branch = git("branch", "--show-current")
        git("commit", "--allow-empty", "-qm", "current")
        current = git("rev-parse", "HEAD")
        git("checkout", "--orphan", "unrelated")
        git("commit", "--allow-empty", "-qm", "unrelated")
        unrelated = git("rev-parse", "HEAD")
        git("checkout", branch)
        return ancestor, current, unrelated

    @staticmethod
    def _make_build_output_config(root: Path, build_commit: str, current_commit: str) -> dict:
        """建立只供G0构建输出校验使用的本地绑定。"""
        xsa = {"path": str(root / "artifacts/platform.xsa"), "sha256": "a" * 64}
        app_elf = {"path": str(root / "artifacts/app.elf"), "sha256": "b" * 64}
        init_elf = {"path": str(root / "artifacts/init.elf"), "sha256": "c" * 64}
        build = {
            "status": "PASS_OFFLINE_FULL_XSA_BUILD",
            "hardware_mode": "FULL_PLATFORM_BOUND",
            "source_commit": build_commit,
            "config": {"xsa": xsa["path"], "xsa_sha256": xsa["sha256"]},
            "xsa_sha256": xsa["sha256"],
            "elf": app_elf,
            "initializer_elf": init_elf,
        }
        build_path = root / "artifacts/build_details.json"
        build_path.parent.mkdir(parents=True, exist_ok=True)
        build_path.write_text(json.dumps(build), encoding="utf-8")
        build_binding = {"path": str(build_path),
                         "sha256": hashlib.sha256(build_path.read_bytes()).hexdigest()}
        return {"source_commit": current_commit,
                "build_details": build_binding,
                "bindings": {"xsa": xsa, "app_elf": app_elf, "init_elf": init_elf}}

    def test_cold_receipt_rejects_wrong_controller_system_stop_and_unproven_lifecycle(self):
        cases = (("controller_source_sha256", "0" * 64), ("reset_method", "TCF_SYSTEM_STOP_ONLY"),
                 ("cold_lifecycle_proven", False))
        for field, value in cases:
            with self.subTest(field=field), tempfile.TemporaryDirectory(prefix="s2b_t18_cold_reject_") as temp:
                root = Path(temp)
                config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
                config = json.loads(config_path.read_text(encoding="utf-8"))
                cold_path = Path(config["cold_basis"]["path"])
                receipt = json.loads(cold_path.read_text(encoding="utf-8"))
                receipt[field] = value
                cold_path.write_text(json.dumps(receipt), encoding="utf-8")
                config["cold_basis"]["sha256"] = hashlib.sha256(cold_path.read_bytes()).hexdigest()
                with mock.patch.object(runner, "ROOT", root), \
                        mock.patch.object(runner, "G0_BASIS_PATH", Path(config["g0_basis"]["path"])), \
                        mock.patch.object(runner, "G0_BASIS_SHA256", config["g0_basis"]["sha256"]), \
                        mock.patch.object(runner, "COLD_BASIS_PATH", cold_path), \
                        mock.patch.object(runner, "COLD_BASIS_SHA256", config["cold_basis"]["sha256"]):
                    message = "controller SHA" if field == "controller_source_sha256" else "未证明真实硬复位/POR"
                    with self.assertRaisesRegex(runner.RunnerError, message):
                        runner.validate_preflight_basis(config)

    def test_finalize_manifest_binds_exact_g0_receipt_path_and_sha(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_finalize_g0_") as temp:
            root = Path(temp)
            run_dir = root / "report/evidence/S2B-T18/test_run"
            deploy_dir = root / "report/evidence/S2B-T18/test_deployment"
            run_dir.mkdir(parents=True)
            deploy_dir.mkdir(parents=True)
            manifest_path = run_dir / "delivery_manifest.json"
            manifest_path.write_text(json.dumps({"files": [], "checks": []}), encoding="utf-8")
            (deploy_dir / "orchestrator_calls.jsonl").write_bytes(b"")
            source_path = root / "test_source.py"
            source_path.write_text("test-only / not approval\n", encoding="utf-8")
            bindings = {}
            for name in ("preparation", "build_details", "visibility_proof", "visibility_review",
                         "final_platform_manifest", "final_review", "cold_basis", "g0_basis"):
                path = root / "inputs" / (name + ".json")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("test-only / not approval: " + name + "\n", encoding="utf-8")
                bindings[name] = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            config = {**bindings, "bindings": {}}
            fake_module = type("FakeModule", (), {"__file__": str(source_path)})

            class FakeDelivery:
                __file__ = str(source_path)

                @staticmethod
                def check_manifest(mode, path, root_path):
                    return {"status": "CHECKS_OK", "path": path, "root": root_path}

            apis = type("FakeApis", (), {"acceptance": fake_module, "jtag": fake_module,
                                          "transport": fake_module, "platform": fake_module,
                                          "delivery": FakeDelivery})()
            checked = {"run_dir": run_dir, "deploy_dir": deploy_dir, "preparation": {}}
            record = {"status": "FAILED", "cleanup_steps": [], "cleanup_errors": []}
            with mock.patch.object(runner, "ROOT", root), mock.patch.object(runner, "__file__", str(source_path)):
                result = runner.finalize_evidence(config, checked, apis, b"test-only / not approval", record,
                                                  journal=None, controller=None, wire=None, runtime_objects={})
            self.assertEqual(result["status"], "CHECKS_OK")
            self.assertEqual(manifest_path, run_dir / "delivery_manifest.json")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            expected_path = bindings["g0_basis"]["path"]
            rows = [row for row in manifest["files"] if row["path"] == Path(expected_path).relative_to(root).as_posix()]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["sha256"], bindings["g0_basis"]["sha256"])

    def test_direct_v1_validator_keeps_second_preflight_gate(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_direct_validate_") as temp:
            root = Path(temp)
            config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
            config = {key: None for key in runner.CONFIG_KEYS}
            config.update(json.loads(config_path.read_text(encoding="utf-8")))
            config["schema_version"] = 1
            config["source_commit"] = "0" * 40
            with mock.patch.object(runner, "ROOT", root), \
                    mock.patch.object(runner, "G0_BASIS_PATH", None), \
                    mock.patch.object(runner, "G0_BASIS_SHA256", None), \
                    mock.patch.object(runner.subprocess, "run", side_effect=AssertionError("不得继续")) as git:
                with self.assertRaisesRegex(runner.RunnerError, "尚无独立审查固定的正式回执SHA"):
                    runner.validate_v1_inputs(config, apis=object())
            git.assert_not_called()

    def test_csr_reentry_requires_bound_complete_model_pass_and_same_hardware(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_csr_reentry_") as temp:
            root = Path(temp)
            config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["run_id"] = "csr_current_run"
            run_id = "prior_model_run"
            config["hw_server"] = {"process_id": 41, "executable_path": r"D:\Xilinx\hw_server.exe",
                                   "creation_time_filetime_utc": "100"}
            config["serial"] = {"identity": {"port": "COM8", "name": "USB Serial Device (COM8)",
                                                "pnp_device_id": r"USB\VID_1234&PID_5678",
                                                "config_manager_error_code": 0}}
            evidence = root / "report/evidence/S2B-T18"
            run_dir = evidence / run_id
            deploy = evidence / (run_id + "_deployment")
            run_dir.mkdir(parents=True)
            deploy.mkdir(parents=True)
            prior_config = {"run_id": run_id, "bindings": config["bindings"],
                            "hw_server": config["hw_server"], "serial": config["serial"]}
            config_binding = deploy / "input_config.json"
            config_binding.write_text(json.dumps(prior_config), encoding="utf-8")
            validated = {"server": {"ProcessId": 41, "ExecutablePath": r"D:\Xilinx\hw_server.exe",
                                    "CreationTimeFileTimeUtc": "100"},
                         "listeners": [{"LocalAddress": "127.0.0.1", "LocalPort": 3121, "OwningProcess": 41}],
                         "uart": {"Name": "USB Serial Device (COM8)", "PNPDeviceID": r"USB\VID_1234&PID_5678",
                                  "ConfigManagerErrorCode": 0}}
            result = {"scope": "model", "status": "PASS_MODEL_CORPUS_AND_STRESS_ONLY",
                      "native_exit_code": 0, "run_id": run_id, "cleanup_errors": [],
                      "finished_at_utc8": "2026-10-18T22:00:00+08:00",
                      "acceptance": {"status": "PASS_MODEL_CORPUS_AND_STRESS_ONLY",
                                     "completed_stress": 1000, "completed_corpus": 109},
                      "identity_snapshots": [{"label": label, "validated": validated}
                          for label in ("before_runtime", "after_connect", "before_serial", "after_serial_open")]}
            result_path = run_dir / "orchestrator_result.json"
            result_path.write_text(json.dumps(result), encoding="utf-8")
            targets = {
                "APU": {"target_id": 1, "target_ctx": "apu_ctx", "level": 0, "name": "APU", "parent_ctx": "", "parent": "",
                        "jtag_device_id": 2, "jtag_device_ctx": "dap_ctx", "jtag_device_index": 0, "jtag_device_name": "arm_dap",
                        "jtag_cable_id": 1, "jtag_cable_ctx": "cable_ctx", "jtag_cable_name": "JTAG-HS1",
                        "jtag_cable_manufacturer": "Digilent", "jtag_cable_product": "JTAG-HS1", "jtag_cable_serial": "serial-1"},
                "ARM Cortex-A9 MPCore #0": {"target_id": 2, "target_ctx": "cpu0_ctx", "level": 1,
                        "name": "ARM Cortex-A9 MPCore #0", "parent_ctx": "apu_ctx", "parent": "APU",
                        "jtag_device_id": 2, "jtag_device_ctx": "dap_ctx", "jtag_device_index": 0, "jtag_device_name": "arm_dap",
                        "jtag_cable_id": 1, "jtag_cable_ctx": "cable_ctx", "jtag_cable_name": "JTAG-HS1",
                        "jtag_cable_manufacturer": "Digilent", "jtag_cable_product": "JTAG-HS1", "jtag_cable_serial": "serial-1"},
                "ARM Cortex-A9 MPCore #1": {"target_id": 3, "target_ctx": "cpu1_ctx", "level": 1,
                        "name": "ARM Cortex-A9 MPCore #1", "parent_ctx": "apu_ctx", "parent": "APU",
                        "jtag_device_id": 2, "jtag_device_ctx": "dap_ctx", "jtag_device_index": 0, "jtag_device_name": "arm_dap",
                        "jtag_cable_id": 1, "jtag_cable_ctx": "cable_ctx", "jtag_cable_name": "JTAG-HS1",
                        "jtag_cable_manufacturer": "Digilent", "jtag_cable_product": "JTAG-HS1", "jtag_cable_serial": "serial-1"},
                "xc7z020": {"target_id": 4, "target_ctx": "fpga_ctx", "level": 0, "name": "xc7z020", "parent_ctx": "", "parent": "",
                        "jtag_device_id": 3, "jtag_device_ctx": "fpga_device_ctx", "jtag_device_index": 1, "jtag_device_name": "xc7z020",
                        "jtag_cable_id": 1, "jtag_cable_ctx": "cable_ctx", "jtag_cable_name": "JTAG-HS1",
                        "jtag_cable_manufacturer": "Digilent", "jtag_cable_product": "JTAG-HS1", "jtag_cable_serial": "serial-1"}}
            def call(api, *, repr_value=None, kwargs=None):
                return {"api": api, "status": "RETURNED", "args": ["--target_properties"] if api.endswith("properties") else [],
                        "kwargs": kwargs or {}, "return_repr": repr_value}
            model_calls = [call("session.targets.properties", repr_value=repr({"target_" + str(i): row
                          for i, row in enumerate(targets.values())})),
                           call("cpu0.dow.app", kwargs={"file": prior_config["bindings"]["app_elf"]["path"],
                                                        "auto_stop": True, "set_entry": True}),
                           call("cpu0.con.app"), call("cpu1.state", repr_value="'Stopped: (Suspended)'"),
                           call("cpu0.state", repr_value="'Running'")]
            model_jtag_result = {"status": "API_OBSERVATIONS_SAVED_ACCEPTANCE_PENDING", "cleanup_errors": [],
                                 "bindings": prior_config["bindings"], "calls": model_calls, "targets": targets}
            model_jtag_result_path = deploy / "jtag_result.json"
            model_jtag_result_path.write_text(json.dumps(model_jtag_result), encoding="utf-8")
            model_jtag_calls_path = deploy / "jtag_calls.jsonl"
            model_jtag_calls_path.write_text("".join(json.dumps(row) + "\n" for row in model_calls), encoding="utf-8")
            self.assertEqual(result_path.parent.name, run_id)
            self.assertEqual(config_binding.parent.name, run_id + "_deployment")

            failure_id = "formal_csr_recovery_20261019_r02"
            failure_run_dir = evidence / failure_id
            failure_deploy = evidence / (failure_id + "_deployment")
            failure_run_dir.mkdir()
            failure_deploy.mkdir()
            failure_calls = [call("session.targets.properties", repr_value=repr({"target_" + str(i): row
                             for i, row in enumerate(targets.values())})),
                             call("cpu1.state", repr_value="'Stopped: (Suspended)'"),
                             call("cpu0.state", repr_value="'Running'")]
            failure_jtag_result = {"status": "FAILED", "error": "JtagError('CPU0未停止')",
                                   "cleanup_errors": [], "bindings": prior_config["bindings"],
                                   "calls": failure_calls}
            failure_jtag_result_path = failure_deploy / "jtag_result.json"
            failure_jtag_result_path.write_text(json.dumps(failure_jtag_result), encoding="utf-8")
            failure_jtag_calls_path = failure_deploy / "jtag_calls.jsonl"
            failure_jtag_calls_path.write_text("".join(json.dumps(row) + "\n" for row in failure_calls), encoding="utf-8")
            failure_orchestrator_calls_path = failure_deploy / "orchestrator_calls.jsonl"
            failure_orchestrator_calls_path.write_text(json.dumps({"step": "board_flow", "status": "FAILED",
                "uart_tx_count": 0, "exception": "RunnerError('CPU0未停止')"}) + "\n", encoding="utf-8")
            failure_result_path = failure_run_dir / "orchestrator_result.json"
            failure_result_path.write_text(json.dumps({"run_id": failure_id, "scope": "csr", "status": "FAILED",
                "native_exit_code": 2, "started_at_utc8": "2026-10-19T10:00:00+08:00",
                "traceback": "RunnerError: CPU0未停止", "identity_snapshots": [
                    {"label": "before_runtime", "validated": validated}]}), encoding="utf-8")

            def bind(path):
                return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

            binding = {"model_result": bind(result_path), "model_input_config": bind(config_binding),
                       "model_jtag_result": bind(model_jtag_result_path), "model_jtag_calls": bind(model_jtag_calls_path),
                       "prior_csr_result": bind(failure_result_path),
                       "prior_csr_jtag_result": bind(failure_jtag_result_path),
                       "prior_csr_jtag_calls": bind(failure_jtag_calls_path),
                       "prior_csr_orchestrator_calls": bind(failure_orchestrator_calls_path)}
            config["csr_reentry"] = binding
            with mock.patch.object(runner, "ROOT", root), \
                    mock.patch.object(runner, "EVIDENCE_PARENT", evidence):
                checked = runner.validate_csr_reentry(config, scope="csr")
                self.assertEqual(checked["model_run_id"], run_id)
                self.assertEqual(checked["artifact_bindings"]["app_elf"], config["bindings"]["app_elf"])
                self.assertEqual(checked["prior_csr_failure"]["run_id"], failure_id)
                with self.assertRaisesRegex(runner.RunnerError, "model scope禁止"):
                    runner.validate_csr_reentry(config, scope="model")

                for field, value, message in (("native_exit_code", 2, "完整PASS"),
                                              ("cleanup_errors", [{"step": "x"}], "完整PASS"),
                                              ("acceptance", {"status": "PASS_MODEL_CORPUS_AND_STRESS_ONLY",
                                                               "completed_stress": 999,
                                                               "completed_corpus": 109}, "1000次压力")):
                    mutated = dict(result, **{field: value})
                    result_path.write_text(json.dumps(mutated), encoding="utf-8")
                    bad = dict(binding, model_result=bind(result_path))
                    with self.assertRaisesRegex(runner.RunnerError, message):
                        runner.validate_csr_reentry(dict(config, csr_reentry=bad), scope="csr")
                result_path.write_text(json.dumps(result), encoding="utf-8")
                bad = dict(config, csr_reentry={**binding, "model_result": dict(binding["model_result"], sha256="0" * 64)})
                with self.assertRaisesRegex(runner.RunnerError, "SHA-256"):
                    runner.validate_csr_reentry(bad, scope="csr")
                changed_artifact = json.loads(config_binding.read_text(encoding="utf-8"))
                changed_artifact["bindings"]["app_elf"] = {"path": "other.elf", "sha256": "f" * 64}
                config_binding.write_text(json.dumps(changed_artifact), encoding="utf-8")
                bad = dict(binding, model_input_config=bind(config_binding))
                with self.assertRaisesRegex(runner.RunnerError, "app_elf"):
                    runner.validate_csr_reentry(dict(config, csr_reentry=bad), scope="csr")
                config_binding.write_text(json.dumps(prior_config), encoding="utf-8")
                wrong_config_path = run_dir / "input_config.json"
                wrong_config_path.write_bytes(config_binding.read_bytes())
                bad = dict(binding, model_input_config=bind(wrong_config_path))
                with self.assertRaisesRegex(runner.RunnerError, "相邻run/deployment目录"):
                    runner.validate_csr_reentry(dict(config, csr_reentry=bad), scope="csr")
                for changed, message in ((dict(config, hw_server={**config["hw_server"], "process_id": 42}),
                                          "hw_server/COM身份"),
                                         (dict(config, serial={"identity": {**config["serial"]["identity"],
                                                                             "port": "COM9"}}),
                                          "hw_server/COM身份")):
                    with self.assertRaisesRegex(runner.RunnerError, message):
                        runner.validate_csr_reentry(dict(changed, csr_reentry=binding), scope="csr")
                changed_calls = model_calls + [call("apu.rst.system.stop", kwargs={"type": "system"})]
                model_jtag_calls_path.write_text("".join(json.dumps(row) + "\n" for row in changed_calls), encoding="utf-8")
                bad = dict(config, csr_reentry=dict(binding, model_jtag_calls=bind(model_jtag_calls_path)))
                with self.assertRaisesRegex(runner.RunnerError, "jtag_calls与jtag_result.calls不一致"):
                    runner.validate_csr_reentry(bad, scope="csr")
                model_jtag_calls_path.write_text("".join(json.dumps(row) + "\n" for row in model_calls), encoding="utf-8")
                bad_model_calls = list(model_calls)
                bad_model_calls[1], bad_model_calls[2] = bad_model_calls[2], bad_model_calls[1]
                model_jtag_result["calls"] = bad_model_calls
                model_jtag_result_path.write_text(json.dumps(model_jtag_result), encoding="utf-8")
                model_jtag_calls_path.write_text("".join(json.dumps(row) + "\n" for row in bad_model_calls), encoding="utf-8")
                bad = dict(config, csr_reentry=dict(binding,
                    model_jtag_result=bind(model_jtag_result_path), model_jtag_calls=bind(model_jtag_calls_path)))
                with self.assertRaisesRegex(runner.RunnerError, "app下载与continue"):
                    runner.validate_csr_reentry(bad, scope="csr")
                model_jtag_result["calls"] = model_calls
                model_jtag_result_path.write_text(json.dumps(model_jtag_result), encoding="utf-8")
                model_jtag_calls_path.write_text("".join(json.dumps(row) + "\n" for row in model_calls), encoding="utf-8")

                changed_targets = json.loads(json.dumps(targets))
                changed_targets["ARM Cortex-A9 MPCore #0"]["jtag_cable_serial"] = "other-board"
                failure_calls[0]["return_repr"] = repr({"target_" + str(i): row
                    for i, row in enumerate(changed_targets.values())})
                failure_jtag_result["calls"] = failure_calls
                failure_jtag_result_path.write_text(json.dumps(failure_jtag_result), encoding="utf-8")
                failure_jtag_calls_path.write_text("".join(json.dumps(row) + "\n" for row in failure_calls), encoding="utf-8")
                bad = dict(config, csr_reentry=dict(binding, prior_csr_jtag_result=bind(failure_jtag_result_path),
                                                     prior_csr_jtag_calls=bind(failure_jtag_calls_path)))
                with self.assertRaisesRegex(runner.RunnerError, "JTAG目标链身份缺失或不一致"):
                    runner.validate_csr_reentry(bad, scope="csr")
                failure_calls[0]["return_repr"] = repr({"target_" + str(i): row
                    for i, row in enumerate(targets.values())})
                failure_jtag_result["calls"] = failure_calls
                failure_jtag_result_path.write_text(json.dumps(failure_jtag_result), encoding="utf-8")
                failure_jtag_calls_path.write_text("".join(json.dumps(row) + "\n" for row in failure_calls), encoding="utf-8")

                mutating_calls = failure_calls + [call("apu.rst.system.stop", kwargs={"type": "system"})]
                failure_jtag_result["calls"] = mutating_calls
                failure_jtag_result_path.write_text(json.dumps(failure_jtag_result), encoding="utf-8")
                failure_jtag_calls_path.write_text("".join(json.dumps(row) + "\n" for row in mutating_calls), encoding="utf-8")
                bad = dict(config, csr_reentry=dict(binding, prior_csr_jtag_result=bind(failure_jtag_result_path),
                                                     prior_csr_jtag_calls=bind(failure_jtag_calls_path)))
                with self.assertRaisesRegex(runner.RunnerError, "可能改变板卡状态"):
                    runner.validate_csr_reentry(bad, scope="csr")

    def test_csr_missing_reentry_binding_fails_before_hardware_setup(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_csr_missing_binding_") as temp:
            root = Path(temp)
            config_dir = root / "report/evidence/S2B-T18/test_run"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "runner_config.json"
            config_path.write_text("{}", encoding="utf-8")
            runtime_spy = mock.Mock()
            with mock.patch.object(runner, "ROOT", root), \
                    mock.patch.object(runner, "validate_preflight_basis"), \
                    mock.patch.object(runner, "load_pinned_csr_map_helper",
                                      side_effect=AssertionError("不得继续预检")) as load_helper, \
                    mock.patch.object(runner, "load_apis",
                                      side_effect=AssertionError("不得导入API")) as load_apis:
                with self.assertRaisesRegex(runner.RunnerError, "精确绑定前序模型与R02失败证据"):
                    runner.run(config_path, runtime=runtime_spy, scope="csr")
            load_helper.assert_not_called()
            load_apis.assert_not_called()
            runtime_spy.identity.assert_not_called()
            runtime_spy.modules.assert_not_called()
            runtime_spy.session.assert_not_called()
            runtime_spy.serial.assert_not_called()

    def test_csr_reentry_records_cpu0_stop_before_existing_deploy_flow(self):
        from verification import s2b_csr_board_acceptance as csr_validator
        trace = []
        csr_snapshot = {offset: 0 for offset in csr_validator.OFFSETS}
        csr_snapshot.update({0: 0x53324250, 4: 0x100, 0x00C: 0x400,
                             0x030: 0x10000000, 0x034: 0x02000000, 0x038: 0x01000000,
                             0x03C: 0x01ADADB8, 0x040: 0x01A46100, 0x044: 5070,
                             0x048: 0x01AD5E80, 0x04C: 20280})
        names = ("APU", "ARM Cortex-A9 MPCore #0", "ARM Cortex-A9 MPCore #1", "xc7z020")
        identity = {}
        for index, name in enumerate(names):
            identity[name] = {"target_id": index + 1, "target_ctx": "ctx_" + str(index),
                              "level": 0 if index in (0, 3) else 1, "name": name,
                              "parent_ctx": "" if index in (0, 3) else "ctx_0",
                              "parent": "" if index in (0, 3) else "APU",
                              "jtag_device_id": 2 if index < 3 else 3,
                              "jtag_device_ctx": "dap_ctx" if index < 3 else "fpga_ctx",
                              "jtag_device_index": 0 if index < 3 else 1,
                              "jtag_device_name": "arm_dap" if index < 3 else "xc7z020",
                              "jtag_cable_id": 1, "jtag_cable_ctx": "cable_ctx",
                              "jtag_cable_name": "JTAG-HS1", "jtag_cable_manufacturer": "Digilent",
                              "jtag_cable_product": "JTAG-HS1", "jtag_cable_serial": "serial-1"}
        app_bytes = bytes(range(1, 21))
        execution = {"pc": 0x100000, "cpsr": 0}

        class Target:
            def __init__(self, name):
                self.name = name

            def stop(self):
                trace.append("cpu0_stop_api")
                state["cpu0"] = "Stopped (Suspended)"

            def rrd(self, *_args, **_kwargs):
                return {"cpsr": execution["cpsr"]}

        state = {"cpu0": "Running", "cpu1": "Stopped (Suspended)"}

        class Controller(FakeController):
            def __init__(self):
                super().__init__(trace)
                self.record = {"calls": []}
                self.session = type("Session", (), {"targets": lambda *_args, **_kwargs: {"cpu0": "cpu0"}})()
                self.targets = {"cpu0": Target("cpu0")}

            def call(self, name, function, *args, **kwargs):
                trace.append(name)
                result = ({"target_" + str(index): row for index, row in enumerate(identity.values())}
                          if name == "session.targets.properties.csr_reentry" else
                          function(*args, **kwargs) if callable(function) else None)
                self.record["calls"].append({"api": name, "status": "RETURNED"})
                return result

            def refresh_targets(self, rows):
                trace.append("refresh_targets")

            def gate(self, *, both=True):
                trace.append("gate_both" if both else "gate_cpu1_only")
                runner.require(state["cpu1"].startswith("Stopped"), "mock CPU1 running")

            def state(self, label):
                trace.append("state_" + label)
                return state[label]

            def pc(self, label):
                trace.append("pc_" + label)
                return execution["pc"]

            def words(self, address, count):
                trace.append("words_" + str(address) + "_" + str(count))
                offset = address - 0x100000
                raw = app_bytes[offset:offset + count * 4]
                return [int.from_bytes(raw[index:index + 4], "little")
                        for index in range(0, len(raw), 4)]

            def guarded(self, function):
                return function()

            def select_and_gate(self):
                trace.append("select_and_gate")

            def stable_csr(self, label):
                trace.append(label)
                return dict(csr_snapshot)

        class Jtag:
            @staticmethod
            def validate_targets(rows):
                trace.append("validate_target_chain")
                return identity

        class ElfParser:
            @staticmethod
            def parse_elf(raw):
                assert raw == app_bytes
                return {"programs": [{"type": 1, "flags": 5, "virtual": 0x100000,
                                      "offset": 0, "file_size": len(raw), "memory_size": len(raw)}],
                        "sections": [{"name": ".text", "type": 1, "flags": 6,
                                      "address": 0x100000, "offset": 0, "size": len(raw)}]}

        class CsrFlow:
            csr = csr_validator

            @staticmethod
            def execute(*_args):
                trace.append("csr_execute")
                return {"status": "PASS_CSR_RECOVERY_SCOPE_ONLY"}

        class Apis:
            jtag = Jtag
            elf_parser = ElfParser
            acceptance = FakeAcceptance(trace, FakeWire(trace))
            csr_flow = CsrFlow

        reentry = {"model_run_id": "formal_model_r02",
                   "model_result": {"path": "result.json", "sha256": "a" * 64},
                   "model_input_config": {"path": "input_config.json", "sha256": "b" * 64},
                   "model_jtag_result": {"path": "jtag_result.json", "sha256": "c" * 64},
                   "model_jtag_calls": {"path": "jtag_calls.jsonl", "sha256": "d" * 64},
                   "model_target_identity": json.loads(json.dumps(identity)),
                   "prior_csr_failure": {"run_id": "formal_csr_recovery_20261019_r02",
                                         "target_identity": json.loads(json.dumps(identity))},
                   "artifact_bindings": {name: {"path": name, "sha256": "e" * 64}
                                         for name in ("app_elf", "bit", "xsa")}}
        checked = self.checked()
        checked["csr_reentry"] = reentry
        controller = Controller()
        wire = FakeWire(trace)
        original_verify_binding = runner.verify_binding
        def verify_app(binding, label, **kwargs):
            if label == "CSR重入绑定应用ELF":
                return Path("app.elf"), app_bytes
            return original_verify_binding(binding, label, **kwargs)
        with mock.patch.object(runner, "verify_binding", side_effect=verify_app):
            result = runner.execute_board_flow(controller, wire, self.config(), checked, Apis,
                                               scope="csr")
        self.assertEqual(result["status"], "PASS_CSR_RECOVERY_SCOPE_ONLY")
        self.assertLess(trace.index("gate_cpu1_only"), trace.index("cpu0.stop.csr_reentry"))
        self.assertLess(trace.index("validate_target_chain"), trace.index("cpu0.stop.csr_reentry"))
        self.assertLess(trace.index("cpu0.rrd.cpsr.csr_reentry"), trace.index("cpu0.stop.csr_reentry"))
        self.assertLess(trace.index("pc_cpu0"), trace.index("cpu0.stop.csr_reentry"))
        self.assertLess(trace.index("words_1048576_4"), trace.index("cpu0.stop.csr_reentry"))
        self.assertLess(trace.index("cpu0.stop.csr_reentry"), trace.index("select_and_gate"))
        self.assertLess(trace.index("select_and_gate"), trace.index("system_reset_stop"))
        self.assertLess(trace.index("system_reset_stop"), trace.index("csr_execute"))
        self.assertEqual(controller.record["csr_reentry"]["before_cpu0"], "Running")
        self.assertEqual(controller.record["csr_reentry"]["after_cpu0"], "Stopped (Suspended)")
        self.assertEqual(controller.record["csr_reentry"]["model_run_id"], "formal_model_r02")
        self.assertEqual(controller.record["csr_reentry"]["current_app_pc"]["verification"],
                         "MATCH_EXECUTABLE_LOAD_AND_SECTION")
        self.assertEqual(controller.record["csr_reentry"]["current_app_pc"]["instruction_bytes"], 16)
        self.assertFalse(controller.record["csr_reentry"]["current_app_pc"]["thumb_state"])
        self.assertIn("无法从本机日志全面证明", controller.record["csr_reentry"]["continuity_limit"])

        trace.clear()
        state.update(cpu0="Running", cpu1="Stopped (Suspended)")
        execution.update(pc=0x100002, cpsr=1 << 5)
        thumb_controller = Controller()
        with mock.patch.object(runner, "verify_binding", side_effect=verify_app):
            thumb_result = runner.execute_board_flow(thumb_controller, FakeWire(trace), self.config(), checked,
                                                     Apis, scope="csr")
        self.assertEqual(thumb_result["status"], "PASS_CSR_RECOVERY_SCOPE_ONLY")
        self.assertIn("words_1048576_5", trace)
        self.assertEqual(thumb_controller.record["csr_reentry"]["current_app_pc"]["readback_alignment_offset"], 2)
        self.assertTrue(thumb_controller.record["csr_reentry"]["current_app_pc"]["thumb_state"])

        trace.clear()
        state.update(cpu0="Stopped (Suspended)", cpu1="Stopped (Suspended)")
        execution.update(pc=0x100000, cpsr=0)
        stopped_controller = Controller()
        with mock.patch.object(runner, "verify_binding", side_effect=verify_app):
            stopped_result = runner.execute_board_flow(stopped_controller, FakeWire(trace), self.config(), checked,
                                                       Apis, scope="csr")
        self.assertEqual(stopped_result["status"], "PASS_CSR_RECOVERY_SCOPE_ONLY")
        self.assertEqual(stopped_controller.record["csr_reentry"]["stop_status"], "ALREADY_STOPPED")
        self.assertIsNone(stopped_controller.record["csr_reentry"]["stop_call_index"])
        self.assertNotIn("cpu0_stop_api", trace)
        self.assertLess(trace.index("words_1048576_4"), trace.index("select_and_gate"))
        self.assertLess(trace.index("select_and_gate"), trace.index("system_reset_stop"))

        class MapHelper:
            @staticmethod
            def register_csr_debug_map(*_args):
                trace.append("csr_map_register")

        initial_csr = dict(csr_snapshot)
        for field, value, allowed in ((0x00C, 0xE04, True), (0x00C, 0x4400, False),
                                      (0x00C, 0x1400, False), (0x068, 1, False),
                                      (0x074, 0x20, False)):
            with self.subTest(old_csr_field=field, value=value):
                trace.clear()
                csr_snapshot.clear(); csr_snapshot.update(initial_csr)
                csr_snapshot[field] = value
                state.update(cpu0="Stopped (Suspended)", cpu1="Stopped (Suspended)")
                current = Controller()
                with mock.patch.object(runner, "verify_binding", side_effect=verify_app):
                    if allowed:
                        runner.execute_board_flow(current, FakeWire(trace), self.config(), checked, Apis,
                            scope="csr", csr_map=(MapHelper, {}, {}, object(), {}))
                        self.assertLess(trace.index("csr_map_register"),
                                        trace.index("csr_reentry.before_system_reset"))
                        self.assertLess(trace.index("csr_reentry.before_system_reset"),
                                        trace.index("system_reset_stop"))
                    else:
                        with self.assertRaises((runner.RunnerError, csr_validator.CsrAcceptanceError)):
                            runner.execute_board_flow(current, FakeWire(trace), self.config(), checked, Apis,
                                scope="csr", csr_map=(MapHelper, {}, {}, object(), {}))
                        self.assertNotIn("system_reset_stop", trace)
        csr_snapshot.clear(); csr_snapshot.update(initial_csr)

        trace.clear()
        state.update(cpu0="Running", cpu1="Stopped (Suspended)")
        identity["ARM Cortex-A9 MPCore #0"]["jtag_cable_serial"] = "different-live-chain"
        mismatch_controller = Controller()
        with mock.patch.object(runner, "verify_binding", side_effect=verify_app):
            with self.assertRaisesRegex(runner.RunnerError, "身份缺失或不一致"):
                runner.execute_board_flow(mismatch_controller, FakeWire(trace), self.config(), checked,
                                          Apis, scope="csr")
        self.assertNotIn("cpu0_stop_api", trace)
        self.assertNotIn("cpu0.stop.csr_reentry", trace)

    def test_csr_reentry_live_chain_and_pc_instruction_are_fail_closed(self):
        raw = bytes(range(20))
        elf = {"programs": [{"type": 1, "flags": 5, "virtual": 0x1000, "offset": 0,
                             "file_size": 20, "memory_size": 20}],
               "sections": [{"name": ".text", "type": 1, "flags": 6, "address": 0x1000,
                             "offset": 0, "size": 20}]}
        valid = runner._validate_app_pc_instructions(elf, raw, 0x1000, 0, raw[:16])
        self.assertEqual(valid["instruction_bytes_sha256"], hashlib.sha256(raw[:16]).hexdigest())
        thumb = runner._validate_app_pc_instructions(elf, raw, 0x1002, 1 << 5, raw[2:18])
        self.assertTrue(thumb["thumb_state"])
        with self.assertRaisesRegex(runner.RunnerError, "不在唯一"):
            runner._validate_app_pc_instructions(elf, raw, 0x2000, 0, raw[:16])
        with self.assertRaisesRegex(runner.RunnerError, "不一致"):
            runner._validate_app_pc_instructions(elf, raw, 0x1000, 0,
                                                 bytes([raw[0] ^ 1]) + raw[1:16])
        with self.assertRaisesRegex(runner.RunnerError, "对齐不符"):
            runner._validate_app_pc_instructions(elf, raw, 0x1002, 0, raw[2:18])
        identity = {"CPU0": {"target_id": 1, "target_ctx": "cpu0", "level": 1, "name": "CPU0",
                             "parent_ctx": "apu", "parent": "APU", "jtag_device_id": 1,
                             "jtag_device_ctx": "dap", "jtag_device_index": 0,
                             "jtag_device_name": "arm_dap", "jtag_cable_id": 1,
                             "jtag_cable_ctx": "cable", "jtag_cable_name": "JTAG-HS1",
                             "jtag_cable_manufacturer": "Digilent", "jtag_cable_product": "HS1",
                             "jtag_cable_serial": "serial"}}
        changed = json.loads(json.dumps(identity))
        changed["CPU0"]["target_id"] = 2
        with self.assertRaisesRegex(runner.RunnerError, "身份缺失或不一致"):
            runner._same_jtag_target_identity(identity, changed)
        missing = json.loads(json.dumps(identity))
        del missing["CPU0"]["jtag_cable_serial"]
        with self.assertRaisesRegex(runner.RunnerError, "身份缺失"):
            runner._same_jtag_target_identity(missing, missing)

    def test_t16_controller_source_sha_boundary_is_preserved(self):
        runner.validate_controller_source_pin({"path": "synthetic-test-source", "sha256": runner.JTAG_SOURCE_SHA256})
        with self.assertRaisesRegex(runner.RunnerError, "T16 JTAG controller"):
            runner.validate_controller_source_pin({"path": "synthetic-test-source", "sha256": "0" * 64})

    @staticmethod
    def _make_preflight_tree(root: Path, *, physical: str, uart: str) -> Path:
        root.mkdir(parents=True, exist_ok=True)
        runner.subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
        runner.subprocess.run(["git", "config", "user.name", "T18 Test"], cwd=root, check=True, capture_output=True)
        runner.subprocess.run(["git", "config", "user.email", "t18-test@example.invalid"], cwd=root,
                              check=True, capture_output=True)
        runner.subprocess.run(["git", "commit", "--allow-empty", "-qm", "test baseline"], cwd=root,
                              check=True, capture_output=True)
        docs = root / "docs/obsidian-project/02-方案设计"
        docs.mkdir(parents=True)
        physical_path = docs / "s2b_physical_interface_candidate.md"
        uart_path = docs / "s2b_board_transport.md"
        physical_path.write_text("test-only / not approval: 状态：" + physical + "；版本：s2b-physical/1.0.0\n", encoding="utf-8")
        uart_path.write_text("test-only / not approval: 状态：" + uart + "；版本：s2bu/1.1\n", encoding="utf-8")
        source_commit = runner.subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                                              capture_output=True, text=True, encoding="ascii",
                                              check=True).stdout.strip()

        def fixture(path: Path, label: str) -> dict:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(("test-only / not approval: " + label + "\n").encode("utf-8"))
            return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

        def bind_existing(path: Path) -> dict:
            return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

        tool_source_path = root / "verification/s2b_board_jtag.py"
        tool_source_path.parent.mkdir(parents=True, exist_ok=True)
        tool_source_path.write_bytes((ROOT / "verification/s2b_board_jtag.py").read_bytes())

        bindings = {
            "interface": bind_existing(physical_path),
            "uart_interface": bind_existing(uart_path),
            "tool_source": bind_existing(tool_source_path),
            "xsa": fixture(root / "artifacts/full_platform.xsa", "XSA"),
            "bit": fixture(root / "artifacts/full_platform.bit", "bitstream"),
            "app_elf": fixture(root / "artifacts/inference.elf", "application ELF"),
            "init_elf": fixture(root / "artifacts/init.elf", "initializer ELF"),
        }
        top_bindings = {
            name: fixture(root / "artifacts" / (name + ".json"), name)
            for name in ("preparation", "visibility_proof", "visibility_review", "final_platform_manifest", "final_review")
        }
        build = {
            "status": "PASS_OFFLINE_FULL_XSA_BUILD", "hardware_mode": "FULL_PLATFORM_BOUND",
            "source_commit": source_commit,
            "config": {"xsa": bindings["xsa"]["path"], "xsa_sha256": bindings["xsa"]["sha256"]},
            "xsa_sha256": bindings["xsa"]["sha256"],
            "elf": dict(bindings["app_elf"]), "initializer_elf": dict(bindings["init_elf"]),
        }
        build_path = root / "artifacts/build_details.json"
        build_path.write_text(json.dumps(build), encoding="utf-8")
        build_binding = {"path": str(build_path), "sha256": hashlib.sha256(build_path.read_bytes()).hexdigest()}
        g0_path = root / "synthetic_g0_pin_not_approval.json"
        cold_path = root / "synthetic_cold_pin_not_approval.json"
        evidence_path = root / "report/evidence/S2B-T16/test_only_por_evidence.json"
        evidence = fixture(evidence_path, "synthetic physical POR evidence")
        versions = {"interface": "s2b-physical/1.0.0", "uart_interface": "s2bu/1.1"}
        current_bindings = {"interface": {**bindings["interface"], "version": versions["interface"]},
                            "uart_interface": {**bindings["uart_interface"], "version": versions["uart_interface"]},
                            "preparation": top_bindings["preparation"], "build_details": build_binding,
                            "xsa": bindings["xsa"], "bit": bindings["bit"], "app_elf": bindings["app_elf"],
                            "init_elf": bindings["init_elf"], "visibility_proof": top_bindings["visibility_proof"],
                            "visibility_review": top_bindings["visibility_review"],
                            "final_platform_manifest": top_bindings["final_platform_manifest"],
                            "final_review": top_bindings["final_review"]}
        deadlines = {"core_timeout": 0xFFFFFFFF, "drain_timeout": 0xFFFFFFFF,
                     "response_timeout_seconds": 450}
        g0_receipt = {"schema_version": 1, "status": "PASS", "role": "INDEPENDENT_REVIEWER",
                      "scope": "S2B_T18_G0_APPROVAL", "source_commit": source_commit,
                      "interface_versions": versions, "bindings": current_bindings,
                      "deadline_profile": deadlines}
        cold_receipt = {"schema_version": 1, "status": "PASS", "role": "INDEPENDENT_REVIEWER",
                        "scope": "S2B_T18_UNIFIED_COLD_LIFECYCLE",
                        "controller_source_sha256": runner.COLD_RECEIPT_CONTROLLER_SHA256,
                        "reset_method": "PHYSICAL_POR", "evidence_kind": "PHYSICAL_HARD_RESET_POR",
                        "hard_reset_proven": True, "cold_lifecycle_proven": True, "evidence": evidence}
        g0_path.write_text(json.dumps(g0_receipt), encoding="utf-8")
        cold_path.write_text(json.dumps(cold_receipt), encoding="utf-8")
        config = {
            "schema_version": 1, "source_commit": source_commit, "bindings": bindings,
            **top_bindings, "build_details": build_binding, **deadlines,
            "g0_basis": {"path": str(g0_path), "sha256": hashlib.sha256(g0_path.read_bytes()).hexdigest()},
            "cold_basis": {"path": str(cold_path), "sha256": hashlib.sha256(cold_path.read_bytes()).hexdigest()},
        }
        config_dir = root / "report/evidence/S2B-T18/test_run"
        config_dir.mkdir(parents=True)
        config_path = config_dir / "runner_config.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        return config_path

    @staticmethod
    def _mutate_pinned_g0_receipt(root: Path, config: dict, mutate) -> None:
        g0_path = Path(config["g0_basis"]["path"])
        receipt = json.loads(g0_path.read_text(encoding="utf-8"))
        mutate(receipt)
        g0_path.write_text(json.dumps(receipt), encoding="utf-8")
        config["g0_basis"]["sha256"] = hashlib.sha256(g0_path.read_bytes()).hexdigest()

    def _assert_run_preflight_fails(self, root: Path, config_path: Path, message: str) -> None:
        runtime_spy = mock.Mock()
        with mock.patch.object(runner, "ROOT", root), \
                mock.patch.object(runner, "load_apis", side_effect=AssertionError("不得导入API")) as load_apis, \
                mock.patch.object(runner, "ProductionRuntime", side_effect=AssertionError("不得初始化runtime")) as runtime, \
                mock.patch.object(runner, "collect_system_identity", side_effect=AssertionError("不得探测设备")) as identity:
            with self.assertRaisesRegex(runner.RunnerError, message):
                runner.run(config_path, runtime=runtime_spy)
        load_apis.assert_not_called()
        runtime.assert_not_called()
        identity.assert_not_called()
        runtime_spy.identity.assert_not_called()
        runtime_spy.modules.assert_not_called()
        runtime_spy.session.assert_not_called()
        runtime_spy.serial.assert_not_called()

    def test_execute_flow_registers_csr_map_after_reset_before_deploy(self):
        trace = []
        wire = FakeWire(trace)
        controller = FakeController(trace)
        acceptance = FakeAcceptance(trace, wire)

        class MapHelper:
            @staticmethod
            def register_csr_debug_map(config, record, journal, session, controller, owner):
                trace.append("csr_map_register")
                record["debug_memory_map"] = {"status": "REGISTERED_CSR_ONLY"}

        map_record = {"verified_inputs": {"compat_artifacts": {"implemented_xsa": {"path": "xsa", "sha256": "a" * 64}}}}
        result = runner.execute_board_flow(
            controller, wire, self.config(), self.checked(), FakeApis(acceptance),
            csr_map=(MapHelper, {}, map_record, object(), {}))
        self.assertEqual(result["status"], "PASS_MODEL_CORPUS_AND_STRESS_ONLY")
        self.assertLess(trace.index("system_reset_stop"), trace.index("csr_map_register"))
        self.assertLess(trace.index("csr_map_register"), trace.index("download_init"))

    def test_real_r04_helper_registers_and_cleans_csr_map_after_partial_failure(self):
        helper, source = runner.load_pinned_csr_map_helper()
        helper_path = ROOT / "vitis/run_s2b_visibility_probe.py"
        self.assertEqual(source, {"path": str(helper_path), "sha256": runner.CSR_MAP_HELPER_SOURCE_SHA256})
        self.assertEqual(hashlib.sha256(helper_path.read_bytes()).hexdigest(), runner.CSR_MAP_HELPER_SOURCE_SHA256)
        qualification_config = json.loads(
            (ROOT / "report/evidence/S2B-T19/single_sample_qualification_20261018_r02/input_config.json")
            .read_text(encoding="utf-8"))
        xsa_binding = qualification_config["bindings"]["xsa"]

        class FakeTarget:
            def __init__(self, session, *, fail_load=False):
                self._name = "APU"
                self._ctx = "target-apu"
                self._id = 1
                self.session = session
                self.fail_load = fail_load

            def loadhw(self, *, hw, mem_ranges):
                self.session._designtable[os.path.realpath(hw)] = {
                    "targets": [self._ctx], "channels": [self.session._curchan]}
                self.session._memmap_ctxs[self.session._curchan] = {self._ctx: {"csr": {
                    "base": 0x43C00000, "size": 0x10000, "high": 0x43C0FFFF,
                    "type": "REGISTER", "flags": 3}}}
                self.session._memmaptable[self.session._curchan] = {self._ctx: {"csr": [{
                    "Addr": 0x43C00000, "Size": 0x10000, "Flags": 3}]}}
                if self.fail_load:
                    raise OSError("mock partial loadhw failure")

            def unloadhw(self):
                self.session._designtable.clear()
                self.session._memmap_ctxs.clear()
                self.session._memmaptable.clear()

        class FakeSession:
            def __init__(self, *, fail_load=False):
                self._curchan = "mock-channel"
                self._designtable = {}
                self._memmap_ctxs = {}
                self._memmaptable = {}
                self._curtarget = None
                self.properties = {}
                self.apu = FakeTarget(self, fail_load=fail_load)
                self._curtarget = self.apu

            def targets(self, *args, **kwargs):
                if "id" in kwargs:
                    return self.apu
                return self.properties

        def target_rows():
            common = {"jtag_cable_manufacturer": "Digilent", "jtag_cable_product": "JTAG-HS1",
                      "jtag_cable_serial": "210512180081", "jtag_cable_ctx": "cable"}
            rows = [
                {**common, "target_id": 1, "target_ctx": "target-apu", "name": "APU",
                 "parent_ctx": "", "parent": "", "jtag_device_ctx": "device-apu",
                 "jtag_device_name": "arm_dap"},
                {**common, "target_id": 2, "target_ctx": "target-cpu0", "name": "ARM Cortex-A9 MPCore #0",
                 "parent_ctx": "target-apu", "parent": "APU", "jtag_device_ctx": "device-apu",
                 "jtag_device_name": "arm_dap"},
                {**common, "target_id": 3, "target_ctx": "target-cpu1", "name": "ARM Cortex-A9 MPCore #1",
                 "parent_ctx": "target-apu", "parent": "APU", "jtag_device_ctx": "device-apu",
                 "jtag_device_name": "arm_dap"},
                {**common, "target_id": 4, "target_ctx": "target-fpga", "name": "xc7z020",
                 "parent_ctx": "", "parent": "", "jtag_device_ctx": "device-fpga",
                 "jtag_device_name": "xc7z020"},
            ]
            return {row["target_ctx"]: row for row in rows}

        class FakeController:
            def __init__(self, session):
                self.targets = {"apu": session.apu}
                self.selected = {row["name"]: row for row in session.properties.values()}

            def gate(self):
                return None

        class FakeLog:
            def __init__(self, path):
                self.journal = runner.Journal(path)
                self.stream = self.journal.stream

            def call(self, *args, **kwargs):
                return self.journal.call(*args, **kwargs)

            def close(self):
                self.journal.close()

        with tempfile.TemporaryDirectory(prefix="s2b_t18_csr_map_") as temp:
            root = Path(temp)
            with mock.patch.object(helper, "verify_runtime_sources", return_value={}):
                for fail_load in (False, True):
                    with self.subTest(fail_load=fail_load):
                        case_root = root / str(fail_load)
                        case_root.mkdir()
                        session = FakeSession(fail_load=fail_load)
                        session.properties = target_rows()
                        controller = FakeController(session)
                        helper_config = {"sdk_files": {}}
                        record = {"verified_inputs": {"compat_artifacts": {"implemented_xsa": xsa_binding}},
                                  "cleanup_errors": []}
                        owner = {}
                        log = FakeLog(case_root / "calls.jsonl")
                        try:
                            if fail_load:
                                with self.assertRaisesRegex(OSError, "partial loadhw"):
                                    helper.register_csr_debug_map(helper_config, record, log, session,
                                                                  controller, owner)
                                self.assertTrue(owner["attempted"])
                                self.assertEqual(record["debug_memory_map"]["status"], "ATTEMPTED")
                            else:
                                helper.register_csr_debug_map(helper_config, record, log, session,
                                                              controller, owner)
                                self.assertEqual(record["debug_memory_map"]["status"], "REGISTERED_CSR_ONLY")
                            helper.clear_csr_debug_map(helper_config, record, log, session, owner)
                            self.assertEqual(record["debug_memory_map"]["cleanup"], "OWNED_HW_MAP_CLEARED")
                            self.assertEqual(session._designtable, {})
                        finally:
                            log.close()

    def test_v1_manifest_receipt_allows_t18_only_after_complete_admission(self):
        trace = []
        wire = FakeWire(trace)
        controller = FakeController(trace)
        acceptance = FakeAcceptance(trace, wire)
        config = self.config()
        checked = self.checked()
        result = runner.execute_board_flow(controller, wire, config, checked, FakeApis(acceptance))
        self.assertEqual(result["status"], "PASS_MODEL_CORPUS_AND_STRESS_ONLY")
        self.assertEqual(trace[:6], ["select_and_gate", "system_reset_stop", "download_init",
                                     "observe_eos1", "postconfig", "download_app"])
        self.assertLess(trace.index("download_app"), trace.index("admit"))
        self.assertLess(trace.index("banner"), trace.index("admit"))
        self.assertLess(trace.index("admit"), trace.index("execute"))
        self.assertEqual(len(wire.sent_requests), 1)

    def test_banner_uses_verified_build_record_with_binding_only_config(self):
        """使用实板同款文件引用配置，构建内容来自预检已校验的结果。"""
        trace = []
        wire = FakeWire(trace)
        controller = FakeController(trace)
        acceptance = FakeAcceptance(trace, wire)
        checked = self.checked()
        build_path = ROOT / "report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04_artifacts/build_details.json"
        checked["build"] = json.loads(build_path.read_text(encoding="utf-8"))
        result = runner.execute_board_flow(controller, wire, self.config(), checked, FakeApis(acceptance))
        self.assertEqual(result["status"], "PASS_MODEL_CORPUS_AND_STRESS_ONLY")
        self.assertEqual(wire.banner_bindings,
                         (checked["build"]["source_sha256"]["vitis/s2b_inference_app.c"],
                          checked["build"]["xsa_sha256"]))

    def test_wrong_manifest_receipt_blocks_t18_without_uart_tx(self):
        trace = []
        wire = FakeWire(trace)
        controller = FakeController(trace)
        acceptance = FakeAcceptance(trace, wire, fail_receipt=True)
        with self.assertRaises(runner.RunnerError):
            runner.execute_board_flow(controller, wire, self.config(), self.checked(), FakeApis(acceptance))
        self.assertEqual(acceptance.execute_count, 0)
        self.assertEqual(wire.sent_requests, {})
        self.assertTrue(wire.failed)
        self.assertIn("fail_stop", trace)

    def test_eos_and_postconfig_failure_never_download_app_or_transmit(self):
        for stage in ("eos", "postconfig"):
            with self.subTest(stage=stage):
                trace = []
                wire = FakeWire(trace)
                controller = FakeController(trace, fail_at=stage)
                acceptance = FakeAcceptance(trace, wire)
                with self.assertRaises(runner.RunnerError):
                    runner.execute_board_flow(controller, wire, self.config(), self.checked(), FakeApis(acceptance))
                self.assertNotIn("download_app", trace)
                self.assertEqual(acceptance.execute_count, 0)
                self.assertEqual(wire.sent_requests, {})
                self.assertTrue(wire.failed)
                self.assertIn("fail_stop", trace)

    def test_dynamic_jtag_and_uart_errors_fail_closed_without_retry(self):
        trace = []
        wire = FakeWire(trace)
        controller = FakeController(trace, fail_select=True)
        acceptance = FakeAcceptance(trace, wire)
        with self.assertRaises(runner.RunnerError):
            runner.execute_board_flow(controller, wire, self.config(), self.checked(), FakeApis(acceptance))
        self.assertEqual(acceptance.execute_count, 0)
        self.assertEqual(wire.sent_requests, {})
        self.assertTrue(wire.failed)
        self.assertIn("fail_stop", trace)

        trace = []
        wire = FakeWire(trace, fail_send=True)
        controller = FakeController(trace)
        acceptance = FakeAcceptance(trace, wire)
        with self.assertRaises(runner.RunnerError):
            runner.execute_board_flow(controller, wire, self.config(), self.checked(), FakeApis(acceptance))
        self.assertEqual(acceptance.execute_count, 1)
        self.assertEqual(len(wire.sent_requests), 1)
        self.assertTrue(wire.failed)
        self.assertIn("fail_stop", trace)

    def test_banner_failure_blocks_admission_and_csr_scope_is_explicit(self):
        trace = []
        wire = FakeWire(trace, fail_banner=True)
        controller = FakeController(trace)
        acceptance = FakeAcceptance(trace, wire)
        with self.assertRaises(runner.RunnerError):
            runner.execute_board_flow(controller, wire, self.config(), self.checked(), FakeApis(acceptance))
        self.assertNotIn("admit", trace)
        self.assertEqual(acceptance.execute_count, 0)
        self.assertFalse(wire.sent_requests)

        class FakeCsrFlow:
            @staticmethod
            def execute(controller, wire, config, checked, apis, admission, journal):
                trace.append("csr_execute")
                return {"status": "PASS_CSR_RECOVERY_SCOPE_ONLY"}

        trace = []
        wire = FakeWire(trace)
        controller = FakeController(trace)
        acceptance = FakeAcceptance(trace, wire)
        result = runner.execute_board_flow(controller, wire, self.config(), self.checked(),
                                           FakeApis(acceptance, FakeCsrFlow), scope="csr")
        self.assertEqual(result["status"], "PASS_CSR_RECOVERY_SCOPE_ONLY")
        self.assertLess(trace.index("banner"), trace.index("admit"))
        self.assertLess(trace.index("admit"), trace.index("csr_execute"))
        self.assertEqual(acceptance.execute_count, 0)

        failed_result = {"status": "FAILED_CSR_RECOVERY_SCOPE_ONLY",
                         "error": "RuntimeError('mid-flow failure')",
                         "t20_outputs": [{"path": "busy_result.json", "sha256": "a" * 64}]}

        class FailedCsrFlow:
            @staticmethod
            def execute(controller, wire, config, checked, apis, admission, journal):
                return failed_result

        trace = []
        wire = FakeWire(trace)
        controller = FakeController(trace)
        acceptance = FakeAcceptance(trace, wire)
        with self.assertRaises(runner.RunnerError) as raised:
            runner.execute_board_flow(controller, wire, self.config(), self.checked(),
                                      FakeApis(acceptance, FailedCsrFlow), scope="csr")
        self.assertEqual(raised.exception.csr_flow_result, failed_result)

    def test_csr_missing_bresp_is_preserved_as_blocked_after_safe_flow(self):
        """证据类型未暴露可保留受阻结论，不能被改成通过或失败清理路径。"""
        blocked = {"status": "BLOCKED_CSR_RECOVERY_SCOPE_ONLY",
                   "blockers": [{"name": "busy_start_native_bresp", "status": "BLOCKED"}]}

        class BlockedCsrFlow:
            @staticmethod
            def execute(controller, wire, config, checked, apis, admission, journal):
                return blocked

        trace = []
        wire = FakeWire(trace)
        controller = FakeController(trace)
        acceptance = FakeAcceptance(trace, wire)
        result = runner.execute_board_flow(controller, wire, self.config(), self.checked(),
                                          FakeApis(acceptance, BlockedCsrFlow), scope="csr")
        self.assertEqual(result["status"], "BLOCKED_CSR_RECOVERY_SCOPE_ONLY")
        self.assertEqual(result["blockers"], blocked["blockers"])
        self.assertEqual(acceptance.execute_count, 0)

    def test_blocked_csr_manifest_check_passes_real_delivery_schema(self):
        """受阻的CSR检查须被真实清单检查器识别，不能在收尾时变成封包失败。"""
        from verification import check_stage_delivery as delivery
        from verification import s2b_csr_acceptance_flow as csr_flow
        item = csr_flow._scope_check({"status": "BLOCKED_CSR_RECOVERY_SCOPE_ONLY"})
        errors, statuses = [], []
        delivery.validate_check(item, 0, "evidence", errors, statuses)
        self.assertEqual(errors, [])
        self.assertIsNone(item["exit_code"])
        self.assertEqual(statuses[0]["status"], "BLOCKED")

    def test_scope_and_deadline_profile_are_strict(self):
        with self.assertRaisesRegex(runner.RunnerError, "scope"):
            runner.run("missing.json", scope="arbitrary")
        config = {"core_timeout": 1, "drain_timeout": 1, "response_timeout_seconds": 450}
        runner._validate_deadline_profile(config)
        cases = (("core_timeout", 0), ("core_timeout", True), ("core_timeout", 1.0),
                 ("core_timeout", 0x100000000), ("drain_timeout", 0), ("drain_timeout", False),
                 ("drain_timeout", 1.5), ("drain_timeout", 0x100000000),
                 ("response_timeout_seconds", 0), ("response_timeout_seconds", float("inf")),
                 ("response_timeout_seconds", 450.01))
        for field, value in cases:
            with self.subTest(field=field, value=value), self.assertRaises(runner.RunnerError):
                runner._validate_deadline_profile(dict(config, **{field: value}))

    def test_g0_deadline_profile_is_bound_to_config_values(self):
        with tempfile.TemporaryDirectory(prefix="s2b_t18_deadline_profile_") as temp:
            root = Path(temp)
            config_path = self._make_preflight_tree(root, physical="G0_FROZEN", uart="G0_FROZEN")
            config = json.loads(config_path.read_text(encoding="utf-8"))
            receipt = json.loads(Path(config["g0_basis"]["path"]).read_text(encoding="utf-8"))
            receipt["deadline_profile"]["drain_timeout"] -= 1
            with mock.patch.object(runner, "ROOT", root):
                versions = runner._validate_interface_freeze_sources(config["bindings"])
                with self.assertRaisesRegex(runner.RunnerError, "deadline_profile与当前config值不一致"):
                    runner._validate_g0_receipt(receipt, config, versions)

    def test_serial_identity_is_config_driven_and_exact(self):
        config = {"hw_server": {"process_id": 41, "executable_path": r"D:\Xilinx\hw_server.exe",
                                "creation_time_filetime_utc": "100"},
                  "serial": {"identity": {"port": "COM8", "name": "USB Serial Device (COM8)",
                                           "pnp_device_id": "USB\\VID_1234&PID_5678", "config_manager_error_code": 0}}}
        snapshot = {"snapshot": {
            "servers": [{"ProcessId": 41, "ExecutablePath": r"D:\Xilinx\hw_server.exe",
                         "CreationTimeFileTimeUtc": "100"}],
            "listeners": [{"LocalAddress": "127.0.0.1", "LocalPort": 3121, "OwningProcess": 41}],
            "ports": [{"Name": "USB Serial Device (COM8)", "PNPDeviceID": "USB\\VID_1234&PID_5678",
                       "ConfigManagerErrorCode": 0}],
        }}
        self.assertEqual(runner.validate_system_identity(snapshot, config)["uart"]["Name"], "USB Serial Device (COM8)")
        snapshot["snapshot"]["ports"][0]["PNPDeviceID"] = "USB\\VID_0000&PID_0000"
        with self.assertRaises(runner.RunnerError):
            runner.validate_system_identity(snapshot, config)

    @staticmethod
    def config():
        return {"build_details": {"path": "build.json", "sha256": "c" * 64},
                "visibility_review": {"path": "review.json", "sha256": "d" * 64},
                "final_review": {"path": "final_review.json", "sha256": "e" * 64},
                "core_timeout": 0xFFFFFFFF, "drain_timeout": 60,
                "final_platform_manifest": {"path": "manifest.json", "sha256": "f" * 64}}

    @staticmethod
    def checked():
        return {"build": {"source_sha256": {"vitis/s2b_inference_app.c": "a" * 64},
                          "xsa_sha256": "b" * 64},
                "cold_basis": {"path": "cold.json", "sha256": "f" * 64},
                "proof_path": Path("profile.json"), "review_path": Path("review.json"),
                "manifest_path": Path("manifest.json"), "final_review_path": Path("final_review.json"),
                "preparation_path": Path("preparation.json"), "run_dir": Path("run"),
                "deploy_dir": Path("deployment")}


if __name__ == "__main__":
    unittest.main()
