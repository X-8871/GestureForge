#!/usr/bin/env python3
"""S10完整旧新CONV组合地址差分；内部受控域不冒充公开START覆盖。"""
from __future__ import annotations
import argparse
from collections import Counter
import copy
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
import test_s2b_backend_coordinates_rtl as support

ROOT=Path(__file__).resolve().parents[1]
BASELINE="3f24c94564d10103aaa00db07356f666b085f687"
OLD_SHA="ea3e123327827a2d090a705bb7e364af29cf7e1088bc86c7bd54bf55e36df5fc"
ENGINE="src/s2b_conv_tile_engine.sv"
RUNNER="verification/test_s2b_conv_feature_address_rtl.py"
SEED=0x5A1710
U32=(1<<32)-1
U64=(1<<64)-1
INPUTS=("feature_scan_channel","input_height_latched","input_width_latched","tile_start_y",
        "stride_y_latched","feature_scan_y","pad_top_latched","tile_start_x","stride_x_latched",
        "feature_scan_x","pad_left_latched","input_base_latched","patch_height","patch_width",
        "feature_scan_index","patch_byte_count")
GOLD=("plane","y","x","bounds","offset","address","range","action","advance","aligned","strobe","row")


def signed64(value):
    """保持原64位二补码signed解释。"""
    value&=U64
    return value-(1<<64) if value&(1<<63) else value


def oracle(v):
    """独立旧嵌套NCHW整数定义；只在原节点取模，不引用候选plane表达式。"""
    c,h,w,ty,sy,fy,py,tx,sx,fx,px,base,ph,pw,index,count,state,rsp_valid,rsp_error=v
    plane=ph*pw
    y=signed64(ty*sy+fy-py) if plane and pw else 0
    x=signed64(tx*sx+fx-px) if plane and pw else 0
    bounds=int(bool(plane and pw and 0<=y<h and 0<=x<w))
    offset=(((c*h+(y&U64))&U64)*w+(x&U64))&U64 if bounds else 0
    address=(base+offset)&U64 if bounds else 0
    bad=int(address>U32)
    action=0 if index>=count else 1 if not bounds else 2 if bad else 3
    mapped=rsp_error if rsp_error in (0,1,2,6) else 6
    advance=int((state==1 and index<count and not bounds) or (state==2 and rsp_valid and mapped==0))
    row=(y*w)&U64 if bounds else 0
    return plane,y&U64,x&U64,bounds,offset,address,bad,action,advance,address&0xfffffffc,1<<(address&3),row


