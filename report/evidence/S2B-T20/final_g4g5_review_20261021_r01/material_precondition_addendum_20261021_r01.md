# 2B 板级前置资料与历史 DDR 探针补充核查

日期：2026-10-21（UTC+8）  
范围：只读核查阶段计划、AX7Z020 手册引用、R04 PS 配置证据和 2026-10-17 R02 DDR 探针；未操作硬件、未改代码/STATE/HEAD。  
结论：**有限 DDR 写读前置有真实零错观测；完整前置文档链尚不能据现有审计包判为闭合。**

## 规范与身份边界

`docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md` 第 70 行要求：重新上电并下载/启动；PS UART 输出可辨认信息并记录串口端口/参数；在明确安全范围的 DDR 地址做写入/读回并记录模式、次数、零不匹配；同时核实所用引脚、电平、时钟与资料页码。文本没有要求 DDR 前置必须绑定后续应用的同一个 ELF 或 bitstream，也没有要求整片 DDR 扫描。

用户已明确器件订货型号 `XC7Z020-2CLG400I`，DDR 采用 AX7Z020 手册候选 `MT41K256M16TW-107`；本核查按此边界，不要求厂家再次确认，不外推为实装颗粒解码。板上观察 `D9PSK` 与 PCB 修订仍未知，保留为实物身份限制，不作为本项额外阻断。

## 已满足的有限观测

- `S2B-T19/cache_probe_execution_20261017_r02/visibility_probe_result.json` 记录 `API_OBSERVATIONS_SAVED_ACCEPTANCE_PENDING`，两种方向/模式各 256 B，地址 `0x10000000`，seed 为 `722665479` 和 `722665480`，结果 `CROSS_MASTER_256_BYTES_MATCHED`。原始两相 UART 记录与结果文件在同 RunId 下；`input_config.json` 绑定 init ELF、app ELF、XSA、bitstream 的精确路径和 SHA。独立 `ddr_prior_probe_review_20261021_r01` 仅对 CPU↔DAP/256 B/两相/零错作限定范围 PASS。其 `cold_lifecycle_proven=false`、状态仍待 acceptance，不得扩写成冷上电、全 DDR/HP0 或阶段通过。
- 该探针发生于 2026-10-17 02:12 UTC+8，早于 2026-10-18 的模型资格运行。故它可支持“先完成受限安全 DDR 写读后再开始模型压力运行”的时序要求；阶段计划没有要求与后来重建 R04 app 的 ELF/bit 完全相同。R04 当前 app 若另行运行缓存/DDR 探针，只绑定 R04 身份，不能改写或倒填 10-17 记录。
- 同一 R02 输入记录标出 CP210x `COM4`；结果记录端口参数为 115200、8N1、无硬件流控，并保存了可辨认 `S2B-INFERENCE/1 READY` banner 与 UART 原始收发材料。此项支持 UART 功能和所记录串口参数，不单独证明 PCB 走线/电压。
- R04 `ps7_readback.tcldict` 的 requested/actual 对照一致：PS crystal 请求 33.333333 MHz，UART1/MIO48..49、MIO48/49 LVCMOS 1.8 V，DDR 候选/32-bit bus/16-bit device/533.333333 MHz；R04 HWH/init 与 T15 rebuild 记录绑定配置。该证据说明实际构建配置，不等价于示波器时钟实测或实物引脚/电平测量。

## 文档页码审计结果与最小缺项

- 当前 AX7Z020 手册 SHA `7d9e34045501637bc6277f7ad372f168165fc6969c640092909f1317b10ccedf`。T04 `board/ps_platform.md` 将第 8 页用于 AC7Z020/器件，第 12 页用于 U8/U9、`MT41K256M16TW-107`、2×16-bit/32-bit、1 GB 与 533 MHz，第 13 页为器件照片；本轮实际读取的 `source_manual/document.md` 同样仅抽取了第 6、8、12、13 页。T19 `volatile_pl_program.../programming_record.json` 另列了当前手册页 `[6,9,11,12,13,14,15]` 并记录过有限独立 board-mapping review，但该 review 的范围是“支持本轮易失 PL 测试候选”；没有留下页码分别对应 PS_CLK、UART 物理连线和电压的可审计映射。旧 `AX7020 V2.2` 字段表中 page 14/15/26 的映射不能替代这份当前 AX7Z020 手册的页证据。
- 因此，DDR 型号/配置候选和配置内时钟参数有来源及精确读回；UART 实际收发与串口设置有运行记录。但阶段计划明列的“所用引脚、电平、时钟和资料页码”整体链条，当前包未把当前手册对应页与 R04 的 PS_CLK、UART MIO/电平逐项相连。此为**最小文档闭合项**，不是要求新增硬件测试，也不要求确认实际 PCB 修订或解码 `D9PSK`。
- 最小补充：一张短页码映射表，注明当前手册 SHA 与精确印刷页/图号，逐项映射 PS_CLK 频率/源、UART1 MIO48/49 到板上 USB-UART 路径及信号电平，并引用 R04 `ps7_readback.tcldict`/T15 init-HWH 的实际配置值；注明板卡 PCB 修订与实装 DDR 未确认。若当前手册没有足够页内容，则明确把手册支持范围限定为候选，按已有正式原理图/实物资料来源补齐其余项。无需重复历史 DDR 探针。

## 对阶段验收的影响

历史 10-17 R02 提供有限 DDR 写读前置观测，不能单独关闭完整 2B 前置。R04 当前正式恢复/验收还须以其自身实际 PS init、UART 记录及用户规定的上电/下载启动流程留存新结果；R02 的 `cold_lifecycle_proven=false` 不可借用作 R04 冷上电证据。本文不判 G3/G4/G5 通过。
