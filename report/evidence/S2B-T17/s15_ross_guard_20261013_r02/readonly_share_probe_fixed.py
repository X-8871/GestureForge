"""隔离验证只读目录句柄与no-delete-share的rename阻止能力。"""

from __future__ import annotations

import ctypes
import json
import os
from ctypes import wintypes
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUN = ROOT / "readonly_share_probe_20261013_a2"
READ_ATTRIBUTES = 0x0080
LIST_DIRECTORY = 0x0001
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
ERROR_SHARING_VIOLATION = 32
ERROR_ACCESS_DENIED = 5


def _open(kernel32, path: Path, access: int):
    handle = kernel32.CreateFileW(
        str(path), access, FILE_SHARE_READ | FILE_SHARE_WRITE, None,
        OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT,
        None,
    )
    if not handle or handle == wintypes.HANDLE(-1).value:
        return None, ctypes.get_last_error()
    return handle, 0


def _rename_status(source: Path, destination: Path) -> tuple[str, int | None]:
    try:
        os.rename(source, destination)
        return "renamed", None
    except OSError as error:
        winerror = getattr(error, "winerror", None)
        if winerror in (ERROR_ACCESS_DENIED, ERROR_SHARING_VIOLATION):
            return "blocked", winerror
        return "error", winerror


def main() -> int:
    if os.name != "nt":
        raise RuntimeError("该探针只支持Windows")
    if RUN.exists() or RUN.is_symlink():
        raise RuntimeError(f"隔离探针路径已存在：{RUN}")
    RUN.mkdir()
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                    wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD,
                                    wintypes.HANDLE]
    kernel32.CreateFileW.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    actual_prefixes = [
        Path(r"C:\Users"),
        Path(r"C:\Users\22061"),
        Path(r"C:\Users\22061\.codex"),
        Path(r"C:\Users\22061\.codex\worktrees"),
        Path(r"C:\Users\22061\.codex\worktrees\96a3"),
        Path(r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition"),
    ]
    actual_open = []
    for access_name, access in (("FILE_READ_ATTRIBUTES", READ_ATTRIBUTES),
                                ("FILE_LIST_DIRECTORY", LIST_DIRECTORY),
                                ("READ_ATTRIBUTES|LIST_DIRECTORY", READ_ATTRIBUTES | LIST_DIRECTORY)):
        for path in actual_prefixes:
            handle, error = _open(kernel32, path, access)
            record = {"access": access_name, "path": str(path), "opened": handle is not None,
                      "winerror": error}
            if handle is not None:
                record["close_ok"] = bool(kernel32.CloseHandle(handle))
                record["close_winerror"] = 0 if record["close_ok"] else ctypes.get_last_error()
            actual_open.append(record)

    isolated_tests = []
    for access_name, access in (("FILE_READ_ATTRIBUTES", READ_ATTRIBUTES),
                                ("FILE_LIST_DIRECTORY", LIST_DIRECTORY),
                                ("READ_ATTRIBUTES|LIST_DIRECTORY", READ_ATTRIBUTES | LIST_DIRECTORY)):
        for component in ("c_users_fixture", "profile_fixture", "repo_fixture"):
            case_root = RUN / f"{access_name.replace('|', '_')}_{component}"
            target = case_root / "directory"
            moved = case_root / "renamed"
            target.mkdir(parents=True)
            child = target / "content-change.bin"
            handle, open_error = _open(kernel32, target, access)
            item = {"access": access_name, "component_case": component,
                    "target": str(target), "opened": handle is not None,
                    "open_winerror": open_error}
            if handle is not None:
                try:
                    child.write_bytes(b"write while directory handle held")
                    item["content_write_succeeded"] = child.exists()
                    item["rename_while_held"], item["rename_winerror_while_held"] = _rename_status(target, moved)
                    item["target_exists_while_held"] = target.exists()
                    item["moved_exists_while_held"] = moved.exists()
                finally:
                    item["close_ok"] = bool(kernel32.CloseHandle(handle))
                    item["close_winerror"] = 0 if item["close_ok"] else ctypes.get_last_error()
                if item["rename_while_held"] == "blocked":
                    item["rename_after_release"], item["rename_winerror_after_release"] = _rename_status(target, moved)
                else:
                    item["rename_after_release"] = "not-retried"
                if moved.exists():
                    reverse, reverse_error = _rename_status(moved, target)
                    item["restore_after_probe"] = reverse
                    item["restore_winerror"] = reverse_error
            isolated_tests.append(item)

    state = {
        "run": str(RUN),
        "share_mode": FILE_SHARE_READ | FILE_SHARE_WRITE,
        "actual_prefix_open_tests": actual_open,
        "isolated_tests": isolated_tests,
        "note": "真实前缀仅以只读句柄打开后立即关闭；rename/write仅作用于隔离探针目录。",
    }
    (RUN / "result.json").write_text(json.dumps(state, ensure_ascii=False,
                                                sort_keys=True, indent=2) + "\n",
                                     encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, sort_keys=True))
    for item in isolated_tests:
        if not item.get("opened") or not item.get("close_ok") or not item.get("content_write_succeeded"):
            return 2
        if item.get("rename_while_held") != "blocked" or item.get("rename_after_release") != "renamed":
            return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
