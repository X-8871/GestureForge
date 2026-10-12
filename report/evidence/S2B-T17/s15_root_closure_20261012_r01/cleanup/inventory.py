import hashlib
import json
import os
import stat
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

root = Path.cwd().resolve(strict=True)
out = root / 'tmp/2B/S2B-T17/s15_cache_cleanup_20261012_r01'
assert out.is_dir() and not out.is_symlink()
started = time.monotonic()
hash_cache = {}

def sha(path):
    path = Path(path)
    key = str(path)
    if key not in hash_cache:
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
                digest.update(block)
        hash_cache[key] = digest.hexdigest()
    return hash_cache[key]

def rel(path):
    return Path(path).relative_to(root).as_posix()

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def write(name, value):
    target = out / name
    assert not target.exists()
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return {'path': rel(target), 'sha256': sha(target), 'bytes': target.stat().st_size}

base = root / 'report/evidence/S2B-T17'
s12 = base / 's12_timing_cones_20261012_r01'
s13 = base / 's13_root_review_20261012_r01'
s14 = base / 's14_independent_functional_review_20261012_r01'
manifest_paths = [s12 / 'delivery_manifest_r02.json', s13 / 'delivery_manifest.json', s14 / 'delivery_manifest.json', base / 'independent_s12_functional_review_20261012_r01/delivery_manifest.json']
manifests = {rel(p): load(p) for p in manifest_paths}
bound = {f['path']: f['sha256'] for m in manifests.values() for f in m['files']}
audit_rows = []
manifest_summaries = []
for manifest_path in manifest_paths:
    manifest_name = rel(manifest_path)
    rows = []
    for index, entry in enumerate(manifests[manifest_name]['files']):
        path = root / entry['path']
        try:
            actual = sha(path)
            state = 'MATCH' if actual == entry['sha256'] else 'HASH_MISMATCH'
            row = {'index': index, 'path': entry['path'], 'expected_sha256': entry['sha256'], 'actual_sha256': actual, 'bytes': path.stat().st_size, 'state': state}
        except OSError as exc:
            row = {'index': index, 'path': entry['path'], 'expected_sha256': entry['sha256'], 'state': 'READ_ERROR', 'error': str(exc)}
        rows.append(row)
    summary = {'path': manifest_name, 'sha256': sha(manifest_path), 'total_files': len(rows), 'matching': sum(r['state'] == 'MATCH' for r in rows), 'mismatches': [r for r in rows if r['state'] != 'MATCH'], 'gch_declared_paths': [f['path'] for f in manifests[manifest_name]['files'] if f['path'].endswith('.gch')]}
    assert not summary['gch_declared_paths']
    manifest_summaries.append(summary)
    audit_rows.append({'manifest': manifest_name, 'rows': rows})

groups = [
    ('independent_s14_functional_review_20261012_r01', 'boundary/obj_dir', 'Vtb_s2b_conv_validation', s14 / 'boundary/compile.native.json', s14 / 'boundary/simulation.native.json', None, s14 / 'delivery_manifest.json'),
    ('independent_s14_functional_review_20261012_r01', 'route_frozen/obj_dir', 'Vtb_s2b_route_specialization', s14 / 'route_frozen/compile.native.json', s14 / 'route_frozen/simulation.native.json', None, s14 / 'delivery_manifest.json'),
    ('independent_s13_functional_review_20261012_r01', 'rtl/obj_dir', 'Vtb_s2b_conv_validation', s13 / 'functional/independent_compile.native.json', s13 / 'functional/independent_simulation.native.json', None, s13 / 'delivery_manifest.json'),
]
for run, prefix, stem, native_group in [
    ('s12_conv_layer0_20261012_r01', 'obj_dir', 'Vtb_s2b_conv_layer0', 'layer0'),
    ('s12_conv_boundary_20261012_r01', 'obj_dir', 'Vtb_s2b_conv_validation', 'boundary'),
    ('s12_backend_timing_20261012_r01', 'obj_dir', 'Vtb_s2b_backend_coordinates', 'backend'),
    ('s12_pool_timing_20261012_r01', 'rtl_run/obj_engine', 'Vtb_s2b_geometry_specialization', 'pool'),
    ('s12_pool_timing_20261012_r01', 'rtl_run/obj_geometry', 'Vtb_s8_geometry', 'pool'),
    ('s12_route_generic_20261012_r01', 'obj_dir', 'Vtb_s2b_route_specialization', 'generic_route'),
]:
    validation = base / run / 'validation.json'
    groups.append((run, prefix, stem, validation, validation, s12 / ('execution_raw/' + native_group + '/native_receipt.json'), s12 / 'delivery_manifest_r02.json'))

