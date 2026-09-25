"""S2A-T24：验证 CPU layer golden exporter 的冻结输入和 pilot 规则。"""

from __future__ import annotations

import copy
import contextlib
import hashlib
import io
import unittest
import tempfile
import zlib
from pathlib import Path
from unittest import mock

import numpy as np

from verification import s2a_cpu_layer_goldens as goldens


ROOT = Path(__file__).resolve().parents[1]


class CpuLayerGoldenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.context = goldens.load_context(ROOT)
        cls.context["_synthetic_replay_checks"] = goldens.verify_synthetic_replay(cls.context)

    def _make_zero_pilot(self, sample_index: int) -> dict[str, object]:
        sample = self.context["samples"][sample_index]
        contract_rows = self.context["t22"]["network_dispatch"]["layers"]
        captures = []
        for layer_index, contract_row in enumerate(contract_rows):
            output = contract_row["output_tensor"]
            captures.append(
                {
                    "layer_index": layer_index,
                    "op": contract_row["op"],
                    "shape_nchw": output["shape_nchw"],
                    "scale": output["scale"],
                    "raw_bytes": bytes(output["length_bytes"]),
                }
            )
        raw_stream, compressed, tensor_rows = goldens.serialize_tensor_stream(captures, contract_rows)
        conv_stats = [
            {
                "layer_index": row["layer_index"],
                "int32_overflow_count": 0,
                "raw_accumulator_int32_overflow_count": 0,
                "bias_accumulator_int32_overflow_count": 0,
                "accumulator_with_bias_int32_overflow_count": 0,
            }
            for row in self.context["manifest"]["layers"]
            if row["op"] == "convolutional"
        ]
        return {
            "sample_index": sample_index,
            "sample": sample,
            "image_path": None,
            "label_path": None,
            "image_sha256": sample.get("image_sha256", sample.get("rgb_sha256")),
            "label_sha256": sample.get("label_sha256"),
            "rgb_shape_hwc": [sample["height"], sample["width"], 3],
            "input_raw_bytes": 519168,
            "input_sha256": sample["pl_input_sha256"],
            "synthetic_checks": [],
            "raw_stream": raw_stream,
            "compressed_stream": compressed,
            "tensor_rows": tensor_rows,
            "convolution_stats": conv_stats,
            "elapsed_seconds": 0.001,
        }

    def _create_t25_test_checkpoint(self, output_dir: Path, completed: int = 1) -> dict[str, object]:
        output_dir.mkdir()
        tensor_dir = output_dir / "tensors"
        tensor_dir.mkdir()
        goldens._append_t25_log(output_dir / goldens.T25_LOG_NAME, {"event": "test"}, create=True)
        records = []
        index = goldens.build_t25_index(self.context, records)
        goldens.atomic_write_checkpoint(output_dir / goldens.T25_INDEX_NAME, index)
        for sample_index in range(completed):
            pilot = self._make_zero_pilot(sample_index)
            index = goldens._append_t25_checkpoint_sample(self.context, output_dir, records, pilot)
            records = index["samples"]
        return index

    def test_source_pin_mutation_and_omission_fail_closed(self) -> None:
        mutated = copy.deepcopy(self.context["source_bindings"])
        mutated[0]["sha256"] = "0" * 64
        with self.assertRaises(goldens.GoldenExportError):
            goldens.validate_source_bindings(mutated, self.context["source_bindings"])
        omitted = copy.deepcopy(self.context["source_bindings"][:-1])
        with self.assertRaises(goldens.GoldenExportError):
            goldens.validate_source_bindings(omitted, self.context["source_bindings"])

    def test_fixed_catalog_order_and_hash_format_are_checked(self) -> None:
        document = copy.deepcopy(self.context["samples_doc"])
        samples = goldens.validate_sample_catalog(document, goldens.PINNED_SHA256[goldens.MANIFEST_PATH])
        self.assertEqual(len(samples), 109)
        document["samples"][0]["frame_id"] = 1
        with self.assertRaises(goldens.GoldenExportError):
            goldens.validate_sample_catalog(document, goldens.PINNED_SHA256[goldens.MANIFEST_PATH])
        document = copy.deepcopy(self.context["samples_doc"])
        document["samples"][0]["pl_input_sha256"] = "not-a-digest"
        with self.assertRaises(goldens.GoldenExportError):
            goldens.validate_sample_catalog(document, goldens.PINNED_SHA256[goldens.MANIFEST_PATH])

    def test_original_image_and_preprocessed_input_hash_mismatch_are_rejected(self) -> None:
        image_payload = b"frozen-image-bytes"
        image_digest = hashlib.sha256(image_payload).hexdigest()
        self.assertEqual(goldens.verify_digest(image_payload, image_digest, "image"), image_digest)
        with self.assertRaises(goldens.GoldenExportError):
            goldens.verify_digest(image_payload, "0" * 64, "image")

        tensor = np.asarray([[[-127]], [[0]], [[127]]], dtype=np.int8)
        raw = tensor.tobytes(order="C")
        expected = hashlib.sha256(raw).hexdigest()
        verified, digest = goldens.validate_preprocessed_input(tensor, [1, 3, 1, 1], expected)
        self.assertEqual(verified, raw)
        self.assertEqual(digest, expected)
        with self.assertRaises(goldens.GoldenExportError):
            goldens.validate_preprocessed_input(tensor, [1, 3, 1, 1], "0" * 64)

    def test_synthetic_cases_replay_rgb_and_d2_pl_input_hashes(self) -> None:
        checks = goldens.verify_synthetic_replay(self.context)
        self.assertEqual(len(checks), 4)
        fixed = {
            row["sample_id"]: row
            for row in self.context["samples"]
            if row["source"] == "synthetic_rgb416"
        }
        for check in checks:
            self.assertEqual(check["rgb_sha256"], fixed[check["sample_id"]]["rgb_sha256"])
            self.assertEqual(check["pl_input_sha256"], fixed[check["sample_id"]]["pl_input_sha256"])

    def test_tensor_shape_scale_length_and_hash_are_checked(self) -> None:
        values = np.asarray([[[-1, 0]], [[1, 127]]], dtype=np.int8)
        descriptor = {"shape_nchw": [1, 2, 1, 2], "scale": 0.25, "length_bytes": 4}
        raw, metadata = goldens.validate_tensor_payload(
            0, "convolutional", values, 0.25, descriptor, hashlib.sha256(values.tobytes()).hexdigest()
        )
        self.assertEqual(len(raw), 4)
        self.assertEqual(metadata["shape_nchw"], descriptor["shape_nchw"])
        with self.assertRaises(goldens.GoldenExportError):
            goldens.validate_tensor_payload(0, "convolutional", values, 0.5, descriptor)
        bad_shape = copy.deepcopy(descriptor)
        bad_shape["shape_nchw"] = [1, 2, 2, 1]
        with self.assertRaises(goldens.GoldenExportError):
            goldens.validate_tensor_payload(0, "convolutional", values, 0.25, bad_shape)
        bad_length = copy.deepcopy(descriptor)
        bad_length["length_bytes"] = 5
        with self.assertRaises(goldens.GoldenExportError):
            goldens.validate_tensor_payload(0, "convolutional", values, 0.25, bad_length)
        with self.assertRaises(goldens.GoldenExportError):
            goldens.validate_tensor_payload(0, "convolutional", values, 0.25, descriptor, "0" * 64)

    def test_t22_yolo_aliases_reference_source_and_do_not_duplicate_storage(self) -> None:
        rows = self.context["t22"]["network_dispatch"]["layers"]
        goldens.validate_yolo_alias(rows[30], rows[29])
        goldens.validate_yolo_alias(rows[37], rows[36])
        mutated = copy.deepcopy(rows[30])
        mutated["output_tensor"]["address"] += 1
        with self.assertRaises(goldens.GoldenExportError):
            goldens.validate_yolo_alias(mutated, rows[29])

    def test_any_nonzero_int32_overflow_rejects_convolution_sample(self) -> None:
        goldens.validate_no_conv_overflow(
            {
                "int32_overflow_count": 0,
                "raw_accumulator_int32_overflow_count": 0,
                "bias_accumulator_int32_overflow_count": 0,
                "accumulator_with_bias_int32_overflow_count": 0,
            }
        )
        for field in (
            "int32_overflow_count",
            "raw_accumulator_int32_overflow_count",
            "bias_accumulator_int32_overflow_count",
            "accumulator_with_bias_int32_overflow_count",
        ):
            stats = {"int32_overflow_count": 0, field: 1}
            with self.subTest(field=field), self.assertRaises(goldens.GoldenExportError):
                goldens.validate_no_conv_overflow(stats)

    def test_zlib_stream_roundtrip_offsets_and_alias_range(self) -> None:
        raw = b"tensor"
        digest = hashlib.sha256(raw).hexdigest()
        rows = [
            {
                "layer_index": 0,
                "byte_offset": 0,
                "byte_length": len(raw),
                "tensor_sha256": digest,
                "stored": True,
                "alias_of_layer_index": None,
            },
            {
                "layer_index": 1,
                "byte_offset": 0,
                "byte_length": len(raw),
                "tensor_sha256": digest,
                "stored": False,
                "alias_of_layer_index": 0,
            },
        ]
        packed = zlib.compress(raw, level=9)
        unpacked = zlib.decompress(packed)
        self.assertEqual(unpacked, raw)
        goldens.validate_tensor_stream(unpacked, rows)
        bad = copy.deepcopy(rows)
        bad[1]["byte_offset"] = 1
        with self.assertRaises(goldens.GoldenExportError):
            goldens.validate_tensor_stream(unpacked, bad)

    def test_pilot_index_cannot_claim_full_sample_or_stage_completion(self) -> None:
        index = {
            "schema_version": "gestureforge_s2a_cpu_layer_golden_index_v1",
            "status": "PILOT_ONLY",
            "stage_acceptance": {"G4": "NOT_MET", "G5": "NOT_MET"},
            "pilot_sample": {
                "sample_index": 0,
                "sample_id": "test_fist_000",
            },
            "network": {"layer_count": 38},
            "fixed_sample_catalog": {
                "total_samples": 109,
                "completed_samples": 1,
                "remaining_samples": 108,
            },
        }
        goldens.validate_pilot_index(index)
        mutated = copy.deepcopy(index)
        mutated["fixed_sample_catalog"]["completed_samples"] = 109
        with self.assertRaises(goldens.GoldenExportError):
            goldens.validate_pilot_index(mutated)
        mutated = copy.deepcopy(index)
        mutated["stage_acceptance"]["G5"] = "PASS"
        with self.assertRaises(goldens.GoldenExportError):
            goldens.validate_pilot_index(mutated)

    def test_t25_checkpoint_resume_skips_completed_and_completes_only_at_109(self) -> None:
        with tempfile.TemporaryDirectory(prefix="s2a_t25_resume_") as temporary:
            output_dir = Path(temporary) / "output"
            initial = self._create_t25_test_checkpoint(output_dir, completed=1)
            self.assertEqual(initial["status"], "IN_PROGRESS")
            loaded, records = goldens._load_t25_checkpoint(self.context, output_dir)
            self.assertEqual(loaded["fixed_sample_catalog"]["completed_samples"], 1)
            self.assertEqual([row["sample_index"] for row in records], [0])

            called = []

            def fake_runner(context, sample_index, max_seconds, synthetic_checks=None):
                called.append(sample_index)
                return self._make_zero_pilot(sample_index)

            with mock.patch.object(
                goldens,
                "_append_t25_checkpoint_sample",
                wraps=goldens._append_t25_checkpoint_sample,
            ) as checkpoint_writer:
                with contextlib.redirect_stdout(io.StringIO()):
                    result = goldens._execute_t25(
                        self.context,
                        output_dir,
                        resume=True,
                        max_sample_seconds=600.0,
                        max_total_seconds=7200.0,
                        sample_runner=fake_runner,
                    )
            self.assertEqual(called, list(range(1, goldens.EXPECTED_SAMPLE_COUNT)))
            self.assertEqual(checkpoint_writer.call_count, goldens.EXPECTED_SAMPLE_COUNT - 1)
            self.assertEqual(result["status"], "COMPLETE")
            self.assertEqual(result["fixed_sample_catalog"]["completed_samples"], 109)
            goldens.validate_t25_index_status(result)
            validated, complete_records = goldens._load_t25_checkpoint(self.context, output_dir)
            self.assertEqual(validated["status"], "COMPLETE")
            self.assertEqual(len(complete_records), 109)

    def test_t25_rejects_corrupt_or_unindexed_shard_and_preserves_existing_bytes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="s2a_t25_corrupt_") as temporary:
            output_dir = Path(temporary) / "corrupt"
            self._create_t25_test_checkpoint(output_dir, completed=1)
            shard = output_dir / "tensors" / "sample_000.zlib"
            original = shard.read_bytes()
            with self.assertRaises(goldens.GoldenExportError):
                goldens.atomic_create_shard(shard, b"replacement")
            self.assertEqual(shard.read_bytes(), original)
            goldens._load_t25_checkpoint(self.context, output_dir)
            shard.write_bytes(b"corrupt")
            with self.assertRaises(goldens.GoldenExportError):
                goldens._load_t25_checkpoint(self.context, output_dir)

        with tempfile.TemporaryDirectory(prefix="s2a_t25_conflict_") as temporary:
            output_dir = Path(temporary) / "conflict"
            self._create_t25_test_checkpoint(output_dir, completed=1)
            (output_dir / "tensors" / "sample_001.zlib").write_bytes(b"orphan")
            with self.assertRaises(goldens.GoldenExportError):
                goldens._load_t25_checkpoint(self.context, output_dir)

    def test_t25_status_gate_and_source_binding_mutations_fail_closed(self) -> None:
        incomplete = goldens.build_t25_index(self.context, [{"sample_index": i} for i in range(108)])
        self.assertEqual(incomplete["status"], "IN_PROGRESS")
        goldens.validate_t25_index_status(incomplete)
        complete = goldens.build_t25_index(self.context, [{"sample_index": i} for i in range(109)])
        self.assertEqual(complete["status"], "COMPLETE")
        goldens.validate_t25_index_status(complete)
        invalid = copy.deepcopy(incomplete)
        invalid["status"] = "COMPLETE"
        with self.assertRaises(goldens.GoldenExportError):
            goldens.validate_t25_index_status(invalid)

        with tempfile.TemporaryDirectory(prefix="s2a_t25_binding_") as temporary:
            output_dir = Path(temporary) / "output"
            self._create_t25_test_checkpoint(output_dir, completed=1)
            index_path = output_dir / goldens.T25_INDEX_NAME
            index = goldens.json.loads(index_path.read_text(encoding="utf-8"))
            index["tooling_bindings"][0]["sha256"] = "0" * 64
            goldens.atomic_write_checkpoint(index_path, index)
            with self.assertRaises(goldens.GoldenExportError):
                goldens._load_t25_checkpoint(self.context, output_dir)


if __name__ == "__main__":
    unittest.main(verbosity=2)
