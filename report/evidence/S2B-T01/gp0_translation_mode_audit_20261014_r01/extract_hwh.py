#!/usr/bin/env python3
"""从XSA提取HWH，并核对GP0转换器、时钟和reset的静态连接。"""

from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[4]
RUN_DIR = Path(__file__).resolve().parent
XSA_REL = Path(
    "report/evidence/S2B-T19/visibility1_timing_current_20261014_r01/"
    "artifacts/s2b_inference_wrapper_current.xsa"
)
T19_MANIFEST_REL = Path(
    "report/evidence/S2B-T19/visibility1_timing_current_20261014_r01/"
    "delivery_manifest.json"
)
CANDIDATE_REL = Path(
    "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
)
TOP_REL = Path("src/s2b_inference_top.sv")
T19_TOP_REL = Path(
    "report/evidence/S2B-T19/visibility1_timing_current_20261014_r01/"
    "sources/s2b_inference_top.sv"
)
EXPECTED_XSA_SHA256 = "90f8d0b9e857f8beb9d99a6264b96441f9ba9b4b0af0568dbbcc064aecba6065"
EXPECTED_HWH_SHA256 = "67e5af631d346d16640bafbd262af7a33bda0236f1a950e632c2e05c90681370"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def module_by_instance(tree: ET.Element, instance: str) -> ET.Element:
    for module in tree.iter("MODULE"):
        if module.attrib.get("INSTANCE") == instance:
            return module
    raise AssertionError(f"找不到HWH模块：{instance}")


def port_by_name(module: ET.Element, name: str) -> ET.Element:
    for port in module.findall("./PORTS/PORT"):
        if port.attrib.get("NAME") == name:
            return port
    raise AssertionError(
        f"找不到HWH端口：{module.attrib.get('INSTANCE')}.{name}"
    )


def connections(port: ET.Element) -> list[str]:
    return [
        f"{item.attrib.get('INSTANCE')}.{item.attrib.get('PORT')}"
        for item in port.findall("./CONNECTIONS/CONNECTION")
    ]


def parameters(module: ET.Element) -> dict[str, str]:
    return {
        item.attrib["NAME"]: item.attrib["VALUE"]
        for item in module.findall("./PARAMETERS/PARAMETER")
        if "NAME" in item.attrib and "VALUE" in item.attrib
    }


def bus_interfaces(module: ET.Element) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for interface in module.findall("./BUSINTERFACES/BUSINTERFACE"):
        result[interface.attrib["NAME"]] = {
            "type": interface.attrib.get("TYPE", ""),
            "protocol": next(
                (
                    item.attrib.get("VALUE", "")
                    for item in interface.findall("./PARAMETER")
                    if item.attrib.get("NAME") == "PROTOCOL"
                ),
                "",
            ),
            "data_width": interface.attrib.get("DATAWIDTH", ""),
            "id_width": next(
                (
                    item.attrib.get("VALUE", "")
                    for item in interface.findall("./PARAMETER")
                    if item.attrib.get("NAME") == "ID_WIDTH"
                ),
                "",
            ),
            "bus_name": interface.attrib.get("BUSNAME", ""),
        }
    return result


