"""离线构建隔离的Cortex-A9 BRESP诊断ELF并封存静态产物。"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "cpu_bresp_diag_ocm_20261019_r01"
EVIDENCE = ROOT / "report" / "evidence" / "S2B-T20" / RUN_ID
WORK = ROOT / "tmp" / "2B" / "S2B-T20" / RUN_ID
ARTIFACTS = ROOT / "report" / "evidence" / "S2B-T15" / "qualification_r04_xsa_rebuild_20261016_r04_artifacts"
R07_DEPLOYMENT = ROOT / "report" / "evidence" / "S2B-T18" / "formal_csr_recovery_20261019_r07_deployment"
VITIS_ROOT = Path(r"D:\Xilinx\2026.1\Vitis")
TOOL_ROOT = VITIS_ROOT / "gnu" / "aarch32" / "nt" / "gcc-arm-none-eabi" / "bin"
LOW_OCM_BEGIN = 0x00000000
LOW_OCM_END = 0x00030000
CODE_BEGIN = 0x0000C000
CODE_END = 0x00010000
TTB_BEGIN = 0x00010000
TTB_END = 0x00014000
STACK_BEGIN = 0x0002C000
STACK_END = 0x0002D000
MAILBOX_BEGIN = 0x0002E000
MAILBOX_END = 0x0002F000
CSR_BASE = 0x43C00000
CPU1_PARK_PC = 0xFFFFFF34
EXPECTED_INIT_SHA = "237dd959f903589c657b743ea1fce175628aaa24020384058fc66339c779e7b1"
EXPECTED_APP_SHA = "a51499895e9387a74db87a3267843b9fbf7fdfa8b6646fcbc5db01485e090bf8"
EXPECTED_XSA_SHA = "ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6"
EXPECTED_BIT_SHA = "555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def exact_file(path: Path) -> Path:
    require(path.is_file(), f"缺少精确输入文件：{path}")
    return path.resolve(strict=True)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def run_command(command: list[str], log_path: Path, commands: list[dict[str, object]]) -> str:
    completed = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8", errors="replace",
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    log_path.write_text(completed.stdout, encoding="utf-8", newline="\n")
    commands.append({"command": command, "cwd": str(ROOT), "log": str(log_path), "exit_code": completed.returncode})
    require(completed.returncode == 0, f"离线工具退出{completed.returncode}：{command[0]}；详见{log_path}")
    return completed.stdout


def load_and_validate_layout() -> dict[str, object]:
    layout_path = exact_file(ARTIFACTS / "init_elf_layout.json")
    layout = json.loads(layout_path.read_text(encoding="utf-8"))
    require(layout.get("entry") == 0, "已有init ELF入口不在低OCM基址")
    programs = [item for item in layout.get("programs", []) if item.get("type") == 1 and item.get("memory_size", 0)]
    require(len(programs) == 2, "已有init ELF的OCM PT_LOAD数量不符合R04冻结布局")
    low = next((item for item in programs if item["physical"] == 0), None)
    high = next((item for item in programs if item["physical"] == 0xFFFF0000), None)
    require(low is not None and high is not None, "已有init ELF未同时绑定低OCM与高OCM栈")
    low_end = int(low["physical"]) + int(low["memory_size"])
    high_end = int(high["physical"]) + int(high["memory_size"])
    require(low_end == 0xB210, f"init ELF低OCM实际结束地址变化：0x{low_end:08x}")
    require(high_end == 0xFFFFD400, f"init ELF高OCM栈结束地址变化：0x{high_end:08x}")
    require(low_end <= CODE_BEGIN < CODE_END == TTB_BEGIN < TTB_END <= STACK_BEGIN < STACK_END < MAILBOX_BEGIN < MAILBOX_END <= LOW_OCM_END,
            "隔离代码、栈、mailbox的低OCM范围重叠或越界")
    return {"layout_path": str(layout_path), "layout_sha256": sha256(layout_path),
            "low_pt_load": low, "high_pt_load": high, "low_end_exclusive": low_end,
            "diagnostic_code_range": [CODE_BEGIN, CODE_END], "diagnostic_stack_range": [STACK_BEGIN, STACK_END],
            "mailbox_range": [MAILBOX_BEGIN, MAILBOX_END]}


def validate_cpu1_and_ocm() -> dict[str, object]:
    result_path = exact_file(R07_DEPLOYMENT / "jtag_result.json")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    before = result.get("system_reset", {}).get("before", {})
    after = result.get("system_reset", {}).get("after", {})
    require(before.get("ocm_cfg") == 24 and after.get("ocm_cfg") == 24,
            "R07记录的OCM_CFG不等于0x18，低/高bank映射证据不一致")
    require(before.get("cpu1_pc") == CPU1_PARK_PC and after.get("cpu1_pc") == CPU1_PARK_PC,
            "R07记录CPU1停核PC变化或落入未知位置")
    cpu1 = result.get("targets", {}).get("ARM Cortex-A9 MPCore #1", {})
    require(cpu1.get("state_reason") == "Suspended", "R07记录未证明CPU1当时为Suspended")
    require(not (LOW_OCM_BEGIN <= CPU1_PARK_PC < LOW_OCM_END), "CPU1停核PC与诊断低OCM分配重叠")
    return {"path": str(result_path), "sha256": sha256(result_path), "ocm_cfg": 24,
            "historical_cpu1_state": cpu1.get("state_reason"), "historical_cpu1_pc": CPU1_PARK_PC,
            "note": "这是R07历史快照；每次真实执行诊断前仍须重新确认CPU1停核及PC不变。"}


def main() -> int:
    require(not EVIDENCE.exists(), f"拒绝覆盖已存在的evidence RunId：{EVIDENCE}")
    require(not WORK.exists(), f"拒绝覆盖已存在的临时RunId：{WORK}")
    source = exact_file(ROOT / "vitis" / "s2b_bresp_diag.S")
    builder = exact_file(Path(__file__))
    init_elf = exact_file(ARTIFACTS / "init.elf")
    app_elf = exact_file(ARTIFACTS / "infer.elf")
    xsa = exact_file(ROOT / "report" / "evidence" / "S2B-T19" / "visibility1_csr_fixed_20261016_r04" /
                     "artifacts" / "s2b_inference.xsa")
    bit = exact_file(ROOT / "report" / "evidence" / "S2B-T19" / "visibility1_csr_fixed_20261016_r04" /
                     "artifacts" / "s2b_inference.bit")
    require(sha256(init_elf) == EXPECTED_INIT_SHA, "R04 init.elf SHA与冻结值不符")
    require(sha256(app_elf) == EXPECTED_APP_SHA, "R04 infer.elf SHA与冻结值不符")
    require(sha256(xsa) == EXPECTED_XSA_SHA, "R04 XSA SHA与冻结值不符")
    require(sha256(bit) == EXPECTED_BIT_SHA, "R04 bit SHA与冻结值不符")
    ocm = load_and_validate_layout()
    cpu1 = validate_cpu1_and_ocm()

    gcc = exact_file(TOOL_ROOT / "arm-none-eabi-gcc.exe")
    objdump = exact_file(TOOL_ROOT / "arm-none-eabi-objdump.exe")
    readelf = exact_file(TOOL_ROOT / "arm-none-eabi-readelf.exe")
    EVIDENCE.mkdir(parents=True, exist_ok=False)
    WORK.mkdir(parents=True, exist_ok=False)
    (EVIDENCE / "source_snapshot").mkdir()
    (WORK / "build").mkdir()
    (EVIDENCE / "source_snapshot" / source.name).write_bytes(source.read_bytes())
    (EVIDENCE / "source_snapshot" / builder.name).write_bytes(builder.read_bytes())

    linker = WORK / "build" / "s2b_bresp_diag.ld"
    linker_text = f"""ENTRY(_diag_start)
