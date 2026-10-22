# S6-A 冻结自证报告（导出副本复跑）

- 规则：任何冻结/交付提交必须自证：导出该提交后，自检 + inputs + evidence 三项检查全部 exit 0。
- 生成：2026-10-23 04:33:24+0800

## worktree snapshot（提交前自验；不含 .git/tmp 与本工具输出）

- 判定：**SELF_PROVEN**；契约 `S6A-G0-v1.7`；RunId `s6a_g0_20261022_r08`
- 该提交内 S6-B 证据目录文件数：**132**（STATE 声明该目录时必须 > 0）
- 证据目录文件数：40

| 检查 | 真实退出码 |
|---|---|
| selfcheck（C11：清单 + STATE） | 0 |
| check_stage_delivery --mode inputs | 0 |
| check_stage_delivery --mode evidence | 0 |

**总体判定：ALL_SELF_PROVEN**

导出复跑只证明该提交的证据自足性与清单/STATE 一致性；不代表语义正确、独立审查或实物验收通过。
