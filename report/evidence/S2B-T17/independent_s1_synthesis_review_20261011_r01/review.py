"""独立只读核查固定 S1 综合证据，仅向本脚本目录写收据。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import base64
import hashlib
import json
import re
import subprocess
import sys
import time
import zipfile

sys.stdout.reconfigure(encoding='utf-8')
root = Path.cwd()
out = Path(__file__).parent
run = root / 'report/evidence/S2B-T17/s1_platform_20261011_r01'
baseline = '6d00ff2d05e92fa6cff05243fb620f8a0232b9f1'
manifest = run / 'collector_delivery_manifest_r02.json'
expected_manifest = '46997fb8534ac66dfdfe8f75958da1ec5dd37ad43a66b51bf00264f77270fbfb'
started = time.monotonic()
checks = []
commands = []

def sha(path):
    """按原始字节计算哈希。"""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    """按 UTF-8 读取机器记录。"""
    return json.loads(Path(path).read_text(encoding='utf-8'))

def check(name, valid, detail=None):
    """累计检查结果，保留失败具体位置。"""
    checks.append({'name': name, 'status': 'PASS' if valid else 'FAIL', 'detail': detail})

def execute(name, argv, expected):
    """执行只读轻量检查，将原始输出写入隔离目录。"""
    begin = time.monotonic()
    result = subprocess.run(argv, cwd=root, capture_output=True)
    (out / (name + '.stdout.log')).write_bytes(result.stdout)
    (out / (name + '.stderr.log')).write_bytes(result.stderr)
    record = {'name': name, 'command': argv, 'exit_code': result.returncode, 'expected_exit_code': expected, 'elapsed_seconds': time.monotonic() - begin, 'stdout_sha256': sha(out / (name + '.stdout.log')), 'stderr_sha256': sha(out / (name + '.stderr.log'))}
    commands.append(record)
    check(name, result.returncode == expected, record)
    return result

m = read(manifest)
check('固定清单哈希与基线', sha(manifest) == expected_manifest and m['source_commit'] == baseline)
head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, cwd=root)
check('当前 Git HEAD', head.returncode == 0 and head.stdout.decode().strip() == baseline)
paths = {row['path'] for row in m['files'] if row['path'].startswith(m['evidence_dir'] + '/')}
actual = {p.relative_to(root).as_posix() for p in run.rglob('*') if p.is_file() and p != manifest}
check('全部证据文件恰好列清', paths == actual, {'listed': len(paths), 'actual': len(actual), 'missing': sorted(actual - paths), 'extra': sorted(paths - actual)})
bad = [row['path'] for row in m['files'] if not (root / row['path']).is_file() or sha(root / row['path']) != row['sha256']]
check('清单所有 SHA 独立重算', not bad, {'file_count': len(m['files']), 'bad': bad})
inventory = read(run / 'collector_original_inventory.json')
for name in ['root_files_before_collection', 'previous_run_original_34']:
    rows = inventory[name]
    bad = [path for path, row in rows.items() if sha(root / path) != (row['sha256'] if isinstance(row, dict) else row)]
    check(name, not bad, {'count': len(rows), 'bad': bad})
check('旧清单自身未改', sha(inventory['previous_run_original_34_inventory_path']) == inventory['previous_run_original_34_inventory_sha256'])
before = read(run / 'source_before.json')
after = read(run / 'source_after.json')
check('28 源码前后原始绑定一致', before['sources'] == after['sources'] and len(before['sources']) == 28 and before['source_commit'] == baseline)
source_rows = []
for row in before['sources']:
    data = (run / 'source_snapshot' / row['path']).read_bytes()
    blob = subprocess.run(['git', 'show', baseline + ':' + row['path']], cwd=root, capture_output=True)
    raw = blob.returncode == 0 and data == blob.stdout
    eol = blob.returncode == 0 and b'\r\n' not in blob.stdout and blob.stdout.replace(b'\n', b'\r\n') == data
    source_rows.append({**row, 'git_blob_sha256': hashlib.sha256(blob.stdout).hexdigest(), 'git_exit_code': blob.returncode, 'raw_same': raw, 'exact_lf_to_crlf': eol})
    check('源码 ' + row['path'], hashlib.sha256(data).hexdigest() == row['sha256'] and len(data) == row['bytes'] and (raw or eol))
check('24 RAW 相同及 4 精确换行关系', sum(row['raw_same'] for row in source_rows) == 24 and sum(not row['raw_same'] and row['exact_lf_to_crlf'] for row in source_rows) == 4)
frozen_path = root / 'report/evidence/S2A-T68/g4_synthesis_20261005/candidate8x8_core_ooc_run01_20261006/source_manifest.json'
frozen = read(frozen_path)
frozen_rows = []
for row in frozen['rtl_sources']:
    data = (run / 'source_snapshot' / row['relative_path']).read_bytes()
    blob = subprocess.run(['git','show','671f9cf494b92ce182b3f1542fefd0cfd4b209f5:' + row['relative_path']],cwd=root,capture_output=True)
    frozen_rows.append({'path':row['relative_path'],'frozen_commit':'671f9cf494b92ce182b3f1542fefd0cfd4b209f5','frozen_blob_sha256':hashlib.sha256(blob.stdout).hexdigest(),'historical_999_manifest_sha256':row['sha256']})
    check('最终冻结 2A 源 ' + row['relative_path'], blob.returncode == 0 and (data == blob.stdout or b'\r\n' not in blob.stdout and data == blob.stdout.replace(b'\n',b'\r\n')))
execute('frozen14_worktree_diff', ['git','diff','--exit-code','671f9cf494b92ce182b3f1542fefd0cfd4b209f5','--'] + [row['relative_path'] for row in frozen['rtl_sources']], 0)
mapping = read(run / 'collector_native_archive_mapping.json')
bad = []
for row in mapping['files']:
    if sha(row['original_path']) != row['sha256'] or sha(root / row['saved_path']) != row['sha256']:
        bad.append(row['saved_path'])
check('5 native job 的 44 原件逐字节绑定', len(mapping['files']) == 44 and len(mapping['jobs']) == 5 and not bad, bad)
for job in mapping['jobs']:
    folder = run / 'native_jobs' / job['saved_directory']
    log = (folder / 'runme.log').read_text(encoding='utf-8')
    peak = max(map(float, re.findall(r'peak = ([0-9.]+)', log)))
    elapsed = re.search(r'synth_design:.*?elapsed = (\d+):(\d+):(\d+)', log)
    seconds = int(elapsed[1]) * 3600 + int(elapsed[2]) * 60 + int(elapsed[3])
    check('native 成功 ' + job['run'], 'synth_design completed successfully' in log and '0 Critical Warnings and 0 Errors encountered' in log and (folder / '.vivado.end.rst').is_file() and (folder / '__synthesis_is_complete__').is_file() and not (folder / '.vivado.error.rst').exists() and peak == job['single_process_reported_peak_mb'] and seconds == job['synth_design_elapsed_seconds'] and job['raw_process_exit_code'] is None)
for row in mapping['dcp_references']:
    check('DCP 仅缓存 ' + Path(row['path']).name, sha(row['path']) == row['sha256'] and row['permanent_artifact'] is False)
profile = read(run / 'source_snapshot/board/s2b_inference_platform.json')
native_tcl = (run / 'native_jobs/s2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl').read_text(encoding='utf-8')
block = re.search(r'read_verilog -library xil_defaultlib -sv \{([^}]+)\}', native_tcl)[1]
native_inputs = [Path(line.strip()).relative_to(root).as_posix() for line in block.splitlines() if line.strip()]
check('实际 native 18 RTL 与固定 profile 闭包', len(native_inputs) == 18 and set(native_inputs) == set(profile['rtl_sources']) == set(mapping['native_rtl_inputs']) and all(path in {r['path'] for r in before['sources']} for path in native_inputs))
raw = read(run / 'root_mcp_calls.json')
history = json.loads(raw['history']['content'][0]['text'])['history']
check('原始 MCP 字节与 base64', (run / 'root_mcp_calls.json').read_bytes() == base64.b64decode((run / 'root_mcp_calls.json.b64').read_bytes()))
check('真实 history 55—64', [row['id'] for row in history] == list(range(55, 65)))
check('UTF8 重载与系统设置原命令', history[1]['command'].startswith('source -encoding utf-8 -notrace ') and history[2]['command'].startswith('encoding system utf-8;') and history[1]['code'] == history[2]['code'] == 0)
wait = next(row for row in history if row['command'] == 'wait_on_run synth_1')
mc = read(run / 'collector_mcp_classification.json')
check('即时 wait 与累计峰值限制', wait['code'] == 0 and wait['elapsed'] == 0.046 and mc['wait_is_not_synthesis_wall_runtime'] is True and mc['process_tree_peak_memory'] == 'NOT_MEASURED')
products = (run / 'products.tcldict').read_text(encoding='utf-8')
check('capture 失败及 native 成功分别保留', 'status FAIL code 0' in products and 'native_counts_before {WARNING 9' in products and 'native_counts_after {WARNING 1' in products and history[3]['code'] == 1)
snap = root / mc['root_session_log']['snapshot_path']
check('原追加日志前缀绑定', Path(mc['root_session_log']['original_path']).read_bytes()[:snap.stat().st_size] == snap.read_bytes() and sha(snap) == mc['root_session_log']['snapshot_sha256'])
x = read(run / 'collector_xsa_member_comparison.json')
with zipfile.ZipFile(root / x['new_xsa_path']) as new, zipfile.ZipFile(root / x['compiled_old_xsa_path']) as old:
    check('双 XSA ZIP CRC', new.testzip() is None and old.testzip() is None)
    for row in x['members']:
        a, b = old.read(row['member']), new.read(row['member'])
        check('XSA 成员 ' + row['member'], (a == b) == row['raw_byte_identical'] and hashlib.sha256(a).hexdigest() == row['old_sha256'] and hashlib.sha256(b).hexdigest() == row['new_sha256'] and old.getinfo(row['member']).CRC == row['old_crc32'] and new.getinfo(row['member']).CRC == row['new_crc32'])
build = read(root / x['old_actual_build_details_path'])
check('旧软件实际构建绑定旧 XSA', build['config']['xsa_sha256'] == build['xsa_sha256'] == x['compiled_old_xsa_sha256'] and Path(build['config']['xsa']) == root / x['compiled_old_xsa_path'] and any(row['name'] == 'platform.build' and row['return_repr'] == '0' for row in build['api_calls']) and any(row['name'] == 'app.build' and row['return_repr'] == '0' for row in build['api_calls']))
check('新旧整包区别', x['same_whole_xsa'] is False and sha(root / x['new_xsa_path']) != sha(root / x['compiled_old_xsa_path']))
timing = (run / 'timing_summary_synth.rpt').read_text(encoding='utf-8')
summary = timing.split('| Design Timing Summary', 1)[1].split('| Clock Summary', 1)[0]
line = next(line for line in summary.splitlines() if line.lstrip().startswith('-75.099')).split()
check('独立核对 STA 12 个汇总字段', line == ['-75.099','-117550.977','2636','14635','0.037','0.000','0','14635','8.870','0.000','0','4164'])
check('时钟及最坏路径', '20.000          50.000' in timing and 'Logic Levels:           237  (CARRY4=206' in timing and 'Data Path Delay:        94.695ns' in timing and 'layer_cursor_reg[0]/C' in timing and 'u_maxpool_engine/FSM_sequential_state_reg[0]/D' in timing)
check('内部约束覆盖及无有效例外', 'checking unconstrained_internal_endpoints (0)' in timing and 'No valid timing exceptions found.' in (run / 'exceptions_synth.rpt').read_text(encoding='utf-8'))
check('实际 native 可见性参数为 0', "Parameter PROFILE_VISIBILITY_PROVEN bound to: 1'b0" in (run / 'native_jobs/s2b_inference_infer_0_synth_1/runme.log').read_text(encoding='utf-8') and before['visibility'] == after['visibility'] == 0 and before['platform_version'] == after['platform_version'] == '0.1.1')
failure_log = (run / 'collector_failure_r01.log').read_text(encoding='utf-8')
check('保留首次采集 UTF8 错误原文', "UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc3 in position 33266" in failure_log and read(run / 'collector_failure_r01.json')['native_exit_code'] == 1)
util = (run / 'utilization_flat_synth.rpt').read_text(encoding='utf-8')
resources = {'Slice LUTs*':38427, 'Slice Registers':4000, 'Block RAM Tile':32, 'DSPs':173, 'Register as Latch':0}
for key, value in resources.items():
    match = re.search(r'\|\s*' + re.escape(key) + r'\s*\|\s*(\d+)\s*\|', util)
    check('资源 ' + key, match is not None and int(match[1]) == value)
for mode, expected in [('evidence',0),('inputs',2)]:
    execute('packaging_' + mode, [sys.executable,'-B','verification/check_stage_delivery.py','--mode',mode,'--manifest',str(manifest)], expected)
execute('sta_classifier', [sys.executable,'-B',str(run / 'collector_classify_sta.py')], 2)
check('收尾清单冻结哈希仍一致', sha(manifest) == expected_manifest)
receipt = {'status':'PASS_EVIDENCE_INTEGRITY' if all(row['status'] == 'PASS' for row in checks) else 'CHANGES_REQUIRED','scope':'仅 S1 证据完整性与分类；不批准时序、实现、位流、缓存恢复、G3/G4/G5','source_commit':baseline,'manifest_path':str(manifest),'manifest_sha256':sha(manifest),'checked_at_utc8':datetime.now(timezone(timedelta(hours=8))).isoformat(),'elapsed_seconds':time.monotonic()-started,'peak_memory':'NOT_MEASURED','heavy_jobs':0,'MCP_calls':0,'project_mutations':0,'source_rows':source_rows,'frozen_2a_sources':frozen_rows,'review_rerun_note':'初始76项通过；额外核验最初误以历史999 OOC清单作为最终14源冻结基线，发现top不同后按STATE实际冻结671f9cf重新独立比较并修正检查脚本。该误判不涉及被审证据修改。','checks':checks,'commands':commands,'old_actual_build_details':build}
(out / 'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':receipt['status'],'checks':len(checks),'failed':[row for row in checks if row['status']!='PASS'],'elapsed_seconds':receipt['elapsed_seconds'],'receipt_sha256':sha(out / 'receipt.json')},ensure_ascii=False,indent=2))
sys.exit(0 if receipt['status']=='PASS_EVIDENCE_INTEGRITY' else 2)
