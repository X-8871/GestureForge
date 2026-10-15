"""只读复核visibility0的CPU/DAP 256字节探针兼容事实；不导入SDK、不接硬件。"""

from pathlib import Path
import argparse
import ast
import hashlib
import importlib.util
import json
import re
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).absolute().parents[4]
sys.path.insert(0, str(ROOT / "verification"))
RUN = "report/evidence/S2B-T19/visibility0_compatibility_20261014_r01"
V0 = "report/evidence/S2B-T19/visibility0_hp_rebuild_20261014_r02"
V1 = "report/evidence/S2B-T19/visibility1_timing_current_20261014_r01"
BSP = "report/evidence/S2B-T15/visibility1_xsa_20261014_r01"
EXPECTED = {
    "compiled_xsa": (V1 + "/artifacts/s2b_inference_wrapper_current.xsa", "90f8d0b9e857f8beb9d99a6264b96441f9ba9b4b0af0568dbbcc064aecba6065"),
    "implemented_xsa": (V0 + "/s2b_inference_implemented_r02.xsa", "7d605bde08a6ca9f6c74f2ba5bc537a610b47ef0233f2761fb07f31332b6f238"),
    "bit": (V0 + "/s2b_inference_implemented_r02.bit", "4c3fda32757e87f642b64fd2a0fb9978158e0f45dfe6aa9aecf7eef61752107e"),
    "app_elf": (BSP + "/infer.elf", "a7ca427ab06f5f81a650bcb0d2bda3ed0adb716c3c2cb226c34519e695d47869"),
    "init_elf": (BSP + "/init.elf", "7132ed104bc84066b714f61f61419b8c43474a4ef101cb51298b3027e30e2ee2"),
}
COMPAT = {"same_ps7_config", "same_ps_init_bytes", "same_bsp_mmu_macros", "same_uart_ddr_csr_clocks", "full_model_core_present", "postroute_timing_pass"}
ARTIFACTS = {"compiled_xsa", "implemented_xsa", "init_elf", "app_elf", "bit", "build_details", "platform_manifest"}


