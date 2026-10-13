"""独立读取实际导出、软件交接、监护及冻结证据；不启动厂商工具或访问硬件。"""
import hashlib
import io
import json
import os
from pathlib import Path
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition")
OUT = Path(__file__).absolute().parent
RUN = ROOT / "report/evidence/S2B-T17/direct_bitgen_20261013T054357Z_ccbeeb35a2053320"
PS_NAMES = ("ps7_init.c", "ps7_init.h", "ps7_init_gpl.c", "ps7_init_gpl.h", "ps7_init.html", "ps7_init.tcl")


def require(ok, message):
    """异常停止使用真实断言，不依赖优化模式。"""
    if not ok:
        raise RuntimeError(message)


def sha(raw):
    """按原始字节计算摘要。"""
    return hashlib.sha256(raw).hexdigest()


def exact(path):
    """逐组件拒绝重解析点并核验真实文件。"""
    path = Path(path)
    require(path.is_absolute(), "路径不是绝对路径")
    for current in reversed((path,) + tuple(path.parents)):
        info = os.lstat(current)
        require(not current.is_symlink() and not getattr(info, "st_file_attributes", 0) & 0x400,
                "路径包含重解析点")
    require(path.is_file(), "精确文件不存在")
    return path


def raw(path):
    """读取通过路径门禁的普通文件。"""
    return exact(path).read_bytes()


def bind(path):
    """记录真实路径与实际摘要。"""
    path = exact(path)
    data = path.read_bytes()
    return {"path": str(path), "sha256": sha(data), "bytes": len(data)}


def read_json(path):
    """按UTF8读取证据。"""
    return json.loads(raw(path).decode("utf-8"))


def archive(data):
    """只在内存内读取已绑定归档，拒绝重复成员和过大展开量。"""
    with zipfile.ZipFile(io.BytesIO(data)) as stream:
        entries = stream.infolist()
        require(len(entries) == len({item.filename for item in entries}), "归档重复成员")
        require(sum(item.file_size for item in entries) < 128 * 1024 * 1024, "归档展开预算超限")
        return {item.filename: stream.read(item) for item in entries}


def hwh(members):
    """独立解析PS配置、地址范围和全模型核心。"""
    names = [name for name in members if name.endswith(".hwh")]
    require(len(names) == 1, "HWH必须唯一")
    tree = ET.fromstring(members[names[0]])
    modules = list(tree.iter("MODULE"))
    ps = [item for item in modules if item.get("MODTYPE") == "processing_system7"]
    require(len(ps) == 1, "PS7必须唯一")
    rows = ps[0].findall("PARAMETERS/PARAMETER")
    params = {item.get("NAME"): item.get("VALUE") for item in rows}
    require(len(params) == len(rows), "PS参数重复")
    cores = [item for item in modules if item.get("MODTYPE") == "s2b_inference_top"]
    return {"name": names[0], "sha256": sha(members[names[0]]), "ps_parameters": params,
            "memranges": [dict(item.attrib) for item in tree.iter("MEMRANGE")],
            "cores": [{"attributes": dict(item.attrib), "parameters": {param.get("NAME"): param.get("VALUE")
                       for param in item.findall("PARAMETERS/PARAMETER")}} for item in cores]}


def bit_header(data):
    """解析完整位流头和配置载荷，不把时间字段差异当作载荷差异。"""
    cursor = 2 + struct.unpack_from(">H", data, 0)[0]
    require(struct.unpack_from(">H", data, cursor)[0] == 1, "位流头标记长度错误")
    cursor += 2
    fields = {}
    for key in "abcde":
        require(data[cursor:cursor + 1] == key.encode("ascii"), "位流头字段次序错误")
        cursor += 1
        if key == "e":
            size = struct.unpack_from(">I", data, cursor)[0]
            cursor += 4
            require(cursor + size == len(data), "载荷长度和文件大小不一致")
            payload = data[cursor:]
            return {"fields": fields, "header_bytes": cursor, "payload_bytes": size,
                    "payload_sha256": sha(payload)}, payload
        size = struct.unpack_from(">H", data, cursor)[0]
        cursor += 2
        fields[key] = data[cursor:cursor + size].rstrip(b"\0").decode("ascii")
        cursor += size
    raise RuntimeError("位流载荷缺失")


