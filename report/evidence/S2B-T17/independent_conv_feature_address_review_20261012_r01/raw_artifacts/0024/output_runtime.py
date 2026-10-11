#!/usr/bin/env python3
"""S9完整CONV的组合全域差分；公开START周期及数值由既有runner单独验证。"""
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

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "3f24c94564d10103aaa00db07356f666b085f687"
OLD_SHA = "ea3e123327827a2d090a705bb7e364af29cf7e1088bc86c7bd54bf55e36df5fc"
ENGINE = "src/s2b_conv_tile_engine.sv"
RUNNER = "verification/test_s2b_conv_output_address_rtl.py"
SEED = 0x591117
U32 = (1 << 32)-1
U64 = (1 << 64)-1
INPUTS = ("output_group_base", "output_lane_index", "output_height_latched", "output_width_latched",
          "tile_start_y", "output_point_scan_y", "tile_start_x", "output_point_scan_x",
          "output_base_latched", "output_channels_latched", "group_lane_count",
          "output_point_index", "tile_point_count")


def oracle(v):
    """按旧NCHW定义先截32位，再完整无限精度嵌套乘加，最后仅按原64域取模。"""
    group, lane, h, w, ty, py, tx, px, base, oc, lanes, point, points = v
    c, y, x = (group+lane)&U32, (ty+py)&U32, (tx+px)&U32
    offset = ((c*h+y)*w+x)&U64
    address = (offset+base)&U64
    # S8现有长度生产值：前两因子低32乘W，结果64再零扩到128；不消费validation。
    elements = ((oc*h)&U32)*w
    bad = int(address>U32 or offset>=elements)
    action = 0 if lane>=lanes else 1 if point>=points else 2 if bad else 3
    return c, y, x, offset, address, bad, action, elements


def vectors(model):
    """独立固定种子、全32输入、手算反例及21冻结CONV窗口。"""
    rows = []
    categories = Counter()
    actions = Counter()
    manual = {}
    def add(kind, v):
        gold = oracle(v)
        rows.append((v, gold))
        categories[kind] += 1
        actions[str(gold[6])] += 1
        return gold
    edge = (0,1,2,7,8,13,65535,65536,1<<31,U32-1,U32)
    for c,h,w in itertools.product(edge,repeat=3):
        for lane,y,x,base in ((0,0,0,0),(7,U32,U32,U32),(U32,1,U32,1),(8,65536,65536,U32)):
            for lanes,point,points in ((8,0,64),(0,0,64),(U32,U32,64)):
                add("boundary_consumed_and_unconsumed",(c,lane,h,w,y,0,x,0,base,1,lanes,point,points))
    rng = random.Random(SEED)
    for i in range(100000):
        v = [rng.getrandbits(32) for _ in INPUTS]
        if i%3==0:
            v[1]=rng.randrange(8);v[10]=8;v[11]=rng.randrange(64);v[12]=64
        add("random_full_u32",tuple(v))
    shapes=[]
    for layer in model["layers"]:
        if layer["op"]!="convolutional":
            continue
        _,oc,h,w=layer["output_shape_nchw"]
        assert 0<oc<=512 and 0<h<=208 and 0<w<=208
        shapes.append({"layer_index":layer["layer_index"],"shape":layer["output_shape_nchw"]})
        for c,y,x in itertools.product((0,oc-1),(0,h-1),(0,w-1)):
            gold=add("model_corner_last_u32_address",(c-c%8,c%8,h,w,y-y%8,y%8,x-x%8,x%8,U32-oc*h*w+1,oc,8,0,64))
            assert gold[4]<=U32 and gold[3]<oc*h*w
        for _ in range(200):
            c,y,x=rng.randrange(oc),rng.randrange(h),rng.randrange(w)
            add("model_coordinate",(c-c%8,c%8,h,w,y-y%8,y%8,x-x%8,x%8,0,oc,8,0,64))
    cases={
        "ordinary_manual":(8,3,13,13,8,4,8,4,100,32,8,0,64),
        "channel33_original_wrap":(U32,1,1,1,0,0,0,0,0,1,8,0,64),
        "coordinate33_original_wrap":(0,0,1,1,U32,1,U32,1,0,1,8,0,64),
        "offset64_original_wrap":(1<<31,0,65536,131072,0,0,0,0,0,1,8,0,64),
        "address64_original_wrap":(2,0,1<<31,U32,0,0,U32,0,1,1,8,0,64),
        "low32_only_alias":(1,0,65536,65536,0,0,0,0,0,2,8,0,64),
        "base33_carry":(0,0,1,2,0,0,1,0,U32,1,8,0,64),
    }
    for name,v in cases.items():
        gold=add("manual",v)
        manual[name]={"input":v,"expected":gold}
        add("manual_unconsumed_lane",v[:10]+(0,0,64))
        add("manual_unconsumed_point",v[:11]+(64,64))
    assert manual["ordinary_manual"]["expected"][3]==2027
    assert manual["channel33_original_wrap"]["expected"][0]==0
    assert manual["offset64_original_wrap"]["expected"][3]==0
    assert manual["address64_original_wrap"]["expected"][4]==0
    assert manual["low32_only_alias"]["expected"][3]==1<<32
    assert manual["base33_carry"]["expected"][4]==1<<32
    text="\n".join(" ".join(f"{n:x}" for n in (*v,*gold)) for v,gold in rows)+"\n"
    return text,{"seed":SEED,"seed_hex":hex(SEED),"vectors":len(rows),"categories":dict(categories),
                 "branch_counts":dict(actions),"manual":manual,"model_conv_shapes":shapes,
                 "scope":"组合内部受控输入涵盖通用32位域，时钟保持0，不代表公开START可达轨迹。",
                 "oracle":"原嵌套NCHW无限精度整数，仅原C/Y/X及offset/address节点取模；不读取候选因式分解公式。"}


