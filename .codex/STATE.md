# 阶段4 状态（摄像头推理 · 离线准备 + 4-A/4-B 起步）

更新：2026-10-22 19:45（UTC+8）。工作树 `D:\codex-worktrees\w4`／分支 `stage4-infer-prep`／起始 `8ee2530`（自 `main`）。规则见 `D:\FPGA_Competition\AGENTS.md`。
**本树只做阶段4 离线工作；不是阶段4 验收。** 板上注入（4-D）与真实摄像头验收必须等正式硬件授权与阶段3 交付。

## 目标与范围

- 本轮（CDX-20261022-010 §2/§3，总入口 015 r02）：**4-A** 更新并冻结本轮 G0 基线（对齐 2B 冻结回执、钉扎完整 SHA、UART 方案 B、三范围、候选上限边界口径）；**4-B** 交付与阶段5 共享的输入/结果契约 + 最小单帧注入通路（离线可验证）。
- 不做：板卡/JTAG/COM4/串口、Vivado/xsim、真实摄像头/HDMI；不改 w5/w6/dbdf/w2b/main；两个 mailbox 只读；不改 2B 接口正文。

## 本轮完成（离线，均可复跑）

| 任务 | 交付物 | 证据 RunId | 状态 |
|---|---|---|---|
| 4-A G0 r06 | `docs/stage4/S4A_*.md`、`s4a_*.json`、`scripts/stage4_s4a/*` | `report/evidence/S4-A/s4a_g0_20261022_r01/` | 自检 18/18 + 变异 9/9 + 官方 CHECKS_OK；**待独立审查** |
| 4-B 契约 | `docs/stage4/S4B_shared_input_result_contract.{md,json}`（`s4-shared-io/1.1.0` r02）、`scripts/stage4_s4ctrl/verify_shared_io_contract.py` | `report/evidence/S4-CTRL/S4-C02/s4_shared_io_20261022_r02/` | 自检 18/18；rev-spec 首轮 CHANGES_REQUIRED（T1–T4）已修；**复审待跑** |
| 4-B 注入通路 | `docs/stage4/S4B_stage4_address_map.json`、`docs/stage4/S4B_injection_path_runbook.md`、`vitis/stage4/s4_inject_frame{.h,.c}`、`s4_inject_frame_host.c`、`scripts/stage4_s4b/run_s4b_injection_offline.py`、`verification/test_s4_inject_frame.py` | `report/evidence/S4-B/s4b_injection_20261022_r01/` | gcc 0 error/0 warning；23 用例全符；2 小图 CRC 独立复现；地址图正/反例 PASS；unittest 8 OK；官方 CHECKS_OK；**待独立审查** |
| 跨方记录 | `report/evidence/S4-CTRL/S4-C03/**`（S4CTRL-20261022-003：G0 r06 + 共享契约对阶段5 的绑定变更） | 同左 | 待项目总控转达 |

- **4-A 关键事实**：2B 已于 2026-10-22 正式冻结并释放硬件（回执 `2687e87a…`、代码基线 `16ce2cdf…`、最终提交 `07c3d395…`、G4/G5 PASS、1000 连续任务 + 108 ACK 闭环）；当前硬件归属以现场会话为准（阶段5 板测）。`upstream_bindings` 24 条（23 文件全 MATCH + 109 分片目录聚合），覆盖 2A 文档/证据、`D:\FPGA_Data` 5 项外部资产、D2/D9/D6、2B 文档/C 参考/软件实现/平台/冻结回执。候选上限边界：12675 可行、12676 硬错误（`S2A_T62_INVALID_ARGUMENT`→CSR `BAD_ARGUMENT(1)`），禁用 4096，不与 ≤15 混同。
- **4-B 关键事实**：注入点必须在被验收预处理之前；注入下 `capture_time_available=false`、`capture_time_ns` 用 0 哨兵+注解、注入起点只记 `injection_start_ns`；显示语义用阶段5 G0 已决值 `B_latest_result_overlay`；HUD 13 字段；唯一映射键 `(session_id, frame_id, result_seq)`；stale 双基准共享阶段5 `STALE_AGE_LIMIT_NS`（阶段4 侧仍 DRAFT）。
- **本轮修掉的三处实现缺陷**（Lead 集成测试发现，已登记）：① host 缓存适配结构体为栈变量被环长期持有（悬垂指针）→ 改静态；② `capture_avail` 与契约 `capture_time_available` 语义反向 → 改互补映射；③ `token_present` 只匹配孤立 key 使 `capture=<ns>` 永远被忽略、伪造采集时间路径不可测 → 改用 `token_value`。

