# S3-T05 v6 帧缓冲指纹上板判读：**实时直通成立**（2026-10-20 13:0x–13:2x UTC+8）

## 1. 输入

- 位流：SOF 修复变体 `7cb33068…8710`（`tmp/s3r06/t04_sof_fix_20261020_r01/.../impl_1/design_1_wrapper.bit`）
- XSA：`1f5b138e…cb0e3`；ps7_init 取自该 XSA
- 应用（v6，均由 `1f5b138e…cb0e3` XSA 构建、exit 0）：
  - 普通版 `an5642_j11cmos2_v6.elf` = `1053673a35d3140d448528887f80bae3d79f5e239c67c7e54e193dbc694fccf7`
  - 彩条版 `an5642_j11cmos2_v6_tp.elf` = `1594d67612d78cf8b1c0834973d6bb666a422d9260f2b6bcb3353fe265e7c5c5`
- 命令：`bash scripts/stage3_t05/run_t05_board_capture.sh <sof_fix_run> <elf> v6|v6tp 120`（两次；`T05_DOWNLOAD_EXIT=0`、`T05_READ_EXIT=0`）

## 2. 决定性结果：帧缓冲在持续变化 ⇒ **实时采集成立**

v6 对 3 处区域（fb+0x000000 / +0x080000 / +0x100000）各 64 KB 计算 `sum32 + CRC-32(0xEDB88320)`，
**读前 `Xil_DCacheInvalidateRange`**（cache 正确），在 t≈5/10/15/20/25 s 各打一次：

| site | t=5 | t=10 | t=15 | t=20 | t=25 |
|---|---|---|---|---|---|
| 0 hash | 113876F3 | 8B58755C | 3B1C7CBD | EB1850A8 | DCAE4115 |
| 1 hash | C9AA75F0 | 2F243F34 | 71607CDC | 777B5AC1 | 4715167D |
| 2 hash | F47230AF | 4483B858 | FF38BEC7 | E44B4BCF | BAF09477 |

**15 个指纹互不相同**（nz 亦在 16369–16384 间波动）⇒ **S2MM 在这 20 秒窗口内持续写入新内容**。
同时 t≈30 s 传感器回读 `4202=0x00`（仍在流）。

→ **“相机 → DVP → 厂商 IP → subset converter → S2MM → DDR → MM2S → v_axi4s_vid_out → rgb2dvi → HDMI 显示器”
的实时直通在实物上成立**；此前基于 JTAG 标记法得出的“冻结单帧”判断**作废**
（xsdb `mwr/mrd` 经 halt 的 A9 数据 cache，不可作为 DDR 内容证据，已如实记录在 `t05_soffix_board_20261020_r01/`）。

## 3. 彩条对照（颜色判读用，进行中）

彩条版 ELF 运行证据：`S3_DIAG6_TESTPATTERN=ON write_status=0`，t≈30 s 回读 `503D=0x80`（测试图已开）。
彩条是**静态**已知图案：site0 的指纹在 t=5 与 t=25 完全相同（`E48F2360`），与静态图案+持续写入一致。
**颜色是否正确的判读需要人眼/照片**（标准 8 条：白/黄/青/绿/品红/红/蓝/黑），由 Wong 提供；本轮未做色卡或仪器测量。

## 4. 仍存在的已知现象（不影响直通）

- S2MM SR 启动后仍带一次粘滞错误：`0x00015810`（`bit4 INT + bit11 FSZ_MORE/SOFLate + ErrIrq`）；
  清 sticky 后 **20 s 内不再复现**（见 `t05_soffix_board_20261020_r01/`）。判读：DMA 在“流中途启动”的一次性竞态；
  未定位到会影响连续写入的证据（指纹持续变化即为反证）。
- `CRITICAL WARNING [Timing 38-249]`（rgb2dvi SerialClk 与 PIX_CLK 未声明 ×5 关系）仍在；DRC 0 error、时序为正。

## 5. 限制

- 未接显示器 **以外的**仪器验证；偏色成因未定论；未做耐久测试；未烧 QSPI。
- 彩条版含**对传感器的一次写**（`0x503D=0x80`），可通过重新下载/复位恢复；未做恢复性复核。