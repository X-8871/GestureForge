"""对冻结S15 DCP执行唯一一次受控direct Vivado batch bitgen。"""
import argparse
import ctypes
import datetime
import hashlib
import json
import msvcrt
import os
import re
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
CMD_EXE = r"C:\Windows\System32\cmd.exe"
VIVADO_BIN = r"D:\Xilinx\2026.1\Vivado\bin"
VIVADO_BAT = r"D:\Xilinx\2026.1\Vivado\bin\vivado.bat"
VIVADO_EXE = r"D:\Xilinx\2026.1\Vivado\bin\unwrapped\win64.o\vivado.exe"
XVCREDIST_EXE = r"D:\Xilinx\2026.1\Vivado\tps\win64\xvcredist.exe"
XVCREDIST_LINK_DIRECTORY = r"D:\Xilinx\2026.1\Vivado\tps"
XVCREDIST_LINK_TARGET = r"..\tps"
XVCREDIST_RESOLVED_ROOT = r"D:\Xilinx\2026.1\tps"
EXPECTED_XVCREDIST_SHA256 = "9AF2EDB12A74BE5F1F2B9FD7D0BA888EE36CF87A8F9F4CD131EC59B66BD12019"
REDIST_CHECK_SKIP_ENV = "XIL_PA_NO_REDIST_CHECK"
TCLSTORE_DATA_LINK = r"D:\Xilinx\2026.1\Vivado\data"
TCLSTORE_DATA_LINK_TARGET = r"..\data"
TCLSTORE_CANONICAL_DATA_ROOT = r"D:\Xilinx\2026.1\data"
TCLSTORE_CANONICAL_ROOT = r"D:\Xilinx\2026.1\data\XilinxTclStore"
TCLSTORE_INSTALL_ROOT = r"D:\Xilinx\2026.1"
APPDATA_MAX_PATH_UTF16_CHARS = 259
VIVADO_SETUP_ENVIRONMENT_VARIABLES = (
    "RDI_SETUP_ENV_FUNCTION",
    "RDI_BINROOT",
    "RDI_APPROOT",
    "RDI_BASEROOT",
    "RDI_INSTALLROOT",
    "_RDI_SETENV_RUN",
    "RDI_BASELINE",
    "XILINX_PATH",
    "MYVIVADO",
)
VIVADO_BATCH_SUPPORT = {
    "setupEnv.bat": r"D:\Xilinx\2026.1\Vivado\bin\setupEnv.bat",
    "loader.bat": r"D:\Xilinx\2026.1\Vivado\bin\loader.bat",
    "rdiArgs.bat": r"D:\Xilinx\2026.1\Vivado\bin\rdiArgs.bat",
}
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
TOKEN_QUERY = 0x0008
TOKEN_USER_CLASS = 1
ERROR_INSUFFICIENT_BUFFER = 122
SE_FILE_OBJECT = 1
OWNER_SECURITY_INFORMATION = 0x00000001
DACL_SECURITY_INFORMATION = 0x00000004
PROTECTED_DACL_SECURITY_INFORMATION = 0x80000000
SE_DACL_PROTECTED = 0x1000
ACCESS_ALLOWED_ACE_TYPE = 0
OBJECT_INHERIT_ACE = 0x01
CONTAINER_INHERIT_ACE = 0x02
INHERITED_ACE = 0x10
FILE_ALL_ACCESS = 0x001F01FF
FILE_READ_CONTROL = 0x00020000
FILE_DELETE = 0x00010000
FILE_WRITE_DATA = 0x00000002
FILE_APPEND_DATA = 0x00000004
FILE_WRITE_EA = 0x00000010
FILE_DELETE_CHILD = 0x00000040
FILE_WRITE_ATTRIBUTES = 0x00000100
WRITE_DAC = 0x00040000
WRITE_OWNER = 0x00080000
GENERIC_WRITE = 0x40000000
GENERIC_ALL = 0x10000000
ACCESS_SYSTEM_SECURITY = 0x01000000
SE_GROUP_ENABLED = 0x00000004
FILE_SHARE_DELETE = 0x00000004
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
SYSTEM_SID = "S-1-5-18"
ADMINISTRATORS_SID = "S-1-5-32-544"
OWNER_RIGHTS_SID = "S-1-3-4"
PROFILE_PARENT_MUTATION_MASK = (
    FILE_WRITE_DATA
    | FILE_APPEND_DATA
    | FILE_WRITE_EA
    | FILE_DELETE_CHILD
    | FILE_DELETE
    | FILE_WRITE_ATTRIBUTES
    | WRITE_DAC
    | WRITE_OWNER
    | GENERIC_WRITE
    | GENERIC_ALL
    | ACCESS_SYSTEM_SECURITY
)
CMD_SAFE_TOKEN = re.compile(r"\A[A-Za-z0-9_:\\/.-]+\Z", re.ASCII)
LICENSE_ENVIRONMENT_NAMES = ("XILINXD_LICENSE_FILE", "LM_LICENSE_FILE")


class ControllerError(RuntimeError):
    """预检、监护或产物闭合不能证明时停止bitgen。"""


class FILE_ATTRIBUTE_TAG_INFO(ctypes.Structure):
    _fields_ = [("FileAttributes", job_guard.wintypes.DWORD), ("ReparseTag", job_guard.wintypes.DWORD)]


class SID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("Sid", ctypes.c_void_p), ("Attributes", job_guard.wintypes.DWORD)]


class TOKEN_USER(ctypes.Structure):
    _fields_ = [("User", SID_AND_ATTRIBUTES)]


class TOKEN_GROUPS_HEADER(ctypes.Structure):
    _fields_ = [("GroupCount", job_guard.wintypes.DWORD), ("Groups", SID_AND_ATTRIBUTES * 1)]


class ACL_HEADER(ctypes.Structure):
    _fields_ = [
        ("AclRevision", job_guard.wintypes.BYTE),
        ("Sbz1", job_guard.wintypes.BYTE),
        ("AclSize", job_guard.wintypes.WORD),
        ("AceCount", job_guard.wintypes.WORD),
        ("Sbz2", job_guard.wintypes.WORD),
    ]


class ACE_HEADER(ctypes.Structure):
    _fields_ = [
        ("AceType", job_guard.wintypes.BYTE),
        ("AceFlags", job_guard.wintypes.BYTE),
        ("AceSize", job_guard.wintypes.WORD),
    ]


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


def _record_controller_exception(manifest, error):
    """以固定脱敏结构记录控制器异常，不序列化异常类型或原始文本。"""
    manifest["controller_exception"] = {
        "category": "CONTROLLER_EXCEPTION",
        "details_redacted": True,
        "message": "原始异常文本已省略",
    }
    manifest["status"] = "FAILED_OR_INCOMPLETE"
    manifest["stop_reason"] = "CONTROLLER_EXCEPTION_REDACTED"
    return manifest["stop_reason"]


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


def _user_documents_profile_root(current_user_sid):
    """从当前用户的规范USERPROFILE推导已存在的Documents根目录。"""
    profile_value = os.environ.get("USERPROFILE")
    if not profile_value:
        raise ControllerError("USERPROFILE未定义，拒绝退回到TEMP或LocalAppData")
    profile_path = _assert_path_chain(profile_value, "directory")
    canonical_profile = str(Path(profile_path).resolve(strict=True))
    if os.path.normcase(os.path.normpath(profile_path)) != os.path.normcase(
        os.path.normpath(canonical_profile)
    ):
        raise ControllerError("USERPROFILE不是规范路径或含路径别名")
    _verify_private_profile_parent(
        canonical_profile,
        current_user_sid,
        allowed_owner_sids=(SYSTEM_SID, ADMINISTRATORS_SID),
    )
    documents_path = os.path.join(canonical_profile, "Documents")
    documents_path = _assert_path_chain(documents_path, "directory")
    canonical_documents = str(Path(documents_path).resolve(strict=True))
    if os.path.normcase(os.path.normpath(documents_path)) != os.path.normcase(
        os.path.normpath(canonical_documents)
    ):
        raise ControllerError("USERPROFILE下Documents不是规范路径或含路径别名")
    return canonical_documents


def _verified_vivado_batch_paths(batch_path):
    """验证Vivado批处理入口，并返回其实际安装bin目录。"""
    verified_batch = _assert_path_chain(batch_path, "file")
    working_directory = _assert_path_chain(os.path.dirname(verified_batch), "directory")
    return verified_batch, working_directory


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


def _validate_cmd_token(token, label):
    """只允许不含cmd展开、控制符、空白或引用符的固定安全参数。"""
    if not isinstance(token, str) or not token or not CMD_SAFE_TOKEN.fullmatch(token):
        raise ControllerError(f"拒绝不安全cmd.exe参数{label}：{token!r}")
    return token


def _build_cmd_batch_argv(cmd_executable, batch_path, batch_arguments):
    """以无引号安全词构造cmd /D /S /C命令，避免批处理注入和转义歧义。"""
    _validate_cmd_token(cmd_executable, "cmd映像")
    _validate_cmd_token(batch_path, "批处理路径")
    if not os.path.isabs(cmd_executable) or not os.path.isabs(batch_path):
        raise ControllerError("cmd映像与批处理入口都必须是绝对路径")
    if not isinstance(batch_arguments, (list, tuple)):
        raise ControllerError("批处理参数必须是序列")
    safe_arguments = [
        _validate_cmd_token(value, f"[{index}]")
        for index, value in enumerate(batch_arguments)
    ]
    command = "call " + " ".join([batch_path, *safe_arguments])
    argv = [cmd_executable, "/D", "/S", "/V:OFF", "/C", command]
    return argv, command


def _verify_vivado_batch_chain(batch_paths):
    """静态核对Vivado入口、loader、rdiArgs及setupEnv之间的厂商调用链。"""
    contents = {}
    for name, path in batch_paths.items():
        contents[name] = Path(path).read_text(encoding="utf-8", errors="replace").casefold()
    required_calls = {
        "vivado.bat": (
            'call "%_rdi_binroot%/setupenv.bat"',
            'call "%rdi_binroot%/setupenv.bat" "%rdi_binroot%" xilinx_vivado',
            'call "%rdi_binroot%/loader.bat" -exec %rdi_prog% %*',
        ),
        "loader.bat": (
            'call "%rdi_binroot%/rdiargs.bat" %*',
            r"set xvredist=%rdi_approot%\tps\%rdi_platform%\xvcredist.exe",
            "if not [%xil_pa_no_redist_check%] == [1] (",
            '"%xvredist%" -check',
            "if [!errorlevel!] == [1] (",
            "if not defined _rdi_setenv_run (",
        ),
        "rdiArgs.bat": (
            'call "%rdi_binroot%/setupenv.bat"',
            "set rdi_platform=win64",
            "if [%2] == [batch] (",
            "set rdi_batch_mode=true",
        ),
        "setupEnv.bat": (
            "if defined rdi_setup_env_function (",
            "call :%rdi_setup_env_function% %*",
            "set rdi_setup_env_function=",
            "set rdi_binroot=%~dp0",
            'call :dirname "%rdi_binroot%" rdi_approot',
        ),
    }
    for name, snippets in required_calls.items():
        text = contents.get(name)
        if text is None:
            raise ControllerError(f"Vivado批处理链缺少{name}")
        for snippet in snippets:
            if snippet not in text:
                raise ControllerError(f"Vivado批处理调用链与预期不符：{name} 缺少 {snippet!r}")
    vivado_text = contents["vivado.bat"]
    initial_setup_call = vivado_text.find('call "%_rdi_binroot%/setupenv.bat"')
    internal_hook_assignment = vivado_text.find("set rdi_setup_env_function=dirname")
    if initial_setup_call < 0 or internal_hook_assignment < 0 or initial_setup_call > internal_hook_assignment:
        raise ControllerError("Vivado入口未先于内部DIRNAME钩子调用setupEnv正常初始化")
    return {name: list(snippets) for name, snippets in required_calls.items()}


