"""本轮原生轻量包装：记录实际身份、直接子终态和已知身份读回，未知不推断。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil
import native_contract as contract
import compat_pins

HERE = Path(__file__).absolute().parent
ROOT = HERE.parents[3]

def identity(process):
    birth = process.create_time()
    row = {'pid': process.pid, 'create_time': birth, 'exe': process.exe(), 'cwd': process.cwd(), 'cmdline': process.cmdline(), 'ppid': process.ppid()}
    if not process.is_running() or psutil.Process(process.pid).create_time() != birth:
        raise RuntimeError('采集身份漂移')
    return row

def read_identity(row):
    try:
        process = psutil.Process(row['pid'])
        if process.create_time() != row['create_time']:
            return dict(row, same_identity_exists=False, observed_status='PID_REUSED',new_object_untouched=True)
        actual=identity(process)
        same=all(actual[k]==row[k] for k in ('pid','create_time','exe','cwd','cmdline','ppid'))
        return dict(row, same_identity_exists=True if same else None, observed_status='ALIVE' if same else 'IDENTITY_CHANGED',actual=actual)
    except psutil.NoSuchProcess:
        return dict(row, same_identity_exists=False, observed_status='NO_SUCH_PROCESS')
    except (psutil.AccessDenied, RuntimeError) as error:
        return dict(row, same_identity_exists=None, observed_status='UNKNOWN_ACCESS_DENIED', exception=str(error))

def owned_child_action_ready(child, launcher):
    """动作前读回直接子与本包装六字段及出生父关系；任何未知或漂移不动。"""
    parent=read_identity(launcher)
    leaf=read_identity(child)
    return parent['same_identity_exists'] is True and leaf['same_identity_exists'] is True and child['ppid']==launcher['pid'] and child['create_time']>=launcher['create_time']

def validate_capture_executable(command_executable):
    """只允许经固定路径、逐prefix路径与SHA验证的Vitis Python。"""
    runtime_config = compat_pins.runtime_config_binding()
    current = compat_pins.validate_native_python_pin(sys.executable, compat_pins.NATIVE_PYTHON_SHA256)
    command = compat_pins.validate_native_python_pin(command_executable, compat_pins.NATIVE_PYTHON_SHA256)
    if current != command:
        raise ValueError('当前解释器与子进程解释器绑定不同')
    return command, runtime_config

def main(metadata=None):
    if metadata is not None and (type(metadata) is not dict or set(metadata) != {'mode', 'prefix'}):
        raise ValueError('包装metadata只允许mode/prefix')
    label, *command = sys.argv[1:]
    assert label.isidentifier() and command
    if metadata is not None and (metadata['prefix']!=label or metadata['mode'] not in ('prepare','source','collect','seal')):
        raise ValueError('metadata模式或prefix与实际标签不同')
    native_python, runtime_config = validate_capture_executable(command[0])
    outputs = [HERE/(label+suffix) for suffix in ('.stdout.bin', '.stderr.bin', '.native.json')]
    assert not any(path.exists() for path in outputs)
    def tool_bindings():return contract.capture_tools(HERE,ROOT)
    before_tools=tool_bindings()
    def bind(path):
        raw=path.read_bytes()
        return dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
    consumed_gate=None;gate_path=None;summary_path=None;source_path=None
    is_collector=command[:5]==[sys.executable,'-X','utf8','-B',str(HERE/'collector.py')]
    if is_collector:
        parsed=contract.collector_arguments(command[5:])
        if metadata is None:metadata=dict(mode=parsed['mode'],prefix=label)
        if metadata is not None and metadata['mode']!=parsed['mode']:raise ValueError('实际collector模式与metadata不同')
        if parsed['mode']=='collect':
            import compat_pins
            gate_path=compat_pins.exact(parsed['options']['--gate']);consumed_gate=bind(gate_path)
            summary_path=compat_pins.SYNTH_REPORT/'s15_collection_summary.json'
        elif parsed['mode']=='source':
            import compat_pins
            source_path=compat_pins.SOURCE_PRE/('source_'+parsed['options']['--phase']+'.json')
    launcher = psutil.Process()
    launcher_identity = identity(launcher)
    known = {}
    unknown = []
    confirmed_exits=[]
    peak = 0
    started = time.monotonic()
    failure = None
    child_identity = None
    code = None
    with outputs[0].open('xb') as stdout, outputs[1].open('xb') as stderr:
        child = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr, creationflags=subprocess.DETACHED_PROCESS)
        try:
            child_identity = identity(psutil.Process(child.pid))
            known[(child_identity['pid'], child_identity['create_time'])] = child_identity
        except (psutil.NoSuchProcess, psutil.AccessDenied, RuntimeError) as error:
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
                    if any(item['pid']==row['pid'] and item['create_time']!=row['create_time'] for item in known.values()):
                        raise RuntimeError('采样PID复用，禁止采纳新对象身份')
                    previous=known.get((row['pid'],row['create_time']))
                    if previous is not None and any(previous[key]!=row[key] for key in contract.IDENTITY_KEYS):
                        raise RuntimeError('已知身份六字段漂移，不能改写原身份')
                    rss += process.memory_info().rss
                    if process.pid != launcher.pid:
                        known[(row['pid'], row['create_time'])] = row
                except (psutil.NoSuchProcess, psutil.AccessDenied, RuntimeError) as error:
                    expected=next((row for row in known.values() if row['pid']==process.pid),None)
                    confirmation=read_identity(expected) if expected is not None and isinstance(error,psutil.NoSuchProcess) else None
                    if confirmation is not None and confirmation['same_identity_exists'] is False:
                        confirmed_exits.append(confirmation)
                    else:
                        unknown.append({'phase': 'identity_or_rss_sample', 'pid': process.pid, 'create_time': None if expected is None else expected['create_time'], 'exception_type': type(error).__name__, 'exception': str(error),'fresh_readback':confirmation})
            peak = max(peak, rss)
            if rss > 268435456 or time.monotonic()-started > 120:
                failure = 'TREE_RSS_GT_256MiB' if rss > 268435456 else 'ELAPSED_GT_120_SECONDS'
                # 只终止本包装直接创建且出生身份已确认的子进程；不碰未知身份或外部进程。
                if child_identity is not None and owned_child_action_ready(child_identity,launcher_identity):
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
    after_tools=tool_bindings()
    consumed_gate_after=bind(gate_path) if gate_path is not None else None
    summary_binding=bind(summary_path) if summary_path is not None and summary_path.is_file() else None
    source_binding=bind(source_path) if source_path is not None and source_path.is_file() else None
    if before_tools!=after_tools:failure=(failure or '')+';TOOLS_CHANGED'
    if consumed_gate!=consumed_gate_after:failure=(failure or '')+';CONSUMED_GATE_CHANGED'
    unresolved=not bool(terminal) or any(row['same_identity_exists'] is not False for row in terminal)
    wrapper_code=1 if failure is not None or code is None else 2 if unknown or unresolved else code
    status='BLOCKED_BUDGET_OR_BINDING' if failure is not None or code is None else 'BLOCKED_UNKNOWN_IDENTITY' if unknown or unresolved else 'CLOSED_NATIVE_SUCCESS' if code==0 else 'CLOSED_NATIVE_CHILD_FAILURE'
    result = {'command': command, 'wrapper_command': sys.orig_argv, 'cwd': str(ROOT), 'launcher_identity': launcher_identity,
        'direct_child_identity': child_identity, 'native_exit_code': code, 'direct_child_wait_returned': code is not None,
        'wrapper_exit_code':wrapper_code,'capture_status':status,'capture_target_kind':'COLLECTOR' if is_collector else 'GENERIC_CANARY',
        'consumed_gate':consumed_gate,'consumed_gate_after':consumed_gate_after,'collection_summary':summary_binding,'source_output':source_binding,
        'elapsed_seconds': time.monotonic()-started, 'sampled_owned_tree_peak_bytes': peak, 'sample_interval_seconds': 0.05,
        'unknown_samples': unknown, 'unknown_count': len(unknown), 'absolute_tree_peak_bytes': None,
        'confirmed_capture_exits':confirmed_exits,
        'known_descendant_identity_terminal_observations': terminal, 'known_descendants_same_identity_absent_at_observation': bool(terminal) and all(row['same_identity_exists'] is False for row in terminal),
        'launcher_terminal': 'RUNNING_WHEN_RECORD_WRITTEN', 'entire_os_tree_terminal': 'NOT_PROVEN_BY_DISCRETE_ENUMERATION', 'budget_stop': failure,
        'native_python': native_python, 'runtime_config': runtime_config,
        'python': sys.version, 'psutil': psutil.__version__,
        'tool_bindings_before': before_tools, 'tool_bindings_after': after_tools,
        'stdout': {'path': outputs[0].relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(outputs[0].read_bytes()).hexdigest(), 'bytes': outputs[0].stat().st_size},
        'stderr': {'path': outputs[1].relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(outputs[1].read_bytes()).hexdigest(), 'bytes': outputs[1].stat().st_size}}
    if metadata is not None:
        # 仅附加模式标识与已闭合原流，禁止覆盖实际命令、身份或原生退出码。
        result.update(metadata)
        result['closed_logs'] = [result['stdout'], result['stderr']]
    with outputs[2].open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps(result, ensure_ascii=False))
    return wrapper_code

if __name__=='__main__': sys.exit(main())
