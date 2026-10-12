"""仅补核G0最终r04包装，保留r03真实失败。"""
import hashlib,json,subprocess,sys
from pathlib import Path
import psutil
O=Path(__file__).absolute().parent; R=O.parents[3]; D=R/'report/evidence/S2B-T17/s14_timing_g0_20261012_r01'; M=D/'delivery_manifest_r04.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
expected='3d7ac4b3631c689946a1704d7843fe09f79ff94d4b4c3d6fd7722f0f6a863dca'
assert M.is_file() and sha(M)==expected
cmd=[sys.executable,'-X','utf8','-B',str(R/'verification/check_stage_delivery.py'),'--mode','evidence','--manifest',str(M),'--project-root',str(R)]
p=subprocess.Popen(cmd,cwd=R,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
try: birth=psutil.Process(p.pid).create_time()
except psutil.Error: birth=None
stdout,stderr=p.communicate(); (O/'g0_evidence_r04.stdout.bin').write_bytes(stdout); (O/'g0_evidence_r04.stderr.bin').write_bytes(stderr)
old=json.loads((O/'g0_metadata_addendum.json').read_text(encoding='utf-8'))
assert all(row['ok'] for row in old['checks'] if row['name']!='G0 evidence实际native0')
new={'status':'PASS_READ_ONLY_ATTRIBUTION_METADATA_ONLY' if p.returncode==0 else 'CHANGES_REQUIRED','stop':'STOP_METADATA_REVIEW_COMPLETE','manifest':{'path':M.relative_to(R).as_posix(),'sha256':expected},'prior_semantic_review':{'path':(O/'g0_metadata_addendum.json').relative_to(R).as_posix(),'sha256':sha(O/'g0_metadata_addendum.json'),'actual_r03_evidence_return':2,'reason':'未绑定本轮新delivery_manifest_r04.json，原失败两流保留；102逐路径/22+68+12分组、来源范围及owned旧实例检查已通过。'},'native_checker':{'argv':cmd,'pid':p.pid,'birth':birth,'actual_wait_return':p.returncode,'stdout_sha256':hashlib.sha256(stdout).hexdigest(),'stderr_sha256':hashlib.sha256(stderr).hexdigest(),'internal_child_identity':'UNKNOWN'},'scope':'仅准许提交S13失败证据及S14只读归因元数据；不批准S14生产修复、综合、PNR、硬件或连续预算PASS。','limitations':['r04使用实际timing_all Tcl并把未采finalize.argv置null，没有补造运行命令。','未重跑102端点或任何设计；只补本最终清单evidence包装核对，实际S13 STA仍FAIL。']}
(O/'g0_metadata_addendum_r04.json').write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':new['status'],'native_wait':p.returncode,'receipt_sha256':sha(O/'g0_metadata_addendum_r04.json')},ensure_ascii=False)); sys.exit(0 if p.returncode==0 else 1)