def need(condition, message):
    """错误不能被python优化选项消除。"""
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load_module(relative, name):
    """只导入仓库只读解析器；SDK模块完全不消费。"""
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def audit():
    """重新读取原件、核对原字节并输出确定性事实，不写文件。"""
    inputs = {}
    facts = {}
    checks = {}
    errors = {}
    historical_bindings = {}

    def raw(relative, expected=None):
        path = ROOT / relative
        need(path.is_file() and not path.is_symlink(), "精确普通文件缺失：" + relative)
        need(any(p.name == path.name for p in path.parent.iterdir()), "目标名称字符不符：" + relative)
        data = path.read_bytes()
        actual = digest(data)
        need(expected is None or actual == expected, "原字节SHA不符：" + relative)
        need(relative not in historical_bindings or actual == historical_bindings[relative], "上游证据清单绑定漂移：" + relative)
        inputs[relative] = actual
        return data

    def document(relative):
        return json.loads(raw(relative).decode("utf-8-sig"))

    def checked(name, function):
        try:
            facts[name] = function()
            checks[name] = True
        except Exception as error:
            checks[name] = False
            errors[name] = str(error)

    artifacts = {}
    for name, (relative, expected) in EXPECTED.items():
        raw(relative, expected)
        artifacts[name] = {"path": str(ROOT / relative), "sha256": expected}
    build = document(BSP + "/build_details.json")
    artifacts["build_details"] = {"path": str(ROOT / (BSP + "/build_details.json")), "sha256": inputs[BSP + "/build_details.json"]}
    original0 = document(V0 + "/delivery_manifest.json")
    original1 = document(V1 + "/delivery_manifest.json")
    build_manifest = document(BSP + "/delivery_manifest.json")
    for manifest in (original0, original1, build_manifest):
        for row in manifest["files"]:
            if any(row["path"].startswith(prefix + "/") for prefix in (V0, V1, BSP)):
                need(row["path"] not in historical_bindings or historical_bindings[row["path"]] == row["sha256"], "上游重复绑定冲突")
                historical_bindings[row["path"]] = row["sha256"]
    need(inputs[V1 + "/delivery_manifest.json"] == build["config"]["platform_manifest_sha256"], "编译平台清单与原构建不同")
    need(build["status"] == "PASS_OFFLINE_FULL_XSA_BUILD" and build["hardware_execution"] == "NOT_RUN", "构建状态或硬件状态不符")
    need(build["xsa_sha256"] == EXPECTED["compiled_xsa"][1] == build["config"]["xsa_sha256"], "构建XSA不符")
    for name, key in (("app_elf", "elf"), ("init_elf", "initializer_elf")):
        need(build[key]["path"] == artifacts[name]["path"] and build[key]["sha256"] == artifacts[name]["sha256"], "构建ELF绑定不同")
    for name, row in build["files"].items():
        data = raw(BSP + "/" + name, row["sha256"])
        need(row["path"] == str(ROOT / (BSP + "/" + name)), "实际BSP路径不同")
    archive_data = {}
    for name in ("compiled_xsa", "implemented_xsa"):
        with zipfile.ZipFile(ROOT / EXPECTED[name][0]) as archive:
            members = archive.namelist()
            need(len(members) == len(set(members)) and archive.testzip() is None, "XSA有重复/损坏成员")
            archive_data[name] = {member: archive.read(member) for member in members}
        metadata = json.loads(archive_data[name]["xsa.json"])
        need(metadata["devices"][0]["part"]["name"] == "xc7z020clg400-2", "XSA器件不同")
    trees = {name: ET.fromstring(data["s2b_inference.hwh"]) for name, data in archive_data.items()}

    def ps_parameters():
        rows = []
        for tree in trees.values():
            ps = tree.findall(".//MODULE[@INSTANCE='ps7']")
            need(len(ps) == 1, "ps7实例不唯一")
            pairs = [(p.get("NAME"), p.get("VALUE")) for p in ps[0].findall("./PARAMETERS/PARAMETER")]
            need(len(pairs) == 937 and len(dict(pairs)) == 937, "937项PS参数数量/唯一性不符")
            rows.append(dict(pairs))
        need(rows[0] == rows[1], "PS参数原值不同")
        return {"parameter_count": 937, "all_names_and_values_equal": True, "canonical_sha256": digest(json.dumps(rows[0], sort_keys=True, separators=(",", ":")).encode("utf-8"))}

    checked("same_ps7_config", ps_parameters)

    def init_bytes():
        names = ["ps7_init.c", "ps7_init.h", "ps7_init.html", "ps7_init.tcl", "ps7_init_gpl.c", "ps7_init_gpl.h"]
        result = {}
        for name in names:
            left, right = (archive_data[key][name] for key in ("compiled_xsa", "implemented_xsa"))
            need(left == right, "PS初始化成员字节不同：" + name)
            result[name] = {"sha256": digest(left), "bytes": len(left)}
            if name in ("ps7_init.c", "ps7_init.h", "ps7_init.tcl"):
                need(raw(BSP + "/" + name) == left, "实际初始化编译输入不是XSA原件：" + name)
        return result

    checked("same_ps_init_bytes", init_bytes)

    def bsp_mmu():
        parser = load_module("verification/check_s2b_ps_smoke_layout.py", "offline_elf_parser")
        raw("verification/check_s2b_ps_smoke_layout.py")
        mmu = re.sub(r"/\*.*?\*/", "", raw(BSP + "/xil_mmu.h").decode("utf-8"), flags=re.S)
        config = raw(BSP + "/bspconfig.h").decode("utf-8")
        commands = document(BSP + "/bsp_compile_commands.json")
        need(not any(re.search(r"(?:^|\s)-D\s*USE_AMP(?:\s|=|$)", p["command"]) for p in commands), "实际BSP启用了USE_AMP")
        need(re.search(r"^#define\s+XPAR_CPU_ID\s+0\s*$", config, re.M), "实际BSP不是CPU0")
        need(parser.macro_int(mmu, "NORM_WB_CACHE") == 0x15DE6 and parser.macro_int(mmu, "DEVICE_MEMORY") == 0xC06, "实际MMU宏不同")
        tables = {}
        for name in ("app_elf", "init_elf"):
            data = raw(EXPECTED[name][0])
            elf = parser.parse_elf(data)
            sections = [s for s in elf["sections"] if s["name"] == ".mmu_tbl"]
            need(len(sections) == 1 and sections[0]["size"] == 16384, "实际ELF没有完整MMU表")
            section = sections[0]
            table = struct.unpack_from("<4096I", data, section["offset"])
            need(all(table[index] == (index << 20) + 0x15DE6 for index in range(0x100, 0x120)), "实际ELF的32MiB arena启动属性不同")
            for index in range(0x100, 0x120):
                aliases = [slot for slot, descriptor in enumerate(table) if descriptor & 3 == 2 and descriptor & 0xFFF00000 == index << 20]
                need(aliases == [index], "实际MMU表存在arena第二别名")
            need(table[0x43C] == 0x43C00C02 and table[0xE00] == 0xE0000C06, "实际ELF启动CSR/UART属性不同")
            tables[name] = {"address": section["address"], "bytes": section["size"], "sha256": digest(data[section["offset"]:section["offset"] + section["size"]]), "arena_all_32_sections_wb_shareable": True, "arena_no_second_alias_in_actual_startup_table": True, "csr_startup_descriptor": "0x43c00c02", "uart_startup_descriptor": "0xe0000c06"}
        need(tables["app_elf"]["sha256"] == tables["init_elf"]["sha256"], "实际ELF MMU表字节不同")
        app = raw(BSP + "/source_snapshot/s2b_inference_app.c", build["source_sha256"]["vitis/s2b_inference_app.c"]).decode("utf-8")
        need("Xil_SetTlbAttributes((INTPTR)CSR_BASE, DEVICE_MEMORY);" in app, "实际编译应用未将CSR改为Device")
        need("Xil_DCacheFlushRange" in app and "Xil_DCacheInvalidateRange" in app, "实际应用cache维护缺失")
        return {"no_USE_AMP_in_bsp_commands": True, "cpu_id": 0, "NORM_WB_CACHE": "0x15de6", "DEVICE_MEMORY": "0xc06", "elf_tables": tables, "csr_device_retag_in_actual_app": True, "bsp_reused_from_compiled_xsa": True, "comparison_scope": "复用同一CPU0 BSP及同一ELF，结合937项PS/地址/时钟完全一致；未生成vis0新BSP。"}

    checked("same_bsp_mmu_macros", bsp_mmu)

    def addresses():
        parser = load_module("verification/check_s2b_ps_smoke_layout.py", "offline_macro_parser")
        macros = raw(BSP + "/xparameters.h").decode("utf-8")
        config = raw(BSP + "/bspconfig.h").decode("utf-8")
        expected_macros = {"XPAR_UART1_BASEADDR": 0xE0001000, "XPAR_UART1_HIGHADDR": 0xE0001FFF, "XPAR_UART1_CLOCK_FREQ": 100000000, "XPAR_INFER_BASEADDR": 0x43C00000, "XPAR_INFER_HIGHADDR": 0x43C0FFFF, "XPAR_PS7_DDR_0_BASEADDRESS": 0x100000, "XPAR_PS7_DDR_0_HIGHADDRESS": 0x3FFFFFFF}
        need(all(parser.macro_int(macros, name) == value for name, value in expected_macros.items()), "实际BSP地址/时钟不同")
        need(parser.macro_int(config, "STDIN_BASEADDRESS") == parser.macro_int(config, "STDOUT_BASEADDRESS") == 0xE0001000, "BSP串口不同")
        regions = [[p.attrib for p in tree.findall(".//MEMRANGE")] for tree in trees.values()]
        need(regions[0] == regions[1], "HWH全部MEMRANGE不同")
        for tree in trees.values():
            ps = {p.get("NAME"): p.get("VALUE") for p in tree.findall(".//MODULE[@INSTANCE='ps7']/PARAMETERS/PARAMETER")}
            for name, value in {"PCW_UART1_BASEADDR": "0xE0001000", "PCW_UART1_HIGHADDR": "0xE0001FFF", "PCW_UART1_BAUD_RATE": "115200", "PCW_UART1_UART1_IO": "MIO 48 .. 49", "PCW_ACT_UART_PERIPHERAL_FREQMHZ": "100.000000", "PCW_DDR_RAM_HIGHADDR": "0x3FFFFFFF", "PCW_FPGA0_PERIPHERAL_FREQMHZ": "50", "PCW_USE_M_AXI_GP0": "1", "PCW_USE_S_AXI_HP0": "1"}.items():
                need(ps[name] == value, "实际HWH字段不同：" + name)
        return {"bsp_macros": expected_macros, "all_hwh_memranges_equal": True, "hwh_memranges": regions[0], "uart": "UART1/MIO48..49/115200/100MHz", "pl_clock_hz": 50000000}

    checked("same_uart_ddr_csr_clocks", addresses)

    def full_core():
        profile = document("board/s2b_inference_platform.json")
        sources = profile["rtl_sources"]
        need(len(sources) == 18 and len(set(sources)) == 18, "RTL闭包不是18项")
        original_rows = {p["path"]: p["sha256"] for p in original0["files"]}
        snapshot_rows = {p["path"]: p["sha256"] for p in original1["files"]}
        git_sources = {}
        for source in sources:
            expected = original_rows[source]
            raw(source, expected)
            snapshot = V1 + "/sources/" + Path(source).name
            raw(snapshot, expected)
            need(snapshot_rows[snapshot] == expected, "编译XSA快照RTL与vis0不同")
            result = subprocess.run(["git", "show", original0["source_commit"] + ":" + source], cwd=ROOT, capture_output=True, check=False)
            actual_source = raw(source)
            need(result.returncode == 0, "vis0源码原提交不能读取：" + source)
            if result.stdout != actual_source:
                need(result.stdout.replace(b"\r\n", b"\n") == actual_source.replace(b"\r\n", b"\n"), "运行源码与原提交存在非换行差异：" + source)
            git_sources[source] = {"git_blob_sha256": digest(result.stdout), "runtime_bytes_sha256": expected, "raw_bytes_equal": result.stdout == actual_source, "only_line_endings_differ": result.stdout != actual_source, "git_show_native_exit_code": result.returncode}
        hierarchy = raw(V0 + "/synth_hierarchical_utilization.rpt").decode("utf-8")
        for name in ("s2b_stage2b_core", "s2b_network_backend", "s2b_conv_tile_engine", "s2b_maxpool_engine", "s2b_route_engine", "s2b_upsample_engine", "s2a_runtime_shell"):
            need(name in hierarchy, "实际综合层级缺失：" + name)
        for key, visibility in (("compiled_xsa", "1"), ("implemented_xsa", "0")):
            infer = trees[key].findall(".//MODULE[@INSTANCE='infer']")
            need(len(infer) == 1 and infer[0].get("MODTYPE") == "s2b_inference_top", "XSA完整核实例不符")
            parameters = {p.get("NAME"): p.get("VALUE") for p in infer[0].findall("./PARAMETERS/PARAMETER")}
            need(parameters["PROFILE_VISIBILITY_PROVEN"] == visibility, "可见性参数不是批准候选值")
        bit_members = [name for name in archive_data["implemented_xsa"] if name.endswith(".bit")]
        need(len(bit_members) == 1 and digest(archive_data["implemented_xsa"][bit_members[0]]) == EXPECTED["bit"][1], "实际部署bit与vis0 XSA不一致")
        checker = load_module("verification/check_s2b_inference_platform.py", "offline_platform_checker")
        raw("verification/check_s2b_inference_platform.py")
        closure = checker.check_static(ROOT)
        for path, expected in closure.items():
            raw(path, expected)
        return {"rtl_source_count": 18, "rtl_sha256": {s: inputs[s] for s in sources}, "git_source_comparison": git_sources, "source_sha256_for_entry": closure, "vis0_source_commit": original0["source_commit"], "vis1_source_commit": original1["source_commit"], "both_xsa_full_model_module": True, "synth_hierarchy_full_backend_present": True, "compiled_visibility": 1, "implemented_visibility": 0, "embedded_bit_matches_selected_bit": True}

    checked("full_model_core_present", full_core)

    def timing():
        result = {}
        for kind, heading in (("setup_max", "WNS"), ("hold_min", "WHS")):
            text = raw(V0 + "/postroute_" + kind + "_r02.rpt").decode("utf-8")
            need("Design State : Routed" in text and "Speed File   : -2" in text and "All user specified timing constraints are met." in text, "实际routed/-2时序报告状态不符")
            lines = text.splitlines()
            headings = [i for i, line in enumerate(lines) if line.strip().startswith(heading + "(ns)")]
            need(headings, "实际时序汇总表不可解析")
            values = lines[headings[0] + 2].split()
            need(len(values) == 8, "实际时序数值列数量不同")
            slack, total, failing, count, pulse, pulse_total, pulse_failing, pulse_count = values
            need(float(slack) >= 0 and float(total) == 0 and int(failing) == 0 and float(pulse) >= 0 and float(pulse_total) == 0 and int(pulse_failing) == 0, "实际时序失败")
            result[kind] = {"worst_slack_ns": float(slack), "total_negative_slack_ns": float(total), "failing_endpoints": int(failing), "total_endpoints": int(count), "pulse_width_slack_ns": float(pulse), "pulse_failing_endpoints": int(pulse_failing), "pulse_total_endpoints": int(pulse_count)}
        coverage = raw(V0 + "/postroute_check_timing_r02.rpt").decode("utf-8")
        for name in ("no_clock", "unconstrained_internal_endpoints", "no_input_delay", "no_output_delay"):
            need(re.search(r"checking " + name + r" \(0\)", coverage), "时序覆盖存在缺口：" + name)
        clocks = raw(V0 + "/postroute_clocks_r02.rpt").decode("utf-8")
        need(re.search(r"clk_fpga_0\s+20\.000", clocks), "实际约束时钟不是20ns")
        route = raw(V0 + "/postroute_route_status_r02.rpt").decode("utf-8")
        need(re.search(r"nets with routing errors.*:\s*0", route), "实际路由有错误")
        need(re.search(r"routable nets.*:\s*28621", route) and re.search(r"fully routed nets.*:\s*28621", route), "实际路由未全部完成")
        result["clock_period_ns"] = 20.0
        result["routing_errors"] = 0
        result["routed_nets"] = 28621
        return result

    checked("postroute_timing_pass", timing)
    entry = ast.parse(raw("vitis/run_s2b_visibility_probe.py").decode("utf-8"))
    entry_sets = {n.targets[0].id: ast.literal_eval(n.value) for n in entry.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in ("COMPAT_CHECKS", "ARTIFACT_KEYS")}
    need(entry_sets == {"COMPAT_CHECKS": COMPAT, "ARTIFACT_KEYS": ARTIFACTS}, "现有入口精确字段集合发生变化")
    host_drift = {}
    for path, expected in build["source_sha256"].items():
        actual = digest(raw(path))
        if actual != expected:
            host_drift[path] = {"compiled_sha256": expected, "current_sha256": actual}
    transport = load_module("verification/s2b_board_transport.py", "offline_transport")
    try:
        transport.verify_build(ROOT / (BSP + "/build_details.json"))
        old_build_preflight = {"status": "PASS", "function": "verify_build", "reason": "只读构建绑定检查通过；未调用运行入口或硬件。"}
    except Exception as error:
        old_build_preflight = {"status": "BLOCKED", "function": "verify_build", "reason": str(error), "sdk_uart_hardware_access": False}
    return {"scope": "visibility0_cache_probe_only", "scope_reason": "仅评估同一ELF/BSP搭配visibility0 implemented XSA/bit后执行CPU/DAP 256B预探针的兼容事实；不LOAD、不START、不走PL/HP0。", "checks": checks, "facts": facts, "errors": errors, "bound_artifacts": artifacts, "entry_contract": {"COMPAT_CHECKS": sorted(COMPAT), "ARTIFACT_KEYS": sorted(ARTIFACTS), "receipt_not_created": True, "final_runtime_config_not_created": True}, "input_sha256": dict(sorted(inputs.items())), "original_manifest_checks": {"visibility0": original0["checks"], "visibility1": original1["checks"], "build": build_manifest["checks"]}, "current_build_source_drift": host_drift, "old_build_runtime_preflight": old_build_preflight, "hardware_observations": {"current_platform_cpu_dap_probe": "NOT_RUN", "32MiB_arena_visibility": "NOT_RUN", "PL_HP0_cache_visibility": "NOT_RUN", "full_model_g0": "BLOCKED", "golden_100": "NOT_RUN", "continuous_1000": "NOT_RUN"}}


def main():
    """默认输出事实；--verify核对封存摘要，不产生缓存或新文件。"""
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    try:
        result = audit()
        need(set(result["checks"]) == COMPAT and all(result["checks"].values()), "有兼容事实受阻：" + json.dumps(result["errors"], ensure_ascii=False))
        if args.verify:
            saved = json.loads((ROOT / RUN / "summary.json").read_text(encoding="utf-8"))
            need(saved["audit"] == result, "封存摘要与现有原件/源码不符")
            print("OFFLINE_COMPAT_FACTS_VERIFIED; independent_review_not_asserted; hardware_not_run")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        print(json.dumps({"status": "BLOCKED", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
