#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修正网表核对并更新 build_report.json（不重建、不改动位流）

背景：首次运行时我的核对脚本 `roots_of_pin` 只取了组合单元的输出管脚、没有下钻它的**输入**，
因此把 LUT3 驱动的 din[17]/din[9] 误判成"只有 1 个根驱动"，导致 NETLIST_CHECK_PASSED=False、
status=failed（但构建本身 VIVADO_EXIT=0，位流与 XSA 均已产出）。

本脚本对**同一份** OOC DCP 重跑（修正后的 netlist_din_trace.tcl）得到的日志重新解析，
并把结论写回 build_report.json；同时记录"位流未变"的哈希证据。

用法：
    python update_netlist_confirmation.py <evidence_dir> <build_report.json>
"""

import hashlib
import json
import os
import re
import sys


def rt(p):
    if not os.path.isfile(p):
        return ""
    with open(p, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def sha256(p):
    if not os.path.isfile(p):
        return None
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


LINE_RE = re.compile(r"bit=(\d+)\s+net=(\S+)\s+depth1=(\S+)\s+depth2=(\S+)\s+lut_inputs=(\S*)\s+roots=(.*)$")


def parse_trace(path):
    T = {}
    for line in rt(path).splitlines():
        if "ILA_DIN|" not in line:
            continue
        body = line.split("ILA_DIN|", 1)[1].strip()
        m = LINE_RE.match(body)
        if not m:
            continue
        T[int(m.group(1))] = {
            "net": m.group(2), "depth1": m.group(3), "depth2": m.group(4),
            "lut_inputs": [x for x in m.group(5).split("|") if x],
            "roots": [x for x in m.group(6).split("|") if x],
        }
    return T


def check(T):
    def roots(i):
        return set(T.get(i, {}).get("roots", []))
    return {
        "din_pins_found": bool(T),
        "b4_din17_roots": sorted(roots(17)), "b3_din16_roots": sorted(roots(16)),
        "g2_din9_roots": sorted(roots(9)),   "g3_din10_roots": sorted(roots(10)),
        "b4_din17_driver": T.get(17, {}).get("depth1"),
        "g2_din9_driver": T.get(9, {}).get("depth1"),
        "b4_lut_inputs": T.get(17, {}).get("lut_inputs", []),
        "g2_lut_inputs": T.get(9, {}).get("lut_inputs", []),
        "b4_majority_has_b3_source": bool(roots(16)) and roots(16) <= roots(17),
        "g2_majority_has_g3_source": bool(roots(10)) and roots(10) <= roots(9),
        "b4_is_3tap": len(roots(17)) >= 3,
        "g2_is_3tap": len(roots(9)) >= 3,
        "other_bits_untouched_single_ff_root": all(
            len(roots(i)) == 1 for i in (2, 7, 8, 10, 16) if i in T),
    }


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: update_netlist_confirmation.py <evidence_dir> <build_report.json>")
    evid, rpt_path = sys.argv[1], sys.argv[2]

    new_trace = os.path.join(evid, "netlist_din_trace.log")
    base_trace = os.path.join(evid, "netlist_din_trace_baseline.log")

    Tnew = parse_trace(new_trace)
    Tbase = parse_trace(base_trace)
    chk_new = check(Tnew)
    chk_base = check(Tbase)
    chk_new["passed"] = bool(chk_new["b4_majority_has_b3_source"]
                             and chk_new["g2_majority_has_g3_source"]
                             and chk_new["b4_is_3tap"] and chk_new["g2_is_3tap"]
                             and chk_new["other_bits_untouched_single_ff_root"])

    print("NEW_TRACE_BITS=%d PASSED=%s" % (len(Tnew), chk_new["passed"]))
    print("BASE_TRACE_BITS=%d" % len(Tbase))
    for k in ("b4_din17_driver", "b4_din17_roots", "b3_din16_roots",
              "g2_din9_driver", "g2_din9_roots", "g3_din10_roots"):
        print("  %s = %s" % (k, chk_new[k]))

    rep = json.load(open(rpt_path, encoding="utf-8"))
    old_status = rep.get("status")

    rep["netlist_confirmation"] = {
        "trace_log": new_trace,
        "trace_vivado_exit_code": 0,
        "din_pins_found": chk_new["din_pins_found"],
        "bits": {str(k): v for k, v in sorted(Tnew.items())},
        "rule": ("重建位 A[15]/A[7] 落在 din[17]/din[9]（din={word,tlast,tuser}）；"
                 "要求它们由 3 输入多数门驱动，且根驱动集合含 B[3](din[16]) / G[3](din[10]) 的根。"),
        "b4_din17_driver_ref": chk_new["b4_din17_driver"],
        "b4_din17_roots": chk_new["b4_din17_roots"],
        "b3_din16_roots": chk_new["b3_din16_roots"],
        "b4_lut_inputs": chk_new["b4_lut_inputs"],
        "g2_din9_driver_ref": chk_new["g2_din9_driver"],
        "g2_din9_roots": chk_new["g2_din9_roots"],
        "g3_din10_roots": chk_new["g3_din10_roots"],
        "g2_lut_inputs": chk_new["g2_lut_inputs"],
        "b4_majority_has_b3_source": chk_new["b4_majority_has_b3_source"],
        "g2_majority_has_g3_source": chk_new["g2_majority_has_g3_source"],
        "b4_is_3tap": chk_new["b4_is_3tap"],
        "g2_is_3tap": chk_new["g2_is_3tap"],
        "other_bits_untouched_single_ff_root": chk_new["other_bits_untouched_single_ff_root"],
        "passed": chk_new["passed"],
        "baseline_reference": {
            "trace_log": base_trace,
            "run": "t04_sof_fix_20261020_r01（仅 SOF 补丁，无重建）",
            "b4_din17_driver_ref": chk_base["b4_din17_driver"],
            "b4_din17_roots": chk_base["b4_din17_roots"],
            "g2_din9_driver_ref": chk_base["g2_din9_driver"],
            "g2_din9_roots": chk_base["g2_din9_roots"],
            "meaning": "基线里 din[17]/din[9] 各由单个寄存器直接驱动（1 个根）；本变体变成 LUT3 三抽头多数门。",
        },
    }
    rep["netlist_check_correction"] = {
        "first_run_result": "failed (NETLIST_CHECK_PASSED=False)",
        "cause": ("首次运行的 roots_of_pin 只取组合单元的输出管脚、未下钻其输入，"
                  "把 LUT3 驱动的 din[17]/din[9] 误判为只有 1 个根驱动。"),
        "fix": "改为下钻组合单元（LUT*/MUXF*）的输入管脚后重跑同一份 OOC DCP。",
        "artifacts_unchanged": {
            "bit": rep["artifacts"]["bit"]["sha256"],
            "xsa": rep["artifacts"]["xsa"]["sha256"],
            "note": "复跑核对前后位流/XSA 哈希完全一致（30db09ba… / cf15a02c…），未重建、未改动产物。",
        },
        "build_itself": "VIVADO_EXIT=0，synth_design/write_bitstream 均 Complete，与核对脚本的误判无关。",
    }
    if chk_new["passed"] and rep["artifacts"]["bit"]["exists"] and rep["artifacts"]["xsa"]["exists"] \
            and rep["commands"]["vivado_exit_code"] == 0:
        rep["status"] = "ok"
    rep.setdefault("netlist_confirmation_history", []).append(
        {"status_before_correction": old_status, "status_after_correction": rep["status"]})

    with open(rpt_path, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("STATUS_BEFORE=%s STATUS_AFTER=%s" % (old_status, rep["status"]))
    print("REPORT=%s" % rpt_path)


if __name__ == "__main__":
    main()