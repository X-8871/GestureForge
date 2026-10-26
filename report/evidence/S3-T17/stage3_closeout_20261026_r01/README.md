# 阶段3 收尾判定与冻结（2026-10-26）

- RunId：`stage3_closeout_20261026_r01`；工作树/分支：`D:\codex-worktrees\dbdf` / `codex/stage3-video`
- 授权：Wong 2026-10-26「都可以」（接受两项残留为记录性局限 + 含下载窗口）与「交给你来做」（委托完成真彩判据与收尾）
- 判定：**阶段3 收尾通过（带记录性局限）**

## 1. 逐条对照（验收计划「阶段3：摄像头视频链路」）

| 要求 | 状态 | 证据 |
|---|---|---|
| HDMI 摄像头→已确认输入→FPGA→HDMI→显示器；不支持则记录差距并由用户确认替代接口 | **满足**（通道差异已记录：本版为 **AN5642/OV5640 → J11 扩展口 → PL 采集/DDR → HDMI**，非 HDMI 摄像头；该替代由 Wong 方向确认） | 交付基线 + `t05_v6_board_…`/`t05_monitor_…`；本 RunId；AGENTS 接口差异条款 |
| 原始画面：分辨率 | **满足** 1280×720（运行期 `VSIZE=0x02D0`/`HSIZE=0x0F00`） | `t17_g3_reconfirm_20261026_r02/register_probe.txt` |
| 像素格式 | **满足** RGB565（`0x4300=0x60`）+ 内存序 B,G,R + 每行 3840 B | UART `S3_DIAG5_SENS`、`…/rows/`、`reference_frame_set.md` |
| 帧/行边界 | **满足**（厂商 IP `s_axis_tuser` 改为 hblank 连续低 ≥16384 pclk 后首个有效像素；`GAP_THRESH=16384`，HTS=1892/VTS=740 ⇒ 612<16384<38452） | `alinx_ov5640_sof_hrefgap.patch` `fd854a62…`、`t05_sof_fix_20261020_r01` |
| 帧率 | **记录性局限**：未仪器测量帧率/PCLK（仅链路配置与活性证据）；不得编造数值 | `t05_timing17_nominal_pclk_reaudit_20261026_r02/`（名义 84 MHz 未仪器测量） |
| ≥30 分钟无输入/显示死锁 | **满足** 31 min 15 s、7 轮、活写标记 5/5、无停止/复位/死锁 | `t05_stage3_window_20261024_r01/` |
| 像素计数与配置对应 | **满足**（帧 2,764,800 B = 720×3840；`ADDR`/`STRIDE`/`HSIZE`/`VSIZE` 运行期回读一致；采集与显示同址 `0x00110C00`） | 本 RunId `register_probe.txt`、`rows_dump.txt` |
| 测试图案/运动场景检查花屏、撕裂、停帧 | **满足**：彩条满量程且色相顺序正确（白 `B5=31`、绿 `G6=63`；本轮与 2026-10-23 同型）；实景目视「画面可以接受，正常颜色」；未观察到花屏/撕裂/停帧（早前导出撕裂系**读取方法**造成，已记录更正） | `…/bars_frame/bars_g3.png`、`t05_new_module_reverify_20261023_r01/`、`decisions/stage3_human_visual_20261024_r01.md` |
| 证据：接口来源、配置、帧/像素计数、连续日志和视频 | **满足（带局限）**：接口/配置/计数/连续日志（UART 35 min）齐备；**未录制连续视频**（以连续日志 + 帧转储 + 人工目视替代） | 各 RunId；`t05_stage3_window_20261024_r01/uart_window_*.log` |

## 2. 当前部署 G3 重确认（本轮完成）

- **下载**：`T05_DOWNLOAD_EXIT=0`；bit `7cb33068…`（1,668,969 B）、XSA `1f5b138e…`（633,089 B）、ELF `1457cda4…`（306,272 B），本地实算哈希与记录一致。
- **身份/配置/地址**：UART `ADDR=0x00110C00`、`S3_DIAG9_PAD` 一致、`CHIPID 三路 0x5640`；`ADDR_S2MM=ADDR_MM2S=0x00110C00`、`STRIDE=HSIZE=0x0F00`、`VSIZE=0x02D0`、`CR_S2MM=0x00018003`、`MM2S_SR=0x00011000`；`SR_S2MM=0x00015810`（启动瞬态第 3 次独立复现）。
- **真彩判据（本轮完成）**：既定彩条用例（写前回读、写后校验 `readback=0x80`），8 段满量程且顺序正确 ⇒ **真彩在位、无缺位**；随后恢复部署应用（`0x503D` 由 init 写回；`ADDR=0x00110C00`、帧指纹 t=5/25 互异 ⇒ 实时）。
- **人工目视**：2026-10-24 01:41 Wong「画面可以接受，正常颜色」——**本版位流/ELF/端口/接线未变更**，该判定对本部署仍有效；本轮另以已知彩条机器判据复证。

## 3. 冻结基线（可恢复）

| 项 | 值 |
|---|---|
| 冻结提交 | 见 `manifest.json` 的 `freeze_commit`（本记录所在提交） |
| 位流 / XSA / 应用 | `7cb33068…`（1,668,969 B）/ `1f5b138e…`（633,089 B）/ `an5642_j11cmos2_v10_read.elf` `1457cda4…`（306,272 B） |
| 约束 / 补丁 | `an5642_j11_cmos2.xdc` `2dae928c…` / `alinx_ov5640_sof_hrefgap.patch` `fd854a62…` |
| 本地附注 tag | `stage3-close-20261026`（**不 push**） |
| 恢复入口 | `bash scripts/stage3_t05/run_t05_board_capture.sh tmp/s3r06/t04_sof_fix_20261020_r01 tmp/s3r06/t04_j11cmos2_elf_v10/elf_build/app/an5642_j11cmos2_v10_read.elf <tag> 70`（下载即恢复；随后按第 2 节核对身份/地址） |

## 4. 记录性局限（均已由 Wong 明确接受或有据备案）

1. **VDMA 首帧 bit11 根因**：`PARTIAL/OPEN`——仅定位到启动即 `0x14810`、t=5 s 新增 bit12，第 3 次独立复现；无 AXI-Stream 握手观测、无 ILA；功能无影响、31 min 稳态无复现。清除条件：启动阶段采集 reset/配置/`CR.RS`/VSIZE 与首帧 `TVALID/TUSER/TLAST/TREADY` 对齐。
2. **task-11 完整 SEC 等价**：`BLOCKED_NOT_RUN`（本机无适用引擎/license，且源/primitive/INIT-GSR 绑定缺项）；静态阈值译码与局部转移已 PASS；不得安装工具。
3. **TIMING-17 / I/O delay（C2/I1–I3）**：Wong 2026-10-24 备案为「已记录局限」，未宣称验证；隔离实验证明 TIMING-36/30 可消除，但**正式工程源未改**。
4. **帧率/PCLK 未仪器测量**；**未录制连续视频**；**无 ILA**（BASIC 许可禁 debug core，不免除功能/时序/耐久标准）。
5. G2：完整 G2 证据审查已独立 `PASS`（基线 `78f2bde`）；早期 stdluma/gray 补丁仅人工审阅（若重启须复审）。

## 5. 未做项与边界

未烧 QSPI、未改接线、未做电气测量；v14 诊断候选**仍未审查成包、不得部署**；本轮所有板级动作均为易失（下载 + 只读回读 + 既定彩条用例并已恢复）。本记录不代表阶段4/5/6 任何结论。