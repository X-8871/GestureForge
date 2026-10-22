# S5-T01 硬件放行与板卡状态核验 RunId `s5t01_release_20261022_r01`

- 时间（UTC+8）：2026-10-22 13:35
- 结论：**放行依据成立（门禁 `GO`，exit 0）**；但**板卡 JTAG 链未枚举（两次独立探测均为 0 目标）**，故**尚未执行任何下载/写寄存器**；已向 Wong 请求上电确认。
- 未执行：位流下载、ELF 下载、`0x503D` 写入/回写、叠框出图、截图/照片、FPS/延迟实测、G3。

## 1. 放行依据（替代让出，已留痕）

| 项 | 内容 |
|---|---|
| 门禁结果 | `decision=GO`，`reasons=[]`，`release_basis=operator_authorization`，退出码 **0** |
| 授权 | `authorized_by=Wong`；原文：“用户 2026-10-22 13:25 明确告知：可以上板，codex 已经暂停（2B 会话已停）。作为替代让出依据；仍要求无硬件进程、无锁。” |
| 信箱状态 | 仍**无**新的书面让出（最近占用通知 `CDX-20261022-006`）；DSH `DSH-20261022-009` 已请求让出。故本轮以用户显式授权为让出依据，**不伪造信箱记录**。 |
| fail-closed 检查 | 硬件/EDA 进程：**0**（枚举成功 `hardware_process_enumeration_ok=true`）；六棵树 `index.lock`：**无** |

## 2. 冻结产物核验（dbdf 只读盘，未修改）

| 产物 | 实际 SHA-256 | 与冻结声明 |
|---|---|---|
| 部署位流（标准亮度灰度）`t04_stdluma_20261022_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit` | `44e609cc…c4afb` | **匹配** `44e609cc…`（阶段3 收尾清单） |
| XSA | `90e1bdee…b1c4` | **匹配** `90e1bdee…` |
| v12 彩条+冻结 ELF | `527a74fc…9845c5` | 阶段3 T14 v12 工具（含“使用前须确认硬件占用未让出”） |
| v11 取帧 ELF | `c01133b1…26c4` | 阶段3 T05 v11 |

- 备选位流（未用）：纯绿灰度 `2f72aaa4…`；其余（dual-msb 彩色 `30db09ba…`、SOF 基线 `7cb33068…`）仅留档。
- v12 应用的可编译工作区已定位（只读）：`dbdf/tmp/s3r06/t04_j11cmos2_elf_v12/elf_build/`（含 `display_demo.c`、`Makefile`、`lscript.ld`、BSP）——可作为 S5-T01 P1 叠框应用的基线（复制进本树后改造，**不改 dbdf**）。

## 3. JTAG 现场核验（只读，两次独立探测）

| 项 | 结果 |
|---|---|
| 探测 1（`jtag_probe.tcl`，含 `disconnect`） | 退出码 0；`targets` **空**（无目标） |
| 探测 2（`jtag_probe2.tcl`，简化、等待 2 s） | 退出码 0；`targets` **空**（无目标） |
| JTAG 线缆（USB） | **在线**：`USB Serial Converter`（FTDI）状态 OK |
| 串口 | **在线**：`Silicon Labs CP210x … (COM4)` |
| 残留服务 | 每次探测后核验并结束**我自己的**遗留 `hw_server`（PID 9800 自行退出；PID 8136 由我核实归属后结束）→ 收尾**无** `hw_server`/`xsdb`/`vivado` 进程（不驻留） |

**判读**：线缆与串口在场、服务无残留，但 JTAG 链 0 目标 ⇒ 最可能为**板卡未上电**（或板卡 JTAG 未处于可枚举状态）。**未做**任何上电/接线改动（属人工操作）。

## 4. 下一步（需人工一步）

1. **请 Wong 给板卡上电**（并确认 JTAG/USB 与 COM4 接法与阶段3/2B 使用时一致、HDMI 显示器已连）。
2. 上电后我一键执行：门禁复核（GO）→ 下载冻结灰度位流 + v12 图案 ELF → 读回 `0x503D` 与 VDMA 状态 → 只读转储帧缓冲核对图案 → 随后构建并下载 **P1 PS 软件叠框**应用做注入叠框验收。
3. 收尾：`0x503D` 写回 `0x00`、退出 `hw_server`（不驻留）、记录板卡恢复状态。

## 5. 证据文件

- `hardware_gate.json`（GO + 授权留痕）、`console/gate_stdout.txt`
- `console/frozen_artifact_hashes.txt`（四项冻结产物实际哈希）
- `console/jtag_probe.txt`、`console/jtag_probe2.txt`（两次探测原始输出）
- `run_manifest.json`（哈希绑定、命令与真实退出码、限制、未执行项）