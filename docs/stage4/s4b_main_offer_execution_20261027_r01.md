# main 侧硬件 OFFER 执行指引（1 小时内有效）

- 时间：2026-10-27 14:57（UTC+8）
- 触发：Wong 已授权硬件窗口（R-1 完成）
- 卡点：**R-2 只能由 main 提交**，阶段4 不得写 main
- 本文件由阶段4 生成，供 main 侧或 DSH 执行

---

## 1. 现状（已实测）

| 项 | 实测结果 |
|---|---|
| main 分支 / HEAD | `main` / `bdb7a360916641382a04f018c668774543e45b8e` |
| main STATE 中的 OFFER 行 | **不存在**（`grep S4-B-REAL-02B::s4b_hardware_session_handoff` 无命中） |
| main STATE 中的写权行 | **不存在**（不影响 OFFER 校验，OFFER 只需一行） |
| main 工作树未提交改动 | **423 项**，其中 `.codex/STATE.md` 已被修改 |
| w4 写权负责人 | `Workbuddy 阶段4总控`（`_state_stage_owner` 实测可解析） |
| 其余门禁 | **6/8**：operator_authorization / timing_freeze / range_reservation / command_delivery_review / g0_approval / cold_basis 均成立 |

只差两类：`hardware_session_handoff`（本文件解决）与 `exclusive_session`（OFFER 到位后现场取证）。

---

## 2. 要做的一件事

在 main 提交**唯一一行** OFFER 到 `.codex/STATE.md`。

不要手写。用生成器：它会读 main 的 HEAD 取「起始提交」、读 w4 的写权负责人拼出
`OFFERED Workbuddy 阶段4总控`，并用 adapter 自己的解析器**离线自校验**这一行。

```bash
python -B D:/codex-worktrees/w4/scripts/stage4_s4b/make_offer_line.py \
  --run-id s4b_ps_tensor_hw_20261027_r01
```

预期输出（心跳会取当前时间，下面为示例）：

```text
任务=`S4-B-REAL-02B::s4b_hardware_session_handoff` | 负责人=`DSH` | 工作树/分支=`D:\FPGA_Competition / main` | 起始提交=`bdb7a360916641382a04f018c668774543e45b8e` | 允许修改范围=`S4B_PS_TENSOR_DIAGNOSTIC` | 未提交改动归属=`存在 423 项未提交改动，提交 OFFER 前须先清理或登记归属` | 让出声明=`OFFERED` | 心跳(UTC+8)=`2026-10-27 14:54` | 证据入口=`hardware_run_id=s4b_ps_tensor_hw_20261027_r01` | 恢复命令=`...` | 状态/下一接手方=`OFFERED Workbuddy 阶段4总控`
```

它会打印 `[OK] 自校验通过`。若打印 `[FAIL]`，按其列出的问题修，不要强行提交。

---

## 3. 提交（在 main 执行）

```bash
git -C "D:/FPGA_Competition" add -- .codex/STATE.md
git -C "D:/FPGA_Competition" commit -m "chore(stage4): offer hardware window to w4 (s4b_ps_tensor_hw_20261027_r01)"
git -C "D:/FPGA_Competition" rev-parse HEAD   # 记下这个 40 位 SHA
```

### 三个必须注意的点

1. **只 add `.codex/STATE.md`**。main 工作树有 423 项未提交改动，`git add -A` 会把它们全部卷进这次提交。
2. **提交后不要再动 main 的 `.codex/STATE.md`**。校验要求 OFFER 行在「OFFER 提交 / main 当前 HEAD / main 工作树」三处**完全一致**；提交后再改 STATE（哪怕只改一个字不加提交），工作树那条就对不上，OFFER 立即失效。
3. **`起始提交` 的值**是生成时的 main HEAD。如果生成之后 main 又产生了新提交，**必须重跑生成器**，否则「起始提交」不再是 OFFER 提交的祖先，校验会拒。

### 关于那 423 项未提交改动

