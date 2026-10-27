# S5-T02 板上动态映射（窗口 A） RunId `s5t02_board_dynamic_map_20261027_r01`

> 数字均由本包产物派生：`board_verify.json`（对拍）、`console/logs/*`（UART/回读/转储）、ELF 哈希。
> **本包 = 阶段5 硬件窗口（Wong 2026-10-27 12:26 授权；门 `hw_gate_20261027_r03` = GO）**。

## 1. 结论（逐项）
| 项 | 状态 | 依据 |
|---|---|---|
| **B1 板上几何 ⇄ 冻结参考** | **PASS（数值层）** | 板上 UART `S5DM_B` 6 用例 22 框：矩形（对参考**与**预计算表）、边框像素数、标签锚点、placement **110/110 全一致，0 失败** |
| **B2 过期边界** | **PASS** | 用例6：`S5DM id=6 nbox=0 stale=1 reason=stale_flag`（过期即 0 框、状态如实）；阈值常量 `stale_limit_ns=200000000` |
| **B4 HUD 13 字段** | **部分** | 板上 `S5_P1_HUD_FIELDS=13`、`capture_fps=NA inference_fps=NA inference_time_ns=NA`；**逐字段取值**未在本包核对（需画面回读/目视） |
| **B5 计数单位** | **NOT_RUN** | 本包为 6 用例循环模式，未跑 120 帧计数流 |
| **B1 像素级叠加（真画进缓冲）** | **未确认（NOT_RUN）** | 显示缓冲在期望边框列上取到的是背景值而非类颜色；且既有解码器 `decode_mrd_rows.py` 的期望**早于当前应用修订**（期望红框 `(64,64,255)`、白角、平滑斜坡 252 等），其 3 PASS/10 FAIL **不可用于**判定本版本 ⇒ 需先修判据/定位后再下结论 |
| HDMI 真彩目视/拍照 | **NOT_RUN** | 需人工拍照（摄像头模块待重购）；受连接判据未重做 |
| 30 分钟板上长跑（B6）/ T5-10 板上回归 | **NOT_RUN** | 本轮未执行 |
| 真实回放上板链路 | **NOT_RUN** | 阶段4 冻结件仅允许离线回放消费；板上真实回放还需八类门禁（记录 0/8） |

## 2. 部署与真实退出码
| 步骤 | 结果 |
|---|---|
| 交付构建（默认路径，未开开关） | `MAKE_EXIT=0`，ELF `085a02dc…`（**与打补丁前逐字节相同** ⇒ 既有验收路径未被改动） |
| 动态映射构建（`-DS5_DYNAMIC_MAP=1`） | `MAKE_EXIT=0`，ELF `25be3c4d…`（356420 B） |
| 单用例5 构建（`-DS5_DYNAMIC_MAP=1 -DS5_SINGLE_CASE=5`） | `MAKE_EXIT=0`，见 `console/logs` 与 ELF 清单 |
| JTAG 下载（PL bit + ps7_init + dow ELF + run） | `T03_DL_ALL_DONE=1`，`XSDB_EXIT=0`（两次部署均 0） |
| 显示缓冲点回读 / 整行转储 | `read_exit=0` / `dump_exit=0`（寄存器：MM2S_CR=00011001、FW1=0x2D0、FW2=0xF00） |
| 既有像素解码器 | `decode_mrd_rows.py` **exit 1（3 PASS/10 FAIL）**，期望过期，**不作为本版本判据** |

## 3. 输入/工具绑定
- PL 位流：`design_1_wrapper.bit` SHA-256 `44e609cc…`（阶段3 provisional freeze，**易失下载，未烧 QSPI**）
- XSA：`90e1bdee…`（与阶段4 契约绑定一致）
- 参考实现：`verification/s5_display_geometry_reference.py` SHA-256 `dfca9adf9f065746…`
- 标签尺寸口径：**应用侧指标**（宽=app: w=6*2*len(label), h=7*2）；与离线对拍器的渲染层字体口径不同 ⇒ 两者 anchor 不可混比
- 源码基线：w5 `38adca024683…`

## 4. 限制与 NOT_RUN（不得外推）
- 板上时钟为**固定虚拟基准**（capture/result/commit），**非实测**采集/推理时间；HUD 的 `capture_fps/inference_fps` 必然 NA。
- 本轮**未重做受连接判据**（部署身份逐字符核对、真彩目视）⇒ 不得引用旧目视结论。
- 本包只证明**几何数值一致性**；**像素级叠加与 HD 画面未确认**。
- **§4.5/§7.3 未关闭**；板级 B1（像素层）/B4（逐字段）/B5/B6/B7–B10、真实回放上板、摄像头路径、T5-10 均 **NOT_RUN**；**G0/G1/G3/G4/G5 判定不归本包**。
