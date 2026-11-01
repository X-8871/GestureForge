"""逐路径前缀只读探测DELETE-deny目录句柄权限。"""

from __future__ import annotations

import ctypes
import json
import os
from ctypes import wintypes
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RUN = ROOT / "prefix_access_probe_20261013_a1"
DELETE = 0x00010000
FILE_READ_ATTRIBUTES = 0x0080
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000


def main() -> int:
    if os.name != "nt":
        raise RuntimeError("该探针只支持Windows")
    if RUN.exists() or RUN.is_symlink():
        raise RuntimeError(f"隔离探针路径已存在：{RUN}")
    RUN.mkdir()
    target = RUN / "probe-target"
    target.mkdir()
    path = target.resolve(strict=True)
    parts = path.parts
    if not parts or not parts[0].endswith("\\"):
        raise RuntimeError(f"不是本地DOS绝对路径：{path}")
    prefixes = [Path(parts[0])]
    current = prefixes[0]
    for part in parts[1:]:
        current = current / part
        prefixes.append(current)

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create_file = kernel32.CreateFileW
    create_file.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                            wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD,
                            wintypes.HANDLE]
    create_file.restype = wintypes.HANDLE
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = [wintypes.HANDLE]
    close_handle.restype = wintypes.BOOL
    invalid = wintypes.HANDLE(-1).value
    results = []
    # 卷根固定，不尝试给C:\申请DELETE权限；逐个核对其余实际组件。
    for prefix in prefixes[1:]:
        handle = create_file(
            str(prefix), DELETE | FILE_READ_ATTRIBUTES,
            FILE_SHARE_READ | FILE_SHARE_WRITE, None, OPEN_EXISTING,
            FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT, None,
        )
        if not handle or handle == invalid:
            results.append({"path": str(prefix), "opened": False, "winerror": ctypes.get_last_error()})
            continue
        ok = bool(close_handle(handle))
        results.append({"path": str(prefix), "opened": True,
                        "close_ok": ok, "close_winerror": 0 if ok else ctypes.get_last_error()})
    state = {"run": str(RUN), "fixed_volume_root": str(prefixes[0]), "results": results}
    (RUN / "result.json").write_text(json.dumps(state, ensure_ascii=False,
                                                sort_keys=True, indent=2) + "\n",
                                     encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, sort_keys=True))
    if any(not item["opened"] or not item["close_ok"] for item in results):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
