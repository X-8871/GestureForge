# S3-T05-SW5 v9：DVP 端口控制寄存器回读 + 可选可逆写测试 ELF（task-8）

日期：2026-10-21（UTC+8）｜基线 HEAD：`a0c95e4ceb7904878bfcae050d462f28db044fca`｜未提交 Git｜**只构建：不上板、不下载、不烧 QSPI**

用途：验证“蓝 bit7 与绿 bit4 置位率 0.000% ⇒ DVP 两字节 MSB 同时恒 0 ⇒ 单线 `cmos_d[9]` 无信号”
是否由 **`0x301D` bit3（D9 output select = 1，该线输出寄存器固定值）** 造成。若是，则该故障**软件可修**。

## 1. 三个 ELF（文件名固定）

| 文件名 | 编译期配置 | SHA-256（306,272 B） |
|---|---|---|
| `an5642_j11cmos2_v9_read.elf` | 默认（`S3_PAD_SEL_CLEAR=0` / `S3_DVP_ORDER_DEBUG=0`）纯只读 | `b2e8fa55322da275ef6de2a79f3571ec694b9863d7797e1981104b92a02097b5` |
| `an5642_j11cmos2_v9_padclear.elf` | `-DS3_PAD_SEL_CLEAR=1` | `5debc927bafab7492616c6d6280681fa294eb8358e07e33c09aa4ffb02cefbbc` |
| `an5642_j11cmos2_v9_orderdbg.elf` | `-DS3_DVP_ORDER_DEBUG=1` | `eeadef6f370c0318f6d68fb69474958cd119072a8bf792da84ff1ff10ba12e4b` |

目录 `tmp/s3r06/t04_j11cmos2_elf_v9/elf_build/app/`；均由 SOF 修复 XSA（`1f5b138e…cb0e3`）构建，**退出码全 0**。

## 2. 编译行（原文；完整见 `elf_build_evidence.txt`）

```
v9_read     : arm-none-eabi-gcc -O2 -c -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -c display_demo.c -o display_demo.o …
v9_padclear : arm-none-eabi-gcc -O2 -c -DS3_PAD_SEL_CLEAR=1 -mcpu=cortex-a9 … -c display_demo.c -o display_demo.o …
v9_orderdbg : arm-none-eabi-gcc -O2 -c -DS3_DVP_ORDER_DEBUG=1 -mcpu=cortex-a9 … -c display_demo.c -o display_demo.o …
read_dfo(取证): arm-none-eabi-gcc -O2 -c -DS3_PAD_SEL_CLEAR=0 -DS3_DVP_ORDER_DEBUG=0 -mcpu=cortex-a9 … -c display_demo.c …
```

* `v9_read` 由标准入口（`run_stage3_vitis_elf.cmd`，不带 `-D`）构建；为满足“编译行逐字含对应 `-D`”，
  另用 `-DS3_PAD_SEL_CLEAR=0 -DS3_DVP_ORDER_DEBUG=0` 重建对照 ELF `…_v9_read_dfo.elf`，
  **与官方 `v9_read` 逐字节相同**（同为 `b2e8fa55…97b5`）。对照 ELF 不是交付物。
* 机器证据：ELF 内字符串分支互斥；`objdump` 立即数（`0x301D`=12317 / `0x301E`=12318 / `0x4745`=18245）
  read 各 1 次、padclear 为 4/4/1、orderdbg 为 1/1/4，与“只有对应写路径被编进来”一致。

## 3. 判定规则（上板只看一行）

`S3_DIAG9_PAD=3017=… 3018=… 301D=… 301E=… 300A=… 300B=… 4741=… 4745=… 4300=… 501F=… S3_DIAG9_D9SEL=%u D6SEL=%u`

| D9SEL | 含义 | 下一步 |
|---|---|---|
| 1 | `0x301D` bit3 = 1 ⇒ D9 线输出寄存器固定值，假设成立 | 用 `v9_padclear` 复验（写后回读应变成 0，再看 MSB 置位率是否恢复） |
| 0 | 假设排除 | D9 无信号转向引脚/焊接/模块侧（本卡不处置） |
| 255 | `0x301D` **读失败**（未知） | 不能据此下结论；先查 I2C/供电 |

