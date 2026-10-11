#!/usr/bin/env python3
"""独立审查静态门禁、公开口连接及 Tcl 新运行目录约束。"""
import copy
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

root = Path(__file__).absolute().parents[4]
out = Path(__file__).absolute().parent
spec = importlib.util.spec_from_file_location('platform_checker', root / 'verification/check_s2b_inference_platform.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
sources = checker.check_static(root)
results = []

def save(name, data):
    """只写隔离审查目录。"""
    path = out / name
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return path

def command(name, args, expected=0):
    """保存原生命令、日志与退出码。"""
    begin = time.monotonic()
    environment = os.environ.copy()
    environment['VERILATOR_ROOT'] = 'D:/FPGA_S2A_MSYS2_20261001/env/mingw64/share/verilator'
    run = subprocess.run(args, cwd=root, capture_output=True, env=environment)
    (out / (name + '.stdout.log')).write_bytes(run.stdout)
    (out / (name + '.stderr.log')).write_bytes(run.stderr)
    results.append({'name': name, 'command': args, 'native_exit_code': run.returncode,
                    'expected_exit_code': expected, 'seconds': time.monotonic()-begin,
                    'VERILATOR_ROOT': environment['VERILATOR_ROOT'] if name == 'lint' else None})
    assert run.returncode == expected, (name, run.returncode)

command('static', [sys.executable, '-B', str(root / 'verification/check_s2b_inference_platform.py')])
command('single_proof', [sys.executable, '-B', str(root / 'verification/check_s2b_inference_platform.py'),
                        '--visibility-proof', str(root / 'board/s2b_inference_platform.json')], 1)

raw = out / 'synthetic_raw.txt'
raw.write_text('这是审查生成的虚构材料，没有硬件验证结论。\n', encoding='utf-8')
proof = {'schema_version': 1, 'status': 'PASS', 'profile_version': 's2b-inference-platform/0.1.0', 'source_sha256': sources}
checks = {
    'hp_path_audit': ['axi3_nonbufferable_basis', 'axcache_0000_full_path', 'direct_hp0_no_bridge', 'no_early_write_response', 'full_model_core_present'],
    'ps_cache_proof': ['dedicated_32mib_arena', 'cache_maintenance_actual_bsp', 'cpu_cross_master_readback', 'no_use_amp', 'single_cacheable_alias', 'cpu1_other_writers_stopped', 'unified_cold_reset_lifecycle'],
}
for key, names in checks.items():
    path = save(key + '.json', {'status': 'PASS', 'source_sha256': sources,
        'checks': {name: True for name in names},
        'evidence_files': [{'path': raw.relative_to(root).as_posix(), 'sha256': checker.sha256(raw)}]})
    proof[key] = {'path': path.relative_to(root).as_posix(), 'sha256': checker.sha256(path)}
proof_path = save('synthetic_proof.json', proof)
review = {'status': 'PASS', 'role': 'INDEPENDENT_REVIEWER', 'approved_profile_sha256': checker.sha256(proof_path), 'visibility_parameter': 1, 'cold_reset_only': True}
review_path = save('synthetic_review.json', review)
command('synthetic_payload_acceptance', [sys.executable, '-B', str(root / 'verification/check_s2b_inference_platform.py'),
    '--visibility-proof', str(proof_path), '--review', str(review_path)])
mutations = [
    ('wrong_role', 'review', lambda p: p.update(role='DEVELOPER')),
    ('wrong_review_hash', 'review', lambda p: p.update(approved_profile_sha256='0'*64)),
    ('visibility_zero', 'review', lambda p: p.update(visibility_parameter=0)),
    ('no_cold_reset', 'review', lambda p: p.update(cold_reset_only=False)),
    ('stale_source', 'proof', lambda p: p['source_sha256'].update({'src/s2b_inference_top.sv': '0'*64})),
    ('proof_status', 'proof', lambda p: p.update(status='BUILD_CANDIDATE')),
    ('path_escape', 'proof', lambda p: p['hp_path_audit'].update(path='../AGENTS.md')),
    ('bad_artifact_hash', 'proof', lambda p: p['hp_path_audit'].update(sha256='0'*64)),
]
for name, kind, mutate in mutations:
    changed_proof, changed_review = copy.deepcopy(proof), copy.deepcopy(review)
    mutate(changed_review if kind == 'review' else changed_proof)
    pp = save(name + '_proof.json', changed_proof)
    if kind == 'proof': changed_review['approved_profile_sha256'] = checker.sha256(pp)
    rp = save(name + '_review.json', changed_review)
    command(name, [sys.executable, '-B', str(root / 'verification/check_s2b_inference_platform.py'),
        '--visibility-proof', str(pp), '--review', str(rp)], 1)

wrapper = (root / 'src/s2b_inference_top.sv').read_text(encoding='utf-8')
abi = []
for module, instance in [('s2a_stage2a_core_ooc','core'), ('s2b_control_csr','control'), ('s2b_hp0_word_adapter','adapter')]:
    source = (root / ('src/' + module + '.sv')).read_text(encoding='utf-8')
    header = source[:source.index(');')]
    header = re.sub(r'//[^\n]*', '', header)
    ports = set()
    for group in re.findall(r'\b(?:input|output)\s+(?:logic|wire)\s*(?:\[[^]]*\]\s*)?(.*?)(?=\binput|\boutput|$)', header, re.S):
        ports.update(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b', group))
    block = re.search(r'\b' + module + r'\s+' + instance + r'\s*\((.*?)\n    \);', wrapper, re.S).group(1)
    named = re.findall(r'\.([A-Za-z_][A-Za-z_0-9]*)\(', block)
    assert set(named) == ports and len(named) == len(set(named)), (module, ports-set(named), set(named)-ports)
    abi.append({'module': module, 'ports': sorted(ports), 'connections': len(named), 'source_sha256': checker.sha256(root / ('src/' + module + '.sv'))})
save('public_abi.json', abi)
rtl = json.loads((root / 'board/s2b_inference_platform.json').read_text(encoding='utf-8'))['rtl_sources']
command('lint', ['D:/FPGA_S2A_MSYS2_20261001/env/mingw64/bin/verilator_bin.exe', '--lint-only', '--timing', '-Wall', '-Wno-fatal',
    '--top-module', 's2b_inference_top', '--Mdir', str(out / 'obj_dir')] + [str(root / path) for path in rtl])
save('probe_results.json', {'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root).decode().strip(),
    'source_sha256': sources, 'source_stability': sources == checker.check_static(root), 'runs': results,
    'limitations': ['虚构材料被接受仅证明机器绑定不验证语义；这些材料绝不能用作实际启用审批。', '仅静态端口检查，未审T11功能。', '未运行Vivado IPI、综合、实现或实物。']})
print('REVIEW_PROBES:OK')
