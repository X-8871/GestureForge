import hashlib
import json
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
import psutil

# 本脚本仅读取当前冻结包与固定Git对象，轻量检查输出只写独立目录。
ROOT=Path.cwd().resolve()
OUT=Path(__file__).absolute().parent/(sys.argv[1] if len(sys.argv)>1 else '')
E=ROOT/'report/evidence/S2B-T17/s11_platform_20261012_r01'
COMMIT='a710ec431474841a81912a6055f861e811a151e3'
MSHA='723cd835363a44d7aa9c7f27897204bf36f04e2d545ee1a463d6c998664dc98b'
seen={}; checks=[]; commands=[]; enc=[]; started=time.monotonic()
peak_sample=0

def raw(path,role='input',record=True):
    global peak_sample
    p=Path(path)
    if not p.is_absolute(): p=ROOT/p
    assert p.is_file() and not p.is_symlink(),str(p)
    data=p.read_bytes()
    if record:
        k=p.relative_to(ROOT).as_posix()
        seen[k]={'path':k,'sha256':hashlib.sha256(data).hexdigest(),'role':role}
    peak_sample=max(peak_sample,psutil.Process().memory_info().rss)
    assert peak_sample<=134217728,peak_sample
    return data

def obj(p): return json.loads(raw(p).decode('utf-8','strict'))
def text(p,role='log'):
    b=raw(p,role)
    try:return b.decode('utf-8','strict')
    except UnicodeDecodeError:
        enc.append({'path':str(p),'inspection':'LATIN1_ASCII_BYTE_PRESERVING_ONLY','original_bytes_preserved':True})
        return b.decode('latin1')
def check(name,condition,evidence=''):
    checks.append({'name':name,'status':'PASS' if condition else 'FAIL','evidence':evidence})
def save(n,j):
    with (OUT/n).open('x',encoding='utf-8',newline='\n') as f: json.dump(j,f,ensure_ascii=False,indent=2);f.write('\n')
def verify(row,key='path',record=False):
    b=raw(row[key],record=record)
    return hashlib.sha256(b).hexdigest()==row['sha256'] and ('bytes' not in row or len(b)==row['bytes'])
def unwrap(j):
    if j.get('status')=='fulfilled':j=j['value']
    return j.get('result',j)
def mcp(j):return json.loads(next(x['text'] for x in unwrap(j)['content'] if x['type']=='text'))
def run(label,args):
    t=time.monotonic();p=subprocess.run(args,cwd=ROOT,capture_output=True,check=False)
    for s,b in [('stdout.log',p.stdout),('stderr.log',p.stderr)]:
        with (OUT/(label+'.'+s)).open('xb') as f:f.write(b)
    r={'command':args,'native_exit_code':p.returncode,'elapsed_seconds':time.monotonic()-t}
    save(label+'.native.json',r);commands.append(r)
    return p

manifest=obj(E/'s11_delivery_manifest_r05.json')
check('固定主入口/752绑定',hashlib.sha256(raw(E/'s11_delivery_manifest_r05.json')).hexdigest()==MSHA and manifest['source_commit']==COMMIT and len(manifest['files'])==752)
check('752实际SHA/严格字段',all(set(x)=={'path','sha256','role'} and verify(x) for x in manifest['files']))
helper=ROOT/'tmp/2B/S2B-T17/s11_collection_actual_finalize_20261012_r01'
h=obj(helper/'final_collection_receipt.json')
check('helper固定receipt/raw760',hashlib.sha256(raw(helper/'final_collection_receipt.json')).hexdigest()=='c07f5cff0c69052fd33dd026b824e5cca1810429d25062124c3817523051c220' and hashlib.sha256(raw(helper/'raw_manifest.jsonl')).hexdigest()=='873fcd693c7022974af7f4f7e1f5d17840f0ca77898fec93f5ae0eadeb18ca26')
hr=[json.loads(x) for x in text(helper/'raw_manifest.jsonl').splitlines()]
check('helper760可恢复原件',len(hr)==760 and all(set(x)=={'path','sha256','role'} and verify(x) for x in hr))
source=obj(E/'s11_source_binding.json'); before=obj(source['before']['path']); after=obj(source['after']['path'])
check('前后43/33/SHA一致',verify(source['before'],record=True) and verify(source['after'],record=True) and before['source_commit']==after['source_commit']==COMMIT and before['source_count']==after['source_count']==43 and before['platform_static_source_count']==after['platform_static_source_count']==33 and before['source_sha256']==after['source_sha256'])
bm={x['path']:x for x in before['source_files']}; am={x['path']:x for x in after['source_files']}; counts={'RAW_IDENTICAL':0,'GIT_LF_TO_RAW_CRLF':0}; gr=[]
for path,row in bm.items():
    snap=raw(row['snapshot'],'source');later=raw(am[path]['snapshot'],'source');current=raw(path,'source')
    argv=['git','show',COMMIT+':'+path];cp=subprocess.run(argv,cwd=ROOT,capture_output=True)
    relation='RAW_IDENTICAL' if cp.stdout==snap else 'GIT_LF_TO_RAW_CRLF';counts[relation]+=1
    check('固定Git/当前/快照：'+path,cp.returncode==0 and snap==current==later and hashlib.sha256(snap).hexdigest()==row['sha256']==am[path]['sha256'] and hashlib.sha256(cp.stdout).hexdigest()==row['git_blob_sha256'] and (cp.stdout==snap or (b'\r\n' not in cp.stdout and cp.stdout.replace(b'\n',b'\r\n')==snap)) and relation==row['git_relation'],relation)
    gr.append({'command':argv,'native_exit_code':cp.returncode,'stdout_sha256':hashlib.sha256(cp.stdout).hexdigest(),'stderr':cp.stderr.decode('utf-8','replace')})
