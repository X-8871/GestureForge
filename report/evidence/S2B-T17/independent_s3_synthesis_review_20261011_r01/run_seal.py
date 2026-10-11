"""封存父进程日志并记录真实原生退出码。"""
from collect_archive import *
record=native([sys.executable,"-B",str(TMP/"seal_archive.py")],"seal",where=TMP)
print(json.dumps(record,ensure_ascii=True));raise SystemExit(record["native_exit_code"])
