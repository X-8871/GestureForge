"""S15隔离草稿的固定待冻结项；缺少真实冻结时阻断所有收集写入。"""
import hashlib
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).parents[4]
WORK = Path(__file__).parent
SOURCE_COMMIT = None
SOURCE_FREEZE = WORK / "__PENDING_S15_SOURCE_FREEZE__"
SOURCE_FREEZE_SHA = None
FUNCTIONAL_G1 = ROOT / "__PENDING_S15_FUNCTIONAL_G1__"
FUNCTIONAL_G1_SHA = None
FUNCTIONAL_G2 = ROOT / "__PENDING_S15_FUNCTIONAL_G2__"
FUNCTIONAL_G2_SHA = None
FUNCTIONAL_G2_EXPECTED_STATUS = None
SYNTH_MANIFEST = ROOT / "__PENDING_S15_SYNTH_MANIFEST__"
SYNTH_MANIFEST_SHA = None
SYNTH_G2 = ROOT / "__PENDING_S15_SYNTH_G2__"
SYNTH_G2_SHA = None
SYNTH_G2_EXPECTED_STATUS = None
SYNTH_CACHE = WORK / "__PENDING_S15_SYNTH_CACHE__"
PNR_CACHE = WORK / "__PENDING_S15_PNR_CACHE__"
PROJECT = WORK / "__PENDING_S15_PROJECT__"
SYNTH_REPORT = ROOT / "__PENDING_S15_SYNTH_REPORT__"
PNR_REPORT = ROOT / "__PENDING_S15_PNR_REPORT__"
SOURCE_PRE = ROOT / "__PENDING_S15_SOURCE_PRE__"
GUARD = WORK / "guard.py"
GUARD_SHA = "e055276318f6e215981bdceadb437ebe2bf50ec160b8d93c2d11c33bc89f886f"
SUP = WORK / "supervisor.py"
SUP_SHA = "de7a5051687a391a7705f6bc8b54c8fb3d6a008f7423e2978d746953b6ae3968"
NATIVE_PYTHON = r"D:\Xilinx\2026.1\tps\win64\python-3.13.0\python.exe"
NATIVE_PYTHON_SHA256 = "d289b7527fe1a1e18a64da085ab50d319bcbba92ab1d58fa0ac073a1c240fc75"
ARCHIVE = ROOT / "report/evidence/S2B-T17/s15_launch_tools_20261012_r02"
MAPPING_SHA = 'f423d1fa461356876af52958d3de89005f667b54ba5a6bd9ee863daa4343cde4'
RECOVERY_SHA = '91f8de21e70521b9cf4cbc8dbe3ceabf2ca12d38ca78f27706ec5c88afcb4c0e'
TOOLS_G2 = ROOT / "__PENDING_S15_TOOLS_G2__"
TOOLS_G2_SHA = None
TOOLS_G2_EXPECTED_STATUS = None
RUNTIME_CONFIG = WORK / "runtime_pins.json"
_CONFIG_SELECTOR = os.environ.get("S15_RUNTIME_CONFIG")
if _CONFIG_SELECTOR is not None:
    RUNTIME_CONFIG = Path(_CONFIG_SELECTOR)
_LOADED_CONFIG_SHA = None
_CONFIG_FIELDS = ("SOURCE_COMMIT", "SOURCE_FREEZE", "SOURCE_FREEZE_SHA", "FUNCTIONAL_G1", "FUNCTIONAL_G1_SHA", "FUNCTIONAL_G2", "FUNCTIONAL_G2_SHA", "FUNCTIONAL_G2_EXPECTED_STATUS", "SYNTH_MANIFEST", "SYNTH_MANIFEST_SHA", "SYNTH_G2", "SYNTH_G2_SHA", "SYNTH_G2_EXPECTED_STATUS", "SYNTH_CACHE", "PNR_CACHE", "PROJECT", "SYNTH_REPORT", "PNR_REPORT", "SOURCE_PRE", "TOOLS_G2", "TOOLS_G2_SHA", "TOOLS_G2_EXPECTED_STATUS", "NATIVE_PYTHON", "NATIVE_PYTHON_SHA256")
_CONFIG_PATHS = {"SOURCE_FREEZE", "FUNCTIONAL_G1", "FUNCTIONAL_G2", "SYNTH_MANIFEST", "SYNTH_G2", "SYNTH_CACHE", "PNR_CACHE", "PROJECT", "SYNTH_REPORT", "PNR_REPORT", "SOURCE_PRE", "TOOLS_G2"}
_LOADED_HELPER_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