save('source_git.native.json',gr)
check('37RAW/6EOL/原14',counts=={'RAW_IDENTICAL':37,'GIT_LF_TO_RAW_CRLF':6} and len(source['frozen14'])==14 and all(bm[k]['sha256']==v for k,v in source['frozen14'].items()))
freeze=obj(source['freeze']['path'])
check('已审G1冻结入口SHA',verify(source['freeze'],record=True),source['freeze'])
summary=obj(E/'s11_collection_summary.json');mapping=obj(E/'s11_native_mapping.json')
check('闭合原库存不变',all(verify(x) for x in summary['original_raw_inventory']) and all(verify(x,'original_path') and verify(x,'saved_path') for x in summary['closed_input_mapping']))
drift=[]
for row in mapping['files']:
    if not verify(row,'original_path'):
        drift.append({'path':row['original_path'],'frozen_sha256':row['sha256'],'current_sha256':hashlib.sha256(raw(row['original_path'],record=False)).hexdigest(),'recovery_path':row['saved_path']})
save('temporary_native_origin_drift.json',drift)
check('真实native5jobs冻结副本',len(mapping['jobs'])==5 and all(verify(x,'saved_path') for x in mapping['files']),len(mapping['files']))
check('原址漂移仅5个临时gen_run.xml/保存原件仍同SHA',len(drift)==5 and all(x['path'].endswith('/gen_run.xml') for x in drift),drift)
for job in mapping['jobs']:
    rows=[x for x in mapping['files'] if x['saved_path'].endswith('.vds') and '/'+job['run']+'/' in x['original_path']]
    assert len(rows)==1
    log=text(rows[0]['saved_path']);d=(ROOT/rows[0]['saved_path']).parent
    elapsed=re.findall(r'synth_design:.*?elapsed = (\d+:\d+:\d+)',log)[-1]
    seconds=sum(int(v)*m for v,m in zip(elapsed.split(':'),(3600,60,1)))
    peak=max(map(float,re.findall(r'peak = ([0-9.]+)',log)))
    check('完成/marker/线程/未知OS码：'+job['run'],'synth_design completed successfully' in log and '0 Critical Warnings and 0 Errors encountered' in log and 'maximum of 1 processes' in log and (d/'__synthesis_is_complete__').is_file() and (d/'.vivado.end.rst').is_file() and job['raw_os_process_exit_code'] is None and seconds==job['synth_elapsed_seconds'] and peak==job['reported_single_process_peak_mb'],{'elapsed':seconds,'single_process_peak_mb':peak,'raw_os_code':None})
