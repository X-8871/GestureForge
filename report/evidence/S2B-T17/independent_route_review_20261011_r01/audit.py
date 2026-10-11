"""独立核对冻结绑定、公开来源、手算路由及机读交付检查。"""
from pathlib import Path
import hashlib, json, re, subprocess, sys, time, os
import psutil
W=Path(__file__).resolve().parent
R=W.parents[3]
B=R/'report/evidence/S2B-T17'
start=time.monotonic()
out={'status':'RUNNING','checks':[],'commands':[]}
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,ok,detail=None):
    assert ok,name
    out['checks'].append({'name':name,'status':'PASS','detail':detail})
def j(p): return json.loads(p.read_text(encoding='utf-8'))
def run(name,cmd,cwd=R,env=None,expect=0):
    t=time.monotonic(); log=W/(name+'.log'); peak=0
    with log.open('wb') as f:
        p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT)
        while p.poll() is None:
            try:
                tree=[psutil.Process(p.pid)]+psutil.Process(p.pid).children(recursive=True)
                peak=max(peak,sum(x.memory_info().rss for x in tree if x.is_running()))
            except psutil.Error: pass
            if time.monotonic()-t>60 or peak>1024**3:
                for x in reversed(tree):
                    try: x.kill()
                    except psutil.Error: pass
                raise RuntimeError('超预算停止')
            time.sleep(.1)
    rec={'name':name,'command':cmd,'native_exit_code':p.returncode,'seconds':round(time.monotonic()-t,3),'peak_tree_rss_bytes':peak,'log':log.name,'sha256':h(log)}
    out['commands'].append(rec);check(name,p.returncode==expect,rec)
    return log.read_text(encoding='utf-8',errors='replace')
