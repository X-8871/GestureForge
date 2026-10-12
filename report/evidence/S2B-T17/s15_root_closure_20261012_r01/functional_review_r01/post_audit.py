"""补充精确Git字节关系及独立全地址向量核验，冻结最终只读审查回执。"""
from pathlib import Path
import sys, os, json, hashlib, collections, time
from datetime import datetime, timezone, timedelta
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'verification'))
import test_s2b_conv_tile_origin_rtl as previous
import test_s2b_backend_coordinates_rtl as support
def sha(path):
    """核验原件真实SHA。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):
    """读取UTF8 JSON。"""
    return json.loads(path.read_text(encoding='utf-8'))
def save(name,data):
    """只写入全新本次文件。"""
    with (HERE/name).open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(data,stream,ensure_ascii=False,indent=2);stream.write('\n')
started=time.monotonic();base='0700c33e6faba8861cc2e7646a8981e424a69c45'
receipt=read(HERE/'attempt_r02/final_review_receipt.json')
assert receipt['status']=='PASS_G2_FUNCTIONAL_ONLY' and receipt['source_sha256_pre']==receipt['source_sha256_post']
assert previous.git('rev-parse','HEAD').decode().strip()==base
profile=read(ROOT/'board/s2b_inference_platform.json');relations=[]
for path in profile['rtl_sources']:
    if path=='src/s2b_conv_tile_engine.sv':continue
    blob=previous.git('show',base+':'+path);raw=(ROOT/path).read_bytes()
    if blob==raw:relation='RAW_IDENTICAL'
    else:
        assert b'\r\n' not in blob and blob.replace(b'\n',b'\r\n')==raw,path
        relation='EXACT_LF_TO_CRLF'
    relations.append(dict(path=path,relation=relation,git_sha256=hashlib.sha256(blob).hexdigest(),raw_sha256=sha(ROOT/path)))
save('exact_git_raw_relationships.json',relations)
formal=ROOT/'report/evidence/S2B-T17/s15_arithmetic_fix_20261012_r01';u32=(1<<32)-1;u64=(1<<64)-1
counts=collections.Counter();n=0
vector=formal/'feature_r01/feature/address_vectors.txt'
for line in vector.read_text(encoding='utf-8').splitlines():
    fields=[int(token,16) for token in line.split()];assert len(fields)==31
    c,h,w,ty,sy,fy,py,tx,sx,fx,px,baseaddr,ph,pw,index,count,state,valid,error=fields[:19]
    plane=ph*pw;y=(ty*sy+fy-py)&u64;x=(tx*sx+fx-px)&u64
    if y&(1<<63):y-=1<<64
    if x&(1<<63):x-=1<<64
    if plane==0 or pw==0:y=x=0
    bounds=int(plane!=0 and pw!=0 and 0<=y<h and 0<=x<w)
    offset=((c*h+y)*w+x)&u64 if bounds else 0
    address=(baseaddr+offset)&u64 if bounds else 0
    bad=int(address>u32);action=0 if index>=count else 1 if not bounds else 2 if bad else 3
    mapped=error if error in (0,1,2,6) else 6
    advance=int((state==1 and index<count and not bounds) or (state==2 and valid==1 and mapped==0))
    gold=[plane,y&u64,x&u64,bounds,offset,address,bad,action,advance,address&0xfffffffc,1<<(address&3),(y*w)&u64 if bounds else 0]
    assert gold==fields[19:],n
    counts[action]+=1;n+=1
assert n==120361 and dict(counts)=={0:29981,1:48100,2:40124,3:2156}
feature=dict(vectors=n,branch_counts=dict(counts),sha256=sha(vector),basis='独立Python整数旧嵌套NCHW、signed64坐标、原节点mod64及END/padding/RANGE/request顺序；不调用Developer oracle。')
counts=collections.Counter();n=0;vector=formal/'output_r01/output/address_vectors.txt'
for line in vector.read_text(encoding='utf-8').splitlines():
    fields=[int(token,16) for token in line.split()];assert len(fields)==21
    group,lane,h,w,ty,py,tx,px,baseaddr,oc,lanes,point,points=fields[:13]
    c=(group+lane)&u32;y=(ty+py)&u32;x=(tx+px)&u32
    offset=((c*h+y)*w+x)&u64;address=(baseaddr+offset)&u64;elements=((oc*h)&u32)*w
    bad=int(address>u32 or offset>=elements);action=0 if lane>=lanes else 1 if point>=points else 2 if bad else 3
    assert [c,y,x,offset,address,bad,action,elements]==fields[13:],n
    counts[action]+=1;n+=1
assert n==120361
save('independent_complete_vector_audit.json',dict(feature=feature,output=dict(vectors=n,branch_counts=dict(counts),sha256=sha(vector)),scope='独立核验完整G1刺激黄金；不替代已经审计真实RTL compile/simulation原件。'))
tool=Path('D:/FPGA_S2A_MSYS2_20261001/env');checker=support.load_checker()
env=dict(os.environ,PATH=str(tool/'usr/bin')+os.pathsep+str(tool/'mingw64/bin')+os.pathsep+os.environ.get('PATH',''))
toolrecord=dict(runs=[])
for name,path in (('gpp',tool/'mingw64/bin/g++.exe'),('make',tool/'usr/bin/make.exe')):
    previous.execute(name+'_version',[str(checker.exact_file(path)),'--version'],HERE,HERE,env,toolrecord,30)
reviewed=[]
for path in ('src/s2b_conv_tile_engine.sv','board/s2b_inference_platform.json','verification/check_s2b_inference_platform.py','verification/test_s2b_conv_feature_address_rtl.py','verification/test_s2b_s15_arithmetic_rtl.py'):
    assert sha(ROOT/path)==receipt['source_sha256_post'][path]
    reviewed.append(dict(path=path,sha256=sha(ROOT/path)))
for path,digest in receipt['source_sha256_post'].items():assert sha(ROOT/path)==digest
assert previous.git('rev-parse','HEAD').decode().strip()==base
final=dict(schema_version=1,status='PASS_G2_FUNCTIONAL_ONLY',stop=True,source_commit=base,reviewed5source=reviewed,
 review_receipt=dict(path=(HERE/'attempt_r02/final_review_receipt.json').relative_to(ROOT).as_posix(),sha256=sha(HERE/'attempt_r02/final_review_receipt.json')),
 native_driver=dict(path=(HERE/'review_driver_r02.native.json').relative_to(ROOT).as_posix(),sha256=sha(HERE/'review_driver_r02.native.json')),
 independent_vectors=dict(feature=feature,output_vectors=n),exact_git_relationships=relations,tool_version_runs=toolrecord['runs'],
 findings=[],failure_r01=dict(path=(HERE/'final_review_receipt.json').relative_to(ROOT).as_posix(),sha256=sha(HERE/'final_review_receipt.json'),reason='审查driver直接比较Git LF与冻结CRLF导致假漂移；原件、原driver源码及native1保留，explicit字节关系补充关闭。'),
 reviewed_logic=dict(width='完整unsigned64 H*W；32bit因子最大乘积仍小于2^64',start='同一个既有接受START沿消费raw H/W；随后latched一致',priority='hard_reset > abort > state/accepted_START；其他拍保持',consumer='仅替换feature空间平面；原bounds/default0、signed64原点、channel乘法与加法mod64、END/padding/BAD_RANGE及请求握手保持'),
 limitations=receipt['limitations'],elapsed_seconds=round(time.monotonic()-started,3),created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat())
save('final_stop_receipt.json',final)
print(json.dumps(dict(status=final['status'],stop=True,reviewed5source=reviewed,sha256=sha(HERE/'final_stop_receipt.json')),ensure_ascii=True),flush=True)
