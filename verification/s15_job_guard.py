"""仅用于 S15 Job Object 门禁候选和隔离 fixture。"""
import ctypes
import json
import math
import os
import secrets
import struct
import subprocess
import time
from ctypes import wintypes

import psutil


if os.name != "nt":
    raise RuntimeError("Job Object 候选仅支持 Windows")


JOB_OBJECT_QUERY = 0x0004
JOB_OBJECT_SET_ATTRIBUTES = 0x0010
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION = 1
JOB_OBJECT_BASIC_PROCESS_ID_LIST = 3
PROCESS_TERMINATE = 0x0001
PROCESS_CREATE_PROCESS = 0x0080
PROCESS_VM_READ = 0x0010
PROCESS_SET_QUOTA = 0x0100
PROCESS_QUERY_INFORMATION = 0x0400
SYNCHRONIZE = 0x00100000
TH32CS_SNAPPROCESS = 0x00000002
ERROR_NO_MORE_FILES = 18
ERROR_MORE_DATA = 234
STILL_ACTIVE = 259
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 258
CREATE_SUSPENDED = 0x00000004
EXTENDED_STARTUPINFO_PRESENT = 0x00080000
CREATE_UNICODE_ENVIRONMENT = 0x00000400
STARTF_USESTDHANDLES = 0x00000100
PROC_THREAD_ATTRIBUTE_HANDLE_LIST = 0x00020002
ERROR_INSUFFICIENT_BUFFER = 122
ERROR_ACCESS_DENIED = 5
MAX_PID_LIST = 4096
RSS_LIMIT_BYTES = 6 * 1024 * 1024 * 1024
RAM_FLOOR_BYTES = 512 * 1024 * 1024
DISK_FLOOR_BYTES = 8 * 1024 * 1024 * 1024
SAMPLE_GAP_LIMIT_SECONDS = 1.0
SUPERVISOR_HANDOFF_LIMIT_SECONDS = 5.0
CONSUMER_FRESHNESS_LIMIT_SECONDS = 10.0
NO_PROGRESS_LIMIT_SECONDS = 900.0
ROSS_IDENTITY_FIELDS = ("pid", "create_time", "exe", "cwd", "cmdline", "ppid")


class JobGuardError(RuntimeError):
    """Job API、身份或预算不能证明时停止门禁。"""


class GateBlocked(JobGuardError):
    """READY 前置条件未能证明。"""


class _ReadyToken:
    """绑定当前Job实例的一次性READY能力对象。"""

    __slots__ = ("owner", "nonce", "receipt")

    def __init__(self, owner, nonce, receipt):
        self.owner = owner
        self.nonce = nonce
        self.receipt = receipt


class FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]


class BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_ulonglong),
        ("WriteOperationCount", ctypes.c_ulonglong),
        ("OtherOperationCount", ctypes.c_ulonglong),
        ("ReadTransferCount", ctypes.c_ulonglong),
        ("WriteTransferCount", ctypes.c_ulonglong),
        ("OtherTransferCount", ctypes.c_ulonglong),
    ]


class EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", BASIC_LIMIT_INFORMATION),
        ("IoInfo", IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


class BASIC_ACCOUNTING_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("TotalUserTime", ctypes.c_longlong),
        ("TotalKernelTime", ctypes.c_longlong),
        ("ThisPeriodTotalUserTime", ctypes.c_longlong),
        ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
        ("TotalPageFaultCount", wintypes.DWORD),
        ("TotalProcesses", wintypes.DWORD),
        ("ActiveProcesses", wintypes.DWORD),
        ("TotalTerminatedProcesses", wintypes.DWORD),
    ]


class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_size_t),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", wintypes.WCHAR * 260),
    ]


class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("nLength", wintypes.DWORD),
        ("lpSecurityDescriptor", ctypes.c_void_p),
        ("bInheritHandle", wintypes.BOOL),
    ]


class STARTUPINFOW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", ctypes.POINTER(ctypes.c_ubyte)),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    ]


class STARTUPINFOEXW(ctypes.Structure):
    _fields_ = [("StartupInfo", STARTUPINFOW), ("lpAttributeList", ctypes.c_void_p)]


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    ]


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
psapi = ctypes.WinDLL("psapi", use_last_error=True)
kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
kernel32.CreateJobObjectW.restype = wintypes.HANDLE
kernel32.CreateProcessW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.LPWSTR,
    ctypes.c_void_p,
    ctypes.c_void_p,
    wintypes.BOOL,
    wintypes.DWORD,
    ctypes.c_void_p,
    wintypes.LPCWSTR,
    ctypes.c_void_p,
    ctypes.POINTER(PROCESS_INFORMATION),
]
kernel32.CreateProcessW.restype = wintypes.BOOL
kernel32.ResumeThread.argtypes = [wintypes.HANDLE]
kernel32.ResumeThread.restype = wintypes.DWORD
kernel32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
kernel32.TerminateProcess.restype = wintypes.BOOL
kernel32.InitializeProcThreadAttributeList.argtypes = [ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(ctypes.c_size_t)]
kernel32.InitializeProcThreadAttributeList.restype = wintypes.BOOL
kernel32.UpdateProcThreadAttribute.argtypes = [ctypes.c_void_p, wintypes.DWORD, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p]
kernel32.UpdateProcThreadAttribute.restype = wintypes.BOOL
kernel32.DeleteProcThreadAttributeList.argtypes = [ctypes.c_void_p]
kernel32.DeleteProcThreadAttributeList.restype = None
kernel32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
kernel32.SetInformationJobObject.restype = wintypes.BOOL
kernel32.QueryInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
kernel32.QueryInformationJobObject.restype = wintypes.BOOL
kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
kernel32.IsProcessInJob.argtypes = [wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)]
kernel32.IsProcessInJob.restype = wintypes.BOOL
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
kernel32.WaitForSingleObject.restype = wintypes.DWORD
kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
kernel32.GetExitCodeProcess.restype = wintypes.BOOL
kernel32.GetProcessTimes.argtypes = [wintypes.HANDLE, ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME), ctypes.POINTER(FILETIME)]
kernel32.GetProcessTimes.restype = wintypes.BOOL
kernel32.GetProcessId.argtypes = [wintypes.HANDLE]
kernel32.GetProcessId.restype = wintypes.DWORD
kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
kernel32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
kernel32.Process32FirstW.restype = wintypes.BOOL
kernel32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
kernel32.Process32NextW.restype = wintypes.BOOL
kernel32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
kernel32.TerminateJobObject.restype = wintypes.BOOL
kernel32.GlobalMemoryStatusEx.argtypes = [ctypes.c_void_p]
kernel32.GlobalMemoryStatusEx.restype = wintypes.BOOL
kernel32.GetDiskFreeSpaceExW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_ulonglong), ctypes.POINTER(ctypes.c_ulonglong), ctypes.POINTER(ctypes.c_ulonglong)]
kernel32.GetDiskFreeSpaceExW.restype = wintypes.BOOL
psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS), wintypes.DWORD]
psapi.GetProcessMemoryInfo.restype = wintypes.BOOL


def _win_error(operation):
    code = ctypes.get_last_error()
    return JobGuardError(f"{operation} 失败：WinError {code}")


def _filetime_value(value):
    return (int(value.dwHighDateTime) << 32) | int(value.dwLowDateTime)


def process_creation_ticks(handle):
    created, exited, kernel, user = FILETIME(), FILETIME(), FILETIME(), FILETIME()
    if not kernel32.GetProcessTimes(handle, ctypes.byref(created), ctypes.byref(exited), ctypes.byref(kernel), ctypes.byref(user)):
        raise _win_error("GetProcessTimes")
    return _filetime_value(created)


def process_identity(pid):
    """双读六字段；PID出生时间变化、权限错误和字段缺失均拒绝。"""
    try:
        first = psutil.Process(int(pid))
        with first.oneshot():
            identity = {
                "pid": first.pid,
                "create_time": first.create_time(),
                "exe": first.exe(),
                "cwd": first.cwd(),
                "cmdline": first.cmdline(),
                "ppid": first.ppid(),
            }
        second = psutil.Process(int(pid))
        if second.create_time() != identity["create_time"] or second.ppid() != identity["ppid"]:
            raise GateBlocked("六字段读回期间进程身份或父PID变化")
        if not identity["exe"] or not identity["cwd"] or not identity["cmdline"]:
            raise GateBlocked("六字段有空值")
        return identity
    except (psutil.Error, OSError, ValueError) as error:
        raise GateBlocked(f"六字段无法读取：{error!r}") from error