## 上游冻结绑定（只读）

- 2A G0 `7c2c8684…`、manifest `9dd2477b…`、109 样本 `ccf741c1…`、T25 索引 `cbda3f25…` + 分片恢复清单 `5352b2ef…`（109 个/390,700,998 B）、T29 `24361a13…`、D2 `6a3453d5…`、D9 `94dacdac…`、D6 `4dcf0f7d…`；2A 外部资产 cfg `5475dff0…`/weights `3984affa…`/gf8 `f6feb6d4…`/calibration `d637a2fe…`/manifest.csv `fd60e7a6…`（现场可读、全部 MATCH）。
- 2B：物理接口 `c5559f64…`、UART 正文 `b305c84c…`、C 参考 `.c` `cf1904da…`/`.h` `edd61d7f…`、transport.py `7dda231e…`、`s2b_inference_app.c` `9ed222a1…`、`build_s2b_inference.py` `ffa81cba…`、平台 JSON `6f69e6ad…`、冻结回执 `2687e87a…`。
- 阶段5 G0 字段 `8eac7007…`（只读引用；其 S4-A 绑定仍为 r05，已通过 S4CTRL-003 请求阶段5 改绑 r06）。

## 未决与风险

- **独立审查未完成（环境限制）**：本轮多个 Reviewer 子代理连续 provider 失败（rev-spec/rev-c/dev-inject 多次 exit 异常），4-A r06、共享契约 r02、4-B 注入通路**尚未取得独立审查 PASS**；Lead 只做了自检、变异自证与官方清单核验，**不得据此宣称 G2 通过**。恢复后需补审（rev-spec 审契约/4-A，rev-b 审 4-B）。
- 契约与地址图为 `DRAFT_PENDING_REVIEW`；`stale_limit_ns` 仍 `DRAFT_PENDING_APPROVAL`（草案 200 ms），需正式 G0 或 Wong 批准；批准载体建议阶段5 `STALE_AGE_LIMIT_NS` 唯一。
- 4-D 板测需正式实物授权与会话交接；阶段5 正在板测，硬件不归本树。
- 注入/合成结果不得替代摄像头 G5；灰度输入不得对彩色 golden。

## 硬件与资源边界

- 全程未访问/未重启 `hw_server`、JTAG、COM4、串口；未启动 Vivado/xsim/综合；只用轻量 Python + `d:\mingw64\bin\gcc.exe`；未写只读树。

## 证据入口与下一步

- 证据：`report/evidence/S4-A/s4a_g0_20261022_r01/`、`report/evidence/S4-B/s4b_injection_20261022_r01/`、`report/evidence/S4-CTRL/S4-C02|S4-C03/`；历史：`S4-A/s4a_draft_*_r05`、`S4-B/20261021_r13`、`S4-C`、`S4-D`。
- 下一步：① 补独立审查（4-A r06、契约 r02、4-B）→ 关闭阻断后由 Lead 提交；② 阶段5 改绑 S4-A r06 并按契约消费；③ 取得硬件授权后做 4-D 单帧注入板测、再 109/1000 与摄像头回归。

## 交接行（11 字段，2026-10-22 19:45）

任务=`S4-CTRL 阶段4 起步 4-A（G0 r06 冻结）+ 4-B（共享契约 + 单帧注入通路，离线）` | 负责人=`DSH 阶段4 总控` | 工作树/分支=`D:\codex-worktrees\w4` / `stage4-infer-prep` | 起始提交=`8ee2530` | 允许修改范围=`本树全部（docs/、verification/、scripts/、vitis/、report/evidence/**、tmp/4/**、.codex/STATE.md）；主树/w2b/w5/w6/dbdf/96a3/厂商原件只读` | 未提交改动归属=`本树本轮改动全部由本总控持有；主树/w2b/w5 脏改动非本树，未触碰` | 让出声明=`未让出：本树写权由本窗口独占；不接管其他阶段工作树、不争用硬件` | 心跳(UTC+8)=`2026-10-22 19:45` | 证据入口=`report/evidence/S4-A/s4a_g0_20261022_r01/`、`report/evidence/S4-B/s4b_injection_20261022_r01/`、`report/evidence/S4-CTRL/S4-C02|S4-C03/` | 恢复命令=`git -C D:/codex-worktrees/w4 status --short; git -C D:/codex-worktrees/w4 rev-parse --short HEAD; git -C D:/codex-worktrees/w4 rev-parse --git-path index.lock` | 状态/下一接手方=`IN_PROGRESS（离线交付完成，待独立审查后提交；4-D 板测需正式硬件授权）/ 本阶段4 总控`