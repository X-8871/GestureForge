import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition')
OUT = Path(__file__).resolve().parent
PKG = ROOT / 'report/evidence/S2B-T17/s15_postroute_20261012_r01'
SYN = ROOT / 'report/evidence/S2B-T17/s15_platform_20261012_r01'
HEAD = '926c2fd382069e68e6c5ec533b7d3b6a87fbb363'
MANIFEST_SHA = '4f7456caead3fd099db0c939953073641c46ee1d2c556e47f3f923a47779a9ff'
errors = []
checks = []
bindings = []
facts = {}

def ck(ok, name, detail=None):
    checks.append({'name': name, 'pass': bool(ok), 'detail': detail})
    if not ok:
        errors.append({'name': name, 'detail': detail})

def sha(data):
    return hashlib.sha256(data).hexdigest()

def raw(path):
    assert path.is_file(), str(path)
    return path.read_bytes()

def js(path):
    return json.loads(raw(path).decode('utf-8'))

def txt(path):
    return raw(path).decode('utf-8')

def save_input(path):
    data = raw(path)
    rel = path.relative_to(ROOT)
    target = OUT / 'inputs' / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_bytes(data)
    assert raw(target) == data
    bindings.append({'source': str(path), 'saved': str(target.relative_to(OUT)), 'sha256': sha(data), 'bytes': len(data)})

def payload(path):
    d = js(path)
    d = d.get('result', d)
    texts = [x['text'] for x in d.get('content',[]) if x.get('type') == 'text']
    assert len(texts) == 1
    return json.loads(texts[0])

def native(command, label):
    folder = OUT / 'commands'
    folder.mkdir(exist_ok=True)
    with (folder/(label+'.stdout.bin')).open('xb') as so, (folder/(label+'.stderr.bin')).open('xb') as se:
        p = subprocess.Popen(command, cwd=ROOT, stdout=so, stderr=se)
        rc = p.wait()
    data = raw(folder/(label+'.stdout.bin'))
    rec = {'command': command, 'native_child_wait': rc, 'direct_wait': True, 'pid': p.pid, 'stdout_sha256': sha(data), 'stderr_sha256': sha(raw(folder/(label+'.stderr.bin')))}
    (folder/(label+'.native.json')).write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    ck(rc == 0, 'native '+label, rec)
    return data

