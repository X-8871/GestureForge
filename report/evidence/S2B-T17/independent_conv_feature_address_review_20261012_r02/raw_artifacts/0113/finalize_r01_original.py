"""只读闭合诊断实例映射；同一程序补充合法消费样例并封存。"""
from pathlib import Path
import json,sys,subprocess,hashlib,time,random,re,os,psutil
from collections import Counter
ROOT=Path.cwd();WORK=Path(__file__).resolve().parent;BASE=ROOT/'report/evidence/S2B-T17/conv_feature_address_20261011_r01';U32=2**32-1;SEED=0x191012B8
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def oracle(v):
    """旧嵌套式及原signed64坐标，独立于候选checker的重排表达式。"""
    c,h,w,ty,sy,fy,py,tx,sx,fx,px,base,ph,pw,index,count,state,rsp,error=v
    def signed(n):return n%2**64-2**64 if n%2**64>=2**63 else n%2**64
    plane=ph*pw;y=signed(ty*sy+fy-py) if plane else 0;x=signed(tx*sx+fx-px) if plane else 0
    valid=int(plane!=0 and 0<=y<h and 0<=x<w);offset=((c*h+y)*w+x)%2**64 if valid else 0;address=(base+offset)%2**64 if valid else 0
    bad=int(address>U32);action=0 if index>=count else 1 if not valid else 2 if bad else 3
    advance=int(state==1 and index<count and not valid or state==2 and rsp and error==0)
    return plane,y%2**64,x%2**64,valid,offset,address,bad,action,advance,address&0xfffffffc,1<<(address%4),y*w if valid else 0
began=time.monotonic();r=load(WORK/'validation.json');assert r['status']=='FAIL' and 'line 166' in r['traceback'] and 'AssertionError' in r['traceback']
assert len(r['runs'])==4 and [x['native_exit_code'] for x in r['runs']]==[0,2,0,0]
compile_text=(WORK/'compile.log').read_text(encoding='utf-8');headers=re.findall(r'^%Warning-(?:MULTIDRIVEN|LATCH|UNOPTFLAT):.*',compile_text,re.M);assert len(headers)==34 and all('MULTIDRIVEN' in h for h in headers)
blocks=re.findall(r'%Warning-MULTIDRIVEN:.*?(?=%Warning-|g\+\+|make|$)',compile_text,re.S);assert len(blocks)==34
tb=(WORK/'tb_feature.sv').read_text(encoding='utf-8');symbols=set(re.findall(r'(?:u_old|u_dut)\.(\w+)\s*=',tb));assert len(symbols)==17
diagnostics=[];seen=Counter()
for block in blocks:
    header=block.splitlines()[0];signal=re.search(r": '([^']+)'",header).group(1);assert signal in symbols
    file,line=re.search(r'(tb_feature\.sv):(\d+):\d+: \.\.\. Location of other write',block).groups();line=int(line);assignment=tb.splitlines()[line-1]
    assert re.search(r'(?:u_old|u_dut)\.'+signal+r'\s*=',assignment)
    source=re.search(r'MULTIDRIVEN: ([^:]+):',header).group(1);assert source in ['source\\s9_conv_tile_engine_original.sv','source\\s2b_conv_tile_engine.sv']
    seen[(source,signal)]+=1;diagnostics.append({'header':header,'tb_line':line,'assignment':assignment,'raw':block})
assert len(seen)==34 and all(v==1 for v in seen.values())
assert '$finish' not in tb and '$finish' not in (WORK/'tb_boundary.sv').read_text(encoding='utf-8')
top=(WORK/'tb_combined.sv').read_text(encoding='utf-8');assert 'wait(feature_done && boundary_done)' in top and top.count('$finish')==1
first=(WORK/'simulation.log').read_text(encoding='utf-8');assert 'vectors=24011 end=4033 padding=11974 range=8002 request=2' in first and 'CONV_VALIDATION vectors=5996 cycles=100697 abort_mask=000fffff reset_mask=000fffff response_cases=24 raw80=1' in first and 'PASS BOTH_DONE' in first
# 复用已冻结的24011独立向量，新增合法请求域5001例，保持原种子与新增种子分别记录。
rows=[]
for line in (WORK/'feature_vectors.txt').read_text(encoding='utf-8').splitlines():
    allvalues=[int(n,16) for n in line.split()];v=allvalues[:19];gold=oracle(v);assert tuple(allvalues[19:])==gold;rows.append((v,gold))
normal=[2,3,5,0,0,2,0,0,0,4,0,100,1,1,0,1,1,0,0];assert oracle(normal)[4:6]==(44,144);rows.append((normal,oracle(normal)))
rng=random.Random(SEED)
for i in range(5000):
    h=rng.randrange(1,417);w=rng.randrange(1,417);c=rng.randrange(512);y=rng.randrange(h);x=rng.randrange(w)
    offset=(c*h+y)*w+x;address=U32-rng.randrange(8) if i%2 else rng.randrange(0x10000000,0x12000000)
    v=[c,h,w,0,0,y,0,0,0,x,0,address-offset,1,1,0,1,1,0,0];gold=oracle(v);assert gold[7]==3;rows.append((v,gold))
