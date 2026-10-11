"""保存最终封包的原生退出码，避免正式清单自引用。"""
from collection_common import *
record=run_closed([sys.executable,'-B',str(WORK / 'finalize_s6.py')],'s6_finalization',timeout=55)
require(record['native_exit_code']==0,'最终封包失败，失败输出保留')
print(json.dumps(record,ensure_ascii=False))
