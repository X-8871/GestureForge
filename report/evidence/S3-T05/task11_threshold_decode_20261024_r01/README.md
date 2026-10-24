# task-11 阈值 LUT 静态解码

- RunId：`task11_threshold_decode_20261024_r01`
- 源码基线：`1d54894be4d547955034eeff8bce853dd4286fac`（`codex/stage3-video`）
- 结论标签：`PASS_STATIC_THRESHOLD_DECODE`
- 本记录只验证冻结 OOC 综合后网表中一个 LUT4 的静态组合函数。

## 冻结输入与网表连接

| 输入 | SHA-256 | 字节数 |
|---|---|---:|
| `board/stage3/software/sensor/alinx_ov5640_sof_hrefgap.patch` | `fd854a622b52c32a43a6770be3f583cce29864a764845c313b623514c91ab2c5` | 2,204 |
| `tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/design_1_alinx_ov5640_0_0_synth_1/design_1_alinx_ov5640_0_0_sim_netlist.v` | `7b8f457c1cd5377367b3032369ba72fc5d00ac465629ecd970d6fb7e479b852a` | 227,006 |

网表顶层将 `cmos_hblank_low_cnt_reg[15:14]` 连接到 `cmos_8_16bit_m0.S`；该模块声明 `input [1:0]S`。`s_axis_tuser_i_2` 是 `LUT4`，`INIT=16'h00A8`，输入映射为 `I0=current hblank`、`I1=S[1]`、`I2=S[0]`、`I3=cmos_hblank_d0`。因此 LUT 地址位序为 `I0 + 2×I1 + 4×I2 + 8×I3`，INIT 的置位地址为 3、5、7，对应：

```text
current_hblank && (counter[15] || counter[14]) && !previous_hblank
```

对 16 位无符号计数器，`counter[15] || counter[14]` 等价于 `counter >= 16384`。

## 穷举结果

脚本枚举全部 `65536 × 2 × 2 = 262144` 组计数器、当前 hblank 和前一拍 hblank 输入：

- LUT 输出为真的组合数：`49152`
- 阈值参考函数为真的组合数：`49152`
- 真值表差异：`0`
- `result.json` 的 verdict：`PASS_STATIC_THRESHOLD_DECODE`

期望真值数由计数器范围 `[16384, 65535]` 的 49,152 个取值乘以唯一满足 `current_hblank=1, previous_hblank=0` 的输入组合得到。

## 复现

在 Windows PowerShell 中运行以下命令；本次退出码为 `0`：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'D:\codex-worktrees\dbdf\report\evidence\S3-T05\task11_threshold_decode_20261024_r01\decode_threshold.py'
```

脚本只读取冻结补丁、OOC 网表和 Git HEAD/分支，并以排他方式在本 RunId 目录创建 `result.json`；若输出已存在则拒绝覆盖。Python 版本为 `3.12.14`，Git 版本为 `2.56.0.windows.2`。

证据目录包装检查最终返回 `CHECKS_OK`、退出码 `0`。首版清单曾因把 `.runs` 生成目录内的网表列入 `files` 而被检查器拒绝（退出码 `1`）；修正后保留网表完整路径/SHA-256 于 `result.json`，并在 manifest 检查说明中再次绑定。该检查只验证清单与目录文件绑定，不代表 G0/G4/G5。

最终包装检查命令：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'D:\FPGA_Competition\verification\check_stage_delivery.py' --mode evidence --project-root 'D:\codex-worktrees\dbdf' --manifest 'report/evidence/S3-T05/task11_threshold_decode_20261024_r01/manifest.json'
```

## 限制

结论仅说明当前 SHA-256 固定的 OOC 网表 LUT4 组合真值表等价于 `16384` 阈值判定。它不证明 RTL 与网表的顺序等价，也不证明计数器的状态更新、复位、饱和行为或 `cmos_hblank_d0` 的周期关系。没有执行 Vivado、仿真或硬件操作；不得将本结论写成完整 task-11 网表等价性通过。
