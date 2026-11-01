"""验证完整本地目录祖先链的DELETE-deny句柄与内容写入兼容性。"""

from __future__ import annotations

import ctypes
import json
import os
from ctypes import wintypes
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUN = ROOT / "ancestor_chain_probe_20261013_a1"
SANDBOX = RUN / "sandbox"
LEVEL_A = SANDBOX / "a"
LEVEL_B = LEVEL_A / "b"
OUTPUT = LEVEL_B / "output"
CHILD = OUTPUT / "write-test.bin"
DELETE = 0x00010000
FILE_READ_ATTRIBUTES = 0x0080
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400
ERROR_SHARING_VIOLATION = 32
ERROR_ACCESS_DENIED = 5


class FileTime(ctypes.Structure):
    _fields_ = [("low", wintypes.DWORD), ("high", wintypes.DWORD)]


class ByHandleInfo(ctypes.Structure):
    _fields_ = [
        ("attributes", wintypes.DWORD),
        ("creation", FileTime),
        ("access", FileTime),
        ("write", FileTime),
        ("volume", wintypes.DWORD),
        ("size_high", wintypes.DWORD),
        ("size_low", wintypes.DWORD),
        ("links", wintypes.DWORD),
        ("index_high", wintypes.DWORD),
        ("index_low", wintypes.DWORD),
    ]


def _prefixes(path: Path) -> list[Path]:
    parts = path.parts
    if not parts or not parts[0].endswith("\\"):
        raise RuntimeError(f"不是本地绝对DOS路径：{path}")
    result = [Path(parts[0])]
    current = result[0]
    for part in parts[1:]:
        current = current / part
        result.append(current)
    return result


def main() -> int:
    if os.name != "nt":
        raise RuntimeError("该探针只支持Windows")
    if RUN.exists() or RUN.is_symlink():
        raise RuntimeError(f"隔离探针路径已存在：{RUN}")
    RUN.mkdir()
    OUTPUT.mkdir(parents=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create_file = kernel32.CreateFileW
    create_file.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                            wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD,
                            wintypes.HANDLE]
    create_file.restype = wintypes.HANDLE
    get_info = kernel32.GetFileInformationByHandle
    get_info.argtypes = [wintypes.HANDLE, ctypes.POINTER(ByHandleInfo)]
    get_info.restype = wintypes.BOOL
    final_path = kernel32.GetFinalPathNameByHandleW
    final_path.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
    final_path.restype = wintypes.DWORD
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = [wintypes.HANDLE]
    close_handle.restype = wintypes.BOOL
    invalid = wintypes.HANDLE(-1).value
    handles: list[tuple[Path, int, dict]] = []
    state: dict[str, object] = {
        "run": str(RUN),
        "share_mode": FILE_SHARE_READ | FILE_SHARE_WRITE,
        "desired_access": DELETE | FILE_READ_ATTRIBUTES,
        "open_prefixes": [],
        "open_failure": None,
        "rename_attempts": [],
        "delete_attempt": None,
    }
    try:
        for prefix in _prefixes(OUTPUT):
            handle = create_file(
                str(prefix), DELETE | FILE_READ_ATTRIBUTES,
                FILE_SHARE_READ | FILE_SHARE_WRITE, None, OPEN_EXISTING,
                FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT, None,
            )
            if not handle or handle == invalid:
                state["open_failure"] = {"path": str(prefix), "winerror": ctypes.get_last_error()}
                break
            info = ByHandleInfo()
            if not get_info(handle, ctypes.byref(info)):
                error = ctypes.get_last_error()
                close_handle(handle)
                state["open_failure"] = {"path": str(prefix), "winerror": error, "stage": "GetFileInformationByHandle"}
                break
            identity = {
                "attributes": int(info.attributes),
                "volume_serial": int(info.volume),
                "file_index": (int(info.index_high) << 32) | int(info.index_low),
            }
            buf = ctypes.create_unicode_buffer(32768)
            length = final_path(handle, buf, len(buf), 0)
            if not length or length >= len(buf):
                error = ctypes.get_last_error()
                close_handle(handle)
                state["open_failure"] = {"path": str(prefix), "winerror": error, "stage": "GetFinalPathNameByHandleW"}
                break
            identity["final_path"] = buf.value
            if info.attributes & FILE_ATTRIBUTE_REPARSE_POINT:
                close_handle(handle)
                state["open_failure"] = {"path": str(prefix), "reason": "reparse-point"}
                break
            handles.append((prefix, handle, identity))
            state["open_prefixes"].append({"path": str(prefix), **identity})

        if state["open_failure"] is None:
            CHILD.write_bytes(b"written while all ancestor pins held")
            for source in (LEVEL_A, LEVEL_B, OUTPUT):
                destination = source.with_name(source.name + "_renamed")
                try:
                    os.rename(source, destination)
                    status, error = "renamed", None
                except OSError as exc:
                    error = getattr(exc, "winerror", None)
                    status = "blocked" if error in (ERROR_ACCESS_DENIED, ERROR_SHARING_VIOLATION) else "error"
                state["rename_attempts"].append({
                    "source": str(source), "destination": str(destination),
                    "status": status, "winerror": error,
                    "source_exists": source.exists(), "destination_exists": destination.exists(),
                })
            CHILD.unlink()
            try:
                os.rmdir(OUTPUT)
                status, error = "removed", None
            except OSError as exc:
                error = getattr(exc, "winerror", None)
                status = "blocked" if error in (ERROR_ACCESS_DENIED, ERROR_SHARING_VIOLATION) else "error"
            state["delete_attempt"] = {"path": str(OUTPUT), "status": status, "winerror": error, "exists": OUTPUT.exists()}
    finally:
        close_results = []
        for prefix, handle, identity in reversed(handles):
            ok = bool(close_handle(handle))
            close_error = 0 if ok else ctypes.get_last_error()
            close_results.append({"path": str(prefix), "ok": ok, "winerror": close_error})
        state["close_results"] = close_results
        state["all_handles_closed"] = all(item["ok"] for item in close_results)

    rename_after = None
    if state["open_failure"] is None and state["all_handles_closed"]:
        try:
            os.rename(OUTPUT, OUTPUT.with_name("output_after_release"))
            rename_after = "renamed"
        except OSError as exc:
            rename_after = {"error": repr(exc), "winerror": getattr(exc, "winerror", None)}
    state["rename_after_release"] = rename_after
    result_path = RUN / "result.json"
    result_path.write_text(json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, sort_keys=True))
    if state["open_failure"] is not None or not state["all_handles_closed"]:
        return 2
    if not CHILD.exists() and any(item["status"] != "blocked" for item in state["rename_attempts"]):
        return 3
    if any(item["status"] != "blocked" for item in state["rename_attempts"]):
        return 4
    if state["delete_attempt"]["status"] != "blocked" or rename_after != "renamed":
        return 5
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
