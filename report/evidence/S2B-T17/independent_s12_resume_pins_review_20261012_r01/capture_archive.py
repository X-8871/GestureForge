"""本轮原生轻量包装：记录实际身份、直接子终态和已知身份读回，未知不推断。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil

HERE = Path(__file__).absolute().parent
ROOT = HERE.parents[3]

def identity(process):
    return {'pid': process.pid, 'create_time': process.create_time()}

def read_identity(row):
    try:
        process = psutil.Process(row['pid'])
        same = process.create_time() == row['create_time']
        return dict(row, same_identity_exists=same, observed_status=process.status() if same else 'PID_REUSED')
    except psutil.NoSuchProcess:
        return dict(row, same_identity_exists=False, observed_status='NO_SUCH_PROCESS')
    except psutil.AccessDenied as error:
        return dict(row, same_identity_exists=None, observed_status='UNKNOWN_ACCESS_DENIED', exception=str(error))

def main():
    label, *command = sys.argv[1:]
    assert label.isidentifier() and command
    assert command[0] == 'C:\\Users\\22061\\AppData\\Local\\Programs\\Python\\Python312\\python.exe'
    outputs = [HERE/(label+suffix) for suffix in ('.stdout.bin', '.stderr.bin', '.native.json')]
    assert not any(path.exists() for path in outputs)
    launcher = psutil.Process()
    launcher_identity = identity(launcher)
    known = {}
    unknown = []
    peak = 0
    started = time.monotonic()
    failure = None
    child_identity = None
    code = None
    with outputs[0].open('xb') as stdout, outputs[1].open('xb') as stderr:
        child = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr)
        try:
            child_identity = identity(psutil.Process(child.pid))
            known[(child_identity['pid'], child_identity['create_time'])] = child_identity
        except (psutil.NoSuchProcess, psutil.AccessDenied) as error:
            unknown.append({'phase': 'direct_child_birth', 'pid': child.pid, 'create_time': None, 'exception_type': type(error).__name__, 'exception': str(error)})
        while True:
            processes = [launcher]
            try:
                processes += launcher.children(recursive=True)
            except (psutil.NoSuchProcess, psutil.AccessDenied) as error:
                unknown.append({'phase': 'descendant_enumeration', 'pid': getattr(error, 'pid', None), 'create_time': None, 'exception_type': type(error).__name__, 'exception': str(error)})
            rss = 0
            for process in processes:
                try:
                    row = identity(process)
                    rss += process.memory_info().rss
                    if process.pid != launcher.pid:
                        known[(row['pid'], row['create_time'])] = row
                except (psutil.NoSuchProcess, psutil.AccessDenied) as error:
                    unknown.append({'phase': 'identity_or_rss_sample', 'pid': process.pid, 'create_time': next((row['create_time'] for row in known.values() if row['pid']==process.pid), None), 'exception_type': type(error).__name__, 'exception': str(error)})
            peak = max(peak, rss)
            if rss > 268435456 or time.monotonic()-started > 120:
                failure = 'TREE_RSS_GT_256MiB' if rss > 268435456 else 'ELAPSED_GT_120_SECONDS'
                # 只终止本包装直接创建且出生身份已确认的子进程；不碰未知身份或外部进程。
                if child_identity is not None and read_identity(child_identity)['same_identity_exists'] is True:
                    child.terminate()
                break
            if child.poll() is not None:
                break
            time.sleep(0.05)
        try:
            code = child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            failure = (failure or '')+';DIRECT_CHILD_WAIT_TIMEOUT'
    terminal = [read_identity(row) for row in known.values()]
    result = {'command': command, 'wrapper_command': sys.orig_argv, 'cwd': str(ROOT), 'launcher_identity': launcher_identity,
        'direct_child_identity': child_identity, 'native_exit_code': code, 'direct_child_wait_returned': code is not None,
        'elapsed_seconds': time.monotonic()-started, 'sampled_owned_tree_peak_bytes': peak, 'sample_interval_seconds': 0.05,
        'unknown_samples': unknown, 'unknown_count': len(unknown), 'absolute_tree_peak_bytes': None,
        'known_descendant_identity_terminal_observations': terminal, 'known_descendants_same_identity_absent_at_observation': bool(terminal) and all(row['same_identity_exists'] is False for row in terminal),
        'launcher_terminal': 'RUNNING_WHEN_RECORD_WRITTEN', 'entire_os_tree_terminal': 'NOT_PROVEN_BY_DISCRETE_ENUMERATION', 'budget_stop': failure,
        'python': sys.version, 'psutil': psutil.__version__,
        'stdout': {'path': outputs[0].relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(outputs[0].read_bytes()).hexdigest(), 'bytes': outputs[0].stat().st_size},
        'stderr': {'path': outputs[1].relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(outputs[1].read_bytes()).hexdigest(), 'bytes': outputs[1].stat().st_size}}
    with outputs[2].open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps(result, ensure_ascii=False))
    return 1 if failure is not None or code is None else code

if __name__=='__main__': sys.exit(main())
