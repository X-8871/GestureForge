#!/usr/bin/env python3
"""为本次 Vitis 离线构建生成可复核的阶段证据清单。"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RUN_ID = "implemented_xsa_20261014_r01"
EVIDENCE = ROOT / "report/evidence/S2B-T15" / RUN_ID
CONFIG = ROOT / "tmp/2B/S2B-T15/build_implemented_20261014_r01.json"
PLATFORM_DIR = ROOT / "report/evidence/S2B-T19/visibility0_hp_rebuild_20261014_r02"
PLATFORM_MANIFEST = PLATFORM_DIR / "delivery_manifest.json"
XSA = PLATFORM_DIR / "s2b_inference_implemented_r02.xsa"
MODEL = ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
MANIFEST = EVIDENCE / "delivery_manifest.json"


def require(condition: bool, message: str) -> None:
    """使用显式条件保护证据绑定。"""
    if not condition:
        raise RuntimeError(message)


def digest(path: Path) -> str:
    """计算文件原始字节 SHA-256。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entry(path: Path, role: str, reason: str) -> dict[str, str]:
    """生成仓库内文件条目并绑定完整字节摘要。"""
    resolved = path.resolve(strict=True)
    require(resolved.is_relative_to(ROOT), f"证据路径必须位于仓库内：{resolved}")
    require(resolved.is_file() and not resolved.is_symlink(), f"必须是普通文件：{resolved}")
    return {
        "path": resolved.relative_to(ROOT).as_posix(),
        "sha256": digest(resolved),
        "role": role,
        "keep_reason": reason,
    }


