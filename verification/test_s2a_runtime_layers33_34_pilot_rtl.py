"""验证 S2A-T28 固定 layer33→34 runtime shell 集成规格与黄金生成。"""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from verification import s2a_runtime_layers33_34_pilot as pilot


class RuntimeLayers33To34PilotTests(unittest.TestCase):
    """检查冻结来源、相邻层契约、seeded golden 和仿真覆盖代码。"""

    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.hashes,
            cls.manifest,
            cls.contract,
            cls.t18,
            cls.t19,
            cls.descriptors,
        ) = pilot._verify_sources()

    def test_frozen_sources_and_evidence_hashes_match(self) -> None:
        """固定 G0/T10/T12/T18/T19/T22/T27 来源需逐项匹配摘要。"""
        self.assertEqual(len(self.hashes), len(pilot._PINNED_HASHES) + 4)
        for name, expected in pilot._PINNED_HASHES.items():
            self.assertEqual(self.hashes[name], expected)

    def test_manifest_and_contract_describe_layer33_then_route34(self) -> None:
        """两层规格需固定 NCHW shape、address、length 和 route ref 顺序。"""
        layer33 = self.descriptors["layer33"]
        layer34 = self.descriptors["layer34"]
        self.assertEqual(layer33["input_address"], 27598336)
        self.assertEqual(layer33["input_length_bytes"], 21632)
        self.assertEqual(layer33["output_address"], 27619968)
        self.assertEqual(layer33["output_shape_nchw"], [1, 128, 26, 26])
        self.assertEqual(layer34["source_order"], [33, 23])
        self.assertEqual(layer34["source_addresses"], [27619968, 26727936])
        self.assertEqual(layer34["source_lengths_bytes"], [86528, 173056])
        self.assertEqual(layer34["output_address"], 27706496)
        self.assertEqual(layer34["output_length_bytes"], 259584)
        self.assertEqual(layer34["source_q31_multipliers"], [1959924335, 2147483648])

    def test_route_uses_ordered_per_reference_scales(self) -> None:
        """route 的权威 scale 与 shape 必须和 cfg ref 顺序一一对应。"""
        manifest = copy.deepcopy(self.manifest)
        contract = copy.deepcopy(self.contract)
        manifest["layers"][34]["input_scale"] = 9.25
        pilot._validate_contract(manifest, contract, self.t18, self.t19)

        manifest = copy.deepcopy(self.manifest)
        manifest["layers"][34]["input_scales"] = list(
            reversed(manifest["layers"][34]["input_scales"])
        )
        with self.assertRaisesRegex(AssertionError, "per-ref scale"):
            pilot._validate_contract(manifest, copy.deepcopy(self.contract), self.t18, self.t19)

        contract = copy.deepcopy(self.contract)
        route_inputs = contract["network_dispatch"]["layers"][34][
            "input_tensors_in_manifest_order"
        ]
        route_inputs[0], route_inputs[1] = route_inputs[1], route_inputs[0]
        with self.assertRaisesRegex(AssertionError, "ref 顺序/per-ref scale"):
            pilot._validate_contract(copy.deepcopy(self.manifest), contract, self.t18, self.t19)

    def test_t22_global_deadline_and_terminal_event_are_frozen(self) -> None:
        """T22 必须保留单一全任务 deadline 和单周期无反压 terminal。"""
        malformed = copy.deepcopy(self.contract)
        malformed["dispatch_protocol"]["global_timeout"][
            "per_layer_timeout_restart_allowed"
        ] = True
        with self.assertRaisesRegex(AssertionError, "global deadline / single terminal"):
            pilot._validate_contract(self.manifest, malformed, self.t18, self.t19)

    def test_seeded_inputs_and_both_layer_goldens_are_deterministic(self) -> None:
        """固定 seed 必须重现两输入和 layer33/layer34 完整输出。"""
        first = pilot._materialize_golden(
            self.descriptors["layer33"], self.descriptors["layer34"]
        )
        second = pilot._materialize_golden(
            self.descriptors["layer33"], self.descriptors["layer34"]
        )
        self.assertEqual(first, second)
        self.assertEqual(first["seed"], 0x2A202609)
        self.assertEqual(len(first["layer32_input"]), 21632)
        self.assertEqual(len(first["layer23_input"]), 173056)
        self.assertEqual(len(first["layer33_expected"]), 86528)
        self.assertEqual(len(first["layer34_expected"]), 259584)
        self.assertEqual(
            first["layer32_sha256"],
            "b802ea6dd78029bd9a1c90a5dc752e94f9f4818dab4998886f96e2b404dd294a",
        )
        self.assertEqual(
            first["layer23_sha256"],
            "bd4dd681d43f218257d159517966eef69388dd8aa65d78db4728d885fd589a04",
        )
        self.assertEqual(
            first["layer33_sha256"],
            "d18340a742d1d4bddf1598ee946bf9f67dff21e75f5567d902880969b37f8c25",
        )
        self.assertEqual(
            first["layer34_sha256"],
            "098c977fa4d0aa8ab0bae4b3030d4cc712c71728ef2d9cf41c2da4b56454939f",
        )
        self.assertNotIn(0x80, first["layer32_input"])
        self.assertNotIn(0x80, first["layer23_input"])
        self.assertEqual(
            first["layer34_expected"][128 * 26 * 26 :], first["layer23_input"]
        )

    def test_q31_rounding_matches_frozen_half_away_reference(self) -> None:
        """T19 Q31 整数舍入需覆盖全部有效 signed INT8 值。"""
        source0_ratio = 0.145512708528774 / 0.1594378704161156
        source1_ratio = 1.0
        for value in range(-127, 128):
            self.assertEqual(
                pilot._requantize_q31(value, 1959924335),
                pilot._requantize_float_reference(value, source0_ratio),
            )
            self.assertEqual(
                pilot._requantize_q31(value, 2147483648),
                pilot._requantize_float_reference(value, source1_ratio),
            )

    def test_feature_ranges_are_manifest_derived(self) -> None:
        """地址范围证据应由完整 manifest 计算出 36 个无重叠区间。"""
        with tempfile.TemporaryDirectory(prefix="s2a_t28_ranges_") as temporary:
            work = Path(temporary)
            digest, count = pilot._write_memory_ranges(self.manifest, work)
            payload = (work / "memory_ranges.dat").read_bytes()
        self.assertEqual(count, 36)
        self.assertEqual(digest, pilot._sha256_bytes(payload))
        rows = payload.decode("ascii").splitlines()
        self.assertEqual(int(rows[0].split()[-1], 16), 36)
        self.assertEqual(len(rows), 37)

    def test_source_hash_guard_accepts_unchanged_snapshot(self) -> None:
        """编译前后源码摘要相同时应允许正常写出结果。"""
        snapshot = {"rtl.sv": "a" * 64, "input.json": "b" * 64}
        pilot._assert_source_snapshot_equal(snapshot, dict(snapshot), "unit test")

    def test_source_hash_change_refuses_pass_evidence(self) -> None:
        """运行期间源码变化时必须拒绝 PASS evidence 且不能创建文件。"""
        before = {"rtl.sv": "a" * 64}
        after = {"rtl.sv": "c" * 64}
        with tempfile.TemporaryDirectory(prefix="s2a_t28_hash_guard_") as temporary:
            evidence = Path(temporary) / "result.json"
            with self.assertRaisesRegex(AssertionError, "source hash snapshot changed"):
                pilot._write_verified_evidence(
                    evidence, {"result": "PASS"}, before, after
                )
            self.assertFalse(evidence.exists())

    def test_source_hash_guard_writes_evidence_after_match(self) -> None:
        """源码摘要一致时 evidence 文件可按 UTF-8 JSON 写出。"""
        snapshot = {"rtl.sv": "a" * 64}
        result = {"result": "PASS", "source_bindings": snapshot}
        with tempfile.TemporaryDirectory(prefix="s2a_t28_hash_guard_") as temporary:
            evidence = Path(temporary) / "result.json"
            payload = pilot._write_verified_evidence(
                evidence, result, snapshot, dict(snapshot)
            )
            self.assertEqual(evidence.read_bytes(), payload)
            self.assertEqual(json.loads(evidence.read_text(encoding="utf-8")), result)

    def test_tb_asserts_order_cancel_and_direct_memory_protocol(self) -> None:
        """新 TB 应真实执行 route 顺序、稳定握手与取消检查。"""
        wrapper = (pilot._ROOT / pilot._WRAPPER).read_text(encoding="utf-8")
        testbench = (pilot._ROOT / pilot._TB).read_text(encoding="utf-8")
        self.assertIn("hard_reset || backend_abort || soft_reset_now", wrapper)
        self.assertIn("layer33_done", wrapper)
        self.assertIn("layer34_done", wrapper)
        self.assertIn("backpressure 期间 memory request 字段变化", testbench)
        self.assertIn("route source0 顺序/初始化错误", testbench)
        self.assertIn("global_timeout abort=1 route_starts=0", testbench)
        self.assertIn("while ((active_stage != 2'd2) || (layer34_start_count == 0))", testbench)
        self.assertIn("CHECK layer33_boundary terminal_events=%0d", testbench)
        self.assertIn("quick_boundary_reset terminal_events=0 late_side_effects=0", testbench)
        self.assertIn("hard_reset pending_write=1 late_side_effects=0", testbench)
        self.assertIn("soft_reset pending_write=1 late_side_effects=0", testbench)
        self.assertIn("terminal_event_count != 1", testbench)


if __name__ == "__main__":
    unittest.main()
