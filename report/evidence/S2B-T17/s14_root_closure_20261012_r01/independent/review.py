import hashlib
import json
import pathlib
import re
import subprocess
import sys
import time
import zipfile

# 本脚本仅核查固定原件和运行轻量只读清单检查器。
ROOT = pathlib.Path.cwd()
OUT = pathlib.Path(__file__).parent
R = ROOT / 'report/evidence/S2B-T17/s14_root_closure_20261012_r01'
P = ROOT / 'report/evidence/S2B-T17/s14_platform_20261012_r01'
C = P / 'mcp_closed'
BASE = '53772ae581ff3ccfb3a9d411cdc66fc67c3e2161'

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, d):
    (OUT / name).write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

manifest = read(R / 'delivery_manifest.json')
before_hashes = {x['path']: sha(ROOT / x['path']) for x in manifest['files']}
manifest_sha = sha(R / 'delivery_manifest.json')
assert manifest_sha == 'd55d5f5d0e15c84846809ae36841a2df2839365af683e1f12a38efcda0ec49eb'
assert len(before_hashes) == 449
assert all(before_hashes[x['path']] == x['sha256'] for x in manifest['files'])
save('original449_hash_index.json', before_hashes)
results = {'manifest_sha256': manifest_sha, 'bound_files': len(before_hashes), 'checks': len(manifest['checks'])}
for mode in ['evidence', 'inputs']:
    cmd = [sys.executable, '-X', 'utf8', '-B', 'verification/check_stage_delivery.py', '--mode', mode, '--manifest', str(R / 'delivery_manifest.json')]
    started = time.perf_counter()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    peak = None
    try:
        import psutil
        sampled = psutil.Process(proc.pid)
        while proc.poll() is None:
            try:
                rss = sampled.memory_info().rss
                peak = rss if peak is None else max(peak, rss)
            except psutil.Error:
                pass
            time.sleep(0.01)
    except ImportError:
        pass
    stdout, stderr = proc.communicate()
    (OUT / (mode + '.stdout.bin')).write_bytes(stdout)
    (OUT / (mode + '.stderr.bin')).write_bytes(stderr)
    results[mode] = {'command': cmd, 'native_exit_code': proc.returncode, 'elapsed_seconds': time.perf_counter()-started, 'sampled_single_process_peak_bytes': peak, 'tree_peak_bytes': None, 'stdout_sha256': hashlib.sha256(stdout).hexdigest(), 'stderr_sha256': hashlib.sha256(stderr).hexdigest(), 'stdout': stdout.decode('utf-8', errors='replace'), 'stderr': stderr.decode('utf-8', errors='replace')}
save('checker_actual.json',results)
sources_before = read(C / 'source_before.json')
sources_after = read(C / 'source_after.json')
binding = read(P / 's14_source_binding.json')
assert sources_before['source_sha256'] == sources_after['source_sha256']
assert sources_before['static_source_sha256'] == sources_after['static_source_sha256']
assert sources_before['frozen14_sha256'] == sources_after['frozen14_sha256']
assert len(sources_before['source_sha256']) == 45
assert len(sources_before['static_source_sha256']) == 33
assert len(sources_before['frozen14_sha256']) == 14
assert len(binding['compiled_rtl']) == 18
assert all(sha(ROOT / k) == v for k,v in sources_before['source_sha256'].items())
assert all(sha(ROOT / k) == v for k,v in sources_before['static_source_sha256'].items())
source_detail = [{'path':k,'sha256':v,'git_raw_sha256':hashlib.sha256(subprocess.check_output(['C:/Program Files/Git/cmd/git.exe','show',BASE+':'+k])).hexdigest()} for k,v in sources_before['source_sha256'].items()]
save('source_binding_independent.json', {'before':sha(C/'source_before.json'),'after':sha(C/'source_after.json'),'counts':[45,33,14,18], 'files':source_detail,'raw_git_equal_count':sum(x['sha256']==x['git_raw_sha256'] for x in source_detail)})
history_tool = read(C / 'history_closed.tool.json')
history = json.loads(history_tool['content'][0]['text'])
save('history_structure.json',{'type':type(history).__name__,'keys':list(history) if isinstance(history,dict) else None})
mcp = read(P / 's14_mcp_binding.json')
save('mcp_independent.json',{'paired_summary':[{'label':x['label'],'native_id':x['native_history']['id'],'native_code':x['native_history']['code'],'command':x['native_history']['command'],'elapsed':x['native_history']['elapsed'],'client_code':x.get('client_exit_code')} for x in mcp['paired_calls']], 'raw_history':history})
jobs=[]
for job in (P/'native_jobs').iterdir():
    log=(job/'runme.log').read_text(encoding='utf-8',errors='replace')
    jobs.append({'name':job.name,'log_sha256':sha(job/'runme.log'),'end_marker':(job/'.vivado.end.rst').is_file(),'completion_marker':(job/'__synthesis_is_complete__').is_file(),'error_marker':(job/'.vivado.error.rst').exists(),'completion_lines':[x for x in log.splitlines() if ('completed' in x.lower() or 'errors' in x.lower() or 'synth_design: Time' in x)][-8:]})
