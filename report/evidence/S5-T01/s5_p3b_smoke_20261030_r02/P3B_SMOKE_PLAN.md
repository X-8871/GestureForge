# P3b 上屏冒烟：板级窗口操作单与判据（S5-T01，2026-10-30 r01，离线编写）

> 状态：**脚本已离线写好并 dry-run 通过；未上板、未跑 Vivado、未 git**。
> 执行窗口：由 lead 独占板卡后按其流程开窗；本文件是给 lead/执行者的操作单。
> 编号：HDMI 显示链 = **阶段5**（S5-T01）。
> 边界：`ENABLE=0`；不烧 QSPI；不改线；不 push；**PL 编程后禁 `rst -system`**；不主张 G3/G4/G5。

## 1. 目的与产物

- 目的：在 P3b 候选位流上跑显示 ELF，验证 **DDR → VDMA → VTC → rgb2dvi → HDMI 720p60 出图** 的最小闭环，
  用 UART 的 `S5DISP RESULT=` 一行机器可读结果按写死判据判定 PASS/FAIL。
- 执行器：`run_p3b_smoke.py`（同目录；本文件 §7 有命令）。
- 若不满足判据：**停、保原文、回报 lead**，不重试、不放宽判据。

## 2. 物料与身份（IDENT，先核 SHA 再碰板）

| # | 物料 | 路径 | 期望 SHA-256 |
|---|---|---|---|
| 1 | **P3b 位流**（尚未产出） | `D:\tmp\lead\p3b_video_20261030_r01\out\s4d_p3b_r01.bit` | 产出后由 lead 给出，用 `--expect-bit-sha` 传入 |
| 2 | 显示 ELF（当前基线，**待重建**） | `D:\tmp\lead\p3b_display_sw_20261030_r01\build\s5_display_app.elf` | `9fdec1d909054b1a08fdcd9a6b048fc8e0381327dc07e711e9c85d8de8790b38`（268,184 B）；重建后用 `--expect-elf-sha` 传新值 |
| 3 | 驱动 v3.2.7 | `D:\codex-worktrees\w4\scripts\stage4_s4b\run_bringup_driver.py` | `6c41ff4c4c4043d8f53ff963806f8e3e5211086ca8de204b0773985898d4e461` |
| 4 | init ELF（ps7_init 载体） | `D:\codex-worktrees\w4\report\evidence\S4-B\s4b_ps_tensor_20261023_r13\verified_payload\init.elf` | `237dd959f903589c657b743ea1fce175628aaa24020384058fc66339c779e7b1`（170,592 B） |
| 5 | 串口 | COM4 @ 115200（沿用既有窗口流程） | — |
| 6 | 显示器 | HDMI 输入，**必须能锁 1280×720@60**（见 §6） | — |

基址/约定（来自 P3b 设计，只读引用）：VTC `0x43C30000`、VDMA `0x43C40000`、
帧缓冲 A `0x13000000` / B `0x13384000`（1280×720×4 = 3,686,400 B/帧，A/B 双缓冲）。

## 3. HDMI 接线与 OEN

- 引脚（来自 `D:\tmp\lead\p3b_video_20261030_r01\p3b_tmds.xdc`，厂商参考工程第 4–17 行）：

  | 信号 | 引脚 | 电平 |
  |---|---|---|
  | `TMDS_clk_p` / `TMDS_clk_n` | **U13** / （N 由 P 推出） | TMDS_33 |
  | `TMDS_data_p[0]` / `_n[0]` | **W14** / （N 由 P 推出） | TMDS_33 |
  | `TMDS_data_p[1]` / `_n[1]` | **Y18** / （N 由 P 推出） | TMDS_33 |
  | `TMDS_data_p[2]` / `_n[2]` | **Y16** / （N 由 P 推出） | TMDS_33 |
  | `hdmi_oen` | **V16** | LVCMOS33 |
- **`hdmi_oen` 由 PL 内部逻辑驱动，软件不控制**；其有效电平（高有效/低有效）以厂商参考工程为准。
  若黑屏：先量 **V16 电平**是否与厂商参考工程一致（同一 bit 同一逻辑，正常应与参考一致），
  再查显示器输入源/线缆。**不要飞线、不要改 XDC、不要改 top**（均只读）。
- 显示器：接板卡 HDMI OUT；输入源手动选 HDMI；分辨率/刷新率置自动或 1280×720@60。
- 时钟（来自 P3b 设计/构建报告）：像素时钟 `74.21875 MHz`、5x 串行时钟 `371.09375 MHz`
  （clk_wiz 整数分频的近似；相对标准 720p60 的 74.25/371.25 MHz 偏差 −0.042%，显示器一般可容忍）。

## 4. 上板步骤（窗口执行器按此顺序；任一步失败即停）

> 统一要求：PL 编程后**绝不 `rst -system`**；装载只用 `drv.load_elf_ddr`（已编程时走 `rst -processor -stop`，
> 保住 PL 配置）。所有命令/输出落证据目录。

