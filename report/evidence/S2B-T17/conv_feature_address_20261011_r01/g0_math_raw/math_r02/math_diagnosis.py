#!/usr/bin/env python3
"""只读S10 G0源码与实际报告，纯整数检查候选恒等式，不证明RTL或STA。"""
import hashlib
import itertools
import json
from pathlib import Path
import random
import re
import subprocess
import time

WORK=Path(__file__).resolve().parent
ROOT=WORK.parents[4]
HEAD="38c5bc02f42920d4203aa6752530d09c80fc4c57"
U32=(1<<32)-1
U64=(1<<64)-1
SEED=0x5A1011
sha=lambda data:hashlib.sha256(data).hexdigest()


def signed64(value):
    """还原原SV signed64赋值的二补码解释。"""
    value&=U64
    return value-(1<<64) if value&(1<<63) else value


def eval_case(v):
    """旧嵌套式与候选各自计算；坐标生成/门控/消费顺序完全保留。"""
    c,h,w,ty,sy,fy,py,tx,sx,fx,px,base,ph,pw,index,count=v
    gate=bool(ph*pw and pw)
    y=signed64(ty*sy+fy-py) if gate else 0
    x=signed64(tx*sx+fx-px) if gate else 0
    bounds=gate and 0<=y<h and 0<=x<w
    old=((((c*h)&U64)+(y&U64))&U64)*w+(x&U64)
    old=old&U64 if bounds else 0
    plane=h*w
    channel=(c*plane)&U64
    row=((y&U64)*w)&U64
    new=(channel+row+(x&U64))&U64 if bounds else 0
    old_addr=(base+old)&U64 if bounds else 0
    new_addr=(base+new)&U64 if bounds else 0
    branch="END" if index>=count else "PADDING" if not bounds else "RANGE" if old_addr>U32 else "REQUEST"
    assert old==new and old_addr==new_addr
    return {"input":v,"signed_y":y,"signed_x":x,"gate":gate,"bounds":bounds,"offset":old,"address":old_addr,"branch":branch}


