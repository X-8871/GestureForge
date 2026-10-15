"""S2B-T19单样本入口的离线门禁与失败安全测试。"""
from pathlib import Path
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).absolute().parents[1]
ENTRY_PATH = ROOT / "vitis/run_s2b_model_qualification.py"
EVIDENCE_ROOT = ROOT / "report/evidence/S2B-T19/model_qualification_entry_20261015_r01"
SPEC = importlib.util.spec_from_file_location("s2b_model_qualification_entry", ENTRY_PATH)
ENTRY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENTRY)


def valid_config(run_dir="unused"):
    """构造只用于纯离线类型测试的最小配置，不声明任何正式批准。"""
    dummy = {"path": str(ROOT / "unused.json"), "sha256": "a" * 64}
    return {
        "schema_version": 1,
        "source_commit": "1" * 40,
        "run_dir": run_dir,
        "build_details": dummy,
        "bindings": {},
        "owned_hw_server_identity": dummy,
        "uart_identity": {
            "port": "COM4",
            "name": "CP210x (COM4)",
            "pnp_device_id": "USB\\UNIT_FIXTURE",
            "config_manager_error_code": 0,
        },
        "cold_basis": dummy,
        "sdk_files": [],
        "pyserial_files": [],
        "asset_root": str(ROOT / "assets"),
        "qualification_receipt": {
            "path": str(ROOT / "untrusted-review.json"),
            "sha256": "b" * 64,
        },
        "sample_index": 0,
        "frame": 0,
        "repeat": 1,
        "core_timeout_cycles": 1,
        "drain_timeout_cycles": 1,
        "response_timeout_seconds": 450,
        "g0_basis": dummy,
        "timeout_basis": dummy,
    }


def valid_manual_root_documents():
    """构造与固定人工信任根schema一致的离线夹具。"""
    platform_key = "report/evidence/S2B-T19/current_probe_scope_20261015_r01/platform_delivery_manifest.json"
    provenance = {
        "schema_version": 1,
        "kind": "s2b-independent-review-provenance/1.0.0",
        "reviewer_task": ENTRY.MANUAL_REVIEWER_TASK,
        "role": "INDEPENDENT_REVIEWER",
        "source_commit": ENTRY.MANUAL_REVIEW_SOURCE_COMMIT,
        "verdict": "PASS",
        "scope": ENTRY.MANUAL_REVIEW_SCOPE,
        "frozen_reviewed_inputs": {platform_key: ENTRY.MANUAL_PLATFORM_MANIFEST["sha256"]},
        "independent_raw_facts": {
            "status": "INDEPENDENT_RAW_FACTS_PASS",
            "dynamic_hardware": "NOT_RUN",
        },
        "hardware_execution": "NOT_RUN",
    }
    compatibility = {
        "schema_version": 1,
        "kind": "s2b-runtime-platform-compatibility/1.0.0",
        "role": "INDEPENDENT_REVIEWER",
        "status": "PASS",
        "scope": ENTRY.MANUAL_REVIEW_SCOPE,
        "visibility_parameter": 0,
        "artifacts": {"platform_manifest": dict(ENTRY.MANUAL_PLATFORM_MANIFEST)},
    }
    return provenance, compatibility


def valid_qualification_trust_claim():
    """构造仅供离线门禁单测使用的固定Reviewer/root声明。"""
    return {
        "reviewer_task": ENTRY.MANUAL_REVIEWER_TASK,
        "manual_trust_root": ENTRY.MANUAL_TRUST_ROOT_CLAIM,
    }


