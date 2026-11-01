# 板窗心跳与M3实际PASS

心跳(UTC+8)：2026-11-01T00:35:16+08:00。Codex仍持有至01:00，Wong已明确其他窗口停止用板。002所述r53冲突发生后已由Wong再次POR并E1通过。

M3 r05实际结论PASS（固定只读保持事件）：12615680B，before/after各双读共4份都与41907f53...基准一致，0字节/0位变化，holder506秒受控停止；各步骤/比较exit0，嵌套server主动TerminateJobObject码124不是自然exit0，timed_out=false且CLEANUP_CONFIRMED。独立报告legacy_codex_20261031/r03/review_new/R03_M3_actual_r05_review_20261101.md SHA d6c599a617613453cb677817b70dc8212941a2c29f16bdb60d1556b2d03be4e2。

C2 R04源/构建与host回归独立复审PASS（review_r04.md SHA bca69311942809375986c814f6173fc00062894b1b41873f438455a3e66b4dc4）。真实候选ELF77bc9ee3...不改。R02部署已单次init/编程P3q，但XSDB许可范围0..0x3fffffff漏含PL寄存器0x43c00000，故guard阻止应用启动；这是我方脚本问题。正常一次close/Job清理，未con应用。已改与M3成功相同的0..0x7fffffff许可范围，并逐项静态验证RAW/result/2B/VDMA地址覆盖；这只是调试器允许范围，不宣称DDR有2GiB。

按R15再次请求物理POR后用全新R03部署，不在旧RunId重跑。应用代码没变，不复位、不push、ENABLE=0。剩余时间优先C2实测，01:00前归还。

R09标准SHA256 commit_blob补验已完成：w6/report/evidence/R09/r09_commit_verify_20261101_r01/manifest.json SHA939278bb96f2f004e87a786ac5abce75c1a6a30a3835d636e0da4c25e260dd3f，固定f0fab846，strict30/0/exit0。此补验不改变C4的CHANGES_REQUIRED语义结论。
