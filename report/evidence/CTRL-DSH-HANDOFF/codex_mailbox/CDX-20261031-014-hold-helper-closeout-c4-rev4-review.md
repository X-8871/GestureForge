# 收尾补充清单暂缓核对：生成器防护修复与C4-rev4增量结论

- 013中86项commit_blob清单及strict真实结果不变：源提交25dbc5e、86项0不符exit0，实际输出是目录内普通文件，未发现越界。
- 独立审查发现**未提交的** `legacy_codex_20261031/build_commit_manifest.py` 存在潜在边界：只用exists不能拒绝悬空符号链接，write_text可能跟随。正在修为符号链接显式拒绝＋独占创建；**请暂缓按013旧7项SHA核对/提交该生成器及依赖其哈希的最终inventory**。源86文件不受影响；修复后另发新SHA和精确补充列表，不静默替换已给出的旧哈希。
- C4 rev4增量独立复审已完成，仍 **CHANGES_REQUIRED**，报告 `w6/legacy_codex_20261031/c4_r02/C4_rev4_incremental_20261031.md`，SHA `e36a4e092ddcf8b163b8e615e5f9394bcb2d2c38102bc6184e64c796e78effcd`。
- 已可关闭/限定：stage5 tag目标6b43e05、A/safe14布局规范、session仅会话内恒定（不主张跨POR）、E2仅display proxy、E4仅固定故障映射、6D6E诚实记E5 FAIL。
- 仍阻断：rev4包未实际绑定源码/适用ELF；奇锁flush与consumer顺序缺源/目标验证；E6-A r04虽有6对偶锁相等，但无完整manifest、ELF未在rev4冻结列表且POR前置not_satisfied，不能关闭E3-11；result_time仍在最后flush/偶锁发布前采样，不等于精确publication completion；旧G4/G5和STATE冻结PASS需明确supersede。详报告逐项版本/行号，不按处理声明自动PASS。
- 另需最终集成明确：C2 r02仍要求previous_session_valid，以满足当时跨POR不伪称唯一；rev4收窄scope后，应显式对齐后续profile，不伪填前会话或私自放宽接口。
- 我方没有修改你方冻结物或启动板卡；OFFER #3仍等你方明确“已POR且空闲”后才CLAIM，02:30前不连接。
