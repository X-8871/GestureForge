import hashlib
import json
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

OUT = Path(__file__).resolve().parent
PYTHON = r'C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe'
TZ = timezone(timedelta(hours=8))
command = [PYTHON, '-X', 'utf8', '-B', str(OUT / 'snapshot_driver.py')]
started = datetime.now(TZ).isoformat()
with (OUT / 'native.stdout.log').open('xb') as stdout, (OUT / 'native.stderr.log').open('xb') as stderr:
    child = subprocess.Popen(command, stdout=stdout, stderr=stderr, cwd=OUT)
    code = child.wait()
execution = {'command': command, 'pid': child.pid, 'native_child_wait': code, 'direct_wait': True, 'started_at_utc8': started, 'ended_at_utc8': datetime.now(TZ).isoformat(), 'host_exit_is_not_native_child_exit': True}
(OUT / 'native_execution.json').write_text(json.dumps(execution, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
rows = []
for p in sorted(OUT.iterdir()):
    if p.is_file() and p.name not in ('original_file_index.json', 'final_stop_receipt.json'):
        data = p.read_bytes()
        rows.append({'path': p.name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
index = {'files': rows, 'file_count': len(rows), 'cache_exclusions': [], 'scope': '本次只读观察原件、驱动和真实子进程日志。'}
ip = OUT / 'original_file_index.json'
ip.write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
receipt = {'status': 'OBSERVATION_ONLY_CONTINUOUS_BUDGET_NOT_PROVEN', 'stop': True, 'native_child_wait': code, 'direct_wait': True, 'session_status_call_count': 1, 'index_sha256': hashlib.sha256(ip.read_bytes()).hexdigest(), 'root_alert_sent': True, 'scope': '一次只读观察已停止；不批准PNR、预算或G3/G4/G5。', 'time_utc8': datetime.now(TZ).isoformat()}
rp = OUT / 'final_stop_receipt.json'
rp.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'native_child_wait': code, 'stop': True, 'index_sha256': receipt['index_sha256'], 'receipt_sha256': hashlib.sha256(rp.read_bytes()).hexdigest()}, ensure_ascii=False))
raise SystemExit(code)
