"""固定独立审查结论与原件索引，保留阻断及原生限制。"""
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone, timedelta

HERE = Path(__file__).parent
ROOT = HERE.parents[3]
WORK = ROOT / 'tmp/2B/S2B-T17/s15_launch_prepare_20261012_r01'
PACKAGE = ROOT / 'report/evidence/S2B-T17/s15_launch_tools_20261012_r01'

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def row(path):
    return dict(path=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size)

def save(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')

probe = read(HERE / 'review_probe_result.json')
audit = read(HERE / 'evidence_audit_result_r02.json')
original = read(PACKAGE / 'g1_receipt.json')
unchanged = all(row(ROOT / r['path'])['sha256'] == r['sha256'] for r in original['tools'])
native = read(HERE / 'review_native_canary.native.json')
receipt = dict(
    status='CHANGES_REQUIRED',
    created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),
    baseline_commit=probe['baseline_head'],
    reviewed_manifest=row(PACKAGE / 'delivery_manifest.json'),
    reviewed_g1_receipt=row(PACKAGE / 'g1_receipt.json'),
    reviewed_tools=original['tools'],
    reviewed_tools_unchanged_at_stop=unchanged,
    stop=True,
    tool_g2_pass=False,
    production_source_function_g2='NOT_REVIEWED',
    actual_s15_runtime='NOT_RUN',
    actual_s15_sta='NOT_RUN',
    actual_continuous_budget='NOT_PROVEN',
    g3_g4_g5='NOT_RUN',
    checks=22,
    passed_checks=17,
    failed_counterexamples=5,
    findings=[
        dict(priority='P1', path='tmp/2B/S2B-T17/s15_launch_prepare_20261012_r01/collector.py', start=216, end=238,
             title='原生记录缺失或矛盾身份与工具metadata仍接受',
             impact='runtime_native_records对缺launcher/direct_child/tool字段、child出生早于launcher且ppid错误、工具前后哈希不同、budget_stop非空但child code0的记录均返回成功；seal第422行仅按child code0标PASS，可掩盖包装失败或未核来源。',
             evidence_cases=['reject_missing_identity_and_tool_metadata', 'reject_wrong_parent_birth', 'reject_tool_hash_changed', 'reject_budget_stop_with_child_rc0'],
             closure='验证完整真实metadata结构、六字段身份及直接父PID/出生时间关系、完整wrapper与child命令、实际cwd、前后工具集合/冻结SHA一致、日志精确各自路径/字节和真实直接wait。缺字段与矛盾值必须阻断；未知和失败原件保留并分别列状态，budget_stop/包装失败不得因child0变为PASS。使用非fixture真实capture记录为正向；禁止给缺字段fixture当实际G2通过。'),
        dict(priority='P1', path='tmp/2B/S2B-T17/s15_launch_prepare_20261012_r01/collector.py', start=231, end=406,
             title='collect完整argv及实际关闭gate来源未绑定',
             impact='仅command前六项一致即可接受collect，错误--commit和其他--gate均成功。seal只核summary.source_commit及任一collect0，未绑定summary.root_gate到实际被consume的关闭原件，因此不能证明该collect产自本轮闭合输入。',
             evidence_cases=['reject_wrong_collect_commit_gate'],
             closure='严格解析无重复或额外参数的完整source/collect命令与phase、commit、实际所消费gate原字节绑定；核collect summary.root_gate及SOURCE/config/MCP九命令/闭合原件来自该gate。真实顺序是collect消费不可覆写gate_r01，完成后seal消费新gate_r02增补已闭合collect wrapper；允许明确的native列表扩展等有证据差异并核其上游字段语义一致，不能机械要求两gate路径相同或回写oldgate。补完整有效链正向、wrong gate/SOURCE/config/MCP/原件差异负向。'),
    ],
    independent_native=dict(command=native['command'], native_exit_code=native['native_exit_code'], direct_child_wait_returned=native['direct_child_wait_returned'], unknown_count=native['unknown_count'], elapsed_seconds=native['elapsed_seconds'], sampled_owned_tree_peak_bytes=native['sampled_owned_tree_peak_bytes'], known_descendants_same_identity_absent_at_observation=native['known_descendants_same_identity_absent_at_observation'], entire_os_tree_terminal=native['entire_os_tree_terminal']),
    real_s14=audit['s14_real_rounds'],
    real_s14_sta_status=audit['s14_sta']['status'],
    accepted_root_layout='ROOT已明确SYNTH_CACHE=工具WORK，PROJECT=WORK/project_s15_r01；HERE==CACHE不列缺陷。',
    evidence=[row(HERE / name) for name in ('review_probe.py', 'review_probe_result.json', 'evidence_audit.py', 'evidence_audit_result.json', 'evidence_audit_result_r02.json', 'review_native_canary.native.json')],
    limitations=['S14三轮94/41/216raw、348/351valid、3TREE_RESCAN_NOT_CLOSED及FAIL_TIMING保持失败；不后验重分类。', '本审查仅轻量原生和模拟反例；未启动Vivado、ROSS、JTAG、串口或大型编译，未修改共享分支/生产被审文件，不提交。', '实际源码profile冻结、功能G2及工具G2仍PENDING；不编造本次批准。', '审查第一次audit误读实际gap字段，r01原件仍留；r02改读actual_start_gap_seconds，原G1 cadence/consumer最大gap均1.0秒。', '初次sandbox执行Python被拒绝，随后仅授权离线审查的require_escalated执行成功；没有绕过实物或MCP门槛。', '实际canary只证明直接子wait返回及离散已知身份观察，整OS树与绝对连续峰仍NOT_PROVEN。'],
)
save(HERE / 'final_review_receipt.json', receipt)
files = [row(path) for path in sorted(HERE.rglob('*')) if path.is_file()]
save(HERE / 'original_file_index.json', dict(status='STOP_REVIEW_ORIGINALS_INDEXED', files=files, root=str(HERE)))
print(json.dumps(dict(status=receipt['status'], frozen_tools_unchanged=unchanged, receipt=row(HERE / 'final_review_receipt.json'), index=row(HERE / 'original_file_index.json'), files=len(files)), ensure_ascii=False))
