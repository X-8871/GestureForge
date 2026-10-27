# S4D 4-D 离线构建 · Phase 1 三栏盘点与设计冻结（2026-10-27 r01）

- 任务：**S4-T32**（`S4-T32` 4-D 离线构建；**全离线**，不含板级）。工作树 `D:\codex-worktrees\w4`（`stage4-infer-prep`）。
- 状态：**Phase 1 交付（G0 盘点 + 设计冻结 + 构建计划）**；Phase 2 重型构建**未开始**，等待项目总控确认。
- 边界：未接触板卡（不启 `hw_server`/`xsdb`、不装载、不烧录）；`ENABLE=0`；未 FROZEN；不 push；不改 w2b/dbdf/w5/w6/主目录；25 项遗留未提交改动未动。
- 依据：D1=A 裁决（`raw_frame [0x12000000,0x12C00000)`、`raw_meta [0x12C00000,0x12C08000)`、禁区 `[0x12C08000,0x20000000)`）；ADR `S4B_pl_preprocess_g0_readiness.md` §8（接口 G0 草案）；地址图 `7c20ac89…`（APPROVED，`ENABLE=0`）；契约 r07 `25bc30d5…`。
- **本文件不构成任何关口通过**：它只冻结"要建什么、建在哪、怎么验"，不等于 G0 审查通过，也不等于 G3/G4/G5。

## 1. 三栏盘点（只读核验结果）

### 1.1 PL 侧（2B 平台 + 4-D 增量）

| 已有 | 缺失 | 需改 |
|---|---|---|
| 2B 冻结平台：bitstream `555a70c2…`、XSA `ea52da1b…`（w2b 冻结树 `07c3d39`）；`s2b_inference_top`（`module_ref`，`infer_M_AXI` **64 位** master → `ps7 S_AXI_HP0`，AXI3、6 位 ID）；`ps7_M_AXI_GP0` AXI3 32 位 → `axi_protocol_converter` → AXI4-Lite，CSR 窗口 `0x43C00000..0x43C10000`（64 KiB）；FCLK0 **50 MHz** 由 PS 提供（无 MMCM）；INT8 计算 RTL 块（conv/mac/maxpool/route/geometry，w2b `src/`） | **`s4b_preproc_frame` 未实例化**（BGR→RGB + 几何 + 打包）；**AXI4-Lite 新块 `0x200..0x27c` 未实现**；**generic word master 未实例化**；**4-D 位流/ XSA 未构建**；`s2b_inference.hwh` 只有旧 CSR + HP0 通路 | wrapper router 需在保留旧 CSR 行为（`0x008` START/ABORT/ACK、`0x00c` STATUS）前提下挂新块；BD 需加新块与地址分配；位流必须**重新综合/实现**（不能复用 `555a70c2`） |

**时序历史事实（必须带进风险）**：2B 同族 S10/S11 post-route 均为 **50 MHz 未收敛**（S10 WNS −4.405 ns、S11 WNS −3.201 ns）。4-D 增量只会更紧（新块 + 更长组合路径），**不得**假设 50 MHz 会自然闭合。

### 1.2 阶段3 视频接口（只读引用）

| 已有 | 缺失 | 需改 |
|---|---|---|
| `dbdf` 树阶段3 成果：历史三 framebuffer `[0x00114C00,0x003B7C00)`、`[0x00703800,0x009A6800)`、`[0x00CF2400,0x00F95400)`（与候选区不重叠）；参考帧集与 JTAG/COM4 使用记录 | 4-D **不走视频 DMA**：首轮用 host/JTAG RAW 注入 + 冻结 109 样本（ADR §8.2/§8.7 已定"不合并阶段3视频 XSA"），因此不需要摄像头→DDR 的 DMA 链 | 无（本卡不改 dbdf；不合并视频 XSA） |

### 1.3 阶段4 PS 侧（推理/解码/NMS）

