#!/usr/bin/env python3
"""S15：私有输入H乘W缓存、独立地址黄金与原公开轨迹的串行G1。"""
from __future__ import annotations
import argparse
import copy
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
import test_s2b_conv_tile_origin_rtl as previous
import test_s2b_conv_output_address_rtl as output
import test_s2b_conv_validation_rtl as validation
import test_s2b_conv_feature_address_rtl as feature
import test_s2b_backend_coordinates_rtl as support
import test_s2b_geometry_specialization_rtl as geometry
import test_s2b_route_specialization_rtl as route

ROOT=Path(__file__).resolve().parents[1]
BASELINE="0700c33e6faba8861cc2e7646a8981e424a69c45"
RUN_ID="s15_arithmetic_fix_20261012_r01"
RUNNER="verification/test_s2b_s15_arithmetic_rtl.py"
ENGINE="src/s2b_conv_tile_engine.sv"
QUERY="src/s2b_route_query.sv"
SHAPES=((32,104,104),(64,52,52),(64,104,104),(128,26,26),(128,52,52),(256,13,13),(256,26,26))
SEED=0x5A1715
sha=previous.sha
save=previous.save

def contract(checker):
    """只允许S15的五项缓存替换；ROUTE生产源码保持S14完整字节。"""
    old=previous.git("show",BASELINE+":"+ENGINE).decode("utf-8").replace("\r\n","\n")
    expected=old
    for before,after in checker.S15_INPUT_GEOMETRY_CACHE_REPLACEMENTS:
        assert expected.count(before)==1
        expected=expected.replace(before,after)
    assert expected==(ROOT/ENGINE).read_text(encoding="utf-8")
    assert old.split(");",1)[0]==expected.split(");",1)[0]
    query=previous.git("show",BASELINE+":"+QUERY)
    assert query==(ROOT/QUERY).read_bytes()
    return {ENGINE:dict(reference_commit=BASELINE,old_git_sha256=hashlib.sha256(old.encode()).hexdigest(),rules=5,public_header_equal=True),QUERY:dict(reference_commit=BASELINE,unchanged_sha256=sha(ROOT/QUERY))}


