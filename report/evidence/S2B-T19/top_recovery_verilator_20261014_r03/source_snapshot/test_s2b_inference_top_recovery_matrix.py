import ctypes
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from ctypes import wintypes


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "top_recovery_verilator_20261014_r03"
EVIDENCE = ROOT / "report" / "evidence" / "S2B-T19" / RUN_ID
CACHE = ROOT / "tmp" / "2B" / "S2B-T19" / RUN_ID
TOOLCHAIN = Path(r"D:\FPGA_S2A_MSYS2_20261001\env")
VERILATOR = TOOLCHAIN / "mingw64" / "bin" / "verilator_bin.exe"
VERILATOR_ROOT = TOOLCHAIN / "mingw64" / "share" / "verilator"
MAKE = TOOLCHAIN / "usr" / "bin" / "make.exe"
GXX = TOOLCHAIN / "mingw64" / "bin" / "g++.exe"
EXPECTED_HEAD = "4ed359844e036f0e44c8f2648f8daab64b3b3116"
EXPECTED_BASELINE = {
    "sim/tb_s2b_inference_top_recovery.sv": "30b2b4c12a201142a4592980379baa13f536edf612d43a53b88b601edd5e909e",
    "src/s2b_inference_top.sv": "dffd20728b6a3b88c9c4a0c63987e10460a54728f5e348ccf1f8182e78c859c1",
    "src/s2b_control_csr.sv": "f884619e665502decbbb9186b4b79fa3f5d57c7ea0868a52d4af1f553a9a9629",
    "src/s2b_hp0_word_adapter.sv": "344f5553da157434039ec531ccef83cd74dba9c67533a0b88642438e5b5a8f62",
}
RTL_RELATIVE_PATHS = [
    "src/s2a_network_descriptor_pkg.sv",
    "src/s2b_maxpool_geometry.sv",
    "src/int8_maxpool_window.sv",
    "src/s2b_route_query.sv",
    "src/int8_upsample_query.sv",
    "src/s2b_conv_tile_engine.sv",
    "src/s2b_maxpool_engine.sv",
    "src/s2b_route_engine.sv",
    "src/s2b_upsample_engine.sv",
    "src/s2b_network_backend.sv",
    "src/s2a_memory_master.sv",
    "src/s2a_runtime_shell.sv",
    "src/s2b_stage2b_core.sv",
    "src/s2a_control_csr.sv",
    "src/s2b_request_guard.sv",
    "src/s2b_hp0_word_adapter.sv",
    "src/s2b_control_csr.sv",
    "src/s2b_inference_top.sv",
    "sim/tb_s2b_inference_top_recovery_matrix.sv",
]
WALL_TIMEOUT_SECONDS = {"compile": 600, "simulation": 60, "version": 30}
NO_PROGRESS_TIMEOUT_SECONDS = {"compile": 180, "simulation": 30, "version": 20}

GENERIC_READ = 0x80000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x00000080
HANDLE_FLAG_INHERIT = 0x00000001
CREATE_SUSPENDED = 0x00000004
CREATE_UNICODE_ENVIRONMENT = 0x00000400
CREATE_NO_WINDOW = 0x08000000
STARTF_USESTDHANDLES = 0x00000100
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION = 1
JOB_OBJECT_BASIC_PROCESS_ID_LIST = 3
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 258
INFINITE = 0xFFFFFFFF
STILL_ACTIVE = 259
PROCESS_ID_CAPACITY = 4096


class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("nLength", wintypes.DWORD),
        ("lpSecurityDescriptor", wintypes.LPVOID),
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


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    ]


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


class BASIC_PROCESS_ID_LIST(ctypes.Structure):
    _fields_ = [
        ("NumberOfAssignedProcesses", wintypes.DWORD),
        ("NumberOfProcessIdsInList", wintypes.DWORD),
        ("ProcessIdList", ctypes.c_size_t * PROCESS_ID_CAPACITY),
    ]


KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)
KERNEL32.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPWSTR]
KERNEL32.CreateJobObjectW.restype = wintypes.HANDLE
KERNEL32.SetInformationJobObject.argtypes = [
    wintypes.HANDLE,
    ctypes.c_int,
    wintypes.LPVOID,
    wintypes.DWORD,
]
KERNEL32.SetInformationJobObject.restype = wintypes.BOOL
KERNEL32.QueryInformationJobObject.argtypes = [
    wintypes.HANDLE,
    ctypes.c_int,
    wintypes.LPVOID,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
]
KERNEL32.QueryInformationJobObject.restype = wintypes.BOOL
KERNEL32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
KERNEL32.AssignProcessToJobObject.restype = wintypes.BOOL
KERNEL32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
KERNEL32.TerminateJobObject.restype = wintypes.BOOL
KERNEL32.CreateProcessW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.LPWSTR,
    wintypes.LPVOID,
    wintypes.LPVOID,
    wintypes.BOOL,
    wintypes.DWORD,
    wintypes.LPVOID,
    wintypes.LPCWSTR,
    ctypes.POINTER(STARTUPINFOW),
    ctypes.POINTER(PROCESS_INFORMATION),
]
KERNEL32.CreateProcessW.restype = wintypes.BOOL
KERNEL32.ResumeThread.argtypes = [wintypes.HANDLE]
KERNEL32.ResumeThread.restype = wintypes.DWORD
KERNEL32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
KERNEL32.WaitForSingleObject.restype = wintypes.DWORD
KERNEL32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
KERNEL32.GetExitCodeProcess.restype = wintypes.BOOL
KERNEL32.GetProcessId.argtypes = [wintypes.HANDLE]
KERNEL32.GetProcessId.restype = wintypes.DWORD
KERNEL32.QueryFullProcessImageNameW.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.LPWSTR,
    ctypes.POINTER(wintypes.DWORD),
]
KERNEL32.QueryFullProcessImageNameW.restype = wintypes.BOOL
KERNEL32.SetHandleInformation.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD]
KERNEL32.SetHandleInformation.restype = wintypes.BOOL
KERNEL32.CreateFileW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.DWORD,
    wintypes.DWORD,
    ctypes.POINTER(SECURITY_ATTRIBUTES),
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.HANDLE,
]
KERNEL32.CreateFileW.restype = wintypes.HANDLE
KERNEL32.CloseHandle.argtypes = [wintypes.HANDLE]
KERNEL32.CloseHandle.restype = wintypes.BOOL


def utc8_now():
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds")


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_row(relative_path):
    path = ROOT / Path(relative_path)
    if not path.is_file():
        raise FileNotFoundError(f"源文件不是普通文件：{path}")
    return {
        "path": relative_path.replace("\\", "/"),
        "absolute_path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def last_error(operation):
    return OSError(ctypes.get_last_error(), f"{operation}失敗")


def job_query(job, information_class, structure):
    returned = wintypes.DWORD()
    if not KERNEL32.QueryInformationJobObject(
        job,
        information_class,
        ctypes.byref(structure),
        ctypes.sizeof(structure),
        ctypes.byref(returned),
    ):
        raise last_error("QueryInformationJobObject")
    if returned.value != ctypes.sizeof(structure):
        raise RuntimeError("Job Object資訊讀回大小不符")
    return structure


def job_pids(job):
    record = BASIC_PROCESS_ID_LIST()
    returned = wintypes.DWORD()
    if not KERNEL32.QueryInformationJobObject(
        job,
        JOB_OBJECT_BASIC_PROCESS_ID_LIST,
        ctypes.byref(record),
        ctypes.sizeof(record),
        ctypes.byref(returned),
    ):
        raise last_error("QueryInformationJobObject(BasicProcessIdList)")
    if returned.value < 2 * ctypes.sizeof(wintypes.DWORD):
        raise RuntimeError("Job Object進程列表讀回長度過短")
    count = int(record.NumberOfProcessIdsInList)
    if count > PROCESS_ID_CAPACITY:
        raise RuntimeError("Job Object進程數超過固定讀回緩衝區")
    return [int(record.ProcessIdList[index]) for index in range(count)]


def job_active_count(job):
    record = job_query(job, JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION,
                       BASIC_ACCOUNTING_INFORMATION())
    return int(record.ActiveProcesses)


def wait_job_empty(job, timeout_seconds):
    deadline = time.monotonic() + timeout_seconds
    last_pids = []
    last_active = -1
    while time.monotonic() < deadline:
        last_pids = job_pids(job)
        last_active = job_active_count(job)
        if not last_pids and last_active == 0:
            repeated_pids = job_pids(job)
            repeated_active = job_active_count(job)
            if not repeated_pids and repeated_active == 0:
                return {
                    "job_pids": [],
                    "active_processes": 0,
                    "second_read_job_pids": repeated_pids,
                    "second_read_active_processes": repeated_active,
                }
        time.sleep(0.05)
    return {
        "job_pids": last_pids,
        "active_processes": last_active,
        "second_read_job_pids": None,
        "second_read_active_processes": None,
    }


def create_inheritable_nul():
    security = SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES), None, True)
    handle = KERNEL32.CreateFileW(
        "NUL",
        GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        ctypes.byref(security),
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        None,
    )
    if not handle or handle == wintypes.HANDLE(-1).value:
        raise last_error("CreateFileW(NUL)")
    return handle


