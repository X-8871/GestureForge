"""准备完整CONV组合锥、独立旧式黄金和真实RTL变体；本脚本不编译。"""
import ast
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import random
import re
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
WORK=Path(__file__).resolve().parent/"cones_input"
assert not WORK.exists();WORK.mkdir()
sys.path.insert(0,str(ROOT/"verification"))
import test_s2b_backend_coordinates_rtl as support
import test_s2b_conv_validation_rtl as validation
U32=(1<<32)-1;U64=(1<<64)-1;SEED=0x5C120612
ENGINE="src/s2b_conv_tile_engine.sv"
sha=lambda raw:hashlib.sha256(raw).hexdigest()
raw=(ROOT/ENGINE).read_bytes()
assert sha(raw)=="c46ed3e1e8af0089b2a78434c0b34869a2b1f5cf11071688345828f4a9c28454"
oldraw=subprocess.check_output(["git","-c","core.longpaths=true","-c","maintenance.auto=false","show",validation.SOURCE_BASELINE+":"+ENGINE],cwd=ROOT)
assert sha(oldraw)=="51b76623b29a852ebf66cb818ef947d932c14055e4acbb20bd8fe811bb32d555"
old=oldraw.decode("utf-8");current=raw.decode("utf-8")
contract=validation.assert_conv_contract(old.replace("\r\n","\n"),current.replace("\r\n","\n"))
model=json.loads((ROOT/support.MODEL).read_text(encoding="utf-8"))
FIELDS=("layer_index_latched","input_channels_latched","input_height_latched","input_width_latched","output_channels_latched","output_height_latched","output_width_latched","kernel_height_latched","kernel_width_latched","stride_y_latched","stride_x_latched","pad_left_latched","pad_right_latched","pad_top_latched","pad_bottom_latched")
EXTRA=("tile_start_y","tile_start_x","group_lane_count","feature_read_in_bounds","feature_read_data","weight_byte","accumulator","compute_reduction_index","reduction_count_latched","compute_input_channel","compute_kernel_y","compute_kernel_x","compute_point_scan_y","compute_point_scan_x","patch_height","patch_width","tile_width")
GOLD=("extent_y","extent_x","ph","pw","bytes","fh","fw","fp","fb","full_bad","descriptor","hit","bad_argument","overflow","enable","channel","ky","kx","ri","iy","ix","bounds","index64","index32")
WIDTH={"fh":19,"fw":19,"fb":29,"full_bad":1,"descriptor":98,"hit":1,"bad_argument":1,"overflow":1,"enable":1,"iy":64,"ix":64,"bounds":1,"index64":64}

def signed(value,bits):
    """在原节点按补码解释符号。"""
    value&=(1<<bits)-1
    return value-(1<<bits) if value&(1<<(bits-1)) else value

