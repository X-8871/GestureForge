#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""带框阶段4 冻结回放包消费链路的测试（含**判别力**）。

覆盖：
  1. 真实包（只读 w4）→ 消费者 **exit 0**，1 框、`xyxy_px` 存在、五元组 age 为 null（不伪造）；
  2. 篡改包字节 → 完整性哈希不符 ⇒ **exit 1 拒绝消费**；
  3. 篡改包内 `boxes[0].xyxy`（并同步更新索引哈希使其通过完整性）⇒ **包内交叉核对失败 ⇒ exit 1**；
  4. 标签守卫：把 `input_kind` 改成 `synthetic_replay` ⇒ 守卫抛 `LabelViolation`（不得回退到合成口径）。
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
DRIVER = REPO_ROOT / "scripts/stage5_t03/s5t03_stage4_positive_replay.py"

REAL_DIR = pathlib.Path(r"D:\codex-worktrees\w4\report\evidence\S4-CTRL"
                        r"\s4t27_replay_positive_20261027_r01")
REAL_INDEX = REAL_DIR / "freeze_index.json"
CONTRACT = pathlib.Path(r"D:\codex-worktrees\w4\docs\stage4\s4b_shared_input_result_contract.json")

import scripts.stage5_t03.s5t03_stage4_positive_replay as DRV  # noqa: E402
import scripts.stage5_t03.s5t03_stage4_frozen_replay as C  # noqa: E402


def _run(index: pathlib.Path, out: pathlib.Path) -> int:
    return subprocess.run([sys.executable, "-B", str(DRIVER), "--out", str(out), "--index", str(index),
                           "--contract", str(CONTRACT)], capture_output=True).returncode


class T_PositiveReplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="s5pos_")
        cls.dir = pathlib.Path(cls.tmp.name)
        if not REAL_INDEX.is_file():
            raise unittest.SkipTest("真实带框包不可用（w4 只读依赖）")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_01_real_package_consumed(self) -> None:
        out = self.dir / "out_real"
        self.assertEqual(_run(REAL_INDEX, out), 0)
        report = json.loads((out / "positive_report.json").read_text(encoding="utf-8"))
        self.assertTrue(report["integrity"]["all_pass"])
        self.assertEqual(report["counts"]["detections"], 1)
        self.assertEqual(report["counts"]["boxes_with_px"], 1)
        self.assertTrue(report["cross_check_passed"])
        self.assertEqual(report["input_kind"], "stage4_frozen_replay")
        self.assertEqual(report["input_variant"], "positive_with_detections")
        five = report["five_tuple"]
        self.assertIsNone(five["age_result_ns"])
        self.assertIsNone(five["age_frame_ns"])
        self.assertTrue(five["display_eligible"])
        self.assertEqual(five["display_semantics"], "C.latest_result_overlay".replace("C.", "B_"))
        branch = report["frame"]["detections"][0]["xyxy_px"]
        self.assertEqual(set(branch), {"x1", "y1", "x2", "y2"})

    def _copy_package(self, name: str, mutate) -> pathlib.Path:
        """复制真实包到临时目录并可选篡改；同步索引哈希（保证只测目标判据）。"""
        target = self.dir / name
        shutil.rmtree(target, ignore_errors=True)
        target.mkdir(parents=True)
        pkg = json.loads((REAL_DIR / "task27_replay_result_package_positive.json").read_text(encoding="utf-8"))
        mutate(pkg)
        pkg_path = target / "task27_replay_result_package_positive.json"
        pkg_path.write_text(json.dumps(pkg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        index = json.loads(REAL_INDEX.read_text(encoding="utf-8"))
        index["package_path"] = pkg_path.name
        index["package_sha256"] = hashlib.sha256(pkg_path.read_bytes()).hexdigest()
        index_path = target / "freeze_index.json"
        index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        return index_path

    def test_02_tampered_bytes_refused(self) -> None:
        target = self.dir / "tamper_bytes"
        shutil.rmtree(target, ignore_errors=True)
        shutil.copytree(REAL_DIR, target)
        pkg_path = target / "task27_replay_result_package_positive.json"
        pkg_path.write_bytes(pkg_path.read_bytes() + b" ")      # 破坏字节但不动索引登记
        self.assertEqual(_run(target / "freeze_index.json", self.dir / "out_tamper"), 1)

    def test_03_crosscheck_mismatch_fails(self) -> None:
        def mutate(pkg: dict) -> None:
            pkg["detections"]["boxes"][0]["xyxy"] = [0.1, 0.1, 0.2, 0.2]   # 与 t29 参考不一致
        index_path = self._copy_package("crosscheck", mutate)
        self.assertEqual(_run(index_path, self.dir / "out_cross"), 1)
        report = json.loads((self.dir / "out_cross" / "positive_report.json").read_text(encoding="utf-8"))
        self.assertFalse(report["cross_check_passed"])

    def test_04_label_guard_blocks_synthetic_fallback(self) -> None:
        with self.assertRaises(C.LabelViolation):
            C.assert_replay_labels({"input_kind": "synthetic_replay",
                                    "consumption_mode": C.CONSUMPTION_MODE,
                                    "evidence_kind": C.EVIDENCE_KIND}, where="unit_test")

    def test_05_index_schema_is_checked(self) -> None:
        bad = self.dir / "bad_index.json"
        bad.write_text(json.dumps({"schema_version": "something_else"}), encoding="utf-8")
        self.assertEqual(_run(bad, self.dir / "out_bad"), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)