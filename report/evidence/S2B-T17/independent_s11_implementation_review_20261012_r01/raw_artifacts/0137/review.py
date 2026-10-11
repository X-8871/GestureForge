"""独立只读核对实际PNR失败证据；不执行Git、设计命令或真实任务进程查询。"""
import ast, hashlib, json, math, re, subprocess, sys, time
from pathlib import Path
from types import SimpleNamespace
import psutil
ROOT=Path(__file__).parents[4]
WORK=Path(__file__).parent
FORMAL=ROOT/'report/evidence/S2B-T17/s11_implementation_20261012_r01'
START=time.monotonic(); checks=[]; used={}; failures=[]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
def path(v):
    p=Path(v) if Path(v).is_absolute() else ROOT/v
    if not p.is_file(): raise ValueError('路径不是实际文件：'+str(p))
    return p
def remember(p,role='input'):
    p=path(p); used[p.relative_to(ROOT).as_posix()]=role; return p
def read(v,role='input'):
    return json.loads(remember(v,role).read_text(encoding='utf-8'))
def check(name,condition,detail=None):
    checks.append(dict(name=name,passed=bool(condition),detail=detail))
    if not condition: failures.append(name)
def verify(row):
    p=path(row['path']); return sha(p)==row['sha256'] and ('bytes' not in row or p.stat().st_size==row['bytes'])
def mcp(value):
    result=value.get('result',value)
    return json.loads(next(b['text'] for b in result['content'] if b['type']=='text'))
manifest=read(FORMAL/'delivery_manifest_r02.json')
check('主清单冻结SHA',sha(FORMAL/'delivery_manifest_r02.json')=='a760ec030d6f858cfa508e533ab907d139078458879462e0ee2f2738ed610035')
check('全部586绑定原字节',len(manifest['files'])==586 and all(verify(r) for r in manifest['files']))
sb=read(FORMAL/'s11_implementation_source_binding.json'); cb=read(FORMAL/'pnr_closed_binding.json'); sta=read(FORMAL/'pnr_sta_result.json')
for name,digest in [('s11_implementation_source_binding.json','6885815113032963526b573910f2ce1b4a45c0bbcd5f179a67e61b88e7ab4008'),('pnr_closed_binding.json','df278ccca650f648a3382f80e1db265497e96ecaaa3279a437484672e7060df7'),('pnr_sta_result.json','0eef9dd617cdefc829ce92a0d4a107b9ed33220150a9b1b05a717071827f2062')]:
    check(name+'冻结SHA',sha(FORMAL/name)==digest)
mapping={r['original']['path']:r['saved'] for r in cb['mapping']}
check('保存原字节恢复映射',all(verify(r['saved']) and r['original']['sha256']==r['saved']['sha256'] and r['original']['bytes']==r['saved']['bytes'] for r in cb['mapping']),len(mapping))
def saved(original): return path(mapping.get(original,{'path':original})['path'])
gate=read(FORMAL/'collector_code/closed_gate_actual_r04.json')
check('关闭门禁和单次执行',gate['project_closed'] is True and gate['owned_root_exited'] is True and gate['root_declared_implementation_execution_count']==1)
freeze=read('report/evidence/S2B-T17/maxpool_geometry_factor_20261012_r02/source_freeze.json')
sources={r['path']:r['sha256'] for r in freeze['source_files']}
check('43源当前与冻结相同',len(sources)==43 and all(sha(path(p))==digest for p,digest in sources.items()))
check('43来源快照全部相同',len(sb['source_files'])==43 and all(sha(path(r['snapshot']))==r['sha256']==sources[r['path']] for r in sb['source_files']))
check('33静态18RTL8派生原14',sb['static_count']==33 and sb['active_rtl_count']==18 and sb['derived_rtl_count']==8 and sb['frozen14_count']==14 and sb['frozen14']==freeze['frozen14'] and set(sb['active_rtl_sources'])==set(freeze['active_rtl_sources']))
check('原14实际字节',all(sha(path(p))==digest for p,digest in freeze['frozen14'].items()))
before=read(saved(gate['source_before']['path'])); after=read(saved(gate['source_after']['path']))
for label,rec in [('before',before),('after',after)]:
    check(label+'源集合',rec['source_commit']==manifest['source_commit'] and {r['path']:r['sha256'] for r in rec['source_files']}==sources and rec['frozen14_sha256']==freeze['frozen14'])
