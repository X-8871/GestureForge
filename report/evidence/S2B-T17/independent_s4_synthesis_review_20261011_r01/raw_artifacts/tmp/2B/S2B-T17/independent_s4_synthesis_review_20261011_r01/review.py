"""独立只读核查 S4 失败综合证据，所有新文件仅写入本隔离目录。"""
import copy
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
BASE = ROOT / 'report/evidence/S2B-T17/s4_platform_20261011_r01'
PRE = ROOT / 'report/evidence/S2B-T17/s4_source_preflight_20261011_r03'
COMMIT = 'f96d3e225fd6d92fd33c0407e20c9585c997c870'
EXPECTED_MANIFEST = 'cc638501782ed0bf95a63e97cf0128b91fcb629754095201d0feb4e26979a535'
START = time.monotonic()
CHECKS = []
NATIVE = []
DETAILS = {}


def require(ok, message):
    """每条断言都由真实原件独立计算。"""
    if not ok:
        raise AssertionError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def exact(path):
    """完整路径存在、无符号链接，且目标为普通文件。"""
    p = Path(path)
    require(p.is_file() and not p.is_symlink(), '文件目标类型错误：' + str(p))
    require(p.resolve().is_relative_to(ROOT), '目标超出项目：' + str(p))
    return p


def read(path):
    return json.loads(exact(path).read_text(encoding='utf-8'))


def save(path, value):
    """新目标禁止覆盖，文本统一 UTF-8。"""
    require(path.parent == OUT and not path.exists(), '独立输出目标已存在或越界')
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def binding(row, key='path'):
    """精确核对字节及 SHA，不接受换行归一化。"""
    p = exact(ROOT / row[key])
    raw = p.read_bytes()
    require(sha(raw) == row['sha256'], 'SHA 不符：' + str(p))
    if 'bytes' in row:
        require(len(raw) == row['bytes'], '字节数不符：' + str(p))
    return raw


def run_native(label, command, expected, retain_stdout=True):
    """真实原生退出码与宿主返回码分别保存。"""
    started = time.monotonic()
    proc = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}, timeout=60)
    record = {'label': label, 'command': command, 'native_exit_code': proc.returncode,
              'elapsed_seconds': time.monotonic() - started,
              'stdout_sha256': sha(proc.stdout), 'stdout_bytes': len(proc.stdout),
              'stderr_sha256': sha(proc.stderr), 'stderr_bytes': len(proc.stderr),
              'stderr_utf8': proc.stderr.decode('utf-8', errors='replace')}
    if retain_stdout:
        for suffix, raw in [('stdout.log', proc.stdout), ('stderr.log', proc.stderr)]:
            p = OUT / (label + '.' + suffix)
            require(not p.exists(), '原生输出目标已存在')
            p.write_bytes(raw)
        record['stdout_path'] = rel(OUT / (label + '.stdout.log'))
        record['stderr_path'] = rel(OUT / (label + '.stderr.log'))
    else:
        record['stdout_policy'] = 'Git blob 可由固定对象重建；真实输出哈希与字节数留存，未重复归档源码原字节。'
    NATIVE.append(record)
    require(proc.returncode == expected, '原生退出码不符：' + label + ':' + str(proc.returncode))
    return proc.stdout


def group(name, function):
    """单组失败保留异常，继续不依赖该结果的只读核查。"""
    started = time.monotonic()
    try:
        function()
        record = {'name': name, 'status': 'PASS', 'elapsed_seconds': time.monotonic() - started}
    except Exception as exc:
        record = {'name': name, 'status': 'CHANGES_REQUIRED', 'error': repr(exc),
                  'traceback': traceback.format_exc(), 'elapsed_seconds': time.monotonic() - started}
    CHECKS.append(record)
    print(json.dumps(record, ensure_ascii=False), flush=True)


