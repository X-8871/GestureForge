# -*- coding: utf-8 -*-
"""独立评审：故障注入，验证被审自检的判别力（写隔离目录，不碰被审文件）。

做法：从被审提交的 git 字节取出 JSON/DOC，注入已知缺陷，再用**最终版自检**跑，
记录真实退出码与失败检查项；与未注入基线对照。
"""
import json, subprocess, os, io, sys, copy

WT = r"D:\codex-worktrees\w6"
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "faultinj")
os.makedirs(WORK, exist_ok=True)
JREL = "docs/stage6/s6a_stage6_g0_behavior_v1.json"
DOCREL = "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"
REV = "b20b670"

def blob(rev, rel):
    p = subprocess.run(["git", "-C", WT, "cat-file", "blob", f"{rev}:{rel}"], capture_output=True)
    assert p.returncode == 0, p.stderr
    return p.stdout

BASE_JSON = blob(REV, JREL).decode("utf-8")
BASE_DOC = blob(REV, DOCREL).decode("utf-8")
CASES = os.path.join(WT, "report/evidence/S6-A/s6a_g0_20261022_r04/hand_computed_cases.json")
UPSTREAM = os.path.join(WT, "report/evidence/S6-A/s6a_g0_20261022_r04/upstream_bindings.json")
EV = os.path.join(WT, "report/evidence/S6-A/s6a_g0_20261022_r04")
STATE = os.path.join(WT, ".codex/STATE.md")
SELFCHECK = os.path.join(WT, "verification/s6_g0_selfcheck.py")

def run_case(name, doc=BASE_DOC, data=None):
    tag = name
    jp = os.path.join(WORK, f"{tag}.json")
    dp = os.path.join(WORK, f"{tag}.md")
    op = os.path.join(WORK, f"{tag}.result.json")
    with open(dp, "w", encoding="utf-8", newline="") as f:
        f.write(doc)
    payload = BASE_JSON if data is None else json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    with open(jp, "w", encoding="utf-8", newline="") as f:
        f.write(payload)
    cmd = [sys.executable, "-B", SELFCHECK, "--json", jp, "--doc", dp,
           "--cases", CASES, "--upstream", UPSTREAM, "--out", op,
           "--project-root", WT, "--evidence-dir", EV, "--state", STATE]
    p = subprocess.run(cmd, capture_output=True, cwd=WT)
    rc = p.returncode
    res = json.load(open(op, encoding="utf-8"))
    failed = [c["id"] for c in res["checks"] if c["status"] == "FAIL"]
    detail = {c["id"]: c["detail"] for c in res["checks"] if c["status"] == "FAIL"}
    return rc, res["status"], failed, detail

def mut(tag, fn_doc=None, fn_data=None, expect=None, note=""):
    doc = BASE_DOC
    data = json.loads(BASE_JSON)
    if fn_doc: doc = fn_doc(doc)
    if fn_data: fn_data(data)
    rc, status, failed, detail = run_case(tag, doc, data)
    print(f"\n### [{tag}] {note}")
    print(f"    预期触发: {expect}")
    print(f"    实测: exit={rc} status={status} FAILED_CHECKS={failed}")
    for k, v in detail.items():
        print(f"      - {k}: {v[:400]}")
    return rc, status, failed

print("=" * 100)
print("基线对照（无注入，必须 exit 0 / ALL_PASS）")
rc, st, fa, _ = run_case("baseline")
print(f"    exit={rc} status={st} failed={fa}")

print("=" * 100)
print("R3-B01 类回归测试（C12 判别力）")

mut("f1_s02_text",
    fn_doc=lambda d: d.replace("连续 `WINDOW_MATCH` 帧数 ≥ `T6-S02`",
                               "连续匹配帧数 ≥ `T6-S02`", 1),
    expect="C12 FAIL（§12 T6-S02 行回到未绑谓词写法）",
    note="把 §12 T6-S02 行改回 R3-B01 原始缺陷写法")

mut("f2_l02_text",
    fn_doc=lambda d: d.replace("| 丢失时间 `T6-L02` | `t_now − t_last_target_continues ≥ T6-L02` |",
                               "| 丢失时间 `T6-L02` | `t_now − t_last_match ≥ T6-L02` |", 1),
    expect="C12 FAIL（丢失时间行改用已废弃锚点 t_last_match，无“废弃”标注）",
    note="把 §12 T6-L02 行改回 t_last_match")

mut("f3_matched_frames",
    fn_doc=lambda d: d.replace("## 14. 阈值与指标登记",
                               "锚点名称：matched_frames 表示匹配帧计数。\n\n## 14. 阈值与指标登记", 1),
    expect="C12 FAIL（新插入 matched_frames 未标注废弃）",
    note="插入含 matched_frames 的规格句（无“废弃”标注）")

mut("f4_t_last_match_normative",
    fn_doc=lambda d: d.replace("## 14. 阈值与指标登记",
                               "丢失判定锚点取 t_last_match 的值作为条件输入。\n\n## 14. 阈值与指标登记", 1),
    expect="C12 FAIL（规范句用 t_last_match 且附近无“废弃”）",
    note="插入规范语义使用 t_last_match")

