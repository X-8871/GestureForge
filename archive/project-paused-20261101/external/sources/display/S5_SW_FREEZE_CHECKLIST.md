# S5 软件冻结清单（P3q / G5 软件侧）

- 任务：阶段5 HDMI 显示链 PS 侧显示软件（P3b-sw → P3q 集成体变体）
- 生成：2026-10-30（UTC+8），**本清单只做核验与记录，未改任何代码/宏，未重编**
- 权威依据：`build/build_record.json`（sha256 `58117d07e65ad6869cfa9e44251741992316f0fb2dc69ab60d4e15e00c1d8b2f`）
  + `build/` 下实际产物（本清单中的哈希均从磁盘现算）
- 边界：离线构建 + 主机自检；本轮**未接触板卡/JTAG/COM4/hw_server，未运行 Vivado，未 git 提交**
- 冻结范围：**P3q 有界 / 长跑 / idleprobe 三份 ELF**（其余变体为兼容/回归用，见 §1.2）

---

## 1. P3q 三份 ELF（冻结交付物）

构建时间（UTC+8）：`2026-10-30T18:48:57`（build_record），ELF mtime 18:48:48–18:48:49；
构建退出码：compile 0 / link 0 / size 0 / nm 0；**警告 0**；符号检查 `missing=[]`。

| 角色 | 文件 | sha256 | 字节数 | berkeley (text/data/bss) | mtime |
|---|---|---|---|---|---|
| **有界（默认，上板用）** | `build/s5_display_app.elf` | `b79d322dfaac87f45d72f5e21c7bfe2fdbc3a34f6cd71da206f5c7f4b2ee3497` | **281,624** | 44,336 / 68 / 2,354,528 | 18:48:48 |
| **长跑（1800 s）** | `build/s5_display_app_longrun.elf` | `6aab247348f8f029c63de0c5a2ca64929af27a4a575c35a6581e91b1a555fd7f` | **284,812** | — | 18:48:49 |
| **idleprobe（10 帧 + 3 s 空闲测速）** | `build/s5_display_app_idleprobe.elf` | `c36b2885a0a78b2ccc9588cb20c9a586bbf933273a20fd1680ee42826f57c3bd` | **285,600** | — | 18:48:49 |

### 1.1 三份 ELF 的编译宏差异（其余完全相同）

| 宏 | 有界 | 长跑 | idleprobe |
|---|---|---|---|
| `S5_LONG_RUN` | 0（默认） | **1** | 0 |
| `S5_IDLE_PROBE` | 0（默认） | 0 | **1** |
| `S5_VDMA_BASE` | `0x43C40000` | 同 | 同 |
| `S5_UF_FRAME_REG` | `0x43C50000` | 同 | 同 |
| `S5_UF_TOTAL_REG` | `0x43C50008` | 同 | 同 |
| `S5_NO_VTC` | 1 | 同 | 同 |
| `S5_TEST_PATTERN` | 1 | 同 | 同 |

其它生效默认值（源码内）：`S5_TEST_PATTERN_HOLD_MS=2000`、`S5_SOURCE_REAL=1`、`S5_DCACHE_FLUSH=1`、
`S5_RUN_FRAMES=180`、`S5_RUN_MAX_MS=60000`、`S5_RUN_MAX_MS_LONG=1800000`、
`S5_IDLE_PROBE_FRAMES=10`、`S5_IDLE_PROBE_MS=3000`、`S5_VDMA_FSYNC=0`。

### 1.2 兼容/回归变体（非冻结交付物，仅备查）

| 变体 | sha256 | 字节 |
|---|---|---|
| P3n 有界 / 长跑 / idleprobe | `c489aad5…` / `9464378f…` / `461ad189…` | 284,324 / 284,744 / 285,504 |
| P3p（fsync）有界 / 长跑 / idleprobe | `47a52f93…` / `bb9fd551…` / `4e19ed7b…` | 284,488 / 284,908 / 285,696 |
| P3b 回归 | `654c0739…` | 323,180 |

（完整哈希见 `build/build_record.json` 的 `outputs.p3n_elfs / outputs.p3p_elfs / outputs.p3b_elf`）

---

## 2. 构建命令与工具链

**一键命令（唯一入口）**：

```bat
cd /d D:\tmp\lead\p3b_display_sw_20261030_r01
python build_s5_display_app.py
```

工具链 / 依赖（均只读引用，未修改）：

