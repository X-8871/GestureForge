"""只读核验 R2 候选、全局首次加载事实及映射到旧源码快照的 r01 绑定。"""

import csv
import hashlib
import json
from pathlib import Path
import re
import sys
import tkinter
import xml.etree.ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).absolute().parents[4]
RUN = ROOT / "report/evidence/S2B-T04/ps_platform_20261008_r02"
CANDIDATE = RUN / "candidate_attempt1"
PRIOR = ROOT / "report/evidence/S2B-T04/ps_platform_20261008_r01"
TCL = tkinter.Tcl()


def require(condition, message):
    """任何未通过条件都以非零退出，不受 Python 优化选项影响。"""
    if not condition:
        raise ValueError(message)


def read_bytes(path):
    """按既有字面路径读取普通文件，不猜测或替换分隔符。"""
    require(path.is_file(), f"缺少文件：{path}")
    return path.read_bytes()


def sha(path):
    return hashlib.sha256(read_bytes(path)).hexdigest()


def read_json(path):
    return json.loads(read_bytes(path).decode("utf-8"))


def tcl_dict(text):
    """只拆分 Tcl list，不求值或 source 原始证据。"""
    items = TCL.splitlist(text)
    require(len(items) % 2 == 0, "Tcl dict 奇数项")
    result = dict(zip(items[::2], items[1::2]))
    require(len(result) * 2 == len(items), "Tcl dict 重复键")
    return result


def record(name):
    envelope = tcl_dict(read_bytes(CANDIDATE / name).decode("utf-8"))
    require(envelope["schema_version"] == "1", "证据 schema 错误")
    return tcl_dict(envelope["data"])


def receipt(result):
    return json.loads(result["content"][0]["text"])


