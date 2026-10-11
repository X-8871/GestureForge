"""独立只读绑定核验及最小合成反例，不执行Git、Tcl或硬件。"""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import psutil

ROOT = Path(__file__).parents[4]
OUT = Path(__file__).parent
WORK = ROOT/'tmp/2B/S2B-T17/s12_physical_compat_prepare_20261012_r01'
started = time.monotonic()
peak = 0
def sample():
    """采集本进程RSS，绝对连续峰未知。"""
    global peak
    peak = max(peak, psutil.Process().memory_info().rss)
    assert peak < 134217728
def digest(path):
    """流式读取原字节，避免累积大输入。"""
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(65536), b''):
            h.update(block)
    return h.hexdigest()
def dump(path, obj):
    """隔离目录只创建新文件。"""
    assert path.is_relative_to(OUT)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')
def read(path):
    return json.loads(path.read_text(encoding='utf-8'))
manifest = WORK/'raw_manifest.jsonl'
assert digest(manifest)=='448666a160722be83767ba53a775695e515f3df918cef490141c6a47545d1166'
seen=set(); total=0; count=0
for line in manifest.read_text(encoding='utf-8').splitlines():
    row=json.loads(line); path=WORK/row['path']
    assert row['path'] not in seen and str(path)==row['absolute_path']
    seen.add(row['path'])
    assert path.is_file() and not path.is_symlink() and not path.is_junction()
    assert path.stat().st_size==row['bytes'] and digest(path)==row['sha256'], row['path']
    total+=row['bytes']; count+=1; sample()
assert count==1836
entry=read(WORK/'final_draft_binding.json')
for row in entry['files']:
    path=WORK/row['path']
    assert path.stat().st_size==row['bytes'] and digest(path)==row['sha256']
    ast.parse(path.read_text(encoding='utf-8'))
for row in read(WORK/'input_bindings.json'):
    path=ROOT/row['path']
    assert str(path)==row['absolute_path'] and path.is_file()
    assert path.stat().st_size==row['bytes'] and digest(path)==row['sha256']
sys.path.insert(0,str(WORK))
import compat_pins as p
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
impl=module('independent_impl',WORK/'impl_collector.py')
after=module('independent_after',WORK/'source_after_check.py')
recovery=[p.resolve_permanent(p.GUARD,p.GUARD_SHA),p.resolve_permanent(p.SUP,p.SUP_SHA)]
archive=p.ARCHIVE/'delivery_manifest_r02.json'
assert digest(archive)=='139d5b72f9faa0bb58943b0dcff0d5e70ebcd8d189246e061a4df6013f8c3dce'
results=[]
try:
    p.require_ready()
except ValueError as exc:
    assert 'BLOCKED_PENDING_S12_PINS' in str(exc)
    results.append(dict(name='真实pins缺失',outcome='REJECTED_EXPECTED',exception=str(exc)))
else:
    raise AssertionError('缺失pins错误接受')
old_ready=p.require_ready; old_commit=impl.COMMIT
p.require_ready=lambda pnr=False: None
impl.COMMIT='0'*40
base=WORK/'fixtures/history/valid_no_invalid'
original=read(base/'gate.json')
def counterexample(label,code):
    """只替换合成history及其匹配客户端码，保留全部真实哈希门禁。"""
    case=OUT/(label+'_'+str(code)); case.mkdir()
    gate=copy.deepcopy(original)
    history=impl.c.mcp_json(read(base/'history.json'))['history']
    index=next(i for i,r in enumerate(gate['design_mcp_records']) if r['label']==label)
    history[index]['code']=code
    call=read(ROOT/gate['design_mcp_records'][index]['path'])
    call['result']['content'][0]['text']=json.dumps(dict(exit_code=code))
    call_path=case/'call.json'; dump(call_path,call)
    row=impl.c.binding(call_path); row.update(id=history[index]['id'],label=label)
    gate['design_mcp_records'][index]=row
    hist_path=case/'history.json'
    dump(hist_path,dict(fixture_test=True,content=[dict(type='text',text=json.dumps(dict(history=history)))]))
    gate['mcp_history']=impl.c.binding(hist_path)
    gate_path=case/'gate.json'; dump(gate_path,gate)
    try:
        _,paired=impl.closed_gate(gate_path)
        results.append(dict(name=label+' native '+repr(code),outcome='ACCEPTED_BAD_SYNTHETIC',paired_codes={r['label']:r['history']['code'] for r in paired},gate=gate_path.relative_to(ROOT).as_posix()))
    except ValueError as exc:
        results.append(dict(name=label+' native '+repr(code),outcome='REJECTED',exception=str(exc)))
try:
    for label in ('launch','wait','open_run','reports','close'):
        for code in (1,None,False,0.0,'0'):
            counterexample(label,code)
finally:
    p.require_ready=old_ready; impl.COMMIT=old_commit
for blob,raw,expected in [(b'A\nB\n',b'A\r\nB\r\n','GIT_LF_TO_RAW_CRLF'),(b'A\r\nB\n',b'A\r\nB\r\n','REJECTED'),(b'A\n',b'A\r\n\x00','REJECTED')]:
    try:
        actual=after.compare_raw(blob,raw)
    except ValueError:
        actual='REJECTED'
    assert actual==expected
    results.append(dict(name='独立RAW手算',blob_hex=blob.hex(),raw_hex=raw.hex(),outcome=actual))
sample()
receipt=dict(status='CHANGES_REQUIRED',scope='COMPAT_LOGIC_ONLY',manifest_sha256=digest(manifest),raw_files_verified=count,raw_input_bytes=total,source_entry_sha256=digest(WORK/'final_draft_binding.json'),receipt_sha256=digest(WORK/'compatibility_delivery_receipt.json'),pending_sha256=digest(WORK/'pending_pins.json'),fixed_restore_manifest_sha256=digest(archive),recovery=recovery,cases=results,elapsed_seconds=time.monotonic()-started,sampled_self_rss_peak_bytes=peak,absolute_peak_bytes=None,actual_git_calls=0,actual_tcl_calls=0,hardware_vivado_ross=False,source_commit=None,physical_g0='BLOCKED',old_s11_budget='BLOCKED',sta='NOT_RUN',g3='NOT_RUN',g5='NOT_RUN')
dump(OUT/'independent_result.json',receipt)
print(json.dumps(receipt,ensure_ascii=False))
