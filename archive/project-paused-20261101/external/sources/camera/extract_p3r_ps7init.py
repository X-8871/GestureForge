# -*- coding: utf-8 -*-
"""extract_p3r_ps7init.py —— 从 P3r XSA 提取 ps7_init.tcl（板级零等待用）

用法：
    python extract_p3r_ps7init.py                      # 自动挑最新 out/build*/s4d_p3r_r01.xsa
    python extract_p3r_ps7init.py --build b11k         # 指定 build 目录
    python extract_p3r_ps7init.py --xsa <path> --tag mytag
    python extract_p3r_ps7init.py --dry-run            # 只打印将做什么，不落盘

输出：
    <build 目录同级>/p3r_<tag>_ps7_init.tcl
    控制台/JSON 打印：条目、字节数、sha256

说明：
- Zynq-7000 的 Vivado XSA 顶层直接含 ps7_init.tcl / ps7_init.c / ps7_init.h / ps7_init.html
- 本脚本按白名单提取（默认只取 ps7_init.tcl），不改动 XSA
- 幂等：同名文件内容一致则跳过重写
"""
import argparse
import glob
import hashlib
import io
import json
import os
import sys
import zipfile

BASE = os.path.dirname(os.path.abspath(__file__))
WANTED_DEFAULT = ("ps7_init.tcl",)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def find_latest_xsa() -> str:
    cands = sorted(
        glob.glob(os.path.join(BASE, "out", "build*", "s4d_p3r_r01.xsa")),
        key=os.path.getmtime,
    )
    if not cands:
        raise SystemExit("未找到任何 out/build*/s4d_p3r_r01.xsa")
    return cands[-1]


def build_tag_from_xsa(xsa_path: str) -> str:
    parent = os.path.basename(os.path.dirname(os.path.abspath(xsa_path)))
    return parent if parent.startswith("build") else "latest"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xsa", default="")
    ap.add_argument("--build", default="", help="例如 b11k / build11k")
    ap.add_argument("--tag", default="", help="输出文件里的标签，默认取 build 目录名")
    ap.add_argument("--items", default=",".join(WANTED_DEFAULT))
    ap.add_argument("--outdir", default="")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.xsa:
        xsa = args.xsa
    elif args.build:
        # 兼容 b11h / b11i / 11i / build11i 等写法
        cands = [args.build, "build" + args.build, "build" + args.build.lstrip("b"), "build" + args.build.lstrip("build")]
        name = None
        for c in cands:
            if os.path.isdir(os.path.join(BASE, "out", c)):
                name = c
                break
        if name is None:
            name = "build" + args.build.lstrip("b")
        xsa = os.path.join(BASE, "out", name, "s4d_p3r_r01.xsa")
    else:
        xsa = find_latest_xsa()

    if not os.path.isfile(xsa):
        print(json.dumps({"ok": False, "error": "XSA 不存在", "xsa": xsa}, ensure_ascii=False))
        return 2

    tag = args.tag or build_tag_from_xsa(xsa)
    outdir = args.outdir or BASE
    items = [s.strip() for s in args.items.split(",") if s.strip()]

    print("XSA : %s (%d B)" % (xsa, os.path.getsize(xsa)))
    print("标签: %s" % tag)
    print("条目: %s" % ", ".join(items))

    results = []
    with zipfile.ZipFile(xsa) as zf:
        names = set(zf.namelist())
        for item in items:
            if item not in names:
                print("  [缺失] %s（该 XSA 内没有此条目）" % item)
                results.append({"item": item, "ok": False, "reason": "not_in_xsa"})
                continue
            data = zf.read(item)
            out_name = "p3r_%s_%s" % (tag, item) if item != "ps7_init.tcl" else "p3r_%s_ps7_init.tcl" % tag
            out_path = os.path.join(outdir, out_name)
            info = {"item": item, "out": out_path, "bytes": len(data), "sha256": sha256_bytes(data), "ok": True}
            if args.dry_run:
                info["action"] = "would_write"
            else:
                old = None
                if os.path.isfile(out_path):
                    with io.open(out_path, "rb") as fh:
                        old = fh.read()
                if old == data:
                    info["action"] = "unchanged"
                else:
                    with io.open(out_path, "wb") as fh:
                        fh.write(data)
                    info["action"] = "written"
            results.append(info)
            print("  [%s] %-14s -> %s  %d B  sha256=%s"
                  % (info.get("action", "dry-run"), item, out_path, len(data), info["sha256"]))

    ok = all(r["ok"] for r in results)
    print(json.dumps({"ok": ok, "xsa": xsa, "tag": tag, "results": results}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())