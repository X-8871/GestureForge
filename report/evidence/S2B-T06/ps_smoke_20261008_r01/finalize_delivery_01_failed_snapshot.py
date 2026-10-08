#!/usr/bin/env python3
"""核对本轮实际构建证据并独占生成最终实验汇总和交付清单。"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import stat
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).absolute().parents[4]
RUN_REL = "report/evidence/S2B-T06/ps_smoke_20261008_r01"
RUN = ROOT / RUN_REL
BASELINE = "90652b45ef31e763bd3e6f7527e2fd080ece61a8"
SOURCE_HASHES = {
    "vitis/s2b_ps_smoke.c": "d2bb6f0941c2e3765c5a71f889d2e7e1e0428429237f5443510e81cedd16786b",
    "vitis/build_s2b_ps_smoke.py": "addff3a419609ac8203c8838edfd6fd56fb53baccf40efc403fca4eb36b50d76",
    "verification/check_s2b_ps_smoke_layout.py": "6c12023cc9660d392a0f3e393df2ebaf425af8a4cbb51886a35749d0c6fa0f77",
    "vitis/s2b_ps_smoke.md": "c15290c48ccbc03c55418c2efa0ca2df815eacdeffb60e53363eca4fba490db5",
}
LIMITATIONS = [
    "本交付仅完成离线开发及自动检查；独立G2审查尚未执行，实板初始化、UART和DDR为NOT_RUN。",
    "器件厂商XC/-2声明与照片XA冲突、PCB版本、电源、接线、实际DDR校准及冷JTAG条件仍须部署前人工核实。",
    "专属DDR区间是本ELF/linker的离线归属证明，不代表实板物理安全窗口或全DDR可靠性已经验证。",
    "首次实物操作须明确授权；CPU0独占、CPU1停止、无DMA或PL writer、非安全冷JTAG且BootROM完成是运行前提。",
    "没有执行debug session、connect、targets、寄存器读写、断点、下载、初始化或板卡运行命令。",
    "本轮不消费模型或AXI接口，不冻结物理PS/PL地址映射、DDR所有权业务协议或阶段2B验收指标。",
    "Vitis批处理可能在脚本失败时仍退出0，必须联合实际build_details、API结果、ELF和layout状态判断。",
    "全进程树峰值内存及本轮全部工具调用量未测；记录的API计数和子命令计数仅覆盖builder实际范围。",
    "旧失败尝试、原FSBL诊断和旧说明/审计原件均保留；人工入口只使用build_08最小OCM初始化壳。",
    "包装CHECKS_OK仅证明清单和哈希完整，不能替代G0、独立审查、实物测试或阶段验收。",
]


def require(condition: bool, message: str) -> None:
    """遇到任何版本、路径或结果不一致即停止。"""
    if not condition:
        raise ValueError(message)


def exact_regular(path: Path, directory: bool = False) -> Path:
    """逐分量核验字面名称和类型，不接受任务输入中的链接。"""
    require(path.is_absolute(), f"路径必须绝对：{path}")
    current = Path(path.anchor)
    for name in path.parts[len(current.parts):]:
        with os.scandir(current) as entries:
            require(any(entry.name == name for entry in entries), f"缺少精确分量：{current / name}")
        current = current / name
        info = os.lstat(current)
        require(not stat.S_ISLNK(info.st_mode) and not (getattr(info, "st_file_attributes", 0) & 0x400), f"拒绝链接：{current}")
    require(current.is_dir() if directory else current.is_file(), f"目标类型不符：{current}")
    return current


def sha(path: Path) -> str:
    """计算精确常规文件的原始字节哈希。"""
    return hashlib.sha256(exact_regular(path).read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    """读取UTF-8实验记录。"""
    return json.loads(exact_regular(path).read_text(encoding="utf-8"))


def new_target(name: str) -> Path:
    """核验精确父目录并拒绝覆盖任何现有名称。"""
    parent = exact_regular(RUN, directory=True)
    require("/" not in name and "\\" not in name, "新目标必须为单个文件名")
    require(not (parent / name).exists(), f"禁止覆盖：{parent / name}")
    return parent / name


def write_json(path: Path, data: dict) -> None:
    """用UTF-8/LF独占写入，失败时保留已生成文件。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def report() -> None:
    """完成轻量只读复核并记录所有实际状态。"""
    report_path = new_target("offline_validation_08.json")
    audit_path = new_target("startup_and_stop_audit_08_r02.json")
    disassembly_path = new_target("smoke_disassembly_build08_r02.log")
    details = read_json(RUN / "build_08/build_details.json")
    execution = read_json(RUN / "build_execution_08.json")
    layout = read_json(RUN / "build_08/layout_check.json")
    inputs = read_json(RUN / "inputs_manifest_r03.json")
    syntax = read_json(RUN / "operation_doc_syntax_check_r02.json")
    require(details["status"] == "PASS_OFFLINE_BUILD_AND_LAYOUT", "实际构建未通过")
    require(details["config"]["source_commit"] == details["config"]["xsa_source_commit"] == BASELINE, "固定上游提交不符")
    require(execution["post_wrapper_exit_code_observed"] == 0, "实际包装退出非零")
    require(execution["os_state"]["own_pid_still_exists"] is False, "构建自有进程未确证结束")
    require(layout["status"] == "PASS_OFFLINE_LAYOUT" and layout["initializer"]["status"] == "PASS_OFFLINE_MINIMAL_OCM_INIT", "联合布局未通过")
    require(layout["buffer_begin"] == 0x01100000 and layout["buffer_end_exclusive"] == 0x01200000 and layout["buffer_bytes"] == 1048576, "buffer区间或大小改变")
    for relative, expected in SOURCE_HASHES.items():
        path = exact_regular(ROOT / relative)
        raw = path.read_bytes()
        require(sha(path) == expected and b"\r" not in raw, f"源码哈希或LF改变：{relative}")
        raw.decode("utf-8")
        if relative.endswith(".py"):
            ast.parse(raw.decode("utf-8"), filename=str(path))
        if relative != "vitis/s2b_ps_smoke.md":
            require(details["source_sha256"][str(path)] == expected, f"构建源码绑定不同：{relative}")
            snapshot = RUN / "build_08/source_snapshot" / path.name
            require(snapshot.read_bytes() == raw, f"构建源码快照不同：{relative}")
    require(syntax["doc_sha256"] == SOURCE_HASHES["vitis/s2b_ps_smoke.md"], "操作包语法记录版本不同")
    require(syntax["status"] == "PASS_OPERATION_DOC_SYNTAX_ONLY" and len(syntax["blocks"]) == 12, "操作包解析记录不完整")
    require(all(item["status"] == "PASS_PARSE_ONLY" for item in syntax["blocks"]), "示例块解析未通过")
    require(syntax["commands_in_document_executed"] is False, "本轮不允许执行实物示例")
    for item in inputs["interfaces"] + inputs["files"]:
        require(sha(ROOT / item["path"]) == item["sha256"], f"固定输入哈希改变：{item['path']}")
    require(sha(RUN / "inputs_manifest_r03.json") == details["config"]["inputs_manifest_sha256"], "实际输入清单不同")
    for item in details["files"].values():
        require(sha(Path(item["path"])) == item["sha256"], f"产物哈希改变：{item['path']}")
    for command in details["commands"]:
        require(command["exit_code"] == 0 and sha(Path(command["log"])) == command["log_sha256"], "原实际子命令或日志未通过")
    with zipfile.ZipFile(details["config"]["xsa"]) as archive:
        for name in ("ps7_init.c", "ps7_init.h", "ps7_init.tcl"):
            require(archive.read(name) == (RUN / "build_08" / name).read_bytes(), f"初始化源非XSA同字节：{name}")
    self_test = layout["self_test"]
    negative_cases = self_test["negative_cases_rejected"] + self_test["initializer_negative_cases_rejected"] + self_test["exact_identifier_negative_cases_rejected"]
    require(self_test["status"] == "PASS" and len(negative_cases) == 14 and self_test["arm_program_executed"] is False, "14项离线反例不完整")
    require(self_test["exact_identifier_positive_cases"] == ["official_ps7GetSiliconVersion_call"], "官方标识符正例未通过")
    commit_command = ["git", "cat-file", "-e", BASELINE + "^{commit}"]
    commit_result = subprocess.run(commit_command, cwd=ROOT, capture_output=True, check=False)
    require(commit_result.returncode == 0, "真实上游提交缺失")
    status_result = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, check=False)
    require(status_result.returncode == 0, "Git状态无法读取")
    installed = read_json(RUN / "installed_paths_prebuild_r02.json")
    objdump_records = [item for item in installed["records"] if item["requested"].endswith("\\arm-none-eabi-objdump.exe")]
    require(len(objdump_records) == 1, "objdump安装记录不唯一")
    objdump = objdump_records[0]
    executable = exact_regular(Path(objdump["filesystem_target"]))
    require(sha(executable) == objdump["sha256"], "已核验objdump安装字节改变")
    command = [str(executable), "-d", str(exact_regular(RUN / "build_08/s2b_ps_smoke.elf"))]
    started = time.perf_counter()
    with disassembly_path.open("xb") as stream:
        objdump_result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=False)
    elapsed = time.perf_counter() - started
    require(objdump_result.returncode == 0, "只读objdump失败，保留新日志")
    old_audit_path = exact_regular(RUN / "startup_and_stop_audit_08.json")
    audit = read_json(old_audit_path)
    require(sha(disassembly_path) == audit["smoke_disassembly_sha256"], "同ELF只读反汇编字节不同")
    audit["smoke_objdump_command"] = command
    audit["smoke_objdump_cwd"] = str(ROOT)
    audit["smoke_objdump_exit_code"] = objdump_result.returncode
    audit["smoke_objdump_elapsed_seconds"] = elapsed
    audit["smoke_disassembly_path"] = str(disassembly_path)
    audit["correction"] = {
        "original_path": old_audit_path.relative_to(ROOT).as_posix(),
        "original_sha256": sha(old_audit_path),
        "reason": "原命令说明含Python字符串转义控制字符；原件保留，新argv由已核验真实路径构造并实际执行。ELF、日志字节和断点结论不变。",
    }
    write_json(audit_path, audit)
    history = []
    for number in range(1, 9):
        path = RUN / f"build_{number:02d}/build_details.json"
        previous = read_json(path)
        history.append({
            "attempt": number, "status": previous["status"], "details_path": path.relative_to(ROOT).as_posix(),
            "details_sha256": sha(path), "config": previous["config"], "config_sha256": previous["config_sha256"],
            "source_sha256": previous["source_sha256"], "error": previous.get("error"),
            "elapsed_seconds": previous["elapsed_seconds"], "api_call_count": previous["api_call_count"],
            "command_count": previous["command_count"], "commands": previous["commands"],
            "hardware_execution": previous["hardware_execution"], "own_server_cleanup": previous.get("own_server_cleanup"),
            "cli_exit_inference": "不根据Vitis批处理0推断脚本成功；真实FAIL/PASS以本记录和原始日志为准。",
        })
    require(all(item["status"] == "FAIL" for item in history[:7]), "旧失败原记录被改变")
    evidence = {
        name: {"path": RUN_REL + "/" + name, "sha256": sha(RUN / name)}
        for name in ["inputs_manifest_r03.json", "build_config_08.json", "build_execution_08.json", "cli_build_08.log", "build_08/build_details.json", "build_08/layout_binding.json", "build_08/layout_check.json", "startup_and_stop_audit_08_r02.json", "operation_doc_syntax_check_r02.json", "xsdb_operating_basis_r03.json"]
    }
    write_json(report_path, {
        "schema_version": 1, "status": "PASS_OFFLINE_SOURCE_INPUT_ARTIFACT_BINDINGS", "checked_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "native_python_version": sys.version,
        "source_commit": BASELINE, "xsa_source_commit": BASELINE, "source_sha256": SOURCE_HASHES,
        "input_interfaces": inputs["interfaces"], "input_files": inputs["files"], "build_attempt": 8,
        "successful_build_command": details["config"]["command"], "build_workspace": details["config"]["workspace"],
        "actual_batch_exit_code": execution["vitis_batch_exit_code_observed"], "actual_post_wrapper_exit_code": execution["post_wrapper_exit_code_observed"],
        "actual_build_elapsed_seconds": details["elapsed_seconds"], "actual_build_api_call_count": details["api_call_count"],
        "actual_build_command_count": details["command_count"], "total_build_attempts": len(history),
        "build_attempt_elapsed_sum_seconds": sum(item["elapsed_seconds"] for item in history),
        "build_attempt_api_call_count_sum": sum(item["api_call_count"] for item in history),
        "build_attempt_command_count_sum": sum(item["command_count"] for item in history),
        "peak_memory_bytes": None, "peak_memory_reason": "未测量Vitis全进程树峰值内存；不将预检空闲内存或单进程量冒充峰值。",
        "whole_task_tool_calls": None, "whole_task_tool_calls_reason": "未对全部工具调用建立完整计数；builder计数只覆盖上述真实attempt。",
        "artifacts": details["files"], "evidence": evidence, "buffer_range": [layout["buffer_begin"], layout["buffer_end_exclusive"]],
        "app_range": [layout["app_begin"], layout["app_end_exclusive"]], "buffer_bytes": layout["buffer_bytes"],
        "initializer_ocm_ranges": layout["initializer"]["ocm_ranges"], "initializer_ctor_names": layout["initializer"]["constructor_names"],
        "negative_cases_rejected": negative_cases, "exact_identifier_positive_cases": self_test["exact_identifier_positive_cases"],
        "manual_syntax_blocks": 12, "commands_in_document_executed": False, "own_server_os_cleanup": execution["os_state"],
        "history": history, "corrected_objdump": {"command": command, "exit_code": objdump_result.returncode, "elapsed_seconds": elapsed, "log": str(disassembly_path), "log_sha256": sha(disassembly_path)},
        "git_commit_existence": {"command": commit_command, "exit_code": commit_result.returncode, "scope": "仅证明提交存在；批准由正式冻结记录和acceptance单独绑定。"},
        "git_status_observed": status_result.stdout.decode("utf-8"), "hardware_execution": "NOT_RUN", "independent_review": "NOT_RUN",
        "limitations": LIMITATIONS,
    })
    print("PASS_FINAL_SOURCE_INPUT_ARTIFACT_BINDINGS")


