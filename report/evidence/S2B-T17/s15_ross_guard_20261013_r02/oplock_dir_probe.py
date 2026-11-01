"""在隔离证据目录中验证 Windows 目录 RH oplock 能否阻止目录改名。"""

from __future__ import annotations

import ctypes
import json
import os
import threading
import time
from ctypes import wintypes
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUN = ROOT / "oplock_probe_20261013_a1"
SRC = RUN / "source"
DST = RUN / "renamed"
FSCTL_REQUEST_OPLOCK = 0x00090240
FILE_READ_ATTRIBUTES = 0x0080
FILE_SHARE_ALL = 0x00000007
OPEN_EXISTING = 3
FILE_FLAG_OVERLAPPED = 0x40000000
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
OPLOCK_LEVEL_CACHE_READ = 0x00000001
OPLOCK_LEVEL_CACHE_HANDLE = 0x00000002
REQUEST_OPLOCK_CURRENT_VERSION = 1
REQUEST_OPLOCK_INPUT_FLAG_REQUEST = 0x00000001
ERROR_IO_PENDING = 997
WAIT_OBJECT_0 = 0


class RequestIn(ctypes.Structure):
    _fields_ = [("StructureVersion", wintypes.WORD),
                ("StructureLength", wintypes.WORD),
                ("RequestedOplockLevel", wintypes.DWORD),
                ("Flags", wintypes.DWORD)]


class RequestOut(ctypes.Structure):
    _fields_ = [("StructureVersion", wintypes.WORD),
                ("StructureLength", wintypes.WORD),
                ("OriginalOplockLevel", wintypes.DWORD),
                ("NewOplockLevel", wintypes.DWORD),
                ("Flags", wintypes.DWORD),
                ("AccessMode", wintypes.DWORD),
                ("ShareMode", wintypes.DWORD)]


class Overlapped(ctypes.Structure):
    _fields_ = [("Internal", ctypes.c_void_p),
                ("InternalHigh", ctypes.c_void_p),
                ("Offset", wintypes.DWORD),
                ("OffsetHigh", wintypes.DWORD),
                ("hEvent", wintypes.HANDLE)]


def main() -> int:
    if os.name != "nt":
        raise RuntimeError("该探针只支持 Windows")
    if RUN.exists() or RUN.is_symlink():
        raise RuntimeError(f"隔离探针路径已存在：{RUN}")
    RUN.mkdir()
    SRC.mkdir()

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create_file = kernel32.CreateFileW
    create_file.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                            wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD,
                            wintypes.HANDLE]
    create_file.restype = wintypes.HANDLE
    create_event = kernel32.CreateEventW
    create_event.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.BOOL,
                             wintypes.LPCWSTR]
    create_event.restype = wintypes.HANDLE
    device_io = kernel32.DeviceIoControl
    device_io.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID,
                          wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD,
                          ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(Overlapped)]
    device_io.restype = wintypes.BOOL
    wait_for = kernel32.WaitForSingleObject
    wait_for.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    wait_for.restype = wintypes.DWORD
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = [wintypes.HANDLE]
    close_handle.restype = wintypes.BOOL

    event = create_event(None, True, False, None)
    if not event or event == wintypes.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    handle = create_file(str(SRC), FILE_READ_ATTRIBUTES, FILE_SHARE_ALL, None,
                         OPEN_EXISTING,
                         FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OVERLAPPED, None)
    if not handle or handle == wintypes.HANDLE(-1).value:
        close_handle(event)
        raise ctypes.WinError(ctypes.get_last_error())

    overlapped = Overlapped()
    overlapped.hEvent = event
    request = RequestIn(REQUEST_OPLOCK_CURRENT_VERSION,
                        ctypes.sizeof(RequestIn),
                        OPLOCK_LEVEL_CACHE_READ | OPLOCK_LEVEL_CACHE_HANDLE,
                        REQUEST_OPLOCK_INPUT_FLAG_REQUEST)
    result = RequestOut()
    result.StructureVersion = REQUEST_OPLOCK_CURRENT_VERSION
    result.StructureLength = ctypes.sizeof(RequestOut)
    bytes_returned = wintypes.DWORD(0)
    granted = bool(device_io(handle, FSCTL_REQUEST_OPLOCK,
                             ctypes.byref(request), ctypes.sizeof(request),
                             ctypes.byref(result), ctypes.sizeof(result),
                             ctypes.byref(bytes_returned), ctypes.byref(overlapped)))
    request_error = 0 if granted else ctypes.get_last_error()
    if granted or request_error != ERROR_IO_PENDING:
        close_handle(handle)
        close_handle(event)
        raise OSError(f"目录 RH oplock 未确认授予，immediate={granted} WinError={request_error}")

    rename_result: dict[str, object] = {}

    def rename_worker() -> None:
        started = time.monotonic()
        try:
            os.rename(SRC, DST)
            rename_result["status"] = "renamed"
        except BaseException as exc:  # 记录隔离探针线程异常
            rename_result["status"] = "error"
            rename_result["error"] = repr(exc)
        rename_result["elapsed_s"] = time.monotonic() - started

    worker = threading.Thread(target=rename_worker, daemon=True)
    worker.start()
    wait_result = wait_for(event, 5000)
    state = {
        "run": str(RUN),
        "filesystem": "local Windows path",
        "oplock_ioctl": hex(FSCTL_REQUEST_OPLOCK),
        "requested_level": OPLOCK_LEVEL_CACHE_READ | OPLOCK_LEVEL_CACHE_HANDLE,
        "device_io_immediate": granted,
        "device_io_error": request_error,
        "wait_result": int(wait_result),
        "break_event_signaled": wait_result == WAIT_OBJECT_0,
        "break_output": {
            "original_level": int(result.OriginalOplockLevel),
            "new_level": int(result.NewOplockLevel),
            "flags": int(result.Flags),
            "internal_status": int(overlapped.Internal or 0),
        },
        "rename_thread_alive_before_release": worker.is_alive(),
        "source_exists_before_release": SRC.exists(),
        "destination_exists_before_release": DST.exists(),
        "rename_result_before_release": dict(rename_result),
    }

    # 关闭持锁句柄会隐式确认 oplock break，释放等待中的改名操作。
    close_ok = bool(close_handle(handle))
    close_error = 0 if close_ok else ctypes.get_last_error()
    worker.join(5)
    state["close_handle_ok"] = close_ok
    state["close_handle_error"] = close_error
    state["rename_thread_alive_after_release"] = worker.is_alive()
    state["rename_result_after_release"] = dict(rename_result)
    state["source_exists_after_release"] = SRC.exists()
    state["destination_exists_after_release"] = DST.exists()
    event_close_ok = bool(close_handle(event))
    state["event_close_ok"] = event_close_ok
    (RUN / "result.json").write_text(json.dumps(state, ensure_ascii=False,
                                                sort_keys=True, indent=2) + "\n",
                                     encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, sort_keys=True))

    if not close_ok or not event_close_ok or worker.is_alive():
        return 2
    if not state["break_event_signaled"] or not state["rename_thread_alive_before_release"]:
        return 3
    if not state["source_exists_before_release"] or state["destination_exists_before_release"]:
        return 4
    if rename_result.get("status") != "renamed" or not state["destination_exists_after_release"]:
        return 5
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
