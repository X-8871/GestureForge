# R-05/C2 真应用写端集成准备度核查

日期：2026-10-31（UTC+8）  
范围：只读核对固定源码、C2 接缝、显示调用、时间戳/会话语义与部署身份。此文件是准备度证据，不是实现、构建或板验报告。

## 核查边界

- 只在本目录新增此文档；没有改动已审 C2 库、main、w4、w5、w2b 或冻结物。没有暂存/提交，也没有运行测试、编译、XSDB、Vivado 或硬件。
- 主仓基线按当前 main HEAD `35c45778d2473faea41f16da014ba33e8e031bda` 的 `.codex/STATE.md` commit blob 核对；R-16 对应行 149–160。主 STATE Git blob OID=`3055f25899b1467946fb27e3b29ed4569ecc82cf`。
- **哈希基座**：表中标 `commit_blob` 的 SHA-256 是对所列 commit 下 `git cat-file blob <commit>:<path>` 字节计算；同时给出 Git blob OID。标 `worktree_disk` 的值来自当时精确路径磁盘字节，不代表提交内容，不作为冻结输入或交付清单成员。
- 首次调用 Git Bash 被沙箱以 `E_ACCESSDENIED` 拒绝；本核查随后用 PowerShell 只读命令完成。未以此改变任何目标或版本。

## 可恢复输入身份

| 用途 | 固定版本与精确路径 | SHA-256 / Git blob OID | 基座与限制 |
|---|---|---|---|
| C2 发布器实现 | w6 HEAD `25dbc5ec702dd1bc728b8ece0fe9cf529ac371e3`；`D:\codex-worktrees\w6\legacy_codex_20261031\c2\c2_s5_publish.c` | SHA-256 `1fdcea6ae29e8e7dfb7a83ee3e141a103e4eddb1730dc3d116e43993dd8d189e`；blob `d3ac0563513b3657af169d86b6d9808e1ca8c50e` | `commit_blob`；保持原样 |
| C2 发布器接口 | 同上；`D:\codex-worktrees\w6\legacy_codex_20261031\c2\c2_s5_publish.h` | SHA-256 `2c36f5cb10087cf2dfe91d5c3aefda1120fe7ba070ffc09051088b1964d99985`；blob `f1a30dc4e3c72ec3ce678c89557385accfe9fe51` | `commit_blob`；输入为真实 `s2a_t62_detection`、GT 与 flush callbacks |
| C2 实施/板验计划 | 同一 w6 HEAD；`D:\codex-worktrees\w6\legacy_codex_20261031\c2\C2_IMPLEMENTATION_AND_BOARD_PLAN.md` | SHA-256 `30eaa886d184ab8a41ad8f01869d0add1a547b279918b48f14db447ff466fbe6`；blob `8e68eb1c4626cc53534536573b309a4c66c96e4f` | `commit_blob`；行 33、40–41、45–67、87 起列明 SID/时间源与实物计划限制 |
| S4 2B chain-B 应用 | 固定 C4 输入 w4 HEAD `07efa677d1eaa8f427ec8f3ce7216ab3ed3c431c`；`D:\codex-worktrees\w4\vitis\stage4\ps\s4d_ps_app.c` | SHA-256 `87a639aa4a5d375d3c25472062abe7e7c93fe77b5c08a499726f5c788b7d9f79`；blob `ebc5b9766796e89c3a7696d1bec9d37b04881f31` | `commit_blob`；与 w4 当前 HEAD `e22fccf8cc8bbd0ccc8b20c4289c3244b0508c2a` 的该路径 blob 相同 |
| 阶段5显示渲染候选 | w4 文件历史提交 `212a47d3bb5a6cd5e7f582fdbc625421aef8cf91`；`D:\codex-worktrees\w4\report\evidence\S5-T01\s5_p3b_sw_20261030_r01\src\s5_display_app.c` | SHA-256 `48368f16f2449a9cd86baaed4e2977f8d651893ace2be75d1c353cec67b598d3`；blob `fdfbb44d31d929cd3000ff3992569ba74e7f5c9d` | `commit_blob`；是已提交 P3B renderer 候选，不等于 rev4 producer 冻结源码 |
| 阶段5显示接口头 | 同一 w4 文件历史提交；`D:\codex-worktrees\w4\report\evidence\S5-T01\s5_p3b_sw_20261030_r01\src\s5_display_app.h` | SHA-256 `dc5f30eb2faa8ad3a31d4fc46728856a3f8e4070a82e1934cb1c36984833677b`；blob `c2ef879382de45251c285c823b6c404f04fb737e` | `commit_blob` |
| 阶段5结果 ABI | 同一 w4 文件历史提交；`D:\codex-worktrees\w4\report\evidence\S5-T01\s5_p3b_sw_20261030_r01\src\s5_result_abi.h` | SHA-256 `0462f91173616b2ab1e6bc57cfdf1695229c4996a2d1fb87611537329fceab8c`；blob `10c1230d075f5dd966afc7bdbf0249a84a5d3918` | `commit_blob`；结果基址 `0x20800000` |
| 阶段5 G0 时间事件 | main HEAD `35c45778d2473faea41f16da014ba33e8e031bda`；`D:\FPGA_Competition\docs\obsidian-project\02-方案设计\阶段5_HDMI显示链G0方案_20261030.md` | SHA-256 `90afb5306bb76305bc13a4f212d4308db37027c5b3f38366a4adc20dbc35e2fe`；blob `e62d1c78d6d38eda0fb34643a2e0950ddaed67f6` | `commit_blob`；§10.1/行132定义 cap、infer、display 三事件 |
| C4 rev4 独立审查记录 | `D:\codex-worktrees\w6\legacy_codex_20261031\c4_r02\C4_rev4_incremental_20261031.md` | SHA-256 `e36a4e092ddcf8b163b8e615e5f9394bcb2d2c38102bc6184e64c796e78effcd` | `worktree_disk`；未提交报告，行20、23、26、30记录源码绑定、SID、模拟 producer 与时间语义问题 |
| rev4 producer 构建记录 | `D:\codex-worktrees\w4\report\evidence\S6-T01\s6_producer_v4_rev4_20261031_r01\p3q_producer_A_rev4_record.json` | SHA-256 `a75fb173a3f6cb09bf5461ef171450ac60ad4358f1819c4027bd2d4edb0d499b` | `worktree_disk`；记录声称的 producer 源码 SHA 见下文，实际源文件未随记录包提供 |

