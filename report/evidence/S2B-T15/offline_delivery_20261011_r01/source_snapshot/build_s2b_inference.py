#!/usr/bin/env python3
"""用本机Vitis2026.1自建CPU0 BSP、候选推理应用与同XSA最小OCM初始化。"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import zipfile
import xml.etree.ElementTree as ET

from build_s2b_ps_smoke import (INITIALIZER_C, copy_exclusive, exact_path, new_directory,
                               new_file, require_under, run_checked, sha256, unique_file, write_json)

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / "verification"))
from check_s2b_ps_smoke_layout import macro_int, parse_elf, require, verify_cache_contract

MODEL_PATH = ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
MODEL_SHA = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"


def xsa_contract(path, mode):
    """检查实际HWH的PS DDR/UART及Full模式GP0/HP0/FCLK，不推断实物身份。"""
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "XSA重复成员")
        hwh = [name for name in names if name.endswith(".hwh")]
        require(len(hwh) == 1 and archive.getinfo(hwh[0]).file_size < 16 * 1024 * 1024, "HWH数量/大小错误")
        tree = ET.fromstring(archive.read(hwh[0]))
    modules = list(tree.iter("MODULE"))
    ps = [item for item in modules if item.attrib.get("MODTYPE") == "processing_system7"]
    require(len(ps) == 1, "PS7实例数量错误")
    pairs = ps[0].findall("PARAMETERS/PARAMETER")
    params = {item.attrib["NAME"]: item.attrib["VALUE"] for item in pairs}
    require(len(params) == len(pairs), "PS7参数重复")
    begin, high = int(params["PCW_DDR_RAM_BASEADDR"], 0), int(params["PCW_DDR_RAM_HIGHADDR"], 0)
    require(begin <= 0x100000 and high >= 0x11FFFFFF, "DDR不能容纳应用及32MiB arena")
    require(params["PCW_UART1_PERIPHERAL_ENABLE"] == "1" and params["PCW_UART1_UART1_IO"] == "MIO 48 .. 49" and
            int(params["PCW_UART1_BASEADDR"], 0) == 0xE0001000, "实际XSA UART1配置错误")
    if mode == "FULL_PLATFORM_BOUND":
        require(params.get("PCW_USE_M_AXI_GP0") == "1" and params.get("PCW_USE_S_AXI_HP0") == "1", "完整XSA缺GP0/HP0")
        require(float(params.get("PCW_FPGA0_PERIPHERAL_FREQMHZ", "0")) == 50.0, "完整XSA FCLK0目标不是50MHz")
        require(any(item.attrib.get("MODTYPE") == "s2b_inference_top" for item in modules), "完整XSA未含整网顶层module")
    else:
        require(len(modules) == 1 and params.get("PCW_USE_M_AXI_GP0") == "0" and params.get("PCW_USE_S_AXI_HP0") == "0", "UNIT_ONLY模式只接受冻结PS-only XSA")
    return {"hwh_member": hwh[0], "ddr_begin": begin, "ddr_end": high + 1,
            "uart1_base": 0xE0001000, "hardware_mode": mode, "ps_instance": ps[0].attrib["INSTANCE"],
            "parameters": {key: params.get(key) for key in ("PCW_USE_M_AXI_GP0", "PCW_USE_S_AXI_HP0", "PCW_FPGA0_PERIPHERAL_FREQMHZ")}}


def verify_app_elf(path):
    """检查实际ARM ELF全部分配节、文件段和arena、heap、stack半开区间。"""
    parsed = parse_elf(exact_path(path, "file").read_bytes())
    require(0x00100000 <= parsed["entry"] < 0x01100000, "ELF入口不在应用区域")
    arenas = [row for row in parsed["sections"] if row["name"] == ".s2b_tensor_ddr"]
    require(len(arenas) == 1, "arena节数量错误")
    arena = arenas[0]
    require(arena["type"] == 8 and arena["address"] == 0x10000000 and arena["size"] == 0x02000000 and arena["align"] >= 64, "arena不满足NOLOAD/固定地址/32MiB/64B")
    for row in parsed["sections"]:
        if row["flags"] & 2 and row["size"] and row["name"] != ".s2b_tensor_ddr":
            require(0x00100000 <= row["address"] and row["address"] + row["size"] <= 0x01100000, f"分配节落在应用外：{row['name']}")
    for row in parsed["programs"]:
        if row["type"] == 1 and row["memory_size"]:
            require(row["virtual"] == row["physical"], "ELF VMA/LMA不一致")
            app = 0x00100000 <= row["virtual"] and row["virtual"] + row["memory_size"] <= 0x01100000
            noload = row["virtual"] == 0x10000000 and row["memory_size"] == 0x02000000 and row["file_size"] == 0
            require(app or noload, "LOAD段越界、跨区或arena包含下载字节")
    named = {row["name"]: row for row in parsed["sections"]}
    require(all(name in named for name in (".heap", ".stack", ".bss")), "ELF缺heap/stack/bss")
    heap, stack = named[".heap"], named[".stack"]
    require(heap["size"] >= 0x100000 and stack["size"] >= 0x10000, "应用heap/stack预算不足")
    require(heap["address"] + heap["size"] <= stack["address"] or stack["address"] + stack["size"] <= heap["address"], "heap/stack重叠")
    return parsed


def build(config_path):
    """创建独占Vitis server和短名workspace，失败证据/工具原件全部保留。"""
    config_path = exact_path(config_path, "file")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    fields = {"schema_version", "source_commit", "xsa", "xsa_sha256", "xsa_source_commit", "hardware_mode",
              "platform_manifest", "platform_manifest_sha256", "workspace", "artifact_dir"}
    require(set(config) == fields and config["schema_version"] == 1, "配置schema/字段不符")
    mode = config["hardware_mode"]
    require(mode in {"FULL_PLATFORM_BOUND", "UNIT_ONLY_PS_XSA"}, "必须显式区分完整平台/仅CPU离线单元")
    for key in ("source_commit", "xsa_source_commit"):
        require(re.fullmatch(r"[0-9a-f]{40}", config[key]) is not None, "必须固定提交")
        require(subprocess.run(["git", "cat-file", "-e", config[key] + "^{commit}"], cwd=ROOT, capture_output=True).returncode == 0, "基线Git对象不可恢复")
    xsa, platform_manifest = exact_path(config["xsa"], "file"), exact_path(config["platform_manifest"], "file")
    require(sha256(xsa) == config["xsa_sha256"] and sha256(platform_manifest) == config["platform_manifest_sha256"], "XSA或平台证据清单绑定SHA错误")
    require(sha256(MODEL_PATH) == MODEL_SHA, "冻结模型原字节SHA错误")
    model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    metadata = xsa_contract(xsa, mode)
    workspace, artifact = Path(config["workspace"]), Path(config["artifact_dir"])
    cache_parent, evidence_parent = exact_path(ROOT / "tmp/2B/S2B-T15", "directory"), exact_path(ROOT / "report/evidence/S2B-T15", "directory")
    require_under(workspace, cache_parent); require_under(artifact, evidence_parent)
    new_file(workspace); new_file(artifact)
    artifact = new_directory(artifact, evidence_parent)
    record = {"schema_version": 1, "status": "FAIL", "hardware_execution": "NOT_RUN", "hardware_mode": mode,
              "config": config, "config_sha256": sha256(config_path), "source_commit": config["source_commit"],
              "xsa_sha256": config["xsa_sha256"], "xsa_metadata": metadata, "commands": [], "api_calls": [],
              "source_sha256": {}, "files": {}, "attempts": 1, "peak_memory_bytes": None,
              "peak_memory_reason": "未测量Vitis整棵进程树峰值内存"}
    started, created = time.monotonic(), False
    try:
        require("v2026.1" in os.environ.get("XILINX_VITIS_VERSION", ""), "必须通过本机Vitis2026.1 -s运行")
        import vitis
        import build_pb2
        import platform_pb2

        def api(label, function, *args, **kwargs):
            """真实API类型与返回值逐项留证，不把整数SUCCESS当True。"""
            begin = time.monotonic()
            entry = {"name": label, "args": [repr(item) for item in args], "kwargs": {key: repr(value) for key, value in kwargs.items()}}
            record["api_calls"].append(entry)
            try:
                result = function(*args, **kwargs)
                entry.update(return_type=type(result).__name__, return_repr=repr(result))
                return result
            except Exception as error:
                entry["error"] = repr(error)
                raise
            finally:
                entry["elapsed_seconds"] = time.monotonic() - begin
                print(json.dumps(entry, ensure_ascii=False), flush=True)

        def build_api(label, function, descriptor):
            """比较实际protobuf成功枚举。"""
            result = api(label, function)
            expected = descriptor.fields_by_name["type"].enum_type.values_by_name["SUCCESS"].number
            require(type(result) is int and result == expected, f"{label}实际构建未成功：{result!r}")

        snapshot = new_directory(artifact / "source_snapshot", artifact)
        for relative in ("vitis/s2b_inference_app.c", "vitis/build_s2b_inference.py", "vitis/build_s2b_ps_smoke.py",
                         "verification/s2a_ps_decode_nms_reference.c", "verification/s2a_ps_decode_nms_reference.h",
                         "verification/s2b_board_transport.py", "verification/check_s2b_ps_smoke_layout.py"):
            source = exact_path(ROOT / relative, "file")
            record["source_sha256"][relative] = sha256(source)
            copy_exclusive(source, snapshot / source.name)
        workspace = new_directory(workspace, cache_parent)
        client = api("vitis.create_client", vitis.create_client, workspace=str(workspace)); created = True
        require(client._serverObj.cp is not None, "未创建本次独占server")
        record["own_server_pid"] = client._serverObj.cp.pid
        require(api("client.set_workspace", client.set_workspace, path=str(workspace)) is True, "workspace配置失败")
        platform = api("client.create_platform_component", client.create_platform_component, name="ps7", hw_design=str(xsa),
                       cpu="ps7_cortexa9_0", os="standalone", domain_name="cpu0", no_boot_bsp=True, generate_dtb=False)
        domain = api("platform.get_domain", platform.get_domain, name="cpu0")
        for parameter in ("standalone_stdin", "standalone_stdout"):
            require(api("domain.set_config:" + parameter, domain.set_config, "os", parameter, "ps7_uart_1") is True, "UART1 BSP配置失败")
            require(api("domain.get_config:" + parameter, domain.get_config, "os", parameter).get("value") == "ps7_uart_1", "UART BSP回读失败")
        build_api("platform.build", platform.build, platform_pb2.PlatformResponse.DESCRIPTOR)
        platform_root = exact_path(workspace / "ps7", "directory")
        bsp = exact_path(platform_root / "ps7_cortexa9_0/cpu0/bsp", "directory")
        bsp_sources = {"xparameters.h": "include/xparameters.h", "bspconfig.h": "include/bspconfig.h",
                       "xil_cache.c": "libsrc/standalone/src/arm/cortexa9/xil_cache.c",
                       "xil_mmu.c": "libsrc/standalone/src/arm/cortexa9/xil_mmu.c", "xil_mmu.h": "include/xil_mmu.h",
                       "translation_table.S": "libsrc/standalone/src/arm/cortexa9/gcc/translation_table.S",
                       "xuartps_g.c": "libsrc/uartps/src/xuartps_g.c", "xuartps.c": "libsrc/uartps/src/xuartps.c",
                       "xiltimer.c": "libsrc/xiltimer/src/xiltimer.c", "xiltimer.h": "include/xiltimer.h",
                       "globaltimer_sleep_zynq.c": "libsrc/xiltimer/src/core/default_timer/globaltimer_sleep_zynq.c",
                       "xtimer_config.h": "include/xtimer_config.h",
                       "bsp_compile_commands.json": "libsrc/build_configs/gen_bsp/compile_commands.json"}
        for name, relative in bsp_sources.items():
            source = exact_path(bsp / relative, "file")
            copied = copy_exclusive(source, artifact / name)
            record["files"][name] = {"path": str(copied), "source_path": str(source), "sha256": sha256(copied)}
        verify_cache_contract((artifact / "xil_cache.c").read_text(encoding="utf-8"))
        compile_text = (artifact / "bsp_compile_commands.json").read_text(encoding="utf-8")
        require("-DUSE_AMP" not in compile_text, "实际BSP编译禁止USE_AMP")
        require("globaltimer_sleep_zynq.c" in compile_text and "xiltimer.c" in compile_text,
                "真实SDT BSP没有编译global timer实现")
        mmu_header = (artifact / "xil_mmu.h").read_text(encoding="utf-8")
        require("DEVICE_MEMORY" in mmu_header and "0xC06" in mmu_header, "实际Device MMIO属性定义不符")
        app = api("client.create_app_component", client.create_app_component, name="infer", platform=str(unique_file(platform_root, "ps7.xpfm")),
                  domain="cpu0", template="empty_application")
        require(api("app.import_files", app.import_files, from_loc=str(ROOT / "vitis"), files=["s2b_inference_app.c"], dest_dir_in_cmp="src") is True, "应用源码导入失败")
        require(api("app.import_files:decoder", app.import_files, from_loc=str(ROOT / "verification"),
                    files=["s2a_ps_decode_nms_reference.c", "s2a_ps_decode_nms_reference.h"], dest_dir_in_cmp="src") is True, "冻结C参考导入失败")
        source_root = exact_path(workspace / "infer/src", "directory")
        xparams = (artifact / "xparameters.h").read_text(encoding="utf-8")
        uart_macros = re.findall(r"^\s*#define\s+(XPAR_XUARTPS_[0-9]+_BASEADDR)\s+", xparams, re.MULTILINE)
        uart_macros = [name for name in uart_macros if macro_int(xparams, name) == 0xE0001000]
        require(len(uart_macros) == 1, "UART1实际BSP canonical宏不唯一")
        for name in ("STDIN_BASEADDRESS", "STDOUT_BASEADDRESS"):
            require(macro_int((artifact / "bspconfig.h").read_text(encoding="utf-8"), name) == 0xE0001000, "BSP标准IO不是UART1")
        header = new_file(source_root / "s2b_inference_platform.h")
        heads = {item["name"]: item for item in model["address_map"]["heads"]}
        with header.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write("/* 从实际XSA、BSP、冻结模型和本次源码SHA生成。 */\n")
            stream.write(f"#define S2B_UART1_BASE {uart_macros[0]}\n#define S2B_BSP_CACHELINE_BYTES 32U\n")
            stream.write(f'#define S2B_C_SOURCE_SHA256 "{record["source_sha256"]["vitis/s2b_inference_app.c"]}"\n')
            stream.write(f'#define S2B_XSA_SHA256 "{config["xsa_sha256"]}"\n#define S2B_MODEL_SHA256 "{MODEL_SHA}"\n')
            stream.write(f'#define S2B_HEAD13_SCALE {heads["head13"]["int8_scale"]!r}\n#define S2B_HEAD26_SCALE {heads["head26"]["int8_scale"]!r}\n')
        ld = api("app.get_ld_script", app.get_ld_script)
        ld_path = exact_path(ld.file_path, "file"); require_under(ld_path, workspace)
        copy_exclusive(ld_path, artifact / "default_lscript.ld")
        regions = api("ld.get_memory_regions", ld.get_memory_regions)
        ddr = [item for item in regions if "ddr" in item["name"].lower()]
        require(len(ddr) == 1, "默认DDR区域不唯一")
        app_region = ddr[0]["name"]
        require(int(ddr[0]["base_address"], 0) == 0x00100000 and
                int(ddr[0]["base_address"], 0) + int(ddr[0]["size"], 0) >= 0x12000000, "实际BSP DDR应用/arena范围不符")
        require(api("ld.update_memory_region", ld.update_memory_region, name=app_region, base_address="0x100000", size="0x1000000") is True, "应用16MiB区域失败")
        require(api("ld.add_memory_region", ld.add_memory_region, name="s2b_tensor_ddr", base_address="0x10000000", size="0x2000000") is True, "专属arena区域失败")
        require(api("ld.set_stack_size", ld.set_stack_size, "0x10000") is True, "stack64KiB配置失败")
        require(api("ld.set_heap_size", ld.set_heap_size, "0x100000") is True, "heap1MiB配置失败")
        text = ld_path.read_text(encoding="utf-8")
        # 实际2026.1 API没有删除region方法；只在本次新workspace裁剪生成MEMORY声明。
        memory = f"MEMORY\n{{\n  {app_region} : ORIGIN = 0x00100000, LENGTH = 0x01000000\n  s2b_tensor_ddr : ORIGIN = 0x10000000, LENGTH = 0x02000000\n}}"
        text, replaced = re.subn(r"\bMEMORY\s*\{[^}]*\}", lambda match: memory, text, count=1)
        require(replaced == 1, "默认ld MEMORY声明缺失")
        closing = text.rfind("}")
        require(closing >= 0 and text.rstrip().endswith("}"), "默认ld结构不符")
        arena = """\n/* arena独占32MiB且不属于启动.bss清零范围。 */
