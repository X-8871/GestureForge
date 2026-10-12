"""只绑定本轮真实源码与启动目录，所有检查均为离线轻量操作。"""
import ast
from datetime import datetime, timezone, timedelta
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import patch
import psutil

HERE = Path(__file__).absolute().parent
ROOT = HERE.parents[3]
BASE = ROOT / 'tmp/2B/S2B-T17/s12_physical_resume_prepare_20261012_r01'
PRE = ROOT / 'report/evidence/S2B-T17/s12_launch_source_preflight_20261012_r01'
OLDPRE = ROOT / 'report/evidence/S2B-T17/s12_resume_source_preflight_20261012_r01'
HEAD = '467463757158aed80d6f75afadff6a8458614a29'
CODE = '09b4c6f60fb74c2fda1b56d2f316ca374dfae7cf'
GIT = Path('C:/Program Files/Git/bin/git.exe')
EXPECTED_MANIFEST = '5d8e1316caf593f417645fd4f05c7db26784fcadb15b85a5f55e4e74bf9216ff'
EXPECTED_FREEZE = 'f8cbae8ce77e6caa7945d2e6485c28bc93a12ef0226d59c2abd8f42e38b01b77'
RUNS = []

def sha(data):
    """原字节哈希，不修改换行。"""
    return hashlib.sha256(data).hexdigest()

def exact(path, directory=False):
    """逐组件校验精确名称、类型与链接。"""
    current = Path(path.anchor)
    for part in path.parts[1:]:
        hits = [p for p in current.iterdir() if p.name == part]
        assert len(hits) == 1, str(path)
        current = hits[0]
        assert not current.is_symlink() and not current.is_junction(), str(path)
    assert current.is_dir() if directory else current.is_file(), str(path)
    return current

def put(path, data):
    """只能创建授权的新目录中的文件。"""
    assert path.is_relative_to(HERE) or path.is_relative_to(PRE)
    exact(path.parent, True)
    with path.open('xb') as stream:
        stream.write(data)

def write(path, value):
    """创建中文UTF-8证据。"""
    put(path, (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))

def bind(path):
    """返回仓库相对路径及原字节绑定。"""
    data = exact(path).read_bytes()
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(data), 'bytes': len(data)}

def run(label, command, input_data=None, expected=0):
    """保存直接子进程原生退出、出生时间和输出，不依赖宿主退出归一化。"""
    start = time.monotonic()
    out = HERE / (label+'.stdout.bin')
    err = HERE / (label+'.stderr.bin')
    with out.open('xb') as stdout, err.open('xb') as stderr:
        child = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.PIPE if input_data is not None else subprocess.DEVNULL, stdout=stdout, stderr=stderr)
        try:
            birth = psutil.Process(child.pid).create_time()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            birth = 'UNKNOWN'
        child.communicate(input=input_data, timeout=120)
        direct_wait = child.wait(timeout=1)
    record = {'command': command, 'cwd': str(ROOT), 'pid': child.pid, 'create_time_unix': birth,
              'native_exit_code': child.returncode, 'direct_wait_exit_code': direct_wait,
              'terminal_state': 'EXITED_DIRECT_CHILD_WAIT', 'elapsed_seconds': time.monotonic()-start,
              'stdout': bind(out), 'stderr': bind(err), 'input': None if input_data is None else {'sha256': sha(input_data), 'bytes': len(input_data)},
              'peak_memory_bytes': 'UNKNOWN', 'inner_child_pid_create_time': 'UNKNOWN'}
    write(HERE/(label+'.native.json'), record)
    RUNS.append(record)
    assert direct_wait == child.returncode == expected, (label, record, err.read_bytes().decode('utf-8', errors='replace'))
    return out.read_bytes(), record

