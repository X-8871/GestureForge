# XDC 编写指南（阶段5 HDMI 显示链 / S5-T01）

> 适用范围：本阶段及后续**所有** Vivado 工程（P3b 起强制引用）。
> 建立依据：2026-10-30 P3a+ 构建中实测到**两个**会让"约束静默失效"的陷阱，
> 代价是一整轮 16 min 的构建结论作废。本文把这两条固化成规则 + 可执行自检。

---

## 0. 三条硬规则（TL;DR）

1. **XDC 文件里只写声明式命令**，禁止 `if/foreach/for/while/proc/set/catch/eval/expr/lappend`。
2. **需要条件判断 → 写进 Tcl 脚本**（`-source` 的构建脚本，或 impl 的 `STEPS.OPT_DESIGN.TCL.PRE` 钩子），不要写进 XDC。
   ⚠️ `set_clock_groups` 这类要按名字找时钟的约束，**别放 XDC**（用户 XDC 早于 IP/BD 时钟约束被处理，实测会拿到空集合）。
3. **构建日志里不允许出现** `[Designutils 20-1307]` 或 `[Vivado 12-4739]`；并必须用 `report_clocks` 核对期望时钟真实存在。
   （注意：`PROCESSING_ORDER {LATE}` **实测不能**修复第 2 条的 `12-4739`，见 §2。）

构建前自检（必须）：

```powershell
python check_xdc_declarative.py <你的.xdc>
# 退出码 0 = 100% 声明式；1 = 有控制流（会静默失效）；2 = 输入错误
```

---

## 1. 陷阱一：XDC 不支持控制流，且**静默忽略**

### 实测现象
第一版 `p3a_video.xdc`（保留为反向证据 `p3a_video_xdc_v1_rejected.xdc`）用 `if`/`foreach` 做
"时钟是否已派生"的守卫和"按时钟周期分桶"的时钟组：

```
CRITICAL WARNING: [Designutils 20-1307] Command 'if' is not supported in the xdc constraint file.      [p3a_video.xdc:18]
CRITICAL WARNING: [Designutils 20-1307] Command 'foreach' is not supported in the xdc constraint file. [p3a_video.xdc:34]
（共 10 条）
```

### 危害（为什么最危险）
- **不是 ERROR，构建照常完成**，只有 CRITICAL WARNING 刷屏；
- 被拒的命令**整条跳过**：守卫里的 `create_clock` 没执行、`foreach` 里的 `set_clock_groups` 根本没被调用、`set_false_path` 没加；
- 时序报告**照样有数字**（Vivado 会给 MMCM 输出自动派生时钟），于是极易误判"约束已生效"。

### 规则与替代写法
| 想做的事 | ❌ 错误（XDC 里） | ✅ 正确 |
|---|---|---|
| 时钟存在才创建 | `if {[llength [get_clocks ...]] == 0} { create_clock ... }` | 直接把时钟**写死**（工程是确定性的）：`create_clock -period 13.4737 -name xxx [get_ports yyy]` |
| 按时钟周期分桶 | `foreach c [get_clocks] { ... }` | 用**确切时钟名**展开：`set_clock_groups -asynchronous -group [get_clocks clk_a] -group [get_clocks clk_b]` |
| 端口可能不存在才加假路径 | `if {[llength [get_ports ...]] > 0} { set_false_path ... }` | 直接 `set_false_path -to [get_ports {...}]`（端口一定存在；不存在就让它报错，早失败好过静默） |
| 需要真正的条件逻辑 | — | 移到 **Tcl 钩子**：`set_property STEPS.OPT_DESIGN.TCL.PRE <hook.tcl> [get_runs impl_1]` |

### 反向证据
- `D:\tmp\lead\p3a_video_20261030_r01\p3a_video_xdc_v1_rejected.xdc`（v1，22 处控制流）
- `out\xdc_static_check.log`（自检器对 v1 报 `FAIL -- 22 control-flow/unknown command(s)`）

---

## 2. 陷阱二：用户 XDC **早于** IP/BD 的时钟约束被处理

### 实测现象
改成声明式后，这一行仍报 6 条 Critical Warning：

```
CRITICAL WARNING: [Vivado 12-4739] set_clock_groups:No valid object(s) found for
  '-group [get_clocks -include_generated_clocks clk_fpga_0]'.  [p3a_video.xdc:38]
（clk_fpga_1、clk_out1_s4d_p3a_clk_wiz_0_0 各 2 条）
```

### 根因
`clk_fpga_0/1` 由 **PS7 IP 的约束**创建、`clk_out1_*` 由 **MMCM 自动派生**；
而用户 XDC（fileset `constrs_1`）默认**先于**这些 IP/BD 约束处理，此刻 `get_clocks` 返回空
→ 三个 `-group` 全空 → 时钟组未建立（但构建不失败）。

### 修法（**2026-10-30 P3b 实测修正**：做法 A 无效，请直接用做法 B）

- **做法 A（`PROCESSING_ORDER {LATE}`）——⚠️ 实测无效，不要依赖**：
  在 P3b 中已按此设置，构建日志仍出现 6 条 `[Vivado 12-4739]`（`p3b_tmds.xdc:34`），
  即 `get_clocks` 仍取到空集合。**结论：LATE 不足以让用户 XDC 排到 IP/BD 时钟之后。**
