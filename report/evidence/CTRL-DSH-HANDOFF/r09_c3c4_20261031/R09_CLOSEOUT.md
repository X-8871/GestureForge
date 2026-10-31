# R-09 闭环记录（C3 测量学 / C4 独立复审）

- 日期：2026-10-31（UTC+8）
- 结论：**R-09 关闭**（交付侧与证据侧均落盘；仅"SEC/no-ILA 裁决"仍作为 R-02②④ 单独跟踪）

## 1. 交付内容（Codex 侧，DSH 串行提交）

| 编号 | 内容 | w6 提交 | 结果 |
|---|---|---|---|
| C3 | T6-A03 测量学方法 + 离线分析，独立复审 **PASS** | `97e07a4` | 交付 |
| C4 | 独立复审（r02 主报告、r05/rev4 增量） | `97e07a4` | 交付 |
| C2 | 真实推理写端集成材料（C2 review r01/r02） | `97e07a4` | 交付（板上验收见 R-05） |
| M3 | M3 成对取样工作区（`m3_w02`） | `97e07a4` | 材料就绪，**执行仍受 R-03 阻塞** |
| R03 | 复核/守则/完整性审查 8 篇 | `97e07a4` | 交付 |
| — | CTRL-LEGACY 证据目录（c3_collector / closeout / final_followup 的 `submission_inventory.json`） | `f0fab84` | 交付 |

- 权威文件清单与逐文件 blob：见同目录 `manifest.json`（`hash_basis: commit_blob`，30 项，全部按 w6 提交对象取哈希）

## 2. C4 复审 8 项的处置（已由 DSH 在 2026-10-31 01:5x 处理完毕）

① sidecar 覆盖项（rev3/方案 A 已修）；② seqlock → rev4 + 生产者 v4；③ E5 改判 FAIL 口径；④ E2 范围限定；⑤ 源码绑定重列；⑥ 阶段5 身份统一 tag `6b43e05`；⑦ session 主张收窄；⑧ 文档/清单一致性。
（对应信箱 `DSH-20261031-023`，复审回执 `CDX-20261031-005`）

## 3. 边界与遗留

- **C4 中"真实推理写端"部分**：仍待板上验收 → 归入 **R-05**，不在 R-09 内重复计。
- **R-02② SEC（sequential equivalence checking）**：已澄清为只能对"不含相机 wrapper 的 S5/S6 限定交付"作 scope-specific 不适用论证，**仍需 Wong 裁决** → 归入 R-02，不阻塞 R-09。
- **R-02④ no-ILA**：同样待 Wong 裁决 → R-02。
- **R-03 M3**：工具/材料已就绪，Codex 休息期间 BLOCKED；恢复需新 OFFER + 新 RunId。

## 4. 验证方式（可复核）

```bash
# 清单 30 项逐项按 w6 提交对象复核（0 不一致即通过；本记录生成时执行结果 checked=30 mismatch=0，exit=0）
python -B D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF\r09_c3c4_20261031\verify_r09_manifest.py ^
  D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF\r09_c3c4_20261031\manifest.json

# 单文件抽查（w6 仓库）
git -C D:\codex-worktrees\w6 rev-parse 97e07a4:legacy_codex_20261031/c4_r02/C4_R02_review_20261031.md
```

> 说明：本清单用 `hash_basis: commit_blob`（git blob 对象 SHA-1 + blob 字节数），绑定 w6 的 `97e07a4` 与 `f0fab84` 两个提交，不依赖工作区磁盘字节，故不受 autocrlf 影响。项目统一门禁 `check_manifest_hash_basis.py` 面向本仓库内的项目式清单，本条为**跨工作树 git-blob 清单**，故提供等效的自校验脚本 `verify_r09_manifest.py`。

## 5. 结论

R-09（C3/C4 交付）**关闭**。后续与 Codex 相关的开放项只剩：**R-02②④（待 Wong 裁决）**、**R-03（BLOCKED，需新 OFFER）**、**R-05（待板上验收）**。
