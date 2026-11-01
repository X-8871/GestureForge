# MVP 上板串联判据清单（M1–M6，2026-11-01 r01，给 board-runner）

> 链路：core0 显示 ELF（相机+HUD，`s5_display_app_p3r_camera.elf`，SHA `6a4a252d…`）
> → 两核 stop 时权重 `dow -data`+`verify -data` → core1 推理 ELF（`s4d_ps_app_mvp_core1.elf`，SHA `1acf5d81…`）
> → 采集 90 s。判据**写死**，不得临时放宽；失败即停、保原文、不重试、不 `rst -system`。
> 推理侧 UART 行全部来自本任务 ELF；显示侧行来自 `s5_display_app.c`（video-sw），格式已核。

## 0. 先核身份（任何不符即停）

| 项 | 值 |
|---|---|
| 显示 ELF | `s5_display_app_p3r_camera.elf`，SHA-256 `6a4a252da120f7712c4e566f33cf44306ffccf639814c08b88323d256c431df7`（393,128 B） |
| 推理 ELF（core1） | `s4d_ps_app_mvp_core1.elf`，SHA-256 `5806d33de1e888bb8b4fb2f63ef64246087316b4335f8b74fbba0710d0b48270`（267,888 B，`_start=0x02000e14`） |
| 推理 ELF（core0 单机备选） | `s4d_ps_app_mvp.elf`，SHA-256 `a5e22651f53b3dcd00e6514034712f1287acb911ee6444bad08e256b5a0f2d47` |
| 权重 | `D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_tiny416_int8_weight_r2\gesture_yolov4_tiny_416_int8_weights.gf8`，SHA-256 `f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39`，5,903,100 B |
| 权重装载 | `dow -data <gf8> 0x10100000` 后 `verify -data <gf8> 0x10100000`；回读 `mrd 0x10100000` = `4E494647`（"GFIN"） |

## M1 位流/PL 编程

- 期望 UART/日志（Vivado 侧）：`PROGRAM_OK`；四动作 LVL 0xA→0xF 后读回 `LVL_SHFTR_EN=0xF`。
- PASS：`PROGRAM_OK` 出现 且 0xF 读回断言成功 且 **全程无 `rst -system`**。
- FAIL：无 `PROGRAM_OK` / LVL 断言失败 → 停（PL 状态不明，不再写 PL，不复位救场）。

## M2 权重驻留（硬前置，必须在 core1 `con` 前）

- 期望命令退出码：`dow -data` = 0 且 `verify -data` = **0**（xsdb 内建逐字节校验）。
- 期望 UART（core1 启动首行之一）：`MVP WEIGHTS: GFINT8W1 OK @0x10100000`。
- PASS：verify=0 **且** 出现 `GFINT8W1 OK`。
- FAIL 处置（回退）：
  1. `verify -data` ≠0 → 重传一次（`dow -data` 再 `verify -data`）；仍失败 ⇒ **停**，不 `con` core1；
  2. verify=0 但 UART 打 `MVP WEIGHTS: MISSING(GFINT8W1)` ⇒ 地址/覆盖冲突（core1 镜像或其它写入覆盖了 `0x10100000`）→ 停，回报；
  3. 不得用"跳过权重直接跑"当作 PASS。

## M3 相机帧源（core0 先起）

- 期望 UART（显示 ELF，任选其实际格式，出现即算）：
  - `CAM: init OK chip=0x5640 1280x720 stride=… raw=0x12000000 (24bpp BGR888)`（成功路径；芯片 ID 以实物为准）
  - 或 `CAM: FAILED rc=…（…）→ 继续显示测试图`（相机未通；仍可判显示，但 M3 记 FAIL）
  - `=== S5 P3B display app (P3b-sw, offline build) ===`、`source: real (result block @20800000 magic=53355253, raw @12000000 … BGR888)`
- 推理侧可观测：首轮 `MVP TIME … raw_nz=<n>`，`n>0` 表示 `0x12000000` 前 4 KB 有数据。
- PASS：`CAM: init OK` 且 至少一条 `MVP TIME` 的 `raw_nz>0`（或 JTAG `mrd 0x12000000` 非零）。
- FAIL：`raw_nz` 恒 0 / raw 全零 → 相机或 VDMA 未出帧，M3 FAIL（推理结果不可信）；停并回报。

