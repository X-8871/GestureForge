"""轻量父进程保存实际 Collector 原生码及已关闭日志。"""
from collection_common import *
started=time.monotonic()
record=run_closed([sys.executable,"-B",str(CACHE/"collect_s3_synthesis.py")],"s3_collection_collector")
record["outer_elapsed_seconds"]=time.monotonic()-started
save(CACHE/"collector_execution_result.json",record)
print(json.dumps(record,ensure_ascii=False))
raise SystemExit(record["native_exit_code"])
