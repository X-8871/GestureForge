# E2 冷启动确认（VDMA 读流未启动 WARN）

- 结论：**COLD_BOOT_VDMA_STREAM_NOT_STARTED**

| 文件 | 字节 | sha256 |
|---|---|---|
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/results.json` | 4059 | `45c62e05796e1fdc8b25fd0bbb1c00691246dc6261f37f5a77bd6991106e7c88` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S1_IDENT.json` | 284 | `1958d172e825fc953f5de5c1a79116ecb07eb2c93e439f7cd3e4d8943abafd0e` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S2_loadhw_stop.exit_code.txt` | 8 | `2095d5302e465922147e220c0389f7a923ea0c1509a23097f04b3c220798aef8` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S2_loadhw_stop.json` | 247 | `be79db12520cb464fe7fc64b04eed29325c024abd069f91cbe9cf33ab1e12c0b` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S2_loadhw_stop_output.txt` | 701 | `eb3bd313787c0b5ed40d0598b748b0c14f469f5037fe16951350c992878c0d2d` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S3_ps7_init.exit_code.txt` | 8 | `2095d5302e465922147e220c0389f7a923ea0c1509a23097f04b3c220798aef8` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S3_ps7_init.json` | 41 | `b269e0bd91e0bf909bf0f75ba139e1cffb6d2611e5c36304134b187f8ac53d3b` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S3_ps7_init_output.txt` | 406 | `9f4b8f3e06bacf19b977cd4d796027055d9430a060d5e6bf40ee8a5e0fe0543b` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S4_fpga.exit_code.txt` | 8 | `2095d5302e465922147e220c0389f7a923ea0c1509a23097f04b3c220798aef8` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S4_fpga_output.txt` | 264 | `f4d1f19a07e9941226b118ab66cf95bd36be01d37d4a7f4351388de0a44c6bdb` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S4_lvl_A.exit_code.txt` | 8 | `2095d5302e465922147e220c0389f7a923ea0c1509a23097f04b3c220798aef8` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S4_lvl_A_output.txt` | 616 | `ae588c4fe9adbcf7710aca04219083ce3b721d9428c48ec47396753e8b8db173` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S4_lvl_F.exit_code.txt` | 8 | `2095d5302e465922147e220c0389f7a923ea0c1509a23097f04b3c220798aef8` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S4_lvl_F_output.txt` | 616 | `06292d8fcc228f7864d6d5e897885f33eaf1964b9ad9dc13377ffdc703483c9e` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S4_program_pl.json` | 71 | `5913238fdd19075b13d8def7f0151eca8fdfe97cc9b7149290d85f7e58a52448` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S5_pl_probe.exit_code.txt` | 8 | `2095d5302e465922147e220c0389f7a923ea0c1509a23097f04b3c220798aef8` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S5_pl_probe.json` | 201 | `626556d852300bc2a9fd06151e88724b362e7f417e79d06abded9bde4a689d4a` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S5_pl_probe_output.txt` | 721 | `c36e95e9939c278de29cdbcfd4bcc68eb59321f0a49b6d5c6bb67cf29cc13189` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S6_load_app.exit_code.txt` | 8 | `2095d5302e465922147e220c0389f7a923ea0c1509a23097f04b3c220798aef8` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S6_load_app.json` | 141 | `54f14980648a2dee2939846461c75fea3a3748afb6853ff9680db398ea4e32b6` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S6_load_app_output.txt` | 898 | `136a301570ef6f21ccf65975fea64f9cc521e40b66f5e628615c712dabb8031c` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S6b_watchdog.json` | 565 | `2d5698ad0abf2d0c92b8e98e097bc80e4bf7886495be74955ea05f57c1d0227a` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S7_uart_output.txt` | 1232 | `dbb8b77109420d1f10a5477f83c6928c9083bc24db8feec7398201f39bfdd147` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S8_gt_lo.bin` | 4 | `35b51193ca01ab502df364c36e051ebf7bc1cfe330566ef354bb6f45aa4a8a71` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S8_gt_lo.exit_code.txt` | 8 | `2095d5302e465922147e220c0389f7a923ea0c1509a23097f04b3c220798aef8` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S8_gt_lo_output.txt` | 295 | `b16c9c301d028937e2ddda72e7a31ea0938d1e0cc34f0a4245be2e16aa2f3daa` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S8_judgement.json` | 486 | `19df87be75c21bc3f80f9fa89e37a2a14520ee508936eb362046cb856d6e8d0e` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S8_stop.exit_code.txt` | 8 | `2095d5302e465922147e220c0389f7a923ea0c1509a23097f04b3c220798aef8` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S8_stop_output.txt` | 243 | `a292656a6d3c74a86c23fb96b145e0bc8f4b7f5b2336f43684d9106743198153` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S9_stop.exit_code.txt` | 8 | `2095d5302e465922147e220c0389f7a923ea0c1509a23097f04b3c220798aef8` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S9_stop_output.txt` | 240 | `90f155cb7ad3cdc510f4c4b14689b61211996d1718b23505db3b29257fec367a` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/S9_teardown.json` | 176 | `7800458f0d6635c06f408d4c21a39c69940a905db7bd857eec2a8ea3ab8bea0a` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/W3_judgement.json` | 675 | `1a318d1e6f8fa41b975b733dba96c524da49e750b3c87e373dfd12683e91fe6e` |
| `report/evidence/S6-T01/s6e_e2_frame_period_20261030_r12/window_close.txt` | 872 | `bc9b12477657ef84d11d4ea527e0dea3ad75d9d0074aa31479168cf78307f30a` |
