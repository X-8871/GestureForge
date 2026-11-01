# P3q 冻结复现清单（阶段5 G5）

| 项 | 值 |
|---|---|
| 任务 / RunId | 阶段5 S5-T01 / `g5_freeze_p3q_20261030_r01` |
| 工具 | **Vivado v2026.1**（SW Build 6511674, 2026-06-16；IP Build 6504888） |
| 器件 | `xc7z020clg400-2` |
| 工程 / BD / 顶层 | `s4d_p3q_r01` / `s4d_p3q` / `top_p3q` |
| 产物时间 | bit **2026-10-30 18:44:34**；XSA **18:45:20**（构建会话 18:31:10 → 18:45:20，约 14 min） |
| 机器清单元数据 | `BUILD_MANIFEST_P3Q.json`（本目录，38 个输入 sha + 2 个产物 sha） |

## 1. 构建命令（一次到底）

```bat
cd /d D:\FPGA_Competition
vivado.exe -mode batch -notrace ^
  -log  D:\tmp\lead\p3q_video_20261030_r01\s5_p3q_build_20261030_r01_vivado.log ^
  -journal D:\tmp\lead\p3q_video_20261030_r01\s4d_p3q_r01.jou ^
  -source D:\tmp\lead\p3q_video_20261030_r01\bd_p3q.tcl ^
  -tclargs build
```

- `bd_p3q.tcl` 内全部绝对路径，工作目录无关（当时 CWD=`D:/FPGA_Competition`）。
- `-tclargs build` 必须带；不带则脚本只做 BD validate 后退出（validate-only 模式）。
- 构建脚本 sha256：见 manifest `inputs.role=构建脚本`。

## 2. 构建参数（脚本内固定）

| 阶段 | 命令 |
|---|---|
| 综合 | `launch_runs synth_1 -jobs 2` → `wait_on_run synth_1`（PROGRESS=100% 否则报错） |
| 实现 | `set_property STEPS.WRITE_BITSTREAM.ARGS.BIN_FILE true [get_runs impl_1]`；`launch_runs impl_1 -to_step write_bitstream -jobs 2` → `wait_on_run impl_1` |
| 导出 | `open_run impl_1` → report_timing_summary / util / drc / io / clocks / clock_utilization → `write_hw_platform -fixed -force -file out/s4d_p3q_r01.xsa` |
| bit 复制 | 从 `out/proj/s4d_p3q_r01.runs/impl_1/*.bit` 复制为 `out/s4d_p3q_r01.bit` |

## 3. 源文件与约束（清单见 BUILD_MANIFEST_P3Q.json，共 38 个输入）

- **约束（2 个）**：`p3q.xdc`（引脚/时钟/IO 标准）、`p3q_cdc.xdc`（32 位格雷码 CDC 的 `set_max_delay -datapath_only`）
- **P3q 自身 RTL（3 个 + 7 个厂商 VHDL）**：`rtl/top_p3q.v`、`rtl/axis_to_video.v`、`rtl/rgb2dvi_wrap.vhd`；
  `src/rgb2dvi/{DVI_Constants,SyncAsync,SyncAsyncReset,ClockGen,TMDS_Encoder,OutputSERDES,rgb2dvi}.vhd`（厂商源逐字节复制）
- **preproc v2 RTL（7 个，p2c 冻结源）**：`D:/tmp/lead/p2c_20261029_r02/src/rtl/`
  `s4d_coord_tables.svh`、`s4d_preproc_csr.sv`、`s4d_preproc_engine_v2.sv`、`s4d_axi4_rd_shim.sv`、
  `s4d_preproc_out_axis.sv`、`s4d_preproc_v2_wrap.sv`、`s4d_axis8_to_axis64.sv`
- **2B 推理核 RTL（18 个 .sv，w2b 只读引用）**：`D:/FPGA_Competition/w2b/src/…`（清单内逐个 sha，含 `s2b_inference_top.sv` 等）

## 4. 产物 sha256

| 文件 | 字节 | sha256 | 时间（UTC+8） |
|---|---|---|---|
| `out\s4d_p3q_r01.bit` | 4,045,762 | `4d6ea2efd71bc6f9113f3a009278f097443d8a03b244aaedac70ec23f0b9b6e4` | 18:44:34 |
| `out\s4d_p3q_r01.xsa` | 344,843 | `dfefc883b0fe267cf8bffc3f76b15067b9ab7ed99779670d661f8261907fe96d` | 18:45:20 |

时序/DRC/资源：`WNS +0.371 / TNS 0.000 / 失败端点 0 / WHS +0.036`；DRC 444 条 **0 error**；
LUT 24,769 (46.56%)、FF 12,648、BRAM 35.5、DSP 158、MMCM 1、BUFG 4、OSERDESE2 8、IOB 10。
构建日志：**0 ERROR / 0 CRITICAL WARNING / 98 WARNING**。