vector=WORK/'feature_vectors_consumed.txt';vector.write_text('\n'.join(' '.join(f'{n:x}' for n in (*v,*gold)) for v,gold in rows)+'\n',encoding='utf-8')
cmd=[str(WORK/'build/Vtb_combined.exe'),'+VECTOR_PATH='+str(vector).replace('\\','/')];start=time.monotonic();peak=0
with (WORK/'simulation_consumed.log').open('x',encoding='utf-8') as log:
    proc=subprocess.Popen(cmd,cwd=WORK,stdout=log,stderr=subprocess.STDOUT)
    while proc.poll() is None:
        try:
            p=psutil.Process(proc.pid);peak=max(peak,sum(c.memory_info().rss for c in [p]+p.children(recursive=True) if c.is_running()))
        except psutil.Error:pass
        assert peak<=1073741824 and time.monotonic()-start<30
        time.sleep(.05)
assert proc.returncode==0
sim={'name':'same_compile_consumed_simulation','command':subprocess.list2cmdline(cmd),'native_exit_code':proc.returncode,'seconds':round(time.monotonic()-start,3),'peak_child_tree_rss_bytes':peak,'log_sha256':sha(WORK/'simulation_consumed.log')}
counts=Counter(str(g[7]) for v,g in rows);actual=(WORK/'simulation_consumed.log').read_text(encoding='utf-8')
assert f'vectors={len(rows)} end={counts["0"]} padding={counts["1"]} range={counts["2"]} request={counts["3"]}' in actual and 'CONV_VALIDATION vectors=5996 cycles=100697 abort_mask=000fffff reset_mask=000fffff response_cases=24 raw80=1' in actual and 'PASS BOTH_DONE feature=1 boundary=1' in actual
freeze=load(BASE/'source_freeze.json');profile=load(ROOT/'board/s2b_inference_platform.json');assert len(freeze['source_files'])==43
assert profile['physical_interface']=='s2b-physical-candidate/0.1.1' and profile['clock_hz']==50000000 and profile['visibility_default']==0
for row in freeze['source_files']:assert sha(ROOT/row['path'])==row['sha256']
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()=='3f24c94564d10103aaa00db07356f666b085f687'
new=(ROOT/'src/s2b_conv_tile_engine.sv').read_text(encoding='utf-8');old=subprocess.check_output(['git','show','3f24c94564d10103aaa00db07356f666b085f687:src/s2b_conv_tile_engine.sv']).decode('utf-8').replace('\r\n','\n');ff='    always_ff @(posedge clk) begin';assert old[old.index(ff):]==new[new.index(ff):] and old.split(');',1)[0]==new.split(');',1)[0]
for p in (WORK/'source').iterdir():
    if p.name=='s9_conv_tile_engine_original.sv':assert p.read_text(encoding='utf-8')==old.replace('module s2b_conv_tile_engine (','module s2b_conv_tile_engine_original (')
    else:assert p.read_bytes()==(ROOT/'src'/p.name).read_bytes()