| 项 | 路径 / 版本 |
|---|---|
| 编译器 | `D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-gcc.exe`，**GCC 13.4.0**（`arm-xilinx-eabi-gcc.exe (GCC) 13.4.0`） |
| BSP | `D:\codex-worktrees\w4\tmp\4\S4-B-REAL-01\s4b_ps_tensor_20261023_r13\bundle_extract\bundle\workspace\ps7\export\ps7\sw\cpu0` |
| 启动代码 | 同上 `lib/`（`libxil.a` / `libxilstandalone.a` / `libxiltimer.a`）+ `-specs=<BSP>/Xilinx.spec` |
| 链接脚本 | `D:\codex-worktrees\w4\tmp\4\S4-T34\ps_app_build\lscript_s4t34.ld` |
| 源文件 | `src/s5_display_app.c`、`vdma_ctrl.c`、`vtc_ctrl.c`、`s5_timebase.c`、`s5_real_source.c` |

**编译选项（CFLAGS，脚本内固定）**：

```text
-mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -DSDT
-Wall -Wextra -O2 -g3 -std=gnu11 -ffunction-sections -fdata-sections -U__clang__
-specs=<BSP>/Xilinx.spec -I<BSP>/include -Isrc
```

**链接**：

```text
-Wl,-Map=build/s5_display_app.map,--cref,--gc-sections
<objects> -o build/s5_display_app.elf
-L<BSP>/lib -Wl,-T -Wl,<lscript>
-Wl,--start-group -lxilstandalone -lxiltimer -lxil -lgcc -lc -lm -Wl,--end-group
```

**变体增量宏**：长跑 `-DS5_LONG_RUN=1`；idleprobe `-DS5_IDLE_PROBE=1`（仅重编 `s5_display_app.c` 一次，其余 `.o` 复用）。
P3q 三地址/无 VTC 宏是**源码默认值**，命令行不传也成立；显式写法：
`-DS5_VDMA_BASE=0x43C40000u -DS5_UF_FRAME_REG=0x43C50000u -DS5_UF_TOTAL_REG=0x43C50008u -DS5_NO_VTC=1`。

---

## 3. 最小重建步骤（从 `src/` + `tools/` 恢复到三份 ELF）

1. 确认依赖存在（缺一即失败，脚本退出码 2）：`GCC/SIZE/NM`、`BSP/include`、`BSP/lib`、`BSP/Xilinx.spec`、`lscript_s4t34.ld`、`src/` 五个 `.c`。
2. 确认 `src/` 与 §4 的哈希逐一致（见 §6 核验命令）。
3. 执行 `python build_s5_display_app.py`（无需参数；`--skip-host` 只跳过主机自检、不推荐用于冻结核验）。
4. 比对产物（必须逐字节一致；同工具链/BSP 下已验证可复现）：

| 文件 | 期望 sha256 |
|---|---|
| `build/s5_display_app.elf` | `b79d322dfaac87f45d72f5e21c7bfe2fdbc3a34f6cd71da206f5c7f4b2ee3497` |
| `build/s5_display_app_longrun.elf` | `6aab247348f8f029c63de0c5a2ca64929af27a4a575c35a6581e91b1a555fd7f` |
| `build/s5_display_app_idleprobe.elf` | `c36b2885a0a78b2ccc9588cb20c9a586bbf933273a20fd1680ee42826f57c3bd` |

5. 核验命令（Windows PowerShell）：

```powershell
Get-FileHash build\s5_display_app.elf,build\s5_display_app_longrun.elf,build\s5_display_app_idleprobe.elf -Algorithm SHA256
python build_s5_display_app.py      # 期望 exit 0，日志 build\build_s5_display_app.log 内无 warning:
```

6. 主机自检（脚本自动跑，均要求退出码 0）：渲染 PNG（当前 build/ 下 17 张，含 pattern_deterministic）、VTC/VDMA 寄存器序列（P3b 基址假寄存器堆）、
   P3p fsync 位、真实源 6 用例（含 G3-B `box_crc=0x2D949C0C`）。
   证据：`build/selftest_vtc_vdma.txt`、`build/selftest_vtc_vdma_fsync.txt`、`build/selftest_real_source.txt`。

> 说明：可复现性只在**同一 gcc 13.4.0 + 同一 BSP/lscript** 下承诺；换工具链或 BSP 后 ELF 哈希变化属预期，需重新登记。

---

## 4. 源码与工具清单（sha256）

### 4.1 `src/`（12 个文件，全部参与或定义构建）

