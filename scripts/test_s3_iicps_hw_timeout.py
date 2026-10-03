#!/usr/bin/env python3
"""验证 Vitis 2026.1 IICPS 接收 TO overlay 及真实提取函数的主机行为。"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "board/stage3/software/sensor/iicps_v3_23_hw_timeout.patch"
RUN_ROOT = ROOT / "tmp/s3_iicps_timeout"
BASELINE_COMMIT = "cd484f986e307500305f3db5c5f2f28e67d6126f"
SOURCE_SPECS = {
    "xiicps_master.c": (
        Path(r"D:\Xilinx\2026.1\Vitis\data\embeddedsw\XilinxProcessorIPLib\drivers\iicps_v3_23\src\xiicps_master.c"),
        "6e002edfd94b80b0dfdd54215c0a536e5fbe06380d7a40f0418b6e52066e3b10",
    ),
    "xiicps_xfer.c": (
        Path(r"D:\Xilinx\2026.1\Vitis\data\embeddedsw\XilinxProcessorIPLib\drivers\iicps_v3_23\src\xiicps_xfer.c"),
        "628414e27016be423ca950af493d522556587e4e04f1eef0e1ce7b10ecffbc1f",
    ),
    "xiicps.h": (
        Path(r"D:\Xilinx\2026.1\Vitis\data\embeddedsw\XilinxProcessorIPLib\drivers\iicps_v3_23\src\xiicps.h"),
        "a96553e979223be1828a781f1bdeb818c61db661e154337b8cf3b4bf10b500ca",
    ),
    "xiicps_hw.h": (
        Path(r"D:\Xilinx\2026.1\Vitis\data\embeddedsw\XilinxProcessorIPLib\drivers\iicps_v3_23\src\xiicps_hw.h"),
        "0013bcfc147a4c7fc1e60bba7368b5742b638661afb7fdf7efb8dab3223b3d9a",
    ),
}
PATCH_TARGETS = {"src/xiicps_master.c", "src/xiicps_xfer.c"}


class ValidationError(RuntimeError):
    """表示任务基线或源码契约验证失败。"""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def function_text(source: str, prefix: str) -> str:
    """从 C 源码提取一个完整函数，忽略注释和字面量中的花括号。"""
    start = source.find(prefix)
    if start < 0:
        raise ValidationError(f"找不到函数定义：{prefix}")
    brace = source.find("{", start)
    if brace < 0:
        raise ValidationError(f"函数没有函数体：{prefix}")
    depth = 0
    state = "code"
    index = brace
    while index < len(source):
        char = source[index]
        following = source[index + 1] if index + 1 < len(source) else ""
        if state == "code":
            if char == "/" and following == "*":
                state = "block"
                index += 2
                continue
            if char == "/" and following == "/":
                state = "line"
                index += 2
                continue
            if char == '"':
                state = "string"
            elif char == "'":
                state = "character"
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return source[start : index + 1]
        elif state == "block" and char == "*" and following == "/":
            state = "code"
            index += 2
            continue
        elif state == "line" and char == "\n":
            state = "code"
        elif state in ("string", "character"):
            if char == "\\":
                index += 2
                continue
            if (state == "string" and char == '"') or (
                state == "character" and char == "'"
            ):
                state = "code"
        index += 1
    raise ValidationError(f"函数花括号不匹配：{prefix}")


def outside_function(source: str, prefix: str) -> str:
    body = function_text(source, prefix)
    return source.replace(body, "<FUNCTION>", 1)


def check_contract(master_before: str, xfer_before: str,
                   master_after: str, xfer_after: str,
                   patch_text: str) -> list[str]:
    targets = set()
    for line in patch_text.splitlines():
        match = re.fullmatch(r"diff --git a/(\S+) b/(\S+)", line)
        if match:
            if match.group(1) != match.group(2):
                raise ValidationError(f"overlay 不允许重命名：{line}")
            targets.add(match.group(1))
    if targets != PATCH_TARGETS:
        raise ValidationError(f"overlay 修改范围不符：{sorted(targets)}")

    recv_prefix = "s32 XIicPs_MasterRecvPolled("
    read_prefix = "void XIicPs_MasterPolledRead("
    if outside_function(master_before, recv_prefix) != outside_function(master_after, recv_prefix):
        raise ValidationError("master.c 在 MasterRecvPolled 以外存在改动")
    if outside_function(xfer_before, read_prefix) != outside_function(xfer_after, read_prefix):
        raise ValidationError("xfer.c 在 MasterPolledRead 以外存在改动")
    send_prefix = "s32 XIicPs_MasterSendPolled("
    if function_text(master_before, send_prefix) != function_text(master_after, send_prefix):
        raise ValidationError("MasterSendPolled 发送路径发生变化")

    read_fn = function_text(xfer_after, read_prefix)
    recv_fn = function_text(master_after, recv_prefix)
    if not re.search(r"ErrorMask\s*=.*?XIICPS_IXR_TO_MASK", read_fn, re.S):
        raise ValidationError("MasterPolledRead 错误掩码未包含硬件 TO")
    if not re.search(
        r"XIicPs_MasterRead\(InstancePtr, IsHold, &ByteCountVar\);\s*"
        r"IntrStatusReg\s*=\s*XIicPs_ReadReg\(BaseAddr,\s*XIICPS_ISR_OFFSET\);\s*"
        r"if\s*\(\(IntrStatusReg\s*&\s*ErrorMask\)\s*!=\s*0U\)\s*\{\s*break;",
        read_fn,
    ):
        raise ValidationError("FIFO 服务之后未重读 ISR 并退出错误轮询")
    wait_start = read_fn.find("while (XIicPs_RxFIFOFull(")
    wait_end = read_fn.find("if ((InstancePtr->RecvByteCount - XIICPS_FIFO_DEPTH)", wait_start)
    if wait_start < 0 or wait_end < 0:
        raise ValidationError("缺少 Zynq FIFO-full 等待或后续长度写入位置")
    wait_block = read_fn[wait_start:wait_end]
    if "IntrStatusReg = XIicPs_ReadReg(BaseAddr," not in wait_block:
        raise ValidationError("FIFO-full 内层等待未轮询 ISR")
    if "(IntrStatusReg & ErrorMask) != 0U" not in wait_block:
        raise ValidationError("FIFO-full 内层等待未响应已置位错误/TO")
    if not re.search(
        r"IntrStatusReg\s*=\s*XIicPs_ReadReg\(BaseAddr,\s*XIICPS_ISR_OFFSET\);\s*"
        r"if\s*\(\(IntrStatusReg\s*&\s*ErrorMask\)\s*!=\s*0U\)\s*\{\s*return;",
        wait_block,
    ):
        raise ValidationError("FIFO-full 等待返回前缺少最终 ISR 检查")
    if not re.search(
        r"XIICPS_IXR_NACK_MASK\s*\|\s*\(u32\)XIICPS_IXR_TO_MASK", recv_fn
    ):
        raise ValidationError("MasterRecvPolled 最终错误掩码未包含 TO")
    if "XIICPS_IXR_ARB_LOST_MASK" not in recv_fn or "XST_IIC_ARB_LOST" not in recv_fn:
        raise ValidationError("仲裁丢失的既有返回语义未保留")
    if "(IntrStatusReg & Intrs) != 0U" not in recv_fn or "Result = (s32)XST_FAILURE" not in recv_fn:
        raise ValidationError("TO/NACK 等非仲裁错误未映射为 XST_FAILURE")

    return [
        "补丁仅修改两个目标 C 文件中的指定接收函数，发送函数与函数外文本不变",
        "FIFO 服务后重新读取 ISR，已置位错误终止普通轮询",
        "Zynq FIFO-full 内层持续检查错误，错误返回前不写下一段传输长度",
        "最终掩码包含 TO；NACK 返回 XST_FAILURE、仲裁丢失返回码保持不变",
    ]


HOST_PREAMBLE = r'''#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uintptr_t UINTPTR;
typedef int32_t s32;

#define XIICPS_ADDR_OFFSET 0x08U
#define XIICPS_ISR_OFFSET 0x10U
#define XIICPS_TRANS_SIZE_OFFSET 0x14U
#define XIICPS_IXR_ARB_LOST_MASK 0x00000200U
#define XIICPS_IXR_RX_UNF_MASK 0x00000080U
#define XIICPS_IXR_RX_OVR_MASK 0x00000020U
#define XIICPS_IXR_TO_MASK 0x00000008U
#define XIICPS_IXR_NACK_MASK 0x00000004U
#define XIICPS_IXR_COMP_MASK 0x00000001U
#define XIICPS_FIFO_DEPTH 16
#define XIICPS_MAX_TRANSFER_SIZE 252U
#define XPLAT_ZYNQ 1U

typedef struct {
    struct { UINTPTR BaseAddress; } Config;
    s32 RecvByteCount;
    s32 UpdateTxSize;
} XIicPs;

enum { CASE_MID_READ_TO = 1, CASE_FIFO_WAIT_TO, CASE_NORMAL_COMPLETE };

static int active_case;
static u32 mock_isr;
static u32 mock_addr;
static u32 mock_transfer_size;
static u32 platform_info;
static unsigned master_read_calls;
static unsigned fifo_full_polls;
static unsigned isr_reads;
static unsigned isr_reads_after_to;
static unsigned transfer_size_writes;

static u32 XIicPs_ReadReg(UINTPTR base, u32 offset);
static void XIicPs_WriteReg(UINTPTR base, u32 offset, u32 value);
static u32 XGetPlatform_Info(void);
static void XIicPs_MasterRead(XIicPs *instance, s32 hold, s32 *byte_count);
static u32 XIicPs_RxFIFOFull(XIicPs *instance, s32 byte_count);
'''

HOST_DRIVER = r'''
static u32 XIicPs_ReadReg(UINTPTR base, u32 offset)
{
    (void)base;
    if (offset == XIICPS_ISR_OFFSET) {
        isr_reads++;
        if ((mock_isr & XIICPS_IXR_TO_MASK) != 0U) isr_reads_after_to++;
        return mock_isr;
    }
    if (offset == XIICPS_ADDR_OFFSET) return mock_addr;
    if (offset == XIICPS_TRANS_SIZE_OFFSET) return mock_transfer_size;
    return 0U;
}

static void XIicPs_WriteReg(UINTPTR base, u32 offset, u32 value)
{
    (void)base;
    if (offset == XIICPS_ISR_OFFSET) mock_isr &= ~value;
    else if (offset == XIICPS_ADDR_OFFSET) mock_addr = value;
    else if (offset == XIICPS_TRANS_SIZE_OFFSET) {
        mock_transfer_size = value;
        transfer_size_writes++;
    }
}

static u32 XGetPlatform_Info(void)
{
    return platform_info;
}

static void XIicPs_MasterRead(XIicPs *instance, s32 hold, s32 *byte_count)
{
    (void)hold;
    (void)byte_count;
    master_read_calls++;
    if (active_case == CASE_MID_READ_TO) {
        if (master_read_calls == 1U) instance->RecvByteCount--;
        else if (master_read_calls == 2U) mock_isr |= XIICPS_IXR_TO_MASK;
    } else if (active_case == CASE_NORMAL_COMPLETE) {
        instance->RecvByteCount = 0;
        mock_isr |= XIICPS_IXR_COMP_MASK;
    }
}

static u32 XIicPs_RxFIFOFull(XIicPs *instance, s32 byte_count)
{
    (void)instance;
    (void)byte_count;
    fifo_full_polls++;
    if (active_case == CASE_FIFO_WAIT_TO) {
        if (fifo_full_polls == 2U) mock_isr |= XIICPS_IXR_TO_MASK;
        return 1U;
    }
    return 0U;
}
'''

HOST_MAIN = r'''
static int run_case(const char *name, int case_id, u32 platform, s32 recv_count,
                    s32 update_size, s32 byte_count, unsigned expected_reads,
                    unsigned expected_fifo_polls, unsigned expected_isr_reads,
                    unsigned expected_reads_after_to, unsigned expected_size_writes,
                    int expect_to, int expect_complete)
{
    XIicPs instance = {0};
    int saw_to;
    int saw_complete;
    active_case = case_id;
    mock_isr = 0U;
    mock_addr = 0x21U;
    mock_transfer_size = 252U;
    platform_info = platform;
    master_read_calls = 0U;
    fifo_full_polls = 0U;
    isr_reads = 0U;
    isr_reads_after_to = 0U;
    transfer_size_writes = 0U;
    instance.Config.BaseAddress = 0U;
    instance.RecvByteCount = recv_count;
    instance.UpdateTxSize = update_size;
    XIicPs_MasterPolledRead(&instance, 0, byte_count);
    saw_to = (mock_isr & XIICPS_IXR_TO_MASK) != 0U;
    saw_complete = (mock_isr & XIICPS_IXR_COMP_MASK) != 0U;
    if (master_read_calls != expected_reads ||
        fifo_full_polls != expected_fifo_polls ||
        isr_reads != expected_isr_reads ||
        isr_reads_after_to != expected_reads_after_to ||
        transfer_size_writes != expected_size_writes ||
        saw_to != expect_to || saw_complete != expect_complete) {
        fprintf(stderr,
                "FAIL %s master_read_calls=%u fifo_full_polls=%u isr_reads=%u isr_reads_after_to=%u transfer_size_writes=%u to=%d complete=%d\n",
                name, master_read_calls, fifo_full_polls, isr_reads,
                isr_reads_after_to, transfer_size_writes, saw_to, saw_complete);
        return 1;
    }
    printf("SCENARIO %s PASS master_read_calls=%u fifo_full_polls=%u isr_reads=%u isr_reads_after_to=%u transfer_size_writes=%u\n",
           name, master_read_calls, fifo_full_polls, isr_reads,
           isr_reads_after_to, transfer_size_writes);
    return 0;
}

int main(void)
{
    int failures = 0;
    failures += run_case("mid_read_to", CASE_MID_READ_TO, 0U, 4, 0, 4,
                         2U, 0U, 4U, 1U, 0U, 1, 0);
    failures += run_case("fifo_wait_delayed_to", CASE_FIFO_WAIT_TO, XPLAT_ZYNQ,
                         300, 1, XIICPS_FIFO_DEPTH + 1, 1U, 2U, 4U, 1U,
                         0U, 1, 0);
    failures += run_case("normal_completion_control", CASE_NORMAL_COMPLETE,
                         0U, 1, 0, 1, 1U, 0U, 3U, 0U, 0U, 0, 1);
    if (failures != 0) return EXIT_FAILURE;
    puts("RESULT: 3/3 host behavior scenarios passed");
    return EXIT_SUCCESS;
}
'''


def build_host_harness(read_function: str) -> str:
    return "\n".join((HOST_PREAMBLE, read_function, HOST_DRIVER, HOST_MAIN))


def run_host_harness(read_function: str, run_dir: Path) -> tuple[dict, int]:
    harness_path = run_dir / "iicps_timeout_host_harness.c"
    harness_path.write_text(build_host_harness(read_function), encoding="utf-8", newline="\n")
    gcc = shutil.which("gcc")
    if gcc is None:
        return ({
            "status": "NOT_RUN_GCC_UNAVAILABLE",
            "compiler": None,
            "compile_command": None,
            "compile_return_code": None,
            "runtime_command": None,
            "runtime_return_code": None,
            "runtime_timed_out": False,
            "scenarios": [],
        }, 2)

    version = subprocess.run([gcc, "--version"], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", check=True).stdout.splitlines()[0]
    executable = run_dir / ("iicps_timeout_host_harness.exe" if sys.platform == "win32"
                            else "iicps_timeout_host_harness")
    compile_command = [gcc, "-std=c99", "-Wall", "-Wextra", "-Werror", "-O0",
                       str(harness_path), "-o", str(executable)]
    compile_result = subprocess.run(compile_command, cwd=run_dir, capture_output=True,
                                    text=True, encoding="utf-8", errors="replace", timeout=30)
    (run_dir / "compile_stdout.txt").write_text(compile_result.stdout, encoding="utf-8")
    (run_dir / "compile_stderr.txt").write_text(compile_result.stderr, encoding="utf-8")
    result = {
        "status": "COMPILE_FAILED" if compile_result.returncode != 0 else "COMPILED",
        "compiler": version,
        "compile_command": compile_command,
        "compile_return_code": compile_result.returncode,
        "compile_stdout": compile_result.stdout,
        "compile_stderr": compile_result.stderr,
        "runtime_command": None,
        "runtime_return_code": None,
        "runtime_timed_out": False,
        "runtime_timeout_seconds": 10,
        "runtime_duration_seconds": None,
        "runtime_stdout": "",
        "runtime_stderr": "",
        "scenarios": [],
    }
    if compile_result.returncode != 0:
        return result, 1

    runtime_command = [str(executable)]
    start_time = time.perf_counter()
    try:
        runtime = subprocess.run(runtime_command, cwd=run_dir, capture_output=True, text=True,
                                 encoding="utf-8", errors="replace", timeout=10)
    except subprocess.TimeoutExpired as error:
        result.update({
            "status": "RUNTIME_TIMEOUT",
            "runtime_command": runtime_command,
            "runtime_timed_out": True,
            "runtime_duration_seconds": round(time.perf_counter() - start_time, 6),
            "runtime_stdout": error.stdout or "",
            "runtime_stderr": error.stderr or "",
        })
        (run_dir / "runtime_stdout.txt").write_text(str(result["runtime_stdout"]), encoding="utf-8")
        (run_dir / "runtime_stderr.txt").write_text(str(result["runtime_stderr"]), encoding="utf-8")
        return result, 1

    (run_dir / "runtime_stdout.txt").write_text(runtime.stdout, encoding="utf-8")
    (run_dir / "runtime_stderr.txt").write_text(runtime.stderr, encoding="utf-8")
    scenario_pattern = re.compile(
        r"^SCENARIO (\S+) PASS master_read_calls=(\d+) fifo_full_polls=(\d+) "
        r"isr_reads=(\d+) isr_reads_after_to=(\d+) transfer_size_writes=(\d+)$"
    )
    scenarios = []
    for line in runtime.stdout.splitlines():
        match = scenario_pattern.fullmatch(line)
        if match:
            scenarios.append({
                "name": match.group(1),
                "master_read_calls": int(match.group(2)),
                "fifo_full_polls": int(match.group(3)),
                "isr_reads": int(match.group(4)),
                "isr_reads_after_to": int(match.group(5)),
                "transfer_size_writes": int(match.group(6)),
            })
    passed = runtime.returncode == 0 and len(scenarios) == 3 and \
        "RESULT: 3/3 host behavior scenarios passed" in runtime.stdout
    result.update({
        "status": "PASS" if passed else "RUNTIME_FAILED",
        "runtime_command": runtime_command,
        "runtime_return_code": runtime.returncode,
        "runtime_duration_seconds": round(time.perf_counter() - start_time, 6),
        "runtime_stdout": runtime.stdout,
        "runtime_stderr": runtime.stderr,
        "scenarios": scenarios,
    })
    return result, 0 if passed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-name", required=True, help="tmp 下新的唯一证据目录名")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", args.run_name):
        raise ValidationError("run-name 只能包含 ASCII 字母、数字、下划线和连字符")
    if not PATCH.is_file():
        raise ValidationError(f"overlay 文件不存在：{PATCH}")

    baseline_reachable = subprocess.run(
        ["git", "merge-base", "--is-ancestor", BASELINE_COMMIT, "HEAD"], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8"
    )
    if baseline_reachable.returncode != 0:
        raise ValidationError(
            f"仓库 HEAD 不包含固定基线提交 {BASELINE_COMMIT}；拒绝混用其他工程基线"
        )
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
        capture_output=True, text=True, encoding="utf-8"
    ).stdout.strip()

    originals: dict[str, bytes] = {}
    before_hashes: dict[str, str] = {}
    for name, (source_path, expected_hash) in SOURCE_SPECS.items():
        if not source_path.is_file():
            raise ValidationError(f"厂商原件不存在：{source_path}")
        data = source_path.read_bytes()
        actual_hash = sha256(data)
        if actual_hash != expected_hash:
            raise ValidationError(
                f"原件 SHA-256 不匹配；未应用补丁：{source_path}\n"
                f"actual={actual_hash}\nexpected={expected_hash}"
            )
        originals[name] = data
        before_hashes[name] = actual_hash

    run_dir = RUN_ROOT / args.run_name
    if run_dir.exists():
        raise ValidationError(f"证据目录已存在，拒绝覆盖：{run_dir}")
    baseline_dir = run_dir / "baseline"
    source_dir = run_dir / "src"
    baseline_dir.mkdir(parents=True)
    source_dir.mkdir()
    for name, data in originals.items():
        (baseline_dir / name).write_bytes(data)
        if name != "xiicps.h":
            (source_dir / name).write_bytes(data)

    patch_text = PATCH.read_text(encoding="utf-8")
    git = shutil_which_git()
    patch_prefix = run_dir.relative_to(ROOT).as_posix()
    check = subprocess.run(
        [git, "apply", "--check", "-p1", f"--directory={patch_prefix}", str(PATCH)], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8"
    )
    if check.returncode != 0:
        raise ValidationError("git apply --check 失败：" + check.stdout + check.stderr)
    apply = subprocess.run(
        [git, "apply", "-p1", f"--directory={patch_prefix}", str(PATCH)], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8"
    )
    if apply.returncode != 0:
        raise ValidationError("git apply 失败：" + apply.stdout + apply.stderr)

    before_master = (baseline_dir / "xiicps_master.c").read_text(encoding="utf-8")
    before_xfer = (baseline_dir / "xiicps_xfer.c").read_text(encoding="utf-8")
    after_master = (source_dir / "xiicps_master.c").read_text(encoding="utf-8")
    after_xfer = (source_dir / "xiicps_xfer.c").read_text(encoding="utf-8")
    checks = check_contract(before_master, before_xfer, after_master, after_xfer, patch_text)
    after_hashes = {
        name: sha256((source_dir / name).read_bytes())
        for name in ("xiicps_master.c", "xiicps_xfer.c")
    }
    diff_lines: list[str] = []
    for name in ("xiicps_xfer.c", "xiicps_master.c"):
        diff_lines.extend(difflib.unified_diff(
            (baseline_dir / name).read_text(encoding="utf-8").splitlines(True),
            (source_dir / name).read_text(encoding="utf-8").splitlines(True),
            fromfile=f"a/src/{name}", tofile=f"b/src/{name}"
        ))
    diff_path = run_dir / "applied_overlay.diff"
    diff_path.write_text("".join(diff_lines), encoding="utf-8", newline="\n")

    read_function = function_text(after_xfer, "void XIicPs_MasterPolledRead(")
    function_line = after_xfer[:after_xfer.find(read_function)].count("\n") + 1
    host_harness, harness_exit = run_host_harness(read_function, run_dir)

    summary = {
        "task_id": "S3-SW02-IICPS-HW-TO-02",
        "baseline_commit": head,
        "vendor_source_before_sha256": before_hashes,
        "overlay_patch": str(PATCH.relative_to(ROOT)),
        "overlay_patch_sha256": sha256(PATCH.read_bytes()),
        "overlay_source_after_sha256": after_hashes,
        "source_contract_checks": checks,
        "executed_function": {
            "symbol": "XIicPs_MasterPolledRead",
            "source_copy": str((source_dir / "xiicps_xfer.c").relative_to(ROOT)),
            "source_line": function_line,
            "extracted_function_sha256": sha256(read_function.encode("utf-8")),
            "method": "从固定散列原件应用冻结补丁后按函数边界提取真实函数体，并原样编译进 harness.c；驱动控制逻辑未手工重写。",
        },
        "host_harness": host_harness,
        "patch_check_exit_code": check.returncode,
        "patch_apply_exit_code": apply.returncode,
        "limitations": [
            "host harness 执行真实 XIicPs_MasterPolledRead 函数体；XIicPs_MasterRead 字节服务、寄存器/MMIO、ISR、FIFO-full及平台查询由mock提供。",
            "不证明 Vitis/BSP 构建、真实 MMIO/FIFO 时序、Timeout 寄存器配置或板上行为。",
        ],
        "evidence": [
            str(diff_path.relative_to(ROOT)),
            str((source_dir / "xiicps_master.c").relative_to(ROOT)),
            str((source_dir / "xiicps_xfer.c").relative_to(ROOT)),
            str((run_dir / "iicps_timeout_host_harness.c").relative_to(ROOT)),
            str((run_dir / "runtime_stdout.txt").relative_to(ROOT)),
        ],
    }
    summary_path = run_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
    print("PASS baseline commit and four original driver-file SHA-256 values")
    print(f"PASS overlay replay: {summary['overlay_patch_sha256']}")
    for check_text in checks:
        print(f"PASS source contract: {check_text}")
    print(f"HOST HARNESS: {host_harness['status']}")
    if host_harness.get("compile_return_code") is not None:
        print(f"COMPILE_EXIT_CODE: {host_harness['compile_return_code']}")
    if host_harness.get("runtime_return_code") is not None:
        print(f"RUNTIME_EXIT_CODE: {host_harness['runtime_return_code']}")
    if host_harness.get("runtime_stdout"):
        print(host_harness["runtime_stdout"], end="")
    print("LIMITATION: mocks cover MMIO/FIFO dependencies; no Vitis/BSP or hardware validation")
    print(f"EVIDENCE: {summary_path.relative_to(ROOT)}")
    return harness_exit


def shutil_which_git() -> str:
    import shutil

    git = shutil.which("git")
    if git is None:
        raise ValidationError("git 命令不可用，无法应用 unified diff")
    return git


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValidationError, subprocess.CalledProcessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
