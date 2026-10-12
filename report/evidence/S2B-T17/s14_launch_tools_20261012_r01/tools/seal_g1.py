"""封存S14工具G1及失败原件；SOURCE/真实运行仍待ROOT与独审，绝不派发heavy。"""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import sys
import compat_pins as p

W=Path(__file__).parent;ROOT=W.parents[3];D=p.ARCHIVE
OLD=ROOT/'tmp/2B/S2B-T17/s13_launch_prepare_20261012_r01'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):
    assert path.is_relative_to(W) or path.is_relative_to(D)
    with path.open('x',encoding='utf-8',newline='\n') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
def copy(source,target):
    assert source.is_file() and not source.is_symlink() and not source.is_junction() and not target.exists()
    target.parent.mkdir(parents=True,exist_ok=True)
    raw=source.read_bytes()
    with target.open('xb') as stream:stream.write(raw)
    assert sha(source)==sha(target)
    return dict(original_absolute_path=str(source),sha256=sha(source),bytes=len(raw),archived_repo_path=target.relative_to(ROOT).as_posix())
assert p.SOURCE_COMMIT is None and p._LOADED_CONFIG_SHA is None and not p.RUNTIME_CONFIG.exists()
assert sha(p.GUARD)==p.GUARD_SHA and sha(p.SUP)==p.SUP_SHA
tools=[];diffs=[]
mapping=json.loads((W/'baseline_mapping.json').read_text(encoding='utf-8'))
for row in mapping['files']:
    source=Path(row['source']);assert sha(source)==row['source_sha256'] and source.stat().st_size==row['bytes']
    target=W/source.name
    patch=''.join(difflib.unified_diff(source.read_text(encoding='utf-8').splitlines(keepends=True),target.read_text(encoding='utf-8').splitlines(keepends=True),fromfile='冻结S13:'+source.name,tofile='S14工具G1:'+source.name))
    path=W/(source.name+'.diff')
    with path.open('x',encoding='utf-8',newline='\n') as stream:stream.write(patch)
    diffs.append(dict(path=path.name,sha256=sha(path)))
    copy(source,D/'baseline'/source.name)
for path in sorted(W.glob('*.py')):
    ast.parse(path.read_text(encoding='utf-8'))
    tools.append(copy(path,D/'tools'/path.name))
assert p.resolve_permanent(p.GUARD,p.GUARD_SHA)['sha256']==p.GUARD_SHA
assert p.resolve_permanent(p.SUP,p.SUP_SHA)['sha256']==p.SUP_SHA
native=[]
for path in sorted(W.glob('*.native.json')):
    record=json.loads(path.read_text(encoding='utf-8'))
    native.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),native_exit_code=record['native_exit_code'],elapsed_seconds=record.get('elapsed_seconds'),sampled_owned_tree_peak_bytes=record.get('sampled_owned_tree_peak_bytes'),unknown_count=record.get('unknown_count'),budget_stop=record.get('budget_stop')))
