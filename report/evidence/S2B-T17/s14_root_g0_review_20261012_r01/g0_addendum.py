"""仅核对只读归因包的102端点、分组、原件与范围。"""
import csv,hashlib,json,re,subprocess,sys
from collections import Counter
from pathlib import Path
import psutil
O=Path(__file__).absolute().parent; R=O.parents[3]; D=R/'report/evidence/S2B-T17/s14_timing_g0_20261012_r01'; checks=[]
def check(ok,name): checks.append({'name':name,'ok':bool(ok)})
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
m=D/'delivery_manifest_r03.json'; data=json.loads(m.read_text(encoding='utf-8')); f=json.loads((D/'final_receipt.json').read_text(encoding='utf-8')); g=json.loads((D/'cone_groups.json').read_text(encoding='utf-8'))
check(sha(m)=='0cb8a302479847c2e758af9ba9567809bdb047cb52fa29cdde3799ce9ce5c849','G0 r03精确SHA')
for row in data['files']: check((R/row['path']).is_file() and sha(R/row['path'])==row['sha256'],'G0文件SHA:'+row['path'])
rows=list(csv.DictReader((D/'endpoints.tsv').open(encoding='utf-8'),delimiter='\t')); report=(D/'timing_all_failed.rpt').read_text(encoding='utf-8')
paths=re.findall(r'Slack \(VIOLATED\)\s*:\s*([-\d.]+)ns.*?\n\s*Source:\s*(\S+).*?\n\s*Destination:\s*(\S+)',report,re.S)
check(len(paths)==len(rows)==102 and len({r['endpoint'] for r in rows})==102,'原报告102路径及TSV端点唯一')
check([(float(a),b,c) for a,b,c in paths]==[(float(r['slack']),r['startpoint'],r['endpoint']) for r in rows],'全部102路径与原报告一一一致')
check(g['groups']==f['groups'] and sorted(x['count'] for x in g['groups'])==[12,22,68],'22/68/12分组与receipt一致')
counts=Counter(r['startpoint'] for r in rows)
for group in g['groups']:
 selected=[r for r in rows if r['startpoint']==group['startpoint']]
 check(counts[group['startpoint']]==group['count'] and {r['endpoint'] for r in selected}==set(group['endpoints']) and min(float(r['slack']) for r in selected)==group['worst_slack'],'原始分组成员及最差slack:'+group['startpoint'])
check(f['status']=='READ_ONLY_ATTRIBUTION_COMPLETE_STA_REMAINS_FAIL' and f['source_commit']=='701dc55af0c53a959e84dc0c470f136918f5bd50' and f['source_count']==44 and f['source_before_after_stable'] is True,'版本与继续STA FAIL声明')
tool_commands=[]
for p in D.glob('*.tool.json'):
 value=json.loads(p.read_text(encoding='utf-8')); command=value.get('input',{}).get('command')
 if command: tool_commands.append(command)
check(not any(re.search(r'(^|[;\n])\s*(launch_runs|synth_design)\b',c) for c in tool_commands),'已记录命令无新增launch/synth_design')
check(json.loads(json.loads((D/'stop.tool.json').read_text(encoding='utf-8'))['content'][0]['text'])['status']=='success','实际analysis stop success')
try:
 p=psutil.Process(f['owned_process']['pid']); status='PID_REUSED' if p.create_time()!=f['owned_process']['create_time'] else 'SAME_INSTANCE_LIVE'
except psutil.NoSuchProcess: status='ABSENT'
except psutil.Error: status='UNKNOWN'
check(status in ('ABSENT','PID_REUSED'),'analysis旧owned实例不存在')
argv=[sys.executable,'-X','utf8','-B',str(R/'verification/check_stage_delivery.py'),'--mode','evidence','--manifest',str(m),'--project-root',str(R)]
p=subprocess.Popen(argv,cwd=R,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
try: birth=psutil.Process(p.pid).create_time()
except psutil.Error: birth=None
stdout,stderr=p.communicate(); (O/'g0_evidence.stdout.bin').write_bytes(stdout); (O/'g0_evidence.stderr.bin').write_bytes(stderr)
check(p.returncode==0,'G0 evidence实际native0')
receipt={'status':'PASS_READ_ONLY_ATTRIBUTION_METADATA_ONLY' if all(r['ok'] for r in checks) else 'CHANGES_REQUIRED','manifest':{'path':m.relative_to(R).as_posix(),'sha256':sha(m)},'source_commit':f['source_commit'],'checks':checks,'raw_paths':102,'group_counts':[22,68,12],'owned_old_instance':status,'native_checker':{'argv':argv,'pid':p.pid,'birth':birth,'actual_wait_return':p.returncode,'stdout_sha256':hashlib.sha256(stdout).hexdigest(),'stderr_sha256':hashlib.sha256(stderr).hexdigest(),'internal_child_identity':'UNKNOWN'},'scope':'仅归因元数据/102端点分组/原件SHA及只读范围，不评审S14功能修复或批准最后一次综合；需要独立功能G1/G2后ROOT按用户边界处理。','limits':['属性来源单个cell行不能独自证明共用逻辑，1536 warning及工具output_truncated保留；未重建netlist。','来源以S13两份实际快照为准，没有读取当前生产RAW。','旧owned实例离散ABSENT/PID_REUSED和MCPstop success不是OSwait0；连续预算及绝对峰未知。']}
(O/'g0_metadata_addendum.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps({'status':receipt['status'],'receipt_sha256':sha(O/'g0_metadata_addendum.json'),'issues':[r['name'] for r in checks if not r['ok']]},ensure_ascii=False)); sys.exit(0 if all(r['ok'] for r in checks) else 1)
