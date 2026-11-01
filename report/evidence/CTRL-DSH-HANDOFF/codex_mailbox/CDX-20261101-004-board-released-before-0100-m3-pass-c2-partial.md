# 01:00前归还板卡：M3实际PASS / C2发布成功但显示未闭环

2026-11-01 00:59:30 UTC+8 主机CIM确认3121/3122监听均为空。所有本轮hw_server/XSDB已收尾，双核已停；此后我方不再连接板卡，独占板窗归还DSH。

## 本轮结论

- M3 r05：PASS，12615680B，before/after各双读4份均为固定41907f53...基准，0字节/0位变化；实际Job506秒、受控清理。独立实际证据审查PASS，SHA d6c599a617613453cb677817b70dc8212941a2c29f16bdb60d1556b2d03be4e2。仅静止保持事件，不推断推理活动期间保持性，不声称历史6bit硬因已定。
- C2最后实测 `w6/report/evidence/R05-C2/c2_real_20261101_r05`：固定GF8权重5903100B已显式预载0x10100000并JTAG读回hash f6feb6d4...一致；同一fixture实际tensorCRC5B183B50，PL DONE_SAFE=1/error0、47287ms，decode rc0/count1/raw2。
- 实际UART `C2 PUBLISH RESULT`：pass1、SID10359、seq0、seqlock2、n_dets1、status1、business_state3(OK)、age_pub0ms、flush_gap_ticks850/valid1。此为板上真实发布观察，不是host mock。
- 随后的P3B渲染调用没有返回，没有C2 DISPLAY或最终CHAINB RESULT；控制器95秒停止采集、一次停核/Job收尾。因此**C2整体验收仍FAIL/BLOCKED**，不把发布成功当成显示/HDMI成功。板上读回步骤未执行，最后只读故障快照又遇到XSDB寄存器名r14不接受，未取得PC或结果块；这项失败也保留，不伪报独立DDR读回完成。

## 更正与限制

先前把error1称“超时”不准确，已由RTL/ELF复核纠正：源和ELF都写FFFFFFFF，error1有参数/请求错误等来源；冷POR部署原先漏掉独立GF8权重预载。补齐权重并读回后相同ELF正常完成47287ms计算。旧错误1的具体后端来源仍未唯一确定，不将缺权重简单等同该枚举码。所有失败RunId保留。

01:00前最后只读快照仅确认核已Stopped，后因rrd r14不支持而退出，之后服务正常清理。全局board_state当前abnormal=true，last run为C2显示未完成；**下一正式板窗须Wong物理POR+E1 --por**。不要求DSH立即开窗，不假称clean业务成功。

R09已按实际提交f0fab846完成标准commit_blob strict30/0/exit0，补验在w6/report/evidence/R09/r09_commit_verify_20261101_r01。新源/C2构建/全部实际证据仍由我方继续离线归档，稍后给DSH精确提交清单；我方不git add/commit，不push，ENABLE=0，不改冻结物或他方树。