infer=text(E/'native_jobs/s2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl','source')
block=re.search(r'read_verilog -library xil_defaultlib -sv \{([^}]+)\}',infer)[1]
rtl=[Path(x.strip()).relative_to(ROOT).as_posix() for x in block.splitlines() if x.strip()]
setup=text(E/'setup_synthesis.tcldict','diagnostic')
check('真实compiled18/profile/visibility/clock',len(set(rtl))==18 and set(rtl)==set(source['compiled_rtl']) and 'profile 0.1.11 visibility 0 clock_hz 50000000' in setup and 'threads 1 jobs 1' in setup,rtl)
xpr=ET.fromstring(raw(ROOT/'tmp/2B/S2B-T17/s11p1/s2b_inference_candidate.xpr','artifact'))
paths=[x.attrib['Path'] for x in xpr.findall(".//FileSets/FileSet[@Name='sources_1']/File")]
check('XPR唯一wrapper/-2',len([p for p in paths if p.endswith('/s2b_inference_wrapper.v')])==1 and all(x.attrib['Val']=='xc7z020clg400-2' for x in xpr.findall(".//Option[@Name='Part']")))
binding=obj(E/'s11_mcp_binding.json');gate=obj(summary['root_gate']['path']);history=mcp(obj(gate['mcp_history']['path']))['history']
check('九真实history/单次launch/products',len(history)==9 and [x['label'] for x in binding['paired_calls']]==['source','builder','setup','launch','wait','open_run','reports','query_xdc','close'] and all(x==p['native_history'] for x,p in zip(history,binding['paired_calls'])) and sum(x['command']=='launch_runs synth_1 -jobs 1' for x in history)==1 and binding['products_repeated'] is False)
for row in binding['paired_calls']:
    actual=obj(row['client_record']['path']); result=unwrap(actual)
    if row['label']=='wait':
        check('nativewait0/569.942与client300s超时分列',row['client_timeout'] is True and row['client_exit_code'] is None and row['native_history']['code']==0 and row['native_history']['elapsed']==569.942 and result['isError'] is True and 'after 300s' in json.dumps(result))
    else:
        check('client/native：'+row['label'],mcp(actual)['exit_code']==row['client_exit_code']==row['native_history']['code'] and row['client_timeout'] is False,row['client_exit_code'])
products=text(E/'products.tcldict','diagnostic')
check('一次products native0/capture1原警告计数','status FAIL code 0 raw PRODUCTS:OK' in products and 'native_counts_before {WARNING 9' in products and 'native_counts_after {WARNING 1' in products and binding['products_native_exit_code']==0 and binding['products_capture_exit_code']==1)
timing=text(E/'timing_summary_synth.rpt');section=timing.split('| Design Timing Summary',1)[1].split('| Clock Summary',1)[0]
rows=[x.split() for x in section.splitlines() if re.fullmatch(r'\s*-?\d+\.\d+(?:\s+-?\d+(?:\.\d+)?){11}\s*',x)]
check('50MHzSTA真实FAIL数值',len(rows)==1 and list(map(float,rows[0]))==[-4.404,-1939.802,787,14873,.037,0,0,14873,8.870,0,0,4151] and 'Timing constraints are not met.' in timing and summary['timing']['status']=='FAIL_TIMING')
check('12项漏约束0/50MHz20ns',all(set(re.findall('checking '+k+r' \((\d+)\)',timing))=={'0'} for k in summary['timing']['check_timing']) and '20.000' in text(E/'clocks_synth.rpt'))
worst=text(E/'timing_worst_synth.rpt').split('Slack (VIOLATED)',2)[1]
check('最差MaxPool24.000ns/21levels',summary['worst_path']['source'] in worst and summary['worst_path']['destination'] in worst and '24.000ns' in worst and '21  (CARRY4=11 DSP48E1=3' in worst and summary['worst_path']['speed_file'].startswith('-2'))
util=text(E/'utilization_flat_synth.rpt')
for label,value in [('Slice LUTs*',18955),('Slice Registers',3987),('Block RAM Tile',32),('DSPs',145),('Register as Latch',0)]:
    match=re.search(r'\|\s*'+re.escape(label)+r'\s*\|\s*(\d+)\s*\|',util);check('资源：'+label,bool(match) and int(match[1])==value,value)
xdc=text(E/'constraints_synth.xdc','source');oldxdc=text(ROOT/'report/evidence/S2B-T17/s7_platform_20261011_r01/constraints_synth.xdc','source')
def actualxdc(s):return [x.strip() for x in s.splitlines() if x.strip() and not x.lstrip().startswith('#')]
check('两原resetCDC例外未扩大',actualxdc(xdc)==actualxdc(oldxdc) and xdc.count('set_false_path')==2 and 'No valid timing exceptions found.' in text(E/'exceptions_synth.rpt'))
check('方法学/DRC未关闭','Large setup violation' in text(E/'methodology_synth.rpt') and 'Warning' in text(E/'drc_synth.rpt'))
xsa=obj(E/'s11_xsa_comparison.json')
check('新旧XSA绑定',verify(xsa['old_xsa'],record=True) and verify(xsa['new_xsa'],record=True))
with zipfile.ZipFile(ROOT/xsa['old_xsa']['path']) as old,zipfile.ZipFile(ROOT/xsa['new_xsa']['path']) as new:
    init=[x['member'] for x in xsa['members'] if x['member'].startswith('ps7_init')]
    check('六PSinit相同/HWH不同/无bit',len(init)==6 and all(old.read(k)==new.read(k)==raw(E/'generated_inputs'/k) for k in init) and old.read('s2b_inference.hwh')!=new.read('s2b_inference.hwh') and not any(x.endswith('.bit') for x in new.namelist()) and xsa['runtime_elf_bsp_compatibility']=='NOT_APPROVED')
