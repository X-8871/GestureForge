"""只枚举本次本地硬件服务的目标；不停止、复位、下载或运行CPU。"""

from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import subprocess
import traceback


def main():
    """保存真实连接、目标与清理结果，绝不调用目标写入或执行命令。"""
    run = Path(__file__).resolve().parent
    identity_path = run / 'hw_server_identity.json'
    result_path = run / 'jtag_targets_result.json'
    assert identity_path.is_file()
    assert not result_path.exists()
    identity = json.loads(identity_path.read_text(encoding='utf-8-sig'))
    expected_pid = int(identity['native']['ProcessId'])
    expected_created = identity['native']['CreationTimeFileTimeUtc']
    native_path = r'D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\hw_server.exe'
    record = {
        'started_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
        'scope': '只连接本次本地hw_server并枚举目标，不读写目标寄存器或内存，不停止/复位/下载/运行目标。',
        'hardware_program_execution': 'NOT_RUN',
        'status': 'IN_PROGRESS',
        'expected_hw_server_pid': expected_pid,
        'calls': [],
        'cleanup_errors': [],
    }
    session = None
    channel = None
    sdk = None

    def check_server():
        """核对实际监听PID、全部hw_server及创建时间，禁止连到其他会话。"""
        command = (
            "$ErrorActionPreference='Stop'; "
            "$servers=@(Get-CimInstance Win32_Process -Filter \"Name='hw_server.exe'\" | "
            "Select-Object ProcessId,ParentProcessId,ExecutablePath,@{Name='CreationTimeFileTimeUtc';Expression={[string]$_.CreationDate.ToFileTimeUtc()}}); "
            "$listeners=@(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction SilentlyContinue | "
            "Select-Object LocalAddress,LocalPort,OwningProcess); "
            "[pscustomobject]@{servers=$servers;listeners=$listeners}|ConvertTo-Json -Depth 5"
        )
        probe = subprocess.run(['powershell.exe', '-NoProfile', '-Command', command], capture_output=True)
        assert probe.returncode == 0, probe.stderr.decode('utf-8', errors='replace')
        data = json.loads(probe.stdout.decode('utf-8-sig'))
        assert len(data['servers']) == 1, data
        server = data['servers'][0]
        assert int(server['ProcessId']) == expected_pid, data
        assert server['ExecutablePath'] == native_path, data
        assert server['CreationTimeFileTimeUtc'] == expected_created, data
        assert data['listeners'] and all(int(item['OwningProcess']) == expected_pid for item in data['listeners']), data
        record['calls'].append({'command': command, 'exit_code': probe.returncode, 'server_snapshot': data})

    try:
        check_server()
        import xsdb
        sdk = xsdb
        record['calls'].append({'api': 'xsdb.start_debug_session', 'state': 'CALLING'})
        session = xsdb.start_debug_session()
        record['calls'].append({'api': "session.connect(host='127.0.0.1', port=3121, server='hw_server')", 'state': 'CALLING'})
        channel = session.connect(host='127.0.0.1', port=3121, server='hw_server')
        record['channel'] = str(channel)
        check_server()
        record['calls'].append({'api': "session.targets('--target_properties')", 'state': 'CALLING'})
        targets = session.targets('--target_properties')
        record['targets'] = targets
        print('TARGET_PROPERTIES', json.dumps(targets, ensure_ascii=False, default=str), flush=True)
        record['status'] = 'TARGETS_ENUMERATED' if targets else 'NO_JTAG_TARGETS'
    except BaseException as error:
        record['status'] = 'PROBE_FAILED'
        record['error'] = repr(error)
        record['traceback'] = traceback.format_exc()
        print(record['traceback'], flush=True)
    finally:
        if session is not None and channel is not None:
            try:
                session.disconnect(chan=channel)
                record['calls'].append({'api': 'session.disconnect(chan=channel)', 'state': 'DONE'})
            except BaseException as error:
                record['cleanup_errors'].append(repr(error))
        if sdk is not None:
            try:
                sdk.dispose()
                record['calls'].append({'api': 'xsdb.dispose()', 'state': 'DONE'})
            except BaseException as error:
                record['cleanup_errors'].append(repr(error))
        if record['cleanup_errors']:
            record['status'] = 'PROBE_FAILED'
        record['finished_at'] = datetime.now(timezone(timedelta(hours=8))).isoformat()
        with result_path.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2, default=str)
            stream.write('\n')
        print('JTAG_PROBE_RESULT', json.dumps(record, ensure_ascii=False, default=str), flush=True)
    return 0 if record['status'] in {'TARGETS_ENUMERATED', 'NO_JTAG_TARGETS'} else 1


if __name__ == '__main__':
    raise SystemExit(main())
