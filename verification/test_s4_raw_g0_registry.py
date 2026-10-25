"""RAW 登记表重复事实的拒绝不一致回归；通过主入口验证退出码。"""

import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.stage4_s4b import audit_raw_system_g0_gaps as audit


class RawRegistryConsistencyTests(unittest.TestCase):
    """真实登记表作为基线，每次只扰动一个重复事实。"""

    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(audit.REGISTRY.read_text(encoding="utf-8"))

    def run_registry(self, mutate=None, mutate_contract=None):
        """隔离夹具与结果；保留真实依据件读取和主入口拒绝路径。"""
        registry = copy.deepcopy(self.registry)
        if mutate:
            mutate(registry)
        with tempfile.TemporaryDirectory(prefix="s4_raw_registry_") as directory:
            root = Path(directory)
            fixture = root / "registry.json"
            contract_path = audit.CONTRACT
            if mutate_contract:
                contract = json.loads(contract_path.read_text(encoding="utf-8"))
                mutate_contract(contract)
                contract_fixture = root / "contract.json"
                contract_fixture.write_text(json.dumps(contract, ensure_ascii=False), encoding="utf-8")
                for entry in registry["basis_bindings"]:
                    if entry["id"] == "shared_input_contract":
                        entry["path"] = str(contract_fixture)
                        entry["sha256"] = audit.sha256_of(contract_fixture)
                        break
                contract_path = contract_fixture
            fixture.write_text(json.dumps(registry, ensure_ascii=False), encoding="utf-8")
            out = root / "result"
            with patch.object(audit, "REGISTRY", fixture), patch.object(audit, "CONTRACT", contract_path), patch(
                "sys.argv", ["audit_raw_system_g0_gaps.py", "--evidence-dir", str(out)]
            ), contextlib.redirect_stdout(io.StringIO()):
                code = audit.main()
            result = json.loads((out / "raw_system_g0_gap_audit_result.json").read_text(encoding="utf-8"))
        return code, result

    def assert_rejected(self, mutate, expected):
        """确认独立新增检查阻断，而非其他错误偶然导致失败。"""
        code, result = self.run_registry(mutate)
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "FAIL")
        check = result["checks"]["redundant_facts_consistent"]
        self.assertEqual(check["status"], "FAIL")
        self.assertTrue(any(expected in error for error in check["actual"]["errors"]))
        self.assertTrue(all(check["status"] == "PASS" for name, check in result["checks"].items()
                            if name != "redundant_facts_consistent"))

    def test_matching_real_registry_passes(self):
        code, result = self.run_registry()
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "PASS")

    def test_stale_owner_hash_rejected(self):
        self.assert_rejected(lambda r: r["documented_historical_owners"][1].update(
            basis_sha256="19f754d828ca00ca83da1ac23499cb9dc0e1a91788ca8e253ccbe33d32ee9ec3"), "basis_sha256")

    def test_missing_hash_binding_rejected(self):
        self.assert_rejected(lambda r: r["documented_historical_owners"][1].pop("basis_binding_id"), "basis_sha256")

    def test_original_decimal_start_rejected(self):
        self.assert_rejected(lambda r: r["documented_historical_owners"][0].update(start=708608), "start/start_hex")

    def test_original_decimal_end_rejected(self):
        self.assert_rejected(lambda r: r["documented_historical_owners"][3].update(end_exclusive=16348160), "end_exclusive/end_hex")

    def test_changed_hex_address_rejected(self):
        self.assert_rejected(lambda r: r["documented_historical_owners"][0].update(start_hex="0x00114C01"), "start/start_hex")

    def test_candidate_hex_address_rejected(self):
        self.assert_rejected(lambda r: r["candidate_intervals"]["raw"].update(start_hex="0x12000001"), "start/start_hex")

    def test_malformed_hex_address_rejected(self):
        self.assert_rejected(lambda r: r["documented_historical_owners"][0].update(start_hex="invalid"), "start/start_hex")

    def test_false_runtime_implementation_claim_rejected(self):
        code, result = self.run_registry(mutate_contract=lambda contract: contract["input_frame_contract"].update(
            runtime_support_status="IMPLEMENTED"
        ))
        self.assertEqual(code, 1)
        self.assertEqual(result["checks"]["bgr888_runtime_support_fail_closed"]["status"], "FAIL")
        self.assertTrue(all(check["status"] == "PASS" for name, check in result["checks"].items()
                            if name != "bgr888_runtime_support_fail_closed"))

    def test_mailbox_code_cannot_be_cast_to_c_enum(self):
        code, result = self.run_registry(mutate_contract=lambda contract: contract["input_frame_contract"][
            "runtime_support"]["mailbox_numeric_encoding"].update(direct_cast_allowed=True)
        )
        self.assertEqual(code, 1)
        self.assertEqual(result["checks"]["bgr888_runtime_support_fail_closed"]["status"], "FAIL")
        self.assertTrue(all(check["status"] == "PASS" for name, check in result["checks"].items()
                            if name != "bgr888_runtime_support_fail_closed"))


if __name__ == "__main__":
    unittest.main()
