# board-runner 交班要点（2026-11-01 05:25，等 build11l 期间整理）

> 面向接班的 board-runner / 明早 Wong：只写"可复核事实 + 下一步命令 + 风险"，不重复 lead 的总交接文档。

## 1) 一句话状态

- **软件侧全链路已证清**（权重→推理 ACK→S5RS status→显示消费→HUD 中文手势名，含合成数据验证）
- **唯一未解**：相机 AXIS 流 → VDMA S2MM 的 **SOF（tuser）采样**；`CAM_SR` 恒 `0x14810`（`FSZ_MORE`），`0x12000000` 无真实帧
- 板卡现 **clean**（`board_state.abnormal=false`，`last_clean_run=mvp_chain_20261101_r11b`），`hw_server=0`、3121/3122 空闲、核停

## 2) 今晚已验证的事实（可直接引用）

| 事实 | 证据（RunId） |
|---|---|
| `CR.RESET` 清不掉问题已解决（`CAM_CR=0x10001`，RS=1/reset=0） | `mvp_chain_20261101_r02` / `r05` + `S14_post_scan.json` |
| 几何最终对齐 1280×720/3840/720（`CAM: geom dvpho=1280 dvpvo=720`） | `mvp_chain_20261101_r09` |
| 相机实际出流：`TLAST_BEAT=1280`、`TUSER_TLAST=720`、`TUSER_SHAPED≈VSYNC≈4880/120s`（build11i） | `mvp_chain_20261101_r05` |
| build11k 打断 tuser 整形：`TUSER_SHAPED` 4880→**1**、`VSYNC_NEG` 4880→1、`CAM: frm` 恒 0、3 新探针全 0 | `mvp_chain_20261101_r11b` |
| core1 ACK 修复有效：`MVP S5RS … status=0x1`、`MVP ERR` 839→**0**、`MVP CHECK raw_blank status=0x1 … OK` | `mvp_chain_20261101_r11b` / `mvp_ack_20261101_r01` |
| **显示消费真实帧已单独验证**：注入 `0x20800000 status=0x1 n_dets=1` + 红蓝图 ⇒ `src=real`、`boxes n=1`、`gesture=数字一` | `disp_realpath_20261101_r03` |
| `--clear-raw` 有效：清零后 `raw_nz=0` 正确基线（避免残留图假阳性） | `mvp_chain_20261101_r11b`（`S5b_clear_raw.json`） |

## 3) 待办（按优先级）

1. **build11l**（xsim 先行；预计 05:45）→ 跑 `mvp_chain_20261101_r12`
   - 判据：`0x12000000` 快照随时间变化、`CAM: sr_after_1s=0x10000`、`TLAST2TUSER==0`、`FRAME_BEATS==921600`、`TUSER2TLAST==1280`
   - 若通过 ⇒ 立刻报 lead，安排手势窗
2. 相机通后跑**手势验收**：`python run_mvp_20261101_accept.py --gesture-window 180`
   - 脚本 sha `21793dfcc290295493e93eebf7afbd11e6e1325e689ba76d3551a1b21a36bf7f`
   - 默认 build11l 位流（可用 `--bit/--xsa/--bit-sha/--xsa-sha` 覆盖）；内置 `--clear-raw`
   - 产出 `MVP_ACCEPT_REPORT.md` + `MVP_ACCEPT_CRITERIA.json`；需人工把屏幕照片存 `<证据目录>/screen_photo.jpg`

## 4) 关键命令（照抄可用）

```bash
# 相机验证窗（build11l，120 s）
python run_mvp_20261031.py --run-id mvp_chain_20261101_r12 \
  --bit ...\out\build11l\s4d_p3r_r01.bit --bit-sha <b11l> \
  --xsa ...\out\build11l\s4d_p3r_r01.xsa --xsa-sha <b11l> \
  --ps7init-tcl p3r_build11l_ps7_init.tcl \
  --display-elf ...\build\s5_display_app_p3r_camera.elf --display-sha d1ecc0d8... \
  --infer-elf ...\s4d_ps_app_mvp_core1.elf --infer-sha 5806d33d... \
  --weights D:\FPGA_Data\...\gesture_yolov4_tiny_416_int8_weights.gf8 --weights-sha f6feb6d4... \
  --clear-raw --collect-seconds 120

# 手势验收（明早 Wong）
python run_mvp_20261101_accept.py --gesture-window 180
```

## 5) 规则与风险（必须遵守）

