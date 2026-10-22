#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""独立 Reviewer 第 5 轮（S6-A r05）自写核验脚本：只读被审树，输出全部落隔离评审目录。"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path("D:/codex-worktrees/w6")
OUT = Path("D:/FPGA_Competition/tmp/review/S6A_r05_20261023_r01")
RUN = ROOT / "report/evidence/S6-A/s6a_g0_20261022_r05"
R04 = "b20b6705e8c7dd6c43cc2195860e3fc84e1c4ec7"
R05 = "1632761b2d60d8c1328aa82be97d53eef30e1072"

lines: list[str] = []


def say(text: str = "") -> None:
    lines.append(text)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_blob(commit: str, relpath: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "cat-file", "blob", f"{commit}:{relpath}"],
        capture_output=True, check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(f"git cat-file 失败 {commit}:{relpath}: {completed.stderr!r}")
    return completed.stdout


json_rel = "docs/stage6/s6a_stage6_g0_behavior_v1.json"
doc_rel = "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"

say("=" * 78)
say("A. 自算 SHA-256（被审提交 1632761 版本 = 工作区字节）")
say("=" * 78)
for rel in (
    json_rel, doc_rel,
    "verification/s6_g0_selfcheck.py",
    "verification/s6a_build_evidence.py",
    "verification/s6a_r05_probe.py",
    "verification/s6a_rerun_legacy_failures.py",
    ".codex/STATE.md",
):
    work = (ROOT / rel).read_bytes()
    blob = git_blob(R05, rel)
    say(f"{rel}\n  worktree={sha256_bytes(work)}\n  git@1632761={sha256_bytes(blob)}  "
        f"{'一致' if work == blob else '**不一致（工作区已偏离提交）**'}")

say()
say("=" * 78)
say("B. 自检复跑 vs 入库 selfcheck_result.json")
say("=" * 78)
mine = json.loads((OUT / "my_selfcheck_r05.json").read_text(encoding="utf-8"))
theirs = json.loads((RUN / "selfcheck_result.json").read_text(encoding="utf-8"))
say(f"我的 status={mine['status']} errors={len(mine['errors'])} checks={len(mine['checks'])}")
say(f"入库 status={theirs['status']} errors={len(theirs['errors'])} checks={len(theirs['checks'])}")
say(f"run_id 我的={mine['run_id']} 入库={theirs['run_id']}")
say(f"artifact_version 我的={mine['artifact_version']} 入库={theirs['artifact_version']}")
diff_ids = []
for a, b in zip(mine["checks"], theirs["checks"]):
    if (a["id"], a["status"], a["detail"]) != (b["id"], b["status"], b["detail"]):
        diff_ids.append((a["id"], b["id"], b["status"], a["status"], a["detail"][:200], b["detail"][:200]))
say(f"逐项（id/status/detail）不一致数：{len(diff_ids)}")
for row in diff_ids:
    say(f"  {row}")
mk, tk = mine["inputs"], theirs["inputs"]
for key in sorted(set(mk) | set(tk)):
    if key.endswith("_path"):
        continue
    same = mk.get(key) == tk.get(key)
    say(f"inputs.{key}: {'一致' if same else '**不同**'} {mk.get(key)} vs {tk.get(key)}")
say(f"id_inventory 相等：{mine['id_inventory'] == theirs['id_inventory']}")
say(f"全部 17 项状态：{[(c['id'], c['status']) for c in mine['checks']]}")
say("入库 selfcheck_result.json 中关键 detail 摘录：")
for c in theirs["checks"]:
    if c["id"] in ("C7", "C12", "C17", "C11", "C1"):
        say(f"  {c['id']} [{c['status']}] {c['detail'][:400]}")

say()
say("=" * 78)
say("C. check_stage_delivery 输出 vs 提交的 *_mode_output.txt")
say("=" * 78)
for label, mine_file, committed in (
    ("inputs", "my_check_inputs.txt", "check_inputs_mode_output.txt"),
    ("evidence", "my_check_evidence.txt", "check_evidence_mode_output.txt"),
):
    a = (OUT / mine_file).read_bytes()
    b = (RUN / committed).read_bytes()
    say(f"[{label}] 我的={a!r}")
    say(f"[{label}] 入库={b!r}")
    say(f"[{label}] 逐字节相同：{a == b}")

say()
say("=" * 78)
say("D. 证据目录文件 / 哈希清单 / manifest 双向核对")
say("=" * 78)
actual = sorted(p.relative_to(RUN).as_posix() for p in RUN.rglob("*") if p.is_file())
say(f"运行目录实际文件 {len(actual)} 个")
for name in actual:
    say(f"  {name}  {sha256_file(RUN / name)[:16]}…")
hash_txt = (RUN / "hashes_sha256.txt").read_text(encoding="utf-8")
parsed: dict[str, str] = {}
for match in re.finditer(r"([0-9a-fA-F]{64})\s+\*?([^\s]+)", hash_txt):
    parsed[match.group(2).replace("\\", "/")] = match.group(1).lower()
