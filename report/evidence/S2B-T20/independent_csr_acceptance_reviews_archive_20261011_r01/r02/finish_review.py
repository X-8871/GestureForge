"""生成R2独立软件审查收据；不盖过板上、冻结接口及旧会话恢复阻断。"""
import ast
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).absolute().parent
ROOT = OUT.parents[3]
def binding(path):
    """精确路径逐组件核验后绑定原字节摘要。"""
    for item in reversed([path, *path.parents]):
        assert not getattr(item.lstat(), 'st_file_attributes', 0) & 0x400, str(item)
    assert path.is_file(), str(path)
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}

frozen = {
    'verification/s2b_csr_board_acceptance.py': 'b26a3cfaa9e7ecc5d901339b9edd85ba342a29d3a88930981096390c7309aa8a',
    'verification/test_s2b_csr_board_acceptance.py': 'ba273b2c0dd86d22de20685ab51a2ec065bfd7d9c345b2c70fcbed86f6569126',
    'report/evidence/S2B-T20/csr_acceptance_20261011_r03/delivery_manifest_r02.json': 'b13f49452e788e5ca6d7843addf0b2f9cba420edaa3cd79c189455740448379f'}
for relative, wanted in frozen.items():
    assert binding(ROOT / relative)['sha256'] == wanted, relative
manifest = json.loads((ROOT / list(frozen)[2]).read_text(encoding='utf-8'))
rechecked = []
for item in manifest['files'] + manifest['interfaces']:
    current = binding(ROOT / item['path'])
    assert current['sha256'] == item['sha256'], item['path']
    rechecked.append(current)
old_receipt = binding(ROOT / 'tmp/2B/S2B-T20/independent_csr_acceptance_review_20261011_r01/review_receipt.json')
assert old_receipt['sha256'] == '97f7479abe00e0d5463a7038b0fd0a7dd0a86e5288b27d1a5ba875e1d2b88b70'
old_source = ROOT / 'report/evidence/S2B-T20/csr_acceptance_20261011_r01/source_snapshot/s2b_csr_board_acceptance.py'
new_source = ROOT / 'verification/s2b_csr_board_acceptance.py'
def unaffected_ast(path):
    """确认语义修复范围，忽略行号和待关闭的单个函数。"""
    return [ast.dump(node, include_attributes=False) for node in ast.parse(path.read_text(encoding='utf-8')).body
            if not isinstance(node, ast.FunctionDef) or node.name != 'prior_model_success']
assert unaffected_ast(old_source) == unaffected_ast(new_source)
suite = json.loads((OUT / 'offline_suite_result_r02.json').read_text(encoding='utf-8'))
history = json.loads((OUT / 'independent_history_result.json').read_text(encoding='utf-8'))
nonempty = json.loads((OUT / 'nonempty_golden_result_r03.json').read_text(encoding='utf-8'))
prepared = json.loads((OUT / 'prepared_asset_result.json').read_text(encoding='utf-8'))
native = {name: json.loads((OUT / (name + '_native.json')).read_text(encoding='utf-8'))
          for name in ('suite', 'history', 'nonempty', 'prepared', 'evidence', 'inputs')}
