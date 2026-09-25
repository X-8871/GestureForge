"""验证 T27 layer33 shell-child pilot 的来源、黄金和 memory map。"""

from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from verification import s2a_runtime_layer33_pilot as pilot


class RuntimeLayer33PilotTests(unittest.TestCase):
    """检查 T27 固定输入、contract 和可执行仿真依赖。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.hashes, cls.manifest, cls.contract, cls.descriptor = pilot._verify_frozen_bindings()

    def test_all_frozen_sources_match_pins(self) -> None:
        """冻结 G0、T10、T12、T18 与 T22 源哈希应一致。"""
        self.assertEqual(len(self.hashes), len(pilot._PINNED_HASHES) + 4)
        for relative, expected in pilot._PINNED_HASHES.items():
            self.assertEqual(self.hashes[relative], expected)

    def test_hash_mutation_fails_closed(self) -> None:
        """错误来源摘要必须被 fail-closed 拒绝。"""
        with self.assertRaisesRegex(AssertionError, "SHA-256 不匹配"):
            pilot._assert_pinned_hash("mutated source", "0" * 64, "1" * 64)

    def test_manifest_and_t22_layer33_fields_agree(self) -> None:
        """G0 manifest 与 T22 必须共同描述 layer33 地址、形状和 nearest-repeat。"""
        self.assertEqual(self.descriptor["cfg_section"], 34)
        self.assertEqual(self.descriptor["input_address"], 27598336)
        self.assertEqual(self.descriptor["input_length_bytes"], 21632)
        self.assertEqual(self.descriptor["input_shape_nchw"], [1, 128, 13, 13])
        self.assertEqual(self.descriptor["output_address"], 27619968)
        self.assertEqual(self.descriptor["output_length_bytes"], 86528)
        self.assertEqual(self.descriptor["output_shape_nchw"], [1, 128, 26, 26])
        self.assertEqual(self.descriptor["method"], "nearest_repeat")
        self.assertEqual(self.descriptor["stride"], 2)

    def test_t22_single_terminal_event_is_required(self) -> None:
        """多周期或有 backpressure 的 completion 语义必须拒绝。"""
        malformed = copy.deepcopy(self.contract)
        malformed["dispatch_protocol"]["completion_event"]["pulse_cycles"] = 2
        with self.assertRaisesRegex(AssertionError, "timeout 或单周期终态事件"):
            pilot._layer33_descriptor(self.manifest, malformed)

    def test_independent_t10_nearest_repeat_golden(self) -> None:
        """Python oracle 应重现 T18 冻结输入与完整输出摘要。"""
        input_bytes, output_bytes = pilot._materialize_golden(self.descriptor)
        self.assertEqual(len(input_bytes), 21632)
        self.assertEqual(pilot._sha256_bytes(input_bytes),
                         "e4a755bd4b0e34607c3d245adc640aaf427e1f6d2a25f1cd39a33fb9bb51abcb")
        self.assertEqual(len(output_bytes), 86528)
        self.assertEqual(pilot._sha256_bytes(output_bytes),
                         "39d1494ec1dfa28846aebfd56bff2396c5610c60873c99cae6186d8f3ea4a9ab")

    def test_manifest_memory_ranges_are_derived_and_sorted(self) -> None:
        """T10 range 文件应由 manifest 派生并包含 36 个非 alias 张量。"""
        with tempfile.TemporaryDirectory(prefix="s2a_t27_ranges_") as temporary:
            work = Path(temporary)
            digest, count = pilot._write_memory_ranges(self.manifest, work)
            payload = (work / "memory_ranges.dat").read_bytes()
        self.assertEqual(count, 36)
        self.assertEqual(digest, pilot._sha256_bytes(payload))
        rows = payload.decode("ascii").splitlines()
        self.assertEqual(int(rows[0].split()[-1], 16), 36)
        self.assertEqual(len(rows), 37)

    def test_wrapper_and_testbench_bind_expected_cancel_path(self) -> None:
        """wrapper 与 testbench 必须显式覆盖 G0 cancel 和 child terminal。"""
        wrapper = (pilot._ROOT / pilot._WRAPPER).read_text(encoding="utf-8")
        testbench = (pilot._ROOT / pilot._TB).read_text(encoding="utf-8")
        self.assertIn("hard_reset || backend_abort || soft_reset_now", wrapper)
        self.assertIn("child_done || child_error", wrapper)
        self.assertIn("u_runtime_shell.cancel_master", testbench)
        self.assertIn("wait_pending_write", testbench)
        self.assertIn("terminal_event_count != 1", testbench)


if __name__ == "__main__":
    unittest.main()