| 步 | 动作 | 期望/判据 | 失败即停（见 §5） |
|---|---|---|---|
| **S1** | IDENT：核 4 个 SHA + 文件存在 | 全部 match；位流存在（若给 `--expect-bit-sha` 必须匹配） | 停，不碰板 |
| **S2** | 板卡前置：无重型进程、3121 无 LISTENING、无 index.lock、空闲内存 ≥1 GB、COM4 可开 | 全 PASS | 停，不碰板 |
| **S3** | 起 hw_server（自起 PID）→ xsdb 枚举 | 3121 LISTENING；`targets` 里见 `Cortex-A9` | 停、杀自起 hw_server |
| **S4** | 2B 四动作：SLCR UNLOCK(0xDF0D) → `LVL_SHFTR_EN=0xA` → **编程 P3b 位流**（`program_2b_bit.tcl`，期望 `PROGRAM_OK`）→ `LVL_SHFTR_EN=0xF` 并读回断言 | 四动作全 PASS；无 `rst -system` | 停（PL 状态不明则不再写 PL） |
| **S5** | `load_elf_ddr(显示 ELF, hold_reset=True)`：init.elf ps7_init（con 2500 ms）→ `rst -processor -stop` → dow 显示 ELF → LVL 0xF 断言 → con | xsdb exit=0 且无 xsdb 错误文本 | 停 |
| **S6** | UART 采集：needle `S5DISP RESULT=`，窗口 **90 s**（≥60 s 硬下限）；只解析完整行 | 见到结果行；末尾半行丢弃（单独记 `S5DISP_uart_tail_partial.txt`） | 停（窗口内无结果行） |
| **S7** | 判据 J-1…J-8（写死，见 §4.1） | 全 PASS ⇒ `P3B_SMOKE_PASS` | 停（任一 FAIL） |
| **S8** | 收窗：关串口 → 杀自起 hw_server → 核验 3121 无 LISTENING、无残留重型进程 → 写 `window_close.txt` | 3121=0 且无残留 | 记 `STOPPED_TEARDOWN_FAIL` |

### 4.1 判据（写死，不得放宽；改判据须新 RunId + lead 批准）

| ID | 判据 | 阈值/处理 |
|---|---|---|
| J-1 | `S5DISP RESULT` 行存在，JSON 可解析，且含 `pass/fps_cap/fps_inf/fps_dis/latency_ms/age_ms/vdma_err` | 缺键/解析失败 ⇒ FAIL |
| J-2 | `pass == 1` | 写死 |
| J-3 | `vdma_err == 0` | 写死 |
| J-4 | `fps_dis >= 55`（720p60 理论 60） | **且 `<= 90`**；>90 视为单位歧义（疑似 ×10）⇒ **FAIL，不猜** |
| J-5 | `age_ms <= 47317` | = 47300 + 17（47.3 s 推理周期 + 17 ms 抖动） |
| J-6 | `0 <= latency_ms <= 1000` | 数值合理（排除 0xFFFF/负数/离谱值） |
| J-7 | 结果行/JSON 无 `error`/`timeout` 语义 | fail-closed（出现即 FAIL） |
| J-8 | UART 结果窗 ≥60 s；末尾半行丢弃、不计入判据 | 脚本强制 |

预期结果行样例（**单位待 SW 冻结，见 §8-U1**）：

```
S5DISP RESULT={"pass":1,"fps_cap":30,"fps_inf":28,"fps_dis":60,"latency_ms":17,"age_ms":47310,"vdma_err":0}
```

## 5. 异常停止点（统一处置：停、保日志、回报 lead，不重试、不 `rst -system`）

| 停止点 | 触发 | 处置 |
|---|---|---|
| **X1** IDENT 失败 | 位流/ELF/驱动/init SHA 不匹配或文件缺失 | 停；**这是最常见的"位流还没产出"**，回 lead 拿 SHA |
| **X2** P0 失败 | 重型进程/3121/COM4/index.lock/内存 | 停；等资源释放后**新 RunId** 再来 |
| **X3** 枚举失败 | 无 Cortex-A9 / xsdb 报错 | 停；杀自起 hw_server；查 JTAG 线/电源 |
| **X4** 四动作失败 | `program_2b_bit.tcl` 无 `PROGRAM_OK` / LVL 断言失败 | 停；PL 状态不明，**不得再写 PL/不得复位救场** |
| **X5** 装载失败 | xsdb exit≠0 或日志命中错误文本 | 停；保留 xsdb 日志 |
| **X6** 无结果行 | 90 s 内未见 `S5DISP RESULT=` | 停；把 UART 原文交回（很可能是显示 ELF 还没实现该打印，见 §8-U2） |
| **X7** 判据 FAIL | J-1..J-7 任一 FAIL | 停；保留 `W3_judgement.json`，按字段定因 |
| **X8** 收窗异常 | 3121 仍 LISTENING / 残留重型进程 | 记为 `STOPPED_TEARDOWN_FAIL` 并回报 |

另：**黑屏但 J 全 PASS** 属于"机器判据 PASS、显示面未验证"——必须人工确认屏幕（见 §6），
不得仅凭 UART 判定"上屏成功"。

