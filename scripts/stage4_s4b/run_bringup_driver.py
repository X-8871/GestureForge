"""阶段4 4-D bring-up 执行驱动 v3.2.6（S4-T34；S1 候选区口径 + 快照恢复 + PS-PL 四动作 + xsdb 错误文本守卫 + cmd 元字符规避）。

v3.2 变更（2026-10-28，窗口 #2 根因修复）：
  1. **修复 NameError**：`load_elf_ddr()` 引用模块级 `INIT_ELF`，v3.1 从未赋值 ⇒ 装载阶段必抛
     `NameError`；v3.2 定义 `INIT_ELF`（registry 内 verified_payload/init.elf）并新增自检
     `init_elf_constant_defined` 与**真实执行 `load_elf_ddr()` 路径**的 mock 自检。
  2. **PS-PL 电平转换器使能**（窗口 #2 证据：`mrd 0x43C00000` 先报 `Bitstream is not programmed`，
     装 PL 后报 `Level shifters are not enabled` ⇒ PS 访问 PL AXI-Lite 被拒，M4-b 卡在 `M4B STEP=1`）：
     新增 `enable_ps_pl_level_shifters()`（SLCR 解锁→写 LVL_SHFTR_EN→加锁→**读回断言**）与
     `stage_pspl_setup_and_load()`（复位→0xA→装 PL→0xF+读回→装 init/app），并在每次 ELF 装载后
     **内联重断言 0xF 且读回校验**；`_PL_STATE["programmed"]` 为真时装载改用 `rst -processor -stop`，
     避免 `rst -system -stop` 清空 PL（v3.1 的三个装载点都会清 PL）。
     **UG585 v1.2（厂商 TRM，`ug585-Zynq-7000-TRM.pdf`）依据**：
       * §2.4.8 PS–PL Voltage Level Shifter Enables（文档页 46）："If the PL is being configured, the
         level shifters should be set to 0xA … Once the PL is fully configured, the level shifter
         enables should be set to 0xF."
       * §2.5 注（文档页 46）／§5 Interconnect（文档页 106/112/113）："The PL level shifters must be
         enabled via LVL_SHFTR_EN before PL logic communication can occur."
       * §6 Boot and Configuration，PL Reconfiguration flow（文档页 150）：步骤 2 写 0xA 关闭、
         步骤 10 写 0xF 使能。
       * Appendix B.28 System Level Control Registers (slcr)：SLCR 基址 0xF8000000；
         **SLCR_UNLOCK** abs `0xF8000008`（`UNLOCK_KEY[15:0]=0xDF0D` 解除写保护，文档页 1411）；
         **SLCR_LOCK** abs `0xF8000004`（`LOCK_KEY[15:0]=0x767B` 重新加锁，文档页 1411）；
         **LVL_SHFTR_EN** abs `0xF8000900`，rw，reset `0x00000000`，bit3 `USER_LVL_INP_EN_0`、
         bit2 `USER_LVL_OUT_EN_0`、bit1 `USER_LVL_INP_EN_1`、bit0 `USER_LVL_OUT_EN_1`，
         bit4 reserved“Do not modify”、31:5 reserved（文档页 1522）。
       * 注：**重新加锁是写 `0x767B` 到 `0xF8000004`**，不是写 0 到 `0xF8000008`。
  3. 自检新增：`init_elf_constant_defined`、`load_elf_ddr_*`（mock 硬件真实跑装载路径）、
     `lvl_shifter_tcl_exact`、`lvl_shifter_readback_0xF_pass`、`lvl_shifter_readback_0xA_must_fail`、
     `pspl_stage_wires_lvl_shifter`。
  4. **v3.2.1（窗口 #3 实测暴露的两层工具缺陷）**：
     (a) 读回输出原为 `puts "PPL_LVL_RB=$_rb"`，实测 **xsdb 把 `=` 变成一个空格**，且 `mrd -value`
         返回**十进制**（日志实际为 `PPL_LVL_RB 10`）；旧解析正则又会误匹配**日志首行的回显命令**
         （其中含同样字样）⇒ 假 FAIL。
     (b) 改用 `format "… %08X"` 后，**`%0` 被 cmd 当作 `%0`（批处理脚本名）展开**，输出变成
         `PPL_LVL_RB D:Xilinx?6.1Vitisinxsdb.bat8X` ⇒ 再次假 FAIL。
     最终方案：**完全避开 `%` 与 `=`**——输出 **两行**（`PPL_LVL_RB` 标记行 + 十进制数值行）
     加一行 TCL 侧判定（`PPL_LVL_RB_OK`/`_BAD`，由 `if {$_rb == <value>}` 在板端比较）；
     驱动按"标记行之后的第一个非空行"解析数值，并以 TCL 侧判定交叉校验。
     自检新增 `lvl_shifter_parses_real_log_shape(0xA)` 与 `lvl_shifter_echo_line_not_misparsed`
     两条按**真实日志形状**（含回显命令与 OK/BAD 行）的回归。
  5. **v3.2.2（窗口 #3 r04 实测）**：内联断言原用 `expr {$_rb & 0xF}`，而 **`&` 经 `cmd /c` 是命令分隔符**
     ⇒ `dow` 整条命令 `exit=255 "The syntax of the command is incorrect."`（M4-b 装载失败，应用根本没跑）。
     改为直接比较 `$_rb != <value>`（无 `&`）。**教训：经 `cmd /c` 传给 xsdb 的 TCL 里不得出现
     `%`（被当 `%0` 展开）、`&`（命令分隔符）**；已加自检 `pspl_tcl_no_cmd_metachars`。
  6. **v3.2.3（CSR 通路审计后补入）**：2B XSA 的 `ps7_post_config` 是**四动作**
     （`s2b_board_jtag.py:199-200`）：`SLCR_UNLOCK=0xDF0D → LVL_SHFTR_EN → **FPGA_RST_CTRL=0** → SLCR_LOCK=0x767B`；
     v3.2.2 只做了两个，**缺 `mwr 0xF8000240 0x0`（撤销 FPGA 软复位）**。本版补齐并按 2B 顺序执行，
     读回断言改为**两条**（`0xF8000900`=value 且 `0xF8000240`=0），新增自检
     `pspl_four_actions_order`、`fpga_rst_ctrl_zero_readback`、`fpga_rst_ctrl_nonzero_must_fail`。
     依据见 `docs/stage4/S4D_ps_pl_level_shifter_enable_20261028_r01.md` 与
     `report/evidence/S4-T34/csr_base_audit_20261028_r01/`（UG585 §2.6 / PDF 页 1412、1454）。
     **注意：仍不把 JTAG `mrd 0x43C00000` 作判据**（调试器需 `loadhw` 登记地址，属工具限制）。
  7. **v3.2.4（窗口 #4 实测的 fail-open 修复）**：`xsdb -eval` 在 TCL 报错时**进程退出码仍为 0**
     （实测 `W0_write.exit_code.txt=0` 而日志是 `no targets found`）⇒ 只判进程码会**假成功**。
     本版新增 `XSDb_ERROR_PATTERNS` + `_xsdb_error_text()` + `xsdb_checked()` + `jtag_write_checked()`：
     命中 `no targets found` / `while executing` / `Memory read|write error` / `Invalid target` /
     `not been added to the memory map` / `unexpected arguments` / `not supported for target`
     ⇒ **该步直接判 FAIL（无论进程码）**；`load_elf_ddr`、S1b 恢复写、四动作使能均已接入。
     另新增 **`dap_recovered()` 双条件判定**（lead 2026-10-28 裁决）：必须 ① 枚举到
     `Cortex-A9 MPCore #0` **且** ② 该行不含 `APB AP transaction error`，缺一不得写"恢复"。

与 v2 的差别：
  1. 分段固定顺序：**S1 bisect → S2 DDR 位测试 → 装载 PS 应用 → M4-b → M4-a → M3 复检 →（可选 chain-lite）→ 收尾**；
     顺序来自 bring-up 清单对齐结论：M3 复检必须放在 M4-b/M4-a **之后**，避免被 M3 提前阻断；
  2. **S1 bisect（只读）**：复位后 dump D0 → 装 PL 后 dump D1 → dow init.elf+con 后 dump D2，两两比较给出
     `CHANGED_AT_PL_PROGRAM` / `CHANGED_AT_INIT_EXEC` / `PRE_EXISTING_CHANGE` / `NEITHER_STAGE`，全程只 mrd；
  3. **S2 DDR 位测试（受控写+恢复）**：区域 `0x11AE0000–0x11B00000`（128 KiB），4 图样（0x00、0xFF、0xAA55 交替、
     walking-1），T0 立即 / T1 全图样写完后 / T2 延迟 1 s 读回比对；**收尾按快照恢复，恢复 diff 必须 0**；
     判定 `DDR_BIT_TEST_PASS` / `DDR_BIT_ERROR_SUSPECTED` / `DDR_RETENTION_SUSPECTED`；恢复差异≠0 **立即停**；
  4. **装载新 PS 应用**：先核 ELF SHA-256 前缀 `1224f048`（SW 变体）→ `rst -system -stop` → `dow init.elf` → `con`
     → 等 → `dow app` → `rst -processor -stop` → `con`；**必须收到 UART 横幅 `S4D PS APP` 才继续**；
  5. **M4-b → M4-a → M3**：判据沿用 v2 已验证实现（`run_window_b_driver` 模块），不再写死状态；
  6. 每步真实退出码落 `<step>.exit_code.txt`；任一步 FAIL 即停；`--chain-lite` 在应用尚未输出框 JSON 时
     如实记 `NOT_RUN` 并写原因，**不得**用离线结果替代；
  7. `--offline-selftest`：不碰硬件，纯函数验证区域算术、图样、身份前缀、判定逻辑、顺序、Tcl 桩与"无硬编码"。

用法（离线上板前预演）：
  python -B scripts/stage4_s4b/run_bringup_driver.py --offline-selftest
用法（开板窗口，板卡档期获批后）：
  python -B scripts/stage4_s4b/run_bringup_driver.py --window \
      --bit <bit> --init-elf <init.elf> --app-elf <s4d_ps_app_sw0.elf> \
      --m4b-elf <m4b.elf> --m4b-input <bin> --m4b-weights <bin> --m4b-head13 <bin> --m4b-head26 <bin> \
      --m3-reference <m3_snapshot_orig.bin> [--chain-lite]
退出码：0=全 PASS 或合法 NOT_RUN；1=有 FAIL/中止；2=输入错误；3=离线自检失败。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import re
import struct
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

W = Path(r"D:\codex-worktrees\w4")
SCRIPTS = W / "scripts" / "stage4_s4b"
sys.path.insert(0, str(SCRIPTS))

import run_window_b_driver as base  # noqa: E402  v2 已验证原语（xsdb/jtag/uart/M4/M3）

CN = timezone(timedelta(hours=8))
RUN_DIR = W / "report" / "evidence" / "S4-T34" / "bringup_driver_v3_20261028_r01"
BIT_REGISTERED_PREFIX = "555a70c2"
# 应用身份：r2（M4-b 加 STEP 标记 + 强符号保活；解码接线判据不变）
APP_SW_SHA = "4fc095ae6283a893960d77d607c8e0471b5787e639e6f072383fb41f34c0aaba"
APP_SW_PREFIX = "4fc095ae"
APP_SW_SHA_R1 = "1224f04891bfc9229d361a55d73932a4200eafc33918d859d418a0b5f32f8b34"

# ---- v3.2：init.elf（v3.1 缺失导致 load_elf_ddr NameError）----
INIT_ELF = W / "report/evidence/S4-B/s4b_ps_tensor_20261023_r13/verified_payload/init.elf"

# ---- v3.2：PS-PL 电平转换器（UG585 v1.2 Appendix B.28；见模块 docstring 的章节/位定义引用）----
SLCR_UNLOCK_ADDR = 0xF8000008   # SLCR_UNLOCK：UNLOCK_KEY[15:0]=0xDF0D 解除写保护（文档页 1411）
SLCR_LOCK_ADDR = 0xF8000004     # SLCR_LOCK：LOCK_KEY[15:0]=0x767B 重新加锁（文档页 1411）
LVL_SHFTR_EN_ADDR = 0xF8000900  # LVL_SHFTR_EN：bits[3:0]=INP/OUT_EN_0/1；bit4 保留勿改（文档页 1522）
FPGA_RST_CTRL_ADDR = 0xF8000240  # FPGA_RST_CTRL：FPGA[3:0]_OUT_RST 等软复位，写 0 = 撤销（文档页 1412/1454）
SLCR_UNLOCK_KEY = 0xDF0D
SLCR_LOCK_KEY = 0x767B
LVL_SHFTR_CFG = 0xA             # §2.4.8：PL 配置期间（关输入、防毛刺）
LVL_SHFTR_ON = 0xF              # §2.4.8/§6：PL 配置完成后使能全部
_PL_STATE = {"programmed": False, "lvl_readback": None, "fpga_rst_ctrl_readback": None}

# ---- v3.2.4：xsdb 日志错误文本守卫（fail-closed；xsdb 在 TCL 报错时进程码仍为 0）----
XSDb_ERROR_PATTERNS = (
    "no targets found",
    "while executing",
    "memory read error",
    "memory write error",
    "invalid target",
    "not been added to the memory map",
    "unexpected arguments",
    "not supported for target",
)


def dap_recovered(targets_text: str | None) -> tuple[bool, dict]:
    """DAP 恢复判定（**双条件**，缺一不得写"恢复"）：

    ① 枚举到 `Cortex-A9 MPCore #0`；
    ② 该行**不含** `APB AP transaction error`（有错误码说明调试 APB 仍不可用）。
    依据：lead 2026-10-28 裁决（窗口 #4 观测到 A9 出现但带 `DAP status 0xF0000021`）。
    """
    txt = targets_text or ""
    a9_lines = [ln.strip() for ln in txt.splitlines()
                if "Cortex-A9" in ln and "#0" in ln]
    cond1 = bool(a9_lines)
    cond2 = cond1 and not any("APB AP transaction error" in ln for ln in a9_lines)
    detail = {"a9_line": a9_lines[0] if a9_lines else None,
              "cond1_enumerated_a9": cond1,
              "cond2_no_apb_error_on_a9_line": cond2,
              "apb_error_present_on_a9": any("APB AP transaction error" in ln for ln in a9_lines)}
    return (cond1 and cond2), detail

# 候选区（S1 dump / 恢复；12,615,680 B）
CAND_BASE = 0x12000000
CAND_END = 0x12C08000
CAND_BYTES = CAND_END - CAND_BASE
# DDR 位测试区（S2；128 KiB）
TEST_BASE = 0x11AE0000
TEST_END = 0x11B00000
TEST_BYTES = TEST_END - TEST_BASE
# S1 精简模式：6 个已知变化地址（±64 B，向下 64 B 对齐）
PROBE_ADDRS = (0x12B09E1B, 0x12B4805B, 0x12B4906A, 0x12B4930E, 0x12BC8F82, 0x12BC9F5B)
HEAD26_END = 0x11ADADB8          # 头 26 数据末尾（冻结证据）
META_REQ = 0x12C00000            # HOST_REQ
META_RESULT = 0x12C00100         # PS_RESULT

STAGE_ORDER = ["S1_bisect", "S2_ddr_bit_test", "P2_load_app",
               "M4b_dma_visibility", "M4a_cache_visibility", "M3_recheck",
               "S3_chain_lite", "P4_teardown"]

BUDGET_MIN = {"S1_bisect": 10, "S2_ddr_bit_test": 20, "P2_load_app": 4,
              "M4b_dma_visibility": 8, "M4a_cache_visibility": 5, "M3_recheck": 7,
              "S3_chain_lite": 5, "P4_teardown": 1}

FORBIDDEN_TOKENS = (
    # offline-selftest 允许：以下为禁用词清单本身，扫描时整段跳过
    "NOT_APPLICABLE", 'status": "PASS"', "TODO_PASS", "hardcoded")
    # offline-selftest 允许：禁用词清单结束


# ---------------------------------------------------------------- 纯函数（离线可测）

def now_cn() -> str:
    """UTC+8 时间串。"""
    return datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds")


def sha256_file(path: Path | None) -> str | None:
    """文件 SHA-256。"""
    if path is None or not Path(path).is_file():
        return None
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def region_arithmetic_ok() -> tuple[bool, dict]:
    """区域算术：候选区 12,615,680 B；测试区 128 KiB、64 B 对齐、不压 head26。"""
    detail = {
        "candidate": {"base": hex(CAND_BASE), "end": hex(CAND_END), "bytes": CAND_BYTES,
                      "size_12_6m": CAND_BYTES == 12615680,
                      "aligned64": CAND_BASE % 64 == 0 and CAND_END % 64 == 0},
        "test": {"base": hex(TEST_BASE), "end": hex(TEST_END), "bytes": TEST_BYTES,
                 "aligned64": TEST_BASE % 64 == 0 and TEST_END % 64 == 0,
                 "size_128k": TEST_BYTES == 0x20000,
                 "no_head26_overlap": TEST_BASE > HEAD26_END,
                 "below_meta": TEST_END <= META_REQ},
        "probe_addrs": [hex(a) for a in PROBE_ADDRS],
        "probe_aligned": all((a & ~0x3F) % 64 == 0 for a in PROBE_ADDRS),
    }
    ok = (detail["candidate"]["size_12_6m"] and detail["candidate"]["aligned64"]
          and all(v for k, v in detail["test"].items() if isinstance(v, bool))
          and len(PROBE_ADDRS) == 6)
    return ok, detail


def make_pattern(name: str, nbytes: int) -> bytes:
    """生成 S2 图样字节（长度必须 4 字节对齐）。"""
    if nbytes % 4 != 0:
        raise ValueError("图样长度须 4 字节对齐")
    n = nbytes // 4
    if name == "zeros":
        return b"\x00" * nbytes
    if name == "ones":
        return b"\xff" * nbytes
    if name == "aa55":
        return (struct.pack("<I", 0xAA55AA55) * n)[:nbytes]
    if name == "walking1":
        words = [struct.pack("<I", 1 << (i % 32)) for i in range(n)]
        return b"".join(words)
    raise ValueError(f"未知图样 {name}")


def s1_verdict(dumps: list[tuple[str, bytes]], expected_len: int | None = None) -> tuple[str, dict]:
    """S1 bisect 判定：两两比较 D0/D1/D2。

    长度前置：给定 expected_len 时，任一 dump 长度不等 ⇒ INVALID_LENGTH（禁止用 zip 截断产生假 0 diff）。
    """
    if len(dumps) != 3:
        raise ValueError("S1 需要 D0/D1/D2 三份 dump")
    names = [d[0] for d in dumps]
    datas = [d[1] for d in dumps]
    if expected_len is not None:
        lens = {n: len(d) for n, d in zip(names, datas)}
        if any(v != expected_len for v in lens.values()):
            return "INVALID_LENGTH", {"labels": names, "lengths": lens,
                                      "expected_len": expected_len,
                                      "rule": "长度不等 ⇒ 不得比较、不得判 0 diff"}
    same01 = datas[0] == datas[1]
    same12 = datas[1] == datas[2]
    same02 = datas[0] == datas[2]
    detail = {"labels": names, "same_D0_D1": same01, "same_D1_D2": same12,
              "same_D0_D2": same02,
              "diff_byte_counts": {
                  "D0_vs_D1": sum(a != b for a, b in zip(datas[0], datas[1])),
                  "D1_vs_D2": sum(a != b for a, b in zip(datas[1], datas[2])),
                  "D0_vs_D2": sum(a != b for a, b in zip(datas[0], datas[2]))}}
    if same01 and same12:
        return "NEITHER_STAGE", detail          # 全程无变化
    if not same01 and same12:
        return "CHANGED_AT_PL_PROGRAM", detail  # 装 PL 后变化，init 后又不变
    if same01 and not same12:
        return "CHANGED_AT_INIT_EXEC", detail   # init.elf+con 后变化
    if same02:
        return "NEITHER_STAGE", detail          # 两端相同、中间不同 ⇒ 已回改，按未解释处理
    return "PRE_EXISTING_CHANGE", detail        # 每一步都在变或首尾不一致


def s2_verdict(results: dict, restore_diff: int) -> tuple[str, dict]:
    """S2 DDR 位测试判定。"""
    if restore_diff != 0:
        return "HARD_STOP_RESTORE_DIFF", {"restore_diff": restore_diff}
    bad = {k: v for k, v in results.items() if v}
    if not bad:
        return "DDR_BIT_TEST_PASS", {"errors": 0}
    t1_only = all(k.startswith("T2_") for k in bad) is False and "T2" in "".join(bad)
    retention = all(k.startswith("T2_") for k in bad) and not any(k.startswith("T0_") or k.startswith("T1_") for k in bad)
    if retention or t1_only:
        return "DDR_RETENTION_SUSPECTED", {"failing": sorted(bad)}
    return "DDR_BIT_ERROR_SUSPECTED", {"failing": sorted(bad)}


def s1_tcl(step: str, action: str, init_elf: Path | None = None) -> str:
    """生成 S1 只读 Tcl（复位/装 PL 由外部程序调用；dump 全用 mrd）。"""
    pre = f"connect -url {base.HW_URL}; {base.select_core()}"
    if action == "dump":
        return (pre + f"mrd -bin -file {{outfile}} {hex(CAND_BASE)} {CAND_BYTES // 4}; "
                      "disconnect; exit")
    if action == "reset_stop":
        return pre + "rst -system -stop; puts \"S1_RST_STOPPED\"; disconnect; exit"
    if action == "ps7_init":
        # DDR 控制器复位时不可读；init.elf 自带 ps7_init，先运行它把 DDR 配置起来再停核
        return pre + f"rst -system -stop; dow {Path(init_elf).as_posix()}; con; after 2000; " \
                     "rst -processor -stop; puts \"S1_PS7_INIT_DONE\"; disconnect; exit"
    if action == "d2_keep_pl":
        # 分支①：**保持 PL 配置**，只停核 + 装 init（不 rst -system，不清 PL）
        return pre + f"rst -processor -stop; dow {Path(init_elf).as_posix()}; con; after 2000; " \
                     "rst -processor -stop; puts \"S1_D2_KEEP_PL\"; disconnect; exit"
    if action == "d2_system_reset":
        # 分支②：系统复位后重新初始化（含 DDR 重新初始化）
        return pre + f"rst -system -stop; dow {Path(init_elf).as_posix()}; con; after 2000; " \
                     "rst -processor -stop; puts \"S1_D2_SYSTEM_RESET\"; disconnect; exit"
    if action == "init_con":
        return pre + f"rst -system -stop; dow {Path(init_elf).as_posix()}; con; after 3000; " \
                     "rst -processor -stop; puts \"S1_INIT_RUNNING\"; disconnect; exit"
    raise ValueError(f"未知 S1 动作 {action}")


def s2_tcl(action: str, addr: int, nbytes: int, pattern: Path | None = None) -> str:
    """生成 S2 受控写/读 Tcl（写只发生在候选窗口内）。"""
    pre = f"connect -url {base.HW_URL}; {base.select_core()}"
    if action == "read":
        return (pre + f"mrd -bin -file {{outfile}} {hex(addr)} {nbytes // 4}; "
                      "disconnect; exit")
    if action == "write":
        return (pre + f"mwr -bin -file {Path(pattern).as_posix()} {hex(addr)} {nbytes // 4}; "
                      "puts \"S2_WRITTEN\"; disconnect; exit")
    raise ValueError(f"未知 S2 动作 {action}")


# ---------------------------------------------------------------- v3.2 PS-PL 电平转换器
def parse_mrd_value(raw: str | None) -> int | None:
    """解析 xsdb `mrd -value` 的读回值（可能是 `0x…`、8 位十六进制、或十进制）。"""
    s = (raw or "").strip()
    if not s:
        return None
    if s.lower().startswith("0x"):
        try:
            return int(s, 16)
        except ValueError:
            return None
    if re.fullmatch(r"[0-9a-fA-F]{8}", s):
        return int(s, 16)
    if re.fullmatch(r"[0-9a-fA-F]+", s) and re.search(r"[a-fA-F]", s):
        return int(s, 16)
    if re.fullmatch(r"[0-9]+", s):
        return int(s, 10)
    return None


def _xsdb_error_text(txt: str | None) -> str | None:
    """在 xsdb 日志里找 TCL/硬件错误文本；命中即返回该行（**fail-closed 守卫**）。

    背景（窗口 #4 实测）：`xsdb -eval` 在 TCL 报错时**进程退出码仍为 0**
    （例：`W0_write.exit_code.txt=0` 而日志是 `no targets found`）⇒ 只判进程码会**假成功**。
    """
    low = (txt or "").lower()
    for pat in XSDb_ERROR_PATTERNS:
        if pat in low:
            for line in (txt or "").splitlines():
                if pat in line.lower():
                    return line.strip()[:200]
            return pat
    return None


def xsdb_checked(eval_text: str, tag: str, timeout: int = 1200) -> tuple[int, str | None]:
    """执行 xsdb 并**同时**校验进程码与日志错误文本；返回 (exit_code, error_text)。"""
    code = base.xsdb(eval_text, tag, timeout=timeout)
    return code, _xsdb_error_text(_read_step_log(tag))


def jtag_write_checked(path: Path, addr: int, tag: str, words: int) -> tuple[int, str | None]:
    """整块写内存并校验日志错误文本（防"TCL 报错但进程码 0"的假成功）。"""
    return xsdb_checked(f"connect -url {base.HW_URL}; {base.select_core()}"
                        f"mwr -bin -file {Path(path).as_posix()} {hex(addr)} {words}; "
                        f"disconnect; exit", tag)


def lvl_shifter_tcl(value: int, readback_hint: str = "PPL_LVL_RB") -> str:
    """生成 PS-PL 使能 TCL：**四动作**（与 2B `ps7_post_config` 一致）+ 双读回。

    顺序（`s2b_board_jtag.py:199-200` 的四动作）：
      1. `SLCR_UNLOCK  = 0xDF0D → 0xF8000008`
      2. `LVL_SHFTR_EN = <value> → 0xF8000900`
      3. `FPGA_RST_CTRL = 0x0 → 0xF8000240`（撤销 FPGA 软复位；**v3.2.2 遗漏，本版补入**）
      4. `SLCR_LOCK    = 0x767B → 0xF8000004`

    依据 UG585 v1.2（厂商 TRM `ug585-Zynq-7000-TRM.pdf`，均为**原文核对**）：
      * §2.4.8（文档页 46）：配置期间 0xA / 配置完成后 0xF；
      * §2.5 注（文档页 46）、§5（文档页 106/112/113）：LVL_SHFTR_EN 必须在 PL 逻辑通信前使能；
      * §6 PL Reconfiguration flow（文档页 150）：步骤 2 写 0xA、步骤 10 写 0xF；
      * Appendix B.28（文档页 1411/1522）：SLCR_UNLOCK `0xF8000008`/`0xDF0D`、
        SLCR_LOCK `0xF8000004`/`0x767B`、LVL_SHFTR_EN `0xF8000900`（bits[3:0]）；
      * **`slcr.FPGA_RST_CTRL` = `0xF8000240`**（rw，"FPGA Software Reset Control"，汇总文档页 1412、
        详表页 1454；语义 §2.6 文档页 47：控制 `FPGA[3:0]_OUT_RST`，异步于 FCLK），写 0 = 撤销软复位。

    读回断言**两条**：`0xF8000900` 必须 = value、`0xF8000240` 必须 = 0；任一不符即 FAIL。
    注意：经 `cmd /c` 传给 xsdb 的 TCL **不得含 `%`（会被当 `%0` 展开）与 `&`（命令分隔符）**。
    """
    return (
        f"connect -url {base.HW_URL}; {base.select_core()}"
        f"mwr {hex(SLCR_UNLOCK_ADDR)} {hex(SLCR_UNLOCK_KEY)}; "
        f"mwr {hex(LVL_SHFTR_EN_ADDR)} {hex(value)}; "
        f"mwr {hex(FPGA_RST_CTRL_ADDR)} 0x0; "
        f"mwr {hex(SLCR_LOCK_ADDR)} {hex(SLCR_LOCK_KEY)}; "
        f"set _rb [mrd -value {hex(LVL_SHFTR_EN_ADDR)}]; "
        f"set _rb2 [mrd -value {hex(FPGA_RST_CTRL_ADDR)}]; "
        f"puts {{{readback_hint}}}; puts $_rb; "
        f"puts {{{readback_hint}_RST}}; puts $_rb2; "
        f"if {{$_rb == {value}}} {{ puts {{{readback_hint}_OK}} }} "
        f"else {{ puts {{{readback_hint}_BAD}} }}; "
        f"if {{$_rb2 == 0}} {{ puts {{{readback_hint}_RST_OK}} }} "
        f"else {{ puts {{{readback_hint}_RST_BAD}} }}; "
        f"disconnect; exit"
    )


def lvl_shifter_inline_assert(value: int = LVL_SHFTR_ON, hint: str = "PPL_LVL_RB") -> str:
    """装载/启动前的**内联**断言片段（四动作 + 双读回）；任一读回不符即 `error` 终止该步。

    v3.2.5：**整段不使用双引号**（puts/error 全用 Tcl 大括号）。原因：经 `cmd /c xsdb.bat -eval`
    传递时内嵌 `"` 会被 cmd 重新切分（窗口 #4 r03 实测：`dow` 整条命令 `exit=255`，
    日志为 `...puts \"HOLD_STATE was unexpected at this time.`）。
    """
    return (
        f"mwr {hex(SLCR_UNLOCK_ADDR)} {hex(SLCR_UNLOCK_KEY)}; "
        f"mwr {hex(LVL_SHFTR_EN_ADDR)} {hex(value)}; "
        f"mwr {hex(FPGA_RST_CTRL_ADDR)} 0x0; "
        f"mwr {hex(SLCR_LOCK_ADDR)} {hex(SLCR_LOCK_KEY)}; "
        f"set _rb [mrd -value {hex(LVL_SHFTR_EN_ADDR)}]; "
        f"set _rb2 [mrd -value {hex(FPGA_RST_CTRL_ADDR)}]; "
        f"puts {{{hint}}}; puts $_rb; puts {{{hint}_RST}}; puts $_rb2; "
        f"if {{$_rb == {value}}} {{}} else "
        f"{{ error {{PS-PL level shifters readback not equal to {hex(value)}}} }}; "
        f"if {{$_rb2 == 0}} {{}} else "
        f"{{ error {{FPGA_RST_CTRL readback not zero, FPGA soft reset still asserted}} }}; "
    )


def _read_step_log(tag: str) -> str:
    """读 `<tag>.log`：优先驱动 RUN_DIR，其次 base.RUN_DIR（base.xsdb 的落盘位置）。"""
    for root in (RUN_DIR, getattr(base, "RUN_DIR", None)):
        if not root:
            continue
        p = Path(root) / f"{tag}.log"
        if p.is_file():
            return p.read_text(encoding="utf-8", errors="replace")
    return ""


def _log_marker_value(lines: list[str], marker: str) -> str | None:
    """取"独占一行的 marker"之后的第一个非空行（xsdb 把 puts 的每行单独输出）。"""
    for i, ln in enumerate(lines):
        if ln == marker:
            for nxt in lines[i + 1:]:
                if nxt:
                    return nxt
            return None
    return None


def enable_ps_pl_level_shifters(value: int = LVL_SHFTR_ON, tag: str = "PPL_lvl_shifter") -> dict:
    """执行四动作并**双读回断言**：`0xF8000900`=value **且** `0xF8000240`=0，任一不符即 FAIL。

    v3.2.1 修正：xsdb 日志首行是回显的整条 `-eval`（含同样标记字样），旧正则误匹配 ⇒ 现按
    "独占一行的 marker + 下一个非空行"解析（回显行不会整行等于 marker）。
    v3.2.3：补 `FPGA_RST_CTRL=0` 并纳入断言（2B `ps7_post_config` 四动作之一）。
    """
    code = base.xsdb(lvl_shifter_tcl(value), tag)
    txt = _read_step_log(tag)
    lines = [ln.strip() for ln in txt.replace("\r\n", "\n").split("\n")]
    raw = _log_marker_value(lines, "PPL_LVL_RB")
    raw_rst = _log_marker_value(lines, "PPL_LVL_RB_RST")
    readback = parse_mrd_value(raw)
    rst_readback = parse_mrd_value(raw_rst)
    tcl_verdict = ("OK" if "PPL_LVL_RB_OK" in lines
                   else ("BAD" if "PPL_LVL_RB_BAD" in lines else None))
    rst_verdict = ("OK" if "PPL_LVL_RB_RST_OK" in lines
                   else ("BAD" if "PPL_LVL_RB_RST_BAD" in lines else None))
    err = _xsdb_error_text(txt)
    ok = (code == 0 and err is None and readback == value and rst_readback == 0
          and tcl_verdict != "BAD" and rst_verdict != "BAD")
    res = {"status": "PASS" if ok else "FAIL", "exit_code": 0 if ok else 1,
           "actions": ["SLCR_UNLOCK=0xDF0D", f"LVL_SHFTR_EN={hex(value)}",
                       "FPGA_RST_CTRL=0x0", "SLCR_LOCK=0x767B"],
           "xsdb_error_text": err,
           "write_value": hex(value), "readback_raw": raw, "tcl_verdict": tcl_verdict,
           "readback": hex(readback) if readback is not None else None,
           "fpga_rst_ctrl_raw": raw_rst, "fpga_rst_ctrl_verdict": rst_verdict,
           "fpga_rst_ctrl_readback": hex(rst_readback) if rst_readback is not None else None,
           "xsdb_exit": code,
           "ug585_ref": ("v1.2 §2.4.8（配置期 0xA / 完成 0xF）、§2.5 note、§6 PL Reconfiguration 步骤 2/10、"
                         "Appendix B.28（SLCR_UNLOCK 0xF8000008=0xDF0D；SLCR_LOCK 0xF8000004=0x767B；"
                         "LVL_SHFTR_EN 0xF8000900 bits[3:0]；FPGA_RST_CTRL 0xF8000240 见 §2.6/页 1454）"),
           "note": "双读回：LVL_SHFTR_EN 必须等于写入值、FPGA_RST_CTRL 必须为 0；任一不符即 FAIL，不继续"}
    if ok:
        _PL_STATE["lvl_readback"] = readback
        _PL_STATE["fpga_rst_ctrl_readback"] = rst_readback
    return res


def no_hardcoded_status(source: str) -> tuple[bool, dict]:
    """源码不得写死 NOT_APPLICABLE / 固定 PASS 字段。"""
    hits = []
    in_allow_block = False
    for line_no, line in enumerate(source.splitlines(), 1):
        if "# offline-selftest 允许：以下为禁用词清单本身" in line:
            in_allow_block = True
            continue
        if "# offline-selftest 允许：禁用词清单结束" in line:
            in_allow_block = False
            continue
        if in_allow_block or "# offline-selftest 允许" in line:
            continue
        if "no_hardcoded_status" in line or "源码不得写死" in line:   # 扫描器自身
            continue
        for tok in FORBIDDEN_TOKENS:
            if tok not in line:
                continue
            # 允许"判定后返回"：PASS 由同一行条件表达式决定
            if tok == 'status": "PASS"' and ("if " in line or "else" in line
                                               or '"verdict": verdict' in line):
                continue
            hits.append({"line": line_no, "token": tok, "text": line.strip()[:120]})
    return not hits, {"hits": hits}


def order_ok() -> tuple[bool, dict]:
    """顺序断言：M4-b 在 M4-a 之前、M4-a 在 M3 之前，S1/S2 在最前。"""
    idx = {name: STAGE_ORDER.index(name) for name in STAGE_ORDER}
    ok = (idx["S1_bisect"] < idx["S2_ddr_bit_test"] < idx["M4b_dma_visibility"]
          < idx["M4a_cache_visibility"] < idx["M3_recheck"] < idx["S3_chain_lite"])
    return ok, {"order": STAGE_ORDER, "ok": ok}


def budget_ok() -> tuple[bool, dict]:
    """时间盒：总预算 60 min 内（teardown 计入）。"""
    total = sum(BUDGET_MIN.values())
    return total <= 60, {"budget_min": BUDGET_MIN, "total": total, "limit": 60}


def tcl_stubs_ok() -> tuple[bool, dict]:
    """Tcl 桩自检：PL 装载脚本含 PROGRAM_OK 判据。"""
    p = SCRIPTS / "program_2b_bit.tcl"
    txt = p.read_text(encoding="utf-8") if p.is_file() else ""
    detail = {"exists": p.is_file(), "has_PROGRAM_OK": "PROGRAM_OK" in txt,
              "has_program_hw": "program_hw_devices" in txt}
    return all(detail.values()), detail


def chain_lite_available(app_prints_boxes: bool) -> tuple[str, str]:
    """chain-lite 可用性：应用必须已在 UART 输出框 JSON 或发布到结果区。"""
    if not app_prints_boxes:
        return "NOT_RUN", "PS 应用当前只在 UART 输出 frame/rc/seq，未输出框 JSON/未发布 boxes；chain-lite 需应用补充后另开卡"
    return "READY", ""


def ps_result_parse(raw: bytes) -> dict:
    """解析 PS_RESULT 64 B（与 s4d_result_t 同布局）。"""
    if len(raw) < 64:
        raise ValueError("PS_RESULT 长度不足 64 B")
    magic, version, session, frame, seq, phys, err, reject, raw_cnt, box_cnt = struct.unpack_from("<10I", raw, 0)
    return {"magic": magic, "version": version, "session_id": session, "frame_id": frame,
            "result_seq": seq, "phys_status": phys, "error_code": err,
            "last_reject": reject, "raw_candidate_count": raw_cnt, "box_count": box_cnt}


def read_exit(path: Path) -> int | None:
    """读取真实退出码文件。"""
    if not path.is_file():
        return None
    txt = path.read_text(encoding="utf-8").strip()
    return int(txt.split("=")[1]) if txt.startswith("exit=") else None


def write_exit(step: str, code: int) -> None:
    """落真实退出码。"""
    (RUN_DIR / f"{step}.exit_code.txt").write_text(f"exit={code}\n", encoding="utf-8")


def log(msg: str) -> None:
    """控制台 + 逐行日志。"""
    print(msg, flush=True)
    with (RUN_DIR / "driver_v3_console.log").open("a", encoding="utf-8") as fh:
        fh.write(msg + "\n")


# ---------------------------------------------------------------- 离线自检

def offline_selftest() -> int:
    """不碰硬件：纯函数 + 源码/桩检查。"""
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    checks: list[dict] = []

    ok, detail = region_arithmetic_ok()
    checks.append({"name": "region_arithmetic", "ok": ok, "detail": detail})
    patterns = {}
    for name in ("zeros", "ones", "aa55", "walking1"):
        data = make_pattern(name, TEST_BYTES)
        patterns[name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        checks.append({"name": f"pattern[{name}]", "ok": len(data) == TEST_BYTES, "detail": patterns[name]})
    checks.append({"name": "pattern_distinct",
                   "ok": len({v["sha256"] for v in patterns.values()}) == 4,
                   "detail": "四种图样哈希须互异"})

    d0 = bytes(64); d1 = bytes([1]) * 64; d2 = bytes([1]) * 64
    v, _ = s1_verdict([("D0", d0), ("D1", d1), ("D2", d2)])
    checks.append({"name": "s1_verdict_CHANGED_AT_PL_PROGRAM", "ok": v == "CHANGED_AT_PL_PROGRAM", "detail": v})
    v, _ = s1_verdict([("D0", d0), ("D1", d0), ("D2", d1)])
    checks.append({"name": "s1_verdict_CHANGED_AT_INIT_EXEC", "ok": v == "CHANGED_AT_INIT_EXEC", "detail": v})
    v, _ = s1_verdict([("D0", d0), ("D1", d0), ("D2", d0)])
    checks.append({"name": "s1_verdict_NEITHER_STAGE", "ok": v == "NEITHER_STAGE", "detail": v})
    v, _ = s1_verdict([("D0", d0), ("D1", d1), ("D2", bytes([2]) * 64)])
    checks.append({"name": "s1_verdict_PRE_EXISTING_CHANGE", "ok": v == "PRE_EXISTING_CHANGE", "detail": v})

    v, _ = s2_verdict({}, 0)
    checks.append({"name": "s2_pass", "ok": v == "DDR_BIT_TEST_PASS", "detail": v})
    v, _ = s2_verdict({"T2_pattern": 3}, 0)
    checks.append({"name": "s2_retention", "ok": v == "DDR_RETENTION_SUSPECTED", "detail": v})
    v, _ = s2_verdict({"T0_zeros": 1}, 0)
    checks.append({"name": "s2_bit_error", "ok": v == "DDR_BIT_ERROR_SUSPECTED", "detail": v})
    v, _ = s2_verdict({}, 5)
    checks.append({"name": "s2_restore_hard_stop", "ok": v == "HARD_STOP_RESTORE_DIFF", "detail": v})

    src = Path(__file__).read_text(encoding="utf-8")
    ok, detail = no_hardcoded_status(src)
    checks.append({"name": "no_hardcoded_status", "ok": ok, "detail": detail})
    ok, detail = order_ok()
    checks.append({"name": "stage_order", "ok": ok, "detail": detail})
    ok, detail = budget_ok()
    checks.append({"name": "time_budget_60min", "ok": ok, "detail": detail})
    ok, detail = tcl_stubs_ok()
    checks.append({"name": "tcl_stub", "ok": ok, "detail": detail})

    # S1 默认口径必须是候选区 12,615,680 B
    r_base, r_bytes, r_label = s1_region(SimpleNamespace(s1_region="candidate"))
    checks.append({"name": "s1_default_candidate_region",
                   "ok": (r_base, r_bytes, r_label) == (CAND_BASE, CAND_BYTES, "candidate")
                         and r_bytes == 12615680,
                   "detail": {"base": hex(r_base), "bytes": r_bytes, "label": r_label}})
    p_base, p_bytes, p_label = s1_region(SimpleNamespace(s1_region="probe6"))
    checks.append({"name": "s1_probe6_mode",
                   "ok": p_label == "probe6" and p_bytes == 6 * 128 and len(PROBE_ADDRS) == 6,
                   "detail": {"bytes": p_bytes, "addrs": [hex(a) for a in PROBE_ADDRS]}})
    restore_src = "S1b_restore_write" in Path(__file__).read_text(encoding="utf-8")
    checks.append({"name": "s1_candidate_restore_step_present", "ok": restore_src,
                   "detail": "恢复写 + 回读 diff 必须 0 的步骤存在于 stage_s1"})

    app_sha = sha256_file(W / "report/evidence/S4-T34/ps_decode_link_20261028_r01/s4d_ps_app_sw0.elf")
    checks.append({"name": "app_sw_sha_prefix",
                   "ok": bool(app_sha) and app_sha.startswith(APP_SW_PREFIX) and app_sha == APP_SW_SHA,
                   "detail": {"actual": app_sha, "expected_prefix": APP_SW_PREFIX}})
    checks.append({"name": "bit_identity_prefix", "ok": len(BIT_REGISTERED_PREFIX) == 8,
                   "detail": BIT_REGISTERED_PREFIX})
    st, reason = chain_lite_available(app_prints_boxes=False)
    checks.append({"name": "chain_lite_honest_NOT_RUN", "ok": st == "NOT_RUN" and bool(reason), "detail": {"status": st, "reason": reason}})

    # ---- B 段：长度前置 / D2 双分支 / dump 负面控制 ----
    v, d = s1_verdict([("D0", bytes(64)), ("D1", bytes(63)), ("D2", bytes(64))], expected_len=64)
    checks.append({"name": "s1_verdict_INVALID_LENGTH", "ok": v == "INVALID_LENGTH", "detail": d})
    v, d = s1_verdict([("D0", bytes(64)), ("D1", bytes(64)), ("D2", bytes(64))], expected_len=64)
    checks.append({"name": "s1_verdict_length_ok_NEITHER_STAGE", "ok": v == "NEITHER_STAGE", "detail": d})
    v, d = s1_verdict([("D0", bytes(64)), ("D1", bytes(64)), ("D2", bytes(64))])
    checks.append({"name": "s1_verdict_no_expected_len_legacy_ok", "ok": v == "NEITHER_STAGE", "detail": "legacy 调用不受影响"})
    s1_len_guard = "INVALID_LENGTH" in Path(__file__).read_text(encoding="utf-8")
    checks.append({"name": "s1_verdict_len_guard_present", "ok": s1_len_guard, "detail": "源码含 INVALID_LENGTH 分支"})

    t_keep = s1_tcl("D2", "d2_keep_pl", INIT_ELF)
    t_sys = s1_tcl("D2", "d2_system_reset", INIT_ELF)
    checks.append({"name": "d2_branch_keep_pl_contract",
                   "ok": ("rst -processor" in t_keep) and ("rst -system" not in t_keep)
                         and ("dow" in t_keep) and ("S1_D2_KEEP_PL" in t_keep),
                   "detail": {"no_system_reset": "rst -system" not in t_keep}})
    checks.append({"name": "d2_branch_system_reset_contract",
                   "ok": ("rst -system" in t_sys) and ("dow" in t_sys) and ("S1_D2_SYSTEM_RESET" in t_sys),
                   "detail": {"has_system_reset": "rst -system" in t_sys}})
    checks.append({"name": "d2_branches_distinct", "ok": t_keep != t_sys and "S1_D2_KEEP_PL" in t_keep,
                   "detail": "两分支 TCL 必须互异且各自有标记"})

    ok, why = dump_verdict("exit=0\nMemory read error at 0x11B00000. Cannot access DDR: the controller is held in reset", 32, 32, 0)
    checks.append({"name": "dump_nc_error_text_not_pass", "ok": (not ok) and "错误文本" in why, "detail": why})
    ok, why = dump_verdict("exit=0\n", 31, 32, 0)
    checks.append({"name": "dump_nc_short_bin_not_pass", "ok": (not ok) and "长度" in why, "detail": why})
    ok, why = dump_verdict("exit=0\n", None, 32, 0)
    checks.append({"name": "dump_nc_missing_bin_not_pass", "ok": (not ok) and "缺失" in why, "detail": why})
    ok, why = dump_verdict("exit=0\n", 32, 32, 0)
    checks.append({"name": "dump_nc_clean_pass", "ok": ok, "detail": why})
    ok, why = dump_verdict("Blocked address 0x43c00010", 32, 32, 0)
    checks.append({"name": "dump_nc_blocked_address_not_pass", "ok": not ok, "detail": why})

    tcl_s1 = s1_tcl("D0", "dump")
    checks.append({"name": "s1_tcl_read_only", "ok": "mrd" in tcl_s1 and "mwr" not in tcl_s1, "detail": tcl_s1[:120]})
    tcl_s2w = s2_tcl("write", TEST_BASE, TEST_BYTES, Path("p.bin"))
    checks.append({"name": "s2_tcl_uses_region", "ok": hex(TEST_BASE) in tcl_s2w and "mwr" in tcl_s2w,
                   "detail": tcl_s2w[:120]})
    raw = struct.pack("<10I", 0x53344452, 1, 7, 42, 3, 0, 0, 0, 2, 1) + b"\x00" * 24
    parsed = ps_result_parse(raw)
    checks.append({"name": "ps_result_parse", "ok": parsed["box_count"] == 1 and parsed["raw_candidate_count"] == 2,
                   "detail": parsed})

    # ---- v3.2 新增：INIT_ELF 缺陷回归 + load_elf_ddr 真实执行路径（mock 硬件）+ PS-PL 电平转换器 ----
    checks.append({"name": "init_elf_constant_defined",
                   "ok": isinstance(INIT_ELF, Path) and INIT_ELF.is_file(),
                   "detail": {"path": str(INIT_ELF), "exists": INIT_ELF.is_file()}})
    tcl_lvl = lvl_shifter_tcl(LVL_SHFTR_ON)
    need = ("mwr 0xf8000008 0xdf0d", "mwr 0xf8000900 0xf", "mwr 0xf8000004 0x767b", "ppl_lvl_rb")
    checks.append({"name": "lvl_shifter_tcl_exact",
                   "ok": all(k in tcl_lvl.lower() for k in need),
                   "detail": {"missing": [k for k in need if k not in tcl_lvl.lower()], "tcl": tcl_lvl[:260]}})
    checks.append({"name": "lvl_shifter_lock_key_is_0x767b_not_zero",
                   "ok": "mwr 0xf8000004 0x767b" in tcl_lvl.lower() and "mwr 0xf8000008 0x0;" not in tcl_lvl.lower(),
                   "detail": "UG585 B.28：加锁是写 0x767B 到 0xF8000004（不是写 0 到 0xF8000008）"})
    checks.append({"name": "lvl_shifter_inline_assert_readback",
                   "ok": "mrd -value 0xf8000900" in lvl_shifter_inline_assert().lower()
                         and "error" in lvl_shifter_inline_assert().lower(),
                   "detail": "装载期内联断言必须读回并在不符时 error"})
    _orig_xsdb = base.xsdb
    _orig_ensure_uart = globals().get("ensure_uart")
    _captured: dict = {}
    try:
        def _fake_xsdb(eval_text, step, timeout=600):
            _captured[step] = eval_text
            return 0

        base.xsdb = _fake_xsdb
        globals()["ensure_uart"] = lambda: None
        # (a) PL 未装载：必须用 rst -system -stop，且含 init.elf 路径与装载期 0xF 断言
        _PL_STATE["programmed"] = False
        code_a = load_elf_ddr(INIT_ELF, "SELFTEST_load_unprogrammed")
        tcl_a = _captured.get("SELFTEST_load_unprogrammed", "")
        checks.append({"name": "load_elf_ddr_runs_no_nameerror(system_reset)",
                       "ok": code_a == 0 and "rst -system -stop" in tcl_a
                             and INIT_ELF.as_posix() in tcl_a and "0xf8000900" in tcl_a.lower(),
                       "detail": {"exit": code_a, "has_system_reset": "rst -system -stop" in tcl_a,
                                  "has_init_elf": INIT_ELF.as_posix() in tcl_a,
                                  "has_lvl_assert": "0xf8000900" in tcl_a.lower()}})
        # (b) PL 已装载：必须改用 rst -processor -stop，且**不得**出现 rst -system（否则清 PL）
        _PL_STATE["programmed"] = True
        code_b = load_elf_ddr(Path("SELFTEST_app.elf"), "SELFTEST_load_programmed")
        tcl_b = _captured.get("SELFTEST_load_programmed", "")
        checks.append({"name": "load_elf_ddr_preserves_pl(rst -processor)",
                       "ok": code_b == 0 and "rst -processor -stop" in tcl_b
                             and "rst -system -stop" not in tcl_b,
                       "detail": {"exit": code_b, "processor_reset": "rst -processor -stop" in tcl_b,
                                  "no_system_reset": "rst -system -stop" not in tcl_b}})

        # (c) 读回 0xF → PASS；(d) 读回 0xA → 必须 FAIL（判别力两侧）
        # 日志按 **base.xsdb 真实形状** 造：首行是回显的整条 -eval（含标记字样），其后才是
        # `PPL_LVL_RB` 标记行 + 十进制数值行 + TCL 侧 OK/BAD 判定行（窗口 #3 实测形状）
        def _fake_xsdb_rb(dec_text: str, verdict: str = "OK", rst_dec: str = "0",
                          rst_verdict: str = "OK", echo_marker: bool = True):
            def _f(eval_text, step, timeout=600):
                RUN_DIR.mkdir(parents=True, exist_ok=True)
                echo = ('$ cmd /c xsdb.bat -eval connect -url tcp:127.0.0.1:3121; ...; '
                        'set _rb [mrd -value 0xf8000900]; puts "PPL_LVL_RB"; puts $_rb; '
                        'set _rb2 [mrd -value 0xf8000240]; puts "PPL_LVL_RB_RST"; puts $_rb2; '
                        'disconnect; exit') if echo_marker else "$ cmd /c xsdb.bat"
                body = f"{echo}\nexit=0 elapsed=0.778\nPPL_LVL_RB\n{dec_text}\n"
                if verdict:
                    body += f"PPL_LVL_RB_{verdict}\n"
                body += f"PPL_LVL_RB_RST\n{rst_dec}\n"
                if rst_verdict:
                    body += f"PPL_LVL_RB_RST_{rst_verdict}\n"
                (RUN_DIR / f"{step}.log").write_text(body + "\n", encoding="utf-8")
                return 0
            return _f

        base.xsdb = _fake_xsdb_rb("15")
        r_on = enable_ps_pl_level_shifters(LVL_SHFTR_ON, "SELFTEST_lvl_pass")
        checks.append({"name": "lvl_shifter_readback_0xF_pass", "ok": r_on["status"] == "PASS",
                       "detail": r_on})
        base.xsdb = _fake_xsdb_rb("10", verdict="BAD")
        r_bad = enable_ps_pl_level_shifters(LVL_SHFTR_ON, "SELFTEST_lvl_fail")
        checks.append({"name": "lvl_shifter_readback_0xA_must_fail", "ok": r_bad["status"] == "FAIL",
                       "detail": r_bad})
        # (e) 回归：真实日志形状（回显行含标记）必须解析到标记行之后的数值行；写 0xA 读 0xA → PASS
        base.xsdb = _fake_xsdb_rb("10")
        r_real = enable_ps_pl_level_shifters(LVL_SHFTR_CFG, "SELFTEST_lvl_cfg_real_shape")
        checks.append({"name": "lvl_shifter_parses_real_log_shape(0xA)",
                       "ok": r_real["status"] == "PASS" and r_real.get("readback") == "0xa",
                       "detail": r_real})
        # (f) 回归：回显行含标记、数值行不符 → 必须 FAIL，且 readback 必须是**数值行**的值（0xf）
        base.xsdb = _fake_xsdb_rb("15")
        r_echo = enable_ps_pl_level_shifters(LVL_SHFTR_CFG, "SELFTEST_lvl_echo_mismatch")
        checks.append({"name": "lvl_shifter_echo_line_not_misparsed",
                       "ok": r_echo["status"] == "FAIL" and r_echo.get("readback") == "0xf",
                       "detail": r_echo})
        # (g) v3.2.3：FPGA_RST_CTRL 读回 0 → PASS（另一条读回断言的正例）
        base.xsdb = _fake_xsdb_rb("15", rst_dec="0")
        r_rst_ok = enable_ps_pl_level_shifters(LVL_SHFTR_ON, "SELFTEST_rst_zero_pass")
        checks.append({"name": "fpga_rst_ctrl_zero_readback",
                       "ok": r_rst_ok["status"] == "PASS"
                             and r_rst_ok.get("fpga_rst_ctrl_readback") == "0x0",
                       "detail": r_rst_ok})
        # (h) v3.2.3：FPGA_RST_CTRL 读回非 0 → 必须 FAIL（说明仍有 FPGA 软复位被按住）
        base.xsdb = _fake_xsdb_rb("15", rst_dec="1", rst_verdict="BAD")
        r_rst_bad = enable_ps_pl_level_shifters(LVL_SHFTR_ON, "SELFTEST_rst_nonzero_fail")
        checks.append({"name": "fpga_rst_ctrl_nonzero_must_fail",
                       "ok": r_rst_bad["status"] == "FAIL"
                             and r_rst_bad.get("fpga_rst_ctrl_readback") == "0x1",
                       "detail": r_rst_bad})
        # (i) v3.2.4：日志错误文本守卫（判别力两侧：报错必抓、干净必过）
        def _fake_log(body: str):
            def _f(eval_text, step, timeout=600):
                RUN_DIR.mkdir(parents=True, exist_ok=True)
                (RUN_DIR / f"{step}.log").write_text(body, encoding="utf-8")
                return 0          # 关键：故意返回 0，模拟 xsdb 的"TCL 报错但进程码 0"
            return _f

        err_body = ('$ cmd /c xsdb.bat -eval ...\nexit=0 elapsed=0.800\n'
                    'no targets found with "name =~ "*Cortex-A9*#0*"". available targets:\n'
                    '    while executing\n"error \\"no targets found\\""\n')
        clean_body = "$ cmd /c xsdb.bat -eval ...\nexit=0 elapsed=0.500\nS1_RST_STOPPED\n"
        base.xsdb = _fake_log(err_body)
        code_e, err_e = xsdb_checked("connect; targets; disconnect; exit", "SELFTEST_guard_err")
        base.xsdb = _fake_log(clean_body)
        code_c, err_c = xsdb_checked("connect; rst -system -stop; disconnect; exit", "SELFTEST_guard_clean")
        checks.append({"name": "xsdb_error_guard_both_sides",
                       "ok": (code_e == 0 and err_e is not None and "no targets found" in err_e.lower()
                              and code_c == 0 and err_c is None),
                       "detail": {"err_side": {"exit": code_e, "error": err_e},
                                  "clean_side": {"exit": code_c, "error": err_c},
                                  "rule": "进程码 0 但日志含错误文本 ⇒ 必须判失败"}})
        # (j) 注入：load_elf_ddr 在"假成功"日志下必须返回非 0
        base.xsdb = _fake_log(err_body)
        code_ph = load_elf_ddr(INIT_ELF, "SELFTEST_load_phantom")
        checks.append({"name": "load_elf_ddr_fails_on_phantom_success", "ok": code_ph != 0,
                       "detail": {"returned": code_ph,
                                  "rule": "xsdb 进程码 0 但日志报 no targets found ⇒ 装载必须判失败"}})
        # (k) v3.2.4：DAP 恢复双条件（lead 裁决）
        ok_clean, det_clean = dap_recovered(
            "  1  APU\n  2  ARM Cortex-A9 MPCore #0\n  3  ARM Cortex-A9 MPCore #1\n  4  xc7z020\n")
        ok_apb, det_apb = dap_recovered(
            "  2  ARM Cortex-A9 MPCore #0 (APB AP transaction error, DAP status 0xF0000021)\n")
        ok_none, det_none = dap_recovered("  1  DAP (APB AP transaction error, DAP status 0x30000021)\n  2  xc7z020\n")
        checks.append({"name": "dap_recovered_requires_no_apb_error",
                       "ok": (ok_clean and not ok_apb and not ok_none),
                       "detail": {"clean_a9": det_clean, "a9_with_apb_error": det_apb,
                                  "no_a9": det_none,
                                  "rule": "必须 ①枚举到 A9#0 且 ②该行无 APB AP transaction error"}})
    finally:
        base.xsdb = _orig_xsdb
        if _orig_ensure_uart is not None:
            globals()["ensure_uart"] = _orig_ensure_uart
        _PL_STATE["programmed"] = False
        _PL_STATE["lvl_readback"] = None
    src_v32 = Path(__file__).read_text(encoding="utf-8")
    # v3.2.3：四动作顺序必须是 unlock → LVL_SHFTR_EN → FPGA_RST_CTRL → lock（与 2B ps7_post_config 一致）
    tcl_four = lvl_shifter_tcl(LVL_SHFTR_ON).lower()
    idx = [tcl_four.find(f"mwr {hex(SLCR_UNLOCK_ADDR)}"),
           tcl_four.find(f"mwr {hex(LVL_SHFTR_EN_ADDR)}"),
           tcl_four.find(f"mwr {hex(FPGA_RST_CTRL_ADDR)} 0x0"),
           tcl_four.find(f"mwr {hex(SLCR_LOCK_ADDR)}")]
    checks.append({"name": "pspl_four_actions_order",
                   "ok": all(i >= 0 for i in idx) and idx == sorted(idx),
                   "detail": {"order_index": idx,
                              "expected": ["SLCR_UNLOCK=0xDF0D", "LVL_SHFTR_EN", "FPGA_RST_CTRL=0x0",
                                           "SLCR_LOCK=0x767B"],
                              "ref": "2B verification/s2b_board_jtag.py:199-200 的四动作顺序"}})
    bad_chars = []
    for tname, tcl_txt, chars in (("lvl_shifter_tcl", lvl_shifter_tcl(LVL_SHFTR_ON), ("%", "&")),
                                  ("inline_assert", lvl_shifter_inline_assert(), ("%", "&", '"', '!'))):
        for ch in chars:
            if ch in tcl_txt:
                bad_chars.append({"tcl": tname, "char": ch})
    checks.append({"name": "pspl_tcl_no_cmd_metachars", "ok": not bad_chars,
                   "detail": {"bad": bad_chars,
                              "rule": "经 cmd /c 传给 xsdb 的 TCL 不得含 % （被当 %0 展开）、& （命令分隔符）、\" （会被再次切分）"}})
    checks.append({"name": "pspl_stage_wires_lvl_shifter",
                   "ok": "def stage_pspl_setup_and_load" in src_v32
                         and "stage_pspl_setup_and_load(args)" in src_v32
                         and "LVL_SHFTR_EN_ADDR = 0xF8000900" in src_v32,
                   "detail": "装载段必须调用新 stage 且 SLCR 地址常量为 0xF8000900"})

    fails = [c for c in checks if not c["ok"]]
    payload = {"task_id": "S4-T34", "run_id": RUN_DIR.name, "generated_utc8": now_cn(),
               "checks": checks, "fail": [c["name"] for c in fails],
               "verdict": "PASS" if not fails else "FAIL"}
    print(json.dumps({"checks": checks, "fail": payload["fail"], "verdict": payload["verdict"]},
                     ensure_ascii=False, indent=2))
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "offline_selftest.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    code = 0 if not fails else 3
    (RUN_DIR / "offline_selftest.exit_code.txt").write_text(f"exit={code}\n", encoding="utf-8")
    log(f"OFFLINE_SELFTEST_{'PASS' if not fails else 'FAIL'} ({len(checks) - len(fails)}/{len(checks)}) exit={code}")
    return code


# ---------------------------------------------------------------- 硬件分段（窗口内执行）

DUMP_ERROR_PATTERNS = ("Memory read error", "Blocked address", "Cannot access DDR",
                       "no targets found", "Memory access error", "read error")


def dump_verdict(log_text: str, file_size: int | None, nbytes: int, exit_code: int) -> tuple[bool, str]:
    """纯函数：dump 是否可信。exit0 不足以判 PASS（xsdb fail-open）。"""
    if exit_code != 0:
        return False, f"xsdb_exit={exit_code}"
    if file_size is None:
        return False, "bin 缺失"
    if file_size != nbytes:
        return False, f"bin 长度 {file_size} != {nbytes}"
    if not re.search(r"(?i)Memory (read|access) error|Blocked address|no targets found|Cannot access DDR",
                     log_text or ""):
        return True, "ok"
    return False, "日志含目标错误文本"


def _dump(tag: str, addr: int, nbytes: int, out: Path) -> int:
    """JTAG 只读 dump：退出码 + 产出文件长度 + 日志错误文本三重判定。"""
    code = base.jtag_read(addr, nbytes, out, tag)
    logp = base.RUN_DIR / f"{tag}.log"
    text = logp.read_text(encoding="utf-8", errors="replace") if logp.is_file() else ""
    ok, why = dump_verdict(text, out.stat().st_size if out.is_file() else None, nbytes, code)
    if not ok:
        log(f"[FAIL] {tag}: {why}")
        return 1
    return 0


def s1_region(args) -> tuple[int, int, str]:
    """S1 dump 口径：candidate（默认 12,615,680 B）/ test / probe6。"""
    mode = getattr(args, "s1_region", "candidate")
    if mode == "candidate":
        return CAND_BASE, CAND_BYTES, "candidate"
    if mode == "test":
        return TEST_BASE, TEST_BYTES, "test"
    if mode == "probe6":
        return 0, len(PROBE_ADDRS) * 128, "probe6"
    raise ValueError(f"未知 S1 区间 {mode}")


def probe6_dump(tag: str) -> bytes:
    """六个已知地址各取 128 B（向下 64 B 对齐一行），拼成 768 B。"""
    buf = b""
    for idx, addr in enumerate(PROBE_ADDRS):
        row = addr & ~0x3F
        out = RUN_DIR / f"{tag}_probe{idx}.bin"
        c = _dump(f"{tag}_probe{idx}", row, 128, out)
        if c != 0 or not out.is_file():
            raise RuntimeError(f"probe6 dump 失败 idx={idx}")
        buf += out.read_bytes()
    return buf


_SER: dict = {"ser": None}


def p0_gate() -> dict:
    """P0：无重型进程、3121 无 LISTENING、无 index.lock、COM4 可打开；并预开串口缓冲横幅。"""
    heavy = base.heavy_processes()
    listen = base.listening_3121()
    lock = (W / ".git" / "index.lock").exists()
    com = False
    err = ""
    try:
        import serial
        ser = serial.Serial("COM4", 115200, timeout=0.2)
        ser.reset_input_buffer()
        _SER["ser"] = ser
        com = True
    except Exception as exc:  # noqa: BLE001
        err = str(exc)
    ok = (not heavy) and listen == 0 and not lock and com
    return {"ok": ok, "heavy_processes": heavy, "listening_3121": listen,
            "index_lock": lock, "com4_present": com, "com4_error": err,
            "uart_preopened": com}


def ensure_uart():
    """确保 COM4 打开（前一段可能已 close）；重开并清缓冲。"""
    ser = _SER.get("ser")
    try:
        if ser is not None and ser.is_open:
            return ser
    except Exception:
        pass
    import serial
    ser = serial.Serial("COM4", 115200, timeout=0.2)
    ser.reset_input_buffer()
    _SER["ser"] = ser
    return ser


def uart_open_preopened():
    """返回预开串口（横幅已在缓冲中）。"""
    try:
        ser = ensure_uart()
    except Exception as exc:  # noqa: BLE001
        return None, f"COM4 不可用: {exc}"
    return ser, None


def load_elf_ddr(elf, tag, hold_reset=True):
    """先跑 init.elf 的 ps7_init 恢复 DDR，再 dow 目标 ELF；dow 后不再 rst（会把入口重置掉）。

    v3.2：`_PL_STATE["programmed"]` 为真时改用 `rst -processor -stop`——**不再 `rst -system -stop`**，
    因为系统复位会清空 PL 配置（窗口 #2 证据：复位后 `mrd 0x43C00000` 报 `Bitstream is not programmed`）；
    并在 `dow` 应用之后、`con` 之前**重新写 0xF 并读回断言**（ps7_init 可能改写 SLCR；UG585 §2.4.8）。
    """
    ensure_uart()
    reset = "rst -processor -stop; " if _PL_STATE["programmed"] else "rst -system -stop; "
    cmds = (
        "connect -url %s; %s" % (base.HW_URL, base.select_core())
        + reset
        + "dow %s; con; after 2500; " % INIT_ELF.as_posix()
        + "rst -processor -stop; dow %s; " % Path(elf).as_posix()
        + lvl_shifter_inline_assert(LVL_SHFTR_ON)
        + 'after 200; puts "HOLD_STATE=[state]"; '
        + 'con; after 2000; puts "RUN_STATE=[state]"; disconnect; exit'
    )
    code, err = xsdb_checked(cmds, tag, timeout=1200)
    if err is not None:
        (RUN_DIR / f"{tag}.xsdb_error_text.txt").write_text(err + "\n", encoding="utf-8", newline="\n")
        log(f"[FAIL] {tag}: xsdb 日志错误文本命中 ⇒ 视为失败：{err}")
        return 99 if code == 0 else code
    return code


def stage_s1(args) -> dict:
    """S1：候选区三段 dump（D0 ps7_init 后 / D1 装 PL 后 / D2 init 后）+ 快照恢复 + 恢复后 diff=0。"""
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    base_addr, nbytes, label = s1_region(args)
    dumps: list[tuple[str, bytes]] = []

    def one_dump(tag: str, name: str) -> bytes:
        if label == "probe6":
            data = probe6_dump(tag)
            (RUN_DIR / f"{name}.bin").write_bytes(data)
            write_exit(tag, 0)
            return data
        out = RUN_DIR / f"{name}.bin"
        c = _dump(tag, base_addr, nbytes, out)
        write_exit(tag, c)
        if c != 0:
            raise RuntimeError(f"{name} dump 失败 exit={c}")
        return out.read_bytes()

    try:
        code = base.xsdb(s1_tcl("D0", "reset_stop"), "S1_reset_stop")
        write_exit("S1_reset_stop", code)
        if code != 0:
            return {"status": "FAIL", "reason": "复位停止失败", "exit": code}
        # DDR 控制器复位时不可读 ⇒ D0 先跑 init.elf 的 ps7_init 再停核
        code = base.xsdb(s1_tcl("D0", "ps7_init", args.init_elf), "S1_ps7_init")
        write_exit("S1_ps7_init", code)
        if code != 0:
            return {"status": "FAIL", "reason": "ps7_init（DDR 配置）失败", "exit": code}
        dumps.append(("D0", one_dump("S1_dump_D0", "s1_D0")))
        code = base.program_pl(args.bit, BIT_REGISTERED_PREFIX)
        write_exit("S1_program_pl", code)
        if code != 0:
            return {"status": "FAIL", "reason": "PL 装载失败", "exit": code}
        dumps.append(("D1", one_dump("S1_dump_D1", "s1_D1")))
        code = base.xsdb(s1_tcl("D2", "init_con", args.init_elf), "S1_init_elf_con")
        write_exit("S1_init_elf_con", code)
        if code != 0:
            return {"status": "FAIL", "reason": "init.elf 下载/运行失败", "exit": code}
        dumps.append(("D2", one_dump("S1_dump_D2", "s1_D2")))
    except RuntimeError as exc:
        return {"status": "FAIL", "reason": str(exc)}

    verdict, detail = s1_verdict(dumps)
    detail["region"] = {"mode": label, "base": hex(CAND_BASE if label == "candidate" else base_addr),
                        "bytes": len(dumps[0][1])}
    detail["dump_sha256"] = {
        name: hashlib.sha256(data).hexdigest() for name, data in dumps}
    # 候选区现场恢复（M3 快照整区写回 → 回读 diff 必须 0 → 作为新基线）
    restore = {"status": "NOT_RUN", "reason": "未提供 --m3-reference"}
    ref = Path(args.m3_reference) if getattr(args, "m3_reference", None) else None
    if ref is not None and ref.is_file():
        ref_bytes = ref.read_bytes()
        if len(ref_bytes) != CAND_BYTES:
            return {"status": "FAIL", "reason": f"M3 快照尺寸不符：{len(ref_bytes)} != {CAND_BYTES}",
                    "verdict": verdict}
        c, err = jtag_write_checked(ref, CAND_BASE, "S1b_restore_write", CAND_BYTES // 4)
        write_exit("S1b_restore_write", c)
        if c != 0 or err is not None:
            return {"status": "FAIL",
                    "reason": f"候选区恢复写失败（立即停）；xsdb_error_text={err}", "exit": c}
        chk = RUN_DIR / "s1_post_restore.bin"
        c = _dump("S1b_post_restore_dump", CAND_BASE, CAND_BYTES, chk)
        write_exit("S1b_post_restore_dump", c)
        if c != 0:
            return {"status": "FAIL", "reason": "恢复后 dump 失败"}
        post = chk.read_bytes()
        diff = sum(x != y for x, y in zip(post, ref_bytes))
        restore = {"status": "PASS" if diff == 0 else "FAIL", "restore_diff": diff,
                   "post_restore_sha256": hashlib.sha256(post).hexdigest(),
                   "note": "整区恢复后 diff 必须 0；该 SHA 作为新基线"}
        if diff != 0:
            return {"status": "FAIL", "verdict": verdict, "reason": f"恢复后 diff={diff} ≠ 0（立即停）",
                    "restore": restore}
    return {"status": "PASS", "verdict": verdict, "detail": detail, "restore": restore,
            "note": "D0 = ps7_init 完成并停核后（DDR 可访问），非上电态；S1 段含候选区快照恢复"}


def stage_s2() -> dict:
    """S2 DDR 位测试：四种图样写读比对 + 快照恢复（恢复 diff 必须 0）。"""
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    snap = RUN_DIR / "s2_snapshot.bin"
    c = _dump("S2_snapshot", TEST_BASE, TEST_BYTES, snap)
    write_exit("S2_snapshot", c)
    if c != 0:
        return {"status": "FAIL", "reason": "快照失败", "exit": c}
    snap_bytes = snap.read_bytes()
    results: dict[str, int] = {}
    for name in ("zeros", "ones", "aa55", "walking1"):
        pat = RUN_DIR / f"s2_pattern_{name}.bin"
        pat.write_bytes(make_pattern(name, TEST_BYTES))
        c = base.xsdb(s2_tcl("write", TEST_BASE, TEST_BYTES, pat), f"S2_write_{name}")
        write_exit(f"S2_write_{name}", c)
        if c != 0:
            return {"status": "FAIL", "reason": f"写图样 {name} 失败", "exit": c}
        rb = RUN_DIR / f"s2_readback_{name}.bin"
        c = _dump(f"S2_readback_{name}", TEST_BASE, TEST_BYTES, rb)
        write_exit(f"S2_readback_{name}", c)
        if c != 0:
            return {"status": "FAIL", "reason": f"读回 {name} 失败", "exit": c}
        results[f"T0_{name}"] = sum(a != b for a, b in zip(rb.read_bytes(), make_pattern(name, TEST_BYTES)))
    last = RUN_DIR / "s2_readback_last.bin"
    c = _dump("S2_T1", TEST_BASE, TEST_BYTES, last)
    write_exit("S2_T1", c)
    results["T1_after_all"] = sum(a != b for a, b in zip(last.read_bytes(), make_pattern("walking1", TEST_BYTES)))
    time.sleep(1.0)
    late = RUN_DIR / "s2_readback_T2.bin"
    c = _dump("S2_T2", TEST_BASE, TEST_BYTES, late)
    write_exit("S2_T2", c)
    results["T2_delayed"] = sum(a != b for a, b in zip(late.read_bytes(), make_pattern("walking1", TEST_BYTES)))
    # 收尾：按快照恢复并校验 diff=0
    pat = RUN_DIR / "s2_restore.bin"
    pat.write_bytes(snap_bytes)
    c = base.xsdb(s2_tcl("write", TEST_BASE, TEST_BYTES, pat), "S2_restore_write")
    write_exit("S2_restore_write", c)
    if c != 0:
        return {"status": "FAIL", "reason": "恢复写失败（立即停，不得继续）", "exit": c}
    chk = RUN_DIR / "s2_restore_check.bin"
    c = _dump("S2_restore_check", TEST_BASE, TEST_BYTES, chk)
    write_exit("S2_restore_check", c)
    if c != 0:
        return {"status": "FAIL", "reason": "恢复校验读失败", "exit": c}
    restore_diff = sum(a != b for a, b in zip(chk.read_bytes(), snap_bytes))
    verdict, detail = s2_verdict(results, restore_diff)
    return {"status": "PASS" if verdict == "DDR_BIT_TEST_PASS" else "FAIL",  # offline-selftest 允许：判定后返回（PASS 由上文判据产生）
            "verdict": verdict, "detail": detail, "errors": results,
            "restore_diff": restore_diff,
            "stop": "恢复差异≠0 ⇒ 立即停" if restore_diff else ""}


def stage_load_app(args) -> dict:
    """P2：校验 ELF 身份 → 装载 PS 应用 → 等 UART 横幅。"""
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    app_sha = sha256_file(args.app_elf)
    gate = bool(app_sha) and app_sha.startswith(APP_SW_PREFIX)
    (RUN_DIR / "P2_app_identity.json").write_text(json.dumps(
        {"expected": APP_SW_SHA, "actual": app_sha, "prefix_ok": gate}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    if not gate:
        return {"status": "FAIL", "reason": f"ELF 身份不符：{app_sha} 不以 {APP_SW_PREFIX} 开头", "actual": app_sha}
    c = base.load_elf(args.app_elf, "P2_load_app", hold_reset=True)
    write_exit("P2_load_app", c)
    if c != 0:
        return {"status": "FAIL", "reason": "PS 应用装载失败", "exit": c}
    ser, err = base.uart_open()
    if ser is None:
        return {"status": "FAIL", "reason": f"UART 不可用：{err}"}
    try:
        line = base.uart_wait(ser, "S4D PS APP", 30)
    finally:
        try:
            ser.close()
        except Exception:
            pass
    if line is None:
        return {"status": "FAIL", "reason": "30 s 内未收到 S4D PS APP 横幅（不继续）"}
    return {"status": "PASS", "banner": line, "elf_sha256": app_sha}  # offline-selftest 允许：判定后返回（PASS 由上文判据产生）


def stage_pspl_setup_and_load(args) -> dict:
    """v3.2 的装载段：复位 → 0xA → 装 PL → 0xF+读回 → 装 init/app（装载期再断言 0xF）→ 收横幅。

    依据 UG585 v1.2 §2.4.8/§2.5/§6/Appendix B.28（见模块与 `lvl_shifter_tcl` 的引用）。
    任一步失败即返回 FAIL 并保留子步退出码；**不把读回不符当成可用**。
    """
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    out: dict = {}
    c0 = base.xsdb(s1_tcl("PPL", "reset_stop"), "PPL_reset_stop")
    out["reset_stop_exit"] = c0
    if c0 != 0:
        return {"status": "FAIL", "reason": "复位停止失败", "exit_code": c0, "detail": out}
    _PL_STATE["programmed"] = False
    a = enable_ps_pl_level_shifters(LVL_SHFTR_CFG, "PPL_lvl_0xA_cfg")
    out["lvl_0xA"] = a
    if a["status"] != "PASS":
        return {"status": "FAIL", "reason": "配置期 LVL_SHFTR_EN=0xA 写入/读回失败", "exit_code": 1, "detail": out}
    cp = base.program_pl(Path(args.bit), BIT_REGISTERED_PREFIX)
    out["program_pl_exit"] = cp
    if cp != 0:
        return {"status": "FAIL", "reason": "PL 装载失败", "exit_code": cp, "detail": out}
    _PL_STATE["programmed"] = True
    f = enable_ps_pl_level_shifters(LVL_SHFTR_ON, "PPL_lvl_0xF_after_cfg")
    out["lvl_0xF"] = f
    if f["status"] != "PASS":
        return {"status": "FAIL", "reason": "配置后 LVL_SHFTR_EN=0xF 写入/读回失败", "exit_code": 1, "detail": out}
    app = stage_load_app(args)
    out["app_load"] = app
    status = "PASS" if app.get("status") == "PASS" else "FAIL"
    return {"status": status, "exit_code": 0 if status == "PASS" else 1, "detail": out,
            "note": "装载段已内联重断言 PS-PL 电平转换器（读回必须 0xF）"}


def stage_chain_lite(args, app_prints_boxes: bool = False) -> dict:
    """S3：可选 chain-lite；应用未输出框 JSON 时如实 NOT_RUN。"""
    st, reason = chain_lite_available(app_prints_boxes)
    if st == "NOT_RUN":
        return {"status": "NOT_RUN", "reason": reason}
    # 预留实现位：应用补充框 JSON 后在此接入（当前不可达，避免伪实现）
    return {"status": "NOT_RUN", "reason": "chain-lite 接入点未实现（离线未启用）"}


def main() -> int:
    """入口：离线自检或窗口执行。"""
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline-selftest", action="store_true")
    ap.add_argument("--s1-region", choices=("candidate", "test", "probe6"), default="candidate")
    ap.add_argument("--window", action="store_true")
    ap.add_argument("--bit", type=Path)
    ap.add_argument("--init-elf", type=Path)
    ap.add_argument("--app-elf", type=Path)
    ap.add_argument("--m4b-elf", type=Path)
    ap.add_argument("--m4b-input", type=Path)
    ap.add_argument("--m4b-weights", type=Path)
    ap.add_argument("--m4b-head13", type=Path)
    ap.add_argument("--m4b-head26", type=Path)
    ap.add_argument("--m3-reference", type=Path)
    ap.add_argument("--chain-lite", action="store_true")
    args = ap.parse_args()

    if args.offline_selftest:
        return offline_selftest()
    if not args.window:
        print("需要 --offline-selftest 或 --window")
        return 2
    for name in ("bit", "init_elf", "app_elf", "m4b_elf", "m4b_input", "m4b_weights",
                 "m4b_head13", "m4b_head26", "m3_reference"):
        p = getattr(args, name)
        if p is None or not Path(p).is_file():
            print(f"[FAIL] 缺输入 {name}：{p}")
            return 2

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    base.RUN_DIR = RUN_DIR
    results: dict = {"task_id": "S4-T34", "run_id": RUN_DIR.name, "started_utc8": now_cn(),
                     "stage_order": STAGE_ORDER, "budget_min": BUDGET_MIN,
                     "steps": {}, "stop_reason": None, "boundary": "离线文档就绪；未上板；ENABLE=0；不主张 G3/G4/G5"}
    hw_pid = None
    try:
        # 窗口补丁：P0 的 COM4 实开判定、UART 预开生命周期、装载保留 DDR
        base.uart_open = uart_open_preopened
        base.load_elf = load_elf_ddr
        p0 = p0_gate()
        results["P0_gate"] = p0
        (RUN_DIR / "P0_gate.json").write_text(json.dumps(p0, ensure_ascii=False, indent=2) + "\n",
                                              encoding="utf-8", newline="\n")
        if not p0["ok"]:
            results["stop_reason"] = "P0 门禁未通过"
        else:
            srv = base.start_hw_server()
            hw_pid = srv.get("pid")
            if not srv["ok"]:
                results["stop_reason"] = "hw_server 未就绪"
        if results["stop_reason"] is None:
            s1 = stage_s1(args)
            results["steps"]["S1_bisect"] = s1
            if s1["status"] != "PASS":
                results["stop_reason"] = f"S1 bisect {s1['status']}"
        if results["stop_reason"] is None:
            s2 = stage_s2()
            results["steps"]["S2_ddr_bit_test"] = s2
            if s2["status"] != "PASS":
                results["stop_reason"] = f"S2 {s2.get('verdict', 'FAIL')}"
        if results["stop_reason"] is None:
            p2 = stage_pspl_setup_and_load(args)
            results["steps"]["P2_load_app"] = p2
            if p2["status"] != "PASS":
                results["stop_reason"] = "PS 应用装载/横幅失败（含 PS-PL 电平转换器使能）"
        m4_args = SimpleNamespace(m4b_elf=args.m4b_elf, m4b_input=args.m4b_input,
                                  m4b_weights=args.m4b_weights, m4b_head13=args.m4b_head13,
                                  m4b_head26=args.m4b_head26, skip_m4b=False)
        if results["stop_reason"] is None:
            m4b = base.step_m4b(m4_args)
            results["steps"]["M4b_dma_visibility"] = m4b
            if m4b["status"] != "PASS":
                results["stop_reason"] = f"M4-b {m4b['status']}"
        if results["stop_reason"] is None:
            m4a = base.step_m4a()
            results["steps"]["M4a_cache_visibility"] = m4a
            if m4a["status"] != "PASS":
                results["stop_reason"] = "M4-a 失败"
        if results["stop_reason"] is None:
            m3 = base.step_m3_recheck(args.m3_reference)
            results["steps"]["M3_recheck"] = m3
            if m3["status"] != "PASS":
                results["stop_reason"] = "M3 复检不通过（差异≠0 ⇒ 立即停）"
        if results["stop_reason"] is None:
            results["steps"]["S3_chain_lite"] = stage_chain_lite(args, app_prints_boxes=args.chain_lite)
    finally:
        ser = _SER.get("ser")
        if ser is not None:
            try:
                ser.close()
            except Exception:  # noqa: BLE001
                pass
        teardown = base.stop_hw_server(hw_pid) if hw_pid else {"stopped_pid": None, "listening_3121": base.listening_3121(),
                                                              "residual_processes": base.heavy_processes()}
        results["steps"]["P4_teardown"] = {"status": "PASS" if teardown["listening_3121"] == 0 and not teardown.get("residual_processes") else "FAIL",  # offline-selftest 允许：判定后返回（PASS 由上文判据产生）
                                           "detail": teardown}
        results["finished_utc8"] = now_cn()
        ok_steps = all(v.get("status") in ("PASS", "NOT_RUN") for v in results["steps"].values())
        results["conclusion"] = ("BRINGUP_ALL_PASS_OR_NOT_RUN" if results["stop_reason"] is None and ok_steps
                                 else "STOPPED_ON_FAILURE")
        (RUN_DIR / "results_bringup_v3.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n",
                                                         encoding="utf-8", newline="\n")
        log(json.dumps({"conclusion": results["conclusion"], "stop_reason": results["stop_reason"],
                        "steps": {k: v.get("status") for k, v in results["steps"].items()}}, ensure_ascii=False))
    return 0 if results["conclusion"].startswith("BRINGUP_ALL") else 1


if __name__ == "__main__":
    sys.exit(main())