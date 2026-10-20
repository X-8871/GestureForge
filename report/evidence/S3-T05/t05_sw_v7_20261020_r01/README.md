# S3-T05-SW3 v7：ISP/AWB 回读 + AWB 关闭 A/B ELF（task-4）

日期：2026-10-20（UTC+8）｜基线 commit：`41ee5ba003147d77349e8908c38b2efc97752ca8`｜未提交 Git｜**未上板**

用途：验证“彩条蓝色分量只有期望约 42%”是否由传感器 ISP/AWB 造成——先只读回读 AWB/AEC/ISP 实际值，
再用一个启动 S2MM 前关闭 AWB 的 A/B ELF 做对照。同轮保留 v6 的 64 KB 帧缓冲指纹，便于同时确认“仍在写帧”。

## 1. 交付物与哈希

| 产物 | SHA-256 |
|---|---|
| 补丁 `board/stage3/software/sensor/s3_t04_app_diag_v7.patch`（只改 `display_demo.c`，373 行） | `d471317726818a835e5e6aaf25108df688b122f6aacd641e933d48fffcb79cad` |
| ELF `tmp/s3r06/t04_j11cmos2_elf_v7/elf_build/app/an5642_j11cmos2_v7.elf`（默认，AWB 不动） | `f33a10cc46e508002247fb233d44a28bc723b1e87cb8d39f6774f36d133b62af`（306,208 B） |
| ELF `…/an5642_j11cmos2_v7_awboff.elf`（`-DS3_AWB_OFF=1`，启动 S2MM 前关 AWB） | `72d3390933315303ad8dce4af405ff77b020d6a06a5bf1fbf8dceb9053b5293b`（306,208 B） |
| 生成器 `scripts/stage3_t04/make_app_diag_patch.py`（新增 `v7`；默认变体仍为 `v5`） | `bf12bb390a1d6898c9c5696c79aea54cf03f34f32363f509f141b81a30a40820` |

## 2. 命令与真实退出码

| 步骤 | 退出码 | 结果 |
|---|---|---|
| 默认变体回归（无参数） | 0 | 与 `s3_t04_app_diag_v5.patch` **逐字节相同** |
| `v4` 回归 | 0 | 与 `s3_t04_app_diag_v4.patch` **逐字节相同** |
| `v6` 回归 | 0 | 与 `s3_t04_app_diag_v6.patch` **逐字节相同**（`4c7becc1…b960`，与任务卡一致） |
| `v7` 生成 | 0 | `GIT_APPLY_EXIT=0`；`VERIFY_HAS_D7_*` 全 True |
| 厂商副本 `git apply --check -p1 <v7>` | 0 | 只含 `display_demo.c` |
| v7 ELF（SOF 修复 XSA，`run_v7_elf_build.sh`） | 0 | sdtgen PASS + `[OK] ELF`；`display_demo.c` 无 warning |
| AWB-OFF ELF（`run_v7_awboff_elf_build.sh`） | 0 | 日志逐字含 `-DS3_AWB_OFF=1`；`V7_AWBOFF_MAKE_RC=0` |

命令原文见 `build_report.json` 的 `commands`。输入 XSA = `tmp/s3r06/t04_sof_fix_20261020_r01/design_1_wrapper.xsa`（`1f5b138e…cb0e3`）。

**开关生效的机器证据**：默认 ELF 只含字符串 `S3_DIAG7_AWB_OFF=OFF`；AWB-OFF ELF 只含 `S3_DIAG7_AWB_OFF=ON`（互斥）。

## 3. v7 打印内容（上板判读）

1. `S3_DIAG7_AWB=5001=0x%02X 3406=0x%02X 3400..3405=0x%02X,0x%02X,0x%02X,0x%02X,0x%02X,0x%02X 503D=0x%02X 4300=0x%02X 501F=0x%02X`（严格按卡面格式）
2. `S3_DIAG7_AE=3503=0x%02X 3500..3502=0x%02X,0x%02X,0x%02X 3035=0x%02X`
3. `S3_DIAG7_ISP_A=5580..5585=…`、`S3_DIAG7_ISP_B=5586..558B=…`
4. `S3_DIAG7_AWB_OFF=ON before=0x%02X after=0x%02X write_status=%d` + `S3_DIAG7_AWB_OFF_VERIFY readback=0x%02X`（AWB-OFF ELF）；默认 ELF 打印 `S3_DIAG7_AWB_OFF=OFF (0x5001 unchanged)`
5. 保留 v6：`S3_DIAG6_FP`（3 处 × 64 KB，cache 失效后读，t≈5/10/15/20/25 s）、`S3_DIAG6_SR`、`S3_DIAG6_SENS`（t≈30 s）