它们会被 `git add .codex/STATE.md` 带入的只有 STATE 一个文件；其余 422 项不受影响。
但 STATE 里既有的未提交差异会一并进入这次提交——这与阶段4 早前遇到的是同一类整文件问题。
内容不会丢失，只是这批差异的历史归属会落在「OFFER 提交」名下。若不接受，需先由 main 侧单独处理 STATE 差异，再提交 OFFER。

---

## 4. OFFER 提交后，阶段4 的动作（1 小时内完成）

```bash
# ① 生成 CLAIM 行（自动取 offer_commit / blob_oid / sha256 / 起始提交）
python -B D:/codex-worktrees/w4/scripts/stage4_s4b/make_claim_line.py \
  --offer-commit <OFFER提交SHA> --run-id s4b_ps_tensor_hw_20261027_r01

# ② 把打印出的 CLAIM 行加进 w4 的 .codex/STATE.md，单独提交
git -C D:/codex-worktrees/w4 add -- .codex/STATE.md
git -C D:/codex-worktrees/w4 commit -m "chore(stage4): claim hardware window"

# ③ 生成 handoff 门禁记录（绑两侧 blob）
python -B D:/codex-worktrees/w4/scripts/stage4_s4b/make_handoff_record.py \
  --offer-commit <OFFER提交SHA> --claim-commit <CLAIM提交SHA> \
  --hardware-run-id s4b_ps_tensor_hw_20261027_r01 \
  --out-dir report/evidence/S4-B/s4b_hw_handoff_<RunId>

# ④ 机检：应只剩 exclusive_session
python -B D:/codex-worktrees/w4/scripts/stage4_s4b/check_hardware_gate_readiness.py \
  --run-id <RunId> --preparation "D:/codex-worktrees/w4/tmp/4/S4-B-REAL-02B/s4b_ps_adapter_g3_20261027_r01/adapter_preparation.json" \
  --hardware-run-id s4b_ps_tensor_hw_20261027_r01 \
  --gate-dir report/evidence/S4-B/s4b_hw_gates_<新RunId> \
  --evidence-dir report/evidence/S4-B/s4b_hw_gate_readiness_<新RunId>

# ⑤ 建会话并留证（30 分钟内开跑）
python -B D:/codex-worktrees/w4/scripts/stage4_s4b/make_runtime_gate_records.py \
  --role exclusive_session \
  --preparation "D:/codex-worktrees/w4/tmp/4/S4-B-REAL-02B/s4b_ps_adapter_g3_20261027_r01/adapter_preparation.json" \
  --hardware-run-id s4b_ps_tensor_hw_20261027_r01 \
  --out-dir report/evidence/S4-B/s4b_hw_gates_<新RunId> --expect-uart COM4
```

**时间约束（硬）**：

- OFFER 心跳 **1 小时**有效 → ①–④ 必须在 1 小时内；
- `exclusive_session` 校验 **30 分钟**内有效 → ⑤ 之后必须立即开跑；
- OFFER 过期 → 必须由 main **重新提交**一行新的 OFFER，不能改旧行（改旧行会让「OFFER 提交内的一致性」失效）。

---

## 5. 工具就绪状态（已负控验证）

| 工具 | 作用 | 负控结果 |
|---|---|---|
| `make_offer_line.py` | 生成并自校验 main OFFER 行 | 自校验通过；main 工作树脏会 `[WARN]` |
| `make_claim_line.py` | 从 OFFER 提交生成 w4 CLAIM 行 | 对无 OFFER 的提交 `exit 1` |
| `make_handoff_record.py` | 绑两侧 blob 生成 handoff 记录 | 两个合法但无 OFFER 的提交 → 「OFFER 行数为 0」，`exit 1`，无残留目录 |
| `check_hardware_gate_readiness.py` | 门禁机检（判定权归 adapter） | 六类伪造记录被逐字段拒绝 |

---

## 6. 不做的事

- 阶段4 不写 main、不代签 OFFER；
- 不启动 `hw_server` / `xsdb`，不打开串口，不装载位流——在 handoff 通过之前；
- 不把「Wong 已授权窗口」等同于「OFFER 已发出」：授权是 R-1，OFFER 是 R-2。
