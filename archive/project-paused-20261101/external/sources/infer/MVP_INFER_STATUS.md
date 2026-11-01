# MVP 推理侧现状、计时口径与提速路线（S5-T01/MVP，2026-11-01 r01）

> 状态：**MVP 推理 ELF 已离线构建**（core0/core1 两版），未上板；本文是给 lead/video-sw 的事实底稿。
> 边界：纯离线；未碰板卡/JTAG/COM4/hw_server、未跑 Vivado 综合、未 git。`ENABLE=0`，不主张 G3/G4/G5。

## 1. 推理入口（谁在跑、从哪进、结果在哪）

| 层 | 组件 | 说明 |
|---|---|---|
| ELF（单机自测） | `D:\tmp\lead\mvp_infer_20261031_r01\build\s4d_ps_app_mvp.elf` | `_start=0x00100e14`；SHA-256 `d1e9616f9cbb20212e117c3476724e6c4abed464c91a70a665a3ad4dca43afa3` |
| ELF（双核 core1） | 同目录 `s4d_ps_app_mvp_core1.elf` | `_start=0x02000e14`（重链接 `lscript_s4t34_core1.ld`）；SHA-256 `c1eaea5908973f479beb36d2046300c256c6493c947247bcac6d36675854ad5e` |
| 源码 | `src\s4d_ps_app_mvp.c`（由 `make_mvp_app.py` 从 w4 `vitis/stage4/ps/s4d_ps_app.c`（sha `c07c26f7…`）定点生成）+ `s4d_sw_preproc.c`、`s2a_ps_decode_nms_reference.c`（S4-B-REAL 同一冻结参考）+ `s5_result_abi.h`（只读引用） |
| 主循环 | `s4d_mvp_cam_loop()`（`__attribute__((noinline,used))`，已核符号） | 相机 raw → D2 letterbox → 2B PL 网络 → 解码/NMS → S5RS |
| 网络入口 | `s2b_network_start_from_tensor(session, frame_id)` | 写 `0x43C00000` 冻结 2B CSR（FRAME/INADDR/INBYTES/WADDR/WBYTES/超时/START），轮询 `STATUS[2:0]==DONE(4)`/FAULT |
| 解码入口 | `s2a_decode_nms_reference()` → `s2a_t62_decode_nms()` | r13 冻结参考；head13 `0x10000000+0x01A46100`（5,070 B）、head26 `+0x01AD5E80`（20,280 B），scale 0.24267549589862975 / 0.30223452951025775 |
| 结果块 | **S5RS `0x20800000`**（lead 2026-10-31 决策，复用阶段5 冻结 ABI） | 每轮 `s4d_mvp_publish()`；详见 `MVP_RESULT_INTERFACE.md` |
| 旧接口（不用） | `s4d_result_t` 64 B @ `0x12C00100` | 只有计数/状态，无框；MVP 不用 |

## 2. 五类索引（权威，别再搞反）

`D:\FPGA_Data\HaGRIDv2\darknet_inputs\gesture.names`（sha `5926aa20…`）= `fist / palm / one / two_up / three`；
`gesture.data`、`gesture_train_r1.data` 均 `classes=5, names=gesture.names`；`labels/test/<类>/*.txt` 首列实测 0..4。
→ **0=拳头 fist、1=布 palm、2=数字一 one、3=数字二 two_up、4=数字三 three**。
任务列举的"一/二/三/拳/布"**不是**索引顺序。

## 3. 计时口径（已定因，勿再混用）

- **权威：整链 ≈47.3 s/轮（真实时间基座）**（lead 2026-10-31 实测；与 w4 `s4d_time_basis_20261029_r01`
  的 47.4–47.6 s/轮一致）。
- 历史 **11.8 s/帧是坏分母产物**（BSP `xtimer_config.h` 宏无括号 ⇒ 有效分母 4×GT；应用自报被压小 4×）；
  **不得再把 11.8 与 35 相加**（会重复计算）。