check('源码a710与实际HEAD932分列',after['actual_head_at_check']==after['actual_head_after_check']=='932051cdacdf02f729d6a7554b07118d05e96aa4' and after['source_commit']=='a710ec431474841a81912a6055f861e811a151e3')
check('before明示继承不冒充新预检','继承' in sb['before_scope'] and '不冒充' in sb['before_scope'])
during=read(saved('tmp/2B/S2B-T17/s11_impl_root_run_20261012_r01/source_during_r01.json'))
check('during实际43源',during['source_sha256']==sources)
git_base='tmp/2B/S2B-T17/s11_impl_root_run_20261012_r01/source_after_check_r01/'
git_dir=git_base+'git_native/'
commands=read(saved(git_base+'git_commands.json'))
if isinstance(commands,dict): commands=commands.get('commands',commands.get('records',[]))
git_relations={}; git_good=True
for i,row in enumerate(after['source_files'],1):
    blob=remember(saved(git_dir+f'git_{i:02d}.stdout.log'),'log').read_bytes()
    native=read(saved(git_dir+f'git_{i:02d}.native.json'),'result')
    raw=path(row['snapshot']).read_bytes()
    relation='RAW_IDENTICAL' if raw==blob else 'GIT_LF_TO_RAW_CRLF' if b'\r\n' not in blob and raw==blob.replace(b'\n',b'\r\n') else 'MISMATCH'
    git_relations[relation]=git_relations.get(relation,0)+1
    git_good &= native['native_exit_code']==0 and row['git_blob_sha256']==hashlib.sha256(blob).hexdigest() and relation==row['git_relation'] and native['command']==row['git_native_command']
check('实际保存Git原字节及精确EOL关系',git_good,git_relations)
for idx in (0,44):
    text=remember(saved(git_dir+f'git_{idx:02d}.stdout.log'),'log').read_text(encoding='utf-8').strip()
    check('HEAD原生回读'+str(idx),text==after['actual_head_at_check'] and read(saved(git_dir+f'git_{idx:02d}.native.json'))['native_exit_code']==0)
history=mcp(read(saved(gate['mcp_history']['path'])))['history']; byid={r['id']:r for r in history}
check('13history双射',len(history)==len(byid)==len(gate['design_mcp_records'])==13 and {r['id'] for r in gate['design_mcp_records']}==set(byid))
pair_good=True; codes={}; times={}
for row in gate['design_mcp_records']:
    call=read(saved(row['path'])); actual=mcp(call); item=byid[row['id']]
    pair_good &= call['input']['command']==item['command'] and actual['exit_code']==item['code']
    codes[row['label']]=item['code']; times[row['label']]=item
check('实际命令客户端与native一致',pair_good,codes)
approved='launch_runs impl_1 -to_step {phys_opt_design (Post-Route)} -jobs 1'
check('唯一成功批准launch',sum(r['command'].startswith('launch_runs impl_1') and r['code']==0 for r in history)==1 and times['launch']['command']==approved and codes['launch_invalid']==1 and codes['wait']==codes['close']==0)
report=remember(saved(gate['timing_summary']['path']),'log').read_text(encoding='utf-8')
section=report.split('| Design Timing Summary',1)[1].split('| Clock Summary',1)[0]
vals=next(line.split() for line in section.splitlines() if re.fullmatch(r'\s*-?\d+\.\d+(?:\s+-?\d+(?:\.\d+)?){11}\s*',line))
check('独立实际STA数值',list(map(float,vals[:8]))==[-3.201,-2123.755,908,15082,.037,0,0,15082],vals)
check('真实postroute50MHz与12检查0','Physopt postRoute' in report and re.search(r'^clk_fpga_0\s+\{0\.000\s+10\.000\}\s+20\.000\s+50\.000',report,re.M) and all(int(x)==0 for x in re.findall(r'checking \w+ \((\d+)\)',report)))
check('分类FAIL原生2',sta['native_exit_code']==2 and sta['status']=='FAIL_TIMING' and read(FORMAL/'pnr_classifier.native.json')['native_exit_code']==2)
reports={Path(p).name:p for p in mapping if '/reports/' in p}
details={}
for key in ('route_status_postroute.rpt','utilization_postroute.rpt','drc_postroute.rpt','methodology_postroute.rpt'):
    if key in reports: details[key]=remember(saved(reports[key]),'log').read_text(encoding='utf-8')
