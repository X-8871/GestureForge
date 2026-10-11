"""记录准备脚本的真实原生返回码，仅写隔离收集目录。"""
from collection_common import *
record=run_closed([sys.executable,'-B',str(WORK/'prepare_s7.py')],'preparation',timeout=45)
require(record['native_exit_code']==0,'准备检查失败，关闭日志已保留')
receipt=read(WORK/'prepared_receipt.json')
print(json.dumps({'status':receipt['status'],'source_commit':receipt['source_commit'],'expected_source_count':receipt['expected_source_count'],'before_declared_git_raw_count':receipt['before_declared_git_raw_count'],'before_declared_exact_eol_count':receipt['before_declared_exact_eol_count'],'prepared_receipt':binding(WORK/'prepared_receipt.json'),'preparation_native':binding(WORK/'preparation.native.json'),'native_exit_code':record['native_exit_code'],'elapsed_seconds':record['elapsed_seconds'],'formal_report_written':False,'s7_active_job_files_consumed':False},ensure_ascii=False))
