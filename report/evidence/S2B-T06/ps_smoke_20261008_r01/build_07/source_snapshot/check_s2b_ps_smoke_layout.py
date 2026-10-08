#!/usr/bin/env python3
"""只读核验PS检查ELF、map、实际BSP与XSA的独占DDR布局。"""

from __future__ import annotations

import argparse
import copy
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

from check_stage_delivery import _check_absolute_path, load_json_strict, sha256_file


BUFFER_SIZE = 1024 * 1024
APP_SIZE = 16 * 1024 * 1024
STACK_PAIRS = [
    ("_stack_end", "_stack", 0x4000),
    ("_irq_stack_end", "__irq_stack", 1024),
    ("_supervisor_stack_end", "__supervisor_stack", 2048),
    ("_abort_stack_end", "__abort_stack", 1024),
    ("_fiq_stack_end", "__fiq_stack", 1024),
    ("_undef_stack_end", "__undef_stack", 1024),
]


def require(condition: bool, message: str) -> None:
    """所有歧义、未完成检查和错误均返回失败。"""
    if not condition:
        raise ValueError(message)


def interval(begin: int, size: int) -> tuple[int, int]:
    """核对32位非空半开区间，禁止地址溢出。"""
    require(type(begin) is int and type(size) is int, "区间字段必须为整数")
    require(begin >= 0 and size > 0 and begin + size <= 0x100000000,
            f"区间无效或32位溢出：{begin:#x}+{size:#x}")
    return begin, begin + size


def contained(inner: tuple[int, int], outer: tuple[int, int]) -> bool:
    """比较半开区间，结束地址不属于区间。"""
    return outer[0] <= inner[0] < inner[1] <= outer[1]


def overlaps(left: tuple[int, int], right: tuple[int, int]) -> bool:
    """相邻区间不算重叠。"""
    return left[0] < right[1] and right[0] < left[1]


def xsa_metadata(path: Path) -> dict[str, Any]:
    """从实际PS-only HWH读取DDR/UART参数，不推断物理板卡身份。"""
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "XSA含重复成员")
        require(not any(name.lower().endswith((".bit", ".pdi")) for name in names),
                "PS-only输入XSA不得含位流")
        hwh = [name for name in names if name.endswith(".hwh")]
        require(len(hwh) == 1, "XSA必须唯一包含HWH")
        require(archive.getinfo(hwh[0]).file_size < 8 * 1024 * 1024, "HWH超出本任务读取预算")
        tree = ET.fromstring(archive.read(hwh[0]))
    modules = list(tree.iter("MODULE"))
    require(len(modules) == 1 and modules[0].attrib.get("MODTYPE") == "processing_system7",
            "XSA必须仅包含processing_system7")
    pairs = list(modules[0].findall("PARAMETERS/PARAMETER"))
    params = {item.attrib["NAME"]: item.attrib["VALUE"] for item in pairs}
    require(len(params) == len(pairs), "HWH参数重复")
    for key in ("PCW_USE_M_AXI_GP0", "PCW_USE_M_AXI_GP1", "PCW_USE_S_AXI_GP0",
                "PCW_USE_S_AXI_GP1", "PCW_USE_S_AXI_HP0", "PCW_USE_S_AXI_HP1",
                "PCW_USE_S_AXI_HP2", "PCW_USE_S_AXI_HP3", "PCW_USE_S_AXI_ACP"):
        require(params.get(key) == "0", f"PS-only前提不符：{key}")
    require(params.get("PCW_UART1_PERIPHERAL_ENABLE") == "1", "XSA未启用UART1")
    require(params.get("PCW_UART1_UART1_IO") == "MIO 48 .. 49", "XSA UART1 MIO不符")
    base = int(params["PCW_DDR_RAM_BASEADDR"], 0)
    high = int(params["PCW_DDR_RAM_HIGHADDR"], 0)
    uart = int(params["PCW_UART1_BASEADDR"], 0)
    require(uart == 0xE0001000, "XSA UART1基地址不符")
    interval(base, high - base + 1)
    return {"hwh_member": hwh[0], "ddr_begin": base, "ddr_end": high + 1,
            "uart1_base": uart, "ps_module": modules[0].attrib["INSTANCE"]}


