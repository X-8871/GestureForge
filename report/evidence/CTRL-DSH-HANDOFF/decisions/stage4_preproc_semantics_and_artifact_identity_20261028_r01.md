# 裁决：预处理语义 D2 权威 + 冻结产物按 SHA 引用（2026-10-28）

- 编号：`stage4_preproc_semantics_and_artifact_identity_20261028_r01`
- 时间：2026-10-28 21:15（UTC+8）；签发：DSH 项目总控；依据：chain-lite-A/B 板上结果与逐字节对拍。
- 适用范围：阶段4 预处理语义与冻结产物身份口径；不改变任何验收判据。

## 1. 裁决①：PS/SW 预处理语义以**冻结 D2** 为准

- **D2 口径**（唯一有效）：Darknet letterbox（`offset=(dst-new)//2`）+ **端点对齐双线性** + `v/255` + **对称量化 `scale=1/127`、zero-point=0**、半数远离零、饱和 [-127,127] + **pad `0.5` → int8 `64`** + **CHW** 布局。
- **作废口径**：`vitis/stage4/ps/s4d_geometry.h` 原描述的"**最近邻缩放 + `int8(v-128)` + pad=0**"——仅作历史记录，已标注 `LEGACY_4B_SUPERSEDED_BY_D2`；**该文件的几何参数表（`new_w=416/new_h=312/pad_l=0/pad_t=52` 与 `src_x=(x*20)/13` 等）仍然有效**。
- **可核事实（裁决依据）**：
  1. 主机 gcc 编译**与 PS 同一份** `s4d_sw_preproc.c`，输入 T25 源图解码 raw，输出与冻结张量 `bridge_input_postquant_int8_chw.bin`（`da26d385…`，519,168 B）**逐字节一致、SHA 相同、diff=0**（`report/evidence/S4-T34/sw_preproc_pairing_20261028_r01/`，`BYTE_EXACT_MATCH`）；
  2. 只有 D2 路径能复现该冻结张量；旧口径产出必然不同。
- **执行**：只改文档/注释与声明，**不改实现**；D2 路径即 `s4d_sw_preproc.{h,c}` 当前实现。

## 2. 裁决②：冻结/交付产物**按登记 SHA 引用**，不要求"可重建出同一 SHA"

- 阶段4 各 ELF 的生效身份 = **登记 SHA**（`app_elf_registration_r*.json`）；
- 源码演进（`-g3` 调试信息随行号变化、新增 CHAIN/CHAINB 分支等）导致"当前源码重建 SHA ≠ 历史 SHA"属**预期漂移**，**不作为失败**；
- 但**源码快照必须可追溯**：每个 ELF 的源码 SHA 与构建命令须在登记文件中可查（r3/r4/r5 已登记 `version_mapping_and_rebuild_drift`）；
- 新产物一律"新 SHA + 新登记"，**不覆盖旧文件、不复用旧 SHA**。

## 3. 本裁决所依据的板上结果（仅 2B 平台位流适用）

| 项 | 结果 | 证据 |
|---|---|---|
| chain-lite-A（注入冻结张量 → PL 网络 → PS 解码 → UART） | **PASS**：`DONE_SAFE`、`elapsed 11,821 ms`、`count=1/raw=2`，8 字段与 r13 参考 **abs diff 全 0.0** | `bringup_chainlite_a_20261028_r03/` |
| chain-lite-B（RAW 帧 → **PS/SW 预处理** → PL 网络 → PS 解码 → UART） | **PASS**：板上张量 `CRC-32 0x5B183B50` == 离线同 C 同 RAW；框 8 字段 **abs diff 全 0.0**（`max_abs_diff=0.0`） | `bringup_chainlite_b_20261028_r01/` |
| 候选区恢复 | 每次窗口 W0/W4 **diff=0**（基线 `41907f53…`） | 各窗口 `restore_diff` |

- fixture RAW 标 **`FIXTURE_GENERATED（非摄像头实拍）`**（cv2 `INTER_AREA` 640×480，生成命令与 SHA 在 `fixture_manifest.json`）；
- 上述"预处理"是 **PS 软件实现**，**不是 PL 预处理**（PL v2 属后续任务）。

## 4. 明确未主张

- 不主张 **G3/G4/G5**、不主张阶段4 验收通过；
- 结论仅覆盖 **2B 平台位流 `555a70c2…`**，不覆盖未来 4-D 自建位流；
- `M3=FAIL/未闭合`（`REGION_CHANGED` 未解释；单窗口内装 PL/执行 init 不改候选区已由 S1 证明）；`M2` 仍待重审；
- `ENABLE=1` 未解锁；未 push。