def derive():
    """复用旧快照与Git原件，只生成新的当前HEAD绑定。"""
    exact(ROOT, True); exact(HERE, True); exact(BASE, True); exact(PRE.parent, True); exact(GIT)
    for target in (PRE, ROOT/'report/evidence/S2B-T17/s12_platform_20261012_r03', ROOT/'report/evidence/S2B-T17/s12_implementation_20261012_r03'):
        assert not target.exists(), str(target)
    assert sha(exact(OLDPRE/'delivery_manifest_r05.json').read_bytes()) == EXPECTED_MANIFEST
    freeze_bytes = exact(BASE/'source_freeze.json').read_bytes()
    assert sha(freeze_bytes) == EXPECTED_FREEZE
    assert sha(exact(OLDPRE/'source_freeze.json').read_bytes()) == EXPECTED_FREEZE
    freeze = json.loads(freeze_bytes)
    rows = freeze['source_files']
    assert len(rows) == len({r['path'] for r in rows}) == 43
    gitbase = [str(GIT), '-c', 'core.longpaths=true', '-c', 'maintenance.auto=false']
    actual, _ = run('head_before', gitbase+['rev-parse', 'HEAD'])
    assert actual.decode('ascii').strip() == HEAD
    staged, _ = run('staged_before', gitbase+['diff', '--cached', '--name-only'])
    assert not staged.strip()
    status, _ = run('status_before', gitbase+['status', '--short', '--untracked-files=normal'])
    assert status.decode('utf-8').count('?? ') == 2 and not any(line[:2] != '??' for line in status.decode('utf-8').splitlines())
    specs = [commit+':'+row['path'] for row in rows for commit in (CODE, freeze['source_commit'], HEAD)]
    request = ('\n'.join(specs)+'\n').encode('utf-8')
    put(HERE/'git_batch_request.txt', request)
    output, native = run('git_batch', gitbase+['cat-file', '--batch-check'], request)
    result = output.decode('ascii').splitlines()
    assert len(result) == 129
    object_rows = []
    for index, row in enumerate(rows):
        raw = exact(ROOT/row['path']).read_bytes()
        assert sha(raw) == row['sha256'] and len(raw) == row['bytes']
        assert exact(ROOT/row['snapshot']).read_bytes() == raw
        old_native = row['git_native']
        assert old_native['native_exit_code'] == 0
        blob = exact(ROOT/old_native['stdout']['path']).read_bytes()
        assert sha(blob) == row['git_blob_sha256'] == old_native['stdout']['sha256']
        assert len(blob) == old_native['stdout']['bytes']
        assert sha(exact(ROOT/old_native['stderr']['path']).read_bytes()) == old_native['stderr']['sha256']
        oid = hashlib.sha1(b'blob '+str(len(blob)).encode('ascii')+b'\0'+blob).hexdigest()
        expected = oid+' blob '+str(len(blob))
        assert result[index*3:index*3+3] == [expected]*3, row['path']
        relation = 'RAW_IDENTICAL' if raw == blob else 'GIT_LF_TO_RAW_CRLF'
        assert raw == blob or (b'\r\n' not in blob and blob.replace(b'\n', b'\r\n') == raw)
        assert relation == row['git_relation']
        row['historical_git_native'] = row.pop('git_native')
        row['git_native'] = dict(native, batch_request_index=index*3+2, blob_oid=oid, raw_blob_reused=old_native['stdout'])
        object_rows.append({'path': row['path'], 'actual_head': HEAD, 'code_commit': CODE, 'old_evidence_head': freeze['source_commit'],
                            'git_blob_oid': oid, 'git_blob_sha256': sha(blob), 'raw_sha256': sha(raw), 'git_relation': relation,
                            'batch_indexes': [index*3, index*3+1, index*3+2], 'snapshot_reused': row['snapshot'], 'git_raw_reused': old_native['stdout']})
    assert sum(r['git_relation']=='RAW_IDENTICAL' for r in rows) == 37
    assert sum(r['git_relation']=='GIT_LF_TO_RAW_CRLF' for r in rows) == 6
    freeze['source_commit'] = HEAD
    freeze['created_at_utc8'] = datetime.now(timezone(timedelta(hours=8))).isoformat()
    freeze['code_commit_unchanged_objects'] = {'source_commit': CODE, 'actual_head': HEAD, 'source_count': 43, 'raw_identical': 37, 'exact_eol': 6,
        'object_equivalence_path': (HERE/'source_object_equivalence.json').relative_to(ROOT).as_posix(),
        'scope': '129个Git对象实际batch-check；43当前HEAD对象OID与复用Git原件一致，生产RAW及快照按旧freeze逐项校验'}
    write(HERE/'source_object_equivalence.json', {'status': 'PASS_43_CURRENT_HEAD_GIT_AND_RAW', 'source_commit': HEAD, 'code_commit': CODE, 'rows': object_rows, 'batch_native': native})
    write(HERE/'source_freeze.json', freeze)
    freeze_sha = sha((HERE/'source_freeze.json').read_bytes())
    old_binding = json.loads(exact(BASE/'tool_binding.json').read_text(encoding='utf-8'))
    tools = []
    changed = []
    for item in old_binding['tools']:
        name = item['path']; prior = exact(BASE/name).read_bytes()
        assert sha(prior) == item['sha256']
        content = prior
        if name == 'compat_pins.py':
            assert sha(prior) == '0531ba2f6fbf92515806c686731b485489bf0b6f1d6fae57a7e99b87e71e783a'
            changes = {
                "SOURCE_COMMIT = '09e0135234ed257d1f878b80bf63eeefcdc6143f'": "SOURCE_COMMIT = '"+HEAD+"'",
                "SOURCE_FREEZE_SHA = '"+EXPECTED_FREEZE+"'": "SOURCE_FREEZE_SHA = '"+freeze_sha+"'",
                's12_resume_source_preflight_20261012_r01': PRE.name,
                's12_platform_20261012_r02': 's12_platform_20261012_r03',
                's12_implementation_20261012_r02': 's12_implementation_20261012_r03'}
            for before, after in changes.items():
                assert content.count(before.encode('utf-8')) == 1
                content = content.replace(before.encode('utf-8'), after.encode('utf-8'))
            oldnodes, newnodes = ast.parse(prior.decode('utf-8')).body, ast.parse(content.decode('utf-8')).body
            assert len(oldnodes) == len(newnodes)
            for old, new in zip(oldnodes, newnodes):
                if ast.dump(old, include_attributes=False) != ast.dump(new, include_attributes=False):
                    assert isinstance(old, ast.Assign) and isinstance(new, ast.Assign)
                    assert old.targets[0].id == new.targets[0].id
                    changed.append(old.targets[0].id)
            assert set(changed) == {'SOURCE_COMMIT', 'SOURCE_FREEZE_SHA', 'SOURCE_PRE', 'SYNTH_REPORT', 'PNR_REPORT'}
        ast.parse(content.decode('utf-8'))
        put(HERE/name, content)
        if content != prior:
            put(HERE/(name+'.diff'), ''.join(difflib.unified_diff(prior.decode('utf-8').splitlines(True), content.decode('utf-8').splitlines(True), fromfile='resume/'+name, tofile='launch/'+name)).encode('utf-8'))
        tools.append({'path': name, 'sha256': sha(content), 'bytes': len(content), 'baseline_sha256': sha(prior), 'changed': content != prior})
    for name in ('synth_cache', 'pnr_cache'):
        (HERE/name).mkdir()
    binding = {'status': 'STOP_LAUNCH_PINS_G1_PENDING_INDEPENDENT_G2', 'source_commit': HEAD, 'code_commit': CODE,
        'source_freeze': bind(HERE/'source_freeze.json'), 'tools': tools, 'changed_files': ['compat_pins.py'], 'changed_constants': changed,
        'function_logic_changed': False, 'common_sha': old_binding['common_sha'], 'source_count': 43, 'static_count': 33, 'git_raw_identical': 37,
        'git_eol_exact': 6, 'pnr_synth_dependencies': 'None/PENDING', 'heavy_or_hardware': False,
        'reused_manifest': bind(OLDPRE/'delivery_manifest_r05.json'), 'reused_freeze': bind(OLDPRE/'source_freeze.json'),
        'reused_functional_g1': freeze['functional_g1'], 'reused_functional_g2': freeze['functional_g2']}
    assert binding['common_sha'] == '61916205c4993ae856e6ba9afbb198f2cfee1f36b76aff27743e916880beeaad'
    write(HERE/'tool_binding.json', binding)
    write(HERE/'execution_plan.json', {'source_commit': HEAD, 'code_commit': CODE, 'source_freeze': bind(HERE/'source_freeze.json'), 'runtime': str(HERE),
        'source_pre': str(PRE), 'synth_report': str(ROOT/'report/evidence/S2B-T17/s12_platform_20261012_r03'),
        'pnr_report': str(ROOT/'report/evidence/S2B-T17/s12_implementation_20261012_r03'),
        'runtime_prepared': True, 'actual_vivado_session': 'NOT_RUN', 'actual_synthesis': 'NOT_RUN', 'actual_pnr': 'NOT_RUN',
        'user_resource_authorization': '用户允许启动时RAM低于4.5GiB；仅启动RAM门槛覆盖，ROOT保留运行监测',
        'resource_sample': {'available_ram_bytes': psutil.virtual_memory().available, 'c_disk_free_bytes': psutil.disk_usage('C:\\').free},
        'limit': '不启动Vivado、重型任务或硬件；PNR仍需实际综合G1/G2冻结；真正source-before按未修改collector创建一套必要快照。'})

