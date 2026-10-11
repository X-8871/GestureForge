"""收集已结束S5实际综合原件，仅消费封存快照及Git5cb。"""
from collection_common import *
from datetime import datetime, timezone, timedelta
import re, xml.etree.ElementTree as ET, zipfile, zlib

def first(pattern, text):
    """要求实际报告包含唯一定位的首项字段。"""
    values = re.findall(pattern, text, re.M)
    require(values, '缺少字段：' + pattern)
    return values[0].strip()

started = time.monotonic()
original_check()
rawcopy(WORK / 'initial_inventory.json', REPORT / 's5_collection_original_inventory.json')
for name in ('collection_common.py', 'classify_s5_sta.py', 'collect_s5.py', 'run_collection.py', 'finalize_s5.py', 'run_finalization.py'):
    rawcopy(WORK / name, REPORT / ('s5_collection_' + name))
root_log = REPORT / 's5_collection_root_session_snapshot.log'
require(sha(root_log) == '2db94cb1610b60a00dfe8aa096ec886da103cfbb2d44e64cb58ad02294606eb5' and root_log.stat().st_size == 520599, 'root关闭快照不同')
save(REPORT / 's5_collection_root_log_binding.json', {'snapshot': binding(root_log), 'scope': '原始累计副本包含旧运行；本次只绑定history95–103及s5p1五job。未读取活动源累计日志。', 'active_log_consumed': False, 'root_cumulative_peak_is_s5_process_tree_peak': False})

before = read(PRE / 'source_before.json')
after = read(PRE / 'source_after.json')
static = read(CACHE / 'static_actual_closed.json')
require(sha(PRE / 'source_before.json') == '4bf20ffe8803a6296f3d9190d7e12da1267185790e58669e12ae6c9beba1d845', 'before哈希不同')
require(sha(PRE / 'source_after.json') == 'f62299dafeb80aad93881b45cc101b763382e20819ffb08b996a0b7588560a78', 'after哈希不同')
require(sha(CACHE / 'static_actual_closed.json') == 'fb94e84c9fb5bacccf35c5f7c76f3e1ee4afa6cd5a893dc071aeb13672602cdc', 'static封存不同')
require(before['source_commit'] == after['source_commit'] == static['source_commit'] == BASELINE, '基线不同')
rows = before['source_files']
later = {r['path']: r for r in after['source_files']}
require(len(rows) == len(later) == 38 and static['source_count'] == len(static['source_sha256']) == 31, '实际计数不是38/31')
require(set(static['source_sha256']) | set(static['extra_bindings']) == set(later) and not set(static['source_sha256']) & set(static['extra_bindings']) and len(static['extra_bindings']) == 7, '31+7闭包不同')
sources = []
for row in rows:
    old, new = exact(ROOT / row['snapshot']), exact(ROOT / later[row['path']]['snapshot'])
    require(sha(old) == sha(new) == row['sha256'] == later[row['path']]['sha256'] and old.stat().st_size == new.stat().st_size == row['bytes'] == later[row['path']]['bytes'], '前后源快照漂移：' + row['path'])
    blob, command, code = git_blob(row['path'])
    same = blob == old.read_bytes()
    eol = not same and b'\r\n' not in blob and blob.replace(b'\n', b'\r\n') == old.read_bytes()
    require(hashlib.sha256(blob).hexdigest() == row['git_blob_sha256'] and (same or eol), 'Git原字节或精确EOL关系不同')
    require(row['git_relation'] == ('RAW_IDENTICAL' if same else 'GIT_LF_TO_RAW_CRLF'), '原关系标签不同')
    if row['path'] in static['source_sha256']:
        require(row['sha256'] == static['source_sha256'][row['path']], '静态源码哈希不同')
    sources.append({**row, 'snapshot_after': rel(new), 'git_native_command': command, 'git_native_exit_code': code, 'git_raw_same': same, 'exact_git_lf_to_snapshot_crlf': eol, 'live_source_consumed': False})