tests={name:json.loads((W/name).read_text(encoding='utf-8')) for name in ['selftest_result.json','monitor_fixture_result.json','collector_fixture_result_r02.json','s14_regression_result_r02.json','final_binding_checks_result.json']}
assert all(row['status'].startswith('PASS') for row in tests.values())
passed_methods=sum(tests[name][field] for name,field in [('selftest_result.json','mock_tests'),('monitor_fixture_result.json','mock_methods'),('collector_fixture_result_r02.json','methods'),('s14_regression_result_r02.json','methods'),('final_binding_checks_result.json','methods')])
receipt=dict(status='STOP_G1_TOOLS_PENDING_INDEPENDENT_G2',task='S14_RESOURCE_LAUNCH_TOOLS',baseline_commit=mapping['source_commit'],source_commit=None,source_freeze=None,root_profile_pending='s2b-inference-platform/0.1.14',tools=tools,diffs=diffs,test_methods=passed_methods,legacy_and_new_results=tests,native_records=native,native_expected_codes=dict(s14_pending_prepare_refusal=1,s14_regressions_r01=1),native_elapsed_seconds=sum(r['elapsed_seconds'] or 0 for r in native),sampled_owned_tree_peak_bytes=max(r['sampled_owned_tree_peak_bytes'] or 0 for r in native),absolute_tree_peak_bytes=None,actual_canaries=dict(guard_owned_threshold=1,guard_one_second_cadence=1,consumer_independent_clock=1,native_metadata=2),changes=['末表当前成员六字段/本次ROOT匹配且直接父ABSENT时，只有本次known_lineage允许historical_member+reject_reused_ancestor；RSS真实、HISTORICAL_CHAIN、stoppableFalse、父退出只记一次。','max3/twoalive、停止内核、资源阈值与consumer10秒硬限制不变。','启动只等待完整newline并validJSON的首行，再调用complete；2秒期限仍failclosed。','native/prepare/seal统一s14 prefix；内部mode/prefix/closed_logs不可覆盖command/nativecode，非prepare固定HERE==已pinCACHE。','seal继承未定义profile错误修复为实际FREEZE.profile，写入前验证0.1.14。','新S14 PNR专用source_after助手统计取已核集合长度；S13实跑collector PRE的44源记录未改变、未改判。','新模板SOURCE/G1/G2/RunIds/TOOLS_G2仍PENDING；ROOT须materialize新S14_RUNTIME_CONFIG，不复用旧配置。'],failed_attempts=['Git Bash自动转换Python argv导致native_capture启动前assert/native1，未创建wrapper记录；真实原生码见工具输出，不算成功。','新增回归r01真实native1：mock seal暴露继承NameError；first_generation保存当时四源码，stdout/stderr/native记录及全部失败夹具保留。','历史S13 native_capture缺mode/prefix/closed_logs，collector sealglob错用s12且profile未定义；本工具G1不追认历史seal成功。'],limitations=['这是Developer G1，不是独立G2；须另一Reviewer串行核当前冻结版本。','模拟history/Git/source及mock seal明确fixture，不是实跑或真实SOURCE冻结。','仅自有轻量canary；无Vivado/ROSS/RTL编译/综合/PNR/设备。','原生wrapper短命采样UNKNOWN按原件保留，后续已知身份ABSENT只为观察，不证明完整OS树或连续峰。','固定恢复映射只核并保存工具，不恢复覆盖S13原件。'],physical_g0='NOT_APPROVED',actual_source_before='NOT_RUN',actual_runtime='NOT_RUN',actual_budget='NOT_RUN',actual_sta='NOT_RUN',g3='NOT_RUN',g5='NOT_RUN',old_s11_budget='BLOCKED',stop=True)
save(W/'final_g1_receipt.json',receipt);copy(W/'final_g1_receipt.json',D/'final_g1_receipt.json')
raw=[]
for path in sorted(W.rglob('*')):
    if path.is_file():raw.append(copy(path,D/'raw'/path.relative_to(W)))
save(D/'g1_raw_mapping.json',dict(binding_rows=raw))
index=D/'raw_manifest.jsonl'
with index.open('x',encoding='utf-8',newline='\n') as stream:
    for row in raw:stream.write(json.dumps(row,ensure_ascii=False)+'\n')
files=[]
for path in sorted(D.rglob('*')):
    if path.is_file():files.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),role='source' if path.suffix=='.py' else 'log' if path.suffix in ('.bin','.log') else 'result'))
checks=[dict(name='工具轻量G1',status='PASS',command='已绑定逐项原生command/log/真实退出码；非一次单命令',exit_code=0,reason='复用回归+新边界+帮助与预期拒绝分别核验；失败不覆盖。')]
for name in ('独立工具G2','真实SOURCE与source-before','真实资源准入与唯一综合','实际预算及STA','G3实物与G5'):checks.append(dict(name=name,status='NOT_RUN',command=None,exit_code=None,reason='本工具准备不批准或执行该项。'))
manifest=dict(schema_version=1,stage='2B',task_id='S2B-T17',run_id=D.name,source_commit=mapping['source_commit'],evidence_dir=D.relative_to(ROOT).as_posix(),interfaces=[],tool_versions=dict(python=sys.version,psutil='7.2.2',profile='0.1.14模板；真实ROOT SOURCE未冻结'),files=files,checks=checks,limitations=['source_commit仅S13工具fork基线701dc，不是本次生产SOURCE；实际production SOURCE为null，工具实际字节均独立绑定。']+receipt['limitations'])
save(D/'delivery_manifest.json',manifest)
print(json.dumps(dict(status=receipt['status'],receipt_sha256=sha(D/'final_g1_receipt.json'),manifest_sha256=sha(D/'delivery_manifest.json'),raw_manifest_sha256=sha(index),raw_count=len(raw),tools=len(tools),methods=passed_methods,peak=receipt['sampled_owned_tree_peak_bytes'],elapsed=receipt['native_elapsed_seconds']),ensure_ascii=False))
