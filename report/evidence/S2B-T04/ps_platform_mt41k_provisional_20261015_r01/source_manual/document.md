<!-- page: 6 -->

## 一、 开发板简介

在这里，对这款AX7Z020 ZYNQ开发平台进行简单的功能介绍。

开发板的整个结构，继承了我们一贯的核心板+扩展板的模式来设计的。核心板和扩展板 之间使用高速板间连接器连接。

核心板主要由XC7Z020 + 2 个 DDR3 + QSPI FLASH 的最小系统构成，承担 ZYNQ 系 统的高速数据处理和存储的功能， ZYNQ7020和两片DDR3之间的数据位宽为32位，两片 DDR3 容量高达 1GB。ZYNQ7020  采用 Xilinx 公司的 Zynq7000 系列的芯片，型号为 XC7Z020-2CLG400I。ZYNQ7020 芯片可分成处理器系统部分 Processor System（PS）和 可编程逻辑部分Programmable Logic（PL） 。

底板为核心板扩展了丰富的外围接口， 其中包含1路千兆以太网接口、 1路USB2.0 HOST 接口、1路HDMI输出接口、1路SD Card接口、1路UART USB接口、1路SD卡接口、1 路MIPI 接口、2 路 CAN 总线接口、2 路 RS485 总线接口、2 路 AD 输入接口、2 路 40 针的 扩展口和一些按键LED。

下图为整个开发系统的结构示意图：

<!-- image -->

<!-- image -->

<!-- page: 8 -->

## 二、 AC7Z020 核心板

## ( 一 ) 简介

AC7Z020( 核心板型号，下同 )核心板，ZYNQ芯片是基于XILINX公司的ZYNQ7000系列 的XC7Z020-2CLG400I。ZYNQ 芯片的 PS 系统集成了两个 ARM Cortex™-A9 处理器， AMBA®互连，内部存储器，外部存储器接口和外设。ZYNQ芯片的FPGA内部含有丰富的 可编程逻辑单元，DSP和内部RAM。

这款核心板使用了2片Micron公司的MT41K256M16TW-107这款DDR3芯片，每片 DDR 的容量为512MB；2片DDR芯片组合成32bit的数据总线宽度，ZYNQ和DDR3之间 的读写数据时钟频率高达533Mhz；这样的配置，可以满足系统的高带宽的数据处理的需求。

为了和底板连接，这款核心板的2个板对板连接器扩展出了PS端的USB接口，千兆以 太网接口，SD卡接口及其它剩余的MIO口。以及PL端的BANK13, BAN34和BANK35的 几乎所有IO口（122个） ，其中BANK34和BANK35的IO的电平可以通过更换核心板上的 LDO 芯片来修改，满足用户不同电平接口的要求。对于需要大量IO的用户，此核心板将是不 错的选择。而且IO连接部分，ZYNQ芯片到接口之间走线做了等长和差分处理，并且核心板 尺寸仅为35*42（mm） ，对于二次开发来说非常适合。

<!-- image -->

<!-- image -->

<!-- page: 12 -->

<!-- image -->

MT41K256M16TW-107(兼容海力士的H5TQ4G63AFR-PBI）。DDR3 SDRAM的总线宽度 共为32bit。DDR3 SDRAM的最高运行速度可达533MHz(数据速率1066Mbps)。该DDR3存 储系统直接连接到了ZYNQ处理系统（PS）的BANK 502的存储器接口上。DDR3 SDRAM的 具体配置如下表2-3-1所示。

表5-1 DDR3 SDRAM配置

| 位号    | 芯片型号              | 容量           | 厂家     |
|-------|-------------------|--------------|--------|
| U8,U9 | MT41K256M16TW-107 | 256M x 16bit | Micron |

DDR3 的硬件设计需要严格考虑信号完整性，我们在电路设计和 PCB 设计的时候已经充 分考虑了匹配电阻/终端电阻,走线阻抗控制， 走线等长控制，   保证DDR3的高速稳定的工作。 DDR3 DRAM 的硬件连接方式如图2-3-1所示:

图2-3-1 DDR3 DRAM原理图部分

<!-- image -->

图2-3-2 为 DDR3 DRAM 实物图

<!-- page: 13 -->

图2-3-2 DDR3 DRAM 实物图

<!-- image -->

<!-- image -->

## DDR3 DRAM 引脚分配：

| 信号名称              | ZYNQ引脚名   | ZYNQ引脚号     |
|-------------------|-----------|-------------|
| PS_DDR_DQS_P0_502 | C2        | DDR3_DQS0_P |
| PS_DDR_DQS_N0_502 | B2        | DDR3_DQS0_N |
| PS_DDR_DQS_P1_502 | G2        | DDR3_DQS1_P |
| PS_DDR_DQS_N1_502 | F2        | DDR3_DQS1_N |
| PS_DDR_DQS_P2_502 | R2        | DDR3_DQS2_P |
| PS_DDR_DQS_N2_502 | T2        | DDR3_DQS2_N |
| PS_DDR_DQS_P3_502 | W5        | DDR3_DQS3_P |
| PS_DDR_DQS_N3_502 | W4        | DDR3_DQS4_N |
| PS_DDR_DQ0_502    | C3        | DDR3_D0     |
| PS_DDR_DQ1_502    | B3        | DDR3_D1     |
| PS_DDR_DQ2_502    | A2        | DDR3_D2     |
| PS_DDR_DQ3_502    | A4        | DDR3_D3     |
| PS_DDR_DQ4_502    | D3        | DDR3_D4     |
| PS_DDR_DQ5_502    | D1        | DDR3_D5     |
