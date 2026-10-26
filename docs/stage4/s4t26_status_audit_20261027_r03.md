# S4-T26 状态审计（2026-10-27 r03，Workbuddy 阶段4总控）

- 审计范围：task-26（S4-T26-GOLDEN-REBIND）当前状态、输入缺口、producer 身份与黄金来源。
- 工作树/分支：`D:\codex-worktrees\w4` / `stage4-infer-prep`，HEAD `0fcd67595ae5be85b99ee93928a9b265786f3af0`。
- 本文件只做**只读审计与关闭条件登记**：未改算法、未生成黄金、未跑真实推理、未接触硬件。
- 不构成 G0/G1/G3/G4/G5 或实物验收结论；`ENABLE=0`、RAW 系统 G0 未闭合、P/4-D/G3/G5 `NOT_RUN` 全部不变。
- 文档版本：第 3 版（前两版经独立 Reviewer 判 `CHANGES_REQUIRED` 后修订；早期草稿为未提交文件，已由本版取代，不主张其留存）。

## 1. 结论摘要

| 项 | 审计结论 |
|---|---|
| 接管 | 真实 `--claim` `HANDOFF_OK / exit 0 / 9 PASS`（2026-10-27 00:41:39） |
| 既有 15 项 | 未变、未清理、未暂存；19 个未跟踪文件 SHA **19/19 一致**；STATE 既有差异（27 增/8 删）仍在工作区未提交 |
| G0 | r13 `BLOCKED / exit 2 / 0 FAIL`，两项 producer SHA 不一致仍成立 |
| producer 身份（B1） | **不可复现**：记录 `f025f5ab…`（EXE）/`0487e694…`（hook）在固定路径与全部候选副本（4 个 EXE、5 个 hook 源）中零命中 |
| 成因 | 报告生成 13:45:35；固定路径 EXE/hook mtime 为 18:12:10 / 18:11:39（+15,995 / +15,964 秒）⇒ 校准跑完后该路径被重新构建并覆盖 |
| 黄金来源 | T25/T29 冻结张量材料化通过；两样本 head13/head26 黄金齐备且 SHA 自洽 |
| 旧结论是否仍适用 | **否**：`2929/5070、10358/20280` 产生于 T25 预处理修复（`e65ea51`）之前；修复后诊断探针 38/38 层逐字节一致、四份 head 与黄金完全一致 |
| 权威门（B2） | 当前桥接器字节（`8a80c33c…`）**从未产生过 PASS 门运行**：7 次桥接结果全部早于该提交 ⇒ task-26 仍 `BLOCKED` |

一句话：**数值层面已被后续证据推翻，程序层面仍未重跑，所以状态仍是 BLOCKED，不能改写成 PASS。**

## 2. producer 身份审计（B1，未闭合）

- 报告：`report/evidence/S1-T02/20260922_s1_t02_d2_tiny416_activation_calibration_r1.json`，`generated_at_utc8 = 2026-09-22T13:45:35+08:00`，原始字节 SHA `6d73283c…87216`。该值已由脚本 `--expect-report-sha256` 内置钉死：不一致即 `exit 2`；若要换钉必须显式 `--allow-repin`，且换钉后结论仍为 `BLOCKED/1`。
- 报告的 producer SHA 由生产工具**运行期**计算（`verification/s1_t02_d2_activation_calibration.py` 第 248/250 行 `sha256_file(...)`）。
- 工具 SHA 的字节口径（与 B3 同类，必须写明）：报告记录路径 `D:\FPGA_Competition\verification\s1_t02_d2_activation_calibration.py` 原始字节 = `288390f8bafe2c601604556e61f204a35305f1503802c3ca7bf96e7788f7dde4`（14,925 B，LF），与报告 `tool.sha256` 逐字符一致；**仓库内同名副本为 CRLF（15,267 B，raw `53a0d2af…`），归一化后同为 `288390f8…`**。
- 复算结果：

| producer | 记录值 | 固定路径当前值 | 候选副本 | mtime 差 |
|---|---|---|---|---|
| `darknet.exe` | `f025f5ab…f229948` | `879148e0…5ce1289`（3,087,872 B） | 4 个，0 命中 | +15,995 秒 |
| `network_kernels.cu` | `0487e694…ef7d65` | `ef907ba3…2f196f`（41,420 B） | 5 个，0 命中 | +15,964 秒 |

- 旁证：`darknet_source` 子仓库 HEAD = 报告记录的 `darknet_source_commit 59596d7`，其 `src/network_kernels.cu` 提交版 SHA `52020bb8…d8379`（30,853 B）；hook 版（41,420 B）是**未提交的工作区改动**。构建目录内 173 个 `.obj` 的时间分布为 13:38×74、13:39×12、17:36×84、17:45×2、18:12×1 —— **84/173 落在 17:36（报告之后），最新一个 18:12 与被覆盖的 EXE 同时段**。
- 判定：**原始 producer 字节未保留，无法用现有文件重建该身份**。mtime 先后只是覆盖时点的旁证，不是内容来源的证明。

