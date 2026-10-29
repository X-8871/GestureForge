# P2c 候选位流证据清单

- P2c 候选位流：preproc（源图基址 0x12000000）+ AXIS→64b 打包 + AXI DMA S2MM→HP0 + 2B 推理

| 文件 | 字节 | sha256 |
|---|---|---|
| `s4d_p2c.bit` | 4045770 | `0c8ec47660057da8d89a3a0b22ced2b04ba23a4f7a2ba3e51157fe97e2e8352f` |
| `s4d_p2c.xsa` | 353184 | `3f0ed9eab27cc84790b884d14174b668024ba3e9fc0d05925908a4d19207e38e` |
| `reports/timing_route.rpt` | 259849 | `8ea66b6122a22086ed11c40ac4f4d4a913a6bc3b96890816b0e2a54a74fa3b12` |
| `reports/util_route.rpt` | 11894 | `34161b1951d55e63a9b327e6fcd7a6f8b6d6daa37a14bd8ee6bbec57be58c085` |
| `logs/build_p2c.stdout` | 144855 | `785fff1a50c653c7dec0ca8939816eee3f237cfaa8e7880119f6e4eb8271217f` |
| `logs/build_p2c_output.txt` | 143156 | `898eccb19988c363b49811a12b651ea000c5d05532ae0b7c53000739b04b902d` |
| `inputs/bd_p2c.tcl` | 8824 | `bad5cb10a102d9c9baaa9f390f603251f596bed147be51326949368ca4c78d9d` |
| `inputs/SRC_BASE.patch` | 1901 | `2255e06eabc764d79cc8fc9d120dab717b25d1ae8e06b7406c3495ae97bf73d6` |
| `inputs/rtl/s4d_axi4_rd_shim.sv` | 7207 | `8bcf1c1d124a96a7a7cc3c47e802d2fc5cfba851655e11aae9d1ae8686fc0d59` |
| `inputs/rtl/s4d_axis8_to_axis64.sv` | 4541 | `0078dbf69bbe1a8416497434a5eac2bb3e83b90bf9c5118401251e5079e98d04` |
| `inputs/rtl/s4d_coord_tables.svh` | 30288 | `42ebbd8f879df9f539f78d29adcd04c43c7bf605d84db71f67ce0712329d9883` |
| `inputs/rtl/s4d_preproc_axi_wrapper.sv` | 6547 | `670f12ba1d2175aa4069f568b18872aed6c2d5476f65c11c804437dd91eb2a9b` |
| `inputs/rtl/s4d_preproc_csr.sv` | 11850 | `38afc806db1624dc6d6ff96860a4318604b05fed35552c17fded5b43577256a8` |
| `inputs/rtl/s4d_preproc_engine_v2.sv` | 24597 | `06be0fcaf2a21e8c1715a722959f2b71a3784be7bf7eb82025687c64f070e8ae` |
| `inputs/rtl/s4d_preproc_letterbox.sv` | 11336 | `439ceae066af5e8ac133c18c251803698042bf8085c7e9a65fe1f7817dd4d9e0` |
| `inputs/rtl/s4d_preproc_out_axis.sv` | 3778 | `a27828e842e31198e2f300ff3f6e683d7f49c0bdc36566181d1a1fad0d14d1b4` |
| `inputs/rtl/s4d_preproc_v2_wrap.sv` | 9713 | `a84eeb55158907f7a1c05638aa085cef31b5a7ad0b3e0f353fbd987bfc60865a` |
| `inputs/tb/tb_s4d_axis8_to_axis64.sv` | 3642 | `f2127e893244c1351138b687464e5e805b1f0ad9e92c37a8cd298722558cb08b` |
| `logs/xvlog.log` | 379 | `09962bdbf21fa85a6ddab12ef0422230829e7b4e5fec5742b08b4c526b909c71` |
| `logs/xelab.log` | 622 | `3b824bacb8550f042a4b6fa8c3da735314db3f0889b1fa9122c0415bbe4336b3` |
| `logs/xsim.log` | 1349 | `22dfada35556f18e41446599a266db86d8ceb1642ebe0faa62b769007e63505f` |
| `logs/packer_tb_output.txt` | 737 | `b31fd5bc424d5c56c8e5adbf37333dff92f7d50b4f9ba8ea74ef0c08acc31408` |
