"""记录本轮审计和两个包装模式的真实child wait及两流。"""
import hashlib,json,subprocess,sys,time
from pathlib import Path
import psutil
O=Path(__file__).absolute().parent; R=O.parents[3]; records=[]
manifest=R/'report/evidence/S2B-T17/s13_root_closure_20261012_r01/delivery_manifest_r03.json'
jobs=[('audit_r02',[sys.executable,'-X','utf8','-B',str(O/'audit.py')],0)]
for mode,expected in [('evidence',0),('inputs',2)]:
 jobs.append((mode,[sys.executable,'-X','utf8','-B',str(R/'verification/check_stage_delivery.py'),'--mode',mode,'--manifest',str(manifest),'--project-root',str(R)],expected))
for label,command,expected in jobs:
 start=time.monotonic(); p=subprocess.Popen(command,cwd=R,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 try: birth=psutil.Process(p.pid).create_time()
 except psutil.Error: birth=None
 stdout,stderr=p.communicate(); (O/(label+'.stdout.bin')).write_bytes(stdout); (O/(label+'.stderr.bin')).write_bytes(stderr)
 row={'label':label,'command':command,'pid':p.pid,'birth':birth,'actual_wait_return':p.returncode,'expected_return':expected,'elapsed_seconds':time.monotonic()-start,'stdout_sha256':hashlib.sha256(stdout).hexdigest(),'stderr_sha256':hashlib.sha256(stderr).hexdigest(),'internal_git_or_process_tree_identity':'UNKNOWN'}; records.append(row)
 print(json.dumps(row,ensure_ascii=False)); print(stdout.decode('utf-8',errors='replace')[-2500:]); print(stderr.decode('utf-8',errors='replace')[-1000:])
(O/'native_results_r02.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sys.exit(0 if all(r['actual_wait_return']==r['expected_return'] for r in records) else 1)