mut("f5_whitelist_bypass",
    fn_doc=lambda d: d.replace("## 14. 阈值与指标登记",
                               "本条为废弃说明：" + "填充" * 40 +
                               " 条件仍用 t_last_match 判定。\n\n## 14. 阈值与指标登记", 1),
    expect="C12 PASS 或 FAIL？用于验证 ±60 字符白名单窗（“废弃”距 token 超过 60 字符）",
    note="把“废弃”放到距 token >60 字符处，测试白名单窗是否被绕过")

mut("f6_whitelist_bypass_near",
    fn_doc=lambda d: d.replace("## 14. 阈值与指标登记",
                               "已废弃写法 t_last_match 不再使用。\n\n## 14. 阈值与指标登记", 1),
    expect="C12 PASS（“废弃”紧邻 token，属放行白名单）",
    note="紧邻“已废弃”标注 → 应被放行（验证白名单确实生效）")

print("=" * 100)
print("R3-B02 类回归测试（全量双向断言判别力）")

def rm_usedby(name, entry):
    def f(data):
        lst = data["predicates"][name]["used_by"]
        data["predicates"][name]["used_by"] = [x for x in lst if not x.startswith(entry)]
    return f

def add_usedby(name, entry):
    def f(data):
        data["predicates"][name]["used_by"].append(entry)
    return f

mut("f7_only_forward", fn_data=add_usedby("WINDOW_MATCH", "B02 幽灵绑定"),
    expect="C12 FAIL only_forward=[B02]",
    note="往 WINDOW_MATCH.used_by 加入不存在的反向绑定 B02")

mut("f8_only_reverse", fn_data=rm_usedby("TARGET_CONTINUES", "B14"),
    expect="C12 FAIL only_reverse=[B14]",
    note="从 TARGET_CONTINUES.used_by 删掉 B14（B14 仍声明 predicates_used）")

mut("f9_m1_overdeclare",
    fn_data=lambda data: [t for t in data["transitions"] if t["id"] == "M1"][0].__setitem__(
        "predicates_used", ["TARGET_CONTINUES", "WINDOW_MATCH"]),
    expect="C12 FAIL（M1 必须只声明 TARGET_CONTINUES）",
    note="M1 过度声明 WINDOW_MATCH")

mut("f10_b13_field",
    fn_data=lambda data: [b for b in data["behavior_rows"] if b["id"] == "B13"][0].__setitem__(
        "predicates_used", ["TARGET_CONTINUES"]),
    expect="C12 FAIL（M5/B13 不得出现 predicates_used 字段）",
    note="给 B13 加上 predicates_used，制造叙述不实")

mut("f11_undefined_predicate",
    fn_data=lambda data: [t for t in data["transitions"] if t["id"] == "M8"][0].__setitem__(
        "predicates_used", ["TARGET_CONTINUES", "GHOST_PRED"]),
    expect="C12 FAIL 含未定义谓词",
    note="引入未定义谓词名")

mut("f12_empty_predicates",
    fn_data=lambda data: [t for t in data["transitions"] if t["id"] == "M2"][0].__setitem__(
        "predicates_used", []),
    expect="C12 是否捕获空列表（策略要求不用谓词的条目不得出现该字段）",
    note="给不使用谓词的 M2 加空列表 predicates_used（策略违规探测）")

print("=" * 100)
print("观察项 / STABLE 锁存（C17 判别力）")

def add_m16(data):
    data["transitions"].append({
        "id": "M16", "from": "STABLE", "to": "CANDIDATE", "priority": "P3",
        "condition": "窗口中断即退回候选", "params": [], "predicates_used": ["WINDOW_MATCH"],
    })
    data["stable_latching"]["exit_paths"] = ["M2", "M10", "M5", "M16"]

mut("f13_stable_demote", fn_data=add_m16,
    expect="C17 FAIL（锁存定论下不得存在 STABLE→CANDIDATE）",
    note="新增 STABLE→CANDIDATE 迁移并把 exit_paths 改一致（测 C17 的 demote 断言）")

mut("f14_latch_false",
    fn_data=lambda data: data["stable_latching"].__setitem__("latched", False),
    expect="C17 FAIL",
    note="stable_latching.latched 改为 false")

mut("f15_exitpath_drift",
    fn_data=lambda data: data["stable_latching"].__setitem__("exit_paths", ["M2", "M5"]),
    expect="C17 FAIL（退出路径与迁移表不一致）",
    note="声明退出路径与迁移表漂移")

print("=" * 100)
print("参数纪律（C4 判别力）")
mut("f16_param_approved",
    fn_data=lambda data: [p for p in data["parameters"] if p["id"] == "T6-K01"][0].__setitem__(
        "approval_status", "APPROVED"),
    expect="C4 FAIL（有待批准项被标为已批准）",
    note="把 T6-K01 的 approval_status 改成 APPROVED")

print("\n" + "=" * 100)
print("故障注入完成（所有产物在隔离目录 faultinj/）")