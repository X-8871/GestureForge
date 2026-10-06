"""用合成记录核验 T68 跨 RunId 恢复清单与旧工具闭包。"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from verification import s2a_t68_recovery_manifest as recovery
from verification import test_s2a_t68_snapshot_git_binding as snapshot_tests
from verification import verify_s2a_t68_snapshot_git_binding as snapshot
try:
    from verification import verify_s2a_t68_d9_outputs as d9
except ModuleNotFoundError as error:
    if error.name != "cv2":
        raise
    d9 = None


def _write_json(path: Path, value: dict[str, Any]) -> bytes:
    """以固定 UTF-8 编码写入合成 JSON。"""
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


def _sha(path: Path) -> str:
    """计算测试证据文件摘要。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _race_exclusive_create(target: Path, sentinel: bytes, original_open: Any) -> Any:
    """模拟检查与独占打开之间另一个进程先创建目标文件。"""
    def open_with_race(path: Path, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if path == target and mode == "xb":
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
            descriptor = os.open(os.fspath(path), flags, 0o666)
            try:
                os.write(descriptor, sentinel)
            finally:
                os.close(descriptor)
            raise FileExistsError(17, "simulated concurrent exclusive create", os.fspath(path))
        return original_open(path, mode, *args, **kwargs)

    return open_with_race


class RecoveryManifestTests(unittest.TestCase):
    """覆盖混合 RunId 成功路径、哈希篡改与 D9 历史 tooling 验证。"""

    @classmethod
    def setUpClass(cls) -> None:
        """从明确 commit/tree 读取两组测试闭包。"""
        cls.new_commit = subprocess.run(
            ["git", "-C", str(snapshot.ROOT), "rev-parse", "--verify", "HEAD^{commit}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout.decode("ascii").strip()
        cls.new_tree = subprocess.run(
            ["git", "-C", str(snapshot.ROOT), "rev-parse", "--verify", "HEAD^{tree}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout.decode("ascii").strip()
        cls.old_closure = snapshot.load_candidate_closure(snapshot.ROOT, recovery.OLD_COMMIT, recovery.OLD_TREE)
        cls.new_closure = snapshot.load_candidate_closure(snapshot.ROOT, cls.new_commit, cls.new_tree)

    def make_mixed_recovery(self, temporary: Path) -> tuple[Path, Path, dict[str, Any]]:
        """构造旧 0..24、新 25..108 分属两棵 Git tree 的记录。"""
        evidence_root = temporary / recovery.OLD_RUN_ID
        evidence_root.mkdir()
        old_evidence = temporary / "old_source"
        new_evidence = temporary / "new_source"
        harness = snapshot_tests.SnapshotGitBindingTests()
        harness.make_batch(old_evidence, run_id=recovery.OLD_RUN_ID, closure=self.old_closure)
        new_run_id = "synthetic_recovery_new"
        harness.make_batch(new_evidence, run_id=new_run_id, closure=self.new_closure)
        for index in range(25):
            source = old_evidence / "runs" / f"sample_{index:03d}" / recovery.OLD_RUN_ID
            target = evidence_root / "runs" / f"sample_{index:03d}" / recovery.OLD_RUN_ID
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, target)
            self.rebind_synthetic_run(target, recovery.OLD_RUN_ID, index)
        for index in range(25, 109):
            source = new_evidence / "runs" / f"sample_{index:03d}" / new_run_id
            target = evidence_root / "runs" / f"sample_{index:03d}" / new_run_id
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, target)
            self.rebind_synthetic_run(target, new_run_id, index)

        dispatch_name = "batch_dispatch_recovery_synthetic"
        dispatch_dir = evidence_root / dispatch_name
        dispatch_dir.mkdir()
        _write_json(dispatch_dir / "scheduler_source_snapshot.json", {
            "schema_version": "gestureforge_s2a_t68_batch_scheduler_source_v1",
            "path": str(snapshot.ROOT / "verification/run_s2a_t68_batch_verilator.ps1"),
            "bytes": 1,
            "sha256": "0" * 64,
            "frozen_utc": "2026-10-07T00:00:00Z",
        })
        summary_events: list[dict[str, Any]] = []
        for index in range(25, 109):
            sample_dir = dispatch_dir
            stdout_path = dispatch_dir / f"sample_{index:03d}.stdout.log"
            stderr_path = dispatch_dir / f"sample_{index:03d}.stderr.log"
            stdout_path.write_bytes(f"sample={index} stdout\n".encode("utf-8"))
            stderr_path.write_bytes(b"")
            run_dir = evidence_root / "runs" / f"sample_{index:03d}" / new_run_id
            record_paths = {
                "compile_source_snapshot.json": run_dir / "compile_source_snapshot.json",
                "compile_execution_record.json": run_dir / "compile_execution_record.json",
                "simulation_execution_record.json": run_dir / "simulation_execution_record.json",
            }
            event_path = dispatch_dir / f"sample_{index:03d}_event.json"
            event = {
                "schema_version": "gestureforge_s2a_t68_batch_event_v1",
                "sample_index": index,
                "run_id": new_run_id,
                "status": "PASS_RUNNER_AND_RECORDS",
                "runner_exit_code": 0,
                "process_id": index,
                "process_started_utc": "2026-10-07T00:00:00Z",
                "process_finished_utc": "2026-10-07T00:00:01Z",
                "stdout_path": str(stdout_path),
                "stdout_sha256": _sha(stdout_path),
                "stdout_bytes": stdout_path.stat().st_size,
                "stdout_read_attempts": 1,
                "stdout_read_error": None,
                "stderr_path": str(stderr_path),
                "stderr_sha256": _sha(stderr_path),
                "stderr_bytes": stderr_path.stat().st_size,
                "stderr_read_attempts": 1,
                "stderr_read_error": None,
                "validated_records": {
                    "compile_snapshot_sha256": _sha(record_paths["compile_source_snapshot.json"]),
                    "compile_record_sha256": _sha(record_paths["compile_execution_record.json"]),
                    "simulation_record_sha256": _sha(record_paths["simulation_execution_record.json"]),
                },
                "failure": None,
            }
            event_raw = _write_json(event_path, event)
            summary_events.append({
                "sample_index": index,
                "path": str(event_path),
                "sha256": hashlib.sha256(event_raw).hexdigest(),
                "write_error": None,
            })
        _write_json(dispatch_dir / "batch_summary.json", {
            "schema_version": "gestureforge_s2a_t68_batch_summary_v1",
            "status": "PASS_RESUMED_84_RUNNERS",
            "evidence_directory": str(evidence_root),
            "run_id": new_run_id,
            "recovery_mode": True,
            "first_index": 25,
            "last_index": 108,
            "succeeded_indices": list(range(25, 109)),
            "failed_indices": [],
            "remaining_indices": [],
            "events": summary_events,
        })
        path, manifest, _ = recovery.create_manifest(
            evidence_root,
            new_run_id,
            self.new_commit,
            self.new_tree,
            dispatch_name,
            "recovery_manifest_synthetic",
        )
        return evidence_root, path, manifest

    @staticmethod
    def rebind_synthetic_run(run_dir: Path, run_id: str, sample_index: int) -> None:
        """将合成 compile argv 与移动后的测试 evidence 路径重新绑定。"""
        snapshot_path = run_dir / "compile_source_snapshot.json"
        compile_path = run_dir / "compile_execution_record.json"
        simulation_path = run_dir / "simulation_execution_record.json"
        source_snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        compile_record = json.loads(compile_path.read_text(encoding="utf-8"))
        simulation_record = json.loads(simulation_path.read_text(encoding="utf-8"))
        source_snapshot["command"][6] = str(run_dir / "build")
        compile_record["command"] = [compile_record["verilator_path"], *source_snapshot["command"]]
        snapshot_raw = _write_json(snapshot_path, source_snapshot)
        compile_raw = _write_json(compile_path, compile_record)
        simulation_record["compile_source_snapshot_sha256"] = hashlib.sha256(snapshot_raw).hexdigest()
        simulation_record["compile_execution_record_sha256"] = hashlib.sha256(compile_raw).hexdigest()
        _write_json(simulation_path, simulation_record)

    def test_two_run_id_manifest_and_snapshot_tree_verification(self) -> None:
        """完整恢复清单应按各组不同 commit/tree 验证并精确覆盖 109 行。"""
        with tempfile.TemporaryDirectory(prefix="s2a_t68_recovery_mixed_") as temporary:
            evidence_root, manifest_path, manifest = self.make_mixed_recovery(Path(temporary))
            report = snapshot.verify_recovery_batch(evidence_root, manifest_path)
            self.assertEqual(report["status"], "PASS_109_CROSS_RUNID_RECOVERY_SOURCE_SNAPSHOT_TO_GIT_TREE")
            self.assertEqual([row["sample_index"] for row in manifest["samples"]], list(range(109)))
            self.assertEqual(manifest["samples"][0]["candidate_commit"], recovery.OLD_COMMIT)
            self.assertEqual(manifest["samples"][24]["candidate_tree"], recovery.OLD_TREE)
            self.assertEqual(manifest["samples"][25]["candidate_commit"], self.new_commit)
            self.assertEqual(report["groups"][0]["sample_range"], [0, 24])
            self.assertEqual(report["groups"][1]["sample_range"], [25, 108])
            self.assertEqual(len(report["samples"]), 109)
            self.assertEqual(json.loads(manifest_path.read_text(encoding="utf-8")), manifest)

            report_path, report_sha = snapshot._write_new_recovery_report(
                evidence_root, "synthetic_recovery_new", report
            )
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8")), report)
            self.assertEqual(hashlib.sha256(report_path.read_bytes()).hexdigest(), report_sha)

            original_open = Path.open
            manifest_sentinel = b"manifest sentinel must survive\n"
            manifest_race_path = evidence_root / "recovery_manifest_race.json"
            with patch.object(
                Path,
                "open",
                new=_race_exclusive_create(manifest_race_path, manifest_sentinel, original_open),
            ):
                with self.assertRaisesRegex(recovery.RecoveryManifestError, "请使用新名称重试"):
                    recovery.create_manifest(
                        evidence_root,
                        manifest["new_group"]["run_id"],
                        self.new_commit,
                        self.new_tree,
                        manifest["dispatch"]["name"],
                        "recovery_manifest_race",
                    )
            self.assertEqual(manifest_race_path.read_bytes(), manifest_sentinel)

            report_sentinel = b"report sentinel must survive\n"
            report_race_path = evidence_root / "source_snapshot_git_binding_recovery_synthetic_recovery_race.json"
            with patch.object(
                Path,
                "open",
                new=_race_exclusive_create(report_race_path, report_sentinel, original_open),
            ):
                with self.assertRaisesRegex(snapshot.SnapshotBindingError, "请使用新名称重试"):
                    snapshot._write_new_recovery_report(evidence_root, "synthetic_recovery_race", report)
            self.assertEqual(report_race_path.read_bytes(), report_sentinel)

            changed = json.loads(manifest_path.read_text(encoding="utf-8"))
            changed["samples"][0]["record_sha256"]["compile_execution_record.json"] = "f" * 64
            manifest_path.write_text(json.dumps(changed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(snapshot.SnapshotBindingError):
                snapshot.verify_recovery_batch(evidence_root, manifest_path)

    def test_old_commit_tree_policy_rejects_runner_only_candidate(self) -> None:
        """旧组不能改绑到只匹配 runner 的 commit/tree。"""
        with tempfile.TemporaryDirectory(prefix="s2a_t68_recovery_policy_") as temporary:
            evidence_root = Path(temporary)
            dispatch_name = "dispatch"
            dispatch_dir = evidence_root / dispatch_name
            dispatch_dir.mkdir()
            summary_raw = _write_json(dispatch_dir / "batch_summary.json", {
                "status": "PASS_RESUMED_84_RUNNERS",
                "run_id": "synthetic_new",
                "recovery_mode": True,
                "first_index": 25,
                "last_index": 108,
            })
            scheduler_raw = _write_json(dispatch_dir / "scheduler_source_snapshot.json", {})
            manifest = {
                "schema_version": recovery.SCHEMA,
                "status": "PASS_109_RECOVERY_MANIFEST",
                "sample_count": 109,
                "evidence_root": str(evidence_root),
                "old_group": {
                    "run_id": recovery.OLD_RUN_ID,
                    "candidate_commit": "a1298dbc4b41eb9ac54caca77e18fd00bee30538",
                    "candidate_tree": "dbac6be3f860e1ade64eaf55add4e1915ea74545",
                    "first_index": 0,
                    "last_index": 24,
                    "binding_scope": "11_rtl_sources_plus_3_tooling_sources",
                },
                "new_group": {
                    "run_id": "synthetic_new",
                    "candidate_commit": self.new_commit,
                    "candidate_tree": self.new_tree,
                    "first_index": 25,
                    "last_index": 108,
                    "binding_scope": "11_rtl_sources_plus_3_tooling_sources",
                },
                "dispatch": {
                    "name": dispatch_name,
                    "batch_summary_sha256": hashlib.sha256(summary_raw).hexdigest(),
                    "scheduler_snapshot_sha256": hashlib.sha256(scheduler_raw).hexdigest(),
                    "events": [],
                },
                "samples": [],
            }
            with self.assertRaises(recovery.RecoveryManifestError):
                recovery.validate_manifest(manifest, evidence_root)

    def test_manifest_load_rejects_different_nonbackend_compile_source(self) -> None:
        """即使 backend 相同，manifest 也必须拒绝其他编译源不同的 candidate tree。"""
        mismatched_commit = "a1298dbc4b41eb9ac54caca77e18fd00bee30538"
        mismatched_tree = "dbac6be3f860e1ade64eaf55add4e1915ea74545"
        mismatched_closure = snapshot.load_candidate_closure(snapshot.ROOT, mismatched_commit, mismatched_tree)
        old_backend_sha = self.old_closure["sources"]["src/s2a_network_backend.sv"]["sha256"]
        self.assertEqual(mismatched_closure["sources"]["src/s2a_network_backend.sv"]["sha256"], old_backend_sha)
        self.assertNotEqual(
            mismatched_closure["sources"]["src/int8_maxpool_geometry.sv"]["sha256"],
            self.old_closure["sources"]["src/int8_maxpool_geometry.sv"]["sha256"],
        )

        with tempfile.TemporaryDirectory(prefix="s2a_t68_source_closure_mismatch_") as temporary:
            evidence_root = Path(temporary) / recovery.OLD_RUN_ID
            evidence_root.mkdir()
            source_mismatch_error = r"^旧/新 candidate 编译源 SHA 不一致：src/int8_maxpool_geometry\.sv$"
            with self.assertRaisesRegex(recovery.RecoveryManifestError, source_mismatch_error):
                recovery.preflight(
                    evidence_root,
                    "synthetic_new",
                    mismatched_commit,
                    mismatched_tree,
                    "dispatch",
                    "manifest",
                )
            with self.assertRaisesRegex(recovery.RecoveryManifestError, source_mismatch_error):
                recovery.verify_recovery_samples(
                    evidence_root,
                    recovery.OLD_COMMIT,
                    recovery.OLD_TREE,
                    "synthetic_new",
                    mismatched_commit,
                    mismatched_tree,
                )

            manifest = {
                "schema_version": recovery.SCHEMA,
                "status": "PASS_109_RECOVERY_MANIFEST",
                "sample_count": 109,
                "evidence_root": str(evidence_root),
                "old_group": {
                    "run_id": recovery.OLD_RUN_ID,
                    "candidate_commit": recovery.OLD_COMMIT,
                    "candidate_tree": recovery.OLD_TREE,
                    "first_index": 0,
                    "last_index": 24,
                    "binding_scope": "11_rtl_sources_plus_3_tooling_sources",
                },
                "new_group": {
                    "run_id": "synthetic_new",
                    "candidate_commit": mismatched_commit,
                    "candidate_tree": mismatched_tree,
                    "first_index": 25,
                    "last_index": 108,
                    "binding_scope": "11_rtl_sources_plus_3_tooling_sources",
                },
            }
            with self.assertRaisesRegex(recovery.RecoveryManifestError, source_mismatch_error):
                recovery.validate_manifest(manifest, evidence_root)

            manifest_path = evidence_root / "mismatched_candidate.json"
            _write_json(manifest_path, manifest)
            with self.assertRaisesRegex(recovery.RecoveryManifestError, source_mismatch_error):
                recovery.load_manifest(manifest_path, evidence_root)

    @unittest.skipIf(d9 is None, "当前固定 Python 环境缺少 cv2，跳过 D9 tooling map 单测")
    def test_d9_accepts_historical_tool_hash_only_through_git_binding_map(self) -> None:
        """旧 runner 当前文件哈希不同，但经 candidate Git 闭包验证后可用于 D9。"""
        with tempfile.TemporaryDirectory(prefix="s2a_t68_d9_old_tooling_") as temporary:
            sample_dir = Path(temporary)
            rows = []
            expected: dict[str, dict[str, Any]] = {}
            for relative in snapshot.COMPILE_TOOLING_PATHS:
                source = self.old_closure["sources"][relative]
                path = snapshot.ROOT.joinpath(*Path(relative).parts)
                rows.append({"path": str(path), "bytes": source["bytes"], "sha256": source["sha256"]})
                expected[d9.canonical_path(path)] = {"bytes": source["bytes"], "sha256": source["sha256"]}
            record = {
                "tooling_sources": rows,
                "runner_path": rows[0]["path"],
                "runner_sha256": rows[0]["sha256"],
            }
            checked = d9.verify_tooling_bindings(record, sample_dir, "old group", expected)
            self.assertEqual(len(checked), 3)
            self.assertEqual(rows[0]["sha256"], "9da435c5abd8cedcf9a59a8d92433e72c149dcaa008c472e68c2c4530bab7e4d")
            record["runner_sha256"] = "0" * 64
            with self.assertRaises(d9.D9VerificationError):
                d9.verify_tooling_bindings(record, sample_dir, "old group", expected)


if __name__ == "__main__":
    unittest.main()
