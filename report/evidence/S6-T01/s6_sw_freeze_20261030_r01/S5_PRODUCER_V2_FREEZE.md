# S5 生产者 v2 冻结记录（阶段6 G4/G5 软件冻结件）

- 生成 2026-10-30（UTC+8）；范围 P3q 生产者 v2（sidecar `S5X1` + seqlock + 故障注入）；口径依据 `docs/obsidian-project/02-方案设计/阶段6_交互控制_6D口径冻结_20261030.md`。
- 边界：离线构建 + 主机自检；未接触板卡/Vivado/git；**本轮只写文档，未重编、未改代码**。
- 源码基线：`src/s5_display_app.c` `b2ec56e0…`、`src/s5_display_app.h` `86a32db4…`、`src/s5_publish_abi.h` `4ae38014…`（新增）、`tools/real_source_selftest.c` `a64fa0e3…`。
- 套件构建：`python build_s5_display_app.py`，2026-10-30T22:05:14+08:00，exit compile/link/size/nm=0/0/0/0（`build/build_record.json`）。
## 1. v2 ELF 清单（sha256 / 字节 / mtime）
| ELF | 用途 | sha256 | 字节 | mtime |
|---|---|---|---|---|
| `…_p3q_producer.elf` | 有界（E3/E4 主用） | `0fae384afe58846f55b850fcf025d97f5706be28dc5eb8fc1f290d42b581cd4a` | 301,152 | 22:05:12 |
| `…_p3q_producer_longrun.elf` | 长跑 30 min | `97c33f58b974e4ff805debc4a7683617e77852f81ab9b3f0d90cead775975e79` | 301,500 | 22:05:13 |
| `…_p3q_producer_idleprobe.elf` | 空闲测速（E2） | `7357c3e52228fcd0eb732b770f200561a2d0dec05c74e03b69c90a1f732563fe` | 300,812 | 22:05:13 |
| `…_p3q_producer_fault.elf` | cycle 相位轮换 | `1bd8fe2dde1a102a4ba5daf5ffd5d492a3b8dfc96350406e12504d5dedb3f52a` | 301,664 | 22:05:14 |
| `…_p3q_producer_fault_overrun.elf` | E4 overrun | `bd4963893f8cbcb35511696dbce000e33631db20c32fc40de633f4ff7a0126e9` | 300,912 | 22:08:27 |
| `…_p3q_producer_fault_stale.elf` | E4 stale | `8453a752626926740e3c1eff5694b881f92c8d05c06cc5e322c8fc597bf15e53` | 300,960 | 22:08:28 |
| `…_p3q_producer_fault_invalid.elf` | E4 invalid | `3d1d78c45139931d9cfeac67a248c07f2149d25135d01af8201694ec4a0cd3da` | 301,048 | 22:08:28 |
| `…_p3q_producer_fault_no_hand.elf` | E4 no_hand | `47acb4bc9da3c3f3c9e95af487897ee99532f7ecbd85c1267e67f0bddfc47109` | 301,576 | 22:08:29 |

