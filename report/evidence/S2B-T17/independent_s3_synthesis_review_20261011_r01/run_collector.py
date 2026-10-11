"""实际执行轻量归档并保存已关闭日志、原生码与耗时。"""
from collect_archive import *
record=native([sys.executable,"-B",str(TMP/"collect_archive.py")],"collector",where=TMP)
print(json.dumps(record,ensure_ascii=True));raise SystemExit(record["native_exit_code"])
