"""T25 shard 恢复器的隔离合成测试，不运行真实模型生成器。"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
import zlib
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("restore_s2a_t25_shards.py")
SPEC = importlib.util.spec_from_file_location("restore_s2a_t25_shards_under_test", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
RESTORE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RESTORE)


def _run_git(root: Path, *args: str) -> str:
    """在临时合成仓库中运行 Git 命令。"""
    result = subprocess.run(
        ["git", "-C", os.fspath(root), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise AssertionError(f"临时 Git 命令失败: {args}: {result.stderr}")
    return result.stdout.strip()


class T25ShardRestoreSyntheticTests(unittest.TestCase):
    """验证摘要、基线绑定、发布及拒绝覆盖行为。"""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="s2a-t25-restore-test-")
        self.root = Path(self.temp.name) / "repo"
        self.t25 = self.root / "report" / "evidence" / "S2A-T25"
        self.t25.mkdir(parents=True)
        self.index_path = self.t25 / "cpu_layer_golden_index.json"
        self.generator_path = self.root / RESTORE.GENERATOR_RELATIVE_PATH
        self.generator_path.parent.mkdir(parents=True)
        self.generator_bytes = b"GENERATOR_MARKER = 'frozen'\n"
        self.generator_path.write_bytes(self.generator_bytes)
        self.index_doc = {
            "synthetic": "baseline-index",
            "tooling_bindings": [
                {
                    "role": "t25_exporter",
                    "path": RESTORE.GENERATOR_RELATIVE_PATH,
                    "sha256": hashlib.sha256(self.generator_bytes).hexdigest(),
                }
            ],
        }
        self.index_bytes = (json.dumps(self.index_doc, sort_keys=True) + "\n").encode("utf-8")
        self.index_path.write_bytes(self.index_bytes)
        _run_git(self.root, "init", "--quiet")
        _run_git(self.root, "config", "user.name", "Synthetic Test")
        _run_git(self.root, "config", "user.email", "synthetic@example.invalid")
        _run_git(self.root, "add", "--", RESTORE.INDEX_RELATIVE_PATH, RESTORE.GENERATOR_RELATIVE_PATH)
        _run_git(self.root, "commit", "--quiet", "-m", "synthetic frozen index")
        self.baseline = _run_git(self.root, "rev-parse", "HEAD")

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def _shard_record(raw: bytes) -> tuple[bytes, dict[str, object]]:
        """构造仅供单元测试使用的合成 shard 及摘要记录。"""
        compressed = zlib.compress(raw, level=9)
        record: dict[str, object] = {
            "compressed_bytes": len(compressed),
            "sha256": hashlib.sha256(compressed).hexdigest(),
            "decompressed_bytes": len(raw),
            "decompressed_sha256": hashlib.sha256(raw).hexdigest(),
        }
        return compressed, record

    def test_compressed_and_decompressed_hashes_must_match(self) -> None:
        raw = b"synthetic T25 tensor stream" * 31
        compressed, record = self._shard_record(raw)
        RESTORE._validate_compressed_payload(compressed, record)

        with self.assertRaises(RESTORE.RestoreError):
            RESTORE._validate_compressed_payload(compressed + b"x", record)

        wrong_raw_record = dict(record)
        wrong_raw_record["decompressed_sha256"] = "0" * 64
        with self.assertRaises(RESTORE.RestoreError):
            RESTORE._validate_compressed_payload(compressed, wrong_raw_record)

    def test_baseline_index_must_be_tracked_and_byte_identical(self) -> None:
        index, raw, digest = RESTORE._read_frozen_index(self.root, self.baseline)
        self.assertEqual(index, self.index_doc)
        self.assertEqual(raw, self.index_bytes)
        self.assertEqual(digest, hashlib.sha256(self.index_bytes).hexdigest())

        self.index_path.write_bytes(b'{"synthetic":"modified"}\n')
        with self.assertRaises(RESTORE.RestoreError):
            RESTORE._read_frozen_index(self.root, self.baseline)

    def test_modified_generator_is_rejected_before_module_execution(self) -> None:
        marker_path = self.generator_path.with_name("generator-executed.marker")
        modified_source = (
            "from pathlib import Path\n"
            "Path(__file__).with_name('generator-executed.marker').write_text('executed', encoding='utf-8')\n"
        ).encode("utf-8")
        self.generator_path.write_bytes(modified_source)
        index, _, _ = RESTORE._read_frozen_index(self.root, self.baseline)

        with self.assertRaises(RESTORE.RestoreError):
            RESTORE._load_generator(self.root, index, self.baseline)

        self.assertFalse(marker_path.exists())

    def test_generator_executes_verified_frozen_blob_bytes(self) -> None:
        index, _, _ = RESTORE._read_frozen_index(self.root, self.baseline)

        generator = RESTORE._load_generator(self.root, index, self.baseline)

        self.assertEqual(generator.GENERATOR_MARKER, "frozen")

    def test_atomic_publish_preserves_index_and_publishes_synthetic_file(self) -> None:
        stage = self.t25 / ".synthetic-stage"
        stage.mkdir()
        shard = b"synthetic shard only"
        (stage / "sample_000.zlib").write_bytes(shard)
        destination = self.t25 / "tensors"

        RESTORE._publish_directory(stage, destination)

        self.assertEqual((destination / "sample_000.zlib").read_bytes(), shard)
        self.assertEqual(self.index_path.read_bytes(), self.index_bytes)
        self.assertFalse(stage.exists())

    def test_existing_destination_is_never_replaced(self) -> None:
        stage = self.t25 / ".synthetic-stage"
        stage.mkdir()
        (stage / "sample_000.zlib").write_bytes(b"new synthetic data")
        destination = self.t25 / "tensors"
        destination.mkdir()
        sentinel = destination / "user-file.txt"
        sentinel.write_bytes(b"preserve me")

        with self.assertRaises(RESTORE.RestoreError):
            RESTORE._publish_directory(stage, destination)

        self.assertEqual(sentinel.read_bytes(), b"preserve me")
        self.assertTrue((stage / "sample_000.zlib").is_file())
        self.assertEqual(self.index_path.read_bytes(), self.index_bytes)

    def test_symlink_destination_is_rejected(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        destination = self.t25 / "tensors"
        try:
            destination.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"当前系统不能创建测试符号链接: {exc}")
        stage = self.t25 / ".synthetic-stage"
        stage.mkdir()

        with self.assertRaises(RESTORE.RestoreError):
            RESTORE._publish_directory(stage, destination)

        self.assertTrue(destination.is_symlink())
        self.assertEqual(list(outside.iterdir()), [])
        self.assertEqual(self.index_path.read_bytes(), self.index_bytes)

    def test_index_shape_requires_all_109_synthetic_records(self) -> None:
        records = []
        for sample_index in range(RESTORE.EXPECTED_SAMPLE_COUNT):
            expected_path = (
                f"{RESTORE.T25_DIRECTORY_RELATIVE_PATH}/tensors/"
                f"sample_{sample_index:03d}.zlib"
            )
            records.append(
                {
                    "sample_index": sample_index,
                    "sample_id": f"synthetic-{sample_index:03d}",
                    "network": {
                        "layer_count": RESTORE.EXPECTED_LAYER_COUNT,
                        "unique_output_raw_bytes": RESTORE.EXPECTED_RAW_BYTES,
                        "raw_stream_sha256": "a" * 64,
                        "compressed_shard": {
                            "path": expected_path,
                            "codec": "zlib",
                            "compression_level": 9,
                            "compressed_bytes": 1,
                            "sha256": "b" * 64,
                            "decompressed_bytes": RESTORE.EXPECTED_RAW_BYTES,
                            "decompressed_sha256": "a" * 64,
                        },
                    },
                }
            )
        index = {
            "schema_version": "gestureforge_s2a_cpu_layer_golden_index_v2",
            "task_id": "S2A-T25",
            "model_id": "tiny416",
            "status": "COMPLETE",
            "stage_acceptance": {"G4": "NOT_MET", "G5": "NOT_MET"},
            "fixed_sample_catalog": {
                "path": "report/evidence/S2A-T01/fixed_test_samples.json",
                "total_samples": RESTORE.EXPECTED_SAMPLE_COUNT,
                "completed_samples": RESTORE.EXPECTED_SAMPLE_COUNT,
                "remaining_samples": 0,
            },
            "network": {
                "layer_count": RESTORE.EXPECTED_LAYER_COUNT,
                "unique_output_raw_bytes_per_sample": RESTORE.EXPECTED_RAW_BYTES,
            },
            "samples": records,
        }

        actual = RESTORE._check_frozen_index_shape(index)
        self.assertEqual(len(actual), RESTORE.EXPECTED_SAMPLE_COUNT)
        index["samples"].pop()
        with self.assertRaises(RESTORE.RestoreError):
            RESTORE._check_frozen_index_shape(index)


if __name__ == "__main__":
    unittest.main()