def _vivado_setup_environment_guard(environment):
    """拒绝父环境覆盖setupEnv根路径或控制其初始化流程的变量。"""
    present = sorted(name for name in VIVADO_SETUP_ENVIRONMENT_VARIABLES if environment.get(name) is not None)
    if present:
        raise ControllerError("Vivado setupEnv环境覆盖拒绝：" + ",".join(present))
    vivado_binroot = Path(VIVADO_BIN)
    return {
        "status": "PASS_PARENT_OVERRIDES_ABSENT",
        "parent_override_variables_absent": list(VIVADO_SETUP_ENVIRONMENT_VARIABLES),
        "child_override_variables_removed": list(VIVADO_SETUP_ENVIRONMENT_VARIABLES),
        "rdi_binroot": str(vivado_binroot),
        "rdi_approot": str(vivado_binroot.parent),
        "setupenv_initialization_source": "setupEnv.bat derives RDI_BINROOT from its own %~dp0, then RDI_APPROOT from RDI_BINROOT",
    }


def _validate_xvcredist_link_observation(link_directory, link_target, resolved_directory):
    """只接受已核验的Vivado tps相对符号链接及其精确目标。"""
    expected_link = os.path.normcase(os.path.abspath(XVCREDIST_LINK_DIRECTORY))
    observed_link = os.path.normcase(os.path.abspath(os.fspath(link_directory)))
    if observed_link != expected_link:
        raise ControllerError("xvcredist tps符号链接路径与核验路径不符")
    if link_target != XVCREDIST_LINK_TARGET:
        raise ControllerError("xvcredist tps符号链接文本目标与核验值不符")
    expected_target = os.path.normcase(os.path.abspath(XVCREDIST_RESOLVED_ROOT))
    observed_target = os.path.normcase(os.path.abspath(os.fspath(resolved_directory)))
    if observed_target != expected_target:
        raise ControllerError("xvcredist tps符号链接严格解析目标与核验路径不符")
    return {
        "link_directory_path": os.path.abspath(os.fspath(link_directory)),
        "link_type": "symbolic_link",
        "link_target": link_target,
        "expected_link_target": XVCREDIST_LINK_TARGET,
        "resolved_target_path": os.path.abspath(os.fspath(resolved_directory)),
        "expected_resolved_target_path": XVCREDIST_RESOLVED_ROOT,
    }


def _resolve_xvcredist_executable():
    """解析唯一允许的tps链接，再校验真实xvcredist二进制路径。"""
    link_directory = Path(XVCREDIST_LINK_DIRECTORY)
    logical_executable = Path(XVCREDIST_EXE)
    expected_logical_executable = link_directory / "win64" / "xvcredist.exe"
    if os.path.normcase(os.path.abspath(logical_executable)) != os.path.normcase(
        os.path.abspath(expected_logical_executable)
    ):
        raise ControllerError("xvcredist逻辑入口路径与核验的tps链接不符")
    _assert_path_chain(link_directory.parent, "directory")
    if not link_directory.is_symlink():
        raise ControllerError("Vivado\\tps不是要求的符号链接")
    try:
        link_target = os.readlink(os.fspath(link_directory))
        resolved_directory = link_directory.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ControllerError(f"解析Vivado\\tps符号链接失败：{error}") from error
    link_facts = _validate_xvcredist_link_observation(link_directory, link_target, resolved_directory)
    resolved_executable = _assert_path_chain(
        Path(link_facts["resolved_target_path"]) / "win64" / "xvcredist.exe",
        "file",
    )
    link_facts["logical_executable_path"] = str(logical_executable)
    link_facts["resolved_executable_path"] = resolved_executable
    return resolved_executable, link_facts


def _recheck_xvcredist_link_before_bitgen(facts):
    """主Bitgen Job创建前重核tps链接解析及已锁定二进制哈希。"""
    executable, current = _resolve_xvcredist_executable()
    expected = facts["xvcredist_link_resolution"]
    for key in ("link_directory_path", "link_target", "resolved_target_path", "logical_executable_path", "resolved_executable_path"):
        if key == "link_target":
            unchanged = current[key] == expected[key]
        else:
            unchanged = os.path.normcase(os.path.abspath(current[key])) == os.path.normcase(
                os.path.abspath(expected[key])
            )
        if not unchanged:
            raise ControllerError(f"Bitgen启动前xvcredist链接解析变化：{key}")
    digest = _sha256(executable)
    if digest != facts["xvcredist_executable_sha256"]:
        raise ControllerError("Bitgen启动前xvcredist真实二进制SHA256变化")
    current["status"] = "PASS_UNCHANGED_BEFORE_BITGEN_JOB"
    current["resolved_executable_sha256"] = digest
    return current


def _preflight_inputs():
    setup_environment_guard = _vivado_setup_environment_guard(os.environ)
    _ensure_exact_repository()
    dcp = _assert_path_chain(FROZEN_DCP, "file")
    cmd_executable = _assert_path_chain(CMD_EXE, "file")
    vivado_batch, vivado_working_directory = _verified_vivado_batch_paths(VIVADO_BAT)
    vivado_executable = _assert_path_chain(VIVADO_EXE, "file")
    support_paths = {
        name: _assert_path_chain(path, "file")
        for name, path in VIVADO_BATCH_SUPPORT.items()
    }
    vivado_binroot = Path(vivado_batch).parent
    if os.path.normcase(os.path.abspath(VIVADO_BIN)) != os.path.normcase(os.path.abspath(vivado_binroot)):
        raise ControllerError("Vivado配置binroot与入口vivado.bat所在目录不一致")
    for name, path in support_paths.items():
        if os.path.normcase(os.path.abspath(Path(path).parent)) != os.path.normcase(os.path.abspath(vivado_binroot)):
            raise ControllerError(f"Vivado批处理依赖{name}不在入口binroot，无法绑定setupEnv解析路径")
    setup_environment_guard.update(
        {
            "rdi_binroot": str(vivado_binroot),
            "rdi_approot": str(vivado_binroot.parent),
            "setupenv_path": support_paths["setupEnv.bat"],
            "setupenv_sha256": _sha256(support_paths["setupEnv.bat"]),
        }
    )
    redist_path, xvcredist_link_resolution = _resolve_xvcredist_executable()
    redist_app_root = Path(vivado_batch).parent.parent
    expected_redist_path = redist_app_root / "tps" / "win64" / "xvcredist.exe"
    if os.path.normcase(os.path.abspath(xvcredist_link_resolution["logical_executable_path"])) != os.path.normcase(
        os.path.abspath(expected_redist_path)
    ):
        raise ControllerError("xvcredist预检映像路径与Vivado入口的AppRoot/win64解析不符")
    if _sha256(redist_path) != EXPECTED_XVCREDIST_SHA256:
        raise ControllerError("xvcredist.exe SHA256与已核验安装包不符")
    baseline_path = redist_app_root / "data" / "baseline.txt"
    if os.path.lexists(baseline_path):
        raise ControllerError("检测到Vivado baseline.txt会重定向loader的RDI_APPROOT，拒绝跳过未绑定检查")
    source = _assert_path_chain(Path(__file__).with_name(TCL_SCRIPT_NAME), "file")
    evidence = _effective_evidence_root()
    dcp_hash = _sha256(dcp)
    if dcp_hash != EXPECTED_DCP_SHA256:
        raise ControllerError(f"冻结DCP SHA256不符：expected={EXPECTED_DCP_SHA256}, actual={dcp_hash}")
    batch_paths = {"vivado.bat": vivado_batch, **support_paths}
    batch_call_chain = _verify_vivado_batch_chain(batch_paths)
    install_init_candidates = _install_vivado_init_candidates()
    for init_path in install_init_candidates:
        scripts_dir = os.path.dirname(init_path)
        if os.path.lexists(scripts_dir):
            _assert_path_chain(scripts_dir, "directory")
        if os.path.lexists(init_path):
            _assert_path_chain(init_path, "file")
            raise ControllerError(f"检测到可能在Vivado启动时自动执行的安装级Tcl初始化脚本：{init_path!r}")
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise ControllerError("APPDATA未定义，不能审计默认许可证且保留显式许可设置")
    _assert_path_chain(appdata, "directory")
    user_init_audit = _audit_user_init_scripts(appdata)
    license_audit = _audit_license_configuration(os.environ, appdata)
    if not license_audit["usable"]:
        raise ControllerError(
            "缺少非空显式XILINXD_LICENSE_FILE/LM_LICENSE_FILE，且APPDATA下没有唯一可核验的默认.lic"
        )
    toolchain_files = {
        "cmd.exe": {"path": cmd_executable, "sha256": _sha256(cmd_executable)},
        "vivado.bat": {"path": vivado_batch, "sha256": _sha256(vivado_batch)},
        "vivado.exe": {"path": vivado_executable, "sha256": _sha256(vivado_executable)},
        "xvcredist.exe": {"path": redist_path, "sha256": _sha256(redist_path)},
        **{
            name: {"path": path, "sha256": _sha256(path)}
            for name, path in support_paths.items()
        },
    }
    return {
        "dcp_path": dcp,
        "dcp_sha256": dcp_hash,
        "cmd_executable_path": cmd_executable,
        "vivado_batch_path": vivado_batch,
        "vivado_working_directory": vivado_working_directory,
        "vivado_executable_path": vivado_executable,
        "vivado_executable_sha256": toolchain_files["vivado.exe"]["sha256"],
        "xvcredist_executable_path": redist_path,
        "xvcredist_executable_sha256": toolchain_files["xvcredist.exe"]["sha256"],
        "xvcredist_link_resolution": xvcredist_link_resolution,
        "redist_resolution_guard": {
            "rdi_bin_root": str(Path(vivado_batch).parent),
            "rdi_app_root": str(redist_app_root),
            "rdi_platform": "win64",
            "baseline_path": str(baseline_path),
            "baseline_absent": True,
            "path_override_environment_absent": ["XILINX_PATH", "MYVIVADO", "RDI_BASELINE"],
        },
        "vivado_setup_environment_guard": setup_environment_guard,
        "toolchain_files": toolchain_files,
        "batch_call_chain": batch_call_chain,
        "vivado_expected_version": EXPECTED_VIVADO_VERSION,
        "tcl_source_path": source,
        "tcl_source_sha256": _sha256(source),
        "controller_source_path": _assert_path_chain(__file__, "file"),
        "controller_source_sha256": _sha256(__file__),
        "evidence_root": evidence,
        "vivado_install_init_candidates_absent": install_init_candidates,
        "user_init_script_audit": user_init_audit,
        "parent_appdata_isolated": True,
        "license_environment_audit": license_audit,
    }


def _install_vivado_init_candidates():
    """列出Vivado安装树中可能自动source的初始化脚本。"""
    product_root = Path(VIVADO_EXE).parents[3]
    names = ("Vivado_init.tcl", "init.tcl")
    return [
        str(root / name)
        for root in (product_root / EXPECTED_VIVADO_VERSION / "scripts", product_root / "scripts")
        for name in names
    ]


def _audit_user_init_scripts(appdata):
    """只记录用户Tcl初始化脚本的相对位置和哈希，不读取或执行脚本内容。"""
    appdata = _assert_path_chain(appdata, "directory")
    user_root = Path(appdata) / "Xilinx" / "Vivado"
    candidates = (
        ("versioned/Vivado_init.tcl", user_root / EXPECTED_VIVADO_VERSION / "Vivado_init.tcl"),
        ("versioned/init.tcl", user_root / EXPECTED_VIVADO_VERSION / "init.tcl"),
        ("general/Vivado_init.tcl", user_root / "Vivado_init.tcl"),
        ("general/init.tcl", user_root / "init.tcl"),
    )
    records = []
    for relative_name, candidate in candidates:
        if not os.path.lexists(candidate):
            records.append({"relative_name": relative_name, "exists": False, "sha256": None})
            continue
        _assert_path_chain(candidate, "file")
        records.append(
            {
                "relative_name": relative_name,
                "exists": True,
                "size_bytes": os.path.getsize(candidate),
                "sha256": _sha256(candidate),
            }
        )
    return {"source_scripts": records, "copied_to_child_appdata": False}


