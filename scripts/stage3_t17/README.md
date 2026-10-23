# scripts/stage3_t17：阶段3 色彩复测工具（task-17）

到货前离线准备 + 到货后一键复测。全部工具**默认不接触硬件**；硬件阶段需双前提放行。判定口径见
`report/evidence/S3-T17/t17_color_retest_prep_20261023_r01/t17_judgement_table.json`。

| 工具 | 作用 | 是否碰硬件 |
|---|---|---|
| `run_t17_color_retest.sh` | 一键执行器：`preflight`/`judge`/`link`/`baseline`/`bars`/`all` | `preflight`/`judge` 离线；其余需放行 |
| `analyze_t17_bit_integrity.py` | 位完整性/真彩（机器部分）判定器，含 `--selftest` | 否 |
| `check_t17_preflight.py` | 离线前置：分支/HEAD/锁/重型进程 + 冻结产物实算哈希 + 硬件门禁 | 否 |
| `jtag_t17_link_check.tcl` | 只读 JTAG 链路确认（用 `llength [targets]`/`jtag targets` 判定） | 是（只读） |
| `jtag_t17_dump_rows.tcl` | 安全转储 halt→mrd→con；**base/stride 必须显式传入** | 是（只读） |
| `make_t17_manifest.py` | 实测后打 manifest + hashes（退出码只接受真实值） | 否 |

## 常用命令

```bash
# 离线（随时可跑，不动板）
bash scripts/stage3_t17/run_t17_color_retest.sh preflight --run-id t17_color_retest_20261023_r01
python -B scripts/stage3_t17/analyze_t17_bit_integrity.py --selftest
python -B scripts/stage3_t17/analyze_t17_bit_integrity.py --frame <frame_full.bin>

# 到货后（需 Wong 开工信号 + 硬件窗口书面确认，并先填 report/evidence/S3-T17/hw_authorization.json）
bash scripts/stage3_t17/run_t17_color_retest.sh all --run-id t17_color_retest_20261023_r01 --allow-hardware
```

## 硬件安全规则（已内建）

1. `link`/`baseline`/`bars` 需要同时满足：显式 `--allow-hardware` **且** `report/evidence/S3-T17/hw_authorization.json`
   的 `wong_go`、`codex_hw_release` 均为 true；否则**退出 3 且不动板**（离线实测已验证）。
2. 只做易失 JTAG（下载 bit/ELF、halt→mrd→con 只读、写 0x503D 彩条并恢复）；**不烧 QSPI、不改接线**。
3. 自起的 `hw_server` 用完即终止；运行前**已存在**的他人会话一律不终止（只记录）。
4. 转储前必须从运行期回读 `ADDR_S2MM`/`STRIDE_S2MM`；**禁止**使用脚本内建旧地址（本目录的 TCL 不提供默认值）。
5. 每个 RunId 一次；证据目录与输出目录**拒绝已存在**，不覆盖旧轮次。
6. 一次只跑一个重型任务；`preflight` 会先查重型进程与 `index.lock`。

## 判定器退出码（与旧脚本语义相反，报告须注明所用脚本）

| 码 | 含义 |
|---|---|
| 0 | `BIT_INTEGRITY_PASS`（C1–C7 全通过） |
| 1 | `DEFECT_REPRODUCED`（复现「两字节 MSB 同时丢失」旧签名） |
| 2 | `USAGE_OR_INPUT_ERROR`（缺文件/长度非法/彩条段不足） |
| 3 | `INCONCLUSIVE_ATYPICAL`（非典型，需人工判读，不得当通过） |

旧 `scripts/stage3_t05/analyze_missing_msb_signature.py`：`0=符合旧缺位签名`、`1=不符合` ⇒ **不可混用**。