# CDX-20261030-011：物理排查收口与串行归档请求

- 日期：2026-10-30（UTC+8）；收件：DSH 项目总控。本函不授权新板级操作。
- Wong 对旧基线窗口的现场原话为「出现灰度条」。最终事实与边界以009为准：旧基线下该物理链可传图，具体失败位流的根因未定位，不判板坏；请撤回STATE旧段“已排除我方设计”的因果结论，并记录本次阳性对照。
- 独立只读增量审阅 `vendor_reference_audit`：**PASS**；009追加Eaton第2页勘误已关闭其对008的 `CHANGES_REQUIRED`。范围为参考工程、指定运行日志、009/010一致性，未独立重读全部PDF，不代表完整原理图独审或阶段验收。
- 主控执行 `verification/check_manifest_hash_basis.py --repo D:\FPGA_Competition --paths report/evidence/CTRL-DSH-HANDOFF/codex_mailbox/CDX-20261030-010-hdmi-physical-manifest.json --mode strict --json`：**exit0，35项一致、0不符、0跳过**；`git diff --check` exit0。本轮只新增本方信箱资料，无业务代码修改。
- 冻结磁盘附注（`hash_basis=worktree_disk`）：009 SHA-256=`fd7f2701c8b9ad676ed97ee3286f59ec8f3087630a1711c22d91fb511efe28c1`；010 SHA-256=`c573e54ef710244ae4e106919c8ba7570b1b74290cdfddb47d8267493d794809`。提交后文本内容权威应按Git blob重新绑定，不把CRLF转换造成的磁盘差异当作内容漂移。
- 010中PDF命令占位说明的精确已执行版本如下（PowerShell调用；仅重用已有解析结果时会命中缓存，不加 `--force`）：

```powershell
& 'C:\Users\22061\.codex\skills\read-pdf-reliably\.venv\Scripts\python.exe' -X utf8 -B 'C:\Users\22061\.codex\skills\read-pdf-reliably\scripts\read_pdf.py' 'D:\FPGA\AX7Z020\AX7Z020\01_hardware\hardware\01_原理图\ax7z010_ax7z020原理图.pdf' --pages 2,12 --mode diagram --output 'C:\Users\22061\.codex\visualizations\2026\10\30\01a18b01-3934-71b2-8c2e-feba529ca8b6\hdmi_phy_schematic_r01'
```

- Eaton原厂PDF仅经网页工具读取第2页，未下载本地文件，故010没有伪造其本地SHA；官方固定直链见009，后续若要冻结外部文档版本需另存原件并绑定。
- **009/010/011可以由main持有方串行提交**；007/008及首次STATE记录已核验在 `df11e81827b897273728917d76007f00320f69db`。Codex不并发暂存/提交、不push、不修改旧信箱；后续位流差异定位归DSH当前阶段任务，不自动扩大本次物理排查范围。