def _probe_default_license_directory(appdata):
    """只审计APPDATA默认许可证文件的存在、长度和哈希，不记录路径或内容。"""
    license_dir = Path(appdata) / "XilinxLicense"
    result = {"directory_exists": False, "license_file_count": 0, "files": [], "uninspectable_entries": 0}
    if not os.path.lexists(license_dir):
        return result
    try:
        _assert_path_chain(license_dir, "directory")
        entries = list(license_dir.iterdir())
    except BaseException:
        result["directory_exists"] = True
        result["uninspectable_entries"] = 1
        return result
    result["directory_exists"] = True
    for entry in entries:
        if entry.suffix.casefold() != ".lic":
            continue
        try:
            _assert_path_chain(entry, "file")
            size = os.path.getsize(entry)
            digest = _sha256(entry)
        except BaseException:
            result["uninspectable_entries"] += 1
            continue
        result["files"].append({"size_bytes": size, "sha256": digest})
    result["license_file_count"] = len(result["files"])
    return result


def _resolve_single_default_license_path(appdata, license_audit):
    """在私有APPDATA启动前重核唯一默认许可证，仅返回实际传给Vivado的路径。"""
    if not license_audit.get("default_license_used"):
        return None
    try:
        license_dir = Path(appdata) / "XilinxLicense"
        selected = [entry for entry in license_dir.iterdir() if entry.suffix.casefold() == ".lic"]
        recorded = license_audit["default_appdata_license_probe"]["files"]
        if len(selected) != 1 or len(recorded) != 1:
            raise OSError("default license file set changed")
        path = _assert_path_chain(selected[0], "file")
        record = {"size_bytes": os.path.getsize(path), "sha256": _sha256(path)}
        if record != recorded[0]:
            raise OSError("default license metadata changed")
        return path
    except BaseException:
        raise ControllerError("默认许可证路径重核失败；原始异常与路径已隐藏") from None


def _audit_license_configuration(environment, appdata):
    """只核对显式许可变量是否非空，或唯一默认许可证文件的元数据。"""
    variables = []
    any_explicit_value = False
    for name in LICENSE_ENVIRONMENT_NAMES:
        raw_value = environment.get(name)
        present = raw_value is not None and bool(raw_value.strip())
        any_explicit_value = any_explicit_value or present
        variables.append(
            {
                "name": name,
                "set": raw_value is not None,
                "nonempty": present,
                "value_sha256": hashlib.sha256(raw_value.encode("utf-8")).hexdigest().upper()
                if raw_value is not None
                else None,
            }
        )
    default_probe = _probe_default_license_directory(appdata)
    default_files = default_probe["files"]
    default_usable = (
        not any_explicit_value
        and default_probe["uninspectable_entries"] == 0
        and len(default_files) == 1
        and default_files[0]["size_bytes"] > 0
    )
    return {
        "usable": any_explicit_value or default_usable,
        "mode": "explicit_environment" if any_explicit_value else "single_default_file" if default_usable else "unavailable",
        "fallback_license_path": default_probe.get("single_file_path") if default_usable else None,
        "fallback_license_sha256": default_files[0]["sha256"] if default_usable else None,
        "fallback_license_size_bytes": default_files[0]["size_bytes"] if default_usable else None,
        "variables": variables,
        "default_appdata_license_probe": default_probe,
        "default_license_used": default_usable,
    }


def _sid_to_string(sid_pointer):
    """将Win32 SID转换为可精确比较的文本并释放系统分配缓冲区。"""
    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    advapi32.ConvertSidToStringSidW.argtypes = [ctypes.c_void_p, ctypes.POINTER(job_guard.wintypes.LPWSTR)]
    advapi32.ConvertSidToStringSidW.restype = job_guard.wintypes.BOOL
    text_pointer = job_guard.wintypes.LPWSTR()
    if not advapi32.ConvertSidToStringSidW(sid_pointer, ctypes.byref(text_pointer)):
        raise job_guard._win_error("ConvertSidToStringSidW")
    try:
        return text_pointer.value
    finally:
        job_guard.kernel32.LocalFree.argtypes = [job_guard.wintypes.HLOCAL]
        job_guard.kernel32.LocalFree.restype = job_guard.wintypes.HLOCAL
        job_guard.kernel32.LocalFree(ctypes.cast(text_pointer, job_guard.wintypes.HLOCAL))


def _current_process_token_sids():
    """读取当前进程用户和启用组SID，不依赖显示名称或账户名。"""
    kernel32 = job_guard.kernel32
    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel32.GetCurrentProcess.argtypes = []
    kernel32.GetCurrentProcess.restype = job_guard.wintypes.HANDLE
    advapi32.OpenProcessToken.argtypes = [
        job_guard.wintypes.HANDLE,
        job_guard.wintypes.DWORD,
        ctypes.POINTER(job_guard.wintypes.HANDLE),
    ]
    advapi32.OpenProcessToken.restype = job_guard.wintypes.BOOL
    advapi32.GetTokenInformation.argtypes = [
        job_guard.wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        job_guard.wintypes.DWORD,
        ctypes.POINTER(job_guard.wintypes.DWORD),
    ]
    advapi32.GetTokenInformation.restype = job_guard.wintypes.BOOL
    token = job_guard.wintypes.HANDLE()
    if not advapi32.OpenProcessToken(kernel32.GetCurrentProcess(), TOKEN_QUERY, ctypes.byref(token)):
        raise job_guard._win_error("OpenProcessToken(profile ACL)")
    try:
        def read_token_buffer(token_class, minimum_size):
            required = job_guard.wintypes.DWORD()
            advapi32.GetTokenInformation(token, token_class, None, 0, ctypes.byref(required))
            if ctypes.get_last_error() != ERROR_INSUFFICIENT_BUFFER or required.value < minimum_size:
                raise job_guard._win_error("GetTokenInformation(buffer size)")
            buffer = ctypes.create_string_buffer(required.value)
            if not advapi32.GetTokenInformation(
                token, token_class, ctypes.byref(buffer), required.value, ctypes.byref(required)
            ):
                raise job_guard._win_error("GetTokenInformation(profile ACL)")
            return buffer

        user_buffer = read_token_buffer(TOKEN_USER_CLASS, ctypes.sizeof(TOKEN_USER))
        user = ctypes.cast(ctypes.byref(user_buffer), ctypes.POINTER(TOKEN_USER)).contents
        if not user.User.Sid:
            raise ControllerError("当前进程令牌用户SID为空")
        user_sid = _sid_to_string(user.User.Sid)
        groups_buffer = read_token_buffer(2, ctypes.sizeof(TOKEN_GROUPS_HEADER))
        groups = ctypes.cast(ctypes.byref(groups_buffer), ctypes.POINTER(TOKEN_GROUPS_HEADER)).contents
        group_base = ctypes.addressof(groups_buffer) + TOKEN_GROUPS_HEADER.Groups.offset
        group_size = ctypes.sizeof(SID_AND_ATTRIBUTES)
        enabled_groups = set()
        for index in range(int(groups.GroupCount)):
            group = ctypes.cast(group_base + index * group_size, ctypes.POINTER(SID_AND_ATTRIBUTES)).contents
            if int(group.Attributes) & SE_GROUP_ENABLED and group.Sid:
                enabled_groups.add(_sid_to_string(group.Sid).casefold())
        return user_sid, enabled_groups
    finally:
        job_guard._checked_close_handle(token, "profile ACL process token")


def _create_private_profile_directory(profile_path, current_user_sid):
    """在首次创建目录时原子指定受保护的私有DACL。"""
    sddl = (
        f"O:{current_user_sid}D:P"
        f"(A;OICI;FA;;;{current_user_sid})"
        f"(A;OICI;FA;;;{SYSTEM_SID})"
        f"(A;OICI;FA;;;{ADMINISTRATORS_SID})"
    )
    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [
        job_guard.wintypes.LPCWSTR,
        job_guard.wintypes.DWORD,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(job_guard.wintypes.DWORD),
    ]
    advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW.restype = job_guard.wintypes.BOOL
    descriptor = ctypes.c_void_p()
    descriptor_size = job_guard.wintypes.DWORD()
    if not advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW(
        sddl, 1, ctypes.byref(descriptor), ctypes.byref(descriptor_size)
    ):
        raise job_guard._win_error("ConvertStringSecurityDescriptorToSecurityDescriptorW(private APPDATA)")
    try:
        security_attributes = job_guard.SECURITY_ATTRIBUTES(
            ctypes.sizeof(job_guard.SECURITY_ATTRIBUTES), descriptor, False
        )
        kernel32 = job_guard.kernel32
        kernel32.CreateDirectoryW.argtypes = [
            job_guard.wintypes.LPCWSTR,
            ctypes.POINTER(job_guard.SECURITY_ATTRIBUTES),
        ]
        kernel32.CreateDirectoryW.restype = job_guard.wintypes.BOOL
        if not kernel32.CreateDirectoryW(str(profile_path), ctypes.byref(security_attributes)):
            error_code = ctypes.get_last_error()
            if error_code == 183:
                raise ControllerError(f"拒绝复用已存在APPDATA profile路径：{str(profile_path)!r}")
            raise ControllerError(
                f"原子创建受控DACL APPDATA profile失败：path={str(profile_path)!r}, winerror={error_code}"
            )
    finally:
        job_guard.kernel32.LocalFree.argtypes = [job_guard.wintypes.HLOCAL]
        job_guard.kernel32.LocalFree.restype = job_guard.wintypes.HLOCAL
        job_guard.kernel32.LocalFree(ctypes.cast(descriptor, job_guard.wintypes.HLOCAL))


