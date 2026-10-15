# S2B-T04 PS7 DDR 暂定离线候选

版本：`s2b-ps-platform/1.0.2`。目标器件输入为 `XC7Z020-2CLG400I`，Vivado part 为 `xc7z020clg400-2`。本版只将用户授权的 `MT41K256M16TW-107` 暂作 PS7 DDR 配置输入；它仍是离线候选，不证明当前实板装配、PCB 版次、电源或时序适配。

## R03 候选配置

`vivado/s2b_ps_platform.tcl` 的 `requested` 返回映射现显式请求 `CONFIG.PCW_UIPARAM_DDR_PARTNO {MT41K256M16TW-107}`。几何、频率和状态同时记录在 `ps_platform_fields.json` 的 `active_ddr_candidate` 中。配置内容如下：

| 项目 | 暂定候选 | 依据与边界 |
|---|---:|---|
| PS7 `PARTNO` | `MT41K256M16TW-107` | 用户授权的临时输入；不是实物丝印确认 |
| DRAM 技术族 | DDR3L | Micron MT41K 产品资料 |
| PS7 `MEMORY_TYPE` 枚举 | `DDR 3` | Vivado PS7 的配置枚举；与 DDR3L 技术族分开记录 |
| 颗粒数与单颗位宽 | 2 × 16 bit | AX7Z020 开发板手册第 12 页的 U8/U9 记录 |
| 单颗容量与总容量 | 4 Gbit；合计 1 GB | 256M × 16 bit × 两颗；手册给出 1 GB，Micron 目录列 `32 Meg x 16 x 8 banks` |
| PS7 几何输入 | 行 15、列 10、8 banks（Bank 地址 3 bit） | R02 PS7 对 MT41K 型号的离线读回；与 Micron 32 Meg ×16 ×8 banks 的组织匹配。R03 本身没有 Vivado 读回 |
| 请求 DDR 时钟 | 533.333333 MHz | 手册第 12 页的建议值；此项不代表时序通过 |
| CL/CWL、tAA/tRCD/tRP 等 | 未设置 | 精确器件时序表与 PS7 profile 对应关系仍为 **BLOCKED** |
| 板级走线延时与电源 | 未设置/未知 | PCB 版次、走线延时、VDD/VDDQ/VTT 尚未实物确认或测量 |

AX7Z020 用户手册 SHA-256 为 `7d9e34045501637bc6277f7ad372f168165fc6969c640092909f1317b10ccedf`：第 8 页标记 AC7Z020 核心板及 `XC7Z020-2CLG400I`；第 12 页记载 U8/U9、`MT41K256M16TW-107`、双颗 16-bit、32-bit 总线、1 GB 和 533 MHz/1066 Mbps 建议；第 13 页为芯片照片。该手册未证明当前板卡的实装料号或 PCB 版次。

Micron 产品目录将 MT41K256M16 列为 `32 Meg x 16 x 8 banks`，用于核对容量与 Bank 组织：[MT41K256M16TW 产品目录](https://www.micron.com/products/memory/dram-components/ddr3-sdram/part-catalog/part-detail/mt41k256m16tw)。`MT41K256M16TW-107-M-P` 页面含扩展后缀规格；其 1.35 V、933 MHz、CL13 等数据不转用于本次裸料号输入：[扩展后缀产品目录](https://www.micron.com/products/memory/dram-components/ddr3-sdram/part-catalog/part-detail/mt41k256m16tw-107-m-p)。上述页面于 2026-10-16 查阅。当前未取得可用于 `MT41K256M16TW-107` 的精确厂家时序表，因此不判定 533.333 MHz 下的时序兼容性。

AMD 文档说明 Zynq-7000 PS DDR 控制器可配置 DDR3/DDR3L：[UG585 DDR Controller](https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/DDR-Controller)。UG933 提供 PS DDR 的通用 VCCO 和 PCB 设计指导：[UG933 Zynq PCB Design Guide](https://docs.amd.com/api/khub/documents/emfVNNoDnc5paYCtwGzwPg/content)。这些资料不替代当前板卡电源实测或原理图版次绑定。

R02 `report/evidence/S2B-T04/ps_platform_mt41k_provisional_20261015_r02/candidate_readback.tcldict` 的 SHA-256 为 `5FE5A32103B6BEED8EF984665D0270DA3F19E060B0389BB46B4B728AEFF00CB0`。它记录 Vivado 2026.1 对 MT41K 候选的属性读回，仅供本版静态交叉核对；不是本次源码配置的重新运行结果，也不是时序、电源或硬件资格证明。R02 的 CL/CWL 和 timing 属性仍需精确器件时序表独立核验。

## 旧记录与兼容性

`ps_platform_fields.json` 中原 `fields`、`review_state` 与 `candidate_artifacts` 条目仍保留 2026-10-08 R2 的历史信息，其中旧配置曾用 Hynix `H5TQ4G63AFR-PBC` 与 PS7 profile `MT41J256M16 RE-125`。这些条目不再表示当前活动 DDR 候选；R03 的机器可读字段以 `active_ddr_candidate` 为准。旧 R2 证据没有改写。

JSON 保持 `schema_version: 1`，通过新增可选 `active_ddr_candidate` 与 `historical_field_scope` 表达暂定状态；仓库内未发现直接解析该字段表业务字段的消费者。`verification/check_s2b_inference_platform.py` 会把当前字段表和 Tcl 哈希绑定到可见性证明；旧证明仍绑定先前源码，后续使用前需更新并复审。本任务仅运行静态模式，不宣称旧证明适用于 R03。

本次没有启动 Vivado，没有生成/接受 XSA 或 bitstream，没有初始化 PS/DDR，没有连接或操作板卡。硬件执行为 `NOT_RUN`；实物料号、PCB 版次和电源状态未确认；时序兼容性 `BLOCKED`。本记录不关闭 DDR G0/G3，也不构成 2B G4/G5 通过。
