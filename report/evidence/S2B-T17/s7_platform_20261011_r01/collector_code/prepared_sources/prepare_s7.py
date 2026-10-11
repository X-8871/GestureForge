"""仅核验收集准备与闭合 S6 格式，不读取活动 S7 工程和日志。"""
from collection_common import *
import ast
from datetime import datetime, timezone, timedelta

require(not (WORK/'closed_inputs.json').exists(),'准备期已有关闭门禁，需总控决定继续阶段')
before_path=exact(PRE/'source_before.json')
require(sha(before_path)==BEFORE_SHA and sha(FREEZE)==FREEZE_SHA,'已知输入SHA不同')
before=read(before_path)
freeze=read(FREEZE)
rows=before['source_files']
require(before['source_commit']==BASELINE and len(rows)==39 and before['platform_static_source_count']==31,'本轮before基线或计数不同')
require({r['path']:r['sha256'] for r in rows}==freeze['source_sha256'],'before与freeze闭包不同')
require(len(before['frozen14_sha256'])==14 and before['frozen14_sha256']==freeze['frozen14_sha256'],'原14绑定不同')
require(sum(r['git_relation']=='RAW_IDENTICAL' for r in rows)==33 and sum(r['git_relation']=='GIT_LF_TO_RAW_CRLF' for r in rows)==6,'before声明不是33RAW+6EOL')
previous=ROOT/'report/evidence/S2B-T17/s6_platform_20261011_r01'
schema=[]
for label in ('source','builder','setup','launch','wait','open','reports','query_xdc','close'):
    path=exact(previous/'mcp_closed'/('mcp_'+label+'.json'))
    record=read(path)
    result=mcp_result(record)
    captured='input' in record
    require(captured or label in ('source','builder'),'S6已关闭参考格式意外')
    if label!='wait':
        parsed=mcp_json(record)
        require(isinstance(parsed['exit_code'],int),'参考真实码缺失')
    else:
        require(result.get('isError') is True,'参考超时格式不同')
    schema.append({'label':label,'reference':binding(path),'client_input_captured':captured,'schema':'INPUT_RESULT_WRAPPER' if captured else 'RAW_CALL_TOOL_RESULT'})
source_files=[]
for name in ('collection_common.py','classify_s7_sta.py','prepare_s7.py','run_preparation.py','collect_s7.py','run_collection.py','finalize_s7.py','run_finalization.py'):
    path=exact(WORK/name)
    ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
    source_files.append(binding(path))
record={'status':'STOP_PREPARED_ONLY','prepared_at_utc8':datetime.now(timezone(timedelta(hours=8))).isoformat(),'source_commit':BASELINE,'source_before':binding(before_path),'source_freeze':binding(FREEZE),'expected_source_count':39,'expected_static_count':31,'expected_extra_count':8,'before_declared_git_raw_count':33,'before_declared_exact_eol_count':6,'before_metadata_only':True,'actual_after_static_history_log_not_consumed':True,'formal_report_written':False,'s7_active_job_files_consumed':False,'ross_hardware_or_heavy_compile_executed':False,'schema_reference':schema,'prepared_scripts':source_files,'gate':'必须收到ROOT明确CLOSED_INPUTS_READY并建立本cache closed_inputs.json，正式收集才会执行。','sta_status':'UNKNOWN_NOT_RUN','g1_g2_g3_g4_g5_approved':False,'tool_versions':{'python':sys.version}}
save(WORK/'prepared_receipt.json',record)
print(json.dumps(record,ensure_ascii=False))
