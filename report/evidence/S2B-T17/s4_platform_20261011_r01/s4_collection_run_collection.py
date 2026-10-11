"""运行一次 S4 Collector，关闭后保存真实退出码与输出。"""
from collection_common import *
record=run_closed([sys.executable,"-B",str(CACHE/"collect_s4_synthesis.py")],"s4_collection_collector",REPORT)
print(json.dumps(record,ensure_ascii=False))
raise SystemExit(record["native_exit_code"])
