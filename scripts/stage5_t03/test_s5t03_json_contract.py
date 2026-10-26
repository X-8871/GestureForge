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
        """契约缺必需键/缺文件 ⇒ 必须 ContractError（退出码 2，fail-closed）。"""
        bad = self.tmpdir / "bad_contract.json"
        self._write_json(bad, {"contract_id": "x"})
        with self.assertRaises(V.ContractError):
            V.load_contract(bad)
        # 逐个删除必需键都必须被抓住（B5：不得静默放过）
        for key in self.contract["contract_required_keys"]:
            trimmed = {k: v for k, v in self.contract.items() if k != key}
            path = self.tmpdir / f"contract_without_{key}.json"
            self._write_json(path, trimmed)
            with self.assertRaises(V.ContractError, msg=f"缺 {key} 未被抓住"):
                V.load_contract(path)
        with self.assertRaises(V.ContractError):
            V.load_contract(self.tmpdir / "nope.json")

    def test_20_schema_version_value_is_guarded(self) -> None:
        """B2：schema_version 值错（乱填/升版）必须违约。"""
        run = self._copy("multi_geometry_render", "b2_schema")
        obj = json.loads((run / "results.json").read_text(encoding="utf-8"))
        obj["schema_version"] = "gestureforge_s5t03_multi_geometry_render_v2"
        self._write_json(run / "results.json", obj)
        entry = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
        for item in entry["files"]:
            if item["path"] == "results.json":
                item["sha256"] = V.sha256_file(run / "results.json")   # 隔离出"仅 schema 值"这一项
        self._write_json(run / "manifest.json", entry)
        report = V.validate_package(run, self.contract)
        self.assertFalse(report["ok"])
        self.assertTrue(any("schema_version" in item for item in report["errors"]), report["errors"])

    def test_21_file_hash_drift_is_detected(self) -> None:
        """B3：篡改包内文件内容（清单未同步）必须违约。"""
        run = self._copy("multi_geometry_render", "b3_hash")
        target = run / "results.json"
        original = target.read_text(encoding="utf-8")
        target.write_text(original + " ", encoding="utf-8", newline="\n")
        report = V.validate_package(run, self.contract)
        self.assertFalse(report["ok"])
        self.assertTrue(any("哈希不符" in item for item in report["errors"]), report["errors"])

    def test_22_checks_passed_false_is_rejected(self) -> None:
        """B4：checks.passed=False（失败运行）不得作为交付证据。"""
        run = self._copy("multi_geometry_render", "b4_passed")
        obj = json.loads((run / "results.json").read_text(encoding="utf-8"))
        obj["checks"] = {"passed": False, "failures": ["x"]}
        self._write_json(run / "results.json", obj)
        report = V.validate_package(run, self.contract)
        self.assertFalse(report["ok"])
        self.assertTrue(any("passed" in item for item in report["errors"]), report["errors"])

    def test_23_frame_stable_subset_is_checked(self) -> None:
        """B1：逐帧 stable 必需字段缺失必须违约（不能只查 frame_assertion_required）。"""
        run = self._copy("replay_display", "b1_frames")
        path = run / "frame_assertions.jsonl"
        lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        lines[0].pop("result_seq", None)
        body = chr(10).join(json.dumps(item, ensure_ascii=False) for item in lines)
        path.write_text(body + chr(10), encoding="utf-8", newline="\n")
        manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
        for item in manifest["files"]:
            if item["path"] == path.name:
                item["sha256"] = V.sha256_file(path)
        self._write_json(run / "manifest.json", manifest)
        report = V.validate_package(run, self.contract)
        self.assertFalse(report["ok"])
        self.assertTrue(any("result_seq" in item for item in report["errors"]), report["errors"])

    def test_24_exit_code_semantics(self) -> None:
        """B6：2=输入/环境错误（契约缺键、包目录不存在、packages-from 文件不存在、无参数）。"""
        self.assertEqual(V.main(["--package", str(self.tmpdir / "no_such_package")]), 2)
        self.assertEqual(V.main(["--packages-from", str(self.tmpdir / "no_such_list.txt")]), 2)
        self.assertEqual(V.main([]), 2)
        bad = self.tmpdir / "incomplete_contract.json"
        self._write_json(bad, {"contract_id": "x"})
        self.assertEqual(V.main(["--contract", str(bad), "--package", str(REAL["multi_geometry_render"])]), 2)

    def test_25_event_log_reject_reason_key_documented(self) -> None:
        """契约必须如实登记事件日志的拒绝原因键为 `rr`（复审第 6 项：文档曾写不存在的 `reason`）。"""
        self.assertEqual(self.contract["event_log_fields"]["reject_reason_key"].split("（")[0], "rr")
        self.assertTrue(self.contract["known_inconsistencies"])
        self.assertIn("rr", self.contract["known_inconsistencies"][0]["consumer_rule"])

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