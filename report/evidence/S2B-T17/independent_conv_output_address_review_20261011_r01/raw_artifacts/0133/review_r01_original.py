"""S9独立整数黄金与公共START重建；仅写本审查目录。"""
from pathlib import Path
import sys,json,hashlib,subprocess,os,time,re,random,shutil,traceback
from collections import Counter
import psutil
ROOT=Path.cwd(); WORK=Path(__file__).resolve().parent
BASE=ROOT/'report/evidence/S2B-T17/conv_output_address_20261011_r03'
sys.path.insert(0,str(ROOT/'verification'))
import test_s2b_conv_output_address_rtl as s9
import test_s2b_conv_validation_rtl as conv
import test_s2b_geometry_specialization_rtl as geometry
REPORT={'status':'RUNNING','runs':[]}; INPUTS=set(); SEED=0x191012A5; U32=2**32-1; U64=2**64-1
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def raw(p):
    """绑定真实直接输入。"""
    p=ROOT/p if isinstance(p,str) else p; assert p.is_file(),p; INPUTS.add(p); return p.read_bytes()
def read(p): return json.loads(raw(p).decode('utf-8'))
def text(p): return raw(p).decode('utf-8')
def disk_size(): return sum(p.stat().st_size for p in WORK.rglob('*') if p.is_file())
def run(label,cmd,cwd=WORK,env=None,expected=0,timeout=600):
    """单编译进程树实时RSS、目录预算及超时守卫，日志不覆盖。"""
    started=time.monotonic(); peak=0; disk_peak=disk_size(); failed=None; next_disk=0
    with (WORK/(label+'.log')).open('x',encoding='utf-8') as out:
        proc=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=out,stderr=subprocess.STDOUT)
        while proc.poll() is None:
            try:
                parent=psutil.Process(proc.pid); members=[parent]+parent.children(recursive=True)
                peak=max(peak,sum(p.memory_info().rss for p in members if p.is_running()))
            except psutil.Error: pass
            if time.monotonic()>next_disk: disk_peak=max(disk_peak,disk_size()); next_disk=time.monotonic()+3
            if peak>1610612736 or disk_peak>1073741824 or time.monotonic()-started>timeout:
                failed='RSS_LIMIT' if peak>1610612736 else 'DISK_LIMIT' if disk_peak>1073741824 else 'TIMEOUT'
                subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],stdout=out,stderr=subprocess.STDOUT); proc.wait(); break
            time.sleep(.1)
    row={'name':label,'command':subprocess.list2cmdline(cmd),'native_exit_code':proc.returncode,'expected_exit_code':expected,'seconds':round(time.monotonic()-started,3),'peak_tree_rss_bytes':peak,'observed_review_directory_bytes':max(disk_peak,disk_size()),'failure':failed,'log_sha256':sha(WORK/(label+'.log'))}
    REPORT['runs'].append(row); assert failed is None and proc.returncode==expected,row
def oracle(v):
    """直接展开NCHW数学式，节点明确按原32/64位取模，不用候选因式分解。"""
    group,lane,h,w,ty,py,tx,px,base,oc,lanes,point,points=v
    c=(group+lane)%2**32; y=(ty+py)%2**32; x=(tx+px)%2**32
    original=((c*h+y)*w+x)%2**64; address=(base+original)%2**64
    elements=((oc*h)%2**32)*w; bad=int(address>U32 or original>=elements)
    branch=0 if lane>=lanes else 1 if point>=points else 2 if bad else 3
    return c,y,x,original,address,bad,branch,elements