index=obj(E/'resource_monitoring/resource_index.json')
check('资源543映射/386复制157复用',len(index['mapping'])==543 and sum(x['mode']=='RAW_COPY' for x in index['mapping'])==386 and sum(x['mode']=='EXISTING_PERMANENT_RAW_SHA_IDENTICAL' for x in index['mapping'])==157 and all(verify(x['original']) and verify(x['saved']) and x['original']['sha256']==x['saved']['sha256'] for x in index['mapping']))
reused=[x['saved']['path'] for x in index['mapping'] if x['mode']=='EXISTING_PERMANENT_RAW_SHA_IDENTICAL']
cp=run('git_formal_reused',['git','ls-tree','-r','--name-only',COMMIT,'--','report/evidence/S2B-T17/s10_platform_20261012_r01/resource_monitoring'])
check('157复用路径在固定Git',cp.returncode==0 and set(reused)<=set(cp.stdout.decode('utf-8').splitlines()))
reused_git=[]
for path in sorted(set(reused)):
    argv=['git','show',COMMIT+':'+path];cp=subprocess.run(argv,cwd=ROOT,capture_output=True)
    good=cp.returncode==0 and hashlib.sha256(cp.stdout).hexdigest()==hashlib.sha256(raw(path,record=False)).hexdigest()
    reused_git.append({'command':argv,'native_exit_code':cp.returncode,'stdout_sha256':hashlib.sha256(cp.stdout).hexdigest(),'match':good})
save('reused_git.native.json',reused_git)
check('S10正式复用固定Git字节一致',all(x['match'] for x in reused_git),len(reused_git))
def resource(suffix):
    found=[x for x in index['mapping'] if x['original']['path'].endswith(suffix)];assert len(found)==1,suffix
    return found[0]['saved']['path']
g1=obj(resource('s11_guard_actual_20261012_r01/guard/guard_receipt.json'));s1=obj(resource('s11_guard_actual_20261012_r01/supervisor_receipt.json'))
samples=[json.loads(x) for x in text(resource('s11_guard_actual_20261012_r01/guard/samples.jsonl')).splitlines()]
check('首轮BLOCKED3/sup2/150/392.546',g1['status']=='BLOCKED' and g1['reason']=='INCOMPLETE_TREE_IDENTITY' and len(samples)==g1['samples']==150 and abs(g1['elapsed_seconds']-392.546)<.001 and s1['child_native_exit_code']==3 and s1['supervisor_exit_code']==2)
check('实际窗口峰5.405GB/min670662656',max(x['tree_rss_bytes'] for x in samples if x['tree_rss_bytes'] is not None)==g1['sampled_peak_tree_rss_bytes']==5405806592 and min(x['available_ram_bytes'] for x in samples)==g1['minimum_sampled_available_ram_bytes']==670662656 and all(x['limits']==index['limits']=={'tree_rss_bytes':6442450944,'available_ram_bytes':536870912,'c_disk_free_bytes':8589934592} for x in samples))
last=json.dumps(samples[-1]);check('36612同样本ABSENT+UNKNOWN/RSSnull',samples[-1]['tree_rss_bytes'] is None and '36612' in last and 'ABSENT' in last and 'UNKNOWN' in last,last)
g2=obj(resource('s11_guard_actual_20261012_r02/guard/guard_receipt.json'));s2=obj(resource('s11_guard_actual_20261012_r02/supervisor_receipt.json'))
check('r02关闭0仅known/旧guard/sup2',g2['status']=='ROOT_EXITED' and s2['child_native_exit_code']==0 and s2['supervisor_exit_code']==2 and index['diagnostic_monitor']['heavy_coverage'] is False and index['diagnostic_monitor']['actual_guard_sha256']=='9cad1ddf5f1b2d48b99c6d10451756536b25c4abf613f0af8b16e0ffd629f86c' and index['race2_used_for_heavy'] is False)
check('全程覆盖BLOCKED/null/集成没执行',index['budget_exit_code'] is None and 'BLOCKED' in index['status'] and any('只消费' in x and '5秒' in x for x in index['limitations']) and any('isError' in x for x in index['limitations']))
for x in manifest['checks']:
    if x['status'] in ['BLOCKED','NOT_RUN']:check('schema空码：'+x['name'],x['exit_code'] is None)
    if x['name'].startswith('包装') and ('r02' in x['name'] or 'r03' in x['name']):check('原包装真实FAIL2：'+x['name'],x['status']=='FAIL' and x['exit_code']==2)
