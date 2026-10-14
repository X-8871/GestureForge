"""阶段交付清单检查器的隔离单元测试。"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from verification import check_stage_delivery as checker


PROJECT_ROOT = Path(__file__).absolute().parent.parent
CHECKER_PATH = PROJECT_ROOT / "verification" / "check_stage_delivery.py"
PLACEHOLDER_VARIANTS = (
    "TBD",
    "TODO",
    "PENDING",
    "unfrozen",
    "Not Frozen",
    "placeholder",
    "unknown",
    "none",
    "null",
    "Not Applicable",
    "NOT APPLICABLE",
    "not_applicable",
    "not-applicable",
    "Not Applicable.",
    "N/A",
    "N.A.",
    "NA",
    "不适用",
    "不适用。",
    "待填写",
    "待补",
    "待冻结",
    "待确认",
    "待确认。",
    "待定",
    "待定。",
    "未冻结",
    "未填写",
    "占位",
    "runid",
    "s2b-txx",
    "TBD。",
    "---",
    "...",
    "<unresolved>",
    "xxx",
)


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class StageDeliveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="stage-delivery-test-")
        self.root = Path(self.temporary.name)
        subprocess.run(["git", "init", "--quiet"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "config", "user.name", "Stage Delivery Test"],
            cwd=self.root,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "stage-delivery-test@example.invalid"],
            cwd=self.root,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "--quiet", "--allow-empty", "-m", "fixture"],
            cwd=self.root,
            check=True,
        )
        self.commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout.strip()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_bytes(self, relative: str, content: bytes) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def write_json(self, relative: str, data: dict) -> Path:
        return self.write_bytes(
            relative,
            json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
        )

    def input_manifest(self) -> dict:
        interface = b"# Formal input contract\n"
        input_data = b"golden input fixture\n"
        self.write_bytes("docs/formal/input_contract.md", interface)
        self.write_bytes("fixtures/input.bin", input_data)
        return {
            "schema_version": 1,
            "stage": "2B",
            "task_id": "S2B-T01",
            "run_id": "input-check-01",
            "source_commit": self.commit,
            "evidence_dir": "report/evidence/S2B-T01/input-check-01",
            "interfaces": [
                {
                    "name": "formal input contract",
                    "version": "2026-10-01",
                    "frozen": True,
                    "path": "docs/formal/input_contract.md",
                    "sha256": digest(interface),
                }
            ],
            "files": [
                {
                    "path": "fixtures/input.bin",
                    "sha256": digest(input_data),
                    "role": "input",
                }
            ],
            "checks": [
                {
                    "name": "input dependency",
                    "status": "PASS",
                    "command": "python validate_input.py",
                    "exit_code": 0,
                }
            ],
            "limitations": [],
        }

    def evidence_manifest(self) -> tuple[dict, Path]:
        task_id = "S2B-T02"
        run_id = "run-01"
        run_relative = f"report/evidence/{task_id}/{run_id}"
        run_dir = self.root / run_relative
        source_data = b"source snapshot\n"
        result_data = b"result record\n"
        log_data = b"tool output\n"
        self.write_bytes("src/kernel.py", source_data)
        self.write_bytes(f"{run_relative}/result.json", result_data)
        self.write_bytes(f"{run_relative}/run.log", log_data)
        interface_data = b"# Frozen interface record\n"
        self.write_bytes("docs/formal/output_contract.md", interface_data)
        data = {
            "schema_version": 1,
            "stage": "2B",
            "task_id": task_id,
            "run_id": run_id,
            "source_commit": self.commit,
            "evidence_dir": run_relative,
            "interfaces": [
                {
                    "name": "output contract",
                    "version": "v1",
                    "frozen": True,
                    "path": "docs/formal/output_contract.md",
                    "sha256": digest(interface_data),
                }
            ],
            "files": [
                {"path": "src/kernel.py", "sha256": digest(source_data), "role": "source"},
                {
                    "path": f"{run_relative}/result.json",
                    "sha256": digest(result_data),
                    "role": "result",
                },
                {
                    "path": f"{run_relative}/run.log",
                    "sha256": digest(log_data),
                    "role": "log",
                },
            ],
            "checks": [
                {
                    "name": "simulation",
                    "status": "PASS",
                    "command": "python run_sim.py",
                    "exit_code": 0,
                }
            ],
            "limitations": [],
            "tool_versions": {"Python": "3.12.10"},
        }
        manifest_path = self.write_json(f"{run_relative}/delivery_manifest.json", data)
        return data, manifest_path

    def run_direct(self, mode: str, data: dict, relative: str = "manifest.json") -> dict:
        manifest_path = self.write_json(relative, data)
        return checker.check_manifest(mode, str(manifest_path), str(self.root))

    def run_cli(
        self,
        mode: str,
        manifest_path: Path,
        project_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        command = [
            sys.executable,
            "-B",
            str(CHECKER_PATH),
            "--mode",
            mode,
            "--manifest",
            str(manifest_path),
        ]
        if project_root is not None:
            command.extend(["--project-root", str(project_root)])
        return subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test正常_inputs_通过(self) -> None:
        result = self.run_direct("inputs", self.input_manifest())
        self.assertEqual("CHECKS_OK", result["status"], result["errors"])
        self.assertEqual("PASS", result["check_statuses"][0]["status"])

    def test_inputs_显式接口不适用仍需真实输入且通过(self) -> None:
        data = self.input_manifest()
        data["interfaces"] = []
        data["interfaces_not_applicable_reason"] = "本任务无适用上游接口，待正式G0确认"
        result = self.run_direct("inputs", data)
        self.assertEqual("CHECKS_OK", result["status"], result["errors"])
        self.assertEqual("NOT_APPLICABLE", result["interfaces_not_applicable"]["status"])
        self.assertEqual(
            data["interfaces_not_applicable_reason"],
            result["interfaces_not_applicable"]["reason"],
        )
        self.assertEqual(
            "其适用性仍须正式G0/Reviewer确认",
            result["interfaces_not_applicable"]["review_note"],
        )
        self.assertEqual("input", data["files"][0]["role"])

    def test_evidence_显式接口不适用声明通过(self) -> None:
        data, manifest_path = self.evidence_manifest()
        data["interfaces"] = []
        data["interfaces_not_applicable_reason"] = "本次独立验证无适用上游接口，待正式G0确认"
        self.write_json(manifest_path.relative_to(self.root).as_posix(), data)
        result = checker.check_manifest("evidence", str(manifest_path), str(self.root))
        self.assertEqual("CHECKS_OK", result["status"], result["errors"])
        self.assertEqual("NOT_APPLICABLE", result["interfaces_not_applicable"]["status"])
        self.assertEqual(
            "其适用性仍须正式G0/Reviewer确认",
            result["interfaces_not_applicable"]["review_note"],
        )

    def test接口不适用理由缺失空白占位或类型错误拒绝(self) -> None:
        missing = object()
        for reason in (missing, "", "   ", "TBD", "待确认", None, 7):
            with self.subTest(reason=reason):
                data = self.input_manifest()
                data["interfaces"] = []
                if reason is missing:
                    data.pop("interfaces_not_applicable_reason", None)
                else:
                    data["interfaces_not_applicable_reason"] = reason
                result = self.run_direct("inputs", data)
                self.assertEqual("CHECKS_FAILED", result["status"])
                self.assertTrue(
                    any("interfaces_not_applicable_reason" in error for error in result["errors"])
                )

    def test接口不适用理由拒绝大小写分隔符标点及中文占位(self) -> None:
        for reason in PLACEHOLDER_VARIANTS:
            with self.subTest(reason=reason):
                data = self.input_manifest()
                data["interfaces"] = []
                data["interfaces_not_applicable_reason"] = reason
                result = self.run_direct("inputs", data)
                self.assertEqual("CHECKS_FAILED", result["status"])
                self.assertTrue(
                    any("interfaces_not_applicable_reason" in error for error in result["errors"])
                )
                self.assertEqual(reason, data["interfaces_not_applicable_reason"])

    def test接口不适用理由接受具体中英文原因(self) -> None:
        reasons = (
            "本任务只检查本机脚本，不消费上游模型或硬件接口",
            "This task checks only local scripts and consumes no upstream model or hardware interface.",
        )
        for reason in reasons:
            with self.subTest(reason=reason):
                data = self.input_manifest()
                data["interfaces"] = []
                data["interfaces_not_applicable_reason"] = reason
                result = self.run_direct("inputs", data)
                self.assertEqual("CHECKS_OK", result["status"], result["errors"])

    def test_PASS与FAIL命令拒绝纯占位值(self) -> None:
        for command in PLACEHOLDER_VARIANTS:
            with self.subTest(status="PASS", command=command):
                data = self.input_manifest()
                data["checks"][0]["command"] = command
                result = self.run_direct("inputs", data)
                self.assertEqual("CHECKS_FAILED", result["status"])
                self.assertTrue(any(".command" in error for error in result["errors"]))

        data, manifest_path = self.evidence_manifest()
        data["checks"][0] = {
            "name": "simulation",
            "status": "FAIL",
            "command": "TBD",
            "exit_code": 7,
            "reason": "fixture reports a real simulation failure",
        }
        self.write_json(manifest_path.relative_to(self.root).as_posix(), data)
        result = checker.check_manifest("evidence", str(manifest_path), str(self.root))
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any(".command" in error for error in result["errors"]))

    def testlimitations拒绝纯占位并接受具体说明及空数组(self) -> None:
        for limitation in PLACEHOLDER_VARIANTS:
            with self.subTest(limitation=limitation):
                data = self.input_manifest()
                data["limitations"] = [limitation]
                result = self.run_direct("inputs", data)
                self.assertEqual("CHECKS_FAILED", result["status"])
                self.assertTrue(any("limitations[0]" in error for error in result["errors"]))

        data = self.input_manifest()
        data["checks"][0]["command"] = "python validate_input.py --label TBD"
        data["limitations"] = [
            "Vivado was NOT_RUN because this check consumes only an offline input fixture."
        ]
        result = self.run_direct("inputs", data)
        self.assertEqual("CHECKS_OK", result["status"], result["errors"])

        data["limitations"] = []
        result = self.run_direct("inputs", data)
        self.assertEqual("CHECKS_OK", result["status"], result["errors"])

        for status in ("BLOCKED", "NOT_RUN", "NOT_APPLICABLE"):
            with self.subTest(status=status, command=None):
                data, manifest_path = self.evidence_manifest()
                data["checks"][0] = {
                    "name": "optional check",
                    "status": status,
                    "command": None,
                    "exit_code": None,
                    "reason": f"This check is {status} in the fixture.",
                }
                self.write_json(manifest_path.relative_to(self.root).as_posix(), data)
                result = checker.check_manifest("evidence", str(manifest_path), str(self.root))
                self.assertEqual("CHECKS_OK", result["status"], result["errors"])

    def testReviewer_Not_Applicable_CLI反例必须非零(self) -> None:
        data = self.input_manifest()
        data["interfaces"] = []
        data["interfaces_not_applicable_reason"] = "Not Applicable"
        manifest = self.write_json("manifest.json", data)
        completed = self.run_cli("inputs", manifest, self.root)
        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("", completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(
            any("interfaces_not_applicable_reason" in error for error in result["errors"])
        )

    def testevidence接口不适用不能使用占位理由(self) -> None:
        data, manifest_path = self.evidence_manifest()
        data["interfaces"] = []
        data["interfaces_not_applicable_reason"] = "Not Applicable"
        self.write_json(manifest_path.relative_to(self.root).as_posix(), data)
        result = checker.check_manifest("evidence", str(manifest_path), str(self.root))
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(
            any("interfaces_not_applicable_reason" in error for error in result["errors"])
        )

    def test非空接口不能用不适用理由绕过冻结核验(self) -> None:
        for frozen in (False, True):
            with self.subTest(frozen=frozen):
                data = self.input_manifest()
                data["interfaces_not_applicable_reason"] = "无适用接口"
                data["interfaces"][0]["frozen"] = frozen
                result = self.run_direct("inputs", data)
                self.assertEqual("CHECKS_FAILED", result["status"])
                self.assertTrue(
                    any("interfaces 非空时" in error for error in result["errors"])
                )
                if not frozen:
                    self.assertTrue(any("未冻结" in error for error in result["errors"]))

    def test正常_evidence_完整枚举通过(self) -> None:
        _, manifest_path = self.evidence_manifest()
        result = checker.check_manifest("evidence", str(manifest_path), str(self.root))
        self.assertEqual("CHECKS_OK", result["status"], result["errors"])
        self.assertEqual({"PASS"}, {item["status"] for item in result["check_statuses"]})

    def test有效_FAIL_证据包保留失败状态但包装核验通过(self) -> None:
        data, manifest_path = self.evidence_manifest()
        data["checks"] = [
            {
                "name": "simulation",
                "status": "FAIL",
                "command": "python run_sim.py",
                "exit_code": 7,
                "reason": "fixture reports a real simulation failure",
            }
        ]
        self.write_json(manifest_path.relative_to(self.root).as_posix(), data)
        result = checker.check_manifest("evidence", str(manifest_path), str(self.root))
        self.assertEqual("CHECKS_OK", result["status"], result["errors"])
        self.assertEqual("FAIL", result["check_statuses"][0]["status"])
        self.assertIn("real simulation failure", result["check_statuses"][0]["reason"])

    def test_inputs_未冻结接口阻断(self) -> None:
        data = self.input_manifest()
        data["interfaces"][0]["frozen"] = False
        result = self.run_direct("inputs", data)
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("未冻结" in error for error in result["errors"]))

    def test占位版本拒绝(self) -> None:
        for version in ("TBD", "PENDING", "待冻结"):
            with self.subTest(version=version):
                data = self.input_manifest()
                data["interfaces"][0]["version"] = version
                result = self.run_direct("inputs", data)
                self.assertEqual("CHECKS_FAILED", result["status"])
                self.assertTrue(any("占位" in error for error in result["errors"]))

    def test接口frozen类型必须为布尔(self) -> None:
        data = self.input_manifest()
        data["interfaces"][0]["frozen"] = "true"
        result = self.run_direct("inputs", data)
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("frozen 必须是布尔值" in error for error in result["errors"]))

    def test缺失输入文件拒绝(self) -> None:
        data = self.input_manifest()
        (self.root / "fixtures/input.bin").unlink()
        result = self.run_direct("inputs", data)
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("不存在" in error or "不可访问" in error for error in result["errors"]))

    def test输入文件哈希错误拒绝(self) -> None:
        data = self.input_manifest()
        data["files"][0]["sha256"] = "0" * 64
        result = self.run_direct("inputs", data)
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("SHA-256 不匹配" in error for error in result["errors"]))

    def test未知_commit_SHA_拒绝(self) -> None:
        data = self.input_manifest()
        data["source_commit"] = "0" * 40
        result = self.run_direct("inputs", data)
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("Git commit 对象" in error for error in result["errors"]))

    def test_git_blob_SHA_不能伪装_commit(self) -> None:
        data = self.input_manifest()
        blob = subprocess.run(
            ["git", "hash-object", "-w", "--stdin"],
            cwd=self.root,
            input=b"not a commit",
            capture_output=True,
            check=True,
        ).stdout.decode("ascii").strip()
        data["source_commit"] = blob
        result = self.run_direct("inputs", data)
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("commit 对象" in error for error in result["errors"]))

    def test_PASS_与非零退出码矛盾拒绝(self) -> None:
        data = self.input_manifest()
        data["checks"][0]["exit_code"] = 1
        result = self.run_direct("inputs", data)
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("PASS 时" in error for error in result["errors"]))

    def test_FAIL_与零退出码矛盾拒绝(self) -> None:
        data, manifest_path = self.evidence_manifest()
        data["checks"][0] = {
            "name": "simulation",
            "status": "FAIL",
            "command": "python run_sim.py",
            "exit_code": 0,
            "reason": "claimed failure",
        }
        self.write_json(manifest_path.relative_to(self.root).as_posix(), data)
        result = checker.check_manifest("evidence", str(manifest_path), str(self.root))
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("真实非零" in error for error in result["errors"]))

    def test_NOT_APPLICABLE_缺理由拒绝(self) -> None:
        data = self.input_manifest()
        data["checks"][0] = {
            "name": "dependency",
            "status": "NOT_APPLICABLE",
            "command": None,
            "exit_code": None,
        }
        result = self.run_direct("inputs", data)
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("必须说明原因" in error for error in result["errors"]))

    def test布尔值不能作为_exit_code(self) -> None:
        data = self.input_manifest()
        data["checks"][0]["exit_code"] = True
        result = self.run_direct("inputs", data)
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("布尔值不算整数" in error for error in result["errors"]))

    def test_inputs依赖_FAIL_BLOCKED_NOT_RUN_均阻断(self) -> None:
        for status in ("FAIL", "BLOCKED", "NOT_RUN"):
            with self.subTest(status=status):
                data = self.input_manifest()
                data["checks"][0] = {
                    "name": "dependency",
                    "status": status,
                    "command": "python dependency_check.py" if status == "FAIL" else None,
                    "exit_code": 3 if status == "FAIL" else None,
                    "reason": f"dependency is {status}",
                }
                result = self.run_direct("inputs", data)
                self.assertEqual("CHECKS_FAILED", result["status"])
                self.assertTrue(any("阻断 inputs" in error for error in result["errors"]))

    def test合理的_NOT_APPLICABLE_及理由可接受(self) -> None:
        data = self.input_manifest()
        data["checks"][0] = {
            "name": "optional dependency",
            "status": "NOT_APPLICABLE",
            "command": None,
            "exit_code": None,
            "reason": "本任务没有该上游依赖",
        }
        result = self.run_direct("inputs", data)
        self.assertEqual("CHECKS_OK", result["status"], result["errors"])

    def test_NOT_APPLICABLE_check_reason同样拒绝占位但接受具体原因(self) -> None:
        for reason in ("NOT APPLICABLE", "not_applicable", "不适用。", "待确认。", "TBD。"):
            with self.subTest(reason=reason):
                data = self.input_manifest()
                data["checks"][0] = {
                    "name": "optional dependency",
                    "status": "NOT_APPLICABLE",
                    "command": None,
                    "exit_code": None,
                    "reason": reason,
                }
                result = self.run_direct("inputs", data)
                self.assertEqual("CHECKS_FAILED", result["status"])
                self.assertTrue(any(".reason" in error for error in result["errors"]))
        for reason in (
            "本任务没有该上游依赖",
            "This task has no applicable upstream dependency.",
        ):
            with self.subTest(reason=reason):
                data = self.input_manifest()
                data["checks"][0] = {
                    "name": "optional dependency",
                    "status": "NOT_APPLICABLE",
                    "command": None,
                    "exit_code": None,
                    "reason": reason,
                }
                result = self.run_direct("inputs", data)
                self.assertEqual("CHECKS_OK", result["status"], result["errors"])

    def test非法_JSON常量拒绝(self) -> None:
        manifest = self.root / "manifest.json"
        manifest.write_text('{"value":NaN}', encoding="utf-8")
        result = checker.check_manifest("inputs", str(manifest), str(self.root))
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("非法常量" in error for error in result["errors"]))

    def test重复_JSON键拒绝(self) -> None:
        manifest = self.root / "manifest.json"
        manifest.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
        result = checker.check_manifest("inputs", str(manifest), str(self.root))
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("重复键" in error for error in result["errors"]))

    def test非法_JSON语法拒绝(self) -> None:
        manifest = self.root / "manifest.json"
        manifest.write_text("{broken", encoding="utf-8")
        result = checker.check_manifest("inputs", str(manifest), str(self.root))
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("解析失败" in error for error in result["errors"]))

    def test错误顶层类型和布尔_schema_version拒绝(self) -> None:
        result = self.run_direct("inputs", [])
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("顶层必须是对象" in error for error in result["errors"]))
        data = self.input_manifest()
        data["schema_version"] = True
        result = self.run_direct("inputs", data)
        self.assertTrue(any("schema_version 必须是整数" in error for error in result["errors"]))

    def test未知字段拒绝(self) -> None:
        data = self.input_manifest()
        data["tensor_shape"] = [1, 2, 3]
        result = self.run_direct("inputs", data)
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("未知字段" in error for error in result["errors"]))

    def test相对路径越界拒绝(self) -> None:
        data = self.input_manifest()
        data["files"][0]["path"] = "../outside.bin"
        result = self.run_direct("inputs", data)
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("不得包含 . 或 .." in error for error in result["errors"]))

    def test绝对路径越出仓库拒绝(self) -> None:
        data = self.input_manifest()
        data["files"][0]["path"] = str(self.root.parent / "outside.bin")
        result = self.run_direct("inputs", data)
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("越出 project-root" in error for error in result["errors"]))

    def testproject_root拒绝点路径分量(self) -> None:
        data = self.input_manifest()
        manifest = self.write_json("manifest.json", data)
        result = checker.check_manifest("inputs", str(manifest), str(self.root / "." / ".."))
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("project-root" in error for error in result["errors"]))

    def test仓库内绝对路径可核验(self) -> None:
        data = self.input_manifest()
        data["files"][0]["path"] = str(self.root / "fixtures/input.bin")
        result = self.run_direct("inputs", data)
        self.assertEqual("CHECKS_OK", result["status"], result["errors"])

    def test项目根父目录拒绝枚举时使用规范路径并保留大小写检查(self) -> None:
        data = self.input_manifest()
        manifest = self.write_json("manifest.json", data)
        linked_bytes = b"linked input\n"
        self.write_bytes("input_alias/sample.bin", linked_bytes)
        reparse_data = self.input_manifest()
        reparse_data["files"][0] = {
            "path": "input_alias/sample.bin",
            "sha256": digest(linked_bytes),
            "role": "input",
        }
        reparse_manifest = self.write_json("reparse_manifest.json", reparse_data)
        real_scandir = checker.os.scandir
        blocked_root = os.path.normcase(os.path.abspath(os.fspath(Path(self.root.anchor))))
        blocked_root_calls: list[str] = []

        def restricted_scandir(path: str | os.PathLike[str]):
            path_key = os.path.normcase(os.path.abspath(os.fspath(path)))
            if path_key == blocked_root:
                blocked_root_calls.append(os.fspath(path))
                raise PermissionError(5, "enumeration denied", os.fspath(path))
            return real_scandir(path)

        link_key = os.path.normcase(os.path.abspath(os.fspath(self.root / "input_alias")))
        real_lstat = checker.os.lstat

        def reparse_lstat(path: str | os.PathLike[str]) -> os.stat_result:
            info = real_lstat(path)
            if os.path.normcase(os.path.abspath(os.fspath(path))) == link_key:
                return type(
                    "ReparseStat",
                    (),
                    {"st_mode": info.st_mode, "st_file_attributes": 0x400},
                )()
            return info

        missing_root = self.root / "missing_project_root"
        ordinary_file_root = self.root / "fixtures" / "input.bin"
        wrong_case_root = self.root.with_name(self.root.name.swapcase())
        with (
            patch.object(checker.os, "scandir", side_effect=restricted_scandir),
            patch.object(checker.os, "lstat", side_effect=reparse_lstat),
        ):
            accessible = checker.check_manifest("inputs", str(manifest), str(self.root))
            wrong_case = checker.check_manifest("inputs", str(manifest), str(wrong_case_root))
            reparse = checker.check_manifest("inputs", str(reparse_manifest), str(self.root))
            missing = checker.check_manifest("inputs", str(manifest), str(missing_root))
            ordinary_file = checker.check_manifest("inputs", str(manifest), str(ordinary_file_root))

        self.assertEqual("CHECKS_OK", accessible["status"], accessible["errors"])
        self.assertEqual("CHECKS_FAILED", wrong_case["status"])
        self.assertTrue(
            any("大小写不精确" in error for error in wrong_case["errors"]),
            wrong_case["errors"],
        )
        self.assertEqual("CHECKS_FAILED", reparse["status"])
        self.assertTrue(
            any("符号链接或 reparse 点" in error for error in reparse["errors"]),
            reparse["errors"],
        )
        self.assertEqual("CHECKS_FAILED", missing["status"])
        self.assertTrue(any("路径不可访问" in error for error in missing["errors"]), missing["errors"])
        self.assertEqual("CHECKS_FAILED", ordinary_file["status"])
        self.assertTrue(any("不是目录" in error for error in ordinary_file["errors"]), ordinary_file["errors"])
        self.assertGreaterEqual(len(blocked_root_calls), 5, blocked_root_calls)

    def test父路径reparse点拒绝(self) -> None:
        data = self.input_manifest()
        link = self.root / "input_alias"
        link.mkdir()
        (link / "sample.bin").write_bytes(b"linked input\n")
        data["files"][0] = {
            "path": "input_alias/sample.bin",
            "sha256": digest(b"linked input\n"),
            "role": "input",
        }
        link_key = os.path.normcase(os.path.abspath(os.fspath(link)))
        real_lstat = os.lstat

        def reparse_lstat(path: str | os.PathLike[str]) -> os.stat_result:
            info = real_lstat(path)
            if os.path.normcase(os.path.abspath(os.fspath(path))) == link_key:
                return type(
                    "ReparseStat",
                    (),
                    {"st_mode": info.st_mode, "st_file_attributes": 0x400},
                )()
            return info

        manifest = self.write_json("manifest.json", data)
        with patch.object(checker.os, "lstat", side_effect=reparse_lstat):
            result = checker.check_manifest("inputs", str(manifest), str(self.root))
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("符号链接或 reparse 点" in error for error in result["errors"]))

    def test清单路径reparse点拒绝(self) -> None:
        data = self.input_manifest()
        manifest = self.write_json("linked_manifest.json", data)
        manifest_key = os.path.normcase(os.path.abspath(os.fspath(manifest)))
        real_lstat = os.lstat

        def reparse_lstat(path: str | os.PathLike[str]) -> os.stat_result:
            info = real_lstat(path)
            if os.path.normcase(os.path.abspath(os.fspath(path))) == manifest_key:
                return type(
                    "ReparseStat",
                    (),
                    {"st_mode": info.st_mode, "st_file_attributes": 0x400},
                )()
            return info

        with patch.object(checker.os, "lstat", side_effect=reparse_lstat):
            result = checker.check_manifest("inputs", str(manifest), str(self.root))
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("符号链接或 reparse 点" in error for error in result["errors"]))

    def testreparse属性被识别(self) -> None:
        from types import SimpleNamespace

        info = SimpleNamespace(st_mode=stat.S_IFREG, st_file_attributes=0x400)
        self.assertTrue(checker.is_reparse_or_symlink(info))

    def test编译缓存扩展名拒绝(self) -> None:
        data = self.input_manifest()
        cache = b"object cache"
        self.write_bytes("fixtures/kernel.o", cache)
        data["files"].append(
            {"path": "fixtures/kernel.o", "sha256": digest(cache), "role": "source"}
        )
        result = self.run_direct("inputs", data)
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("编译缓存" in error for error in result["errors"]))

    def testevidence内生成工程目录拒绝(self) -> None:
        _, manifest_path = self.evidence_manifest()
        cache_dir = manifest_path.parent / "obj_dir"
        cache_dir.mkdir()
        (cache_dir / "model.o").write_bytes(b"cache")
        result = checker.check_manifest("evidence", str(manifest_path), str(self.root))
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("生成缓存/工程目录" in error for error in result["errors"]))

    def test诊断波形必须逐项填写保留理由(self) -> None:
        data, manifest_path = self.evidence_manifest()
        for relative in (
            "report/evidence/S2B-T02/run-01/wave.vcd",
            "report/evidence/S2B-T02/run-01/wave.vcd.gz",
        ):
            waveform = b"waveform evidence"
            self.write_bytes(relative, waveform)
            data["files"].append(
                {"path": relative, "sha256": digest(waveform), "role": "diagnostic"}
            )
        self.write_json(manifest_path.relative_to(self.root).as_posix(), data)
        result = checker.check_manifest("evidence", str(manifest_path), str(self.root))
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("必须填写 keep_reason" in error for error in result["errors"]))
        for item in data["files"][-2:]:
            item["keep_reason"] = "保留用于定位波形时序异常"
        self.write_json(manifest_path.relative_to(self.root).as_posix(), data)
        result = checker.check_manifest("evidence", str(manifest_path), str(self.root))
        self.assertEqual("CHECKS_OK", result["status"], result["errors"])

    def test运行目录漏列文件拒绝(self) -> None:
        _, manifest_path = self.evidence_manifest()
        (manifest_path.parent / "extra.txt").write_text("unlisted", encoding="utf-8")
        result = checker.check_manifest("evidence", str(manifest_path), str(self.root))
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("未列入 files" in error for error in result["errors"]))

    def test运行目录以外的归档不会被扫描(self) -> None:
        _, manifest_path = self.evidence_manifest()
        archive_cache = self.root / "report/archive/old_run/build"
        archive_cache.mkdir(parents=True)
        (archive_cache / "old.o").write_bytes(b"historical cache")
        result = checker.check_manifest("evidence", str(manifest_path), str(self.root))
        self.assertEqual("CHECKS_OK", result["status"], result["errors"])

    def test文件枚举预算包含上限且超一项失败(self) -> None:
        data, manifest_path = self.evidence_manifest()
        run_dir = manifest_path.parent
        self.assertEqual(
            3,
            sum(1 for path in run_dir.iterdir() if path.is_file()),
            "fixture 应含 result、log 和实际写入的 manifest 三个普通文件",
        )
        with patch.object(checker, "MAX_EVIDENCE_FILES", 3):
            result = checker.check_manifest("evidence", str(manifest_path), str(self.root))
        self.assertEqual("CHECKS_OK", result["status"], result["errors"])

        extra_relative = "report/evidence/S2B-T02/run-01/extra_artifact.bin"
        extra_data = b"declared artifact beyond enumeration budget"
        self.write_bytes(extra_relative, extra_data)
        data["files"].append(
            {"path": extra_relative, "sha256": digest(extra_data), "role": "artifact"}
        )
        self.write_json(manifest_path.relative_to(self.root).as_posix(), data)
        self.assertEqual(
            4,
            sum(1 for path in run_dir.iterdir() if path.is_file()),
            "新增且已声明的 artifact 应使普通文件总数恰好多一项",
        )
        with patch.object(checker, "MAX_EVIDENCE_FILES", 3):
            result = checker.check_manifest("evidence", str(manifest_path), str(self.root))
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertEqual(1, len(result["errors"]), result["errors"])
        self.assertTrue(
            any("枚举超过上限" in error and "未完成" in error for error in result["errors"]),
            result["errors"],
        )

    def test_streaming_scan_stops_at_first_over_budget_file_and_closes_handle(self) -> None:
        data, manifest_path = self.evidence_manifest()
        run_dir = manifest_path.parent
        run_relative = data["evidence_dir"]
        for index in range(4):
            relative = f"{run_relative}/extra_{index}.bin"
            content = f"declared artifact {index}".encode("utf-8")
            self.write_bytes(relative, content)
            data["files"].append(
                {"path": relative, "sha256": digest(content), "role": "artifact"}
            )
        self.write_json(manifest_path.relative_to(self.root).as_posix(), data)

        manifest_relative = manifest_path.relative_to(self.root).as_posix()
        run_files = {
            path.relative_to(self.root).as_posix()
            for path in run_dir.iterdir()
            if path.is_file()
        }
        declared_run_files = {
            item["path"] for item in data["files"] if item["path"].startswith(run_relative + "/")
        }
        self.assertEqual(7, len(run_files), "测试目录应有七个普通文件，含 manifest")
        self.assertEqual(run_files - {manifest_relative}, declared_run_files)
        valid_manifest = checker.check_manifest("evidence", str(manifest_path), str(self.root))
        self.assertEqual("CHECKS_OK", valid_manifest["status"], valid_manifest["errors"])

        real_scandir = checker.os.scandir
        target_key = os.path.normcase(os.path.abspath(os.fspath(run_dir)))
        trackers = []

        class ScandirTracker:
            def __init__(self, path: str | os.PathLike[str]) -> None:
                self._context = real_scandir(path)
                self._iterator = None
                self.next_calls = 0
                self.entries_yielded = 0
                self.context_exited = False
                self.handle_closed = False

            def __enter__(self):
                self._iterator = self._context.__enter__()
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                self.context_exited = True
                try:
                    return self._context.__exit__(exc_type, exc_value, traceback)
                finally:
                    self.handle_closed = True

            def __iter__(self):
                return self

            def __next__(self):
                self.next_calls += 1
                entry = next(self._iterator)
                self.entries_yielded += 1
                return entry

        def tracked_scandir(path: str | os.PathLike[str]):
            path_key = os.path.normcase(os.path.abspath(os.fspath(path)))
            if path_key != target_key:
                return real_scandir(path)
            tracker = ScandirTracker(path)
            trackers.append(tracker)
            return tracker

        errors: list[str] = []
        with patch.object(checker, "MAX_EVIDENCE_FILES", 3):
            with patch.object(checker.os, "scandir", side_effect=tracked_scandir):
                found = checker.scan_evidence_directory(
                    self.root, run_dir, manifest_path, errors
                )

        self.assertIsNone(found)
        self.assertEqual(1, len(errors), errors)
        self.assertIn("超过上限 3", errors[0])
        self.assertIn("枚举未完成", errors[0])
        self.assertEqual(1, len(trackers))
        tracker = trackers[0]
        self.assertEqual(4, tracker.entries_yielded)
        self.assertEqual(4, tracker.next_calls)
        self.assertTrue(tracker.context_exited)
        self.assertTrue(tracker.handle_closed)
        with self.assertRaises(StopIteration):
            next(tracker._iterator)

    def testmanifest必须位于精确运行目录(self) -> None:
        data, manifest_path = self.evidence_manifest()
        data["run_id"] = "another-run"
        data["evidence_dir"] = "report/evidence/S2B-T02/another-run"
        (self.root / data["evidence_dir"]).mkdir(parents=True)
        self.write_json(manifest_path.relative_to(self.root).as_posix(), data)
        result = checker.check_manifest("evidence", str(manifest_path), str(self.root))
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(
            any("manifest 本身必须位于" in error for error in result["errors"])
        )

    def test缺tool_versions拒绝(self) -> None:
        data, manifest_path = self.evidence_manifest()
        del data["tool_versions"]
        self.write_json(manifest_path.relative_to(self.root).as_posix(), data)
        result = checker.check_manifest("evidence", str(manifest_path), str(self.root))
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("tool_versions" in error for error in result["errors"]))

    def test模板必须保持未就绪且CLI只输出JSON(self) -> None:
        manifest = PROJECT_ROOT / "verification" / "stage_delivery_template.json"
        template = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual([False, False, False], [item["frozen"] for item in template["interfaces"]])
        self.assertEqual([], template["files"])
        self.assertEqual({"BLOCKED"}, {item["status"] for item in template["checks"]})
        completed = self.run_cli("inputs", manifest)
        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("", completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual("CHECKS_FAILED", result["status"])
        self.assertTrue(any("未冻结" in error for error in result["errors"]))
        self.assertEqual(
            "检查结果不代表 G0/G4/G5 或实物验收。",
            result["scope_statement"],
        )

    def test只读检查没有文件副作用(self) -> None:
        data = self.input_manifest()
        manifest_path = self.write_json("manifest.json", data)
        before = {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }
        result = checker.check_manifest("inputs", str(manifest_path), str(self.root))
        after = {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }
        self.assertEqual("CHECKS_OK", result["status"], result["errors"])
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
