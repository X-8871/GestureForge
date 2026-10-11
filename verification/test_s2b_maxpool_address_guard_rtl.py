#!/usr/bin/env python3
"""验证S12冻结POOL常量实例、全域几何守卫及真实引擎每周期等价。"""
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
import test_s2b_geometry_specialization_rtl as engine
import test_s2b_backend_coordinates_rtl as backend

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "2257a450239ea19ef4e2ddf7b2833d44020f95e3"
SOURCE_BASELINE = "891f750045ce141a8152c96025da559ff1d3a321"
RUNNER = "verification/test_s2b_maxpool_address_guard_rtl.py"
SEED = 0x581011
U32 = (1 << 32)-1
INPUTS = ("input_base_address", "input_channels", "input_height", "input_width",
          "kernel_height", "kernel_width", "stride_y", "stride_x", "darknet_padding_parameter",
          "input_channel", "output_y", "output_x")


def oracle(v):
    """独立NCHW数学定义，使用无限精度整数及公开错误优先生成全部字段。"""
    base, channels, h, w, kh, kw, sy, sx, pad, ch, y, x = v
    zero = (0, 0, 0, 0) + (0,)*36
    if (kh, kw) not in ((2, 2), (3, 3)) or not all((channels, h, w, sy, sx)):
        return (1,)+zero
    if h+pad < kh or w+pad < kw:
        return (1,)+zero
    oh, ow = (h+pad-kh)//sy+1, (w+pad-kw)//sx+1
    if ch >= channels or y >= oh or x >= ow:
        return (1,)+zero
    oy, ox = y*sy-pad//2, x*sx-pad//2
    taps = []; mask = 0; overflow = False
    for tap in range(9):
        if tap >= kh*kw:
            taps.extend((0, 0, 0, 0)); continue
        ky, kx = divmod(tap, kw); ty, tx = oy+ky, ox+kx; addr = 0
        if 0 <= ty < h and 0 <= tx < w:
            mask |= 1 << tap
            row = ch*h+ty
            assert 0 <= row < channels*h < 2**64
            exact = base+row*w+tx
            # 窄表达式只用于交叉核验证明，黄金值始终来自上面的完整地址。
            row_low_sum = ((ch*h) & U32)+ty
            row_high = bool((ch*h) >> 32 or row_low_sum >> 32)
            q = (row_low_sum & U32)*w
            column_sum = (q & U32)+tx
            base_sum = base+(column_sum & U32)
            narrow_bad = bool(row_high or q >> 32 or column_sum >> 32 or base_sum >> 32)
            assert narrow_bad == (exact > U32)
            overflow |= exact > U32
            addr = exact if exact <= U32 else 0
        taps.extend((addr, ch, ty & ((1 << 64)-1), tx & ((1 << 64)-1)))
    return (2,)+zero if overflow else (0, oh, ow, kh*kw, mask, *taps)


