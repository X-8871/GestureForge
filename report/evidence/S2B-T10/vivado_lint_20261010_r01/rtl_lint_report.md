# S2B-T10 候选 RTL 的 Vivado lint 原始检查

时间：2026-10-10（UTC+8）。Vivado 2026.1 Build 6511674；器件 `xc7z020clg400-2`；明确 top `s2b_hp0_word_adapter`，仅包含 adapter 与请求准入模块的 SHA 绑定快照。命令为 `synth_design -top s2b_hp0_word_adapter -part xc7z020clg400-2 -lint -file $lint_report_file`，原生退出码 0，实际 5.882 秒，报告峰值内存 1333.660 MB。此为 lint，不是完整综合、时序或实物验证。

## 原始结果与核对

canonical CSV 是 Vivado 2026.1 直接产生的 `linter.csv`，共 4 行，与原始输出 `Total of 4 linter message(s) generated` 一致。本环境没有技能所述 `read_file` 工具，因此通过普通文件读取展示 CSV 原文，由总控逐行核对；未用 Tcl 或脚本解析/分组报告，未解析 ASCII 表格。未增加报告之外的诊断。3 项 WARNING、1 项 CRITICAL WARNING，零 ERROR；工具退出码 0 不表示这些问题关闭。

| 规则 | 数量 | 占比 | 严重性 |
|---|---:|---:|---|
| ASSIGN-1 | 1 | 25% | WARNING |
| ASSIGN-2 | 1 | 25% | CRITICAL WARNING |
| ASSIGN-5 | 1 | 25% | WARNING |
| ASSIGN-6 | 1 | 25% | WARNING |

文件：adapter 三项（行 280、74、59），guard 一项（行 57）。所有行号指本 Run 的 source_snapshot 原件，不是后续修正版。

## 四项诊断及关闭建议

### ASSIGN-2：显式统一无符号 lane 计算

guard 行 57 的实际表达式混合无符号地址与有符号 `int lane` 的定宽 cast。lane 仅遍历 0..3，但该类型问题需要消除。应显式构造 33-bit 无符号 lane，继续保留 33-bit 地址加法和原范围检查。

```diff
-                lane_addr = {1'b0, mem_addr} + 33'(lane); // 删除混合符号表达式。
+                lane_addr = {1'b0, mem_addr} + {31'd0, lane[1:0]}; // lane 为 0..3，显式无符号扩展。
```

### ASSIGN-1：捕获已核验地址并保持内部计算精度

adapter 行 280（工具同时指出行 145）重新进行地址平移及 lane 相加，工具给出最大 34-bit 而仅使用 32-bit。建议实际捕获 guard 返回的物理地址，内部足够位宽计算 lane，范围合法时才使用接口位宽；不得通过去掉 guard 或静默 wrap 关闭警告。

```diff
-                d.araddr = q.addr + 32'h10000000 + // 删除重复平移的加法链。
-                    ((q.rmask == 4'b1111) ? 32'd0 : {30'd0, next_lane}); // 删除隐式截至 32-bit 的运算。
```

### ASSIGN-5：函数结果显式完整赋值

adapter 行 74 的函数使用 SV early return，Vivado 报函数 bit0 未设置。建议改为对函数结果有默认值及互斥分支的完整赋值，优先次序仍为 lane0→lane3，功能不变后重跑全部 mask。

```diff
-        if (mask[0]) return 2'd0; // 删除工具报未赋值的 early return 写法。
-        if (mask[1]) return 2'd1; // 删除 early return 写法。
-        if (mask[2]) return 2'd2; // 删除 early return 写法。
-        return 2'd3; // 删除 early return 写法。
+        if (mask[0]) lowest_lane = 2'd0; // 显式赋值完整函数返回值。
+        else if (mask[1]) lowest_lane = 2'd1; // 保持 lane1 次优先。
+        else if (mask[2]) lowest_lane = 2'd2; // 保持 lane2 次优先。
+        else lowest_lane = 2'd3; // 完整覆盖所有剩余输入。
```

### ASSIGN-6：使用 guard 产生的物理地址

adapter 行 59 的 `logic [31:0] unused_guard_address;` 实际被赋值但未读取。建议把此输出用于请求捕获后的物理账本，消除地址重复计算；它和 ASSIGN-1 一并验证。此项是未使用信号诊断，不单独宣称运行结果错误。

```diff
-    logic [31:0] unused_guard_address; // 删除不读取的命名与使用方式。
+    logic [31:0] guard_address; // 捕获并实际用于已核验的物理事务地址。
```

## 状态与验证要求

已读取 ROSS 技能及 `resolution/ASSIGN-1.md`、`ASSIGN-2.md`、`ASSIGN-5.md`、`ASSIGN-6.md`；按其显式类型、完整赋值和未使用信号修复原则处理，不采用 warning suppression 或 waiver。最高优先关闭 ASSIGN-2，其余一并修复。Developer 已获准仅做兼容性修改；必须保存新 Run 原件、重跑请求准入 70,736 条及 adapter 全部向量/异常场景，再重新运行 Vivado lint 并独立审查。此 Run 保留原始问题，不能改写为后续零警告结果。没有发布 SAFE、接口冻结或板上通过。
