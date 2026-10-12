import hashlib
import json
import pathlib
import subprocess
import sys
import time

# 精确运行只读清单检查，保存真实原生退出码与未测量字段。
root = pathlib.Path.cwd()
out = pathlib.Path(__file__).parent
results = []
for mode in ['evidence', 'inputs']:
    command = [sys.executable, '-X', 'utf8', '-B', str(root / 'verification/check_stage_delivery.py'), '--mode', mode, '--manifest', str(root / 'report/evidence/S2B-T17/s14_root_closure_20261012_r01/delivery_manifest.json'), '--project-root', str(root)]
    started = time.perf_counter()
    result = subprocess.run(command, capture_output=True)
    for channel in ['stdout', 'stderr']:
        (out / ('unsandboxed_' + mode + '.' + channel + '.bin')).write_bytes(getattr(result, channel))
    results.append({'mode': mode, 'command': command, 'native_exit_code': result.returncode, 'elapsed_seconds': time.perf_counter() - started, 'sampled_peak_bytes': None, 'stdout_sha256': hashlib.sha256(result.stdout).hexdigest(), 'stderr_sha256': hashlib.sha256(result.stderr).hexdigest(), 'stdout': result.stdout.decode('utf-8', errors='replace'), 'stderr': result.stderr.decode('utf-8', errors='replace')})
(out / 'checker_unsandboxed_actual.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(results, ensure_ascii=False, indent=2))
