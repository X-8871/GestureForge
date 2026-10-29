# P2a/P2b 构建输入 RTL 归档（2026-10-29）

- 目的：P2a/P2b 位流的 preproc v2 RTL 原先只存在于 `D:\tmp\lead\p2a_20261029_r01\src\rtl`（**不在任何 git 树**），
  冻结位流因此不可复现。本目录把构建输入原样归档进 w4 证据树，并以 `hash_basis=commit_blob` 绑定。
- 身份：文件字节与原构建输入逐字节相同（见 `manifest.json` 的 `items[].source` 与 sha256）；
  与原构建输入目录一致，**未做任何修改**。
- 限制：仅补可复现性；未重跑综合/实现；不改变 P2a/P2b 位流身份；不主张 G3/G4/G5。

## 文件
- `rtl/s4d_axi4_rd_shim.sv`  7207 B  sha256 `8bcf1c1d124a96a7a7cc3c47e802d2fc5cfba851655e11aae9d1ae8686fc0d59`
- `rtl/s4d_coord_tables.svh`  30288 B  sha256 `42ebbd8f879df9f539f78d29adcd04c43c7bf605d84db71f67ce0712329d9883`
- `rtl/s4d_preproc_axi_wrapper.sv`  6547 B  sha256 `670f12ba1d2175aa4069f568b18872aed6c2d5476f65c11c804437dd91eb2a9b`
- `rtl/s4d_preproc_csr.sv`  11850 B  sha256 `38afc806db1624dc6d6ff96860a4318604b05fed35552c17fded5b43577256a8`
- `rtl/s4d_preproc_engine_v2.sv`  24470 B  sha256 `8f2df01b767fc0ce2bfc1a35dd77438d1de4d21e9dab7ed6b217c71ca688e845`
- `rtl/s4d_preproc_letterbox.sv`  11336 B  sha256 `439ceae066af5e8ac133c18c251803698042bf8085c7e9a65fe1f7817dd4d9e0`
- `rtl/s4d_preproc_out_axis.sv`  3778 B  sha256 `a27828e842e31198e2f300ff3f6e683d7f49c0bdc36566181d1a1fad0d14d1b4`
- `rtl/s4d_preproc_v2_wrap.sv`  9717 B  sha256 `d0264a4471333b7d0561e1103947039b012552e78d05b5555954d1e2a7568d5d`
- `bd_preproc_v2.tcl`  5790 B  sha256 `d10f314318cab247621dff1a3b2f4881d57509f6ca4bf283fe0a48f6f495b019`
