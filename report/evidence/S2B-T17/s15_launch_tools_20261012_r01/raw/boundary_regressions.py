"""S14三类窗口及采集真实失败的轻量边界反例；不降低max3或两轮活集合标准。"""
import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import guard
import selftest
import collector as c
import compat_pins as pins

W=Path(__file__).parent
ROWS=[]

class Closure(unittest.TestCase):
    def sequence(self, rounds):
        world=selftest.World(); monitor,root=selftest.monitor(world)
        calls=[]
        def next_round(bound,observed):
            calls.append(len(calls)+1)
            return rounds[len(calls)-1]
        monitor.collect_round=next_round
        members,unknown,exits=monitor.collect(root)
        ROWS.append(dict(case=self._testMethodName,scans=len(calls),unknown=unknown,fixture_only=True))
        return monitor,members,unknown,exits

    def test_same_alive_set_second_round_absent_exit_closes(self):
        root=dict(pid=100,create_time=1)
        result=dict(expected=dict(pid=200,create_time=2),status='ABSENT')
        m,members,unknown,exits=self.sequence([([root],[],[]),([root],[],[result])])
        self.assertFalse(unknown);self.assertTrue(m.collection_observation['closed'])
        self.assertEqual(exits,[result]);self.assertEqual(m.collection_observation['scans'],2)

    def test_previous_alive_exit_needs_third_identical_round(self):
        root=dict(pid=100,create_time=1); old=dict(pid=200,create_time=2)
        result=dict(expected=old,status='ABSENT')
        m,_,unknown,exits=self.sequence([([root,old],[],[]),([root],[],[result]),([root],[],[])])
        self.assertFalse(unknown);self.assertEqual(m.collection_observation['scans'],3);self.assertEqual(exits,[result])

    def test_newborn_each_round_stays_blocked(self):
        root=dict(pid=100,create_time=1)
        rounds=[([root]+[dict(pid=200+i,create_time=2+i) for i in range(n)],[],[]) for n in (1,2,3)]
        m,_,unknown,_=self.sequence(rounds)
        self.assertFalse(m.collection_observation['closed']);self.assertEqual(unknown[0]['reason'],'TREE_RESCAN_NOT_CLOSED')

    def test_exit_and_newbirth_not_equivalent(self):
        root=dict(pid=100,create_time=1)
        rounds=[([root,dict(pid=200,create_time=n)],[],[]) for n in (2,3,4)]
        _,_,unknown,_=self.sequence(rounds);self.assertTrue(unknown)

    def test_any_unknown_round_stops_no_skip(self):
        root=dict(pid=100,create_time=1)
        for index in (0,1,2):
            rounds=[([root,dict(pid=200,create_time=n)],[],[]) for n in (2,3,4)]
            rounds[index]=([root],[dict(reason='UNKNOWN_ACCESS_DENIED')],[])
            m,_,unknown,_=self.sequence(rounds)
            self.assertTrue(unknown);self.assertEqual(m.collection_observation['scans'],index+1)

    def test_original_reuse_is_exit_new_object_untouched(self):
        world=selftest.World();m,root=selftest.monitor(world)
        with patch.object(guard.psutil,'Process',world.process):
            expected=guard.base_identity(world.process(200));world.make(200,22,100,20)
            result=m.readback_member(expected)
            self.assertEqual(result['status'],'ORIGINAL_PID_REUSED');self.assertTrue(result['new_object_untouched'])
            world.fail[(200,'create_time')]=guard.psutil.AccessDenied(200)
            self.assertEqual(m.readback_member(expected)['status'],'UNKNOWN')

    def test_full_fields_drift_never_alive(self):
        for field,value in [('exe','其他.exe'),('cwd',str(W/'elsewhere')),('ppid',777),('cmdline',['other'])]:
            world=selftest.World();m,root=selftest.monitor(world)
            with patch.object(guard.psutil,'Process',world.process):
                expected=guard.base_identity(world.process(200));world.nodes[200][field]=value
                self.assertEqual(m.readback_member(expected)['status'],'IDENTITY_CHANGED')

    def test_final_parent_then_leaf_exit_removed(self):
        world=selftest.World();world.make(300,3,200,37);m,root=selftest.monitor(world)
        with patch.object(guard.psutil,'Process',world.process):
            first,unknown,_=m.collect(root);self.assertFalse(unknown)
            observed={(v['pid'],v['create_time']):v for v in first}
            real_read=m.readback_member;real_chain=m.round_chain;armed=False;changed=False
            def chain(*args):
                nonlocal armed
                value=real_chain(*args)
                if args[0]['pid']==300:armed=True
                return value
            def read(expected):
                nonlocal changed
                if armed and expected['pid']==100 and not changed:
                    world.nodes.pop(200);changed=True
                if changed and expected['pid']==300:
                    world.nodes.pop(300,None)
                return real_read(expected)
            m.round_chain=chain;m.readback_member=read
            members,unknown,exits=m.collect_round(root,observed)
            self.assertFalse(unknown);self.assertEqual([r['pid'] for r in members],[100])
            self.assertEqual({r['expected']['pid'] for r in exits},{200,300})

