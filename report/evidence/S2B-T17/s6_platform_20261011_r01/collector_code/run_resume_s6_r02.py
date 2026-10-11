"""记录 r02 续收集的原生退出码并封存关闭日志。"""
from collection_common import *
record=run_closed([sys.executable,'-B',str(WORK / 'resume_s6_r02.py')],'s6_collection_collector_r02',timeout=55)
copy_closed('s6_collection_collector_r02')
require(record['native_exit_code']==0,'r02续收集失败，原件与日志保留')
print(json.dumps(record,ensure_ascii=False))
