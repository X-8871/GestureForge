"""仅显式执行离线探针；通过挂起创建与 Windows Job 约束本轮进程树。"""

import argparse
import ctypes as C
from ctypes import wintypes as W
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
BAT = Path(r"D:\Xilinx\2026.1\Vitis\bin\xsdb.bat")
PROBE = HERE / "probe.tcl"
PROBE_BYTES = b"puts [info patchlevel]\nexit\n"
TOOLS = [BAT, BAT.parent / "setupEnv.bat", BAT.parent / "loader.bat",
         BAT.parent / "rdiArgs.bat", BAT.parent / "unwrapped/win64.o/xsdb.exe",
         BAT.parent.parent / "lib/win64.o/tcl86t.dll"]
WAIT_OBJECT_0, WAIT_TIMEOUT = 0, 258


class STARTUPINFO(C.Structure):
    _fields_ = [("cb", W.DWORD), ("lpReserved", W.LPWSTR), ("lpDesktop", W.LPWSTR),
                ("lpTitle", W.LPWSTR), ("dwX", W.DWORD), ("dwY", W.DWORD),
                ("dwXSize", W.DWORD), ("dwYSize", W.DWORD), ("dwXCountChars", W.DWORD),
                ("dwYCountChars", W.DWORD), ("dwFillAttribute", W.DWORD),
                ("dwFlags", W.DWORD), ("wShowWindow", W.WORD), ("cbReserved2", W.WORD),
                ("lpReserved2", C.POINTER(C.c_byte)), ("hStdInput", W.HANDLE),
                ("hStdOutput", W.HANDLE), ("hStdError", W.HANDLE)]


class STARTUPINFOEX(C.Structure):
    _fields_ = [("StartupInfo", STARTUPINFO), ("lpAttributeList", W.LPVOID)]


class PROCESS_INFORMATION(C.Structure):
    _fields_ = [("hProcess", W.HANDLE), ("hThread", W.HANDLE),
                ("dwProcessId", W.DWORD), ("dwThreadId", W.DWORD)]


class BASIC_LIMIT(C.Structure):
    _fields_ = [("PerProcessUserTimeLimit", C.c_int64), ("PerJobUserTimeLimit", C.c_int64),
                ("LimitFlags", W.DWORD), ("MinimumWorkingSetSize", C.c_size_t),
                ("MaximumWorkingSetSize", C.c_size_t), ("ActiveProcessLimit", W.DWORD),
                ("Affinity", C.c_size_t), ("PriorityClass", W.DWORD),
                ("SchedulingClass", W.DWORD)]


