"""只纠正首版Collector额外FAIL计数假设，并复核已审绑定未漂移。"""
import copy
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import review_r02 as audited

parent = Path(__file__).resolve().parent
out = parent / 'r03'
started = time.monotonic()
manifest = audited.read(audited.BASE / 's6_collection_delivery_manifest_r02.json')
audited.require(audited.sha((audited.BASE / 's6_collection_delivery_manifest_r02.json').read_bytes()) == audited.MANIFEST_SHA,
                'r02以后业务清单改变')
for row in manifest['files'] + manifest['interfaces']:
    audited.binding(row)
previous_path = parent / 'r02/receipt.json'
previous = audited.read(previous_path)
audited.require(previous['reviewed_source_commit'] == audited.COMMIT
                and previous['reviewed_manifest_sha256'] == audited.MANIFEST_SHA
                and len(previous['checks']) == 9, '已审版本不符')
audited.require([i for i, r in enumerate(previous['checks']) if r['status'] != 'PASS'] == [6]
                and previous['checks'][6]['error'] == "AssertionError('FAIL改判PASS')", '关闭范围超出唯一Reviewer假设问题')
commands = audited.read(parent / 'r02/native_commands.json')
audited.require(commands['count'] == len(commands['commands']) == 42, '真实native命令记录不全')
for item in commands['commands']:
    audited.require(isinstance(item['command'], list) and isinstance(item['native_exit_code'], int), 'native格式错误')
    expected_code = 2 if item['label'] in {'checker_inputs', 'classifier_original'} else 0
    audited.require(item['native_exit_code'] == expected_code, '复用命令原生码错误')
    for stem in ['stdout', 'stderr']:
        if stem + '_path' in item:
            raw = audited.exact(audited.ROOT / item[stem + '_path']).read_bytes()
            audited.require(audited.sha(raw) == item[stem + '_sha256'] and len(raw) == item[stem + '_bytes'], '独审原始输出漂移')
source_binding = audited.read(audited.BASE / 's6_collection_source_binding.json')
for i, row in enumerate(source_binding['sources']):
    item = next(c for c in commands['commands'] if c['label'] == 'git_source_%02d' % i)
    audited.require(item['command'] == ['git', 'show', audited.COMMIT + ':' + row['path']]
                    and item['stdout_sha256'] == row['git_blob_sha256'], '复用Git命令/原输出不符')
audited.require(previous['details']['independent_native']['evidence'] == 0
                and previous['details']['independent_native']['inputs'] == 2
                and previous['details']['independent_native']['classifier'] == 2
                and len(previous['details']['counterexamples']) == 7
                and all(c['status'] == 'EXPECTED_REJECTION' for c in previous['details']['counterexamples']), '复用r02检查或反例状态错误')
expected = {'50MHz综合态STA分类': 2, 'builder与products捕获原失败': 1,
            '首版Collector原失败': 1, '已关闭inputs依赖检查': 2}
actual = {r['name']: r['exit_code'] for r in manifest['checks'] if r['status'] == 'FAIL'}
audited.require(actual == expected, '四项真实失败状态/原生码不符')
notrun = [r for r in manifest['checks'] if r['status'] == 'NOT_RUN']
audited.require(len(notrun) == 7 and all(r['command'] is None and r['exit_code'] is None for r in notrun), 'NOT_RUN被改判成功')
execution = audited.read(audited.BASE / 's6_collection_execution_receipt.json')
audited.require(audited.sha((audited.BASE / 's6_collection_execution_receipt.json').read_bytes()) == audited.FINAL_SHA
                and execution['status'].startswith('STOP_S6_FAIL_TIMING'), '原Collector STOP版本变化')
codes = {}
for stem, code in [('s6_collection_collector', 1), ('s6_collection_collector_r02', 0), ('s6_collection_sta', 2),
                   ('s6_collection_evidence_r01', 0), ('s6_collection_inputs_r01', 2)]:
    record = audited.read(audited.BASE / (stem + '.native.json'))
    audited.require(record['native_exit_code'] == code, '原native码漂移')
    for row in record['closed_logs']:
        audited.binding(row)
        original = audited.BASE / Path(row['path']).name
        audited.require(audited.sha(original.read_bytes()) == row['sha256'], '原生日志正式副本错误')
    codes[stem] = {'native_exit_code': code, 'elapsed_seconds': record['elapsed_seconds']}
