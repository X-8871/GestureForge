"""准备ROUTE通用与私有完整query边界，独立旧黄金不改，暂不编译。"""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import re
import subprocess
import sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
WORK=HERE/"route_input";assert not WORK.exists();WORK.mkdir()
sys.path.insert(0,str(ROOT/"verification"))
import test_s2b_backend_coordinates_rtl as support
import test_s2b_route_specialization_rtl as route
import test_s2b_route_address_guard_rtl as guard
BASELINE="891f750045ce141a8152c96025da559ff1d3a321"
raw=(ROOT/"src/s2b_route_query.sv").read_bytes()
assert hashlib.sha256(raw).hexdigest()=="48a3c7fe7a92d5b89b53c256d74cbc9e074b0408e88b4e08ec68334c9ad53905"
oldraw=subprocess.check_output(["git","-c","core.longpaths=true","-c","maintenance.auto=false","show",BASELINE+":src/s2b_route_query.sv"],cwd=ROOT)
assert hashlib.sha256(oldraw).hexdigest()=="5953287f838c91a0e342c98c39d2ff43aa0bbf17fd7bc98e89767bce09305a8e"
model=json.loads((ROOT/support.MODEL).read_text(encoding="utf-8"))
ports=guard.query_ports();inputs=[n for d,w,n in ports if d=="input"];outputs=[n for d,w,n in ports if d=="output"]
assert len(inputs)==24 and len(outputs)==8
tuples=set()
for row in model["layers"]:
    if row["op"]!="route":continue
    for source in row["input_tensor_indices"]:tuples.add(tuple(model["layers"][source]["output_shape_nchw"][1:]))
assert len(tuples)==7
counts=Counter();total=0;private_hits=0;private_misses=0
stream=(WORK/"vectors.dat").open("x",encoding="utf-8",newline="\n")
def add(kind,v,expected=None):
    """所有八个通用输出仍由冻结S6独立oracle生成。"""
    global total,private_hits,private_misses
    gold=guard.query_oracle(v) if expected is None else expected
    hit0=(v["source0_channels"],v["source0_height"],v["source0_width"]) in tuples
    hit1=v["source_count"]!=2 or (v["source1_channels"],v["source1_height"],v["source1_width"]) in tuples
    hit=hit0 and hit1
    # 私有不匹配分支明确ARG；其余完整旧query错误顺序完全不变。
    private=gold if hit else (0,0,0,0,0,0,0,1)
    row=[v[n]&((1<<8)-1 if n.endswith("value") else (1<<32)-1) for n in inputs]+list(gold)+list(private)+[int(hit)]
    stream.write(" ".join(f"{x:x}" for x in row)+"\n")
    counts[kind]+=1;total+=1;private_hits+=int(hit);private_misses+=int(not hit)
generic,metadata=guard.cases()
for v,gold in generic:add("old_generic_"+str(gold[-1]),v,gold)
del generic
layers=[]
for index,row in enumerate(model["layers"]):
    if row["op"]!="route":continue
    base=route.layer_values(model,index);base.update(source0_value=23,source1_value=-31)
    layers.append(index)
    for ch,y,x in itertools.product((0,row["output_shape_nchw"][1]-1),(0,row["output_shape_nchw"][2]-1),(0,row["output_shape_nchw"][3]-1)):
        add("private_frozen_corners",dict(base,output_channel=ch,output_y=y,output_x=x))
    for raw_value in range(-128,128):
        for ch in (0,row["output_shape_nchw"][1]-1):add("private_all_int8",dict(base,output_channel=ch,source0_value=raw_value,source1_value=raw_value))
    for slot in range(base["source_count"]):
        for field in ("channels","height","width"):
            changed=dict(base);changed[f"source{slot}_{field}"]^=1<<16
            if field=="channels":changed[f"source{slot}_channel_end"]=changed[f"source{slot}_{field}"]
            add("private_full96_high_alias",changed)
        shape=base[f"source{slot}_channels"]*base[f"source{slot}_height"]*base[f"source{slot}_width"]
        for length in (0,shape-1,shape,shape+1,0xffffffff):
            add("private_length_range_priority",dict(base,**{f"source{slot}_length_bytes":length}))
        for address in (0,0xffffffff-shape,0x100000000-shape,0xffffffff):
            add("private_base_range_priority",dict(base,**{f"source{slot}_base_address":address}))
    if base["source_count"]==1:
        unused=dict(base)
        for field in inputs:
            if field.startswith("source1_"):unused[field]=-128 if field.endswith("value") else 0xffffffff
        add("private_count1_unused_source1_all_high",unused)
        unused0=dict(base)
        for field in inputs:
            if field.startswith("source1_"):unused0[field]=-128 if field.endswith("value") else 0
        add("private_count1_unused_source1_all_zero",unused0)
        add("private_count2_consumes_invalid_source1",dict(unused0,source_count=2))
