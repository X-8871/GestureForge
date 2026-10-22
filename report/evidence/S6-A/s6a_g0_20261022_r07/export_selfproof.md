# S6-A 冻结自证报告（导出副本复跑）

- 规则：任何冻结/交付提交必须自证：导出该提交后，自检 + inputs + evidence 三项检查全部 exit 0。
- 生成：2026-10-23 03:19:43+0800

## commit 04ea58e1e363e956b8a46ae5711ec8aecb27bfd4

- 判定：**NOT_SELF_PROVEN**；契约 `S6A-G0-v1.5`；RunId `s6a_g0_20261022_r06`
- 该提交内 S6-B 证据目录文件数：**0**（STATE 声明该目录时必须 > 0）
- 证据目录文件数：36

| 检查 | 真实退出码 |
|---|---|
| selfcheck（含 C11 清单/STATE） | 1 |
| check_stage_delivery --mode inputs | 0 |
| check_stage_delivery --mode evidence | 0 |

## worktree snapshot（提交前自验；不含 .git/tmp 与本工具输出）

- 判定：**SELF_PROVEN**；契约 `S6A-G0-v1.6`；RunId `s6a_g0_20261022_r07`
- 该提交内 S6-B 证据目录文件数：**40**（STATE 声明该目录时必须 > 0）
- 证据目录文件数：39

| 检查 | 真实退出码 |
|---|---|
| selfcheck（含 C11 清单/STATE） | 0 |
| check_stage_delivery --mode inputs | 0 |
| check_stage_delivery --mode evidence | 0 |

**总体判定：NOT_ALL_SELF_PROVEN**

导出复跑只证明该提交的证据自足性与清单/STATE 一致性；不代表语义正确、独立审查或实物验收通过。