def _open_process(pid, access):
    handle = kernel32.OpenProcess(access, False, int(pid))
    if not handle:
        raise _win_error(f"OpenProcess(pid={pid})")
    return handle


def _api_open_process(pid, access):
    """为身份竞态回归提供可替换的WinAPI入口。"""
    return _open_process(pid, access)


def _api_process_id(handle):
    """从已打开的进程句柄读回不可复用的当前PID绑定。"""
    value = int(kernel32.GetProcessId(handle))
    if value <= 0:
        raise _win_error("GetProcessId")
    return value


def _api_creation_ticks(handle):
    return process_creation_ticks(handle)


def _api_process_identity(pid):
    return process_identity(pid)


def _api_assign_process(job_handle, process_handle):
    return bool(kernel32.AssignProcessToJobObject(job_handle, process_handle))


def _api_is_process_in_job(process_handle, job_handle):
    return _is_in_job(process_handle, job_handle)


def _api_close_handle(handle):
    return bool(kernel32.CloseHandle(handle))


def _api_create_process(application, command_line, cwd, startup, startup_ex, inherited_handles, environment_block=None):
    """直接调用CreateProcessW；此处不经过shell或subprocess。"""
    info = PROCESS_INFORMATION()
    if startup_ex is None:
        startup_pointer = ctypes.cast(ctypes.byref(startup), ctypes.c_void_p)
        flags = CREATE_SUSPENDED
    else:
        startup_pointer = ctypes.cast(ctypes.byref(startup_ex), ctypes.c_void_p)
        flags = CREATE_SUSPENDED | EXTENDED_STARTUPINFO_PRESENT
    environment_pointer = None
    if environment_block is not None:
        flags |= CREATE_UNICODE_ENVIRONMENT
        environment_pointer = ctypes.cast(environment_block, ctypes.c_void_p)
    command_buffer = ctypes.create_unicode_buffer(command_line)
    ok = kernel32.CreateProcessW(
        application,
        command_buffer,
        None,
        None,
        bool(inherited_handles),
        flags,
        environment_pointer,
        cwd,
        startup_pointer,
        ctypes.byref(info),
    )
    if not ok:
        raise _win_error("CreateProcessW(CREATE_SUSPENDED)")
    return info


def _api_resume_thread(handle):
    return int(kernel32.ResumeThread(handle))


def _api_terminate_process(handle, exit_code):
    return bool(kernel32.TerminateProcess(handle, int(exit_code)))


def _api_wait(handle, milliseconds):
    return int(kernel32.WaitForSingleObject(handle, int(milliseconds)))


def _api_get_exit_code(handle):
    value = wintypes.DWORD()
    if not kernel32.GetExitCodeProcess(handle, ctypes.byref(value)):
        raise _win_error("GetExitCodeProcess")
    return int(value.value)


def _api_process_snapshot():
    """创建Toolhelp进程快照，供故障注入测试替换。"""
    return kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)


def _api_process32_first(snapshot, entry):
    """读取快照首项，供故障注入测试替换。"""
    return bool(kernel32.Process32FirstW(snapshot, ctypes.byref(entry)))


def _api_process32_next(snapshot, entry):
    """读取快照下一项，供故障注入测试替换。"""
    return bool(kernel32.Process32NextW(snapshot, ctypes.byref(entry)))


def _checked_close_handle(handle, operation):
    if handle and not _api_close_handle(handle):
        raise _win_error(f"CloseHandle({operation})")


def _filetime_to_unix_seconds(ticks):
    return (int(ticks) - 116444736000000000) / 10000000.0


def _assert_handle_identity(handle, pid, birth_ticks, identity):
    """逐次证明PID、FILETIME出生时刻和独立六字段读取属于同一句柄。"""
    handle_pid = _api_process_id(handle)
    if handle_pid != int(pid) or identity.get("pid") != int(pid):
        raise GateBlocked(f"进程HANDLE PID绑定漂移：requested={pid}, handle={handle_pid}, identity={identity.get('pid')}")
    before_ticks = _api_creation_ticks(handle)
    if before_ticks != int(birth_ticks):
        raise GateBlocked("进程HANDLE FILETIME出生时刻漂移")
    handle_created = _filetime_to_unix_seconds(before_ticks)
    try:
        identity_created = float(identity["create_time"])
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise GateBlocked(f"独立六字段缺少有效create_time：{error!r}") from error
    if not math.isfinite(identity_created) or abs(identity_created - handle_created) > 0.0001:
        raise GateBlocked("独立六字段create_time与HANDLE FILETIME不一致")
    reread = _api_process_identity(handle_pid)
    if not _identity_equal(identity, reread):
        raise GateBlocked("独立六字段身份在HANDLE绑定期间发生变化")
    after_pid = _api_process_id(handle)
    after_ticks = _api_creation_ticks(handle)
    if after_pid != handle_pid or after_ticks != before_ticks:
        raise GateBlocked("进程HANDLE PID/FILETIME在身份复读期间发生变化")


def _is_in_job(process_handle, job_handle):
    answer = wintypes.BOOL()
    if not kernel32.IsProcessInJob(process_handle, job_handle, ctypes.byref(answer)):
        raise _win_error("IsProcessInJob")
    return bool(answer.value)


def process_table():
    """Toolhelp单快照读取PID及父PID；API失败不降级到推测。"""
    snapshot = _api_process_snapshot()
    invalid = ctypes.c_void_p(-1).value
    if not snapshot or snapshot == invalid:
        raise _win_error("CreateToolhelp32Snapshot")
    rows = {}
    primary_error = None
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(entry)
        if not _api_process32_first(snapshot, entry):
            raise _win_error("Process32FirstW")
        while True:
            pid = int(entry.th32ProcessID)
            if pid:
                rows[pid] = int(entry.th32ParentProcessID)
            entry.dwSize = ctypes.sizeof(entry)
            if not _api_process32_next(snapshot, entry):
                code = ctypes.get_last_error()
                if code == ERROR_NO_MORE_FILES:
                    break
                ctypes.set_last_error(code)
                raise _win_error("Process32NextW")
    except BaseException as error:
        primary_error = error
        raise
    finally:
        try:
            _checked_close_handle(snapshot, "Toolhelp process snapshot")
        except BaseException as close_error:
            if primary_error is None:
                raise
            raise GateBlocked(
                "Toolhelp快照处理失败且句柄清理也失败；"
                f"主错误={primary_error!r}；CloseHandle错误={close_error!r}"
            ) from primary_error
    return rows


def descendants(root_pid):
    table = process_table()
    if root_pid not in table:
        raise GateBlocked("Toolhelp快照中缺少root PID")
    children = {}
    for pid, parent in table.items():
        children.setdefault(parent, []).append(pid)
    found, queue = set(), [root_pid]
    while queue:
        parent = queue.pop(0)
        for child in children.get(parent, []):
            if child in found or child == root_pid:
                raise GateBlocked("Toolhelp进程父子关系成环或PID重复")
            found.add(child)
            queue.append(child)
    return found


def _open_process_identity_handle(pid, access):
    handle = _api_open_process(pid, access)
    try:
        handle_pid = _api_process_id(handle)
        if handle_pid != int(pid):
            raise GateBlocked(f"OpenProcess返回的HANDLE属于其他PID：requested={pid}, actual={handle_pid}")
        ticks = _api_creation_ticks(handle)
        identity = _api_process_identity(handle_pid)
        _assert_handle_identity(handle, pid, ticks, identity)
        return handle, ticks, identity
    except BaseException as primary:
        try:
            _checked_close_handle(handle, "未绑定进程句柄")
        except BaseException as cleanup:
            raise GateBlocked(f"进程身份核验失败：{primary!r}；关闭未绑定HANDLE也失败：{cleanup!r}") from primary
        raise


