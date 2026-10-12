"""冻结SOURCE内容入口独审阻断与原件索引，不改变原入口或审批。"""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone,timedelta
HERE=Path(__file__).parent;ROOT=HERE.parents[3]
W=ROOT/'tmp/2B/S2B-T17/s15_source_closure_fallback_20261012_r01'
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def row(path):return dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size)
def save(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as stream:json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
probe=read(HERE/'probe_result.json');g1=read(W/'g1_receipt.json');inventory=read(W/'frozen_inventory.json')
assert row(W/'source_closure.py')==g1['implementation']==probe['entry']
assert all(row(ROOT/item['path'])==item for item in inventory['files'])
receipt=dict(status='CHANGES_REQUIRED',stop=True,created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),source_commit='926c2fd382069e68e6c5ec533b7d3b6a87fbb363',entry=row(W/'source_closure.py'),g1_receipt=row(W/'g1_receipt.json'),frozen_inventory=row(W/'frozen_inventory.json'),frozen_originals_hash_checked=len(inventory['files']),independent_checks=26,passed=22,unexpected_accepts=4,
    findings=[dict(priority='P2',path='tmp/2B/S2B-T17/s15_source_closure_fallback_20261012_r01/source_closure.py',start=148,end=183,title='未知包装分支仍接受丢失原生metadata',
        impact='在UNKNOWN27/wrapper2的原生记录逻辑反例中，删除capture_target_kind、budget_stop、known_descendant_identity_terminal_observations或known_descendants_same_identity_absent_at_observation，capture仍接受。没有升级预算PASS，但无法落实拒绝metadata丢失和完整原件结构验收，尤其after未由固定admission SHA保护时缺项可进入内容封包。',
        closure='先强制完整SOURCE capture schema及字段类型：包括target kind=COLLECTOR、budget_stop显式None或有效失败字符串、known terminal列表和known absent显式布尔等。核完整wrapper/native码为int（拒bool），已知终态每行完整六字段与合法状态，未知记录保持明确。允许真实UNKNOWN27/wrapper2做SOURCE内容补证，原状态/原未知/原预算值保存；缺字段或矛盾一律拒绝，不套用原工具禁止UNKNOWN的seal契约，不追认SOURCE capture或预算PASS。补四拒绝负向及真实blocked捕获正向。')],
    verified_scope=['实际SOURCE/config固定SHA，46 RAW+snapshot、33 static、原14与13工具G2及r01guard actual/recovery依赖一致。','既有48 Git directwait/hash逐字段及RAW/exact LF->CRLF关系独立复核；未启动Git。','实际before child0、directwait、wrapper2/UNKNOWN27、guard BLOCKED及原流哈希保留。','child非零/布尔码、完整命令/父birth、重要identity/tool/log字段缺失、directwait缺失、假capture PASS/预算PASS均拒绝。','缺真实after立即拒绝；完整after尚未由本审查运行或生成。'],
    evidence=[row(HERE/name) for name in ('probe.py','probe_result.json')],
    limitations=['该入口SOURCE内容范围不批准原seal、STA、连续预算或G3/G5；无Git/ROSS/Vivado/硬件/重编译执行。','additional_evidence当前为可选列表，显式逻辑after fixture中空列表仍可closed；该入口不能单独保证完整collect/MCP9/STA/approved_evidence已封存。若ROOT另有独立证据封包，应明确该范围并按显式闭合清单核完整性；若本入口承担完整已批准证据，需额外强制列表/清单绑定。','核查原件94项全部SHA/bytes仍符合库存；未修改入口、原13工具/config/SOURCE/ROOTclosure/分支或提交。','逻辑metadata反例通过注入独立副本隔离字段校验，未改实际固定UNKNOWN27原件或其admission SHA。'])
save(HERE/'final_review_receipt.json',receipt)
files=[row(path) for path in sorted(HERE.rglob('*')) if path.is_file()]
save(HERE/'original_file_index.json',dict(status='STOP_REVIEW_ORIGINALS_INDEXED',files=files,root=str(HERE)))
print(json.dumps(dict(status=receipt['status'],receipt=row(HERE/'final_review_receipt.json'),index=row(HERE/'original_file_index.json'),original_count=len(files),frozen_originals=len(inventory['files'])),ensure_ascii=False))
