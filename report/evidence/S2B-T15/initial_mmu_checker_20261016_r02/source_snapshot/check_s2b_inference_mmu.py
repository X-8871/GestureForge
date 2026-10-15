#!/usr/bin/env python3
"""核验推理ELF中的初始ARMv7短描述符MMU表及静态属性来源。"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
from typing import Any

from check_s2b_ps_smoke_layout import parse_elf, require


ARENA_BEGIN = 0x10000000
ARENA_END = 0x12000000
EXPECTED_CSR_BASE = 0x43C00000
SECTION_BYTES = 0x100000
L1_ENTRIES = 4096
L1_BYTES = L1_ENTRIES * 4
SECTION_TYPE_MASK = 0x3
SECTION_TYPE = 0x2
SUPERSECTION_BIT = 1 << 18
OUTPUT_BASE_MASK = 0xFFF00000
ATTRIBUTE_MASK = 0x000FFFFF


def _sha256(data: bytes) -> str:
    """计算输入原字节的SHA-256。"""
    return hashlib.sha256(data).hexdigest()


def _strip_c_comments(text: str) -> str:
    """删除C风格注释以避免注释文本影响静态匹配。"""
    return re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.DOTALL)


def _c_tokens(text: str) -> tuple[str, ...]:
    """将C语句转换成不受空白影响的词元序列。"""
    return tuple(re.findall(
        r"0[xX][0-9a-fA-F]+[uUlL]*|[A-Za-z_]\w*|[0-9]+[uUlL]*|"
        r"==|!=|<=|>=|\+=|-=|\*=|/=|&&|\|\||->|\+\+|--|[^\s]",
        text,
    ))


def _read_integer_macro(text: str, name: str) -> int:
    """读取唯一的整数宏，拒绝表达式、缺失与重复定义。"""
    clean = _strip_c_comments(text)
    matches = re.findall(
        rf"^\s*#\s*define\s+{re.escape(name)}\s+(0[xX][0-9a-fA-F]+|[0-9]+)[uUlL]*\s*$",
        clean,
        re.MULTILINE,
    )
    require(len(matches) == 1, f"BSP整数宏缺失、重复或非字面量：{name}")
    return int(matches[0], 0)


def _find_translation_compile_command(text: str) -> tuple[dict[str, Any], bool]:
    """从实际BSP编译数据库选出唯一translation_table.S命令。"""
    try:
        rows = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError(f"BSP编译命令JSON无效：{error}") from error
    require(isinstance(rows, list), "BSP编译命令必须是数组")
    matches = [row for row in rows if isinstance(row, dict) and
               str(row.get("file", "")).replace("\\", "/").rsplit("/", 1)[-1] == "translation_table.S"]
    require(len(matches) == 1, "BSP translation_table.S实际编译命令必须唯一")
    command = matches[0].get("command")
    require(isinstance(command, str) and command.strip(), "translation_table.S编译命令缺失")
    require(re.search(r"(?:^|\s)-mcpu=cortex-a9(?:\s|$)", command, re.IGNORECASE) is not None,
            "translation_table.S未按Cortex-A9目标编译")
    require(re.search(r"(?:^|\s)-D(?:\s+)?USE_AMP(?:=|\s|$)", command) is None,
            "translation_table.S编译命令启用了USE_AMP")
    sdt = re.search(r"(?:^|\s)-DSDT(?:=1)?(?:\s|$)", command) is not None
    return matches[0], sdt


def _selected_ddr_macros(text: str) -> tuple[int, int, str]:
    """按translation_table.S的宏优先级选择实际DDR地址宏。"""
    clean = _strip_c_comments(text)
    if re.search(r"^\s*#\s*define\s+USE_AMP\b", clean, re.MULTILINE):
        raise ValueError("实际BSP配置头启用了USE_AMP")
    base_name, high_name = "XPAR_PS7_DDR_0_S_AXI_BASEADDR", "XPAR_PS7_DDR_0_S_AXI_HIGHADDR"
    if not re.search(rf"^\s*#\s*define\s+{re.escape(base_name)}\b", clean, re.MULTILINE):
        base_name, high_name = "XPAR_PS7_DDR_0_BASEADDRESS", "XPAR_PS7_DDR_0_HIGHADDRESS"
    base = _read_integer_macro(text, base_name)
    high = _read_integer_macro(text, high_name)
    require(base == SECTION_BYTES, "translation_table.S首个DDR段必须从1MiB起始")
    require(high >= ARENA_END - 1 and high < 0x100000000, "实际BSP DDR宏未覆盖完整arena")
    require((high + 1 - base) % SECTION_BYTES == 0, "实际BSP DDR范围不是整数MiB")
    return base, high, f"{base_name}/{high_name}"


def _verify_translation_source(text: str, cache_attr: int) -> None:
    """核对本次实际BSP汇编源中的非AMP DDR段生成语义。"""
    clean = _strip_c_comments(text)
    require(len(re.findall(r"(?im)^\s*\.section\s+\.mmu_tbl\s*,\s*\"a\"\s*$", clean)) == 1,
            "translation_table.S必须唯一声明只读.mmu_tbl")
    require(len(re.findall(r"(?im)^\s*\.globl\s+MMUTable\s*$", clean)) == 1 and
            len(re.findall(r"(?im)^\s*MMUTable\s*:\s*$", clean)) == 1,
            "translation_table.S的MMUTable全局标签缺失或重复")
    require(re.search(
        r"(?im)^\s*#\s*include\s+\"bspconfig\.h\"\s*$", clean) is not None,
        "translation_table.S未包含实际BSP配置头")
    require(re.search(
        r"(?ims)^\s*#\s*ifndef\s+SDT\s*\n\s*#\s*include\s+\"xparameters\.h\"\s*\n"
        r"\s*#\s*else\s*\n\s*#\s*include\s+\"xmem_config\.h\"\s*\n\s*#\s*endif\b", clean),
        "translation_table.S的SDT/传统DDR头选择语义不受支持")
    require(re.search(
        r"(?ims)^\s*#\s*ifdef\s+XPAR_PS7_DDR_0_S_AXI_BASEADDR\s*\n"
        r"\s*\.set\s+DDR_START\s*,\s*XPAR_PS7_DDR_0_S_AXI_BASEADDR\s*\n"
        r"\s*\.set\s+DDR_END\s*,\s*XPAR_PS7_DDR_0_S_AXI_HIGHADDR\s*\n"
        r"\s*\.set\s+DDR_SIZE\s*,\s*\(DDR_END\s*-\s*DDR_START\)\s*\+\s*1\s*\n"
        r"\s*\.set\s+DDR_REG\s*,\s*DDR_SIZE\s*/\s*0x100000\s*\n"
        r"\s*#\s*elif\s+defined\s*\(\s*XPAR_PS7_DDR_0_BASEADDRESS\s*\)\s*\n"
        r"\s*\.set\s+DDR_START\s*,\s*XPAR_PS7_DDR_0_BASEADDRESS\s*\n"
        r"\s*\.set\s+DDR_END\s*,\s*XPAR_PS7_DDR_0_HIGHADDRESS\s*\n"
        r"\s*\.set\s+DDR_SIZE\s*,\s*\(DDR_END\s*-\s*DDR_START\)\s*\+\s*1\s*\n"
        r"\s*\.set\s+DDR_REG\s*,\s*DDR_SIZE\s*/\s*0x100000\s*\n"
        r"\s*#\s*else\s*\n\s*\.set\s+DDR_REG\s*,\s*0\s*\n\s*#\s*endif\b", clean),
        "translation_table.S DDR范围到1MiB重复数的生成逻辑不受支持")

    branches = re.findall(
        r"(?ims)^\s*#\s*ifndef\s+USE_AMP\s*(.*?)^\s*#\s*else\s*(.*?)^\s*#\s*endif\b",
        clean,
    )
    require(len(branches) == 1, "translation_table.S非AMP属性分支缺失、重复或结构不受支持")
    non_amp, _amp = branches[0]

    def word_attributes(body: str) -> list[int]:
        return [int(value, 0) for value in re.findall(
            r"(?im)^\s*\.word\s+SECT\s*\+\s*(0[xX][0-9a-fA-F]+)\s*$", body)]

    require(word_attributes(non_amp) == [cache_attr],
            "translation_table.S非AMP首段属性与实际NORM_WB_CACHE不符")
    ddr_blocks = re.findall(r"(?ims)^\s*\.rept\s+DDR_REG\b(.*?)^\s*\.endr\b", clean)
    require(len(ddr_blocks) == 1 and word_attributes(ddr_blocks[0]) == [cache_attr],
            "translation_table.S DDR重复段未使用实际NORM_WB_CACHE")
    require(re.search(r"(?im)^\s*\.set\s+DDR_REG\s*,\s*DDR_SIZE\s*/\s*0x100000\s*$", clean),
            "translation_table.S DDR_REG不再按1MiB段计数")
    require(re.search(r"(?im)^\s*\.set\s+SECT\s*,\s*0\s*$", clean),
            "translation_table.S首段虚拟地址不再从零开始")
    require(re.search(r"(?im)^\s*\.set\s+SECT\s*,\s*SECT\s*\+\s*0x100000\s*$", clean),
            "translation_table.S缺少1MiB段地址递增")


def _verify_runtime_update_boundary(app_source: str, app_preprocessed: str,
                                   xil_mmu_source: str, device_attr: int) -> dict[str, Any]:
    """限定核对当前PS应用CSR属性更新的单段静态影响范围。"""
    app_clean = _strip_c_comments(app_source)
    app_pre = _strip_c_comments(app_preprocessed)
    app_pre = re.sub(r"(?m)^\s*#\s*\d+[^\n]*$", "", app_pre)
    define = re.findall(r"(?im)^\s*#\s*define\s+CSR_BASE\s+(0[xX][0-9a-fA-F]+|[0-9]+)[uUlL]*\s*$",
                        app_clean)
    require(len(define) == 1, "PS应用CSR_BASE缺失、重复或非字面量")
    csr_base = int(define[0], 0)
    require(csr_base == EXPECTED_CSR_BASE,
            f"PS应用CSR_BASE必须等于冻结地址{EXPECTED_CSR_BASE:#010x}")
    calls = re.findall(r"\bXil_SetTlbAttributes\s*\(", app_clean)
    require(len(calls) == 1 and re.search(
        r"\bXil_SetTlbAttributes\s*\(\s*\(INTPTR\)\s*CSR_BASE\s*,\s*DEVICE_MEMORY\s*\)", app_clean),
        "PS应用必须只有一处明确CSR_BASE/DEVICE_MEMORY更新调用")
    require(not re.search(r"\b(?:MMUTable|TTBR[0-1]|Xil_MemMap|Xil_EnableMMU|Xil_DisableMMU)\b|\bmcr\b",
                          app_clean, re.IGNORECASE), "PS应用含未审计的其他显式MMU修改入口")
    expanded = re.findall(
        r"\bXil_SetTlbAttributes\s*\(\s*\(INTPTR\)\s*(0[xX][0-9a-fA-F]+|[0-9]+)[uUlL]*\s*,\s*(0[xX][0-9a-fA-F]+|[0-9]+)[uUlL]*\s*\)",
        app_pre,
    )
    require(len(expanded) == 1 and tuple(int(item, 0) for item in expanded[0]) ==
            (csr_base, device_attr), "实际预处理应用未唯一展开预期CSR地址与DEVICE_MEMORY值")

    source = _strip_c_comments(xil_mmu_source)
    definitions = list(re.finditer(r"\bXil_SetTlbAttributes\s*\([^;{}]*\)\s*\{", source))
    require(len(definitions) == 1, "实际BSP Xil_SetTlbAttributes函数定义缺失或重复")
    opening = definitions[0].end() - 1
    depth, cursor = 1, opening + 1
    while cursor < len(source) and depth:
        depth += (source[cursor] == "{") - (source[cursor] == "}")
        cursor += 1
    require(depth == 0, "实际BSP Xil_SetTlbAttributes函数体截断")
    body = source[opening + 1:cursor - 1]
    expected_body = """
        u32 *ptr;
        u32 section;
        section = Addr / 0x100000U;
        ptr = &MMUTable;
        ptr += section;
        if (ptr != NULL) {
            *ptr = (Addr & 0xFFF00000U) | attrib;
        }
        Xil_DCacheFlush();
        mtcp(XREG_CP15_INVAL_UTLB_UNLOCKED, 0U);
        mtcp(XREG_CP15_INVAL_BRANCH_ARRAY, 0U);
        dsb();
        isb();
    """
    require(_c_tokens(body) == _c_tokens(expected_body),
            "实际BSP Xil_SetTlbAttributes完整函数体不匹配受支持的单项L1更新语义")
    require(csr_base % SECTION_BYTES == 0, "CSR_BASE未按1MiB边界对齐")
    csr_section = csr_base // SECTION_BYTES
    arena_first, arena_last = ARENA_BEGIN // SECTION_BYTES, ARENA_END // SECTION_BYTES
    require(not arena_first <= csr_section < arena_last, "CSR属性更新影响范围与arena重叠")
    return {
        "source_call_count": 1,
        "preprocessed_call_count": 1,
        "csr_base": csr_base,
        "csr_section_index": csr_section,
        "device_memory_attribute": device_attr,
        "updated_l1_entry_count_per_call": 1,
        "updated_virtual_range": [csr_section * SECTION_BYTES, (csr_section + 1) * SECTION_BYTES],
        "arena_overlap": False,
        "claim_scope": "仅为静态源代码与预处理文本核对；未证明调用已执行或运行后页表状态",
    }


def verify_mmu_table(elf_bytes: bytes, parsed_elf: dict[str, Any], *,
                     xil_mmu_header: str, translation_table: str,
                     bsp_config_header: str, ddr_config_header: str,
                     xparameters_header: str, bsp_compile_commands: str, app_source: str,
                     app_preprocessed: str, xil_mmu_source: str,
                     link_map: str) -> dict[str, Any]:
    """从实际ELF字节与同次parse_elf结果核验初始CPU0短描述符表。"""
    require(isinstance(elf_bytes, bytes) and len(elf_bytes) >= 52, "ELF原字节缺失或过短")
    require(isinstance(parsed_elf, dict), "现有parse_elf结果类型无效")
    sections = parsed_elf.get("sections")
    symbols = parsed_elf.get("symbols")
    require(isinstance(sections, list) and isinstance(symbols, list), "parse_elf未返回节表/符号表")
    mmu_sections = [item for item in sections if isinstance(item, dict) and item.get("name") == ".mmu_tbl"]
    require(len(mmu_sections) == 1, ".mmu_tbl节必须唯一")
    section = mmu_sections[0]
    require(section.get("type") == 1 and section.get("flags", 0) & 2,
            ".mmu_tbl必须是文件支持的ALLOC节")
    require(section.get("size") == L1_BYTES, ".mmu_tbl必须恰为4096项/16KiB")
    require(section.get("address", -1) % L1_BYTES == 0, ".mmu_tbl起始地址未按16KiB对齐")
    offset = section.get("offset")
    require(type(offset) is int and 0 <= offset and offset + L1_BYTES <= len(elf_bytes),
            ".mmu_tbl ELF原字节范围被截断")
    table_symbols = [item for item in symbols if isinstance(item, dict) and item.get("name") == "MMUTable"]
    require(len(table_symbols) == 1, "MMUTable符号必须唯一")
    symbol = table_symbols[0]
    require(symbol.get("section") == section.get("index") and symbol.get("value") == section.get("address"),
            "MMUTable符号未精确指向唯一.mmu_tbl起始")

    cache_attr = _read_integer_macro(xil_mmu_header, "NORM_WB_CACHE")
    device_attr = _read_integer_macro(xil_mmu_header, "DEVICE_MEMORY")
    require(cache_attr & OUTPUT_BASE_MASK == 0 and cache_attr & SECTION_TYPE_MASK == SECTION_TYPE and
            not cache_attr & SUPERSECTION_BIT,
            "实际NORM_WB_CACHE宏不能作为ARMv7普通1MiB section属性")
    command, sdt = _find_translation_compile_command(bsp_compile_commands)
    config_header = ddr_config_header if sdt else xparameters_header
    require(re.search(r"^\s*#\s*define\s+USE_AMP\b", _strip_c_comments(bsp_config_header), re.MULTILINE) is None,
            "实际BSP配置头启用了USE_AMP")
    require(re.search(r"^\s*#\s*define\s+USE_AMP\b", _strip_c_comments(xparameters_header), re.MULTILINE) is None,
            "实际xparameters.h启用了USE_AMP")
    require(re.search(r"^\s*#\s*define\s+USE_AMP\b", _strip_c_comments(ddr_config_header), re.MULTILINE) is None,
            "实际xmem_config.h启用了USE_AMP")
    ddr_begin, ddr_high, ddr_macro_names = _selected_ddr_macros(config_header)
    require(ARENA_BEGIN >= ddr_begin and ARENA_END - 1 <= ddr_high,
            "实际translation_table.S使用的DDR宏未覆盖完整arena")
    _verify_translation_source(translation_table, cache_attr)

    words = struct.unpack_from("<4096I", elf_bytes, offset)
    fault_count = 0
    section_count = 0
    unsupported: list[dict[str, int]] = []
    arena_aliases: list[dict[str, int]] = []
    for virtual_index, descriptor in enumerate(words):
        kind = descriptor & SECTION_TYPE_MASK
        if kind == 0:
            fault_count += 1
            continue
        if kind == 1:
            unsupported.append({"virtual_index": virtual_index, "descriptor": descriptor, "kind": kind})
            continue
        if kind == 3:
            unsupported.append({"virtual_index": virtual_index, "descriptor": descriptor,
                                "kind": "type_11_pxn_feature_not_bound"})
            continue
        section_count += 1
        if descriptor & SUPERSECTION_BIT:
            unsupported.append({"virtual_index": virtual_index, "descriptor": descriptor, "kind": "supersection"})
            continue
        physical_base = descriptor & OUTPUT_BASE_MASK
        if ARENA_BEGIN <= physical_base < ARENA_END and physical_base != virtual_index * SECTION_BYTES:
            arena_aliases.append({"virtual_index": virtual_index, "physical_base": physical_base,
                                  "descriptor": descriptor})
    require(not unsupported, f"L1表含不支持的coarse/type-11/supersection描述符：{unsupported[:4]}")
    require(not arena_aliases, f"L1表将arena物理段映射到非identity虚拟段：{arena_aliases[:4]}")

    arena_first, arena_last = ARENA_BEGIN // SECTION_BYTES, ARENA_END // SECTION_BYTES
    arena_mappings = []
    for virtual_index in range(arena_first, arena_last):
        descriptor = words[virtual_index]
        require(descriptor & SECTION_TYPE_MASK == SECTION_TYPE,
                f"arena虚拟段{virtual_index:#x}不是普通section描述符")
        require(not descriptor & SUPERSECTION_BIT,
                f"arena虚拟段{virtual_index:#x}使用不支持的supersection")
        require(descriptor & OUTPUT_BASE_MASK == virtual_index * SECTION_BYTES,
                f"arena虚拟段{virtual_index:#x}不是identity映射")
        require(descriptor & ATTRIBUTE_MASK == cache_attr,
                f"arena虚拟段{virtual_index:#x}属性不匹配实际NORM_WB_CACHE")
        arena_mappings.append({"virtual_base": virtual_index * SECTION_BYTES,
                               "physical_base": descriptor & OUTPUT_BASE_MASK,
                               "descriptor": descriptor,
                               "attribute_bits": descriptor & ATTRIBUTE_MASK})

    output_map_rows = [line for line in link_map.splitlines()
                       if re.match(r"^\.mmu_tbl\s+", line)]
    require(len(output_map_rows) == 1, "链接map中的.mmu_tbl输出节必须唯一")
    output_match = re.match(
        r"^\.mmu_tbl\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)(?:\s+.*)?$",
        output_map_rows[0],
    )
    require(output_match is not None, "链接map中的.mmu_tbl输出节地址/大小格式无效")
    output_address, output_size = (int(output_match.group(index), 0) for index in (1, 2))
    require(output_address == section["address"] and output_size == section["size"],
            "链接map输出.mmu_tbl的起始地址/大小与实际ELF节不一致")

    map_rows = [line for line in link_map.splitlines()
                if re.match(r"^\s+\.mmu_tbl\s+", line)]
    require(len(map_rows) == 1, "链接map中的.mmu_tbl输入节必须唯一")
    map_match = re.match(
        r"^\s*\.mmu_tbl\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)\s+"
        r"(.+translation_table\.S\.obj)\)?\s*$",
        map_rows[0],
    )
    require(map_match is not None,
            "链接map未将.mmu_tbl唯一绑定到translation_table.S.obj")
    map_address, map_size = (int(map_match.group(index), 0) for index in (1, 2))
    require(map_address == section["address"] and map_size == section["size"],
            "链接map中的.mmu_tbl起始地址/大小与实际ELF节不一致")
    symbol_rows = [line for line in link_map.splitlines() if re.search(r"\bMMUTable\s*$", line)]
    require(len(symbol_rows) == 1 and re.search(
        rf"\b0x{section['address']:08x}\s+MMUTable\s*$", symbol_rows[0], re.IGNORECASE),
        "链接map中的MMUTable地址不唯一或与实际ELF不同")
    runtime_update = _verify_runtime_update_boundary(
        app_source, app_preprocessed, xil_mmu_source, device_attr)
    require(command.get("file") is not None, "BSP编译命令缺少源文件绑定")

    return {
        "schema_version": 1,
        "status": "PASS_STATIC_INITIAL_MMU_TABLE",
        "scope": "仅核验本次infer.elf中的初始CPU0 ARMv7短描述符L1表及已列明静态源代码",
        "hardware_execution": "NOT_RUN",
        "g0_effect": "NONE",
        "elf_sha256": _sha256(elf_bytes),
        "table_sha256": _sha256(elf_bytes[offset:offset + L1_BYTES]),
        "section": {"index": section["index"], "address": section["address"], "offset": offset,
                    "size_bytes": L1_BYTES, "entry_count": L1_ENTRIES,
                    "address_alignment_bytes": L1_BYTES, "elf_section_alignment": section["align"],
                    "MMUTable_symbol_value": symbol["value"]},
        "architecture": "ARMv7-A Cortex-A9",
        "descriptor_format": "ARMv7 short-descriptor first-level 1MiB section",
        "descriptor_counts": {"fault": fault_count, "section": section_count,
                              "unsupported": len(unsupported)},
        "arena": {"virtual_begin": ARENA_BEGIN, "virtual_end_exclusive": ARENA_END,
                  "section_count": arena_last - arena_first,
                  "identity_cacheable_mappings": arena_mappings,
                  "physical_alias_count": len(arena_aliases),
                  "alias_scan_l1_entry_count": L1_ENTRIES},
        "bsp_attributes": {"macro": "NORM_WB_CACHE", "value": cache_attr,
                           "device_memory_macro_value": device_attr,
                           "ddr_macros": ddr_macro_names, "ddr_begin": ddr_begin,
                           "ddr_end_inclusive": _read_integer_macro(config_header, ddr_macro_names.split("/")[1]),
                           "non_amp_compile": True, "translation_table_source_sha256": _sha256(translation_table.encode("utf-8")),
                           "xil_mmu_header_sha256": _sha256(xil_mmu_header.encode("utf-8")),
                           "bsp_config_header_sha256": _sha256(bsp_config_header.encode("utf-8")),
                           "xparameters_header_sha256": _sha256(xparameters_header.encode("utf-8")),
                           "xmem_config_header_sha256": _sha256(ddr_config_header.encode("utf-8")),
                           "active_ddr_config_header_sha256": _sha256(config_header.encode("utf-8")),
                           "bsp_compile_commands_sha256": _sha256(bsp_compile_commands.encode("utf-8")),
                           "app_source_sha256": _sha256(app_source.encode("utf-8")),
                           "app_preprocessed_sha256": _sha256(app_preprocessed.encode("utf-8")),
                           "xil_mmu_source_sha256": _sha256(xil_mmu_source.encode("utf-8")),
                           "link_map_sha256": _sha256(link_map.encode("utf-8"))},
        "runtime_static_update": runtime_update,
        "link_map_translation_table_section": map_rows[0].strip(),
        "link_map_translation_table_address": map_address,
        "link_map_translation_table_size": map_size,
        "link_map_output_translation_table_address": output_address,
        "link_map_output_translation_table_size": output_size,
        "limitations": [
            "只证明链接ELF中的初始CPU0 L1表字节，不证明调用启动代码后或运行中的实际页表状态。",
            "仅扫描4096个L1项；coarse/L2、supersection及未绑定PXN能力的type-11均失败关闭，不推断CPU1独立表或实板HP0可见性。",
            "CSR属性更新仅按当前应用预处理代码和BSP函数静态推导其单个1MiB表项范围，不证明该调用已执行。",
        ],
    }


def main() -> int:
    """提供对已生成推理ELF的独立只读命令行入口。"""
    parser = argparse.ArgumentParser(description="核验推理ELF初始MMU表")
    for option in ("elf", "xil-mmu-header", "translation-table", "bsp-config-header",
                   "ddr-config-header", "xparameters-header", "bsp-compile-commands", "app-source",
                   "app-preprocessed", "xil-mmu-source", "link-map"):
        parser.add_argument("--" + option, required=True)
    args = parser.parse_args()
    values = vars(args)
    elf_path = Path(values.pop("elf"))
    elf_bytes = elf_path.read_bytes()
    parsed = parse_elf(elf_bytes)
    texts = {key.replace("-", "_"): Path(value).read_bytes().decode("utf-8")
             for key, value in values.items()}
    report = verify_mmu_table(elf_bytes, parsed, **texts)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