## 3. 黄金来源审计（材料齐备）

- 材料化清单：`s4t26_golden_rebind_20261026_r02/golden_materialization_manifest.json`，状态 `MATERIALIZED_AND_SHA_VERIFIED`，来源为 T25 分片按 `byte_offset` 切片、未重新量化。
- 独立复算四份 head 二进制与黄金文件：

| 样本 | head13 | head26 |
|---|---|---|
| `test_fist_000`（idx 0） | `07b59ca3…d2cab6` 一致 | `7524ce5c…e7be14e` 一致 |
| `approved_no_hand_001`（idx 102） | `902bb209…3730ea6d` 一致 | `f96cca66…0277e1c2` 一致 |

- 边界（不得夸大）：诊断探针“38/38 层逐字节一致”中，layer 30/37 是 yolo 层且 `t25_stored=false`（别名指向 29/36），这两层不是与独立存储的 T25 张量比对，而是与头部张量别名比对。**结论仍成立，但不得表述为“38 层独立存储张量全部一致”。**

## 4. 证据冲突与时间线

| 时间 | 事件 | 证据 |
|---|---|---|
| 10-26 22:01 | G0 r13 `BLOCKED`（producer SHA） | `s4t26_g0_inputs_20261026_r13/preflight_verification.json` |
| 10-26 22:12 | 权威桥接 r02 `BLOCKED`：sample_102 head 一致、sample_000 不一致 | `s4t26_golden_rebind_20261026_r02/replay_forward_bridge_result.json`；其桥接器身份 `6780446f…` 记录在同目录 `preflight_verification.json` 的 `bridge_source.sha256` |
| 10-26 23:00 | 诊断探针 r02：`LAYER_MATCH_AND_REQUIRED_GATES_PASS`，`first_byte_mismatch_layer = null`，两门 head 全一致，D9/NMS 2→1 | `s4t26_layer_divergence_20261026_r02/layer_divergence_report.json`（桥接器 `8a80c33c…`） |
| 10-26 23:05 | 提交 `e65ea51`：桥接器改用 T25 冻结预处理（blob `8a80c33c…`） | `git show e65ea51:scripts/stage4_s4ctrl/replay_forward_bridge.py` |
| 10-27 00:36 | 治理提交 `0fcd675` | `git log` |

- 因此：`2929/5070、10358/20280` 属旧预处理结果，对当前代码不再适用；但诊断探针只是“观察 `forward_one` 局部变量”的诊断，**不是权威门运行**，不能替代门 PASS。
- 权威门（两门 + 单字节负控 + PNG `IMREAD_UNCHANGED` + task-25 回放帧）在当前桥接器上 `NOT_RUN`。

## 5. 字节口径歧义（B3）

| 文件 | 原始字节 SHA | CRLF 归一化 SHA | 绑定方 |
|---|---|---|---|
| `report/evidence/S2A-T29/cpu_decode_nms_reference.json` | `26392c8d…071d33`（274,238 B，8,513 处 CRLF） | `24361a13…a0231`（265,725 B，= HEAD blob） | 契约 `s4a_stage4_g0_fields.json` 绑**归一化**；`golden_materialization_manifest.json` 绑**原始** |
| `report/evidence/S2A-T25/cpu_layer_golden_index.json` | `2d76f9e2…8c72` | `cbda3f25…f6950d` | 材料化清单绑**原始** |

- 两者内容同源（归一化后与 HEAD blob 一致），**不是内容漂移**；但跨记录按字节比对会得到假不一致。
- 关闭条件：每条绑定记录显式声明 `byte_basis`（raw / crlf-normalized / git-blob），校验器按声明复算；新增记录一律声明。

## 6. 关闭条件与责任方

| 编号 | 阻断 | 关闭条件 | 责任方 | 缺失文件/前置 |
|---|---|---|---|---|
| B1 | activation producer 身份不可复现 | 二选一，须 Wong 裁决：**(a)** 登记“provenance 断点”，冻结 scale 仅按数值 SHA 使用，并为任何新前向单独绑定 producer；**(b)** 授权用当前 EXE/hook 重跑 512 样本标定生成新 scale 集（会改变冻结值，需回归 2A/2B/4 全部依赖） | Wong 裁决；阶段4 总控执行（离线） | 原始 `darknet.exe` = `f025f5ab…`、hook = `0487e694…`；本地已确认无副本 |
| B2 | 当前桥接器无权威门 PASS 运行 | 用当前字节 `8a80c33c…` 以**新 RunId** 跑两门 + 负控 + PNG + 回放帧，产出 `status=PASS / 整型 exit 0` 且 `preflight_verification.json.bridge_source.sha256` 等于当前字节、五项必备检查全 PASS 的运行 | 阶段4 总控 | 需先明确 G0 仍 BLOCKED 时是否允许执行门运行（现有 `task_blockers` 会 fail-closed 拦下） |
| B3 | 绑定字节口径歧义 | 各记录声明 `byte_basis` 并复算；历史记录保留原值并追加说明 | 阶段4 总控 + 独立 Reviewer | 无 |
| B4 | 旧 r02 证据缺输入身份字段 | 当前桥接器已输出 `preprocessing_representations`，但只有重跑才会落盘 | 依赖 B2 | 无 |
| B5 | task-27 输入包（下游依赖，不计入本轮阻断） | 依赖 B2 全 PASS；生成后须标 `replay_only` | 阶段4 总控 | 依赖 B1/B2 |

