"""冻结fallback R2独审批准范围与原件索引，不授予STA或连续预算批准。"""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone,timedelta
HERE=Path(__file__).parent;ROOT=HERE.parents[3]
W=ROOT/'tmp/2B/S2B-T17/s15_source_closure_fallback_20261012_r02'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def row(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as stream:json.dump(v,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
result=read(HERE/'review_result.json');g1=read(W/'g1_receipt.json');inventory=read(W/'frozen_inventory.json')
assert result['status']=='PASS_SOURCE_CLOSURE_TOOL_G2_ONLY' and len(result['checks'])==50 and all(r['status']=='PASS' for r in result['checks'])
assert row(W/'source_closure.py')==g1['implementation']==result['entry']
assert len(inventory['files'])==572 and all(row(ROOT/r['path'])==r for r in inventory['files'])
assert all(row(ROOT/r['path'])==r for r in result['tools_unchanged'])
receipt=dict(status='PASS_SOURCE_CLOSURE_TOOL_G2_ONLY',stop=True,created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),
    source_commit=result['source_commit'],reviewed_entry=result['entry'],reviewed_tools=[result['entry']],reviewed_g1=result['g1_receipt'],reviewed_inventory=result['frozen_inventory'],frozen_originals_checked=572,
    independent_checks=50,all_pass=True,r1_p2_closed=True,four_missing_metadata_counterexamples_rejected=True,
    covered=['完整原native_capture字段存在与类型检查；native/wrapper int严格拒bool/float。','每个已知终态六字段、合法终态状态/exists三态、直接子绑定和汇总absence一致。','UNKNOWN各明细字段、计数、PID/birth类型、异常原件完整；27/26未知分支继续真实wrapper2/BLOCKED。','实际SOURCE config/adm/G1-G2依赖、46 RAW与92 snapshots、33 static、14 frozen、13工具及额外r01guard恢复副本字节一致。','既有48 Git directwait/stdout hash与RAW/exact LF->CRLF逐项复核；未启动Git。','额外证据可空；输出明确mcp9_sta_validation NOT_IN_SCOPE，不授予九MCP/五job/STA的设计语义验收。'],
    actual_independent_package=dict(command=result['actual_native']['command'],native_exit_code=0,direct_child_wait_returned=True,elapsed_seconds=result['actual_native']['elapsed_seconds'],entry_original=result['actual_native']['entry_original'],entry_identical_byte_copy=result['actual_native']['entry_copy'],receipt=result['package_receipt'],manifest=result['package_manifest'],files_hash_checked=174,existing_same_directory_native_exit_code=1,existing_same_directory_direct_child_wait_returned=True),
    preserved_original_states=dict(source_before_child_native_exit_code=0,source_after_child_native_exit_code=0,before_wrapper_exit_code=2,after_wrapper_exit_code=2,before_unknown_count=27,after_unknown_count=26,budget_status='BLOCKED',continuous_budget_pass=False),
    original_13_tools_unchanged=result['tools_unchanged'],mcp9_sta_validation='NOT_IN_SCOPE',original_seal='NOT_CALLED_NOT_PASSED',actual_sta='NOT_REVIEWED_BY_THIS_AGENT',g3_g4_g5='NOT_APPROVED_BY_THIS_ENTRY',
    evidence=[row(HERE/name) for name in ('review.py','review_result.json','actual.wait.json','actual.stdout.bin','actual.stderr.bin','existing.wait.json','existing.stdout.bin','existing.stderr.bin')],
    findings=[],
    limitations=['仅批准固定SOURCE closure软件入口；真实SOURCE内容封包不追认原capture、连续资源预算、STA、板上或阶段验收。','独立执行的是固定entry同SHA原字节副本，位于相同ROOT深度新审查目录；仅允许输出父目录随副本HERE变化，生产依赖路径和所有实现字节保持完全一致。','174文件独立封包仍在tmp审查目录，标准正式目录的产物清单机器核验由ROOT实际归档后执行；未把tmp布局称CHECKS_OK。','无Git/ROSS/Vivado/硬件/大型编译执行，未修改原13工具、config/SOURCE、被审entry、ROOTclosure、共享分支或提交。','全部真实UNKNOWN/guard和consumer BLOCKED原件及R1失败仍保留；新入口不调用原seal，不将未知或非零改成PASS。'])
save(HERE/'final_review_receipt.json',receipt)
files=[row(p) for p in sorted(HERE.rglob('*')) if p.is_file()]
save(HERE/'original_file_index.json',dict(status='STOP_REVIEW_ORIGINALS_INDEXED',files=files,root=str(HERE)))
print(json.dumps(dict(status=receipt['status'],receipt=row(HERE/'final_review_receipt.json'),index=row(HERE/'original_file_index.json'),original_count=len(files)),ensure_ascii=False))