def _memory_status():
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", wintypes.DWORD),
            ("dwMemoryLoad", wintypes.DWORD),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(status)
    if not kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise _win_error("GlobalMemoryStatusEx")
    return int(status.ullAvailPhys), int(status.ullTotalPhys)


def _disk_free_c():
    free = ctypes.c_ulonglong()
    total = ctypes.c_ulonglong()
    available = ctypes.c_ulonglong()
    if not kernel32.GetDiskFreeSpaceExW("C:\\", ctypes.byref(available), ctypes.byref(total), ctypes.byref(free)):
        raise _win_error("GetDiskFreeSpaceExW(C:) ")
    return int(available.value)


def _process_rss(handle):
    counters = PROCESS_MEMORY_COUNTERS()
    counters.cb = ctypes.sizeof(counters)
    if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
        raise _win_error("GetProcessMemoryInfo")
    return int(counters.WorkingSetSize)


def parse_ross_idle_record(record):
    """绑定ROSS session_id和MCP envelope，不接受running或模糊状态。"""
    if type(record) is not dict or type(record.get("input")) is not dict or type(record.get("result")) is not dict:
        raise GateBlocked("ROSS MCP记录结构不完整")
    input_sid = record["input"].get("session_id")
    if type(input_sid) is not str or not input_sid:
        raise GateBlocked("ROSS input缺少精确session_id")
    blocks = record["result"].get("content")
    if (
        type(blocks) is not list
        or len(blocks) != 1
        or type(blocks[0]) is not dict
        or blocks[0].get("type") != "text"
    ):
        raise GateBlocked("ROSS结果必须恰有一个文本块")
    if record["result"].get("isError") is True:
        raise GateBlocked("ROSS MCP结果标记为错误")
    try:
        payload = json.loads(blocks[0]["text"])
    except (KeyError, TypeError, ValueError) as error:
        raise GateBlocked(f"ROSS文本不是严格JSON：{error!r}") from error
    if type(payload) is not dict or payload.get("session_id") != input_sid:
        raise GateBlocked("ROSS session_id输入与返回不一致")
    if payload.get("status") != "idle" or payload.get("active_command") is not None:
        raise GateBlocked("ROSS会话未明确处于idle")
    identity = payload.get("root_identity")
    if type(identity) is not dict or set(identity) != set(ROSS_IDENTITY_FIELDS):
        raise GateBlocked("ROSS root身份不是完整六字段")
    if type(identity.get("pid")) is not int or identity["pid"] <= 0:
        raise GateBlocked("ROSS root PID无效")
    if type(identity.get("create_time")) not in (int, float):
        raise GateBlocked("ROSS root创建时间类型无效")
    if type(identity.get("exe")) is not str or type(identity.get("cwd")) is not str:
        raise GateBlocked("ROSS root路径字段类型无效")
    if type(identity.get("cmdline")) is not list or not all(type(item) is str for item in identity["cmdline"]):
        raise GateBlocked("ROSS root命令行字段无效")
    if type(identity.get("ppid")) is not int:
        raise GateBlocked("ROSS root父PID字段无效")
    return input_sid, identity


def _identity_equal(left, right):
    return all(left.get(key) == right.get(key) for key in ROSS_IDENTITY_FIELDS)


def _decode_job_pid_list(buffer, pointer_size=None):
    """按指定ULONG_PTR位宽纯解码Job PID数组并校验计数、边界和唯一性。"""
    raw = bytes(buffer)
    width = ctypes.sizeof(ctypes.c_size_t) if pointer_size is None else int(pointer_size)
    if width not in (4, 8):
        raise GateBlocked(f"Job PID列表ULONG_PTR位宽不支持：{width}")
    if len(raw) < 8:
        raise GateBlocked(f"Job PID列表头部被截断：{len(raw)}字节")
    assigned, listed = struct.unpack_from("<II", raw, 0)
    capacity = (len(raw) - 8) // width
    if assigned > capacity or listed > capacity:
        raise GateBlocked(
            f"Job PID列表计数超出缓冲边界：assigned={assigned}, listed={listed}, capacity={capacity}, width={width}"
        )
    if assigned != listed:
        raise GateBlocked(f"Job PID列表assigned/listed计数不一致：{assigned}/{listed}")
    format_code = "I" if width == 4 else "Q"
    pids = tuple(struct.unpack_from("<" + format_code, raw, 8 + index * width)[0] for index in range(listed))
    if any(pid == 0 for pid in pids) or len(set(pids)) != len(pids):
        raise GateBlocked("Job PID列表含零PID或重复PID")
    return tuple(sorted(int(pid) for pid in pids))


class SuspendedRootError(JobGuardError):
    """CREATE_SUSPENDED启动未能闭合，已附带原始错误与逐项清理结果。"""

    def __init__(self, primary_error, events, cleanup_errors):
        self.primary_error = primary_error
        self.events = list(events)
        self.cleanup_errors = list(cleanup_errors)
        super().__init__(
            "suspended root 启动被fail-closed："
            f"primary={primary_error!r}; cleanup_errors={self.cleanup_errors!r}; events={self.events!r}"
        )


class SuspendedRootProcess:
    """保存CreateProcessW原始句柄及Job归属，且仅在门禁全过后恢复线程。"""

    def __init__(self, job, process_info, identity, birth_ticks, events):
        self.job = job
        self.process_info = process_info
        self.identity = dict(identity)
        self.birth_ticks = int(birth_ticks)
        self.events = list(events)
        self.resumed = True
        self.closed = False

    @property
    def pid(self):
        return int(self.process_info.dwProcessId)

    @property
    def process_handle(self):
        return self.process_info.hProcess

    def wait_and_close(self, timeout_seconds=30.0):
        """闭合真实root句柄、Job成员及退出码后关闭全部自有句柄。"""
        if self.closed:
            raise GateBlocked("suspended root句柄已关闭")
        wait_ms = max(0, int(float(timeout_seconds) * 1000))
        root_wait = _api_wait(self.process_handle, wait_ms)
        if root_wait != WAIT_OBJECT_0:
            if root_wait == WAIT_TIMEOUT:
                raise GateBlocked("等待CreateProcessW root退出超时")
            raise _win_error(f"WaitForSingleObject(root)={root_wait}")
        root_exit_code = _api_get_exit_code(self.process_handle)
        if root_exit_code == STILL_ACTIVE:
            raise GateBlocked("root HANDLE已signal但GetExitCodeProcess仍为STILL_ACTIVE")
        final = self.job.wait_empty_and_verify(timeout_seconds=timeout_seconds, root_must_exit=True)
        final["root_native_handle_exit_code"] = root_exit_code
        final["root_native_handle_pid"] = self.pid
        final["root_native_handle_birth_ticks"] = self.birth_ticks
        final["resume_thread_previous_suspend_count"] = 1
        self._close_all()
        return {"final": final, "events": list(self.events)}

    def _close_all(self):
        errors = []
        try:
            self.job.close()
        except BaseException as error:
            errors.append(f"JobObject/成员句柄关闭失败：{error!r}")
        for name, handle in (("root thread", self.process_info.hThread), ("root process", self.process_info.hProcess)):
            if handle:
                try:
                    _checked_close_handle(handle, name)
                except BaseException as error:
                    errors.append(f"CloseHandle({name})失败：{error!r}")
                else:
                    if name == "root thread":
                        self.process_info.hThread = None
                    else:
                        self.process_info.hProcess = None
        self.closed = not errors
        if errors:
            self.job.cleanup_errors.extend(errors)
            raise GateBlocked("成功生命周期句柄关闭不完整：" + "；".join(errors))


def _close_attribute_list(buffer, pointer):
    if pointer:
        kernel32.DeleteProcThreadAttributeList(pointer)


