"""保存轻量复制补核的真实原生退出码和关闭日志。"""
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

out = Path(__file__).resolve().parent
root = out.parents[3]
command = [sys.executable, '-B', '-X', 'utf8', str(out / 'copy_review.py')]
start = time.perf_counter()
result = subprocess.run(command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}, timeout=60)
logs = []
for suffix, raw in [('stdout.log', result.stdout), ('stderr.log', result.stderr)]:
    p = out / ('copy_review.' + suffix)
    assert not p.exists()
    p.write_bytes(raw)
    logs.append({'path': p.relative_to(root).as_posix(), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
native = {'command': command, 'native_exit_code': result.returncode,
          'elapsed_seconds': time.perf_counter() - start, 'closed_logs': logs, 'peak_memory_bytes': None}
target = out / 'copy_review.native.json'
assert not target.exists()
target.write_text(json.dumps(native, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(result.stdout.decode('utf-8', errors='replace'))
print(result.stderr.decode('utf-8', errors='replace'), file=sys.stderr)
print(json.dumps(native, ensure_ascii=False))
raise SystemExit(result.returncode)
