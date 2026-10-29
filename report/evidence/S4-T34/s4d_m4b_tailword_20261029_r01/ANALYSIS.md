# M4-b head13 尾字（byte 5,068/5,069）差异定位 —— 结论：**(b) 参考预置口径缺陷**

- 任务：S4-T34 / 共享任务板 `task-2`
- RunId：`s4d_m4b_tailword_20261029_r01`
- 时间：2026-10-29（UTC+8）
- 被查现象：2B 基线位流（sha256 `555a70c2…`）上 M4-b 自检 `done=1 status=0x00000E04 error=0`，
  但 `diff13=2 first13=5068`、`diff26=0 first26=-1`，`pass=0`。

## 0. 结论（先给判定）

**判定 (b)：应用比较/参考口径问题。** 具体是**宿主侧参考预置只写了 5,070//4 = 1,267 个字
= 5,068 B**，head13 尾 word 的 lane 0/1（byte 5,068/5,069）**从未写入 0x12000000**，
比较时读到的仍是候选区快照旧值 `0xFF 0x8F`；而参考文件该 2 字节的有效值是 `0x06 0x05`。
PL 侧不是根因：同一 2B 位流（`555a70c2…`）在 window #6 r03 用**补齐到 5,072 B** 的同一参考
预置时，`diff13=0 diff26=0 stale=1 pass=1`（`bringup_window6_20261028_r03/m4b_uart_r3.log:14,16`）。

- **应用比较范围是正确的**：`s4d_ps_app.c:572-573` 逐字节比较 `S4D_HEAD13_BYTES=5070`
  （`s4d_ps_app.c:320`），没有按字对齐截断，符合 2A 冻结规格（
  `S2A-T01_模型交付规格与G0接口冻结.md:71`：“5,070-byte 的 head13 尾 word 只选择 lane `0011`；
  不得因为 word 对齐而越过其逻辑张量尾部”）。⇒ **不是 (b) 的“比较范围”分支**。
- **真正的 (b) 分支是“参考口径”**：参考数据写入（host `xsdb mwr -bin -file <file> <addr> <words>`）
  的 `words` 参数是 **32-bit 字数**，`5,070 // 4 = 1,267`，尾 2 字节被丢。

## 1. 证据链（可复核）

### E1 参考文件尾部就是有效数据（不是 padding）

`report/evidence/S4-B/20261021_r01/test_fist_000_head13.raw`
（5,070 B，sha256 `07b59ca389890e8ac2ac704d97364e9717164becbbe90950dc10e9ed28d2cab6`）：

| 偏移 | 5,064 | 5,065 | 5,066 | 5,067 | **5,068** | **5,069** |
|---|---|---|---|---|---|---|
| 值 | `0x01` | `0xFF` | `0xFE` | `0x00` | **`0x06`** | **`0x05`** |

⇒ 尾 word（偏移 5,068）lane 0/1 的有效值 = `0x06/0x05`，即该 word 低 16 位 = **`0x0506`**。
文件在 5,070 处结束，lane 2/3（byte 5,070/5,071）不存在于逻辑张量。
（对照：head26 = 20,280 B，`20280 % 4 == 0`，没有半字尾部 ⇒ 不存在同类问题。）

### E2 基线 run r03 的预置命令确实少一个字

`report/evidence/S4-T34/s4d_m4b_baseline_2b_20261029_r03/M4b_pre_ref_head13.log:1`：

```
mwr -bin -file …/test_fist_000_head13.raw 0x12000000 1267
```

1,267 字 × 4 = **5,068 B**，覆盖 byte 0..5,067；byte 5,068/5,069 **未写**。
同 run 的 head26 预置是 `… head26.raw 0x12002000 5070`，5,070 字 = 20,280 B **完整覆盖**
⇒ 两 head 唯一的差别正好是“是否被字粒度截断”，与“只有 head13 有 2 字节差异”完全对应。

### E3 预置后 0x12000000+5,068 的实际内容 = 旧值（漏写实证）

同 run 的候选区 dump（只读解析，见 `tailword_probe.py` / `tailword_probe_output.txt`）：

