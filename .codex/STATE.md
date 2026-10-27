# 阶段5 状态（HDMI 结果显示与结果关联）——**离线范围冻结**

## 收尾快照（2026-10-27 19:10 UTC+8；本节优先于下方任何历史陈述）

- **冻结口径 `OFFLINE_SCOPE_FROZEN`（离线范围冻结）**：只冻结离线契约/实现/证据字节集；**不主张** G0/G1/G3/G4/G5 或任何板级/实物/实时结论。本卡（`task-29`/`S5-T04`）**不需要板卡**，本轮未连接、未加载位流、未烧录。
- **冻结前基线**（构建冻结集时 HEAD）：`2a2d2cc01cd31444a1a854115d99a31cbe8499bf`；**冻结提交（被审）**：见 §7 与外部报告（`git log -1` 为权威）。
- **冻结集**：`report/evidence/S5-T04/s5_freeze_20261027_r05/frozen_set.json`，**77 个成员 / 覆盖 196 个已跟踪文件**（契约与字节保真规则含 `.gitattributes` 共 14 / 离线实现 3 / 离线 replay-display 证据 44 / S5-T02 离线 7 / 宿主只读引用 9；目录成员为 `file_set`，逐件列 path+sha256+bytes），sha256 `109254238e2aede8ab9005ed153e768e611c3ba325a5b1b75b312b415408b1bf`。
- **校验器**：`verification/verify_stage5_frozen_set.py`（只读、fail-closed：0 一致 / 1 不一致 / 2 输入或环境错误；`--frozen-set` **必须显式给出**，禁止内置 RunId 默认路径）→ 实测 **exit 0 / `FROZEN_SET_VERIFIED`（77/77）**；**注入自测**（必须失败）→ **exit 0 / `SELFTEST_PASS`**：clean=0、改一字节=**1**、删一件=**2**。
- **离线回归主套件**：10 个模块 **142 项 / 0 失败 / 2 skip / exit 0**（168 s，虚拟长跑 106 573 帧在内）。
- **包装检查器**：`check_stage_delivery --mode evidence` M1/M2 均 **exit 0 / CHECKS_OK**；运行器 `final_exit=0`。
- **安静窗口**：0 个 `vivado.exe/xsdb/hw_server/vitis/xsim`；2 个 `vivado-mcp-server-windows` 桥接进程按 `DSH-20261027-017` 只作信息记录（非板级占用）。工作树无已跟踪改动、无 `index.lock`。
- **F6 自证**：冻结提交 `git archive` 导出（无 Git 元数据）+ `--shared --no-checkout` 独立检出两种形态下复跑校验器/检查器，见 `report/evidence/S5-T04/s5_freeze_f6export_20261027_r01/`。
- **tag**：`stage5-offline-freeze-20261027`（本地附注 tag，**不 push**）。

## 写权与交接（更正过期陈述）

- 旧 STATEMENT「Codex 仍持本树写权」**已过期**：本树写权自 **2026-10-26 21:21** 起由 **DSH 阶段5 总控**持有（`handoff_check --claim` = `HANDOFF_OK` PASS 9 / 0）。
- 本卡执行方＝DSH 阶段5 总控；复审由 DSH 项目总控另派 Reviewer；**复审期间停写被审对象**。

## 冻结范围（只此四类）

1. **离线契约/规格**（`docs/stage5/**`）：显示契约 JSON、输入绑定 JSON、离线参数/用例骨架、JSON 契约、`stale=200 ms` 的 UR-3 决策（引用 Wong 批准回执）。
2. **离线实现**：`scripts/stage5_t03/**`（渲染/回放/长跑/多几何/HUD 遮挡/JSON 契约/阶段4 冻结包消费）＋ `verification/s5_display_geometry_reference.py`。
3. **离线证据包**：`s5t03_offline_replay_display_…_r06`、`…offline_long_run_replay…_r04`、`…multi_geometry_render…_r02`、`…json_contract…_r04`、`…hud_occlusion…_r02`、`…stage4_frozen_replay…_r04`、`…stage4_positive_replay…_r01`、`S5-T01/s5t02_offline_dynamic_map_20261027_r02`。
4. **宿主只读引用**（`scope=host`）：阶段3 参考帧 `939fce22…` 与回放绑定、阶段4 回放结果包冻结记录/索引/带框包、Wong `stale=200 ms` 回执、阶段3/阶段4 局限引用。

## 明确不主张（逐条）

真实回放接入（板上/实时）｜板上动态映射/绘制｜摄像头真实采集｜真实集成 30 分钟｜T5-10 板上回归｜HUD 屏上视觉确认｜真彩目视｜任何 G0/G1/G3/G4/G5 通过｜真实采集质量/颜色｜端到端延迟实测（时钟 `PENDING_MEASUREMENT`）。
`task-27`（回放/彩色输入路径实现 + 用阶段4 冻结回放包做离线动态回归）**整体 NOT_RUN**；本冻结只覆盖既有离线骨架与离线消费。

