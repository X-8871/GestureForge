# 阶段3 板级单次窗口（2026-10-24，RunId `t05_stage3_window_20261024_r01`）

- 执行方：**DSH 阶段3 总控（stage3-lead）＝ `dbdf` 唯一写入方**；在 `dbdf` 内运行（执行器 cwd 护栏）。
- 授权：Wong 2026-10-24「1.可开工」（决策记录 `report/evidence/CTRL-DSH-HANDOFF/decisions/stage_3_4_direction_20261024_r01.md`
  sha256 `907084cd…`）；跨方通报 `DSH-20261024-004`（sha256 `b820fcd1…`）；Codex 不争用 `CDX-20261023-018` §3.1（sha256 `9360ae1b…`）。
  工具门禁文件：`report/evidence/S3-T17/hw_authorization.json`（本窗口写，`wong_go=true`、`codex_hw_release=true`）。
- 范围（单次、串行）：① ≥30 分钟实时耐久；② VDMA 粘滞 `0x00015810` 核对；③ 参考帧集采集（供阶段4 回放）。
  **不含**：阶段4/5/6 板级、QSPI 烧录、改接线/电气测量、J10 通道（Wong 2026-10-24 范围排除）。
- 部署身份（开窗实测，全部与记录一致）：bit `7cb33068…`（无补偿 SOF）、XSA `1f5b138e…`、`an5642_j11cmos2_v10_read.elf` `1457cda4…`、
  冻结用 `v11_freeze` `c01133b1…`；见 `window_open_prestate.json`。

## 1. 开窗现场
- 开窗时刻（UTC+8）：2026-10-24 00:35:00（`window_open_prestate.json` 的 `window_start_utc8`）与产物身份哈希。
- 开窗前进程/端口/COM：**无** `vivado`/`xsdb`/`hw_server` 进程、**3121 无监听**、COM4 未打开。
  **口径更正（评审 B-4）**：`window_open_prestate.json` **不含**进程/端口/COM 字段；上述三项来自**当时控制台核对的逐字转录**
  `window_open_machine_snapshot.txt`（**transcript，非机器可读探针**，当时未落盘）；如需机器可读，须在下一次窗口按同命令落盘。
- 只做易失性 JTAG 下载（PS_RESET → FPGA_PROGRAM → PS7_INIT → DOW → RUN）；不烧 QSPI、不改接线。

## 2. 三项结果

### 2.1 ≥30 分钟实时耐久 —— **达成**
- 循环脚本：`endurance_loop.sh`（本目录副本；每 300 s 一轮「只读探测 + 活写标记」，共 7 轮）。
- **起止：`00:49:16 → 01:20:31`（31 min 15 s）**；7 轮时间戳 00:49:16 / 00:54:29 / 00:59:38 / 01:04:49 / 01:10:00 / 01:15:09 / 01:20:20。
- **每轮 `OVERWRITTEN=5/5`**（DMA 连续写帧）；每轮 `CR=0x00010003`、`ADDR_S2MM=0x00110C00`、`MM2S_SR=0x00011000`、`READ_n_EXIT=0`、`PROBE_n_EXIT=0`：原始 `endurance_probes.txt`。
- UART 连续抓取 **00:35:01 → 01:10:01（35 min）**：`uart_window_20261024_003501-011001.log`
  （**提交内**产物，文件名带抓取起止；含三路 CHIPID `0x5640`、`0x503D=0x00`、5 次采样 × 3 站点指纹全部相异）。
  **入库例外（评审 B-1）**：该文件被 `.gitignore:20 *.log` 命中，故以 `git add -f` 显式入库；manifest 中已登记该例外。
- 判据满足：标记全部被覆盖 + 时间跨度 ≥30 分钟 + 无停止/复位/死锁事件（全程无异常输出）。
- 限制：本项为**机读连续性与活动性**证据；"连续画面"的目视确认属 Wong 端（未做，见未关闭项）。

### 2.2 VDMA 粘滞 `0x00015810` —— **PARTIAL（不宣布关闭）**
- **启动阶段值（口径更正，评审 N-4）**：应用 `phase=0` 时 **`0x00014810`**（帧计数类 IRQ 位尚未置位），
  **t=5 s 起为 `0x00015810`**；窗口**清除所用值 = `0x00015810`**（下载后、未清时只读探测所读值）。
  其余同批读数：`CR=0x00010003`、`VSIZE=0x2D0`、`HSIZE=STRIDE=0xF00`、`ADDR=0x00110C00`、`MM2S_SR=0x00011000`；**两次独立启动均复现**。
