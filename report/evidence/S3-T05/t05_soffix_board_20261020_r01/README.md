# S3-T05 SOF 修复位流上板验证（2026-10-20 12:5x–13:0x UTC+8）

## 1. 输入与命令

- 位流：`tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit`（SHA-256 `7cb330685260ced38636d3e90a92160979b0f88770d380269e9864722ce48710`）
- XSA：`tmp/s3r06/t04_sof_fix_20261020_r01/design_1_wrapper.xsa`（`1f5b138e693065c6257e29075018f7654d4c3a6b67dcab051f0ea8ac106cb0e3`）
- 应用：v5 诊断 ELF `a54d0385…1b0c3e`（PS 接口未变，沿用；ps7_init 取自新 XSA）
- 命令：`bash scripts/stage3_t05/run_t05_board_capture.sh <sof_fix_run> <v5 elf> soffix 120` → `T05_DOWNLOAD_EXIT=0`、`T05_READ_EXIT=0`

## 2. 结果

| 观察 | 修复前（J11CMOS2 位流） | 修复后（SOF fix 位流） |
|---|---|---|
| 上电启动后 S2MM SR（未清 sticky） | `0x00014810 / 0x00015810`（INT+FSZ_MORE/SOFLate+ErrIrq） | 同样 `0x00014810 / 0x00015810` |
| **清 sticky 后 20 s 内是否再出现错误** | 未做（当时无法区分） | **`SR=0x00011000` 保持不变（只有 FrmCntIrq+阈值字段，无错误位）** ✅ |
| 帧缓冲三处内容 | 采样间有变化 | 采样间有变化（v5 应用 cache 正确回读） |

**结论（有限、如实）**：SOF 修复位流下，**清掉 sticky 位后 20 秒内不再产生 FSZ_MORE/SOFLate 或 DMAIntErr**，
说明“帧起始不再持续缺失”；启动瞬间的一次粘滞错误可能与“DMA 在流中途启动”的竞态有关（**未证实**）。

## 3. 未能定论：画面是否实时（JTAG 标记法不可靠，已弃用）

用 JTAG 向帧缓冲写标记字、看是否被新帧覆盖的方法得到**互相矛盾**的结果
（`0x00120C40` 处：一次 200 ms 内被覆盖、另一次 4 s 未被覆盖、再一轮 5/5 被覆盖；
每次读写都在 halt 的 A9 上通过 DAP 进行）。**判读：xsdb `mwr/mrd` 在 halt 的 A9 上可能经数据 cache，
不能作为 DDR 内容的可靠证据**，因此不据此下“冻结/实时”结论。

可信的是**应用侧 cache 正确回读**（每次读前 `Xil_DCacheInvalidateRange`）：
v5 在 t≈5/15/25 s 三次采样的帧缓冲内容**互不相同**，SR 亦随时间从 `0x14810` 变为 `0x15810`
→ 与“DMA 在采样窗口内持续写帧”一致，但**不足以排除静态场景下的偶发写入**。

**→ 需要一次“运动测试”作为最终判据**：Wong 在镜头前挥手，看画面是否跟随。

## 4. 其他在线实验（均已还原/易失）

- `scripts/stage3_t05/jtag_sr_clear_liveness.tcl`：清 S2MM SR（W1C）+ 20 s 观察 → 见上表。
- `scripts/stage3_t05/jtag_framestore_probe.tcl`：S2MM 帧存地址 `FS1=0x00110C00`、FS2–FS4=0；`0x00100000` 仍是应用代码（`EA000049`）未被 DMA 破坏。
- `scripts/stage3_t05/jtag_cont_write_probe.tcl`：重启 S2MM 后（`SR=0x14810`）标记 5/5 未被覆盖 → **JTAG 手动重启会重现“SOFLate + 停写”**，说明该错误与“在流中途启动 DMA”有关；应用启动路径未重现同样停滞（见第 3 节）。
- 未烧 QSPI、未改接线、未做电气测量。

## 5. 限制

- 未取得 ILA 波形（BASIC 许可无 `create_debug_core`），VSYNC/TUSER 只有行为证据。
- “画面是否实时”“偏色成因”均**未定论**；本记录不构成 G3 通过。