MEMORY {{
  DIAG (rwx) : ORIGIN = 0x{CODE_BEGIN:08x}, LENGTH = 0x{CODE_END - CODE_BEGIN:x}
  TTB (rw) : ORIGIN = 0x{TTB_BEGIN:08x}, LENGTH = 0x{TTB_END - TTB_BEGIN:x}
}}
SECTIONS {{
  .vectors ORIGIN(DIAG) : ALIGN(32) {{ KEEP(*(.vectors)) }} > DIAG
  .text : ALIGN(4) {{ *(.text.boot) *(.text*) *(.rodata*) }} > DIAG
  __diag_end = .;
  .diag_ttb ORIGIN(TTB) (NOLOAD) : ALIGN(0x4000) {{ KEEP(*(.diag_ttb)) }} > TTB
  /DISCARD/ : {{ *(.comment) *(.note*) *(.eh_frame*) *(.ARM.attributes) }}
}}
ASSERT(__diag_end <= 0x{CODE_END:08x}, "诊断代码越过保留低OCM范围")
ASSERT(SIZEOF(.diag_ttb) == 0x4000, "独立L1表必须为16KiB")
"""
    linker.write_text(linker_text, encoding="utf-8", newline="\n")
    (EVIDENCE / "s2b_bresp_diag.ld").write_text(linker_text, encoding="utf-8", newline="\n")
    obj = WORK / "build" / "s2b_bresp_diag.o"
    elf = EVIDENCE / "s2b_bresp_diag.elf"
    map_path = EVIDENCE / "s2b_bresp_diag.map"
    commands: list[dict[str, object]] = []
    gcc_version = run_command([str(gcc), "--version"], EVIDENCE / "gcc_version.log", commands)
    run_command([str(gcc), "-c", "-x", "assembler-with-cpp", "-mcpu=cortex-a9", "-marm", "-ffreestanding",
                 "-o", str(obj), str(source)], EVIDENCE / "assemble.log", commands)
    run_command([str(gcc), "-nostdlib", "-nostartfiles", "-mcpu=cortex-a9", "-marm", "-Wl,--build-id=none",
                 f"-Wl,-Map={map_path}", f"-Wl,-T,{linker}", "-o", str(elf), str(obj)],
                EVIDENCE / "link.log", commands)
    disassembly = run_command([str(objdump), "-d", str(elf)], EVIDENCE / "disassembly.log", commands)
    readelf_output = run_command([str(readelf), "-h", "-lW", "-SW", "-sW", str(elf)],
                                 EVIDENCE / "readelf.log", commands)
    require("diag_busy_start_store" in disassembly and re.search(r"e5801000\s+str\s+r1, \[r0\]", disassembly) is not None,
            "第二次START store的符号或精确STR机器码未在反汇编中确认")
    entry_match = re.search(r"entry point address:\s+0x([0-9a-f]+)", readelf_output.lower())
    require(entry_match is not None and CODE_BEGIN <= int(entry_match.group(1), 16) < CODE_END,
            "诊断ELF入口不在诊断低OCM代码区")
    require("0x0000c000" in readelf_output.lower(), "诊断ELF的可加载段未位于低OCM")
    require(re.search(r"\.diag_ttb\s+NOBITS\s+00010000\s+", readelf_output) is not None,
            "独立16KiB L1表未被链接到低OCM的0x10000")
    require("0x0002c000" not in readelf_output.lower(), "诊断ELF意外占用保留栈边界")

    schema = {
        "schema_version": 1,
        "kind": "s2b-cpu-bresp-diagnostic-mailbox/1.0.0",
        "base": MAILBOX_BEGIN,
        "bytes_reserved": MAILBOX_END - MAILBOX_BEGIN,
        "words": {
            "0x00": "magic: 0x42524453=已开始，0x4252444f=有条件SLVERR，0x4252554e=外部abort但未达严格SLVERR条件，0x42524641=前置/其他异常失败",
            "0x04": "MIDR", "0x08": "SCTLR启动快照", "0x0c": "TTBCR", "0x10": "TTBR0原值",
            "0x14": "CSR一级表项地址", "0x18": "CSR表项旧描述符", "0x1c": "CSR表项Strongly-ordered描述符",
            "0x20": "启动PHYS_STATUS", "0x24": "启动AXI_PROGRESS", "0x28": "启动LAST_REJECT",
            "0x2c": "起始EPOCH_LO", "0x30": "起始EPOCH_HI", "0x34": "起始RESULT_FRAME_ID",
            "0x38": "busy前PHYS_STATUS", "0x3c": "busy前LAST_REJECT", "0x40": "busy前EPOCH_LO",
            "0x44": "busy前EPOCH_HI", "0x48": "busy前RESULT_FRAME_ID", "0x4c": "DFSR",
            "0x50": "SPSR_abt", "0x54": "LR_abt", "0x58": "fault_pc=LR_abt-8", "0x5c": "fault_opcode",
            "0x60": "DFAR", "0x64": "busy后PHYS_STATUS", "0x68": "busy后EPOCH_LO",
            "0x6c": "busy后EPOCH_HI", "0x70": "busy后RESULT_FRAME_ID", "0x74": "busy后LAST_REJECT",
            "0x78": "busy后AXI_PROGRESS", "0x80": "首次观察ARMING的PHYS_STATUS或0",
            "0x84": "ARMING EPOCH_LO", "0x88": "ARMING EPOCH_HI", "0x8c": "ARMING RESULT_FRAME_ID",
            "0x90": "ARMING LAST_REJECT", "0x7c": "失败原因码",
            "0x98": "诊断私有L1表的OCM地址"
        },
        "slverr_acceptance": ["同步外部数据abort状态", "DFSR.WnR=1", "DFSR.ExT=1",
                              "DFAR=0x43c00008", "fault_pc精确等于diag_busy_start_store",
                              "opcode=0xe5801000", "busy前状态为RUN且PHYS_OWNER_PL=1",
                              "busy前LAST_REJECT=0、busy后LAST_REJECT=1",
                              "busy前后EPOCH及RESULT_FRAME_ID不变"],
        "non_acceptance": "no-abort、其他异常、DECERR、异步abort、地址/指令/状态不匹配均不分类为SLVERR；CPU停驻，不重试、ACK、reset或清账本。"
    }
    write_json(EVIDENCE / "mailbox_schema.json", schema)
    write_json(EVIDENCE / "ocm_allocation.json", {
        "schema_version": 1, "status": "STATIC_LAYOUT_VALIDATION_ONLY",
        "low_ocm": [LOW_OCM_BEGIN, LOW_OCM_END], "init_elf": ocm,
        "diagnostic_code": [CODE_BEGIN, CODE_END], "diagnostic_private_l1_table": [TTB_BEGIN, TTB_END],
        "diagnostic_stack": [STACK_BEGIN, STACK_END],
        "reserved_guard": [STACK_END, MAILBOX_BEGIN], "mailbox": [MAILBOX_BEGIN, MAILBOX_END],
        "cpu1_historical_snapshot": cpu1,
        "runtime_precondition": "每次真实使用前重读OCM_CFG并核实CPU1仍Stopped/Suspended且PC不在诊断代码、栈、mailbox范围；本构建不证明当前硬件状态。"
    })
    write_json(EVIDENCE / "commands.json", commands)
    result = {
        "schema_version": 1, "run_id": RUN_ID,
        "status": "OFFLINE_BUILD_OK_NOT_HARDWARE_RESULT",
        "hardware_execution": "NOT_RUN", "sdk_or_jtag_access": "NOT_USED",
        "source": {"path": str(source), "sha256": sha256(source)},
        "builder": {"path": str(builder), "sha256": sha256(builder)},
        "toolchain": {"gcc": str(gcc), "gcc_version_first_line": gcc_version.splitlines()[0],
                       "objdump": str(objdump), "readelf": str(readelf)},
        "inputs": {"init_elf": {"path": str(init_elf), "sha256": sha256(init_elf)},
                   "infer_elf": {"path": str(app_elf), "sha256": sha256(app_elf)},
                   "xsa": {"path": str(xsa), "sha256": sha256(xsa)},
                   "bit": {"path": str(bit), "sha256": sha256(bit)}},
        "artifacts": {name: {"path": str(EVIDENCE / name), "sha256": sha256(EVIDENCE / name)}
                      for name in ("s2b_bresp_diag.elf", "s2b_bresp_diag.map", "disassembly.log", "readelf.log",
                                   "mailbox_schema.json", "ocm_allocation.json", "s2b_bresp_diag.ld")},
        "limitations": ["只完成汇编、链接、静态地址/机器码核验；不证明板上ELF装载、MMU运行状态、AXI响应或mailbox内容。",
                        "Strongly-ordered仅用于独立诊断ELF的CSR段；其证据不能替代正式Device映射推理应用。",
                        "R07 CPU1停核PC及OCM_CFG是历史记录；上板前须新鲜确认CPU1、OCM_CFG和SAFE/ledger-empty。",
                        "输入/权重已加载并flush及旧事务SAFE/ledger-empty是板上执行前提，不由此离线构建器验证。",
                        "诊断期间CPU0不返回infer.elf上下文；需由总控在真实SAFE/ledger-empty后恢复原R04 bit、原infer.elf及约定黄金流程。"],
        "commands": commands
    }
    write_json(EVIDENCE / "build_result.json", result)
    print(json.dumps({"status": result["status"], "evidence": str(EVIDENCE),
                      "elf_sha256": sha256(elf), "commands": len(commands)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"OFFLINE_BUILD_FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
