import json
from pathlib import Path
ROOT = Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition')
P = ROOT / 'report/evidence/S2B-T17/s15_postroute_20261012_r01'
def brief(path):
    d = json.loads(path.read_text(encoding='utf-8'))
    print(str(path.relative_to(P)), 'keys=', list(d))
    for k,v in d.items():
        if isinstance(v,list):
            print(k, 'count=',len(v), 'first=',str(v[:1])[:1200])
        elif isinstance(v,dict):
            print(k, 'keys=',list(v))
        elif isinstance(v,(str,int,bool,float)) or v is None:
            print(k, str(v)[:180])
for rel in ['native_capture_closed/source_freeze_r01.json','raw_root/closed_runtime_observation.json','native_capture_closed/prepared_receipt_r04.json','raw_root/source_before_pnr.native.json','raw_root/source_after_pnr_r02.native.json','raw_root/r02_terminal_receipt.json','delivery_manifest_r03.json']:
    brief(P/rel)
print('NATIVE JOBS', [str(x.relative_to(P)) for x in (P/'native_jobs').rglob('*') if x.is_file()])
print('PACKHISTORY', [str(x.relative_to(P)) for x in (P/'packaging_history').rglob('*') if x.is_file()])
for r in ['raw_root/history_full.tool.json','raw_root/setup.tool.json','raw_root/open_project.tool.json','raw_root/stop.tool.json','raw_root/wait.tool.json']:
    d=json.loads((P/r).read_text(encoding='utf-8'))
    d=d.get('result',d)
    texts=[json.loads(c['text']) if c['text'].startswith('{') else c['text'] for c in d.get('content',[]) if c.get('type')=='text']
    if 'history' in str(texts[:1]) and isinstance(texts[0],dict) and 'history' in texts[0]:
        print('HISTORY',json.dumps([{k:v for k,v in x.items() if k!='output'} for x in texts[0]['history']], ensure_ascii=False))
    else: print(r,str(texts)[:4000])
