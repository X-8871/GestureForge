"""独立只读核查固定表、真实证据与时序块契约。"""
import hashlib,json,re,subprocess,time,random,sys
from pathlib import Path
import ctypes
ROOT=Path.cwd(); OUT=ROOT/'tmp/2B/S2B-T17/independent_s12_functional_review_20261012_r01'
MAIN=ROOT/'report/evidence/S2B-T17/s12_timing_cones_20261012_r01'
start=time.monotonic(); records=[]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def check(condition,label,detail=None):
 assert condition,label
 records.append(dict(check=label,result='PASS',detail=detail))
def gitblob(path):return subprocess.check_output(['git','-c','core.longpaths=true','-c','maintenance.auto=false','show','891f750045ce141a8152c96025da559ff1d3a321:'+path]).decode('utf-8').replace('\r\n','\n')
freeze=load(MAIN/'source_freeze.json'); summary=load(MAIN/'g1_summary.json')
for name,expected in [('source_freeze.json','eadf373c59420aa234a5e6394c9ca08066b480bdde6263f91600cf21bbbe02c7'),('source_diff.patch','6be9a040c20520403532aec5a2626292f93b8b91845b21d883b69dae2ceb0a5d'),('g1_summary.json','0674603c86f92762d172085323fdd0328d7a364735a87b45e389f0ede9d19549')]:check(sha(MAIN/name)==expected,'冻结索引 '+name)
for s in freeze['source_files']:
 check(sha(ROOT/s['path'])==s['sha256'] and sha(ROOT/s['snapshot'])==s['sha256'] and (ROOT/s['snapshot']).stat().st_size==s['bytes'],'43源及快照 '+s['path'])
check(len(freeze['source_files'])==43 and len(freeze['modified_files'])==16 and len(freeze['active_rtl_sources'])==18 and len(freeze['frozen14'])==14,'闭包数量')
for p,h in freeze['frozen14'].items():check(sha(ROOT/p)==h,'原14 RAW '+p)
conv=(ROOT/'src/s2b_conv_tile_engine.sv').read_text(encoding='utf-8'); old=gitblob('src/s2b_conv_tile_engine.sv')
ff='    always_ff @(posedge clk) begin'; a=old[old.index(ff):]; b=conv[conv.index(ff):]
# 逐赋值规范为三个获准RHS占位，其他字节必须相等。
def norm(text):
 for name in ('patch_height','patch_width','patch_byte_count'):
  pattern=r'(?m)^                    '+name+r' <=[\s\S]*?;'
  hits=list(re.finditer(pattern,text));check(len(hits)==1,'获准RHS唯一 '+name)
  text=re.sub(pattern,'                    '+name+' <= REVIEW_ALLOWED;',text)
 return text
check(norm(a)==norm(b),'CONV其他FF逐字节等同Git基线')
for p in ('src/s2b_maxpool_engine.sv','src/s2b_route_engine.sv','src/s2b_network_backend.sv'):
 current=(ROOT/p).read_text(encoding='utf-8'); ref=gitblob(p)
 check(current[current.index('    always_ff'):]==ref[ref.index('    always_ff'):],'其他FF不变 '+p)
m=load(ROOT/'report/evidence/S2A-T01/tiny416_model_manifest.json'); layers=m['layers']
pattern=r"480'h([0-9A-Fa-f]{120}): frozen_conv_descriptor_lookup = \{1'b1, 26'd(\d+), 26'd(\d+), 45'd(\d+)\};"
entries={tuple(int(h[i:i+8],16) for i in range(0,120,8)):tuple(map(int,(p,r,w))) for h,p,r,w in re.findall(pattern,conv)}
frozen={}
for row in layers:
 if row['op']!='convolutional':continue
 _,c,ih,iw=row['input_shape_nchw'];_,oc,oh,ow=row['output_shape_nchw'];kh,kw=row['kernel_hw'];sy,sx=row['stride_hw'];pads=row['padding_lrtb'];idx=row['layer_index']
 key=(idx,c,ih,iw,oc,oh,ow,kh,kw,sy,sx,*pads);frozen[idx]=key
 check(entries.get(key)==(c*kh,c*kh*kw,oc*c*kh*kw),'独立模型480bit '+str(idx))
check(len(entries)==len(frozen)==21,'CONV全部21键无冗余')
tile={int(k,16):tuple(map(int,(h,w,b))) for k,h,w,b in re.findall(r"40'h([0-9A-Fa-f]{10}): frozen_conv_tile_lookup = \{32'd(\d+), 32'd(\d+), 32'd(\d+)\};",conv)}
U32=(1<<32)-1
for idx,key in frozen.items():
 for y in range(9):
  for x in range(9):
   h=((y-1)*key[9]+key[7])&U32;w=((x-1)*key[10]+key[8])&U32;b=(h*w*key[1])&U32
   assert tile[(idx<<8)|(y<<4)|x]==(h,w,b),(idx,y,x)
check(len(tile)==1701,'独立重算21乘81全部extent表',len(tile))
full={int(k):tuple(map(int,(h,w,p,b))) for k,h,w,p,b in re.findall(r"32'd(\d+): frozen_full_tile_lookup = \{19'd(\d+), 19'd(\d+), 32'd(\d+), 29'd(\d+)\};",conv)}
for idx,key in frozen.items():
 h=(min(8,key[5])-1)*key[9]+key[7];w=(min(8,key[6])-1)*key[10]+key[8]
 assert full[idx]==(h,w,h*w,h*w*key[1]),idx
