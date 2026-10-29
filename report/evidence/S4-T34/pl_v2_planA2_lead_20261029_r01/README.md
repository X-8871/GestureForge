# PL v2 planA2（lead 亲自执行）：4 拍 + (ONE24 - dy_q) 前移，2026-10-29 10:10–10:35

## 背景
Workbuddy 4 拍版（r3 提交 c646ee7）100 MHz WNS = -1.395，top10 全在拍3 列插值：
`p_dy_q_reg -> 2*DSP48E1 + CARRY4x16 -> p_vq24_reg`（11.287 ns），其中 `ONE24 - dy_q` 的 24 位减法占 4 级 CARRY。
按批准的方案 A 执行（Wong 2026-10-29 指令：由 lead 自己仿真综合，Workbuddy 停手）。

## 改动（只 3 处，算术不变）
1. 新增 `logic [24:0] p_dy_inv_q;`
2. 拍1 沿同一 always_ff 增加 `p_dy_inv_q <= ONE24 - {1'b0, dy_q};`（行级常量，数值/位宽不变）
3. `v_q48 = (p_dy_inv_q * p_top24) + ({1'b0, p_dy_q} * p_bot24);`（原式 `((ONE24 - ...) * p_top24) + ...`）

## TB 等价（lead 本机跑，真实退出码）
| TB | xvlog/xelab/xsim | RESULT |
|---|---|---|
| engine_v2 | 0/0/0 | pass=1 mismatch=0 cycles=**2,655,174**（与 4 拍版**完全相同**）、FNV dut==gold=`0x39a2a8950a11322e` |
| v2_axi | 0/0/0 | pass=1 mismatch=0 cycles=2,676,472、ars=2073、4k_viol=0、FNV 相同 |
| v2_axis | 0/0/0 | pass=1 mismatch=0 cycles=2,713,979、tlast=1 tuser=1（该 TB 无 FNV 仪表） |

⇒ A 不改拍数 ⇒ cycles 不变，符合预期；三个 TB 全部等价通过。

## 综合（synth_design，仅引擎，100/150 MHz）
| 时钟 | WNS | WHS | LUT | FF | DSP | BRAM |
|---|---|---|---|---|---|---|
| 100 MHz | **-0.279**（前版 -1.395） | +0.125 | 2,119 | 404 | 13 | 0 |
| 150 MHz | -3.612 | +0.125 | — | — | — | — |

新 top 路径已从拍3 移走：`oy_reg_rep[5]/C -> rd_addr_reg[0]/D`（data path 10.142 ns；logic 5.861 + route 4.281）。
⇒ 拍1（地址/坐标）成为新瓶颈；列插值拍已干净。

## 判定与边界
- 100 MHz 综合仍差 **0.279 ns（2.8%）**，**不宣称时序收敛**；
- 是否可接受由实现（place/route）判定：综合无物理优化、route 估计保守；
- 边界：离线综合，未实现/未布线、未出 bit、未上板；不主张 G3/G4/G5。