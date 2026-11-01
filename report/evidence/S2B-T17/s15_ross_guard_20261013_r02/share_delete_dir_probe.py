"""在隔离目录中检查DELETE访问与分享标志能否阻止被打开目录改名。"""

from __future__ import annotations

import ctypes
import json
import os
from ctypes import wintypes
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUN = ROOT / "share_delete_probe_20261013_a1"
SRC = RUN / "source"
DST = RUN / "renamed"
CHILD = SRC / "content-change.bin"
DELETE = 0x00010000
FILE_READ_ATTRIBUTES = 0x0080
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
ERROR_SHARING_VIOLATION = 32
ERROR_ACCESS_DENIED = 5


def main() -> int:
    if os.name != "nt":
        raise RuntimeError("该探针只支持 Windows")
    if RUN.exists() or RUN.is_symlink():
        raise RuntimeError(f"隔离探针路径已存在：{RUN}")
    RUN.mkdir()
    SRC.mkdir()
    CHILD.write_bytes(b"before-open")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create_file = kernel32.CreateFileW
    create_file.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                            wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD,
                            wintypes.HANDLE]
    create_file.restype = wintypes.HANDLE
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = [wintypes.HANDLE]
    close_handle.restype = wintypes.BOOL
    handle = create_file(
        str(SRC), DELETE | FILE_READ_ATTRIBUTES,
        FILE_SHARE_READ | FILE_SHARE_WRITE, None, OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT, None,
    )
    invalid = wintypes.HANDLE(-1).value
    if not handle or handle == invalid:
        error = ctypes.get_last_error()
        state = {"handle_opened": False, "open_error": error, "run": str(RUN)}
        (RUN / "result.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(state, sort_keys=True))
        return 2

    # 目录内容变更后再尝试改名，覆盖长时间bitgen写入的关键条件。
    CHILD.write_bytes(b"after-open-content-change")
    rename_error = None
    try:
        os.rename(SRC, DST)
        rename_state = "renamed"
    except OSError as error:
        rename_error = getattr(error, "winerror", None)
        rename_state = "blocked" if rename_error in (ERROR_ACCESS_DENIED, ERROR_SHARING_VIOLATION) else "error"
    state = {
        "run": str(RUN),
        "handle_opened": True,
        "desired_access": DELETE | FILE_READ_ATTRIBUTES,
        "share_mode": FILE_SHARE_READ | FILE_SHARE_WRITE,
        "content_changed_after_open": CHILD.exists() and CHILD.read_bytes() == b"after-open-content-change",
        "rename_state_before_release": rename_state,
        "rename_winerror_before_release": rename_error,
        "source_exists_before_release": SRC.exists(),
        "destination_exists_before_release": DST.exists(),
    }
    close_ok = bool(close_handle(handle))
    close_error = 0 if close_ok else ctypes.get_last_error()
    state["close_handle_ok"] = close_ok
    state["close_handle_error"] = close_error
    if rename_state == "blocked":
        try:
            os.rename(SRC, DST)
            state["rename_state_after_release"] = "renamed"
        except OSError as error:
            state["rename_state_after_release"] = "error"
            state["rename_winerror_after_release"] = getattr(error, "winerror", None)
    else:
        state["rename_state_after_release"] = "not-retried"
    state["source_exists_after_release"] = SRC.exists()
    state["destination_exists_after_release"] = DST.exists()
    (RUN / "result.json").write_text(json.dumps(state, ensure_ascii=False,
                                                sort_keys=True, indent=2) + "\n",
                                     encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, sort_keys=True))
    if not close_ok:
        return 3
    if rename_state != "blocked" or not state["source_exists_before_release"]:
        return 4
    if state.get("rename_state_after_release") != "renamed" or not state["destination_exists_after_release"]:
        return 5
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
