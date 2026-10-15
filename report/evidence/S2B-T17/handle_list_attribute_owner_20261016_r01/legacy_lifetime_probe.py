"""只读复现HEAD版本的HANDLE_LIST值数组所有权，不创建进程。"""
import ctypes
import gc
import subprocess
import types
import weakref


source = subprocess.check_output(
    ["git", "show", "HEAD:verification/s15_job_guard.py"],
    text=True,
    encoding="utf-8",
)
legacy = types.ModuleType("s15_job_guard_legacy_lifetime_probe")
legacy.__file__ = "HEAD:verification/s15_job_guard.py"
exec(compile(source, legacy.__file__, "exec"), legacy.__dict__)

handles = (0x101, 0x202, 0x303)
expected_size = len(handles) * ctypes.sizeof(legacy.wintypes.HANDLE)
captured = {}
original_cast = ctypes.cast
original_update = legacy.kernel32.UpdateProcThreadAttribute


def capture_cast(value, target):
    if (
        isinstance(value, ctypes.Array)
        and getattr(type(value), "_type_", None) == legacy.wintypes.HANDLE
        and ctypes.sizeof(value) == expected_size
    ):
        captured["owner_ref"] = weakref.ref(value)
        captured["address"] = ctypes.addressof(value)
        captured["array_type"] = type(value).__name__
    return original_cast(value, target)


def update_attribute(pointer, flags, attribute, value, size, previous, returned_size):
    captured["attribute_value_address"] = int(value.value or 0)
    captured["value_size"] = int(size)
    return True


legacy.ctypes.cast = capture_cast
legacy.kernel32.UpdateProcThreadAttribute = update_attribute
try:
    attribute_buffer, attribute_pointer = legacy._initialize_handle_list(handles)
finally:
    legacy.ctypes.cast = original_cast
    legacy.kernel32.UpdateProcThreadAttribute = original_update

gc.collect()
owner_ref = captured["owner_ref"]
print("baseline_commit=", subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip())
print("array_type=", captured["array_type"])
print("array_address=", hex(captured["address"]))
print("attribute_value_address=", hex(captured["attribute_value_address"]))
print("captured_size=", captured["value_size"])
print("weakref_alive_after_return_gc=", owner_ref() is not None)

reused = False
observed = None
handle_array_type = legacy.wintypes.HANDLE * len(handles)
for index in range(200000):
    candidate = handle_array_type(0xA000 + index, 0xB000 + index, 0xC000 + index)
    if ctypes.addressof(candidate) == captured["address"]:
        reused = True
        observed = tuple(int(value or 0) for value in candidate)
        break
print("same_size_address_reused=", reused)
print("reused_values=", tuple(hex(value) for value in observed) if observed is not None else "unavailable")
legacy._close_attribute_list(attribute_buffer, attribute_pointer)
