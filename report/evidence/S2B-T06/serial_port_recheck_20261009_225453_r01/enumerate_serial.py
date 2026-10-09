import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def new_json(path, value):
    with path.open('xb') as stream:
        stream.write((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))


root = Path.cwd()
parent = root / 'report/evidence/S2B-T06'
assert parent.is_dir()
shell = Path('C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe')
assert shell.is_file()
now = datetime.now(timezone(timedelta(hours=8)))
run_id = 'serial_port_recheck_' + now.strftime('%Y%m%d_%H%M%S') + '_r01'
folder = parent / run_id
assert not folder.exists()
folder.mkdir()
baseline = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
# 只枚举Windows串口设备，不打开串口，不触发DTR/RTS或板卡复位。
command = "[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false); $ErrorActionPreference='Stop'; $serialDevices=@(Get-CimInstance Win32_SerialPort | Select-Object DeviceID,Name,PNPDeviceID,Status); $usbSerialDevices=@(Get-CimInstance Win32_PnPEntity | Where-Object { $_.Name -match '\\(COM[0-9]+\\)' } | Select-Object Name,PNPDeviceID,Status,ConfigManagerErrorCode); [pscustomobject]@{observed_at=(Get-Date).ToUniversalTime().AddHours(8).ToString('yyyy-MM-ddTHH:mm:ss.fffffff')+'+08:00';serial_devices=$serialDevices;com_devices=$usbSerialDevices}|ConvertTo-Json -Depth 5"
argv = [str(shell.resolve()), '-NoProfile', '-Command', command]
result = subprocess.run(argv, capture_output=True)
for name, data in [('enumeration.stdout.log', result.stdout), ('enumeration.stderr.log', result.stderr), ('enumerate_serial.py', Path(__file__).read_bytes())]:
    with (folder / name).open('xb') as stream:
        stream.write(data)
new_json(folder / 'execution.json', {'source_commit': baseline, 'argv': argv, 'exit_code': result.returncode, 'scope': '只读设备枚举，无串口打开或实物修改'})
assert result.returncode == 0, result.stderr
observed = json.loads(result.stdout.decode('utf-8-sig'))
expected = 'USB\\VID_10C4&PID_EA60\\D02E61162787ED11A536569F9D1CC348'
ports = [p for p in observed['serial_devices'] if p['DeviceID'] == 'COM4' and p['PNPDeviceID'] == expected and p['Status'] == 'OK']
pnp = [p for p in observed['com_devices'] if p['PNPDeviceID'] == expected and p['Status'] == 'OK' and p['ConfigManagerErrorCode'] == 0]
passed = len(ports) == 1 and len(pnp) == 1
old = root / 'report/evidence/S2B-T06/ps_uart_clock_retest_20261009_172557_r01/capture_identity.json'
assert old.is_file()
new_json(folder / 'port_result.json', {'status': 'PASS_DEVICE_ENUMERATION' if passed else 'DEVICE_IDENTITY_MISMATCH', 'observation': observed, 'selected_port': 'COM4' if passed else None, 'expected_pnp': expected, 'prior_identity_sha256': sha(old), 'serial_open_execution': 'NOT_RUN', 'limitation': '设备枚举OK不等于新UART数据/PS初始化/DDR运行通过；前次通过记录按原运行保留。'})
files = [{'path': old.relative_to(root).as_posix(), 'role': 'input', 'sha256': sha(old)}]
for path in sorted(folder.iterdir()):
    files.append({'path': path.relative_to(root).as_posix(), 'role': 'log' if path.suffix == '.log' else 'source' if path.suffix == '.py' else 'result' if path.name == 'port_result.json' else 'diagnostic', 'sha256': sha(path)})
new_json(folder / 'delivery_manifest.json', {
    'schema_version': 1, 'stage': '2B', 'task_id': 'S2B-T06', 'run_id': run_id,
    'source_commit': baseline, 'evidence_dir': folder.relative_to(root).as_posix(),
    'interfaces': [], 'interfaces_not_applicable_reason': '本次仅检查Windows设备枚举及此前同一USB设备身份，不消费模型或PS/PL业务接口。',
    'files': files,
    'checks': [{'name': 'COM4及既有CP210x身份枚举', 'status': 'PASS' if passed else 'FAIL', 'command': json.dumps(argv, ensure_ascii=False), 'exit_code': result.returncode, 'reason': '实际串口/PNP双重枚举核对固定设备标识；不打开串口。'}],
    'tool_versions': {'Windows_PowerShell': '系统内置Windows PowerShell，精确执行文件路径见execution.json', 'Python': platform.python_version()},
    'limitations': ['只读快照，不持续监控；未打开或抢占COM4，不改变DTR/RTS、复位、核状态或旧日志。', '设备枚举和前次功能通过分开判定，后续实物操作仍需重新核对当前独占条件。'],
})
print(json.dumps({'path': folder.relative_to(root).as_posix(), 'status': 'PASS_DEVICE_ENUMERATION' if passed else 'DEVICE_IDENTITY_MISMATCH', 'port': 'COM4' if passed else None}, ensure_ascii=True))
raise SystemExit(0 if passed else 1)
