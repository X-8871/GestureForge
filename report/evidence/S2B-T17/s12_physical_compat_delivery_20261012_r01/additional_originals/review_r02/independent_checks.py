"""R2独立只读复审，所有命令内容与Git返回值均为合成，不访问设备。"""
import ast
import contextlib
import copy
import difflib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import time
import types
import psutil

ROOT=Path(__file__).parents[4];OUT=Path(__file__).parent
WORK=ROOT/'tmp/2B/S2B-T17/s12_physical_compat_prepare_20261012_r02'
OLD=ROOT/'tmp/2B/S2B-T17/s12_physical_compat_prepare_20261012_r01'
started=time.monotonic();peak=0;results=[]
def sample():
    """仅采样本进程，不操作其他任务。"""
    global peak
    peak=max(peak,psutil.Process().memory_info().rss)
    assert peak<134217728
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(65536),b''):h.update(block)
    return h.hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def save(path,value):
    """隔离新路径只创建，不覆盖已有原件。"""
    assert path.is_relative_to(OUT)
    with path.open('x',encoding='utf-8',newline='\n') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
directory_names={};verified_dirs=set()
def exact(path):
    """核每个精确名称、类型及链接；只读缓存目录枚举。"""
    assert path.is_absolute()
    current=Path(path.anchor)
    for name in path.parts[1:]:
        if str(current) not in directory_names:directory_names[str(current)]={p.name for p in current.iterdir()}
        assert name in directory_names[str(current)],str(path)
        current=current/name
        if str(current) not in verified_dirs:
            assert not current.is_symlink() and not current.is_junction()
            if current.is_dir():verified_dirs.add(str(current))
    assert current.is_file()
    return current
assert sha(WORK/'final_draft_binding.json')=='8513ce1d1ea8a563fdc1e73f7ea57dca7be9bc63b81794d808a0d61af9f83562'
assert sha(WORK/'compatibility_delivery_receipt.json')=='8fe0346124032ec99bc637d9402901df2a9c462098634984f6838242f5da3c78'
assert sha(WORK/'raw_manifest.jsonl')=='0e5cdd71fd3ff35b76fa440147b72613154fb5840269c010e2396e60d9adbec5'
count=0;total=0;seen=set()
for line in (WORK/'raw_manifest.jsonl').read_text(encoding='utf-8').splitlines():
    row=json.loads(line);path=exact(WORK/row['path'])
    assert str(path)==row['absolute_path'] and row['path'] not in seen
    seen.add(row['path']);count+=1;total+=row['bytes']
    assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],row['path']
    sample()
assert count==3245 and total==2021798
entry=read(WORK/'final_draft_binding.json')
for row in entry['files']:
    path=exact(WORK/row['path']);assert sha(path)==row['sha256'] and path.stat().st_size==row['bytes']
    ast.parse(path.read_text(encoding='utf-8'))
    expected=''.join(difflib.unified_diff((OLD/row['path']).read_text(encoding='utf-8').splitlines(keepends=True),path.read_text(encoding='utf-8').splitlines(keepends=True),fromfile='冻结r01:'+row['path'],tofile='S12-PH-COMPAT2-R2:'+row['path']))
    assert (WORK/row['diff']).read_text(encoding='utf-8')==expected,row['diff']
for row in read(WORK/'input_bindings.json'):
    path=exact(Path(row['path']));assert sha(path)==row['sha256']
    if 'bytes' in row:assert path.stat().st_size==row['bytes']