check(len(full)==21,'独立全tile固定容量表')
aliases=0
for key in entries:
 for i in range(15):
  alias=list(key);alias[i]^=0x10000;assert tuple(alias) not in entries;aliases+=1
check(aliases==315,'完整高16别名拒绝',aliases)
rng=random.Random(0x1210A7); generic=0
for extent in range(9):
 for _ in range(10000):
  stride=rng.getrandbits(32);kernel=rng.getrandbits(32)
  coefficient=extent-1
  # 独立展开移位加法与旧U32乘法，含extent0。
  got=(kernel-stride)&U32 if extent==0 else (kernel+sum(stride<<bit for bit in range(3) if coefficient&(1<<bit)))&U32
  assert got==((extent-1)*stride+kernel)&U32;generic+=1
check(generic==90000,'通用axis模32独立随机',dict(seed=0x1210A7,vectors=generic))
route=(ROOT/'src/s2b_route_query.sv').read_text(encoding='utf-8')
shapes={tuple(int(h[i:i+8],16) for i in range(0,24,8)):tuple(map(int,(p,b))) for h,p,b in re.findall(r"96'h([0-9A-Fa-f]{24}): frozen_shape_lookup = \{1'b1, 64'd(\d+), 64'd(\d+)\};",route)}
reached=set(); route_layers=[]
for row in layers:
 if row['op']!='route':continue
 route_layers.append(row['layer_index'])
 for idx in row['input_tensor_indices']:
  shape=tuple(layers[idx]['output_shape_nchw'][1:]);reached.add(shape)
  c,h,w=shape;assert shapes[shape]==(c*h,c*h*w)
check(len(route_layers)==11 and reached==set(shapes) and len(shapes)==7,'11可达ROUTE七完整CHW',dict(layers=route_layers,shapes=sorted(shapes)))
check('if (source_count == 32\'d2) begin\n            if (FROZEN_ROUTE_SHAPES)' in route,'count1不消费source1固定命中')
# 整个输出偏移的等式在合法固定维度及任意U32坐标下成立；64位上界无溢出。
for idx,ch,h,w in [(9,128,52,52),(17,256,26,26),(25,512,13,13)]:
 bound=U32*h*w+U32*w+U32;assert bound<(1<<64)
 for _ in range(10000):
  c,y,x=(rng.getrandbits(32) for _ in range(3));assert ((c*h+y)*w+x)==c*(h*w)+y*w+x
check(True,'POOL固定输出64bit恒等式及最大界')
results=[]
for r in summary['runs']:
 check(sha(ROOT/r['validation_path'])==r['validation_sha256'],'真实validation '+r['stage'])
 check(sha(ROOT/r['native_path'])==r['native_sha256'],'真实native '+r['stage'])
 val=load(ROOT/r['validation_path']);native=load(ROOT/r['native_path'])
 check(val['status']==r['status'] and r['native_returncode']==0,'实际状态 '+r['stage'])
 for execution in r['runs']:
  check(execution['exit_code']==0 and sha(ROOT/execution['log'])==execution['log_sha256'],'原始运行log '+r['stage']+'/'+execution['name'])
  log=(ROOT/execution['log']).read_text(encoding='utf-8')
  check(not re.search(r'%Warning-(LATCH|UNOPTFLAT):',log),'无新LATCH UNOPTFLAT '+r['stage']+'/'+execution['name'])
 results.append(dict(stage=r['stage'],native_returncode=r['native_returncode'],status=val['status'],elapsed_seconds=r['elapsed_seconds'],coverage=r['actual_fields'],native_keys=list(native)))
class MemoryCounters(ctypes.Structure):
 _fields_=[('cb',ctypes.c_ulong),('faults',ctypes.c_ulong)]+[(name,ctypes.c_size_t) for name in ('peak_working','working','peak_paged','paged','peak_nonpaged','nonpaged','pagefile','peak_pagefile')]
mem=MemoryCounters();mem.cb=ctypes.sizeof(mem)
ctypes.windll.kernel32.GetCurrentProcess.restype=ctypes.c_void_p
ctypes.windll.psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong]
check(bool(ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(),ctypes.byref(mem),mem.cb)),'Windows实际进程内存读取')
peak=mem.peak_working
check(peak<=134217728,'Reviewer轻量128MiB预算',peak)
receipt=dict(status='PASS_MATH_SOURCE_RAW_REVIEW_PARTIAL_PENDING_PACKAGING',source_baseline=freeze['source_commit'],source_state='UNCOMMITTED_CANDIDATE_RAW',records=records,runs=results,seed=0x1210A7,seconds=time.monotonic()-start,sampled_peak_self_bytes=peak,python=sys.version,argv=sys.argv,limitations=['仅轻量独立重算和只读核查，未重跑大型RTL/CPU卷积。','新包装未冻结，最终G2待独立包装核查。','二态范围，未形式穷举U32组合或XZ。'])
(OUT/'math_raw_receipt_r03.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=receipt['status'],checks=len(records),seconds=receipt['seconds'],peak_bytes=peak),ensure_ascii=False))
