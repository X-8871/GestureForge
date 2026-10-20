# S3-T05「SOF 修复变体」证据入口

- 任务：task-2（阶段总控 2026-10-20 改派：帧同步修复变体；ILA 诊断降为可选）
- RunId：`tmp/s3r06/t04_sof_fix_20261020_r01`（新建，未复用任何既有 RunId）
- 基线提交：`e9b853f356ac6f32b2b9b961c71d55bf0c26f6c4`（分支 `codex/stage3-video`）
- 构建命令（真实原文见 `build_report.json.commands.build`）：
  `D:/Xilinx/2026.1/Vivado/bin/vivado -mode batch -source scripts/stage3_t04/build_t04_camera.tcl -log <run>/vivado.log -journal <run>/vivado.jou -tclargs <run> <run>/vendor_src`
- 启动器：`scripts/stage3_t04/run_t04_camera_j11cmos2_soffix_build.sh`
- **真实退出码：0**（impl_1 = `write_bitstream Complete!`、PROGRESS 100%）

## 产物（SHA-256）

| 产物 | 路径 | SHA-256 |
| --- | --- | --- |
| bitstream | `tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit` | `7cb330685260ced38636d3e90a92160979b0f88770d380269e9864722ce48710` |
| XSA | `tmp/s3r06/t04_sof_fix_20261020_r01/design_1_wrapper.xsa` | `1f5b138e693065c6257e29075018f7654d4c3a6b67dcab051f0ea8ac106cb0e3` |
| 补丁 | `board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch` | `fd854a622b52c32a43a6770be3f583cce29864a764845c313b623514c91ab2c5` |
| 补丁前 RTL | vendor `my_ip/ov5640_ip/src/alinx_ov5640.v` | `98260b62f996ec700eb766c6c4e57706b2c1ff3a8224a5105a3641b6475b3e4d` |
| 补丁后 RTL | 同上（应用补丁后） | `db4857fe2fc8d86aa831bac619ddfc676d076f0114ba2c07988d944f894adce6` |

## 补丁内容（3 个 hunk，+24 / −5 行，纯 ASCII）

`my_ip/ov5640_ip/src/alinx_ov5640.v`：

1. 新增参数 `GAP_THRESH = 16'd16384`；
2. 新增 `reg[15:0] cmos_hblank_low_cnt`；
3. `s_axis_tuser` 触发条件由 `cmos_vsync_d1==1 && cmos_vsync_d0==0` 改为
   `cmos_hblank_d0==0 && cmos_hblank==1 && cmos_hblank_low_cnt >= GAP_THRESH`
   （hblank 连续低 >= GAP_THRESH 个 pclk 后的第一个有效像素 = 帧第一行第一个有效像素），
   保留原「置起 → 首个 `s_axis_tvalid` 清除」结构；计数器饱和不回绕。

未 OR 原 vsync 触发；未打开 `DEBUG_OV5640`（构建里显式保持 `false`）。

## 时序依据（独立核算，与总控估算不同）

来自厂商驱动 `Vitis/auto_create_vitis/src/an5642_single/ov5640.c` 的 1280x720 寄存器表：

| 项 | 值 | 依据 |
| --- | --- | --- |
| PCLK | 84 MHz | `0x3035=0x21, 0x3036=0x69`（驱动注释 input 24MHz → PCLK 84MHz） |
| HTS | 1892 | `0x380c/0x380d = 0x0764` |
| VTS | 740 | `0x380e/0x380f = 0x02e4` |
| 有效尺寸 | 1280x720 | `0x3808/0x3809=0x0500`、`0x380a/0x380b=0x02d0` |
| 行消隐间隙 | 612 pclk | HTS − 1280 |
| 场消隐间隙 | ≈38452 pclk | (VTS − 720) × HTS + 612 = 20×1892 + 612 |

结论：`612 < 16384 < 38452`，默认阈值两侧都有余量；帧率 = 1892×740/84e6 = 16.67 ms = 60 fps，
与 PCLK=84MHz 自洽。**总控给出的「行周期约 3784 pclk、HBLANK 约 2.5k」与寄存器不符（约 2× 偏差），
本轮以寄存器核算为准。**

## 构建结果

| 指标 | 本次（含补丁） | 基线 04 run | 说明 |
| --- | --- | --- | --- |
| WNS (ns) | 1.054525 | 1.141183 | 下降 0.087，仍为正 |
| TNS (ns) | 0.000000 | 0.000000 | |
| WHS (ns) | 0.058931 | 0.058332 | 仍为正 |
| THS (ns) | 0.000000 | 0.000000 | |
| DRC Error | 0 | 0 | 8 条 Warning，明细与基线一致 |
| 峰值内存 | 2568.176 MB | 2555.516 MB | |
| Slice Registers | 10548 | 10534 | +14（IP 自身 OOC：401 → 415，与 16 位计数器一致） |
| 耗时 | 550 s | — | |

补丁进入设计的独立旁证：工程 `.gen/.../ipshared/564b/src/alinx_ov5640.v` 副本哈希 =
补丁后 RTL 哈希，且含 `GAP_THRESH`；摄像头 IP OOC 综合寄存器数 +14。

## 本目录文件

- `build_report.json`：机器可读产物清单（含命令、退出码、补丁信息、时序、DRC、内存、产物哈希、限制）
- `alinx_ov5640_sof_hrefgap.patch`：补丁原文（与仓库内文件同哈希）
- `patch_git_apply.log`：`git apply --check` 与 `git apply` 的真实输出与返回码（均 0）
- `make_sof_hrefgap_patch.py`：补丁生成器（可复现；含锚点断言与 hunk 级往返自检）
- `patch_verification/`：补丁三方核对（`pristine_alinx_ov5640.v` 补丁前、
  `expected_patched_alinx_ov5640.v` 补丁后、`alinx_ov5640_sof_hrefgap.patch` 补丁本体）；
  三个文件哈希与 `build_report.json` 记录一致，可直接 byte-level 复核
- `vivado.log` / `vivado.jou`：Vivado 原始日志与命令流水
- `report_*.rpt`：实现后的时序/DRC/利用率/时钟报告副本

## 限制与未执行

- 未下载、未烧 QSPI、未上板；图像与 VDMA S2MM SR 验证由阶段总控执行。
- 未做 RTL 功能仿真（无既有 testbench）；正确性靠时序核算 + 上板实测。
- 复位后第一帧可能无 SOF（`cmos_aresetn` 由 200M pclk 计数器保持低约 2.4 s）；第二个场消隐起必然超过阈值。
- `GAP_THRESH=16384` 只对 1280x720（HTS=1892/VTS=740）成立；换模式需重新核算（阈值必须 < 场消隐 pclk 数）。
- 首次 `launch_runs synth_1` 的 OOC 子 run 有启动期抖动（`Could not open 'C' for writing`，3 条 ERROR），
  由 `build_t04_camera.tcl` 的重试机制在第 1 次重试后恢复，非设计错误。
- 未提交 Git（由阶段总控统一提交）。