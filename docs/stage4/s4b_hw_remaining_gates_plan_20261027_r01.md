# 剩余 4 类硬件门禁的完成路径（2026-10-27 r01）

- 现状：八类门禁 **4/8** 已成立（`operator_authorization`、`timing_freeze`、`range_reservation`、`command_delivery_review`）。
- 本文只讲剩下 4 类怎么关、谁关、什么顺序关。不含任何板级结果。

## 0. 一句话结论

| 门禁 | 性质 | 谁能解 | 关键约束 |
|---|---|---|---|
| `g0_approval` | **签字类** | Wong 批准地址图 + 共享地址图 | 两份文件都要 `APPROVED`，且 SHA 会随之改变 |
| `hardware_session_handoff` | **签字类** | main 发 OFFER + w4 写 CLAIM | OFFER 心跳 **1 小时内**有效 |
| `cold_basis` | **现场类** | 你断电/上电，我取证 | 需可绑定的断电证据文件 |
| `exclusive_session` | **现场类** | 我，执行时 | 取证后 **30 分钟内**必须开跑 |

## 1. g0_approval（签字类）

需要三份文件同时成立，缺一不可：

| 文件 | 现在 | 谁推进 |
|---|---|---|
| `docs/stage4/S4B_stage4_address_map.json` | `status=DRAFT_PENDING_REVIEW` | 独立复审 + **Wong 批准** |
| `docs/stage4/S4B_shared_address_map.json` | **本轮已起草**，`DRAFT_PENDING_REVIEW` | 独立复审 + **Wong 批准** |
| `docs/stage4/s4a_stale_age_limit_approval_applied_20261024_r01.json` | 已具备（Wong 10-23 批准 stale 200 ms） | 无需动作 |

### 1.1 地址图批准的具体动作

1. 独立只读复审对象：`S4B_stage4_address_map.json` + `s4b_raw_address_ownership_proposal_20261024_r01.json`（A 方案）。
2. 复审须覆盖：区域边界是否与冻结 2A/2B 一致（`network_input_tensor` / `gf8_weight_package` / `feature_envelope` / `pl_control_csr` 不得被改动）、RAW/META 是否与 W5 显示缓冲冲突、`raw_meta` 内部布局是否与 §8.2 一致。
3. 复审 PASS 后，把 `status` 改为 `APPROVED`，并在文件内记录 `approved_by`、`approved_at_utc8`、`review_binding{path,sha256}`。
4. **注意**：改状态会改变文件 SHA，`g0_approval` 记录必须用**改后**的 SHA 重新生成。

### 1.2 共享地址图批准

本轮起草的 `S4B_shared_address_map.json` 是**投影**，不引入任何新地址：

- 8 个区域全部照抄 stage4 地址图的 base/len/status；
- 两条未决项（`display_buffer` 属阶段3/5、`ps_internal_stack_heap_layout` 属 PS linker）标注 `UNRESOLVED_DO_NOT_GUESS`；
- 明确写「本文件不是访问许可」「数字冲突以 stage4 地址图为准」。

批准同样需要独立复审 + Wong 签字。**它不阻断诊断范围**（本诊断不触达 display_buffer），但 g0 要求它必须是 `APPROVED`。

### 1.3 批准后怎么生成 g0 记录

```powershell
& 'C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe' -B scripts/stage4_s4b/make_hardware_gate_records.py `
  --preparation "<本轮 adapter 准备清单>" `
  --hardware-run-id s4b_ps_tensor_hw_20261027_r01 `
  --out-dir report/evidence/S4-B/s4b_hw_gates_<新RunId> `
  --review-file report/evidence/S4-B/s4b_adapter_review_20261027_r02/adapter_review.json
```

（当前生成器尚未包含 `g0_approval`；批准后需扩展生成器补三段绑定：`address_map_binding` / `shared_address_binding` / `timebase_binding`。）

## 2. hardware_session_handoff（签字类）

三步，且**必须倒序准备、正序执行**，因为 OFFER 只有 1 小时生命：

```
T-∞   你授权硬件窗口（书面一句话即可，超出"只交接 w4 写权"的范围）
T-0   先确认 g0 / cold_basis / exclusive 都已就绪（否则 OFFER 会白烧）
T+0   main 提交 OFFER 行（心跳写当前时刻）
T+5m  我用 make_claim_line.py 生成 CLAIM 行并提交
T+15m 补齐 exclusive_session 现场取证
T+20m 开跑（必须在 OFFER 心跳后 1 小时内开始校验）
```

OFFER 行模板与逐字段校验要求见 `docs/stage4/s4b_hw_offer_claim_20261027_r01.md` §4。

**最容易踩的坑**：OFFER 提交后如果 g0 还没通，1 小时后 OFFER 自动失效，必须重新提交（会留下两条历史行，第二条才是有效的，但 `_unique_handoff_task_row` 要求唯一——所以旧行必须先撤销或在原行上更新并重新提交）。

## 3. cold_basis（现场类）

`basis_kind` 只接受两种：