**不得**用诊断探针、离线回放或历史结果替代上述任一项。

## 7. 本窗口已做 / 未做

已做（全部只读或离线，均留证据）：

| 产物 | 入口 | 真实结果 |
|---|---|---|
| 接管与保护核验 | `report/evidence/S4-CTRL/w4_workbuddy_takeover_20261027_r02/manifest.json` | claim `exit 0 / 9 PASS`；19/19 字节未变 |
| producer 身份与绑定审计 | `report/evidence/S4-CTRL/s4t26_producer_audit_20261027_r04/audit.json` | `BLOCKED / exit 1`，7 项未闭合 |
| 门禁证据对齐 | `report/evidence/S4-CTRL/s4t26_gate_reconcile_20261027_r05/reconcile.json` | `BLOCKED / exit 1`，2 项未闭合 |
| 工具 fail-closed 自测 | `report/evidence/S4-CTRL/s4t26_failclosed_selftest_20261027_r07/selftest.json` | `PASS / exit 0`，20 项子进程用例 + 1 项函数级真值表（残留检查在临时目录上下文内执行，T16a/T16b/T17 均记录 `residue_present=false`） |

术语区分：本节“工具 fail-closed 自测”测的是**检查器自己的判定逻辑**；B2 关闭条件里的“单字节负控”是**门内检查项**（真实前向的扰动对照），两者不同，后者仍是 `NOT_RUN`。

留档但不作为证据（均为本窗口更早的迭代，原样保留、不被引用为结论依据）：`s4t26_producer_audit_20261027_r00/`（首跑 TypeError，已补 `NOT_EVIDENCE` manifest，无 `audit.json` 结论）、`…_r01|r02|r03/`、`s4t26_gate_reconcile_20261027_r01|r02|r03|r04/`、`s4t26_failclosed_selftest_20261027_r01|r02|r03|r04|r05|r06/`。

未做（`NOT_RUN`，不得当作已做）：真实网络推理、权威门运行、单字节负控、task-27 包、任何板卡/JTAG/COM4/摄像头/HDMI/Vivado/hw_server 操作。

## 8. 检验器边界与复跑命令

```bash
PY=C:/Users/22061/.workbuddy/binaries/python/versions/3.13.12/python.exe
"$PY" -B scripts/stage4_s4ctrl/audit_t26_producer_provenance.py \
  --evidence-dir report/evidence/S4-CTRL/s4t26_producer_audit_<新RunId>
"$PY" -B scripts/stage4_s4ctrl/reconcile_t26_gate_evidence.py \
  --evidence-dir report/evidence/S4-CTRL/s4t26_gate_reconcile_<新RunId>
"$PY" -B verification/test_s4t26_failclosed.py \
  --evidence-dir report/evidence/S4-CTRL/s4t26_failclosed_selftest_<新RunId>
```

- 退出码语义：`0` = 全通过；`1` = 存在未闭合阻断（常态）；`2` = 输入或环境错误（证据缺失/损坏/结构非法、参数非法、RunId 复用）。
- 三个脚本都不接受“跳过”开关：绑定审计强制；报告 SHA 钉死；门通过必须是 `status=PASS` + **整型** `exit_code=0`（排除 `False`/`"0"`）+ 运行期桥接器 SHA 等于当前字节 + 五项必备检查全 PASS。
- **PASS 的边界**：`reconcile` 输出 `PASS` 只表示“证据文件内部自洽且满足判定条件”。伪造一份自洽证据根同样能得到 PASS（负控 T14 正控即此路径），因此 PASS 必须与桥接器原始运行证据一起使用，不得单独作为“门已在实机跑过”的证明。
- 复核记录：第 1 轮判 `CHANGES_REQUIRED`（P1–P10：时间戳当通过、`--no-binding-audit` 绿通道、报告未钉死、退出码 1/2 混同、`.obj` 表述、r01 表述、B 编号、工具 SHA 口径、r00 无 manifest、命名措辞）；第 2 轮判 `CHANGES_REQUIRED`（F1 `False == 0` 绿通道、F2 非法结构 JSON 崩成 exit 1、F3 文档与 r00 manifest 不同步、F4 负控自述不实、R1 STATE 哈希口径）；第 3 轮判 `CHANGES_REQUIRED`（B-1 `RecursionError` 逃逸成 exit 1、B-2 落盘失败留 0 字节残文件、B-3 单运行结果损坏被降级为“没跑过”，另 N-1…N-6）。上述均已处理并以新 RunId 重新留证，未沿用旧证据。
