# S5-T04 阶段5 **离线范围冻结**（`OFFLINE_SCOPE_FROZEN`）——冻结文书

> 冻结标识：`S5T04-OFFLINE-SCOPE-FROZEN-20261027-R01`｜RunId：`s5_freeze_20261027_r01`｜生成：2026-10-27T18:32:41+08:00
> 冻结前基线提交（构建冻结集时的 HEAD）：`5fcbe9eaf6c4fc949d98c761536cc1c3f6d34d5c`；本轮内容提交见 §6。
> 本冻结**只覆盖离线字节集**：不主张 G0/G1/G3/G4/G5，不主张任何板级/实物/实时结论。
> 本卡不需要板卡（Wong 2026-10-27 确认）；本轮未连接、未加载位流、未烧录、未占用 JTAG/串口。

## 1. 冻结范围（只此四类）
1. **离线契约/规格**：`docs/stage5/**` 中列出的显示契约 JSON、输入绑定 JSON、离线参数/用例骨架、JSON 契约、UR-3 决策（stale=200 ms 批准引用）。
2. **离线实现**：`verification/s5_display_geometry_reference.py`、`scripts/stage5_t03/**`（渲染/回放/长跑/多几何/HUD 遮挡/JSON 契约/阶段4 冻结包消费）、`scripts/stage5_s5a|s5b|s5c/**`。
3. **离线证据包**：见 `frozen_set.json` 的 `offline_evidence_replay_display` 与 `offline_evidence_s5t02` 组（`s5t03_offline_replay_display_20261026_r06`、`…offline_long_run_replay…r04`、`…multi_geometry_render…r02`、`…json_contract…r04`、`…hud_occlusion…r02`、`…stage4_frozen_replay…r04`、`…stage4_positive_replay…r01`、`S5-T01/s5t02_offline_dynamic_map_20261027_r02`）。
4. **宿主侧只读引用**（`scope=host`）：阶段3 参考帧 `939fce22…` 与回放绑定、阶段4 回放结果包冻结记录/索引/带框包、Wong 批准的 `stale=200 ms` 回执、阶段3/阶段4 局限引用文件。

成员总数与分组计数（现场生成）：
```json
{
  "frozen_set_id": "S5T04-OFFLINE-SCOPE-FROZEN-20261027-R01",
  "baseline_commit": "5fcbe9eaf6c4fc949d98c761536cc1c3f6d34d5c",
  "generated_utc8": "2026-10-27T18:32:41+08:00",
  "members": 76,
  "by_group": {
    "contracts_and_specs": 13,
    "offline_implementation": 3,
    "offline_evidence_replay_display": 44,
    "offline_evidence_s5t02": 7,
    "host_upstream_references": 9
  }
}
```

## 2. 明确不主张（逐条写死）
1. **真实回放接入**（板上/实时）：不主张。阶段4 回放结果包已冻结（`replay_only`）且本树有**离线**消费证据，但 `task-27` 整体 **NOT_RUN**。
2. **板上动态映射/绘制**：不主张（S5-T02 板级 §4.5/§7.3 未关闭）。
3. **摄像头真实采集**：不主张。
4. **真实集成 30 分钟**：不主张（仅有离线虚拟长跑）。
5. **T5-10 板上回归**：不主张。
6. **HUD 屏上视觉确认**：不主张（仅有离线栅格化遮挡量化）。
7. **任何 G0/G1/G3/G4/G5 通过**：不主张。
8. **真实采集质量/颜色与端到端延迟实测**：不主张（`capture_clock=PENDING_MEASUREMENT`）。
9. **上游关口的替代判定**：不主张；上游自述局限按其原文继承（§3）。

## 3. 继承的上游局限（引用不改写）
- 阶段3：VDMA 首帧 bit11 `PARTIAL_OPEN`、task-11 `BLOCKED_NOT_RUN`、`TIMING-17`/I-O delay 未签核 （引用 `D:/codex-worktrees/dbdf/report/evidence/S3-T17/stage3_closeout_20261026_r01/manifest.json`）。
- 阶段4：`complete_stage4_or_RGB_preprocess=NOT_CLAIMED`（引用 `D:/codex-worktrees/w4/docs/stage4/s4_stage4_freeze_supplement_hardware_20261027_r01.md`）。
- 以上只引用，不重解释、不替代其所有者判定。