def checker_negatives(checker,work,bindings):
    """S15独立固定绑定拒绝自报版本、哈希、登记语义和冻结查表漂移。"""
    fixture=work/"checker_fixture";fixture.mkdir()
    for path in bindings:
        target=fixture/path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/path,target)
    profile_path=fixture/"board/s2b_inference_platform.json"
    original=json.loads(profile_path.read_text(encoding="utf-8"));records=[]
    def reject(name,change):
        """每个反例独立恢复真实源码，自动更新自报SHA也必须拒绝。"""
        profile=copy.deepcopy(original);changed=change(profile)
        profile_path.write_text(json.dumps(profile,ensure_ascii=False),encoding="utf-8")
        try:checker.check_static(fixture)
        except (ValueError,KeyError,TypeError,OSError) as error:records.append(dict(name=name,status="REJECTED",reason=str(error)))
        else:raise ValueError("反例未拒绝："+name)
        finally:
            for path in changed if isinstance(changed,list) else []:shutil.copyfile(ROOT/path,fixture/path)
            shutil.copyfile(ROOT/"board/s2b_inference_platform.json",profile_path)
    def source(profile,path,before,after):
        """精确一次匹配，篡改者的新增替换不覆盖检查器固定授权。"""
        target=fixture/path;text=target.read_text(encoding="utf-8");assert text.count(before)==1
        target.write_text(text.replace(before,after),encoding="utf-8",newline="\n")
        for item in profile["source_derivation"]["derived_sources"]+profile["source_derivation"]["upstream_sources"]:
            if item["path"]==path:
                item["sha256"]=sha(target)
                if "replacements" in item:item["replacements"].append([before,after])
        return [path]
    for value in ("0.1.0","0.1.11","0.1.13","0.1.14","0.1.15"):
        reject("旧profile"+value,lambda p,v=value:p.update(version="s2b-inference-platform/"+v))
    reject("闭包遗漏",lambda p:p["rtl_sources"].pop())
    reject("闭包重复",lambda p:p["rtl_sources"].append(p["rtl_sources"][0]))
    reject("时钟降低",lambda p:p.update(clock_hz=25000000))
    reject("physical漂移",lambda p:p.update(physical_interface="s2b-physical-candidate/0.1.3"))
    for name,path,before,after in (
        ("输入geometry误用旧latched",ENGINE,"input_geometry_plane <= {32'd0, input_height} * {32'd0, input_width};","input_geometry_plane <= {32'd0, input_height_latched} * {32'd0, input_width_latched};"),
        ("输入geometry丢高32",ENGINE,"input_geometry_plane <= {32'd0, input_height} * {32'd0, input_width};","input_geometry_plane <= {32'd0, 32'(input_height * input_width)};"),
        ("输入geometry错用C乘H",ENGINE,"feature_geometry_plane = input_geometry_plane;","feature_geometry_plane = input_element_plane;"),
        ("START误用旧latched",ENGINE,"input_element_plane <= {32'd0, input_channels} * {32'd0, input_height};","input_element_plane <= {32'd0, input_channels_latched} * {32'd0, input_height_latched};"),
        ("START丢高32",ENGINE,"input_element_plane <= {32'd0, input_channels} * {32'd0, input_height};","input_element_plane <= {32'd0, 32'(input_channels * input_height)};"),
        ("geometry错加",ENGINE,"output_geometry_plane <= {32'd0, output_height} * {32'd0, output_width};","output_geometry_plane <= {32'd0, output_height} + {32'd0, output_width};"),
        ("额外周期",ENGINE,"state <= ST_VALIDATE;","state <= ST_IDLE;"),
        ("丢高位拒绝",ENGINE,"(input_element_plane[63:32] != 32'd0)","(input_element_plane[63:32] != 32'd0 && 1'b0)"),
        ("冻结tuple低位alias",QUERY,"frozen_spatial_plane_lookup({source0_channels, source0_height, source0_width})","frozen_spatial_plane_lookup({source0_channels[15:0], source0_height[15:0], source0_width[15:0]})"),
        ("冻结plane错误",QUERY,"frozen_spatial_plane_lookup = 32'd10816;","frozen_spatial_plane_lookup = 32'd10817;"),
        ("冻结丢row",QUERY,"output_y * source0_width + output_x;","32'd0 + output_x;"),
        ("旧Tcl版本","vivado/s2b_inference_platform.tcl","variable version 0.1.13","variable version 0.1.12"),
        ("冻结原件自报SHA","src/s2a_network_backend.sv","module s2a_network_backend (","module bad_backend (")):
        if name=="冻结plane错误":
            before="96'h000000200000006800000068: "+before
            after="96'h000000200000006800000068: "+after
        reject(name,lambda p,f=path,b=before,a=after:source(p,f,b,a))
    return records

def math_proof():
    """独立无限精度计算原节点模域，包含高32溢出和三因子超64位。"""
    rng=random.Random(SEED);u32=(1<<32)-1;u64=(1<<64)-1
    edge=(0,1,2,255,256,4608,65535,65536,(1<<31)-1,1<<31,u32)
    values=list(itertools.product(edge,repeat=3))+[tuple(rng.getrandbits(32) for _ in range(3)) for _ in range(50000)]
    for c,h,w in values:
        cached=(c*h)&u64
        # 新空间缓存对全部unsigned32因子精确；channel与base仍在原模64域。
        spatial=h*w
        assert spatial<=u64 and spatial==((h*w)&u64)
        assert cached==c*h
        assert ((c*h)&u32)*w==(cached&u32)*w
        assert (c*h>>32!=0 or (((c*h)&u32)*w)>>32!=0)==(cached>>32!=0 or ((cached&u32)*w)>>32!=0)
        for ch,y,x,base in ((u32,u32,u32,u32),(17,31,63,0xFFFFF000)):
            assert (base+((ch*h+y)*w+x))&u64==(base+ch*((h*w)&u64)+y*w+x)&u64
    count=0
    for c,h,w in SHAPES:
        for ch in range(c):
            for y in range(h):
                for x in range(w):
                    assert (((ch*h+y)*w+x)&u32)==((ch*(h*w)+y*w+x)&u32)
                    count+=1
    ring=list(itertools.product(edge,repeat=4))+[tuple(rng.getrandbits(32) for _ in range(4)) for _ in range(50000)]
    for ch,h,w,y in ring:
        x=rng.getrandbits(32)
        assert (((ch*h+y)*w+x)&u32)==((ch*((h*w)&u32)+y*w+x)&u32)
    return dict(status="PASS_MATH_ONLY",seed=SEED,register_vectors=len(values),input_geometry_vectors=len(values),frozen_shapes=SHAPES,exhaustive_frozen_coordinates=count,mod32_vectors=len(ring))

