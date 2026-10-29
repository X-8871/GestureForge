# 阶段5 P3b 硬件构建证据清单

- bit `s4d_p3b_r01.bit` 4045762 B sha256 `1670b0b38e4fef7ffe8021a99e4c9a1c0a92724e84f13d3fe5a8ca77a7b6f572`
- XSA `s4d_p3b_r01.xsa` 376153 B sha256 `2171583fbac75c00519d7633ff351b2f81feabbe1bc9b96953fdac1fff33719d`

- **WNS +0.544 ns / WHS +0.022 ns，TNS=THS=0，失败端点 0/52,363**
- LUT 25,967(48.81%)、FF 14,892(14.00%)、BRAM 36.5(26.07%)、DSP 158(71.82%)、MMCM 1、BUFG 5、OSERDESE2 8
- DRC 429 条 / 0 error（无 NSTD-1/UCIO-1）
- 时钟自证：13.474 ns 像素、2.695 ns 5×、20/10 ns

> 技术记录：`PROCESSING_ORDER {LATE}` 未修复 12-4739（仍 6 条），改用路由后补加时钟组，WNS/WHS 不变；`hdmi_oen` 按厂商源码驱动 1，上板不亮时第一处置点为反相。

| 文件 | 字节 | sha256 |
|---|---|---|
| `report/evidence/S5-T01/s5_p3b_hw_20261030_r01/.gitattributes` | 41 | `161d4fc3fc645d35e126e4ee4badaab15cc28a339831082c9f33490211f027b9` |
| `report/evidence/S5-T01/s5_p3b_hw_20261030_r01/bd_p3b.tcl` | 30504 | `fc4da51e9a1831dea3d1be0b17265393e707bd9694717f8876c340b14f84717f` |
| `report/evidence/S5-T01/s5_p3b_hw_20261030_r01/build_console_output.txt` | 176397 | `be4ee8f96ae34570ddc1bd907c91849979194fabd1f1b5adec7260f9a993dca3` |
| `report/evidence/S5-T01/s5_p3b_hw_20261030_r01/P3B_BUILD_REPORT.md` | 18312 | `3b3b5ab4e8993110fcc2004227a947a3418e003f8bdbee3812afb3520ada8348` |
| `report/evidence/S5-T01/s5_p3b_hw_20261030_r01/p3b_tmds.xdc` | 3727 | `65178374e0fe4891e6ed100e8f61c7cb7a4ba69281a8dd267eec07e2acdf1e99` |
| `report/evidence/S5-T01/s5_p3b_hw_20261030_r01/top_p3b_clock_utilization_routed.rpt` | 33053 | `4db4c069e4fdc0b98a803031a5b6e8a5e3563d6882cb490819832b958199d4b7` |
| `report/evidence/S5-T01/s5_p3b_hw_20261030_r01/top_p3b_drc_routed.rpt` | 268744 | `3a8a1995aded3e96e02aa59eea8cbe36fcf1f91552269280df8130656569bbd4` |
| `report/evidence/S5-T01/s5_p3b_hw_20261030_r01/top_p3b_methodology_drc_routed.rpt` | 4887 | `8cdb0b8d3b93bc73d2bf218c478c1b6308a5bf5feb245e920ae5f84da89a5406` |
| `report/evidence/S5-T01/s5_p3b_hw_20261030_r01/top_p3b_timing_summary_routed.rpt` | 984183 | `a0c76cf8372a6d210db1c64290c611dfb6fe6508ee3cf5ccf1289c0f195568a8` |
| `report/evidence/S5-T01/s5_p3b_hw_20261030_r01/top_p3b_utilization_placed.rpt` | 12648 | `7f6d0de58b2579f23494e5170ddd46489b31480cfceeae70f798c66a9fd7a51c` |
| `report/evidence/S5-T01/s5_p3b_hw_20261030_r01/XDC_GUIDELINES.md` | 8749 | `7a26775995d596959ce1d3501c0b3a6e2982fa2035a8c3f276ebc5c1d23435de` |