def parse_elf(data: bytes) -> dict[str, Any]:
    """解析实际ELF32 ARM头、所有节、LOAD段和符号表，拒绝截断格式。"""
    require(len(data) >= 52 and data[:7] == b"\x7fELF\x01\x01\x01", "必须是ELF32小端格式")
    fields = struct.unpack_from("<HHIIIIIHHHHHH", data, 16)
    typ, machine, version, entry, phoff, shoff, flags, ehsize, phsize, phnum, shsize, shnum, shstr = fields
    require((typ, machine, version, ehsize, phsize, shsize) == (2, 40, 1, 52, 32, 40),
            "ELF类型、ARM架构或表项大小不符")
    require(0 < phnum < 128 and 0 < shnum < 4096 and 0 < shstr < shnum,
            "ELF表项数量或名称表无效")
    require(phoff + phnum * phsize <= len(data) and shoff + shnum * shsize <= len(data),
            "ELF表被截断")
    raw_sections = [struct.unpack_from("<IIIIIIIIII", data, shoff + index * shsize)
                    for index in range(shnum)]

    def payload(row: tuple[int, ...]) -> bytes:
        require(row[4] + row[5] <= len(data), "ELF节内容被截断")
        return data[row[4]:row[4] + row[5]]

    def name_at(table: bytes, offset: int) -> str:
        require(offset < len(table), "ELF字符串索引越界")
        end = table.find(b"\0", offset)
        require(end >= 0, "ELF字符串缺少终止符")
        return table[offset:end].decode("ascii")

    strings = payload(raw_sections[shstr])
    sections = []
    symbols = []
    for index, row in enumerate(raw_sections):
        name = name_at(strings, row[0])
        sections.append({"index": index, "name": name, "type": row[1], "flags": row[2],
                         "address": row[3], "offset": row[4], "size": row[5], "align": row[8]})
        if row[1] != 8:
            payload(row)
        if row[1] == 2:
            require(row[9] == 16 and row[5] % 16 == 0 and 0 < row[6] < shnum,
                    "ELF符号表格式无效")
            names = payload(raw_sections[row[6]])
            for offset in range(row[4], row[4] + row[5], 16):
                st_name, value, size, info, other, section = struct.unpack_from("<IIIBBH", data, offset)
                symbols.append({"name": name_at(names, st_name), "value": value, "size": size,
                                "type": info & 15, "section": section})
    require(symbols, "ELF缺少可复核的符号表")
    programs = []
    for index in range(phnum):
        row = struct.unpack_from("<IIIIIIII", data, phoff + index * phsize)
        require(row[1] + row[4] <= len(data) and row[4] <= row[5], "ELF程序段被截断或大小无效")
        programs.append({"type": row[0], "offset": row[1], "virtual": row[2], "physical": row[3],
                         "file_size": row[4], "memory_size": row[5], "flags": row[6], "align": row[7]})
    return {"entry": entry, "flags": flags, "sections": sections, "programs": programs,
            "symbols": symbols}


def macro_int(text: str, name: str) -> int:
    """仅接受实际BSP中的唯一整数宏定义，不猜宏别名。"""
    matches = re.findall(rf"^\s*#define\s+{re.escape(name)}\s+(0[xX][0-9a-fA-F]+|[0-9]+)[uUlL]*\s*$",
                         text, re.MULTILINE)
    require(len(matches) == 1, f"BSP整数宏缺失或重复：{name}")
    return int(matches[0], 0)


def verify_cache_contract(text: str) -> None:
    """分别检查实际两项范围函数内的32B常量，不借用其他函数的常量。"""
    for name in ("Xil_DCacheFlushRange", "Xil_DCacheInvalidateRange"):
        found = list(re.finditer(rf"void\s+{name}\s*\(INTPTR\s+adr,\s*u32\s+len\)\s*\{{", text))
        require(len(found) == 1, f"实际缓存函数缺失或重复：{name}")
        begin = found[0].end()
        balance = 1
        end = begin
        while end < len(text) and balance:
            balance += (text[end] == "{") - (text[end] == "}")
            end += 1
        require(balance == 0, f"实际缓存函数内容未完整读取：{name}")
        body = text[begin:end - 1]
        values = re.findall(r"const\s+u32\s+cacheline\s*=\s*([0-9]+)U\s*;", body)
        require(values == ["32"], f"实际范围函数缓存行不符：{name}")
        require("#ifndef USE_AMP" in body and "XPS_L2CC_BASEADDR" in body,
                f"实际范围函数缺少非AMP的L2维护：{name}")


def brace_body(text: str, opening: int) -> str:
    """提取已去注释的C大括号块；未闭合时拒绝继续审计。"""
    require(text[opening] == "{", "审计块起点不是大括号")
    balance = 1
    end = opening + 1
    while end < len(text) and balance:
        balance += (text[end] == "{") - (text[end] == "}")
        end += 1
    require(balance == 0, "审计C块未完整读取")
    return text[opening + 1:end - 1]


def c_function(text: str, name: str) -> str:
    """只接受唯一函数定义，不把声明或注释当作实现。"""
    clean = re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.DOTALL)
    matches = list(re.finditer(rf"\b{re.escape(name)}\s*\([^;{{}}]*\)\s*\{{", clean))
    require(len(matches) == 1, f"审计函数定义缺失或重复：{name}")
    return brace_body(clean, matches[0].end() - 1)