def bench():
    """解析完整原公共端口，只受控赋值组合依赖寄存器；不force状态或启动事务。"""
    header=(ROOT/ENGINE).read_text(encoding="utf-8").split(");",1)[0]
    ports=re.findall(r"\b(input|output)\s+logic\s*((?:signed\s*)?(?:\[[^\]]+\])?)\s*(\w+)",header)
    conn=",".join(f".{n}({'clk' if n=='clk' else chr(39)+'0' if d=='input' else ''})" for d,w,n in ports)
    decl="\n".join(f"logic [31:0] v_{n};" for n in INPUTS)
    names=("c","y","x","offset","address","bad","action","elements")
    gold="\n".join(f"logic [{31 if n in ('c','y','x') else 1 if n=='action' else 0 if n=='bad' else 63}:0] gold_{n};" for n in names)
    assigns="\n".join(f"{instance}.{n}=v_{n};" for instance in ("u_old","u_dut") for n in INPUTS)
    checks=[]
    for inst in ("u_old","u_dut"):
        for signal,key in (("output_channel_current","c"),("output_global_y","y"),("output_global_x","x"),
                           ("output_byte_offset_wide","offset"),("output_address_wide","address")):
            checks.append(f'if({inst}.{signal} !== gold_{key}) $fatal(1,"组合字段{inst}.{signal} case=%0d",count);')
        checks.append(f'if({inst}.output_elements_wide !== {{64\'d0,gold_elements}}) $fatal(1,"组合长度域 case=%0d",count);')
        checks.append(f'if((({inst}.output_address_wide>64\'hFFFFFFFF)||({inst}.output_byte_offset_wide>={inst}.output_elements_wide)) !== gold_bad) $fatal(1,"原范围判据 case=%0d",count);')
        checks.append(f'if(action({inst}.output_lane_index,{inst}.group_lane_count,{inst}.output_point_index,{inst}.tile_point_count,(({inst}.output_address_wide>64\'hFFFFFFFF)||({inst}.output_byte_offset_wide>={inst}.output_elements_wide))) !== gold_action) $fatal(1,"未消费分支次序 case=%0d",count);')
    fmt=" ".join("%h" for _ in range(len(INPUTS)+len(names)))+"\\n"
    args=",".join(["v_"+n for n in INPUTS]+["gold_"+n for n in names])
    return f'''// 完整旧/新CONV模块组合锥对比；公开运行由独立START回归负责。
`timescale 1ns/1ps
module tb_s2b_conv_output_address;
logic clk=0;
{decl}
{gold}
s2b_conv_tile_engine_original u_old ({conn});
s2b_conv_tile_engine u_dut ({conn});
function automatic logic [1:0] action(input logic[31:0] lane,lanes,point,points,input logic bad);
begin if(lane>=lanes) action=0;else if(point>=points)action=1;else if(bad)action=2;else action=3;end
endfunction
integer fd,scanned,count=0;integer branch_count[0:3]='{{default:0}};string vector_path;
initial begin
 if(!$value$plusargs("VECTOR_PATH=%s",vector_path))$fatal(1,"精确向量路径缺失");
 fd=$fopen(vector_path,"r");if(fd==0)$fatal(1,"向量缺失");
 while(!$feof(fd))begin
  scanned=$fscanf(fd,"{fmt}",{args});
  if(scanned=={len(INPUTS)+len(names)})begin
   {assigns}
   #1;
   {"\n".join(checks)}
   branch_count[gold_action]++;count++;
  end else if(scanned!=-1)$fatal(1,"向量字段不足");
 end
 $fclose(fd);$display("PASS S9_CONV_OUTPUT_ADDRESS vectors=%0d advance=%0d next_lane=%0d range=%0d request=%0d",count,branch_count[0],branch_count[1],branch_count[2],branch_count[3]);$finish;
end
endmodule
'''


