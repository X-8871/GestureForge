# S5 生产者冻结记录 **rev5 / 身份 A**（阶段6 G4/G5 软件冻结件）

- 生成 2026-10-31（UTC+8）。**rev5 = rev4 + 可观测字段（E6-A 取证）**：协议、身份 A（sidecar `0x20800000+0x100`、`n_dets ≤ 14` fail-closed、flush `[0x20800000,0x20800120)` 288 B）、业务映射、故障注入**全部不变**；仅在 `S5CONS` 增加 `s1/s2/retries` 与 `RETRY`/`TIMEOUT` 行。
- 口径依据：`docs/obsidian-project/02-方案设计/阶段6_交互控制_6D口径冻结_20261030.md`（rev4 口径 + E6-A 观测要求）。旧 rev1–rev4 全部作废仅存档：`build/rev2_archived/`、`build/rev3_archived/`、`build/rev4_archived/`。
- 边界：离线构建 + 主机自检；未接触板卡/Vivado/git；只重编 producer 系列（显示三件套未重编）。
- 构建记录：`build/p3q_producer_A_rev5_record.json`（sha256 `807f427b79ef66e93ab7e0225f5b9d9c5a157dbe4264c23b7bdff676c274cef9`），构建时间 **2026-10-31T01:58:56+08:00**。

## 1. rev5 ELF 清单（本冻结件即对应以下 8 个 ELF）

| ELF | 用途 | sha256 | 字节 |
|---|---|---|---|
| `s5_display_app_p3q_producer.elf` | 有界（E6-A/E3 主用） | `ca6c24301537cd9db0ac514a6df5762db2f26f72c14ad0793c774dc88f99076e` | 304,040 |
| `s5_display_app_p3q_producer_longrun.elf` | 长跑 30 min | `6260250a4a9707657c354016f951122743fa502a8f4b8356ef772aea3f7047a5` | 304,472 |
| `s5_display_app_p3q_producer_idleprobe.elf` | 空闲测速（E2，板级挂起不采用） | `2c14cb0e1d5060d5d6e78b1ed38853da34a4aafc82fb23b4908a31f048b336f0` | 303,688 |
| `s5_display_app_p3q_producer_fault.elf` | 故障相位轮换（每 120 次发布） | `7e3ce32c11417f4a3cbd3f2b849cd79f9ef97ba46cbbffa9c62f60dc6a3e0834` | 304,508 |
| `…_fault_overrun.elf` | E4 固定 overrun | `89ae6adc577c42b7e196034e5ddacc0733d3d1b3eebae4ba84a9cc3893b11306` | 303,788 |
| `…_fault_stale.elf` | E4 固定 stale | `2e39bd26071c51ad6dca33b10193a1d346600b59aef2402ef464fc2d232edc61` | 303,848 |
| `…_fault_invalid.elf` | E4 固定 invalid | `5e92ae693f054df20f0c29163adda6d62c56f358a111135d5f5523beec1cc6ab` | 303,892 |
| `…_fault_no_hand.elf` | E4 固定 no_hand | `a3cdb877566678dcb02e044bde3365eb20714f7943f5317cd29703013d28dd89` | 304,552 |

- 编译：同套件 flags（`-O2 -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -std=gnu11 -Wall -Wextra --gc-sections -specs=Xilinx.spec`）+ P3q 默认宏 + `-DS5_PRODUCER=1`（故障版 `-DS5_PROD_FAULT=1/2/3/4/5`；长跑/idleprobe 加 `-DS5_LONG_RUN=1`/`-DS5_IDLE_PROBE=1`）；工具链 `arm-xilinx-eabi-gcc 13.4.0`、BSP `w4/…/ps7/sw/cpu0`、`lscript_s4t34.ld`；有界版 berkeley text 48,560 / data 112 / bss 2,355,440；exit 0、零告警。
- 显示三件套未重编：`e4ba0cb4…`/285,572、`cbf5ebe3…`/288,772、`2c880e4e…`/289,532（阶段5 冻结物保持）。