def _initialize_handle_list(handles):
    """建立STARTUPINFOEX白名单，避免向Vivado继承控制器的其他HANDLE。"""
    if not handles:
        return None, None
    size = ctypes.c_size_t(0)
    kernel32.InitializeProcThreadAttributeList(None, 1, 0, ctypes.byref(size))
    code = ctypes.get_last_error()
    if code != ERROR_INSUFFICIENT_BUFFER or size.value <= 0:
        ctypes.set_last_error(code)
        raise _win_error("InitializeProcThreadAttributeList(size)")
    buffer = ctypes.create_string_buffer(size.value)
    pointer = ctypes.cast(buffer, ctypes.c_void_p)
    if not kernel32.InitializeProcThreadAttributeList(pointer, 1, 0, ctypes.byref(size)):
        raise _win_error("InitializeProcThreadAttributeList")
    handle_array = (wintypes.HANDLE * len(handles))(*[wintypes.HANDLE(handle) for handle in handles])
    if not kernel32.UpdateProcThreadAttribute(
        pointer,
        0,
        PROC_THREAD_ATTRIBUTE_HANDLE_LIST,
        ctypes.cast(handle_array, ctypes.c_void_p),
        ctypes.sizeof(handle_array),
        None,
        None,
    ):
        error = _win_error("UpdateProcThreadAttribute(HANDLE_LIST)")
        kernel32.DeleteProcThreadAttributeList(pointer)
        raise error
    return buffer, pointer


def launch_suspended_root(job, executable, argv, cwd=None, std_handles=None, environment=None):
    """直接创建挂起子进程，先Assign并稳定核验Job成员，再唯一一次ResumeThread。"""
    if os.name != "nt":
        raise GateBlocked("CREATE_SUSPENDED direct launcher仅支持Windows")
    if not isinstance(job, JobObject) or job.closed or not job.handle:
        raise GateBlocked("direct launcher需要打开且有效的本任务JobObject")
    if not isinstance(executable, str) or not os.path.isabs(executable):
        raise GateBlocked("目标映像必须是精确绝对路径")
    if not isinstance(argv, (list, tuple)) or not argv or argv[0] != executable:
        raise GateBlocked("argv[0]必须逐字符等于CreateProcessW应用映像路径")
    if std_handles is not None and (not isinstance(std_handles, (list, tuple)) or len(std_handles) != 3):
        raise GateBlocked("标准句柄必须按stdin/stdout/stderr给出三个HANDLE")
    if job.pid_list() or job.accounting()["active_processes"] != 0:
        raise GateBlocked("CreateProcessW前本任务Job必须为空")

    events = []
    info = None
    assigned = False
    root_registered = False
    attribute_buffer = None
    attribute_pointer = None
    try:
        startup = STARTUPINFOW()
        startup.cb = ctypes.sizeof(STARTUPINFOW)
        startup_ex = None
        inherited = ()
        if std_handles is not None:
            inherited = tuple(std_handles)
            if any(not handle for handle in inherited):
                raise GateBlocked("標準句柄包含NULL")
            attribute_buffer, attribute_pointer = _initialize_handle_list(inherited)
            startup_ex = STARTUPINFOEXW()
            startup_ex.StartupInfo = startup
            startup_ex.StartupInfo.cb = ctypes.sizeof(STARTUPINFOEXW)
            startup_ex.StartupInfo.dwFlags = STARTF_USESTDHANDLES
            startup_ex.StartupInfo.hStdInput = inherited[0]
            startup_ex.StartupInfo.hStdOutput = inherited[1]
            startup_ex.StartupInfo.hStdError = inherited[2]
            startup_ex.lpAttributeList = attribute_pointer
        command_line = subprocess.list2cmdline(list(argv))
        environment_buffer = None
        if environment is not None:
            if not isinstance(environment, dict):
                raise GateBlocked("direct launcher环境必须是字符串键值字典")
            entries = []
            for key, value in environment.items():
                drive_key = isinstance(key, str) and len(key) == 3 and key[0] == "=" and key[1].isalpha() and key[2] == ":"
                if not isinstance(key, str) or not isinstance(value, str) or not key or ("=" in key and not drive_key) or "\0" in key or "\0" in value:
                    raise GateBlocked(f"direct launcher环境项格式不符：{key!r}")
                entries.append((key, value))
            entries.sort(key=lambda row: row[0].casefold())
            environment_text = "\0".join(f"{key}={value}" for key, value in entries) + "\0\0"
            environment_buffer = ctypes.create_unicode_buffer(environment_text)
        info = _api_create_process(
            executable,
            command_line,
            cwd,
            startup,
            startup_ex,
            bool(inherited),
            environment_block=environment_buffer,
        )
        events.append({"event": "CREATE_SUSPENDED", "pid": int(info.dwProcessId), "monotonic_seconds": time.monotonic()})
        if int(info.dwProcessId) <= 0 or int(info.hProcess or 0) <= 0 or int(info.hThread or 0) <= 0:
            raise GateBlocked("CreateProcessW返回空PID或HANDLE")
        handle_pid = _api_process_id(info.hProcess)
        birth_ticks = _api_creation_ticks(info.hProcess)
        identity = _api_process_identity(handle_pid)
        _assert_handle_identity(info.hProcess, info.dwProcessId, birth_ticks, identity)
        expected_image = os.path.normcase(os.path.abspath(executable))
        actual_image = os.path.normcase(os.path.abspath(identity["exe"]))
        if actual_image != expected_image:
            raise GateBlocked(f"CreateProcessW映像身份不符：expected={executable!r}, actual={identity['exe']!r}")
        if identity.get("cmdline") != list(argv):
            raise GateBlocked(f"CreateProcessW命令行读回不符：expected={list(argv)!r}, actual={identity.get('cmdline')!r}")
        if identity.get("ppid") != os.getpid():
            raise GateBlocked(f"CreateProcessW root父PID不是本控制器：expected={os.getpid()}, actual={identity.get('ppid')}")
        if _api_is_process_in_job(info.hProcess, job.handle):
            raise GateBlocked("Assign前root已属于本次目標Job")
        if not _api_assign_process(job.handle, info.hProcess):
            raise _win_error("AssignProcessToJobObject(CREATE_SUSPENDED root)")
        assigned = True
        events.append({"event": "ASSIGN_PROCESS_TO_JOB", "pid": int(info.dwProcessId), "monotonic_seconds": time.monotonic()})
        _assert_handle_identity(info.hProcess, info.dwProcessId, birth_ticks, identity)
        if not _api_is_process_in_job(info.hProcess, job.handle):
            raise GateBlocked("Assign后原始root HANDLE的IsProcessInJob读回为false")

        root = job._remember_process(
            int(info.dwProcessId),
            PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | PROCESS_SET_QUOTA | PROCESS_TERMINATE | SYNCHRONIZE,
        )
        root_registered = True
        if root["birth_ticks"] != birth_ticks or not _identity_equal(root["identity"], identity):
            raise GateBlocked("Job成员句柄与CreateProcessW原始root HANDLE身份不一致")
        job.root_pid = int(info.dwProcessId)
        job.root_birth_ticks = int(birth_ticks)
        job.root_identity = dict(identity)
        suspended_membership = job._verify_suspended_root_membership(
            info.hProcess, int(info.dwProcessId), birth_ticks, identity,
        )
        before_resume_pids = job.pid_list()
        before_resume_accounting = job.accounting()
        if before_resume_pids != (int(info.dwProcessId),) or before_resume_accounting["active_processes"] != 1:
            raise GateBlocked(
                "ResumeThread前Job成員未精確閉合："
                f"pids={before_resume_pids}, accounting={before_resume_accounting}"
            )
        flags = job.query_limit_flags()
        if flags != JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE or flags & (0x00000800 | 0x00001000):
            raise GateBlocked(f"ResumeThread前Job限制读回不符：0x{flags:08x}")
        _assert_handle_identity(info.hProcess, info.dwProcessId, birth_ticks, identity)
        if not _api_is_process_in_job(info.hProcess, job.handle):
            raise GateBlocked("ResumeThread前原始root HANDLE不在本次Job")
        events.append({
            "event": "PRE_RESUME_CLOSED",
            "pid": int(info.dwProcessId),
            "job_pids": list(before_resume_pids),
            "accounting": before_resume_accounting,
            "suspended_root_membership": suspended_membership,
            "job_limit_flags": flags,
            "monotonic_seconds": time.monotonic(),
        })
        resume_count = _api_resume_thread(info.hThread)
        if resume_count == 0xFFFFFFFF:
            raise _win_error("ResumeThread")
        if resume_count != 1:
            raise GateBlocked(f"ResumeThread先前挂起计数不是唯一预期值1：{resume_count}")
        events.append({"event": "RESUME_THREAD", "pid": int(info.dwProcessId), "previous_suspend_count": resume_count, "monotonic_seconds": time.monotonic()})
        _close_attribute_list(attribute_buffer, attribute_pointer)
        attribute_buffer = attribute_pointer = None
        return SuspendedRootProcess(job, info, identity, birth_ticks, events)
    except BaseException as primary:
        cleanup_errors = []
        if attribute_pointer:
            try:
                _close_attribute_list(attribute_buffer, attribute_pointer)
            except BaseException as error:
                cleanup_errors.append(f"DeleteProcThreadAttributeList失败：{error!r}")
        if info is not None and info.hProcess:
            terminated_by_job = False
            if assigned and not job.closed:
                try:
                    job.terminate_own_job(92)
                    terminated_by_job = True
                    events.append({"event": "TERMINATE_OWN_JOB", "monotonic_seconds": time.monotonic()})
                except BaseException as error:
                    cleanup_errors.append(f"TerminateJobObject失败：{error!r}")
            if not terminated_by_job:
                try:
                    if not _api_terminate_process(info.hProcess, 92):
                        cleanup_errors.append(f"TerminateProcess(root)返回FALSE：WinError {ctypes.get_last_error()}")
                    else:
                        events.append({"event": "TERMINATE_ROOT", "monotonic_seconds": time.monotonic()})
                except BaseException as error:
                    cleanup_errors.append(f"TerminateProcess(root)调用失败：{error!r}")
            try:
                wait = _api_wait(info.hProcess, 30000)
                if wait == WAIT_TIMEOUT and terminated_by_job:
                    events.append({"event": "JOB_TERMINATE_WAIT_TIMEOUT", "monotonic_seconds": time.monotonic()})
                    if not _api_terminate_process(info.hProcess, 92):
                        cleanup_errors.append(f"fallback TerminateProcess(root)返回FALSE：WinError {ctypes.get_last_error()}")
                    else:
                        events.append({"event": "TERMINATE_ROOT_FALLBACK", "monotonic_seconds": time.monotonic()})
                    wait = _api_wait(info.hProcess, 30000)
                if wait != WAIT_OBJECT_0:
                    cleanup_errors.append(f"WaitForSingleObject(root)未闭合：{wait}")
                else:
                    exit_code = _api_get_exit_code(info.hProcess)
                    if exit_code == STILL_ACTIVE:
                        cleanup_errors.append("root HANDLE已signal但GetExitCodeProcess为STILL_ACTIVE")
                    events.append({"event": "ROOT_REAPED", "exit_code": exit_code, "monotonic_seconds": time.monotonic()})
            except BaseException as error:
                cleanup_errors.append(f"root等候/退出码读回失败：{error!r}")
            if assigned and not job.closed:
                try:
                    if root_registered:
                        events.append({"event": "JOB_REAPED", "result": job.wait_empty_and_verify(timeout_seconds=30.0, root_must_exit=True), "monotonic_seconds": time.monotonic()})
                    else:
                        deadline = time.monotonic() + 30.0
                        while time.monotonic() < deadline:
                            pids = job.pid_list()
                            accounting = job.accounting()
                            if not pids and accounting["active_processes"] == 0:
                                break
                            time.sleep(0.05)
                        else:
                            raise GateBlocked(f"失败清理后Job仍有成员：pids={pids}, accounting={accounting}")
                        if job.pid_list() or job.accounting()["active_processes"] != 0:
                            raise GateBlocked("失败清理后Job成员第二次读回非空")
                        events.append({"event": "JOB_REAPED_WITHOUT_ROOT_IDENTITY", "monotonic_seconds": time.monotonic()})
                except BaseException as error:
                    cleanup_errors.append(f"Job终态闭合读回失败：{error!r}")
        if not job.closed:
            try:
                job.close()
                events.append({"event": "CLOSE_OWN_JOB", "monotonic_seconds": time.monotonic()})
            except BaseException as error:
                cleanup_errors.append(f"CloseHandle(Job/member)失败：{error!r}")
        if info is not None:
            for name, handle in (("root thread", info.hThread), ("root process", info.hProcess)):
                if handle:
                    try:
                        _checked_close_handle(handle, name)
                    except BaseException as error:
                        cleanup_errors.append(f"CloseHandle({name})失败：{error!r}")
                    else:
                        if name == "root thread":
                            info.hThread = None
                        else:
                            info.hProcess = None
        events.append({"event": "FAIL_CLOSED", "resume_attempted": any(row.get("event") == "RESUME_THREAD" for row in events), "monotonic_seconds": time.monotonic()})
        raise SuspendedRootError(primary, events, cleanup_errors) from primary


