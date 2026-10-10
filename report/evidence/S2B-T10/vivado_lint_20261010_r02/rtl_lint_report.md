# S2B-T10 第一次兼容修正的 Vivado lint

时间：2026-10-10（UTC+8）。Vivado 2026.1 Build 6511674，top 为 `s2b_hp0_word_adapter`，器件 `xc7z020clg400-2`。独立 Tcl 会话读取本目录的实际 SHA 绑定源码快照。执行 `synth_design -top s2b_hp0_word_adapter -part xc7z020clg400-2 -lint -file $lint_report_file`，原生退出码 0，5.891 秒，报告峰值内存 1330.828 MB。

## 实际消息

直接 canonical CSV 共一行，与原始 `Total of 1 linter message(s) generated` 一致：ASSIGN-5、WARNING、`lowest_lane`、bit0、adapter 行74。0 CRITICAL、0 ERROR；没有 INFO 严重性的 lint violation。原始工具 INFO 日志不是额外 violation。普通文件读取展示 CSV 后由总控逐行核对，原因是本环境没有技能所述 read_file 工具；未用脚本分组、未解析 ASCII 表格。

| 规则 | 数量 | 占比 | 严重性 |
|---|---:|---:|---|
| ASSIGN-5 | 1 | 100% | WARNING |

受影响文件只有 `source_snapshot/s2b_hp0_word_adapter.sv`，行74。r01 的 ASSIGN-1、ASSIGN-2、ASSIGN-6 已不出现在本 Run CSV 中；不改写 r01 原件。

## 已读取的真实代码与关闭建议

函数已有默认赋值3和低三个 lane 的优先分支，仍被该工具报告 bit0 未赋值。本报告保留工具诊断，不凭仿真通过宣布 lint 消息不存在。依据已读取的 `resolution/ASSIGN-5.md`，使用完整驱动原则；删除 helper，在现有组合块直接给 next_lane 完整赋值，保持默认 lane3、lane0→2 优先序。

```diff
-        next_lane = lowest_lane(q.remaining[2:0]); // 删除仍被工具报告的 helper 调用。
+        next_lane = 2'd3; // 完整默认驱动，非零 remaining 的剩余情况选 lane3。
+        if (q.remaining[0]) next_lane = 2'd0; // 保持 lane0 第一优先。
+        else if (q.remaining[1]) next_lane = 2'd1; // 保持 lane1 第二优先。
+        else if (q.remaining[2]) next_lane = 2'd2; // 保持 lane2 第三优先。
```

这是针对当前唯一诊断的修改建议；不改变准入规则、物理地址、事务账本或恢复语义，不 suppression、不 waiver。Developer 已获准修改并要求以新 Run 重跑全部 adapter 与 guard 检查，之后再做独立 lint 和新版独立 Reviewer 核验。

## 限制与状态

本 Run 检查命令成功，但 lint 关闭标准仍 FAIL，剩余一项未关闭。未进行完整综合/布局布线、正式时钟/XDC、CSR/HP/cache 集成或实物测试；不能发布接口冻结或 SAFE_TO_REUSE。源码和日志保存为本次修正的历史原件，不得用后续结果覆盖。技能的专用文件读取工具不可用与设计诊断分别披露，不作为忽略诊断的理由。