class Collector(unittest.TestCase):
    def test_identifier_only_backslash(self):
        row=dict(path='report\\evidence/S2B-T17/test.json',sha256='a'*64,bytes=1)
        canonical=c.manifest_identifier(row)
        self.assertEqual(canonical['path'],'report/evidence/S2B-T17/test.json')
        self.assertEqual(row['path'],'report\\evidence/S2B-T17/test.json')
        for name in ['C:\\real\\file','/absolute','\\absolute','a/../b','a\\.\\b','a//b','a\\\\b','']:
            with self.assertRaises(ValueError):c.manifest_identifier(dict(row,path=name))

    def test_gate_cli_exact_name(self):
        value='b'*40; gate=str(W/'fixture_gate.json')
        with patch.object(sys,'argv',['collector.py','collect','--commit',value,'--gate',gate]),patch.object(c,'collect',return_value=77) as collect:
            self.assertEqual(c.main(),77);collect.assert_called_once_with(value,Path(gate))
        with patch.object(sys,'argv',['collector.py','collect','--commit',value,'--closed-gate',gate]),contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as failure:c.main()
            self.assertEqual(failure.exception.code,2)

    def test_missing_explicit_native_fails_descriptively(self):
        for gate in ({},{'native_wrappers':[]}):
            with self.assertRaisesRegex(ValueError,'native_wrappers'):c.runtime_native_records(gate)

    def test_unknown_native_schema_retained_rejected(self):
        directory=W/'native_schema_fixture';directory.mkdir()
        path=directory/'s15_runtime_old.native.json'
        path.write_text(json.dumps(dict(native_exit_code=0,command=['OLD_G1'])),encoding='utf-8')
        with patch.object(c,'CACHE',directory):
            with self.assertRaisesRegex(ValueError,'mode'):c.runtime_native_records(dict(native_wrappers=[c.binding(path)]))
        self.assertTrue(path.is_file())

    def test_pending_no_real_freeze_approval(self):
        self.assertIsNone(pins.SOURCE_COMMIT);self.assertIsNone(pins.TOOLS_G2_SHA)
        self.assertIsNone(pins.FUNCTIONAL_G2_SHA)
        with self.assertRaises(ValueError):pins.require_ready()

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(cls) for cls in (Closure,Collector)]))
    with (W/'boundary_regression_result.json').open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(dict(status='PASS_G1_FIXTURE_ONLY' if result.wasSuccessful() else 'FAIL_PRESERVED',methods=result.testsRun,cases=ROWS,
                       real_s14_reclassification=False,ongoing_birth_within_three_scans='BLOCKED',vivado_ross_hardware=False),stream,ensure_ascii=False,indent=2);stream.write('\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