def check_candidate():
    fields = read_json(ROOT / "board/ps_platform_fields.json")
    require(fields["part"] == "xc7z020clg400-2", "目标器件错误")
    with (CANDIDATE / "readback.tsv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    actual = {row["parameter"]: row["actual"] for row in rows}
    require(len(actual) == len(rows) == len(fields["fields"]) == 73, "读回字段数量错误")
    source_parameters = set()
    for field in fields["fields"]:
        key = field["parameter"]
        require(key not in source_parameters, "来源字段重复")
        source_parameters.add(key)
        require(actual[key] == field["actual"], f"字段表读回不符：{key}")
        require(field["source_ids"] and all(s in fields["sources"] for s in field["source_ids"]), "来源缺失")
        if field["role"] == "requested":
            require(field["candidate"] == actual[key], f"请求回退：{key}")
    script = read_bytes(ROOT / "vivado/s2b_ps_platform.tcl").decode("utf-8")
    section = script.split("proc ::s2b_ps_platform::requested {} {", 1)[1].split("proc ::s2b_ps_platform::configure", 1)[0]
    requested = dict(re.findall(r"(CONFIG\.[A-Z0-9_]+) \{([^}]*)\}", section))
    require(len(requested) == sum(f["role"] == "requested" for f in fields["fields"]) == 50, "请求数量错误")
    require(all(actual[k] == v for k, v in requested.items()), "Tcl 请求与读回不同")
    bd = read_json(CANDIDATE / "s2b_ps_only.bd")["design"]
    require(bd["design_info"]["device"] == fields["part"] and bd["design_info"]["validated"] == "true", "BD 未验证或器件不同")
    require(list(bd["components"]) == ["ps7"], "BD 不止一个 PS7")
    require(set(bd["interface_ports"]) == {"DDR_0", "FIXED_IO_0"}, "外部接口错误")
    ports = bd["interface_ports"]["DDR_0"]["port_maps"]
    require((ports["DQ"]["left"], ports["DQ"]["right"]) == ("31", "0"), "DQ 物理连接宽度错误")
    require((ports["ADDR"]["left"], ports["BA"]["left"]) == ("14", "2"), "DDR 地址连接错误")
    require(bd["interface_ports"]["FIXED_IO_0"]["port_maps"]["MIO"]["left"] == "53", "MIO 连接错误")
    with ZipFile(CANDIDATE / "s2b_ps_only.xsa") as archive:
        require(archive.testzip() is None, "XSA ZIP 损坏")
        names = archive.namelist()
        require(not any(n.lower().endswith((".bit", ".bin", ".mcs")) for n in names), "XSA 含位流")
        hwh = ET.fromstring(archive.read("s2b_ps_only.hwh"))
        modules = hwh.findall(".//MODULE")
        require(len(modules) == 1 and modules[0].attrib["MODTYPE"] == "processing_system7" and modules[0].attrib["IS_PL"] == "FALSE", "HWH 非 PS-only")
        wanted = {k.removeprefix("CONFIG.") for k in actual}
        parameter_rows = [p for p in modules[0].findall(".//PARAMETER") if p.attrib.get("NAME") in wanted]
        parameters = {p.attrib["NAME"]: p.attrib["VALUE"] for p in parameter_rows}
        require(len(parameters) == len(parameter_rows) == 73, "HWH 实际字段缺失或重复")
        require(all(parameters[k.removeprefix("CONFIG.")] == v for k, v in actual.items()), "HWH 与读回不同")
        for name in ("ps7_init.c", "ps7_init.h", "ps7_init.tcl"):
            require(read_bytes(CANDIDATE / name) == archive.read(name), f"XSA 初始化字节不同：{name}")
    wrapper = read_bytes(CANDIDATE / "s2b_ps_only_wrapper.v").decode("utf-8")
    require(re.search(r"inout\s*\[31:0\]\s*DDR_0_dq", wrapper), "wrapper DDR 宽度错误")
    require(not re.search(r"\b[MS]_AXI_|FCLK_", wrapper), "wrapper 有 PL AXI/时钟")
    artifacts = fields["candidate_artifacts"]
    for key, name in (("xsa", "s2b_ps_only.xsa"), ("bd", "s2b_ps_only.bd"), ("wrapper", "s2b_ps_only_wrapper.v")):
        require(sha(CANDIDATE / name) == artifacts[key + "_sha256"], "字段表产物 SHA 不符")
    require(fields["sources"]["current_readback"]["sha256"] == sha(CANDIDATE / "readback.tsv"), "字段表 readback SHA 不符")
    for name in ("vivado/s2b_ps_platform.tcl", "board/ps_platform_fields.json", "board/ps_platform.md"):
        raw = read_bytes(ROOT / name)
        raw.decode("utf-8")
        require(b"\r" not in raw, f"当前源码非 LF：{name}")
    return {"requested_parameters": len(requested), "readback_parameters": len(actual), "bd_cells": list(bd["components"]), "external_interfaces": list(bd["interface_ports"]), "xsa_entries": names, "contains_bitstream": False}


def check_fresh_helper_and_capture():
    calls = read_json(RUN / "vivado_calls.json")
    probe = receipt(calls[0]["result"])
    require(probe["exit_code"] == 0 and probe["output"] == "VERSION 2026.1 PROJECT {} GLOBAL_HELPER 0 GLOBAL_NAMESPACE 0 NESTED_NAMESPACE 0", "会话不干净")
    require(all(c["mode"] == "proxy" and receipt(c["result"])["exit_code"] == 0 for c in calls), "R2 MCP 调用未成功")
    full = next(c for c in calls if c["step"] == "fresh_full_candidate_attempt1")
    require(full["source_sha"] == sha(ROOT / "vivado/s2b_ps_platform.tcl"), "实际运行 Tcl 绑定不同")
    require("PS_PLATFORM:OFFLINE_CANDIDATE_OK" in receipt(full["result"])["output"], "完整运行未完成")
    helper = record("helper_load.tcldict")
    expected = {"helper_preexisting": "0", "helper_namespace_before": "0", "helper_namespace_after": "1", "api_origin": "::ipcfg::help", "nested_namespace_present": "0", "initial_source_global": "1", "caller_namespace": "::s2b_ps_platform"}
    require(all(helper[k] == v for k, v in expected.items()), "首次 helper 作用域事实不符")
    require("uplevel #0 [list source -notrace $helper]" in read_bytes(ROOT / "vivado/s2b_ps_platform.tcl").decode("utf-8"), "全局 source 修复缺失")
    post = record("post_validate.tcldict")
    require(post["stuck"] == "" and post["nested_namespace"] == "0" and post["api_origin"] == "::ipcfg::help", "验证后配置或作用域错误")
    capture = {}
    for stage in ("configure", "validate", "products", "products_recheck", "export"):
        r = record(stage + ".tcldict")
        require(r["code"] == "0" and r["error_count"] == "0" and r["critical_count"] == "0", "阶段 Tcl 错误或关键警告")
        require(r["status"] == ("FAIL" if stage == "products" else "OK"), "capture 状态不符")
        if stage == "products":
            require(r["capture_error"] == "CAPTURE_FAIL:native message export incomplete or counters changed: WARNING emitted=-9 exported=0", "原 capture 失败原因不同")
        capture[stage] = {k: r[k] for k in ("status", "code", "warning_count", "critical_count", "error_count", "elapsed_ms")}
        if "capture_error" in r:
            capture[stage]["capture_error"] = r["capture_error"]
        native = read_bytes(RUN / "vivado_native.log") if (RUN / "vivado_native.log").exists() else read_bytes(Path(r["native_log_source"]))
        start, end = (int(v) for v in TCL.splitlist(r["native_log_offsets"]))
        require(native[start:end] == read_bytes(CANDIDATE / (stage + ".tcldict.native.log")), "原生日志区间不同")
    return {"helper_load": expected, "capture": capture, "full_run_elapsed_seconds": receipt(full["result"])["elapsed_seconds"]}


def check_history():
    mapping = read_json(RUN / "source_prior_mapping.json")
    sources = {r["original_path"]: r for r in mapping["source_mappings"]}
    require(len(sources) == 3, "旧源码映射数量不同")
    for r in sources.values():
        require(sha(ROOT / r["snapshot_path"]) == r["sha256"], "旧源码快照 SHA 不同")
        require(len(read_bytes(ROOT / r["snapshot_path"])) == r["bytes"], "旧源码快照长度不同")
    files = mapping["prior_run_files"]
    prior_names = {p.relative_to(ROOT).as_posix() for p in PRIOR.rglob("*") if p.is_file()}
    require(prior_names == {r["path"] for r in files} and len(files) == 100, "r01 文件集合变化")
    for r in files:
        require(sha(ROOT / r["path"]) == r["sha256"], f"r01 历史文件变化：{r['path']}")
        require(len(read_bytes(ROOT / r["path"])) == r["bytes"], "r01 历史文件长度变化")
    counts = {}
    for name in ("delivery_manifest.json", "inputs_manifest.json"):
        manifest = read_json(PRIOR / name)
        mapped = 0
        for r in manifest["files"]:
            bound = ROOT / r["path"]
            if r["path"] in sources:
                bound = ROOT / sources[r["path"]]["snapshot_path"]
                mapped += 1
            require(sha(bound) == r["sha256"], f"旧清单重放绑定错误：{r['path']}")
        require(mapped == 3, "旧清单应通过三个旧源码快照重放")
        counts[name] = {"files_verified": len(manifest["files"]), "source_snapshot_bindings": mapped, "manifest_sha256": sha(PRIOR / name)}
    failure = receipt(read_json(RUN / "r1_diagnostic/rebuild_receipt.json")["result"])
    require(failure["exit_code"] == 1 and "parent namespace doesn't exist" in failure["output"], "R1 原始失败事实丢失")
    return {"r01_files_unchanged": len(files), "manifests_replayed": counts, "r01_review_status": "CHANGES_REQUIRED", "r01_clean_rebuild_exit_code": failure["exit_code"], "r01_not_frozen": True}


if __name__ == "__main__":
    result = {"status": "CANDIDATE_AND_HISTORY_CHECKS_OK", "candidate": check_candidate(), "fresh_session": check_fresh_helper_and_capture(), "history": check_history(), "python": sys.version.split()[0]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
