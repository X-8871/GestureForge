#!/usr/bin/env python3
"""重放 IICPS 两层超时 overlay，并运行真实接收函数体的主机 mock。"""

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
HARDWARE_PATCH = ROOT / "board/stage3/software/sensor/iicps_v3_23_hw_timeout.patch"
SOFTWARE_PATCH = ROOT / "board/stage3/software/sensor/iicps_v3_23_sw_deadline.patch"
RUN_ROOT = ROOT / "tmp/s3_iicps_sw_timeout"
BASELINE_COMMIT = "806331d6e6193b539dea76058ad38e5bf71d2d70"
HARDWARE_PATCH_SHA256 = "73083bc57385e8aeabf659db69a1a7c017db2021d5d24e0eeb8dfbdbda77f859"
VENDOR_SRC = Path(
    r"D:\Xilinx\2026.1\Vitis\data\embeddedsw\XilinxProcessorIPLib\drivers\iicps_v3_23\src"
)
SOURCE_SPECS = {
    "xiicps_master.c": "6e002edfd94b80b0dfdd54215c0a536e5fbe06380d7a40f0418b6e52066e3b10",
    "xiicps_xfer.c": "628414e27016be423ca950af493d522556587e4e04f1eef0e1ce7b10ecffbc1f",
    "xiicps_xfer.h": "94a72a32a8c1e1a18a0506c998de88c69e9e1cb612da483cec91bccc7ef64a0b",
    "xiicps.c": "c60c4afda63d4b6dbe09066ac67ad2883aae04f81d637b38ccd7c0b7f70b58b3",
    "xiicps.h": "a96553e979223be1828a781f1bdeb818c61db661e154337b8cf3b4bf10b500ca",
    "xiicps_hw.h": "0013bcfc147a4c7fc1e60bba7368b5742b638661afb7fdf7efb8dab3223b3d9a",
}
HARDWARE_TARGETS = {"src/xiicps_master.c", "src/xiicps_xfer.c"}
SOFTWARE_TARGETS = {
    "src/xiicps_master.c",
    "src/xiicps_xfer.c",
    "src/xiicps_xfer.h",
}


class ValidationError(RuntimeError):
    """表示基线、补丁重放或行为契约不符合要求。"""


def sha256(data: bytes) -> str:
    """计算字节内容的 SHA-256。"""
    return hashlib.sha256(data).hexdigest()


def function_text(source: str, prefix: str) -> str:
    """从 C 源码中抽取完整函数体，忽略注释和字面量中的花括号。"""
    start = source.find(prefix)
    if start < 0:
        raise ValidationError(f"找不到函数定义：{prefix}")
    brace = source.find("{", start)
    if brace < 0:
        raise ValidationError(f"函数没有函数体：{prefix}")
    depth = 0
    index = brace
    state = "code"
    while index < len(source):
        char = source[index]
        next_char = source[index + 1] if index + 1 < len(source) else ""
        if state == "code":
            if char == "/" and next_char == "*":
                state = "block_comment"
                index += 2
                continue
            if char == "/" and next_char == "/":
                state = "line_comment"
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
        elif state == "block_comment":
            if char == "*" and next_char == "/":
                state = "code"
                index += 2
                continue
        elif state == "line_comment":
            if char == "\n":
                state = "code"
        elif state in {"string", "character"}:
            if char == "\\":
                index += 2
                continue
            if (state == "string" and char == '"') or (
                state == "character" and char == "'"
            ):
                state = "code"
        index += 1
    raise ValidationError(f"函数花括号不匹配：{prefix}")


def without_function(source: str, prefix: str) -> str:
    """移除指定函数，便于确认补丁没有触及其他函数。"""
    function = function_text(source, prefix)
    return source.replace(function, "", 1)


def patch_targets(patch_text: str) -> set[str]:
    """读取 unified diff 的目标文件集合。"""
    targets: set[str] = set()
    for line in patch_text.splitlines():
        match = re.fullmatch(r"diff --git a/(\S+) b/(\S+)", line)
        if match:
            if match.group(1) != match.group(2):
                raise ValidationError(f"补丁不允许重命名：{line}")
            targets.add(match.group(1))
    return targets


def verify_vendor_hashes(snapshot: dict[str, bytes]) -> dict[str, str]:
    """对固定 Vitis 原件逐文件校验，返回通过的摘要。"""
    if set(snapshot) != set(SOURCE_SPECS):
        raise ValidationError("固定厂商源码集合不匹配")
    actual_hashes: dict[str, str] = {}
    for name, expected in SOURCE_SPECS.items():
        actual = sha256(snapshot[name])
        if actual != expected:
            raise ValidationError(
                f"拒绝变化的 Vitis 原件：{name} actual={actual} expected={expected}"
            )
        actual_hashes[name] = actual
    return actual_hashes


def verify_vendor_api_inventory() -> dict[str, int]:
    """核对固定 Vitis 源目录中轮询读 API 的声明、调用和定义数量。"""
    expression = re.compile(rb"\bXIicPs_MasterPolledRead\s*\(")
    occurrences: dict[str, int] = {}
    source_files = sorted(
        path for path in VENDOR_SRC.rglob("*")
        if path.is_file() and path.suffix.lower() in {".c", ".h"}
    )
    if not source_files:
        raise ValidationError("固定 Vitis 源目录中没有 C/H 源文件")
    for path in source_files:
        matches = len(expression.findall(path.read_bytes()))
        if matches:
            occurrences[path.relative_to(VENDOR_SRC).as_posix()] = matches
    expected = {
        "xiicps_master.c": 1,
        "xiicps_xfer.c": 1,
        "xiicps_xfer.h": 1,
    }
    if occurrences != expected:
        raise ValidationError(
            f"固定 Vitis 源目录 API 声明/调用/定义清单不匹配：{occurrences}"
        )
    return occurrences


