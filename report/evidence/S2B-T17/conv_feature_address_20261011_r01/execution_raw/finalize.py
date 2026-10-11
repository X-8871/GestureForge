#!/usr/bin/env python3
"""只封存S10真实功能运行和标准六角色清单；失败/未执行不伪报通过。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
WORK=Path(__file__).resolve().parent
BASE="3f24c94564d10103aaa00db07356f666b085f687"
STAGES={"feature":"conv_feature_address_20261011_r01","output":"conv_output_address_20261011_r04",
        "boundary":"conv_feature_address_boundary_20261011_r01","layer0":"conv_feature_address_layer0_20261011_r01",
        "backend":"conv_feature_address_trace_20261011_r01","geometry":"conv_feature_address_geometry_20261011_r01"}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding="utf-8"))


def write(path,value):
    """新原件一次写入，禁止覆盖旧RunId。"""
    with path.open("x",encoding="utf-8",newline="\n") as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write("\n")


def copy_file(source,target):
    """精确目标按原字节复制，禁止覆盖。"""
    target.parent.mkdir(parents=True,exist_ok=True)
    assert not target.exists();shutil.copyfile(source,target)


def diagnostic(reports):
    """受控驱动逐信号限定；新生产异常诊断不得混入豁免。"""
    direct=[]
    feature_expected={"state","feature_scan_channel","input_height_latched","input_width_latched","tile_start_y","stride_y_latched","feature_scan_y","pad_top_latched","tile_start_x","stride_x_latched","feature_scan_x","pad_left_latched","input_base_latched","patch_height","patch_width","feature_scan_index","patch_byte_count"}
    output_expected={"output_group_base","output_lane_index","output_height_latched","output_width_latched","tile_start_y","output_point_scan_y","tile_start_x","output_point_scan_x","output_base_latched","output_channels_latched","group_lane_count","output_point_index","tile_point_count"}
    for stage,expected in (("feature",feature_expected),("output",output_expected)):
        evidence=ROOT/"report/evidence/S2B-T17"/STAGES[stage]
        tbpath=evidence/("tb_s2b_conv_"+("feature" if stage=="feature" else "output")+"_address.sv")
        tb=tbpath.read_text(encoding="utf-8")
        assert "logic clk=0;" in tb and not re.search(r"always\s*#|clk\s*<=|clk\s*=\s*~|\bforce\b",tb)
        logpath=ROOT/next(r["log"] for r in reports[stage]["runs"] if r["name"]=="compile")
        log=logpath.read_text(encoding="utf-8");records=[]
        for m in re.finditer(r"%Warning-MULTIDRIVEN: ([^\r\n]+)",log):
            item=re.search(r"^(.+?):(\d+):(\d+):.*?: '([^']+)'",m[1]);assert item,m[1]
            source,line,col,signal=item.groups();assert signal in expected
            instance="u_old" if "s9_conv_tile_engine_original.sv" in source else "u_dut"
            assert instance=="u_old" or "s2b_conv_tile_engine.sv" in source
            target=f"{instance}.{signal}=" if signal=="state" else f"{instance}.{signal}=v_{signal};"
            drives=[i+1 for i,text in enumerate(tb.splitlines()) if target in text];assert len(drives)==1,(stage,signal,drives)
            stop=log.find("%Warning-",m.end());block=log[m.start():stop if stop>=0 else len(log)]
            records.append({"module_instance":instance,"signal":signal,"production_source":source,"source_line":int(line),"source_column":int(col),"testbench_line":drives[0],"compile_log_line":log[:m.start()].count("\n")+1,"raw_diagnostic":block.strip()})
        assert len(records)==2*len(expected) and {(r["module_instance"],r["signal"]) for r in records}=={(i,n) for i in ("u_old","u_dut") for n in expected}
        assert not re.search(r"%Warning-(?:LATCH|UNOPTFLAT):",log)
        direct.append({"stage":stage,"scope":"TB主动驱动的旧新完整引擎内部组合依赖，clk恒0/FF未执行；feature包含受控enum状态。不是公开START覆盖。","tb":{"path":tbpath.relative_to(ROOT).as_posix(),"sha256":sha(tbpath)},"log":{"path":logpath.relative_to(ROOT).as_posix(),"sha256":sha(logpath)},"records":records})
    public=[]
    for stage in ("boundary","layer0","geometry"):
        for run in reports[stage]["runs"]:
            if "compile" not in run["name"]:continue
            path=ROOT/run["log"];assert not re.search(r"%Warning-(?:LATCH|UNOPTFLAT|MULTIDRIVEN):",path.read_text(encoding="utf-8"))
            public.append({"stage":stage,"path":run["log"],"sha256":sha(path),"three_abnormal_diagnostics":[]})
    backend=ROOT/next(r["log"] for r in reports["backend"]["runs"] if r["name"]=="compile")
    prior=ROOT/"report/evidence/S2B-T17/conv_output_address_trace_20261011_r01/compile.log"
    headers=re.findall(r"%Warning-MULTIDRIVEN: [^\r\n]+",backend.read_text(encoding="utf-8"))
    assert headers==re.findall(r"%Warning-MULTIDRIVEN: [^\r\n]+",prior.read_text(encoding="utf-8")) and len(headers)==16
    assert not re.search(r"%Warning-(?:LATCH|UNOPTFLAT):",backend.read_text(encoding="utf-8"))
    tb=ROOT/"report/evidence/S2B-T17"/STAGES["backend"]/"tb_s2b_backend_coordinates.sv"
    prior_tb=prior.parent/"tb_s2b_backend_coordinates.sv";assert sha(tb)==sha(prior_tb)
    return {"direct_scopes":direct,"public_compile_checks":public,"backend_inherited":{"count":16,"headers":headers,"prior_log":{"path":prior.relative_to(ROOT).as_posix(),"sha256":sha(prior)},"actual_log":{"path":backend.relative_to(ROOT).as_posix(),"sha256":sha(backend)},"testbench_sha256":sha(tb),"prior_testbench_sha256":sha(prior_tb),"scope":"既有relational段force/release/初态注入；完整trace和公开入口释放注入。仅承认同S9既有TB诊断，未全局豁免新增生产。"}}


def main():
    """全部回归结束后固定来源；不修改已测代码或Git。"""
    started=time.monotonic()
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()==BASE
    main=ROOT/"report/evidence/S2B-T17"/STAGES["feature"]
    spec=importlib.util.spec_from_file_location("s10_checker",ROOT/"verification/check_s2b_inference_platform.py");checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    static=checker.check_static(ROOT)
    upstream_path=ROOT/"report/evidence/S2B-T17/conv_output_address_20261011_r03/source_freeze.json"
    assert sha(upstream_path)=="d32a4017d8bb51632c7437c484db25ec34d77b42a93a6404c5c14c620f0377a9"
    upstream=read(upstream_path)
    paths=list(dict.fromkeys([x["path"] for x in upstream["source_files"]]+list(static)+["verification/test_s2b_conv_feature_address_rtl.py"]))
    assert len(paths)==43 and len(static)==33
    hashes={p:sha(ROOT/p) for p in paths}
    reports={s:read(ROOT/"report/evidence/S2B-T17"/r/"validation.json") for s,r in STAGES.items()}
    natives={s:read(WORK/(s+"_native.json")) for s in STAGES}
    for stage,report in reports.items():
        assert report["status"].startswith("PASS") and natives[stage]["native_exit_code"]==0 and not natives[stage]["stop_reason"]
        assert report["source_sha256_pre"]==report["source_sha256_post"]
        assert all(sha(ROOT/p)==h for p,h in report["source_sha256_post"].items())
        assert natives[stage]["peak_tree_rss_bytes"]<=1073741824
        assert sum(p.stat().st_size for p in (WORK/STAGES[stage]).rglob("*") if p.is_file())<=314572800
    assert len(reports["feature"]["checker_negatives"])==26 and len(reports["feature"]["feature_mutants"])==8
    assert len(reports["output"]["offset_mutants"])==8
    frozen={p:sha(ROOT/p) for p in checker.FROZEN_CORE_SHA256};assert frozen==upstream["frozen14"]==checker.FROZEN_CORE_SHA256
    write(main/"diagnostic_scope.json",diagnostic(reports))
    snapshot=main/"final_source_snapshot";snapshot.mkdir()
    for p in paths:copy_file(ROOT/p,snapshot/p)
    modified=["src/s2b_conv_tile_engine.sv","verification/check_s2b_inference_platform.py","board/s2b_inference_platform.json","board/s2b_inference_platform.md","vivado/s2b_inference_platform.tcl","verification/test_s2b_geometry_specialization_rtl.py","verification/test_s2b_backend_coordinates_rtl.py","verification/test_s2b_conv_validation_rtl.py","verification/test_s2b_conv_output_address_rtl.py"]
    diff=subprocess.check_output(["git","diff","--no-ext-diff","--no-color",BASE,"--",*modified],cwd=ROOT)
    added=subprocess.run(["git","diff","--no-index","--no-ext-diff","--no-color","--","NUL","verification/test_s2b_conv_feature_address_rtl.py"],cwd=ROOT,capture_output=True);assert added.returncode==1
    with (main/"source_diff.patch").open("xb") as f:f.write(diff+added.stdout)
    g0=ROOT/"tmp/2B/S2B-T17/s10_g0_diagnosis_20261011_r01"
    for name in ("math_r02/result.json","math_r02/native_capture.json","math_r02/math_diagnosis.py","math_r02/stdout.log","math_r02/stderr.log","manual_label_correction.json","a2_r01/result.json","a2_r01/native_capture.json","a2_r01/probe.py","a2_r01/stdout.log","a2_r01/stderr.log"):
        copy_file(g0/name,main/"g0_math_raw"/name)
    runtime=main/"execution_raw";runtime.mkdir()
    for path in WORK.iterdir():
        if path.is_file() and path.suffix in (".py",".json",".log") and not path.name.startswith("finalize_"):
            copy_file(path,runtime/path.name)
    freeze={"schema_version":1,"source_commit":BASE,"profile":"s2b-inference-platform/0.1.10","active_rtl_sources":read(ROOT/"board/s2b_inference_platform.json")["rtl_sources"],"upstream_s9_freeze":{"path":upstream_path.relative_to(ROOT).as_posix(),"sha256":sha(upstream_path)},"source_files":[{"path":p,"sha256":h,"bytes":(ROOT/p).stat().st_size,"snapshot":(snapshot/p).relative_to(ROOT).as_posix()} for p,h in hashes.items()],"frozen14":frozen,"tested_source_drift":{},"source_diff_sha256":sha(main/"source_diff.patch"),"modified_files":{p:hashes[p] for p in modified+["verification/test_s2b_conv_feature_address_rtl.py"]}}
    write(main/"source_freeze.json",freeze)
    limits=["功能G1与G2/真实STA/实现/G3分别判断，S9真实WNS−4.527ns仍FAIL，本轮不声称时序改善。","feature完整signed64坐标与bounds不动；row低32仅在原bounds内消费，channel/base仍模64，未消费offset/address默认0及全部FF/状态/周期/owner/错误优先保持。","direct feature34/output26受控TB驱动警告逐条绑定，clk恒0/FF不执行；不是公开START轨迹。backend16既有诊断与S9日志/TB逐字相同。","layer0真实完整CONV数值/周期与独立CPU；backend15非CONV完整trace中CONV为共享控制stub，未执行新109全网或21CONV全数值。","原14/50MHz/物理0.1.1/visibility0/模型/109/100黄金/1000实板指标保持。"]
    summary={"status":"PASS_S10_G1_FUNCTIONAL_ONLY","source_commit":BASE,"profile":"s2b-inference-platform/0.1.10","source_closure_count":43,"static_source_count":33,"extra_source_count":10,"active_rtl_count":18,"derived_rtl_count":8,"frozen_active_rtl_count":6,"outer_rtl_count":4,"feature":reports["feature"]["actual_coverage"],"output":reports["output"]["actual_coverage"],"boundary":reports["boundary"]["actual_coverage"],"layer0":reports["layer0"]["actual_coverage"],"cpu_layer0":reports["layer0"]["independent_cpu_layer0"],"backend":reports["backend"]["simulation_counts"],"public_entries":reports["backend"]["public_entries"],"geometry":reports["geometry"]["simulation_counts"],"platform_negatives":26,"feature_mutants":8,"output_mutants":8,"execution":[{"stage":s,"run_id":STAGES[s],"native_exit_code":n["native_exit_code"],"seconds":n["elapsed_seconds"],"peak_tree_rss_bytes":n["peak_tree_rss_bytes"],"runs":reports[s]["runs"]} for s,n in natives.items()],"independent_review":"NOT_RUN","sta":"NOT_RUN","implementation":"NOT_RUN","g3":"NOT_RUN","tool_calls":"本包保存全部原生runner及子命令；完整会话工具调用量未测。","limitations":limits}
    write(main/"g1_summary.json",summary)
    upstream_manifest=ROOT/"report/evidence/S2B-T17/conv_output_address_20261011_r03/delivery_manifest_r02.json"
    interfaces=read(upstream_manifest)["interfaces"]
    assert all(sha(ROOT/i["path"])==i["sha256"] for i in interfaces)
    manifests={}
    for stage,runid in STAGES.items():
        evidence=ROOT/"report/evidence/S2B-T17"/runid
        files={p:{"path":p,"sha256":h,"role":"source"} for p,h in hashes.items()}
        external=[upstream_path,upstream_manifest,main/"source_freeze.json",main/"g1_summary.json",ROOT/"report/evidence/S2B-T17/s9_platform_20261011_r01/timing_worst_synth.rpt"]
        for path in [*sorted(evidence.rglob("*")),*external]:
            if not path.is_file() or path.name=="delivery_manifest.json":continue
            relative=path.relative_to(ROOT).as_posix()
            own=path.is_relative_to(evidence)
            role="input" if not own or path.name=="address_vectors.txt" else "log" if path.suffix==".log" else "source" if path.suffix in (".py",".sv",".tcl",".md") else "diagnostic" if path.suffix==".patch" else "result"
            assert not any(part in (".runs",".gen",".srcs",".cache") for part in path.parts)
            files[relative]={"path":relative,"sha256":sha(path),"role":role}
        checks=[{"name":"真实原生runner","status":"PASS","command":natives[stage]["command"],"exit_code":natives[stage]["native_exit_code"],"reason":"实际执行原生结果，未用host归一替代native；1GiB/300MiB外层守卫。"}]
        for record in reports[stage]["runs"]:checks.append({"name":record["name"],"status":"PASS","command":subprocess.list2cmdline(record["command"]),"exit_code":record["exit_code"],"reason":"实际compile/simulation原生命令与日志。"})
        if stage=="feature":checks.append({"name":"26平台负向及8feature语义mutants","status":"PASS","command":natives[stage]["command"],"exit_code":natives[stage]["native_exit_code"],"reason":"此真实runner内执行，validation保存每一真实拒绝原因；并非自报审查0。"})
        checks.extend({"name":name,"status":"NOT_RUN","command":None,"exit_code":None,"reason":reason} for name,reason in (("独立G2","ROOT随后固定差异独审。"),("S10真实STA与实现","仅功能G1，S9实际STA仍FAIL。"),("G3实板","本轮无设备操作。")))
        manifest={"schema_version":1,"stage":"2B","task_id":"S2B-T17","run_id":runid,"source_commit":BASE,"evidence_dir":evidence.relative_to(ROOT).as_posix(),"interfaces":interfaces,"tool_versions":reports[stage]["tool_versions"],"files":list(files.values()),"checks":checks,"limitations":limits}
        target=evidence/"delivery_manifest.json";write(target,manifest);manifests[stage]={"path":target.relative_to(ROOT).as_posix(),"sha256":sha(target)}
    captures=[]
    for stage,item in manifests.items():
        for mode in ("evidence","inputs"):
            argv=[sys.executable,"-X","utf8","-B",str(ROOT/"verification/check_stage_delivery.py"),"--project-root",str(ROOT),"--mode",mode,"--manifest",str(ROOT/item["path"])]
            done=subprocess.run(argv,cwd=ROOT,capture_output=True)
            record={"stage":stage,"mode":mode,"command":subprocess.list2cmdline(argv),"argv":argv,"native_exit_code":done.returncode,"stdout":done.stdout.decode("utf-8"),"stderr":done.stderr.decode("utf-8")}
            write(WORK/(stage+"_"+mode+"_native.json"),record);assert done.returncode==(0 if mode=="evidence" else 2),record
            captures.append({"stage":stage,"mode":mode,"native_exit_code":done.returncode});print(json.dumps(captures[-1]),flush=True)
    assert all(sha(ROOT/p)==h for p,h in hashes.items())
    final={"status":"STOP_READY_G1_ONLY","source_commit":BASE,"source_freeze_sha256":sha(main/"source_freeze.json"),"diff_sha256":sha(main/"source_diff.patch"),"g1_summary_sha256":sha(main/"g1_summary.json"),"modified":freeze["modified_files"],"manifests":manifests,"checks":captures,"peak_tree_rss_bytes":max(n["peak_tree_rss_bytes"] for n in natives.values()),"elapsed_seconds":time.monotonic()-started}
    write(WORK/"final_package_receipt.json",final);print(json.dumps(final,ensure_ascii=False),flush=True)


if __name__=="__main__":main()