- **pre/post 分解：尚无可用证据**（S4-B 证据逐文件无 per-stage 计时）。"PS 35 s"来源未证，暂记 UNKNOWN。
  本轮 ELF 已打 4 个 GT 时间戳，一次窗口即可定：
  `MVP TIME t0_pre=… t1_pl=… t2_decode=… t3_pub=… dt_pre=… dt_pl=… dt_dec=… dt_all=… raw_nz=…`
  （语义：t0_pre=预处理完成、t1_pl=PL DONE、t2_decode=解码完成、t3_pub=发布完成；dt_pre=预处理、dt_pl、dt_dec、dt_all=全轮；`raw_nz`=raw 前 4 KB 非零 u32 计数，判"帧有没有进来"）。
- 判读原则：
  - `dt_pl` 占 dt_all 大头 ⇒ 瓶颈在 2B PL 引擎（160 B 方案或换引擎才有意义）；
  - `dt_pre` 大 ⇒ 优化 PS 预处理（当前 D2 double 双线性，可改定点 LUT 且保持逐字节口径，预计 5–10×）；
  - `dt_dec` 大 ⇒ 优化解码（double→float/定点、early-threshold、NMS 早有 15 上限，收益有限）；
  - `raw_nz==0` ⇒ 相机帧没进来（不是推理问题）。

## 4. 保持 416 时的"便宜提速空间"（不改模型/不重建 PL）

| # | 项 | 依据/做法 | 预期收益 | 风险 |
|---|---|---|---|---|
| S1 | PS 预处理定点化 | `s4d_sw_preproc.c` 现为逐像素 double 双线性 + `/255`；用 Q16 查表 + 整数双线性，**保持 D2 逐字节口径**（需回归对拍 da26d385…） | 预处理 5–10×（绝对值待实测，若 dt_pre≈1–2 s 则省 ~1 s） | 舍入口径必须与 D2 完全一致，需冻结张量对拍 |
| S2 | 解码去 double | `s2a_t62_decode_nms` 用 double + 软件 exp；改 float + 查表 sigmoid | dt_dec 若占几十 ms 收益很小；若占数秒才有意义 | 数值容差 1e-6 需复核 |
| S3 | 单帧输出上限 | 已 15 框；可降到 8（显示侧只画前几个） | NMS 微降 | 与判据/参考不一致，需 lead 批 |
| S4 | 搬运/缓存 | 每轮 flush 519,168 B tensor + invalidate heads；改为按产出行粒度维护（需 PL 提供完成范围） | 小幅 | 正确性风险高，不建议先做 |
| S5 | UART 打印降频 | `MVP TIME` 每轮一行（~110 B，47 s/轮下可忽略） | 0 | — |

结论：**416 下没有"便宜的 6.8×"**；S1 最多省 1–2 s，满足不了 3–6 s/帧目标。

## 5. B 方案（160×160）：可行的离线管线与取舍

### 5.1 已确认的离线工具链（都在本机，只读）

- 冻结 416 模型：cfg `…\runs\s1_t02_d8_tiny416_formal_r2\configs\gesture_yolov4_tiny_416_d8_formal.cfg`（sha `5475dff0…`）、
  weights `…\checkpoints\gesture_yolov4_tiny_416_d8_formal_6000.weights`（23,558,276 B，sha `3984affa…`）。
- **量化/校准/打包/前向参考齐全**：`w4\verification\s1_t02_d2_calibration.py`（512 张清单）、
  `s1_t02_d2_activation_calibration.py`（逐层 activation scale）、`s1_t02_d2_int8_weight_reference.py`
  （cfg+weights → `GFINT8W1` 包）、`s1_t02_d2_int8_forward.py`（INT8 整数前向 + requant 参考）。
- 校准所需的 **darknet 构建与 hook 仍在**：
  `D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_activation_calibration_r1\darknet_build\Release\darknet.exe`
  （sha `f025f5ab…`）+ `darknet_source`（hook `network_kernels.cu` sha `0487e694…`，commit `59596d78…`）。

### 5.2 B1：INT8 160（PL 路线）—— 离线可做，但**部署被 PL 卡住**

