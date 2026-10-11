"""在授权原生解释器下独立只读执行清单检查并保存原始stdout字节。"""
import subprocess,json,time,hashlib,sys,ctypes
from pathlib import Path
root=Path.cwd();out=root/'tmp/2B/S2B-T17/independent_s12_functional_review_20261012_r01';main=root/'report/evidence/S2B-T17/s12_timing_cones_20261012_r01';runs=[]
for mode,expected in [('evidence',0),('inputs',2)]:
 cmd=[sys.executable,'-X','utf8','-B','verification/check_stage_delivery.py','--mode',mode,'--manifest',str(main/'delivery_manifest_r02.json'),'--project-root',str(root)]
 started=time.monotonic();r=subprocess.run(cmd,cwd=root,capture_output=True)
 stdout=out/(mode+'_native_checker.stdout.log');stderr=out/(mode+'_native_checker.stderr.log')
 if stdout.exists() or stderr.exists():raise ValueError('原生checker RunId输出已存在')
 stdout.write_bytes(r.stdout);stderr.write_bytes(r.stderr)
 parsed=json.loads(r.stdout.decode('utf-8'))
 runs.append(dict(command=cmd,native_exit_code=r.returncode,expected_exit_code=expected,status=parsed['status'],seconds=time.monotonic()-started,stdout_path=str(stdout),stdout_sha256=hashlib.sha256(r.stdout).hexdigest(),stderr_path=str(stderr),stderr_sha256=hashlib.sha256(r.stderr).hexdigest()))
 if r.returncode!=expected:raise ValueError(runs[-1])
 print(mode,r.returncode,parsed['status'])
receipt=dict(status='PASS_EXPECTED_READONLY_CHECKER_CODES',runs=runs,python=sys.version,interpreter=sys.executable,limitations=['expected inputs2未冻结/历史FAIL/本Run前G2状态，不能解释为接口冻结或STA/G3批准。','原始sandbox枚举拒绝另存，原生授权解释器真实输出不覆盖该失败。','子进程绝对峰未测；只读清单检查，无RTL或Vivado。'])
(out/'native_checker_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
