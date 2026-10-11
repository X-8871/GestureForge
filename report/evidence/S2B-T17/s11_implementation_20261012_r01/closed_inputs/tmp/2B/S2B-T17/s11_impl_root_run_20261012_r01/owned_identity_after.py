"""只读复核已授权S11运行的已知身份退出，不枚举或停止其它窗口。"""
import hashlib
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import psutil


CACHE = Path(__file__).parent
GUARD = CACHE.parent / 's11_impl_guard_actual_20261012_r01'
receipt = json.loads((GUARD / 'guard' / 'guard_receipt.json').read_text(encoding='utf-8'))
supervisor = json.loads((GUARD / 'supervisor_receipt.json').read_text(encoding='utf-8'))
expected = [receipt['binding'], supervisor['guard_identity']]
expected.extend(row['expected'] for row in receipt['confirmed_sample_exits'])
for row in receipt.get('final_known_member_readback', []):
    expected.append(row['expected'])
rows = []
seen = set()
for item in expected:
    key = (item['pid'], item['create_time'])
    if key in seen:
        continue
    seen.add(key)
    try:
        process = psutil.Process(item['pid'])
        actual = {'pid': process.pid, 'create_time': process.create_time()}
        if actual['create_time'] != item['create_time']:
            status = 'PID_REUSED_OLD_IDENTITY_EXITED'
        else:
            actual.update(exe=process.exe(), cwd=process.cwd(), cmdline=process.cmdline(), ppid=process.ppid())
            status = 'STILL_PRESENT'
    except psutil.NoSuchProcess as error:
        actual = {'native_error': repr(error)}
        status = 'ABSENT'
    except psutil.Error as error:
        actual = {'native_error': repr(error)}
        status = 'UNKNOWN'
    rows.append({'expected': item, 'actual_readback': actual, 'status': status})
success = all(row['status'] in ('ABSENT', 'PID_REUSED_OLD_IDENTITY_EXITED') for row in rows)
output = CACHE / 'owned_identity_after.json'
result = {'status': 'KNOWN_IDENTITIES_EXITED' if success else 'BLOCKED',
          'at_utc8': datetime.now(timezone(timedelta(hours=8))).isoformat(),
          'source_commit': receipt['source_commit'], 'run_id': receipt['run_id'],
          'readback': rows, 'native_exit_code': 0 if success else 3,
          'process_scan_or_stop_performed': False,
          'limitations': ['仅复核本次已知身份，不宣称采样间未知短命进程的连续闭合。']}
with output.open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(result, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'status': result['status'], 'identities': len(rows), 'native_exit_code': result['native_exit_code'],
                  'path': str(output), 'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}, ensure_ascii=False))
raise SystemExit(result['native_exit_code'])
