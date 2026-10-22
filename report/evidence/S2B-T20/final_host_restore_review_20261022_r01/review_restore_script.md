# A：阶段3到2B恢复脚本独立审查

- 结论：**CHANGES_REQUIRED**
- 被审文件：`tmp/2B/restore_2b_after_stage3_20261022_r01.py`
- SHA-256：`a698c4815474656a473d5bbb732b396591feaff10a3dcab8ac03725232ffe6b8`
- 基线：工作树 `D:\FPGA_Competition\w2b`，HEAD `aef41a87d8e2724376b50b48365404e2dcf80c41`。
- 范围：静态控制流、脚本绑定及冻结ELF LOAD地址解析。未运行脚本，未连接或操作硬件，未改写阶段3 STATE/HEAD。

## 阻断问题

1. **前置PC门禁会拒绝已知的stage3运行现场。** 第310–312行要求CPU0 PC命中冻结stage3可执行LOAD，且不命中2B原infer可执行LOAD。独立解析两份绑定ELF得到：
   - stage3 `v10_read`：`[0x100000, 0x110010)`；
   - 2B原R04 `infer.elf`：`[0x100000, 0x10ed70)`；
   - STATE既有现场PC `0x105D0C` 同时落在两段内。

   因此已记录的现场满足第一项、违反第二项，脚本在任何停核之前抛错，无法到达后续按停核后16字节指令唯一匹配ELF的检查。这与本次恢复目标冲突。关闭条件：保留停核前每核state/PC证据；避免用重叠LOAD区间排除stage3；在授权场景下停稳所需运行核后，用已绑定ELF的实际PC指令字节唯一识别，再进入各自安全分支；歧义或不匹配仍立即停止。

2. **多核停机条件只用CPU0身份约束，却可能停止CPU1。** 在 `any_core_running` 分支，代码只检查CPU0 PC，之后会停止所有 `states_before` 为 `Running` 的核。CPU1 的PC虽有记录，但没有stage3身份/允许停机条件核验。关闭条件：明确记录并核验每个将被停止的Running核的授权依据；若脚本设计仅由CPU0代表stage3进程，应把该依据与对CPU1的停机授权明确绑定，并在核验失败时不停止该核。

## 通过项与限制

冻结stage3 README、XSA、bit、ELF以及阶段3 STATE 的SHA固定核验设计清晰；VDMA映射限定两个64 KiB窗口，检查RUNSTOP清除和HALTED后卸载映射，再观察EOS0；2B分支要求已停止、原infer指令匹配且CSR安全IDLE/账本0；恢复另建deployment session并使用当前runner/source binding。脚本明确标为恢复而非验收，不操作传感器/I2C，也未将system reset声称为POR。

由于上述停核门禁阻断且多核停止授权未完整证明，不能批准运行该SHA。修复后需冻结新SHA并复审。此结论不表示恢复已执行或硬件状态已改变。
