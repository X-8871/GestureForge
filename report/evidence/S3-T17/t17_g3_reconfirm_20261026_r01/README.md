# 阶段3 部署 G3 重确认（只读窗口）—— 结果：**未完成**

- RunId：`t17_g3_reconfirm_20261026_r01`
- 时间：2026-10-26（UTC+8）
- 工作树/分支：`D:\codex-worktrees\dbdf` / `codex/stage3-video`；基线 `2ed66096c0f49d89817bf8c33607c7d54f69ac0e`
- 授权依据：Wong 2026-10-26「现在准许你接管阶段三」+「目前已上板，赶快完成阶段三的冻结」；范围为**只读**（不下载、不复位、不写寄存器、不改线）。

## 1. 做了什么（命令与真实退出码）

```
# 链路+目标树（只读）
bash scripts/stage3_t03b/run_xsdb.sh .../scripts/stage3_t17/jtag_t17_link_check.tcl
  → T17_JTAG_LINK=OK；TARGET_COUNT=16；含 APU、Cortex-A9 #0/#1 (Running)、xc7z020；无 DAP 错误
  → T17_JTAG_EXIT=0；wrapper XSDB_EXIT=0

# 只读寄存器探测（halt→mrd→con，含状态闸门与"读失败即停"）
bash scripts/stage3_t03b/run_xsdb.sh .../scripts/stage3_t17/jtag_t17_g3_reconfirm.tcl <空目录>
  → G3R_CONNECT_OK=1；G3R_STATE_AFTER_STOP=Stopped: (Suspended)
  → G3R_FAIL=Memory read error at 0x43010034. Timeout waiting for the Instruction Complete bit
  → G3R_STATE_BEFORE_CON=APB AP transaction error, DAP status 0xF0000021
  → G3R_CON_SKIPPED=STATE_NOT_STOPPED；G3R_EXIT=2（wrapper XSDB_EXIT=0）

# 串口只读 30 s（COM4 @115200）
python scripts/stage3_t03b/read_uart.py COM4 30 <本 RunId>/uart_capture_30s.bin
  → 字节数 0；S3_DIAG_APP_ENTER / SENSOR_ID / DISPLAY_START / VDMA_WRITE_STARTED 四个标记全 MISSING
```

## 2. 观察事实与结论

| 事实 | 含义 |
|---|---|
| JTAG 链/目标树正常（HS1 `210512180081`、`arm_dap`、`xc7z020 23727093`、A9 双核 Running） | 调试链路本身可用；10-26 早前的 DAP `0x30000021` 已由现场断电重启解除（本轮独立验证） |
| `stop` 后状态为 `Stopped: (Suspended)`，随即对 `0x43010034` **读超时** | A9 可停；失败发生在**对 PL 外设地址的 AXI 访问**上 ⇒ 该地址**当前无响应** |
| 读失败后 DAP = `APB AP transaction error, DAP status 0xF0000021`，`con` 被闸门跳过 | DAP 再次被读超时打坏；A9 #0 **停留在 halt**（本脚本按"读失败即停、不重试、非 Stopped 不 con"执行，未连续失败） |
| COM4 30 s **无任何输出**（4 标记全 MISSING） | 当前没有应用在打印（没有 S3_DIAG_* 输出） |
| 无 `hw_server/cs_server` 残留、3121 无监听 | 收窗干净 |

**结论（不夸大）**：**当前板上不是目标部署状态** —— 采集/显示 VDMA（`0x43010000` 区间）不可访问，且无应用输出。最可能是**断电重启后 PL 位流（RAM 配置）已丢失**（本工程从未烧写 QSPI），也不排除 PL 为其它设计；两者都使该地址无响应。因此本轮**没有**完成：部署身份核对（bit/XSA/ELF）、运行期 `ADDR_S2MM`/`ADDR_MM2S` 回读、真彩画面重做。**部署 G3 仍为开放项。**

## 3. 限制与未做项

- **未下载位流**（只读窗口不含下载/烧录）；因此无法在板上恢复目标部署，也无法间接核对 bit/XSA/ELF 身份。
- JTAG 无法读取位流内容哈希 ⇒ 即使部署在位，身份核对也只能是**间接**（配置值/地址/行为），本记录不声称可直接读 hash。
- **副作用披露**：本轮探测导致 DAP 进入错误态且 A9 #0 停留 halt。恢复方式：**现场断电重启**（与 10-26 早前同一手段）；本工程 PL 配置为易失，重启后需重新下载位流才能恢复目标部署。
- 未做电气测量、未烧 QSPI、未改接线。

## 4. 要达到可冻结的 G3，所需的最小窗口（建议）

1. 现场**断电重启**恢复 DAP/A9；
2. 新窗口（**含下载授权**）：下载无补偿 SOF 位流 `7cb33068…` + `an5642_j11cmos2_v10_read.elf` `1457cda4…`；
3. 窗口内：回读 `ADDR_S2MM`/`ADDR_MM2S`/`STRIDE`/`HSIZE`/`VSIZE`/`CR`/`SR`，抓 UART `S3_DIAG5_CFG`/`S3_DIAG9_PAD` 行，转储 3 行做位完整性判据；
4. **真彩目视由 Wong 重做并记录原话**（当前部署变更后旧目视已失效）；
5. 之后方可判"当前部署 G3 重确认 PASS"，并结合 VDMA/task-11 的处置决定阶段3能否冻结。