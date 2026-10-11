"""固定本次只读审查范围、问题与证据索引，不批准实际物理执行。"""
import hashlib
import json
from pathlib import Path
import sys

OUT=Path(__file__).parent
ROOT=Path(__file__).parents[4]
WORK=ROOT/'tmp/2B/S2B-T17/s12_physical_compat_prepare_20261012_r01'
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
entry=read(WORK/'final_draft_binding.json')
for row in entry['files']:
    assert sha(WORK/row['path'])==row['sha256'] and (WORK/row['path']).stat().st_size==row['bytes']
receipt=read(WORK/'compatibility_delivery_receipt.json')
native=[]
for row in receipt['native_calls']:
    label=row['label']; path=WORK/('head.native.json' if label=='head_read_only' else label+'.native.json')
    actual=read(path)
    assert type(actual['native_exit_code']) is int and actual['native_exit_code']==row['expected_code']==row['native_exit_code']
    if label.endswith('_blocked'):
        assert b'BLOCKED_PENDING_S12_PINS' in (WORK/(label+'.stderr.bin')).read_bytes()
    native.append(dict(label=label,native_exit_code=actual['native_exit_code'],file=path.relative_to(ROOT).as_posix(),sha256=sha(path)))
assert len(native)==19 and sum(r['native_exit_code']==0 for r in native)==10
checks=read(OUT/'independent_result.json');source=read(OUT/'source_pin_result.json')
findings=[
    dict(priority='P2',file='impl_collector.py',lines=[94,101,102,103,104],title='PNR五个成功history未严格限制int0',impact='wait/open_run/reports的失败或未知/错误类型码在匹配客户端字段后可通过关闭门禁；launch/close也误接受False与0.0。当前25坏例19被接受，不能批准COMPAT逻辑G2。',evidence='independent_result.json',closure='五required labels要求type(code)is int且code==0；客户端码若存在也须正确类型并等于history，客户端timeout保留独立状态且history仍严格0。25类型/失败矩阵及有效int0/optionalinvalid精确非0正例通过。'),
    dict(priority='P2',file='collector.py',lines=[146,147,148,182,184],title='CLI源码commit未闭合到最终固定SOURCE_COMMIT',impact='已pin A但CLI及实际HEAD为B且43文件同字节时，source(B,before)仍接受并输出B。collect/seal关闭门禁同样只与传入commit比，最终SOURCE_COMMIT未形成统一绑定。',evidence='source_pin_result.json',closure='source/collect/seal须在任何写入前拒绝CLI commit与compat_pins.SOURCE_COMMIT不同，固定freeze中的实际commit语义需一致；增加不同commit同RAW反例。')
]
result=dict(status='CHANGES_REQUIRED',task_id='S12-PH-G2-COMPAT2',scope='COMPAT_LOGIC_ONLY',reviewed_source_entry=dict(path=(WORK/'final_draft_binding.json').relative_to(ROOT).as_posix(),sha256=sha(WORK/'final_draft_binding.json')),reviewed_files=entry['files'],raw_manifest=dict(path=(WORK/'raw_manifest.jsonl').relative_to(ROOT).as_posix(),sha256=sha(WORK/'raw_manifest.jsonl'),files=1836,manifest_bytes=(WORK/'raw_manifest.jsonl').stat().st_size,total_raw_bytes=checks['raw_input_bytes']),native_original_records=native,developer_test_coverage=dict(schema_history_recovery=57,full_source_after_main=9,independently_read_test_scripts=True,actual_source_after_git_calls=0,full_large_fixture_not_rerun=True,missing_original_cases='五个成功history的失败/未知/类型矩阵与CLI不同固定commit同RAW'),independent_checks=dict(pnr_bad_cases=25,bad_cases_accepted=19,raw_hand_cases=3,source_commit_same_bytes_case='ACCEPTED_BAD_SYNTHETIC_COMMIT',native_success_commands=2,elapsed_seconds=checks['elapsed_seconds']+source['elapsed_seconds'],sampled_self_rss_peak_bytes=max(checks['sampled_self_rss_peak_bytes'],source['sampled_self_rss_bytes']),absolute_peak_bytes=None,git_tcl_vivado_ross_or_hardware_calls=0),findings=findings,limitations=['只读核验实际冻结六源与1836RAW，没有重跑大夹具/RTL或实际Git/Tcl。','初次普通sandbox Python启动被OS拒绝，native未启动/null；其PowerShell宿主0不是Python真实返回码。Node lstat亦EPERM，未启动Python。','首个真正native独审脚本误将RAW总长度1260049当manifest自身长度导致assert失败/native1；修正计量断言后成功，manifest自身686162B、1836 RAW总1260049B。','测试中ready/静态/实际Git的替身仅用于合成反例，实际RAW快照与history哈希核验保留；未伪称实际运行。','最终pins/真实运行/sourcefreeze/helper共同版本仍需冻结复审；物理G0、实际预算/STA/G3/G5未批准；旧S11预算BLOCKED。','被审/生产文件未修改，无Git提交。'],physical_g0='BLOCKED_PENDING_REAL_PINS',actual_budget='NOT_RUN',actual_sta='NOT_RUN',old_s11_budget='BLOCKED',g3='NOT_RUN',g5='NOT_RUN',stop=True)
path=OUT/'final_review_receipt.json'
with path.open('x',encoding='utf-8',newline='\n') as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
files=[]
for p in sorted(OUT.rglob('*')):
    if p.is_file():files.append(dict(path=p.relative_to(OUT).as_posix(),sha256=sha(p),bytes=p.stat().st_size))
with (OUT/'raw_manifest.jsonl').open('x',encoding='utf-8',newline='\n') as stream:
    for row in files:stream.write(json.dumps(row,ensure_ascii=False)+'\n')
print(json.dumps(dict(status=result['status'],receipt_sha256=sha(path),raw_manifest_sha256=sha(OUT/'raw_manifest.jsonl'),raw_files=len(files),findings=2,developer_native_records=len(native),native_exit_code=0),ensure_ascii=False))
