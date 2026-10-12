"""顺序复用原guard/monitor/collector轻量回归及自有canary，保存实际码不启动heavy。"""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import native_capture

W=Path(__file__).parent
rows=[]
for label,name in [('s14_guard_r01','selftest.py'),('s14_monitor_r01','monitor_fixtures.py'),('s14_final_light_r01','final_light_checks.py')]:
    path=W/name;before=hashlib.sha256(path.read_bytes()).hexdigest()
    sys.argv=[str(W/'native_capture.py'),label,sys.executable,'-X','utf8','-B',str(path)]
    with contextlib.redirect_stdout(io.StringIO()):code=native_capture.main()
    record=json.loads((W/(label+'.native.json')).read_text(encoding='utf-8'))
    rows.append(dict(label=label,native_exit_code=code,script_sha_before=before,script_sha_after=hashlib.sha256(path.read_bytes()).hexdigest(),record=record))
    print(json.dumps(dict(label=label,native_exit_code=code,elapsed_seconds=record['elapsed_seconds']),ensure_ascii=False),flush=True)
with (W/'legacy_checks_result.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump(dict(status='PASS_G1_ONLY' if all(r['native_exit_code']==0 for r in rows) else 'FAIL_PRESERVED',records=rows,actual_heavy_vivado_hardware=False),stream,ensure_ascii=False,indent=2);stream.write('\n')
raise SystemExit(0 if all(r['native_exit_code']==0 for r in rows) else 1)