## 5. 从零重建最小步骤

1. **环境**：Vivado 2026.1；器件 `xc7z020clg400-2`；内存 ≥4 GB 可用、磁盘 ≥10 GB（本机 16 GB 实测通过）。
2. **源树三处就位**（全部为冻结副本，不改内容）：
   - `D:/tmp/lead/p2c_20261029_r02/src/rtl/`（preproc v2，7 文件）
   - `D:/FPGA_Competition/w2b/src/`（2B 推理核，18 文件）
   - `D:/tmp/lead/p3q_video_20261030_r01/`（bd_p3q.tcl、2 个 xdc、rtl/ 3 个、src/rgb2dvi/ 7 个）
3. **在空 out 目录重建**：复制 `p3q_video_20261030_r01` 到新目录（或改脚本内 `base`/`out` 两个变量指向新目录），
   执行 §1 的命令（带 `build`）。
4. **校验点（日志尾部必须出现）**：
   ```
   P3Q_FCLK1_ACT=100.000000 MHz
   P3Q_SRC_BASE_BD=0x12000000
   ==== P3Q BD VALIDATED ====
   P3Q_SUMMARY WNS=0.371 WHS=0.036
   P3Q_DRC: Checks found: 444
   P3Q_BIT_OK
   P3Q_XSA_OK
   ==== P3Q DONE ====
   ```
5. **比对产物**：bit/XSA 的 sha256 应与 §4 完全一致（Vivado 位流对同一脚本/源/工具版本是可复现的；若 sha 不同，
   先查源树 sha 与 Vivado 版本，再查是否有 `out/proj` 残留被复用）。
6. **手工步骤：无**。RTL/约束引入、BD 构建、地址分配、综合、实现、bit/XSA 导出、报告生成全部在 `bd_p3q.tcl` 内。

## 6. 非确定性 / 注意事项（如实记录）

1. **首轮 validate 失败（已修，属构建过程事实）**：2026-10-30 18:25:46 会话报
   `ERROR: [BD 41-758] ... clock pins are not connected`（`gpio_uf/s_axi_aclk` 未接时钟）。
   修复：在 tcl 中把 `gpio_uf/s_axi_aclk`/`s_axi_aresetn` 接到 FCLK_CLK0 / `rst_all`；18:31:10 重跑成功。
   **本次交付产物全部来自第二次会话（PID 47260）。**
2. `[BD 41-1306] WARNING`×6：`m_axis_mm2s_*`/`gpio_io_i` 等被用户直连 net 覆盖接口连接 —— 本设计就是逐位连接流，
   属预期；**不要把 `write_bd_tcl` 回写的 BD 当作源，重建以 `bd_p3q.tcl` 为准**。
3. `[IP_Flow 19-4994] WARNING`×2：重新生成时覆盖 vdma_0 / pc_hp2 的 `_ooc.xdc` —— 正常 IP 生成行为，不影响产物。
4. **OOC 并行**：综合时 12 个 IP OOC 子 run 一同拉起（并发度由 `-jobs 2` 控制），本次未见重试/卡死；
   16 GB 本机无内存告警。若换机器重建，建议保持 `-jobs 2`（16 GB 档位），不要盲目加大。
5. **phys_opt 中间估计 WNS=-0.557** 与最终布线 **+0.371** 不同属正常收敛过程；冻结以 `P3Q_SUMMARY` 为准。
6. `out/ps7_init.*` 的 mtime=19:30:35 是板测 `loadhw -hw *.xsa` 触发的重新导出，**不是构建时间**；
   XSA 内 ps7_init 与 18:45 构建一致（以 XSA sha 为准）。
7. 无外部 IP 仓库、无自定义 IP 打包（rgb2dvi 为厂商源复制）⇒ 无 IP 版本漂移面。

## 7. 上板验证证据（同一产物）

- 计算回归（P3q）：`S4-T34/g4_q_m4b_close_20261030_r01`（47,287 ms）、`g4_q_chainlite_a_20261030_r01`（47,287 ms、框与参考全等）、
  `g4_q_p2c_tensor_crc_20261030_r01`（`0x5B183B50`）
- 显示 G3（P3q）：`S5-T01/g4_q_disp_g3a_20261030_r01`（fps 60、欠载 0）、`g4_q_disp_g3b_20261030_r01`（`box_crc=0x2D949C0C`）、
  `g4_q_disp_g3c_20261030_r01`（整帧 CRC 匹配 118,858,521）
- 并发（显示带宽 + 2B）：`S5-T01/g4_q_concurrent_display_2b_20261030_r09`（47,420 ms，+133 ms/+0.28%，欠载 0）
- 30 min 长稳（G5 冻结项）：`S5-T01/g5_q_longrun_p3q_20261030_r01`（结论见该目录 `window_close.txt`）