def verify_source_contract(
    original: dict[str, str],
    hardware: dict[str, str],
    software: dict[str, str],
    hardware_text: str,
    software_text: str,
) -> list[str]:
    """核对补丁范围、轮询边界、返回码及 Abort 语义。"""
    if patch_targets(hardware_text) != HARDWARE_TARGETS:
        raise ValidationError("既有硬件 TO overlay 的文件范围发生变化")
    if patch_targets(software_text) != SOFTWARE_TARGETS:
        raise ValidationError("软件 deadline overlay 文件范围不符合任务边界")

    read_prefix = "s32 XIicPs_MasterPolledRead("
    recv_prefix = "s32 XIicPs_MasterRecvPolled("
    send_prefix = "s32 XIicPs_MasterSendPolled("
    read_original = function_text(original["xiicps_xfer.c"], "void XIicPs_MasterPolledRead(")
    read_hardware = function_text(hardware["xiicps_xfer.c"], "void XIicPs_MasterPolledRead(")
    read_software = function_text(software["xiicps_xfer.c"], read_prefix)
    recv_hardware = function_text(hardware["xiicps_master.c"], recv_prefix)
    recv_software = function_text(software["xiicps_master.c"], recv_prefix)
    send_original = function_text(original["xiicps_master.c"], send_prefix)
    send_software = function_text(software["xiicps_master.c"], send_prefix)

    if original["xiicps_master.c"].count("XIicPs_MasterPolledRead(") != 1:
        raise ValidationError("固定 master.c 不是唯一的一处轮询读调用点")
    if send_original != send_software:
        raise ValidationError("发送路径被软件 deadline overlay 改动")
    if "#include \"xstatus.h\"" not in original["xiicps.h"]:
        raise ValidationError("XIicPs 公共头没有引入标准状态码头文件")
    if not re.search(
        r"\(u32\)XIICPS_CR_RESET_VALUE\s*\|\s*\(u32\)XIICPS_CR_CLR_FIFO_MASK",
        original["xiicps.c"],
    ):
        raise ValidationError("固定版本 XIicPs_Abort 未验证为复位控制寄存器并清 FIFO")
    if "#define XIICPS_CR_RESET_VALUE\t\t\t\t 0U" not in original["xiicps_hw.h"]:
        if not re.search(r"#define\s+XIICPS_CR_RESET_VALUE\s+0U", original["xiicps_hw.h"]):
            raise ValidationError("固定版本控制寄存器复位值不是已核对的 0")
    if "s32 XIicPs_MasterPolledRead(" not in software["xiicps_xfer.h"]:
        raise ValidationError("内部轮询读 API 没有返回状态码")
    if "void XIicPs_MasterPolledRead(" in software["xiicps_xfer.h"]:
        raise ValidationError("内部轮询读 API 仍声明为 void")
    if not re.search(
        r"#ifndef\s+XIICPS_RX_MAX_LOOPCNT\s*"
        r"/\*[^\n]*软件轮询上限[^\n]*不是硬实时期限[^\n]*\*/\s*"
        r"#define\s+XIICPS_RX_MAX_LOOPCNT\s+1000000U\s*#endif",
        software["xiicps_xfer.c"],
    ):
        raise ValidationError("生产默认软件轮询上限不是可覆盖的 1,000,000")
    if read_software.count("usleep(1U)") < 2:
        raise ValidationError("普通轮询和 Zynq FIFO-full 内循环未分别延时计数")
    if read_software.count("return (s32)XST_TIMEOUT;") != 2:
        raise ValidationError("普通轮询与 FIFO-full 路径应各自返回软件超时")
    if "XIICPS_IXR_TO_MASK" not in read_hardware or "XIICPS_IXR_TO_MASK" not in recv_hardware:
        raise ValidationError("先行硬件 TO overlay 没有完整保留")
    if "XIicPs_Abort(InstancePtr);" not in recv_software:
        raise ValidationError("MasterRecvPolled 超时分支未调用 XIicPs_Abort")
    if not re.search(
        r"else\s+if\s*\(ReadStatus\s*==\s*\(s32\)XST_TIMEOUT\)\s*\{.*?"
        r"XIicPs_Abort\(InstancePtr\);\s*"
        r"InstancePtr->UpdateTxSize\s*=\s*0;\s*"
        r"Result\s*=\s*\(s32\)XST_TIMEOUT;",
        recv_software,
        re.S,
    ):
        raise ValidationError("纯软件超时必须 Abort 后只复位分段标志 UpdateTxSize")
    if len(re.findall(r"InstancePtr->UpdateTxSize\s*=\s*0;", recv_software)) != 1:
        raise ValidationError("超时分支之外不得新增 UpdateTxSize 清理")
    timeout_branch = re.search(
        r"else\s+if\s*\(ReadStatus\s*==\s*\(s32\)XST_TIMEOUT\)\s*\{(?P<body>[^{}]*)\}",
        recv_software,
        re.S,
    )
    if timeout_branch is None:
        raise ValidationError("找不到纯软件超时分支以核对实例字段改动范围")
    timeout_instance_writes = re.findall(
        r"InstancePtr->([A-Za-z_]\w*)\s*=", timeout_branch.group("body")
    )
    if timeout_instance_writes != ["UpdateTxSize"]:
        raise ValidationError(
            f"超时分支只能复位 UpdateTxSize，不得清理其他实例字段：{timeout_instance_writes}"
        )
    if not re.search(
        r"if\s*\(\(IntrStatusReg\s*&\s*Intrs\)\s*!=\s*0U\)\s*\{\s*"
        r"if\s*\(\(IntrStatusReg\s*&\s*XIICPS_IXR_ARB_LOST_MASK\)\s*!=\s*0U\)\s*\{"
        r"\s*Result\s*=\s*\(s32\)\s*XST_IIC_ARB_LOST;.*?"
        r"\}\s*else\s*\{\s*Result\s*=\s*\(s32\)XST_FAILURE;\s*\}\s*\}"
        r"\s*else\s+if\s*\(ReadStatus\s*==\s*\(s32\)XST_TIMEOUT\)",
        recv_software,
        re.S,
    ):
        raise ValidationError("硬件仲裁丢失/错误没有优先于软件超时映射")
    if without_function(hardware["xiicps_master.c"], recv_prefix) != without_function(
        software["xiicps_master.c"], recv_prefix
    ):
        raise ValidationError("MasterRecvPolled 以外的 master.c 内容被软件 overlay 改动")
    if software["xiicps_xfer.h"].replace(
        "s32 XIicPs_MasterPolledRead(", "void XIicPs_MasterPolledRead(", 1
    ) != hardware["xiicps_xfer.h"]:
        raise ValidationError("xiicps_xfer.h 除轮询读返回类型外还有其他改动")

    xfer_hardware_rest = without_function(hardware["xiicps_xfer.c"], "void XIicPs_MasterPolledRead(")
    xfer_software_rest = without_function(software["xiicps_xfer.c"], read_prefix)
    xfer_software_rest = xfer_software_rest.replace('#include "sleep.h"\n', "", 1)
    xfer_software_rest = xfer_software_rest.replace(
        "* @return       XST_TIMEOUT 表示软件轮询到达上限；否则返回 XST_SUCCESS。",
        "* @return       None.",
        1,
    )
    xfer_software_rest = re.sub(
        r"#ifndef XIICPS_RX_MAX_LOOPCNT\n"
        r"/\*[^\n]*\*/\n"
        r"#define XIICPS_RX_MAX_LOOPCNT 1000000U\n"
        r"#endif\n",
        "",
        xfer_software_rest,
    )
    if xfer_hardware_rest != xfer_software_rest:
        raise ValidationError("MasterPolledRead 以外的 xfer.c 内容被软件 overlay 改动")

    return [
        "固定 Vitis 源目录仅有一处 MasterPolledRead 调用，状态返回可局部传播",
        "1,000,000 次 usleep(1) 是可编译期缩小的软件轮询界限，不作硬实时承诺",
        "硬件 TO/NACK 仍走 XST_FAILURE，仲裁丢失优先返回 XST_IIC_ARB_LOST",
        "纯软件超时由 MasterRecvPolled 调用 Abort；Abort 清控制寄存器、FIFO 与 ISR",
        "纯软件超时 Abort 后仅清 UpdateTxSize，保留其余实例软件状态",
        "发送函数体与成功路径保持既有逻辑",
    ]


