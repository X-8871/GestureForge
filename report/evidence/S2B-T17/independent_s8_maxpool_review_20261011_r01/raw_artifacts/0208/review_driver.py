"""S8独立审查：无限精度黄金、冻结字节和真实RTL回归。"""
from pathlib import Path
import sys, os, json, hashlib, subprocess, random, itertools, time, shutil, traceback
from collections import Counter
ROOT = Path.cwd()
WORK = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'verification'))
import test_s2b_maxpool_address_guard_rtl as s8
import test_s2b_geometry_specialization_rtl as eng
import psutil
SEED = 0x11A85C29
U = 2**32-1
report = {'status':'RUNNING','seed':SEED,'runs':[],'findings':[]}
direct = set()
def sha(p):
    """实际原始字节绑定。"""
    return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    """记录直接读取的输入。"""
    p=ROOT/p if isinstance(p,str) else p
    direct.add(p)
    return json.loads(p.read_text(encoding='utf-8'))
def golden(v):
    """直接按NCHW定义；无RTL分段算式或被审oracle依赖。"""
    b,c,h,w,kh,kw,sy,sx,p,ch,y,x=v
    blank=(0,)*40
    if (kh,kw) not in [(2,2),(3,3)] or min(c,h,w,sy,sx)==0 or h+p<kh or w+p<kw:
        return (1,)+blank
    oh=1+(h+p-kh)//sy; ow=1+(w+p-kw)//sx
    if ch>=c or y>=oh or x>=ow: return (1,)+blank
    taps=[]; mask=0; bad=False
    for i in range(9):
        if i>=kh*kw: taps.extend([0]*4); continue
        yy=y*sy-p//2+i//kw; xx=x*sx-p//2+i%kw; a=0
        if yy in range(h) and xx in range(w):
            mask |= 1<<i
            a=b+(ch*h+yy)*w+xx
            if a>U: bad=True; a=0
        taps.extend([a,ch,yy%(2**64),xx%(2**64)])
    return (2,)+blank if bad else (0,oh,ow,kh*kw,mask,*taps)