离线步骤（估 0.5–1 天）：
1. 由 416 cfg 派生 160 cfg（`width=height=160`；anchors 按 160/416=0.3846 缩放→ (3.85,5.38)…(132.3,122.7)，**这是假设**，需精度回归验证）；
2. 用同一 512 张 `calibration.list` + 上面的 darknet/hook 重跑 activation stats → 新的逐层 scale；
3. `s1_t02_d2_int8_weight_reference.py --cfg cfg160 --weights 6000.weights --output gf8_160 ...` 生成新 `GFINT8W1`；
4. `s1_t02_d2_int8_forward.py ...` 在新 head 形状（5×5、10×10）上跑 109 张固定样本，与 416 基线比类别/框/分数；
5. 新 decode 常量（head13 750 B、head26 3,000 B）。
**阻断**：160 的 PL 引擎需要**新的网络引擎位流**；可在本机找到的只有冻结 2B 位流（无 RTL 源码目录），
且 P3b 时序余量已 39 ps ⇒ 重建=新 PL 设计+综合+时序，**不是"明早"能交付**。→ B1 需 lead 明确 RTL 归属/是否准重建 PL。

### 5.3 B2：160 纯 PS 推理（推荐先做，不依赖 PL/不重建位流）

- 用 **float32** 权重（同一 `6000.weights`）在 Cortex-A9 VFP 上跑 YOLOv4-tiny 160：
  算力 ≈ 5.9 GFLOP × (160/416)² ≈ **0.87 GFLOP/帧**；A9@667MHz 实际 0.3–1 GFLOP/s ⇒ **约 1–3 s/帧**，
  加预处理/解码/搬运仍在 **3–5 s** 区间，满足目标；**无量化精度损失、无校准依赖、无 PL 改动**。
- 代价：把 cfg 执行器（38 层：conv/leaky/maxpool/route/upsample/yolo）用 C 写一次（约 1–2k 行，
  可参考 `s1_t02_d2_int8_forward.py` 的层语义与 `verification` 里的 golden），用 109 张固定样本对拍。
  估 1 天（离线），明早可出首版 + 板上一帧计时。
- 若 PS 实测仍 >6 s：再退回 B1（需新 PL）或折中（160 INT8 在 PS 上跑，省 float 带宽）。

### 5.4 建议

**先做 B2-float 160（纯 PS）**：唯一不依赖 PL 重建、不依赖重新校准、且明早能出结果的路线；
同时用新 ELF 的 T0–T3 实测确认 47.3 s 的真实瓶颈（若 dt_pl 才是大头，B2 更显价值）。
B1(INT8 160) 的离线模型/量化包可以在 B2 并行的同时生成（§5.2 步骤 1–5），但**不要承诺明早上板**。

## 6. 上板运行（已给 lead 的 r52/r53 口径；详见本轮消息）

1. core0（显示/相机）先起：`init.elf` ps7_init → 四动作（LVL 0xA→program bit→LVL 0xF）→ `dow` 显示 ELF；
2. 两核 stop 时 `dow -data <gf8> 0x10100000` + `verify -data`（5,903,100 B，sha `f6feb6d4…`，首字 `4E494647`）；
3. `dow` 推理 core1 ELF（`s4d_ps_app_mvp_core1.elf`）→ `con` core0 → `con` core1；
4. 观测：`MVP WEIGHTS: GFINT8W1 OK`、`MVP TIME … raw_nz=…`、`MVP S5RS frame=… n_dets=…`；显示侧看框是否随手势更新。

## 7. 未决/风险

| # | 项 | 状态 |
|---|---|---|
| U1 | 47.3 s 的 dt_pre/dt_pl/dt_dec 真实比例 | **待板上 T0–T3 实测**（本轮 ELF 已仪表化） |
| U2 | "PS 35 s" 的来源 | UNKNOWN；不得与 11.8 s 相加 |
| U3 | 双核可行性 | 两个 standalone ELF 默认同链接 `0x00100000`；已给 core1 重链接版；**未上板验证**（core1 需在 core0 ps7_init 后启动，禁止重跑 ps7_init） |
| U4 | 相机帧同步/撕裂 | 未做握手（lead 决定先接受）；`raw_nz` 仅能判"有数据"，不能判"整帧/新鲜" |
| U5 | B1 的 PL 引擎 RTL 归属 | 未找到 RTL 源码目录，需 lead 确认 |
| U6 | 160 anchors 缩放/精度 | 假设，需 109 张回归 |
| U7 | core1 起 UART 打印 | `xil_printf` 直写 UART 寄存器，依赖 core0 ps7_init 已配好 UART 时钟/引脚；**未上板验证** |