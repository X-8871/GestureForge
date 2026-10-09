"""保存UART诊断字段修复的源码、真实ELF及包装核验依据。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition")
RUN = "ps_uart_clock_fix_20261009_172254_r02"
EVIDENCE = ROOT / "report/evidence/S2B-T06" / RUN
OLD = ROOT / "report/evidence/S2B-T06/ps_smoke_20261008_r01/build_08"
FAILED = ROOT / "report/evidence/S2B-T06/ps_uart_clock_fix_20261009_171959_r01"
CACHE = ROOT / "tmp/2B/S2B-T06/ucf_172254_r02/workspace"
TOOLS = Path(r"D:\Xilinx\2026.1\gnu\aarch32\nt\gcc-arm-none-eabi\bin")

def digest(path):
    """按实际字节绑定。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_new(directory, name, data):
    """创建UTF-8证据；现有产物一律不覆盖。"""
    with (directory / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")

def binding(path, role):
    """形成仓库相对的证据清单项。"""
    item = {"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "role": role}
    if path.suffix in (".elf", ".map"):
        item["keep_reason"] = "绑定真实编译产物及可复核布局，供独立审查和后续授权部署使用。"
    return item

def main():
    """仅核对已完成的离线构建，不连接或操作设备。"""
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(ROOT / "vitis"))
    sys.path.insert(0, str(ROOT / "verification"))
    from build_s2b_ps_smoke import exact_path, copy_exclusive
    from check_s2b_ps_smoke_layout import parse_elf
    assert json.loads((EVIDENCE / "build_receipt.json").read_text(encoding="utf-8"))["effective_exit_code"] == 0
    for item in (EVIDENCE, OLD, FAILED, CACHE, TOOLS):
        exact_path(item, "directory")
    copy_exclusive(Path(__file__).absolute(), EVIDENCE / "finalize_evidence.py")
    driver = exact_path(CACHE / "ps7/ps7_cortexa9_0/cpu0/bsp/libsrc/uartps/src", "directory")
    for name in ("xuartps.c", "xuartps_options.c"):
        copy_exclusive(driver / name, EVIDENCE / name)
    copy_exclusive(ROOT / "vitis/s2b_ps_smoke.md", EVIDENCE / "s2b_ps_smoke.md")
    old_source = (OLD / "s2b_ps_smoke.c").read_bytes()
    new_source = (ROOT / "vitis/s2b_ps_smoke.c").read_bytes()
    assert old_source.count(b"(unsigned long)uart.InputClockHz") == 1
    assert new_source == old_source.replace(b"(unsigned long)uart.InputClockHz", b"(unsigned long)uart.Config.InputClockHz")
    assert new_source == (EVIDENCE / "build/s2b_ps_smoke.c").read_bytes()
    records = []
    def run(command, log_name):
        """保留真实命令、退出码和日志。"""
        started = time.monotonic()
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, check=False)
        with (EVIDENCE / log_name).open("xb") as stream:
            stream.write(proc.stdout)
            stream.write(proc.stderr)
        records.append({"command": command, "cwd": str(ROOT), "exit_code": proc.returncode,
                        "elapsed_seconds": time.monotonic() - started, "log": log_name, "log_sha256": digest(EVIDENCE / log_name)})
        assert proc.returncode == 0, log_name
    objdump = exact_path(TOOLS / "arm-none-eabi-objdump.exe", "file")
    readelf = exact_path(TOOLS / "arm-none-eabi-readelf.exe", "file")
    gcc = exact_path(TOOLS / "arm-none-eabi-gcc.exe", "file")
    run([str(objdump), "-d", str(EVIDENCE / "build/s2b_ps_smoke.elf")], "smoke_disassembly.log")
    run([str(objdump), "-d", str(OLD / "s2b_ps_smoke.elf")], "legacy_smoke_disassembly.log")
    run([str(readelf), "--version"], "readelf_version.log")
    run([str(objdump), "--version"], "objdump_version.log")
    run(["git", "diff", "--check", "--", "vitis/s2b_ps_smoke.c", "vitis/s2b_ps_smoke.md"], "diff_check.log")
    run(["git", "diff", "--", "vitis/s2b_ps_smoke.c", "vitis/s2b_ps_smoke.md"], "source_diff.patch")
    def function_bytes(path):
        """从真实ELF符号区间提取机器码，避免只比源码。"""
        data = path.read_bytes()
        model = parse_elf(data)
        funcs = {}
        for symbol in model["symbols"]:
            if symbol["type"] != 2 or not symbol["size"] or not symbol["section"]:
                continue
            section = model["sections"][symbol["section"]]
            begin = section["offset"] + symbol["value"] - section["address"]
            funcs[symbol["name"]] = {"address": symbol["value"], "size": symbol["size"],
                                     "machine_code_sha256": hashlib.sha256(data[begin:begin + symbol["size"]]).hexdigest()}
        return model, funcs
    old_model, old_functions = function_bytes(OLD / "s2b_ps_smoke.elf")
    model, new_functions = function_bytes(EVIDENCE / "build/s2b_ps_smoke.elf")
    changes = {name: {"old": old_functions.get(name), "new": new_functions.get(name)} for name in set(old_functions) | set(new_functions) if old_functions.get(name) != new_functions.get(name)}
    assert set(changes) == {"main"}, changes
    required = ("_exit", "s2b_smoke_result", "s2b_smoke_buffer", "__s2b_smoke_buffer_start", "__s2b_smoke_buffer_end", "main")
    symbols = {name: next(item for item in model["symbols"] if item["name"] == name) for name in required}
    raw = ROOT / "report/evidence/S2B-T06/ps_jtag_retry_20261009_165853_r02/uart_raw.bin"
    old_lines = raw.read_bytes().decode("ascii").splitlines()
    assert len(old_lines) == 23 and sum(line.startswith("PATTERN_PASS ") for line in old_lines) == 16
    assert "PASS passes=2 patterns=8 verified_words=4194304 mismatches=0" in old_lines
    assert digest(raw) == "c76cf9255c4ab4259c4eb5efa1501380af7e8397839caaa9d5fc6bf8713f7d60"
    tools = {str(path): digest(path) for path in (gcc, readelf, objdump, exact_path(Path(sys.executable), "file"), exact_path(Path(r"D:\Xilinx\2026.1\Vitis\bin\vitis.bat"), "file"))}
    write_new(EVIDENCE, "diagnosis_and_binary_binding.json", {
        "schema_version": 1, "source_commit": "117911e63cd7468418f11847ffedc9293dbca075", "status": "PASS_OFFLINE_MINIMAL_FIELD_FIX",
        "hardware_execution": "NOT_RUN", "formal_software_freeze": "NOT_APPROVED_FOR_NEW_VERSION",
        "cause": "静态实例的顶层InputClockHz未被驱动赋值；CfgInitialize及SetBaudRate使用Config.InputClockHz。",
        "driver_source": [{"path": str(EVIDENCE / name), "sha256": digest(EVIDENCE / name)} for name in ("xuartps.c", "xuartps_options.c")],
        "driver_assign_line": 122, "driver_baud_clock_lines": [544, 551, 553], "driver_config_clock_hz": 100000000,
        "app_changed_line": 173, "source_sha256": digest(ROOT / "vitis/s2b_ps_smoke.c"), "doc_sha256": digest(ROOT / "vitis/s2b_ps_smoke.md"),
        "elf_sha256": digest(EVIDENCE / "build/s2b_ps_smoke.elf"), "entry": model["entry"], "symbols": symbols,
        "function_count": len(new_functions), "only_changed_function": changes,
        "unchanged_function_machine_code_count": len(new_functions) - 1,
        "old_real_run": {"uart_raw_path": raw.relative_to(ROOT).as_posix(), "uart_raw_sha256": digest(raw), "line_count": 23, "pattern_pass_count": 16,
                         "verified_words": 4194304, "mismatches": 0, "reported_clock_hz": 0,
                         "scope": "旧版功能检查条件满足，诊断缺陷单列；该结果不归于新版。"},
        "original_acceptance_clock_condition": "正式freeze及操作说明要求UART115200/8N1等完整结果；未指定clock_hz数值为原成功条件。",
        "freeze_document_sha256": digest(ROOT / "docs/obsidian-project/04-提交材料/阶段验收/stage2b_ps_smoke_offline_freeze_20261009.md"),
        "failed_first_attempt": {"path": FAILED.relative_to(ROOT).as_posix(), "reason": "CMake对象目录244字符接近250限值；依赖文件创建报错。",
                                 "recovery": "仅更换新的短缓存路径后同builder构建通过；旧失败产物保持原状。"},
        "tool_sha256": tools, "commands": records,
        "limitations": ["新版本未独立审查、未运行实板；不能沿用旧版实测。", "clock_hz是BSP配置值，物理时钟未测量。", "不改变UART设置、DDR范围、模式、协议行名和数量、异常码。", "完整进程树峰值内存及跨工具调用总量未测。"]})
    for directory in (FAILED, EVIDENCE):
        receipt = json.loads((directory / "build_receipt.json").read_text(encoding="utf-8"))
        success = receipt["effective_exit_code"] == 0
        files = [binding(path, "source" if path.suffix in (".c", ".h", ".py", ".md") else "artifact" if path.suffix in (".elf", ".map", ".ld") else "log" if path.suffix in (".log", ".patch") else "result") for path in sorted(directory.rglob("*")) if path.is_file()]
        files.extend([binding(ROOT / "vitis/s2b_ps_smoke.c", "source"), binding(ROOT / "vitis/s2b_ps_smoke.md", "source")])
        manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T06", "run_id": directory.name,
                    "source_commit": "117911e63cd7468418f11847ffedc9293dbca075", "evidence_dir": directory.relative_to(ROOT).as_posix(),
                    "interfaces": json.loads((directory / "inputs_manifest.json").read_text(encoding="utf-8"))["interfaces"],
                    "files": files, "tool_versions": {"Vitis": "2026.1", "Python": "3.13.0", "ARM_GCC": "13.4.0"},
                    "checks": [{"name": "同XSA真实离线构建和联合布局", "status": "PASS" if success else "FAIL", "command": json.dumps(receipt["command"], ensure_ascii=False),
                                "exit_code": receipt["effective_exit_code"], "reason": "真实API/布局成功且原生退出0。" if success else "原生CLI退出0但平台API失败，有效退出1；保留CMake底层依赖文件错误。"},
                               {"name": "新版实板执行", "status": "NOT_RUN", "command": None, "exit_code": None, "reason": "本次仅离线修复，不连接设备；旧实测仅绑定旧版。"}],
                    "limitations": ["包装核验不代表独立G2或硬件G3/G4/G5通过。", "新版正式软件冻结未批准；保持旧冻结与证据原件。", "首次长缓存构建失败包保留，短缓存恢复为另立新Run。"]}
        write_new(directory, "delivery_manifest.json", manifest)
    print(json.dumps({"status": "EVIDENCE_SAVED", "entry": hex(model["entry"]), "symbols": {name: hex(symbol["value"]) for name, symbol in symbols.items()},
                      "c_sha256": digest(ROOT / "vitis/s2b_ps_smoke.c"), "elf_sha256": digest(EVIDENCE / "build/s2b_ps_smoke.elf"), "changed_functions": sorted(changes)}, ensure_ascii=False), flush=True)

if __name__ == "__main__":
    main()