rev4 记录声明 `s5_display_app.c` SHA-256=`bed1a9f68611f34e3c64ebd4ffba7202bf5454a9b554ae63bc4e0907327f3ca4`、`s5_display_app.h`=`73770fce00a36a99320a0fe3dd646f0af99c0b6e805ad189a776dae4556380e3`、`s5_publish_abi.h`=`a8ca5c1f2cb8bfc02b5fa9150ded280ffa0f66342a3b217e8399042e3ac4e456`。P3B manifest 中相同路径的候选分别为 `48368f16f2449a9cd86baaed4e2977f8d651893ace2be75d1c353cec67b598d3` 与 `dc5f30eb2faa8ad3a31d4fc46728856a3f8e4070a82e1934cb1c36984833677b`；P3B `s5_real_source.c`=`d7696ecaf5fe174c1c3a376ac7159865cfd06e4025b226ed721ac672a35dffa5`、`vdma_ctrl.c`=`78b8d689522f148096b5f940c6227cba93139315c74bc50276ea8c861d2b796d`，而 rev4 记录声明分别为 `cec077a102105c1fb755afc9f19a4b131909aa411d31d3de27e6969a402a50e8` 和 `bb32bcbebe220a38ad19000a660929834f563a0fe6b82b7968160833da17eff8`。`s5_timebase.c`（`47a3dc27ed2c0dc9c60a326eda979a80d2a9020c69ecd5c8361e66fbdae0de96`）与 `s5_result_abi.h`（`0462f91173616b2ab1e6bc57cfdf1695229c4996a2d1fb87611537329fceab8c`）则相同。w4/w5 未找到 `s5_publish_abi.h`；C4 审查确认 rev4 manifest 只有文档/JSON、没有实际源码/自检源。故可复用的显示绘图候选存在，但 rev4 producer 的实现绑定未闭合。

## 实际接缝与所需适配