| 文件 | 字节 5,064..5,071 | 尾 word(5,068) LE |
|---|---|---|
| `W0_dump.bin`（预置后、M4-b 前） | `fa 4a 40 95  ff 8f 2a e0` | `0xE02A8FFF` |
| `W4_dump.bin`（运行后） | `01 ff fe 00  ff 8f 2a e0` | `0xE02A8FFF` |
| 补齐参考（5,072 B，见 E4） | `01 ff fe 00  06 05 00 00` | **`0x00000506`** |

- 字节 5,064..5,067 在预置后**变成了参考文件的值**（`01 ff fe 00`）⇒ 1,267 字确实写到了 5,067；
- 字节 5,068/5,069 在预置前后都是 `FF 8F`（来自 `m3_snapshot_orig.bin` 的既有内容）
  ⇒ **参考尾 2 字节没有被预置**；
- 因此应用在 `s4d_ps_app.c:572` 用 `ff 8f` 作基准比较 `arena[5,068/5,069]`，
  PL 只要写入正确的 `06 05`，就必然得到 `diff13=2 first13=5068`。**这解释了观测到的全部现象。**

### E4 反证 (a)：同一 2B 位流、同一参考、补齐预置时 diff=0

`report/evidence/S4-T34/bringup_window6_20261028_r03/`（2026-10-28，位流同为
`555a70c2…`，见 `IDENT.json:4-8`）：

- 预置改为**补齐文件**：`W2_pre_head13_padded.bin` = head13.raw + 2×`0x00` = 5,072 B
  （sha256 `ad45b1cce3e1f45ceeb4955f4b8aaf2021ba778d78554e5a096ec50aacae8895`），
  按 **1,268 字**写入（`W2_M4b_preload_details.json:10-20`；`W2_pre_head13.log:1`；
  `window_close.txt:10`“preload 尾部补齐（head13 5,070→5,072 B / 1,268 字）”）。
- 结果：`m4b_uart_r3.log:14` `diff13=0 first13=-1 diff26=0 first26=-1`；
  `:16` `M4B RESULT={"pass":1,…,"stale":1,"gate":1,"ack_idle":1,…}`。
- 该 run 还先对输出区投毒（`W2_M4b_preload_details.json:71-90`）使 `stale=1`，排除“读到旧结果”的假通过。

⇒ PL 在该位流上把 5,070 字节（含尾 word 的 lane 0/1）写对了。**(a) 不成立。**

### E5 现存缺陷位置（宿主脚本，非应用源码）

`w4/scripts/stage4_s4b/run_window_b_driver.py`（当前 sha256 `9979fba6…`）`:355`：

```python
pre["jtag_ref_head13"] = jtag_write_file(head13, RAW_BASE, "M4b_pre_ref_head13", HEAD13_BYTES // 4)
```

`HEAD13_BYTES // 4` = 1,267（截断）；同一脚本 `:356` 对 head26 恰好整除，所以 `diff26=0`。
证据归属：`M4b_pre_ref_head13` 这一 JTAG 步骤 tag 在本仓库脚本中**只有**该文件的 `:355` 产生
（`grep -rn 'M4b_pre_ref_head13' --include='*.py'` 仅命中 `run_window_b_driver.py` 与其
`tmp/4/S4-T33_*` 历史副本），而该 run 记录的预置命令正是 1,267 字。
window #6 用的是另一支 `run_bringup_driver.py`（v3.2.6，带 pad 逻辑），因此当时是 PASS；
本轮 2B 基线 run 走的是 `run_window_b_driver.py`，缺陷回归。

### E6 附带发现：基线 run m4b 还有第二个宿主侧前置缺陷（stale=0）

`m4b_uart.log:24` 的 `"stale":0` ⇒ 运行前 `arena[head13_off..+1]` 已等于参考首 2 字节，
“新旧可判别”条件不成立，`pass` 判据（含 `stale==1`）即使在 diff 修好后仍会为 0。
⇒ 关闭时必须同时补“输出区投毒”（window #6 的做法），否则无法关闭。

## 2. 应用侧改动（最小、诊断，不改判据）

`vitis/stage4/ps/s4d_ps_app.c`（本任务独占写区），仅新增尾字取证，**比较范围与 pass 判据一字未改**：

