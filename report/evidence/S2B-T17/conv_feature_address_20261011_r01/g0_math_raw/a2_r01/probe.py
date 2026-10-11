#!/usr/bin/env python3
"""验证仅在原bounds内消费低32行坐标的A2纯整数证明。"""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import subprocess
import time

WORK=Path(__file__).resolve().parent
ROOT=WORK.parents[4]
SOURCE=ROOT/"src/s2b_conv_tile_engine.sv"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original_sha=sha(SOURCE)
assert original_sha=="ea3e123327827a2d090a705bb7e364af29cf7e1088bc86c7bd54bf55e36df5fc"
oracle_path=WORK.parent/"math_r02/math_diagnosis.py"
spec=importlib.util.spec_from_file_location("old_nested_math",oracle_path)
oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
started=time.monotonic();rng=random.Random(0x5A1022)
prior=json.loads((WORK.parent/"math_r02/result.json").read_text(encoding="utf-8"))
cases=[("g0_manual_"+x["name"],x["input"]) for x in prior["manual"]]
U32=oracle.U32;U64=oracle.U64
for name,h,y in (("H_zero",0,0),("Y_zero",1,0),("Y_bit32",U32,1<<32),("Y_equal_Hmax",U32,U32),("Y_max_consumed",U32,U32-1)):
    if y==1<<32:v=[1,h,U32,65536,65536,0,0,0,0,0,0,0,1,1,0,1]
    else:v=[1,h,U32,0,0,y,0,0,0,0,0,0,1,1,0,1]
    cases.append((name,v))
for c,h,w in itertools.product((0,1,2,65536,0x80000000,U32),repeat=3):
    cases.append(("extreme_C_H_W",[c,h,w,0,0,0,0,0,0,0,0,U32,1,1,0,1]))
for _ in range(100000):cases.append(("random_full_u32",[rng.getrandbits(32) for _ in range(16)]))
for _ in range(50000):
    c,h,w,base=[rng.getrandbits(32) for _ in range(4)]
    cases.append(("random_inbounds",[c,h,w,0,0,rng.randrange(h) if h else 0,0,0,0,rng.randrange(w) if w else 0,0,base,1,1,0,1]))
categories={};branches={};manual=[];consumed=0
for name,v in cases:
    old=oracle.eval_case(v)
    row=0;offset=0;address=0
    if old["bounds"]:
        y=old["signed_y"];x=old["signed_x"]
        assert 0<=y<v[1]<=U32 and (y>>32)==0
        full_row=((y&U64)*v[2])&U64
        row=(y&U32)*v[2]
        assert row==full_row and row<=U64
        channel=(v[0]*(v[1]*v[2]))&U64
        offset=(channel+row+(x&U64))&U64
        address=(v[11]+offset)&U64
        consumed+=1
    assert offset==old["offset"] and address==old["address"]
    categories[name]=categories.get(name,0)+1
    branches[old["branch"]]=branches.get(old["branch"],0)+1
    if not name.startswith("random") and name!="extreme_C_H_W":manual.append({"name":name,"input":v,"signed_y":old["signed_y"],"signed_x":old["signed_x"],"bounds":old["bounds"],"new_row_default_or_consumed":row,"offset":offset,"address":address,"branch":old["branch"]})
report={"status":"PASS_A2_PURE_INTEGER_G0_ONLY","seed_hex":"0x5a1022","samples":len(cases),"inbounds_consumed":consumed,"categories":categories,"branches":branches,"manual":manual,"source_raw_sha256":original_sha,"old_nested_oracle":{"path":str(oracle_path),"sha256":sha(oracle_path)},"proof":"原bounds蕴含0<=signedY<H<=2^32-1，故0<=Y<=2^32-2且Y[63:32]=0；H=0时bounds不可能真。仅在bounds内full unsigned Y64*W32与zeroext(Ylow32)*W32逐位相同，后者32x32结果精确64。未bounds时row/offset/address默认0，不消费低32别名。channel与base仍原模64，不增加错误守卫。","boundary_semantics":["bit63=1的signedY为负，原bounds拒绝；bit63=0而bit32及以上非零的Y>=2^32>H，原bounds拒绝。","Y=U32,H=U32因严格小于拒绝；Y=U32-1,H=U32可消费且row精确64。","Y负值或高位非零即使low32别名0，仍保持padding；禁止改变bounds生成或比较。"],"scope":"只证明被原bounds消费的row乘法；新内部row信号无需匹配A在未消费分支的任意中间值。全原公开与内部旧字段仍须后续RTL全字段差分。","sta":"NOT_RUN；从可含高位的Y64乘W32改为显式零扩展Y32乘W32可能减少有效乘法位宽/DSP深度，但工具可能已优化原门控，不承诺改善或通过。","elapsed_seconds":time.monotonic()-started}
assert sha(SOURCE)==original_sha
with (WORK/"result.json").open("x",encoding="utf-8",newline="\n") as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write("\n")
print(json.dumps({"status":report["status"],"samples":report["samples"],"inbounds_consumed":consumed,"branches":branches,"elapsed_seconds":report["elapsed_seconds"],"result_sha256":sha(WORK/"result.json"),"script_sha256":sha(Path(__file__))},ensure_ascii=False))