def make_child_environment():
    environment = os.environ.copy()
    tool_bin = str(TOOLCHAIN / "mingw64" / "bin")
    make_bin = str(TOOLCHAIN / "usr" / "bin")
    environment["PATH"] = make_bin + os.pathsep + tool_bin + os.pathsep + environment.get("PATH", "")
    environment["VERILATOR_ROOT"] = str(VERILATOR_ROOT)
    return environment


def environment_buffer(environment):
    rows = sorted(environment.items(), key=lambda pair: pair[0].casefold())
    text = "\0".join(f"{key}={value}" for key, value in rows) + "\0\0"
    return ctypes.create_unicode_buffer(text)


def run_native_stage(name, executable, arguments, cwd, stdout_path, stderr_path):
    import msvcrt

    executable = str(Path(executable).resolve(strict=True))
    argv = [executable, *[str(value) for value in arguments]]
    stdout_file = open(stdout_path, "xb", buffering=0)
    stderr_file = open(stderr_path, "xb", buffering=0)
    job = None
    process_info = PROCESS_INFORMATION()
    nul_handle = None
    root_assigned = False
    record = {
        "name": name,
        "command": argv,
        "working_directory": str(Path(cwd).resolve(strict=True)),
        "started_at_utc8": utc8_now(),
        "native_exit_code": None,
        "runner_exit_code": None,
        "timed_out": False,
        "no_progress_timeout": False,
        "termination_requested": False,
        "root_pid": None,
        "root_image_readback": None,
        "job_limit_flags_expected": JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE,
        "job_before_close": None,
        "process_tree_closed": False,
        "cleanup_errors": [],
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
    }
    try:
        for output_file in (stdout_file, stderr_file):
            handle = wintypes.HANDLE(msvcrt.get_osfhandle(output_file.fileno()))
            if not KERNEL32.SetHandleInformation(
                handle, HANDLE_FLAG_INHERIT, HANDLE_FLAG_INHERIT
            ):
                raise last_error("SetHandleInformation(output inherit)")
        nul_handle = create_inheritable_nul()
        job = KERNEL32.CreateJobObjectW(None, None)
        if not job:
            raise last_error("CreateJobObjectW")
        limits = EXTENDED_LIMIT_INFORMATION()
        limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not KERNEL32.SetInformationJobObject(
            job,
            JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(limits),
            ctypes.sizeof(limits),
        ):
            raise last_error("SetInformationJobObject")
        readback = job_query(job, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
                             EXTENDED_LIMIT_INFORMATION())
        flags = int(readback.BasicLimitInformation.LimitFlags)
        record["job_limit_flags_readback"] = flags
        if flags != JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE:
            raise RuntimeError(f"Job Object限制旗標讀回不符：0x{flags:x}")
        if job_pids(job) or job_active_count(job) != 0:
            raise RuntimeError("啟動前本任務Job Object不是空集合")

        startup = STARTUPINFOW()
        startup.cb = ctypes.sizeof(STARTUPINFOW)
        startup.dwFlags = STARTF_USESTDHANDLES
        startup.hStdInput = nul_handle
        startup.hStdOutput = wintypes.HANDLE(msvcrt.get_osfhandle(stdout_file.fileno()))
        startup.hStdError = wintypes.HANDLE(msvcrt.get_osfhandle(stderr_file.fileno()))
        environment = environment_buffer(make_child_environment())
        command_line = ctypes.create_unicode_buffer(subprocess.list2cmdline(argv))
        created = KERNEL32.CreateProcessW(
            executable,
            command_line,
            None,
            None,
            True,
            CREATE_SUSPENDED | CREATE_UNICODE_ENVIRONMENT | CREATE_NO_WINDOW,
            ctypes.cast(environment, wintypes.LPVOID),
            record["working_directory"],
            ctypes.byref(startup),
            ctypes.byref(process_info),
        )
        if not created:
            raise last_error("CreateProcessW(CREATE_SUSPENDED)")
        record["root_pid"] = int(process_info.dwProcessId)
        if KERNEL32.GetProcessId(process_info.hProcess) != process_info.dwProcessId:
            raise RuntimeError("root process HANDLE PID讀回不符")
        image_buffer = ctypes.create_unicode_buffer(32768)
        image_length = wintypes.DWORD(len(image_buffer))
        if not KERNEL32.QueryFullProcessImageNameW(
            process_info.hProcess, 0, image_buffer, ctypes.byref(image_length)
        ):
            raise last_error("QueryFullProcessImageNameW")
        record["root_image_readback"] = image_buffer.value
        if os.path.normcase(os.path.abspath(image_buffer.value)) != os.path.normcase(executable):
            raise RuntimeError("root process映像路徑與指定Verilator/tool映像不符")
        if not KERNEL32.AssignProcessToJobObject(job, process_info.hProcess):
            raise last_error("AssignProcessToJobObject")
        root_assigned = True
        before_resume_pids = job_pids(job)
        before_resume_active = job_active_count(job)
        if before_resume_pids != [int(process_info.dwProcessId)] or before_resume_active != 1:
            raise RuntimeError("ResumeThread前Job成員沒有精確收斂至本次root")
        record["job_before_resume_pids"] = before_resume_pids
        record["job_before_resume_active_processes"] = before_resume_active
        resume_count = KERNEL32.ResumeThread(process_info.hThread)
        if resume_count == 0xFFFFFFFF:
            raise last_error("ResumeThread")
        record["resume_thread_previous_suspend_count"] = int(resume_count)
        if resume_count != 1:
            raise RuntimeError(f"ResumeThread先前掛起計數不是1：{resume_count}")
        record["resumed_at_utc8"] = utc8_now()

        for inherited_handle in (startup.hStdOutput, startup.hStdError, nul_handle):
            if not KERNEL32.SetHandleInformation(inherited_handle, HANDLE_FLAG_INHERIT, 0):
                raise last_error("SetHandleInformation(clear inherit)")
        if not KERNEL32.CloseHandle(nul_handle):
            raise last_error("CloseHandle(parent NUL)")
        nul_handle = None

        wall_budget = WALL_TIMEOUT_SECONDS.get(name, 60)
        progress_budget = NO_PROGRESS_TIMEOUT_SECONDS.get(name, 30)
        deadline = time.monotonic() + wall_budget
        last_progress_time = time.monotonic()
        last_sizes = (Path(stdout_path).stat().st_size, Path(stderr_path).stat().st_size)
        wait_result = None
        while True:
            wait_result = KERNEL32.WaitForSingleObject(process_info.hProcess, 100)
            if wait_result == WAIT_OBJECT_0:
                break
            if wait_result != WAIT_TIMEOUT:
                raise RuntimeError(f"root WaitForSingleObject返回未知值：{wait_result}")
            now = time.monotonic()
            sizes = (Path(stdout_path).stat().st_size, Path(stderr_path).stat().st_size)
            if sizes != last_sizes:
                last_sizes = sizes
                last_progress_time = now
            if now >= deadline:
                record["timed_out"] = True
                record["termination_reason"] = "WALL_TIMEOUT"
                break
            if now - last_progress_time >= progress_budget:
                record["timed_out"] = True
                record["no_progress_timeout"] = True
                record["termination_reason"] = "NO_PROGRESS_TIMEOUT"
                break

        if record["timed_out"]:
            record["termination_requested"] = True
            if not KERNEL32.TerminateJobObject(job, 124):
                raise last_error("TerminateJobObject(timeout)")
            root_wait = KERNEL32.WaitForSingleObject(process_info.hProcess, 30000)
            if root_wait != WAIT_OBJECT_0:
                raise RuntimeError(f"超時後root進程未於30秒內退出：{root_wait}")

        exit_code = wintypes.DWORD()
        if not KERNEL32.GetExitCodeProcess(process_info.hProcess, ctypes.byref(exit_code)):
            raise last_error("GetExitCodeProcess")
        if exit_code.value == STILL_ACTIVE:
            raise RuntimeError("root HANDLE已signal但退出碼仍是STILL_ACTIVE")
        record["native_exit_code"] = int(exit_code.value)

        tree_state = wait_job_empty(job, 30.0)
        if tree_state["active_processes"] != 0 or tree_state["job_pids"]:
            record["cleanup_errors"].append("自然退出後子進程仍存活，已終止本次Job")
            record["termination_requested"] = True
            if not KERNEL32.TerminateJobObject(job, 125):
                record["cleanup_errors"].append(
                    f"TerminateJobObject(殘留子進程)失敗：{ctypes.get_last_error()}"
                )
            tree_state = wait_job_empty(job, 30.0)
        record["job_before_close"] = tree_state
        record["process_tree_closed"] = (
            tree_state["active_processes"] == 0
            and not tree_state["job_pids"]
            and tree_state["second_read_active_processes"] == 0
            and tree_state["second_read_job_pids"] == []
        )
        record["runner_exit_code"] = (
            124 if record["timed_out"] else
            (0 if record["native_exit_code"] == 0 and record["process_tree_closed"]
             and not record["cleanup_errors"] else 1)
        )
    except BaseException as error:
        record["error"] = f"{type(error).__name__}: {error}"
        record["cleanup_errors"].append(traceback.format_exc())
        if job and root_assigned:
            record["termination_requested"] = True
            KERNEL32.TerminateJobObject(job, 125)
            if process_info.hProcess:
                KERNEL32.WaitForSingleObject(process_info.hProcess, 30000)
            tree_state = wait_job_empty(job, 30.0)
            record["job_before_close"] = tree_state
            record["process_tree_closed"] = (
                tree_state["active_processes"] == 0 and not tree_state["job_pids"]
                and tree_state["second_read_active_processes"] == 0
                and tree_state["second_read_job_pids"] == []
            )
        record["runner_exit_code"] = 1
    finally:
        if nul_handle:
            KERNEL32.CloseHandle(nul_handle)
        if job:
            if not record["process_tree_closed"]:
                KERNEL32.TerminateJobObject(job, 125)
                if process_info.hProcess:
                    KERNEL32.WaitForSingleObject(process_info.hProcess, 30000)
                try:
                    tree_state = wait_job_empty(job, 30.0)
                    record["job_before_close_final"] = tree_state
                    record["process_tree_closed"] = (
                        tree_state["active_processes"] == 0 and not tree_state["job_pids"]
                        and tree_state["second_read_active_processes"] == 0
                        and tree_state["second_read_job_pids"] == []
                    )
                except BaseException as cleanup_error:
                    record["cleanup_errors"].append(
                        f"最終Job閉合核查失敗：{cleanup_error!r}"
                    )
            KERNEL32.CloseHandle(job)
        for name_handle in ("hThread", "hProcess"):
            handle = getattr(process_info, name_handle)
            if handle:
                KERNEL32.CloseHandle(handle)
                setattr(process_info, name_handle, None)
        stdout_file.close()
        stderr_file.close()
        record["finished_at_utc8"] = utc8_now()
        record["stdout_bytes"] = Path(stdout_path).stat().st_size
        record["stderr_bytes"] = Path(stderr_path).stat().st_size
        if not record["process_tree_closed"] and record["runner_exit_code"] == 0:
            record["runner_exit_code"] = 1
    return record