| 位置 | 改动 |
|---|---|
| `:321-325` | 新增 `S4D_HEAD13_TAIL_OFF = (5070 & ~3) = 5,068`，注释引用 2A lane `0011` 规格 |
| `:471-472` | 局部量 `tail13_before/after/ref`、`lane01_ok/lane23_ok` |
| `:496-498` | START 前快照 arena 尾 word（先 invalidate） |
| `:582-595` | done=1 时打印 `M4B TAIL13 off=5068 before=… after=… ref=… lane01_ok=… lane23_ok=…`；
`lane23_ok` 直接检验 2A“不得越过逻辑张量尾部”（PL 是否只选 lane `0011`） |
| `:612-625` | `M4B RESULT` 增补同上 5 个**诊断字段**（driver 用 `json.loads` 只读 `pass`/`gate`，向后兼容） |

判读语义（一次上板即可定案，无需额外 `mrd` 手工步骤）：

- `after` 低 16 位 == `ref` 低 16 位（`0x0506`）⇒ lane 0/1 写得对；
- `after` 高 16 位 == `before` 高 16 位 ⇒ PL 未越过逻辑张量尾部（lane `0011`）；
- 若 `after` 低 16 位 ≠ `0x0506`，或高 16 位被改写 ⇒ 才是 (a)，需转 w2b RTL。

## 3. 重建（新目录，未覆盖原 build 目录）

脚本：`D:\tmp\lead\tailfix_20261029_r01\build_tailfix.sh`（复制自
`D:\tmp\lead\rebuild_timeout_20261029_r01\build_timeout_fix.sh`，只改输出目录与本轮注释；
原脚本/原 build 目录未改动）。
输入源码：`s4d_ps_app.c` sha256 `87a639aa4a5d375d3c25472062abe7e7c93fe77b5c08a499726f5c788b7d9f79`；
链接脚本 `lscript_s4t34.ld` sha256 `c0350ef1…`（见 `build_logs/input_sha256.txt`）。

| 变体 | ELF sha256 | 编译 | 链接 | size/nm |
|---|---|---|---|---|
| chainA | `87e049b4db8f7debd212f91b354648c2e83f845d419048ae5783d1a9923bdc52` | 0 | 0 | 0 / 0 |
| chainB | `06bb0209c81f9286e386ca07de9c4364523c9c16091ac361e43a2e4b95d4e7ae` | 0 | 0 | 0 / 0 |
| m4b | `553fbf7ea7de8bc75edaf99c0b4d5cb79ef39e556e768b91abd459d1cf240e84` | 0 | 0 | 0 / 0 |

- 所有 `preproc/decode/compile/link/size/nm` 退出码均为 0（`build_logs/exit_codes.txt`）；
  两次独立构建 ELF sha256 完全一致（确定性）。
- 唯一告警 `S4D_ST_ERROR redefined`（`:308` 与 `:119`）为**既有**告警，
  原 build 日志 `rebuild_timeout_20261029_r01/logs/app_m4b.log` 内容逐字相同，非本轮引入。
- 与旧 m4b ELF（`aaedaf3c…`）差异：text 38,304→38,800 B（+496 B，纯诊断字符串/代码），
  `data/bss` 不变。功能路径未变，旧 run 的基线结论不受影响。

## 4. 板上取证 / 关闭清单（交 board-runner，一个窗口可完成）

**无需先取证再修**：下述步骤同时是修复验证与取证。地址均为 PS 视角。

1. 装载 **2B 基线位流** sha256 `555a70c2…`（`S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit`）。
2. 候选区恢复照旧（`m3_snapshot_orig.bin` → `0x12000000`，sha256 `41907f53…`）。
3. 参考预置（head13 **必须补到尾 word**，二选一）：
   - **推荐**：`mwr -bin -file …/bringup_window6_20261028_r03/W2_pre_head13_padded.bin 0x12000000 1268`
     （5,072 B，sha256 `ad45b1cc…`；= head13.raw + 2×`0x00`）；
   - 或沿用旧命令后补一条：`mwr 0x120013CC 0x00000506`（= byte 5,068..5,071 = `06 05 00 00`）。
   - head26：`mwr -bin -file …/test_fist_000_head26.raw 0x12002000 5070`（不变）。
4. 陈旧可判别（否则 `stale=0`，必 FAIL）：投毒
   `mwr 0x11A46100` head13 首 64 B = `0xFC`；`mwr 0x11AD5E80` head26 首 64 B = `0xFD`。
