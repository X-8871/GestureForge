#!/usr/bin/env python3
"""S13：现有PRE拍原点登记、公开逐周期差分和受影响单任务回归。"""
from __future__ import annotations
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import time
import psutil
import test_s2b_conv_validation_rtl as validation
import test_s2b_conv_feature_address_rtl as feature
import test_s2b_backend_coordinates_rtl as support
import test_s2b_geometry_specialization_rtl as geometry
import test_s2b_route_specialization_rtl as route

ROOT=Path(__file__).resolve().parents[1]
DEVELOPMENT_START="467463757158aed80d6f75afadff6a8458614a29"
RUN_ID="s13_tile_origin_20261012_r01"
ENGINE="src/s2b_conv_tile_engine.sv"
RUNNER="verification/test_s2b_conv_tile_origin_rtl.py"
SEED=0x5A1713

def sha(path):
    """绑定真实原字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path,value):
    """唯一新目标，失败和旧运行不覆盖。"""
    with path.open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write("\n")

def exact_directory(path):
    """逐组件验证完整精确目录及类型，复用真实枚举返回目标。"""
    if not path.is_absolute():raise ValueError("不是完整绝对目录")
    current=Path(path.anchor)
    for name in path.parts[1:]:
        matches=[p for p in current.iterdir() if p.name==name]
        if len(matches)!=1:raise ValueError("精确目录不存在："+str(path))
        current=matches[0]
        if current.is_symlink() or current.is_junction() or not current.is_dir():raise ValueError("目录类型或链接错误")
    return current

def git(*args):
    """只读Git，所有调用显式关闭自动维护并支持长路径。"""
    command=["git","-c","core.longpaths=true","-c","maintenance.auto=false",*args]
    done=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=30)
    if done.returncode:raise ValueError("Git真实失败："+str(done.returncode)+":"+done.stderr.decode("utf-8",errors="replace"))
    return done.stdout

def resource(checker,work):
    """每次编译先确认无其他重型工具；不能判断的候选明确阻断。"""
    heavy=[];unknown=[]
    for process in psutil.process_iter(["name"]):
        name=process.info.get("name")
        if not name:continue
        if re.fullmatch(r"(?:vivado|verilator_bin|cc1plus|Vtb_.*)\.exe",name,re.I):
            try:heavy.append(dict(pid=process.pid,name=name,create_time_unix=process.create_time(),rss=process.memory_info().rss))
            except psutil.Error as error:unknown.append(dict(pid=process.pid,name=name,error=str(error)))
    result=dict(available_ram_bytes=psutil.virtual_memory().available,disk_free_bytes=shutil.disk_usage(work).free,heavy=heavy,unknown=unknown,jobs=1,threads=1)
    if heavy or unknown or result["available_ram_bytes"]<2147483648 or result["disk_free_bytes"]<1073741824:raise ValueError("编译准入阻断："+json.dumps(result,ensure_ascii=False))
    return result

def execute(name,command,work,evidence,env,record,timeout):
    """捕获实际直接子进程身份、返回码和两原生流，单任务限额监测。"""
    print(json.dumps(dict(event="START",test=evidence.name,command=name),ensure_ascii=False),flush=True)
    started=time.monotonic();peak=0;failure=None
    out=evidence/(name+".stdout.log");err=evidence/(name+".stderr.log")
    with out.open("xb") as stdout,err.open("xb") as stderr:
        child=subprocess.Popen(command,cwd=work,env=env,stdout=stdout,stderr=stderr)
        try:birth=psutil.Process(child.pid).create_time()
        except psutil.Error:birth="UNKNOWN"
        while child.poll() is None:
            try:
                members=[psutil.Process(child.pid)]+psutil.Process(child.pid).children(recursive=True)
                peak=max(peak,sum(p.memory_info().rss for p in members if p.is_running()))
            except psutil.Error:pass
            if peak>1073741824 or time.monotonic()-started>timeout or psutil.virtual_memory().available<536870912:
                failure="RSS_LIMIT" if peak>1073741824 else "TIMEOUT" if time.monotonic()-started>timeout else "SYSTEM_RAM_LIMIT"
                subprocess.run(["taskkill","/PID",str(child.pid),"/T","/F"],stdout=stdout,stderr=stderr,timeout=30)
                break
            time.sleep(.1)
        code=child.wait(timeout=30)
    row=dict(name=name,command=command,cwd=str(work),pid=child.pid,create_time_unix=birth,native_exit_code=code,direct_wait_exit_code=code,terminal_state="EXITED_DIRECT_CHILD_WAIT",elapsed_seconds=round(time.monotonic()-started,3),peak_tree_rss_bytes=peak,failure=failure,stdout=dict(path=out.relative_to(ROOT).as_posix(),sha256=sha(out)),stderr=dict(path=err.relative_to(ROOT).as_posix(),sha256=sha(err)))
    record["runs"].append(row)
    save(evidence/(name+".native.json"),row)
    print(json.dumps(dict(event="END",test=evidence.name,name=name,code=code,seconds=row["elapsed_seconds"],peak=peak),ensure_ascii=False),flush=True)
    if code or failure:raise ValueError("原生任务失败："+str(row))
    return out.read_text(encoding="utf-8",errors="strict")

def origin_monitor(instance="u_candidate"):
    """公开轨迹只读候选寄存器，PRE前计算旧完整表达式，PRE后核实登记。"""
    return f"""