| 方式 | 需要什么 | 谁做 |
|---|---|---|
| `physical_power_cycle` | 断电到上电的时间戳 + 可绑定证据文件（如串口冷启动日志、电源开关照片、或你的一句话确认记录） | 你断电，我落证据 |
| `independently_proven_cold_lifecycle` | 独立证明旧 AXI 生命周期已清除（无历史 session、无 hw_server 残留、PL 冷配置） | 我取证 |

**最快的路径**：你执行一次物理断电 → 上电，我记录时间戳 + 当时 `hw_server` 未运行 + 无历史 session，生成 `physical_power_cycle` 记录。

记录字段（adapter 要求）：`status=PASS`、`hardware_run_id`、`artifact_identity_sha256`、`old_axi_lifecycle_cleared=true`、`basis_kind`、`evidence_binding{path,sha256}`。

## 4. exclusive_session（现场类）

执行时现场取证，30 分钟有效窗口。必须同时满足：

| 字段 | 判据 |
|---|---|
| `status` | `PASS` |
| `exclusive` | `true` |
| `hw_server_pid` | 正整数，且进程表中确有该 `hw_server.exe` |
| `xsdb_peer` | 精确 `{Host: localhost, Port: 3121}` 或 `{127.0.0.1, 3121}` |
| `uart_port` | 非空，且与交接的 stream 端口一致（建议 `COM4`） |
| `verified_at_utc8` | 距今 ≤ 1800 秒 |

生成器：`scripts/stage4_s4b/make_runtime_gate_records.py`（读取实时 pid / 端口，写出记录并立即打印剩余有效秒数）。

## 5. 推荐执行顺序（一次成功的最短路径）

```
第 1 步  地址图 + 共享地址图：独立复审 → 你批准（两份 status→APPROVED）
第 2 步  我重新生成 g0_approval（用批准后的 SHA）
第 3 步  你物理断电 → 上电；我生成 cold_basis
第 4 步  你授权硬件窗口（一句话）
第 5 步  main 提交 OFFER（心跳=当前）
第 6 步  我提交 CLAIM（make_claim_line.py）
第 7 步  我启动 hw_server + xsdb + UART，生成 exclusive_session（30 分钟窗口开始）
第 8 步  adapter `execute_prepared` 开跑
```

第 5–8 步必须在 **1 小时内**全部完成；第 7–8 步必须在 **30 分钟内**完成。


## 7. 地址图复审结论（2026-10-27，CHANGES_REQUIRED）

独立复审判 **不可批准**，6 项阻断，其中 3 项已在共享图 r02 修复：

| 编号 | 内容 | 状态 |
|---|---|---|
| B2 | 共享图非忠实投影（新增 producer 事实、自述"不含新事实"为假、`ps_app_arena` 措辞矛盾） | ✅ r02 已修：改回源图语义 + `path_specific` |
| B3 | "不触达 display_buffer"可被 ELF 布局反驳 | ✅ r02 已修：明写 `.bss=[0x00118100,0x0071E6D0)` 覆盖 W5 buf1 `0x00703800`，并加"禁止并发加载" |
| B4 | `injection_frame_rgb` 未标已取代 | ✅ r02 已修：加 `superseded_by=raw_frame` + `must_not_load` |
| **B1** | **`network_input_tensor` 写入方方向冲突** | ❌ 待 **Wong 裁决** |
| B5 | 两个离线校验器硬编码 `DRAFT`，翻状态会让套件失败 | ❌ 待批准时同批改 |
| B6 | 契约 / readiness / 缺口表四处绑定 + "仍为 DRAFT"表述会过期 | ❌ 待批准时同批重绑 |

### 7.1 B1 是什么（必须你定）

同一个 519,168 B 张量，两条路径的写入方说法互斥：

| 路径 | 写入方 | 出处 |
|---|---|---|
| UART / CPU | **PS 写**（memcpy 到 arena），PL 只读 | 地址图 `network_input_tensor`、2B 接口 `:51`、r13 实测 |
| mailbox / RAW | **PL 预处理写**，网络 master 只读 | readiness `:175/:193/:306`（待批准的 mailbox 设计） |

契约规定"各 region 方向以地址图 `cache_maintenance` 为准"。所以：**按现图批准，等于批准"PL 不得写张量"**，mailbox 路径当场作废。

三个选项：

| 选项 | 做法 | 代价 |
|---|---|---|
| A | 地址图内按路径拆方向（`uart_cpu`: PS 写；`mailbox_raw`: PL 写），同步 `cache_maintenance` | 改冻结 2A/2B 区域的所有权表述，需 2B 层级确认 |
| B | 地址图仅覆盖 UART 路径，mailbox 方向另立新条目并单独获批 | 文件变复杂，但不动已冻结语义 |
| C | 暂不批地址图，先把 mailbox 路径整体推迟到下一阶段 | 硬件诊断只能走 UART/CPU 路径（即现 r13 单元的能力范围） |

**我的建议是 C 或 B**：当前 adapter 与准备清单就是 UART/CPU 路径（r13），先跑通它；mailbox 那套（G-20/G-05/G-10/G-11）本来也还没实现完。

## 6. 本轮明确不做

- 未把任何 `status` 改为 `APPROVED`（批准权在 Wong）。
- 未在 main 写任何行，未提交 OFFER/CLAIM。
- 未启动 hw_server / xsdb / 串口，未接触板卡。
- `ENABLE=0` 未变。