def _inspect_directory_security(
    directory_path,
    current_user_sid,
    require_private_dacl=False,
    require_inherited_profile_dacl=False,
):
    """从目录HANDLE读取owner、DACL和reparse属性。"""
    directory_path = os.fspath(directory_path)
    _assert_path_chain(directory_path, "directory")
    kernel32 = job_guard.kernel32
    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
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
    handle = kernel32.CreateFileW(
        directory_path,
        FILE_READ_CONTROL,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        None,
        OPEN_EXISTING,
        FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS,
        None,
    )
    if not handle or int(handle) == INVALID_HANDLE_VALUE:
        raise job_guard._win_error("CreateFileW(directory security handle)")
    try:
        kernel32.GetFileInformationByHandleEx.argtypes = [
            job_guard.wintypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            job_guard.wintypes.DWORD,
        ]
        kernel32.GetFileInformationByHandleEx.restype = job_guard.wintypes.BOOL
        attributes = FILE_ATTRIBUTE_TAG_INFO()
        if not kernel32.GetFileInformationByHandleEx(
            handle, FILE_ATTRIBUTE_TAG_INFO_CLASS, ctypes.byref(attributes), ctypes.sizeof(attributes)
        ):
            raise job_guard._win_error("GetFileInformationByHandleEx(directory security)")
        if int(attributes.FileAttributes) & FILE_ATTRIBUTE_REPARSE_POINT:
            raise ControllerError(f"APPDATA安全目录含重解析点：{directory_path!r}")
        if not int(attributes.FileAttributes) & FILE_ATTRIBUTE_DIRECTORY:
            raise ControllerError(f"APPDATA安全路径不是目录：{directory_path!r}")

        advapi32.GetSecurityInfo.argtypes = [
            job_guard.wintypes.HANDLE,
            job_guard.wintypes.DWORD,
            job_guard.wintypes.DWORD,
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(ctypes.c_void_p),
        ]
        advapi32.GetSecurityInfo.restype = job_guard.wintypes.DWORD
        owner = ctypes.c_void_p()
        dacl = ctypes.c_void_p()
        descriptor = ctypes.c_void_p()
        security_flags = OWNER_SECURITY_INFORMATION | DACL_SECURITY_INFORMATION
        status = advapi32.GetSecurityInfo(
            handle,
            SE_FILE_OBJECT,
            security_flags,
            ctypes.byref(owner),
            None,
            ctypes.byref(dacl),
            None,
            ctypes.byref(descriptor),
        )
        if status != 0:
            raise ControllerError(f"GetSecurityInfo(APPDATA目录)失败：path={directory_path!r}, winerror={int(status)}")
        try:
            if not owner.value or not dacl.value:
                raise ControllerError(f"APPDATA安全目录缺少owner或DACL：{directory_path!r}")
            owner_sid = _sid_to_string(owner)
            if owner_sid.casefold() != current_user_sid.casefold():
                raise ControllerError(f"APPDATA安全目录owner不是当前用户：{directory_path!r}")
            advapi32.GetSecurityDescriptorControl.argtypes = [
                ctypes.c_void_p,
                ctypes.POINTER(job_guard.wintypes.WORD),
                ctypes.POINTER(job_guard.wintypes.DWORD),
            ]
            advapi32.GetSecurityDescriptorControl.restype = job_guard.wintypes.BOOL
            control = job_guard.wintypes.WORD()
            revision = job_guard.wintypes.DWORD()
            if not advapi32.GetSecurityDescriptorControl(descriptor, ctypes.byref(control), ctypes.byref(revision)):
                raise job_guard._win_error("GetSecurityDescriptorControl(APPDATA)")
            protected = bool(control.value & SE_DACL_PROTECTED)
            if require_private_dacl and not protected:
                raise ControllerError(f"APPDATA profile DACL未protected：{directory_path!r}")
            if require_inherited_profile_dacl and protected:
                raise ControllerError(f"APPDATA profile子项未继承受控DACL：{directory_path!r}")
            if not require_private_dacl and not require_inherited_profile_dacl:
                return {
                    "owner_matches_current_user": True,
                    "dacl_protected": protected,
                    "directory_path": directory_path,
                }

            acl = ctypes.cast(dacl, ctypes.POINTER(ACL_HEADER)).contents
            if int(acl.AceCount) != 3:
                raise ControllerError(f"APPDATA profile DACL ACE数量不为3：{directory_path!r}")
            expected_roles = {
                current_user_sid.casefold(): "CURRENT_USER",
                SYSTEM_SID.casefold(): "SYSTEM",
                ADMINISTRATORS_SID.casefold(): "ADMINISTRATORS",
            }
            expected_flags = OBJECT_INHERIT_ACE | CONTAINER_INHERIT_ACE
            if require_inherited_profile_dacl:
                expected_flags |= INHERITED_ACE
            observed = []
            for index in range(int(acl.AceCount)):
                ace_pointer = ctypes.c_void_p()
                if not advapi32.GetAce(dacl, index, ctypes.byref(ace_pointer)):
                    raise job_guard._win_error("GetAce(APPDATA profile)")
                ace_header = ctypes.cast(ace_pointer, ctypes.POINTER(ACE_HEADER)).contents
                if ace_header.AceType != ACCESS_ALLOWED_ACE_TYPE or int(ace_header.AceSize) < 16:
                    raise ControllerError(f"APPDATA profile DACL含额外ACE：{directory_path!r}")
                mask = ctypes.c_uint32.from_address(ace_pointer.value + 4).value
                sid_text = _sid_to_string(ctypes.c_void_p(ace_pointer.value + 8)).casefold()
                role = expected_roles.get(sid_text)
                if (
                    role is None
                    or int(ace_header.AceFlags) != expected_flags
                    or mask != FILE_ALL_ACCESS
                ):
                    raise ControllerError(f"APPDATA profile DACL主体或权限不精确：{directory_path!r}")
                observed.append({"principal": role, "mask": mask, "inherit_flags": int(ace_header.AceFlags)})
            if {item["principal"] for item in observed} != {"CURRENT_USER", "SYSTEM", "ADMINISTRATORS"}:
                raise ControllerError(f"APPDATA profile DACL主体集合不精确：{directory_path!r}")
            return {
                "owner_matches_current_user": True,
                "current_user_sid_sha256": hashlib.sha256(current_user_sid.encode("ascii")).hexdigest().upper(),
                "dacl_protected": protected,
                "ace_count": len(observed),
                "aces": sorted(observed, key=lambda item: item["principal"]),
                "only_expected_principals_with_full_control": True,
            }
        finally:
            if descriptor.value:
                kernel32.LocalFree.argtypes = [job_guard.wintypes.HLOCAL]
                kernel32.LocalFree.restype = job_guard.wintypes.HLOCAL
                kernel32.LocalFree(ctypes.cast(descriptor, job_guard.wintypes.HLOCAL))
    finally:
        job_guard._checked_close_handle(handle, "APPDATA directory security handle")


def _audit_private_profile_parent_acl(
    current_user_sid, owner_sid, ace_entries, allowed_owner_sids=None
):
    """按全部ACE审计profile父目录，拒绝非可信主体获得任何修改权限。"""
    sid_pattern = re.compile(r"S-[0-9]+-(?:[0-9]+-)*[0-9]+\Z", re.ASCII)
    if not isinstance(current_user_sid, str) or not sid_pattern.fullmatch(current_user_sid):
        raise ControllerError("当前用户SID无法安全解析")
    if not isinstance(owner_sid, str) or not sid_pattern.fullmatch(owner_sid):
        raise ControllerError("APPDATA父目录owner SID无法安全解析")
    owner_roles = {
        current_user_sid.casefold(): "CURRENT_USER",
        SYSTEM_SID.casefold(): "SYSTEM",
        ADMINISTRATORS_SID.casefold(): "ADMINISTRATORS",
    }
    permitted_owner_sids = {current_user_sid.casefold()}
    if allowed_owner_sids is not None:
        if not isinstance(allowed_owner_sids, (list, tuple, set, frozenset)):
            raise ControllerError("APPDATA父目录owner允许列表无效")
        for allowed_sid in allowed_owner_sids:
            if (
                not isinstance(allowed_sid, str)
                or not sid_pattern.fullmatch(allowed_sid)
                or allowed_sid.casefold()
                not in {SYSTEM_SID.casefold(), ADMINISTRATORS_SID.casefold()}
            ):
                raise ControllerError("APPDATA父目录owner允许列表含未信任主体")
            permitted_owner_sids.add(allowed_sid.casefold())
    owner_role = owner_roles.get(owner_sid.casefold())
    if owner_sid.casefold() not in permitted_owner_sids or owner_role is None:
        raise ControllerError("APPDATA父目录owner不属于明确允许的当前用户或系统主体")
    if not isinstance(ace_entries, (list, tuple)):
        raise ControllerError("APPDATA父目录ACE列表无法安全解析")

    trusted_principals = {
        current_user_sid.casefold(),
        SYSTEM_SID.casefold(),
        ADMINISTRATORS_SID.casefold(),
    }
    if owner_sid.casefold() == current_user_sid.casefold():
        trusted_principals.add(OWNER_RIGHTS_SID.casefold())
    nontrusted_readonly_count = 0
    for entry in ace_entries:
        if not isinstance(entry, dict) or entry.get("ace_type") != ACCESS_ALLOWED_ACE_TYPE:
            raise ControllerError("APPDATA父目录含非允许或无法安全评估的ACE")
        sid_text = entry.get("sid")
        if not isinstance(sid_text, str) or not sid_pattern.fullmatch(sid_text):
            raise ControllerError("APPDATA父目录ACE主体SID无法安全解析")
        mask = entry.get("mask")
        if not isinstance(mask, int) or mask < 0 or mask > 0xFFFFFFFF:
            raise ControllerError("APPDATA父目录ACE权限掩码无法安全解析")
        if sid_text.casefold() not in trusted_principals:
            if mask & PROFILE_PARENT_MUTATION_MASK:
                raise ControllerError(
                    "APPDATA父目录非受信任主体具有写入或替换权限："
                    f"sid={sid_text!r}, mask=0x{mask:08X}"
                )
            nontrusted_readonly_count += 1
    return {
        "owner_matches_current_user": owner_sid.casefold() == current_user_sid.casefold(),
        "owner_role": owner_role,
        "parent_mutable_by_nontrusted_principal": False,
        "ace_count": len(ace_entries),
        "nontrusted_readonly_ace_count": nontrusted_readonly_count,
    }


def _verify_private_profile_parent(parent_path, current_user_sid, allowed_owner_sids=None):
    """拒绝能被非可信主体修改或替换profile的父目录。"""
    path = _assert_path_chain(parent_path, "directory")
    token_user_sid, _enabled_groups = _current_process_token_sids()
    if token_user_sid.casefold() != current_user_sid.casefold():
        raise ControllerError("APPDATA父目录审计期间当前进程用户SID发生变化")
    kernel32 = job_guard.kernel32
    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    advapi32.GetSecurityInfo.argtypes = [
        job_guard.wintypes.HANDLE,
        job_guard.wintypes.DWORD,
        job_guard.wintypes.DWORD,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_void_p),
    ]
    advapi32.GetSecurityInfo.restype = job_guard.wintypes.DWORD
    handle = kernel32.CreateFileW(
        path,
        FILE_READ_CONTROL,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        None,
        OPEN_EXISTING,
        FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS,
        None,
    )
    if not handle or int(handle) == INVALID_HANDLE_VALUE:
        raise job_guard._win_error("CreateFileW(APPDATA parent ACL)")
    try:
        owner = ctypes.c_void_p()
        dacl = ctypes.c_void_p()
        descriptor = ctypes.c_void_p()
        status = advapi32.GetSecurityInfo(
            handle,
            SE_FILE_OBJECT,
            OWNER_SECURITY_INFORMATION | DACL_SECURITY_INFORMATION,
            ctypes.byref(owner),
            None,
            ctypes.byref(dacl),
            None,
            ctypes.byref(descriptor),
        )
        if status != 0:
            raise ControllerError(f"读取APPDATA父目录ACL失败：path={path!r}, winerror={int(status)}")
        try:
            if not owner.value or not dacl.value:
                raise ControllerError(f"APPDATA父目录缺少owner或DACL：{path!r}")
            acl = ctypes.cast(dacl, ctypes.POINTER(ACL_HEADER)).contents
            owner_sid = _sid_to_string(owner)
            ace_entries = []
            for index in range(int(acl.AceCount)):
                ace_pointer = ctypes.c_void_p()
                if not advapi32.GetAce(dacl, index, ctypes.byref(ace_pointer)):
                    raise job_guard._win_error("GetAce(APPDATA parent)")
                ace_header = ctypes.cast(ace_pointer, ctypes.POINTER(ACE_HEADER)).contents
                entry = {"ace_type": int(ace_header.AceType)}
                if ace_header.AceType == ACCESS_ALLOWED_ACE_TYPE:
                    if int(ace_header.AceSize) < 16:
                        raise ControllerError(f"APPDATA父目录ACE长度不足以包含SID：{path!r}")
                    entry["mask"] = ctypes.c_uint32.from_address(ace_pointer.value + 4).value
                    entry["sid"] = _sid_to_string(ctypes.c_void_p(ace_pointer.value + 8))
                ace_entries.append(entry)
            acl_audit = _audit_private_profile_parent_acl(
                current_user_sid,
                owner_sid,
                ace_entries,
                allowed_owner_sids=allowed_owner_sids,
            )
            return {
                "owner_matches_current_user": acl_audit["owner_matches_current_user"],
                "owner_role": acl_audit["owner_role"],
                "parent_mutable_by_nontrusted_principal": acl_audit[
                    "parent_mutable_by_nontrusted_principal"
                ],
                "parent_acl_ace_count": acl_audit["ace_count"],
                "nontrusted_readonly_ace_count": acl_audit[
                    "nontrusted_readonly_ace_count"
                ],
            }
        finally:
            if descriptor.value:
                kernel32.LocalFree.argtypes = [job_guard.wintypes.HLOCAL]
                kernel32.LocalFree.restype = job_guard.wintypes.HLOCAL
                kernel32.LocalFree(ctypes.cast(descriptor, job_guard.wintypes.HLOCAL))
    finally:
        job_guard._checked_close_handle(handle, "APPDATA parent ACL handle")


def _path_file_identity(path):
    """读取普通目录项的卷号与文件索引，供失败回滚核对身份。"""
    info = os.lstat(path)
    if stat.S_ISLNK(info.st_mode) or int(getattr(info, "st_file_attributes", 0)) & FILE_ATTRIBUTE_REPARSE_POINT:
        raise ControllerError(f"回滚目标是符号链接或重解析点：{os.fspath(path)!r}")
    return int(info.st_dev), int(info.st_ino)


