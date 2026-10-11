#!/usr/bin/env python3
"""只封存S9真实功能运行；失败原件保留，缓存不入证据，不提交Git。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[4]
WORK=Path(__file__).resolve().parent
BASELINE="5ea54b441bd885e10eac4794cbad5ad48c510a49"
MAIN="conv_output_address_20261011_r03"
STAGES={"direct_r03":MAIN,"boundary":"conv_output_address_boundary_20261011_r01",
        "layer0":"conv_output_address_layer0_20261011_r01","backend":"conv_output_address_trace_20261011_r01",
        "geometry":"conv_output_address_geometry_20261011_r01"}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding="utf-8"))


def write(path,value):
    """一次写入新原件，禁止覆盖已封存文件。"""
    with path.open("x",encoding="utf-8",newline="\n") as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write("\n")


def copy_file(source,target):
    """按授权精确目标复制；已有目标必须原字节相同。"""
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():assert sha(target)==sha(source)
    else:shutil.copyfile(source,target)


def diagnostic(main,reports):
    """逐条限定direct测试驱动警告；公开START回归不允许三类异常诊断。"""
    report=reports["direct_r03"]
    run=next(x for x in report["runs"] if x["name"]=="compile")
    logpath=ROOT/run["log"];log=logpath.read_text(encoding="utf-8")
    tbpath=main/"tb_s2b_conv_output_address.sv";tb=tbpath.read_text(encoding="utf-8")
    assert "logic clk=0;" in tb and not re.search(r"always\s*#|clk\s*<=|clk\s*=\s*~",tb)
    assert len(re.findall(r"\bclk\s*=",tb))==1 and not re.search(r"\bforce\b",tb)
    expected={"output_group_base","output_lane_index","output_height_latched","output_width_latched",
              "tile_start_y","output_point_scan_y","tile_start_x","output_point_scan_x","output_base_latched",
              "output_channels_latched","group_lane_count","output_point_index","tile_point_count"}
    records=[]
    starts=list(re.finditer(r"%Warning-MULTIDRIVEN: ([^\r\n]+)",log))
    for m in starts:
        first=m[1]
        item=re.search(r"^(.+?):(\d+):(\d+):.*?: '([^']+)'",first)
        assert item,first
        source,line,col,signal=item.groups()
        assert signal in expected
        instance="u_old" if "s8_conv_tile_engine_original.sv" in source else "u_dut"
        assert instance=="u_old" or "s2b_conv_tile_engine.sv" in source
        drives=[i+1 for i,text in enumerate(tb.splitlines()) if f"{instance}.{signal}=v_{signal};" in text]
        assert len(drives)==1
        stop=log.find("%Warning-",m.end())
        block=log[m.start():stop if stop>=0 else len(log)]
        records.append({"module_instance":instance,"signal":signal,"production_source":source,
                        "source_line":int(line),"source_column":int(col),"testbench_line":drives[0],
                        "compile_log_line":log[:m.start()].count("\n")+1,"raw_diagnostic":block.strip()})
    assert {(r["module_instance"],r["signal"]) for r in records}=={(i,n) for i in ("u_old","u_dut") for n in expected}
    assert len(records)==26
    assert not re.search(r"%Warning-(?:LATCH|UNOPTFLAT):",log)
    public=[]
    for stage in ("boundary","layer0","geometry"):
        for run in reports[stage]["runs"]:
            if "compile" not in run["name"]:continue
            path=ROOT/run["log"];text=path.read_text(encoding="utf-8")
            assert not re.search(r"%Warning-(?:LATCH|UNOPTFLAT|MULTIDRIVEN):",text),(stage,str(path))
            public.append({"stage":stage,"path":run["log"],"sha256":sha(path),"three_abnormal_diagnostics":[]})
    backend_path=ROOT/next(r["log"] for r in reports["backend"]["runs"] if r["name"]=="compile")
    previous_path=ROOT/"report/evidence/S2B-T17/maxpool_address_guard_trace_20261011_r01/compile.log"
    previous=previous_path.read_text(encoding="utf-8");backend=backend_path.read_text(encoding="utf-8")
    prior_headers=re.findall(r"%Warning-MULTIDRIVEN: [^\r\n]+",previous)
    actual_headers=re.findall(r"%Warning-MULTIDRIVEN: [^\r\n]+",backend)
    assert prior_headers==actual_headers and len(actual_headers)==16
    assert not re.search(r"%Warning-(?:LATCH|UNOPTFLAT):",backend)
    backend_tb=ROOT/"report/evidence/S2B-T17/conv_output_address_trace_20261011_r01/tb_s2b_backend_coordinates.sv"
    prior_tb=ROOT/"report/evidence/S2B-T17/maxpool_address_guard_trace_20261011_r01/tb_s2b_backend_coordinates.sv"
    assert sha(backend_tb)==sha(prior_tb)
    inherited={"count":16,"raw_headers":actual_headers,
               "source_previous_log":{"path":previous_path.relative_to(ROOT).as_posix(),"sha256":sha(previous_path)},
               "source_actual_log":{"path":backend_path.relative_to(ROOT).as_posix(),"sha256":sha(backend_path)},
               "testbench_identical_to_s8":{"path":backend_tb.relative_to(ROOT).as_posix(),"sha256":sha(backend_tb),"previous_path":prior_tb.relative_to(ROOT).as_posix()},
               "scope":"原relational boundary段force/release及关系初态驱动；PUBLIC_ENTRY/完整trace释放所有注入，完整TB逐字同S8。仅承认既有诊断，不豁免新生产驱动。"}
    return {"scope":"direct TB主动驱动13个旧/新寄存器，时钟恒0且无上升沿，FF未执行；CONV公开START诊断严格另查。backend继承注入诊断单独同S8原件对照。",
            "testbench":{"path":tbpath.relative_to(ROOT).as_posix(),"sha256":sha(tbpath)},
            "compile_log":{"path":logpath.relative_to(ROOT).as_posix(),"sha256":sha(logpath)},
            "records":records,"public_compile_checks":public,"backend_inherited":inherited}


def main():
    """执行真实轻量反例后冻结全部源和每个运行的标准六角色清单。"""
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()==BASELINE
    main=ROOT/"report/evidence/S2B-T17"/MAIN
    spec=importlib.util.spec_from_file_location("s9_checker",ROOT/"verification/check_s2b_inference_platform.py")
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    bindings=checker.check_static(ROOT)
    upstream_path=ROOT/"report/evidence/S2B-T17/maxpool_address_guard_20261011_r01/source_freeze.json"
    assert sha(upstream_path)=="f1a70a6f0b703a1e062c479cbc18177b3800f337e06a9fe25dc7d07363ed8708"
    upstream=read(upstream_path)
    paths=list(dict.fromkeys([x["path"] for x in upstream["source_files"]]+list(bindings)+["verification/test_s2b_conv_output_address_rtl.py"]))
    assert len(paths)==42
    hashes={p:sha(ROOT/p) for p in paths}
    reports={stage:read(ROOT/"report/evidence/S2B-T17"/run/"validation.json") for stage,run in STAGES.items()}
    natives={stage:read(WORK/(stage+"_native.json")) for stage in STAGES}
    for stage,report in reports.items():
        assert report["status"].startswith("PASS") and natives[stage]["native_exit_code"]==0
        pre=report["source_sha256_pre"];post=report["source_sha256_post"]
        assert pre==post and all(hashes.get(p,sha(ROOT/p))==h for p,h in post.items())
    frozen={p:sha(ROOT/p) for p in checker.FROZEN_CORE_SHA256}
    assert frozen==checker.FROZEN_CORE_SHA256==upstream["frozen14"]
    # 轻量反例原生码由subprocess保存；不是自报审查0。
    negative_cmd=[sys.executable,"-X","utf8","-B",str(WORK/"platform_negatives.py")]
    negative=subprocess.run(negative_cmd,cwd=ROOT,capture_output=True)
    write(main/"platform_negative_native.json",{"command":subprocess.list2cmdline(negative_cmd),"argv":negative_cmd,
          "native_exit_code":negative.returncode,"stdout":negative.stdout.decode("utf-8"),"stderr":negative.stderr.decode("utf-8")})
    assert negative.returncode==0
    negative_report=json.loads(negative.stdout)
    assert negative_report["total"]==26
    write(main/"platform_negatives.json",negative_report)
    write(main/"diagnostic_scope.json",diagnostic(main,reports))
    snapshot=main/"final_source_snapshot";snapshot.mkdir()
    for p in paths:copy_file(ROOT/p,snapshot/p)
    modified=["src/s2b_conv_tile_engine.sv","verification/check_s2b_inference_platform.py","board/s2b_inference_platform.json",
              "board/s2b_inference_platform.md","vivado/s2b_inference_platform.tcl","verification/test_s2b_geometry_specialization_rtl.py",
              "verification/test_s2b_backend_coordinates_rtl.py","verification/test_s2b_conv_validation_rtl.py"]
    diff=subprocess.check_output(["git","diff","--no-ext-diff","--no-color",BASELINE,"--",*modified],cwd=ROOT)
    added=subprocess.run(["git","diff","--no-index","--no-ext-diff","--no-color","--","NUL","verification/test_s2b_conv_output_address_rtl.py"],cwd=ROOT,capture_output=True)
    assert added.returncode==1
    (main/"source_diff.patch").write_bytes(diff+added.stdout)
    # G0数学与首轮失败精简原件绑定；不将数学结果作为RTL/G2证据。
    g0=ROOT/"tmp/2B/S2B-T17/s9_g0_prepare_20261011_r01"
    for name in ("math_probe.py","run_probe.py","result_r02.json","native_capture_r02.json","stdout_r02.log","stderr_r02.log","native_capture.json","stdout.log","stderr.log","failed_initial/math_probe.py","failed_initial/run_probe.py"):
        copy_file(g0/name,main/"g0_math_raw"/name)
    runtime=main/"execution_raw";runtime.mkdir()
    for path in WORK.iterdir():
        if path.is_file() and (path.suffix in (".py",".json",".log")) and path.name!="finalize.py" and not path.name.startswith("finalize_"):copy_file(path,runtime/path.name)
    copy_file(Path(__file__),runtime/"finalize.py")
    freeze={"schema_version":1,"source_commit":BASELINE,"profile":"s2b-inference-platform/0.1.9",
            "active_rtl_sources":json.loads((ROOT/"board/s2b_inference_platform.json").read_text(encoding="utf-8"))["rtl_sources"],
            "upstream_s8_freeze":{"path":upstream_path.relative_to(ROOT).as_posix(),"sha256":sha(upstream_path)},
            "source_files":[{"path":p,"sha256":h,"bytes":(ROOT/p).stat().st_size,"snapshot":(snapshot/p).relative_to(ROOT).as_posix()} for p,h in hashes.items()],
            "frozen14":frozen,"tested_source_drift":{},"source_diff_sha256":sha(main/"source_diff.patch"),
            "modified_files":{p:hashes[p] for p in modified+["verification/test_s2b_conv_output_address_rtl.py"]}}
    write(main/"source_freeze.json",freeze)
    summary={"status":"PASS_S9_G1_FUNCTIONAL_ONLY","source_commit":BASELINE,"profile":"s2b-inference-platform/0.1.9",
             "source_closure_count":len(paths),"static_source_count":len(bindings),"active_rtl_count":18,"derived_rtl_count":8,"frozen_active_rtl_count":6,"outer_rtl_count":4,
             "direct":reports["direct_r03"]["actual_coverage"],"boundary":reports["boundary"]["actual_coverage"],
             "layer0":reports["layer0"]["actual_coverage"],"cpu_layer0":reports["layer0"]["independent_cpu_layer0"],
             "backend":reports["backend"]["simulation_counts"],"public_entries":reports["backend"]["public_entries"],
             "geometry":reports["geometry"].get("simulation_counts",reports["geometry"].get("runs")),
             "platform_negatives":26,"original_platform_negatives":25,"added_old_s8_profile_negative":1,"offset_mutants":8,
             "execution":[{"stage":s,"run_id":STAGES[s],"native_exit_code":n["native_exit_code"],"seconds":n["elapsed_seconds"],"peak_tree_rss_bytes":n["peak_tree_rss_bytes"],"runs":reports[s]["runs"]} for s,n in natives.items()],
             "failed_attempts":[{"run_id":"conv_output_address_20261011_r01","native_exit_code":read(WORK/"direct_native.json")["native_exit_code"],"reason":"DISK_LIMIT：完整编译PCH加两个重复模型夹具/向量触发300MiB守卫"},
                                {"run_id":"conv_output_address_20261011_r02","native_exit_code":read(WORK/"direct_r02_native.json")["native_exit_code"],"reason":"DISK_LIMIT：夹具已缩至静态闭包，但PCH加20MiB重复向量略超300MiB；r03用相同原件VECTOR_PATH消除缓存副本"}],
             "independent_review":"NOT_RUN","sta":"NOT_RUN","implementation":"NOT_RUN","g3":"NOT_RUN",
             "tool_calls":"只统计本包真实native记录和runner子命令；完整会话工具调用量未测。",
             "limitations":["direct内部组合输入非公开START可达域，受控寄存器驱动的26条MULTIDRIVEN按diagnostic_scope逐条绑定；CONV公开START三类异常诊断为空；backend16既有bench驱动诊断逐条同S8。",
                            "原S8 unsigned64域、C/Y/X低32截断、所有FF/FSM/端口/guard原样；不增33/65进位拒绝。",
                            "layer0为真实CONV完整数值/周期；backend15非CONV完整trace的CONV仍是共享控制stub，未声称21CONV全数值或新109全网。",
                            "50MHz/100黄金样本/1000实板标准未降低；G1功能通过不代表实际S9 STA或G2/G3。"]}
    write(main/"g1_summary.json",summary)
    interfaces=read(ROOT/"report/evidence/S2B-T17/maxpool_address_guard_20261011_r01/delivery_manifest.json")["interfaces"]
    for interface in interfaces:assert sha(ROOT/interface["path"])==interface["sha256"]
    for stage,runid in STAGES.items():
        evidence=ROOT/"report/evidence/S2B-T17"/runid
        manifest={"schema_version":1,"stage":"2B","task_id":"S2B-T17","run_id":runid,"source_commit":BASELINE,
                  "evidence_dir":evidence.relative_to(ROOT).as_posix(),"interfaces":interfaces,"tool_versions":reports[stage]["tool_versions"],"files":[],"checks":[],"limitations":summary["limitations"]}
        manifest["files"]=[{"path":p,"sha256":h,"role":"source"} for p,h in hashes.items()]
        external=[upstream_path,main/"source_freeze.json",main/"g1_summary.json",ROOT/"report/evidence/S2B-T17/s8_platform_20261011_r01/timing_worst_synth.rpt"]
        if stage=="direct_r03":
            for failed in ("conv_output_address_20261011_r01","conv_output_address_20261011_r02"):
                external.extend(p for p in (ROOT/"report/evidence/S2B-T17"/failed).rglob("*") if p.is_file())
        for path in [*sorted(evidence.rglob("*")),*external]:
            if not path.is_file() or path.name=="delivery_manifest.json":continue
            role="log" if path.suffix==".log" else "input" if path.name=="address_vectors.txt" else "source" if path.suffix in (".sv",".py",".tcl",".md") else "diagnostic" if path.suffix==".patch" else "result"
            manifest["files"].append({"path":path.relative_to(ROOT).as_posix(),"sha256":sha(path),"role":role})
        manifest["files"]=list({f["path"]:f for f in manifest["files"]}.values())
        native=natives[stage]
        manifest["checks"].append({"name":"真实原生runner","status":"PASS","command":native["command"],"exit_code":native["native_exit_code"],"reason":"实际子进程结果，原生记录与日志已保存；宿主shell归一未替代native码。"})
        for record in reports[stage]["runs"]:
            manifest["checks"].append({"name":record["name"],"status":"PASS","command":subprocess.list2cmdline(record["command"]),"exit_code":record["exit_code"],"reason":"实际compile/simulation原生结果，单job/thread及峰RSS绑定。"})
        if stage=="direct_r03":
            manifest["checks"].append({"name":"26平台反例","status":"PASS","command":subprocess.list2cmdline(negative_cmd),"exit_code":negative.returncode,"reason":"25原函数反例原样复跑+1旧S8 profile；不填独审自报0。"})
            for name in ("direct","direct_r02"):
                n=read(WORK/(name+"_native.json"))
                manifest["checks"].append({"name":"已修复缓存准备失败_"+name,"status":"FAIL","command":n["command"],"exit_code":n["native_exit_code"],"reason":"失败原件保留，r03同刺激/原黄金成功；失败不是RTL mismatch。"})
        manifest["checks"].extend({"name":name,"status":"NOT_RUN","command":None,"exit_code":None,"reason":reason} for name,reason in (("独立G2","ROOT随后固定源后独审。"),("S9实际STA与实现","仅功能G1，S8真实STA仍FAIL。"),("G3实板","本轮无设备操作。")))
        write(evidence/"delivery_manifest.json",manifest)
    captures=[]
    for stage,runid in STAGES.items():
        for mode in ("evidence","inputs"):
            argv=[sys.executable,"-X","utf8","-B",str(ROOT/"verification/check_stage_delivery.py"),"--project-root",str(ROOT),"--mode",mode,"--manifest",str(ROOT/"report/evidence/S2B-T17"/runid/"delivery_manifest.json")]
            done=subprocess.run(argv,cwd=ROOT,capture_output=True)
            record={"run_id":runid,"mode":mode,"command":subprocess.list2cmdline(argv),"argv":argv,"native_exit_code":done.returncode,"stdout":done.stdout.decode("utf-8"),"stderr":done.stderr.decode("utf-8")}
            write(WORK/(stage+"_"+mode+"_native.json"),record);captures.append(record)
            assert done.returncode==(0 if mode=="evidence" else 2),record
            print(json.dumps({"run_id":runid,"mode":mode,"native_exit_code":done.returncode},ensure_ascii=False),flush=True)
    assert all(sha(ROOT/p)==h for p,h in hashes.items())
    print(json.dumps({"status":"STOP_READY_G1_ONLY","source_freeze_sha256":sha(main/"source_freeze.json"),"diff_sha256":sha(main/"source_diff.patch"),"modified":freeze["modified_files"],"peak_tree_rss_bytes":max(n["peak_tree_rss_bytes"] for n in natives.values())},ensure_ascii=False),flush=True)


if __name__=="__main__":main()
