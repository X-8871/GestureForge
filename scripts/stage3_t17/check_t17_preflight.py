#!/usr/bin/env python3
"""S3-T17 到货后复测的离线前置检查（只读，不接触硬件）。

检查内容（全部离线）：
  1. 工作树 / 分支 / HEAD / index.lock / 未提交改动（交由 handoff 契约的同一口径，但不重复实现状态机）；
  2. 重型进程（vivado/xsim/xelab/xvlog/hw_server/cs_server/xsdb）；
  3. 复测所需冻结产物的**实际存在性与 SHA-256**（缓存已被清理过，不得凭历史 manifest 推断存在）；
  4. 硬件门禁：是否存在 `hw_authorization.json`（Wong 开工信号 + 硬件窗口书面让出/时间窗）。

退出码：
  0 = OFFLINE_GO（离线前置通过；是否可动板另看 hardware_window_confirmed）
  1 = OFFLINE_NO_GO（存在硬性失败项，不得开始）
  2 = 用法/环境错误

边界：本脚本只读，不启动 hw_server、不下载、不烧录、不改任何文件。
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

UTC8 = timezone(timedelta(hours=8))
WT = "D:/codex-worktrees/dbdf"
EXPECTED_BRANCH = "codex/stage3-video"
EXPECTED_HEAD = "f94c25ff2bd539e2ca45b450334ddc8bb8cde6e7"
HEAVY = ("vivado", "xsim", "xelab", "xvlog", "hw_server", "cs_server", "xsdb")

# 到货后复测所需冻结产物（哈希取自各证据包与冻结记录，读取前逐项实算比对）
REQUIRED_ARTIFACTS = [
    {
        "id": "baseline_bit_sof_fix",
        "path": "tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit",
        "sha256": "7cb330685260ced38636d3e90a92160979b0f88770d380269e9864722ce48710",
        "role": "无补偿原始基线位流（真彩/位完整性复测必须用它，禁用灰度或补偿位流）",
    },
    {
        "id": "baseline_xsa_sof_fix",
        "path": "tmp/s3r06/t04_sof_fix_20261020_r01/design_1_wrapper.xsa",
        "sha256": "1f5b138e693065c6257e29075018f7654d4c3a6b67dcab051f0ea8ac106cb0e3",
        "role": "与基线位流配套的 XSA（PS 初始化/BSP）",
    },
    {
        "id": "elf_v9_read",
        "path": "tmp/s3r06/t04_j11cmos2_elf_v9/elf_build/app/an5642_j11cmos2_v9_read.elf",
        "sha256": "b2e8fa55322da275ef6de2a79f3571ec694b9863d7797e1981104b92a02097b5",
        "role": "只读回读 ELF（配置侧排除 + 回读寄存器）",
    },
    {
        "id": "elf_v10_read",
        "path": "tmp/s3r06/t04_j11cmos2_elf_v10/elf_build/app/an5642_j11cmos2_v10_read.elf",
        "sha256": "1457cda4867649dce8b54b2ebe9c7bafc0a2a1d4d1deba112adc6f6492306073",
        "role": "灰度/实时部署应用（init 表会把 0x503D 写回 0x00，用作彩条模式恢复）",
    },
    {
        "id": "elf_v12_bars_freeze",
        "path": "tmp/s3r06/t04_j11cmos2_elf_v12/elf_build/app/an5642_j11cmos2_v12_bars_freeze.elf",
        "sha256": "527a74fca6ea0774c34625015720a5163fc58557d44c64e29428700fd09845c5",
        "role": "写 0x503D=0x80 内部彩条（仅易失）+ 停流保持；使用前必须回读原值、用后恢复",
    },
    {
        "id": "deployment_bit_stdluma",
        "path": "tmp/s3r06/t04_stdluma_20261022_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit",
        "sha256": "44e609ccc62647c1748cbeecc64b2fdaa0c53b07db6b7bd1c8a230ca65fc4afb",
        "role": "当前部署灰度位流（复测结束后如需回到灰度部署状态，用它恢复）",
    },
    {
        "id": "deployment_xsa_stdluma",
        "path": "tmp/s3r06/t04_stdluma_20261022_r01/design_1_wrapper.xsa",
        "sha256": "90e1bdee1f5baaf9e772edcddc800aab6927d2099b54a45bc020025d82ccb1c4",
        "role": "当前部署灰度 XSA",
    },
    {
        "id": "analyzer_t17",
        "path": "scripts/stage3_t17/analyze_t17_bit_integrity.py",
        "sha256": None,
        "role": "本轮判定器（哈希在本轮 prep 清单中登记）",
    },
]


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run_git(args, cwd):
    cmd = ["git", "--no-optional-locks", *args]
    try:
        cp = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", check=False)
    except OSError as exc:
        return None, f"无法执行 git：{exc}"
    if cp.returncode != 0:
        return None, (cp.stderr or "").strip() or f"git 退出码 {cp.returncode}"
    return (cp.stdout or "").strip(), None


def detect_heavy():
    if os.name == "nt":
        try:
            cp = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True,
                                text=True, encoding="utf-8", errors="replace", check=False)
        except OSError as exc:
            return None, f"tasklist 不可用：{exc}"
        if cp.returncode != 0:
            return None, f"tasklist 退出码 {cp.returncode}"
        hits = []
        for row in csv.reader(io.StringIO(cp.stdout or "")):
            if len(row) >= 2 and row[0].strip():
                name = os.path.basename(row[0].strip()).casefold()
                if name.endswith(".exe"):
                    name = name[:-4]
                if name in HEAVY:
                    hits.append({"image": row[0].strip(), "pid": row[1].strip()})
        return hits, None
    try:
        cp = subprocess.run(["ps", "-A", "-o", "comm="], capture_output=True, text=True, check=False)
    except OSError as exc:
        return None, f"ps 不可用：{exc}"
    hits = [{"image": line.strip(), "pid": ""} for line in (cp.stdout or "").splitlines()
            if os.path.basename(line.strip()).casefold().split(".")[0] in HEAVY]
    return hits, None


def main(argv):
    ap = argparse.ArgumentParser(description="S3-T17 离线前置检查", allow_abbrev=False)
    ap.add_argument("--worktree", default=WT)
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args(argv)

    wt = os.path.abspath(args.worktree)
    report = {"created_utc8": datetime.now(UTC8).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
              "worktree": wt, "checks": {}, "hardware_window_confirmed": False}
    fails = []

    if not os.path.isdir(wt):
        report["verdict"] = "USAGE_OR_ENV_ERROR"
        report["reason"] = f"工作树不存在：{wt}"
        report["exit_code"] = 2
        print(report["reason"])
        return 2

    branch, err = run_git(("rev-parse", "--abbrev-ref", "HEAD"), wt)
    head, err2 = run_git(("rev-parse", "HEAD"), wt)
    status, err3 = run_git(("status", "--short"), wt)
    lockpath, err4 = run_git(("rev-parse", "--git-path", "index.lock"), wt)
    report["checks"]["git"] = {
        "branch": branch, "head": head,
        "branch_ok": branch == EXPECTED_BRANCH, "head_ok": head == EXPECTED_HEAD,
        "status_short": (status or "").splitlines(),
        "index_lock_path": lockpath,
        "index_lock_present": bool(lockpath) and os.path.lexists(lockpath if os.path.isabs(lockpath) else os.path.join(wt, lockpath)),
        "errors": [e for e in (err, err2, err3, err4) if e],
    }
    if not report["checks"]["git"]["branch_ok"]:
        fails.append(f"分支不是 {EXPECTED_BRANCH}：{branch}")
    if not report["checks"]["git"]["head_ok"]:
        fails.append(f"HEAD 不是本轮基线 {EXPECTED_HEAD}：{head}")
    if report["checks"]["git"]["index_lock_present"]:
        fails.append("存在 index.lock：可能有未完成的 git 写操作，不得动板")

    hits, perr = detect_heavy()
    report["checks"]["heavy_processes"] = {"hits": hits, "probe_error": perr}
    if hits:
        fails.append("存在重型进程占用：" + "、".join(f"{h['image']}(pid={h['pid']})" for h in hits))

    artifacts = []
    for item in REQUIRED_ARTIFACTS:
        p = os.path.join(wt, item["path"].replace("/", os.sep))
        entry = {"id": item["id"], "path": item["path"], "role": item["role"],
                 "expected_sha256": item["sha256"], "exists": os.path.isfile(p)}
        if entry["exists"]:
            entry["actual_sha256"] = sha256_file(p)
            entry["size_bytes"] = os.path.getsize(p)
            entry["sha256_ok"] = (item["sha256"] is None) or (entry["actual_sha256"] == item["sha256"])
        else:
            entry["sha256_ok"] = False
        artifacts.append(entry)
        if not entry["exists"]:
            fails.append(f"缺产物：{item['id']} → {item['path']}")
        elif not entry["sha256_ok"]:
            fails.append(f"哈希不符：{item['id']} 期望 {item['sha256']} 实得 {entry['actual_sha256']}")
    report["checks"]["artifacts"] = artifacts

    auth_candidates = [
        os.path.join(wt, "report/evidence/S3-T17", "hw_authorization.json"),
    ]
    auth = None
    for cand in auth_candidates:
        if os.path.isfile(cand):
            try:
                auth = json.load(open(cand, encoding="utf-8"))
                auth["_path"] = os.path.relpath(cand, wt).replace("\\", "/")
            except (OSError, ValueError) as exc:
                fails.append(f"hw_authorization.json 不可解析：{exc}")
            break
    confirm = bool(auth) and bool(auth.get("wong_go")) and bool(auth.get("codex_hw_release"))
    report["checks"]["hardware_gate"] = {
        "authorization_file": auth,
        "required": ["wong_go", "codex_hw_release"],
        "hardware_window_confirmed": confirm,
        "note": "两前提同时成立（Wong 开工信号 + 硬件窗口书面让出/时间窗）才可动板；本脚本不判断真伪，只读登记。",
    }
    report["hardware_window_confirmed"] = confirm

    report["failed_items"] = fails
    report["verdict"] = "OFFLINE_NO_GO" if fails else "OFFLINE_GO"
    report["exit_code"] = 1 if fails else 0
    print(f"前置检查结论={report['verdict']}（离线）")
    print(f"分支={branch} HEAD={head} index.lock={report['checks']['git']['index_lock_present']}")
    print(f"未提交改动={len(report['checks']['git']['status_short'])} 项")
    print(f"重型进程={'无' if not hits else hits}")
    for entry in artifacts:
        print("  [%s] %-26s %s" % ("OK" if entry.get("sha256_ok") else "FAIL", entry["id"], entry["path"]))
    print(f"硬件窗口已确认={confirm}（Wong 开工信号 + Codex 书面让出/时间窗；见 hw_authorization.json）")
    if fails:
        print("失败项：")
        for f in fails:
            print("  - " + f)
    if args.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
        json.dump(report, open(args.json_out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"JSON_OUT={args.json_out}")
    return report["exit_code"]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))