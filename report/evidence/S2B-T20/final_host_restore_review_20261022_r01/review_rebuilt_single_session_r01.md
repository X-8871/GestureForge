# 重建 ELF 同会话恢复入口独立审查 R01

- 结论：**PASS（代码审查及限定回归范围）**
- 被审实现：`verification/s2b_rebuilt_app_acceptance.py`，SHA-256 `79ccfdbc37e3ef5fe7b51165c49c1dbd23c0e09aab1196b17f87ab315679bc93`
- 被审测试：`verification/test_s2b_rebuilt_app_acceptance.py`，SHA-256 `aa2b788d90b3e748f5ea854baffeb6cb812d008df5c41cfc469b6229f0785986`
- 基线 HEAD：`91151507b769a29db3145a07a2d4ad92d78ec53a`
- 范围：单会话入口门禁、BootROM与2B安全IDLE分支、CSR map owner注册/清理、R04部署/真实验收路径回归。未操作硬件。

## 审查发现

- `_preflight_entry()` 在同一个生产controller/session中重新枚举和验证JTAG目标链，逐核记录停前state/PC，对实际 `Running` 核调用stop，再记录停后state/PC；要求双核Stopped并通过`gate(both=True)`后才读BOOT_MODE及继续分支。
- BootROM分支需PC精确为CPU0 `0xFFFFFF28`、CPU1 `0xFFFFFF34`，BOOT_MODE=0，并由严格`CONFIG_STATUS`解析确认EOS、DONE internal/pin、GWE、GTS及startup phase全0。该分支明确不读取不存在的CSR，也不提前注册CSR map。任何一个条件不满足都会异常退出，不复位/部署。
- 非BootROM分支在同session仅注册一次CSR map，再要求完整safe IDLE/PS owner/ledger0快照后才能复位；错误分支由外层finally按owner `attempted` 状态清理部分/完整映射。
- BootROM分支在状态门禁通过后先system reset，之后注册本session CSR map一次再部署；2B分支沿用预复位已注册映射，不重复注册。helper要求map_session为同一session且owner未attempted，wrapper最终清理此owner映射后再断开session/XSDB。
- 后续R04全bit/postconfig/重建ELF、UART banner、256字节CPU↔DAP cache probe、真实OP_WEIGHTS seq3、sample000黄金与seq4动态ACK、最终停止CPU/安全IDLE及账本0的主流程未改。wrapper `vitis/run_s2b_rebuilt_app_acceptance.py` 未修改；失败路径由wrapper执行controller fail-stop、关闭UART、清映射、断session/XSDB并持久化cleanup状态。
- 本次回归：

  `C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m unittest verification.test_s2b_rebuilt_app_acceptance`

  退出码0；14项测试通过。覆盖BootROM CPU1受控停止/不读CSR、EOS和未配置字段负例、非BootROM不安全ledger拒绝、输入/ELF绑定及wrapper dispatch边界。

## 限制

PASS只覆盖离线代码和上述回归，不代表本次板上入口谓词已满足或实测完成，也不代表G3/G4/G5。真实运行必须在当前生产session中重新观察state/PC、BOOT_MODE和CONFIG_STATUS；旧R01/R02结果仅作历史定位，不复用旧DDR/权重/POR连续性。
