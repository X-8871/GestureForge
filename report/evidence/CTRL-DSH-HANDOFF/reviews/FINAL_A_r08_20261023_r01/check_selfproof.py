#!/usr/bin/env python3
"""N-r07-2：两份 _selfproof 报告的自洽性、主体、以及清单内嵌自证检查项。"""
from __future__ import annotations

import json
import re
from pathlib import Path

R = Path(r"D:/FPGA_Competition/tmp/review/FINAL_A_20261023_r01")
C = R / "committed"
E8 = C / "f3c537d"
E3 = C / "e3aeb09"
R3 = C / "05126fd"
B7 = C / "bdcf896"


def T(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def dump(label: str, p: Path) -> None:
    print("\n" + "=" * 92)
    print(label, "::", p)
    print("=" * 92)
    if not p.is_file():
        print("   缺失")
        return
    txt = T(p)
    d = json.loads(txt)
    print("   verdict =", d.get("verdict"))
    print("   generated_at =", d.get("generated_at"))
    print("   subject_note =", str(d.get("subject_note"))[:400])
    for s in d.get("subjects", []):
        print(f"   subject: {s.get('subject')} -> {s.get('verdict')} "
              f"checks={[c['exit_code'] for c in s.get('checks', [])]}")
        print(f"      newline_alignment: {json.dumps(s.get('newline_alignment'), ensure_ascii=False)[:260]}")
    for needle in ("NOT_SELF_PROVEN", "\"FAIL\"", "status\": \"FAIL"):
        hits = [(i, ln) for i, ln in enumerate(txt.splitlines(), 1) if needle in ln]
        print(f"   含 {needle}: {len(hits)} 行")
        for i, ln in hits[:6]:
            print(f"      L{i}: {ln.strip()[:220]}")


def main() -> int:
    dump("S6-A r08 _selfproof（f3c537d 交付字节）",
         E8 / "report/evidence/S6-A/s6a_g0_20261022_r08_selfproof/export_selfproof.json")
    dump("S6-A r08 _selfproof（e3aeb09 版本，仅供比较）",
         E3 / "report/evidence/S6-A/s6a_g0_20261022_r08_selfproof/export_selfproof.json")
    dump("S6-B r03 _selfproof（f3c537d 交付字节）",
         E8 / "report/evidence/S6-B/s6b_core_20261023_r03_selfproof/export_selfproof.json")
    dump("S6-B r03 _selfproof（05126fd 版本）",
         R3 / "report/evidence/S6-B/s6b_core_20261023_r03_selfproof/export_selfproof.json")

    print("\n" + "=" * 92)
    print("r08 delivery_manifest.json 内嵌的自证检查项（f3c537d）")
    print("=" * 92)
    for rev, tag in ((E8, "f3c537d"), (E3, "e3aeb09"), (R3, "05126fd")):
        p = rev / "report/evidence/S6-A/s6a_g0_20261022_r08/delivery_manifest.json"
        if not p.is_file():
            print(f"  [{tag}] 缺失")
            continue
        d = json.loads(T(p))
        print(f"  [{tag}] source_commit = {d.get('source_commit')}")
        for c in d.get("checks", []):
            print(f"     - {c['name'][:60]} | {c['status']} | exit={c['exit_code']}")
            if c.get("reason"):
                print(f"       reason: {c['reason'][:400]}")

    print("\n" + "=" * 92)
    print("S6-B r03 清单 source_commit（f3c537d）")
    print("=" * 92)
    p = E8 / "report/evidence/S6-B/s6b_core_20261023_r03/delivery_manifest.json"
    if p.is_file():
        d = json.loads(T(p))
        print("   source_commit =", d.get("source_commit"))
        for c in d.get("checks", []):
            print(f"     - {c['name'][:60]} | {c['status']} | exit={c['exit_code']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())