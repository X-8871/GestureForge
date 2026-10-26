#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 HUD 遮挡量化测试（离线；不接板卡、不联网）。

覆盖
====
1. 端到端：9 个（几何×布局）用例全部满足期望，且**面板交叉核验一致**；
2. **判别力（针对已修正的口径缺陷）**：落在 HUD 面板下的框必须报出 >0 遮挡；
   曾用 `A \\ B`（HUD 颜色同样"非背景"）会把它算成 ~0 —— 该用例必须能抓住这种退步；
3. 远离面板的框遮挡必须**恰为 0**（不得虚报）；
4. 阈值判定：`ratio <= limit ⇒ WITHIN_LIMIT`，否则 `EXCEEDS_LIMIT`；收紧阈值必须能把用例判为超限；
5. 面板法 == 逐像素差法（结构一致性）；`hud_pixels` > 0；
6. fail-open：缺 Pillow ⇒ `exit 1` 且 `passed=false`；
7. 无硬件依赖。
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.stage5_t03.s5t03_hud_occlusion as HO  # noqa: E402
import scripts.stage5_t03.s5t03_render as RD  # noqa: E402


class T_HudOcclusion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="s5t03_hud_")
        cls.out = pathlib.Path(cls.tmp.name) / "run"
        cls.code = HO.run(out_dir=cls.out, limit=HO.DEFAULT_LIMIT,
                          geometries=(HO.MG.GEOMETRIES[0], HO.MG.GEOMETRIES[1], HO.MG.GEOMETRIES[2]))
        cls.results = json.loads((cls.out / "results.json").read_text(encoding="utf-8"))
        cls.cases = {(c["geometry"], c["layout"]): c for c in cls.results["cases"]}

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_01_exit_and_case_count(self) -> None:
        self.assertEqual(self.code, 0, self.results["checks"])
        self.assertEqual(len(self.results["cases"]), 9)
        for case in self.results["cases"]:
            self.assertTrue(case["expectation_met"], f"{case['geometry']}/{case['layout']}")

    def test_02_boxes_are_actually_drawn(self) -> None:
        """回归：手写检测字典会被管线拒收（曾导致 total=0 的假通过），必须有真实框线像素。"""
        for case in self.results["cases"]:
            self.assertGreater(case["boxes"], 0, f"{case['geometry']}/{case['layout']}")
            self.assertGreater(case["border_pixels_total"], 100, f"{case['geometry']}/{case['layout']}")

    def test_03_under_hud_occlusion_is_detected(self) -> None:
        """判别力核心：面板下的框遮挡必须 >0（用 `A\\B` 的错误口径会被算成 ~0）。"""
        for geometry in ("landscape_1280x720", "portrait_720x1280", "oddw_683x384"):
            case = self.cases[(geometry, "top_left_under_hud")]
            self.assertGreater(case["border_pixels_occluded"], 100, geometry)
            self.assertGreater(case["occlusion_ratio"], 0.5, geometry)
            self.assertEqual(case["verdict"], "EXCEEDS_LIMIT", geometry)

    def test_04_far_box_has_zero_occlusion(self) -> None:
        """远端框不得虚报遮挡。"""
        for geometry in ("landscape_1280x720", "portrait_720x1280", "oddw_683x384"):
            case = self.cases[(geometry, "far_bottom_right")]
            self.assertEqual(case["border_pixels_occluded"], 0, geometry)
            self.assertEqual(case["occlusion_ratio"], 0.0, geometry)
            self.assertEqual(case["verdict"], "WITHIN_LIMIT", geometry)

    def test_05_panel_and_pixel_methods_agree(self) -> None:
        """两种独立口径（逐像素差 vs 面板矩形）必须一致；HUD 像素集非空。"""
        for case in self.results["cases"]:
            self.assertTrue(case["methods_consistent"], f"{case['geometry']}/{case['layout']}")
            self.assertEqual(case["panel_method_pixels"], case["border_pixels_occluded"])
            self.assertGreater(case["hud_pixels"], 0, case["geometry"])
            self.assertIsNotNone(case["hud_panel_px"])

    def test_06_threshold_verdict_is_live(self) -> None:
        """阈值必须真正参与判定：把 limit 收到 0 后，同布局必须全部 EXCEEDS_LIMIT。"""
        with tempfile.TemporaryDirectory(prefix="s5t03_hud0_") as tmp:
            out = pathlib.Path(tmp) / "run"
            code = HO.run(out_dir=out, limit=0.0,
                          geometries=(HO.MG.GEOMETRIES[0],))
            results = json.loads((out / "results.json").read_text(encoding="utf-8"))
            self.assertEqual(code, 0)
            by_layout = {c["layout"]: c for c in results["cases"]}
            self.assertEqual(by_layout["top_left_under_hud"]["verdict"], "EXCEEDS_LIMIT")
            self.assertEqual(by_layout["far_bottom_right"]["verdict"], "WITHIN_LIMIT")  # 0 <= 0 仍通过
            self.assertEqual(results["limit"]["value"], 0.0)

    def test_07_artifacts_and_binding(self) -> None:
        for rel in ("results.json", "manifest.json"):
            self.assertTrue((self.out / rel).is_file())
        self.assertTrue(list((self.out / "keyframes").glob("*.png")))
        manifest = json.loads((self.out / "manifest.json").read_text(encoding="utf-8"))
        for role, entry in manifest["tools"].items():
            path = REPO_ROOT / entry["path"]
            self.assertTrue(path.is_file(), role)
            self.assertEqual(HO.sha256_file(path), entry["sha256"], role)

    def test_08_honest_labels(self) -> None:
        """诚实标注：阈值是离线口径（非验收指标）；真实回放/板上 NOT_RUN；PNG 非权威。"""
        limit = self.results["limit"]
        self.assertIn("非", limit["semantics"])
        self.assertEqual(self.results["input_scope_label"], "synthetic_replay")
        self.assertEqual(self.results["status"], "PRELIMINARY")
        self.assertTrue(any("真实回放" in item for item in self.results["not_run"]))
        self.assertTrue(any("板上" in item for item in self.results["not_run"]))
        self.assertTrue(any("JSON 为权威" in item for item in self.results["limitations"]))

    def test_09_missing_pillow_is_failure(self) -> None:
        original = RD.PIL_AVAILABLE
        try:
            RD.PIL_AVAILABLE = False
            with tempfile.TemporaryDirectory(prefix="s5t03_hud_nopil_") as tmp:
                out = pathlib.Path(tmp) / "run"
                code = HO.run(out_dir=out, limit=HO.DEFAULT_LIMIT,
                              geometries=(HO.MG.GEOMETRIES[2],))
                results = json.loads((out / "results.json").read_text(encoding="utf-8"))
                self.assertEqual(code, 1)
                self.assertFalse(results["checks"]["passed"])
                self.assertTrue(any("render_unavailable" in item for item in results["checks"]["failures"]))
        finally:
            RD.PIL_AVAILABLE = original

    def test_10_no_hardware_dependency(self) -> None:
        source = (REPO_ROOT / "scripts/stage5_t03/s5t03_hud_occlusion.py").read_text(encoding="utf-8").lower()
        for forbidden in ("import serial", "import pyvisa", "import usb", '["hw_server"',
                          '["xsdb"', '["vivado"', '["xsct"'):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main(verbosity=2)