require(sum(r['git_raw_same'] for r in sources) == 32 and sum(r['exact_git_lf_to_snapshot_crlf'] for r in sources) == 6, '不是32RAW+6精确EOL')
freeze = exact(ROOT / before['source_freeze'])
require(sha(freeze) == before['source_freeze_sha256'] == after['source_freeze_sha256'] == '4d9540a77c9c15e796609ba54040090556b577f3a9851434166859aba19090f6', 'freeze字节漂移')
frozen = read(freeze)
require(frozen['source_sha256'] == {r['path']: r['sha256'] for r in rows}, '实际38与封存38不同')
require(before['frozen14_sha256'] == after['frozen14_sha256'] == frozen['frozen14_sha256'] and len(frozen['frozen14_sha256']) == 14, '原14绑定不同')
for name, expected in frozen['frozen14_sha256'].items():
    require(later[name]['sha256'] == expected, '原14快照漂移')
profile = read(ROOT / later['board/s2b_inference_platform.json']['snapshot'])
require(profile['version'] == 's2b-inference-platform/0.1.5' and profile['clock_hz'] == 50000000 and profile['visibility_default'] == 0 and profile['vivado_part'] == 'xc7z020clg400-2', '实际profile不同')
s4_before_path = ROOT / 'report/evidence/S2B-T17/s4_source_preflight_20261011_r03/source_before.json'
s4 = read(s4_before_path)
s4names = {r['path'] for r in s4['source_files']}
require(len(s4names) == 37 and s4names < set(later), '37→38不是严格新增1项')
added = sorted(set(later) - s4names)
require(added == ['report/evidence/S2A-T01/tiny416_model_manifest.json'], '额外输入不是模型manifest')
save(REPORT / 's5_collection_source_binding.json', {'status': 'S5_ACTUAL38_BEFORE_AFTER_IDENTICAL_GIT5CB_BOUND', 'source_commit': BASELINE, 'source_before': binding(PRE / 'source_before.json'), 'source_after': binding(PRE / 'source_after.json'), 'static_actual': binding(CACHE / 'static_actual_closed.json'), 'source_freeze': binding(freeze), 'source_count': 38, 'platform_static_source_count': 31, 'extra_bindings': static['extra_bindings'], 'sources': sources, 'git_raw_same_count': 32, 'exact_eol_count': 6, 'frozen14_unchanged': True, 'frozen14_sha256': frozen['frozen14_sha256'], 'prior_s4_source_before': binding(s4_before_path), 'prior_s4_count': 37, 'new_binding_from_s4': added, 'live_source_consumed': False, 'note': 'path为历史源码标识；绑定已捕获snapshot和snapshot_after，不依赖后来S6修改的live路径。模型manifest复用已有快照，未重复复制22MB。freeze内旧提交及旧G2状态原样保留，实际运行源码提交以本清单为准。'})

native_root = mkdir_new(REPORT / 'native_jobs')
run_root = exact(PROJECT / 's2b_inference_candidate.runs', 'directory')
directories = sorted(p for p in run_root.iterdir() if p.is_dir() and p.name != '.jobs')
require(len(directories) == 5, '不是五个实际job')
mapping, jobs = [], []
for directory in directories:
    target = mkdir_new(native_root / ('wrapper_native_s5_r01' if directory.name == 'synth_1' else directory.name))
    log = exact(directory / 'runme.log').read_text(encoding='utf-8')
    require('synth_design completed successfully' in log and '0 Critical Warnings and 0 Errors encountered' in log, '原生综合未完成')
    require((directory / '__synthesis_is_complete__').is_file() and (directory / '.vivado.end.rst').is_file() and not (directory / '.vivado.error.rst').exists(), '原生结束marker不同')
    for path in sorted(directory.iterdir()):
        if path.is_file() and (path.suffix in ('.tcl', '.log', '.jou', '.vds', '.xdc', '.rpt', '.rst', '.js', '.sh', '.bat', '.xml') or path.name in ('htr.txt', '__synthesis_is_complete__')):
            mapping.append(rawcopy(path, target / path.name))
    process = ET.fromstring((directory / '.vivado.begin.rst').read_bytes()).find('Process')
    require(process is not None, 'launcher缺失')
    elapsed = re.search(r'synth_design:.*?elapsed = (\d+):(\d+):(\d+)', log)
    require(elapsed, '综合耗时缺失')
    start = first(r'Start of session at:\s*([^\r\n]+)', log)
    end = first(r'Exiting Vivado at ([^\r\n]+)', log).removesuffix('...')
    diag = re.findall(r'(\d+) Infos, (\d+) Warnings, (\d+) Critical Warnings and (\d+) Errors encountered', log)
    jobs.append({'run': directory.name, 'saved_directory': rel(target), 'status': 'NATIVE_SYNTH_COMPLETED_LOG_AND_MARKERS', 'actual_vivado_job_pid': int(first(r'Process ID\s*:\s*(\d+)', log)), 'launcher_pid_from_begin_rst': int(process.attrib['Pid']), 'launcher_command': process.attrib['Command'], 'session_start_local': start, 'session_end_local': end, 'timezone_context': 'UTC+8', 'session_wall_seconds_from_native_timestamps': (datetime.strptime(end, '%a %b %d %H:%M:%S %Y') - datetime.strptime(start, '%a %b %d %H:%M:%S %Y')).total_seconds(), 'synth_design_elapsed_seconds': int(elapsed[1])*3600 + int(elapsed[2])*60 + int(elapsed[3]), 'reported_single_process_peak_mb': max(map(float, re.findall(r'peak = ([0-9.]+)', log))), 'peak_unit': 'Vivado日志MB，未换算为GiB或进程树峰', 'final_diagnostics': dict(zip(('infos', 'warnings', 'critical_warnings', 'errors'), map(int, diag[-1]))), 'raw_os_process_exit_code': None, 'os_exit_code_reason': '未直接观测OS子进程退出码；原生日志、结束marker和同次wait0为完成依据。'})