def vectors(model):
    """固定总量与独立种子，多域/手算/冻结21CONV代表窗口均明确计数。"""
    rows=[];categories=Counter();branches=Counter();manual={}
    def add(kind,v):
        gold=oracle(v);rows.append((v,gold));categories[kind]+=1;branches[str(gold[7])]+=1;return gold
    cases={
        "ordinary":(3,13,13,8,1,4,1,8,1,4,1,100,2,2,0,4,1,0,0),
        "negative_padding":(0,1,1,0,1,0,1,0,1,0,0,U32,1,1,0,1,1,0,0),
        "bit63_negative_low32_alias":(0,1,1,U32,U32,0,1,0,0,0,0,0,1,1,0,1,1,0,0),
        "bit32_positive_low32_alias":(0,1,1,65536,65536,0,0,0,0,0,0,0,1,1,0,1,1,0,0),
        "Y_equal_H":(0,U32,1,0,0,U32,0,0,0,0,0,0,1,1,0,1,1,0,0),
        "H_zero":(0,0,1,0,0,0,0,0,0,0,0,0,1,1,0,1,1,0,0),
        "W_zero":(0,1,0,0,0,0,0,0,0,0,0,0,1,1,0,1,1,0,0),
        "max_valid_Y_exact_row64":(0,U32,U32,0,0,U32-1,0,0,0,U32-1,0,0,1,1,0,1,1,0,0),
        "channel_terms_mod64_offset_zero":(1<<31,2,U32,0,0,1,0,0,0,1,0,0,1,1,0,1,1,0,0),
        "base_mod64_address_zero":(1<<31,2,U32,0,0,1,0,0,0,0,0,1,1,1,0,1,1,0,0),
        "low32_offset_alias_range":(1,65536,65536,0,0,0,0,0,0,0,0,0,1,1,0,1,1,0,0),
        "base33_range":(0,1,2,0,0,0,0,0,0,1,0,U32,1,1,0,1,1,0,0),
        "patch_gate_zero":(1,U32,U32,U32,U32,U32,U32,U32,U32,U32,U32,U32,0,1,0,1,1,0,0),
        "END_before_RANGE":(1,65536,65536,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0),
        "END_before_PADDING":(0,1,1,0,1,0,1,0,1,0,0,U32,1,1,1,1,1,0,0),
    }
    for name,v in cases.items():manual[name]={"input":v,"expected":add("manual",v)}
    assert manual["channel_terms_mod64_offset_zero"]["expected"][4]==0
    assert manual["base_mod64_address_zero"]["expected"][4]==U64
    assert manual["base_mod64_address_zero"]["expected"][5]==0
    assert manual["bit63_negative_low32_alias"]["expected"][1]==(1<<64)-(1<<33)
    assert manual["bit32_positive_low32_alias"]["expected"][1]==1<<32
    assert manual["max_valid_Y_exact_row64"]["expected"][11]==(U32-1)*U32
    for c,h,w in itertools.product((0,1,2,65536,1<<31,U32),repeat=3):
        add("C_H_W_boundaries",(c,h,w,0,0,0,0,0,0,0,0,U32,1,1,0,1,1,0,0))
    rng=random.Random(SEED)
    for _ in range(60000):add("random_full_u32",tuple([rng.getrandbits(32) for _ in INPUTS]+[rng.randrange(4),rng.randrange(2),rng.randrange(8)]))
    for _ in range(40000):
        c,h,w,base=[rng.getrandbits(32) for _ in range(4)]
        add("random_inbounds",(c,h,w,0,0,rng.randrange(h) if h else 0,0,0,0,rng.randrange(w) if w else 0,0,base,1,1,0,1,rng.randrange(4),rng.randrange(2),rng.randrange(8)))
    for _ in range(18000):
        v=[rng.getrandbits(32) for _ in INPUTS];v[3]=0;v[4]=0;v[5]=0;v[6]=rng.randrange(1,U32);v[12]=1;v[13]=1
        v[14]=0;v[15]=1;add("random_negative_padding",tuple(v+[rng.randrange(4),rng.randrange(2),rng.randrange(8)]))
    shapes=[]
    for layer in model["layers"]:
        if layer["op"]!="convolutional":continue
        _,c,h,w=layer["input_shape_nchw"];shapes.append({"layer_index":layer["layer_index"],"input_shape":layer["input_shape_nchw"]})
        for _ in range(100):add("frozen_model_coordinate",(rng.randrange(c),h,w,0,0,rng.randrange(h),0,0,0,rng.randrange(w),0,U32-c*h*w+1,1,1,0,1,1,0,0))
    for state,error in itertools.product(range(3),range(8)):
        v=list(cases["ordinary"]);v[-3:]=[state,1,error];add("advance_response_mapping",tuple(v))
    for state,gate in itertools.product(range(3),range(2)):
        v=list(cases["negative_padding"]);v[12]=gate;v[-3:]=[state,1,0];add("advance_patch_gate",tuple(v))
    assert len(rows)==120361 and len(shapes)==21
    text="\n".join(" ".join(f"{n:x}" for n in (*v,*gold)) for v,gold in rows)+"\n"
    return text,{"seed":SEED,"seed_hex":hex(SEED),"vectors":len(rows),"categories":dict(categories),"branch_counts":dict(branches),"manual":manual,"frozen_conv_shapes":shapes,"scope":"原内部寄存器/状态受控组合域，clk恒0；不是公开START可达轨迹或周期覆盖。","oracle":"独立旧嵌套式；不读取候选factorization。新row仅bounds内消费，未bounds默认0。"}


