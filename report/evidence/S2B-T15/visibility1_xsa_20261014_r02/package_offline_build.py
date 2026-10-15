"""一次性封装已完成的R02离线构建，不启动工具或覆盖任何输出。"""

from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import sys
import time


RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[3]
sys.path.insert(0, str(ROOT / "verification"))
from s2b_board_transport import verify_build, MODEL_SHA
from check_s2b_ps_smoke_layout import parse_elf


def sha(raw):
    """计算原始字节摘要。"""
    return hashlib.sha256(raw).hexdigest()


def bound(path):
    """绑定实际普通文件的仓库相对路径和字节。"""
    assert path.is_file(), str(path)
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path.read_bytes())}


def section_view(raw, section):
    """NOLOAD节仅比较元数据，不把ELF后续字节误当初始化内容。"""
    if section is None:
        return None
    result = {key: section[key] for key in ("type", "flags", "address", "size", "align")}
    result["file_offset"] = section["offset"]
    result["payload_sha256"] = None if section["type"] == 8 else sha(raw[section["offset"]:section["offset"] + section["size"]])
    result["payload_kind"] = "NOBITS_NO_FILE_PAYLOAD" if section["type"] == 8 else "ELF_FILE_BYTES"
    return result


def symbol_view(raw, elf, symbol):
    """比较实际函数字节，清除ARM Thumb符号地址最低位后定位文件偏移。"""
    if symbol is None:
        return None
    result = dict(symbol)
    result["payload_sha256"] = None
    if symbol["size"] and 0 < symbol["section"] < len(elf["sections"]):
        section = elf["sections"][symbol["section"]]
        begin = (symbol["value"] & ~1) - section["address"]
        assert section["type"] != 8 and 0 <= begin <= section["size"] - symbol["size"]
        result["payload_sha256"] = sha(raw[section["offset"] + begin:section["offset"] + begin + symbol["size"]])
    return result


def compare_elf(name):
    """对照旧包与新包全部SHF_ALLOC节及有长度的函数符号。"""
    old_path = ROOT / "report/evidence/S2B-T15/visibility1_xsa_20261014_r01" / name
    new_path = RUN / name
    old_raw, new_raw = old_path.read_bytes(), new_path.read_bytes()
    old, new = parse_elf(old_raw), parse_elf(new_raw)
    old_sections = {row["name"]: row for row in old["sections"] if row["flags"] & 2}
    new_sections = {row["name"]: row for row in new["sections"] if row["flags"] & 2}
    rows = []
    for key in sorted(old_sections.keys() | new_sections.keys()):
        left, right = old_sections.get(key), new_sections.get(key)
        lv, rv = section_view(old_raw, left), section_view(new_raw, right)
        metadata_same = bool(left and right and all(left[k] == right[k] for k in ("type", "flags", "address", "size", "align")))
        payload_same = bool(lv and rv and lv["payload_sha256"] == rv["payload_sha256"])
        differences = None
        if left and right and left["type"] != 8 and right["type"] != 8:
            a = old_raw[left["offset"]:left["offset"] + left["size"]]
            b = new_raw[right["offset"]:right["offset"] + right["size"]]
            positions = [index for index, (x, y) in enumerate(zip(a, b)) if x != y]
            differences = {"different_byte_count_in_overlap": len(positions), "size_delta": len(b) - len(a), "first_offsets": positions[:16]}
        rows.append({"name": key, "old": lv, "new": rv, "runtime_metadata_equal": metadata_same,
                     "file_payload_equal": payload_same, "runtime_section_equal": metadata_same and payload_same, "differences": differences})
    old_symbols = {s["name"]: s for s in old["symbols"] if s["name"] and s["type"] == 2 and s["size"]}
    new_symbols = {s["name"]: s for s in new["symbols"] if s["name"] and s["type"] == 2 and s["size"]}
    functions = []
    for key in sorted(old_symbols.keys() | new_symbols.keys()):
        a = symbol_view(old_raw, old, old_symbols.get(key))
        b = symbol_view(new_raw, new, new_symbols.get(key))
        same = bool(a and b and all(a[k] == b[k] for k in ("value", "size", "type", "payload_sha256")))
        functions.append({"name": key, "old": a, "new": b, "equal": same})
    keys = []
    for key in ("_boot", "_start", "MMUTable", "main", "Xil_SetTlbAttributes", "Xil_DCacheFlushRange", "Xil_DCacheInvalidateRange"):
        a = next((s for s in old["symbols"] if s["name"] == key), None)
        b = next((s for s in new["symbols"] if s["name"] == key), None)
        keys.append({"name": key, "old": symbol_view(old_raw, old, a), "new": symbol_view(new_raw, new, b)})
    return {"old_elf": bound(old_path), "new_elf": bound(new_path), "whole_elf_equal": old_raw == new_raw,
            "old_entry": old["entry"], "new_entry": new["entry"], "allocated_sections": rows,
            "different_runtime_sections": [r["name"] for r in rows if not r["runtime_section_equal"]],
            "function_symbols": functions, "different_function_symbols": [r["name"] for r in functions if not r["equal"]],
            "key_symbols": keys, "boot_section_presence": {"old": ".boot" in old_sections, "new": ".boot" in new_sections},
            "load_segments": {"old": [p for p in old["programs"] if p["type"] == 1], "new": [p for p in new["programs"] if p["type"] == 1]},
            "limits": ["零长度符号仅比较地址与所属节；不能据此单独证明函数字节一致。", "函数按名称配对，地址、长度与字节SHA均列出，供GP0迁移复核；不代替新的软件契约独审。"]}


