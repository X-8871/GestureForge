"""只读补核最终r05的关闭命令作用域及包装。"""
import hashlib,json,subprocess,sys
from pathlib import Path
import psutil
O=Path(__file__).absolute().parent; R=O.parents[3]; D=R/'report/evidence/S2B-T17/s14_timing_g0_20261012_r01'; M=D/'delivery_manifest_r05.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
expected='0468861e06569cdbf4388beeae61d9910cc2b1f05a60b63ae2dd228f19de4d0a'
assert M.is_file() and sha(M)==expected
m=json.loads(M.read_text(encoding='utf-8')); c=json.loads((D/'close_project.tool.json').read_text(encoding='utf-8')); result=json.loads(c['result']['content'][0]['text'])
assert m['checks'][1]['command']==c['command']=='close_project' and m['checks'][1]['exit_code']==result['exit_code']==0
assert 'finalize shell argv未知' in m['checks'][1]['reason'] and any('不补造finalize argv' in s for s in m['limitations'])
assert m['checks'][2]['status']=='FAIL' and all(x['status']=='NOT_RUN' for x in m['checks'][3:])
cmd=[sys.executable,'-X','utf8','-B',str(R/'verification/check_stage_delivery.py'),'--mode','evidence','--manifest',str(M),'--project-root',str(R)]
p=subprocess.Popen(cmd,cwd=R,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
try: birth=psutil.Process(p.pid).create_time()
except psutil.Error: birth=None
stdout,stderr=p.communicate(); (O/'g0_evidence_r05.stdout.bin').write_bytes(stdout); (O/'g0_evidence_r05.stderr.bin').write_bytes(stderr)
receipt={'status':'PASS_METADATA_ONLY' if p.returncode==0 else 'CHANGES_REQUIRED','stop':'STOP_FINAL_G0_METADATA_REVIEW','manifest':{'path':M.relative_to(R).as_posix(),'sha256':expected},'scope':'G0只读归因元数据及最终r05包装；close_project命令/native0只说明工程关闭，44快照证据另列，不伪造finalize argv。允许ROOT提交该元数据范围，不批准S14功能修复、综合、PNR、硬件或连续预算。','native_checker':{'argv':cmd,'pid':p.pid,'birth':birth,'actual_wait_return':p.returncode,'stdout_sha256':hashlib.sha256(stdout).hexdigest(),'stderr_sha256':hashlib.sha256(stderr).hexdigest(),'internal_child_identity':'UNKNOWN'},'closed_issue':'r04 PASS/null command包装阻断已用原件close_project/native0关闭，原失败清单及Reviewer输出保留。','semantic_witness':{'path':(O/'g0_metadata_addendum.json').relative_to(R).as_posix(),'sha256':sha(O/'g0_metadata_addendum.json'),'scope':'102原报告/TSV逐路径相同，22/68/12分组及最差slack正确，旧owned实例ABSENT，未新增launch；此前仅r03包装因出现r04而失败。'},'limits':['本轮只执行包装及声明作用域核对，不重复102端点分析。','S13综合态STA仍FAIL；finalize原生0不提供未知shell argv；MCP关闭及离散旧实例ABSENT不是OS wait0。','被审文件、源码、STATE和Git未修改，未调用Vivado或设计重跑。']}
(O/'g0_metadata_addendum_r05.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':receipt['status'],'native_wait':p.returncode,'receipt_sha256':sha(O/'g0_metadata_addendum_r05.json')},ensure_ascii=False)); sys.exit(0 if p.returncode==0 else 1)
