"""S4-T31 载荷登记生成器（离线；不接触板卡、不启动 xsdb）。

只为四项实测生成本地登记清单：工具链路径、Tcl 载荷、可选既有载荷（r13 诊断件，
**本轮不使用**，仅登记身份）、以及 M1–M4 的载荷判定矩阵。
输出：report/evidence/S4-B/s4_ddr_four_measurements_20261027_r01/preparation/payload_registry.json
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CN = timezone(timedelta(hours=8))
W = Path(r"D:\codex-worktrees\w4")
RUN = W / "report" / "evidence" / "S4-B" / "s4_ddr_four_measurements_20261027_r01"
PREP = RUN / "preparation"


def sha256_file(path: Path) -> str | None:
    """文件 SHA-256（不存在返回 None）。"""
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def entry(path: Path, role: str, note: str = "") -> dict[str, object]:
    """登记一个文件：仓库相对路径 + 完整 SHA-256 + 大小。"""
    try:
        rel = str(path.relative_to(W)).replace("\\", "/")
    except ValueError:
        rel = str(path)
    return {
        "path": rel,
        "absolute_path": str(path),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size if path.is_file() else None,
        "role": role,
        "note": note,
    }


def main() -> int:
    """生成 payload_registry.json。"""
    PREP.mkdir(parents=True, exist_ok=True)

    plan = W / "docs" / "stage4" / "S4B_ddr_four_measurements_execution_plan_20261027_r01.md"
    tcl = {name: W / "scripts" / "stage4_s4b" / name
           for name in ("m1_cpu1_state.tcl", "m2_consumer_check.tcl", "m3_candidate_rw.tcl")}

    # 既有载荷（r13 诊断件）：仅登记身份，本轮不装载
    r13 = W / "report" / "evidence" / "S4-B" / "s4b_ps_tensor_20261023_r13"
    existing = [entry(r13 / "s4b_ps_tensor_diagnostic.elf", "existing_payload_not_used",
                      "业务诊断程序（张量/权重绑定），违反“不加业务功能”要求 ⇒ 本轮不装载"),
                entry(r13 / "s4b_ps_tensor_diagnostic.map", "existing_payload_not_used", "同上"),
                entry(r13 / "verified_payload" / "init.elf", "existing_payload_not_used",
                      "r13 初始化载荷；本轮 M1–M3 不需要（纯 JTAG 寄存器/内存访问）")]

    registry = {
        "schema_version": 1,
        "task_id": "S4-B/S4-T31",
        "run_id": "s4_ddr_four_measurements_20261027_r01",
        "generated_utc8": datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds"),
        "hardware_execution": "NOT_RUN",
        "board_access": "NONE（离线准备；未启动 hw_server/xsdb、未装载、未接触板卡）",
        "authorization": {
            "window": "report/evidence/CTRL-DSH-HANDOFF/decisions/window_s4_four_measurements_authorization_20261027_r01.md",
            "window_minutes": 45,
            "issues_window": "NO（须 DSH 项目总控下达“开窗”指令）",
        },
        "host": {"platform": platform.platform(), "python": sys.version},
        "toolchain": [
            {"id": "xsdb", "path": r"D:\Xilinx\2026.1\Vitis\bin\xsdb.bat",
             "exists": Path(r"D:\Xilinx\2026.1\Vitis\bin\xsdb.bat").is_file(),
             "version": "PENDING_SMOKE（离线期禁止启动 xsdb，版本在窗口 P1 smoke 记录）",
             "note": "xsdb Python 包路径 D:/Xilinx/2026.1/Vitis/scripts/xsdb 与 cli/python-packages/site-packages（既有 runner 文档记录）"},
            {"id": "vitis_install", "path": r"D:\Xilinx\2026.1\Vitis", "exists": Path(r"D:\Xilinx\2026.1\Vitis").is_dir()},
            {"id": "vivado_install", "path": r"D:\Xilinx\2026.1\Vivado", "exists": Path(r"D:\Xilinx\2026.1\Vivado").is_dir()},
        ],
        "payloads": {
            "plan_document": entry(plan, "plan", "M1–M4 执行计划书（含恢复算法、判定阈值、停止条件、45 min 预算）"),
            "tcl_scripts": [entry(p, "payload_tcl", "离线新增；未经真实 xsdb 执行（窗口 P1 先 smoke）")
                            for p in tcl.values()],
            "existing_not_used": existing,
            "minimal_measurement_elf": {
                "status": "READY",
                "purpose": "**M4-a 用，不用于推理**（不含业务功能：只做区间内读/写、cache 维护、CRC）",
                "elf": entry(PREP / "payloads" / "m4a_cache_probe.elf", "payload_elf",
                             "OCM 装载（0x0/0x4000/0xffff0000），与候选区零重叠 ⇒ 下载不污染被测区"),
                "map": entry(PREP / "payloads" / "m4a_cache_probe.map", "payload_map", "链接映射"),
                "build_record": entry(PREP / "payloads" / "build_record.json", "build_record",
                                      "工具链版本、完整编译/链接命令、源/链接脚本/BSP 库 SHA-256"),
                "source": entry(W / "scripts" / "stage4_s4b" / "m4a_src" / "m4a_cache_probe.c", "payload_source",
                                "最小测量程序源码（离线可复现构建）"),
                "build_script": entry(W / "scripts" / "stage4_s4b" / "build_m4a_measurement_elf.py", "build_script",
                                      "python -B scripts/stage4_s4b/build_m4a_measurement_elf.py（离线；窗口内禁止编译）"),
                "toolchain_version": "arm-xilinx-eabi-gcc (GCC) 13.4.0（Vitis 2026.1 aarch32）",
                "uart_protocol": "COM4 115200 8N1；命令 R/I/F/W/Q；应答行以 M4A 开头；cache 维护按 64 B 向外取整",
                "constraints_verified": "只在候选区内读写；越界请求拒绝；装载段与候选区零重叠；无 PL/DMA/业务功能",
            },
        },
        "applicability": {
            "M1": {"payload": "none（纯 JTAG 目标/寄存器查询）", "status": "READY",
                   "judgment": "CPU1 state=halted 且间隔 2 s 两次 PC 不变"},
            "M2": {"payload": "none（targets + DevCfg STATUS 只读）", "status": "READY_WITH_CONSTRUCTIVE_LIMIT",
                   "judgment": "无第二调试客户端 + PL 未配置（PCAP STATUS）+ CPU1 halted；"
                               "总线级 DDR 活动无探针 ⇒ 以构造性证明替代，证据须显式标注"},
            "M3": {"payload": "none（mrd/mwr，区间断言内）", "status": "READY_WITH_TIME_RISK",
                   "judgment": "先只读快照 → 写-回读 → 回写原字节 → SHA+逐字节双判据差异必须为 0；"
                               "速率探针外推 >18 min 时降级为分层抽样并标 SAMPLED_PARTIAL"},
            "M4a": {"payload": "init.elf（必需）+ m4a_cache_probe.elf（本轮构建）", "status": "READY",
                    "judgment": "flush/invalidate（64 B 向外取整）后 PS 侧 CRC/回读与 JTAG 侧写入/恢复一致"},
            "M4b": {"payload": "无（需 PL consumer）", "status": "NOT_APPLICABLE",
                    "judgment": "DMA 可见性需 PL master ⇒ 改设计；**并入 4-D bring-up 作为必测项**"},
            "M4_overall": {"status": "PARTIAL_READY",
                           "note": "M4-a 可测；M4-b NOT_APPLICABLE ⇒ **M4 未闭合 ⇒ ENABLE=1 前置不满足**，"
                                   "本窗口即使 M1/M2/M3/M4-a 全过也不得申请 ENABLE=1/4-D（另裁）"},
        },
        "risk_statement": {
            "R1_M3_write_ddr": "写候选区属破坏性操作；缓解：先只读快照落盘+SHA，写前再断言区间，恢复用快照回写并双判据校验；掉电时可用已落盘快照在下一窗口恢复",
            "R2_M3_time": "12,615,680 B × 4 次 JTAG 传输可能逼近预算；缓解：64 KiB 速率探针 → 外推 → 抽样降级（标 SAMPLED_PARTIAL）",
            "R3_M2_limit": "无总线级探针，只能构造性排除；不得表述为直接测量了 DDR 总线",
            "R4_M4_not_applicable": "M4-b 需 PL consumer（改设计）⇒ NOT_APPLICABLE；且导致 ENABLE=1 前置不满足，须另裁",
            "R5_tcl_unverified": "边界禁止开窗前启动 xsdb ⇒ Tcl 未在真实工具上验证；窗口 P1 先 smoke，失败即停不现场改脚本",
            "R6_foreign_process": "P0 核对不通过（他方 hw_server/Vivado/COM4 占用/锁）则不开口",
            "R7_identity": "装载前逐项比对本清单 SHA，不符即停",
        },
        "not_done": [
            "未启动 xsdb / 未连接板卡 / 未装载任何载荷（窗口外禁止）",
            "Tcl 与最小 ELF 均**未在真实 xsdb/板上执行过**（窗口 P1 先 smoke）",
            "M4-b（DMA 可见性）不在本窗口：NOT_APPLICABLE，并入 4-D bring-up",
            "未开窗（等待 DSH 项目总控指令）",
        ],
        "boundary": "只读离线准备；ENABLE=0；不 FROZEN；无板级访问；不 push；不构成任何关口通过。",
    }

    out = PREP / "payload_registry.json"
    out.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"registry": str(out), "sha256": sha256_file(out),
                      "tcl": [{"path": e["path"], "sha256": e["sha256"]} for e in registry["payloads"]["tcl_scripts"]],
                      "plan_sha256": registry["payloads"]["plan_document"]["sha256"],
                      "elf_sha256": registry["payloads"]["minimal_measurement_elf"]["elf"]["sha256"],
                      "M4a": registry["applicability"]["M4a"]["status"],
                      "M4b": registry["applicability"]["M4b"]["status"],
                      "M4_overall": registry["applicability"]["M4_overall"]["status"]},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())