def cache_monitor():
    """仅从真实START握手与reset/abort读候选内部寄存器，不强制内部状态。"""
    return """
integer s15_starts=0,s15_raw_differences=0,s15_clears=0,s15_holds=0;
logic s15_start,s15_clear;
logic [63:0] s15_input,s15_output,s15_geometry,s15_old_input,s15_old_output,s15_old_geometry,s15_hw,s15_old_hw;
always @(posedge clk) begin
 s15_clear=hard_reset || abort;
 s15_start=!s15_clear && start_valid && start_ready;
 s15_input={32'd0,input_channels}*{32'd0,input_height};
 s15_output={32'd0,output_channels}*{32'd0,output_height};
 s15_geometry={32'd0,output_height}*{32'd0,output_width};
 s15_hw={32'd0,input_height}*{32'd0,input_width};
 s15_old_hw=u_candidate.input_geometry_plane;
 s15_old_input=u_candidate.input_element_plane;
 s15_old_output=u_candidate.output_element_plane;
 s15_old_geometry=u_candidate.output_geometry_plane;
 if(s15_start && (input_channels!=u_candidate.input_channels_latched || input_height!=u_candidate.input_height_latched || output_channels!=u_candidate.output_channels_latched || output_height!=u_candidate.output_height_latched || output_width!=u_candidate.output_width_latched || input_width!=u_candidate.input_width_latched))s15_raw_differences++;
 #1;
 if(s15_clear)begin
  if(u_candidate.input_geometry_plane!==64'd0 || u_candidate.input_element_plane!==64'd0 || u_candidate.output_element_plane!==64'd0 || u_candidate.output_geometry_plane!==64'd0)$fatal(1,"S15 reset/abort缓存未清零");
  s15_clears++;
 end else if(s15_start)begin
  if(u_candidate.input_geometry_plane!==s15_hw || u_candidate.input_element_plane!==s15_input || u_candidate.output_element_plane!==s15_output || u_candidate.output_geometry_plane!==s15_geometry)$fatal(1,"S15 START未登记本拍完整raw64位参数");
  s15_starts++;
 end else begin
  if(u_candidate.input_geometry_plane!==s15_old_hw || u_candidate.input_element_plane!==s15_old_input || u_candidate.output_element_plane!==s15_old_output || u_candidate.output_geometry_plane!==s15_old_geometry)$fatal(1,"S15非START缓存保持失败");
  s15_holds++;
 end
end
"""

def boundary_bench(names,small):
    """保留原20状态、横纵tile、通道组、packed lane和响应错误公开差分。"""
    text=previous.boundary_bench(names,small)
    directed="""
reset_dut;defaults;
for(integer i=0;i<32;i++)begin
 input_batch_count=2;
 input_channels=32'hffffffff-32'(i);input_height=32'h80000000+32'(i);
 output_channels=32'hfffffffe-32'(i);output_height=32'h80000001+32'(i);output_width=32'hffffffff-32'(i);
 start_dut;tick;
 if(!result_valid || result_error_code!==3'd1)$fatal(1,"S15连续START首分支错误优先失败");
 result_ready=1;tick;result_ready=0;
end
reset_dut;defaults;
for(integer i=0;i<8;i++)begin
 input_batch_count=2;
 case(i)
  0:begin input_height=0;input_width=0;end
  1:begin input_height=0;input_width=32'hffffffff;end
  2:begin input_height=32'hffffffff;input_width=0;end
  3:begin input_height=1;input_width=32'hffffffff;end
  4:begin input_height=32'hffffffff;input_width=1;end
  5:begin input_height=32'hffffffff;input_width=32'hffffffff;end
  6:begin input_height=32'h80000000;input_width=32'hffffffff;end
  7:begin input_height=65536;input_width=65536;end
 endcase
 start_dut;tick;
 if(!result_valid || result_error_code!==3'd1)$fatal(1,"S15任意H/W登记或首错优先失败");
 result_ready=1;tick;result_ready=0;
end
reset_dut;defaults;start_dut;buffer_owner_pl=0;tick;
if(!result_valid || result_error_code!==3'd1)$fatal(1,"S15 VALIDATE未实时读取owner");
result_ready=1;tick;result_ready=0;
reset_dut;defaults;
input_channels=2;input_height=32'h80000000;input_width=2;kernel_height=1;kernel_width=1;
input_length_bytes=0;input_base_address=32'hffffffff;start_dut;tick;
if(!result_valid || result_error_code!==3'd3)$fatal(1,"S15高32溢出BAD_LENGTH优先失败");
result_ready=1;tick;result_ready=0;
reset_dut;defaults;
if(s15_starts<40 || s15_raw_differences<32 || s15_clears<40 || s15_holds==0)$fatal(1,"S15登记顺序覆盖不足");
$display("PASS S15_START_CACHE starts=%0d raw_differences=%0d clears=%0d holds=%0d directed=42",s15_starts,s15_raw_differences,s15_clears,s15_holds);
"""
    marker=' $display("PASS CONV_VALIDATION'
    assert text.count(marker)==1
    return text.replace(marker,directed+marker).replace("endmodule",cache_monitor()+"\nendmodule")