def _rollback_private_appdata_profile(profile_path, current_user_sid, profile_identity, probe_path, probe_identity):
    """仅在目录身份、ACL和内容均匹配本次创建事实时回滚空profile。"""
    profile_path = Path(profile_path)
    if profile_identity is None or _path_file_identity(profile_path) != profile_identity:
        raise ControllerError(f"APPDATA profile目录身份无法证明，保留路径：{str(profile_path)!r}")
    _inspect_directory_security(profile_path, current_user_sid, require_private_dacl=True)
    entries = list(profile_path.iterdir())
    if entries:
        if len(entries) != 1 or probe_identity is None or entries[0] != probe_path:
            raise ControllerError(f"APPDATA profile含非本次probe内容，保留路径：{str(profile_path)!r}")
        if _path_file_identity(probe_path) != probe_identity:
            raise ControllerError(f"APPDATA profile probe身份无法证明，保留路径：{str(profile_path)!r}")
        probe_info = os.lstat(probe_path)
        if not stat.S_ISREG(probe_info.st_mode) or probe_info.st_size != 0:
            raise ControllerError(f"APPDATA profile probe类型或内容变化，保留路径：{str(profile_path)!r}")
        _assert_path_chain(probe_path, "file")
        probe_path.unlink()
    if list(profile_path.iterdir()):
        raise ControllerError(f"APPDATA profile回滚时目录非空，保留路径：{str(profile_path)!r}")
    if _path_file_identity(profile_path) != profile_identity:
        raise ControllerError(f"APPDATA profile回滚前目录身份变化，保留路径：{str(profile_path)!r}")
    _inspect_directory_security(profile_path, current_user_sid, require_private_dacl=True)
    profile_path.rmdir()


def _verified_tclstore_source_root():
    """只接受已核验的 Vivado data 相对符号链接及其安装内目标。"""
    link_path = Path(TCLSTORE_DATA_LINK)
    _assert_path_chain(link_path.parent, "directory")
    try:
        link_info = os.lstat(link_path)
        link_target = os.readlink(link_path)
    except OSError as error:
        raise ControllerError(f"无法核验Vivado data符号链接：{error!r}") from error
    if not stat.S_ISLNK(link_info.st_mode) or not int(
        getattr(link_info, "st_file_attributes", 0)
    ) & FILE_ATTRIBUTE_REPARSE_POINT:
        raise ControllerError("Vivado data不再是核验过的符号链接")
    if link_target != TCLSTORE_DATA_LINK_TARGET:
        raise ControllerError("Vivado data符号链接文本目标发生变化")
    canonical_data = Path(link_path.resolve(strict=True))
    expected_data = Path(TCLSTORE_CANONICAL_DATA_ROOT)
    install_root = Path(TCLSTORE_INSTALL_ROOT).resolve(strict=True)
    if os.path.normcase(os.path.normpath(str(canonical_data))) != os.path.normcase(
        os.path.normpath(str(expected_data))
    ):
        raise ControllerError("Vivado data符号链接严格解析目标不符")
    if not canonical_data.is_relative_to(install_root):
        raise ControllerError("Vivado data解析目标越出核验的2026.1安装根")
    _assert_path_chain(canonical_data, "directory")
    source_root = canonical_data / "XilinxTclStore"
    if os.path.normcase(os.path.normpath(str(source_root.resolve(strict=True)))) != os.path.normcase(
        os.path.normpath(TCLSTORE_CANONICAL_ROOT)
    ):
        raise ControllerError("Vivado TclStore规范解析路径与核验值不符")
    _assert_path_chain(source_root, "directory")
    return source_root


def _vendor_tclstore_relative_files():
    """只读列举核验版厂商TclStore文件路径，不读取或复制缓存内容。"""
    source_root = _verified_tclstore_source_root()
    relative_files = []
    casefolded = set()
    for current, directory_names, file_names in os.walk(
        source_root, topdown=True, followlinks=False
    ):
        current_path = Path(current)
        retained_directories = []
        for name in sorted(directory_names):
            directory_path = current_path / name
            info = os.lstat(directory_path)
            if stat.S_ISLNK(info.st_mode) or int(
                getattr(info, "st_file_attributes", 0)
            ) & FILE_ATTRIBUTE_REPARSE_POINT:
                raise ControllerError(f"TclStore目录含未核验重解析点：{directory_path!s}")
            retained_directories.append(name)
        directory_names[:] = retained_directories
        for name in sorted(file_names):
            file_path = current_path / name
            info = os.lstat(file_path)
            if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode) or int(
                getattr(info, "st_file_attributes", 0)
            ) & FILE_ATTRIBUTE_REPARSE_POINT:
                raise ControllerError(f"TclStore文件不是普通文件：{file_path!s}")
            relative = file_path.relative_to(source_root).as_posix()
            relative_parts = relative.split("/")
            if (
                not relative
                or any(part in ("", ".", "..") or ":" in part or "\\" in part for part in relative_parts)
            ):
                raise ControllerError(f"TclStore包含不安全相对文件名：{relative!r}")
            folded = relative.casefold()
            if folded in casefolded:
                raise ControllerError(f"TclStore包含大小写不唯一相对路径：{relative!r}")
            casefolded.add(folded)
            relative_files.append(relative)
    if not relative_files:
        raise ControllerError("核验版厂商TclStore没有普通文件，拒绝建立APPDATA配置")
    return sorted(relative_files, key=str.casefold)


def _windows_path_utf16_chars(path):
    """返回Windows路径所占UTF-16代码单元数。"""
    return len(os.fspath(path).encode("utf-16-le")) // 2


def _private_appdata_path_length_audit(appdata_path, vendor_relative_files):
    """要求TclStore每个厂商相对落点都低于传统Windows路径上限。"""
    appdata_path = Path(appdata_path)
    store_root = appdata_path / "Xilinx" / "Vivado" / EXPECTED_VIVADO_VERSION / "XilinxTclStore"
    if not vendor_relative_files:
        raise ControllerError("缺少厂商TclStore相对文件路径，拒绝启动")
    longest = None
    longest_path_chars = -1
    max_relative_chars = 0
    for relative in vendor_relative_files:
        if not isinstance(relative, str):
            raise ControllerError("TclStore相对路径必须是文本")
        parts = relative.split("/")
        if (
            not relative
            or relative.startswith("/")
            or any(part in ("", ".", "..") or ":" in part or "\\" in part for part in parts)
        ):
            raise ControllerError(f"TclStore相对路径不安全：{relative!r}")
        if any(_windows_path_utf16_chars(part) > 255 for part in parts):
            raise ControllerError(f"TclStore路径组件超过Windows单组件上限：{relative!r}")
        relative_chars = _windows_path_utf16_chars(relative.replace("/", os.sep))
        destination = store_root.joinpath(*parts)
        destination_chars = _windows_path_utf16_chars(destination)
        if relative_chars > max_relative_chars:
            max_relative_chars = relative_chars
        if destination_chars > longest_path_chars:
            longest = relative
            longest_path_chars = destination_chars
    if longest_path_chars > APPDATA_MAX_PATH_UTF16_CHARS:
        raise ControllerError(
            "私有APPDATA下TclStore落点超过259 UTF-16字符，拒绝启动："
            f"max={longest_path_chars}, relative={longest!r}"
        )
    return {
        "destination_path_limit_utf16_chars": APPDATA_MAX_PATH_UTF16_CHARS,
        "max_vendor_relative_path_utf16_chars": max_relative_chars,
        "longest_vendor_relative_path": longest,
        "longest_destination_path_utf16_chars": longest_path_chars,
        "vendor_file_count": len(vendor_relative_files),
        "all_destination_paths_within_limit": True,
    }


