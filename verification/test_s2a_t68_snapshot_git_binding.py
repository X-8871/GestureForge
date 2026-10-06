"""用合成记录测试 T68 源快照到冻结 Git tree 的绑定检查。"""

from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from verification import verify_s2a_t68_snapshot_git_binding as checker


def _write_json(path: Path, value: dict[str, Any]) -> bytes:
    """以确定的 UTF-8 格式保存合成 JSON 并返回原始字节。"""
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


class SnapshotGitBindingTests(unittest.TestCase):
    """覆盖全量成功、源映射失败和执行记录哈希失败。"""

    @classmethod
    def setUpClass(cls) -> None:
        """只加载并验证一次固定静态闭包。"""
        cls.closure = checker.load_pinned_closure()

    def make_batch(
        self,
        evidence_root: Path,
        run_id: str = "synthetic109",
        omit_sample_index: int | None = None,
        closure: dict[str, Any] | None = None,
    ) -> None:
        """构造合成记录，可选跳过一个固定样本目录。"""
        manifest_sources = (closure or self.closure)["sources"]
        source_rows = [
            {
                "path": str(checker.ROOT / Path(*Path(relative).parts)),
                "sha256": manifest_sources[relative]["sha256"],
                "bytes": manifest_sources[relative]["bytes"],
            }
            for relative in checker.COMPILE_SOURCE_PATHS
        ]
        tooling_rows = [
            {
                "path": str(checker.ROOT / Path(*Path(relative).parts)),
                "sha256": manifest_sources[relative]["sha256"],
                "bytes": manifest_sources[relative]["bytes"],
            }
            for relative in checker.COMPILE_TOOLING_PATHS
        ]
        verilator_path = checker.VERILATOR_PATH
        backend_sha = manifest_sources["src/s2a_network_backend.sv"]["sha256"]
        runner_path = str(checker.ROOT / Path(*Path(checker.COMPILE_TOOLING_PATHS[0]).parts))
        runner_sha = manifest_sources[checker.COMPILE_TOOLING_PATHS[0]]["sha256"]

        for sample_index in range(checker.SAMPLE_COUNT):
            if sample_index == omit_sample_index:
                continue
            sample_dir = evidence_root / "runs" / f"sample_{sample_index:03d}" / run_id
            command_args = [
                "--binary",
                "--timing",
                "-Wno-fatal",
                "--top-module",
                checker.TOP_MODULE,
                "--Mdir",
                str(sample_dir / "build"),
                "-CFLAGS",
                checker.ABI_CFLAGS,
                *[str(checker.ROOT / Path(*Path(relative).parts)) for relative in checker.COMPILE_SOURCE_PATHS],
            ]
            snapshot = {
                "schema_version": checker.COMPILED_SOURCE_SCHEMA,
                "task_id": checker.TASK_ID,
                "sample_index": sample_index,
                "run_id": run_id,
                "top_module": checker.TOP_MODULE,
                "backend_sha256_expected": backend_sha,
                "source_count": len(checker.COMPILE_SOURCE_PATHS),
                "verilator_path": verilator_path,
                "simulator_started": False,
                "command": command_args,
                "sources": copy.deepcopy(source_rows),
                "tooling_sources": copy.deepcopy(tooling_rows),
            }
            compile_record = {
                "schema_version": checker.COMPILE_RECORD_SCHEMA,
                "sample_index": sample_index,
                "run_id": run_id,
                "exit_code": 0,
                "simulator_started": False,
                "native_exit_code": 0,
                "compile_accepted": True,
                "launch_error": "",
                "warning_gate": "-Wno-fatal",
                "warning_count": 0,
                "error_count": 0,
                "warning_text_retained": True,
                "source_unchanged": True,
                "tooling_sources_unchanged": True,
                "command": [verilator_path, *command_args],
                "verilator_path": verilator_path,
                "backend_sha256_expected": backend_sha,
                "sources_after": copy.deepcopy(source_rows),
                "tooling_sources": copy.deepcopy(tooling_rows),
                "tooling_sources_after": copy.deepcopy(tooling_rows),
                "runner_path": runner_path,
                "runner_sha256": runner_sha,
            }
            snapshot_raw = _write_json(sample_dir / "compile_source_snapshot.json", snapshot)
            compile_raw = _write_json(sample_dir / "compile_execution_record.json", compile_record)
            simulation_record = {
                "schema_version": checker.SIMULATION_RECORD_SCHEMA,
                "sample_index": sample_index,
                "run_id": run_id,
                "compile_source_snapshot_sha256": hashlib.sha256(snapshot_raw).hexdigest(),
                "compile_execution_record_sha256": hashlib.sha256(compile_raw).hexdigest(),
                "tooling_sources": copy.deepcopy(tooling_rows),
                "runner_path": runner_path,
                "runner_sha256": runner_sha,
            }
            _write_json(sample_dir / "simulation_execution_record.json", simulation_record)

    def assert_cli_failure_without_report(self, evidence_root: Path, run_id: str = "synthetic109") -> None:
        """确认损坏夹具令 CLI 失败且不创建报告。"""
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            result = checker.main(["--evidence-root", str(evidence_root), "--run-id", run_id])
        self.assertEqual(result, 2, stderr.getvalue())
        self.assertFalse((evidence_root / f"source_snapshot_git_binding_{run_id}.json").exists())

    def test_full_109_sample_batch_passes(self) -> None:
        """完整合成样本必须精确覆盖 0..108 且报告范围受限。"""
        with tempfile.TemporaryDirectory(prefix="s2a_t68_snapshot_pass_") as temporary:
            evidence_root = Path(temporary)
            self.make_batch(evidence_root)
            report = checker.verify_batch(evidence_root, "synthetic109")
        self.assertEqual(report["status"], "PASS_109_SOURCE_SNAPSHOT_TO_GIT_TREE")
        self.assertEqual(report["sample_count"], 109)
        self.assertEqual([row["sample_index"] for row in report["samples"]], list(range(109)))
        self.assertEqual(len(report["samples"][0]["compile_sources"]), 11)
        self.assertEqual(len(report["samples"][0]["compile_tooling_sources"]), 3)
        self.assertIn("不证明仿真完成", report["scope"])

    def test_worktree_blob_check_is_limited_to_compiled_sources_and_tooling(self) -> None:
        """冻结闭包的辅助源码按 baseline tree 核验，不要求当前工作树未变。"""
        actual_run = checker.subprocess.run
        checked_paths: list[str] = []

        def record_git_call(command: list[str], *args: Any, **kwargs: Any) -> Any:
            if len(command) > 3 and command[3] == "hash-object":
                checked_paths.append(Path(command[-1]).relative_to(checker.ROOT).as_posix())
            return actual_run(command, *args, **kwargs)

        with mock.patch.object(checker.subprocess, "run", side_effect=record_git_call):
            closure = checker.load_pinned_closure()

        self.assertEqual(checked_paths, list(checker.COMPILE_SOURCE_PATHS + checker.COMPILE_TOOLING_PATHS))
        self.assertEqual(len(closure["sources"]), 38)

    def test_wrong_source_hash_fails_without_output(self) -> None:
        """错误的编译源哈希必须失败，且不留下结果报告。"""
        with tempfile.TemporaryDirectory(prefix="s2a_t68_snapshot_wrong_") as temporary:
            evidence_root = Path(temporary)
            self.make_batch(evidence_root)
            snapshot_path = evidence_root / "runs" / "sample_017" / "synthetic109" / "compile_source_snapshot.json"
            snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
            snapshot["sources"][0]["sha256"] = "0" * 64
            _write_json(snapshot_path, snapshot)
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = checker.main(["--evidence-root", str(evidence_root), "--run-id", "synthetic109"])
            self.assertEqual(result, 2)
            self.assertIn("SHA-256", stderr.getvalue())
            self.assertFalse((evidence_root / "source_snapshot_git_binding_synthetic109.json").exists())

    def test_missing_source_row_fails(self) -> None:
        """少一个批准编译源时必须失败关闭。"""
        with tempfile.TemporaryDirectory(prefix="s2a_t68_snapshot_missing_") as temporary:
            evidence_root = Path(temporary)
            self.make_batch(evidence_root)
            snapshot_path = evidence_root / "runs" / "sample_000" / "synthetic109" / "compile_source_snapshot.json"
            snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
            snapshot["sources"].pop()
            _write_json(snapshot_path, snapshot)
            with self.assertRaises(checker.SnapshotBindingError):
                checker.verify_batch(evidence_root, "synthetic109")
            self.assertFalse((evidence_root / "source_snapshot_git_binding_synthetic109.json").exists())

    def test_record_hash_binding_failure_fails_without_output(self) -> None:
        """simulation record 错绑 compile record 哈希时必须失败。"""
        with tempfile.TemporaryDirectory(prefix="s2a_t68_snapshot_record_hash_") as temporary:
            evidence_root = Path(temporary)
            self.make_batch(evidence_root)
            simulation_path = evidence_root / "runs" / "sample_108" / "synthetic109" / "simulation_execution_record.json"
            simulation = json.loads(simulation_path.read_text(encoding="utf-8"))
            simulation["compile_execution_record_sha256"] = "f" * 64
            _write_json(simulation_path, simulation)
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = checker.main(["--evidence-root", str(evidence_root), "--run-id", "synthetic109"])
            self.assertEqual(result, 2)
            self.assertIn("compile SHA", stderr.getvalue())
            self.assertFalse((evidence_root / "source_snapshot_git_binding_synthetic109.json").exists())

    def test_cli_writes_new_report_and_refuses_overwrite(self) -> None:
        """CLI 只在通过后写新报告，并拒绝覆盖既有报告。"""
        with tempfile.TemporaryDirectory(prefix="s2a_t68_snapshot_cli_") as temporary:
            evidence_root = Path(temporary)
            self.make_batch(evidence_root)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(checker.main(["--evidence-root", str(evidence_root), "--run-id", "synthetic109"]), 0)
            report_path = evidence_root / "source_snapshot_git_binding_synthetic109.json"
            original = report_path.read_bytes()
            report = json.loads(original.decode("utf-8"))
            self.assertEqual(report["status"], checker.REPORT_STATUS)
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                self.assertEqual(checker.main(["--evidence-root", str(evidence_root), "--run-id", "synthetic109"]), 2)
            self.assertEqual(report_path.read_bytes(), original)

    def test_tooling_sources_after_fail_closed(self) -> None:
        """post-compile tooling 列表必须完整、唯一且逐项匹配。"""
        cases = (
            ("missing", lambda rows: rows.pop()),
            ("wrong_sha", lambda rows: rows[0].update(sha256="0" * 64)),
            ("wrong_bytes", lambda rows: rows[0].update(bytes=rows[0]["bytes"] + 1)),
            ("extra", lambda rows: rows.append(copy.deepcopy(rows[0]) | {"path": str(checker.ROOT / "verification/extra.py")})),
            ("duplicate", lambda rows: rows.__setitem__(1, copy.deepcopy(rows[0]))),
        )
        for case_name, mutate in cases:
            with self.subTest(case=case_name), tempfile.TemporaryDirectory(prefix=f"s2a_t68_tooling_after_{case_name}_") as temporary:
                evidence_root = Path(temporary)
                self.make_batch(evidence_root)
                record_path = evidence_root / "runs" / "sample_000" / "synthetic109" / "compile_execution_record.json"
                record = json.loads(record_path.read_text(encoding="utf-8"))
                mutate(record["tooling_sources_after"])
                _write_json(record_path, record)
                self.assert_cli_failure_without_report(evidence_root)

    def test_compile_argv_contract_fail_closed(self) -> None:
        """改变固定参数、Mdir 或有序源操作数必须失败且不留报告。"""
        cases = (
            ("altered_argument", lambda snapshot: snapshot["command"].__setitem__(1, "--no-timing")),
            ("removed_argument", lambda snapshot: snapshot["command"].pop(0)),
            ("wrong_mdir", lambda snapshot: snapshot["command"].__setitem__(6, str(checker.ROOT / "other_build"))),
            ("missing_source", lambda snapshot: snapshot["command"].pop()),
            ("replaced_source", lambda snapshot: snapshot["command"].__setitem__(-1, str(checker.ROOT / "src/s2a_network_backend.sv"))),
        )
        for case_name, mutate in cases:
            with self.subTest(case=case_name), tempfile.TemporaryDirectory(prefix=f"s2a_t68_argv_{case_name}_") as temporary:
                evidence_root = Path(temporary)
                self.make_batch(evidence_root)
                sample_dir = evidence_root / "runs" / "sample_000" / "synthetic109"
                snapshot_path = sample_dir / "compile_source_snapshot.json"
                compile_path = sample_dir / "compile_execution_record.json"
                snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
                compile_record = json.loads(compile_path.read_text(encoding="utf-8"))
                mutate(snapshot)
                compile_record["command"] = [compile_record["verilator_path"], *snapshot["command"]]
                _write_json(snapshot_path, snapshot)
                _write_json(compile_path, compile_record)
                self.assert_cli_failure_without_report(evidence_root)

    def test_snapshot_command_metadata_fail_closed(self) -> None:
        """task、top、源数量和 Verilator 路径字段必须与批准配置一致。"""
        cases = (
            ("wrong_task", lambda snapshot, compile_record: snapshot.update(task_id="S2A-T99")),
            ("wrong_top", lambda snapshot, compile_record: snapshot.update(top_module="wrong_top")),
            ("wrong_source_count", lambda snapshot, compile_record: snapshot.update(source_count=10)),
            ("wrong_verilator", lambda snapshot, compile_record: snapshot.update(verilator_path="C:/other/verilator.exe")),
        )
        for case_name, mutate in cases:
            with self.subTest(case=case_name), tempfile.TemporaryDirectory(prefix=f"s2a_t68_metadata_{case_name}_") as temporary:
                evidence_root = Path(temporary)
                self.make_batch(evidence_root)
                sample_dir = evidence_root / "runs" / "sample_000" / "synthetic109"
                snapshot_path = sample_dir / "compile_source_snapshot.json"
                compile_path = sample_dir / "compile_execution_record.json"
                snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
                compile_record = json.loads(compile_path.read_text(encoding="utf-8"))
                mutate(snapshot, compile_record)
                _write_json(snapshot_path, snapshot)
                _write_json(compile_path, compile_record)
                self.assert_cli_failure_without_report(evidence_root)

    def test_exact_run_directory_set_fail_closed(self) -> None:
        """RunId 目录必须恰好对应 sample_000..sample_108。"""
        cases = ("missing_sample", "extra_sample_109")
        for case_name in cases:
            with self.subTest(case=case_name), tempfile.TemporaryDirectory(prefix=f"s2a_t68_directory_set_{case_name}_") as temporary:
                evidence_root = Path(temporary)
                if case_name == "missing_sample":
                    self.make_batch(evidence_root, omit_sample_index=108)
                else:
                    self.make_batch(evidence_root)
                    (evidence_root / "runs" / "sample_109" / "synthetic109").mkdir(parents=True)
                self.assert_cli_failure_without_report(evidence_root)

    def test_source_row_path_escape_fails_without_report(self) -> None:
        """仓库外的编译源路径必须令 CLI 失败且不留报告。"""
        with tempfile.TemporaryDirectory(prefix="s2a_t68_source_path_escape_") as temporary:
            evidence_root = Path(temporary)
            self.make_batch(evidence_root)
            snapshot_path = evidence_root / "runs" / "sample_000" / "synthetic109" / "compile_source_snapshot.json"
            snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
            snapshot["sources"][0]["path"] = str(evidence_root / "outside_source.sv")
            _write_json(snapshot_path, snapshot)
            self.assert_cli_failure_without_report(evidence_root)


