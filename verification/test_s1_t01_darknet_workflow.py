"""S1-T01 官方 Darknet 流程入口的失败即停和命令构造回归测试。"""

from __future__ import annotations

import io
import struct
import tempfile
import unittest
from argparse import Namespace
from contextlib import ExitStack, redirect_stderr
from pathlib import Path
import hashlib
import json
from datetime import datetime
from unittest.mock import patch

try:
    import verification.s1_t01_darknet_workflow as workflow
except ModuleNotFoundError:
    import s1_t01_darknet_workflow as workflow

try:
    import verification.s1_t02_d6_detection_metrics as d6_metrics
except ModuleNotFoundError:
    import s1_t02_d6_detection_metrics as d6_metrics


class DarknetWorkflowTest(unittest.TestCase):
    """验证短训边界、审批门槛和官方命令格式。"""

    @staticmethod
    def _make_training_inputs(root: Path, train_bytes: bytes | None = None, valid_bytes: bytes | None = None) -> dict[str, object]:
        """建立隔离的训练清单、.data、manifest 和对应的人工期望索引。"""

        train_image = root / "train_image.jpg"
        valid_image = root / "valid_image.jpg"
        train_label = root / "train_image.txt"
        valid_label = root / "valid_image.txt"
        train_image.write_bytes(b"train image")
        valid_image.write_bytes(b"valid image")
        train_label.write_text("", encoding="utf-8")
        valid_label.write_text("", encoding="utf-8")
        train_list = root / "train.list"
        valid_list = root / "valid.list"
        train_list.write_bytes(train_bytes if train_bytes is not None else f"{train_image}\n".encode())
        valid_list.write_bytes(valid_bytes if valid_bytes is not None else f"{valid_image}\n".encode())
        data_config = root / "gesture.data"
        data_config.write_text(
            f"classes=5\ntrain={train_list}\nvalid={valid_list}\n",
            encoding="utf-8",
        )
        manifest = root / "manifest.csv"
        manifest.write_text(
            "image,label,split,session_id,person_id,source,license,is_real\n"
            "train_image.jpg,train_image.txt,train,session_train,person_train,synthetic,CC0,false\n"
            "valid_image.jpg,valid_image.txt,val,session_val,person_val,synthetic,CC0,false\n",
            encoding="utf-8",
        )
        args = Namespace(data_config=data_config, manifest=manifest, data_root=root)
        snapshot, manifest_images, data_config_values = workflow._capture_training_input_snapshot(
            args, root, "preflight"
        )
        return {
            "args": args,
            "manifest_images": manifest_images,
            "data_config_values": data_config_values,
            "snapshot": snapshot,
            "train_list": train_list,
            "valid_list": valid_list,
            "train_image": train_image,
            "valid_image": valid_image,
            "data_config": data_config,
            "manifest": manifest,
        }

    @staticmethod
    def _make_approved_preflight_fixture(root: Path, dry_run: bool = False) -> dict[str, object]:
        """建立获批 manifest A 及可将其替换为合法 B 的 train 预检夹具。"""

        inputs = DarknetWorkflowTest._make_training_inputs(root)
        train_image = inputs["train_image"]
        valid_image = inputs["valid_image"]
        train_label = root / "train_image.txt"
        valid_label = root / "valid_image.txt"
        second_train_image = root / "second_train_image.jpg"
        second_train_label = root / "second_train_image.txt"
        second_train_image.write_bytes(b"second train image")
        second_train_label.write_text("", encoding="utf-8")

        manifest = inputs["manifest"]
        header = "image,label,split,session_id,person_id,source,license,is_real\n"
        train_row = "train_image.jpg,train_image.txt,train,session_train,person_train,friend,approved,true\n"
        no_hand_row = "valid_image.jpg,valid_image.txt,val,session_no_hand,person_no_hand,friend,approved,true\n"
        manifest_a = (header + train_row + no_hand_row).encode("utf-8")
        manifest_b = (
            header
            + train_row
            + no_hand_row
            + "second_train_image.jpg,second_train_image.txt,train,session_train_2,person_train_2,friend,approved,true\n"
        ).encode("utf-8")
        manifest.write_bytes(manifest_a)
        inputs["train_list"].write_text(f"{train_image}\n", encoding="utf-8")
        inputs["valid_list"].write_text(f"{valid_image}\n", encoding="utf-8")

        names = root / "gesture.names"
        names.write_text("fist\npalm\none\ntwo_up\nthree\n", encoding="utf-8")
        backup = root / "backup"
        backup.mkdir()
        data_config = inputs["data_config"]
        data_config.write_text(
            f"classes=5\nnames={names}\ntrain={inputs['train_list']}\nvalid={inputs['valid_list']}\n"
            f"backup={backup}\nsaveweights=1000\nsavelast=500\n",
            encoding="utf-8",
        )
        model_config = root / "gesture.cfg"
        model_config.write_text("[net]\nmax_batches=6000\n", encoding="utf-8")
        executable = root / "darknet.exe"
        executable.write_bytes(b"synthetic executable")
        environment_report = root / "environment.json"
        environment_report.write_text("{}", encoding="utf-8")
        initial_weights = root / "initial.weights"
        initial_weights.write_bytes(b"initial")

        dataset_report = root / "dataset.json"
        dataset_report.write_text(
            json.dumps(
                {
                    "status": "PASS_AUTOMATED_MANUAL_PENDING",
                    "manifest": str(manifest),
                    "data_root": str(root),
                    "checks": {"AC02": "通过", "AC03": "通过", "AC04": "待人工抽查"},
                }
            ),
            encoding="utf-8",
        )
        dataset_approval = root / "approval.json"
        approval = {
            "status": "APPROVED",
            "reviewer": "Wong",
            "dataset_report": str(dataset_report),
            "dataset_report_sha256": hashlib.sha256(dataset_report.read_bytes()).hexdigest(),
            "manifest_sha256": hashlib.sha256(manifest_a).hexdigest(),
            "no_hand_images": [
                {"image": "valid_image.jpg", "split": "val", "role": "no_hand", "manifest_row": 3}
            ],
        }
        dataset_approval.write_text(json.dumps(approval), encoding="utf-8")

        args = Namespace(
            action="train",
            formal_training=True,
            darknet_executable=executable,
            environment_report=environment_report,
            data_root=root,
            manifest=manifest,
            dataset_report=dataset_report,
            dataset_approval=dataset_approval,
            data_config=data_config,
            model_config=model_config,
            names_file=names,
            working_directory=root,
            run_dir=root / "run",
            report=root / "report.json",
            timeout_seconds=60.0,
            no_progress_timeout_seconds=30.0,
            darknet_seed=424242,
            initial_weights=initial_weights,
            checkpoint_output=backup / "gesture_1000.weights",
            dry_run=dry_run,
        )
        return {
            **inputs,
            "args": args,
            "manifest_a": manifest_a,
            "manifest_b": manifest_b,
            "second_train_image": second_train_image,
            "report": workflow._base_report(args),
            "dataset_approval": approval,
        }

    @staticmethod
    def _preflight_test_patches(dataset_gate_side_effect: object) -> ExitStack:
        """替换与清单竞态无关的环境和模型依赖，保留真实数据 gate。"""

        stack = ExitStack()
        stack.enter_context(patch.object(workflow, "_validate_environment_gate", return_value={}))
        stack.enter_context(patch.object(workflow, "_validate_dataset_gate", side_effect=dataset_gate_side_effect))
        stack.enter_context(patch.object(workflow, "_validate_model_config", return_value={"max_batches": 6000}))
        stack.enter_context(patch.object(workflow, "_validate_checkpoint_io", return_value=None))
        stack.enter_context(patch.object(workflow, "_check_no_existing_process", return_value=None))
        stack.enter_context(patch.object(workflow, "_identity_artifacts", return_value={}))
        return stack

    @staticmethod
    def _attach_training_binding(report: dict[str, object], fixture: dict[str, object]) -> None:
        """把通过合成预检的输入快照装入运行测试报告。"""

        report["training_input_binding"] = {
            "status": "PREFLIGHT_CAPTURED",
            "preflight": fixture["snapshot"],
            "before_child": None,
            "after_child": None,
            "execution_status": "NOT_STARTED",
            "scope_notice": "仅比较 preflight、before_child、after_child 各采样点；不证明 child 运行期间未发生后又恢复的修改。",
        }

    @staticmethod
    def _make_train_execute_fixture(
        root: Path,
        training_inputs: dict[str, object],
        dry_run: bool = False,
    ) -> tuple[Namespace, dict[str, object], dict[str, object]]:
        """构造不依赖 CUDA/Darknet 的训练执行夹具。"""

        checkpoint = root / "backup" / "gesture_10.weights"
        args = Namespace(
            action="train",
            data_config=training_inputs["data_config"],
            manifest=training_inputs["manifest"],
            data_root=root,
            model_config=root / "gesture.cfg",
            initial_weights=root / "initial.weights",
            checkpoint_output=checkpoint,
            run_dir=root / "run",
            timeout_seconds=10.0,
            no_progress_timeout_seconds=10.0,
            dry_run=dry_run,
            darknet_seed=424242,
        )
        report = workflow._base_report(args)
        DarknetWorkflowTest._attach_training_binding(report, training_inputs)
        report["inputs"] = {"checkpoint_mapping": {"candidate_names": [checkpoint.name]}}
        report["outputs"] = {"checkpoint_output": {"path": str(checkpoint)}}
        context = {
            "executable": root / "darknet.exe",
            "working_directory": root,
            "checkpoint_output": checkpoint,
            "checkpoint_plan": {"candidate_names": [checkpoint.name]},
            "manifest_images": training_inputs["manifest_images"],
        }
        return args, report, context

    def test_training_input_snapshot_binds_exact_bytes_counts_paths_and_utc8(self) -> None:
        """训练输入快照必须记录实际路径、字节、行数、哈希、manifest 计数及时点。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            train_image = root / "train_image.jpg"
            train_image.write_bytes(b"train image")
            fixture = self._make_training_inputs(
                root,
                train_bytes=f"{train_image}\n# synthetic note\n\n".encode("utf-8"),
            )
            snapshot = fixture["snapshot"]
            train_list = fixture["train_list"]
            self.assertEqual(snapshot["status"], "CAPTURED")
            self.assertEqual(snapshot["capture_point"], "preflight")
            captured = datetime.fromisoformat(snapshot["captured_at_utc8"])
            self.assertEqual(captured.utcoffset().total_seconds(), 8 * 60 * 60)
            self.assertEqual(snapshot["data_config"]["path"], workflow._canonical_path(fixture["data_config"]))
            self.assertEqual(snapshot["data_config"]["sha256"], hashlib.sha256(fixture["data_config"].read_bytes()).hexdigest())
            self.assertEqual(snapshot["manifest"]["path"], workflow._canonical_path(fixture["manifest"]))
            self.assertEqual(snapshot["manifest"]["sha256"], hashlib.sha256(fixture["manifest"].read_bytes()).hexdigest())
            self.assertEqual(snapshot["manifest"]["size_bytes"], fixture["manifest"].stat().st_size)
            self.assertEqual(snapshot["manifest"]["sample_counts"], {"train": 1, "val": 1, "test": 0})
            self.assertEqual(snapshot["lists"]["train"]["path"], workflow._canonical_path(train_list))
            self.assertEqual(snapshot["lists"]["train"]["sha256"], hashlib.sha256(train_list.read_bytes()).hexdigest())
            self.assertEqual(snapshot["lists"]["train"]["size_bytes"], train_list.stat().st_size)
            self.assertEqual(snapshot["lists"]["train"]["line_count"], 3)
            self.assertEqual(snapshot["lists"]["train"]["sample_count"], 1)

    def test_manifest_replacement_and_restore_during_parse_cannot_mix_snapshot_and_counts(self) -> None:
        """解析期间 manifest A→B→A 时，快照映射和计数仍绑定已捕获的 A 字节。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = self._make_training_inputs(root)
            manifest_path = inputs["manifest"]
            manifest_a = manifest_path.read_bytes()
            train_b = root / "second_train_image.jpg"
            label_b = root / "second_train_image.txt"
            train_b.write_bytes(b"second train image")
            label_b.write_text("", encoding="utf-8")
            manifest_b = (
                "image,label,split,session_id,person_id,source,license,is_real\n"
                "train_image.jpg,train_image.txt,train,session_train,person_train,synthetic,CC0,false\n"
                "second_train_image.jpg,second_train_image.txt,train,session_train_2,person_train_2,synthetic,CC0,false\n"
                "valid_image.jpg,valid_image.txt,val,session_val,person_val,synthetic,CC0,false\n"
            ).encode("utf-8")
            original_parser = workflow._load_manifest_images_from_bytes

            def replace_and_restore(raw: bytes, manifest: Path, data_root: Path, errors: list[str]) -> dict[str, dict[str, dict[str, object]]]:
                """模拟解析期间磁盘文件换成 B 后再恢复 A。"""

                manifest.write_bytes(manifest_b)
                try:
                    return original_parser(raw, manifest, data_root, errors)
                finally:
                    manifest.write_bytes(manifest_a)

            with patch.object(workflow, "_load_manifest_images_from_bytes", side_effect=replace_and_restore):
                snapshot, manifest_images, _ = workflow._capture_training_input_snapshot(
                    inputs["args"], root, "preflight"
                )
            self.assertEqual(snapshot["status"], "CAPTURED")
            self.assertEqual(snapshot["manifest"]["sha256"], hashlib.sha256(manifest_a).hexdigest())
            self.assertEqual(snapshot["manifest"]["size_bytes"], len(manifest_a))
            self.assertEqual(snapshot["manifest"]["sample_counts"], {"train": 1, "val": 1, "test": 0})
            self.assertEqual(len(manifest_images["train"]), 1)
            self.assertEqual(len(manifest_images["val"]), 1)
            self.assertEqual(snapshot["lists"]["train"]["capture_status"], "CAPTURED")

    def test_manifest_replaced_after_approval_blocks_preflight_and_never_spawns_child(self) -> None:
        """批准 A 后在预检前或 child 前替换成 B，均须阻断且不调用 child。"""

        for replacement_point in ("before_preflight", "after_approval_gate"):
            with self.subTest(replacement_point=replacement_point), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                fixture = self._make_approved_preflight_fixture(root)
                args = fixture["args"]
                report = fixture["report"]
                manifest = fixture["manifest"]
                manifest_a = fixture["manifest_a"]
                manifest_b = fixture["manifest_b"]
                expected_hash = hashlib.sha256(manifest_a).hexdigest()
                actual_hash = hashlib.sha256(manifest_b).hexdigest()
                validate_gate = workflow._validate_dataset_gate
                if replacement_point == "before_preflight":
                    manifest.write_bytes(manifest_b)

                def approve_a_then_replace_with_b(
                    report_path: Path,
                    approval_path: Path,
                    manifest_path: Path,
                    data_root: Path,
                    errors: list[str],
                    training_manifest_snapshot: dict[str, object] | None = None,
                ) -> dict[str, object]:
                    """按稳定快照真实核验批准 SHA，并可在校验后替换磁盘文件。"""

                    result = validate_gate(
                        report_path,
                        approval_path,
                        manifest_path,
                        data_root,
                        errors,
                        training_manifest_snapshot=training_manifest_snapshot,
                    )
                    if replacement_point == "after_approval_gate":
                        self.assertEqual(errors, [])
                        manifest_path.write_bytes(manifest_b)
                    return result

                with self._preflight_test_patches(approve_a_then_replace_with_b) as _patches:
                    context = workflow._preflight(args, report)

                binding = report["training_input_binding"]
                snapshot = binding["preflight"]
                self.assertEqual(
                    snapshot["status"],
                    "FAILED" if replacement_point == "before_preflight" else "CAPTURED",
                )
                expected_snapshot_hash = (
                    actual_hash if replacement_point == "before_preflight" else expected_hash
                )
                self.assertEqual(snapshot["manifest"]["sha256"], expected_snapshot_hash)
                self.assertEqual(report["inputs"]["manifest_sha256"], snapshot["manifest"]["sha256"])
                if replacement_point == "after_approval_gate":
                    self.assertEqual(report["errors"], [])
                with patch.object(workflow, "_run_command") as runner:
                    workflow._execute(args, report, context)
                runner.assert_not_called()
                if replacement_point == "before_preflight":
                    self.assertTrue(
                        any("获批 manifest SHA-256 与训练输入快照不一致" in error for error in report["errors"])
                    )
                    self.assertEqual(binding["status"], "BLOCKED")
                    self.assertEqual(binding["execution_status"], "BLOCKED_PREFLIGHT")
                    self.assertEqual(report["status"], "BLOCKED_PREFLIGHT")
                else:
                    self.assertEqual(binding["preflight"]["manifest"]["sha256"], expected_hash)
                    self.assertEqual(binding["before_child"]["manifest"]["sha256"], actual_hash)
                    self.assertFalse(binding["before_child"]["comparison_to_preflight"]["matches"])
                    self.assertEqual(binding["execution_status"], "PRELAUNCH_REJECTED")
                    self.assertEqual(report["status"], "EXECUTION_FAILED")
                    self.assertTrue(any("启动前训练输入与 preflight 不一致" in error for error in report["errors"]))

    def test_approved_manifest_snapshot_is_the_reported_training_identity(self) -> None:
        """审批清单 A 与快照一致时预检通过，报告 SHA/字节数直接来自该快照。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = self._make_approved_preflight_fixture(root)
            manifest = fixture["manifest"]
            manifest_a = fixture["manifest_a"]
            validate_gate = workflow._validate_dataset_gate

            def validate_unchanged_gate(
                report_path: Path,
                approval_path: Path,
                manifest_path: Path,
                data_root: Path,
                errors: list[str],
                training_manifest_snapshot: dict[str, object] | None = None,
            ) -> dict[str, object]:
                """使用真实 gate 验证清单 A 和对应批准。"""

                return validate_gate(
                    report_path,
                    approval_path,
                    manifest_path,
                    data_root,
                    errors,
                    training_manifest_snapshot=training_manifest_snapshot,
                )

            manifest_file_hash_reads: list[Path] = []
            original_sha256 = workflow._sha256

            def track_sha256(path: Path) -> str:
                if workflow._same_path(path, manifest):
                    manifest_file_hash_reads.append(path)
                return original_sha256(path)

            with self._preflight_test_patches(validate_unchanged_gate) as _patches, patch.object(
                workflow, "_sha256", side_effect=track_sha256
            ):
                workflow._preflight(fixture["args"], fixture["report"])

            report = fixture["report"]
            snapshot = report["training_input_binding"]["preflight"]
            expected_hash = hashlib.sha256(manifest_a).hexdigest()
            self.assertEqual(report["errors"], [])
            self.assertEqual(report["training_input_binding"]["status"], "PREFLIGHT_CAPTURED")
            self.assertEqual(report["inputs"]["manifest_sha256"], expected_hash)
            self.assertEqual(report["inputs"]["manifest_size_bytes"], len(manifest_a))
            self.assertEqual(snapshot["manifest"]["sha256"], expected_hash)
            self.assertEqual(snapshot["manifest"]["size_bytes"], len(manifest_a))
            self.assertEqual(
                fixture["dataset_approval"]["manifest_sha256"],
                snapshot["manifest"]["sha256"],
            )
            self.assertEqual(
                report["inputs"]["manifest_sha256"],
                snapshot["manifest"]["sha256"],
            )
            self.assertEqual(manifest_file_hash_reads, [])

    def test_training_dry_run_records_only_preflight_and_never_spawns_child(self) -> None:
        """dry-run 明确为 PLANNED_NO_EXECUTION，不能伪称执行前后复核。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = self._make_training_inputs(root)
            args, report, context = self._make_train_execute_fixture(root, inputs, dry_run=True)
            with patch.object(workflow, "_run_command") as runner:
                workflow._execute(args, report, context)
            self.assertEqual(report["status"], "PLANNED_NO_EXECUTION")
            binding = report["training_input_binding"]
            self.assertEqual(binding["status"], "PLANNED_NO_EXECUTION")
            self.assertEqual(binding["execution_status"], "PLANNED_NO_EXECUTION")
            self.assertIsNone(binding["before_child"])
            self.assertIsNone(binding["after_child"])
            self.assertIn("仅记录 preflight", report["acceptance"]["training_input_binding"])
            self.assertIn("不证明 child 运行期间", binding["scope_notice"])
            runner.assert_not_called()

    def test_training_list_change_before_child_prevents_spawn(self) -> None:
        """正式 child 启动前任一训练清单内容变化都必须被拦截。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = self._make_training_inputs(root)
            args, report, context = self._make_train_execute_fixture(root, inputs)
            inputs["valid_list"].write_bytes(inputs["valid_list"].read_bytes() + b"# changed before launch\n")
            with patch.object(workflow, "_run_command") as runner:
                workflow._execute(args, report, context)
            self.assertEqual(report["status"], "EXECUTION_FAILED")
            self.assertEqual(report["training_input_binding"]["execution_status"], "PRELAUNCH_REJECTED")
            self.assertFalse(report["training_input_binding"]["before_child"]["comparison_to_preflight"]["matches"])
            self.assertTrue(any("启动前训练输入与 preflight 不一致" in error for error in report["errors"]))
            self.assertEqual(report["acceptance"]["command_executed"], False)
            runner.assert_not_called()

    def test_training_list_change_during_child_is_detected_after_return(self) -> None:
        """child 运行期间修改任一清单必须在返回后造成执行失败。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = self._make_training_inputs(root)
            args, report, context = self._make_train_execute_fixture(root, inputs)

            def mutate_during_child(*_args: object, **_kwargs: object) -> dict[str, object]:
                """模拟 child 改写 train.list 后正常返回。"""

                inputs["train_list"].write_bytes(inputs["train_list"].read_bytes() + b"# changed in child\n")
                context["checkpoint_output"].parent.mkdir(parents=True, exist_ok=True)
                context["checkpoint_output"].write_bytes(b"synthetic checkpoint")
                return {
                    "exit_code": 0,
                    "stop_reason": None,
                    "non_finite_observed": False,
                    "loss_token_observed": True,
                    "observed_update_steps": list(range(1, 11)),
                    "output": "loss=1.0",
                    "log_sha256": "synthetic-log",
                }

            with patch.object(workflow, "_run_command", side_effect=mutate_during_child) as runner:
                workflow._execute(args, report, context)
            self.assertEqual(runner.call_count, 1)
            self.assertEqual(report["training_input_binding"]["execution_status"], "POSTRUN_MISMATCH")
            self.assertFalse(report["training_input_binding"]["after_child"]["comparison_to_preflight"]["matches"])
            self.assertEqual(report["status"], "EXECUTION_FAILED")
            self.assertTrue(any("返回后训练输入与 preflight 不一致" in error for error in report["errors"]))
            self.assertNotIn("ac05_candidate", report.get("acceptance", {}))

    def test_child_nonzero_and_postrun_list_read_failure_remain_failed(self) -> None:
        """child 非零退出且返回后清单缺失时，报告保留两项失败证据。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = self._make_training_inputs(root)
            args, report, context = self._make_train_execute_fixture(root, inputs)

            def fail_child_and_remove_list(*_args: object, **_kwargs: object) -> dict[str, object]:
                """模拟 child 失败后 valid.list 消失。"""

                inputs["valid_list"].unlink()
                return {
                    "exit_code": 1,
                    "stop_reason": None,
                    "non_finite_observed": False,
                    "loss_token_observed": False,
                    "observed_update_steps": [],
                    "output": "synthetic child failure",
                }

            with patch.object(workflow, "_run_command", side_effect=fail_child_and_remove_list):
                workflow._execute(args, report, context)
            self.assertEqual(report["status"], "EXECUTION_FAILED")
            self.assertEqual(report["commands"][0]["exit_code"], 1)
            self.assertEqual(report["training_input_binding"]["after_child"]["status"], "FAILED")
            self.assertFalse(
                report["training_input_binding"]["after_child"]["comparison_to_preflight"]["matches"]
            )
            self.assertTrue(any("清单缺失、不可读或读取期间发生变化" in error for error in report["errors"]))

    def test_missing_or_unreadable_training_list_blocks_report_and_child(self) -> None:
        """缺失或不可读清单均不得让 train/resume 报告进入通过状态。"""

        for mode in ("missing", "unreadable"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                inputs = self._make_training_inputs(root)
                train_list = inputs["train_list"]
                if mode == "missing":
                    train_list.unlink()
                    snapshot, _, _ = workflow._capture_training_input_snapshot(
                        inputs["args"], root, "preflight"
                    )
                elif mode == "unreadable":
                    original_read_bytes = Path.read_bytes

                    def fail_training_list_read(path: Path) -> bytes:
                        if path == train_list:
                            raise PermissionError("synthetic access denied")
                        return original_read_bytes(path)

                    with patch.object(Path, "read_bytes", fail_training_list_read):
                        snapshot, _, _ = workflow._capture_training_input_snapshot(
                            inputs["args"], root, "preflight"
                        )
                self.assertEqual(snapshot["status"], "FAILED")
                self.assertEqual(snapshot["lists"]["train"]["capture_status"], "FAILED")
                args, report, context = self._make_train_execute_fixture(root, inputs, dry_run=True)
                report["training_input_binding"].update(
                    {"status": "BLOCKED", "preflight": snapshot, "execution_status": "BLOCKED_PREFLIGHT"}
                )
                with patch.object(workflow, "_run_command") as runner:
                    workflow._execute(args, report, context)
                self.assertEqual(report["status"], "BLOCKED_PREFLIGHT")
                self.assertNotEqual(report["status"], "PASS")
                runner.assert_not_called()

    def test_missing_or_unreadable_manifest_blocks_snapshot_and_child(self) -> None:
        """manifest 缺失、不可读或采集期间变化时必须阻断执行。"""

        for mode in ("missing", "unreadable", "unstable"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                inputs = self._make_training_inputs(root)
                manifest = inputs["manifest"]
                if mode == "missing":
                    manifest.unlink()
                    snapshot, _, _ = workflow._capture_training_input_snapshot(
                        inputs["args"], root, "preflight"
                    )
                elif mode == "unreadable":
                    original_read_bytes = Path.read_bytes

                    def fail_manifest_read(path: Path) -> bytes:
                        if path == manifest:
                            raise PermissionError("synthetic manifest access denied")
                        return original_read_bytes(path)

                    with patch.object(Path, "read_bytes", fail_manifest_read):
                        snapshot, _, _ = workflow._capture_training_input_snapshot(
                            inputs["args"], root, "preflight"
                        )
                else:
                    original_read_bytes = Path.read_bytes

                    def change_manifest_during_read(path: Path) -> bytes:
                        """在读出 A 后替换为不同字节，使前后 stat 不同。"""

                        raw = original_read_bytes(path)
                        if path == manifest:
                            path.write_bytes(raw + b"# changed during read\n")
                        return raw

                    with patch.object(Path, "read_bytes", change_manifest_during_read):
                        snapshot, _, _ = workflow._capture_training_input_snapshot(
                            inputs["args"], root, "preflight"
                        )
                self.assertEqual(snapshot["status"], "FAILED")
                self.assertEqual(snapshot["manifest"]["capture_status"], "FAILED")
                if mode == "unstable":
                    self.assertTrue(any("读取期间发生变化" in error for error in snapshot["errors"]))
                else:
                    self.assertTrue(snapshot["errors"])
                args, report, context = self._make_train_execute_fixture(root, inputs, dry_run=True)
                report["training_input_binding"].update(
                    {"status": "BLOCKED", "preflight": snapshot, "execution_status": "BLOCKED_PREFLIGHT"}
                )
                with patch.object(workflow, "_run_command") as runner:
                    workflow._execute(args, report, context)
                self.assertEqual(report["status"], "BLOCKED_PREFLIGHT")
                runner.assert_not_called()

    def test_process_check_accepts_localized_notice_when_csv_has_valid_process_rows(self) -> None:
        """忽略本地化空任务提示，只按完整 CSV 进程行判断且无目标行时通过。"""

        executable = Path("darknet.exe")
        output = (
            "INFO: ��� localized no-task notice\r\n"
            '"python.exe","1234","Console","1","10,000 K"\r\n'
            '"explorer.exe","2345","Console","1","20,000 K"\r\n'
            '"darknet-helper.exe","3456","Console","1","30,000 K"\r\n'
        )
        completed = Namespace(returncode=0, stdout=output, stderr="")
        with patch.object(workflow.os, "name", "nt"), patch.object(
            workflow.subprocess, "run", return_value=completed
        ) as runner:
            error = workflow._check_no_existing_process(executable)

        self.assertIsNone(error)
        command = runner.call_args.args[0]
        self.assertEqual(command, ["tasklist", "/FO", "CSV", "/NH"])
        self.assertNotIn("/FI", command)

    def test_process_check_blocks_exact_darknet_image_name(self) -> None:
        """完整 tasklist CSV 中 image name 大小写不同但精确同名时阻断。"""

        output = (
            '"python.exe","1234","Console","1","10,000 K"\r\n'
            '"DarkNet.EXE","4321","Console","1","25,000 K"\r\n'
        )
        completed = Namespace(returncode=0, stdout=output, stderr="")
        with patch.object(workflow.os, "name", "nt"), patch.object(
            workflow.subprocess, "run", return_value=completed
        ):
            error = workflow._check_no_existing_process(Path("darknet.exe"))

        self.assertIsNotNone(error)
        self.assertIn("检测到已有同名 Darknet 进程", error)

    def test_process_check_fails_closed_for_untrusted_or_failed_output(self) -> None:
        """无有效进程行、畸形 CSV、非零退出和命令异常都不能误放行。"""

        valid_row = '"python.exe","1234","Console","1","10,000 K"\r\n'
        cases = (
            (Namespace(returncode=0, stdout="INFO: ��� no-task notice\r\n", stderr=""), "可验证"),
            (Namespace(returncode=0, stdout="unrecognized output\r\n" + valid_row, stderr=""), "非 CSV 输出"),
            (
                Namespace(returncode=0, stdout='"bad row","x"\r\n' + valid_row, stderr=""),
                "不是可信的 CSV 进程记录",
            ),
            (
                Namespace(returncode=0, stdout='"unterminated\r\n' + valid_row, stderr=""),
                "CSV 无法解析",
            ),
            (Namespace(returncode=1, stdout=valid_row, stderr="tasklist failed"), "退出码 1"),
            (Namespace(returncode=0, stdout=valid_row, stderr="tasklist warning"), "错误输出"),
        )
        for completed, expected_error in cases:
            with self.subTest(expected_error=expected_error), patch.object(
                workflow.os, "name", "nt"
            ), patch.object(workflow.subprocess, "run", return_value=completed):
                error = workflow._check_no_existing_process(Path("darknet.exe"))
                self.assertIsNotNone(error)
                self.assertIn(expected_error, error)

        with patch.object(workflow.os, "name", "nt"), patch.object(
            workflow.subprocess, "run", side_effect=OSError("synthetic tasklist failure")
        ):
            error = workflow._check_no_existing_process(Path("darknet.exe"))
        self.assertIsNotNone(error)
        self.assertIn("无法确认同名进程状态", error)

        with patch.object(workflow.os, "name", "nt"), patch.object(
            workflow.subprocess,
            "run",
            side_effect=workflow.subprocess.TimeoutExpired(cmd="tasklist", timeout=10),
        ):
            error = workflow._check_no_existing_process(Path("darknet.exe"))
        self.assertIsNotNone(error)
        self.assertIn("无法确认同名进程状态", error)

    def test_darknet_seed_parser_accepts_only_nonnegative_uint32(self) -> None:
        """种子解析接受边界值并拒绝缺失、负数、溢出和非十进制文本。"""

        self.assertEqual(workflow._parse_darknet_seed("0"), 0)
        self.assertEqual(workflow._parse_darknet_seed("4294967295"), 4294967295)
        for value in ("-1", "4294967296", "1.0", "abc", "+1", " 1", ""):
            with self.subTest(value=value):
                with self.assertRaises(Exception):
                    workflow._parse_darknet_seed(value)

    def test_darknet_seed_is_child_only_and_parent_is_unchanged(self) -> None:
        """显式种子只覆盖子进程环境，父 Python 环境保持原值。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / "seed.log"
            command = [
                workflow.sys.executable,
                "-c",
                f"import os; print(os.environ.get('{workflow.DARKNET_SEED_ENV}'), flush=True)",
            ]
            with patch.dict(workflow.os.environ, {workflow.DARKNET_SEED_ENV: "parent-value"}, clear=False):
                result = workflow._run_command(command, root, log, 10, 10, darknet_seed=424242)
                self.assertEqual(workflow.os.environ[workflow.DARKNET_SEED_ENV], "parent-value")
            self.assertEqual(result["exit_code"], 0)
            self.assertNotIn("output", result)
            self.assertEqual(result["log"], str(log.resolve()))
            self.assertEqual(result["log_sha256"], hashlib.sha256(log.read_bytes()).hexdigest())
            self.assertEqual(result["log_size_bytes"], log.stat().st_size)
            self.assertEqual(result["seed_binding"]["environment_variable"], workflow.DARKNET_SEED_ENV)
            self.assertEqual(result["seed_binding"]["value"], 424242)
            self.assertTrue(result["seed_binding"]["parent_process_unchanged"])

    def test_run_command_parses_runtime_log_without_returning_raw_output(self) -> None:
        """完整进程输出只用于提取摘要，命令结果不携带原始日志文本。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / "parsed.log"
            command = [
                workflow.sys.executable,
                "-c",
                "print('10: loss=0.125', flush=True); print('11: loss=0.0625', flush=True)",
            ]
            result = workflow._run_command(command, root, log, 10, 10)

            self.assertEqual(result["observed_update_steps"], [10, 11])
            self.assertTrue(result["loss_token_observed"])
            self.assertFalse(result["non_finite_observed"])
            self.assertEqual(result["exit_code"], 0)
            self.assertIsNone(result["stop_reason"])
            self.assertNotIn("output", result)
            self.assertNotIn(log.read_text(encoding="utf-8"), json.dumps(result, ensure_ascii=False))
            self.assertEqual(result["log"], str(log.resolve()))
            self.assertEqual(result["log_sha256"], hashlib.sha256(log.read_bytes()).hexdigest())
            self.assertEqual(result["log_size_bytes"], len(log.read_bytes()))

    def test_run_command_fails_closed_when_log_hash_cannot_be_collected(self) -> None:
        """运行日志摘要采集失败时保留明确错误并使命令结果不可通过。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / "hash_failure.log"
            command = [workflow.sys.executable, "-c", "print('10: loss=0.125', flush=True)"]
            with patch.object(workflow, "_sha256", side_effect=OSError("synthetic digest failure")):
                result = workflow._run_command(command, root, log, 10, 10)

            self.assertEqual(result["exit_code"], 0)
            self.assertEqual(result["stop_reason"], "运行日志证据不可用")
            self.assertIn("SHA-256 或字节数不可采集", result["error"])
            self.assertIsNone(result["log_sha256"])
            self.assertIsNone(result["log_size_bytes"])
            self.assertNotIn("output", result)

    def test_run_command_fails_closed_when_log_cannot_be_read(self) -> None:
        """运行日志读取失败必须留下错误并阻止命令结果通过。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / "read_failure.log"
            command = [workflow.sys.executable, "-c", "print('10: loss=0.125', flush=True)"]
            with patch.object(workflow, "_read_log", side_effect=OSError("synthetic read failure")):
                result = workflow._run_command(command, root, log, 10, 10)

            self.assertEqual(result["exit_code"], 0)
            self.assertEqual(result["stop_reason"], "运行日志不可读")
            self.assertIn("无法验证完整输出", result["error"])
            self.assertTrue(result["log_sha256"])
            self.assertIsInstance(result["log_size_bytes"], int)
            self.assertNotIn("output", result)

    def test_seed_binding_is_recorded_for_train_and_default_is_unseeded(self) -> None:
        """训练报告记录显式种子，未提供种子时不改变默认无注入语义。"""

        seeded = workflow._base_report(Namespace(action="train", darknet_seed=424242))
        unseeded = workflow._base_report(Namespace(action="train"))
        self.assertEqual(seeded["seed_binding"]["value"], 424242)
        self.assertTrue(seeded["seed_binding"]["passed_to_child_process"])
        self.assertIsNone(unseeded["seed_binding"]["value"])
        self.assertFalse(unseeded["seed_binding"]["passed_to_child_process"])

    def test_model_config_rejects_long_training(self) -> None:
        """完整长训 max_batches 不能从短训入口启动。"""

        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "long.cfg"
            for max_batches in (4000, 6000):
                with self.subTest(max_batches=max_batches):
                    config.write_text(
                        f"[net]\nmax_batches={max_batches}\nwidth=320\nheight=320\n[yolo]\nclasses=5\n",
                        encoding="utf-8",
                    )
                    errors: list[str] = []
                    workflow._validate_model_config(config, errors)
                    self.assertTrue(any("max_batches" in error for error in errors))

    def test_formal_training_profile_accepts_only_exact_6000_schedule(self) -> None:
        """正式 profile 只接受 6000 步及获批的 4800/5400 学习率节点。"""

        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "formal.cfg"
            for max_batches in (5999, 6001):
                with self.subTest(max_batches=max_batches):
                    config.write_text(
                        "[net]\n"
                        f"max_batches={max_batches}\nsteps=4800,5400\nwidth=416\nheight=416\n"
                        "[convolutional]\nfilters=30\n[yolo]\nclasses=5\n",
                        encoding="utf-8",
                    )
                    errors: list[str] = []
                    workflow._validate_model_config(config, errors, formal_training=True)
                    self.assertTrue(any("max_batches 必须恰好为 6000" in error for error in errors))

            config.write_text(
                "[net]\nmax_batches=6000\nsteps=4800,5400\nwidth=416\nheight=416\n"
                "[convolutional]\nfilters=30\n[yolo]\nclasses=5\n",
                encoding="utf-8",
            )
            errors = []
            model = workflow._validate_model_config(config, errors, formal_training=True)
            self.assertEqual(errors, [])
            self.assertEqual(model["max_batches"], 6000)
            self.assertEqual(model["steps"], [4800, 5400])

            config.write_text(
                "[net]\nmax_batches=6000\nsteps=4800,5401\nwidth=416\nheight=416\n"
                "[convolutional]\nfilters=30\n[yolo]\nclasses=5\n",
                encoding="utf-8",
            )
            errors = []
            workflow._validate_model_config(config, errors, formal_training=True)
            self.assertTrue(any("steps 必须为 4800,5400" in error for error in errors))

    def test_formal_flag_is_limited_to_train_and_resume_and_reported(self) -> None:
        """正式 profile 参数仅注册在 train/resume，且报告明确绑定 profile 与验收边界。"""

        parser = workflow._build_parser()
        common = [
            "--darknet-executable", "darknet.exe",
            "--environment-report", "environment.json",
            "--data-root", "data",
            "--manifest", "manifest.csv",
            "--dataset-report", "dataset.json",
            "--dataset-approval", "approval.json",
            "--data-config", "gesture.data",
            "--model-config", "gesture.cfg",
            "--names-file", "gesture.names",
            "--working-directory", "work",
            "--run-dir", "run",
            "--report", "report.json",
        ]
        train = parser.parse_args([
            "train", "--formal-training", *common,
            "--initial-weights", "initial.weights",
            "--checkpoint-output", "backup/gesture_1000.weights",
        ])
        resume = parser.parse_args([
            "resume", "--formal-training", *common,
            "--checkpoint", "backup/gesture_1000.weights",
            "--resume-from-step", "1000",
            "--checkpoint-output", "backup/gesture_2000.weights",
        ])
        self.assertTrue(train.formal_training)
        self.assertTrue(resume.formal_training)
        self.assertEqual(workflow._base_report(train)["training_profile"], "formal_6000")
        self.assertEqual(workflow._base_report(resume)["training_profile"], "formal_6000")
        self.assertIn("不代表精度", workflow._base_report(train)["training_profile_notice"])

        evaluate_args = [
            "evaluate", *common,
            "--weights", "weights",
            "--valid-list", "valid.list",
            "--zero-prediction-image", "no_hand.jpg",
            "--formal-training",
        ]
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as raised:
            parser.parse_args(evaluate_args)
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("unrecognized arguments: --formal-training", stderr.getvalue())
        evaluate = parser.parse_args(evaluate_args[:-1])
        self.assertEqual(workflow._base_report(evaluate)["training_profile"], "not_applicable")

    def test_formal_profile_is_bound_to_execution_result(self) -> None:
        """训练命令、运行结果和候选验收字段都记录同一正式 profile。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            training_inputs = self._make_training_inputs(root)
            run_dir = root / "run"
            backup = root / "backup"
            backup.mkdir()
            checkpoint = backup / "gesture_10.weights"
            args = Namespace(
                action="train",
                formal_training=True,
                darknet_seed=424242,
                data_config=training_inputs["data_config"],
                manifest=training_inputs["manifest"],
                data_root=root,
                model_config=root / "gesture.cfg",
                initial_weights=root / "initial.weights",
                checkpoint_output=checkpoint,
                run_dir=run_dir,
                timeout_seconds=21600.0,
                no_progress_timeout_seconds=300.0,
                dry_run=False,
            )
            report = workflow._base_report(args)
            self._attach_training_binding(report, training_inputs)
            report["inputs"] = {"checkpoint_mapping": {"candidate_names": [checkpoint.name]}}
            report["outputs"] = {"checkpoint_output": {"path": str(checkpoint)}}
            context = {
                "executable": root / "darknet.exe",
                "working_directory": root,
                "checkpoint_output": checkpoint,
                "checkpoint_plan": {"candidates": [str(checkpoint)]},
                "manifest_images": training_inputs["manifest_images"],
            }

            def fake_train(*_args: object, **_kwargs: object) -> dict[str, object]:
                """模拟训练返回并创建一个隔离的测试检查点。"""

                checkpoint.write_bytes(b"simulated checkpoint")
                return {
                    "exit_code": 0,
                    "stop_reason": None,
                    "non_finite_observed": False,
                    "loss_token_observed": True,
                    "observed_update_steps": list(range(1, 6001)),
                    "output": "FULL_LOG_SENTINEL_" + ("x" * 10000),
                    "log_sha256": "simulated-log-sha256",
                    "log_size_bytes": 10016,
                    "log": str(run_dir / "darknet.log"),
                }

            with patch.object(workflow, "_run_command", side_effect=fake_train):
                workflow._execute(args, report, context)

            self.assertEqual(report["status"], "EXECUTED_REVIEW_REQUIRED")
            self.assertEqual(report["planned_commands"][0]["training_profile"], "formal_6000")
            self.assertEqual(report["commands"][0]["training_profile"], "formal_6000")
            self.assertEqual(report["acceptance"]["training_profile"], "formal_6000")
            self.assertNotIn("output", report["commands"][0])
            serialized_report = json.dumps(report, ensure_ascii=False)
            self.assertNotIn("FULL_LOG_SENTINEL_", serialized_report)
            self.assertEqual(report["commands"][0]["log_size_bytes"], 10016)
            self.assertEqual(report["commands"][0]["log"], str((run_dir / "darknet.log")))

    def test_formal_update_range_requires_all_contiguous_steps(self) -> None:
        """正式 train 和 resume 的日志不得缺步、提前结束或越过 6000。"""

        errors: list[str] = []
        workflow._validate_formal_update_range("train", list(range(1, 6001)), None, errors)
        self.assertEqual(errors, [])

        workflow._validate_formal_update_range("train", list(range(1, 6000)), None, errors)
        self.assertTrue(any("未证明本次动作完整连续更新至 6000" in error for error in errors))

        errors = []
        workflow._validate_formal_update_range("resume", list(range(21, 6001)), 20, errors)
        self.assertEqual(errors, [])

        errors = []
        workflow._validate_formal_update_range("resume", list(range(21, 6000)), 20, errors)
        self.assertTrue(any("未证明本次动作完整连续更新至 6000" in error for error in errors))

    def test_formal_training_preflight_accepts_train_resume_and_rejects_resume_at_6000(self) -> None:
        """正式 profile 通过完整结构预检，并保持恢复步数严格小于 6000。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_root = root / "data"
            working = root / "working"
            run_dir = root / "run"
            backup = root / "backup"
            for path in (data_root, working, run_dir, backup):
                path.mkdir()
            executable = root / "darknet.exe"
            executable.write_bytes(b"binary")
            manifest = data_root / "manifest.csv"
            manifest.write_text("fixture manifest\n", encoding="utf-8")
            environment_report = root / "environment.json"
            environment_report.write_text("{}", encoding="utf-8")
            dataset_report = root / "dataset.json"
            dataset_report.write_text("{}", encoding="utf-8")
            dataset_approval = root / "approval.json"
            dataset_approval.write_text("{}", encoding="utf-8")
            train_list = root / "train.list"
            train_list.write_text("", encoding="utf-8")
            valid_list = root / "valid.list"
            valid_list.write_text("", encoding="utf-8")
            names = root / "gesture.names"
            names.write_text("fist\npalm\none\ntwo_up\nthree\n", encoding="utf-8")
            data_config = root / "gesture.data"
            data_config.write_text(
                f"classes=5\nnames={names}\ntrain={train_list}\nvalid={valid_list}\n"
                f"backup={backup}\nsaveweights=1000\nsavelast=500\n",
                encoding="utf-8",
            )
            model_config = root / "gesture.cfg"
            model_config.write_text(
                "[net]\nmax_batches=6000\nsteps=4800,5400\nwidth=416\nheight=416\n"
                "[convolutional]\nfilters=30\n[yolo]\nclasses=5\n",
                encoding="utf-8",
            )
            initial_weights = root / "initial.weights"
            initial_weights.write_bytes(b"initial")

            def make_args(action: str, resume_from_step: int = 1000) -> Namespace:
                """结构化构造 train/resume 预检参数，不启动 Darknet。"""

                checkpoint_output = backup / (
                    "gesture_1000.weights" if action == "train" else "gesture_final.weights"
                )
                checkpoint = backup / f"gesture_{resume_from_step}.weights"
                if action == "resume" and not checkpoint.exists():
                    checkpoint.write_bytes(b"resume input")
                return Namespace(
                    action=action,
                    formal_training=True,
                    darknet_executable=executable,
                    environment_report=environment_report,
                    data_root=data_root,
                    manifest=manifest,
                    dataset_report=dataset_report,
                    dataset_approval=dataset_approval,
                    data_config=data_config,
                    model_config=model_config,
                    names_file=names,
                    working_directory=working,
                    run_dir=run_dir,
                    report=root / "report.json",
                    dry_run=True,
                    timeout_seconds=21600.0,
                    no_progress_timeout_seconds=300.0,
                    darknet_seed=424242,
                    initial_weights=initial_weights,
                    checkpoint_output=checkpoint_output,
                    checkpoint=checkpoint,
                    resume_from_step=resume_from_step,
                )

            patches = [
                patch.object(workflow, "_validate_environment_gate", return_value={}),
                patch.object(
                    workflow,
                    "_validate_dataset_gate",
                    return_value={
                        "approval": {"manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest()},
                        "manifest_snapshot_matches_approval": True,
                    },
                ),
                patch.object(
                    workflow,
                    "_load_manifest_images_from_bytes",
                    return_value={"train": {}, "val": {}, "test": {}},
                ),
                patch.object(workflow, "_load_valid_list", return_value=[]),
                patch.object(workflow, "_validate_no_hand_approval", return_value={}),
                patch.object(workflow, "_check_no_existing_process", return_value=None),
                patch.object(workflow, "_identity_artifacts", return_value={}),
            ]
            with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
                default_train = make_args("train")
                default_train.formal_training = False
                default_train.darknet_seed = None
                default_report = workflow._base_report(default_train)
                workflow._preflight(default_train, default_report)
                self.assertEqual(default_report["training_profile"], "diagnostic_short")
                self.assertFalse(any("必须显式提供 --darknet-seed" in error for error in default_report["errors"]))
                self.assertTrue(any("短训安全范围" in error for error in default_report["errors"]))

                data_a = data_config.read_bytes()
                data_b = (
                    f"classes=4\nnames={root / 'wrong.names'}\ntrain={train_list}\nvalid={valid_list}\n"
                    f"backup={root / 'missing_backup'}\nsaveweights=0\nsavelast=500\n"
                ).encode("utf-8")
                original_text_parser = workflow._parse_key_values_text

                def replace_data_during_parse(text: str) -> dict[str, str]:
                    """解析已捕获 A 文本时暂将路径内容替换为 B，再恢复 A。"""

                    data_config.write_bytes(data_b)
                    try:
                        return original_text_parser(text)
                    finally:
                        data_config.write_bytes(data_a)

                race_args = make_args("train")
                race_report = workflow._base_report(race_args)
                with patch.object(
                    workflow,
                    "_parse_key_values_text",
                    side_effect=replace_data_during_parse,
                ), patch.object(workflow, "_parse_key_values", side_effect=AssertionError("禁止从路径重读 .data")) as path_parser:
                    workflow._preflight(race_args, race_report)
                expected_data_values = original_text_parser(data_a.decode("utf-8-sig"))
                expected_data_sha = hashlib.sha256(data_a).hexdigest()
                path_parser.assert_not_called()
                self.assertEqual(race_report["errors"], [])
                self.assertEqual(
                    race_report["inputs"]["data_config"],
                    workflow._canonical_path(data_config),
                )
                self.assertEqual(race_report["inputs"]["data_config_values"], expected_data_values)
                self.assertEqual(race_report["inputs"]["artifact_sha256"]["data_config"], expected_data_sha)
                self.assertEqual(
                    race_report["training_input_binding"]["preflight"]["data_config"]["sha256"],
                    expected_data_sha,
                )
                self.assertEqual(
                    race_report["training_input_binding"]["preflight"]["data_config"]["size_bytes"],
                    len(data_a),
                )
                self.assertEqual(
                    race_report["training_input_binding"]["preflight"]["data_config"]["values"],
                    expected_data_values,
                )
                self.assertEqual(data_config.read_bytes(), data_a)

                for action in ("train", "resume"):
                    with self.subTest(action=action, seed="missing"):
                        formal_without_seed = make_args(action, 2345 if action == "resume" else 1000)
                        formal_without_seed.darknet_seed = None
                        formal_without_seed_report = workflow._base_report(formal_without_seed)
                        workflow._preflight(formal_without_seed, formal_without_seed_report)
                        self.assertEqual(formal_without_seed_report["status"], "BLOCKED_PREFLIGHT")
                        self.assertTrue(
                            any("必须显式提供 --darknet-seed" in error for error in formal_without_seed_report["errors"])
                        )
                        if action == "resume":
                            formal_without_seed.checkpoint.unlink()

                for action, step in (("train", 1000), ("resume", 5999)):
                    with self.subTest(action=action, step=step):
                        args = make_args(action, step)
                        report = workflow._base_report(args)
                        context = workflow._preflight(args, report)
                        self.assertEqual(report["errors"], [])
                        self.assertEqual(report["training_profile"], "formal_6000")
                        self.assertEqual(report["seed_binding"]["value"], 424242)
                        self.assertTrue(report["seed_binding"]["passed_to_child_process"])
                        self.assertEqual(report["inputs"]["model_config_values"]["max_batches"], 6000)
                        self.assertEqual(context["checkpoint_output"], args.checkpoint_output.resolve())
                        if action == "train":
                            expected = [
                                "gesture_last.weights",
                                *(f"gesture_{step}.weights" for step in range(1000, 6001, 1000)),
                                "gesture_final.weights",
                            ]
                            self.assertEqual(context["checkpoint_plan"]["candidate_names"], expected)
                            self.assertNotIn("gesture_1001.weights", context["checkpoint_plan"]["candidate_names"])

                invalid_resume = make_args("resume", 6000)
                invalid_report = workflow._base_report(invalid_resume)
                workflow._preflight(invalid_resume, invalid_report)
                self.assertTrue(any("必须小于 cfg max_batches" in error for error in invalid_report["errors"]))

    def test_model_config_requires_eleven_batches_for_resume(self) -> None:
        """十步训练不能为恢复再提供一个更新步。"""

        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "short.cfg"
            config.write_text(
                "[net]\nmax_batches=10\nwidth=320\nheight=320\n[yolo]\nclasses=5\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            workflow._validate_model_config(config, errors)
            self.assertTrue(any("短训安全范围" in error for error in errors))

    def test_build_commands_are_official_darknet_without_shell(self) -> None:
        """训练、恢复和测试命令都固定为 Darknet detector 子命令。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_cfg = root / "gesture.data"
            model_cfg = root / "gesture.cfg"
            names = root / "gesture.names"
            data_cfg.write_text("classes=5\nnames=gesture.names\nvalid=valid.txt\n", encoding="utf-8")
            model_cfg.write_text("[net]\nmax_batches=11\nwidth=320\nheight=320\n[yolo]\nclasses=5\n", encoding="utf-8")
            names.write_text("fist\npalm\none\ntwo_up\nthree\n", encoding="utf-8")
            image = root / "image.jpg"
            context = {"executable": root / "darknet.exe", "working_directory": root, "valid_images": [image]}
            common = {
                "data_config": data_cfg,
                "model_config": model_cfg,
                "initial_weights": root / "initial.weights",
                "checkpoint": root / "checkpoint.weights",
                "weights": root / "checkpoint.weights",
            }
            train = Namespace(action="train", **common)
            resume = Namespace(action="resume", **common)
            evaluate = Namespace(action="evaluate", **common)
            self.assertEqual(workflow._commands_for_action(train, context)[0][1:3], ["detector", "train"])
            self.assertEqual(workflow._commands_for_action(resume, context)[0][1:3], ["detector", "train"])
            self.assertEqual(workflow._commands_for_action(evaluate, context)[0][1:3], ["detector", "test"])
            evaluate_command = workflow._commands_for_action(evaluate, context)[0]
            self.assertIn("-out", evaluate_command)
            self.assertNotIn(workflow._darknet_cli_path(image), evaluate_command)
            self.assertNotIn("-ext_output", evaluate_command)
            self.assertNotIn("-shell", workflow._commands_for_action(train, context)[0])

    def test_evaluate_help_describes_runtime_stdin_workflow(self) -> None:
        """evaluate help 必须准确描述 runtime stdin 单进程流程。"""

        help_text = " ".join(workflow._build_parser().format_help().split())
        expected = "读取 valid 清单生成隔离 runtime stdin 清单，单进程执行官方 Darknet detector test -out JSON；-thresh 0.249999 仅用于捕获，并逐图解析"
        self.assertIn(expected, help_text)
        self.assertNotIn("带显式 filename", help_text)

    def test_capture_threshold_cli_and_metric_lower_boundary_are_compatible(self) -> None:
        """显式捕获阈值低于D6下限，确保0.25经Darknet严格比较后仍可评估。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args = Namespace(
                action="evaluate",
                data_config=root / "gesture.data",
                model_config=root / "gesture.cfg",
                weights=root / "weights",
                run_dir=root / "run",
            )
            command = workflow._commands_for_action(
                args,
                {
                    "executable": root / "darknet.exe",
                    "working_directory": root,
                    "evaluation_json": args.run_dir / "evaluation.json",
                },
            )[0]
            threshold_index = command.index("-thresh")
            threshold_text = command[threshold_index + 1]
            self.assertEqual(threshold_text, "0.249999")

            darknet_float_threshold = struct.unpack("f", struct.pack("f", float(threshold_text)))[0]
            metric_floor = workflow.D6_SCORE_THRESHOLD_RANGE[0]
            self.assertGreater(metric_floor, darknet_float_threshold)
            captured_scores = [0.25] if 0.25 > darknet_float_threshold else []
            self.assertEqual(captured_scores, [0.25])
            prediction = d6_metrics.Prediction(
                image_key=str(root / "image.png"),
                class_id=0,
                name="fist",
                confidence=captured_scores[0],
                box=(0.1, 0.1, 0.3, 0.3),
                source_order=0,
            )
            self.assertEqual(d6_metrics.stable_nms([prediction], metric_floor, 0.45, 15), [prediction])

            policy = workflow._base_report(args)["evaluation_threshold_policy"]
            self.assertEqual(policy["darknet_capture"]["cli_flag"], "-thresh")
            self.assertEqual(policy["darknet_capture"]["value"], workflow.D6_CAPTURE_THRESHOLD)
            self.assertEqual(policy["final_metric_score_threshold"]["allowed_range_inclusive"], [0.25, 0.50])
            self.assertIsNone(policy["final_metric_score_threshold"]["selected"])
            self.assertFalse(policy["final_metric_score_threshold"]["frozen"])

    def test_dataset_gate_rejects_current_unapproved_report(self) -> None:
        """缺少人工批准时不能进入训练或评估。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "manifest.csv"
            report = root / "dataset.json"
            approval = root / "approval.json"
            manifest.write_text("image,split,session_id,person_id,source,license,is_real\n", encoding="utf-8")
            report.write_text(
                '{"status":"FAIL","manifest":"' + str(manifest).replace("\\", "\\\\") + '","checks":{"AC02":"通过自动检查","AC03":"未通过","AC04":"未执行"}}',
                encoding="utf-8",
            )
            approval.write_text("{\"status\":\"APPROVED\",\"reviewer\":\"Wong\"}", encoding="utf-8")
            errors: list[str] = []
            workflow._validate_dataset_gate(report, approval, manifest, root, errors)
            self.assertTrue(errors)
            self.assertTrue(any("AC03" in error or "人工批准" in error for error in errors))

    def test_run_command_stops_on_non_finite_log(self) -> None:
        """日志出现 NaN 时立即终止，不返回成功。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / "run.log"
            command = [
                workflow.sys.executable,
                "-c",
                "print('10: loss=NaN', flush=True); import time; time.sleep(5)",
            ]
            result = workflow._run_command(command, root, log, 10, 10)
            self.assertEqual(result["stop_reason"], "日志出现 NaN/Inf")

    def test_each_yolo_head_requires_preceding_filters(self) -> None:
        """多检测头必须逐头检查前置卷积 filters。"""

        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "multi.cfg"
            config.write_text(
                "[net]\nmax_batches=11\nwidth=320\nheight=320\n"
                "[convolutional]\nfilters=29\n[ yolo ]\nclasses=5\n"
                "[convolutional]\nfilters=30\n[yolo]\nclasses=5\n"
                "[yolo]\nclasses=5\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            workflow._validate_model_config(config, errors)
            self.assertTrue(any("第 1 个" in error and "filters" in error for error in errors))
            self.assertTrue(any("第 3 个" in error and "前置" in error for error in errors))

    def test_data_config_requires_official_checkpoint_keys(self) -> None:
        """data 配置缺少训练清单、backup 或保存间隔时必须失败。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_cfg = root / "gesture.data"
            names = root / "gesture.names"
            data_cfg.write_text("classes=5\nnames=gesture.names\nvalid=valid.txt\n", encoding="utf-8")
            names.write_text("fist\npalm\none\ntwo_up\nthree\n", encoding="utf-8")
            errors: list[str] = []
            workflow._validate_data_config(data_cfg, names, errors, root)
            self.assertTrue(any("必要键" in error for error in errors))

    def test_dataset_approval_reviewer_must_be_exact_wong(self) -> None:
        """空 reviewer 和非 Wong 身份都不能通过人工批准门。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "manifest.csv"
            report = root / "dataset.json"
            manifest.write_text("image,label,split,session_id,person_id,source,license,is_real\n", encoding="utf-8")
            report.write_text(
                json.dumps(
                    {
                        "status": "PASS_AUTOMATED_MANUAL_PENDING",
                        "manifest": str(manifest),
                        "data_root": str(root),
                        "checks": {"AC02": "通过", "AC03": "通过", "AC04": "待人工抽查"},
                    }
                ),
                encoding="utf-8",
            )
            for reviewer in ("Not-Wong", ""):
                approval = root / f"approval_{len(reviewer)}.json"
                approval.write_text(
                    json.dumps(
                        {
                            "status": "APPROVED",
                            "reviewer": reviewer,
                            "dataset_report": str(report),
                            "dataset_report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
                            "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
                        }
                    ),
                    encoding="utf-8",
                )
                errors: list[str] = []
                workflow._validate_dataset_gate(report, approval, manifest, root, errors)
                self.assertTrue(any("严格为 Wong" in error for error in errors))

    def test_manifest_requires_label_and_existing_binding(self) -> None:
        """manifest 必须提供标签列并拒绝缺失标签文件。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "manifest.csv"
            manifest.write_text(
                "image,label,split,session_id,person_id,source,license,is_real\n"
                "images/a.jpg,labels/a.txt,train,s,p,src,lic,1\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            value = workflow._load_manifest_images(manifest, root, errors)
            self.assertIn("train", value)
            self.assertTrue(any("标签不存在" in error for error in errors))

    def test_checkpoint_plan_binds_cfg_stem_and_save_intervals(self) -> None:
        """检查点候选必须来自 backup、cfg 基名及 saveweights/savelast。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            backup = root / "backup"
            backup.mkdir()
            cfg = root / "gesture.cfg"
            values = {"backup": "backup", "saveweights": "10", "savelast": "5"}
            errors: list[str] = []
            plan = workflow._checkpoint_plan(values, cfg, root, 20, 0, errors)
            self.assertEqual(errors, [])
            self.assertEqual(
                plan["candidate_names"],
                ["gesture_last.weights", "gesture_10.weights", "gesture_20.weights", "gesture_final.weights"],
            )
            self.assertIsNotNone(workflow._checkpoint_name_kind(Path("gesture_last.weights"), "gesture"))
            self.assertIsNone(workflow._checkpoint_name_kind(Path("other_10.weights"), "gesture"))
            errors = []
            workflow._validate_checkpoint_io(
                "train", None, backup / "gesture_15.weights", plan, "gesture", None, errors
            )
            self.assertTrue(any("可能产生" in error for error in errors))
            errors = []
            workflow._validate_checkpoint_io(
                "train", None, backup / "gesture_10.weights", plan, "gesture", None, errors
            )
            self.assertEqual(errors, [])
            existing = backup / "gesture_10.weights"
            existing.write_bytes(b"old")
            errors = []
            workflow._validate_checkpoint_io(
                "train", None, existing, plan, "gesture", None, errors
            )
            self.assertTrue(any("拒绝覆盖" in error for error in errors))

    def test_resume_accepts_only_numbered_checkpoint_and_protects_input(self) -> None:
        """resume 只接受 numbered 输入，并保留输入输出及哈希保护。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            backup = root / "backup"
            backup.mkdir()
            cfg = root / "gesture.cfg"
            values = {"backup": "backup", "saveweights": "10", "savelast": "5"}
            plan = workflow._checkpoint_plan(values, cfg, root, 20, 10, [])
            self.assertEqual(
                plan["candidate_names"],
                ["gesture_last.weights", "gesture_20.weights", "gesture_final.weights"],
            )
            numbered = backup / "gesture_10.weights"
            numbered.write_bytes(b"input")
            errors: list[str] = []
            workflow._validate_checkpoint_io(
                "resume", numbered, backup / "gesture_final.weights", plan, "gesture", 10, errors
            )
            self.assertEqual(errors, [])
            errors = []
            workflow._validate_checkpoint_io(
                "resume", numbered, backup / "gesture_15.weights", plan, "gesture", 10, errors
            )
            self.assertTrue(any("可能产生" in error for error in errors))
            for suffix in ("last", "final"):
                errors = []
                workflow._validate_checkpoint_io(
                    "resume", backup / f"gesture_{suffix}.weights", backup / "gesture_20.weights", plan, "gesture", 10, errors
                )
                self.assertTrue(any("只允许同一 cfg 基名的 numbered" in error for error in errors))

    def test_checkpoint_plan_simulates_dynamic_resume_intervals(self) -> None:
        """恢复起点非整除保存间隔时，候选点须逐步更新以贴合 Darknet。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            backup = root / "backup"
            backup.mkdir()
            cfg = root / "gesture.cfg"
            values = {"backup": "backup", "saveweights": "10", "savelast": "5"}
            errors: list[str] = []
            plan = workflow._checkpoint_plan(values, cfg, root, 20, 7, errors)
            self.assertEqual(errors, [])
            self.assertEqual(
                plan["candidate_names"],
                ["gesture_10.weights", "gesture_last.weights", "gesture_20.weights", "gesture_final.weights"],
            )
            self.assertNotIn("gesture_17.weights", plan["candidate_names"])

    def test_checkpoint_plan_formal_6000_contains_only_save_intervals(self) -> None:
        """正式 6000 步只列出每千步编号点、last 与 final，不枚举间隔外更新。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            backup = root / "backup"
            backup.mkdir()
            cfg = root / "gesture_yolov4_tiny_416_d8_formal.cfg"
            values = {"backup": "backup", "saveweights": "1000", "savelast": "500"}
            errors: list[str] = []
            plan = workflow._checkpoint_plan(values, cfg, root, 6000, 0, errors)
            expected = [
                f"{cfg.stem}_last.weights",
                *(f"{cfg.stem}_{step}.weights" for step in range(1000, 6001, 1000)),
                f"{cfg.stem}_final.weights",
            ]
            self.assertEqual(errors, [])
            self.assertEqual(plan["candidate_names"], expected)
            self.assertEqual(len(plan["candidate_names"]), 8)
            self.assertNotIn(f"{cfg.stem}_1001.weights", plan["candidate_names"])

    def test_path_length_gate_blocks_train_resume_and_evaluate(self) -> None:
        """实际传给 Darknet 的超长路径必须在三种动作启动前失败。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            long_path = root / ("p" * 280 + ".weights")
            common = [
                "--darknet-executable", str(root / "darknet.exe"),
                "--environment-report", str(root / "environment.json"),
                "--data-root", str(root),
                "--manifest", str(root / "manifest.csv"),
                "--dataset-report", str(root / "dataset.json"),
                "--dataset-approval", str(root / "approval.json"),
                "--data-config", str(root / "gesture.data"),
                "--model-config", str(root / "gesture.cfg"),
                "--names-file", str(root / "gesture.names"),
                "--working-directory", str(root),
                "--run-dir", str(root / "run"),
                "--report", str(root / "report.json"),
            ]
            for action in ("train", "resume", "evaluate"):
                with self.subTest(action=action):
                    if action == "train":
                        argv = [*common, "--initial-weights", str(long_path), "--checkpoint-output", str(root / "backup" / "gesture_10.weights")]
                        context = {
                            "executable": root / "darknet.exe",
                            "working_directory": root,
                            "valid_images": [],
                            "checkpoint_output": root / "backup" / "gesture_10.weights",
                            "checkpoint_plan": {"candidates": []},
                        }
                    elif action == "resume":
                        argv = [*common, "--checkpoint", str(long_path), "--resume-from-step", "10", "--checkpoint-output", str(root / "backup" / "gesture_20.weights")]
                        context = {
                            "executable": root / "darknet.exe",
                            "working_directory": root,
                            "valid_images": [],
                            "checkpoint_output": root / "backup" / "gesture_20.weights",
                            "checkpoint_plan": {"candidates": []},
                        }
                    else:
                        image = root / ("i" * 280 + ".jpg")
                        argv = [*common, "--weights", str(root / "weights"), "--valid-list", str(root / "valid.txt"), "--zero-prediction-image", str(image)]
                        context = {
                            "executable": root / "darknet.exe",
                            "working_directory": root,
                            "valid_images": [image],
                            "evaluation_json": root / "run" / "evaluation.json",
                            "evaluation_output_paths": [root / "run" / "detections" / "eval_000001.json"],
                        }
                    with patch.object(workflow, "_preflight", return_value=context), patch.object(workflow, "_execute") as execute:
                        code = workflow.main([action, *argv])
                    saved = json.loads((root / "report.json").read_text(encoding="utf-8"))
                    self.assertEqual(code, 2)
                    self.assertEqual(saved["status"], "BLOCKED_PREFLIGHT")
                    self.assertEqual(saved["exit_code"], 2)
                    self.assertTrue(any("256" in error and "不会截断" in error for error in saved["errors"]))
                    execute.assert_not_called()

    def test_top_level_exit_code_is_zero_for_success_and_dry_run(self) -> None:
        """成功执行和 dry-run 报告的顶层退出码都必须为零。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            training_inputs = self._make_training_inputs(root)
            checkpoint_output = root / "backup" / "gesture_10.weights"
            context = {
                "executable": root / "darknet.exe",
                "working_directory": root,
                "valid_images": [],
                "checkpoint_output": checkpoint_output,
                "checkpoint_plan": {"candidates": []},
                "manifest_images": training_inputs["manifest_images"],
            }
            common = [
                "train",
                "--darknet-executable", str(root / "darknet.exe"),
                "--environment-report", str(root / "environment.json"),
                "--data-root", str(root),
                "--manifest", str(training_inputs["manifest"]),
                "--dataset-report", str(root / "dataset.json"),
                "--dataset-approval", str(root / "approval.json"),
                "--data-config", str(training_inputs["data_config"]),
                "--model-config", str(root / "gesture.cfg"),
                "--names-file", str(root / "gesture.names"),
                "--working-directory", str(root),
                "--run-dir", str(root / "run"),
                "--initial-weights", str(root / "initial.weights"),
                "--checkpoint-output", str(checkpoint_output),
            ]

            def fake_success(args: Namespace, report: dict[str, object], value: dict[str, object]) -> None:
                """注入成功动作结果，验证 main 的报告收口。"""

                report["status"] = "EXECUTED_REVIEW_REQUIRED"

            def fake_preflight(args: Namespace, report: dict[str, object]) -> dict[str, object]:
                """注入具有真实合成输入快照的最小预检上下文。"""

                self._attach_training_binding(report, training_inputs)
                return context

            success_report = root / "success.json"
            with patch.object(workflow, "_preflight", side_effect=fake_preflight), patch.object(
                workflow, "_execute", side_effect=fake_success
            ):
                success_code = workflow.main([*common, "--report", str(success_report)])
            success = json.loads(success_report.read_text(encoding="utf-8"))
            self.assertEqual(success_code, 0)
            self.assertEqual(success["status"], "EXECUTED_REVIEW_REQUIRED")
            self.assertEqual(success["exit_code"], 0)

            dry_run_report = root / "dry_run.json"
            with patch.object(workflow, "_preflight", side_effect=fake_preflight):
                dry_run_code = workflow.main([*common, "--report", str(dry_run_report), "--dry-run"])
            dry_run = json.loads(dry_run_report.read_text(encoding="utf-8"))
            self.assertEqual(dry_run_code, 0)
            self.assertEqual(dry_run["status"], "PLANNED_NO_EXECUTION")
            self.assertEqual(dry_run["exit_code"], 0)

    def test_no_hand_binding_rejects_unapproved_target(self) -> None:
        """zero 目标不在 Wong 批准的 no_hand 行中时必须失败。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "image.jpg"
            label = root / "image.txt"
            image.write_bytes(b"image")
            label.write_bytes(b"")
            rows = {
                "val": {
                    workflow._canonical_path(image): {
                        "image": str(image),
                        "label": str(label),
                        "manifest_row": 2,
                        "split": "val",
                    }
                }
            }
            errors: list[str] = []
            approved = workflow._validate_no_hand_approval(
                {"no_hand_images": [{"image": "other.jpg", "split": "val", "role": "no_hand", "manifest_row": 2}]},
                rows,
                root,
                errors,
            )
            self.assertEqual(approved, {})
            self.assertTrue(any("未绑定 manifest" in error for error in errors))

    def test_detection_json_proves_zero_and_rejects_nonzero(self) -> None:
        """评估必须从 objects=[] 证明零框，非零目标不能靠进程退出码通过。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "image.jpg"
            image.write_bytes(b"image")
            output = root / "detections.json"
            errors: list[str] = []
            output.write_text(
                json.dumps([{"filename": str(image), "objects": []}]),
                encoding="utf-8",
            )
            parsed = workflow._parse_detection_output(output, [image], image, errors, root)
            self.assertTrue(parsed["zero_prediction"]["actual_zero_boxes"])
            self.assertEqual(errors, [])
            output.write_text(
                json.dumps([{"filename": str(image), "objects": [{"class_id": 0, "confidence": 0.9, "bbox": [0.5, 0.5, 0.2, 0.2]}]}]),
                encoding="utf-8",
            )
            errors = []
            parsed = workflow._parse_detection_output(output, [image], image, errors, root)
            self.assertFalse(parsed["zero_prediction"]["actual_zero_boxes"])
            self.assertTrue(any("不是零框" in error for error in errors))

    def test_detection_object_rejects_invalid_class_identity(self) -> None:
        """检测框必须使用范围内且相互一致的 class_id/name。"""

        valid_tail = {"confidence": 0.8, "bbox": [0.5, 0.5, 0.2, 0.2]}
        cases = [
            {"class_id": -1, "name": "fist"},
            {"class_id": 5, "name": "fist"},
            {"class_id": 0, "name": "unknown"},
            {"class_id": 0, "name": "palm"},
            {"class_id": True, "name": "fist"},
        ]
        for invalid in cases:
            with self.subTest(invalid=invalid):
                errors: list[str] = []
                workflow._validate_detection_object({**invalid, **valid_tail}, 1, 1, errors)
                self.assertTrue(errors)
        errors = []
        workflow._validate_detection_object({"class_id": 0, "name": "fist", **valid_tail}, 1, 1, errors)
        self.assertEqual(errors, [])

    def test_run_command_scans_completed_oom_and_corrupt_logs(self) -> None:
        """子进程立即退出时，完整日志中的 OOM/输入错误仍必须阻断。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index, message in enumerate((
                "CUDA out of memory",
                "Error opening label",
                "Cannot load image image.jpg",
                "Can't open label file image.txt",
                "Couldn't open file valid.txt",
            ), start=1):
                result = workflow._run_command(
                    [workflow.sys.executable, "-c", f"print({message!r})"],
                    root,
                    root / f"immediate_{index}.log",
                    10,
                    10,
                )
                self.assertEqual(result["stop_reason"], "日志出现 OOM 或数据损坏停止标记")

    def test_run_command_stops_on_total_timeout(self) -> None:
        """进程持续运行但无日志时必须按总超时停止。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = workflow._run_command(
                [workflow.sys.executable, "-c", "import time; time.sleep(3)"],
                root,
                root / "total_timeout.log",
                0.2,
                5,
            )
            self.assertIn("总运行时间", result["stop_reason"] or "")

    def test_run_command_stops_on_no_progress(self) -> None:
        """没有日志增长时必须按无进度超时停止。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = workflow._run_command(
                [workflow.sys.executable, "-c", "import time; time.sleep(2)"],
                root,
                root / "no_progress.log",
                5,
                0.2,
            )
            self.assertIn("无进度", result["stop_reason"] or "")

    def test_evaluate_rejects_non_finite_process_result(self) -> None:
        """evaluate 分支即使退出码为零也必须拒绝非有限日志。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "image.jpg"
            valid_list = root / "valid.txt"
            image.write_bytes(b"image")
            valid_list.write_text(str(image) + "\n", encoding="utf-8")
            args = Namespace(
                action="evaluate",
                data_config=root / "gesture.data",
                model_config=root / "gesture.cfg",
                weights=root / "weights",
                valid_list=valid_list,
                zero_prediction_image=image,
                run_dir=root / "run",
                timeout_seconds=10.0,
                no_progress_timeout_seconds=10.0,
                dry_run=False,
            )
            report = {
                "status": "BLOCKED_PREFLIGHT",
                "commands": [],
                "errors": [],
                "outputs": {
                    "evaluation_json": {"path": str(args.run_dir / "evaluation.json"), "sha256": "unavailable"}
                },
            }
            context = {
                "executable": root / "darknet.exe",
                "working_directory": root,
                "valid_images": [image],
                "evaluation_json": args.run_dir / "evaluation.json",
            }
            with patch.object(
                workflow,
                "_run_command",
                return_value={
                    "exit_code": 0,
                    "stop_reason": None,
                    "non_finite_observed": True,
                    "log_sha256": "unavailable",
                    "output": "10: loss=NaN",
                },
            ):
                workflow._execute(args, report, context)
            self.assertTrue(any("非有限" in error for error in report["errors"]))

    def test_execute_resume_protects_input_and_requires_new_checkpoint(self) -> None:
        """resume 执行后必须证明输入 SHA 不变且输出由本次运行新生成。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            training_inputs = self._make_training_inputs(root)
            backup = root / "backup"
            backup.mkdir()
            checkpoint = backup / "gesture_10.weights"
            output = backup / "gesture_20.weights"
            checkpoint.write_bytes(b"resume-input")
            before = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
            run_dir = root / "run"
            args = Namespace(
                action="resume",
                data_config=training_inputs["data_config"],
                manifest=training_inputs["manifest"],
                data_root=root,
                model_config=root / "gesture.cfg",
                checkpoint=checkpoint,
                checkpoint_output=output,
                resume_from_step=10,
                run_dir=run_dir,
                timeout_seconds=10.0,
                no_progress_timeout_seconds=10.0,
                dry_run=False,
            )
            report = {
                "status": "BLOCKED_PREFLIGHT",
                "commands": [],
                "errors": [],
                "training_input_binding": {
                    "status": "PREFLIGHT_CAPTURED",
                    "preflight": training_inputs["snapshot"],
                    "before_child": None,
                    "after_child": None,
                    "execution_status": "NOT_STARTED",
                    "scope_notice": "仅比较 preflight、before_child、after_child 各采样点；不证明 child 运行期间未发生后又恢复的修改。",
                },
                "inputs": {
                    "resume_checkpoint_sha256_before": before,
                    "checkpoint_mapping": {"cfg_stem": "gesture", "candidates": []},
                },
                "outputs": {"checkpoint_output": {"path": str(output), "sha256_before": "unavailable"}},
            }
            context = {
                "executable": root / "darknet.exe",
                "working_directory": root,
                "checkpoint_input": checkpoint,
                "checkpoint_output": output,
                "checkpoint_plan": {"cfg_stem": "gesture", "candidates": []},
                "manifest_images": training_inputs["manifest_images"],
            }

            def fake_resume(command: list[str], *_args: object, **_kwargs: object) -> dict[str, object]:
                """写入模拟的本次恢复检查点。"""

                output.write_bytes(b"new-resume-output")
                return {
                    "exit_code": 0,
                    "stop_reason": None,
                    "non_finite_observed": False,
                    "observed_update_steps": [10, 11],
                    "loss_token_observed": True,
                    "log_sha256": "simulated",
                    "output": "10: loss=1.0\n11: loss=0.9\n",
                }

            with patch.object(workflow, "_run_command", side_effect=fake_resume):
                workflow._execute(args, report, context)
            self.assertTrue(output.is_file())
            self.assertEqual(hashlib.sha256(checkpoint.read_bytes()).hexdigest(), before)
            self.assertTrue(report["checkpoint"]["input_unchanged"])
            self.assertTrue(report["checkpoint"]["output_path"].endswith("gesture_20.weights"))
            self.assertNotEqual(report["checkpoint"]["output_sha256"], before)
            self.assertTrue(report["acceptance"]["checkpoint_output_created"])
            self.assertEqual(report["errors"], [])

    def test_execute_evaluate_rejects_empty_and_malformed_detector_json(self) -> None:
        """空或畸形 detector JSON 必须写错误并保持 AC06 候选为假。"""

        for index, payload in enumerate(("", "{}"), start=1):
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                image = root / "image.jpg"
                image.write_bytes(b"image")
                valid_list = root / "valid.txt"
                valid_list.write_text(f"{image}\n", encoding="utf-8")
                run_dir = root / f"run_{index}"
                args = Namespace(
                    action="evaluate",
                    data_config=root / "gesture.data",
                    model_config=root / "gesture.cfg",
                    weights=root / "weights",
                    valid_list=root / "valid.txt",
                    zero_prediction_image=image,
                    run_dir=run_dir,
                    timeout_seconds=10.0,
                    no_progress_timeout_seconds=10.0,
                    dry_run=False,
                )
                output_path = run_dir / "detections" / "eval_000001.json"
                report = {
                    "status": "BLOCKED_PREFLIGHT",
                    "commands": [],
                    "errors": [],
                    "outputs": {"evaluation_json": {"path": str(run_dir / "evaluation.json"), "sha256": "unavailable"}},
                }
                context = {
                    "executable": root / "darknet.exe",
                    "working_directory": root,
                    "valid_images": [image],
                    "evaluation_json": run_dir / "evaluation.json",
                    "evaluation_output_paths": [output_path],
                }

                def fake_invalid_json(command: list[str], *_args: object, **_kwargs: object) -> dict[str, object]:
                    """写入指定的无效 detector JSON。"""

                    output = Path(command[command.index("-out") + 1])
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_text(payload, encoding="utf-8")
                    return {"exit_code": 0, "stop_reason": None, "non_finite_observed": False, "log_sha256": "simulated", "output": ""}

                with patch.object(workflow, "_run_command", side_effect=fake_invalid_json):
                    workflow._execute(args, report, context)
                self.assertTrue(report["errors"])
                self.assertFalse(report["acceptance"]["ac06_candidate"])
                self.assertTrue((run_dir / "evaluation.jsonl").is_file())

    def test_immediate_darknet_failure_marks_train_and_evaluate_reports_failed(self) -> None:
        """模拟立即 OOM/损坏退出，train 和 evaluate 都必须落盘为执行失败。"""

        for action in ("train", "evaluate"):
            with self.subTest(action=action), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                training_inputs = self._make_training_inputs(root) if action == "train" else None
                run_dir = root / "run"
                report_path = root / "report.json"
                image = root / "image.jpg"
                image.write_bytes(b"image")
                valid_list = root / "valid.txt"
                valid_list.write_text(str(image) + "\n", encoding="utf-8")
                common = [
                    action,
                    "--darknet-executable", str(root / "darknet.exe"),
                    "--environment-report", str(root / "environment.json"),
                    "--data-root", str(root),
                    "--manifest", str(training_inputs["manifest"] if training_inputs else root / "manifest.csv"),
                    "--dataset-report", str(root / "dataset.json"),
                    "--dataset-approval", str(root / "approval.json"),
                    "--data-config", str(training_inputs["data_config"] if training_inputs else root / "gesture.data"),
                    "--model-config", str(root / "gesture.cfg"),
                    "--names-file", str(root / "gesture.names"),
                    "--working-directory", str(root),
                    "--run-dir", str(run_dir),
                    "--report", str(report_path),
                ]
                if action == "train":
                    common.extend([
                        "--initial-weights", str(root / "initial.weights"),
                        "--checkpoint-output", str(root / "backup" / "gesture_final.weights"),
                    ])
                else:
                    common.extend([
                        "--weights", str(root / "weights"),
                        "--valid-list", str(valid_list),
                        "--zero-prediction-image", str(image),
                    ])

                def fake_preflight(args: Namespace, report: dict[str, object]) -> dict[str, object]:
                    """注入已完成预检的最小上下文，隔离测试执行失败收口。"""

                    report["inputs"] = {}
                    if args.action == "train":
                        output = args.checkpoint_output.resolve()
                        report["outputs"] = {"checkpoint_output": {"path": str(output)}}
                        self._attach_training_binding(report, training_inputs)
                        return {
                            "executable": args.darknet_executable.resolve(),
                            "working_directory": root,
                            "checkpoint_output": output,
                            "manifest_images": training_inputs["manifest_images"],
                        }
                    output = args.run_dir.resolve() / "evaluation.json"
                    image_output = args.run_dir.resolve() / "detections" / "eval_000001.json"
                    report["outputs"] = {"evaluation_json": {"path": str(output)}}
                    return {
                        "executable": args.darknet_executable.resolve(),
                        "working_directory": root,
                        "valid_images": [image],
                        "evaluation_json": output,
                        "evaluation_output_paths": [image_output],
                    }

                with patch.object(workflow, "_preflight", side_effect=fake_preflight), patch.object(
                    workflow,
                    "_run_command",
                    return_value={
                        "exit_code": 1,
                        "stop_reason": "日志出现 OOM 或数据损坏停止标记",
                        "non_finite_observed": False,
                        "log_sha256": "unavailable",
                        "output": "FULL_FAILURE_LOG_SENTINEL_" + ("y" * 10000),
                    },
                ):
                    code = workflow.main(common)
                saved = json.loads(report_path.read_text(encoding="utf-8"))
                self.assertEqual(code, 2)
                self.assertEqual(saved["status"], "EXECUTION_FAILED")
                self.assertEqual(saved["exit_code"], 2)
                self.assertEqual(len(saved["commands"]), 1)
                self.assertNotIn("output", saved["commands"][0])
                self.assertNotIn("FULL_FAILURE_LOG_SENTINEL_", report_path.read_text(encoding="utf-8"))
                self.assertTrue(saved["errors"])

    def test_evaluate_simulated_single_process_binds_ordered_records(self) -> None:
        """模拟单进程 stdin 评估，验证 frame_id 顺序绑定和逐图派生输出。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image_one = root / "zero.jpg"
            image_two = root / "gesture.jpg"
            valid_list = root / "valid.txt"
            for image in (image_one, image_two):
                image.write_bytes(b"image")
            valid_list.write_text(f"{image_one}\n{image_two}\n", encoding="utf-8")
            run_dir = root / "run"
            output_paths = [run_dir / "detections" / "eval_000001.json", run_dir / "detections" / "eval_000002.json"]
            args = Namespace(
                action="evaluate",
                data_config=root / "gesture.data",
                model_config=root / "gesture.cfg",
                weights=root / "weights",
                valid_list=valid_list,
                zero_prediction_image=image_one,
                run_dir=run_dir,
                timeout_seconds=10.0,
                no_progress_timeout_seconds=10.0,
                dry_run=False,
            )
            report = {
                "status": "BLOCKED_PREFLIGHT",
                "commands": [],
                "errors": [],
                "outputs": {"evaluation_json": {"path": str(run_dir / "evaluation.json"), "sha256": "unavailable"}},
            }
            context = {
                "executable": root / "darknet.exe",
                "working_directory": root,
                "valid_images": [image_one, image_two],
                "evaluation_json": run_dir / "evaluation.json",
                "evaluation_output_paths": output_paths,
            }

            def fake_darknet(command: list[str], *_args: object, **_kwargs: object) -> dict[str, object]:
                """写入模拟 detector test 的规范 filename 有序 JSON。"""

                output_path = Path(command[command.index("-out") + 1])
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(json.dumps([
                    {"frame_id": 1, "filename": workflow._darknet_cli_path(image_one), "objects": []},
                    {"frame_id": 2, "filename": workflow._darknet_cli_path(image_two), "objects": [{
                        "class_id": 0,
                        "name": "fist",
                        "confidence": 0.8,
                        "relative_coordinates": {"center_x": 0.5, "center_y": 0.5, "width": 0.2, "height": 0.2},
                    }]},
                ]), encoding="utf-8")
                return {
                    "exit_code": 0,
                    "stop_reason": None,
                    "non_finite_observed": False,
                    "log_sha256": "simulated-log-sha256",
                    "log_size_bytes": 9000,
                    "log": str(run_dir / "evaluate.log"),
                    "output": "FULL_EVALUATION_LOG_SENTINEL_" + ("z" * 9000),
                }

            with patch.object(workflow, "_run_command", side_effect=fake_darknet) as runner:
                workflow._execute(args, report, context)
            self.assertEqual(runner.call_count, 1)
            command = runner.call_args_list[0].args[0]
            self.assertNotIn("-ext_output", command)
            self.assertNotIn(str(image_one), command)
            self.assertNotIn(str(image_two), command)
            runtime_list = run_dir / "runtime_valid.list"
            self.assertEqual(runner.call_args_list[0].kwargs["stdin_path"], runtime_list)
            self.assertEqual(
                runtime_list.read_text(encoding="utf-8"),
                f"{workflow._darknet_cli_path(image_one)}\n{workflow._darknet_cli_path(image_two)}\n",
            )
            self.assertEqual(report["acceptance"]["completed_image_count"], 2)
            self.assertEqual(report["acceptance"]["detector_test_command_count"], 1)
            self.assertNotIn("output", report["commands"][0])
            serialized_report = json.dumps(report, ensure_ascii=False)
            self.assertNotIn("FULL_EVALUATION_LOG_SENTINEL_", serialized_report)
            self.assertEqual(report["commands"][0]["log_size_bytes"], 9000)
            self.assertEqual(report["commands"][0]["training_profile"], "not_applicable")
            self.assertEqual(report["acceptance"]["ordered_binding"], "filename_and_frame_id_ordered_valid_list")
            self.assertTrue(report["acceptance"]["zero_prediction_actual_zero_boxes"])
            self.assertTrue((run_dir / "evaluation.json").is_file())
            self.assertTrue((run_dir / "evaluation.jsonl").is_file())
            self.assertEqual(
                json.loads(output_paths[0].read_text(encoding="utf-8"))[0]["filename"],
                workflow._darknet_cli_path(image_one),
            )
            self.assertEqual(
                json.loads(output_paths[1].read_text(encoding="utf-8"))[0]["filename"],
                workflow._darknet_cli_path(image_two),
            )

    def test_ordered_detector_json_rejects_frame_id_gap(self) -> None:
        """detector JSON 出现 frame_id 跳号时必须失败。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "image.jpg"
            output = root / "evaluation.json"
            image.write_bytes(b"image")
            output.write_text(
                json.dumps([{"frame_id": 2, "filename": workflow._darknet_cli_path(image), "objects": []}]),
                encoding="utf-8",
            )
            errors: list[str] = []
            workflow._parse_detection_output(
                output,
                [image],
                image,
                errors,
                root,
                require_zero=True,
                allow_ordered_records=True,
            )
            self.assertTrue(any("frame_id" in error for error in errors))

    def test_runtime_stdin_list_normalizes_windows_paths_and_records_mapping(self) -> None:
        """runtime 清单使用正斜杠，且每行仍解析到对应 source 图片。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            images = [root / "a.jpg", root / "nested" / "b.png"]
            for image in images:
                image.parent.mkdir(parents=True, exist_ok=True)
                image.write_bytes(b"image")
            source = root / "valid.list"
            source.write_text("\n".join(str(image) for image in images) + "\n", encoding="utf-8")
            runtime = root / "run" / "runtime_valid.list"
            errors: list[str] = []
            info = workflow._prepare_runtime_stdin_list(source, runtime, images, errors)
            self.assertEqual(errors, [])
            self.assertEqual(info["line_count"], 2)
            self.assertEqual(info["source_valid_list"]["sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertTrue(info["source_to_runtime_ordered_canonical"])
            self.assertNotIn("\\", runtime.read_text(encoding="utf-8"))

    def test_runtime_stdin_list_rejects_malformed_duplicate_and_wrong_order(self) -> None:
        """runtime 清单的畸形、重复和错序必须在启动前拒绝。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first.jpg"
            second = root / "second.jpg"
            first.write_bytes(b"image")
            second.write_bytes(b"image")
            cases = {
                "malformed": "not-an-absolute-path\n",
                "duplicate": "{first}\n{first}\n",
                "wrong_order": "{second}\n{first}\n",
            }
            for name, template in cases.items():
                with self.subTest(case=name):
                    runtime = root / f"{name}.list"
                    runtime.write_text(
                        template.format(
                            first=workflow._darknet_cli_path(first),
                            second=workflow._darknet_cli_path(second),
                        ),
                        encoding="utf-8",
                    )
                    errors: list[str] = []
                    workflow._validate_runtime_stdin_list(runtime, [first, second], errors)
                    self.assertTrue(errors)

    def test_evaluate_cli_omits_filename_for_stdin_mode(self) -> None:
        """单进程 stdin 评估命令不携带 filename，避免 Darknet 写出非法 JSON 反斜杠。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = root / "image.jpg"
            image.write_bytes(b"image")
            args = Namespace(
                action="evaluate",
                data_config=root / "gesture.data",
                model_config=root / "gesture.cfg",
                weights=root / "weights",
                valid_list=root / "valid.txt",
                zero_prediction_image=image,
                run_dir=root / "run",
            )
            commands = workflow._commands_for_action(
                args,
                {
                    "executable": root / "darknet.exe",
                    "working_directory": root,
                    "valid_images": [image],
                    "evaluation_json": args.run_dir / "evaluation.json",
                },
            )
            command = commands[0]
            self.assertEqual(
                command[3:9],
                [
                    str(args.data_config.resolve()),
                    str(args.model_config.resolve()),
                    str(args.weights.resolve()),
                    "-dont_show",
                    "-out",
                    str(args.run_dir.resolve() / "evaluation.json"),
                ],
            )
            self.assertNotIn(str(image), command)
            self.assertNotIn("-ext_output", command)

    def test_malformed_preflight_schema_writes_blocked_report(self) -> None:
        """畸形环境、数据或审批 JSON 必须统一写 BLOCKED_PREFLIGHT 报告并返回 2。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_root = root / "data"
            work = root / "work"
            data_root.mkdir()
            work.mkdir()
            manifest = data_root / "manifest.csv"
            manifest.write_text(
                "image,label,split,session_id,person_id,source,license,is_real\n", encoding="utf-8"
            )
            data_cfg = work / "gesture.data"
            data_cfg.write_text("classes=5\n", encoding="utf-8")
            model_cfg = work / "gesture.cfg"
            model_cfg.write_text("[net]\nmax_batches=11\nwidth=320\nheight=320\n", encoding="utf-8")
            names = work / "gesture.names"
            names.write_text("fist\npalm\none\ntwo_up\nthree\n", encoding="utf-8")
            env = root / "environment.json"
            dataset = root / "dataset.json"
            approval = root / "approval.json"
            env.write_text('{"status":"PASS","framework":"official-darknet-cuda","checks":[]}', encoding="utf-8")
            dataset.write_text('{"status":"PASS_AUTOMATED_MANUAL_PENDING","checks":[]}', encoding="utf-8")
            approval.write_text("[]", encoding="utf-8")
            report_path = root / "blocked.json"
            code = workflow.main(
                [
                    "evaluate",
                    "--darknet-executable", str(root / "darknet.exe"),
                    "--environment-report", str(env),
                    "--data-root", str(data_root),
                    "--manifest", str(manifest),
                    "--dataset-report", str(dataset),
                    "--dataset-approval", str(approval),
                    "--data-config", str(data_cfg),
                    "--model-config", str(model_cfg),
                    "--names-file", str(names),
                    "--working-directory", str(work),
                    "--run-dir", str(root / "run"),
                    "--report", str(report_path),
                    "--weights", str(root / "weights"),
                    "--valid-list", str(work / "valid.txt"),
                    "--zero-prediction-image", str(root / "zero.jpg"),
                ]
            )
            self.assertEqual(code, 2)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "BLOCKED_PREFLIGHT")
            self.assertEqual(report["exit_code"], 2)
            self.assertTrue(report["errors"])
            self.assertFalse(any("AttributeError" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
