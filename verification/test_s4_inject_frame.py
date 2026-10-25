#!/usr/bin/env python3
"""阶段4 单帧注入通路的离线单元与集成测试。

覆盖地址图区间与缓存对齐、重叠负例、契约词表、来源/采集时间真值表、LCG payload、
严格状态字段，以及完整 host 与独立 C API 反例回归。

运行：cd <w4> && python -B -m unittest verification.test_s4_inject_frame -v
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import os
import uuid
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[1]
DRIVER = WORKTREE / "scripts" / "stage4_s4b" / "run_s4b_injection_offline.py"
MAP = WORKTREE / "docs" / "stage4" / "S4B_stage4_address_map.json"
CONTRACT = WORKTREE / "docs" / "stage4" / "s4b_shared_input_result_contract.json"
HEADER = WORKTREE / "vitis" / "stage4" / "s4_inject_frame.h"


def load_driver():
    """按路径加载离线驱动模块。"""
    spec = importlib.util.spec_from_file_location("s4b_injection_driver", DRIVER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def pairwise_overlaps(regions: list[dict]) -> list[tuple[str, str]]:
    """独立计算两两重叠（半开区间：start = max(base), end = min(end)）。"""
    overlaps = []
    for i in range(len(regions)):
        for j in range(i + 1, len(regions)):
            a, b = regions[i], regions[j]
            if max(a["base_addr"], b["base_addr"]) < min(a["end_addr_exclusive"], b["end_addr_exclusive"]):
                overlaps.append((a["name"], b["name"]))
    return overlaps


class AddressMapTests(unittest.TestCase):
    """地址图自洽性与重叠检测。"""

    def setUp(self) -> None:
        self.data = json.loads(MAP.read_text(encoding="utf-8"))
        self.regions = self.data["regions"]

    def test_regions_are_half_open_and_consistent(self) -> None:
        for region in self.regions:
            self.assertEqual(region["end_addr_exclusive"] - region["base_addr"], region["length_bytes"], region["name"])
            self.assertEqual(int(region["base_addr_hex"], 16), region["base_addr"], region["name"])

    def test_no_top_level_overlaps(self) -> None:
        self.assertEqual(pairwise_overlaps(self.regions), [])

    def test_hardware_line_and_maintenance_alignment_are_distinct(self) -> None:
        address_space = self.data["address_space"]
        self.assertEqual(address_space["hardware_cache_line_bytes"], 32)
        self.assertEqual(address_space["maintenance_alignment_bytes"], 64)
        self.assertIn("不代表物理缓存行大小", address_space["cache_line_basis"])

    def test_overlap_detector_catches_injected_overlap(self) -> None:
        mutated = [dict(r) for r in self.regions]
        injected = next(r for r in mutated if r["name"] == "injection_frame_rgb")
        gf8 = next(r for r in mutated if r["name"] == "gf8_weight_package")
        injected["base_addr"] = gf8["base_addr"]
        injected["end_addr_exclusive"] = gf8["base_addr"] + injected["length_bytes"]
        self.assertNotEqual(pairwise_overlaps(mutated), [], "负例未被检出：重叠检测可能失效")

    def test_driver_map_check_passes_and_detects_negative(self) -> None:
        driver = load_driver()
        result = driver.check_address_map(self.regions, self.data)
        self.assertEqual(result["status"], "PASS", result["problems"])
        self.assertTrue(result["negative_control"]["detected"])


class VocabularyTests(unittest.TestCase):
    """契约与实现词表一致性。"""

    def test_contract_bump_fails_closed_against_legacy_c_api(self) -> None:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        header = HEADER.read_text(encoding="utf-8")
        self.assertEqual(contract["contract_version"], "1.2.0")
        self.assertEqual(contract["revision"], "r06")
        self.assertEqual(contract["status"], "DRAFT_PENDING_REVIEW")
        self.assertEqual(contract["input_frame_contract"]["runtime_support_status"], "NOT_IMPLEMENTED")
        self.assertEqual(contract["input_frame_contract"]["runtime_support"]["mailbox_ps_driver"]["status"], "NOT_IMPLEMENTED")
        self.assertEqual(contract["input_frame_contract"]["runtime_support"]["pl_preprocessor"]["integration_status"], "NOT_INSTANTIATED")
        self.assertIn('#define S4_INJECT_CONTRACT_VERSION "s4-shared-io/1.1.0"', header)
        self.assertNotIn("S4_FMT_BGR888", header)

    def test_bgr888_and_platform_byte_order_are_separate(self) -> None:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        address_map = json.loads(MAP.read_text(encoding="utf-8"))
        raw_format = contract["input_source_profiles"]["raw_frame_format"]
        self.assertEqual(raw_format["pixel_format"], "BGR888")
        self.assertEqual(raw_format["channel_order"], ["B", "G", "R"])
        self.assertEqual(raw_format["byte_order"], "little")
        self.assertEqual(address_map["injection_point"]["region_name"], "raw_frame")
        self.assertEqual(address_map["injection_point"]["pixel_format"], "BGR888")
        self.assertEqual(address_map["injection_point"]["channel_order"], ["B", "G", "R"])
        self.assertEqual(address_map["injection_point"]["byte_order"], "little")
        self.assertEqual(address_map["status"], "DRAFT_PENDING_REVIEW")
        self.assertEqual(address_map["injection_point"]["runtime_support_status"], "NOT_IMPLEMENTED")

        runtime = contract["input_frame_contract"]["runtime_support"]
        mailbox_code = runtime["mailbox_numeric_encoding"]
        self.assertEqual(mailbox_code["field_name"], "mailbox_pixel_format_code")
        self.assertEqual(mailbox_code["candidate_value"], 1)
        self.assertEqual(mailbox_code["candidate_maps_to_pixel_format"], "BGR888")
        self.assertEqual(mailbox_code["current_c_enum_value_1"], "S4_FMT_RGB565")
        self.assertFalse(mailbox_code["direct_cast_allowed"])
        self.assertEqual(mailbox_code["mapping_implementation_status"], "NOT_IMPLEMENTED")

    def test_stage3_legacy_byte_order_maps_to_channel_order(self) -> None:
        """确认旧 Stage3 BGR 字段映射为像素通道语义。"""
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        mapping = contract["input_source_profiles"]["sensor_and_ddr_format"]["legacy_stage3_metadata_mapping"]
        self.assertEqual(mapping["legacy_field"], "source_byte_order")
        self.assertEqual(mapping["legacy_value"], "BGR")
        self.assertEqual(mapping["maps_to"], {
            "pixel_format": "BGR888", "channel_order": ["B", "G", "R"]
        })
        self.assertEqual(mapping["does_not_map_to"], "platform byte_order")

    def test_contract_source_capture_truth_table_is_exact(self) -> None:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        mapping = contract["input_frame_contract"]["vocabulary_mapping"]
        self.assertEqual(mapping["source_kind"]["map"], {
            "file_injection": "BOARD_INJECTION",
            "synthetic": "OFFLINE_REGRESSION",
            "camera": "CAMERA",
        })
        self.assertEqual(mapping["capture_time_truth_table"]["synthetic"], {
            "capture_time_available": False,
            "capture_time_ns": 0,
            "unavailable_fields_contains_capture_time_ns": True,
        })

    def test_no_contract_undefined_scope_value(self) -> None:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

        def collect_values(node, out):
            if isinstance(node, dict):
                for key, value in node.items():
                    if key in ("values", "allowed_values") and isinstance(value, list):
                        out.extend(str(v) for v in value)
                    collect_values(value, out)
            elif isinstance(node, list):
                for item in node:
                    collect_values(item, out)

        values: list[str] = []
        collect_values(contract, values)
        self.assertNotIn("INJECTION_ONLY", values)
        for rel in ("vitis/stage4/s4_inject_frame.h", "vitis/stage4/s4_inject_frame.c", "vitis/stage4/s4_inject_frame_host.c"):
            self.assertNotIn("INJECTION_ONLY", (WORKTREE / rel).read_text(encoding="utf-8"), rel)

    def test_payload_generator_matches_lcg(self) -> None:
        driver = load_driver()
        payload = driver.lcg_payload(1, 8)
        self.assertEqual(len(payload), 8)
        self.assertEqual(driver.lcg_payload(1, 8), payload)
        self.assertNotEqual(driver.lcg_payload(2, 8), payload)


class IntegrationTests(unittest.TestCase):
    """完整离线驱动集成。"""

    def test_offline_driver_passes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="s4b_inj_") as tmp:
            evidence = Path(tmp) / "evidence"
            run_id = f"s4fix_unittest_{uuid.uuid4().hex}"
            env = os.environ.copy()
            env["PYTHONUTF8"] = "1"
            env["PYTHONIOENCODING"] = "utf-8"
            proc = subprocess.run(
                [sys.executable, "-B", str(DRIVER), "--run-id", run_id, "--evidence-dir", str(evidence)],
                capture_output=True, env=env,
            )
            stdout = proc.stdout.decode("utf-8", errors="strict")
            stderr = proc.stderr.decode("utf-8", errors="strict")
            self.assertEqual(proc.returncode, 0, stdout[-4000:] + stderr[-2000:])
            summary = json.loads((evidence / "injection_offline_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["status"], "PASS")
            self.assertEqual(summary["counts"]["failed"], 0)
            self.assertEqual(summary["counts"]["host_direct_api_failures"], 0)
            self.assertGreaterEqual(summary["counts"]["host_direct_api_checks"], 20)
            self.assertTrue(summary["direct_c_api_test"]["matched"])
            self.assertEqual(
                summary["counts"]["host_direct_api_checks"],
                summary["direct_c_api_test"]["summary"]["checks"],
            )
            api_names = {row["check"] for row in summary["direct_c_api_test"]["checks"]}
            for name in (
                "invalid_initial_region_name_preserves_uninitialized_ring",
                "same_session_retry_after_initial_region_failure",
                "invalid_idle_ring_reset_preserves_ring_and_session",
            ):
                self.assertIn(name, api_names)
            if sys.maxsize > 0xFFFFFFFF:
                self.assertIn("64_bit_size_t_payload_length_branch_not_applicable", api_names)
                self.assertIn("64_bit_consumer_read_size_bounds_behavior_not_applicable", api_names)
                self.assertNotIn("32_bit_consumer_read_ddr_length_exceeds_size_t_rejected", api_names)
            else:
                self.assertIn("32_bit_consumer_read_ddr_length_exceeds_size_t_rejected", api_names)
            self.assertEqual(summary["direct_c_api_32bit"]["compile_only_status"], "PASS")
            self.assertEqual(summary["counts"]["direct_api_32bit_compile_units"], 2)
            self.assertEqual(
                summary["counts"]["direct_api_32bit_behavior"],
                summary["direct_c_api_32bit"]["behavioral_status"],
            )
            self.assertIn(summary["direct_c_api_32bit"]["behavioral_status"], ("PASS", "NOT_RUN"))
            self.assertEqual(summary["address_map"]["check"]["status"], "PASS")
            self.assertEqual(summary["build"]["exit_code"], 0)
            self.assertEqual(summary["build_warning_lines"], [])
            cases = {c["case"]: c for c in summary["cases"]}
            for name in ("single_frame_full", "queue_full_on_third_frame", "no_overwrite_held_slot",
                         "fault_forged_capture_time", "fault_measurement_scope", "fault_event_order",
                         "fault_consumer_timeout", "fault_duplicate_frame", "fault_overlap_before_write",
                         "fault_accept_10_then_9", "fault_release_out_of_order",
                         "fault_abort_before_stop_confirmation", "fault_skip_flush", "fault_skip_invalidate",
                         "fault_shift_invalidate", "fault_skip_barrier", "valid_synthetic_source",
                         "valid_camera_source", "fault_synthetic_capture_available",
                         "fault_camera_capture_missing", "fault_capture_trailing_junk", "fault_capture_empty",
                         "fault_capture_negative", "fault_capture_overflow", "fault_u32_width_overflow",
                         "fault_u32_frame_overflow", "fault_slot_overflow"):
                self.assertIn(name, cases)
                self.assertTrue(cases[name]["matched"], name)
                self.assertTrue(cases[name]["stable_status_field_reason_matched"], name)


if __name__ == "__main__":
    unittest.main()
