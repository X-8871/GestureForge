"""只读复核交付绑定并生成独立审查收据，不批准任何板上验收。"""
import ast
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).absolute().parent
ROOT = OUT.parents[3]
def sha(path):
    """原始字节摘要，不转换换行。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
def path_check(path):
    """逐组件核验类型与无重解析，不接受隐藏路径替换。"""
    for part in reversed([path, *path.parents]):
        stat = part.lstat()
        assert not (getattr(stat, 'st_file_attributes', 0) & 0x400), str(part)
    assert path.is_file(), str(path)

frozen = {
    'verification/s2b_csr_board_acceptance.py': 'c494a2ce720908e7e4efcee5aa161db54aef00045b4611ba7145d7f4b2752328',
    'verification/test_s2b_csr_board_acceptance.py': 'd97872259c9328e005cebad3bd3fb5718bf42675df005eb87c4413522a589d02',
    'report/evidence/S2B-T20/csr_acceptance_20261011_r01/delivery_manifest_r03.json': '1242a79a343a458ba6d43de93aaec151fef3a07a9aa7b45ca15bb4af51ec24a2'}
for relative, expected in frozen.items():
    path_check(ROOT / relative)
    assert sha(ROOT / relative) == expected, relative
manifest = json.loads((ROOT / list(frozen)[2]).read_text(encoding='utf-8'))
bindings = []
for item in manifest['files'] + manifest['interfaces']:
    path = ROOT / item['path']; path_check(path)
    actual = sha(path)
    bindings.append({'path': item['path'], 'expected_sha256': item['sha256'],
                     'actual_sha256': actual, 'match': actual == item['sha256']})
assert all(item['match'] for item in bindings), bindings
comments = []
for relative in list(frozen)[:2]:
    source = (ROOT / relative).read_text(encoding='utf-8')
    tree = ast.parse(source)
    strings = [ast.get_docstring(node) for node in ast.walk(tree) if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))]
    assert all(any('\u4e00' <= char <= '\u9fff' for char in value) for value in strings if value)
    comments.append({'path': relative, 'docstrings_have_chinese': True})
platform_path = ROOT / 'verification/check_s2b_inference_platform.py'
native = {}
for name in ('offline_native.json', 'offline_r02_native.json', 'prior_native.json', 'outstanding_native.json', 'nonempty_native.json', 'nonempty_r02_native.json', 'nonempty_r03_native.json'):
    native[name] = json.loads((OUT / name).read_text(encoding='utf-8'))
suite = json.loads((OUT / 'offline_suite_result_r02.json').read_text(encoding='utf-8'))
artifacts = []
for path in sorted(OUT.rglob('*')):
    if path.is_file():
        path_check(path)
        artifacts.append({'path': str(path.relative_to(OUT)), 'sha256': sha(path), 'bytes': path.stat().st_size})
receipt = {
    'schema_version': 1, 'task': 'S2B-T20', 'review_round': 1, 'status': 'CHANGES_REQUIRED',
    'finished_at_utc8': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'source_commit_g1': manifest['source_commit'],
    'observed_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'head_change_reason': '根代理仅提交T19；T20两源码与G1清单原始摘要未变',
    'frozen_raw_sha256': frozen, 'manifest_binding_recheck': bindings,
    'scope': ['T11 RTL与物理候选0.1.1的START/SLVERR、参数优先级、epoch、ACK静止矩阵',
              'owner/ledger/两核停止/scene/visibility1证明与产物绑定门禁及未知SDK异常不冒称SLVERR',
              'short_deadline真实候选观测与合法隔离、显式ACK；旧PS会话热恢复BLOCKED',
              'T16真实格式WAIT/final/abort错误码8及账本0、mode3 ACK、T18双头和全部框检查',
              '实际WireSession MOCK发送/receipt/raw解析的模型前置门禁反例；独立中心单框手算'],
    'findings': [{'priority': 'P2', 'file': 'verification/s2b_csr_board_acceptance.py',
        'lines': [156, 173], 'title': '历史LOAD与最后响应不能证明当前已消费的模型状态',
        'cause': 'accepted_weights用历史OR累计；最后RUN仅比UART接收尾部，未要求最后发送请求已消费且为该RUN。',
        'impact': '旧正确LOAD后成功接受替代权重仍允许abort/recovery；成功seed RUN后已发送未消费LOAD也允许入口再发DIAG，当前模型/请求因果前置不成立。',
        'evidence': ['prior_state_counterexample.json', 'outstanding_request_counterexample.json'],
        'physical_basis': 'vitis/s2b_inference_app.c:442-446每次成功OP_WEIGHTS均覆盖arena，不能用早期LOAD代表当前权重。',
        'close_conditions': ['按实际发送及完整receipt顺序重放，最后有效LOAD的payload身份必须匹配冻结plan，且位于该seed RUN之前。',
            '最后发送请求必须就是最后完整成功seed RUN，无未消费的后续请求；核对实际sequence/frame/payload/epoch及UART原字节，不仅字典元数据。',
            '两反例拒绝；正常正确LOAD+最终seed RUN继续通过；不修改wire epoch、不清除failstop、不伪造compat或板上PASS。']}],
    'native_commands': native, 'offline_suite': suite,
    'additional_results': ['prior_state_counterexample.json', 'outstanding_request_counterexample.json', 'nonempty_golden_result_r03.json'],
    'review_harness_failures': ['offline首轮因TemporaryDirectory位置dir与封装kwargs冲突；修复仅隔离封装后22项通过，原失败保留。',
        '非空框首轮手算记录使用name而正式schema要求class_name；诊断后修正仅审查脚本。',
        '非空框r02上调score超过1先被运输检查拒绝；r03改为范围内下调0.01，明确被全部框黄金检查拒绝。'],
    'resource_limits': {'budget_bytes': 300 * 1024 * 1024,
        'observed_suite_peak_working_set_bytes': suite['single_process_peak_working_set_bytes'],
        'extra_counterexamples_peak_memory_bytes': None, 'extra_peak_note': '未单独采样峰值；顺序执行小型MOCK，无SDK/重型工具。',
        'process_tree_peak_bytes': None},
    'language': comments,
    'platform_checker_current_raw_sha256': sha(platform_path),
    'platform_checker_scope': '仅记录当前S3并行工作版本；不把该版本称T20已验证STA/ROM/bit，不执行完整runtime preflight。',
    'limitations': ['BOARD_NOT_RUN；无SDKSession/connect/Serialopen/server/实板/ROSS/重型任务。',
        '根代理尚未创建正式109实板prepare；仅冻结模型与T18资产校验静态检查，MOCK不能代表实际输入或板上黄金。',
        '非空框手算只MOCK：验证计划和外层生产入场被测试替身替代，生产恢复/T16/Wire/T18全框检查实际执行。',
        '自然推进busy BLOCKED；short_deadline同旧PS软件热恢复BLOCKED；G2不能替代G3/fullcompat/finalbit/visibility批准。'],
    'artifacts': artifacts, 'project_sources_modified': False, 'git_commit_created': False, 'reviewer_write_state': 'STOP_AFTER_RECEIPT'}
with (OUT / 'review_receipt.json').open('x', encoding='utf-8') as handle:
    json.dump(receipt, handle, ensure_ascii=False, indent=2)
print(json.dumps({'status': receipt['status'], 'receipt_sha256': sha(OUT / 'review_receipt.json'),
                  'g1_bindings': len(bindings), 'artifact_count': len(artifacts), 'head': receipt['observed_head']}, ensure_ascii=False))
