# MVP 推理 → 显示：S5RS 结果块接口（生产者视角，2026-10-31 r01）

> 决策：**复用阶段5 已冻结的 S5RS 结果块**（lead 2026-10-31 决定），不新增 `0x12C07000`。
> ABI 权威文件：`s5_result_abi.h`（r06j 冻结；本 ELF 以**只读**方式原样引用，未改布局）。
> 消费者：显示应用 `s5_real_source.c::S5Real_Parse`（已就绪，video-sw 不需要改 ABI）。

## 1. 谁写、写什么、谁读

| 角色 | 组件 | 行为 |
|---|---|---|
| 生产者 | `s4d_ps_app_mvp.elf`（本任务） | 每轮推理结束后写 S5RS 块（`s4d_mvp_publish()`） |
| 消费者 | 显示 ELF（`s5_display_app.elf` 的 `s5_real_source.c`） | 每显示帧 `S5Real_Parse(0x20800000)`，按 `frame_id` 变化取最新结果；双读校验 magic |
| 位置 | DDR `0x20800000` | 帧缓冲末端 `0x20708000` 之后的预留 8 MiB（不属禁区） |

## 2. 字节布局（little-endian；全部 u32 对齐；**每个框 16 B 步进**）

| 偏移 | 类型 | 字段 | 生产端写入 |
|---:|---|---|---|
| `0x00` | u32 | `magic` | **最后写** `0x53355253`（"S5RS"） |
| `0x04` | u32 | `frame_id` | 推理轮次自增（0,1,2…） |
| `0x08` | u32 | `n_dets` | 0..16（当前解码上限 15） |
| `0x0C` | u32 | `cap_lo` | 帧"采集完成"GT ticks 低 32 位（本实现用**预处理完成时刻**近似） |
| `0x10` | u32 | `cap_hi` | 同上高 32 位 |
| `0x14` | u32 | `inf_lo` | 推理完成（PL 2B DONE_SAFE）GT ticks 低 32 位 |
| `0x18` | u32 | `inf_hi` | 同上高 32 位 |
| `0x1C` | u32 | `status` | bit0=`valid`（本轮结果有效）；本实现成功时 `0x1`，失败时 `0` |
| `0x20+16*i` | u16 x4 | `x,y,w,h` | **原图 640×480 画布像素坐标**（见 §4） |
| `0x28+16*i` | u8 | `cls` | 0..4（见 §3） |
| `0x29+16*i` | u8 | `score_q8` | `round(score*255)`，0..255 |
| `0x2A+16*i` | u16 | `reserved` | 写 0 |
| `0x2C+16*i` | u32 | `pad` | 写 0（ABI 文本"16 B/项"与字段 12 B 的差额，**双方都按 16 B 步进**） |

块总长 `0x120` B（32 B 头 + 16×16 B）；生产端 flush 范围 `[0x20800000, 0x20800120)`。

## 3. 类别索引（权威）

