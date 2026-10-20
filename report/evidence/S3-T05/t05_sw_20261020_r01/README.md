# S3-T05-SW 证据入口（task-1｜2026-10-20）

| 文件 | 内容 |
|---|---|
| `build_report.json` | 机器可读清单：基线 commit、改动文件与 SHA-256、命令原文与真实退出码、产物路径与 SHA-256、限制与未执行项 |
| `s2mm_sr_decode_conclusion.md` | **S2MM SR（0x43010034）位定义解码结论**（三份本地依据：驱动头文件 / IP 元数据 / IP HDL），含已有实测读数的判读与上板判读规则 |
| `sr_bit_sources/` | 上述三份依据的原文摘录（含源文件 SHA-256）与解析输出 |

产物（不属于证据包，落点见 `build_report.json`）：

* v5 补丁：`board/stage3/software/sensor/s3_t04_app_diag_v5.patch`（只改 `display_demo.c`，`git apply --check` 退出码 0）
* 补丁生成器（含 v5 变体）：`scripts/stage3_t04/make_app_diag_patch.py`
* 上板用 ELF：`tmp/s3r06/t04_j11cmos2_elf_v5/elf_build/app/an5642_j11cmos2_v5.elf`
  SHA-256 `a54d038530fc1a63ea84c897600195f68b7f14d7094f89951d6218e8fb1b0c3e`（306,188 B，构建退出码 0）

未执行：上板下载/UART 采集（由阶段总控在独立运行执行）、Vivado 综合/实现、Git 提交、QSPI 烧写。