| 已有 | 缺失 | 需改 |
|---|---|---|
| r13 板级诊断 ELF `bfe88660…`（432,788 B）与 map `4a0f9cf8…`；`ps_app_arena [0x00100000,0x01100000)`；tensor arena `[0x10000000,0x12000000)`；`s2a_ps_decode_nms_reference.c`（解码/NMS 参考）；`s4b_ps_trace.c`（trace）；`s4_uart_meta_pack()`/`s4_uart_box_pack()` 固定 40 B/48 B 布局 | **RAW task 入口 `infer_one_from_pl_tensor()`**（复用冻结网络启动/heads/T62-T29 解码，跳过 CPU tensor memcpy 与 input cache writeback）；**mailbox driver**（HOST_REQ/PS_ACK/PS_GEOM/PS_RESULT）；**`mailbox_pixel_format_code=1 → BGR888` 显式映射表**（C enum `1=RGB565`，禁止直接 cast） | PS 固件需新增 RAW task 分支、去掉覆盖 PL 输出的 memcpy；保留 weights clean/flush、feature flush+invalidate、head 输出 invalidate+DSB；固定 UART `RUN` 流程保持不变 |

### 1.4 阶段5 显示叠加（只读引用）

| 已有 | 缺失 | 需改 |
|---|---|---|
| `w5` 树离线成果（显示/叠加设计文档，`docs/obsidian-project/02-方案设计/INT8乘加接口说明.md` 等） | 4-D 首轮显示叠加**不在本卡验收范围**（首轮以 UART + JTAG mailbox 结果区为主）；显示接线待 4-D bring-up 后再议 | 无（不改 w5） |

## 2. 4-D 目标数据流与增量范围

```
host/JTAG RAW 注入(BGR888, 109 样本)
   → [PL] s4b_preproc_frame: BGR→RGB + resize/pad 几何 + INT8 量化打包
   → [PL] HP0 串行 owner 写 frozen input tensor [0x10000000,0x1007EC00) 519,168 B
   → [PL] 冻结 INT8 网络(2B s2b_inference_top) 推理
   → [PS] 读 heads → T62/T29 解码/NMS → 40 B meta + 48 B×box 结果
   → 发布到 raw_meta PS_RESULT(+0x0100) / JTAG_RAW_TASK 数据区(+0x4f40)
   → UART(s2bu/1.1 固定 RUN 流程不变) + 显示叠加（后续）
```

**增量（相对 2B 平台与阶段4 诊断）**
1. **PL 预处理为新增**：`s4b_preproc_frame` + generic word master + AXI4-Lite 新块 `0x200..0x27c`；**不新增 DMA IP**，HP0 写仍走 `infer_M_AXI`（64 位）这套既有通路，由**串行 owner 状态机**保证同一时刻只有一个 HP0 写方。
2. **DMA/cache 一致性机制**（不引入新硬件，纯协议 + PS 维护）：
   - PS 侧：64 B 外对齐的行维护边界；跨 PL 交付前后按 ADR §8.2 做 `flush/invalidate` 并用 `DSB` 定序；
   - PL 侧：只对获批半开区间发起 8 B 对齐单拍访问；RAW 末拍只覆盖 `storage_bytes` 内逻辑 + 零 pad；
   - 完成序：`STATUS.network ledger empty` / `tensor-valid` 位 + `RESULT_CONSUMED` 门控，**不以"HP0 暂时安静"推断 safe-idle**（ADR §8.7 G2 明确禁止）。
3. **PS 侧增量**：RAW task 入口 + mailbox driver + 像素格式显式映射；**不变**：冻结网络启动、heads、T62/T29 解码、UART 固定 RUN 流程。

## 3. 地址与缓冲区分配（D1=A 内，机器可读见 `S4D_4d_address_allocation_20261027_r01.json`）