## 4. 冻结集校验器与真实退出码
| 步骤 | 命令 | 退出码 | 结论 |
|---|---|---|---|
| 冻结集生成 | `python -B scripts/stage5_t04/build_stage5_frozen_set.py` | 0 | 76 个成员，`frozen_set.json` sha256 `7d593bb6289d991e8348100ec7916e500bcac1c56d5be5964724991c4332b1e1` |
| 冻结集校验 | `python -B verification/verify_stage5_frozen_set.py` | **0** | `FROZEN_SET_VERIFIED`（一致 76 / 不一致 0 / 环境错误 0） |
| 注入自测（必须失败） | `python -B verification/verify_stage5_frozen_set.py --selftest <tmp>` | **0** | `SELFTEST_PASS`：clean=0（期望 0）、篡改一字节=1（期望 1）、删一件=2（期望 2） |
| 离线套件（回归） | `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B -m unittest scripts.stage5_t03.test_s5t03_frozen_replay scripts.stage5_t03.test_s5t03_hud_occlusion scripts.stage5_t03.test_s5t03_json_contract scripts.stage5_t03.test_s5t03_json_contract_malformed scripts.stage5_t03.test_s5t03_long_run_replay scripts.stage5_t03.test_s5t03_multi_geometry_render scripts.stage5_t03.test_s5t03_replay_display scripts.stage5_t03.test_s5t03_skeleton scripts.stage5_t03.test_s5t03_stage4_positive_replay verification.test_s5_display_geometry_reference` | 0 | Ran 142 / failures 0 / errors 0 / skipped 2 |
| 历史模块探测（**非门禁**） | `python -B -m unittest scripts.stage5_s5b.test_s5b_overlay scripts.stage5_s5c.test_s5c_regression` | 1 | Ran 83 / failures 18 / errors 0 —— **已知缺口**（w4 侧黄金数据漂移），不计入本冻结回归主张，见 §8 |
| 安静窗口 | `tasklist` 过滤 `vivado.exe, xsdb, hw_server, vitis, xsim` | 0 | QUIET（桥接进程 2 个，已按 DSH-20261027-017 区分） |
| 工作树已跟踪改动 | `git status --short --untracked-files=no` | 0 | CLEAN；index.lock ABSENT |

> 包装检查器（`check_stage_delivery --mode evidence`，M1/M2）的真实退出码见 `console/check_evidence_mode_output.txt` 与 `results_freeze.json`；`CHECKS_OK` 只代表清单/绑定检查通过。

## 5. 从零复跑（恢复入口）
```bash
git -C D:/codex-worktrees/w5 log --oneline -3; git -C D:/codex-worktrees/w5 status --short
python -B D:/codex-worktrees/w5/verification/verify_stage5_frozen_set.py --root D:/codex-worktrees/w5
python -B D:/codex-worktrees/w5/verification/verify_stage5_frozen_set.py --selftest tmp/5/S5-T04/frozen_selftest
python -B D:/codex-worktrees/w5/scripts/stage5_t04/build_stage5_frozen_set.py --out <out.json>   # 可复现同一冻结集
python -B D:/codex-worktrees/w5/scripts/stage5_t04/run_stage5_freeze_evidence.py --run-dir report/evidence/S5-T04/<新RunId> --source-commit <提交>
python -B -m unittest scripts.stage5_t03.test_s5t03_frozen_replay scripts.stage5_t03.test_s5t03_hud_occlusion scripts.stage5_t03.test_s5t03_json_contract scripts.stage5_t03.test_s5t03_json_contract_malformed scripts.stage5_t03.test_s5t03_long_run_replay scripts.stage5_t03.test_s5t03_multi_geometry_render scripts.stage5_t03.test_s5t03_replay_display scripts.stage5_t03.test_s5t03_skeleton scripts.stage5_t03.test_s5t03_stage4_positive_replay verification.test_s5_display_geometry_reference
python -B D:/FPGA_Competition/verification/check_stage_delivery.py --mode evidence --project-root D:/codex-worktrees/w5 --manifest report/evidence/S5-T04/<RunId>/delivery_manifest.json
```
- 离线回归的可视/数值入口（示例）：`python -B scripts/stage5_t03/s5t03_replay_display.py --out report/evidence/S5-T03/<新RunId> --mode mixed --frames 240 --keyframe-max 24 --stage3-binding <binding> --demo-mp4`。
- 在**离开本机**的副本中，`scope=host` 引用可用 `--skip-host-references` 跳过（跳过项会逐条打印，不得当作已验证）。

