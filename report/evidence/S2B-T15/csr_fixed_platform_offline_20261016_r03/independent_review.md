# 当前 BSP/ELF 离线构建独立审查

- 审查者：当前任务独立子代理 `/root/vitis_managed_review`，模型参数 `gpt-6-luna` / `high`。
- 审查结论：PASS，仅限 G2 源码和本次离线构建证据；不代表 G0/G3/G4/G5 或板测通过。
- 被审源码基线：`3942603390435e7eba3cb8e7ce32e48838dfa7bb`。
- 被审清单 SHA-256：`17b6c017740972565755aa2d75a1b19fb51dce3d5482de8427c465184ce71b79`。
- 本记录为总控按真实子代理结果整理的审查摘要，不是数字签名或命令执行记录。

## 独立核查结果

清单 67/67 项存在且原始字节哈希一致。builder 的九项源码与快照和当前源码一致。外层 `PASS_OFFLINE_CANDIDATE_BUILD_ONLY`、原生退出 0、143.297 秒；内层 `PASS_OFFLINE_FULL_XSA_BUILD`、111.266 秒。client 自然排空，公开 close/dispose 完成；专属 server Job 显式终止后稳定空读并关闭句柄，未宣称优雅 RPC 退出。

XSA 绑定 T13 r03 no-bit 平台。HWH/readback 显示 GP0/HP0 启用、32 位 AXI4-Lite CSR、visibility=0。实际 ELF 反汇编对应 CSR word ldr/str。静态 MMU 报告通过：L1 表地址 0x00110000；32 MiB arena 为 0x10000000–0x12000000 的 32 个 identity cacheable section，无物理别名；CSR section 使用 DEVICE_MEMORY；未启用 USE_AMP。实际反汇编包含 TLB 属性更新和 cache flush/invalidate 调用。

Reviewer 复跑 checker 时使用 Path.read_text 导致文本换行归一化，该次新输出的文本输入哈希未用于证据；改以原始字节核对封包 MMU 报告的 11/11 输入绑定，报告自身哈希亦匹配清单。

## 未覆盖事项

未下载或执行应用，未验证实际页表、DDR、HP0/cache 可见性；109 黄金样本、1000 连续任务及恢复仍未执行。
