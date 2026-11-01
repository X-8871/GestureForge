"""流式读取单次查询结果，输出限定的HP/cache/资源摘要。"""
from pathlib import Path
import hashlib
import json
import re

root = Path.cwd()
base = root / "report/evidence/S2B-T19/postroute_hp0_query_20261013_r01/attempt_r04"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
signals, cones, leaves = [], [], []
for line in (base / "hp0_signals.tcllist").read_text(encoding="utf-8").splitlines():
    if "SAXIHP0AWCACHE[" in line or "SAXIHP0ARCACHE[" in line:
        name = re.search(r"SAXIHP0(?:AW|AR)CACHE\[[0-3]\]", line).group(0)
        segments = line.split(" SEGMENTS ", 1)[1].split(" GROUP ", 1)[0]
        signals.append({"pin": name, "tied_global_gnd_net_observed": "<const0>" in segments,
                        "uses_gnd_named_segment": any(x in segments for x in ("/GND", "/<const0>"))})
for line in (base / "hp0_cones.tcllist").read_text(encoding="utf-8").splitlines():
    if line.startswith("CONE_BEGIN "):
        fields = line.split()
        cones.append({"signal": fields[2], "endpoint_count": int(fields[-1])})
for line in (base / "net_leaf_pins.tcllist").read_text(encoding="utf-8").splitlines():
    if line.startswith("GROUP_BEGIN "):
        if leaves and leaves[-1].get("active"):
            leaves[-1]["active"] = False
        key = line.split(" count ", 1)[0]
        if "<const0>" in key and ("AWCACHE[" in key or "ARCACHE[" in key):
            leaves.append({"group_line_sha256": hashlib.sha256(line.encode()).hexdigest(),
                           "leaf_count": int(line.rsplit(" count ", 1)[1]),
                           "cache_bits_in_group": sorted(set(re.findall(r"(?:AW|AR)CACHE\[[0-3]\]", key))),
                           "global_constant_net": "<const0>", "ground_driver_observed": False, "active": True})
    elif line.startswith("LEAF ") and leaves and leaves[-1].get("active"):
        if " OUT " in line and line.rstrip().endswith(" GND"):
            leaves[-1]["ground_driver_observed"] = True
rpt = (base / "utilization_hierarchical.rpt").read_text(encoding="utf-8", errors="replace")
summary = {"status": "QUERY_FACTS_ONLY_NOT_PHYSICAL_ACCEPTANCE",
    "source_commit": "c8742858fbb23331763358775daa44dafb95db94",
    "input_dcp_sha256": "db2aaf706c99121eada307fec80b4d69b362f1232ff17fcf65f4dd5c0015ad83",
    "query_result": {"path": str(base / "result.tcldict"), "sha256": sha(base / "result.tcldict"),
                     "text": (base / "result.tcldict").read_text(encoding="utf-8")[-200:]},
    "postroute_report_sha256": sha(base / "utilization_hierarchical.rpt"),
    "cache_pins": signals, "cache_leaf_groups": leaves, "selected_handshake_cone_counts": cones,
    "observations": ["Postroute fixed visibility0 DCP was loaded read-only; source/dcp identity is exact.",
                     "Unconnected outputs were only documented auxiliary HP0 reset/count outputs; required transaction pins were netted.",
                     "All eight PS7 HP0 ARCACHE/AWCACHE bits belong to one common net group rooted at infer/<const0>; its leaf list contains an OUT GND primitive. This establishes the current DCP tie to zero, not PS7 behavioral cache/coherency semantics.",
                     "Static request/response endpoint cones reach retained adapter/control state; connectivity does not prove runtime AXI transaction completion or DDR coherency.",
                     "No final bounded query covered FCLK clock/reset source or core start-to-output route; these remain unmeasured."],
    "selected_report_lines": [line for line in rpt.splitlines() if any(key in line for key in ("Slice LUTs", "Slice Registers", "DSPs", "Block RAM Tile", "DSP48"))][:80],
    "execution_receipt_sha256": sha(base / "execution_receipt.json"),
    "tool_call_count": None, "wall_seconds": 36.285170899998775, "sampled_peak_process_tree_rss_bytes": 1876975616,
    "limitations": ["Tcl/launcher native0 and QUERY_COMPLETED mean bounded read-only query succeeded only.",
                    "Selected GND net group can include entire common fanout; cache bits appear tied to constant 0 but this report alone is not PS7 behavioral proof.",
                    "FCLK/core-start/output path and complete cache semantics not established; no visibility1 resynthesis or board operation."]}
summary["cache_leaf_groups"] = [{key: value for key, value in row.items() if key != "active"} for row in leaves]
summary["status"] = "QUERY_FACTS_PARTIAL_NOT_PHYSICAL_ACCEPTANCE"
target = root / "report/evidence/S2B-T19/postroute_hp0_query_20261013_r01/query_summary_r03.json"
assert not target.exists()
target.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"summary_sha256": sha(target), "cache_pin_count": len(signals),
                  "cache_leaf_group_count": len(leaves), "cone_count": len(cones)}, ensure_ascii=False))
