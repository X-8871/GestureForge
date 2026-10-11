"""独立只读核查 S5 已关闭的失败综合证据；仅本目录可写。"""
import copy
import ctypes
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import traceback
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'report/evidence/S2B-T17/s5_platform_20261011_r01'
PRE = ROOT / 'report/evidence/S2B-T17/s5_source_preflight_20261011_r01'
CACHE = ROOT / 'tmp/2B/S2B-T17/s5_synthesis_collect_20261011_r01'
COMMIT = '5cb092dcce3631f310e67228738a674a6a82ce41'
MANIFEST_SHA = 'efc201ca9b69139aa95813403a5c0b8af0b22e89eb72a1bd29b439dc9f647945'
FINAL_SHA = 'd245c594c1f7ee4f332e66e671e7f1cf86bd88c8f5975c58f24e0e69110afefc'
START = time.monotonic()
CHECKS, NATIVE, DETAILS = [], [], {}


def require(ok, message):
    """不接受缺失值或隐式成功。"""
    if not ok:
        raise AssertionError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def exact(path):
    """逐级检查文件名大小写，验证完整路径及目标类型。"""
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), '文件目标类型错误：' + str(path))
    require(path.resolve().is_relative_to(ROOT), '目标超出项目：' + str(path))
    check = ROOT
    for part in path.relative_to(ROOT).parts:
        require(part in [p.name for p in check.iterdir()], '路径字符不匹配：' + str(path))
        check /= part
    return path


def read(path):
    return json.loads(exact(path).read_text(encoding='utf-8'))


def save(name, value):
    """禁止覆盖已有独审输出。"""
    path = OUT / name
    require(path.parent == OUT and not path.exists(), '输出目标已存在或越界')
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def binding(row, key='path'):
    path = exact(ROOT / row[key])
    raw = path.read_bytes()
    require(sha(raw) == row['sha256'], 'SHA不符：' + str(path))
    if 'bytes' in row:
        require(len(raw) == row['bytes'], '字节数不符：' + str(path))
    return raw


def memory_peak(pid):
    """读取本进程可测的 Windows 工作集峰；不冒充整个进程树。"""
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in ['PeakWorkingSetSize', 'WorkingSetSize',
            'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
            'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage']]
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    handle = kernel.OpenProcess(0x0410, False, pid)
    if not handle:
        return None
    try:
        data = Counters()
        data.cb = ctypes.sizeof(data)
        if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(data), data.cb):
            return None
        return {'peak_working_set_bytes': data.PeakWorkingSetSize,
                'peak_pagefile_bytes': data.PeakPagefileUsage, 'pid': pid}
    finally:
        kernel.CloseHandle(handle)


def run_native(label, command, expected, keep=True):
    started = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=60, env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    item = {'label': label, 'command': command, 'native_exit_code': result.returncode,
            'elapsed_seconds': time.monotonic() - started, 'stdout_sha256': sha(result.stdout),
            'stdout_bytes': len(result.stdout), 'stderr_sha256': sha(result.stderr),
            'stderr_bytes': len(result.stderr), 'process_tree_peak_memory_bytes': None}
    if keep:
        for suffix, raw in [('stdout.log', result.stdout), ('stderr.log', result.stderr)]:
            p = OUT / (label + '.' + suffix)
            require(not p.exists(), '日志目标已存在')
            p.write_bytes(raw)
            item[suffix.split('.')[0] + '_path'] = rel(p)
    else:
        item['stdout_policy'] = '固定Git对象及已绑定快照可恢复原字节；本次真实输出留SHA及bytes。'
    NATIVE.append(item)
    require(result.returncode == expected, '原生码不符：' + label + ':' + str(result.returncode))
    return result.stdout


def group(name, function):
    started = time.monotonic()
    try:
        function()
        item = {'name': name, 'status': 'PASS'}
    except Exception as exc:
        item = {'name': name, 'status': 'CHANGES_REQUIRED', 'error': repr(exc),
                'traceback': traceback.format_exc(), 'closure': '修正指出的绑定或解释后重新只读核验。'}
    item['elapsed_seconds'] = time.monotonic() - started
    CHECKS.append(item)
    print(json.dumps(item, ensure_ascii=False), flush=True)