def main() -> None:
    """核验构建结果、绑定输入与源文件，并写出清单。"""
    details_path = EVIDENCE / "build_details.json"
    details = json.loads(details_path.read_text(encoding="utf-8"))
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    require(details["status"] == "PASS_OFFLINE_FULL_XSA_BUILD", "Vitis 完整 XSA 离线构建未通过")
    require(details["hardware_execution"] == "NOT_RUN", "本证据任务意外包含实板动作")
    require(details["config_sha256"] == digest(CONFIG), "构建配置哈希与 build_details 不一致")
    require(details["xsa_sha256"] == digest(XSA) == config["xsa_sha256"], "implemented XSA 绑定不一致")
    require(digest(PLATFORM_MANIFEST) == config["platform_manifest_sha256"], "上游平台清单哈希不一致")
    require(details["own_server_cleanup"] == "DISPOSE_CALLED", "独占 Vitis server 未记录释放")
    require(all(item["exit_code"] == 0 for item in details["commands"]), "工具版本、readelf 或 objdump 命令失败")

    app = json.loads((EVIDENCE / "elf_layout.json").read_text(encoding="utf-8"))
    arenas = [section for section in app["sections"] if section["name"] == ".s2b_tensor_ddr"]
    require(app["entry"] == 0x00100000, "应用 ELF 入口不在批准的 DDR 应用区域")
    require(len(arenas) == 1 and arenas[0]["type"] == 8 and arenas[0]["address"] == 0x10000000
            and arenas[0]["size"] == 0x02000000 and arenas[0]["align"] >= 64,
            "应用 ELF 的 32 MiB NOLOAD arena 布局错误")
    require(digest(EVIDENCE / "infer.elf") == details["elf"]["sha256"], "应用 ELF 哈希与构建回执不一致")

    init = json.loads((EVIDENCE / "init_elf_layout.json").read_text(encoding="utf-8"))
    allocated = [section for section in init["sections"] if section["flags"] & 2 and section["size"]]
    require(all((0 <= section["address"] and section["address"] + section["size"] <= 0x30000)
                or (0xFFFF0000 <= section["address"] and section["address"] + section["size"] <= 0xFFFFFE00)
                for section in allocated), "PS 初始化 ELF 含 OCM 外的已分配节")
    symbols = {symbol["name"] for symbol in init["symbols"]}
    require({"s2b_ps_init_ready", "s2b_ps_init_fail", "ps7_init"} <= symbols, "PS 初始化 ELF 入口符号缺失")
    require(digest(EVIDENCE / "init.elf") == details["initializer_elf"]["sha256"], "初始化 ELF 哈希与回执不一致")

    platform_log = (EVIDENCE / "vitis_platform_cpu0_build.log").read_text(encoding="utf-8", errors="replace")
    app_log = (EVIDENCE / "vitis_app_build.log").read_text(encoding="utf-8", errors="replace")
    init_log = (EVIDENCE / "vitis_ps_init_build.log").read_text(encoding="utf-8", errors="replace")
    require("[102/102]" in platform_log, "CPU0 BSP 原生日志没有完整构建结束标记")
    require("[4/4] Linking C executable infer.elf" in app_log, "应用原生日志未记录最终链接步骤")
    require("[4/4] Linking C executable init.elf" in init_log, "初始化原生日志未记录最终链接步骤")

    source_entries = []
    source_names = {
        "vitis/s2b_inference_app.c": "绑定本次应用编译输入。",
        "vitis/build_s2b_inference.py": "绑定本次 Vitis 构建逻辑。",
        "vitis/build_s2b_ps_smoke.py": "绑定本次 Vitis 公共 ELF、缓存及路径核验逻辑。",
        "verification/s2a_ps_decode_nms_reference.c": "绑定应用导入的冻结 C 解码参考。",
        "verification/s2a_ps_decode_nms_reference.h": "绑定应用导入的冻结 C 解码参考头文件。",
        "verification/s2b_board_transport.py": "绑定本次应用使用的 UART 运输协议实现。",
        "verification/check_s2b_ps_smoke_layout.py": "绑定本次 ELF 和缓存契约核验实现。",
    }
    for relative, expected_hash in sorted(details["source_sha256"].items()):
        source = ROOT / relative
        require(relative in source_names and digest(source) == expected_hash, f"源码与构建快照不一致：{relative}")
        committed = subprocess.run(["git", "show", f"{details['source_commit']}:{relative}"], cwd=ROOT,
                                   capture_output=True, check=True).stdout
        require(hashlib.sha256(committed).hexdigest() == expected_hash, f"源码不匹配绑定提交：{relative}")
        source_entries.append(entry(source, "source", source_names[relative]))
    require(set(details["source_sha256"]) == set(source_names), "构建源码绑定集合不完整")

    files = []
    for path in sorted(EVIDENCE.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"证据目录出现符号链接：{path}")
        if not path.is_file() or path == MANIFEST:
            continue
        relative = path.relative_to(EVIDENCE).as_posix()
        if "source_snapshot/" in relative or path.name == "package_delivery_manifest.py":
            role, reason = "source", "保留本次 Vitis 实际消费的源码快照及清单生成器。"
        elif path.suffix.casefold() == ".log":
            role, reason = "log", "保留 Vitis/GNU 工具的原始构建、链接或失败诊断日志。"
        elif path.suffix.casefold() == ".json":
            role, reason = "result", "保留本次构建回执、编译命令、输入输出绑定及 ELF 核验结果。"
        else:
            role, reason = "artifact", "保留本次 CPU0 应用、PS 初始化、平台输入副本或链接诊断产物。"
        files.append(entry(path, role, reason))

    for path, reason in (
        (MODEL, "绑定冻结 S2A-T01 tiny416 模型描述。"),
        (XSA, "绑定 R02 实现位流、完整 PS/PL 与 -2 器件配置的平台输入。"),
        (PLATFORM_MANIFEST, "绑定经 R02 独立复审的实现与平台证据清单。"),
        (CONFIG, "绑定本次 Vitis 构建的提交、XSA、平台清单及唯一输出路径。"),
    ):
        files.append(entry(path, "input", reason))
    files.extend(source_entries)
    files.sort(key=lambda item: item["path"])
    require(len({item["path"] for item in files}) == len(files), "清单文件路径重复")

    physical = ROOT / "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
    uart = ROOT / "docs/obsidian-project/02-方案设计/s2b_board_transport.md"
    model_interface = ROOT / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
    manifest = {
        "schema_version": 1,
        "stage": "2B",
        "task_id": "S2B-T15",
        "run_id": RUN_ID,
        "source_commit": details["source_commit"],
        "evidence_dir": "report/evidence/S2B-T15/" + RUN_ID,
        "interfaces": [
            {"name": "tiny416 模型、张量与逻辑 CSR 接口", "version": "S2A-T01/G0", "frozen": True,
             "path": model_interface.relative_to(ROOT).as_posix(), "sha256": digest(model_interface)},
            {"name": "PS/PL 物理接口候选", "version": "s2b-physical-candidate/0.1.1", "frozen": False,
             "path": physical.relative_to(ROOT).as_posix(), "sha256": digest(physical)},
            {"name": "CPU0/UART 运输候选", "version": "s2bu-candidate/1.1", "frozen": False,
             "path": uart.relative_to(ROOT).as_posix(), "sha256": digest(uart)},
        ],
        "files": files,
        "checks": [
            {"name": "初次 Vitis 启动受沙箱阻断", "status": "FAIL",
             "command": "Vitis 2026.1 -s vitis/build_s2b_inference.py（首次沙箱内调用）", "exit_code": 1,
             "reason": "Python 在读取配置时枚举 C:\\Users\\22061 收到 WinError 5；失败发生在构建预检阶段，未创建工作区、ELF 或证据输出。完整摘要日志已保留，未被误记为设计失败。"},
            {"name": "源码及提交绑定", "status": "PASS",
             "command": "核对 build_details source_sha256、源码快照及 Git 提交对象", "exit_code": 0,
             "reason": "7 个应用、构建器、运输、解码参考和 ELF/缓存核验源码的散列均匹配绑定提交与本次快照。"},
            {"name": "implemented XSA 与 CPU0 BSP", "status": "PASS",
             "command": "Vitis 2026.1 client.create_platform_component/platform.build", "exit_code": 0,
             "reason": f"完整实现 XSA SHA-256={details['xsa_sha256']}；平台含 CPU0 standalone，UART1 为 stdin/stdout；实际 BSP 编译完成 102/102。"},
            {"name": "CPU0 推理应用及 DDR ELF 布局", "status": "PASS",
             "command": "Vitis 2026.1 app.build；readelf/objdump；build_s2b_inference.verify_app_elf", "exit_code": 0,
             "reason": f"应用入口 0x{app['entry']:08X}；32 MiB arena 为 0x10000000 NOLOAD、64-byte 对齐；ELF SHA-256={details['elf']['sha256']}；应用及冻结 C 解码参考按 -Werror 构建。"},
            {"name": "同 XSA PS 初始化 ELF 与 OCM 布局", "status": "PASS",
             "command": "Vitis 2026.1 init.build；readelf/objdump；OCM 与入口符号检查", "exit_code": 0,
             "reason": f"init.elf 已链接，分配节位于 OCM，含受控 ps7_init 入口及 ready/fail 标志；SHA-256={details['initializer_elf']['sha256']}。只构建，未执行。"},
            {"name": "Vitis 离线完整平台构建", "status": "PASS",
             "command": "S2B_INFERENCE_CONFIG=<本清单绑定配置>; D:\\Xilinx\\2026.1\\Vitis\\bin\\vitis.bat -s vitis/build_s2b_inference.py", "exit_code": 0,
             "reason": f"Vitis v2026.1 (64-bit)；状态 PASS_OFFLINE_FULL_XSA_BUILD；独占 server 已释放；总耗时 {details['elapsed_seconds']:.1f} 秒；硬件执行 NOT_RUN。"},
            {"name": "证据目录 SHA-256 封装核验", "status": "PASS",
             "command": "ROSS ipcfg::python_exec 调用 verification/check_stage_delivery.py 的 evidence 模式", "exit_code": 0,
             "reason": "最终运行目录内所有文件均由本清单绑定；校验器返回 CHECKS_OK 且无 errors/warnings。本项仅为封装核验。"},
            {"name": "G0 PS/PL 与 UART 接口冻结", "status": "BLOCKED", "command": None, "exit_code": None,
             "reason": "PS/PL 文档仍为 CANDIDATE_NOT_FROZEN，UART 文档仍为候选版本；该阻塞需要由 Wong 决定接口冻结依据。"},
            {"name": "JTAG 下载、PS 初始化、UART/DDR/cache 与模型板测", "status": "NOT_RUN", "command": None, "exit_code": None,
             "reason": "本次仅离线构建，板卡保持断电；G0 与冷启动生命周期回执尚未冻结，未尝试下载或执行 ELF。"},
        ],
        "limitations": [
            "本次仅证明基于 R02 implemented XSA 的离线 CPU0 BSP、推理应用与同 XSA PS 初始化 ELF 成功构建；不是 G3/G4/G5 或模型上板验收。",
            "AX7020 芯片照片丝印为 XA7Z020 CLG400，用户转述厂商确认实板 XC7Z020-2CLG400I；当前 XSA 按 xc7z020clg400-2 构建，但物理器件及温级尚未现场核实。",
            "PS/PL 物理接口 s2b-physical-candidate/0.1.1 与 UART s2bu-candidate/1.1 均未冻结；板级部署准入代码缺少固定 G0 与冷启动回执，实板操作仍阻断。",
            "应用 ELF 入口为 0x00100000，32 MiB NOLOAD arena 位于 0x10000000；生成 PS 初始化 ELF 只从该 XSA 提取并编译，未通过 JTAG 执行。",
            "BSP 原始日志记录了厂商 dmaps 未使用参数警告；同 XSA 的 ps7_init.c 在 -Wall/-Wextra 下有符号比较警告；应用代码和冻结解码参考以 -Werror 成功构建。",
            "Vitis 进程树峰值内存未测量；首个沙箱内启动因系统访问权限失败，随后相同绑定的离线构建退出码为 0。",
        ],
        "tool_versions": {
            "Vivado": "2026.1 build 6511674",
            "Vitis": "2026.1 (64-bit; SW Build 6511674)",
            "ARM GNU": "arm-xilinx-eabi-gcc 13.4.0",
        },
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"manifest": MANIFEST.relative_to(ROOT).as_posix(), "files": len(files),
                      "manifest_sha256": digest(MANIFEST), "build_status": details["status"]},
                     ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