save('native_jobs_independent.json',jobs)
monitor=[]
for run in ['r01','r02','r03']:
    g=read(C/f'supervision_{run}__guard__guard_receipt.json')
    s=read(C/f'supervision_{run}__supervisor_receipt.json')
    u=read(C/f'native_consumer_{run}__consumer_receipt.json')
    samples=[json.loads(x) for x in (C/f'supervision_{run}__guard__samples.jsonl').read_text(encoding='utf-8').splitlines()]
    valid=[x for x in samples if x.get('collection_observation',{}).get('closed') and x.get('tree_rss_bytes') is not None]
    monitor.append({'run':run,'guard_status':g['status'],'guard_reason':g['reason'],'guard_native':s['child_native_exit_code'],'supervisor_native':s['supervisor_exit_code'],'consumer_native':u['native_exit_code'],'raw_sample_count':len(samples),'receipt_sample_count':g['samples'],'unclosed_samples':sum(not x.get('collection_observation',{}).get('closed',False) for x in samples),'valid_peak':max(x['tree_rss_bytes'] for x in valid),'maximum_schedule_delay':max(x.get('schedule_delay_seconds',0) or 0 for x in samples),'maximum_start_gap':max(x.get('actual_start_gap_seconds',0) or 0 for x in samples),'absolute_peak':g['absolute_peak_memory_bytes']})
save('monitor_independent.json',monitor)
comparisons=read(P/'s14_xsa_comparison.json')
oldpath=pathlib.Path(comparisons['old_xsa']['path'])
newpath=pathlib.Path(comparisons['new_xsa']['path'])
with zipfile.ZipFile(oldpath) as old,zipfile.ZipFile(newpath) as new:
    relation=[{'name':x,'old_sha256':hashlib.sha256(old.read(x)).hexdigest(),'new_sha256':hashlib.sha256(new.read(x)).hexdigest(),'equal':old.read(x)==new.read(x)} for x in new.namelist() if x in old.namelist() and ('ps7_init' in x or x.endswith('.hwh'))]
save('xsa_members_independent.json',relation)
pack=[]
for label in ['s14_prepare_r01','s14_source_before_r01','s14_source_after_r01','s14_collect_r01','s14_collect_r02','s14_collect_r03','s14_seal_r01']:
    d=read(R/(label+'.native.json'))
    pack.append({'label':label,'command':d['command'],'keys':list(d),'native_record_sha256':sha(R/(label+'.native.json')),'exit_code':d.get('native_exit_code',d.get('exit_code')),'elapsed_seconds':d.get('elapsed_seconds'),'stderr':(R/(label+'.stderr.bin')).read_bytes().decode('utf-8',errors='replace')})
save('packing_independent.json',pack)
save('root_observation_independent.json',read(C/'root__closed_runtime_observation.json'))
companion=R/'host_execution_receipts.json'
assert sha(companion)=='b6f2b5c3476154e62fa127aac257621bb389b2240f92f671ac1f26eb4c4a1d70'
save('companion_structure.json', {'sha256':sha(companion),'content':read(companion)})
after_hashes={x['path']:sha(ROOT/x['path']) for x in manifest['files']}
assert before_hashes == after_hashes
assert manifest_sha == sha(R/'delivery_manifest.json')
save('original449_after_hash_index.json',after_hashes)
save('initial_execution_complete.json',{'status':'READONLY_CHECKS_DONE','source_commit':BASE,'bound449_unchanged':True,'manifest_sha256':manifest_sha,'checker_codes':{x:results[x]['native_exit_code'] for x in ['evidence','inputs']},'monitor':monitor,'job_count':len(jobs),'xsa_relations':relation,'final_actual_receipt_sha256':sha(R/'final_actual_receipt.json'),'companion_sha256':sha(companion)})
print(json.dumps(read(OUT/'initial_execution_complete.json'),ensure_ascii=False,indent=2))
