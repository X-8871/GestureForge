"""只读S14原件并复制明确工具集合到新S15目录；不运行重型工具。"""
from pathlib import Path
import hashlib
import json
import sys
import psutil

W = Path(__file__).parent
ROOT = W.parents[3]
OLD = W.parent / 's14_launch_prepare_20261012_r01'
RUN = W.parent / 's14_physical_launch_root_20261012_r01'
NAMES = ['guard.py', 'supervisor.py', 'runtime_consumer.py', 'launch_monitor.py',
         'collector.py', 'impl_collector.py', 'compat_pins.py', 'native.py',
         'native_capture.py', 'materialize_runtime_config.py', 'source_after_check.py',
         'native_source_after.py', 'selftest.py', 'monitor_fixtures.py', 'collector_fixtures.py',
         's14_regressions.py']

def binding(p):
    return dict(path=p.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size)

def save(p, value):
    with p.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')

assert OLD.is_dir() and RUN.is_dir() and W.is_dir()
rows=[]
for name in NAMES:
    original=OLD/name
    assert original.is_file()
    target=W/('s15_regressions.py' if name=='s14_regressions.py' else name)
    assert not target.exists()
    text=original.read_text(encoding='utf-8').replace('S14', 'S15').replace('s14_', 's15_').replace('0.1.14', '0.1.15')
    with target.open('x', encoding='utf-8', newline='\n') as f:
        f.write(text)
    rows.append(dict(original=binding(original), fork=binding(target)))

rounds=[]
for n in ['01','02','03']:
    directory=RUN/('supervision_r'+n)
    samples_path=directory/'guard'/'samples.jsonl'
    events_path=directory/'guard'/'events.jsonl'
    guard_path=directory/'guard'/'guard_receipt.json'
    sup_path=directory/'supervisor_receipt.json'
    consumer_path=RUN/('native_consumer_r'+n)/'consumer_receipt.json'
    samples=[json.loads(line) for line in samples_path.read_text(encoding='utf-8').splitlines()]
    events=[json.loads(line) for line in events_path.read_text(encoding='utf-8').splitlines()]
    bad=[dict(index=s['index'],uncertain=s['uncertain'],collection=s['collection_observation'],
              exits=s['confirmed_exits'],members=[{k:m[k] for k in ['pid','create_time','exe','cwd','ppid']} for m in s['members']])
         for s in samples if s['tree_rss_bytes'] is None]
    rounds.append(dict(round=n, raw=[binding(p) for p in [samples_path,events_path,guard_path,sup_path,consumer_path]],
                       sample_count=len(samples), valid_samples=sum(s['tree_rss_bytes'] is not None for s in samples),
                       invalid=bad, terminal_events=events[-2:],guard=json.loads(guard_path.read_text(encoding='utf-8')),
                       supervisor=json.loads(sup_path.read_text(encoding='utf-8')), consumer=json.loads(consumer_path.read_text(encoding='utf-8'))))
save(W/'s14_diagnostic.json', dict(status='READ_ONLY_S14_FAILURES_RETAINED',python=sys.version,psutil=psutil.__version__,
     original_tools=rows,rounds=rounds,limitations=['真实S14结果不追认通过；三个窗口只保留原始可验证事实。']))
print(json.dumps(dict(status='FORKED',tools=len(rows),rounds=[dict(round=r['round'],raw=r['sample_count'],valid=r['valid_samples'],invalid=r['invalid']) for r in rounds]),ensure_ascii=False))
