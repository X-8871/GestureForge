# R-03 独立复核：M3 实际窗口与 M4B 离线根因（2026-10-31）

## 结论

**PASS（限于本报告核查的证据诚实性、来源绑定和离线诊断）。** 这不表示 M3 成对取样通过：本轮 M3 实际结果是 **BLOCKED，before/event/after/compare 全部 NOT_RUN**。

## 核查范围与只读边界

- R01：`D:\codex-worktrees\w6\report\evidence\R03-M3\m3_pair_20261031_r01` 的 INCIDENT、setup/close Tcl、对应 stdout/stderr、launcher execution、server Job 收尾及 3 份主机身份快照。
- M4B：`D:\codex-worktrees\w6\report\evidence\R03-M3\m4b_rootcause_20261031_r02` 所列 ROOT_CAUSE、analysis、反汇编、历史源码/registration、四份 UART 样本；以及 `D:\codex-worktrees\w6\legacy_codex_20261031\r03\analyze_m4b.py`。
- 未运行 XSDB、Vivado、hw_server 或硬件。仅对已存在的失败 ELF 离线执行 `arm-none-eabi-objdump`，退出码 0。未运行会创建/覆盖 RunId 证据的 `analyze_m4b.py`，未修改待审源或证据。

## R01 实际结果

- setup Tcl 对 `Cortex-A9 MPCore #0` 做唯一目标选择后，记录 `SELECTED_UNIQUE=ARM Cortex-A9 MPCore #0`；下一条真实 stderr 为 `ERROR: CPU_NOT_STOPPED: Running`。源码顺序是在两核状态检查之后才到 `loadhw`、SLCR 写、`fpga`、`dow`；因此本次失败在这些动作前退出。日志未出现任何对应执行标记。`execution.json` 的 `root_exit_code=0` / `PASS_PROCESS_ONLY` 只说明 XSDB 进程层状态；INCIDENT 将该语义失败正确记为 BLOCKED。
- close 日志分别记录两核 `Stopped: (Suspended)` 和 `M3_CLOSE_CORES_STOPPED`。close 与 server launcher 记录显示 Job 清理确认、线程已 join、无超时错误；server 在 `CLOSED_BY_REQUEST` 正常收尾，完成时间 `01:21:08.245793+08:00`，Job 耗时 55.437 秒，进程数归零。post 查询退出 0，hw_server/xsdb/vivado/xsim/vitis 进程与 3121/3122 监听均为空。
- `pre_verified_host_tool_identities.json` 与 `post_host_tool_identities.json` 的 13 项文件路径、字节数及 SHA-256 数组逐项相同；二者的主机查询退出码均为 0，快照均无进程/监听。另一个 pre 快照也与之相同。三者时间分别为 01:14:50、01:16:25、01:21:33（UTC+8）。
- **证据限制：** CLAIM 写明开 Job 前还会复核主机空闲状态，但 R01 包内最近的持久化 pre_verified 快照是 01:16:25，未找到 01:20 开 Job 前即时核验的独立记录。总控随后告知：其 01:19:48 在本聊天工具记录中执行了进程名与 3121/3122 监听查询，exit 0、输出 0B、耗时约 1.37 秒；该观测未写入 R01，不能作为包内持久化证据。故本复核保留上述证据缺口，不伪称它已绑定进 R01；这不改变 setup 读到 Running、失败前未执行后续动作、close 及 post 清理的结论。

## M4B 离线根因

- 被诊断的失败 ELF SHA-256 为 `ada4b30d98298ec9cea053d97d01e9fea91ae97e70c8a13f7be1bc36079445a7`，与失败窗口身份记录一致。对该 ELF 的反汇编在 `0x103664/0x10366c` 形成 `r4=0x43c00000`，`0x103738` 置 `r2=400 (0x190)`，`0x10373c` 和 `0x103744` 分别写 `[r4,#40]` / `[r4,#44]`。所以此 ELF 的 core/drain timeout 是 400 周期，即按 50 MHz 计算 8 微秒；这纠正了旧 r01 的粗略 timeout 说法。
- 失败 UART 结果为 `done=2/error=5/pass=0`，包含 `STEP=7 compare heads (done=2)`，没有实际 `M4B HEADS diff13=...` 行。对应固定源码 commit `6c09df12c585568b2737da2116fe43913e0062cb` 的 `s4d_m4b_selfcheck` 将 d13/d26 初始化为 0，且只在 `done==1` 中做 invalidate/比较并打印 HEADS 行；ELF 控制流的失败路径 `0x103904→0x103814` 返回结果输出，未进入 `0x103954` 开始的 invalidate/比较路径。因此失败样本中 diff=0 的正确含义是**未计算**，不是实测相等。
- 三份成功 UART 均是独立的历史样本：各自有真实 HEADS 行、`pass=1/done=1/error=0/diff13=0/diff26=0`，elapsed 均 47,287 ms。它们不能算成本轮新采样。
- 独立哈希复核：历史源码副本 SHA 与 analysis 的 `source_sha256` 相同（`c07c26f7…b6a1d0b`）；registration 副本与原件相同；失败及 3 份成功样本副本逐份与 analysis 所指原始日志 SHA 相同；失败 ELF 文件 SHA 与 analysis 一致。analysis 同时保留未执行、历史样本及未排除历史 6-bit 变化原因等限制。
- `analyze_m4b.py` 只读取固定源码 commit、旧 ELF、registration 与历史日志，并调用离线 objdump；会创建指定 R02 RunId 且拒绝覆盖已存在目录。此复核未运行它。其“其他旧 ELF 为 `0x40000000`”说明在本审查中未另行绑定并复核那一不同 ELF；本结论只确认 SHA `ada4b30d…` 的失败 ELF 为 400 周期。

## 关键复核命令

- PowerShell 只读解析快照并比较 identity 数组、读取日志及 JSON、SHA-256 文件哈希：退出码 0。
- 对失败 ELF 运行 `arm-none-eabi-objdump -d --disassemble=s4d_m4b_selfcheck <精确失败ELF路径>`：退出码 0；关键指令地址和分支已与保存的 `old_elf_disassembly.txt` 交叉核对。
- 未运行自动化测试；本项是证据与静态/离线诊断审查。

## 最终判定边界

R01 安全失败与收尾证据、M4B 的 400 周期及“失败 diff 零为未执行比较”诊断相互一致，故以上限定范围 **PASS**。M3 的 before/event/after 读数不存在，不能宣称本轮硬件测量通过；本报告也不推断历史 6-bit 变化原因或不同 SHA ELF 的 timeout。