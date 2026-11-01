"""验证 FILE_LIST_DIRECTORY 只读句柄能否稳定锁定隔离目录祖先链。"""

from __future__ import annotations

import ctypes
import json
import os
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent / "readonly_chain_probe_20261013_a3"
if ROOT.exists():
    raise RuntimeError(f"精确目标已经存在，拒绝覆盖：{ROOT}")
ROOT.mkdir()

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
CreateFileW = kernel32.CreateFileW
CreateFileW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.c_void_p]
CreateFileW.restype = ctypes.c_void_p
CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [ctypes.c_void_p]
CloseHandle.restype = ctypes.c_int

FILE_LIST_DIRECTORY = 0x0001
FILE_SHARE_READ = 0x0001
FILE_SHARE_WRITE = 0x0002
OPEN_EXISTING = 3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


def open_directory(path: Path) -> int:
    """以只列目录权限、拒绝共享删除的方式打开一个目录。"""
    ctypes.set_last_error(0)
    handle = CreateFileW(str(path), FILE_LIST_DIRECTORY,
                         FILE_SHARE_READ | FILE_SHARE_WRITE, None,
                         OPEN_EXISTING,
                         FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT,
                         None)
    if handle in (None, INVALID_HANDLE_VALUE):
        raise OSError(ctypes.get_last_error(), f"CreateFileW 失败：{path}")
    return int(handle)


def close_handle(handle: int) -> tuple[bool, int]:
    """关闭句柄并立即记录 Win32 错误码。"""
    ctypes.set_last_error(0)
    ok = bool(CloseHandle(ctypes.c_void_p(handle)))
    return ok, 0 if ok else ctypes.get_last_error()


def one_case(component: str, index: int) -> dict[str, object]:
    """在独立新树里锁住从 Users 到目标组件的完整前缀。"""
    base = ROOT / f"case_{component}"
    names = ["Users", "profile", "repo"]
    paths: list[Path] = []
    cursor = base
    for name in names:
        cursor = cursor / name
        cursor.mkdir(parents=True, exist_ok=True)
        paths.append(cursor)

    handles: list[int] = []
    opened_paths: list[str] = []
    closes: list[dict[str, object]] = []
    try:
        for prefix in paths[:index + 1]:
            handles.append(open_directory(prefix))
            opened_paths.append(str(prefix))

        target = paths[index]
        moved = target.with_name(target.name + "_moved")
        attempt = {"state": "not-attempted", "winerror": None}
        try:
            os.rename(target, moved)
            attempt["state"] = "renamed"
        except OSError as exc:
            attempt["state"] = "blocked"
            attempt["winerror"] = getattr(exc, "winerror", None)

        # 租约持有期间，在最终目录写入普通输出文件，模拟 bitgen 产物写入。
        output = paths[-1] / "bitgen_output_fixture.bin"
        output.write_bytes(b"lease-write-probe\x00")
        write_ok = output.read_bytes() == b"lease-write-probe\x00"

        source_exists_held = target.exists()
        moved_exists_held = moved.exists()
    finally:
        for handle in reversed(handles):
            ok, err = close_handle(handle)
            closes.append({"ok": ok, "winerror": err})

    after = {"state": "not-attempted", "winerror": None}
    restored = {"state": "not-attempted", "winerror": None}
    try:
        os.rename(target, moved)
        after["state"] = "renamed"
        os.rename(moved, target)
        restored["state"] = "restored"
    except OSError as exc:
        after["state"] = "failed"
        after["winerror"] = getattr(exc, "winerror", None)
        if moved.exists() and not target.exists():
            try:
                os.rename(moved, target)
                restored["state"] = "restored-after-failure"
            except OSError as restore_exc:
                restored["state"] = "failed"
                restored["winerror"] = getattr(restore_exc, "winerror", None)

    return {
        "component": component,
        "prefix_paths_opened": opened_paths,
        "open_count": len(handles),
        "held_rename": attempt,
        "source_exists_while_held": source_exists_held,
        "moved_exists_while_held": moved_exists_held,
        "content_write_and_readback": write_ok,
        "handle_closes_reverse_order": closes,
        "rename_after_release": after,
        "restore": restored,
        "target_exists_after_restore": target.exists(),
        "moved_exists_after_restore": moved.exists(),
    }


def main() -> int:
    started = time.time()
    cases = [one_case("c_users", 0), one_case("profile", 1),
             one_case("repo", 2)]
    result = {
        "run": str(ROOT),
        "started_unix": started,
        "finished_unix": time.time(),
        "desired_access": FILE_LIST_DIRECTORY,
        "share_mode": FILE_SHARE_READ | FILE_SHARE_WRITE,
        "open_flags": FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT,
        "cases": cases,
        "scope": "所有改名和内容写入均限于本脚本创建的独立隔离树。",
    }
    out = ROOT / "result.json"
    out.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True,
                              indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    for case in cases:
        if case["held_rename"]["state"] != "blocked":
            return 1
        if case["held_rename"]["winerror"] != 32:
            return 2
        if not case["source_exists_while_held"] or case["moved_exists_while_held"]:
            return 3
        if not case["content_write_and_readback"]:
            return 4
        if any(not item["ok"] for item in case["handle_closes_reverse_order"]):
            return 5
        if case["rename_after_release"]["state"] != "renamed":
            return 6
        if case["restore"]["state"] != "restored":
            return 7
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
