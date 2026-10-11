"""独立轻量审查运行器，所有新产物限定在本次隔离目录。"""
import sys
sys.dont_write_bytecode = True
import unittest
import tempfile
import json
import pathlib
import hashlib
import time

目录 = pathlib.Path(__file__).absolute().parent
根目录 = 目录.parents[3]
sys.path.insert(0, str(根目录))
from verification import test_s2b_board_transport as 测试

原创建 = tempfile.mkdtemp
def 创建(*args, **kwargs):
    kwargs['dir'] = 目录
    return 原创建(*args, **kwargs)
tempfile.mkdtemp = 创建
开始 = time.monotonic()
with (目录 / 'unittest.log').open('x', encoding='utf-8') as 日志:
    结果 = unittest.TextTestRunner(stream=日志, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(测试))
记录 = {'status': 'PASS' if 结果.wasSuccessful() else 'FAIL', 'tests': 结果.testsRun,
        'failures': len(结果.failures), 'errors': len(结果.errors), 'skipped': len(结果.skipped),
        'elapsed_seconds': time.monotonic()-开始, 'native_directory': str(测试.NativeTests.directory),
        'log_sha256': hashlib.sha256((目录/'unittest.log').read_bytes()).hexdigest()}
with (目录/'test_result.json').open('x', encoding='utf-8') as 流:
    json.dump(记录, 流, ensure_ascii=False, indent=2)
print(json.dumps(记录, ensure_ascii=False))
sys.exit(0 if 结果.wasSuccessful() else 1)
