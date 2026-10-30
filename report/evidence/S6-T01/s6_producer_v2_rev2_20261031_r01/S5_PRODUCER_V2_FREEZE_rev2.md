# S5 生产者 v2 冻结记录 **rev2**（阶段6 G4/G5 软件冻结件）

- 生成 2026-10-31（UTC+8）。**rev2 勘误（取代 rev1 / 2026-10-30 22:05）**：sidecar 偏移 `+0x100` → **`+0x120`**（rev1 会压到第 14 号检测项）；flush `0x120` → **`0x140`**；`n_dets>16` **fail-closed**。口径依据 `docs/obsidian-project/02-方案设计/阶段6_交互控制_6D口径冻结_20261030.md`（rev2，main `cd81325`）。
- 边界：离线构建 + 主机自检；未接触板卡/Vivado/git。**只重编 producer 系列**（显示三件套未重编）。
- 源码基线：`src/s5_display_app.c` `1c64777850d511d12d41a9dd8a12f4bac167eab45fcbdef510e87fb510566165`、`src/s5_display_app.h` `fb0026de8a0c8969797ef1ea6985898e06c3cedee766fdcd4f9f5b7ef6c3e8ec`、`src/s5_publish_abi.h` `7f7c3c2a8610c64f554c192745fe62ce9db3b45f995b515091f3bb121fa4fee8`。
- 构建记录：`build/p3q_producer_v2_rev2_record.json`（sha256 `2b8850ddf4f547ac765d1910d132778770334887adf7b40018ea5cd60558aeb9`），构建时间 **2026-10-31T00:51:10+08:00**。

## 1. rev2 ELF 清单（sha256 / 字节）

| ELF | 用途 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_p3q_producer.elf` | 有界（E3/E4 主用） | `c36d1133d0cc604eea6adbb89ae3b5119ad652a106f9fdc818bc1f91680050bd` | 301,312 |
| `s5_display_app_p3q_producer_longrun.elf` | 长跑 30 min | `87fcab6bb2df668574742051bee7dfbedbf797f399e9c7ca59e20f4873192f03` | 301,764 |
| `s5_display_app_p3q_producer_idleprobe.elf` | 空闲测速（E2，板级挂起不采用） | `be3011fc93407c415e4d71947bceac9f3c46114a0dd751e7d7a62a37a0b7c7bc` | 300,920 |
| `s5_display_app_p3q_producer_fault.elf` | 故障相位轮换（每 120 次发布） | `d3e9e4f61318a78f20d3c408eabc2423b664d5568d6c975865a889cf07502a30` | 301,836 |
| `…_fault_overrun.elf` | E4 固定 overrun | `1ffd640959026b9b779a6106813f57edc5222755ef2ab41ba965ca820fed7acd` | 301,196 |
| `…_fault_stale.elf` | E4 固定 stale | `35fafa677a15090208fa19febc92533f085e94bbe5cb507b61baa4403665a024` | 301,216 |
| `…_fault_invalid.elf` | E4 固定 invalid | `bd0d63eaa17508d6e468aa53b7e539be3ba5fe9f3f93fe3274f4ab8559d31344` | 301,328 |
| `…_fault_no_hand.elf` | E4 固定 no_hand | `cd23655cdf30cedeaf833df0c4ddc19347db8c3c4136a28fcc6413e7c1c1a9a5` | 301,832 |

- 编译：同套件 flags（`-O2 -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -std=gnu11 -Wall -Wextra --gc-sections -specs=Xilinx.spec`）+ P3q 默认宏 + `-DS5_PRODUCER=1`（故障版另加 `-DS5_PROD_FAULT=1/2/3/4/5`；长跑/idleprobe 另加 `-DS5_LONG_RUN=1`/`-DS5_IDLE_PROBE=1`）；工具链 `arm-xilinx-eabi-gcc 13.4.0`、BSP `w4/…/ps7/sw/cpu0`、`lscript_s4t34.ld`；有界版 berkeley text 47,888 / data 72 / bss 2,355,248。
- **显示三件套未重编**：`s5_display_app.elf`=`e4ba0cb4…`/285,572、长跑=`cbf5ebe3…`、idleprobe=`2c880e4e…`（阶段5 冻结物保持）；本轮改动均在 `#if S5_PRODUCER` 分支与宏/注释内，显示路径不读 sidecar。
- `build/build_record.json` 中的 producer 条目仍为 rev1（22:05），**已被本 rev2 记录取代**；下次全量构建会刷新。

## 2. sidecar `S5X1`（基址 `0x20800000+0x120`，32 B，小端）