infer = next(j for j in jobs if j['run'] == 's2b_inference_infer_0_synth_1')
require(infer['synth_design_elapsed_seconds'] == 159 and infer['reported_single_process_peak_mb'] == 2200.098, '核心实测值不同')
require(max(j['reported_single_process_peak_mb'] for j in jobs) == 2209.809, '五job可得单进程最大值不同')
tcl = (native_root / 's2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl').read_text(encoding='utf-8')
block = first(r'read_verilog -library xil_defaultlib -sv \{([^}]+)\}', tcl)
compiled = [Path(line.strip()).relative_to(ROOT).as_posix() for line in block.splitlines() if line.strip()]
require(len(compiled) == len(set(compiled)) == 18 and set(compiled) == set(profile['rtl_sources']), '原生编译18不同')
generated = mkdir_new(REPORT / 'generated_inputs')
genroot = exact(PROJECT / 's2b_inference_candidate.gen/sources_1/bd/s2b_inference', 'directory')
constraints = sorted(genroot.rglob('*.xdc')) + sorted(run_root.rglob('*_propImpl.xdc'))
require(len(constraints) == 7 and len({p.name for p in constraints}) == 7, '生成约束实际数不同')
for path in constraints:
    mapping.append(rawcopy(path, generated / path.name))
wrapper = exact(PROJECT / 's2b_inference_candidate.srcs/sources_1/imports/hdl/s2b_inference_wrapper.v')
genwrapper = exact(genroot / 'hdl/s2b_inference_wrapper.v')
require(sha(wrapper) == sha(genwrapper), 'import/generated wrapper不同')
mapping.append(rawcopy(wrapper, generated / wrapper.name))
for path in (exact(genroot / 'synth/s2b_inference.v'), exact(genroot / 'ip/s2b_inference_infer_0/synth/s2b_inference_infer_0.sv')):
    mapping.append(rawcopy(path, generated / path.name))
require(wrapper.as_posix() in (native_root / 'wrapper_native_s5_r01/s2b_inference_wrapper.tcl').read_text(encoding='utf-8'), '真实wrapper编译路径缺失')
require('wrapper ' + wrapper.as_posix() + ' top s2b_inference_wrapper' in (REPORT / 'setup_synthesis.tcldict').read_text(encoding='utf-8'), 'setup唯一wrapper绑定不同')
save(REPORT / 's5_collection_native_mapping.json', {'files': mapping, 'jobs': jobs, 'native_job_count': 5, 'native_raw_copy_count': len(mapping), 'actual_compiled_rtl_sources': compiled, 'actual_compiled_source_count': 18, 'actual_compiled_source_snapshots': [{'source_identifier': name, 'source_snapshot': later[name]['snapshot'], 'sha256': later[name]['sha256']} for name in compiled], 'source_binding': rel(REPORT / 's5_collection_source_binding.json'), 'wrapper_import': binding(wrapper), 'wrapper_generated_original': binding(genwrapper), 'unique_registered_wrapper_count_from_setup': 1, 'generated_wrapper_raw_equals_imported': True, 'single_process_peak_max_mb': 2209.809, 'process_tree_peak_memory_bytes': None, 'excluded_cache_policy': '只保存必要原生脚本/日志/VDS/marker和生成约束；DCP/PB/WDF/缓存及整工程不复制。VDS在本次为文本原生日志，非波形。'})

