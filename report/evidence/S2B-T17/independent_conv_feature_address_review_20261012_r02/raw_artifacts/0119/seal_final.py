"""仅封存完整失败原件与直接读取的SV输入，不重复执行编译/仿真。"""
from pathlib import Path
import json,hashlib,sys,subprocess,time
ROOT=Path.cwd();WORK=Path(__file__).resolve().parent;started=time.monotonic()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
receipt=WORK/'final_review_receipt.json';r=load(receipt);assert r['decision']=='PASS' and r['reviewer_stop']
for p,d in r['source_sha256'].items():assert sha(ROOT/p)==d
raw=WORK/'raw_manifest.jsonl';rows={row['path']:row for row in [json.loads(line) for line in raw.read_text(encoding='utf-8').splitlines()]}
for row in rows.values():assert sha(ROOT/row['path'])==row['sha256'],row['path']
for relative in load(WORK/'direct_inputs.json'):
    if relative.endswith('.sv') and 'source_snapshot' not in relative and 'final_source_snapshot' not in relative:
        p=ROOT/relative;rows[relative]={'path':relative,'sha256':sha(p),'role':'input'}
for name,role in [('finalize_initial_failure.json','diagnostic'),('seal_final.py','source')]:
    p=WORK/name;relative=p.relative_to(ROOT).as_posix();rows[relative]={'path':relative,'sha256':sha(p),'role':role}
r['commands'].append({'name':'final_failure_original_and_raw_sv_seal','command':subprocess.list2cmdline([sys.executable,'-X','utf8','-B',str(WORK/'seal_final.py')]),'native_exit_code':0,'seconds':round(time.monotonic()-started,3),'script_sha256':sha(WORK/'seal_final.py')})
r['tools']={'verilator':'5.050 2026-07-01','python':sys.version.split()[0],'toolchain':'D:/FPGA_S2A_MSYS2_20261001/env','configured_model_reported_by_root':'gpt-6.1-sol/high'}
r['failure_originals']={'initial_review':'validation.json完整traceback/原review.py/native1；已编译及首仿真native0。','supplement_finalize':'finalize_initial_failure.json工具原stderr/原finalize_r01_original.py/原空simulation_consumed.log/native1；原子程序码未知null。','loader_reproduction':'loader_failure.json与simulation_loader_failure.log，原生3221225785由实际子程序捕获，不填为宿主0。'}
receipt.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');relative=receipt.relative_to(ROOT).as_posix();rows[relative]={'path':relative,'sha256':sha(receipt),'role':'result'}
assert all(set(v)=={'path','sha256','role'} and v['role'] in ['source','input','result','log','diagnostic','artifact'] for v in rows.values())
raw.write_text(''.join(json.dumps(v,ensure_ascii=False)+'\n' for v in sorted(rows.values(),key=lambda v:v['path'])),encoding='utf-8')
print(json.dumps({'decision':'PASS','reviewer_stop':True,'receipt_sha256':sha(receipt),'raw_manifest_sha256':sha(raw),'bindings':len(rows),'seconds':round(time.monotonic()-started,3)},ensure_ascii=False))
