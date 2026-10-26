# JSON 契约 v1.0.2 校验证据 RunId `s5t03_json_contract_20261026_r03`

> 数字口径：本摘要逐项取自本包 `manifest.json` / `console/`（机器可读权威）；冲突以 JSON/日志为准。
> 本包为**元/过程包**（校验器输出）：**不适用**该契约本身（无 `results.json` 与产物 schema）。

- 被测代码提交（本包 `source_commit`）：`5e5e20423a95…`
- 契约版本：**1.0.2**；契约文件 `docs/stage5/s5t03_json_contract_v1.json`（SHA 见 manifest.contract）
- 本包独立套件日志：`Ran 112 tests` / OK（SHA `2807110da5ac…`）

## 1. 正向校验（exit 0，含**事件日志键位核对**）
```
OK   s5t03_offline_replay_display_20261026_r06        kind=replay_display frames=240 errors=[]
OK   s5t03_offline_long_run_replay_20261026_r04       kind=long_run_replay frames=106573 errors=[]
OK   s5t03_multi_geometry_render_20261026_r02         kind=multi_geometry_render frames=None errors=[]
contract=gestureforge_s5t03_json_contract v1.0.2 packages=3 failed=0
```
三最终包在新增的事件日志键位核对下仍全部通过 ⇒ 契约声明的 compact 键位与实物一致。

## 2. 本轮关闭的 2 项阻断（复审 BL-1 / BL-2）
| 项 | 问题 | 处置 | 实测 |
|---|---|---|---|
| **BL-1** | 契约 `event_log_fields` 的键位清单**与实物不符**（我此前把 frame_assertions 字段名误当事件日志键） | 改为实物 compact 键：submit `t,fid,sid,seq,oc,vf,rr,ri,rd,rb,pri`；commit `t,dfid,ts,rfid,sid,seq,st,dr,bx,za,se,w`（图例指向 params `log_artifacts.compact_fields_*`）；**校验器新增键位核对**（读 `logs/events_*.jsonl(.gz)` 首条记录逐字比对） | 键位改错 → **exit 1**；实物三包 → exit 0 |
| **BL-2** | 契约是"合法 JSON 但非对象"时崩成 **exit 1** | `load_contract` 首行加类型守卫；`artifact_kinds`/`stability`/`event_log_fields` 改 `.get()`+类型校验 ⇒ 环境错误统一 **exit 2** | 契约 = `[1,2,3]`/`"abc"`/`42`/`null`/`false`/`3.5` → **exit 2**；自声明短 required 列表、删 stability 并同步移除 required → **exit 2** |

## 3. 附带修复（非阻断观察）
- **O-1**：`manifest.json` 豁免改为**仅包根**；子目录同名多余文件（如 `keyframes/manifest.json`）→ **exit 1**（新增用例 `test_07`）。
- **O-3**：契约新增 `frame_assertion_required_vs_stable` 说明两清单当前逐字相同及校验行为（避免"查两遍实为一遍"的误读）。
- **O-7**：JSON 侧补注"`stream.frame_period_ns` 是**离线虚拟步长**，≠ 阶段4 实测帧周期 P，T6-A03 仍 NOT_RUN"，并登记 `t_effective/window_complete` 语义尚未入契约。

## 4. 判别力（负向，均在临时契约/临时副本上，未改动证据）
- 畸形契约 6 类（非对象）→ 全 exit 2；短 required 列表 / 缺 `artifact_kinds` / 删 `stability` → exit 2；
- 键位改错 → exit 1；子目录多余 `manifest.json` → exit 1；`schema_version` 值错 → exit 1；哈希漂移 → exit 1；`passed=false` → exit 1。

## 5. 边界
- 只证明**结构契约、文件哈希与事件日志键位**；不代表接口语义正确、测试成功、独立审查通过或 G0/G2/G4/G5；
- **真实回放接入 / 板上 / 摄像头 = NOT_RUN**；**不接板卡**、不联网；PNG/MP4 非验收依据；**G0/G1/G3/G4/G5 均未通过**；
- 前序 `…_r01`（契约 v1.0.0 + 旧校验器）、`…_r02`（v1.0.1）保留不删，已被本包取代。
