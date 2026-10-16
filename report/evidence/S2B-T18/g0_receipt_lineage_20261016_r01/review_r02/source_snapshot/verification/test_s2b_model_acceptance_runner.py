"""S2B-T18 runner 的隔离门禁与失败语义测试。"""
from __future__ import annotations

import importlib.util
import hashlib
import json
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
        self.assertNotIn("run_s2b_visibility_probe", source)
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

    def test_default_unpinned_g0_and_cold_basis_fail_before_runtime_or_device_import(self):
        self.assertIsNone(runner.G0_BASIS_PATH)
        self.assertIsNone(runner.G0_BASIS_SHA256)
        self.assertIsNone(runner.COLD_BASIS_PATH)
        self.assertIsNone(runner.COLD_BASIS_SHA256)
        with tempfile.TemporaryDirectory(prefix="s2b_t18_default_block_") as temp:
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

    def test_checked_in_interfaces_are_unfrozen_and_block_preflight(self):
        bindings = {}
        for name, relative in (
                ("interface", "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"),
                ("uart_interface", "docs/obsidian-project/02-方案设计/s2b_board_transport.md")):
            path = runner.ROOT / relative
            bindings[name] = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        with self.assertRaisesRegex(runner.RunnerError, "PS/PL物理接口仍未冻结"):
            runner.validate_preflight_basis({"bindings": bindings,
                                             "g0_basis": {"path": "unused", "sha256": "0" * 64},
                                             "cold_basis": {"path": "unused", "sha256": "0" * 64}})

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
                    mock.patch.object(runner.subprocess, "run", side_effect=AssertionError("不得继续")) as git:
                with self.assertRaisesRegex(runner.RunnerError, "尚无独立审查固定的正式回执SHA"):
                    runner.validate_v1_inputs(config, apis=object())
            git.assert_not_called()

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
        physical_path.write_text("test-only / not approval: 状态：" + physical + "；版本：physical-test/0.1\n", encoding="utf-8")
        uart_path.write_text("test-only / not approval: 状态：" + uart + "；版本：uart-test/0.1\n", encoding="utf-8")
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
        versions = {"interface": "physical-test/0.1", "uart_interface": "uart-test/0.1"}
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
                        "controller_source_sha256": runner.JTAG_SOURCE_SHA256,
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
        return {"build_details": {"path": "build.json", "sha256": "c" * 64,
                                  "source_sha256": {"vitis/s2b_inference_app.c": "a" * 64},
                                  "xsa_sha256": "b" * 64},
                "visibility_review": {"path": "review.json", "sha256": "d" * 64},
                "final_review": {"path": "final_review.json", "sha256": "e" * 64},
                "core_timeout": 0xFFFFFFFF, "drain_timeout": 60,
                "final_platform_manifest": {"path": "manifest.json", "sha256": "f" * 64}}

    @staticmethod
    def checked():
        return {"cold_basis": {"path": "cold.json", "sha256": "f" * 64},
                "proof_path": Path("profile.json"), "review_path": Path("review.json"),
                "manifest_path": Path("manifest.json"), "final_review_path": Path("final_review.json"),
                "preparation_path": Path("preparation.json"), "run_dir": Path("run"),
                "deploy_dir": Path("deployment")}


if __name__ == "__main__":
    unittest.main()