assert [native[name]['native_exit_code'] for name in native] == [0, 0, 0, 0, 0, 2]
assert suite['single_process_peak_working_set_bytes'] < 300 * 1024 * 1024
receipt = {
    'schema_version': 1, 'role': 'INDEPENDENT_REVIEWER', 'task': 'S2B-T20', 'review_round': 2,
    'status': 'PASS', 'approval_scope': 'SOFTWARE_G2_ONLY',
    'finished_at_utc8': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'source_commit_g1': manifest['source_commit'],
    'observed_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'head_note': 'root证据提交改变HEAD，实际冻结T20两源码与G1清单均未变；不以HEAD变更冒称源码drift。',
    'frozen_raw_sha256': frozen, 'manifest_binding_recheck': rechecked,
    'previous_review_preserved': old_receipt,
    'closed_findings': [{'priority': 'P2', 'file': 'verification/s2b_csr_board_acceptance.py', 'lines': [147, 223],
        'title': '当前最后有效LOAD与最终已消费seed RUN的因果门禁',
        'proof': ['按sequence连续发送、逐请求TX/RX事件与完整receipt串行重放；TX磁盘headers及连续RX原件完整匹配。',
                  '每次响应重核request/header/payload/frame/CRC、TX计数与发送SHA、RX头/载荷SHA与meta及严格epoch；最后有效LOAD绑定当前权重。',
                  '最后实际发送且完整消费的请求须为sample000 frame0/640x480/repeat1 RUN；任何未消费后续请求或异步发送不放行。',
                  'R1正确LOAD被成功替代、seed RUN后未消费LOAD两原因按真实WireSession重演均拒绝；正常与重新恢复权重后的新seed RUN仍通过。'],
        'runtime_evidence': 'independent_history_result.json', 'remaining_findings': []}],
    'scope': ['33方法/30subcase离线全回归及11个独立真实WireSession MOCK历史案例',
              'R1静止19矩阵、非法START SLVERR/合法参数START epoch+1 ERROR_SAFE、ACK、owner/ledger/两核停止语义保持，prior之外AST一致',
              '新源实际执行T16 WAIT/final code8/账本0、mode3显式ACK、T18双头及非空手算全部框检查；范围内score下降0.01拒绝',
              '已存在root正式109 prepare、生产validate_plan、437项实际权重/input/reference/head逐组件无reparse及原始SHA只读核验',
              'G1清单evidence/inputs双模式与失败/NOT_RUN/BLOCKED状态保留'],
    'native_commands': native, 'suite_result': suite,
    'independent_history': history, 'nonempty_golden_mock': nonempty,
    'actual_prepared_assets': {'preparation': prepared['preparation'], 'rows': prepared['rows'],
        'bound_assets': len(prepared['files']), 'sample000': prepared['sample000'],
        'result_file': 'prepared_asset_result.json', 'board_execution': 'NOT_RUN'},
    'resources': {'budget_bytes': 300 * 1024 * 1024,
        'suite_peak_working_set_bytes': suite['single_process_peak_working_set_bytes'],
        'extra_case_peak_bytes': None, 'process_tree_peak_bytes': None,
        'note': '追加独立案例顺序执行；未独立采样各峰值，不把预算称实测峰值。未运行重型或SDK。'},
    'limitations': ['仅软件G2：BOARD NOT_RUN；无SDKSession/connect/Serialopen/server/ROSS/硬件操作。',
        '真实prepare绑定成功只证明冻结资产；实际109模型、bit/postroute/cache/fullcompat/visibility1/G3均不由本收据批准。',
        '自然推进busy明确BLOCKED；short_deadline同旧wire/PS软件热恢复明确BLOCKED；不做resync、epoch改写或failstop清除。',
        '非空手算仅MOCK，外层execute/validate_plan为明确测试替身；实际root prepare另外只读核验，未将MOCK充当实际sample000结果。',
        'evidence native0为包装核验，inputs native2因未冻结接口、历史失败、NOT_RUN和BLOCKED；不覆盖历史G1/R1失败。'],
    'project_sources_modified': False, 'old_artifacts_modified': False, 'git_commit_created': False,
    'reviewer_write_state': 'STOP_AFTER_RECEIPT',
    'artifacts': [binding(path) for path in sorted(OUT.rglob('*')) if path.is_file()]}
with (OUT / 'review_receipt.json').open('x', encoding='utf-8') as handle:
    json.dump(receipt, handle, ensure_ascii=False, indent=2)
print(json.dumps({'status': 'PASS', 'receipt_sha256': binding(OUT / 'review_receipt.json')['sha256'],
    'artifact_count': len(receipt['artifacts']), 'g1_bindings': len(rechecked),
    'source_unchanged': True, 'head': receipt['observed_head']}, ensure_ascii=False))
