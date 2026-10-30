# S5 生产者冻结记录 **rev3 / 身份 A**（阶段6 G4/G5 软件冻结件）

- 生成 2026-10-31（UTC+8）。**正式身份 = A（Wong 裁定，口径 rev3）**：sidecar 基址 `0x20800000+0x100`（32 B，字段顺序不变）、**`n_dets ≤ 14` fail-closed**、flush **`[0x20800000, 0x20800120)`（288 B）**。rev2（`+0x120`/16 框，2026-10-31 00:51）**作废，仅存档**（`build/rev2_archived/` + `S5_PRODUCER_V2_FREEZE_rev2_archived.md`）。
- 口径依据：`docs/obsidian-project/02-方案设计/阶段6_交互控制_6D口径冻结_20261030.md`（rev3，main 已提交）。
- 边界：离线构建 + 主机自检；未接触板卡/Vivado/git；**只重编 producer 系列**（显示三件套未重编）。
- 源码基线：`src/s5_display_app.c` `2caf90c4a3d1becbc19dcee00fc310e8288e5c5c23fd7f56f44a5e2f4fad00ff`、`src/s5_display_app.h` `73770fce00a36a99320a0fe3dd646f0af99c0b6e805ad189a776dae4556380e3`、`src/s5_publish_abi.h` `5e7c2224b7cbc6dac1196757a70922f9400549a9a6282af5e20a97c38e555834`、`tools/real_source_selftest.c` `d90fe02849b133b1ebc48d7f0001c32f178f201695e41a1510216c65de5fb7d1`。
- 构建记录：`build/p3q_producer_A_rev3_record.json`（sha256 `d60683b76f2cd373bcbe0a8ad2ff8b326c4688bf7f6ecb2bcfad4c62e53ffdd0`），构建时间 **2026-10-31T01:07:58+08:00**。

## 1. 身份 A ELF 清单（sha256 / 字节）

