# S5 生产者冻结记录 **rev4 / 身份 A**（阶段6 G4/G5 软件冻结件）

- 生成 2026-10-31（UTC+8）。**身份 A（Wong 裁定）不变**：sidecar `0x20800000+0x100`、`n_dets ≤ 14` fail-closed、flush **`[0x20800000,0x20800120)`（288 B）**。**rev4 = C4 复审修正**：seqlock 写者/消费者顺序严格化（见 §3），旧 rev1/rev2/rev3 全部作废仅存档（`build/rev2_archived/`、`build/rev3_archived/`）。
- 口径依据：`docs/obsidian-project/02-方案设计/阶段6_交互控制_6D口径冻结_20261030.md`（rev4）。
- 边界：离线构建 + 主机自检；未接触板卡/Vivado/git；只重编 producer 系列（显示三件套未重编）。
- 构建记录：`build/p3q_producer_A_rev4_record.json`（sha256 `a75fb173a3f6cb09bf5461ef171450ac60ad4358f1819c4027bd2d4edb0d499b`），构建时间 **2026-10-31T01:24:03+08:00**。

## 1. rev4 ELF 清单（本冻结件即对应以下 8 个 ELF）

| ELF | 用途 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_p3q_producer.elf` | 有界（E6/E3 主用） | `a7cce74646adcc120fba12e40f5de2b7a440cd400a60f1c9737d8ab220069053` | 303,392 |
| `s5_display_app_p3q_producer_longrun.elf` | 长跑 30 min | `b563453b70624cb95ea23e1da7655582237b153345efcd36a30dab8c1fadee17` | 303,828 |
| `s5_display_app_p3q_producer_idleprobe.elf` | 空闲测速（E2，板级挂起不采用） | `c81f829b9ae682ad1a5236ab2606eef77eb6d8dad747293fbba7c3c019bc67cc` | 303,388 |
| `s5_display_app_p3q_producer_fault.elf` | 故障相位轮换（每 120 次发布） | `48fd7d7e635e34b8612cc06434221823655710bcd867623a94de989a04aee123` | 303,872 |
| `…_fault_overrun.elf` | E4 固定 overrun | `a993f352657053e77302d085b4cfeff4fb53b86625681b2dd7342da75d606d25` | 303,148 |
| `…_fault_stale.elf` | E4 固定 stale | `38771e80d8fa56f40da3896382abd5a6ef674403d5008ed9b57ac1ae3d40e466` | 303,220 |
| `…_fault_invalid.elf` | E4 固定 invalid | `7f9dc7c4af6122e2a5cdd2356e5d8570dc7fbe05e74e6be57c91cf5599588685` | 303,272 |
| `…_fault_no_hand.elf` | E4 固定 no_hand | `cb03404d059bba34b6551d09f7066eccbd98a12ee5281b98b01e9b9b3b97d83f` | 304,156 |

- 编译：同套件 flags（`-O2 -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -std=gnu11 -Wall -Wextra --gc-sections -specs=Xilinx.spec`）+ P3q 默认宏 + `-DS5_PRODUCER=1`（故障版 `-DS5_PROD_FAULT=1/2/3/4/5`；长跑/idleprobe 加 `-DS5_LONG_RUN=1`/`-DS5_IDLE_PROBE=1`）；工具链 `arm-xilinx-eabi-gcc 13.4.0`、BSP `w4/…/ps7/sw/cpu0`、`lscript_s4t34.ld`；有界版 berkeley text 48,280 / data 112 / bss 2,355,440；exit 0、零告警。
- 显示三件套未重编：`e4ba0cb4…`/285,572、`cbf5ebe3…`/288,772、`2c880e4e…`/289,532（阶段5 冻结物保持）。

## 2. sidecar `S5X1`（基址 `0x20800000+0x100`，32 B，小端；字段顺序不变）

| 偏移 | 字段 | 口径 | 实现 |
|---|---|---|---|
| +0x00 | `magic2`=0x53355831 | §3 结构 | `S5Pub_PackSidecar()` |
| +0x04 | `version`=1 | §3 | 同上 |
| +0x08 | `session_id` | §3.1（**仅主张会话内恒定**） | `s5_pub_pick_session_id()` |
| +0x0C | `result_seq` | §3.2 | `S5Pub_NextSeq()` |
| +0x10/+0x14 | `result_time_lo/hi` | §3.4（整块最后写入） | `S5Pub_WritePublish()` |
| +0x18 | `seqlock` | §3.3 | `S5Pub_WritePublish()` / `S5Pub_ReadPublish()` |
| +0x1C | `reserved`=0 | 保留 | `S5Pub_PackSidecar()` |

- 布局：头 32 B + 检测项（≤14，槽位 0..13）→ sidecar `[0x100,0x120)`；flush 288 B。编译期断言：`S5_PUB_SIDECAR_BASE==0x20800100`、`S5_PUB_PUBLISH_BYTES==0x120`。

## 3. rev4 seqlock 顺序（C4 两个缺陷的修正）

**写者 `S5Pub_WritePublish()`（`src/s5_display_app.c`）**
1. `seqlock++`（奇）→ **单独 clean/flush 该 4 B 锁行** → `DSB()`
2. 写 32 B 头 + 检测项（≤14）+ sidecar 非时间字段 → **最后写 `result_time`**
3. **clean/flush `[0x20800000,0x20800120)`（288 B）** → `DSB()`
4. `seqlock++`（偶）→ **clean/flush 锁行** → `DSB()`

**消费者 `S5Pub_ReadPublish()`**
1. **先 invalidate**（锁行 + payload 区间一起，288 B）
2. 读 `seqlock`(`s1`)，奇则重试（≤3）
3. 读 payload → **`DMB()`**
4. 再读 `seqlock`(`s2`)，要求 `s1==s2` 且为偶，否则重试（≤3，超限 TIMEOUT）
5. 禁止"只读一次锁"或"先取锁后 invalidate"（已由实现顺序保证，case0f 记录调用序验证）

**ARM 侧端口**：写者 `s5_pub_mem`（flush=Xil_DCacheFlushRange、barrier=DSB）；消费者 `s5_pub_read_mem`（invalidate=Xil_DCacheInvalidateRange、barrier=DMB）。

## 4. `n_dets ≤ 14` fail-closed（身份 A 核心）

- `S5_PUB_NDETS_MAX=14`、`S5Pub_NDetsOk()`（`src/s5_publish_abi.h`）；`s5_prod_emit()` 中 `n_dets>14` → 不写块、seq 不推进、`s5_pub_overrun=1`，打印 `S5PROD REJECT n_dets=%d (>14) status.overrun=1 (fail-closed, 本帧不发布)`；禁止静默截断。

## 5. 源码绑定（磁盘实际 sha256，rev4）

| 文件 | sha256 |
|---|---|
| `src/s5_display_app.c` | `bed1a9f68611f34e3c64ebd4ffba7202bf5454a9b554ae63bc4e0907327f3ca4` |
| `src/s5_display_app.h` | `73770fce00a36a99320a0fe3dd646f0af99c0b6e805ad189a776dae4556380e3` |
| `src/s5_publish_abi.h` | `a8ca5c1f2cb8bfc02b5fa9150ded280ffa0f66342a3b217e8399042e3ac4e456` |
| `src/s5_result_abi.h` | `0462f91173616b2ab1e6bc57cfdf1695229c4996a2d1fb87611537329fceab8c`（未改） |
| `src/s5_real_source.c` | `cec077a102105c1fb755afc9f19a4b131909aa411d31d3de27e6969a402a50e8` |
| `src/s5_timebase.c` | `47a3dc27ed2c0dc9c60a326eda979a80d2a9020c69ecd5c8361e66fbdae0de96` |
| `src/vdma_ctrl.c` | `bb32bcbebe220a38ad19000a660929834f563a0fe6b82b7968160833da17eff8` |
| `tools/real_source_selftest.c` | `666572d524a964b8f9fc123cc11424a9cdf6d2556ad8d3ed7b8d0eb0b10677cc` |
| `build_s5_display_app.py` | `4cc8bc8b3539efee27611a58ddd67f727791b15ca9ea41c12561b22fd2005118`（未改） |

## 6. 自检（离线，exit 0）

- `case0c` sidecar 往返；`case0e` `n_dets≤14` 门（14 允许 / 15、16 拒绝）+ sidecar@0x100 + flush 288 B；**`case0f`（rev4 新增）seqlock 顺序断言**：写者记录序 `flush_lock→barrier→flush_payload→barrier→flush_lock→barrier`、读者 `invalidate→barrier`、奇数锁拒绝、偶值写入 `sl==2`；`case0d` seq 回绕（`0xFFFFFFFE→0xFFFFFFFF` 接受、`0xFFFFFFFF→0` 拒绝）+ seqlock 奇偶 + 业务状态五条映射 —— 全 PASS。

## 7. session 主张收窄（rev4）

- **只主张"会话内 `session_id` 恒定"**；**跨 POR 唯一性不主张**（列为阶段7 **R-14**）。`s5_pub_pick_session_id()` 的"碰撞 +1，≤8 次"仅为降低碰撞概率的 **best-effort**，不构成唯一性保证（代码注释已同步）。

## 8. 已知限制

1. 旧 E3（`s6e_e3_age_20261030_r01`）与 E5 证据**保留原判、不复用**；板窗用新 RunId 跑 E6 系列（A + E4-rev4）。
2. 无运行期故障切换（`S5_PROD_FAULT` 编译期）；E4 用 4 个固定模式 ELF。
3. idleprobe 板级挂起、不采用；E2 用 `fps_dis`（`VDMA: read period = … us -> fps_dis=60`），不可与 `fps_dis_idle` 混用。
4. `gt_now` 需反推（`result_time+age_pub`）；旧生产者（无 sidecar magic2）降级非原子。
5. 真实 `n_dets/cls/score/坐标` 与真实推理延迟仍由真实推理链提供（本版模拟框 + `inf=cap+7 ms`）。
6. 未上板：E2–E6 板级结论不在本冻结件范围。

## 9. 与冻结 32 B 显示 ABI 兼容声明

- **未修改** `src/s5_result_abi.h`（32 B 头 + 16 B 项语义逐字不变）；sidecar 为 `+0x100` 增量扩展，旧消费者可忽略。
- A 身份使用约束：ABI 物理容纳 16 项，A 只用 0..13（14 项），槽位 14/15 被 sidecar 覆盖；`>14` 一律拒绝发布。
- flush 288 B 不触碰 `+0x120` 之后；显示消费者不读 sidecar ⇒ **阶段5 冻结物不受影响**。