def classify_infer_differences():
    """按原始节字节验证构建标识与路径差异，不改写任何ELF内容。"""
    payloads = []
    for directory in (ROOT / "report/evidence/S2B-T15/visibility1_xsa_20261014_r01", RUN):
        raw = (directory / "infer.elf").read_bytes()
        sections = {row["name"]: row for row in parse_elf(raw)["sections"]}
        payloads.append({name: raw[sections[name]["offset"]:sections[name]["offset"] + sections[name]["size"]]
                         for name in (".text", ".rodata")})
    old, new = payloads
    header = bytes.fromhex("040000001400000003000000474e5500")
    note = old[".text"].find(header)
    assert note >= 0 and new[".text"].find(header) == note
    assert len(old[".text"]) == len(new[".text"])
    positions = [i for i, (a, b) in enumerate(zip(old[".text"], new[".text"])) if a != b]
    assert positions == list(range(note + len(header), note + len(header) + 20))
    before, after = b"t19_visibility1_20261014_r01", b"t19_visibility1_20261014_r02"
    assert old[".rodata"].count(before) == 3 and old[".rodata"].replace(before, after) == new[".rodata"]
    return {"text": {"kind": "GNU_NT_GNU_BUILD_ID_NOTE_DESCRIPTOR", "header_hex": header.hex(),
                     "section_note_offset": note, "descriptor_bytes": 20, "different_byte_count": len(positions),
                     "all_other_text_bytes_equal": True},
            "rodata": {"kind": "THREE_UARTPS_SOURCE_PATH_RUN_ID_BYTES", "old_run_component": before.decode("ascii"),
                       "new_run_component": after.decode("ascii"), "occurrences": 3,
                       "exact_replacement_matches_all_rodata_bytes": True},
            "limit": "该分类只解释两份绑定ELF的差异；新的GP0软件契约适用性仍须另行独立复核。"}