def frozen_vectors(model,ports):
    """使用旧独立数学oracle，完整96位tuple失配只提升为原BAD_ARGUMENT。"""
    original=route.oracle
    def oracle(v,raw):
        """冻结先验覆盖完整C/H/W，合法坐标和动态-128仍由旧oracle核验。"""
        result=original(v,raw)
        mismatch=any(tuple(v[f"source{s}_{k}"] for k in ("channels","height","width")) not in SHAPES for s in range(2 if v["source_count"]==2 else 1))
        return (1,*result[1:]) if mismatch else result
    route.oracle=oracle
    try:return route.vectors(model,ports)
    finally:route.oracle=original

def frozen_bench(model,ports):
    """S14与S15均实际启用私有参数1；query全空间独立NCHW黄金照旧。"""
    text=route.testbench(model,ports)
    for before,after in (("s2a_route_engine dut_old","s2b_route_engine_s14 #(.FROZEN_ROUTE_SHAPES(1)) dut_old"),("s2b_route_engine dut_new","s2b_route_engine #(.FROZEN_ROUTE_SHAPES(1)) dut_new"),("int8_route_query q_qo","s2b_route_query_s14 #(.FROZEN_ROUTE_SHAPES(1)) q_qo"),("s2b_route_query q_qn","s2b_route_query #(.FROZEN_ROUTE_SHAPES(1)) q_qn"),("qo_error_code!=0||qn_error_code!=1","qo_error_code!=1||qn_error_code!=1")):
        assert before in text
        text=text.replace(before,after)
    return text

