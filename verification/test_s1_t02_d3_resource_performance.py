import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import s1_t02_d3_resource_performance as checker
except ModuleNotFoundError:
    from verification import s1_t02_d3_resource_performance as checker


ROOT = Path(__file__).resolve().parents[1]
CFG_PATHS = {
    "tiny320": Path(r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\s1_t02_float_setup_r1\configs\gesture_yolov4_tiny_320_float_setup.cfg"),
    "tiny416": Path(r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\s1_t02_float_setup_r1\configs\gesture_yolov4_tiny_416_float_setup.cfg"),
    "full": Path(r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\s1_t02_float_setup_r1\configs\yolov4_5class_float_pc_setup.cfg"),
}
D2_REFERENCE = ROOT / "verification" / "s1_t02_d2_numeric_reference.py"


def _metrics():
    return {"lut_pct": 10.0, "ff_pct": 20.0, "bram_pct": 30.0, "dsp_pct": 40.0}


def _timing():
    return {"wns_ns": 1.0, "whs_ns": 2.0, "tns_ns": 0.0, "ths_ns": 0.0}


def _resource_evidence(applicable=True):
    def entry(kind):
        return {"evidence_kind": kind, "status": "MEASURED", "utilization": _metrics(), "timing": _timing()}

    return {
        "estimate": entry("estimate"),
        "synthesis": entry("synthesis") if applicable else {"evidence_kind": "synthesis", "status": "NOT_APPLICABLE", "reason": "完整模型仅作 PC 对照"},
        "board_measurement": entry("board_measurement") if applicable else {"evidence_kind": "board_measurement", "status": "NOT_APPLICABLE", "reason": "完整模型不进入上板资源验收"},
    }


def _storage():
    return {
        "status": "MEASURED",
        "weights_bytes": 100,
        "feature_map_peak_bytes": 200,
        "frame_buffer_bytes": 300,
        "ps_buffer_bytes": 400,
        "ddr_peak_bytes": 1000,
        "address_ranges": [
            {"name": "weights", "start": 0, "end": 100},
            {"name": "feature_map", "start": 100, "end": 300},
            {"name": "frame_buffer", "start": 300, "end": 600},
            {"name": "ps_buffer", "start": 600, "end": 1000},
        ],
    }


def _bandwidth():
    return {
        "status": "MEASURED",
        "unit": "bytes_per_second",
        "video_input_bytes_per_s": 1.0,
        "model_transfer_bytes_per_s": 2.0,
        "ps_decode_nms_bytes_per_s": 3.0,
        "cache_competition_bytes_per_s": 4.0,
        "total_peak_bytes_per_s": 10.0,
    }


def _performance(model_key, status="MEASURED", effective=10000):
    return {
        "status": status,
        "fixed_config": {
            "model_id": checker.MODEL_IDS[model_key],
            "input_size": checker.MODEL_INPUT_SIZES[model_key],
            "weight_sha256": "a" * 64,
            "cfg_sha256": checker.sha256_file(CFG_PATHS[model_key]),
            "preprocess_sha256": checker.sha256_file(D2_REFERENCE),
            "score_threshold": 0.25,
            "nms_iou": 0.45,
            "max_detections": 15,
        },
        "warmup": 100,
        "effective_inferences": effective,
        "sample_selection": "all_valid_samples_no_fast_sample_filter",
        "stages": {
            stage: {"status": status, "mean_ms": 1.0, "p50_ms": 1.0, "p95_ms": 2.0, "p99_ms": 3.0}
            for stage in checker.PERFORMANCE_STAGES
        },
        "failure_counts": {"timeout": 0, "drop": 0, "failure": 0},
    }


def _base_document():
    root = Path(__file__).resolve().parents[1]
    models = {}
    for key in checker.MODEL_KEYS:
        applicable = key != "full"
        models[key] = {
            "role": checker.MODEL_ROLES[key],
            "applicability": {"board_resource_gate": applicable, "pc_budget": True},
            "resource": {"evidence": _resource_evidence(applicable), "storage": _storage(), "ddr_bandwidth": _bandwidth()},
            "performance": _performance(key),
        }
    return {
        "schema_version": "s1_t02_d3_resource_performance_v1",
        "task": "S1-T02-D3",
        "hardware_baseline": {"board": "AX7Z020", "device": "XA7Z020", "package": "CLG400", "speed_grade": "-1"},
        "thresholds": {"max_utilization_percent": 85, "wns_min_ns": 0, "whs_min_ns": 0, "tns_max_ns": 0, "ths_max_ns": 0},
        "final_threshold_status": "pending_until_wong_decision",
        "file_bindings": {
            "test_file": str(Path(__file__).resolve()),
            "tiny320_cfg": str(CFG_PATHS["tiny320"]),
            "tiny416_cfg": str(CFG_PATHS["tiny416"]),
            "full_cfg": str(CFG_PATHS["full"]),
            "d2_numeric_reference": str(D2_REFERENCE),
        },
        "provenance_requests": {"competition_repository": str(root)},
        "models": models,
    }


class ResourcePerformanceCheckerTests(unittest.TestCase):
    def test_legal_document_is_structurally_valid_but_threshold_pending(self):
        result = checker.validate_document(_base_document())
        self.assertTrue(result["validation"]["schema_valid"])
        self.assertEqual(result["validation"]["status"], "READY_FOR_WONG_DECISION")
        self.assertEqual(result["validation"]["errors"], [])

    def test_resource_over_limit_is_rejected(self):
        document = _base_document()
        document["models"]["tiny320"]["resource"]["evidence"]["estimate"]["utilization"]["lut_pct"] = 85.1
        result = checker.validate_document(document)
        self.assertFalse(result["validation"]["schema_valid"])
        self.assertTrue(any("lut_pct" in item and "85" in item for item in result["validation"]["errors"]))

    def test_address_overlap_is_rejected(self):
        document = _base_document()
        document["models"]["tiny416"]["resource"]["storage"]["address_ranges"][1]["start"] = 99
        result = checker.validate_document(document)
        self.assertFalse(result["validation"]["schema_valid"])
        self.assertTrue(any("重叠" in item for item in result["validation"]["errors"]))

    def test_measured_performance_requires_ten_thousand_samples(self):
        document = _base_document()
        document["models"]["tiny320"]["performance"]["effective_inferences"] = 9999
        result = checker.validate_document(document)
        self.assertFalse(result["validation"]["schema_valid"])
        self.assertTrue(any("10000" in item for item in result["validation"]["errors"]))

    def test_estimate_only_is_pending_not_pass(self):
        document = _base_document()
        resource = document["models"]["tiny320"]["resource"]
        resource["evidence"]["estimate"]["status"] = "PENDING"
        resource["evidence"]["synthesis"]["status"] = "NOT_EXECUTED"
        resource["evidence"]["board_measurement"]["status"] = "NOT_EXECUTED"
        resource["storage"] = {"status": "PENDING", **{field: None for field in checker.STORAGE_FIELDS}, "address_ranges": []}
        resource["ddr_bandwidth"] = {"status": "PENDING", **{field: None for field in checker.BANDWIDTH_FIELDS}}
        result = checker.validate_document(document)
        self.assertTrue(result["validation"]["schema_valid"])
        self.assertEqual(result["validation"]["status"], "NOT_EXECUTED_PENDING")
        self.assertNotEqual(result["validation"]["status"], "PASS")

    def test_full_board_resource_is_not_applicable(self):
        result = checker.validate_document(_base_document())
        self.assertTrue(result["validation"]["schema_valid"])
        self.assertEqual(result["validation"]["models"]["full"]["resource_status"], "NOT_APPLICABLE_PC_ONLY")

    def test_old_threshold_status_is_rejected(self):
        document = _base_document()
        document["final_threshold_status"] = "20_fps"
        result = checker.validate_document(document)
        self.assertFalse(result["validation"]["schema_valid"])
        self.assertTrue(any("pending_until_wong_decision" in item for item in result["validation"]["errors"]))

    def test_measured_storage_missing_field_is_rejected(self):
        document = _base_document()
        storage = document["models"]["tiny320"]["resource"]["storage"]
        del storage["weights_bytes"]
        result = checker.validate_document(document)
        self.assertFalse(result["validation"]["schema_valid"])
        self.assertTrue(any("storage.weights_bytes" in item and "缺少字段" in item for item in result["validation"]["errors"]))

    def test_measured_bandwidth_missing_field_is_rejected(self):
        document = _base_document()
        bandwidth = document["models"]["tiny320"]["resource"]["ddr_bandwidth"]
        del bandwidth["total_peak_bytes_per_s"]
        result = checker.validate_document(document)
        self.assertFalse(result["validation"]["schema_valid"])
        self.assertTrue(any("ddr_bandwidth.total_peak_bytes_per_s" in item and "缺少字段" in item for item in result["validation"]["errors"]))

    def test_measured_stage_missing_field_is_rejected(self):
        document = _base_document()
        stage = document["models"]["tiny320"]["performance"]["stages"]["preprocess"]
        del stage["mean_ms"]
        result = checker.validate_document(document)
        self.assertFalse(result["validation"]["schema_valid"])
        self.assertTrue(any("stages.preprocess.mean_ms" in item and "MEASURED" in item for item in result["validation"]["errors"]))

    def test_illegal_storage_bandwidth_and_stage_status_are_rejected(self):
        for target in ("storage", "ddr_bandwidth"):
            with self.subTest(target=target):
                document = _base_document()
                document["models"]["tiny320"]["resource"][target]["status"] = "BROKEN"
                result = checker.validate_document(document)
                self.assertFalse(result["validation"]["schema_valid"])
                self.assertTrue(any(target + ".status" in item and "非法状态" in item for item in result["validation"]["errors"]))
        document = _base_document()
        document["models"]["tiny320"]["performance"]["stages"]["preprocess"]["status"] = "BROKEN"
        result = checker.validate_document(document)
        self.assertFalse(result["validation"]["schema_valid"])
        self.assertTrue(any("stages.preprocess.status" in item and "非法状态" in item for item in result["validation"]["errors"]))

    def test_model_size_id_and_hash_binding_are_rejected(self):
        cases = (
            ("input_size", [416, 416], "input_size"),
            ("model_id", "wrong_model", "model_id"),
            ("cfg_sha256", "b" * 63, "cfg_sha256"),
            ("preprocess_sha256", "c" * 63, "preprocess_sha256"),
        )
        for field, value, marker in cases:
            with self.subTest(field=field):
                document = _base_document()
                document["models"]["tiny320"]["performance"]["fixed_config"][field] = value
                result = checker.validate_document(document)
                self.assertFalse(result["validation"]["schema_valid"])
                self.assertTrue(any(marker in item for item in result["validation"]["errors"]))

    def test_preprocess_hash_matches_bound_d2_reference_for_every_model(self):
        document = _base_document()
        expected = checker.sha256_file(D2_REFERENCE)
        for key in checker.MODEL_KEYS:
            with self.subTest(model=key):
                self.assertEqual(document["models"][key]["performance"]["fixed_config"]["preprocess_sha256"], expected)
        result = checker.validate_document(document)
        self.assertTrue(result["validation"]["schema_valid"])

    def test_preprocess_hash_mismatch_with_bound_d2_reference_is_rejected(self):
        document = _base_document()
        document["models"]["full"]["performance"]["fixed_config"]["preprocess_sha256"] = "0" * 64
        result = checker.validate_document(document)
        self.assertFalse(result["validation"]["schema_valid"])
        self.assertTrue(any("full.performance.fixed_config.preprocess_sha256" in item and "d2_numeric_reference" in item for item in result["validation"]["errors"]))

    def test_measured_fixed_config_rejects_missing_required_bindings(self):
        for field in ("weight_sha256", "score_threshold", "nms_iou"):
            with self.subTest(field=field):
                document = _base_document()
                document["models"]["tiny320"]["performance"]["fixed_config"][field] = None
                result = checker.validate_document(document)
                self.assertFalse(result["validation"]["schema_valid"])
                self.assertTrue(any("tiny320.performance.fixed_config." + field in item and "MEASURED" in item for item in result["validation"]["errors"]))

    def test_non_measured_missing_weight_remains_pending(self):
        document = _base_document()
        document["models"]["tiny320"]["performance"] = _performance("tiny320", status="NOT_EXECUTED")
        document["models"]["tiny320"]["performance"]["fixed_config"]["weight_sha256"] = None
        result = checker.validate_document(document)
        self.assertTrue(result["validation"]["schema_valid"])
        self.assertEqual(result["validation"]["status"], "NOT_EXECUTED_PENDING")

    def test_cli_rejects_same_input_and_report_after_resolution(self):
        with self.subTest("same_path"):
            path = ROOT / "report" / "evidence" / "S1-T02" / "d3_same_path_fixture.json"
            with patch.object(checker.sys, "argv", ["checker", "--input", str(path), "--report", str(path), "--summary", str(path.with_suffix(".md"))]):
                self.assertEqual(checker.main(), 2)


if __name__ == "__main__":
    unittest.main()
