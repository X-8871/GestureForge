"""冻结独立SOURCE入口G1；只写本轮TMP，不封真实after或继承预算批准。"""
from datetime import datetime,timedelta,timezone
import ast,json,subprocess,sys,time
from pathlib import Path
import source_closure as c
HERE=Path(__file__).parent;ROOT=c.ROOT
assert not (HERE/'g1_receipt.json').exists()
result=c.read(HERE/'regression_result_r03.json');wait=c.read(HERE/'regressions_r03.wait.json')
assert result['status']=='PASS_G1_ONLY' and wait['native_exit_code']==0 and wait['direct_child_wait_returned'] is True
assert wait['tool_before']==wait['tool_after']==c.binding(HERE/'source_closure.py')
command=[sys.executable,'-X','utf8','-B',str(HERE/'source_closure.py'),'--request',str(HERE/'request_pending_after_r03.json'),'--output-dir',str(HERE/'s15_source_closure_actual_rejected_r01')]
start=time.monotonic()
with (HERE/'missing_after_cli.stdout.bin').open('xb') as out,(HERE/'missing_after_cli.stderr.bin').open('xb') as err:
    code=subprocess.run(command,cwd=ROOT,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW,timeout=20).returncode
assert code==1 and not (HERE/'s15_source_closure_actual_rejected_r01').exists()
cli=dict(command=command,native_exit_code=code,direct_child_wait_returned=True,elapsed_seconds=time.monotonic()-start,stdout=c.binding(HERE/'missing_after_cli.stdout.bin'),stderr=c.binding(HERE/'missing_after_cli.stderr.bin'),reason='after实际输入缺失；校验失败未创建输出目录。')
c.save(HERE/'missing_after_cli.wait.json',cli)
config,freeze,tools,inputs=c.baseline(c.binding(c.CONFIG))
for path in HERE.glob('*.py'):ast.parse(path.read_text(encoding='utf-8'))
receipt=dict(status='STOP_G1_SOURCE_CLOSURE_ENTRY_PENDING_INDEPENDENT_G2',stop=True,created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),
 implementation=c.binding(HERE/'source_closure.py'),source_commit=c.SOURCE,config=c.binding(c.CONFIG),source_freeze=c.binding(Path(config['SOURCE_FREEZE'])),
 source_count=46,static_count=33,frozen_original_count=14,reviewed_existing_tools=tools,existing_runtime_dependencies=freeze['tool_runtime_dependencies'],
 methods=25,regression_result=c.binding(HERE/'regression_result_r03.json'),real_wait=wait,actual_cli_rejection=cli,
 actual_before='SOURCE_CONTENT_ONLY_CHILD0_WRAPPER2_UNKNOWN27',actual_after='NOT_AVAILABLE_NOT_EXECUTED',
 original_seal='NOT_CALLED_NOT_PASSED',budget='BLOCKED_PRESERVED',sta='NOT_APPROVED',entry_g2='PENDING',hardware='NOT_RUN',g5='NOT_APPROVED',
 future_cli=[sys.executable,'-X','utf8','-B',str(HERE/'source_closure.py'),'--request','ROOT实际新增完整request绝对路径','--output-dir','ROOT指定的新绝对目录'],
 request_usage=['以request_pending_after_r03.json为字段模板，新建request，不覆盖模板或任何已闭合原件。',
 'source_after/capture_after必须填ROOT实际产生的path/sha256/bytes；新入口要求SOURCE-before/after各真实collector child0、directwait、stdout确认、snapshot和工具前后实际完整绑定。',
 'budget_records显式列所有本次需封存的已闭合guard/consumer收据，budget_status按实际BLOCKED或NOT_PROVEN；禁止PASS。',
 'additional_evidence显式列现collector collect生成的九MCP/五job/STA等原件；新入口只核字节并复制，不调用collector/seal/ROSS或生成设计报告。',
 '实际正式输出必须ROOT指定report/evidence/S2B-T17下的新s15_source_closure_前缀RunId；当前开发仅TMP试验。',
 '新manifest保留source包装FAIL及预算NOT_RUN+BLOCKED理由，CHECKS_OK只表示封装一致性，不代表预算、STA、独审、实物或阶段验收。'],
 restore_scope=['恢复到同一精确ROOT及fallback入口路径；入口文件、实际request和所有封装raw mapping按SHA逐项恢复。',
 '实际SOURCE包包括config/freeze/46 RAW源码/前后92快照/前后source JSON/两真实native捕获及流/admission原件/G1-G2 receipt/13工具及额外r01守卫实际与恢复副本。',
 '守卫samples/events及明确指定budget收据按原字节归档；原UNKNOWN/BLOCKED不能升级。',
 '既有Git stdout只在ROOT admission记录SHA，没有另造原流；本入口以RAW或逆exactLFCRLF字节重新计算同SHA，未执行Git。',
 'G1/G2完整历史实验包、设计生成工程/五job/STA及硬件恢复不由SOURCE包自动补齐；按ROOT显式additional_evidence列表或既有冻结包独立恢复。'],
 failures_preserved=['首轮driver真实wait1因测试误把TMP checker预期2当0；源文件/原流/fixture清单均保留failed_attempt_r01及旧RunId。',
 '最终checker真实2只因TMP不属于正式report落点，严格未改检查器或假称CHECKS_OK。',
 '实际missing-after CLI native1/directwait，未创建输出。'],
 limitations=['未修改已审13工具、生产源码或config；没有Git、ROSS、Vivado、重型或硬件调用。',
 '25项含真实before只读正向、拒绝反例及显式封包机械fixture；尚无真实after完整生产正向。',
 '本G1不是SOURCE独审/G2，不调用或冒充原seal通过，不批准真实监护/连续峰/STA/G3/G5。'])
c.save(HERE/'g1_receipt.json',receipt)
files=[c.binding(path) for path in sorted(HERE.rglob('*')) if path.is_file()]
c.save(HERE/'frozen_inventory.json',dict(status=receipt['status'],implementation=receipt['implementation'],files=files,source_commit=c.SOURCE,entry_g2=None))
print(json.dumps(dict(status=receipt['status'],entry=receipt['implementation'],receipt=c.binding(HERE/'g1_receipt.json'),inventory=c.binding(HERE/'frozen_inventory.json'),files=len(files)),ensure_ascii=False))
