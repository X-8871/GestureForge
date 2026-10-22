# A：阶段3到2B恢复脚本增量独立复审 R02

- 结论：**CHANGES_REQUIRED**
- 被审脚本：`tmp/2B/restore_2b_after_stage3_20261022_r01.py`
- SHA-256：`c5bdf5c04c32dc99a280729d19e46e1d8c73b56679cb0d8688622bfea2ef1b64`
- HEAD：`91151507b769a29db3145a07a2d4ad92d78ec53a`
- 范围：增量及整个恢复流程静态复审；执行Python AST解析及只读冻结输入/HWH/ELF验证。未运行恢复脚本，未连接或操作硬件，未修改stage3 STATE/HEAD。

## 已关闭的 R01 问题

脚本已移除重叠LOAD区间排他门禁；逐核记录停前状态/PC和授权依据，只对状态为 `Running` 的核调用stop；stop后执行 `gate(both=True)`，并保存双核停后状态/PC，确认两核停止后才对CPU0读指令。随后要求冻结stage3 ELF和原R04 infer ELF中恰有一个逐字匹配，否则不会进入任何部署分支。对旧现场PC `0x105D0C` 的离线16字节检查与此逻辑相符：stage3字节 `0000a0e31eff2fe10030a0e300c0a0e3` 匹配stage3 ELF且不匹配infer ELF。

用户/总控授权边界已在本次任务输入中明确允许独占任务停止CPU0和CPU1，脚本逐核记录该依据；未调用任何板上操作。

## 阻断问题

1. **preflight session清理失败后仍继续创建deployment session和部署。** 第349行调用 `_close_session(...)`，该函数会捕获 `controller.close()`、`session.disconnect()`、`xsdb.dispose()` 或日志关闭异常并写入 `record["cleanup_errors"]`，但返回后脚本不检查这些错误，直接将session对象清空并在第353行建立新session，随后第358行执行system reset并继续部署。若旧session断开或XSDB释放失败，脚本会在旧会话生命周期未确认结束时继续硬件更改；结尾返回2并记录错误不能撤销已发生的system reset/deployment。

   关闭条件：preflight清理后，在创建deployment session前检查清理结果；至少任何 `session.disconnect` 或 `xsdb.dispose` 失败都必须失败关闭、保存 `FAILED_RESTORE` 和错误并停止，不执行后续reset/deploy。其他controller/journal清理错误须按其对会话/映射安全的影响明确门禁，不能仅在末尾汇总。

## 其他复核

- 当前阶段3STATE符合脚本要求的DONE状态；冻结README/ELF/XSA/bit SHA与脚本常量一致。
- 冻结XSA HWH中两段VDMA分别为 `0x43000000–0x4300FFFF` 与 `0x43010000–0x4301FFFF`；脚本只申请这两个REGISTER窗口，检查SDK映射精确范围/权限，清RUNSTOP并观察HALTED后卸载映射，再观察system reset后的EOS0。
- 恢复仍在新的deployment session上使用原R04 init/XSA/bit/infer和固定runner/helper，app停止后核验CSR安全IDLE/账本0。脚本明确限定为恢复、不执行UART/G3/G4/G5验收、不改I2C、且不声称system reset等于POR。

因此本SHA尚不能批准运行。修复preflight清理失败时的继续执行路径后，冻结新SHA并重新复审。PASS后仍不代表恢复已实际运行或硬件验收通过。