| 文件 | 字节 | sha256 |
|---|---|---|
| `s5_display_app.c` | 63,909 | `c28a7543a4c86460e7ddd82e1fe1ee5f5ca3f2ebdcca17cf4c3eff2239b09d2a` |
| `s5_display_app.h` | 15,456 | `f77aa2a905f1a5d6667e1e7c72cd4e39a7519f4d864189648c0ebe0c7e42dcee` |
| `s5_real_source.c` | 8,983 | `d7696ecaf5fe174c1c3a376ac7159865cfd06e4025b226ed721ac672a35dffa5` |
| `s5_real_source.h` | 4,379 | `c6d50b3361074d642941173f89fd23eb66867e508d203eb9465af65577416948` |
| `s5_result_abi.h` | 3,829 | `0462f91173616b2ab1e6bc57cfdf1695229c4996a2d1fb87611537329fceab8c` |
| `s5_timebase.c` | 1,500 | `47a3dc27ed2c0dc9c60a326eda979a80d2a9020c69ecd5c8361e66fbdae0de96` |
| `s5_timebase.h` | 2,420 | `3a2e9c8e3da8b4f6c2ea72755d5b428d241788d5da18d15e4b688072d469d64a` |
| `s5_font8x16.h` | 12,040 | `2f26b78b1098b974c60ee2a1d173107c5b44ef8f8f19dbdc4b599ef93a2d50d3` |
| `vdma_ctrl.c` | 10,172 | `bb32bcbebe220a38ad19000a660929834f563a0fe6b82b7968160833da17eff8` |
| `vdma_ctrl.h` | 11,564 | `5634859380f47c7c9d1072907eafbccc8253add014319a36cd1d7af40af83db1` |
| `vtc_ctrl.c` | 12,300 | `8ba7d212b4f5d5ec2781bc84b9041cbe218dd935596644acd72de5bf532b6fa6` |
| `vtc_ctrl.h` | 7,541 | `68d1555cd3a78aff5d206a90229c1184cdd096b3c00f09b441ecb42c24162458` |

### 4.2 `tools/` 与构建脚本（主机自检用，不进 ARM ELF）

| 文件 | 字节 | sha256 |
|---|---|---|
| `host_render_test.c` | 6,684 | `edec1529dfc3b6911bc8550e9991ff41f586c5718b86d3615d148cc0452f1077` |
| `real_source_selftest.c` | 17,256 | `b5963eb1a1fef781e9432f122c4fc517a43efb60363786d73d283994423a0063` |
| `vtc_vdma_selftest.c` | 9,354 | `a6e4fa341ea1e8d1d3c6a622609d72889fb04183100e470f78ad68e3b86d4294` |
| `gen_font8x16.py` | 6,150 | `b9c5a583435d7120f76ae36b17df4a761f347cd1983866fefc66a0b2e3c04b87` |
| `host_xil_shim/xil_io.h` | 798 | `1844e41d2b61f00af0a278d7d7147bdaca605318e24bf7e65155cc40f566e263` |
| `build_s5_display_app.py`（根目录） | 27,839 | `b53e3962b09ecb28519eff242e24f72dbb3f9a9a99a6d2a37fb41604a97dcfa0` |

### 4.3 证据文件（本次冻结核验对象）

| 文件 | 字节 | sha256 |
|---|---|---|
| `build/build_record.json` | 9,114 | `58117d07e65ad6869cfa9e44251741992316f0fb2dc69ab60d4e15e00c1d8b2f` |
| `build/build_s5_display_app.log` | 47,329 | `c5ca0f1b1e10e8807d8180455cdd3f0ffd08a3b71c4a9e535210341737d4e97c` |
| `build/s5_display_app.map` | 220,944 | `10e309cf7c402bc13898b102f1d3a066da2346e7194ee405b8de6b479bed4d6d` |
| `build/selftest_real_source.txt` | 2,119 | `e8a2f2f92fe73a2f8c36e536aa87e6b17fa73cd6d0b5c0659144bb7bf95cbeda` |
| `build/selftest_vtc_vdma.txt` | 1,649 | `04547942d6f9d5fd611e442f180d241a52d483802de2c3435f93465a7135d8bb` |
| `build/selftest_vtc_vdma_fsync.txt` | 1,717 | `1de0c9806ce5da1bdbe474741e0b7c48099065775b36f738667ae664ed12ece7` |
| `S5_P3B_SW_REPORT.md` | 79,716 | `9f4c40145b20fc4cb576dde9d67dc4df5c759d04dd7d73bd96538023b521f516` |

---

## 5. 已知限制（随冻结记录生效）