来源：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\gesture.names`（27 B，sha256 `5926aa20da3fa403315e64a116202d355b044d17f6d7949f5709ce9c9ae3d368`），
`gesture.data` / `gesture_train_r1.data` 均 `classes=5, names=gesture.names`；
标注 `labels/test/<类名>/*.txt` 首列实测：fist→0、palm→1、one→2、two_up→3、three→4。

| cls | 训练名 | 中文（MVP 口径） |
|---:|---|---|
| 0 | `fist` | 拳头 |
| 1 | `palm` | 布 |
| 2 | `one` | 数字一 |
| 3 | `two_up` | 数字二 |
| 4 | `three` | 数字三 |

⚠ 注意：MVP 需求列举顺序"一/二/三/拳/布"**不是**索引顺序；显示侧必须用上表 0..4。

## 4. 坐标换算（生产端已做，显示侧直接用像素）

- 推理输入：相机 raw `0x12000000`，BGR888，默认 **1280×720**（`-DS4D_MVP_RAW_W/H` 可改）。
- 预处理：D2 冻结口径 letterbox（端点对齐双线性、v/255、对称量化 1/127、pad 0.5）→ 416×416 CHW INT8。
- 解码：`s2a_decode_nms_reference()` 以**相机原图宽高**做 letterbox 逆变换 → 归一化 `xyxy∈[0,1]`。
- 发布换算：`x_px = round(x_norm * 640)`、`y_px = round(y_norm * 480)`、`w/h = round(|x2-x1|*640 / |y2-y1|*480)`，
  夹到 `[0,639]/[0,479]`，`w/h≥1`，超出画布则裁剪。**cls 已含在框内**，显示侧无需再查表。

## 5. 写/读协议（无锁、读侧不读半成品）

生产端（本 ELF）顺序：
1. 写全部 `dets[]`（仅前 `n_dets` 项）与头字段（`frame_id/n_dets/cap/inf/status`）；
2. `s4d_region_flush(0x20800000, 0x120)` + `dsb`；
3. **最后**写 `magic=0x53355253`；
4. 再 flush 头部 32 B + `dsb`。

读侧（已实现，已核对 `s5_display_app.c:2510`）：每显示帧先
`s5_invalidate(S5_RESULT_BASE, S5_RESULT_BLOCK_BYTES)`（D-cache invalidate），再 `S5Real_Parse()`：
先判 `magic`，再判 `status.valid`，然后 **frame_id 双重读**（前后不一致判 torn，本帧回退到上一帧），
最后按 **16 B 步进**取 `n_dets` 项。`frame_id` 变化才刷新显示；magic 不符/valid=0 → 保持上一帧并置 stale
（阶段5 G0 语义 `B_latest_result_overlay`）。

## 6. 时间语义与显示侧影响（重要）

- `cap_*`/`inf_*` 是 **GT ticks**（333,333,343 Hz）；显示侧按既有 `s5_timebase` 换算 ms。
- 当前整链 **≈47.3 s/轮**（真实时间基座，见 `MVP_INFER_STATUS.md` §3），因此：
  - 显示侧 `age_frame_ns` ≈ 47 s，远超阶段5 `stale_limit_ns=200 ms` ⇒ **每帧都会判 stale**（预期现象，不是 bug）；
  - MVP 验收应看"框是否随手势更新（每轮一次）+ AGE 面板数值"，不要把 stale 当失败判据；
  - 后续提速（160 B 方案）落地后 age 会降到秒级，届时再按 200 ms stale 规则判。
- 本实现 `cap` 用"预处理完成时刻"近似（相机 ELF 尚无采集时间戳字段）；相机接口定稿后可换真值，显示侧无需改。

## 7. 前置条件（窗口执行前核对）

1. 权重已驻留 `0x10100000`：`GFINT8W1` 头、5,903,100 B（sha `f6feb6d4…cc39`）；ELF 启动打印
   `MVP WEIGHTS: GFINT8W1 OK/MISSING`，MISSING 时不要继续采信结果。
2. 相机已出帧到 `0x12000000`（BGR888，1280×720 默认）；**当前无帧同步握手**，相机写入与读取可能撕裂
   （见 §8-U3）。
3. PL 为 2B 平台位流（`0x43C00000` CSR，DONE_SAFE 语义）。
4. 显示 ELF 已支持 S5RS 解析且运行中。

## 8. 未决/风险（不得当成已解决）

| # | 项 | 状态 | 处置 |
|---|---|---|---|
| U1 | 相机确切几何（1280×720 vs 1280×960） | 待 lead 给 | 改 `-DS4D_MVP_RAW_W/H` 重建，ABI 不变 |
| U2 | 权重预载由谁负责（launcher/camera ELF/JTAG） | 未定 | 目前靠外部预载；ELF 只检查+打印 |
| U3 | 相机帧同步（撕裂/半帧） | **未做** | 需相机 ELF 提供 `ready/epoch` 或双缓冲索引；本 ELF 当前直接读 raw |
| U4 | `cap/inf` 时钟域 | GT ticks（单核） | 双核 AMP 时需固定同源，见阶段4 时间基座 |
| U5 | ABI 文本 16 B vs 字段 12 B | 双方按 16 B 步进 | 生产/消费均已按 16 B；联调时保持一致 |
| U6 | 47.3 s/轮下 stale 常亮 | 预期 | 见 §6；提速后复评 |---

## 10. rev r02 追加（2026-11-01）：raw_nz 观测点、双核 core1 版

- **`raw_nz`（可观测点，已加）**：`MVP TIME` 行尾新增 `raw_nz=<0..1024>` = `0x12000000` 前 **4 KB 的非零 u32 个数**。
  判读：`0` = 相机帧没进来/全零（先查相机，不要怀疑推理）；`1024` = 前 4 KB 全非零（有数据）；
  中间值 = 有数据但可能未铺满/黑边。它**不**证明整帧新鲜（无握手，仍可能撕裂）。
- **双核 core1 版 ELF（已加，供双核串联）**：
  `s4d_ps_app_mvp_core1.elf`（`_start=0x02000e14`，bss 到 `0x0218fd10`，
  SHA-256 `c1eaea5908973f479beb36d2046300c256c6493c947247bcac6d36675854ad5e`），
  由 `lscript_s4t34_core1.ld`（ORIGIN 0x02000000）重链接；
  与 core0 显示 ELF（`_start=0x00100e14`，bss 到 `0x00239568`）**地址不重叠**。
  单机自测版仍为 `s4d_ps_app_mvp.elf`（`0x00100000`，SHA `d1e9616f…`）。
- **启动顺序**（双核 MVP）：core0 先（ps7_init → 四动作 → dow 显示 ELF → 相机出帧）→ 两核 stop 时
  `dow -data <gf8> 0x10100000` + `verify -data` → dow core1 推理 ELF → `con` core0 → `con` core1。
  **权重必须在 core1 `con` 前就位**；core1 不需要 core0 任何 ready 标志（自循环轮询 raw）。
- **缓存一致性**：core0 写 raw 的 VDMA 是 DMA 直写 DDR；core1 每轮先 `s4d_region_invalidate(raw)` 再读；
  core1 写 S5RS 后 flush，core0 读前 invalidate（`s5_display_app.c:2510` 已核）——双向都正确，无需额外握手。---

## 11. rev r03 追加（2026-11-01）：raw_blank 安全闸、n_dets=0 语义、ELF SHA 更新

### 11.1 为什么加 raw_blank 安全闸

零输入帧（`0x12000000` 全 0）下，logits 全 0 → `sigmoid(0)=0.5`，objectness×class = **0.25**，
恰好满足解码阈值 `confidence >= 0.25` ⇒ 会产出"假框"（每格/每 anchor 候选，NMS 后最多 15 个）。
这不是"无手势"，而是**误导性框**。因此生产端加了闸：

- 每轮统计 `raw_nz`（raw 前 4 KB 的非零 u32 个数，0..1024）；
- `raw_nz == 0` ⇒ 判定相机帧缺失：**网络照跑**（链路仍被验证），但发布时强制 `n_dets = 0`、
  `status.valid = 1`，并打印 `MVP NOTE raw_blank n_dets=<原值>->0`；
- 不改变 ABI、不改变显示侧解析。

### 11.2 `n_dets=0` 的合法语义（显示侧已按此实现）

- `status.valid = 1`：本帧结果块**有效**（推理跑完、无错误）；`n_dets=0` 表示**该帧无手势**，
  与"结果块不可用"不同。
- 显示侧：`valid=1 & n=0` → `src=real`、HUD `gesture=none` / `conf=0.00`，**不回退 sim**；
  `S5DISP RESULT.pass` 仍可为 1（显示链路健康）。
- 只有 `status.valid=0`（网络/解码错误）才让显示侧走 fallback：raw 有效→`src=real_nobox`，raw 全零→`src=test`；
  `src=sim` 只在 `S5_SOURCE_REAL=0` 或测试图案失败时出现。

### 11.3 ELF 身份（以本节为准，旧 SHA 作废）

| 变体 | SHA-256 | 用途 |
|---|---|---|
| `s4d_ps_app_mvp_core1.elf` | `1acf5d8151e9c6fdb2f96a2335da6496af8c5248357bacd1c1e19eb40f345de5` | **MVP 上板串联（core1）** |
| `s4d_ps_app_mvp.elf` | `3889c705c9d20723c464d2e68e6aba3cfdc8c724c61c6d82b4e67179217d9721` | core0 单机自测 |

（旧 `c1eaea59…` / `d1e9616f…` 为未加 raw_blank 闸的版本，作废。）
---

## 12. rev r04 追加（2026-11-01 03:4x）：**每帧 ACK 修复** + `status` 语义与显示门控

### 12.1 根因（r08/r09 `status=0` 不是写字段 bug）

`0x20800000` dump：`frame_id=0x37A(890)`、`n_dets=0`、`cap/inf` 均停在上电 ~183 s、**`status=0`**。
890 帧 / 183 s ≈ **0.2 s/轮** —— 真网络一轮 47 s，说明 **START 每轮瞬间被拒**：

- 2B 引擎每帧 DONE_SAFE 后必须 **ACK**（读 epoch → 写 `ACKLO/ACKHI` → `CMD=4`）才回 `IDLE|SAFE_REUSE`；
- S4-B 主机路径的 ACK 由 **host 发 `OP_ACK`**；MVP 自循环原先**没有 ACK** ⇒ 下一轮 `s2b_network_start_from_tensor()`
  在 `is_idle()` 失败处返回 **-2** ⇒ 走错误路径 `publish(status=0)` ⇒ 显示侧 `result_not_valid`。
- 所以：**`status=0` 是 ACK 缺失的后果**，不是 status 字段写错；只改 status 掩码会掩盖引擎状态坏掉的事实。

### 12.2 修复内容（本 ELF）

1. 每帧 `DONE_SAFE` 后自动 ACK：`s4d_mvp_ack()`（epoch 双读 → `ACKLO/ACKHI` → `CMD=4` → 轮询回到
   `IDLE && SAFE_REUSE && !OWNER_PL/AXI_PENDING/HEAD_VALID/TERMINAL/FIRST_PENDING`）。
2. 网络失败路径先尽力 ACK 再发布 `status=0`（避免后续每轮空转 -2），并打印 `MVP ERR network rc=…`。
3. **status 语义（已按 lead 要求）**：
   - 一帧被处理（成功跑完网络+解码，**包括 `raw_nz==0`、`n_dets==0`**）⇒ `status = 0x1`（valid）；
   - 只有网络/解码真正失败（`rc≠0`）⇒ `status = 0`（invalid）；
   - **不置 stale(bit2)**、不置 overrun(bit1)：47.3 s/轮下置 stale 只会让 HUD 变告警色，无意义（见 §12.3）。
4. 发布顺序不变：`dets/帧号/cap/inf/status` → flush+`dsb` → **最后写 magic** → flush+`dsb`（status 在 magic 之前）。
5. 回读自检（每帧）：发布后 invalidate + 重读，校验 `magic/status/n_dets`：
   - 失败打印 `MVP ASSERT FAIL s5rs magic=… status=… n=… exp(…)`；
   - `raw_nz==0` 时打印 `MVP CHECK raw_blank status=0x1 n_dets=0 (exp status=0x1 n=0) OK/FAIL`。
6. 编译期断言：`S5_RESULT_ST_VALID==1`、且 `(VALID & STALE)==0`（MVP 不置 stale）。

### 12.3 显示侧门控关系（已核 `s5_display_app.c` / `s5_real_source.c`）

- `S5Real_Parse`：先判 `magic`，再判 **`status.valid`(bit0)**；`valid=0` ⇒ 返回 `result_not_valid`，
  显示侧便走 fallback（raw 有效→`src=real_nobox`，raw 全零→`src=test`）。**这是"灰底"的直接门控**，所以
  `status.valid=1` 对 MVP 必需。
- `stale`(bit2)：仅影响 HUD 颜色（`S5_COLOR_WARN`），**不参与 `pass` 判定**、不改变 `src`；
  显示侧另有 `age_ms>200 ms → AGE_OVER` 仅作 HUD 提示。47.3 s/轮下 AGE 必然 >200 ms，属预期。
- `S5DISP RESULT.pass` 只看：`vdma_init_ok`、`vdma_err==0`、`frames>0`、帧完整性抽检、`src!=sim`；
  与 `n_dets` 无关。故 `n_dets=0`（有帧无手势）**不影响 pass**。

### 12.4 ELF 身份（r04，旧 SHA 作废）

| 变体 | SHA-256 | 字节 |
|---|---|---|
| `s4d_ps_app_mvp_core1.elf`（**上板用**） | `5806d33de1e888bb8b4fb2f63ef64246087316b4335f8b74fbba0710d0b48270` | 267,888 |
| `s4d_ps_app_mvp.elf`（core0 单机备选） | `a5e22651f53b3dcd00e6514034712f1287acb911ee6444bad08e256b5a0f2d47` | 267,888 |
