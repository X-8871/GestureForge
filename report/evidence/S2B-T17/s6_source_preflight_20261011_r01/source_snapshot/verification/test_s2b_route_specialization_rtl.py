#!/usr/bin/env python3
"""验证冻结ROUTE可达域、独立数学、原/派生query和engine全公开周期。"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import time

import psutil
import test_s2b_backend_coordinates_rtl as backend
import test_s2b_geometry_specialization_rtl as geometry

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "5cb092dcce3631f310e67228738a674a6a82ce41"
RUNNER = "verification/test_s2b_route_specialization_rtl.py"
SEED = 0x2B173011
RTL = ("src/int8_route_query.sv", "src/s2b_route_query.sv",
       "src/s2a_route_engine.sv", "src/s2b_route_engine.sv")


def route_math(model, package):
    """逐字段对照冻结manifest/ROM，独立枚举每个ROUTE源通道和完整空间。"""
    def array(name):
        match = re.search(r"\b" + name + r"\s+\[0:37\](?:\[0:1\])?\s*=\s*'\{(.*?)\};", package, re.S)
        if not match:
            raise ValueError("ROM字段缺失：" + name)
        return [int(v, 16) for v in re.findall(r"\d+'h([0-9A-Fa-f]+)", match[1])]
    groups, ids = array("S2A_GROUP_COUNT"), array("S2A_ROUTE_GROUP_ID")
    starts, ends = array("S2A_ROUTE_CHANNEL_START"), array("S2A_ROUTE_CHANNEL_END")
    rows = []
    for i, layer in enumerate(model["layers"]):
        if layer["op"] != "route":
            continue
        g, gid = layer["route_groups"], layer["route_group_id"]
        if groups[i] != g or ids[i] != gid or g not in (1, 2):
            raise ValueError("冻结组数/组号不符")
        ranges = layer["route_source_channel_ranges"]
        for slot, (begin, end) in enumerate(ranges):
            source = model["layers"][layer["input_tensor_indices"][slot]]
            c, h, w = source["output_shape_nchw"][1:]
            if starts[i*2+slot] != begin or ends[i*2+slot] != end:
                raise ValueError("ROM通道切片不符")
            if c % g or begin != gid*(c//g) or end != (gid+1)*(c//g):
                raise ValueError("独立group切片关系失败")
            for channel in range(begin, end):
                for y in range(h):
                    for x in range(w):
                        offset = (channel*h+y)*w+x
                        if not (0 <= offset < source["tensor_length_bytes"]):
                            raise ValueError("源空间超界")
        count = math.prod(layer["output_shape_nchw"])
        rows.append({"layer": i, "groups": g, "group_id": gid, "ranges": ranges,
                     "outputs": count, "status": "PASS"})
    if [r["layer"] for r in rows] != [3,6,8,11,14,16,19,22,24,31,34]:
        raise ValueError("ROUTE层集合改变")
    source = (ROOT/"src/s2b_network_backend.sv").read_text(encoding="utf-8")
    if source.count(".groups({16'd0, S2A_GROUP_COUNT[layer_cursor]})") != 2:
        raise ValueError("组数不是唯一冻结ROM来源")
    return {"status": "PASS", "layers": rows, "outputs": sum(r["outputs"] for r in rows),
            "unreachable_generic_groups": {"status": "NOT_APPLICABLE", "groups": "3..2^32-1",
                "reason": "原2A通用合法多组与派生拒绝不等价；公开CSR无groups字段，原冻结ROM每个ROUTE仅1/2，START/inputbase/owner/abort/reset不改变该ROM。"}}


def layer_values(model, index):
    """只从冻结manifest生成公开输入，不依赖候选内部组合运算。"""
    row = model["layers"][index]
    c,h,w = row["output_shape_nchw"][1:]
    values = {"source_count": len(row["input_tensor_indices"]), "groups": row["route_groups"],
              "group_id": row["route_group_id"], "output_channel": 0, "output_y": 0, "output_x": 0,
              "output_base_address": row["tensor_address"], "output_length_bytes": row["tensor_length_bytes"],
              "output_channels": c, "output_height": h, "output_width": w}
    for slot in (0,1):
        src = model["layers"][row["input_tensor_indices"][slot]] if slot < values["source_count"] else None
        shape = src["output_shape_nchw"][1:] if src else (0,0,0)
        begin,end = row["route_source_channel_ranges"][slot] if src else (0,0)
        mul = round(row["input_scales"][slot]/row["output_scale"]*2**31) if src else 0
        for key,val in (("base_address",src["tensor_address"] if src else 0),
                        ("length_bytes",src["tensor_length_bytes"] if src else 0),
                        ("channels",shape[0]),("height",shape[1]),("width",shape[2]),
                        ("channel_start",begin),("channel_end",end),("multiplier_q31",mul)):
            values[f"source{slot}_{key}"] = val
    return values


def oracle(v, raw):
    """按数学整数和公开错误优先手算单元素；样例值不超过RTL宽度。"""
    g, gid, n = v["groups"],v["group_id"],v["source_count"]
    bad = n not in (1,2) or g == 0 or gid >= g
    rng = False
    selected = []
    for slot in range(2 if n == 2 else 1):
        p = f"source{slot}_"
        c,h,w,begin,end,mul = [v[p+k] for k in ("channels","height","width","channel_start","channel_end","multiplier_q31")]
        bad |= c == 0 or h == 0 or w == 0 or begin >= end or end > c or mul == 0 or mul > 2**31
        if slot == 1:
            bad |= h != v["source0_height"] or w != v["source0_width"] or begin != 0 or end != c or g != 1
        if slot == 0 and g == 1:
            bad |= begin != 0 or end != c
        if slot == 0 and g == 2:
            bad |= n != 1 or c % 2 != 0 or begin != gid*(c//2) or end != (gid+1)*(c//2)
        size = c*h*w if c*h <= 0xFFFFFFFF else 0
        rng |= c*h > 0xFFFFFFFF or size > 0xFFFFFFFF
        length,base = v[p+"length_bytes"],v[p+"base_address"]
        rng |= length == 0 or length < size or base+length > 2**32
        selected.append((end-begin)&0xFFFFFFFF)
    oc = sum(selected)
    ch,y,x = [v[k] for k in ("output_channel","output_y","output_x")]
    bad |= y >= v["source0_height"] or x >= v["source0_width"] or ch >= oc
    rng |= oc > 0xFFFFFFFF
    slot = 0 if ch < selected[0] else 1 if n == 2 else 0
    p = f"source{slot}_"
    sch = v[p+"channel_start"] + ch - (selected[0] if slot else 0)
    addr = v[p+"base_address"] + (sch*v["source0_height"]+y)*v["source0_width"]+x
    rng |= addr > 0xFFFFFFFF or addr-v[p+"base_address"] >= v[p+"length_bytes"]
    initial = 1 if bad else 2 if rng else 0
    if initial == 0:
        outcount = v["output_channels"]*v["output_height"]*v["output_width"]
        if (oc,v["source0_height"],v["source0_width"]) != (v["output_channels"],v["output_height"],v["output_width"]) or 0 in (v["output_channels"],v["output_height"],v["output_width"],v["output_length_bytes"]) or outcount > v["output_length_bytes"]:
            initial = 3
        elif v["output_base_address"]+v["output_length_bytes"] > 2**32:
            initial = 2
    outaddr = v["output_base_address"]+(ch*v["output_height"]+y)*v["output_width"]+x
    if initial == 0 and (outaddr > 0xFFFFFFFF or outaddr-v["output_base_address"] >= v["output_length_bytes"]):
        initial = 2
    mag = min(127,(abs(raw)*v[p+"multiplier_q31"]+2**30)//2**31)
    return initial,slot,addr&0xFFFFFFFF,outaddr&0xFFFFFFFF,(-mag if raw < 0 else mag)&255


def vectors(model, ports):
    """全部通道/四packed lane和INT8值，定向非法、响应、八态abort/reset及长stall。"""
    names = [n for d,w,n in ports if d == "input" and n not in geometry.PORT_SKIP]
    rows=[]; categories=Counter()
    def add(cat,v,raw=23,error=0,target=0,control=0,state=255,stall=1):
        expected,slot,addr,outaddr,value = oracle(v,raw)
        requests = 0 if expected else 1 if raw == -128 or (error and target == 1) else 2
        if not expected:
            expected = (error if error in (1,2,6) else 6) if error and target in (1,2) else 1 if raw == -128 else 0
        extras = [raw&255,error,target,control,state,stall,expected,slot,addr,outaddr,value,requests]
        rows.append(" ".join(f"{v[n]&0xFFFFFFFF:x}" for n in names)+" "+" ".join(f"{x:x}" for x in extras)); categories[cat]+=1
    for i,row in enumerate(model["layers"]):
        if row["op"] != "route": continue
        v=layer_values(model,i); c,h,w=row["output_shape_nchw"][1:]
        for ch in range(c):
            for lane in range(4):
                add("all_channels_packed_lanes",dict(v,output_channel=ch,output_x=lane),raw=((ch+lane)%255)-127)
        for raw in range(-128,128):
            for ch in {0,c-1}:
                add("all_int8_values_both_sources",dict(v,output_channel=ch),raw=raw)
        for key in names:
            if key.startswith("source1_") and v["source_count"] != 2: continue
            for val in (0,1,3,0xFFFFFFFF):
                if val != v[key] and key != "groups": add("field_boundary",dict(v,**{key:val}))
        add("groups_zero",dict(v,groups=0))
        add("group2_odd_channels",dict(v,groups=2,source_count=1,source0_channels=3))
        add("argument_before_range",dict(v,groups=0,source0_base_address=0xFFFFFFFF,output_length_bytes=0))
        add("source_range_before_output_length",dict(v,source0_length_bytes=0,output_length_bytes=0))
        for error in range(1,8):
            for target in (1,2): add("response_error",v,error=error,target=target)
        for control in (1,2):
            for state in range(8): add("abort_each_state" if control == 1 else "reset_each_state",v,control=control,state=state)
        add("long_stall_abort",v,control=3,stall=2)
        add("no_stall",v,stall=0)
        if v["groups"] == 2:
            add("group2_lower_half_generic_preserved",dict(v,group_id=0,source0_channel_start=0,
                source0_channel_end=v["source0_channels"]//2))
    return "\n".join(rows)+"\n",{"vectors":len(rows),"categories":dict(categories),"parameter_order":names,"seed":SEED}


def testbench(model, ports):
    """同一真实memory响应口驱动双引擎，比较全部公开输出并独立核对结果。"""
    parts=["module tb_s2b_route_specialization; logic clk=0, hard_reset=1; integer cycles=0,cases=0,query_cases=0,abort_mask=0,reset_mask=0;",
           "integer pending=0,delay_count=0,requests=0,raw=0,response_error=0,error_target=0,stall=0; logic [31:0] rsp_data; logic [2:0] rsp_error;"]
    for d,w,n in ports:
        if n in ("clk","hard_reset"): continue
        parts.append(f"logic {w} {n};" if d == "input" else f"logic {w} old_{n}, new_{n};")
    for variant,module in (("old","s2a_route_engine"),("new","s2b_route_engine")):
        parts.append(module+" dut_"+variant+" ("+",".join(f".{n}({variant+'_'+n if d=='output' else n})" for d,w,n in ports)+");")
    outputs=[n for d,w,n in ports if d == "output"]
    comparisons="\n".join(f'if(old_{n} !== new_{n}) $fatal(1,"route公开输出差异 {n} case=%0d cycle=%0d",cases,cycles);' for n in outputs)
    parts.append("task automatic compare; begin "+comparisons+" end endtask\ntask automatic tick; begin clk=0; #2;compare;clk=1;#2;compare;clk=0;#1;cycles++;end endtask")
    assignments=" ".join(n+"=0;" for d,w,n in ports if d == "input" and n not in ("clk","hard_reset"))
    parts.append("task automatic clear;begin "+assignments+" pending=0;requests=0;hard_reset=1;tick;hard_reset=0;tick;end endtask")
    parts.append("""