generated=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in (WORK/'build').iterdir() if p.suffix in ['.cpp','.h','.mk']]
assert any(p['path'].endswith('__main.cpp') for p in generated) and not list((WORK/'build').glob('*.gch'))
audit={'status':'PASS','diagnostics':diagnostics,'symbol_instances':34,'generated_cpp_header_make_inputs':generated,'reused_build_sha_scope':'同一个Vtb_combined.exe，不列可重建EXE；原compile命令与新simulation命令绑定。','simulation':sim,'new_seed':SEED,'new_seed_hex':hex(SEED),'consumed_vectors_added':5001,'total_vectors':len(rows),'branch_counts':dict(counts),'elapsed_seconds':round(time.monotonic()-began,3)}
(WORK/'closure_validation.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review_command=subprocess.list2cmdline([sys.executable,'-X','utf8','-B',str(WORK/'review.py')]);final_command=subprocess.list2cmdline([sys.executable,'-X','utf8','-B',str(WORK/'finalize.py')])
receipt={'schema_version':1,'task_id':'S2B-T17-S10-G2','decision':'PASS','reviewer_stop':True,'source_commit':'3f24c94564d10103aaa00db07356f666b085f687','source_freeze_sha256':sha(BASE/'source_freeze.json'),'reviewed_manifest_sha256':sha(BASE/'delivery_manifest.json'),'source_diff_sha256':sha(BASE/'source_diff.patch'),'profile':'s2b-inference-platform/0.1.10','modified_source_sha256':freeze['modified_files'],'source_sha256':{row['path']:row['sha256'] for row in freeze['source_files']},'ff_sha256':r['ff_sha256'],'findings':[],
 'math_proof':'保留signed64坐标/bounds：0≤Y<H≤UINT32蕴含Y高32为0，Y×W为精确64；无符号64环中((C×H+Y)×W+X)等于C×(H×W)+Y×W+X。channel及base仍原模64。END→PADDING→RANGE→READ及新零默认只影响未消费内部中间量，FF/FSM/端口/请求周期/owner/错误优先不变，S9output组合逐字不变。',
 'independent_math':r['independent_math'],'consumed_domain_supplement':{k:audit[k] for k in ['new_seed','new_seed_hex','consumed_vectors_added','total_vectors','branch_counts']},'public_start':{'vectors':5996,'cycles':100697,'abort_mask':'000fffff','reset_mask':'000fffff','response_cases':24,'raw80':1,'both_done_marker':True},'feature_mutants':r['feature_mutants'],'output_mutants':r['output_mutants'],'platform_negatives':r['platform_negatives'],'g1_readonly_counts':r['g1_counts_reviewed'],'g1_adapters':r['g1_adapters'],'g1_compiled_closure':r['g1_compile_closure'],
 'commands':[{'name':'initial_review_diagnostic_name_failure','command':review_command,'native_exit_code':1,'seconds':None,'script_sha256':sha(WORK/'review.py'),'reason':'唯一compile及双回归simulation已native0；后置审查断言仍按原模块名，合并top实例名改变导致自测失败，validation traceback保留。'},{'name':'diagnostic_map_and_finalize','command':final_command,'native_exit_code':0,'seconds':audit['elapsed_seconds'],'script_sha256':sha(WORK/'finalize.py')}]+r['runs']+[sim],
 'diagnostic_scope':{'feature':34,'output':26,'backend':16,'public_three_classes':0,'combined':'每条其他写入位置均tb_feature.sv对应精确17寄存器×旧新；实例名为合并top实际路径，原clk恒0/FF未执行。代表实例名不作为生产豁免；公开单独G1三个compile无三类警告。','production_zero_warning_claim':False},
 'resource':{'compile_count':1,'jobs':1,'threads':1,'max_sampled_child_tree_rss_bytes':max(x['peak_child_tree_rss_bytes'] for x in r['runs']+[sim]),'cache_sample_peak_bytes':max(x['cache_sample_peak_bytes'] for x in r['runs']),'rss_limit_bytes':1073741824,'cache_limit_bytes':314572800,'sampling_seconds':0.1,'scope':'初始driver子树采样峰，不含Python审查宿主；补充simulation采样0.05秒。PCH仅通过隔离no_pch.mk关闭，原C++入口/文件/Makefile逐项绑定。'},
 'limitations':['PASS只覆盖S10候选功能G2，不批准时序闭合/实现/postroute/bit/runtime/BOARD109/1000/G3–G5。','G1完整layer0+独立CPU、逐请求数值/握手，backend15非CONV完整trace/38层CONV控制stub/12公共反例、geometry及output120361原件只读审阅，未重复长回归或21层CONV全数值/109整网。','独立受控feature域不冒充公开START可达覆盖；公共5996例由双TB真实完成，20态abort/reset和24响应单独标记。','包装evidence原生0/inputs原生2仅包装；物理0.1.1候选未冻结及未执行项仍阻断。','S9真实WNS−4.527/TNS−1840.705仍FAIL；新STA/G3及109板测NOT_RUN。','未操作板卡/串口/JTAG/ROSS/Vivado，未改生产/正式证据/STATE/Git，子代理不提交。']}
(WORK/'final_review_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# 旧manifest负责旧大证据树；本清单只绑定实际直接审阅材料与自有新输出。
inputs=set(ROOT/row['path'] for row in freeze['source_files'])
for p in load(WORK/'direct_inputs.json'):
    q=ROOT/p
    if q.suffix in ['.json','.log','.patch','.py'] and 'source_snapshot' not in p and 'final_source_snapshot' not in p:inputs.add(q)
items={q:{'path':q.relative_to(ROOT).as_posix(),'sha256':sha(q),'role':'input'} for q in inputs}
for q in WORK.rglob('*'):
    if not q.is_file() or q.name=='raw_manifest.jsonl' or any(p in ['checker_fixture','feature_mutants','offset_mutants'] for p in q.relative_to(WORK).parts):continue
    if 'build' in q.relative_to(WORK).parts and q.suffix not in ['.cpp','.h','.mk']:continue
    assert q.suffix.lower() not in ['.exe','.o','.gch','.dcp','.bit']
    role='log' if q.suffix=='.log' else 'source' if q.suffix in ['.py','.sv','.cpp','.h','.mk'] else 'input' if 'vectors' in q.name else 'result'
    items[q]={'path':q.relative_to(ROOT).as_posix(),'sha256':sha(q),'role':role}
values=sorted(items.values(),key=lambda x:x['path']);assert all(set(v)=={'path','sha256','role'} and v['role'] in ['source','input','result','log','diagnostic','artifact'] for v in values)
(WORK/'raw_manifest.jsonl').write_text(''.join(json.dumps(v,ensure_ascii=False)+'\n' for v in values),encoding='utf-8')
print(json.dumps({'decision':'PASS','reviewer_stop':True,'receipt_sha256':sha(WORK/'final_review_receipt.json'),'raw_manifest_sha256':sha(WORK/'raw_manifest.jsonl'),'bindings':len(values),'initial_runs':r['runs'],'supplement':sim,'counts':dict(counts),'seconds':audit['elapsed_seconds']},ensure_ascii=False))
