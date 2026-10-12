"""只复制S13固定助手源码到新S14目录，保留来源映射，不复制运行配置或旧结果。"""
import hashlib
import json
from pathlib import Path

W=Path(__file__).parent;ROOT=W.parents[3]
OLD=ROOT/'tmp/2B/S2B-T17/s13_launch_prepare_20261012_r01'
D=ROOT/'report/evidence/S2B-T17/s14_launch_tools_20261012_r01'
assert OLD.is_dir() and D.parent.is_dir() and not D.exists();D.mkdir()
names=['guard.py','supervisor.py','runtime_consumer.py','launch_monitor.py','collector.py','impl_collector.py','source_after_check.py','native_source_after.py','native.py','native_capture.py','materialize_runtime_config.py','compat_pins.py','selftest.py','monitor_fixtures.py','fixture_supervision.py','collector_fixtures.py','final_light_checks.py','prepare_tool_mapping.py']
rows=[]
for name in names:
    source=OLD/name;target=W/name
    assert source.is_file() and not source.is_symlink() and not source.is_junction() and not target.exists()
    raw=source.read_bytes()
    with target.open('xb') as stream:stream.write(raw)
    rows.append(dict(source=str(source),source_sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),target=str(target)))
with (W/'baseline_mapping.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump(dict(source_commit='701dc55af0c53a959e84dc0c470f136918f5bd50',files=rows),stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps(dict(status='COPIED_BASELINE_ONLY',files=len(rows),runtime_config_copied=False,source_freeze_created=False),ensure_ascii=False))