def oracle(v,state,tuples):
    """独立原嵌套式和原U32/64赋值节点，未读取候选表结果。"""
    d=dict(zip(FIELDS+EXTRA,v));g={}
    lid,c,h,w,oc,oh,ow,kh,kw,sy,sx,pl,pr,pt,pb=v[:15]
    ey=min((oh-d["tile_start_y"])&U32,8);ex=min((ow-d["tile_start_x"])&U32,8)
    ph=(((ey-1)&U32)*sy+kh)&U32;pw=(((ex-1)&U32)*sx+kw)&U32
    g.update(extent_y=ey,extent_x=ex,ph=ph,pw=pw,bytes=(ph*pw*c)&U32)
    dy=0 if oh==0 else oh-1 if oh<8 else 7;dx=0 if ow==0 else ow-1 if ow<8 else 7
    fh=(dy*(sy&65535)+(kh&8191))&((1<<19)-1)
    fw=(dx*(sx&65535)+(kw&8191))&((1<<19)-1)
    fp=((fh&65535)*(fw&65535))&U32;fb=((fp&65535)*(c&8191))&((1<<29)-1)
    bad=int(bool((dy and sy>>16) or fh>>16 or (fh&65535)>51200 or (dx and sx>>16) or fw>>16 or (fw&65535)>51200 or fp>>16 or fb>51200))
    g.update(fh=fh,fw=fw,fp=fp,fb=fb,full_bad=bad)
    hit=int(tuple(v[:15]) in tuples)
    g["hit"]=hit;g["descriptor"]=((1<<97)|((c*kh)<<71)|((c*kh*kw)<<45)|(oc*c*kh*kw)) if hit else 0
    f=signed(d["feature_read_data"],8) if d["feature_read_in_bounds"] else 0
    weight=signed(d["weight_byte"],8);acc=signed(d["accumulator"],32)
    badarg=int(d["group_lane_count"]!=0 and d["feature_read_in_bounds"]!=0 and (f==-128 or weight==-128))
    summ=acc+f*weight;overflow=int(d["group_lane_count"]!=0 and (summ<-(1<<31) or summ>(1<<31)-1))
    c0=d["compute_input_channel"];y0=d["compute_kernel_y"];x0=d["compute_kernel_x"];ri=d["compute_reduction_index"]
    c1,y1,x1=c0,y0,x0
    if ((x0+1)&U32)>=kw:
        x1=0
        if ((y0+1)&U32)>=kh:y1=0;c1=(c0+1)&U32
        else:y1=(y0+1)&U32
    else:x1=(x0+1)&U32
    enable=state in (1,2) or (state==3 and ((ri+1)&U32)<d["reduction_count_latched"] and not badarg and not overflow)
    if state in (1,2):cc=yy=xx=rr=0
    elif state==3 and enable:cc,yy,xx,rr=c1,y1,x1,(ri+1)&U32
    else:cc,yy,xx,rr=c0,y0,x0,ri
    iy=ix=index64=bounds=0
    if ((kh*kw)&U32)!=0 and d["tile_width"]!=0:
        py=d["compute_point_scan_y"];px=d["compute_point_scan_x"]
        iy=signed(d["tile_start_y"]*sy+py*sy+yy-pt,64)
        ix=signed(d["tile_start_x"]*sx+px*sx+xx-pl,64)
        bounds=int(0<=iy<h and 0<=ix<w)
        index64=(cc*d["patch_height"]*d["patch_width"]+(py*sy+yy)*d["patch_width"]+px*sx+xx)&U64
    g.update(bad_argument=badarg,overflow=overflow,enable=int(enable),channel=cc,ky=yy,kx=xx,ri=rr,iy=iy&U64,ix=ix&U64,bounds=bounds,index64=index64,index32=index64&U32)
    return tuple(g[n] for n in GOLD)

tuples=[]
for row in model["layers"]:
    if row["op"]!="convolutional":continue
    tuples.append((row["layer_index"],*row["input_shape_nchw"][1:],*row["output_shape_nchw"][1:],*row["kernel_hw"],*row["stride_hw"],*row["padding_lrtb"]))
# 模型独立tuple逐字段核验固定规则，再生成独立黄金。
checker=support.load_checker();checker.check_static(ROOT)
assert tuple(tuples)==checker.S12_CONV_FROZEN_FIELDS and len(tuples)==21
counts=Counter();rng=random.Random(SEED);vector_count=0
vector_stream=(WORK/"vectors.dat").open("x",encoding="utf-8",newline="\n")
def add(kind,v,state):
    """流式保存向量，避免重复大列表超过轻量内存预算。"""
    global vector_count
    gold=oracle(v,state,tuples);counts[kind]+=1;vector_count+=1
    vector_stream.write(" ".join(f"{x:x}" for x in (*v,state,*gold))+"\n")
base_extra=(0,0,1,1,1,1,0,0,2,0,0,0,0,0,1,1,8)
for fields in tuples:
    for ey,ex in itertools.product(range(9),repeat=2):
        extras=list(base_extra);extras[0]=(fields[5]-ey)&U32;extras[1]=(fields[6]-ex)&U32
        add("frozen_extent81",tuple(fields)+tuple(extras),3)
    for field in range(15):
        changed=list(fields);changed[field]^=1<<16
        add("frozen_high16_alias_miss",tuple(changed)+base_extra,3)
