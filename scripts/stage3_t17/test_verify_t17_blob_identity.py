#!/usr/bin/env python3
"""固定树期望集合的定向 CLI 回归；全部夹具只写入操作系统临时目录。"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("verify_t17_blob_identity.py")
SCOPE = "report/evidence/S3-T05/run"


class BlobIdentityTests(unittest.TestCase):
    """覆盖原漏洞及历史固定提交的合法复跑方式。"""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="t17_identity_")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "core.autocrlf", "false")
        self.run_dir = self.repo / SCOPE
        self.run_dir.mkdir(parents=True)
        for name, body in (("README.md", "说明\n"), ("probe.txt", "探测\n"),
                           ("result.json", "{}\n")):
            (self.run_dir / name).write_text(body, encoding="utf-8", newline="\n")
        (self.run_dir / "frame.bin").write_bytes(b"\x00\x01\xff")
        self.git("add", "--all")
        self.git("-c", "user.name=定向测试", "-c", "user.email=t17@local",
                 "commit", "-qm", "夹具基线")
        self.commit = self.git("rev-parse", "HEAD").stdout.decode().strip()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True,
                              capture_output=True)

    def verify(self, *, scope=SCOPE, certify=SCOPE, repo=None, extra=()):
        output = self.root / "result.json"
        if output.exists():
            output.unlink()
        cp = subprocess.run([sys.executable, "-B", str(SCRIPT), "--repo-root",
                             str(repo or self.repo), "--commit", self.commit,
                             "--scope", scope, "--certify", certify,
                             "--json-out", str(output), *extra], capture_output=True)
        result = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {}
        return cp, result

    def assert_rejected(self, result):
        cp, data = result
        self.assertNotEqual(cp.returncode, 0, cp.stdout.decode("utf-8"))
        self.assertNotIn(b"BLOB_BYTE_IDENTITY_OK", cp.stdout)
        self.assertNotEqual(data.get("verdict"), "BLOB_BYTE_IDENTITY_OK")
        return data

    def test_complete_fixed_tree_passes_text_only(self):
        cp, data = self.verify()
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertEqual(data["expected_file_count"], 3)
        self.assertEqual(data["files_checked"], 3)
        self.assertFalse(any(p.endswith(".bin") for p in data["expected_text_files"]))

    def test_missing_single_file_rejected(self):
        (self.run_dir / "probe.txt").unlink()
        data = self.assert_rejected(self.verify())
        self.assertEqual(data["missing_from_worktree"], [SCOPE + "/probe.txt"])

    def test_readme_only_rejected(self):
        (self.run_dir / "probe.txt").unlink()
        (self.run_dir / "result.json").unlink()
        data = self.assert_rejected(self.verify())
        self.assertEqual(len(data["missing_from_worktree"]), 2)

    def test_missing_directory_rejected(self):
        shutil.rmtree(self.run_dir)
        self.assertEqual(len(self.assert_rejected(self.verify())["missing_from_worktree"]), 3)

    def test_nonexistent_scope_and_certify_rejected(self):
        data = self.assert_rejected(self.verify(scope="absent/run", certify="absent/run"))
        self.assertEqual(data["expected_file_count"], 0)

    def test_zero_text_objects_rejected(self):
        data = self.assert_rejected(self.verify(extra=("--exclude", SCOPE + "/README.md",
            "--exclude", SCOPE + "/probe.txt", "--exclude", SCOPE + "/result.json")))
        self.assertEqual(data["expected_file_count"], 0)

    def test_uncovered_certified_directory_rejected(self):
        cp, data = self.verify(certify="report/evidence/other")
        self.assertEqual(cp.returncode, 4)
        self.assert_rejected((cp, data))

    def test_extra_file_rejected(self):
        (self.run_dir / "extra.md").write_text("额外\n", encoding="utf-8")
        data = self.assert_rejected(self.verify())
        self.assertEqual(data["unexpected_in_worktree"], [SCOPE + "/extra.md"])

    def test_changed_file_rejected(self):
        (self.run_dir / "probe.txt").write_text("变更\n", encoding="utf-8")
        self.assertEqual(self.assert_rejected(self.verify())["mismatch_count"], 1)

    def test_gitdir_view_readme_only_rejected(self):
        view = self.root / "readonly_view"
        (view / SCOPE).mkdir(parents=True)
        (view / ".git").write_text("gitdir: " + str(self.repo / ".git") + "\n", encoding="utf-8")
        shutil.copyfile(self.run_dir / "README.md", view / SCOPE / "README.md")
        data = self.assert_rejected(self.verify(repo=view))
        self.assertEqual(len(data["missing_from_worktree"]), 2)

    def test_historical_fixed_commit_with_explicit_exclusion(self):
        (self.run_dir / "later.md").write_text("后增附件\n", encoding="utf-8")
        self.git("add", "--all")
        self.git("-c", "user.name=定向测试", "-c", "user.email=t17@local",
                 "commit", "-qm", "后续提交")
        cp, data = self.verify(extra=("--exclude", SCOPE + "/later.md"))
        self.assertEqual(cp.returncode, 0, cp.stdout)
        self.assertEqual(data["commit"], self.commit)
        self.assertEqual(data["expected_file_count"], 3)

    def test_certified_directory_without_text_objects_rejected(self):
        (self.run_dir / "binary_only").mkdir()
        (self.run_dir / "binary_only" / "f.bin").write_bytes(b"\x00")
        self.git("add", "--all")
        self.git("-c", "user.name=定向测试", "-c", "user.email=t17@local",
                 "commit", "-qm", "二进制目录")
        self.commit = self.git("rev-parse", "HEAD").stdout.decode().strip()
        data = self.assert_rejected(self.verify(certify=SCOPE + "/binary_only"))
        self.assertEqual(data["empty_certified_dirs"], [SCOPE + "/binary_only"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