integer origin_preps=0,origin_x_tiles=0,origin_y_tiles=0,origin_clears=0;
logic [63:0] expected_origin_y,expected_origin_x;
logic check_origin_prep,check_origin_clear;
always @(posedge clk) begin
 check_origin_clear=hard_reset || abort || ({instance}.state=={instance}.ST_IDLE && start_valid && start_ready);
 check_origin_prep=!hard_reset && !abort && {instance}.state=={instance}.ST_TILE_PREP;
 expected_origin_y=64'({instance}.tile_start_y)*64'({instance}.stride_y_latched)-64'({instance}.pad_top_latched);
 expected_origin_x=64'({instance}.tile_start_x)*64'({instance}.stride_x_latched)-64'({instance}.pad_left_latched);
 #1;
 if(check_origin_clear)begin
  if({instance}.tile_origin_y!==64'd0 || {instance}.tile_origin_x!==64'd0)$fatal(1,"origin复位/abort/START清零失败");
  origin_clears++;
 end else if(check_origin_prep)begin
  if({instance}.tile_origin_y!==expected_origin_y || {instance}.tile_origin_x!==expected_origin_x)$fatal(1,"PRE原点登记失败");
  origin_preps++;if({instance}.tile_start_x!=0)origin_x_tiles++;if({instance}.tile_start_y!=0)origin_y_tiles++;
 end
end
always @(negedge clk)begin
 if(!hard_reset && !abort && ({instance}.state=={instance}.ST_FEATURE_SCAN || {instance}.state=={instance}.ST_FEATURE_REQUEST || {instance}.state=={instance}.ST_FEATURE_RESPONSE))begin
  if({instance}.tile_origin_y!==(64'({instance}.tile_start_y)*64'({instance}.stride_y_latched)-64'({instance}.pad_top_latched)) || {instance}.tile_origin_x!==(64'({instance}.tile_start_x)*64'({instance}.stride_x_latched)-64'({instance}.pad_left_latched)))$fatal(1,"特征消费拍origin不变量失败");
 end
end
"""

def boundary_bench(names,small):
    """复用原20状态公开差分，并新增无需复位的首/横/纵tile与新START轨迹。"""
    text=validation.boundary_tb(names,small)
    addition="""
 raw_invalid=0;
 for(integer job=0;job<2;job++)begin
  defaults;requests=0;error_code=0;error_request=0;pending=0;backend_rsp_valid=0;
  input_channels=1;input_height=(job==0?9:19);input_width=input_height;
  input_length_bytes=input_height*input_width;output_channels=1;output_height=(job==0?9:11);output_width=output_height;
  output_length_bytes=output_height*output_width;kernel_height=1;kernel_width=1;
  stride_y=(job==0?1:2);stride_x=stride_y;pad_top=job;pad_bottom=job;pad_left=job;pad_right=job;
  quantized_weight_bytes=1;start_dut;timeout_count=0;
  while(!result_valid && timeout_count<100000)begin service;timeout_count++;end
  if(!result_valid || result_error_code!=0)$fatal(1,"公开多tile/newSTART轨迹失败job=%0d",job);
  $display("S13_PUBLIC_TRACE job=%0d requests=%0d cycles=%0d preps=%0d",job,requests,timeout_count,origin_preps);
  result_ready=1;service;result_ready=0;
 end
 if(origin_preps<8 || origin_x_tiles<2 || origin_y_tiles<2 || origin_clears<40)$fatal(1,"顺序origin覆盖不足");
 $display("PASS S13_ORIGIN_INVARIANTS preps=%0d x_tiles=%0d y_tiles=%0d clears=%0d",origin_preps,origin_x_tiles,origin_y_tiles,origin_clears);