1. **`vcnt` 是软件计数**：`PARKPTR.READSTR` 切换次数；axi_vdma 6.3 的 SR 无硬件帧计数字段（`XAXIVDMA_FRMCNT_MASK` 属 CR[23:16] 调试字段，需 genlock/调试特性），故 `vcnt ≈` 软件观测到的消耗帧数，不等同硬件帧计数。
2. **时间戳 0 = 未知**：结果块 `cap/inf` 全 0 时 `age_ms=0`、`latency_ms=0`（不用 `now−0` 算巨大值）；时间戳“在未来”同样按 0 处理。
3. **`fps_dis` / `fps_upd` 定义**：`fps_dis`=显示刷新率（VDMA 读帧存切换周期实测，测不到填 0 不虚填）；`fps_upd`=软件更新（渲染）速率=`frames/渲染阶段elapsed`；`fps_cap/fps_inf`=结果块时间戳窗口。
4. **`uf_frame` / `uf_total` 地址**：P3q GPIO `0x43C50000`（ch1 data，本帧欠载，每 vsync 归零）、`0x43C50008`（ch2 data，累计 sticky）；**`+0x04` 是 ch1 三态寄存器，不可当数据用**；`uf_pix` 为兼容字段（= `uf_total`）。
5. **`S5_TEST_PATTERN=1` 两帧存同图**：A/B 都画“8 竖彩条 + 4 px 白框 + 中央白十字”的**同一张**图（避免 circular 输出两帧不同图案造成闪烁），VDMA 启动后保持 2 s 再进入渲染；`=0` 才回到 A=棋盘/B=彩条。
6. **无 VTC**：P3q/P3n 均 `S5_NO_VTC=1`，软件不访问 `0x43C30000`（P3q 该地址不存在），时序由 PL `axis_to_video` 自产；`vtc_ctrl.c` 仍保留但 P3q 主程序不调用。
7. **结果块 ABI 16 B/项 vs 字段合计 12 B**：读端按 16 B 步进、忽略末尾 4 B 填充；生产端必须同一步进（另一 ABI 风险项）。
8. **真实源仅主机验证**：`src/s5_real_source.c` 用 fixture + 合成块离线验证；板上需生产端实际写 `0x20800000`、相机/DMA 填 `0x12000000` 才能验通。
9. **本轮未上板**：VDMA 实际搬数、`axis_to_video` 时序/fsync、TMDS、DDR 带宽、撕裂/闪烁均未在本轮核验；板上行为见此前 P3b/P3n/P3p/P3q 冒烟记录（不在本清单范围）。
10. **DDR 并发**：P3q 上 HP0/HP1(50 MHz) 与 HP2(100 MHz) 并发读同一颗 DDR，2B 单帧耗时与显示欠载可能变化（板级复测，与软件无关）；欠载可由 `uf_frame/uf_total` 直接观测。

---

## 6. 冻结核验记录（本轮离线核验，全部只读）

| 核验项 | 方法 | 结果 |
|---|---|---|
| 三份 ELF 哈希/大小与 build_record 一致 | `Get-FileHash` + `build_record.json` | **PASS** |
| 三份 ELF 由同一构建产生 | mtime 18:48:48–49 + record `built_utc8=2026-10-30T18:48:57+08:00` | **PASS** |
| `src/` 输入哈希与 build_record 一致 | 逐个 sha256 比对（7 项 inputs） | **PASS** |
| 构建退出码 | record `exit_codes` | **PASS**（compile/link/size/nm = 0/0/0/0） |
| 符号检查 | record `symbol_check` | **PASS**（`missing=[]`） |
| 主机自检 | `reg_selftest_vtc_vdma` / `real_source_selftest` / `reg_selftest_p3p_fsync` | **PASS**（exit 0） |
| GPIO 偏移断言 | 编译期 `_Static_assert((TOTAL-FRAME)==8)`（host 渲染自检内） | **PASS** |
| 报告与 build 目录一致性 | 见 §7 | **FAIL（仅文档，未改代码）** |

---

## 7. 发现的不一致（如实记录，请你裁定是否修文档）

**代码/产物无问题**；不一致只在 `S5_P3B_SW_REPORT.md` 的**历史章节未随每次构建更新**：

1. 报告 §0（第 19–20 行）仍写 r06b 时代数值：ELF `62f3595c…` / 309,700 B、长跑 `ad1d2e69…` / 312,892 B ——
   **实际**为 `b79d322d…` / 281,624 B、`6aab2473…` / 284,812 B（本清单 §1 为准）。
2. 报告 §1 交付物表（第 45 行起）的源码哈希是 r05 时代（如 `s5_display_app.c` 写 `3056ede3…`，实际 `c28a7543…`），
   与 §4 本清单不一致。
3. 报告 §11.5（第 716–717 行）的构建数值同为旧值（`62f3595c…` / 309,700 B）。
4. 报告 §11.10 中 P3p 变体哈希（`40cfa6a1…` 等）是 r06f 构建值；当前磁盘为 `47a52f93…`（r06h 重建，差异见 §1.2）。
   —— 原因是 r06g 引入 `uf_frame/uf_total` 两字段后兼容变体亦随之重编；**P3q 三份主交付不受影响**。
5. `build_record.json` 的 `boundary`/`phase` 中文字段在 Windows 控制台显示为乱码，文件本身为 UTF-8 正常（`json.load` 读取正常），非数据损坏。

结论：**P3q 三份 ELF + `src/` 源码可用于 G5 软件侧冻结**；报告顶部历史数值需重生成一次（或明确以本清单 + `build_record.json` 为权威）。
本轮按要求**未改代码、未改宏、未重编**。
