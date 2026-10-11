"""轻量守护替身，不读取或操作任何目标PID。"""
from pathlib import Path
import sys,json,time
mode,binding_path,out=sys.argv[1:];directory=Path(out);directory.mkdir();binding=json.loads(Path(binding_path).read_text(encoding='utf-8'))
print('独立替身stdout原字节',flush=True);print('独立替身stderr原字节',file=sys.stderr,flush=True)
root=dict(binding)
if mode=='mismatch':root['create_time']+=1
row={'index':0,'members':[root],'alerts':['fixture_alert'] if mode=='alert' else [],'uncertain':[]}
(directory/'samples.jsonl').write_text(json.dumps(row,ensure_ascii=False)+'\n',encoding='utf-8')
time.sleep(5.25 if mode=='valid' else .25)
(directory/'guard_receipt.json').write_text(json.dumps({'status':'ROOT_EXITED' if mode=='valid' else 'BLOCKED','limitations':['只覆盖此前已知成员；轻量替身不探测任何目标PID。']},ensure_ascii=False),encoding='utf-8')
raise SystemExit(0 if mode=='valid' else 7 if mode=='mismatch' else 2)