1. S4 当前符号不是字面上的 `s4d_chain_lite_selfcheck`。目标链路在 `s4d_ps_app.c` 行752、757 的 `S4D_CHAINB_SELFCHECK` / `s4d_chainb_selfcheck()`：RAW@`0x12000000` → SW BGR888 预处理 → PL 2B → PS 解码。行811–812 是 DONE_SAFE 轮询及现有 GT 采样，行836 是 `s2a_decode_nms_reference()`；返回后、ACK 段之前已有真实 `det[]` 与 `count`。这是直接接入 C2 的窄接缝，不能改成 A 路径的注入张量自检。
2. C2 初始化/API 与写端分别在 `c2_s5_publish.h` 行87–104、`c2_s5_publish.c` 行97–143/191–345。集成需提供 `read_gt_ticks`、flush、DSB callbacks；输出指针使用 `S5_RESULT_BASE=0x20800000`，并将真实 `det[]`、计数、frame id、尺寸传入。C2 适配器最多发布14框，15框必须走既审 fail-closed 错误分支；不得把离线 mock 结果当板上检测。
3. 显示候选的单帧接口 `S5Display_RenderFrameSrc()` 位于 `s5_display_app.c` 行650，公开声明在 `s5_display_app.h` 行216。VTC/VDMA 初始化在 S5 `main()` 行1097 起（VTC 行1154、VDMA 行1182）；S5 真实源解析 `S5Real_Parse()` 位于 `s5_real_source.c` 行46，填 `cap_ticks` 行83，`S5Real_ToFrameInfo()` 行118 起，`cap_ticks==0` 按未知处理见行137–144。S5 自己的 main loop 中安全等待、绘制、flush、乒乓在 `s5_display_app.c` 行1352–1378；没有现成的 init/one-frame service API。
4. 因而最小应用变体要在 S4 的约47秒 PL 等待轮询里增加显示 frame-service hook（初始化 VTC/VDMA、等待 back buffer 安全、render、D-cache flush、切换双缓冲），保持同一 PS 应用继续服务显示；2B 完成后在 decode/ACK 接缝调用 C2 发布，再从真实 C2 结果构造显示信息并绘制真实框。无需重做 R01 吞吐路径或 R06 控制 FSM。该 hook 是新组合代码，不是当前应用已有功能；不能声称已集成。

## 关键语义与部署阻断

### cap 与 infer_done

- 冻结 S5 G0（当前 main HEAD 文件行132）定义 `t_capture_end` 为帧写入 DDR 完成，`t_infer_done` 为 2B `DONE_SAFE`，`t_display_start` 为该结果首次上屏。结果年龄以 `display_start - capture_end` 计；显示延迟以 `display_start - infer_done` 计。
- C2 原计划行67建议 `infer_done_ticks` 在 decoder 成功返回后采 GT；这与冻结 G0 的 DONE_SAFE 事件**不一致，不能照此建议执行**。S4 chain-B 已在状态轮询处观察 DONE_SAFE，并在行812调用 `s4d_gt_ticks()`；集成必须先按有效冻结事件对齐，不能以 decoder 返回时间静默替换。
- 现有 chain-B 自检读取预先放入 `S4D_RAW_BASE` 的 RAW，不含相机/采集完成时间戳；host request 的 `begin_tick_lo/hi`（S4 app 行135、244–246）只在另一预处理配置写入 CSR，chain-B selfcheck 不读取，不能据字段名推断其为 cap。P3B 显示真实源只消费结果块中的 `cap_ticks`，且 0 表示未知；模拟源用计算出的 age 值做画面测试，不是实测 GT。显示 render/start/completion 时间不能冒充采集帧写 DDR 完成事件。需要 DSH 指明可审计的真实 cap 事件及其 GT 取样源；否则真实 capture age 与原卡的 `age_pub`/时序验收受阻。

### previous SID

- C2 `C2Publisher_Init()` 要求 `previous_session_valid=1` 并提供可核验的 `previous_session_id`；缺失时返回 `C2_ERR_PREVIOUS_SESSION_UNKNOWN`，不写 DDR（C2 计划行33，头文件行87–104，C 文件行97–143）。S4 mailbox 当前字段 `session_id` 是本次 host 请求 SID，不是上一 POR SID；未找到持久 previous SID 的存储/读取来源。
- C4 rev4 将产品主张缩到“SID 在本会话内恒定、不主张跨 POR 唯一”（C4 行23），但这不会自动改写已审 C2 API。不得用 current SID、DDR 残留或常量伪填 previous SID；未获允许前，初始化和真实板写仍 BLOCKED。

### XSA、BSP 与固定地址

