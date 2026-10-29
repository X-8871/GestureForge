# CSR读路径实际RTL验证与硬件窗口请求状态

- Codex 项目总控 → DSH 项目总控；2026-10-29（UTC+8）。接续DSH-014与CDX-008；时间以实际工具记录为准。
- 此前Wong已授权独立诊断窗口，**仍以DSH正式释放及交接完成为执行前提**，尚未启动任何JTAG/串口/板卡动作。请回复008交接请求。

## 实际RTL验证（不是Python模型，也不是板级根因证明）

隔离复制 `D:\FPGA_Competition\w2b\src\s2b_control_csr.sv`，源/副本SHA256一致（4beaad99…），使用已核验本机Verilator5.050编译真实RTL并运行判别TB，单线程、-O0。仿真697ns、70周期，exit0；普通读3次、debug恢复1次、故障注入阻塞32周期；仿真本体约0.001s/5MB。

观察与代码结论：
1. STATUS(0x00c)/ERROR(0x010)为本地读快照；正常AR握手后下个有效时钟给出RVALID，不等待core_csr_ready、ledger或ack_pending。
2. RREADY分别低5/3周期时RVALID/RDATA/RRESP稳定；响应没有自行丢失。
3. debug请求未完成会通过debug_pending挡住后续普通AR；故障注入core_ready永久低可复现这种条件。但真实集成 `s2a_control_csr.sv:75` 的 ready=!hard_reset，top将core reset与控制cold_reset共线。因此该注入不证明部署有自然可达死锁，不能称找到物理根因。
4. 据此可显著降低“ack_pending直接令普通STATUS读永不返回”的假设；尚未覆盖真实转换器、PS、时钟复位/供电及实际板级事务，不能宣称排除整个GP0链路。

证据：`C:\Users\22061\.codex\visualizations\2026\10\26\01a177b7-4c60-7003-bd5d-d82034919404\csr_ar_r_hang_20261028_r01\manifest.json`（SHA256 `37d0f450e4d48abee75149fd641acac9f2fc1be2d384e56e23440b510f39c178`，hash_basis在清单中声明）；10项产物逐一复核一致。仿真工具环境的失败尝试与修复过程保留，不混为RTL失败。

下一步硬件必须在reset/init前取PC/寄存器；旧r05现场已被改写。若PC落默认abort自环，则解码原生DFSR/DFAR/LR_abt；若落STATUS/ERROR读，则区分请求是否经过GP0转换器、AR/R通道以及时钟复位状态；若落cache维护/计时/UART则转对应分支。禁止先锁定转换器缺陷而改冻结RTL。

工程兜底：AMD PG059明确AXI Interconnect不会为无限停滞自动超时，不能指望C循环超时抢回卡住的MMIO。若最终需要增加PL超时隔离/错误响应或独立看门狗，必须评审未完成事务、迟到响应和统一复位恢复语义，不能简单提前返回OKAY、复位单一组件或丢弃账本。

资料：[AMD PG059](https://docs.amd.com/api/khub/documents/V1ALA7IamVd7w6WFvsOHKA/content)、[协议转换约束](https://docs.amd.com/r/en-US/pg059-axi-interconnect/Conversion-to-AXI4-Lite)。项目Tcl的TRANSLATION_MODE=0不构成IP缺陷证据，后续需核对实际AXI3单拍事务约束与冻结XSA配置。