for version in ['r02','r03']:
    n=obj(helper/('pack_evidence_'+version+'.native.json'));log=text(helper/('pack_evidence_'+version+'.stdout.log'))
    check('原checker失败保留：'+version,n.get('native_exit_code',n.get('exit_code'))==2 and ('CHECKS_FAILED' in log or 'ERROR' in log or 'FAIL' in log),n)
check('helper失败未冒充stderr原字节',all(x['raw_native_stderr_captured'] is False and x['tool_return_available'] is True for x in h['helper_failures']) and any('64k' in x and '转录' in x for x in manifest['limitations']),h['helper_failures'])
node=obj(E/'root_native_closed/node_limit_failure_transcription_r01.json')
poll=obj(E/'mcp_closed/s11_supervisor_wait_consumption_closed.tool.json')
falsegate=obj(E/'mcp_closed/s11_false_gate_error_closed.tool.json')
check('64k转录明确非原字节/native空',node['original_tool_return_bytes_saved'] is False and node['native_exit_code'] is None and node['input_code_sha256'] is None and '64000-byte' in json.dumps(node))
check('单poll终态2/[]真实错误说明',len(poll)==1 and poll[0]['result']['exit_code']==2 and falsegate['diagnosis']['uncertain']==[] and 'isError' in falsegate['reason'])
for mode,expected in [('evidence',0),('inputs',2)]:
    cp=run(mode,[sys.executable,'-B','-X','utf8',str(ROOT/'verification/check_stage_delivery.py'),'--mode',mode,'--manifest',str(E/'s11_delivery_manifest_r05.json'),'--project-root',str(ROOT)])
    check('当前轻量包装真实码：'+mode,cp.returncode==expected,{'native':cp.returncode,'expected':expected,'scope':'包装'})
check('实现/postroute/硬件NOT_RUN',summary['implementation']==summary['postroute']==summary['hardware']=='NOT_RUN' and all(x['status']=='NOT_RUN' for x in manifest['checks'] if x['name'] in ['实现及postroute','G3板上cache/模型/109/1000任务']))
result={'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'CHANGES_REQUIRED','scope':'S11实际综合失败证据准确性及可恢复性，仅G2事实审查','source_commit':COMMIT,'reviewed_manifest_hash':MSHA,'reviewer_stop':'STOP_READONLY_S11_ACTUAL_REVIEW_FROZEN','checks':checks,'findings':[x for x in checks if x['status']=='FAIL'],'commands':commands,'elapsed_seconds':time.monotonic()-started,'sampled_self_rss_bytes':peak_sample,'absolute_self_peak_memory_bytes':None,'encoding_notes':enc,'limitations':['50MHz/-2综合STA FAIL WNS−4.404/TNS−1939.802/787of14873；不批准时序收敛、实现/postroute/bit/G3/G4/G5或部署','全程预算覆盖BLOCKED；150样本仅窗口，36612 ABSENT+UNKNOWN导致RSS缺测不补0，r02仅报告闭合旧guard，race2未用于heavy','ROOT未执行每5秒消费，仅单poll；[]truthy/isError未检查后continuedlaunch错误保留','native5job日志与marker成功，OS码未捕获null；nativewait0/569.942s与client300s超时不同','两helper失败无原stderr字节，64k错误仅工具返回转录；失败collect1/r02r03checker2保留','六PSinit同旧而HWH不同不继承runtime/BSP兼容','未执行重型/仿真/ROSS/设备/真实任务进程操作，不改源/正式证据/Git/STATE；当前PNR另Run不在本审查','752/760/543逐项SHA核验但raw仅关键入口，不复制历史包；自有RSS离散采样非绝对峰']}
result['temporary_origin_drift']=drift
result['limitations'].append('临时s11p1五个gen_run.xml当前原址SHA已变化；保存的100个native副本全部固定SHA通过，恢复必须消费正式saved_path而非临时原址。')
save('review_result.json',result);save('review_inputs.json',list(seen.values()))
print(json.dumps({'status':result['status'],'checks':len(checks),'findings':result['findings'],'elapsed_seconds':result['elapsed_seconds'],'sampled_self_rss_bytes':peak_sample},ensure_ascii=False))
raise SystemExit(0 if result['status']=='PASS' else 2)
