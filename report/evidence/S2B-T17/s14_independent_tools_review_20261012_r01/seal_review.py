"""封存独立工具G2结论；不扩展为实际部署或真实SOURCE批准。"""
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

W=Path(__file__).resolve().parent
ROOT=W.parents[3]
D=ROOT/'report/evidence/S2B-T17/s14_launch_tools_20261012_r01'
ORIGINAL=ROOT/'tmp/2B/S2B-T17/s14_launch_prepare_20261012_r01'
def read(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def binding(path): return dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),bytes=path.stat().st_size)
def save(path,value):
    assert path.is_relative_to(W)
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')

tests=read(W/'test_receipt.json'); native=read(W/'review_r02.native.json')
assert tests['status']=='PASS_INDEPENDENT_LIGHT_CHECKS_ONLY' and tests['tests']==60
assert native['native_exit_code']==0
original=read(D/'final_g1_receipt_r02.json')
for row in original['tools']:
    assert sha(Path(row['original_absolute_path']))==sha(ROOT/row['archived_repo_path'])==row['sha256']
    assert sha(W/Path(row['original_absolute_path']).name)==row['sha256']
assert sha(D/'delivery_manifest_r02.json')=='0f74e386ac005c5e69fc01f41dd5dd25ef8cf73e93ed134f54a5e9f1cd1e98a3'
command=[sys.executable,'-X','utf8','-B',str(ROOT/'verification/check_stage_delivery.py'),'--mode','evidence','--manifest',str(D/'delivery_manifest_r02.json')]
began=time.monotonic()
with (W/'independent_checker.stdout.bin').open('xb') as stdout,(W/'independent_checker.stderr.bin').open('xb') as stderr:
    completed=subprocess.run(command,cwd=ROOT,stdout=stdout,stderr=stderr,timeout=30)
save(W/'independent_checker.native.json',dict(command=command,cwd=str(ROOT),native_exit_code=completed.returncode,elapsed_seconds=time.monotonic()-began,
     logs=[binding(W/'independent_checker.stdout.bin'),binding(W/'independent_checker.stderr.bin')],scope='只读包装核验，不是语义或真实运行批准'))
assert completed.returncode==0
assert read(W/'independent_checker.stdout.bin')['status']=='CHECKS_OK'
consumer=read(W/'native_consumer_canary_r03/native_canary_result.json')
terminal=read(W/'native_consumer_canary_r03/known_identity_terminal.json')
assert all(row['same_identity_present'] is False for row in terminal['observations'])
assert consumer['supervisor_native_exit_code']==2 and consumer['consumer_native_exit_code']==2
assert read(W/'independent_native_nonzero.native.json')['native_exit_code']==7
head_command=['git','rev-parse','HEAD']
head=subprocess.run(head_command,cwd=ROOT,capture_output=True,timeout=10)
assert head.returncode==0
actual_head=head.stdout.decode('ascii').strip()
files=[binding(path) for path in sorted(W.rglob('*')) if path.is_file()]
save(W/'raw_manifest.jsonl',dict(files=files,说明='JSON索引绑定全部独审原件；不包含本索引或最终回执以避免循环'))
result=dict(status='PASS_TOOL_G2_ONLY',task='S14_RESOURCE_LAUNCH_TOOLS',created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),
    reviewed_baseline_head='5a674888acdedaa41127c4ea354231e10140eea5',actual_head_at_review_end=actual_head,
    developer_tool_fork_baseline=original['baseline_commit'],production_source_commit=None,
    reviewed_manifest=binding(D/'delivery_manifest_r02.json'),reviewed_g1_receipt=binding(D/'final_g1_receipt_r02.json'),
    source_hashes=original['tools'],raw_manifest=binding(W/'raw_manifest.jsonl'),
    commands=[dict(command=native['command'],native_exit_code=0,native_record=binding(W/'review_r02.native.json')),
              dict(command=command,native_exit_code=0,native_record=binding(W/'independent_checker.native.json'))],
    test_scope=dict(total_methods=60,developer_methods_reexecuted=55,independent_additional_methods=5,
                    developer_final_binding_methods=4,developer_final_binding_note='4方法重复的Closure/Config已包含7方法重跑；其余AST/实际common/guard/SUP/pending绑定另独立直接核查，不能累计为64方法',
                    actual_owned_canaries=5,canaries=['threshold','one_second_cadence','consumer_independent_clock','native_metadata_code0','native_metadata_code7'],
                    consumer_target_seconds=5,consumer_hard_seconds=10,guard_target_seconds=1,maximum_collection_rounds=3,required_consistent_alive_sets=2,
                    runtime_os_pid_reuse_test=False,actual_vivado=False,actual_ross=False,hardware=False),
    findings=[],checks=[dict(name=name,status='PASS') for name in [
        '正式清单全部文件、23工具live/归档/独审快照及原生日志绑定',
        '末表ABSENT只认可本次known_lineage/当前六字段/ROOT，HISTORICAL_CHAIN真实RSS且stoppableFalse',
        'UNKNOWN/reuse/drift/no_proof/new_orphan拒绝及historical停止权限拒绝',
        '首行newline和合法UTF8/JSON先于complete，2秒期限拒绝仍保留',
        'native metadata白名单、真实code7不覆盖、非prepareHERE==pinCACHE、s14收尾前缀及实际profile0.1.14',
        'prepare绑定native_capture、PNR助手count取真实len、commonSHA一致、旧S13记录未改判',
        '停止内核/collect/max3/twoalive/consumer未改变，6GiB/512MiB/8GiB及5s目标/10s硬限保留']],
    failed_attempts=[dict(name='独审r01',native_record=binding(W/'review.native.json'),native_exit_code=1,
                         reason='审查脚本错误期待纯文本CHECKS_OK，实际原件为合法JSON；未进入测试，原失败脚本和日志保留，非工具缺陷')],
    performance=dict(elapsed_seconds=native['elapsed_seconds'],sampled_owned_tree_peak_bytes=native['sampled_owned_tree_peak_bytes'],sample_interval_seconds=.05,
                     unknown_samples_count=len(native['unknown_samples']),continuous_peak_bytes=None),
    limitations=['此PASS只批准固定工具字节的G2，不批准生产源码、runtime配置、RESOURCE预算、SOURCE-before/after、真实综合、STA、PNR、ELF/BSP兼容、G3/G4/G5。',
                 'SOURCE_commit/G1/G2/RunIds/TOOLS_G2与实际runtime_config仍PENDING；ROOT须固定实际G0/依赖后消费本receipt，不继承历史配置。',
                 '实际canary只作用于独审自有轻量进程；已知身份最终ABSENT不证明整个OS树闭合或连续绝对峰。',
                 '原selftest监督器SHA193416字段是旧诊断；新0ad7实际字节由tools/finalbindings/独审快照固定，未追认为旧测试新版本证明。',
                 'Developer post-manifest checker r02为后置单独原件，已独立核SHA/原生0/JSON；不声称其已被当时manifest自绑定。',
                 '本Reviewer仅写授权独审tmp目录，不修改WORK/生产/HEAD/branch，不提交；永久证据归档与commit由ROOT负责。'],
    not_run={name:'NOT_RUN' for name in ['production_source_freeze','runtime_config_materialization','real_source_before_after','real_resource_admission','real_unique_synthesis','actual_budget','actual_sta','pnr','hardware_g3','stage_g5']},
    stop=True)
save(W/'final_review_receipt.json',result)
print(json.dumps(dict(status=result['status'],receipt=binding(W/'final_review_receipt.json'),files=len(files),methods=60,canaries=5,stop=True),ensure_ascii=False))
