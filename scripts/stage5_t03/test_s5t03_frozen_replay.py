#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 阶段4 冻结包离线消费的**新增测试**（含判别力用例）。

测试范围
========
- 完整性：冻结包逐文件 sha256+bytes、契约绑定、`upstream_bindings` 漂移现场复算；
  **篡改任一字节必须被拒绝**（不得只校验 package.json）。
- 标签：真实回放口径（`stage4_frozen_replay`/`replay_only`/`offline_replay`）；
  **改回 synthetic 必须判失败**（判别力）。
- 几何对拍：`detections[].xyxy_px` 与独立重算逐框比对（含**篡改一个 `xyxy_px` 必须判失败**）。
- 时间口径：`FILE_INJECTION` 0 哨兵 ⇒ 端到端延迟不可定义；`injection_start_ns` 不得冒用。

所有判别力用例都断言"篡改后被判 FAIL"，避免只证明"正常路径能过"。
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.stage5_t03.check_s5t03_frozen_replay as CHK  # noqa: E402
import scripts.stage5_t03.s5t03_freeze_integrity as FI  # noqa: E402
import scripts.stage5_t03.s5t03_stage4_frozen_replay as C  # noqa: E402
import verification.s5_display_geometry_reference as R  # noqa: E402

PACKAGE_DIR = C.DEFAULT_PACKAGE_DIR
FREEZE_RECORD = C.DEFAULT_FREEZE_RECORD
CONTRACT = C.DEFAULT_CONTRACT
EXPECTED_GATE_BOX_PX = {"x1": 357, "y1": 713, "x2": 501, "y2": 837}
EXPECTED_GATE_BORDER_PIXELS = 1071

_WORKDIR: pathlib.Path | None = None
_ARTIFACTS: pathlib.Path | None = None
_INTEGRITY: dict | None = None


def setUpModule() -> None:                                    # noqa: N802 (unittest 约定)
    global _WORKDIR, _ARTIFACTS, _INTEGRITY
    _WORKDIR = pathlib.Path(tempfile.mkdtemp(prefix="s5t03_frozen_replay_"))
    _ARTIFACTS = _WORKDIR / "artifacts"
    _INTEGRITY = FI.verify_all(freeze_record_path=FREEZE_RECORD, package_dir=PACKAGE_DIR,
                               contract_json=CONTRACT, drift=True)
    package, integrity = C.load_frozen_package(package_dir=PACKAGE_DIR,
                                               freeze_record_path=FREEZE_RECORD,
                                               contract_json=CONTRACT, drift=False)
    artifacts = C.build_artifacts(package=package, package_dir=PACKAGE_DIR, integrity=integrity)
    C.write_artifacts(out_dir=_ARTIFACTS, package=package, package_dir=PACKAGE_DIR,
                      freeze_record_path=FREEZE_RECORD, contract_json=CONTRACT,
                      integrity=integrity, artifacts=artifacts)


def tearDownModule() -> None:                                 # noqa: N802
    if _WORKDIR is not None and _WORKDIR.exists():
        shutil.rmtree(_WORKDIR, ignore_errors=True)


def copy_artifacts(name: str) -> pathlib.Path:
    target = _WORKDIR / name
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(_ARTIFACTS, target)
    return target


def run_checker(artifacts_dir: pathlib.Path, *, out: pathlib.Path | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-B", "scripts/stage5_t03/check_s5t03_frozen_replay.py",
           "--artifacts", str(artifacts_dir), "--package-dir", str(PACKAGE_DIR),
           "--freeze-record", str(FREEZE_RECORD), "--contract", str(CONTRACT), "--skip-integrity"]
    if out is not None:
        cmd += ["--out", str(out)]
    return subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


