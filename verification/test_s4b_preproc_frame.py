"""验证整帧PL仿真fixture及独立D2黄金边界。"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from verification import run_s4b_preproc_frame as frame


class S4BPreprocFrameFixtureTests(unittest.TestCase):
    """检查fixture、几何布局、量化边界与地址范围。"""

    @classmethod
    def setUpClass(cls) -> None:
        """将测试临时文件限制在调用者提供的w4 RunId。"""
        temp_value = os.environ.get("TEMP")
        if not temp_value:
            raise RuntimeError("测试要求TEMP指向本任务w4隔离目录")
        temp_root = Path(temp_value)
        if not temp_root.is_absolute() or not temp_root.is_dir():
            raise RuntimeError("TEMP必须是已存在的绝对目录")
        if "S4B-PL-FRAME-01" not in str(temp_root):
            raise RuntimeError("TEMP必须位于本任务隔离RunId目录下")
        cls._temporary = tempfile.TemporaryDirectory(prefix="frame_fixtures_", dir=temp_root)
        cls.output_dir = Path(cls._temporary.name)
        cls.manifest = frame.build_fixtures(cls.output_dir)
        cls.cases = cls.manifest["cases"]

    @classmethod
    def tearDownClass(cls) -> None:
        """只清理本测试创建的隔离临时目录。"""
        cls._temporary.cleanup()

    def test_frozen_d2_and_geometry_builder_are_bound(self) -> None:
        """fixture必须绑定指定D2源码及几何元数据生成器。"""
        self.assertEqual(self.manifest["d2_reference_sha256"], frame.EXPECTED_D2_SHA256)
        self.assertEqual(self.manifest["geometry_base"], frame.EXPECTED_GEOMETRY_BASE)
        self.assertEqual(self.manifest["numeric_base"], frame.EXPECTED_NUMERIC_BASE)
        self.assertRegex(self.manifest["geometry_builder_sha256"], r"^[0-9a-f]{64}$")

    def test_same_size_fixture_uses_chw_and_aligned_regions(self) -> None:
        """同尺寸样例输出长度、CHW平面及地址基址符合描述符。"""
        case = self.cases[0]
        self.assertEqual(case["name"], "same_size_4x4")
        self.assertEqual(case["expected_bytes"], 4 * 4 * 3)
        descriptor = case["descriptor"]
        self.assertEqual(descriptor[:10], [4, 4, 12, 48, 48, 48, 4, 4, 0, 0])
        self.assertTrue(all(address % 8 == 0 for address in descriptor[10:14]))
        expected = bytes.fromhex(
            "".join(line.strip() for line in (self.output_dir / "expected_small_same.hex").read_text().splitlines())
        )
        self.assertEqual(hashlib.sha256(expected).hexdigest(), case["expected_sha256"])

    def test_axis_one_metadata_selects_the_last_source_index(self) -> None:
        """新轴长为1的D2分支必须落到源末端，且仅活动项有内容。"""
        case = self.cases[1]
        self.assertEqual(case["name"], "axis_one_letterbox_1x3_to_4x4")
        self.assertEqual(case["new_size"], {"width": 1, "height": 4})
        self.assertEqual(case["padding"]["left"], 1)
        descriptor = case["descriptor"]
        self.assertEqual(descriptor[6:10], [1, 4, 1, 0])
        self.assertEqual(case["expected_bytes"], 48)

    def test_large_prefix_contains_padding_and_real_d2_boundary(self) -> None:
        """202×329案例的通道0前88字节含80个64补边及x81量化100。"""
        case = self.cases[2]
        self.assertEqual(case["name"], "boundary_202x329_to_416_prefix")
        self.assertEqual(case["new_size"], {"width": 255, "height": 416})
        self.assertEqual(case["padding"]["left"], 80)
        self.assertEqual(self.manifest["boundary_prefix"]["bytes"], 88)
        self.assertEqual(self.manifest["boundary_prefix"]["x81_value"], 100)
        prefix_lines = (self.output_dir / "expected_large_prefix88.hex").read_text().splitlines()
        prefix = bytes(int(line, 16) for line in prefix_lines)
        self.assertEqual(prefix[:80], bytes([64] * 80))
        self.assertEqual(prefix[81], 100)
        self.assertEqual(hashlib.sha256(prefix).hexdigest(), self.manifest["boundary_prefix"]["sha256"])

    def test_table_capacity_is_padded_with_zero_and_memory_size_is_exact(self) -> None:
        """固定416槽表的未活动项保持零，仿真内存镜像覆盖声明地址。"""
        memory_path = self.output_dir / "memory.hex"
        self.assertEqual(self.manifest["memory_words"], frame.MEMORY_WORDS)
        self.assertEqual(len(memory_path.read_text(encoding="ascii").splitlines()), frame.MEMORY_WORDS)
        self.assertEqual(self.manifest["memory_sha256"], hashlib.sha256(memory_path.read_bytes()).hexdigest())
        self.assertEqual(json.loads((self.output_dir / "fixtures.json").read_text(encoding="utf-8"))["status"],
                         "FIXTURES_PREPARED_NOT_SIMULATED")


if __name__ == "__main__":
    unittest.main()
