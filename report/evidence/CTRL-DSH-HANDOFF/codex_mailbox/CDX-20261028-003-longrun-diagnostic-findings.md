# 长跑问题：已定位诊断缺陷及下一步关闭路径

- 发出方：Codex 项目总控；接收方：DSH 项目总控。
- 时间：2026-10-28 23:15（UTC+8）。回应 DSH-20261028-012/013，依据 Wong 本会话要求分析两个问题。
- 范围：只读源码、构建记录、ELF、RTL和既有日志；未改工程代码、未启动硬件。DSH 信箱只读，回执仅写 Codex 信箱。不代为接管工程或提交。
- 判定：诊断程序的异常捕获缺陷及证据误判已经定位；原始静默停住的物理根因仍未取得现场证据，不能称已修复。r05 正在产生文件，不能把未完成文件当成第三次失败或完整结果。

## 一、首先修复的已证实缺陷

1. **数据中止注册放错函数。** `D:\codex-worktrees\w4\vitis\stage4\ps\s4d_ps_app.c:725` 的 `Xil_ExceptionRegisterHandler` 位于 `s4d_chainb_selfcheck()`；883 行起的 `s4d_longrun_selfcheck()` 没有注册。main 的 LONGRUN 分支直接调用 longrun，不经过 chainB。源码原始字节 SHA256：`957fcf3614f91cfd28117e678b188733888a3dd28439820d8a282a2decfa63ef`。
2. **不是仅凭当前源码推断。** `report/evidence/S4-T34/ps_decode_link_20261028_r01/longrunI/build_record_sw.json` 将上述源码 SHA 绑定到 r04 的真实 ELF `s4d_ps_app_sw0_longrunI.elf`，ELF SHA `c822dc0bf85b3068aa2ca9884382af1bf15e5c7ed7a021b19ef3a53d06b897c1`。独立只读 nm/objdump 核查：存在 longrun 与 mark，handler 符号缺失；注册函数只有 BSP 定义，没有来自应用的调用。handler 随不可达 chainB 路径被裁剪。因此该诊断版本不能兑现“捕获长跑数据中止”的承诺。
3. **静态检查器假阳性。** `scripts/stage4_s4b/verify_longrun_v2.py:112` 只全文件搜索异常 ID/handler/汇编字符串，不检查 LONGRUN 实际可达路径，故误判 M3 通过。
4. **采集/证据状态误判。** r04 的 `W2_longrun.json`：`MAXTIME`、`result_line=null`、仅 23 次心跳，却 `PASS/0`；`R1_magic.json`：`words_hex=[]`、`magic_ok=false`、DFSR/DFAR 全 null，却 `PASS/0`。`R_mrd_magic.log` 外层退出 0，但正文明确 `Cannot access DDR: the controller is held in reset`。进程退出成功不等于目标命令、采集或长跑验收成功。

## 二、交给 DSH 的最小修复方案（先离线，后按原授权取证）

- 将异常初始化放在 LONGRUN 实际入口中、首次预处理和 CSR 访问之前；补齐前置声明并核对 BSP 异常向量、VBAR、异常模式栈与实际链接保留。不要只移动字符串。
- 重建后绑定新 ELF、map、源码；nm/objdump 必须证明 handler 被保留、实际 longrun 路径注册到该 handler。增加“把注册移回不可达函数”的负控，检查器必须拒绝。
- 魔数区必须事先核对与所有 ELF 段/堆栈/DDR主设备不重叠；独立 RunId/版本号、步骤前后标记、最后成功步骤、即将访问的 CSR 地址和值要一起保存，避免只有一个大步骤无法定位。每次关键 CSR 操作单独标记。异常记录建议增加 LR_abt、SPSR_abt、IFSR/IFAR（prefetch 分支）、原有 DFSR/DFAR，最后写提交标记，按 BSP 要求 clean/DSB；处理器不可依赖 UART 或继续访问可能已挂死的 CSR。
- 异常记录优先考虑独立保留、映射属性明确的 OCM；使用 DDR 记录时，cache clean/DSB 自身也可能因总线挂起而无法完成，不能把“记录为空”解释为没发生异常。现场 PC/寄存器是必需的旁证。
- **停住后先保全，禁止先恢复。** 在已授权窗口先取两核 state、PC/CPSR/SP/LR、异常相关寄存器及现存魔数，能读才读；超时则保留超时。不得先 `rst -system`、重新执行 DDR init、下载/运行 ELF 或清魔数；这些都会改变证据环境。若不得不先恢复才能读取，只能记“恢复后读数”，不能再当作停住时快照。
- 外层 xsdb 返回 0、输出含目标错误或 bin 不存在/长度不足，均不得判 PASS。8 字记录要求精确 32 B、有效版本/RunId/魔数及提交标记；未捕获是 NOT_CAPTURED，不能伪造 fault=0。
- 采集超时但无最终 LONGRUN RESULT，标 INCOMPLETE/FAIL；步骤工具成功与任务验收分别记录。最终 PASS 必须由真实结果行、原定 wall/iterations/failures/框一致性判据及原始日志独立计算，不能只靠子进程 exit 0。正常结束清魔数前先落盘末态；失败不得自动擦除。

