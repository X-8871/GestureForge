import io

add = """
### 11.14 生产者 v2：sidecar `S5X1` + seqlock + 序号规则 + 故障注入（r06j）

依据：`docs/obsidian-project/02-方案设计/阶段6_交互控制_6D口径冻结_20261030.md`（6-D 口径冻结）。
**不改冻结的 32 B 显示 ABI**（`s5_result_abi.h` 未动）；扩展全部在新增 `src/s5_publish_abi.h`。

#### 11.14.1 与冻结口径逐条对应

| 冻结口径条目 | 本实现 | 证据 |
|---|---|---|
| sidecar 位置 `0x20800000+0x100`、32 B `S5X1` | `S5_PUB_SIDECAR_BASE=0x20800100`，`S5_PUB_MAGIC2=0x53355831`、`version=1`、`reserved=0` | ELF 内含 `0x20800100`/`S5X1` 常量；host case0d sidecar 打包/回读一致 |
| `session_id=(GT_at_start>>10)&0xFFFF`，碰撞 +1 重试 ≤8 | `s5_pub_pick_session_id()`：读旧 sidecar magic/version/session，相等则 +1 掩 16 位，最多 8 次 | 代码 + 打印 `S5PROD session start: sid=..` |
| `result_seq` 会话内从 0 严格 +1 | `S5Pub_NextSeq()`；`s5_pub_seq` 起点 0 | host case0d：`0→1`、`0xFFFFFFFE→0xFFFFFFFF` PASS |
| `0xFFFFFFFE→0xFFFFFFFF` 正常；`0xFFFFFFFF→0` 拒绝 | `S5Pub_NextSeq` 上限判定（≥0xFFFFFFFF 返回 -1） | host case0d：`0xFFFFFFFF` 拒绝 PASS |
| 同会话回退拒绝并置 `status.overrun=1` | seq 只能 +1；拒绝时 `s5_pub_overrun=1`（sticky），后续发布 `status.bit1=1` | 代码 + `S5PROD REJECT seq: ... status.overrun=1` 行 |
| seqlock：奇→写→flush→偶 | `seqlock++`；写头/项/sidecar 非时间字段；`result_time` 最后写；flush；`seqlock++`；再 flush | `s5_prod_emit()`；host case0d 校验奇=不稳定/偶且相同=稳定 |
| `result_time` = 发布完成时刻，最后写 | 写 `RTIME_LO/HI` 后立刻 `s5_pub_flush()`（288 B） | 代码顺序 |
| 消费者：读序偶→invalidate→读→再读序偶相同，重试 ≤3 超限 TIMEOUT | `s5_pub_consume()` 3 次重试；缺 sidecar（magic2 不符）→ 旧生产者非原子路径 | `S5CONS ...` / `S5CONS sidecar absent` / `S5CONS TIMEOUT` 三种打印 |
| 业务状态优先级（valid=0→ERROR；overrun→ERROR；stale 或 age>200→TIMEOUT；valid=1&n=0→NO_HAND；否则 OK） | `S5Pub_BizState(v, age_ms)`，严格按优先级短路 | host case0d 五条映射逐条 PASS（含 200ms 边界） |
| `age_publish=(GT_now-result_time)×1000/333,333,343` | `S5Pub_AgePublishMs()`（0/未来时间戳→0） | host case0d 7 ms 用例 PASS |
| `NO_HAND` 注入 | 编译期 `S5_PROD_NO_HAND_EVERY_N=N`（每 N 帧 n=0）；故障相位 `no_hand` 常态注入 | 代码；打印 `state=NO_HAND` |
| 故障注入（6-E E4） | `S5_PROD_FAULT=` none/overrun/stale/invalid/no_hand/**cycle**；cycle=按 120 帧相位轮换 none→no_hand→stale→overrun→invalid | 单独 ELF `..._producer_fault.elf` |
| 实时发布时刻可信 | `result_time` 取自全局定时器 `0xF8F00200`（本 BSP 无 `xtime_l.h`，故用 `S5Ticks_Now()`，同一计数器；`_Static_assert(COUNTS_PER_SECOND==S5_GT_HZ)`） | 代码注释 + 静态断言 |

#### 11.14.2 打印格式（新增字段）

```text
S5PROD session start: sid=41237 frame_id=0 tag=a55a status=0x1 rtime_ms=3 (333 Hz)
S5PROD frame_id=187 n=2 status=0x1 sid=41237 seq=187 rtime_ms=5123 age_pub=0 state=OK fault=none cap_ms=5116
S5CONS sid=41237 seq=187 n=2 status=0x1 age_pub=1 state=OK seqlock=374
```
`S5CONS` 是**消费者视角**（seqlock 协议读 + 业务状态映射），每 60 帧一行；异常时为
`S5CONS sidecar absent (旧生产者, 非原子路径)` 或 `S5CONS TIMEOUT (seqlock 3 次重试不一致)`。
`S5PROD REJECT seq: last=4294967295 ... status.overrun=1` 在 seq 拒绝时打印。

**离线样例（模拟 ticks，非板上真实值；板上为真实 GT ticks）**：
`S5PROD frame_id=187 n=2 status=0x1 sid=41237 seq=187 rtime_ms=23 age_pub=0 state=OK fault=none cap_ms=16`

#### 11.14.3 生产者已实现 vs 仍需真实推理链

| 字段/能力 | 状态 | 说明 |
|---|---|---|
| magic/frame_id/n_dets/status、16 B 项布局 | **已实现** | 冻结 ABI，逐字节遵守 |
| `cap/inf` 真实时基 | **已实现** | 全局定时器 ticks；`inf=cap+2,333,334`（7 ms，模拟推理完成） |
| `session_id` / `result_seq` / `result_time` / `seqlock` | **已实现** | sidecar S5X1，规则见 §11.14.1 |
| 业务状态映射与异常路径 | **已实现（可注入）** | ERROR/TIMEOUT/NO_HAND/OK；`S5_PROD_FAULT` 受控注入 |
| 真实 `n_dets/cls/score/坐标` | **仍需真实推理链（Codex C2）** | 当前用 `S5Sim_NextFrame()` 的移动框（源 640×480 坐标） |
| 真实推理延迟（inf 真实完成时刻） | **仍需真实推理链** | 当前固定 7 ms 偏移 |
| 交互层状态机消费语义 | 归 DSH 主控（后续规格） | 本实现只提供生产者 + 消费端读协议样例 |

#### 11.14.4 ELF（构建 exit 0、零告警）

| 变体 | sha256 | size |
|---|---|---|
| **P3q 生产者 v2·有界** | `0fae384afe58846f55b850fcf025d97f5706be28dc5eb8fc1f290d42b581cd4a` | **301,152 B**（text 47,776 / data 72 / bss 2,355,184） |
| **P3q 生产者 v2·长跑** | `97c33f58b974e4ff805debc4a7683617e77852f81ab9b3f0d90cead775975e79` | 301,500 B |
| **P3q 生产者 v2·idleprobe** | `7357c3e52228fcd0eb732b770f200561a2d0dec05c74e03b69c90a1f732563fe` | 300,812 B |
| **P3q 生产者 v2·故障注入**（`-DS5_PROD_FAULT=5` 相位轮换） | `1bd8fe2dde1a102a4ba5daf5ffd5d492a3b8dfc96350406e12504d5dedb3f52a` | 301,664 B |

编译：P3q 默认宏 + `-DS5_PRODUCER=1`（故障版再加 `-DS5_PROD_FAULT=5`；长跑/idleprobe 加对应开关）。
ELF 静态核验：含 `0x20800100`（sidecar 基址）与 `0x53355831`（"S5X1"）常量。

**离线自检**：新增 case0d（sidecar 打包/回读、seqlock 奇偶与一致性、seq 三种规则、业务状态五条映射 + 200 ms 边界、7 ms age 计算、样例 S5PROD 行）全 PASS；
沿用 case0c（v1 打包 + ABI 往返）；渲染/VTC-VDMA/P3p fsync/真实源 6 用例仍 PASS。
"""

p = r"S5_P3B_SW_REPORT.md"
with io.open(p, "a", encoding="utf-8", newline="\n") as f:
    f.write(add)
print("appended")