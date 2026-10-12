import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

ROOT=Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition')
OUT=Path(__file__).resolve().parent
P=ROOT/'report/evidence/S2B-T17/s15_postroute_20261012_r01'
checks=[]
errors=[]
def ck(ok,name,detail=None):
    checks.append({'name':name,'pass':bool(ok),'detail':detail})
    if not ok: errors.append({'name':name,'detail':detail})
def read(p):
    assert p.is_file(),str(p)
    return p.read_bytes()
def js(p): return json.loads(read(p).decode('utf-8'))
def save(p):
    target=OUT/'inputs'/p.relative_to(ROOT)
    target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists(): target.write_bytes(read(p))
    ck(read(target)==read(p),'补充原件快照 '+str(p.relative_to(ROOT)))
def digest(p): return hashlib.sha256(read(p)).hexdigest()
stats=[]
for r in [1,2]:
    folder=P/'raw_root'/('supervision_r%02d'%r)
    rows=[json.loads(x) for x in read(folder/'guard/samples.jsonl').decode('utf-8').splitlines()]
    g=js(folder/'guard/guard_receipt.json')
    s=js(folder/'supervisor_receipt.json')
    c=js(P/'raw_root'/('native_consumer_r%02d'%r)/'consumer_receipt.json')
    valid=[x['tree_rss_bytes'] for x in rows if x['tree_rss_bytes'] is not None]
    gaps=[x['actual_start_gap_seconds'] for x in rows if x['actual_start_gap_seconds'] is not None]
    stat={'round':r,'sample_count':len(rows),'valid_count':len(valid),'unclosed_count':len(rows)-len(valid),'sampled_peak_tree_rss_bytes':max(valid),'minimum_ram_bytes':min(x['available_ram_bytes'] for x in rows),'minimum_c_free_bytes':min(x['c_disk_free_bytes'] for x in rows),'gaps_above_1s':sum(x>1 for x in gaps),'maximum_start_gap_seconds':max(gaps),'first_utc8':rows[0]['at_utc8'],'last_utc8':rows[-1]['at_utc8'],'alerts_count':sum(len(x['alerts']) for x in rows),'guard_native_child_wait':s['child_native_exit_code'],'supervisor_self_reported_exit_code':s['supervisor_exit_code'],'consumer_self_reported_exit_code':c['native_exit_code'],'absolute_continuous_tree_peak_bytes':None}
    ck(stat['sampled_peak_tree_rss_bytes']==g['sampled_peak_tree_rss_bytes'] and stat['minimum_ram_bytes']==g['minimum_sampled_available_ram_bytes'] and stat['minimum_c_free_bytes']==g['minimum_sampled_c_disk_free_bytes'],'独立预算统计 r'+str(r),stat)
    ck(stat['guard_native_child_wait']==3 and stat['supervisor_self_reported_exit_code']==2 and stat['consumer_self_reported_exit_code']==2 and c['blocked_latched'],'真实3/2/2不得被包装0抹除 r'+str(r))
    ck(stat['unclosed_count']==1 and rows[-1]['uncertain'] and rows[-1]['tree_rss_bytes'] is None,'真实身份缺口 r'+str(r))
    cl=P/'raw_root'/('native_consumer_r%02d'%r)/'consumption.jsonl'
    ck(digest(cl)==c['consumption_jsonl_sha256'] and len(read(cl))==c['consumption_jsonl_bytes'],'消费日志真绑定 r'+str(r))
    save(cl)
    stats.append(stat)
gap=(datetime.fromisoformat(stats[1]['first_utc8'])-datetime.fromisoformat('2026-10-12T14:49:06.6316187+08:00')).total_seconds()
ck(datetime.fromisoformat(stats[0]['last_utc8'])<datetime.fromisoformat('2026-10-12T14:49:06+08:00') and gap>500,'PNR开始前r01已终态且r02迟到超过500s',gap)
terminal=js(P/'raw_root/r02_terminal_receipt.json')
ck(terminal['host_tool_exit_code']==1 and terminal['supervisor_self_reported_exit_code']==2 and terminal['consumer_direct_parent_wait']=='NOT_AVAILABLE','host1及native2分列且consumer直接父wait未知')
ck(terminal['absolute_tree_peak_bytes'] is None and terminal['continuous_budget_status']=='BLOCKED_NOT_PROVEN_CONTINUOUS','连续预算BLOCKED不得PASS')

