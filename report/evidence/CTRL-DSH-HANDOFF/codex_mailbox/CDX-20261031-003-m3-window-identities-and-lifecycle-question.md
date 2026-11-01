# M3板窗身份回执与生命周期核对

- 接受DSH-019的01:20–01:45，实际占板≤9min；当前仍离线准备，待最终采样程序独立审查与生命周期核对后发CLAIM，不在本信提前启动。
- bit：`D:\FPGA_Competition\w2b\report\evidence\S2B-T19\visibility1_csr_fixed_20261016_r04\artifacts\s2b_inference.bit`，SHA `555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7`。
- XSA：同目录 `s2b_inference.xsa`，SHA `ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6`。
- 初始化ELF：`D:\codex-worktrees\w4\report\evidence\S4-B\s4b_ps_tensor_20261023_r13\verified_payload\init.elf`，SHA `237dd959f903589c657b743ea1fce175628aaa24020384058fc66339c779e7b1`。应用ELF：`D:\tmp\lead\tailfix_20261029_r01\build\s4d_ps_app_sw0_chainA.elf`，SHA `87e049b4db8f7debd212f91b354648c2e83f845d419048ae5783d1a9923bdc52`。字节数及程序哈希另附机器清单；m3_pair本身是Python采样程序，不是ELF。
- 当前需确认：租约称“PL=P3q、两核stop”，这意味着PS/DDR已在当前POR初始化。请明确当前POR以来ps7_init是否已运行；若已运行，我方将不重复init，仅安全重编PL/手动dow并取样。若要求冷启动重新init，请先由DSH/Wong记录新的物理POR；我方不reset、不假定未初始化。
- 本次M3事件计划为 `readonly-mrd-sampling-no-candidate-write`：部署/必要原快照恢复均在before之前，before/after各双读；中间仅只读CSR/状态与短时保持，两核停止。不会把此结果扩大成“真实推理活动期间保持性”；该项如需实测须另给arena输入/权重预载授权，不把空arena导致error=1当推理成功。
- 禁任何rst、禁load_elf_ddr、禁QSPI；只清理自建会话，DAP/halt异常立即停手不重试。端口在窗口启动前实测3121，必要时3122；不碰显示地址。
