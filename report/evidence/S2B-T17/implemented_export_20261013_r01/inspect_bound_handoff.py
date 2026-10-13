"""只读核对 C0、S15 和冻结 DCP 的软件交接事实；不调用 Vivado 或改写归档。"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).absolute().parents[4]
WORK = Path(__file__).absolute().parent
DCP_SHA = "db2aaf706c99121eada307fec80b4d69b362f1232ff17fcf65f4dd5c0015ad83"
C0_SHA = "6cff0c6afd009bf051028c4b793cc99c3c0c700002c2fdb2d247a33d2fc076a7"
PS_MEMBERS = ("ps7_init.c", "ps7_init.h", "ps7_init_gpl.c", "ps7_init_gpl.h", "ps7_init.html", "ps7_init.tcl")


def require(condition, message):
    """使用不会被 Python -O 移除的输入门禁。"""
    if not condition:
        raise RuntimeError(message)


def sha(raw):
    """计算原始字节的摘要。"""
    return hashlib.sha256(raw).hexdigest()


def file_record(path):
    """只接受已经存在的精确文件。"""
    require(path.is_file(), "精确文件不存在或目标类型错误：" + str(path))
    raw = path.read_bytes()
    return {"path": str(path), "bytes": len(raw), "sha256": sha(raw)}


def archive(raw):
    """在内存中读取成员，拒绝重复名称。"""
    with zipfile.ZipFile(io.BytesIO(raw)) as stream:
        names = stream.namelist()
        require(len(names) == len(set(names)), "归档包含重复成员")
        return {name: stream.read(name) for name in names}


def hwh_facts(members):
    """保存实际 PS 参数、地址和核心参数供独立审查。"""
    names = [name for name in members if name.endswith(".hwh")]
    require(len(names) == 1, "HWH 成员数量错误")
    tree = ET.fromstring(members[names[0]])
    modules = list(tree.iter("MODULE"))
    ps = [item for item in modules if item.get("MODTYPE") == "processing_system7"]
    require(len(ps) == 1, "PS7 实例数量错误")
    rows = ps[0].findall("PARAMETERS/PARAMETER")
    params = {item.get("NAME"): item.get("VALUE") for item in rows}
    require(len(params) == len(rows), "PS7 参数重复")
    cores = [item for item in modules if item.get("MODTYPE") == "s2b_inference_top"]
    return {"hwh_sha256": sha(members[names[0]]), "ps_parameters": params,
            "memranges": [dict(item.attrib) for item in tree.iter("MEMRANGE")],
            "full_model_core": [{"attributes": dict(item.attrib), "parameters":
                {param.get("NAME"): param.get("VALUE") for param in item.findall("PARAMETERS/PARAMETER")}}
                for item in cores]}


def main():
    """输出候选事实，不生成独审收据或平台通过结论。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--implemented-xsa", type=Path)
    parser.add_argument("--generated-bit", type=Path)
    parser.add_argument("--output", type=Path, default=WORK / "offline_handoff_facts_r01.json")
    args = parser.parse_args()
    require(args.output.parent.absolute() == WORK, "输出必须位于本准备目录")
    require(not args.output.exists(), "拒绝覆盖已有输出")
    c0 = ROOT / "report/evidence/S2B-T13/artifact_recheck_20261011_r01/s2b_inference_no_bit.xsa"
    s15 = ROOT / "report/evidence/S2B-T17/s15_platform_20261012_r01/s2b_inference_no_bit.xsa"
    dcp = ROOT / "tmp/2B/S2B-T17/s15_launch_prepare_20261012_r02/project_s15_r01/s2b_inference_candidate.runs/impl_1/s2b_inference_wrapper_postroute_physopt.dcp"
    bit_run = ROOT / "report/evidence/S2B-T17/direct_bitgen_20261013T051947Z_2635b4b7e4ba05fe"
    bit = args.generated_bit.absolute() if args.generated_bit else bit_run / "s2b_inference_wrapper_postroute_physopt.bit"
    build_path = ROOT / "report/evidence/S2B-T15/full_build_20261011_r01/build_details.json"
    build = json.loads(build_path.read_text(encoding="utf-8"))
    bindings = {name: file_record(path) for name, path in
                (("c0", c0), ("s15_no_bit", s15), ("dcp", dcp), ("bit", bit), ("build_details", build_path))}
    require(bindings["c0"]["sha256"] == C0_SHA == build["xsa_sha256"], "C0 XSA 绑定漂移")
    require(bindings["dcp"]["sha256"] == DCP_SHA, "冻结 DCP 绑定漂移")
    require(0 < bindings["bit"]["bytes"] <= 33554432, "生成 bit 为空或超过 32 MiB")
    if not args.generated_bit:
        require(bindings["bit"]["bytes"] == 4045776, "默认 bit 长度漂移")
    dcp_members = archive(dcp.read_bytes())
    hwdefs = [name for name in dcp_members if name.endswith(".hwdef")]
    require(len(hwdefs) == 1, "DCP 内 hwdef 成员数量错误")
    handoffs = {"c0": archive(c0.read_bytes()), "s15_no_bit": archive(s15.read_bytes()),
                "dcp_hwdef": archive(dcp_members[hwdefs[0]])}
    if args.implemented_xsa:
        xsa = args.implemented_xsa.absolute()
        bindings["implemented_xsa"] = file_record(xsa)
        handoffs["implemented_xsa"] = archive(xsa.read_bytes())
    facts = {name: hwh_facts(members) for name, members in handoffs.items()}
    comparisons = {}
    for name, members in handoffs.items():
        comparisons[name] = {
            "ps_parameter_count": len(facts[name]["ps_parameters"]),
            "ps_parameter_differences_from_c0": {key: [facts["c0"]["ps_parameters"].get(key), facts[name]["ps_parameters"].get(key)]
                for key in sorted(set(facts["c0"]["ps_parameters"]) | set(facts[name]["ps_parameters"]))
                if facts["c0"]["ps_parameters"].get(key) != facts[name]["ps_parameters"].get(key)},
            "ps_init_members": {member: {"sha256": sha(members[member]), "same_c0_bytes": members[member] == handoffs["c0"][member]}
                                for member in PS_MEMBERS},
            "hwh_same_s15_bytes": members["s2b_inference.hwh"] == handoffs["s15_no_bit"]["s2b_inference.hwh"]}
        if name == "implemented_xsa":
            bits = [member for member in members if member.endswith(".bit")]
            comparisons[name]["bits"] = {member: {"bytes": len(members[member]), "sha256": sha(members[member]),
                "same_generated_bit_bytes": members[member] == bit.read_bytes()} for member in bits}
    software = {}
    for name in ("xparameters.h", "bspconfig.h", "xil_mmu.h", "xil_mmu.c", "translation_table.S", "bsp_compile_commands.json"):
        declared = build["files"][name]
        path = Path(declared["path"])
        row = file_record(path)
        require(row["sha256"] == declared["sha256"], "软件构建文件绑定漂移：" + name)
        software[name] = row
        if path.suffix == ".h":
            software[name]["relevant_macros"] = [line for line in path.read_text(encoding="utf-8").splitlines()
                if line.startswith("#define") and re.search(r"UART|DDR|CPU|CLOCK|DEVICE_MEMORY|NORM|CACHE|INFER|40000000", line)]
    for name in ("elf", "initializer_elf"):
        declared = build[name]
        software[name] = file_record(Path(declared["path"]))
        require(software[name]["sha256"] == declared["sha256"], "ELF 绑定漂移：" + name)
    limitations = ["本脚本仅离线核查，实际工具运行日志须另行绑定。", "尚未获得独立 runtime 兼容批准。",
                   "未访问许可证私密文件或板卡。"]
    if not args.implemented_xsa:
        limitations.extend(["本次未指定 implemented XSA，既有 bit 的官方发现规则未动态核验。",
            "S15 no_bit 及 DCP 内 hwdef 的相等事实不替代最终官方 XSA 核验。"])
    result = {"schema_version": 1, "status": "OFFLINE_HANDOFF_FACTS_ONLY", "bindings": bindings,
              "dcp_embedded_hwdef_sha256": sha(dcp_members[hwdefs[0]]), "comparisons": comparisons,
              "hwh_facts": facts, "preserved_c0_software": software,
              "limitations": limitations}
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"output": str(args.output), "sha256": sha(args.output.read_bytes()),
        "comparisons": {name: {"ps_differences": len(row["ps_parameter_differences_from_c0"]),
            "all_six_ps_init_same": all(item["same_c0_bytes"] for item in row["ps_init_members"].values()),
            "hwh_same_s15_bytes": row["hwh_same_s15_bytes"]} for name, row in comparisons.items()}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
