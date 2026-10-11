"""封存两轮轻量独审原件清单；每条仅path/sha256/role，字节数单独记录。"""
import hashlib
import json
from pathlib import Path

out = Path(__file__).resolve().parent
root = out.parents[3]
prior = root / 'tmp/2B/S2B-T17/independent_s4_synthesis_review_20261011_r01'
assert out.is_dir() and prior.is_dir()
manifest_path = out / 'raw_delivery_manifest.json'
stats_path = out / 'raw_bytes.json'
assert not manifest_path.exists() and not stats_path.exists()
receipt = json.loads((out / 'receipt.json').read_text(encoding='utf-8'))
assert receipt['status'] == 'PASS_EVIDENCE_INTEGRITY_ONLY'
assert json.loads((prior / 'review.native.json').read_text(encoding='utf-8'))['native_exit_code'] == 2
assert json.loads((out / 'review.native.json').read_text(encoding='utf-8'))['native_exit_code'] == 0
records = []
bytes_rows = []
for directory in [prior, out]:
    for p in sorted(directory.iterdir()):
        assert p.is_file() and not p.is_symlink()
        raw = p.read_bytes()
        path = p.relative_to(root).as_posix()
        role = 'source' if p.suffix == '.py' else ('log' if p.suffix == '.log' else 'result')
        records.append({'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'role': role})
        bytes_rows.append({'path': path, 'bytes': len(raw)})
stats = {'status': 'SEALED_RAW_BYTES', 'file_count_excluding_seal_indexes': len(records),
         'total_bytes_excluding_seal_indexes': sum(row['bytes'] for row in bytes_rows),
         'files': bytes_rows, 'index_self_policy': '本字节表及raw_manifest自身不自绑定；本表由raw_manifest绑定。',
         'native_review_exit_codes': {'r01': 2, 'r02': 0},
         'audit_native_commands': {'r01': json.loads((prior / 'native_commands.json').read_text(encoding='utf-8'))['count'],
                                   'r02': json.loads((out / 'native_commands.json').read_text(encoding='utf-8'))['count']},
         'review_process_elapsed_seconds': {'r01': json.loads((prior / 'review.native.json').read_text(encoding='utf-8'))['elapsed_seconds'],
                                            'r02': json.loads((out / 'review.native.json').read_text(encoding='utf-8'))['elapsed_seconds']},
         'review_peak_memory_bytes': None, 'review_peak_reason': '未测本轻量独审进程或进程树峰；不使用Vivado峰替代。'}
stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
records.append({'path': stats_path.relative_to(root).as_posix(),
                'sha256': hashlib.sha256(stats_path.read_bytes()).hexdigest(), 'role': 'result'})
manifest = {'schema_version': 1, 'status': 'PASS_EVIDENCE_INTEGRITY_ONLY', 'task_id': 'S2B-T17',
            'reviewed_source_commit': 'f96d3e225fd6d92fd33c0407e20c9585c997c870',
            'reviewed_manifest_sha256': 'cc638501782ed0bf95a63e97cf0128b91fcb629754095201d0feb4e26979a535',
            'receipt': {'path': (out / 'receipt.json').relative_to(root).as_posix(),
                        'sha256': hashlib.sha256((out / 'receipt.json').read_bytes()).hexdigest()},
            'files': records, 'bytes_table': stats_path.relative_to(root).as_posix(),
            'policy': '精确RAW清单含r01脚本问题原件、r02成功原件及Collector最终闭合RAW补充；无缓存或重建副本。清单自身由总控归档映射另绑定。'}
assert all(set(row) == {'path', 'sha256', 'role'} for row in records)
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': 'STOP_PASS_EVIDENCE_INTEGRITY_ONLY',
                  'receipt': manifest['receipt'],
                  'raw_manifest_path': manifest_path.relative_to(root).as_posix(),
                  'raw_manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                  'raw_listed_files': len(records),
                  'raw_listed_bytes': stats['total_bytes_excluding_seal_indexes'] + stats_path.stat().st_size,
                  'total_files_including_manifest': len(records) + 1,
                  'total_bytes_including_manifest': stats['total_bytes_excluding_seal_indexes'] + stats_path.stat().st_size + manifest_path.stat().st_size,
                  'review_native_exit_codes': {'r01': 2, 'r02': 0}}, ensure_ascii=False))