"""
    marker=' $display("PASS CONV_VALIDATION'
    assert text.count(marker)==1
    text=text.replace(marker,addition+marker)
    tap="""
integer tap_samples=0;
always @(negedge clk)begin
 if(!hard_reset && !abort && u_dut.compute_read_enable)begin
  if(!u_candidate.compute_read_enable || u_dut.compute_read_tap_in_bounds!==u_candidate.compute_read_tap_in_bounds || u_dut.compute_read_feature_index_wide!==u_candidate.compute_read_feature_index_wide)$fatal(1,"真实顺序tap坐标/索引差分失败");
  tap_samples++;
 end
end
"""
    text=text.replace(' $display("PASS S13_ORIGIN_INVARIANTS', ' if(tap_samples==0)$fatal(1,"顺序tap覆盖缺失");\n $display("PASS S13_TAP_REGRESSION samples=%0d",tap_samples);\n $display("PASS S13_ORIGIN_INVARIANTS')
    return text.replace("endmodule",origin_monitor()+tap+"\nendmodule")

def algebra():
    """无限精度整数分别在原节点取模，证明完整U32乘积/bit63回绕与移项。"""
    mask=(1<<64)-1;rng=random.Random(SEED)
    edges=(0,1,2,65535,65536,0x7fffffff,0x80000000,0xffffffff)
    rows=list(itertools.product(edges,repeat=4))+[tuple(rng.getrandbits(32) for _ in range(4)) for _ in range(20000)]
    for tile,stride,scan,pad in rows:
        old=(tile*stride+scan-pad)&mask
        origin=(tile*stride-pad)&mask
        assert (origin+scan)&mask==old
    return dict(status="PASS_MOD64_ASSOCIATIVITY",seed=SEED,vectors=len(rows),scope="独立数学全宽边界；不代替实际PRE登记与公开事务覆盖")

def contract(checker):
    """只允许固定六项origin替换，旧状态机和其余FF完整字节核对。"""
    old=git("show",DEVELOPMENT_START+":"+ENGINE).decode("utf-8").replace("\r\n","\n")
    expected=old
    for before,after in checker.S13_TILE_ORIGIN_REPLACEMENTS:
        assert expected.count(before)==1
        expected=expected.replace(before,after)
    assert expected==(ROOT/ENGINE).read_text(encoding="utf-8")
    assert old.split(");",1)[0]==expected.split(");",1)[0]
    assert old.count("always_ff")==expected.count("always_ff")==2
    return dict(status="EXACT_SIX_ORIGIN_REPLACEMENTS_ONLY",reference_commit=DEVELOPMENT_START,old_git_sha256=hashlib.sha256(old.encode()).hexdigest(),public_header_equal=True,state_machine_cycles_unchanged_by_structure=True)

def main():
    """串行单job；所有输出仅在指定S13运行下，失败保留并真实返回非零。"""
    parser=argparse.ArgumentParser();parser.add_argument("--mode",choices=("all","feature","boundary","layer0","regressions"),default="all")
    parser.add_argument("--attempt",default="r01");parser.add_argument("--toolchain",type=Path,default=Path("D:/FPGA_S2A_MSYS2_20261001/env"));args=parser.parse_args()
    if not re.fullmatch(r"r[0-9]{2}",args.attempt):raise ValueError("attempt字面名称非法")
    checker=support.load_checker()
    parents=[ROOT/"tmp/2B/S2B-T17",ROOT/"report/evidence/S2B-T17"]
    bases=[]
    for parent in parents:
        parent=exact_directory(parent);base=parent/RUN_ID
        if not base.exists():base.mkdir()
        else:base=exact_directory(base)
        target=base/(args.mode+"_"+args.attempt)
        if target.exists():raise ValueError("已有attempt不覆盖")
        target.mkdir();bases.append(target)
    work,evidence=bases;begin=time.monotonic()
    report=dict(schema_version=1,task_id="S2B-T17-S13",run_id=RUN_ID,mode=args.mode,attempt=args.attempt,status="FAIL",development_start_commit=DEVELOPMENT_START,observed_head_at_start=git("rev-parse","HEAD").decode().strip(),runs=[],limitations=["S13功能G1不代表50MHz STA、PNR、G2、109整网或板上通过。","组合feature测试为origin不变量条件下的受控内部域；公开PRE登记由boundary/layer0另外证明。","没有运行Vivado或硬件；原S12 STA失败与资源监测GAP保留。"])
    result=1
    try:
        sources=checker.check_static(ROOT)
        for path in (RUNNER,validation.RUNNER,feature.RUNNER,support.RUNNER,geometry.RUNNER,route.RUNNER,support.MODEL,"sim/tb_s2a_t66_candidate_blackbox.sv","verification/s1_t02_d2_int8_forward.py"):
            sources[path]=sha(checker.exact_file(ROOT/path))
        report["source_sha256_pre"]=sources;report["frozen14_sha256"]={p:sha(ROOT/p) for p in checker.FROZEN_CORE_SHA256}
        snapshot=evidence/"source_snapshot";snapshot.mkdir()
        for path in sources:
            target=snapshot/path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/path,target)
        report["contract"]=contract(checker);report["algebra"]=algebra()
        report["checker_negatives"]=support.checker_negatives(checker,work,checker.check_static(ROOT))
        model=json.loads((ROOT/support.MODEL).read_text(encoding="utf-8"))
        tools=exact_directory(args.toolchain/"mingw64/bin");make=exact_directory(args.toolchain/"usr/bin")
        verilator=checker.exact_file(tools/"verilator_bin.exe")
        checker.exact_file(tools/"g++.exe");checker.exact_file(make/"make.exe")
        env=dict(os.environ,PATH=str(make)+os.pathsep+str(tools)+os.pathsep+os.environ.get("PATH",""),VERILATOR_ROOT=str(args.toolchain/"mingw64/share/verilator"),PYTHONUTF8="1")
        report["tool_versions"]=dict(python=sys.version,verilator=subprocess.check_output([str(verilator),"--version"],cwd=work,env=env,text=True,timeout=30).strip())
        def compile_test(name,top,rtl,bench,files=None,extra=None,simulation_timeout=1200):
            """每个测试固定独立子目录，串行构建和运行并保存输入原件。"""
            wd=work/name;ed=evidence/name;wd.mkdir();ed.mkdir();source=wd/"source";source.mkdir()
            record=dict(name=name,runs=[],resource_preflight=resource(checker,wd));report.setdefault("tests",[]).append(record)
            for path in rtl:shutil.copyfile(ROOT/path,source/Path(path).name)
            for path,payload in (files or {}).items():
                for directory in (wd,ed):(directory/path).write_text(payload,encoding="utf-8",newline="\n")
            if extra:
                for name0,payload in extra.items():(source/name0).write_text(payload,encoding="utf-8",newline="\n")
            for directory in (wd,ed):(directory/(top+".sv")).write_text(bench,encoding="utf-8",newline="\n")
            command=[str(verilator),"--binary","--timing","--timescale","1ns/1ps","-Wall","-Wno-fatal","-j","1","--threads","1","--output-split","10000","--output-split-cfuncs","100","--top-module",top,"--Mdir","obj_dir","-MAKEFLAGS","PYTHON3='\""+sys.executable+"\"'","-CFLAGS","-D_GLIBCXX_USE_CXX11_ABI=0 -O1",*["source/"+Path(p).name for p in rtl],*["source/"+p for p in (extra or {})],top+".sv"]
            execute("compile",command,wd,ed,env,record,900)
            sim=[str(checker.exact_file(wd/("obj_dir/V"+top+".exe")))]
            if name=="feature":sim.append("+VECTOR_PATH="+str(ed/"address_vectors.txt").replace("\\","/"))
            if name=="layer0":sim.extend("+T66_"+kind+"_PATH="+str(validation.FIXTURE/name0).replace("\\","/") for kind,name0 in zip(("INPUT","WEIGHT","GOLDEN"),validation.FIXED))
            text=execute("simulation",sim,wd,ed,env,record,simulation_timeout)
            return record,text
        if args.mode in ("all","feature"):
            vectors,proof=feature.vectors(model);report["feature_oracle"]=proof
            bench=feature.bench()
            origin_inputs="\n".join("u_dut.tile_origin_"+axis+" = $signed(64'(v_tile_start_"+axis+") * 64'(v_stride_"+axis+"_latched) - 64'(v_"+pad+"_latched));" for axis,pad in (("y","pad_top"),("x","pad_left")))
            bench=bench.replace("#1;\n",origin_inputs+"\n#1;\n")
            original=git("show",feature.BASELINE+":"+ENGINE).decode("utf-8").replace("\r\n","\n").replace("module s2b_conv_tile_engine (","module s2b_conv_tile_engine_original (")
            record,text=compile_test("feature","tb_s2b_conv_feature_address",("src/s2a_network_descriptor_pkg.sv",ENGINE),bench,{"address_vectors.txt":vectors},{"s9_conv_tile_engine_original.sv":original})
            match=re.search(r"PASS S10_CONV_FEATURE_ADDRESS vectors=(\d+) end=(\d+) padding=(\d+) range=(\d+) request=(\d+)",text)
            assert match and int(match[1])==proof["vectors"]
            record["coverage"]=dict(zip(("vectors","end","padding","range","request"),map(int,match.groups())))
        if args.mode in ("all","boundary"):
            names,vectors,small,proof=validation.vectors(model);report["boundary_oracle"]=proof
            record,text=compile_test("boundary","tb_s2b_conv_validation",validation.RTL,boundary_bench(names,small),{"validation_vectors.txt":vectors})
            match=re.search(r"PASS CONV_VALIDATION vectors=(\d+) cycles=(\d+) abort_mask=([a-fA-F0-9]+) reset_mask=([a-fA-F0-9]+) response_cases=24 raw80=1",text)
            assert match and int(match[1])==proof["vectors"] and int(match[3],16)==int(match[4],16)==0xfffff
            invariant=re.search(r"PASS S13_ORIGIN_INVARIANTS preps=(\d+) x_tiles=(\d+) y_tiles=(\d+) clears=(\d+)",text);assert invariant
            tap=re.search(r"PASS S13_TAP_REGRESSION samples=(\d+)",text);assert tap
            record["coverage"]=dict(vectors=int(match[1]),cycles=int(match[2]),abort_mask=match[3],reset_mask=match[4],response_cases=24,tap_samples=int(tap[1]),origin=dict(zip(("preps","x_tiles","y_tiles","clears"),map(int,invariant.groups()))),public_traces=re.findall(r"S13_PUBLIC_TRACE.*",text))
        if args.mode in ("all","regressions"):
            declarations={kind:geometry.ports(ROOT/path) for kind,path in (("pool","src/s2a_maxpool_engine.sv"),("upsample","src/s2a_upsample_engine.sv"))}
            payload={};coverage={}
            for kind in declarations:payload[kind+"_vectors.dat"],coverage[kind]=geometry.vector_data(kind,declarations[kind],model)
            record,text=compile_test("geometry","tb_s2b_geometry_specialization",geometry.RTL,geometry.generate_tb(declarations),payload)
            assert "PASS" in text;record["coverage"]=coverage
            ports=geometry.ports(ROOT/"src/s2a_route_engine.sv");vectors,coverage=route.vectors(model,ports)
            record,text=compile_test("route","tb_s2b_route_specialization",route.RTL,route.testbench(model,ports),{"route_vectors.dat":vectors})
            assert "PASS" in text;record["coverage"]=coverage
        if args.mode in ("all","layer0"):
            cpu=evidence/"cpu_layer0";cpu.mkdir()
            for name,(size,digest) in validation.FIXED.items():
                path=checker.exact_file(validation.FIXTURE/name);assert path.stat().st_size==size and sha(path)==digest
            report["cpu_layer0"]=validation.cpu_layer0(model,cpu,checker)
            bench=validation.layer0_tb().replace("endmodule",origin_monitor()+"\nendmodule")
            record,text=compile_test("layer0","tb_s2b_conv_layer0",validation.RTL,bench)
            assert text.count("PASS: T66 candidate blackbox sample0 layer0 full tensor matched T25; bytes=1384448 mismatches=0")==1
            match=re.search(r"bytes=(\d+) mismatches=0 input_reads=(\d+) weight_reads=(\d+) output_writes=(\d+) requests=(\d+) responses=(\d+) request_stalls=(\d+) response_stalls=(\d+) cycles=(\d+)",text);assert match
            record["coverage"]=dict(zip(("bytes","input_reads","weight_reads","output_writes","requests","responses","request_stalls","response_stalls","cycles"),map(int,match.groups())))
        report["source_sha256_post"]={p:sha(ROOT/p) for p in sources}
        assert sources==report["source_sha256_post"]
        report["observed_head_at_end"]=git("rev-parse","HEAD").decode().strip()
        report["status"]="PASS_S13_"+args.mode.upper()+"_G1_ONLY";result=0
    except Exception as error:
        report["error"]=str(error)
    report["elapsed_seconds"]=round(time.monotonic()-begin,3)
    report["created_at_utc8"]=datetime.now(timezone(timedelta(hours=8))).isoformat()
    save(evidence/"validation.json",report)
    print(json.dumps(dict(status=report["status"],error=report.get("error"),evidence=str(evidence),seconds=report["elapsed_seconds"]),ensure_ascii=False),flush=True)
    return result

if __name__=="__main__":raise SystemExit(main())