## 6. 提交与 F6 自证
- 冻结前基线（`frozen_set.json.baseline_commit`）：`5fcbe9eaf6c4fc949d98c761536cc1c3f6d34d5c`。
- 本轮内容提交与最终 HEAD：见外部报告（本文件不写自身提交哈希，避免自指）；`git log -1` 为权威。
- **F6 自证**：本轮内容提交单独 `git archive` 导出后，在导出副本内复跑冻结集校验器与 `check_stage_delivery`，原始输出与真实退出码见 `report/evidence/S5-T04/s5_freeze_f6export_20261027_r01/`。
- 本地附注 tag：`stage5-offline-freeze-20261027`（**不 push**）。

## 7. 限制
- **离线范围冻结**：本包只冻结**离线**契约/实现/证据字节并证明其可复现，不代表 G0/G1/G3/G4/G5 或任何板级/实物验收。
- **不主张真实回放接入**：阶段4 回放结果包（`s4t27_replay_package_freeze_20261027_r01`，`replay_only`）与本树离线消费已存在，但 `task-27`（回放/彩色输入路径实现 + 用回放结果包做离线动态回归）整体仍 **NOT_RUN**；板上/实时回放不主张。
- **不主张板级项**：板上动态映射/绘制、摄像头真实采集、真实集成 30 分钟、T5-10 板上回归、HUD 屏上视觉确认、真彩目视一律 NOT_RUN。
- **继承上游局限（引用不改写）**：阶段3 VDMA 首帧 bit11 `PARTIAL_OPEN`、task-11 `BLOCKED_NOT_RUN`、`TIMING-17`/I-O delay 未签核；阶段4 `complete_stage4_or_RGB_preprocess=NOT_CLAIMED`。
- **宿主侧引用**：阶段3 帧/绑定与阶段4 冻结包记录、Wong 批准回执为仓库外只读引用；本包只按哈希引用其字节，不改写、不复制其所有权。
- 冻结集只覆盖 `frozen_set.json` 列出的成员；冻结文书自身（README/manifest/console）不在被冻结成员内（由 Git 提交与清单绑定）。
- **已知缺口（未闭合）**：`scripts/stage5_s5a|s5b|s5c`（S5-A/B/C 历史离线准备）测试因 w4 侧黄金数据漂移而失败，不纳入冻结集、不计入本冻结的离线回归主张；原始输出见 `console/legacy_suite_known_gap.txt`。
- `CHECKS_OK` 仅表示清单/文件绑定/目录检查通过，不代表接口语义正确、测试充分、独立审查通过或任何关口通过。

## 8. 未闭合项与未做项（NOT_RUN，如实）
1. **历史模块已知缺口**：`scripts/stage5_s5a|s5b|s5c`（S5-A/B/C 历史离线准备）探测 1，Ran 83 / failures 18 / errors 0；根因＝其测试依赖 w4 侧黄金数据（`s4c_replay_20261021_r05`、`S4-B/20261021_r13`）上游漂移，**不属于本卡定义的离线 replay/display 路径**；原始输出见 `console/legacy_suite_known_gap.txt`。本冻结**不冒称**这些历史模块回归通过；其历史结论仍按各自 RunId 自证。
2. **`task-27`（回放/彩色输入路径实现 + 用阶段4 冻结回放包做离线动态显示回归）未按卡交付**：阶段4 回放结果包已冻结（`replay_only`）且本树有离线消费证据，但该卡整体 NOT_RUN。
3. **板级 B1–B10 全项**：已随 Wong 拔板暂停；重连后需先过第 0 步（占用/部署身份/运行期回读地址/真彩目视需 Wong 在场）。
4. **端到端真实链窗口**（`end2end_real_chain_window_plan_20261027_r01`）中的 P1=task-27、W-E=B1–B10 均未开工（等待信号）。
5. **阶段5 G0/G1/G3/G4/G5 与实物验收仍未通过**。
