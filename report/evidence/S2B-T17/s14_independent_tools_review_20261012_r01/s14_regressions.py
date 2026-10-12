"""S14三处修复的纯模拟及自有轻量原生记录回归，不读取设备或生产源。"""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import patch
import guard
import selftest
import launch_monitor as launcher
import runtime_consumer as consumer
import compat_pins as pins
import collector as c
import native_capture

W=Path(__file__).parent;RUN=sys.argv[1] if len(sys.argv)>1 else 'r01';F=W/('s14_fixtures_'+RUN);F.mkdir()
ROWS=[]
def save(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
class FinalParent(unittest.TestCase):
    def run_case(self,kind):
        world=selftest.World();world.make(300,3,200,37)
        monitor,root=selftest.monitor(world)
        with patch.object(guard.psutil,'Process',world.process):
            first,unknown,_=monitor.collect(root)
            self.assertFalse(unknown)
            observed={(r['pid'],r['create_time']):r for r in first}
            real_chain=monitor.round_chain;real_read=monitor.readback_member;real_root=monitor.get_root
            armed=False;changed=False
            def chain(item,bound,table):
                nonlocal armed
                result=real_chain(item,bound,table)
                if item['pid']==300:armed=True
                return result
            def read(expected):
                nonlocal changed
                if armed and not changed and expected['pid']==100:
                    changed=True
                    if kind in ('absent','no_proof','root_drift'):world.nodes.pop(200)
                    elif kind=='reuse':world.make(200,22,100,20)
                    elif kind=='unknown':world.fail[(200,'create_time')]=guard.psutil.AccessDenied(200)
                    elif kind=='parent_drift':world.nodes[200]['exe']='其他.exe'
                    elif kind=='member_drift':world.nodes[300]['cmdline']=['其他']
                    if kind=='no_proof':monitor.known_lineage.pop((300,3))
                return real_read(expected)
            monitor.round_chain=chain;monitor.readback_member=read
            if kind=='root_drift':
                monitor.get_root=lambda:('MATCH',dict(root,exe='其他ROOT.exe')) if changed else real_root()
            members,uncertain,exits=monitor.collect_round(root,observed)
            if kind=='absent':
                self.assertFalse(uncertain)
                leaf=next(r for r in members if r['pid']==300)
                self.assertEqual(leaf['rss_bytes'],37);self.assertTrue(leaf['monitorable'])
                self.assertFalse(leaf['stoppable']);self.assertEqual(leaf['lineage_mode'],'HISTORICAL_CHAIN')
                self.assertEqual(sum(r['rss_bytes'] for r in members),47)
                self.assertEqual(len([r for r in exits if r['expected']['pid']==200]),1)
                monitor.record_sample_exit(dict(expected=observed[(200,2)],status='ABSENT'),exits)
                self.assertEqual(len([r for r in exits if r['expected']['pid']==200]),1)
            else:self.assertTrue(uncertain,kind)
            self.assertFalse(any(r['kind']=='TERMINATE_SENT' for r in monitor.events))
            ROWS.append(dict(case='末表/'+kind,uncertain=bool(uncertain),fixture_test=True))
    def test_absent_retains_real_rss_once(self):self.run_case('absent')
    def test_reuse_blocked(self):self.run_case('reuse')
    def test_unknown_blocked(self):self.run_case('unknown')
    def test_parent_drift_blocked(self):self.run_case('parent_drift')
    def test_member_drift_blocked(self):self.run_case('member_drift')
    def test_no_proof_blocked(self):self.run_case('no_proof')
    def test_root_drift_blocked(self):self.run_case('root_drift')
    def test_new_orphan_not_adopted(self):
        world=selftest.World();world.make(300,3,200,37);monitor,root=selftest.monitor(world)
        with patch.object(guard.psutil,'Process',world.process):
            members,unknown,_=monitor.collect(root);self.assertFalse(unknown)
            monitor.last_members.update({(r['pid'],r['create_time']):r for r in members})
            world.nodes.pop(200);world.make(400,4,300,41)
            members,unknown,_=monitor.collect(root)
            self.assertTrue(unknown);self.assertNotIn((400,4),monitor.known_lineage)
            self.assertFalse(any(r['pid']==400 for r in members))

class Startup(unittest.TestCase):
    def test_partial_then_json_before_complete(self):
        base=F/'partial';base.mkdir();path=base/'first.jsonl'
        self.assertIsNone(launcher.startup_first_consumption(path))
        with path.open('xb') as stream:stream.write(b'{"status":')
        with patch.object(consumer,'complete',side_effect=AssertionError('半行不能调用complete')):
            self.assertIsNone(launcher.startup_first_consumption(path))
        with path.open('ab') as stream:stream.write(b'"CONSUMED_LIVE_READY"}\n')
        result=launcher.startup_first_consumption(path);self.assertEqual(result['row']['status'],'CONSUMED_LIVE_READY')
        with (base/'bad.jsonl').open('xb') as stream:stream.write(b'{broken}\n')
        with patch.object(consumer,'complete',side_effect=AssertionError('无效JSON不能调用complete')):
            with self.assertRaises(ValueError):launcher.startup_first_consumption(base/'bad.jsonl')
    def launch_case(self,name,expire=False):
        base=F/name;base.mkdir();consumption=base/'consumer';consumption.mkdir()
        config=base/'config.json';save(config,dict(output_dir=str(consumption)))
        path=consumption/'consumption.jsonl'
        with path.open('xb') as stream:stream.write(b'{"status":')
        ident=dict(pid=123,create_time=1,exe='模拟',cwd=str(base),cmdline=['模拟'],ppid=0)
        child=type('Child',(),dict(pid=123,poll=lambda self:None))()
        clock=[0]
        def sleep(seconds):
            clock[0]+=seconds
            if not expire and clock[0]>=.1 and not path.read_bytes().endswith(b'\n'):
                with path.open('ab') as stream:stream.write(b'"CONSUMED_LIVE_READY"}\n')
        with patch.object(sys,'argv',['launch_monitor.py','--config',str(config),'--output-dir',str(base/'handoff')]),patch.object(consumer,'launch',return_value=(child,dict(identity=ident))),patch.object(consumer,'identity',return_value=ident),patch.object(launcher.time,'monotonic',side_effect=lambda:clock[0]),patch.object(launcher.time,'sleep',side_effect=sleep),contextlib.redirect_stdout(io.StringIO()):
            code=launcher.main()
        receipt=json.loads((base/'handoff/handoff_receipt.json').read_text(encoding='utf-8'))
        self.assertEqual(code,2 if expire else 0)
        self.assertEqual(receipt['status'],'BLOCKED_BACKGROUND_STARTUP' if expire else 'READY_NATIVE_BACKGROUND_RUNNING')
        self.assertEqual(receipt['heavy_terminal'],'NOT_PROVEN')
    def test_main_waits_for_partial_firstline(self):self.launch_case('startup_wait')
    def test_deadline_still_blocks_partial(self):self.launch_case('startup_expire',True)

class NativeSeal(unittest.TestCase):
    def run_native(self,prefix,mode='source',cache=True):
        captured=[]
        with patch.object(sys,'argv',['native.py','--prefix',prefix,'--',mode]),patch.object(pins,'require_ready'),patch.object(pins,'SYNTH_CACHE',native_capture.HERE if cache else W/'different_CACHE'),patch.object(native_capture,'main',side_effect=lambda **kw:captured.append(kw) or 0):
            try:runpy.run_path(str(W/'native.py'),run_name='__main__')
            except SystemExit as exc:self.assertEqual(exc.code,0)
        return captured
    def test_prefix_strict_and_mode_metadata(self):
        for name in ('s12_bad','s13_bad','s14-bad','s14_','S14_bad'):
            with self.assertRaises(ValueError):self.run_native(name)
        for mode in ('prepare','source','collect','seal'):
            self.assertEqual(self.run_native('s14_positive',mode),[dict(metadata=dict(mode=mode,prefix='s14_positive'))])
    def test_cache_mismatch_before_capture(self):
        with self.assertRaisesRegex(ValueError,'CACHE相同'):self.run_native('s14_cache',cache=False)
    def test_metadata_cannot_override_native(self):
        with patch.object(native_capture.subprocess,'Popen',side_effect=AssertionError('无效metadata不能启动')):
            with self.assertRaises(ValueError):native_capture.main(dict(mode='collect',prefix='s14_bad',native_exit_code=0))
    def test_actual_native_metadata_canary(self):
        with patch.object(sys,'argv',['native_capture.py','s14_metadata_canary_'+RUN,sys.executable,'-X','utf8','-B','-c','print("仅自有轻量原生夹具")']):
            with contextlib.redirect_stdout(io.StringIO()):code=native_capture.main(dict(mode='collect',prefix='s14_metadata_canary'))
        self.assertEqual(code,0)
        receipt=json.loads((W/('s14_metadata_canary_'+RUN+'.native.json')).read_text(encoding='utf-8'))
        self.assertEqual(receipt['mode'],'collect');self.assertEqual(receipt['prefix'],'s14_metadata_canary')
        self.assertEqual(receipt['closed_logs'],[receipt['stdout'],receipt['stderr']])
        self.assertEqual(receipt['native_exit_code'],0)
    def test_mock_seal_consumes_s14_records_only(self):
        base=F/'seal';base.mkdir();report=base/'report';report.mkdir();cache=base/'cache';cache.mkdir()
        commit='b'*40;freeze=base/'freeze.json';save(freeze,dict(profile='s2b-inference-platform/0.1.14',source_commit=commit))
        before=base/'before.json';after=base/'after.json'
        for path in (before,after):save(path,dict(source_files=[],fixture_test=True))
        save(report/'s14_collection_summary.json',dict(source_commit=commit,limitations=['仅模拟收尾，不是实际执行'],timing=dict(status='SYNTHETIC_ONLY')))
        save(report/'s14_sta_classifier.native.json',dict(native_exit_code=0,windows_command='SYNTHETIC',fixture_test=True))
        for label,mode,phase in [('collect','collect',None),('before','source','before'),('after','source','after')]:
            command=['SYNTHETIC','--commit',commit]+(['--phase',phase] if phase else [])
            save(cache/('s14_'+label+'.native.json'),dict(mode=mode,prefix='s14_'+label,native_exit_code=0,command=command,closed_logs=[],fixture_test=True))
        save(cache/'s12_stale.native.json',dict(fixture_test=True,not_this_run=True))
        gate=dict(source_before=dict(path=before.relative_to(c.ROOT).as_posix()),source_after=dict(path=after.relative_to(c.ROOT).as_posix()),approved_evidence=[])
        real_read=c.read
        def read(path):
            if path.name=='s7_collection_delivery_manifest_r03.json':return dict(interfaces=[])
            return real_read(path)
        with patch.object(pins,'require_ready'),patch.object(c,'require_pinned_commit'),patch.object(c,'closed_gate',return_value=gate),patch.object(c,'REPORT',report),patch.object(c,'CACHE',cache),patch.object(c,'FREEZE',freeze),patch.object(c,'read',side_effect=read),contextlib.redirect_stdout(io.StringIO()):
            c.seal(commit,base/'NO_GATE_READ')
        manifest=json.loads((report/'s14_delivery_manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(len([r for r in manifest['checks'] if r['name'].startswith('实际原生包装：')]),3)
        self.assertFalse((report/'native_closed/s12_stale.native.json').exists())
        self.assertEqual(manifest['schema_version'],1)

if __name__=='__main__':
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(cls) for cls in (FinalParent,Startup,NativeSeal)])
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    save(W/('s14_regression_result_'+RUN+'.json'),dict(status='PASS_G1_FIXTURE_ONLY' if result.wasSuccessful() else 'FAIL_PRESERVED',methods=result.testsRun,cases=ROWS,source_commit=None,actual_runtime='NOT_RUN',actual_source_freeze='NOT_RUN',vivado_ross_hardware=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