def manifest() -> None:
    """消费已完成复核记录，绑定本Run全部文件而不提前声明包装通过。"""
    target = new_target("delivery_manifest.json")
    result = read_json(RUN / "offline_validation_08.json")
    require(result["status"] == "PASS_OFFLINE_SOURCE_INPUT_ARTIFACT_BINDINGS", "必须先实际完成复核")
    inputs = read_json(RUN / "inputs_manifest_r03.json")
    details = read_json(RUN / "build_08/build_details.json")
    files = [{"path": relative, "sha256": sha(ROOT / relative), "role": "source"} for relative in SOURCE_HASHES]
    files.extend(inputs["files"])
    files.append({"path": "verification/check_stage_delivery.py", "sha256": sha(ROOT / "verification/check_stage_delivery.py"), "role": "input"})
    for path in sorted(RUN.rglob("*"), key=lambda item: item.relative_to(RUN).as_posix()):
        if path.is_dir():
            exact_regular(path, directory=True)
            continue
        exact_regular(path)
        relative = path.relative_to(ROOT).as_posix()
        if path.suffix == ".log":
            role, reason = "log", "保留原始命令输出、真实失败和后续诊断，不能只凭包装或CLI退出判断结果。"
        elif path.suffix in {".elf", ".map", ".ld"}:
            role, reason = "artifact", "用于本版本ELF/链接布局复核；build_08为当前候选，旧attempt产物仅供失败诊断，禁止作为人工入口。"
        elif path.suffix == ".json":
            role, reason = "result", "保留版本绑定、实际配置、自动检查和失败状态；各字段的FAIL/NOT_RUN不因包装检查通过而更改。"
        else:
            role, reason = "diagnostic", "保留实际源码快照、BSP/startup/初始化来源或帮助核验脚本，支持复核真实构建和旧失败。"
        files.append({"path": relative, "sha256": sha(path), "role": role, "keep_reason": reason})
    commands = details["commands"]
    finalize_command = subprocess.list2cmdline([sys.executable, "-B", str(Path(__file__).absolute()), "report"])
    checks = [
        {"name": "固定上游输入清单", "status": "PASS", "command": subprocess.list2cmdline(commands[0]["command"]), "exit_code": commands[0]["exit_code"], "reason": "仅核对G0声明的固定输入；批准来自正式冻结记录。"},
        {"name": "全新隔离workspace真实平台及两个应用构建", "status": "PASS", "command": details["config"]["command"], "exit_code": result["actual_post_wrapper_exit_code"], "reason": "原API platform.build/app.build/initializer.build均实际成功0；CLI0之外联合ELF、map及实际layout核验。"},
        {"name": "真实ELF联合布局和14项反例", "status": "PASS", "command": subprocess.list2cmdline(commands[-1]["command"]), "exit_code": commands[-1]["exit_code"], "reason": "真实ARM文件只作离线解析；官方ps7GetSiliconVersion正例接受，真正GetSiliconVersion反例拒绝。"},
        {"name": "最终源码输入产物及历史失败保全核对", "status": "PASS", "command": finalize_command, "exit_code": 0, "reason": "此命令已完成并返回0；原build_01至07仍为FAIL，不重新标成成功。"},
        {"name": "固定ELF返回断点只读反汇编", "status": "PASS", "command": subprocess.list2cmdline(result["corrected_objdump"]["command"]), "exit_code": result["corrected_objdump"]["exit_code"], "reason": "原审计命令说明转义错误保留，新argv和相同反汇编字节由实际命令重新绑定。"},
        {"name": "旧build_07检查器误报", "status": "FAIL", "command": subprocess.list2cmdline(result["history"][6]["commands"][-1]["command"]), "exit_code": result["history"][6]["commands"][-1]["exit_code"], "reason": "旧检查器把ps7GetSiliconVersion当作GetSiliconVersion，原失败和字节保留；精确标识符修正后全新build_08实际通过。"},
        {"name": "独立G2审查", "status": "NOT_RUN", "command": None, "exit_code": None, "reason": "Developer停止写入后由总控安排独立Reviewer，在隔离目录真实重建。"},
        {"name": "板卡初始化UART和DDR", "status": "NOT_RUN", "command": None, "exit_code": None, "reason": "本轮授权仅离线软件准备，尚未连接或操作板卡；物理身份与CPU0独占等运行前提仍待人工核实。"},
    ]
    write_json(target, {
        "schema_version": 1, "stage": "2B", "task_id": "S2B-T06", "run_id": "ps_smoke_20261008_r01", "source_commit": BASELINE,
        "evidence_dir": RUN_REL, "interfaces": inputs["interfaces"], "files": files, "checks": checks, "limitations": LIMITATIONS,
        "tool_versions": {"Vitis": "2026.1 SW Build 6511674", "A9 GCC": "arm-xilinx-eabi 13.4.0", "Vitis API Python": "3.13.0", "Native Python": result.get("native_python_version", "3.12.10"), "Layout checker": "SHA256 " + SOURCE_HASHES["verification/check_s2b_ps_smoke_layout.py"]},
    })
    print("CREATED_DELIVERY_MANIFEST", len(files), sha(target))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["report", "manifest"])
    args = parser.parse_args()
    require(Path.cwd() == ROOT, "必须在精确项目根执行")
    if args.phase == "report":
        report()
    else:
        manifest()
