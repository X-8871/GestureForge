import importlib.util
import json
import shutil
import subprocess
import time
from pathlib import Path

scratch = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('owned_archive_support', scratch / 'archive.py')
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)
archive = support.ARCHIVE
started = time.perf_counter()
prior = archive / 'delivery_manifest_r02.json'
assert support.sha(prior) == '066e149694c5319d8abc3e33867f5e79ddaa20b65ac632d115a6f6282dcb5251'
manifest = json.loads(prior.read_text(encoding='utf-8'))
mapping = []
extra_files = []
names = ('final_evidence_r02.stdout.log', 'final_evidence_r02.stderr.log', 'final_evidence_r02.native.json',
         'final_inputs_r02.stdout.log', 'final_inputs_r02.stderr.log', 'final_inputs_r02.native.json',
         'wrapper_receipt_r02.json', 'complete_archive.stdout.log', 'complete_archive.stderr.log',
         'complete_archive.native.json', 'freeze_archive.py')
for name in names:
    original = support.exact_file(scratch / name)
    saved = archive / 'packaging_calls' / name
    assert not saved.exists()
    shutil.copyfile(original, saved)
    assert support.sha(saved) == support.sha(original)
    role = 'source' if name.endswith('.py') else 'log' if name.endswith('.log') else 'result'
    extra_files.append(support.local_entry(saved, role))
    mapping.append({'original_path': support.relative(original), 'archive_path': support.relative(saved),
                    'sha256': support.sha(saved), 'bytes': saved.stat().st_size})
    support.budget()
mapping_path = archive / 'packaging_calls_mapping_r03.json'
support.write_json(mapping_path, {'mapping': mapping, 'reason': '正式封包保存真实r02成功evidence0与受阻inputs2的原日志/native/包装器回执'})
extra_files.append(support.local_entry(mapping_path, 'result'))
manifest['files'].extend(extra_files)
manifest['files'].append(support.local_entry(prior, 'input'))
for mode in ('evidence', 'inputs'):
    native = json.loads((scratch / f'final_{mode}_r02.native.json').read_text(encoding='utf-8'))
    assert native['native_exit_code'] == (0 if mode == 'evidence' else 2)
    manifest['checks'].append({'name': f'归档r02实际{mode}包装检查',
                               'status': 'PASS' if mode == 'evidence' else 'FAIL',
                               'command': subprocess.list2cmdline(native['command']), 'exit_code': native['native_exit_code'],
                               'reason': '仅机器包装；物理接口未冻结、STA FAIL和预算BLOCKED保持原结论'})
manifest['checks'].append({'name': '归档补充包装器实际native0', 'status': 'PASS',
                           'command': json.loads((scratch / 'complete_archive.native.json').read_text(encoding='utf-8'))['command'],
                           'exit_code': 0, 'reason': '实际工具返回与原stdout/stderr绑定，首轮native1原件保留'})
final = archive / 'delivery_manifest_r03.json'
support.write_json(final, manifest)
evidence, evidence_paths = support.run_check('evidence', final, 'final_evidence_r03')
inputs, inputs_paths = support.run_check('inputs', final, 'final_inputs_r03')
for row in manifest['files']:
    assert support.sha(support.exact_file(support.ROOT / row['path'])) == row['sha256']
for name, expected in (('final_review_receipt.json', '5bbaaa083f904b557a33da5afe250fdff334f31ef0419507199a744e8bf63522'),
                       ('raw_manifest.jsonl', '8fc1f8da9fe6d3f18f530d6f20d1120f6582f7fb57e5cf96a5402143208ad827')):
    assert support.sha(support.ORIGIN / name) == expected
support.budget()
receipt = {'status': 'PASS_ARCHIVE_BINDING_ONLY', 'manifest': support.local_entry(final, 'result'),
           'source_commit': support.SOURCE_COMMIT, 'actual_evidence_head': support.EVIDENCE_HEAD,
           'original_entries_verified': 177, 'original_saved_mapping_verified': 509,
           'source_recovery_count': 43, 'raw_unique_copies': 168,
           'packaging_calls_copies': 19, 'physical_copied_original_files': 187,
           'manifest_file_bindings': len(manifest['files']),
           'elapsed_seconds': time.perf_counter() - started, 'archive_and_scratch_bytes': support.size_total(),
           'sampled_self_and_direct_child_rss_peak_bytes': support.OBSERVED_RSS_MAX,
           'absolute_process_tree_peak_bytes': None, 'final_evidence': evidence, 'final_inputs': inputs,
           'final_native_records': [support.local_entry(path, 'input') for path in (*evidence_paths, *inputs_paths)],
           'prior_native_results': {'archive_first': 1, 'initial_evidence_environment': 2,
                                    'runtime_probe': 1, 'complete_archive': 0, 'r02_evidence': 0, 'r02_inputs': 2},
           'business_sta': 'FAIL', 'business_budget': 'BLOCKED', 'independent_review_check_count': 59,
           'archive_limit_bytes': support.DISK_LIMIT, 'tree_limit_bytes': support.TREE_LIMIT, 'seconds_limit': support.TIME_LIMIT,
           'limitations': ['没有新增功能、RTL、重型、独审、实物或阶段验收',
                           '标准清单保留r01/r02/r03，原失败与成功包装原件已进入正式归档',
                           '仅自有包装器与直接checker采样；绝对整树峰和瞬时Git只读子进程峰未测',
                           '最终r03只读检查结果由本scratch回执SHA绑定；不制造循环自校验或修改已检查清单']}
support.write_json(scratch / 'wrapper_receipt_r03.json', receipt)
print(json.dumps({key: receipt[key] for key in ('status', 'manifest', 'physical_copied_original_files', 'manifest_file_bindings', 'elapsed_seconds', 'archive_and_scratch_bytes', 'sampled_self_and_direct_child_rss_peak_bytes')}, ensure_ascii=False))