## 6. 显示器与降级建议（"显示器不支持 720p60"风险）

P3b 位流固定输出 720p60；PL **不读 EDID**（TMDS 单向），所以显示器必须自己接受该时序。降级阶梯（按顺序）：

1. **首选**：换一台支持 1280×720@60 的显示器/电视（绝大多数 1080p 显示器也接受 720p60 输入）。
2. 用 **HDMI→DVI 转接头 + DVI 显示器**（TMDS 电气兼容；需显示器支持 720p60）。
3. 用 **HDMI 采集卡/示波器**确认板卡确有 TMDS 输出（像素时钟 74.21875 MHz、5x 371.09375 MHz），
   把"板卡出图"与"显示器锁相"两个问题分开定因。
4. 若显示器只支持 1080p：**软件无法降级**（位流固定 720p60），需重建 1080p 位流（P3c，超本任务范围，
   回 lead 决策；且 1080p 的 5x 时钟 742.5 MHz 对 OSERDESE2 与 -2 器件时序是否可行需重新评估）。
5. 诊断顺序（黑屏）：显示器 OSD 是否显示 `1280x720@60` → 量 V16(OEN) 电平 → JTAG 看帧缓冲
   `0x13000000` 内容（先 `loadhw` 注册内存映射，**禁 `mrd -force`**）→ 查 BD 中 `v_axi4s_vid_out`
   的 `locked` / VDMA `SR/CR`（需软核辅助读，不在本脚本内；由 lead 决定是否加诊断）。
6. **照片占位**：屏幕正常时手机拍照（含显示器 OSD 的 1280×720@60），命名 `screen_720p60.jpg`；
   照片只作**人工佐证**，不参与 J-1..J-8 机器判据。

## 7. 运行方式

```bash
# 0) 离线下先 dry-run（不碰硬件；位流未产出也能跑）
python -B run_p3b_smoke.py --dry-run

# 1) 离线判据自测（14 个正/负例，不碰硬件）
python -B run_p3b_smoke.py --self-test

# 2) 真实窗口（lead 独占板卡时）——位流/ELF SHA 由 lead 给
python -B run_p3b_smoke.py --run-id s5_p3b_smoke_20261030_r01 \
    --expect-bit-sha <P3b 位流 SHA-256> --expect-elf-sha <显示 ELF SHA-256> \
    --collect-seconds 90
```

证据目录（脚本创建并写原始日志，manifest 由 lead 做）：
`D:\codex-worktrees\w4\report\evidence\S5-T01\<RunId>\`
- `S1_IDENT.json` … `S8_teardown.json`（逐步）+ `.exit_code.txt`
- `S5DISP_uart.log`（完整行）、`S5DISP_uart_tail_partial.txt`（末尾半行，不解析）
- `W3_judgement.json`（逐条判据）、`results_p3b_smoke.json`（总结）、`window_close.txt`
- `PL_program.log` / `S5_load_display.log` / `S3_enum.log` 等驱动日志

## 8. 依赖与未决（执行前必须确认）

| # | 项 | 状态 | 影响 |
|---|---|---|---|
| U1 | `fps_dis` 单位（整数 fps 还是 ×10） | **未冻结** | 判据 J-4 按整数 fps 写死；若 SW 打 ×10，脚本会以"单位歧义"FAIL（不猜）。请 SW 侧冻结为整数 fps 或明确 `fps_dis_x10` 键名后改判据 |
| U2 | 显示 ELF 目前**没有** `S5DISP RESULT=` 打印（`s5_display_app.c` 主循环为 `for(;;)`，只每 60 帧打 `frame ...`） | **必须重建** | 当前 ELF 跑本窗口会在 X6 停（无结果行）；这是预期行为，不是脚本缺陷 |
| U3 | P3b 位流尚未产出（`out/` 为空） | **等 lead** | dry-run 已报告缺失；真实窗口 X1 停 |
| U4 | `age_ms ≈ 47.3 s` 的依据 | 已记录 | 来自时间基座定因：真实 ≈47.4 s/推理轮（旧应用口径 11.8 s 为坏分母）；J-5 取 47317 ms |
| U5 | `hdmi_oen` 有效电平 | **UNKNOWN** | XDC 只给引脚；由 PL 逻辑决定，参考厂商工程；黑屏先量 V16 |
| U6 | 显示器是否锁 720p60 | 现场确认 | 见 §6 降级阶梯 |
| U7 | `S5DISP RESULT` 的打印时机/次数 | 未冻结 | 脚本取**最后一条**完整结果行；若 SW 周期性打印，最后一条即最新 |

## 9. 禁止清单（违反即整窗作废）

1. PL 编程后 `rst -system`（会清 PL 配置）；2. `-force` / 手写非法 CSR 探测；
3. 改 XDC/top/BD/RTL（全部只读）；4. 烧 QSPI、改线、飞线；
5. 放宽/临时改判据；6. 失败后重试同一窗口（应新 RunId + 定因）；
7. 用 P2a/P2b/P2c 位流冒充 P3b；8. 把 UART 判据 PASS 直接写成"上屏验收通过"。