def pin_tests():
    """只做新绑定受影响门禁的最小真实及内存反例检查。"""
    sys.path.insert(0, str(HERE))
    import compat_pins as pins
    import collector
    cases = []
    pins.require_ready()
    freeze, hashes, static, _ = collector.load_freeze()
    assert len(hashes) == 43 and len(static) == 33
    cases.append({'name': '真实launch pins与43源码', 'status': 'PASS'})
    def rejected(name, action):
        try:
            action()
        except ValueError as error:
            cases.append({'name': name, 'status': 'REJECTED_EXPECTED', 'exception': str(error), 'fixture_only': True})
        else:
            raise AssertionError(name+'误接受')
    rejected('PNR仍缺实际综合G1/G2', lambda: pins.require_ready(pnr=True))
    different = '09e0135234ed257d1f878b80bf63eeefcdc6143f'
    rejected('source CLI异commit', lambda: collector.source(different, 'before'))
    with patch.object(collector, 'git', return_value=(different.encode('ascii'), [])):
        rejected('HEAD异commit', lambda: collector.source(HEAD, 'before'))
    with patch.object(collector, 'read', return_value=dict(freeze, source_commit=different)):
        rejected('freeze异commit', collector.load_freeze)
    rejected('freeze SHA漂移', lambda: pins.pinned(pins.SOURCE_FREEZE, '0'*64))
    assert pins.WORK == HERE and pins.PROJECT == HERE/'project'
    assert pins.SYNTH_CACHE == HERE/'synth_cache' and pins.PNR_CACHE == HERE/'pnr_cache'
    assert pins.SYNTH_MANIFEST_SHA is pins.SYNTH_G2_SHA is pins.SYNTH_G2_EXPECTED_STATUS is None
    assert not pins.PROJECT.exists() and not pins.SYNTH_REPORT.exists() and not pins.PNR_REPORT.exists()
    before = json.loads((PRE/'source_before.json').read_text(encoding='utf-8'))
    assert before['source_commit'] == HEAD and {r['path']:r['sha256'] for r in before['source_files']} == hashes
    for row in before['source_files']:
        assert sha(exact(ROOT/row['snapshot']).read_bytes()) == row['sha256']
        assert sha(exact(ROOT/row['path']).read_bytes()) == row['sha256']
    cases.append({'name': '真实source-before43快照与生产RAW稳定', 'status': 'PASS', 'inner_git_pid_create_time': 'UNKNOWN'})
    write(HERE/'launch_pins_test_receipt.json', {'status': 'PASS_LAUNCH_PINS_G1_ONLY', 'cases': cases,
        'actual_hardware_or_vivado': 'NOT_RUN', 'scope': '只重查本次五常量绑定和HEAD/freeze/PNR门禁，既有完整门禁回归按原SHA复用'})