def bench():
    """完整引擎组合字段观测；内部驱动范围逐条登记，公开回归不得注入。"""
    header=(ROOT/ENGINE).read_text(encoding="utf-8").split(");",1)[0]
    ports=re.findall(r"\b(input|output)\s+logic\s*((?:signed\s*)?(?:\[[^\]]+\])?)\s*(\w+)",header)
    conn=",".join(f".{n}({'clk' if n=='clk' else 'v_rsp_valid' if n=='backend_rsp_valid' else 'v_rsp_error' if n=='backend_rsp_error' else chr(39)+'0' if d=='input' else ''})" for d,w,n in ports)
    decl="\n".join(f"logic [31:0] v_{n};" for n in INPUTS)
    widths={"bounds":1,"range":1,"action":2,"advance":1,"aligned":32,"strobe":4}
    gold="\n".join(f"logic [{widths.get(n,64)-1}:0] gold_{n};" for n in GOLD)
    assigns="\n".join(f"{inst}.{n}=v_{n};" for inst in ("u_old","u_dut") for n in INPUTS)
    states="\n".join(f"case(v_state) 0:{inst}.state={inst}.ST_IDLE;1:{inst}.state={inst}.ST_FEATURE_SCAN;2:{inst}.state={inst}.ST_FEATURE_RESPONSE;default:{inst}.state={inst}.ST_WEIGHT_SCAN;endcase" for inst in ("u_old","u_dut"))
    checks=[]
    for inst in ("u_old","u_dut"):
        for signal,key in (("patch_plane_bytes","plane"),("feature_input_y","y"),("feature_input_x","x"),("feature_scan_in_bounds","bounds"),("feature_source_offset","offset"),("feature_source_address_wide","address"),("feature_scan_advance","advance")):
            checks.append(f'if({inst}.{signal}!==gold_{key})$fatal(1,"组合字段{inst}.{signal} case=%0d",count);')
        checks.append(f'if(({inst}.feature_source_address_wide>64\'hFFFFFFFF)!==gold_range)$fatal(1,"原范围判据 case=%0d",count);')
        checks.append(f'if(action({inst}.feature_scan_index,{inst}.patch_byte_count,{inst}.feature_scan_in_bounds,({inst}.feature_source_address_wide>64\'hFFFFFFFF))!==gold_action)$fatal(1,"消费顺序 case=%0d",count);')
        checks.append(f'if(gold_action==3 && v_state==1)begin if({{{inst}.feature_source_address_wide[31:2],2\'b00}}!==gold_aligned || (4\'b0001<<{inst}.feature_source_address_wide[1:0])!==gold_strobe)$fatal(1,"请求对齐/strobe case=%0d",count);end')
    checks.append('if(u_dut.feature_row_offset!==gold_row)$fatal(1,"消费行精确64/未bounds默认0 case=%0d",count);')
    fmt=" ".join("%h" for _ in range(len(INPUTS)+3+len(GOLD)))+"\\n"
    args=",".join(["v_"+n for n in INPUTS]+["v_state","v_rsp_valid","v_rsp_error"]+["gold_"+n for n in GOLD])
    return f'''// 仅受控组合域：完整旧新模块、时钟恒0、无posedge；不属于公开事务覆盖。
`timescale 1ns/1ps
module tb_s2b_conv_feature_address;
logic clk=0;logic[1:0]v_state;logic v_rsp_valid;logic[2:0]v_rsp_error;
{decl}
{gold}
s2b_conv_tile_engine_original u_old ({conn});
s2b_conv_tile_engine u_dut ({conn});
function automatic logic[1:0]action(input logic[31:0]index,count,input logic bounds,bad);
begin if(index>=count)action=0;else if(!bounds)action=1;else if(bad)action=2;else action=3;end
endfunction
integer fd,scanned,count=0;integer branch_count[0:3]='{{default:0}};string vector_path;
initial begin
if(!$value$plusargs("VECTOR_PATH=%s",vector_path))$fatal(1,"精确向量路径缺失");
fd=$fopen(vector_path,"r");if(fd==0)$fatal(1,"向量缺失");
while(!$feof(fd))begin
scanned=$fscanf(fd,"{fmt}",{args});
if(scanned=={len(INPUTS)+3+len(GOLD)})begin
{assigns}
{states}
#1;
{"\n".join(checks)}
branch_count[gold_action]++;count++;
end else if(scanned!=-1)$fatal(1,"向量字段不足");
end
$fclose(fd);$display("PASS S10_CONV_FEATURE_ADDRESS vectors=%0d end=%0d padding=%0d range=%0d request=%0d",count,branch_count[0],branch_count[1],branch_count[2],branch_count[3]);$finish;
end
endmodule
'''


