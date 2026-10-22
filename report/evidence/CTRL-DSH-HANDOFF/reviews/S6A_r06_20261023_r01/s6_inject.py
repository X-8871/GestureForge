#!/usr/bin/env python3
# 只读检查脚本 6：生成注入副本（全部写隔离目录）
import json, sys, io, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ISO = pathlib.Path(r"D:\FPGA_Competition\tmp\review\S6A_r06_20261023_r01")
EV = ISO / "blobs/r06ev/report/evidence/S6-A/s6a_g0_20261022_r06"
W = ISO / "runs"
W.mkdir(exist_ok=True)

cases = json.load(open(EV / "hand_computed_cases.json", encoding="utf-8"))
js = json.load(open(ISO / "blobs/r06_docs_stage6_s6a_stage6_g0_behavior_v1.json", encoding="utf-8"))


def save_cases(mut, name):
    d = json.loads(json.dumps(cases, ensure_ascii=False))
    mut(d)
    p = W / name
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


def save_json(mut, name):
    d = json.loads(json.dumps(js, ensure_ascii=False))
    mut(d)
    p = W / name
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


def by_id(d, cid):
    return next(c for c in d["cases"] if c["case_id"] == cid)


# 1) HC-31 完全回退为旧口径（第 6 个 WM 帧 166.5 ms / m3_fires=false）
def m1(d):
    e = by_id(d, "HC-31")["expected"]
    e.update({"window_span_ms": 166.5, "m3_fires": False, "completion_index": 5,
              "later_of_applied": False, "m3_fires_count_only": True})


# 2) 只把 later_of_applied 改成 false
def m2(d):
    by_id(d, "HC-31")["expected"]["later_of_applied"] = False


# 3) 只把 m3_fires_count_only 改成 true（旧口径对照字段失去判别力）
def m3(d):
    by_id(d, "HC-31")["expected"]["m3_fires_count_only"] = True


# 4) 删除 HC-31（样例数回落到 30）
def m4(d):
    d["cases"] = [c for c in d["cases"] if c["case_id"] != "HC-31"]


# 5) 把 HC-29 的同帧结论改成取较晚（伪造 later_of）
def m5(d):
    by_id(d, "HC-29")["expected"]["later_of_applied"] = True


outs = []
outs.append(save_cases(m1, "inj_hc31_old.json"))
outs.append(save_cases(m2, "inj_hc31_later_false.json"))
outs.append(save_cases(m3, "inj_hc31_count_only_true.json"))
outs.append(save_cases(m4, "inj_hc31_removed.json"))
outs.append(save_cases(m5, "inj_hc29_later_true.json"))


# 6) JSON time_anchors.window_complete 回退为旧口径（探测该锚点是否被机器断言）
def j1(d):
    d["time_anchors"]["window_complete"] = ("窗口完成时刻 = 第 T6-S02 个 WINDOW_MATCH 结果到达"
                                            "且时长条件同时满足的那一帧的显式输入时刻。")


# 7) JSON M3.condition 去掉「取较晚」
def j2(d):
    for t in d["transitions"]:
        if t["id"] == "M3":
            t["condition"] = "连续 WINDOW_MATCH 帧数 ≥ T6-S02 且窗口时长 ≥ T6-S01；不得按 TARGET_CONTINUES 计帧"


# 8) 把 B07.condition 的旧措辞改成与 time_anchors 一致（探测修正是否安全）
def j3(d):
    for r in d["behavior_rows"]:
        if r["id"] == "B07":
            r["condition"] = ("连续 WINDOW_MATCH 帧数 ≥ T6-S02 且窗口时长 ≥ T6-S01；"
                              "完成时刻=第一个同时满足两者的帧（T6-S03 取较晚满足者）；NO_HAND 不计入")


# 9) 同时修 B07 与 B27 的旧措辞
def j4(d):
    for r in d["behavior_rows"]:
        if r["id"] == "B07":
            r["condition"] = r["condition"].replace("完成时刻=第 N 个 WINDOW_MATCH 结果到达时刻",
                                                    "完成时刻=第一个同时满足帧数与时长的帧（取较晚）")
        if r["id"] == "B27":
            r["output"] = r["output"].replace("窗口完成时刻=第 N 个 WINDOW_MATCH 结果到达时刻（实测）",
                                              "窗口完成时刻=第一个同时满足帧数与时长的帧（实测）")


outs.append(save_json(j1, "inj_anchor_old.json"))
outs.append(save_json(j2, "inj_m3_no_later.json"))
outs.append(save_json(j3, "inj_b07_fixed.json"))
outs.append(save_json(j4, "inj_b07_b27_fixed.json"))

for p in outs:
    print("生成:", p.name)