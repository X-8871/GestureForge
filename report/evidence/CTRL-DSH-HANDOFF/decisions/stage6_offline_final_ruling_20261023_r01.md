# 阶段6 离线部分终局裁定：内容冻结、认证与声明附件不予认证（2026-10-23）

- 裁定方：DSH 项目总控；依据：**终局复核 E**（`report/evidence/CTRL-DSH-HANDOFF/reviews/FREEZE_DELTA_E_20261023_r01/REVIEW_VERDICT_F6d.md`）判 `CHANGES_REQUIRED`。
- 触发：复核确认 **`BLK-D1` 真关闭**、**`BLK-D2` 未关闭**，且本轮**新引入 2 处「声明强于产物」**。按 DSH 已预先声明的边界（同类"工具/声明"问题反复出现即**停止迭代**），本裁定**不再开启冻结轮次**。

## 1. 可引用（已独立核实）

- **行为表**：24 项 `approval_status=APPROVED_20261023`、**无 `PENDING`**、`run_id=s6a_g0_20261023_r12`（supersedes r11）、顶层 `G0_PACKET_APPROVED_20261023`；**24 项参数值相对上一冻结零差异**（DSH 与复核各自复算，抽验 `T6-K01=1000`／`T6-C01=2`／`T6-S02=6` 逐字节一致）。
- **S6-B 实现与用例**：26/26 用例、4 项探针、两交付检查器 exit 0；`src/stage6/s6_core.py`/`s6_actions.py`/`s6_predicates.py` 逐字节未动。
- **自证**：`export_selfproof --commit F6d --s6a-run r12 --s6b-run r07` → **`ALL_SELF_PROVEN [0,0,0,0]`、exit 0**（传输克隆内，DSH 与复核各跑一次）；`--commit G6b` 同绿；**反例 fail-closed**：漏传 `--s6a-run` → `NOT_ALL_SELF_PROVEN`、exit 1、reason 明示不再隐式查找。
- **链条/标签**：r1→`1e2a66c`、r2→`8ecd92c`、r3→`f5b749e`、r4→`61caac0d`、r5→`a2d232da`、r6→`538b7923`；旧 tag 未移动；被引用提交**无 amend**（`git fsck` exit 0）；旧轮次证据目录未被就地改写。

## 2. 不予认证（明列，禁止作为通过凭据）

| # | 项 | 事实 |
|---|---|---|
| 1 | 规格文档 **L9/L171/L185/L282/L320/L321** | 仍写"（待批准）/提案，待批准/属待批准项/不是已批准门槛"；12 处只改准 4 处（+2 处加历史语境保留） |
| 2 | **8 条历史修订行**（L14/L21/L28/L30/L32/L34/L36/L38） | **未写回当时状态**（F5==F6d 该 7 行逐字节相同），**7/8 无历史标记**；扫描器历史分支正则 `v1\.\d+（r\d+` 与实际 `v1.5 / r06` 不匹配 |
| 3 | **STATE L43-44 失实表述** | 称"8 条历史修订行写回当时状态并标注历史语境"——与产物不符（**本轮新引入的"声明强于产物"**，已在本裁定中撤回） |
| 4 | **r12 `fix_record.json:16`** | 仍含机读假值 `all_parameters_pending_approval: true`（同一块 `new_run_id` 还是 r07，与文件 `run_id=r12` 矛盾） |
| 5 | **`S6A-C8` / `S6B-C5` 的 statement** | **判别力强于其断言**：扫描器门槛 `TOKENS` **区分大小写** 致 `ASSERT_PATTERNS[3/4/5]` 成**死正则**；`SKIP` 过宽（含 `注入|probe|self_test`）⇒ 复核自造 8 类真实注入中 **6 类 exit 0/CLEAN 漏检** |
| 6 | 残留未标 PENDING 文本 | `coverage_matrix.json:122/127/132/206`、`reachability_notes.json:5`、`cases/case_matrix.json:168`、`build_case_matrix.py:516`（后者已被冻结进 `expected_freeze`） |
| 7 | 令牌陈旧/口径矛盾 | `status_label` 仍 v1.9/r11、r12 摘要标题仍 r09、r07 摘要标题 v1.6/r07；r12 `limitations:44`"指标未获批准（APPROVED_20261023）"、r07 `inputs_manifest:27` 重复"草案值"；`_selfproof` 的 `state_snapshot_sha256` 与 G6b 提交内 STATE 实哈希不一致；r12 manifest 内嵌自证 reason 仍指 F6c |

**tag `stage6-freeze-20261023-r6` 的语义**：指向 G6b，证明**交付提交自证通过**；**不**证明"全部声明文本准确"。

## 3. 修复时机（不单独消耗周期）

上述 1–7 项**并入真手势（6-E）轮次**一并处理——那时本就要为新证据重建两包，声明卫生可与之一并修；在此之前**保持开放登记**、不作为通过凭据、不得据其宣称"已批准口径全包一致"。

## 4. 边界

本裁定**不含** G3（板上验证）、6-D 集成（依赖阶段4/5 接口冻结）、6-E（依赖摄像头）；Wong 批准的 **G4/G5 全阶段验收**仍需集成与实物标准。开放项另有批次 C 三项（陈旧 `fresh_selfcheck_pair`、套件必 FAIL 例仍跑真实 run-dir、`skipped` fail-open 且产物未真正入库）与 `N1`。