# S3CTRL-20261021-003：Codex → DSH 阶段三交接补充

- 用户要求：补充交接文档，由 DSH 接续完成阶段三任务。
- 交接时间：2026-10-21 19:53（UTC+8）；状态以本树 `.codex/STATE.md` 末尾 11 字段行为准。
- 工作树：`D:\codex-worktrees\dbdf`；分支：`codex/stage3-video`。
- 技术基线：`0d47801266a96c950d025702c158734f9bbd25de`。本交接文档及 STATE 将另作一次提交，接手时 HEAD 应为该交接提交，不是强制等于技术基线。
- Codex 除本次交接文件提交外已停止工程写入；提交完成后不再启动构建、板测、心跳写入或后台任务。DSH 接管前必须重新检查资源及会话，不能把本次快照当作永久占用许可。

## 1. 接手顺序与边界

完整阅读本树 `.codex/STATE.md`、本文件，再读 `D:\FPGA_Competition\AGENTS.md`。旧 `S3CTRL-20261021-002` 仅作为历史依据；与本次实际证据冲突的结论以本文件及所引证据更正，不覆盖历史原件。

核验完整路径、分支、HEAD、`git status --short`、由 `git rev-parse --git-path index.lock` 解析的锁、重型进程及 2B 的 `hw_server`/JTAG 会话。确认 OFFERED 后按协议改为 CLAIMED→IN_PROGRESS，更新负责人和心跳。

只写 `D:\codex-worktrees\dbdf` 的既有阶段三范围；`D:\FPGA_Competition` 和 `D:\FPGA\AX7Z020` 业务文件只读，不写两个 mailbox。Git 提交会更新工作树对应的公共 Git 元数据，应串行提交，但不得修改主仓工作区。不删除、移动或回退 `NA/`、`clockInfo.txt`、旧提交或任何旧运行目录。构建产物留在原有忽略的 `tmp/**`，不因未提交而清理。

2026-10-21 19:52–19:53 快照：工作区只有原有未跟踪 `NA/`、`clockInfo.txt`；无 index.lock；Git Bash `ps -W` 未见 Vivado 本体、hw_server、XSDB、xsim 或本轮 PDF 阅读进程，`netstat -ano` 无 3121 条目。存在多个 `vivado-mcp-server` 辅助进程，不代表正在综合或可随意结束；本轮未终止它们。本轮构建监督记录退出码 0，PDF 解析已完成；无须恢复或重复启动这些任务。接手时必须重新核对。

## 2. 阶段现状：实时成立，颜色未过，未冻结

第一版范围仍是 AN5642（OV5640）单通道 → 扩展口 → PL/DDR → HDMI 原始视频，不加 CNN、检测框或双目同步。

- J11 上使用模块 CMOS2，可读 CHIPID `0x5640` 并实时出图。CMOS1 历史无 ACK 不能单独证明模块物理故障。
- 厂商 SOF 已由 VSYNC 边沿改为 HREF 长间隙后的首像素；保留该已验证修复，不倒回旧帧同步实现。
- 原始未补偿样本显示 B 最高位为 0、maxB=120，G 同时缺 bit4；不应再写“绿色正常”。
- 新补偿数值生效、maxB=248，但 Wong 明确反馈“实时正常，但偏青或其他色偏”“阴影部位偏蓝色，白色部分偏黄”。照片呈明显黄/紫蓝伪彩，颜色 FAIL。
- 当前板上最后一次已知下载是本轮补偿位流；它是失败实验版。交接时没有重新读取实板确认此刻配置，接手后不能假定板卡未掉电或未被别的任务使用。

### 必须保留的三项纠正

1. **旧补丁确已进入 OOC 和实机数据路径**。原先补丁改的是输入低 5 位，实际对应显示红，不是显示蓝；旧行样本 offset2 符合重建字母表。“补丁未进入设计”结论作废。
2. **缺失线索指向 DVP 字节 MSB／`cmos_d[9]`，不是 D6**。实际 DDR offset0/1/2 是 B/G/R；B 来自输入字 `[15:11]`，G 来自 `[10:5]`，R 来自 `[4:0]`。字 bit15 与 bit7 分别影响蓝最高位和绿 bit4，均来自两个字节的 MSB。
3. **低 4 位拉伸不能恢复丢失最高位**。新公式 `{s_axis_tdata[14:11],s_axis_tdata[14],s_axis_tdata[10:0]}` 只证明显示蓝近似重建生效，不恢复真实亮度。不得通过调白平衡掩盖伪彩、放宽颜色判据或将 `maxB>127` 当作修复验收。