def main():
    """先只读证据核验，后一次一个真实编译任务。"""
    start=time.monotonic(); assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==s9.BASELINE
    freeze=read(BASE/'source_freeze.json'); manifest=read(BASE/'delivery_manifest_r02.json'); g1=read(BASE/'g1_summary.json')
    for p,d in [('delivery_manifest_r02.json','913314a9f81eda308c75a9f4f59802fd36f11f55886ad0ad4abb24cacc3e7088'),('source_freeze.json','d32a4017d8bb51632c7437c484db25ec34d77b42a93a6404c5c14c620f0377a9'),('g1_summary.json','15a639f09df413b02918c60132713a89143efb3d11fbab9322b06a56a943b217'),('source_diff.patch','5bdcd2e2c28b16c37037ac3097e60b765deeed889f24cb6db5fd4c7857dfed5c')]: assert sha(BASE/p)==d
    for row in manifest['files']: assert hashlib.sha256(raw(row['path'])).hexdigest()==row['sha256'],row['path']
    assert len(freeze['source_files'])==42 and len(freeze['modified_files'])==9 and not freeze['tested_source_drift']
    for row in freeze['source_files']:
        value=raw(row['path']); assert len(value)==row['bytes'] and hashlib.sha256(value).hexdigest()==row['sha256']
        assert raw(row['snapshot'])==value
    for p,d in freeze['frozen14'].items(): assert hashlib.sha256(raw(p)).hexdigest()==d
    tracked=subprocess.check_output(['git','diff','--name-only','--',*freeze['modified_files']],text=True).splitlines()
    assert set(tracked)==set(freeze['modified_files'])-{'verification/test_s2b_conv_output_address_rtl.py'}
    old=subprocess.check_output(['git','show',s9.BASELINE+':'+s9.ENGINE]); assert hashlib.sha256(old).hexdigest()==s9.OLD_SHA
    actual=text(s9.ENGINE); oldtext=old.decode('utf-8').replace('\r\n','\n'); ff='    always_ff @(posedge clk) begin'
    assert actual[actual.index(ff):]==oldtext[oldtext.index(ff):] and actual.split(');',1)[0]==oldtext.split(');',1)[0]
    REPORT['ff_sha256']=hashlib.sha256(actual[actual.index(ff):].encode()).hexdigest()
    checker=s9.support.load_checker(); static=checker.check_static(ROOT); profile=read('board/s2b_inference_platform.json')
    assert profile['version']=='s2b-inference-platform/0.1.9' and profile['clock_hz']==50000000 and profile['visibility_default']==0
    assert len(profile['rtl_sources'])==18 and len(profile['source_derivation']['derived_sources'])==8
    REPORT['mutants']=s9.mutants(checker,WORK,static); REPORT['negative_checks']=geometry.checker_negatives(checker,WORK,static)
    run('evidence',[sys.executable,'-X','utf8','-B','verification/check_stage_delivery.py','--mode','evidence','--manifest',str(BASE/'delivery_manifest_r02.json')],ROOT)
    run('inputs',[sys.executable,'-X','utf8','-B','verification/check_stage_delivery.py','--mode','inputs','--manifest',str(BASE/'delivery_manifest_r02.json')],ROOT,expected=2)
    for stage in g1['execution']:
        report=read(ROOT/'report/evidence/S2B-T17'/stage['run_id']/'validation.json')
        assert report['source_sha256_pre']==report['source_sha256_post']
        for p,d in report['source_sha256_pre'].items(): assert sha(ROOT/p)==d,p
        for record in stage['runs']:
            assert record['exit_code']==0 and record['failure'] is None and hashlib.sha256(raw(record['log'])).hexdigest()==record['log_sha256']
    diagnosis=read(BASE/'diagnostic_scope.json'); log=text(BASE/'compile.log'); bench=text(BASE/'tb_s2b_conv_output_address.sv')
    headers=re.findall(r'^%Warning-(?:MULTIDRIVEN|LATCH|UNOPTFLAT):.*',log,re.M)
    assert len(headers)==26 and all('MULTIDRIVEN' in h for h in headers) and len(diagnosis['records'])==26
    assert 'logic clk=0;' in bench and not re.search(r'clk\s*(?:<=|=)\s*1|always\s+#',bench)
    for row in diagnosis['records']:
        assert row['raw_diagnostic'] in log
        assert row['signal'] in s9.INPUTS and row['module_instance'] in ['u_old','u_dut']
        assert row['module_instance']+'.'+row['signal']+'=v_'+row['signal']+';' in bench
    for row in diagnosis['public_compile_checks']:
        value=text(row['path']); assert sha(ROOT/row['path'])==row['sha256'] and not re.findall(r'%Warning-(?:MULTIDRIVEN|LATCH|UNOPTFLAT):',value)
    inherited=diagnosis['backend_inherited']; newer=text(inherited['source_actual_log']['path']); older=text(inherited['source_previous_log']['path'])
    assert re.findall(r'^%Warning-(?:MULTIDRIVEN|LATCH|UNOPTFLAT):.*',newer,re.M)==re.findall(r'^%Warning-(?:MULTIDRIVEN|LATCH|UNOPTFLAT):.*',older,re.M)==inherited['raw_headers']
    tbrow=inherited['testbench_identical_to_s8']; assert raw(tbrow['path'])==raw(tbrow['previous_path'])
    traces=text('report/evidence/S2B-T17/conv_output_address_trace_20261011_r01/simulation.log')
    assert 'layers=15 outputs=5234944 requests=12286976 cycles=102468267' in traces and 'PUBLIC_ENTRY trials=12' in traces
    layerlog=text('report/evidence/S2B-T17/conv_output_address_layer0_20261011_r01/simulation.log')
    assert 'bytes=1384448 mismatches=0' in layerlog and 'requests=2551955 responses=2551955' in layerlog and 'cycles=27235743' in layerlog
    layerreport=read('report/evidence/S2B-T17/conv_output_address_layer0_20261011_r01/validation.json')
    cpu=layerreport['independent_cpu_layer0']; assert cpu['status']=='PASS' and cpu['mismatches']==0 and cpu['blas_threads_before_after']==[1,1]
    REPORT['g1_evidence_counts']={k:g1[k] for k in ['direct','boundary','layer0','backend','geometry']}
    manual=[('normal',(8,3,13,13,8,4,8,4,100,32,8,0,64)),('channel32_wrap',(U32,1,1,1,0,0,0,0,0,1,8,0,64)),('coordinate32_wrap',(0,0,1,1,U32,1,U32,1,0,1,8,0,64)),('offset64_wrap',(2**31,0,65536,131072,0,0,0,0,0,1,8,0,64)),('address64_wrap',(2,0,2**31,U32,0,0,U32,0,1,1,8,0,64)),('low32_alias',(1,0,65536,65536,0,0,0,0,0,2,8,0,64)),('base33carry',(0,0,1,2,0,0,1,0,U32,1,8,0,64)),('unconsumed_lane',(U32,U32,U32,U32,U32,U32,U32,U32,U32,U32,0,0,64)),('unconsumed_point',(0,0,U32,U32,0,0,0,0,U32,U32,8,64,64))]
    assert oracle(manual[0][1])[3]==2027 and oracle(manual[3][1])[3]==0 and oracle(manual[4][1])[4]==0 and oracle(manual[5][1])[3]==2**32 and oracle(manual[6][1])[4]==2**32
    vectors=[(v,oracle(v)) for n,v in manual]; rng=random.Random(SEED)
    edge=[0,1,2,7,8,13,65535,65536,65537,2**31,U32]
    for i in range(24000):
        v=[rng.choice(edge) if i%4==0 else rng.getrandbits(32) for n in s9.INPUTS]
        if i%3==0: v[1]=rng.randrange(8); v[10]=8; v[11]=rng.randrange(64); v[12]=64
        vectors.append((tuple(v),oracle(v)))
    counts=Counter(g[6] for v,g in vectors)
    REPORT['independent_math']={'seed':SEED,'vectors':len(vectors),'branch_counts':dict(counts),'manual':[{'name':n,'input':v,'expected':oracle(v)} for n,v in manual]}
    (WORK/'address_vectors.txt').write_text('\n'.join(' '.join(f'{a:x}' for a in (*v,*g)) for v,g in vectors)+'\n',encoding='utf-8')
    (WORK/'tb_s2b_conv_output_address.sv').write_text(s9.bench(),encoding='utf-8')
    model=read(s9.support.MODEL); names,data,small,math=conv.vectors(model)
    (WORK/'validation_vectors.txt').write_text(data,encoding='utf-8')
    (WORK/'tb_s2b_conv_validation.sv').write_text(conv.boundary_tb(names,small),encoding='utf-8')
    REPORT['public_boundary_vectors']=math['vectors']
    source=WORK/'source'; source.mkdir()
    for p in conv.RTL: shutil.copyfile(ROOT/p,source/Path(p).name)
    (source/'s8_conv_tile_engine_original.sv').write_text(oldtext.replace('module s2b_conv_tile_engine (','module s2b_conv_tile_engine_original ('),encoding='utf-8')
    tool=Path(r'D:\FPGA_S2A_MSYS2_20261001\env'); bin=tool/'mingw64/bin'; make=tool/'usr/bin'; env=os.environ.copy()
    env.update(PATH=str(make)+os.pathsep+str(bin)+os.pathsep+env['PATH'],VERILATOR_ROOT=str(tool/'mingw64/share/verilator'),PYTHONUTF8='1')
    heavy=[p.info for p in psutil.process_iter(['pid','name']) if p.info['name'] and re.fullmatch(r'(?:vivado|verilator_bin|cc1plus|Vtb_.*)\.exe',p.info['name'],re.I)]
    REPORT['preflight']={'heavy':heavy,'ram_available':psutil.virtual_memory().available,'disk_free':shutil.disk_usage(WORK).free,'rss_limit':1610612736,'disk_budget':1073741824}; assert not heavy and REPORT['preflight']['ram_available']>2**31 and REPORT['preflight']['disk_free']>2**30
    common=[str(bin/'verilator_bin.exe'),'--binary','--timing','--timescale','1ns/1ps','-Wall','-Wno-fatal','-j','1','--threads','1','--output-split','10000','--output-split-cfuncs','100','-MAKEFLAGS','PYTHON3=\'"'+sys.executable+'"\'','-CFLAGS','-D_GLIBCXX_USE_CXX11_ABI=0 -O1']
    for label,top,files in [('direct','tb_s2b_conv_output_address',['source/s2a_network_descriptor_pkg.sv','source/s8_conv_tile_engine_original.sv','source/s2b_conv_tile_engine.sv','tb_s2b_conv_output_address.sv']),('public','tb_s2b_conv_validation',['source/'+Path(p).name for p in conv.RTL]+['tb_s2b_conv_validation.sv'])]:
        run(label+'_compile',common+['--top-module',top,'--Mdir','build_'+label,*files],env=env)
        sim=[str(WORK/('build_'+label)/('V'+top+'.exe'))]
        if label=='direct': sim+=['+VECTOR_PATH='+str(WORK/'address_vectors.txt').replace('\\','/')]
        run(label+'_simulation',sim,env=env)
        actual_log=(WORK/(label+'_compile.log')).read_text(encoding='utf-8'); kinds=re.findall(r'^%Warning-(?:MULTIDRIVEN|LATCH|UNOPTFLAT):.*',actual_log,re.M)
        assert not kinds if label=='public' else len(kinds)==26 and all('MULTIDRIVEN' in k for k in kinds)
    assert f'vectors={len(vectors)}' in (WORK/'direct_simulation.log').read_text(encoding='utf-8')
    assert 'abort_mask=000fffff reset_mask=000fffff response_cases=24 raw80=1' in (WORK/'public_simulation.log').read_text(encoding='utf-8')
    for row in freeze['source_files']: assert sha(ROOT/row['path'])==row['sha256']
    REPORT.update(status='PASS_S9_FUNCTIONAL_G2_ONLY',source_freeze_sha256=sha(BASE/'source_freeze.json'),modified_files=freeze['modified_files'],source_sha256={r['path']:r['sha256'] for r in freeze['source_files']},elapsed_seconds=round(time.monotonic()-start,3),diagnostic_scope='26 direct TB only; 16 inherited backend; zero of those classes public boundary/layer0/geometry')
try: main()
except Exception: REPORT['status']='FAIL'; REPORT['traceback']=traceback.format_exc()
(WORK/'validation.json').write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(WORK/'direct_inputs.json').write_text(json.dumps(sorted(p.relative_to(ROOT).as_posix() for p in INPUTS),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':REPORT['status'],'seconds':REPORT.get('elapsed_seconds'),'error':REPORT.get('traceback')},ensure_ascii=False))
raise SystemExit(0 if REPORT['status'].startswith('PASS') else 1)