try:
    f=B/'route_specialization_20261011_r07/source_freeze.json'; freeze=j(f)
    check('freeze_sha',h(f)=='b550628ca96fd193e571e7144efcc3bc1ad0f5c9123ff2ba40899edee6b52231')
    mf=B/'route_specialization_20261011_r07/delivery_manifest.json';m=j(mf)
    check('manifest_sha',h(mf)=='b6fa0a51eecd332635f5f189f1b80d18480a144fb7edde4cba515c802bbcf330')
    for p,d in freeze['source_sha256'].items():check('source_pre:'+p,h(R/p)==d)
    for row in m['files']:check('binding:'+row['path'],h(R/row['path'])==row['sha256'])
    for p,d in freeze['frozen14_sha256'].items():
        raw=subprocess.check_output(['git','show','671f9cf494b92ce182b3f1542fefd0cfd4b209f5:'+p],cwd=R)
        actual=(R/p).read_bytes()
        check('raw14_git_content:'+p,raw.replace(b'\r\n',b'\n')==actual.replace(b'\r\n',b'\n') and d==h(R/p),{'actual_raw_sha':d,'git_blob_sha':hashlib.sha256(raw).hexdigest(),'actual_crlf':actual.count(b'\r\n'),'git_crlf':raw.count(b'\r\n'),'relation':'RAW_IDENTICAL' if raw==actual else 'ONLY_CRLF_VS_LF'})
    old=(R/'src/s2a_route_engine.sv').read_text(encoding='utf-8')
    new=(R/'src/s2b_route_engine.sv').read_text(encoding='utf-8')
    check('engine_exact',old.replace('module s2a_route_engine (','module s2b_route_engine (').replace('int8_route_query u_query (','s2b_route_query u_query (')==new)
    raw=subprocess.check_output(['git','show',freeze['task_baseline_commit']+':src/s2b_network_backend.sv'],cwd=R).decode('utf-8').replace('\r\n','\n')
    check('backend_exact',raw.replace('s2a_route_engine u_route_engine','s2b_route_engine u_route_engine')==(R/'src/s2b_network_backend.sv').read_text(encoding='utf-8'))
    p=j(R/'board/s2b_inference_platform.json'); names=[]
    for s in p['rtl_sources']: names+=re.findall(r'^\s*(?:module|package)\s+(\w+)',(R/s).read_text(encoding='utf-8'),re.M)
    check('closure_18_unique',len(p['rtl_sources'])==18 and len(names)==18 and len(set(names))==18,names)
    check('no_old_route_active','src/int8_route_query.sv' not in p['rtl_sources'] and 'src/s2a_route_engine.sv' not in p['rtl_sources'])
    rom=(R/'src/s2a_network_descriptor_pkg.sv').read_text(encoding='utf-8')
    def arr(n):return [int(x,16) for x in re.findall(r"\d+'h([0-9a-fA-F]+)",re.search(r'\b'+n+r"\s+\[0:37\].*?=\s*'\{(.*?)\};",rom,re.S).group(1))]
    g,gid=arr('S2A_GROUP_COUNT'),arr('S2A_ROUTE_GROUP_ID')
    layers=[3,6,8,11,14,16,19,22,24,31,34]
    check('rom_domain',all((g[i],gid[i])==((2,1) if i in [3,11,19] else (1,0)) for i in layers),[(i,g[i],gid[i]) for i in layers])
    ds={rid:j(B/rid/'validation.json') for rid in ['route_specialization_20261011_r08','route_specialization_20261011_r05','route_specialization_20261011_r06','coordinates_20261011_r04']}
    check('trace15_identical',ds['route_specialization_20261011_r05']['trace_summaries']==ds['coordinates_20261011_r04']['trace_summaries'])
    for rid in list(ds)[:3]:
        d=ds[rid]
        check('run_status:'+rid,d['status'].startswith('PASS') and all(x['exit_code']==0 for x in d['runs']))
        for a in d['artifacts']:check('artifact:'+a['path'],h(R/a['path'])==a['sha256'])
        for k,digest in d['source_sha256_pre'].items():check('run_pre_post:'+rid+':'+k,digest==d['source_sha256_post'][k]==h(R/k))
    run('static',[sys.executable,'-X','utf8','-B','verification/check_s2b_inference_platform.py'])
    run('evidence',[sys.executable,'-X','utf8','-B','verification/check_stage_delivery.py','--mode','evidence','--manifest',str(mf)])
    run('inputs',[sys.executable,'-X','utf8','-B','verification/check_stage_delivery.py','--mode','inputs','--manifest',str(mf)],expect=2)
    run('diff',['git','diff','--check'])
    # 独立夹具不导入Developer oracle，合法小尺寸用整数手算，另覆盖地址及错误优先。
    source=(R/'src/int8_route_query.sv').read_text(encoding='utf-8')
    ports=re.findall(r'^\s*(input|output)\s+logic\s*(signed\s*)?(\[[^\]]+\])?\s*(\w+)',source.split(');',1)[0],re.M)
    ins=[n for d,s,w,n in ports if d=='input'];outs=[n for d,s,w,n in ports if d=='output']
    tb=['module tb_independent; integer cases=0;']
    for d,s,w,n in ports:
        tb.append('logic '+s+w+' '+(n if d=='input' else 'a_'+n+',b_'+n)+';')
    for label,module in [('a','int8_route_query'),('b','s2b_route_query')]:
        tb.append(module+' '+label+' ('+','.join('.'+n+'('+(n if d=='input' else label+'_'+n)+')' for d,s,w,n in ports)+');')
    rows=[]
    for group in [1,2]:
        for groupid in range(group):
            for val in [-127,-126,-31,-3,-1,0,1,3,31,126,127]:
                for mul in [1,0x40000000,0x7fffffff,0x80000000]:
                    for ch,y,x in [(0,0,0),(1,1,2),(8//group-1,1,2)]:
                        v={n:0 for n in ins};v.update(source_count=1,groups=group,group_id=groupid,source0_base_address=0x1001,source0_length_bytes=48,source0_channels=8,source0_height=2,source0_width=3,source0_channel_start=groupid*(8//group),source0_channel_end=(groupid+1)*(8//group),source0_multiplier_q31=mul,source0_value=val,output_channel=ch,output_y=y,output_x=x)
                        sch=groupid*(8//group)+ch;mag=(abs(val)*mul+2**30)//2**31
                        exp=dict(output_channels=8//group,output_height=2,output_width=3,source_index=0,source_channel=sch,source_address=0x1001+sch*6+y*3+x,output_value=(-mag if val<0 else mag)&255,error_code=0)
                        rows.append((v,exp,True))
    for group,c,begin,end in [(3,6,2,4),(4,8,2,4),(0x80000000,0x80000000,1,2),(0xffffffff,0xffffffff,1,2)]:
        v={n:0 for n in ins};v.update(source_count=1,groups=group,group_id=1,source0_channels=c,source0_height=1,source0_width=1,source0_length_bytes=c,source0_channel_start=begin,source0_channel_end=end,source0_multiplier_q31=0x80000000,source0_value=23)
        rows.append((v,{n:0 for n in outs}|{'error_code':1},False))
    legal=rows[0][0]
    for changes,error in [({'groups':0,'source0_length_bytes':0},1),({'group_id':2,'source0_base_address':0xffffffff},1),({'source0_length_bytes':0},2),({'source0_base_address':0xfffffff0},2),({'source0_value':-128},1),({'source0_multiplier_q31':0xffffffff},1),({'output_y':2},1),({'source0_channels':0xffffffff,'source0_height':0xffffffff},1)]:
        rows.append((legal|changes,{n:0 for n in outs}|{'error_code':error},True))
    tb.append('initial begin')
    for v,exp,same in rows:
        tb.append(' '.join(n+'=32\'h'+format(x&0xffffffff,'x')+';' for n,x in v.items())+' #1;')
        for n,x in exp.items():tb.append('if(b_'+n+'!=='+('8' if n=='output_value' else '3' if n=='error_code' else '32')+"'h"+format(x,'x')+') $fatal(1,"手算失败 '+n+' case=%0d",cases);')
        if same:
            for n in outs:tb.append('if(a_'+n+'!==b_'+n+')$fatal(1,"差分失败 '+n+'");')
        else:tb.append('if(a_error_code!=0)$fatal(1,"原通用合法输入失败");')
        tb.append('cases++;')
    tb.append('$display("PASS_INDEPENDENT_QUERY cases=%0d",cases);$finish;end endmodule')
    (W/'tb_independent.sv').write_text('\n'.join(tb)+'\n',encoding='utf-8',newline='\n')
    (W/'vectors.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    env=os.environ.copy();tc=Path(r'D:\FPGA_S2A_MSYS2_20261001\env');env['PATH']=str(tc/'usr/bin')+os.pathsep+str(tc/'mingw64/bin')+os.pathsep+env['PATH'];env['VERILATOR_ROOT']=str(tc/'mingw64/share/verilator');env['PYTHONUTF8']='1'
    out['preflight']={'available_ram':psutil.virtual_memory().available,'disk_free':psutil.disk_usage(str(W)).free,'processes':[{'pid':p.pid,'name':p.info['name'],'rss':p.memory_info().rss} for p in psutil.process_iter(['name']) if p.info['name'] and p.info['name'].lower() in ['vivado.exe','verilator_bin.exe','cc1plus.exe']]}
    check('resource_budget',out['preflight']['available_ram']>1024**3 and out['preflight']['disk_free']>300*1024**2,out['preflight'])
    cmd=[str(tc/'mingw64/bin/verilator_bin.exe'),'--binary','--timing','--timescale','1ns/1ps','-Wall','-Wno-fatal','-j','1','--threads','1','--top-module','tb_independent','--Mdir','obj_dir','-MAKEFLAGS',"PYTHON3='\""+sys.executable+"\"'",'-CFLAGS','-D_GLIBCXX_USE_CXX11_ABI=0 -O1',str(R/'src/int8_route_query.sv'),str(R/'src/s2b_route_query.sv'),'tb_independent.sv']
    run('compile',cmd,W,env)
    text=run('simulation',[str(W/'obj_dir/Vtb_independent.exe')],W,env)
    check('independent_count','PASS_INDEPENDENT_QUERY cases='+str(len(rows)) in text,len(rows))
    for p,d in freeze['source_sha256'].items():check('source_post:'+p,h(R/p)==d)
    check('freeze_post',h(f)=='b550628ca96fd193e571e7144efcc3bc1ad0f5c9123ff2ba40899edee6b52231')
    out['status']='PASS'
except Exception as e:
    out['status']='FAIL';out['error']=repr(e)
finally:
    out['seconds']=round(time.monotonic()-start,3)
    (W/'audit_results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':out['status'],'error':out.get('error'),'checks':len(out['checks']),'commands':out['commands'],'seconds':out['seconds']},ensure_ascii=False,indent=2))
sys.exit(0 if out['status']=='PASS' else 1)
