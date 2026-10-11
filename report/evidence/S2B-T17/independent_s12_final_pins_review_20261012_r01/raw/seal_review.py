"""独立审查收尾，只核原件并冻结本隔离目录的回执和RAW索引。"""
import hashlib
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from audit import EXPECTED, COMMIT

OUT = pathlib.Path(__file__).absolute().parent
ROOT = OUT.parents[3]
PACK = ROOT / 'report/evidence/S2B-T17/s12_source_preflight_20261012_r02'
WORK = ROOT / 'tmp/2B/S2B-T17/s12_physical_final_prepare_20261012_r02'

def sha(path):
    """精确原字节流式绑定。"""
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()

def read(path):
    """UTF8读取本轮核查结果。"""
    return json.loads(path.read_text(encoding='utf-8'))

def binding(path):
    """为冻结文件记录路径、SHA及长度。"""
    return {'path': str(path), 'sha256': sha(path), 'bytes': path.stat().st_size}

def save(path, value):
    """仅创建本独立目录的新目标。"""
    assert path.parent == OUT and not path.exists()
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')

inputs = []
for name, expected in EXPECTED.items():
    assert sha(PACK / name) == expected
    inputs.append(binding(PACK / name))
freeze = read(PACK / 'source_freeze.json')
for row in freeze['source_files']:
    actual = ROOT / row['path']
    snapshot = ROOT / row['snapshot']
    assert actual.stat().st_size == snapshot.stat().st_size == row['bytes']
    assert sha(actual) == sha(snapshot) == row['sha256']
tools = read(PACK / 'tool_binding.json')['tools']
for row in tools:
    assert sha(WORK / row['path']) == row['sha256']
command = ['git', '-c', 'core.longpaths=true', '-c', 'maintenance.auto=false', 'rev-parse', 'HEAD']
process = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=30)
assert process.returncode == 0 and process.stdout.decode('ascii').strip() == COMMIT
save(OUT / 'postcheck.json', {'status': 'PASS_POST_REVIEW_BYTES_AND_HEAD', 'command': command, 'native_exit_code': process.returncode, 'actual_head': process.stdout.decode('ascii').strip(), 'source_count': 43, 'six_tools_unchanged': True, 'eight_frozen_inputs_unchanged': True})
rows = [binding(path) for path in sorted(OUT.rglob('*')) if path.is_file()]
with (OUT / 'raw_index.jsonl').open('x', encoding='utf-8', newline='\n') as f:
    for row in rows:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')
