r"""更新 MVP 文档：接入 per-frame ACK 修复后的 SHA 与 status 语义（r04）。"""
from __future__ import annotations

import sys
from pathlib import Path

OUT = Path(r"D:\tmp\lead\mvp_infer_20261031_r01")
CHECK = OUT / "MVP_CHAIN_CHECKLIST.md"
IFACE = OUT / "MVP_RESULT_INTERFACE.md"

OLD_CORE1 = "1acf5d8151e9c6fdb2f96a2335da6496af8c5248357bacd1c1e19eb40f345de5"
NEW_CORE1 = "5806d33de1e888bb8b4fb2f63ef64246087316b4335f8b74fbba0710d0b48270"
OLD_CORE0 = "3889c705c9d20723c464d2e68e6aba3cfdc8c724c61c6d82b4e67179217d9721"
NEW_CORE0 = "a5e22651f53b3dcd00e6514034712f1287acb911ee6444bad08e256b5a0f2d47"

INTERFACE_ADD = f"""
---

## 12. rev r04 追加（2026-11-01 03:4x）：**每帧 ACK 修复** + `status` 语义与显示门控

### 12.1 根因（r08/r09 `status=0` 不是写字段 bug）

`0x20800000` dump：`frame_id=0x37A(890)`、`n_dets=0`、`cap/inf` 均停在上电 ~183 s、**`status=0`**。
890 帧 / 183 s ≈ **0.2 s/轮** —— 真网络一轮 47 s，说明 **START 每轮瞬间被拒**：

- 2B 引擎每帧 DONE_SAFE 后必须 **ACK**（读 epoch → 写 `ACKLO/ACKHI` → `CMD=4`）才回 `IDLE|SAFE_REUSE`；
- S4-B 主机路径的 ACK 由 **host 发 `OP_ACK`**；MVP 自循环原先**没有 ACK** ⇒ 下一轮 `s2b_network_start_from_tensor()`
  在 `is_idle()` 失败处返回 **-2** ⇒ 走错误路径 `publish(status=0)` ⇒ 显示侧 `result_not_valid`。
- 所以：**`status=0` 是 ACK 缺失的后果**，不是 status 字段写错；只改 status 掩码会掩盖引擎状态坏掉的事实。

### 12.2 修复内容（本 ELF）

1. 每帧 `DONE_SAFE` 后自动 ACK：`s4d_mvp_ack()`（epoch 双读 → `ACKLO/ACKHI` → `CMD=4` → 轮询回到
   `IDLE && SAFE_REUSE && !OWNER_PL/AXI_PENDING/HEAD_VALID/TERMINAL/FIRST_PENDING`）。
2. 网络失败路径先尽力 ACK 再发布 `status=0`（避免后续每轮空转 -2），并打印 `MVP ERR network rc=…`。
3. **status 语义（已按 lead 要求）**：
   - 一帧被处理（成功跑完网络+解码，**包括 `raw_nz==0`、`n_dets==0`**）⇒ `status = 0x1`（valid）；
   - 只有网络/解码真正失败（`rc≠0`）⇒ `status = 0`（invalid）；
   - **不置 stale(bit2)**、不置 overrun(bit1)：47.3 s/轮下置 stale 只会让 HUD 变告警色，无意义（见 §12.3）。
4. 发布顺序不变：`dets/帧号/cap/inf/status` → flush+`dsb` → **最后写 magic** → flush+`dsb`（status 在 magic 之前）。
5. 回读自检（每帧）：发布后 invalidate + 重读，校验 `magic/status/n_dets`：
   - 失败打印 `MVP ASSERT FAIL s5rs magic=… status=… n=… exp(…)`；
   - `raw_nz==0` 时打印 `MVP CHECK raw_blank status=0x1 n_dets=0 (exp status=0x1 n=0) OK/FAIL`。
6. 编译期断言：`S5_RESULT_ST_VALID==1`、且 `(VALID & STALE)==0`（MVP 不置 stale）。

### 12.3 显示侧门控关系（已核 `s5_display_app.c` / `s5_real_source.c`）

- `S5Real_Parse`：先判 `magic`，再判 **`status.valid`(bit0)**；`valid=0` ⇒ 返回 `result_not_valid`，
  显示侧便走 fallback（raw 有效→`src=real_nobox`，raw 全零→`src=test`）。**这是"灰底"的直接门控**，所以
  `status.valid=1` 对 MVP 必需。
- `stale`(bit2)：仅影响 HUD 颜色（`S5_COLOR_WARN`），**不参与 `pass` 判定**、不改变 `src`；
  显示侧另有 `age_ms>200 ms → AGE_OVER` 仅作 HUD 提示。47.3 s/轮下 AGE 必然 >200 ms，属预期。
- `S5DISP RESULT.pass` 只看：`vdma_init_ok`、`vdma_err==0`、`frames>0`、帧完整性抽检、`src!=sim`；
  与 `n_dets` 无关。故 `n_dets=0`（有帧无手势）**不影响 pass**。

### 12.4 ELF 身份（r04，旧 SHA 作废）

| 变体 | SHA-256 | 字节 |
|---|---|---|
| `s4d_ps_app_mvp_core1.elf`（**上板用**） | `{NEW_CORE1}` | 267,888 |
| `s4d_ps_app_mvp.elf`（core0 单机备选） | `{NEW_CORE0}` | 267,888 |
"""

CHECK_EXTRA = f"""
## 附：r04 变更（2026-11-01 03:4x）—— 必读

- **ELF 已更新（含每帧 ACK 修复）**，SHA 见「0. 先核身份」最新表（core1 `{NEW_CORE1[:12]}…`）；旧 `{OLD_CORE1[:8]}…` 作废。
- **`status` 期望值**：`MVP S5RS … status=0x1`；若见 `status=0x0` ⇒ 网络/解码失败（看紧邻 `MVP ERR network rc=…`
  行；最常见 `rc=-2` = 上一轮未 ACK/引擎未回 idle）。**不得**把 `status=0` 当作"可接受"。
- **新增自检行**：`MVP CHECK raw_blank status=0x1 n_dets=0 (exp status=0x1 n=0) OK`
  （相机未通时出现；FAIL 则逐轮 `MVP ASSERT FAIL`）。
- `stale` 位：生产端**不置**（bit2=0）；显示侧 stale 只影响 HUD 颜色，不影响 `pass`/`src`。
- M4 判据不变；M5 增加一条：`MVP S5RS … status=0x1` ≥1。
"""


def main() -> int:
    c = CHECK.read_text(encoding="utf-8")
    c = c.replace(OLD_CORE1, NEW_CORE1).replace(OLD_CORE0, NEW_CORE0)
    c = c.replace("`MVP S5RS frame=<k> n_dets=<0..15> magic=0x53355253`",
                  "`MVP S5RS frame=<k> n_dets=<0..15> magic=0x53355253 status=0x1`")
    c = c.replace("MVP S5RS frame=0 n_dets=1 magic=0x53355253",
                  "MVP S5RS frame=0 n_dets=1 magic=0x53355253 status=0x1")
    c += CHECK_EXTRA
    CHECK.write_text(c, encoding="utf-8", newline="\n")

    i = IFACE.read_text(encoding="utf-8")
    i += INTERFACE_ADD
    IFACE.write_text(i, encoding="utf-8", newline="\n")
    print("[OK] docs updated:", CHECK.name, IFACE.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())