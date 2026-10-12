import hashlib
import json
import stat
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

root = Path.cwd().resolve(strict=True)
out = root / 'tmp/2B/S2B-T17/s15_cache_cleanup_20261012_r02'
review = root / 'tmp/2B/S2B-T17/independent_s15_functional_review_20261012_r01'
started = time.monotonic()
hashes = {}

def sha(path):
    key = str(path)
    if key not in hashes:
        h = hashlib.sha256()
        with Path(path).open('rb') as stream:
            for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
                h.update(block)
        hashes[key] = h.hexdigest()
    return hashes[key]

def rel(path):
    return Path(path).relative_to(root).as_posix()

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def write(name, value):
    target = out / name
    assert not target.exists()
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return {'path': rel(target), 'sha256': sha(target), 'bytes': target.stat().st_size}

draft = load(out / 'g1_cleanup_plan_draft.json')
g1aud = load(out / 'manifest_file_hash_audit_g1.json')
assert sha(root / g1aud['manifest']) == g1aud['sha256']
preserved = load(out / 'preserved_artifact_inventory_g1.json')
proofs = []
for proof in load(out / 'completion_proofs_g1.json'):
    records = {}
    for field, source in [('compile_record', 'compile'), ('simulation_record', 'simulation')]:
        p = (root / proof[source]['stdout']['path']).parent / (source + '.native.json')
        record = load(p)
        assert record == proof[source]
        records[field] = {'path': rel(p), 'sha256': sha(p), 'record': record}
    proofs.append({'object_directory': str(Path(proof['simulation']['command'][0]).parent), **records, 'outer_native': {'path': proof['outer_native_path'], 'sha256': proof['outer_native_sha256'], 'record': proof['outer_native']}, 'formal_manifest': proof['formal_manifest'], 'original_archive_sources': proof['original_archive_sources']})

stop = review / 'final_stop_receipt.json'
indexpath = review / 'artifact_hash_index.json'
assert sha(stop) == 'da99b27ad6c8628afe23f3154f43ca91e04d0bf31d06fafa982932bca7b92a34'
assert sha(indexpath) == 'ce731e3ce2418ba18fcea65a006b8be72de37fc4e06fb5f14327d24784e66cdd'
sv = load(stop)
index = load(indexpath)
assert sv['stop'] and index['stop'] and sv['status'] == index['status'] == 'PASS_G2_FUNCTIONAL_ONLY'
assert not any(row['path'].endswith('.gch') for row in index['files'])
indexrows = []
for entry in index['files']:
    p = root / entry['path']
    actual = sha(p)
    assert actual == entry['sha256'] and p.stat().st_size == entry['size_bytes']
    indexrows.append({'path': entry['path'], 'expected_sha256': entry['sha256'], 'actual_sha256': actual, 'bytes': p.stat().st_size, 'state': 'MATCH'})
preserved.extend([{'path': str(stop), 'sha256': sha(stop), 'bytes': stop.stat().st_size}, {'path': str(indexpath), 'sha256': sha(indexpath), 'bytes': indexpath.stat().st_size}])
driverpath = root / sv['native_driver']['path']
assert sha(driverpath) == sv['native_driver']['sha256']
driver = load(driverpath)
assert driver['native_exit_code'] == 0
compile_candidates = [root / row['path'] for row in index['files'] if row['path'].endswith('/boundary/compile.native.json')]
assert len(compile_candidates) == 1
cp = compile_candidates[0]
sp = cp.with_name('simulation.native.json')
cr, sr = load(cp), load(sp)
for record in [cr, sr]:
    assert record['native_exit_code'] == record['direct_wait_exit_code'] == 0
    assert record['terminal_state'] == 'EXITED_DIRECT_CHILD_WAIT' and record['failure'] is None
    for channel in ['stdout', 'stderr']:
        p = Path(record[channel]['path'])
        p = p if p.is_absolute() else root / p
        assert sha(p) == record[channel]['sha256']
cwd = Path(cr['cwd'])
assert review in cwd.parents and cwd == Path(sr['cwd'])
obj = Path(sr['command'][0]).parent
assert obj == cwd / 'obj_dir'
assert all(not p.is_symlink() and not p.is_junction() for p in [obj, *obj.parents] if p == root or root in p.parents)
indexbound = {r['path']: r['sha256'] for r in index['files']}
sources = []
for arg in cr['command']:
    if arg.endswith('.sv'):
        p = cwd / arg
        assert sha(p) == indexbound[rel(p)]
        sources.append({'original_indexed_source': str(p), 'sha256': sha(p)})
for p in obj.iterdir():
    if p.is_file() and p.suffix != '.gch':
        preserved.append({'path': str(p), 'sha256': sha(p), 'bytes': p.stat().st_size})
