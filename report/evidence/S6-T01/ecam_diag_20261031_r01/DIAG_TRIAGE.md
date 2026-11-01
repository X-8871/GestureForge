# E-cam 诊断窗结果（复位修复验证）

- RunId：`ecam_diag_20261031_r01`；时间 2026-10-31 12:54:32–12:55:57（UTC+8）
- 身份：P3r **build3**（`648f3156…` / XSA `1284f637…`）；诊断 ELF `f224f5e5…`（328,460 B）
- 结论：**ECAM_DIAG_FAIL**（复位修复成功，但 I2C 探测未通；按 lead 规则**不进入窗口 2**）

## 1) 复位修复 —— **成功** ✅
```
CAM: rst pin before=0x0 (reg 0x41200000)
CAM: reset seq: assert(0) 500 ms -> release(1) 500 ms -> release(1) 500 ms
CAM: rst pin after=0x1 (低有效: 1=释放)
```
- 停核快照：**0x41200000 = 0x00000001** ✅（旧版本一直为 0）

## 2) I2C 探测 —— **失败（起步异常）** ❌
```
CAM: i2c clk_assumed=111111115 div=63 cr=0x3F07 sr=0x0 rc=0
CAM: i2c clk_assumed=100000000 div=63 cr=0x3F07 sr=0x0 rc=0
CAM: i2c clk_assumed=50000000  div=63 cr=0x3F07 sr=0x0 rc=0
CAM: i2c clk_assumed=166666667 div=63 cr=0x3F07 sr=0x0 rc=0
CAM: i2c clk_assumed=133333333 div=63 cr=0x3F07 sr=0x0 rc=0
CAM: i2c clk_assumed=40000000  div=63 cr=0x3F07 sr=0x0 rc=0
CAM: probe addr7=0x3C w8=0x78 r8=0x79 ack=0 isr_addr=0x0 isr_data=0x0 rc=-2
CAM: chipid reg0x300A=0x00 reg0x300B=0x00
CAM: FAIL sub=-2 stage=addr/ack reg=0x300A val=0x300A isr=0x0
CAM: FAILED rc=-11（I2C/覆盖表/回读/S2MM 配置阶段失败）→ 继续显示测试图
```
- 按判读规则：`rc=-2 & isr_addr=0` ⇒ **I2C 起步异常**（不是 NACK 0x10 的"器件无响应"）
- `ack=0`、`isr_addr=0x0`、`isr_data=0x0`、`sr=0x0` ⇒ 传输未真正启动/未产生中断状态位
- 6 条 `clk_assumed` 行覆盖 40–166.7 MHz 假设，**div 恒 63**、`cr=0x3F07`、`sr=0x0`

## 3) 停核快照（只读）
| 寄存器 | 地址 | 值 | 说明 |
|---|---|---|---|
| cmos_rstn | 0x41200000 | **0x00000001** | ✅ 复位已释放 |
| CAM_GPIO | 0x43C70000 | 0x00000000 | 帧计数/控制未启动 |
| camera VDMA CR | 0x43C60000 | 0x00000000 | 未配置（应用未到 S2MM 阶段） |
| camera VDMA SR | 0x43C60004 | 0x00000000 | — |
| display VDMA CR/SR | 0x43C40000/04 | 0x00010002 / 0x00011001 | 正常 |
| 2B CSR | 0x43C00000 | 0x53324250 | AXI 正常 |

## 4) 判据
| 项 | 结果 |
|---|---|
| D1 rst after=0x1 | **PASS** |
| D2 reset seq（两次 release(1)） | **PASS** |
| D3 i2c clk 行 ≥1（6 条） | **PASS** |
| D4 probe ack=1 | **FAIL**（ack=0, rc=-2, isr_addr=0） |
| D5 chipid=0x5640 | **FAIL**（0x0000） |
| D6 无 CAM: FAIL | **FAIL**（sub=-2 stage=addr/ack） |

## 5) 下一步建议（给 video-sw / video-bd）
1. **确认 SCCB 走哪条总线**：PS I2C0/I2C1（EMIO）还是 PL 软 I2C；打印控制器基址与 `CR/SR/ISR` 全寄存器值（现在只有 cr/sr，缺 ISR）
2. **总线电平静态检查**：SCL/SDA 空闲应为高；若被拉低 ⇒ 上拉缺失/器件短路；建议 APP 加"GPIO 模式读 SCL/SDA 电平 + 9 个 SCL 时钟 bus-recovery"诊断
3. **XCLK 是否起振**（相机模组 24 MHz；若由 PL 供时钟，确认 P3r 中该时钟已使能）
4. **相机供电/PWDN**：CAM_GPIO=0 时确认模组电源使能位是否需要软件置 1（若 GPIO 里有 pwdn/power 位，诊断版应先设置再探测）
5. `div=63 恒` 提示分频计算可能被固定/钳位，结合真实 I2C 输入时钟（PS I2C 为 111.111 MHz）核对 `clk_assumed=111111115` 那条是否生效
6. 复位修复已确认（rst=1），下一版只需聚焦 I2C 起步；**未进入窗口 2（修复版相机 ELF）**，因其前提 `chipid=0x5640` 未满足

## 6) 收窗
- 正常收窗（teardown PASS、零残留、board_state clean）
- 未运行窗口 2 `ecam_camera_20261031_r02`（按 lead 条件：chipid=0x5640 才跑）