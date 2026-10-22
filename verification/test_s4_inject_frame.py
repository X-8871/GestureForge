#!/usr/bin/env python3
"""阶段4 单帧注入通路（4-B）的离线单元/集成测试。

覆盖：
  1. 地址图区间自洽与两两不相交（独立实现，不复用驱动结论）；
  2. 负例：人为制造重叠必须被检出（证明检查不是恒真）；
  3. payload 生成器与 host 一致（LCG 复现）；
  4. 契约版本一致性：C 头 `S4_INJECT_CONTRACT_VERSION` == 契约 JSON `contract_version`；
  5. 契约词表一致：源码不得出现契约未定义的 `INJECTION_ONLY`；
  6. 集成：跑完整离线驱动，断言 exit 0 且 summary.status == PASS。

运行：cd <w4> && python -m unittest verification.test_s4_inject_frame -v
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
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

    def test_contract_version_matches_header(self) -> None:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        header = HEADER.read_text(encoding="utf-8")
        expected = f'{contract["contract_id"]}/{contract["contract_version"]}'
        self.assertIn(f'#define S4_INJECT_CONTRACT_VERSION "{expected}"', header)

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
            proc = subprocess.run(
                [sys.executable, "-B", str(DRIVER), "--run-id", "unittest_offline", "--evidence-dir", str(evidence)],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            self.assertEqual(proc.returncode, 0, proc.stdout[-4000:] + proc.stderr[-2000:])
            summary = json.loads((evidence / "injection_offline_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["status"], "PASS")
            self.assertEqual(summary["counts"]["failed"], 0)
            self.assertEqual(summary["address_map"]["check"]["status"], "PASS")
            self.assertEqual(summary["build"]["exit_code"], 0)
            self.assertEqual(summary["build_warning_lines"], [])
            cases = {c["case"]: c for c in summary["cases"]}
            for name in ("single_frame_full", "queue_full_on_third_frame", "no_overwrite_held_slot",
                         "fault_forged_capture_time", "fault_measurement_scope", "fault_event_order",
                         "fault_consumer_timeout", "fault_duplicate_frame"):
                self.assertIn(name, cases)
                self.assertTrue(cases[name]["matched"], name)


if __name__ == "__main__":
    unittest.main()