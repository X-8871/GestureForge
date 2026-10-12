"""独立只读核查本轮启动绑定；只创建本目录证据，不执行Vivado。"""
import ast
from datetime import datetime, timedelta, timezone
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
WORK = ROOT/'tmp/2B/S2B-T17/s12_launch_prepare_20261012_r01'
BASE = ROOT/'tmp/2B/S2B-T17/s12_physical_resume_prepare_20261012_r01'
RUN = ROOT/'tmp/2B/S2B-T17/s12_physical_launch_root_20261012_r01'
PRE = ROOT/'report/evidence/S2B-T17/s12_launch_source_preflight_20261012_r01'
HEAD = '467463757158aed80d6f75afadff6a8458614a29'
GIT = 'C:/Program Files/Git/bin/git.exe'
CASES = []
RUNS = []
START = time.monotonic()

def sha(data):
    """按原始字节计算哈希。"""
    return hashlib.sha256(data).hexdigest()

def exact(path, directory=False):
    """逐组件核查真实完整名称与目标类型，拒绝链接。"""
    current = Path(path.anchor)
    for part in path.parts[1:]:
        matches = [p for p in current.iterdir() if p.name == part]
        assert len(matches) == 1, str(path)
        current = matches[0]
        assert not current.is_symlink() and not current.is_junction(), str(path)
    assert current.is_dir() if directory else current.is_file(), str(path)
    return current

def load(path):
    """只读UTF-8对象。"""
    return json.loads(exact(path).read_text(encoding='utf-8'))

def put(name, data):
    """仅创建隔离审查目录的新证据。"""
    exact(HERE, True)
    with (HERE/name).open('xb') as stream:
        stream.write(data)

def write(name, value):
    """保存UTF-8独立结果。"""
    put(name, (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))

def bind(path):
    """读取并绑定真实文件。"""
    data = exact(path).read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(data), bytes=len(data))

def run(label, args, input_data=None):
    """保留真实直接子进程返回值、身份和必要日志。"""
    if (HERE/(label+'.stdout.bin')).exists():
        label += '_r02'
    begin = time.monotonic()
    with (HERE/(label+'.stdout.bin')).open('xb') as out, (HERE/(label+'.stderr.bin')).open('xb') as err:
        child = subprocess.Popen(args, cwd=ROOT, stdin=subprocess.PIPE if input_data is not None else subprocess.DEVNULL, stdout=out, stderr=err)
        try:
            birth = psutil.Process(child.pid).create_time()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            birth = 'UNKNOWN'
        child.communicate(input_data, timeout=60)
        code = child.wait(timeout=1)
    value = dict(command=args, cwd=str(ROOT), pid=child.pid, create_time=birth,
                 native_exit_code=child.returncode, direct_wait_exit_code=code,
                 elapsed_seconds=time.monotonic()-begin, terminal_state='EXITED_DIRECT_CHILD_WAIT',
                 stdout=bind(HERE/(label+'.stdout.bin')), stderr=bind(HERE/(label+'.stderr.bin')),
                 internal_git_identity='UNKNOWN', whole_tree_terminal='UNKNOWN')
    write(label+'.native.json', value)
    RUNS.append(value)
    assert code == child.returncode == 0, label
    return (HERE/(label+'.stdout.bin')).read_bytes()

def rejected(name, callback):
    """代表性反例只能只读，意外放行立即失败。"""
    try:
        callback()
    except ValueError as error:
        CASES.append(dict(name=name, status='REJECTED_EXPECTED', message=str(error), fixture_only=True))
    else:
        raise AssertionError('反例意外通过：'+name)

