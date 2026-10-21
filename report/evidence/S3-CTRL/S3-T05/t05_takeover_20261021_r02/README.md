# S3-T05 接管与蓝位重建落点纠正

日期：2026-10-21（UTC+8）。基线 `d476df8db21614df35bb3ccb11843b1beca88212`，工作树 `D:\codex-worktrees\dbdf`，分支 `codex/stage3-video`。

## 接管核验

两份交接原文及主仓库 AGENTS 已完整读取。DSH 的 OFFERED 声明与 Wong 本轮明确接管指令一致；STATE 依次写入 CLAIMED、IN_PROGRESS。接管时无 index.lock、Vivado/xsim 重型任务、hw_server 或 TCP 3121 监听，仅发现原有 `NA/`、`clockInfo.txt`。没有结束任何进程。

`takeover_record.json` 保存本轮归属声明；`handoff_check.json` 保存检查器命令、真实退出码 **0** 和输出。前一次 r01 因缺少 manifest 导致退出码 1，原样保留；没有把末尾成功命令的退出码当作前一检查结果。

## 纠正“补丁没有进入运行设计”

旧运行 `tmp/s3r06/t04_bluefix_20261020_r01` 的综合日志实际读取该运行的 `.gen/.../ipshared/564b/src/alinx_ov5640.v`。OOC 功能网表中，FIFO RAM 的写入端对低 5 位实现 `{b3,b2,b1,b0,b3}`。这是已综合的真实连接，不是仅检查源文件中存在标记。

转换器综合网表和 `rgb2dvi.vhd` 共同给出以下端到端映射：

| 相机输入字字段 | DDR 字节偏移 | HDMI 颜色 | 旧补丁作用 |
|---|---|---|---|
| `tdata[15:11]` | 0 | 蓝 | 不变，仍 0…120 |
| `tdata[10:5]` | 1 | 绿 | 不变 |
| `tdata[4:0]` | 2 | 红 | 被重建 |

补丁后的三个历史样本（本目录 `samples/01`～`03`）的 offset2 均精确落在 `{0,16,…,112,136,152,…,248}`，与该公式的 16 档字母表完全一致；offset0 仍为 0…120、步长 8。未打该补丁的 J10 对照样本 offset2 含普通 5 位量化值。原始输入、下载日志、bit、XSA、RTL 和结构网表均在 JSON 中以 SHA-256 绑定。

因此旧修复已进入运行设计，但改错了显示通道；不能据此重建缓存、替换另一份源，或归咎于下载了错误位流。原有 bit/XSA 和采样文件均保留。

## 重建公式及根因边界

既定近似策略为 `b'=2*(b mod 16)+floor((b mod 16)/8)`。对显示蓝而言，应作用于输入字的**高 5 位**，同时保留 `tdata[10:0]`。

旧注释“只改 bit4”及 `b+(b>=8?16:0)` 均与实际拼接式不符；拼接会重映射该颜色的全部 5 位。此处是近似拉伸，不能恢复真实丢失的最高位，不能声称色彩保真。

还观察到所有已检查的绿色样本均无字节 bit4。显示蓝 bit7 对应输入字 bit15，绿 bit4 对应输入字 bit7；二者都是 DVP 字节的最高位，即 `cmos_d[9]`。这与旧归因 `cmos_d[6]` 不符。该模式提示需检查共同数据路径最高位，但**尚不能证明模块/传感器硬件故障**。本轮蓝通道最小修复不顺便修改绿色数据。

## 复核命令和限制

```bash
python -B scripts/stage3_t05/analyze_channel_mapping.py \
  --worktree D:/codex-worktrees/dbdf \
  --output D:/codex-worktrees/dbdf/report/evidence/S3-CTRL/S3-T05/t05_takeover_20261021_r02
```

本次真实退出码 0。重跑必须换新输出目录；r02 已存在，脚本会拒绝覆盖。

本报告是旧产物的离线复核，没有重新下载或采样；历史采样时间绑定仍依赖旧日志。尚无本轮实机修复结论，G3/G4/G5 未通过。绿色缺位、既有时序方法学警告和长时间运行验收均未关闭。
