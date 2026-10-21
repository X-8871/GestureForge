# SUPERSEDED：本 RunId 不是最终证据

- 状态：被取代（保留，不删除；按“RunId 不覆盖、失败与中间证据独立保留”规则留痕）。
- 本 RunId 事实：候选双口径实现后的运行：status=FAIL（77 PASS / 3 FAIL，其中 s4a_field_names 因当时契约新增字段尚未实现而失败）；契约读取值 1d7fd5f0…。
- 取代原因：产出于早期脚本/契约版本（检查项与判据少于冻结版），且契约此后由 r04 升到 r05；
  契约对齐与对拍结论须以绑定 r05 的最终 RunId 为准。
- 说明：本 RunId 早于 `delivery_manifest.json` 制度，目录内没有清单文件；其 `offline_chain_summary.json`
  为当时真实运行记录，未做任何内容改写。
- 最终证据：`report/evidence/S4-B/20261021_r13/`（冻结版源码产出，绑定 9 项源码 SHA-256，`delivery_manifest.json` 通过
  `verification/check_stage_delivery.py --mode evidence`）。
- 取证方式：本说明是唯一新增文件；本目录内无清单可供更新，故未产生清单哈希变更。2026-10-21（UTC+8）。
