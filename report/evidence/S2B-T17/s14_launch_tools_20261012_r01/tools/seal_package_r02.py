"""保留首次清单检查失败，新建补齐适用性说明的包装清单；工具源码不变。"""
import hashlib
import json
from pathlib import Path
import shutil

W = Path(__file__).parent
ROOT = W.parents[3]
D = ROOT / 'report/evidence/S2B-T17/s14_launch_tools_20261012_r01'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert W.is_dir() and D.is_dir()
def save(path, value):
    assert path.is_relative_to(D) and not path.exists()
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
receipt = json.loads((D/'final_g1_receipt.json').read_text(encoding='utf-8'))
for row in receipt['tools']:
    assert sha(Path(row['original_absolute_path'])) == row['sha256']
    assert sha(ROOT/row['archived_repo_path']) == row['sha256']
for suffix in ('.stdout.bin', '.stderr.bin', '.native.json'):
    original = W/('s14_evidence_check_r01'+suffix)
    target = D/'validation'/original.name
    assert original.is_file() and not target.exists()
    target.parent.mkdir(exist_ok=True)
    shutil.copyfile(original, target)
    assert sha(original) == sha(target)
assert json.loads((W/'s14_evidence_check_r01.native.json').read_text(encoding='utf-8'))['native_exit_code'] == 2
assert json.loads((W/'s14_evidence_check_r01.stdout.bin').read_text(encoding='utf-8'))['errors'] == ['interfaces 为空时必须提供 interfaces_not_applicable_reason']
target = D/'tools'/Path(__file__).name
assert not target.exists()
shutil.copyfile(Path(__file__), target)
receipt['packaging_revision'] = dict(original_receipt_sha256=sha(D/'final_g1_receipt.json'), original_manifest_sha256=sha(D/'delivery_manifest.json'), initial_checker_native_exit_code=2, correction='仅新增interfaces_not_applicable_reason；保留初次失败清单/完整原始日志。', selftest_old_supervisor_field='继承selftest输出193416字段仅历史诊断，不能证明当前supervisor；当前0ad7实际SHA见tools与final_binding_checks_result。')
receipt['package_extra_source'] = dict(path=target.relative_to(ROOT).as_posix(), sha256=sha(target))
save(D/'final_g1_receipt_r02.json', receipt)
manifest = json.loads((D/'delivery_manifest.json').read_text(encoding='utf-8'))
manifest['interfaces_not_applicable_reason'] = '本次只交付资源监测及采集工具兼容修复，不改变业务接口；真实S14 SOURCE/profile/接口冻结仍由ROOT准备并复审。'
manifest['files'] = [dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path), role='source' if path.suffix=='.py' else 'log' if path.suffix in ('.bin','.log') else 'result') for path in sorted(D.rglob('*')) if path.is_file()]
save(D/'delivery_manifest_r02.json', manifest)
print(json.dumps(dict(status='STOP_G1_TOOLS_PENDING_INDEPENDENT_G2', receipt_r02_sha256=sha(D/'final_g1_receipt_r02.json'), manifest_r02_sha256=sha(D/'delivery_manifest_r02.json'), frozen_tool_files=len(receipt['tools'])), ensure_ascii=False))
