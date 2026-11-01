# C2 real-chainB r03 独立审查

审查时间：2026-11-01 00:10（UTC+8）  
审查结论：CHANGES_REQUIRED（存在板前阻断）  
审查边界：只读审查源码、候选 ELF、map、编译日志和现有 host 测试；未操作板卡、JTAG、UART、socket、vendor 工具；未修改源码、ELF、其他工作树或 Git。

## 固定对象

- w6 HEAD：f0fab846304aec4aa1baeeb012f9ce2888e86812。审查范围目录在该工作树下显示为未跟踪目录 legacy_codex_20261031/c2_board/；本报告是该目录中新建的审查文件。
- 源码目录：D:\codex-worktrees\w6\legacy_codex_20261031\c2_board\src\；fixture：inputs\fixture_fist_000_640x480_bgr888.raw。
- 候选 ELF：D:\codex-worktrees\w6\tmp\c2_real_chainb_20261101_r03\c2_real_chainb_display.elf；大小 1,345,004 B；SHA-256 3F26525C1DD9944763F3B60EE6D1DC8BEDE2CD5F0B0FEA53BF72303494A7EB2E，与任务卡一致。ELF 为 elf32-little，装载地址从 0x00100000 开始。
- fixture SHA-256：CE37AA772AEC9D45084EDC37F3A1E0FE1B258385EC57B1FD994D98614792DAD4；候选 ELF 中 fixture start/end 符号跨度为 0xE1000（921,600 B），与 fixture 大小一致。

## 阻断问题

### P1：最终 CHAINB 成功位会掩盖 C2 发布或显示失败

位置：src/s4d_ps_app.c:971-977、1006-1008、1021-1026。

C2 发布器对可处理的上游/内容错误返回正值：C2_PUBLISH_TOO_MANY_REJECTED=2、C2_PUBLISH_DETECTION_REJECTED=3、C2_PUBLISH_UPSTREAM_INVALID=1（见 src/c2_s5_publish.h:62-76）。调用方仅对 publish_rc < 0 提前返回，因此这些正值会继续读回无 VALID 的错误结果；只有 publish_rc==OK 才调用 C2_DisplayOneFrame。最终 CHAINB RESULT.pass 的判据却只看 DONE、PL error、decode_rc、原始 decoder count>=1 和 ACK idle，不包含 publish_rc，也不包含 C2_DisplayOneFrame 返回值。

decoder 输出容量为 15（src/s4d_ps_app.c:341；冻结解码器 src/s2a_ps_decode_nms_reference.c:10、263），而 C2 ABI 旁挂区要求上限 14（src/c2_s5_publish.h:14、18）。因此 15 框会产生发布拒绝，但原始 count 仍可满足最终 count>=1；非法坐标导致的 detection rejection 同理。此时 C2 PUBLISH 会报告 pass=0，显示会跳过或失败，最终 CHAINB RESULT 仍可能报告 pass=1。publish 成功但显示函数失败时，代码只打印 DISPLAY pass=0，最终 pass 同样仍可能为 1。

影响：用于板上验收的最终摘要不能证明 C2 发布成功或软件显示服务成功，会把失败链路误报为 PASS。关闭条件：最终成功判据必须纳入 C2 发布结果及显示调用结果；明确区分显示失败/未运行；增加离线回归覆盖 15 框拒绝、检测项拒绝和显示失败，并确认这些情形的最终 pass 均为 0。修复后冻结新的源码/ELF SHA 并复审。

## 已核实通过的范围

- 候选 ELF 的 DWARF/符号/字符串与目标变体一致：GNU C11 13.4.0、Cortex-A9、-O2；宏为 C2_REAL_FIXTURE_MODE=1、S4D_CHAINB_SELFCHECK=1、PREPROC_SRC=0；包含 main、s4d_chainb_selfcheck、C2Publisher_InitRev4Session、C2Publisher_PublishRev4、C2_DisplayOneFrame、S5Real_Parse 及 fixture 边界符号。
- 代码路径确为 fixture DDR copy+flush 完成后取 capture_ticks，软件 BGR888→INT8 CHW 预处理，启动 2B PL，DONE_SAFE 命中时取 infer_done_ticks，读真实 head13/head26 并调用冻结解码/NMS，随后调用 C2 Rev4 发布与单帧显示。日志字串明确 camera=0、source=real_fixture，不冒称真实摄像头。
- 解码框按 640×480 原图坐标编码，ABI 检测项保持 16 B 步进；C2 可发布上限 14，与末尾 32 B sidecar 不重叠。Rev4 先奇锁 flush 4 B、payload flush 288 B、再偶锁 flush 4 B；旧 API 的四次 flush 保持。旧 session SID 读取有 invalidate、DSB、sidecar 前后偶锁检查；新 Rev4 初始化只主张本会话 SID 恒定，不主张跨 POR 唯一。result_time 在最终 flush 前采样，receipt 记录到 flush 完成的 tick gap，不能称其为最终完成时刻。
- C2 显示代码会解析结果、用真实 fixture 转画布、渲染 A/B 双缓冲、flush 两个 framebuffer、初始化 VTC/VDMA；结果字符串固定 physical_scanout=NOT_VERIFIED。软件 render 和 VDMA 启动不能替代 HDMI 实物目视验收。
- 代码审阅确认 C2_ClassifyBusinessState 的无效状态→ERROR、过龄或 STALE→TIMEOUT、有效零框→NO_HAND、有效非零框→OK 映射合理；现有 test_c2_rev4_profile.c 仅断言了 NO_HAND，ERROR/TIMEOUT/OK 和上述最终摘要失败传播未获该测试覆盖。