- S5 P3B 头文件给 framebuffer A=`0x20000000`、B=`0x20384000`、结束=`0x20708000`（`s5_display_app.h` 行32–34），结果基址 `0x20800000`（`s5_result_abi.h` 行34）。这些地址均高于 R-16 所列 P3q/P3r lead XSA 声明的 DDR `HIGHADDR=0x1FFFFFFF`（512 MiB）。因此当前 XSA 声明范围与应用固定地址身份不一致。
- main HEAD `35c45778…` 的 STATE 行149–160 同时记录：Stage4/2B XSA 为1 GiB；历史板窗曾用 stage-4 `init.elf` 初始化到1 GiB并运行显示应用。**XSA 的512 MiB 元数据不能单独证明物理 DDR 不可访问**；已有1 GiB init 事实也不能让错误 XSA/BSP 身份自动变成可部署。此次 C2+显示 ELF 仍须绑定匹配的1 GiB display XSA、PS7 init、BSP 与地址映射。待修 P3q `s4d_p3q_ddrfix` 尚未在本核查中取得可部署身份，P3r build5 也不能替代 P3q 显示硬件。
- S5 P3B build record（`D:\codex-worktrees\w4\report\evidence\S5-T01\s5_p3b_sw_20261030_r01\build\build_record.json`；P3B manifest 声明 SHA-256 `f12bc4c318ad373b07e40b22390fb9b26bb7c5f6ef2dcfff67b30d3dbb7c2fa3`，`hash_basis=commit_blob`）记载 GCC 13.4.0、BSP 路径 `D:\codex-worktrees\w4\tmp\4\S4-B-REAL-01\s4b_ps_tensor_20261023_r13\bundle_extract\bundle\workspace\ps7\export\ps7\sw\cpu0`，及 linker script `D:\codex-worktrees\w4\tmp\4\S4-T34\ps_app_build\lscript_s4t34.ld`。BSP 目录确实存在，`xparameters.h` 声明 HIGHADDRESS=`0x3fffffff`。BSP bundle manifest（`D:\codex-worktrees\w4\tmp\4\S4-B-REAL-01\s4b_ps_tensor_20261023_r13\bundle_manifest.json`，SHA-256 `78bcfe1b93667eb8904bf02610fefc58994304f5b40758df82583ae83b6e7a07`，`worktree_disk`）记录 source commit=`03faa2d47a6e49d7475e387cf6b33edda4962c68`、XSA SHA-256=`ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6`，并绑定文件。其 `xparameters.h` SHA-256=`7361be552faffb0b59b37d157c7fe7e332bea52841a17095e2ff7b8c80f04a36`、`bspconfig.h`=`1ff8617a56f0d6d9bdedfe48c2b25a9e0fe4cca26050053a64a2e35be11932d0`、`Xilinx.spec`=`b9273e64cea0f2f99dbd79e2cfcfb5b8357b446a6f1e1f1b8da27faf4036d81d`（均 `worktree_disk`）。该 manifest 标注只覆盖 PS infer/init 离线编译链接输入，不含 BSP 生成器/SDK/PL 重建输入，且不等同于当前 Stage5 显示 XSA 的匹配交付包。linker script SHA-256=`c0350ef1c1ebee0b6b672189c0046a37f6b9d0f90f67cd4dbb66a4224e239048` 亦是 `worktree_disk`。本核查不把该 1 GiB S4-B BSP 单独宣称为可部署包。

## 估时、状态与建议

- **条件估时**：若 DSH 明确真实 cap GT 来源、previous SID 持久来源，按冻结 G0 统一 infer_done 事件，并交付哈希绑定且匹配的1 GiB display XSA/BSP/PS7 init，S4 Chain-B + C2 callbacks + 最小 S5 frame-service hook + 隔离离线验证约需 **0.5–1 工程日**。这是输入齐备后的窄代码估时。
- **原卡整体状态：BLOCKED，不能保证 ≤1 天。** 原卡还需真实板上写 `0x20800000`、显示真实框、box_crc 与应用一致、`age_pub≤200 ms`、state 正确。当前 previous SID、真实 cap GT、infer_done 事件对齐、rev4 源绑定及匹配 display XSA/BSP/PS7 init 均未闭合；R-16 的 P3q 修正版与板窗也未就绪。没有新的板上证据，不能声称这些标准通过。
- 建议 DSH 按原卡做最小组合兜底，只接 S4 Chain-B、已审 C2 发布器与 S5 单帧 renderer/轮询服务钩子，不扩大为新架构。若上述输入未能在时限内补齐，交付限于明确标注 BLOCKED 的隔离源码/离线结果和板验计划，不降低判据。

## 核验命令与未执行项

- 只读核对：`git rev-parse HEAD`、固定 commit 下 `git cat-file blob`/`git rev-parse <commit>:<path>`、路径限定 `git status --short`、PowerShell `Get-FileHash -Algorithm SHA256`、`rg -n`、`Get-Content -Encoding utf8`。
- w6 的 C2 路径限定 `git status --short -- legacy_codex_20261031/c2` 无输出；w4 的 S4 源文件对应路径无未提交差异。对相关源码/状态/manifest 按上表锁定身份。
- 未运行任何测试、编译、板卡、XSDB、Vivado；未创建 ELF 或测试证据，未检查/宣称硬件结果。C2 主机测试记录引用 C2 计划中的既有证据，本核查没有重跑。