| 偏移 | 字段 | 口径 | 实现 |
|---|---|---|---|
| +0x00 | `magic2`=0x53355831 | §3 结构 | `S5Pub_PackSidecar()` L824 |
| +0x04 | `version`=1 | §3 | 同上 |
| +0x08 | `session_id` | §3.1 | `s5_pub_pick_session_id()` L1284（GT>>10&0xFFFF，碰撞 +1≤8） |
| +0x0C | `result_seq` | §3.2 | `S5Pub_NextSeq()` L840 |
| +0x10/+0x14 | `result_time_lo/hi` | §3.4 | `s5_prod_emit()` L1361：整块最后写入 + 立即 flush |
| +0x18 | `seqlock` | §3.3 | `s5_prod_emit()`：奇→写→flush→偶→flush |
| +0x1C | `reserved`=0 | 保留 | `S5Pub_PackSidecar()` |

- 内存布局：块 `[0x00,0x120)`（32 B 头 + 16×16 B 项）→ sidecar `[0x120,0x140)`；**flush 范围 `[0x20800000,0x20800140)`**。
- 编译期断言：`_Static_assert(S5_PUB_SIDECAR_BASE == 0x20800120u)`、`_Static_assert(S5_PUB_PUBLISH_BYTES == 0x140u)`（`src/s5_publish_abi.h`）。

## 3. seqlock 发布时序 / 消费者协议 / fail-closed

- 生产者 `s5_prod_emit()`（每帧或 `S5_PROD_EVERY_N`）：`seqlock++`(奇) → 写 32 B 头+16×16 B 项 → 写 sidecar 非时间字段 → 写 `result_time`(最后) → `Xil_DCacheFlushRange(0x20800000,0x140)` → `seqlock++`(偶) → 再 flush。
- **`n_dets` fail-closed（rev2 新增）**：`n_dets > S5_PUB_NDETS_MAX(16)` 时**拒绝发布本帧**（不写块、seq 不推进），置 `s5_pub_overrun=1` 并打印 `S5PROD REJECT n_dets=%d (>16) status.overrun=1 (fail-closed, 本帧不发布)`；后续发布 `status.overrun=1` → 业务状态 ERROR。
- 消费者 `s5_pub_consume()` L1453（每 60 帧）：读 `seqlock`(须偶) → `invalidate(0x140)` → 读头+sidecar → 再读 `seqlock`(须偶且同)；≤3 次重试，超限 `S5CONS TIMEOUT`；旧生产者（`magic2` 不符）走非原子降级。
- 打印：`S5CONS sid=%d seq=%d n=%d status=0x%x age_pub=%d state=%s seqlock=%d`；`age_pub=(GT_now−result_time)×1000/333333343`；`gt_now` 用 `result_time+age_pub` 反推。

## 4. `session_id` / `result_seq` / 业务状态实现位置（`src/s5_display_app.c`）

- `S5Pub_PackSidecar()` L824、`S5Pub_NextSeq()` L840、`S5Pub_AgePublishMs()` L852、`S5Pub_BizState()` L866、`S5Pub_SeqlockStable()` L886。
- `s5_pub_flush()` L1278、`s5_pub_pick_session_id()` L1284、`s5_prod_session_start()` L1334、`s5_prod_emit()` L1361、`s5_pub_consume()` L1453。
- 拒绝回绕证据：host 自检 case0d（`build/selftest_real_source.txt`，`tools/real_source_selftest.c` `a64fa0e3…`）：`0xFFFFFFFE→0xFFFFFFFF` 接受、`0xFFFFFFFF→0` 拒绝、seqlock 奇=不稳定/偶且同=稳定、业务状态五条映射 + 200 ms 边界 PASS。
- 业务状态优先级：valid=0→ERROR、overrun→ERROR、stale 或 age>200 ms→TIMEOUT、valid&&n=0→NO_HAND、否则 OK。

## 5. 已知限制（rev2）

1. **E3 证据需新 RunId 复验**：`s6e_e3_age_20261030_r01` 在 rev1（sidecar `+0x100`）下采集——语义有效，但偏移不同，rev2 后须新 RunId 重采，**不复用 E3**。
2. 无运行期故障切换（编译期 `S5_PROD_FAULT`）；E4 用 4 个固定模式 ELF。
3. idleprobe 变体板级挂起、不采用；E2 用 `fps_dis`（`VDMA: read period = … us -> fps_dis=60`）。
4. `gt_now` 需反推（UART 无该字段）；idleprobe 口径不可与 `fps_dis` 混用。
5. 旧生产者降级非原子；真实 `n_dets/cls/score/坐标` 与真实推理延迟仍由真实推理链提供（v2 用模拟框 + `inf=cap+7 ms`）。
6. 未上板：E2–E5 板级结论不在本冻结件范围。

## 6. 与冻结 32 B 显示 ABI 的兼容声明

- **未修改** `src/s5_result_abi.h`（32 B 头 + 16 B 项语义逐字不变）；sidecar 是 `+0x120` 处的**增量扩展**，旧消费者可忽略。
- flush 范围 `0x140` 覆盖头/项/sidecar，**不触碰 `+0x140` 之后**内存（`S5_RESULT_SPACE_BYTES` 预留 8 MiB，不受影响）。
- 显示消费者不读 sidecar ⇒ **阶段5 冻结物（显示三件套 ELF）不受影响**。