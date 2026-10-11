"""最终封装命令输出仅写隔离tmp，避免改变已封存正式目录。"""
from collection_common import *
record=run_closed([sys.executable,"-B",str(CACHE/"finalize_s4_manifest.py")],"s4_finalization")
print(json.dumps(record,ensure_ascii=False))
raise SystemExit(record["native_exit_code"])
