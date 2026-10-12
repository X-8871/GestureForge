"""独立只读工具审查；模拟进程不触及实际守卫或生产源。"""
import ast
import copy
from datetime import datetime, timezone, timedelta
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

OUT = Path(__file__).absolute().parent
ROOT = OUT.parents[3]
WORK = ROOT / 'tmp/2B/S2B-T17/s13_launch_prepare_20261012_r01'
REPORT = ROOT / 'report/evidence/S2B-T17/s13_launch_tools_20261012_r01'
sys.path.insert(0, str(WORK))
import guard
import selftest
import runtime_consumer as consumer
import collector
import collector_fixtures
import compat_pins as pins
import native_capture

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

ROWS = []
def check(label, result, **details):
    ROWS.append(dict(case=label, pass_expected_behavior=bool(result), **details))
    if not result:
        print('FINDING '+label, flush=True)

EXPECTED = {'delivery_manifest_r02.json':'c8352fd913bd8bc1448fb05ffd78803438c4c6e6a6e99887f542d151721b0ece', 'author_receipt.json':'9b4d6f091d05ac31b52064f795c8335cdb957abc68bfab89e212b47a13dc6344', 'raw_mapping.json':'ec18dc0541539aa579fa9644bdc3c9d2b31e9014b21b58a192e2d2377a8392d7'}
for name, expected in EXPECTED.items():
    check('binding_'+name, sha(REPORT/name)==expected, actual_sha256=sha(REPORT/name))
for name, expected in {'guard.py':'056cbd06289490589f17f70076046eb2811a4a256edb0ccd8d2b19b2537bff07','supervisor.py':'7438201f3fa38fe84daaa3203634ec532f3f4069f6a13bfb155db9d055fe6325','runtime_consumer.py':'8e8d3f4d19ceeafa1a3894941a77e8839a5f6559760d114b826518ef7289df0b','collector.py':'8daa418df39e8306f000b27dda7b140fe0a837c796226571b955a0d609baeacd'}.items():
    check('tool_'+name, sha(WORK/name)==expected and sha(REPORT/'tools'/name)==expected)
manifest = read(REPORT/'delivery_manifest_r02.json')
bad = []
for row in manifest['files']:
    path = ROOT/row['path']
    if not path.is_file() or sha(path)!=row['sha256']:
        bad.append(row['path'])
check('all_manifest_files', not bad, count=len(manifest['files']), mismatch=bad)
for name in ('raw_mapping.json','archive_mapping.json'):
    bad=[]; mappings=read(REPORT/name)['binding_rows']
    for row in mappings:
        for path in (Path(row['original_absolute_path']),ROOT/row['archived_repo_path']):
            if not path.is_file() or sha(path)!=row['sha256'] or path.stat().st_size!=row['bytes']:
                bad.append(str(path))
    check('original_archive_'+name, not bad, count=len(mappings), mismatch=bad)

def functions(path):
    tree=ast.parse(path.read_text(encoding='utf-8'))
    result={}
    for node in tree.body:
        if isinstance(node,ast.FunctionDef): result[node.name]=ast.dump(node,include_attributes=False)
        if isinstance(node,ast.ClassDef):
            result.update({node.name+'.'+item.name:ast.dump(item,include_attributes=False) for item in node.body if isinstance(item,ast.FunctionDef)})
    return result
old,new=functions(REPORT/'baseline'/'guard.py'),functions(WORK/'guard.py')
changed=[k for k in old if old[k]!=new.get(k)]
added=sorted(set(new)-set(old))
check('guard_minimal_ast', changed==['Guard.collect_round'] and added==['Guard.round_ancestor_readback','Guard.round_chain','Guard.round_identity'], changed=changed,added=added)

