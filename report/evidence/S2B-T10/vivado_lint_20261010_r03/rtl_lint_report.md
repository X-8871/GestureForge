# S2B-T10 最终候选 RTL 的 Vivado lint

时间：2026-10-10（UTC+8）。Vivado 2026.1 Build 6511674；器件 `xc7z020clg400-2`；top `s2b_hp0_word_adapter`。独立新 Tcl 会话读取本 Run 的 guard 和 adapter 源快照；唯一 top 与明确输入一致。adapter SHA `640043c98ce1e80a973e836d62c57a2b9ed2e91e268186ce63a55dc8e5ae3ff7`，guard SHA `b09d8bddd60775efe49857b2ea837031db75c0fb802ace6075a3364da9d24531`。

## 真实结果

命令 `synth_design -top s2b_hp0_word_adapter -part xc7z020clg400-2 -lint -file $lint_report_file` 原生退出码0，实际5.456秒，报告峰值内存1331.348 MB。输出明确为 `Total of 0 linter message(s) generated`，并记录0 Warnings、0 Critical Warnings、0 Errors。11条运行INFO不是lint violations。

**0 lint violations found。** Vivado 2026.1直接产生的canonical CSV `linter.csv`存在、大小0字节、无非空行，与工具实际Total0一致；空CSV是零诊断的正确表示，不凭技能的一般非空检查误判为失败。本环境未提供技能所述read_file工具，因此以普通文件读取展示CSV原字节，再由总控核对；没有用Tcl或脚本解析/分组，没有解析ASCII表格，也没有添加工具报告之外的问题。

| 规则 | 数量 | 占比 | 严重性 |
|---|---:|---|---|
| 无诊断 | 0 | 不适用（分母为0） | 不适用 |

受影响文件：无。检查范围包括上述两个源快照，不包括测试台、冻结2A core、BD或完整PS/PL平台。

## 修正追溯

r01保留4条原始诊断，r02保留剩余ASSIGN-5；本Run使用独立会话和新快照重新执行，而非复用已验证状态或改写原结果。修正包括显式无符号33-bit lane、实际捕获guard验证的物理地址、对已证明4B对齐地址选择低2bit lane，以及在组合块完整赋值next_lane。没有warning suppression、waiver或改变总线、对象、所有权及恢复语义。

## 结论与适用边界

该候选的Vivado RTL lint子项PASS。无需根据零诊断虚构代码修改或修复示例；独立Reviewer还须核对实现、真实仿真及源版本。此次命令只启用-lint，不能称完整综合或资源验收，不证明锁定时钟、时序收敛、PS/PL/cache可见性、板上行为或SAFE_TO_REUSE。完整物理接口0.1.1仍未冻结，2B G0/G3/G4/G5仍需后续集成与实物标准。本次会话关闭记录、native原件、execute返回与history均绑定在delivery manifest。