guard=read(saved(gate['guard_receipt']['path'])); sup=read(saved(gate['supervisor_receipt']['path'])); owned=read(saved(gate['owned_root_exit_proof']['path']))
check('guard0 supervisor2实际终态',guard['status']=='ROOT_EXITED' and sup['child_native_exit_code']==0 and sup['supervisor_exit_code']==2 and not guard['retained'])
check('离散预算阈值没有改动',guard['limits']==dict(tree_rss_bytes=6442450944,available_ram_bytes=536870912,c_disk_free_bytes=8589934592) and guard['sample_interval_seconds']==1)
sample_original=str(Path(gate['guard_receipt']['path']).parent/'samples.jsonl').replace('\\','/')
sample=remember(saved(sample_original),'log'); count=0; peak=0; minram=10**30; mindisk=10**30; uncertain=0; alerts=0; maxgap=0; last=None; first=None; identities=set(); historical=0; absent=0; missing=0
with sample.open(encoding='utf-8') as f:
    for line in f:
        row=json.loads(line); count+=1
        first=first or row
        if row['tree_rss_bytes'] is None: missing+=1
        else: peak=max(peak,row['tree_rss_bytes'])
        minram=min(minram,row['available_ram_bytes']); mindisk=min(mindisk,row['c_disk_free_bytes'])
        if last is not None: maxgap=max(maxgap,row['elapsed_seconds']-last['elapsed_seconds'])
        last=row; uncertain+=len(row.get('uncertain',[])); alerts+=len(row.get('alerts',[])); absent+=len(row.get('confirmed_exits',[]))
        for member in row['members']:
            identities.add((member['pid'],member['create_time'])); historical+=member.get('lineage_mode')=='HISTORICAL_CHAIN'
resource=dict(samples=count,peak=peak,min_ram=minram,min_disk=mindisk,uncertain=uncertain,alerts=alerts,missing_tree_samples=missing,max_gap_seconds=maxgap,first_at=first['at_utc8'],last_at=last['at_utc8'],distinct_observed_identities=len(identities),historical_member_samples=historical,confirmed_exit_events=absent)
check('3288采样独立统计一致',count==guard['samples']==3288 and peak==guard['sampled_peak_tree_rss_bytes']==3226779648 and minram==guard['minimum_sampled_available_ram_bytes']==2044063744 and mindisk==guard['minimum_sampled_c_disk_free_bytes']==15353761792,resource)
check('实测样本缺测不补与绝对峰未知',guard['absolute_peak_memory_bytes'] is None,dict(unknown=uncertain,alerts=alerts,missing=missing))
readbacks=owned.get('readback',owned.get('readbacks',[]))
check('已记录身份缺失证明',owned['status']=='KNOWN_IDENTITIES_EXITED' and readbacks and all(r['status']=='ABSENT' for r in readbacks),len(readbacks))
check('预算仍BLOCKED不冒充批准',cb['budget_status']=='BLOCKED_PENDING_INDEPENDENT_ACTUAL_COVERAGE_REVIEW' and any(r['status']=='BLOCKED' and r['exit_code'] is None for r in manifest['checks']))
inventory=read(FORMAL/'original_inventory.json'); check('初始报告原件可恢复',all(verify(r) for r in inventory['files']))
receipt=read('tmp/2B/S2B-T17/s11_impl_collection_run_20261012_r01/final_collection_receipt.json')
check('实际collect单次0及峰统计范围',receipt['collect']['native_exit_code']==0 and receipt['collect']['sampled_owned_tree_rss_peak_bytes']==67178496)
for mode in ('evidence','inputs'):
    command=[sys.executable,'-B','-X','utf8',str(ROOT/'verification/check_stage_delivery.py'),'--mode',mode,'--project-root',str(ROOT),'--manifest',str(FORMAL/'delivery_manifest_r02.json')]
    begin=time.monotonic(); p=subprocess.run(command,cwd=ROOT,capture_output=True)
    for suffix,data in [('stdout.log',p.stdout),('stderr.log',p.stderr)]:
        with (WORK/(mode+'.'+suffix)).open('xb') as f: f.write(data)
    native=dict(command=command,native_exit_code=p.returncode,elapsed_seconds=time.monotonic()-begin)
    with (WORK/(mode+'.native.json')).open('x',encoding='utf-8') as f: json.dump(native,f,ensure_ascii=False,indent=2)
    check('当前机器包装'+mode,p.returncode==(0 if mode=='evidence' else 2),native)
result=dict(status='CHANGES_REQUIRED' if failures else 'PASS',checks=checks,failures=failures,resource=resource,report_names=sorted(reports),report_details=details,history=times,used_inputs=used,elapsed_seconds=time.monotonic()-START,sampled_self_rss_bytes=psutil.Process().memory_info().rss,absolute_peak_memory_bytes=None,budget_assessment='BLOCKED：离散已核成员样本数值通过，不能证明ROOT每5秒消费与完整全程对象覆盖；未采到短命对象及连续峰未知，不追填缺测。')
with (WORK/'review_result.json').open('x',encoding='utf-8') as f: json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({k:result[k] for k in ('status','failures','resource','elapsed_seconds','sampled_self_rss_bytes')},ensure_ascii=False))
raise SystemExit(2 if failures else 0)