def require(condition, message):
    """未知项一律拒绝，不填充历史批准。"""
    if not condition:
        raise ValueError(message)

_WIN_FIND_API = None

def _windows_api_path(path):
    """为超长绝对路径添加Win32扩展前缀。"""
    value = str(path)
    if len(value) >= 260 and not value.startswith("\\\\?\\"):
        if value.startswith("\\\\"):
            return "\\\\?\\UNC\\" + value[2:]
        return "\\\\?\\" + value
    return value

def _windows_normalized_name(value):
    """去除句柄API返回的扩展命名空间前缀，保留实际大小写。"""
    if value.startswith("\\\\?\\UNC\\"):
        return "\\\\" + value[8:]
    if value.startswith("\\\\?\\"):
        return value[4:]
    return value

def _windows_kernel_api():
    """缓存无状态Win32函数绑定；失败调用仍按当前路径重新执行。"""
    global _WIN_FIND_API
    if _WIN_FIND_API is None:
        import ctypes
        from ctypes import wintypes
        class FindData(ctypes.Structure):
            _fields_ = [("attributes", wintypes.DWORD),
                        ("creation", wintypes.FILETIME),
                        ("access", wintypes.FILETIME),
                        ("write", wintypes.FILETIME),
                        ("size_high", wintypes.DWORD),
                        ("size_low", wintypes.DWORD),
                        ("reserved0", wintypes.DWORD),
                        ("reserved1", wintypes.DWORD),
                        ("filename", wintypes.WCHAR * 260),
                        ("alternate", wintypes.WCHAR * 14)]
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        find_first = kernel32.FindFirstFileW
        find_first.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(FindData)]
        find_first.restype = wintypes.HANDLE
        find_close = kernel32.FindClose
        find_close.argtypes = [wintypes.HANDLE]
        find_close.restype = wintypes.BOOL
        get_attributes = kernel32.GetFileAttributesW
        get_attributes.argtypes = [wintypes.LPCWSTR]
        get_attributes.restype = wintypes.DWORD
        create_file = kernel32.CreateFileW
        create_file.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD,
                                wintypes.HANDLE]
        create_file.restype = wintypes.HANDLE
        get_final_name = kernel32.GetFinalPathNameByHandleW
        get_final_name.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD,
                                   wintypes.DWORD]
        get_final_name.restype = wintypes.DWORD
        close_handle = kernel32.CloseHandle
        close_handle.argtypes = [wintypes.HANDLE]
        close_handle.restype = wintypes.BOOL
        _WIN_FIND_API = (ctypes, FindData, find_first, find_close, get_attributes,
                         create_file, get_final_name, close_handle)
    return _WIN_FIND_API

def _windows_find_leaf(path):
    """读取完整无通配路径所指单一目录项的原始叶名。"""
    ctypes, FindData, find_first, find_close, _, _, _, _ = _windows_kernel_api()
    data = FindData()
    handle = find_first(_windows_api_path(path), ctypes.byref(data))
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return data.filename, int(data.attributes)
    finally:
        find_close(handle)

