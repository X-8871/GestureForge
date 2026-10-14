"""覆盖 S2B tiny416 请求量复算中的 tile、padding 和 alias 规则。"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from verification.s2b_memory_request_budget import (
    MANIFEST_RELATIVE,
    MANIFEST_SHA256,
    ROOT,
    T66_ACCEPTANCE_RELATIVE,
    T66_ACCEPTANCE_SHA256,
    T66_LAYER0_REQUESTS,
    conv_tile_metrics,
    cycle_sensitivity,
    upsample_read_requests,
    validate_manifest,
)
from verification.test_s2a_conv_tile_cycle_budget import maxpool_read_bytes


class MemoryRequestBudgetTests(unittest.TestCase):
    """核对 tile feature 复用、权重重复、padding 和非卷积访问。"""

    def setUp(self) -> None:
        self.manifest_path = ROOT / MANIFEST_RELATIVE
        self.manifest_raw = self.manifest_path.read_bytes()
        self.assertEqual(hashlib.sha256(self.manifest_raw).hexdigest(), MANIFEST_SHA256)
        self.manifest = json.loads(self.manifest_raw.decode("utf-8"))

    def test_feature_patch_is_loaded_once_across_output_lane_groups(self) -> None:
        """同一空间 tile 的 feature patch 不因输出通道分组重读。"""
        metrics = conv_tile_metrics(
            [1, 3, 10, 9], [1, 10, 10, 9], [1, 1], [1, 1], [0, 0, 0, 0]
        )
        self.assertEqual(metrics.feature_read_requests, 270)
        self.assertEqual(metrics.mac_group_taps, 540)

    def test_weight_bytes_repeat_for_each_spatial_tile(self) -> None:
        """卷积权重按空间 tile 重读，尾部 lane group 只计有效输出通道。"""
        metrics = conv_tile_metrics(
            [1, 3, 10, 9], [1, 10, 10, 9], [1, 1], [1, 1], [0, 0, 0, 0]
        )
        self.assertEqual((metrics.tile_rows, metrics.tile_columns, metrics.spatial_tiles), (2, 2, 4))
        self.assertEqual(metrics.weight_read_requests, 10 * 3 * 4)

    def test_padding_scan_slots_do_not_become_feature_requests(self) -> None:
        """tile 会扫描 padding 坐标并填零，但只有输入边界内位置请求 HP0。"""
        metrics = conv_tile_metrics(
            [1, 1, 5, 5], [1, 1, 5, 5], [3, 3], [1, 1], [1, 1, 1, 1]
        )
        self.assertEqual(metrics.patch_scan_slots, 49)
        self.assertEqual(metrics.feature_read_requests, 25)
        self.assertEqual(metrics.padding_scan_slots, 24)
        self.assertEqual(metrics.mac_group_taps, 225)

    def test_upsample_reads_once_for_every_output_element(self) -> None:
        """2× nearest-repeat scheduler 每个输出坐标都发起一次源查询。"""
        reads = upsample_read_requests([1, 2, 2, 2], [1, 2, 4, 4], 2, "nearest_repeat", 1.0)
        self.assertEqual(reads, 32)
        self.assertEqual(reads, 4 * (1 * 2 * 2 * 2))

    def test_repeating_frozen_stall_vector_preserves_its_phase(self) -> None:
        """精确重复 TB 向量与连续 5.6 平均成本场景分别给出。"""
        result = cycle_sensitivity(96_135_961, 424_506_368, 11_382_150, 38, (0, 1, 2, 7, 3))
        scenarios = {row["name"]: row for row in result["scenarios"]}
        self.assertEqual(scenarios["frozen_tb_pattern_periodic_sequence"]["estimated_total_cycles"], 1_478_431_619)
        self.assertEqual(
            scenarios["continuous_average_at_frozen_tb_pattern_mean"]["estimated_total_cycles"],
            1_478_431_622,
        )

    def test_current_maxpool_count_uses_existing_valid_window_helper(self) -> None:
        """冻结 maxpool 的读请求继续调用 2A valid-window 统计 helper。"""
        row = self.manifest["layers"][9]
        self.assertEqual(maxpool_read_bytes(row), row["tensor_length_bytes"] * 4)

    def test_unknown_manifest_field_is_rejected(self) -> None:
        """descriptor 新增字段必须先扩展已审计的支持范围。"""
        changed = copy.deepcopy(self.manifest)
        changed["layers"][0]["unknown_request_mode"] = "burst"
        with self.assertRaisesRegex(ValueError, "unknown or missing fields"):
            validate_manifest(changed)

    def test_t66_layer0_matches_sha_bound_acceptance_reference(self) -> None:
        """从真实 layer0 descriptor 复算并与 T68 SHA 绑定记录交叉核对。"""
        rows = validate_manifest(self.manifest)
        record = rows[0]
        self.assertEqual(record["request_total"], T66_LAYER0_REQUESTS)
        self.assertEqual(record["write_requests"], 1_384_448)
        report_path = ROOT / T66_ACCEPTANCE_RELATIVE
        report_raw = report_path.read_bytes()
        self.assertEqual(hashlib.sha256(report_raw).hexdigest(), T66_ACCEPTANCE_SHA256)
        report = report_raw.decode("utf-8")
        self.assertIn(
            "report/evidence/S2A-T66/candidate999_t66_postfix_retry_20261008/simulation/simulation_execution_record.json",
            report,
        )
        self.assertIn("1b7bb9efcf4dc1f5ef0e920a28e5549888005cc2986e42158fc4adfca8e848b3", report)
        self.assertIn("2,551,955 请求与响应", report)

    def test_frozen_manifest_has_only_supported_tiny416_operations(self) -> None:
        """完整 frozen descriptor 的层数、字段和几何均在支持集合中。"""
        rows = validate_manifest(self.manifest)
        self.assertEqual(len(rows), 38)
        self.assertEqual(sum(row["request_total"] for row in rows), 96_135_961)


if __name__ == "__main__":
    unittest.main(verbosity=2)
