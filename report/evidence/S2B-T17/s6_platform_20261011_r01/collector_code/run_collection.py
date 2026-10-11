"""记录 Collector 真正原生退出码，随后复制已关闭日志。"""
from collection_common import *
record=run_closed([sys.executable,'-B',str(WORK / 'collect_s6.py')],'s6_collection_collector',timeout=55)
copy_closed('s6_collection_collector')
require(record['native_exit_code']==0,'Collector失败，原件与失败输出保留')
print(json.dumps(record,ensure_ascii=False))