try:
    mp = PKG/'delivery_manifest_r03.json'
    ck(sha(raw(mp)) == MANIFEST_SHA,'固定r03清单SHA')
    m = js(mp)
    ck(len(m['files']) == 637 and m['source_commit'] == HEAD,'637绑定及SOURCE')
    filechecks = []
    for row in m['files'] + m['interfaces']:
        path = ROOT/row['path']
        data = raw(path)
        good = sha(data) == row['sha256'] and ('bytes' not in row or len(data)==row['bytes'])
        ck(good,'清单绑定 '+row['path'])
        filechecks.append({'path':row['path'],'sha256':sha(data),'bytes':len(data),'pass':good})
    facts['manifest_files'] = filechecks
    package_cmd = [sys.executable,'-X','utf8','-B',str(ROOT/'verification/check_stage_delivery.py'),'--mode','evidence','--manifest',str(mp)]
    packaging = native(package_cmd,'packaging_r03')
    ck(b'CHECKS_OK' in packaging,'独立包装CHECKS_OK')
    save_input(ROOT/'verification/check_stage_delivery.py')
    save_input(mp)
    for rel in ['pnr_sta_result.json','pnr_closed_binding.json','pnr_original_file_map.json','timing_summary_pnr.rpt','timing_worst_pnr.rpt','utilization_pnr.rpt','utilization_flat_pnr.rpt','clocks_pnr.rpt','exceptions_pnr.rpt','constraints_pnr.xdc','methodology_pnr.rpt','drc_pnr.rpt','route_status_pnr.rpt']:
        save_input(PKG/rel)
    freeze = js(PKG/'native_capture_closed/source_freeze_r01.json')
    ck(freeze['source_commit']==HEAD and freeze['profile']=='s2b-inference-platform/0.1.15' and freeze['tcl_builder_namespace_version']=='0.1.12','冻结profile15/namespace12')
    ck(len(freeze['source_files'])==46 and len(freeze['active_rtl_sources'])==18 and len(freeze['frozen14'])==14 and len(freeze['static_source_sha256'])==33,'46源码18RTL14原件33static')
    save_input(PKG/'native_capture_closed/source_freeze_r01.json')
    gd = ['C:\\Program Files\\Git\\cmd\\git.exe','-c','core.longpaths=true','-c','maintenance.auto=false','-C',str(ROOT)]
    ck(native(gd+['rev-parse','HEAD'],'git_00').decode().strip()==HEAD,'当前HEAD固定')
    source_rows = []
    prior = {}
    for phase in ['before','after']:
        folder = PKG/'source_checks'/phase
        d = js(folder/'source_after.json')
        mapping = {x['original']['path']:x['saved'] for x in js(folder/'archive_mapping.json')['files']}
        for x in js(folder/'archive_mapping.json')['files']:
            ck(x['original']['sha256']==x['saved']['sha256'] and x['original']['bytes']==x['saved']['bytes'] and sha(raw(ROOT/x['saved']['path']))==x['saved']['sha256'],'源码归档映射 '+phase+' '+x['saved']['path'])
        ck(len(d['source_files'])==46 and d['actual_head_at_check']==HEAD and d['actual_head_after_check']==HEAD,'before/after SOURCE '+phase)
        commands = js(folder/'git_commands.json')['commands']
        ck(len(commands)==48 and all(x['native_exit_code']==0 for x in commands),'原48git native0 '+phase)
        for i,c in enumerate(commands):
            archived = js(folder/'git_native'/('git_%02d.native.json'%i))
            ck(archived['command']==c['command'] and archived['native_exit_code']==0,'原Git argv/rc '+phase+str(i))
            for stream in ['stdout','stderr']:
                b=raw(folder/'git_native'/('git_%02d.%s.log'%(i,stream)))
                ck(sha(b)==c[stream]['sha256'] and len(b)==c[stream]['bytes'],'原Git流绑定 '+phase+str(i)+stream)
        save_input(folder/'source_after.json')
        save_input(folder/'archive_mapping.json')
        save_input(folder/'git_commands.json')
        for i,row in enumerate(d['source_files']):
            b=raw(ROOT/mapping[row['snapshot']]['path'])
            ck(sha(b)==row['sha256'] and len(b)==row['bytes'] and b==raw(ROOT/row['path']),'源码before/after/actual '+phase+' '+row['path'])
            gb=raw(folder/'git_native'/('git_%02d.stdout.log'%(i+1)))
            relation = 'RAW_IDENTICAL' if gb==b else ('GIT_LF_TO_RAW_CRLF' if b'\r\n' not in gb and gb.replace(b'\n',b'\r\n')==b else 'INVALID')
            ck(relation!='INVALID' and relation==row['git_relation'] and sha(gb)==row['git_blob_sha256'],'原Git精确关系 '+phase+' '+row['path'])
            if phase=='before':
                actual_git=native(gd+['show',HEAD+':'+row['path']],'git_%02d'%(i+1))
                ck(actual_git==gb,'独立Git blob '+row['path'])
                prior[row['path']]=b
                source_rows.append({'path':row['path'],'sha256':sha(b),'bytes':len(b),'git_relation':relation,'git_blob_sha256':sha(gb)})
            else:
                ck(prior[row['path']]==b,'前后逐字节 '+row['path'])
    ck(native(gd+['rev-parse','HEAD'],'git_47').decode().strip()==HEAD,'核查结束HEAD固定')
    for path,h in freeze['static_source_sha256'].items():
        ck(sha(raw(ROOT/path))==h,'33static '+path)
    for path,h in freeze['frozen14'].items():
        ck(sha(raw(ROOT/path))==h,'14原RTL '+path)
    facts['source_rows']=source_rows
    facts['git_relations']=dict(Counter(x['git_relation'] for x in source_rows))
    synth_manifest=SYN/'s15_root_delivery_manifest_r03.json'
    synth_receipt=ROOT/'report/evidence/S2B-T17/s15_root_closure_20261012_r01/synth_sta_review_r01/final_stop_receipt.json'
    ck(sha(raw(synth_manifest))=='02e5d0d6da4ac331e0c0686d710c58d27944fe60dcd8b474296cbb6a31e88824','固定综合manifest')
    ck(sha(raw(synth_receipt))=='5568193452ba8b33b719420fb7175a22fe78d40e010cae8409e6070018a3714e','固定综合G2receipt')
    save_input(synth_manifest)
    save_input(synth_receipt)
    for key in ['functional_g2','tool_g2']:
        row=freeze[key]
        ck(sha(raw(ROOT/row['path']))==row['sha256'],'冻结依赖 '+key)
        save_input(ROOT/row['path'])
    constraints=lambda s:[x.strip() for x in s.splitlines() if x.strip() and not x.strip().startswith('#')]
    xdc=constraints(txt(PKG/'constraints_pnr.xdc'))
    old=constraints(txt(SYN/'constraints_synth.xdc'))
    ck(xdc==old,'综合至PNR全部实际时序约束无变化',xdc)
    ck(sum(x.startswith('set_false_path') for x in xdc)==2 and not any('multicycle' in x or 'set_max_delay' in x or 'set_clock_groups' in x for x in xdc),'仅已有两reset falsepath无额外放宽')
    ck(any('create_clock -period 20.000' in x for x in xdc) and any('set_input_jitter clk_fpga_0 0.600'==x for x in xdc),'20ns及0.6jitter')
    save_input(SYN/'constraints_synth.xdc')
    timing=txt(PKG/'timing_summary_pnr.rpt')
    nums=re.search(r'\n\s*(0\.007)\s+(0\.000)\s+(0)\s+(15425)\s+(0\.087)\s+(0\.000)\s+(0)\s+(15425)\s+(8\.870)\s+(0\.000)\s+(0)\s+(4534)\s*\n',timing)
    ck(nums is not None and 'Physopt postRoute' in timing and '-2  PRODUCTION' in timing,'独立setup/hold/pulse数值及postRoute -2')
    ct=dict((k,int(v)) for k,v in re.findall(r'\d+\. checking (\w+) \((\d+)\)',timing))
    ck(len(ct)==12 and set(ct.values())=={0},'全部12 check_timing零',ct)
    ck('clk_fpga_0  {0.000 10.000}     20.000          50.000' in timing,'实际50MHz钟波形')
    worst=txt(PKG/'timing_worst_pnr.rpt')
    paths=[]
    for block in re.split(r'(?=Slack \()',worst)[1:]:
        slack=float(re.search(r'Slack \(MET\)\s*:\s*([\d.]+)ns',block)[1])
        source=re.search(r'Source:\s*(\S+)',block)[1]
        dest=re.search(r'Destination:\s*(\S+)',block)[1]
        delay=float(re.search(r'Data Path Delay:\s*([\d.]+)ns',block)[1])
        req=float(re.search(r'Requirement:\s*([\d.]+)ns',block)[1])
        paths.append({'slack_ns':slack,'source':source,'destination':dest,'data_path_delay_ns':delay,'requirement_ns':req})
    ck(len(paths)==30 and min(x['slack_ns'] for x in paths)==0.007 and all(x['requirement_ns']==20 for x in paths),'独立30真实worst paths',paths[:3])
    facts['worst_paths']=paths
    route=txt(PKG/'route_status_pnr.rpt')
    ck(re.search(r'routable nets\.+\s*:\s*33918',route) is not None and re.search(r'fully routed nets\.+\s*:\s*33918',route) is not None and re.search(r'nets with routing errors\.+\s*:\s*0',route) is not None,'33918全部布线且零failed nets')
    methodology=txt(PKG/'methodology_pnr.rpt')
    ck('Checks found: 0' in methodology and 'Fully Routed' in methodology,'standalone methodology零')
    drc=txt(PKG/'drc_pnr.rpt')
    dcounts=Counter(re.findall(r'^(DPIP-1|DPOP-1|DPOP-2)#\d+ Warning',drc,re.M))
    ck(dcounts=={'DPIP-1':113,'DPOP-1':142,'DPOP-2':140} and 'Checks found: 395' in drc,'395真实DSP warning保留',dict(dcounts))
    util=txt(PKG/'utilization_flat_pnr.rpt')
    resources={}
    for k,want in [('Slice LUTs',19891),('Slice Registers',4371),('Register as Latch',0),('Block RAM Tile',32),('DSPs',143)]:
        matches=re.findall(r'\|\s*'+re.escape(k)+r'\s*\|\s*(\d+)\s*\|',util)
        ck(matches and all(int(x)==want for x in matches),'资源 '+k,matches)
        resources[k]=want
    facts['resources']=resources
    hist=payload(PKG/'raw_root/history_full.tool.json')['history']
    ck(len(hist)==8 and all(x['code']==0 for x in hist),'8真实MCP命令native0')
    expected=['open_project','set_param','launch_runs','wait_on_run','open_run','report_timing_summary','write_xdc','close_project']
    ck([x['command'].split()[0] for x in hist]==expected,'MCP八命令完整顺序')
    ck(hist[2]['command']=='launch_runs impl_1 -to_step {phys_opt_design (Post-Route)} -jobs 1' and hist[3]['command']=='wait_on_run impl_1' and hist[3]['elapsed']==1274.19,'唯一PNR launch/jobs1/nativewait0')
    facts['history']=[{k:v for k,v in x.items() if k!='output'} for x in hist]
    for label,i in [('open_project',0),('setup',1),('launch',2),('open_run',4),('reports',5),('query_xdc',6),('close',7)]:
        d=payload(PKG/'raw_root'/(label+'.tool.json'))
        ck(d['exit_code']==hist[i]['code'] and d['output']==hist[i]['output'] and js(PKG/'raw_root'/(label+'.tool.json'))['input']['command']==hist[i]['command'],'MCP history对照 '+label)
        save_input(PKG/'raw_root'/(label+'.tool.json'))
    ck('impl_1 {status {phys_opt_design (Post-Route) Complete!} progress 100%}' in hist[6]['output'] and 'threads 1 post_physopt 1' in hist[6]['output'],'实际run终态及线程')
    waittxt=txt(PKG/'raw_root/wait.tool.json')
    ck('timed out awaiting tools/call after 300s' in waittxt,'客户300s超时保留')
    ck(payload(PKG/'raw_root/stop.tool.json')['status']=='success','ROSS stop.success原件')
    for rel in ['raw_root/history_full.tool.json','raw_root/wait.tool.json','raw_root/stop.tool.json','raw_root/actual_run_count.json','raw_root/closed_runtime_observation.json','raw_root/r02_terminal_receipt.json','native_capture_closed/prepared_receipt_r04.json','raw_root/prepare_pnr.native.json','raw_root/pnr_classifier_r01.native.json']:
        save_input(PKG/rel)
    job=txt(PKG/'native_jobs/runme.log')
    ck('impl_1 finished' in hist[3]['output'] and 'phys_opt_design completed successfully' in job and 'postroute_physopt.dcp' in job and 'Exiting Vivado at Mon Oct 12 15:10:27 2026' in job,'实际run日志与checkpoint闭合')
    ck(not list((PKG/'native_jobs').glob('*.error.rst')),'无native error marker')
    for step in ['init_design','opt_design','place_design','phys_opt_design','route_design','post_route_phys_opt_design','vivado']:
        ck((PKG/'native_jobs'/('.'+step+'.end.rst')).is_file(),'真实完成marker '+step)
        save_input(PKG/'native_jobs'/('.'+step+'.end.rst'))
    for rel in ['native_jobs/runme.log','native_jobs/s2b_inference_wrapper.tcl','native_jobs/vivado.jou','native_jobs/s2b_inference_wrapper_timing_summary_postroute_physopted.rpt']:
        save_input(PKG/rel)
    facts['tool_reported_single_process_peak_mb']=max(float(x) for x in re.findall(r'Memory \(MB\): peak =\s*([\d.]+)',job))
    observed=js(PKG/'raw_root/closed_runtime_observation.json')
    ck(len(observed['known_identity_observations'])==14 and all(x['status']=='ABSENT' for x in observed['known_identity_observations']) and observed['root_observation']['status']=='ABSENT','14已知旧身份ABSENT')
    ck(observed['implementation_worker_os_exit_code'] is None and observed['entire_os_tree_terminal']=='NOT_PROVEN_BY_DISCRETE_KNOWN_IDENTITY_ENUMERATION','未伪造完整OS树及worker native')
    monitor=[]
    for r in [1,2]:
        folder=PKG/'raw_root'/('supervision_r%02d'%r)
        samples=[json.loads(x) for x in txt(folder/'guard/samples.jsonl').splitlines()]
        guard=js(folder/'guard/guard_receipt.json')
        sup=js(folder/'supervisor_receipt.json')
        consumer=js(PKG/'raw_root'/('native_consumer_r%02d'%r)/'consumer_receipt.json')
        ck(len(samples)==(92 if r==1 else 647) and guard['status']=='BLOCKED' and consumer['status']=='BLOCKED_RUNTIME_MONITOR','监护真实BLOCKED r'+str(r))
        monitor.append({'round':r,'sample_count':len(samples),'first':samples[0],'last':samples[-1],'guard':guard,'supervisor':sup,'consumer':consumer})
        for rel in ['guard/samples.jsonl','guard/events.jsonl','guard/guard_receipt.json','supervision.jsonl','supervisor_receipt.json']:
            save_input(folder/rel)
        save_input(PKG/'raw_root'/('native_consumer_r%02d'%r)/'consumer_receipt.json')
    facts['monitor_originals']=monitor
    for phase,label,unknown in [('before','source_before_pnr',28),('after','source_after_pnr_r02',37)]:
        extension='stdout.bin' if phase=='before' else 'stdout.log'
        capture=js(PKG/'raw_root'/(label+'.'+extension))
        ck(capture['native_exit_code']==0 and capture['wrapper_exit_code']==2 and capture['unknown_count']==unknown and capture['direct_child_wait_returned'],'SOURCE真实child0/wrapper2/UNKNOWN '+phase)
        save_input(PKG/'raw_root'/(label+'.'+extension))
        save_input(PKG/'raw_root'/(label+'.native.json'))
    for r in [1,2]:
        n=js(PKG/'packaging_history'/('pnr_packaging_check_r%02d.native.json'%r))
        ck(n['native_exit_code']==2,'真实历史包装失败2 r'+str(r))
        for stream in ['native.json','stdout.log','stderr.log']:
            save_input(PKG/'packaging_history'/('pnr_packaging_check_r%02d.'%r+stream))
    rootcheck=ROOT/'tmp/2B/S2B-T17/s15_postroute_root_20261012_r01/pnr_packaging_check_r03.native.json'
    ck(js(rootcheck)['native_exit_code']==0 and js(rootcheck)['direct_wait'],'ROOT真实r03包装0')
    save_input(rootcheck)
    for stream in ['stdout.log','stderr.log']:
        save_input(rootcheck.with_name('pnr_packaging_check_r03.'+stream))
except Exception as exc:
    errors.append({'name':'审查驱动异常','detail':repr(exc)})
    import traceback
    traceback.print_exc()
result={'status':'MACHINE_CHECKS_PASS_PNR_STA_SCOPE' if not errors else 'MACHINE_CHECKS_FAILED','checks':checks,'errors':errors,'facts':facts,'input_bindings':bindings,'continuous_budget':'NOT_PROVEN','bit_runtime_G3_G4_G5':'NOT_PASSED','time_utc8':datetime.now(timezone(timedelta(hours=8))).isoformat()}
(OUT/'audit_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'checks':len(checks),'errors':errors,'git_relations':facts.get('git_relations'),'resources':facts.get('resources')},ensure_ascii=False))
raise SystemExit(0 if not errors else 2)