def _windows_handle_name(path):
    """以OPEN_REPARSE_POINT读取该prefix的规范化实际大小写路径。"""
    ctypes, _, _, _, _, create_file, get_final_name, close_handle = _windows_kernel_api()
    handle = create_file(_windows_api_path(path), 0x0080, 0x00000001 | 0x00000002 | 0x00000004,
                         None, 3, 0x02000000 | 0x00200000, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        buffer = ctypes.create_unicode_buffer(32768)
        length = get_final_name(handle, buffer, len(buffer), 0)
        if not length:
            raise ctypes.WinError(ctypes.get_last_error())
        if length >= len(buffer):
            raise OSError("句柄规范化路径超出缓冲区")
        return _windows_normalized_name(buffer.value)
    finally:
        close_handle(handle)

def _windows_attributes(path):
    """逐prefix读取自身属性，属性不可读即失败关闭。"""
    import ctypes
    _, _, _, _, get_attributes, _, _, _ = _windows_kernel_api()
    value = get_attributes(_windows_api_path(path))
    if value == 0xFFFFFFFF:
        raise ctypes.WinError(ctypes.get_last_error())
    return int(value)

def windows_find_info(path):
    """逐prefix核对大小写和自身reparse属性，不枚举父目录。"""
    require(os.name == "nt", "Windows路径查询只能在Windows运行")
    path = Path(path)
    try:
        actual, find_attributes = _windows_find_leaf(path)
        require(actual == path.name, "FindFirstFileW叶名大小写不同："+str(path))
    except OSError as find_error:
        try:
            actual_path = _windows_handle_name(path)
        except OSError as handle_error:
            raise OSError("精确prefix无法核验："+str(path)+"；FindFirstFileW="+repr(find_error)+"；句柄="+repr(handle_error)) from handle_error
        expected = _windows_normalized_name(str(path))
        require(actual_path == expected, "句柄规范化prefix大小写或路径不同："+str(path))
        find_attributes = None
    attributes = _windows_attributes(path)
    if find_attributes is not None:
        require((find_attributes & (0x10 | 0x400)) == (attributes & (0x10 | 0x400)),
                "FindFirstFileW与GetFileAttributesW的目录/reparse位不同："+str(path))
    return path.name, attributes

def exact(path, directory=False):
    """逐组件核验精确路径及类型，拒绝链接。"""
    raw = os.fspath(path)
    require(type(raw) is str, "路径不是Unicode字符串")
    require(not any(component in {".", ".."} for component in re.split(r"[\\/]", raw)),
            "原始路径含点路径组件：" + raw)
    path = Path(raw)
    require(path.is_absolute(), "不是完整绝对路径")
    require(not path.drive.startswith("\\\\"), "UNC或设备命名空间路径不适用于本机C盘部署")
    current = Path(path.anchor)
    if os.name == "nt":
        attributes = None
        for name in path.parts[1:]:
            if attributes is not None:
                require(attributes & 0x10, "父目录类型错误："+str(current))
            actual, attributes = windows_find_info(current/name)
            require(actual == name, "精确大小写名称不存在："+str(path))
            require(not attributes & 0x400, "路径含重解析点："+str(current/name))
            current = current/name
        if attributes is None:
            attributes = 0x10 if current.is_dir() else 0
        is_directory = bool(attributes & 0x10)
        require(is_directory if directory else (not is_directory and not attributes & 0x40), "路径类型不同")
    else:
        for name in path.parts[1:]:
            require(name in {p.name for p in current.iterdir()}, "精确路径不存在："+str(path))
            current = current/name
            require(not current.is_symlink() and not current.is_junction(), "拒绝链接路径")
        require(current.is_dir() if directory else current.is_file(), "路径类型不同")
    return current

def pinned(path, digest):
    """哈希必须由最终冻结提供且与实际原字节相同。"""
    require(isinstance(digest, str) and re.fullmatch("[0-9a-f]{64}", digest), "BLOCKED_PENDING_S15_PINS：缺实际输入SHA")
    path = exact(path)
    require(hashlib.sha256(path.read_bytes()).hexdigest()==digest, "冻结输入漂移")
    return path


def validate_native_python_pin(path, digest):
    """只接受固定Vitis解释器路径与SHA，并逐组件拒绝别名或reparse。"""
    require(type(path) is str and path == NATIVE_PYTHON, "NATIVE_PYTHON路径不在固定白名单")
    require(type(digest) is str and digest == NATIVE_PYTHON_SHA256, "NATIVE_PYTHON_SHA256不在固定白名单")
    candidate = Path(path)
    require(str(candidate) == path and candidate.is_absolute(), "NATIVE_PYTHON路径不是精确绝对路径")
    candidate = exact(candidate)
    resolved = candidate.resolve(strict=True)
    require(str(resolved) == NATIVE_PYTHON, "NATIVE_PYTHON解析路径与固定路径不同")
    raw = candidate.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    require(actual == NATIVE_PYTHON_SHA256, "NATIVE_PYTHON文件SHA漂移")
    return dict(path=NATIVE_PYTHON, sha256=actual, bytes=len(raw))


def load_runtime_config():
    """只读严格JSON数据；缺文件继续待冻结，禁止借配置改guard/SUP或资源门槛。"""
    global _LOADED_CONFIG_SHA
    if _CONFIG_SELECTOR is not None:
        selector_path = Path(_CONFIG_SELECTOR)
        require(str(selector_path)==_CONFIG_SELECTOR and selector_path.is_absolute() and str(RUNTIME_CONFIG)==_CONFIG_SELECTOR and selector_path.parent==WORK and re.fullmatch(r"runtime_pins_(?:synth|pnr)_r[0-9]+\.json", selector_path.name), "配置选择器不是本目录精确新版本文件")
        exact(RUNTIME_CONFIG)
    if not RUNTIME_CONFIG.exists():
        return
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "配置重复键")
            result[key] = value
        return result
    raw = exact(RUNTIME_CONFIG).read_bytes()
    data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique)
    require(type(data) is dict and set(data)==set(_CONFIG_FIELDS), "配置字段缺失或超出白名单")
    require(data["NATIVE_PYTHON"] == NATIVE_PYTHON, "配置NATIVE_PYTHON与固定Vitis路径不同")
    require(data["NATIVE_PYTHON_SHA256"] == NATIVE_PYTHON_SHA256, "配置NATIVE_PYTHON_SHA256与固定Vitis散列不同")
    validate_native_python_pin(data["NATIVE_PYTHON"], data["NATIVE_PYTHON_SHA256"])
    for key, value in data.items():
        if key in {"NATIVE_PYTHON", "NATIVE_PYTHON_SHA256"}:
            continue
        if key in _CONFIG_PATHS:
            if value is None and key in {"SYNTH_MANIFEST", "SYNTH_G2"}:
                continue
            require(type(value) is str and str(Path(value))==value and Path(value).is_absolute() and all(part not in {".", ".."} for part in Path(value).parts) and Path(value).is_relative_to(ROOT), "配置路径不能含点路径、规范化别名、越界或非绝对："+key)
            globals()[key] = Path(value)
        else:
            require(value is None or type(value) is str, "配置标量类型错误："+key)
            globals()[key] = value
    _LOADED_CONFIG_SHA = hashlib.sha256(raw).hexdigest()


