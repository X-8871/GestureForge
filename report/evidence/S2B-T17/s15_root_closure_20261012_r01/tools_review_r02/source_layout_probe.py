"""独立布局与防覆盖验证，仅用隔离逻辑fixture，不冻结生产SOURCE。"""
import contextlib
import json
from pathlib import Path
import sys
from unittest.mock import patch
HERE=Path(__file__).parent;ROOT=HERE.parents[3];W=ROOT/'tmp/2B/S2B-T17/s15_launch_prepare_20261012_r02'
sys.path.insert(0,str(W))
import collector as c
import compat_pins as pins
F=HERE/'source_layout_fixture';F.mkdir()
PRE=F/'pre';REPORT=F/'report';PROJECT=F/'project';FREEZE=F/'freeze.json';COMMIT='b'*40
FREEZE.write_text(json.dumps(dict(fixture_test=True,frozen14={})),encoding='utf-8')
checks=[]
with contextlib.ExitStack() as stack:
    for name,value in [('PRE',PRE),('REPORT',REPORT),('PROJECT',PROJECT),('FREEZE',FREEZE),('FREEZE_SHA',c.sha(FREEZE)),('CACHE',F)]:stack.enter_context(patch.object(c,name,value))
    stack.enter_context(patch.object(pins,'SOURCE_COMMIT',COMMIT));stack.enter_context(patch.object(pins,'require_ready'))
    stack.enter_context(patch.object(c,'load_freeze',return_value=(dict(frozen14={}),{},{},dict(version='s2b-inference-platform/0.1.15'))))
    stack.enter_context(patch.object(c,'git',side_effect=lambda *args:((COMMIT+'\n').encode() if args==('rev-parse','HEAD') else b'',list(args))))
    with contextlib.redirect_stdout(__import__('io').StringIO()):c.source(COMMIT,'before')
    checks.append(dict(name='fresh_before_creates_PRE_REPORT',passed=PRE.is_dir() and REPORT.is_dir() and not PROJECT.exists()))
    original=c.binding(PRE/'source_before.json')
    try:c.source(COMMIT,'before');rejected=False
    except ValueError:rejected=True
    checks.append(dict(name='existing_before_rejected_preserves_original',passed=rejected and c.binding(PRE/'source_before.json')==original))
    PROJECT.mkdir()
    with contextlib.redirect_stdout(__import__('io').StringIO()):c.source(COMMIT,'after')
    after=c.binding(PRE/'source_after.json')
    checks.append(dict(name='fresh_after_valid_in_existing_layout',passed=after['bytes']>0))
    try:c.source(COMMIT,'after');rejected=False
    except ValueError:rejected=True
    checks.append(dict(name='existing_after_rejected_preserves_original',passed=rejected and c.binding(PRE/'source_after.json')==after))
assert pins.SOURCE_COMMIT is None
with (HERE/'source_layout_probe_result.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump(dict(status='PASS_FIXTURE_ONLY' if all(r['passed'] for r in checks) else 'FAIL',checks=checks,actual_source_approval=False),stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps(dict(checks=checks,actual_source_approval=False),ensure_ascii=False))