manual=[("extent0_wrap",(0,1,4,4,32,0,0,3,3,U32,U32,0,0,0,0)+base_extra,3),
        ("bad_argument_blocks_next",tuples[0]+tuple(list(base_extra[:4])+[128]+list(base_extra[5:])),3),
        ("overflow_blocks_next",tuples[0]+tuple(list(base_extra[:6])+[0x7fffffff]+list(base_extra[7:])),3),
        ("ri32_wrap",tuples[0]+tuple(list(base_extra[:7])+[U32]+list(base_extra[8:])),3)]
for name,v,state in manual:add(name,v,state)
for j in range(120000):
    # 每项保留完整U32字段；定期选择冻结tuple使next-read有效域也充分覆盖。
    fields=tuple(rng.getrandbits(32) for _ in FIELDS) if j%3 else tuples[j%21]
    extras=[rng.getrandbits(32) for _ in EXTRA]
    extras[2]=rng.randrange(9);extras[3]=rng.randrange(2);extras[4]=rng.randrange(256);extras[5]=rng.randrange(256)
    if j%4==0:extras[7]=0;extras[8]=2
    if j%7==0:extras[4]=128
    if j%11==0:extras[4]=extras[5]=1;extras[6]=0x7fffffff
    add("generic_full_u32_and_next",tuple(fields)+tuple(extras),j%5)
vector_stream.close()

header=current.split(");",1)[0]
ports=re.findall(r"\b(input|output)\s+logic\s*((?:signed\s*)?(?:\[[^\]]+\])?)\s*(\w+)",header)
conn=",".join(f".{n}({'clk' if n=='clk' else chr(39)+'0' if d=='input' else ''})" for d,w,n in ports)
decl="\n".join(f"logic[31:0]v_{n};" for n in FIELDS+EXTRA)
gold_decl="\n".join(f"logic[{WIDTH.get(n,32)-1}:0]gold_{n};" for n in GOLD)
instances=("u_old","u_generic","u_private","u_next_mutant")
drive="\n".join(f"{inst}.{n}=v_{n};" for inst in instances for n in FIELDS+EXTRA if n not in ("weight_byte","accumulator"))
drive+="\n"+"\n".join(f"for(integer lane=0;lane<8;lane++)begin {inst}.weight_read_byte[lane]=v_weight_byte[7:0];{inst}.lane_accumulator[lane]=v_accumulator;end" for inst in instances)
states="\n".join(f"case(v_state)0:{inst}.state={inst}.ST_IDLE;1:{inst}.state={inst}.ST_COMPUTE_PREP;2:{inst}.state={inst}.ST_COMPUTE_POINT_PREP;3:{inst}.state={inst}.ST_COMPUTE;default:{inst}.state={inst}.ST_REQUANT;endcase" for inst in instances)
checks=[]
for inst in ("u_old","u_generic","u_private"):
    for signal,key in (("full_tile_patch_height_narrow","fh"),("full_tile_patch_width_narrow","fw"),("full_tile_patch_plane_narrow","fp"),("full_tile_patch_bytes_narrow","fb"),("full_tile_patch_bad","full_bad")):
        cond="gold_hit && " if inst=="u_private" else ""
        checks.append(f'if({cond}({inst}.{signal}!==gold_{key}))$fatal(1,"全tile {inst}.{signal} case=%0d",count);')
    for signal,key in (("compute_bad_argument","bad_argument"),("compute_overflow","overflow"),("compute_read_enable","enable")):
        checks.append(f'if({inst}.{signal}!==gold_{key})$fatal(1,"读enable/MAC {inst}.{signal} case=%0d",count);')
    for signal,key in (("compute_read_input_channel","channel"),("compute_read_kernel_y","ky"),("compute_read_kernel_x","kx"),("compute_read_reduction_index","ri"),("compute_read_input_y","iy"),("compute_read_input_x","ix"),("compute_read_tap_in_bounds","bounds"),("compute_read_feature_index_wide","index64"),("compute_read_feature_index","index32")):
        checks.append(f'if(gold_enable && ({inst}.{signal}!==gold_{key}))$fatal(1,"实际读取消费 {inst}.{signal} case=%0d",count);')
