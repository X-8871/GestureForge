"""捕获最终封包原生退出码，不向正式包增加自引用输出。"""
from collection_common import *
closed_gate()
record=run_closed([sys.executable,'-B',str(WORK/'finalize_s7.py')],'s7_finalization',timeout=55)
require(record['native_exit_code']==0,'最终封包失败，关闭日志保留')
print(json.dumps(record,ensure_ascii=False))