audit = read(OUT / 'audit_result_r02.json')
supplement = read(OUT / 'supplement_result.json')
receipt = {
    'schema_version': 1,
    'task_id': 'S12-FINAL-PINS-G2-R01',
    'status': 'PASS_FINAL_PINS_G2_ONLY',
    'stop': True,
    'created_at_utc8': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'source_commit': COMMIT,
    'actual_head_at_final_check': COMMIT,
    'runtime': {'model': 'gpt-6.1-sol', 'reasoning_effort': 'high', 'basis': 'ROOT创建的本agent实际配置；本轮未更改参数'},
    'reviewed_work_directory': str(WORK),
    'formal_package': str(PACK),
    'frozen_input_bindings': inputs,
    'tools': tools,
    'independent_results': {'manifest_bindings': audit['manifest_bindings'], 'original_restore_rows': audit['restore_rows'], 'deduplicated_saved_objects': audit['restore_objects'], 'source_count': 43, 'static_count': 33, 'active_rtl_count': 18, 'derived_count': 8, 'original14_count': 14, 'git_relations': audit['git_relations'], 'actual_serial_git_calls_in_successful_audit': len(audit['git_commands']), 'gate_cases': len(audit['cases']), 'case_details': audit['cases'], 'helper_function_ast_unchanged': True, 'other_five_tools_raw_unchanged_from_reviewed_compat_r02': True, 'changed_helper_top_level_constants': supplement['changed_top_level_assignments']},
    'upstream_compat_basis': {'manifest_sha256': supplement['compat_manifest_sha256'], 'review_receipt_sha256': supplement['compat_review_receipt_sha256'], 'status': supplement['compat_review_status'], 'reviewed_file_sha_matches': True, 'scope': '只核既有独审来源和五文件字节继承；未复跑6404条归档或完整旧COMPAT测试'},
    'native_records': [read(OUT / name) for name in ('audit.native.json', 'audit_r02.native.json', 'supplement.native.json', 'checker_evidence.native.json', 'checker_inputs.native.json')],
    'developer_native_evidence': supplement['developer_tests'],
    'reviewer_first_failure': {'native_exit_code': 1, 'location': 'audit.py:174', 'cause': 'Reviewer误用compat_pins.sha属性；实际helper没有此函数。', 'closure': '新audit_r02仅改为模拟_LOADED_HELPER_SHA漂移并使用新Git/输出落点；native0。', 'original_script_and_trace_preserved': True},
    'historical_failures_preserved': supplement['historical_failures'],
    'plan_resource_values_verified': supplement['resources_verified'],
    'functional_contract': audit['plan_contract'],
    'findings': [],
    'version_role_clarification': [
        '综合collector.source before/after严格SOURCE_COMMIT==CLI==实际HEAD09b4；ROOT保持该HEAD至本轮综合source-after与自有实验闭合。',
        '后续PNR沿已审COMPAT原逻辑，实际metadata HEAD与显式expected-head相等；immutable SOURCE_COMMIT09b4、全部43 RAW及其Git对象独立保留。未要求PNR元数据HEAD永久09b4。',
        'PNR SYNTH_MANIFEST/SYNTH_G2仍None/PENDING且实际门禁拒绝；未来补入真实综合manifest/G2/实际metadata HEAD后须重新冻结和独审。',
        'source_freeze内r01 snapshot与Git原件是来源角色，本轮helper实际读取r02/source_freeze，SHA及43 snapshot均核真。'
    ],
    'physical_admission': {'status': 'BLOCKED', 'frozen_sample': audit['admission_sample'], 'note': 'RAM3994320896B低于4831838208B启动门槛；本回执不授权跨过资源门槛，ROOT须实际启动前重新核准入。'},
    'remaining_status': {'physical_g0': 'BLOCKED_PENDING_ACTUAL_RESOURCE_ADMISSION', 'source_after': 'NOT_RUN', 'new_owned_session_log': 'NOT_RUN_ACTUAL_SESSION_NOT_CREATED', 'synthesis': 'NOT_RUN', 'pnr': 'NOT_RUN_PENDING_SYNTH_G2', 'actual_heavy_budget': 'NOT_RUN', 'sta': 'NOT_RUN', 'g3': 'NOT_RUN', 'g5': 'NOT_RUN', 'old_s11_budget': 'BLOCKED'},
    'raw_index': binding(OUT / 'raw_index.jsonl'),
    'raw_index_file_count': len(rows),
    'raw_index_scope': '全部已完成独立脚本/RAW日志/Git原件/核查JSON；不包含随后生成的本receipt及seal，二者由seal单独绑定。被审大包与原件按固定SHA引用，未在本目录复制。',
    'limitations': [
        '只批准最终pins逻辑G2和物理输入准备，不代表实际物理G0、预算、STA、109模型/1000连续实板或2B阶段通过。',
        '独立采样峰134877184B/0.02秒/UNKNOWN1，连续OS原子绝对树峰null；不是重型资源预算PASS。',
        'Developer真实before native0/6.031秒/采样峰128966656B/UNKNOWN1属于新256MiB轻量capture；旧128MiB宿主1/child null不追认。',
        '旧S11 PNR失败及预算BLOCKED继续保留，未调用Vivado/ROSS/硬件或重型仿真。',
        '未修改任何被审/生产/Git/STATE，无Reviewer提交；code提交由ROOT负责。',
        '机器evidence0只验证绑定；inputs2包含NOT_RUN/BLOCKED及旧precheck FAIL，未把它改写为物理准入通过。'
    ]
}
save(OUT / 'final_review_receipt.json', receipt)
seal = {'status': 'STOP_FROZEN_REVIEW', 'receipt': binding(OUT / 'final_review_receipt.json'), 'raw_index': binding(OUT / 'raw_index.jsonl'), 'raw_files': len(rows), 'source_commit': COMMIT}
save(OUT / 'seal.json', seal)
print(json.dumps(seal, ensure_ascii=False))
