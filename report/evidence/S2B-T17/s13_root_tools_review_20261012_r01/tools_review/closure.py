"""只读收尾实际轻量流与旧失败原件；不重跑canary。"""
import ast
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

OUT=Path(__file__).absolute().parent
ROOT=OUT.parents[3]
WORK=ROOT/'tmp/2B/S2B-T17/s13_launch_prepare_20261012_r01'
REPORT=ROOT/'report/evidence/S2B-T17/s13_launch_tools_20261012_r01'
sys.path.insert(0,str(WORK))
import guard
import selftest
import compat_pins
def read(path): return json.loads(path.read_text(encoding='utf-8'))
def rows(path): return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
checks=[]
def check(label,success,**extra):
    checks.append(dict(case=label,pass_expected_behavior=bool(success),**extra))
    assert success,label

world=selftest.World(); monitor,root=selftest.monitor(world)
with patch.object(guard.psutil,'Process',world.process):
    members,unknown,exits=monitor.collect(root)
    child=next(row for row in members if row['pid']==200)
    original=monitor.event
    def after_event(kind,**details):
        original(kind,**details)
        if kind=='PRE_STOP_VERIFIED': world.nodes[200]['cmdline']=['临时漂移']
    monitor.event=after_event
    result=monitor.stop_one(child,root,'fixture')
check('stop_action_rechecks_after_event',result['status']=='BLOCKED' and not any(row['kind']=='TERMINATE_SENT' for row in monitor.events))

canary=WORK/'native_consumer_canary_r03'
consumed=rows(canary/'consumer'/'consumption.jsonl')
sup=rows(canary/'supervision'/'supervision.jsonl')
samples=rows(canary/'supervision'/'guard'/'samples.jsonl')
receipt=read(canary/'consumer'/'consumer_receipt.json')
supervised=read(canary/'supervision'/'supervisor_receipt.json')
guard_result=read(canary/'supervision'/'guard'/'guard_receipt.json')
readback=read(WORK/'native_consumer_canary_r03_result.json') if (WORK/'native_consumer_canary_r03_result.json').exists() else None
close=json.loads((WORK/'close_fixture_r03.stdout.bin').read_text(encoding='utf-8'))
live=[row for row in consumed if row['status']=='CONSUMED_LIVE_READY']
check('native_independent_live_rows',len(live)==3 and consumed[-1]['status']=='BLOCKED_RUNTIME_MONITOR',gaps=[row['actual_gap_seconds'] for row in consumed])
for previous,current in zip(consumed,consumed[1:]):
    check('actual_gap_record_'+str(current['index']),abs(current['actual_gap_seconds']-(current['monotonic_seconds']-previous['monotonic_seconds']))<1e-9)
check('actual_consumer_terminal2',receipt['native_exit_code']==2 and receipt['heavy_terminal']=='NOT_PROVEN' and close['consumer_native_exit_code']==2)
check('supervisor_actual_child2',supervised['child_native_exit_code']==2 and close['supervisor_native_exit_code']==2)
check('guard_stop_not_budgetpass',guard_result['status']=='STOPPED' and close['guard_native_exit_code']==2 and close['root_canary_native_exit_code'] is None)
check('known_standins_absent_only',all(row['same_identity_present'] is False for row in close['known_identity_readback']['observations']) and close['complete_tree_terminal']=='NOT_PROVEN')
check('canonical_capture_native0',read(OUT/'canonical_python_fixture.native.json')['native_exit_code']==0)
check('fixed_recovery_map',sha(REPORT/'archive_mapping.json')==compat_pins.MAPPING_SHA and sha(REPORT/'recovery_entry.json')==compat_pins.RECOVERY_SHA)
check('historical_fixture_failures_kept',all(read(WORK/(name+'.native.json'))['native_exit_code']==1 for name in ['guard_fixture_r01','monitor_fixture_r01','monitor_fixture_r02','monitor_fixture_r03']))
check('schema_failure_evidence2_kept',read(REPORT/'packaging_failure_r01'/'final_evidence_r01.native.json')['native_exit_code']==2)
author=read(REPORT/'author_receipt.json')
check('unknown_and_loop_limits_transparent',author['unknown_observation_count']==13 and author['absolute_tree_peak_bytes'] is None and author['complete_tree_terminal']=='NOT_PROVEN' and any('循环' in item for item in author['limitations']))
check('source_ready_stays_pending',author['SOURCE_COMMIT'] is None and compat_pins.SOURCE_COMMIT is None)
result=dict(status='PASS_TOOL_G2_ONLY',checks=checks,actual_consumer_gaps=[row['actual_gap_seconds'] for row in consumed],raw_history_not_reexecuted=True)
(OUT/'closure_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
