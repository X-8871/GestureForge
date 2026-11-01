# 今晚结论交接 · R-07 真实相机接入（2026-10-31）

> 范围：阶段5 `S5-T01` + `R-07` 相机链路（PL 侧）。写入方：video-bd（DSH BD 子代理）。板级执行：board-runner/video-sw。
> 工作目录：`D:\tmp\lead\p3r_camera_20261031_r01\`（工程 `s4d_p3r_r01`，BD `s4d_p3r`）。详细技术过程见 `P3R_REPORT.md` §15–§22。
> 约束：全程**离线构建**，未做 git 提交、未改其他 run 目录。

## 1. 今晚目标与最终状态

- **目标**：让真实 OV5640 经 `DVP → (RGB565→RGB888) → VDMA S2MM` 真正写满 DDR 一帧（921,600 B，stride 1920）。
- **最终状态**：**未通**。
- **一句话卡点**：`axi_vdma_1`（S2MM-only）的 **`S2MM_CR` 的 RESET 位（bit2）无法清除**，导致 `XAxiVdma_CfgInitialize` 的"读通道复位"轮询超时；而**时钟与复位输入已逐项实测正常**，故判定为 **VDMA IP 实例自身异常**，正在用 build11g 验证"重建实例 + 三路时钟同域"。

## 2. 已确认打通的部分（带证据）

| 能力 | 证据 |
|---|---|
| SCCB 手动位操作通道可用，读到 CHIPID `0x5640` | build7/build8 产物 + 板级窗口（§17，R-17） |
| 302 项完整寄存器表 + 覆盖表（写入/回读一致） | `P3R_REPORT.md` §17 + 板级窗口回读记录 |
| sensor 真实出流：**15.0–15.2 fps**、**1,228,800 px/frame**、PCLK **84 MHz** | 板级窗口 r37/r38（PL 侧计数器 `0x43C90000/0x43CA0000`） |
| 厂商 IP 的 `m_axis` 侧 beat 定量 **27.6M beat/s** | 板级窗口 r41（lead 记录口径） |
| 阶段3 对照实验：同板同 sensor **今天仍能出图/写 DDR** | 阶段3 冻结 XSA `1f5b138e…` 复测 |
| 显示链路不受影响：fps=60、VDMA `vdma_0` 正常 | 全程各窗口 |
| 相机链的 BD 结构、地址、位宽与阶段3 逐项一致 | `P3R_REPORT.md` §3/§4/§5 + `out/build11f/s4d_p3r_r01.xsa` 的 `.hwh` |

## 3. 已排除的假设清单（每条一句 + 证据）

1. **SCCB 驱动不可用（PS7 EMIO I2C0）** —— 排除：手动 `gpio_sccb` 位操作已读到 `0x5640`（R-17；build7/8）。
2. **sensor 未正确配置** —— 排除：302 项表回读全对，且出流 15 fps、像素计数正确（r37/r38）。
3. **FSYNC 语义错（`c_use_s2mm_fsync=2` 需 tuser）** —— 排除：build11a 改 0（free-run）后 `SR` 变干净（`0x10000`），但**仍零 beat**。
4. **`tuser`(SOF) 未接到 VDMA** —— 排除：build10b2 已三成员网接回，仍零 beat。
5. **寄存器映射/写序错** —— 排除：r51 用**官方驱动** `XAxiVdma_CfgInitialize` 同样失败（返回 1、复位轮询超时）；且 `0xA0/A4/A8/AC` 可写可回读。
6. **CR 写入顺序/位选错** —— 排除：r48 写 `0/1/8` 读回恒含 bit2；r51 官方驱动 `CR=0x10006` 同样 RESET 置位。
7. **复位电平未释放** —— 排除：r50/r51 实测 `0x43D40000+0x00 = 0x3`（`rst_100` 与 `rst_all` 均为 1）。
8. **三路时钟未在动 / FCLK1 未使能** —— 排除：r51 实测 FCLK0 **50.0 MHz**、FCLK1 **100.3 MHz**；`.hwh` 中 `PCW_FPGA1_PERIPHERAL_FREQMHZ=100`、`PCW_FPGA_FCLK1_ENABLE=1`。
9. **官方驱动路径能绕过** —— 排除：r51 `CfgInitialize=1`（"Read channel reset failed" 超时）、`DmaStart=9`。
10. **厂商 IP 有 `s_axis_*` 输入端口未接** —— 排除：IP 仅 12 个端口，`s_axis_*` 全为内部信号（`alinx_ov5640.v` 端口列表实证）。
11. **VDMA `*_prmry_resetn` 悬空被 tie 0** —— 排除：`axi_vdma_1` 仅有 `axi_resetn` 一个复位端口（hwh 实测），且已连接。
12. **`C_PRMY_IS_ACLK_ASYNC` 未置位** —— 排除：该参数在本 IP 上**不存在**（`get_property` 读回空）。
13. **HREF/VSYNC 极性错** —— 排除：r40 四种极性（`0x4740=0x20/0x21/0x22/0x23`）全部 `dIP_TVALID=0`、`dBEAT=0`。
14. **`c_s2mm_sof_enable=1` 与 free-run 冲突** —— 排除：build11c 关掉后仍 `CR=0x10004`、零 beat。
15. **`axi_resetn` 复位域不匹配** —— 已改（build11e 改接 `rst_100`），无改善；r50 证明两路复位本就已释放。

## 4. build 清单（build2 → build11g）

| build | 用途/关键改动 | bit sha256（前 16 位全文见 §14） | XSA |ledge 结果 |
|---|---|---|---|---|
| build2（`out/`） | 基线（含相机链、显示链） | `6202872e5958ee38…` | `7b26a487…` | 出图正常；DDR 512 MiB |
| build3 | 相机链结构对齐阶段3 | `648f31567e0a2091…` | `1284f637…` | 可下板 |
| build4 | 修 PS7 UART 时钟缺失 + `cmos_rst` 默认值 | `e86efef68a55389c…` | `d2d2447c…` | UART 可用 |
| build5 | **DDR 512 MiB → 1 GiB**（真根因修复） | `da89789ba9f57db6…` | `3e8d56e2…` | DDR 可写满帧 |
| build6 | I2C0 EMIO 对齐（2 项被 IP 忽略） | `767fb7361d916a68…` | `8151fd0d…` | 无效，转手动 SCCB |
| build7 | `gpio_sccb` 手动 SCCB 测试通道 | `3ae13e42f19f9d08…` | `55194a75…` | 读到 CHIPID `0x5640` |
| build8 | SCCB 默认 `mode=1` + 8-bit 电平 | `7acea72617024db9…` | `07728bd2…` | SCCB 稳定 |
| build9 | 相机输入计数器（PCLK/HREF/VSYNC） | `25310a64545255bc…` | `5a00d969…` | **WNS −5.161**（假 CDC），下板计数正确 |
| build9b | 补 `p3r_cdc_b9.xdc`（cam_pclk→clk_100 灰码） | `9b6fb9bc9c378c11…` | `d4dc8b97…` | WNS +0.269 |
| build10 | 拆分 tdata 为标量（**失败废弃**） | — | — | `[BD 41-2383]` 宽度降级 |
| build10b | tdata 保留接口 + 1-bit 信号 tap | `44bc86ed4657d914…` | `314289913d…` | WNS +0.313 |
| build10b2 | **`tuser` 三成员网接回 VDMA** | 同 build10b（bit 相同） | 同 build10b | 零 beat |
| build11a | `c_use_s2mm_fsync=2 → 0`（free-run） | `378521254047ef4a…` | `8e72c826…` | `SR` 变干净，仍零 beat |
| build11b | IP 输出侧 4 计数器（0x43CE/0x43CF） | `ba0f7009a29c651f…` | `c3866d95…` | 定位 tready 高/tvalid≈0 |
| build11c | `c_s2mm_sof_enable=0`、`c_flush_on_fsync=0` | `50e974144dbfc48b…` | `59a59ffe…` | 仍 `CR=0x10004` |
| build11d | 厂商 IP 源码副本 + 内部探针（**废弃**） | — | — | r48 给出更直接根因后主动停止 |
| build11e | VDMA `axi_resetn` 改接 `rst_100`(100 MHz 域) | `c74a1fd44a71e4a8…` | `a03ec976…` | 仍 `CR=0x10004` |
| build11f | 时钟/复位电平观测（0x43D4/0x43D5） | `4ae379a9aa2dd4ca…` | `46dfdf7e…` | r50/r51 证明复位/时钟均正常 |
| **build11g** | **全新实例 `axi_vdma_cam` + 三路 aclk 全 100 MHz + `axi_clock_converter`** | **构建中（见 §7）** | — | 待 r52 |

## 5. 软件 ELF 清单（v1 → v29d）

> ⚠️ **本项不在 video-bd 记录范围内**（ELF 由 `video-sw`/lead 维护）。今晚已知：
> - **v27e**：`8fd0ef8ee7cf77f1d97d6465ed2ae39cfc216945f4f71269bb45fbf80120af12`（r50 用）
> - **v29d**：官方驱动路径（`XAxiVdma_CfgInitialize` 判据，r51 用）
> - 其余版本请从 `video-sw` 的构建记录补齐后并入本文档。

## 6. 板级窗口清单（r19 → r52）

| 窗口 | 一句话结论 | 证据入口 |
|---|---|---|
| r37/r38 | sensor 真实出流 15.0–15.2 fps、1,228,800 px/frame、PCLK 84 MHz | `ecam_diag_*` 对应 RunId + PL 计数器 |
| r39 | VDMA CR 运行、`SR=0x10000` 干净，但 beat 不落 DDR | 同上 |
| r40 | 四种 HREF/VSYNC 极性全 `dIP_TVALID=0` ⇒ 极性排除 | 同上 |
| r41 | IP `m_axis` beat 定量 27.6M/s（lead 口径） | 同上 |
| r48 | **写 `S2MM_CR` 的 `0/1/8` 均读回含 bit2（RESET）** ⇒ 通道被按在复位 | 同上 |
| r49/r49a | build11e 后仍 `CR=0x10004`；但 `SR` 变干净（FSYNC=0 生效） | 同上 |
| r50 | `RST_100=0x3`、FCLK0=50.0M、FCLK1=100.3M ⇒ 复位/时钟**正常** | 同上 |
| r51 | **官方驱动 `CfgInitialize=1`（复位轮询超时）、`CR=0x10006`** | 同上 |
| r52 | build11g（全新实例 + 三路同域）——**待跑** | 待生成 |

> 说明：r19–r36 属早期窗口（UART/DDR/SCCB 阶段），其结论已固化到 §15–§17 与上表 build 清单，明细以 lead 的窗口台账为准。

## 7. 当前唯一未解问题（交接核心）

**现象**：`XAxiVdma` 的 S2MM 通道 `CR.RESET`（bit2）无法清除 ⇒ 驱动 `CfgInitialize` 复位轮询超时（r51 返回 1 / `DmaStart=9`）；手写寄存器同样无效（r48）。

**已确认正常**：`axi_resetn=1`、`s_axi_lite_aclk`(50M)/`s_axis_s2mm_aclk`(100M)/`m_axi_s2mm_aclk`(100M) 均在动、FCLK0/1 频率正确、`.hwh` 中 FCLK1 使能、AXI-Lite 寄存器可读可写。

**正在验证（build11g）**：① 用**全新实例名** `axi_vdma_cam` 重新生成（排除旧 XCI/缓存异常）；② **三路 aclk 全部 = FCLK1(100 MHz)**（AXI-Lite 经 `axi_clock_converter` 从 50→100）；③ `axi_resetn = rst_100`；④ 新增 `0x43D60000`（`+0x00`=`axi_resetn` 电平、`+0x08`=`s_axi_lite_aclk` 计数）。

**r52 成功判据**：`0x43D60000+0x00` bit0=1 → `CfgInitialize=0` → `CR` 写 1 读回 `0x00000001` → `SR` 出现 IOC → `frmcnt` 递增 / `raw` 非零。

## 8. 明早的两条备选路径（若 build11g 仍失败）

1. **与阶段3 逐项 diff VDMA**：阶段3 用 `axi_vdma v6.17`、**三时钟同为 150 MHz 且同域**；逐项对比两版 IP 参数、寄存器复位默认值、`ps7_init` 差异，找出"为何阶段3 的 RESET 能自清"。
2. **阶段3 采集子图整段移植**：把阶段3 `alinx_ov5640 + axis_subset_converter + axi_vdma + HP2` 的 BD 片段原样移植进本工程（保留本工程的显示/PSU/地址布局），最小化"我们自己拼装"引入的差异。

## 9. 给 Wong 的决策点

- **若 build11g 通过**：R-07 相机链路收尾，进入相机窗 `R7-1..R7-8` + 正式证据归档。
- **若 build11g 仍失败**：建议接受**路径②（阶段3 子图移植）**——代价约 1.5–2 h（BD 重排 + 1 次 ~50 min 构建 + 1 次板级），风险是地址/时钟需重新对齐但结构已被阶段3 证明可用；**不建议**把 R-07 直接记为"受限"，因为阶段3 同板同 sensor 可工作，说明硬件与 sensor 均无问题。
- 需要决策的边界：是否允许为提高命中率**同时保留一份"显示链不动、仅替换采集子图"的最小改动版本**（推荐，回退风险最低）。

## 10. 未完成事项

1. **物理 POR**（清 `abnormal` 状态）——今晚多次重配 PL 未做冷启动，建议明早做一次彻底断电重启后再判 r52/r53。
2. **相机验收窗 `R7-1..R7-8` 未跑**（真实画面、帧率、颜色、长时间稳定性等）。
3. **正式证据归档未做**：`report/evidence/<task_id>/<run_id>/` 的 manifest（含 `hash_basis=commit_blob`）、产物清单与索引尚未生成本轮版本。
4. build11d 的探针版 RTL（`rtl/p3r_ov5640_dbg.v`、`rtl/p3r_cmos_8_16bit.v`）保留但未完成构建，若后续需要 IP 内部观测可直接启用。
5. 本文件与 `P3R_REPORT.md` §21/§22 为今晚的完整技术记录；**build11g 产物 sha 与 r52 结论待补到 §7/§4 表格**。

## 11. 脚本与 RTL 文件清单（明早接手用）

| 文件 | 用途 |
|---|---|
| `bd_p3r.tcl` … `bd_p3r_b11g.tcl` | 各 build 的 BD 生成脚本（自包含：建工程→BD→综合→实现→bit/XSA→报告） |
| `rtl/top_p3r.v` | build2–build6 顶层 |
| `rtl/top_p3r_sccbtest.v` | build7（SCCB 测试通道） |
| `rtl/top_p3r_b8.v` / `_b9.v` / `_b10b.v` / `_b11b.v` / `_b11f.v` / `_b11g.v` | 对应 build 的顶层 |
| `rtl/axis_to_video.v`、`rtl/rgb2dvi_wrap.vhd` | 显示链（阶段5 基线，今晚未改） |
| `rtl/p3r_ov5640_dbg.v`、`rtl/p3r_cmos_8_16bit.v` | 厂商 IP 源码副本 + 只读探针（build11d 用，废弃但保留） |
| `xdc/p3r.xdc`、`xdc/p3r_cdc.xdc`、`xdc/p3r_cdc_b9.xdc` | 引脚/时钟/CDC（`cam_pclk→clk_100` 灰码两级同步 + `set_max_delay -datapath_only`） |
| `s5_p3r_build<N>_console.log` / `_vivado.log` | 各 build 完整控制台与 Vivado 日志 |
| `out/build<N>/` | 各 build 的工程、`timing_route.rpt`、`util_route.rpt`、`drc.rpt`、bit/XSA |

**构建命令（单台 Vivado、`-jobs 1`）**
```bat
vivado -mode batch -notrace -log s5_p3r_buildNN_vivado.log ^
       -journal s4d_p3r_bNN.jou -source bd_p3r_bNN.tcl -tclargs build
