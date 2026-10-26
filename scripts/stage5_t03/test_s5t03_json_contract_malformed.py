#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""契约**畸形输入与键位核对**测试（复审 BL-2 与 BL-1 的永久防线；只读、不联网、不接板卡）。

覆盖
====
1. **BL-2**：契约是合法 JSON 但**不是对象**（数组/字符串/数字/null/bool）⇒ 必须 `ContractError`（退出码 2）；
   自声明短 `contract_required_keys` + 缺 `artifact_kinds`、删 `stability` 但同步从 required 列表移除 ⇒ 同样 exit 2
   （**不得崩成 1、更不得静默 0**）。
2. **BL-1**：契约声明的**事件日志键集**必须与实物首条 submit/commit 记录**逐字一致**；
   把契约键位改错 ⇒ 校验器必须 exit 1（此前校验器不读事件日志，漂移无法被发现）。
3. **O-1**：仅豁免**包根** `manifest.json`；子目录下同名的多余文件必须被抓住。
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
SHORT = EVID / "s5t03_offline_replay_display_20261026_r06"
LONG = EVID / "s5t03_offline_long_run_replay_20261026_r04"
MG = EVID / "s5t03_multi_geometry_render_20261026_r02"
MALFORMED = ["[1, 2, 3]", '"abc"', "42", "null", "false", "3.5"]


class T_ContractMalformed(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = V.load_contract()
        cls.tmp = tempfile.TemporaryDirectory(prefix="s5t03_malformed_")
        cls.tmpdir = pathlib.Path(cls.tmp.name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def _write(self, name: str, text: str) -> pathlib.Path:
        path = self.tmpdir / name
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    # ── BL-2 ───────────────────────────────────────────────────────────────
    def test_01_non_object_contracts_are_environment_errors(self) -> None:
        for index, text in enumerate(MALFORMED):
            path = self._write(f"non_object_{index}.json", text)
            with self.assertRaises(V.ContractError, msg=f"{text} 未被判为环境错误"):
                V.load_contract(path)
            self.assertEqual(V.main(["--contract", str(path), "--package", str(MG)]), 2,
                             f"{text} 的退出码应为 2")

    def test_02_self_declared_short_required_list_is_caught(self) -> None:
        """自声明短 required 列表 + 缺 artifact_kinds ⇒ 必须 exit 2，不得 KeyError（崩成 1）。"""
        path = self._write("short_required.json",
                           json.dumps({"contract_id": "x", "contract_required_keys": ["contract_id"]}))
        with self.assertRaises(V.ContractError):
            V.load_contract(path)
        self.assertEqual(V.main(["--contract", str(path), "--package", str(MG)]), 2)

    def test_03_missing_section_removed_from_required_is_caught(self) -> None:
        """删 stability 且同步从 required 列表移除 ⇒ 仍需 exit 2（不得静默放过）。"""
        trimmed = {k: v for k, v in self.contract.items() if k != "stability"}
        trimmed["contract_required_keys"] = [k for k in trimmed["contract_required_keys"] if k != "stability"]
        path = self._write("no_stability.json", json.dumps(trimmed, ensure_ascii=False))
        with self.assertRaises(V.ContractError):
            V.load_contract(path)
        self.assertEqual(V.main(["--contract", str(path), "--package", str(MG)]), 2)

    def test_04_artifact_kinds_wrong_type_is_caught(self) -> None:
        broken = dict(self.contract)
        broken["artifact_kinds"] = ["not", "a", "map"]
        path = self._write("kinds_list.json", json.dumps(broken, ensure_ascii=False))
        with self.assertRaises(V.ContractError):
            V.load_contract(path)

    # ── BL-1 ───────────────────────────────────────────────────────────────
    def test_05_declared_event_log_keys_match_reality(self) -> None:
        """契约声明的事件日志键集必须等于实物首条记录键集（短跑与长跑都查）。"""
        spec = self.contract["event_log_fields"]
        for run in (SHORT, LONG):
            logs = sorted(list(run.glob("logs/events_*.jsonl")) + list(run.glob("logs/events_*.jsonl.gz")))
            self.assertTrue(logs, run.name)
            path = logs[0]
            opener = (lambda: gzip.open(path, "rt", encoding="utf-8")) if path.suffix == ".gz" else \
                     (lambda: open(path, encoding="utf-8"))
            seen: dict[str, set] = {}
            with opener() as handle:
                for line in handle:
                    if not line.strip():
                        continue
                    record = json.loads(line)
                    if record.get("t") in ("sub", "commit"):
                        seen.setdefault(record["t"], set(record))
                    if len(seen) == 2:
                        break
            self.assertEqual(seen["sub"], set(spec["submit_record_keys"]), run.name)
            self.assertEqual(seen["commit"], set(spec["commit_record_keys"]), run.name)
            counts, errs = V.check_event_log_keys(run, self.contract)
            self.assertEqual(errs, [], run.name)
            self.assertEqual(counts["sub"], len(spec["submit_record_keys"]))

    def test_06_wrong_declared_keys_fail_validation(self) -> None:
        """把契约键位改错（模拟 BL-1 的漂移）⇒ 校验器必须 exit 1。"""
        broken = dict(self.contract)
        broken["event_log_fields"] = dict(broken["event_log_fields"])
        broken["event_log_fields"]["submit_record_keys"] = ["t", "state", "drawn", "boxes"]
        path = self._write("bad_keys.json", json.dumps(broken, ensure_ascii=False))
        self.assertEqual(V.main(["--contract", str(path), "--package", str(SHORT)]), 1)
        counts, errs = V.check_event_log_keys(SHORT, broken)
        self.assertTrue(errs and "事件日志" in errs[0], errs)

    # ── O-1 ────────────────────────────────────────────────────────────────
    def test_07_only_package_root_manifest_is_exempt(self) -> None:
        """子目录里的同名 manifest.json 是**多余文件**，必须被抓住（只豁免包根那份）。"""
        run = self.tmpdir / "mg_subdir_manifest"
        shutil.rmtree(run, ignore_errors=True)
        shutil.copytree(MG, run)
        extra = run / "keyframes" / "manifest.json"
        extra.write_text("{}\n", encoding="utf-8", newline="\n")
        report = V.validate_package(run, self.contract)
        self.assertFalse(report["ok"])
        self.assertTrue(any("未列入" in item for item in report["errors"]), report["errors"])

    def test_08_real_packages_still_pass(self) -> None:
        for run in (SHORT, LONG, MG):
            report = V.validate_package(run, self.contract)
            self.assertTrue(report["ok"], f"{run.name}: {report['errors']}")


if __name__ == "__main__":
    unittest.main(verbosity=2)