proofs.append({'object_directory': str(obj), 'compile_record': {'path': rel(cp), 'sha256': sha(cp), 'record': cr}, 'simulation_record': {'path': rel(sp), 'sha256': sha(sp), 'record': sr}, 'outer_native': {'path': rel(driverpath), 'sha256': sha(driverpath), 'record': driver}, 'original_indexed_sources': sources, 'reviewer_stop': {'path': rel(stop), 'sha256': sha(stop)}, 'reviewer_index': {'path': rel(indexpath), 'sha256': sha(indexpath)}, 'formal_archive_status': 'ROOT将随后精确复制162原件及index；当前绑定真实STOP原件，缓存从index明确排除。'})
items = draft['items']
exe = Path(sr['command'][0])
for suffix in ['fast', 'slow']:
    p = obj / (exe.stem + '__pch.h.' + suffix + '.gch')
    st = p.lstat()
    assert stat.S_ISREG(st.st_mode) and st.st_nlink == 1
    assert not p.is_symlink() and not p.is_junction() and not (getattr(st, 'st_file_attributes', 0) & 0x400)
    assert p.resolve(strict=True) == p
    header = obj / (exe.stem + '__pch.h')
    assert header.is_file()
    items.append({'exact_windows_path': str(p), 'relative_path': rel(p), 'target_type': 'regular_file', 'bytes': st.st_size, 'sha256': sha(p), 'mtime_ns': st.st_mtime_ns, 'link_count': st.st_nlink, 'symlink': False, 'junction': False, 'reparse_point': False, 'completion_proof_index': len(proofs) - 1, 'retained_header': {'path': str(header), 'sha256': sha(header)}, 'original_reviewer_index': rel(indexpath), 'eligible_after_root_rechecks': True})
for item in items:
    p = Path(item['exact_windows_path'])
    st = p.lstat()
    assert st.st_size == item['bytes'] and st.st_mtime_ns == item['mtime_ns'] and st.st_nlink == 1
    assert not p.is_symlink() and not p.is_junction() and not (getattr(st, 'st_file_attributes', 0) & 0x400)

dep = load(out / 'dependency_reference_audit_g1.json')
dep['formal_manifest_required_gch_files'] = []
dep['reviewer_index_required_gch_files'] = []
dep['reviewer_index'] = {'path': rel(indexpath), 'sha256': sha(indexpath), 'stop_receipt_sha256': sha(stop)}
occurrences = []
for row in index['files']:
    p = root / row['path']
    if p.suffix not in ['.json', '.py', '.md']:
        continue
    text = p.read_text(encoding='utf-8')
    if '.gch' in text:
        occurrences.append({'path': rel(p), 'sha256': sha(p), 'lines': [{'line': i, 'text': line[:700]} for i, line in enumerate(text.splitlines(), 1) if '.gch' in line]})
    for item in items:
        assert item['relative_path'] not in text and item['exact_windows_path'] not in text
dep['reviewer_gch_literal_occurrences'] = occurrences
dep['interpretation'] = '只读index及归属原件核验；编译日志创建GCH不属于输入依赖；实际恢复原件不声明GCH。'
audit = {'summaries': [{'path': g1aud['manifest'], 'sha256': g1aud['sha256'], 'total_files': g1aud['total'], 'matching': g1aud['matching'], 'gch_declared_paths': []}, {'path': rel(indexpath), 'sha256': sha(indexpath), 'total_files': len(indexrows), 'matching': len(indexrows), 'gch_declared_paths': [], 'kind': 'reviewer_original_hash_index_not_formal_manifest'}], 'audits': [{'manifest': g1aud['manifest'], 'rows': g1aud['rows']}, {'manifest': rel(indexpath), 'rows': indexrows}]}
proofref = write('completion_proofs.json', proofs)
auditref = write('manifest_file_hash_audit.json', audit)
preservedref = write('preserved_artifact_inventory.json', preserved)
depref = write('dependency_reference_audit.json', dep)
plan = {'schema_version': 1, 'status': 'READ_ONLY_PLAN_ROOT_PROCESS_AND_PATH_RECHECK_REQUIRED', 'created_at_utc8': datetime.now(timezone(timedelta(hours=8))).isoformat(), 'workspace': str(root), 'items': items, 'item_count': len(items), 'total_bytes': sum(i['bytes'] for i in items), 'total_gib': sum(i['bytes'] for i in items) / 2**30, 'completion_proofs': proofref, 'formal_manifest_audit': auditref, 'preserved_artifact_inventory': preservedref, 'dependency_reference_audit': depref, 'elapsed_seconds': round(time.monotonic() - started, 3), 'limitations': ['未删除、未测试、未运行Vivado/ROSS/硬件/Git，未改生产或工具。', '未核全OS进程、实时disk/RAM；总控删除前重查实际活动进程与每项精确路径、类型、hash/size/mtime/链接。', '独立Reviewer已真实STOP；当前绑定tmp真实原件及162项index，ROOT随后正式归档后操作。', 'exe/o/a/source/header/黄金/日志/所有失败原件保留。', '本轮仅处理12项新GCH，不访问已r01删除18项。', '最初G1只读脚本因误设归档布局exit1，修正为按清单实际source_snapshot哈希匹配；未运行测试或改证据。', '峰内存与全部工具调用量未测；批量G1审计成功一次，最终补充成功一次。']}
planref = write('cleanup_plan.json', plan)
newrefs = [proofref, auditref, preservedref, depref, planref]
for p in out.iterdir():
    if p.is_file() and p.name not in {r['path'].split('/')[-1] for r in newrefs}:
        newrefs.append({'path': rel(p), 'sha256': sha(p), 'bytes': p.stat().st_size})
indexref = write('original_index.json', newrefs)
print(json.dumps({'plan': planref, 'index': indexref, 'count': len(items), 'bytes': plan['total_bytes'], 'reviewer_indexed_files': len(indexrows), 'gch_literals': occurrences, 'elapsed_seconds': plan['elapsed_seconds']}, ensure_ascii=False))
