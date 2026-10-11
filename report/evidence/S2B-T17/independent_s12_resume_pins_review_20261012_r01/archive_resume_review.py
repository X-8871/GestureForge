"""新增独审与终态原流正式归档：旧交付不改，真实资源阻断和身份未知分别保留。"""
from datetime import datetime, timezone, timedelta
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import psutil

HERE = Path(__file__).absolute().parent
ROOT = HERE.parents[3]
OUT = ROOT/'report/evidence/S2B-T17/independent_s12_resume_pins_review_20261012_r01'
REVIEW = ROOT/'tmp/2B/S2B-T17/independent_s12_resume_pins_review_20261012_r01'
DEVELOPER = ROOT/'tmp/2B/S2B-T17/s12_physical_resume_prepare_20261012_r01'
MAIN = ROOT/'report/evidence/S2B-T17/s12_resume_source_preflight_20261012_r01'
CONTINUE = ROOT/'tmp/2B/S2B-T17/s12_root_run_20261012_r01/goal_continuation_20261012_r01'
HEAD = '09e0135234ed257d1f878b80bf63eeefcdc6143f'
PINNED = {
 MAIN/'delivery_manifest_r05.json': '5d8e1316caf593f417645fd4f05c7db26784fcadb15b85a5f55e4e74bf9216ff',
 REVIEW/'final_review_receipt_r02.json': '0d20f9d0d44523dd77e531cd1514c659e0e54056082686baecd9930098a1e9be',
 REVIEW/'raw_manifest_r02.jsonl': 'e6ad4f29d3890fcd53e8a72e603ab4f00a8ba701907527ec9a2a00d641754fc9',
 REVIEW/'seal_r03.native.json': '40bcaba8a1a8b868f040aaf8f7d595028d057c36b190ff44364e9c3ef44db2fa'}

def exact(path, directory=False):
    current = Path(path.anchor)
    for name in path.parts[1:]:
        hits = [item for item in current.iterdir() if item.name == name]
        assert len(hits)==1, str(path)
        current = hits[0]
        assert not current.is_symlink() and not current.is_junction(), str(path)
    assert current.is_dir() if directory else current.is_file(), str(path)
    return current

def digest(path):
    value = exact(path).read_bytes()
    return hashlib.sha256(value).hexdigest(), len(value)

def bind(path):
    sha, size = digest(path)
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha, 'bytes': size}

def write(path, value):
    assert path.is_relative_to(HERE) or path.is_relative_to(OUT)
    exact(path.parent, True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write('\n')

def read(path):
    return json.loads(exact(path).read_text(encoding='utf-8'))

def copy(source, target):
    before = digest(source)
    exact(target.parent, True)
    with target.open('xb') as stream: stream.write(exact(source).read_bytes())
    assert digest(source)==digest(target)==before

def identity_read(row):
    try:
        proc = psutil.Process(row['pid'])
        same = proc.create_time()==row['create_time']
        return dict(row, same_identity_exists=same, observed_status=proc.status() if same else 'PID_REUSED')
    except psutil.NoSuchProcess:
        return dict(row, same_identity_exists=False, observed_status='NO_SUCH_PROCESS')
    except psutil.AccessDenied as error:
        return dict(row, same_identity_exists=None, observed_status='UNKNOWN_ACCESS_DENIED', exception=str(error))

def git(label, *arguments):
    command = ['C:\\Program Files\\Git\\bin\\git.exe', '-c', 'core.longpaths=true', '-c', 'maintenance.auto=false', *arguments]
    outputs = [HERE/(label+suffix) for suffix in ('.stdout.bin', '.stderr.bin')]
    identity = None
    unknown = None
    with outputs[0].open('xb') as stdout, outputs[1].open('xb') as stderr:
        child = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr)
        try: identity = {'pid': child.pid, 'create_time': psutil.Process(child.pid).create_time()}
        except (psutil.NoSuchProcess, psutil.AccessDenied) as error:
            unknown = {'pid': child.pid, 'create_time': None, 'exception_type': type(error).__name__, 'exception': str(error)}
        code = child.wait(timeout=30)
    native = {'command': command, 'cwd': str(ROOT), 'direct_child_identity': identity, 'identity_exception': unknown, 'native_exit_code': code,
        'direct_child_wait_returned': True, 'direct_child_identity_after_wait': identity_read(identity) if identity else None,
        'complete_tree_terminal': 'NOT_PROVEN', 'stdout': bind(outputs[0]), 'stderr': bind(outputs[1])}
    write(HERE/(label+'.native.json'), native)
    assert code==0
    return outputs[0].read_bytes()

