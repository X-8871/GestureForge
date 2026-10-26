#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 离线**长跑回放**测试（小样本端到端 + 判据算术；不接板卡、不联网）。

覆盖要点
========
1. 端到端产物齐全（`results.json` / `frame_assertions.jsonl.gz` / `logs/events_*.jsonl.gz` / `keyframes/` / `manifest.json`）；
2. **硬不变量**：每帧恰好一次提交事件（无死锁）、时间戳单调、计数可复算、断言覆盖全部帧；
3. **诚实标注**：小样本**不得**声称"≥30 分钟"（`canonical_long_run=false` 且软判据为 `null`）；
4. 规范帧数的判据算术（`period_count × period ≥ 1.8e12`，余量 < 1 周期）——纯算术，不跑 10 万帧；
5. 过期边界三例（渲染路径）PASS；`demo` 未请求时显式 `NOT_RUN` 且 `demo_only`；
6. 无硬件依赖（不引入 serial/hw_server/xsdb/vivado 调用）。
"""

from __future__ import annotations

import gzip
import json
import pathlib
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.stage5_t03.s5t03_long_run_replay as LR  # noqa: E402
import verification.s5_display_geometry_reference as R  # noqa: E402

PARAMS = LR.load_params()
FROZEN = PARAMS["newly_frozen_for_skeleton_only"]
SEED = int(FROZEN["seed"])
CANON_FRAMES = int(FROZEN["long_run_min_frames"])
PERIOD_NS = int(FROZEN["long_run_virtual_frame_period_ns"])
REQUIRED_NS = int(FROZEN["long_run_virtual_duration_ns"])


class T_LongRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="s5t03_long_")
        cls.out = pathlib.Path(cls.tmp.name) / "run"
        cls.code = LR.run_long(out_dir=cls.out, frames=2000, seed=SEED, canvas=(1280, 720),
                               stage3_binding=None, keyframe_max=6, want_demo=False,
                               stream_mode="mixed", warmup_frames=0)
        cls.results = json.loads((cls.out / "results.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((cls.out / "manifest.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_01_exit_and_artifacts(self) -> None:
        """小样本必须 exit 0 且产物齐全。"""
        self.assertEqual(self.code, 0, self.results["checks"])
        for rel in ("results.json", "manifest.json", "frame_assertions.jsonl.gz"):
            self.assertTrue((self.out / rel).is_file(), f"缺产物 {rel}")
        self.assertTrue(list((self.out / "logs").glob("events_*.jsonl.gz")), "缺事件日志")
        self.assertTrue(list((self.out / "keyframes").glob("*.png")), "缺关键帧")

    def test_02_hard_invariants(self) -> None:
        """硬不变量：每帧一次提交、时间戳单调、可复算、无死锁。"""
        inv = self.results["invariants"]
        for key in ("one_commit_event_per_frame", "commit_timestamps_monotonic",
                    "recompute_matches_online", "no_deadlock"):
            self.assertTrue(inv[key], f"{key} 必须为真")
        self.assertEqual(self.results["assertion_count"], 2000)

    def test_03_smoke_does_not_claim_30min(self) -> None:
        """诚实标注：小样本不得声称 ≥30 分钟；软判据应为 null 或 false（不得为假阳性 true）。"""
        inv = self.results["invariants"]
        self.assertFalse(inv["canonical_long_run"])
        self.assertIsNone(inv["margin_within_one_period"])
        self.assertLess(inv["virtual_elapsed_ns"], REQUIRED_NS)
        self.assertIn("显示/叠加路径", " ".join(self.results["limitations"]))

    def test_04_canonical_arithmetic(self) -> None:
        """规范帧数的判据算术（纯计算，不跑 10 万帧）。"""
        period_count = CANON_FRAMES - 1
        virtual = period_count * PERIOD_NS
        self.assertEqual(period_count, int(FROZEN["long_run_period_count"]))
        self.assertGreaterEqual(virtual, REQUIRED_NS)
        margin = virtual - REQUIRED_NS
        self.assertGreaterEqual(margin, 0)
        self.assertLess(margin, PERIOD_NS)
        self.assertEqual(margin, int(FROZEN["long_run_margin_ns"]))

    def test_05_gz_assertions_cover_all_frames(self) -> None:
        """`frame_assertions.jsonl.gz` 必须覆盖全部帧，且事件日志行数 ≥ 帧数。"""
        with gzip.open(self.out / "frame_assertions.jsonl.gz", "rt", encoding="utf-8") as handle:
            lines = [line for line in handle if line.strip()]
        self.assertEqual(len(lines), 2000)
        first = json.loads(lines[0])
        for key in ("displayed_frame_id", "result_frame_id", "result_seq", "state", "age_frame_ns",
                    "assertion_mode", "input_scope_label"):
            self.assertIn(key, first)
        log = next((self.out / "logs").glob("events_*.jsonl.gz"))
        with gzip.open(log, "rt", encoding="utf-8") as handle:
            events = sum(1 for line in handle if line.strip())
        self.assertGreaterEqual(events, 2000)

    def test_06_boundary_cases_pass(self) -> None:
        """过期边界三例（渲染路径）必须 PASS 且语义正确。"""
        cases = {item["case_id"]: item for item in self.results["boundary_cases"]}
        self.assertEqual(len(cases), 3)
        self.assertFalse(cases["age_equals_limit_not_stale"]["stale_effective"])
        self.assertTrue(cases["age_limit_plus_one_stale"]["stale_effective"])
        self.assertTrue(cases["explicit_stale_flag"]["stale_effective"])
        for item in cases.values():
            self.assertTrue(item["pass"], item["case_id"])

    def test_07_demo_not_requested_is_explicit(self) -> None:
        """未请求 demo ⇒ 显式 NOT_RUN 且 demo_only。"""
        self.assertEqual(self.results["demo"]["status"], "NOT_RUN")
        self.assertTrue(self.results["demo"]["demo_only"])

    def test_08_honest_labels_and_tools(self) -> None:
        """诚实标注与工具绑定：合成流/PRELIMINARY/NOT_RUN 清单/参考契约哈希。"""
        self.assertEqual(self.results["input_scope_label"], "synthetic_replay")
        self.assertEqual(self.results["status"], "PRELIMINARY")
        self.assertTrue(any("真实回放" in item for item in self.results["not_run"]))
        self.assertTrue(any("NOT_RUN" in item or "未通过" in item for item in self.results["limitations"])
                        or any("G0" in item for item in self.results["limitations"]))
        self.assertEqual(self.manifest["tools"]["geometry_reference"]["contract_id"], R.CONTRACT_ID)
        self.assertEqual(self.manifest["tools"]["long_run_replay"]["sha256"],
                         LR.sha256_file(REPO_ROOT / "scripts/stage5_t03/s5t03_long_run_replay.py"))

    def test_09_no_hardware_dependency(self) -> None:
        """长跑模块不得引入串口/硬件会话依赖。"""
        source = (REPO_ROOT / "scripts/stage5_t03/s5t03_long_run_replay.py").read_text(encoding="utf-8").lower()
        for forbidden in ("import serial", "import pyserial", "import pyvisa", "import usb",
                          '["hw_server"', '["xsdb"', '["vivado"', '["xsct"'):
            self.assertNotIn(forbidden, source, f"不应包含 {forbidden}")


    def test_10_missing_pillow_reported_as_failure(self) -> None:
        """同一口径覆盖长跑模块：缺 Pillow ⇒ `passed=false` 且退出码 1。"""
        import scripts.stage5_t03.s5t03_render as _RD
        original = _RD.PIL_AVAILABLE
        try:
            _RD.PIL_AVAILABLE = False
            with tempfile.TemporaryDirectory(prefix="s5t03_long_nopil_") as tmp:
                out = pathlib.Path(tmp) / "run"
                code = LR.run_long(out_dir=out, frames=300, seed=SEED, canvas=(1280, 720),
                                   stage3_binding=None, keyframe_max=3, want_demo=False,
                                   stream_mode="mixed", warmup_frames=0)
                results = json.loads((out / "results.json").read_text(encoding="utf-8"))
                self.assertEqual(code, 1)
                self.assertFalse(results["checks"]["passed"])
                self.assertTrue(any("render_unavailable" in item for item in results["checks"]["failures"]))
        finally:
            _RD.PIL_AVAILABLE = original


if __name__ == "__main__":
    unittest.main(verbosity=2)