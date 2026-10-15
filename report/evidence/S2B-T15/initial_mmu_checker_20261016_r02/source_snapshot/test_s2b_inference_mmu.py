#!/usr/bin/env python3
"""用小型合成ELF覆盖初始MMU检查器的正例与失败关闭路径。"""

from __future__ import annotations

import json
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_s2b_inference_mmu import verify_mmu_table
from check_s2b_ps_smoke_layout import parse_elf


NORM_WB_CACHE = 0x15DE6
DEVICE_MEMORY = 0xC06
ARENA_FIRST = 0x100
ARENA_LAST = 0x120
OUTPUT_BASE_MASK = 0xFFF00000

HEADER = """#define NORM_WB_CACHE 0x15DE6
#define DEVICE_MEMORY 0xC06
"""

TRANSLATION_TABLE = """#include "bspconfig.h"
#ifndef SDT
#include "xparameters.h"
#else
#include "xmem_config.h"
#endif
.globl MMUTable
.section .mmu_tbl,"a"
MMUTable:
.set SECT, 0
#ifdef XPAR_PS7_DDR_0_S_AXI_BASEADDR
.set DDR_START, XPAR_PS7_DDR_0_S_AXI_BASEADDR
.set DDR_END, XPAR_PS7_DDR_0_S_AXI_HIGHADDR
.set DDR_SIZE, (DDR_END - DDR_START)+1
.set DDR_REG, DDR_SIZE/0x100000
#elif defined(XPAR_PS7_DDR_0_BASEADDRESS)
.set DDR_START, XPAR_PS7_DDR_0_BASEADDRESS
.set DDR_END, XPAR_PS7_DDR_0_HIGHADDRESS
.set DDR_SIZE, (DDR_END - DDR_START)+1
.set DDR_REG, DDR_SIZE/0x100000
#else
.set DDR_REG, 0
#endif
#ifndef USE_AMP
.word SECT + 0x15de6
#else
.word SECT + 0x14de6
#endif
.set SECT, SECT+0x100000
.rept DDR_REG
.word SECT + 0x15de6
.set SECT, SECT+0x100000
.endr
"""

XMEM_CONFIG = """#define XPAR_PS7_DDR_0_BASEADDRESS 0x100000
#define XPAR_PS7_DDR_0_HIGHADDRESS 0x3fffffff
"""

XPARAMETERS = """#define XPAR_PS7_DDR_0_BASEADDRESS 0x100000
#define XPAR_PS7_DDR_0_HIGHADDRESS 0x3fffffff
"""

BSP_CONFIG = """#define BSPCONFIG_H
"""

COMPILE_COMMANDS = json.dumps([{
    "file": "C:\\bsp\\translation_table.S",
    "command": "arm-none-eabi-gcc -DSDT -mcpu=cortex-a9 -c translation_table.S",
}])

APP_SOURCE = """#define CSR_BASE 0x43C00000U
void initialise(void) {
    Xil_SetTlbAttributes((INTPTR)CSR_BASE, DEVICE_MEMORY);
}
"""

APP_PREPROCESSED = """# 40 \"s2b_inference_app.c\"
Xil_SetTlbAttributes((INTPTR)0x43C00000U,
                     0xC06);
"""

XIL_MMU_SOURCE = """void Xil_SetTlbAttributes(INTPTR Addr, u32 attrib)
{
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
}
"""

LINK_MAP = """.mmu_tbl        0x00110000     0x4000
                0x00110000                __mmu_tbl_start = .
 *(.mmu_tbl)
 .mmu_tbl       0x00110000     0x4000 C:/bsp/libxilstandalone.a(translation_table.S.obj)
                0x00110000                MMUTable
                0x00114000                __mmu_tbl_end = .
"""


def build_table(changes: dict[int, int] | None = None) -> bytes:
    """生成符合目标DDR布局的L1表并应用单项负例覆盖。"""
    words = [0] * 4096
    words[0] = NORM_WB_CACHE
    for index in range(1, 0x400):
        words[index] = index * 0x100000 | NORM_WB_CACHE
    if changes:
        for index, value in changes.items():
            words[index] = value
    return struct.pack("<4096I", *words)