## M4 推理首轮（core1 自循环，无需 host 触发）

- 期望 UART（逐轮一行，TT 为 GT 毫秒）：
```
MVP APP: CAM=1 raw=0x12000000 1280x720 bgr888 bytes=2764800 s5rs=0x20800000
MVP WEIGHTS: GFINT8W1 OK @0x10100000
MVP TIME t0_pre=1234 t1_pl=48434 t2_decode=48494 t3_pub=48510 dt_pre=1180 dt_pl=47200 dt_dec=60 dt_all=48456 raw_nz=1024
MVP S5RS frame=0 n_dets=1 magic=0x53355253 status=0x1
```
- PASS（M4）：≥1 条 `MVP TIME`，且 `raw_nz>0`，且 `dt_pl ≤ 90000`（2B 网络超时 0xFFFFFFFF≈85.9 s @50 MHz，超过即链路异常）。
- 若 `0x12000000` 全零：会打 `MVP NOTE raw_blank n_dets=…->0`，此时 M4 的 raw_nz 判据 FAIL（但程序不崩）。
- 90 s 窗口在 47.3 s/轮下只够 **1–2 轮**：**不要求**多轮。
- FAIL：90 s 内无 `MVP TIME` → 停（先查 PL 是否编程/权重是否 OK/串口是否被 core0 占用）。

## M5 S5RS 发布 + 显示消费（MVP 核心判据）

- 推理侧期望：`MVP S5RS frame=<k> n_dets=<0..15> magic=0x53355253 status=0x1`（magic 必须一致）。
- 显示侧期望（每帧/结束时）：
```
S5DISP frame=1234 lat=17 age=47310 st=0 sr=0 src=real nbox=1
S5DISP boxes n=1 crc=<u32> hex=<x y w h …>
S5DISP done frames=5400 vcnt=…(sw) vdma_err=0 idle_fps=… idle_us=…
S5DISP RESULT={"pass":1,"fps_cap":…,"fps_inf":…,"fps_dis":60,"fps_upd":…,…, "latency_ms":…,"age_ms":…,"vdma_err":0,"frames":…,"vcnt":…,"box_crc":…,"fb_crc":…,"uf_*":…,"src":"real"}
APP: gesture_changed from=none to=fist
APP: gesture=fist cls=0 conf=0.95 latency_ms=17
```
- **n_dets=0 的合法判读**：`status.valid` 仍为 1（有帧、无手势 ≠ 无效帧）→ 显示侧 HUD 显示 `gesture=none`，
  `S5DISP frame … src=real nbox=0`，`pass` 仍可为 1（显示链路健康）；**不得**把 n_dets=0 判成"结果块无效/失败"。
- **`APP: gesture=` 行不保证出现**：它只在 `result.frame_id % 30 == 0` 且 cls<5 时打印；本链每轮 47.3 s，
  该行**最多每 30 轮一次（≈23 min）**，90 s 窗口内**几乎不会出现**。**判据改用**：
  - `APP: gesture_changed from=… to=…`（切换时打，首帧有检测即出现），或
  - `S5DISP frame=… src=real nbox=≥1` + `S5DISP boxes n=≥1 …`。
  要求 board-runner **不要**把缺少 `APP: gesture=` 判为失败；这是显示侧帧号条件，不是推理问题。
- PASS（M5）：`MVP S5RS … magic=0x53355253` ≥1 条 **且** 显示侧 `S5DISP frame=… src=real` ≥1 条
  **且** 最终 `S5DISP RESULT.pass==1`、`vdma_err==0`、`src` ∈ {`real`, `real_nobox`}。
- 若显示侧理由出现 `raw_frame_blank`（src=test）：M3/M4 的 raw 判据已 FAIL，本窗口不判 MVP PASS。

## M6 收窗

