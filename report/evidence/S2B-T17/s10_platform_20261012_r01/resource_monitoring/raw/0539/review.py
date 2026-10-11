"""S10 supervisor独立只读快审，真实子程序码及原字节分开绑定。"""
from pathlib import Path
import sys,json,subprocess,time,hashlib,psutil,traceback
WORK=Path(__file__).resolve().parent;ROOT=WORK.parents[3];SOURCE=ROOT/'tmp/2B/S2B-T17/s10_guard_supervisor_20261012_r01';started=time.monotonic();results={'status':'RUNNING','runs':[]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
try:
    assert sha(SOURCE/'supervisor.py')=='d8c6e2e53b4b3012a139a2ab33969d0c308dc2a42e49976cad205b02ba8b578c'
    assert sha(SOURCE/'native_receipt.json')=='df11940812469f2a239ca9ea2dfbbd7f5f08e0c43a393c018ad2a3ae7245f1ed'
    assert sha(SOURCE/'selftest_result.json')=='b5fff90c2b324f68ce0001d1a3d67bc2c98efeb364a04e5fd15650cee1af1b9c'
    assert sha(ROOT/'tmp/2B/S2B-T17/s10_resource_guard_20261012_r02/guard.py')=='be8d51ba18cf331458e1d747578f332c4e5cc4b72604a3fb6d09e15030abb4d4'
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()=='1eed350c43aae4cdee1f8179a93ce87d75d9f2a8'
    p=psutil.Process();binding={'pid':p.pid,'create_time':p.create_time(),'exe':p.exe(),'cwd':p.cwd(),'cmdline':p.cmdline(),'ppid':p.ppid()}
    assert binding['pid']!=11112
    for mode in ['valid','mismatch','alert','input_drift']:
        directory=WORK/mode;directory.mkdir();bound=directory/'binding_snapshot.json';plan=directory/'plan_snapshot.json';save(bound,binding);save(plan,{'fixture':'不执行真实guard/预算，仅supervisor输入SHA与门禁测试'})
        command=[sys.executable,'-X','utf8','-B',str(WORK/'fake_guard.py'),'valid' if mode=='input_drift' else mode,str(bound),str(directory/'out/guard')]
        inputs=[{'path':str(f),'sha256':sha(f)} for f in [WORK/'fake_guard.py',plan,bound]]
        if mode=='input_drift':inputs[1]['sha256']='0'*64
        config=directory/'config.json';save(config,{'command':command,'binding':binding,'input_rows':inputs,'out':str(directory/'out')})
        cmd=[sys.executable,'-X','utf8','-B',str(WORK/'shim.py'),str(config)];begin=time.monotonic();done=subprocess.run(cmd,cwd=WORK,capture_output=True)
        (directory/'shim.stdout.log').write_bytes(done.stdout);(directory/'shim.stderr.log').write_bytes(done.stderr)
        receipt=load(directory/'out/supervisor_receipt.json');assert done.returncode==2 and receipt['supervisor_exit_code']==2
        events=[json.loads(s) for s in (directory/'out/supervision.jsonl').read_text(encoding='utf-8').splitlines()]
        ready=[e for e in events if e['kind']=='READY'];live=[e for e in events if e['kind']=='LIVE']
        if mode=='valid':
            assert receipt['ready'] and receipt['child_native_exit_code']==0 and len(ready)==1 and len(live)>=2 and live[1]['elapsed_seconds']-live[0]['elapsed_seconds']>=5
            assert all(ready[0]['root_identity'][k]==binding[k] for k in ['pid','create_time','exe','cwd','cmdline','ppid'])
        elif mode=='input_drift':assert not receipt['ready'] and receipt['child_native_exit_code'] is None and receipt['child_pid'] is None and '启动前输入SHA漂移' in receipt['reason']
        else:assert not receipt['ready'] and receipt['child_native_exit_code']==(7 if mode=='mismatch' else 2)
        if mode!='input_drift':
            assert (directory/'out/stdout.log').read_bytes()=='独立替身stdout原字节\r\n'.encode('utf-8')
            assert (directory/'out/stderr.log').read_bytes()=='独立替身stderr原字节\r\n'.encode('utf-8')
        results['runs'].append({'mode':mode,'command':subprocess.list2cmdline(cmd),'native_supervisor_exit_code':done.returncode,'child_native_exit_code':receipt['child_native_exit_code'],'ready':receipt['ready'],'seconds':round(time.monotonic()-begin,3),'receipt_sha256':sha(directory/'out/supervisor_receipt.json')})
    results.update(status='PASS',seconds=round(time.monotonic()-started,3),peak_self_working_set_bytes=getattr(psutil.Process().memory_info(),'peak_wset',None),limitations=['没有启动真实guard，没有探测/停止PID11112或任何目标PID，替身仅读写本目录。','实测保持生产5秒身份复核周期，ROOT/MCP消费集成仍未执行。','READY只按守护当前存活及首样本绑定匹配判断，不将guard正常0或已知成员口径推为整树安全。'])
except Exception:results.update(status='FAIL',traceback=traceback.format_exc())
save(WORK/'validation.json',results);print(json.dumps(results,ensure_ascii=False));raise SystemExit(0 if results['status']=='PASS' else 1)
