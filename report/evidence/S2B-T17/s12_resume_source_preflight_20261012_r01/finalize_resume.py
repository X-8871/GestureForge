"""最终闭合当前已有原生流与事实；不覆写先前清单、receipt或工具。"""
import json
from pathlib import Path
import subprocess
import sys
import seal_resume as seal

HERE = seal.HERE
ROOT = seal.ROOT
OUT = seal.OUT

def git(label, *args):
    command = ['C:\\Program Files\\Git\\bin\\git.exe', '-c', 'core.longpaths=true', '-c', 'maintenance.auto=false', *args]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=30)
    for suffix, content in (('.stdout.bin', result.stdout), ('.stderr.bin', result.stderr)):
        with (HERE/(label+suffix)).open('xb') as stream: stream.write(content)
    row = {'command': command, 'cwd': str(ROOT), 'native_exit_code': result.returncode,
        'stdout': {'path': (HERE/(label+'.stdout.bin')).relative_to(ROOT).as_posix(), 'sha256': seal.digest(HERE/(label+'.stdout.bin'))},
        'stderr': {'path': (HERE/(label+'.stderr.bin')).relative_to(ROOT).as_posix(), 'sha256': seal.digest(HERE/(label+'.stderr.bin'))}}
    seal.write(HERE/(label+'.native.json'), row)
    assert result.returncode==0
    return result.stdout

original_write = seal.write

def final_write(path, value):
    if path.name.startswith('delivery_manifest'):
        gate = [row for row in value['checks'] if row['name']=='pnr_pending_negative_gate']
        assert len(gate)==1 and gate[0]['exit_code']==1
        gate[0]['status'] = 'FAIL'
        gate[0]['reason'] = '实际PNR prepare因缺未冻结综合依赖拒绝native1；预期拒绝断言在logic_tests native0通过。'
        value['checks'].append({'name': 'pnr_synth_dependency', 'status': 'BLOCKED', 'command': None, 'exit_code': None,
            'reason': '实际SYNTH_MANIFEST/SYNTH_G2为None/PENDING，未执行综合，不伪造退出码。'})
        for row in value['checks']:
            if row['name'].startswith(('precheck_', 'final_')) and row['status']=='FAIL':
                row['reason'] = '保留本轮此前包装真实失败原件，后续r03/r04修正后包装单独验证；不追认历史结果。'
        for label in ('r03_evidence', 'r03_inputs'):
            native = json.loads((HERE/(label+'.native.json')).read_text(encoding='utf-8'))
            value['checks'].append({'name': label, 'status': 'PASS' if native['native_exit_code']==0 else 'FAIL',
                'command': ' '.join(native['command']), 'exit_code': native['native_exit_code'],
                'reason': '实际evidence0；实际inputs2保留未冻结/未执行阻断；不是物理G0/G3通过。'})
        value['limitations'].append('final_resume_receipt.json与closed_packaging补齐结束前所有关闭原生流；此finalize与随后只读最终验证的关闭流保留在原tmp，ROOT统一封存提交时点。')
    original_write(path, value)

seal.write = final_write