| 名称 | 半开区间 | 长度 | 对齐 | 用途 |
|---|---|---|---:|---|
| `raw_frame_slot` | `[0x12000000,0x12C00000)` | 12,582,912 | 8 B（`storage_bytes=align_up(logical,8)`） | 单帧 BGR888；首轮单缓冲、109 样本内 |
| `raw_meta` | `[0x12C00000,0x12C08000)` | 32,768 | 64 B | mailbox/geometry/结果区（下表） |
| ├ `HOST_REQ` | `+0x0000..0x007f` | 128 | 8 B | host→PS 请求（magic `S4BR`） |
| ├ `PS_ACK` | `+0x0080..0x00bf` | 64 | 8 B | PS→host 回执（`S4BA`） |
| ├ `PS_GEOM` | `+0x00c0..0x00ff` | 64 | 8 B | 几何参数（`S4BG`） |
| ├ `PS_RESULT` | `+0x0100..0x013f` | 64 | 8 B | 结果描述符（`S4BS`） |
| ├ `X_TABLE` | `+0x0140..0x283f` | 9,984 | 8 B | 416×24 B |
| ├ `Y_TABLE` | `+0x2840..0x4f3f` | 9,984 | 8 B | 416×24 B |
| └ `JTAG_RAW_RESULT` | `+0x4f40..0x7fff` | 12,480 | 8 B | JTAG RAW 任务结果数据区 |
| `frozen_input_tensor`（只读引用，非本卡写） | `[0x10000000,0x1007EC00)` | 519,168 | 64 B | PL 写 / 网络 master 读 |

**不相交证明**：由 `scripts/stage4_s4ctrl/verify_4d_address_allocation.py` 机械核验（见 §6 退出码），检查：① 全部在本卡获批的 `raw_frame`/`raw_meta` 内；② 两两不重叠且半开；③ 与 2B 冻结对象（tensor `[0x10000000,0x1007EC00)`、GF8 `[0x10100000,0x106A12FC)`、feature `[0x11000000,0x11ADADB8)`）不重叠；④ 与禁区 `[0x12C08000,0x20000000)` 不重叠；⑤ mailbox 子偏移与 ADR §8.2 表**逐项一致**（含长度和 32 KiB 合计）；⑥ 8 B/64 B 对齐。

## 4. 接口冻结声明（本卡构建所用 ABI）

- **冻结（本卡内不再改，改动须先报项目总控）**：四类 record 的 magic/`version=1`/`record_bytes`（128/64/64/64）/字段偏移（ADR §8.3）；几何表 schema `version=1`、416×24 B entry、X 表在前 Y 表在后、共 19,968 B；CRC-32/ISO-HDLC（=`zlib.crc32`）；AXI4-Lite 新块偏移 `0x200..0x27c` 与 `ID=0x50423453`、`VERSION=0x00010000`（ADR §8.4）；RAW 像素格式 **BGR888**、`mailbox_pixel_format_code=1` 且**必须经显式映射表**（不得 cast 到 `s4_inject_pixel_format`）；tensor 519,168 B / 64,896×8 B 全 WSTRB 覆盖。
- **非冻结（Phase 2 允许调整，须记录）**：PL 内部流水级数与新增寄存器数量；`s4b_preproc_frame` 内部模块划分；Vitis 应用内任务调度实现；显示叠加接线（本卡不做）。
- **冻结基线**：地址图 `7c20ac89…`、契约 r07 `25bc30d5…`、xref/geometry G2 对象 `e1e79fcf…`（geometry generator 两源），以上任一变更 ⇒ 本卡 Phase 2 前需重绑并重跑本卡验证器。

## 5. Phase 2 构建计划（未执行；须项目总控确认后开始）

**单次重任务约束**：本机 16 GB，同一时刻只跑一个重型构建；Phase 2 全程串行（先 Vivado 后 Vitis），不并行。

