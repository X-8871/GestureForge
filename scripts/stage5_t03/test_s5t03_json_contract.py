#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阶段5 JSON 契约校验器测试（只读既有证据 + 临时篡改副本；不联网、不接板卡）。

覆盖
====
1. 三个**真实最终包**必须通过契约校验（短跑/长跑/多几何，各按种类判定）；
2. **负向**：只读拷贝到临时目录后制造违约（缺必需字段 / 状态标签错 / 缺计数键 / 缺 manifest.files 条目 /
   长跑缺不变量 / 契约文件缺字段），校验器**必须**失败（判别力）；
3. 契约文件自洽（必需字段清单与三类种类声明齐全、计数键 14 个）；
4. 无硬件依赖。
"""

from __future__ import annotations

import gzip
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.stage5_t03.validate_s5t03_json as V  # noqa: E402

EVID = REPO_ROOT / "report/evidence/S5-T03"
REAL = {
    "replay_display": EVID / "s5t03_offline_replay_display_20261026_r06",
    "long_run_replay": EVID / "s5t03_offline_long_run_replay_20261026_r04",
    "multi_geometry_render": EVID / "s5t03_multi_geometry_render_20261026_r02",
}


class T_Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = V.load_contract()
        cls.tmp = tempfile.TemporaryDirectory(prefix="s5t03_contract_")
        cls.tmpdir = pathlib.Path(cls.tmp.name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def _copy(self, kind: str, name: str) -> pathlib.Path:
        dst = self.tmpdir / name
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(REAL[kind], dst)
        return dst

    @staticmethod
    def _write_json(path: pathlib.Path, obj: dict) -> None:
        path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8", newline="\n")

    # ── 正向 ───────────────────────────────────────────────────────────────
    def test_01_real_packages_pass(self) -> None:
        """三个真实最终包必须通过，且种类判定正确、帧数与产物一致。"""
        for kind, run in REAL.items():
            report = V.validate_package(run, self.contract)
            self.assertTrue(report["ok"], f"{run.name}: {report['errors']}")
            self.assertEqual(report.get("kind"), kind)
        self.assertEqual(V.validate_package(REAL["replay_display"], self.contract)["counts"]["frame_assertions"], 240)
        self.assertEqual(V.validate_package(REAL["long_run_replay"], self.contract)["counts"]["frame_assertions"], 106573)

    def test_02_kind_inference_is_not_guessing(self) -> None:
        """种类判定依据固定字段；无法判定必须抛错（不得默认成某一类）。"""
        self.assertEqual(V.infer_kind({"counters": {}}, self.contract), "replay_display")
        self.assertEqual(V.infer_kind({"counters": {}, "invariants": {}}, self.contract), "long_run_replay")
        self.assertEqual(V.infer_kind({"geometries": []}, self.contract), "multi_geometry_render")
        with self.assertRaises(ValueError):
            V.infer_kind({"run_id": "x"}, self.contract)

    def test_03_contract_self_consistency(self) -> None:
        """契约自洽：三类种类齐全、计数键 14 个、逐帧/manifest 必需字段非空、稳定集非空。"""
        kinds = self.contract["artifact_kinds"]
        self.assertEqual(set(kinds), {"replay_display", "long_run_replay", "multi_geometry_render"})
        self.assertEqual(len(self.contract["counter_keys"]), 14)
        self.assertEqual(len(set(self.contract["counter_keys"])), 14)
        for name, spec in kinds.items():
            self.assertTrue(spec["schema_version"].startswith("gestureforge_s5t03_"), name)
            self.assertTrue(spec["required_results"], name)
        self.assertTrue(self.contract["frame_assertion_required"])
        self.assertTrue(self.contract["manifest_required"])
        self.assertTrue(self.contract["stability"]["stable_for_consumers"])
        self.assertTrue(self.contract["stability"]["detail_not_for_consumers"])

    # ── 负向（判别力）──────────────────────────────────────────────────────
    def test_10_missing_required_field_fails(self) -> None:
        run = self._copy("multi_geometry_render", "mg_missing")
        obj = json.loads((run / "results.json").read_text(encoding="utf-8"))
        obj.pop("numeric_checks")
        self._write_json(run / "results.json", obj)
        report = V.validate_package(run, self.contract)
        self.assertFalse(report["ok"])
        self.assertTrue(any("numeric_checks" in item for item in report["errors"]))

    def test_11_wrong_status_label_fails(self) -> None:
        run = self._copy("multi_geometry_render", "mg_status")
        obj = json.loads((run / "results.json").read_text(encoding="utf-8"))
        obj["status"] = "DONE"
        self._write_json(run / "results.json", obj)
        report = V.validate_package(run, self.contract)
        self.assertFalse(report["ok"])
        self.assertTrue(any("status" in item for item in report["errors"]))

    def test_12_missing_counter_key_fails(self) -> None:
        run = self._copy("replay_display", "short_counter")
        obj = json.loads((run / "results.json").read_text(encoding="utf-8"))
        obj["counters"].pop("stale_cleared", None)
        self._write_json(run / "results.json", obj)
        report = V.validate_package(run, self.contract)
        self.assertFalse(report["ok"])
        self.assertTrue(any("counters" in item for item in report["errors"]))

    def test_13_long_run_missing_invariant_fails(self) -> None:
        run = self._copy("long_run_replay", "long_inv")
        obj = json.loads((run / "results.json").read_text(encoding="utf-8"))
        obj["invariants"].pop("one_commit_event_per_frame", None)
        self._write_json(run / "results.json", obj)
        report = V.validate_package(run, self.contract)
        self.assertFalse(report["ok"])
        self.assertTrue(any("one_commit_event_per_frame" in item for item in report["errors"]))

    def test_14_missing_frame_assertions_fails_for_replay(self) -> None:
        run = self._copy("replay_display", "short_noframes")
        (run / "frame_assertions.jsonl").unlink()
        report = V.validate_package(run, self.contract)
        self.assertFalse(report["ok"])
        self.assertTrue(any("frame_assertions" in item for item in report["errors"]))
        # 多几何种类**不要求**逐帧断言 ⇒ 同条件下应通过
        mg = V.validate_package(REAL["multi_geometry_render"], self.contract)
        self.assertTrue(mg["ok"])

    def test_15_manifest_missing_files_entry_field_fails(self) -> None:
        run = self._copy("multi_geometry_render", "mg_manifest")
        obj = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
        obj["files"][0].pop("sha256")
        self._write_json(run / "manifest.json", obj)
        report = V.validate_package(run, self.contract)
        self.assertFalse(report["ok"])
        self.assertTrue(any("manifest.files" in item for item in report["errors"]))

    def test_16_duplicated_frame_assertion_key_compression_is_ok(self) -> None:
        """`.jsonl.gz` 与 `.jsonl` 都必须可校验（长跑用 gzip + compact）。"""
        report = V.validate_package(REAL["long_run_replay"], self.contract)
        self.assertTrue(report["ok"])
        self.assertEqual(report["counts"]["frame_assertions"], 106573)

    def test_17_broken_contract_fails_closed(self) -> None:
        """契约缺必需键 ⇒ 必须抛错（fail-closed，不得静默放过）。"""
        bad = self.tmpdir / "bad_contract.json"
        self._write_json(bad, {"contract_id": "x"})
        with self.assertRaises(ValueError):
            V.load_contract(bad)
        with self.assertRaises(FileNotFoundError):
            V.load_contract(self.tmpdir / "nope.json")

    def test_18_cli_exit_codes(self) -> None:
        """CLI：全通过 0；违约 1；未指定包 2。"""
        good = [str(p) for p in REAL.values()]
        argv = [a for p in good for a in ("--package", p)]
        self.assertEqual(V.main(argv), 0)
        run = self._copy("multi_geometry_render", "mg_cli")
        obj = json.loads((run / "results.json").read_text(encoding="utf-8"))
        obj.pop("limitations")
        self._write_json(run / "results.json", obj)
        self.assertEqual(V.main(["--package", str(run)]), 1)
        self.assertEqual(V.main([]), 2)

    def test_19_no_hardware_dependency(self) -> None:
        source = (REPO_ROOT / "scripts/stage5_t03/validate_s5t03_json.py").read_text(encoding="utf-8").lower()
        for forbidden in ("import serial", "import pyvisa", "import usb", '["hw_server"',
                          '["xsdb"', '["vivado"', '["xsct"'):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main(verbosity=2)