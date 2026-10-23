import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"D:\codex-worktrees\w4")
RUN_ID = "s4b_ps_tensor_20261023_r13"
OLD_RUN_ID = "s4b_ps_tensor_20261023_r12"
EVIDENCE_REL = f"report/evidence/S4-B/{RUN_ID}"
EVIDENCE_DIR = ROOT / EVIDENCE_REL
MANIFEST_PATH = EVIDENCE_DIR / "delivery_manifest.json"
TEMPLATE_PATH = ROOT / "report/evidence/S4-B" / OLD_RUN_ID / "delivery_manifest.json"
EXPECTED_HEAD = "b7aceb8e81fe297511d0581d43c08aabf7df46f9"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_first(path: Path) -> str:
    return path.read_text(encoding="utf-8").splitlines()[0].strip()


def record_command(records: dict, name: str) -> tuple[str, int]:
    row = records[name]
    command = subprocess.list2cmdline(row["command"])
    return command, row["exit_code"]


def main() -> None:
    if Path.cwd().resolve() != ROOT.resolve():
        raise RuntimeError("当前目录不是任务指定的w4工作树")
    if MANIFEST_PATH.exists():
        raise RuntimeError("拒绝覆盖既有r13 delivery manifest")
    head = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    if head != EXPECTED_HEAD:
        raise RuntimeError(f"r13构建基线改变：{head}")
    manifest = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    manifest["run_id"] = RUN_ID
    manifest["source_commit"] = head
    manifest["evidence_dir"] = EVIDENCE_REL
    run_cfg = json.loads((EVIDENCE_DIR / "run_config.json").read_text(encoding="utf-8"))
    if run_cfg.get("run_id") != RUN_ID or run_cfg.get("hardware_reservation_status") != "BUILD_ONLY_NOT_RESERVED_FOR_HARDWARE":
        raise RuntimeError("r13 run_config身份或预留状态不匹配")

    for row in manifest["files"]:
        relative = row["path"].replace(OLD_RUN_ID, RUN_ID)
        path = ROOT / Path(relative)
        if not path.is_file():
            raise RuntimeError(f"清单输入文件缺失：{relative}")
        row["path"] = relative
        row["sha256"] = sha256(path)
    for interface in manifest["interfaces"]:
        interface_path = ROOT / Path(interface["path"])
        interface["sha256"] = sha256(interface_path)

    listed_evidence = {row["path"] for row in manifest["files"] if row["path"].startswith(EVIDENCE_REL + "/")}
    actual_evidence = {
        path.relative_to(ROOT).as_posix()
        for path in EVIDENCE_DIR.rglob("*")
        if path.is_file() and path != MANIFEST_PATH
    }
    if listed_evidence != actual_evidence:
        missing = sorted(actual_evidence - listed_evidence)
        extra = sorted(listed_evidence - actual_evidence)
        raise RuntimeError(f"r13清单未精确枚举目录，未列={missing}，不存在={extra}")

    commands_path = EVIDENCE_DIR / "commands.json"
    commands = json.loads(commands_path.read_text(encoding="utf-8"))["commands"]
    command_rows = {row["name"]: row for row in commands}
    machine = json.loads((EVIDENCE_DIR / "machine_result.json").read_text(encoding="utf-8"))
    inventory = json.loads((EVIDENCE_DIR / "external_inputs_inventory.json").read_text(encoding="utf-8"))
    suite = machine["host_tests"]
    run_command = subprocess.list2cmdline([
        sys.executable, "-B", "scripts/stage4_s4b/build_s4b_ps_tensor.py",
        "--run-id", RUN_ID,
        "--boot-seed", run_cfg["boot_seed"],
        "--session-first", run_cfg["session_first"],
        "--session-last", run_cfg["session_last"],
    ])
    checks = []

    def add(name: str, status: str, command: str | None, exit_code: int | None, reason: str) -> None:
        checks.append({"name": name, "status": status, "command": command, "exit_code": exit_code, "reason": reason})

    frozen_pass = machine.get("external_inputs_unchanged_after_build") is True and all(
        row.get("exists") is True and row.get("status") == "PASS" for row in inventory.get("external_inputs", [])
    )
    add("external_frozen_input_hashes", "PASS" if frozen_pass else "FAIL", run_command, 0 if frozen_pass else 1,
        "r13构建器已前后核对恢复包、冻结app、模型/XSA及工具输入，结果记录于external_inputs_inventory.json。")
    for key, check_name, command_name, reason in (
        ("strict_host_c_compile", "strict_host_c_api_compile", "host_c_api_compile", "严格C11主机编译及警告视为错误。"),
        ("direct_c_api_regression", "direct_host_c_api_regression", "host_c_api_regression", "主机C API回归，覆盖记录发布与不可覆盖语义。"),
        ("u32_session_exhaustion", "u32_session_range_exhaustion", "host_c_api_session_exhaustion", "u32 session范围耗尽不回绕、不重用。"),
        ("python_unit_status", "python_snapshot_binding_path_memory_suite", "python_unit_suite", "38项PS tensor源码/接口单元测试通过；含成功RUN后one-shot停泊测试。"),
    ):
        status = "PASS" if suite.get(key) == "PASS" else "FAIL"
        command, exit_code = record_command(command_rows, command_name)
        add(check_name, status, command, exit_code, reason)
    arm_names = [row["name"] for row in commands if row["name"].startswith("compile_") or row["name"] == "link_s4b_ps_tensor"]
    arm_codes = [command_rows[name]["exit_code"] for name in arm_names]
    arm_pass = bool(arm_names) and all(code == 0 for code in arm_codes)
    add("official_aarch32_compile_link", "PASS" if arm_pass else "FAIL",
        "commands.json中的三个AArch32编译单元及链接记录", 0 if arm_pass else 1,
        "使用随冻结恢复包绑定的BSP头文件、静态库及链接脚本离线编译链接；未运行Vitis平台重建。")
    elf_names = ("elf_size", "elf_sections", "elf_symbols")
    elf_codes = [command_rows[name]["exit_code"] for name in elf_names]
    elf_pass = all(code == 0 for code in elf_codes) and bool(machine.get("memory_ranges"))
    add("elf_memory_layout", "PASS" if elf_pass else "FAIL",
        "commands.json中的elf_size/elf_sections/elf_symbols及memory_ranges.json", 0 if elf_pass else 1,
        "离线核对ELF符号/段、trace与PS arena、stack和输入范围；不代表实物地址图获批。")
    add("hardware_board_ps_pl_uart", "NOT_RUN", None, None,
        "未执行JTAG、UART、板卡装载、PS运行、PL、DDR导出、停止或恢复。")
    add("rgb_preprocessing", "BLOCKED", None, None,
        "RGB预处理仍BLOCKED_PENDING_G0；本构建仅接收已准备的INT8_CHW_416张量。")
    manifest["checks"] = checks
    manifest["tool_versions"] = {
        "python": sys.version.splitlines()[0] + " (AMD64)",
        "host_gcc": text_first(EVIDENCE_DIR / "host_gcc_version.stdout.txt"),
        "official_aarch32_gcc": text_first(EVIDENCE_DIR / "aarch32_gcc_version.stdout.txt"),
        "aarch32_tools": "工具文件SHA-256记录于external_inputs_inventory.json",
    }
    manifest["limitations"] = list(machine.get("limitations", [])) + [
        "delivery_manifest.json在离线构建完成后按r13实际文件、日志、运行配置及源码当前字节生成；source_commit记录构建时Git基线，files行提供实际字节SHA。"
    ]
    raw = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with MANIFEST_PATH.open("xb") as stream:
        stream.write(raw)
        stream.flush()
    print(f"MANIFEST_WRITTEN={MANIFEST_PATH}")
    print(f"MANIFEST_SHA256={hashlib.sha256(raw).hexdigest()}")
    print(f"SOURCE_COMMIT={head}")
    print(f"EVIDENCE_FILES={len(actual_evidence)}; ALL_FILES={len(manifest['files'])}")


if __name__ == "__main__":
    main()
