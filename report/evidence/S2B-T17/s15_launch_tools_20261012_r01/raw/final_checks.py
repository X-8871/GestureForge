"""最终工具pin、动作前完整归属、失败后已知身份只读关闭核验。"""
import ast
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import compat_pins as pins
import native_capture as n
import collector as c
import guard

W=Path(__file__).parent

class Bindings(unittest.TestCase):
    def test_tools_match_actual_pins(self):
        import supervisor
        self.assertEqual(supervisor.GUARD_SHA,pins.GUARD_SHA)
        for path,digest in [(pins.GUARD,pins.GUARD_SHA),(pins.SUP,pins.SUP_SHA)]:
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),digest)
            row=pins.resolve_permanent(path,digest)
            self.assertEqual(row['sha256'],digest)
        for name in ('impl_collector.py','source_after_check.py'):
            tree=ast.parse((W/name).read_text(encoding='utf-8'))
            values={a.targets[0].id:ast.literal_eval(a.value) for a in tree.body if isinstance(a,ast.Assign) and isinstance(a.targets[0],ast.Name) and isinstance(a.value,ast.Constant)}
            self.assertEqual(values['COMMON_SHA'],c.sha(W/'collector.py'))

    def test_all_tools_parse_utf8(self):
        for p in W.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))

    def test_actual_source_pending(self):
        self.assertIsNone(pins.SOURCE_COMMIT)
        self.assertFalse(pins.RUNTIME_CONFIG.exists())
        self.assertIsNone(pins.FUNCTIONAL_G2_SHA);self.assertIsNone(pins.TOOLS_G2_SHA)
        with self.assertRaises(ValueError):pins.require_ready()

    def test_budget_stop_full_identity_and_parent(self):
        launcher=dict(pid=100,create_time=1,exe='wrapper',cwd='cwd',cmdline=['wrapper'],ppid=0)
        child=dict(pid=200,create_time=2,exe='child',cwd='cwd',cmdline=['child'],ppid=100)
        with patch.object(n,'read_identity',return_value=dict(same_identity_exists=True)):
            self.assertTrue(n.owned_child_action_ready(child,launcher))
            self.assertFalse(n.owned_child_action_ready(dict(child,ppid=999),launcher))
            self.assertFalse(n.owned_child_action_ready(dict(child,create_time=.5),launcher))
        for state in (False,None):
            for where in (0,1):
                rows=[dict(same_identity_exists=True),dict(same_identity_exists=True)]
                rows[where]['same_identity_exists']=state
                with patch.object(n,'read_identity',side_effect=rows):self.assertFalse(n.owned_child_action_ready(child,launcher))

    def test_readback_six_fields_drift_is_unknown(self):
        row=dict(pid=200,create_time=2,exe='child',cwd='cwd',cmdline=['child'],ppid=100)
        process=type('Process',(),dict(create_time=lambda self:2))()
        for field,value in [('exe','other'),('cwd','other'),('ppid',999),('cmdline',['other'])]:
            with patch.object(n.psutil,'Process',return_value=process),patch.object(n,'identity',return_value=dict(row,**{field:value})):
                result=n.read_identity(row)
                self.assertIsNone(result['same_identity_exists']);self.assertEqual(result['observed_status'],'IDENTITY_CHANGED')

    def test_metadata_prefix_no_spawn(self):
        with patch.object(sys,'argv',['native_capture.py','s15_actual',sys.executable]),patch.object(n.subprocess,'Popen',side_effect=AssertionError('不允许启动')):
            with self.assertRaises(ValueError):n.main(dict(mode='collect',prefix='s15_other'))

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Bindings))
    # 从已保存原件取明确六字段，只有只读读回，不操作任何未知或仍活对象。
    known={}
    for directory in ('owned_threshold_canary','owned_threshold_canary_r03','one_second_cadence_canary_r03'):
        receipt=W/directory/'guard/guard_receipt.json'
        if receipt.is_file():
            r=json.loads(receipt.read_text(encoding='utf-8'))
            for item in [r['binding'],r.get('initial_root_identity'),*[x.get('identity') for x in r.get('retained',[])],*[x.get('before') for x in r.get('stopped',[])]]:
                if item and all(k in item for k in guard.IDENTITY_KEYS):known[(item['pid'],item['create_time'])]=item
    for directory in ('native_consumer_canary_r03','native_consumer_canary_r04','native_consumer_canary_r05'):
        p=W/directory/'known_identity_terminal.json'
        if p.is_file():
            for row in json.loads(p.read_text(encoding='utf-8'))['observations']:
                item=row['expected'];known[(item['pid'],item['create_time'])]=item
    monitor=guard.Guard({}, {}, W/'unused_readonly')
    observations=[monitor.readback_member(row) for row in known.values()]
    with (W/('final_checks_result_'+(sys.argv[1] if len(sys.argv)>1 else 'r01')+'.json')).open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(dict(status='PASS_G1_ONLY' if result.wasSuccessful() else 'FAIL_PRESERVED',methods=result.testsRun,
                       known_identity_observations=observations,known_same_birth_absent=all(r['status'] in ('ABSENT','ORIGINAL_PID_REUSED') for r in observations),
                       entire_os_tree_terminal='NOT_PROVEN',actions_executed=False,actual_source_commit=None,
                       function_g2=None,tools_g2=None,continuous_resource_pass=False),stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps(dict(methods=result.testsRun,known_identities=len(observations),statuses=[r['status'] for r in observations]),ensure_ascii=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