items = []
completion_audit = []
preserved_inventory = []
for run, prefix, stem, cp, sp, outer, mp in groups:
    run_dir = root / 'tmp/2B/S2B-T17' / run
    obj = run_dir / prefix
    assert obj.is_dir() and obj.resolve(strict=True) == obj
    assert all(not p.is_symlink() and not p.is_junction() for p in [run_dir, *obj.parents] if p == root or root in p.parents)
    cv, sv = load(cp), load(sp)
    if cp == sp:
        cr = next(r for r in cv['runs'] if r['name'] == ('engine_compile' if prefix.endswith('obj_engine') else 'geometry_compile' if prefix.endswith('obj_geometry') else 'compile'))
        sr = next(r for r in sv['runs'] if r['name'] == cr['name'].replace('compile', 'simulation'))
    else:
        cr, sr = cv, sv
    assert cr.get('native_exit_code', cr.get('exit_code')) == 0
    assert sr.get('native_exit_code', sr.get('exit_code')) == 0
    assert not cr.get('failure') and not sr.get('failure')
    assert Path(sr['command'][0]) == obj / (stem + '.exe')
    for p in [cp, sp]:
        assert rel(p) in bound and sha(p) == bound[rel(p)]
    if outer:
        ov = load(outer)
        assert ov['native_returncode'] == 0 and not ov.get('supervisor_stop')
        assert run in ov['command'] and sha(outer) == bound[rel(outer)]
    logs = []
    for record in [cr, sr]:
        if 'log' in record:
            p = root / record['log']
            assert sha(p) == record['log_sha256']
            logs.append({'path': rel(p), 'sha256': sha(p)})
        else:
            for field in ['stdout', 'stderr']:
                expected = record[field]['sha256']
                matches = [r for m in manifests.values() for r in m['files'] if r['sha256'] == expected and field in r['path']]
                assert matches
                p = root / matches[0]['path']
                assert sha(p) == expected
                logs.append({'path': rel(p), 'sha256': expected})
    retained = []
    for p in obj.iterdir():
        if p.is_file() and not p.name.endswith('.gch'):
            retained.append({'path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p)})
    assert any(p['path'].endswith(stem + '.exe') for p in retained)
    assert any(p['path'].endswith('.o') for p in retained)
    assert any(p['path'].endswith('.cpp') for p in retained)
    preserved_inventory.extend(retained)
    proof = {'run_id': run, 'object_directory': str(obj), 'compile_record': {'path': rel(cp), 'sha256': sha(cp), 'record': cr}, 'simulation_record': {'path': rel(sp), 'sha256': sha(sp), 'record': sr}, 'outer_native': {'path': rel(outer), 'sha256': sha(outer), 'command': load(outer)['command'], 'native_returncode': 0} if outer else None, 'logs': logs, 'formal_manifest': {'path': rel(mp), 'sha256': sha(mp)}, 'preserved_non_gch_files': len(retained)}
    completion_audit.append(proof)
    for suffix in ['fast', 'slow']:
        p = obj / (stem + '__pch.h.' + suffix + '.gch')
        st = p.lstat()
        assert stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and not p.is_symlink() and not p.is_junction()
        assert p.resolve(strict=True) == p
        header = obj / (stem + '__pch.h')
        assert header.is_file()
        items.append({'exact_windows_path': str(p), 'relative_path': rel(p), 'target_type': 'regular_file', 'bytes': st.st_size, 'sha256': sha(p), 'mtime_ns': st.st_mtime_ns, 'link_count': st.st_nlink, 'symlink': False, 'junction': False, 'reparse_point': bool(getattr(st, 'st_file_attributes', 0) & 0x400), 'completion_proof_index': len(completion_audit) - 1, 'formal_manifest': rel(mp), 'retained_header': {'path': str(header), 'sha256': sha(header)}, 'eligible_after_root_rechecks': True})
        assert not items[-1]['reparse_point']

dependency_scope = [base / 'independent_s12_functional_review_20261012_r01', s13 / 'functional', s14, s12]
reference_rows = []
exact_hits = []
for directory in dependency_scope:
    for p in directory.rglob('*'):
        if not p.is_file() or p.suffix not in ['.json', '.py']:
            continue
        content = p.read_text(encoding='utf-8', errors='strict')
        # 日志中的编译输出不作为恢复输入；依赖、脚本和清单另行检查。
        if '.gch' in content:
            occurrences = [{'line': i, 'text': line[:700]} for i, line in enumerate(content.splitlines(), 1) if '.gch' in line]
            reference_rows.append({'path': rel(p), 'sha256': sha(p), 'occurrences': occurrences})
        for item in items:
            if item['exact_windows_path'] in content or item['relative_path'] in content:
                exact_hits.append({'path': rel(p), 'target': item['exact_windows_path']})
assert not exact_hits
checker = root / 'verification/check_stage_delivery.py'
checker_text = checker.read_text(encoding='utf-8')
assert 'CACHE_SUFFIXES = {".gch", ".o", ".obj"}' in checker_text
dependency_audit = {'scoped_directories': [rel(p) for p in dependency_scope], 'exact_candidate_reference_hits': exact_hits, 'gch_literal_occurrences': reference_rows, 'formal_manifest_required_gch_files': [], 'checker': {'path': rel(checker), 'sha256': sha(checker), 'meaning': '只枚举正式evidence_dir及清单files；.gch属于禁止混入正式证据的编译缓存，指定候选全部在tmp。'}, 'interpretation': '仅限关联运行。脚本显式排除编译缓存或说明缓存可重建不表示依赖；请总控核对literal occurrence上下文。'}
summary_ref = write('manifest_file_hash_audit.json', {'summaries': manifest_summaries, 'audits': audit_rows})
completion_ref = write('completion_proofs.json', completion_audit)
preserved_ref = write('preserved_artifact_inventory.json', preserved_inventory)
dependency_ref = write('dependency_reference_audit.json', dependency_audit)
plan = {'schema_version': 1, 'status': 'READ_ONLY_PLAN_ROOT_PROCESS_AND_PATH_RECHECK_REQUIRED', 'created_at_utc8': datetime.now(timezone(timedelta(hours=8))).isoformat(), 'workspace': str(root), 'items': items, 'item_count': len(items), 'total_bytes': sum(i['bytes'] for i in items), 'total_gib': sum(i['bytes'] for i in items) / 2**30, 'completion_proofs': completion_ref, 'formal_manifest_audit': summary_ref, 'preserved_artifact_inventory': preserved_ref, 'dependency_reference_audit': dependency_ref, 'elapsed_seconds': round(time.monotonic() - started, 3), 'limitations': ['未删除任何文件；未运行测试、综合、Vivado、串口或JTAG。', '本脚本只读文件和元数据，没有采集全OS进程；总控删除前须重查实际活动进程及每项hash/size/精确路径、类型与链接。', '历史清单的活动生产源码可能已变；逐项hash差异原样披露，正式原件、源快照、生成source、exe/o/a、黄金和失败记录均保留。', '2.5GB按十进制满足；总计少于2.5GiB，不能混淆。', '仅生成指定tmp计划与只读证据，不编辑生产、不提交。', '峰值内存、全部工具调用数量未测；运行一次批量审计。']}
result = write('cleanup_plan.json', plan)
print(json.dumps({'cleanup_plan': result, 'count': len(items), 'bytes': plan['total_bytes'], 'gch_literals': len(reference_rows), 'manifest_summaries': [{k:v for k,v in m.items() if k != 'mismatches'} | {'mismatch_count': len(m['mismatches'])} for m in manifest_summaries], 'elapsed_seconds': plan['elapsed_seconds']}, ensure_ascii=False))
