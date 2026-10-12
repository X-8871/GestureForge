"""保留首次包装失败，新增canonical任务标识清单，不改源码或旧清单。"""
from pathlib import Path
import sys
import json
sys.path.insert(0,str(Path.cwd()/'verification'))
import test_s2b_conv_tile_origin_rtl as support
import test_s2b_backend_coordinates_rtl as backend

root=Path.cwd()
evidence=support.exact_directory(root/'report/evidence/S2B-T17/s15_arithmetic_fix_20261012_r01')
cache=support.exact_directory(root/'tmp/2B/S2B-T17/s15_timing_g0_20261012_r01')
target=evidence/'packaging_failure_r01'
target.mkdir()
checker=backend.load_checker()
for name in ('delivery_evidence_check.stdout.bin','delivery_evidence_check.stderr.bin','delivery_evidence_check.native.json'):
    path=checker.exact_file(cache/name)
    with (target/name).open('xb') as stream:stream.write(path.read_bytes())
with (evidence/'packaging_repair_source.py').open('xb') as stream:stream.write(Path(__file__).read_bytes())
failure=json.loads((target/'delivery_evidence_check.native.json').read_text(encoding='utf-8'))
assert failure['native_exit_code']==failure['direct_wait_exit_code']==2
support.save(evidence/'packaging_repair_receipt.json',dict(status='REPAIR_CANONICAL_TASK_ID_ONLY',old_manifest_sha256=support.sha(evidence/'delivery_manifest.json'),old_task_id='S2B-T17-S15',new_task_id='S2B-T17',reason='包装检查按task_id要求evidence_dir同名；既有批准目录为S2B-T17，故仅修正清单任务标识，S15保留在run_id/结果中。',native_failed_check=failure,production_unchanged=True))
manifest=json.loads((evidence/'delivery_manifest.json').read_text(encoding='utf-8'))
manifest['task_id']='S2B-T17'
manifest['files']=[item for item in manifest['files'] if not item['path'].startswith(evidence.relative_to(root).as_posix()+'/')]
for path in sorted(evidence.rglob('*')):
    if not path.is_file():continue
    role='source' if 'source_snapshot' in path.parts or path.suffix=='.py' else 'log' if path.suffix in ['.log','.bin'] and path.name!='cpu_layer0_expected.bin' else 'input' if path.suffix in ['.txt','.dat','.sv'] else 'result'
    manifest['files'].append(dict(path=path.relative_to(root).as_posix(),sha256=support.sha(path),role=role))
support.save(evidence/'delivery_manifest_r02.json',manifest)
print(json.dumps(dict(status='REPAIR_PACKAGING_ONLY',manifest_sha256=support.sha(evidence/'delivery_manifest_r02.json'),files=len(manifest['files'])),ensure_ascii=False))