## 2. sidecar `S5X1`（基址 `0x20800000+0x100`，32 B，小端；字段/顺序不变）

| 偏移 | 字段 | 口径 | 实现 |
|---|---|---|---|
| +0x00 | `magic2`=0x53355831 | §3 结构 | `S5Pub_PackSidecar()` |
| +0x04 | `version`=1 | §3 | 同上 |
| +0x08 | `session_id` | §3.1（仅主张会话内恒定） | `s5_pub_pick_session_id()` |
| +0x0C | `result_seq` | §3.2 | `S5Pub_NextSeq()` |
| +0x10/+0x14 | `result_time_lo/hi` | §3.4（整块最后写入） | `S5Pub_WritePublish()` |
| +0x18 | `seqlock` | §3.3 | `S5Pub_WritePublish()` / `S5Pub_ReadPublish()` |
| +0x1C | `reserved`=0 | 保留 | `S5Pub_PackSidecar()` |

- 布局：头 32 B + 检测项（≤14，槽位 0..13）→ sidecar `[0x100,0x120)`；flush 288 B；编译期断言 `S5_PUB_SIDECAR_BASE==0x20800100`、`S5_PUB_PUBLISH_BYTES==0x120`。

## 3. rev5 可观测字段（唯一新增，协议不变）

- **正常 `S5CONS` 行**（仅当 `s1==s2` 且均为偶时输出，即协议成功条件）：
  `S5CONS sid=%d seq=%d n=%d status=0x%x age_pub=%d state=%s seqlock=%d s1=%d s2=%d retries=%d`
- **发生重试且最终成功**：先另打一行 `S5CONS RETRY seq=%d attempt=%d s1=%d s2=%d`，再打正常行。
- **重试超限（TIMEOUT）**：`S5CONS TIMEOUT seq=%d attempt=%d s1=%d s2=%d`（正常行不输出）。
- 轨迹来源 `S5PubReadTrace { attempts, retries(attempts-1), s1_last, s2_last }`（`S5Pub_ReadPublish()` 第 4 参数），`retries` 只做观测、不改变重试上限（仍 ≤3 次）。
- 离线样例（host case0f 输出）：
  `S5CONS sid=0 seq=0 n=2 status=0x0 age_pub=0 state=OK seqlock=2 s1=2 s2=2 retries=0（离线样例：s1==s2 且偶）`
  `S5CONS TIMEOUT seq=0 attempt=3 s1=1 s2=0（离线样例：奇数锁 3 次重试后 TIMEOUT）`

## 4. seqlock 顺序（与 rev4 相同，未改）

**写者 `S5Pub_WritePublish()`**：①`seqlock++`(奇)→单独 flush 4 B 锁行→`DSB` ②写头+项(≤14)+sidecar 非时间字段→`result_time` 最后 ③flush 288 B→`DSB` ④`seqlock++`(偶)→flush 锁行→`DSB`。
**消费者 `S5Pub_ReadPublish()`**：①invalidate-first（锁行+payload 288 B）②读 `s1`，奇重试(≤3) ③读 payload→`DMB` ④读 `s2`，须 `s1==s2` 且偶，否则重试(≤3，超限 TIMEOUT)。禁止"只读一次锁"/"先取锁后 invalidate"。
**ARM 端口**：写者 `s5_pub_mem`（flush+DSB）；消费者 `s5_pub_read_mem`（invalidate+DMB）。

## 5. `n_dets ≤ 14` fail-closed（身份 A 核心，未改）

`S5_PUB_NDETS_MAX=14`、`S5Pub_NDetsOk()`（`src/s5_publish_abi.h`）；`s5_prod_emit()` 中 `n_dets>14` → 不写块、seq 不推进、`s5_pub_overrun=1`，打印 `S5PROD REJECT n_dets=%d (>14) status.overrun=1 (fail-closed, 本帧不发布)`；禁止静默截断。

## 6. 源码绑定（磁盘实际 sha256，rev5）

