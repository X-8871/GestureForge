"""独立只读审查：改变合法刺激重跑真实非卷积RTL，所有输出留在隔离目录。"""
from pathlib import Path
import hashlib, importlib.util, json, math, os, re, shutil, subprocess, sys, time
sys.stdout.reconfigure(encoding='utf-8')
WORK=Path(__file__).resolve().parent
ROOT=WORK.parents[3]
START=time.monotonic()
def sha(p):
    """绑定原始字节。"""
    return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,p):
    """导入只读函数，不调用工程入口。"""
    s=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
r=load('coordinate_runner',ROOT/'verification/test_s2b_backend_coordinates_rtl.py')
c=load('platform_checker',ROOT/'verification/check_s2b_inference_platform.py')
report={'status':'FAIL','baseline_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'runs':[],
 'limitations':['复用已审阅的Developer TB生成函数；独立改变响应数据和背压/owner周期，独立检查请求oracle来源及边界数学。',
 '原backend仅更名，实际pool/route/up；共享conv stub仅控制，CONV数值/109整网/STA/G3 NOT_RUN。',
 '每个非conv层从合法DISPATCH入口独立启动；不执行前置卷积；边界内部控制对双方同注入。'],
 'resource_budget':{'jobs':1,'threads':1,'rss_limit_bytes':1610612736,'cache_limit_bytes':314572800,'evidence_limit_bytes':104857600}}