def loader():
    path = exact(ROOT/'verification/check_stage_delivery.py')
    spec = importlib.util.spec_from_file_location('archive_schema_checker', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

def manifest(name, archive_command, closed_checks=False):
    external = read(OUT/'external_input_bindings.json')['files']
    files = []
    for path in sorted(OUT.rglob('*')):
        if path.is_file():
            sha, _ = digest(path)
            role = 'source' if path.suffix=='.py' else 'result' if path.name.endswith('receipt.json') else 'artifact'
            files.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha, 'role': role,
                'keep_reason': '本轮独审与终态归档原字节；旧索引失效/真实失败/资源阻断/PID和UNKNOWN限制保留，不代替实物或完整树终态'})
    files.extend(external)
    checks = [
        {'name': 'resume_pins_independent_logic_g2', 'status': 'PASS', 'command': ' '.join(read(REVIEW/'review_r03.native.json')['argv']), 'exit_code': 0,
            'reason': '只消费final_review_receipt_r02真实PASS_RESUME_PINS_G2_ONLY；已失效首receipt不得单独消费。'},
        {'name': 'archive_raw_byte_binding', 'status': 'PASS', 'command': archive_command, 'exit_code': 0,
            'reason': '逐项精确路径/SHA/bytes，封存真实Raw，不追认失败或未执行项。'},
        {'name': 'heavy_resource_admission', 'status': 'BLOCKED', 'command': None, 'exit_code': None,
            'reason': 'ROOT两次实际available RAM低于4.5GiB。06:52样本3983073280B/C11501858816B；未来必须重新真实准入。'},
        {'name': 's12_physical_execution', 'status': 'NOT_RUN', 'command': None, 'exit_code': None,
            'reason': 'NOT_STARTED_RESOURCE_BLOCKED：未创建owned Vivado或硬件session，source-after/synth/PNR/STA/bit/fullXSA/Vitis/cache/model/G3-G5未执行。'},
        {'name': 'historical_developer_full_tree_terminal', 'status': 'BLOCKED', 'command': None, 'exit_code': None,
            'reason': '历史Developer没有PID/create_time；UNKNOWN1身份无法恢复，完整树UNKNOWN；直接poll/native返回及tool handle终态不能证明整树闭合。'}]
    if closed_checks:
        for label in ('precheck_evidence', 'precheck_inputs'):
            record = read(HERE/(label+'.native.json'))
            checks.append({'name': label, 'status': 'PASS' if record['native_exit_code']==0 else 'FAIL',
                'command': ' '.join(record['command']), 'exit_code': record['native_exit_code'],
                'reason': 'evidence0仅字节包装；inputs2保留未冻结/NOT_RUN/RESOURCE_BLOCKED/完整历史tree未知。'})
    data = {'schema_version': 1, 'stage': '2B', 'task_id': 'S2B-T17', 'run_id': OUT.name, 'source_commit': HEAD,
        'evidence_dir': OUT.relative_to(ROOT).as_posix(), 'interfaces': [],
        'interfaces_not_applicable_reason': '本轮只归档独立pins审查、实际终态原流和资源阻断，复用已冻结源码及功能G1/G2业务入口；不新增模型或总线接口冻结。',
        'files': files, 'checks': checks, 'tool_versions': {'python': sys.version, 'psutil': psutil.__version__, 'git': '本轮已记录精确命令、原生退出、实际PID/create_time及关闭原流'},
        'limitations': ['G2仅离线逻辑pins，资源准入/物理G0/部署/完整2B/G3-G5未批准',
            '历史Developer完整tree未知、UNKNOWN1身份不可恢复；Reviewer已知身份闭合仅适用于其实际记录范围',
            'ROOT尚未决定本轮实验准备是否关闭，没有新metadata提交；保持CLI==SOURCE_COMMIT==actualHEAD09e',
            '新包装记录launcher/directchild出生身份及已知身份读回；规定节拍离散RSS不是连续绝对峰，整树枚举不是全量完备证明',
            '最后finalseal及最终evidence/inputs验证关闭原流保留新archive scratch；不自指入自身正式清单，ROOT后续封存需保留该循环限制',
            '旧索引/receipt和所有真实失败保留，不改旧交付或原索引，不复跑原功能，不启动Vivado/硬件或修改资源阈值']}
    write(OUT/name, data)