class CandidateSnapshotGitBindingTests(unittest.TestCase):
    """覆盖显式 candidate commit/tree 的 Git object 绑定路径。"""

    @classmethod
    def setUpClass(cls) -> None:
        """从当前 HEAD 自动选取可复现的 candidate commit/tree。"""
        cls.candidate_commit = subprocess.run(
            ["git", "-C", str(checker.ROOT), "rev-parse", "--verify", "HEAD^{commit}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout.decode("ascii").strip()
        cls.candidate_tree = subprocess.run(
            ["git", "-C", str(checker.ROOT), "rev-parse", "--verify", "HEAD^{tree}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout.decode("ascii").strip()
        cls.mismatched_tree = checker.BASELINE_TREE
        if cls.mismatched_tree == cls.candidate_tree:
            cls.mismatched_tree = subprocess.run(
                ["git", "-C", str(checker.ROOT), "rev-parse", "--verify", f"{cls.candidate_commit}^1^{{tree}}"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).stdout.decode("ascii").strip()
        if cls.mismatched_tree == cls.candidate_tree:
            raise RuntimeError("测试需要一个与 candidate tree 不同的有效 Git tree")
        cls.closure = checker.load_candidate_closure(checker.ROOT, cls.candidate_commit, cls.candidate_tree)

    def test_candidate_closure_uses_git_objects_and_fixed_38_source_scope(self) -> None:
        """候选清单按给定 commit/tree 读取全部 Git objects 并保留 11+3 编译分类。"""
        self.assertEqual(len(self.closure["sources"]), 38)
        self.assertEqual(len(checker.COMPILE_SOURCE_PATHS), 11)
        self.assertEqual(len(checker.COMPILE_TOOLING_PATHS), 3)
        for relative, row in self.closure["sources"].items():
            object_id = subprocess.run(
                ["git", "-C", str(checker.ROOT), "rev-parse", "--verify", f"{self.candidate_commit}:{relative}"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).stdout.decode("ascii").strip()
            raw = subprocess.run(
                ["git", "-C", str(checker.ROOT), "cat-file", "blob", object_id],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).stdout
            self.assertEqual(row["git_blob_sha1"], object_id)
            self.assertEqual(row["bytes"], len(raw))
            self.assertEqual(row["sha256"], hashlib.sha256(raw).hexdigest())

    def test_full_109_candidate_snapshot_batch_passes_without_t29_claim(self) -> None:
        """109 个快照逐样本匹配 candidate object，报告明确选择 commit/tree。"""
        with tempfile.TemporaryDirectory(prefix="s2a_t68_candidate_snapshot_pass_") as temporary:
            evidence_root = Path(temporary)
            SnapshotGitBindingTests.make_batch(self, evidence_root, closure=self.closure)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = checker.main(
                    [
                        "--evidence-root",
                        str(evidence_root),
                        "--run-id",
                        "synthetic109",
                        "--candidate-commit",
                        self.candidate_commit,
                        "--candidate-tree",
                        self.candidate_tree,
                    ]
                )
            self.assertEqual(result, 0, output.getvalue())
            report = json.loads(output.getvalue())
            saved_report = json.loads((evidence_root / "source_snapshot_git_binding_synthetic109.json").read_text(encoding="utf-8"))

        self.assertEqual(report["status"], checker.CANDIDATE_REPORT_STATUS)
        self.assertEqual(report["binding_mode"], "candidate_git_commit_tree")
        self.assertEqual(report["sample_count"], 109)
        self.assertEqual(report["static_source_closure"]["candidate_commit"], self.candidate_commit)
        self.assertEqual(report["static_source_closure"]["candidate_tree_sha1"], self.candidate_tree)
        self.assertEqual(report["static_source_closure"]["source_count"], 38)
        self.assertEqual(report["static_source_closure"]["compiled_source_count"], 11)
        self.assertEqual(report["static_source_closure"]["compile_tooling_count"], 3)
        self.assertEqual(report["static_source_closure"]["candidate_git_object_content_verified_count"], 38)
        candidate_sources = {row["path"]: row for row in report["static_source_closure"]["candidate_sources"]}
        self.assertEqual(len(candidate_sources), 38)
        self.assertTrue(set(checker.COMPILE_SOURCE_PATHS).issubset(candidate_sources))
        self.assertTrue(set(checker.COMPILE_TOOLING_PATHS).issubset(candidate_sources))
        for sample in report["samples"]:
            self.assertEqual(len(sample["compile_sources"]), 11)
            self.assertEqual(len(sample["compile_tooling_sources"]), 3)
            for row in sample["compile_sources"] + sample["compile_tooling_sources"]:
                expected = candidate_sources[row["path"]]
                self.assertEqual(row["sha256"], expected["sha256"])
                self.assertEqual(row["bytes"], expected["bytes"])
                self.assertEqual(row["git_blob_sha1"], expected["git_blob_sha1"])
        self.assertNotIn("baseline_commit", report["static_source_closure"])
        self.assertNotIn("baseline_tree_sha1", report["static_source_closure"])
        self.assertNotIn("matches_t29_frozen_binding", json.dumps(report, ensure_ascii=False))
        self.assertIn("不声称与旧 T29 冻结源码绑定", report["scope"])
        self.assertEqual(saved_report["binding_mode"], "candidate_git_commit_tree")

    def test_candidate_tree_mismatch_fails_closed(self) -> None:
        """commit/tree 参数不匹配时必须在遍历样本前失败。"""
        with self.assertRaisesRegex(checker.SnapshotBindingError, "candidate commit 的 tree id 与指定值不符"):
            checker.load_candidate_closure(checker.ROOT, self.candidate_commit, self.mismatched_tree)

    def test_candidate_source_and_runner_mismatches_name_candidate_binding(self) -> None:
        """候选源哈希、字节长度和 runner 哈希错误需指出 candidate 来源。"""
        relative = checker.COMPILE_SOURCE_PATHS[0]
        expected = self.closure["sources"][relative]
        absolute = str(checker.ROOT / Path(*Path(relative).parts))
        wrong_sha_row = {"path": absolute, "sha256": "0" * 64, "bytes": expected["bytes"]}
        with self.assertRaisesRegex(checker.SnapshotBindingError, "candidate Git commit/tree"):
            checker._binding_rows([wrong_sha_row], (relative,), self.closure, checker.ROOT, "sample_000 snapshot sources")

        wrong_length_row = {"path": absolute, "sha256": expected["sha256"], "bytes": expected["bytes"] + 1}
        with self.assertRaisesRegex(checker.SnapshotBindingError, "candidate Git commit/tree"):
            checker._binding_rows([wrong_length_row], (relative,), self.closure, checker.ROOT, "sample_000 snapshot sources")

        runner_relative = checker.COMPILE_TOOLING_PATHS[0]
        wrong_runner_record = {
            "runner_path": str(checker.ROOT / Path(*Path(runner_relative).parts)),
            "runner_sha256": "0" * 64,
        }
        with self.assertRaisesRegex(checker.SnapshotBindingError, "candidate Git commit/tree"):
            checker._require_runner_binding(wrong_runner_record, self.closure, checker.ROOT, "sample_000 compile")

        pinned_closure = dict(self.closure)
        pinned_closure.pop("binding_mode")
        with self.assertRaisesRegex(checker.SnapshotBindingError, "Git baseline"):
            checker._binding_rows([wrong_sha_row], (relative,), pinned_closure, checker.ROOT, "sample_000 snapshot sources")
        with self.assertRaisesRegex(checker.SnapshotBindingError, "Git baseline"):
            checker._binding_rows([wrong_length_row], (relative,), pinned_closure, checker.ROOT, "sample_000 snapshot sources")
        with self.assertRaisesRegex(checker.SnapshotBindingError, "Git baseline"):
            checker._require_runner_binding(wrong_runner_record, pinned_closure, checker.ROOT, "sample_000 compile")

    def test_candidate_cli_requires_both_commit_and_tree(self) -> None:
        """CLI 拒绝只提供 commit 或只提供 tree 的不完整绑定参数。"""
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            result = checker.main(["--evidence-root", str(checker.ROOT), "--run-id", "synthetic109", "--candidate-commit", self.candidate_commit])
        self.assertEqual(result, 2)
        self.assertIn("必须同时提供", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