def inventory_audit():
    manifest_path = BASE / 's4_collection_delivery_manifest_r02.json'
    require(sha(exact(manifest_path).read_bytes()) == EXPECTED_MANIFEST, '被审版本改变')
    manifest = read(manifest_path)
    require(manifest['source_commit'] == COMMIT and len(manifest['files']) == 276
            and len(manifest['interfaces']) == 2, '清单范围不符')
    require(len({r['path'] for r in manifest['files']}) == 276, '清单路径重复')
    for row in manifest['files'] + manifest['interfaces']:
        binding(row)
    main = {rel(p): {'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size}
            for p in BASE.rglob('*') if p.is_file()}
    require(len(main) == 187 and sum(r['bytes'] for r in main.values()) == 5983718, 'main 封存统计不符')
    listed = {r['path'] for r in manifest['files']}
    require(set(main) - {rel(manifest_path)} <= listed, 'main 原件未完整绑定')
    original = read(BASE / 's4_collection_original_inventory.json')
    require(original['file_count'] == len(original['files']) == 142, '原142数量错误')
    for row in original['files']:
        binding(row)
        require(row['path'] in listed, '原142遗漏')
    closed = read(BASE / 's4_collection_closed_inventory.json')
    require(closed['file_count'] == len(closed['files']) == 185, 'closed 数量错误')
    require(closed['total_bytes'] == sum(r['bytes'] for r in closed['files']) == 5865871, 'closed 字节统计错误')
    for row in closed['files']:
        binding(row)
    remaining = set(main) - {r['path'] for r in closed['files']}
    require(remaining == {rel(manifest_path), rel(BASE / 's4_collection_closed_inventory.json')}, '封存后出现未声明原件')
    rootlog = read(BASE / 's4_collection_root_session_snapshot.json')['snapshot']
    binding(rootlog)
    require(rootlog['sha256'] == '5d604023f62bf8d1474ac63f49bbf759ab81eb1fc09da6ba262e2b285b9c1863'
            and rootlog['bytes'] == 457507, '根会话封存不符')
    DETAILS['inventory'] = {'manifest_sha256': EXPECTED_MANIFEST, 'files': 276, 'interfaces': 2,
                            'original_raw_files': 142, 'main_files': 187, 'main_bytes': 5983718,
                            'closed_inventory_files': 185, 'closed_inventory_bytes': 5865871}
    for name, expected in [('s4_source_preflight_20261011_r01', 2), ('s4_source_preflight_20261011_r02', 2),
                           ('s4_source_preflight_20261011_r03', 83)]:
        paths = {rel(p) for p in (ROOT / 'report/evidence/S2B-T17' / name).rglob('*') if p.is_file()}
        require(len(paths) == expected and paths <= listed, 'preflight 原件范围缺失：' + name)


def source_audit():
    before, after = read(PRE / 'source_before.json'), read(PRE / 'source_after.json')
    source = read(BASE / 's4_collection_source_binding.json')
    freeze_path = ROOT / 'report/evidence/S2B-T17/conv_validation_20261011_r15/source_freeze.json'
    freeze = read(freeze_path)
    require(sha(freeze_path.read_bytes()) == 'd8f2af3f6ac243267c12d9a8ca1b8559b0ff1e69054492b4eab50dcdee62a846', '来源冻结 SHA 错误')
    require(len(source['sources']) == len(before['source_files']) == len(after['source_files']) == 37, '37闭包错误')
    by_before = {r['path']: r for r in before['source_files']}
    by_after = {r['path']: r for r in after['source_files']}
    require(set(by_before) == set(by_after) == set(freeze['source_sha256']), '闭包成员错误')
    require(before['platform_static_source_count'] == after['platform_static_source_count'] == 31, 'static 应为31')
    require(before['source_commit'] == after['source_commit'] == source['source_commit'] == COMMIT, '源码基线错误')
    counts = {'RAW_IDENTICAL': 0, 'GIT_LF_TO_RAW_CRLF': 0}
    source_results = []
    for i, row in enumerate(source['sources']):
        path = row['path']
        raw = exact(ROOT / row['snapshot']).read_bytes()
        later = exact(ROOT / row['snapshot_after']).read_bytes()
        require(raw == later and sha(raw) == row['sha256'] == by_before[path]['sha256']
                == by_after[path]['sha256'] == freeze['source_sha256'][path], '源快照不符：' + path)
        require(len(raw) == row['bytes'], '源码字节错误')
        blob = run_native('git_source_%02d' % i, ['git', 'show', COMMIT + ':' + path], 0, False)
        equal = blob == raw
        eol = not equal and b'\r' not in blob and blob.replace(b'\n', b'\r\n') == raw
        relation = 'RAW_IDENTICAL' if equal else 'GIT_LF_TO_RAW_CRLF'
        require(equal or eol, 'Git 关系超出精确LF到CRLF：' + path)
        require(row['git_relation'] == relation and row['git_blob_sha256'] == sha(blob)
                and row['git_raw_same'] == equal and row['exact_git_lf_to_snapshot_crlf'] == eol
                and row['live_source_consumed'] is False, '关系元数据错误：' + path)
        counts[relation] += 1
        source_results.append({'path': path, 'raw_sha256': sha(raw), 'git_blob_sha256': sha(blob), 'relation': relation})
    require(counts == {'RAW_IDENTICAL': 31, 'GIT_LF_TO_RAW_CRLF': 6}, 'EOL 分布错误')
    require(len(source['extra_test_oracle_sources']) == 6 and len(set(by_before) - set(source['extra_test_oracle_sources'])) == 31, '31+6闭包错误')
    originals = before['frozen14_sha256']
    require(len(originals) == 14 and originals == after['frozen14_sha256'] == source['frozen14_sha256'] == freeze['frozen14_sha256'], '原14冻结错误')
    for path, expected in originals.items():
        require(sha((PRE / 'source_snapshot' / path).read_bytes()) == expected, '原14字节变化')
    checker = BASE / 's4_collection_stage_checker_snapshot.py'
    blob = run_native('git_checker', ['git', 'show', COMMIT + ':verification/check_stage_delivery.py'], 0, False)
    require(blob == checker.read_bytes(), 'checker 不是固定Git原字节')
    g2 = ROOT / 'report/evidence/S2B-T17/independent_conv_validation_review_20261011_r01/delivery_manifest_r02.json'
    require(sha(exact(g2).read_bytes()) == '374ec84f9072298c415999808b54f5658e95cbf1fe8c0c9534049fb24d53f003', 'S4 G2来源哈希错误')
    DETAILS['sources'] = {'source_count': 37, 'static_count': 31, 'extra_count': 6,
                          'counts': counts, 'original14_unchanged': True, 'results': source_results,
                          'g2_scope': '仅核固定G2入口哈希，不重跑或继承综合/STA通过。'}


def native_audit():
    native = read(BASE / 's4_collection_native_mapping.json')
    require(len(native['files']) == native['native_raw_copy_count'] == 89 and len(native['jobs']) == 5, 'native范围错误')
    paths = set()
    for row in native['files']:
        raw = binding(row, 'saved_path')
        original = exact(Path(row['original_path']))
        require(original.read_bytes() == raw, 'native RAW 复制不符：' + row['saved_path'])
        require(Path(row['saved_path']).suffix.lower() not in ['.dcp', '.vds', '.pb', '.wdf'], '混入缓存')
        paths.add(row['saved_path'])
    require(len(paths) == 89, 'native映射重复')
    results = []
    for job in native['jobs']:
        directory = ROOT / job['saved_directory']
        require(directory.is_dir() and (directory / '.vivado.end.rst').is_file()
                and (directory / '__synthesis_is_complete__').is_file()
                and not (directory / '.vivado.error.rst').exists(), '完成marker错误')
        log = (directory / 'runme.log').read_text(encoding='utf-8')
        begin = ET.fromstring((directory / '.vivado.begin.rst').read_bytes()).find('Process')
        pid = int(re.search(r'Process ID\s*:\s*(\d+)', log)[1])
        peak = max(map(float, re.findall(r'peak = ([0-9.]+)', log)))
        hours, minutes, seconds = map(int, re.search(r'synth_design: Time \(s\):.*?elapsed = (\d+):(\d+):(\d+)', log)[1:])
        diag = list(map(int, re.findall(r'(\d+) Infos, (\d+) Warnings, (\d+) Critical Warnings and (\d+) Errors encountered\.', log)[-1]))
        require(pid == job['actual_vivado_job_pid'] and int(begin.attrib['Pid']) == job['launcher_pid_from_begin_rst'], 'PID误绑')
        require(peak == job['reported_single_process_peak_mb'] and hours * 3600 + minutes * 60 + seconds == job['synth_design_elapsed_seconds'], '耗时/峰不符')
        require(dict(zip(['infos', 'warnings', 'critical_warnings', 'errors'], diag)) == job['final_diagnostics'], '诊断统计错误')
        require(job['raw_os_process_exit_code'] is None and diag[2:] == [0, 0], '伪填OS退出码或真实综合失败')
        require(job['session_start_local'] in log and job['session_end_local'] in log, '原生起止时间错误')
        results.append({'run': job['run'], 'vivado_pid': pid, 'launcher_pid': int(begin.attrib['Pid']),
                        'seconds': job['synth_design_elapsed_seconds'], 'single_process_peak_mb': peak, 'diagnostics': diag})
    tcl = (BASE / 'native_jobs/s2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl').read_text(encoding='utf-8')
    block = re.search(r'read_verilog -library xil_defaultlib -sv \{(.*?)\}', tcl, re.S)[1]
    compiled = [rel(Path(p.strip())) for p in block.splitlines() if p.strip()]
    profile = read(PRE / 'source_snapshot/board/s2b_inference_platform.json')
    require(len(compiled) == len(set(compiled)) == 18 and set(compiled) == set(profile['rtl_sources'])
            == set(native['actual_compiled_rtl_sources']), '原生编译18闭包错误')
    source = {r['path']: r for r in read(BASE / 's4_collection_source_binding.json')['sources']}
    for row in native['actual_compiled_source_snapshots']:
        require(row['source_identifier'] in compiled and row['sha256'] == source[row['source_identifier']]['sha256'], '编译快照映射错误')
    wrapper = binding(native['wrapper_import'], 'saved_path')
    require(sha(wrapper) == 'fa9606be49793076ccf93e3f784dc61e1476811f539a011a82dbca45cf49a6d1'
            and len(wrapper) == 2637, 'wrapper原件错误')
    generated = binding(native['wrapper_generated_original'])
    require(wrapper == generated, 'import/generated wrapper不相同')
    wrapper_tcl = (BASE / 'native_jobs/wrapper_native_s4_r01/s2b_inference_wrapper.tcl').read_text(encoding='utf-8')
    require(wrapper_tcl.count('imports/hdl/s2b_inference_wrapper.v') == 1, '实际wrapper不唯一')
    require(profile['visibility_default'] == 0 and profile['clock_hz'] == 50000000
            and profile['vivado_part'] == 'xc7z020clg400-2', 'profile范围错误')
    DETAILS['native_jobs'] = results
    DETAILS['compiled'] = {'count': 18, 'wrapper_count': 1, 'visibility': 0,
                           'clock_hz': 50000000, 'part': 'xc7z020clg400-2'}


def mcp_audit():
    raw = read(PRE / 'root_mcp_calls_with_history.json')
    history = json.loads(raw['history']['content'][0]['text'])['history']
    require(len(raw['calls']) == 9 and len(history) == 15, 'MCP记录口径错误')
    by_id = {r['id']: r for r in history}
    require(set(by_id) == set(range(80, 95)), 'native history不完整')
    pairs = read(BASE / 's4_collection_mcp_history_binding.json')['paired_calls']
    require(len(pairs) == 9, '闭合配对不全')
    for i, call in enumerate(raw['calls'], 86):
        result = json.loads(call['result']['content'][0]['text'])
        require(call['command'] == by_id[i]['command'] and result['exit_code'] == by_id[i]['code'], 'MCP与native不符')
        require(pairs[i - 86]['native_history'] == by_id[i] and pairs[i - 86]['client_result'] == call['result'], '配对封存不同')
    require((by_id[87]['code'], by_id[87]['elapsed'], by_id[90]['code'], by_id[90]['elapsed'],
             by_id[92]['code'], by_id[92]['elapsed'], by_id[94]['code']) == (1, 24.06, 0, 271.383, 0, 29.896, 0), '关键退出码/耗时错误')
    require(by_id[94]['command'] == 'close_project' and by_id[94]['output'] == '', '未关闭项目')
    require('source_count 18 wrapper_count 1' in by_id[88]['output']
            and 'part xc7z020clg400-2 visibility 0' in by_id[88]['output'], '实际源查询错误')
    require(by_id[93]['output'].count('status {Not started} progress 0%') == 5, '实现已启动或状态缺失')
    require('17:22:06 2026' in by_id[89]['output'] and '17:28:21 2026' in by_id[90]['output'], '启动/完成时间错误')
    products = (BASE / 'products.tcldict').read_text(encoding='utf-8')
    for token in ['status FAIL code 0 raw PRODUCTS:OK', 'WARNING emitted=-8 exported=2',
                  'native_counts_before {WARNING 9', 'native_counts_after {WARNING 1']:
        require(token in products, 'products原FAIL元数据缺失')
    DETAILS['mcp'] = {'execute_calls': 9, 'history_query_calls': 1, 'total_including_history_query': 10,
                      'native_history_entries': 15, 's4_native_history_ids': list(range(86, 95)),
                      'mcp_wait_timeout': False, 'wait_native_exit_code': 0,
                      'wait_elapsed_seconds': 271.383, 'launch_to_finish_seconds': 375,
                      'builder_native_exit_code': 1, 'builder_seconds': 24.06,
                      'products_native_exit_code': 0, 'products_capture_exit_code': 1,
                      'implementation_started': False, 'root_cumulative_peak_mb': 2691.660,
                      'root_cumulative_peak_is_s4_peak': False, 'process_tree_peak_memory_bytes': None}


def parse_timing(text):
    """按独立区段解析汇总，拒绝重复/状态/时钟与文字矛盾。"""
    require(re.findall(r'^\| Design State\s*:\s*(.+)$', text, re.M) == ['Synthesized'], '不是综合态')
    section = text.split('| Design Timing Summary', 1)[1].split('| Clock Summary', 1)[0]
    rows = [l.split() for l in section.splitlines()
            if re.fullmatch(r'\s*-?\d+\.\d+(?:\s+-?\d+(?:\.\d+)?){11}\s*', l)]
    require(len(rows) == 1, 'timing汇总不唯一')
    names = ['wns_ns', 'tns_ns', 'setup_failing_endpoints', 'setup_total_endpoints', 'whs_ns', 'ths_ns',
             'hold_failing_endpoints', 'hold_total_endpoints', 'wpws_ns', 'tpws_ns', 'pulse_failing_endpoints', 'pulse_total_endpoints']
    values = {k: float(v) if k.endswith('_ns') else int(v) for k, v in zip(names, rows[0])}
    require(re.findall(r'^clk_fpga_0\s+\{[\d.]+\s+[\d.]+\}\s+([\d.]+)\s+([\d.]+)\s*$', text, re.M) == [('20.000', '50.000')], '时钟错误')
    require('Timing constraints are not met.' in text and values['wns_ns'] < 0
            and values['setup_failing_endpoints'] > 0, '时序文字/数值矛盾')
    return values


def reports_audit():
    timing_text = (BASE / 'timing_summary_synth.rpt').read_text(encoding='utf-8')
    timing = parse_timing(timing_text)
    summary = read(BASE / 's4_collection_summary_final.json')
    require(timing == summary['timing'] == read(BASE / 's4_collection_sta_result.json')['timing'], 'STA汇总不同')
    require((timing['wns_ns'], timing['tns_ns'], timing['setup_failing_endpoints'], timing['setup_total_endpoints'],
             timing['whs_ns'], timing['ths_ns'], timing['wpws_ns'], timing['tpws_ns'])
            == (-21.981, -5506.339, 759, 14655, 0.037, 0, 8.870, 0), 'STA关键原数值不同')
    for name, value in summary['check_timing'].items():
        counts = set(re.findall(r'checking ' + name + r' \((\d+)\)', timing_text))
        require(counts == {'0'} and value == 0, 'check_timing计数不同')
    worst = (BASE / 'timing_worst_synth.rpt').read_text(encoding='utf-8')
    def first(pattern):
        return re.search(pattern, worst, re.M)[1]
    values = {'source': first(r'^\s*Source:\s*(\S+)'), 'destination': first(r'^\s*Destination:\s*(\S+)'),
              'logic_levels': int(first(r'^\s*Logic Levels:\s*(\d+)')),
              'carry4': int(first(r'^\s*Logic Levels:.*?CARRY4=(\d+)')),
              'dsp48e1': int(first(r'^\s*Logic Levels:.*?DSP48E1=(\d+)')),
              'data_path_delay_ns': float(first(r'^\s*Data Path Delay:\s*([\d.]+)ns')),
              'logic_delay_ns': float(first(r'^\s*Data Path Delay:.*?logic ([\d.]+)ns')),
              'route_delay_ns': float(first(r'^\s*Data Path Delay:.*?route ([\d.]+)ns'))}
    require(values == {k: v for k, v in summary['worst_path'].items() if k != 'reported_logic_resource'}, '最坏路径原值不同')
    require('full_tile_patch_bytes_wide3' in worst, '宽校验路径资源缺失')
    conv = (PRE / 'source_snapshot/src/s2b_conv_tile_engine.sv').read_text(encoding='utf-8')
    require('full_tile_patch_bytes_wide' in conv and 'output_width_latched' in conv
            and 'result_error_latched' in conv, '路径与固定源未对应')
    util = (BASE / 'utilization_flat_synth.rpt').read_text(encoding='utf-8')
    resource_rows = [('lut', 'Slice LUTs*'), ('ff', 'Slice Registers'), ('bram', 'Block RAM Tile'),
                     ('dsp', 'DSPs'), ('latch', 'Register as Latch')]
    resources = {key: int(re.search(r'^\|\s*' + re.escape(label) + r'\s*\|\s*(\d+)\s*\|', util, re.M)[1])
                 for key, label in resource_rows}
    require(resources == summary['resources'] == {'lut': 29904, 'ff': 4006, 'bram': 32, 'dsp': 166, 'latch': 0}, '资源不同')
    xdc = (BASE / 'constraints_synth.xdc').read_text(encoding='utf-8')
    falsepaths = re.findall(r'^current_instance ([^\n]+)\n(set_false_path[^\n]+)', xdc, re.M)
    constraints = read(BASE / 's4_collection_constraints_binding.json')
    require([{'scope': a, 'command': b} for a, b in falsepaths] == constraints['exported_reset_cdc_false_paths']
            and len(falsepaths) == 2 and xdc.count('set_false_path') == 2, '两scoped reset例外未准确保存')
    require('create_clock -period 20.000 -name clk_fpga_0' in xdc and 'set_input_jitter clk_fpga_0 0.600' in xdc, '时钟原约束不同')
    require('No valid timing exceptions found.' in (BASE / 'exceptions_synth.rpt').read_text(encoding='utf-8'), 'exceptions原文字缺失')
    for name in ['timing_summary_synth.rpt', 'timing_worst_synth.rpt', 'utilization_flat_synth.rpt',
                 'utilization_synth.rpt', 'clocks_synth.rpt', 'exceptions_synth.rpt', 'methodology_synth.rpt', 'drc_synth.rpt']:
        text = (BASE / name).read_text(encoding='utf-8')
        require('Vivado v.2026.1' in text and 'Design State : Synthesized' in text, '报告版本/状态错误：' + name)
    DETAILS['reports'] = {'status': 'FAIL_TIMING', 'timing': timing, 'resources': resources, 'worst_path': values,
                          'exported_scoped_reset_false_paths': falsepaths, 'check_timing_all_zero': True,
                          'exception_report_statement': 'No valid timing exceptions found.'}


def xsa_audit():
    comp = read(BASE / 's4_collection_xsa_member_comparison.json')
    for row in [comp['old_xsa'], comp['new_xsa']]:
        binding(row)
    with zipfile.ZipFile(ROOT / comp['old_xsa']['path']) as old, zipfile.ZipFile(ROOT / comp['new_xsa']['path']) as new:
        require(set(old.namelist()) == set(new.namelist()), 'XSA成员集合改变')
        require(not any(n.lower().endswith('.bit') for n in new.namelist()), 'XSA含bit')
        for row in comp['members']:
            a, b = old.read(row['member']), new.read(row['member'])
            require(sha(a) == row['old_sha256'] and sha(b) == row['new_sha256']
                    and len(a) == row['old_bytes'] and len(b) == row['new_bytes']
                    and (a == b) == row['raw_equal'], 'XSA成员原字节不符')
            require(old.getinfo(row['member']).CRC == row['old_crc32'] and new.getinfo(row['member']).CRC == row['new_crc32'], '成员CRC不符')
        require(sum(r['raw_equal'] for r in comp['members']) == 6 and len(comp['members']) == 7
                and comp['members'][-1]['member'] == 's2b_inference.hwh' and not comp['members'][-1]['raw_equal'], 'PS/HWH范围错误')
    DETAILS['xsa'] = {'psinit_equal_members': 6, 'hwh_equal': False, 'contains_bit': False,
                      'compatibility_approval': False, 'runtime_approval': False}


def failure_audit():
    r01 = read(ROOT / 'report/evidence/S2B-T17/s4_source_preflight_20261011_r01/failed_root_preflight.json')
    r02 = read(ROOT / 'report/evidence/S2B-T17/s4_source_preflight_20261011_r02/failed_root_preflight_and_correction.json')
    require(r01['actual_static_source_count'] == 34 and r02['actual_static_source_count'] == 31
            and r02['actual_frozen_source_count'] == 37 and '误写' in r02['first_record_correction'], '原错误与纠正丢失')
    require(r01['expected_count_in_initial_root_driver'] == 33 and r02['expected_count_in_second_root_driver'] == 34
            and r01['exec_command_exit_code'] == r02['exec_command_exit_code'] == 1, '前置失败元数据改变')
    require(not r01['inner_exit_code_separately_measured'] and not r02['inner_exit_code_separately_measured'], '伪造inner退出码')
    expected = {'s4_collection_collector': 1, 's4_collection_recovery_r02': 0, 's4_collection_final': 0,
                's4_collection_evidence_r01': 0, 's4_collection_inputs_r01': 2, 's4_collection_sta': 2}
    actual = {}
    for stem, value in expected.items():
        record = read(BASE / (stem + '.native.json'))
        require(record['native_exit_code'] == value, '历史原生退出码改变：' + stem)
        actual[stem] = value
        for row in record['closed_logs']:
            archived = BASE / Path(row['path']).name
            require(archived.is_file() and sha(archived.read_bytes()) == row['sha256']
                    and archived.stat().st_size == row['bytes'], '历史stdout/stderr原件遗漏：' + stem)
    require('s2b_inference_infer_0.v' in read(BASE / 's4_collection_failure_r01.json')['error'], '初轮精确扩展名失败丢失')
    original = (BASE / 's4_collection_collect_s4_synthesis.py').read_text(encoding='utf-8')
    recovery = (BASE / 's4_collection_seal_collection_r02.py').read_text(encoding='utf-8')
    require('s2b_inference_infer_0.v' in original and 's2b_inference_infer_0.sv' in recovery, '初轮脚本被覆盖或新脚本未修正')
    DETAILS['preserved_failures'] = {'actual_static_count': 31, 'frozen_count': 37,
                                   'r01_wrong_claim_34_superseded': True, 'native_codes': actual,
                                   'r03_native_receipt_limitation': '前后0来自总控执行事实；原r03未独立保存native进程receipt。'}


def checker_audit():
    checker = str(BASE / 's4_collection_stage_checker_snapshot.py')
    manifest = str(BASE / 's4_collection_delivery_manifest_r02.json')
    for mode, code in [('evidence', 0), ('inputs', 2)]:
        stdout = run_native('checker_' + mode, [sys.executable, '-B', '-X', 'utf8', checker, '--mode', mode,
                                                '--manifest', manifest, '--project-root', str(ROOT)], code)
        require(('CHECKS_OK' in stdout.decode('utf-8')) == (mode == 'evidence'), '包装/inputs状态混淆')
    run_native('classifier_original', [sys.executable, '-B', '-X', 'utf8',
               str(BASE / 's4_collection_classify_s4_sta.py'), '--report', str(BASE / 'timing_summary_synth.rpt'),
               '--result', str(OUT / 'classifier_original_result.json')], 2)
    DETAILS['independent_native'] = {'evidence': 0, 'inputs': 2, 'classifier': 2,
                                    'checker_source': '固定f96 Git原字节快照；未运行live平台checker。'}


def counterexamples():
    """独立元数据反例在内存验证；不改原件，不复制大报告。"""
    cases = []
    def reject(name, function):
        try:
            function()
        except (AssertionError, ValueError, IndexError, KeyError) as exc:
            cases.append({'name': name, 'status': 'EXPECTED_REJECTION', 'exception': repr(exc)})
        else:
            raise AssertionError('反例未拒绝：' + name)
    item = copy.deepcopy(read(BASE / 's4_collection_delivery_manifest_r02.json')['files'][0])
    item['sha256'] = '0' * 64
    reject('SHA篡改', lambda: binding(item))
    item2 = copy.deepcopy(read(BASE / 's4_collection_original_inventory.json')['files'][0])
    item2['bytes'] += 1
    reject('字节计数篡改', lambda: binding(item2))
    item3 = copy.deepcopy(read(BASE / 's4_collection_delivery_manifest_r02.json')['files'][0])
    item3['path'] += '.不存在'
    reject('精确路径不存在', lambda: binding(item3))
    text = (BASE / 'timing_summary_synth.rpt').read_text(encoding='utf-8')
    reject('综合状态伪改实现态', lambda: parse_timing(text.replace('Design State : Synthesized', 'Design State : Routed')))
    reject('时序文字伪改通过', lambda: parse_timing(text.replace('Timing constraints are not met.', 'Timing constraints are met.')))
    reject('50MHz伪改25MHz', lambda: parse_timing(text.replace('20.000', '40.000')))
    reject('summary区缺失', lambda: parse_timing(text.replace('| Design Timing Summary', '| Missing Timing Summary')))
    row = next(l for l in text.split('| Design Timing Summary', 1)[1].split('| Clock Summary', 1)[0].splitlines()
               if re.fullmatch(r'\s*-?\d+\.\d+(?:\s+-?\d+(?:\.\d+)?){11}\s*', l))
    reject('summary重复数据行', lambda: parse_timing(text.replace(row, row + '\n' + row)))
    raw = (PRE / 'source_snapshot/src/s2b_conv_tile_engine.sv').read_bytes()
    reject('源码单字节篡改', lambda: require(sha(raw + b'\n') == sha(raw), '源码RAW发生变化'))
    DETAILS['counterexamples'] = cases


def main():
    """各核查组完成后封存独审receipt，失败返回2。"""
    require(ROOT == Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition'), 'ROOT完整精确路径错误')
    for name, function in [('276绑定及142原件/封存inventory', inventory_audit), ('37源码/Git精确EOL/原14/G2入口', source_audit),
                           ('89native映射/五job/PID/18闭包/wrapper', native_audit), ('MCP封闭出入口及原失败', mcp_audit),
                           ('实际STA/资源/路径/约束/报告版本', reports_audit), ('PSinit六成员及HWH/no-bit', xsa_audit),
                           ('计数/collector历史失败与原生码', failure_audit), ('固定checker及classifier原生确认', checker_audit),
                           ('独立轻量元数据反例', counterexamples)]:
        group(name, function)
    decision = 'PASS_EVIDENCE_INTEGRITY_ONLY' if all(r['status'] == 'PASS' for r in CHECKS) else 'CHANGES_REQUIRED'
    save(OUT / 'native_commands.json', {'commands': NATIVE, 'count': len(NATIVE), 'peak_memory_bytes': None,
                                       'peak_reason': '轻量独审未测内存峰；不借用Vivado峰值。'})
    receipt = {'schema_version': 1, 'status': decision, 'reviewed_source_commit': COMMIT,
               'reviewed_manifest': rel(BASE / 's4_collection_delivery_manifest_r02.json'),
               'reviewed_manifest_sha256': EXPECTED_MANIFEST, 'created_at_utc8': datetime.now(timezone(timedelta(hours=8))).isoformat(),
               'checks': CHECKS, 'details': DETAILS, 'native_command_count': len(NATIVE),
               'elapsed_seconds': time.monotonic() - START, 'peak_memory_bytes': None,
               'modification_scope': rel(OUT), 'project_code_modified': False,
               'limitations': ['仅批准S4失败证据准确性/完整性；STA仍FAIL_TIMING，未批准runtime/cache/模型/物理G0/G3/G4/G5。',
                               '没有重新综合、仿真、实现、生成bit或操作硬件/ROSS/SDK/串口。',
                               '当前S5 live源码不消费；没有运行当前live平台checker或继承S3 timeout。',
                               '源Git输出只记录真实SHA/bytes/native码；原字节已有固定Git和已绑定快照，可重建。',
                               'MCP封存9个execute+1个history查询；15个native history含6个历史S3条目，S4仅86至94。',
                               '完整进程树/本独审内存峰未测；核心183s/2240.094MB与root累计2691.660MB分别解释。']}
    save(OUT / 'receipt.json', receipt)
    print(json.dumps({'status': decision, 'groups': len(CHECKS), 'native_command_count': len(NATIVE),
                      'elapsed_seconds': receipt['elapsed_seconds']}, ensure_ascii=False), flush=True)
    return 0 if decision == 'PASS_EVIDENCE_INTEGRITY_ONLY' else 2


if __name__ == '__main__':
    raise SystemExit(main())