def main():
    """每次只启动一个编译，保留原生码及失败。"""
    started=time.monotonic()
    assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==eng.BASELINE
    freeze=read('report/evidence/S2B-T17/maxpool_address_guard_20261011_r01/source_freeze.json')
    assert len(freeze['source_files'])==41 and len(freeze['active_rtl_sources'])==18
    report['source_freeze_sha256']=sha(ROOT/'report/evidence/S2B-T17/maxpool_address_guard_20261011_r01/source_freeze.json')
    for row in freeze['source_files']:
        path=ROOT/row['path']; snap=ROOT/row['snapshot']; direct.update([path,snap])
        assert sha(path)==sha(snap)==row['sha256'] and path.stat().st_size==row['bytes'],row['path']
    report['source_sha256']={r['path']:r['sha256'] for r in freeze['source_files']}
    for p,d in freeze['frozen14'].items(): assert sha(ROOT/p)==d
    diff=subprocess.check_output(['git','diff','--',*[r['path'] for r in freeze['source_files']]])
    (WORK/'reviewed_tracked_diff.patch').write_bytes(diff)
    expected=ROOT/'tmp/2B/S2B-T17/s8_root_run_20261011_r01/source_diff_at_stop.patch'; direct.add(expected)
    assert sha(expected)==sha(WORK/'reviewed_tracked_diff.patch')=='b7958f18dd3752a82a905d042e6924ceecf47228c3cc6ac59b666cc72162f49e'
    old=subprocess.check_output(['git','show',eng.BASELINE+':src/s2b_maxpool_engine.sv']).decode('utf-8')
    current=(ROOT/'src/s2b_maxpool_engine.sv').read_text(encoding='utf-8')
    assert current==old.replace('int8_maxpool_geometry u_geometry','s2b_maxpool_geometry u_geometry')
    report['always_ff_sha256']=hashlib.sha256(current.split('    always_ff',1)[1].encode()).hexdigest()
    checker=eng.load_checker(); bindings=checker.check_static(ROOT)
    report['static_binding_count']=len(bindings)
    report['mutants']=s8.mutants(checker,WORK,bindings)
    report['public_negative']=eng.checker_negatives(checker,WORK,bindings)
    for run in ('maxpool_address_guard_20261011_r01','maxpool_address_guard_trace_20261011_r01'):
        base=ROOT/'report/evidence/S2B-T17'/run
        validation=read(base/'validation.json')
        for p,d in validation['source_sha256_pre'].items():
            if p.endswith('.md'):
                assert freeze['tested_source_drift'][run][p]['tested']==d
            else: assert sha(ROOT/p)==d,p
        for item in validation['runs']:
            log=ROOT/item['log']; direct.add(log)
            assert sha(log)==item['log_sha256'] and item['exit_code']==0 and item['failure'] is None
        manifest=read(base/'delivery_manifest.json')
        for item in manifest['files']:
            p=ROOT/item['path']; assert sha(p)==item['sha256'],item['path']
        for mode,expected_rc in [('evidence',0),('inputs',2)]:
            eng.execute(run+'_'+mode,[sys.executable,'-B','verification/check_stage_delivery.py','--mode',mode,'--manifest',str(base/'delivery_manifest.json')],ROOT,WORK,os.environ.copy(),report,60) if expected_rc==0 else package_negative(run,base,mode)
    cap=read('report/evidence/S2B-T17/maxpool_address_guard_trace_20261011_r01/runtime_cache_capture.json')
    source=(ROOT/cap['source_path']).read_bytes()
    assert hashlib.sha256(source).hexdigest()==cap['source_sha256']
    assert source.decode('utf-8').count(cap['before'])==1
    assert hashlib.sha256(source.decode('utf-8').replace(cap['before'],cap['after']).encode()).hexdigest()==cap['transformed_sha256']
    assert cap['after'].replace('/s8_pool_g1_20261011_r01','')==cap['before'] and cap['native_exit_code']==0
    rows=[]; stats=Counter(); labels=[]
    def add(name,v):
        g=golden(v); rows.append((v,g)); stats[str(g[0])]+=1
        if name!='random': labels.append({'name':name,'input':v,'expected':g})
    manual=[('huge_chw_small_window',(0,U,2,2,2,2,2,2,1,0,0,0)),
      ('unused_row2_overflow',(0,1,3,2**31,2,2,2,2,1,0,0,0)),
      ('padding_high_channel',(U,U,U,U,3,3,1,1,U,U-1,0,0)),
      ('channel_product_high',(0,3,2**31,2,2,2,2,2,1,2,0,0)),
      ('row_carry',(0,2,U,1,2,2,1,1,1,1,1,0)),
      ('width_high',(0,1,3,U,2,2,1,1,1,0,1,0)),
      ('column_carry',(0,1,3,U-1,2,2,1,1,1,0,1,2)),
      ('base_carry',(U-2,1,2,2,2,2,2,2,1,0,0,0)),
      ('last_byte',(U-3,1,2,2,2,2,2,2,1,0,0,0)),
      ('extent33',(0,1,U,U,3,3,1,1,U,0,U,U)),
      ('signed_negative_padding',(0,1,2,2,3,3,3,5,U,0,0,0)),
      ('arg_before_range',(U,1,U,U,2,2,2,2,0,1,0,0))]
    for n,v in manual: add(n,v)
    assert [golden(v)[0] for n,v in manual]==[0,0,0,2,2,2,2,2,0,2,0,1]
    assert golden(manual[8][1])[5:21:4]==(U-3,U-2,U-1,U)
    rng=random.Random(SEED)
    vals=[0,1,2,3,7,13,65535,65536,2**31-1,2**31,U-1,U]
    for _ in range(15000):
        c,h,w=[rng.choice(vals+[rng.getrandbits(32)]) for i in range(3)]
        k=rng.choice([2,3]); p=rng.choice(vals); sy,sx=[rng.choice([0,1,2,3,5,7,U]) for i in range(2)]
        oh=0 if sy==0 else max(0,(h+p-k)//sy+1); ow=0 if sx==0 else max(0,(w+p-k)//sx+1)
        ch=rng.choice([0,max(0,c-1),c,rng.getrandbits(32)])
        y=rng.choice([0,min(U,max(0,oh-1)),min(U,oh),rng.getrandbits(32)])
        x=rng.choice([0,min(U,max(0,ow-1)),min(U,ow),rng.getrandbits(32)])
        add('random',(rng.choice([0,U,rng.getrandbits(32)]),c,h,w,k,k,sy,sx,p,ch,y,x))
    for k,sy,sx,p in itertools.product([2,3],[1,2,3,5],[1,2,3,7],[0,1,2,3,7]):
        h,w,c=5,7,3
        for ch,y,x in itertools.product(range(c),range(max(0,(h+p-k)//sy+1)),range(max(0,(w+p-k)//sx+1))):
            add('random',(100,c,h,w,k,k,sy,sx,p,ch,y,x))
    for i in range(12):
        v=list(manual[0][1]); v[i]=0; add('zero_field_'+str(i),tuple(v))
    for kh,kw in [(0,0),(1,1),(2,3),(3,2),(4,4),(U,U)]:
        v=list(manual[0][1]); v[4:6]=[kh,kw]; add('invalid_kernel',tuple(v))
    (WORK/'geometry_vectors.dat').write_text('\n'.join(' '.join(format(a,'x') for a in (*v,*g)) for v,g in rows)+'\n',encoding='utf-8')
    (WORK/'tb_s8_geometry.sv').write_text(s8.geometry_tb(),encoding='utf-8')
    report['geometry']={'vectors':len(rows),'error_counts':dict(stats),'all_padding_ok':sum(g[0]==0 and g[4]==0 for v,g in rows),'manual':labels}
    model=read(eng.MODEL); eng.SEED=SEED+1
    declarations={'pool':eng.ports(ROOT/'src/s2a_maxpool_engine.sv'),'upsample':eng.ports(ROOT/'src/s2a_upsample_engine.sv')}
    report['engine']={}
    for kind in declarations:
        data,count=eng.vector_data(kind,declarations[kind],model)
        (WORK/(kind+'_vectors.dat')).write_text(data,encoding='utf-8'); report['engine'][kind]=count
    (WORK/'tb_s2b_geometry_specialization.sv').write_text(s8.engine_tb(declarations,model),encoding='utf-8')
    src=WORK/'source'; src.mkdir()
    for p in eng.RTL: shutil.copyfile(ROOT/p,src/Path(p).name)
    env=os.environ.copy(); tool=Path(r'D:\FPGA_S2A_MSYS2_20261001\env'); bd=tool/'mingw64/bin'; md=tool/'usr/bin'
    env.update(PATH=str(md)+os.pathsep+str(bd)+os.pathsep+env['PATH'],VERILATOR_ROOT=str(tool/'mingw64/share/verilator'),PYTHONUTF8='1')
    processes=[{'pid':p.pid,'name':p.info['name']} for p in psutil.process_iter(['name']) if p.info['name'] and p.info['name'].lower() in ['vivado.exe','verilator_bin.exe','cc1plus.exe','xsim.exe']]
    assert not processes,processes
    report['preflight']={'available_ram':psutil.virtual_memory().available,'disk_free':shutil.disk_usage(WORK).free,'heavy_processes':processes}
    assert report['preflight']['available_ram']>2**31
    common=[str(bd/'verilator_bin.exe'),'--binary','--timing','--timescale','1ns/1ps','-Wall','-Wno-fatal','-j','1','--threads','1','--output-split','10000','--output-split-cfuncs','100','-MAKEFLAGS','PYTHON3=\'"'+sys.executable+'"\'','-CFLAGS','-D_GLIBCXX_USE_CXX11_ABI=0 -O1']
    for label,top,files in [('geometry','tb_s8_geometry',['source/int8_maxpool_geometry.sv','source/s2b_maxpool_geometry.sv','tb_s8_geometry.sv']),('engine','tb_s2b_geometry_specialization',['source/'+Path(p).name for p in eng.RTL]+['tb_s2b_geometry_specialization.sv'])]:
        eng.execute(label+'_compile',common+['--top-module',top,'--Mdir','build_'+label,*files],WORK,WORK,env,report,300)
        eng.execute(label+'_simulation',[str(WORK/('build_'+label)/('V'+top+'.exe'))],WORK,WORK,env,report,60)
        log=(WORK/(label+'_compile.log')).read_text(encoding='utf-8')
        assert not any('%Warning-'+w in log for w in ['LATCH','UNOPTFLAT','MULTIDRIVEN'])
    for row in freeze['source_files']: assert sha(ROOT/row['path'])==row['sha256']
    report.update(status='PASS_S8_SOFTWARE_RTL_G2_ONLY',elapsed_seconds=round(time.monotonic()-started,3),sta='NOT_RUN',g3='NOT_RUN')
def package_negative(run,base,mode):
    """保留包装检查器真实原生失败码2。"""
    command=[sys.executable,'-B','verification/check_stage_delivery.py','--mode',mode,'--manifest',str(base/'delivery_manifest.json')]
    start=time.monotonic(); result=subprocess.run(command,cwd=ROOT,capture_output=True)
    (WORK/(run+'_'+mode+'.log')).write_bytes(result.stdout+result.stderr)
    report['runs'].append({'name':run+'_'+mode,'command':command,'exit_code':result.returncode,'seconds':time.monotonic()-start})
    assert result.returncode==2
if __name__=='__main__':
    try: main()
    except Exception:
        report['status']='FAIL'; report['traceback']=traceback.format_exc()
    (WORK/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (WORK/'direct_inputs.json').write_text(json.dumps([p.relative_to(ROOT).as_posix() for p in sorted(direct)],indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'runs':report['runs'],'geometry':report.get('geometry',{}).get('vectors'),'error':report.get('traceback')},ensure_ascii=False))
    raise SystemExit(0 if report['status'].startswith('PASS') else 1)
