"""覆盖平台静态检查器在受限目录下的精确路径核验。"""

from __future__ import annotations

import os
import stat
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from verification.check_s2b_inference_platform import exact_file


class ExactFilePathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.parent = self.root / "CaseDir"
        self.parent.mkdir()
        self.file = self.parent / "MiXeD.txt"
        self.file.write_text("path fixture\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _deny_enumeration(self, denied_parent: Path, synthesize_ancestors: bool = False):
        path_type = type(self.file)
        original_iterdir = path_type.iterdir
        injected: list[str] = []
        synthetic_entries: dict[str, str] = {}
        if synthesize_ancestors:
            current = Path(self.file.anchor)
            for component in self.file.parts[len(current.parts):]:
                if os.fspath(current) == os.fspath(denied_parent):
                    break
                synthetic_entries[os.fspath(current)] = component
                current = current / component

        def iterdir(candidate: Path):
            candidate_text = os.fspath(candidate)
            if candidate_text == os.fspath(denied_parent):
                injected.append(os.fspath(candidate))
                raise PermissionError(5, "injected directory enumeration denial")
            if candidate_text in synthetic_entries:
                return iter([SimpleNamespace(name=synthetic_entries[candidate_text])])
            return original_iterdir(candidate)

        return mock.patch.object(path_type, "iterdir", new=iterdir), injected

    def test_exact_existing_file_passes_normally(self) -> None:
        self.assertEqual(exact_file(self.file), self.file)

    def test_case_mismatch_fails_during_normal_enumeration(self) -> None:
        wrong = self.root / "casedir" / "mixed.txt"
        with self.assertRaises(ValueError):
            exact_file(wrong)

    def test_drive_root_permission_uses_verified_fallback(self) -> None:
        denied = Path(self.file.anchor)
        patcher, injected = self._deny_enumeration(denied)
        with patcher:
            resolved = exact_file(self.file)
        self.assertEqual(len(injected), 1, "必须实际注入一次盘符根枚举拒绝")
        self.assertEqual(resolved, self.file)

    def test_intermediate_parent_permission_uses_verified_fallback(self) -> None:
        patcher, injected = self._deny_enumeration(self.parent, synthesize_ancestors=True)
        with patcher:
            resolved = exact_file(self.file)
        self.assertEqual(len(injected), 1, "必须实际注入一次中间父目录枚举拒绝")
        self.assertEqual(resolved, self.file)

    def test_non_permission_enumeration_error_is_not_ignored(self) -> None:
        path_type = type(self.file)
        original_iterdir = path_type.iterdir
        injected: list[str] = []

        def fail_with_other_error(candidate: Path):
            if os.fspath(candidate) == os.fspath(self.root):
                injected.append(os.fspath(candidate))
                raise OSError(22, "injected non-permission error")
            current = Path(self.file.anchor)
            for component in self.file.parts[len(current.parts):]:
                if os.fspath(current) == os.fspath(candidate):
                    return iter([SimpleNamespace(name=component)])
                current = current / component
            return original_iterdir(candidate)

        with mock.patch.object(path_type, "iterdir", new=fail_with_other_error):
            with self.assertRaises(OSError) as raised:
                exact_file(self.file)
        self.assertNotIsInstance(raised.exception, PermissionError)
        self.assertEqual(len(injected), 1, "必须实际注入一次非PermissionError故障")

    def test_fallback_rejects_case_mismatch(self) -> None:
        wrong = self.root / "casedir" / "MiXeD.txt"
        patcher, injected = self._deny_enumeration(Path(wrong.anchor))
        with patcher:
            with self.assertRaises((OSError, ValueError)):
                exact_file(wrong)
        self.assertEqual(len(injected), 1, "必须实际进入大小写反例的回退路径")

    def test_fallback_rejects_missing_file(self) -> None:
        missing = self.root / "CaseDir" / "missing.txt"
        patcher, injected = self._deny_enumeration(Path(missing.anchor))
        with patcher:
            with self.assertRaises(OSError):
                exact_file(missing)
        self.assertEqual(len(injected), 1, "必须实际进入缺失文件反例的回退路径")

    def test_fallback_rejects_non_directory_middle_component(self) -> None:
        invalid = self.file / "child.txt"
        patcher, injected = self._deny_enumeration(Path(invalid.anchor))
        with patcher:
            with self.assertRaises((OSError, ValueError)):
                exact_file(invalid)
        self.assertEqual(len(injected), 1, "必须实际进入中间分量非目录反例的回退路径")

    def test_fallback_rejects_symbolic_link(self) -> None:
        link = self.root / "linkdir"
        try:
            os.symlink(self.parent, link, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"当前Windows账户不能创建符号链接：{exc}")
        linked_file = link / self.file.name
        patcher, injected = self._deny_enumeration(Path(linked_file.anchor))
        with patcher:
            with self.assertRaises(ValueError):
                exact_file(linked_file)
        self.assertEqual(len(injected), 1, "必须实际进入符号链接反例的回退路径")

    def test_fallback_rejects_symbolic_link_metadata(self) -> None:
        patcher, injected = self._deny_enumeration(Path(self.file.anchor))
        path_type = type(self.file)
        original_lstat = path_type.lstat

        def lstat(candidate: Path):
            if os.fspath(candidate) == os.fspath(self.file):
                return SimpleNamespace(st_mode=stat.S_IFLNK | 0o777, st_file_attributes=0)
            return original_lstat(candidate)

        with patcher, mock.patch.object(path_type, "lstat", new=lstat):
            with self.assertRaisesRegex(ValueError, "拒绝链接路径"):
                exact_file(self.file)
        self.assertEqual(len(injected), 1, "必须实际进入符号链接元数据反例的回退路径")

    def test_fallback_rejects_reparse_attribute(self) -> None:
        patcher, injected = self._deny_enumeration(Path(self.file.anchor))
        path_type = type(self.file)
        original_lstat = path_type.lstat

        def lstat(candidate: Path):
            if os.fspath(candidate) == os.fspath(self.file):
                return SimpleNamespace(st_mode=stat.S_IFREG, st_file_attributes=0x400)
            return original_lstat(candidate)

        with patcher, mock.patch.object(path_type, "lstat", new=lstat):
            with self.assertRaisesRegex(ValueError, "拒绝链接路径"):
                exact_file(self.file)
        self.assertEqual(len(injected), 1, "必须实际进入reparse反例的回退路径")


if __name__ == "__main__":
    unittest.main()
