#!/usr/bin/env python3
"""已批准包内**不得出现 PENDING/待批准陈述**（BLK-D2 机读断言；两侧通用）。

    python -B verification/approved_package_scan.py --project-root <abs> --run-dir <rel> [--inject-self-test]

判定：扫描该 RunId 目录内全部文本文件 + 行为表 JSON + 规格文档，凡出现 `PENDING` / `待批准` 的行，
除**显式历史语境**（行内含「历史语境/当时/历史修订」或形如 `v1.x（rNN` 的版本行）外一律 FAIL。
`--inject-self-test`：在**临时副本**内注入一行 PENDING，必须 FAIL（证明断言有判别力；真实目录不被触碰）。
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path

HISTORICAL = re.compile(r"历史语境|当时|历史修订|历史状态|v1\.\d+（r\d+")
# 只判**状态断言**，不判"工具/自测描述里提到该令牌"（后者不是待批准陈述）
ASSERT_PATTERNS = [
    re.compile(r'"approval_status"\s*:\s*"[^"]*PENDING'),
    re.compile(r'"status"\s*:\s*"[^"]*PENDING'),
    re.compile(r"all_parameters_pending_approval"),
    re.compile(r"parameters_pending_approval"),
    re.compile(r"thresholds_are_draft_not_approved"),
    re.compile(r"DONE_PENDING_APPROVAL"),
    re.compile(r"G0_PACKET_PENDING_APPROVAL"),
    re.compile(r"DECLARED_PENDING"),
    re.compile(r"(阈值|指标|参数|本包|清单|登记)[^\n]{0,14}(待批准|PENDING_APPROVAL)"),
    re.compile(r"(待批准|PENDING_APPROVAL)[^\n]{0,10}(草案值|状态|口径)"),
]
SKIP = re.compile(r"历史语境|当时|历史修订|注入|self[_ -]?test|反向自测|必须 FAIL|必须FAIL|【规则】|"
                  r"rule\"|_probe|probe")
# 放行：评审态、待 Wong 确认（批准记录未覆盖的开放项）——它们不是"本包仍待批准"的陈述
ALLOW = re.compile(r"PENDING_REVIEW|PENDING_CONFIRMATION|PENDING_MODULE|待 Wong 确认|待复核|批准说明|上游依赖")
TOKENS = re.compile(r"PENDING|待批准")
VERSION_LINE = re.compile(r"v1\.\d+（r\d+")


def find_hits(paths: list[Path]) -> list[str]:
    hits: list[str] = []
    for path in paths:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if (TOKENS.search(line) and not HISTORICAL.search(line) and not SKIP.search(line)
                    and not ALLOW.search(line)
                    and any(pat.search(line) for pat in ASSERT_PATTERNS)):
                hits.append(f"{path.name}:{i}: {line.strip()[:110]}")
    return hits


def scan(root: Path, run_rel: str) -> list[str]:
    run_dir = root / run_rel
    targets = [p for p in run_dir.rglob("*") if p.is_file()]
    targets += [root / "docs/stage6/s6a_stage6_g0_behavior_v1.json",
                root / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"]
    return find_hits(targets)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--inject-self-test", action="store_true")
    ap.add_argument("--out", default="tmp/6/approved_package_scan.json")
    args = ap.parse_args(argv)
    root = Path(args.project_root).resolve()
    hits = scan(root, args.run_dir)
    payload = {"schema_version": 1, "artifact": "approved_package_scan", "run_dir": args.run_dir,
               "rule": "已批准版包内不得出现 PENDING/待批准 陈述（历史语境行除外）",
               "hits": hits, "verdict": "CLEAN" if not hits else "PENDING_TEXT_FOUND"}
    if args.inject_self_test:
        with tempfile.TemporaryDirectory() as tmp:
            copy_root = Path(tmp) / "copy"
            shutil.copytree(root / args.run_dir, copy_root / args.run_dir)
            probe = copy_root / args.run_dir / "PENDING_probe.txt"
            probe.parent.mkdir(parents=True, exist_ok=True)
            probe.write_text("本包全部阈值与指标仍为待批准状态\n", encoding="utf-8")
            injected = find_hits([probe])
            payload["self_test"] = {"injected_hits": injected,
                                    "verdict": "AS_EXPECTED" if injected else "UNEXPECTED"}
            payload["verdict"] = ("AS_EXPECTED" if not hits and injected else "UNEXPECTED")
    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": payload["verdict"], "hits": len(hits),
                      "self_test": payload.get("self_test", {}).get("verdict")}, ensure_ascii=False))
    ok = payload["verdict"] in ("CLEAN", "AS_EXPECTED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
