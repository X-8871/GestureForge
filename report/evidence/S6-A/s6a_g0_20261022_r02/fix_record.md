# S6-A 修订记录（v1.1 / r02）

- 任务：`S6-A`（阶段6 G0 包 + 交互行为表）
- 修订输入：独立评审 `S6A_20261022_r01`（结论 `CHANGES_REQUIRED`，B-01..B-05 阻断 + N-01..N-10）
- 被审基线：w6 提交 `1fe4648`
- 修订证据：`report/evidence/S6-A/s6a_g0_20261022_r02/`；r01 目录原样保留、未覆盖
- 阈值纪律：**24 项参数值未改，全部仍为 `PENDING_APPROVAL`**；未在测试集上调参
- 状态：**PENDING_REVIEW**（复评由项目总控另派；本记录不构成“已审查/已通过”）

## 1. 阻断项

| 项 | 处置 | 主要落点 |
|---|---|---|
| B-01 证据清单缺失/命令不可复现 | 新增可复现构建器 `verification/s6a_build_evidence.py`：真实生成 `delivery_manifest.json`、`inputs_manifest.json`、`hashes_sha256.txt`；`hashes` 只哈希实际存在文件；用绝对 `--project-root` 实跑 selfcheck 与 `check_stage_delivery.py` inputs/evidence 两种模式，退出码由构建器实测写入 `manifest.checks`（不硬编码） | 本目录清单 + `S6A_run_summary.md` |
| B-02 `NO_HAND` 计数矛盾 | H-4 拆为「窗口序列推进」与「匹配计数」；`NO_HAND` 不推进匹配计数、零框不得完成稳定窗口；同步 JSON/§9/§11.1/B17；自检 C15 断言 | 文档 §2/§9/§11.1；JSON H-4 |
| B-03 冷却缺全局门 | 新增 H-10：`t_submit+T6-K01` 内任意状态/任意获取不得提交动作；M5 增加全局门；新增 JSON `cooldown_policy`；B13/B14/§10 同步；自检 C13 | 文档 §10；JSON H-10/M5 |
| B-04 `W` 定义矛盾 | 窗口完成时刻 = 第 N 个 `WINDOW_MATCH` 结果到达时刻；`W_min` 仅下界、不进延迟统计；交互延迟 = `t_effective − window_complete`；无实测 P 记 NOT_RUN（U6-13）；自检 C14 | 文档 §9/§15；JSON `low_fps_latency` |
| B-05 “匹配”两套定义 | 拆 `TARGET_CONTINUES`（保持/迟滞）与 `WINDOW_MATCH`（窗口计数），全表引用；禁用含糊“匹配”；自检 C12 | 文档 §3/§8/§9；JSON `predicates` |

## 2. 非阻断项

N-01（M14 删除、§14 `T6-S03`、§3 `E_FRAME_CONFLICT`、`A_DISPLAY_STATE` 删除）、N-02（M4/M7 可达性登记 + U6-12）、N-03（§12.1 缺口、U00 滑动窗口）、N-04（HC-16/17/20 真算 + HC-21..27）、N-05（实测 P/`T6-A03` NOT_RUN + U6-13）、N-06（逐类 UX + U6-14）、N-07（B16/B19/B23 依据）、N-08（旧包失败输出）、N-09（±1 单位口径 + HC-27）、N-10（措辞改 `DELIVERED_PENDING_APPROVAL`）。

## 3. 对评审两条“文档缺项”的更正（如实记录）

- **H-5**：r01 文档第 41 行已存在且与 JSON 语义一致。评审脚本正则要求加粗标题后紧跟 `：`，而该行用逗号 → 漏检。r02 统一格式，C3 改为 ID 集合比对。
- **M2/M10**：r01 文档 §4 表第 66/74 行已存在。评审脚本要求来源状态写在反引号中，而两行来源为“任意” → 漏检。r02 把来源写作 `` `*`（…） ``，C3 对全部迁移比对 from/to。

以上两项属**机器可解析性缺陷**，不是内容缺失；加固后的自检在旧包上仍会因这些格式差异与 S03/`E_FRAME_CONFLICT` 缺失而失败（见 `selfcheck_old_package_failure.json`）。

## 4. 复现命令

见 `fix_record.json` 的 `verification_commands` 与 `S6A_run_summary.md`（含真实退出码）。