def main():
    """每次attempt独占子目录；单job/单线程编译，全部失败及原生返回码保留。"""
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("all","static","feature","output","boundary","regressions","frozen","layer0"),default="all")
    parser.add_argument("--attempt",default="r01")
    parser.add_argument("--toolchain",type=Path,default=Path("D:/FPGA_S2A_MSYS2_20261001/env"))
    args=parser.parse_args()
    if not re.fullmatch(r"r[0-9]{2}",args.attempt):parser.error("attempt字面值错误")
    bases=[]
    for parent in (ROOT/"tmp/2B/S2B-T17",ROOT/"report/evidence/S2B-T17"):
        parent=previous.exact_directory(parent);base=parent/RUN_ID
        if not base.exists():base.mkdir()
        else:base=previous.exact_directory(base)
        target=base/(args.mode+"_"+args.attempt)
        if target.exists():parser.error("已有attempt不覆盖")
        target.mkdir();bases.append(target)
    work,evidence=bases;started=time.monotonic();code=1
    report=dict(schema_version=1,task_id="S2B-T17-S15",run_id=RUN_ID,mode=args.mode,attempt=args.attempt,status="FAIL",source_commit=BASELINE,observed_head_at_start=previous.git("rev-parse","HEAD").decode().strip(),runs=[],limitations=["仅受影响功能G1；不代表G2、50MHz STA、PNR、109整网或实板。","输出地址与feature组合受控夹具只证明登记等式条件域；公开START/PRE由boundary及完整layer0另外验证。","未启动Vivado/硬件；S13的实际STA FAIL及监护BLOCKED仍保留。"])
    try:
        checker=support.load_checker();bindings=checker.check_static(ROOT);static=dict(bindings)
        for path in (RUNNER,previous.RUNNER,output.RUNNER,validation.RUNNER,feature.RUNNER,support.RUNNER,geometry.RUNNER,route.RUNNER,support.MODEL,"sim/tb_s2a_t66_candidate_blackbox.sv","verification/s1_t02_d2_int8_forward.py"):
            bindings[path]=sha(checker.exact_file(ROOT/path))
        report["source_sha256_pre"]=bindings
        report["frozen14_sha256"]={p:sha(ROOT/p) for p in checker.FROZEN_CORE_SHA256}
        assert report["frozen14_sha256"]==checker.FROZEN_CORE_SHA256
        snapshot=evidence/"source_snapshot";snapshot.mkdir()
        for path in bindings:
            target=snapshot/path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/path,target)
        report["contract"]=contract(checker);report["math_proof"]=math_proof()
        report["checker_negatives"]=checker_negatives(checker,work,static)
        report["output_mutants"]=output.mutants(checker,work,static)
        model=json.loads((ROOT/support.MODEL).read_text(encoding="utf-8"))
        assert sha(ROOT/support.MODEL)==support.MODEL_SHA
        tools=previous.exact_directory(args.toolchain/"mingw64/bin");make=previous.exact_directory(args.toolchain/"usr/bin")
        verilator=checker.exact_file(tools/"verilator_bin.exe")
        checker.exact_file(tools/"g++.exe");checker.exact_file(make/"make.exe")
        env=dict(os.environ,PATH=str(make)+os.pathsep+str(tools)+os.pathsep+os.environ.get("PATH",""),VERILATOR_ROOT=str(args.toolchain/"mingw64/share/verilator"),PYTHONUTF8="1")
        report["tool_versions"]=dict(python=sys.version,verilator=subprocess.check_output([str(verilator),"--version"],cwd=work,env=env,text=True,timeout=30).strip())
        def compile_test(name,top,rtl,bench,files=None,extra=None,timeout=1200):
            """实际源码快照和原始刺激保留在证据；编译缓存仅在tmp。"""
            wd=work/name;ed=evidence/name;wd.mkdir();ed.mkdir();source=wd/"source";source.mkdir()
            record=dict(name=name,runs=[],resource_preflight=previous.resource(checker,wd));report.setdefault("tests",[]).append(record)
            for path in rtl:shutil.copyfile(ROOT/path,source/Path(path).name)
            for path,payload in (files or {}).items():
                for directory in (wd,ed):(directory/path).write_text(payload,encoding="utf-8",newline="\n")
            for name0,payload in (extra or {}).items():
                (source/name0).write_text(payload,encoding="utf-8",newline="\n")
                (ed/name0).write_text(payload,encoding="utf-8",newline="\n")
            for directory in (wd,ed):(directory/(top+".sv")).write_text(bench,encoding="utf-8",newline="\n")
            command=[str(verilator),"--binary","--timing","--timescale","1ns/1ps","-Wall","-Wno-fatal","-j","1","--threads","1","--output-split","10000","--output-split-cfuncs","100","--top-module",top,"--Mdir","obj_dir","-MAKEFLAGS","PYTHON3='\""+sys.executable+"\"'","-CFLAGS","-D_GLIBCXX_USE_CXX11_ABI=0 -O1",*["source/"+Path(p).name for p in rtl],*["source/"+p for p in (extra or {})],top+".sv"]
            previous.execute("compile",command,wd,ed,env,record,900)
            sim=[str(checker.exact_file(wd/("obj_dir/V"+top+".exe")))]
            if name in ("feature","output"):sim.append("+VECTOR_PATH="+str(ed/"address_vectors.txt").replace("\\","/"))
            if name=="layer0":sim.extend("+T66_"+kind+"_PATH="+str(validation.FIXTURE/name0).replace("\\","/") for kind,name0 in zip(("INPUT","WEIGHT","GOLDEN"),validation.FIXED))
            return record,previous.execute("simulation",sim,wd,ed,env,record,timeout)
        if args.mode in ("all","feature"):
            data,proof=feature.vectors(model);report["feature_oracle"]=proof
            bench=feature.bench()
            inject="\n".join("u_dut.tile_origin_"+axis+" = $signed(64'(v_tile_start_"+axis+") * 64'(v_stride_"+axis+"_latched) - 64'(v_"+pad+"_latched));" for axis,pad in (("y","pad_top"),("x","pad_left")))
            bench=bench.replace("#1;\n",inject+"\n#1;\n")
            old=previous.git("show",feature.BASELINE+":"+ENGINE).decode("utf-8").replace("\r\n","\n").replace("module s2b_conv_tile_engine (","module s2b_conv_tile_engine_original (")
            record,text=compile_test("feature","tb_s2b_conv_feature_address",("src/s2a_network_descriptor_pkg.sv",ENGINE),bench,{"address_vectors.txt":data},{"s9_conv_tile_engine_original.sv":old})
            match=re.search(r"PASS S10_CONV_FEATURE_ADDRESS vectors=(\d+) end=(\d+) padding=(\d+) range=(\d+) request=(\d+)",text)
            assert match and int(match[1])==proof["vectors"]
            record["coverage"]=dict(zip(("vectors","end","padding","range","request"),map(int,match.groups())))
        if args.mode in ("all","output"):
            data,proof=output.vectors(model);report["output_oracle"]=proof
            old=previous.git("show",output.BASELINE+":"+ENGINE)
            assert hashlib.sha256(old).hexdigest()==output.OLD_SHA
            original=old.decode("utf-8").replace("\r\n","\n").replace("module s2b_conv_tile_engine (","module s2b_conv_tile_engine_original (")
            record,text=compile_test("output","tb_s2b_conv_output_address",("src/s2a_network_descriptor_pkg.sv",ENGINE),output.bench(),{"address_vectors.txt":data},{"s9_conv_tile_engine_original.sv":original})
            match=re.search(r"PASS S9_CONV_OUTPUT_ADDRESS vectors=(\d+) advance=(\d+) next_lane=(\d+) range=(\d+) request=(\d+)",text)
            assert match and int(match[1])==proof["vectors"]
            record["coverage"]=dict(zip(("vectors","advance","next_lane","range","request"),map(int,match.groups())))
        if args.mode in ("all","boundary"):
            names,data,small,proof=validation.vectors(model);report["boundary_oracle"]=proof
            record,text=compile_test("boundary","tb_s2b_conv_validation",validation.RTL,boundary_bench(names,small),{"validation_vectors.txt":data})
            match=re.search(r"PASS CONV_VALIDATION vectors=(\d+) cycles=(\d+) abort_mask=([a-fA-F0-9]+) reset_mask=([a-fA-F0-9]+) response_cases=24 raw80=1",text)
            assert match and int(match[1])==proof["vectors"] and int(match[3],16)==int(match[4],16)==0xfffff
            cache=re.search(r"PASS S15_START_CACHE starts=(\d+) raw_differences=(\d+) clears=(\d+) holds=(\d+) directed=42",text);assert cache
            record["coverage"]=dict(vectors=int(match[1]),cycles=int(match[2]),abort_mask=match[3],reset_mask=match[4],response_cases=24,cache=dict(zip(("starts","raw_differences","clears","holds"),map(int,cache.groups()))),public_traces=re.findall(r"S13_PUBLIC_TRACE.*",text),origin=re.findall(r"PASS S13_ORIGIN_INVARIANTS.*",text),tap=re.findall(r"PASS S13_TAP_REGRESSION.*",text))
        if args.mode in ("all","regressions"):
            declarations={kind:geometry.ports(ROOT/path) for kind,path in (("pool","src/s2a_maxpool_engine.sv"),("upsample","src/s2a_upsample_engine.sv"))}
            files={};coverage={}
            for kind in declarations:files[kind+"_vectors.dat"],coverage[kind]=geometry.vector_data(kind,declarations[kind],model)
            record,text=compile_test("geometry","tb_s2b_geometry_specialization",geometry.RTL,geometry.generate_tb(declarations),files)
            assert re.search(r"PASS GEOMETRY_SPECIALIZATION pool=(\d+) upsample=(\d+) cycles=(\d+) pool_abort=(\d+) upsample_abort=(\d+)",text)
            record["coverage"]=coverage;record["pass_lines"]=re.findall(r"PASS .*",text)
            ports=geometry.ports(ROOT/"src/s2a_route_engine.sv");data,coverage=route.vectors(model,ports)
            record,text=compile_test("route_generic","tb_s2b_route_specialization",route.RTL,route.testbench(model,ports),{"route_vectors.dat":data})
            match=re.search(r"PASS ROUTE_SPECIALIZATION cases=(\d+) queries=(\d+) cycles=(\d+) abort=(\d+) reset=(\d+)",text)
            assert match and int(match[1])==coverage["vectors"] and int(match[4])==int(match[5])==255
            record["coverage"]=coverage;record["actual_pass_fields"]=dict(zip(("cases","queries","cycles","abort","reset"),map(int,match.groups())))
        if args.mode in ("all","frozen"):
            ports=geometry.ports(ROOT/"src/s2a_route_engine.sv");data,coverage=frozen_vectors(model,ports)
            extra={}
            for path,module in ((QUERY,"s2b_route_query"),("src/s2b_route_engine.sv","s2b_route_engine")):
                old=previous.git("show",BASELINE+":"+path).decode("utf-8").replace("\r\n","\n").replace("module "+module,"module "+module+"_s14",1)
                if module=="s2b_route_engine":old=old.replace("s2b_route_query #","s2b_route_query_s14 #",1)
                extra[module+"_s14.sv"]=old
            record,text=compile_test("route_frozen","tb_s2b_route_specialization",(QUERY,"src/s2b_route_engine.sv"),frozen_bench(model,ports),{"route_vectors.dat":data},extra)
            match=re.search(r"PASS ROUTE_SPECIALIZATION cases=(\d+) queries=(\d+) cycles=(\d+) abort=(\d+) reset=(\d+)",text)
            assert match and int(match[1])==coverage["vectors"] and int(match[4])==int(match[5])==255
            record["coverage"]=coverage;record["frozen_shapes"]=SHAPES;record["explicit_parameter1_instances"]=4
            record["actual_pass_fields"]=dict(zip(("cases","queries","cycles","abort","reset"),map(int,match.groups())))
        if args.mode in ("all","layer0"):
            cpu=evidence/"cpu_layer0";cpu.mkdir()
            for name,(size,digest) in validation.FIXED.items():
                path=checker.exact_file(validation.FIXTURE/name);assert path.stat().st_size==size and sha(path)==digest
            report["cpu_layer0"]=validation.cpu_layer0(model,cpu,checker)
            record,text=compile_test("layer0","tb_s2b_conv_layer0",validation.RTL,validation.layer0_tb())
            assert text.count("PASS: T66 candidate blackbox sample0 layer0 full tensor matched T25; bytes=1384448 mismatches=0")==1
            match=re.search(r"bytes=(\d+) mismatches=0 input_reads=(\d+) weight_reads=(\d+) output_writes=(\d+) requests=(\d+) responses=(\d+) request_stalls=(\d+) response_stalls=(\d+) cycles=(\d+)",text);assert match
            record["coverage"]=dict(zip(("bytes","input_reads","weight_reads","output_writes","requests","responses","request_stalls","response_stalls","cycles"),map(int,match.groups())))
        report["source_sha256_post"]={p:sha(ROOT/p) for p in bindings}
        assert report["source_sha256_pre"]==report["source_sha256_post"]
        report["observed_head_at_end"]=previous.git("rev-parse","HEAD").decode().strip()
        report["status"]="PASS_S15_"+args.mode.upper()+"_G1_ONLY";code=0
    except Exception as error:report["error"]=str(error)
    report["elapsed_seconds"]=round(time.monotonic()-started,3)
    report["created_at_utc8"]=datetime.now(timezone(timedelta(hours=8))).isoformat()
    save(evidence/"validation.json",report)
    print(json.dumps(dict(status=report["status"],error=report.get("error"),evidence=str(evidence),seconds=report["elapsed_seconds"]),ensure_ascii=False),flush=True)
    return code

if __name__=="__main__":raise SystemExit(main())
