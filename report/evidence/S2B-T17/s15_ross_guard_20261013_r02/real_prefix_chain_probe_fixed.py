"""同时只读固定实际工作区祖先链并复核Win32文件身份。"""

from __future__ import annotations

import ctypes
import json
import os
import time
from pathlib import Path
from ctypes import wintypes


EVIDENCE_ROOT = Path(__file__).resolve().parent
RUN = EVIDENCE_ROOT / "real_prefix_chain_probe_20261013_a4"
if RUN.exists():
    raise RuntimeError(f"精确证据目标已经存在，拒绝覆盖：{RUN}")
RUN.mkdir()

REPO = Path(__file__).resolve().parents[4]
PREFIXES = [
    Path(r"C:\Users"),
    Path(r"C:\Users\22061"),
    Path(r"C:\Users\22061\.codex"),
    Path(r"C:\Users\22061\.codex\worktrees"),
    Path(r"C:\Users\22061\.codex\worktrees\96a3"),
    REPO,
    REPO / "report",
    REPO / "report" / "evidence",
    REPO / "report" / "evidence" / "S2B-T17",
    EVIDENCE_ROOT,
]


class FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]


class BY_HANDLE_FILE_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("dwFileAttributes", wintypes.DWORD),
        ("ftCreationTime", FILETIME),
        ("ftLastAccessTime", FILETIME),
        ("ftLastWriteTime", FILETIME),
        ("dwVolumeSerialNumber", wintypes.DWORD),
        ("nFileSizeHigh", wintypes.DWORD),
        ("nFileSizeLow", wintypes.DWORD),
        ("nNumberOfLinks", wintypes.DWORD),
        ("nFileIndexHigh", wintypes.DWORD),
        ("nFileIndexLow", wintypes.DWORD),
    ]


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
CreateFileW = kernel32.CreateFileW
CreateFileW.argtypes = [ctypes.c_wchar_p, wintypes.DWORD, wintypes.DWORD,
                        ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD,
                        wintypes.HANDLE]
CreateFileW.restype = wintypes.HANDLE
GetFileInformationByHandle = kernel32.GetFileInformationByHandle
GetFileInformationByHandle.argtypes = [wintypes.HANDLE,
                                       ctypes.POINTER(BY_HANDLE_FILE_INFORMATION)]
GetFileInformationByHandle.restype = wintypes.BOOL
GetFinalPathNameByHandleW = kernel32.GetFinalPathNameByHandleW
GetFinalPathNameByHandleW.argtypes = [wintypes.HANDLE, wintypes.LPWSTR,
                                      wintypes.DWORD, wintypes.DWORD]
GetFinalPathNameByHandleW.restype = wintypes.DWORD
CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [wintypes.HANDLE]
CloseHandle.restype = wintypes.BOOL

FILE_LIST_DIRECTORY = 0x0001
FILE_SHARE_READ = 0x0001
FILE_SHARE_WRITE = 0x0002
OPEN_EXISTING = 3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


def open_dir(path: Path):
    """只读列目录打开，拒绝共享删除并显式打开reparse点本身。"""
    ctypes.set_last_error(0)
    handle = CreateFileW(str(path), FILE_LIST_DIRECTORY,
                         FILE_SHARE_READ | FILE_SHARE_WRITE, None,
                         OPEN_EXISTING,
                         FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT,
                         None)
    if not handle or handle == INVALID_HANDLE_VALUE:
        raise OSError(ctypes.get_last_error(), f"打开目录失败：{path}")
    return handle


def identity(handle) -> dict:
    """从目录句柄取得卷序列号、文件索引和属性。"""
    info = BY_HANDLE_FILE_INFORMATION()
    ctypes.set_last_error(0)
    if not GetFileInformationByHandle(handle, ctypes.byref(info)):
        raise OSError(ctypes.get_last_error(), "GetFileInformationByHandle失败")
    return {
        "attributes": int(info.dwFileAttributes),
        "volume_serial": int(info.dwVolumeSerialNumber),
        "file_id": (int(info.nFileIndexHigh) << 32) | int(info.nFileIndexLow),
        "creation_ticks": (int(info.ftCreationTime.dwHighDateTime) << 32)
        | int(info.ftCreationTime.dwLowDateTime),
    }


