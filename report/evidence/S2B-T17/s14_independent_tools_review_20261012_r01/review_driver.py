"""S14独立只读审查：绑定原件并在自身目录运行冻结快照的轻量反例。"""
import ast
import contextlib
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

W = Path(__file__).resolve().parent
ROOT = W.parents[3]
D = ROOT / 'report/evidence/S2B-T17/s14_launch_tools_20261012_r01'
ORIGINAL = ROOT / 'tmp/2B/S2B-T17/s14_launch_prepare_20261012_r01'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):
    return json.loads(path.read_text(encoding='utf-8'))
def save(path, value):
    assert path.is_relative_to(W)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

assert 'S14_RUNTIME_CONFIG' not in os.environ
assert sha(D/'delivery_manifest_r02.json') == '0f74e386ac005c5e69fc01f41dd5dd25ef8cf73e93ed134f54a5e9f1cd1e98a3'
assert sha(D/'final_g1_receipt_r02.json') == 'b571281cafacc574ddeb00bfced23a9ef79b76448c2054aedf41ba3a6b2b4c61'
manifest = read(D/'delivery_manifest_r02.json')
receipt = read(D/'final_g1_receipt_r02.json')
bound = []
for row in manifest['files']:
    path = ROOT/row['path']
    assert path.is_file() and sha(path) == row['sha256'], str(path)
    bound.append(dict(path=row['path'], sha256=sha(path), bytes=path.stat().st_size))
tools = []
for row in receipt['tools']:
    path = Path(row['original_absolute_path'])
    archived = ROOT/row['archived_repo_path']
    assert path.parent == ORIGINAL and sha(path) == sha(archived) == row['sha256']
    assert path.stat().st_size == archived.stat().st_size == row['bytes']
    copied = W/path.name
    if not copied.exists():
        with copied.open('xb') as stream:
            stream.write(archived.read_bytes())
    assert sha(copied) == row['sha256']
    tools.append(dict(original=str(path), snapshot=str(copied), sha256=row['sha256']))
for row in receipt['diffs']:
    assert sha(ORIGINAL/row['path']) == sha(D/'raw'/row['path']) == row['sha256']
for row in receipt['native_records']:
    original = ROOT/row['path']
    assert sha(original) == row['sha256']
    record = read(original)
    assert record['native_exit_code'] == row['native_exit_code']
    for field in ('stdout','stderr'):
        log = record[field]
        assert sha(ROOT/log['path']) == log['sha256']
        assert (ROOT/log['path']).stat().st_size == log['bytes']
postcheck = read(ORIGINAL/'s14_evidence_check_r02.native.json')
assert postcheck['native_exit_code'] == 0
for field in ('stdout','stderr'):
    log = postcheck[field]
    assert sha(ROOT/log['path']) == log['sha256']
assert read(ORIGINAL/'s14_evidence_check_r02.stdout.bin')['status'] == 'CHECKS_OK'
save(W/'original_binding_checks.json', dict(status='PASS_BINDINGS_ONLY', files=bound, tools=tools,
     developer_native_records=receipt['native_records'],
     post_manifest_checker=dict(path=str(ORIGINAL/'s14_evidence_check_r02.native.json'), sha256=sha(ORIGINAL/'s14_evidence_check_r02.native.json'), native_exit_code=0, manifest_self_binding=False)))

# 快照导入保持原始字节；仅覆盖夹具落点，不改生产或被审原件。
sys.path.insert(0, str(W))
sys.argv = [str(W/'s14_regressions.py'), 'independent']
import guard
import selftest
import monitor_fixtures
import collector_fixtures
import s14_regressions as regression
import collector
import compat_pins
import launch_monitor
import runtime_consumer
import native_capture
import supervisor
assert sha(compat_pins.GUARD) == compat_pins.GUARD_SHA
assert sha(compat_pins.SUP) == compat_pins.SUP_SHA
assert supervisor.GUARD_SHA == compat_pins.GUARD_SHA
assert compat_pins.SOURCE_COMMIT is None and compat_pins._LOADED_CONFIG_SHA is None
for name in ('impl_collector.py','source_after_check.py'):
    tree = ast.parse((W/name).read_text(encoding='utf-8'))
    constant = next(n.value.value for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='COMMON_SHA')
    assert constant == sha(W/'collector.py')
for name in ('historical_member','record_sample_exit','stop_tree','stop_one','collect'):
    def function(path):
        return next(n for n in ast.walk(ast.parse(path.read_text(encoding='utf-8'))) if isinstance(n,ast.FunctionDef) and n.name==name)
    assert ast.dump(function(D/'baseline/guard.py')) == ast.dump(function(W/'guard.py'))
assert (W/'runtime_consumer.py').read_bytes() == (D/'baseline/runtime_consumer.py').read_bytes()