HOST_PREAMBLE = r'''#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uintptr_t UINTPTR;
typedef int32_t s32;

#define XST_SUCCESS 0L
#define XST_FAILURE 1L
#define XST_IIC_ARB_LOST 71L
#define XST_TIMEOUT 73L
#define XIL_COMPONENT_IS_READY 1U
#define XIICPS_ADDR_MASK 0x3FFU
#define XIICPS_ADDR_OFFSET 0x08U
#define XIICPS_CR_OFFSET 0x00U
#define XIICPS_ISR_OFFSET 0x10U
#define XIICPS_TRANS_SIZE_OFFSET 0x14U
#define XIICPS_CR_CLR_FIFO_MASK 0x00000040U
#define XIICPS_CR_RESET_VALUE 0U
#define XIICPS_IXR_ARB_LOST_MASK 0x00000200U
#define XIICPS_IXR_RX_UNF_MASK 0x00000080U
#define XIICPS_IXR_RX_OVR_MASK 0x00000020U
#define XIICPS_IXR_TO_MASK 0x00000008U
#define XIICPS_IXR_NACK_MASK 0x00000004U
#define XIICPS_IXR_COMP_MASK 0x00000001U
#define XIICPS_CR_HOLD_MASK 0x00000010U
#define XIICPS_FIFO_DEPTH 16
#define XIICPS_MAX_TRANSFER_SIZE 252U
#define XPLAT_ZYNQ 1U
#define RECVING_ROLE 1

typedef struct {
    struct { UINTPTR BaseAddress; } Config;
    u32 IsReady;
    s32 IsRepeatedStart;
    u8 *RecvBufferPtr;
    s32 RecvByteCount;
    s32 UpdateTxSize;
} XIicPs;

enum {
    CASE_SUCCESS = 1,
    CASE_NACK,
    CASE_HARDWARE_TO,
    CASE_ARB_LOST,
    CASE_ORDINARY_TIMEOUT,
    CASE_ZYNQ_FIFO_TIMEOUT
};

static int active_case;
static u32 active_platform;
static u32 mock_isr;
static u32 mock_addr;
static u32 mock_cr;
static u32 mock_transfer_size;
static u32 transfer_size_values[8];
static unsigned master_read_calls;
static unsigned fifo_full_calls;
static unsigned isr_reads;
static unsigned transfer_size_writes;
static unsigned abort_calls;
static unsigned abort_cr_reset_seen;
static u32 abort_cr_write_value;
static s32 abort_update_tx_size_seen;
static unsigned sleep_calls;
static unsigned bad_sleep_delay;

static u32 XIicPs_ReadReg(UINTPTR base, u32 offset);
static void XIicPs_WriteReg(UINTPTR base, u32 offset, u32 value);
static u32 XGetPlatform_Info(void);
static void XIicPs_MasterRead(XIicPs *instance, s32 hold, s32 *byte_count);
static u32 XIicPs_RxFIFOFull(XIicPs *instance, s32 byte_count);
static s32 XIicPs_SetupMaster(XIicPs *instance, s32 role);
static void XIicPs_Abort(XIicPs *instance);
static void usleep(unsigned long usec);
s32 XIicPs_MasterPolledRead(XIicPs *instance, s32 hold, s32 byte_count);

#define Xil_AssertNonvoid(expression) \
    do { if (!(expression)) return (s32)XST_FAILURE; } while (0)
'''