def cases():
    """有效小域全坐标、宽输入、明确边界和参数非法样本；种子固定。"""
    rows = []; counts = Counter(); errors = Counter(); padding = 0
    def add(category, v):
        nonlocal padding
        expected = oracle(v); rows.append((v, expected)); counts[category] += 1; errors[expected[0]] += 1
        padding += expected[0] == 0 and expected[4] == 0
    for c, h, w, k, sy, sx, pad in itertools.product((1, 2), range(1, 4), range(1, 4), (2, 3), (1, 2, 3), (1, 2, 3), range(4)):
        oh, ow = max(0, (h+pad-k)//sy+1), max(0, (w+pad-k)//sx+1)
        for ch, y, x in itertools.product(range(c+1), range(oh+1), range(ow+1)):
            for base in (0, U32, U32-c*h*w):
                add("small_all_coordinates_and_outside", (base,c,h,w,k,k,sy,sx,pad,ch,y,x))
    rng = random.Random(SEED)
    for _ in range(20000):
        c,h,w = (rng.choice((1,2,3,13,65536,0x80000000,U32,rng.getrandbits(32))) for _ in range(3))
        k = rng.choice((2,3)); pad = rng.choice((0,1,2,3,100,U32,rng.getrandbits(32)))
        sy,sx = rng.choice((1,2,3,U32)),rng.choice((1,2,3,U32))
        oh,ow = max(0,(h+pad-k)//sy+1),max(0,(w+pad-k)//sx+1)
        y = rng.choice((0,min(U32,max(0,oh-1)),min(U32,oh),rng.getrandbits(32)))
        x = rng.choice((0,min(U32,max(0,ow-1)),min(U32,ow),rng.getrandbits(32)))
        ch = rng.choice((0,max(0,c-1),c,rng.getrandbits(32))) & U32
        add("wide_u32_random", (rng.choice((0,U32,rng.getrandbits(32))),c,h,w,k,k,sy,sx,pad,ch,y,x))
    manual = [
        ("huge_shape_small_window", (0,U32,2,2,2,2,2,2,1,0,0,0),0),
        ("unused_row2_overflow", (0,1,3,0x80000000,2,2,2,2,1,0,0,0),0),
        ("all_padding_high_row", (0,2,3,0x80000000,2,2,1,1,100,1,50,0),0),
        ("last_address_u32", (U32-3,1,2,2,2,2,2,2,1,0,0,0),0),
        ("base_add_carry", (U32-2,1,2,2,2,2,2,2,1,0,0,0),2),
        ("channel_product_high", (0,3,0x80000000,2,2,2,2,2,1,2,0,0),2),
        ("row_sum_carry", (0,2,U32,1,2,2,1,1,1,1,1,0),2),
        ("row_width_high", (0,1,3,U32,2,2,1,1,1,0,1,0),2),
        ("column_add_carry", (0,1,3,U32-1,2,2,1,1,1,0,1,2),2),
        ("c0_high_plane", (0,1,3,0x80000000,2,2,2,2,1,0,0,0),0),
        ("c1_plane_m", (0,2,2,0x80000000,2,2,2,2,1,1,0,0),2),
        ("c2_plane_half_m", (0,3,1,0x80000000,2,2,1,1,1,2,0,0),2),
        ("channel_row_carry", (0,2,3,0x55555555,2,2,1,1,1,1,1,0),2),
        ("row_x_carry", (0,1,2,U32,2,2,1,1,1,0,1,1),2),
        ("signed_padding_u32", (0,1,2,2,3,3,1,1,U32,0,0,0),0),
    ]
    for name, v, error in manual:
        assert oracle(v)[0] == error, name
        add(name,v)
    valid = (0,1,2,2,2,2,2,2,1,0,0,0)
    for index in (1,2,3,6,7):
        v = list(valid); v[index] = 0; add("zero_required_field",tuple(v))
    for kh,kw in ((0,0),(1,1),(2,3),(3,2),(4,4),(U32,U32)):
        v = list(valid); v[4:6] = kh,kw; add("invalid_kernel_pair",tuple(v))
    return rows, dict(vectors=len(rows),categories=dict(counts),errors=dict(errors),all_padding_success=padding,seed=SEED,manual=[dict(name=n,input=v,expected_error=e) for n,v,e in manual])


def geometry_tb():
    """全部公开字段同时对照原RTL与独立黄金，含九组signed坐标。"""
    p = ["module tb_s8_geometry;", "integer count=0; integer scanned; integer f; string vector_path;", "logic [2:0] gold_error; logic [32:0] gold_h,gold_w; logic [3:0] gold_count; logic [8:0] gold_mask;"]
    p += [f"logic [31:0] {n};" for n in INPUTS]
    for variant in ("old","new","gold"):
        if variant != "gold": p += [f"logic [2:0] {variant}_error; logic [32:0] {variant}_h,{variant}_w; logic [3:0] {variant}_count; logic [8:0] {variant}_mask;"]
        p += [f"logic [31:0] {variant}_address[0:8],{variant}_channel[0:8]; logic signed [63:0] {variant}_y[0:8],{variant}_x[0:8];"]
    for variant,module in (("old","int8_maxpool_geometry"),("new","s2b_maxpool_geometry")):
        ports = [f".{n}({n})" for n in INPUTS]+[f".{n}({variant}_{suffix})" for n,suffix in (("output_height","h"),("output_width","w"),("tap_count","count"),("tap_valid_mask","mask"),("error_code","error"),("tap_address","address"),("tap_source_channel","channel"),("tap_source_y","y"),("tap_source_x","x"))]
        p += [f"{module} {variant}_dut("+",".join(ports)+");"]
    fields = list(INPUTS)+["gold_error","gold_h","gold_w","gold_count","gold_mask"]
    fields += [f"gold_{n}[{tap}]" for tap in range(9) for n in ("address","channel","y","x")]
    p += ["initial begin if(!$value$plusargs(\"VECTOR_PATH=%s\",vector_path)) $fatal(1,\"缺少VECTOR_PATH\"); f=$fopen(vector_path,\"r\"); if(!f) $fatal(1,\"缺少向量\"); while(!$feof(f)) begin", 'scanned=$fscanf(f,"'+" ".join("%h" for _ in fields)+'\\n",'+",".join(fields)+");", f"if(scanned=={len(fields)}) begin #1;"]
    for variant in ("old","new"):
        p += [f"if({{{variant}_error,{variant}_h,{variant}_w,{variant}_count,{variant}_mask}} !== {{gold_error,gold_h,gold_w,gold_count,gold_mask}}) $fatal(1,\"几何头字段不等价 {variant} case=%0d\",count);",
              f"for(integer t=0;t<9;t++) if({{{variant}_address[t],{variant}_channel[t],{variant}_y[t],{variant}_x[t]}} !== {{gold_address[t],gold_channel[t],gold_y[t],gold_x[t]}}) $fatal(1,\"几何tap字段不等价 {variant} case=%0d tap=%0d\",count,t);"]
    p += ['count++; end else if(scanned!=-1) $fatal(1,"向量字段不足"); end $fclose(f); $display("PASS S8_GEOMETRY vectors=%0d",count); $finish; end endmodule']
    return "// 原RTL与独立NCHW黄金全字段比较。\n"+"\n".join(p)+"\n"


def engine_tb(declarations, model):
    """复用原真实引擎差分并补充全部状态硬复位和同沿刺激优先。"""
    tb = engine.generate_tb(declarations)
    tasks = []
    for kind,prefix,index,states in (("pool","p",9,7),("upsample","u",33,6)):
        layer,source = model["layers"][index],model["layers"][index-1]
        ic,ih,iw = source["output_shape_nchw"][1:]; oc,oh,ow = layer["output_shape_nchw"][1:]
        values = dict(layer_index=index,input_base_address=source["tensor_address"],input_length_bytes=source["tensor_length_bytes"],input_channels=ic,input_height=ih,input_width=iw,output_base_address=layer["tensor_address"],output_length_bytes=layer["tensor_length_bytes"],output_channels=oc,output_height=oh,output_width=ow,kernel_height=2,kernel_width=2,stride_y=2,stride_x=2,darknet_padding_parameter=1,stride=2,output_channel=0,output_y=0,output_x=0)
        assigns = " ".join(f"{prefix}_{n}_in=32'h{values[n]:x};" for d,w,n in declarations[kind] if d=="input" and n not in engine.PORT_SKIP)
        tasks += [f"integer {prefix}_reset_coverage=0; task automatic {prefix}_resets; integer elapsed; begin for(integer target=0;target<{states};target++) begin {prefix}_clear; {assigns}",
                  f"{prefix}_pending=0; {prefix}_requests=0; {prefix}_raw=0; {prefix}_response_error=0; {prefix}_error_target=0; {prefix}_stall=1;",
                  f"if(target!=0) begin {prefix}_start_valid_in=1; tick; {prefix}_start_valid_in=0; elapsed=0; while(integer'({prefix}_old.state)!=target && elapsed<200) begin {prefix}_service; elapsed++; end if(elapsed>=200) $fatal(1,\"reset状态不可达\"); end",
                  f"reset=1; {prefix}_start_valid_in=1; {prefix}_result_ready_in=1; {prefix}_backend_rsp_valid_in=1; {prefix}_abort_in=1; tick;",
                  f"if({prefix}_start_ready_old || {prefix}_backend_req_valid_old || {prefix}_result_valid_old || !{prefix}_backend_cancel_old || {prefix}_result_value_old!=0 || {prefix}_result_error_code_old!=0 || {prefix}_result_output_address_old!=0) $fatal(1,\"hard_reset优先或输出清零错误\");",
                  f"{prefix}_reset_coverage|=1<<target; {prefix}_clear; {prefix}_pending=0; reset=0; tick; if(!{prefix}_start_ready_old) $fatal(1,\"reset恢复失败\"); end end endtask"]
    marker = "initial begin p_clear; u_clear;"
    assert marker in tb
    tb = tb.replace(marker,"\n".join(tasks)+"\n"+marker)
    tb = tb.replace("p_vectors; u_vectors;", "p_vectors; u_vectors; p_resets; u_resets; if(p_reset_coverage!=127 || u_reset_coverage!=63) $fatal(1,\"reset覆盖不足\"); $display(\"RESET_COVERAGE pool=%0d upsample=%0d\",p_reset_coverage,u_reset_coverage);")
    return tb


def mutants(checker, work, bindings):
    """自报SHA仍不能修改守卫、清零或模块引用，拒绝原件绑定变化。"""
    fixture = work/"mutants"; fixture.mkdir()
    for p in bindings:
        target=fixture/p; target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(ROOT/p,target)
    profile_path=fixture/"board/s2b_inference_platform.json"; original=profile_path.read_bytes(); records=[]
    for name,path,before,after in (
        ("删除高plane守卫", "src/s2b_maxpool_geometry.sv", "(plane_work[63:32] != 32'd0)", "1'b0"),
        ("C0错误拒绝高plane", "src/s2b_maxpool_geometry.sv", "(input_channel != 32'd0)", "1'b1"),
        ("删除通道低plane乘积高位", "src/s2b_maxpool_geometry.sv", "(channel_offset_work[63:32] != 32'd0)", "1'b0"),
        ("删除通道行加法进位", "src/s2b_maxpool_geometry.sv", "channel_row_sum_work[32] ||", "1'b0 ||"),
        ("提前拒绝全padding高通道", "src/s2b_maxpool_geometry.sv", "if (tap_range_error) begin", "if (tap_range_error || channel_offset_high) begin"),
        ("提前拒绝未消费第三行", "src/s2b_maxpool_geometry.sv", "if (tap_range_error) begin", "if (tap_range_error || row_offset_work[2][63:32] != 0) begin"),
        ("删除宽度乘积高位", "src/s2b_maxpool_geometry.sv", "selected_row_high || selected_offset_high ||", "selected_row_high || 1'b0 ||"),
        ("删除列加法进位", "src/s2b_maxpool_geometry.sv", "logical_offset_work[32] || address_work[32]", "1'b0 || address_work[32]"),
        ("删除base进位", "src/s2b_maxpool_geometry.sv", "logical_offset_work[32] || address_work[32]", "logical_offset_work[32] || 1'b0"),
        ("更改RANGE清零", "src/s2b_maxpool_geometry.sv", "if (tap_range_error) begin", "if (1'b0) begin"),
        ("更改ARG清零", "src/s2b_maxpool_geometry.sv", "if (error_code == BAD_ARGUMENT) begin", "if (1'b0) begin"),
        ("POOL错层选择及自报SHA", "src/s2b_maxpool_engine.sv", "32'd17: geometry_shape_select = 2'd1;", "32'd17: geometry_shape_select = 2'd0;"),
        ("POOL错plane及自报SHA", "src/s2b_maxpool_engine.sv", "64'd2704", "64'd2705"),
        ("POOL漏row及自报SHA", "src/s2b_maxpool_engine.sv", "({32'd0, output_y} * 64'd52)", "64'd0"),
        ("POOL漏X及自报SHA", "src/s2b_maxpool_engine.sv", "({32'd0, output_y} * 64'd52) + {32'd0, output_x}", "({32'd0, output_y} * 64'd52) + 64'd0"),
        ("POOL截通道高位及自报SHA", "src/s2b_maxpool_engine.sv", "{32'd0, output_channel} * 64'd2704", "{32'd0, (output_channel * 32'd2704)}"),
        ("engine引用回退", "src/s2b_maxpool_engine.sv", "s2b_maxpool_geometry u_geometry_l9", "int8_maxpool_geometry u_geometry_l9"),
    ):
        target=fixture/path; raw=(ROOT/path).read_bytes(); assert raw.count(before.encode())==1
        target.write_bytes(raw.replace(before.encode(),after.encode()))
        profile=json.loads(original); digest=backend.sha(target)
        for row in profile["source_derivation"]["derived_sources"]:
            if row["path"]==path: row["sha256"]=digest
        profile_path.write_text(json.dumps(profile,ensure_ascii=False),encoding="utf-8")
        try: checker.check_static(fixture)
        except ValueError as exc: records.append(dict(name=name,status="REJECTED",reason=str(exc)))
        else: raise ValueError("自报SHA反例未拒绝："+name)
        target.write_bytes(raw); profile_path.write_bytes(original)
    return records


def main():
    """新运行不覆盖；每项记录原生退出码、源码快照、资源和真实覆盖。"""
    ap=argparse.ArgumentParser(); ap.add_argument("--run-id",required=True)
    ap.add_argument("--toolchain",type=Path,default=Path(r"D:\FPGA_S2A_MSYS2_20261001\env")); args=ap.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+",args.run_id): ap.error("RunId非法")
    work=ROOT/"tmp/2B/S2B-T17"/args.run_id/"rtl_run"
    evidence=ROOT/"report/evidence/S2B-T17"/args.run_id
    for p in (work.parent,evidence.parent):
        if not p.is_dir() or p.is_symlink(): ap.error("精确父目录不可用")
    if work.exists() or evidence.exists(): ap.error("RunId已存在")
    work.mkdir(); evidence.mkdir(); start=time.monotonic()
    report=dict(task_id="S2B-T17-S12",status="FAIL",source_commit=SOURCE_BASELINE,seed=SEED,runs=[],sta="NOT_RUN",g3="NOT_RUN",independent_review="NOT_RUN",resource_budget=dict(jobs=1,threads=1,rss_limit_bytes=1073741824),limitations=["不是U32全组合穷举；无限精度恒等证明及有限有种子RTL样本共同验证。","真实geometry和engine全公开输出比较；CONV数值、109新整网、STA、实板均未执行。","原继承WIDTH/UNUSED诊断保留-Wall/-Wno-fatal，不接受LATCH/UNOPTFLAT/MULTIDRIVEN。"])
    try:
        assert subprocess.check_output(["git","-c","core.longpaths=true","-c","maintenance.auto=false","rev-parse","HEAD"],cwd=ROOT,text=True).strip()==SOURCE_BASELINE
        checker=backend.load_checker(); bindings=checker.check_static(ROOT)
        for p in (RUNNER,engine.RUNNER,backend.RUNNER,backend.MODEL): bindings[p]=backend.sha(ROOT/p)
        report["source_sha256_pre"]=dict(bindings)
        report["frozen14_sha256_pre"]={p:backend.sha(ROOT/p) for p in checker.FROZEN_CORE_SHA256}
        assert backend.sha(ROOT/"src/s2b_maxpool_engine.sv")=="5f62e5aa5790b7ac9dad342d4ca4a6a4878611efa165884b47e376ff2f4e5b48"
        old=subprocess.check_output(["git","-c","core.longpaths=true","-c","maintenance.auto=false","show",BASELINE+":src/s2b_maxpool_engine.sv"],cwd=ROOT).decode("utf-8")
        current=(ROOT/"src/s2b_maxpool_engine.sv").read_text(encoding="utf-8")
        expected=old.replace("int8_maxpool_geometry u_geometry","s2b_maxpool_geometry u_geometry")
        for before,after in checker.POOL_FIXED_GEOMETRY_REPLACEMENTS:
            assert expected.count(before)==1
            expected=expected.replace(before,after)
        assert current==expected
        assert current.split("    always_ff",1)[1]==old.split("    always_ff",1)[1]
        report["engine_structure"]=dict(only_change="geometry常量实例/选择及64位输出偏移；全部always_ff不变",always_ff_sha256=hashlib.sha256(current.split("    always_ff",1)[1].encode()).hexdigest())
        report["resource_preflight"]=dict(available_ram_bytes=psutil.virtual_memory().available,disk_free_bytes=shutil.disk_usage(work).free,running_tools=[dict(pid=p.pid,name=p.info["name"]) for p in psutil.process_iter(["name"]) if p.info["name"] and p.info["name"].lower() in ("vivado.exe","verilator_bin.exe","cc1plus.exe","xsim.exe")])
        assert report["resource_preflight"]["available_ram_bytes"]>=2147483648 and report["resource_preflight"]["disk_free_bytes"]>=1073741824
        assert not report["resource_preflight"]["running_tools"]
        report["checker_semantic_mutants"]=mutants(checker,work,checker.check_static(ROOT))
        report["checker_public_negatives"]=engine.checker_negatives(checker,work,checker.check_static(ROOT))
        rows,report["geometry_coverage"]=cases()
        data="\n".join(" ".join(f"{n:x}" for n in (*v,*expected)) for v,expected in rows)+"\n"
        (evidence/"geometry_vectors.dat").write_text(data,encoding="utf-8",newline="\n")
        for directory in (work,evidence):
            (directory/"tb_s8_geometry.sv").write_text(geometry_tb(),encoding="utf-8",newline="\n")
        model=json.loads((ROOT/backend.MODEL).read_text(encoding="utf-8")); assert backend.sha(ROOT/backend.MODEL)==backend.MODEL_SHA
        declarations={"pool":engine.ports(ROOT/"src/s2a_maxpool_engine.sv"),"upsample":engine.ports(ROOT/"src/s2a_upsample_engine.sv")}
        report["engine_coverage"]={}
        for kind in declarations:
            data,counts=engine.vector_data(kind,declarations[kind],model); report["engine_coverage"][kind]=counts
            for directory in (work,evidence): (directory/(kind+"_vectors.dat")).write_text(data,encoding="utf-8",newline="\n")
        for directory in (work,evidence): (directory/"tb_s2b_geometry_specialization.sv").write_text(engine_tb(declarations,model),encoding="utf-8",newline="\n")
        source=work/"source"; source.mkdir(); snapshot=evidence/"source_snapshot"; snapshot.mkdir()
        for p in bindings:
            target=snapshot/p; target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(ROOT/p,target)
        for p in engine.RTL: shutil.copyfile(ROOT/p,source/Path(p).name)
        env=os.environ.copy(); bd=args.toolchain/"mingw64/bin"; md=args.toolchain/"usr/bin"
        env["PATH"]=str(md)+os.pathsep+str(bd)+os.pathsep+env.get("PATH",""); env["VERILATOR_ROOT"]=str(args.toolchain/"mingw64/share/verilator"); env["PYTHONUTF8"]="1"
        verilator=bd/"verilator_bin.exe"
        for p in (verilator,bd/"g++.exe",md/"make.exe"): checker.exact_file(p)
        report["tool_versions"]=dict(python=sys.version,verilator=subprocess.check_output([str(verilator),"--version"],env=env,text=True,timeout=30).strip())
        common=[str(verilator),"--binary","--timing","--timescale","1ns/1ps","-Wall","-Wno-fatal","-j","1","--threads","1","--output-split","10000","--output-split-cfuncs","100","-MAKEFLAGS","PYTHON3='\""+sys.executable+"\"'","-CFLAGS","-D_GLIBCXX_USE_CXX11_ABI=0 -O1"]
        for label,top,files in (("geometry","tb_s8_geometry",["source/int8_maxpool_geometry.sv","source/s2b_maxpool_geometry.sv","tb_s8_geometry.sv"]),("engine","tb_s2b_geometry_specialization",["source/"+Path(p).name for p in engine.RTL]+["tb_s2b_geometry_specialization.sv"])):
            command=common+["--top-module",top,"--Mdir","obj_"+label,*files]
            engine.execute(label+"_compile",command,work,evidence,env,report,600)
            engine.execute(label+"_simulation",[str(work/("obj_"+label)/("V"+top+".exe")),*(["+VECTOR_PATH="+str(evidence/"geometry_vectors.dat")] if label=="geometry" else [])],work,evidence,env,report,600)
            warnings=re.findall(r"%Warning-(?:LATCH|UNOPTFLAT|MULTIDRIVEN).*",(evidence/(label+"_compile.log")).read_text(encoding="utf-8"))
            assert not warnings, warnings
        geometry_log=(evidence/"geometry_simulation.log").read_text(encoding="utf-8")
        assert re.findall(r"PASS S8_GEOMETRY vectors=(\d+)",geometry_log)==[str(len(rows))]
        log=(evidence/"engine_simulation.log").read_text(encoding="utf-8")
        matches=re.findall(r"PASS GEOMETRY_SPECIALIZATION pool=(\d+) upsample=(\d+) cycles=(\d+) pool_abort=(\d+) upsample_abort=(\d+)",log); assert len(matches)==1
        report["engine_simulation_counts"]=dict(zip(("pool","upsample","cycles","pool_abort","upsample_abort"),map(int,matches[0])))
        assert report["engine_simulation_counts"]["pool"]==report["engine_coverage"]["pool"]["vectors"]
        assert report["engine_simulation_counts"]["upsample"]==report["engine_coverage"]["upsample"]["vectors"]
        assert report["engine_simulation_counts"]["pool_abort"]==127 and report["engine_simulation_counts"]["upsample_abort"]==63
        assert "RESET_COVERAGE pool=127 upsample=63" in log
        report["source_sha256_post"]={p:backend.sha(ROOT/p) for p in bindings}; assert report["source_sha256_post"]==bindings
        report["frozen14_sha256_post"]={p:backend.sha(ROOT/p) for p in checker.FROZEN_CORE_SHA256}; assert report["frozen14_sha256_pre"]==report["frozen14_sha256_post"]
        report["status"]="PASS_MAXPOOL_ADDRESS_GUARD_G1"
    except Exception as exc: report["failure"]=repr(exc)
    report["seconds"]=round(time.monotonic()-start,3)
    (evidence/"validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({k:report.get(k) for k in ("status","seconds","geometry_coverage","engine_simulation_counts","failure")},ensure_ascii=False),flush=True)
    return 0 if report["status"]=="PASS_MAXPOOL_ADDRESS_GUARD_G1" else 1


if __name__=="__main__":
    raise SystemExit(main())