error = (audited.BASE / 's6_collection_collector.stderr.log').read_text(encoding='utf-8')
audited.require("KeyError: 'input'" in error and "call['input']['command']" in error, '首失败未保留')
preview = audited.read(audited.BASE / 's6_collection_preview_diagnostic.json')
audited.require(preview['host_tool_exit_code'] == 1 and preview['native_exit_code'] is None
                and preview['raw_log_modified'] is False and preview['stdout_raw_complete'] is False
                and preview['stderr_raw_complete'] is False, '辅助预览native或raw完整度伪填')
classifier = audited.read(audited.BASE / 's6_collection_sta_checker_binding.json')
audited.require(classifier['requested_native_exit_code'] is None
                and not (audited.ROOT / classifier['requested_identifier']).exists(), '原错误路径事实错误')
audited.require(audited.binding(classifier['actual_classifier_snapshot']) == audited.binding(classifier['actual_classifier_original']),
                '实际分类器字节改变')
summary = audited.read(audited.BASE / 's6_collection_summary_final.json')
audited.require(summary['collector_native_exit_code'] == 0 and summary['first_collector_native_exit_code'] == 1
                and summary['native_classifier_exit_code'] == 2 and summary['closed_packaging_codes'] == {'evidence': 0, 'inputs': 2},
                '实际FAIL/包装结果混淆')
receipt = copy.deepcopy(previous)
receipt['status'] = 'PASS_EVIDENCE_INTEGRITY_ONLY'
receipt['created_at_utc8'] = datetime.now(timezone(timedelta(hours=8))).isoformat()
receipt['checks'][6] = {'name': '首collector/辅助preview/分类路径/NOT_RUN', 'status': 'PASS',
                      'elapsed_seconds': time.monotonic() - started,
                      'reason': '四条FAIL分别STA2、builder1、首Collector1、inputs2；不存在改判成功。'}
receipt['details']['preserved_failures'] = {'native_codes': codes, 'manifest_failures': actual,
    'first_failure': "KeyError('input')", 'aux_preview_host_exit_code': 1, 'aux_preview_native_exit_code': None,
    'actual_classifier': classifier['actual_classifier_snapshot'], 'not_run_names': [r['name'] for r in notrun],
    'collector_execution_receipt_sha256': audited.FINAL_SHA}
receipt['modification_scope'] = out.relative_to(audited.ROOT).as_posix()
receipt['prior_reviewer_failures'] = [
    {'run': 'r01', 'native_exit_code': 1, 'classification': 'Reviewer生成正则语法错误，未执行证据核查。',
     'native_sha256': audited.sha((parent / 'review.native.json').read_bytes())},
    {'run': 'r02', 'native_exit_code': 2, 'classification': 'Reviewer沿用S5三FAIL计数；S6首Collector另有一FAIL。',
     'native_sha256': audited.sha((parent / 'r02/review.native.json').read_bytes()),
     'receipt_sha256': audited.sha(previous_path.read_bytes())}]
receipt.pop('prior_reviewer_failure', None)
receipt['incremental_review'] = {'prior_run': 'r02', 'passed_groups_reused': 8,
    'closed_group': 6, 'all_315_file_and_2_interface_bindings_rechecked': True,
    'prior_native_command_count': 42, 'prior_counterexamples': 7,
    'reason': '固定Git对象和315原件绑定未变；无需重复已经通过的Git/报告/反例。'}
receipt['closure_elapsed_seconds'] = time.monotonic() - started
receipt['reviewer_closure_process_memory'] = audited.memory_peak(os.getpid())
target = out / 'receipt.json'
audited.require(not target.exists(), '禁止覆盖独审最终receipt')
target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': receipt['status'], 'execution_state': 'STOP', 'groups': 9,
                  'counterexamples': 7, 'native_commands': 42, 'closure_elapsed_seconds': receipt['closure_elapsed_seconds']}, ensure_ascii=False))
