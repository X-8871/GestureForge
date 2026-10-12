import hashlib
import json
import stat
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

root = Path.cwd().resolve(strict=True)
out = root / 'tmp/2B/S2B-T17/s15_cache_cleanup_20261012_r02'
formal = root / 'report/evidence/S2B-T17/s15_arithmetic_fix_20261012_r01'
cache_base = root / 'tmp/2B/S2B-T17/s15_arithmetic_fix_20261012_r01'
started = time.monotonic()
hashes = {}

def sha(path):
    key = str(path)
    if key not in hashes:
        digest = hashlib.sha256()
        with Path(path).open('rb') as stream:
            for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
                digest.update(block)
        hashes[key] = digest.hexdigest()
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

manifest_path = formal / 'delivery_manifest_r02.json'
assert sha(manifest_path) == 'd6f678d5d95869228fbc75348f4b56942ba15efaa3785b25511257bc5a4b5cc9'
manifest = load(manifest_path)
bound = {f['path']: f['sha256'] for f in manifest['files']}
assert not any(p.endswith('.gch') or p.startswith('tmp/') for p in bound)
audit = []
for entry in manifest['files']:
    target = root / entry['path']
    actual = sha(target)
    audit.append({'path': entry['path'], 'expected_sha256': entry['sha256'], 'actual_sha256': actual, 'bytes': target.stat().st_size, 'state': 'MATCH' if actual == entry['sha256'] else 'HASH_MISMATCH'})
