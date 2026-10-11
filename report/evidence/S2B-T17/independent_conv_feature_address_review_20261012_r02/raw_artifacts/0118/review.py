"""S10独立整数黄金、证据闭包及一次编译的双回归。"""
from pathlib import Path
import sys,os,json,hashlib,subprocess,time,random,re,shutil,traceback
from collections import Counter
import psutil
ROOT=Path.cwd();WORK=Path(__file__).resolve().parent;BASE=ROOT/'report/evidence/S2B-T17/conv_feature_address_20261011_r01'
BASELINE='3f24c94564d10103aaa00db07356f666b085f687';U32=2**32-1;U64=2**64-1;SEED=0x191012B7
sys.path.insert(0,str(ROOT/'verification'))
import test_s2b_conv_feature_address_rtl as feature
import test_s2b_conv_output_address_rtl as output
import test_s2b_conv_validation_rtl as conv
import test_s2b_geometry_specialization_rtl as geo
REPORT={'status':'RUNNING','runs':[]};INPUTS=set()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def raw(p):
    """原件哈希不做换行转换。"""
    p=ROOT/p if isinstance(p,str) else p;assert p.is_file(),p;INPUTS.add(p);return p.read_bytes()
def load(p):return json.loads(raw(p).decode('utf-8-sig'))
def text(p):return raw(p).decode('utf-8').replace('\r\n','\n')
def save(name,value):(WORK/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(name,cmd,cwd=WORK,env=None,expected=0):
    """采样真实子进程树，超预算只终止本次子树并保留原件。"""
    begun=time.monotonic();peak=0;disk=0;reason=None
    with (WORK/(name+'.log')).open('x',encoding='utf-8') as log:
        proc=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT)
        while proc.poll() is None:
            try:
                parent=psutil.Process(proc.pid);members=[parent]+parent.children(recursive=True);peak=max(peak,sum(p.memory_info().rss for p in members if p.is_running()))
            except psutil.Error:pass
            cache=WORK/'build';disk=max(disk,sum(p.stat().st_size for p in cache.rglob('*') if p.is_file()) if cache.exists() else 0)
            if peak>1073741824 or disk>314572800 or time.monotonic()-begun>240:
                reason='RSS_LIMIT' if peak>1073741824 else 'CACHE_LIMIT' if disk>314572800 else 'TIMEOUT'
                subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],stdout=log,stderr=subprocess.STDOUT);proc.wait();break
            time.sleep(.1)
    row={'name':name,'command':subprocess.list2cmdline(cmd),'native_exit_code':proc.returncode,'expected_exit_code':expected,'seconds':round(time.monotonic()-begun,3),'peak_child_tree_rss_bytes':peak,'cache_sample_peak_bytes':disk,'stop_reason':reason,'log_sha256':sha(WORK/(name+'.log'))}
    REPORT['runs'].append(row);assert reason is None and proc.returncode==expected,row
def oracle(v):
    """独立逐节点展开旧整数定义，signed解释及原模域明确保留。"""
    c,h,w,ty,sy,fy,py,tx,sx,fx,px,base,ph,pw,index,count,state,rsp,error=v
    plane=ph*pw
    def coordinate(start,stride,scan,pad):
        bits=(start*stride+scan-pad)%2**64
        return bits-2**64 if bits>=2**63 else bits
    y=coordinate(ty,sy,fy,py) if plane else 0;x=coordinate(tx,sx,fx,px) if plane else 0
    bounds=int(plane!=0 and y>=0 and y<h and x>=0 and x<w)
    offset=((c*h+y)*w+x)%2**64 if bounds else 0;address=(base+offset)%2**64 if bounds else 0
    bad=int(address>U32);action=0 if index>=count else 1 if not bounds else 2 if bad else 3
    advance=int(state==1 and index<count and not bounds or state==2 and rsp and error==0)
    return plane,y%2**64,x%2**64,bounds,offset,address,bad,action,advance,address&0xfffffffc,1<<(address%4),y*w if bounds else 0
