# SUPERSEDED：本 RunId 不是最终证据

- 状态：被取代（该轮离线链为 PASS）（保留，不删除；按“RunId 不覆盖、失败与中间证据独立保留”规则留痕）。
- 取代原因：
  1. **脚本演进**：本 RunId 的 `offline_chain_summary.json` 由当时版本的
     `scripts/stage4_s4b/run_s4b_offline_chain.py` 产出，检查项与语义对齐判据少于冻结版
     （冻结版新增 F1 计算式语义对齐门闸、F4 `measurement_scope` 唯一位置等）。
  2. **契约修订**：本 RunId 运行期绑定的 S4-A 契约哈希见其 `offline_chain_summary.json`
     的 `contract.sha256`；S4-A 之后由 r04 升到 r05（candidate 口径与硬错误语义、
     `evidence_annotation.measurement_scope` 定义），契约对齐结论须以绑定 r05 的最终 RunId 为准。
- 本 RunId 具体事实：93 项检查 PASS、0 SKIP、运行期绑定 S4-A r05 契约；但产出于 F1–F6 整改之前的脚本版本，其语义对齐项部分为手写常量而非计算式判定。
- 最终证据：`report/evidence/S4-B/20261021_r12/`（冻结版源码产出，绑定全部源码 SHA-256，且 `delivery_manifest.json`
  通过 `verification/check_stage_delivery.py --mode evidence`）。
- 取证方式：本目录原有文件未做任何内容改写；本说明是唯一新增文件，其哈希已列入本目录
  `delivery_manifest.json` 的 `files`。