HOST_DRIVER = r'''static u32 XIicPs_ReadReg(UINTPTR base, u32 offset)
{
    (void)base;
    if (offset == XIICPS_ISR_OFFSET) {
        isr_reads++;
        return mock_isr;
    }
    if (offset == XIICPS_ADDR_OFFSET) return mock_addr;
    if (offset == XIICPS_CR_OFFSET) return mock_cr;
    if (offset == XIICPS_TRANS_SIZE_OFFSET) return mock_transfer_size;
    return 0U;
}

static void XIicPs_WriteReg(UINTPTR base, u32 offset, u32 value)
{
    (void)base;
    if (offset == XIICPS_ISR_OFFSET) mock_isr &= ~value;
    else if (offset == XIICPS_ADDR_OFFSET) mock_addr = value;
    else if (offset == XIICPS_CR_OFFSET) mock_cr = value;
    else if (offset == XIICPS_TRANS_SIZE_OFFSET) {
        if (transfer_size_writes < 8U) {
            transfer_size_values[transfer_size_writes] = value;
        }
        mock_transfer_size = value;
        transfer_size_writes++;
    }
}

static u32 XGetPlatform_Info(void)
{
    return active_platform;
}

static void XIicPs_MasterRead(XIicPs *instance, s32 hold, s32 *byte_count)
{
    (void)hold;
    master_read_calls++;
    if (active_case == CASE_SUCCESS) {
        instance->RecvByteCount = 0;
        mock_isr |= XIICPS_IXR_COMP_MASK;
    } else if (active_case == CASE_NACK) {
        mock_isr |= XIICPS_IXR_NACK_MASK;
    } else if (active_case == CASE_HARDWARE_TO) {
        mock_isr |= XIICPS_IXR_TO_MASK;
    } else if (active_case == CASE_ARB_LOST) {
        mock_isr |= XIICPS_IXR_ARB_LOST_MASK;
    } else if (active_case == CASE_ZYNQ_FIFO_TIMEOUT) {
        *byte_count = XIICPS_FIFO_DEPTH + 1;
    }
}

static u32 XIicPs_RxFIFOFull(XIicPs *instance, s32 byte_count)
{
    (void)instance;
    (void)byte_count;
    fifo_full_calls++;
    return active_case == CASE_ZYNQ_FIFO_TIMEOUT ? 1U : 0U;
}

static s32 XIicPs_SetupMaster(XIicPs *instance, s32 role)
{
    (void)instance;
    (void)role;
    return (s32)XST_SUCCESS;
}

static void XIicPs_Abort(XIicPs *instance)
{
    abort_calls++;
    abort_update_tx_size_seen = instance->UpdateTxSize;
    abort_cr_write_value = (u32)XIICPS_CR_RESET_VALUE |
                           (u32)XIICPS_CR_CLR_FIFO_MASK;
    mock_cr = (u32)XIICPS_CR_RESET_VALUE;
    mock_isr = 0U;
    abort_cr_reset_seen = (abort_cr_write_value ==
                           ((u32)XIICPS_CR_RESET_VALUE |
                            (u32)XIICPS_CR_CLR_FIFO_MASK)) &&
                          (mock_cr == (u32)XIICPS_CR_RESET_VALUE) &&
                          ((mock_cr & (u32)XIICPS_CR_HOLD_MASK) == 0U);
}

static void usleep(unsigned long usec)
{
    sleep_calls++;
    if (usec != 1UL) bad_sleep_delay++;
}
'''