mcpdir = mkdir_new(REPORT / 'mcp_closed')
for name in sorted(p.name for p in CACHE.glob('mcp_*.json')) + ['resource_preflight.json', 'status_post_client_timeout.json', 'static_actual_closed.json', 'source_preflight.py']:
    rawcopy(CACHE / name, mcpdir / name)
history = [h for b in read(mcpdir / 'mcp_history_closed.json')['content'] if b['type'] == 'text' for h in json.loads(b['text']).get('history', [])]
require([h['id'] for h in history] == list(range(95,104)), '实际history不是95–103')
labels = ('source', 'builder', 'setup', 'launch', 'wait', 'open_run', 'reports', 'query_xdc', 'close')
paired = []
for label, item in zip(labels, history):
    call = read(mcpdir / ('mcp_' + label + '.json'))
    require(call['input']['command'] == item['command'], 'MCP/native命令不匹配')
    if label == 'wait':
        require(call['result'].get('isError') is True and '300s' in call['result']['content'][0]['text'] and item['code'] == 0 and item['elapsed'] == 301.425, '客户端timeout/native成功事实不同')
    else:
        require(json.loads(call['result']['content'][0]['text'])['exit_code'] == item['code'], 'MCP/native码不同')
    paired.append({'label': label, 'client_record': binding(mcpdir / ('mcp_' + label + '.json')), 'native_history': item, 'client_wall_ms': call.get('wall_ms')})
byid = {h['id']: h for h in history}
states = byid[102]['output']
require(states.count('status {synth_design Complete!} progress 100%') == 5 and states.count('status {Not started} progress 0%') == 5 and 'clock_period 20.000' in states, '真实run状态不同')
require('[Sun Oct 11 18:26:44 2026] Launched synth_1' in byid[98]['output'] and '[Sun Oct 11 18:32:19 2026] synth_1 finished' in byid[99]['output'], '整次launcher时刻不同')
products = (REPORT / 'products.tcldict').read_text(encoding='utf-8')
require('status FAIL code 0 raw PRODUCTS:OK' in products and 'WARNING emitted=-8 exported=2' in products and 'native_counts_before {WARNING 9' in products and 'native_counts_after {WARNING 1' in products, 'products原FAIL不同')
save(REPORT / 's5_collection_mcp_history_binding.json', {'status': 'CLOSED_HISTORY95_TO103_BOUND_CLIENT_NATIVE_RESULTS', 'paired_calls': paired, 'mcp_execute_calls': 9, 'mcp_history_calls': 1, 'execute_plus_history_calls': 10, 'post_timeout_status_queries': 1, 'all_host_tool_calls': None, 'client_wait_is_error': True, 'client_wait_timeout_seconds': 300, 'client_wait_wall_ms': read(mcpdir / 'mcp_wait.json')['wall_ms'], 'native_wait_exit_code': 0, 'native_wait_elapsed_seconds': 301.425, 'launch_timestamp_local': '2026-10-11T18:26:44+08:00', 'native_vivado_wrapper_exit_local': '2026-10-11T18:32:18+08:00', 'launcher_finished_local': '2026-10-11T18:32:19+08:00', 'launch_to_native_wrapper_exit_seconds': 334, 'launch_to_launcher_finished_seconds': 335, 'whole_builder_native_exit_code': 1, 'whole_builder_native_elapsed_seconds': byid[96]['elapsed'], 'products_native_exit_code': 0, 'products_capture_exit_code': 1, 'products_warning_counter_before': 9, 'products_warning_counter_after': 1, 'products_warning_emitted_delta': -8, 'products_warning_exported_count': 2, 'products_repeated': False, 'root_session_cumulative_peak_mb': 2695.598, 'root_session_peak_is_s5_run_peak': False, 'process_tree_peak_memory_bytes': None, 'implementation_started': False, 'implementation_strategy_list_only': states.split(' impl_strategies ', 1)[1], 'source_json_host_serialization_failure': {'tool_chunk_id': 'c1da5f', 'host_native_exit_code': 1, 'error': 'Invalid control character', 'target_written_by_failed_attempt': False, 'recovered_file': binding(mcpdir / 'mcp_source.json'), 'recovery_basis': '同一个实际MCP返回经apply_patch重建，非重新source执行；关闭history95独立绑定命令/code0。原始client raw失败流未作为独立字节文件获得，不能声称原生raw逐字节绑定。'}})