def inventory_audit():
    manifest = read(BASE / 's5_collection_delivery_manifest_r02.json')
    require(sha((BASE / 's5_collection_delivery_manifest_r02.json').read_bytes()) == MANIFEST_SHA,
            '待审manifest变化')
    require(manifest['source_commit'] == COMMIT and len(manifest['files']) == 288
            and len(manifest['interfaces']) == 2, 'manifest基线/范围错误')
    require(len({r['path'] for r in manifest['files']}) == 288, 'manifest路径重复')
    roles = {'source', 'input', 'result', 'log', 'script', 'report', 'manifest', 'output', 'artifact'}
    for row in manifest['files']:
        require(set(row) == {'path', 'sha256', 'role'} and row['role'] in roles, 'role或files格式错误')
        binding(row)
    for row in manifest['interfaces']:
        binding(row)
    require(manifest['interfaces'][0]['frozen'] is True
            and manifest['interfaces'][1]['frozen'] is False
            and manifest['interfaces'][1]['version'] == 's2b-physical-candidate/0.1.1', '候选接口伪冻结')
    main = {rel(p): {'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size}
            for p in BASE.rglob('*') if p.is_file()}
    require(len(main) == 207 and sum(r['bytes'] for r in main.values()) == 8803895, 'formal封存数量不同')
    listed = {r['path'] for r in manifest['files']}
    require(set(main) - {rel(BASE / 's5_collection_delivery_manifest_r02.json')} <= listed, 'formal未完整绑定')
    original = read(BASE / 's5_collection_original_inventory.json')['files']
    require(len(original) == 56, '原始库存数量错误')
    for row in original:
        binding(row)
        require(row['path'] in listed, '初始原件遗漏')
    closed = read(BASE / 's5_collection_closed_inventory.json')
    require(closed['file_count'] == len(closed['files']) == 205
            and closed['total_bytes'] == sum(r['bytes'] for r in closed['files']) == 8680097, 'closed统计错误')
    for row in closed['files']:
        binding(row)
    require(set(main) - {r['path'] for r in closed['files']} == {
        rel(BASE / 's5_collection_closed_inventory.json'), rel(BASE / 's5_collection_delivery_manifest_r02.json')},
        'closed后有未声明文件')
    rootlog = read(BASE / 's5_collection_root_log_binding.json')
    binding(rootlog['snapshot'])
    require(rootlog['snapshot']['sha256'] == '2db94cb1610b60a00dfe8aa096ec886da103cfbb2d44e64cb58ad02294606eb5'
            and rootlog['active_log_consumed'] is False, 'root log封存错误')
    DETAILS['inventory'] = {'bindings': 288, 'interfaces': 2, 'formal_files': 207,
                            'formal_bytes': 8803895, 'initial_files': 56, 'new_files': 151,
                            'closed_files_before_manifest': 205, 'all_hashes_raw': True}


def source_audit():
    source = read(BASE / 's5_collection_source_binding.json')
    before, after = read(PRE / 'source_before.json'), read(PRE / 'source_after.json')
    for field, expected in [('source_before', '4bf20ffe8803a6296f3d9190d7e12da1267185790e58669e12ae6c9beba1d845'),
                            ('source_after', 'f62299dafeb80aad93881b45cc101b763382e20819ffb08b996a0b7588560a78'),
                            ('static_actual', 'fb94e84c9fb5bacccf35c5f7c76f3e1ee4afa6cd5a893dc071aeb13672602cdc')]:
        binding(source[field])
        require(source[field]['sha256'] == expected, '固定preflight哈希不同')
    freeze = json.loads(binding(source['source_freeze']))
    static = json.loads(binding(source['static_actual']))
    require(len(source['sources']) == len(before['source_files']) == len(after['source_files']) == 38,
            '38闭包错误')
    require(source['source_commit'] == before['source_commit'] == after['source_commit'] == static['source_commit'] == COMMIT,
            '实际源码基线不同')
    require(before['platform_static_source_count'] == after['platform_static_source_count'] == static['source_count'] == 31,
            'static数量错误')
    b = {r['path']: r for r in before['source_files']}
    a = {r['path']: r for r in after['source_files']}
    require(set(a) == set(b) == set(freeze['source_sha256']), '闭包成员不同')
    counts = {'RAW_IDENTICAL': 0, 'GIT_LF_TO_RAW_CRLF': 0}
    results = []
    for i, row in enumerate(source['sources']):
        raw = exact(ROOT / row['snapshot']).read_bytes()
        later = exact(ROOT / row['snapshot_after']).read_bytes()
        path = row['path']
        require(raw == later and sha(raw) == row['sha256'] == a[path]['sha256']
                == b[path]['sha256'] == freeze['source_sha256'][path] and len(raw) == row['bytes'], '源码RAW不符：' + path)
        blob = run_native('git_source_%02d' % i, ['git', 'show', COMMIT + ':' + path], 0, False)
        equal = blob == raw
        eol = not equal and b'\r' not in blob and blob.replace(b'\n', b'\r\n') == raw
        relation = 'RAW_IDENTICAL' if equal else 'GIT_LF_TO_RAW_CRLF'
        require(equal or eol, '非精确EOL差异：' + path)
        require(row['git_relation'] == relation and row['git_blob_sha256'] == sha(blob)
                and row['git_raw_same'] == equal and row['exact_git_lf_to_snapshot_crlf'] == eol
                and row['live_source_consumed'] is False and row['git_native_exit_code'] == 0, 'Git关系元数据不符')
        counts[relation] += 1
        results.append({'path': path, 'raw_sha256': sha(raw), 'git_blob_sha256': sha(blob), 'relation': relation})
    require(counts == {'RAW_IDENTICAL': 32, 'GIT_LF_TO_RAW_CRLF': 6}, 'Git/EOL数量不同')
    require(len(source['extra_bindings']) == 7 and set(a) - set(source['extra_bindings']) == set(static['source_sha256']),
            '31+7成员不同')
    require(all(a[p]['sha256'] == h for p, h in static['source_sha256'].items()), 'static哈希不符')
    originals = source['frozen14_sha256']
    require(len(originals) == 14 and originals == before['frozen14_sha256'] == after['frozen14_sha256'] == freeze['frozen14_sha256'],
            '原14冻结不符')
    require(all(sha((PRE / 'source_snapshot' / p).read_bytes()) == h for p, h in originals.items()), '原14字节改变')
    checker = run_native('git_checker', ['git', 'show', COMMIT + ':verification/check_stage_delivery.py'], 0, False)
    require(checker == (BASE / 's5_collection_stage_checker_snapshot.py').read_bytes(), 'checker不是固定GitRAW')
    g2 = exact(ROOT / 'report/evidence/S2B-T17/independent_patch_guard_review_20261011_r01/delivery_manifest_r03.json')
    require(sha(g2.read_bytes()) == '9c31c881c39158f61380d9745480d7890974ff249554f4769a7f3a5d1ed1ce12', 'S5等价G2入口不同')
    prior = json.loads(binding(source['prior_s4_source_before']))
    require(len(prior['source_files']) == 37 and set(a) - {r['path'] for r in prior['source_files']} ==
            {'report/evidence/S2A-T01/tiny416_model_manifest.json'}, 'S4到S5新增绑定不同')
    DETAILS['sources'] = {'source_count': 38, 'static_count': 31, 'extra_count': 7, 'counts': counts,
                          'original14_unchanged': True, 'results': results,
                          'freeze_old_metadata_preserved': True, 'live_s6_consumed': False,
                          'g2_scope': '仅核既有等价G2入口哈希；不继承STA通过。'}


def native_audit():
    native = read(BASE / 's5_collection_native_mapping.json')
    require(len(native['files']) == native['native_raw_copy_count'] == 94 and len(native['jobs']) == 5, 'native数量不同')
    require(len({r['saved_path'] for r in native['files']}) == 94, 'native路径重复')
    vds = 0
    for row in native['files']:
        raw = binding(row, 'saved_path')
        require(exact(ROOT / row['original_path']).read_bytes() == raw, 'native副本不等于原件')
        suffix = Path(row['saved_path']).suffix.lower()
        require(suffix not in ['.dcp', '.pb', '.wdf'], '混入缓存')
        if suffix == '.vds':
            raw.decode('utf-8')
            vds += 1
    require(vds == 5, '实际文本VDS不足五份')
    results = []
    for job in native['jobs']:
        directory = ROOT / job['saved_directory']
        require((directory / '.vivado.end.rst').is_file() and (directory / '__synthesis_is_complete__').is_file()
                and not (directory / '.vivado.error.rst').exists(), '完成marker错误')
        log = exact(directory / 'runme.log').read_text(encoding='utf-8')
        launcher = int(ET.fromstring((directory / '.vivado.begin.rst').read_bytes()).find('Process').attrib['Pid'])
        pid = int(re.search(r'Process ID\s*:\s*(\d+)', log)[1])
        peak = max(map(float, re.findall(r'peak = ([0-9.]+)', log)))
        h, m, s = map(int, re.search(r'synth_design: Time \(s\):.*?elapsed = (\d+):(\d+):(\d+)', log).groups())
        diag = list(map(int, re.findall(r'(\d+) Infos, (\d+) Warnings, (\d+) Critical Warnings and (\d+) Errors encountered\.', log)[-1]))
        require(pid == job['actual_vivado_job_pid'] and launcher == job['launcher_pid_from_begin_rst'], 'job PID不符')
        require(peak == job['reported_single_process_peak_mb'] and h * 3600 + m * 60 + s == job['synth_design_elapsed_seconds'],
                'job耗时/峰不同')
        require(dict(zip(['infos', 'warnings', 'critical_warnings', 'errors'], diag)) == job['final_diagnostics']
                and diag[2:] == [0, 0] and job['raw_os_process_exit_code'] is None, '诊断或OS退出码错误')
        require(job['session_start_local'] in log and job['session_end_local'] in log, 'job起止时间不同')
        results.append({'run': job['run'], 'pid': pid, 'launcher_pid': launcher,
                        'synth_seconds': h * 3600 + m * 60 + s, 'single_process_peak_mb': peak, 'diagnostics': diag})
    tcl = exact(BASE / 'native_jobs/s2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl').read_text(encoding='utf-8')
    block = re.search(r'read_verilog -library xil_defaultlib -sv \{(.*?)\}', tcl, re.S)[1]
    compiled = [rel(Path(p.strip())) for p in block.splitlines() if p.strip()]
    profile = read(PRE / 'source_snapshot/board/s2b_inference_platform.json')
    require(len(compiled) == len(set(compiled)) == 18 and set(compiled) == set(profile['rtl_sources'])
            == set(native['actual_compiled_rtl_sources']), '实际编译18闭包错误')
    source = {r['path']: r for r in read(BASE / 's5_collection_source_binding.json')['sources']}
    require(len(native['actual_compiled_source_snapshots']) == 18, '编译快照不全')
    for row in native['actual_compiled_source_snapshots']:
        require(row['source_identifier'] in compiled and row['sha256'] == source[row['source_identifier']]['sha256'],
                '编译源码快照不符')
        require(sha(exact(ROOT / row['source_snapshot']).read_bytes()) == row['sha256'], '编译snapshotRAW错误')
    wrapper = binding(native['wrapper_import'])
    require(wrapper == binding(native['wrapper_generated_original'])
            == (BASE / 'generated_inputs/s2b_inference_wrapper.v').read_bytes()
            and len(wrapper) == 2637, 'wrapper复制错误')
    wrapper_tcl = (BASE / 'native_jobs/wrapper_native_s5_r01/s2b_inference_wrapper.tcl').read_text(encoding='utf-8')
    require(wrapper_tcl.count('imports/hdl/s2b_inference_wrapper.v') == 1
            and native['unique_registered_wrapper_count_from_setup'] == 1, 'wrapper注册不唯一')
    require(profile['profile_version'] == 's2b-inference-platform/0.1.5' and profile['visibility_default'] == 0
            and profile['clock_hz'] == 50000000 and profile['vivado_part'] == 'xc7z020clg400-2', 'profile错误')
    require(max(r['single_process_peak_mb'] for r in results) == 2209.809, '单job最大峰不同')
    infer = next(r for r in results if r['run'] == 's2b_inference_infer_0_synth_1')
    require((infer['synth_seconds'], infer['single_process_peak_mb']) == (159, 2200.098), '核心统计不同')
    DETAILS['native_jobs'] = results
    DETAILS['compiled'] = {'count': 18, 'wrapper_count': 1, 'vds_text_count': vds, 'clock_hz': 50000000,
                           'part': 'xc7z020clg400-2', 'visibility': 0, 'profile': profile['profile_version']}


def mcp_audit():
    metadata = read(BASE / 's5_collection_mcp_history_binding.json')
    raw = read(BASE / 'mcp_closed/mcp_history_closed.json')
    history = json.loads(raw['content'][0]['text'])['history']
    require(len(history) == 9 and {r['id'] for r in history} == set(range(95, 104)), 'history95至103不完整')
    pairs = metadata['paired_calls']
    require(len(pairs) == 9, 'MCP配对数量错误')
    for native, pair in zip(history, pairs):
        require(native == pair['native_history'], 'history配对不同')
        client = json.loads(binding(pair['client_record']))
        require(client['input']['command'] == native['command'] and client['wall_ms'] == pair['client_wall_ms'], 'client命令不同')
        if pair['label'] == 'wait':
            require(client['result']['isError'] is True and 'after 300s' in client['result']['content'][0]['text'], 'client timeout丢失')
        else:
            require(json.loads(client['result']['content'][0]['text'])['exit_code'] == native['code'], 'client与native码不同')
    by = {r['id']: r for r in history}
    require((by[95]['code'], by[96]['code'], by[96]['elapsed'], by[99]['code'], by[99]['elapsed'],
             by[101]['code'], by[101]['elapsed'], by[103]['code']) == (0, 1, 23.28, 0, 301.425, 0, 22.382, 0), '关键native码/耗时不同')
    require(by[103]['command'] == 'close_project' and by[103]['output'] == '', '项目未关闭')
    require(by[102]['output'].count('status {synth_design Complete!} progress 100%') == 5
            and by[102]['output'].count('status {Not started} progress 0%') == 5, 'synth/impl状态错误')
    require('18:26:44 2026' in by[98]['output'] and '18:32:18 2026' in by[99]['output']
            and '18:32:19 2026' in by[99]['output'], 'native实际起止时间不同')
    status = json.loads(read(BASE / 'mcp_closed/status_post_client_timeout.json')['content'][0]['text'])
    require(status['last_completed'] == 'wait_on_run synth_1' and status['last_completed_code'] == 0
            and status['last_completed_elapsed'] == 301.425 and status['is_command_running'] is False, 'timeout后实际状态不同')
    products = (BASE / 'products.tcldict').read_text(encoding='utf-8')
    for token in ['status FAIL code 0 raw PRODUCTS:OK', 'WARNING emitted=-8 exported=2',
                  'native_counts_before {WARNING 9', 'native_counts_after {WARNING 1']:
        require(token in products, 'products原始失败缺失')
    require(metadata['implementation_started'] is False and metadata['products_repeated'] is False
            and metadata['execute_plus_history_calls'] == 10 and metadata['post_timeout_status_queries'] == 1
            and metadata['root_session_peak_is_s5_run_peak'] is False and metadata['process_tree_peak_memory_bytes'] is None,
            'MCP统计外推错误')
    failure = metadata['source_json_host_serialization_failure']
    require(failure['host_native_exit_code'] == 1 and failure['target_written_by_failed_attempt'] is False
            and '逐字节' in failure['recovery_basis'], '序列化失败透明度不足')
    DETAILS['mcp'] = {k: metadata[k] for k in ['mcp_execute_calls', 'mcp_history_calls', 'execute_plus_history_calls',
        'post_timeout_status_queries', 'client_wait_is_error', 'client_wait_timeout_seconds', 'client_wait_wall_ms',
        'native_wait_exit_code', 'native_wait_elapsed_seconds', 'launch_to_native_wrapper_exit_seconds',
        'launch_to_launcher_finished_seconds', 'products_native_exit_code', 'products_capture_exit_code',
        'whole_builder_native_exit_code', 'root_session_cumulative_peak_mb', 'process_tree_peak_memory_bytes', 'implementation_started']}


def parse_timing(text):
    """从原报告区段独立解析，拒绝伪状态、重复汇总和时钟修改。"""
    require(re.findall(r'^\| Design State\s*:\s*(.+)$', text, re.M) == ['Synthesized'], '不是综合态')
    section = text.split('| Design Timing Summary', 1)[1].split('| Clock Summary', 1)[0]
    rows = [line.split() for line in section.splitlines()
            if re.fullmatch(r'\s*-?\d+\.\d+(?:\s+-?\d+(?:\.\d+)?){11}\s*', line)]
    require(len(rows) == 1, '汇总行不唯一')
    names = ['wns_ns', 'tns_ns', 'setup_failing_endpoints', 'setup_total_endpoints', 'whs_ns', 'ths_ns',
             'hold_failing_endpoints', 'hold_total_endpoints', 'wpws_ns', 'tpws_ns', 'pulse_failing_endpoints', 'pulse_total_endpoints']
    values = {k: float(v) if k.endswith('_ns') else int(v) for k, v in zip(names, rows[0])}
    require(re.findall(r'^clk_fpga_0\s+\{[\d.]+\s+[\d.]+\}\s+([\d.]+)\s+([\d.]+)\s*$', text, re.M)
            == [('20.000', '50.000')], '时钟不同')
    require('Timing constraints are not met.' in text and values['wns_ns'] < 0
            and values['setup_failing_endpoints'] > 0, '文字与时序数值矛盾')
    return values


def reports_audit():
    timing_text = (BASE / 'timing_summary_synth.rpt').read_text(encoding='utf-8')
    timing = parse_timing(timing_text)
    summary = read(BASE / 's5_collection_summary_final.json')
    require(timing == summary['timing'] == read(BASE / 's5_collection_sta_result.json')['timing'], 'STA原值与分类不同')
    require((timing['wns_ns'], timing['tns_ns'], timing['setup_failing_endpoints'], timing['setup_total_endpoints'],
            timing['whs_ns'], timing['ths_ns'], timing['wpws_ns'], timing['tpws_ns']) ==
            (-12.623, -4759.345, 763, 14804, 0.037, 0, 8.870, 0), 'STA关键值不同')
    for name, value in summary['check_timing'].items():
        require(set(re.findall(r'checking ' + name + r' \((\d+)\)', timing_text)) == {'0'} and value == 0, 'check_timing计数不同')
    worst = (BASE / 'timing_worst_synth.rpt').read_text(encoding='utf-8')
    def first(pattern):
        return re.search(pattern, worst, re.M)[1]
    values = {'source': first(r'^\s*Source:\s*(\S+)'), 'destination': first(r'^\s*Destination:\s*(\S+)'),
              'logic_levels': int(first(r'^\s*Logic Levels:\s*(\d+)')), 'carry4': int(first(r'^\s*Logic Levels:.*?CARRY4=(\d+)')),
              'dsp48e1': int(first(r'^\s*Logic Levels:.*?DSP48E1=(\d+)')),
              'data_path_delay_ns': float(first(r'^\s*Data Path Delay:\s*([\d.]+)ns')),
              'logic_delay_ns': float(first(r'^\s*Data Path Delay:.*?logic ([\d.]+)ns')),
              'route_delay_ns': float(first(r'^\s*Data Path Delay:.*?route ([\d.]+)ns'))}
    require(values == summary['worst_path'] and values['logic_levels'] == 62 and values['carry4'] == 38
            and values['dsp48e1'] == 1 and values['data_path_delay_ns'] == 32.219, '最差路径原值不同')
    require(values['source'].endswith('/validation_ok6__5/CLK') and values['destination'].endswith('/result_error_latched_reg[0]/D'),
            'CONV路径端点不同')
    conv = (PRE / 'source_snapshot/src/s2b_conv_tile_engine.sv').read_text(encoding='utf-8')
    require('validation_ok6' in conv and 'result_error_latched' in conv, '报告与固定CONV源码不对应')
    util = (BASE / 'utilization_flat_synth.rpt').read_text(encoding='utf-8')
    resource_rows = [('lut', 'Slice LUTs*'), ('ff', 'Slice Registers'), ('bram', 'Block RAM Tile'), ('dsp', 'DSPs'), ('latch', 'Register as Latch')]
    resources = {key: int(re.search(r'^\|\s*' + re.escape(label) + r'\s*\|\s*(\d+)\s*\|', util, re.M)[1]) for key, label in resource_rows}
    require(resources == summary['resources'] == {'lut': 24470, 'ff': 4028, 'bram': 32, 'dsp': 156, 'latch': 0}, '资源统计不同')
    xdc = (BASE / 'constraints_synth.xdc').read_text(encoding='utf-8')
    falsepaths = re.findall(r'^current_instance ([^\n]+)\n(set_false_path[^\n]+)', xdc, re.M)
    constraints = read(BASE / 's5_collection_constraints_binding.json')
    require([{'scope': a, 'command': b} for a, b in falsepaths] == constraints['exported_reset_cdc_false_paths']
            and len(falsepaths) == xdc.count('set_false_path') == 2, '两scoped resetCDC例外错误')
    require('create_clock -period 20.000 -name clk_fpga_0' in xdc and 'set_input_jitter clk_fpga_0 0.600' in xdc, '实际约束不同')
    require('No valid timing exceptions found.' in (BASE / 'exceptions_synth.rpt').read_text(encoding='utf-8'), '例外报告原文缺失')
    methodology = (BASE / 'methodology_synth.rpt').read_text(encoding='utf-8')
    require('747' in methodology and 'TIMING-16' in methodology, 'methodology条目缺失')
    for name in ['timing_summary_synth.rpt', 'timing_worst_synth.rpt', 'utilization_flat_synth.rpt', 'utilization_synth.rpt',
                 'clocks_synth.rpt', 'exceptions_synth.rpt', 'methodology_synth.rpt', 'drc_synth.rpt']:
        text = (BASE / name).read_text(encoding='utf-8')
        require('Vivado v.2026.1' in text and 'Design State : Synthesized' in text, '报告版本或状态错误：' + name)
    DETAILS['reports'] = {'status': 'FAIL_TIMING', 'timing': timing, 'resources': resources, 'worst_path': values,
                          'exported_scoped_reset_false_paths': falsepaths, 'check_timing_all_zero': True,
                          'methodology_rule': 'TIMING-16', 'methodology_checks': 747,
                          'exception_report_statement': 'No valid timing exceptions found.'}


def xsa_audit():
    comp = read(BASE / 's5_collection_xsa_member_comparison.json')
    binding(comp['old_xsa'])
    binding(comp['new_xsa'])
    with zipfile.ZipFile(ROOT / comp['old_xsa']['path']) as old, zipfile.ZipFile(ROOT / comp['new_xsa']['path']) as new:
        require(set(old.namelist()) == set(new.namelist()) and not any(n.lower().endswith('.bit') for n in new.namelist()), 'XSA集合或bit错误')
        for row in comp['members']:
            a, b = old.read(row['member']), new.read(row['member'])
            require(sha(a) == row['old_sha256'] and sha(b) == row['new_sha256'] and len(a) == row['old_bytes']
                    and len(b) == row['new_bytes'] and (a == b) == row['raw_equal'], 'XSA成员字节不符')
            require(old.getinfo(row['member']).CRC == row['old_crc32'] and new.getinfo(row['member']).CRC == row['new_crc32'], 'XSA CRC不同')
            if 'generated_original' in row:
                require(binding(row['generated_original']) == b and binding(row['saved_copy'], 'saved_path') == b, 'PSinit原件/副本不同')
        require(sum(r['raw_equal'] for r in comp['members']) == 6 and len(comp['members']) == 7
                and comp['members'][-1]['member'] == 's2b_inference.hwh' and comp['members'][-1]['raw_equal'] is False, '六PSinit/HWH错误')
        metadata = json.loads(new.read('xsa.json'))
        require(metadata['platformState'] == 'pre_synth' and metadata['devices'][0]['part']['name'] == 'xc7z020clg400-2', 'XSA原状态不同')
    pstcl = (BASE / 'generated_inputs/ps7_init.tcl').read_text(encoding='utf-8')
    for row in comp['official_generated_postconfig_tables']:
        body = re.search(r'proc ' + row['official_generated_procedure'] + r' \{\} \{([^}]+)\}', pstcl)[1]
        require([line.strip() for line in body.splitlines() if line.strip()] == row['operations'], 'postconfig表不等于实际生成源')
    require(comp['elf_runtime_compatibility'] == 'NOT_APPROVED', '错误继承runtime兼容批准')
    DETAILS['xsa'] = {'psinit_equal_members': 6, 'hwh_equal': False, 'contains_bit': False,
                      'state': 'pre_synth', 'runtime_approval': False, 'postconfig_operations_executed': False}


def failure_audit():
    final_path = exact(CACHE / 'final_status.json')
    require(sha(final_path.read_bytes()) == FINAL_SHA, 'collector STOP版本变化')
    final = read(final_path)
    require(final['final_manifest']['sha256'] == MANIFEST_SHA and final['formal_report_files'] == 207
            and final['formal_report_bytes'] == 8803895 and final['status'].startswith('STOP_S5_FAIL_TIMING'), '最终STOP状态错误')
    codes = {}
    copies = []
    for stem, code in [('s5_collection_collector', 0), ('s5_collection_sta', 2), ('s5_collection_evidence_r01', 0),
                       ('s5_collection_inputs_r01', 2), ('s5_finalization', 0), ('s5_final_evidence', 0), ('s5_final_inputs', 2)]:
        original = exact(CACHE / (stem + '.native.json'))
        item = read(original)
        require(item['native_exit_code'] == code, '保留native码不同：' + stem)
        codes[stem] = {'native_exit_code': code, 'elapsed_seconds': item['elapsed_seconds']}
        for row in item['closed_logs']:
            binding(row)
        for p in [original] + [ROOT / row['path'] for row in item['closed_logs']]:
            raw = exact(p).read_bytes()
            target = OUT / ('upstream_' + p.name)
            require(not target.exists(), '关闭原件复制目标存在')
            target.write_bytes(raw)
            copies.append({'original_path': rel(p), 'saved_path': rel(target), 'sha256': sha(raw), 'bytes': len(raw)})
    (OUT / 'upstream_final_status.json').write_bytes(final_path.read_bytes())
    require(final['final_checks']['evidence']['native_exit_code'] == 0 and final['final_checks']['inputs']['native_exit_code'] == 2,
            '包装与测试结果混淆')
    manifest = read(BASE / 's5_collection_delivery_manifest_r02.json')
    notrun = [r for r in manifest['checks'] if r['status'] == 'NOT_RUN']
    require(len(notrun) == 7 and all(r['command'] is None and r['exit_code'] is None for r in notrun), 'NOT_RUN丢失或伪造码')
    fail = [r for r in manifest['checks'] if r['status'] == 'FAIL']
    require(sorted(r['exit_code'] for r in fail) == [1, 2, 2], 'FAIL被改判PASS')
    DETAILS['preserved_failures'] = {'native_codes': codes, 'upstream_closed_copies': copies,
        'not_run_names': [r['name'] for r in notrun], 'collector_stop_sha256': FINAL_SHA,
        'finalizer_inner_and_wrapper_elapsed_separate': {'inner': final['finalize_elapsed_seconds'],
                                                       'wrapper': codes['s5_finalization']['elapsed_seconds']}}


def checker_audit():
    checker = str(BASE / 's5_collection_stage_checker_snapshot.py')
    manifest = str(BASE / 's5_collection_delivery_manifest_r02.json')
    for mode, code in [('evidence', 0), ('inputs', 2)]:
        stdout = run_native('checker_' + mode, [sys.executable, '-B', '-X', 'utf8', checker, '--mode', mode,
                          '--manifest', manifest, '--project-root', str(ROOT)], code)
        require(('CHECKS_OK' in stdout.decode('utf-8')) == (mode == 'evidence'), '包装与inputs混淆')
    run_native('classifier_original', [sys.executable, '-B', '-X', 'utf8', str(BASE / 's5_collection_classify_s5_sta.py'),
               '--report', str(BASE / 'timing_summary_synth.rpt'), '--result', str(OUT / 'classifier_original_result.json')], 2)
    DETAILS['independent_native'] = {'evidence': 0, 'inputs': 2, 'classifier': 2,
                                    'checker_source': 'Git5cb固定字节；没有运行live S6平台checker。'}


def counterexamples():
    """反例仅在内存修改元数据或报告文本，不覆盖任何业务原件。"""
    cases = []
    def reject(name, operation):
        try:
            operation()
        except (AssertionError, ValueError, IndexError, KeyError) as exc:
            cases.append({'name': name, 'status': 'EXPECTED_REJECTION', 'exception': repr(exc)})
        else:
            raise AssertionError('未拒绝反例：' + name)
    item = copy.deepcopy(read(BASE / 's5_collection_delivery_manifest_r02.json')['files'][0])
    item['sha256'] = '0' * 64
    reject('SHA篡改', lambda: binding(item))
    row = copy.deepcopy(read(BASE / 's5_collection_original_inventory.json')['files'][0])
    row['bytes'] += 1
    reject('字节数篡改', lambda: binding(row))
    item2 = copy.deepcopy(item)
    item2['path'] += '.不存在'
    reject('精确路径不存在', lambda: binding(item2))
    text = (BASE / 'timing_summary_synth.rpt').read_text(encoding='utf-8')
    reject('综合状态伪实现态', lambda: parse_timing(text.replace('Design State : Synthesized', 'Design State : Routed')))
    reject('时序文字伪通过', lambda: parse_timing(text.replace('Timing constraints are not met.', 'Timing constraints are met.')))
    reject('50MHz伪25MHz', lambda: parse_timing(text.replace('20.000', '40.000')))
    reject('summary区缺失', lambda: parse_timing(text.replace('| Design Timing Summary', '| Missing Timing Summary')))
    line = next(l for l in text.split('| Design Timing Summary', 1)[1].split('| Clock Summary', 1)[0].splitlines()
                if re.fullmatch(r'\s*-?\d+\.\d+(?:\s+-?\d+(?:\.\d+)?){11}\s*', l))
    reject('summary重复行', lambda: parse_timing(text.replace(line, line + '\n' + line)))
    raw = (PRE / 'source_snapshot/src/s2b_conv_tile_engine.sv').read_bytes()
    reject('源码单字节变化', lambda: require(sha(raw + b'\n') == sha(raw), '源码RAW改变'))
    interface = copy.deepcopy(read(BASE / 's5_collection_delivery_manifest_r02.json')['interfaces'][1])
    interface['frozen'] = True
    reject('候选接口伪冻结', lambda: require(interface['frozen'] is False, '候选接口必须未冻结'))
    DETAILS['counterexamples'] = cases


def main():
    require(ROOT == Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition'), '精确ROOT错误')
    for name, function in [('288绑定/56原件/207封存', inventory_audit), ('38源码/Git32RAW+6EOL/31+7/原14', source_audit),
        ('94native/五job/5文本VDS/18编译/wrapper', native_audit), ('MCP95至103/timeout/native/原失败', mcp_audit),
        ('STA/资源/路径/约束/报告版本', reports_audit), ('六PSinit/HWH/postconfig表/no-bit', xsa_audit),
        ('collector STOP及实际失败/NOT_RUN', failure_audit), ('固定checker/classifier原生执行', checker_audit),
        ('十项轻量元数据篡改反例', counterexamples)]:
        group(name, function)
    status = 'PASS_EVIDENCE_INTEGRITY_ONLY' if all(r['status'] == 'PASS' for r in CHECKS) else 'CHANGES_REQUIRED'
    save('native_commands.json', {'commands': NATIVE, 'count': len(NATIVE)})
    receipt = {'schema_version': 1, 'status': status, 'execution_state': 'STOP', 'review_task': 'S2B-T17-S5-G2',
        'reviewed_source_commit': COMMIT, 'reviewed_manifest': rel(BASE / 's5_collection_delivery_manifest_r02.json'),
        'reviewed_manifest_sha256': MANIFEST_SHA, 'reviewed_collector_stop_sha256': FINAL_SHA,
        'created_at_utc8': datetime.now(timezone(timedelta(hours=8))).isoformat(), 'checks': CHECKS, 'details': DETAILS,
        'native_command_count': len(NATIVE), 'elapsed_seconds': time.monotonic() - START,
        'reviewer_process_memory': memory_peak(os.getpid()), 'process_tree_peak_memory_bytes': None,
        'modification_scope': rel(OUT), 'project_code_modified': False, 'git_or_state_modified': False,
        'review_scope': 'S5失败证据准确性和完整性；不审S6，不重跑RTL/综合，不操作设备/ROSS。',
        'setup_corrections': ['exec_command的shell参数未启用Git Bash；改为PowerShell显式调用Bash。',
                              '首次只读摘要打印遇GBK不可编码字符退出1；后续明确PYTHONIOENCODING=utf-8，未改原件。'],
        'limitations': ['STA仍FAIL_TIMING；本PASS仅针对失败证据，不批准STA/runtime/物理接口/G3/G4/G5。',
                        'postroute/bit/cache/model/109/1000次/BOARD均NOT_RUN；物理0.1.1 NOT_FROZEN、visibility0。',
                        'Git输出真实码/SHA/bytes留存；固定Git对象和已有快照可恢复，不重复新建业务清单。',
                        'MCP客户端300s timeout与实际wait0/301.425s分开；执行9+history1另status1。',
                        'core159s/2200.098MB、max single ps7 2209.809MB、root累计2695.598MB分记；综合整树峰未知。',
                        'source首宿主序列化失败1未获得独立原始raw流；恢复文件和history95透明保留，未伪称逐字节恢复。']}
    save('receipt.json', receipt)
    print(json.dumps({'status': status, 'execution_state': 'STOP', 'groups': len(CHECKS),
                      'native_commands': len(NATIVE), 'elapsed_seconds': receipt['elapsed_seconds']}, ensure_ascii=False), flush=True)
    return 0 if status == 'PASS_EVIDENCE_INTEGRITY_ONLY' else 2


if __name__ == '__main__':
    raise SystemExit(main())