def runtime_config_binding():
    """实际配置原字节与本进程导入时必须一致，另由ROOT/清单绑定该SHA。"""
    require(_LOADED_CONFIG_SHA is not None and hashlib.sha256(exact(RUNTIME_CONFIG).read_bytes()).hexdigest()==_LOADED_CONFIG_SHA, "运行配置未冻结或导入后漂移")
    return dict(path=RUNTIME_CONFIG.relative_to(ROOT).as_posix(), sha256=_LOADED_CONFIG_SHA, bytes=RUNTIME_CONFIG.stat().st_size)

def require_ready(pnr=False):
    """先阻断缺失commit，再核真实G1/G2与唯一路径；不创建目录。"""
    require(hashlib.sha256(exact(Path(__file__)).read_bytes()).hexdigest()==_LOADED_HELPER_SHA, "冻结门禁代码在导入后漂移")
    runtime_config_binding()
    validate_native_python_pin(NATIVE_PYTHON, NATIVE_PYTHON_SHA256)
    require(isinstance(SOURCE_COMMIT, str) and re.fullmatch("[0-9a-f]{40}", SOURCE_COMMIT), "BLOCKED_PENDING_S15_PINS：缺ROOT最终commit/实际源码冻结/RunIds/功能G2")
    for path in (SYNTH_CACHE, PNR_CACHE, PROJECT, SYNTH_REPORT, PNR_REPORT, SOURCE_PRE):
        require("__PENDING_" not in str(path) and path.is_absolute() and path.is_relative_to(ROOT), "BLOCKED_PENDING_S15_PINS：缺实际唯一RunId")
    require(len({str(path) for path in (SYNTH_CACHE, PNR_CACHE, PROJECT, SYNTH_REPORT, PNR_REPORT, SOURCE_PRE)})==6, "RunId落点重复")
    pinned(SOURCE_FREEZE, SOURCE_FREEZE_SHA)
    freeze=json.loads(SOURCE_FREEZE.read_text(encoding="utf-8"))
    require(freeze.get("source_commit")==SOURCE_COMMIT and freeze.get("profile")=="s2b-inference-platform/0.1.15","本轮SOURCE/profile冻结不同")
    pinned(FUNCTIONAL_G1, FUNCTIONAL_G1_SHA)
    review=json.loads(pinned(FUNCTIONAL_G2, FUNCTIONAL_G2_SHA).read_text(encoding="utf-8"))
    require(isinstance(FUNCTIONAL_G2_EXPECTED_STATUS, str) and FUNCTIONAL_G2_EXPECTED_STATUS.startswith("PASS") and review.get("status")==FUNCTIONAL_G2_EXPECTED_STATUS, "功能G2未绑定实际PASS原件")
    review=json.loads(pinned(TOOLS_G2, TOOLS_G2_SHA).read_text(encoding="utf-8"))
    require(isinstance(TOOLS_G2_EXPECTED_STATUS, str) and TOOLS_G2_EXPECTED_STATUS.startswith("PASS") and review.get("status")==TOOLS_G2_EXPECTED_STATUS, "S15新guard/SUP/consumer工具G2未冻结")
    if pnr:
        pinned(SYNTH_MANIFEST, SYNTH_MANIFEST_SHA)
        review=json.loads(pinned(SYNTH_G2, SYNTH_G2_SHA).read_text(encoding="utf-8"))
        require(isinstance(SYNTH_G2_EXPECTED_STATUS, str) and SYNTH_G2_EXPECTED_STATUS.startswith("PASS") and review.get("status")==SYNTH_G2_EXPECTED_STATUS, "综合G2未绑定实际PASS原件")
    resolve_permanent(GUARD, GUARD_SHA)
    resolve_permanent(SUP, SUP_SHA)