for field,value in (('exe','异.exe'),('cwd','异目录'),('cmdline',['异命令']),('ppid',0)):
    world=selftest.World(); monitor,root=selftest.monitor(world); original=monitor.round_chain
    def mutate(item,root,table):
        result=original(item,root,table); world.nodes[200][field]=value; return result
    monitor.round_chain=mutate
    with patch.object(guard.psutil,'Process',world.process):
        members,unknown,exits=monitor.collect(root)
    check('final_drift_'+field,bool(unknown) and not monitor.collection_observation['closed'])
for target in (100,200):
    world=selftest.World(); monitor,root=selftest.monitor(world); original=monitor.round_chain
    def deny(item,root,table):
        result=original(item,root,table); world.fail[(target,'exe')]=guard.psutil.AccessDenied(target); return result
    monitor.round_chain=deny
    with patch.object(guard.psutil,'Process',world.process):
        result=monitor.collect(root)
    check('final_access_denied_'+str(target),bool(result[1]) and not monitor.collection_observation['closed'])
world=selftest.World(); monitor,root=selftest.monitor(world)
with patch.object(guard.psutil,'Process',world.process):
    first=monitor.collect(root); monitor.last_members={(row['pid'],row['create_time']):row for row in first[0]}
    world.nodes[200]['rss_bytes']=777
    second=monitor.collect(root)
check('no_cross_round_rss_cache',not second[1] and sum(row['rss_bytes'] for row in second[0])==787)
world=selftest.World(); monitor,root=selftest.monitor(world); world.make(300,3,200,30)
with patch.object(guard.psutil,'Process',world.process):
    first=monitor.collect(root); monitor.last_members={(row['pid'],row['create_time']):row for row in first[0]}
    world.make(200,88,100,40)
    second=monitor.collect(root)
check('ancestor_reused_failclosed',bool(second[1]))

def good():
    root=dict(pid=10,create_time=1,exe='fixture',cwd='fixture',cmdline=['fixture'],ppid=1)
    owned=dict(root,pid=20,ppid=10)
    journal=[dict(kind='READY',guard_identity=owned),dict(kind='LIVE',identity=owned,monotonic_seconds=time.monotonic())]
    sample=dict(members=[root],alerts=[],uncertain=[],collection_observation={'closed':True},sample_ended_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),tree_rss_bytes=1,available_ram_bytes=512*1024**2,c_disk_free_bytes=8*1024**3)
    return [journal,[sample],root,owned,[{'mtime_age_seconds':0},{'mtime_age_seconds':0}],5]
check('consumer_valid',consumer.evaluate(*good())==[])
for mode in ('alerts_absent','uncertain_wrong_type','closed_false','terminal','sample_stale','live_stale','mtime_stale','gap_stale','rss_bool','ram_low','disk_low'):
    args=good(); sample=args[1][0]
    if mode=='alerts_absent': del sample['alerts']
    elif mode=='uncertain_wrong_type': sample['uncertain']={}
    elif mode=='closed_false': sample['collection_observation']['closed']=False
    elif mode=='terminal': args[0].append(dict(kind='TERMINAL'))
    elif mode=='sample_stale': sample['sample_ended_at_utc8']=(datetime.now(timezone(timedelta(hours=8)))-timedelta(seconds=11)).isoformat()
    elif mode=='live_stale': args[0][-1]['monotonic_seconds']-=11
    elif mode=='mtime_stale': args[4][0]['mtime_age_seconds']=11
    elif mode=='gap_stale': args[5]=11
    elif mode=='rss_bool': sample['tree_rss_bytes']=True
    elif mode=='ram_low': sample['available_ram_bytes']-=1
    elif mode=='disk_low': sample['c_disk_free_bytes']-=1
    check('consumer_'+mode,bool(consumer.evaluate(*args)))
args=good(); args[5]=5.1
check('consumer_target5_hard10',consumer.evaluate(*args)==[] and consumer.TARGET_SECONDS==5 and consumer.FRESHNESS_SECONDS==10)
for key in consumer.KEYS:
    args=good(); args[0][-1]['identity']=dict(args[3]); args[0][-1]['identity'][key]='drift'
    check('consumer_identity_'+key,bool(consumer.evaluate(*args)))
