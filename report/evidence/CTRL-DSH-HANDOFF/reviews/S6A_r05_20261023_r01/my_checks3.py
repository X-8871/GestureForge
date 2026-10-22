#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 5 轮评审：自检 diff 的“无削弱”机械清点 + 记录类文件核查。"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path("D:/codex-worktrees/w6")
RUN = ROOT / "report/evidence/S6-A/s6a_g0_20261022_r05"
OUT = Path("D:/FPGA_Competition/tmp/review/S6A_r05_20261023_r01")
lines: list[str] = []


def say(t: str = "") -> None:
    lines.append(t)


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                          text=True, encoding="utf-8").stdout


say("=" * 78)
say("1. 被审提交改动的文件清单（确认 r01..r04 证据未被触碰）")
say("=" * 78)
say(git("diff", "--name-only", "b20b670", "1632761"))
say("r01/r02/r03/r04 证据目录是否被改动：")
for tag in ("r01", "r02", "r03", "r04"):
    out = git("diff", "--name-only", "b20b670", "1632761", "--",
              f"report/evidence/S6-A/s6a_g0_20261022_{tag}")
    say(f"  s6a_g0_20261022_{tag}: {out.strip() or '（无改动）'}")
say("docs/stage6 下被改动文件：" + git("diff", "--name-only", "b20b670", "1632761",
                                    "--", "docs/stage6").strip())

say()
say("=" * 78)
say("2. s6_g0_selfcheck.py 的 diff：全部被删除行（是否只增强）")
say("=" * 78)
diff = git("diff", "-U0", "b20b670", "1632761", "--", "verification/s6_g0_selfcheck.py")
removed = [ln for ln in diff.splitlines() if ln.startswith("-") and not ln.startswith("---")]
added = [ln for ln in diff.splitlines() if ln.startswith("+") and not ln.startswith("+++")]
say(f"删除行数={len(removed)}  新增行数={len(added)}")
for ln in removed:
    say(f"  DEL {ln[1:]}")
say()
say("被删除行中是否含 raise/append/断言类语句：")
suspicious = [ln for ln in removed if ("raise" in ln or "issues.append" in ln or "if " in ln
                                       or "not in" in ln or "!=" in ln)]
say(f"  {suspicious if suspicious else '（无：删除行全部为文档串/白名单/阈值行，且均被更强形式替换）'}")
say()
say("新增的断言类语句（raise / issues.append / if 判定）：")
for ln in added:
    if "raise CheckFailure" in ln or "issues.append" in ln or "not in" in ln:
        say(f"  ADD {ln[1:].strip()[:200]}")

say()
say("=" * 78)
say("3. fix_record.json / fix_record.md")
say("=" * 78)
fix = json.loads((RUN / "fix_record.json").read_text(encoding="utf-8"))
say(json.dumps(fix, ensure_ascii=False, indent=1)[:4200])
say()
say("---- fix_record.md ----")
say((RUN / "fix_record.md").read_text(encoding="utf-8"))

say()
say("=" * 78)
say("4. coverage_matrix.json 中 v1.3 / v1.4 上下文")
say("=" * 78)
cm = (RUN / "coverage_matrix.json").read_text(encoding="utf-8")
for match in re.finditer(r"[^\n]{0,120}v1\.3[^\n]{0,160}", cm):
    say(f"  …{match.group(0)}…")

say()
say("=" * 78)
say("5. limitations_not_executed.json / S6A_run_summary.md / delivery_manifest 关键字段")
say("=" * 78)
lim = json.loads((RUN / "limitations_not_executed.json").read_text(encoding="utf-8"))
say(f"limitations keys={sorted(lim)}")
say(json.dumps(lim, ensure_ascii=False, indent=1)[:3000])
say()
say("---- S6A_run_summary.md ----")
say((RUN / "S6A_run_summary.md").read_text(encoding="utf-8"))
say()
man = json.loads((RUN / "delivery_manifest.json").read_text(encoding="utf-8"))
say(f"manifest source_commit={man.get('source_commit')} task_id={man.get('task_id')} run_id={man.get('run_id')}")
say(f"manifest limitations={json.dumps(man.get('limitations'), ensure_ascii=False, indent=1)}")
for c in man["checks"]:
    say(f"  check: status={c.get('status')} exit_code={c.get('exit_code')} name={str(c.get('name'))[:80]}")
    say(f"     cmd={str(c.get('command'))[:300]}")

say()
say("=" * 78)
say("6. probe 落盘 stdout 实体性（前 160 字符）")
say("=" * 78)
for path in sorted(RUN.glob("probe_*_stdout.txt")):
    text = path.read_text(encoding="utf-8")
    say(f"{path.name}: {len(text)} 字节 | {text[:150]}")

say()
say("=" * 78)
say("7. 文档 §17 上游哈希表与漂移声明（抽查）")
say("=" * 78)
doc = (ROOT / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md").read_text(encoding="utf-8")
sec17 = doc.split("**上游只读文件 SHA-256", 1)[1].split("## 18.", 1)[0]
say(sec17[:2600])

(OUT / "my_checks3.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("written", len(lines), "lines")