def mutants(checker,work,bindings):
    """自报SHA和替换仍须被独立固定规则真实拒绝。"""
    fixture=work/"feature_mutants";fixture.mkdir()
    for p in bindings:
        target=fixture/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,target)
    profile_path=fixture/"board/s2b_inference_platform.json";profile_original=json.loads(profile_path.read_text(encoding="utf-8"))
    original=(ROOT/ENGINE).read_text(encoding="utf-8")
    cases=(("bit63负坐标被误放行","(feature_input_y >= 64'sd0)","1'b1"),
           ("bit32坐标低位别名","(feature_input_y < $signed({32'd0, input_height_latched}))","(feature_input_y[31:0] < input_height_latched)"),
           ("plane错误加法","feature_geometry_plane = {32'd0, input_height_latched} * {32'd0, input_width_latched};","feature_geometry_plane = {32'd0, input_height_latched} + {32'd0, input_width_latched};"),
           ("channel丢高位","feature_source_offset = feature_channel_plane_offset + feature_row_offset +","feature_source_offset = {32'd0, feature_channel_plane_offset[31:0]} + feature_row_offset +"),
           ("row丢高位","logic [63:0] feature_row_offset;","logic [31:0] feature_row_offset;"),
           ("丢row","feature_source_offset = feature_channel_plane_offset + feature_row_offset +","feature_source_offset = feature_channel_plane_offset + 64'd0 +"),
           ("丢X","                                        feature_input_x[63:0];","                                        64'd0;"),
           ("错误65位carry拒绝","(feature_source_address_wide > 64'h0000_0000_FFFF_FFFF)","(({1'b0, feature_source_offset} + {33'd0, input_base_latched}) > 65'h0000_0000_FFFF_FFFF)"))
    records=[]
    for name,before,after in cases:
        assert original.count(before)==1,name
        target=fixture/ENGINE;target.write_text(original.replace(before,after),encoding="utf-8",newline="\n")
        profile=copy.deepcopy(profile_original);item=next(i for i in profile["source_derivation"]["derived_sources"] if i["path"]==ENGINE)
        item["sha256"]=support.sha(target);item["replacements"].append([before,after]);profile_path.write_text(json.dumps(profile,ensure_ascii=False,indent=2),encoding="utf-8")
        try:checker.check_static(fixture)
        except (ValueError,KeyError,TypeError,OSError) as exc:records.append({"name":name,"status":"REJECTED","reason":str(exc),"mutant_sha256":support.sha(target)})
        else:raise ValueError("语义反例未拒绝："+name)
    return records


