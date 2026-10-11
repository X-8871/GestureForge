"""独立核对冻结交付原字节、历史helper映射、真实日志和冻结Git来源。"""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,time,re,difflib,sys
sys.stdout.reconfigure(encoding='utf-8')
W=Path(__file__).resolve().parent; R=W.parents[3]; P=R/'report/evidence/S2B-T17/coordinates_20261011_r04'; start=time.monotonic()
def sha(p):
    """原字节SHA。"""
    return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    """UTF8 JSON。"""
    return json.loads(p.read_text(encoding='utf-8'))
report={'status':'FAIL','checks':[]}
def check(label,good):
    """所有检查须实际通过。"""
    report['checks'].append({'name':label,'passed':bool(good)}); assert good,label
try:
    expected={'delivery_manifest.json':'f25f99e66a27a86e2d619809cdc0f8fdd2b3469a77d235ac6e95dc7f3c71926b','validation.json':'3434d8e8d98a0c4cce7eaa7d0d1b8c7792f039fbe6733842d93d2e121f56de74','provenance.json':'0265c36cf7fa7f9160b700cfd02cedd04502f080417f33c0c44fa06957ad6bdb'}
    for p,h in expected.items(): check('封存SHA '+p,sha(P/p)==h)
    m=read(P/'delivery_manifest.json');v=read(P/'validation.json');q=read(P/'provenance.json')
    check('77绑定且不重复',len(m['files'])==77 and len({x['path'] for x in m['files']})==77)
    for x in m['files']: check('manifest '+x['path'],sha(R/x['path'])==x['sha256'])
    hist=q['captured_artifact_history']
    for k in ('archive','current'): check('helper '+k,sha(R/hist[k+'_path'])==hist[k+'_sha256'])
    check('captured旧helper映射',hist['captured_sha256']==hist['archive_sha256'] and (R/hist['archive_path']).stat().st_size==hist['captured_bytes'])
    report['helper_history_diff']=''.join(difflib.unified_diff((R/hist['archive_path']).read_text(encoding='utf-8').splitlines(True),(R/hist['current_path']).read_text(encoding='utf-8').splitlines(True)))
    for x in v['artifacts']:
        p=R/x['path']
        if x['path']==hist['captured_path']: p=R/hist['archive_path']
        check('validation原件 '+x['path'],sha(p)==x['sha256'] and p.stat().st_size==x['bytes'])
    check('validation来源前后不变',v['source_sha256_pre']==v['source_sha256_post'] and v['frozen14_sha256_pre']==v['frozen14_sha256_post'])
    for p,h in v['source_sha256_pre'].items(): check('实际source '+p,sha(R/p)==h)
    frozen=[]
    for p,h in v['frozen14_sha256_pre'].items():
        blob=subprocess.check_output(['git','show','671f9cf494b92ce182b3f1542fefd0cfd4b209f5:'+p],cwd=R);raw=(R/p).read_bytes()
        check('最终freeze '+p,raw.replace(b'\r\n',b'\n')==blob.replace(b'\r\n',b'\n') and sha(R/p)==h)
        frozen.append({'path':p,'raw_sha256':h,'git_blob_sha256':hashlib.sha256(blob).hexdigest(),'raw_equal':raw==blob})
    report['frozen14']=frozen
    for run in v['runs']:
        check('真实native '+run['name'],run['exit_code']==0 and run['failure'] is None and sha(R/run['log'])==run['log_sha256'])
    check('STA/G3未误继承',v['sta']=='NOT_RUN' and v['g3']=='NOT_RUN')
    original=subprocess.check_output(['git','show','6d00ff2d05e92fa6cff05243fb620f8a0232b9f1:src/s2b_network_backend.sv'],cwd=R)
    check('S1直接Git原件',(P/'s1_network_backend.sv').read_bytes()==original)
    spec=importlib.util.spec_from_file_location('runner',R/'verification/test_s2b_backend_coordinates_rtl.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
    model=read(R/r.MODEL)
    check('Developer TB可从实际runner/model重放',r.generate_tb(model).encode()==(P/'tb_s2b_backend_coordinates.sv').read_bytes())
    check('conv明确共享stub',r.convolution_stub().encode()==(P/'convolution_stub.sv').read_bytes())
    log=(P/'simulation.log').read_text(encoding='utf-8')
    actual=re.findall(r'PASS BACKEND_COORDINATES boundary=(\d+) layers=(\d+) outputs=(\d+) requests=(\d+) cycles=(\d+) owner_drop_results=(\d+)',log)
    check('原件实际PASS计数',len(actual)==1 and list(map(int,actual[0]))==list(v['simulation_counts'].values()))
    report['prior_attempts']=[]
    for name in ('coordinates_20261011_r01','coordinates_20261011_r02','coordinates_20261011_r03'):
        p=P.parent/name/'validation.json';data=read(p);report['prior_attempts'].append({'run':name,'validation_sha256':sha(p),'status':data['status'],'failure':data.get('failure'),'runs':data.get('runs')})
        check('旧失败原件仍在 '+name,data['status']=='FAIL')
    current=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
    diff=subprocess.check_output(['git','diff','--name-only','1f2f9b964135ae6b92ccf557fd3f1de9639c3f46',current,'--',*v['source_sha256_pre']],cwd=R,text=True)
    check('无关T19提交未改变S2闭包',not diff.strip());report['actual_head']=current
    report['status']='PASS_DELIVERY_BINDINGS'
except Exception as exc: report['failure']=repr(exc)
report['seconds']=round(time.monotonic()-start,6)
(W/'delivery_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'checks':len(report['checks']),'seconds':report['seconds'],'failure':report.get('failure'),'helper_history_diff':report.get('helper_history_diff')},ensure_ascii=False))
raise SystemExit(0 if report['status']=='PASS_DELIVERY_BINDINGS' else 1)
