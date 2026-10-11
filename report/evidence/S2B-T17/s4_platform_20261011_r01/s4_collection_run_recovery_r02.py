"""只执行新的封装恢复，保存关闭的真实返回。"""
from collection_common import *
record=run_closed([sys.executable,"-B",str(CACHE/"seal_collection_r02.py")],"s4_collection_recovery_r02",REPORT)
print(json.dumps(record,ensure_ascii=False))
raise SystemExit(record["native_exit_code"])
