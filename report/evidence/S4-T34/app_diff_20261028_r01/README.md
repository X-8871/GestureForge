# 旧/新应用事务差异（离线）

| | 旧应用 | 新应用 |
|---|---|---|
| ELF | `D:/FPGA_Competition/w2b/report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04_artifacts/infer.elf` | `report/evidence/S4-T34/ps_decode_link_20261028_r01/longrunK/s4d_ps_app_sw0_longrunK.elf` |
| SHA-256 | `a51499895e9387a74db87a3267843b9fbf7fdfa8b6646fcbc5db01485e090bf8` | `b7a654aac7698c1e1d34332146ba7b284985c48ef507f96ee8b8c6211b4d3665` |
| 大小 | 389216 B | 278332 B |

## CSR 偏移集合（从反汇编字面量提取）
- 旧应用覆盖 **0** 个偏移；新应用覆盖 **1** 个。
- **旧独有**：`{}`
- **新独有**：`{'0xd180': 1}`
- 共有偏移（旧/新引用次数）：`{}`

## cache / 异常指令计数
| 类别 | 旧 | 新 |
|---|---|---|
| dc_clean_c7_10 | 2 | 2 |
| dc_clean_inval_c7_14 | 10 | 10 |
| dc_inval_c7_6 | 8 | 8 |
| dc_inval_c7_5 | 17 | 14 |
| ic_inval_c7_5 | 7 | 7 |
| tlb_c8 | 4 | 1 |
| dfsr_c5 | 0 | 1 |
| dfar_c6 | 0 | 1 |
| dsb | 78 | 74 |
| dmb | 0 | 0 |"

> 说明：新应用的 DFSR/DFAR 读来自**数据中止处理器**（本轮新加）；旧应用计数非 0 说明其 BSP/库内也有中止处理路径。

## 结论口径
- 静态差异**只能**给出候选点，不能证明因果；因果需要 r06 窗口的 `error_code(0x010)/last_reject(0x064)/status(0x00C)` 三读。
- 边界：离线、未上板、不改判据、不主张 G3/G4/G5。
