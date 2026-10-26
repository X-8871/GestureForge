#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 多几何渲染测试（离线；不接板卡、不联网）。

覆盖
====
1. 四种几何（1280×720 / 720×1280 / 683×384 / 683×384→1920×1080 k=2）**逐像素**与冻结参考一致；
2. 冻结几何数值（奇数补边 91/92 非对称；canvas_fit k=2 / 1366×768 / offset(277,156)）；
3. **映射函数判别**：画布-fit 必须用 `original_norm_to_canvas_px`；误用 exact 映射像素不同（有用例锁死）；
4. 产物/绑定/诚实标注（NOT_RUN 含真实回放与板上；声明不代表板级 HDMI 时序）；
5. fail-open：缺 Pillow ⇒ `exit 1` + `passed=false`；
6. 无硬件依赖。
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

import scripts.stage5_t03.s5t03_multi_geometry_render as MG  # noqa: E402
import scripts.stage5_t03.s5t03_render as RD  # noqa: E402
import verification.s5_display_geometry_reference as R  # noqa: E402

PARAMS = MG.load_params()
SEED = int(PARAMS["newly_frozen_for_skeleton_only"]["seed"])


class T_MultiGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="s5t03_mg_")
        cls.out = pathlib.Path(cls.tmp.name) / "run"
        cls.code = MG.run(out_dir=cls.out, seed=SEED)
        cls.results = json.loads((cls.out / "results.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((cls.out / "manifest.json").read_text(encoding="utf-8"))
        cls.by_id = {g["id"]: g for g in cls.results["geometries"]}

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_01_exit_and_all_geometries_pixel_exact(self) -> None:
        """四种几何都必须 exit 0 且**逐像素**与参考一致（missing/extra 均为 0）。"""
        self.assertEqual(self.code, 0, self.results["checks"])
        self.assertEqual(len(self.results["geometries"]), 4)
        for geometry in self.results["geometries"]:
            a = geometry["assertions"]
            self.assertTrue(a.get("rendered_pixels_equal_reference"), geometry["id"])
            self.assertEqual(a.get("missing_px"), 0, geometry["id"])
            self.assertEqual(a.get("extra_px"), 0, geometry["id"])
            self.assertGreater(a.get("rendered_pixels"), 0, geometry["id"])

    def test_02_frozen_geometry_numbers(self) -> None:
        """奇数补边与整数倍画布的冻结数值（与参考函数逐值一致）。"""
        odd = R.letterbox_geometry(683, 384)
        fit = R.canvas_fit(683, 384, 1920, 1080)
        self.assertEqual((odd["new_width"], odd["new_height"]), (416, 233))
        self.assertEqual((odd["offset_x"], odd["offset_y"]), (0, 91))
        self.assertEqual(odd["pad_bottom"], 92)
        self.assertTrue(odd["asymmetric_padding"])
        self.assertEqual((fit["scale_k"], fit["drawn_width"], fit["drawn_height"]), (2, 1366, 768))
        self.assertEqual((fit["offset_x"], fit["offset_y"]), (277, 156))
        for name, ok in self.results["numeric_checks"].items():
            self.assertTrue(ok, name)
        self.assertEqual(self.results["canvas_fit"], fit)

    def test_03_canvas_fit_mapping_is_not_exact_mapping(self) -> None:
        """画布-fit 必须用 `original_norm_to_canvas_px`（误用 exact 映射 → 像素不同）。"""
        item = self.by_id["canvas_683x384_k2_1920x1080"]
        self.assertTrue(item["exact_vs_canvas_fit_differ"], "两种映射必须给出不同像素")
        detections = MG.build_detections()
        fit = R.canvas_fit(683, 384, 1920, 1080)
        for detection, box in zip(detections, item["boxes"]):
            self.assertEqual(dict(box["px"]), dict(R.original_norm_to_canvas_px(detection["xyxy"], fit)))

    def test_04_pixel_sets_recomputed_independently(self) -> None:
        """独立复算：每个几何的渲染像素集合 == `R.border_pixel_sets` 并集（不信 results 自述）。"""
        if not RD.PIL_AVAILABLE:
            self.skipTest("Pillow 不可用")
        background_rgb = (9, 9, 9)
        for geometry in self.results["geometries"]:
            width, height = geometry["canvas"]
            background = RD.Image.new("RGB", (width, height), background_rgb)
            decision = MG._decision_from_boxes(geometry["boxes"], (width, height))
            font, _ = RD.load_font(RD.font_size_px(height))
            image, _ = RD.render_frame(decision, canvas_width=width, canvas_height=height,
                                       background=background, hud=None, font=font,
                                       draw_hud=False, draw_labels=False)
            pixels = image.load()
            rendered = {(x, y) for x in range(width) for y in range(height) if pixels[x, y] != background_rgb}
            expected: set[tuple[int, int]] = set()
            for box in geometry["boxes"]:
                px = box["px"]
                expected |= set(R.border_pixel_sets(int(px["x1"]), int(px["y1"]), int(px["x2"]),
                                                    int(px["y2"]), R.DISPLAY_LINE_WIDTH_PX, width, height))
            self.assertEqual(rendered, expected, geometry["id"])

    def test_05_artifacts_binding_and_honesty(self) -> None:
        """产物齐全、工具哈希一致、诚实标注齐备。"""
        for rel in ("results.json", "manifest.json"):
            self.assertTrue((self.out / rel).is_file())
        keyframes = list((self.out / "keyframes").glob("*.png"))
        self.assertEqual(len(keyframes), 8, "每个几何 2 张（overlay + border_only）")
        for name, entry in self.manifest["tools"].items():
            path = REPO_ROOT / entry["path"]
            if path.is_file():
                self.assertEqual(MG.sha256_file(path), entry["sha256"], name)
        self.assertEqual(self.results["input_scope_label"], "synthetic_replay")
        self.assertEqual(self.results["status"], "PRELIMINARY")
        self.assertTrue(any("真实回放" in item for item in self.results["not_run"]))
        self.assertTrue(any("板上" in item for item in self.results["not_run"]))
        self.assertTrue(any("HDMI" in item or "时序" in item for item in self.results["limitations"]))

    def test_06_no_hardware_dependency(self) -> None:
        source = (REPO_ROOT / "scripts/stage5_t03/s5t03_multi_geometry_render.py").read_text(
            encoding="utf-8").lower()
        for forbidden in ("import serial", "import pyvisa", "import usb", '["hw_server"',
                          '["xsdb"', '["vivado"', '["xsct"'):
            self.assertNotIn(forbidden, source)

    def test_07_missing_pillow_is_failure(self) -> None:
        """fail-open 关闭：缺 Pillow ⇒ `exit 1` + `passed=false`。"""
        original = RD.PIL_AVAILABLE
        try:
            RD.PIL_AVAILABLE = False
            with tempfile.TemporaryDirectory(prefix="s5t03_mg_nopil_") as tmp:
                out = pathlib.Path(tmp) / "run"
                code = MG.run(out_dir=out, seed=SEED)
                results = json.loads((out / "results.json").read_text(encoding="utf-8"))
                self.assertEqual(code, 1)
                self.assertFalse(results["checks"]["passed"])
                self.assertTrue(any("render_unavailable" in item for item in results["checks"]["failures"]))
        finally:
            RD.PIL_AVAILABLE = original


if __name__ == "__main__":
    unittest.main(verbosity=2)