with patch.object(consumer,'identity',side_effect=guard.psutil.AccessDenied(10)):
    check('stop_unknown_rejected',consumer.request_stop(good()[3],good()[2],str(OUT))['status']=='STOP_REJECTED_IDENTITY_OR_PATH')
for pnr in (False,True):
    try: pins.require_ready(pnr); refused=False
    except ValueError: refused=True
    check('pending_source_gate_'+str(pnr),refused and pins.SOURCE_COMMIT is None)
for name,raw in (('duplicate','{"SOURCE_COMMIT":null,"SOURCE_COMMIT":null}'),('extra',json.dumps(dict.fromkeys(pins._CONFIG_FIELDS,None)|{'GUARD_SHA':'a'*64}))):
    path=OUT/(name+'.json'); path.write_text(raw,encoding='utf-8')
    with patch.object(pins,'RUNTIME_CONFIG',path):
        try: pins.load_runtime_config(); refused=False
        except ValueError: refused=True
    check('config_'+name,refused)
for count in (43,44):
    check('closure_actual_'+str(count),len(collector_fixtures.Closure().run_closure(count)[1])==count)
for mode in ('runner','profile','rtl','clock'):
    try: collector_fixtures.Closure().run_closure(broken=mode); refused=False
    except ValueError: refused=True
    check('closure_reject_'+mode,refused)
call=dict(input=dict(session_id='ownfixture',command='wait_on_run synth_1'),result=dict(content=[dict(type='text',text=json.dumps(dict(status='running',session_id='ownfixture',command='wait_on_run synth_1')))]))
item=dict(command='wait_on_run synth_1',code=0)
paired=collector.client_pair(item,'wait',call)
check('running_client_null_history0',paired['client_running_handoff'] and paired['client_exit_code'] is None and item['code']==0)
for mode in ('wrongsession','wrongcommand','claimedexit','historyunknown','nonwait'):
    broken=copy.deepcopy(call); payload=json.loads(broken['result']['content'][0]['text']); hist=dict(item); label='wait'
    if mode=='wrongsession': payload['session_id']='foreign'
    elif mode=='wrongcommand': payload['command']='wait_on_run impl_1'
    elif mode=='claimedexit': payload['exit_code']=0
    elif mode=='historyunknown': hist['code']=None
    else: label='launch'
    broken['result']['content'][0]['text']=json.dumps(payload)
    try: collector.client_pair(hist,label,broken); refused=False
    except ValueError: refused=True
    check('client_reject_'+mode,refused)

# 规范解释器启动是已授权的轻量模式；审查包装本身不发实际子命令。
with patch.object(sys,'argv',[str(WORK/'native_capture.py'),'canonical_python_fixture',sys.executable,'-X','utf8','-B',str(WORK/'collector.py'),'--help']):
    try:
        with patch.object(native_capture,'HERE',OUT): native_capture.main()
        capture_accepts=True; capture_error=None
    except AssertionError as error:
        capture_accepts=False; capture_error=repr(error)
check('canonical_python_native_capture',capture_accepts,actual_sys_executable=sys.executable,error=capture_error)

result=dict(status='PASS_TOOL_G2_ONLY' if all(row['pass_expected_behavior'] for row in ROWS) else 'CHANGES_REQUIRED',checks=ROWS,python=sys.version,psutil=guard.psutil.__version__,review_identity=dict(pid=guard.psutil.Process().pid,create_time=guard.psutil.Process().create_time()),production_reads=False,heavy_or_hardware=False,reviewed_manifest_sha256=EXPECTED['delivery_manifest_r02.json'])
(OUT/'independent_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=result['status'],checks=len(ROWS),findings=[row for row in ROWS if not row['pass_expected_behavior']]),ensure_ascii=False))
raise SystemExit(0 if result['status']=='PASS_TOOL_G2_ONLY' else 1)
