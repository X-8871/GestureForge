"""运行隔离归档阶段，保存真实原生退出码和已关闭日志。"""
import json
from pathlib import Path
import subprocess
import sys
import time

TMP = Path(__file__).resolve().parent
ROOT = TMP.parents[3]
phase = sys.argv[1]
assert phase in {'collect', 'seal'}
prefix = 'collector' if phase == 'collect' else 'seal'
command = [sys.executable, '-X', 'utf8', '-B', str(TMP / 'archive_s4_review.py'), phase]
started = time.perf_counter()
with (TMP / f'{prefix}.stdout.log').open('xb') as out, (TMP / f'{prefix}.stderr.log').open('xb') as err:
    result = subprocess.run(command, cwd=ROOT, stdout=out, stderr=err)
record = {'command': command, 'cwd': str(ROOT), 'native_exit_code': result.returncode, 'seconds': time.perf_counter() - started}
with (TMP / f'{prefix}.native.json').open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps(record, ensure_ascii=True))
if result.returncode:
    print((TMP / f'{prefix}.stderr.log').read_text(encoding='utf-8'))
raise SystemExit(result.returncode)