## 3. 已核实的格式与采集路径

本轮 `uart.txt` 第 12–14 行实际回读：`0x4300=0x60`、`0x501F=0x01`、`0x4740=0x20`、`0x3034=0x1A`、`0x503D=0x00`。不能把初始化注释代替回读，但这几个值已有实机记录。

官方资料优先：

`D:\FPGA_Competition\摄像头资料\官方资料\AN5642\AN5642_CD\CD\datasheet\camera\OV5640_datasheet.pdf`

SHA-256：`b7059c287dd23ab36730daf5db93f1d921bb1509fce37af1884c09dcda06ace7`。

- PDF 第 87 页：`0x4300=0x60` 是 RGB565，字节序为 `{b[4:0],g[5:3]}`、`{g[2:0],r[4:0]}`，与已核实显示映射一致。
- PDF 第 141 页：`0x501F[2:0]=001` 选择 ISP RGB。
- PDF 第 102 页：`0x3017` / `0x3018` 是数据脚等输出使能，`0x301D` 是选择控制；目前缺这些相关控制的实际回读，不能以表中写入 FF 代替。
- PDF 第 93 页：`0x4740` 为极性控制，`0x4741` 为测试图案，`0x4745` 有位序控制。只据定义设计受控实验，不猜测未定义位或调试选择的副作用。
- 现有链路是 DVP、两字节拼接 RGB565，没有 Bayer 去马赛克、YUV→RGB 或 MIPI 接收模块；豆包的通用文字仅为参考，不据外观直接改成 RAW/Bayer 路线。

独立 Reviewer 已确认 F17 实现为 `cmos1_d[9]`、INPUT、LVCMOS33、Bank35（新运行 `impl_1/design_1_wrapper_io_placed.rpt` 第 154 行）。顶层/OOC 连接到采样触发器，未发现该入口直接接常零；官方 `cmos_8_16bit.v` 第 55 行拼接完整字节，没有在此截掉 MSB。**这不等于验证了实际电平、时序裕量或传感器输出正确性。**

## 4. 固定版本、证据和脚本陷阱

失败实验运行：`D:\codex-worktrees\dbdf\tmp\s3r06\t04_display_bluefix_20261021_r01`。

- bit：`project/ov5640_single.runs/impl_1/design_1_wrapper.bit`，SHA-256 `0f3b74e4b090d8b8789806e23a1f7a17731d331e78ab918c13a1233b8bf2b61d`。
- XSA：`design_1_wrapper.xsa`，SHA-256 `b9a565729148be989cb37e10eaf46f0da7c5df0fec2db856a278afba9daddf17`。
- 复用 ELF：`D:\codex-worktrees\dbdf\tmp\s3r06\t04_j11cmos2_elf_v8\elf_build\app\an5642_j11cmos2_v8_off.elf`，SHA-256 `85e989196dc34f5f1cc7b87607b2905f54405ec95a5486cf14916edd7eec145e`。
- 当前 AWB 未手动固定；ELF 文件名中的 `off` 不能代替日志解读，实际 UART 说明 auto AWB unchanged。
- 实现退出 0，耗时约 970.3 秒；WNS 1.249946 ns、WHS 0.006289 ns、DRC 0 error / 8 warnings，不是完整时序签核。
- 方法学仍有 TIMING-17 critical 236、TIMING-36 critical 1、未约束内部端点及 I/O delay 缺失；不得加虚假时钟关系或豁免来换通过。
- UART 5–25 秒持续记录 S2MM sticky `0x00015810`；15/15 指纹变化不代表 VDMA 无错误，需单独清理/观测和解释。

证据入口（以下相对路径均位于本工作树）：