| # | 步骤 | 命令（模板） | 预计耗时 | 产出 |
|---|---|---|---|---:|
| B1 | 工作区准备 | 复制 2B 冻结 BD/RTL 闭包到 `tmp/4/S4-T32/build_<run>/`（只读源，不写 w2b） | 5 min | 独立构建目录 |
| B2 | 新块 RTL | 加 `s4b_preproc_frame` + word master + AXI4-Lite `0x200..0x27c`（新源，w4 `src/`） | — | RTL |
| B3 | Vivado 综合 | `vivado -mode batch -source build_4d.tcl`：`synth_design` → `opt_design` → `place_design` → `route_design` → `write_bitstream`；50 MHz 约束 | **40–80 min**（单任务） | `s4d_inference.bit` + 利用率/时序摘要 |
| B4 | XSA 导出 | `write_hw_platform -fixed -include_bit` | 5 min | `s4d_inference.xsa` |
| B5 | Vitis 平台 | `vitis -c`：从 B4 XSA 建 platform，编译 BSP | 15–25 min | platform |
| B6 | Vitis 应用 | 4-D 应用（初始化 + RAW task + mailbox driver + UART + 可选显示） | 15–25 min | `s4d_app.elf` + map |
| B7 | 登记 | 写 `payload_registry_4d.json`（`hash_basis=commit_blob` + `hash_basis_commit`）+ 构建记录（命令/退出码/耗时/工具版本） | 10 min | 证据 |

**硬要求**：所有命令与**真实退出码**落盘（不得手填）；任一步非 0 即停并保留日志；bit/XSA/ELF 记录完整 SHA-256 与大小；利用率/时序摘要取自工具报告原文件（不重算、不美化）；若时序不收敛 ⇒ **如实记录 FAIL**，不降低 50 MHz 目标、不改验收指标。

## 6. 风险清单

| # | 风险 | 影响 | 缓解 |
|---|---|---|---|
| R1 | **50 MHz 时序历史未收敛**（2B S10 −4.405 ns / S11 −3.201 ns） | 4-D 位流可能 WNS<0 | Phase 2 先跑综合+时序评估，再决定是否加流水；不隐瞒 FAIL |
| R2 | 新块资源挤占（LUT/FF/BRAM/DSP） | 实现失败或拥塞 | 综合后立刻看利用率；超预算先报后改架构 |
| R3 | **cache 一致性**（BGR 帧/张量/结果区） | 数据错但不报错 | 64 B 外对齐维护 + flush/invalidate + `DSB`；M4-a/M4-b 判据实测（Phase 3） |
| R4 | **DMA 完成序**误判（以"HP0 安静"当 safe-idle） | 覆盖未完成数据 | 只认 `ledger empty`/`tensor-valid`/`RESULT_CONSUMED` 位（ADR §8.7 G2 禁止） |
| R5 | HP0 带宽/时延超预算 | 帧率不达标 | 记录 grant tick/tensor done tick；不设 1800 s 上限（ADR §8.7） |
| R6 | 候选区仍 **BLOCKED**（地址图未登记 RAW/META owner） | 板上不得访问 | 本卡只离线构建；bring-up 前须由文档写入方登记 owner 并解除 blocked |
| R7 | 构建工具/器件版本漂移 | 产物不可复现 | 记录 Vivado/Vitis 版本、器件 `xc7z020clg400-2`、完整命令与 SHA |
| R8 | 109 样本尺寸超出 RAW 容量 | 注入失败 | 容量校验：最大帧 11,059,200 B ≤ 12,582,912 B（余量 1,523,712 B）；越界即拒 |

## 7. 未做（明确记录）

- Phase 2 未开始：无综合、无实现、无 bitstream、无 XSA、无 Vitis 构建、无 ELF ⇒ **本卡当前无任何构建产物**。
- Phase 3 未开始：M3/M4-a/M4-b 判据与 bring-up 计划未落盘（下一阶段交付）。
- 未接触板卡；`ENABLE=0`；未 FROZEN；不 push；未动 25 项遗留。
- 不声称已审查/已通过；不把"设计冻结"升级为 G0 PASS。