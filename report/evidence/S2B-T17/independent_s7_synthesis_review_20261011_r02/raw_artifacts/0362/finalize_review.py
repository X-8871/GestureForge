import hashlib
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 所有审查脚本的失败保留原样；手工核查只对已定位的审查器口径错误作说明。
root = Path.cwd().resolve()
out = Path(__file__).resolve().parent
e = root / "report/evidence/S2B-T17/s7_platform_20261011_r01"
checks = []

def obj(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def check(name, condition, evidence):
    checks.append({"name": name, "status": "PASS" if condition else "FAIL", "evidence": evidence})

audit = obj(out / "audit_result.json")
supplement = obj(out / "supplement_result.json")
history = obj(out / "history_compact.json")
source = (root / "report/evidence/S2B-T17/s7_source_preflight_20261011_r01/source_snapshot/vivado/s2b_inference_platform.tcl").read_text(encoding="utf-8")
body = source.split("proc ::s2b_inference_platform::run", 1)[1]
builder_count = sum(x["command"].startswith("::s2b_inference_platform::run ") for x in history)
launch_count = sum(x["command"] == "launch_runs synth_1 -jobs 1" for x in history)
check("nested products单次执行真实口径", builder_count == launch_count == 1 and body.count("capture $evidence_dir products [list ::s2b_inference_platform::products $evidence_dir] {PRODUCTS:OK}") == 1 and sum("::s2b_inference_platform::products" in x["command"] for x in history) == 0, "history id2执行run一次，冻结run函数第362行嵌套products一次；products非独立history命令。supplement初次按顶层products计数导致失败，原失败不改写。")
check("自动核验失败项关闭范围", audit["failures"] == ["checker_evidence真实退出码"] and [x["name"] for x in supplement["checks"] if x["status"] == "FAIL"] == ["history恰好单次synthesis及products"], "第一次未指定--project-root已更正，第二次history嵌套计数已由冻结Tcl与native products原件关闭。其余自动检查通过。")
for mode, expected in (("evidence", 0), ("inputs", 2)):
    native = obj(out / ("checker_" + mode + "_corrected.native.json"))
    result = obj(out / ("checker_" + mode + "_corrected.stdout.log"))
    check("最终轻量" + mode + "真实码", native["native_exit_code"] == expected and result["task_id"] == "S2B-T17", {"native_exit_code": native["native_exit_code"], "status": result["status"]})
check("时序分类真实码2", obj(out / "classifier.native.json")["native_exit_code"] == 2 and obj(out / "classifier_result.json")["status"] == "FAIL_TIMING", "仅失败分类准确性，不能据此批准时序收敛")

def matching(value, target):
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == target:
                found.append(child)
            found.extend(matching(child, target))
    elif isinstance(value, list):
        for child in value:
            found.extend(matching(child, target))
    return found

def values(found):
    result = []
    for group in found:
        if isinstance(group, list):
            result.extend(x.get("value") for x in group if isinstance(x, dict) and "value" in x)
    return result

ps = obj(out / "ps7_xci_decoded.json")
infer = obj(out / "infer_xci_decoded.json")
xci_fields = {k: values(matching(ps, k)) for k in ("PCW_FPGA0_PERIPHERAL_FREQMHZ", "PCW_USE_M_AXI_GP0", "PCW_USE_S_AXI_HP0", "PCW_S_AXI_HP0_DATA_WIDTH")}
xci_fields["PROFILE_VISIBILITY_PROVEN"] = values(matching(infer, "PROFILE_VISIBILITY_PROVEN"))
check("XCI时钟及visibility参数", xci_fields["PCW_FPGA0_PERIPHERAL_FREQMHZ"] == ["50"] and xci_fields["PCW_USE_M_AXI_GP0"] == ["1"] and xci_fields["PCW_USE_S_AXI_HP0"] == ["1"] and xci_fields["PCW_S_AXI_HP0_DATA_WIDTH"] == ["64"] and set(xci_fields["PROFILE_VISIBILITY_PROVEN"]) == {"0"}, xci_fields)
for filename, fields in (("methodology_synth.rpt", [("TIMING-16", 722)]), ("drc_synth.rpt", [("DPIP-1", 112), ("DPOP-1", 141), ("DPOP-2", 140)])):
    text = (e / filename).read_text(encoding="utf-8")
    good = all(re.search(r"\|\s*" + re.escape(k) + r"\s*\|[^\n]*\|\s*" + str(v) + r"\s*\|", text) is not None for k, v in fields)
    check("方法学/DRC原告警保留：" + filename, good, fields)
checks_pass = all(x["status"] == "PASS" for x in checks)
result = {
    "status": "PASS" if checks_pass else "CHANGES_REQUIRED",
    "scope": "S7失败证据准确性独立审查；不代表STA收敛、runtime兼容、实板部署、G3/G4/G5或阶段2B验收通过",
    "source_commit": "a5caefba952a08f365d57193696b08c0e1aff2a5",
    "manifest": {"path": "report/evidence/S2B-T17/s7_platform_20261011_r01/s7_collection_delivery_manifest_r03.json", "sha256": "63582f7312bb1cb4ac3141ca826cf00e8ef621fac43abc994c82c66e7c1fb296"},
    "collector_receipt": {"path": "report/evidence/S2B-T17/s7_platform_20261011_r01/s7_collection_execution_receipt_r03.json", "sha256": "6e742a785929159493c11f707eab6a1e3ce3d035651508fd49fcdb77b4b72977"},
    "independent_checks": checks,
    "coverage": ["336清单SHA和role，39=31+8，33RAW+6精确EOL，前后39源码同SHA，原14未改", "94native/1184705字节/5VDS，55初始原件同SHA，原生job成功/零error，18XPR RTL，六XCI", "关闭history、原ROOT日志SHA、单次products与单并发launch、wait0/241.088s无clienttimeout、builder1/products native0/capture1/emitted-8/exported2保留", "50MHz20ns时钟、12项check_timing零、两个原resetCDC命令与S6一致、WNS/TNS/hold/pulse/最差路径和资源原报告", "六PSinit逐字节对T13相同及HWH不同、pre_synth XSA无bit、methodology/DRC告警保留", "轻量evidence0/inputs2/classifier2，明确限制且未扩大结论"],
    "limitations": ["impl/postroute/bit/BOARD/G3-G5未执行或未批准；FAIL_TIMING不能部署", "PSinit相同不足以证明runtime兼容；物理接口0.1.1未冻结", "core综合161秒/2160.531MB，五个原生job最大单进程2208.859MB，进程树峰值未测", "before快照未独立记录原生码，不补造；Collector门禁argv历史转录问题有明确更正", "未再次运行重型RTL/综合、Vivado、ROSS、设备；未改Git索引/分支/STATE/生产证据", "Reviewer首次Python sandbox launcher创建失败1，已用核验路径及批准的精确范围执行恢复；审查器两次口径失败原件均保留"],
    "stop": "STOP_READONLY_REVIEW_FROZEN_ROOT_OWNS_NEXT_ACTION",
    "created_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat()
}
with (out / "review_result.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(result, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps({"status": result["status"], "checks": len(checks), "failures": [x for x in checks if x["status"] == "FAIL"]}, ensure_ascii=False))
raise SystemExit(0 if checks_pass else 2)