- `report/evidence/S3-T05/t05_display_bluefix_board_20261021_r01/README.md`：完整实验结论；`visual_result.json`、原照片、UART、下载日志、三行原始数据、`board_analysis.json`、`closeout_review.json`、清单均在同目录。
- `report/evidence/S3-T05/t05_display_bluefix_20261021_r01/`：构建/时序/DRC报告及清单。
- `report/evidence/S3-T05/t05_codex_g2_20261021_r01/`：十项源码哈希与独立审查；其中“尚未上板”是当时快照，已由后续板测证据补充，不覆盖。
- `report/evidence/S3-T05/t05_codex_diagnosis_20261021_r01/` 与 `report/evidence/S3-CTRL/S3-T05/t05_takeover_20261021_r03/`：旧错误通道判断的复算与原始样本。r01/r02/r03 各自保留失败或当时状态，不把早期失败包装结果当当前状态。
- 新运行 `inspection_results/` 与 `tmp/3/S3-T05/t05_methodology_baseline_20261021_r01/`：新旧方法学检查输出。
- `tmp/3/S3-T05/t05_sensor_register_pdf_20261021_r01/`：官方 PDF 技能解析，manifest success、OCR false；选页 23/24/86/93/102/141，87 页另经原 PDF 原生文本提取核对。无需重跑全量解析。

### 不要原样重启的一次性工具

`scripts/stage3_t04/check_display_bluefix.py` 钉住旧基线 `d476df8...` 与固定 RunId；构建启动器也固定本轮 RunId。提交后身份检查拒绝是设计行为，不是 TCL 损坏。后续应在新运行、明确新源码基线下设计实验，不删除旧目录或关闭身份检查强行复用。

`scripts/stage3_t05/jtag_dump_display_channels.tcl` 只适用于已核实 base=`0x00110C00`、stride=3840、1280×720 的当前 ELF。**重编 ELF 可能改变缓冲地址，必须读取/验证实际 VDMA FRAME0 与布局，再调整安全转储；不要抓错地址后判断颜色或冻结帧。**

**禁止原样执行历史 `jtag_dump_rows3.tcl`**：其暂停失败后仍可能继续 mrd，恢复失败也不能可靠报告非零。旧002交接中的该命令仅保留历史，不作为接续命令；请用上述已审安全脚本，并手动创建全新空输出目录。

`run_t05_board_capture.sh` 末尾只返回下载退出码；UART/只读探测状态另有输出，不能仅凭脚本最终 0 就声称全部通过。使用前只读检查脚本，保留各步骤真实退出码、输入哈希与日志；所有新日志目录用唯一 tag 并验证不存在，不能依赖脚本替你防覆盖。

## 5. DSH 接续路线及停止条件

1. 接管后先绑定新基线，复核上述证据；不要重做已证实“旧补丁进入 OOC”排查，也不继续把低位近似拉伸当修复。
2. 基于官方初始化表/手册，补全 DVP 输出使能、数据选择、位序等实际回读；保持读操作与寄存器写测试分离，逐项记录原值、期望、读回和恢复方案。新 ELF 在隔离目录构建，勿 `make clean` 旧 BSP/旧 ELF。
3. 选择有明确可区分结果的单变量实验：先以内部已知彩条/既有 HDMI 证据定位显示后段，再以传感器测试图案及原始采样区分源端、采样与拼接/FIFO/DDR。旧彩条记录不能冒充新测；不得靠画面外观单独判因。无 ILA 时使用受控诊断 RTL/应用侧 cache 正确的采样，不直接 mrd 运行中的 A9。
4. 如需改 RTL 或传感器易失配置，先完成适用的便宜测试和独立 Reviewer，再单并发受控构建、核对 OOC/网表与约束、易失上板；正确连接不凭截图猜测。不要在采样时序未核实时宣称硬件坏。
5. 找到原因后实施实际修复，验证真实通道数据、实时性、颜色、VDMA 状态及相关时序；再做正式计划要求的至少 30 分钟连续无输入/显示死锁验证，保留计数、日志及视频/用户观察。记录帧率/分辨率/像素格式和丢帧口径，不添加未经确认的指标。
6. 通过适用 G1/G2/G3/G4/G5，更新 STATE 与证据、检查清单，核对差异并提交；不自动 push。任何未完成项明确说明，不能因提交或文档完成就写阶段 DONE。新权限、硬件操作或重大范围选择缺失时向 Wong 提出明确请求，继续不依赖它的安全工作。