classifier = run_closed([sys.executable, '-B', str(WORK / 'classify_s5_sta.py'), '--report', str(REPORT / 'timing_summary_synth.rpt'), '--result', str(REPORT / 's5_collection_sta_result.json')], 's5_collection_sta')
require(classifier['native_exit_code'] == 2, 'STA分类不是实际2')
copy_closed('s5_collection_sta')
sta = read(REPORT / 's5_collection_sta_result.json')
timing = sta['timing']
require((timing['wns_ns'], timing['tns_ns'], timing['setup_failing_endpoints'], timing['setup_total_endpoints']) == (-12.623,-4759.345,763,14804) and not any(sta['check_timing'].values()), 'STA实际值不同')
util = (REPORT / 'utilization_flat_synth.rpt').read_text(encoding='utf-8')
resources = {k: int(first(r'^\|\s*' + re.escape(label) + r'\s*\|\s*(\d+)\s*\|', util)) for k,label in (('lut','Slice LUTs*'),('ff','Slice Registers'),('bram','Block RAM Tile'),('dsp','DSPs'),('latch','Register as Latch'))}
require(resources == {'lut':24470,'ff':4028,'bram':32,'dsp':156,'latch':0}, '资源实际值不同')
worst = (REPORT / 'timing_worst_synth.rpt').read_text(encoding='utf-8')
w = {'source': first(r'^\s*Source:\s*(\S+)', worst), 'destination': first(r'^\s*Destination:\s*(\S+)', worst), 'logic_levels': int(first(r'^\s*Logic Levels:\s*(\d+)', worst)), 'carry4': int(first(r'^\s*Logic Levels:.*?CARRY4=(\d+)', worst)), 'dsp48e1': int(first(r'^\s*Logic Levels:.*?DSP48E1=(\d+)', worst)), 'data_path_delay_ns': float(first(r'^\s*Data Path Delay:\s*([\d.]+)ns', worst)), 'logic_delay_ns': float(first(r'^\s*Data Path Delay:.*?logic ([\d.]+)ns', worst)), 'route_delay_ns': float(first(r'^\s*Data Path Delay:.*?route ([\d.]+)ns', worst))}
require(w['source'].endswith('u_conv_engine/validation_ok6__5/CLK') and w['destination'].endswith('u_conv_engine/result_error_latched_reg[0]/D') and (w['logic_levels'],w['carry4'],w['dsp48e1'],w['data_path_delay_ns'],w['logic_delay_ns'],w['route_delay_ns']) == (62,38,1,32.219,19.492,12.727), '最坏路径不同')
xdc = (REPORT / 'constraints_synth.xdc').read_text(encoding='utf-8')
exceptions = re.findall(r'current_instance ([^\r\n]+)\r?\n(set_false_path[^\r\n]+)', xdc)
require(len(exceptions) == 2 and all('rst_fclk0/U0/EXT_LPF/' in scope and 'syncstages_ff_reg[0]' in command for scope,command in exceptions), 'resetCDC例外不同')
require('No valid timing exceptions found.' in (REPORT / 'exceptions_synth.rpt').read_text(encoding='utf-8'), '原exceptions报告不同')
save(REPORT / 's5_collection_constraints_binding.json', {'clock': sta['clock'], 'input_jitter_ns': 0.6, 'check_timing': sta['check_timing'], 'exported_reset_cdc_false_paths': [{'scope': scope, 'command': command} for scope,command in exceptions], 'exported_false_path_count': 2, 'report_exceptions_raw_statement': 'No valid timing exceptions found.', 'interpretation': '无内部漏约束仅指本次检查计数0；write_xdc两个scoped resetCDC false_path和原report_exceptions文字分别保留，不能称零false_path。'})
method = (REPORT / 'methodology_synth.rpt').read_text(encoding='utf-8')
drc = (REPORT / 'drc_synth.rpt').read_text(encoding='utf-8')
require(int(first(r'Checks found:\s*(\d+)', method)) == 747 and '| TIMING-16 | Warning' in method, 'methodology不同')
drc_rules = [{'rule': a, 'severity': b, 'description': c.strip(), 'count': int(d)} for a,b,c,d in re.findall(r'^\|\s*([A-Z]+-\d+)\s*\|\s*(\w+)\s*\|([^|]+)\|\s*(\d+)\s*\|', drc, re.M)]
require(sum(r['count'] for r in drc_rules) == 417, 'DRC实际数不同')