def main():
    """核实真实源绑定及运行身份，不替代物理验收。"""
    exact(ROOT, True); exact(HERE, True); exact(WORK, True); exact(RUN, True)
    expected = {
        WORK/'source_freeze.json': '887440ebb81fbec718670aacbf1cb3bfaa9e6e5641199e92d15ee37ca16dd8f0',
        WORK/'compat_pins.py': '6f0584248d4380f7750575a80b14abeb16305cb2a30eaba8a97193ad4f45a4bf',
        WORK/'tool_binding.json': '677dcb5a70dca17204db9c40b25811a1dd5570d948c89c43d5d59089f0d8a6a2',
        PRE/'delivery_manifest.json': '516a37bb63dd2b9d0adaf4ae5489215eb9fa232a79313eef308363f44acdd189',
        PRE/'source_before.json': '663e79742115a5eb04c9d3bdb2cfa7f60b47b951d17edc43dd3aae9979e23066',
        RUN/'resource_plan.json': '74bab7c749b2ba05f1d1bbaa0e785c13f294ef0f41d5664de131b912d32519d6',
        RUN/'owned_binding.json': 'e50b46d67d5cf0cba20ad90d0812e8701962bfbeec3ce47e04d01532703d5774'}
    for path, digest in expected.items():
        assert bind(path)['sha256'] == digest, str(path)
    manifest = load(PRE/'delivery_manifest.json')
    for item in manifest['files']:
        assert bind(ROOT/item['path'])['sha256'] == item['sha256'], item['path']
    tools = load(WORK/'tool_binding.json')
    assert tools['common_sha'] == '61916205c4993ae856e6ba9afbb198f2cfee1f36b76aff27743e916880beeaad'
    for item in tools['tools']:
        assert bind(WORK/item['path'])['sha256'] == item['sha256']
        if item['path'] != 'compat_pins.py':
            assert (WORK/item['path']).read_bytes() == exact(BASE/item['path']).read_bytes()
    old = ast.parse(exact(BASE/'compat_pins.py').read_text(encoding='utf-8')).body
    new = ast.parse(exact(WORK/'compat_pins.py').read_text(encoding='utf-8')).body
    assert len(old) == len(new)
    changes = []
    for left, right in zip(old, new):
        if ast.dump(left) != ast.dump(right):
            assert isinstance(left, ast.Assign) and isinstance(right, ast.Assign)
            assert left.targets[0].id == right.targets[0].id
            changes.append(left.targets[0].id)
    assert set(changes) == {'SOURCE_COMMIT','SOURCE_FREEZE_SHA','SOURCE_PRE','SYNTH_REPORT','PNR_REPORT'}
    git = [GIT, '-c', 'core.longpaths=true', '-c', 'maintenance.auto=false']
    assert run('actual_head', git+['rev-parse','HEAD']).decode('ascii').strip() == HEAD
    frozen = load(WORK/'source_freeze.json'); rows = frozen['source_files']
    assert frozen['source_commit'] == HEAD and len(rows) == len({r['path'] for r in rows}) == 43
    specs = [c+':'+r['path'] for r in rows for c in ('09b4c6f60fb74c2fda1b56d2f316ca374dfae7cf','09e0135234ed257d1f878b80bf63eeefcdc6143f',HEAD)]
    batch = ('\n'.join(specs)+'\n').encode('utf-8')
    if not (HERE/'git_batch_request.txt').exists():
        put('git_batch_request.txt', batch)
    else:
        assert (HERE/'git_batch_request.txt').read_bytes() == batch
    result = run('git_batch', git+['cat-file','--batch-check'], batch).decode('ascii').splitlines()
    raw_count = 0
    for i, row in enumerate(rows):
        raw = exact(ROOT/row['path']).read_bytes()
        assert sha(raw) == row['sha256'] and len(raw) == row['bytes']
        assert raw == exact(ROOT/row['snapshot']).read_bytes()
        historical = row['historical_git_native']
        assert historical['native_exit_code'] == 0
        blob = exact(ROOT/historical['stdout']['path']).read_bytes()
        assert sha(blob) == row['git_blob_sha256'] == historical['stdout']['sha256']
        assert sha(exact(ROOT/historical['stderr']['path']).read_bytes()) == historical['stderr']['sha256']
        oid = hashlib.sha1(b'blob '+str(len(blob)).encode('ascii')+b'\0'+blob).hexdigest()
        assert result[i*3:i*3+3] == [oid+' blob '+str(len(blob))]*3
        if blob == raw:
            assert row['git_relation'] == 'RAW_IDENTICAL'; raw_count += 1
        else:
            assert b'\r\n' not in blob and blob.replace(b'\n',b'\r\n') == raw
            assert row['git_relation'] == 'GIT_LF_TO_RAW_CRLF'
    assert raw_count == 37
    sys.path.insert(0, str(WORK))
    import compat_pins as pins
    import collector
    pins.require_ready()
    _, hashes, static, profile = collector.load_freeze()
    assert len(hashes) == 43 and len(static) == 33 and profile['vivado_part'] == 'xc7z020clg400-2'
    paths = [pins.SYNTH_CACHE,pins.PNR_CACHE,pins.PROJECT,pins.SYNTH_REPORT,pins.PNR_REPORT,pins.SOURCE_PRE]
    assert len(set(paths)) == 6
    assert not pins.SYNTH_REPORT.exists() and not pins.PNR_REPORT.exists() and not pins.PROJECT.exists()
    before = load(PRE/'source_before.json')
    assert before['source_commit'] == before['actual_head_at_check'] == HEAD
    assert {r['path']:r['sha256'] for r in before['source_files']} == hashes
    CASES.append(dict(name='实际pins/load_freeze及43源129Git对象/33static/18RTL/8派生/原14',status='PASS'))
    rejected('缺真实综合依赖PNR', lambda:pins.require_ready(True))
    rejected('错误CLI提交', lambda:collector.source('0'*40,'before'))
    with patch.object(collector,'git',return_value=(('0'*40+'\n').encode('ascii'),['fixture'])):
        rejected('错误实际HEAD响应',lambda:collector.source(HEAD,'before'))
    with patch.object(pins,'SOURCE_FREEZE_SHA','0'*64):
        rejected('冻结SHA漂移',lambda:pins.require_ready())
    plan=load(RUN/'resource_plan.json'); owned=load(RUN/'owned_binding.json')
    assert plan['source_commit'] == owned['source_commit'] == HEAD
    for key, value in {'new_run_tree_rss_limit_bytes':6442450944,'new_run_available_ram_stop_bytes':536870912,'minimum_c_disk_free_before_dispatch_bytes':8589934592,'resource_sample_interval_seconds':1,'supervisor_live_interval_seconds':5,'no_log_progress_stop_seconds':900,'launch_jobs':1,'general_maxThreads':1,'simultaneous_heavy':1}.items():
        assert plan[key] == value, key
    assert owned['no_progress_seconds'] == 900 and not owned.get('fixture_test',False)
    assert plan['startup_ram_minimum_waiver_authorized'] and plan['actual_pre_start_ram_bytes'] >= 4831838208
    assert owned['pid'] == 5832 and owned['create_time'] == 1791766374.8010526 and Path(owned['cwd']) == RUN
    assert set(map(Path,owned['allowed_run_dirs'])) == {RUN,WORK}
    for key, digest in [('GUARD','a2f5c581b79a40116bf59c240a7b8c0fe35bac4db7b26a79ce5ba14c451a18ac'),('SUP','193416f869463c38065e257545720032438ab12c7bbe30beec6bc8c53d8f9ca0')]:
        assert bind(getattr(pins,key))['sha256'] == digest
    process=psutil.Process(owned['pid'])
    identity=dict(pid=process.pid,create_time=process.create_time(),exe=process.exe(),cwd=process.cwd(),cmdline=process.cmdline(),ppid=process.ppid())
    assert all(identity[k] == owned[k] for k in identity)
    assert process.is_running() and psutil.Process(owned['pid']).create_time() == owned['create_time']
    journal=[json.loads(line) for line in exact(RUN/'supervision/supervision.jsonl').read_text(encoding='utf-8').splitlines()]
    ready=[r for r in journal if r.get('kind') == 'READY']
    assert len(ready) == 1 and not any(r.get('kind') == 'TERMINAL' for r in journal)
    guard=ready[0]['guard_identity']; gp=psutil.Process(guard['pid'])
    assert guard['pid'] == 23572 and guard['create_time'] == 1791766495.4617307
    assert gp.create_time() == guard['create_time'] and gp.cmdline() == guard['cmdline']
    capture=bind(RUN/'capture_owned.py')
    CASES.append(dict(name='ROOT计划固定阈值/自有PID真实身份/已审保护工具/READY',status='PASS'))
    assert run('actual_head_after',git+['rev-parse','HEAD']).decode('ascii').strip() == HEAD
    for path,digest in expected.items():
        assert bind(path)['sha256'] == digest
    receipt=dict(status='PASS_LAUNCH_PINS_G2_ONLY', source_commit=HEAD,
                 reviewed_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),
                 elapsed_seconds=time.monotonic()-START, frozen_inputs=[bind(p) for p in expected],
                 capture_owned=capture, manifest_files_checked=len(manifest['files']), changed_constants=changes,
                 cases=CASES, source_count=43, raw_identical=37, exact_eol=6, git_objects=129,
                 root_identity_snapshot=identity, guard_identity_snapshot=guard, native_runs=RUNS,
                 python=sys.version,psutil=psutil.__version__, production_modified=False,
                 reviewer_script=bind(Path(__file__).absolute()), vivado_calls=0, hardware_calls=0,
                 limitations=['仅批准本次最终启动输入及保护绑定G2；实际综合、STA、PNR、bit、硬件/G3-G5未验收。',
                 '错误HEAD等反例为只读mock，不切换共享HEAD或改写PRE。',
                 'guard与supervisor完整逻辑沿用固定SHA独审，本轮未重跑旧全套回归。',
                 '身份与READY为读时快照，运行文件动态变化；不承诺连续绝对峰值或OS原子全树关闭。',
                 '直接Git子进程已wait；内部子进程身份、全树终态及峰值内存UNKNOWN。',
                 '未调整模型运行参数；子代理模型/effort由父代理实际派发控制。',
                 '审查首运行原生1：本脚本误读profile.part导致KeyError；已改实际vivado_part字段，首轮Git日志保留。'])
    write('final_review_receipt.json',receipt)
    print(json.dumps(dict(status=receipt['status'],receipt=bind(HERE/'final_review_receipt.json'), elapsed_seconds=receipt['elapsed_seconds']),ensure_ascii=False))

if __name__ == '__main__':
    main()
