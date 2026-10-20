# S3-T05-SW4 v8：手动白平衡 + 5 档 B 增益 ELF（task-5）

日期：2026-10-20（UTC+8）｜基线 commit：`41ee5ba003147d77349e8908c38b2efc97752ca8`｜未提交 Git｜**未上板**

用途：用白纸做闭环标定——把 AWB 手动增益打开（`0x3406=0x01`）并按 `0x3400..0x3405` 写 R/G/B 增益，
5 个 ELF（1 个不动增益 + 4 档 B）逐一刷写，看白纸在显示器上是否变白；每轮同时看 v7 的 AWB/AE/ISP 回读与 v6 的 64 KB 指纹。

## 1. 五个 ELF（文件名固定，便于按名刷写）

| 文件名 | 编译期配置 | SHA-256（306,208 B） |
|---|---|---|
| `an5642_j11cmos2_v8_off.elf` | `S3_WB_MANUAL=0`（不动 0x3406/增益） | `85e989196dc34f5f1cc7b87607b2905f54405ec95a5486cf14916edd7eec145e` |
| `an5642_j11cmos2_v8_b2048.elf` | MANUAL + R=1024 G=1024 **B=2048** | `ef89df1520228e0388f6590c8fd4181a92c323b08a5f49f25d27fd49df43da47` |
| `an5642_j11cmos2_v8_b2560.elf` | MANUAL + R=1024 G=1024 **B=2560** | `7c068a658dc6a5f0876aa1ba62b86662d70aab34b76f366c80a43ad318f7879a` |
| `an5642_j11cmos2_v8_b3072.elf` | MANUAL + R=1024 G=1024 **B=3072** | `3124befe02f475033a677772c18664f9f5f3236300bb05d803d385ca70d9783d` |
| `an5642_j11cmos2_v8_b3584.elf` | MANUAL + R=1024 G=1024 **B=3584** | `7ccf332f01e59d98df4f60483a843583104d9ce85cbaa49e3e7438fa8915257b` |

全部在 `tmp/s3r06/t04_j11cmos2_elf_v8/elf_build/app/`；均由 SOF 修复 XSA（`1f5b138e…cb0e3`）构建，5 次构建**退出码均 0**。

## 2. 五条编译行（原文；另见 `elf_build_evidence.txt`）

```
an5642_j11cmos2_v8_off.elf   : arm-none-eabi-gcc -O2 -c -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -c display_demo.c -o display_demo.o …
an5642_j11cmos2_v8_b2048.elf : arm-none-eabi-gcc -O2 -c -DS3_WB_MANUAL=1 -DS3_WB_R=1024 -DS3_WB_G=1024 -DS3_WB_B=2048 -mcpu=… -c display_demo.c -o display_demo.o …
an5642_j11cmos2_v8_b2560.elf : arm-none-eabi-gcc -O2 -c -DS3_WB_MANUAL=1 -DS3_WB_R=1024 -DS3_WB_G=1024 -DS3_WB_B=2560 -mcpu=… -c display_demo.c -o display_demo.o …
an5642_j11cmos2_v8_b3072.elf : arm-none-eabi-gcc -O2 -c -DS3_WB_MANUAL=1 -DS3_WB_R=1024 -DS3_WB_G=1024 -DS3_WB_B=3072 -mcpu=… -c display_demo.c -o display_demo.o …
an5642_j11cmos2_v8_b3584.elf : arm-none-eabi-gcc -O2 -c -DS3_WB_MANUAL=1 -DS3_WB_R=1024 -DS3_WB_G=1024 -DS3_WB_B=3584 -mcpu=… -c display_demo.c -o display_demo.o …
```

* `v8_off` 由标准入口（`run_stage3_vitis_elf.cmd`，不带 `-D`，用源码默认值）构建。为满足“编译行逐字含对应 `-D`”的取证要求，
  另用 `-DS3_WB_MANUAL=0 -DS3_WB_R=1024 -DS3_WB_G=1024 -DS3_WB_B=1024` 重建了一个对照 ELF（`…_v8_off_dfo.elf`），
  **其 SHA-256 与官方 `v8_off` 完全相同**（`85e98919…145e`）→ 证明 off 配置的编译期值就是 0/1024/1024/1024。对照 ELF 不是交付物。
* 额外机器证据：ELF 内字符串 MANUAL/OFF 互斥；`arm-none-eabi-objdump -d` 在每个 WB ELF 的 `.text` 里查到各自的 B 立即数
  （b2048: `#2048`×7；b2560: `#2560`×2；b3072: `#3072`×3；b3584: `#3584`×2；基线各 5 个 `#2048`+1 个 `#3072` 来自 BSP/libxil）。

## 3. 我采用的增益编码 + 如何用回读定论（卡面重点 1）

* **写入**：`hi = (gain >> 8) & 0xFF` → 高位寄存器，`lo = gain & 0xFF` → 低位寄存器（R: 0x3400/0x3401，G: 0x3402/0x3403，B: 0x3404/0x3405），
  并写 `0x3406 = 0x01` 使能手动增益；**写完立即回读 6 个寄存器**。
