"""记录本次轻量封存恢复的真实原生码与已关闭日志。"""
from collection_common import *
started=time.monotonic()
record=run_closed([sys.executable,"-B",str(CACHE/"seal_s3_collection.py")],"s3_collection_seal")
record["outer_elapsed_seconds"]=time.monotonic()-started
save(CACHE/"seal_execution_result.json",record)
print(json.dumps(record,ensure_ascii=False))
raise SystemExit(record["native_exit_code"])