say(f"hashes_sha256.txt 解析 {len(parsed)} 条")
missing = [k for k in parsed if not (RUN / k).is_file() and not (ROOT / k).is_file()]
bad = []
for k, want in parsed.items():
    target = RUN / k if (RUN / k).is_file() else ROOT / k
    if target.is_file() and sha256_file(target) != want:
        bad.append(k)
say(f"  声明缺失={missing}  哈希不符={bad}  未列入清单的实际文件="
    f"{sorted(set(actual) - set(parsed) - {'hashes_sha256.txt'})}")

manifest = json.loads((RUN / "delivery_manifest.json").read_text(encoding="utf-8"))
say(f"manifest.files 条数={len(manifest.get('files', []))}  evidence_dir={manifest.get('evidence_dir')!r}")
say(f"manifest.checks={json.dumps(manifest.get('checks'), ensure_ascii=False)[:900]}")
m_missing, m_bad = [], []
for item in manifest["files"]:
    raw = str(item["path"]).replace("\\", "/")
    target = ROOT / raw
    if not target.is_file():
        m_missing.append(raw)
    elif sha256_file(target) != item["sha256"]:
        m_bad.append(raw)
say(f"manifest 声明缺失={m_missing}")
say(f"manifest 哈希不符={m_bad}")
declared_run = set()
for item in manifest["files"]:
    raw = str(item["path"]).replace("\\", "/")
    prefix = "report/evidence/S6-A/s6a_g0_20261022_r05/"
    if raw.startswith(prefix):
        declared_run.add(raw[len(prefix):])
    elif "/" not in raw:
        declared_run.add(raw)
say(f"manifest 未声明但实际存在的运行目录文件={sorted(set(actual) - declared_run - {'delivery_manifest.json'})}")
say(f"manifest 声明但实际缺失的运行目录文件={sorted(declared_run - set(actual))}")

say()
say("=" * 78)
say("E. r04(b20b670) vs r05(1632761) 逐字段比较")
say("=" * 78)
d4 = json.loads(git_blob(R04, json_rel).decode("utf-8"))
d5 = json.loads(git_blob(R05, json_rel).decode("utf-8"))
say(f"artifact_version: r04={d4['artifact_version']} r05={d5['artifact_version']}")
p4 = {i["id"]: i for i in d4["parameters"]}
p5 = {i["id"]: i for i in d5["parameters"]}
say(f"参数集合相等：{set(p4) == set(p5)}  数量 {len(p4)} -> {len(p5)}")
pf = []
for pid in sorted(set(p4) | set(p5)):
    if p4.get(pid) != p5.get(pid):
        pf.append((pid, p4.get(pid), p5.get(pid)))
say(f"参数逐字段差异数：{len(pf)}")
for pid, a, b in pf:
    say(f"  {pid}: {json.dumps(a, ensure_ascii=False)} -> {json.dumps(b, ensure_ascii=False)}")
say(f"r05 非 PENDING_APPROVAL 参数：{[i['id'] for i in d5['parameters'] if i['approval_status'] != 'PENDING_APPROVAL']}")
say(f"r05 参数草案值：{ {i['id']: i.get('draft_value') for i in d5['parameters']} }")


def ids(block: str) -> set[str]:
    return {i["id"] for i in d5[block]}


for block in ("transitions", "hard_invariants", "behavior_rows", "open_decisions", "parameters"):
    a = {i["id"] for i in d4[block]}
    b = {i["id"] for i in d5[block]}
    say(f"{block}: r04={len(a)} r05={len(b)}  新增={sorted(b - a)}  删除={sorted(a - b)}")
say(f"states: r04={d4['states']} r05={d5['states']}")
say(f"顶层键 新增={sorted(set(d5) - set(d4))}  删除={sorted(set(d4) - set(d5))}")
say(f"predicates 键变化: {sorted(set(d5['predicates']) - set(d4['predicates']))}")
say(f"revision 键变化: {sorted(set(d5['revision']) - set(d4['revision']))} / 删除 {sorted(set(d4['revision']) - set(d5['revision']))}")
say(f"non-param 顶层字段差异：")
for key in sorted(set(d4) & set(d5)):
    if key in ("parameters", "revision", "run_id", "artifact_version", "status_label", "status_note",
               "baseline", "supersedes_run_id", "limitations", "predicate_binding_policy", "stable_latching"):
        continue
    if d4[key] != d5[key]:
        say(f"  {key} 不同（长度 {len(json.dumps(d4[key], ensure_ascii=False))} -> "
            f"{len(json.dumps(d5[key], ensure_ascii=False))}）")
say(f"baseline: {json.dumps(d4['baseline'], ensure_ascii=False)}\n       -> {json.dumps(d5['baseline'], ensure_ascii=False)}")
say(f"revision.review_verdict: r04={d4['revision']['review_verdict']!r}")
say(f"                         r05={d5['revision']['review_verdict']!r}")
say(f"r05 semantic_changes={d5['revision']['semantic_changes']}")
say(f"r05 supersedes={d5['supersedes_run_id']}  revision.supersedes={d5['revision']['supersedes_run_id']}")
say(f"r05 revision.changes 条数={len(d5['revision']['changes'])} issues="
    f"{[c['issue'] for c in d5['revision']['changes']]}")

