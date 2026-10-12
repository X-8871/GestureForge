"""对冻结S15 DCP执行唯一一次受控direct Vivado batch bitgen。"""
import argparse
import ctypes
import datetime
import hashlib
import json
import msvcrt
import os
import secrets
import stat
import sys
import time
from pathlib import Path

import s15_job_guard as job_guard


REPOSITORY = r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition"
EVIDENCE_ROOT = r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T17"
EVIDENCE_ROOT_ENV = "S15_DIRECT_BITGEN_EVIDENCE_ROOT"
FROZEN_DCP = (
    "C:\\Users\\22061\\.codex\\worktrees\\96a3\\FPGA_Competition\\tmp\\2B\\S2B-T17\\"
    "s15_launch_prepare_20261012_r02\\project_s15_r01\\s2b_inference_candidate.runs\\impl_1\\"
    "s2b_inference_wrapper_postroute_physopt.dcp"
)
EXPECTED_DCP_SHA256 = "DB2AAF706C99121EADA307FEC80B4D69B362F1232FF17FCF65F4DD5C0015AD83"
VIVADO_EXE = r"D:\Xilinx\2026.1\Vivado\bin\unwrapped\win64.o\vivado.exe"
EXPECTED_VIVADO_VERSION = "2026.1"
EXPECTED_PART = "xc7z020clg400-2"
EXPECTED_BIT_NAME = "s2b_inference_wrapper_postroute_physopt.bit"
TCL_SCRIPT_NAME = "s15_frozen_dcp_bitgen.tcl"
DCP_COPY_NAME = "s2b_inference_wrapper_postroute_physopt.dcp"
TCL_COPY_NAME = "s15_frozen_dcp_bitgen.tcl"
TCL_PROGRESS_NAME = "tcl_progress.jsonl"
SAMPLE_INTERVAL_SECONDS = 0.75
TERMINATION_EXIT_CODE = 93
FILE_ATTRIBUTE_REPARSE_POINT = 0x0400
GENERIC_READ = 0x80000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
STARTUP_STD_HANDLE_INHERIT = 0x0001
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
FILE_ATTRIBUTE_NORMAL = 0x00000080
FILE_ATTRIBUTE_DIRECTORY = 0x00000010
FILE_ATTRIBUTE_TAG_INFO_CLASS = 9
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


class ControllerError(RuntimeError):
    """预检、监护或产物闭合不能证明时停止bitgen。"""


class FILE_ATTRIBUTE_TAG_INFO(ctypes.Structure):
    _fields_ = [("FileAttributes", job_guard.wintypes.DWORD), ("ReparseTag", job_guard.wintypes.DWORD)]


class InputReadLock:
    """持有只共享读权限的Win32文件HANDLE，阻止输入副本写入、改名或删除。"""

    def __init__(self, path):
        self.path = os.fspath(path)
        _assert_path_chain(self.path, "file")
        kernel32 = job_guard.kernel32
        kernel32.CreateFileW.argtypes = [
            job_guard.wintypes.LPCWSTR,
            job_guard.wintypes.DWORD,
            job_guard.wintypes.DWORD,
            ctypes.c_void_p,
            job_guard.wintypes.DWORD,
            job_guard.wintypes.DWORD,
            job_guard.wintypes.HANDLE,
        ]
        kernel32.CreateFileW.restype = job_guard.wintypes.HANDLE
        self.handle = kernel32.CreateFileW(
            self.path,
            GENERIC_READ,
            FILE_SHARE_READ,
            None,
            OPEN_EXISTING,
            FILE_FLAG_OPEN_REPARSE_POINT | FILE_ATTRIBUTE_NORMAL,
            None,
        )
        if not self.handle or int(self.handle) == INVALID_HANDLE_VALUE:
            raise job_guard._win_error("CreateFileW(input lock/share-read-only)")
        self.closed = False
        try:
            kernel32.GetFileInformationByHandleEx.argtypes = [
                job_guard.wintypes.HANDLE,
                ctypes.c_int,
                ctypes.c_void_p,
                job_guard.wintypes.DWORD,
            ]
            kernel32.GetFileInformationByHandleEx.restype = job_guard.wintypes.BOOL
            info = FILE_ATTRIBUTE_TAG_INFO()
            if not kernel32.GetFileInformationByHandleEx(
                self.handle,
                FILE_ATTRIBUTE_TAG_INFO_CLASS,
                ctypes.byref(info),
                ctypes.sizeof(info),
            ):
                raise job_guard._win_error("GetFileInformationByHandleEx(FileAttributeTagInfo)")
            if int(info.FileAttributes) & FILE_ATTRIBUTE_REPARSE_POINT:
                raise ControllerError(f"输入锁HANDLE指向重解析点：{self.path!r}")
            if int(info.FileAttributes) & FILE_ATTRIBUTE_DIRECTORY:
                raise ControllerError(f"输入锁HANDLE指向目录：{self.path!r}")
        except BaseException:
            job_guard._checked_close_handle(self.handle, "failed input read lock")
            self.closed = True
            raise

    def close(self):
        if self.closed:
            return
        job_guard._checked_close_handle(self.handle, "input read lock")
        self.closed = True


class ManifestWriter:
    """在唯一Run目录内持续落盘本次运行的审计清单。"""

    def __init__(self, run_dir, manifest):
        self.path = Path(run_dir) / "manifest.json"
        self.stream = self.path.open("x", encoding="utf-8", newline="\n")
        self.manifest = manifest
        self.write()

    def write(self):
        _assert_path_chain(self.path, "file")
        self.stream.seek(0)
        self.stream.truncate()
        json.dump(self.manifest, self.stream, ensure_ascii=False, sort_keys=True, indent=2)
        self.stream.write("\n")
        self.stream.flush()
        os.fsync(self.stream.fileno())

    def close(self):
        self.stream.close()


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest().upper()