stream.close()
old=oldraw.decode("utf-8").replace("module s2b_route_query (","module s12_route_query_original (")
current=raw.decode("utf-8")
alias=current.replace("module s2b_route_query #(","module s12_route_query_alias #(").replace("case (shape_key)","case (shape_key & 96'h0000ffff0000ffff0000ffff)")
needle="        if (source_count == 32'd2) begin\n            if (FROZEN_ROUTE_SHAPES) begin"
assert current.count(needle)==1
unused=current.replace("module s2b_route_query #(","module s12_route_query_unused #(").replace(needle,"        if (1'b1) begin\n            if (FROZEN_ROUTE_SHAPES) begin")
for name,text in (("s12_route_query_original.sv",old),("s2b_route_query.sv",current),("s12_route_query_alias.sv",alias),("s12_route_query_unused.sv",unused)):
    (WORK/name).write_text(text,encoding="utf-8",newline="\n")
decl="\n".join(f"logic {w} v_{n};" if d=="input" else f"logic {w} old_{n},generic_{n},private_{n},alias_{n},unused_{n};" for d,w,n in ports)
gold="\n".join(f"logic {w} gold_{n},private_gold_{n};" for d,w,n in ports if d=="output")
inst=[]
for prefix,module,param in (("old","s12_route_query_original",""),("generic","s2b_route_query",""),("private","s2b_route_query"," #(.FROZEN_ROUTE_SHAPES(1'b1))"),("alias","s12_route_query_alias"," #(.FROZEN_ROUTE_SHAPES(1'b1))"),("unused","s12_route_query_unused"," #(.FROZEN_ROUTE_SHAPES(1'b1))")):
    inst.append(module+param+" u_"+prefix+" ("+",".join(f".{n}({'v_' if d=='input' else prefix+'_'}{n})" for d,w,n in ports)+");")
fmt=" ".join("%h" for _ in range(41))+"\\n";arguments=",".join(["v_"+n for n in inputs]+["gold_"+n for n in outputs]+["private_gold_"+n for n in outputs]+["domain_hit"])
checks="\n".join(f'if({prefix}_{n}!=={g}_{n})$fatal(1,"ROUTE全字段{prefix}.{n} case=%0d",count);' for prefix,g in (("old","gold"),("generic","gold"),("private","private_gold")) for n in outputs)
alias_diff=" || ".join(f"alias_{n}!==private_gold_{n}" for n in outputs)
unused_diff=" || ".join(f"unused_{n}!==private_gold_{n}" for n in outputs)
tb=f'''// 完整旧/通用/私有query；所有值经公开端口注入，无内部强制。
`timescale 1ns/1ps
module tb_s12_route_private;
{decl}
{gold}
{chr(10).join(inst)}
integer fd,n,count=0,domain_hit=0,hits=0,misses=0,alias_kills=0,unused_kills=0;string vector_path;
initial begin
if(!$value$plusargs("VECTOR_PATH=%s",vector_path))$fatal(1,"向量路径缺失");
fd=$fopen(vector_path,"r");if(!fd)$fatal(1,"向量缺失");
while(!$feof(fd))begin n=$fscanf(fd,"{fmt}",{arguments});
if(n==41)begin #1;
{checks}
if({alias_diff})alias_kills++;
if({unused_diff})unused_kills++;
if(domain_hit)hits++;else misses++;count++;
end else if(n!=-1)$fatal(1,"字段数错误");end
if(!alias_kills||!unused_kills)$fatal(1,"ROUTE实际语义变体未击杀");
$display("PASS S12_ROUTE_PRIVATE vectors=%0d hits=%0d misses=%0d alias=%0d unused=%0d",count,hits,misses,alias_kills,unused_kills);$finish;
end
endmodule
'''
(WORK/"tb_s12_route_private.sv").write_text(tb,encoding="utf-8",newline="\n")
receipt={"status":"PREPARED_NOT_RUN","source_commit":BASELINE,"vectors":total,"categories":dict(counts),"private_hit_vectors":private_hits,"private_miss_vectors":private_misses,"route_layers":layers,"frozen_shape_tuples":sorted(tuples),"old_generic_coverage":metadata,"old_raw_sha256":hashlib.sha256(oldraw).hexdigest(),"candidate_raw_sha256":hashlib.sha256(raw).hexdigest(),"oracle_sha256":support.sha(ROOT/"verification/test_s2b_route_address_guard_rtl.py"),"oracle_scope":"原S6独立整数oracle完全不变；私有miss仅明确ARG新增不可达域差异；count1不消费source1。","files":[{"path":str(p),"sha256":support.sha(p),"role":"source" if p.suffix==".sv" else "input"} for p in sorted(WORK.iterdir()) if p.is_file()],"limits":"只准备，尚未编译/仿真/变体击杀；与backend实际START完整trace及default0公共周期回归互补。"}
(WORK/"prepared_receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"status":receipt["status"],"vectors":total,"hits":private_hits,"misses":private_misses,"bytes":sum(p.stat().st_size for p in WORK.iterdir())},ensure_ascii=False))
