"""闭合三轮Reviewer必要原件，字节数另表，不复制业务报告或缓存。"""
import hashlib
import json
from pathlib import Path

out = Path(__file__).resolve().parent
root = out.parents[3]
receipt_path = out / 'r03/receipt.json'
receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
assert receipt['status'] == 'PASS_EVIDENCE_INTEGRITY_ONLY'
manifest_path, stats_path = out / 'raw_delivery_manifest.json', out / 'raw_bytes.json'
assert not manifest_path.exists() and not stats_path.exists()
records, sizes = [], {}
for path in sorted(out.rglob('*')):
    if not path.is_file():
        continue
    assert not path.is_symlink() and path.suffix.lower() in {'.py', '.json', '.log'}
    assert not any(p in {'obj_dir', 'SDK', 'sdk', '__pycache__'} for p in path.parts)
    raw = path.read_bytes()
    name = path.relative_to(root).as_posix()
    role = 'source' if path.suffix == '.py' else 'log' if path.suffix == '.log' else 'result'
    records.append({'path': name, 'sha256': hashlib.sha256(raw).hexdigest(), 'role': role})
    sizes[name] = len(raw)
native_codes, elapsed = {}, {}
for name, relative in [('r01', 'review.native.json'), ('r02', 'r02/review.native.json'), ('r03', 'r03/review.native.json')]:
    native = json.loads((out / relative).read_text(encoding='utf-8'))
    assert isinstance(native['command'], list) and isinstance(native['native_exit_code'], int)
    native_codes[name] = native['native_exit_code']
    elapsed[name] = native['elapsed_seconds']
assert native_codes == {'r01': 1, 'r02': 2, 'r03': 0}
stats = {'status': 'SEALED_RAW_BYTES', 'file_count_excluding_seal_indexes': len(records),
    'total_bytes_excluding_seal_indexes': sum(sizes.values()), 'file_bytes': sizes,
    'files': [{'path': p, 'bytes': n} for p, n in sizes.items()],
    'native_review_exit_codes': native_codes, 'review_process_elapsed_seconds': elapsed,
    'audit_native_commands': {'r01': 0, 'r02': 42, 'r03': 0},
    'r03_incremental_scope': '复核315文件及2接口绑定、r02真实命令/输出哈希和四FAIL分类；复用八组及七反例，无重跑。',
    'observed_reviewer_process_memory': {'r02': receipt['reviewer_process_memory'], 'r03': receipt['reviewer_closure_process_memory']},
    'process_tree_peak_memory_bytes': None,
    'index_self_policy': '字节表与raw_manifest不自引用；字节表由raw_manifest绑定。'}
stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
records.append({'path': stats_path.relative_to(root).as_posix(),
                'sha256': hashlib.sha256(stats_path.read_bytes()).hexdigest(), 'role': 'result'})
manifest = {'schema_version': 1, 'status': 'PASS_EVIDENCE_INTEGRITY_ONLY', 'task_id': 'S2B-T17',
    'reviewed_source_commit': receipt['reviewed_source_commit'],
    'reviewed_manifest_sha256': receipt['reviewed_manifest_sha256'],
    'receipt': {'path': receipt_path.relative_to(root).as_posix(), 'sha256': hashlib.sha256(receipt_path.read_bytes()).hexdigest()},
    'files': records, 'bytes_table': stats_path.relative_to(root).as_posix(),
    'policy': '仅绑定必要Reviewer脚本、native元数据/日志、receipt及反例；首两轮脚本问题真实失败保持，最终r03仅证据完整性通过。'}
assert all(set(row) == {'path', 'sha256', 'role'} for row in records)
assert manifest['receipt']['path'] in {row['path'] for row in records}
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': 'STOP_PASS_EVIDENCE_INTEGRITY_ONLY', 'receipt': manifest['receipt'],
    'raw_manifest_path': manifest_path.relative_to(root).as_posix(),
    'raw_manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
    'raw_listed_files': len(records), 'raw_listed_bytes': sum(sizes.values()) + stats_path.stat().st_size,
    'total_files_including_manifest': len(records) + 1,
    'total_bytes_including_manifest': sum(sizes.values()) + stats_path.stat().st_size + manifest_path.stat().st_size,
    'native_review_exit_codes': native_codes, 'review_process_elapsed_seconds': elapsed,
    'observed_process_memory': stats['observed_reviewer_process_memory']}, ensure_ascii=False))
