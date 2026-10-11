"""最终恢复清单检查返回写tmp，不更改正式封存目录。"""
from collection_common import *
record=run_closed([sys.executable,"-B",str(CACHE/"finalize_recovery_r02.py")],"s4_finalization_recovery_r02")
print(json.dumps(record,ensure_ascii=False))
raise SystemExit(record["native_exit_code"])
