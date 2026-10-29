# 探针版长跑应用（首次 CSR 访问前打印 SLCR）—— 2026-10-29

## 目的
r06 现象：UART 打印到 `LONGRUN STEP=1 sw_preproc rc=0` 后 1100 s 零输出，应用停在**首次 CSR 访问（`s4d_is_idle()` 读 0x00C）**。
JTAG 侧无法区分"PL 无时钟 / 位流未配置 / 从口复位未释放"，因此把探针放进**应用内部**：
PS 读 SLCR 不依赖 PL，即使 PL 挂死也能打印。

## 改动（只读探针，不改任何判据）
在 `s4d_longrun_selfcheck()` 中、`prc != 0` 检查之后、**首次 `s4d_is_idle()` 之前**，打印：
- `0xF8000900` LVL_SHFTR_EN（PS↔PL 电平转换使能）
- `0xF8000170` FCLK_CTRL0（PL 时钟）
- `0xF8000120` APER_CLK_CTRL（外设时钟门控）
- `0xF8000240` FPGA_RST_CTRL（PL 软复位）

输出格式：`LONGRUN PROBE slcr shftr=0x%08x fclk0=0x%08x aper=0x%08x fpga_rst=0x%08x`

## 构建（逐字复用 longrunK 的 flags / specs / BSP / 链接脚本）
- 源码：`vitis/stage4/ps/s4d_ps_app.c`（本轮修改）
- 产物：`s4d_ps_app_sw0_longrunP.elf`
- SHA-256：**`faa399b268e35a2f7d0bef7ecbcb38ebef444abdd7fb0a50351db46e3d6def2c`**
- 编译/链接真实退出码：compile_app=0、compile_pre=0、link=0、size=0
- `strings` 命中 `LONGRUN PROBE` 1 次（探针字符串确实进了 ELF）

## 判读规则（窗口执行时）
| PROBE 值 | 含义 | 下一步 |
|---|---|---|
| `shftr` 低 4 位 ≠ 0xF | 电平转换未开 | 先置 `0xF8000900=0x0F` 再跑 |
| `fclk0` 的 FCLK0 使能位 = 0 | PL 无时钟 | 查 ps7_init/时钟配置 |
| `rstd`（FPGA_RST_CTRL）≠ 0 | PL 复位未释放 | 写 `0xF8000240=0` |
| 三者都正常但 CSR 读仍挂 | 位流/PL 从口问题 | 查位流配置与 DevCfg |

## 边界
离线编译；未上板；`ENABLE=0`；不主张 G3/G4/G5；不改任何验收判据。