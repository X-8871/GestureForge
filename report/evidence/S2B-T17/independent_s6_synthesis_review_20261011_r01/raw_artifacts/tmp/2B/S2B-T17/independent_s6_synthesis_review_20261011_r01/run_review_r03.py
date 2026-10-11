"""记录增量关闭的真实原生码和stdout/stderr。"""
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

parent = Path(__file__).resolve().parent
out = parent / 'r03'
root = parent.parents[3]
command = [sys.executable, '-B', '-X', 'utf8', str(parent / 'review_r03.py')]
started = time.monotonic()
proc = subprocess.run(command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                      env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}, timeout=60)
logs = []
for suffix, raw in [('stdout.log', proc.stdout), ('stderr.log', proc.stderr)]:
    target = out / ('review.' + suffix)
    assert not target.exists()
    target.write_bytes(raw)
    logs.append({'path': target.relative_to(root).as_posix(), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
record = {'command': command, 'native_exit_code': proc.returncode, 'elapsed_seconds': time.monotonic() - started,
          'closed_logs': logs, 'process_tree_peak_memory_bytes': None}
target = out / 'review.native.json'
assert not target.exists()
target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(proc.stdout.decode('utf-8', errors='replace'))
print(json.dumps(record, ensure_ascii=False))
raise SystemExit(proc.returncode)
