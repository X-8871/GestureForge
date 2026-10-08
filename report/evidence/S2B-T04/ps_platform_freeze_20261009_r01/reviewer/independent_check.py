"""核对全新复建、候选实物描述、历史源码映射及防覆盖实际证据。"""

import hashlib
import json
import pathlib
import re
import tkinter
import xml.etree.ElementTree as ET
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[4]
REVIEW = pathlib.Path(__file__).resolve().parent
RUN = ROOT / "report/evidence/S2B-T04/ps_platform_20261008_r02"
CANDIDATE = RUN / "candidate_attempt1"
OLD = ROOT / "report/evidence/S2B-T04/ps_platform_20261008_r01"
TCL = tkinter.Tcl()


def read_json(path):
    """按 UTF-8 读取机器证据。"""
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    """绑定文件原字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_dict(text):
    """按 Tcl 数据列表解析，绝不执行证据源码。"""
    parts = TCL.splitlist(text)
    assert len(parts) % 2 == 0
    return dict(zip(parts[::2], parts[1::2]))


def data_file(path):
    """读取证据包中的 data 字典。"""
    return parse_dict(parse_dict(path.read_text(encoding="utf-8"))["data"])


def tool_result(receipt):
    """只解析实际回执的 JSON 内容。"""
    return json.loads(receipt["content"][0]["text"])


def canonical_xml(element):
    """仅去掉 HWH 根节点的时间戳，比较完整结构与其余属性。"""
    attributes = dict(element.attrib)
    if element.tag == "EDKSYSTEM":
        attributes.pop("TIMESTAMP", None)
    return (element.tag, tuple(sorted(attributes.items())), (element.text or "").strip(), tuple(canonical_xml(child) for child in element))


fields = read_json(ROOT / "board/ps_platform_fields.json")
delivery = read_json(RUN / "delivery_manifest.json")
inputs = read_json(RUN / "inputs_manifest.json")
assert len(delivery["files"]) == 178 and len(inputs["files"]) == 15
for manifest in (delivery, inputs):
    assert not manifest["interfaces"] and manifest["interfaces_not_applicable_reason"]
    for entry in manifest["files"]:
        file = ROOT / entry["path"]
        assert file.is_file() and sha(file) == entry["sha256"], entry["path"]

mapping = read_json(RUN / "source_prior_mapping.json")
assert len(mapping["source_mappings"]) == 3 and len(mapping["prior_run_files"]) == 100
old_sources = {}
for item in mapping["source_mappings"]:
    file = ROOT / item["snapshot_path"]
    assert file.is_file() and sha(file) == item["sha256"] and file.stat().st_size == item["bytes"]
    old_sources[item["original_path"]] = file
for item in mapping["prior_run_files"]:
    file = ROOT / item["path"]
    assert file.is_file() and sha(file) == item["sha256"] and file.stat().st_size == item["bytes"]
old_counts = {}
for name, count in (("delivery_manifest.json", 102), ("inputs_manifest.json", 12)):
    manifest = read_json(OLD / name)
    assert len(manifest["files"]) == count
    for entry in manifest["files"]:
        file = old_sources.get(entry["path"], ROOT / entry["path"])
        assert file.is_file() and sha(file) == entry["sha256"], entry["path"]
    old_counts[name] = count

fresh = tool_result(read_json(REVIEW / "fresh_session_receipt.json"))
assert fresh["exit_code"] == 0 and "CURRENT_PROJECT {} HELPER_NAMESPACE 0 HELPER_API 0" in fresh["output"]
rebuild = tool_result(read_json(REVIEW / "rebuild_receipt.json")["result"])
assert rebuild["exit_code"] == 0 and rebuild["output"].endswith("PS_PLATFORM:OFFLINE_CANDIDATE_OK")
own_start = tool_result(read_json(REVIEW / "startup_receipt.json"))
candidate_start = tool_result(read_json(RUN / "startup_receipt.json")["result"])
assert own_start["process_id"] == 30012 and own_start["session_id"] == "vivado-20261009-001132-1a6316ad"
source = (ROOT / "vivado/s2b_ps_platform.tcl").read_text(encoding="utf-8")
body = source.split("proc ::s2b_ps_platform::requested {} {", 1)[1].split("proc ::s2b_ps_platform::configure", 1)[0]
request = dict(re.findall(r"(CONFIG\.[A-Za-z0-9_]+) \{([^{}]*)\}", body))
assert len(request) == 50

init_bytes = {}
handoffs = {}
wrapper_bodies = {}
native_stages = {}
for label, artifact, start, native in (
    ("candidate", CANDIDATE, candidate_start, RUN / "vivado_native.log"),
    ("reviewer", REVIEW / "evidence", own_start, pathlib.Path(own_start["log_file"])),
):
    load = data_file(artifact / "helper_load.tcldict")
    for key, value in {"helper_preexisting": "0", "helper_namespace_before": "0", "helper_namespace_after": "1", "api_origin": "::ipcfg::help", "nested_namespace_present": "0", "initial_source_global": "1"}.items():
        assert load[key] == value, (label, key)
    bd = read_json(artifact / "s2b_ps_only.bd")["design"]
    assert bd["design_info"]["device"] == "xc7z020clg400-2" and bd["design_info"]["validated"] == "true"
    assert list(bd["components"]) == ["ps7"] and set(bd["interface_ports"]) == {"DDR_0", "FIXED_IO_0"}
    assert "ports" not in bd
    bd_params = {key: value["value"] for key, value in bd["components"]["ps7"]["parameters"].items()}
    readback = dict(line.split("\t", 1) for line in (artifact / "readback.tsv").read_text(encoding="utf-8").splitlines()[1:])
    baseline = data_file(artifact / "baseline.tcldict")
    interface = data_file(artifact / "interfaces.tcldict")
    assert TCL.splitlist(interface["cells"]) == ("/ps7",)
    assert set(TCL.splitlist(interface["interfaces"])) == {"/ps7/DDR", "/ps7/FIXED_IO"}
    assert not any(re.search(r"AXI|FCLK|FRESET", name) for name in TCL.splitlist(interface["scalar_pins"]))
    with zipfile.ZipFile(artifact / "s2b_ps_only.xsa") as archive:
        assert archive.testzip() is None
        assert not any(name.lower().endswith((".bit", ".dcp")) for name in archive.namelist())
        handoff = ET.fromstring(archive.read("s2b_ps_only.hwh"))
        handoffs[label] = canonical_xml(handoff)
        modules = list(handoff.iter("MODULE"))
        assert len(modules) == 1 and modules[0].get("MODTYPE") == "processing_system7"
        module = modules[0]
        params = {item.get("NAME"): item.get("VALUE") for item in module.find("PARAMETERS") if item.get("VALUE") is not None}
        for field in fields["fields"]:
            key = field["parameter"]
            plain = key.removeprefix("CONFIG.")
            assert readback[key] == params[plain] == field["actual"], (label, key)
            if plain in bd_params:
                assert bd_params[plain] == field["actual"]
            if field["role"] == "requested":
                assert request[key] == field["candidate"] == field["actual"] and baseline[key] == field["baseline"]
            if key.startswith(("CONFIG.PCW_USE_", "CONFIG.PCW_EN_CLK", "CONFIG.PCW_EN_RST")):
                assert field["actual"] == "0"
        for key, value in {"PCW_UART1_UART1_IO": "MIO 48 .. 49", "PCW_PRESET_BANK1_VOLTAGE": "LVCMOS 1.8V", "PCW_MIO_48_DIRECTION": "out", "PCW_MIO_49_DIRECTION": "in", "PCW_UART1_BASEADDR": "0xE0001000", "PCW_UART1_HIGHADDR": "0xE0001FFF", "PCW_UIPARAM_DDR_BUS_WIDTH": "32 Bit", "PCW_UIPARAM_DDR_DRAM_WIDTH": "16 Bits", "PCW_UIPARAM_DDR_DEVICE_CAPACITY": "4096 MBits", "PCW_UIPARAM_DDR_CL": "7", "PCW_UIPARAM_DDR_CWL": "6"}.items():
            assert params[key] == value
        assert 2 ** (15 + 10 + 3) * 4 == 1073741824
        init_bytes[label] = {name: archive.read(name) for name in ("ps7_init.c", "ps7_init.h", "ps7_init.tcl")}
        if label == "candidate":
            for name, value in init_bytes[label].items():
                assert value == (artifact / name).read_bytes()
        hardware = ET.fromstring(archive.read("hwdef.xml"))
        assert hardware.find("SYSTEMINFO").get("PART") == "xc7z020clg400-2" and hardware.find("MODE").get("Name") == "Pre-Synthesis"
        assert json.loads(archive.read("xsa.json"))["platformState"] == "pre_synth"
        ports = {item.get("NAME"): item.attrib for item in module.find("PORTS")}
        assert not any(re.search(r"AXI|FCLK|FRESET", name) for name in ports)
        assert {item.get("NAME") for item in module.find("BUSINTERFACES")} == {"DDR", "FIXED_IO"}
    wrapper_file = artifact / "s2b_ps_only_wrapper.v"
    assert wrapper_file.is_file()
    wrapper = wrapper_file.read_text(encoding="utf-8")
    wrapper_bodies[label] = wrapper[wrapper.index("`timescale"):]
    for logical, pin, physical, left in (("DQ", "DDR_DQ", "DDR_0_dq", 31), ("ADDR", "DDR_Addr", "DDR_0_addr", 14), ("BA", "DDR_BankAddr", "DDR_0_ba", 2), ("DM", "DDR_DM", "DDR_0_dm", 3), ("DQS_N", "DDR_DQS_n", "DDR_0_dqs_n", 3), ("DQS_P", "DDR_DQS", "DDR_0_dqs_p", 3)):
        port_map = bd["interface_ports"]["DDR_0"]["port_maps"][logical]
        assert port_map["left"] == str(left) and port_map["right"] == "0" and port_map["physical_name"] == physical
        assert ports[pin]["LEFT"] == str(left) and ports[pin]["RIGHT"] == "0"
        assert re.search(rf"inout\s+\[{left}:0\]\s*{re.escape(physical)};", wrapper)
    native_bytes = native.read_bytes()
    native_stages[label] = {}
    for stage in ("configure", "validate", "products", "products_recheck", "export"):
        capture = data_file(artifact / (stage + ".tcldict"))
        assert capture["code"] == "0" and capture["error_count"] == "0" and capture["critical_count"] == "0"
        assert capture["native_log_source"] == start["log_file"]
        assert capture["status"] == ("FAIL" if stage == "products" else "OK")
        if stage == "products":
            assert capture["capture_error"] == "CAPTURE_FAIL:native message export incomplete or counters changed: WARNING emitted=-9 exported=0"
        begin, end = map(int, TCL.splitlist(capture["native_log_offsets"]))
        current = (artifact / (stage + ".tcldict.native.log")).read_bytes()
        assert native_bytes[begin:end] == current
        text = current.decode("utf-8", errors="replace")
        assert not re.search(r"^(?:ERROR|CRITICAL WARNING):", text, re.MULTILINE)
        assert not re.search(r"Cannot set the parameter|Invalid parameter|disabled parameter|Ignoring", text)
        native_stages[label][stage] = {"status": capture["status"], "offsets": [begin, end], "sha256": hashlib.sha256(current).hexdigest()}

assert (CANDIDATE / "s2b_ps_only.bd").read_bytes() == (REVIEW / "evidence/s2b_ps_only.bd").read_bytes()
assert init_bytes["candidate"] == init_bytes["reviewer"]
assert handoffs["candidate"] == handoffs["reviewer"] and wrapper_bodies["candidate"] == wrapper_bodies["reviewer"]
before = data_file(REVIEW / "evidence/reviewer_guard_before_close.tcldict")
after = data_file(REVIEW / "evidence/reviewer_guard_after_close.tcldict")
guard_count = 0
for data, expected in ((before, 7), (after, 3)):
    guards = parse_dict(data["guards"])
    assert len(guards) == expected and all(TCL.splitlist(value)[0] == "1" for value in guards.values())
    guard_count += len(guards)
assert before["request_stuck"] == "" and after["current_project"] == ""
assert before["api_origin"] == after["api_origin"] == "::ipcfg::help"
assert after["nested_namespace"] == before["nested_namespace"] == "0"
for name in ("unexpected_project", "unexpected_evidence", "unexpected_prepare", "relative_path", "unexpected_evidence_closed", "unexpected_project_closed", "unexpected_missing_evidence", "missing_parent"):
    assert not (REVIEW / name).exists()
attempts = parse_dict((REVIEW / "evidence/attempts.tcldict").read_text(encoding="utf-8"))
assert set(attempts) == {"s2b_ps_only /defaults", "s2b_ps_only /ps7"}
assert all(parse_dict(value)["count"] == "1" and parse_dict(value)["code"] == "0" for value in attempts.values())

checks = {item["name"]: item for item in delivery["checks"]}
assert checks["末尾非必要拒绝覆盖与关闭状态查询"]["status"] == "BLOCKED" and checks["末尾非必要拒绝覆盖与关闭状态查询"]["exit_code"] is None
calls = read_json(RUN / "vivado_calls.json")
assert isinstance(calls, list)
for call in calls:
    result = tool_result(call["result"])
    assert result["exit_code"] == 0
    if call["step"] == "fresh_full_candidate_attempt1":
        assert result["elapsed_seconds"] == 24.707 and call["source_sha256"] == sha(ROOT / "vivado/s2b_ps_platform.tcl")
        assert result["output"].endswith("PS_PLATFORM:OFFLINE_CANDIDATE_OK")

print(json.dumps({"status": "INDEPENDENT_REBUILD_AND_BINDINGS_PASS", "rebuild_exit_code": rebuild["exit_code"], "rebuild_elapsed_seconds": rebuild["elapsed_seconds"], "delivery_bindings": 178, "input_bindings": 15, "historical_files": 100, "historical_manifest_bindings": old_counts, "source_snapshots": 3, "fields_checked": 73, "requested_checked": 50, "guard_count": guard_count, "fresh_helper_namespace_before": 0, "fresh_helper_namespace_after": 1, "nested_helper_namespace": 0, "candidate_xsa_sha256": sha(CANDIDATE / "s2b_ps_only.xsa"), "reviewer_xsa_sha256": sha(REVIEW / "evidence/s2b_ps_only.xsa"), "bd_sha256": sha(CANDIDATE / "s2b_ps_only.bd"), "init_sha256": {name: hashlib.sha256(value).hexdigest() for name, value in init_bytes["reviewer"].items()}, "hwh_full_semantics_equal_except_root_timestamp": True, "wrapper_body_equal": True, "native_stages": native_stages, "limits": ["原开发末尾UNKNOWN查询仍为BLOCKED，本次防覆盖由独立实际运行补充。", "仅离线G2，不代表实板profile或阶段2B G0/G3/G5。"]}, ensure_ascii=False, separators=(",", ":")))
