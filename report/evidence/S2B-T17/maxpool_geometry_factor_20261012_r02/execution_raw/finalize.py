"""封存S11真实功能原件和标准六角色清单，包装通过不代表STA或G2。"""
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
BASE="4288795b1e8c75b98cbbeb69ac33709172e97c66"
STAGES={"guard":"maxpool_geometry_factor_20261012_r02","backend":"maxpool_geometry_factor_trace_20261012_r01"}
MODIFIED=["src/s2b_maxpool_geometry.sv","verification/check_s2b_inference_platform.py","board/s2b_inference_platform.json","board/s2b_inference_platform.md","vivado/s2b_inference_platform.tcl","verification/test_s2b_maxpool_address_guard_rtl.py","verification/test_s2b_geometry_specialization_rtl.py","verification/test_s2b_backend_coordinates_rtl.py"]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding="utf-8"))

def write(path,value):
    """新文件只写一次，不覆盖历史。"""
    with path.open("x",encoding="utf-8",newline="\n") as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write("\n")

def copy(source,target):
    """原字节复制到精确新目标。"""
    target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();shutil.copyfile(source,target)

def main():
    """真实全部运行结束后冻结源和诊断；不修改被测代码或Git。"""
    started=time.monotonic();assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()==BASE
    main=ROOT/"report/evidence/S2B-T17"/STAGES["guard"]
    checker_path=ROOT/"verification/check_s2b_inference_platform.py"
    spec=importlib.util.spec_from_file_location("s11_checker",checker_path);checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    static=checker.check_static(ROOT)
    upstream_path=ROOT/"report/evidence/S2B-T17/conv_feature_address_20261011_r01/source_freeze.json"
    assert sha(upstream_path)=="8fcbb7313ced5b8046e4ff74bd274ed4b7d47c3d00a776bc50a4b0d73bb96360"
    paths=[row["path"] for row in read(upstream_path)["source_files"]]
    assert len(paths)==43 and len(static)==33 and set(static)<=set(paths)
    hashes={p:sha(ROOT/p) for p in paths};assert hashes==read(WORK/"initial_source.json")["source_sha256_pre"]
    frozen={p:sha(ROOT/p) for p in checker.FROZEN_CORE_SHA256};assert frozen==checker.FROZEN_CORE_SHA256==read(upstream_path)["frozen14"]
    assert hashes["src/s2b_maxpool_engine.sv"]=="8908ec272fa47db816f110ccf7483d359733bf0e4f1dbea4b29d2b543af18f70"
    reports={s:read(ROOT/"report/evidence/S2B-T17"/run/"validation.json") for s,run in STAGES.items()}
    natives={s:read(WORK/(s+"_native.json")) for s in STAGES}
    for s,r in reports.items():
        assert r["status"].startswith("PASS") and natives[s]["native_exit_code"]==0 and not natives[s]["stop_reason"]
        assert r["source_sha256_pre"]==r["source_sha256_post"]
        assert all(hashes[p]==h for p,h in r["source_sha256_post"].items())
        assert natives[s]["peak_tree_rss_bytes"]<=1073741824
        cache=WORK/("rtl_run" if s=="guard" else STAGES[s])
        assert sum(p.stat().st_size for p in cache.rglob("*") if p.is_file())<=(671088640 if s=="guard" else 314572800)
    guard=reports["guard"];assert guard["geometry_coverage"]["vectors"]==82591
    assert len(guard["checker_public_negatives"])==26 and len(guard["checker_semantic_mutants"])==12
    assert guard["engine_simulation_counts"]["pool"]==19645 and guard["engine_simulation_counts"]["upsample"]==3456
    diagnostics=[]
    for run in guard["runs"]:
        if "compile" in run["name"]:
            path=ROOT/run["log"];assert not re.search(r"%Warning-(?:LATCH|UNOPTFLAT|MULTIDRIVEN):",path.read_text(encoding="utf-8"))
            diagnostics.append({"path":run["log"],"sha256":sha(path),"new_production_abnormal_diagnostics":[]})
    log=ROOT/next(r["log"] for r in reports["backend"]["runs"] if r["name"]=="compile")
    prior=ROOT/"report/evidence/S2B-T17/conv_feature_address_trace_20261011_r01/compile.log"
    headers=re.findall(r"%Warning-MULTIDRIVEN: [^\r\n]+",log.read_text(encoding="utf-8"))
    assert headers==re.findall(r"%Warning-MULTIDRIVEN: [^\r\n]+",prior.read_text(encoding="utf-8")) and len(headers)==16
    assert not re.search(r"%Warning-(?:LATCH|UNOPTFLAT):",log.read_text(encoding="utf-8"))
    tb=log.parent/"tb_s2b_backend_coordinates.sv";prior_tb=prior.parent/tb.name;assert sha(tb)==sha(prior_tb)
    write(main/"diagnostic_scope.json",{"geometry_engine_compile":diagnostics,"backend_inherited":{"count":16,"headers":headers,"prior_log":{"path":prior.relative_to(ROOT).as_posix(),"sha256":sha(prior)},"actual_log":{"path":log.relative_to(ROOT).as_posix(),"sha256":sha(log)},"testbench_sha256":sha(tb),"prior_testbench_sha256":sha(prior_tb),"scope":"仅既有TB关系检查force/release/初态注入，完整trace/公开入口释放注入；逐条同S10，不声称零警告、不豁免新增生产异常。"}})
    snapshot=main/"final_source_snapshot";snapshot.mkdir()
    for p in paths:copy(ROOT/p,snapshot/p)
    diff=subprocess.check_output(["git","diff","--no-ext-diff","--no-color",BASE,"--",*MODIFIED],cwd=ROOT)
    with (main/"source_diff.patch").open("xb") as f:f.write(diff)
    failure=main/"r01_failed_raw";failure.mkdir()
    old=WORK.parent/"maxpool_geometry_factor_20261012_r01"
    for name in ("guard_native.json","guard_stderr.log","guard_stdout.log","guard_adapter.json","initial_source.json","run_stage.py"):
        copy(old/name,failure/name)
    old_evidence=ROOT/"report/evidence/S2B-T17/maxpool_geometry_factor_20261012_r01"
    for name in ("geometry_compile.log","geometry_simulation.log","engine_compile.log"):
        copy(old_evidence/name,failure/name)
    old_md=old_evidence/"source_snapshot/board/s2b_inference_platform.md"
    assert sha(old_md)==read(old/"initial_source.json")["source_sha256_pre"]["board/s2b_inference_platform.md"]
    copy(old_md,failure/"source_metadata/board/s2b_inference_platform.md")
    copy(WORK/"budget_repair_receipt.json",failure/"budget_repair_receipt.json")
    runtime=main/"execution_raw";runtime.mkdir()
    for path in WORK.iterdir():
        if path.is_file() and path.suffix in (".py",".json",".log") and not path.name.startswith("finalize_"):
            copy(path,runtime/path.name)
    freeze={"schema_version":1,"source_commit":BASE,"profile":"s2b-inference-platform/0.1.11","active_rtl_sources":read(ROOT/"board/s2b_inference_platform.json")["rtl_sources"],"upstream_s10_freeze":{"path":upstream_path.relative_to(ROOT).as_posix(),"sha256":sha(upstream_path)},"source_files":[{"path":p,"sha256":h,"bytes":(ROOT/p).stat().st_size,"snapshot":(snapshot/p).relative_to(ROOT).as_posix()} for p,h in hashes.items()],"frozen14":frozen,"engine_raw_unchanged":hashes["src/s2b_maxpool_engine.sv"],"tested_source_drift":{},"source_diff_sha256":sha(main/"source_diff.patch"),"modified_files":{p:hashes[p] for p in MODIFIED}}
    write(main/"source_freeze.json",freeze)
    limits=["功能G1与独立G2/STA/实板分别判断；S10真实WNS−4.405ns仍FAIL且resource coverage BLOCKED，未继承通过。本轮没有Vivado/硬件。","原14/engine原字节、全部端口/FF/FSM/错误优先/周期、50MHz/physical0.1.1/visibility0及正式109/100gold/1000实板指标保持。","fullfield黄金仍旧无限精度嵌套地址；保留全部82586旧刺激并增加5项手算，seed0x581011。有限样本不是U32穷举。","几何和公开POOL/UP包含全部状态abort/reset、backpressure/RESULT hold；backend15非CONV完整trace/38控制stub/12负向；CONV数值/层0/新109整网未重跑。","backend16既有TB MULTIDRIVEN逐条同S10，非新生产警告；本轮geometry/engine LATCH/UNOPTFLAT/MULTIDRIVEN为零。","峰RSS是0.2秒离散采样树峰，非连续绝对峰；单job/thread1，外层1GiB/guard合计640MiB、backend300MiB预算。"]
    summary={"status":"PASS_S11_G1_FUNCTIONAL_ONLY","source_commit":BASE,"profile":"s2b-inference-platform/0.1.11","source_closure_count":43,"static_source_count":33,"extra_source_count":10,"active_rtl_count":18,"derived_rtl_count":8,"frozen_active_rtl_count":6,"outer_rtl_count":4,"geometry_fullfield":guard["geometry_coverage"],"geometry_public":guard["engine_simulation_counts"],"platform_negatives":26,"semantic_mutants":12,"backend":reports["backend"]["simulation_counts"],"public_entries":reports["backend"]["public_entries"],"execution":[{"stage":s,"run_id":STAGES[s],"native_exit_code":n["native_exit_code"],"seconds":n["elapsed_seconds"],"peak_tree_rss_bytes":n["peak_tree_rss_bytes"],"runs":reports[s]["runs"]} for s,n in natives.items()],"independent_review":"NOT_RUN","sta":"NOT_RUN","implementation":"NOT_RUN","g3":"NOT_RUN","r01_failure":{"native_exit_code":1,"reason":"旧300MiB合计缓存守卫真实失败，非设计失败，保留原判定。","cache_bytes_at_diagnosis":438587316,"geometry_vectors_pass":82591,"new_budget_authorization":"ROOT明确仅S11 guard两个独立编译合计640MiB，RSS1GiB与backend300MiB不变。"},"limitations":limits}
    write(main/"g1_summary.json",summary)
    upstream_manifest=ROOT/"report/evidence/S2B-T17/conv_feature_address_20261011_r01/delivery_manifest.json"
    interfaces=read(upstream_manifest)["interfaces"];assert all(sha(ROOT/i["path"])==i["sha256"] for i in interfaces)
    manifests={}
    for stage,run in STAGES.items():
        evidence=ROOT/"report/evidence/S2B-T17"/run
        files={p:{"path":p,"sha256":h,"role":"source"} for p,h in hashes.items()}
        external=[upstream_path,upstream_manifest,main/"source_freeze.json",main/"g1_summary.json",ROOT/"report/evidence/S2B-T17/s10_platform_20261012_r01/timing_worst_synth.rpt"]
        for path in [*sorted(evidence.rglob("*")),*external]:
            if not path.is_file() or path.name=="delivery_manifest.json":continue
            relative=path.relative_to(ROOT).as_posix();own=path.is_relative_to(evidence)
            role="input" if not own or path.name.endswith("_vectors.dat") else "log" if path.suffix==".log" else "source" if path.suffix in (".py",".sv",".tcl",".md") else "diagnostic" if path.suffix==".patch" else "result"
            assert not any(p in (".runs",".gen",".srcs",".cache") for p in path.parts)
            assert path.suffix.lower() not in (".exe",".o",".dcp",".bit")
            files[relative]={"path":relative,"sha256":sha(path),"role":role}
        checks=[{"name":"真实原生runner","status":"PASS","command":natives[stage]["command"],"exit_code":natives[stage]["native_exit_code"],"reason":"实际原生执行，单job/thread1及外层1GiB/guard合计640MiB、backend300MiB守卫。"}]
        for record in reports[stage]["runs"]:checks.append({"name":record["name"],"status":"PASS","command":subprocess.list2cmdline(record["command"]),"exit_code":record["exit_code"],"reason":"真实编译/仿真命令与原生退出码；原始日志绑定。"})
        checks.extend({"name":name,"status":"NOT_RUN","command":None,"exit_code":None,"reason":reason} for name,reason in (("独立G2","ROOT随后独立审查。"),("S11真实STA与实现","仅功能G1，S10实际STA仍FAIL。"),("G3实板","未操作设备。")))
        manifest={"schema_version":1,"stage":"2B","task_id":"S2B-T17","run_id":run,"source_commit":BASE,"evidence_dir":evidence.relative_to(ROOT).as_posix(),"interfaces":interfaces,"tool_versions":reports[stage]["tool_versions"],"files":list(files.values()),"checks":checks,"limitations":limits}
        target=evidence/"delivery_manifest.json";write(target,manifest);manifests[stage]={"path":target.relative_to(ROOT).as_posix(),"sha256":sha(target)}
    captures=[]
    for stage,item in manifests.items():
        for mode in ("evidence","inputs"):
            argv=[sys.executable,"-X","utf8","-B",str(ROOT/"verification/check_stage_delivery.py"),"--project-root",str(ROOT),"--mode",mode,"--manifest",str(ROOT/item["path"])]
            done=subprocess.run(argv,cwd=ROOT,capture_output=True)
            record={"stage":stage,"mode":mode,"command":subprocess.list2cmdline(argv),"argv":argv,"native_exit_code":done.returncode,"stdout":done.stdout.decode("utf-8"),"stderr":done.stderr.decode("utf-8")}
            write(WORK/(stage+"_"+mode+"_native.json"),record);assert done.returncode==(0 if mode=="evidence" else 2),record
            captures.append({"stage":stage,"mode":mode,"native_exit_code":done.returncode})
    assert hashes=={p:sha(ROOT/p) for p in paths}
    final={"status":"STOP_READY_G1_ONLY","source_commit":BASE,"source_freeze_sha256":sha(main/"source_freeze.json"),"diff_sha256":sha(main/"source_diff.patch"),"g1_summary_sha256":sha(main/"g1_summary.json"),"modified":freeze["modified_files"],"manifests":manifests,"checks":captures,"peak_tree_rss_bytes":max(n["peak_tree_rss_bytes"] for n in natives.values()),"elapsed_seconds":time.monotonic()-started}
    write(WORK/"final_package_receipt.json",final);print(json.dumps(final,ensure_ascii=False),flush=True)

if __name__=="__main__":main()