class IO_COUNTERS(C.Structure):
    _fields_ = [(name, C.c_uint64) for name in ("ReadOperationCount", "WriteOperationCount",
                "OtherOperationCount", "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]


class EXTENDED_LIMIT(C.Structure):
    _fields_ = [("BasicLimitInformation", BASIC_LIMIT), ("IoInfo", IO_COUNTERS),
                ("ProcessMemoryLimit", C.c_size_t), ("JobMemoryLimit", C.c_size_t),
                ("PeakProcessMemoryUsed", C.c_size_t), ("PeakJobMemoryUsed", C.c_size_t)]


class ACCOUNTING(C.Structure):
    _fields_ = [("TotalUserTime", C.c_int64), ("TotalKernelTime", C.c_int64),
                ("ThisPeriodTotalUserTime", C.c_int64), ("ThisPeriodTotalKernelTime", C.c_int64),
                ("TotalPageFaultCount", W.DWORD), ("TotalProcesses", W.DWORD),
                ("ActiveProcesses", W.DWORD), ("TotalTerminatedProcesses", W.DWORD)]


class Native:
    """所有结束操作仅使用本轮创建的 Job 或根进程句柄。"""

    def __init__(self):
        if os.name != "nt":
            raise RuntimeError("Windows only")
        self.k = C.WinDLL("kernel32", use_last_error=True)
        signatures = {
            "CreateJobObjectW": ([W.LPVOID, W.LPCWSTR], W.HANDLE),
            "SetInformationJobObject": ([W.HANDLE, C.c_int, W.LPVOID, W.DWORD], W.BOOL),
            "QueryInformationJobObject": ([W.HANDLE, C.c_int, W.LPVOID, W.DWORD, W.LPVOID], W.BOOL),
            "AssignProcessToJobObject": ([W.HANDLE, W.HANDLE], W.BOOL),
            "TerminateJobObject": ([W.HANDLE, W.UINT], W.BOOL),
            "TerminateProcess": ([W.HANDLE, W.UINT], W.BOOL),
            "CloseHandle": ([W.HANDLE], W.BOOL),
            "WaitForSingleObject": ([W.HANDLE, W.DWORD], W.DWORD),
            "GetExitCodeProcess": ([W.HANDLE, C.POINTER(W.DWORD)], W.BOOL),
            "ResumeThread": ([W.HANDLE], W.DWORD),
            "InitializeProcThreadAttributeList": ([W.LPVOID, W.DWORD, W.DWORD, C.POINTER(C.c_size_t)], W.BOOL),
            "UpdateProcThreadAttribute": ([W.LPVOID, W.DWORD, C.c_size_t, W.LPVOID, C.c_size_t, W.LPVOID, W.LPVOID], W.BOOL),
            "DeleteProcThreadAttributeList": ([W.LPVOID], None),
            "CreateProcessW": ([W.LPCWSTR, W.LPWSTR, W.LPVOID, W.LPVOID, W.BOOL,
                                W.DWORD, W.LPVOID, W.LPCWSTR, W.LPVOID, C.POINTER(PROCESS_INFORMATION)], W.BOOL),
        }
        for name, (args, result) in signatures.items():
            function = getattr(self.k, name)
            function.argtypes, function.restype = args, result

    def checked(self, ok, operation):
        if not ok:
            raise OSError(C.get_last_error(), operation)
        return ok

    def assign(self, job, process):
        self.checked(self.k.AssignProcessToJobObject(job, process), "AssignProcessToJobObject")

    def terminate_job(self, job):
        self.checked(self.k.TerminateJobObject(job, 124), "TerminateJobObject")

    def accounting(self, job):
        info = ACCOUNTING()
        self.checked(self.k.QueryInformationJobObject(job, 1, C.byref(info), C.sizeof(info), None),
                     "QueryInformationJobObject(accounting)")
        return {name: int(getattr(info, name)) for name in
                ("TotalProcesses", "ActiveProcesses", "TotalTerminatedProcesses")}

    def pids(self, job):
        # 固定上限用于证据采样；失败时拒绝判定成功，绝不按 PID 结束进程。
        buffer = C.create_string_buffer(8 + C.sizeof(C.c_size_t) * 1024)
        self.checked(self.k.QueryInformationJobObject(job, 3, buffer, len(buffer), None),
                     "QueryInformationJobObject(process_ids)")
        count = C.cast(C.addressof(buffer) + 4, C.POINTER(W.DWORD))[0]
        return list((C.c_size_t * count).from_address(C.addressof(buffer) + 8))


def run_job(application, command_line, cwd, environment, output_dir, timeout, api=None):
    """运行受限本轮进程树，并在返回前终止 Job 中的全部剩余进程。"""
    import msvcrt
    if not (0 < timeout <= 600):
        raise ValueError("M3任务超时必须大于0且不超过600秒")
    api = api or Native()
    k = api.k
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=False)
    result = {"application": str(application), "command_line": command_line,
              "cwd": str(cwd), "timeout_seconds": timeout,
              "creation_flags": ["CREATE_SUSPENDED", "CREATE_NO_WINDOW",
                                 "CREATE_UNICODE_ENVIRONMENT", "EXTENDED_STARTUPINFO_PRESENT"],
              "job_limit_flags": ["JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE"],
              "breakaway_allowed": False, "resumed": False, "assigned": False,
              "timed_out": False, "cleanup_confirmed": False, "errors": [], "job_samples": []}
    job = None
    pi = PROCESS_INFORMATION()
    attributes = None
    files = []
    started = time.monotonic()
    try:
        job = api.checked(k.CreateJobObjectW(None, None), "CreateJobObjectW")
        limits = EXTENDED_LIMIT()
        limits.BasicLimitInformation.LimitFlags = 0x2000
        api.checked(k.SetInformationJobObject(job, 9, C.byref(limits), C.sizeof(limits)),
                    "SetInformationJobObject(KILL_ON_JOB_CLOSE)")
        files = [open(os.devnull, "rb"), open(output_dir / "stdout.bin", "xb"),
                 open(output_dir / "stderr.bin", "xb")]
        handles = (W.HANDLE * 3)(*[msvcrt.get_osfhandle(f.fileno()) for f in files])
        for handle in handles:
            os.set_handle_inheritable(handle, True)
        attribute_size = C.c_size_t()
        k.InitializeProcThreadAttributeList(None, 1, 0, C.byref(attribute_size))
        attributes = C.create_string_buffer(attribute_size.value)
        api.checked(k.InitializeProcThreadAttributeList(attributes, 1, 0, C.byref(attribute_size)),
                    "InitializeProcThreadAttributeList")
        api.checked(k.UpdateProcThreadAttribute(attributes, 0, 0x20002, handles, C.sizeof(handles), None, None),
                    "UpdateProcThreadAttribute(HANDLE_LIST)")
        si = STARTUPINFOEX()
        si.StartupInfo.cb = C.sizeof(si)
        si.StartupInfo.dwFlags = 0x100
        si.StartupInfo.hStdInput, si.StartupInfo.hStdOutput, si.StartupInfo.hStdError = handles
        si.lpAttributeList = C.cast(attributes, W.LPVOID)
        env_block = C.create_unicode_buffer("\0".join(f"{key}={value}" for key, value in
                                                     sorted(environment.items(), key=lambda item: item[0].upper())) + "\0\0")
        api.checked(k.CreateProcessW(str(application), C.create_unicode_buffer(command_line), None, None,
                    True, 0x4 | 0x08000000 | 0x400 | 0x80000, env_block, str(cwd),
                    C.byref(si), C.byref(pi)), "CreateProcessW(suspended)")
        result["root_pid"] = int(pi.dwProcessId)
        api.assign(job, pi.hProcess)
        result["assigned"] = True
        result["job_samples"].append({"phase": "before_resume", **api.accounting(job), "pids": api.pids(job)})
        api.checked(k.ResumeThread(pi.hThread) != 0xFFFFFFFF, "ResumeThread")
        result["resumed"] = True
        wait = k.WaitForSingleObject(pi.hProcess, int(timeout * 1000))
        if wait == WAIT_TIMEOUT:
            result["timed_out"] = True
        elif wait != WAIT_OBJECT_0:
            raise OSError(C.get_last_error(), "WaitForSingleObject(root)")
        else:
            code = W.DWORD()
            api.checked(k.GetExitCodeProcess(pi.hProcess, C.byref(code)), "GetExitCodeProcess")
            result["root_exit_code"] = int(code.value)
    except BaseException as error:
        result["errors"].append(f"{type(error).__name__}: {error}")
    finally:
        # 任意异常都先清理；绑定失败时根线程尚未恢复，根句柄是唯一回滚目标。
        if pi.hProcess:
            try:
                if result["assigned"]:
                    result["job_samples"].append({"phase": "before_cleanup", **api.accounting(job), "pids": api.pids(job)})
                    api.terminate_job(job)
                    deadline = time.monotonic() + 3.0
                    while True:
                        final = api.accounting(job)
                        if final["ActiveProcesses"] == 0:
                            result["job_samples"].append({"phase": "after_cleanup", **final, "pids": api.pids(job)})
                            result["cleanup_confirmed"] = k.WaitForSingleObject(pi.hProcess, 500) == WAIT_OBJECT_0
                            break
                        if time.monotonic() >= deadline:
                            raise RuntimeError("Job cleanup deadline exceeded")
                        time.sleep(0.02)
                else:
                    api.checked(k.TerminateProcess(pi.hProcess, 125), "TerminateProcess(suspended rollback)")
                    result["cleanup_confirmed"] = k.WaitForSingleObject(pi.hProcess, 1000) == WAIT_OBJECT_0
            except BaseException as error:
                result["errors"].append(f"cleanup: {type(error).__name__}: {error}")
                # 即使核验/TerminateJobObject失败，关闭本进程独占的Job句柄仍触发系统杀树。
            if job:
                closed = bool(k.CloseHandle(job))
                result["job_handle_closed"] = closed
                if not closed:
                    result["errors"].append("CloseHandle(job) failed")
                    result["cleanup_confirmed"] = False
                job = None
            result["root_wait_after_job_close"] = int(k.WaitForSingleObject(pi.hProcess, 1000))
            if result["root_wait_after_job_close"] != WAIT_OBJECT_0:
                result["cleanup_confirmed"] = False
                result["errors"].append("root did not terminate after job close")
            code = W.DWORD()
            if k.GetExitCodeProcess(pi.hProcess, C.byref(code)):
                result["root_exit_code_after_cleanup"] = int(code.value)
        elif job:
            k.CloseHandle(job)
        for handle in (pi.hThread, pi.hProcess):
            if handle:
                k.CloseHandle(handle)
        if attributes:
            k.DeleteProcThreadAttributeList(attributes)
        for file in files:
            file.close()
        result["elapsed_seconds"] = round(time.monotonic() - started, 6)
        result["status"] = classify(result, (output_dir / "stdout.bin").read_bytes()
                                    if (output_dir / "stdout.bin").exists() else b"")
        (output_dir / "execution.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def classify(result, stdout):
    if not result["cleanup_confirmed"]:
        return "CLEANUP_UNCONFIRMED"
    if result["errors"]:
        return "LAUNCH_OR_CLEANUP_ERROR"
    if result["timed_out"]:
        return "TIMEOUT"
    if result.get("root_exit_code") != 0:
        return "NONZERO_EXIT"
    if not re.search(rb"(?m)^8\.6\.[0-9]+\r?$", stdout):
        return "PATCHLEVEL_MARKER_MISSING"
    return "PASS"


def offline_environment(cwd):
    # 环境完全新建，不修改父进程；不传入密钥、调试覆盖、用户启动脚本路径或全量环境。
    windows = os.environ.get("SystemRoot", r"C:\Windows")
    return {"SystemRoot": windows, "WINDIR": windows, "SystemDrive": Path(windows).drive,
            "ComSpec": str(Path(windows) / "System32/cmd.exe"),
            "PATH": str(Path(windows) / "System32") + ";" + windows,
            "PATHEXT": ".COM;.EXE;.BAT;.CMD", "PROCESSOR_ARCHITECTURE": "AMD64",
            "TEMP": str(cwd), "TMP": str(cwd), "USERPROFILE": str(cwd),
            "APPDATA": str(cwd), "LOCALAPPDATA": str(cwd), "RDI_VERBOSE": "False"}
