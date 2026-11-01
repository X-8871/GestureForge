"""S2A-T29 冻结 head 输入、压缩 shard 与 D9 调用夹具。"""

from __future__ import annotations

import hashlib
import tempfile
import unittest
import zlib
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from verification import s2a_decode_nms_reference as reference


class DecodeNmsReferenceTests(unittest.TestCase):
    def test_zlib_shard_hash_size_and_raw_stream_are_bound(self) -> None:
        raw = bytes(range(64))
        compressed = zlib.compress(raw, level=9)
        digest = hashlib.sha256(raw).hexdigest()
        shard = {
            "codec": "zlib",
            "compressed_bytes": len(compressed),
            "sha256": hashlib.sha256(compressed).hexdigest(),
            "decompressed_bytes": len(raw),
            "decompressed_sha256": digest,
        }
        network = {"unique_output_raw_bytes": len(raw), "raw_stream_sha256": digest}
        self.assertEqual(reference.verify_zlib_shard(compressed, shard, network), raw)

        bad_compressed_hash = dict(shard, sha256="0" * 64)
        with self.assertRaises(reference.ReferenceError):
            reference.verify_zlib_shard(compressed, bad_compressed_hash, network)
        bad_length = dict(shard, decompressed_bytes=len(raw) - 1)
        with self.assertRaises(reference.ReferenceError):
            reference.verify_zlib_shard(compressed, bad_length, network)

    def test_zlib_shard_rejects_trailing_bytes_and_expansion_beyond_declared_size(self) -> None:
        raw = b"frozen bytes"
        compressed = zlib.compress(raw, level=9)
        digest = hashlib.sha256(raw).hexdigest()
        shard = {
            "codec": "zlib",
            "compressed_bytes": len(compressed) + 5,
            "sha256": hashlib.sha256(compressed + b"extra").hexdigest(),
            "decompressed_bytes": len(raw),
            "decompressed_sha256": digest,
        }
        network = {"unique_output_raw_bytes": len(raw), "raw_stream_sha256": digest}
        with self.assertRaises(reference.ReferenceError):
            reference.verify_zlib_shard(compressed + b"extra", shard, network)

        smaller_shard = dict(shard, compressed_bytes=len(compressed), sha256=hashlib.sha256(compressed).hexdigest(), decompressed_bytes=len(raw) - 1)
        smaller_network = {"unique_output_raw_bytes": len(raw) - 1, "raw_stream_sha256": digest}
        with self.assertRaises(reference.ReferenceError):
            reference.verify_zlib_shard(compressed, smaller_shard, smaller_network)

    def test_shard_directory_requires_exact_expected_name_set(self) -> None:
        expected = {f"sample_{index:03d}.zlib" for index in range(3)}
        reference.validate_exact_shard_names(expected, set(expected))
        with self.assertRaises(reference.ReferenceError):
            reference.validate_exact_shard_names(expected, {"sample_000.zlib", "sample_001.zlib"})
        with self.assertRaises(reference.ReferenceError):
            reference.validate_exact_shard_names(expected, set(expected) | {"orphan.zlib"})

    def test_sample_pair_rejects_order_source_and_label_drift(self) -> None:
        fixed = {
            "frame_id": 7,
            "sample_id": "test_one_007",
            "source": "official_hagrid_test",
            "coverage_tags": ["class:one"],
            "ground_truth_yolo": [[2, 0.5, 0.5, 0.2, 0.2]],
        }
        indexed = dict(fixed, sample_index=7)
        reference._validate_sample_pair(fixed, indexed, 7)
        for field, value in (("frame_id", 8), ("source", "unknown"), ("ground_truth_yolo", [])):
            changed = dict(indexed, **{field: value})
            with self.subTest(field=field), self.assertRaises(reference.ReferenceError):
                reference._validate_sample_pair(fixed, changed, 7)

    def test_synthetic_catalog_without_gt_field_means_empty_gt(self) -> None:
        sample = {"sample_id": "synthetic_black", "source": "synthetic_rgb416"}
        self.assertEqual(reference._sample_ground_truth(sample), [])
        malformed = dict(sample, ground_truth_yolo="not-a-list")
        with self.assertRaises(reference.ReferenceError):
            reference._sample_ground_truth(malformed)

    def test_frozen_d9_is_called_with_all_zero_head_candidates_and_stable_replay(self) -> None:
        heads = {
            "13x13": np.zeros((3, 10, 13, 13), dtype=np.float64),
            "26x26": np.zeros((3, 10, 26, 26), dtype=np.float64),
        }
        first, first_raw_count = reference.decode_and_count_candidates(heads, "synthetic_fixture", 416, 416, 0.25)
        second, second_raw_count = reference.decode_and_count_candidates(heads, "synthetic_fixture", 416, 416, 0.25)
        expected_raw_count = (13 * 13 + 26 * 26) * 3 * 5
        self.assertEqual(first_raw_count, expected_raw_count)
        self.assertEqual(second_raw_count, expected_raw_count)
        self.assertEqual([reference._prediction_json(item) for item in first], [reference._prediction_json(item) for item in second])
        self.assertLessEqual(len(first), 15)
        reference._validate_predictions(first, "synthetic_fixture", first_raw_count, 15)

    def test_prediction_validator_rejects_unknown_class_bad_box_or_wrong_order(self) -> None:
        good = SimpleNamespace(image_key="sample", class_id=0, name="fist", confidence=0.5, box=(0.1, 0.2, 0.6, 0.8), source_order=10)
        reference._validate_predictions([good], "sample", 2, 15)
        bad_class = SimpleNamespace(**{**good.__dict__, "class_id": 5})
        bad_box = SimpleNamespace(**{**good.__dict__, "box": (0.9, 0.1, 0.2, 0.8)})
        lower_then_higher = [
            good,
            SimpleNamespace(**{**good.__dict__, "confidence": 0.7, "source_order": 11}),
        ]
        for predictions in ([bad_class], [bad_box], lower_then_higher):
            with self.subTest(predictions=predictions), self.assertRaises(reference.ReferenceError):
                reference._validate_predictions(list(predictions), "sample", 2, 15)

    def test_repo_path_rejects_parent_escape(self) -> None:
        with tempfile.TemporaryDirectory(prefix="s2a_t29_path_test_") as directory:
            root = Path(directory)
            with self.assertRaises(reference.ReferenceError):
                reference._repo_path(root, "../outside.json")

    def test_runtime_head_accepts_baseline_and_t29_descendant_but_rejects_unrelated(self) -> None:
        later_task_head = "a" * 40
        unrelated_head = "b" * 40
        checks: list[tuple[str, str]] = []

        def is_ancestor(ancestor: str, descendant: str) -> bool:
            checks.append((ancestor, descendant))
            return ancestor == reference.BASELINE_HEAD and descendant == later_task_head

        self.assertEqual(reference.classify_runtime_head(reference.BASELINE_HEAD, reference.BASELINE_HEAD, is_ancestor), "baseline")
        self.assertEqual(checks, [])
        self.assertEqual(reference.classify_runtime_head(reference.BASELINE_HEAD, later_task_head, is_ancestor), "descendant")
        self.assertEqual(checks, [(reference.BASELINE_HEAD, later_task_head)])
        with self.assertRaises(reference.ReferenceError):
            reference.classify_runtime_head(reference.BASELINE_HEAD, unrelated_head, is_ancestor)

    def test_canonical_evidence_digest_ignores_runtime_head_observation_only(self) -> None:
        baseline_run = {
            "baseline_git_head": reference.BASELINE_HEAD,
            "runtime_git_head": {
                "observed": reference.BASELINE_HEAD,
                "relation_to_baseline": "baseline",
                "checked_stable_during_run": True,
            },
            "payload": {"samples": 109},
        }
        descendant_run = {
            "baseline_git_head": reference.BASELINE_HEAD,
            "runtime_git_head": {
                "observed": "a" * 40,
                "relation_to_baseline": "descendant",
                "checked_stable_during_run": True,
            },
            "payload": {"samples": 109},
        }
        self.assertEqual(reference._canonical_evidence_bytes(baseline_run), reference._canonical_evidence_bytes(descendant_run))

    def test_frozen_d9_fixture_metadata_does_not_observe_worktree_file(self) -> None:
        metadata = reference._frozen_fixture_metadata(
            {
                "path": "verification/test_s1_t02_d9_yolo_decode.py",
                "sha256": "7c5aebac28f316c16e4fbef80905c73b21036cfeab80115c926f143605277f5a",
                "source_commit": "0ce55634c4e07000b0f8c1640b3b6ba4ab072386",
            }
        )
        self.assertFalse(metadata["used_by_t29"])
        self.assertEqual(metadata["frozen_source_commit"], "0ce55634c4e07000b0f8c1640b3b6ba4ab072386")
        self.assertNotIn("observed_worktree_sha256", metadata)
        self.assertNotIn("worktree_matches_frozen", metadata)


if __name__ == "__main__":
    unittest.main()