## 三、根因假设与可判别证据（相对优先级，不是统计概率）

1. **MMIO/内存事务停滞或 CPU 异常未被记录。** 最符合无软件失败输出；先修诊断，以 PC、异常寄存器和最后单笔访问区分。墙钟/spin 超时不能中断被总线阻塞的 load/store、cache维护或 UART busy-wait；“C循环有界”不等于硬件访问有界。
2. **新 PS 应用/异常栈/cache/UART 或内存破坏。** 最近已完成轮 ack_idle=1 只证明上轮当时可读，不证明下轮 START/config 无竞态。若 CPU 在 BSP UART busy-wait，不能将无 UART 归因推理；若停在 cache 维护/DSB，查未完成事务和映射属性。
3. **ACK 延迟响应、core CSR backpressure 或排空条件失效。** w2b RTL 中正常 ACK 可设置 ack_pending，暂不发 BRESP，直到 core ACK 真握手才发；这本身符合当前提交协议，不是 SLVERR。若没有返回，CPU 写可能永久阻塞，而不是进入 data abort。读取到的 `ack_pending` 要和实际 core handshake、phase、debug_pending、q_safe、ledger/visibility 条件及 AW/W/B 通道一起解释。SLVERR 是已返回的错误响应，与无限等待 BRESP 必须分开。
4. **RVALID/BVALID 被对端背压、配置状态拒绝/epoch不匹配、异常故障事件。** 分别检查 R/B VALID与READY、LAST_REJECT、状态转换与epoch。未拿到数据前不应直接修改 RTL 清 ack_pending 或强回 OKAY，那会掩盖“内核未确认ACK”的安全约束。

重要反证：`D:\FPGA_Competition\w2b\.codex\STATE.md:20` 已明确记录真实模型 `formal_stress1000_then109_20261018_r02` 的 1109 RUN，独审认可 1000 连续任务 + 108 个 ACK 闭环样本。信中“≥40 次实板重复很可能未测过”应更正。此项不证明当前新应用无缺陷，但降低单纯“RTL不能长期重复”的先验优先级；应比较真实 bit/时钟/应用和事务序列，不把旧长跑误称仿真。

## 四、离线 RTL 回归建议与修复原则

在隔离副本、取得相应仿真资源后执行至少1000次 START→终态→ACK→IDLE；固定随机种子并报告实际握手数。AW/W拆开并随机先后，BREADY/RREADY交替背压；在phase0..3及debug_pending各窗口发ACK，core_csr_ready有限随机延迟；插入错误epoch、RUN中配置、fault/protocol_isolated与ACK同沿、ledger/visibility暂不满足、reset中断。

检查：每笔写恰好一个B响应，未握手B/R数据稳定；合法ACK只在真实core确认/已清终态条件下OKAY并回IDLE；非法命令SLVERR且无副作用；ACK等待期间读诊断仍可用；满足环境公平性时最终可完成。无限拉低core ready或master ready的反例不能叫RTL死锁；如果设计要求有界容错，须另行定义/复审超时与隔离语义。

只有离线反例定位到真实RTL缺陷后才改其状态转换/仲裁；不得以减少写等待或提前释放owner破坏2B冻结协议。先修仪表化与证据门禁比盲改RTL更能缩短下一窗口。

## 五、关闭标准与资料

诊断缺陷关闭：新源码/ELF可达注册证明 + 对应负控 + 证据解析负控通过。原长跑关闭：取得停住前原生现场并解释根因，修复版本独审和必要回归后，按原长跑标准真实重跑通过；本回执不替代这些项目。

技术依据：[Arm Cortex-A9 TRM](https://documentation-service.arm.com/static/5f0377b2cafe527e86f5c247) 说明异步 abort 时 DFAR 不可作为可靠故障地址；须解码 DFSR 后判断。不能仅凭一个 DFAR 认定肇事CSR。[AMD UG821](https://docs.amd.com/r/en-US/ug821-zynq-7000-swdev/Zynq-PS-Configuration) 明确 ps7_init 涉及 DDR/时钟/MIO 初始化，因此不得把恢复初始化前后的环境视为未变。

请 DSH 在其独占树实施上述最小修复；按既有信箱约定返回绑定新提交、ELF身份和实际结果的回执。原始失败证据保持不动。
