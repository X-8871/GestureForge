#!/usr/bin/env python3
"""补充核查：needle 判别力（去掉路径守卫）、清单/STATE 声明 vs 实际文件、
虚假「已审查/已通过」扫描、S6-B r03 _selfproof 未通过明细。"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

R = Path(r"D:/FPGA_Competition/tmp/review/FINAL_A_20261023_r01")
C = R / "committed"
E8 = C / "f3c537d"
RUN = E8 / "report/evidence/S6-A/s6a_g0_20261022_r08"

NEEDLES = ["M4 不可达", "M4/M7 不可达", "不得计入覆盖", "m4_reachable_under_draft\": false",
           "m4_reachable_under_draft=false", "M4 在草案参数下不可达"]
MARKERS = ("原声明", "历史", "改为", "r07", "BLK-r07-1", "NB-09", "『")
SCAN_NAMES = ("coverage_matrix.json", "limitations_not_executed.json", "fix_record.json", "fix_record.md",
              "S6A_run_summary.md", "delivery_manifest.json", "hand_computed_cases.json")


def T(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def h(t: str) -> None:
    print("\n" + "=" * 92)
    print(t)
    print("=" * 92)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    # (a) 去掉路径守卫后的 needle 判别力（对同一批被扫文件）
    h("A. claim_verify needle 判别力（忠实复算，去掉绝对路径守卫；文件 = 入库字节）")
    scan_files = [RUN / n for n in SCAN_NAMES if (RUN / n).is_file()]
    scan_files += [E8 / "docs/stage6/s6a_stage6_g0_behavior_v1.json",
                   E8 / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
                   E8 / ".codex/STATE.md",
                   E8 / "verification/s6a_build_evidence.py"]
    hits = []
    for p in scan_files:
        for i, line in enumerate(T(p).splitlines(), 1):
            if any(m in line for m in MARKERS):
                continue
            for n in NEEDLES:
                if n in line:
                    hits.append(f"{p.relative_to(E8).as_posix()}:{i} [{n}]")
    print("   被扫文件数 =", len(scan_files))
    print("   needle 命中（无路径守卫）：")
    for x in hits:
        print("     ", x)
    print("   => 0 命中" if not hits else "   => 非 0 命中")
    print("\n   反证：把出厂探针字面量注入后（同一套 needle / 同一批文件）")
    injected = "草案 500ms ≥ T6-L02 300ms，M4 不可达（U6-12）；本行不得计入覆盖声明。"
    m = [n for n in NEEDLES if n in injected]
    print("     命中 =", m)

    # (b) 清单双向 + STATE 声明
    h("B. 声明 vs 实际：r08 清单双向、STATE 声明文件/目录存在性")
    dm = json.loads(T(RUN / "delivery_manifest.json"))
    declared = [str(i["path"]).replace("\\", "/") for i in dm["files"]]
    actual = sorted(p.relative_to(RUN).as_posix() for p in RUN.rglob("*") if p.is_file())
    run_declared = [x for x in declared if not x.startswith("docs/") and not x.startswith(".codex/")
                    and not x.startswith("verification/") and not x.startswith("src/")]
    print("   清单 files 条数:", len(declared))
    print("   运行目录内声明:", len(run_declared))
    print("   运行目录实际文件:", len(actual))
    print("   实际多出（未声明）:", sorted(set(actual) - set(run_declared)))
    print("   声明缺失:", sorted(set(run_declared) - set(actual)))
    print("   外部绑定（前 12）:", [x for x in declared if x not in run_declared][:12])
    missing_ext, bad = [], []
    for x in declared:
        p = RUN / x
        if not p.is_file():
            p = E8 / x
        if not p.is_file():
            missing_ext.append(x)
            continue
        data = p.read_bytes()
        want = None
        for i in dm["files"]:
            if str(i["path"]).replace("\\", "/") == x:
                want = str(i["sha256"]).lower()
        if sha(data) == want or sha(data.replace(b"\r\n", b"\n")) == want \
                or sha(data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")) == want:
            continue
        bad.append(x)
    print("   全量：缺失 =", missing_ext, "；哈希不符 =", bad)
    # hashes_sha256.txt 自洽
    hs = {}
    for line in T(RUN / "hashes_sha256.txt").splitlines():
        if "  " in line:
            a, b = line.split("  ", 1)
            hs[b.strip()] = a.strip()
    mismatch = []
    for rel, want in hs.items():
        p = RUN / rel
        if not p.is_file():
            mismatch.append((rel, "缺失"))
            continue
        data = p.read_bytes()
        if sha(data) != want and sha(data.replace(b"\r\n", b"\n")) != want:
            mismatch.append((rel, "哈希不符"))
    print("   hashes_sha256.txt 条数:", len(hs), "；不一致 =", mismatch)
    # STATE
    st = T(E8 / ".codex/STATE.md")
    paths = sorted(set(re.findall(r"`(report/evidence/[^`]+?)`", st)))
    print("   STATE 声明的 report/evidence 路径:")
    for p in paths:
        full = E8 / p
        print(f"     {p} -> {'存在' if full.exists() else '缺失'}")

    # (c) 虚假「已审查/已通过」扫描
    h("C. 虚假「已审查/已通过/已冻结」表述扫描")
    pat = re.compile(r"已(通过|审查|复核|验收)|审查通过|PASS 通过|已冻结|已批准|APPROVED|FROZEN")
    targets = [p for p in RUN.rglob("*") if p.is_file()]
    targets += [p for p in (E8 / "report/evidence/S6-A/s6a_g0_20261022_r08_selfproof").rglob("*") if p.is_file()]
    targets += [E8 / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
                E8 / "docs/stage6/s6a_stage6_g0_behavior_v1.json",
                E8 / ".codex/STATE.md"]
    neg = ("不代表", "不构成", "不得", "未完成", "未通过", "未经", "不是", "不得自称", "不宣称", "未取得")
    cnt = 0
    for p in sorted(set(targets)):
        for i, line in enumerate(T(p).splitlines(), 1):
            if pat.search(line):
                flag = "（否定语境）" if any(n in line for n in neg) else "（**需人工判读**）"
                if flag == "（**需人工判读**）":
                    cnt += 1
                print(f"   {flag} {p.relative_to(E8).as_posix()}:{i}: {line.strip()[:220]}")
    print("   需人工判读的行数 =", cnt)

    # (d) S6-B r03 _selfproof 未通过明细
    h("D. S6-B r03 _selfproof（f3c537d 交付字节）subject 明细")
    p = E8 / "report/evidence/S6-B/s6b_core_20261023_r03_selfproof/export_selfproof.json"
    d = json.loads(T(p))
    print("   verdict =", d["verdict"], "；generated_at =", d["generated_at"])
    for s in d["subjects"]:
        print(f"   - {s['subject']} -> {s['verdict']}")
        for c in s["checks"]:
            print(f"       {c['name'][:70]} exit={c['exit_code']}")
            if c["exit_code"] != 0:
                print(f"          stdout_tail: {c['stdout_tail'][:500]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())