- **异常终止**：崩在"应用加载前"⇒ 写 `board_state_correction.md` + `corrected_by` 更正后重跑；崩在"应用运行中"⇒ **停手等物理 POR**
- 每窗后必须核 `hw_server=0`、3121/3122 空闲；`board_state.abnormal=false`
- 不重跑/不改写旧 RunId；证据一律新目录
- 开窗必须带 `--clear-raw`（或先确认 `0x12000000` 无残留）
- 单次 `rst -system`（MVP 脚本 init 阶段一次）；`rst -processor` 每核每窗最多一次
- 只有 E1 `--por` 能清真实残态；correction 仅限"脚本 bug 误标且已核实无配置/零残留"

## 6) 文件清单（board-runner 维护）

- 主脚本：`D:\tmp\lead\p3b_smoke_20261030_r01\run_mvp_20261031.py`（含 `--clear-raw`、J1–J6、4+3 个探针）
- 验收脚本：`run_mvp_20261101_accept.py`
- 探针脚本：`run_vsize_probe.py`（VSIZE 直接验证）、`run_disp_realpath.py` / `run_disp_realpath_s5rs.py`（显示侧合成验证）
- 后置扫描：`r02_post_scan.py` / `r03_post_scan.py` / `r04_post_scan.py`（同一模板）
- 证据索引：`report/evidence/S6-T01/EVIDENCE_INDEX_20261101.md`（可重跑 `make_evidence_index.py`）
- 位流 ps7_init：`p3r_b11h/b11i_ps7_init.tcl`、`p3r_build11k_ps7_init.tcl`（b11l 到时自动提取为 `p3r_build11l_ps7_init.tcl`）
---

## 7) 最新进展（07:30 更新：b11l/b11o 结果 + 根因收敛）

### 已完成窗口

| RunId | 位流 | 结论 | 关键事实 |
|---|---|---|---|
| `mvp_chain_20261101_r12` | b11l | 相机结构验证 | 探针**全对**：`TUSER2TLAST=1280`、`TLAST2TUSER=0`、`FRAME_BEATS=921600`、`TLAST_BEAT=1280`、`TUSER_TLAST=720`、`TUSER_SHAPED=VSYNC_NEG=5142/120s`；但 `CAM_SR=0x14810`、`0x12000000` 全 0、`FRMCNT=1` |
| `mvp_chain_20261101_r14` | b11o | 同 b11l 结果 | `pc_hp2 READ_WRITE_MODE=READ_WRITE` 已生效（hwh 实证 + 构建告警消失），但 `CAM_SR` 仍 `0x14810`、`DDR` 仍全 0 ⇒ **pc_hp2 写方向不是根因** |

### 已排除的根因

1. ~~CR.RESET 清不掉~~ —— b11a/v27e 后解决（`CAM_CR=0x10001`）
2. ~~几何不一致（640x480 vs 720/3840）~~ —— v32 后统一 720（`dvpvo=720`、`VSIZE=720`）
3. ~~tuser 整形缺失~~ —— b11l 修复（`TUSER_SHAPED≈VSYNC`）
4. ~~smartconnect 写方向 / pc_hp2 READ_ONLY~~ —— b11o 修复，**行为不变**
5. ~~core1 每帧 ACK~~ —— `5806d33d…` 修复（`status=0x1`、`MVP ERR=0`）

### 当前唯一未解

- `CAM_SR` 恒 `0x14810`：bit4 `0x10` DATAMOVER INTERNAL ERROR + bit11 `0x800` FSZ_MORE + bit14 `0x4000` Error IRQ + `FRMCNT=1`
- AXIS 探针证明**流侧帧结构完全正确**（921600 beats/帧、1280/行、720 行、帧间 0 beat、tuser 每帧 1 个、`S2MM_STALL=0`）
- `0x12000000` 全 0、`FRMCNT` 恒 1 ⇒ 帧被中止、写未到 DDR

### 下一步（建议）

**build11p = b11o + ILA**，探两组信号（任一即可定性）：
- AXI 写侧：`m_axi_s2mm_awvalid/awready`、`wvalid/wready/wlast`、`bvalid/bresp`
- AXIS 侧：`s_axis_s2mm_tvalid/tready/tlast/tuser`
- 判读：`awvalid` 不拉高 ⇒ 写通道问题；`bresp≠0` ⇒ HP2 拒绝；tlast/tuser 相位与探针不符 ⇒ 帧边界问题
- ILA 深度 8192，触发 `awvalid && awready` 或 `tuser`

### 明早验收命令（未变）

`ash
python run_mvp_20261101_accept.py --gesture-window 180
`
- 当前默认位流 = **build11o**（`7c46a8a9…`）；若 build11p 出了，用 `--bit/--xsa/--bit-sha/--xsa-sha` 覆盖
- 脚本 sha 当前 = `62eda36a6273a9896f2d4c513cf4a9888ebbae06a752c669016a5928bfdd2377`（改成 b11p 默认后会变，需同步）
- **首窗前必须 `--clear-raw`**（脚本已内置）