def parse_result_lines(simulation_text):
    results = {}
    for line in simulation_text.splitlines():
        if not line.startswith("RESULT scenario="):
            continue
        fields = {}
        for item in line.split():
            if "=" in item:
                key, value = item.split("=", 1)
                fields[key] = value
        scenario = fields.get("scenario")
        if scenario in results:
            raise RuntimeError(f"仿真重複輸出scenario={scenario}結果行")
        results[scenario] = fields
    return results


def validate_results(simulation_text):
    results = parse_result_lines(simulation_text)
    expected = {
        "1": {
            "name": "late_slverr",
            "first_error": "5",
            "isolated_state": "6",
            "final_state": "5",
            "final_owner": "0",
            "final_safe": "1",
            "final_pending": "0",
            "detail": "0x08",
            "epoch": "0x0000000000000001",
            "ack_epoch": "0x0000000000000001",
            "ack_status": "0",
            "restarted_epoch": "0x0000000000000002",
            "ar_count": "2",
            "r_count": "1",
            "late_rresp": "2",
            "late_rlast": "1",
        },
        "2": {
            "name": "protocol_isolation",
            "first_error": "8",
            "state": "6",
            "owner": "1",
            "safe": "0",
            "pending": "0",
            "pending_after_bad": "1",
            "error_after_bad": "8",
            "detail": "0x18",
            "epoch": "0x0000000000000002",
            "ack_epoch_after_attempt": "0x0000000000000001",
            "pre_ack_epoch_low_bresp": "2",
            "pre_ack_epoch_high_bresp": "2",
            "pre_ack_bresp": "2",
            "pre_start_bresp": "2",
            "post_ack_epoch_low_bresp": "2",
            "post_ack_epoch_high_bresp": "2",
            "post_ack_bresp": "2",
            "post_start_bresp": "2",
            "bad_rresp": "0",
            "bad_rlast": "0",
            "ar_count": "2",
            "r_count": "3",
        },
    }
    if set(results) != set(expected):
        raise RuntimeError(f"仿真scenario結果集合不符：observed={sorted(results)}")
    for scenario, expected_fields in expected.items():
        for field, wanted in expected_fields.items():
            observed = results[scenario].get(field)
            if observed != wanted:
                raise RuntimeError(
                    f"scenario={scenario} {field}不符：observed={observed!r} expected={wanted!r}"
                )
    if simulation_text.count("PASS TOP_RECOVERY_MATRIX scenarios=2 ") != 1:
        raise RuntimeError("沒有唯一完整矩陣PASS marker")
    return results


