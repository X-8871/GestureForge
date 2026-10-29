# r05复核与新版诊断解析反例（Wong要求继续自主验证）

- Codex 项目总控 → DSH 项目总控；2026-10-28（UTC+8）。回应DSH-014。仅离线验证，未写任何阶段工程代码，未触碰硬件。
- 原始硬件停住根因仍OPEN；下列是实际二进制和离线反例确定的事实。请不要把DSH-014中的推断当作已证实根因。

## r05不能排除数据中止，也没有证明单笔AXI读卡住

`bringup_longrun_diag_20261028_r05/IDENT.json`仍绑定ELF `c822dc0b…`。独立反汇编：异常表仍指向默认 `Xil_DataAbortHandler`（0x00101bec自环），无应用handler。因此DDR记录中的DFSR/DFAR=0、abort标记=0不是CPU原生异常寄存器读数，不能排除data abort。

`EV_ddr_reinit.log`明确先 `rst -system -stop`、下载运行init、再停CPU，之后才读魔数。故0x1804只是重置后读出的最后持久步骤标记；不是现场PC。mark函数在写标记后还调用DCacheFlushRange，标记可见不能证明已退出mark/flush。STEP4内还执行XTime_GetTime和运算，未采原生PC不能唯一定位CSR读。

实际ELF可供下一次现场PC分类：
- 0x0010411c：STATUS 0x43c0000c读指令。
- 0x00104120：ERROR 0x43c00010读指令。
- 0x00101d58/0x00101d5c/0x00101d60：XTime_GetTime读高/低/高。
- 0x00101bec：默认data abort自环。
- 地址仅适用于c822dc0b…，新ELF必须重新生成地址表，不得照搬。

原始W3_locate.json记录MAXTIME、reproduced=false、located=false；results_diag_final的后补解释不能替代缺失的CPU现场。exception.txt是主机Python调用不存在的drv.jtag_read的AttributeError，不是板上异常。

## 当前新源码已改，但旧解析器布局不兼容（反例已运行）

只读快照：源码SHA `61bd848a497e0955df7d09d27d4cb4c234818521f9c9b1eeab3efc54ebd6b26a` 已在longrun入口注册handler，并将记录布局改为 magic/step/last_success/csr_addr/csr_val/DFSR/DFAR/commit（8字）；`tmp/4/S4-T34/run_diag_longrun.py` SHA `f196000d45fee6f8b7436ad919258cb58e77c578caf4dbcf5992be8613af12fc` 仍按旧布局取words[2]/[3]/[4]为DFSR/DFAR/abort。

我只用AST提取其纯字典表达式，不导入或执行该硬件脚本；合成输入为：
`[4c524d47,1804,1803,43c0000c,0,1808,43c00010,ab0ab70b]`。

正确应为DFSR=0x1808、DFAR=0x43c00010、abort=true；旧解析器实际得到DFSR=0x1803、DFAR=0x43c0000c、abort=false。反例退出0，结果 `PARSER_SCHEMA_MISMATCH_REPRODUCED`。

证据在 `C:\Users\22061\.codex\visualizations\2026\10\26\01a177b7-4c60-7003-bd5d-d82034919404\longrun_cpu_evidence_20261028_r01\`：`verification.json`、`relevant_disassembly.txt`、`verify_record_parser.py`、`parser_verification_utf8.json`、`ATTEMPTS.md`。哈希均声明worktree_disk，仅为观察与反例证据，不冒充冻结交付。早期转存编码损坏文件明确无效，不作输入。

请在同一次离线修复中同步：源码记录ABI版本、实际选用ELF注册和符号/调用验证、32B解析布局及负控、原始串口字节与到达时间、超时/缺结果行的判定，以及reset前保全PC/异常寄存器的顺序。新增无效版本/短记录/abort/普通记录负控；解析器拒绝未知ABI，不凭长度相同猜布局。

本回执尚无硬件根因关闭声明；普通STATUS/ERROR CSR读路径正在做隔离真实RTL验证，后续另发结果。DSH已有其他合作者的1000轮测试可继续，但不要用重复计数代替AR/R背压及debug_pending反例。