硬件齐全、AN5642 已到手；板卡照片已在用户此前指定的 `C:\Users\22061\Documents\Obsidian Vault\02-项目\基于 AX7Z020 的低比特神经网络 FPGA 加速系统，实现摄像头手势识别并驱动板卡进行实时交互\01-竞赛材料`。路径引用只作定位，读取前仍核验精确存在；不要再次索要已提供的板卡照片。需要 Wong 看显示器、摆放目标或配合上板时直接给清晰步骤与预期。

## 6. 不变红线

- 不烧 QSPI/非易失存储、不改接线、不做电气测量、不替用户购买硬件。工程诊断授权不扩大这些边界。
- 同时只跑一个重型任务；启动前核对资源与 2B `hw_server`。不终止、复位或接管归属不明/2B 的会话。
- BASIC 按进程设置 `XILINXD_LICENSE_FILE=D:/Xilinx_licenses/basic_only.lic`；不读/上传许可内容，不加 ILA。受控 Vivado 时设 `VMCP_AUTOSTART=0`，日志与 TEMP/TMP 落在本轮隔离目录，遵守原有用户 init 脚本风险约束。
- 对 A9 读取必须 `stop → mrd → con`；暂停失败不读，异常仍尝试恢复。运行中直接 mrd 可导致 DAP `0x30000021`。`targets -set *DAP* → rst -type system` 会清 PL，不能当无副作用只读恢复；使用前核对会话和允许范围，再按已授权易失流程重下 bit/ELF。
- Git Bash：`C:\Program Files\Git\bin\bash.exe`；UTF-8、中文注释、UTC+8。保持现有源/工程布局与完整字面路径，不写主仓业务文件/mailbox，不覆盖散落件/历史证据。

## 7. 可直接粘贴给 DSH 的提示词

```text
你是 DSH 侧【阶段三总控】，Wong 要求你接续完成阶段三，不是只写排查方案。

先完整读取 D:\codex-worktrees\dbdf\.codex\STATE.md 和
D:\codex-worktrees\dbdf\report\evidence\S3-CTRL\S3-T05\S3CTRL-20261021-003-handoff-to-dsh-stage3.md，
再读 D:\FPGA_Competition\AGENTS.md。这是本次交接依据；旧002中的D6硬件故障、补丁未进入设计及主目标已完全达成等判断已被新证据更正。

工作树只能用 D:\codex-worktrees\dbdf，分支 codex/stage3-video。技术基线 0d47801266a96c950d025702c158734f9bbd25de，HEAD还包含后续交接提交，先核对而非回退。核验完整路径、分支/HEAD、status、index.lock、重型进程及2B hw_server；确认STATE OFFERED后CLAIMED→IN_PROGRESS，独占写入并更新心跳。Codex本次交接提交后已停止写入；保留NA/、clockInfo.txt及所有旧tmp运行。

范围：AN5642/OV5640单通道经PL/DDR到HDMI原始实时图像，无CNN/检测框/双目同步。实时已成立，颜色未过，阶段未冻结。实际回读4300=60、501F=01为RGB565；不是据外观判Bayer。旧补丁已生效但改错显示通道；新蓝低位拉伸也已生效，maxB=248，却被Wong确认阴影蓝/亮部黄、明显伪彩，颜色FAIL。不要继续盲调AWB或把数值通过当验收。

首查共同缺失的DVP字节MSB/cmos_d[9]：它对应原始字bit15与bit7，分别影响蓝最高位和绿bit4；不是D6，尚无硬件故障证明。F17输入/OOC采样连接和完整字节拼接已复核。按官方资料补全3017/3018、数据选择/位序等实际回读，设计单变量彩条/采样实验，再修复真实根因。注意新ELF可改变帧地址，安全转储不能盲用0x00110C00；一次性构建器绑定旧HEAD/RunId，不删除旧目录强行重跑。VDMA sticky 0x00015810及方法学critical/I/O约束缺口均未关闭。

按交接文档路线持续完成开发、独立审查、受控构建、适用实板验证、至少30分钟耐久、证据和Git提交；不得降低验收标准。需要Wong上板配合或看显示器就直接说明步骤，不重复索要已有板卡照片。只写阶段三树，主仓/厂商原件只读，不写mailbox；不QSPI、不改接线、不电气测量、不干扰2B，一次一个重任务。A9读取严格stop→mrd→con；BASIC许可按进程注入，无ILA。新权限/重大决策缺失再向Wong请求，不宣称未完成任务已通过。
```