for inst in ("u_generic","u_private"):
    for signal,key in (("tile_prep_extent_y","extent_y"),("tile_prep_extent_x","extent_x")):
        checks.append(f'if({inst}.{signal}!==gold_{key})$fatal(1,"extent {inst} case=%0d",count);')
    for signal,key in (("tile_prep_patch_height","ph"),("tile_prep_patch_width","pw"),("tile_prep_patch_bytes","bytes")):
        expected=f"gold_{key}" if inst=="u_generic" else f"(gold_hit ? gold_{key}:32'd0)"
        checks.append(f'if({inst}.{signal}!=={expected})$fatal(1,"原FF右式 {inst}.{signal} case=%0d",count);')
checks.append('if(u_private.frozen_conv_descriptor!==gold_descriptor)$fatal(1,"完整480bit命中 case=%0d",count);')
checks.append('if(u_generic.reduction_count_bad!==u_old.reduction_count_bad || u_generic.reduction_count_wide!==u_old.reduction_count_wide || u_generic.expected_weight_bytes_wide!==u_old.expected_weight_bytes_wide)$fatal(1,"通用稳定算术不同 case=%0d",count);')
checks.append('if(gold_hit && (u_private.reduction_count_bad!==u_old.reduction_count_bad || u_private.reduction_count_wide!==u_old.reduction_count_wide || u_private.expected_weight_bytes_wide!==u_old.expected_weight_bytes_wide))$fatal(1,"私有稳定算术不同 case=%0d",count);')
function=lambda name:re.search(r"^    function automatic logic[^\n]*\b"+name+r"\(.*?    endfunction",current,re.S|re.M)[0]
# 分别提取完整生产函数并单点改写；不是Python公式替身。
descriptor=function("frozen_conv_descriptor_lookup")
tile=function("frozen_conv_tile_lookup")
full=function("frozen_full_tile_lookup")
axis=function("generic_tile_patch_axis")
mask="0000ffff"*15
mut_descriptor=descriptor.replace("frozen_conv_descriptor_lookup","mut_alias_lookup").replace("case (descriptor_key)","case (descriptor_key & 480'h"+mask+")")
assert tile.count("{32'd10, 32'd10, 32'd51200}")==1
mut_tile=tile.replace("frozen_conv_tile_lookup","mut_tile_lookup").replace("{32'd10, 32'd10, 32'd51200}","{32'd10, 32'd10, 32'd51199}")
assert full.count("{19'd10, 19'd10, 32'd100, 29'd51200}")==1
mut_full=full.replace("frozen_full_tile_lookup","mut_full_lookup").replace("{19'd10, 19'd10, 32'd100, 29'd51200}","{19'd10, 19'd10, 32'd100, 29'd51199}")
mut_axis=axis.replace("generic_tile_patch_axis","mut_axis").replace("kernel_size - stride","kernel_size")
key="{"+",".join("v_"+n for n in FIELDS)+"}"
mutchecks=f'''if(mut_alias_lookup({key})!==gold_descriptor)alias_kills++;
if(gold_hit && mut_tile_lookup({{v_layer_index_latched,gold_extent_y[3:0],gold_extent_x[3:0]}})!=={{gold_ph,gold_pw,gold_bytes}})tile_kills++;
if(gold_hit && mut_full_lookup(v_layer_index_latched)!=={{gold_fh,gold_fw,gold_fp,gold_fb}})full_kills++;
if(mut_axis(gold_extent_y,v_stride_y_latched,v_kernel_height_latched)!==gold_ph)axis_kills++;
if(u_next_mutant.compute_read_enable!==gold_enable)next_kills++;
'''
fmt=" ".join("%h" for _ in range(len(FIELDS)+len(EXTRA)+1+len(GOLD)))+"\\n"
args=",".join(["v_"+n for n in FIELDS+EXTRA]+["v_state"]+["gold_"+n for n in GOLD])
tb=f'''// 仅组合域：完整旧/通用新/私有新；内部寄存器受控，时钟恒0，无FF执行。
`timescale 1ns/1ps
module tb_s12_conv_cones;
logic clk=0;logic[31:0]v_state;
{decl}
{gold_decl}
s2b_conv_tile_engine_original u_old({conn});
s2b_conv_tile_engine u_generic({conn});
s2b_conv_tile_engine #(.FROZEN_CONV_DESCRIPTOR(1'b1)) u_private({conn});
s2b_conv_tile_engine_next_mutant u_next_mutant({conn});
{mut_descriptor}
{mut_tile}
{mut_full}
{mut_axis}
integer fd,n,count=0,alias_kills=0,tile_kills=0,full_kills=0,axis_kills=0,next_kills=0;string vector_path;
initial begin
if(!$value$plusargs("VECTOR_PATH=%s",vector_path))$fatal(1,"向量路径缺失");
fd=$fopen(vector_path,"r");if(fd==0)$fatal(1,"向量缺失");
while(!$feof(fd))begin
n=$fscanf(fd,"{fmt}",{args});
if(n=={len(FIELDS)+len(EXTRA)+1+len(GOLD)})begin
{drive}
{states}
#1;
{chr(10).join(checks)}
{mutchecks}
count++;
end else if(n!=-1)$fatal(1,"向量字段不足");
end
if(alias_kills==0||tile_kills==0||full_kills==0||axis_kills==0||next_kills==0)$fatal(1,"语义变体未被实际RTL/黄金击杀");
$display("PASS S12_CONV_CONES vectors=%0d alias=%0d tile=%0d full=%0d extent=%0d next=%0d",count,alias_kills,tile_kills,full_kills,axis_kills,next_kills);$finish;
end
endmodule
'''
bad=current.replace("module s2b_conv_tile_engine #(","module s2b_conv_tile_engine_next_mutant #(")
assert bad.count("compute_read_enable = !compute_bad_argument && !compute_overflow;")==1
bad=bad.replace("compute_read_enable = !compute_bad_argument && !compute_overflow;","compute_read_enable = 1'b1;")
for name,body in (("s2b_conv_tile_engine_original.sv",old.replace("module s2b_conv_tile_engine (","module s2b_conv_tile_engine_original (")),("s2b_conv_tile_engine.sv",current),("s2b_conv_tile_engine_next_mutant.sv",bad),("tb_s12_conv_cones.sv",tb)):
    (WORK/name).write_text(body,encoding="utf-8",newline="\n")
