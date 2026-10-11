"""记录最终封包的真实原生退出码，不增加正式自引用文件。"""
from collection_common import *
record=run_closed([sys.executable,'-B',str(WORK / 'finalize_s6_r02.py')],'s6_finalization_r02',timeout=55)
require(record['native_exit_code']==0,'最终封包失败，失败输出保留')
print(json.dumps(record,ensure_ascii=False))