- **做法 B（推荐，一定有效）**：把 `set_clock_groups` 放进 **impl 钩子**（Tcl 允许控制流，且此刻设计已 link、时钟齐全）：
  ```tcl
  set_property STEPS.OPT_DESIGN.TCL.PRE "$base/clk_groups_hook.tcl" [get_runs impl_1]
  ```
  钩子内可用 `foreach`/`if`，并建议打印 `P3B_HOOK clock_groups APPLIED` 作为日志证据。
- **做法 C（事后分析，用于已验证位流的"修正数字"）**：在已路由 DCP 上补加时钟组再重算
  （P3b 已这么做，见 `post_clkgrp_p3b.tcl` / `out\post_clkgrp.log`）：
  ```tcl
  open_checkpoint <impl_1>/top_p3b_routed.dcp
  set_clock_groups -asynchronous -group [get_clocks clk_fpga_0] -group [get_clocks clk_fpga_1] -group [get_clocks clk_out*_<bd>_clk_wiz_0_0]
  update_timing -full
  report_timing_summary -file timing_post_clkgrp.rpt
  ```

### P3b 的实测结论（可直接引用）
在 P3b 上补加四域异步组后 `WNS/WHS` **完全不变**（0.544 / 0.022 ns）→
**关键路径不跨时钟域，异步组缺失只影响"跨域路径是否被分析"，不影响报告数字**，
所以缺组时得到的数字是**保守下界**，可用于达标判定。

### 影响判读（重要）
异步组缺失 = 跨域路径仍按**同步**分析 = 约束**更严格**。
所以 P3a+ 的 `WNS +0.041 / WHS +0.043` 是**保守下界**，不是"放宽后"的数字。

---

## 3. 构建后必须做的时钟自检

```tcl
# 在 open_run impl_1 之后
report_clocks -file $out/clocks_route.rpt
report_clock_interaction -delay_type min_max -file $out/clk_interaction_route.rpt
report_clock_utilization -file $out/clk_util_route.rpt
```

判读要点：
1. `clocks_route.rpt` 里**每个期望时钟都要出现**，且周期正确；
2. 若某时钟是被 `clk_wiz` MMCM 输出驱动，应能看到属性含 `G`（generated）；
3. **"Async" 关系**要能在 `report_clock_interaction` 里体现（未被异步声明时会出现
   "Timed / Partial False Path" 之类的交叉分析）；
4. 日志里 `grep '12-4739'` 必须为空。

### P3b 的期望值（构建后逐条核对）
| 期望时钟 | 周期 | 来源 | 如何核对 |
|---|---|---|---|
| `clk_fpga_0` | 20.000 ns（50 MHz） | PS7 FCLK0 | `clocks_route.rpt` |
| `clk_fpga_1` | 10.000 ns（100 MHz） | PS7 FCLK1 | 同上 |
| `clk_out1_<bd>_clk_wiz_0_0` | **13.474 ns（74.21875 MHz）** | MMCM CLKOUT0（像素域） | 同上（属性应含 G/A） |
| `clk_out2_<bd>_clk_wiz_0_0` | **2.6945 ns（371.09375 MHz = 5×）** | MMCM CLKOUT1（OSERDESE2 CLK） | 同上；P3b 中该时钟**必须存在**（P3a 因未连接被 trim） |
| `clkfbout_<bd>_clk_wiz_0_0` | 80.000 ns | MMCM 反馈 | 可忽略 |
| 时钟组 | — | 50 / 100 / (像素+5× 同组) | `grep '12-4739'` 为空 + `clk_interaction` 显示 async 关系 |

---

## 4. 新 XDC 上线清单（复制到每个新工程）

- [ ] 全程声明式：`python check_xdc_declarative.py <xdc>` 返回 0
- [ ] **`set_clock_groups` 不要写在 XDC 里**：改放 impl `STEPS.OPT_DESIGN.TCL.PRE` 钩子（`PROCESSING_ORDER LATE` 实测无效）
- [ ] 构建日志 `grep '20-1307'` 为空
- [ ] 构建日志 `grep '12-4739'` 为空（若不为空：按 §2 做法 B/C 处理，并在报告里说明数字是否为保守下界）
- [ ] `report_clocks` 里期望时钟齐全、周期正确
- [ ] 引脚：只对 `_p` 端设 `PACKAGE_PIN`，`_p/_n` 都设 `IOSTANDARD`（差分 N 由 P 推出）
- [ ] 引脚与电平**逐个引用厂商 XDC 的文件路径与行号**，不臆造
- [ ] 无下游器件的输出**不要编造 output_delay**：用 `set_false_path` 并写明理由，接入真实器件时删除

---

## 5. 本文件配套资产

| 文件 | 用途 |
|---|---|
| `check_xdc_declarative.py` | 声明式自检器（退出码 0/1/2），构建前必跑 |
| `out\xdc_static_check.log` | 自检器对 [P3a v1（反向证据）/ P3b / P3a v2] 的实际输出 |
| `p3b_tmds.xdc` | 按本指南写的示范：声明式 + TMDS 引脚引用厂商行号 |
| `post_clkgrp_p3b.tcl` + `out\post_clkgrp.log` | **做法 C** 的实例：路由后补加时钟组并重算时序（P3b 实测数字不变） |
| `P3B_BUILD_REPORT.md` | P3b 构建结果（含 §6.2 "12-4739 仍存在"的实测记录） |
| `D:\tmp\lead\p3a_video_20261030_r01\p3a_video_xdc_v1_rejected.xdc` | 陷阱一的反向证据（勿复制使用） |
| `D:\tmp\lead\p3a_video_20261030_r01\P3A_BUILD_REPORT.md` §6/§7 | 两个陷阱的完整实测记录 |