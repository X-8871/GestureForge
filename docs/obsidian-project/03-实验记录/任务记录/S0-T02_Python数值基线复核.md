---
type: guide
domain: embedded
status: active
created: 2026-09-10
updated: 2026-09-10
---

# S0-T02 Python 数值基线复核

状态：待开发。计划执行日 2026-09-11。已有历史 4 项测试通过，不代表本任务审查与验收已完成。

## 任务卡

目标：以现有代码完成一次有版本、有原始输出、有独立审查的 G0—G4 软件交付。无需板卡，不要求 Wong 重写代码。

规格唯一依据 [[02-方案设计/INT8乘加接口说明]]：4 项 signed INT8 点积，偏置 0，18 位累加，除以 256 最近整数舍入且中点远离零，再饱和到 [-128,127]。范围 -65024～65536。不是最终 CNN 量化规格。

输入：`verification/int8_mac_reference.py`、`verification/test_int8_mac_reference.py`、现有黄金 JSON。输出：基线复核日志、审查与验收记录。修改范围默认只有证据和本任务记录；测试失败需要修改代码时，按规范记录原因、回归和新提交，不扩展 RTL。

前置：Python 可运行、Git 状态明确；不依赖 S0-T01 的全部实物核验。基线提交执行时记录完整哈希，不能永久使用文档生成日的哈希。

## 验收矩阵

| 编号 | 方法 | 通过条件 | 证据 |
|---|---|---|---|
| PY-01 | 执行现有 unittest | 4 项测试通过、退出码 0 | 完整 stdout/stderr |
| PY-02 | 检查 Decimal 独立算法测试与范围 | -65024～65536 共 130561 个整数舍入/饱和比较通过 | 测试代码与日志 |
| PY-03 | 检查现有黄金 JSON 与当前生成结果 | 25 组，种子 20260907；a/b、乘积、累加、舍入、饱和全部对应 | 比较程序/命令与输出 |
| PY-04 | 独立核对代表值 | acc=65536→127；-65024→-128；384→2；-384→-2；0→0 | 计算过程/断言 |
| PY-05 | 审查输入与边界覆盖 | 明确当前非法输入测试覆盖范围，不把未覆盖 b 侧/长度等声称已覆盖；发现阻断缺口先补测 | 审查记录 |

注意现有 4 测试中黄金测试主要检查累加，不足以单独证明磁盘 JSON 所有字段。因此 PY-03 必须独立读取已有 JSON 比较，不能先覆盖文件再说旧文件正确。已准备只读核验程序 `verification/check_saved_golden.py`，按下方命令执行，不覆盖原 JSON。

## 可直接执行的软件操作单

正常由 AI 执行；若需 Wong 手动执行，在 PowerShell 输入：

```powershell
Set-Location -LiteralPath 'D:\FPGA_Competition'
$pyExe = 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
git rev-parse HEAD
git status --short
& $pyExe -B -X utf8 -m unittest discover -s verification -p 'test_*.py' -v
$testExit = $LASTEXITCODE
Write-Output "测试退出码=$testExit"
if ($testExit -ne 0) { throw "单元测试失败，先保存输出" }
& $pyExe -B -X utf8 verification/check_saved_golden.py
$goldenExit = $LASTEXITCODE
Write-Output "黄金核验退出码=$goldenExit"
if ($goldenExit -ne 0) { throw "黄金核验失败，先保存输出" }
```

预期：4 项测试成功、最后为 OK、退出码 0。一般数秒内完成；超过 60 秒仍未结束时保存输出并反馈，不修改 Python 算法去绕开测试。路径不存在时返回错误全文，不安装未知包。

第二条 Python 命令完成 PY-03/04，并检查双侧 12 个非法输入；预期 JSON 显示 golden_cases=25、mismatches=0、boundary_checks=5、invalid_input_checks=12、source_modified=false，退出码 0。PY-05 仍由审查核查覆盖范围。开发将命令与输出归档到 `report/evidence/S0-T02/运行编号/`；需要你执行时提供完整命令，不能只说“检查黄金结果”。不要为重现覆盖已有证据。

## 执行、审查与验收记录

- 执行时间/提交/工具/日志：待填写。
- PY-01～05 实际结果：未执行（本任务轮次）。
- G0：规格与方法已准备，开发开工核实版本后判定。
- G1：未执行。G2：未执行。
- G3：不适用，纯 PC 数值复核，不涉及实物运行。
- G4：未验收。
- 审查使用 [[03-实验记录/任务记录/任务记录模板]] 的问题表写入此处；问题修复后指定新提交再复核。
- 通过后下一任务：由总控创建 INT8 RTL 的接口与周期级任务卡；不能直接把现有数学说明当成已冻结的 RTL 握手规格。

## 2026-09-10 准备性自检（不代替明日验收）

AI 已运行上述两条 Python 检查：4 测试通过；25 组磁盘黄金数据零不匹配、5 个边界和12 个非法输入检查通过。证据 `report/evidence/preparation-20260910/checks.json`。这属于操作说明与辅助脚本预检，尚无独立审查结论，不提前通过 G2/G4。

## 新阶段体系对应

本任务为阶段0开工子任务，编号保持以保留证据链；不代表整个阶段0或阶段1PC模型完成。完整RTL仿真属于阶段2A，固定输入上板属于阶段2B，后续任务按新计划编号。