def main():
    """真实完整引擎编译与组合域回归，失败原件保留，单任务缓存独占。"""
    parser=argparse.ArgumentParser();parser.add_argument("--run-id",required=True)
    parser.add_argument("--toolchain",type=Path,default=Path("D:/FPGA_S2A_MSYS2_20261001/env"));args=parser.parse_args()
    if not re.fullmatch(r"conv_feature_address_20261011_r\d+",args.run_id):parser.error("RunId不符")
    cache=ROOT/"tmp/2B/S2B-T17/s10_conv_g1_20261011_r01";evidence=ROOT/"report/evidence/S2B-T17"/args.run_id;work=cache/args.run_id
    if not cache.is_dir() or not evidence.parent.is_dir() or work.exists() or evidence.exists():parser.error("精确父目录/新RunId不符")
    work.mkdir();evidence.mkdir();started=time.monotonic()
    report={"schema_version":1,"task_id":"S2B-T17-S10","run_id":args.run_id,"source_commit":BASELINE,"status":"FAIL","runs":[],"limitations":["内部寄存器/状态受控组合域，clk恒0；不作公开START可达域/周期证明。","公开START/owner/backpressure/abort-reset/数值由原boundary/layer0另跑。","G2/STA/G3/新109全网NOT_RUN"]}
    try:
        assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()==BASELINE
        checker=support.load_checker();static=checker.check_static(ROOT);bindings=dict(static)
        bindings.update({p:support.sha(ROOT/p) for p in (RUNNER,support.RUNNER,support.MODEL)})
        report["source_sha256_pre"]=bindings;snapshot=evidence/"source_snapshot";snapshot.mkdir()
        for p in bindings:
            target=snapshot/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,target)
        report["frozen14_sha256"]={p:support.sha(ROOT/p) for p in checker.FROZEN_CORE_SHA256};assert report["frozen14_sha256"]==checker.FROZEN_CORE_SHA256
        old=subprocess.check_output(["git","show",BASELINE+":"+ENGINE],cwd=ROOT);assert hashlib.sha256(old).hexdigest()==OLD_SHA
        old_lf=old.decode("utf-8").replace("\r\n","\n");actual=(ROOT/ENGINE).read_text(encoding="utf-8");ff="    always_ff @(posedge clk) begin"
        assert old_lf[old_lf.index(ff):]==actual[actual.index(ff):] and old_lf.split(");",1)[0]==actual.split(");",1)[0]
        report["ff_and_interface"]={"status":"IDENTICAL_LF_CONTENT","suffix_sha256":hashlib.sha256(actual[actual.index(ff):].encode()).hexdigest(),"old_git_sha256":OLD_SHA}
        assert support.sha(ROOT/support.MODEL)==support.MODEL_SHA
        text,proof=vectors(json.loads((ROOT/support.MODEL).read_text(encoding="utf-8")));report["math_oracle"]=proof
        report["checker_negatives"]=support.checker_negatives(checker,work,static)
        fixture=work/"checker_fixture";profile_path=fixture/"board/s2b_inference_platform.json";profile=json.loads(profile_path.read_text(encoding="utf-8"));profile["version"]="s2b-inference-platform/0.1.9";profile_path.write_text(json.dumps(profile,ensure_ascii=False),encoding="utf-8")
        try:checker.check_static(fixture)
        except ValueError as exc:report["checker_negatives"].append({"name":"旧profile0.1.9","status":"REJECTED","reason":str(exc)})
        else:raise ValueError("旧S9 profile未拒绝")
        report["feature_mutants"]=mutants(checker,work,static)
        source=work/"source";source.mkdir()
        for p in ("src/s2a_network_descriptor_pkg.sv",ENGINE):shutil.copyfile(ROOT/p,source/Path(p).name)
        original=old_lf.replace("module s2b_conv_tile_engine (","module s2b_conv_tile_engine_original (")
        for directory in (source,evidence):(directory/"s9_conv_tile_engine_original.sv").write_text(original,encoding="utf-8",newline="\n")
        tb=bench();(evidence/"address_vectors.txt").write_text(text,encoding="utf-8",newline="\n")
        for directory in (work,evidence):(directory/"tb_s2b_conv_feature_address.sv").write_text(tb,encoding="utf-8",newline="\n")
        env=os.environ.copy();tools=args.toolchain/"mingw64/bin";make=args.toolchain/"usr/bin";verilator=checker.exact_file(tools/"verilator_bin.exe")
        env["PATH"]=str(make)+os.pathsep+str(tools)+os.pathsep+env.get("PATH","");env["VERILATOR_ROOT"]=str(args.toolchain/"mingw64/share/verilator");env["PYTHONUTF8"]="1"
        heavy=[{"pid":p.pid,"name":p.info["name"]} for p in psutil.process_iter(["name"]) if p.info["name"] and re.fullmatch(r"(?:vivado|verilator_bin|cc1plus|Vtb_.*)\.exe",p.info["name"],re.I)]
        report["resource_preflight"]={"available_ram_bytes":psutil.virtual_memory().available,"disk_free_bytes":shutil.disk_usage(work).free,"heavy_processes":heavy,"jobs":1,"threads":1,"outer_rss_limit_bytes":1073741824,"cache_limit_bytes":314572800}
        assert not heavy and report["resource_preflight"]["available_ram_bytes"]>2147483648 and report["resource_preflight"]["disk_free_bytes"]>1073741824
        report["tool_versions"]={"python":sys.version,"verilator":subprocess.check_output([str(verilator),"--version"],cwd=work,env=env,text=True).strip()}
        cmd=[str(verilator),"--binary","--timing","--timescale","1ns/1ps","-Wall","-Wno-fatal","-j","1","--threads","1","--output-split","10000","--output-split-cfuncs","100","--top-module","tb_s2b_conv_feature_address","--Mdir","obj_dir","-MAKEFLAGS","PYTHON3='\""+sys.executable+"\"'","-CFLAGS","-D_GLIBCXX_USE_CXX11_ABI=0 -O1","source/s2a_network_descriptor_pkg.sv","source/s9_conv_tile_engine_original.sv","source/s2b_conv_tile_engine.sv","tb_s2b_conv_feature_address.sv"]
        support.execute("compile",cmd,work,evidence,env,report,600)
        support.execute("simulation",[str(work/"obj_dir/Vtb_s2b_conv_feature_address.exe"),"+VECTOR_PATH="+str(evidence/"address_vectors.txt").replace("\\","/")],work,evidence,env,report,180)
        log=(evidence/"simulation.log").read_text(encoding="utf-8");marker=re.findall(r"PASS S10_CONV_FEATURE_ADDRESS vectors=(\d+) end=(\d+) padding=(\d+) range=(\d+) request=(\d+)",log)
        assert len(marker)==1 and int(marker[0][0])==proof["vectors"] and [int(n) for n in marker[0][1:]]==[proof["branch_counts"].get(str(i),0) for i in range(4)]
        report["actual_coverage"]=dict(zip(("vectors","end","padding","range","request"),map(int,marker[0])))
        report["source_sha256_post"]={p:support.sha(ROOT/p) for p in bindings};assert report["source_sha256_post"]==bindings
        report["status"]="PASS_CONV_FEATURE_ADDRESS_COMBINATIONAL_G1"
    except Exception as exc:report["error"]=repr(exc)
    finally:
        report["elapsed_seconds"]=round(time.monotonic()-started,3);(evidence/"validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":report["status"],"seconds":report["elapsed_seconds"],"coverage":report.get("actual_coverage"),"error":report.get("error")},ensure_ascii=False))
    return 0 if report["status"]=="PASS_CONV_FEATURE_ADDRESS_COMBINATIONAL_G1" else 2


if __name__=="__main__":raise SystemExit(main())
