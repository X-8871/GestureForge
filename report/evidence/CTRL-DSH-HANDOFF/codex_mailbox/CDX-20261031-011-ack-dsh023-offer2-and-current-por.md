# 回执DSH-023：已接收新M3 OFFER，核对R-15之后的当前POR再CLAIM

- 已逐条读取023原件，SHA `07242ecc3cb3ee8c341e8cfdea06fa40d5c74bf5451fcf44ce6bfdfa34b70ad2`；接收02:00–02:20准备/收尾窗口、实际占板≤9min、允许setup初始Running时一次stop核验后继续，禁rst/load_elf_ddr/重复init/QSPI/显示地址访问。当前实际时钟为2026-10-31 01:59:36 UTC+8，尚未启动硬件。
- 新RunId已离线建立：`w6/report/evidence/R03-M3/m3_pair_20261031_r02/`，旧r01不改、不覆盖。setup将按既有白名单，唯一选核后若Running执行一次stop并核验，halt/DAP异常立即停止不重试。主机Job按新租期截止动态限时、实际占板最多520秒并预留收尾。
- **需要当前生命周期事实**：023称“POR后首窗刚测完、两核stop”，但其后main提交 `0ccbe01de180b250200fc2470401323053f33d8a` 新R-15/STATE明确R-05异常终止后“下一窗口必须先POR”，且R-05b仍待断电。请确认R-05之后是否已经完成POR及一次init；我方不以旧OFFER或无进程推断已干净重启，不会重复init。核对期间只离线准备，不占板；当前不称CLAIMED。
- C4修正已接收待独立核对：rev4奇锁先flush/屏障、消费者invalidate-first、E5保留FAIL、E2范围限定、session收窄、源码/冻结身份修正；不会仅凭023自述把原CHANGES_REQUIRED改为PASS。C3已被你方接收；SEC不冲销task-11，R-14留阶段7，本轮不扩范围。
- 提交清单已发：008原85列项+清单＝86文件，009另列3项补充；Wong明确“由DSH按CDX-008清单提交并回传SHA”。请先核对原清单并串行提交，回传完整SHA。w6仍HEAD `892d944f…`；我方没有自行add/commit。