def mutants(checker,work,bindings):
    """独立固定派生规则拒绝语义篡改，即使篡改者同步自报SHA和替换清单。"""
    fixture=work/"offset_mutants";fixture.mkdir()
    for p in bindings:
        target=fixture/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,target)
    profile_path=fixture/"board/s2b_inference_platform.json"
    profile_original=json.loads(profile_path.read_text(encoding="utf-8"))
    original=(ROOT/ENGINE).read_text(encoding="utf-8")
    cases=(
        ("丢offset高位", "output_channel_plane_offset + output_row_offset +", "{32'd0, output_channel_plane_offset[31:0]} + {32'd0, output_row_offset[31:0]} +"),
        ("错误33位通道carry", "output_channel_plane_offset = {32'd0, output_channel_current} * output_geometry_plane;", "output_channel_plane_offset = ({32'd0, output_group_base} + {32'd0, output_lane_index}) * output_geometry_plane;"),
        ("错误65位addresscarry拒绝", "(output_address_wide > 64'h0000_0000_FFFF_FFFF)", "(({1'b0, output_byte_offset_wide} + {33'd0, output_base_latched}) > 65'h0000_0000_FFFF_FFFF)"),
        ("丢row", "output_channel_plane_offset + output_row_offset +", "output_channel_plane_offset + 64'd0 +"),
        ("丢x", "                                  {32'd0, output_global_x};", "                                  64'd0;"),
        ("错误plane", "output_geometry_plane = {32'd0, output_height_latched} * {32'd0, output_width_latched};", "output_geometry_plane = {32'd0, output_height_latched} + {32'd0, output_width_latched};"),
        ("错误signed扩展", "output_channel_plane_offset = {32'd0, output_channel_current} * output_geometry_plane;", "output_channel_plane_offset = $signed(output_channel_current) * $signed(output_geometry_plane);"),
        ("非法低32alias", "logic [63:0] output_byte_offset_wide;", "logic [31:0] output_byte_offset_wide;"),
    )
    records=[]
    for label,before,after in cases:
        assert original.count(before)==1,label
        target=fixture/ENGINE;target.write_text(original.replace(before,after),encoding="utf-8",newline="\n")
        profile=copy.deepcopy(profile_original)
        item=next(i for i in profile["source_derivation"]["derived_sources"] if i["path"]==ENGINE)
        item["sha256"]=support.sha(target)
        # 自报新增替换同样不能覆盖检查器内独立固定允许差异。
        item["replacements"].append([before,after])
        profile_path.write_text(json.dumps(profile,ensure_ascii=False,indent=2),encoding="utf-8")
        try:checker.check_static(fixture)
        except (ValueError,KeyError,TypeError,OSError) as exc:records.append({"name":label,"status":"REJECTED","reason":str(exc),"mutant_sha256":support.sha(target)})
        else:raise ValueError("语义反例未拒绝："+label)
    return records


