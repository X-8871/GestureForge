<!-- page: 9 -->

<!-- image -->

## ( 二 ) ZYNQ 芯片

开发板使用的是Xilinx 公司的Zynq7000 系列的芯片，型号为XC7Z020-2CLG400I。芯 片的PS系统集成了两个ARM Cortex™-A9处理器，AMBA®互连，内部存储器，外部存储 器接口和外设。这些外设主要包括USB总线接口，以太网接口，SD/SDIO接口，I2C总线接 口，CAN 总线接口，UART 接口，GPIO 等。PS 可以独立运行并在上电或复位下启动。 ZYNQ7000 芯片的总体框图如图2-2-1 所示

## AC7Z020 核心板正面图

AC7Z020 核心板背面图

<!-- image -->

<!-- page: 11 -->

<!-- image -->

XC7Z020-2CLG400I 芯片的速度等级为-2，工业级，封装为 BGA400，引脚间距为 0.8mm，ZYNQ7000 系列的具体的芯片型号定义如下图2-2-2所示。

图2-2-2 ZYNQ型号命名规则定义

<!-- image -->

图2-2-3 为开发板所用的XC7Z020 芯片实物图。

图2-2-3 XC7Z020芯片实物

<!-- image -->

## ( 三 ) DDR3 DRAM

AC7Z020核心板上配有两片Micron公司的DDR3 SDRAM芯片(共计1GB),型号为

<!-- page: 14 -->

<!-- image -->

| DDR3_D6   | PS_DDR_DQ6_502   | C1   |
|-----------|------------------|------|
| DDR3_D7   | PS_DDR_DQ7_502   | E1   |
| DDR3_D8   | PS_DDR_DQ8_502   | E2   |
| DDR3_D9   | PS_DDR_DQ9_502   | E3   |
| DDR3_D10  | PS_DDR_DQ10_502  | G3   |
| DDR3_D11  | PS_DDR_DQ11_502  | H3   |
| DDR3_D12  | PS_DDR_DQ12_502  | J3   |
| DDR3_D13  | PS_DDR_DQ13_502  | H2   |
| DDR3_D14  | PS_DDR_DQ14_502  | H1   |
| DDR3_D15  | PS_DDR_DQ15_502  | J1   |
| DDR3_D16  | PS_DDR_DQ16_502  | P1   |
| DDR3_D17  | PS_DDR_DQ17_502  | P3   |
| DDR3_D18  | PS_DDR_DQ18_502  | R3   |
| DDR3_D19  | PS_DDR_DQ19_502  | R1   |
| DDR3_D20  | PS_DDR_DQ20_502  | T4   |
| DDR3_D21  | PS_DDR_DQ21_502  | U4   |
| DDR3_D22  | PS_DDR_DQ22_502  | U2   |
| DDR3_D23  | PS_DDR_DQ23_502  | U3   |
| DDR3_D24  | PS_DDR_DQ24_502  | V1   |
| DDR3_D25  | PS_DDR_DQ25_502  | Y3   |
| DDR3_D26  | PS_DDR_DQ26_502  | W1   |
| DDR3_D27  | PS_DDR_DQ27_502  | Y4   |
| DDR3_D28  | PS_DDR_DQ28_502  | Y2   |
| DDR3_D29  | PS_DDR_DQ29_502  | W3   |
| DDR3_D30  | PS_DDR_DQ30_502  | V2   |
| DDR3_D31  | PS_DDR_DQ31_502  | V3   |
| DDR3_DM0  | PS_DDR_DM0_502   | A1   |
| DDR3_DM1  | PS_DDR_DM1_502   | F1   |
| DDR3_DM2  | PS_DDR_DM2_502   | T1   |
| DDR3_DM3  | PS_DDR_DM3_502   | Y1   |
| DDR3_A0   | PS_DDR_A0_502    | N2   |
| DDR3_A1   | PS_DDR_A1_502    | K2   |

<!-- page: 15 -->

<!-- image -->

| DDR3_A2                      | PS_DDR_A2_502     | M3       |
|------------------------------|-------------------|----------|
| PS_DDR_A3_502                | K3                | DDR3_A3  |
| PS_DDR_A4_502                | M4                | DDR3_A4  |
| PS_DDR_A5_502                | L1                | DDR3_A5  |
| PS_DDR_A6_502                | L4                | DDR3_A6  |
| PS_DDR_A7_502                | K4                | DDR3_A7  |
| PS_DDR_A8_502                | K1                | DDR3_A8  |
| PS_DDR_A9_502                | J4                | DDR3_A9  |
| PS_DDR_A10_502               | F5                | DDR3_A10 |
| PS_DDR_A11_502               | G4                | DDR3_A11 |
| PS_DDR_A12_502               | E4                | DDR3_A12 |
|                              | PS_DDR_A13_502 D4 | DDR3_A13 |
| PS_DDR_A14_502               | F4                | DDR3_A14 |
| PS_DDR_BA0_502               | L5                | DDR3_BA0 |
| PS_DDR_BA1_502               | R4                | DDR3_BA1 |
| PS_DDR_BA2_502               | J5                | DDR3_BA2 |
| PS_DDR_CS_B_502              | N1                | DDR3_S0  |
| PS_DDR_RAS_B_502             | P4                | DDR3_RAS |
| PS_DDR_CAS_B_502             | P5                | DDR3_CAS |
| PS_DDR_WE_B_502              | M5                | DDR3_WE  |
| DDR3_ODT PS_DDR_ODT_502      | N5                |          |
| DDR3_RESET PS_DDR_DRST_B_502 | B4                |          |
| DDR3_CLK0_P PS_DDR_CKP_502   | L2                |          |
| DDR3_CLK0_N PS_DDR_CKN_502   | M2                |          |
| DDR3_CKE                     | PS_DDR_CKE_502    | N3       |
