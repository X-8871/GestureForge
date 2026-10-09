"""仅停止本次已核实的两核并读取状态、PC和三个寄存器；不初始化或运行程序。"""

from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import io
import json
import subprocess
import sys
import traceback


def main():
    """保存真实API输出，清理连接时保持已停止的CPU状态。"""
    run = Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T06\ps_jtag_retry_20261009_120653_r01')
    if str(Path(__file__)) != str(run / 'ps_state_probe.py') or not run.is_dir():
        raise RuntimeError('脚本或运行目录与已核实的精确路径不同。')
    result_path = run / 'ps_state_result.json'
    if any(item.name.casefold() == result_path.name.casefold() for item in run.iterdir()):
        raise RuntimeError('结果名称已存在或有大小写冲突，拒绝覆盖。')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    now = lambda: datetime.now(timezone(timedelta(hours=8))).isoformat()
    record = {
        'started_at': now(), 'status': 'IN_PROGRESS',
        'scope': '仅对本次唯一APU的两核按Running状态停止，读取两核PC及CPU0三个寄存器。',
        'hardware_program_execution': 'NOT_RUN', 'cold_jtag_proven': False,
        'ps_initialization_execution': 'NOT_RUN', 'cpu_resume_execution': 'NOT_RUN',
        'calls': [], 'stop_requested': [], 'halted_confirmed': [], 'cleanup_errors': [],
    }
    session = channel = sdk = None

    def emit(event):
        print(json.dumps(event, ensure_ascii=False, default=str), flush=True)

    def call(api, function, *args, **kwargs):
        """同时保留实际打印文本和返回值表示，不猜测PC文本格式。"""
        item = {'time': now(), 'api': api, 'args': list(args), 'kwargs': kwargs, 'state': 'CALLING'}
        record['calls'].append(item)
        emit(item)
        output, errors = io.StringIO(), io.StringIO()
        try:
            with redirect_stdout(output), redirect_stderr(errors):
                value = function(*args, **kwargs)
            item.update(state='DONE', return_repr=repr(value), return_type=type(value).__name__)
            return value
        except BaseException as error:
            item.update(state='FAILED', error=repr(error), traceback=traceback.format_exc())
            raise
        finally:
            item.update(finished_at=now(), stdout=output.getvalue(), stderr=errors.getvalue())
            emit(item)

    def check_server():
        """复用本次服务门禁，显式核对归属；不依赖可被优化删除的assert。"""
        command = (
            "$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false); "
            "$servers=@(Get-CimInstance Win32_Process -Filter \"Name='hw_server.exe'\" | "
            "Select-Object ProcessId,ParentProcessId,ExecutablePath,@{Name='CreationTimeFileTimeUtc';Expression={[string]$_.CreationDate.ToFileTimeUtc()}}); "
            "$listeners=@(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction SilentlyContinue | "
            "Select-Object LocalAddress,LocalPort,OwningProcess); "
            "[pscustomobject]@{servers=$servers;listeners=$listeners}|ConvertTo-Json -Depth 5"
        )
        probe = subprocess.run(['powershell.exe', '-NoProfile', '-Command', command], capture_output=True, timeout=15)
        item = {'time': now(), 'command': command, 'exit_code': probe.returncode,
                'stdout': probe.stdout.decode('utf-8-sig', errors='replace'),
                'stderr': probe.stderr.decode('utf-8-sig', errors='replace')}
        record['calls'].append(item)
        emit(item)
        if probe.returncode != 0:
            raise RuntimeError('服务归属查询失败。')
        data = json.loads(item['stdout'])
        if len(data['servers']) != 1 or data['servers'][0] != expected_native:
            raise RuntimeError('唯一服务的PID、父PID、路径或创建时间与本次授权记录不同。')
        if not data['listeners'] or any(int(row['OwningProcess']) != 39576 or int(row['LocalPort']) != 3121 for row in data['listeners']):
            raise RuntimeError('3121监听归属与本次服务不同。')

    def validate_targets(targets):
        """拒绝多板或未知目标，按实际上下文选择两核，不固定目标ID。"""
        names = ('APU', 'ARM Cortex-A9 MPCore #0', 'ARM Cortex-A9 MPCore #1', 'xc7z020')
        if not isinstance(targets, dict) or len(targets) != len(names):
            raise RuntimeError('目标数量或返回结构改变。')
        selected = {}
        for ctx, target in targets.items():
            name = target['name']
            if name not in names or name in selected or target['target_ctx'] != ctx:
                raise RuntimeError('目标名称重复、未知或上下文不一致。')
            if (target['jtag_cable_manufacturer'], target['jtag_cable_product'], target['jtag_cable_serial']) != ('Digilent', 'JTAG-HS1', '210512180081'):
                raise RuntimeError('目标线缆与本次授权线缆不同。')
            if type(target['target_id']) is not int or target['target_id'] <= 0:
                raise RuntimeError('目标ID无效。')
            selected[name] = target
        apu = selected['APU']
        if len({target['target_id'] for target in selected.values()}) != 4:
            raise RuntimeError('目标ID不唯一。')
        for name in names[1:3]:
            cpu = selected[name]
            if cpu['parent_ctx'] != apu['target_ctx'] or cpu['parent'] != 'APU' or cpu['jtag_device_ctx'] != apu['jtag_device_ctx']:
                raise RuntimeError('两核不属于同一唯一APU。')
        if len({target['jtag_cable_ctx'] for target in selected.values()}) != 1:
            raise RuntimeError('目标不在同一线缆上下文。')
        return selected

    # 先以CreateNew预留结果文件，避免停止CPU之后才发现结果无法创建。
    with result_path.open('x', encoding='utf-8', newline='\n') as stream:
        try:
            if sys.flags.optimize != 0:
                raise RuntimeError('只接受未优化的Python执行。')
            identity = json.loads((run / 'hw_server_identity.json').read_text(encoding='utf-8-sig'))
            expected_native = {'ProcessId': 39576, 'ParentProcessId': 37840,
                               'ExecutablePath': r'D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\hw_server.exe',
                               'CreationTimeFileTimeUtc': '134359925214792270'}
            if identity['status'] != 'OWNED_SERVER_READY' or identity['native'] != expected_native or identity['launcher_pid'] != 37840:
                raise RuntimeError('已保存服务身份与本次固定服务不同。')
            # 旧成功枚举仅校验同一线缆与板卡目标身份，不证明本次冷JTAG或profile。
            baseline_path = Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T06\ps_connection_debug_20261009_113002_r01\jtag_targets_result.json')
            baseline_bytes = baseline_path.read_bytes()
            baseline_sha = '49d579836ecd1287f7de7422fb2e2be1b2af7fb186c0a38542858475c825ae45'
            if hashlib.sha256(baseline_bytes).hexdigest() != baseline_sha:
                raise RuntimeError('旧成功枚举基线SHA与已核实版本不同。')
            baseline = json.loads(baseline_bytes.decode('utf-8'))
            record['target_identity_baseline'] = {'path': str(baseline_path), 'sha256': baseline_sha,
                                                 'purpose': '旧成功枚举仅核对身份，不证明本次冷JTAG或profile。'}
            if baseline['status'] != 'TARGETS_ENUMERATED' or baseline['cleanup_errors']:
                raise RuntimeError('前置枚举记录未成功或未清理完成。')
            expected_targets = validate_targets(baseline['targets'])
            check_server()
            import xsdb
            sdk = xsdb
            session = call('xsdb.start_debug_session', xsdb.start_debug_session)
            channel = call('session.connect', session.connect, host='127.0.0.1', port=3121, server='hw_server')
            check_server()
            properties = call('session.targets', session.targets, '--target_properties')
            record['target_properties'] = properties
            current_targets = validate_targets(properties)
            binding_keys = ('target_ctx', 'name', 'parent_ctx', 'jtag_device_ctx', 'jtag_device_name', 'jtag_device_index', 'jtag_cable_ctx')
            for name, target in current_targets.items():
                if any(target[key] != expected_targets[name][key] for key in binding_keys):
                    raise RuntimeError('本次重新枚举的目标链与前置记录不同。')
            cores = {}
            for label, name in (('cpu0', 'ARM Cortex-A9 MPCore #0'), ('cpu1', 'ARM Cortex-A9 MPCore #1')):
                target = current_targets[name]
                core = call('session.targets', session.targets, id=target['target_id'])
                if vars(core).get('_ctx') != target['target_ctx'] or vars(core).get('_id') != target['target_id'] or vars(core).get('_name') != name:
                    raise RuntimeError('选择的目标对象与实际枚举的上下文不一致。')
                cores[label] = core
            before = {label: call(label + '.state', core.state) for label, core in cores.items()}
            record['states_before'] = before
            if any(not isinstance(state, str) or not (state == 'Running' or state.startswith('Stopped')) for state in before.values()):
                raise RuntimeError('CPU状态未知，停止后续操作。')
            for label, core in cores.items():
                state = call(label + '.state', core.state)
                if state == 'Running':
                    record['stop_requested'].append(label)
                    call(label + '.stop', core.stop)
                elif not isinstance(state, str) or not state.startswith('Stopped'):
                    raise RuntimeError('停止前CPU状态变为未知。')
                state = call(label + '.state', core.state)
                record.setdefault('states_after', {})[label] = state
                if not isinstance(state, str) or not state.startswith('Stopped'):
                    raise RuntimeError('CPU停止状态未确认。')
                record['halted_confirmed'].append(label)
            for label, core in cores.items():
                call(label + '.rrd', core.rrd, reg='pc')
            for name, address in (('BOOT_MODE', 0xF800025C), ('MCTRL', 0xF8007080), ('OCM_CFG', 0xF8000910)):
                call('cpu0.mrd.' + name, cores['cpu0'].mrd, '--value', address=address, size=1, word_size=4)
            record['status'] = 'PS_STATE_READBACK_SAVED'
        except BaseException as error:
            record.update(status='PROBE_FAILED', error=repr(error), traceback=traceback.format_exc())
            emit({'time': now(), 'event': 'PROBE_FAILED', 'traceback': record['traceback']})
        finally:
            # 只关闭本次连接；绝不恢复CPU、复位或停止外部服务。
            if session is not None and channel is not None:
                try:
                    call('session.disconnect', session.disconnect, chan=channel)
                except BaseException as error:
                    record['cleanup_errors'].append(repr(error))
            if sdk is not None:
                try:
                    call('xsdb.dispose', sdk.dispose)
                except BaseException as error:
                    record['cleanup_errors'].append(repr(error))
            if record['cleanup_errors']:
                record['status'] = 'PROBE_FAILED'
            record['finished_at'] = now()
            json.dump(record, stream, ensure_ascii=False, indent=2, default=str)
            stream.write('\n')
            stream.flush()
            emit({'time': now(), 'event': 'PS_STATE_RESULT', 'record': record})
    return 0 if record['status'] == 'PS_STATE_READBACK_SAVED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
