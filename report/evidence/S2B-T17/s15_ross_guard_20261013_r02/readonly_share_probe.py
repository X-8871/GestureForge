"""比较只读目录句柄的no-delete-share路径pin及实际祖先打开能力。"""

from __future__ import annotations

import ctypes
import json
import os
from ctypes import wintypes
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUN = ROOT / "readonly_share_probe_20261013_a1"
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


def main() -> int:
    if os.name != "nt":
        raise RuntimeError("该探针只支持Windows")
    if RUN.exists() or RUN.is_symlink():
        raise RuntimeError(f"隔离探针路径已存在：{RUN}")
    RUN.mkdir()
    sandbox = RUN / "sandbox"
    level_a = sandbox / "a"
    level_b = level_a / "b"
    output = level_b / "output"
    output.mkdir(parents=True)

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
    actual_results = []
    actual_handles = []
    for access_name, access in (("FILE_READ_ATTRIBUTES", READ_ATTRIBUTES),
                                ("FILE_LIST_DIRECTORY", LIST_DIRECTORY),
                                ("READ_ATTRIBUTES|LIST_DIRECTORY", READ_ATTRIBUTES | LIST_DIRECTORY)):
        for path in actual_prefixes:
            handle, error = _open(kernel32, path, access)
            actual_results.append({"access": access_name, "path": str(path),
                                   "opened": handle is not None, "winerror": error})
            if handle is not None:
                actual_handles.append((path, handle))
    for path, handle in reversed(actual_handles):
        if not kernel32.CloseHandle(handle):
            raise ctypes.WinError(ctypes.get_last_error())

    pin_results = []
    for access_name, access in (("FILE_READ_ATTRIBUTES", READ_ATTRIBUTES),
                                ("FILE_LIST_DIRECTORY", LIST_DIRECTORY),
                                ("READ_ATTRIBUTES|LIST_DIRECTORY", READ_ATTRIBUTES | LIST_DIRECTORY)):
        handles = []
        open_errors = []
        try:
            for path in (level_a, level_b, output):
                handle, error = _open(kernel32, path, access)
                if handle is None:
                    open_errors.append({"path": str(path), "winerror": error})
                    break
                handles.append((path, handle))
            if open_errors:
                pin_results.append({"access": access_name, "open_errors": open_errors,
                                    "rename_attempts": []})
                continue
            (output / "content-change.bin").write_bytes(b"write while pinned")
            attempts = []
            for source in (level_a, level_b, output):
                destination = source.with_name(source.name + "_renamed")
                try:
                    os.rename(source, destination)
                    status, error = "renamed", None
                except OSError as exc:
                    error = getattr(exc, "winerror", None)
                    status = "blocked" if error in (ERROR_ACCESS_DENIED, ERROR_SHARING_VIOLATION) else "error"
                attempts.append({"source": str(source), "status": status,
                                 "winerror": error, "source_exists": source.exists(),
                                 "destination_exists": destination.exists()})
            pin_results.append({"access": access_name, "open_errors": [],
                                "content_write_succeeded": (output / "content-change.bin").exists(),
                                "rename_attempts": attempts})
        finally:
            for path, handle in reversed(handles):
                if not kernel32.CloseHandle(handle):
                    raise ctypes.WinError(ctypes.get_last_error())

    state = {
        "run": str(RUN),
        "share_mode": FILE_SHARE_READ | FILE_SHARE_WRITE,
        "actual_prefix_open_tests": actual_results,
        "isolated_tree_pin_tests": pin_results,
        "note": "実路径只读打开后立即关闭；改名测试仅作用于本RunId自建sandbox。",
    }
    (RUN / "result.json").write_text(json.dumps(state, ensure_ascii=False,
                                                sort_keys=True, indent=2) + "\n",
                                     encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, sort_keys=True))
    for item in pin_results:
        if item.get("open_errors") or not item.get("content_write_succeeded"):
            return 2
        if any(attempt["status"] != "blocked" for attempt in item["rename_attempts"]):
            return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