| ELF | 用途 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_p3q_producer.elf` | 有界（E3/E4 主用） | `bef4abb520dfa8ec6958ca592e16c1a778647c3659b13b938cd169e83c987cad` | 301,812 |
| `s5_display_app_p3q_producer_longrun.elf` | 长跑 30 min | `e2d1b338efb41278aecad2f6587874a3122252e0f04a56a869c10f015ae0a8bf` | 302,008 |
| `s5_display_app_p3q_producer_idleprobe.elf` | 空闲测速（E2，板级挂起不采用） | `a21382d23c0b3262a4bc6d4dcaf8dbc7d7c415fcf75b11393e7d224cbbbde09c` | 301,416 |
| `s5_display_app_p3q_producer_fault.elf` | 故障相位轮换（每 120 次发布） | `410d6020f75182f1b9a767812aa586e509799cd46f76d259d76502e2f8da8d10` | 302,052 |
| `…_fault_overrun.elf` | E4 固定 overrun | `8b9e00a7f9c2747a935a0cbd7b1e9d514563cf4a1df0d6f0e6c119f8cd39c763` | 301,352 |
| `…_fault_stale.elf` | E4 固定 stale | `b678b2799ffae1134048c9cd6f464078790cbfdf4e9818b31c736c3700a0614c` | 301,352 |
| `…_fault_invalid.elf` | E4 固定 invalid | `02a5c8ef703282146ea60f482c734bb0dd82a8b4b854c5d3952f5c24c6d2403a` | 301,476 |
| `…_fault_no_hand.elf` | E4 固定 no_hand | `1f23ef76361336a58730ce058a68e3a773f420cc89b1345d12ddefaecf5b303d` | 302,372 |

- 编译：同套件 flags（`-O2 -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -std=gnu11 -Wall -Wextra --gc-sections -specs=Xilinx.spec`）+ P3q 默认宏 + `-DS5_PRODUCER=1`（故障版另加 `-DS5_PROD_FAULT=1/2/3/4/5`；长跑/idleprobe 另加 `-DS5_LONG_RUN=1`/`-DS5_IDLE_PROBE=1`）；工具链 `arm-xilinx-eabi-gcc 13.4.0`、BSP `w4/…/ps7/sw/cpu0`、`lscript_s4t34.ld`；有界版 berkeley text 47,880 / data 72 / bss 2,355,184；退出码 0、零告警。
- **显示三件套未重编**：`s5_display_app.elf`=`e4ba0cb4…`/285,572、长跑=`cbf5ebe3…`、idleprobe=`2c880e4e…`（阶段5 冻结物保持）。
- `build/build_record.json` 的 producer 条目仍为 rev1（22:05），已被 rev2/rev3 记录取代；下次全量构建刷新。

## 2. sidecar `S5X1`（基址 `0x20800000+0x100`，32 B，小端）

| 偏移 | 字段 | 口径 | 实现 |
|---|---|---|---|
| +0x00 | `magic2`=0x53355831 | §3 结构 | `S5Pub_PackSidecar()` L824 |
| +0x04 | `version`=1 | §3 | 同上 |
| +0x08 | `session_id` | §3.1 | `s5_pub_pick_session_id()` L1284（GT>>10&0xFFFF，碰撞 +1≤8） |
| +0x0C | `result_seq` | §3.2 | `S5Pub_NextSeq()` L840 |
| +0x10/+0x14 | `result_time_lo/hi` | §3.4 | `s5_prod_emit()` L1361：整块最后写入 + 立即 flush |
| +0x18 | `seqlock` | §3.3 | `s5_prod_emit()`：奇→写→flush→偶→flush |
| +0x1C | `reserved`=0 | 保留 | `S5Pub_PackSidecar()` |

- 布局：头 32 B + 检测项（每项 16 B，**仅槽位 0..13 可用**，`≤0x100`）→ sidecar `[0x100,0x120)`；**flush `[0x20800000,0x20800120)` = 288 B**。
- sidecar 故意覆盖检测项槽位 14、15 ⇒ **`n_dets ≤ 14` 是 A 身份的硬约束**。
- 编译期断言：`_Static_assert(S5_PUB_SIDECAR_BASE == 0x20800100u)`、`_Static_assert(S5_PUB_PUBLISH_BYTES == 0x120u)`（`src/s5_publish_abi.h`）。

## 3. `n_dets ≤ 14` fail-closed（A 的核心实现）

- 上限宏：`S5_PUB_NDETS_MAX = 14`；判定 `S5Pub_NDetsOk(n)`（`src/s5_publish_abi.h`，返回 0=允许 / -1=拒绝）。
- 生产端 `s5_prod_emit()`（`src/s5_display_app.c` L1361，判定在 **L1379**）：`n_dets>14` 时
  **不写块、seq 不推进**，置 `s5_pub_overrun=1`，打印
  `S5PROD REJECT n_dets=%d (>14) status.overrun=1 (fail-closed, 本帧不发布)`；之后发布 `status.overrun=1` → 业务状态 ERROR。**禁止静默截断**（截断会让消费端误以为结果完整）。
- 打包函数内部 `n` 亦按 `S5_PUB_NDETS_MAX` 钳制（L1366），防御性保证不会越界写 sidecar 区。

## 4. seqlock 发布时序 / 消费者协议

- 生产者：`seqlock++`(奇) → 写 32 B 头+项 → 写 sidecar 非时间字段 → 写 `result_time`(最后) → `Xil_DCacheFlushRange(0x20800000,0x120)` → `seqlock++`(偶) → 再 flush。
- 消费者 `s5_pub_consume()` L1470（每 60 帧）：读 `seqlock`(须偶) → `invalidate(0x120)` → 读头+sidecar → 再读 `seqlock`(须偶且同)；≤3 次重试，超限 `S5CONS TIMEOUT`；旧生产者（`magic2` 不符）走非原子降级。
- 打印：`S5CONS sid=%d seq=%d n=%d status=0x%x age_pub=%d state=%s seqlock=%d`；`age_pub=(GT_now−result_time)×1000/333333343`；`gt_now` 用 `result_time+age_pub` 反推。

## 5. `session_id` / `result_seq` / 业务状态 实现位置（`src/s5_display_app.c`）

- `S5Pub_PackSidecar()` L824、`S5Pub_NextSeq()` L840、`S5Pub_AgePublishMs()` L852、`S5Pub_BizState()` L866、`S5Pub_SeqlockStable()` L886、`S5Pub_NDetsOk()`（`s5_publish_abi.h` inline）。
- `s5_pub_flush()` L1278、`s5_pub_pick_session_id()` L1284、`s5_prod_session_start()` L1334、`s5_prod_emit()` L1361、`s5_pub_consume()` L1470。
- 离线证据：`build/selftest_real_source.txt`（`tools/real_source_selftest.c` `d90fe028…`）：**case0c** sidecar 往返、**case0e** `n_dets≤14` 门（14 允许 / 15、16 拒绝；sidecar @0x100、flush 288 B）、**case0d** seq 回绕（`0xFFFFFFFE→0xFFFFFFFF` 接受、`0xFFFFFFFF→0` 拒绝）+ seqlock 奇偶 + 业务状态五条映射；全部 PASS（exit 0）。
- 业务状态优先级：valid=0→ERROR、overrun→ERROR、stale 或 age>200 ms→TIMEOUT、valid&&n=0→NO_HAND、否则 OK。

## 6. 已知限制

1. **旧 E3 可作行为参考**：`s6e_e3_age_20261030_r01` 本就是 `+0x100` 偏移，与 A 一致；但它是 **rev1 软件（无 14 框 fail-closed）**，A 重编后建议新 RunId 与 E4-rev3 同窗复验。
2. 无运行期故障切换（编译期 `S5_PROD_FAULT`）；E4 用 4 个固定模式 ELF。
3. idleprobe 变体板级挂起、不采用；E2 用 `fps_dis`（`VDMA: read period = … us -> fps_dis=60`），其口径不可与 `fps_dis_idle` 混用。
4. `gt_now` 需反推（UART 无该字段）；旧生产者降级非原子。
5. 真实 `n_dets/cls/score/坐标` 与真实推理延迟仍由真实推理链提供（本版用模拟框 + `inf=cap+7 ms`）。
6. 未上板：E2–E5 板级结论不在本冻结件范围；rev2 全部产物（含 ELF）作废、仅存档。

## 7. 与冻结 32 B 显示 ABI 的兼容声明

- **未修改** `src/s5_result_abi.h`（32 B 头 + 16 B 项语义逐字不变）；sidecar 是 `+0x100` 的**增量扩展**，旧消费者可忽略。
- A 身份与 ABI 的差异仅在使用约束：ABI 物理上容纳 16 项，A 只用 **0..13**（14 项），槽位 14/15 被 sidecar 覆盖；`>14` 一律拒绝发布。
- flush 288 B（0x120）覆盖头/项/sidecar，**不触碰 `+0x120` 之后**内存；显示消费者不读 sidecar ⇒ **阶段5 冻结物不受影响**。