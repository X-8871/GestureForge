"""独立只读核查 S6 已关闭的失败综合证据；仅本目录可写。"""
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
BASE = ROOT / 'report/evidence/S2B-T17/s6_platform_20261011_r01'
PRE = ROOT / 'report/evidence/S2B-T17/s6_source_preflight_20261011_r01'
CACHE = ROOT / 'tmp/2B/S2B-T17/s6_collection_20261011_r01'
COMMIT = 'b0dbf0dcde758e15046cda36bf2c7424f179b5ae'
MANIFEST_SHA = 'c898be1d13a5f2beed3bfcacd3f2f18cb0c4220ef38bbf747d3ce80e5952ce13'
FINAL_SHA = 'a3abd4fc820c5cc418bbd74b8684e4a7f2147f6a88cfda6526c77331ec70f6b0'
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
    manifest = read(BASE / 's6_collection_delivery_manifest_r02.json')
    require(sha((BASE / 's6_collection_delivery_manifest_r02.json').read_bytes()) == MANIFEST_SHA, 'manifest变化')
    require(manifest['source_commit'] == COMMIT and len(manifest['files']) == 315 and len(manifest['interfaces']) == 2, '清单基线/范围错误')
    listed = {r['path'] for r in manifest['files']}
    require(len(listed) == 315 and rel(BASE / 's6_collection_delivery_manifest_r02.json') not in listed, '重复或自引用')
    for row in manifest['files']:
        require(set(row) == {'path','sha256','role'} and row['role'] in {'source','input','result','log','diagnostic','artifact'}, '格式/角色错误')
        require(not any(p in {'.cache','.runs','.gen','obj_dir','SDK','sdk'} for p in Path(row['path']).parts)
                and Path(row['path']).suffix.lower() not in {'.exe','.dcp','.pb','.wdf'}, '业务清单混入缓存')
        binding(row)
    for row in manifest['interfaces']:
        binding(row)
    require(manifest['interfaces'][0]['frozen'] is True and manifest['interfaces'][1]['frozen'] is False
            and manifest['interfaces'][1]['version'] == 's2b-physical-candidate/0.1.1', '物理候选伪冻结')
    main = {rel(p): {'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in BASE.rglob('*') if p.is_file()}
    require(len(main)==234 and sum(r['bytes'] for r in main.values())==7311772, 'formal封存统计不同')
    require(set(main)-{rel(BASE/'s6_collection_delivery_manifest_r02.json')} <= listed, 'formal未完整绑定')
    original = read(BASE/'s6_collection_original_inventory.json')
    require(original['file_count']==len(original['files'])==55 and original['total_bytes']==2566278, '初始55统计不同')
    for row in original['files']:
        binding(row)
        require(row['path'] in listed, '原件遗漏')
    closed=read(BASE/'s6_collection_closed_inventory.json')
    require(closed['file_count']==len(closed['files'])==232 and closed['total_bytes']==sum(r['bytes'] for r in closed['files'])==7175790,'closed统计不同')
    for row in closed['files']:
        binding(row)
    require(set(main)-{r['path'] for r in closed['files']}=={rel(BASE/'s6_collection_closed_inventory.json'),rel(BASE/'s6_collection_delivery_manifest_r02.json')}, '封存后未声明原件')
    rootlog=read(BASE/'s6_collection_root_log_binding.json')
    raw=binding(rootlog['snapshot'])
    require(sha(raw)=='5c27e90921ee6dd1670959f0b0dabdad64992efc0f1b06da4e2273a448f1ce23' and len(raw)==65467 and rootlog['active_log_consumed'] is False,'root原字节错误')
    try:
        raw.decode('utf-8')
    except UnicodeDecodeError:
        decodable=False
    else:
        decodable=True
    require(decodable is False and rootlog['raw_utf8_decodable'] is False and rootlog['raw_bytes_preserved'] is True,'错误声称root UTF8可解码')
    peaks=list(map(float,re.findall(rb'peak = ([0-9.]+)',raw)))
    require(max(peaks)==rootlog['root_session_cumulative_peak_mb']==2056.789,'ASCII峰值不同')
    DETAILS['inventory']={'bindings':315,'formal_files':234,'formal_bytes':7311772,'initial_files':55,
        'native_root_raw_utf8_decodable':False,'root_snapshot_sha256':sha(raw),'root_snapshot_bytes':len(raw),
        'root_cumulative_peak_mb':2056.789,'root_peak_is_process_tree_peak':False,'cache_or_selfreference':False}

def source_audit():
    source = read(BASE / 's6_collection_source_binding.json')
    before, after = read(PRE / 'source_before.json'), read(PRE / 'source_after.json')
    for field, expected in [('source_before', '1031972cab9e1ae69405923ed5b2cf50e887297841a588742b91ef5ab046d09a'),
                            ('source_after', 'f9af1b301a95ff1072da244ed3c67de3786c9576c33d41ae72255aeb11f6b4fb'),
                            ('static_actual', '3f2f5d1724a025578c52f15433d6c53fac16fdf4057508b00d7295ce77ff6974')]:
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
    require(checker == (BASE / 's6_collection_stage_checker_snapshot.py').read_bytes(), 'checker不是固定GitRAW')
    g2 = exact(ROOT / 'report/evidence/S2B-T17/independent_length_guard_review_20261011_r02/delivery_manifest_r02.json')
    require(sha(g2.read_bytes()) == 'ffd8661888e2d076bb9ca72cd942594cd09987fd88dddd410eafbb5c75bffe85', 'S6等价G2入口不同')
    DETAILS['sources'] = {'source_count': 38, 'static_count': 31, 'extra_count': 7, 'counts': counts,
                          'original14_unchanged': True, 'results': results,
                          'freeze_old_metadata_preserved': True, 'live_s6_consumed': False,
                          'g2_scope': '仅核既有等价G2入口哈希；不继承STA通过。'}


def native_audit():
    native = read(BASE / 's6_collection_native_mapping.json')
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
    require(vds == 5 and sum(r['bytes'] for r in native['files']) == 1190306, '五文本VDS或native字节统计不同')
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
    source = {r['path']: r for r in read(BASE / 's6_collection_source_binding.json')['sources']}
    require(len(native['actual_compiled_source_snapshots']) == 18, '编译快照不全')
    for row in native['actual_compiled_source_snapshots']:
        require(row['source_identifier'] in compiled and row['sha256'] == source[row['source_identifier']]['sha256'],
                '编译源码快照不符')
        require(sha(exact(ROOT / row['source_snapshot']).read_bytes()) == row['sha256'], '编译snapshotRAW错误')
    wrapper = binding(native['wrapper_import'])
    require(wrapper == binding(native['wrapper_generated_original'])
            == (BASE / 'generated_inputs/s2b_inference_wrapper.v').read_bytes()
            and len(wrapper) == 2637, 'wrapper复制错误')
    wrapper_tcl = (BASE / 'native_jobs/wrapper_native_s6_r01/s2b_inference_wrapper.tcl').read_text(encoding='utf-8')
    require(wrapper_tcl.count('imports/hdl/s2b_inference_wrapper.v') == 1
            and native['unique_registered_wrapper_count_from_setup'] == 1, 'wrapper注册不唯一')
    require(profile['version'] == 's2b-inference-platform/0.1.6' and profile['visibility_default'] == 0
            and profile['clock_hz'] == 50000000 and profile['vivado_part'] == 'xc7z020clg400-2', 'profile错误')
    require(max(r['single_process_peak_mb'] for r in results) == 2210.242, '单job最大峰不同')
    infer = next(r for r in results if r['run'] == 's2b_inference_infer_0_synth_1')
    require((infer['synth_seconds'], infer['single_process_peak_mb']) == (164, 2175.812), '核心统计不同')
    DETAILS['native_jobs'] = results
    DETAILS['compiled'] = {'count': 18, 'wrapper_count': 1, 'vds_text_count': vds, 'clock_hz': 50000000,
                           'part': 'xc7z020clg400-2', 'visibility': 0, 'profile': profile['version']}


def mcp_audit():
    metadata=read(BASE/'s6_collection_mcp_history_binding.json')
    history=json.loads(read(BASE/'mcp_closed/mcp_history.json')['content'][0]['text'])['history']
    require(len(history)==9 and {r['id'] for r in history}==set(range(1,10)),'history1至9错误')
    pairs=metadata['paired_calls']
    require(len(pairs)==9,'client配对数量不同')
    for native,pair in zip(history,pairs):
        require(native==pair['native_history'],'history配对不同')
        client=json.loads(binding(pair['client_record']))
        if pair['label'] in {'source','builder'}:
            require(pair['saved_client_schema']=='RAW_CALL_TOOL_RESULT' and pair['client_input_captured'] is False
                    and 'input' not in client and pair['client_wall_ms'] is None,'伪造source/builder client输入')
            result=client
        else:
            require(client['input']['command']==native['command'] and client['wall_ms']==pair['client_wall_ms'],'client命令/耗时不同')
            result=client['result']
        if pair['label']=='wait':
            require(result['isError'] is True and 'after 300s' in result['content'][0]['text'],'timeout丢失')
        else:
            require(json.loads(result['content'][0]['text'])['exit_code']==native['code'],'client/native码不同')
    by={r['id']:r for r in history}
    require((by[1]['code'],by[2]['code'],by[2]['elapsed'],by[5]['code'],by[5]['elapsed'],
             by[7]['code'],by[7]['elapsed'],by[9]['code'])==(0,1,35.823,0,301.363,0,20.3,0),'关键native码/耗时不同')
    require(by[9]['command']=='close_project' and by[9]['output']=='','项目未关闭')
    require(by[8]['output'].count('status {synth_design Complete!} progress 100%')==5
            and by[8]['output'].count('status {Not started} progress 0%')==5,'实际synth/impl状态不同')
    require('19:31:44 2026' in by[4]['output'] and '19:37:26 2026' in by[5]['output']
            and '19:37:30 2026' in by[5]['output'],'实际起止时间不同')
    status=json.loads(read(BASE/'mcp_closed/mcp_status_after_wait.json')['content'][0]['text'])
    require(status['command_running'] is False and status['status_reliable'] is True,'post-timeout状态不可靠')
    runs=status['runs']
    require(sum(r['type']=='synth' and r['progress']=='100%' and r['status']=='synth_design Complete!' for r in runs)==5
            and sum(r['type']=='impl' and r['progress']=='0%' and r['status']=='Not started' for r in runs)==5,'post-timeout状态与history不同')
    products=(BASE/'products.tcldict').read_text(encoding='utf-8')
    for token in ['status FAIL code 0 raw PRODUCTS:OK','WARNING emitted=-8 exported=2',
                  'native_counts_before {WARNING 9','native_counts_after {WARNING 1']:
        require(token in products,'products失败原件缺失')
    require(metadata['implementation_started'] is False and metadata['products_repeated'] is False
            and metadata['execute_plus_history_calls']==10 and metadata['post_timeout_status_queries']==1
            and metadata['root_peak_is_run_process_tree_peak'] is False,'MCP统计外推错误')
    launch=datetime.fromisoformat(metadata['launch_timestamp_local'])
    wrapper=datetime.fromisoformat(metadata['native_wrapper_exit_local'])
    finished=datetime.fromisoformat(metadata['launcher_finished_local'])
    require((wrapper-launch).total_seconds()==metadata['launch_to_native_wrapper_exit_seconds']==342
            and (finished-launch).total_seconds()==metadata['launch_to_launcher_finished_seconds']==346,'elapsed映射不同')
    lifecycle=read(BASE/'s6_collection_owned_session_lifecycle.json')
    require(lifecycle['project_close_native_history']==by[9] and lifecycle['stop_native_os_exit_code'] is None
            and lifecycle['post_stop_process_absence_raw_captured_in_this_package'] is False,'session关闭/未测字段错误')
    binding(lifecycle['stop_result'])
    DETAILS['mcp']={k:metadata[k] for k in ['mcp_execute_calls','mcp_history_calls','execute_plus_history_calls',
        'post_timeout_status_queries','client_wait_is_error','client_wait_timeout_seconds','client_wait_wall_ms',
        'native_wait_exit_code','native_wait_elapsed_seconds','launch_to_native_wrapper_exit_seconds',
        'launch_to_launcher_finished_seconds','whole_builder_native_exit_code','products_native_exit_code',
        'products_capture_exit_code','root_session_cumulative_peak_mb','implementation_started']}
    DETAILS['mcp']['source_builder_inputs_captured']=False

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
    summary = read(BASE / 's6_collection_summary_final.json')
    require(timing == summary['timing'] == read(BASE / 's6_collection_sta_result.json')['timing'], 'STA原值与分类不同')
    require((timing['wns_ns'], timing['tns_ns'], timing['setup_failing_endpoints'], timing['setup_total_endpoints'],
            timing['whs_ns'], timing['ths_ns'], timing['wpws_ns'], timing['tpws_ns']) ==
            (-11.799, -3819.396, 736, 14767, 0.037, 0, 8.870, 0), 'STA关键值不同')
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
    require(values == summary['worst_path'] and values['logic_levels'] == 38 and values['carry4'] == 20
            and values['dsp48e1'] == 3 and values['data_path_delay_ns'] == 31.187, '最差路径原值不同')
    require(values['source'].endswith('/source0_end_latched_reg[6]/C') and values['destination'].endswith('/output_address_latched_reg[0]/CE'),
            'ROUTE路径端点不同')
    conv = (PRE / 'source_snapshot/src/s2b_route_engine.sv').read_text(encoding='utf-8')
    require('source0_end_latched' in conv and 'output_address_latched' in conv, '报告与固定ROUTE源码不对应')
    util = (BASE / 'utilization_flat_synth.rpt').read_text(encoding='utf-8')
    resource_rows = [('lut', 'Slice LUTs*'), ('ff', 'Slice Registers'), ('bram', 'Block RAM Tile'), ('dsp', 'DSPs'), ('latch', 'Register as Latch')]
    resources = {key: int(re.search(r'^\|\s*' + re.escape(label) + r'\s*\|\s*(\d+)\s*\|', util, re.M)[1]) for key, label in resource_rows}
    require(resources == summary['resources'] == {'lut': 20078, 'ff': 3973, 'bram': 32, 'dsp': 145, 'latch': 0}, '资源统计不同')
    xdc = (BASE / 'constraints_synth.xdc').read_text(encoding='utf-8')
    falsepaths = re.findall(r'^current_instance ([^\n]+)\n(set_false_path[^\n]+)', xdc, re.M)
    constraints = read(BASE / 's6_collection_constraints_binding.json')
    require([{'scope': a, 'command': b} for a, b in falsepaths] == constraints['exported_reset_cdc_false_paths']
            and len(falsepaths) == xdc.count('set_false_path') == 2, '两scoped resetCDC例外错误')
    require('create_clock -period 20.000 -name clk_fpga_0' in xdc and 'set_input_jitter clk_fpga_0 0.600' in xdc, '实际约束不同')
    require('No valid timing exceptions found.' in (BASE / 'exceptions_synth.rpt').read_text(encoding='utf-8'), '例外报告原文缺失')
    methodology = (BASE / 'methodology_synth.rpt').read_text(encoding='utf-8')
    require(re.findall(r'^\s*Checks found:\s*(\d+)\s*
    for name in ['timing_summary_synth.rpt', 'timing_worst_synth.rpt', 'utilization_flat_synth.rpt', 'utilization_synth.rpt',
                 'clocks_synth.rpt', 'exceptions_synth.rpt', 'methodology_synth.rpt', 'drc_synth.rpt']:
        text = (BASE / name).read_text(encoding='utf-8')
        require('Vivado v.2026.1' in text and 'Design State : Synthesized' in text, '报告版本或状态错误：' + name)
    DETAILS['reports'] = {'status': 'FAIL_TIMING', 'timing': timing, 'resources': resources, 'worst_path': values,
                          'exported_scoped_reset_false_paths': falsepaths, 'check_timing_all_zero': True,
                          'methodology_rule': 'TIMING-16', 'methodology_checks': 736,
                          'exception_report_statement': 'No valid timing exceptions found.'}


def xsa_audit():
    comp = read(BASE / 's6_collection_xsa_member_comparison.json')
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
    execution=read(BASE/'s6_collection_execution_receipt.json')
    require(sha((BASE/'s6_collection_execution_receipt.json').read_bytes())==FINAL_SHA
            and execution['source_commit']==COMMIT and execution['status'].startswith('STOP_S6_FAIL_TIMING'),'Collector STOP版本变化')
    for key in ['collector','first_collector','packaging']:
        binding(execution[key])
    codes={}
    for stem,code in [('s6_collection_collector',1),('s6_collection_collector_r02',0),('s6_collection_sta',2),
                      ('s6_collection_evidence_r01',0),('s6_collection_inputs_r01',2)]:
        record=read(BASE/(stem+'.native.json'))
        require(isinstance(record['command'],list) and record['native_exit_code']==code,'历史native码改变：'+stem)
        for row in record['closed_logs']:
            binding(row)
            archived=BASE/Path(row['path']).name
            require(archived.is_file() and sha(archived.read_bytes())==row['sha256'],'归档native流遗漏')
        codes[stem]={'native_exit_code':code,'elapsed_seconds':record['elapsed_seconds']}
    error=(BASE/'s6_collection_collector.stderr.log').read_text(encoding='utf-8')
    require("KeyError: 'input'" in error and "call['input']['command']" in error,'首collector失败未保留')
    diagnostic=read(BASE/'s6_collection_preview_diagnostic.json')
    require(diagnostic['host_tool_exit_code']==1 and diagnostic['native_exit_code'] is None
            and diagnostic['raw_log_modified'] is False and diagnostic['stdout_raw_complete'] is False
            and diagnostic['stderr_raw_complete'] is False,'辅助预览未测字段伪填')
    actual=read(BASE/'s6_collection_sta_checker_binding.json')
    require(actual['requested_identifier']=='verification/check_s2b_inference_sta.py'
            and actual['requested_native_exit_code'] is None,'错误路径伪执行')
    snapshot=binding(actual['actual_classifier_snapshot'])
    require(snapshot==binding(actual['actual_classifier_original']),'分类器复用原字节不同')
    require(not (ROOT/actual['requested_identifier']).exists(),'历史指定不存在路径事实改变')
    manifest=read(BASE/'s6_collection_delivery_manifest_r02.json')
    notrun=[r for r in manifest['checks'] if r['status']=='NOT_RUN']
    require(len(notrun)==7 and all(r['command'] is None and r['exit_code'] is None for r in notrun),'NOT_RUN状态丢失')
    require(sorted(r['exit_code'] for r in manifest['checks'] if r['status']=='FAIL')==[1,2,2],'FAIL改判PASS')
    summary=read(BASE/'s6_collection_summary_final.json')
    require(summary['collector_native_exit_code']==0 and summary['first_collector_native_exit_code']==1
            and summary['native_classifier_exit_code']==2 and summary['closed_packaging_codes']=={'evidence':0,'inputs':2},'三类失败状态混淆')
    DETAILS['preserved_failures']={'native_codes':codes,'first_failure':"KeyError('input')",
        'aux_preview_host_exit_code':1,'aux_preview_native_exit_code':None,
        'requested_classifier_not_present':actual['requested_identifier'],
        'actual_classifier':actual['actual_classifier_snapshot'],'not_run_names':[r['name'] for r in notrun],
        'collector_execution_receipt_sha256':FINAL_SHA,
        'review_task_classifier_name_correction':'s6_collection_classify_s6_sta.py不存在，实际绑定collector_code/classify_s6_sta.py。'}

def checker_audit():
    checker = str(BASE / 's6_collection_stage_checker_snapshot.py')
    manifest = str(BASE / 's6_collection_delivery_manifest_r02.json')
    for mode, code in [('evidence', 0), ('inputs', 2)]:
        stdout = run_native('checker_' + mode, [sys.executable, '-B', '-X', 'utf8', checker, '--mode', mode,
                          '--manifest', manifest, '--project-root', str(ROOT)], code)
        require(('CHECKS_OK' in stdout.decode('utf-8')) == (mode == 'evidence'), '包装与inputs混淆')
    run_native('classifier_original', [sys.executable, '-B', '-X', 'utf8', str(BASE / 'collector_code/classify_s6_sta.py'),
               '--report', str(BASE / 'timing_summary_synth.rpt'), '--result', str(OUT / 'classifier_original_result.json')], 2)
    DETAILS['independent_native'] = {'evidence': 0, 'inputs': 2, 'classifier': 2,
                                    'checker_source': 'Git5cb固定字节；没有运行live S6平台checker。'}


def validate_claims(sta,summary,native,inputs):
    require(sta['status']=='FAIL_TIMING' and sta['timing']==DETAILS['reports']['timing'],'STA状态/数值矛盾')
    require(summary['resources']==DETAILS['reports']['resources'],'资源与原报告不同')
    require(len(native['files'])==94 and sum(Path(r['saved_path']).suffix=='.vds' for r in native['files'])==5,'native/VDS遗漏')
    require(inputs==DETAILS['independent_native']['inputs']==2,'inputs被伪改0')
    require(summary['worst_path']==DETAILS['reports']['worst_path'],'路径与原报告不同')


def counterexamples():
    """七个反例仅改变内存元数据和文本，业务原件不动。"""
    original_sta=read(BASE/'s6_collection_sta_result.json')
    original_summary=read(BASE/'s6_collection_summary_final.json')
    original_native=read(BASE/'s6_collection_native_mapping.json')
    validate_claims(original_sta,original_summary,original_native,2)
    cases=[]
    def reject(name,operation):
        try:
            operation()
        except (AssertionError,ValueError,IndexError,KeyError) as exc:
            cases.append({'name':name,'status':'EXPECTED_REJECTION','exception':repr(exc)})
        else:
            raise AssertionError('反例未拒绝：'+name)
    false_sta=copy.deepcopy(original_sta)
    false_sta['status']='PASS'
    reject('错误STA标PASS',lambda:validate_claims(false_sta,original_summary,original_native,2))
    text=(BASE/'timing_summary_synth.rpt').read_text(encoding='utf-8')
    reject('50MHz伪25MHz',lambda:parse_timing(text.replace('20.000','40.000')))
    resources=copy.deepcopy(original_summary)
    resources['resources']['lut']+=1
    reject('资源数值错误',lambda:validate_claims(original_sta,resources,original_native,2))
    native=copy.deepcopy(original_native)
    native['files']=[r for r in native['files'] if not r['saved_path'].endswith('.vds')]
    reject('遗漏5VDS',lambda:validate_claims(original_sta,original_summary,native,2))
    raw=(PRE/'source_snapshot/src/s2b_conv_tile_engine.sv').read_bytes()
    reject('源码单字节漂移',lambda:require(sha(raw+b'\n')==sha(raw),'RAW源码漂移'))
    reject('假inputs0',lambda:validate_claims(original_sta,original_summary,original_native,0))
    item=copy.deepcopy(read(BASE/'s6_collection_delivery_manifest_r02.json')['files'][0])
    item['sha256']='0'*64
    reject('文件SHA篡改',lambda:binding(item))
    DETAILS['counterexamples']=cases

def main():
    require(ROOT==Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition'),'精确ROOT错误')
    for name,function in [('315绑定/55原件/234formal/raw非UTF8',inventory_audit),
        ('38源码/Git32RAW+6EOL/31+7/原14',source_audit),('94native/1190306B/五job/5VDS/18编译/wrapper',native_audit),
        ('MCP1至9/raw无input/timeout/native/elapsed',mcp_audit),('实际STA/资源/ROUTE路径/约束',reports_audit),
        ('六PSinit/HWH/no-bit/postconfig',xsa_audit),('首collector/辅助preview/分类路径/NOT_RUN',failure_audit),
        ('固定checker/classifier原生执行',checker_audit),('七个metadata反例',counterexamples)]:
        group(name,function)
    status='PASS_EVIDENCE_INTEGRITY_ONLY' if all(r['status']=='PASS' for r in CHECKS) else 'CHANGES_REQUIRED'
    save('native_commands.json',{'commands':NATIVE,'count':len(NATIVE)})
    receipt={'schema_version':1,'status':status,'execution_state':'STOP','review_task':'S2B-T17-S6-G2',
        'reviewed_source_commit':COMMIT,'reviewed_manifest':rel(BASE/'s6_collection_delivery_manifest_r02.json'),
        'reviewed_manifest_sha256':MANIFEST_SHA,'reviewed_collector_receipt_sha256':FINAL_SHA,
        'created_at_utc8':datetime.now(timezone(timedelta(hours=8))).isoformat(),'checks':CHECKS,'details':DETAILS,
        'native_command_count':len(NATIVE),'elapsed_seconds':time.monotonic()-START,
        'reviewer_process_memory':memory_peak(os.getpid()),'process_tree_peak_memory_bytes':None,
        'modification_scope':rel(OUT),'project_code_modified':False,'git_or_state_modified':False,
        'review_scope':'固定b0源码及S6失败证据完整性；未运行RTL/综合/设备/ROSS。',
        'limitations':['STA仍FAIL_TIMING；本PASS不批准STA/物理freeze/runtime/G3/G4/G5。',
            '实现/postroute/bit/cache/model/109/1000次/BOARD均NOT_RUN；物理0.1.1 NOT_FROZEN、visibility0。',
            'Git输出留真实native码/SHA/bytes，可从固定Git对象及既有快照重建，未复制大报告/SDK/EXE。',
            'source和builder的client input未捕获，命令依据同次关闭history1/2；不伪造client输入。',
            'MCP client300s timeout与nativewait0/301.363s分记；wrapperexit342s与launcherfinished346s分记。',
            'core164s/2175.812MB、maxsingle2210.242MB、root累计2056.789MB分记；综合全树峰未知。',
            '原root snapshot非UTF8仅RAW和ASCII字段核对，不以replacement decoding宣称原字节恢复。',
            'owned session停止结果success已保留；本包未捕获post-stop PID absence原始文件，未现场查询。',
            'task卡中的s6_collection_classify_s6_sta.py不存在，按已声明实际collector_code/classify_s6_sta.py绑定执行。']}
    save('receipt.json',receipt)
    print(json.dumps({'status':status,'execution_state':'STOP','groups':len(CHECKS),'negative_cases':len(DETAILS.get('counterexamples',[])),
        'native_commands':len(NATIVE),'elapsed_seconds':receipt['elapsed_seconds']},ensure_ascii=False),flush=True)
    return 0 if status=='PASS_EVIDENCE_INTEGRITY_ONLY' else 2


if __name__=='__main__':
    raise SystemExit(main())
