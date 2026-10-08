# S2B-T04 PS-only UART/DDR 离线候选

版本：`s2b-ps-platform/1.0.0`。候选目标为 `xc7z020clg400-2`，依 Wong 最新选择及目标决策提交 `4b6fcfcfb41d9647d043dd62ad5329d60799a19e`。本轮源码基线为 `f68dbf11618c4b9b38ab7993a5c033537c90a88b`；新增脚本/字段实际 SHA 以运行清单为准。XA 丝印照片与厂商 XC 答复的冲突仍需部署前核实。

## 范围与依据

本工具创建一个 PS7 BD，外部化 `DDR`/`FIXED_IO`，关闭 GP/HP/ACP、PL FCLK 和复位端口。未引入模型、网络计算、PL AXI、XDC、Vitis 或硬件操作。候选参数逐项来源、旧例程行号、真实默认值及当前 readback 见 `ps_platform_fields.json`，不据此冻结 UART wire 协议或 DDR 安全窗口。

| 字段 | 候选与实测读回 | 厂商依据 |
|---|---|---|
| PS 晶振 | 33.333333 MHz，E7/BANK500；BANK500 3.3V | V2.2 PDF14–15 §5.1、图5-1；旧 Tcl227/719 |
| UART1 | TX MIO48/B12，RX MIO49/C12，BANK501 1.8V，地址 E0001000..E0001FFF | V2.2 PDF26 引脚表/图6-8；旧 Tcl719–720/837–845 |
| DDR 容量 | 2×16bit，合计 32bit/1GB，行15/列10/Bank3 | V2.2 PDF17–18 §6.2；旧 Tcl850/856/871/873/902/909 |
| DDR 颗粒/profile | 手册 H5TQ4G63AFR-PBC；兼容 profile MT41J256M16 RE-125 | V2.2 PDF17 §6.2 明确兼容；旧 Tcl908 |
| DDR 时钟/时序 | 请求 533.333333 MHz，实际 533.333374 MHz；CL7/CWL6/DDR3_1066F | 旧 Tcl847/857/872/905/910，Vivado2026.1 当前 profile 读回 |
| 板级延时候选 | 各 lane 0.25ns board delay、0ns DQS-to-clock | 旧 Tcl852–855/886–889；未实测 PCB，不作为校准值 |
| 当前封装延时 | 0.089/0.075/0.085/0.092；DQS-to-clock -0.025/0.014/-0.009/-0.033 | 由当前 XC/-2 与 Vivado2026.1 派生，未复制旧 Tcl704–711 |

原件 SHA 与准确原件路径见字段表的 `sources`。厂商 2017.4 例程原件位于 `D:/FPGA/AX7Z020/AX7Z020/course_s2_sdk/01_ps_uart/ps_uart.srcs/sources_1/bd/top/hw_handoff/top_bd.tcl`。V2.2 原件由 Wong 提供，所需原页渲染与解析记录保存到本次 `source_proof`。

保留资料缺陷：V2.2 PDF18 表6-1 的厂家 `micron` 与 PDF17 的 SK hynix 相冲突；旧 AC7 的 -PBI/MT41K-107 不作为新版实物颗粒依据。新版 Micro-USB/J7 与旧非B底板 MINI_USB/位号有差异，需按实际 PCB 核对。

## 已生成的候选

主交付是 `report/evidence/S2B-T04/ps_platform_20261008_r01/rebuild_attempt4/` 的 BD/XSA，来自完整新目录重建，退出 0。前两轮原始错误/计数诊断包原样保留；顶层早期 XSA 仅用于失败诊断，不作为下游绑定版本。

- `s2b_ps_only.xsa`：无位流硬件描述，SHA `7960a1a814b1260950ca3812b55959fb0b58694c4484e287ba836ef30f4dd7d7`。
- `s2b_ps_only.bd`：已强制验证的原始 BD，SHA `0d02803271faaafbd4bb795ae8f1f15fc09d35ef1b6647dca3ee3710711f59db`。
- `readback.tsv`/`interfaces.tcldict`：50 项请求和23项派生读回，仅一个 PS7 单元、两条外部接口。
- XSA 内的 `ps7_init.*`：候选 PS 初始化数据；另行保留 C/H/Tcl 供下游检查和复核，未在硬件运行。

真实 DDR 连接宽度按 BD `port_maps` 的 DQ[31:0]、ADDR[14:0]、BA[2:0]及 wrapper/HWH 核验。通用 DDR 外部接口模板保留 DATA_WIDTH=8、CAS_LATENCY=11 等默认 metadata，它们不代表 PS7 的实际总线或时序；实际 PS7 配置/HWH 是 32Bit、CL7/CWL6。

## 重建入口

使用空闲且归属明确的 Vivado2026.1 Tcl 会话。`PROJECT_NEW`、`EVIDENCE_NEW` 均须为绝对字面路径、精确父目录存在且目标不存在；不能指向既有运行目录。复建预计约一分钟，无综合/实现。保留原生日志和 capture 原始日志，ERROR/CRITICAL WARNING、配置回退或 capture 再次失败即停止。

```tcl
source -notrace {C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition/vivado/s2b_ps_platform.tcl}
puts [::s2b_ps_platform::run {PROJECT_NEW} {EVIDENCE_NEW} {IPCFG_LIBRARY} {NATIVE_LOG_EXACT}]
```

`IPCFG_LIBRARY` 为已安装 ROSS `vivado-ip-configurator/lib/ipcfg.tcl` 的精确路径；`NATIVE_LOG_EXACT` 必须来自该会话启动记录。脚本在打开 BD 后只首次加载 helper，预检 Vivado Python、分阶段 capture。实际已核验的调用参数保留在 `vivado_calls.json`，不要把示例占位词当作文件路径。

Vivado2026.1 在 `generate_target` 期间会重排普通警告历史，ROSS capture 可报告 WARNING 计数变化。脚本只在本次 Tcl 成功、0 ERROR/CRITICAL 且失败原因精确为该计数变化时，对输出生成进行一次新文件复验；失败原包保留，复验仍须严格 OK。主运行 force-validate 原生区间保留两条 `BD 5-700/5-699` 警告：PS-only 未启用 PL AXI，因此没有相应 PL 地址空间和地址段。计数器额外显示7条历史普通警告，完整 before/after 日志保留，未隐藏或清零消息。

恢复现有候选只读检查时，工程位于 `tmp/2B/S2B-T04/ps_platform_20261008_r01/final_project/s2b_ps_candidate.xpr`；这不是重新运行 `run` 的目录。完整重建必须选择新的工程和证据子目录，不能 `-force` 覆盖旧 RunId。

## 验收边界

自动产物检查及包装检查只覆盖文件完整性、源绑定、配置和结构。115200/8N1 为后续软件任务，DDR 延时训练和稳定性、PCB/丝印、UART 接线、缓存一致性和可用内存窗口仍未作实物验证。G3 对本离线候选不适用；阶段2B整网上板 G0/G3、1000连续任务均未完成。本任务没有模型冻结接口依赖，清单使用明确的不适用说明，不伪造 frozen 模型字段。
