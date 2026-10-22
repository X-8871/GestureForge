# BootROM现场恢复入口独立审查 R02

- 结论：**PASS（静态控制流与离线绑定审查）**
- 被审脚本：`tmp/2B/restore_2b_from_bootrom_20261022_r02.py`
- SHA-256：`0d606e27b6d226f50e36c7f6c745dac5616b6d33e4d8bb31b99b1f0e0d7d393d`
- HEAD：`91151507b769a29db3145a07a2d4ad92d78ec53a`
- 范围：新入口的现场门禁、失败回执定位用途、R04输入等价性、部署/异常清理控制流。未运行恢复脚本，未连接或操作硬件。

## 关键核验

- r01失败回执实际SHA为 `66cbd23a74fb60fb729048529c6f7e4762275ee7a30047d60da558e48cf3e54e`，与脚本常量一致；脚本仅要求其状态为 `FAILED_RESTORE`、清理无错及前后PC为 `0xFFFFFF28/0xFFFFFF34`，并明确标为定位依据，不继承旧复位、DDR、权重或POR连续性。
- 新建XSDB session后先 `select_and_gate()`，其gate核验CPU0/CPU1停止、JTAG启动模式和当前目标链。脚本再次记录双核PC/state及BOOT_MODE，并要求双核仍停止、PC精确匹配两个BootROM地址、BOOT_MODE=0。
- 只有之后读取的 `CONFIG_STATUS` 同时满足 EOS=0、DONE internal/pin=0、GWE=0、GTS_CFG_B=0、startup phase=0，才通过 `require_bootrom_config()` 并执行system reset。底层解析器还严格验证CONFIG_STATUS原字、32位完整metadata、字段无重叠及EOS位4一致。无法确认是当前BootROM/PL未配置现场时，不会复位/部署。
- `build_config()` 仅更新R10绑定中的官方SDK配置、当前服务身份、动态HEAD/runner SHA及RunId；R04 init、app ELF、XSA、bit、CSR/interface等部署绑定与已成功的 `stage3_to_2b_restore_20261021_r03` 输入配置逐项一致。R04 infer SHA为 `a51499895e9387a74db87a3267843b9fbf7fdfa8b6646fcbc5db01485e090bf8`，SDK运行配置含297个文件绑定；hw_server身份绑定当前PID 4812 / creation FILETIME `134371091860065760`。
- 通过后沿用原已验证恢复的次序：system-stop后EOS0→固定CSR map helper注册→R04 init/full bit/original infer部署→停止app→稳定CSR SAFE IDLE/ledger0。与R03成功恢复相比，部署核心绑定完全一致；新增部分只是在reset/deploy前加入当前BootROM/EOS0门禁。不经过stage3/VDMA分支。
- 异常由 `FAILED_RESTORE`、traceback及独占创建的 `restore_result.json` 记录；已尝试CSR map会清理，再逐项关闭controller、session、XSDB和journal。任何清理错误都进入结果并使退出码为2。脚本明确不执行UART/G3/G4/G5、不改I2C，system reset不宣称POR。
- 使用绑定Python运行时对脚本执行AST解析，输出 `AST_PARSE_OK`，退出码0；以只读方式执行 `verify_prior_failure()` 和 `build_config()`，前者验证通过，后者确认上述绑定一致。两项均未连接硬件。

## 边界

PASS仅表示此恢复入口的静态和离线绑定审查通过。审核时未读取或验证之后的当前板上状态；实际运行仍须以脚本fresh session观察到的PC/state、BOOT_MODE和CONFIG_STATUS为准。该结果不代表恢复已执行、G3/G4/G5通过或旧DDR/权重/物理POR连续性成立。
