# 独立审查结论（第 3 轮，BI-1 残余）：`PASS`

- 审查者：第三轮独立审查 subagent（`30753425`），只读；验证产物仅在其系统临时目录。
- 时间（UTC+8）：2026-10-22 19:5x
- 被审版本：HEAD `6d8fafe` 的**工作树未提交**修复；sha256 复核一致
  - `check_hardware_gate.py` = `ce62ab20abcee52ae7839f3e113216980b0de40e518de5364bc6c1f9ecc29b66`
  - `test_hardware_gate.py` = `4f419710cda8cbfdf04b210d56086a6e5aabbfab77a3284fc1591c4143f0be38`
- **结论：`PASS`**（第二轮 BI-1 残余关闭条件 ①–④ 全部满足）

## 1. 逐条核验（真实退出码）
| 项 | 方法 | 结果 |
|---|---|---|
| 反斜杠 `file` 被正确应用 | 夹具 A（独立探针） | 占用 → `exit 1 / OCCUPIED`、不在 `unregistered_neutral`、无"未被应用"；反斜杠让出（晚于占用）→ `exit 0 / GO / RELEASED / reasons=[]` |
| 裸名+前缀混写重复 | 夹具 B / B 强变体 | `exit 1`（`缺少信箱目录前缀`、`指向的信箱文件缺席`）；强变体在 HEAD 门禁下 `exit 0 / GO`（复现第二轮 fail-open），固定版 `exit 1 BLOCKED` |
| 共享规范化（①） | 读码 + 函数级实测 | `normalize_file_entry` 同时供 validate/classify；同一 `files` 集合下构造不出"validate 过、classify 找不到" |
| 条件③ | 跨信箱同 basename 遮蔽 | `exit 1`，含"状态类登记项未被应用…等同于静默丢弃" |
| 测试 | `python -B -m unittest … -v` | **exit 0，Ran 32 tests，OK**（复审时点） |
| 对抗自证 | 临时副本回退 | 回退 classify 用原始键 → `exit 1`，failures=1（test_29 抓 GO）；HEAD 门禁 + 新测试 → failures=2 |
| 回归护栏 | 真实登记表+真实信箱 | `exit 0 / GO / RELEASED / reasons=[]`；`CDX-20261022-014` 仍中性 `operation_doc`；状态记录 4 条 |
| 真实只读门禁 | real/real 模式 | **exit 0**，GO/RELEASED/reasons=[]/无未登记；扫描 25/25；无进程、无 index.lock |

## 2. 非阻断观察与处置（本轮已全部处理）
1. **test_32 无判别力** → 已加 `test_33`（让出 920 + 占用 921，传 `--release-id 920`，断言仅"占用态"、无"未提供匹配的 --release-id"）。
2. **条件③ 无独立用例** → 已加 `test_34`（跨信箱同 basename，断言必须 BLOCKED）。
3. **既有残余 fail-open：`scan_mailboxes` 按 basename 跨根去重**（同名文件互相遮蔽，被覆盖方永不解析）→ **已修**：`scan_mailboxes` 返回**列表**（不按名去重）、`validate_registry`/`classify` 改为遍历列表、`mailbox_files_scanned` 输出 `root/basename`。`test_34` 即该 fail-open 的回归锁。
4. 工作树另有未提交改动（`gen_overlay_cases.py`、`s5_overlay.c`，属 §3/§5 工作），不在门禁审查范围。

## 3. 复审后补充验证（Lead 执行）
- `python -B -m unittest scripts.stage5_t01.test_hardware_gate` → **Ran 34 tests，OK，exit 0**（原 32 + test_33 + test_34）。
- 真实只读门禁（real/real）→ **exit 0 / GO / RELEASED**（见 `console/real_gate_postfix3.txt`）。

## 4. 结论与限制
- 三轮审查结论：`CHANGES_REQUIRED`（BI-1/BI-2）→ `CHANGES_REQUIRED`（BI-1 残余）→ **`PASS`**。
- 该脚本现已可用于真实只读门禁（仍须遵守：门禁 GO 不等于 G3/G4/G5，不自动授予硬件使用权）。
- 已知宽松点（未阻断、记录在案）：`--scope` 为子串匹配；跨根同名文件现会各自解析（更严），登记表需按 `root/basename` 精确登记；`.`/`..` 等异常路径未专门测试。