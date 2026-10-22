# S5-T01 上板尝试 RunId `s5t01_board_20261022_r01`（板卡已上电，JTAG 链为空）

- 时间（UTC+8）：2026-10-22 13:38
- 结论：**门禁 `GO`（依据＝Wong 显式授权）**；**板卡上电后 JTAG 链仍为空（0 器件）** → **未下载位流/ELF、未写任何寄存器**，已停并请求物理排查。
- 关键判据：hw_server **已识别到 JTAG 线缆**，但 XSDB 目标树为空 ⇒ 问题在**线缆的板侧排线**或**板卡 FPGA 供电**，不在 USB/驱动/进程占用。

## 1. 门禁（本 run 复核）

| 项 | 结果 |
|---|---|
| decision / exit | `GO` / **0** |
| release_basis | `operator_authorization`（`authorized_by=Wong`，13:25 授权、13:34 反馈已上电；已留痕） |
| fail-closed 项 | 无硬件/EDA 进程、六棵树无 `index.lock`、进程枚举成功 |

## 2. JTAG 诊断链（全部只读）

| 步骤 | 命令/输出 | 判读 |
|---|---|---|
| 上电后链探测 | `run_xsdb.sh jtag_probe2.tcl` → `targets` 空 | 目标树无器件 |
| xsdb 命令表 | `info commands *jtag*` → 存在 `jtag` | 可查线缆/子命令 |
| 子命令探测 | `jtag frequency` → `Invalid target. Use "jtag targets" command to select a target` | 无目标可选 |
| **线缆查询** | `jtag servers` → **`digilent-ftdi cables 1`**；`jtag targets` → **`1 Digilent JTAG-HS1 210512180081`** | **USB 侧线缆已被识别并占用** |
| 目标树 | `targets` → **空** | **FPGA TAP 未枚举** |
| USB 侧旁证 | `USB Serial Converter`(FTDI `VID_0403&PID_6014`) 状态 OK；`COM4`(CP210x) 在线 | 线缆与串口在系统层面正常 |

**判读**：外置 **Digilent JTAG-HS1** 探针（S/N `210512180081`）已插在 USB 且被 hw_server 认领；但排线另一端未使 FPGA TAP 出现在链上。最可能：① 探针**排线未插稳/未插到板卡 JTAG 排针**（或 Pin1 反向）；② 板卡**只有 USB 供电、FPGA 核心电源未上**（DC 适配器/电源开关）；③ JTAG 链被复位保持。

## 3. 未执行与无副作用声明

- **未执行**：位流下载、ELF 下载与运行、`0x503D` 写入与回写、叠框出图、截图/照片、FPS/延迟实测、G3。
- **无副作用**：未改动板卡配置、未烧录 QSPI、未改他人工作树；每次探测后清理**本进程产生的** `hw_server`，本 run 收尾**无** `hw_server`/`xsdb`/`vivado` 驻留。
- 发现并记录：v12 应用**不自动恢复** `0x503D`（源码 `S3_DIAG9_ORDER=NOT_RESTORED`）⇒ S5-T01 将在自建 P1 应用内**显式写回 `0x00`**，不依赖现有 ELF。

## 4. 需人工确认（一步）

1. **JTAG-HS1 的排线**是否插在 AX7020 的 JTAG 排针上并插稳（与阶段3/2B 使用同一排针与方向）。
2. **板卡电源**：DC 适配器是否接好、电源指示灯是否亮（USB 供电不足以点亮 FPGA 核心）。
3. （如需视觉证据）HDMI 显示器是否连好。

完成后我会立即重跑链探测；一旦 `targets` 非空，即按运行书执行：冻结灰度位流 + v12 图案 → 只读转储核对 → 构建并下载 P1 叠框应用做注入验收。

## 5. 证据文件

- `hardware_gate.json`、`console/gate_stdout.txt`
- `console/jtag_probe_powered.txt`（上电后探测）、`console/jtag_chain_query2.txt`（**线缆已识别/目标为空**的关键证据）
- `console/xsdb_cmd_dump.txt`、`console/jtag_chain_query.txt`
- `run_manifest.json`（哈希绑定、命令与真实退出码、限制、未执行项）