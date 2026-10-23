"""新模块复测证据落档（2026-10-23，Wong 通知新模块到货）。"""
import hashlib
import os
import shutil

WT = r"D:\codex-worktrees\dbdf"
OUT = os.path.join(WT, "report", "evidence", "S3-T05", "t05_new_module_reverify_20261023_r01")
SRC = [
    ("tmp/3/S3-T05/newbars_20261023_r01/bars_newmodule.png", "bars_newmodule.png"),
    ("tmp/3/S3-T05/newbars_20261023_r01/frame_full.bin", "bars_frame_full.bin"),
    ("tmp/3/S3-T05/newmod_retest_20261023_r01/row_y100.bin", "row_y100.bin"),
    ("tmp/3/S3-T05/newmod_retest_20261023_r01/row_y400.bin", "row_y400.bin"),
    ("tmp/3/S3-T05/newmod_retest_20261023_r01/row_y600.bin", "row_y600.bin"),
]

README = """# 新模块复测（2026-10-23，Wong 通知新模块到货）

## 结论：**真彩色恢复，缺位问题消除**

位流/应用：无补偿 SOF 基线 `7cb33068…` + `an5642_j11cmos2_v9_read.elf`（只读）/ `v12_bars_freeze`（彩条）。

### 1. 缺位签名判据（3 行 × 1280 像素，`analyze_missing_msb_signature.py`）
| 行 | maxB | 蓝 bit7 置位率 | 绿 bit4 置位率 |
|---|---|---|---|
| y=100 | 240 | **39.141%** | **50.156%** |
| y=400 | 248 | **25.547%** | **38.047%** |
| y=600 | 248 | **21.719%** | **40.547%** |

旧模块同名判据为 **0.000% / 0.000%**；现判定 **“不符合签名”** ⇒ DVP 数据线已正常。

### 2. 传感器健康度
`S3_DIAG2_CHIPID_TRY0=TRY1=TRY2=0x5640` —— 旧模块仅 TRY0 应答（CMOS1 整路无应答），现三路全部应答。

### 3. 彩条精确复核（`0x503D: 0x00→0x80`，回读 `0x80`；stop→mrd→con 安全转储）
| x | R,G,B | 判读 |
|---|---|---|
| 80 | 248,252,248 | 白（**B5=31 满量程**） |
| 240 | 248,252,56 | 黄 |
| 400 | 48,252,224 | 青 |
| 560 | 32,252,0 | 绿（**G6=63 满量程**） |
| 720 | 216,0,248 | 品红 |
| 880 | 200,0,32 | 红 |
| 1040 | 0,0,192 | 蓝 |
| 1200 | 0,4,0 | 黑 |

旧模块为 白 `B5=15(120)`、绿 `G6=59(236)`；现全部满量程 ⇒ **缺位消除、色相顺序正确（白/黄/青/绿/品红/红/蓝/黑）**。

### 4. 实景行通道统计
`B/R = 0.99 / 0.87 / 0.85`（旧模块 0.45）；`max R/G/B = 248/252/248` ⇒ 三通道均可到满量程；`|R−G| ≈ 13.9–18.2`、`|G−B| ≈ 7.1–16.7`（随场景变化 ⇒ 真实色度，非恒 0）。

## 处置
- **颜色项解除受阻**；板卡已切回**实时彩色**（无补偿基线 + `v10_read`，指纹随画面变化）。
- 灰度补偿位流与证据保留可回退，但**部署按彩色更新**（Wong 原计划：模块到货后更新）。

## 限制
- 未做 ≥30 分钟耐久与温升观测；未做电气/镜头复检（镜头清晰度此前已按“定焦远焦”结论接受）。
- 旧模块（故障件）的证据与结论保留在 `t05_color_msb_missing_20261022_r01/` 与 `t05_freeze_20261021_r01/`，可作返修依据。
"""

HASHES_NOTE = "旧模块对照（签名判据 0.000%/0.000%，白条 B5=15、绿 G6=59）见 t05_color_msb_missing_20261022_r01/。\n"


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    lines = []
    for rel, name in SRC:
        s = os.path.join(WT, rel.replace("/", os.sep))
        d = os.path.join(OUT, name)
        shutil.copy2(s, d)
        lines.append("%s *%s  (source %s)" % (sha256(d), name, rel))
        print("COPIED %-24s %s" % (name, sha256(d)[:16]))
    with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8") as f:
        f.write(README)
    lines.insert(0, "%s *README.md" % sha256(os.path.join(OUT, "README.md")))
    with open(os.path.join(OUT, "hashes.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n" + HASHES_NOTE)
    print("OUT=%s" % OUT)


if __name__ == "__main__":
    main()