HOST_MAIN = r'''static void reset_mocks(int scenario, u32 platform)
{
    unsigned index;
    active_case = scenario;
    active_platform = platform;
    mock_isr = 0U;
    mock_addr = 0x21U;
    mock_cr = 0U;
    mock_transfer_size = 0U;
    for (index = 0U; index < 8U; index++) transfer_size_values[index] = 0U;
    master_read_calls = 0U;
    fifo_full_calls = 0U;
    isr_reads = 0U;
    transfer_size_writes = 0U;
    abort_calls = 0U;
    abort_cr_reset_seen = 0U;
    abort_cr_write_value = 0U;
    abort_update_tx_size_seen = 0;
    sleep_calls = 0U;
    bad_sleep_delay = 0U;
}

static int run_case(const char *name, int scenario, u32 platform, s32 bytes,
                    s32 repeated_start, s32 expected_status,
                    unsigned expected_abort, unsigned expected_transfer_writes,
                    unsigned expected_fifo_calls, unsigned expected_sleep_calls,
                    u32 expected_isr)
{
    XIicPs instance = {0};
    u8 receive_buffer[300] = {0};
    s32 status;
    reset_mocks(scenario, platform);
    instance.Config.BaseAddress = 0U;
    instance.IsReady = XIL_COMPONENT_IS_READY;
    instance.IsRepeatedStart = repeated_start;
    status = XIicPs_MasterRecvPolled(&instance, receive_buffer, bytes, 0x21U);
    if (status != expected_status || abort_calls != expected_abort ||
        transfer_size_writes != expected_transfer_writes ||
        fifo_full_calls != expected_fifo_calls || sleep_calls != expected_sleep_calls ||
        bad_sleep_delay != 0U || mock_isr != expected_isr ||
        (expected_abort != 0U && abort_cr_reset_seen == 0U)) {
        fprintf(stderr,
                "FAIL %s status=%d abort=%u xfer_size_writes=%u fifo=%u sleep=%u bad_delay=%u isr=0x%08x cr=0x%08x\n",
                name, status, abort_calls, transfer_size_writes, fifo_full_calls,
                sleep_calls, bad_sleep_delay, mock_isr, mock_cr);
        return 1;
    }
    printf("CASE %s PASS status=%d abort=%u xfer_size_writes=%u fifo=%u sleep=%u cr=0x%08x\n",
           name, status, abort_calls, transfer_size_writes, fifo_full_calls,
           sleep_calls, mock_cr);
    return 0;
}

static int run_reuse_after_long_timeout(void)
{
    XIicPs instance = {0};
    u8 long_buffer[300] = {0};
    u8 short_buffer[XIICPS_FIFO_DEPTH + 1U] = {0};
    s32 long_status;
    s32 short_status;

    reset_mocks(CASE_ZYNQ_FIFO_TIMEOUT, XPLAT_ZYNQ);
    instance.Config.BaseAddress = 0U;
    instance.IsReady = XIL_COMPONENT_IS_READY;
    instance.IsRepeatedStart = 0;
    long_status = XIicPs_MasterRecvPolled(&instance, long_buffer,
                                          (s32)sizeof(long_buffer), 0x21U);
    if (long_status != (s32)XST_TIMEOUT || instance.UpdateTxSize != 0 ||
        instance.RecvByteCount != (s32)sizeof(long_buffer) ||
        instance.RecvBufferPtr != long_buffer || abort_calls != 1U ||
        abort_update_tx_size_seen != 1 || abort_cr_reset_seen == 0U ||
        abort_cr_write_value != ((u32)XIICPS_CR_RESET_VALUE |
                                 (u32)XIICPS_CR_CLR_FIFO_MASK) ||
        mock_cr != (u32)XIICPS_CR_RESET_VALUE || mock_isr != 0U ||
        transfer_size_writes != 1U || transfer_size_values[0] != 252U ||
        mock_transfer_size != 252U || fifo_full_calls != 2U || sleep_calls != 3U) {
        fprintf(stderr,
                "FAIL long_timeout_state status=%d update=%d recv_count=%d abort=%u abort_update=%d abort_cr_write=0x%08x xfer_writes=%u first_size=%u fifo=%u sleep=%u cr=0x%08x isr=0x%08x\n",
                long_status, instance.UpdateTxSize, instance.RecvByteCount,
                abort_calls, abort_update_tx_size_seen, abort_cr_write_value,
                transfer_size_writes, transfer_size_values[0], fifo_full_calls,
                sleep_calls, mock_cr, mock_isr);
        return 1;
    }

    active_case = CASE_SUCCESS;
    active_platform = XPLAT_ZYNQ;
    short_status = XIicPs_MasterRecvPolled(
        &instance, short_buffer, (s32)sizeof(short_buffer), 0x21U);
    if (short_status != (s32)XST_SUCCESS || instance.UpdateTxSize != 0 ||
        instance.RecvByteCount != 0 || instance.RecvBufferPtr != short_buffer ||
        abort_calls != 1U || abort_update_tx_size_seen != 1 ||
        abort_cr_reset_seen == 0U ||
        abort_cr_write_value != ((u32)XIICPS_CR_RESET_VALUE |
                                 (u32)XIICPS_CR_CLR_FIFO_MASK) ||
        mock_cr != (u32)XIICPS_CR_RESET_VALUE ||
        mock_isr != (u32)XIICPS_IXR_COMP_MASK ||
        transfer_size_writes != 2U || transfer_size_values[0] != 252U ||
        transfer_size_values[1] != (u32)sizeof(short_buffer) ||
        mock_transfer_size != (u32)sizeof(short_buffer) || fifo_full_calls != 2U ||
        sleep_calls != 3U || bad_sleep_delay != 0U) {
        fprintf(stderr,
                "FAIL short_reuse status=%d update=%d recv_count=%d abort=%u xfer_writes=%u sizes=[%u,%u] fifo=%u sleep=%u cr=0x%08x isr=0x%08x\n",
                short_status, instance.UpdateTxSize, instance.RecvByteCount,
                abort_calls, transfer_size_writes, transfer_size_values[0],
                transfer_size_values[1], fifo_full_calls, sleep_calls,
                mock_cr, mock_isr);
        return 1;
    }
    printf("CASE zynq_long_timeout_then_short_success PASS long_status=%d short_status=%d update_tx_size=%d trans_size=[%u,%u] abort=%u abort_update=%d abort_cr_write=0x%08x fifo=%u\n",
           long_status, short_status, instance.UpdateTxSize,
           transfer_size_values[0], transfer_size_values[1], abort_calls,
           abort_update_tx_size_seen, abort_cr_write_value, fifo_full_calls);
    return 0;
}

int main(void)
{
    int failures = 0;
    failures += run_case("success", CASE_SUCCESS, 0U, 1, 0,
                         (s32)XST_SUCCESS, 0U, 1U, 0U, 0U,
                         XIICPS_IXR_COMP_MASK);
    failures += run_case("nack_failure", CASE_NACK, 0U, 1, 0,
                         (s32)XST_FAILURE, 0U, 1U, 0U, 0U,
                         XIICPS_IXR_NACK_MASK);
    failures += run_case("hardware_to_failure", CASE_HARDWARE_TO, 0U, 1, 0,
                         (s32)XST_FAILURE, 0U, 1U, 0U, 0U,
                         XIICPS_IXR_TO_MASK);
    failures += run_case("arbitration_lost", CASE_ARB_LOST, 0U, 1, 0,
                         (s32)XST_IIC_ARB_LOST, 0U, 1U, 0U, 0U,
                         XIICPS_IXR_ARB_LOST_MASK);
    failures += run_case("ordinary_poll_timeout", CASE_ORDINARY_TIMEOUT, 0U, 1, 0,
                         (s32)XST_TIMEOUT, 1U, 1U, 0U, 3U, 0U);
    failures += run_case("zynq_fifo_timeout", CASE_ZYNQ_FIFO_TIMEOUT,
                         XPLAT_ZYNQ, 300, 1, (s32)XST_TIMEOUT,
                         1U, 1U, 2U, 3U, 0U);
    failures += run_reuse_after_long_timeout();
    if (failures != 0) return EXIT_FAILURE;
    puts("RESULT=7/7 real-function host scenarios passed");
    return EXIT_SUCCESS;
}
'''