class JobObject:
    """仅持有当前候选Job；默认关闭句柄时终止本Job成员。"""

    def __init__(self, kill_on_close=True):
        self.handle = kernel32.CreateJobObjectW(None, None)
        if not self.handle:
            raise _win_error("CreateJobObjectW")
        self.closed = False
        self.cleanup_errors = []
        self.member_handles = {}
        self._ready_nonce = secrets.token_bytes(32)
        self._ready_token = None
        self._ready_token_consumed = False
        self._dispatch_used = False
        flags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE if kill_on_close else 0
        limits = EXTENDED_LIMIT_INFORMATION()
        limits.BasicLimitInformation.LimitFlags = flags
        if not kernel32.SetInformationJobObject(
            self.handle,
            JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(limits),
            ctypes.sizeof(limits),
        ):
            error = _win_error("SetInformationJobObject(ExtendedLimitInformation)")
            self.close()
            raise error
        try:
            self.flags = self.query_limit_flags()
        except BaseException as primary:
            try:
                self.close()
            except BaseException as cleanup:
                raise GateBlocked(
                    "初始Job限制读回失败且Job HANDLE清理失败："
                    f"primary={primary!r}; cleanup={cleanup!r}"
                ) from primary
            raise
        if self.flags != flags or self.flags & (0x00000800 | 0x00001000):
            self.close()
            raise GateBlocked(f"Job限制标志读回不符：0x{self.flags:08x}")

    def query_limit_flags(self):
        info = EXTENDED_LIMIT_INFORMATION()
        returned = wintypes.DWORD()
        if not kernel32.QueryInformationJobObject(
            self.handle,
            JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(info),
            ctypes.sizeof(info),
            ctypes.byref(returned),
        ):
            raise _win_error("QueryInformationJobObject(ExtendedLimitInformation)")
        if returned.value != ctypes.sizeof(info):
            raise GateBlocked("ExtendedLimitInformation读回大小不符")
        return int(info.BasicLimitInformation.LimitFlags)

    def accounting(self):
        info = BASIC_ACCOUNTING_INFORMATION()
        returned = wintypes.DWORD()
        if not kernel32.QueryInformationJobObject(
            self.handle,
            JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION,
            ctypes.byref(info),
            ctypes.sizeof(info),
            ctypes.byref(returned),
        ):
            raise _win_error("QueryInformationJobObject(BasicAccountingInformation)")
        if returned.value != ctypes.sizeof(info):
            raise GateBlocked("BasicAccountingInformation读回大小不符")
        return {
            "total_processes": int(info.TotalProcesses),
            "active_processes": int(info.ActiveProcesses),
            "terminated_processes": int(info.TotalTerminatedProcesses),
            "exited_processes": int(info.TotalProcesses - info.ActiveProcesses),
            "page_faults": int(info.TotalPageFaultCount),
        }

    def pid_list(self):
        capacity = 16
        while capacity <= MAX_PID_LIST:
            byte_count = 8 + capacity * ctypes.sizeof(ctypes.c_size_t)
            buffer = ctypes.create_string_buffer(byte_count)
            returned = wintypes.DWORD()
            ok = kernel32.QueryInformationJobObject(
                self.handle,
                JOB_OBJECT_BASIC_PROCESS_ID_LIST,
                ctypes.cast(buffer, ctypes.c_void_p),
                byte_count,
                ctypes.byref(returned),
            )
            if byte_count < 8:
                raise GateBlocked("Job PID列表缓冲小于固定头部")
            assigned, listed = struct.unpack_from("<II", buffer.raw, 0)
            if not ok:
                code = ctypes.get_last_error()
                if code == ERROR_MORE_DATA or assigned > capacity:
                    capacity = max(capacity * 2, int(assigned))
                    continue
                ctypes.set_last_error(code)
                raise _win_error("QueryInformationJobObject(BasicProcessIdList)")
            if assigned > capacity or listed > capacity:
                capacity = max(capacity * 2, int(assigned), int(listed))
                continue
            if assigned != listed:
                capacity = max(capacity * 2, int(assigned))
                continue
            pids = _decode_job_pid_list(buffer.raw, ctypes.sizeof(ctypes.c_size_t))
            if len(pids) != assigned:
                raise GateBlocked("Job PID列表解码数量与API头部不符")
            return pids
        raise GateBlocked("Job PID列表超过4096个成员")

    def membership(self, pid):
        handle = _open_process(pid, PROCESS_QUERY_INFORMATION | SYNCHRONIZE)
        try:
            return _is_in_job(handle, self.handle)
        except BaseException as primary:
            try:
                _checked_close_handle(handle, f"membership PID {pid}")
            except BaseException as cleanup:
                raise GateBlocked(f"Job成员核验失败：{primary!r}；临时HANDLE关闭失败：{cleanup!r}") from primary
            raise
        else:
            _checked_close_handle(handle, f"membership PID {pid}")

    def _remember_process(self, pid, access):
        handle, ticks, identity = _open_process_identity_handle(pid, access)
        key = (int(pid), int(ticks))
        current = self.member_handles.get(key)
        if current is not None:
            _checked_close_handle(handle, f"重复成员PID {pid}")
            if not _identity_equal(current["identity"], identity):
                raise GateBlocked("已核PID出生身份的六字段漂移")
            _assert_handle_identity(current["handle"], pid, current["birth_ticks"], current["identity"])
            return current
        self.member_handles[key] = {"handle": handle, "birth_ticks": ticks, "identity": identity}
        return self.member_handles[key]

    def attach_idle_root(self, ross_record):
        session_id, ross_identity = parse_ross_idle_record(ross_record)
        actual = _api_process_identity(ross_identity["pid"])
        if not _identity_equal(ross_identity, actual):
            raise GateBlocked("ROSS六字段与本机root读回不同")
        root_pid = int(ross_identity["pid"])
        before_descendants = descendants(root_pid)
        if before_descendants:
            raise GateBlocked(f"READY前发现既有后代，拒绝移入任务：{sorted(before_descendants)}")
        access = PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | PROCESS_SET_QUOTA | PROCESS_TERMINATE | SYNCHRONIZE
        root = self._remember_process(root_pid, access)
        _assert_handle_identity(root["handle"], root_pid, root["birth_ticks"], root["identity"])
        if root["identity"]["create_time"] != ross_identity["create_time"]:
            raise GateBlocked("ROSS六字段create_time与已打开root HANDLE身份不一致")
        root_outer_job = _is_in_job(root["handle"], None)
        if _api_is_process_in_job(root["handle"], self.handle):
            raise GateBlocked("root在本次Assign前已属于目标Job")
        if self.pid_list() or self.accounting()["active_processes"] != 0:
            raise GateBlocked("Assign前目标Job不为空")
        assigned = False
        try:
            _assert_handle_identity(root["handle"], root_pid, root["birth_ticks"], root["identity"])
            if not _api_assign_process(self.handle, root["handle"]):
                raise _win_error("AssignProcessToJobObject(root)")
            assigned = True
            _assert_handle_identity(root["handle"], root_pid, root["birth_ticks"], root["identity"])
            if not _api_is_process_in_job(root["handle"], self.handle):
                raise GateBlocked("Assign后原始root HANDLE没有读回属于目标Job")
            after_pids = self.pid_list()
            after_accounting = self.accounting()
            if after_pids != (root_pid,) or after_accounting["active_processes"] != 1:
                raise GateBlocked(f"Assign后Job成员未精确闭合：pids={after_pids}, accounting={after_accounting}")
        except BaseException as primary:
            if assigned and not self.closed:
                try:
                    self.close()
                except BaseException as cleanup:
                    raise GateBlocked(f"Assign后身份/成员复核失败：{primary!r}；自有Job清理失败：{cleanup!r}") from primary
            raise
        self.session_id = session_id
        self.root_pid = root_pid
        self.root_birth_ticks = root["birth_ticks"]
        self.root_identity = dict(ross_identity)
        self.root_outer_job_before = root_outer_job
        self._verify_ready_membership()
        self._baseline_accounting = self.accounting()
        self._baseline_pids = set(self.pid_list())
        self._baseline_keys = set(self.member_handles)
        receipt = {
            "kind": "READY",
            "session_id": self.session_id,
            "root_identity": self.root_identity,
            "root_in_outer_job_before_attach": self.root_outer_job_before,
            "job_limit_flags": self.flags,
            "job_member_pids": list(self.pid_list()),
            "active_processes": self.accounting()["active_processes"],
            "api_sizes": api_sizes(),
            "monotonic_seconds": time.monotonic(),
        }
        self._ready_token = _ReadyToken(self, self._ready_nonce, receipt)
        return receipt, self._ready_token

    def consume_ready_token(self, ready_token, session_id, root_identity):
        """仅控制器派发入口可消费一次READY token并复核实际Job状态。"""
        if (
            not isinstance(ready_token, _ReadyToken)
            or ready_token.owner is not self
            or ready_token.nonce is not self._ready_nonce
            or ready_token is not self._ready_token
            or self._ready_token_consumed
        ):
            raise GateBlocked("READY token伪造、跨Job或已消费")
        receipt = ready_token.receipt
        if receipt.get("session_id") != session_id or not _identity_equal(receipt.get("root_identity", {}), root_identity):
            raise GateBlocked("READY token的session/root身份与控制器绑定不符")
        root = self.member_handles.get((self.root_pid, self.root_birth_ticks))
        if root is None:
            raise GateBlocked("READY token缺少已固定root身份句柄")
        _assert_handle_identity(root["handle"], self.root_pid, self.root_birth_ticks, root["identity"])
        if not _api_is_process_in_job(root["handle"], self.handle):
            raise GateBlocked("READY token消费时root不属于当前Job")
        self._verify_ready_membership()
        self._ready_token_consumed = True
        return receipt

    def _verify_suspended_root_membership(
        self, root_process_handle, root_pid, root_birth_ticks, root_identity,
    ):
        """在未恢复的direct root上核验HANDLE身份与稳定单成员Job。"""
        root_pid = int(root_pid)
        root_birth_ticks = int(root_birth_ticks)
        if self.closed or not self.handle:
            raise GateBlocked("挂起root成员核验需要有效Job句柄")
        if (
            not root_process_handle
            or self.root_pid != root_pid
            or self.root_birth_ticks != root_birth_ticks
            or not _identity_equal(self.root_identity, root_identity)
        ):
            raise GateBlocked("挂起root的PID、出生时刻或六字段身份未绑定到当前Job")
        root = self.member_handles.get((root_pid, root_birth_ticks))
        if root is None:
            raise GateBlocked("挂起root缺少已登记的Job成员身份句柄")

        previous = None
        previous_accounting = None
        for _ in range(8):
            _assert_handle_identity(
                root_process_handle, root_pid, root_birth_ticks, root_identity,
            )
            _assert_handle_identity(
                root["handle"], root_pid, root_birth_ticks, root["identity"],
            )
            if not _api_is_process_in_job(root_process_handle, self.handle):
                raise GateBlocked("挂起root原始HANDLE不属于当前Job")
            if not _api_is_process_in_job(root["handle"], self.handle):
                raise GateBlocked("挂起root成员HANDLE不属于当前Job")
            root_wait = _api_wait(root_process_handle, 0)
            if root_wait != WAIT_TIMEOUT:
                raise GateBlocked(f"ResumeThread前root未保持挂起存活状态：wait={root_wait}")

            pids = tuple(self.pid_list())
            accounting = self.accounting()
            if pids != (root_pid,) or accounting["active_processes"] != 1:
                raise GateBlocked(
                    "挂起root的Job成员不是唯一root："
                    f"pids={pids}, accounting={accounting}"
                )
            state = (pids, accounting["active_processes"])
            if state == previous:
                _assert_handle_identity(
                    root_process_handle, root_pid, root_birth_ticks, root_identity,
                )
                if not _api_is_process_in_job(root_process_handle, self.handle):
                    raise GateBlocked("稳定单成员读回后root原始HANDLE失去Job归属")
                final_wait = _api_wait(root_process_handle, 0)
                if final_wait != WAIT_TIMEOUT:
                    raise GateBlocked(f"稳定单成员读回后root不再保持挂起：wait={final_wait}")
                return {
                    "root_pid": root_pid,
                    "root_birth_ticks": root_birth_ticks,
                    "stable_singleton_reads": 2,
                    "first": {
                        "job_pids": list(previous[0]),
                        "active_processes": previous[1],
                        "accounting": previous_accounting,
                    },
                    "second": {
                        "job_pids": list(pids),
                        "active_processes": accounting["active_processes"],
                        "accounting": accounting,
                    },
                    "root_wait_before_resume": WAIT_TIMEOUT,
                }
            previous = state
            previous_accounting = accounting
            time.sleep(0.05)
        raise GateBlocked("挂起root的Job单成员状态未连续稳定读回")

    def _verify_ready_membership(self):
        previous = None
        for _ in range(8):
            root_handle = self.member_handles[(self.root_pid, self.root_birth_ticks)]
            _assert_handle_identity(root_handle["handle"], self.root_pid, self.root_birth_ticks, root_handle["identity"])
            current_identity = _api_process_identity(self.root_pid)
            if not _identity_equal(current_identity, self.root_identity):
                raise GateBlocked("READY期间root六字段变化")
            if not _api_is_process_in_job(root_handle["handle"], self.handle):
                raise GateBlocked("READY期间原始root HANDLE失去目标Job归属")
            first_pids = set(self.pid_list())
            first_accounting = self.accounting()
            tree = descendants(self.root_pid)
            tree_members = {self.root_pid} | tree
            for pid in tree_members:
                member = self._remember_process(
                    pid,
                    PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | SYNCHRONIZE,
                )
                _assert_handle_identity(member["handle"], pid, member["birth_ticks"], member["identity"])
                if not _api_is_process_in_job(member["handle"], self.handle):
                    raise GateBlocked(f"现存root后代未被Job捕获：PID {pid}")
            second_pids = set(self.pid_list())
            second_accounting = self.accounting()
            state = (frozenset(second_pids), second_accounting["total_processes"], second_accounting["terminated_processes"])
            if (
                first_pids == second_pids == tree_members
                and first_accounting["active_processes"] == len(first_pids)
                and second_accounting["active_processes"] == len(second_pids)
                and first_accounting["total_processes"] == second_accounting["total_processes"]
                and first_accounting["terminated_processes"] == second_accounting["terminated_processes"]
                and state == previous
            ):
                root = self.member_handles[(self.root_pid, self.root_birth_ticks)]
                _assert_handle_identity(root["handle"], self.root_pid, self.root_birth_ticks, root["identity"])
                if not _api_is_process_in_job(root["handle"], self.handle):
                    raise GateBlocked("root Job归属读回失败")
                return
            previous = state
            time.sleep(0.05)
        raise GateBlocked("Job成员集合/进程树/Accounting未能稳定闭合READY")

    def dispatch_after_ready(self, ready_token, host_stdin, command):
        if self._dispatch_used:
            raise GateBlocked("heavy dispatch缺少本次READY收据")
        if not self._ready_token_consumed:
            self.consume_ready_token(ready_token, self.session_id, self.root_identity)
        elif ready_token is not self._ready_token:
            raise GateBlocked("heavy dispatch READY token与已消费token不一致")
        if command != "START_FIXTURE_HEAVY":
            raise GateBlocked("隔离候选只允许启动指定fixture命令")
        if self.accounting()["active_processes"] <= 0 or not self.membership(self.root_pid):
            raise GateBlocked("READY后root已不在本Job，拒绝派发")
        host_stdin.write(json.dumps({"command": command, "session_id": self.session_id}, separators=(",", ":")) + "\n")
        host_stdin.flush()
        self._dispatch_used = True
        return {"kind": "HEAVY_DISPATCH", "session_id": self.session_id, "command": command, "monotonic_seconds": time.monotonic()}

    def sample(self, previous_sample_start=None, previous_accounting=None, previous_pids=None, previous_keys=None):
        started = time.monotonic()
        first_pids = set(self.pid_list())
        first_accounting = self.accounting()
        uncertainty = []
        if first_accounting["active_processes"] != len(first_pids):
            uncertainty.append("ACTIVE_COUNT_PID_LIST_MISMATCH")
        measured, current_keys = [], set()
        access = PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | SYNCHRONIZE
        for pid in sorted(first_pids):
            try:
                member = self._remember_process(pid, access)
                key = (int(pid), int(member["birth_ticks"]))
                current_keys.add(key)
                if not _is_in_job(member["handle"], self.handle):
                    uncertainty.append(f"PID_NOT_IN_JOB:{pid}")
                    continue
                if pid != self.root_pid and member["identity"]["ppid"] not in first_pids:
                    uncertainty.append(f"MEMBER_PARENT_NOT_IN_JOB:{pid}")
                    continue
                if pid == self.root_pid and not _identity_equal(member["identity"], self.root_identity):
                    uncertainty.append("ROOT_IDENTITY_DRIFT")
                    continue
                rss = _process_rss(member["handle"])
                measured.append({"pid": pid, "create_time": member["identity"]["create_time"], "birth_ticks": member["birth_ticks"], "rss_bytes": rss, "identity": member["identity"]})
            except (JobGuardError, GateBlocked, OSError, psutil.Error) as error:
                uncertainty.append(f"MEMBER_READBACK_FAILED:{pid}:{error!r}")
        second_pids = set(self.pid_list())
        second_accounting = self.accounting()
        if first_pids != second_pids:
            uncertainty.append("PID_LIST_CHANGED_DURING_SAMPLE")
        if (
            first_accounting["total_processes"] != second_accounting["total_processes"]
            or first_accounting["active_processes"] != second_accounting["active_processes"]
        ):
            uncertainty.append("JOB_PROCESS_COUNTER_CHANGED_DURING_SAMPLE")
        if second_accounting["active_processes"] != len(second_pids):
            uncertainty.append("SECOND_ACTIVE_COUNT_PID_LIST_MISMATCH")
        if previous_accounting is not None:
            total_delta = second_accounting["total_processes"] - previous_accounting["total_processes"]
            exit_delta = second_accounting["exited_processes"] - previous_accounting["exited_processes"]
            new_seen = len(current_keys - (previous_keys or set()))
            known_ended = len((previous_keys or set()) - current_keys)
            if total_delta < 0 or total_delta != new_seen:
                uncertainty.append(f"UNSAMPLED_PROCESS_CREATION:delta={total_delta}:seen={new_seen}")
            if exit_delta < 0 or exit_delta != known_ended:
                uncertainty.append(f"UNSAMPLED_PROCESS_TERMINATION:delta={exit_delta}:known={known_ended}")
        if previous_sample_start is not None and started - previous_sample_start > SAMPLE_GAP_LIMIT_SECONDS:
            uncertainty.append("SAMPLE_START_GAP_GT_1S")
        try:
            available_ram, total_ram = _memory_status()
            c_free = _disk_free_c()
        except JobGuardError as error:
            uncertainty.append(f"RESOURCE_QUERY_FAILED:{error!r}")
            available_ram, total_ram, c_free = None, None, None
        terminal_empty_proven = (
            not second_pids
            and type(second_accounting.get("active_processes")) is int
            and second_accounting["active_processes"] == 0
            and type(second_accounting.get("exited_processes")) is int
            and type(second_accounting.get("total_processes")) is int
            and second_accounting["exited_processes"] == second_accounting["total_processes"]
        )
        if not uncertainty:
            rss_sum = sum(item["rss_bytes"] for item in measured)
        elif terminal_empty_proven:
            rss_sum = 0
        else:
            rss_sum = None
        return {
            "sample_start_monotonic": started,
            "sample_end_monotonic": time.monotonic(),
            "sample_gap_seconds": None if previous_sample_start is None else started - previous_sample_start,
            "sample_duration_seconds": time.monotonic() - started,
            "job_pids_before": sorted(first_pids),
            "job_pids_after": sorted(second_pids),
            "accounting_before": first_accounting,
            "accounting_after": second_accounting,
            "member_measurements": measured,
            "tree_rss_bytes": rss_sum,
            "rss_metric": "PSAPI_PROCESS_MEMORY_COUNTERS.WorkingSetSize sum; terminal empty Job reports 0 only when second PID list is empty, active_processes=0, and exited_processes=total_processes; other uncertain samples report None; Job committed-memory fields unused",
            "available_ram_bytes": available_ram,
            "total_ram_bytes": total_ram,
            "c_disk_free_bytes": c_free,
            "uncertainty": uncertainty,
            "uncertainty_count": len(uncertainty),
        }

    def evaluate(self, sample, no_progress_seconds):
        alerts = []
        if sample["uncertainty_count"]:
            alerts.append("SAMPLE_UNCERTAIN")
        rss = sample["tree_rss_bytes"]
        if rss is not None and rss > RSS_LIMIT_BYTES:
            alerts.append("TREE_RSS_GT_6_GIB")
        if sample["available_ram_bytes"] is not None and sample["available_ram_bytes"] < RAM_FLOOR_BYTES:
            alerts.append("AVAILABLE_RAM_LT_512_MIB")
        if sample["c_disk_free_bytes"] is not None and sample["c_disk_free_bytes"] < DISK_FLOOR_BYTES:
            alerts.append("C_DISK_FREE_LT_8_GIB")
        if no_progress_seconds >= NO_PROGRESS_LIMIT_SECONDS:
            alerts.append("NO_PROGRESS_GE_900S")
        return alerts

    def terminate_own_job(self, exit_code=91):
        if self.closed:
            raise JobGuardError("不能终止已关闭的Job句柄")
        if not kernel32.TerminateJobObject(self.handle, int(exit_code)):
            raise _win_error("TerminateJobObject(own candidate job)")

    def wait_empty_and_verify(self, timeout_seconds=30.0, root_must_exit=True):
        deadline = time.monotonic() + timeout_seconds
        root_key = (getattr(self, "root_pid", -1), getattr(self, "root_birth_ticks", -1))
        root = self.member_handles.get(root_key)
        if root is None:
            raise GateBlocked("没有已核root身份句柄")
        while time.monotonic() < deadline:
            pids = self.pid_list()
            accounting = self.accounting()
            root_wait = kernel32.WaitForSingleObject(root["handle"], 0)
            member_waits = [
                kernel32.WaitForSingleObject(member["handle"], 0)
                for member in self.member_handles.values()
            ]
            handles_closed = all(wait == WAIT_OBJECT_0 for wait in member_waits)
            root_closed = not root_must_exit or root_wait == WAIT_OBJECT_0
            if not pids and accounting["active_processes"] == 0 and handles_closed and root_closed:
                break
            time.sleep(0.05)
        else:
            raise GateBlocked(
                f"终态等待超时：pids={pids}, active={accounting['active_processes']}, "
                f"root_wait={root_wait}, member_waits={member_waits}"
            )
        repeated_pids = self.pid_list()
        repeated_accounting = self.accounting()
        if repeated_pids or repeated_accounting["active_processes"] != 0:
            raise GateBlocked("终态第二次Job成员读回不为空")
        root_wait = kernel32.WaitForSingleObject(root["handle"], 0)
        if root_must_exit and root_wait != WAIT_OBJECT_0:
            raise GateBlocked(f"root身份句柄未signal：wait={root_wait}")
        readbacks = []
        unknown = []
        alive = []
        for (pid, ticks), member in sorted(self.member_handles.items()):
            wait = kernel32.WaitForSingleObject(member["handle"], 0)
            actual_ticks = process_creation_ticks(member["handle"])
            if actual_ticks != ticks:
                unknown.append({"pid": pid, "reason": "HANDLE_BIRTH_TIME_CHANGED"})
                continue
            if wait == WAIT_TIMEOUT:
                alive.append(pid)
            elif wait != WAIT_OBJECT_0:
                unknown.append({"pid": pid, "reason": f"WAIT_UNKNOWN:{wait}"})
            else:
                exit_code = wintypes.DWORD()
                if not kernel32.GetExitCodeProcess(member["handle"], ctypes.byref(exit_code)):
                    unknown.append({"pid": pid, "reason": "GET_EXIT_CODE_FAILED"})
                elif exit_code.value == STILL_ACTIVE:
                    unknown.append({"pid": pid, "reason": "SIGNALED_BUT_STILL_ACTIVE"})
                else:
                    readbacks.append({"pid": pid, "birth_ticks": ticks, "exit_code": int(exit_code.value), "status": "EXITED"})
        if alive or unknown:
            raise GateBlocked(f"成员终态读回未闭合：alive={alive}, unknown={unknown}")
        final = {
            "job_pids": list(repeated_pids),
            "active_processes": repeated_accounting["active_processes"],
            "total_processes": repeated_accounting["total_processes"],
            "total_terminated_processes": repeated_accounting["terminated_processes"],
            "exited_processes": repeated_accounting["exited_processes"],
            "root_handle_signaled": root_wait == WAIT_OBJECT_0,
            "member_readbacks": readbacks,
            "live_members": alive,
            "unknown_members": unknown,
        }
        if len(readbacks) != repeated_accounting["total_processes"]:
            raise GateBlocked("终态已读回身份句柄数量与Job创建总数不同")
        return final

    def close(self):
        if self.closed:
            return
        errors = []
        if self.handle:
            handle = self.handle
            if _api_close_handle(handle):
                self.handle = None
            else:
                errors.append(f"CloseHandle(JobObject) WinError={ctypes.get_last_error()}")
        for key, member in list(self.member_handles.items()):
            handle = member.get("handle")
            if not handle:
                continue
            if _api_close_handle(handle):
                member["handle"] = None
            else:
                errors.append(f"CloseHandle(member PID={key[0]}, birth={key[1]}) WinError={ctypes.get_last_error()}")
        if errors:
            self.cleanup_errors.extend(errors)
            raise GateBlocked("Job/成员HANDLE清理失败：" + "；".join(errors))
        self.member_handles.clear()
        self.closed = self.handle is None