def validate_initializer(elf: dict[str, Any], regions: list[dict[str, Any]], ld: str, link_map: str,
                         source: str, preprocessed: str, ps_i: str, disassembly: str,
                         boot: str, crt: str, timer_config: str, timer_backend: str, elf_bytes: bytes) -> dict[str, Any]:
    """证明最小初始化壳的OCM归属、独有停点及进入main前的启动数据归属。"""
    memory = re.findall(r"\b(\w+)\s*:\s*ORIGIN\s*=\s*(0x[0-9a-fA-F]+),\s*LENGTH\s*=\s*(0x[0-9a-fA-F]+)", ld)
    require(len(memory) == 2, "官方初始化壳必须仅声明两项OCM区域")
    ocm = [interval(int(begin, 16), int(size, 16)) for _, begin, size in memory]
    require(ocm == [(0, 0x30000), (0xFFFF0000, 0xFFFFFE00)], "官方初始化壳 OCM/CPU1顶部保留区不符")
    for (name, _, _), bounds in zip(memory, ocm):
        actual = [(item["name"], interval(int(item["base_address"], 0), int(item["size"], 0)))
                  for item in regions if "ram" in item["name"].lower()]
        require(sum(contained(bounds, region) for _, region in actual) == 1,
                f"生成平台的实际memory regions不能唯一证明OCM：{name}")
        match = re.findall(rf"^{re.escape(name)}\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)\b", link_map, re.MULTILINE)
        require(len(match) == 1 and interval(int(match[0][0], 16), int(match[0][1], 16)) == bounds,
                f"初始化壳 map OCM区域不符：{name}")
    sections = [item for item in elf["sections"] if item["flags"] & 2 and item["size"]]
    loads = [item for item in elf["programs"] if item["type"] == 1 and item["memory_size"]]
    require(sections and loads, "初始化壳缺少ALLOC/LOAD")
    for kind, items in (("ALLOC", sections), ("LOAD", loads)):
        bounds_list = []
        for item in items:
            if kind == "LOAD":
                require(item["virtual"] == item["physical"], "初始化壳 LOAD虚实地址不符")
                bounds = interval(item["physical"], item["memory_size"])
            else:
                bounds = interval(item["address"], item["size"])
            require(sum(contained(bounds, region) for region in ocm) == 1,
                    f"初始化壳 {kind}越过OCM或CPU1保留区")
            require(not any(overlaps(bounds, old) for old in bounds_list), f"初始化壳 {kind}重叠")
            bounds_list.append(bounds)
    for section in sections:
        require(sum(contained(interval(section["address"], section["size"]),
                              interval(item["physical"], item["memory_size"])) for item in loads) == 1,
                f"初始化壳 ALLOC未被唯一LOAD覆盖：{section['name']}")

    def symbol(name: str) -> dict[str, Any]:
        found = [item for item in elf["symbols"] if item["name"] == name]
        require(len(found) == 1, f"初始化壳符号缺失或重复：{name}")
        return found[0]

    ready = symbol("s2b_ps_init_ready")
    fail = symbol("s2b_ps_init_fail")
    require(any(item["index"] == ready["section"] and item["flags"] & 4 and
                item["address"] <= ready["value"] < item["address"] + item["size"] for item in sections),
            "初始化壳完成符号不属于可执行OCM节")
    require(elf["entry"] == symbol("_vector_table")["value"] == 0, "初始化壳向量入口不符")
    named = {item["name"]: item for item in sections}
    require(".heap" in named and ".stack" in named, "初始化壳缺少heap/stack")
    stacks = []
    for start, end, size in STACK_PAIRS:
        expected = 0x6000 if start in ("_stack_end", "_irq_stack_end") else size
        bounds = interval(symbol(start)["value"], symbol(end)["value"] - symbol(start)["value"])
        require(bounds[1] - bounds[0] == expected and
                contained(bounds, interval(named[".stack"]["address"], named[".stack"]["size"])),
                f"初始化壳模式栈归属/大小不符：{start}")
        require(not any(overlaps(bounds, old) for old in stacks), "初始化壳模式栈重叠")
        stacks.append(bounds)
    heap = interval(symbol("_heap_start")["value"], symbol("_heap_end")["value"] - symbol("_heap_start")["value"])
    require(heap[1] - heap[0] == 0x2000 and contained(heap, interval(named[".heap"]["address"], named[".heap"]["size"])),
            "初始化壳 heap归属/大小不符")
    for name in ("s2b_ps_init_ready", "s2b_ps_init_fail"):
        item = symbol(name)
        require(item["type"] == 2 and item["size"] > 0 and
                any(section["index"] == item["section"] and section["flags"] & 4 and
                    contained(interval(item["value"], item["size"]), interval(section["address"], section["size"]))
                    for section in sections), f"初始化停驻函数不属于可执行OCM：{name}")
        block = c_function(source, name)
        require('for (;;)' in block and '"wfe"' in block and "return" not in block, "初始化停驻函数必须无限WFE")
    for name in ("s2b_ps_init_result", "s2b_ps_init_return"):
        item = symbol(name)
        require(item["type"] == 1 and item["size"] == 4 and item["value"] % 64 == 0 and
                any(contained(interval(item["value"], 4), region) for region in ocm), "初始化状态对象必须位于64B对齐OCM")
    main = c_function(re.sub(r"^\s*#[^\n]*", "", preprocessed, flags=re.MULTILINE), "main")
    required_order = ["Xil_DCacheFlush();", "Xil_DCacheDisable();", "s2b_ps_init_return = ps7_init();",
                      "s2b_ps_init_result = 2U;", "s2b_ps_init_ready();"]
    positions = [main.find(item) for item in required_order]
    require(all(item >= 0 for item in positions) and positions == sorted(positions), "实际初始化壳执行次序不符")
    condition = re.search(r"if\s*\(s2b_ps_init_return\s*!=\s*\(?0\)?\)\s*\{", main)
    require(condition is not None and "s2b_ps_init_fail();" in brace_body(main, condition.end() - 1),
            "实际ps7_init失败未停驻")
    allowed_calls = {"if", "dsb", "ps7_init", "s2b_ps_init_fail", "s2b_ps_init_ready",
                     "Xil_DCacheFlush", "Xil_DCacheDisable", "__asm__", "volatile"}
    source_calls = set(re.findall(r"\b(\w+)\s*\(", c_function(source, "main")))
    require(source_calls <= allowed_calls, f"最小初始化main出现其他调用：{source_calls - allowed_calls}")
    forbidden = ("LoadBootImage", "ps7_post_config", "FabricInit", "XDcfg_Transfer",
                 "FsblHandoffExit", "FsblHandoffJtagExit", "GetSiliconVersion")
    require(not any(symbol["name"] in forbidden for symbol in elf["symbols"]), "初始化ELF仍链接启动器或PL配置入口")
    actual_ps_init = c_function(re.sub(r"^\s*#[^\n]*", "", ps_i, flags=re.MULTILINE), "ps7_init")
    require(not any(name in actual_ps_init for name in forbidden), "实际ps7_init不能调用启动器/PL配置入口")
    clean_disassembly = disassembly.replace("\r", "")
    for name, item in (("s2b_ps_init_ready", ready), ("s2b_ps_init_fail", fail)):
        blocks = re.findall(rf"^[0-9a-f]+ <{name}>:\n(.*?)(?=^[0-9a-f]+ <|\Z)", clean_disassembly, re.MULTILINE | re.DOTALL)
        require(len(blocks) == 1 and "\twfe" in blocks[0] and not re.search(r"\bblx?\s", blocks[0]),
                f"实际停驻机器码必须包含WFE且无调用：{name}")
        calls = re.findall(rf"\bbl\s+([0-9a-f]+)\s+<{name}>", clean_disassembly)
        require(calls and all(int(address, 16) == item["value"] for address in calls), "实际停驻调用地址不符")
    require(len(re.findall(r"\bbl\s+[0-9a-f]+\s+<ps7_init>", clean_disassembly)) == 1,
            "初始化ELF只能由main唯一调用ps7_init")
    named = {item["name"]: item for item in sections}
    require(".mmu_tbl" in named and named[".mmu_tbl"]["size"] == 0x4000 and
            symbol("MMUTable")["value"] == named[".mmu_tbl"]["address"], "启动MMU表必须在已核验OCM节")
    clear_ranges = {}
    for begin_name, end_name in (("__bss_start", "__bss_end"), ("__sbss_start", "__sbss_end")):
        begin, end = symbol(begin_name)["value"], symbol(end_name)["value"]
        require(any(low <= begin <= end <= high for low, high in ocm), "进入main前的启动清零范围越过OCM")
        clear_ranges[begin_name] = [begin, end]
    constructor_addresses = []
    constructor_names = ["frame_dummy"]
    if any(item["name"] == "xtimerinit" for item in elf["symbols"]):
        constructor_names.append("xtimerinit")
    allowed_constructors = {symbol(name)["value"] for name in constructor_names}
    for section in sections:
        if section["name"] in (".init_array", ".preinit_array", ".ctors"):
            require(section["size"] % 4 == 0, "构造函数表格式不符")
            values = struct.unpack_from("<" + "I" * (section["size"] // 4), elf_bytes, section["offset"])
            for address in values:
                require(address in allowed_constructors, "存在未审计的进入main前构造函数")
                constructor_addresses.append(address)
    require(set(constructor_addresses) == allowed_constructors, "实际构造函数表与已链接的允许构造符号不符")
    timer_range = None
    if "xtimerinit" in constructor_names:
        timer_obj = symbol("TimerInst")
        require(timer_obj["type"] == 1 and timer_obj["size"] > 0 and
                any(contained(interval(timer_obj["value"], timer_obj["size"]), region) for region in ocm),
                "计时器构造函数的数据对象必须属于OCM")
        timer_range = [timer_obj["value"], timer_obj["value"] + timer_obj["size"]]
    require(macro_int(timer_config, "XTIMER_IS_DEFAULT_TIMER") == 1 and
            macro_int(timer_config, "XTIMER_NO_TICK_TIMER") == 1, "实际计时器配置超出本次默认PS计时器依据")
    for name in ("XilSleepTimer_Init", "XilTickTimer_Init"):
        body = c_function(timer_backend, name)
        require(not re.search(r"\b(?:Xil_Out32|Xil_In32|XGlobalTimer_Start)\s*\(", body),
                "实际构造计时器初始化不应开始访问DDR或启动计时器")
    require("bic\tr0, r0, #0x1" in boot and "b\t_start" in boot and "bl\tmain" in crt,
            "实际BSP启动必须先关闭旧MMU再进入C启动/main")
    require(not any(name in boot + crt for name in forbidden), "BSP启动不能调用启动器或PL配置入口")
    return {"status": "PASS_OFFLINE_MINIMAL_OCM_INIT", "ready_symbol": "s2b_ps_init_ready",
            "ready_address": ready["value"], "fail_symbol": "s2b_ps_init_fail", "fail_address": fail["value"],
            "result_address": symbol("s2b_ps_init_result")["value"],
            "ps7_return_address": symbol("s2b_ps_init_return")["value"], "entry": elf["entry"], "ocm_ranges": ocm,
            "cpu1_top_reserved": [0xFFFFFE00, 0x100000000], "alloc_sections": sections, "load_segments": loads,
            "mode_stacks": stacks, "heap": heap, "startup_clear_ranges": clear_ranges,
            "constructor_addresses": constructor_addresses, "init_execution": "NOT_RUN",
            "constructor_names": constructor_names, "timer_object_range": timer_range,
            "requires_cold_jtag_boot_cpu0_exclusive_and_cpu1_stopped": True,
            "requires_all_dma_and_pl_writers_idle": True}


def validate_layout(elf: dict[str, Any], policy: dict[str, Any], ld: str, link_map: str,
                    xparams: str, bspconfig: str, cache: str, uart_header: str) -> dict[str, Any]:
    """联合核对独占buffer、全部ALLOC/LOAD、六种模式栈、heap及启动向量。"""
    app = interval(policy["app_begin"], policy["app_size"])
    buffer = interval(policy["buffer_begin"], policy["buffer_size"])
    ddr = (policy["ddr_begin"], policy["ddr_end"])
    require(policy["app_size"] == APP_SIZE and policy["buffer_size"] == BUFFER_SIZE,
            "应用区或buffer大小不符")
    require(app[0] == ddr[0] and app[1] == buffer[0] and contained(buffer, ddr),
            "DDR分区不符或越过BSP保留区")
    require(buffer[0] % 64 == 0 and buffer[1] % 64 == 0, "buffer未64B对齐")
    require(buffer[1] < 0x100000000, "buffer半开结束地址不能在32位计算中回绕")
    require(macro_int(xparams, policy["ddr_base_macro"]) == ddr[0] and
            macro_int(xparams, policy["ddr_high_macro"]) == ddr[1] - 1,
            "实际BSP与XSA的DDR区间不符")
    require(macro_int(xparams, policy["uart_base_macro"]) == 0xE0001000,
            "BSP UART基地址不符")
    require(macro_int(bspconfig, "STDIN_BASEADDRESS") == 0xE0001000 and
            macro_int(bspconfig, "STDOUT_BASEADDRESS") == 0xE0001000, "BSP stdin/stdout不符")
    require("XUartPs_LookupConfig(UINTPTR BaseAddress)" in uart_header,
            "实际BSP缺少SDT基地址LookupConfig签名")
    verify_cache_contract(cache)
    for region_name, bounds in ((policy["app_region"], app), ("s2b_smoke_ddr", buffer)):
        ld_match = re.findall(rf"\b{re.escape(region_name)}\s*(?:\([^)]*\))?\s*:\s*ORIGIN\s*=\s*(0x[0-9a-fA-F]+),\s*LENGTH\s*=\s*(0x[0-9a-fA-F]+)", ld)
        map_match = re.findall(rf"^{re.escape(region_name)}\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)\b", link_map, re.MULTILINE)
        for matches in (ld_match, map_match):
            require(len(matches) == 1 and interval(int(matches[0][0], 16), int(matches[0][1], 16)) == bounds,
                    f"链接脚本/map区域与策略不符：{region_name}")
    sections = [item for item in elf["sections"] if item["flags"] & 2 and item["size"]]
    buffer_sections = [item for item in sections if item["name"] == ".s2b_smoke_buffer"]
    require(len(buffer_sections) == 1, "独占buffer节缺失或重复")
    bs = buffer_sections[0]
    require((bs["address"], bs["address"] + bs["size"]) == buffer and bs["type"] == 8 and
            bs["flags"] == 3 and bs["align"] >= 64, "buffer节边界、NOLOAD属性或对齐不符")
    for item in sections:
        bounds = interval(item["address"], item["size"])
        require(contained(bounds, buffer if item is bs else app), f"ALLOC节越界：{item['name']}")
    for index, left in enumerate(sections):
        for right in sections[index + 1:]:
            require(not overlaps(interval(left["address"], left["size"]),
                                 interval(right["address"], right["size"])), "ALLOC节之间重叠")
    loads = [item for item in elf["programs"] if item["type"] == 1 and item["memory_size"]]
    require(loads, "缺少LOAD段")
    envelope = (app[0], buffer[1])
    for item in loads:
        require(item["virtual"] == item["physical"], "LOAD段存在虚实地址差异")
        bounds = interval(item["physical"], item["memory_size"])
        require(contained(bounds, envelope), "LOAD段越过应用/buffer分区或启动保留区")
        if item["file_size"]:
            require(contained(interval(item["physical"], item["file_size"]), app),
                    "LOAD文件字节进入buffer或分区之外")
    for index, left in enumerate(loads):
        for right in loads[index + 1:]:
            require(not overlaps(interval(left["physical"], left["memory_size"]),
                                 interval(right["physical"], right["memory_size"])), "LOAD段之间重叠")
    for section in sections:
        require(sum(contained(interval(section["address"], section["size"]),
                              interval(item["physical"], item["memory_size"])) for item in loads) == 1,
                f"ALLOC节未被唯一LOAD覆盖：{section['name']}")
    symbols = elf["symbols"]

    def symbol(name: str) -> dict[str, Any]:
        found = [item for item in symbols if item["name"] == name]
        require(len(found) == 1, f"符号缺失或重复：{name}")
        return found[0]

    obj = symbol("s2b_smoke_buffer")
    require(obj["type"] == 1 and obj["section"] == bs["index"] and
            (obj["value"], obj["size"]) == (buffer[0], BUFFER_SIZE), "buffer对象归属或大小不符")
    status = symbol("s2b_smoke_result")
    require(status["type"] == 1 and status["size"] == 4 and status["value"] % 64 == 0 and
            contained(interval(status["value"], status["size"]), app), "物理诊断状态对象不符")
    require(symbol("__s2b_smoke_buffer_start")["value"] == buffer[0] and
            symbol("__s2b_smoke_buffer_end")["value"] == buffer[1], "buffer边界符号不符")
    for item in symbols:
        if item["size"] and item["section"] not in (0, 0xFFF1):
            if overlaps(interval(item["value"], item["size"]), buffer):
                require(item is obj, f"buffer内出现其他有大小的符号：{item['name']}")
    named = {item["name"]: item for item in sections}
    require(".heap" in named and ".stack" in named, "heap/stack分配节缺失")
    for start, end in (("__bss_start", "__bss_end"), ("__sbss_start", "__sbss_end")):
        begin_value = symbol(start)["value"]
        end_value = symbol(end)["value"]
        require(app[0] <= begin_value <= end_value <= app[1], f"启动清零范围越过应用区：{start}")
    stack_section = interval(named[".stack"]["address"], named[".stack"]["size"])
    require(symbol("__stack")["value"] == symbol("_stack")["value"], "启动user stack别名不符")
    stack_ranges = []
    for start, end, size in STACK_PAIRS:
        bounds = interval(symbol(start)["value"], symbol(end)["value"] - symbol(start)["value"])
        require(bounds[1] - bounds[0] == size and contained(bounds, stack_section),
                f"模式栈边界/大小不符：{start}")
        stack_ranges.append({"name": start, "begin": bounds[0], "end": bounds[1]})
    for index, left in enumerate(stack_ranges):
        for right in stack_ranges[index + 1:]:
            require(not overlaps((left["begin"], left["end"]), (right["begin"], right["end"])),
                    "模式栈之间重叠")
    heap = interval(symbol("_heap_start")["value"], symbol("_heap_end")["value"] - symbol("_heap_start")["value"])
    require(heap[1] - heap[0] == 0x4000 and contained(heap, interval(named[".heap"]["address"], named[".heap"]["size"])),
            "heap边界/大小不符")
    require(symbol("_heap")["value"] == symbol("HeapBase")["value"] == heap[0] and
            symbol("HeapLimit")["value"] == heap[1], "运行库heap别名不符")
    require(elf["entry"] == symbol("_vector_table")["value"] and
            any((item["flags"] & 4) and item["address"] <= elf["entry"] < item["address"] + item["size"] for item in sections),
            "启动向量/入口不在应用可执行节")
    map_buffer = re.findall(r"^\.s2b_smoke_buffer\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)\b", link_map, re.MULTILINE)
    require(len(map_buffer) == 1 and interval(int(map_buffer[0][0], 16), int(map_buffer[0][1], 16)) == buffer,
            "map的buffer输出节不符")
    for name, value in (("__s2b_smoke_buffer_start", buffer[0]), ("__s2b_smoke_buffer_end", buffer[1])):
        found = re.findall(rf"^\s*(0x[0-9a-fA-F]+)\s+{name}\s*=", link_map, re.MULTILINE)
        require(len(found) == 1 and int(found[0], 16) == value, f"map边界符号不符：{name}")
    return {"status": "PASS_OFFLINE_LAYOUT", "buffer_begin": buffer[0], "buffer_end_exclusive": buffer[1],
            "buffer_bytes": BUFFER_SIZE, "app_begin": app[0], "app_end_exclusive": app[1],
            "startup_reserved_below": ddr[0], "alloc_sections": sections, "load_segments": loads,
            "mode_stacks": stack_ranges, "heap": list(heap), "entry": elf["entry"],
            "hardware_execution": "NOT_RUN"}


def check_manifest(path: Path, self_test: bool = False) -> dict[str, Any]:
    """核对文件哈希后联合解析；自检只修改内存副本，不执行ARM程序。"""
    errors: list[str] = []
    checked_path = _check_absolute_path(path, "file", errors, "布局清单")
    require(checked_path is not None and not errors, "; ".join(errors))
    manifest = load_json_strict(checked_path)
    require(manifest["schema_version"] == 1 and manifest["hardware_execution"] == "NOT_RUN",
            "布局清单版本或未实测状态不符")
    files = {}
    for name, binding in manifest["files"].items():
        errors: list[str] = []
        actual = _check_absolute_path(Path(binding["path"]), "file", errors, name)
        require(actual is not None and not errors, "; ".join(errors))
        require(sha256_file(actual)[0] == binding["sha256"], f"文件SHA-256不符：{name}")
        files[name] = actual
    metadata = xsa_metadata(files["xsa"])
    policy = manifest["policy"]
    require(all(policy[key] == metadata[key] for key in ("ddr_begin", "ddr_end")),
            "布局策略与实际XSA的DDR区间不符")
    header = files["generated_header"].read_text(encoding="utf-8")
    require(macro_int(header, "S2B_BUFFER_BEGIN") == policy["buffer_begin"] and
            macro_int(header, "S2B_BUFFER_END") == policy["buffer_begin"] + policy["buffer_size"] and
            macro_int(header, "S2B_BSP_CACHELINE_BYTES") == 32,
            "实际编译头与布局策略不符")
    require(re.findall(r"^#define\s+S2B_UART1_BASE\s+(\w+)\s*$", header, re.MULTILINE) ==
            [policy["uart_base_macro"]], "实际编译UART基地址宏不符")
    for macro, name in (("S2B_C_SOURCE_SHA256", "c_source"), ("S2B_XSA_SHA256", "xsa")):
        require(re.findall(rf'^#define\s+{macro}\s+"([0-9a-f]{{64}})"\s*$', header, re.MULTILINE) ==
                [manifest["files"][name]["sha256"]], f"串口构建绑定不符：{macro}")
    elf_bytes = files["elf"].read_bytes()
    elf = parse_elf(elf_bytes)
    texts = [files[name].read_text(encoding="utf-8") for name in
             ("linker", "map", "xparameters", "bspconfig", "cache_source", "uart_header")]
    result = validate_layout(elf, policy, *texts)
    init_bytes = files["init_elf"].read_bytes()
    init_elf = parse_elf(init_bytes)
    init_texts = [files[name].read_text(encoding="utf-8") for name in
                  ("init_linker", "init_map", "init_source", "init_preprocessed", "ps_init_preprocessed",
                   "init_disassembly", "init_boot", "init_crt", "timer_config", "timer_backend")]
    result["initializer"] = validate_initializer(init_elf, manifest["init_policy"]["platform_memory_regions"],
                                                  *init_texts, init_bytes)
    compile_commands = load_json_strict(files["bsp_compile_commands"])
    startup_names = {"boot.S", "xil-crt0.S", "asm_vectors.S", "cpu_init.S", "translation_table.S",
                     "xiltimer.c", "globaltimer_sleep_zynq.c"}
    actual_commands = [item for item in compile_commands if Path(item["file"]).name in startup_names]
    require({Path(item["file"]).name for item in actual_commands} == startup_names and
            len(actual_commands) == len(startup_names), "BSP实际编译启动/构造源不完整或重复")
    require(all("-DSDT" in item["command"] and not re.search(r"-D(?:USE_AMP|SHAREABLE_DDR)\b", item["command"])
                for item in actual_commands), "本次启动代码实际编译宏超出已核验SDT非AMP配置")
    result["initializer"]["actual_startup_compile_commands"] = actual_commands
    require(manifest["init_policy"]["ready_symbol"] == "s2b_ps_init_ready" and
            manifest["init_policy"]["fail_symbol"] == "s2b_ps_init_fail" and
            manifest["init_policy"]["strategy"] == "MINIMAL_OCM_PS7_INIT", "初始化策略与独有停驻符号不符")
    with zipfile.ZipFile(files["xsa"]) as archive:
        for name, key in (("ps7_init.c", "ps_init_c"), ("ps7_init.h", "ps_init_h")):
            matches = [member for member in archive.namelist() if member.split("/")[-1] == name]
            require(len(matches) == 1 and archive.read(matches[0]) == files[key].read_bytes(),
                    f"官方初始化源码不属于固定XSA：{name}")
    result["xsa"] = metadata
    result["bound_sha256"] = {name: binding["sha256"] for name, binding in manifest["files"].items()}
    if self_test:
        cases = []
        mutations = [
            ("buffer_alignment", lambda model: model["sections"][next(i for i, item in enumerate(model["sections"]) if item["name"] == ".s2b_smoke_buffer")].update(address=policy["buffer_begin"] + 4)),
            ("buffer_exec", lambda model: model["sections"][next(i for i, item in enumerate(model["sections"]) if item["name"] == ".s2b_smoke_buffer")].update(flags=7)),
            ("stack_overflow", lambda model: model["sections"][next(i for i, item in enumerate(model["sections"]) if item["name"] == ".stack")].update(address=policy["buffer_begin"])),
            ("load_reserved", lambda model: next(item for item in model["programs"] if item["type"] == 1).update(physical=0, virtual=0)),
            ("object_size", lambda model: next(item for item in model["symbols"] if item["name"] == "s2b_smoke_buffer").update(size=BUFFER_SIZE - 4)),
            ("vector_entry", lambda model: model.update(entry=policy["buffer_begin"])),
        ]
        for name, mutate in mutations:
            model = copy.deepcopy(elf)
            mutate(model)
            try:
                validate_layout(model, policy, *texts)
            except ValueError:
                cases.append(name)
            else:
                raise ValueError(f"离线反例未被拒绝：{name}")
        for name, data in (("bad_magic", b"BAD!" + elf_bytes[4:]), ("truncated_elf", elf_bytes[:51])):
            try:
                parse_elf(data)
            except ValueError:
                cases.append(name)
            else:
                raise ValueError(f"ELF格式反例未被拒绝：{name}")
        for name, replacement in (("cacheline_changed", "const u32 cacheline = 64U;"),
                                  ("cacheline_missing", "const u32 altered = 32U;")):
            altered_cache = re.sub(r"const\s+u32\s+cacheline\s*=\s*32U\s*;", replacement, texts[4], count=1)
            try:
                verify_cache_contract(altered_cache)
            except ValueError:
                cases.append(name)
            else:
                raise ValueError(f"缓存范围实现反例未被拒绝：{name}")
        result["self_test"] = {"status": "PASS", "negative_cases_rejected": cases,
                               "positive_cases": 1, "arm_program_executed": False}
        init_cases = []
        for name, mutate in (
            ("init_load_in_ddr", lambda model: next(item for item in model["programs"] if item["type"] == 1).update(virtual=policy["ddr_begin"], physical=policy["ddr_begin"])),
            ("init_cpu1_reserved", lambda model: next(item for item in model["sections"] if item["name"] == ".stack").update(address=0xFFFFFE00)),
            ("init_ready_missing", lambda model: next(item for item in model["symbols"] if item["name"] == "s2b_ps_init_ready").update(name="missing_ready")),
        ):
            model = copy.deepcopy(init_elf)
            mutate(model)
            try:
                validate_initializer(model, manifest["init_policy"]["platform_memory_regions"], *init_texts, init_bytes)
            except ValueError:
                init_cases.append(name)
            else:
                raise ValueError(f"初始化布局反例未被拒绝：{name}")
        result["self_test"]["initializer_negative_cases_rejected"] = init_cases
    return result


def main() -> int:
    """只读输出JSON检查结果，不修改证据文件。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = check_manifest(args.manifest, args.self_test)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(json.dumps({"status": "FAIL_OFFLINE_LAYOUT", "error": str(error),
                          "hardware_execution": "NOT_RUN"}, ensure_ascii=False))
        sys.exit(1)
