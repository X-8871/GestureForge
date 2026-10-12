"""R2隔离布局、防覆盖及完整工具审查绑定回归；不消费真实SOURCE批准。"""
import ast,contextlib,hashlib,json
from pathlib import Path
from unittest.mock import patch
import collector as c
import compat_pins as pins
import native_contract as contract
W=Path(__file__).parent;ROOT=W.parents[3];F=W/'extra_fixtures_r01';F.mkdir();ROWS=[]
def save(p,value):
    with p.open('x',encoding='utf-8',newline='\n') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
def reject(function):
    try:function()
    except (ValueError,KeyError,TypeError):return
    raise AssertionError('反例被接受')
def check(name,function):
    function();ROWS.append(dict(case=name,status='PASS'))
COMMIT='b'*40
PRE=F/'pre';REPORT=F/'report';PROJECT=F/'project';FREEZE=F/'freeze.json'
save(FREEZE,dict(fixture_test=True,frozen14={}))
with contextlib.ExitStack() as stack:
    for name,value in [('PRE',PRE),('REPORT',REPORT),('PROJECT',PROJECT),('FREEZE',FREEZE),('FREEZE_SHA',c.sha(FREEZE)),('CACHE',F)]:stack.enter_context(patch.object(c,name,value))
    stack.enter_context(patch.object(pins,'SOURCE_COMMIT',COMMIT));stack.enter_context(patch.object(pins,'require_ready'))
    stack.enter_context(patch.object(c,'load_freeze',return_value=(dict(frozen14={}),{},{},dict(version='s2b-inference-platform/0.1.15'))))
    stack.enter_context(patch.object(c,'git',side_effect=lambda *args:((COMMIT+'\n').encode() if args==('rev-parse','HEAD') else b'',list(args))))
    check('source_before_fresh_creates_pre_and_report_fixture',lambda:c.source(COMMIT,'before'))
    assert PRE.is_dir() and REPORT.is_dir() and not PROJECT.exists()
    original=c.binding(PRE/'source_before.json')
    check('source_before_existing_pre_report_rejected_without_overwrite',lambda:reject(lambda:c.source(COMMIT,'before')))
    assert c.binding(PRE/'source_before.json')==original
    PROJECT.mkdir()
    check('source_after_existing_fresh_layout_fixture',lambda:c.source(COMMIT,'after'))
    after=c.binding(PRE/'source_after.json')
    check('source_after_existing_snapshot_rejected_without_overwrite',lambda:reject(lambda:c.source(COMMIT,'after')))
    assert c.binding(PRE/'source_after.json')==after
    FAILED=F/'failed';FAILED.mkdir();FPRE=FAILED/'pre';FREPORT=FAILED/'report'
    save(FAILED/'deliberate_failure.json',dict(fixture_test=True,reason='模拟第二个目录创建失败；保留已创建PRE'))
    native_fresh=c.fresh
    def failing_fresh(path,directory=False):
        if path==FREPORT:raise ValueError('fixture目录创建失败')
        return native_fresh(path,directory)
    with patch.object(c,'PRE',FPRE),patch.object(c,'REPORT',FREPORT),patch.object(c,'PROJECT',FAILED/'project'),patch.object(c,'fresh',side_effect=failing_fresh):
        check('source_before_creation_failure_preserves_new_pre',lambda:reject(lambda:c.source(COMMIT,'before')))
        assert FPRE.is_dir() and not FREPORT.exists()
actual=contract.capture_tools(W,ROOT);review=F/'review_fixture.json'
save(review,dict(status='PASS_FIXTURE_ONLY',reviewed_tools=actual,fixture_test=True))
with patch.object(pins,'TOOLS_G2',review),patch.object(pins,'TOOLS_G2_SHA',c.sha(review)),patch.object(pins,'TOOLS_G2_EXPECTED_STATUS','PASS_FIXTURE_ONLY'):
    check('complete_tool_review_hash_schema_fixture',lambda:c.expected_tool_bindings())
    native_read=c.read
    for label,declared in [('missing',actual[:-1]),('duplicate',actual+[actual[0]]),('hash_changed',[dict(actual[0],sha256='d'*64),*actual[1:]])]:
        with patch.object(c,'read',side_effect=lambda p,declared=declared:dict(status='PASS_FIXTURE_ONLY',reviewed_tools=declared) if p==review else native_read(p)):
            check('reject_review_tool_'+label,lambda:reject(c.expected_tool_bindings))
check('all_python_ast',lambda:[ast.parse(p.read_text(encoding='utf-8')) for p in W.glob('*.py')])
check('pending_actual_source_tools_functional',lambda:reject(pins.require_ready))
assert pins.SOURCE_COMMIT is None and pins.TOOLS_G2_SHA is None and pins.FUNCTIONAL_G2_SHA is None
assert c.sha(W/'guard.py')==pins.GUARD_SHA and c.sha(W/'supervisor.py')==pins.SUP_SHA
for name in ['impl_collector.py','source_after_check.py']:
    assert "COMMON_SHA='"+c.sha(W/'collector.py')+"'" in (W/name).read_text(encoding='utf-8')
save(W/'extra_regression_result.json',dict(status='PASS_G1_ONLY',methods=len(ROWS),cases=ROWS,fixture_test=True,source_approval=None,tools_g2=None,limitations=['布局与审查记录使用显式隔离fixture；没有运行真实生产源码核验。']))
print(json.dumps(dict(status='PASS_G1_ONLY',methods=len(ROWS)),ensure_ascii=False))