old_xsa = exact(ROOT / 'report/evidence/S2B-T13/artifact_recheck_20261011_r01/s2b_inference_no_bit.xsa')
new_xsa = exact(REPORT / 's2b_inference_no_bit.xsa')
members = []
psroot = exact(genroot / 'ip/s2b_inference_ps7_0', 'directory')
with zipfile.ZipFile(old_xsa) as old, zipfile.ZipFile(new_xsa) as new:
    require(not any(n.endswith('.bit') for n in new.namelist()), 'XSA意外含bit')
    for name in ('ps7_init.c','ps7_init.h','ps7_init.html','ps7_init.tcl','ps7_init_gpl.c','ps7_init_gpl.h','s2b_inference.hwh'):
        a,b = old.read(name),new.read(name)
        require(zlib.crc32(a) == old.getinfo(name).CRC and zlib.crc32(b) == new.getinfo(name).CRC, 'XSA CRC不同')
        row = {'member':name,'old_sha256':hashlib.sha256(a).hexdigest(),'new_sha256':hashlib.sha256(b).hexdigest(),'old_bytes':len(a),'new_bytes':len(b),'raw_equal':a==b,'old_crc32':old.getinfo(name).CRC,'new_crc32':new.getinfo(name).CRC}
        if name.startswith('ps7_init'):
            require((psroot / name).read_bytes() == b, '生成PSinit与XSA字节不同')
            row['generated_original'] = binding(psroot / name)
            row['saved_copy'] = rawcopy(psroot / name, generated / name)
        members.append(row)
    require(all(r['raw_equal'] for r in members[:6]) and not members[6]['raw_equal'], 'PSinit/HWH关系不同')
    metadata = {'xsa_json':json.loads(new.read('xsa.json')), 'hwdef_xml':new.read('hwdef.xml').decode('utf-8'), 'xsa_xml':new.read('xsa.xml').decode('utf-8')}
    require(metadata['xsa_json']['platformState'] == 'pre_synth' and metadata['xsa_json']['devices'][0]['part']['name'] == 'xc7z020clg400-2', 'XSA原元数据不同')
    for name in ('hwdef.xml','xsa.json','xsa.xml'):
        require(not (generated / name).exists(), 'XSA成员输出已有')
        with (generated / name).open('xb') as dst:
            dst.write(new.read(name))
pstcl = (generated / 'ps7_init.tcl').read_text(encoding='utf-8')
post = []
for revision in ('1_0','2_0','3_0'):
    body = first(r'proc ps7_post_config_' + revision + r' \{\} \{([^}]+)\}', pstcl)
    operations = [line.strip() for line in body.splitlines() if line.strip()]
    require(operations == ['mwr -force 0XF8000008 0x0000DF0D','mask_write 0XF8000900 0x0000000F 0x0000000F','mask_write 0XF8000240 0xFFFFFFFF 0x00000000','mwr -force 0XF8000004 0x0000767B'], '官方生成postconfig表不同')
    post.append({'silicon_revision':revision,'official_generated_procedure':'ps7_post_config_' + revision,'operations':operations})
save(REPORT / 's5_collection_xsa_member_comparison.json', {'status':'SIX_PSINIT_BYTES_SAME_T13_AND_GENERATED_HWH_CHANGED_NO_BIT','old_xsa':binding(old_xsa),'new_xsa':binding(new_xsa),'members':members,'official_generated_postconfig_tables':post,'xsa_metadata':metadata,'elf_runtime_compatibility':'NOT_APPROVED','note':'官方表指本次Vivado原生生成ps7_init.tcl硅版本表；未外推板级身份、未调用该表、未下载。六成员相等只证明各成员，不批准旧BSP/ELF整体兼容。XSA元数据为pre_synth，与后来综合态STA分开记录。'})

