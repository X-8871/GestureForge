import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

OUT = Path(__file__).resolve().parent
cmd = [sys.executable, '-X', 'utf8', '-B', str(OUT / sys.argv[1])]
label = sys.argv[2]
started = datetime.now(timezone(timedelta(hours=8))).isoformat()
with (OUT / (label + '.stdout.log')).open('xb') as stdout, (OUT / (label + '.stderr.log')).open('xb') as stderr:
    p = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, cwd=OUT)
    rc = p.wait()
record = {'command': cmd, 'pid': p.pid, 'native_child_wait': rc, 'direct_wait': True, 'started_at_utc8': started, 'ended_at_utc8': datetime.now(timezone(timedelta(hours=8))).isoformat(), 'host_exit_is_not_child_exit': True}
(OUT / (label + '.native.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record, ensure_ascii=False))
raise SystemExit(rc)