paired=[]
def walk(v):
    if isinstance(v,dict):
        if isinstance(v.get('original'),dict) and isinstance(v.get('saved'),dict): paired.append(v)
        for x in v.values():walk(x)
    elif isinstance(v,list):
        for x in v:walk(x)
walk(js(P/'pnr_original_file_map.json'))
for x in paired:
    a,b=x['original'],x['saved']
    ck(a['sha256']==b['sha256'] and a['bytes']==b['bytes'] and digest(ROOT/b['path'])==a['sha256'],'正式原件逐字节归档 '+b['path'])
ck(len(paired)>500,'原件映射完整范围',len(paired))

prepared=js(P/'native_capture_closed/prepared_receipt_r04.json')
nativeprepare=js(P/'raw_root/prepare_pnr.native.json')
classifier=js(P/'raw_root/pnr_classifier_r01.native.json')
ck(nativeprepare['native_exit_code']==0 and classifier['native_exit_code']==0 and prepared['status']=='PREPARED_NOT_EXECUTED_NOT_CLOSED','prepare/classify真实0不冒充旧seal成功')
ck('classify' in classifier['command'] and 'collect' not in classifier['command'],'实际classify不调用旧collect')
for row in prepared['dependencies']:
    ck(digest(ROOT/row['path'])==row['sha256'] and len(read(ROOT/row['path']))==row['bytes'],'实际prepared依赖 '+row['path'])

timing=read(P/'native_jobs/s2b_inference_wrapper_timing_summary_postroute_physopted.rpt').decode('utf-8')
ck(re.search(r'\n\s*0\.007\s+0\.000\s+0\s+15425\s+0\.087\s+0\.000\s+0\s+15425\s+8\.870\s+0\.000\s+0\s+4534',timing) is not None,'native postroute physopt同最终STA')
pre=read(P/'native_jobs/s2b_inference_wrapper_timing_summary_routed.rpt').decode('utf-8')
ck('-0.293' in pre and '-2.029' in pre,'prephysopt失败−.293/−2.029真实保留')
save(P/'native_jobs/s2b_inference_wrapper_timing_summary_routed.rpt')
xdc=read(P/'constraints_pnr.xdc').decode('utf-8')
ck('ACTIVE_HIGH_AUX.ACT_HI_AUX' in xdc and 'ACTIVE_LOW_EXT.ACT_LO_EXT' in xdc and xdc.count('set_false_path -to [get_cells {syncstages_ff_reg[0]}]')==2,'reset两例外精确scope')

dcp=ROOT/'tmp/2B/S2B-T17/s15_launch_prepare_20261012_r02/project_s15_r01/s2b_inference_candidate.runs/impl_1/s2b_inference_wrapper_postroute_physopt.dcp'
assert dcp.is_file(),str(dcp)
st1=dcp.stat()
sha=hashlib.sha256()
with dcp.open('rb') as f:
    while True:
        b=f.read(1024*1024)
        if not b: break
        sha.update(b)
st2=dcp.stat()
checkpoint={'path':str(dcp),'sha256':sha.hexdigest(),'bytes':st2.st_size,'mtime_ns':st2.st_mtime_ns,'read_metadata_stable':st1.st_size==st2.st_size and st1.st_mtime_ns==st2.st_mtime_ns,'copied':False,'reference':'本次真实native日志生成并由open_run impl_1恢复；仅固定字节哈希，下游须重新核对并绑定，不授予重型预算。'}
ck(checkpoint['read_metadata_stable'],'实际postroutecheckpoint哈希稳定',checkpoint)
log=read(P/'native_jobs/runme.log').decode('utf-8')
ck(str(dcp).replace('\\','/') in log,'checkpoint精确路径来自实际日志')

alltiming=read(P/'timing_summary_pnr.rpt').decode('utf-8')
hold=[float(x) for x in re.findall(r'Slack \(MET\)\s*:\s*([\d.]+)ns\s*\(arrival time - required time\)',alltiming)]
ck(hold and min(hold)==.087,'独立hold path最小值',min(hold) if hold else None)
facts={'monitor_statistics':stats,'launch_to_r02_first_sample_gap_seconds':gap,'original_paired_mapping_count':len(paired),'fixed_postroute_checkpoint':checkpoint,'scope':'PASS_PNR_STA_ONLY候选；预算BLOCKED和位流/运行/G3-G5未通过。'}
(OUT/'supplement_result.json').write_text(json.dumps({'checks':checks,'errors':errors,'facts':facts},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checks':len(checks),'errors':errors,'facts':facts},ensure_ascii=False))
raise SystemExit(2 if errors else 0)
