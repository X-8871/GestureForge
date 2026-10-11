"""保存Collector原生退出码，随后只复制已关闭日志。"""
from collection_common import *
record = run_closed([sys.executable, '-B', str(WORK / 'collect_s5.py')], 's5_collection_collector')
copy_closed('s5_collection_collector')
require(record['native_exit_code'] == 0, 'Collector失败，原件及失败输出已保留')
print(json.dumps(record, ensure_ascii=False))