def api_sizes():
    return {
        "pointer_bits": ctypes.sizeof(ctypes.c_void_p) * 8,
        "BASIC_LIMIT_INFORMATION_bytes": ctypes.sizeof(BASIC_LIMIT_INFORMATION),
        "IO_COUNTERS_bytes": ctypes.sizeof(IO_COUNTERS),
        "EXTENDED_LIMIT_INFORMATION_bytes": ctypes.sizeof(EXTENDED_LIMIT_INFORMATION),
        "EXTENDED_LIMIT_INFORMATION.IoInfo_offset": EXTENDED_LIMIT_INFORMATION.IoInfo.offset,
        "BASIC_ACCOUNTING_INFORMATION_bytes": ctypes.sizeof(BASIC_ACCOUNTING_INFORMATION),
        "BASIC_ACCOUNTING_INFORMATION.ActiveProcesses_offset": BASIC_ACCOUNTING_INFORMATION.ActiveProcesses.offset,
        "PROCESS_MEMORY_COUNTERS_bytes": ctypes.sizeof(PROCESS_MEMORY_COUNTERS),
        "PROCESSENTRY32W_bytes": ctypes.sizeof(PROCESSENTRY32W),
        "BASIC_PROCESS_ID_LIST_header_bytes": 8,
        "BASIC_PROCESS_ID_LIST_ProcessIdList_offset": 8,
        "JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE": JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE,
        "JOB_OBJECT_LIMIT_BREAKAWAY_OK": False,
        "JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK": False,
        "rss_source": "PSAPI_PROCESS_MEMORY_COUNTERS.WorkingSetSize",
        "job_committed_memory_used_as_rss": False,
    }