* **依据**：v7 上板实测按 `(hi<<8)|lo` 得 R=1085 / G=1024 / B=2021，与“G=1024=1.0×、R/B 为自动增益”自洽；
  本轮 B 档位 2048 已超过 11 位，只有把寄存器对当 ≥12 位字段才能表达。**本任务未与 OV5640 手册核对该位域**，故结论交给回读。
* **判读表**（`S3_DIAG8_WB_RB` 行的 `match=` 三个标志 + `rb_b16`）：

| B 档位 | 若字段 11 位（写入被截断） | 若字段 ≥12 位（全部生效） |
|---|---|---|
| 2048 | `rb_b16=0x0000`（=0，增益退化） | `rb_b16=0x0800` |
| 2560 | `rb_b16=0x0200`（512） | `rb_b16=0x0A00` |
| 3072 | `rb_b16=0x0400`（1024） | `rb_b16=0x0C00` |
| 3584 | `rb_b16=0x0600`（1536） | `rb_b16=0x0E00` |

  `match_b=1` ⇒ 字段 ≥12 位，写入全部生效；`match_b=0` 且 `rb_b16 = B & 0x7FF` ⇒ 字段 11 位、写入被截断，
  需按截断后的实际增益解读画面并把 B 档位改到 ≤2047 重试。R/G=1024 在两种编码下都等于 0x0400，判别只能靠 B 通道。

## 4. v8 的 UART 输出与标定流程

新增两行（在 15 s 等待之前打印）：

```
S3_DIAG8_WB=MANUAL R=0x0400 G=0x0400 B=0x0800 before3406=0x00 after3406=0x01 readback3400..3405=0x04,0x00,0x04,0x00,0x08,0x00
S3_DIAG8_WB_RB rb_r16=0x0400 rb_g16=0x0400 rb_b16=0x0800 match=1,1,1 write_status=0
```

（`S3_WB_MANUAL=0` 时打印 `S3_DIAG8_WB=OFF (auto AWB unchanged)`。`write_status` 为 7 次 I2C 写状态的按位或，0=全成功。）

同时保留：`S3_DIAG7_AWB / AE / ISP_A / ISP_B`（v7 只读回读）、`S3_DIAG6_FP`（3 处 × 64 KB 指纹，t≈5/10/15/20/25 s）、`S3_DIAG6_SENS`（t≈30 s）。

**建议流程**：同一灯光、同一白纸 → 依次刷 `v8_off`（基线，看 AWB 自动增益与白纸颜色）→ `b2048` → `b2560` → `b3072` → `b3584`，
每轮读 `S3_DIAG8_WB_RB` 确认增益真的写进去（match），并看白纸是否变白、以及图像是否过/欠曝（B 增益是整数放大，增益过高会削顶）。

## 5. 命令与退出码（全 0）

| 步骤 | 退出码 | 结果 |
|---|---|---|
| 默认变体回归（无参数） | 0 | 与 v5 补丁**逐字节相同** |
| `v4` / `v6` / `v7` 回归 | 0 / 0 / 0 | 分别与 v4 / v6（`4c7becc1…b960`）/ v7（`d4713177…b79cad`）**逐字节相同** |
| `v8` 生成 | 0 | `GIT_APPLY_EXIT=0`；`VERIFY_HAS_D8_*` 全 True |
| 厂商副本 `git apply --check` | 0 | 只含 `display_demo.c` |
| `v8_off` 构建 | 0 | 标准入口 sdtgen+make |
| 4 个 WB ELF 构建 | 0 | 4 条编译行各含自己的 `-D` |
| off 显式 `-D` 对照构建 | 0 | 与官方 off **逐字节相同** |

## 6. 交付物哈希

| 产物 | SHA-256 |
|---|---|
| `board/stage3/software/sensor/s3_t04_app_diag_v8.patch`（437 行，只改 display_demo.c） | 见 `build_report.json`（现场计算） |
| `scripts/stage3_t04/make_app_diag_patch.py`（新增 `v8`，默认仍 `v5`） | 同上 |
| 证据 `elf_build_evidence.txt`（5 编译行 + 5 哈希 + 开关/objdump 证据） | `e3782961b8fc255e9b196bacd50acde569fb2bc7ac9c751af5c69713ec502969` |

## 7. 限制 / 未执行

* **未上板**：`S3_DIAG8_*` 实际数值与“字段宽度”结论尚未产生；未下载/未运行/未采集 UART。
* 未跑 Vivado 综合/实现；未烧 QSPI；未提交 Git；未查 OV5640 手册核对位域与 `0x3406` 位定义。
* 手动路径只写 `0x3406=0x01` 与增益，**没有清 `0x5001` bit0（AWB 仍使能）**；若 AWB 环路仍会改写增益，
  可组合 `S3_AWB_OFF=1`（v8 补丁两个开关都支持；本轮 5 个 ELF 按卡面只用 `S3_WB_MANUAL`）。
* 手动白平衡只动 AWB 增益，不改色彩矩阵/UV 调整（`0x5388..0x538B`、`0x5580/0x5583`）；白纸仍偏色时应转向这些寄存器
  与 `0x4300`/`0x501F` 的格式语义。
* v8 保留 v6 的 5 次指纹采样，UART 输出时长仍 ≥30 s；`v8_off` 无 `S3_DIAG8_WB_RB` 行（不写增益）。