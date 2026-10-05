"""用合成记录测试 T68 源快照到冻结 Git tree 的绑定检查。"""

from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
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
    ) -> None:
        """构造合成记录，可选跳过一个固定样本目录。"""
        manifest_sources = self.closure["sources"]
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


if __name__ == "__main__":
    unittest.main()
