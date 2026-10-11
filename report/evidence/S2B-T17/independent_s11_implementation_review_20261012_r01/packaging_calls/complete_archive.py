import importlib.util
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

directory = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('owned_archive_support', directory / 'archive.py')
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)
archive = support.ARCHIVE
root = support.ROOT
start = time.perf_counter()
manifest_path = archive / 'delivery_manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
mapping = json.loads((archive / 'archive_mapping.json').read_text(encoding='utf-8'))
first_sha = support.sha(manifest_path)
files = {row['path']: row for row in manifest['files']}
extra_mapping = []


def copy_extra(path, role):
    support.exact_file(path)
    saved = archive / 'packaging_calls' / path.name
    saved.parent.mkdir(exist_ok=True)
    assert not saved.exists(), str(saved)
    shutil.copyfile(path, saved)
    assert support.sha(saved) == support.sha(path)
    entry = support.local_entry(saved, role)
    files[entry['path']] = entry
    extra_mapping.append({'original_path': support.relative(path), 'archive_path': support.relative(saved),
                          'sha256': entry['sha256'], 'bytes': saved.stat().st_size})
    support.budget()


# 复用已完成的归档，不重拷177原件；首版异常原件完整进入补充清单。
for row in mapping['mapping']:
    assert support.sha(support.exact_file(root / row['archive_path'])) == row['sha256']
for path, role in [(directory / name, 'source' if name.endswith('.py') else 'log' if name.endswith('.log') else 'result')
                   for name in ('archive.stdout.log', 'archive.stderr.log', 'archive_first.native.json',
                                'initial_evidence.stdout.log', 'initial_evidence.stderr.log', 'initial_evidence.native.json',
                                'runtime_probe_tool_return_transcription.json', 'complete_archive.py')]:
    copy_extra(path, role)
first_native = json.loads((directory / 'initial_evidence.native.json').read_text(encoding='utf-8'))
assert first_native['native_exit_code'] == 2
manifest['checks'].extend([
    {'name': '归档首版环境访问失败', 'status': 'FAIL', 'command': subprocess.list2cmdline(first_native['command']),
     'exit_code': 2, 'reason': 'sandbox拒绝project-root父目录访问；未进入业务包装核验，不是STA或设计失败'},
    {'name': '归档首版脚本异常退出', 'status': 'FAIL',
     'command': json.loads((directory / 'archive_first.native.json').read_text(encoding='utf-8'))['command'],
     'exit_code': 1, 'reason': '首版checker环境native2触发脚本断言；原stdout/stderr及native记录保留'},
    {'name': '缺失psutil环境探针', 'status': 'FAIL',
     'command': json.loads((directory / 'runtime_probe_tool_return_transcription.json').read_text(encoding='utf-8'))['command'],
     'exit_code': 1, 'reason': '实际工具返回转录，非原stderr；采用Windows标准库ctypes采样自有包装器与直接checker'}])
files[support.relative(manifest_path)] = support.local_entry(manifest_path, 'input')
manifest['limitations'].append('归档首版环境evidence2及脚本1保留；提权只读核验不改变业务STA FAIL与预算BLOCKED。')
supplement_path = archive / 'archive_supplement_mapping.json'
support.write_json(supplement_path, {'original_manifest_sha256': first_sha, 'supplement_mapping': extra_mapping,
                                    'reason': '保存归档包装首版环境失败及补充脚本；不覆盖任何原件或首版清单'})
files[support.relative(supplement_path)] = support.local_entry(supplement_path, 'result')
manifest['files'] = list(files.values())
final_manifest = archive / 'delivery_manifest_r02.json'
support.write_json(final_manifest, manifest)
evidence, evidence_paths = support.run_check('evidence', final_manifest, 'final_evidence_r02')
inputs, inputs_paths = support.run_check('inputs', final_manifest, 'final_inputs_r02')
for path, expected in (
    (support.ORIGIN / 'final_review_receipt.json', '5bbaaa083f904b557a33da5afe250fdff334f31ef0419507199a744e8bf63522'),
    (support.ORIGIN / 'raw_manifest.jsonl', '8fc1f8da9fe6d3f18f530d6f20d1120f6582f7fb57e5cf96a5402143208ad827')):
    assert support.sha(path) == expected
assert support.sha(manifest_path) == first_sha
for row in manifest['files']:
    assert support.sha(support.exact_file(root / row['path'])) == row['sha256']
support.budget()
receipt = {'status': 'PASS_ARCHIVE_BINDING_ONLY', 'source_commit': support.SOURCE_COMMIT,
           'actual_evidence_head': support.EVIDENCE_HEAD, 'manifest': support.local_entry(final_manifest, 'result'),
           'original_entries_verified': 177, 'original_restoration_verified': 509, 'source_recovery_count': 43,
           'raw_unique_copies': 168, 'original_mapping_count': len(mapping['mapping']),
           'supplement_copies': len(extra_mapping), 'manifest_file_bindings': len(manifest['files']),
           'archive_and_scratch_bytes': support.size_total(), 'elapsed_seconds': time.perf_counter() - start,
           'sampled_self_and_direct_child_rss_peak_bytes': support.OBSERVED_RSS_MAX,
           'absolute_process_tree_peak_bytes': None, 'final_evidence': evidence, 'final_inputs': inputs,
           'final_native_records': [support.local_entry(path, 'input') for path in (*evidence_paths, *inputs_paths)],
           'original_sta_status': 'FAIL', 'original_budget_status': 'BLOCKED',
           'checks_scope': '仅59项独立失败事实准确性和归档恢复；没有新增独审或部署验收',
           'limits': {'disk_bytes': support.DISK_LIMIT, 'tree_bytes': support.TREE_LIMIT, 'seconds': support.TIME_LIMIT},
           'prior_native_results': {'initial_evidence': 2, 'initial_archive': 1, 'psutil_probe': 1},
           'limits_and_recovery': ['180秒预算针对本次补充进程；首版另8.711秒，不重跑原归档或审查',
                                   '采样仅包装器与直接checker；绝对进程树峰和瞬时Git子进程峰未测',
                                   '最终r02核验日志在scratch，由本wrapper_receipt按SHA绑定供ROOT正式封包',
                                   '接口profile0.1.11、物理0.1.1未冻结，evidence0只表示包装准确；inputs2仍真实受阻']}
support.write_json(directory / 'wrapper_receipt_r02.json', receipt)
print(json.dumps({key: receipt[key] for key in ('status', 'manifest', 'raw_unique_copies', 'supplement_copies', 'manifest_file_bindings', 'archive_and_scratch_bytes', 'elapsed_seconds', 'sampled_self_and_direct_child_rss_peak_bytes')}, ensure_ascii=False))
