r"""P3d 诊断窗口 r03 的离线重判（只读 r03 原始日志，不碰板卡）。

原因：`mrd -value` 在本机 XSDB 上返回**十进制**字符串，而 runner 当时按十六进制解析，
导致 VDMASR=69633 被读成 0x69633（错误位判据误报）。本脚本按十进制重解析同一份 raw_log，
写出 `S8_reg_snapshot_rejudged.json`、`rejudge.txt`，并把结论追加到 `rejudge.txt`
（原始 S8/S9 证据保留不改）。
"""
import json
import re
import hashlib
from pathlib import Path

RUN = Path(r"D:\codex-worktrees\w4\report\evidence\S5-T01\s5_g3_a_oen0_20261030_r03")
raw = json.loads((RUN / "S8_reg_snapshot.json").read_text(encoding="utf-8"))
body = raw["raw_log"].split("exit=", 1)[-1] if "exit=" in raw["raw_log"] else raw["raw_log"]

REG_ADDR = {
    "VTC_CTL": 0x43C30000,
    "VTC_GTSTAT": 0x43C30064,
    "VTC_STATUS": 0x43C30004,
    "VDMA_MM2S_VDMACR": 0x43C40000,
    "VDMA_MM2S_VDMASR": 0x43C40004,
    "VDMA_PARKPTR": 0x43C40028,
}
vals = {}
for name in REG_ADDR:
    m = re.search(r"REG\s+" + re.escape(name) + r"\b.*?VAL[=\s]+(\S+)", body)
    if m:
        tok = m.group(1).strip()
        vals[name] = int(tok, 16) if tok.lower().startswith("0x") else int(tok, 10)
rblk = ""
if "RBLK_BEGIN" in body and "RBLK_END" in body:
    rblk = body.split("RBLK_BEGIN", 1)[1].split("RBLK_END", 1)[0].strip()
rblk_words = []
for ln in rblk.splitlines():
    for tok in ln.split():
        if re.fullmatch(r"[0-9A-Fa-f]{8}", tok):
            rblk_words.append(int(tok, 16))

ctl = vals.get("VTC_CTL")
gt = vals.get("VTC_GTSTAT")
sr = vals.get("VDMA_MM2S_VDMASR")
cr = vals.get("VDMA_MM2S_VDMACR")
vtc_ok = bool(ctl is not None and (ctl & 0x5) == 0x5 and gt)
err_bits = (sr & 0x38) if isinstance(sr, int) else None          # DMAIntErr/SlvErr/DecErr
err_irq = bool(isinstance(sr, int) and (sr & 0x1000))
halted = bool(isinstance(sr, int) and (sr & 0x1))
rblk_ok = bool(rblk_words) and rblk_words[0] == 0x53355253 and len(rblk_words) >= 8 and rblk_words[2] == 3
out = {
    "note": "离线重判：仅修正 mrd -value 十进制解析口径（原 S8/S9 保留）；同一份原始日志，无新硬件运行",
    "source_raw_log_sha256": hashlib.sha256(raw["raw_log"].encode("utf-8")).hexdigest(),
    "values_decimal": vals,
    "values_hex": {k: hex(v) for k, v in vals.items()},
    "vtc_generating": {"ctl": hex(ctl) if ctl is not None else None, "ctl_bit0_sw": bool(ctl & 0x1),
                       "ctl_bit2_ge": bool(ctl & 0x4), "gtstat": gt, "ok": vtc_ok},
    "vdma": {"dmacr": hex(cr) if cr is not None else None,
             "dmacr_bit1_circular": bool(isinstance(cr, int) and (cr & 0x2)),
             "sr": hex(sr) if sr is not None else None,
             "sr_halted_bit0": halted, "sr_dma_err_bits_3_4_5": err_bits,
             "sr_err_irq_latched_bit12": err_irq,
             "no_dma_transfer_err": err_bits == 0},
    "result_block_words": ["0x%08x" % w for w in rblk_words],
    "result_block_magic_ok": rblk_ok,
    "judgement": {
        "app_pass1": True,
        "vtc_generating": vtc_ok,
        "vdma_no_transfer_err": err_bits == 0,
        "result_block_magic_nbox": rblk_ok,
        "caveat": "VDMA SR bit12(Err_Irq) 已置起，但 DMAIntErr/SlvErr/DecErr(bit3/4/5)=0，且应用自测 vdma_err=0；"
                  "sr 原始值 bit16 超出 PG020 文档位域，需 hw 侧确认是否为 stop 时序/读口径引起",
    },
}
(RUN / "S8_reg_snapshot_rejudged.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n",
                                                  encoding="utf-8", newline="\n")
txt = [
    "## 离线重判（mrd -value 十进制口径修正；同一份 raw_log，无新硬件运行）",
    "",
    "| 寄存器 | 十进制 | 十六进制 |",
    "|---|---|---|",
]
for k, v in vals.items():
    txt.append(f"| {k} | {v} | {hex(v)} |")
txt += [
    "",
    f"- VTC 生成：CTL=0x{ctl:08x}（bit0 SW=1、bit2 GE=1）、GTSTAT={gt} ⇒ **{'OK' if vtc_ok else 'NO'}**",
    f"- VDMA：DMACR=0x{cr:08x}（Circular={'1' if (cr & 2) else '0'}、RS={'1' if (cr & 1) else '0'}），"
    f"SR=0x{sr:08x}（Halted={1 if halted else 0}、DMAErr(bit3/4/5)=0x{err_bits:x}、Err_Irq(bit12)={1 if err_irq else 0}）",
    f"- 结果块首 8 word：{' '.join('0x%08x' % w for w in rblk_words)} ⇒ magic=0x53355253、word2(nbox)=3 ⇒ **{'OK' if rblk_ok else 'NO'}**",
    "- 注意：SR bit12 Err_Irq 已置起但 DMA 传输错误位为 0；SR 原始值含 bit16（超出 PG020 位域），需 hw 侧确认读口径/停机时序。",
    "",
]
(RUN / "rejudge.txt").write_text("\n".join(txt) + "\n", encoding="utf-8", newline="\n")
print("\n".join(txt))