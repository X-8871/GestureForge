"""在独立副本复核冻结输入、真实ELF、故障拒绝与参考算例。"""

import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta


ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT.parents[3]
OUT = ROOT / "review/a01"
RUN = SHARED / "report/evidence/S2B-T06/ps_smoke_20261008_r01"
BUILD = ROOT / "report/evidence/S2B-T06/b01"
sys.path.insert(0, str(ROOT / "verification"))
sys.stdout.reconfigure(encoding="utf-8")
REPORT = {"schema_version": 1, "hardware_execution": "NOT_RUN", "commands": [], "checks": []}


def digest(path):
    """计算原始文件字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    """只读UTF-8 JSON。"""
    return json.loads(path.read_text(encoding="utf-8"))


def write_new(name, value):
    """所有新审查输出均在隔离目录，拒绝覆盖。"""
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def check(name, condition, detail):
    """记录独立核查判据及结果，失败时立即保留诊断。"""
    REPORT["checks"].append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})
    if not condition:
        raise AssertionError(name)


def run(name, argv, expected=0):
    """记录真实argv、cwd、原生退出和原始日志。"""
    started = time.monotonic()
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, check=False, env=dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1"))
    log = OUT / (name + ".log")
    with log.open("xb") as stream:
        stream.write(result.stdout)
        stream.write(result.stderr)
    record = {"name": name, "command": argv, "cwd": str(ROOT), "exit_code": result.returncode,
              "expected_exit_code": expected, "elapsed_seconds": time.monotonic() - started,
              "log": str(log), "log_sha256": digest(log)}
    REPORT["commands"].append(record)
    check(name, result.returncode == expected, record)
    return result


def independent_elf(path):
    """用审查方独立解析实现读取节表、段表及符号，不调用被审解析器。"""
    data = path.read_bytes()
    header = struct.unpack_from("<HHIIIIIHHHHHH", data, 16)
    assert data[:7] == b"\x7fELF\x01\x01\x01" and header[1] == 40
    phoff, shoff, phnum, shnum, shstr = header[4], header[5], header[9], header[11], header[12]
    rows = [struct.unpack_from("<10I", data, shoff + 40 * n) for n in range(shnum)]
    names = data[rows[shstr][4]:rows[shstr][4] + rows[shstr][5]]
    def text(table, offset):
        return table[offset:table.index(b"\0", offset)].decode("ascii")
    sections = {text(names, r[0]): {"index": i, "type": r[1], "flags": r[2], "address": r[3], "offset": r[4], "size": r[5], "row_offset": shoff + 40 * i} for i, r in enumerate(rows)}
    loads = []
    for n in range(phnum):
        r = struct.unpack_from("<8I", data, phoff + 32 * n)
        if r[0] == 1:
            loads.append({"row_offset": phoff + 32 * n, "virtual": r[2], "physical": r[3], "file_size": r[4], "memory_size": r[5]})
    symbols = {}
    for row in rows:
        if row[1] == 2:
            nr = rows[row[6]]
            table = data[nr[4]:nr[4] + nr[5]]
            for offset in range(row[4], row[4] + row[5], 16):
                r = struct.unpack_from("<IIIBBH", data, offset)
                name = text(table, r[0])
                if name:
                    symbols[name] = {"value": r[1], "size": r[2], "type": r[3] & 15, "section": r[5]}
    return {"entry": header[3], "sections": sections, "loads": loads, "symbols": symbols, "data": data}


def machine_function(elf, name):
    """独立取得函数机器码，剥除Thumb标记。"""
    obj = elf["symbols"][name]
    section = next(x for x in elf["sections"].values() if x["index"] == obj["section"])
    offset = section["offset"] + (obj["value"] & ~1) - section["address"]
    return elf["data"][offset:offset + obj["size"]]


def main():
    """只读正式输入，所有实验变体留在副本。"""
    import check_s2b_ps_smoke_layout as layout
    from check_stage_delivery import _check_absolute_path
    spec = importlib.util.spec_from_file_location("review_builder", ROOT / "vitis/build_s2b_ps_smoke.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    frozen = {"vitis/s2b_ps_smoke.c": "d2bb6f0941c2e3765c5a71f889d2e7e1e0428429237f5443510e81cedd16786b", "vitis/build_s2b_ps_smoke.py": "addff3a419609ac8203c8838edfd6fd56fb53baccf40efc403fca4eb36b50d76", "verification/check_s2b_ps_smoke_layout.py": "6c12023cc9660d392a0f3e393df2ebaf425af8a4cbb51886a35749d0c6fa0f77", "vitis/s2b_ps_smoke.md": "c15290c48ccbc03c55418c2efa0ca2df815eacdeffb60e53363eca4fba490db5"}
    check("frozen_four_sources", all(digest(builder.exact_path(SHARED / p, "file")) == d == digest(builder.exact_path(ROOT / p, "file")) for p, d in frozen.items()), frozen)
    copied = read_json(ROOT / "review_input_copy.json")
    check("minimal_copy_11_bytes", len(copied["files"]) == 11 and all(digest(builder.exact_path(x["destination"], "file")) == x["sha256"] == digest(builder.exact_path(x["source"], "file")) for x in copied["files"]), {"count": len(copied["files"]), "receipt_sha256": digest(ROOT / "review_input_copy.json")})
    shared_arg = ["--project-root", str(SHARED)]
    checker = str(ROOT / "verification/check_stage_delivery.py")
    run("shared_inputs", [sys.executable, "-B", checker, "--mode", "inputs", "--manifest", str(RUN / "inputs_manifest_r03.json"), *shared_arg])
    run("shared_evidence", [sys.executable, "-B", checker, "--mode", "evidence", "--manifest", str(RUN / "delivery_manifest.json"), *shared_arg])
    layout_script = str(ROOT / "verification/check_s2b_ps_smoke_layout.py")
    old_layout = run("developer_layout_self_test", [sys.executable, "-B", layout_script, "--manifest", str(RUN / "build_08/layout_binding.json"), "--self-test"])
    old_result = json.loads(old_layout.stdout.decode("utf-8"))
    cases = old_result["self_test"]
    check("fourteen_rejections", len(cases["negative_cases_rejected"] + cases["initializer_negative_cases_rejected"] + cases["exact_identifier_negative_cases_rejected"]) == 14, cases)
    manifest = read_json(RUN / "delivery_manifest.json")
    checked = []
    for binding in manifest["files"]:
        path = Path(binding["path"])
        if not path.is_absolute():
            path = SHARED / path
        errors = []
        actual = _check_absolute_path(path, "file", errors, binding["path"])
        assert actual is not None and not errors, errors
        actual_hash = digest(actual)
        assert actual_hash == binding["sha256"], binding["path"]
        checked.append({"path": str(actual), "sha256": actual_hash, "bytes": actual.stat().st_size})
    write_new("developer_manifest_hashes.json", checked)
    check("developer_284_raw_byte_bindings", len(checked) == 284, {"count": len(checked), "manifest_sha256": digest(RUN / "delivery_manifest.json")})
    history = []
    for n in range(1, 9):
        detail_path = builder.exact_path(RUN / f"build_{n:02}/build_details.json", "file")
        detail = read_json(detail_path)
        check(f"history_{n:02}", detail["status"] == ("PASS_OFFLINE_BUILD_AND_LAYOUT" if n == 8 else "FAIL"), {"status": detail["status"], "error": detail.get("error"), "sha256": digest(detail_path)})
        history.append({"attempt": n, "status": detail["status"], "error": detail.get("error"), "elapsed_seconds": detail["elapsed_seconds"], "api_count": len(detail["api_calls"]), "command_count": len(detail["commands"]), "details_sha256": digest(detail_path)})
    REPORT["developer_history"] = history
    check("history_elapsed_counts", abs(sum(x["elapsed_seconds"] for x in history) - 264.200090499995) < 1e-6 and sum(x["api_count"] for x in history) == 129 and sum(x["command_count"] for x in history) == 18, {"elapsed_sum": sum(x["elapsed_seconds"] for x in history), "api_sum": sum(x["api_count"] for x in history), "commands_sum": sum(x["command_count"] for x in history)})
    models = {}
    for stem, bounds in (("s2b_ps_smoke", [(0x100000, 0x1200000)]), ("s2b_ps_init", [(0, 0x30000), (0xFFFF0000, 0xFFFFFE00)])):
        new = independent_elf(BUILD / (stem + ".elf"))
        old = independent_elf(RUN / "build_08" / (stem + ".elf"))
        models[stem] = new
        alloc = {k: {a: b for a, b in x.items() if a != "row_offset"} for k, x in new["sections"].items() if x["flags"] & 2 and x["size"]}
        for sec in alloc.values():
            assert sum(lo <= sec["address"] < sec["address"] + sec["size"] <= hi for lo, hi in bounds) == 1
        for seg in new["loads"]:
            assert seg["virtual"] == seg["physical"] and sum(lo <= seg["physical"] < seg["physical"] + seg["memory_size"] <= hi for lo, hi in bounds) == 1
        selected = (["main", "pattern_word", "publish_result", "send_text", "send_line", "init_uart", "fail_after_uart", "_exit"] if stem.endswith("smoke") else ["main", "s2b_ps_init_ready", "s2b_ps_init_fail", "ps7_init", "ps7GetSiliconVersion", "__cpu_init", "frame_dummy"])
        comparisons = {name: {"address": new["symbols"][name]["value"], "size": new["symbols"][name]["size"], "new_sha256": hashlib.sha256(machine_function(new, name)).hexdigest(), "same_as_developer": machine_function(new, name) == machine_function(old, name)} for name in selected}
        check(stem + "_independent_memory_and_machine_code", all(x["same_as_developer"] for x in comparisons.values()), {"new_elf_sha256": digest(BUILD / (stem + ".elf")), "developer_elf_sha256": digest(RUN / "build_08" / (stem + ".elf")), "entry": new["entry"], "alloc": alloc, "loads": new["loads"], "functions": comparisons})
    init = models["s2b_ps_init"]
    ctor = init["sections"][".init_array"]
    ctor_values = list(struct.unpack_from("<" + "I" * (ctor["size"] // 4), init["data"], ctor["offset"]))
    check("only_frame_dummy_constructor", ctor_values == [init["symbols"]["frame_dummy"]["value"]] and "xtimerinit" not in init["symbols"] and "TimerInst" not in init["symbols"], {"constructor_addresses": ctor_values})
    forbidden = {"GetSiliconVersion", "ps7_post_config", "LoadBootImage", "FabricInit", "XDcfg_Transfer", "FsblHandoffExit", "FsblHandoffJtagExit"}
    check("no_fsbl_handoff_pcap", not forbidden.intersection(init["symbols"]), {"forbidden": sorted(forbidden)})
    objdump = builder.exact_path(Path(r"D:\Xilinx\2026.1\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-objdump.exe"), "file")
    run("smoke_disassembly", [str(objdump), "-d", str(BUILD / "s2b_ps_smoke.elf")])
    mutations = [
        ("actual_buffer_exec", "elf", "s2b_ps_smoke", lambda raw, model: struct.pack_into("<I", raw, model["sections"][".s2b_smoke_buffer"]["row_offset"] + 8, 7)),
        ("actual_load_reserved", "elf", "s2b_ps_smoke", lambda raw, model: struct.pack_into("<II", raw, model["loads"][0]["row_offset"] + 8, 0, 0)),
        ("actual_ctor_ddr_pointer", "init_elf", "s2b_ps_init", lambda raw, model: struct.pack_into("<I", raw, model["sections"][".init_array"]["offset"], 0x100000)),
    ]
    binding = read_json(BUILD / "layout_binding.json")
    for name, key, stem, mutate in mutations:
        raw = bytearray(models[stem]["data"])
        mutate(raw, models[stem])
        destination = OUT / (name + ".elf")
        with destination.open("xb") as stream:
            stream.write(raw)
        modified = copy.deepcopy(binding)
        modified["files"][key] = {"path": str(destination), "sha256": digest(destination)}
        write_new(name + ".json", modified)
        result = run(name, [sys.executable, "-B", layout_script, "--manifest", str(OUT / (name + ".json"))], 1)
        check(name + "_semantic_rejection", "SHA-256" not in json.loads(result.stdout.decode("utf-8"))["error"], json.loads(result.stdout.decode("utf-8")))
    changed_c = OUT / "changed_c_source.c"
    with changed_c.open("xb") as stream:
        stream.write((ROOT / "vitis/s2b_ps_smoke.c").read_bytes() + "\n/* 独立哈希反例。 */\n".encode("utf-8"))
    for name, recorded_hash in (("source_hash_mismatch", frozen["vitis/s2b_ps_smoke.c"]), ("compiled_header_hash_mismatch", digest(changed_c))):
        modified = copy.deepcopy(binding)
        modified["files"]["c_source"] = {"path": str(changed_c), "sha256": recorded_hash}
        write_new(name + ".json", modified)
        run(name, [sys.executable, "-B", layout_script, "--manifest", str(OUT / (name + ".json"))], 1)
    config = read_json(ROOT / "review/build_config.json")
    for name, changes in (("config_unknown_key", {"unknown": 1}), ("xsa_hash_mismatch", {"xsa_sha256": "0" * 64}), ("inputs_hash_mismatch", {"inputs_manifest_sha256": "0" * 64}), ("source_baseline_mismatch", {"source_commit": "00f51b664fefdaf0c63e605af2427333579fa5f3"}), ("existing_workspace", {})):
        bad = dict(config, **changes)
        path = OUT / (name + ".json")
        write_new(path.name, bad)
        os.environ["S2B_PS_SMOKE_CONFIG"] = str(path)
        try:
            builder.build_from_binding()
        except (ValueError, FileExistsError) as error:
            check(name, True, {"config_sha256": digest(path), "error": str(error), "rejected_before_client_creation": True})
        else:
            raise AssertionError(name + " 未拒绝")
    records = []
    try:
        builder.run_checked([sys.executable, "-c", "import sys; print('REVIEW_EXPECTED_EXIT_7'); sys.exit(7)"], ROOT, OUT / "actual_exit7.log", records)
    except RuntimeError as error:
        check("nonzero_command_preserved", len(records) == 1 and records[0]["exit_code"] == 7 and b"REVIEW_EXPECTED_EXIT_7" in (OUT / "actual_exit7.log").read_bytes(), {"error": str(error), "records": records})
    else:
        raise AssertionError("非零子命令没有停止")
    check("independent_hand_examples", 2 * 8 * 262144 == 4194304 and 0x1100000 + 4 * 262143 == 0x11FFFFC, {"reference_method": "审查方按32位无符号规则手算，与源码各switch分支和循环边界独立对照；未执行ARM", "indices": [0, 31, 32, 262143], "pattern_vectors_hex": [ ["00000000"] * 4, ["FFFFFFFF"] * 4, ["AAAAAAAA"] * 4, ["55555555"] * 4, ["00000000", "0000001F", "00000020", "0003FFFF"], ["FFFFFFFF", "FFFFFFE0", "FFFFFFDF", "FFFC0000"], ["00000001", "80000000", "00000001", "80000000"], ["FFFFFFFE", "7FFFFFFF", "FFFFFFFE", "7FFFFFFF"] ], "checked_total_words": 4194304, "last_byte_offset": "0x000FFFFC", "first_error_example": {"corrupt_indices": [5, 9, 262143], "first_byte_offset": 20, "first_expected": 5, "first_actual": 0, "mismatches": 3, "verified_words_after_first_pattern": 262144}, "task_card_correction": "总控确认cache on/off是转写错误；固定实现和说明均为两轮DCache启用、每模式DSB/Flush/DSB/Invalidate/DSB。"})
    REPORT["status"] = "PASS_INDEPENDENT_OFFLINE_EXPERIMENTS"
    REPORT["finished_at_utc8"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
    write_new("audit_result.json", REPORT)
    print(json.dumps({"status": REPORT["status"], "checks": len(REPORT["checks"]), "commands": len(REPORT["commands"]), "result": str(OUT / "audit_result.json"), "sha256": digest(OUT / "audit_result.json")}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        REPORT["status"] = "FAIL_INDEPENDENT_AUDIT"
        REPORT["error"] = f"{type(error).__name__}: {error}"
        write_new("audit_failure.json", REPORT)
        raise