def main() -> int:
    outputs = [RUN_DIR / "s2b_inference.hwh", RUN_DIR / "hwh_extract.json"]
    if any(path.exists() for path in outputs):
        raise SystemExit("证据输出已存在；拒绝覆盖同一RunId。")

    xsa = ROOT / XSA_REL
    t19_manifest_path = ROOT / T19_MANIFEST_REL
    candidate_path = ROOT / CANDIDATE_REL
    top_path = ROOT / TOP_REL
    t19_top_path = ROOT / T19_TOP_REL

    xsa_sha256 = sha256_file(xsa)
    assert xsa_sha256 == EXPECTED_XSA_SHA256, "XSA哈希与任务输入不符"
    with zipfile.ZipFile(xsa) as archive:
        members = [name for name in archive.namelist() if name.endswith(".hwh")]
        assert members == ["s2b_inference.hwh"], f"HWH成员异常：{members}"
        hwh_bytes = archive.read(members[0])
    hwh_sha256 = sha256_bytes(hwh_bytes)
    assert hwh_sha256 == EXPECTED_HWH_SHA256, "HWH哈希与任务输入不符"
    tree = ET.fromstring(hwh_bytes)

    converter = module_by_instance(tree, "axi_gp0_lite")
    reset = module_by_instance(tree, "rst_fclk0")
    ps = module_by_instance(tree, "ps7")
    converter_params = parameters(converter)
    assert converter.attrib.get("FULLNAME") == "/axi_gp0_lite"
    assert converter.attrib.get("VLNV") == "xilinx.com:ip:axi_protocol_converter:2.1"
    assert converter_params.get("SI_PROTOCOL") == "AXI3"
    assert converter_params.get("MI_PROTOCOL") == "AXI4LITE"
    assert converter_params.get("ADDR_WIDTH") == "32"
    assert converter_params.get("DATA_WIDTH") == "32"
    assert converter_params.get("ID_WIDTH") == "12"
    assert converter_params.get("C_IGNORE_ID") == "0"
    assert converter_params.get("C_TRANSLATION_MODE") == "0"
    assert converter_params.get("TRANSLATION_MODE") == "0"

    len_ports: dict[str, dict[str, object]] = {}
    for direction, ps_name, si_name in (
        ("write", "M_AXI_GP0_AWLEN", "s_axi_awlen"),
        ("read", "M_AXI_GP0_ARLEN", "s_axi_arlen"),
    ):
        ps_port = port_by_name(ps, ps_name)
        si_port = port_by_name(converter, si_name)
        ps_to_converter = connections(ps_port)
        converter_to_ps = connections(si_port)
        expected_converter_path = f"axi_gp0_lite.{si_name}"
        expected_ps_path = f"ps7.{ps_name}"
        assert expected_converter_path in ps_to_converter, (
            f"PS LEN端口未连接到转换器：{ps_name} -> {ps_to_converter}"
        )
        assert expected_ps_path in converter_to_ps, (
            f"转换器SI LEN端口未连接到PS：{si_name} -> {converter_to_ps}"
        )
        len_ports[direction] = {
            "ps_pin": ps_name,
            "ps_width_bits": int(ps_port.attrib["LEFT"])
            - int(ps_port.attrib["RIGHT"])
            + 1,
            "converter_si_pin": si_name,
            "converter_width_bits": int(si_port.attrib["LEFT"])
            - int(si_port.attrib["RIGHT"])
            + 1,
            "static_connection": True,
            "runtime_value": "not inferable from HWH",
        }

    fclk = port_by_name(ps, "FCLK_CLK0")
    ps_gp0_aclk = port_by_name(ps, "M_AXI_GP0_ACLK")
    converter_aclk = port_by_name(converter, "aclk")
    reset_clk = port_by_name(reset, "slowest_sync_clk")
    expected_clock = "ps7.FCLK_CLK0"
    for port in (ps_gp0_aclk, converter_aclk, reset_clk):
        assert expected_clock in connections(port), (
            f"时钟端口未连接到FCLK_CLK0：{port.attrib.get('NAME')}"
        )
    clock_hz = int(fclk.attrib["CLKFREQUENCY"])
    assert clock_hz == 50_000_000

    reset_input = port_by_name(reset, "ext_reset_in")
    reset_output = port_by_name(reset, "peripheral_aresetn")
    converter_reset = port_by_name(converter, "aresetn")
    infer = module_by_instance(tree, "infer")
    infer_reset = port_by_name(infer, "cold_resetn")
    assert "ps7.FCLK_RESET0_N" in connections(reset_input)
    assert "rst_fclk0.peripheral_aresetn" in connections(converter_reset)
    reset_fanout = connections(reset_output)
    assert "axi_gp0_lite.aresetn" in reset_fanout
    assert "infer.cold_resetn" in reset_fanout
    assert connections(infer_reset) == ["rst_fclk0.peripheral_aresetn"]

    t19_manifest = json.loads(t19_manifest_path.read_text(encoding="utf-8"))
    t19_source_item = next(
        item
        for item in t19_manifest["files"]
        if item["path"].endswith("/sources/s2b_inference_top.sv")
    )
    current_head = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    current_top_sha = sha256_file(top_path)
    t19_top_sha = sha256_file(t19_top_path)
    assert current_top_sha == t19_source_item["sha256"]
    assert current_top_sha == t19_top_sha

    reset_params = parameters(reset)
    hwh_out = RUN_DIR / "s2b_inference.hwh"
    json_out = RUN_DIR / "hwh_extract.json"
    data = {
        "audit": {
            "task_id": "S2B-T01-G0",
            "run_id": RUN_DIR.name,
            "scope": "offline_static_xsa_hwh_audit",
            "worktree_head": current_head,
            "candidate_document": {
                "path": CANDIDATE_REL.as_posix(),
                "sha256": sha256_file(candidate_path),
            },
            "current_rtl_source": {
                "path": TOP_REL.as_posix(),
                "sha256": current_top_sha,
            },
        },
        "xsa": {
            "path": XSA_REL.as_posix(),
            "sha256": xsa_sha256,
            "hwh_member": members[0],
            "hwh_member_sha256": hwh_sha256,
            "hwh_extracted_path": hwh_out.relative_to(ROOT).as_posix(),
            "hwh_bytes": len(hwh_bytes),
        },
        "source_provenance": {
            "original_t19_manifest": {
                "path": T19_MANIFEST_REL.as_posix(),
                "sha256": sha256_file(t19_manifest_path),
                "source_commit": t19_manifest["source_commit"],
                "vivado": t19_manifest.get("tool_versions", {}).get("Vivado"),
            },
            "t19_top_snapshot": {
                "path": T19_TOP_REL.as_posix(),
                "sha256": t19_top_sha,
            },
            "current_top_matches_t19_snapshot": current_top_sha == t19_top_sha,
        },
        "converter": {
            "instance": converter.attrib["INSTANCE"],
            "full_name": converter.attrib["FULLNAME"],
            "vlnv": converter.attrib["VLNV"],
            "parameters": {
                key: converter_params[key]
                for key in (
                    "SI_PROTOCOL",
                    "MI_PROTOCOL",
                    "ADDR_WIDTH",
                    "DATA_WIDTH",
                    "ID_WIDTH",
                    "C_IGNORE_ID",
                    "C_TRANSLATION_MODE",
                    "TRANSLATION_MODE",
                )
            },
            "interfaces": bus_interfaces(converter),
            "ps_m_axi_gp0_len_pins": len_ports,
        },
        "clock": {
            "source": "ps7.FCLK_CLK0",
            "nominal_hz": clock_hz,
            "fanout": connections(fclk),
            "ps_m_axi_gp0_aclk": connections(ps_gp0_aclk),
            "converter_aclk": connections(converter_aclk),
            "reset_controller_slowest_sync_clk": connections(reset_clk),
            "static_only": True,
        },
        "reset": {
            "controller_instance": reset.attrib["INSTANCE"],
            "controller_vlnv": reset.attrib["VLNV"],
            "parameters": {
                "C_NUM_INTERCONNECT_ARESETN": reset_params.get(
                    "C_NUM_INTERCONNECT_ARESETN"
                ),
                "C_NUM_PERP_ARESETN": reset_params.get("C_NUM_PERP_ARESETN"),
            },
            "ext_reset_in_from": connections(reset_input),
            "sync_clock_from": connections(reset_clk),
            "peripheral_aresetn_fanout": reset_fanout,
            "converter_aresetn_from": connections(converter_reset),
            "infer_cold_resetn_from": connections(infer_reset),
            "static_only": True,
        },
        "interpretation_limits": [
            "HWH端口连线不提供PS运行事务的AWLEN或ARLEN取值。",
            "静态XSA/HWH不提供AXI READY背压、响应序列或实板事务记录。",
            "reset连线与名义时钟频率不证明实物reset波形、释放时序或复位重叠。",
            "提取成功及配置匹配不代表G0通过、接口冻结或实物验收。",
        ],
        "tool_versions": {
            "python": platform.python_version(),
            "vivado_in_audit_environment": shutil.which("vivado"),
        },
    }
    hwh_out.write_bytes(hwh_bytes)
    json_out.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": "PASS_STATIC_EXTRACTION_ONLY",
                "hwh_sha256": hwh_sha256,
                "json_sha256": sha256_file(json_out),
                "candidate_sha256": data["audit"]["candidate_document"]["sha256"],
                "worktree_head": current_head,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