def copy_source_snapshots(source_rows, snapshot_dir):
    snapshot_dir.mkdir(exist_ok=False)
    copied = []
    all_rows = list(source_rows)
    runner_row = source_row("verification/test_s2b_inference_top_recovery_matrix.py")
    all_rows.append(runner_row)
    for row in all_rows:
        relative = row["path"]
        destination = snapshot_dir / Path(relative).name
        with open(row["absolute_path"], "rb") as source, open(destination, "xb") as target:
            while True:
                block = source.read(1024 * 1024)
                if not block:
                    break
                target.write(block)
        snapshot_hash = sha256_file(destination)
        if snapshot_hash != row["sha256"]:
            raise RuntimeError(f"source snapshot SHA不符：{relative}")
        copied.append({**row, "snapshot_path": str(destination), "snapshot_sha256": snapshot_hash})
    return copied


def git_head():
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git rev-parse HEAD失敗：{completed.stderr.strip()}")
    return completed.stdout.strip()


def run_version_stage(name, executable, argument, raw_dir):
    return run_native_stage(
        name,
        executable,
        [argument],
        ROOT,
        raw_dir / f"{name}_stdout.txt",
        raw_dir / f"{name}_stderr.txt",
    )


def main():
    if os.name != "nt":
        raise RuntimeError("此runner僅支援Windows原生Job Object執行")
    if git_head() != EXPECTED_HEAD:
        raise RuntimeError(f"HEAD不符：actual={git_head()} expected={EXPECTED_HEAD}")
    for relative, expected_hash in EXPECTED_BASELINE.items():
        actual_hash = sha256_file(ROOT / Path(relative))
        if actual_hash != expected_hash:
            raise RuntimeError(f"源碼基線SHA不符：{relative} actual={actual_hash}")
    for path, kind in ((TOOLCHAIN, "dir"), (VERILATOR, "file"),
                       (VERILATOR_ROOT, "dir"), (MAKE, "file"), (GXX, "file")):
        valid = path.is_dir() if kind == "dir" else path.is_file()
        if not valid:
            raise FileNotFoundError(f"批准工具路徑不存在或類型錯誤：{path}")
    if EVIDENCE.exists() or CACHE.exists():
        raise FileExistsError("拒絕覆蓋既有RunId；證據或cache路徑已存在")
    if not EVIDENCE.parent.is_dir() or not CACHE.parent.is_dir():
        raise FileNotFoundError("唯一證據/cache目標的精確父目錄不存在")

    EVIDENCE.mkdir(exist_ok=False)
    CACHE.mkdir(exist_ok=False)
    raw_dir = EVIDENCE / "raw"
    raw_dir.mkdir(exist_ok=False)
    initial_rows = [source_row(relative) for relative in RTL_RELATIVE_PATHS]
    snapshot_rows = copy_source_snapshots(initial_rows, EVIDENCE / "source_snapshot")
    tool_rows = []
    for role, path in (("verilator", VERILATOR), ("make", MAKE), ("g++", GXX),
                       ("python", Path(sys.executable).resolve(strict=True))):
        tool_rows.append({"role": role, "path": str(path), "bytes": path.stat().st_size,
                          "sha256": sha256_file(path)})

    manifest = {
        "schema_version": "gestureforge_s2b_t19_top_recovery_matrix_v1",
        "task_id": "S2B-T19-R03",
        "run_id": RUN_ID,
        "created_at_utc8": utc8_now(),
        "workspace": str(ROOT),
        "source_commit": EXPECTED_HEAD,
        "top_module": "tb_s2b_inference_top_recovery_matrix",
        "scope": "只驗證真實頂層RTL及公開AXI-Lite CSR的離線RTL數字仿真；可見性僅是仿真假設",
        "board_or_cache_verification": "NOT_RUN",
        "baseline_sources": [
            {"path": relative, "expected_sha256": expected_hash,
             "observed_sha256": sha256_file(ROOT / Path(relative))}
            for relative, expected_hash in EXPECTED_BASELINE.items()
        ],
        "sources": snapshot_rows,
        "tools": tool_rows,
        "toolchain_root": str(TOOLCHAIN),
        "verilator_root": str(VERILATOR_ROOT),
        "timeouts_seconds": {
            "compile_wall": WALL_TIMEOUT_SECONDS["compile"],
            "compile_no_progress": NO_PROGRESS_TIMEOUT_SECONDS["compile"],
            "simulation_wall": WALL_TIMEOUT_SECONDS["simulation"],
            "simulation_no_progress": NO_PROGRESS_TIMEOUT_SECONDS["simulation"],
        },
        "process_isolation": {
            "mechanism": "每個native子進程以CREATE_SUSPENDED建立，加入獨立KILL_ON_JOB_CLOSE Job Object後才ResumeThread",
            "single_job": True,
            "job_closed_after_each_command": True,
        },
        "commands": [],
        "scenario_results": {},
        "result": "RUNNING",
        "errors": [],
    }

    try:
        for role, executable in (("version", VERILATOR), ("make_version", MAKE),
                                 ("compiler_version", GXX)):
            stage = run_version_stage(role, executable, "--version", raw_dir)
            manifest["commands"].append(stage)
            if stage.get("runner_exit_code") != 0:
                raise RuntimeError(f"工具版本讀取或Job閉合失敗：{role}")

        mdir = CACHE / "build"
        python_literal = f"PYTHON3='\"{Path(sys.executable).resolve(strict=True)}\"'"
        compile_arguments = [
            "--binary", "--timing", "--timescale", "1ns/1ps",
            "-Wall", "-Wno-fatal", "-j", "1", "--threads", "1",
            "--output-split", "10000", "--output-split-cfuncs", "100",
            "--top-module", "tb_s2b_inference_top_recovery_matrix",
            "--Mdir", str(mdir),
            "-MAKEFLAGS", python_literal,
            "-CFLAGS", "-D_GLIBCXX_USE_CXX11_ABI=0 -O0",
            *[str(ROOT / Path(relative)) for relative in RTL_RELATIVE_PATHS],
        ]
        compile_stage = run_native_stage(
            "compile", VERILATOR, compile_arguments, ROOT,
            raw_dir / "verilator_compile_stdout.txt",
            raw_dir / "verilator_compile_stderr.txt",
        )
        compile_text = (
            (raw_dir / "verilator_compile_stdout.txt").read_text(encoding="utf-8", errors="replace")
            + "\n" + (raw_dir / "verilator_compile_stderr.txt").read_text(encoding="utf-8", errors="replace")
        )
        compile_stage["warning_count"] = len(re.findall(r"(?m)^%Warning[^:\r\n]*:", compile_text))
        compile_stage["error_count"] = len(re.findall(r"(?m)^%Error[^:\r\n]*:", compile_text))
        compile_stage["source_hashes_unchanged"] = all(
            sha256_file(ROOT / Path(row["path"])) == row["sha256"]
            for row in initial_rows
        )
        manifest["commands"].append(compile_stage)
        if (compile_stage.get("runner_exit_code") != 0
                or compile_stage.get("native_exit_code") != 0
                or compile_stage["error_count"] != 0
                or not compile_stage["source_hashes_unchanged"]):
            raise RuntimeError("Verilator編譯失敗、輸入源漂移或編譯Job未閉合")

        binary = mdir / "Vtb_s2b_inference_top_recovery_matrix.exe"
        if not binary.is_file():
            raise FileNotFoundError(f"Verilator沒有生成預期仿真程式：{binary}")
        simulation_stage = run_native_stage(
            "simulation", binary, [], mdir,
            raw_dir / "verilator_simulation_stdout.txt",
            raw_dir / "verilator_simulation_stderr.txt",
        )
        sim_text = (
            (raw_dir / "verilator_simulation_stdout.txt").read_text(encoding="utf-8", errors="replace")
            + "\n" + (raw_dir / "verilator_simulation_stderr.txt").read_text(encoding="utf-8", errors="replace")
        )
        manifest["commands"].append(simulation_stage)
        if (simulation_stage.get("runner_exit_code") != 0
                or simulation_stage.get("native_exit_code") != 0):
            raise RuntimeError("Verilator仿真native退出失败或仿真Job未闭合")
        manifest["scenario_results"] = validate_results(sim_text)
        manifest["result"] = "PASS_RTL_SIMULATION_ONLY"
    except BaseException as error:
        manifest["errors"].append({"type": type(error).__name__, "message": str(error),
                                   "traceback": traceback.format_exc()})
        if not manifest["commands"]:
            manifest["result"] = "BLOCKED_PREFLIGHT_OR_SETUP"
        elif any(command.get("name") == "simulation" for command in manifest["commands"]):
            manifest["result"] = "FAIL_SIMULATION_OR_SEMANTICS"
        else:
            manifest["result"] = "FAIL_TOOL_OR_COMPILE"
    finally:
        final_source_rows = []
        for row in initial_rows:
            final_row = source_row(row["path"])
            final_source_rows.append(final_row)
        manifest["sources_after_run"] = final_source_rows
        manifest["all_sources_unchanged"] = all(
            before["sha256"] == after["sha256"]
            for before, after in zip(initial_rows, final_source_rows)
        )
        manifest["finished_at_utc8"] = utc8_now()
        manifest["evidence_directory"] = str(EVIDENCE)
        manifest["cache_directory"] = str(CACHE)
        manifest["manifest_path"] = str(EVIDENCE / "manifest.json")
        with open(EVIDENCE / "manifest.json", "x", encoding="utf-8", newline="\n") as output:
            json.dump(manifest, output, ensure_ascii=False, indent=2)
            output.write("\n")
    print(json.dumps({"result": manifest["result"], "run_id": RUN_ID,
                      "manifest": str(EVIDENCE / "manifest.json"),
                      "error_count": len(manifest["errors"])}, ensure_ascii=False))
    return 0 if manifest["result"] == "PASS_RTL_SIMULATION_ONLY" and manifest["all_sources_unchanged"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BaseException as error:
        print(f"RUNNER_START_FAILURE {type(error).__name__}: {error}", file=sys.stderr)
        raise
