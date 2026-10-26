# task-11 完整 RTL↔网表顺序等价可行性评估

结论：`BLOCKED_NOT_RUN`。本轮只做离线、只读的范围与工具核验；没有运行 RTL 仿真、形式证明、Vivado/xsim、硬件或摄像头，也没有修改 RTL、网表、工程缓存或既有 RunId。现有局部 SOF 转移证明仍有效，但不满足完整 task-11 的顺序等价要求。

## 验收口径与 G0 判断

本工作树没有找到单独的 S3-T05/task-11 正式任务卡或定义完整形式证明边界的规格文件。当前最明确的验收口径来自 `.codex/STATE.md`：task-11 要求完整 RTL↔网表顺序等价；当前为 `NOT_RUN`。STATE 还明确指出，局部证明没有覆盖五个 cut inputs 的生成/复位、18 位 FIFO 写 bundle、2048 深度双时钟 FIFO 状态、CDC 与 INIT/GSR。`t05_offline_closeout_20261024_r01/task11_netlist_crosscheck.md` 将“RTL↔网表等价性”标为未执行；局部证明 README 也把完整等价列为 `NOT_RUN`。

因此高层目标可以辨认，但 G0 所需的完整比较边界、初态关系、双时钟调度/复位假设、状态匹配和覆盖标准没有冻结。本轮不能自行把局部假设扩展成完整证明规格。

## 固定基线和输入身份

- 工作树：`D:\codex-worktrees\dbdf`；分支：`codex/stage3-video`；本轮只读基线 HEAD：`5c6b2034862cc96f4f2f3b9929d874e034ba4af3`。
- 该提交与旧局部证明绑定的提交 `708aafe9a1c6fbd8fbf6606678e81e05fb4284cf` 不同。当前已检查文件哈希，不把旧证明改称在新 HEAD 上执行。
- 本 RunId 证据文件在共享分支后续推进前形成。总控随后提交 `b7fec9a`、`77a2468`（当前 HEAD `77a246809ad064ccb5f741712ca5ea19b3807b72`）；提交路径仅涉及 `.codex/STATE.md`、`board/stage3/README.md` 和 TIMING-36 证据。对 `5c6b203..77a2468` 的 task-11 输入差异核查为空，并在推进后复核补丁、patched RTL 快照、build report、局部证明脚本/结果、OOC 网表和 XCI 哈希均不变。故 manifest 的 `source_commit=5c6b203…` 是本轮开始时固定基线，不是声称当前 HEAD 未变化。
- 在上述固定基线处记录的状态快照含 `.codex/STATE.md` 已修改，以及 `NA/`、`clockInfo.txt`、两个 timing36 新证据目录和 `scripts/stage3_t17/jtag_t17_w1_sr_sample.tcl` 未跟踪；它们均为既有/并行工作内容，本轮未触碰。Git `index.lock` 不存在。后续提交已集成 TIMING-36 两个目录并清理 STATE 的工作区状态；本包不改写该历史快照。
- 补丁 `board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch`：SHA-256 `fd854a622b52c32a43a6770be3f583cce29864a764845c313b623514c91ab2c5`。
- 既有补丁后 RTL 快照 `report/evidence/S3-T05/t05_sof_fix_20261020_r01/patch_verification/expected_patched_alinx_ov5640.v`：SHA-256 `db4857fe2fc8d86aa831bac619ddfc676d076f0114ba2c07988d944f894adce6`。
- OOC 功能网表 `tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/design_1_alinx_ov5640_0_0_synth_1/design_1_alinx_ov5640_0_0_sim_netlist.v`：227006 字节，SHA-256 `7b8f457c1cd5377367b3032369ba72fc5d00ac465629ecd970d6fb7e479b852a`。头部标记 Vivado 2026.1、2026-10-20、器件 `xc7z020clg400-2`，用途为功能仿真网表。
- 同一 OOC 工程 XCI：SHA-256 `5a330509fc2ff1f08c1bd4f602cdc6f3c6d4ac80cdf92e71e848cace56b44db6`，参数 `DEBUG_OV5640=false`、`BUFFER_DEPTH=2048`。RTL 源默认 `BUFFER_DEPTH=4096`，必须按该实例配置建立比较对象。
- 对应 `build_report.json` 的 `status=ok`，但没有 `source_commit` 字段/值；不能据此宣称已绑定 OOC 生成时的完整源码提交。

上述 `tmp/` 输入只绑定路径和哈希，没有复制到本 RunId；证据可重放性取决于该缓存仍保留。

## 现有局部证明覆盖

