#!/usr/bin/env python3
"""第二轮独立复审：证据绑定负例与精确路径前置检查。"""
import copy
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

root = Path(__file__).absolute().parents[4]
out = Path(__file__).absolute().parent
spec = importlib.util.spec_from_file_location('checker', root / 'verification/check_s2b_inference_platform.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
sources = checker.check_static(root)
reviewed = {path: checker.sha256(root / path) for path in ['src/s2b_inference_top.sv', 'vivado/s2b_inference_platform.tcl',
    'board/s2b_inference_platform.json', 'board/s2b_inference_platform.md', 'verification/check_s2b_inference_platform.py']}
results = []

def save(name, data):
    """仅写新隔离目录；每项原件保持独立名称。"""
    path = out / name
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return path

def run(name, command, expected=0):
    """保留原生命令退出码及输出。"""
    env = os.environ.copy()
    env['VERILATOR_ROOT'] = 'D:/FPGA_S2A_MSYS2_20261001/env/mingw64/share/verilator'
    start = time.monotonic()
    process = subprocess.run(command, cwd=root, capture_output=True, env=env)
    (out / (name+'.stdout.log')).write_bytes(process.stdout)
    (out / (name+'.stderr.log')).write_bytes(process.stderr)
    results.append({'name': name, 'command': command, 'native_exit_code': process.returncode,
        'expected_exit_code': expected, 'seconds': time.monotonic()-start})
    assert process.returncode == expected, (name, process.stderr.decode(errors='replace'))

raw = out / 'synthetic_raw.txt'
raw.write_text('审查负例材料，不是运行证据，不得用于实际启用。\n', encoding='utf-8')
binding = {'path': raw.relative_to(root).as_posix(), 'sha256': checker.sha256(raw)}
runtime = {name: binding for name in ['elf','bsp','mmu','macros','ps_init','cold_lifecycle','uart_log','dap_log']}
profile = json.loads((root / 'board/s2b_inference_platform.json').read_text(encoding='utf-8'))
probe = copy.deepcopy(profile['prior_cache_probe'])
probe['dap_read_write_readback'] = True
proof = {'schema_version': 1, 'status': 'PASS', 'profile_version': profile['version'], 'source_sha256': sources, 'runtime_bindings': runtime}
artifacts = {
 'hp_path_audit': {'status': 'PASS', 'source_sha256': sources, 'checks': {x: True for x in ['axi3_nonbufferable_basis','axcache_0000_full_path','direct_hp0_no_bridge','no_early_write_response','full_model_core_present']}, 'evidence_files': [binding]},
 'ps_cache_proof': {'status': 'PASS', 'source_sha256': sources, 'checks': {x: True for x in ['dedicated_32mib_arena','cache_maintenance_actual_bsp','cpu_dap_prior_probe_idle_no_start','same_runtime_bsp_mmu_macros','no_use_amp','single_cacheable_alias','cpu1_other_writers_stopped','unified_cold_reset_lifecycle']}, 'prior_probe': probe, 'runtime_bindings': runtime, 'evidence_files': [binding]},
}

def fixture(name, mutate=None):
    """造隔离负例并绑定其独立哈希。"""
    p, a = copy.deepcopy(proof), copy.deepcopy(artifacts)
    if mutate: mutate(p, a)
    for key, artifact in a.items():
        path = save(name+'_'+key+'.json', artifact)
        p[key] = {'path': path.relative_to(root).as_posix(), 'sha256': checker.sha256(path)}
    pp = save(name+'_proof.json', p)
    rp = save(name+'_review.json', {'status':'PASS', 'role':'INDEPENDENT_REVIEWER',
        'approved_profile_sha256':checker.sha256(pp), 'visibility_parameter':1, 'cold_reset_only':True})
    return [sys.executable,'-B',str(root / 'verification/check_s2b_inference_platform.py'),
        '--visibility-proof',str(pp),'--review',str(rp),'--review-sha256',checker.sha256(rp)]

run('static', [sys.executable, '-B', str(root / 'verification/check_s2b_inference_platform.py')])
run('binding_only_fixture', fixture('binding_only_fixture'))
base = fixture('missing_fixed_hash')
run('missing_fixed_hash', base[:-2], 1)
base = fixture('wrong_fixed_hash'); base[-1] = '0'*64
run('wrong_fixed_hash', base, 1)
for field, value in [('epoch',1), ('epoch',False), ('start_count',1), ('load_count',1), ('physical_state','RUN'),
    ('visibility_parameter',1), ('operation',3), ('word_count',63), ('dap_read_write_readback',False)]:
    name = 'probe_'+field+'_'+str(value)
    run(name, fixture(name, lambda p,a,f=field,v=value: a['ps_cache_proof']['prior_probe'].update({f:v})), 1)
run('missing_runtime_binding', fixture('missing_runtime_binding', lambda p,a: a['ps_cache_proof']['runtime_bindings'].pop('mmu')), 1)
run('runtime_mismatch', fixture('runtime_mismatch', lambda p,a: p['runtime_bindings'].update({'elf': {'path':binding['path'],'sha256':'0'*64}})), 1)
run('missing_check', fixture('missing_check', lambda p,a: a['ps_cache_proof']['checks'].pop('same_runtime_bsp_mmu_macros')), 1)
run('stale_source', fixture('stale_source', lambda p,a: p['source_sha256'].update({'src/s2b_inference_top.sv':'0'*64})), 1)

target = out / 'junction_target'
target.mkdir()
junction = out / 'junction_parent'
run('create_junction', ['cmd.exe', '/d', '/c', 'mklink', '/J', str(junction), str(target)])
run('path_preflight', ['C:/Program Files/Git/ucrt64/bin/tclsh.exe', str(out / 'path_probe.tcl'), root.as_posix(), out.as_posix()])
rtl = profile['rtl_sources']
run('lint', ['D:/FPGA_S2A_MSYS2_20261001/env/mingw64/bin/verilator_bin.exe', '--lint-only','--timing','-Wall','-Wno-fatal',
    '--top-module','s2b_inference_top','--Mdir',str(out / 'obj_dir')] + [str(root/path) for path in rtl])
save('probe_results.json', {'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip(),
    'reviewed_source_sha256':reviewed, 'source_sha256':sources,
    'reviewed_sources_stable':reviewed == {path:checker.sha256(root/path) for path in reviewed},
    'complete_binding_sources_stable':sources == checker.check_static(root), 'runs':results,
    'limitations':['虚构fixture只验证机器binding，不构成真实批准。','没有Vivado/MCP/实物。','junction保留于隔离tmp，无删除。']})
print('R2_REVIEW_PROBES:OK')