def main():
    assert git('final_head', 'rev-parse', 'HEAD').decode('ascii').strip()==seal.p.SOURCE_COMMIT
    assert not git('final_staged', 'diff', '--cached', '--name-only').strip()
    freeze = json.loads((HERE/'source_freeze.json').read_text(encoding='utf-8'))
    for row in freeze['source_files']:
        assert seal.digest(ROOT/row['path'])==row['sha256']
    assert not seal.p.PROJECT.exists() and not seal.p.SYNTH_REPORT.exists() and not seal.p.PNR_REPORT.exists()
    natives = []
    late_mapping = []
    for path in sorted(HERE.glob('*.native.json')):
        if path.name=='finalize.native.json': continue
        row = json.loads(path.read_text(encoding='utf-8'))
        natives.append(dict(label=path.stem.removesuffix('.native'), **row))
        label = path.name.removesuffix('.native.json')
        for suffix in ('.stdout.bin', '.stderr.bin', '.native.json'):
            source = HERE/(label+suffix)
            target = OUT/'closed_packaging'/(label+suffix)
            if target.exists(): assert seal.digest(target)==seal.digest(source)
            else: seal.copy(source, target)
            late_mapping.append({'original_repo_path': source.relative_to(ROOT).as_posix(), 'archived_repo_path': target.relative_to(ROOT).as_posix(), 'sha256': seal.digest(target), 'bytes': target.stat().st_size})
    seal.copy(Path(__file__).absolute(), OUT/'finalize_resume.py')
    seal.write(OUT/'closed_native_mapping.json', {'rows': late_mapping})
    budget_rows = [row for row in natives if 'sampled_owned_tree_peak_bytes' in row]
    receipt = {'status': 'STOP_RESUME_PINS_LOGIC_G1_PENDING_INDEPENDENT_G2', 'source_commit': seal.p.SOURCE_COMMIT,
        'actual_head_before': '09e0135234ed257d1f878b80bf63eeefcdc6143f', 'actual_head_after': seal.p.SOURCE_COMMIT,
        'staged_empty_before': True, 'staged_empty_after': True, 'actual_raw_source_count_unchanged_after': 43,
        'source_before_native_exit_code': 0, 'logic_native_exit_code': 0, 'logic_cases': 20, 'pnr_prepare_native_exit_code': 1,
        'pnr_dependency': 'BLOCKED_None_PENDING', 'source_count': 43, 'raw_identical': 37, 'exact_eol': 6,
        'source_freeze_sha256': seal.digest(OUT/'source_freeze.json'), 'tool_binding_sha256': seal.digest(OUT/'tool_binding.json'),
        'author_receipt_sha256': seal.digest(OUT/'author_receipt.json'), 'raw_manifest_sha256': seal.digest(OUT/'raw_manifest.jsonl'),
        'closed_native_mapping_sha256': seal.digest(OUT/'closed_native_mapping.json'), 'helper_sha256': seal.digest(OUT/'tools/compat_pins.py'),
        'common_sha256': seal.digest(OUT/'tools/collector.py'),
        'sampled_owned_tree_peak_bytes': max(row['sampled_owned_tree_peak_bytes'] for row in budget_rows),
        'unknown_samples': sum(row['unknown_samples'] for row in budget_rows), 'absolute_tree_peak_bytes': None,
        'native_records': natives, 'max_elapsed_seconds': max(row['elapsed_seconds'] for row in budget_rows),
        'resource_admission': json.loads((OUT/'final_pins_test_receipt.json').read_text(encoding='utf-8'))['resource_admission'],
        'initial_launcher_host_exit_code': 1, 'initial_launcher_child_native_exit_code': None,
        'packaging_failure_history': '首PASS/native1与次BLOCKED/native1均schema失败，原件保留；schema修正为实际拒绝FAIL/native1和依赖BLOCKED/null后r03evidence0/inputs2。',
        'changed_tools': ['compat_pins.py'], 'functions_ast_unchanged': True, 'production_changed': False, 'git_committed': False,
        'hardware_vivado_ross_started': False, 'actual_source_after': 'NOT_RUN', 'resume_g2': 'NOT_RUN', 'physical_g0': 'BLOCKED', 'synth_pnr_budget_sta_g3_g5': 'NOT_RUN'}
    seal.write(OUT/'final_resume_receipt.json', receipt)
    seal.manifest('delivery_manifest_r05.json')
    print(json.dumps({'manifest_sha256': seal.digest(OUT/'delivery_manifest_r05.json'), 'final_receipt_sha256': seal.digest(OUT/'final_resume_receipt.json'),
        'source_freeze_sha256': receipt['source_freeze_sha256'], 'tool_binding_sha256': receipt['tool_binding_sha256'], 'author_receipt_sha256': receipt['author_receipt_sha256'],
        'raw_manifest_sha256': receipt['raw_manifest_sha256'], 'closed_native_mapping_sha256': receipt['closed_native_mapping_sha256'], 'helper_sha256': receipt['helper_sha256'],
        'peak_bytes': receipt['sampled_owned_tree_peak_bytes'], 'unknown_samples': receipt['unknown_samples']}, ensure_ascii=False))

if __name__=='__main__': main()
