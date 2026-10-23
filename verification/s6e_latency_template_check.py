#!/usr/bin/env python3
"""S6-E 延迟占位模板**禁填造**校验器。

    python -B verification/s6e_latency_template_check.py --project-root <abs> [--inject-self-test] [--out <json>]

检查项：
* L1 身份/状态齐全，`status` 必须为 `TEMPLATE_ONLY_NOT_RUN`
* L2 `rule.t6_a03_value` 必须为 `NOT_RUN`
* L3 `placeholders` 内凡以 `_ns` 结尾的字段必须为 `null`；`value_status` 必须为 `NOT_RUN`
* L4 `acceptance_gate.t6_a03_limit_ms` 必须为 `null`（数值未获批）
* L5 行为表 `T6-A03` 的 `draft_value` 必须为 `null` 且其 `value_status` 含 `NOT_RUN`（与批准记录一致）
* L6 方法学文档存在，且含关键定义与「回放不构成实时证据」与「board_monotonic」等必备声明
* L7 行为表 `T6-STALE_LIMIT.draft_value` 必须为 200（跨阶段同源常量）

`--inject-self-test`：在临时副本内注入 5 类必失败缺陷（填 `latency_interaction_p95_ns`、把
`t6_a03_value` 写成数值、填 `t6_a03_limit_ms`、把 `value_status` 改成已测量、从文档删除「回放不构成实时证据」），
要求**每条都必须被判失败**；基线必须 PASS。
退出码：0 = 全部 PASS（且注入全被捕获）；1 = 存在失败。
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

TEMPLATE = "docs/stage6/s6e_latency_measurement_template_v1.json"
METHOD = "docs/stage6/S6E_latency_methodology_v1.md"
BEHAVIOR = "docs/stage6/s6a_stage6_g0_behavior_v1.json"

DOC_NEEDLES = (
    "t_effective − t_trigger",
    "t_effective − window_complete",
    "回放不构成实时证据",
    "board_monotonic",
    "不得填造",
    "T6-A03",
)


def evaluate(root: Path) -> list[str]:
    errors: list[str] = []
    tpath = root / TEMPLATE
    if not tpath.is_file():
        return [f"L1: 缺少模板 {TEMPLATE}"]
    data = json.loads(tpath.read_text(encoding="utf-8"))
    behavior = {p["id"]: p for p in json.loads((root / BEHAVIOR).read_text(encoding="utf-8"))["parameters"]}

    # L1
    for key in ("schema_version", "artifact", "artifact_version", "task_id", "run_id", "status"):
        if not data.get(key):
            errors.append(f"L1: 缺少字段 {key}")
    if data.get("status") != "TEMPLATE_ONLY_NOT_RUN":
        errors.append(f"L1: status 必须为 TEMPLATE_ONLY_NOT_RUN（实际 {data.get('status')!r}）")

    # L2
    rule = data.get("rule", {})
    if rule.get("t6_a03_value") != "NOT_RUN":
        errors.append(f"L2: rule.t6_a03_value 必须为 NOT_RUN（实际 {rule.get('t6_a03_value')!r}）")
    if rule.get("replay_is_not_realtime_evidence") is not True:
        errors.append("L2: 必须声明 replay_is_not_realtime_evidence=true")

    # L3
    placeholders = data.get("placeholders", {})
    filled = {k: v for k, v in placeholders.items()
              if k.endswith("_ns") and v is not None}
    if filled:
        errors.append(f"L3: 存在已填写的 *_ns 占位（禁止填造）：{filled}")
    if placeholders.get("value_status") != "NOT_RUN":
        errors.append(f"L3: placeholders.value_status 必须为 NOT_RUN（实际 {placeholders.get('value_status')!r}）")
    for key in ("filled_by", "filled_from_run_id", "evidence_class"):
        if placeholders.get(key) is not None:
            errors.append(f"L3: {key} 在未测量时必须为 null")

    # L4
    gate = data.get("acceptance_gate", {})
    if gate.get("t6_a03_limit_ms") is not None:
        errors.append(f"L4: acceptance_gate.t6_a03_limit_ms 必须为 null（实际 {gate.get('t6_a03_limit_ms')!r}）")
    if gate.get("t6_a03_value_status") != "NOT_RUN":
        errors.append(f"L4: acceptance_gate.t6_a03_value_status 必须为 NOT_RUN（实际 {gate.get('t6_a03_value_status')!r}）")

    # L5
    a03 = behavior.get("T6-A03", {})
    if a03.get("draft_value") is not None:
        errors.append(f"L5: 行为表 T6-A03.draft_value 必须为 null（实际 {a03.get('draft_value')!r}）")
    if "NOT_RUN" not in str(a03.get("value_status", "")):
        errors.append("L5: 行为表 T6-A03.value_status 必须含 NOT_RUN")

    # L6
    mpath = root / METHOD
    if not mpath.is_file():
        errors.append(f"L6: 缺少方法学文档 {METHOD}")
    else:
        text = mpath.read_text(encoding="utf-8")
        missing = [n for n in DOC_NEEDLES if n not in text]
        if missing:
            errors.append(f"L6: 方法学文档缺少必备声明 {missing}")

    # L7
    stale = behavior.get("T6-STALE_LIMIT", {}).get("draft_value")
    if stale != 200:
        errors.append(f"L7: T6-STALE_LIMIT 必须为 200（实际 {stale}）")
    if data.get("approval_binding", {}).get("stale_age_limit_ms") != 200:
        errors.append("L7: 模板内 stale_age_limit_ms 必须为 200")
    return errors


INJECTIONS = (
    ("J1-filled-latency-ns", lambda d: d["placeholders"].__setitem__("latency_interaction_p95_ns", 180000000)),
    ("J2-t6-a03-numeric-value", lambda d: d["rule"].__setitem__("t6_a03_value", "200ms")),
    ("J3-filled-a03-limit", lambda d: d["acceptance_gate"].__setitem__("t6_a03_limit_ms", 500)),
    ("J4-value-status-measured", lambda d: d["placeholders"].__setitem__("value_status", "MEASURED")),
    ("J5-doc-missing-replay-limit", lambda d: None),  # 文档类注入在下方单独处理
)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True)
    ap.add_argument("--inject-self-test", action="store_true")
    ap.add_argument("--out", default="tmp/6/s6e_latency_template_check.json")
    args = ap.parse_args(argv)
    root = Path(args.project_root).resolve()
    baseline_errors = evaluate(root)
    payload = {
        "schema_version": 1, "artifact": "s6e_latency_template_check",
        "run_id": "s6e_boardfree_20261024_r01",
        "checks": "L1..L7（状态/禁填造占位/上限未获批/行为表 T6-A03 与 stale 一致/方法学文档必备声明）",
        "baseline": {"verdict": "ALL_PASS" if not baseline_errors else "FAILED", "errors": baseline_errors},
        "verdict": "ALL_PASS" if not baseline_errors else "FAILED",
    }
    rc = 0 if not baseline_errors else 1
    if args.inject_self_test:
        injections = []
        all_caught = True
        for name, mutate in INJECTIONS:
            with tempfile.TemporaryDirectory() as tmp:
                copy_root = Path(tmp) / "copy"
                (copy_root / "docs/stage6").mkdir(parents=True, exist_ok=True)
                for rel in (TEMPLATE, METHOD, BEHAVIOR):
                    shutil.copyfile(root / rel, copy_root / rel)
                if name == "J5-doc-missing-replay-limit":
                    mpath = copy_root / METHOD
                    text = mpath.read_text(encoding="utf-8").replace("回放不构成实时证据", "（删除该声明）")
                    mpath.write_text(text, encoding="utf-8")
                else:
                    tpath = copy_root / TEMPLATE
                    doc = json.loads(tpath.read_text(encoding="utf-8"))
                    mutate(doc)
                    tpath.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                errs = evaluate(copy_root)
                caught = bool(errs)
                all_caught = all_caught and caught
                injections.append({"id": name, "caught": caught, "errors": errs[:2]})
        payload["injections"] = injections
        payload["self_test"] = {"verdict": "AS_EXPECTED" if (all_caught and not baseline_errors) else "UNEXPECTED",
                                "all_injections_caught": all_caught}
        payload["verdict"] = payload["self_test"]["verdict"]
        rc = 0 if (all_caught and not baseline_errors) else 1
    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": payload["verdict"], "baseline_errors": len(baseline_errors),
                      "self_test": payload.get("self_test", {}).get("verdict"),
                      "missed": [i["id"] for i in payload.get("injections", []) if not i["caught"]]},
                     ensure_ascii=False))
    for e in baseline_errors:
        print("ERR " + e)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())