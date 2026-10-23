#!/usr/bin/env python3
"""已批准包内**不得出现 PENDING/待批准陈述**（BLK-D2 机读断言；两侧通用）。

    python -B verification/approved_package_scan.py --project-root <abs> --run-dir <rel> [--inject-self-test]

## 判定规则（r13 收紧版；对应 FREEZE_DELTA_E §七.4）

逐行扫描该 RunId 目录内全部文本文件 + 行为表 JSON + 规格文档；凡行内出现
**大小写不敏感**的 `PENDING` 或 `待批准` 令牌者，除下列**逐行豁免**外一律判为命中（FAIL）：

1. `HISTORICAL`：行内含**机读历史标记** `【历史语境` 或 `[HISTORICAL]`（机器可读、逐行）；
2. `ALLOWED`：行内是**非批准类**的合法状态令牌（`PENDING_REVIEW`/`PENDING_CONFIRMATION`/
   `PENDING_MODULE`/`PENDING_MEASUREMENT`/`复评 PENDING`/`待 Wong 确认`/`待复核`），
   或 `"pending_approval": false` 这类**否定式**机器字段，或自测夹具字段名 `injected_pending`；
3. `PROHIBITION`：行本身是**禁止/规则描述**（含 `不得存在`/`不得出现`/`不存在 PENDING`/
   `注入|改回 …PENDING…FAIL`/`反向自测`/`必须 FAIL`）——它禁止 PENDING，不是断言 PENDING。

`SKIP_FILES`：注入/探针/旧包失败证据（`probe_*`、`selfcheck_*failure*`）按**文件级**豁免——
这些文件的存在意义就是保存「必须失败」的注入文本，不是本包的状态断言。

## 判别力自测（两向）

`--inject-self-test`：在**临时副本**内注入 7 类**必判失败**形态与 4 类**必须放行**对照，
要求逐条符合预期（B3/B6/B7 即终审批次 E 点名的机读假字段与文档状态行），真实目录不被触碰。

退出码：0 = CLEAN/AS_EXPECTED；1 = 有命中或自测未达预期。
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path

# 机读历史标记：必须**显式**出现在行内；不再用裸「当时」这类宽词
HISTORICAL = re.compile(r"【历史语境|\[HISTORICAL\]|HISTORICAL_CONTEXT")

# 非批准类合法状态 / 否定式机器字段 / 自测夹具字段名（逐行放行）
ALLOWED = re.compile(
    r"PENDING_REVIEW|PENDING_CONFIRMATION|PENDING_MODULE|PENDING_MEASUREMENT|"
    r"DELIVERED_PENDING_REVIEW|复评\s*PENDING|"
    r"\"(?:any_parameter_|all_parameters_)?pending_approval\"\s*:\s*false|"
    r"injected_pending|待\s*Wong\s*确认|待复核|待 ?Wong ?批",
    re.IGNORECASE,
)

# 禁止/规则描述：行文**否定** PENDING，或**要求注入后必须失败**
PROHIBITION = re.compile(
    r"不得(存在|出现|残留|使用)|禁止出现|不允许(出现|存在)|不存在\s*(PENDING|待批准)|不再(出现|残留)|"
    r"(注入|改回|置为|人为把)[^\n]{0,40}(PENDING|待批准)[^\n]{0,40}(FAIL|失败)|"
    r"(PENDING|待批准)[^\n]{0,20}(?:则|即|→)[^\n]{0,12}(?:必须)?\s*FAIL|"
    r"必须\s*FAIL|反向自测",
    re.IGNORECASE,
)

# 文件级豁免：注入/探针/旧包失败证据（保存的就是「必须失败」的注入文本）
SKIP_FILES = re.compile(r"^(probe_.*|selfcheck_.*failure.*)$", re.IGNORECASE)

# 令牌 = 全部「仍待批准」族：PENDING / 待批准 / 机读假字段的 not_approved 变体
TOKENS = re.compile(r"PENDING|待批准|not_approved", re.IGNORECASE)

# 必判失败形态（终审 E 的 B1..B7；逐条必须被捕获）
MUST_FAIL_FORMS = [
    ("B1-approval-status-field", '"approval_status": "PENDING_APPROVAL"'),
    ("B2-package-thresholds-pending", "本包全部阈值与指标仍为待批准状态"),
    ("B3-machine-field-all-params", '"all_parameters_pending_approval": true'),
    ("B4-machine-field-thresholds", '"thresholds_are_draft_not_approved": true'),
    ("B5-machine-field-params", '"parameters_pending_approval": true'),
    ("B6-doc-status-line", "> **状态：`G0_PACKET_APPROVED_20261023`（待批准）。**"),
    ("B7-doc-constraint-line", "受 `T6-A01` 约束（待批准）。"),
]
# 必须放行对照（合法状态 / 历史标记 / 规则描述）
MUST_PASS_FORMS = [
    ("C1-pending-confirmation", '"pending_confirmation": "U6-16：若 G0 改为不锁存，属实质语义变更。"'),
    ("C2-pending-review", '"review_status_after_fix": "PENDING_REVIEW（是否再复评由项目总控决定）"'),
    ("C3-historical-marker", "全部阈值待批准。　【历史语境：上述为当时状态（该版本产出时尚未批准）】"),
    ("C4-prohibition-rule", 'C4 批准纪律（不得存在 PENDING；每项有批准索引）'),
]


def line_is_hit(line: str) -> bool:
    if not TOKENS.search(line):
        return False
    if HISTORICAL.search(line) or ALLOWED.search(line) or PROHIBITION.search(line):
        return False
    return True


def find_hits(paths: list[Path]) -> list[str]:
    hits: list[str] = []
    for path in paths:
        if not path.is_file() or SKIP_FILES.match(path.name):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if line_is_hit(line):
                hits.append(f"{path.name}:{i}: {line.strip()[:110]}")
    return hits


def scan(root: Path, run_rel: str) -> list[str]:
    run_dir = root / run_rel
    targets = [p for p in run_dir.rglob("*") if p.is_file()]
    targets += [root / "docs/stage6/s6a_stage6_g0_behavior_v1.json",
                root / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"]
    return find_hits(targets)


def counterexample_self_test() -> dict:
    """两向自测：必判失败形态全部命中，必须放行对照全部不命中。"""
    with tempfile.TemporaryDirectory() as tmp:
        probe_dir = Path(tmp)
        must_fail_hits: dict[str, bool] = {}
        for form_id, text in MUST_FAIL_FORMS:
            probe = probe_dir / f"{form_id}.txt"
            probe.write_text(text + "\n", encoding="utf-8")
            must_fail_hits[form_id] = bool(find_hits([probe]))
        must_pass_hits: dict[str, bool] = {}
        for form_id, text in MUST_PASS_FORMS:
            probe = probe_dir / f"{form_id}.txt"
            probe.write_text(text + "\n", encoding="utf-8")
            must_pass_hits[form_id] = bool(find_hits([probe]))
    caught_all = all(must_fail_hits.values())
    clean_all = not any(must_pass_hits.values())
    return {
        "must_fail_caught": must_fail_hits,
        "must_pass_clean": must_pass_hits,
        "missed_forms": [k for k, v in must_fail_hits.items() if not v],
        "false_positive_forms": [k for k, v in must_pass_hits.items() if v],
        "verdict": "AS_EXPECTED" if (caught_all and clean_all) else "UNEXPECTED",
    }


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
               "rule": ("已批准版包内不得出现 PENDING/待批准 陈述（大小写不敏感；"
                        "逐行机读历史标记/非批准类状态/禁止性规则描述除外；"
                        "probe_* 与 selfcheck_*failure* 按文件豁免）"),
               "hits": hits, "verdict": "CLEAN" if not hits else "PENDING_TEXT_FOUND"}
    if args.inject_self_test:
        self_test = counterexample_self_test()
        payload["self_test"] = self_test
        payload["verdict"] = ("AS_EXPECTED" if (not hits and self_test["verdict"] == "AS_EXPECTED")
                              else "UNEXPECTED")
    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": payload["verdict"], "hits": len(hits),
                      "self_test": payload.get("self_test", {}).get("verdict"),
                      "missed_forms": payload.get("self_test", {}).get("missed_forms", []),
                      "false_positive_forms": payload.get("self_test", {}).get("false_positive_forms", [])},
                     ensure_ascii=False))
    ok = payload["verdict"] in ("CLEAN", "AS_EXPECTED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())