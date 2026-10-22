# 独立审查结论（S5-T01 §0 门禁修复）：`CHANGES_REQUIRED`

- 审查者：独立审查 subagent（`223ebca7-f194-4006-9cd7-bca70483122e`），**只读**、未修改被审文件、未提交、未碰板卡与信箱；验证脚本仅落在其系统临时目录。
- 时间（UTC+8）：2026-10-22 19:40 前后
- 被审版本（w5 分支 `stage5-display-prep`，审查基线 `e4533e1d`）：
  - `scripts/stage5_t01/check_hardware_gate.py` = `8b82906e550e1beaed80837750977313e9d463251d48b945976f335bff49f7d2`
  - `scripts/stage5_t01/hardware_handoff_registry.json` = `d21fbfabf6275c44e3041f63ff031985a472692f282e829e3065ceec76db8120`
  - `scripts/stage5_t01/test_hardware_gate.py` = `0b61be9aeee3e0214db0f8a38646210ca4715a91049d02ddd93beb6a92535a2f`
- **结论：`CHANGES_REQUIRED`**（2 个阻断项；第 1/5/6/7/8 条 PASS，第 2/3/4 条部分满足）

## 1. 已达成的修复目标（审查确认）
1. `python -B -m unittest scripts.stage5_t01.test_hardware_gate -v` → **exit 0，Ran 19 OK**。
2. 独立复核登记表：25/25 真实信箱 MD 哈希一致、4/4 `evidence_quote` 命中原文、id/文件名唯一；**真实模式**门禁（`--lock-check real --process-check real`）→ **exit 0 / GO / RELEASED**（让出 `CDX-20261022-007`、最近占用 `CDX-20261022-006`），6 棵树无 `index.lock`、tasklist 枚举成功且无 `hw_server/vivado/xsdb`。
3. **对抗性验证**：把 v2 在临时副本中改回 v1 全文关键词语义 → 同一合成输入 `v2=GO(exit0)` vs `副本=BLOCKED/OCCUPIED(exit1)`；**真实 v1 原件跑真实信箱 → exit 1**，并把操作文档 `CDX-20261022-014` 判为最新占用（缺陷复现）。
4. Dev 既有 19 项测试在该 v1 语义副本上 → `exit 1，FAILED(failures=5)`（含 test_01/test_04）⇒ 测试确能捕获该回归。
5. 第 1 条 PASS：真实 25 扫描 = 4 状态类 + 21 中性；**`CDX-20261022-014` 正是中性 `operation_doc`**（误判已消除）。
6. 第 4/5/6 条 PASS：顺序/范围判定、锁与进程枚举 fail-closed、授权绑定（缺参数/哈希不符/非原文子串/原文不存在 → 拒绝并 BLOCK；合法授权也不能覆盖真实占用）。

## 2. 阻断项（须修复后复审）

### BI-1 登记表↔信箱绑定单向且可跳过（fail-open）
- 位置：`check_hardware_gate.py:79-89、110-141`
- 实测静默 `exit 0 / GO` 的六种不一致：登记占用文件**缺席**（B4，等于"删/改名登记文件即可放行"）、登记项**缺 `sha256`** → 绑定整段跳过（B5）、同一文件**重复登记**且后一条为中性 kind → 占用被遮蔽（B3c）、`kind` **拼写错误** → 静默中性（B12）、占用**缺 `order_key`** → 被让出覆盖（B8b）、`file` 的 `dsh_mailbox/` 前缀未校验 → 绑定到另一信箱同名文件（B11）。
- 冲突条款：§0.3「证据矛盾仍 BLOCKED、不得靠删除校验'修好'」；脚本 docstring 第 10 行亦自称"文件必须存在且 SHA256 一致"。
- **关闭条件**：对每条登记项做 schema 校验并在失败时 BLOCKED —— file 必须按 root+basename 精确出现在扫描集合；`sha256` 必存且一致；`order_key` 必存；`kind ∈ state_changing ∪ neutral_kinds`；同一文件禁止重复登记；跨信箱状态类 `order_key` 重复（排序歧义）亦 BLOCKED；`OCCUPIED` 时 `release_basis=null`。并补相应隔离测试。

### BI-2 未登记＋文件名中性＋无声明标记的"正文自称占用"不阻断
- 位置：`check_hardware_gate.py:113-123`
- 实测 B6：正文"现由本任务独占使用 JTAG 与 COM4" → 中性 → `exit 0 / GO`，旧让出继续放行。跨方无法写 w5 内登记表，只能靠信箱公告。
- **关闭条件（二选一）**：(a) 门禁运行时做**双向完备性校验**（任一未登记信箱文件即 BLOCKED，把 `test_19` 的单向断言升级为运行时校验 + 中性白名单）；或 **(b)** 对未登记文件也把 `HANDOFF_HINT` 的**正文命中**作为 BLOCK 触发。
- **关键回归约束**：已登记为 `operation_doc` 的文件（如 `CDX-20261022-014`）必须仍为中性，不得因正文含"释放/独占"而阻断或改变状态。

## 3. 非阻断观察（供后续参考）
- 现网 `RELEASED` 判定与主 STATE「2B 已释放」及"无进程/无锁"一致。
- `order_key` 跨信箱重复 7 组（现均非状态类；并列时判 OCCUPIED）。
- 缺 `scope` 的登记项被视为覆盖所有 scope。
- 授权仅机械绑定（`authorized_by` 身份未证；任何含该 note 子串的文件——含 014 本身——都可作原文，门禁只留痕）。
- `OCCUPIED` 时仍写 `release_basis=operator_authorization`（误导）。

## 4. 处置（阶段总控）
- 已按流程把 BI-1/BI-2 退回 Developer（`dev-s5-gate`）修复并补测试；修复后冻结新差异送**同一审查者复审**。
- **在复审 PASS 之前，不得依据该脚本放行真实硬件**（§0.5）。本次板卡使用的事实依据是登记表核验的让出记录（`CDX-20261022-007`）与主 STATE 的硬件空闲叙述，不是该脚本的 GO。