def final_name(handle) -> str:
    """读取内核按句柄解析的规范路径。"""
    buffer = ctypes.create_unicode_buffer(32768)
    ctypes.set_last_error(0)
    length = GetFinalPathNameByHandleW(handle, buffer, len(buffer), 0)
    if not length or length >= len(buffer):
        raise OSError(ctypes.get_last_error(), "GetFinalPathNameByHandleW失败")
    value = buffer.value
    if value.startswith("\\\\?\\"):
        value = value[4:]
    return value


def close_checked(handle) -> dict:
    """关闭句柄并保留即时Win32错误码。"""
    ctypes.set_last_error(0)
    ok = bool(CloseHandle(handle))
    return {"ok": ok, "winerror": 0 if ok else ctypes.get_last_error()}


def main() -> int:
    for index, path in enumerate(PREFIXES):
        if not path.is_dir():
            raise RuntimeError(f"实际前缀不是目录或不存在：{path}")
        if index and path.parent != PREFIXES[index - 1]:
            raise RuntimeError(f"前缀链字面关系不连续：{PREFIXES[index - 1]} -> {path}")

    held = []
    records = []
    fresh_handles = []
    closes = []
    started = time.time()
    failure = None
    try:
        for path in PREFIXES:
            handle = open_dir(path)
            held.append(handle)
            ident = identity(handle)
            resolved = final_name(handle)
            expected = str(path)
            if ident["attributes"] & FILE_ATTRIBUTE_REPARSE_POINT:
                raise RuntimeError(f"实际祖先是reparse point：{path}")
            if os.path.normcase(resolved) != os.path.normcase(expected):
                raise RuntimeError(f"句柄最终路径不匹配：{expected} -> {resolved}")
            records.append({"path": expected, "final_path": resolved, **ident})

        # 所有原始句柄都持有后，再按路径重开一次并比较对象身份。
        for expected_record in records:
            path = Path(expected_record["path"])
            handle = open_dir(path)
            fresh_handles.append(handle)
            fresh_identity = identity(handle)
            fresh_final = final_name(handle)
            same = all(fresh_identity[key] == expected_record[key]
                       for key in ("volume_serial", "file_id", "creation_ticks", "attributes"))
            if not same or os.path.normcase(fresh_final) != os.path.normcase(expected_record["final_path"]):
                raise RuntimeError(f"链句柄复读身份或final path漂移：{path}")
            expected_record["reopen_identity_match"] = same
            expected_record["reopen_final_path"] = fresh_final

        # 仅在自己新建的a4目录内测试子文件写入，不触碰实际祖先目录内容。
        test_file = RUN / "held_chain_write_probe.bin"
        test_file.write_bytes(b"a4-write-probe\x00")
        content_write_ok = test_file.read_bytes() == b"a4-write-probe\x00"
    except BaseException as exc:
        failure = {"type": type(exc).__name__, "message": repr(exc),
                   "winerror": getattr(exc, "winerror", None)}
        content_write_ok = False
    finally:
        for handle in reversed(fresh_handles):
            closes.append({"kind": "fresh", **close_checked(handle)})
        for handle in reversed(held):
            closes.append({"kind": "held", **close_checked(handle)})

    result = {
        "run": str(RUN),
        "started_unix": started,
        "finished_unix": time.time(),
        "desired_access": FILE_LIST_DIRECTORY,
        "share_mode": FILE_SHARE_READ | FILE_SHARE_WRITE,
        "open_flags": FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT,
        "fixed_volume_root_excluded": "C:\\",
        "prefixes": records,
        "all_prefixes_held_simultaneously": len(held) == len(PREFIXES),
        "fresh_reopen_identity_match": all(item.get("reopen_identity_match") for item in records),
        "output_subtree_content_write_and_readback": content_write_ok,
        "close_results_reverse_order": closes,
        "failure": failure,
        "scope": "真实祖先只读打开和身份查询；没有对真实祖先执行rename、delete或内容写入。",
    }
    (RUN / "result.json").write_text(json.dumps(result, ensure_ascii=False,
                                                sort_keys=True, indent=2) + "\n",
                                     encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if failure is not None or not content_write_ok or len(records) != len(PREFIXES):
        return 1
    if not result["fresh_reopen_identity_match"]:
        return 2
    if any(not item["ok"] for item in closes):
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