class IndependentBoundary(unittest.TestCase):
    def test_complete_invalid_utf8_refused(self):
        path = W/'invalid_utf8.jsonl'
        path.write_bytes(b'\xff\n')
        with patch.object(runtime_consumer,'complete', side_effect=AssertionError('无效UTF8不得调用解析器')):
            with self.assertRaises(UnicodeError):
                launch_monitor.startup_first_consumption(path)

    def test_newline_empty_refused(self):
        path = W/'empty_line.jsonl'
        path.write_bytes(b'\n')
        with patch.object(runtime_consumer,'complete', side_effect=AssertionError('空首行不得调用解析器')):
            with self.assertRaises(ValueError):
                launch_monitor.startup_first_consumption(path)

    def test_all_member_fields_rejected_after_parent_exit(self):
        for field,value in [('exe','其他.exe'),('cwd','其他目录'),('cmdline',['其他命令']),('ppid',0)]:
            world=selftest.World(); world.make(300,3,200,37)
            monitor,root=selftest.monitor(world)
            with patch.object(guard.psutil,'Process',world.process):
                first,unknown,_=monitor.collect(root); self.assertFalse(unknown)
                observed={(r['pid'],r['create_time']):r for r in first}
                chain=monitor.round_chain; reread=monitor.readback_member
                armed=[False]; changed=[False]
                def wrapper(item,bound,table):
                    result=chain(item,bound,table)
                    if item['pid']==300: armed[0]=True
                    return result
                def reader(expected):
                    if armed[0] and not changed[0] and expected['pid']==100:
                        changed[0]=True
                        world.nodes.pop(200)
                        world.nodes[300][field]=value
                    return reread(expected)
                monitor.round_chain=wrapper; monitor.readback_member=reader
                members,uncertain,exits=monitor.collect_round(root,observed)
                self.assertTrue(uncertain,field)

    def test_historical_cannot_stop_currently_unproved_member(self):
        world=selftest.World(); world.make(300,3,200,37)
        monitor,root=selftest.monitor(world)
        with patch.object(guard.psutil,'Process',world.process):
            members,unknown,_=monitor.collect(root); self.assertFalse(unknown)
            monitor.last_members.update({(r['pid'],r['create_time']):r for r in members})
            world.nodes.pop(200)
            members,unknown,_=monitor.collect(root); self.assertFalse(unknown)
            leaf=next(row for row in members if row['pid']==300)
            self.assertFalse(leaf['stoppable'])
            self.assertEqual(leaf['rss_bytes'],37)
            with self.assertRaises(guard.psutil.NoSuchProcess):
                monitor.verified_chain(leaf,root)

    def test_native_nonzero_preserved(self):
        with patch.object(sys,'argv',['native_capture.py','independent_native_nonzero',sys.executable,'-X','utf8','-B','-c','raise SystemExit(7)']), contextlib.redirect_stdout(io.StringIO()):
            code=native_capture.main(dict(mode='collect',prefix='s14_independent_nonzero'))
        native=read(W/'independent_native_nonzero.native.json')
        self.assertEqual(code,7); self.assertEqual(native['native_exit_code'],7)
        self.assertEqual(native['command'][-1],'raise SystemExit(7)')
        self.assertEqual(native['closed_logs'],[native['stdout'],native['stderr']])

suite = unittest.TestSuite()
for cls in [selftest.Semantics,monitor_fixtures.RoundSafety,monitor_fixtures.ConsumerSafety,collector_fixtures.Closure,collector_fixtures.Pairing,collector_fixtures.Config,regression.FinalParent,regression.Startup,regression.NativeSeal,IndependentBoundary]:
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
started=time.monotonic()
result=unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():
    save(W/'test_failure.json',dict(status='CHANGES_REQUIRED_OR_REVIEW_FIXTURE_FAILURE',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors)))
    raise SystemExit(1)
selftest.canary('independent_owned_threshold',True)
selftest.canary('independent_one_second_cadence',False)
monitor_fixtures.native_canary()
for row in tools:
    assert sha(Path(row['original'])) == sha(Path(row['snapshot'])) == row['sha256']
save(W/'test_receipt.json',dict(status='PASS_INDEPENDENT_LIGHT_CHECKS_ONLY',tests=result.testsRun,errors=0,failures=0,
      elapsed_seconds=time.monotonic()-started,source_hashes=tools,guard_cases=selftest.ROWS,monitor_cases=monitor_fixtures.ROWS,
      regression_cases=regression.ROWS,native_nonzero_code=7,actual_vivado=False,actual_ross=False,hardware=False,
      whole_os_tree_terminal='NOT_PROVEN',continuous_peak_bytes=None,production_source_freeze='NOT_RUN'))
print(json.dumps(dict(status='PASS_INDEPENDENT_LIGHT_CHECKS_ONLY',methods=result.testsRun,elapsed_seconds=time.monotonic()-started),ensure_ascii=False))
