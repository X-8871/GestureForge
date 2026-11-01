# 明早交接（2026-11-01 05:4x UTC+8）

> 目标：Wong 起来时能直接完成「摄像头识别手势 → 显示器显示答案 → 产生交互」的 MVP 验收。

## 一、一句话状态

**软件链已全部打通并逐环验证；唯一未解是相机帧写入 DDR —— build11l（tuser 整形 + xsim 仿真通过）正在构建，约 06:30 出 bit，随后板级 r12 一枪定论。**

## 二、已证实可用（都有板级证据）

| 环节 | 证据 | 窗口 |
|---|---|---|
| CR.RESET 能清除、VDMA 通道可启动 | `CAM_CR=0x10001`（RS=1/RESET=0） | r05/r06/r08/r09 |
| 传感器几何可写可读 | `CAM: geom dvpho=1280 dvpvo=720 hts=1892 vts=740` | r08/r09 |
| 相机数据流存在 | `S2MM_BEAT` 1.4B、`TL_TLAST` 1.09M、`STALL=0`、30 fps | r05–r09 |
| 帧结构正确 | 每行 1280 px、每帧 720 行、tuser 每帧单脉冲（build11i 时 4880/120s） | r05/r06 |
| INT8 权重加载 | `verify -data` 5.9 MB 逐字节通过、`GFINT8W1 OK` | r08/r09/r11b |
| YOLO 推理执行 + 每帧 ACK | `dt_pl≈47.5 s/轮`、`MVP ERR` 0 条 | mvp_ack_r01 |
| S5RS 结果块 | `magic=0x53355253`、`status=0x1`、seq 递增 | mvp_ack_r01 |
| 显示消费真实帧 + HUD | 合成 S5RS + 合成图 ⇒ `src=real`、`nbox=1`、`APP: gesture=数字一` | disp_realpath_r03 |
| 5 类中文映射 | `0=fist 拳头 1=palm 布 2=one 数字一 3=two_up 数字二 4=three 数字三` | gesture.names `5926aa20…` |

## 三、唯一缺口（具体到寄存器级）

相机流正确但 **VDMA 收不到 SOF（tuser）** ⇒ `SR.FSZ_MORE(0x800)` 每帧复现 ⇒ 帧永不完成 ⇒ `0x12000000` 全 0。

- build11i：tuser 在 VSYNC 下降沿产生（无 tvalid 同拍）⇒ 大概率未被 VDMA 采样
- build11k：改成"随首拍 tvalid"但 **RTL 把 vsync 检测通路打断**（`VSYNC_NEG` 4880→1）⇒ 退化
- **build11l**：base = b11j（b11i 通路一行未动）+ 独立模块 `tuser_shaper.v`（aclk 域，`tuser = sof_pending & conv_tvalid`），**xsim 仿真 PASS**（3 帧、每帧 tuser 恰 1 拍）

## 四、build11l 出来后怎么跑（board-runner 已就绪）

```bat
cd /d D:\tmp\lead\p3b_smoke_20261030_r01
python run_mvp_20261031.py --run-id mvp_chain_20261101_r12 ^
  --bit D:\tmp\lead\p3r_camera_20261031_r01\out\build11l\s4d_p3r_r01.bit --bit-sha <b11l> ^
  --xsa D:\tmp\lead\p3r_camera_20261031_r01\out\build11l\s4d_p3r_r01.xsa --xsa-sha <b11l> ^
  --ps7init-tcl p3r_build11l_ps7_init.tcl ^
  --display-elf D:\tmp\lead\p3b_display_sw_20261030_r01\build\s5_display_app_p3r_camera.elf --display-sha d1ecc0d8592cec2d414dc73e2c47ee19c7e0c1eaf9ff25eefcc93465058e5743 ^
  --infer-elf D:\tmp\lead\mvp_infer_20261031_r01\build\s4d_ps_app_mvp_core1.elf --infer-sha 5806d33de1e888bb8b4fb2f63ef64246087316b4335f8b74fbba0710d0b48270 ^
  --weights D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_tiny416_int8_weight_r2\gesture_yolov4_tiny_416_int8_weights.gf8 --weights-sha f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39 ^
  --clear-raw --collect-seconds 120
```

判据（相机通）：
1. `0x12000000` 清零后快照随时间变化
2. `CAM: sr_after_1s` 干净（`0x10000`）
3. 探针：`TLAST2TUSER==0`、`FRAME_BEATS==921600`、`TUSER2TLAST==1280`

## 五、明早 Wong 的验收（一次命令，3 分钟）

```bat
cd /d D:\tmp\lead\p3b_smoke_20261030_r01
python run_mvp_20261101_accept.py --gesture-window 180
```
- 脚本默认用 build11l + v35 显示 ELF + core1 `5806d33d…` + 权重，**内置 `--clear-raw`**
- 采集 180 s，实时打印关键行，结束自动生成 `MVP_ACCEPT_REPORT.md`
- **Wong 只需在摄像头前比手势**：先「数字一」60 s，再「拳头」60 s（识别 47 s/轮，需保持不动）
- 屏幕上应出现：彩色边框 + 左上「手势：数字一/拳头」+ 右下 `lat≈47300ms`；UART 出现 `MVP S5RS … n_dets≥1`、`APP: gesture=…`
- 拍照存到报告里给的 `screen_photo.jpg` 路径

## 六、若 r12 仍不通（备选，按优先级）

1. **build11m**：把 tuser 延迟 1–2 拍（`sof_pending` 消费提前/latch 时序微调），并同时输出"SOF 后 1/2/3 拍的 tvalid/tready 采样值"探针
2. **换 FSYNC=0 路线**：在 build11l 上仅改 `c_use_s2mm_fsync=0`（此时 tlast 逐行 + VSIZE 数帧），并保留探针观察 tready/tvalid 持续情况
3. **自研 AXIS→HP 写模块**（可控性最高，但要 2–3 h RTL + 仿真）

## 七、未完成/限制（如实）

- 相机→DDR 仍未打通（本文件写作时）
- 47.3 s/轮识别延迟未优化（B 方案 160×160 未启动，Wong 已定 MVP 先用 416）
- 非 MVP 任务（R-16/R-17/R-02 裁决材料）按 Wong 指示全部暂停
- 力量：今晚共做 build11a–11l（12 版位流）、mvp_chain r01–r11b + disp_realpath + mvp_ack 等 20 个板窗，全部有证据目录（见 `report/evidence/S6-T01/EVIDENCE_INDEX_20261101.md`）

## 八、关键 sha（明早直接用）

| 件 | sha256 |
|---|---|
| display v35 | `d1ecc0d8592cec2d414dc73e2c47ee19c7e0c1eaf9ff25eefcc93465058e5743` |
| core1（ACK 修复） | `5806d33de1e888bb8b4fb2f63ef64246087316b4335f8b74fbba0710d0b48270` |
| 权重 | `f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39` |
| b11i（对照） | bit `e3400660…` / XSA `e945d026…` |
| b11k（已废） | bit `f1c9b573…`（RTL 退化，不再用） |
