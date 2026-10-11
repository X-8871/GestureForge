#!/usr/bin/env python3
"""独立核对G1原件、失败口径和继承告警，执行包装检查并冻结G2结论。"""
from pathlib import Path
import collections
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import time
import types
import traceback
W=Path(__file__).resolve().parent
R=W.parents[3]
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('independent_review_helpers',W/'review_r02.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.RESULT=m.read(W/'independent_rtl_receipt_r02.json')

def raw_json(p):
    return {'path':p.relative_to(R).as_posix(),'sha256':m.digest(p)}

def warning_blocks(path):
    """逐字包含全部诊断正文，保留日志一基行号；排除随后的编译命令。"""
    lines=path.read_text(encoding='utf-8').splitlines(keepends=True);blocks=[]
    for i,line in enumerate(lines):
        if line.startswith('%Warning-MULTIDRIVEN:'):
            j=i+1
            while j<len(lines) and (lines[j].startswith((' ','\t')) or lines[j].strip()==''):j+=1
            text=''.join(lines[i:j])
            blocks.append({'line':i+1,'end_line':j,'text':text,'sha256':hashlib.sha256(text.encode()).hexdigest()})
    return blocks

def audit_g1():
    """从日志和编译源独立核对G1量化结果；长回归仅绑定。"""
    formal=m.FORMAL; freeze=m.read(formal/'source_freeze.json'); integrity=m.read(formal/'source_integrity.json')
    q1=R/'report/evidence/S2B-T17/route_address_guard_20261011_r01'
    q2=R/'report/evidence/S2B-T17/route_address_guard_20261011_r02'
    v1=m.read(q1/'validation.json');v2=m.read(q2/'validation.json')
    assert v1['status']=='PASS_ROUTE_ADDRESS_GUARD_G1' and v2['status']=='PASS_BACKEND_COORDINATES_G1'
    assert v1['source_commit']==v2['source_commit']==m.BASE
    for p,v in [(q1,v1),(q2,v2)]:
        cap=m.read(p/'native_capture.json');assert cap['native_exit_code']==0
        for run in v['runs']:
            assert type(run['exit_code']) is int and run['exit_code']==0 and run['failure'] is None
            assert m.digest(R/run['log'])==run['log_sha256']
            cmd=run['command'];assert not any(re.search(r'-Wno-(LATCH|UNOPTFLAT|MULTIDRIVEN)',x) for x in cmd)
            if run['name']=='compile':
                assert cmd[cmd.index('-j')+1]=='1' and cmd[cmd.index('--threads')+1]=='1'
    assert v1['runs'][0]['seconds']==19.188 and v1['runs'][0]['peak_tree_rss_bytes']==640159744 and v1['runs'][1]['seconds']==2.172
    assert v2['runs'][0]['seconds']==20.609 and v2['runs'][0]['peak_tree_rss_bytes']==667791360 and v2['runs'][1]['seconds']==166.453
    assert v1['query_coverage']['vectors']==49449 and int(v1['query_coverage']['query_error_histogram']['0'])==20669
    slog1=(q1/'simulation.log').read_text(encoding='utf-8');slog2=(q2/'simulation.log').read_text(encoding='utf-8')
    counts=re.findall(r'PASS ROUTE_SPECIALIZATION cases=(\d+) queries=(\d+) cycles=(\d+) abort=(\d+) reset=(\d+)',slog1)
    assert counts==[('25018','4642169','344751','255','255')]
    counts2=re.findall(r'PASS BACKEND_COORDINATES boundary=(\d+) layers=(\d+) outputs=(\d+) requests=(\d+) cycles=(\d+) owner_drop_results=(\d+)',slog2)
    assert counts2==[('4980736','15','5234944','12286976','102468267','120942')]
    trace=re.findall(r'TRACE layer=(\d+) op=(\d+) outputs=(\d+) requests=(\d+) cycles=(\d+) digest=([0-9a-f]+)',slog2)
    assert len(trace)==15 and [list(x) for x in trace]==v2['trace_summaries']
    assert sum(int(x[2]) for x in trace)==5234944 and sum(int(x[3]) for x in trace)==12286976
    model=m.read(R/'report/evidence/S2A-T01/tiny416_model_manifest.json')
    expected_nonconv=[i for i,x in enumerate(model['layers']) if x['op'] in ('route','maxpool','upsample')]
    assert [int(x[0]) for x in trace]==expected_nonconv
    for item in trace:
        layer,op,outs,req,cycles,dg=item; row=model['layers'][int(layer)]
        n,c,h,w=row['output_shape_nchw'];assert int(outs)==n*c*h*w
        assert int(req)==int(outs)*(5 if row['op']=='maxpool' else 2)
    mask=sum(1<<i for i,x in enumerate(model['layers']) if x['op']=='route')
    public=re.findall(r'PUBLIC_ENTRY trials=(\d+) route_mask=([0-9a-f]+)',slog2)
    assert public==[('12',f'{mask:016x}')] and mask==int('0000000481494948',16)
    # 从RAW快照核对仿真时说明旧SHA和最终说明历史纠正；源实现必须全等。
    snapshots=q1/'source_snapshot';rawmap={p.relative_to(snapshots).as_posix():m.digest(p) for p in snapshots.rglob('*') if p.is_file()}
    assert len(rawmap)==35 and rawmap==integrity['raw_snapshot_sha256']
    md='board/s2b_inference_platform.md'; oldmd='fb5944c7b546f0dc4ccefc273e8a979f672e1214f49246a711715a611c1f87bd'
    assert rawmap[md]==oldmd and freeze['source_sha256'][md]=='a23899c4b304e932a1969c7f819a7d590e683a48282218007942b5622ed16aa1'
    for p,h in rawmap.items():
        assert h==(oldmd if p==md else freeze['source_sha256'][p]),p
        if p in freeze['frozen14_sha256']:assert (snapshots/p).read_bytes()==(R/p).read_bytes()
    before=freeze['source_sha256'].copy();before[md]=oldmd
    assert len(v1['source_sha256_pre'])==35 and v1['source_sha256_pre']==v1['source_sha256_post']=={p:before[p] for p in rawmap}
    # 编译源须是实际工作目录的文件；只授权S6模块重命名。
    compiled=[]
    for runid,val in [('route_address_guard_20261011_r01',v1),('route_address_guard_20261011_r02',v2)]:
        tmp=R/'tmp/2B/S2B-T17'/runid
        for arg in val['runs'][0]['command']:
            if not arg.endswith('.sv'):continue
            path=tmp/arg;assert path.is_file()
            if arg.startswith('source/s6_'):
                p='src/'+path.name.removeprefix('s6_');blob=m.git('show',m.BASE+':'+p)
                assert (q1/('s6_'+Path(p).name)).read_bytes()==blob
                renamed=blob.decode('utf-8').replace('s2b_route_engine','s6_route_engine').replace('s2b_route_query','s6_route_query')
                assert path.read_bytes()==renamed.encode('utf-8')
            elif arg=='source/s2_network_backend.sv':
                raw=(q2/'s2_network_backend.sv').read_bytes()
                assert hashlib.sha256(raw).hexdigest()=='7c6defe3438aa1b2afcedcfc1714d9993c773373dcdd814450d96a2b38778a27'
                assert raw==m.git('show','6d3fd8567b579a51d4042667d47af7d94f2f5a97:src/s2b_network_backend.sv')
                assert path.read_bytes()==raw.replace(b'module s2b_network_backend (',b'module s2b_network_backend_original (')
            elif arg.startswith('source/'):
                p='src/'+path.name;assert m.digest(path)==freeze['source_sha256'][p]
            else:
                assert path.read_bytes()==((q1 if runid.endswith('r01') else q2)/path.name).read_bytes()
            compiled.append({'run_id':runid,**raw_json(path)})
    assert not re.search(r'%Warning-(LATCH|UNOPTFLAT|MULTIDRIVEN)\b',(q1/'compile.log').read_text(encoding='utf-8'))
    baseline=R/'report/evidence/S2B-T17/patch_guard_20261011_r06'
    old=warning_blocks(baseline/'compile.log');new=warning_blocks(q2/'compile.log')
    assert len(old)==len(new)==16 and old==new
    assert (baseline/'tb_s2b_backend_coordinates.sv').read_bytes()==(q2/'tb_s2b_backend_coordinates.sv').read_bytes()
    assert not re.search(r'%Warning-(LATCH|UNOPTFLAT)\b',(q2/'compile.log').read_text(encoding='utf-8'))
    # 正文包含源码赋值和TB另一写入位置，两者逐条与S5完全相同。
    for item in new:
        assert 'tb_s2b_backend_coordinates.sv' in item['text'] and ('release ' in item['text'] or 'output_' in item['text'])
    backendtb=(q2/'tb_s2b_backend_coordinates.sv').read_text(encoding='utf-8')
    assert 'force ' in backendtb and 'release ' in backendtb
    assert all(not re.search(r'verilator\s+lint_off\s+(LATCH|UNOPTFLAT|MULTIDRIVEN)',(R/p).read_text(encoding='utf-8')) for p in freeze['source_sha256'] if p.endswith('.sv'))
    # 黄金来自固定模型shape/地址/scale及Q31再量化，未从候选坐标读取。
    runner=(R/'verification/test_s2b_backend_coordinates_rtl.py').read_text(encoding='utf-8')
    assert 'scales[slot]/row["output_scale"]*2**31' in runner
    m.RESULT['bound_g1']={'rerun':False,'r01_native':m.read(q1/'native_capture.json'),'r02_native':m.read(q2/'native_capture.json'),
        'r01_compile_simulation':v1['runs'],'r02_compile_simulation':v2['runs'],'r01_integer':{'samples':49449,'legal':20669},
        'r01_counts':v1['simulation_counts'],'r02_counts':v2['simulation_counts'],'trace_summaries':[list(x) for x in trace],'public_entries':public,
        'compiled_sources_actual':compiled,'snapshot_raw_count':35,'simulation_old_md_sha256':oldmd,'final_md_sha256':freeze['source_sha256'][md],
        'oracle_audit':'逐请求Golden常量从固定模型NCHW/输入引用/张量地址/route范围/scale独立建立；真实pool/route/up，CONV共享控制stub。非conv逐层合法DISPATCH注入；公共12项另无内部状态注入。未复跑15层或不变CONV layer0。'}
    m.save('inherited_warning_blocks.json',{'s5_log':raw_json(baseline/'compile.log'),'s7_log':raw_json(q2/'compile.log'),'blocks':new,'same_lines_and_full_text':True,'same_tb_raw_sha256':m.digest(q2/'tb_s2b_backend_coordinates.sv'),'new_forbidden_count':0})
    m.RESULT['warnings']={'backend_multidriven_inherited':16,'new_multidriven':0,'latch':0,'unoptflat':0,'pure_route_all_three':0,'full_warning_blocks_bound':'inherited_warning_blocks.json','warnings_suppressed':False}

def audit_failures_and_chain():
    """冻结失败与候选未批准的真实口径，并核对完整七模块派生链。"""
    freeze=m.read(m.FORMAL/'source_freeze.json');profile=m.read(R/'board/s2b_inference_platform.json')
    checker=m.imported('checker_final_audit',R/'verification/check_s2b_inference_platform.py')
    old=types.ModuleType('baseline_checker');old.__file__=str(R/'verification/check_s2b_inference_platform.py')
    exec(compile(m.git('show',m.BASE+':verification/check_s2b_inference_platform.py').decode('utf-8'),old.__file__,'exec'),old.__dict__)
    assert old.FROZEN_CORE_SHA256==checker.FROZEN_CORE_SHA256 and len(checker.DERIVATION_RULES)==7
    deriv=[]
    for upstream,(target,repls) in checker.DERIVATION_RULES.items():
        oldtarget,oldrepls=old.DERIVATION_RULES[upstream];assert target==oldtarget
        added=checker.ROUTE_QUERY_ADDRESS_REPLACEMENTS if target=='src/s2b_route_query.sv' else checker.ROUTE_ENGINE_ADDRESS_REPLACEMENTS if target=='src/s2b_route_engine.sv' else []
        assert repls==oldrepls+added
        text=(R/upstream).read_bytes().decode('utf-8').replace('\r\n','\n')
        for a,b in repls:assert text.count(a)==1;text=text.replace(a,b)
        assert (R/target).read_bytes()==text.encode('utf-8')
        deriv.append({'upstream':upstream,'upstream_raw_sha256':m.digest(R/upstream),'target':target,'target_sha256':m.digest(R/target),'replacements':len(repls),'s7_added':len(added)})
    m.RESULT['derivation_chain']={'modules':deriv,'original14_raw_exact':True,'static31_exact':True,'stages':['S1几何常量','S2同沿坐标carry','S3 ROUTE 1/2组','S4单batch CONV','S5 patch容量','S6长度/reduction','S7 ROUTE地址守卫'],
        'policy':'全部从固定原14经唯一精确替换得到；除query/engine追加允许替换外原S1..S6规则原样保留'}
    classes=collections.Counter();details={}
    for p,h in freeze['source_sha256'].items():
        try:blob=m.git('show',m.BASE+':'+p)
        except Exception:
            assert p=='verification/test_s2b_route_address_guard_rtl.py';c='NEW_SOURCE'
        else:
            raw=(R/p).read_bytes()
            if p in freeze['changed_paths']:c='AUTHORIZED_MODIFICATION'
            elif raw==blob:c='RAW'
            else:assert raw.replace(b'\r\n',b'\n')==blob;c='EXACT_CRLF_TO_LF'
        classes[c]+=1;details[p]=c
    assert dict(classes)=={'EXACT_CRLF_TO_LF':6,'RAW':23,'AUTHORIZED_MODIFICATION':9,'NEW_SOURCE':1}
    m.RESULT['git_source_classes']={'counts':dict(classes),'files':details,'raw_snapshot_eol_transformations':0}
    r3=R/'report/evidence/S2B-T17/route_address_guard_20261011_r03'
    diag=m.read(r3/'preparation_diagnostics.json');cap=m.read(r3/'pack_native_capture.json')
    assert cap['native_exit_code']==1 and all(x['native_exit_code'] is None and x['tool_exit_code']==1 for x in diag['observations'])
    assert 'lint_forbidden_backend' in (r3/'pack_native_stdout.log').read_text(encoding='utf-8')
    assert (m.FORMAL/'failed_pack_delivery_r03.py').read_bytes()==(R/'tmp/2B/S2B-T17/route_address_guard_20261011_r03/pack_delivery.py').read_bytes()
    assert 'assert not read(EVIDENCE/"source_integrity.json")["lint_forbidden_backend"]' in (m.FORMAL/'failed_pack_delivery_r03.py').read_text(encoding='utf-8')
    finaltmp=R/'tmp/2B/S2B-T17/route_address_guard_20261011_r04/final_receipt.json'
    assert m.digest(finaltmp).startswith('67a1556')
    fin=m.read(finaltmp);assert [x['native_exit_code'] for x in fin['records']]==[0,2]
    m.RESULT['preserved_failures']={'r03_pack_native':cap,'early_native_null_host1':diag['observations'],'g1_final_receipt':raw_json(finaltmp),
        'own_r01_native':m.read(W/'review_native_capture.json'),'own_r01_failure':m.read(W/'independent_rtl_receipt.json')['traceback'],
        'own_r01_cause':'独审脚本把Git LF与工作树RAW错误要求完全相同；修改为仅Git比较可用精确CRLF到LF，工作树/冻结快照始终RAW完全匹配。没有编译、没有生产设计失败。',
        'own_r02_native':m.read(W/'review_r02_native_capture.json'),'all_previous_failures_kept':True}
    m.RESULT['limits']=['有限向量不穷举全部二态组合；全域结论依赖独立无界整数蕴含证明和结构核查。','未证明四态X/Z语义。',
        'G1两次编译/长回归原件只绑定，未本轮复跑15层或不变CONV layer0；owner覆盖来自已核G1真实backend。',
        '采样RSS是约50ms进程树采样下界；全Agent/宿主系统峰值和所有工具调用数未知。',
        'profile0.1.7物理候选0.1.1未冻结、visibility0、50MHz；新STA/bit/BOARD/G3/G4/G5未执行，inputs2保持失败。',
        '只写独立tmp目录，无生产源码/STATE/Git/既有报告写入，无提交，无设备/ROSS操作。']

def seal():
    """在全部写入停下后枚举必要原件，不包含缓存/可执行文件或自引用。"""
    freeze=m.read(m.FORMAL/'source_freeze.json')
    assert {p:m.digest(R/p) for p in freeze['source_sha256']}==freeze['source_sha256']
    manifest=m.FORMAL/'delivery_manifest_r03.json'
    assert m.digest(manifest)==m.RESULT['reviewed_manifest_sha256']
    m.RESULT['status']='PASS_G2_ONLY';m.RESULT['stop']=True;m.RESULT['findings']=[]
    m.RESULT['reviewed_manifest']=manifest.relative_to(R).as_posix()
    m.RESULT['reviewed_source_freeze_sha256']=m.digest(m.FORMAL/'source_freeze.json')
    m.RESULT['independent_proof']=raw_json(W/'independent_math_proof.md')
    m.RESULT['source_sha256_after_seal']={p:m.digest(R/p) for p in freeze['source_sha256']}
    m.save('receipt.json',m.RESULT)
    files=[];sizes={}
    excluded={'obj_dir','checker_fixture','__pycache__'}
    for p in sorted(W.rglob('*')):
        if not p.is_file() or any(x in excluded for x in p.relative_to(W).parts) or p.name=='raw_manifest.json':continue
        assert p.suffix.lower() not in ('.exe','.dll','.o','.a','.pyc')
        role='source' if p.suffix in ('.py','.sv') else 'log' if p.suffix=='.log' else 'input' if p.suffix=='.dat' else 'report'
        rel=p.relative_to(R).as_posix();files.append({'path':rel,'sha256':m.digest(p),'role':role});sizes[rel]=p.stat().st_size
    for p in [manifest,m.FORMAL/'source_freeze.json',m.FORMAL/'source_diff.patch',R/'tmp/2B/S2B-T17/route_address_guard_20261011_r04/final_receipt.json']:
        rel=p.relative_to(R).as_posix();files.append({'path':rel,'sha256':m.digest(p),'role':'input'});sizes[rel]=p.stat().st_size
    assert len(files)==len({x['path'] for x in files}) and any(x['path'].endswith('/receipt.json') for x in files)
    raw={'status':'PASS_G2_ONLY','reviewed_source_commit':m.BASE,'reviewed_manifest_sha256':m.RESULT['reviewed_manifest_sha256'],
         'files':files,'file_bytes':sizes,'file_count':len(files),'total_bytes':sum(sizes.values()),'self_reference':False,
         'exclusions':['obj_dir构建缓存/EXE','checker_fixture可重建篡改缓存；七个独立metadata及原因JSON已保留','__pycache__'],
         'reference_scope':'只绑定本轮实际读取的固定入口；G1大报告/SDK/历史构建物不复制，136项闭包已逐字重算hash。'}
    m.save('raw_manifest.json',raw)
    assert all(m.digest(R/x['path'])==x['sha256'] for x in files)
    print(json.dumps({'status':'PASS_G2_ONLY','receipt_sha256':m.digest(W/'receipt.json'),'raw_manifest_sha256':m.digest(W/'raw_manifest.json'),'raw_files':len(files),'raw_bytes':sum(sizes.values()),'STOP':True},ensure_ascii=False),flush=True)

if __name__=='__main__':
    try:
        if '--audit-only' in sys.argv:
            audit_g1();audit_failures_and_chain()
            m.native('static_checker',[sys.executable,'-B','verification/check_s2b_inference_platform.py'])
            m.native('diff_check',['git','-c','core.longpaths=true','diff','--check','--',*m.read(m.FORMAL/'source_freeze.json')['changed_paths']])
            m.native('evidence_checker',[sys.executable,'-B','verification/check_stage_delivery.py','--mode','evidence','--manifest','report/evidence/S2B-T17/route_address_guard_20261011_r04/delivery_manifest_r03.json'])
            m.native('inputs_checker',[sys.executable,'-B','verification/check_stage_delivery.py','--mode','inputs','--manifest','report/evidence/S2B-T17/route_address_guard_20261011_r04/delivery_manifest_r03.json'],expect=2)
            m.save('audit_completed.json',m.RESULT)
            print('AUDIT_COMPLETE_NATIVE_ZERO',flush=True)
        else:
            command=[sys.executable,'-B','-X','utf8',str(Path(__file__).resolve()),'--audit-only']
            began=time.monotonic()
            with (W/'audit_stdout.log').open('xb') as stream:
                child=subprocess.run(command,cwd=R,stdout=stream,stderr=subprocess.STDOUT)
            rec={'command':command,'native_exit_code':child.returncode,'seconds':round(time.monotonic()-began,3),'peak_tree_rss_bytes':None}
            m.save('audit_native_capture.json',rec)
            assert child.returncode==0,rec
            m.RESULT=m.read(W/'audit_completed.json');m.RESULT['audit_native_capture']=rec
            seal()
    except Exception as exc:
        m.RESULT['status']='CHANGES_REQUIRED';m.RESULT['failure']=repr(exc);m.RESULT['traceback']=traceback.format_exc()
        m.save('audit_failure_receipt.json',m.RESULT);print(m.RESULT['traceback'],flush=True);raise SystemExit(2)