class FreezeIntegrityTests(unittest.TestCase):
    """完整性复算（逐文件 sha256+bytes；篡改必拒）。"""

    def test_all_frozen_files_recompute_pass(self) -> None:
        integrity = _INTEGRITY["file_integrity"]
        self.assertEqual(integrity["checked"], 10)
        self.assertTrue(integrity["all_pass"], integrity["records"])
        self.assertEqual(integrity["ok"], 10)

    def test_contract_binding_matches_frozen_reference(self) -> None:
        binding = _INTEGRITY["contract_binding_check"]
        self.assertTrue(binding["json_match"])
        self.assertTrue(binding["json_matches_frozen_offline_reference"])
        self.assertEqual(binding["json_actual_sha256"], FI.EXPECTED_CONTRACT_SHA256)

    def test_upstream_binding_drift_all_pass(self) -> None:
        drift = _INTEGRITY["upstream_binding_drift"]
        self.assertEqual(drift["checked"], 17)
        self.assertTrue(drift["all_pass"], [e for e in drift["entries"] if e["verdict"] != "PASS"])
        blob_entries = [e for e in drift["entries"] if e["byte_basis"] == FI.BLOB_BASIS]
        self.assertEqual(len(blob_entries), 4)          # 3 个 dbdf + 1 个 w5（固定修订）
        for entry in blob_entries:
            self.assertNotEqual(entry["actual_sha256"], FI.EMPTY_SHA256)

    def test_tampered_byte_in_package_is_rejected(self) -> None:
        workdir = pathlib.Path(tempfile.mkdtemp(prefix="s5t03_tamper_pkg_", dir=str(_WORKDIR)))
        names = ["task27_replay_result_package.json", "replay_forward_bridge_result.json"]
        files = []
        for name in names:
            source = PACKAGE_DIR / name
            target = workdir / name
            shutil.copyfile(source, target)
            files.append({"path": name, "bytes": target.stat().st_size, "sha256": FI.sha256_file(target)})
        freeze_record = {"files": files, "missing_files": [], "contract_binding": {}}
        self.assertTrue(FI.verify_package_files(workdir, freeze_record)["all_pass"])
        target = workdir / names[1]
        blob = bytearray(target.read_bytes())
        blob[10] = (blob[10] + 1) % 256                   # 翻转 1 个字节
        target.write_bytes(bytes(blob))
        report = FI.verify_package_files(workdir, freeze_record)
        self.assertFalse(report["all_pass"])
        failed = [r["path"] for r in report["records"] if r["verdict"] == "FAIL"]
        self.assertEqual(failed, [names[1]])

    def test_missing_file_in_package_is_rejected(self) -> None:
        workdir = pathlib.Path(tempfile.mkdtemp(prefix="s5t03_missing_pkg_", dir=str(_WORKDIR)))
        freeze_record = {"files": [{"path": "not_there.json", "bytes": 1, "sha256": "0" * 64}],
                         "missing_files": [], "contract_binding": {}}
        report = FI.verify_package_files(workdir, freeze_record)
        self.assertFalse(report["all_pass"])
        self.assertEqual(report["records"][0]["reason"], "file_missing")

    def test_cross_tree_blob_read_in_wrong_tree_fails_loudly(self) -> None:
        """已知陷阱：在别的树取 blob 会得到空输入哈希——本器必须判 FAIL 而非误报 PASS。"""
        contract_tree = FI.worktree_root(CONTRACT)
        self.assertIsNotNone(contract_tree)
        missing, error = FI.git_blob_sha256(contract_tree, "HEAD",
                                            "report/evidence/S3-T05/no_such_file.md")
        self.assertIsNone(missing)
        self.assertIsNotNone(error)


