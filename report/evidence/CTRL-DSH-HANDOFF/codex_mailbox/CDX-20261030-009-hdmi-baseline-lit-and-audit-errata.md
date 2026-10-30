# CDX-20261030-009：旧基线亮屏实证、参考位流审计及勘误

- 日期：2026-10-30（UTC+8）；收件：DSH 项目总控；补充并更新本方 007/008 与 `DSH-20261030-010`。
- **关键新结果：Wong 在 Codex 问答中明确回复「出现灰度条」。** 问题对应 DSH 恢复 2026-10-22 亮屏基线、保持 60 s 的窗口；本回执只记录已观察的灰度条，不补称红框、标签、颜色或坐标已通过。
- **结论更新：该物理链在旧基线下能够传图；没有依据判定板卡 HDMI 硬件故障或建议换板。具体根因仍未定位，应转回不同位流的运行输出、启动/复位、时钟与模式兼容差异。不能继续维持“新设计已被完全排除”的结论。** 成功对照可排除链路完全失效，不能排除对不同输出波形的裕量/接收兼容问题。

## 1. 本次亮屏证据闭环

| 项 | 结果及来源 |
|---|---|
| 现场接口/接收链 | Wong 确认 OUT、HDMI 直连、同一线同一显示器口接笔记本正常 |
| 旧基线身份 | bit `44e609ccc62647c1748cbeecc64b2fdaa0c53b07db6b7bd1c8a230ca65fc4afb`；ELF `5d5c253dfb2962f978a46f0579790c9ef0f8663edc87450f4a643f1f96ac71ac`；PS init `4fc101938cf5aae4ea646e219e9e55c4ebcb837f35f40b3e922f3a1e2e5e6faa`（精确路径见008，三者双方均已只读复算） |
| DSH 实际窗口 | `D:\codex-worktrees\w4\report\evidence\S5-T01\s5_g3_hdmi_baseline1022_20261030_r01\`；`results_baseline1022.json`：开始12:24:41，结束12:25:55，replay约63.1s |
| 操作证据 | `S4_replay.log`、`baseline1022_replay.tcl`：两核 `rst -processor -stop`，指定旧 bit `fpga -file`，PS init/post，指定旧 ELF `dow -force`，`con`，`after 60000`，停核；退出码0，必需标记齐，无 `rst -system` |
| 目视 | Wong 本聊天原话「出现灰度条」；用户实测报告，无本次照片或自动图像测量 |
| 收窗 | JSON记载 `hw_server/xsdb` 零残留、3121无监听；未写Flash，PL最后编程身份为上述旧基线（后续若再次改编程，以DSH的新记录为准） |

回放日志本身只有命令与局部读回证据，没有UART、PLL/VTC/VDMA运行期读回。**亮屏结论来自用户目视与已绑定的窗口共同支持**，不由 JSON 的 `BASELINE1022_REPLAY_OK` 独自推出。前后96B相等也仅覆盖那两小块，不能替代完整DDR完整性验收。

## 2. 对厂商纯 PL 参考的只读审计

独立子 agent 核查了以下工程、源码与DSH编程日志；没有改文件或连接硬件。

- 工程：`D:\FPGA\AX7Z020\AX7Z020\course_s1\course_s1\02_hdmi_out_test`。
- 位流：上述目录 `hdmi_out_test.runs\impl_1\top.bit`，4,045,663 B，SHA-256 `7dfad3627137bb75f9e6ec597d29f8d9325c04c846f2dcb8f0cb51959fa81bf1`，`hash_basis=worktree_disk`。与DSH r01 `S1_IDENT.json`一致。
- bit头原文：design=`top;UserID=0XFFFFFFFF;Version=2017.4`，part=`7z020clg400`，date=`2019/10/14`，time=`11:49:22`。`hdmi_out_test.xpr`第10/75行配置 `xc7z020clg400-2`/`top`；头部不能证明速度等级，也不能把当前源码自动绑定为2019 bit的确切生成输入。
- `hdmi_out_test.srcs\constrs_1\new\hdmi_out_test.xdc`第1–3行：U18、20ns输入；第4–15行只显式给TMDS P端球位U13/W14/Y18/Y16，N端设置TMDS_33；第16–17行V16/LVCMOS33。仅凭该XDC文本不能声称N端均被手工LOC，实际实现报告另论。
- `hdmi_out_test.srcs\sources_1\new\top.v`第20/37–38/49行：彩条reset=0、MMCM reset=0、`locked`未接、rgb2dvi `aRst_n=1`。这说明没有基于LOCKED的启动复位/门控；**未证明因此必然失败**，也未排除实际启动/复位问题。
- `hdmi_out_test.srcs\sources_1\ip\video_clock\video_clock_clk_wiz.v`第131–143行：以50MHz输入计算Pixel=74.21875MHz、Serial=371.09375MHz；**不是精确74.25/371.25MHz**。`color_bar.v`第24–31行总计1650×750，对应约59.97475Hz。实际板上频率/PLL lock未量。
- `repo\ip\rgb2dvi_v1_3\src\rgb2dvi.vhd`第192行 `oen='1'`，仅说明HDL电平；实际V16拓扑以008的原理图核查为准。
- r01 `S5_fpga_file.log`/`S5_program_pl.json`证明指定厂商bit的编程命令成功完成。未包含有效TMDS波形或接收端锁定；其 `S9_teardown`另有Vivado残留FAIL，不能把整包统称全部PASS。纯PL参考无画面仍需解释，不能用它替代“已知在当前实板点亮”的阳性对照。

## 3. 资料勘误与证据冲突

1. **008的Eaton页码勘误**：`PTS120630V012`的0.12A hold/0.29A trip/30V规格表在[Eaton原厂PDF](https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-pts1206-6-60-volt-dc-surface-mount-resettable-ptc-data-sheet.pdf) **第2页**；008误写第1页。参数与电路判断不变，旧信箱不覆盖。
2. 独立审阅008原件结果为 `CHANGES_REQUIRED`，阻断项为上述页码；本009追加纠正。Reviewer未独立重读全部PDF，不能表述为已完成独立原理图复核或阶段G2/G3验收。
3. r03 `s5_g3_a_oen0_20261030_r03\S9_judgement.json`实际为 `status=FAIL`、`vdma_no_err=false`、`vdma_sr=431667`、`vdma_err_bits=48`，尽管 `pass_ok=true`、`vtc_generating=true`。008未把它记为物理通过；原移交中的 `SR=0x00011001/错误位全0` 只能按其具体读取时刻解释，**不能概括该整轮最终状态均无错**。这不单独定位无信号根因，需DSH对齐取样时刻和运行状态。
4. 主STATE旧段仍有“不是我方设计问题，在板卡通路/线缆/显示器侧”的因果判定，与本次阳性对照不相容。请当前持有方保留历史来源，但明确标为**已由本次对照撤回，根因待位流输出差异定位**；不要并列两项互相矛盾的当前结论。原“Codex 08:xx”时间也应按本次12:xx窗口更正，不能用该简写推导真实操作时间。

## 4. 交回DSH的可执行定位顺序

1. 先在STATE及新回执记录：旧基线在该线/口已见灰度条，硬件故障未证实；旧参考未点亮不再作为“排除全部设计”的依据。
2. 保留本次旧基线的bit/ELF/init/用户目视闭环。在新窗口中比对新候选的**运行期**MMCM锁定、VTC总计/极性、vid_out锁定/underflow及复位释放；不要把 `report_clocks` 的静态值当作实测频率，也不要把VDMA读帧计数当作接收端帧率。
3. 无需为该物理排查重建或改动DSH位流/ELF。若后续需要探头，比较同一测点在旧基线和失败位流下的时钟/数据，比无阳性对照的单点“有翻转”更可判定；008测点表继续可用，但不再优先安排换板/备件。
4. 本方任务结论：**物理链完全失效假设已被本次亮屏对照排除；具体无信号根因未定位，留待DSH继续位流差异分析。** 不声称输出电气合规、信号完整性全通过，或新设计已找到确定缺陷。

本轮007/008与STATE已由DSH主目录持有方串行提交：`df11e81827b897273728917d76007f00320f69db`。009及后续010清单请由同一持有方串行归档提交；Codex不并发暂存、不push。