## 构建/来源一致性与限制

- 候选源码 21 项与 fixture 的 SHA-256 已在审查时实算；关键项：c2_display_hook.c 49F8470D15A61895B0ACCFC159F049344BEAEC50009517123A0CFEC07B44BA17；c2_s5_publish.c DF23E8D33F1B6DD9F92DBDA4DA72FA02B505E3C03F3C91BCA60675F43F72CD0C；c2_s5_publish.h 4C5F595F5B41E2170061EF857DB411A5C2157A956F17F4040FB595BA53F5FCEC；s4d_ps_app.c 78584AF55EAEDA0FFBADDE3E1FEABDB69554A1C5E6FFEBBCAB49DDB2D1006232；s5_display_app.c 48368F16F2449A9CD86BAAED4E2977F8D651893ACE2BE75D1C353CEC67B598D3；s5_result_abi.h 0462F91173616B2AB1E6BC57CFDF1695229C4996A2D1FB87611537329FCEAB8C；test_c2_rev4_profile.c 754613843337A8CBECA2FAEF68063CD0B585811461EB752512F47F497ADB2415。
- ELF DWARF 显示编译单元绝对源路径指向上述 c2_board/src，编译目录 D:\FPGA_Competition；ELF 内宏和 fixture 与预期一致，源文件时间早于对应 object 生成时间，map 与 ELF 时间相同（2026-10-31 16:03:18 UTC）。这支持候选与当前源目录同源，但不是按 Git blob 绑定的可复现产物清单。
- 缓存有 10 个 C 编译单元的对象文件、fixture_blob.o、map 和 ELF。10 个 object log 中 8 个为空；s4d_ps_app.o.log（344 B）有 S4D_ST_ERROR 重定义警告；s5_real_source.o.log（965 B）有 memcpy 未声明警告（缺少 string.h）；link.log 为空。DWARF 记录了 GCC 13.4.0、目标 CPU/常见编译 flags 和宏值，但未留存实际逐条编译/link/size 命令及各命令退出码。Developer 声明 10 单元、link/size 均 exit 0；因日志空白，本 Reviewer 无法独立确认这些命令和退出码。两个 warning 当前不构成本报告的板前阻断，建议在后续改动中清理。
- host test 未由本 Reviewer 执行：尝试在隔离缓存创建 review_host 目录时被 managed sandbox 拒绝（命令退出码 1；编译器随后因目录不存在未运行）。没有测试失败结果可报告。已有测试源只读检查如上。

## 部署与实物边界

- 本任务指定 1 GiB stage4 BSP 一次 init；P3q XSA 仍声明 512 MiB（R16 未修）。源码 framebuffer 范围为 A 0x20000000–0x20384000、B 0x20384000–0x20708000，结果块从 0x20800000 起，均从 XSA 声明的 DDR 末端 0x20000000 起越界。该 1 GiB BSP + P3q XSA 组合须记录为部署身份/地址空间限制，不能称官方匹配平台；该结论不单独要求 root 重综合。
- 板上 POR、ELF 装载、实际 PL 网络、缓存一致性、sidecar/CRC 的硬件读回、VDMA/VTC 运行、HDMI 物理扫描均 NOT_RUN。本报告不代表 G3/G4；即使后续软件显示服务通过，physical_scanout 仍须独立实物核验。

## 审查命令及退出状态

- PowerShell Get-FileHash（源码、fixture、ELF、对象及日志）；rg 行号检索；GNU objdump -h、nm -a、readelf -s/--debug-dump=info/-p .comment、strings -a；所列只读检查均完成且返回匹配输出（退出码 0）。
- host 回归构建尝试因隔离目录写权限受拒（退出码 1），未产生临时文件，也未触及源码。
- 硬件/板卡命令：NOT_RUN（本审查禁止）。