class ConsumerArtifactTests(unittest.TestCase):
    """消费者产物：标签、契约字段、几何换算、时间口径。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.frames = json.loads((_ARTIFACTS / "frames.json").read_text(encoding="utf-8"))
        cls.gate = json.loads((_ARTIFACTS / "gate_evidence_projection.json").read_text(encoding="utf-8"))
        cls.report = json.loads((_ARTIFACTS / "consumer_report.json").read_text(encoding="utf-8"))
        cls.five = [json.loads(line) for line in
                    (_ARTIFACTS / "five_tuples.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]

    def test_labels_are_real_replay_not_synthetic(self) -> None:
        for payload in (self.frames, self.gate, self.report):
            self.assertEqual(payload["input_kind"], "stage4_frozen_replay")
            self.assertEqual(payload["consumption_mode"], "replay_only")
            self.assertEqual(payload["evidence_kind"], "offline_replay")
            self.assertEqual(payload["scope_statement"], C.SCOPE_STATEMENT)
            self.assertEqual(C.label_problems(payload), [])

    def test_replay_frame_record_is_zero_box_no_hand(self) -> None:
        self.assertEqual(self.frames["frame_count"], 1)
        record = self.frames["frames"][0]
        self.assertEqual(record["state"], "NO_HAND")
        self.assertEqual(record["detection_count"], 0)
        self.assertEqual(record["detections"], [])
        self.assertEqual(record["candidate_count_pre_threshold"], 0)
        self.assertEqual(R.validate_result_record(record), [])

    def test_gate_box_px_matches_hand_computed_values(self) -> None:
        record = self.gate["records"][0]
        detection = record["detections"][0]
        self.assertEqual(detection["xyxy_px"], EXPECTED_GATE_BOX_PX)
        self.assertEqual(detection["border_pixels"], EXPECTED_GATE_BORDER_PIXELS)
        self.assertEqual(detection["xyxy_px_canvas"], [1440, 1920])
        self.assertEqual(record["geometry"]["display_canvas"], [1440, 1920])

    def test_gate_evidence_is_not_attributed_to_replay_frame(self) -> None:
        self.assertFalse(self.gate["display_eligible"])
        for record in self.gate["records"]:
            self.assertFalse(record["display_eligible"])
            self.assertFalse(record["is_replay_frame"])
            self.assertEqual(record["attribution"], "gate_evidence_sample_not_replay_frame")
            self.assertEqual(record["sample_id"], "test_fist_000")

    def test_timing_fields_are_not_fabricated(self) -> None:
        record = self.frames["frames"][0]
        self.assertEqual(record["capture_time_ns"], 1792776253000000000)
        for field in ("result_time_ns", "inference_time_ns", "end_to_end_latency_ns"):
            self.assertIsNone(record[field], field)
        basis = record["timing_basis"]
        self.assertEqual(basis["capture_time_ns"]["basis"], C.CAPTURE_BASIS_DOCUMENTED)
        self.assertFalse(basis["capture_time_ns"]["is_measured_capture_clock"])
        self.assertFalse(basis["result_time_ns"]["defined"])
        self.assertFalse(basis["end_to_end_latency_ns"]["defined"])
        self.assertIsNone(basis["injection_start_ns"])
        self.assertFalse(basis["injection_start_ns_used_as_capture_time"])
        self.assertEqual(basis["stale_evaluation"], C.STALE_EVALUATION_NOT_RUN)
        self.assertEqual(record["stale"], None)
        self.assertIn(C.NOT_DECLARED, record["field_bases"]["stale"])

    def test_five_tuple_declares_age_basis(self) -> None:
        self.assertEqual(len(self.five), 1)
        item = self.five[0]
        self.assertEqual(item["display_semantics"], R.DISPLAY_SEMANTICS)
        self.assertIsNone(item["age_result_ns"])
        self.assertIsNone(item["age_frame_ns"])
        self.assertFalse(item["age_basis"]["age_result_ns"]["defined"])
        self.assertFalse(item["age_basis"]["age_frame_ns"]["defined"])
        self.assertIn("injection_start_ns", item["age_basis"]["age_frame_ns"]["basis"])
        self.assertEqual(CHK.check_five_tuples(self.five)["verdict"], "PASS")

    def test_injection_zero_sentinel_makes_latency_undefined(self) -> None:
        frame = {"mode": "FILE_INJECTION", "capture_time_available": False, "capture_time_ns": 0,
                 "injection_start_ns": 123456789, "stale_evaluation": C.STALE_EVALUATION_NOT_RUN}
        basis = C.resolve_timing(frame, state="OK")
        self.assertEqual(basis["capture_time_ns"]["basis"], C.CAPTURE_BASIS_ZERO_SENTINEL)
        self.assertFalse(basis["end_to_end_latency_ns"]["defined"])
        self.assertEqual(basis["end_to_end_latency_ns"]["basis"], C.E2E_BASIS_INJECTION_SENTINEL)
        self.assertEqual(basis["injection_start_ns"], 123456789)
        self.assertFalse(basis["injection_start_ns_used_as_capture_time"])

    def test_injection_start_as_capture_is_refused(self) -> None:
        frame = {"mode": "FILE_INJECTION", "capture_time_available": True,
                 "capture_time_ns": 42, "injection_start_ns": 42}
        with self.assertRaises(C.ConsumerError):
            C.resolve_timing(frame, state="OK")

    def test_governance_boundary_text_present(self) -> None:
        self.assertEqual(self.report["hardware_boundary"],
                         "板上真实回放接入仍需硬件 OFFER/CLAIM + 八类门禁（当前记录 0/8）；"
                         "本次离线接入不构成板上真实回放通过的证据。")
        for forbidden in ("板上行为 / PL 真实运行", "P / 4-D / G3 / G4 / G5 任一项通过"):
            self.assertIn(forbidden, self.report["forbidden_claims"])

    def test_display_path_compatibility_is_declared(self) -> None:
        compatibility = self.report["display_path_compatibility"]
        self.assertTrue(compatibility["contract_fields"].startswith("PASS"))
        self.assertTrue(compatibility["geometry_fit_exact"].startswith("PASS"))
        self.assertIn("REQUIRES_MONOTONIC_PUBLISH_INSTANT",
                      compatibility["timing_dependent_paths"])


class CrosscheckTests(unittest.TestCase):
    """独立对拍检查器：正常通过 + 篡改必失败（判别力）。"""

    def test_full_crosscheck_passes_with_integrity(self) -> None:
        out = _WORKDIR / "crosscheck_full.json"
        proc = subprocess.run(
            [sys.executable, "-B", "scripts/stage5_t03/check_s5t03_frozen_replay.py",
             "--artifacts", str(_ARTIFACTS), "--package-dir", str(PACKAGE_DIR),
             "--freeze-record", str(FREEZE_RECORD), "--contract", str(CONTRACT), "--out", str(out)],
            cwd=str(REPO_ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        report = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(report["verdict"], "PASS")
        self.assertTrue(report["checks"]["integrated_integrity"])
        box = report["box_crosscheck"]
        self.assertEqual(box["boxes_checked"], 2)          # predictions + t29 参考列表
        self.assertEqual(box["axes_checked"], 8)
        self.assertEqual(box["box_mismatches"], 0)
        self.assertEqual(box["empty_records"], 1)          # 回放帧零框
        self.assertTrue(all(v["verdict"] in ("PASS", "PASS_EMPTY") for v in box["verdicts"]))

    def test_tampered_xyxy_px_is_detected(self) -> None:
        for axis in ("x1", "y1", "x2", "y2"):
            with self.subTest(axis=axis):
                workdir = copy_artifacts(f"tamper_px_{axis}")
                target = workdir / "gate_evidence_projection.json"
                payload = json.loads(target.read_text(encoding="utf-8"))
                px = payload["records"][0]["detections"][0]["xyxy_px"]
                px[axis] = int(px[axis]) + 1               # 只改一个轴 1 像素
                target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
                proc = run_checker(workdir)
                self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                self.assertIn("FAIL", proc.stdout)
                self.assertIn("box_crosscheck", proc.stdout)

    def test_tampered_xyxy_source_value_is_detected(self) -> None:
        workdir = copy_artifacts("tamper_xyxy")
        target = workdir / "gate_evidence_projection.json"
        payload = json.loads(target.read_text(encoding="utf-8"))
        payload["records"][0]["detections"][0]["xyxy"][0] = 0.25
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        proc = run_checker(workdir)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)

    def test_synthetic_relabel_is_detected(self) -> None:
        cases = (("frames.json", lambda p: p.update({"input_kind": "synthetic_replay"})),
                 ("consumer_report.json", lambda p: p.update({"evidence_kind": "synthetic_replay"})),
                 ("gate_evidence_projection.json",
                  lambda p: p["records"][0].update({"source_kind": "synthetic"})))
        for name, mutate in cases:
            with self.subTest(target=name):
                workdir = copy_artifacts(f"tamper_label_{name}")
                target = workdir / name
                payload = json.loads(target.read_text(encoding="utf-8"))
                mutate(payload)
                target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
                proc = run_checker(workdir)
                self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                self.assertIn("labels", proc.stdout)

    def test_canvas_declared_by_artifact_is_not_trusted(self) -> None:
        """检查器从冻结包重解析画布：篡改产物画布声明不得影响像素重算结果。"""
        workdir = copy_artifacts("tamper_canvas")
        target = workdir / "gate_evidence_projection.json"
        payload = json.loads(target.read_text(encoding="utf-8"))
        payload["records"][0]["geometry"]["display_canvas"] = [1280, 720]
        payload["records"][0]["detections"][0]["xyxy_px_canvas"] = [1280, 720]
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        proc = run_checker(workdir)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_end_to_end_latency_injection_guard(self) -> None:
        frame = {"mode": "FILE_INJECTION", "capture_time_available": False, "capture_time_ns": 0,
                 "injection_start_ns": 999, "stale_evaluation": C.STALE_EVALUATION_NOT_RUN}
        basis = C.resolve_timing(frame, state="OK")
        record = {"timing_basis": basis, "capture_time_ns": 0, "end_to_end_latency_ns": 123,
                  "result_time_ns": None}
        problems = CHK.check_timing_basis(record, where="tamper[0]")
        self.assertTrue(any("端到端延迟必须不可定义" in p for p in problems), problems)
        record["end_to_end_latency_ns"] = None
        self.assertEqual(CHK.check_timing_basis(record, where="ok[0]"), [])

    def test_injection_start_as_capture_is_flagged_by_checker(self) -> None:
        frame = {"mode": "camera", "capture_time_available": True, "capture_time_ns": 5,
                 "injection_start_ns": None}
        basis = C.resolve_timing(frame, state="OK")
        basis["injection_start_ns"] = 5
        record = {"timing_basis": basis, "capture_time_ns": 5, "end_to_end_latency_ns": None,
                  "result_time_ns": None}
        problems = CHK.check_timing_basis(record, where="tamper[1]")
        self.assertTrue(any("等于 injection_start_ns" in p for p in problems), problems)


if __name__ == "__main__":
    unittest.main(verbosity=2)