def build_elf(table: bytes, duplicate_section: bool = False) -> bytes:
    """封裝最小可由正式ELF32解析器接受的ARM ELF。"""
    if len(table) != 0x4000:
        raise ValueError("测试表长度必须为16KiB")
    data_offset = 84
    data = bytearray(b"\0" * data_offset)
    data[:7] = b"\x7fELF\x01\x01\x01"
    data.extend(table)
    shstr = b"\0.mmu_tbl\0.shstrtab\0.strtab\0.symtab\0"
    shstr_offset = len(data)
    data.extend(shstr)
    strtab = b"\0MMUTable\0"
    strtab_offset = len(data)
    data.extend(strtab)
    symtab_offset = len(data)
    data.extend(b"\0" * 16)
    data.extend(struct.pack("<IIIBBH", 1, 0x00110000, 0, 0, 0, 1))
    shoff = len(data)
    shnum = 6 if duplicate_section else 5
    data.extend(b"\0" * (shnum * 40))
    sections = [
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (1, 1, 2, 0x00110000, data_offset, 0x4000, 0, 0, 1, 0),
        (10, 3, 0, 0, shstr_offset, len(shstr), 0, 0, 1, 0),
        (20, 3, 0, 0, strtab_offset, len(strtab), 0, 0, 1, 0),
        (28, 2, 0, 0, symtab_offset, 32, 3, 1, 4, 16),
    ]
    if duplicate_section:
        sections.append((1, 1, 2, 0x00110000, data_offset, 0x4000, 0, 0, 1, 0))
    for index, section in enumerate(sections):
        struct.pack_into("<IIIIIIIIII", data, shoff + index * 40, *section)
    struct.pack_into("<IIIIIIII", data, 52, 1, 0, 0x00100000, 0x00100000, 0, 0, 5, 4)
    struct.pack_into("<HHIIIIIHHHHHH", data, 16, 2, 40, 1, 0x00100000, 52, shoff,
                     0, 52, 32, 1, 40, shnum, 2)
    return bytes(data)


def run_check(table: bytes, *, source: str = TRANSLATION_TABLE,
              commands: str = COMPILE_COMMANDS, app: str = APP_SOURCE,
              app_preprocessed: str = APP_PREPROCESSED,
              xil_mmu_source: str = XIL_MMU_SOURCE, link_map: str = LINK_MAP,
              xparameters: str = XPARAMETERS, ddr_config: str = XMEM_CONFIG,
              duplicate_section: bool = False) -> dict:
    """调用生产检查器，输入与输出均来自合成ELF字节。"""
    elf = build_elf(table, duplicate_section=duplicate_section)
    parsed = parse_elf(elf)
    return verify_mmu_table(
        elf, parsed,
        xil_mmu_header=HEADER,
        translation_table=source,
        bsp_config_header=BSP_CONFIG,
        ddr_config_header=ddr_config,
        xparameters_header=xparameters,
        bsp_compile_commands=commands,
        app_source=app,
        app_preprocessed=app_preprocessed,
        xil_mmu_source=xil_mmu_source,
        link_map=link_map,
    )


