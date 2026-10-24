#!/usr/bin/env python3
"""验证契约语义解析与绑定 SHA 使用同一原始字节；仓库仅建于系统临时目录。"""

from __future__ import annotations

import contextlib
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import verify_shared_io_contract as checker


class BindingByteConsumptionTests(unittest.TestCase):
    """使用独立两提交仓隔离固定修订与当前磁盘差异。"""

    case_evidence_dir = None

    def setUp(self):
        """保留真实契约的其他门禁，仅替换阶段5绑定来源。"""
        self.temp = tempfile.TemporaryDirectory(prefix="s4_binding_")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repository"
        self.repo.mkdir()
        self.path = self.repo / "stage5.json"
        self.git("init", "--quiet")
        self.git("config", "user.name", "隔离验证")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.contract = json.loads(checker.CONTRACT.read_text(encoding="utf-8"))
        self.binding = next(b for b in self.contract["upstream_bindings"]
                            if b["id"] == "stage5_display_g0_fields")
        fields = self.contract["result_contract"]["display_linkage"]["fields"]
        self.display_value = next(f["values"][0] for f in fields if f["name"] == "display_semantics")

    def git(self, *args):
        """只在本测试创建的临时仓执行 Git 命令。"""
        result = subprocess.run(["git", "-C", str(self.repo), *args],
                                capture_output=True, check=True)
        return result.stdout.decode("utf-8").strip()

    def payload(self, stale, display=None):
        """明确构造两项被消费的阶段5字段。"""
        return (json.dumps({"stale_age_limit_ns": stale,
                            "display_semantics": {"value": display or self.display_value}},
                           ensure_ascii=False) + "\n").encode("utf-8")

    def commit_payload(self, raw):
        """写入并提交测试数据，返回该独立仓的提交号。"""
        self.path.write_bytes(raw)
        self.git("add", "--", "stage5.json")
        self.git("commit", "--quiet", "-m", "隔离测试数据")
        return self.git("rev-parse", "HEAD")

    def prepare(self, pinned, disk, basis="git_blob_fixed_revision"):
        """创建固定提交和不同 HEAD；不克隆共享仓、不操作其分支。"""
        raw = self.payload(pinned)
        revision = self.commit_payload(raw)
        self.commit_payload(self.payload(disk))
        self.binding.update(path=str(self.path), byte_basis=basis,
                            fixed_revision=revision, sha256=hashlib.sha256(raw).hexdigest())

    def run_checker(self):
        """替换唯一契约输入，执行完整检查器并读取退出码和结果。"""
        contract_path = self.root / "contract.json"
        contract_path.write_text(json.dumps(self.contract, ensure_ascii=False), encoding="utf-8")
        evidence = self.root / "result"
        with patch.object(checker, "CONTRACT", contract_path), \
                patch.object(sys, "argv", [str(Path(checker.__file__)), "--evidence-dir", str(evidence)]), \
                contextlib.redirect_stdout(io.StringIO()):
            code = checker.main()
        report = json.loads((evidence / "verify_shared_io_contract_result.json").read_text(encoding="utf-8"))
        if self.case_evidence_dir is not None:
            _, pinned, error = checker.read_binding_bytes(self.binding)
            observation = {
                "case": self._testMethodName, "binding": self.binding,
                "binding_bytes_after_run": pinned.decode("utf-8") if pinned is not None else None,
                "binding_read_error_after_run": error,
                "disk_bytes_after_run": self.path.read_text(encoding="utf-8"),
                "checker_exit_code": code, "checker_result": report,
                "scope": "系统临时目录独立两提交仓；未执行系统HEAD门禁；保留其他真实契约检查",
            }
            target = self.case_evidence_dir / (self._testMethodName + ".json")
            with target.open("x", encoding="utf-8") as handle:
                json.dump(observation, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
        return code, report

    def test_fixed_100_disk_200_contract_200_fails(self):
        """固定100、磁盘200、契约200必须被同源检查拒绝。"""
        self.prepare(100000000, 200000000)
        code, report = self.run_checker()
        self.assertEqual(code, 1)
        self.assertEqual(report["details"]["stage5_stale_age_limit_ns"], 100000000)
        self.assertTrue(any("跨阶段 stale 常量不同源" in f for f in report["failures"]))

    def test_fixed_200_disk_100_contract_200_passes(self):
        """固定200、磁盘100时按固定200判断，其他真实契约门禁保留。"""
        self.prepare(200000000, 100000000)
        code, report = self.run_checker()
        self.assertEqual(code, 0, report["failures"])
        self.assertEqual(report["details"]["stage5_stale_age_limit_ns"], 200000000)

    def test_missing_fixed_revision_fails(self):
        """缺少固定修订不能回退当前磁盘。"""
        self.prepare(100000000, 200000000)
        self.binding.pop("fixed_revision")
        code, report = self.run_checker()
        self.assertEqual(code, 1)
        self.assertNotIn("stage5_stale_age_limit_ns", report["details"])

    def test_unavailable_fixed_revision_fails(self):
        """不存在的固定对象不能回退当前磁盘。"""
        self.prepare(100000000, 200000000)
        self.binding["fixed_revision"] = "0" * 40
        code, report = self.run_checker()
        self.assertEqual(code, 1)
        self.assertNotIn("stage5_stale_age_limit_ns", report["details"])
        bad = report["details"]["upstream_binding_checks"]["bad"]
        self.assertEqual(next(b for b in bad if b["id"] == self.binding["id"])["status"], "BLOB_UNAVAILABLE")

    def test_head_basis_consumes_head_bytes(self):
        """HEAD口径不消费未提交的磁盘变更。"""
        self.prepare(100000000, 200000000, "git_blob_content")
        raw = self.payload(200000000)
        self.binding["sha256"] = hashlib.sha256(raw).hexdigest()
        self.path.write_bytes(self.payload(100000000))
        code, report = self.run_checker()
        self.assertEqual(code, 0, report["failures"])
        self.assertEqual(report["details"]["stage5_stale_age_limit_ns"], 200000000)

    def test_disk_basis_consumes_disk_bytes(self):
        """磁盘口径只消费声明的磁盘原始字节。"""
        self.prepare(100000000, 200000000, "worktree_disk_bytes")
        self.binding["sha256"] = hashlib.sha256(self.path.read_bytes()).hexdigest()
        code, report = self.run_checker()
        self.assertEqual(code, 0, report["failures"])
        self.assertEqual(report["details"]["stage5_stale_age_limit_ns"], 200000000)

    def test_display_semantics_uses_fixed_bytes(self):
        """显示语义同样必须取自固定版本。"""
        raw = self.payload(200000000, "incorrect_semantics")
        revision = self.commit_payload(raw)
        self.commit_payload(self.payload(200000000))
        self.binding.update(path=str(self.path), byte_basis="git_blob_fixed_revision",
                            fixed_revision=revision, sha256=hashlib.sha256(raw).hexdigest())
        code, report = self.run_checker()
        self.assertEqual(code, 1)
        self.assertTrue(any("display_semantics 取值与阶段5 G0 不一致" in f for f in report["failures"]))

    def test_disk_change_after_hash_does_not_change_consumed_bytes(self):
        """哈希读取后磁盘变化不能影响同轮已缓存的语义字节。"""
        self.prepare(100000000, 200000000, "worktree_disk_bytes")
        self.binding["sha256"] = hashlib.sha256(self.path.read_bytes()).hexdigest()
        original = checker.read_binding_bytes
        reads = []

        def read_then_change(binding):
            """仅在目标绑定读取完毕后改变测试磁盘文件。"""
            result = original(binding)
            if binding["path"] == str(self.path):
                reads.append(binding["id"])
                self.path.write_bytes(self.payload(100000000))
            return result

        with patch.object(checker, "read_binding_bytes", side_effect=read_then_change):
            code, report = self.run_checker()
        self.assertEqual(code, 0, report["failures"])
        self.assertEqual(report["details"]["stage5_stale_age_limit_ns"], 200000000)
        # 证据采集会额外读一次；检查器本身只能消费第一次的缓存字节。
        self.assertEqual(len(reads), 2 if self.case_evidence_dir is not None else 1)

    def test_invalid_pinned_json_fails_without_fallback(self):
        """SHA正确但固定字节不是JSON时明确失败。"""
        raw = b"not JSON\n"
        revision = self.commit_payload(raw)
        self.commit_payload(self.payload(200000000))
        self.binding.update(path=str(self.path), byte_basis="git_blob_fixed_revision",
                            fixed_revision=revision, sha256=hashlib.sha256(raw).hexdigest())
        code, report = self.run_checker()
        self.assertEqual(code, 1)
        self.assertTrue(any("已绑定权威 JSON 无法解析" in f for f in report["failures"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="绑定字节消费定向回归")
    parser.add_argument("--case-evidence-dir", type=Path)
    options, remaining = parser.parse_known_args()
    if options.case_evidence_dir is not None:
        options.case_evidence_dir.mkdir(parents=True, exist_ok=False)
        BindingByteConsumptionTests.case_evidence_dir = options.case_evidence_dir
    unittest.main(argv=[sys.argv[0], *remaining], verbosity=2)