blob, command, code = git_blob('verification/check_stage_delivery.py')
checker = REPORT / 's5_collection_stage_checker_snapshot.py'
require(not checker.exists(), 'checker目标已有')
with checker.open('xb') as dst:
    dst.write(blob)
save(REPORT / 's5_collection_stage_checker_binding.json', {'source_commit':BASELINE,'original_identifier':'verification/check_stage_delivery.py','snapshot':binding(checker),'git_native_command':command,'git_native_exit_code':code,'live_checker_consumed':False})
interface_source = exact(ROOT / 'report/evidence/S2B-T17/s4_platform_20261011_r01/s4_collection_delivery_manifest_r02.json')
interfaces = read(interface_source)['interfaces']
for item in interfaces:
    require(sha(ROOT / item['path']) == item['sha256'], '正式接口文档漂移')
externals = [{'path': rel(p), 'role':'input'} for p in (freeze, old_xsa, interface_source, s4_before_path, PRE / 'source_before.json', PRE / 'source_after.json')]
externals += [{'path':r['snapshot'],'role':'source'} for r in rows] + [{'path':r['snapshot'],'role':'source'} for r in after['source_files']]
limitations = ['仅封装S5已结束综合失败证据；STA真实FAIL_TIMING，证据独立审查未执行，G3/G4/G5未通过。','实际5cb源码38=31static+7额外绑定，前后快照相同；32Git RAW+6精确LF→CRLF，原14不变；live S6源码未消费。','freeze原件包含旧提交140e及当时G2 NOT_RUN，实际源码5cb由Git及root前后快照另行绑定；源码等价G2不代表STA通过。','原builder1/products native0 capture1，WARNING9→1、emit−8/export2；XSA原生导出成功不代表builder入口整体成功，未重跑products。','客户端wait300秒timeout/isError与同次native wait0/301.425秒分开；launch至native wrapper退出334秒、launcherfinished335秒分别绑定。','infer synth159秒/单进程峰2200.098MB；五job最大已知单进程ps7 2209.809MB；root累计2695.598MB不能作为本次进程树峰；全树峰未测。','五job原生OS子进程退出码未直接观测，null不伪填0；实际完成依据native日志、marker、historywait0和run100%。','check_timing零计数不代表无例外；两个scoped resetCDC false_path与report_exceptions的No valid文字分别保留。','50MHz综合態WNS−12.623/TNS−4759.345，763/14804setup失败；最坏CONV validation_ok6__5 DSP/CLK至result_error_latched_reg[0]/D，62级/38CARRY4/1DSP，32.219ns。','source JSON宿主序列化曾原生1/Invalid control character且未写目标；同实际MCP结果apply_patch恢复，history95 source0独立绑定。原raw失败流未单独获得，未伪称逐字节恢复。','六PSinit成员与T13及本次生成字节一致而HWH变化；官方生成postconfig表只作证据，未批准旧BSP/ELF整体兼容；XSA pre_synth无bit。','实现/postroute/bit/cache/model/109/1000次/BOARD全部NOT_RUN；物理候选0.1.1 NOT_FROZEN，visibility0。','root9execute+1history=10另计1status；全部host工具调用数、Collector峰及全进程树峰未测；CHECKS_OK仅包装通过。','初次库存检查打印因Windows默认GBK无法编码历史异常字符而退出1，初始库存已保存，未改任何原件；后续明确UTF-8成功，不把该宿主打印失败当综合失败。']
summary = {'status':'COLLECTED_S5_FAIL_TIMING_PENDING_INDEPENDENT_EVIDENCE_REVIEW','source_commit':BASELINE,'source_count':38,'platform_static_source_count':31,'extra_binding_count':7,'compiled_rtl_count':18,'profile_version':profile['version'],'visibility':0,'original_raw_file_count':56,'original_raw_unchanged':True,'native_raw_copy_count':len(mapping),'native_job_count':5,'native_wait_exit_code':0,'native_wait_elapsed_seconds':301.425,'mcp_wait_timeout':True,'launch_to_native_wrapper_exit_wall_seconds':334,'launch_to_launcher_finished_wall_seconds':335,'native_report_exit_code':byid[101]['code'],'native_report_elapsed_seconds':byid[101]['elapsed'],'native_classifier_exit_code':2,'timing':timing,'check_timing':sta['check_timing'],'resources':resources,'worst_path':w,'methodology':{'checks':747,'rule':'TIMING-16','severity':'Warning'},'drc':{'checks':417,'rules':drc_rules},'exported_reset_cdc_false_path_count':2,'external_inputs':externals,'resource_preflight':binding(mcpdir / 'resource_preflight.json'),'disk_free_gib':read(mcpdir / 'resource_preflight.json')['disk_C']['free']/(1024**3),'memory_free_mib':read(mcpdir / 'resource_preflight.json')['machine']['FreePhysicalMemoryKiB']/1024,'threads':1,'jobs':1,'synthesis_execution_count':1,'products_execution_count':1,'mcp_execute_calls':9,'mcp_history_calls':1,'post_timeout_status_queries':1,'collector_peak_memory_bytes':None,'process_tree_peak_memory_bytes':None,'limitations':limitations,'created_at_utc8':datetime.now(timezone(timedelta(hours=8))).isoformat(),'collector_elapsed_so_far_seconds':time.monotonic()-started}
save(REPORT / 's5_collection_summary.json', summary)
checks = [{'name':'S5实际38快照及Git5cb核验','status':'PASS','command':' '.join(sources[0]['git_native_command']),'exit_code':0,'reason':'首条真实Git命令及其余37条命令/码均在source_binding；32RAW+6精确EOL；14冻结源不变。'},{'name':'五个原生综合完成','status':'PASS','command':byid[99]['command'],'exit_code':0,'reason':'history99原生0/301.425秒；clienttimeout单独记录，不冒充原生失败。'},{'name':'实际综合态STA报告生成','status':'PASS','command':byid[101]['command'],'exit_code':0},{'name':'50MHz综合态STA分类','status':'FAIL','command':' '.join(classifier['command']),'exit_code':2,'reason':'WNS−12.623/TNS−4759.345、763/14804setup失败，非postroute。'},{'name':'builder与products捕获原失败','status':'FAIL','command':byid[96]['command'],'exit_code':1,'reason':'builder1，products native0/capture1；WARNING9→1原FAIL保持。'}]
for name in ('S5独立证据准确性审查','实现及postroute','bitstream生成','板上cache probe','板上模型及109样本','1000次板上任务','BOARD及G3验收'):
    checks.append({'name':name,'status':'NOT_RUN','command':None,'exit_code':None,'reason':'本Collector仅收集已结束原件，未执行该项，不能继承通过。'})