- 前 4 个由套件脚本产出并记录在 `build_record.json`；后 4 个用同 flags 单独编译（`-DS5_PROD_FAULT=1/2/3/4`），**不在 build_record 内**。
- 宏：P3q 默认（`S5_VDMA_BASE=0x43C40000`、`S5_UF_FRAME_REG=0x43C50000`、`S5_UF_TOTAL_REG=0x43C50008`、`S5_NO_VTC=1`）+ `-DS5_PRODUCER=1`（长跑/idleprobe 另加 `-DS5_LONG_RUN=1`/`-DS5_IDLE_PROBE=1`）；工具链 `arm-xilinx-eabi-gcc 13.4.0`、BSP `w4/…/ps7/sw/cpu0`、`lscript_s4t34.ld`、`-O2 -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard --gc-sections`。
## 2. sidecar `S5X1`（`0x20800000+0x100`，32 B，小端）↔ 冻结口径
| 偏移 | 字段 | 口径 | 实现 |
|---|---|---|---|
| +0x00 | `magic2`=0x53355831 | §3 结构 | `S5Pub_PackSidecar()` L824 |
| +0x04 | `version`=1 | §3 | 同上 |
| +0x08 | `session_id` | §3.1 | `s5_pub_pick_session_id()` L1284（GT>>10&0xFFFF，碰撞 +1≤8） |
| +0x0C | `result_seq` | §3.2 | `S5Pub_NextSeq()` L840（严格 +1；0xFFFFFFFF→0 拒绝） |
| +0x10/+0x14 | `result_time_lo/hi` | §3.4 | `s5_prod_emit()` L1361：整块最后写入 + 立即 flush |
| +0x18 | `seqlock` | §3.3 | `s5_prod_emit()`：奇→写→flush→偶→flush |
| +0x1C | `reserved`=0 | 保留 | `S5Pub_PackSidecar()` |
## 3. seqlock 发布时序 与 消费者 `S5CONS`
- 生产者 `s5_prod_emit()`（每帧或 `S5_PROD_EVERY_N`）：`seqlock++`(奇) → 写 32 B 头+16×16 B 项 → 写 sidecar 非时间字段 → 写 `result_time`(最后) → `Xil_DCacheFlushRange(0x20800000,0x120)` → `seqlock++`(偶) → 再 flush。
- 消费者 `s5_pub_consume()` L1445（每 60 帧）：读 `seqlock`(须偶) → `Xil_DCacheInvalidateRange(0x20800000,0x120)` → 读整块+sidecar → 再读 `seqlock`(须偶且同)；不一致重试 ≤3 次，超限 `S5CONS TIMEOUT`。
- 打印 `S5CONS sid=%d seq=%d n=%d status=0x%x age_pub=%d state=%s seqlock=%d`；`age_pub=(GT_now−result_time)×1000/333333343`（E3 判据），`gt_now` 用 `result_time+age_pub` 反推。
- 旧生产者（`magic2` 不符）→ `S5CONS sidecar absent (旧生产者, 非原子路径)`，**不声称原子**。
## 4. `session_id` / `result_seq` 规则实现位置（`src/s5_display_app.c`）
- `S5Pub_NextSeq()` L840（seq 规则）、`S5Pub_PackSidecar()` L824、`S5Pub_AgePublishMs()` L852、`S5Pub_SeqlockStable()` L886。
- `s5_pub_pick_session_id()` L1284、`s5_prod_session_start()` L1334（`frame_id=0` 会话起始标记）、`s5_prod_emit()` L1361、`s5_pub_consume()` L1445、`s5_pub_flush()` L1278。
- 拒绝回绕证据：host 自检 case0d（`build/selftest_real_source.txt` `04467cda…`）：`0xFFFFFFFE→0xFFFFFFFF` 接受、`0xFFFFFFFF→0` 拒绝、seqlock 奇=不稳定/偶且同=稳定、sidecar 打包/回读一致，全部 PASS（`selftest_real_source` exit 0）。
## 5. 业务状态映射实现位置
- `S5Pub_BizState()` L866：valid=0→ERROR、overrun→ERROR、stale 或 age>200 ms→TIMEOUT、valid&&n=0→NO_HAND、否则 OK；`S5Pub_StateName()` 取名。
- 生产侧 `s5_prod_emit()` 按 `S5_PROD_FAULT`（none/overrun/stale/invalid/no_hand/cycle）与 `S5_PROD_NO_HAND_EVERY_N` 置 status 位；消费侧 `S5CONS` 用同一映射打印 `state`；host case0d 五条映射 + 200 ms 边界 PASS。
## 6. 已知限制
1. **无运行期故障切换**：`S5_PROD_FAULT` 编译期固定；E4 用 4 个固定模式 ELF，cycle ELF 每 120 次发布轮换相位。
2. **idleprobe 口径**：E2 用 `idle_period_us`/`fps_dis_idle`（停写帧存后的 VDMA 读周期），与渲染时 `fps_dis` 不同口径、不可混用。
3. **`gt_now` 需反推**：UART 只有 `result_time`/`age_pub`，无 `gt_now` 字段。
4. **旧生产者降级非原子**：无 sidecar 时消费者走非原子路径（仅两次 seqlock 缺省 0 的兼容判定）。
5. 真实 `n_dets/cls/score/坐标` 与真实推理延迟仍由真实推理链提供（v2 用模拟框 + `inf=cap+7 ms`）；未上板，E2–E5 板级结论不在本冻结件范围。
## 7. 与冻结 32 B 显示 ABI 的兼容声明
- **未修改** `src/s5_result_abi.h`：`magic/frame_id/n_dets/cap_lo/hi/inf_lo/hi/status` 与 16 B 项布局语义逐字不变。
- sidecar 位于 `+0x100`（288 B 之后），属**增量扩展**，旧消费者可忽略；`reserved` 恒 0，未占用其他语义。
- `flush` 范围 288 B（0x120）覆盖头/项/sidecar，不触碰 `+0x120` 之后内存。