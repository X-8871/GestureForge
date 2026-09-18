"""S1-T02-D4 绑定检查器的单元测试。"""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from . import s1_t02_d4_float_baseline as d4
    from .s1_t02_d4_float_baseline import main, make_report, sha256_file, validate_plan
except ImportError:
    import s1_t02_d4_float_baseline as d4
    from s1_t02_d4_float_baseline import main, make_report, sha256_file, validate_plan


class D4Fixture(unittest.TestCase):
    """为每项测试准备隔离的三模型计划。"""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="s1_t02_d4_")
        self.root = Path(self.temp.name)
        self.run_dir = self.root / "run"
        self.run_dir.mkdir()
        (self.run_dir / "configs").mkdir()
        (self.run_dir / "data").mkdir()
        (self.run_dir / "checkpoints").mkdir()
        (self.run_dir / "build").mkdir()
        self.patched_source = self.run_dir / "official_seeded"
        (self.patched_source / "src").mkdir(parents=True)
        self.modified_source_file = self.patched_source / "src" / "utils.c"
        self.modified_source_file.write_text("隔离修改源\n", encoding="utf-8")
        self.source = self.root / "official_source"
        self.source.mkdir()
        self.exe = self.run_dir / "build" / "darknet.exe"
        self.exe.write_bytes(b"d4 executable")
        self.configure_log = self.run_dir / "configure.log"
        self.configure_log.write_text("configure exit 0\n", encoding="utf-8")
        self.build_log = self.run_dir / "build.log"
        self.build_log.write_text("build exit 0\n", encoding="utf-8")
        self.patch = self.root / "seed_support.patch"
        self.patch.write_text("隔离 seed patch\n", encoding="utf-8")
        self.source_archive = self.run_dir / "official_source.zip"
        self.source_archive.write_bytes(b"official source archive")
        self.names = self.root / "gesture.names"
        self.names.write_text("fist\npalm\none\ntwo_up\nthree\n", encoding="utf-8")
        self.train = self.root / "train.list"
        self.train.write_text("train.png\n" * 118001, encoding="utf-8")
        self.valid = self.root / "valid.list"
        self.valid.write_text("valid.png\n" * 15195, encoding="utf-8")
        self.manifest = self.root / "manifest.csv"
        self.manifest.write_text("manifest\n", encoding="utf-8")
        self.reference = self.root / "numeric_reference.py"
        self.reference.write_text("# 参考\n", encoding="utf-8")
        self.smoke = []
        for name, seed in (("a", 424242), ("b", 424242), ("c", 424243)):
            log = self.run_dir / f"seed_smoke_{name}.log"
            checkpoint = self.run_dir / "checkpoints" / f"seed_smoke_{name}.weights"
            log.write_text(f"seed={seed}\n", encoding="utf-8")
            checkpoint.write_bytes(f"checkpoint={name}\n".encode("ascii"))
            self.smoke.append(
                {
                    "name": f"seed_{name}",
                    "seed": seed,
                    "command_exit_code": 0,
                    "log": str(log),
                    "log_sha256": sha256_file(log),
                    "checkpoint": str(checkpoint),
                    "checkpoint_sha256": sha256_file(checkpoint),
                }
            )
        self.pilot_cfg = self.run_dir / "configs" / "pilot.cfg"
        self.pilot_cfg.write_text(self._cfg_text(416, 2), encoding="utf-8")
        self.pilot_data = self.run_dir / "data" / "pilot.data"
        self.pilot_data.write_text("classes=5\n", encoding="utf-8")
        self.pilot_log = self.run_dir / "pilot.log"
        self.pilot_log.write_text("pilot not executed\n", encoding="utf-8")
        self.weight = self.root / "yolov4-tiny.conv.29"
        self.weight.write_bytes(b"tiny weight")
        self.full_weight = self.root / "yolov4.conv.137"
        self.configs = {}
        self.data_configs = {}
        for model_id, size, yolo_count in (("tiny320", 320, 2), ("tiny416", 416, 2), ("full", 608, 3)):
            cfg = self.run_dir / "configs" / f"{model_id}.cfg"
            cfg.write_text(self._cfg_text(size, yolo_count), encoding="utf-8")
            self.configs[model_id] = cfg
            data = self.run_dir / "data" / f"{model_id}.data"
            backup = self.run_dir / "checkpoints" / model_id
            backup.mkdir()
            data.write_text(
                "\n".join(
                    [
                        "classes=5",
                        f"names={self.names.as_posix()}",
                        f"train={self.train.as_posix()}",
                        f"valid={self.valid.as_posix()}",
                        f"backup={backup.as_posix()}",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            self.data_configs[model_id] = data
        self.plan = self._make_plan()

    def _full_ready_plan(self) -> dict:
        """创建 full 权重已绑定且 pilot 阻断仍保留的计划副本。"""
        self.full_weight.write_bytes(b"full weight fixture with a distinct size")
        plan = copy.deepcopy(self.plan)
        full_weight = plan["models"]["full"]["initial_weight"]
        full_weight.update(
            {
                "path": str(self.full_weight),
                "sha256": sha256_file(self.full_weight),
                "status": "READY",
            }
        )
        plan["models"]["full"]["command"][5] = str(self.full_weight)
        plan["file_bindings"].append(self._binding("full_weight", self.full_weight))
        plan["pilot"].update(
            {
                "status": "BLOCKED",
                "model_id": "tiny416",
                "updates": 8,
                "exit_code": -1073741510,
                "reason": "Windows 0xC000013A 中止，未生成 checkpoint。",
            }
        )
        return plan

    def _run_cli(self, plan: dict) -> tuple[int, dict]:
        """通过正式 CLI 校验隔离计划并读取机器报告。"""
        cli_dir = self.root / "cli"
        cli_dir.mkdir(exist_ok=True)
        input_path = cli_dir / "input.json"
        report_path = cli_dir / "report.json"
        summary_path = cli_dir / "summary.md"
        input_path.write_text(json.dumps(plan, ensure_ascii=False) + "\n", encoding="utf-8")
        with patch.multiple(
            d4,
            W5_R5_FULL_WEIGHT_SHA256=sha256_file(self.full_weight),
            W5_R5_FULL_WEIGHT_SIZE_BYTES=self.full_weight.stat().st_size,
        ):
            exit_code = main(
                [
                    "validate",
                    "--input",
                    str(input_path),
                    "--report",
                    str(report_path),
                    "--summary",
                    str(summary_path),
                ]
            )
        return exit_code, json.loads(report_path.read_text(encoding="utf-8"))

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def _cfg_text(size: int, yolo_count: int) -> str:
        sections = [
            "[net]",
            "batch=64",
            "subdivisions=16" if size != 608 else "subdivisions=32",
            f"width={size}",
            f"height={size}",
            "channels=3",
            "learning_rate=0.00261" if size != 608 else "learning_rate=0.0013",
            "momentum=0.9",
            "decay=0.0005",
            "burn_in=1000",
            "max_batches=6000",
            "steps=4800,5400",
        ]
        for _ in range(yolo_count):
            sections.extend(["[convolutional]", "filters=30", "size=1", "stride=1"])
            sections.extend(["[yolo]", "classes=5", "anchors=10,14,23,27", "mask=0,1"])
        return "\n".join(sections) + "\n"

    def _binding(self, name: str, path: Path, scope: str = "fixed") -> dict:
        return {"name": name, "path": str(path), "sha256": sha256_file(path), "scope": scope}

    def _make_plan(self) -> dict:
        models = {}
        for model_id in ("tiny320", "tiny416", "full"):
            training = {
                "batch": 64,
                "subdivisions": 16 if model_id != "full" else 32,
                "learning_rate": 0.00261 if model_id != "full" else 0.0013,
                "momentum": 0.9,
                "decay": 0.0005,
                "max_batches": 6000,
                "steps": [4800, 5400],
                "burn_in": 1000,
            }
            weight = {"path": str(self.weight), "sha256": sha256_file(self.weight), "status": "READY"}
            if model_id == "full":
                weight = {"path": str(self.root / "yolov4.conv.137"), "sha256": None, "status": "PENDING"}
            models[model_id] = {
                "model_id": model_id,
                "role": "pc_only_reference" if model_id == "full" else "board_candidate",
                "input_size": [608, 608] if model_id == "full" else [int(model_id[-3:])] * 2,
                "config_path": str(self.configs[model_id]),
                "config_sha256": sha256_file(self.configs[model_id]),
                "data_config_path": str(self.data_configs[model_id]),
                "data_config_sha256": sha256_file(self.data_configs[model_id]),
                "training": training,
                "initial_weight": weight,
                "command": [str(self.exe), "detector", "train", str(self.data_configs[model_id]), str(self.configs[model_id]), str(weight["path"]), "-dont_show"],
            }
        bindings = [
            self._binding("executable", self.exe),
            self._binding("seed_patch", self.patch),
            self._binding("source_archive", self.source_archive, "run"),
            self._binding("configure_log", self.configure_log, "run"),
            self._binding("build_log", self.build_log, "run"),
            self._binding("names", self.names),
            self._binding("train_list", self.train),
            self._binding("valid_list", self.valid),
            self._binding("manifest", self.manifest),
        ]
        for model_id in ("tiny320", "tiny416", "full"):
            bindings.extend(
                [
                    self._binding(f"{model_id}_cfg", self.configs[model_id], "run"),
                    self._binding(f"{model_id}_data", self.data_configs[model_id], "run"),
                ]
            )
        bindings.append(self._binding("tiny_weight", self.weight))
        bindings.extend(
            [
                self._binding("pilot_cfg", self.pilot_cfg, "run"),
                self._binding("pilot_data", self.pilot_data, "run"),
                self._binding("pilot_log", self.pilot_log, "run"),
            ]
        )
        for name, item in zip(("a", "b", "c"), self.smoke):
            bindings.append(self._binding(f"seed_smoke_{name}_log", Path(item["log"]), "run"))
            bindings.append(self._binding(f"seed_smoke_{name}_checkpoint", Path(item["checkpoint"]), "run"))
        return {
            "schema_version": "s1-t02-d4-v1",
            "run_dir": str(self.run_dir),
            "source": {
                "repository": str(self.source),
                "commit_observed": "59596d7880f6504768df41d6daa586f5cb2b932f",
                "patched_repository": str(self.patched_source),
                "source_archive": str(self.source_archive),
                "source_archive_sha256": sha256_file(self.source_archive),
                "diff_exit_code": 0,
                "patch_applied": True,
                "modified_files": [
                    {"path": str(self.modified_source_file), "sha256": sha256_file(self.modified_source_file)}
                ],
                "probe": {
                    "network_access": False,
                    "commands": [
                        {
                            "argv": ["git", "-C", self.source.as_posix(), "rev-parse", "HEAD"],
                            "stdout": "59596d7880f6504768df41d6daa586f5cb2b932f\n",
                            "stderr": "",
                            "exit_code": 0,
                        },
                        {
                            "argv": ["git", "-C", self.source.as_posix(), "diff", "--quiet"],
                            "stdout": "",
                            "stderr": "",
                            "exit_code": 0,
                        },
                    ],
                },
            },
            "build": {
                "source_directory": str(self.patched_source),
                "build_directory": str(self.run_dir / "build"),
                "executable_path": str(self.exe),
                "executable_sha256": sha256_file(self.exe),
                "configure_log": str(self.configure_log),
                "configure_log_sha256": sha256_file(self.configure_log),
                "configure_exit_code": 0,
                "build_log": str(self.build_log),
                "build_log_sha256": sha256_file(self.build_log),
                "build_exit_code": 0,
            },
            "seed": {
                "status": "READY",
                "patch_path": str(self.patch),
                "patch_sha256": sha256_file(self.patch),
                "bit_exact": False,
                "seed_smoke": self.smoke,
            },
            "data": {
                "names_path": str(self.names),
                "names_sha256": sha256_file(self.names),
                "train_list_path": str(self.train),
                "train_list_sha256": sha256_file(self.train),
                "valid_list_path": str(self.valid),
                "valid_list_sha256": sha256_file(self.valid),
                "manifest_path": str(self.manifest),
                "manifest_sha256": sha256_file(self.manifest),
                "train_count": 118001,
                "valid_count": 15195,
            },
            "preprocessing": {
                "reference_path": str(self.reference),
                "reference_sha256": sha256_file(self.reference),
            },
            "models": models,
            "file_bindings": bindings,
            "pilot": {
                "status": "NOT_EXECUTED",
                "model_id": "tiny416",
                "max_updates": 100,
                "config_path": str(self.pilot_cfg),
                "config_sha256": sha256_file(self.pilot_cfg),
                "data_config_path": str(self.pilot_data),
                "data_config_sha256": sha256_file(self.pilot_data),
                "combined_log": str(self.pilot_log),
                "combined_log_sha256": sha256_file(self.pilot_log),
            },
            "formal_evaluation": {"status": "NOT_EXECUTED"},
        }

    def test_valid_plan_is_pending_only(self) -> None:
        result = validate_plan(self.plan)
        self.assertEqual([], result["errors"])
        self.assertTrue(result["schema_valid"])
        self.assertEqual("PENDING", result["status"])
        self.assertIn("full.initial_weight", result["pending"])
        self.assertIn("tiny416_pilot", result["pending"])

    def test_model_id_and_size_are_bound(self) -> None:
        bad = copy.deepcopy(self.plan)
        bad["models"]["tiny320"]["model_id"] = "tiny416"
        bad["models"]["tiny416"]["input_size"] = [320, 320]
        result = validate_plan(bad)
        self.assertTrue(any("model_id" in item for item in result["errors"]))
        self.assertTrue(any("input_size" in item for item in result["errors"]))

    def test_hash_format_and_value_are_checked(self) -> None:
        bad = copy.deepcopy(self.plan)
        bad["models"]["tiny416"]["config_sha256"] = "bad"
        bad["build"]["executable_sha256"] = "0" * 64
        result = validate_plan(bad)
        self.assertTrue(any("config_sha256" in item for item in result["errors"]))
        self.assertTrue(any("executable_sha256" in item for item in result["errors"]))

    def test_preprocessing_reference_path_and_hash_are_checked(self) -> None:
        bad = copy.deepcopy(self.plan)
        bad["preprocessing"]["reference_sha256"] = "0" * 63
        result = validate_plan(bad)
        self.assertTrue(any("preprocessing.reference_sha256" in item for item in result["errors"]))
        bad = copy.deepcopy(self.plan)
        bad["preprocessing"]["reference_sha256"] = "0" * 64
        result = validate_plan(bad)
        self.assertTrue(any("preprocessing.reference_sha256" in item for item in result["errors"]))
        bad = copy.deepcopy(self.plan)
        bad["preprocessing"]["reference_path"] = str(self.names)
        result = validate_plan(bad)
        self.assertTrue(any("preprocessing.reference_sha256" in item for item in result["errors"]))

    def test_file_binding_scope_is_checked(self) -> None:
        bad = copy.deepcopy(self.plan)
        bad["file_bindings"][1]["scope"] = "run"
        result = validate_plan(bad)
        self.assertTrue(any("scope=run" in item for item in result["errors"]))

    def test_seed_requires_patch_when_ready(self) -> None:
        bad = copy.deepcopy(self.plan)
        bad["seed"]["patch_sha256"] = "0" * 64
        result = validate_plan(bad)
        self.assertTrue(any("seed.patch_sha256" in item for item in result["errors"]))

    def test_official_train_argv_positions_are_fixed(self) -> None:
        bad = copy.deepcopy(self.plan)
        bad["models"]["tiny416"]["command"][3] = "-dont_show"
        result = validate_plan(bad)
        self.assertTrue(any("commands.tiny416" in item for item in result["errors"]))

    def test_model_argv_paths_are_cross_bound(self) -> None:
        for index in (3, 4, 5):
            bad = copy.deepcopy(self.plan)
            bad["models"]["tiny416"]["command"][index] = str(self.names)
            result = validate_plan(bad)
            self.assertTrue(any(f"commands.tiny416[{index}]" in item for item in result["errors"]))

    def test_seed_and_build_bindings_are_checked(self) -> None:
        bad = copy.deepcopy(self.plan)
        bad["seed"]["seed_smoke"][0]["checkpoint_sha256"] = "0" * 64
        result = validate_plan(bad)
        self.assertTrue(any("seed.seed_smoke[0].checkpoint_sha256" in item for item in result["errors"]))
        bad = copy.deepcopy(self.plan)
        bad["build"]["build_log_sha256"] = "0" * 64
        result = validate_plan(bad)
        self.assertTrue(any("build.build_log_sha256" in item for item in result["errors"]))

    def test_plan_fields_must_match_file_bindings(self) -> None:
        bad = copy.deepcopy(self.plan)
        for binding in bad["file_bindings"]:
            if binding["name"] == "tiny416_cfg":
                binding["path"] = str(self.names)
                break
        result = validate_plan(bad)
        self.assertTrue(any("file_bindings.tiny416_cfg.path" in item for item in result["errors"]))
        bad = copy.deepcopy(self.plan)
        bad["file_bindings"] = [
            item for item in bad["file_bindings"] if item["name"] != "seed_smoke_b_checkpoint"
        ]
        result = validate_plan(bad)
        self.assertTrue(any("seed_smoke_b_checkpoint" in item for item in result["errors"]))

    def test_actual_formal_cfg_training_fields_are_checked(self) -> None:
        cfg = self.configs["tiny416"]
        original = cfg.read_text(encoding="utf-8")
        for old, new, field in (
            ("batch=64", "batch=32", "batch"),
            ("max_batches=6000", "max_batches=5000", "max_batches"),
            ("steps=4800,5400", "steps=4000,5400", "steps"),
        ):
            cfg.write_text(original.replace(old, new), encoding="utf-8")
            digest = sha256_file(cfg)
            self.plan["models"]["tiny416"]["config_sha256"] = digest
            for binding in self.plan["file_bindings"]:
                if binding["name"] == "tiny416_cfg":
                    binding["sha256"] = digest
            result = validate_plan(self.plan)
            self.assertTrue(any(f"models.tiny416.config.{field}" in item for item in result["errors"]))
        cfg.write_text(original, encoding="utf-8")

    def test_blocked_pilot_is_not_reported_as_ready(self) -> None:
        bad = copy.deepcopy(self.plan)
        bad["pilot"] = {
            "status": "BLOCKED",
            "model_id": "tiny416",
            "updates": 8,
            "exit_code": -1073741510,
            "reason": "宿主中止",
        }
        result = validate_plan(bad)
        self.assertEqual("BLOCKED", result["status"])
        self.assertTrue(any("tiny416_pilot" in item for item in result["blocking_reasons"]))

    def test_full_ready_uses_full_weight_binding_and_preserves_pilot_blocker(self) -> None:
        exit_code, report = self._run_cli(self._full_ready_plan())
        validation = report["validation"]
        self.assertEqual(0, exit_code)
        self.assertTrue(validation["schema_valid"])
        self.assertEqual([], validation["errors"])
        self.assertEqual("BLOCKED", validation["status"])
        self.assertTrue(any("tiny416_pilot" in item for item in validation["blocking_reasons"]))

    def test_full_weight_trust_anchor_matches_w5_r5_provenance(self) -> None:
        self.assertEqual(
            "11c5286cfbffabc9a3059927401ab3480e9483ceafd3265779a0dc26c769bed0",
            d4.W5_R5_FULL_WEIGHT_SHA256,
        )
        self.assertEqual(170038676, d4.W5_R5_FULL_WEIGHT_SIZE_BYTES)
        self.assertEqual(
            "768022d56bde61f4b7b24623b76ce0c0ab3edea0252a6afb4b7d1b6e72fe6fc8",
            d4.W5_R5_PROVENANCE_REPORT_SHA256,
        )

    def test_full_ready_requires_a_full_weight_binding(self) -> None:
        plan = self._full_ready_plan()
        plan["file_bindings"] = [
            item for item in plan["file_bindings"] if item["name"] != "full_weight"
        ]
        exit_code, report = self._run_cli(plan)
        validation = report["validation"]
        self.assertEqual(2, exit_code)
        self.assertFalse(validation["schema_valid"])
        self.assertEqual("BLOCKED", validation["status"])
        self.assertTrue(any("file_bindings.full_weight" in item for item in validation["errors"]))
        self.assertTrue(any("tiny416_pilot" in item for item in validation["blocking_reasons"]))

    def test_full_ready_rejects_wrong_binding_name(self) -> None:
        plan = self._full_ready_plan()
        full_binding = next(item for item in plan["file_bindings"] if item["name"] == "full_weight")
        full_binding["name"] = "other_weight"
        exit_code, report = self._run_cli(plan)
        validation = report["validation"]
        self.assertEqual(2, exit_code)
        self.assertFalse(validation["schema_valid"])
        self.assertTrue(any("file_bindings.full_weight" in item for item in validation["errors"]))

    def test_full_ready_rejects_incorrect_declared_and_binding_hashes(self) -> None:
        for mutate in ("model", "binding"):
            with self.subTest(mutate=mutate):
                plan = self._full_ready_plan()
                if mutate == "model":
                    plan["models"]["full"]["initial_weight"]["sha256"] = "0" * 64
                else:
                    full_binding = next(
                        item for item in plan["file_bindings"] if item["name"] == "full_weight"
                    )
                    full_binding["sha256"] = "0" * 64
                exit_code, report = self._run_cli(plan)
                validation = report["validation"]
                self.assertEqual(2, exit_code)
                self.assertFalse(validation["schema_valid"])
                self.assertTrue(any("full" in item and "SHA-256" in item for item in validation["errors"]))

    def test_full_weight_cannot_be_substituted_by_tiny_binding(self) -> None:
        plan = self._full_ready_plan()
        tiny_binding = next(item for item in plan["file_bindings"] if item["name"] == "tiny_weight")
        full_binding = next(item for item in plan["file_bindings"] if item["name"] == "full_weight")
        full_binding["path"] = tiny_binding["path"]
        full_binding["sha256"] = tiny_binding["sha256"]
        exit_code, report = self._run_cli(plan)
        validation = report["validation"]
        self.assertEqual(2, exit_code)
        self.assertFalse(validation["schema_valid"])
        self.assertTrue(any("file_bindings.full_weight.path" in item for item in validation["errors"]))
        self.assertTrue(any("file_bindings.full_weight.sha256" in item for item in validation["errors"]))
        self.assertTrue(any("tiny416_pilot" in item for item in validation["blocking_reasons"]))

    def test_consistent_full_model_command_and_binding_replacement_by_tiny_is_rejected(self) -> None:
        plan = self._full_ready_plan()
        tiny_hash = sha256_file(self.weight)
        full_weight = plan["models"]["full"]["initial_weight"]
        full_weight["path"] = str(self.weight)
        full_weight["sha256"] = tiny_hash
        plan["models"]["full"]["command"][5] = str(self.weight)
        full_binding = next(item for item in plan["file_bindings"] if item["name"] == "full_weight")
        full_binding["path"] = str(self.weight)
        full_binding["sha256"] = tiny_hash
        exit_code, report = self._run_cli(plan)
        validation = report["validation"]
        self.assertEqual(2, exit_code)
        self.assertFalse(validation["schema_valid"])
        self.assertEqual("BLOCKED", validation["status"])
        self.assertTrue(any("W5 R5 已核验 full 权重 SHA-256" in item for item in validation["errors"]))
        self.assertTrue(any("size_bytes" in item for item in validation["errors"]))
        self.assertTrue(any("tiny416_pilot" in item for item in validation["blocking_reasons"]))

    def test_tiny_ready_still_requires_tiny_weight_binding(self) -> None:
        plan = self._full_ready_plan()
        plan["file_bindings"] = [
            item for item in plan["file_bindings"] if item["name"] != "tiny_weight"
        ]
        exit_code, report = self._run_cli(plan)
        validation = report["validation"]
        self.assertEqual(2, exit_code)
        self.assertFalse(validation["schema_valid"])
        self.assertTrue(any("file_bindings.tiny_weight" in item for item in validation["errors"]))


class D4CliContract(unittest.TestCase):
    """检查输入输出文件不能原地覆盖。"""

    def test_json_round_trip_fixture_is_serializable(self) -> None:
        payload = {"status": "BLOCKED", "network_access": False}
        self.assertEqual(payload, json.loads(json.dumps(payload)))

    def test_report_and_summary_same_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="s1_t02_d4_cli_") as temp_dir:
            root = Path(temp_dir)
            input_path = root / "plan.json"
            input_path.write_text("{}\n", encoding="utf-8")
            same_output = root / "same.out"
            exit_code = main(
                [
                    "validate",
                    "--input", str(input_path),
                    "--report", str(same_output),
                    "--summary", str(same_output),
                ]
            )
            self.assertEqual(2, exit_code)


if __name__ == "__main__":
    unittest.main()
