"""总控闭合门禁后捕获 Collector 原生退出码，保持失败原件。"""
from collection_common import *
closed_gate()
record=run_closed([sys.executable,'-B',str(WORK/'collect_s7.py')],'s7_collection_collector',timeout=55)
copy_closed('s7_collection_collector')
require(record['native_exit_code']==0,'Collector原生失败，日志与已有原件保留')
print(json.dumps(record,ensure_ascii=False))