```
**耗时参考**：早期 build 约 25–35 min；带 8–14 个 axi_gpio（OOC 综合逐个跑）后约 **45–60 min**；build11g 含时钟转换器预计 **60–75 min**。

## 12. 观测寄存器地图（当前 build11f/11g 可用，全只读）

| 地址 | 内容 | 判据 |
|---|---|---|
| `0x43C80000+0x00/+0x08` | `gpio_sccb` 控制 / 电平（8 bit） | SCCB 位操作 |
| `0x43C90000+0x00/+0x08` | 相机 PCLK 计数 / HREF 高拍数 | PCLK 84 MHz、HREF>0 ⇒ sensor 出流 |
| `0x43CA0000+0x00` | VSYNC 边沿计数 | ≈15/s ⇒ 帧同步正常 |
| `0x43CB0000+0x00/+0x08` | converter 侧 tlast / tuser 计数 | 行数×fps / ≈15/s |
| `0x43CC0000+0x00/+0x08` | converter 侧 beat 数 / stall 数 | beat 应为百万级 |
| `0x43CD0000+0x00` | 厂商 IP `m_axis_video_aresetn` 电平 | 恒 1（IP 未用） |
| `0x43CE0000+0x00/+0x08` | IP `tvalid` / `tlast` 计数 | tvalid 应百万级 |
| `0x43CF0000+0x00/+0x08` | IP `tuser` 计数 / `tready` 高拍数 | 15/s / 千万级 |
| `0x43C70000+0x00/+0x08` | SOF 计数 / 当前帧地址 | 递增 |
| `0x43C60000` 起 | **采集 VDMA**（`S2MM_CR=+0x30`、`SR=+0x34`、`VSIZE=+0xA0`、`HSIZE=+0xA4`、`STRIDE=+0xA8`、`FRMPTR=+0xAC`） | **本轮核心：`CR` 写 1 读回须为 `0x1`** |
| `0x43D40000+0x00` | `{rst_all_pa, rst_100_pa}` 电平 | r50 实测 `0x3` |
| `0x43D40000+0x08` | FCLK0(50 MHz) 计数 | 两次读差 >0 |
| `0x43D50000+0x00` | FCLK1(100 MHz) 计数 | 两次读差 >0 |
| `0x43D60000+0x00` | `axi_vdma_cam/axi_resetn` 电平（build11g 新增） | 须为 1 |
| `0x43D60000+0x08` | `axi_vdma_cam/s_axi_lite_aclk` 计数（build11g 新增） | 两次读差 >0 |

## 13. 已知环境注意事项（避免重踩）

1. **同一时刻只跑一个重型 Vivado**；多个 build 并行会 OOM（16 GB）。
2. **不要强杀正在启动的 build 进程后立刻删其 `out/build<N>` 目录** —— 会得到 `The batch file cannot be found.` 秒退（今晚踩过一次）；正确做法：先杀进程 → 等待 → 清理 → 再启动。
3. **BD 脚本里引用顺序很关键**：`rst_100`/`rst_all` 的引脚、`gpio_obs_*`/`gpio_dbg_*` 单元、`Mxx_AXI` 连接都必须在其创建之后；否则报 `[BD 41-701] requires at least two pins/ports` 或 `[BD 5-106] Arguments ... cannot be empty`。今晚这类返工 5 次，均在 3–10 min 内修复，属脚本问题而非设计问题。
4. 厂商 IP 原件 `D:\FPGA\AX7Z020`（及 `my_ip/ov5640_ip`）**保持只读**；如需内部观测，使用 `rtl/p3r_ov5640_dbg.v` 副本。
5. 每轮交付后立即把 **bit 的 sha256 先发**（板级要用），报告节后补。

---

**文档结束** · 生成时间 2026-10-31 23:55（UTC+8）· 生成者 video-bd（DSH BD 子代理）
