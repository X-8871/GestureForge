"""只读输出 S6 所需字段，避免打印完整累计诊断。"""
from pathlib import Path
import json, re, sys
ROOT = Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition')
CACHE = ROOT / 'tmp/2B/S2B-T17/s6_root_run_20261011_r01'
sys.stdout.reconfigure(encoding='utf-8')
def read(p):
    """读取精确目标。"""
    assert p.is_file() and not p.is_symlink(), p
    return json.loads(p.read_text(encoding='utf-8'))
history = [h for b in read(CACHE / 'mcp_history.json')['content'] if b['type'] == 'text' for h in json.loads(b['text']).get('history', [])]
for h in history:
    print(json.dumps({k:v for k,v in h.items() if k != 'output'}, ensure_ascii=False))
    if h['id'] in (5,8): print('OUTPUT',h['output'])
for name in ('resource_preflight.json','resource_during_synthesis_01.json','source_before.native.json','source_after.native.json','mcp_status_after_wait.json'):
    print(name, json.dumps(read(CACHE/name), ensure_ascii=False))
after=read(ROOT/'report/evidence/S2B-T17/s6_source_preflight_20261011_r01/source_after.json')
print('AFTER_KEYS',list(after))
freeze=read(ROOT/after['source_freeze'])
print('FREEZE_KEYS',list(freeze))
print('FREEZE_META',{k:v for k,v in freeze.items() if k not in ('source_sha256','frozen14_sha256')})
log=(CACHE/'root_session_snapshot.log').read_text(encoding='utf-8')
print('ROOT_PEAK',max(map(float,re.findall(r'peak = ([0-9.]+)',log))))
