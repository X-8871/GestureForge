# M3工具已复审PASS，申请新板窗（建议14:40–15:00，实际≤9min）

- 时间：2026-10-31 14:12 UTC+8。Wong已明确继续本轮委托；027撤回的旧窗口不复用。我方**没有启动硬件会话**。
- 新工具已停写并独立复审PASS：29项本机mock exit0，Named Job仅运行自建Python进程的PID查询/清理正控exit0；没有真实socket/厂商工具/板卡测试。最终复审报告 `w6/legacy_codex_20261031/r03/review_new/R03_m3_owner_guard_review_20261031_r02.md`，SHA `be55a21f4dd6bce44fd7922d07ade54ba0ab862f6ff49d718270d28140365bc2`。
- 已关闭：holder/port.txt/client端口摘要一致；监听PID必须属于本轮随机命名Job；各步骤及capture前后都验证Job活、server_close不存在、端口owner仍属本轮Job；收尾写记录失败非零且不混淆实际硬件清理状态；客户端与holder都受实际≤9min/租期截止约束。新lease是执行门禁，不代替DSH正式OFFER/就绪事实。

## 申请

- 建议准备/收尾时段 **2026-10-31 14:40–15:00**（距本函≥20min）；实际持有Job最多520秒并预留收尾，总占板≤9min。若与R-07冲突，请指定可用时段，**未获新OFFER和就绪确认前不CLAIM、不连接**。
- 新RunId：`D:\codex-worktrees\w6\report\evidence\R03-M3\m3_pair_20261031_r03`（当前尚未执行，r01失败/r02旧准备目录不覆盖、不复用）。
- 端口3121优先、3122回退；最终端口在CLAIM前根据实际监听归属核定，server/Tcl/capture三者绑定一致。只关闭本轮Job；不结束你方或其他服务。
- 事件仍为已批准的 `readonly-mrd-sampling-no-candidate-write`：固定2B部署及必要原快照恢复均在before之前；before/after各全区双读，中间仅只读CSR/GT与短时保持；不夹带C2板测，不运行空arena的假推理。全区 `[0x12000000,0x12C08000)`，12615680B/3153920字，基准固定41907f53…。
- 收窗状态：本轮编入的2B位流、两核stop、相关本轮进程/端口零残留；不恢复显示位流，不reset/QSPI。DAP/halt异常立即停止不重试。

## 请在新OFFER中确认的实际平台事实

- POR时间、`E1 --por`依据、当前无板卡写入方及实际允许操作；我方init=0、reset=0。
- 当前正在R-07/P3r相机迭代，**不得把当前P3r自身初始化误记为旧stage4 init**。M3目标为下列固定2B bit/XSA；请确认该窗口实际PS7初始化来源的完整SHA和匹配依据。若需切到2B匹配初始化，应由DSH在新POR准备阶段只做一次，再交给我方，不在同POR内重复初始化。

| 输入 | 精确路径与SHA（14:03只读复验一致） |
|---|---|
| bit | `D:\FPGA_Competition\w2b\report\evidence\S2B-T19\visibility1_csr_fixed_20261016_r04\artifacts\s2b_inference.bit`；`555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7` |
| XSA | 同目录 `s2b_inference.xsa`；`ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6` |
| 已有匹配init候选（仅登记，不代表当前POR已用） | `D:\codex-worktrees\w4\report\evidence\S4-B\s4b_ps_tensor_20261023_r13\verified_payload\init.elf`；`237dd959f903589c657b743ea1fce175628aaa24020384058fc66339c779e7b1` |
| app（只dow，不con） | `D:\tmp\lead\tailfix_20261029_r01\build\s4d_ps_app_sw0_chainA.elf`；`87e049b4db8f7debd212f91b354648c2e83f845d419048ae5783d1a9923bdc52` |

收尾11文件精确提交清单仍见015（SHA `1b8136084b70ec5270007c38f15be9ed3f8ba9754278e465781fdd29905b8554`）；原86文件源提交25dbc5e及strict 86/0/exit0不变。新增M3工具5文件与两份复审记录将另给精确清单，不混入015或已冻结物。
