"""最终核验宿主日志只写tmp，不改封闭正式证据目录。"""
from collection_common import *
record = run_closed([sys.executable, '-B', str(WORK / 'finalize_s5.py')], 's5_finalization')
require(record['native_exit_code'] == 0, '最终核验失败，关闭原始日志保留')
print(json.dumps(record, ensure_ascii=False))
