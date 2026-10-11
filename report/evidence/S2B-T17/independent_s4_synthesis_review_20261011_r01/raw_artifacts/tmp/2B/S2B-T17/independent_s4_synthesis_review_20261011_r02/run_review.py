"""执行独立只读检查并保存真实stdout、stderr与原生退出码。"""
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

out = Path(__file__).resolve().parent
root = out.parents[3]
command = [sys.executable, '-B', '-X', 'utf8', str(out / 'review.py')]
started = time.monotonic()
result = subprocess.run(command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}, timeout=60)
logs = []
for suffix, raw in [('stdout.log', result.stdout), ('stderr.log', result.stderr)]:
    p = out / ('review.' + suffix)
    if p.exists():
        raise RuntimeError('独立原件不覆盖')
    p.write_bytes(raw)
    logs.append({'path': p.relative_to(root).as_posix(), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
receipt = {'command': command, 'native_exit_code': result.returncode,
           'elapsed_seconds': time.monotonic() - started, 'closed_logs': logs,
           'peak_memory_bytes': None, 'peak_reason': '未测本轻量独审进程峰。'}
target = out / 'review.native.json'
if target.exists():
    raise RuntimeError('独立native记录不覆盖')
target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(result.stdout.decode('utf-8', errors='replace'))
print(result.stderr.decode('utf-8', errors='replace'), file=sys.stderr)
print(json.dumps(receipt, ensure_ascii=False))
raise SystemExit(result.returncode)