def seal(filename):
    """只归档新增的小工具及本轮原生结果，不复制历史包。"""
    files = []
    for path in sorted(PRE.rglob('*')):
        if path.is_file() and path.name != filename:
            files.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path.read_bytes()), role='source' if 'source_snapshot' in path.parts else 'artifact',
                              keep_reason='本轮真实启动绑定及source-before原件，不代表综合或实物通过'))
    for path in sorted(HERE.glob('*')):
        if path.is_file():
            files.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path.read_bytes()), role='artifact', keep_reason='本轮工具与原生离线结果，运行目录固定保留'))
    freeze = json.loads((HERE/'source_freeze.json').read_text(encoding='utf-8'))
    reused = [OLDPRE/'delivery_manifest_r05.json', OLDPRE/'source_freeze.json', ROOT/freeze['functional_g1']['path'], ROOT/freeze['functional_g2']['path']]
    for path in reused:
        files.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(exact(path).read_bytes()), role='input', keep_reason='复用已固定输入SHA；不复制旧包，不继承为真实综合通过'))
    checks = [{'name': '离线launch绑定和真实source-before', 'status': 'PASS', 'command': sys.orig_argv, 'exit_code': 0, 'reason': '43 RAW稳定、当前HEAD Git对象一致，prepare/source-before及最小门禁检查真实完成'},
              {'name': '真实Vivado综合及实现', 'status': 'NOT_RUN', 'command': 'ROOT尚未派发真实Vivado综合；PNR缺综合G1/G2', 'exit_code': None, 'reason': '本Developer仅负责离线最小启动输入，实际综合、PNR与板上验证均未执行'}]
    write(PRE/filename, {'schema_version': 1, 'stage': '2B', 'task_id': 'S2B-T17', 'run_id': PRE.name, 'source_commit': HEAD,
        'evidence_dir': PRE.relative_to(ROOT).as_posix(), 'interfaces': [],
        'interfaces_not_applicable_reason': '本次仅重绑当前源码HEAD及运行目录，沿用已核实平台业务候选和功能G1/G2，没有新增物理接口冻结。',
        'files': files, 'checks': checks, 'tool_versions': {'python': sys.version, 'psutil': psutil.__version__, 'git': '由git_version真实原生输出绑定'},
        'limitations': ['尚未独立审查，不批准综合、PNR或实物验收。', 'evidence包装0仅表示绑定完整；inputs真实NOT_RUN预期2。',
                        '进程出生及direct wait只记录直接子进程；collector内部Git调用未独立采集PID，明确UNKNOWN。',
                        '峰值内存与完整工具调用量未测；启动RAM覆盖仅由ROOT按用户明确授权决定。']})

