# 阶段5 P3c 带宽修复位流证据清单

- bit `s4d_p3c_r01.bit` 4045762 B sha256 `f55a93706e2bbdb64f32d60947c4139ab0f2acba32861e14ac76ed0efcd31485`
- XSA `s4d_p3c_r01.xsa` 376383 B sha256 `1af694a08bcb2482e31ced3bf0dec5596f7fcc6d4c42a183b81e4c0c963c6d84`

- **WNS +0.228 / WHS +0.036，TNS=THS=0，失败端点 0/52,582**
- LUT 26,021(48.91%)、FF 15,021(14.12%)、BRAM 36.5、DSP 158、MMCM 1、BUFG 5、OSERDESE2 8
- DRC 435 条 / **0 error**（无 NSTD-1/UCIO-1）
- 改动：VDMA 数据面 100 MHz（Lite 与 axi_resetn 保持 50 MHz）、smc_vid/HP2 100 MHz、像素域不变
- ⚠ **带宽是否达标未上板验证**（估算 ~380 MB/s vs 需求 221 MB/s）

| 文件 | 字节 | sha256 |
|---|---|---|
| `report/evidence/S5-T01/s5_p3c_hw_20261030_r01/.gitattributes` | 41 | `161d4fc3fc645d35e126e4ee4badaab15cc28a339831082c9f33490211f027b9` |
| `report/evidence/S5-T01/s5_p3c_hw_20261030_r01/bd_p3c.tcl` | 33470 | `bce7144cd584dbec4c7087fd525f0d5c6a4c1a9e5c827194d693cbbc173a0ad3` |
| `report/evidence/S5-T01/s5_p3c_hw_20261030_r01/build_console_output.txt` | 194180 | `91b892fef9bcb0fda194255ded8b289ef2a152a7d42cf48ad3cee4fbfb628b9f` |
| `report/evidence/S5-T01/s5_p3c_hw_20261030_r01/P3C_BUILD_REPORT.md` | 12012 | `7fc3b05de4b3b7edd35099cfb773aba2aac8d1ee06b6ff3c831c4b1a84b2ed18` |
| `report/evidence/S5-T01/s5_p3c_hw_20261030_r01/post_clkgrp_p3c.tcl` | 2416 | `30625cec31f9efba6a9a1cc114b265ef73605c06f19660ee98d0a797a4553a59` |
| `report/evidence/S5-T01/s5_p3c_hw_20261030_r01/post_p3c_checks.tcl` | 3414 | `05f1d556fa2c5abc3eac5537161e2df218650cd7061c6c1cea2521ec7992d3a8` |
| `report/evidence/S5-T01/s5_p3c_hw_20261030_r01/top_p3c_clock_utilization_routed.rpt` | 34663 | `a00ec0c14e3f77a6dd9e78dd59a138177cade1e41d05aa11b99f1a995eef8f80` |
| `report/evidence/S5-T01/s5_p3c_hw_20261030_r01/top_p3c_drc_routed.rpt` | 270820 | `d0b69c9b2c7896c7d12a47e71c46ab86627adfd1501fc8f1c89e334a76834ad6` |
| `report/evidence/S5-T01/s5_p3c_hw_20261030_r01/top_p3c_timing_summary_routed.rpt` | 1553787 | `83b4fd77cce35b7b1a4a06048914b94ed7192a4ea3232d050d1ad8a718f97362` |
| `report/evidence/S5-T01/s5_p3c_hw_20261030_r01/top_p3c_utilization_placed.rpt` | 12679 | `6ac440091b4c0a90f2f93444b8078bf7d9df92976bf2db6f60edcf796319e747` |
| `report/evidence/S5-T01/s5_p3c_hw_20261030_r01/XDC_GUIDELINES.md` | 8749 | `7a26775995d596959ce1d3501c0b3a6e2982fa2035a8c3f276ebc5c1d23435de` |