try:
    bindings=c.check_static(ROOT); report['source_sha256_pre']={**bindings,r.RUNNER:sha(ROOT/r.RUNNER)}
    report['frozen14_pre']={p:sha(ROOT/p) for p in c.FROZEN_CORE_SHA256}
    model=json.loads((ROOT/r.MODEL).read_text(encoding='utf-8')); assert sha(ROOT/r.MODEL)==r.MODEL_SHA
    report['model_sha256']=sha(ROOT/r.MODEL)
    # 独立用线性索引divmod和受限计数递增验证每层所有合法坐标。
    checks=0; per_layer=[]
    for l,row in enumerate(model['layers']):
        n,ch,h,w=row['output_shape_nchw']; assert n==1 and ch<=512 and h<=208 and w<=208
        cc=yy=xx=0
        for i in range(ch*h*w):
            dc,rem=divmod(i,h*w); dy,dx=divmod(rem,w)
            assert (cc,yy,xx)==(dc,dy,dx)
            checks+=1
            if i+1<ch*h*w:
                if xx+1==w:
                    xx=0
                    if yy+1==h: yy=0; cc+=1
                    else: yy+=1
                else: xx+=1
                assert cc<512 and yy<256 and xx<256
        per_layer.append({'layer':l,'shape':[n,ch,h,w],'coordinates':ch*h*w})
    report['independent_coordinate_proof']={'checks':checks,'layers':per_layer}
    report['rom_manifest_checks']=r.math_proof(model,(ROOT/r.RTL[0]).read_text(encoding='utf-8'))
    report['checker_negatives']=r.checker_negatives(c,WORK,bindings)
    original=subprocess.check_output(['git','show',r.BASELINE+':src/s2b_network_backend.sv'],cwd=ROOT)
    assert hashlib.sha256(original).hexdigest()==r.OLD_BACKEND_SHA
    (WORK/'s1_backend_raw.sv').write_bytes(original)
    source=WORK/'source'; source.mkdir()
    for p in r.RTL: shutil.copyfile(ROOT/p,source/Path(p).name)
    (source/'s1_network_backend.sv').write_text(original.decode('utf-8').replace('module s2b_network_backend (','module s2b_network_backend_original ('),encoding='utf-8',newline='\n')
    tb=r.generate_tb(model)
    changes=[("address ^ (address>>8) ^ 32'ha5","(address*32'd37) ^ (address>>7) ^ 32'h3c"),
             ('(cycles%11)!=0','(cycles%17)!=0'),('(cycles%29)!=0','(cycles%31)!=0')]
    for before,after in changes:
        assert tb.count(before)==1; tb=tb.replace(before,after)
    report['independent_stimulus_changes']=changes
    (WORK/'tb_s2b_backend_coordinates.sv').write_text(tb,encoding='utf-8',newline='\n')
    (WORK/'convolution_stub.sv').write_text(r.convolution_stub(),encoding='utf-8',newline='\n')
    env=os.environ.copy(); tool=Path(r'D:\FPGA_S2A_MSYS2_20261001\env'); bins=tool/'mingw64/bin'; make=tool/'usr/bin'
    env['PATH']=str(make)+os.pathsep+str(bins)+os.pathsep+env.get('PATH',''); env['VERILATOR_ROOT']=str(tool/'mingw64/share/verilator'); env['PYTHONUTF8']='1'
    for p in (bins/'verilator_bin.exe',bins/'g++.exe',make/'make.exe'): c.exact_file(p)
    import psutil
    report['preflight']={'available_ram_bytes':psutil.virtual_memory().available,'disk_free_bytes':shutil.disk_usage(WORK).free,
      'heavy_processes':[{'pid':p.pid,'name':p.info['name']} for p in psutil.process_iter(['name']) if p.info['name'] and any(s in p.info['name'].lower() for s in ('vivado','verilator','vtb_'))]}
    assert report['preflight']['available_ram_bytes']>=2147483648 and report['preflight']['disk_free_bytes']>=1073741824
    assert not report['preflight']['heavy_processes']
    report['tool_versions']={'python':sys.version,'verilator':subprocess.check_output([str(bins/'verilator_bin.exe'),'--version'],env=env,cwd=WORK,text=True).strip()}
    command=[str(bins/'verilator_bin.exe'),'--binary','--timing','--timescale','1ns/1ps','-Wall','-Wno-fatal','-j','1','--threads','1',
      '--output-split','10000','--output-split-cfuncs','100','--top-module','tb_s2b_backend_coordinates','--Mdir','obj_dir',
      '-MAKEFLAGS',"PYTHON3='\""+sys.executable+"\"'",'-CFLAGS','-D_GLIBCXX_USE_CXX11_ABI=0 -O1',
      *['source/'+Path(p).name for p in r.RTL],'source/s1_network_backend.sv','convolution_stub.sv','tb_s2b_backend_coordinates.sv']
    r.execute('compile',command,WORK,WORK,env,report,600)
    r.execute('simulation',[str(WORK/'obj_dir/Vtb_s2b_backend_coordinates.exe')],WORK,WORK,env,report,1200)
    log=(WORK/'simulation.log').read_text(encoding='utf-8')
    found=re.findall(r'PASS BACKEND_COORDINATES boundary=(\d+) layers=(\d+) outputs=(\d+) requests=(\d+) cycles=(\d+) owner_drop_results=(\d+)',log)
    assert len(found)==1
    counts=dict(zip(('boundary_cases','nonconv_layers','nonconv_outputs','nonconv_requests','cycles','owner_drop_results'),map(int,found[0])))
    assert counts['boundary_cases']==4980736 and counts['nonconv_layers']==15 and counts['nonconv_outputs']==5234944 and counts['nonconv_requests']==12286976 and counts['owner_drop_results']>0
    report['simulation_counts']=counts
    report['trace_summaries']=re.findall(r'TRACE layer=(\d+) op=(\d+) outputs=(\d+) requests=(\d+) cycles=(\d+) digest=([0-9a-fA-F]+)',log)
    report['source_sha256_post']={p:sha(ROOT/p) for p in report['source_sha256_pre']}; assert report['source_sha256_post']==report['source_sha256_pre']
    report['frozen14_post']={p:sha(ROOT/p) for p in c.FROZEN_CORE_SHA256}; assert report['frozen14_post']==report['frozen14_pre']
    report['status']='PASS_INDEPENDENT_RTL_EXPERIMENT'
except Exception as exc:
    report['failure']=repr(exc)
report['seconds']=round(time.monotonic()-START,6)
report['files']=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in WORK.iterdir() if p.is_file()]
(WORK/'rtl_receipt.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'seconds':report['seconds'],'counts':report.get('simulation_counts'),'failure':report.get('failure')},ensure_ascii=False),flush=True)
raise SystemExit(0 if report['status']=='PASS_INDEPENDENT_RTL_EXPERIMENT' else 1)