def main():
    """按依赖顺序完成真实离线启动检查后停止写入。"""
    derive()
    py = [sys.executable, '-X', 'utf8', '-B']
    collector = str(HERE/'collector.py')
    run('git_version', [str(GIT), '-c', 'core.longpaths=true', '-c', 'maintenance.auto=false', '--version'])
    run('source_before', py+[collector, 'source', '--commit', HEAD, '--phase', 'before'])
    run('prepare', py+[collector, 'prepare'])
    for name in ('collector', 'impl_collector', 'source_after_check', 'native_source_after', 'native'):
        run('help_'+name, py+[str(HERE/(name+'.py')), '--help'])
    pin_tests()
    final, _ = run('head_after', [str(GIT), '-c', 'core.longpaths=true', '-c', 'maintenance.auto=false', 'rev-parse', 'HEAD'])
    assert final.decode('ascii').strip() == HEAD
    for name in ('source_freeze.json', 'tool_binding.json', 'execution_plan.json', 'source_object_equivalence.json', 'prepared_receipt.json', 'launch_pins_test_receipt.json'):
        put(PRE/name, (HERE/name).read_bytes())
    toolsdir = PRE/'tools'; toolsdir.mkdir()
    for name in ('collector.py', 'impl_collector.py', 'source_after_check.py', 'native_source_after.py', 'native.py', 'compat_pins.py', 'compat_pins.py.diff', 'launch_prepare.py'):
        put(toolsdir/name, (HERE/name).read_bytes())
    write(PRE/'author_receipt.json', {'status': 'STOP_LAUNCH_PREPARED_G1_ONLY', 'source_commit': HEAD, 'code_commit': CODE,
        'runs': RUNS, 'source_stable_count': 43, 'runtime_ready': True, 'actual_synth_pnr_hardware': 'NOT_RUN',
        'environment_exception': '初次默认Git长路径假删除与sandbox阻止Python执行保留在会话工具原件；core.longpaths=true核实只有两个既有无关untracked目录；自动审批允许原Python312原生执行。',
        'peak_memory_bytes': 'UNKNOWN', 'independent_g2': 'NOT_RUN'})
    seal('delivery_manifest_precheck.json')
    manifest = str(PRE/'delivery_manifest_precheck.json')
    run('precheck_evidence', py+[str(ROOT/'verification/check_stage_delivery.py'), '--mode', 'evidence', '--manifest', manifest])
    run('precheck_inputs', py+[str(ROOT/'verification/check_stage_delivery.py'), '--mode', 'inputs', '--manifest', manifest], expected=2)
    seal('delivery_manifest.json')
    manifest = str(PRE/'delivery_manifest.json')
    run('final_evidence', py+[str(ROOT/'verification/check_stage_delivery.py'), '--mode', 'evidence', '--manifest', manifest])
    run('final_inputs', py+[str(ROOT/'verification/check_stage_delivery.py'), '--mode', 'inputs', '--manifest', manifest], expected=2)
    print(json.dumps({'status': 'STOP_LAUNCH_PINS_G1_ONLY', 'runtime': str(HERE), 'source_pre': str(PRE),
                     'freeze': bind(HERE/'source_freeze.json'), 'helper': bind(HERE/'compat_pins.py'),
                     'tool_binding': bind(HERE/'tool_binding.json'), 'manifest': bind(PRE/'delivery_manifest.json'),
                     'source_count': 43, 'git_raw': 37, 'git_eol': 6, 'runtime_prepared': True,
                     'evidence_exit': 0, 'inputs_exit': 2, 'actual_synth_pnr_hardware': 'NOT_RUN'}, ensure_ascii=False))

if __name__ == '__main__':
    main()