def resolve_permanent(original, expected=None):
    """只读取正式去重映射，核对固定原恢复路径、对象SHA；绝不恢复或覆盖。"""
    original=exact(original)
    digest=hashlib.sha256(original.read_bytes()).hexdigest()
    if expected is not None:
        require(digest==expected, "固定工具输入漂移")
    mapping=json.loads(pinned(ARCHIVE/"archive_mapping.json", MAPPING_SHA).read_text(encoding="utf-8"))
    recovery=json.loads(pinned(ARCHIVE/"recovery_entry.json", RECOVERY_SHA).read_text(encoding="utf-8"))
    require(recovery["fixed_project_root"]==str(ROOT), "恢复根目录不同")
    require(recovery["fixed_guard_sha256"]==GUARD_SHA and recovery["fixed_supervisor_sha256"]==SUP_SHA, "恢复固定工具SHA不同")
    if original in (GUARD, SUP):
        required=GUARD_SHA if original==GUARD else SUP_SHA
        require(digest==required, "固定guard/sup不可重pin")
        tools=[row for row in recovery["tool_files"] if row["destination_absolute_path"]==str(original) and row["sha256"]==required]
        require(len(tools)==1, "原绝对恢复目标不唯一或漂移")
    rows=[row for row in mapping["binding_rows"] if row["original_absolute_path"]==str(original) and row["sha256"]==digest]
    require(bool(rows), "正式映射缺少原路径与原SHA")
    saved={row["archived_repo_path"] for row in rows}
    require(len(saved)==1, "归档映射对象不唯一")
    artifact=pinned(ROOT/next(iter(saved)), digest)
    require(artifact.is_relative_to(ARCHIVE), "永久对象不在工具正式包")
    if original in (GUARD, SUP):
        require(tools[0]["artifact_repo_path"]==artifact.relative_to(ROOT).as_posix(), "恢复入口与映射对象不同")
    return dict(path=artifact.relative_to(ROOT).as_posix(), sha256=digest, bytes=artifact.stat().st_size)


load_runtime_config()