class ConfigGateTests(unittest.TestCase):
    """核对严格字段、整数类型及未冻结准入锚点。"""

    def test_valid_narrow_configuration_and_exact_keys(self):
        ENTRY.validate_config(valid_config())
        extra = valid_config()
        extra["allow_hardware"] = True
        with self.assertRaisesRegex(ENTRY.QualificationError, "字段错误"):
            ENTRY.validate_config(extra)
        root_override = valid_config()
        root_override["manual_trust_root"] = ENTRY.MANUAL_TRUST_ROOT_CLAIM
        with self.assertRaisesRegex(ENTRY.QualificationError, "字段错误"):
            ENTRY.validate_config(root_override)
        missing = valid_config()
        del missing["g0_basis"]
        with self.assertRaisesRegex(ENTRY.QualificationError, "字段错误"):
            ENTRY.validate_config(missing)

    def test_bool_float_and_out_of_scope_fields_are_rejected(self):
        for key, value in (("schema_version", True), ("sample_index", False),
                           ("frame", 0.0), ("repeat", True),
                           ("core_timeout_cycles", True),
                           ("drain_timeout_cycles", 0),
                           ("core_timeout_cycles", 0x100000000)):
            with self.subTest(key=key, value=value):
                cfg = valid_config()
                cfg[key] = value
                with self.assertRaises(ENTRY.QualificationError):
                    ENTRY.validate_config(cfg)

    def test_uart_timeout_is_seconds_and_fixed_to_reviewed_value(self):
        ENTRY.validate_config(valid_config())
        for value in (True, 450.0, 449, 451, 0):
            with self.subTest(value=value):
                cfg = valid_config()
                cfg["response_timeout_seconds"] = value
                with self.assertRaises(ENTRY.QualificationError):
                    ENTRY.validate_config(cfg)

    def test_config_cannot_authorize_self_asserted_reviewer(self):
        cfg = valid_config()
        cfg["qualification_receipt"] = {
            "path": str(ROOT / "untrusted-review.json"),
            "sha256": "c" * 64,
            "role": "INDEPENDENT_REVIEWER",
            "status": "PASS",
        }
        with patch.object(ENTRY, "helpers", side_effect=AssertionError("不得读取自报receipt")):
            with self.assertRaisesRegex(ENTRY.QualificationError, "独立Reviewer原件"):
                ENTRY.verify_review(cfg, {}, "d" * 64)

    def test_canonical_entry_digest_normalizes_only_the_anchor_assignment(self):
        with tempfile.TemporaryDirectory(prefix="s2b_entry_digest_") as raw_dir:
            source = Path(raw_dir) / "entry.py"
            first = (b"# fixture\nTRUSTED_REVIEW_ANCHOR = None\nVALUE = 1\n")
            second = (b"# fixture\nTRUSTED_REVIEW_ANCHOR = {'path': 'review.json', 'sha256': '" +
                      b"a" * 64 + b"'}\nVALUE = 1\n")
            changed_other_byte = second.replace(b"VALUE = 1", b"VALUE = 2")
            source.write_bytes(first)
            first_digest = ENTRY.canonical_entry_sha256(source)
            receipt = {"entry_digest_scheme": ENTRY.ENTRY_DIGEST_SCHEME,
                       "canonical_entry_sha256_v1": first_digest}
            ENTRY.require_reviewed_entry_digest(receipt, source)
            source.write_bytes(second)
            self.assertEqual(ENTRY.canonical_entry_sha256(source), first_digest)
            ENTRY.require_reviewed_entry_digest(receipt, source)
            source.write_bytes(changed_other_byte)
            self.assertNotEqual(ENTRY.canonical_entry_sha256(source), first_digest)
            with self.assertRaisesRegex(ENTRY.QualificationError, "canonical digest漂移"):
                ENTRY.require_reviewed_entry_digest(receipt, source)

    def test_canonical_entry_digest_rejects_ambiguous_or_executable_anchor(self):
        with tempfile.TemporaryDirectory(prefix="s2b_entry_anchor_format_") as raw_dir:
            source = Path(raw_dir) / "entry.py"
            for raw in (
                b"TRUSTED_REVIEW_ANCHOR = None\nTRUSTED_REVIEW_ANCHOR = None\n",
                b"TRUSTED_REVIEW_ANCHOR = __import__('os')\n",
                b"TRUSTED_REVIEW_ANCHOR = {'path': 'review.json', 'sha256': 'bad'}\n",
            ):
                with self.subTest(raw=raw):
                    source.write_bytes(raw)
                    with self.assertRaises(ENTRY.QualificationError):
                        ENTRY.canonical_entry_sha256(source)

    def test_source_anchor_replacement_is_rejected_against_existing_config(self):
        cfg = valid_config()
        pinned = {"path": str(ROOT / "review.json"), "sha256": "c" * 64}
        cfg["qualification_receipt"] = pinned
        raw = ENTRY_PATH.read_bytes()
        old = b"TRUSTED_REVIEW_ANCHOR = None"
        replacement = b"TRUSTED_REVIEW_ANCHOR = {'path': 'replacement.json', 'sha256': '" + b"d" * 64 + b"'}"
        self.assertEqual(raw.count(old), 1)
        with tempfile.TemporaryDirectory(prefix="s2b_changed_entry_anchor_") as raw_dir:
            changed_entry = Path(raw_dir) / "entry.py"
            changed_entry.write_bytes(raw.replace(old, replacement, 1))
            with patch.object(ENTRY, "__file__", changed_entry), \
                 patch.object(ENTRY, "TRUSTED_REVIEW_ANCHOR", pinned):
                with self.assertRaisesRegex(ENTRY.QualificationError, "入口内Reviewer锚点与已加载源码值不一致"):
                    ENTRY.require_hardware_enablement(cfg)

    def test_config_cannot_spoof_a_different_pinned_review_anchor(self):
        pinned = {"path": str(ROOT / "review.json"), "sha256": "c" * 64}
        cfg = valid_config()
        cfg["qualification_receipt"] = {"path": str(ROOT / "forged-review.json"), "sha256": "d" * 64}
        with patch.object(ENTRY, "TRUSTED_REVIEW_ANCHOR", pinned), \
             patch.object(ENTRY, "read_trusted_review_anchor", return_value=pinned):
            with self.assertRaisesRegex(ENTRY.QualificationError, "配置与总控固定的独立Reviewer原件锚点不一致"):
                ENTRY.require_hardware_enablement(cfg)

    def test_manual_trust_root_schema_scope_role_and_cross_binding_are_fixed(self):
        self.assertEqual(ENTRY.MANUAL_REVIEW_PROVENANCE["path"],
                         "C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition/report/evidence/S2B-T19/current_probe_independent_20261015_r01/review_provenance.json")
        self.assertEqual(ENTRY.MANUAL_REVIEW_PROVENANCE["sha256"],
                         "c87a2f40a099bdce0fce127af7d3c3282f4b2442e19dbc9da4f299b588321ce5")
        self.assertEqual(ENTRY.MANUAL_RUNTIME_COMPATIBILITY["path"],
                         "C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition/report/evidence/S2B-T19/current_probe_independent_20261015_r01/runtime_compatibility_receipt.json")
        self.assertEqual(ENTRY.MANUAL_RUNTIME_COMPATIBILITY["sha256"],
                         "e22fd0a1fa0399de48d9694dd07c7b10e06dbb60f55aed7ce8a9057fc3d4c7ea")
        provenance, compatibility = valid_manual_root_documents()
        self.assertEqual(ENTRY.validate_manual_review_root_documents(provenance, compatibility),
                         ENTRY.MANUAL_TRUST_ROOT_CLAIM)
        mutations = (
            ("provenance", "schema_version", True),
            ("provenance", "role", "CONFIGURATOR"),
            ("provenance", "reviewer_task", "/root/unauthorized_reviewer"),
            ("provenance", "scope", "visibility1_sample000_single_job"),
            ("provenance", "hardware_execution", "PASS"),
            ("compatibility", "role", "CONFIGURATOR"),
            ("compatibility", "scope", "visibility1_sample000_single_job"),
            ("compatibility", "visibility_parameter", 1),
        )
        for target, key, value in mutations:
            with self.subTest(target=target, key=key):
                changed_provenance, changed_compatibility = valid_manual_root_documents()
                target_object = changed_provenance if target == "provenance" else changed_compatibility
                target_object[key] = value
                with self.assertRaises(ENTRY.QualificationError):
                    ENTRY.validate_manual_review_root_documents(changed_provenance, changed_compatibility)
        changed_provenance, changed_compatibility = valid_manual_root_documents()
        changed_compatibility["artifacts"]["platform_manifest"]["sha256"] = "f" * 64
        with self.assertRaisesRegex(ENTRY.QualificationError, "平台清单原件"):
            ENTRY.validate_manual_review_root_documents(changed_provenance, changed_compatibility)

    def test_coordinated_anchor_config_and_receipt_rewrite_cannot_replace_reviewer_root(self):
        raw = ENTRY_PATH.read_bytes()
        fake_anchor = {"path": str(ROOT / "forged-review.json"), "sha256": "e" * 64}
        old = b"TRUSTED_REVIEW_ANCHOR = None"
        replacement = b"TRUSTED_REVIEW_ANCHOR = " + repr(fake_anchor).encode("utf-8")
        self.assertEqual(raw.count(old), 1)
        with tempfile.TemporaryDirectory(prefix="s2b_coordinated_rewrite_") as raw_dir:
            changed_entry = Path(raw_dir) / "entry.py"
            changed_entry.write_bytes(raw.replace(old, replacement, 1))
            self.assertEqual(ENTRY.canonical_entry_sha256(changed_entry),
                             ENTRY.canonical_entry_sha256(ENTRY_PATH))
            forged_claims = (
                {"reviewer_task": "/root/unauthorized_reviewer",
                 "manual_trust_root": ENTRY.MANUAL_TRUST_ROOT_CLAIM},
                {"reviewer_task": ENTRY.MANUAL_REVIEWER_TASK},
            )
            for forged_receipt in forged_claims:
                with self.subTest(forged_receipt=forged_receipt):
                    cfg = valid_config()
                    cfg["qualification_receipt"] = fake_anchor
                    with patch.object(ENTRY, "__file__", changed_entry), \
                         patch.object(ENTRY, "TRUSTED_REVIEW_ANCHOR", fake_anchor), \
                         patch.object(ENTRY, "TRUSTED_G0_ANCHOR", cfg["g0_basis"]), \
                         patch.object(ENTRY, "TRUSTED_COLD_ANCHOR", cfg["cold_basis"]), \
                         patch.object(ENTRY, "TRUSTED_TIMEOUT_MEASUREMENT_ANCHOR", cfg["timeout_basis"]), \
                         patch.object(ENTRY, "validate_manual_review_trust_root",
                                      return_value=ENTRY.MANUAL_TRUST_ROOT_CLAIM), \
                         patch.object(ENTRY, "document", return_value=forged_receipt):
                        with self.assertRaises(ENTRY.QualificationError):
                            ENTRY.require_hardware_enablement(cfg)

    def test_receipt_schema_requires_versioned_canonical_entry_digest(self):
        self.assertEqual(ENTRY.ENTRY_DIGEST_SCHEME, "s2b-model-qualification-entry-canonical-sha256-v1")
        self.assertIn("canonical_entry_sha256_v1", ENTRY.RECEIPT_KEYS)
        self.assertIn("entry_digest_scheme", ENTRY.RECEIPT_KEYS)
        self.assertIn("reviewer_task", ENTRY.RECEIPT_KEYS)
        self.assertIn("manual_trust_root", ENTRY.RECEIPT_KEYS)
        self.assertNotIn("entry_sha256", ENTRY.RECEIPT_KEYS)

    def test_g0_cold_and_timeout_evidence_must_be_independently_fixed(self):
        cfg = valid_config()
        review = {"path": str(ROOT / "review.json"), "sha256": "c" * 64}
        cfg["qualification_receipt"] = review
        with patch.object(ENTRY, "TRUSTED_REVIEW_ANCHOR", review), \
             patch.object(ENTRY, "read_trusted_review_anchor", return_value=review), \
             patch.object(ENTRY, "validate_manual_review_trust_root",
                          return_value=ENTRY.MANUAL_TRUST_ROOT_CLAIM), \
             patch.object(ENTRY, "document", return_value=valid_qualification_trust_claim()), \
             patch.object(ENTRY, "TRUSTED_G0_ANCHOR", None):
            with self.assertRaisesRegex(ENTRY.QualificationError, "正式G0依据"):
                ENTRY.require_hardware_enablement(cfg)
        with patch.object(ENTRY, "TRUSTED_REVIEW_ANCHOR", review), \
             patch.object(ENTRY, "read_trusted_review_anchor", return_value=review), \
             patch.object(ENTRY, "validate_manual_review_trust_root",
                          return_value=ENTRY.MANUAL_TRUST_ROOT_CLAIM), \
             patch.object(ENTRY, "document", return_value=valid_qualification_trust_claim()), \
             patch.object(ENTRY, "TRUSTED_G0_ANCHOR", cfg["g0_basis"]), \
             patch.object(ENTRY, "TRUSTED_COLD_ANCHOR", None):
            with self.assertRaisesRegex(ENTRY.QualificationError, "POR/冷生命周期依据"):
                ENTRY.require_hardware_enablement(cfg)

    def test_unmeasured_deadline_values_never_enable_hardware(self):
        cfg = valid_config()
        with patch.object(ENTRY, "TRUSTED_REVIEW_ANCHOR", cfg["qualification_receipt"]), \
             patch.object(ENTRY, "read_trusted_review_anchor", return_value=cfg["qualification_receipt"]), \
             patch.object(ENTRY, "validate_manual_review_trust_root",
                          return_value=ENTRY.MANUAL_TRUST_ROOT_CLAIM), \
             patch.object(ENTRY, "document", return_value=valid_qualification_trust_claim()), \
             patch.object(ENTRY, "TRUSTED_G0_ANCHOR", cfg["g0_basis"]), \
             patch.object(ENTRY, "TRUSTED_COLD_ANCHOR", cfg["cold_basis"]), \
             patch.object(ENTRY, "TRUSTED_TIMEOUT_MEASUREMENT_ANCHOR", None):
            for value in (1, 0xFFFFFFFF):
                with self.subTest(value=value):
                    cfg["core_timeout_cycles"] = value
                    cfg["drain_timeout_cycles"] = value
                    with self.assertRaisesRegex(ENTRY.QualificationError, "部署期限测量依据"):
                        ENTRY.require_hardware_enablement(cfg)

    def test_only_uart_observation_timeout_value_is_passed_to_wire(self):
        class FakeWire:
            def __init__(self, stream, rx, tx, *, response_timeout):
                self.stream = stream
                self.response_timeout = response_timeout

        class FakeJtag:
            JtagWireSession = FakeWire

        wire = ENTRY.make_wire(FakeJtag, object(), object(), object(), object(), valid_config())
        self.assertEqual(wire.response_timeout, 450)