assert all(r['state'] == 'MATCH' for r in audit)
proofs = []
items = []
preserved = []
for mode in ['boundary', 'frozen', 'output', 'feature', 'layer0']:
    group = mode + '_r01'
    valpath = formal / group / 'validation.json'
    nativepath = formal / ('native_' + group) / 'native.json'
    native = load(nativepath)
    validation = load(valpath)
    assert validation['status'].startswith('PASS_S15_')
    assert native['native_exit_code'] == native['direct_wait_exit_code'] == 0
    assert validation['source_sha256_pre'] == validation['source_sha256_post']
    assert sha(valpath) == bound[rel(valpath)] and sha(nativepath) == bound[rel(nativepath)]
    for test in validation['tests']:
        cr = next(r for r in test['runs'] if r['name'] == 'compile')
        sr = next(r for r in test['runs'] if r['name'] == 'simulation')
        for run in [cr, sr]:
            assert run['native_exit_code'] == run['direct_wait_exit_code'] == 0
            assert run['terminal_state'] == 'EXITED_DIRECT_CHILD_WAIT' and run['failure'] is None
            for channel in ['stdout', 'stderr']:
                log = root / run[channel]['path']
                assert sha(log) == run[channel]['sha256'] == bound[rel(log)]
        cwd = Path(cr['cwd'])
        assert cache_base in cwd.parents and cwd.resolve(strict=True) == cwd
        obj = cwd / 'obj_dir'
        exe = Path(sr['command'][0])
        assert exe.parent == obj and exe.is_file()
        ancestors = [obj, *obj.parents]
        assert all(not p.is_symlink() and not p.is_junction() for p in ancestors if p == root or root in p.parents)
        report_cwd = formal / cwd.relative_to(cache_base)
        sources = []
        for arg in cr['command']:
            if arg.endswith('.sv'):
                temporary = cwd / arg
                expected = sha(temporary)
                candidates = [root / p for p, value in bound.items() if value == expected and p.startswith(rel(formal / group) + '/')]
                assert candidates, (str(temporary), expected)
                same_name = [p for p in candidates if p.name == temporary.name]
                archival = (same_name or candidates)[0]
                assert expected == sha(archival) == bound[rel(archival)]
                sources.append({'original': str(temporary), 'archive': rel(archival), 'sha256': sha(archival)})
        retained = []
        for p in obj.iterdir():
            if p.is_file() and p.suffix != '.gch':
                retained.append({'path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p)})
        assert any(p['path'].endswith('.exe') for p in retained)
        assert any(p['path'].endswith('.o') for p in retained)
        assert any(p['path'].endswith('.cpp') for p in retained)
        preserved.extend(retained)
        proof = {'mode': mode, 'validation_path': rel(valpath), 'validation_sha256': sha(valpath), 'outer_native_path': rel(nativepath), 'outer_native_sha256': sha(nativepath), 'outer_native': native, 'compile': cr, 'simulation': sr, 'original_archive_sources': sources, 'formal_manifest': {'path': rel(manifest_path), 'sha256': sha(manifest_path)}}
        proofs.append(proof)
        stem = exe.stem
        for suffix in ['fast', 'slow']:
            p = obj / (stem + '__pch.h.' + suffix + '.gch')
            st = p.lstat()
            assert stat.S_ISREG(st.st_mode) and st.st_nlink == 1
            assert not p.is_symlink() and not p.is_junction() and not (getattr(st, 'st_file_attributes', 0) & 0x400)
            assert p.resolve(strict=True) == p
            header = obj / (stem + '__pch.h')
            assert header.is_file()
            items.append({'exact_windows_path': str(p), 'relative_path': rel(p), 'target_type': 'regular_file', 'bytes': st.st_size, 'sha256': sha(p), 'mtime_ns': st.st_mtime_ns, 'link_count': st.st_nlink, 'symlink': False, 'junction': False, 'reparse_point': False, 'completion_proof_index': len(proofs) - 1, 'retained_header': {'path': str(header), 'sha256': sha(header)}, 'formal_manifest': rel(manifest_path), 'eligible_after_root_rechecks': True})

references = []
exact_hits = []
for entry in manifest['files']:
    p = root / entry['path']
    if p.suffix not in ['.json', '.py', '.md']:
        continue
    content = p.read_text(encoding='utf-8')
    if '.gch' in content:
        references.append({'path': rel(p), 'sha256': sha(p), 'occurrences': [{'line': i, 'text': line[:700]} for i, line in enumerate(content.splitlines(), 1) if '.gch' in line]})
    for item in items:
        if item['exact_windows_path'] in content or item['relative_path'] in content:
            exact_hits.append({'path': rel(p), 'candidate': item['exact_windows_path']})
assert not exact_hits
checker = root / 'verification/check_stage_delivery.py'
assert 'CACHE_SUFFIXES = {".gch", ".o", ".obj"}' in checker.read_text(encoding='utf-8')
refs = []
refs.append(write('manifest_file_hash_audit_g1.json', {'manifest': rel(manifest_path), 'sha256': sha(manifest_path), 'total': len(audit), 'matching': len(audit), 'rows': audit}))
refs.append(write('completion_proofs_g1.json', proofs))
refs.append(write('preserved_artifact_inventory_g1.json', preserved))
refs.append(write('dependency_reference_audit_g1.json', {'manifest_required_gch': [], 'exact_candidate_reference_hits': exact_hits, 'gch_literal_occurrences': references, 'checker_path': rel(checker), 'checker_sha256': sha(checker), 'scope': '只读检查当前S15 G1明确manifest文件；不扫描独立Reviewer活动目录。'}))
plan = {'schema_version': 1, 'status': 'G1_ONLY_DRAFT_WAITING_REVIEWER_STOP', 'created_at_utc8': datetime.now(timezone(timedelta(hours=8))).isoformat(), 'workspace': str(root), 'items': items, 'item_count': len(items), 'total_bytes': sum(i['bytes'] for i in items), 'total_gib': sum(i['bytes'] for i in items) / 2**30, 'read_only_evidence': refs, 'excluded_active_reviewer': 'tmp/2B/S2B-T17/independent_s15_functional_review_20261012_r01', 'elapsed_seconds': round(time.monotonic() - started, 3), 'limitations': ['无删除、测试、Vivado、ROSS、串口/JTAG、Git或生产编辑。', '未采全OS真实进程及实时disk/RAM，总控删除前必须另核，并再核每项path/type/hash/size。', '所有exe/o/a/生成source/header/黄金/日志/失败原件保留。', '本草案不声明独立Reviewer已结束，收到ROOT STOP后另作补充并冻结。', '峰值内存和全部工具调用量未测。']}
refs.append(write('g1_cleanup_plan_draft.json', plan))
write('original_index_g1.json', refs)
print(json.dumps({'files': refs, 'count': len(items), 'bytes': plan['total_bytes'], 'elapsed_seconds': plan['elapsed_seconds'], 'gch_literals': len(references)}, ensure_ascii=False))
