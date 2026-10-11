"""封存独审脚本真实原生码和原始输出。"""
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
    target = out / ('review.' + suffix)
    if target.exists():
        raise RuntimeError('禁止覆盖独审日志')
    target.write_bytes(raw)
    logs.append({'path': target.relative_to(root).as_posix(), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
record = {'command': command, 'native_exit_code': result.returncode, 'elapsed_seconds': time.monotonic() - started,
          'closed_logs': logs, 'process_tree_peak_memory_bytes': None}
target = out / 'review.native.json'
if target.exists():
    raise RuntimeError('禁止覆盖独审原生记录')
target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(result.stdout.decode('utf-8', errors='replace'))
print(json.dumps(record, ensure_ascii=False))
raise SystemExit(result.returncode)