class SideEffectAndFailureTests(unittest.TestCase):
    """检查导入、预检及运行失败都不会越过硬件门。"""

    def test_import_and_help_do_not_load_sdk_or_serial(self):
        code = (
            "import importlib.util,sys;"
            f"s=importlib.util.spec_from_file_location('entry',r'{ENTRY_PATH}');"
            "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
            "assert not any(n == 'serial' or n.startswith('serial.') for n in sys.modules);"
            "assert not any(n == 'xsdb' or n.startswith('xsdb.') for n in sys.modules);"
            "print('IMPORT_ISOLATION_OK')"
        )
        imported = subprocess.run([sys.executable, "-X", "utf8", "-B", "-c", code],
                                  capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(imported.returncode, 0, imported.stderr)
        self.assertIn("IMPORT_ISOLATION_OK", imported.stdout)
        env = dict(os.environ)
        env.pop("S2B_MODEL_QUALIFICATION_CONFIG", None)
        help_result = subprocess.run([sys.executable, "-X", "utf8", "-B", str(ENTRY_PATH), "--help"],
                                     capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("--preflight", help_result.stdout)

    def test_preflight_is_read_only_and_returns_no_run_directory(self):
        with tempfile.TemporaryDirectory(prefix="s2b_offline_preflight_") as raw_dir:
            temp_root = Path(raw_dir)
            config_path = temp_root / "config.json"
            config_path.write_text(json.dumps(valid_config()), encoding="utf-8")
            requested = temp_root / "must_not_be_created"
            cfg = valid_config(str(requested))
            config_path.write_text(json.dumps(cfg), encoding="utf-8")
            with patch.object(ENTRY, "TRUSTED_REVIEW_ANCHOR", None), \
                 patch.object(ENTRY, "helpers", return_value=ENTRY.helpers()):
                with self.assertRaisesRegex(ENTRY.QualificationError, "独立Reviewer原件"):
                    ENTRY.run(config_path, offline_only=True)
            self.assertFalse(requested.exists())
            self.assertFalse(any(name == "serial" or name.startswith("serial.") for name in sys.modules))
            self.assertFalse(any(name == "xsdb" or name.startswith("xsdb.") for name in sys.modules))

    def test_hardware_attempt_records_block_before_any_device_import(self):
        probe, jtag, transport = ENTRY.helpers()
        with tempfile.TemporaryDirectory(prefix="s2b_blocked_run_") as raw_dir:
            sandbox_root = Path(raw_dir)
            evidence_parent = sandbox_root / "report/evidence/S2B-T19"
            evidence_parent.mkdir(parents=True)
            run_dir = evidence_parent / "blocked_single_sample"
            cfg = valid_config(str(run_dir))
            config_path = sandbox_root / "config.json"
            config_path.write_text(json.dumps(cfg), encoding="utf-8")
            with patch.object(ENTRY, "ROOT", sandbox_root), \
                 patch.object(ENTRY, "helpers", return_value=(probe, jtag, transport)):
                with self.assertRaisesRegex(ENTRY.QualificationError, "单样本资格阻断/失败"):
                    ENTRY.run(config_path)
            result_path = run_dir / "model_qualification_result.json"
            self.assertTrue(result_path.is_file())
            result = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(result["native_exit_code"], 2)
            self.assertEqual(result["hardware_execution"], "NOT_RUN")
            self.assertFalse(result["cleanup_errors"])
            self.assertFalse(any(name == "serial" or name.startswith("serial.") for name in sys.modules))
            self.assertFalse(any(name == "xsdb" or name.startswith("xsdb.") for name in sys.modules))

    def test_pre_serial_failure_after_tcf_attempt_is_failed_and_cleans_owned_resources(self):
        class FakeRecorder:
            def __init__(self, path, record):
                self.path = path
                self.record = record
                self.stream = path.open("x", encoding="utf-8", newline="\n")

            def call(self, name, function, *args, **kwargs):
                self.record["calls"].append({"api": name})
                result = function(*args, **kwargs)
                return result

        class FakeSession:
            def __init__(self):
                self.disconnect_calls = 0
                self.targets_by_id = {}

            def connect(self, **kwargs):
                return "mock-channel"

            def targets(self, *args, **kwargs):
                if "id" in kwargs:
                    return self.targets_by_id[kwargs["id"]]
                return []

            def disconnect(self, **kwargs):
                self.disconnect_calls += 1

        class FakeTarget:
            def __init__(self, name, context):
                self._name = name
                self._ctx = context

            def state(self):
                return "Stopped"

        class FakeController:
            def __init__(self):
                self.failed = False
                self.targets = {}
                self.record = {"status": "READY", "cleanup_errors": []}
                self.close_calls = 0
                self.fail_stop_calls = 0
                self.reset_calls = 0

            def select_and_gate(self):
                return None

            def system_reset_stop(self, basis):
                self.reset_calls += 1

            def fail_stop(self):
                self.fail_stop_calls += 1

            def close(self):
                self.close_calls += 1

        class FakeSDK:
            def __init__(self, session):
                self.session = session
                self.dispose_calls = 0

            def start_debug_session(self):
                return self.session

            def dispose(self):
                self.dispose_calls += 1

        class FakeSerialModule:
            def __init__(self):
                self.construct_calls = 0

            def Serial(self, **kwargs):
                self.construct_calls += 1
                raise AssertionError("串口应在注入故障之后仍未构造")

        class FakeJtag:
            NAMES = ("APU", "ARM Cortex-A9 MPCore #0", "ARM Cortex-A9 MPCore #1", "xc7z020")
            JtagController = None

            @staticmethod
            def exact_path(raw, directory=False):
                path = Path(raw)
                if directory:
                    if not path.is_dir():
                        raise AssertionError("预期目录缺失")
                elif not path.is_file():
                    raise AssertionError("预期文件缺失")
                return path

            @staticmethod
            def validate_targets(rows):
                return {
                    FakeJtag.NAMES[1]: {"target_id": 11, "target_ctx": "cpu0-context"},
                    FakeJtag.NAMES[2]: {"target_id": 12, "target_ctx": "cpu1-context"},
                }

        class FakeTransport:
            @staticmethod
            def new_directory(path, parent):
                path.mkdir()
                return path

        class FakeProbe:
            Recorder = FakeRecorder

            @staticmethod
            def strict_json(raw):
                return json.loads(raw)

            @staticmethod
            def digest(path):
                import hashlib
                return hashlib.sha256(Path(path).read_bytes()).hexdigest()

            @staticmethod
            def save(path, value):
                with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
                    json.dump(value, stream, ensure_ascii=False)
                    stream.write("\n")

            @staticmethod
            def _identity_snapshot():
                return {"mock": True}

            @staticmethod
            def validate_identity(*args):
                return None

            @staticmethod
            def verify_runtime_sources(*args):
                return None

            @staticmethod
            def clear_csr_debug_map(*args, **kwargs):
                return None

            @staticmethod
            def register_csr_debug_map(*args, **kwargs):
                raise OSError("注入的串口打开前映射注册失败")

        with tempfile.TemporaryDirectory(prefix="s2b_pre_serial_failure_") as raw_dir:
            sandbox_root = Path(raw_dir)
            evidence_parent = sandbox_root / "report/evidence/S2B-T19"
            evidence_parent.mkdir(parents=True)
            run_dir = evidence_parent / "pre_serial_failure"
            config = valid_config(str(run_dir))
            config_path = sandbox_root / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")

            session = FakeSession()
            cpu0 = FakeTarget(FakeJtag.NAMES[1], "cpu0-context")
            cpu1 = FakeTarget(FakeJtag.NAMES[2], "cpu1-context")
            session.targets_by_id = {11: cpu0, 12: cpu1}
            sdk = FakeSDK(session)
            serial_module = FakeSerialModule()
            controller = FakeController()
            FakeJtag.JtagController = lambda *args, **kwargs: controller
            FakeProbe._runtime = staticmethod(lambda cfg: (sdk, serial_module))
            prepared = {"source_commit": config["source_commit"], "server": {},
                        "build": {"source_sha256": {"vitis/s2b_inference_app.c": "a" * 64}}}

            with patch.object(ENTRY, "ROOT", sandbox_root), \
                 patch.object(ENTRY, "helpers", return_value=(FakeProbe, FakeJtag, FakeTransport)), \
                 patch.object(ENTRY, "preflight", return_value=prepared):
                with self.assertRaisesRegex(ENTRY.QualificationError, "单样本资格阻断/失败"):
                    ENTRY.run(config_path)

            result = json.loads((run_dir / "model_qualification_result.json").read_text(encoding="utf-8"))
            self.assertTrue(result["hardware_attempted"])
            self.assertEqual(result["hardware_execution"], "BOARD_INTERACTION_ATTEMPTED")
            self.assertEqual(result["status"], "FAILED")
            self.assertEqual(result["native_exit_code"], 2)
            self.assertEqual(result["cleanup_errors"], [])
            call_names = [row["api"] for row in result["calls"]]
            self.assertIn("session.connect", call_names)
            self.assertIn("controller.close", call_names)
            self.assertIn("owned_map.clear", call_names)
            self.assertIn("session.disconnect", call_names)
            self.assertIn("xsdb.dispose", call_names)
            self.assertNotIn("serial.construct_closed", call_names)
            self.assertNotIn("serial.open", call_names)
            self.assertEqual(serial_module.construct_calls, 0)
            self.assertEqual(controller.close_calls, 1)
            self.assertEqual(session.disconnect_calls, 1)
            self.assertEqual(sdk.dispose_calls, 1)

    def test_post_request_exception_latches_failure_without_retry(self):
        class FakeWire:
            def __init__(self):
                self.failed = False
                self.last_sequence = 0
                self.epoch = 0
                self.abort_pending = None
                self.send_count = 0

            def send(self, *args):
                self.send_count += 1

            def receive(self, *args):
                raise RuntimeError("mock UART response failure")

        class FakeJtag:
            JtagWireSession = FakeWire

        class FakeController:
            def __init__(self):
                self.failed = False
                self.record = {"status": "RUNNING", "cleanup_errors": []}
                self.fail_stop_count = 0

            def gate(self, **kwargs):
                return None

            def stable_csr(self, label):
                return {0: 0x53324250, 4: 0x100, 0x00C: 0x400, 0x010: 0,
                        0x050: 0, 0x054: 0, 0x058: 0, 0x064: 0, 0x068: 0,
                        0x06C: 0, 0x070: 0, 0x074: 0}

            def fail_stop(self):
                self.fail_stop_count += 1

        class FakeTransport:
            OP_WEIGHTS = 1

            @staticmethod
            def reference_row(folder, row):
                return {}

            @staticmethod
            def make_request(*args, **kwargs):
                return object(), b"header"

        class FakeProbe:
            @staticmethod
            def save(path, value):
                return None

        wire = FakeWire()
        controller = FakeController()
        prepared = {"row": {"label": "sample000"}, "weights": b"weights",
                    "weight_path": Path("weights.bin")}
        record = {"status": "RUNNING", "cleanup_errors": []}
        with patch.object(ENTRY, "helpers", return_value=(FakeProbe, FakeJtag, FakeTransport)):
            with self.assertRaisesRegex(RuntimeError, "mock UART response failure"):
                ENTRY.single_job(valid_config(), prepared, controller, wire, Path("unused"), record)
        self.assertEqual(wire.send_count, 1)
        self.assertTrue(wire.failed)
        self.assertTrue(controller.failed)
        self.assertEqual(controller.fail_stop_count, 1)
        self.assertEqual(controller.record["status"], "FAILED")

    def test_cleanup_exception_is_retained_and_fail_stops_controller(self):
        class FakeLog:
            def call(self, name, function, **kwargs):
                return function(**kwargs)

        class FakeController:
            def __init__(self):
                self.failed = False
                self.record = {"status": "RUNNING"}
                self.fail_stop_count = 0

            def fail_stop(self):
                self.fail_stop_count += 1

        def fail_close():
            raise OSError("mock serial close failure")

        record = {"status": "RUNNING", "cleanup_errors": []}
        controller = FakeController()
        error = ENTRY.cleanup_action(FakeLog(), "serial.close", fail_close,
                                     record=record, controller=controller)
        self.assertIsInstance(error, OSError)
        self.assertEqual(record["status"], "FAILED")
        self.assertEqual(record["cleanup_errors"][0]["action"], "serial.close")
        self.assertTrue(controller.failed)
        self.assertEqual(controller.record["status"], "FAILED")
        self.assertEqual(controller.fail_stop_count, 1)


if __name__ == "__main__":
    unittest.main()