def main():
    """快照绑定只读输入与轻量数学原件，禁止写正式证据或生产。"""
    started=time.monotonic()
    actual=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True)
    assert actual.returncode==0 and actual.stdout.decode().strip()==HEAD
    source=ROOT/"src/s2b_conv_tile_engine.sv"
    obj=subprocess.run(["git","show",HEAD+":src/s2b_conv_tile_engine.sv"],cwd=ROOT,capture_output=True)
    assert obj.returncode==0
    source_raw=source.read_bytes()
    assert source_raw.replace(b"\r\n",b"\n")==obj.stdout.replace(b"\r\n",b"\n")
    (WORK/"source_git_object.sv").write_bytes(obj.stdout)
    (WORK/"source_worktree_raw.sv").write_bytes(source_raw)
    reports=[]
    for name in ("timing_summary_synth.rpt","timing_worst_synth.rpt","utilization_flat_synth.rpt"):
        path=ROOT/"report/evidence/S2B-T17/s9_platform_20261011_r01"/name
        assert path.is_file()
        data=path.read_bytes();(WORK/name).write_bytes(data)
        reports.append({"path":str(path),"sha256":sha(data),"bytes":len(data)})
    upstream=ROOT/"report/evidence/S2B-T17/conv_output_address_20261011_r03/source_freeze.json"
    frozen=json.loads(upstream.read_text(encoding="utf-8"))["frozen14"]
    assert len(frozen)==14 and all(sha((ROOT/p).read_bytes())==h for p,h in frozen.items())
    manual=[]
    # 顺序为C/H/W/TY/SY/FY/PY/TX/SX/FX/PX/base/PH/PW/index/count。
    manual.append(("ordinary",[3,13,13,8,1,4,1,8,1,4,1,100,2,2,0,4]))
    manual.append(("negative_y_padding",[0,1,1,0,1,0,1,0,1,0,0,U32,1,1,0,1]))
    manual.append(("signed_signbit_padding",[1,U32,U32,U32,U32,0,0,0,1,0,0,0,1,1,0,1]))
    manual.append(("negative_large_signed_padding",[0,1,1,U32,U32,U32,U32-1,0,1,0,0,0,1,1,0,1]))
    manual.append(("offset64_wrap",[0x80000000,65536,131072,0,0,0,0,0,0,0,0,0,1,1,0,1]))
    manual.append(("low32_offset_alias",[1,65536,65536,0,0,0,0,0,0,0,0,0,1,1,0,1]))
    manual.append(("address64_wrap",[2,0x80000000,U32,0,0,0,0,0,0,U32-1,0,2,1,1,0,1]))
    manual.append(("base33_range",[0,1,2,0,0,0,0,0,0,1,0,U32,1,1,0,1]))
    manual.append(("patch_gate_zero",[1,U32,U32,U32,U32,U32,U32,U32,U32,U32,U32,U32,0,1,0,1]))
    manual.append(("finished_scan_before_range",[1,65536,65536,0,0,0,0,0,0,0,0,0,1,1,1,1]))
    cases=[]
    for name,v in manual:cases.append(("manual_"+name,v))
    extremes=[0,1,2,65535,65536,0x7fffffff,0x80000000,U32]
    for c,h,w in itertools.product(extremes,repeat=3):
        for base in (0,1,U32):cases.append(("C_H_W_base_boundaries",[c,h,w,0,0,0,0,0,0,0,0,base,1,1,0,1]))
    rng=random.Random(SEED)
    for _ in range(100000):
        v=[rng.getrandbits(32) for _ in range(16)]
        cases.append(("random_full_u32",v))
    for _ in range(50000):
        c,h,w,base=[rng.getrandbits(32) for _ in range(4)]
        y=rng.randrange(h) if h else 0;x=rng.randrange(w) if w else 0
        cases.append(("random_consumed_coordinate",[c,h,w,0,0,y,0,0,0,x,0,base,1,1,0,1]))
    counts={};branches={};signed_negative=0;modwrap=0;results=[]
    for category,v in cases:
        result=eval_case(v);counts[category]=counts.get(category,0)+1
        branches[result["branch"]]=branches.get(result["branch"],0)+1
        signed_negative+=int(result["signed_y"]<0 or result["signed_x"]<0)
        modwrap+=int(result["bounds"] and (v[0]*v[1]*v[2]+result["signed_y"]*v[2]+result["signed_x"]>U64))
        if category.startswith("manual_"):results.append({"name":category,**result})
    report={"status":"PASS_PURE_INTEGER_G0_ONLY","source_commit":HEAD,"source_raw_sha256":sha(source_raw),"source_git_sha256":sha(obj.stdout),"source_comparison":"仅显式CRLF归一为LF后原字节一致；未修改源。","reports":reports,"frozen14":frozen,"seed":SEED,"seed_hex":hex(SEED),"samples":len(cases),"categories":counts,"branches":branches,"negative_signed_coordinate_samples":signed_negative,"full_integer_offset_exceeds_u64_consumed_samples":modwrap,"manual":results,"proof":"在Z/(2^64)中((C*H+Y)*W+X)=C*(H*W)+Y*W+X。H/W各32位非负，因此plane64=H*W精确；channel与row仍截到原unsigned64。Y/X保留原signed64坐标及原[63:0]位模式，bounds门控与地址base加法原64回绕不改。","candidate":"仅新增feature_geometry_plane[63:0]/feature_channel_plane_offset[63:0]/feature_row_offset[63:0]组合信号；原feature_scan_in_bounds分支内令plane=zeroext(H)*zeroext(W)，channel=zeroext(C)*plane，row=feature_input_y[63:0]*zeroext(W)，offset=channel+row+feature_input_x[63:0]。源offset/address默认零和所有if/FF不动。","critical_semantics":["feature_input_y/x是signed64，不是S9输出C/Y/X的低32赋值；不允许截坐标或改变零扩展乘积转signed64后的解释。","原coordinate乘加减在64位二补码回绕，bounds仅消费非负且<H/W的值；禁止新增33/65进位守卫。","ST_FEATURE_SCAN先index>=patch_byte_count，再padding，再address>U32，后请求；不得把range提前到未消费扫描/padding。","input完整验证BAD_ARGUMENT/BAD_LENGTH/BAD_RANGE优先与14冻结源全保留；不利用合法输入尺寸来删除通用域保护。"],"limitations":["纯数学证明与随机诊断，不是RTL等价、公开可达域、独审或STA证明。","DSP来源CLK说明综合可吸收已有寄存器；本轮未查询DSP参数，无法精确把feature_source_address_wide7__1唯一映射到某个乘积。","H/W→plane→channel可能成为新最差，Y stride乘加→row→address/guard仍存在，真实STA必须后续判断。"],"elapsed_seconds":time.monotonic()-started}
    with (WORK/"result.json").open("x",encoding="utf-8",newline="\n") as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write("\n")
    assert source.read_bytes()==source_raw
    print(json.dumps({"status":report["status"],"samples":len(cases),"categories":counts,"branches":branches,"elapsed_seconds":report["elapsed_seconds"],"source_raw_sha256":sha(source_raw),"result_sha256":sha((WORK/"result.json").read_bytes())},ensure_ascii=False))


if __name__=="__main__":main()