读不到即 `0xFF`（带传输状态检查的读）；`0xFF` 也可能是合法值，判读须结合位定义。

## 4. 厂商 init 表期望值（对照用，原文见 `vendor_init_extract/`）

| 寄存器 | 厂商写入值 | 厂商注释 |
|---|---|---|
| `0x5001` | `0xa3`（两次） | SDE on, scale on, UV average off, color matrix on, **AWB on**（bit0=1） |
| `0x3503` | `0x00` | AEC/AGC on |
| `0x3035` | `0x21` | PLL（先 0x11 后 0x21） |
| `0x3824` | `0x04` | PCLK manual divider |
| `0x4300` | `0x60` | 厂商注释写 “RGB565” |
| `0x501F` | `0x01` | 厂商注释写 “ISP RGB” |
| `0x5580` / `0x5583` / `0x5589` / `0x558A` / `0x558B` | `0x06` / `0x40` / `0x10` / `0x00` / `0xf8` | saturation on 等 |
| `0x3400..0x3405`、`0x3406`、`0x3500..0x3502`、`0x503D` | **init 表未出现** | AWB 增益/手动增益使能/曝光未由驱动写入 → 由传感器 AWB/AEC 自动环路实时产生；v7 回读的是**当次会话实际值** |

> 判读提示（只陈述厂商源码事实，未在本次任务核对手册原文）：`0x4300=0x60` 的注释写作 “RGB565”、
> `0x501F=0x01` 写作 “ISP RGB”，与“从 DDR 按字节量到三通道”的读法是否一致，建议用 v7 回读值 + 手册原文一并核对。

## 5. A/B 对照怎么用

1. 先跑默认 ELF：`S3_DIAG7_AWB` 行给出 0x5001（应为 0xa3 = AWB 开）与 AWB 增益 0x3400..0x3405；
   `S3_DIAG6_FP` 五次指纹确认仍在写帧。
2. 再跑 AWB-OFF ELF：核对 `S3_DIAG7_AWB_OFF=ON before=0xa3 after=0xa2 write_status=0` 与
   `S3_DIAG7_AWB_OFF_VERIFY readback=0xa2`（若 readback 仍为 0xa3 → 写未生效）。
3. 用同一套彩条测量方法量蓝色分量：
   * 蓝分量恢复到 ~100% ⇒ 成因是 AWB（自动环路对场景的响应）；
   * 蓝分量仍 ~42% ⇒ AWB 不是根因，应转向 0x5580/0x5583（UV adjust）、0x5388..0x538B（color matrix）、或输出格式语义（0x4300/0x501F）。

## 6. 限制 / 未执行

* **未上板**：`S3_DIAG7_*` 实际数值尚未产生；未下载、未运行、未 UART 采集（上板由阶段总控执行）。
* 未跑 Vivado 综合/实现；未烧 QSPI；未提交 Git；未查 OV5640 手册原文核对 0x4300/0x501F 与 0x5001 位定义（只引用厂商源码注释）。
* 回读值是**当次会话实时值**（AWB/AEC 自动环路），两次上板读数不同属正常，不能当固定配置。
* AWB-OFF 只关 `0x5001 bit0`，其它 ISP 块（SDE/CMX/scale/saturation）仍在。
* 若 `0x5001` 读回失败（0xFF），AWB-OFF ELF **跳过写入**并打印 `write_status=-2` 与 `S3_DIAG7_AWB_OFF_SKIPPED`——
  这是相对卡面字面写法的**记录性偏差**（避免用不可信值改写 ISP 使能寄存器）。
* 不适用/未做：无。
* 本任务只做软件与证据；G3 未闭合。