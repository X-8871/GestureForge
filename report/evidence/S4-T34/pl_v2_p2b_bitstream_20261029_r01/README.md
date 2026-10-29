# P2b：4-D 合并位流（preproc + 2B 推理，smartconnect 控制面）与第三次 A/B

## 构建（lead 执行，2026-10-29 12:00–12:22）
设计：PS7(50 MHz、GP0、HP0/64bit) + smartconnect_ctrl(1S→2M：preproc CSR @0x43C10000/0x80、2B CSR @0x43C00000/0x10000)
+ smartconnect_data(2S→1M：preproc M_AXI_RD、infer M_AXI → HP0 0x0/1GB)；**不使用旧 `axi_protocol_converter`**。

| 项 | 结果 |
|---|---|
| BD validate | 通过（地址在 validate 前分配） |
| 时序 | **WNS +0.212 ns / WHS +0.036 ns**，`All user specified timing constraints are met` |
| 资源 | LUT **20,976**(39.4%)｜FF **8,682**(8.2%)｜DSP **147** |
| bit | `s4d_p2b.bit` 4,045,770 B，SHA-256 `47472d2db6e2a7cb5ff3ed2d0196c6dd5b3eb39f7b5ee7b30ed34254494a41e8` |
| XSA | `s4d_p2b.xsa` 317,623 B，SHA-256 `ddb65f19842bc928df7df3f3712012d695801dd7cd07b671c87f0e2e12c0385a` |

**构建踩坑**：① 2B 核 `infer_0` 的接口元数据 FREQ_HZ=50 MHz，与 PS7 100 MHz 冲突 ⇒ 位流改用 **50 MHz**（与 2B 冻结配置一致）；
② preproc wrap 的 FREQ_HZ 元数据同步改 50 MHz（仅元数据，不改逻辑）。

## 第三次 A/B（同一探针应用）
| 位流 | 结果 |
|---|---|
| P2a（仅 preproc，无 infer） | CSR 读**返回**，app fail-fast（前次窗口） |
| 2B 冻结位流（infer，旧转换器） | PROBE 行后**静默停住**（前次窗口） |
| **P2b（preproc + infer，smartconnect，无旧转换器）** | **仍然静默停住**（本次） |

⇒ **"旧 `axi_gp0_lite` 转换器导致挂死"的假设被否定**；目前相关性是：**只要 2B 推理核心在设计里，首次 CSR 读就挂**（P2a 无 infer 则正常）。

## 驱动顺序复测（失败尝试，如实记录）
用历史跑通过的 `stage_pspl_setup_and_load` 顺序（reset_stop → 0xA → program PL → 0xF → load init+app）复测 2B 位流 + 探针应用：
- reset/0xA/program/0xF 全 PASS（0xA/0xF 双读回通过）；
- `stage_load_app` 走 `base.load_elf`（内部 `rst -system -stop`）⇒ **系统复位会清 PL 配置**，且未先跑 `ps7_init` 等 DDR 初始化 ⇒ **30 s 内无横幅**、UART 0 行；
- 结论：该路径不适合本测试（不是应用/硬件失败证据）。历史窗口用的是 `load_elf_ddr`（先 init），顺序不同。

## 2B CSR 直读（挂死现场，JTAG）
`ID=0x53324250`、`STATUS=0x00000C05`（低 3 位 5 = **ERROR_SAFE**）、`error_code=0x010=1`、`0x008` 读触发 `Memory read aborted, Fault status 0x8`。

## 判断与下一步
- **已证**：转换器不是（唯一）原因；2B 核心存在时首次 CSR 读挂死；PL 从口对 JTAG 读正常；2B 核心上电即 ERROR_SAFE。
- **未证**：挂死的具体机制（2B CSR 读通路的内部等待 / PS 访问属性 / 核心侧状态）。
- **下一步**：构建"读前/读后各打印一行"的最小探针（`PROBE pre-read` / `PROBE read=<v>`），把"读本身挂"与"读到之后挂"分开；并在读前在应用内写 `0x008` 之前先读 `ID(0x000)` 确认基本读通路。
- 边界：离线构建 + 两个短窗口；未改判据；`ENABLE=0`；不主张 G3/G4/G5。