def main():
    """完成全部核验后用独占创建输出；失败保留文件且禁止覆盖重跑。"""
    started = time.monotonic()
    assert RUN.is_dir() and ROOT.is_dir()
    config_path = ROOT / "tmp/2B/S2B-T15/visibility1_rebind_config_20261014_r02.json"
    launcher_path = ROOT / "tmp/2B/S2B-T15/visibility1_rebind_launcher_20261014_r02.log"
    workspace = ROOT / "tmp/2B/S2B-T15/t19_visibility1_20261014_r02"
    copies = {
        "build_config.json": config_path,
        "vitis_launcher.log": launcher_path,
        "vitis_bsp_build.log": workspace / "ps7/logs/cpu0_build.log",
        "vitis_infer_build.log": workspace / "infer/build/build.log",
        "vitis_init_build.log": workspace / "init/build/build.log",
    }
    names = list(copies) + ["runtime_section_comparison.json", "summary.json", "delivery_manifest.json"]
    assert all(not (RUN / name).exists() for name in names), "封装输出已存在，拒绝覆盖"
    assert all(path.is_file() for path in copies.values()), "复制来源不是实际文件"
    build_path, build = verify_build(RUN / "build_details.json")
    config_raw = config_path.read_bytes()
    assert sha(config_raw) == build["config_sha256"]
    assert json.loads(config_raw.decode("utf-8")) == build["config"]
    for relative, expected in build["source_sha256"].items():
        assert sha((RUN / "source_snapshot" / Path(relative).name).read_bytes()) == expected
    for binding in build["files"].values():
        assert sha(Path(binding["path"]).read_bytes()) == binding["sha256"]
    for command in build["commands"]:
        assert command["exit_code"] == 0 and sha(Path(command["log"]).read_bytes()) == command["log_sha256"]
    model_path = ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
    assert sha(model_path.read_bytes()) == MODEL_SHA
    assert "[102/102]" in copies["vitis_bsp_build.log"].read_text(encoding="utf-8")
    comparison = {"schema_version": 1, "scope": "离线ELF原字节、SHF_ALLOC节、LOAD段和函数符号对照",
                  "source_commit": build["source_commit"], "infer": compare_elf("infer.elf"), "init": compare_elf("init.elf"),
                  "infer_difference_classification": classify_infer_differences()}
    previous_manifest = ROOT / "report/evidence/S2B-T15/visibility1_xsa_20261014_r01/delivery_manifest.json"
    interfaces = json.loads(previous_manifest.read_text(encoding="utf-8"))["interfaces"]
    for interface in interfaces:
        interface["sha256"] = sha((ROOT / interface["path"]).read_bytes())
    limits = [
        "本任务只封装已有离线构建，不再次运行Vitis/Vivado/JTAG，不下载PL/PS或访问实物。",
        "PS/PL候选s2b-physical-candidate/0.1.1与UART候选s2bu-candidate/1.1尚未整体冻结；G0及部署准入仍BLOCKED。",
        "当前实物已由用户确认XC7Z020-2CLG400I，Vivado part为xc7z020clg400-2；上游历史XA照片备注已由该确认取代，不再列身份阻碍。",
        "CPU1停核、HP0延迟与可见性、32 MiB arena实际cache契约、CORE/DRAIN期限及100/1000实板验收未执行。",
        "新旧完整ELF哈希不同；逐节和符号实际差异见runtime_section_comparison.json，不声明二进制整体一致或继承旧ELF软件契约G2。",
        "Vitis进程树峰值内存未测；own_server_cleanup=DISPOSE_CALLED只记录自有server清理调用。",
        "evidence检查只验证包装和绑定，不能代表G0/G3/G4/G5。",
        "多文件独占写入若中断，保留全部已生成原件；不得删除原件后直接重跑，应另用新RunId或经审查的恢复清单继续。",
    ]
    summary = {"schema_version": 1, "task_id": "S2B-T15", "run_id": RUN.name,
               "created_local": datetime.now(timezone(timedelta(hours=8))).isoformat(),
               "status": build["status"], "hardware_execution": "NOT_RUN", "source_commit": build["source_commit"],
               "xsa_source_commit": build["config"]["xsa_source_commit"], "build_details": bound(build_path),
               "build_config": bound(config_path), "platform_manifest": bound(Path(build["config"]["platform_manifest"])),
               "xsa": bound(Path(build["config"]["xsa"])), "model_manifest": bound(model_path),
               "current_source_sha256": build["source_sha256"], "source_snapshot_verified_count": len(build["source_sha256"]),
               "verify_build": {"status": "PASS", "implementation": bound(ROOT / "verification/s2b_board_transport.py"), "native_exit_code": 0},
               "build": {"native_exit_code": 0, "native_exit_observation": "总控实际工具调用结果，外层日志原字节同时保留。",
                         "launcher_elapsed_seconds": 113.234, "driver_elapsed_seconds": build["elapsed_seconds"],
                         "launcher_argv": ["cmd.exe", "/d", "/c", "D:\\Xilinx\\2026.1\\Vitis\\bin\\vitis.bat", "-s", str(ROOT / "vitis/build_s2b_inference.py")],
                         "launcher_cwd": str(ROOT), "launcher_environment_additions": {"S2B_INFERENCE_CONFIG": str(config_path), "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
                         "launcher_capture": "stdout与stderr合并到xb独占创建的原始日志；300秒期限未触发；参数由总控实际调用回传。",
                         "attempts": build["attempts"], "api_call_count": len(build["api_calls"]), "tool_command_count": len(build["commands"]),
                         "bsp_steps": "102/102", "own_server_cleanup": build["own_server_cleanup"], "peak_memory_bytes": build["peak_memory_bytes"],
                         "peak_memory_reason": build["peak_memory_reason"]},
               "infer_elf": build["elf"], "initializer_elf": build["initializer_elf"],
               "runtime_comparison": {"path": (RUN / "runtime_section_comparison.json").relative_to(ROOT).as_posix(),
                                      "infer_different_sections": comparison["infer"]["different_runtime_sections"],
                                      "init_different_sections": comparison["init"]["different_runtime_sections"],
                                      "infer_different_functions": comparison["infer"]["different_function_symbols"]},
               "interface_gate": "BLOCKED_UNFROZEN_PHYSICAL_AND_UART_CANDIDATES", "limitations": limits}
    payloads = {name: source.read_bytes() for name, source in copies.items()}
    encode = lambda value: (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")
    payloads["runtime_section_comparison.json"] = encode(comparison)
    payloads["summary.json"] = encode(summary)
    files = []
    def add(path, role, raw=None):
        item = bound(path) if raw is None else {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(raw)}
        if any(f["path"] == item["path"] for f in files):
            return
        item.update(role=role, keep_reason="绑定实际构建输入、原始产物、命令日志或本次离线复核依据，保留原字节。")
        files.append(item)
    for path in sorted(RUN.rglob("*")):
        if path.is_file():
            role = "artifact" if path.suffix == ".elf" else "log" if path.suffix == ".log" else "diagnostic" if path.suffix == ".map" else "source" if path.suffix in {".py", ".c", ".h", ".S", ".i", ".ld", ".cmake", ".txt", ".tcl"} else "result"
            add(path, role)
    for name, raw in payloads.items():
        add(RUN / name, "log" if name.endswith(".log") else "input" if name == "build_config.json" else "result", raw)
    for relative in build["source_sha256"]:
        # 这七项包含当前实际导入的运输验证器和ELF解析器，不仅绑定快照。
        add(ROOT / relative, "source")
    for path in [Path(build["config"]["xsa"]), Path(build["config"]["platform_manifest"]), model_path,
                 previous_manifest, ROOT / "report/evidence/S2B-T15/visibility1_xsa_20261014_r01/infer.elf",
                 ROOT / "report/evidence/S2B-T15/visibility1_xsa_20261014_r01/init.elf"]:
        add(path, "input")
    for interface in interfaces:
        add(ROOT / interface["path"], "input")
    manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T15", "run_id": RUN.name,
                "source_commit": build["source_commit"], "evidence_dir": RUN.relative_to(ROOT).as_posix(),
                "interfaces": interfaces, "files": files,
                "tool_versions": {"Python": sys.version.split()[0], "Vitis": build["vitis_version"], "GCC": (RUN / "gcc_version.log").read_text(encoding="utf-8").splitlines()[0]},
                "checks": [
                    {"name": "offline_full_xsa_build", "status": "PASS", "command": "Vitis2026.1 vitis.bat -s vitis/build_s2b_inference.py (配置与原始外层日志见本包)", "exit_code": 0, "reason": "原始build_details记录完整新XSA、BSP、应用及初始化ELF成功，全部工具命令退出0。"},
                    {"name": "current_transport_verify_build", "status": "PASS", "command": "python -X utf8 -B report/evidence/S2B-T15/visibility1_xsa_20261014_r02/package_offline_build.py", "exit_code": 0, "reason": "调用实际当前verify_build，核对XSA、平台清单、两个ELF和当前七源码绑定；源码快照及构建命令日志另逐项核对。"},
                    {"name": "runtime_elf_section_comparison", "status": "PASS", "command": "package_offline_build.py: compare_elf", "exit_code": 0, "reason": "逐SHF_ALLOC节、LOAD段、函数符号与旧R01 ELF比较，真实差异完整记录，不以整体SHA差异判构建失败。"},
                    {"name": "whole_platform_g0", "status": "BLOCKED", "command": None, "exit_code": None, "reason": "PS/PL与UART接口候选尚未整体冻结，离线build不能自动授予部署准入。"},
                    {"name": "hardware_execution", "status": "NOT_RUN", "command": None, "exit_code": None, "reason": "封装范围禁止硬件操作；当前平台黄金样本、连续任务及异常恢复仍待实板。"},
                ], "limitations": limits}
    payloads["delivery_manifest.json"] = encode(manifest)
    for name, raw in payloads.items():
        with (RUN / name).open("xb") as stream:
            stream.write(raw)
    print(json.dumps({"status": "PACKAGE_CREATED", "new_files": list(payloads), "manifest_sha256": sha(payloads["delivery_manifest.json"]), "summary_sha256": sha(payloads["summary.json"]), "elapsed_seconds": time.monotonic() - started}, ensure_ascii=False))


if __name__ == "__main__":
    main()
