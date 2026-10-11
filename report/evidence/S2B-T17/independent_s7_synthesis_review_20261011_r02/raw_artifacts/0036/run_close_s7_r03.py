"""保存只增修正与封包的实际原生返回码。"""
from collection_common import *
record=run_closed([sys.executable,'-B',str(WORK/'close_s7_r03.py')],'s7_close_r03',timeout=55)
require(record['native_exit_code']==0,'r03封包失败，关闭失败输出保留')
print(json.dumps(record,ensure_ascii=False))
