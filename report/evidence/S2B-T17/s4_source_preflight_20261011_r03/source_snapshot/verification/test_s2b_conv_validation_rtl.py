#!/usr/bin/env python3
"""核对CONV batch恒1校验的精确派生及双完整模块逐周期公开行为。"""
from __future__ import annotations
import argparse
import copy
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
# 在NumPy载入前实际限定数学库线程；不依赖提示词或库默认设置。
CPU_THREAD_ENV={name:"1" for name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS")}
os.environ.update(CPU_THREAD_ENV)
import numpy as np
import test_s2b_backend_coordinates_rtl as support

ROOT=Path(__file__).resolve().parents[1]
BASELINE="6d3fd8567b579a51d4042667d47af7d94f2f5a97"
RUNNER="verification/test_s2b_conv_validation_rtl.py"
RTL=("src/s2a_network_descriptor_pkg.sv","src/s2a_conv_tile_engine.sv","src/s2b_conv_tile_engine.sv")
FIXTURE=Path("D:/FPGA_Competition/report/evidence/S2A-T66/tile01/fixture")
FIXED={"sample0_input_chw_int8.bin":(519168,"da26d3850d23d6f8cb466416799358e77fbeceaa8ee27696ebf7ab365248ab9e"),
 "sample0_layer0_gf8_weights.bin":(864,"df49b5d3aeaebd6b4107b99d83ffa791d7a7e24bd7b26df0815c246e5717e633"),
 "sample0_layer0_expected_nchw_int8.bin":(1384448,"220499b6b8122c3264bef4d581967d51eedccc9e28813df3e0ff8f8716bc2ed8")}

def cpu_layer0(model,evidence,checker):
    """按D2冻结规范独立INT64卷积和binary64半远离零量化，并实际恢复T25切片。"""
    import ctypes
    started=time.monotonic();process=psutil.Process();threads_before=process.threads()
    main_thread=ctypes.windll.kernel32.GetCurrentThreadId()
    candidates=list((Path(np.__file__).resolve().parent.parent/"numpy.libs").glob("libscipy_openblas64_*.dll"))
    if len(candidates)!=1:raise ValueError("实际OpenBLAS DLL不唯一")
    blas_path=checker.exact_file(candidates[0]);blas=ctypes.CDLL(str(blas_path))
    get_threads=blas.scipy_openblas_get_num_threads64_;get_threads.restype=ctypes.c_int
    blas_threads=get_threads()
    if blas_threads!=1:raise ValueError("实际OpenBLAS数学线程配置不是1")
    import zlib
    shard=checker.exact_file(Path("D:/FPGA_Competition/report/evidence/S2A-T25/tensors/sample_000.zlib"))
    gf8=checker.exact_file(Path("D:/FPGA_Data/HaGRIDv2/darknet_inputs/runs/s1_t02_d2_tiny416_int8_weight_r2/gesture_yolov4_tiny_416_int8_weights.gf8"))
    if support.sha(shard)!="49488538ced503bad996e284a3593d4fc7a1cf3b605d90221b3ca09875c4966e" or support.sha(gf8)!="f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39":raise ValueError("T25/GF8来源SHA漂移")
    raw=zlib.decompress(shard.read_bytes())
    if hashlib.sha256(raw).hexdigest()!="090b1422f8e8d4d22124568af9778ba7bd5e7168407c0125e1e729d4a5a46f80":raise ValueError("T25恢复SHA漂移")
    golden=(FIXTURE/"sample0_layer0_expected_nchw_int8.bin").read_bytes()
    if raw[:len(golden)]!=golden:raise ValueError("完整layer0夹具不是冻结T25切片")
    row=model["layers"][0];weight=(FIXTURE/"sample0_layer0_gf8_weights.bin").read_bytes()
    if gf8.read_bytes()[316:1180]!=weight:raise ValueError("权重夹具不是冻结GF8切片")
    feature=np.frombuffer((FIXTURE/"sample0_input_chw_int8.bin").read_bytes(),dtype=np.int8).astype(np.int64).reshape(3,416,416)
    padded=np.pad(feature,((0,0),(1,1),(1,1)))
    patch=np.stack([padded[c,ky:ky+416:2,kx:kx+416:2].reshape(-1) for c in range(3) for ky in range(3) for kx in range(3)])
    matrix=np.frombuffer(weight,dtype=np.int8).astype(np.int64).reshape(32,27)
    bounds=np.abs(matrix).sum(axis=1)*127+np.abs(np.asarray(row["bias_accumulator_int32_per_output_channel"],dtype=np.int64))
    if np.any(bounds>2147483647):raise ValueError("INT32中间累加安全界不成立")
    accum=matrix@patch+np.asarray(row["bias_accumulator_int32_per_output_channel"],dtype=np.int64)[:,None]
    values=[]
    for c in range(32):
        scale=float(row["input_scale"])*float(row["weight_scale_per_output_channel"][c])
        scaled=accum[c].astype(np.float64)*scale
        scaled=scaled/float(row["output_scale"])
        scaled=np.where(scaled<0,scaled*0.1,scaled)
        rounded=np.floor(np.abs(scaled)+0.5)*np.where(scaled<0,-1,1)
        values.append(np.clip(rounded,-127,127).astype(np.int8))
    actual=np.concatenate(values).tobytes();mismatches=sum(a!=b for a,b in zip(actual,golden))
    (evidence/"cpu_layer0_expected.bin").write_bytes(actual)
    if actual!=golden:raise ValueError(f"独立CPU卷积与T25不同：{mismatches}")
    memory=process.memory_info();threads_after=process.threads();thread_map={t.id:t for t in threads_before}
    deltas=[{"id":t.id,"main":t.id==main_thread,"user_seconds":t.user_time-thread_map[t.id].user_time,"system_seconds":t.system_time-thread_map[t.id].system_time} for t in threads_after if t.id in thread_map]
    if get_threads()!=1:raise ValueError("CPU数学库实际线程配置变化")
    return {"status":"PASS","cpu_seconds":round(time.monotonic()-started,3),"thread_environment":CPU_THREAD_ENV,"blas_threads_before_after":[blas_threads,get_threads()],
      "blas_dll":{"path":str(blas_path),"sha256":support.sha(blas_path),"getter":"scipy_openblas_get_num_threads64_"},"host_threads_before":len(threads_before),"host_threads_after":len(threads_after),"main_thread_id":main_thread,"thread_cpu_deltas":deltas,
      "thread_scope":"数学库实际getter=1；Python/Windows已有宿主辅助线程另列，INT64点积、逐元素量化均由主线程调用，前后CPU计时分辨率由OS限定。",
      "self_rss_bytes_cpu_end":memory.rss,"peak_self_working_set_bytes_upto_cpu_end":getattr(memory,"peak_wset",None),"peak_scope":"OS进程生命周期峰截至CPU结束；包含导入/前置静态核验，作为CPU内存上界，非全系统峰。",
      "method":"INT64 im2col矩阵点积+manifest fused bias；D2 binary64分别乘/除，负值leaky0.1，半远离零，[-127,127]饱和；未读取生产MQROM或派生引擎。",
      "bytes":len(actual),"mismatches":mismatches,"sha256":hashlib.sha256(actual).hexdigest(),"int32_absolute_bounds":bounds.tolist(),"numpy_version":np.__version__,
      "bindings":[{"path":str(p),"sha256":support.sha(p)} for p in (shard,gf8,ROOT/"verification/s1_t02_d2_int8_forward.py")],"restored_network_bytes":len(raw),"scope":"仅layer0完整CPU重新计算；T25整网shard仅恢复以核对切片，未运行整网。"}
SKIP={"clk","hard_reset","abort","buffer_owner_pl","start_valid","backend_req_ready","backend_rsp_valid","backend_rsp_rdata","backend_rsp_error","result_ready"}

def ports():
    """读取实际端口声明，保留signed及宽度；不读内部算法生成黄金。"""
    text=(ROOT/RTL[1]).read_text(encoding="utf-8").split(");",1)[0]
    return re.findall(r"\b(input|output)\s+logic\s*((?:signed\s*)?(?:\[[^\]]+\])?)\s*(\w+)",text)

def rom(name):
    """仅从冻结描述符取不可变MQ容量和层类型元数据。"""
    text=(ROOT/RTL[0]).read_text(encoding="utf-8")
    m=re.search(r"\b"+name+r"\s+\[0:37\]\s*=\s*'\{(.*?)\};",text,re.S)
    if not m: raise ValueError("ROM字段缺失："+name)
    return [int(v,16) for v in re.findall(r"\d+'h([0-9a-fA-F]+)",m[1])]

def oracle(v,mq,base,ops):
    """独立整数校验：乘积以Python无限精度计算，原64位shape减法明确按模解释。"""
    u=(1<<32)-1; mask=(1<<64)-1
    i=lambda n:v[n]
    lid=i("layer_index"); reduction=i("input_channels")*i("kernel_height")*i("kernel_width")
    first=(not i("buffer_owner_pl") or i("activation_mode")>1 or i("input_batch_count")!=1 or i("output_batch_count")!=1 or
      i("output_batch")!=0 or any(i(n)==0 for n in ("input_channels","input_height","input_width","output_channels","output_height","output_width","kernel_height","kernel_width","stride_y","stride_x")) or
      i("groups")!=1 or i("padding_value_int8")!=0 or reduction==0 or reduction>4608 or lid>=38 or (lid<38 and ops[lid]!=0) or lid!=i("weight_layer_index"))
    if first:return 2 if lid>=38 or lid!=i("weight_layer_index") else 1
    inp=i("input_batch_count")*i("input_channels")*i("input_height")*i("input_width")
    out=i("output_batch_count")*i("output_channels")*i("output_height")*i("output_width")
    weight=i("output_channels")*reduction
    if any(n>u or length!=(n&u) for n,length in ((inp,i("input_length_bytes")),(out,i("output_length_bytes")),(weight,i("quantized_weight_bytes")))):return 3
    ph=(min(i("output_height"),8)-1)*i("stride_y")+i("kernel_height")
    pw=(min(i("output_width"),8)-1)*i("stride_x")+i("kernel_width")
    if (any(i(a)+i(b)>1<<32 for a,b in (("input_base_address","input_length_bytes"),("output_base_address","output_length_bytes"),("weight_package_base_address","weight_package_length_bytes"))) or
        i("weight_package_length_bytes")==0 or i("quantized_weight_offset")+i("quantized_weight_bytes")>i("weight_package_length_bytes") or mq[lid]!=i("output_channels") or
        base[lid]+i("output_channels")>3164 or ph*pw*i("input_channels")>51200 or min(i("output_channels"),8)*reduction>36864):return 2
    for axis,a,b in (("height","pad_top","pad_bottom"),("width","pad_left","pad_right")):
        n=i("input_"+axis)+i(a)+i(b);k=i("kernel_"+axis);s=i("stride_y" if axis=="height" else "stride_x");prod=i("output_"+axis)*s;span=(n-k)&mask
        if n<k or prod<=span or prod>((span+s)&mask):return 1
    return 0

def vectors(model):
    """冻结21层和全字段边界、batch优先交叉、固定种子宽随机独立黄金。"""
    names=[n for d,w,n in ports() if d=="input" and n not in SKIP]
    mq,mb,ops=rom("S2A_T23_MQ_CHANNEL_COUNT"),rom("S2A_T23_MQ_BASE"),rom("S2A_OP")
    layer0=dict.fromkeys(names,0)
    layer0.update(input_batch_count=1,input_channels=3,input_height=4,input_width=4,input_length_bytes=48,
      output_batch_count=1,output_channels=32,output_height=2,output_width=2,output_length_bytes=128,output_base_address=0x1000000,
      kernel_height=3,kernel_width=3,stride_y=1,stride_x=1,groups=1,weight_package_base_address=0x100000,
      weight_package_length_bytes=5903100,quantized_weight_offset=316,quantized_weight_bytes=864,activation_mode=1,buffer_owner_pl=1)
    rows=[]; categories={}; frozen=[]
    def add(cat,v):
        v=dict(v);v.setdefault("buffer_owner_pl",1);v["activation_mode"] &= 3; e=oracle(v,mq,mb,ops)
        rows.append((v,e));categories[cat]=categories.get(cat,0)+1
        return e
    add("small_valid",layer0)
    for row in model["layers"]:
        if row["op"]!="convolutional":continue
        v=dict(layer0);n,c,h,w=row["input_shape_nchw"];on,oc,oh,ow=row["output_shape_nchw"]
        source=row["input_tensor_indices"][0]; inp=0 if source=="network_input" else model["layers"][source]["tensor_address"]
        v.update(layer_index=row["layer_index"],weight_layer_index=row["weight_layer_index"],input_batch_count=n,input_channels=c,input_height=h,input_width=w,
          input_base_address=inp,input_length_bytes=n*c*h*w,output_batch_count=on,output_channels=oc,output_height=oh,output_width=ow,
          output_base_address=row["tensor_address"],output_length_bytes=row["tensor_length_bytes"],kernel_height=row["kernel_hw"][0],kernel_width=row["kernel_hw"][1],
          stride_y=row["stride_hw"][0],stride_x=row["stride_hw"][1],pad_left=row["padding_lrtb"][0],pad_right=row["padding_lrtb"][1],pad_top=row["padding_lrtb"][2],pad_bottom=row["padding_lrtb"][3],
          groups=row["groups"],padding_value_int8=row["padding_value_int8"],activation_mode=int(row["activation"]=="leaky"),
          quantized_weight_offset=row["gf8_parameter_offsets"]["quantized_weight_offset"],quantized_weight_bytes=row["gf8_parameter_offsets"]["quantized_weight_bytes"])
        if add("frozen_conv_descriptor",v)!=0:raise ValueError("冻结CONV校验未通过")
        frozen.append({"layer":row["layer_index"],"inputs":v,"expected":0})
    for field in names:
        for value in (0,1,2,3,7,8,31,32,4608,4609,65535,65536,0x7fffffff,0x80000000,0xfffffffe,0xffffffff):
            v=dict(layer0);v[field]=value;add("each_field_extremes",v)
    # 非法batch必须覆盖全部其他字段的非法优先组合，包括layer异常压过batch。
    for batch_field in ("input_batch_count","output_batch_count"):
        for batch in (0,2,0xffffffff):
            for field in names:
                for value in (0,0xffffffff):
                    v=dict(layer0);v[batch_field]=batch;v[field]=value;add("batch_invalid_priority_cross",v)
    for field in ("input_base_address","output_base_address","weight_package_base_address"):
        length=layer0[{"input_base_address":"input_length_bytes","output_base_address":"output_length_bytes","weight_package_base_address":"weight_package_length_bytes"}[field]]
        for value in ((1<<32)-length-1,(1<<32)-length,(1<<32)-length+1):
            v=dict(layer0);v[field]=value;add("address_end_minus_equal_plus_2pow32",v)
    rng=random.Random(0x2B171004)
    for j in range(2000):
        v=dict(layer0)
        for field in rng.sample(names,rng.randint(1,5)):v[field]=rng.getrandbits(32) & (3 if field=="activation_mode" else 0xffffffff)
        add("wide_random",v)
    text="\n".join(" ".join(f"{v[n]&0xffffffff:x}" for n in names+["buffer_owner_pl"])+f" {e:x}" for v,e in rows)+"\n"
    return names,text,layer0,{"vectors":len(rows),"categories":categories,"seed":0x2B171004,"frozen_conv_layers":frozen,
      "independent_math":"Python无限精度128bit可容纳4个UINT32因子，形状64bit减法/加法显式取模；两batch为1时乘积全值恒等，非1必在首分支拒绝。"}

def pair(header,instance="u_dut"):
    """公开端口同刺激双实例；比较全部输出，包括无效周期保留值。"""
    ports_here=ports(); outputs=[(w,n) for d,w,n in ports_here if d=="output"]
    declarations="\n".join(f"logic {w} candidate_{n};" for w,n in outputs)
    connections=re.sub(r"\.(\w+)\((\w+)\)",lambda m:f".{m[1]}(candidate_{m[2]})" if m[1] in [n for w,n in outputs] else m[0],header)
    connections=connections.replace("s2a_conv_tile_engine "+instance,"s2b_conv_tile_engine u_candidate")
    compare=" || ".join(f"({n} !== candidate_{n})" for w,n in outputs)
    return declarations+"\n"+connections+f"\ninteger compare_cycles=0; always @(negedge clk) begin if ({compare}) $fatal(1,\"CONV公开输出逐周期不同 cycle=%0d\",compare_cycles); compare_cycles++; end\n"

def boundary_tb(names,small):
    """所有合法状态均从公开START实际到达；只读状态定位abort/reset，不强制状态。"""
    ports_here=ports();decl="\n".join(f"logic {w} {n}=0;" for d,w,n in ports_here if n!="clk")
    conn="s2a_conv_tile_engine u_dut ("+",".join(f".{n}({n})" for d,w,n in ports_here)+");"
    defaults=" ".join(f"{n}=32'h{small[n]&0xffffffff:x};" for n in names)+" buffer_owner_pl=1;"
    fmt=" ".join("%h" for _ in range(len(names)+2))+"\\n"
    args=",".join(names+["buffer_owner_pl","expected_error"])
    return f"""`timescale 1ns/1ps
module tb_s2b_conv_validation;
logic clk=0; {decl}
{conn}
{pair(conn)}
integer cycles=0,cases=0,pending=0,delay_count=0,requests=0,error_code=0,error_request=0,raw_invalid=0;
integer abort_mask=0,reset_mask=0,fd,scanned,expected_error,timeout_count;
always #5 clk=~clk;
task automatic tick; begin @(posedge clk); #1; cycles++; @(negedge clk); #1; end endtask
task automatic reset_dut; begin hard_reset=1; abort=0; start_valid=0; result_ready=0; backend_rsp_valid=0; backend_req_ready=0; pending=0; tick; hard_reset=0; tick; end endtask
task automatic defaults; begin {defaults} end endtask
task automatic start_dut; begin start_valid=1; tick; start_valid=0; end endtask
task automatic service;
logic accepted,responded;
begin
 backend_req_ready=(cycles%5)!=0; backend_rsp_valid=pending!=0 && delay_count==0;
 backend_rsp_rdata=raw_invalid!=0?32'h80808080:0; backend_rsp_error=(requests==error_request)?3'(error_code):0;
 #1; accepted=backend_req_valid && backend_req_ready; responded=backend_rsp_valid;
 tick;
 if(responded)pending=0; else if(pending!=0 && delay_count>0)delay_count--;
 if(accepted)begin if(pending!=0)$fatal(1,"重复请求"); requests++;pending=1;delay_count=cycles%4;end
end endtask
initial begin
 reset_dut;
 fd=$fopen("validation_vectors.txt","r"); if(fd==0)$fatal(1,"向量文件缺失");
 while(!$feof(fd))begin
  scanned=$fscanf(fd,"{fmt}",{args});
  if(scanned!={len(names)+2})begin if(!$feof(fd))$fatal(1,"向量读取失败");break;end
  start_dut; tick;
  if(expected_error==0)begin if(result_valid)$fatal(1,"合法层校验被拒绝 case=%0d",cases); abort=1;tick;abort=0;end
  else begin if(!result_valid || result_error_code!=expected_error)$fatal(1,"独立校验黄金不同 case=%0d want=%0d got=%0d",cases,expected_error,result_error_code); result_ready=1;tick;result_ready=0;end
  cases++;reset_dut;
 end
 $fclose(fd);
 for(integer action=0;action<2;action++)begin
  for(integer state_id=0;state_id<20;state_id++)begin
   reset_dut;defaults;requests=0;error_code=0;error_request=0;if(state_id!=0)start_dut;timeout_count=0;
   while(int'(u_dut.state)!=state_id && timeout_count<20000)begin service;timeout_count++;end
   if(timeout_count==20000)$fatal(1,"状态不可达state=%0d",state_id);
   if(action==0)begin abort=1;abort_mask|=1<<state_id;end else begin hard_reset=1;reset_mask|=1<<state_id;end
   service; abort=0;hard_reset=0;pending=0;backend_rsp_valid=0;tick;
   if(busy || result_valid || !start_ready)$fatal(1,"复位abort未回IDLE");
  end
 end
 for(integer code=0;code<8;code++)begin
  for(integer request_target=1;request_target<=3;request_target++)begin
   reset_dut;defaults;requests=0;error_code=code;error_request=(request_target==1?1:request_target==2?49:265);start_dut;
   timeout_count=0;while(!result_valid && timeout_count<20000)begin
    // owner低不取消已接受合法任务；输入batch改变不能改变锁存状态。
    if(timeout_count>2)begin buffer_owner_pl=0;input_batch_count=32'hffffffff;output_batch_count=0;end
    service;timeout_count++;
   end
   if(!result_valid)$fatal(1,"响应错误或成功超时code=%0d target=%0d",code,request_target);
   expected_error=(code==0?0:code==1?1:code==2?2:6);
   if(result_error_code!=expected_error)$fatal(1,"响应映射不同code=%0d target=%0d got=%0d",code,request_target,result_error_code);
   repeat(7)service;result_ready=1;service;result_ready=0;
  end
 end
 reset_dut;defaults;requests=0;error_code=0;error_request=0;raw_invalid=1;start_dut;timeout_count=0;
 while(!result_valid && timeout_count<20000)begin service;timeout_count++;end
 if(!result_valid || result_error_code!=1)$fatal(1,"raw80拒绝语义不同");
 $display("PASS CONV_VALIDATION vectors=%0d cycles=%0d abort_mask=%x reset_mask=%x response_cases=24 raw80=1",cases,cycles,abort_mask,reset_mask);
 $finish;
end
endmodule
"""

def layer0_tb():
    """精确复用冻结T66公开端口黑盒，另加双完整模块全输出比较。"""
    text=(ROOT/"sim/tb_s2a_t66_candidate_blackbox.sv").read_text(encoding="utf-8")
    m=re.search(r"    s2a_conv_tile_engine u_dut \(.*?\n    \);",text,re.S)
    if not m:raise ValueError("T66唯一实例缺失")
    return text.replace(m[0],m[0]+"\n"+pair(m[0])).replace("tb_s2a_t66_candidate_blackbox","tb_s2b_conv_layer0")

def main():
    """独占新Run，冻结全部实际源码后单job构建；失败原件保留。"""
    parser=argparse.ArgumentParser();parser.add_argument("--run-id",required=True);parser.add_argument("--mode",choices=("boundary","layer0"),required=True)
    parser.add_argument("--toolchain",type=Path,default=Path("D:/FPGA_S2A_MSYS2_20261001/env"));parser.add_argument("--prepare-only",action="store_true");args=parser.parse_args()
    if not re.fullmatch(r"conv_validation_20261011_r\d+",args.run_id):raise ValueError("RunId不符")
    work=ROOT/"tmp/2B/S2B-T17"/args.run_id;evidence=ROOT/"report/evidence/S2B-T17"/args.run_id
    for p in (work,evidence):
        if not p.parent.is_dir() or p.exists():raise ValueError("父目录缺失或Run已存在")
        p.mkdir()
    report={"schema_version":1,"task_id":"S2B-T17-S4","run_id":args.run_id,"mode":args.mode,"source_baseline_commit":BASELINE,"status":"FAIL","runs":[]}
    begin=time.monotonic()
    try:
        checker=support.load_checker();bindings=checker.check_static(ROOT)
        bindings.update({p:support.sha(ROOT/p) for p in (RUNNER,"verification/test_s2b_backend_coordinates_rtl.py","sim/tb_s2a_t66_candidate_blackbox.sv","verification/s1_t02_d2_int8_forward.py",support.MODEL)})
        report["source_sha256_pre"]=bindings;report["frozen14_sha256"]={p:support.sha(ROOT/p) for p in checker.FROZEN_CORE_SHA256}
        actual=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip();report["source_commit"]=actual
        if subprocess.check_output(["git","diff","--name-only",BASELINE,actual,"--",*bindings],cwd=ROOT,text=True).strip():raise ValueError("相关已提交源码偏离基线")
        report["checker_negatives"]=support.checker_negatives(checker,work,checker.check_static(ROOT))
        if support.sha(ROOT/support.MODEL)!=support.MODEL_SHA:raise ValueError("冻结manifest SHA漂移")
        # D2原件为CRLF；冻结Git blob为LF，只有关系核验规范换行，仍另绑实际rawSHA。
        d2raw=(ROOT/"verification/s1_t02_d2_int8_forward.py").read_bytes()
        if hashlib.sha256(d2raw.replace(b"\r\n",b"\n")).hexdigest()!="5dfdbb4a9e57256b362629a2de40b9724df6d28ae225ce6d6622429b9cbad393":raise ValueError("D2规范源内容漂移")
        model=json.loads((ROOT/support.MODEL).read_text(encoding="utf-8")); names,text,small,math_report=vectors(model)
        report["math_oracle"]=math_report
        (evidence/"math_oracle.json").write_text(json.dumps(math_report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for directory in (work,evidence):(directory/"validation_vectors.txt").write_text(text,encoding="utf-8")
        report["resource_preflight"]={"available_ram_bytes":psutil.virtual_memory().available,"disk_free_bytes":shutil.disk_usage(work).free,
          "running_tools":[{"pid":p.pid,"name":p.info["name"],"rss":p.memory_info().rss} for p in psutil.process_iter(["name"]) if p.info["name"] and p.info["name"].lower() in ("vivado.exe","verilator_bin.exe","cc1plus.exe","vtb_s2b_conv_layer0.exe","vtb_s2b_conv_validation.exe")],"rss_limit_bytes":1610612736,"cache_limit_bytes":314572800,"heavy_slot":"root已授权唯一槽；job1/thread1"}
        if report["resource_preflight"]["available_ram_bytes"]<2147483648:raise ValueError("可用内存不足")
        source=work/"source";source.mkdir()
        for p in RTL:shutil.copyfile(ROOT/p,source/Path(p).name)
        top="tb_s2b_conv_validation" if args.mode=="boundary" else "tb_s2b_conv_layer0"
        bench=boundary_tb(names,small) if args.mode=="boundary" else layer0_tb()
        for directory in (work,evidence):(directory/(top+".sv")).write_text(bench,encoding="utf-8",newline="\n")
        if args.mode=="layer0":
            report["fixture_bindings"]=[]
            for name,(size,digest) in FIXED.items():
                path=checker.exact_file(FIXTURE/name)
                if path.stat().st_size!=size or support.sha(path)!=digest:raise ValueError("冻结T25夹具漂移")
                report["fixture_bindings"].append({"path":str(path),"bytes":size,"sha256":digest})
            report["independent_cpu_layer0"]=cpu_layer0(model,evidence,checker)
        env=os.environ.copy();tools=args.toolchain/"mingw64/bin";make=args.toolchain/"usr/bin";verilator=checker.exact_file(tools/"verilator_bin.exe")
        env["PATH"]=str(make)+os.pathsep+str(tools)+os.pathsep+env.get("PATH","");env["VERILATOR_ROOT"]=str(args.toolchain/"mingw64/share/verilator");env["PYTHONUTF8"]="1"
        report["tool_versions"]={"python":sys.version,"verilator":subprocess.check_output([str(verilator),"--version"],cwd=work,env=env,text=True).strip()}
        cmd=[str(verilator),"--binary","--timing","--timescale","1ns/1ps","-Wall","-Wno-fatal","-j","1","--threads","1","--output-split","10000","--output-split-cfuncs","100","--top-module",top,"--Mdir","obj_dir","-MAKEFLAGS","PYTHON3='\""+sys.executable+"\"'","-CFLAGS","-D_GLIBCXX_USE_CXX11_ABI=0 -O1",*["source/"+Path(p).name for p in RTL],top+".sv"]
        report["compile_command"]=cmd
        if args.prepare_only:report["status"]="PREPARED_NOT_RUN"
        else:
            support.execute("compile",cmd,work,evidence,env,report,900)
            sim=[str(work/("obj_dir/V"+top+".exe"))]
            if args.mode=="layer0":sim += ["+T66_"+kind+"_PATH="+str(FIXTURE/name).replace("\\","/") for kind,name in zip(("INPUT","WEIGHT","GOLDEN"),FIXED)]
            support.execute("simulation",sim,work,evidence,env,report,1200)
            log=(evidence/"simulation.log").read_text(encoding="utf-8")
            marker="PASS CONV_VALIDATION" if args.mode=="boundary" else "PASS: T66 candidate blackbox sample0 layer0 full tensor matched T25; bytes=1384448 mismatches=0"
            if log.count(marker)!=1:raise ValueError("唯一通过标记缺失")
            if args.mode=="boundary":
                m=re.search(r"PASS CONV_VALIDATION vectors=(\d+) cycles=(\d+) abort_mask=([a-fA-F0-9]+) reset_mask=([a-fA-F0-9]+) response_cases=24 raw80=1",log)
                if not m or int(m[1])!=math_report["vectors"] or int(m[3],16)!=0xfffff or int(m[4],16)!=0xfffff:raise ValueError("实际边界覆盖不完整")
                report["actual_coverage"]={"vectors":int(m[1]),"cycles":int(m[2]),"abort_mask":m[3],"reset_mask":m[4],"response_cases":24,"raw80":1}
            else:
                m=re.search(r"bytes=(\d+) mismatches=0 input_reads=(\d+) weight_reads=(\d+) output_writes=(\d+) requests=(\d+) responses=(\d+) request_stalls=(\d+) response_stalls=(\d+) cycles=(\d+)",log)
                if not m or tuple(map(int,(m[1],m[4],m[5],m[6])))!=(1384448,1384448,2551955,2551955):raise ValueError("完整layer0实际请求/输出覆盖不符")
                report["actual_coverage"]=dict(zip(("bytes","input_reads","weight_reads","output_writes","requests","responses","request_stalls","response_stalls","cycles"),map(int,m.groups())))
            report["pass_marker"]=marker;report["status"]="PASS"
        report["source_sha256_post"]={p:support.sha(ROOT/p) for p in bindings}
        if report["source_sha256_post"]!=bindings:raise ValueError("验证期间源码改变")
    except Exception as exc:report["status"]="FAIL";report["error"]=repr(exc)
    finally:
        report["elapsed_seconds"]=round(time.monotonic()-begin,3);report["thread_environment"]=CPU_THREAD_ENV;report["runner_peak_self_working_set_bytes"]=getattr(psutil.Process().memory_info(),"peak_wset",None)
        report["limitations"]=["G2、综合/STA、postroute、bit、G3未执行；物理接口未冻结。","仅本模式覆盖；不声明109整网或CSR/runtime deadline实板联调。","状态仅只读定位abort/reset；黄金独立于派生乘积。"]
        (evidence/"validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"evidence":str(evidence),"seconds":report["elapsed_seconds"],"error":report.get("error")},ensure_ascii=False))
    return 0 if report["status"] in ("PASS","PREPARED_NOT_RUN") else 2

if __name__=="__main__":raise SystemExit(main())