def build_harness(read_function: str, recv_function: str) -> str:
    """把两段真实函数体与受控 MMIO/mock 拼成主机 harness。"""
    return "\n".join((HOST_PREAMBLE, read_function, recv_function, HOST_DRIVER, HOST_MAIN))


def run_harness(source: str, run_dir: Path) -> tuple[dict, int]:
    """编译并运行函数体 harness，所有产物写入本次唯一证据目录。"""
    source_path = run_dir / "iicps_sw_timeout_host_harness.c"
    source_path.write_text(source, encoding="utf-8", newline="\n")
    gcc = shutil.which("gcc")
    if gcc is None:
        return ({"status": "GCC_UNAVAILABLE", "compile_return_code": None,
                 "runtime_return_code": None, "scenarios": []}, 2)

    version_run = subprocess.run(
        [gcc, "--version"], capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=10
    )
    version = version_run.stdout.splitlines()[0] if version_run.stdout else "unknown"
    executable = run_dir / ("iicps_sw_timeout_host_harness.exe" if sys.platform == "win32"
                            else "iicps_sw_timeout_host_harness")
    compile_command = [gcc, "-std=c99", "-Wall", "-Wextra", "-Werror", "-O0",
                       "-DXIICPS_RX_MAX_LOOPCNT=3U", str(source_path), "-o", str(executable)]
    compiled = subprocess.run(
        compile_command, cwd=run_dir, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=30
    )
    (run_dir / "compile_stdout.txt").write_text(compiled.stdout, encoding="utf-8")
    (run_dir / "compile_stderr.txt").write_text(compiled.stderr, encoding="utf-8")
    result = {
        "status": "COMPILE_FAILED" if compiled.returncode else "COMPILED",
        "compiler": version,
        "compile_command": compile_command,
        "compile_return_code": compiled.returncode,
        "compile_stdout": compiled.stdout,
        "compile_stderr": compiled.stderr,
        "runtime_command": None,
        "runtime_return_code": None,
        "runtime_stdout": "",
        "runtime_stderr": "",
        "runtime_timed_out": False,
        "scenarios": [],
    }
    if compiled.returncode != 0:
        return result, 1

    started = time.perf_counter()
    try:
        runtime = subprocess.run(
            [str(executable)], cwd=run_dir, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=10
        )
    except subprocess.TimeoutExpired as error:
        result.update({
            "status": "RUNTIME_TIMEOUT",
            "runtime_timed_out": True,
            "runtime_duration_seconds": round(time.perf_counter() - started, 6),
            "runtime_stdout": error.stdout or "",
            "runtime_stderr": error.stderr or "",
        })
        (run_dir / "runtime_stdout.txt").write_text(str(result["runtime_stdout"]), encoding="utf-8")
        (run_dir / "runtime_stderr.txt").write_text(str(result["runtime_stderr"]), encoding="utf-8")
        return result, 1

    (run_dir / "runtime_stdout.txt").write_text(runtime.stdout, encoding="utf-8")
    (run_dir / "runtime_stderr.txt").write_text(runtime.stderr, encoding="utf-8")
    scenario_lines = re.findall(r"^CASE (\S+) PASS .*?$", runtime.stdout, re.M)
    passed = (runtime.returncode == 0 and len(scenario_lines) == 7 and
              "RESULT=7/7 real-function host scenarios passed" in runtime.stdout)
    result.update({
        "status": "PASS" if passed else "RUNTIME_FAILED",
        "runtime_command": [str(executable)],
        "runtime_return_code": runtime.returncode,
        "runtime_duration_seconds": round(time.perf_counter() - started, 6),
        "runtime_stdout": runtime.stdout,
        "runtime_stderr": runtime.stderr,
        "scenarios": scenario_lines,
    })
    return result, 0 if passed else 1


