#!/usr/bin/env python3
"""独立扫描：列出 F6d 交付域内所有 PENDING/待批准 相关行（含扫描器未覆盖的形态）。

输出 UTF-8 文本，避免控制台 GBK 问题。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()

TOKENS = re.compile(r"PENDING|待批准")
# 扫描器分类正则（复制自 verification/approved_package_scan.py）
HISTORICAL = re.compile(r"历史语境|当时|历史修订|历史状态|v1\.\d+（r\d+")
SKIP = re.compile(r"历史语境|当时|历史修订|注入|self[_ -]?test|反向自测|必须 FAIL|必须FAIL|【规则】|"
                  r"rule\"|_probe|probe")
ALLOW = re.compile(r"PENDING_REVIEW|PENDING_CONFIRMATION|PENDING_MODULE|待 Wong 确认|待复核|批准说明|上游依赖")
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
# 独立口径：任何 PENDING/待批准/草案未批准 的语义断言（大小写不敏感）
MY_TOKEN = re.compile(r"PENDING|待批准|draft_not_approved|pending_approval", re.IGNORECASE)

TARGETS = [
    "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
    "docs/stage6/s6a_stage6_g0_behavior_v1.json",
]
for run in ("report/evidence/S6-A/s6a_g0_20261023_r12",
            "report/evidence/S6-B/s6b_core_20261023_r07"):
    d = ROOT / run
    TARGETS += [p.relative_to(ROOT).as_posix() for p in sorted(d.rglob("*")) if p.is_file()]

lines_out: list[str] = []
my_hits: list[str] = []
scanner_hits: list[str] = []
dead_patterns: list[str] = []

for rel in TARGETS:
    path = ROOT / rel
    if not path.is_file():
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    for i, line in enumerate(text.splitlines(), 1):
        flagged_scanner = False
        if TOKENS.search(line):
            if not (HISTORICAL.search(line) or SKIP.search(line) or ALLOW.search(line)):
                matched = [n for n, p in enumerate(ASSERT_PATTERNS, 1) if p.search(line)]
                if matched:
                    flagged_scanner = True
                    scanner_hits.append(f"{rel}:{i}: patterns={matched}: {line.strip()[:160]}")
        if MY_TOKEN.search(line):
            is_hist = bool(HISTORICAL.search(line)) or bool(SKIP.search(line)) or bool(ALLOW.search(line))
            tag = "HIST/SKIP/ALLOW" if is_hist else ("SCANNER-HIT" if flagged_scanner else "MY-HIT-ONLY")
            lines_out.append(f"[{tag}] {rel}:{i}: {line.strip()[:220]}")
            if not is_hist:
                my_hits.append(f"{rel}:{i}: {line.strip()[:220]}")

# 死正则：ASSERT_PATTERNS 中在 TOKENS 门槛下永远无法命中的小写形态
for n, p in enumerate(ASSERT_PATTERNS, 1):
    sample = {"all_parameters_pending_approval": 'all_parameters_pending_approval',
              "parameters_pending_approval": 'parameters_pending_approval',
              "thresholds_are_draft_not_approved": 'thresholds_are_draft_not_approved'}.get(p.pattern)
    if sample:
        would_match_assert = bool(p.search(sample))
        would_match_token = bool(TOKENS.search(sample))
        dead_patterns.append(f"pattern#{n} {p.pattern!r}: assert_match={would_match_assert} "
                             f"token_gate_match={would_match_token} -> "
                             f"{'DEAD (token gate blocks it)' if would_match_assert and not would_match_token else 'reachable'}")

report = [
    "### A. 扫描器门槛内命中的行（scanner hits）",
    *([f"  {x}" for x in scanner_hits] or ["  (none)"]),
    "",
    "### B. 我独立口径下（不受 TOKENS 门槛限制）仍未被豁免的 PENDING 行",
    *([f"  {x}" for x in my_hits] or ["  (none)"]),
    "",
    "### C. 死正则判定",
    *[f"  {x}" for x in dead_patterns],
    "",
    "### D. 全部含 token 的行（含被豁免行）",
    *lines_out,
]
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(report) + "\n", encoding="utf-8")
print(f"scanner_hits={len(scanner_hits)} my_hits={len(my_hits)} total_token_lines={len(lines_out)}")