def _assert_path_chain(path, expected_type):
    """逐组件拒绝符号链接、目录联接及其他Windows重解析点。"""
    absolute = os.path.abspath(os.fspath(path))
    drive, tail = os.path.splitdrive(absolute)
    if not drive or not os.path.isabs(absolute):
        raise ControllerError(f"路径不是本机绝对盘符路径：{absolute!r}")
    current = drive + os.sep
    components = [item for item in tail.split(os.sep) if item]
    if not components:
        raise ControllerError(f"路径缺少目标组件：{absolute!r}")
    for index, component in enumerate(components):
        current = os.path.join(current, component)
        try:
            info = os.lstat(current)
        except OSError as error:
            raise ControllerError(f"路径组件不存在或不可读：{current!r}: {error!r}") from error
        if stat.S_ISLNK(info.st_mode) or int(getattr(info, "st_file_attributes", 0)) & FILE_ATTRIBUTE_REPARSE_POINT:
            raise ControllerError(f"拒绝符号链接或重解析路径组件：{current!r}")
        is_last = index == len(components) - 1
        if not is_last and not stat.S_ISDIR(info.st_mode):
            raise ControllerError(f"非末端路径组件不是目录：{current!r}")
        if is_last:
            if expected_type == "file" and (not stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
                raise ControllerError(f"目标不是普通文件：{current!r}")
            if expected_type == "directory" and not stat.S_ISDIR(info.st_mode):
                raise ControllerError(f"目标不是目录：{current!r}")
    return absolute


def _ensure_exact_repository():
    actual = os.path.normcase(os.path.abspath(Path(__file__).parent.parent))
    expected = os.path.normcase(REPOSITORY)
    if actual != expected:
        raise ControllerError(f"控制器工作树不等于固定仓库：expected={REPOSITORY!r}, actual={actual!r}")


def _effective_evidence_root():
    """解析默认证据目录或显式注入的隔离证据目录。"""
    override = os.environ.get(EVIDENCE_ROOT_ENV)
    root = EVIDENCE_ROOT if override is None or override == "" else override
    if not os.path.isabs(root):
        raise ControllerError(f"证据根必须是绝对路径：{root!r}")
    return _assert_path_chain(root, "directory")


def _create_unique_run_dir(evidence_root):
    root = _assert_path_chain(evidence_root, "directory")
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for _ in range(64):
        run_id = f"direct_bitgen_{stamp}_{secrets.token_hex(8)}"
        target = os.path.join(root, run_id)
        try:
            os.mkdir(target)
        except FileExistsError:
            continue
        _assert_path_chain(target, "directory")
        return run_id, Path(target)
    raise ControllerError("未能创建唯一direct bitgen RunId目录")


def _preflight_inputs():
    _ensure_exact_repository()
    dcp = _assert_path_chain(FROZEN_DCP, "file")
    exe = _assert_path_chain(VIVADO_EXE, "file")
    source = _assert_path_chain(Path(__file__).with_name(TCL_SCRIPT_NAME), "file")
    evidence = _effective_evidence_root()
    dcp_hash = _sha256(dcp)
    if dcp_hash != EXPECTED_DCP_SHA256:
        raise ControllerError(f"冻结DCP SHA256不符：expected={EXPECTED_DCP_SHA256}, actual={dcp_hash}")
    enterprise_init_candidates = _enterprise_init_candidates()
    for init_path in enterprise_init_candidates:
        scripts_dir = os.path.dirname(init_path)
        if os.path.lexists(scripts_dir):
            _assert_path_chain(scripts_dir, "directory")
        if os.path.lexists(init_path):
            _assert_path_chain(init_path, "file")
            raise ControllerError(f"检测到可能在Vivado启动时自动执行的安装级Tcl初始化脚本：{init_path!r}")
    return {
        "dcp_path": dcp,
        "dcp_sha256": dcp_hash,
        "vivado_executable_path": exe,
        "vivado_executable_sha256": _sha256(exe),
        "vivado_expected_version": EXPECTED_VIVADO_VERSION,
        "tcl_source_path": source,
        "tcl_source_sha256": _sha256(source),
        "controller_source_path": _assert_path_chain(__file__, "file"),
        "controller_source_sha256": _sha256(__file__),
        "evidence_root": evidence,
        "enterprise_init_candidates_absent": enterprise_init_candidates,
    }


def _enterprise_init_candidates():
    """列出Vivado安装根及版本目录中可能被自动source的初始化脚本。"""
    product_root = Path(VIVADO_EXE).parents[3]
    roots = (product_root / EXPECTED_VIVADO_VERSION / "scripts", product_root / "scripts")
    names = ("Vivado_init.tcl", "init.tcl")
    return [str(root / name) for root in roots for name in names]


def _child_environment(run_dir):
    """保留Vivado运行所需环境，同时将用户级Tcl初始化搜索根隔离到本Run。"""
    appdata = Path(run_dir) / "isolated_appdata"
    appdata.mkdir()
    _assert_path_chain(appdata, "directory")
    environment = dict(os.environ)
    environment["APPDATA"] = str(appdata)
    return environment, str(appdata)


def _copy_verified_input(source_path, destination_path, expected_sha256, label):
    """排他创建输入副本并要求副本及复制后源文件均匹配批准哈希。"""
    source_path = _assert_path_chain(source_path, "file")
    destination_path = os.fspath(destination_path)
    parent = _assert_path_chain(os.path.dirname(destination_path), "directory")
    if os.path.lexists(destination_path):
        raise ControllerError(f"拒绝覆盖已有输入副本：{destination_path!r}")
    if _sha256(source_path) != expected_sha256:
        raise ControllerError(f"复制{label}前源SHA256变化：{source_path!r}")
    digest = hashlib.sha256()
    with open(source_path, "rb") as source, open(destination_path, "xb") as destination:
        while True:
            block = source.read(1024 * 1024)
            if not block:
                break
            destination.write(block)
            digest.update(block)
        destination.flush()
        os.fsync(destination.fileno())
    copied_sha = digest.hexdigest().upper()
    _assert_path_chain(destination_path, "file")
    source_sha_after = _sha256(source_path)
    if copied_sha != expected_sha256 or source_sha_after != expected_sha256:
        raise ControllerError(
            f"复制{label}哈希不闭合：expected={expected_sha256}, copy={copied_sha}, source_after={source_sha_after}"
        )
    return {
        "source_path": source_path,
        "source_sha256_before_copy": expected_sha256,
        "destination_path": destination_path,
        "destination_sha256": copied_sha,
        "source_sha256_after_copy": source_sha_after,
        "parent_path": parent,
    }


def _prepare_run_inputs(run_dir, input_facts):
    """将获批DCP与Tcl复制到隔离Run，并持有不允许写删的Win32共享读锁。"""
    inputs_dir = Path(run_dir) / "inputs"
    inputs_dir.mkdir()
    _assert_path_chain(inputs_dir, "directory")
    input_facts["dcp_copy_path"] = str(inputs_dir / DCP_COPY_NAME)
    input_facts["tcl_copy_path"] = str(inputs_dir / TCL_COPY_NAME)
    input_facts["run_inputs_directory"] = str(inputs_dir)
    copied = []
    locks = []
    try:
        copied.append(_copy_verified_input(input_facts["dcp_path"], input_facts["dcp_copy_path"], input_facts["dcp_sha256"], "冻结DCP"))
        copied.append(_copy_verified_input(input_facts["tcl_source_path"], input_facts["tcl_copy_path"], input_facts["tcl_source_sha256"], "Tcl源脚本"))
        for path in (input_facts["dcp_copy_path"], input_facts["tcl_copy_path"]):
            locks.append(InputReadLock(path))
        locked_hashes = {
            "dcp_copy_sha256": _sha256(input_facts["dcp_copy_path"]),
            "tcl_copy_sha256": _sha256(input_facts["tcl_copy_path"]),
        }
        if locked_hashes["dcp_copy_sha256"] != input_facts["dcp_sha256"]:
            raise ControllerError("只读锁定后的DCP副本SHA256不符")
        if locked_hashes["tcl_copy_sha256"] != input_facts["tcl_source_sha256"]:
            raise ControllerError("只读锁定后的Tcl副本SHA256不符")
        input_facts["run_input_copies"] = copied
        input_facts["locked_copy_hashes"] = locked_hashes
        return locks
    except BaseException as primary:
        cleanup_errors = []
        for lock in reversed(locks):
            try:
                lock.close()
            except BaseException as error:
                cleanup_errors.append(repr(error))
        if cleanup_errors:
            raise ControllerError(f"输入副本准备失败且只读锁清理不闭合：primary={primary!r}; cleanup={cleanup_errors!r}") from primary
        raise


def _open_stdio_handles(run_dir):
    """排他创建本次stdout/stderr并仅允许三个标准句柄被子进程继承。"""
    stdout_path = Path(run_dir) / "stdout.log"
    stderr_path = Path(run_dir) / "stderr.log"
    stdout_stream = stdout_path.open("xb", buffering=0)
    try:
        stderr_stream = stderr_path.open("xb", buffering=0)
    except BaseException:
        stdout_stream.close()
        raise
    nul_attributes = job_guard.SECURITY_ATTRIBUTES(ctypes.sizeof(job_guard.SECURITY_ATTRIBUTES), None, True)
    kernel32 = job_guard.kernel32
    kernel32.CreateFileW.argtypes = [
        job_guard.wintypes.LPCWSTR,
        job_guard.wintypes.DWORD,
        job_guard.wintypes.DWORD,
        ctypes.POINTER(job_guard.SECURITY_ATTRIBUTES),
        job_guard.wintypes.DWORD,
        job_guard.wintypes.DWORD,
        job_guard.wintypes.HANDLE,
    ]
    kernel32.CreateFileW.restype = job_guard.wintypes.HANDLE
    nul_handle = kernel32.CreateFileW(
        "NUL",
        GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        ctypes.byref(nul_attributes),
        OPEN_EXISTING,
        0,
        None,
    )
    if not nul_handle:
        stdout_stream.close()
        stderr_stream.close()
        raise job_guard._win_error("CreateFileW(NUL/stdin)")
    stdout_handle = msvcrt.get_osfhandle(stdout_stream.fileno())
    stderr_handle = msvcrt.get_osfhandle(stderr_stream.fileno())
    try:
        os.set_handle_inheritable(stdout_handle, True)
        os.set_handle_inheritable(stderr_handle, True)
        if not os.get_handle_inheritable(int(nul_handle)):
            raise ControllerError("NUL标准输入HANDLE未设置继承属性")
    except BaseException:
        job_guard._checked_close_handle(nul_handle, "fixture/controller NUL stdin")
        stdout_stream.close()
        stderr_stream.close()
        raise
    return (int(nul_handle), stdout_handle, stderr_handle), (stdout_stream, stderr_stream)


def _close_stdio(handles, streams):
    errors = []
    nul_handle = handles[0] if handles else None
    if nul_handle:
        try:
            job_guard._checked_close_handle(nul_handle, "controller NUL stdin")
        except BaseException as error:
            errors.append(repr(error))
    for stream in streams or ():
        try:
            stream.close()
        except BaseException as error:
            errors.append(repr(error))
    if errors:
        raise ControllerError("标准句柄关闭失败：" + "; ".join(errors))


def _expected_argv(run_dir, inputs):
    run_dir = str(run_dir)
    log_path = os.path.join(run_dir, "vivado.log")
    journal_path = os.path.join(run_dir, "vivado.jou")
    bit_path = os.path.join(run_dir, EXPECTED_BIT_NAME)
    progress_path = os.path.join(run_dir, TCL_PROGRESS_NAME)
    argv = [
        inputs["vivado_executable_path"],
        "-mode",
        "batch",
        "-log",
        log_path,
        "-journal",
        journal_path,
        "-source",
        inputs["tcl_copy_path"],
        "-tclargs",
        inputs["dcp_copy_path"],
        bit_path,
        progress_path,
        inputs["evidence_root"],
    ]
    return argv, {
        "vivado_log": log_path,
        "vivado_journal": journal_path,
        "stdout": os.path.join(run_dir, "stdout.log"),
        "stderr": os.path.join(run_dir, "stderr.log"),
        "tcl_progress": progress_path,
        "bitstream": bit_path,
        "monitor": os.path.join(run_dir, "monitor.jsonl"),
    }


def _file_tail(path, previous_size):
    if not os.path.exists(path):
        return {"exists": False, "size_bytes": 0, "appended_bytes": 0, "tail_sha256": None}
    _assert_path_chain(path, "file")
    size = os.path.getsize(path)
    if size < previous_size:
        raise ControllerError(f"日志在监护期间被截短：path={path!r}, old={previous_size}, new={size}")
    appended = size - previous_size
    digest = None
    if appended:
        with open(path, "rb") as stream:
            stream.seek(max(previous_size, size - 1024 * 1024))
            digest = hashlib.sha256(stream.read()).hexdigest().upper()
    return {"exists": True, "size_bytes": size, "appended_bytes": appended, "tail_sha256": digest}


def _read_progress(path):
    rows = []
    if not os.path.exists(path):
        return rows
    _assert_path_chain(path, "file")
    with open(path, "r", encoding="utf-8") as stream:
        for index, line in enumerate(stream, 1):
            try:
                row = json.loads(line)
            except ValueError as error:
                raise ControllerError(f"Tcl progress第{index}行不是JSON：{error!r}") from error
            if type(row) is not dict or type(row.get("event")) is not str:
                raise ControllerError(f"Tcl progress第{index}行结构不符")
            rows.append(row)
    return rows


def _artifact_record(path):
    if not os.path.exists(path):
        return {"path": os.fspath(path), "exists": False, "size_bytes": None, "sha256": None}
    _assert_path_chain(path, "file")
    return {
        "path": os.fspath(path),
        "exists": True,
        "size_bytes": os.path.getsize(path),
        "sha256": _sha256(path),
    }


def _read_monitor(path):
    """读取并校验控制器JSONL监护记录。"""
    rows = []
    if not os.path.exists(path):
        return rows
    _assert_path_chain(path, "file")
    with open(path, "r", encoding="utf-8") as stream:
        for index, line in enumerate(stream, 1):
            try:
                row = json.loads(line)
            except ValueError as error:
                raise ControllerError(f"monitor第{index}行不是JSON：{error!r}") from error
            if type(row) is not dict:
                raise ControllerError(f"monitor第{index}行不是对象")
            rows.append(row)
    return rows


def _validate_success_artifacts(artifacts, progress_rows, monitor_rows):
    """验证完整运行必须保留的日志、监护记录、Tcl回执和bitstream。"""
    required = ("vivado_log", "vivado_journal", "stdout", "stderr", "monitor", "tcl_progress", "bitstream")
    nonempty = {"vivado_log", "vivado_journal", "monitor", "tcl_progress", "bitstream"}
    issues = []
    for name in required:
        record = artifacts.get(name)
        if not isinstance(record, dict) or record.get("exists") is not True:
            issues.append(f"missing:{name}")
            continue
        size = record.get("size_bytes")
        digest = record.get("sha256")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            issues.append(f"invalid_size:{name}")
        if not isinstance(digest, str) or len(digest) != 64 or any(char not in "0123456789ABCDEF" for char in digest):
            issues.append(f"invalid_sha256:{name}")
        if name in nonempty and isinstance(size, int) and size <= 0:
            issues.append(f"empty:{name}")
    if not progress_rows:
        issues.append("empty_or_invalid:tcl_progress")
    if not monitor_rows:
        issues.append("empty_or_invalid:monitor")
    return {"valid": not issues, "issues": issues, "required_artifacts": list(required)}


def _append_monitor(path, row):
    with open(path, "a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def _has_real_log_progress(appended):
    """只有Vivado正式log或journal追加字节才重置无进展计时。"""
    return any(appended.get(name, {}).get("appended_bytes", 0) > 0 for name in ("vivado_log", "vivado_journal"))


def _sha256_if_present(path):
    if not os.path.lexists(path):
        return None
    _assert_path_chain(path, "file")
    return _sha256(path)


def _kill_and_close(child, reason):
    """对硬停原因终止自有Job并等待根句柄及所有已捕获成员。"""
    result = {"reason": reason, "job_termination": None, "fallback_termination": None, "closure": None, "errors": []}
    try:
        child.job.terminate_own_job(TERMINATION_EXIT_CODE)
        result["job_termination"] = "OK"
    except BaseException as error:
        result["job_termination"] = repr(error)
        result["errors"].append(f"TerminateJobObject: {error!r}")
    try:
        root_wait = job_guard._api_wait(child.process_handle, 30000)
        if root_wait == job_guard.WAIT_TIMEOUT:
            if job_guard._api_terminate_process(child.process_handle, TERMINATION_EXIT_CODE):
                result["fallback_termination"] = "TerminateProcess_OK"
            else:
                result["fallback_termination"] = f"TerminateProcess_FALSE_WinError_{ctypes.get_last_error()}"
            root_wait = job_guard._api_wait(child.process_handle, 30000)
        if root_wait != job_guard.WAIT_OBJECT_0:
            raise ControllerError(f"硬停后root句柄等待未闭合：wait={root_wait}")
        result["root_native_exit_code"] = job_guard._api_get_exit_code(child.process_handle)
    except BaseException as error:
        result["errors"].append(f"root closure: {error!r}")
    try:
        result["closure"] = child.wait_and_close(timeout_seconds=30.0)
    except BaseException as error:
        result["errors"].append(f"all-member closure: {error!r}")
        fallback = {"job_closed": False, "root_wait": None, "root_exit_code": None, "handle_close_errors": []}
        try:
            if not child.job.closed:
                child.job.close()
            fallback["job_closed"] = child.job.closed
        except BaseException as close_error:
            fallback["handle_close_errors"].append(f"Job close: {close_error!r}")
        if child.process_info.hProcess:
            try:
                wait = job_guard._api_wait(child.process_handle, 30000)
                fallback["root_wait"] = wait
                if wait == job_guard.WAIT_OBJECT_0:
                    fallback["root_exit_code"] = job_guard._api_get_exit_code(child.process_handle)
            except BaseException as wait_error:
                fallback["handle_close_errors"].append(f"root wait/read: {wait_error!r}")
        for label, attr in (("root thread", "hThread"), ("root process", "hProcess")):
            handle = getattr(child.process_info, attr)
            if handle:
                try:
                    job_guard._checked_close_handle(handle, label)
                    setattr(child.process_info, attr, None)
                except BaseException as close_error:
                    fallback["handle_close_errors"].append(f"{label} close: {close_error!r}")
        fallback["handles_closed"] = not fallback["handle_close_errors"] and not child.process_info.hThread and not child.process_info.hProcess
        result["failed_closure_fallback"] = fallback
    return result


def _finalize_manifest(writer, run_dir, input_facts, outputs, peaks, result_code, stop_reason, closure, timelines):
    manifest = writer.manifest
    manifest["finish_utc"] = _utc_now()
    manifest["finish_monotonic_seconds"] = time.monotonic()
    manifest["native_root_exit_code"] = result_code
    manifest["stop_reason"] = stop_reason
    manifest["job_final_closure"] = closure
    manifest["resource_peaks_and_floors"] = peaks
    manifest["vivado_tcl_progress"] = _read_progress(outputs["tcl_progress"])
    monitor_rows = _read_monitor(outputs["monitor"])
    manifest["monitor_record_count"] = len(monitor_rows)
    progress = manifest["vivado_tcl_progress"]
    version_events = [row for row in progress if row.get("event") == "vivado_version"]
    part_events = [row for row in progress if row.get("event") == "checkpoint_opened"]
    bit_events = [row for row in progress if row.get("event") == "write_bitstream_complete"]
    manifest["input_paths_and_hashes"]["vivado_actual_version"] = (
        version_events[-1].get("detail") if version_events else None
    )
    expected_success = (
        result_code == 0
        and not stop_reason
        and closure is not None
        and closure.get("final", {}).get("root_native_handle_exit_code") == 0
        and len(version_events) == 1
        and version_events[0].get("detail") == EXPECTED_VIVADO_VERSION
        and len(part_events) == 1
        and part_events[0].get("detail") == EXPECTED_PART
        and len(bit_events) == 1
        and str(bit_events[0].get("detail", "")).isdigit()
        and int(bit_events[0]["detail"]) > 0
    )
    manifest["status"] = "BITGEN_COMPLETE_SOFTWARE_ONLY" if expected_success else "FAILED_OR_INCOMPLETE"
    manifest["artifacts"] = {
        key: _artifact_record(outputs[key])
        for key in ("vivado_log", "vivado_journal", "stdout", "stderr", "tcl_progress", "bitstream", "monitor")
    }
    manifest["input_hashes_after_run"] = {
        "frozen_dcp_original_sha256": _sha256_if_present(input_facts["dcp_path"]),
        "frozen_dcp_copy_sha256": _sha256_if_present(input_facts["dcp_copy_path"]),
        "tcl_source_original_sha256": _sha256_if_present(input_facts["tcl_source_path"]),
        "tcl_source_copy_sha256": _sha256_if_present(input_facts["tcl_copy_path"]),
        "vivado_executable_sha256": _sha256_if_present(input_facts["vivado_executable_path"]),
        "controller_source_sha256": _sha256_if_present(input_facts["controller_source_path"]),
    }
    manifest["input_hashes_match_preflight"] = (
        manifest["input_hashes_after_run"]["frozen_dcp_original_sha256"] == input_facts["dcp_sha256"]
        and manifest["input_hashes_after_run"]["frozen_dcp_copy_sha256"] == input_facts["dcp_sha256"]
        and manifest["input_hashes_after_run"]["tcl_source_original_sha256"] == input_facts["tcl_source_sha256"]
        and manifest["input_hashes_after_run"]["tcl_source_copy_sha256"] == input_facts["tcl_source_sha256"]
        and manifest["input_hashes_after_run"]["vivado_executable_sha256"] == input_facts["vivado_executable_sha256"]
        and manifest["input_hashes_after_run"]["controller_source_sha256"] == input_facts["controller_source_sha256"]
    )
    bit_record = manifest["artifacts"]["bitstream"]
    bit_length_matches = bool(
        bit_record["exists"]
        and bit_record["size_bytes"] > 0
        and bit_events
        and str(bit_record["size_bytes"]) == str(bit_events[-1].get("detail"))
    )
    manifest["bitstream_size_matches_tcl_receipt"] = bit_length_matches
    manifest["artifact_validation"] = _validate_success_artifacts(
        manifest["artifacts"],
        progress,
        monitor_rows,
    )
    if not manifest["artifact_validation"]["valid"] and manifest["status"] == "BITGEN_COMPLETE_SOFTWARE_ONLY":
        manifest["status"] = "FAILED_OR_INCOMPLETE"
        manifest["stop_reason"] = "成功所需日志、监护、Tcl回执或bitstream缺失或无效"
    if not manifest["input_hashes_match_preflight"]:
        manifest["status"] = "FAILED_INPUT_CHANGED"
        manifest["stop_reason"] = "原始或Run输入副本、Vivado可执行文件、Tcl脚本或控制器运行后SHA256变化"
    elif manifest["status"] == "BITGEN_COMPLETE_SOFTWARE_ONLY" and not bit_length_matches:
        manifest["status"] = "FAILED_OR_INCOMPLETE"
        manifest["stop_reason"] = "bitstream大小与Tcl完成回执不一致"
    writer.write()
    return manifest


def _finish_controller_cleanup(writer, manifest, input_locks, run_exit_code):
    """释放输入只读锁并持久化最终清单，任何收尾失败都返回非零。"""
    lock_close_errors = []
    for input_lock in reversed(input_locks):
        try:
            input_lock.close()
        except BaseException as lock_error:
            lock_close_errors.append(repr(lock_error))
    manifest["input_copy_locks_released_utc"] = _utc_now() if not lock_close_errors else None
    manifest["input_copy_lock_release_errors"] = lock_close_errors
    if lock_close_errors:
        manifest["status"] = "FAILED_OR_INCOMPLETE"
        prior_reason = manifest.get("stop_reason") or ""
        manifest["stop_reason"] = ";".join(
            part for part in (prior_reason, "INPUT_COPY_LOCK_RELEASE_FAILED") if part
        )
        run_exit_code = 1
    try:
        writer.write()
    except BaseException as manifest_error:
        manifest.setdefault("finalization_errors", []).append(
            f"final manifest write after input unlock: {manifest_error!r}"
        )
        manifest["status"] = "FAILED_OR_INCOMPLETE"
        prior_reason = manifest.get("stop_reason") or ""
        manifest["stop_reason"] = ";".join(
            part for part in (prior_reason, "FINAL_MANIFEST_WRITE_FAILED") if part
        )
        run_exit_code = 1
        try:
            writer.write()
        except BaseException as retry_error:
            manifest.setdefault("finalization_errors", []).append(
                f"final manifest write retry after failure: {retry_error!r}"
            )
    try:
        writer.close()
    except BaseException as close_error:
        manifest.setdefault("finalization_errors", []).append(
            f"final manifest close after input unlock: {close_error!r}"
        )
        run_exit_code = 1
    return run_exit_code


def run_frozen_bitgen():
    if os.name != "nt":
        raise ControllerError("direct frozen DCP bitgen只支持Windows")
    facts = _preflight_inputs()
    run_id, run_dir = _create_unique_run_dir(facts["evidence_root"])
    run_created_utc = _utc_now()
    run_created_monotonic = time.monotonic()
    facts["run_inputs_directory"] = str(run_dir / "inputs")
    facts["dcp_copy_path"] = str(run_dir / "inputs" / DCP_COPY_NAME)
    facts["tcl_copy_path"] = str(run_dir / "inputs" / TCL_COPY_NAME)
    argv, output_paths = _expected_argv(run_dir, facts)
    manifest = {
        "schema": "s15-direct-frozen-dcp-bitgen/1.0.0",
        "status": "PREPARED_NOT_STARTED",
        "run_id": run_id,
        "run_directory": str(run_dir),
        "run_directory_created_utc": run_created_utc,
        "run_directory_created_monotonic_seconds": run_created_monotonic,
        "input_paths_and_hashes": {
            "frozen_dcp_path": facts["dcp_path"],
            "frozen_dcp_sha256": facts["dcp_sha256"],
            "frozen_dcp_run_copy_path": facts["dcp_copy_path"],
            "frozen_dcp_run_copy_sha256": None,
            "vivado_executable_path": facts["vivado_executable_path"],
            "vivado_executable_sha256": facts["vivado_executable_sha256"],
            "vivado_expected_version": facts["vivado_expected_version"],
            "vivado_actual_version": None,
            "tcl_source_path": facts["tcl_source_path"],
            "tcl_source_sha256": facts["tcl_source_sha256"],
            "tcl_run_copy_path": facts["tcl_copy_path"],
            "tcl_run_copy_sha256": None,
            "controller_source_path": facts["controller_source_path"],
            "controller_source_sha256": facts["controller_source_sha256"],
            "evidence_root": facts["evidence_root"],
            "evidence_root_override_environment": EVIDENCE_ROOT_ENV,
            "enterprise_init_candidates_absent": facts["enterprise_init_candidates_absent"],
        },
        "input_run_copies": [],
        "input_copy_locks_released_utc": None,
        "input_copy_lock_release_errors": [],
        "expected_part": EXPECTED_PART,
        "process_launch": {
            "api": "Win32 CreateProcessW(CREATE_SUSPENDED), then AssignProcessToJobObject, identity/member closure, ResumeThread",
            "argv": argv,
            "windows_command_line": job_guard.subprocess.list2cmdline(argv),
            "working_directory": str(run_dir),
            "root_identity": None,
            "pre_resume_receipt": None,
            "lifecycle_events": [],
        },
        "limits": {
            "job_object_limit_flags": job_guard.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE,
            "breakaway_allowed": False,
            "tree_rss_limit_bytes": job_guard.RSS_LIMIT_BYTES,
            "available_ram_floor_bytes": job_guard.RAM_FLOOR_BYTES,
            "c_disk_free_floor_bytes": job_guard.DISK_FLOOR_BYTES,
            "no_log_or_stage_progress_hard_stop_seconds": job_guard.NO_PROGRESS_LIMIT_SECONDS,
            "progress_rule": "only positive appended bytes to vivado.log or vivado.jou reset the timer",
            "sampling_target_seconds": SAMPLE_INTERVAL_SECONDS,
        },
        "start_utc": None,
        "start_monotonic_seconds": None,
        "finish_utc": None,
        "finish_monotonic_seconds": None,
        "resource_samples": [],
        "resource_peaks_and_floors": None,
        "native_root_exit_code": None,
        "stop_reason": None,
        "job_final_closure": None,
        "artifacts": {},
    }
    writer = ManifestWriter(run_dir, manifest)
    child = None
    job = None
    std_handles = None
    std_streams = ()
    child_environment = None
    input_locks = []
    closure = None
    stop_reason = None
    native_root_exit_code = None
    cleanup_record = None
    run_exit_code = 1
    peaks = {
        "tree_rss_peak_bytes": 0,
        "available_ram_min_bytes": None,
        "c_disk_free_min_bytes": None,
        "sample_count": 0,
    }
    try:
        # 运行前重新核验原始冻结DCP，并先制作、锁定本Run实际使用的输入副本。
        _assert_path_chain(facts["dcp_path"], "file")
        if _sha256(facts["dcp_path"]) != facts["dcp_sha256"]:
            raise ControllerError("启动前冻结DCP SHA256发生变化")
        for output_path in output_paths.values():
            if os.path.lexists(output_path):
                raise ControllerError(f"拒绝覆盖已有目标产物：{output_path!r}")
        input_locks = _prepare_run_inputs(run_dir, facts)
        manifest["input_paths_and_hashes"]["frozen_dcp_run_copy_sha256"] = facts["locked_copy_hashes"]["dcp_copy_sha256"]
        manifest["input_paths_and_hashes"]["tcl_run_copy_sha256"] = facts["locked_copy_hashes"]["tcl_copy_sha256"]
        manifest["input_run_copies"] = facts["run_input_copies"]
        writer.write()
        std_handles, std_streams = _open_stdio_handles(run_dir)
        child_environment, isolated_appdata = _child_environment(run_dir)
        manifest["process_launch"]["isolated_appdata"] = isolated_appdata
        manifest["input_paths_and_hashes"]["enterprise_init_candidates_absent"] = facts["enterprise_init_candidates_absent"]
        job = job_guard.JobObject(kill_on_close=True)
        if job.flags != job_guard.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE:
            raise ControllerError(f"新JobObject限制标志不符：0x{job.flags:08x}")
        manifest["start_utc"] = _utc_now()
        manifest["start_monotonic_seconds"] = time.monotonic()
        manifest["status"] = "CREATE_SUSPENDED"
        writer.write()
        child = job_guard.launch_suspended_root(
            job,
            facts["vivado_executable_path"],
            argv,
            cwd=str(run_dir),
            std_handles=std_handles,
            environment=child_environment,
        )
        _close_stdio(std_handles, std_streams)
        std_handles, std_streams = None, ()
        manifest["status"] = "RUNNING"
        manifest["process_launch"]["root_identity"] = child.identity
        manifest["process_launch"]["lifecycle_events"] = child.events
        manifest["process_launch"]["pre_resume_receipt"] = next(
            row for row in child.events if row.get("event") == "PRE_RESUME_CLOSED"
        )
        writer.write()

        monitor_path = output_paths["monitor"]
        with open(monitor_path, "x", encoding="utf-8", newline="\n"):
            pass
        tracked_logs = {
            name: output_paths[name]
            for name in ("vivado_log", "vivado_journal", "stdout", "stderr", "tcl_progress")
        }
        previous_sizes = {name: 0 for name in tracked_logs}
        last_progress_monotonic = time.monotonic()
        previous_sample_start = None
        previous_accounting = None
        previous_pids = None
        previous_keys = set()
        next_sample = time.monotonic()
        while True:
            delay = next_sample - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            sample = job.sample(
                previous_sample_start=previous_sample_start,
                previous_accounting=previous_accounting,
                previous_pids=previous_pids,
                previous_keys=previous_keys,
            )
            previous_sample_start = sample["sample_start_monotonic"]
            previous_accounting = sample["accounting_after"]
            previous_pids = set(sample["job_pids_after"])
            previous_keys = {
                (row["pid"], row["birth_ticks"])
                for row in sample["member_measurements"]
            }
            appended = {}
            for name, path in tracked_logs.items():
                state = _file_tail(path, previous_sizes[name])
                appended[name] = state
                previous_sizes[name] = state["size_bytes"]
            grew = _has_real_log_progress(appended)
            if grew:
                last_progress_monotonic = time.monotonic()
            no_progress_seconds = time.monotonic() - last_progress_monotonic
            alerts = job.evaluate(sample, no_progress_seconds)
            sample_record = {
                "utc": _utc_now(),
                "monotonic_seconds": time.monotonic(),
                "job_sample": sample,
                "log_tail_growth": appended,
                "progress_reset": grew,
                "no_progress_seconds": no_progress_seconds,
                "alerts": alerts,
            }
            _append_monitor(monitor_path, sample_record)
            manifest["resource_samples"].append(sample_record)
            peaks["sample_count"] += 1
            if sample["tree_rss_bytes"] is not None:
                peaks["tree_rss_peak_bytes"] = max(peaks["tree_rss_peak_bytes"], sample["tree_rss_bytes"])
            available = sample["available_ram_bytes"]
            disk_free = sample["c_disk_free_bytes"]
            if available is not None:
                peaks["available_ram_min_bytes"] = available if peaks["available_ram_min_bytes"] is None else min(peaks["available_ram_min_bytes"], available)
            if disk_free is not None:
                peaks["c_disk_free_min_bytes"] = disk_free if peaks["c_disk_free_min_bytes"] is None else min(peaks["c_disk_free_min_bytes"], disk_free)

            if alerts:
                stop_reason = "HARD_STOP:" + ",".join(alerts)
                break
            root_wait = job_guard._api_wait(child.process_handle, 0)
            if root_wait not in (job_guard.WAIT_OBJECT_0, job_guard.WAIT_TIMEOUT):
                stop_reason = f"HARD_STOP:ROOT_WAIT_UNKNOWN_{root_wait}"
                break
            if root_wait == job_guard.WAIT_OBJECT_0:
                code = job_guard._api_get_exit_code(child.process_handle)
                if code == job_guard.STILL_ACTIVE:
                    stop_reason = "HARD_STOP:ROOT_SIGNALED_STILL_ACTIVE"
                    break
                native_root_exit_code = code
            current_pids = job.pid_list()
            current_accounting = job.accounting()
            if root_wait == job_guard.WAIT_OBJECT_0 and not current_pids and current_accounting["active_processes"] == 0:
                closure = child.wait_and_close(timeout_seconds=30.0)
                child = None
                break
            next_sample = time.monotonic() + SAMPLE_INTERVAL_SECONDS

        manifest["resource_peaks_and_floors"] = peaks
        manifest["stop_reason"] = stop_reason
        if stop_reason:
            _append_monitor(monitor_path, {"utc": _utc_now(), "monotonic_seconds": time.monotonic(), "event": "HARD_STOP", "reason": stop_reason})
            cleanup_record = _kill_and_close(child, stop_reason) if child is not None else None
            child = None
            if cleanup_record is not None:
                closure = cleanup_record.get("closure")
                native_root_exit_code = cleanup_record.get("root_native_exit_code")
            manifest["hard_stop_cleanup"] = cleanup_record
        if closure is not None and native_root_exit_code is None:
            native_root_exit_code = closure["final"].get("root_native_handle_exit_code")
        final = _finalize_manifest(
            writer,
            run_dir,
            facts,
            output_paths,
            peaks,
            native_root_exit_code,
            stop_reason,
            closure,
            None,
        )
        run_exit_code = 0 if final["status"] == "BITGEN_COMPLETE_SOFTWARE_ONLY" else 1
    except BaseException as error:
        stop_reason = stop_reason or f"CONTROLLER_EXCEPTION:{type(error).__name__}:{error}"
        manifest["stop_reason"] = stop_reason
        manifest["controller_exception"] = repr(error)
        manifest["resource_peaks_and_floors"] = peaks
        if child is not None:
            cleanup_record = _kill_and_close(child, stop_reason)
            manifest["hard_stop_cleanup"] = cleanup_record
            closure = cleanup_record.get("closure")
            native_root_exit_code = cleanup_record.get("root_native_exit_code")
            child = None
        if job is not None and not job.closed:
            try:
                job.close()
            except BaseException as close_error:
                manifest.setdefault("cleanup_errors", []).append(repr(close_error))
        if std_handles is not None:
            try:
                _close_stdio(std_handles, std_streams)
            except BaseException as close_error:
                manifest.setdefault("cleanup_errors", []).append(repr(close_error))
        try:
            _finalize_manifest(
                writer,
                run_dir,
                facts,
                output_paths,
                peaks,
                native_root_exit_code,
                stop_reason,
                closure,
                None,
            )
        except BaseException as finalize_error:
            manifest.setdefault("finalization_errors", []).append(repr(finalize_error))
            try:
                writer.write()
            except BaseException:
                pass
        run_exit_code = 1
    finally:
        run_exit_code = _finish_controller_cleanup(writer, manifest, input_locks, run_exit_code)
    return run_exit_code


def main(argv=None):
    parser = argparse.ArgumentParser(description="受控生成冻结S15 DCP bitstream")
    parser.add_argument(
        "--execute-frozen-bitgen",
        action="store_true",
        help="明确允许本控制器启动本次冻结DCP bitgen",
    )
    arguments = parser.parse_args(argv)
    if not arguments.execute_frozen_bitgen:
        parser.error("只有显式传入 --execute-frozen-bitgen 才会启动Vivado")
    try:
        return run_frozen_bitgen()
    except BaseException as error:
        print(f"DIRECT_BITGEN_BLOCKED {type(error).__name__}: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