sys.path.insert(0,str(WORK))
import compat_pins as p
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj
impl=module('independent_r2_impl',WORK/'impl_collector.py')
c=module('independent_r2_synth',WORK/'collector.py')
after=module('independent_r2_after',WORK/'source_after_check.py')
assert p.SOURCE_COMMIT is None and not hasattr(p,'EVIDENCE_HEAD') and impl.EVIDENCE_HEAD_AT_PREPARATION is None
assert ast.dump(next(n for n in ast.parse((OLD/'impl_collector.py').read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name=='timing'))==ast.dump(next(n for n in ast.parse((WORK/'impl_collector.py').read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name=='timing'))
recovery=[p.resolve_permanent(p.GUARD,p.GUARD_SHA),p.resolve_permanent(p.SUP,p.SUP_SHA)]
assert sha(p.ARCHIVE/'delivery_manifest_r02.json')=='139d5b72f9faa0bb58943b0dcff0d5e70ebcd8d189246e061a4df6013f8c3dce'
try:p.require_ready()
except ValueError as exc:assert 'BLOCKED_PENDING_S12_PINS' in str(exc)
else:raise AssertionError('真实缺pin未阻断')
old_ready=p.require_ready;old_pin=p.SOURCE_COMMIT;old_impl_commit=impl.COMMIT
p.require_ready=lambda pnr=False:None;p.SOURCE_COMMIT='a'*40;impl.COMMIT='a'*40
counter=0
def test(name,action,reject=False):
    """独立断言实际函数接受或拒绝，不将模拟结果称实际物理运行。"""
    try:
        value=action()
        assert not reject,'误接受 '+name
        results.append(dict(name=name,outcome='ACCEPTED_SYNTHETIC',detail=value))
    except ValueError as exc:
        assert reject,'误拒绝 '+name+':'+str(exc)
        results.append(dict(name=name,outcome='REJECTED_EXPECTED',exception=str(exc)))
    sample()
def pnr(label=None,code=0,client='SAME',timeout=False,invalid='ABSENT',duplicate=False,wrong=False):
    """从独立五标签真哈希夹具形成history双射；不运行其Tcl字符串。"""
    global counter
    counter+=1;base=OUT/('pnr_'+str(counter));base.mkdir()
    labels=['launch','wait','open_run','reports','close']
    commands=[impl.APPROVED_LAUNCH,'wait_on_run impl_1','open_run impl_1','report_timing_summary -file {SYNTHETIC.rpt}','close_project']
    if invalid!='ABSENT':
        labels.insert(0,'launch_invalid');commands.insert(0,'launch_runs impl_1 -to_step '+('WRONG' if wrong else 'post_route_phys_opt_design')+' -jobs 1')
        if duplicate:labels.insert(0,'launch_invalid');commands.insert(0,commands[0])
    rows=[];history=[]
    for i,(tag,command) in enumerate(zip(labels,commands),1):
        native=invalid if tag=='launch_invalid' else code if tag==label else 0
        client_code=native if tag!=label or client=='SAME' else client
        call=dict(fixture_test=True,input=dict(command=command),result=dict(content=[dict(type='text',text=json.dumps(dict(exit_code=client_code)))]))
        if timeout and tag==label:call['result']['isError']=True
        path=base/('call_'+str(i)+'.json');save(path,call)
        bound=impl.c.binding(path);bound.update(id=i,label=tag);rows.append(bound)
        history.append(dict(id=i,command=command,code=native,fixture_test=True))
    history_path=base/'history.json';save(history_path,dict(fixture_test=True,content=[dict(type='text',text=json.dumps(dict(history=history)))]))
    generic=base/'synthetic.json';save(generic,dict(fixture_test=True))
    gate=dict(root_explicit_signal='CLOSED_PNR_INPUTS_READY',project_closed=True,owned_root_exited=True,source_commit='a'*40,root_declared_implementation_execution_count=1,design_mcp_records=rows,additional_closed_files=[],native_files=[],fixture_test=True)
    for key in ('source_before','source_after','source_before_native','source_after_native','mcp_history','immutable_session_log','guard_receipt','supervisor_receipt','owned_root_exit_proof','resource_admission'):gate[key]=impl.c.binding(history_path if key=='mcp_history' else generic)
    gate_path=base/'gate.json';save(gate_path,gate)
    _,paired=impl.closed_gate(gate_path)
    if timeout:
        item=next(r for r in paired if r['label']==label)
        assert item['client_timeout_or_error'] is True and item['client_exit_code'] is None and type(item['history']['code']) is int and item['history']['code']==0
    return dict(paired=len(paired),timeout_independent=timeout,actual_tcl_calls=0)
try:
    test('五history int0基准',pnr)
    for label in ('launch','wait','open_run','reports','close'):
        for code in (1,None,False,0.0,'0'):
            test('native坏矩阵 '+label+repr(code),lambda label=label,code=code:pnr(label,code),True)
            test('timeout不能掩盖native '+label+repr(code),lambda label=label,code=code:pnr(label,code,timeout=True),True)
            test('client非timeout坏矩阵 '+label+repr(code),lambda label=label,code=code:pnr(label,0,client=code),True)
        test('timeoutclient/native0 '+label,lambda label=label:pnr(label,timeout=True))
    for code in (1,-1,2):test('invalid严格非0 '+repr(code),lambda code=code:pnr(invalid=code))
    for code in (False,True,None,0,0.0,1.0,'1'):test('invalid错误类型/0 '+repr(code),lambda code=code:pnr(invalid=code),True)
    test('invalid精确token',lambda:pnr(invalid=1,wrong=True),True)
    test('invalid唯一',lambda:pnr(invalid=1,duplicate=True),True)

    for name in ('source','closed_gate','collect','seal'):
        base=OUT/('commit_'+name);base.mkdir();before=set(base.iterdir())
        def reject_cli(name=name,base=base):
            if name=='source':return c.source('b'*40,'before')
            if name=='closed_gate':return c.closed_gate(base/'NONEXISTENT','b'*40)
            return getattr(c,name)('b'*40,base/'NONEXISTENT')
        test('CLI B/PIN A写入前 '+name,reject_cli,True)
        assert set(base.iterdir())==before
    def closed_source(name,field=None,mode='closed_gate'):
        base=OUT/name;base.mkdir()
        rows={}
        for key in ('preparation_receipt','source_before','source_after','static_source_closed','immutable_session_log','mcp_history'):
            path=base/(key+'.json');save(path,dict(source_commit='b'*40 if key==field else 'a'*40,fixture_test=True));rows[key]=c.binding(path)
        declared=[]
        for i,label in enumerate(c.LABELS):
            path=base/('call_'+str(i)+'.json');save(path,dict(fixture_test=True));bound=c.binding(path);bound.update(label=label);declared.append(bound)
        gate=dict(rows,root_explicit_signal='CLOSED_INPUTS_READY',project_closed=True,source_commit='a'*40,root_declared_products_execution_count=1,root_declared_synthesis_execution_count=1,design_mcp_records=declared,additional_closed_files=[],approved_evidence=[])
        gate_path=base/'gate.json';save(gate_path,gate);freeze=base/'freeze.json';save(freeze,dict(source_commit='b'*40 if field=='freeze' else 'a'*40,fixture_test=True))
        previous=(c.FREEZE,c.FREEZE_SHA,c.REPORT,c.PRE,c.PROJECT)
        c.FREEZE=freeze;c.FREEZE_SHA=sha(freeze);c.REPORT=base/'NEW_REPORT';c.PRE=base/'NEW_PRE';c.PROJECT=base/'NEW_PROJECT'
        try:
            if mode=='closed_gate':return c.closed_gate(gate_path,'a'*40)
            return getattr(c,mode)('a'*40,gate_path)
        finally:
            assert not c.REPORT.exists() and not c.PRE.exists() and not c.PROJECT.exists()
            c.FREEZE,c.FREEZE_SHA,c.REPORT,c.PRE,c.PROJECT=previous
    test('闭合commit A正例',lambda:bool(closed_source('closed_valid')))
    for mode in ('closed_gate','collect','seal'):
        for field in ('freeze','source_before','source_after'):
            test(mode+' '+field+'commit漂移',lambda mode=mode,field=field:closed_source(mode+'_'+field,field,mode),True)

    def complete_source(name,cli='a'*40,head='a'*40,freeze_commit='a'*40):
        """完整43RAW逻辑独立夹具，只替换Git返回与静态checker，其他门禁保留。"""
        base=OUT/name;base.mkdir();cache=base/'cache';cache.mkdir()
        profile=dict(version='s2b-inference-platform/0.1.12',rtl_sources=['src/SYNTHETIC_'+str(i)+'.sv' for i in range(18)],source_derivation=dict(derived_sources=['SYNTHETIC_D'+str(i) for i in range(8)]),clock_hz=50000000,visibility_default=0)
        names=['board/s2b_inference_platform.json']+profile['rtl_sources']+['extra_'+str(i)+'.txt' for i in range(24)]
        raw={name:json.dumps(profile).encode('utf-8') if name.startswith('board/') else ('合成'+name+'\n').encode('utf-8') for name in names}
        for path,data in raw.items():
            target=base/path;target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as stream:stream.write(data)
        hashes={name:hashlib.sha256(data).hexdigest() for name,data in raw.items()};static={name:hashes[name] for name in names[:33]};fixed14={name:hashes[name] for name in names[1:15]}
        freeze=base/'freeze.json';save(freeze,dict(source_commit=freeze_commit,profile=profile['version'],source_files=[dict(path=name,sha256=hashes[name]) for name in names],frozen14=fixed14,active_rtl_sources=profile['rtl_sources']))
        checker=base/'verification/check_s2b_inference_platform.py';checker.parent.mkdir()
        with checker.open('x',encoding='utf-8') as stream:stream.write('"""模拟静态契约。"""\n')
        globals_old={key:getattr(c,key) for key in ('ROOT','WORK','CACHE','PROJECT','REPORT','PRE','FREEZE','FREEZE_SHA','git','save')}
        c.ROOT=base;c.WORK=base;c.CACHE=cache;c.PROJECT=base/'NEW_PROJECT';c.REPORT=base/'NEW_REPORT';c.PRE=base/'NEW_PRE';c.FREEZE=freeze;c.FREEZE_SHA=sha(freeze)
        calls=[]
        def mock_git(*args):
            calls.append(args)
            if args==('rev-parse','HEAD'):return (head+'\n').encode('ascii'),['SYNTHETIC_GIT',*args]
            if args==('diff','--cached','--name-only'):return b'',['SYNTHETIC_GIT',*args]
            assert args[0]=='show';return raw[args[1].split(':',1)[1]],['SYNTHETIC_GIT',*args]
        c.git=mock_git;old_spec=c.importlib.util.spec_from_file_location;old_module=c.importlib.util.module_from_spec
        c.importlib.util.spec_from_file_location=lambda *args:types.SimpleNamespace(loader=types.SimpleNamespace(exec_module=lambda value:None))
        c.importlib.util.module_from_spec=lambda spec:types.SimpleNamespace(check_static=lambda root:static,FROZEN_CORE_SHA256=fixed14)
        save_real=c.save
        def synthetic_save(path,value):
            value=dict(value,fixture_test=True,actual_git_calls=0)
            if 'status' in value:value['synthetic_expected_status']=value.pop('status');value['status']='SYNTHETIC_TEST_ONLY'
            save_real(path,value)
        c.save=synthetic_save
        try:
            with contextlib.redirect_stdout(io.StringIO()):c.source(cli,'before')
            record=read(c.PRE/'source_before.json')
            assert record['status']=='SYNTHETIC_TEST_ONLY' and record['source_commit']==p.SOURCE_COMMIT and record['source_count']==43
            for row in record['source_files']:assert sha(base/row['snapshot'])==row['sha256']
            return dict(source_count=43,synthetic_git_calls=len(calls),actual_git_calls=0)
        except ValueError:
            assert not c.PRE.exists() and not c.REPORT.exists() and not c.PROJECT.exists()
            raise
        finally:
            for key,value in globals_old.items():setattr(c,key,value)
            c.importlib.util.spec_from_file_location=old_spec;c.importlib.util.module_from_spec=old_module
    test('43同RAW PIN A/CLI_HEAD_freeze B拒绝',lambda:complete_source('full_B',cli='b'*40,head='b'*40,freeze_commit='b'*40),True)
    test('完整source稳定A/43RAW',lambda:complete_source('full_A'))
    test('实际HEAD B拒绝',lambda:complete_source('full_head_B',head='b'*40),True)
    test('实际freeze B拒绝',lambda:complete_source('full_freeze_B',freeze_commit='b'*40),True)
finally:
    p.require_ready=old_ready;p.SOURCE_COMMIT=old_pin;impl.COMMIT=old_impl_commit
assert p.SOURCE_COMMIT is None
try:p.require_ready()
except ValueError as exc:assert 'BLOCKED_PENDING_S12_PINS' in str(exc)
else:raise AssertionError('测试后真实pin未恢复')
for row in entry['files']:assert sha(WORK/row['path'])==row['sha256']
legacy=read(WORK/'fixture_results.json');harness=read(WORK/'after_harness_results.json');regression=read(WORK/'r02_regression_results.json')
assert len(legacy['cases'])==57 and len(harness['cases'])==9 and len(regression['cases'])==108
for row in read(WORK/'native_r02_receipt.json')['records']:
    record=read(WORK/(row['label']+'.native.json'));assert type(record['native_exit_code']) is int and record['native_exit_code']==0
    assert record['script_sha_before']==record['script_sha_after']==row['script_sha_before']
nested=read(WORK/'validate.wrapper.json')['records']+read(WORK/'harness.wrapper.json')['records']
for row in nested:
    actual=read(WORK/(row['label']+'.native.json'));assert type(actual['native_exit_code']) is int and actual['native_exit_code']==actual['expected_native_code']==row['native_exit_code']
    if row['label'].endswith('_blocked'):assert b'BLOCKED_PENDING_S12_PINS' in (WORK/(row['label']+'.stderr.bin')).read_bytes()
assert len(nested)==16
assert read(WORK/'head.native.json')['native_exit_code']==0 and read(WORK/'seal.native.json')['native_exit_code']==0
sample()
result=dict(status='PASS_COMPAT_LOGIC_G2_ONLY',entry_sha256=sha(WORK/'final_draft_binding.json'),reviewed_files=entry['files'],source_entry=(WORK/'final_draft_binding.json').relative_to(ROOT).as_posix(),raw_manifest_sha256=sha(WORK/'raw_manifest.jsonl'),raw_manifest_files=count,total_raw_bytes=total,manifest_bytes=(WORK/'raw_manifest.jsonl').stat().st_size,old_r01_inputs_all_verified=True,full_diff_and_unchanged_timing_checked=True,fixed_recovery=recovery,independent_cases=results,case_count=len(results),developer_cases_bound_and_scripts_reviewed=174,developer_large_fixture_not_rerun=True,developer_outer_native0=5,developer_nested_native0=7,developer_nested_expected_native1=9,developer_head_native0=1,elapsed_seconds=time.monotonic()-started,sampled_self_rss_peak_bytes=peak,absolute_peak_bytes=None,actual_git_tcl_vivado_ross_hardware_calls=0,source_commit=None,evidence_head_role='综合无该角色；PNR None，未声明HEAD不合法化',physical_g0='BLOCKED_PENDING_REAL_PINS',actual_sta='NOT_RUN',actual_budget='NOT_RUN',old_s11_budget='BLOCKED',g3='NOT_RUN',g5='NOT_RUN',limitations=['所有Git与Tcl只为模拟，无真实运行、预算、STA或硬件通过。','最终pins/sourcefreeze/helper共同版本改变后须重新冻结复审。','采样本进程RSS，绝对连续峰未测；无RTL编译或重型进程。'],stop=True)
save(OUT/'final_review_receipt.json',result)
print(json.dumps(dict(status=result['status'],receipt_sha256=sha(OUT/'final_review_receipt.json'),cases=len(results),raw_files=count,elapsed_seconds=result['elapsed_seconds'],peak=peak),ensure_ascii=False))