task automatic service;
logic accept_request,responding;
begin
 backend_req_ready = stall == 2 ? 0 : stall == 0 || cycles%5!=0;
 backend_rsp_valid = pending && delay_count==0;
 backend_rsp_rdata=rsp_data;backend_rsp_error=rsp_error;
 #1;accept_request=old_backend_req_valid&&backend_req_ready;responding=backend_rsp_valid;
 tick;
 if(responding) pending=0;
 else if(pending&&delay_count>0) delay_count--;
 if(accept_request) begin
  if(pending) $fatal(1,"重复请求");
  requests++; pending=1;delay_count=stall==0 ? 0 : cycles%4;
  rsp_data={4{8'(raw)}};
  rsp_error=requests==error_target ? 3'(response_error) : 0;
 end
end endtask
""")
    names=[n for d,w,n in ports if d == "input" and n not in geometry.PORT_SKIP]
    extras=["raw","response_error","error_target","control","target_state","stall","expected_error","expected_slot","expected_addr","expected_outaddr","expected_value","expected_requests"]
    fmt=" ".join("%h" for _ in names+extras)+"\\n"
    parts.append("integer fh,scanned,control,target_state,expected_error,expected_slot,expected_addr,expected_outaddr,expected_value,expected_requests,elapsed,injected;")
    parts.append('initial begin clear;fh=$fopen("route_vectors.dat","r");if(!fh)$fatal(1,"缺向量");while(!$feof(fh)) begin\nclear;scanned=$fscanf(fh,"'+fmt+'",'+",".join(names+extras)+");")
    parts.append(f"""
if(scanned=={len(names)+len(extras)}) begin
 start_valid=1;result_ready=0;injected=0;
 if(control && target_state==0) begin
  if(control==1) begin abort=1;abort_mask|=1;end
  else begin hard_reset=1;reset_mask|=1;end
 end
 tick;start_valid=0;
 if(control && target_state==0) begin
  abort=0;hard_reset=0;tick;
 end else begin
  elapsed=0;
  while(!old_result_valid&&elapsed<300) begin
   if((control==1||control==2)&&integer'(dut_old.state)==target_state) begin
    if(control==1) begin abort=1;abort_mask|=1<<target_state;end
    else begin hard_reset=1;reset_mask|=1<<target_state;end
    tick;injected=1;break;
   end
   service;elapsed++;
   if(control==3&&elapsed==200) begin
    if(old_result_valid||requests!=0) $fatal(1,"无限请求背压提前完成");
    abort=1;tick;injected=1;break;
   end
  end
  if(injected) begin
   if(old_result_valid||old_backend_req_valid) $fatal(1,"活动状态取消失败");
   pending=0;abort=0;hard_reset=0;tick;
  end else begin
   if(!old_result_valid||old_result_error_code!==3'(expected_error)||requests!=expected_requests)
    $fatal(1,"结果/请求oracle不同 case=%0d code=%0d expected=%0d requests=%0d expectedrequests=%0d",cases,old_result_error_code,expected_error,requests,expected_requests);
   if(!expected_error && (old_result_source_index!==32'(expected_slot)||old_result_source_address!==32'(expected_addr)||old_result_output_address!==32'(expected_outaddr)||old_result_value!==8'(expected_value)))
    $fatal(1,"独立数学结果不同");
   if(control&&target_state==7) begin
    if(control==1) begin abort=1;abort_mask|=128;tick;if(!old_result_valid)$fatal(1,"RESULT abort未保持");abort=0;end
    else begin hard_reset=1;reset_mask|=128;tick;if(old_result_valid)$fatal(1,"RESULT reset未清空");hard_reset=0;end
   end
   repeat(3) service;
   result_ready=1;tick;result_ready=0;
  end
 end
 cases++;
end else if(scanned!=-1) $fatal(1,"向量列数错误");
end
$fclose(fh);clear;
QUERY_RUN
if(abort_mask!=255||reset_mask!=255)$fatal(1,"取消状态覆盖缺失");
$display("PASS ROUTE_SPECIALIZATION cases=%0d queries=%0d cycles=%0d abort=%0d reset=%0d",cases,query_cases,cycles,abort_mask,reset_mask);$finish;end
endmodule
""")
    # 直接query把engine的配置端口复用，数值端口单独定义；默认检查实际可达1/2组域。
    query_ports = re.findall(r"^\s*(input|output)\s+logic\s*(?:signed\s*)?(\[[^\]]+\])?\s*(\w+)",
        (ROOT/RTL[0]).read_text(encoding="utf-8").split(");",1)[0],re.M)
    declarations=["logic signed [7:0] source0_value=0,source1_value=0;"]
    qoutputs=[n for d,w,n in query_ports if d == "output"]
    for d,w,n in query_ports:
        if d == "output": declarations.append(f"logic {w} qo_{n},qn_{n};")
    for variant,module in (("qo","int8_route_query"),("qn","s2b_route_query")):
        declarations.append(module+" q_"+variant+" ("+",".join(f".{n}({variant+'_'+n if d=='output' else n})" for d,w,n in query_ports)+");")
    declarations.append("task automatic query_compare;begin #1;"+" ".join(f'if(qo_{n}!==qn_{n})$fatal(1,"query差异 {n}");' for n in qoutputs)+"query_cases++;end endtask")
    qrun=[]
    for index,row in enumerate(model["layers"]):
        if row["op"] != "route": continue
        v=layer_values(model,index);c,h,w=row["output_shape_nchw"][1:]
        qrun.append(" ".join(f"{k}=32'd{x};" for k,x in v.items())+"source0_value=23;source1_value=-31;")
        qrun.append(f"for(integer c=0;c<{c};c++) for(integer y=0;y<{h};y++) for(integer x=0;x<{w};x++) begin output_channel=32'(c);output_y=32'(y);output_x=32'(x);query_compare;")
        selected0=v["source0_channel_end"]-v["source0_channel_start"]
        for slot in range(v["source_count"]):
            p=f"source{slot}_"
            value=23 if slot==0 else -31
            magnitude=(abs(value)*v[p+"multiplier_q31"]+2**30)//2**31
            scaled=(-magnitude if value<0 else magnitude)&255
            channel=f"c+{v[p+'channel_start']}" if slot==0 else f"c-{selected0}+{v[p+'channel_start']}"
            condition=f"c<{selected0}" if slot==0 else f"c>={selected0}"
            qrun.append(f"if({condition} && (qo_error_code!=0 || qo_source_index!={slot} || qo_source_channel!=32'({channel}) || qo_source_address!=32'({v[p+'base_address']}+(({channel})*{h}+y)*{w}+x) || qo_output_channels!={c} || qo_output_height!={h} || qo_output_width!={w} || qo_output_value!==8'd{scaled})) $fatal(1,\"完整空间独立query数学不同layer={index}\");")
        qrun.append("end")
    # 随机宽度/非法值采用固定种子，差分比较包括错误时全部默认输出。
    qrun.append(f"begin integer seed={SEED};integer r; for(integer n=0;n<50000;n++) begin")
    for d,w,n in query_ports:
        if d == "input":
            expression = "$unsigned($random(seed))" if n not in ("groups","source_count") else "32'($unsigned($random(seed))%3)" if n == "groups" else "32'($unsigned($random(seed))%4)"
            qrun.append(f"{n}={expression};")
    qrun.append("query_compare;end end")
    # 原通用合法group3明确非等价，只验证派生拒绝而不冒充全域差分。
    for group,channels,start,end in ((3,6,2,4),(4,8,2,4),(0x80000000,0x80000000,1,2),(0xFFFFFFFF,0xFFFFFFFF,1,2)):
        qrun.append(f"source_count=1;groups=32'd{group};group_id=1;source0_channels=32'd{channels};source0_height=1;source0_width=1;source0_channel_start=32'd{start};source0_channel_end=32'd{end};source0_length_bytes=32'd{channels};source0_base_address=0;source0_multiplier_q31=32'h80000000;output_channel=0;output_y=0;output_x=0;source0_value=23;#1;if(qo_error_code!=0||qn_error_code!=1)$fatal(1,\"通用多组不等价边界未明确\");")
    body="\n".join(parts).replace("QUERY_RUN","\n".join(qrun))
    return body.replace("integer fh,scanned", "\n".join(declarations)+"\ninteger fh,scanned")+"\n"


def main():
    """单job隔离编译；所有源码前后哈希一致才可报告G1范围通过。"""
    parser=argparse.ArgumentParser();parser.add_argument("--run-id",required=True)
    parser.add_argument("--toolchain",type=Path,default=Path(r"D:\FPGA_S2A_MSYS2_20261001\env"));args=parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+",args.run_id):parser.error("RunId非法")
    work=ROOT/"tmp/2B/S2B-T17"/args.run_id;evidence=ROOT/"report/evidence/S2B-T17"/args.run_id
    for p in (work.parent,evidence.parent):
        if not p.is_dir() or p.is_symlink():parser.error("精确父目录不存在")
    if work.exists() or evidence.exists():parser.error("RunId不可覆盖")
    work.mkdir();evidence.mkdir();started=time.monotonic()
    report={"schema_version":1,"task_id":"S2B-T17-S3","run_id":args.run_id,"source_commit":BASELINE,
            "status":"FAIL","runs":[],"g3":"NOT_RUN","sta":"NOT_RUN",
            "resource_budget":{"jobs":1,"threads":1,"rss_limit_bytes":1610612736,"cache_limit_bytes":314572800},
            "limitations":["通用合法groups>=3与派生不等价，明确不适用固定tiny416；原2A通用源码保留。",
                "engine本身无timeout计数器；200周期请求背压后abort，以及原响应错误码1..7验证取消与映射。",
                "完整ROUTE memory序列/owner由另一个真实15nonconv backend runner执行；本runner为directquery完整空间及engine边界。",
                "未执行新闭包综合/时序、109整网、bit或实物，禁止继承旧通过结果。"]}
    try:
        checker=backend.load_checker();bindings=checker.check_static(ROOT)
        bindings.update({RUNNER:backend.sha(ROOT/RUNNER),backend.RUNNER:backend.sha(ROOT/backend.RUNNER),
                         geometry.RUNNER:backend.sha(ROOT/geometry.RUNNER),backend.MODEL:backend.sha(ROOT/backend.MODEL)})
        report["source_sha256_pre"]=bindings.copy()
        report["frozen14_sha256_pre"]={p:backend.sha(ROOT/p) for p in checker.FROZEN_CORE_SHA256}
        actual=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
        committed=subprocess.check_output(["git","diff","--name-only",BASELINE,actual,"--",*bindings],cwd=ROOT,text=True).splitlines()
        if committed:raise ValueError("任务输入源码闭包的提交来源改变")
        report["source_commit"]=actual;report["task_baseline_commit"]=BASELINE
        report["committed_source_changes_since_task_baseline"]=committed
        if backend.sha(ROOT/backend.MODEL)!=backend.MODEL_SHA:raise ValueError("冻结模型改变")
        model=json.loads((ROOT/backend.MODEL).read_text(encoding="utf-8"))
        report["math_proof"]=route_math(model,(ROOT/"src/s2a_network_descriptor_pkg.sv").read_text(encoding="utf-8"))
        report["checker_negatives"]=backend.checker_negatives(checker,work,bindings)
        ports=geometry.ports(ROOT/"src/s2a_route_engine.sv")
        data,report["coverage"]=vectors(model,ports)
        for directory in (work,evidence):
            (directory/"route_vectors.dat").write_text(data,encoding="utf-8",newline="\n")
            (directory/"tb_s2b_route_specialization.sv").write_text(testbench(model,ports),encoding="utf-8",newline="\n")
        source=work/"source";source.mkdir();snapshot=evidence/"source_snapshot";snapshot.mkdir()
        for path in bindings:shutil.copyfile(ROOT/path,snapshot/Path(path).name)
        for path in RTL:shutil.copyfile(ROOT/path,source/Path(path).name)
        for path in RTL[:1]+RTL[2:3]:
            gitraw=subprocess.check_output(["git","show",BASELINE+":"+path],cwd=ROOT)
            if gitraw.decode("utf-8").replace("\r\n","\n")!=(ROOT/path).read_text(encoding="utf-8"):raise ValueError("原ROUTE Git来源变化")
        env=os.environ.copy();bin_dir=args.toolchain/"mingw64/bin";make_dir=args.toolchain/"usr/bin"
        env["PATH"]=str(make_dir)+os.pathsep+str(bin_dir)+os.pathsep+env.get("PATH","")
        env["VERILATOR_ROOT"]=str(args.toolchain/"mingw64/share/verilator");env["PYTHONUTF8"]="1"
        verilator=bin_dir/"verilator_bin.exe"
        for path in (verilator,bin_dir/"g++.exe",make_dir/"make.exe"):checker.exact_file(path)
        report["resource_preflight"]={"available_ram_bytes":psutil.virtual_memory().available,"disk_free_bytes":shutil.disk_usage(work).free,
            "running_tools":[{"pid":p.pid,"name":p.info["name"],"rss":p.memory_info().rss} for p in psutil.process_iter(["name"]) if p.info["name"] and p.info["name"].lower() in ("vivado.exe","verilator_bin.exe","cc1plus.exe")],
            "heavy_slot":"总控确认S2结束并授权本次单job独占。"}
        if report["resource_preflight"]["available_ram_bytes"]<2147483648 or report["resource_preflight"]["disk_free_bytes"]<1073741824:raise ValueError("资源不足")
        report["tool_versions"]={"python":sys.version,"verilator":subprocess.check_output([str(verilator),"--version"],env=env,text=True,timeout=30).strip()}
        command=[str(verilator),"--binary","--timing","--timescale","1ns/1ps","-Wall","-Wno-fatal","-j","1","--threads","1",
            "--output-split","10000","--output-split-cfuncs","100","--top-module","tb_s2b_route_specialization","--Mdir","obj_dir",
            "-MAKEFLAGS","PYTHON3='\""+sys.executable+"\"'","-CFLAGS","-D_GLIBCXX_USE_CXX11_ABI=0 -O1",
            *["source/"+Path(p).name for p in RTL],"tb_s2b_route_specialization.sv"]
        backend.execute("compile",command,work,evidence,env,report,600)
        backend.execute("simulation",[str(work/"obj_dir/Vtb_s2b_route_specialization.exe")],work,evidence,env,report,600)
        text=(evidence/"simulation.log").read_text(encoding="utf-8")
        match=re.findall(r"PASS ROUTE_SPECIALIZATION cases=(\d+) queries=(\d+) cycles=(\d+) abort=(\d+) reset=(\d+)",text)
        if len(match)!=1:raise ValueError("唯一PASS缺失")
        counts=dict(zip(("cases","queries","cycles","abort","reset"),map(int,match[0])))
        if counts["cases"]!=report["coverage"]["vectors"] or counts["queries"]!=report["math_proof"]["outputs"]+50000 or counts["abort"]!=255 or counts["reset"]!=255:raise ValueError("覆盖数不同")
        report["simulation_counts"]=counts
        report["outside_profile_witnesses"]={"status":"NOT_APPLICABLE","cases":4,
            "groups":[3,4,2147483648,4294967295],"original_error":0,"specialized_error":1,
            "reason":"这些原通用合法输入与派生不等价，不计入等价query数；实际公开2B不可选择组数。"}
        report["source_sha256_post"]={p:backend.sha(ROOT/p) for p in bindings}
        report["frozen14_sha256_post"]={p:backend.sha(ROOT/p) for p in checker.FROZEN_CORE_SHA256}
        if report["source_sha256_pre"]!=report["source_sha256_post"] or report["frozen14_sha256_pre"]!=report["frozen14_sha256_post"]:raise ValueError("运行期间源码改变")
        report["status"]="PASS_ROUTE_SPECIALIZATION_DIRECT_G1"
    except Exception as exc:
        report["failure"]=repr(exc)
    report["seconds"]=round(time.monotonic()-started,3)
    report["artifacts"]=[{"path":p.relative_to(ROOT).as_posix(),"sha256":backend.sha(p),"bytes":p.stat().st_size} for p in evidence.rglob("*") if p.is_file()]
    (evidence/"validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({k:report.get(k) for k in ("status","seconds","simulation_counts","failure")},ensure_ascii=False),flush=True)
    return 0 if report["status"]=="PASS_ROUTE_SPECIALIZATION_DIRECT_G1" else 1


if __name__=="__main__":
    raise SystemExit(main())
