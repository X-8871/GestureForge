"""闭合独审原件；files仅path/sha256/role，字节数另表。"""
import hashlib
import json
from pathlib import Path

out = Path(__file__).resolve().parent
root = out.parents[3]
final_receipt = out / 'r02/receipt.json'
receipt = json.loads(final_receipt.read_text(encoding='utf-8'))
assert receipt['status'] == 'PASS_EVIDENCE_INTEGRITY_ONLY'
assert json.loads((out / 'review.native.json').read_text(encoding='utf-8'))['native_exit_code'] == 2
assert json.loads((out / 'r02/review.native.json').read_text(encoding='utf-8'))['native_exit_code'] == 0
files, sizes = [], {}
for path in sorted(out.rglob('*')):
    if not path.is_file():
        continue
    raw = path.read_bytes()
    name = path.relative_to(root).as_posix()
    role = 'source' if path.suffix == '.py' else 'log' if path.suffix == '.log' else 'result'
    files.append({'path': name, 'sha256': hashlib.sha256(raw).hexdigest(), 'role': role})
    sizes[name] = len(raw)
stats_path = out / 'raw_bytes.json'
manifest_path = out / 'raw_delivery_manifest.json'
assert not stats_path.exists() and not manifest_path.exists()
stats = {'status': 'SEALED_RAW_BYTES', 'file_count_excluding_seal_indexes': len(files),
         'total_bytes_excluding_seal_indexes': sum(sizes.values()), 'file_bytes': sizes,
         'files': [{'path': p, 'bytes': n} for p, n in sizes.items()],
         'index_self_policy': '字节表和raw_manifest不自绑定；字节表由raw_manifest绑定。',
         'native_review_exit_codes': {'r01': 2, 'r02': 0},
         'audit_native_commands': {'r01': 42, 'r02': 42},
         'reviewer_process_memory': receipt['reviewer_process_memory'],
         'process_tree_peak_memory_bytes': None}
stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
files.append({'path': stats_path.relative_to(root).as_posix(),
              'sha256': hashlib.sha256(stats_path.read_bytes()).hexdigest(), 'role': 'result'})
manifest = {'schema_version': 1, 'status': 'PASS_EVIDENCE_INTEGRITY_ONLY', 'task_id': 'S2B-T17',
            'reviewed_source_commit': receipt['reviewed_source_commit'],
            'reviewed_manifest_sha256': receipt['reviewed_manifest_sha256'],
            'receipt': {'path': final_receipt.relative_to(root).as_posix(),
                        'sha256': hashlib.sha256(final_receipt.read_bytes()).hexdigest()},
            'files': files, 'bytes_table': stats_path.relative_to(root).as_posix(),
            'policy': '保全首轮Reviewer失败和复核成功原件；清单自身由总控归档映射绑定，仅失败证据完整性。'}
assert all(set(row) == {'path', 'sha256', 'role'} for row in files)
assert any(row['path'] == manifest['receipt']['path'] and row['sha256'] == manifest['receipt']['sha256'] for row in files)
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': 'STOP_PASS_EVIDENCE_INTEGRITY_ONLY', 'receipt': manifest['receipt'],
                  'raw_manifest_path': manifest_path.relative_to(root).as_posix(),
                  'raw_manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                  'raw_listed_files': len(files), 'raw_listed_bytes': sum(sizes.values()) + stats_path.stat().st_size,
                  'total_files_including_manifest': len(files) + 1,
                  'total_bytes_including_manifest': sum(sizes.values()) + stats_path.stat().st_size + manifest_path.stat().st_size}, ensure_ascii=False))