.s2b_tensor_ddr (NOLOAD) : ALIGN(64) {
    __s2b_tensor_start = .; KEEP(*(.s2b_tensor_ddr)) __s2b_tensor_end = .;
} > s2b_tensor_ddr
"""
        text = text[:closing] + arena + text[closing:]
        text += '\nASSERT(ADDR(.s2b_tensor_ddr) == 0x10000000, "arena address")\n'
        text += 'ASSERT(LOADADDR(.s2b_tensor_ddr) == 0x10000000, "arena LMA")\n'
        text += 'ASSERT(SIZEOF(.s2b_tensor_ddr) == 0x2000000, "arena size")\n'
        text += 'ASSERT((_stack < 0x01100000) && (_heap_end < 0x01100000), "app budget")\n'
        with ld_path.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
        for key, value in (("USER_COMPILE_OTHER_FLAGS", "-std=gnu11 -O2 -Wall -Wextra -Werror -ffunction-sections -fdata-sections -save-temps=obj"),
                           ("USER_LINK_OTHER_FLAGS", "-Wl,-Map=infer.map,--cref,--gc-sections"), ("USER_LINK_LIBRARIES", "m")):
            require(api("app.set_app_config:" + key, app.set_app_config, key=key, values=value) is True, "应用构建配置失败")
        build_api("app.build", app.build, build_pb2.BuildResponse.DESCRIPTOR)
        # 保留实际编译命令、CMake配置和预处理结果，关联真正生效的头与宏。
        for name, source in (("app_compile_commands.json", workspace / "infer/build/compile_commands.json"),
                             ("app_UserConfig.cmake", source_root / "UserConfig.cmake"),
                             ("app_CMakeLists.txt", source_root / "CMakeLists.txt"),
                             ("app_preprocessed.i", workspace / "infer/build/CMakeFiles/infer.elf.dir/s2b_inference_app.c.i"),
                             ("decoder_preprocessed.i", workspace / "infer/build/CMakeFiles/infer.elf.dir/s2a_ps_decode_nms_reference.c.i")):
            copied = copy_exclusive(exact_path(source, "file"), artifact / name)
            record["files"][name] = {"path": str(copied), "source_path": str(source), "sha256": sha256(copied)}
        app_commands = json.loads((artifact / "app_compile_commands.json").read_text(encoding="utf-8"))
        for relative in ("s2b_inference_app.c", "s2a_ps_decode_nms_reference.c"):
            matches = [item for item in app_commands if Path(item["file"]) == source_root / relative]
            require(len(matches) == 1 and all(flag in matches[0]["command"] for flag in ("-DSDT", "-Wall", "-Wextra", "-Werror")) and
                    "-DUSE_AMP" not in matches[0]["command"], "实际应用编译命令不满足SDT/严格warnings/非AMP")
        elf = copy_exclusive(unique_file(workspace / "infer", "infer.elf"), artifact / "infer.elf")
        copy_exclusive(unique_file(workspace / "infer", "infer.map"), artifact / "infer.map")
        copy_exclusive(ld_path, artifact / "lscript.ld"); copy_exclusive(header, artifact / header.name)
        parsed = verify_app_elf(elf)
        write_json(artifact / "elf_layout.json", parsed)
        record["elf"] = {"path": str(elf), "sha256": sha256(elf)}

        # 初始化来源必须来自同一新XSA；只构建原字节PS init，绝不执行。
        with zipfile.ZipFile(xsa) as archive:
            for name in ("ps7_init.c", "ps7_init.h", "ps7_init.tcl"):
                members = [item for item in archive.namelist() if item.split("/")[-1] == name]
                require(len(members) == 1 and archive.getinfo(members[0]).file_size < 2 * 1024 * 1024, "PS init成员数量/大小错误")
                with new_file(artifact / name).open("xb") as stream:
                    stream.write(archive.read(members[0]))
        init = api("client.create_app_component:init", client.create_app_component, name="init", platform=str(unique_file(platform_root, "ps7.xpfm")),
                   domain="cpu0", template="empty_application")
        init_c = new_file(artifact / "s2b_ps_init.c")
        with init_c.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(INITIALIZER_C)
        require(api("init.import_files", init.import_files, from_loc=str(artifact), files=["s2b_ps_init.c", "ps7_init.c", "ps7_init.h"], dest_dir_in_cmp="src") is True, "同XSA init来源导入失败")
        init_ld = api("init.get_ld_script", init.get_ld_script)
        init_ld_path = exact_path(init_ld.file_path, "file"); require_under(init_ld_path, workspace)
        official = exact_path(Path(os.environ["XILINX_VITIS"]).parent / "data/embeddedsw/lib/sw_apps/zynq_fsbl/src/lscript.ld", "file")
        copy_exclusive(init_ld_path, artifact / "init_default_lscript.ld")
        with init_ld_path.open("wb") as stream:
            stream.write(official.read_bytes())
        for key, value in (("USER_COMPILE_OTHER_FLAGS", "-std=gnu11 -Wall -Wextra -ffunction-sections -fdata-sections -save-temps=obj"),
                           ("USER_LINK_OTHER_FLAGS", "-Wl,-Map=init.map,--cref,--gc-sections")):
            require(api("init.set_app_config:" + key, init.set_app_config, key=key, values=value) is True, "初始化构建配置失败")
        build_api("init.build", init.build, build_pb2.BuildResponse.DESCRIPTOR)
        init_elf = copy_exclusive(unique_file(workspace / "init", "init.elf"), artifact / "init.elf")
        copy_exclusive(unique_file(workspace / "init", "init.map"), artifact / "init.map")
        copy_exclusive(init_ld_path, artifact / "init_lscript.ld")
        init_parsed = parse_elf(init_elf.read_bytes())
        for section in init_parsed["sections"]:
            if section["flags"] & 2 and section["size"]:
                require((0 <= section["address"] and section["address"] + section["size"] <= 0x30000) or
                        (0xFFFF0000 <= section["address"] and section["address"] + section["size"] <= 0xFFFFFE00), "init分配节不属于OCM")
        names = {item["name"] for item in init_parsed["symbols"]}
        require({"s2b_ps_init_ready", "s2b_ps_init_fail", "ps7_init"} <= names and
                not ({"LoadBootImage", "FabricInit", "XDcfg_Transfer", "ps7_post_config"} & names), "init入口或禁止功能不符")
        write_json(artifact / "init_elf_layout.json", init_parsed)
        record["initializer_elf"] = {"path": str(init_elf), "sha256": sha256(init_elf), "official_linker_sha256": sha256(official)}
        for name, source in (("init_compile_commands.json", workspace / "init/build/compile_commands.json"),
                             ("init_UserConfig.cmake", workspace / "init/src/UserConfig.cmake")):
            copied = copy_exclusive(exact_path(source, "file"), artifact / name)
            record["files"][name] = {"path": str(copied), "source_path": str(source), "sha256": sha256(copied)}
        tool_root = exact_path(Path(os.environ["XILINX_VITIS"]).parent / "gnu/aarch32/nt/gcc-arm-none-eabi/bin", "directory")
        run_checked([str(tool_root / "arm-none-eabi-gcc.exe"), "--version"], workspace, artifact / "gcc_version.log", record["commands"])
        for name, target in (("app", elf), ("init", init_elf)):
            run_checked([str(tool_root / "arm-none-eabi-readelf.exe"), "--wide", "-a", str(target)], workspace, artifact / (name + "_readelf.log"), record["commands"])
            run_checked([str(tool_root / "arm-none-eabi-objdump.exe"), "-d", str(target)], workspace, artifact / (name + "_disassembly.log"), record["commands"])
        for relative, expected in record["source_sha256"].items():
            require(sha256(exact_path(ROOT / relative, "file")) == expected, "构建中项目源码发生变化")
        for relative in ("s2b_inference_app.c", "s2a_ps_decode_nms_reference.c", "s2a_ps_decode_nms_reference.h"):
            expected = record["source_sha256"]["vitis/" + relative if relative == "s2b_inference_app.c" else "verification/" + relative]
            require(sha256(exact_path(source_root / relative, "file")) == expected, "实际编译副本发生变化")
        require(sha256(xsa) == config["xsa_sha256"] and sha256(platform_manifest) == config["platform_manifest_sha256"], "构建中上游XSA绑定发生变化")
        record["vitis_version"] = os.environ["XILINX_VITIS_VERSION"]
        record["status"] = "PASS_OFFLINE_FULL_XSA_BUILD" if mode == "FULL_PLATFORM_BOUND" else "PASS_UNIT_ONLY_PS_XSA_BUILD"
        record["limitations"] = ["本次未执行任何实板动作、原始MMIO拒绝或UART传输；离线PASS不代表2B G3/G4/G5。",
                                 "CPU1停核、排空可见性、实际DDR和整网部署批准由总控独立绑定。",
                                 "初始化原厂源码使用-Wall/-Wextra；应用及冻结C参考使用-Werror，原始编译输出保留。"]
    except BaseException as error:
        record["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        if created:
            try:
                vitis.dispose(); record["own_server_cleanup"] = "DISPOSE_CALLED"
            except BaseException as error:
                record["status"] = "FAIL"; record["cleanup_error"] = repr(error)
        record["elapsed_seconds"] = time.monotonic() - started
        write_json(artifact / "build_details.json", record)
    print(json.dumps({"status": record["status"], "elapsed_seconds": record["elapsed_seconds"], "hardware_execution": "NOT_RUN"}, ensure_ascii=False))


if __name__ == "__main__":
    require("S2B_INFERENCE_CONFIG" in os.environ, "必须显式绑定S2B_INFERENCE_CONFIG")
    build(Path(os.environ["S2B_INFERENCE_CONFIG"]))
