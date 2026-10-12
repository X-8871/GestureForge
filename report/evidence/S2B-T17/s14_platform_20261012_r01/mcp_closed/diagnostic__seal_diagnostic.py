"""绑定既有监护失败原件并保存保守拒绝诊断，不更改G2结论。"""
from datetime import datetime,timezone,timedelta
import hashlib
import json
from pathlib import Path
W=Path(__file__).resolve().parent
ROOT=W.parents[4]
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def binding(path):return dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size)
extract=load(W/'actual_guard_extract.json')
for row in extract['files']:assert binding(ROOT/row['path'])==row
assert hashlib.sha256((W.parent/'final_review_receipt_r02.json').read_bytes()).hexdigest()=='5610d6538ec52030277c2fd4dc591b35057182215d4c56532f27c65f64d59bbb'
receipt=dict(status='DIAGNOSTIC_CONSERVATIVE_FAIL_CLOSED_SUPPORTED',created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),
   reviewed_source='53772ae581ff3ccfb3a9d411cdc66fc67c3e2161',root_pid=19192,root_create_time=1791777476.053502,
   prior_tools_g2=binding(W.parent/'final_review_receipt_r02.json'),prior_tools_g2_modified=False,
   raw_extract=binding(W/'actual_guard_extract.json'),original_bindings=extract['files'],
   conclusion='两次实际日志支持既定max3/相邻两次活身份集合一致规则下的保守非零拒绝；未发现本次S14末表ABSENT修复的错误触发、identity错误采纳或错误停止证据。真实运行监护未连续PASS。',
   support=[dict(run='r01',sample_line=94,index=93,events_lines=[4,5,6,7,8,9],collection_elapsed_seconds=1.016,collection_scans=3,closed=False,
        prior_members=[19192,37728],final_members=[19192,37728,7272,3244,19448,24680],exits=[],
        trigger='12:04:22.536至12:04:23.245依次核得vrs→cmd→cscript→cmd；首次子任务GP0链仍在展开。',
        tree_rss_bytes=None,verified_subset_rss_bytes=1281335296,guard_native_exit_code=3,supervisor_native_exit_code=2,consumer_native_exit_code=2),
      dict(run='r02',sample_line=41,index=40,events_lines=[13,14,15,16,17,18,19,20,21],collection_elapsed_seconds=1.078,collection_scans=3,closed=False,
        prior_members=[19192,37728,7272,17748,15960,19604,16244],final_members=[19192,37728,7272,35476,19360,28512],exits=[19604,16244,17748,15960],
        trigger='12:07:02.190至12:07:02.383确认reset任务四节点ABSENT，12:07:02.531至12:07:02.951核得新的PS7 cmd/cscript/cmd链，IP任务切换跨越采集窗口。',
        tree_rss_bytes=None,verified_subset_rss_bytes=1280520192,guard_native_exit_code=3,supervisor_native_exit_code=2,consumer_native_exit_code=2)],
   resource_trigger='末样本alerts为空；两次闭合样本峰分别1217032192/3609927680B，已观测RAM/CDisk未触及6GiB/512MiB/8GiB门槛。该事实不证明未观测区间满足预算。',
   consumer_cause='consumer r01末行11/r02末行4分别NoSuchProcess守卫23460/23388，按UNKNOWN/BLOCKED锁存真实2；这对应guard已退出，不是把Vivado ROOT19192误判为退出。',
   implementation_reference=dict(path='tmp/2B/S2B-T17/s14_launch_prepare_20261012_r01/guard.py',sha256='1dd9a678776d92d6042fff7c326582ebb360348732f35a6dc1939410dc867b3b',function='Guard.collect',meaning='最多三轮，current活PID/birth集合与上一轮相等且该轮exited为空才closed；末轮仍不满足而没有其他uncertain才追加TREE_RESCAN_NOT_CLOSED。'),
   proof_limit='sample仅保留最后集合与三轮总摘要，events保留新链/退出时点，未逐轮保存三套集合。可以核对真实分叉/退出与正确保守终态；不能独立逐项重建每轮集合，也不能把subset RSS或两段观察拼成连续预算PASS。',
   action='只读诊断STOP；未开启guard、查询/干预进程、修改工具/配置/实际Run、派发综合或硬件；不提出重综合。',
   actual_final_evidence_independent_review='NOT_RUN_BY_THIS_DIAGNOSTIC',stop=True)
target=W/'actual_guard_diagnostic_receipt.json'
with target.open('x',encoding='utf-8',newline='\n') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps(dict(status=receipt['status'],receipt=binding(target),stop=True),ensure_ascii=False))
