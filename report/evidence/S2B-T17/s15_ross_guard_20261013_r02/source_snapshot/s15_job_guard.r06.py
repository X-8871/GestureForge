"""仅用于 S15 Job Object 门禁候选和隔离 fixture。"""
import ctypes
import json
import os
import secrets
import struct
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


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
psapi = ctypes.WinDLL("psapi", use_last_error=True)
kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
kernel32.CreateJobObjectW.restype = wintypes.HANDLE
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


def _is_in_job(process_handle, job_handle):
    answer = wintypes.BOOL()
    if not kernel32.IsProcessInJob(process_handle, job_handle, ctypes.byref(answer)):
        raise _win_error("IsProcessInJob")
    return bool(answer.value)


def process_table():
    """Toolhelp单快照读取PID及父PID；API失败不降级到推测。"""
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    invalid = ctypes.c_void_p(-1).value
    if not snapshot or snapshot == invalid:
        raise _win_error("CreateToolhelp32Snapshot")
    rows = {}
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(entry)
        if not kernel32.Process32FirstW(snapshot, ctypes.byref(entry)):
            raise _win_error("Process32FirstW")
        while True:
            pid = int(entry.th32ProcessID)
            if pid:
                rows[pid] = int(entry.th32ParentProcessID)
            entry.dwSize = ctypes.sizeof(entry)
            if not kernel32.Process32NextW(snapshot, ctypes.byref(entry)):
                code = ctypes.get_last_error()
                if code == ERROR_NO_MORE_FILES:
                    break
                ctypes.set_last_error(code)
                raise _win_error("Process32NextW")
    finally:
        kernel32.CloseHandle(snapshot)
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
    handle = _open_process(pid, access)
    try:
        ticks = process_creation_ticks(handle)
        identity = process_identity(pid)
        after_ticks = process_creation_ticks(handle)
        if ticks != after_ticks:
            raise GateBlocked("进程句柄出生时间漂移")
        return handle, ticks, identity
    except BaseException:
        kernel32.CloseHandle(handle)
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


class JobObject:
    """仅持有当前候选Job；默认关闭句柄时终止本Job成员。"""

    def __init__(self, kill_on_close=True):
        self.handle = kernel32.CreateJobObjectW(None, None)
        if not self.handle:
            raise _win_error("CreateJobObjectW")
        self.closed = False
        self.member_handles = {}
        self._ready_nonce = secrets.token_bytes(32)
        self._ready_token = None
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
        self.flags = self.query_limit_flags()
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
            pids = struct.unpack_from("<" + "Q" * listed, buffer.raw, 8) if listed else ()
            if len(pids) != assigned or len(set(pids)) != len(pids):
                raise GateBlocked("Job PID列表计数或PID唯一性不符")
            return tuple(sorted(int(pid) for pid in pids))
        raise GateBlocked("Job PID列表超过4096个成员")

    def membership(self, pid):
        handle = _open_process(pid, PROCESS_QUERY_INFORMATION | SYNCHRONIZE)
        try:
            return _is_in_job(handle, self.handle)
        finally:
            kernel32.CloseHandle(handle)

    def _remember_process(self, pid, access):
        handle, ticks, identity = _open_process_identity_handle(pid, access)
        key = (int(pid), int(ticks))
        current = self.member_handles.get(key)
        if current is not None:
            kernel32.CloseHandle(handle)
            if not _identity_equal(current["identity"], identity):
                raise GateBlocked("已核PID出生身份的六字段漂移")
            return current
        self.member_handles[key] = {"handle": handle, "birth_ticks": ticks, "identity": identity}
        return self.member_handles[key]

    def attach_idle_root(self, ross_record):
        session_id, ross_identity = parse_ross_idle_record(ross_record)
        actual = process_identity(ross_identity["pid"])
        if not _identity_equal(ross_identity, actual):
            raise GateBlocked("ROSS六字段与本机root读回不同")
        root_pid = int(ross_identity["pid"])
        before_descendants = descendants(root_pid)
        if before_descendants:
            raise GateBlocked(f"READY前发现既有后代，拒绝移入任务：{sorted(before_descendants)}")
        access = PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | PROCESS_SET_QUOTA | PROCESS_TERMINATE | SYNCHRONIZE
        root = self._remember_process(root_pid, access)
        root_outer_job = _is_in_job(root["handle"], None)
        if not kernel32.AssignProcessToJobObject(self.handle, root["handle"]):
            raise _win_error("AssignProcessToJobObject(root)")
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

    def _verify_ready_membership(self):
        previous = None
        for _ in range(8):
            current_identity = process_identity(self.root_pid)
            if not _identity_equal(current_identity, self.root_identity):
                raise GateBlocked("READY期间root六字段变化")
            first_pids = set(self.pid_list())
            first_accounting = self.accounting()
            tree = descendants(self.root_pid)
            tree_members = {self.root_pid} | tree
            for pid in tree_members:
                if not self.membership(pid):
                    raise GateBlocked(f"现存root后代未被Job捕获：PID {pid}")
                self._remember_process(
                    pid,
                    PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | SYNCHRONIZE,
                )
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
                if not _is_in_job(root["handle"], self.handle):
                    raise GateBlocked("root Job归属读回失败")
                return
            previous = state
            time.sleep(0.05)
        raise GateBlocked("Job成员集合/进程树/Accounting未能稳定闭合READY")

    def dispatch_after_ready(self, ready_token, host_stdin, command):
        if (
            not isinstance(ready_token, _ReadyToken)
            or ready_token.owner is not self
            or ready_token.nonce is not self._ready_nonce
            or ready_token is not self._ready_token
            or self._dispatch_used
        ):
            raise GateBlocked("heavy dispatch缺少本次READY收据")
        ready_receipt = ready_token.receipt
        if ready_receipt.get("session_id") != self.session_id or ready_receipt.get("root_identity") != self.root_identity:
            raise GateBlocked("READY收据与当前ROSS会话/root身份不绑定")
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
        rss_sum = sum(item["rss_bytes"] for item in measured) if not uncertainty else None
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
            "rss_metric": "PSAPI_PROCESS_MEMORY_COUNTERS.WorkingSetSize sum; Job committed-memory fields unused",
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
        handle, self.handle = self.handle, None
        self.closed = True
        if handle:
            kernel32.CloseHandle(handle)
        for member in self.member_handles.values():
            kernel32.CloseHandle(member["handle"])
        self.member_handles.clear()


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