- 期望：停核 → 杀自起 hw_server → `3121` 无 LISTENING → 无残留重型进程 → `window_close.txt` 落盘。
- PASS：`3121=0` 且无残留；`window_close.txt` 写明 RunId、结论、各判据、UART 日志路径、权重/ELF/位流 SHA。

## 判据总表（写死）

| ID | 条件 | 来源行 |
|---|---|---|
| J1 身份 | 4 个 SHA 全 match（位流由 lead 给；显示 ELF `6a4a252d…`；推理 `1acf5d81…`；权重 `f6feb6d4…`） | IDENT/命令 |
| J2 PL | `PROGRAM_OK` + LVL 0xF 读回 + 无 `rst -system` | Vivado/日志 |
| J3 权重 | `verify -data`=0 + `MVP WEIGHTS: GFINT8W1 OK` | xsdb/推理 UART |
| J4 帧源 | `raw_nz>0`（≥1 条 MVP TIME）或 JTAG `mrd 0x12000000` 非零 | 推理 UART |
| J5 推理 | ≥1 条 `MVP TIME`，`dt_pl ≤ 90000 ms` | 推理 UART |
| J6 结果块 | ≥1 条 `MVP S5RS … magic=0x53355253`，`n_dets≤15` | 推理 UART |
| J7 显示 | `S5DISP RESULT.pass==1`、`vdma_err==0`、`src∈{real,real_nobox}` | 显示 UART |
| J8 收窗 | 3121=0、无残留、`window_close.txt` 存在 | 主机 |

## 失败分支（不重试、不复位救场）

| 现象 | 判定 | 动作 |
|---|---|---|
| `MVP WEIGHTS: MISSING` 或 verify≠0 | M2/J3 FAIL | 停；不 `con` core1；重传一次仍失败即回报 |
| 90 s 无 `MVP TIME` | M4/J5 FAIL | 停；查 PL 编程、core1 是否 `con`、串口冲突 |
| `MVP TIME` 有但 `raw_nz=0` | M3/J4 FAIL | 停；查相机/VDMA；显示侧会显示测试图（`src=test, reason=raw_frame_blank`） |
| `MVP S5RS` magic 不符 | M5/J6 FAIL | 停；查是否有其它生产者覆盖 `0x20800000` |
| 显示 `S5DISP RESULT.pass=0` + `reason=vdma_error` | M5/J7 FAIL | 停；显示链路问题，与推理无关 |
| `src=sim` | 结果块不可用 | FAIL；先看 J3/J6 |
| 缺 `APP: gesture=` 行 | **不算失败** | 见 M5 说明，用 `gesture_changed`/`S5DISP frame` 代替 |

## 回传材料

1. UART 原始日志（整段，含 `=== S5 P3B display app` 到 `S5DISP RESULT`）；
2. `MVP TIME` / `MVP S5RS` / `MVP WEIGHTS` / `MVP NOTE raw_blank` 行原样；
3. `S5DISP RESULT={...}` 原样 + `S5DISP done …`；
4. 屏幕照片（人工佐证，不参与机器判据）；
5. 四条 SHA + `verify -data` 退出码 + `window_close.txt`。
## 附：r04 变更（2026-11-01 03:4x）—— 必读

- **ELF 已更新（含每帧 ACK 修复）**，SHA 见「0. 先核身份」最新表（core1 `5806d33de1e8…`）；旧 `1acf5d81…` 作废。
- **`status` 期望值**：`MVP S5RS … status=0x1`；若见 `status=0x0` ⇒ 网络/解码失败（看紧邻 `MVP ERR network rc=…`
  行；最常见 `rc=-2` = 上一轮未 ACK/引擎未回 idle）。**不得**把 `status=0` 当作"可接受"。
- **新增自检行**：`MVP CHECK raw_blank status=0x1 n_dets=0 (exp status=0x1 n=0) OK`
  （相机未通时出现；FAIL 则逐轮 `MVP ASSERT FAIL`）。
- `stale` 位：生产端**不置**（bit2=0）；显示侧 stale 只影响 HUD 颜色，不影响 `pass`/`src`。
- M4 判据不变；M5 增加一条：`MVP S5RS … status=0x1` ≥1。