manifest = {'schema_version':1,'stage':'2B','task_id':'S2B-T17','run_id':'s5_platform_20261011_r01','source_commit':BASELINE,'evidence_dir':rel(REPORT),'interfaces':interfaces,'tool_versions':{'python':sys.version,'Vivado':'2026.1 Build6511674 原报告/日志','part':profile['vivado_part'],'profile':profile['version']},'files':manifest_files(externals),'checks':checks,'limitations':limitations}
manifest_path = REPORT / 's5_collection_delivery_manifest_r01.json'
save(manifest_path, manifest)
results = {mode:run_closed([sys.executable,'-B',str(checker),'--mode',mode,'--manifest',str(manifest_path),'--project-root',str(ROOT)],'s5_collection_' + mode + '_r01') for mode in ('evidence','inputs')}
require({k:r['native_exit_code'] for k,r in results.items()} == {'evidence':0,'inputs':2}, '包装实际码不同')
for mode in results:
    copy_closed('s5_collection_' + mode + '_r01')
save(REPORT / 's5_collection_packaging_r01.json', {'status':'EVIDENCE_PACKAGING_OK_INPUTS_ACTUAL_FAIL','checks':results,'policy':'evidence0只代表包装；inputs2含未冻结/实际FAIL/NOT_RUN，不改变阶段门禁。'})
original_check()
print(json.dumps({'status':summary['status'],'original_files':56,'native_copies':len(mapping),'source_count':38,'compiled_rtl_count':18,'codes':{'sta':2,'evidence':0,'inputs':2},'collector_elapsed_seconds':time.monotonic()-started},ensure_ascii=False))