`task11_sof_local_transition_20261025_r01/` 的输入结果 SHA-256 为 `bdf38aa704df31dd610580602f14182ad7e8704d93b7ccfc76ebf93d549b5a9d`，脚本 SHA-256 为 `4c5305802119d07eb2fe30d17a7b63e54cbfa39098715e34f12df44352594f54`。它对 19 位局部状态和每拍相等的 5 位边界输入穷举 `16777216` 组、比较 `335544320` 位，差异为 0，并核对 30 拍边界轨迹；其 verdict 是 `PASS_SOF_LOCAL_TRANSITION`，而完整 task-11 字段仍为 `NOT_RUN`。

局部证明的匹配初态和相等 cut inputs 是证明假设，不是从完整 RTL 推导出的性质。其边界外至少包括：输入状态生成与复位、18 位 `{data,last,user}` FIFO 写 bundle、两个不相关时钟 `cmos_pclk`/`m_axis_video_aclk` 下的 XPM async FIFO、Gray CDC 与复位同步，以及 INIT/GSR/上电状态。它不能推出整个封装 IP 的行为等价。

## 本机轻量工具核验

在 Windows 命令 PATH 中核对了 Yosys/SymbiYosys/EQY/ABC、AIG/SMT 求解器、iverilog/Verilator/SystemVerilog 前端及模型仿真器；均未找到。常见 OSS CAD Suite 安装路径下的 `yosys.exe` 也不存在。工作区 Python 3.12.14 中 `z3`、`pysmt`、`pyverilog`、`amaranth`、`nmigen`、`cocotb`、`sympy`、`pyeda` 均不可导入。没有适用的完整顺序等价工具链。

检查到的 `vivado-mcp-server` 进程仅为现有 MCP 服务进程；本轮没有调用它们，也没有尝试启动 Vivado。即使存在普通仿真器，仿真或有限轨迹抽样也不能替代需要的顺序等价证明。

## 阻碍与最小缺口

1. **证明工具缺失**：需要由任务负责人提供/批准可用的形式等价引擎及其 Yosys/Xilinx UNISIM、XPM FIFO/CDC 模型支持；按本轮授权不得用 Vivado/xsim 替代或安装/联网获取新工具。
2. **G0 证明契约未冻结**：需正式确认比较对象是完整 `alinx_ov5640` IP 封装及其 OOC `BUFFER_DEPTH=2048`、`DEBUG_OV5640=false` 配置；明确 RTL 端口到网表封装端口（包括 18 位 FIFO 输出 bundle）的映射、初始状态关系、两时钟允许关系、异步复位和 INIT/GSR 假设，以及需覆盖的全部输入与可达状态。
3. **输入版本绑定缺口**：需补齐 OOC 构建使用的源提交/生成记录，并冻结 RTL、XCI、XPM/UNISIM 模型与 netlist 的一组同版输入；现有 build report 没有 `source_commit`。
4. **证明覆盖标准**：需规定全可达状态归纳/等价的通过判据、状态分区与状态映射、反例留存方式；不接受局部 cutpoint、随机仿真或有界采样作为完整证明。

在这些缺口闭合前，任务状态保持 `BLOCKED_NOT_RUN`；不得把本包的文件清单检查通过写成 SEC 通过、task-11 完成或阶段3 G5 通过。

## 已执行命令和退出码

- 基线：`git -C D:\codex-worktrees\dbdf rev-parse HEAD` → `5c6b2034862cc96f4f2f3b9929d874e034ba4af3`，退出码 0；`git status --short` 用于记录并行/既有改动，本轮未改写。
- 输入：PowerShell `Get-FileHash -LiteralPath <精确路径> -Algorithm SHA256` 对补丁、patched RTL 快照、XCI、网表及局部证明材料逐项核对；命令成功，详情见 `result.json`。
- 工具：`Get-Command` 逐项查找候选命令；Python `importlib.util.find_spec` 查找上述模块；退出码均为 0，候选等价/仿真工具均未发现。
- 完整 SEC：未运行（命令为空、退出码为空），因为没有可用引擎且 G0 契约未冻结。
- 证据包装：用 `D:\FPGA_Competition\verification\check_stage_delivery.py --mode evidence` 检查本 RunId 清单；该命令只验证文件/哈希绑定，不验证证明结论。
- 首次证据包装检查因清单漏列本 RunId 的 `source` 角色，并把外部既有 README 错标为 `diagnostic`，返回 `CHECKS_FAILED`、退出码 2；已修正清单角色后重新检查。该失败是包装结构错误，不是 RTL/网表证明结果。
