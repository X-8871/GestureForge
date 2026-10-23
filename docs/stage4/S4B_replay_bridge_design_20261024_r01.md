# 阶段4：(A) 输入张量驱动离线前向桥 — 复用面确认与设计（task-26，无板卡轮）

- 状态：**REUSE_SURFACE_CONFIRMED**（桥接实现未开始）；本文件为**范围外**新文件，不动被审三份文件。
- 日期：2026-10-24（UTC+8）；所有者：DSH 阶段4 总控。
- 边界：**离线等价，不声明与板上一致**；计时 `replay_only`；缓冲 `scope=offline_host`；`ENABLE=0`、未 FROZEN、不动硬件。

## 1. 边界 1 的尝试结果：既有入口**无法**直接喂入回放帧（契约层面，不是能力问题）

`s1_t02_d2_int8_forward.py` 的输入契约**硬性**要求：
- `read_calibration_list(path, count)`：校准清单**必须 512 行且无重复**，`sample_count ∈ 1..512`（`EXPECTED_CALIBRATION_SAMPLES = 512`）。
- `load_activation_scales(report, cfg, weights, calibration_list)`：激活报告必须携带且匹配 **`cfg_sha256` / `weights_sha256` / `calibration_list_sha256`**，并断言「固定 512 张 train-only 校准」。

⇒ 想把「回放帧」按校准样本形式喂入，必须**改冻结校准清单或其 SHA 绑定**——**禁止**（边界 1）。故按边界 1 的例外走桥接，且桥接**必须 import 既有前向代码**。

## 2. 复用面（只读探针实测，RunId `t21_replay_bridge_probe_20261024_r02`）

- 被测模块：`verification/s1_t02_d2_int8_forward.py`，**模块 SHA-256 = `0b90ef46b923b046cfcabb0b8ff8aaff4f6b927b9b8ee9eaa10335362c6c922a`**。
- 导入方式（重要）：`importlib` 加载后**必须先注册 `sys.modules`**（模块顶层用 `@dataclass`，未注册会 `AttributeError: 'NoneType' object has no attribute '__dict__'`；首轮 r01 即此失败并保留）。
- 可直接复用的符号：`INPUT_SCALE` = `0.007874015748031496`（=1/127）、`Tensor`、`forward_one`、`parse_cfg`、`read_calibration_list`、`load_activation_scales`、`load_image_chw`、`sha256_file`、`Int8ForwardError`、`EXPECTED_CALIBRATION_SAMPLES`。
- 待解析（探针按名未命中，非缺失）：权重包/浮点权重装载函数实际名（源码中位于「INT8 权重包不可读取」与「浮点权重不可读取」两处错误串附近的函数）。
- 冻结件位置（只读，实测存在）：
  - 校准清单 `D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_calibration_r2\calibration.list`（另有 r1）
  - GFINT8W1 权重包 `…\s1_t02_d2_tiny416_int8_weight_r2\gesture_yolov4_tiny416_int8_weights.gf8`（5,903,100 B；另有 r1）
  - 激活校准目录 `…\s1_t02_d2_activation_calibration_r1\`（激活报告在其中，待定位具体文件名）

## 3. 桥接设计（不复制第二份网络数学）

```
frame_full.bin (BGR,1280x720)            ← 阶段3 回放包（blob 939fce22…）
  → [S1] 形状/长度/哈希校验 + BGR→RGB
  → [S2] 冻结 D2 离线等价预处理（沿冻结量化口径；scale/zero-point 记入证据）
         → CHW INT8 416x416 张量 + 张量哈希
  → [S3] import 既有前向：forward_one(tensor, sections, float_layers, package_layers, activation_scales)
         （sections/浮点层/包层/激活 scale 全部由**冻结件装载函数**得到，不新写数学）
  → [S4] 既有 D9 / 解码-NMS 参考（只读跨树取主目录 T25/T29，登记 HEAD + fail-closed 断言）
  → [S5] 回放结果包（离线/回放标记）
```

**必须随证据提交**：所用 `INPUT_SCALE` 与各层 `activation_scale`、张量哈希、冻结件 SHA（cfg/权重包/激活报告/校准清单）、模块自身 SHA、被读树 HEAD 与漂移断言结果。

**判别力与可复现（边界 3）**：同一输入跑两次须同 heads 哈希；负向对照至少两条——① 故意错一个量化 scale ⇒ 输出必须变；② 篡改输入张量 1 字节 ⇒ heads 哈希必须变。

**对拍（边界 4）**：在同一（冻结）校准样本上，桥接 `forward_one` 输出必须与既有参考**逐值一致**；不一致即不得采用。

## 4. 与既有入口的关系（不越界）

- **不修改**任何冻结件（cfg/权重/GF8 包/D2 黄金/契约/校准清单）。
- 桥接只**新增** w4 内文件；输入/中间产物只写 `tmp/4/S4-CTRL/<run_id>/`。
- 桥接产物一律标注 **offline_equivalent / replay_only**；**不得**表述为 PL 实测或板上一致。

## 5. 下一步

1. 解析权重包/浮点权重装载函数名与激活报告路径（只读）。
2. 实现桥接脚本（新文件 `scripts/stage4_s4ctrl/replay_forward_bridge.py`）+ 单测式自检（可复现、两条负向对照）。
3. 在冻结校准样本上做**逐值对拍**（边界 4）。
4. 跑回放帧 → heads → 解码/NMS（只读跨树 T25/T29，加漂移断言）→ **回放结果包**。
5. 之后再动 G0 离线缺口设计与窗口申请包；**回放绑定落盘仍等复审结论**。