class InferenceMmuChecks(unittest.TestCase):
    """验证目标属性、identity映射、别名检测与不支持表型阻断。"""

    def test_valid_initial_table_and_csr_boundary(self):
        report = run_check(build_table())
        self.assertEqual(report["status"], "PASS_STATIC_INITIAL_MMU_TABLE")
        self.assertEqual(report["arena"]["section_count"], 32)
        self.assertEqual(report["arena"]["physical_alias_count"], 0)
        self.assertEqual(report["arena"]["identity_cacheable_mappings"][0]["attribute_bits"], NORM_WB_CACHE)
        self.assertEqual(report["runtime_static_update"]["csr_section_index"], 0x43C)
        self.assertFalse(report["runtime_static_update"]["arena_overlap"])

    def test_legacy_build_selects_xparameters_ddr_macros(self):
        commands = json.dumps([{"file": "translation_table.S", "command": "arm-none-eabi-gcc -mcpu=cortex-a9 -c translation_table.S"}])
        report = run_check(build_table(), commands=commands,
                           ddr_config="#define XPAR_PS7_DDR_0_BASEADDRESS 0x100000\n#define XPAR_PS7_DDR_0_HIGHADDRESS 0x0fffffff\n")
        self.assertEqual(report["arena"]["section_count"], 32)

    def test_rejects_nonidentity_arena_alias(self):
        with self.assertRaisesRegex(ValueError, "非identity"):
            run_check(build_table({0x200: 0x10000000 | NORM_WB_CACHE}))

    def test_rejects_cache_attribute_mismatch(self):
        with self.assertRaisesRegex(ValueError, "NORM_WB_CACHE"):
            run_check(build_table({ARENA_FIRST: ARENA_FIRST * 0x100000 | 0x16DEA}))

    def test_rejects_missing_arena_mapping(self):
        with self.assertRaisesRegex(ValueError, "普通section"):
            run_check(build_table({ARENA_FIRST: 0}))

    def test_rejects_coarse_descriptor_anywhere(self):
        with self.assertRaisesRegex(ValueError, "coarse/type-11"):
            run_check(build_table({0x300: 0x00100001}))

    def test_rejects_supersection_anywhere(self):
        with self.assertRaisesRegex(ValueError, "supersection"):
            run_check(build_table({0x300: 0x300000 | NORM_WB_CACHE | (1 << 18)}))

    def test_rejects_unqualified_type_11_descriptor_anywhere(self):
        with self.assertRaisesRegex(ValueError, "coarse/type-11"):
            run_check(build_table({0x300: 3}))

    def test_rejects_amp_compile_definition(self):
        commands = json.dumps([{"file": "translation_table.S", "command": "gcc -DSDT -mcpu=cortex-a9 -DUSE_AMP -c translation_table.S"}])
        with self.assertRaisesRegex(ValueError, "USE_AMP"):
            run_check(build_table(), commands=commands)

    def test_rejects_translation_attribute_drift(self):
        source = TRANSLATION_TABLE.replace("0x15de6", "0x16de6")
        with self.assertRaisesRegex(ValueError, "NORM_WB_CACHE"):
            run_check(build_table(), source=source)

    def test_rejects_additional_runtime_mmu_entrypoint(self):
        app = APP_SOURCE + "void extra(void) { Xil_EnableMMU(); }\n"
        with self.assertRaisesRegex(ValueError, "其他显式MMU"):
            run_check(build_table(), app=app)

    def test_rejects_changed_csr_base_even_when_preprocessing_agrees(self):
        app = APP_SOURCE.replace("0x43C00000U", "0x44C00000U")
        preprocessed = APP_PREPROCESSED.replace("0x43C00000U", "0x44C00000U")
        with self.assertRaisesRegex(ValueError, "必须等于冻结地址"):
            run_check(build_table(), app=app, app_preprocessed=preprocessed)

    def test_rejects_negative_index_runtime_table_write(self):
        source = XIL_MMU_SOURCE.replace(
            "        *ptr =",
            "        ptr[-0x33C] = 0;\n        *ptr =",
        )
        with self.assertRaisesRegex(ValueError, "完整函数体"):
            run_check(build_table(), xil_mmu_source=source)

    def test_rejects_indexed_runtime_table_write(self):
        source = XIL_MMU_SOURCE.replace(
            "        *ptr =",
            "        ptr[index] = 0;\n        *ptr =",
        )
        with self.assertRaisesRegex(ValueError, "完整函数体"):
            run_check(build_table(), xil_mmu_source=source)

    def test_rejects_alias_runtime_table_write(self):
        source = XIL_MMU_SOURCE.replace(
            "        *ptr =",
            "        u32 *alias = ptr - 0x33C;\n        *alias = 0;\n        *ptr =",
        )
        with self.assertRaisesRegex(ValueError, "完整函数体"):
            run_check(build_table(), xil_mmu_source=source)

    def test_rejects_link_map_section_address_drift(self):
        link_map = LINK_MAP.replace(".mmu_tbl       0x00110000", ".mmu_tbl       0x00120000")
        with self.assertRaisesRegex(ValueError, "起始地址/大小与实际ELF节不一致"):
            run_check(build_table(), link_map=link_map)

    def test_rejects_link_map_output_section_address_drift(self):
        link_map = LINK_MAP.replace(".mmu_tbl        0x00110000", ".mmu_tbl        0x00120000")
        with self.assertRaisesRegex(ValueError, "输出.mmu_tbl的起始地址/大小"):
            run_check(build_table(), link_map=link_map)

    def test_rejects_link_map_section_size_drift(self):
        link_map = LINK_MAP.replace(
            "0x00110000     0x4000 C:/bsp/libxilstandalone.a(translation_table.S.obj)",
            "0x00110000     0x3000 C:/bsp/libxilstandalone.a(translation_table.S.obj)",
        )
        with self.assertRaisesRegex(ValueError, "起始地址/大小与实际ELF节不一致"):
            run_check(build_table(), link_map=link_map)

    def test_rejects_link_map_wrong_translation_table_object(self):
        link_map = LINK_MAP.replace("translation_table.S.obj", "other_table.S.obj")
        with self.assertRaisesRegex(ValueError, "唯一绑定到translation_table.S.obj"):
            run_check(build_table(), link_map=link_map)

    def test_rejects_duplicate_mmu_section_in_elf(self):
        with self.assertRaisesRegex(ValueError, "必须唯一"):
            run_check(build_table(), duplicate_section=True)

    def test_rejects_truncated_elf(self):
        elf = build_elf(build_table())
        with self.assertRaisesRegex(ValueError, "被截断"):
            parse_elf(elf[:-20])


if __name__ == "__main__":
    unittest.main()