say()
say("=" * 78)
say("F. 必需核查项 1：M5 限定 / stable_latching / predicate_binding_policy")
say("=" * 78)
m5 = next(i for i in d5["transitions"] if i["id"] == "M5")
say(f"JSON M5.condition = {m5['condition']!r}")
say(f"JSON M5.window_advance_required = {m5.get('window_advance_required')!r}")
say(f"JSON M5 keys = {sorted(m5)}")
latch = d5["stable_latching"]
say(f"stable_latching.suppressed_trigger_release = {latch['suppressed_trigger_release']!r}")
say(f"stable_latching keys = {sorted(latch)}")
say(f"predicate_binding_policy.statement = {d5['predicate_binding_policy']['statement']!r}")
say(f"predicate_binding_policy.rule = {d5['predicate_binding_policy']['rule']!r}")
say(f"predicate_binding_policy.empty_list_rule = {d5['predicate_binding_policy'].get('empty_list_rule')!r}")
doc_text = (ROOT / doc_rel).read_text(encoding="utf-8")
m5_rows = [ln for ln in doc_text.splitlines() if re.match(r"^\| M5 \|", ln)]
say(f"文档 §4 M5 行数={len(m5_rows)}")
for ln in m5_rows:
    say(f"  {ln}")
say(f"文档含 statement 逐字：{d5['predicate_binding_policy']['statement'] in doc_text}")
state_text = (ROOT / ".codex/STATE.md").read_text(encoding="utf-8")
say(f"STATE 含 statement 逐字：{d5['predicate_binding_policy']['statement'] in state_text}")
say(f"STATE 含 stable_latching.statement 逐字：{latch['statement'] in state_text}")
say(f"latch.statement = {latch['statement']!r}")
for marker in ("窗口推进帧", "state ∈ {OK,NO_HAND}", "state ∈ {OK, NO_HAND}", "stale=false", "非重复", "非倒序"):
    say(f"  marker {marker!r}: JSON M5={marker in m5['condition']}  文档M5行="
        f"{any(marker in ln for ln in m5_rows)}  release={marker in latch['suppressed_trigger_release']}")

say()
say("=" * 78)
say("G. 必需核查项 4：artifact_version 三处一致 + ID/文件声明 + 声明纪律")
say("=" * 78)
say(f"JSON artifact_version={d5['artifact_version']}")
doc_ver_hits = [ln for ln in doc_text.splitlines() if "v1.4" in ln or "S6A-G0-v1.4" in ln]
say(f"文档提及 v1.4 行数={len(doc_ver_hits)}；含 'S6A-G0-v1.4'：{'S6A-G0-v1.4' in doc_text and 'v1.4' in doc_text}")
say(f"文档是否仍出现 'S6A-G0-v1.3'：{'S6A-G0-v1.3' in doc_text}（历史修订记录内属允许）")
for key in ("fix_record.json", "coverage_matrix.json", "limitations_not_executed.json", "S6A_run_summary.md"):
    txt = (RUN / key).read_text(encoding="utf-8")
    say(f"{key}: v1.4 出现={txt.count('v1.4')} v1.3 出现={txt.count('v1.3')} r05 出现={txt.count('r05')}")

say()
say("未跟踪 WIP src/stage6 引用核对（N-r04-05）：")
for rel in ("src/stage6/s6_core.py", "src/stage6/s6_params.py", "docs/stage6/s6b_frozen_interface_v1.json"):
    p = ROOT / rel
    if not p.is_file():
        say(f"  {rel}: 不存在")
        continue
    txt = p.read_text(encoding="utf-8", errors="replace")
    refs = sorted(set(re.findall(r"docs/stage6/[A-Za-z0-9_./\-]+", txt)))
    say(f"  {rel}: {len(txt.splitlines())} 行；引用 docs/stage6/* = {refs}")
    for ref in refs:
        say(f"     {ref} 存在={(ROOT / ref).is_file()}")
say(f"  git status --short：")
say(subprocess.run(["git", "-C", str(ROOT), "status", "--short"], capture_output=True, text=True,
                   encoding="utf-8").stdout.rstrip())

say()
say("声明纪律扫描（是否自称已审查/已通过/G0 通过）：")
haystacks = {
    "doc": doc_text,
    "json": json.dumps(d5, ensure_ascii=False),
    "STATE": state_text,
    "fix_record": (RUN / "fix_record.md").read_text(encoding="utf-8"),
    "run_summary": (RUN / "S6A_run_summary.md").read_text(encoding="utf-8"),
}
for label, text in haystacks.items():
    for phrase in ("已审查", "审查通过", "已通过", "G0 通过", "已实测通过", "验收已通过"):
        start = 0
        while True:
            idx = text.find(phrase, start)
            if idx < 0:
                break
            ctx = text[max(0, idx - 70): idx + len(phrase) + 70].replace("\n", " ")
            say(f"  [{label}] {phrase} → …{ctx}…")
            start = idx + len(phrase)

(OUT / "my_checks.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))