def diagnostics(value):return re.findall(r'^%Warning-(?:MULTIDRIVEN|LATCH|UNOPTFLAT):.*',value,re.M)
def main():
    """冻结核验与原件审查后，一次廉价编译并等待两个完成标记。"""
    began=time.monotonic();assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==BASELINE
    expected={'source_freeze.json':'8fcbb7313ced5b8046e4ff74bd274ed4b7d47c3d00a776bc50a4b0d73bb96360','delivery_manifest.json':'d69a4ff778f8df0dfa54dff8e7d11f0a18ad161b0d1779bf7fc61d42e9112431','g1_summary.json':'0012a8118e69d8e66400a8282dfd82d67bd7f99db245e8dde340ad3b82497d30','source_diff.patch':'5d3fd3dc77916abe61001bb9555e92c19744a51abb0b5f192438ec6e90f5a835'}
    for p,d in expected.items():assert hashlib.sha256(raw(BASE/p)).hexdigest()==d,p
    freeze=load(BASE/'source_freeze.json');manifest=load(BASE/'delivery_manifest.json');g1=load(BASE/'g1_summary.json')
    for row in manifest['files']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
    assert len(freeze['source_files'])==43 and len(freeze['modified_files'])==10 and not freeze['tested_source_drift']
    for row in freeze['source_files']:
        p=ROOT/row['path'];assert len(raw(p))==row['bytes'] and sha(p)==row['sha256'] and raw(row['snapshot'])==p.read_bytes()
    for p,d in freeze['frozen14'].items():assert hashlib.sha256(raw(p)).hexdigest()==d
    old=subprocess.check_output(['git','show',BASELINE+':'+feature.ENGINE]);assert hashlib.sha256(old).hexdigest()==feature.OLD_SHA
    oldtext=old.decode('utf-8').replace('\r\n','\n');new=text(feature.ENGINE);ff='    always_ff @(posedge clk) begin'
    assert oldtext[oldtext.index(ff):]==new[new.index(ff):] and oldtext.split(');',1)[0]==new.split(');',1)[0]
    REPORT['ff_sha256']=hashlib.sha256(new[new.index(ff):].encode()).hexdigest()
    assert oldtext[oldtext.index('        output_global_y ='):oldtext.index('        mq_prefetch_index =')]==new[new.index('        output_global_y ='):new.index('        mq_prefetch_index =')]
    checker=feature.support.load_checker();bindings=checker.check_static(ROOT);profile=load('board/s2b_inference_platform.json')
    assert profile['version']=='s2b-inference-platform/0.1.10' and profile['clock_hz']==50000000 and profile['visibility_default']==0 and len(profile['rtl_sources'])==18 and len(profile['source_derivation']['derived_sources'])==8
    REPORT['feature_mutants']=feature.mutants(checker,WORK,bindings);REPORT['output_mutants']=output.mutants(checker,WORK,bindings);REPORT['platform_negatives']=geo.checker_negatives(checker,WORK,bindings)
    run('evidence',[sys.executable,'-X','utf8','-B','verification/check_stage_delivery.py','--mode','evidence','--manifest',str(BASE/'delivery_manifest.json')],ROOT)
    run('inputs',[sys.executable,'-X','utf8','-B','verification/check_stage_delivery.py','--mode','inputs','--manifest',str(BASE/'delivery_manifest.json')],ROOT,expected=2)
    d=load(BASE/'diagnostic_scope.json')
    for scope in d['direct_scopes']:
        log=text(scope['log']['path']);tb=text(scope['tb']['path']);count=34 if scope['stage']=='feature' else 26
        assert sha(ROOT/scope['log']['path'])==scope['log']['sha256'] and sha(ROOT/scope['tb']['path'])==scope['tb']['sha256']
        assert len(diagnostics(log))==count==len(scope['records']) and all('MULTIDRIVEN' in h for h in diagnostics(log))
        assert 'logic clk=0;' in tb and not re.search(r'clk\s*(?:<=|=)\s*1|always\s+#',tb)
        for record in scope['records']:
            assert record['raw_diagnostic'] in log and record['module_instance'] in ['u_old','u_dut']
            assert record['signal'] in (set(feature.INPUTS)|{'state'} if scope['stage']=='feature' else set(output.INPUTS))
            assert record['module_instance']+'.'+record['signal']+'=' in tb
    for row in d['public_compile_checks']:assert not diagnostics(text(row['path'])) and sha(ROOT/row['path'])==row['sha256']
    b=d['backend_inherited'];assert diagnostics(text(b['prior_log']['path']))==diagnostics(text(b['actual_log']['path']))==b['headers'] and len(b['headers'])==16
    oldtb=ROOT/'report/evidence/S2B-T17/conv_output_address_trace_20261011_r01/tb_s2b_backend_coordinates.sv';newtb=ROOT/'report/evidence/S2B-T17/conv_feature_address_trace_20261011_r01/tb_s2b_backend_coordinates.sv'
    assert raw(oldtb)==raw(newtb) and sha(newtb)==b['testbench_sha256']==b['prior_testbench_sha256']
    cache=ROOT/'tmp/2B/S2B-T17/s10_conv_g1_20261011_r01';closure=[];adapters=[]
    for stage in g1['execution']:
        ev=ROOT/'report/evidence/S2B-T17'/stage['run_id'];vr=load(ev/'validation.json');assert vr['source_sha256_pre']==vr['source_sha256_post']
        for p,digest in vr['source_sha256_pre'].items():assert sha(ROOT/p)==digest
        for record in stage['runs']:assert record['exit_code']==0 and record['failure'] is None and hashlib.sha256(raw(record['log'])).hexdigest()==record['log_sha256']
        a=load(BASE/'execution_raw'/(stage['stage']+'_adapter.json'));runtime=BASE/'execution_raw'/(stage['stage']+'_runtime.py');native=load(BASE/'execution_raw'/(stage['stage']+'_native.json'))
        value=raw(a['source']).decode('utf-8');assert sha(ROOT/a['source'])==a['source_sha256']
        for change in a['unique_substitutions']:
            assert value.count(change['before'])==1 and change['after']==change['before'].replace('tmp/2B/S2B-T17','tmp/2B/S2B-T17/s10_conv_g1_20261011_r01');value=value.replace(change['before'],change['after'])
        assert raw(runtime)==value.encode() and sha(runtime)==a['transformed_sha256'] and native['native_exit_code']==0 and native['command']
        adapters.append({'stage':stage['stage'],'runtime_sha256':sha(runtime),'command':native['command'],'native_exit_code':native['native_exit_code']})
        for relative in stage['runs'][0]['command']:
            if not relative.endswith('.sv'):continue
            actual=cache/stage['run_id']/relative;assert actual.is_file();raw(actual)
            if relative.startswith('source/') and (ROOT/'src'/actual.name).is_file():assert raw(actual)==raw(ROOT/'src'/actual.name)
            elif actual.name=='s9_conv_tile_engine_original.sv':assert text(actual)==oldtext.replace('module s2b_conv_tile_engine (','module s2b_conv_tile_engine_original (')
            elif actual.name=='s2_network_backend.sv':assert text(actual)==text(ev/actual.name).replace('module s2b_network_backend (','module s2b_network_backend_original (')
            elif actual.name=='s8_conv_tile_engine_original.sv':assert raw(actual)==raw(ev/actual.name)
            else:assert raw(actual)==raw(ev/actual.name)
            closure.append({'path':actual.relative_to(ROOT).as_posix(),'sha256':sha(actual)})
    REPORT['g1_adapters']=adapters;REPORT['g1_compile_closure']=closure
    markers={'conv_feature_address_20261011_r01':['vectors=120361 end=29981 padding=48100 range=40124 request=2156'],'conv_output_address_20261011_r04':['vectors=120361 advance=42698 next_lane=20793 range=52388 request=4482'],'conv_feature_address_layer0_20261011_r01':['bytes=1384448 mismatches=0','requests=2551955 responses=2551955','cycles=27235743'],'conv_feature_address_trace_20261011_r01':['layers=15 outputs=5234944 requests=12286976 cycles=102468267','PUBLIC_ENTRY trials=12'],'conv_feature_address_geometry_20261011_r01':['pool=19645','upsample=3456','cycles=590601']}
    for runid,needles in markers.items():
        value=text(ROOT/'report/evidence/S2B-T17'/runid/'simulation.log')
        for needle in needles:assert needle in value,(runid,needle)
    cpu=load(ROOT/'report/evidence/S2B-T17/conv_feature_address_layer0_20261011_r01/validation.json')['independent_cpu_layer0'];assert cpu['status']=='PASS' and cpu['mismatches']==0 and cpu['blas_threads_before_after']==[1,1]
    REPORT['g1_counts_reviewed']={k:g1[k] for k in ['feature','output','boundary','layer0','cpu_layer0','backend','geometry']}
    base=[0,1,1,0,0,0,0,0,0,0,0,0,1,1,0,1,1,0,0];manual=[]
    def case(name,**changes):
        v=base.copy();mapping={n:i for i,n in enumerate(feature.INPUTS)}
        for name2,value in changes.items():v[mapping[name2]]=value
        manual.append({'name':name,'input':v,'expected':oracle(v)})
    case('H0',input_height_latched=0);case('W0',input_width_latched=0)
    case('bit63negative',tile_start_y=U32,stride_y_latched=U32,pad_top_latched=1)
    case('bit32alias',tile_start_y=65536,stride_y_latched=65536)
    case('YequalsH',input_height_latched=U32,feature_scan_y=U32)
    case('maxY',input_height_latched=U32,input_width_latched=U32,feature_scan_y=U32-1,feature_scan_x=U32-2)
    case('triplewrap',feature_scan_channel=2**31,input_height_latched=2,input_width_latched=U32,feature_scan_y=1,feature_scan_x=1)
    case('basewrap',feature_scan_channel=2**31,input_height_latched=2,input_width_latched=U32,feature_scan_y=1,input_base_latched=1)
    case('base33carry',input_width_latched=2,feature_scan_x=1,input_base_latched=U32)
    case('patch0',patch_height=0,input_base_latched=U32)
    case('ENDbeatsPAD',feature_scan_index=1,pad_top_latched=1)
    assert manual[2]['expected'][1]==2**64-2**33 and manual[3]['expected'][1]==2**32
    assert manual[6]['expected'][4]==0 and manual[7]['expected'][4]==U64 and manual[7]['expected'][5]==0
    assert manual[8]['expected'][5]==2**32
    rows=[(m['input'],m['expected']) for m in manual];rng=random.Random(SEED)
    for i in range(24000):
        v=[rng.getrandbits(32) for _ in feature.INPUTS]+[rng.randrange(4),rng.randrange(2),rng.randrange(8)]
        if i%3==0:
            c,h,w=[rng.getrandbits(32) for _ in range(3)];v[:3]=[c,h,w];v[3:11]=[0,0,rng.randrange(h) if h else 0,0,0,0,rng.randrange(w) if w else 0,0];v[12:16]=[1,1,0,1]
        elif i%3==1:v[3:7]=[0,0,0,rng.randrange(1,U32)];v[12:16]=[1,1,0,1]
        rows.append((v,oracle(v)))
    REPORT['independent_math']={'seed':SEED,'seed_hex':hex(SEED),'vectors':len(rows),'branches':dict(Counter(str(g[7]) for v,g in rows)),'manual':manual,'oracle':'独立旧嵌套整数定义；坐标每节点模64 signed解释，消费bounds内原offset/base模64。'}
    (WORK/'feature_vectors.txt').write_text('\n'.join(' '.join(f'{n:x}' for n in (*v,*g)) for v,g in rows)+'\n',encoding='utf-8')
    feature_tb=feature.bench();assert feature_tb.count('$finish;')==1
    feature_tb=feature_tb.replace('module tb_s2b_conv_feature_address;','module tb_s2b_conv_feature_address(output logic done=0);').replace('$finish;','done=1;')
    model=load(feature.support.MODEL);names,data,small,math=conv.vectors(model);boundary_tb=conv.boundary_tb(names,small);assert boundary_tb.count('$finish;')==1 and math['vectors']==5996
    boundary_tb=boundary_tb.replace('module tb_s2b_conv_validation;','module tb_s2b_conv_validation(output logic done=0);').replace('$finish;','done=1;')
    (WORK/'tb_feature.sv').write_text(feature_tb,encoding='utf-8');(WORK/'tb_boundary.sv').write_text(boundary_tb,encoding='utf-8');(WORK/'validation_vectors.txt').write_text(data,encoding='utf-8')
    (WORK/'tb_combined.sv').write_text('''// 两个完成标记都成立后才结束，任何子回归失败立即报告。
`timescale 1ns/1ps
module tb_combined;
wire feature_done,boundary_done;
tb_s2b_conv_feature_address feature_test(.done(feature_done));
tb_s2b_conv_validation boundary_test(.done(boundary_done));
initial begin wait(feature_done && boundary_done); $display("PASS BOTH_DONE feature=1 boundary=1"); $finish; end
initial begin #2000000; $fatal(1,"两个回归未完整结束"); end
endmodule
''',encoding='utf-8')
    source=WORK/'source';source.mkdir()
    for p in conv.RTL:shutil.copyfile(ROOT/p,source/Path(p).name)
    (source/'s9_conv_tile_engine_original.sv').write_text(oldtext.replace('module s2b_conv_tile_engine (','module s2b_conv_tile_engine_original ('),encoding='utf-8')
    (WORK/'no_pch.mk').write_text('# 关闭可重建PCH，仅保留同一C++来源和普通编译参数。\n%.o: %.cpp\n\t$(CXX) $(OPT_FAST) $(CXXFLAGS) $(CPPFLAGS) -c -o $@ $<\n',encoding='utf-8')
    heavy=[p.info for p in psutil.process_iter(['pid','name']) if p.info['name'] and re.fullmatch(r'(?:vivado|verilator_bin|cc1plus|Vtb_.*)\.exe',p.info['name'],re.I)]
    REPORT['preflight']={'heavy':heavy,'ram_available':psutil.virtual_memory().available,'disk_free':shutil.disk_usage(WORK).free,'rss_limit_bytes':1073741824,'cache_limit_bytes':314572800};assert not heavy and REPORT['preflight']['ram_available']>2**30
    tool=Path('D:/FPGA_S2A_MSYS2_20261001/env');env=os.environ.copy();env.update(PATH=str(tool/'usr/bin')+os.pathsep+str(tool/'mingw64/bin')+os.pathsep+env['PATH'],VERILATOR_ROOT=str(tool/'mingw64/share/verilator'),PYTHONUTF8='1')
    cmd=[str(tool/'mingw64/bin/verilator_bin.exe'),'--binary','--timing','--timescale','1ns/1ps','-Wall','-Wno-fatal','-j','1','--threads','1','--output-split','10000','--output-split-cfuncs','100','--top-module','tb_combined','--Mdir','build','-MAKEFLAGS','VM_DEFAULT_RULES=0 -f ../no_pch.mk PYTHON3=\'"'+sys.executable+'"\'','-CFLAGS','-D_GLIBCXX_USE_CXX11_ABI=0 -O1','source/s2a_network_descriptor_pkg.sv','source/s2a_conv_tile_engine.sv','source/s9_conv_tile_engine_original.sv','source/s2b_conv_tile_engine.sv','tb_feature.sv','tb_boundary.sv','tb_combined.sv']
    run('compile',cmd,env=env);run('simulation',[str(WORK/'build/Vtb_combined.exe'),'+VECTOR_PATH='+str(WORK/'feature_vectors.txt').replace('\\','/')],env=env)
    result=(WORK/'simulation.log').read_text(encoding='utf-8');assert f'S10_CONV_FEATURE_ADDRESS vectors={len(rows)}' in result and 'CONV_VALIDATION vectors=5996 cycles=100697 abort_mask=000fffff reset_mask=000fffff response_cases=24 raw80=1' in result and 'PASS BOTH_DONE feature=1 boundary=1' in result
    warned=diagnostics((WORK/'compile.log').read_text(encoding='utf-8'));assert len(warned)==34 and all('MULTIDRIVEN' in h for h in warned)
    assert all('tb_s2b_conv_feature_address' in chunk for chunk in re.findall(r'%Warning-MULTIDRIVEN:.*?(?=%Warning-|g\+\+|make|$)',(WORK/'compile.log').read_text(encoding='utf-8'),re.S))
    REPORT['own_diagnostics']={'headers':warned,'scope':'仅受控feature TB：17寄存器×旧新，clk恒0；不对生产或公共TB豁免。'}
    REPORT['generated_compile_inputs']=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in (WORK/'build').iterdir() if p.suffix in ['.cpp','.h','.mk']]
    for row in freeze['source_files']:assert sha(ROOT/row['path'])==row['sha256']
    assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==BASELINE
    REPORT.update(status='PASS_S10_FUNCTIONAL_G2_ONLY',source_commit=BASELINE,source_freeze_sha256=sha(BASE/'source_freeze.json'),reviewed_manifest_sha256=sha(BASE/'delivery_manifest.json'),modified_source_sha256=freeze['modified_files'],source_sha256={r['path']:r['sha256'] for r in freeze['source_files']},elapsed_seconds=round(time.monotonic()-began,3))
try:main()
except Exception:REPORT['status']='FAIL';REPORT['traceback']=traceback.format_exc()
save('validation.json',REPORT);save('direct_inputs.json',sorted(p.relative_to(ROOT).as_posix() for p in INPUTS))
print(json.dumps({'status':REPORT['status'],'seconds':REPORT.get('elapsed_seconds'),'error':REPORT.get('traceback')},ensure_ascii=False));raise SystemExit(0 if REPORT['status'].startswith('PASS') else 1)