def archive():
    exact(HERE, True); exact(OUT.parent, True); assert not OUT.exists()
    for path, expected in PINNED.items(): assert digest(path)[0]==expected, str(path)
    main = read(MAIN/'delivery_manifest_r05.json')
    assert main['source_commit']==HEAD
    assert git('head_before', 'rev-parse', 'HEAD').decode('ascii').strip()==HEAD
    assert not git('staged_before', 'diff', '--cached', '--name-only').strip()
    frozen = read(MAIN/'source_freeze.json')
    assert len(frozen['source_files'])==43 and frozen['source_commit']==HEAD
    for row in frozen['source_files']: assert digest(ROOT/row['path'])==(row['sha256'], row['bytes'])
    existing = {}
    external = {}
    for row in main['files']:
        path = exact(ROOT/row['path'])
        measured = digest(path); assert measured[0]==row['sha256']
        external[row['path']] = {'path': row['path'], 'sha256': row['sha256'], 'role': 'input', 'keep_reason': '本轮已审r05恢复对象/业务G1G2来源；外部引用，不复制旧历史raw'}
        if path.is_relative_to(MAIN): existing.setdefault(measured, path)
    external[(MAIN/'delivery_manifest_r05.json').relative_to(ROOT).as_posix()] = {'path': (MAIN/'delivery_manifest_r05.json').relative_to(ROOT).as_posix(), 'sha256': PINNED[MAIN/'delivery_manifest_r05.json'], 'role': 'input', 'keep_reason': '本轮Developer G1正式r05清单，原件只读'}
    mapped_main = {}
    for row in [json.loads(line) for line in exact(MAIN/'raw_manifest.jsonl').read_text(encoding='utf-8').splitlines()]:
        source = exact(ROOT/row['original_repo_path']); target = exact(ROOT/row['archived_repo_path'])
        assert digest(source)==digest(target)==(row['sha256'], row['bytes'])
        mapped_main[row['original_repo_path']] = target
    for row in read(MAIN/'closed_native_mapping.json')['rows']:
        source = exact(ROOT/row['original_repo_path']); target = exact(ROOT/row['archived_repo_path'])
        assert digest(source)==digest(target)==(row['sha256'], row['bytes'])
        mapped_main[row['original_repo_path']] = target
    review_rows = [json.loads(line) for line in exact(REVIEW/'raw_manifest_r02.jsonl').read_text(encoding='utf-8').splitlines()]
    assert len(review_rows)==368
    selected = {}
    for row in review_rows:
        source = exact(ROOT/row['path'])
        assert source.is_relative_to(REVIEW) and digest(source)==(row['sha256'], row['bytes'])
        selected[source] = ('review_index_r02', row['sha256'], row['bytes'])
    for name in ('raw_manifest_r02.jsonl', 'final_review_receipt_r02.json'):
        source = exact(REVIEW/name); sha, size = digest(source); selected[source] = ('review_consumption_entry', sha, size)
    for label in ('seal_closed', 'seal_r02', 'seal_r03'):
        for suffix in ('.stdout.bin', '.stderr.bin', '.native.json'):
            source = exact(REVIEW/(label+suffix)); sha, size = digest(source); selected[source] = ('review_closed_supplement', sha, size)
    assert read(REVIEW/'seal_r02.native.json')['native_exit_code']==1
    assert read(REVIEW/'seal_r03.native.json')['native_exit_code']==0
    for source in REVIEW.iterdir():
        if source.is_file() and source.name.endswith(('.stdout.bin', '.stderr.bin', '.native.json')) and source not in selected:
            sha, size = digest(source); selected[source] = ('review_other_closed_supplement', sha, size)
    for source in DEVELOPER.rglob('*'):
        if source.is_file() and source.name.endswith(('.stdout.bin', '.stderr.bin', '.native.json')):
            rel = source.relative_to(ROOT).as_posix()
            if rel not in mapped_main:
                sha, size = digest(source); selected[source] = ('developer_unbound_closed_supplement', sha, size)
    root_names = ['developer_process_identity_clarification.json', 'memory_diag_r01.json', 'memory_diag_r01.tool.json', 'resource_after_resume_g2.json', 'resource_after_resume_g2.tool.json', 'resource_before_resume.json', 'resource_before_resume.tool.json', 'resume_input_root_binding_check.json', 'root_runtime_memory_observation.json']
    for name in root_names:
        source = exact(CONTINUE/name); sha, size = digest(source); selected[source] = ('root_continuation', sha, size)
    assert read(CONTINUE/'resource_before_resume.json')['status']=='BLOCKED'
    after = read(CONTINUE/'resource_after_resume_g2.json')
    assert after['status']=='BLOCKED' and after['available_ram_bytes']==3983073280 and after['c_disk_free_bytes']==11501858816
    assert after['candidate_heavy_processes']==after['unknown_candidates']==[]
    identity = read(CONTINUE/'developer_process_identity_clarification.json')
    assert identity['pid_create_time_recorded'] is False and identity['whole_os_tree_terminal']=='UNKNOWN'
    assert git('head_after', 'rev-parse', 'HEAD').decode('ascii').strip()==HEAD
    assert not git('staged_after', 'diff', '--cached', '--name-only').strip()
    for row in frozen['source_files']: assert digest(ROOT/row['path'])==(row['sha256'], row['bytes'])
    OUT.mkdir(); (OUT/'raw_objects').mkdir(); (OUT/'raw').mkdir()
    mapping = []
    reused = 0
    for source, (role, expected, size) in sorted(selected.items(), key=lambda row: str(row[0])):
        assert digest(source)==(expected, size)
        key = (expected, size)
        if key in existing:
            target = existing[key]
            reused += 1
            reuse_type = 'existing_r05_object' if target.is_relative_to(MAIN) else 'deduplicated_new_object'
        else:
            target = OUT/'raw_objects'/expected
            copy(source, target); existing[key] = target
            reuse_type = 'new_raw_object'
        assert digest(source)==digest(target)==key
        mapping.append({'original_absolute_path': str(source), 'original_repo_path': source.relative_to(ROOT).as_posix(), 'artifact_repo_path': target.relative_to(ROOT).as_posix(), 'sha256': expected, 'bytes': size, 'role': role, 'object_reuse': reuse_type})
    write(OUT/'archive_mapping.json', {'schema_version': 1, 'source_commit': HEAD, 'binding_rows': mapping})
    for source in (REVIEW/'final_review_receipt_r02.json', REVIEW/'raw_manifest_r02.jsonl'):
        copy(source, OUT/'raw'/source.name)
    for source in (HERE/'capture_archive.py', HERE/'archive_resume_review.py'):
        copy(source, OUT/source.name)
    for source in sorted(HERE.glob('*.native.json')):
        if source.name.startswith('archive.'): continue
        label = source.name.removesuffix('.native.json')
        for suffix in ('.stdout.bin', '.stderr.bin', '.native.json'):
            copy(HERE/(label+suffix), OUT/'raw'/(label+suffix))
    write(OUT/'external_input_bindings.json', {'files': sorted(external.values(), key=lambda row: row['path'])})
    review = read(REVIEW/'final_review_receipt_r02.json')
    assert review['status']=='PASS_RESUME_PINS_G2_ONLY' and review['historical_developer_tree_closed']=='UNKNOWN'
    counts = {role: sum(row['role']==role for row in mapping) for role in {row['role'] for row in mapping}}
    receipt = {'status': 'ARCHIVED_PASS_RESUME_PINS_G2_ONLY_PHYSICAL_NOT_STARTED_RESOURCE_BLOCKED', 'source_commit': HEAD,
        'created_at_utc8': datetime.now(timezone(timedelta(hours=8))).isoformat(), 'current_head_before_after_same': True, 'staged_empty_before_after': True, '43_production_raw_unchanged': True,
        'review_receipt_original': bind(REVIEW/'final_review_receipt_r02.json'), 'review_index_original': bind(REVIEW/'raw_manifest_r02.jsonl'),
        'review_primary_index_rows': 368, 'mapping_rows': len(mapping), 'mapping_bytes_including_duplicates': sum(row['bytes'] for row in mapping), 'mapping_counts_by_role': counts,
        'reused_object_rows': reused, 'new_unique_raw_objects': len(list((OUT/'raw_objects').iterdir())), 'new_unique_raw_bytes': sum(path.stat().st_size for path in (OUT/'raw_objects').iterdir()),
        'external_file_bindings': len(external), 'original_main_raw_rows': 371, 'old_history_packages_copied': False,
        'archive_mapping': bind(OUT/'archive_mapping.json'), 'reviewer_known_identity_scope': '仅r02/r03/最终seal实际记录的身份和时点；无出生时间的未知瞬逝对象不追认已知闭合',
        'reviewer_review_metrics': review['review_metrics'], 'reviewer_known_children_closed': review['known_reviewer_children_closed'],
        'historical_developer_pid_create_time': 'NOT_RECORDED', 'historical_developer_unknown_count': 1, 'historical_developer_UNKNOWN_object': 'UNRECOVERABLE_FROM_RECORDED_EVIDENCE', 'historical_developer_complete_tree_terminal': 'UNKNOWN',
        'direct_poll_native_and_tool_handle_scope': '只证明相应直接命令返回、原流关闭或工具handle终态；不能当作完整OS进程树终态。',
        'root_resource_before': read(CONTINUE/'resource_before_resume.json'), 'root_resource_after': after, 'root_resource_native_exit_code': 2,
        'physical_execution': 'NOT_STARTED_RESOURCE_BLOCKED', 'actual_vivado_session_created': False, 'hardware_access': False,
        'source_after_synth_pnr_sta_bit_fullXSA_Vitis_cache_model_g3_g5': 'NOT_RUN', 'g2_scope': 'LOGIC_PINS_ONLY', 'physical_g0': 'BLOCKED',
        'metadata_head_changed': False, 'root_experiment_prepare_closed_decision': 'NOT_DECIDED', 'collector_head_policy': 'CLI==SOURCE_COMMIT==actualHEAD09e，不以metadata角色放宽综合入口',
        'resource_thresholds_unchanged': {'startup_available_ram_bytes': 4831838208, 'c_disk_bytes': 8589934592, 'runtime_ram_stop_bytes': 536870912, 'tree_rss_bytes': 6442450944, 'sample_seconds': 1, 'root_consumer_seconds': 5},
        'archive_light_budget': {'tree_rss_bytes': 268435456, 'timeout_seconds': 120}, 'continuous_peak_bytes': None,
        'superseded_old_review_entries': review['superseded_own_index'], 'originals_overwritten': False, 'git_committed': False,
        'last_validation_self_reference_limit': '最终验证与finalseal的关闭原生流写新scratch，不自指入正式manifest；ROOT后续闭环封存保留该限制。'}
    write(OUT/'archive_receipt.json', receipt)
    recovery = {'status': 'RECOVERABLE_ARCHIVE_ONLY_NOT_PHYSICAL_APPROVAL', 'fixed_project_root': str(ROOT), 'source_commit': HEAD,
        'mapping': bind(OUT/'archive_mapping.json'), 'review_receipt': bind(OUT/'raw/final_review_receipt_r02.json'), 'review_index': bind(OUT/'raw/raw_manifest_r02.jsonl'),
        'restore_performed': False, 'restore_instruction': '按原完整绝对路径核验缺失、目标类型和ROOT明确范围后逐项SHA/bytes恢复；旧目录/索引/交付不覆盖。外部对象从已审r05包精确取回，不执行正式副本。',
        'existing_main_package': bind(MAIN/'delivery_manifest_r05.json'), 'actual_physical_not_started': True, 'historical_developer_tree': 'UNKNOWN'}
    write(OUT/'recovery_entry.json', recovery)
    command = ' '.join(sys.orig_argv)
    manifest('delivery_manifest_precheck.json', command)
    checker = loader()
    result = checker.check_manifest('evidence', str(OUT/'delivery_manifest_precheck.json'), str(ROOT))
    write(HERE/'schema_precheck.json', result)
    assert result['status']=='CHECKS_OK', result['errors']
    print(json.dumps({'status': receipt['status'], 'mapping_rows': len(mapping), 'mapping_bytes': receipt['mapping_bytes_including_duplicates'], 'counts': counts,
        'new_unique_objects': receipt['new_unique_raw_objects'], 'new_unique_bytes': receipt['new_unique_raw_bytes'], 'external_file_bindings': len(external), 'schema_precheck': result['status']}, ensure_ascii=False))

