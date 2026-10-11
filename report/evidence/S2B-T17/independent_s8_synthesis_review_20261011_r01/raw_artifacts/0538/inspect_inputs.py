"""只读列出审查证据结构，避免打印大段重复日志。"""
from pathlib import Path
import json
base=Path.cwd()/'report/evidence/S2B-T17/s8_platform_20261011_r01'
for name in ['s8_mcp_binding.json','s8_native_mapping.json','s8_original_inventory.json','root_closed/root_closed_gate.json','mcp_closed/mcp_history.json','mcp_closed/mcp_wait.json','mcp_closed/mcp_close.json','root_closed_r02/evidence.native.json']:
    p=base/name
    if not p.is_file(): print(name,'ABSENT'); continue
    obj=json.loads(p.read_text(encoding='utf-8'))
    print(name, 'KEYS',list(obj) if isinstance(obj,dict) else 'LIST '+str(len(obj)))
    if name=='s8_mcp_binding.json':
        for row in obj['paired_calls']:
            print('ROW', {k:v for k,v in row.items() if k not in ['native_history','client_record']},'native', {k:v for k,v in row['native_history'].items() if k not in ['output','command']})
        print('binding extras', {k:v for k,v in obj.items() if k not in ['paired_calls','all_host_tool_calls']})
    elif name=='s8_native_mapping.json':
        for k,v in obj.items(): print(k,str(v)[:1400])
    elif name=='root_closed/root_closed_gate.json':
        for k,v in obj.items(): print(k,str(v)[:1800])
    elif name.endswith('mcp_history.json'):
        if 'result' in obj:
            text=obj['result']['content'][0]['text']; print('history text prefix',text[:1500]); history=json.loads(text)
            print('decoded_history_keys',list(history) if isinstance(history,dict) else 'LIST')
            history=history.get('commands',history.get('history',[])) if isinstance(history,dict) else history
        else: history=obj.get('history',obj.get('commands',[])) if isinstance(obj,dict) else obj
        for row in history: print('history', {k:v for k,v in row.items() if k!='output'})
    elif name.endswith('mcp_wait.json'): print(str(obj)[:9000])
    else: print(str(obj)[:1500])
print('native_jobs files',[(p.relative_to(base).as_posix(),p.stat().st_size) for p in (base/'native_jobs').rglob('*') if p.is_file()])
