---
task_id: S2B-T01
run_id: vendor_manual_audit_20261008_r01
status: BLOCKED
updated: 2026-10-08
timezone: UTC+8
---

# S2B-T01 板卡身份与厂商资料交叉核验

## 结论

阶段 0 已接受 `D:\FPGA\AX7Z020\AX7Z020` 中的 AX7Z020/AX7020 资料作为当前板卡资料，并明确其 DDR、UART 等信息作为后续工程依据；本次保留该接受结论。当前仍缺少把手册中的具体 PS/DDR/UART 字段逐项对应到 `AX701020.3.0` 实板的可复核证据，不能直接复用整套旧 PS/DDR 配置。手册第 11 页写明 `XC7Z020-2CLG400I`，正式实板记录为 `XA7Z020`；这一差异需要核查，但不能单独证明手册不适用。

当前干净基线 XPR 仍为 `xc7z020clg400-2`。总控只读核对的原目录用户 XPR 已改为 `xa7z020clg400-1I`，另含增量 DCP 与仿真 FileSet 改动；其差异保存在 `original_xpr.diff`，没有移植到本工作树。本次没有选择实板 PS/DDR 参数、引脚、电平或执行实物操作。阶段 2B G0 仍为 `BLOCKED`；资料审计、包装检查和实物验收分别判断。

## 基线与来源

- 工作树：`C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition`；分支：`codex/stage2b-t01-board-audit`；基线提交：`e433a081bc5f42a44ddec18b421f651d05e9c639`。
- 阶段 0 验收记录称开发板为 AX7020、版本为 `AX701020.3.0`，芯片照片标记为 `XA7Z020`、`CLG400`；并接受上述资料来源。照片链接指向 Obsidian Vault，本次没有读取、复制该 Vault 图片，故这里核对的是正式记录，并未重新观察实物。
- 干净基线 `vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr` 的 SHA-256 为 `5da854a65ac54d762484ae02bfb3ca0411e5d9fd2d8e0b29658d667c3017c8f4`，顶层器件字段和 synth/impl run 均为 `xc7z020clg400-2`。
- 总控只读观察的外部来源 `D:\FPGA_Competition\vivado\AX7Z020_Gesture\AX7Z020_Gesture.xpr` SHA-256 为 `9e637bb8a31c8c74cdb703d632282a020875f5623893665719c1bbb5035be1ec`；该目录 HEAD 同为 `e433a081bc5f42a44ddec18b421f651d05e9c639`。相对该 HEAD，Part 改为 `xa7z020clg400-1I`，新增 `rom_controller.dcp` 增量综合检查点并修改三个仿真 FileSet 的 Filter。保留的 `original_xpr.diff` 绑定这次观察；Reviewer 仅审查此记录，不重新读取外部 dirty tree。以上不代表该 XPR 已在本工作树采用或经本次验证通过。
- 厂商原件：`D:\FPGA\AX7Z020\AX7Z020\AX7Z020开发板用户手册.pdf`，SHA-256 `7d9e34045501637bc6277f7ad372f168165fc6969c640092909f1317b10ccedf`，大小 2,535,861 bytes。

## 手册页码核查

页码均为 PDF 页码。手册结构化解析成功，50 页均已提取；使用 `read-pdf-reliably` 1.0.0 / Docling 2.115.0，请求模式 `auto`、实际模式 `text`、OCR 未启用、180 DPI、无解析警告、命令退出码 0。已对第 11、12、17、18、33、34 页图像进行视觉核对，并将这六页原始渲染图、`reader_manifest.json` 和 `reader_status.json` 保存在本证据目录。reader 原始 manifest 中的临时路径保持原样，只作为解析来源记录；其他 44 页渲染图与全文解析属于临时缓存，不是冻结依赖。解析耗时、峰值内存与工具调用总量未测。

| PDF 页 | 手册内容 | 对本板的适用性 |
|---:|---|---|
| 11 | 写明 `XC7Z020-2CLG400I`、工业级、速度等级 `-2`；芯片照片标注 `XC7Z020` 和 `CLG400`。 | 与阶段 0 正式记录的 XA 芯片不一致；不能据此确定实板器件系列或速度等级。 |
| 12 | 两颗 Micron `MT41K256M16TW-107`，每颗 `256M × 16bit`，总容量 1 GB、32-bit 总线，接口接 PS `BANK 502`。 | 未建立该核心板与 `AX701020.3.0` 实板的版本对应；没有给出可供 DDR 测试的安全地址窗口。 |
| 17 | X1 为 PS 提供 33.333333 MHz，信号标为 `PS_CLK_500`。 | 该页本身不能证明实际核心板采用相同振荡器和连接。 |
| 18 | PS 时钟引脚表列 `E7`；PL 50 MHz / `U18` 描述明确指向 `AX7Z010` 底板。 | 需要核查该描述与 AX7Z020/AX7020 实板的对应，未据此选择 `U18` 或冻结时钟条件。 |
| 33 | USB-UART 章节说明 CP2102-GM，图中有 TXS0102 电平转换，信号来自 `BANK 500`。 | 未证明实板使用相同接口电路、电压或 USB-UART 芯片。 |
| 34 | 表列 `UART_RX=PS_MIO49/C12`、`UART_TX=PS_MIO48/B12`。 | 字段与 PCB 版本的对应待核查，尚未形成本板 MIO 配置；该硬件章节未给出串口速率参数。 |

## 仍需的最小证据

补充官方资料定位保存在 `official_lookup.json`。官方搜索索引登记了 AX7020 V3.0 手册，但三个官网直连均返回 HTTP 200 的 gzip HTML 挑战页，未取得产品正文、新版 PDF 或可核验的下载链接；这是资料获取限制。索引中的“V3.0”未被当作与 `AX701020.3.0` 对应的证明。原始 HTTP 响应及补充页 1–3 解析留在该记录列明的临时目录，不是本证据包的冻结依赖，也未删除。

1. 将已接受的资料中的 PS DDR、PS UART、PS 时钟、连接器和电平逐字段核对到 `AX701020.3.0`，保存厂商原理图/手册版本及章节/页码；器件系列和速度等级继续按实物记录及 `-1` 工程基线处理。
2. 平台建成后依据实际 PS DDR 映射、链接器中的代码/栈/堆与保留区布局推导安全 DDR 测试区间，记录边界和不重叠检查。当前无 PS Block Design/Vitis 平台，无法完成该推导；不把硬件手册中的容量当作安全窗口。
3. 依据 PS 软件配置选择 UART 参数，与通信终端保持一致并记录。参数选择属于工程实现；串口实际测试仍受实物操作授权边界约束。

S2A-T01 已冻结 tiny416 模型、检测头布局及 PS 解码/NMS 规则，不能继续将其列为未冻结字段；阶段 2B 仍须核定物理地址映射、AXI/DDR 传输、cache 和缓冲所有权绑定。此审计没有验证 PS Block Design、Vitis 平台、物理 AXI/DMA/cache、一致性、实际 UART/DDR、INT8 检测精度下降、位流或时序。