def seal():
    for label in ('archive', 'precheck_evidence', 'precheck_inputs'):
        for suffix in ('.stdout.bin', '.stderr.bin', '.native.json'):
            copy(HERE/(label+suffix), OUT/'raw'/(label+suffix))
    copy(HERE/'schema_precheck.json', OUT/'raw/schema_precheck.json')
    observations = []
    native_records = []
    for label in ('archive', 'precheck_evidence', 'precheck_inputs'):
        record = read(HERE/(label+'.native.json'))
        native_records.append(record)
        observations.append({'label': label, 'launcher_identity_after_wrapper_return': identity_read(record['launcher_identity']),
            'known_descendant_identity_terminal_observations': [identity_read(row) for row in record['known_descendant_identity_terminal_observations']], 'complete_tree_terminal': 'NOT_PROVEN'})
    metrics = {'scope': '仅本轮新归档包装实际出生身份及读回时点，不回填历史Developer/Reviewer身份', 'records': observations,
        'native_records': native_records, 'sampled_peak_bytes': max(row['sampled_owned_tree_peak_bytes'] for row in native_records),
        'unknown_count': sum(row['unknown_count'] for row in native_records), 'absolute_continuous_peak_bytes': None, 'last_finalseal_launcher_terminal': 'RUNNING_WHILE_BUILDING_PACKAGE'}
    write(OUT/'archive_identity_receipt.json', metrics)
    assert read(HERE/'precheck_evidence.native.json')['native_exit_code']==0
    assert read(HERE/'precheck_inputs.native.json')['native_exit_code']==2
    manifest('delivery_manifest.json', ' '.join(read(HERE/'archive.native.json')['command']), closed_checks=True)
    print(json.dumps({'manifest_sha256': digest(OUT/'delivery_manifest.json')[0], 'receipt_sha256': digest(OUT/'archive_receipt.json')[0], 'mapping_sha256': digest(OUT/'archive_mapping.json')[0],
        'recovery_sha256': digest(OUT/'recovery_entry.json')[0], 'identity_receipt_sha256': digest(OUT/'archive_identity_receipt.json')[0],
        'formal_file_count': sum(path.is_file() for path in OUT.rglob('*')), 'formal_bytes': sum(path.stat().st_size for path in OUT.rglob('*') if path.is_file()),
        'archive_sampled_peak_bytes': metrics['sampled_peak_bytes'], 'archive_unknown_count': metrics['unknown_count']}, ensure_ascii=False))

if __name__=='__main__': {'archive': archive, 'seal': seal}[sys.argv[1]]()