## 继承的上游局限（引用不改写）

- 阶段3：VDMA 首帧 bit11 `PARTIAL_OPEN`、task-11 `BLOCKED_NOT_RUN`、`TIMING-17`/I-O delay 未签核（`dbdf/…/S3-T17/stage3_closeout_20261026_r01/manifest.json`）。
- 阶段4：`complete_stage4_or_RGB_preprocess=NOT_CLAIMED`（`w4/docs/stage4/s4_stage4_freeze_supplement_hardware_20261027_r01.md`）。

## 未闭合项

1. **历史模块已知缺口**：`scripts/stage5_s5a|s5b|s5c` 探测 83 项 / **18 失败**（根因：其测试依赖 w4 侧黄金数据 `s4c_replay_20261021_r05`、`S4-B/20261021_r13` 上游漂移）；不在冻结集、不计入本冻结回归主张，原始输出见冻结包 `console/legacy_suite_known_gap.txt`。
2. `task-27` NOT_RUN（阶段4 回放包已冻结、本树有离线消费，但该卡未交付）。
3. 板级 B1–B10 全项暂停：Wong 拔板后未重连复验；重连后需先过第 0 步（占用/部署身份/运行期回读地址/**真彩目视需 Wong 在场**），再按 `CDX-20261023-018` §3 发单次窗口。
4. 端到端真实链窗口（`end2end_real_chain_window_plan_20261027_r01`）：P1=task-27、W-E=B1–B10 均待开工信号。
5. 阶段5 G0/G1/G3/G4/G5 与实物验收仍未通过；`UR-1`（阶段4 回放扩展字段命名并入共享契约）仍待阶段4 确认。

## 证据与恢复入口

- 冻结文书/冻结集/清单：`report/evidence/S5-T04/s5_freeze_20261027_r05/`（README、`frozen_set.json`、`frozen_set_report.json`、`selftest_injection.json`、`results_freeze.json`、`delivery_manifest.json`、`console/**`）
- F6 自证：`report/evidence/S5-T04/s5_freeze_f6export_20261027_r01/`
- **被取代/失败证据（保留不改写）**：`…_r00_runner_crash`（套件摘要解析崩溃）、`…_r01`（导出未带 `.gitattributes` ⇒ 44 项换行所致哈希不符）、`…_r02_incomplete_builder_path`（构建器默认 `--out` 覆盖风险）、`…_r03`（校验器/F6 驱动器硬编码 r01 RunId ⇒ 会验错包）、`…_r04`（目录摘要被未跟踪的 `__pycache__`/构建产物污染 ⇒ 3 项不符）、`s5_freeze_f6export_20261027_r00_crlf_fail` 与 `…_r00b_tracked_dirs_fail`（F6 前两轮失败原始输出）
- 复跑：`python -B verification/verify_stage5_frozen_set.py --root . --frozen-set report/evidence/S5-T04/s5_freeze_20261027_r05/frozen_set.json` → 期望 `FROZEN_SET_VERIFIED` / exit 0；加 `--selftest tmp/5/S5-T04/selftest` → 期望 0/1/2。
- 恢复命令：`git -C D:/codex-worktrees/w5 rev-parse HEAD; git -C D:/codex-worktrees/w5 status --short; git -C D:/codex-worktrees/w5 tag --list "stage5-offline-freeze*"`

## 交接行（11 字段，2026-10-27 19:10 UTC+8）

任务=`S5-T04 阶段5 离线范围冻结（OFFLINE_SCOPE_FROZEN）：冻结集复核 + 冻结文书 + 本地 tag + 送独立复审` | 负责人=`DSH 阶段5 总控（2026-10-26 21:21 起正式认领）` | 工作树/分支=`D:\codex-worktrees\w5` / `stage5-display-prep` | 起始提交=`2a2d2cc01cd31444a1a854115d99a31cbe8499bf` | 允许修改范围=`verification/verify_stage5_frozen_set.py、verification/test_s5_display_geometry_reference.py（夹具修复）、scripts/stage5_t04/**、report/evidence/S5-T04/**、.gitattributes、.codex/STATE.md` | 未提交改动归属=`本轮全部为本卡产物，随冻结提交同批提交；失败/崩溃 RunId 保留不改写` | 让出声明=`本卡为**离线**冻结：未连接/未加载位流/未烧录/未占用 JTAG 串口；固定基线后停写被审对象，等待独立复审；板级项继续暂停` | 心跳(UTC+8)=`2026-10-27 19:10` | 证据入口=`report/evidence/S5-T04/**`、`verification/verify_stage5_frozen_set.py`、`docs/stage5/**` | 恢复命令=`python -B D:/codex-worktrees/w5/verification/verify_stage5_frozen_set.py --root D:/codex-worktrees/w5` | 状态/下一接手方=`FROZEN_FOR_REVIEW（离线范围已冻结并自证；待 DSH 项目总控派独立 Reviewer；此后按序：task-27 → 端到端真实链窗口 P1/W-E）/ 本阶段总控`