- **位解释**：应用自身 `S3_DIAG5_SR_DECODE` = `INT(0x10)+FSZ_MORE(0x800)+ERR_IRQ(0x4000)`（+帧计数状态位）；未新造位名。
- **一次性清除**：`mwr -force 0x43010034 0x00015810`（W1C，沿用既有范式）⇒ `0x00015810 → 0x00011000`（清掉 `0x4810` 三个错误位，残留为状态位）。
- **运行增量**：清除后 **31 分钟 7 次回读，SR 恒为 `0x00011000`** ⇒ 错误位**未复现**；全程 `HALTED=0/IDLE=0`、标记 5/5、显示无错误 ⇒ **未观测到功能影响**。
- **判定：PARTIAL** —— 无根因解释（`FSZ_MORE` 触发源未定位），故**不关闭、不称"零错误"**；后续建议见 `vdma_sticky_result.md` §5。

### 2.3 参考帧集（供阶段4 回放）—— **达成**
- 方法：下载 `v11_freeze`（t≈20 s 停 S2MM 并保持 240 s）⇒ `jtag_t17_dump_rows.tcl <空目录> <base> <stride> 100 400 600 --frame`
  一次导出 3 行 + 整帧；base/stride **取 v11 自身 UART 打印**（`FB=0x00114C00`、`STRIDE=0x00000F00`）并与寄存器回读核对。
- 产物：`frame_full.bin`（2,764,800 B，sha256 `939fce22…`）+ `row_y100/400/600.bin`（3,840 B 各一，哈希见 `reference_frame_set.md`）。
- 内容自检：**0 个全零行**、通道均值 B/G/R=94.1/86.2/93.5、最大值 248/252/248 ⇒ 真实彩色场景。
- 教训（保留失败证据，**归因按自身日志更正，评审 N-2**）：首次转储（`dump_frameset.stdout.txt`）时，
  **S2MM 处于未配置/已停状态**——同批寄存器回读为 `FRAME0/STRIDE/HSIZE/VSIZE = 0x00000000`、`SR=0x00014811`（含 `Halted`），
  ⇒ 所读 `0x00110C00` **并非活动帧缓冲**，故 715/720 行全零。**同时** v11 冻结应用的活动 FB 实为 `0x00114C00`（其 UART 自报），
  即「转储时无活动帧缓冲」为主因、「帧缓冲地址随应用运行期分配、不可跨应用套用」为并存事实；按 v11 自报 FB 重做后成功。

## 3. 收窗 —— **已完成**
- 收窗记录：`window_close.txt`（起止、部署身份、板上最终状态、服务/端口收尾、异常与自我更正、未关闭项）。
- 板上最终状态：**实时彩色在流**（`S2MM_CR=0x00010003`、`ADDR_S2MM=0x00110C00`、`MM2S_SR=0x00011000`、`MM2S 帧地址=0x00110C00`、01:26:49 标记 5/5）。
- 服务收尾：收窗时**无 `hw_server`/`xsdb`/Vivado/vitis 残留**，**3121 无监听**；未结束其他窗口任何进程/服务（窗口期本机另有 w5 离线测试进程，未触碰）。

## 3.1 窗口内新增的只读工具（本目录/仓库）
- `scripts/stage3_t05/jtag_liveness_marker.tcl`（活写标记，无寄存器写）
- `scripts/stage3_t05/jtag_s2mm_sr_clear.tcl`（**一次性** W1C 清 SR，记录前后值）
- `scripts/stage3_t05/jtag_addr_map_read.tcl`、`jtag_addr_scan.tcl`、`jtag_addr_scan_mm2s.tcl`（只读地址事实）
- 结果：`address_facts.md`（含"采集与显示**共用**同一帧缓冲 `0x00110C00`"的实测结论）。

## 4. 边界
- 本记录**不代表**阶段3 G5、G3/G4 或独立审查通过；颜色项仅按 015 r03 标签 `PASS_VERIFIED_NEW_MODULE`。
- 本窗口只覆盖阶段3；阶段4 板级按 `CDX-20261023-019` 暂缓。