def main():
    """独立生成事实摘要；兼容收据需等待正式交付清单和独立判断。"""
    manifest = read_json(RUN / "manifest.json")
    monitors = [json.loads(line) for line in raw(RUN / "monitor.jsonl").decode("utf-8").splitlines()]
    samples = [row for row in monitors if "job_sample" in row]
    progress = [json.loads(line) for line in raw(RUN / "tcl_progress.jsonl").decode("utf-8").splitlines()]
    bindings = {"manifest": bind(RUN / "manifest.json")}
    for key, item in manifest["artifacts"].items():
        actual = bind(Path(item["path"]))
        require(actual["sha256"].upper() == item["sha256"] and actual["bytes"] == item["size_bytes"],
                "实际产物与manifest不一致：" + key)
        bindings[key] = actual
    for item in manifest["input_run_copies"]:
        require(bind(Path(item["source_path"]))["sha256"].upper() == item["destination_sha256"], "源文件SHA漂移")
        require(bind(Path(item["destination_path"]))["sha256"].upper() == item["destination_sha256"], "输入副本SHA漂移")
    require(progress == manifest["vivado_tcl_progress"], "Tcl进度与manifest不一致")
    require(manifest["status"] == "BITGEN_COMPLETE_SOFTWARE_ONLY" and manifest["stop_reason"] is None, "bitgen未成功")
    require(manifest["native_cmd_root_exit_code"] == 0 and manifest["native_vivado_exit_codes"] == [0], "原生退出不为0")
    final = manifest["job_final_closure"]["final"]
    require(final["active_processes"] == 0 and final["exited_processes"] == final["total_processes"] == 2
            and final["total_terminated_processes"] == 0 and final["root_handle_signaled"]
            and final["root_native_handle_exit_code"] == 0
            and not final["job_pids"] and not final["live_members"] and not final["unknown_members"], "进程闭合不完整")
    require(all(row["exit_code"] == 0 and row["status"] == "EXITED" for row in final["member_readbacks"]), "成员退出不为0")
    require(len(samples) == len(manifest["resource_samples"]) == manifest["resource_peaks_and_floors"]["sample_count"], "采样条数不一致")
    require(len(monitors) == manifest["monitor_record_count"], "监控记录数不一致")
    for row, other in zip(samples, manifest["resource_samples"]):
        require(row["job_sample"] == other["job_sample"], "监控采样内容不一致")
    for key, value in {"sampling_target_seconds": 0.5, "tree_rss_limit_bytes": 6442450944,
                       "available_ram_floor_bytes": 536870912, "c_disk_free_floor_bytes": 8589934592,
                       "no_log_or_stage_progress_hard_stop_seconds": 900.0, "job_object_limit_flags": 8192,
                       "breakaway_allowed": False}.items():
        require(manifest["limits"][key] == value, "监护配置漂移：" + key)
    require(max(row["job_sample"]["sample_gap_seconds"] or 0 for row in samples) <= 1.0, "采样超过1秒")
    require(not manifest["input_copy_lock_release_errors"] and not manifest["toolchain_read_lock_release_errors"], "输入锁未安全关闭")
    xsa_path = RUN / "s2b_inference_implemented.xsa"
    bindings["implemented_xsa"] = bind(xsa_path)
    xsa = archive(raw(xsa_path))
    bit_names = [name for name in xsa if name.endswith(".bit")]
    require(len(bit_names) == 1, "官方XSA位流必须唯一")
    external = raw(RUN / "s2b_inference_wrapper_postroute_physopt.bit")
    embedded = xsa[bit_names[0]]
    outer_header, outer_payload = bit_header(external)
    inner_header, inner_payload = bit_header(embedded)
    build_path = ROOT / "report/evidence/S2B-T15/full_build_20261011_r01/build_details.json"
    build = read_json(build_path)
    bindings["build_details"] = bind(build_path)
    compiled = Path(build["config"]["xsa"])
    bindings["compiled_xsa"] = bind(compiled)
    require(bindings["compiled_xsa"]["sha256"] == build["xsa_sha256"] == "6cff0c6afd009bf051028c4b793cc99c3c0c700002c2fdb2d247a33d2fc076a7", "编译XSA绑定不一致")
    s15_path = ROOT / "report/evidence/S2B-T17/s15_platform_20261012_r01/s2b_inference_no_bit.xsa"
    bindings["s15_xsa"] = bind(s15_path)
    dcp_path = Path(manifest["input_paths_and_hashes"]["frozen_dcp_path"])
    dcp = archive(raw(dcp_path))
    hwdefs = [name for name in dcp if name.endswith(".hwdef")]
    require(len(hwdefs) == 1, "DCP交接成员必须唯一")
    handoffs = {"compiled_xsa": archive(raw(compiled)), "s15_xsa": archive(raw(s15_path)),
                "dcp_hwdef": archive(dcp[hwdefs[0]]), "implemented_xsa": xsa}
    facts = {name: hwh(members) for name, members in handoffs.items()}
    comparisons = {}
    for name, members in handoffs.items():
        comparisons[name] = {
            "ps_parameter_count": len(facts[name]["ps_parameters"]),
            "same_ps_parameters_compiled": facts[name]["ps_parameters"] == facts["compiled_xsa"]["ps_parameters"],
            "ps_init": {item: {"sha256": sha(members[item]), "same_compiled": members[item] == handoffs["compiled_xsa"][item]}
                        for item in PS_NAMES},
            "hwh_same_s15": members[facts[name]["name"]] == handoffs["s15_xsa"][facts["s15_xsa"]["name"]]}
    software = {}
    for name in ("xparameters.h", "bspconfig.h", "xil_mmu.h", "xil_mmu.c", "translation_table.S", "bsp_compile_commands.json"):
        item = build["files"][name]
        record = bind(Path(item["path"]))
        require(record["sha256"] == item["sha256"], "BSP文件SHA漂移：" + name)
        software[name] = record
    for key, dest in (("elf", "app_elf"), ("initializer_elf", "init_elf")):
        item = build[key]
        bindings[dest] = bind(Path(item["path"]))
        require(bindings[dest]["sha256"] == item["sha256"], "ELF绑定漂移")
    sys.path.insert(0, str(ROOT / "verification"))
    import check_s2b_inference_platform as checker
    require(Path(checker.__file__).absolute() == ROOT / "verification/check_s2b_inference_platform.py", "静态检查模块来源错误")
    sources = checker.check_static(ROOT)
    pnr_path = ROOT / "report/evidence/S2B-T17/s15_pnr_sta_review_20261012_r01/review_report.json"
    pnr = read_json(pnr_path)
    pnr_sources = {row["path"]: row["sha256"] for row in pnr["source"]["rows"]}
    drift = {name: [value, pnr_sources.get(name)] for name, value in sources.items() if pnr_sources.get(name) != value}
    source_receipt_path = ROOT / "report/evidence/S2B-T17/s15_source_closure_20261012_r01/source_closure_receipt.json"
    source_receipt = read_json(source_receipt_path)
    log = raw(RUN / "vivado.log").decode("utf-8", errors="replace")
    summary = {"status": "INDEPENDENT_FACTS_ONLY", "bindings": bindings, "source_sha256": sources,
               "software_bindings": software, "build_status": build["status"],
               "process": {"native_root": manifest["native_cmd_root_exit_code"], "native_vivado": manifest["native_vivado_exit_codes"],
                   "closure": final, "samples": len(samples), "monitor_records": len(monitors),
                   "sampling_target_seconds": 0.5, "max_sample_gap": max(row["job_sample"]["sample_gap_seconds"] or 0 for row in samples),
                   "peaks": manifest["resource_peaks_and_floors"], "alert_samples": [row for row in samples if row["alerts"]]},
               "progress": progress, "drc_zero_errors": "DRC finished with 0 Errors" in log,
               "export_completed": "write_hw_platform_complete" in [row["event"] for row in progress],
               "embedded_bit": {"member": bit_names[0], "sha256": sha(embedded), "bytes": len(embedded), "header": inner_header},
               "external_bit": {"sha256": sha(external), "bytes": len(external), "header": outer_header},
               "bit_comparison": {"full_bytes_equal": external == embedded, "payload_bytes_equal": outer_payload == inner_payload,
                   "differing_bytes": sum(a != b for a, b in zip(external, embedded))},
               "hwh_facts": facts, "comparisons": comparisons,
               "pnr": {"binding": bind(pnr_path), "status": pnr["status"], "timing": pnr["timing"], "current_source_drift": drift},
               "source_closure": {"binding": bind(source_receipt_path), "status": source_receipt["status"], "keys": list(source_receipt)}}
    output = OUT / "independent_facts_r01.json"
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(summary, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"output": str(output), "sha256": sha(output.read_bytes()), "bit_comparison": summary["bit_comparison"],
                      "xsa_bit_count": len(bit_names), "ps_parameters": {name: [row["ps_parameter_count"], row["same_ps_parameters_compiled"]]
                                                                  for name, row in comparisons.items()},
                      "pnr_source_drift": drift, "pnr_status": pnr["status"], "build_status": build["status"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