def run_git_apply(git: str, patch: Path, run_dir: Path, check: bool) -> dict:
    """在隔离证据树中检查或应用一个 overlay。"""
    prefix = run_dir.relative_to(ROOT).as_posix()
    command = [git, "apply"]
    if check:
        command.append("--check")
    command.extend(["-p1", f"--directory={prefix}", str(patch)])
    outcome = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=30
    )
    return {
        "command": command,
        "return_code": outcome.returncode,
        "stdout": outcome.stdout,
        "stderr": outcome.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-name", required=True, help="tmp 下从未使用过的证据目录名")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", args.run_name):
        raise ValidationError("run-name 仅接受 ASCII 字母、数字、下划线和连字符")
    if not HARDWARE_PATCH.is_file() or not SOFTWARE_PATCH.is_file():
        raise ValidationError("指定 overlay 文件缺失")
    if sha256(HARDWARE_PATCH.read_bytes()) != HARDWARE_PATCH_SHA256:
        raise ValidationError("既有硬件 TO overlay SHA-256 与冻结证据不符")

    git = shutil.which("git")
    if git is None:
        raise ValidationError("git 命令不可用，不能验证基线关系或重放 overlay")
    head_run = subprocess.run(
        [git, "rev-parse", "HEAD"], cwd=ROOT, check=True,
        capture_output=True, text=True, encoding="utf-8", timeout=10
    )
    head = head_run.stdout.strip()
    ancestry_command = [git, "merge-base", "--is-ancestor", BASELINE_COMMIT, "HEAD"]
    ancestry_run = subprocess.run(
        ancestry_command, cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=10
    )
    if ancestry_run.returncode != 0:
        raise ValidationError(
            "固定基线不是当前 HEAD 的祖先，或该基线不可解析："
            f"baseline={BASELINE_COMMIT} HEAD={head} "
            f"git_exit={ancestry_run.returncode} {ancestry_run.stderr.strip()}"
        )

    original_bytes: dict[str, bytes] = {}
    for name, expected in SOURCE_SPECS.items():
        source = VENDOR_SRC / name
        if not source.is_file():
            raise ValidationError(f"固定 Vitis 原件不存在：{source}")
        data = source.read_bytes()
        actual = sha256(data)
        if actual != expected:
            raise ValidationError(
                f"拒绝变化的 Vitis 原件：{source} actual={actual} expected={expected}"
            )
        original_bytes[name] = data
    original_hashes = verify_vendor_hashes(original_bytes)
    vendor_api_inventory = verify_vendor_api_inventory()

    run_dir = RUN_ROOT / args.run_name
    if RUN_ROOT.exists() and (not RUN_ROOT.is_dir() or RUN_ROOT.is_symlink()):
        raise ValidationError(f"证据根不是普通目录：{RUN_ROOT}")
    if run_dir.exists() or run_dir.is_symlink():
        raise ValidationError(f"证据目录已存在，拒绝覆盖：{run_dir}")
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "baseline").mkdir()
    (run_dir / "src").mkdir()

    try:
        baseline_dir = run_dir / "baseline"
        source_dir = run_dir / "src"
        for name, data in original_bytes.items():
            (baseline_dir / name).write_bytes(data)
            (source_dir / name).write_bytes(data)
        inputs_dir = run_dir / "inputs"
        inputs_dir.mkdir()
        shutil.copyfile(HARDWARE_PATCH, inputs_dir / HARDWARE_PATCH.name)
        shutil.copyfile(SOFTWARE_PATCH, inputs_dir / SOFTWARE_PATCH.name)

        tampered = dict(original_bytes)
        tampered_name = "xiicps_master.c"
        tampered[tampered_name] = original_bytes[tampered_name] + b"\n"
        try:
            verify_vendor_hashes(tampered)
        except ValidationError as error:
            hash_guard_selftest = {
                "status": "PASS",
                "changed_file": tampered_name,
                "rejected": True,
                "diagnostic": str(error),
            }
        else:
            raise ValidationError("固定源码哈希防变更自测未拒绝篡改副本")

        apply_records = []
        hardware_snapshot: dict[str, str] | None = None
        for patch in (HARDWARE_PATCH, SOFTWARE_PATCH):
            check_record = run_git_apply(git, patch, run_dir, check=True)
            apply_records.append({"patch": str(patch.relative_to(ROOT)), "phase": "check",
                                  **check_record})
            if check_record["return_code"] != 0:
                raise ValidationError(
                    f"补丁预检查失败：{patch.name}\n{check_record['stdout']}{check_record['stderr']}"
                )
            apply_record = run_git_apply(git, patch, run_dir, check=False)
            apply_records.append({"patch": str(patch.relative_to(ROOT)), "phase": "apply",
                                  **apply_record})
            if apply_record["return_code"] != 0:
                raise ValidationError(
                    f"补丁重放失败：{patch.name}\n{apply_record['stdout']}{apply_record['stderr']}"
                )
            if patch == HARDWARE_PATCH:
                hardware_snapshot = {
                    name: (source_dir / name).read_text(encoding="utf-8")
                    for name in SOURCE_SPECS
                }

        original = {name: (baseline_dir / name).read_text(encoding="utf-8")
                    for name in SOURCE_SPECS}
        if hardware_snapshot is None:
            raise ValidationError("未保存第一阶段硬件 TO overlay 的中间快照")
        hardware = hardware_snapshot
        software = {name: (source_dir / name).read_text(encoding="utf-8")
                    for name in SOURCE_SPECS}
        checks = verify_source_contract(
            original,
            hardware,
            software,
            HARDWARE_PATCH.read_text(encoding="utf-8"),
            SOFTWARE_PATCH.read_text(encoding="utf-8"),
        )
        # 每个文件的 baseline 与 overlay 后 SHA 都作为重放证据保存。
        patched_hashes = {name: sha256((source_dir / name).read_bytes())
                          for name in SOURCE_SPECS}
        diff_parts: list[str] = []
        for name in sorted(SOURCE_SPECS):
            diff_parts.extend(difflib.unified_diff(
                (baseline_dir / name).read_text(encoding="utf-8").splitlines(True),
                (source_dir / name).read_text(encoding="utf-8").splitlines(True),
                fromfile=f"a/src/{name}", tofile=f"b/src/{name}"
            ))
        (run_dir / "replayed_overlays.diff").write_text(
            "".join(diff_parts), encoding="utf-8", newline="\n"
        )

        read_function = function_text(
            software["xiicps_xfer.c"], "s32 XIicPs_MasterPolledRead("
        )
        recv_function = function_text(
            software["xiicps_master.c"], "s32 XIicPs_MasterRecvPolled("
        )
        extracted = {
            "XIicPs_MasterPolledRead": sha256(read_function.encode("utf-8")),
            "XIicPs_MasterRecvPolled": sha256(recv_function.encode("utf-8")),
        }
        harness, harness_exit = run_harness(
            build_harness(read_function, recv_function), run_dir
        )
        end_hashes = {
            name: sha256((VENDOR_SRC / name).read_bytes())
            for name in SOURCE_SPECS
        }
        if end_hashes != original_hashes:
            raise ValidationError("测试期间检测到 Vitis 安装目录源码发生变化")

        summary = {
            "task_id": "S3-SW03-IICPS-SOFTWARE-DEADLINE",
            "baseline_commit": BASELINE_COMMIT,
            "tested_head": head,
            "baseline_ancestry_command": ancestry_command,
            "baseline_ancestry_return_code": ancestry_run.returncode,
            "vendor_source_path": str(VENDOR_SRC),
            "vendor_source_before_sha256": original_hashes,
            "vendor_source_after_sha256": end_hashes,
            "vendor_api_inventory": vendor_api_inventory,
            "source_hash_guard_selftest": hash_guard_selftest,
            "overlay_order": [
                {"path": str(HARDWARE_PATCH.relative_to(ROOT)),
                 "sha256": sha256(HARDWARE_PATCH.read_bytes())},
                {"path": str(SOFTWARE_PATCH.relative_to(ROOT)),
                 "sha256": sha256(SOFTWARE_PATCH.read_bytes())},
            ],
            "overlay_apply_commands": apply_records,
            "overlay_source_after_sha256": patched_hashes,
            "extracted_real_functions_sha256": extracted,
            "source_contract_checks": checks,
            "host_harness": harness,
            "limitations": [
                "主机 harness 编译运行从固定 Vitis 原件顺序重放补丁后抽取的两个真实函数体；MMIO、FIFO、MasterRead、平台信息与 Abort 由 mock 提供。",
                "轮询宏在主机 harness 中以 3 缩小；生产源默认值 1,000,000 另由源码契约核对。",
                "usleep(1) 次数是软件轮询边界，不等于墙钟一秒或硬实时 deadline。",
                "未执行 Vitis/BSP 全量构建、真实硬件/MMIO 验证或实物操作。",
            ],
        }
        summary_path = run_dir / "summary.json"
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8")
        print("PASS fixed baseline is an ancestor of HEAD and six Vitis source SHA-256 values")
        print("PASS source hash guard rejected an altered in-memory source copy")
        print(f"PASS sequential overlay replay: {summary['overlay_order']}")
        for check in checks:
            print(f"PASS source contract: {check}")
        print(f"HOST_HARNESS={harness['status']}")
        print(f"COMPILE_EXIT_CODE={harness.get('compile_return_code')}")
        print(f"RUNTIME_EXIT_CODE={harness.get('runtime_return_code')}")
        if harness.get("runtime_stdout"):
            print(harness["runtime_stdout"], end="")
        print(f"EVIDENCE={summary_path.relative_to(ROOT).as_posix()}")
        return harness_exit
    except Exception as error:
        (run_dir / "failure.txt").write_text(f"{type(error).__name__}: {error}\n",
                                             encoding="utf-8")
        raise


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValidationError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
