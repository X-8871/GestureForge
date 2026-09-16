"""S1-T01 官方 Darknet 流程入口的失败即停和命令构造回归测试。"""

from __future__ import annotations

import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
import hashlib
import json
from unittest.mock import patch

try:
    import verification.s1_t01_darknet_workflow as workflow
except ModuleNotFoundError:
    import s1_t01_darknet_workflow as workflow


class DarknetWorkflowTest(unittest.TestCase):
    """验证短训边界、审批门槛和官方命令格式。"""

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
            self.assertIn("424242", result["output"])
            self.assertEqual(result["seed_binding"]["environment_variable"], workflow.DARKNET_SEED_ENV)
            self.assertEqual(result["seed_binding"]["value"], 424242)
            self.assertTrue(result["seed_binding"]["parent_process_unchanged"])

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
            config.write_text(
                "[net]\nmax_batches=4000\nwidth=320\nheight=320\n[yolo]\nclasses=5\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            workflow._validate_model_config(config, errors)
            self.assertTrue(any("max_batches" in error for error in errors))

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
        expected = "读取 valid 清单生成隔离 runtime stdin 清单，单进程执行官方 Darknet detector test -out JSON 并逐图解析"
        self.assertIn(expected, help_text)
        self.assertNotIn("带显式 filename", help_text)

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
            self.assertIn("gesture_10.weights", plan["candidate_names"])
            self.assertIn("gesture_20.weights", plan["candidate_names"])
            self.assertIn("gesture_last.weights", plan["candidate_names"])
            self.assertIn("gesture_final.weights", plan["candidate_names"])
            self.assertIsNotNone(workflow._checkpoint_name_kind(Path("gesture_last.weights"), "gesture"))
            self.assertIsNone(workflow._checkpoint_name_kind(Path("other_10.weights"), "gesture"))
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
            numbered = backup / "gesture_10.weights"
            numbered.write_bytes(b"input")
            errors: list[str] = []
            workflow._validate_checkpoint_io(
                "resume", numbered, backup / "gesture_final.weights", plan, "gesture", 10, errors
            )
            self.assertEqual(errors, [])
            for suffix in ("last", "final"):
                errors = []
                workflow._validate_checkpoint_io(
                    "resume", backup / f"gesture_{suffix}.weights", backup / "gesture_20.weights", plan, "gesture", 10, errors
                )
                self.assertTrue(any("只允许同一 cfg 基名的 numbered" in error for error in errors))

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
            checkpoint_output = root / "backup" / "gesture_10.weights"
            context = {
                "executable": root / "darknet.exe",
                "working_directory": root,
                "valid_images": [],
                "checkpoint_output": checkpoint_output,
                "checkpoint_plan": {"candidates": []},
            }
            common = [
                "train",
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
                "--initial-weights", str(root / "initial.weights"),
                "--checkpoint-output", str(checkpoint_output),
            ]

            def fake_success(args: Namespace, report: dict[str, object], value: dict[str, object]) -> None:
                """注入成功动作结果，验证 main 的报告收口。"""

                report["status"] = "EXECUTED_REVIEW_REQUIRED"

            success_report = root / "success.json"
            with patch.object(workflow, "_preflight", return_value=context), patch.object(
                workflow, "_execute", side_effect=fake_success
            ):
                success_code = workflow.main([*common, "--report", str(success_report)])
            success = json.loads(success_report.read_text(encoding="utf-8"))
            self.assertEqual(success_code, 0)
            self.assertEqual(success["status"], "EXECUTED_REVIEW_REQUIRED")
            self.assertEqual(success["exit_code"], 0)

            dry_run_report = root / "dry_run.json"
            with patch.object(workflow, "_preflight", return_value=context):
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
            backup = root / "backup"
            backup.mkdir()
            checkpoint = backup / "gesture_10.weights"
            output = backup / "gesture_20.weights"
            checkpoint.write_bytes(b"resume-input")
            before = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
            run_dir = root / "run"
            args = Namespace(
                action="resume",
                data_config=root / "gesture.data",
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
                    "--manifest", str(root / "manifest.csv"),
                    "--dataset-report", str(root / "dataset.json"),
                    "--dataset-approval", str(root / "approval.json"),
                    "--data-config", str(root / "gesture.data"),
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
                        return {"executable": args.darknet_executable.resolve(), "working_directory": root, "checkpoint_output": output}
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
                        "output": "CUDA out of memory",
                    },
                ):
                    code = workflow.main(common)
                saved = json.loads(report_path.read_text(encoding="utf-8"))
                self.assertEqual(code, 2)
                self.assertEqual(saved["status"], "EXECUTION_FAILED")
                self.assertEqual(saved["exit_code"], 2)
                self.assertEqual(len(saved["commands"]), 1)
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
                return {"exit_code": 0, "stop_reason": None, "non_finite_observed": False, "log_sha256": "unavailable", "output": ""}

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
