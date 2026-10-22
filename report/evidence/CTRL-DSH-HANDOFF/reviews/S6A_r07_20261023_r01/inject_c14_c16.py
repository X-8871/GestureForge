#!/usr/bin/env python3
"""C14/C16/C7 判别力注入（我自己构造，隔离目录运行，不改被审文件）。"""
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ISO = Path(r"D:\FPGA_Competition\tmp\review\S6A_r07_20261023_r01")
REPO = ISO / "repo3"
EV = REPO / "report/evidence/S6-A/s6a_g0_20261022_r07"
selfcheck = REPO / "verification/s6_g0_selfcheck.py"
base = json.loads((REPO / "docs/stage6/s6a_stage6_g0_behavior_v1.json").read_text(encoding="utf-8"))


def run(label, data, cases=None):
    jp = ISO / f"inj_{label}.json"
    jp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cp = EV / "hand_computed_cases.json" if cases is None else cases
    cmd = [sys.executable, "-B", str(selfcheck), "--json", str(jp),
           "--doc", str(REPO / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"),
           "--cases", str(cp), "--upstream", str(EV / "upstream_bindings.json"),
           "--out", str(ISO / f"inj_{label}_result.json"), "--project-root", str(REPO),
           "--evidence-dir", str(EV)]
    done = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", check=False)
    result = json.loads((ISO / f"inj_{label}_result.json").read_text(encoding="utf-8"))
    failed = [c["id"] for c in result["checks"] if c["status"] == "FAIL"]
    detail = {c["id"]: c.get("detail", "")[:150] for c in result["checks"] if c["status"] == "FAIL"}
    print(f"[{label}] exit={done.returncode} failed={failed}")
    for k, v in detail.items():
        print(f"    {k}: {v}")
    return failed


# C16-1：把 M4 状态改回不可达
d = json.loads(json.dumps(base))
d["reachability"]["transitions"]["M4"]["status"] = "UNREACHABLE_UNDER_DRAFT_PARAMS"
f = run("c16_m4_unreachable", d)
assert "C16" in f, "C16 必须捕获 M4 不可达回退"

# C16-2：状态保留 REACHABLE，但理由去掉机制关键词
d = json.loads(json.dumps(base))
d["reachability"]["transitions"]["M4"]["reason"] = "T6-S04 与 T6-L02 比较后判定可达"
f = run("c16_reason_no_mechanism", d)
assert "C16" in f, "C16 必须捕获理由缺机制关键词"

# C16-3：U6-12 回到「删除 M4」旧口径
d = json.loads(json.dumps(base))
u = next(i for i in d["open_decisions"] if i["id"] == "U6-12")
u["item"] = "T6-S04/M4 可达性：调整 T6-S04 < T6-L02 或删除 M4/T6-S04"
u["note"] = "原选项：删除 M4 与 T6-S04。"
f = run("c16_u612_delete", d)
assert "C16" in f, "C16 必须捕获 U6-12 删除口径回退"

# C14：B07.condition 回退旧措辞
d = json.loads(json.dumps(base))
row = next(r for r in d["behavior_rows"] if r["id"] == "B07")
row["condition"] = "连续 WINDOW_MATCH 帧数 ≥ T6-S02 且窗口时长 ≥ T6-S01；完成时刻=第 N 个 WINDOW_MATCH 结果到达时刻；NO_HAND 不计入"
f = run("c14_b07_old", d)
assert "C14" in f, "C14 必须捕获旧措辞"

# C14：§9 文档口径回退（改 doc 副本）
doc = (REPO / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md").read_text(encoding="utf-8")
doc2 = doc.replace("**第一个同时满足帧数与时长（取较晚）的帧**", "**第 T6-S02 个 WINDOW_MATCH 结果到达且时长条件同时满足的那一帧**")
bad_doc = ISO / "inj_doc_old.md"
bad_doc.write_text(doc2, encoding="utf-8")
cmd = [sys.executable, "-B", str(selfcheck), "--json", str(REPO / "docs/stage6/s6a_stage6_g0_behavior_v1.json"),
       "--doc", str(bad_doc), "--cases", str(EV / "hand_computed_cases.json"),
       "--upstream", str(EV / "upstream_bindings.json"), "--out", str(ISO / "inj_doc_old_result.json"),
       "--project-root", str(REPO), "--evidence-dir", str(EV)]
done = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
res = json.loads((ISO / "inj_doc_old_result.json").read_text(encoding="utf-8"))
failed = [c["id"] for c in res["checks"] if c["status"] == "FAIL"]
print(f"[c14_doc_s9_old] exit={done.returncode} failed={failed}")
assert "C14" in failed, "C14 必须捕获文档 §9 旧措辞"
print("INJECTION_OK：C14/C16 对旧口径与不可达回退均 FAIL（具备判别力）")