`D9SEL/D6SEL` 只在读成功时才给 0/1；读失败时该寄存器字节与判读位都打 `0xFF/255`（避免把“读不到”误读成“置位 1”）。

## 4. 两个写测试的协议（卡面重点 1）

* `S3_PAD_SEL_CLEAR=1`（`v9_padclear`）：**先回读** `0x301D`/`0x301E` 原值 → 写 `0x301D = 原值 & ~0x08` → **回读校验**；
  `0x301E` **仅当回读 bit1=1 时**才写 `& ~0x02`（否则打印 `S3_DIAG9_FIX_SKIP_301E=1` 且不写）。
  打印：`S3_DIAG9_FIX=301D before=0x… after=0x… readback=0x… 301E before=0x… after=0x… readback=0x… write_status=%d`
* `S3_DVP_ORDER_DEBUG=1`（`v9_orderdbg`）：先回读 `0x4745` → 写 `(原值 & ~0x06) | 0x04`（即 `[2:1]=10`）→ 回读校验；
  **不自动恢复**，打印 `S3_DIAG9_ORDER_WR=4745 before=… after=… readback=… write_status=…` 与 **`S3_DIAG9_ORDER=NOT_RESTORED`**。
* **安全**：任一关键回读失败（I2C 传输失败）时**跳过对应写入**并打印 `*_SKIPPED`，`write_status` 打 `-2`——不用不可信的值改写端口控制寄存器（与 v7/v8 同一原则）。
* **恢复**：UART 里有 `before` 值可手工回写；另外厂商 init 表首两条是 `0x3008=0x82`（软复位）→ 重跑应用或断电重启应恢复默认（**未在实物验证**）。

## 5. 从厂商 init 表查到的事实（对照用）

| 寄存器 | 厂商 init 表 | 说明 |
|---|---|---|
| `0x3017` | `0xff` | 注释：FREX/Vsync/HREF/PCLK/**D[9:6] output enable** |
| `0x3018` | `0xff` | 注释：D[5:0]/GPIO[1:0] output enable |
| `0x301D` / `0x301E` | **未出现** | ⇒ 保持 POR 默认值，**从未被我们的软件回读或设置过** |
| `0x4740` / `0x4741` / `0x4745` | **未出现** | 同上 |

> ⇒ 若 `0x301D` 的 POR 默认把 D9 select 置成 1，症状与实测完全吻合；这正是 v9 要回答的问题。
> 另外 0x3017/0x3018 已写 `0xff`（各数据/同步线 output enable 全开），所以“D9 被 output-disable”这一路径已被厂商 init 表排除，
> 剩下的候选正是 `0x301D` 的 output **select**。

## 6. 命令与退出码（全 0）

| 步骤 | 退出码 | 结果 |
|---|---|---|
| 默认变体回归（无参数） | 0 | 与 v5 补丁**逐字节相同** |
| `v4` / `v6` / `v7` / `v8` 回归 | 0 / 0 / 0 / 0 | 分别与 v4 / v6 / v7 / v8 补丁**逐字节相同** |
| `v9` 生成 | 0 | `GIT_APPLY_EXIT=0`；`VERIFY_HAS_D9_*` 全 True；`VERIFY_HAS_D9_NO_RESTORE_CODE=True` |
| 厂商副本 `git apply --check` | 0 | 只含 `display_demo.c` |
| `v9_read` 构建 | 0 | 标准入口 sdtgen+make |
| `v9_padclear` / `v9_orderdbg` / `read_dfo` 构建 | 0 | 3 条编译行各含自己的 `-D` |

## 7. 限制 / 未执行

* **未上板、未下载、未采集 UART**（Wong 指示暂不上板）→ `S3_DIAG9_*` 实际数值与 D9SEL 结论尚未产生。
* 未跑 Vivado 综合/实现；未烧 QSPI；未提交 Git；未查 OV5640 手册核对 `0x301D/0x301E/0x4745` 位定义（只用任务卡口径与厂商 init 表事实）。
* `padclear` 只清 D9 select 位（并在 bit1 确实置起时清 D6），不动 `0x3017/0x3018` 的 output enable。
* `orderdbg` 改 DVP 输出顺序，可能造成额外错位/花屏（属预期），且**不会自动恢复**。
* v9 保留 v6 的 5 次指纹采样，UART 输出时长仍 ≥30 s；本卡只做软件与证据，G3 未闭合。