# SUPERSEDED：本 RunId 不是最终证据

- 状态：被取代（保留，不删除；按“RunId 不覆盖、失败与中间证据独立保留”规则留痕）。
- 取代原因：**清单文案与实际运行不一致**——本 RunId（以及冻结版清单生成器在被修正前产出的清单）
  的 `unittest_s4_ps_decode` check reason 写作「26 个测试全部通过」，而冻结版
  `verification/test_s4_ps_decode.py`（sha256 `af342704432fb1c2000cc1251eff0d4f3f4a7a5e320fa1a0e647bcd86b5266d6`）
  实跑为 **27 tests OK**。属低报（非夸大）的事实性文案错误。
- 源码字节未变：`vitis/stage4/**`、`scripts/stage4_s4b/**`、`verification/test_s4_ps_decode.py`
  在 r12 之后均未被修改（哈希与冻结集一致）。
- 最终证据：`report/evidence/S4-B/20261021_r13/`（同一冻结源码复跑，清单文案已与实际运行一致，
  且 `delivery_manifest.json` 通过 `verification/check_stage_delivery.py --mode evidence`）。
- 取证方式：本目录原有文件未做任何内容改写（`delivery_manifest.json` 的文案修正已在最终 RunId 中体现）；
  本说明是唯一新增文件，其哈希已列入本目录 `delivery_manifest.json` 的 `files`。2026-10-21（UTC+8）。