drivers=[]
for line_no,line in enumerate(tb.splitlines(),1):
    for inst in instances:
        matches=re.findall(re.escape(inst)+r"\.(\w+)(?:\[lane\])?=",line)
        drivers.extend({"instance":inst,"signal":signal,"tb_line":line_no,"reason":"受控组合域；clk恒0，完整引擎FF不执行"} for signal in matches)
receipt={"status":"PREPARED_NOT_RUN","source_commit":validation.SOURCE_BASELINE,"old_raw_sha256":sha(oldraw),"candidate_raw_sha256":sha(raw),"seed":SEED,"vectors":vector_count,"categories":dict(counts),"frozen_conv_fields":tuples,"model_sha256":sha((ROOT/support.MODEL).read_bytes()),"ff_exception":contract,"controlled_drivers":drivers,"mutants":["480bit高16位别名","tile51200改51199","fulltile51200改51199","extent0丢减法回绕","完整模块next-read漏MAC禁止"],"comparison_scope":"generic全U32稳定算术/extent0..8原FF右式；private仅21完整480bit命中/1701extent；读enable全向量，坐标/地址仅enable消费；未消费新内部next坐标可不同，公共输出回归不放宽。","files":[{"path":str(p),"sha256":sha(p.read_bytes()),"role":"source" if p.suffix==".sv" else "input"} for p in sorted(WORK.iterdir()) if p.is_file()],"limitations":"尚未编译、仿真、语义击杀或STA；本bench不是公开START可达轨迹，公开cycles/3FF实际写入由boundary及private layer0另证。"}
(WORK/"prepared_receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"status":receipt["status"],"vectors":vector_count,"categories":dict(counts),"bytes":sum(p.stat().st_size for p in WORK.iterdir()),"mutants":5},ensure_ascii=False))
