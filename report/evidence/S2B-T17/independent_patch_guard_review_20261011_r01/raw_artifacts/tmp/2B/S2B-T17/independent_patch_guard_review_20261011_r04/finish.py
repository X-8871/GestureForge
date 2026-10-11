#!/usr/bin/env python3
"""补核编译快照与黄金范围，并冻结不含编译缓存的精确审查原件列表。"""
from pathlib import Path
import hashlib
import json
import re
import sys
import psutil
root=Path(r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition")
work=Path(__file__).resolve().parent
g1=root/"report/evidence/S2B-T17/patch_guard_20261011_r07"
def read(p):
    assert p.is_file(),str(p)
    return json.loads(p.read_text(encoding="utf-8"))
def sha(p):
    assert p.is_file(),str(p)
    h=hashlib.sha256()
    with p.open("rb") as f:
        while value:=f.read(1048576):h.update(value)
    return h.hexdigest()
def save(name,value):
    path=work/name
    assert not path.exists(),str(path)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
freeze=read(g1/"source_freeze.json")
bindings=freeze["source_sha256"]
verified=[]
for path,digest in bindings.items():assert sha(root/path)==digest,path
for i in range(2,7):
    directory=g1/("raw/patch_guard_20261011_r"+str(i).zfill(2))
    report=read(directory/"validation.json")
    pre=report["source_sha256_pre"];post=report["source_sha256_post"]
    assert pre==post,(i,"执行期间源码变化")
    for path,digest in pre.items():
        if path in bindings:assert digest==bindings[path],(i,path)
    for snapshot in [p for p in (g1/("compiled_snapshot/patch_guard_20261011_r"+str(i).zfill(2))).iterdir() if p.is_file()]:
        source="src/"+snapshot.name
        if source in bindings:
            assert sha(snapshot)==bindings[source],(i,source)
            verified.append({"run":i,"source":source,"snapshot_sha256":sha(snapshot)})
    # 非卷积backend测试使用已声明的控制stub，另外两份源按原描述符路线绑定。
    if i==6:
        assert (directory/"convolution_stub.sv").is_file()
        log=next(r for r in report["runs"] if r["name"]=="simulation")
        actual_trace=re.findall(r"TRACE layer=(\d+) op=(\d+) outputs=(\d+) requests=(\d+) cycles=(\d+) digest=([0-9a-f]+)",(root/log["log"]).read_text(encoding="utf-8"))
        old_trace=re.findall(r"TRACE layer=(\d+) op=(\d+) outputs=(\d+) requests=(\d+) cycles=(\d+) digest=([0-9a-f]+)",(root/"report/evidence/S2B-T17/conv_validation_20261011_r13/simulation.log").read_text(encoding="utf-8"))
        assert len(actual_trace)==15 and actual_trace==old_trace
gold=(g1/"raw/patch_guard_20261011_r03/cpu_layer0_expected.bin").read_bytes()
assert len(gold)==1384448 and len(set(gold))>16
nonzero=sum(v!=0 for v in gold)
fixture=root/"report/evidence/S2A-T01/tiny416_model_manifest.json"
assert sha(fixture)=="9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
manifest=read(g1/"delivery_manifest_r04.json")
assert (g1/"delivery_manifest_r04.json").read_text(encoding="utf-8").count("\ufffd")==0
assert any(item["frozen"] is False for item in manifest["interfaces"])
assert any(item["status"]=="NOT_RUN" and "S5_50MHz" in item["name"] for item in manifest["checks"])
assert any(item["status"]=="NOT_RUN" and "G3" in item["name"] for item in manifest["checks"])
tools=[{"pid":p.pid,"name":p.info["name"]} for p in psutil.process_iter(["name"]) if p.info["name"] and re.search(r"^(verilator_bin\.exe|cc1plus\.exe|xsim\.exe|Vtb.*\.exe)$",p.info["name"],re.I)]
assert not tools
supplement={"status":"PASS","compile_snapshot_matches_freeze":verified,"g1_pre_post_source_bindings_identical":True,"frozen_source_count":len(bindings),"nonconv_15_traces_equal_S4":True,"backend_conv_is_control_stub":True,"gold_nonzero_bytes":nonzero,"gold_distinct_raw_bytes":len(set(gold)),"model_manifest_streaming_sha256":sha(fixture),"current_manifest_U_FFFD_count":0,"remaining_heavy":tools,"packaging_modes":"未调用stage checker，因其会调用Git而本审查禁用Git；独立流式逐项核对344绑定，并核对原生包装输出及失败/未冻结/NOT_RUN字段。","preflight_failures":{"r01":"结果字段误读，无RTL；宿主1但Python原生未观测","r02":"精确r15向量不存在，依据已存r06路径/SHA修正；Python原生2，无RTL","r03":"资源正则错误包含vivado-mcp服务；Python原生2，无RTL；fresh CIM与r04精确正则确认仅idle root23188"},"proof":{"C_KH_KW_upper":4608,"H_W_19bit_upper":463353,"P32_upper":4294836225,"Q29_upper":301985280,"weight_group_upper":36864,"shape_guard":"原64位无符号模语义保持","priority":"首参数/层索引覆盖→BAD_LENGTH→range/MQ/patch→shape","tail_safety":"通过完整patch容量判据后，每个正tile尾部patch不超过fulltile；后续FF与S4逐字符相同且窄判据不写任何状态。"}}
save("supplemental_checks.json",supplement)
receipt=read(work/"review_receipt.json")
assert receipt["status"]=="PASS_G2_ONLY"
receipt.update(supplemental_checks_sha256=sha(work/"supplemental_checks.json"),blocking_findings=[],final_status="PASS_G2_ONLY",source_baseline_task="71983d70cbfcacbbf90dfa032568f8c68a5c0162",source_baseline_S4="f96d3e225fd6d92fd33c0407e20c9585c997c870",later_root_HEAD_reported="a912cae86a71dfa8928461efff07b9842768d4a7",later_HEAD_scope="总控仅提交S4 evidence/STATE/attrs；本审查不读取Git，仍以冻结38实际源码SHA判断。",stage_checker_not_invoked_due_Git_boundary=True)
save("final_review_receipt.json",receipt)
raw=[]
for i in range(1,5):
    directory=work.parent/("independent_patch_guard_review_20261011_r"+str(i).zfill(2))
    raw += [p for p in directory.iterdir() if p.is_file()]
    if (directory/"source").is_dir():raw += list((directory/"source").iterdir())
entries=[{"path":p.relative_to(root).as_posix(),"sha256":sha(p),"role":"independent_review_raw"} for p in raw]
final={"schema_version":1,"task_id":"S2B-T17-S5","status":"PASS_G2_ONLY","files":entries,"bytes_by_path":{p.relative_to(root).as_posix():p.stat().st_size for p in raw},"manifest_self":"final_raw_delivery_manifest.json自身作为一个额外原件由总控计入；本列表含所有r01-r04顶层及source，明确排除obj_dir缓存。"}
save("final_raw_delivery_manifest.json",final)
print(json.dumps({"status":"PASS_G2_ONLY","receipt_sha256":sha(work/"final_review_receipt.json"),"raw_manifest_sha256":sha(work/"final_raw_delivery_manifest.json"),"raw_manifest_bytes":(work/"final_raw_delivery_manifest.json").stat().st_size,"raw_files":len(entries),"total_raw_bytes_without_manifest":sum(p.stat().st_size for p in raw),"compiled_snapshots":len(verified),"nonzero_layer0":nonzero,"remaining_heavy":tools},ensure_ascii=False))
