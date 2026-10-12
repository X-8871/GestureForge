"""只读核对旧真实失败与新工具原生证据；不重分类旧预算。"""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).parent
ROOT = HERE.parents[3]
WORK = ROOT / 'tmp/2B/S2B-T17/s15_launch_prepare_20261012_r01'
PACKAGE = ROOT / 'report/evidence/S2B-T17/s15_launch_tools_20261012_r01'
sys.path.insert(0, str(WORK))
import collector as c

def read(path):
    return json.loads(c.exact(path).read_text(encoding='utf-8'))

def lines(path):
    return [json.loads(line) for line in c.exact(path).read_text(encoding='utf-8').splitlines() if line]

result = {'s14_real_rounds': [], 'g1_true_native': [], 'read_only': True, 'hardware_or_heavy': False}
for number in (1, 2, 3):
    base = PACKAGE / 's14_original_runtime' / ('supervision_r0' + str(number))
    receipt = read(base / 'guard/guard_receipt.json')
    samples = lines(base / 'guard/samples.jsonl')
    supervisor = read(base / 'supervisor_receipt.json')
    consumer = read(PACKAGE / 's14_original_runtime' / ('native_consumer_r0' + str(number)) / 'consumer_receipt.json')
    result['s14_real_rounds'].append(dict(round=number, status=receipt['status'], reason=receipt['reason'], raw_samples=len(samples), valid_samples=sum(not row.get('uncertain') for row in samples), unclosed_samples=sum(any(x.get('reason') == 'TREE_RESCAN_NOT_CLOSED' for x in row.get('uncertain', [])) for row in samples), guard_child_native_exit_code=supervisor['child_native_exit_code'], consumer_code=consumer['native_exit_code'], consumer_samples=consumer['samples']))
result['s14_sta'] = read(ROOT / 'report/evidence/S2B-T17/s14_platform_20261012_r01/s14_sta_result.json')
for relative in ('owned_threshold_canary_r03', 'one_second_cadence_canary_r03', 'native_consumer_canary_r05'):
    base = WORK / relative
    guard_subdir = 'supervision/guard' if relative.startswith('native_consumer') else 'guard'
    receipt = read(base / guard_subdir / 'guard_receipt.json')
    samples = lines(base / guard_subdir / 'samples.jsonl')
    gaps = [row['actual_start_gap_seconds'] for row in samples if row.get('actual_start_gap_seconds') is not None]
    row = dict(path=relative, status=receipt['status'], samples=len(samples), sampled_peak_tree_rss_bytes=receipt['sampled_peak_tree_rss_bytes'], maximum_sample_gap_seconds=max(gaps) if gaps else None, unknown_samples=sum(bool(s.get('uncertain')) for s in samples), collection_scans=[s.get('collection_observation', {}).get('scans') for s in samples])
    if relative.startswith('native_consumer'):
        sup = read(base / 'supervision/supervisor_receipt.json')
        cons = read(base / 'consumer/consumer_receipt.json')
        row.update(supervisor_child_native=sup['child_native_exit_code'], supervisor_code=sup['supervisor_exit_code'], consumer_code=cons['native_exit_code'], consumer_last_reasons=cons['last']['reasons'])
    else:
        native = read(base / 'native.json')
        row['native_fields'] = {k: v for k, v in native.items() if 'exit' in k or 'code' in k}
    result['g1_true_native'].append(row)
receipt = read(PACKAGE / 'g1_receipt.json')
result['final_tools_hash_check'] = [{**row, 'still_matches': hashlib.sha256(c.exact(ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']} for row in receipt['tools']]
with (HERE / 'evidence_audit_result_r02.json').open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(result, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps(dict(s14_rounds=result['s14_real_rounds'], g1=result['g1_true_native'], s14_sta_status=result['s14_sta']['status'], frozen_tools_unchanged=all(row['still_matches'] for row in result['final_tools_hash_check'])), ensure_ascii=False))