| 文件 | sha256 |
|---|---|
| `src/s5_display_app.c` | `cd2b093a34620cbd538e878c871c3d65f0ab5fdb658ee554ac1045db44459109` |
| `src/s5_display_app.h` | `73770fce00a36a99320a0fe3dd646f0af99c0b6e805ad189a776dae4556380e3` |
| `src/s5_publish_abi.h` | `f89fb1be10c0564c049b8014bb9aaf789f6713e1f56dbb53f8040020f76b5dd3` |
| `src/s5_result_abi.h` | `0462f91173616b2ab1e6bc57cfdf1695229c4996a2d1fb87611537329fceab8c`（未改） |
| `src/s5_real_source.c` | `cec077a102105c1fb755afc9f19a4b131909aa411d31d3de27e6969a402a50e8` |
| `src/s5_timebase.c` | `47a3dc27ed2c0dc9c60a326eda979a80d2a9020c69ecd5c8361e66fbdae0de96` |
| `src/vdma_ctrl.c` | `bb32bcbebe220a38ad19000a660929834f563a0fe6b82b7968160833da17eff8` |
| `tools/real_source_selftest.c` | `c7089d2ba4c0935575f79ee27f783988b869a6eb491cda840bfb5f0eb5a61704` |
| `build_s5_display_app.py` | `4cc8bc8b3539efee27611a58ddd67f727791b15ca9ea41c12561b22fd2005118`（未改） |

## 7. 自检（离线，exit 0）

- `case0c` sidecar 往返；`case0e` `n_dets≤14` 门 + sidecar@0x100 + flush 288 B；`case0d` seq 回绕（`0xFFFFFFFE→0xFFFFFFFF` 接受、`0xFFFFFFFF→0` 拒绝）+ 业务状态五条映射。
- **`case0g`（E6-A 要求：记录 s1/s2 输出）**：由 `case0f` 的 v5 扩展承担（同一函数新增 trace 断言 + 样例打印），输出实测 `S5CONS ... s1=… s2=… retries=…` 与 `S5CONS TIMEOUT …`；不新增独立 case 编号，避免改动 ELF/源码绑定。
- **`case0f`（v5 扩展）**：写者序 `flush_lock→barrier→flush_payload→barrier→flush_lock→barrier`；读者序 `invalidate→barrier`；正常读 `attempts==1、retries==0、s1==s2==seqlock（偶）`；奇数锁 `attempts==3、retries==2、s1 为奇且被拒绝` —— 全 PASS。

## 8. session 主张（rev5 保持收窄）

**只主张"会话内 `session_id` 恒定"；跨 POR 唯一性不主张**（阶段7 **R-14**）；`s5_pub_pick_session_id()` 的碰撞 +1（≤8 次）仅为 best-effort，不构成唯一性保证（代码注释已同步）。

## 9. 已知限制

1. 旧 E3（`s6e_e3_age_20261030_r01`）/E5 证据保留原判、**不复用**；板窗新 RunId（如 `s6e_e6_age_rev4_20261031_r04`）+ rev5 复跑 E6 系列。
2. 无运行期故障切换（`S5_PROD_FAULT` 编译期）；E4 用 4 个固定模式 ELF。
3. idleprobe 板级挂起、不采用；E2 用 `fps_dis`（`VDMA: read period = … us -> fps_dis=60`），不可与 `fps_dis_idle` 混用。
4. `gt_now` 需反推（`result_time+age_pub`）；旧生产者（无 sidecar magic2）降级非原子。
5. 真实 `n_dets/cls/score/坐标` 与真实推理延迟仍由真实推理链提供（本版模拟框 + `inf=cap+7 ms`）。
6. 未上板：E2–E6 板级结论不在本冻结件范围。

## 10. 与冻结 32 B 显示 ABI 兼容声明

- **未修改** `src/s5_result_abi.h`（32 B 头 + 16 B 项语义逐字不变）；sidecar 为 `+0x100` 增量扩展，旧消费者可忽略；flush 288 B 不触碰 `+0x120` 之后。
- 显示消费者不读 sidecar ⇒ **阶段5 冻结物不受影响**；v5 仅新增 UART 观测行，不改变任何总线访问语义。