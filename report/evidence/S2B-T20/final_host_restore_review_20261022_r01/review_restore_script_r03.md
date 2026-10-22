# A：阶段3到2B恢复脚本增量独立复审 R03

- 结论：**PASS（静态审查，仅限恢复脚本控制流）**
- 被审脚本：`tmp/2B/restore_2b_after_stage3_20261022_r01.py`
- SHA-256：`dcefd83cfe917cd6bd47701391a8713446e78f1af5c256bae90fdaedfda4da1d`
- HEAD：`91151507b769a29db3145a07a2d4ad92d78ec53a`
- 审查范围：R02唯一阻断修复、原R01 PC分类/逐核停机修复、恢复控制流及冻结输入离线核验。未运行恢复脚本，未连接或操作硬件，未修改stage3 STATE/HEAD。

## R02问题关闭

R03在关闭preflight controller/session/XSDB/journal并置空引用后，立即要求 `record["cleanup_errors"]` 为空，才继续创建deployment session。任一步关闭失败都会抛错进入 `FAILED_RESTORE` 异常路径，并由 `finally` 保存 `restore_result.json`；该检查先于deployment session创建和system reset，因此失败时不会继续reset/deploy。此前的“记录错误但继续部署”路径已关闭。

## 整体流程复核

- 停核前记录CPU0/CPU1状态和PC，并记录本任务逐核stop授权；仅对 `Running` 核发stop。随后 `gate(both=True)`核验双核已Stopped，再保存停后状态/PC并读取CPU0现场指令。
- 两份ELF LOAD区间重叠不会被用于身份排除。现场指令仅当唯一匹配冻结stage3 `v10_read` 或R04 infer时继续；未知或双重匹配会在reset/deploy前失败。
- 旧现场PC `0x105D0C` 的离线16字节为 `0000a0e31eff2fe10030a0e300c0a0e3`：匹配stage3 ELF，且被原R04 infer ELF拒绝。
- 冻结stage3 STATE状态、README/ELF/XSA/bit SHA及HWH中两个64 KiB VDMA REGISTER窗口与脚本固定值相符。VDMA清RUNSTOP、等待HALTED、卸载映射后才执行system reset并要求EOS0。
- deployment使用独立新XSDB session，沿用固定R04部署绑定；部署后停止app并要求CSR SAFE IDLE/账本0。脚本不做UART验收、不操作传感器/I2C、不声称system reset等同POR。
- 使用随附Python运行时对该文件执行 `ast.parse`，输出 `AST_PARSE_OK`，退出码0。

## 限制

PASS仅表示该SHA的静态恢复控制流审查通过；没有运行脚本或板上动作，不代表G3实物验证、G4任务验收或G5阶段验收。总控仍须按最新现场事实和既有授权决定是否运行，并核对运行结果与清理状态。