5. **附加取证（强烈建议）**：尾 word 投毒，验证 lane `0011` 不越界
   `mwr 0x11A474CC 0x5A5A5A5A`（arena head13 尾 word = `0x10000000 + 0x01A46100 + 5,068`）。
6. 装载新 M4-b ELF sha256 `553fbf7e…`（`D:\tmp\lead\tailfix_20261029_r01\build\s4d_ps_app_sw0_m4b.elf`），
   等 `M4B RESULT=` 行（本轮实测 ~47.3 s / 心跳 log 每 5 s 一行）。
7. 判据（关闭条件，全部满足才算结案）：
   - `pass=1`、`done=1`、`diff13=0`、`diff26=0`、`stale=1`、`gate=1`、`ack_idle=1`；
   - 新增 `M4B TAIL13` 行（未投毒尾 word 时）：`after` 低 16 位 = `0x0506`，`lane01_ok=1`；
   - 若执行了第 5 步：`after=0x5A5A0506`、`lane23_ok=1`（高 16 位仍为 `0x5A5A`）。
8. 若第 7 条不满足：按下列判读分流，只有此时才转 w2b RTL 请求（Codex 写区）：
   - `after` 低 16 位 ≠ `0x0506` ⇒ PL 尾字 lane 0/1 写错 / 未写 ⇒ **(a)**；
   - `after` 高 16 位 ≠ 投毒值 ⇒ PL 越过逻辑张量尾部（违 2A `0011`）⇒ **(a)**；
   - `diff13=0` 但 `pass=0` ⇒ 查 `stale`/`gate`/`ack_idle`，与本 2 字节无关。

## 5. 宿主脚修复建议（不在本任务写区，需 lead 派给脚本 owner / board-runner）

`w4/scripts/stage4_s4b/run_window_b_driver.py:354-355` 最小补丁（与 window #6 已验证做法一致）：

```python
    # head13 = 5,070 B 不是 4 字节整数倍；mwr 的 count 是 32-bit 字数，
    # 5,070//4 = 1,267 字 = 5,068 B ⇒ 尾 2 字节漏写（diff13=2 first13=5068 的根因）。
    h13 = head13.read_bytes()
    h13_pad = h13 + b"\x00" * ((-len(h13)) % 4)          # 5,070 -> 5,072
    h13_out = RUN_DIR / "M4b_pre_ref_head13_padded.bin"
    h13_out.write_bytes(h13_pad)
    pre["jtag_ref_head13"] = jtag_write_file(h13_out, RAW_BASE, "M4b_pre_ref_head13", len(h13_pad) // 4)
```

并建议在该步加断言：`len(h13_pad) % 4 == 0 and len(h13_pad) // 4 >= -(-HEAD13_BYTES // 4)`，
以及 `ASSERT: 尾 word 低 16 位 == 0x0506`（可由 `mrd 0x120013CC 1` 回读校验预置）。

## 6. 限制与未执行项

- 本轮**未接触板卡/JTAG/COM4**，未跑 Vivado；(a) 的排除依据是 2026-10-28 window #6 r03 的
  同一 2B 位流实测（ELF 为 `2404a74e…`，非本轮重建 ELF）；本轮新 ELF 的 `TAIL13` 行可在
  下一次上板时独立复证，二者不矛盾（head 写由 PL 完成，ELF 只配置 CSR 序列并读内存）。
- 未执行：新 ELF 上板、工具链以外的静态分析、RTL 侧检查（无需，属 (a) 分支且未成立）。
- 未改：`D:\tmp\lead\rebuild_timeout_20261029_r01\` 既有文件、w2b 任何文件、git 索引/提交。

## 7. 产物

| 文件 | 说明 |
|---|---|
| `ANALYSIS.md` | 本报告 |
| `tailword_probe.py` / `tailword_probe_output.txt` | 只读复算脚本与输出（参考尾部字节、字数算术、dump 尾 word） |
| `build_logs/` | 三变体编译/链接/size/nm 日志、退出码、输入源码哈希、构建脚本副本 |
| `MANIFEST.sha256` | 本目录产物 sha256 清单（`hash_basis=worktree_disk`） |
| `D:\tmp\lead\tailfix_20261029_r01\build\` | 三个新 ELF（未纳入 git） |