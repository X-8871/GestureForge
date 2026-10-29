# P2c r02 证据清单

- RunId `pl_v2_p2c_dma_bitstream_20261029_r02`（候选；未上板；不主张 G3/G4/G5）

| 文件 | 字节 | sha256 |
|---|---|---|
| `s4d_p2c.bit` | 4045770 | `022f48fbf78722424a7c10a3b2fca6c26d2ce7cbc89e0f8dd1dbd02a99d52ca4` |
| `s4d_p2c.xsa` | 353213 | `8051dd485d9c76fdbc00dff99dbf1716d1f613cebdee40975ec85469de61bf4c` |
| `reports/timing_route.rpt` | 270273 | `8478bd8da3ee1a32b061606a469dc4c95b572831330dcd33ec79db5774a19c07` |
| `reports/util_route.rpt` | 11894 | `5f1bade1fa22cc5ce1f2dc23b86c961f0fadbca72213de8b6038b047b189fd18` |
| `logs/build_p2c_r02_output.txt` | 147622 | `1db5668ebfbf565152b792f5e72cbb3bdf15b9ded622a291eb7a28058700d367` |
| `inputs/bd_p2c.tcl` | 9164 | `ff8b7d2f9a52d34167a8b4f5ac178c35b07a15344789718a50628e1f5eea9b87` |
| `inputs/P2C_R02_vs_frozen.patch` | 6356 | `454603612ecfc3d0dad38cafa71ef162a7781dafef0a774a492657f752cc4bf2` |
| `inputs/rtl/s4d_axi4_rd_shim.sv` | 7207 | `8bcf1c1d124a96a7a7cc3c47e802d2fc5cfba851655e11aae9d1ae8686fc0d59` |
| `inputs/rtl/s4d_axis8_to_axis64.sv` | 4541 | `0078dbf69bbe1a8416497434a5eac2bb3e83b90bf9c5118401251e5079e98d04` |
| `inputs/rtl/s4d_coord_tables.svh` | 30288 | `42ebbd8f879df9f539f78d29adcd04c43c7bf605d84db71f67ce0712329d9883` |
| `inputs/rtl/s4d_preproc_axi_wrapper.sv` | 6547 | `670f12ba1d2175aa4069f568b18872aed6c2d5476f65c11c804437dd91eb2a9b` |
| `inputs/rtl/s4d_preproc_csr.sv` | 11850 | `38afc806db1624dc6d6ff96860a4318604b05fed35552c17fded5b43577256a8` |
| `inputs/rtl/s4d_preproc_engine_v2.sv` | 24650 | `a4391b10c748569321715278c37f65a2710c35f9b1e9f1c4f11986ad4c5d2565` |
| `inputs/rtl/s4d_preproc_letterbox.sv` | 11336 | `439ceae066af5e8ac133c18c251803698042bf8085c7e9a65fe1f7817dd4d9e0` |
| `inputs/rtl/s4d_preproc_out_axis.sv` | 3778 | `a27828e842e31198e2f300ff3f6e683d7f49c0bdc36566181d1a1fad0d14d1b4` |
| `inputs/rtl/s4d_preproc_v2_wrap.sv` | 9845 | `b074ff6380c715247365d5eb9206b9b69d5f28b2f6f298affa3582ced0dfb00c` |
| `inputs/tb/tb_s4d_axis8_to_axis64.sv` | 3642 | `f2127e893244c1351138b687464e5e805b1f0ad9e92c37a8cd298722558cb08b` |
| `logs/packer_tb_output.txt` | 737 | `b31fd5bc424d5c56c8e5adbf37333dff92f7d50b4f9ba8ea74ef0c08acc31408` |
| `regression/results.tsv` | 562 | `e0bd9cb90f1d74138e958c801740d3c445d442b0b4856576f316c70fa133aaad` |
| `regression/work_engine_v2.result.txt` | 140 | `992fe2ee73048c7e8f214e4626c3a6ac66954131f597d000b7aa35027e196e61` |
| `regression/work_v2_axi.result.txt` | 191 | `6a5164752c73d6fe6e9a6e6b8c6356eadabbd82ba4554eeaee7bc2c34ef8e4fe` |
| `regression/work_v2_axis.result.txt` | 99 | `08b85120e1790430c17815ff89384524997e5def59008cf62f27231ad3184737` |
| `regression/run_tb_regression.py` | 3884 | `ff43b2ce1d1abe624796f5efa0f024ac81e845e460fe5b67152d94171e2441de` |
| `logs/dma_length_width_check.txt` | 1021 | `cd081fe64cc746379a00ff75ee05bc43d7dc6e96b1e3fdbf5cb95dd9b59b5b59` |
| `MANIFEST.md` | 2772 | `f062d6ea400c939593fff47e4abd733a0ca310e978c2ff44519ec74ed92ab8a4` |
| `README.md` | 3171 | `8c413daf174e504cd0b11ba6fa567f7b7406c8f5aa79f313a8f9fce0b7ff6e2c` |

hash_basis = commit_blob（本目录随 w4 提交进入 git）。
