#!/usr/bin/env python3
"""修正版：r08 清单/哈希双向核对 + STATE 声明路径存在性（用 git 树判定）+ 单元反例。"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

R = Path(r"D:/FPGA_Competition/tmp/review/FINAL_A_20261023_r01")
E8 = R / "committed/f3c537d"
RUN = E8 / "report/evidence/S6-A/s6a_g0_20261022_r08"
MAIN = Path(r"D:/FPGA_Competition")


def T(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def variants(b: bytes) -> set[str]:
    lf = b.replace(b"\r\n", b"\n")
    return {hashlib.sha256(b).hexdigest(), hashlib.sha256(lf).hexdigest(),
            hashlib.sha256(lf.replace(b"\n", b"\r\n")).hexdigest()}


def h(t: str) -> None:
    print("\n" + "=" * 92)
    print(t)
    print("=" * 92)


def main() -> int:
    dm = json.loads(T(RUN / "delivery_manifest.json"))
    declared = {str(i["path"]).replace("\\", "/"): str(i["sha256"]).lower() for i in dm["files"]}
    prefix = "report/evidence/S6-A/s6a_g0_20261022_r08/"
    run_declared = sorted(k[len(prefix):] for k in declared if k.startswith(prefix))
    ext_declared = sorted(k for k in declared if not k.startswith(prefix))
    actual = sorted(p.relative_to(RUN).as_posix() for p in RUN.rglob("*") if p.is_file())

    h("B1. r08 清单双向（运行目录）")
    print("   清单总数:", len(declared), "= 运行目录", len(run_declared), "+ 外部绑定", len(ext_declared))
    print("   运行目录实际:", len(actual))
    print("   实际多出（未声明）:", sorted(set(actual) - set(run_declared)))
    print("   声明但缺失:", sorted(set(run_declared) - set(actual)))
    print("   外部绑定:", ext_declared)

    h("B2. 每条声明文件存在性 + 哈希（原字节 / LF / CRLF 三口径任一命中）")
    missing, bad = [], []
    for rel, want in declared.items():
        p = None
        for cand in (RUN / rel[len(prefix):] if rel.startswith(prefix) else E8 / rel,
                     E8 / rel, RUN / rel):
            if cand.is_file():
                p = cand
                break
        if p is None:
            missing.append(rel)
            continue
        if want not in variants(p.read_bytes()):
            bad.append((rel, want, hashlib.sha256(p.read_bytes()).hexdigest()))
    print("   缺失:", missing)
    print("   哈希不符:", bad)

    h("B3. hashes_sha256.txt 自洽（38 条，相对 run_dir）")
    hs = {}
    for line in T(RUN / "hashes_sha256.txt").splitlines():
        if "  " in line:
            a, b = line.split("  ", 1)
            hs[b.strip()] = a.strip()
    mism = []
    for rel, want in hs.items():
        p = RUN / rel
        if not p.is_file():
            mism.append((rel, "缺失"))
        elif want not in variants(p.read_bytes()):
            mism.append((rel, "哈希不符"))
    print("   条数:", len(hs), "；不一致:", mism)
    print("   未列入 hashes_sha256.txt 的实际文件:",
          sorted(set(actual) - set(hs)))

    h("B4. STATE 声明的证据路径存在性（用 git 树 f3c537d 判定）")
    st = T(E8 / ".codex/STATE.md")
    paths = sorted(set(re.findall(r"`(report/evidence/[^`]*?)`", st)))
    for p in paths:
        r = subprocess.run(["git", "-C", str(MAIN), "cat-file", "-t", f"f3c537d:{p.rstrip('/')}"],
                           capture_output=True, text=True)
        ok = r.returncode == 0 and r.stdout.strip() in ("tree", "blob")
        print(f"   {p} -> {'存在(' + r.stdout.strip() + ')' if ok else '缺失'}")

    h("B5. 单元反例：align_by_manifest_hashes 只选换行、绝不改写内容")
    sys.path.insert(0, str((R / "envC/verification").resolve()))
    import export_selfproof as es
    root = Path(tempfile.mkdtemp(prefix="unit_align_"))
    tree = root / "t"
    tree.mkdir()
    manifest = {"files": []}
    a_lf = b"alpha\nbeta\n"
    (tree / "a.txt").write_bytes(a_lf.replace(b"\n", b"\r\n"))
    manifest["files"].append({"path": "a.txt", "sha256": hashlib.sha256(a_lf).hexdigest()})
    b_crlf = b"gamma\r\ndelta\r\n"
    (tree / "b.txt").write_bytes(b_crlf.replace(b"\r\n", b"\n"))
    manifest["files"].append({"path": "b.txt", "sha256": hashlib.sha256(b_crlf).hexdigest()})
    (tree / "c.txt").write_bytes(b"epsilon9\n")
    before = (tree / "c.txt").read_bytes()
    manifest["files"].append({"path": "c.txt", "sha256": hashlib.sha256(b"epsilon\n").hexdigest()})
    (tree / "delivery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    res = es.align_by_manifest_hashes(tree, "delivery_manifest.json")
    print("   结果:", json.dumps(res, ensure_ascii=False))
    print("   a.txt 已对齐为 LF:", (tree / "a.txt").read_bytes() == a_lf)
    print("   b.txt 已对齐为 CRLF:", (tree / "b.txt").read_bytes() == b_crlf)
    print("   c.txt 字节未被改写:", (tree / "c.txt").read_bytes() == before, "；在 unresolved:", "c.txt" in res["unresolved"])
    # normalize_line_endings 反向单元
    src = root / "src"
    src.mkdir()
    (src / "d.txt").write_bytes(b"delta\n")
    tree2 = root / "t2"
    tree2.mkdir()
    (tree2 / "d.txt").write_bytes(b"delta\r\n")
    (tree2 / "e.txt").write_bytes(b"x9\n")
    (src / "e.txt").write_bytes(b"x\n")
    res2 = es.normalize_line_endings(tree2, src)
    print("   normalize_line_endings:", json.dumps(res2, ensure_ascii=False))
    print("   e.txt（内容真差）字节未被改写:", (tree2 / "e.txt").read_bytes() == b"x9\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())