"""最后只核共同版本、固定门槛、schema数量及恢复绑定，绝不materialize实际输入。"""
import ast
import hashlib
import json
from pathlib import Path
import unittest
import collector_fixtures
import compat_pins as p
import guard
import supervisor

W=Path(__file__).parent;OLD=W.parents[3]/'tmp/2B/S2B-T17/s13_launch_prepare_20261012_r01'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert p.SOURCE_COMMIT is None and p._LOADED_CONFIG_SHA is None and not p.RUNTIME_CONFIG.exists()
for pnr in (False,True):
    try:p.require_ready(pnr)
    except ValueError as error:assert 'BLOCKED_PENDING_S14_PINS' in str(error)
    else:raise AssertionError('未冻结SOURCE不能通过')
assert sha(p.GUARD)==p.GUARD_SHA==supervisor.GUARD_SHA and sha(p.SUP)==p.SUP_SHA
for name in ('historical_member','record_sample_exit','stop_tree','stop_one','collect'):
    def function(path):return next(n for n in ast.walk(ast.parse(path.read_text(encoding='utf-8'))) if isinstance(n,ast.FunctionDef) and n.name==name)
    assert ast.dump(function(OLD/'guard.py'))==ast.dump(function(W/'guard.py')),name
assert (W/'runtime_consumer.py').read_bytes()==(OLD/'runtime_consumer.py').read_bytes()
suite=unittest.TestSuite([collector_fixtures.Closure('test_actual_count_not_fixed43'),collector_fixtures.Closure('test_hard_requirements'),collector_fixtures.Config('test_pending_refused'),collector_fixtures.Config('test_parse_and_common_fixed')])
result=unittest.TextTestRunner(verbosity=2).run(suite);assert result.wasSuccessful()
source=ast.parse((W/'source_after_check.py').read_text(encoding='utf-8'))
records=[n for n in ast.walk(source) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='dict']
record=next(n for n in records if any(k.arg=='schema_version' for k in n.keywords))
fields={k.arg:ast.unparse(k.value) for k in record.keywords}
assert fields['source_count']=='len(hashes)' and fields['platform_static_source_count']=='len(static)'
with (W/'final_binding_checks_result.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump(dict(status='PASS_G1_BINDINGS_ONLY',methods=result.testsRun,source_commit=None,actual_runtime='NOT_RUN',source_freeze='NOT_RUN',guard_sha256=p.GUARD_SHA,supervisor_sha256=p.SUP_SHA,consumer_unchanged=True,stopping_kernel_and_collect_max3_twoalive_unchanged=True,source_after_count_derived=True),stream,ensure_ascii=False,indent=2);stream.write('\n')
