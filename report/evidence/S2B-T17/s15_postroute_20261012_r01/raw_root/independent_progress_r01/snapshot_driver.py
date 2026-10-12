import hashlib
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition')
RUN = ROOT / 'tmp/2B/S2B-T17/s15_postroute_root_20261012_r01'
OUT = RUN / 'independent_progress_r01'
TZ = timezone(timedelta(hours=8))

def digest(data):
    return hashlib.sha256(data).hexdigest()

assert ROOT.is_dir() and RUN.is_dir() and OUT.is_dir()
paths = [
    RUN / 'supervision_r01/guard/samples.jsonl',
    RUN / 'supervision_r01/guard/events.jsonl',
    RUN / 'supervision_r01/guard/guard_receipt.json',
    RUN / 'supervision_r01/supervision.jsonl',
    RUN / 'supervision_r01/supervisor_receipt.json',
    RUN / 'native_consumer_r01/consumption.jsonl',
    RUN / 'native_consumer_r01/consumer_receipt.json',
    ROOT / 'tmp/2B/S2B-T17/s15_launch_prepare_20261012_r02/project_s15_r01/s2b_inference_candidate.runs/impl_1/runme.log',
]
rows = []
tails = {}
for i, path in enumerate(paths):
    assert path.is_file(), str(path)
    before = path.stat()
    data = path.read_bytes()
    after = path.stat()
    target = OUT / ('snapshot_%02d_%s' % (i, path.name))
    assert not target.exists(), str(target)
    target.write_bytes(data)
    lines = data.decode('utf-8').splitlines()
    tails[str(path.relative_to(ROOT))] = lines[-40:] if path.name == 'runme.log' else lines[-1:]
    rows.append({'source': str(path), 'snapshot': target.name, 'sha256': digest(data), 'bytes': len(data), 'mtime_utc8': datetime.fromtimestamp(after.st_mtime, TZ).isoformat(), 'read_metadata_stable': before.st_size == after.st_size and before.st_mtime_ns == after.st_mtime_ns})
log = paths[-1].read_text(encoding='utf-8') if False else (OUT / 'snapshot_07_runme.log').read_text(encoding='utf-8')
peak = re.findall(r'Memory \(MB\): peak =\s*([0-9.]+)', log)
report = {
    'captured_at_utc8': datetime.now(TZ).isoformat(),
    'session': 'vivado-20261012-144256-cf6822b7',
    'status_call_count': 1,
    'mcp_status': 'SESSION_NOT_FOUND_CALLER_VIEW_ONLY',
    'mcp_failure_is_not_design_failure': True,
    'root_declared_launch_utc8': '2026-10-12T14:49:06+08:00',
    'sources': rows,
    'tails': tails,
    'reported_single_process_peak_memory_mb': max(map(float, peak)) if peak else None,
    'continuous_budget_status': 'NOT_PROVEN',
    'monitor_terminal': 'GUARD_BLOCKED_INCOMPLETE_TREE_IDENTITY_SUP_GUARD_EXITED_CONSUMER_BLOCKED_RUNTIME_MONITOR',
    'scope': '一次只读状态调用及本地日志快照；未执行设计命令、重启、停止或硬件操作。工具内存峰值不代表进程树峰值或连续预算证明。',
}
(OUT / 'snapshot_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'snapshot_count': len(rows), 'reported_peak_memory_mb': report['reported_single_process_peak_memory_mb'], 'continuous_budget_status': report['continuous_budget_status']}, ensure_ascii=False))