def main():
    """独占缓存与新证据运行；功能PASS不代表G2、综合或实板。"""
    parser=argparse.ArgumentParser();parser.add_argument("--run-id",required=True)
    parser.add_argument("--toolchain",type=Path,default=Path("D:/FPGA_S2A_MSYS2_20261001/env"));args=parser.parse_args()
    if not re.fullmatch(r"conv_output_address_20261011_r\d+",args.run_id):parser.error("RunId不符")
    cache=ROOT/"tmp/2B/S2B-T17/s10_conv_g1_20261011_r01"
    evidence=ROOT/"report/evidence/S2B-T17"/args.run_id
    if not cache.is_dir() or not evidence.parent.is_dir():parser.error("精确父目录缺失")
    work=cache/args.run_id
    if work.exists() or evidence.exists() and any(evidence.iterdir()):parser.error("RunId已存在内容，禁止覆盖")
    work.mkdir();evidence.mkdir(exist_ok=True)
    report={"schema_version":1,"task_id":"S2B-T17-S9","run_id":args.run_id,"source_commit":BASELINE,"status":"FAIL","runs":[],
            "limitations":["组合受控输入不是公开START可达域；不force状态、不产生公开周期覆盖。",
                            "公开周期/abort-reset/owner及数值由原conv_validation boundary/layer0单独执行。",
                            "NOT_RUN_G2","NOT_RUN_STA","NOT_RUN_109_NETWORK","NOT_RUN_BOARD"]}
    started=time.monotonic()
    try:
        assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()==BASELINE
        checker=support.load_checker();bindings=checker.check_static(ROOT)
        static_bindings=dict(bindings)
        bindings.update({p:support.sha(ROOT/p) for p in (RUNNER,support.RUNNER,support.MODEL)})
        report["source_sha256_pre"]=bindings
        snapshot=evidence/"source_snapshot";snapshot.mkdir()
        for p in bindings:
            target=snapshot/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,target)
        report["frozen14_sha256"]={p:support.sha(ROOT/p) for p in checker.FROZEN_CORE_SHA256}
        assert report["frozen14_sha256"]==checker.FROZEN_CORE_SHA256
        old=subprocess.check_output(["git","show",BASELINE+":"+ENGINE],cwd=ROOT)
        assert hashlib.sha256(old).hexdigest()==OLD_SHA
        old_lf=old.decode("utf-8").replace("\r\n","\n")
        actual=(ROOT/ENGINE).read_text(encoding="utf-8")
        ff="    always_ff @(posedge clk) begin"
        assert old_lf[old_lf.index(ff):]==actual[actual.index(ff):]
        assert old_lf.split(");",1)[0]==actual.split(");",1)[0]
        report["ff_and_interface"]={"status":"IDENTICAL_LF_CONTENT","suffix_sha256":hashlib.sha256(actual[actual.index(ff):].encode()).hexdigest(),"old_git_sha256":OLD_SHA}
        assert support.sha(ROOT/support.MODEL)==support.MODEL_SHA
        text,proof=vectors(json.loads((ROOT/support.MODEL).read_text(encoding="utf-8")))
        report["math_oracle"]=proof
        report["checker_negatives"]=support.checker_negatives(checker,work,static_bindings)
        report["offset_mutants"]=mutants(checker,work,static_bindings)
        source=work/"source";source.mkdir()
        for p in ("src/s2a_network_descriptor_pkg.sv",ENGINE):shutil.copyfile(ROOT/p,source/Path(p).name)
        original_module=old_lf.replace("module s2b_conv_tile_engine (","module s2b_conv_tile_engine_original (")
        for directory in (source,evidence):(directory/"s9_conv_tile_engine_original.sv").write_text(original_module,encoding="utf-8",newline="\n")
        tb=bench()
        # 正式输入只有一份；仿真通过明确plusarg消费同一原始字节，避免缓存重复占用。
        (evidence/"address_vectors.txt").write_text(text,encoding="utf-8",newline="\n")
        for directory in (work,evidence):
            (directory/"tb_s2b_conv_output_address.sv").write_text(tb,encoding="utf-8",newline="\n")
        env=os.environ.copy();tools=args.toolchain/"mingw64/bin";make=args.toolchain/"usr/bin"
        verilator=checker.exact_file(tools/"verilator_bin.exe")
        env["PATH"]=str(make)+os.pathsep+str(tools)+os.pathsep+env.get("PATH","")
        env["VERILATOR_ROOT"]=str(args.toolchain/"mingw64/share/verilator");env["PYTHONUTF8"]="1"
        report["resource_preflight"]={"available_ram_bytes":psutil.virtual_memory().available,"disk_free_bytes":shutil.disk_usage(work).free,
            "heavy_processes":[{"pid":p.pid,"name":p.info["name"]} for p in psutil.process_iter(["name"]) if p.info["name"] and re.fullmatch(r"(?:vivado|verilator_bin|cc1plus|Vtb_.*)\.exe",p.info["name"],re.I)],
            "jobs":1,"threads":1,"rss_limit_bytes":1610612736,"compile_timeout_seconds":600,"simulation_timeout_seconds":180}
        if report["resource_preflight"]["heavy_processes"] or report["resource_preflight"]["available_ram_bytes"]<2147483648 or report["resource_preflight"]["disk_free_bytes"]<1073741824:raise ValueError("实际重型槽或资源不可用")
        report["tool_versions"]={"python":sys.version,"verilator":subprocess.check_output([str(verilator),"--version"],cwd=work,env=env,text=True).strip()}
        cmd=[str(verilator),"--binary","--timing","--timescale","1ns/1ps","-Wall","-Wno-fatal","-j","1","--threads","1","--output-split","10000","--output-split-cfuncs","100","--top-module","tb_s2b_conv_output_address","--Mdir","obj_dir","-MAKEFLAGS","PYTHON3='\""+sys.executable+"\"'","-CFLAGS","-D_GLIBCXX_USE_CXX11_ABI=0 -O1","source/s2a_network_descriptor_pkg.sv","source/s9_conv_tile_engine_original.sv","source/s2b_conv_tile_engine.sv","tb_s2b_conv_output_address.sv"]
        support.execute("compile",cmd,work,evidence,env,report,600)
        support.execute("simulation",[str(work/"obj_dir/Vtb_s2b_conv_output_address.exe"),"+VECTOR_PATH="+str(evidence/"address_vectors.txt").replace("\\","/")],work,evidence,env,report,180)
        log=(evidence/"simulation.log").read_text(encoding="utf-8")
        marker=re.findall(r"PASS S9_CONV_OUTPUT_ADDRESS vectors=(\d+) advance=(\d+) next_lane=(\d+) range=(\d+) request=(\d+)",log)
        if len(marker)!=1 or int(marker[0][0])!=proof["vectors"]:raise ValueError("真实组合覆盖不足")
        assert [int(n) for n in marker[0][1:]]==[proof["branch_counts"].get(str(i),0) for i in range(4)]
        report["actual_coverage"]=dict(zip(("vectors","advance","next_lane","range","request"),map(int,marker[0])))
        report["source_sha256_post"]={p:support.sha(ROOT/p) for p in bindings}
        if report["source_sha256_post"]!=bindings:raise ValueError("验证期间源码变化")
        report["status"]="PASS_CONV_OUTPUT_ADDRESS_COMBINATIONAL_G1"
    except Exception as exc:
        report["error"]=repr(exc)
    finally:
        report["elapsed_seconds"]=round(time.monotonic()-started,3)
        (evidence/"validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":report["status"],"seconds":report["elapsed_seconds"],"coverage":report.get("actual_coverage"),"error":report.get("error")},ensure_ascii=False))
    return 0 if report["status"]=="PASS_CONV_OUTPUT_ADDRESS_COMBINATIONAL_G1" else 2


if __name__=="__main__":
    raise SystemExit(main())
