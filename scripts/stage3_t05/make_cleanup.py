"""S3-T05 阶段三清理（2026-10-22，Wong 授权）。

原则：
  * 只删阶段三名下（tmp/s3r06/t04_* 与 tmp/3/S3-T05/*）**可重建的构建缓存**；
  * 保留 4 个冻结 run 目录与其 ELF 构建树（冻结哈希仍可原位恢复）；
  * 绝不动 report/**、其它阶段目录、主仓 D:\\FPGA_Competition、NA/、clockInfo.txt；
  * 删除前打印完整清单与字节数，并复核冻结产物哈希仍在。
生成 report/evidence/S3-T05/t05_cleanup_20261022_r01/{README.md,manifest.json}
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

WT = r"D:\codex-worktrees\dbdf"
TMP_S3 = os.path.join(WT, "tmp", "s3r06")
TMP_3 = os.path.join(WT, "tmp", "3", "S3-T05")
OUT = os.path.join(WT, "report", "evidence", "S3-T05", "t05_cleanup_20261022_r01")

# 必须保留的阶段三目录（冻结/部署产物与其构建树）
KEEP = {
    "t04_stdluma_20261022_r01",   # 部署位流 + XSA
    "t04_gray_20261021_r01",      # 备选：纯绿灰度
    "t04_dualmsb_20261021_r01",   # 备选：补偿彩色（留档）
    "t04_sof_fix_20261020_r01",   # 无补偿基线（彩色复测用）
    "t04_j11cmos2_elf_v9",        # 复测用 v9_read
    "t04_j11cmos2_elf_v10",       # 部署用 v10_read（实时灰度）
    "t04_j11cmos2_elf_v11",       # 取帧 v11
    "t04_j11cmos2_elf_v12",       # 彩条 v12
}

FROZEN_CHECK = {
    "tmp/s3r06/t04_stdluma_20261022_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit":
        "44e609ccc62647c1748cbeecc64b2fdaa0c53b07db6b7bd1c8a230ca65fc4afb",
    "tmp/s3r06/t04_stdluma_20261022_r01/design_1_wrapper.xsa":
        "90e1bdee1f5baaf9e772edcddc800aab6927d2099b54a45bc020025d82ccb1c4",
    "tmp/s3r06/t04_gray_20261021_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit":
        "2f72aaa42936225eb7215bd8f138f68e52c27c3ab31ab236c8a3c15f7669af4f",
    "tmp/s3r06/t04_dualmsb_20261021_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit":
        "30db09ba8e4e9df8fca73429ce7e941988391b4475fc88d19ebc86469fff23e4",
    "tmp/s3r06/t04_j11cmos2_elf_v10/elf_build/app/an5642_j11cmos2_v10_read.elf":
        "1457cda4867649dce8b54b2ebe9c7bafc0a2a1d4d1deba112adc6f6492306073",
    "tmp/s3r06/t04_j11cmos2_elf_v11/elf_build/app/an5642_j11cmos2_v11_freeze.elf":
        "c01133b1bb0204f07a5be215dbeb58ca0dcc627115cd3a06f1c56f9b21ca26c4",
    "tmp/s3r06/t04_j11cmos2_elf_v12/elf_build/app/an5642_j11cmos2_v12_bars_freeze.elf":
        "527a74fca6ea0774c34625015720a5163fc58557d44c64e29428700fd09845c5",
}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def dsize(p):
    total = 0
    for root, _dirs, names in os.walk(p):
        for n in names:
            try:
                total += os.path.getsize(os.path.join(root, n))
            except OSError:
                pass
    return total


def git(*a):
    return subprocess.run(["git", "-C", WT] + list(a), capture_output=True, text=True).stdout.strip()


def main():
    if os.path.exists(OUT):
        raise SystemExit("REFUSE_OVERWRITE: " + OUT)

    heavy = subprocess.run(["powershell", "-NoProfile", "-Command",
                            "Get-Process | Where-Object { $_.ProcessName -match 'vivado|xsdb|xsim' } | "
                            "Select-Object -ExpandProperty ProcessName"],
                           capture_output=True, text=True).stdout.strip()
    if heavy:
        raise SystemExit("REFUSE_HEAVY_PROCESS_RUNNING: " + heavy)
    lock = subprocess.run(["git", "-C", WT, "rev-parse", "--git-path", "index.lock"],
                          capture_output=True, text=True).stdout.strip()
    if lock and os.path.exists(lock):
        raise SystemExit("REFUSE_INDEX_LOCK: " + lock)

    # 冻结产物复核
    frozen = {}
    for rel, expect in FROZEN_CHECK.items():
        p = os.path.join(WT, rel.replace("/", os.sep))
        ok = os.path.exists(p) and sha256(p) == expect
        frozen[rel] = {"exists": os.path.exists(p), "sha256_matches": ok, "expected": expect}
    if not all(v["sha256_matches"] for v in frozen.values()):
        raise SystemExit("REFUSE_FROZEN_HASH_MISMATCH: " + json.dumps(frozen, ensure_ascii=False))

    # 候选删除清单（只限阶段三名下）
    victims = []
    for name in sorted(os.listdir(TMP_S3)):
        p = os.path.join(TMP_S3, name)
        if not os.path.isdir(p):
            continue
        if not name.startswith("t04_"):
            continue
        if name in KEEP:
            continue
        victims.append((p, name))
    if os.path.isdir(TMP_3):
        for name in sorted(os.listdir(TMP_3)):
            p = os.path.join(TMP_3, name)
            if os.path.isdir(p):
                victims.append((p, "tmp/3/S3-T05/" + name))

    # 安全拒绝：任何 report/ 或非阶段三路径
    for p, label in victims:
        low = os.path.abspath(p).lower()
        if "\\report\\" in low or ".git" in low or "fpga_competition" in low.replace("codex-worktrees\\dbdf", ""):
            raise SystemExit("REFUSE_OUT_OF_SCOPE: " + p)

    os.makedirs(OUT)
    removed = []
    freed = 0
    for p, label in victims:
        size = dsize(p)
        removed.append({"path": os.path.relpath(p, WT).replace("\\", "/"), "bytes": size})
        freed += size
        shutil.rmtree(p, ignore_errors=False)
        print("REMOVED %-42s %10.1f MB" % (label, size / 1048576.0))

    manifest = {
        "run_id": "t05_cleanup_20261022_r01",
        "task": "S3-T05",
        "date": "2026-10-22",
        "authorisation": "Wong 2026-10-22：阶段4/5已开始，阶段三没有用的垃圾可以清理掉",
        "scope": "仅阶段三名下可重建构建缓存：tmp/s3r06/t04_*（除冻结保留项）与 tmp/3/S3-T05/*",
        "kept": sorted(KEEP),
        "kept_reason": "冻结/部署产物与其构建树（冻结哈希仍可原位恢复）",
        "never_touched": ["report/**（全部留档与提交物）", "其它阶段目录", "主仓 D:\\FPGA_Competition", "NA/ 与 clockInfo.txt（非本阶段文件）"],
        "frozen_hash_check_before_delete": frozen,
        "removed": removed,
        "freed_bytes": freed,
        "head_before": git("rev-parse", "HEAD"),
        "safety_gates": {
            "heavy_processes_running": heavy or "none",
            "index_lock": "absent",
            "frozen_hash_mismatch_refused": True,
            "out_of_scope_refused": True,
        },
        "limitations": ["未清理主仓或其它阶段缓存（无授权）", "留在 tmp/ 的冻结 run 目录未压缩/未迁出"],
    }
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8") as f:
        f.write("# 阶段三缓存清理记录（2026-10-22）\n\n")
        f.write("授权：Wong（阶段4/5 已开始，阶段三无用垃圾可清理）。范围仅限阶段三名下可重建构建缓存。\n\n")
        f.write("## 保留（绝不动）\n\n")
        for k in sorted(KEEP):
            f.write("- `tmp/s3r06/%s`（冻结/部署产物与其构建树）\n" % k)
        f.write("- `report/**`、其它阶段目录、主仓、`NA/`、`clockInfo.txt`\n\n")
        f.write("## 删除前冻结哈希复核（全部一致才继续）\n\n")
        for k, v in sorted(frozen.items()):
            f.write("- %s `%s` ⇒ %s\n" % (k, v["expected"][:16], "OK" if v["sha256_matches"] else "MISMATCH"))
        f.write("\n## 已删除（%d 项，合计 %.1f MB）\n\n" % (len(removed), freed / 1048576.0))
        for r in sorted(removed, key=lambda x: -x["bytes"]):
            f.write("- `%s` （%.1f MB）\n" % (r["path"], r["bytes"] / 1048576.0))
        f.write("\n## 安全闸门\n\n- 无 Vivado/xsdb/xsim 运行：%s\n- index.lock：无\n" % (heavy or "是"))
        f.write("- 冻结哈希任一不符即拒绝执行 ✓\n- 越界路径（report/、主仓等）即拒绝执行 ✓\n\n")
        f.write("## 限制\n\n- 未清理主仓与其它阶段缓存（无授权）；留在 `tmp/` 的冻结 run 目录未迁出。\n")
    print("CLEANUP_RECORD=%s" % OUT)
    print("REMOVED_ITEMS=%d FREED_MB=%.1f HEAD=%s" % (len(removed), freed / 1048576.0, git("rev-parse", "--short", "HEAD")))


if __name__ == "__main__":
    sys.exit(main())