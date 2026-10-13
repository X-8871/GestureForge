"""独立核查编译门禁、ELF页表、时序原报告及官方位流提取。"""
import json
from pathlib import Path
import re
import struct
import sys
from audit import ROOT, OUT, RUN, archive, bind, exact, raw, read_json, require, sha


def elf_mmu(data):
    """按ELF32实际符号定位页表并读取DDR/CSR两个项。"""
    require(data[:6] == b"\x7fELF\x01\x01", "不是小端ELF32")
    header = struct.unpack_from("<16sHHIIIIIHHHHHH", data)
    table, stride, count = header[6], header[11], header[12]
    sections = [struct.unpack_from("<10I", data, table + stride * index) for index in range(count)]
    symbols = []
    for section in sections:
        if section[1] != 2:
            continue
        strings = sections[section[6]]
        names = data[strings[4]:strings[4] + strings[5]]
        for pos in range(section[4], section[4] + section[5], section[9]):
            name, address, size, info, other, section_index = struct.unpack_from("<IIIBBH", data, pos)
            end = names.find(b"\0", name)
            if names[name:end] == b"MMUTable":
                symbols.append((address, size, section_index))
    require(len(symbols) == 1, "MMUTable符号必须唯一")
    address, size, index = symbols[0]
    section = sections[index]
    offset = section[4] + address - section[3]
    require(size in (0, 16384), "页表符号长度异常")
    ddr = struct.unpack_from("<I", data, offset + 0x100 * 4)[0]
    csr = struct.unpack_from("<I", data, offset + 0x43C * 4)[0]
    require(ddr == 0x10015DE6 and csr == 0x43C00C02, "编译页表项不符合DDR缓存及PL有序映射")
    return {"symbol_address": hex(address), "symbol_size": size, "ddr_0x10000000_entry": hex(ddr),
            "csr_0x43c00000_initial_entry": hex(csr)}


def main():
    """执行只读原始门禁，不生成运行兼容批准。"""
    facts = read_json(OUT / "independent_facts_r01.json")
    sys.path.insert(0, str(ROOT / "verification"))
    import s2b_board_transport as transport
    require(Path(transport.__file__).absolute() == ROOT / "verification/s2b_board_transport.py", "实际build verifier来源错误")
    build_path, build = transport.verify_build(Path(facts["bindings"]["build_details"]["path"]))
    for name, digest in build["source_sha256"].items():
        require(bind(ROOT / name)["sha256"] == digest, "编译来源发生漂移")
    pnr = read_json(Path(facts["pnr"]["binding"]["path"]))
    fixed = pnr["fixed_postroute_checkpoint"]
    checkpoint = bind(Path(fixed["path"]))
    require(checkpoint["sha256"] == fixed["sha256"] and checkpoint["bytes"] == fixed["bytes"], "PNR独审固定DCP漂移")
    sta = read_json(ROOT / "report/evidence/S2B-T17/s15_postroute_20261012_r01/pnr_sta_result.json")
    report = bind(ROOT / sta["report"]["path"])
    require(report["sha256"] == sta["report"]["sha256"], "实际PNR时序原报告漂移")
    require(sta["design_state"] == "Physopt postRoute" and sta["timing"]["wns_ns"] == 0.007
            and sta["timing"]["whs_ns"] == 0.087 and all(value == 0 for value in sta["check_timing"].values()), "PNR时序事实不符合审批范围")
    require(not facts["pnr"]["current_source_drift"], "PNR到当前源码闭包漂移")
    handoff = facts["hwh_facts"]
    require(handoff["implemented_xsa"]["memranges"] == handoff["compiled_xsa"]["memranges"], "编译与实现地址映射不一致")
    cores = handoff["implemented_xsa"]["cores"]
    require(len(cores) == 1 and cores[0]["parameters"]["PROFILE_VISIBILITY_PROVEN"] == "0"
            and cores[0]["parameters"]["C_BASEADDR"] == "0x43C00000"
            and cores[0]["parameters"]["C_HIGHADDR"] == "0x43C0FFFF", "全模型核心门控或CSR边界错误")
    for key, item in facts["comparisons"].items():
        require(item["same_ps_parameters_compiled"] and item["ps_parameter_count"] == 937
                and all(row["same_compiled"] for row in item["ps_init"].values()), "PS配置/初始化不相等")
    headers = raw(Path(build["files"]["xparameters.h"]["path"])).decode("utf-8")
    macros = dict(re.findall(r"^#define\s+(\w+)\s+([^\s/]+)", headers, re.M))
    expected = {"XPAR_UART1_BASEADDR": 0xE0001000, "XPAR_UART1_CLOCK_FREQ": 100000000,
                "XPAR_INFER_BASEADDR": 0x43C00000, "XPAR_INFER_HIGHADDR": 0x43C0FFFF,
                "XPAR_PS7_DDR_0_BASEADDRESS": 0x100000, "XPAR_PS7_DDR_0_HIGHADDRESS": 0x3FFFFFFF,
                "XPAR_CPU_CORE_CLOCK_FREQ_HZ": 666666687}
    for name, value in expected.items():
        require(int(macros[name], 0) == value, "BSP宏值错误：" + name)
    mmu_header = raw(Path(build["files"]["xil_mmu.h"]["path"])).decode("utf-8")
    require(re.search(r"^#define\s+DEVICE_MEMORY\s+0xC06\b", mmu_header, re.M) is not None
            and re.search(r"^#define\s+NORM_WB_CACHE\s+0x15DE6\b", mmu_header, re.M) is not None, "MMU宏错误")
    app_source = raw(ROOT / "vitis/s2b_inference_app.c").decode("utf-8")
    require("Xil_SetTlbAttributes((INTPTR)CSR_BASE, DEVICE_MEMORY);" in app_source
            and "Xil_DCacheEnable();" in app_source and "flush_range(0U, 256U)" in app_source
            and "invalidate_range(0U, 256U)" in app_source, "实际缓存探针实现不匹配")
    deployment_path = ROOT / "report/evidence/S2B-T17/implemented_export_20261013_r01/s2b_inference_implemented.bit"
    xsa = archive(raw(Path(facts["bindings"]["implemented_xsa"]["path"])))
    member = facts["embedded_bit"]["member"]
    require(raw(deployment_path) == xsa[member], "实际部署候选不是XSA原始位流成员")
    output = {"status": "INDEPENDENT_OFFLINE_COMPATIBILITY_BASIS_ONLY", "actual_transport_verify_build": "PASS",
              "actual_build_sources": build["source_sha256"], "fixed_pnr_dcp": checkpoint, "actual_pnr_report": report,
              "elf_mmu": elf_mmu(raw(Path(build["elf"]["path"]))), "bsp_macros": expected,
              "visibility_parameter": 0, "addresses_match_actual_implemented_hwh": True,
              "full_model_core_bound_by_current_and_pnr_source_closure": True,
              "official_xsa_embedded_bit_extraction": bind(deployment_path),
              "same_xsa_embedded_bit_bytes": True,
              "initial_csr_map": "Strongly Ordered 0xc02，实际初始化按已绑定DEVICE_MEMORY=0xc06改为Device",
              "limits": "仅离线visibility0缓存探针兼容依据；不证明冷恢复或实板缓存通过，不允许visibility1整网部署。"}
    destination = OUT / "supplement_facts_r01.json"
    with destination.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(output, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"output": str(destination), "sha256": sha(destination.read_bytes()), "elf_mmu": output["elf_mmu"],
                      "deployment_bit": output["official_xsa_embedded_bit_extraction"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