def _create_private_appdata_profile(run_id, profile_nonce=None, temporary_root=None, vendor_relative_files=None):
    """在ACL已核验的用户Documents或显式测试根中排他创建唯一空APPDATA配置。"""
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,96}", str(run_id), flags=re.ASCII):
        raise ControllerError("RunId不能安全用于私有APPDATA路径")
    if profile_nonce is None:
        profile_nonce = secrets.token_hex(16)
    if not re.fullmatch(r"[0-9a-f]{32}", str(profile_nonce), flags=re.ASCII):
        raise ControllerError("APPDATA profile随机标识格式不正确")
    current_user_sid, _enabled_groups = _current_process_token_sids()
    if temporary_root is None:
        parent_path = _user_documents_profile_root(current_user_sid)
        profile_parent_source = "USER_DOCUMENTS"
    else:
        parent_path = _assert_path_chain(temporary_root, "directory")
        profile_parent_source = "EXPLICIT_TEST_ROOT"
    canonical_parent = str(Path(parent_path).resolve(strict=True))
    if os.path.normcase(os.path.normpath(parent_path)) != os.path.normcase(os.path.normpath(canonical_parent)):
        raise ControllerError("APPDATA profile父目录不是规范路径或含路径别名")
    parent_security_audit = _verify_private_profile_parent(parent_path, current_user_sid)
    if vendor_relative_files is None:
        vendor_relative_files = _vendor_tclstore_relative_files()
    run_id_digest = hashlib.sha256(str(run_id).encode("ascii")).hexdigest()[:8].upper()
    profile_id = f"{run_id_digest}_{profile_nonce}"
    profile_path = Path(parent_path) / f"s15_appdata_{profile_id}"
    path_audit = _private_appdata_path_length_audit(profile_path, vendor_relative_files)
    if _windows_path_utf16_chars(profile_path) > APPDATA_MAX_PATH_UTF16_CHARS:
        raise ControllerError("私有APPDATA profile根路径超过259字符，拒绝启动")
    if os.path.lexists(profile_path):
        raise ControllerError(f"拒绝复用已存在APPDATA profile路径：{str(profile_path)!r}")
    _create_private_profile_directory(profile_path, current_user_sid)
    profile_identity = None
    probe_path = profile_path / ".s15_write_delete_probe"
    probe_identity = None
    try:
        profile_identity = _path_file_identity(profile_path)
        _assert_path_chain(profile_path, "directory")
        canonical_profile = str(profile_path.resolve(strict=True))
        if os.path.normcase(os.path.normpath(str(profile_path))) != os.path.normcase(
            os.path.normpath(canonical_profile)
        ):
            raise ControllerError(f"新建APPDATA profile解析路径发生重定向：{str(profile_path)!r}")
        security_audit = _inspect_directory_security(
            profile_path, current_user_sid, require_private_dacl=True
        )
        if any(profile_path.iterdir()):
            raise ControllerError(f"新建APPDATA profile非空，拒绝复用：{str(profile_path)!r}")
        probe_handle = os.open(probe_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            probe_stat = os.fstat(probe_handle)
            probe_identity = (int(probe_stat.st_dev), int(probe_stat.st_ino))
        finally:
            os.close(probe_handle)
        _assert_path_chain(probe_path, "file")
        if _path_file_identity(probe_path) != probe_identity:
            raise ControllerError(f"APPDATA写删权限probe身份变化：{str(profile_path)!r}")
        probe_path.unlink()
        probe_identity = None
        if os.path.lexists(probe_path):
            raise ControllerError(f"APPDATA写删权限probe未能移除：{str(profile_path)!r}")
    except BaseException as error:
        try:
            _rollback_private_appdata_profile(
                profile_path,
                current_user_sid,
                profile_identity,
                probe_path,
                probe_identity,
            )
        except BaseException as rollback_error:
            raise ControllerError(
                f"APPDATA profile预检失败且无法证明安全回滚，保留路径：{str(profile_path)!r}; "
                f"failure={error!r}; rollback={rollback_error!r}"
            ) from rollback_error
        raise
    return str(profile_path), {
        "status": "PASS_PRIVATE_EMPTY_PROFILE",
        "run_id": str(run_id),
        "profile_id": profile_id,
        "path": str(profile_path),
        "profile_parent_source": profile_parent_source,
        "canonical_path": canonical_profile,
        "path_utf16_chars": _windows_path_utf16_chars(profile_path),
        "profile_parent_path": parent_path,
        "profile_parent_path_utf16_chars": _windows_path_utf16_chars(parent_path),
        "parent_security_audit": parent_security_audit,
        "profile_security_audit": security_audit,
        "retention_policy": "runner不会自动删除或复用profile",
        "write_delete_probe": "PASS_CREATED_AND_REMOVED_EMPTY_FILE",
        "path_length_audit": path_audit,
    }


def _child_environment(run_dir, temporary_root=None):
    """创建空私有APPDATA并原样保留显式许可变量或唯一默认许可证。"""
    _assert_path_chain(run_dir, "directory")
    source_appdata = os.environ.get("APPDATA")
    if not source_appdata:
        raise ControllerError("APPDATA未定义，拒绝启动Vivado批处理入口")
    license_audit = _audit_license_configuration(os.environ, source_appdata)
    if not license_audit["usable"]:
        raise ControllerError("创建隔离APPDATA前未找到非空显式许可变量或唯一可核验默认许可证文件")
    isolated_appdata, appdata_profile_audit = _create_private_appdata_profile(
        Path(run_dir).name, temporary_root=temporary_root
    )
    environment = dict(os.environ)
    for name in VIVADO_SETUP_ENVIRONMENT_VARIABLES:
        environment.pop(name, None)
    environment["APPDATA"] = isolated_appdata
    environment["RDI_VERBOSE"] = "False"
    for name in LICENSE_ENVIRONMENT_NAMES:
        if os.environ.get(name) is not None and environment.get(name) != os.environ[name]:
            raise ControllerError(f"显式许可变量未完整继承：{name}")
    if license_audit["default_license_used"]:
        environment["XILINXD_LICENSE_FILE"] = _resolve_single_default_license_path(source_appdata, license_audit)
    return environment, isolated_appdata, license_audit, appdata_profile_audit


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


def _lock_verified_toolchain(facts):
    """只读锁住cmd、Vivado批处理链及目标Vivado映像并复核预检哈希。"""
    locks = []
    locked_hashes = {}
    try:
        for name, record in facts["toolchain_files"].items():
            lock = InputReadLock(record["path"])
            locks.append(lock)
            digest = _sha256(record["path"])
            if digest != record["sha256"]:
                raise ControllerError(f"锁定后的工具链文件SHA256不符：{name}")
            locked_hashes[name] = digest
        return locks, locked_hashes
    except BaseException as primary:
        cleanup_errors = []
        for lock in reversed(locks):
            try:
                lock.close()
            except BaseException as error:
                cleanup_errors.append(repr(error))
        if cleanup_errors:
            raise ControllerError(f"工具链锁定失败且只读锁清理不闭合：primary={primary!r}; cleanup={cleanup_errors!r}") from primary
        raise


def _run_prelaunch_check(executable, argv, cwd, environment, std_handles, expected_sha256):
    """在独立Job中运行只读预检，并要求全部成员身份和自然退出闭合。"""
    executable = _assert_path_chain(executable, "file")
    before_sha256 = _sha256(executable)
    if before_sha256 != expected_sha256:
        raise ControllerError("预检可执行文件启动前SHA256不符")
    job = job_guard.JobObject(kill_on_close=True)
    child = None
    started = time.monotonic()
    try:
        child = job_guard.launch_suspended_root(
            job,
            executable,
            argv,
            cwd=cwd,
            std_handles=std_handles,
            environment=environment,
        )
        identity = dict(child.identity)
        events = list(child.events)
        closure = child.wait_and_close(timeout_seconds=30.0)
        child = None
        exit_code = closure["final"].get("root_native_handle_exit_code")
        after_sha256 = _sha256(executable)
        if after_sha256 != expected_sha256:
            raise ControllerError("预检可执行文件退出后SHA256不符")
        return {
            "status": "CLOSED",
            "executable_path": executable,
            "executable_sha256_before": before_sha256,
            "executable_sha256_after": after_sha256,
            "argv": list(argv),
            "working_directory": cwd,
            "stdio_policy": "shared run stdout.log/stderr.log handles",
            "root_identity": identity,
            "lifecycle_events": events,
            "job_closure": closure,
            "exit_code": exit_code,
            "duration_seconds": time.monotonic() - started,
        }
    except BaseException as error:
        cleanup = _kill_and_close(child, "HARD_STOP:REDIST_PREFLIGHT_CLOSURE") if child is not None else None
        if not job.closed:
            try:
                if not job.pid_list() and job.accounting()["active_processes"] == 0:
                    job.close()
            except BaseException:
                pass
        raise ControllerError(f"独立xvcredist预检未闭合：primary={error!r}; cleanup={cleanup!r}") from error


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
        inputs["vivado_batch_path"],
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


def _record_vivado_job_members(seen, sample, vivado_executable_path, monotonic_seconds):
    """只从已读回身份的Job成员中登记精确Vivado映像。"""
    expected = os.path.normcase(os.path.abspath(vivado_executable_path))
    for member in sample.get("member_measurements", []):
        identity = member.get("identity")
        if not isinstance(identity, dict) or not identity.get("exe"):
            continue
        actual = os.path.normcase(os.path.abspath(identity["exe"]))
        if actual != expected:
            continue
        key = (int(member["pid"]), int(member["birth_ticks"]))
        record = seen.get(key)
        if record is None:
            record = {
                "pid": key[0],
                "birth_ticks": key[1],
                "create_time": identity["create_time"],
                "exe": identity["exe"],
                "cmdline": identity["cmdline"],
                "first_observed_monotonic_seconds": monotonic_seconds,
                "last_observed_monotonic_seconds": monotonic_seconds,
            }
            seen[key] = record
        else:
            record["last_observed_monotonic_seconds"] = monotonic_seconds
    return [seen[key] for key in sorted(seen)]


def _vivado_member_closure(observations, closure):
    """将Vivado Job成员身份观察绑定到最终Job退出码读回。"""
    final_rows = closure.get("final", {}).get("member_readbacks", []) if isinstance(closure, dict) else []
    by_key = {
        (int(row.get("pid", -1)), int(row.get("birth_ticks", -1))): row
        for row in final_rows
        if isinstance(row, dict)
    }
    members = []
    for observation in observations:
        key = (int(observation["pid"]), int(observation["birth_ticks"]))
        final = by_key.get(key)
        members.append(
            {
                **observation,
                "final_status": final.get("status") if final else "NOT_IN_FINAL_JOB_CLOSURE",
                "native_exit_code": final.get("exit_code") if final else None,
            }
        )
    valid = bool(members) and all(
        row["final_status"] == "EXITED" and row["native_exit_code"] == 0 for row in members
    )
    return {"valid": valid, "observed_count": len(members), "members": members}


_TERMINAL_EXIT_SAMPLE_UNCERTAINTY = frozenset(
    {
        "PID_LIST_CHANGED_DURING_SAMPLE",
        "JOB_PROCESS_COUNTER_CHANGED_DURING_SAMPLE",
    }
)
_NO_SUCH_PROCESS_READBACK = re.compile(
    r"MEMBER_READBACK_FAILED:(?P<pid>[0-9]+):GateBlocked\(\"六字段无法读取："
    r"psutil\.NoSuchProcess\(pid=(?P=pid)"
    r"(?:, name='(?:[^'\\]|\\.)*')?"
    r", msg='(?:process PID not found|process no longer exists)'\)\"\)\Z",
    re.ASCII,
)


def _terminal_exit_sample_is_reconcilable(sample, alerts, previous_keys, previous_accounting, child):
    """仅接受由已知Job成员退出造成、且没有其他门禁告警的最后采样竞争。"""
    if alerts != ["SAMPLE_UNCERTAIN"]:
        return False, "sample alerts不是单独的SAMPLE_UNCERTAIN"
    if not isinstance(sample, dict):
        return False, "sample不是对象"
    uncertainty = sample.get("uncertainty")
    if not isinstance(uncertainty, list) or not uncertainty:
        return False, "sample缺少非空uncertainty列表"
    if any(not isinstance(item, str) for item in uncertainty):
        return False, "sample uncertainty包含非字符串项"
    known_keys = {(int(pid), int(ticks)) for pid, ticks in previous_keys}
    root_key = (int(child.pid), int(child.birth_ticks))
    if root_key not in known_keys:
        return False, "此前样本未观察到精确root身份"
    if len({pid for pid, _ticks in known_keys}) != len(known_keys):
        return False, "此前样本存在同PID多重创建时间，拒绝PID复用"
    tree_rss = sample.get("tree_rss_bytes")
    if type(tree_rss) is not int or tree_rss < 0:
        return False, "sample缺少有效tree RSS样本"
    if tree_rss > job_guard.RSS_LIMIT_BYTES:
        return False, "sample tree RSS超过6GiB门禁"

    readback_failure_pids = set()
    for item in uncertainty:
        if item in _TERMINAL_EXIT_SAMPLE_UNCERTAINTY:
            continue
        if isinstance(item, str) and item.startswith("MEMBER_READBACK_FAILED:"):
            match = _NO_SUCH_PROCESS_READBACK.fullmatch(item)
            if match is None:
                return False, "成员读回失败不是精确的psutil.NoSuchProcess"
            pid = int(match.group("pid"))
            if not any(known_pid == pid for known_pid, _ticks in known_keys):
                return False, f"成员读回失败涉及此前未观察PID：{pid}"
            if pid in readback_failure_pids:
                return False, f"成员读回失败重复记录PID：{pid}"
            readback_failure_pids.add(pid)
            continue
        return False, f"sample含有不允许的uncertainty：{item!r}"
    if not readback_failure_pids:
        return False, "sample没有已知成员读回失败，不能归因为退出竞争"

    pids_before = sample.get("job_pids_before")
    pids_after = sample.get("job_pids_after")
    if not isinstance(pids_before, list) or not isinstance(pids_after, list):
        return False, "sample缺少前后Job PID列表"
    if any(type(pid) is not int or pid <= 0 for pid in pids_before + pids_after):
        return False, "sample PID列表含有无效PID"
    before_set, after_set = set(pids_before), set(pids_after)
    if len(before_set) != len(pids_before) or len(after_set) != len(pids_after):
        return False, "sample PID列表含有重复PID"
    known_pids = {pid for pid, _ticks in known_keys}
    if not before_set.issubset(known_pids) or after_set:
        return False, "sample包含未跟踪PID或第二次PID读回仍非空"
    if not readback_failure_pids.issubset(before_set):
        return False, "成员读回失败PID不在该样本首次Job PID列表中"

    accounting_before = sample.get("accounting_before")
    accounting_after = sample.get("accounting_after")
    if not isinstance(accounting_before, dict) or not isinstance(accounting_after, dict):
        return False, "sample缺少前后Job accounting"
    required_counts = ("total_processes", "active_processes", "terminated_processes", "exited_processes")
    if any(type(row.get(key)) is not int or row[key] < 0 for row in (accounting_before, accounting_after) for key in required_counts):
        return False, "sample accounting计数缺失或无效"
    if (
        accounting_before["active_processes"] != len(before_set)
        or accounting_after["active_processes"] != 0
        or accounting_before["total_processes"] != accounting_after["total_processes"]
        or accounting_before["terminated_processes"] != accounting_after["terminated_processes"]
        or accounting_after["exited_processes"] != accounting_after["total_processes"]
    ):
        return False, "sample accounting变化不能证明仅有已知成员退出"
    uncertainties = set(uncertainty)
    if (before_set != after_set) != ("PID_LIST_CHANGED_DURING_SAMPLE" in uncertainties):
        return False, "PID列表变化与uncertainty记录不一致"
    accounting_changed = any(accounting_before[key] != accounting_after[key] for key in required_counts)
    if accounting_changed != ("JOB_PROCESS_COUNTER_CHANGED_DURING_SAMPLE" in uncertainties):
        return False, "Job计数变化与uncertainty记录不一致"

    if not isinstance(previous_accounting, dict):
        return False, "缺少前一稳定样本accounting"
    if any(type(previous_accounting.get(key)) is not int for key in ("total_processes", "exited_processes")):
        return False, "前一稳定样本accounting无效"
    current_keys = set()
    measurements = sample.get("member_measurements")
    if not isinstance(measurements, list):
        return False, "sample成员测量不是列表"
    for row in measurements:
        if (
            not isinstance(row, dict)
            or type(row.get("pid")) is not int
            or row["pid"] <= 0
            or type(row.get("birth_ticks")) is not int
            or row["birth_ticks"] < 0
        ):
            return False, "sample成员测量缺少精确进程身份"
        key = (row["pid"], row["birth_ticks"])
        if key not in known_keys or key in current_keys:
            return False, "sample出现未跟踪或重复的进程身份"
        current_keys.add(key)
    total_delta = accounting_after["total_processes"] - previous_accounting["total_processes"]
    exit_delta = accounting_after["exited_processes"] - previous_accounting["exited_processes"]
    new_seen = len(current_keys - known_keys)
    known_ended = len(known_keys - current_keys)
    if total_delta < 0 or total_delta != new_seen or exit_delta < 0 or exit_delta != known_ended:
        return False, "前后样本差额显示有未采样创建/退出或身份漂移"
    return True, "采样不确定性仅涉及已知Job成员退出"


def _stable_empty_job_readback(job):
    """连续两次读回Job空成员及稳定计数。"""
    first_pids = list(job.pid_list())
    first_accounting = dict(job.accounting())
    second_pids = list(job.pid_list())
    second_accounting = dict(job.accounting())
    stable_fields = ("total_processes", "active_processes", "terminated_processes", "exited_processes")
    if first_pids or second_pids or first_pids != second_pids:
        raise ControllerError("终态竞争收敛时Job PID列表非空或不稳定")
    if any(first_accounting.get(key) != second_accounting.get(key) for key in stable_fields):
        raise ControllerError("终态竞争收敛时Job计数第二次读回不稳定")
    if first_accounting.get("active_processes") != 0 or second_accounting.get("active_processes") != 0:
        raise ControllerError("终态竞争收敛时Job active_processes非零")
    return second_accounting


def _validate_terminal_job_closure(
    closure, child, expected_exit_code, stable_accounting, previous_keys, vivado_observations
):
    """核对wait_and_close返回的完整身份、退出码与已观察Vivado成员。"""
    if not isinstance(closure, dict) or not isinstance(closure.get("final"), dict):
        return False, "wait_and_close没有返回final closure"
    final = closure["final"]
    if (
        final.get("root_handle_signaled") is not True
        or final.get("root_native_handle_pid") != int(child.pid)
        or final.get("root_native_handle_birth_ticks") != int(child.birth_ticks)
    ):
        return False, "final closure没有证明精确root句柄已signal"
    root_exit_code = final.get("root_native_handle_exit_code")
    if type(root_exit_code) is not int or root_exit_code == job_guard.STILL_ACTIVE or root_exit_code != expected_exit_code:
        return False, "final closure的root原生退出码缺失、仍活动或不一致"
    if final.get("job_pids") != [] or final.get("active_processes") != 0:
        return False, "final closure的Job仍有活动成员"
    total = final.get("total_processes")
    readbacks = final.get("member_readbacks")
    if type(total) is not int or total < 1 or not isinstance(readbacks, list) or len(readbacks) != total:
        return False, "final closure身份读回数量与Job total_processes不一致"
    if (
        total != stable_accounting.get("total_processes")
        or final.get("exited_processes") != total
        or final.get("total_terminated_processes") != 0
        or stable_accounting.get("terminated_processes") != 0
        or final.get("unknown_members") != []
        or final.get("live_members") != []
    ):
        return False, "final closure含terminated、alive、unknown或计数不一致"
    keys = set()
    for row in readbacks:
        if not isinstance(row, dict) or type(row.get("pid")) is not int or type(row.get("birth_ticks")) is not int:
            return False, "final closure成员缺少精确身份"
        key = (row["pid"], row["birth_ticks"])
        if key in keys or row.get("status") != "EXITED" or type(row.get("exit_code")) is not int or row["exit_code"] == job_guard.STILL_ACTIVE:
            return False, "final closure成员重复、未退出或退出码无效"
        keys.add(key)
    if (int(child.pid), int(child.birth_ticks)) not in keys:
        return False, "final closure没有root精确身份"
    if not {(int(pid), int(ticks)) for pid, ticks in previous_keys}.issubset(keys):
        return False, "final closure缺少此前样本观察到的Job成员身份"
    root_member = next(
        row for row in readbacks
        if (row["pid"], row["birth_ticks"]) == (int(child.pid), int(child.birth_ticks))
    )
    if root_member["exit_code"] != root_exit_code:
        return False, "root Job成员句柄退出码与CreateProcessW原生句柄不一致"
    observed_vivado_keys = {
        (int(row["pid"]), int(row["birth_ticks"]))
        for row in vivado_observations
    }
    if not observed_vivado_keys.issubset(keys):
        return False, "final closure缺少此前观察到的Vivado成员"
    return True, "root、Job全成员与Vivado观察身份均已闭合"


def _reconcile_terminal_exit_race(
    job,
    child,
    sample,
    alerts,
    previous_keys,
    previous_accounting,
    root_wait,
    root_exit_code,
    vivado_observations,
):
    """仅在严格终态闭合证明成立时，收敛退出沿的最后一次采样不确定性。"""
    result = {
        "reconciled": False,
        "reason": None,
        "closure": None,
        "closed": False,
        "closure_error": False,
        "job_final_readback": None,
    }
    if root_wait != job_guard.WAIT_OBJECT_0 or type(root_exit_code) is not int or root_exit_code == job_guard.STILL_ACTIVE:
        result["reason"] = "root原生句柄仍活动或等待状态未知"
        return result
    valid_sample, reason = _terminal_exit_sample_is_reconcilable(
        sample, alerts, previous_keys, previous_accounting, child
    )
    if not valid_sample:
        result["reason"] = reason
        return result
    try:
        result["job_final_readback"] = _stable_empty_job_readback(job)
        sample_accounting = sample["accounting_after"]
        stable_fields = ("total_processes", "active_processes", "terminated_processes", "exited_processes")
        if any(sample_accounting.get(key) != result["job_final_readback"].get(key) for key in stable_fields):
            result["reason"] = "sample终态计数与Job稳定第二次读回不一致"
            return result
        closure = child.wait_and_close(timeout_seconds=30.0)
        result["closure"] = closure
        result["closed"] = bool(getattr(child, "closed", False))
    except BaseException as error:
        result["reason"] = f"终态Job/成员闭合失败：{error!r}"
        result["closed"] = bool(getattr(child, "closed", False))
        result["closure_error"] = True
        return result
    valid_closure, reason = _validate_terminal_job_closure(
        closure,
        child,
        root_exit_code,
        result["job_final_readback"],
        previous_keys,
        vivado_observations,
    )
    result["reconciled"] = valid_closure
    result["reason"] = reason
    return result


def _terminal_exit_race_runner_transition(alerts, reconciliation):
    """为监护循环确定终态分支，只有完整已关闭结果才跳过硬停清理。"""
    if (
        isinstance(reconciliation, dict)
        and reconciliation.get("reconciled") is True
        and reconciliation.get("closed") is True
        and reconciliation.get("closure") is not None
    ):
        return {
            "reconciled": True,
            "release_child": True,
            "closure": reconciliation["closure"],
            "stop_reason": None,
        }
    reason = reconciliation.get("reason") if isinstance(reconciliation, dict) else None
    stop_reason = "HARD_STOP:" + ",".join(alerts)
    if reason:
        stop_reason += ":TERMINAL_EXIT_RECONCILIATION_REJECTED:" + reason
    return {
        "reconciled": False,
        "release_child": (
            isinstance(reconciliation, dict)
            and reconciliation.get("closed") is True
            and reconciliation.get("closure_error") is not True
        ),
        "closure": reconciliation.get("closure") if isinstance(reconciliation, dict) else None,
        "stop_reason": stop_reason,
    }


def _resolve_terminal_exit_race_for_runner(
    job,
    child,
    sample,
    alerts,
    previous_keys,
    previous_accounting,
    root_wait,
    root_exit_code,
    vivado_observations,
):
    """执行生产runner使用的退出沿收敛、闭合分支及必要清理。"""
    try:
        reconciliation = _reconcile_terminal_exit_race(
            job,
            child,
            sample,
            alerts,
            previous_keys,
            previous_accounting,
            root_wait,
            root_exit_code,
            vivado_observations,
        )
    except BaseException as error:
        reconciliation = {
            "reconciled": False,
            "reason": f"终态退出竞争处理异常：{error!r}",
            "closure": None,
            "closed": bool(getattr(child, "closed", False)),
            "closure_error": True,
            "job_final_readback": None,
        }
    transition = _terminal_exit_race_runner_transition(alerts, reconciliation)
    result = {
        "reconciliation": reconciliation,
        "transition": transition,
        "child": child,
        "closure": None,
        "native_root_exit_code": None,
        "cleanup_record": None,
    }
    if transition["reconciled"]:
        result["closure"] = transition["closure"]
        result["child"] = None
        return result
    if transition["release_child"]:
        result["closure"] = transition["closure"]
        result["child"] = None
        return result
    if child is not None:
        cleanup_record = _kill_and_close(child, transition["stop_reason"])
        result["cleanup_record"] = cleanup_record
        result["closure"] = cleanup_record.get("closure")
        result["native_root_exit_code"] = cleanup_record.get("root_native_exit_code")
        result["child"] = None
    return result


def _ensure_native_exit_diagnostic(closure, native_root_exit_code, stop_reason):
    """闭合后的非零root退出码始终保留为失败诊断。"""
    if closure is None or native_root_exit_code in (None, 0):
        return stop_reason
    diagnostic = f"NATIVE_CMD_ROOT_EXIT_NONZERO_{native_root_exit_code}"
    if not stop_reason:
        return diagnostic
    if diagnostic not in stop_reason:
        return f"{stop_reason}:{diagnostic}"
    return stop_reason


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
    manifest["native_cmd_root_exit_code"] = result_code
    launch = manifest["process_launch"]
    launch["native_cmd_root_exit_code"] = result_code
    manifest["job_final_closure"] = closure
    manifest["resource_peaks_and_floors"] = peaks
    vivado_closure = _vivado_member_closure(launch.get("vivado_member_observations", []), closure)
    launch["vivado_member_closure"] = vivado_closure
    manifest["native_vivado_exit_codes"] = [row["native_exit_code"] for row in vivado_closure["members"]]
    if not vivado_closure["valid"] and not stop_reason:
        stop_reason = "TARGET_VIVADO_NOT_OBSERVED_AS_CLOSED_ZERO_EXIT_JOB_MEMBER"
    manifest["stop_reason"] = stop_reason
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
        and vivado_closure["valid"]
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
        "toolchain_file_sha256": {
            name: _sha256_if_present(record["path"])
            for name, record in input_facts["toolchain_files"].items()
        },
        "controller_source_sha256": _sha256_if_present(input_facts["controller_source_path"]),
    }
    manifest["input_hashes_match_preflight"] = (
        manifest["input_hashes_after_run"]["frozen_dcp_original_sha256"] == input_facts["dcp_sha256"]
        and manifest["input_hashes_after_run"]["frozen_dcp_copy_sha256"] == input_facts["dcp_sha256"]
        and manifest["input_hashes_after_run"]["tcl_source_original_sha256"] == input_facts["tcl_source_sha256"]
        and manifest["input_hashes_after_run"]["tcl_source_copy_sha256"] == input_facts["tcl_source_sha256"]
        and manifest["input_hashes_after_run"]["vivado_executable_sha256"] == input_facts["vivado_executable_sha256"]
        and all(
            manifest["input_hashes_after_run"]["toolchain_file_sha256"].get(name) == record["sha256"]
            for name, record in input_facts["toolchain_files"].items()
        )
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
        manifest["stop_reason"] = "原始/Run输入、cmd/Vivado批处理链、Vivado映像或控制器运行后SHA256变化"
    elif manifest["status"] == "BITGEN_COMPLETE_SOFTWARE_ONLY" and not bit_length_matches:
        manifest["status"] = "FAILED_OR_INCOMPLETE"
        manifest["stop_reason"] = "bitstream大小与Tcl完成回执不一致"
    writer.write()
    return manifest


def _finish_controller_cleanup(writer, manifest, input_locks, run_exit_code, toolchain_locks=()):
    """释放输入只读锁并持久化最终清单，任何收尾失败都返回非零。"""
    lock_close_errors = []
    for input_lock in reversed(input_locks):
        try:
            input_lock.close()
        except BaseException as lock_error:
            lock_close_errors.append(repr(lock_error))
    toolchain_lock_errors = []
    for toolchain_lock in reversed(toolchain_locks):
        try:
            toolchain_lock.close()
        except BaseException as lock_error:
            toolchain_lock_errors.append(repr(lock_error))
    manifest["input_copy_locks_released_utc"] = _utc_now() if not lock_close_errors else None
    manifest["input_copy_lock_release_errors"] = lock_close_errors
    manifest["toolchain_read_locks_released_utc"] = _utc_now() if not toolchain_lock_errors else None
    manifest["toolchain_read_lock_release_errors"] = toolchain_lock_errors
    if lock_close_errors or toolchain_lock_errors:
        manifest["status"] = "FAILED_OR_INCOMPLETE"
        prior_reason = manifest.get("stop_reason") or ""
        manifest["stop_reason"] = ";".join(
            part
            for part in (
                prior_reason,
                "INPUT_COPY_LOCK_RELEASE_FAILED" if lock_close_errors else None,
                "TOOLCHAIN_READ_LOCK_RELEASE_FAILED" if toolchain_lock_errors else None,
            )
            if part
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
    batch_argv, output_paths = _expected_argv(run_dir, facts)
    argv, cmd_command = _build_cmd_batch_argv(
        facts["cmd_executable_path"], facts["vivado_batch_path"], batch_argv[1:]
    )
    manifest = {
        "schema": "s15-direct-frozen-dcp-bitgen/2.0.0",
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
            "toolchain_files": facts["toolchain_files"],
            "vivado_batch_call_chain": facts["batch_call_chain"],
            "vivado_expected_version": facts["vivado_expected_version"],
            "vivado_actual_version": None,
            "tcl_source_path": facts["tcl_source_path"],
            "tcl_source_sha256": facts["tcl_source_sha256"],
            "tcl_run_copy_path": facts["tcl_copy_path"],
            "tcl_run_copy_sha256": None,
            "controller_source_path": facts["controller_source_path"],
            "controller_source_sha256": facts["controller_source_sha256"],
            "evidence_root": facts["evidence_root"],
            "redist_resolution_guard": facts["redist_resolution_guard"],
            "xvcredist_link_resolution": facts["xvcredist_link_resolution"],
            "vivado_setup_environment_guard": facts["vivado_setup_environment_guard"],
            "evidence_root_override_environment": EVIDENCE_ROOT_ENV,
            "vivado_install_init_candidates_absent": facts["vivado_install_init_candidates_absent"],
            "user_init_script_audit": facts["user_init_script_audit"],
            "parent_appdata_isolated": facts["parent_appdata_isolated"],
            "license_environment_audit": facts["license_environment_audit"],
        },
        "input_run_copies": [],
        "input_copy_locks_released_utc": None,
        "input_copy_lock_release_errors": [],
        "toolchain_read_locks_released_utc": None,
        "toolchain_read_lock_release_errors": [],
        "expected_part": EXPECTED_PART,
        "process_launch": {
            "api": "Win32 CreateProcessW(CREATE_SUSPENDED) cmd.exe /D /S /V:OFF /C call vivado.bat; AssignProcessToJobObject, identity/member closure, ResumeThread",
            "root_process_role": "cmd.exe batch environment root",
            "cmd_executable_path": facts["cmd_executable_path"],
            "vivado_batch_path": facts["vivado_batch_path"],
            "vivado_target_executable_path": facts["vivado_executable_path"],
            "cmd_auto_run_disabled": True,
            "rdi_verbose_forced_off": True,
            "batch_command": cmd_command,
            "batch_argv": batch_argv,
            "argv": argv,
            "windows_command_line": job_guard.subprocess.list2cmdline(argv),
            "working_directory": facts["vivado_working_directory"],
            "loader_redist_precheck": None,
            "environment_overrides": [],
            "isolated_appdata_path": None,
            "private_appdata_profile": None,
            "root_identity": None,
            "vivado_member_observations": [],
            "vivado_member_closure": None,
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
        "native_cmd_root_exit_code": None,
        "native_vivado_exit_codes": [],
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
    toolchain_locks = []
    vivado_member_observations = {}
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
        toolchain_locks, locked_toolchain_hashes = _lock_verified_toolchain(facts)
        manifest["input_paths_and_hashes"]["frozen_dcp_run_copy_sha256"] = facts["locked_copy_hashes"]["dcp_copy_sha256"]
        manifest["input_paths_and_hashes"]["tcl_run_copy_sha256"] = facts["locked_copy_hashes"]["tcl_copy_sha256"]
        manifest["input_paths_and_hashes"]["toolchain_locked_sha256"] = locked_toolchain_hashes
        manifest["input_run_copies"] = facts["run_input_copies"]
        writer.write()
        std_handles, std_streams = _open_stdio_handles(run_dir)
        child_environment, isolated_appdata, license_audit, appdata_profile_audit = _child_environment(run_dir)
        manifest["process_launch"]["isolated_appdata_path"] = isolated_appdata
        manifest["process_launch"]["private_appdata_profile"] = appdata_profile_audit
        manifest["input_paths_and_hashes"]["license_environment_audit"] = license_audit
        redist_environment = dict(child_environment)
        redist_environment.pop(REDIST_CHECK_SKIP_ENV, None)
        manifest["process_launch"]["loader_redist_precheck"] = {
            "status": "RUNNING",
            "source": {
                "loader_path": facts["toolchain_files"]["loader.bat"]["path"],
                "loader_sha256": facts["toolchain_files"]["loader.bat"]["sha256"],
                "xvcredist_link_resolution": facts["xvcredist_link_resolution"],
                "rdiArgs_path": facts["toolchain_files"]["rdiArgs.bat"]["path"],
                "rdiArgs_sha256": facts["toolchain_files"]["rdiArgs.bat"]["sha256"],
                "call_chain": facts["batch_call_chain"],
            },
            "skip_environment_variable": REDIST_CHECK_SKIP_ENV,
            "skip_environment_variable_absent_during_check": True,
        }
        writer.write()
        redist_check = _run_prelaunch_check(
            facts["xvcredist_executable_path"],
            [facts["xvcredist_executable_path"], "-check"],
            str(Path(facts["xvcredist_executable_path"]).parent),
            redist_environment,
            std_handles,
            facts["xvcredist_executable_sha256"],
        )
        redist_check.update(
            {
                key: value
                for key, value in manifest["process_launch"]["loader_redist_precheck"].items()
                if key != "status"
            }
        )
        manifest["process_launch"]["loader_redist_precheck"] = redist_check
        writer.write()
        if redist_check["exit_code"] != 0:
            raise ControllerError(f"独立xvcredist -check退出码不是0：{redist_check['exit_code']!r}")
        child_environment[REDIST_CHECK_SKIP_ENV] = "1"
        manifest["process_launch"]["environment_overrides"].append(
            {
                "name": REDIST_CHECK_SKIP_ENV,
                "value": "1",
                "reason": "同Run独立xvcredist.exe -check已受控退出0，loader内重复调用会创建未采样短命成员",
                "precheck_executable_path": redist_check["executable_path"],
                "precheck_executable_sha256": redist_check["executable_sha256_after"],
                "precheck_exit_code": redist_check["exit_code"],
            }
        )
        writer.write()
        manifest["input_paths_and_hashes"]["xvcredist_link_resolution"]["pre_bitgen_recheck"] = (
            _recheck_xvcredist_link_before_bitgen(facts)
        )
        writer.write()
        job = job_guard.JobObject(kill_on_close=True)
        if job.flags != job_guard.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE:
            raise ControllerError(f"新JobObject限制标志不符：0x{job.flags:08x}")
        manifest["start_utc"] = _utc_now()
        manifest["start_monotonic_seconds"] = time.monotonic()
        manifest["status"] = "CREATE_SUSPENDED"
        writer.write()
        child = job_guard.launch_suspended_root(
            job,
            facts["cmd_executable_path"],
            argv,
            cwd=facts["vivado_working_directory"],
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
            sample_previous_accounting = previous_accounting
            sample_previous_keys = set(previous_keys)
            sample = job.sample(
                previous_sample_start=previous_sample_start,
                previous_accounting=sample_previous_accounting,
                previous_pids=previous_pids,
                previous_keys=sample_previous_keys,
            )
            manifest["process_launch"]["vivado_member_observations"] = _record_vivado_job_members(
                vivado_member_observations,
                sample,
                facts["vivado_executable_path"],
                time.monotonic(),
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
            if alerts:
                terminal_result = _resolve_terminal_exit_race_for_runner(
                    job,
                    child,
                    sample,
                    alerts,
                    sample_previous_keys,
                    sample_previous_accounting,
                    root_wait,
                    native_root_exit_code,
                    [
                        vivado_member_observations[key]
                        for key in sorted(vivado_member_observations)
                    ],
                )
                reconciliation = terminal_result["reconciliation"]
                transition = terminal_result["transition"]
                if terminal_result["closure"] is not None:
                    closure = terminal_result["closure"]
                if terminal_result["native_root_exit_code"] is not None:
                    native_root_exit_code = terminal_result["native_root_exit_code"]
                if terminal_result["cleanup_record"] is not None:
                    cleanup_record = terminal_result["cleanup_record"]
                child = terminal_result["child"]
                sample_record["terminal_exit_race_reconciliation"] = {
                    "reconciled": reconciliation["reconciled"],
                    "reason": reconciliation["reason"],
                    "job_final_readback": reconciliation["job_final_readback"],
                    "closure": reconciliation["closure"],
                    "hard_stop_cleanup": terminal_result["cleanup_record"],
                }
                if transition["reconciled"]:
                    closure = transition["closure"]
                    _append_monitor(
                        monitor_path,
                        {
                            "utc": _utc_now(),
                            "monotonic_seconds": time.monotonic(),
                            "event": "TERMINAL_EXIT_SAMPLE_RACE_RECONCILED",
                            "alerts": alerts,
                            "reason": reconciliation["reason"],
                            "job_final_readback": reconciliation["job_final_readback"],
                            "closure": reconciliation["closure"],
                        },
                    )
                    break
                if transition["release_child"] and terminal_result["closure"] is None:
                    closure = transition["closure"]
                stop_reason = transition["stop_reason"]
                break
            current_pids = job.pid_list()
            current_accounting = job.accounting()
            if root_wait == job_guard.WAIT_OBJECT_0 and not current_pids and current_accounting["active_processes"] == 0:
                closure = child.wait_and_close(timeout_seconds=30.0)
                child = None
                break
            next_sample = time.monotonic() + SAMPLE_INTERVAL_SECONDS
        stop_reason = _ensure_native_exit_diagnostic(closure, native_root_exit_code, stop_reason)
        manifest["resource_peaks_and_floors"] = peaks
        manifest["stop_reason"] = stop_reason
        if stop_reason:
            event = "HARD_STOP" if stop_reason.startswith("HARD_STOP:") else "STOP"
            _append_monitor(monitor_path, {"utc": _utc_now(), "monotonic_seconds": time.monotonic(), "event": event, "reason": stop_reason})
            if child is not None:
                cleanup_record = _kill_and_close(child, stop_reason)
                child = None
            if cleanup_record is not None:
                closure = cleanup_record.get("closure")
                native_root_exit_code = cleanup_record.get("root_native_exit_code")
            manifest["hard_stop_cleanup"] = cleanup_record
        if closure is not None and native_root_exit_code is None:
            native_root_exit_code = closure["final"].get("root_native_handle_exit_code")
        manifest["process_launch"]["vivado_member_observations"] = [
            vivado_member_observations[key] for key in sorted(vivado_member_observations)
        ]
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
        stop_reason = _record_controller_exception(manifest, error)
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
        run_exit_code = _finish_controller_cleanup(
            writer,
            manifest,
            input_locks,
            run_exit_code,
            toolchain_locks,
        )
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
