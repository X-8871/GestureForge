#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽取 HC-28/29/30、r04 失败证据、probe 汇总、以及“8 个注入”计数核对。"""
import hashlib
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


cases = json.loads((RUN / "hand_computed_cases.json").read_text(encoding="utf-8"))
say(f"hand_computed_cases.json: cases={len(cases['cases'])} ids="
    f"{[c['case_id'] for c in cases['cases']]}")
say(f"顶层键={sorted(cases)}")
by_id = {c["case_id"]: c for c in cases["cases"]}
for cid in ("HC-28", "HC-29", "HC-30"):
    say()
    say(f"---- {cid} ----")
    say(json.dumps(by_id[cid], ensure_ascii=False, indent=1))

say()
say("=" * 70)
say("r04 失败证据（r05 自检 @ r04 git 字节）")
say("=" * 70)
fail = json.loads((RUN / "selfcheck_r04_failure.json").read_text(encoding="utf-8"))
say(f"status={fail['status']} artifact_version={fail['artifact_version']} run_id={fail['run_id']}")
say(f"inputs={json.dumps(fail['inputs'], ensure_ascii=False)}")
for c in fail["checks"]:
    if c["status"] == "FAIL":
        say(f"FAIL {c['id']}: {c['detail'][:600]}")
say("PASS 项：" + str([c["id"] for c in fail["checks"] if c["status"] == "PASS"]))
say()
pkg = json.loads((RUN / "r04_package_under_test.json").read_text(encoding="utf-8"))
say(f"r04_package_under_test.json: commit={pkg['git_commit']}")
for row in pkg["files_under_test"]:
    say(f"  {row['path']} sha256={row['sha256']}")
say(f"observed={json.dumps(pkg['observed'], ensure_ascii=False)[:400]}")
say(f"evidence_dir_under_test.actual_files={len(pkg['evidence_dir_under_test']['actual_files'])}")

say()
say("=" * 70)
say("probe_summary.json（入库）")
say("=" * 70)
probe = json.loads((RUN / "probe_summary.json").read_text(encoding="utf-8"))
say(f"baseline_verdict={probe['baseline_verdict']} results={len(probe['results'])}")
for r in probe["results"]:
    say(f"  {r['case_id']}: expect_exit={r['expected_exit']} actual={r['actual_exit']} "
        f"expect_check={r['expected_check']} failed={r['failed_checks']} captured={r['captured']} "
        f"verdict={r['verdict']}")
say(f"purpose={probe['purpose']}")
say(f"scope={probe['scope_statement']}")

say()
say("=" * 70)
say("“8 个注入”表述计数核对")
say("=" * 70)
targets = {
    "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md": (ROOT / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"),
    "verification/s6a_r05_probe.py": ROOT / "verification/s6a_r05_probe.py",
    "verification/s6a_build_evidence.py": ROOT / "verification/s6a_build_evidence.py",
    "report/.../S6A_run_summary.md": RUN / "S6A_run_summary.md",
    "report/.../probe_summary.json": RUN / "probe_summary.json",
    "report/.../fix_record.md": RUN / "fix_record.md",
    "report/.../fix_record.json": RUN / "fix_record.json",
    "report/.../coverage_matrix.json": RUN / "coverage_matrix.json",
    "report/.../limitations_not_executed.json": RUN / "limitations_not_executed.json",
    "report/.../delivery_manifest.json": RUN / "delivery_manifest.json",
}
for label, path in targets.items():
    text = path.read_text(encoding="utf-8")
    for match in re.finditer(r"[^\n]{0,40}(8 个注入|8 项注入|8 用例|8 个用例|7 个注入|7 用例)[^\n]{0,60}", text):
        say(f"[{label}] …{match.group(0)}…")

say()
say("git show --format=%H%n%B -s 1632761 全文（提交信息）：")
say(subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%B", "1632761"],
                   capture_output=True, text=True, encoding="utf-8").stdout)

say()
say("=" * 70)
say("r04 证据绑定口径（工作树 CRLF 还是 git LF 字节？）")
say("=" * 70)
r04_selfcheck = json.loads(
    subprocess.run(["git", "-C", str(ROOT), "cat-file", "blob",
                    "b20b670:report/evidence/S6-A/s6a_g0_20261022_r04/selfcheck_result.json"],
                   capture_output=True).stdout.decode("utf-8"))
say(f"r04 selfcheck inputs.behavior_json_sha256={r04_selfcheck['inputs']['behavior_json_sha256']}")
for rel, key in (("docs/stage6/s6a_stage6_g0_behavior_v1.json", "behavior_json_sha256"),
                 ("docs/stage6/S6A_stage6_g0_behavior_spec_v1.md", "human_doc_sha256")):
    blob = subprocess.run(["git", "-C", str(ROOT), "cat-file", "blob", f"b20b670:{rel}"],
                          capture_output=True).stdout
    lf = hashlib.sha256(blob).hexdigest()
    crlf = hashlib.sha256(blob.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")).hexdigest()
    say(f"  {rel}: git(LF)={lf}")
    say(f"     重建CRLF={crlf}  与 r04 入库 {key}="
        f"{'一致(CRLF 口径)' if crlf == r04_selfcheck['inputs'][key] else '不一致'}"
        f"  {'（LF 口径）' if lf == r04_selfcheck['inputs'][key] else ''}")

say()
say("r05 证据绑定口径：")
r05_selfcheck = json.loads((RUN / "selfcheck_result.json").read_text(encoding="utf-8"))
for rel, key in (("docs/stage6/s6a_stage6_g0_behavior_v1.json", "behavior_json_sha256"),
                 ("docs/stage6/S6A_stage6_g0_behavior_spec_v1.md", "human_doc_sha256")):
    blob = subprocess.run(["git", "-C", str(ROOT), "cat-file", "blob", f"1632761:{rel}"],
                          capture_output=True).stdout
    lf = hashlib.sha256(blob).hexdigest()
    crlf = hashlib.sha256(blob.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")).hexdigest()
    say(f"  {rel}: git(LF)={lf}\n     重建CRLF={crlf} 入库={r05_selfcheck['inputs'][key]} "
        f"→ {'CRLF 口径' if crlf == r05_selfcheck['inputs'][key] else '?'}")

(OUT / "my_extract.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("written", len(lines), "lines")