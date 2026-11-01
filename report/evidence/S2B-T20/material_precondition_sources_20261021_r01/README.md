# 当前 AX7Z020 手册 PS_CLK/UART 页码核查

## 来源与提取

原 PDF：`D:\FPGA\AX7Z020\AX7Z020\AX7Z020开发板用户手册.pdf`，SHA-256 `7d9e34045501637bc6277f7ad372f168165fc6969c640092909f1317b10ccedf`，2,535,861 字节、50 页。原件未改动。

Docling 2.115.0、`read-pdf-reliably` 以 `diagram` 模式生成了 PDF 第 17–20、33–34 页 PNG，页码与页面脚注 `17 / 50` 等一致；`ocr_enabled=false`。页图保存在 `key_pages/`，逐页 SHA 与事实索引在 `board_mapping_facts.json`。全篇结构化文本在 `full_manual_document.md`，工具原始 manifest 为 `full_manual_manifest.json`。初次只提取的第 9、11、14、15 页图仍在 `pages/`，它们不包含待查的 UART/PS_CLK 映射。

## 可直接引用的手册事实

- PDF 第 17 页，图 2-5-1：AC7Z020 核心板 X1 为 PS 提供 33.333333 MHz 有源时钟，连接 BANK500 的 PS_CLK_500。
- PDF 第 18 页：时钟引脚表给出 PS_CLK_500 = E7。
- PDF 第 33 页，图 3-6-1：USB-UART 使用 CP2102-GM，示意路径有 TXS0102 电平转换器；图中 ZYNQ 方块写 BANK500。
- PDF 第 34 页：UART_RX = PS_MIO49/C12；UART_TX = PS_MIO48/B12。
- PDF 第 19 页电源表有内部冲突：+1.8 V 行写 BANK501 IO 电压；+1.5 V 行又写 DDR3、ZYNQ Bank501。因此本页不能独立确定 BANK501 的实装 IO 电压。第 33 页 BANK500 方块标注也需与第 34 页 MIO48/49 表并列注明，不能默默视为一致。

## R04 配置对应

完整 R04 XSA：`D:\FPGA_Competition\w2b\report\evidence\S2B-T19\visibility1_csr_fixed_20261016_r04\artifacts\s2b_inference.xsa`，SHA-256 `ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6`。其 HWH 成员 `s2b_inference.hwh` 已只读解出到本目录，SHA-256 `d4dfd4262e9864f978c17b739d7b90b9a68215f0d46a08d73357bac8e092f868`。HWH 报告 PS crystal 33.333333 MHz、UART1 enabled、MIO48..49、MIO48 out/MIO49 in、两 MIO LVCMOS 1.8 V、BANK1 1.8 V、UART1 base `0xE0001000` 和配置 baud 115200。

`ps7_readback.tcldict` SHA-256 `931132b5fe645c66737c9fd3543812a6cecc906a160fb4c341e7a8d8bf17097e` 显示上述 crystal、UART1/MIO、电平及 DDR 候选的 requested/actual 相同。T15 `build_details.json` 把离线重建状态、XSA SHA 和 HWH 成员元数据绑定；`s2b_ps_init.c` 与 `init.elf` 是离线构建输入，wrapper 调用 `ps7_init()`。这些是 R04 硬件设计配置和软件构建证据，不是对当前物理板卡引脚连线、实际电平/时钟的独立测量。

机器可读字段、逐文件哈希与限制见 `board_mapping_facts.json`。用户已确认订货器件 `XC7Z020-2CLG400I` 和采用手册 DDR 候选 `MT41K256M16TW-107`；本记录不要求厂家确认，不推断实装 DDR。D9PSK 与 PCB 修订仍未知。
